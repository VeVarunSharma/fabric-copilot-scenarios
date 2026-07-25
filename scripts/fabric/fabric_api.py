from __future__ import annotations

import base64
import json
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Protocol


FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"
FABRIC_RESOURCE = "https://api.fabric.microsoft.com"
INLINE_BASE64 = "InlineBase64"
TRANSIENT_STATUS_CODES = {429, 503, 504}
RUNNING_OPERATION_STATUSES = {"NotStarted", "Running", "InProgress"}
FAILED_OPERATION_STATUSES = {"Failed", "Cancelled"}
SUCCESS_OPERATION_STATUSES = {"Succeeded", "Completed", "Deduped"}


def redact_sensitive_text(value: str) -> str:
    if not value:
        return value
    redacted = value
    patterns = [
        (r"(?i)(Bearer\s+)[A-Za-z0-9\-\._~\+/]+=*", r"\1<redacted>"),
        (
            r'(?i)("?(?:access[_-]?token|token|authorization)"?\s*[:=]\s*"?)([^"\s,]+)("?)',
            r"\1<redacted>\3",
        ),
    ]
    import re

    for pattern, replacement in patterns:
        redacted = re.sub(pattern, replacement, redacted)
    return redacted


def normalize_headers(headers: Mapping[str, Any] | None) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in (headers or {}).items():
        normalized[str(key).lower()] = str(value)
    return normalized


def parse_retry_after(headers: Mapping[str, str], default: int = 1) -> int:
    raw = normalize_headers(headers).get("retry-after")
    if raw is None:
        return default
    try:
        parsed = int(raw)
    except ValueError:
        return default
    return max(parsed, 0)


def extract_request_id(
    headers: Mapping[str, str] | None, payload: Mapping[str, Any] | None = None
) -> str | None:
    normalized = normalize_headers(headers)
    for key in ("x-ms-request-id", "request-id", "x-ms-operation-id"):
        if normalized.get(key):
            return normalized[key]
    if payload and isinstance(payload, Mapping):
        request_id = payload.get("requestId")
        if request_id:
            return str(request_id)
        error = payload.get("error")
        if isinstance(error, Mapping) and error.get("requestId"):
            return str(error["requestId"])
    return None


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    headers: dict[str, str]
    body: bytes = b""

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")

    def json_body(self) -> Any:
        if not self.body.strip():
            return None
        return json.loads(self.text)


@dataclass(frozen=True)
class ApiResponse:
    status_code: int
    headers: dict[str, str]
    body: Any
    request_id: str | None


class FabricApiError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
        request_id: str | None = None,
        details: Any = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.request_id = request_id
        self.details = details
        parts = [message]
        if error_code:
            parts.append(f"errorCode={error_code}")
        if status_code is not None:
            parts.append(f"status={status_code}")
        if request_id:
            parts.append(f"requestId={request_id}")
        super().__init__(" | ".join(parts))


class TokenProvider(Protocol):
    def get_token(self, resource: str = FABRIC_RESOURCE) -> str:
        ...


class HttpTransport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        body: bytes | None = None,
    ) -> HttpResponse:
        ...


class AzCliTokenProvider:
    def __init__(self, *, command_runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run) -> None:
        self._command_runner = command_runner

    def get_token(self, resource: str = FABRIC_RESOURCE) -> str:
        command = [
            "az",
            "account",
            "get-access-token",
            "--resource",
            resource,
            "--query",
            "accessToken",
            "-o",
            "tsv",
        ]
        try:
            completed = self._command_runner(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise FabricApiError("Azure CLI is required but was not found on PATH") from exc
        if completed.returncode != 0:
            stderr = redact_sensitive_text((completed.stderr or "").strip())
            raise FabricApiError(f"Failed to acquire Fabric access token via Azure CLI: {stderr}")
        token = (completed.stdout or "").strip()
        if not token:
            raise FabricApiError("Azure CLI returned an empty Fabric access token")
        return token


class UrllibHttpTransport:
    def __init__(self, *, timeout: int = 60) -> None:
        self.timeout = timeout

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        body: bytes | None = None,
    ) -> HttpResponse:
        request = urllib.request.Request(
            url,
            data=body,
            headers=dict(headers),
            method=method.upper(),
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return HttpResponse(
                    status_code=int(response.status),
                    headers=normalize_headers(dict(response.headers.items())),
                    body=response.read(),
                )
        except urllib.error.HTTPError as exc:
            return HttpResponse(
                status_code=int(exc.code),
                headers=normalize_headers(dict(exc.headers.items()) if exc.headers else {}),
                body=exc.read(),
            )
        except urllib.error.URLError as exc:
            raise FabricApiError(f"HTTP request failed for {url}: {exc.reason}") from exc


def encode_definition_parts(parts: Mapping[str, bytes]) -> dict[str, Any]:
    return {
        "parts": [
            {
                "path": path,
                "payload": base64.b64encode(payload).decode("ascii"),
                "payloadType": INLINE_BASE64,
            }
            for path, payload in sorted(parts.items())
        ]
    }


def decode_definition_parts(definition: Mapping[str, Any]) -> dict[str, bytes]:
    decoded: dict[str, bytes] = {}
    for part in definition.get("parts", []):
        path = str(part["path"])
        payload_type = part.get("payloadType")
        if payload_type != INLINE_BASE64:
            raise FabricApiError(f"Unsupported definition payload type for {path}: {payload_type}")
        decoded[path] = base64.b64decode(part["payload"])
    return decoded


class FabricApiClient:
    def __init__(
        self,
        *,
        base_url: str = FABRIC_API_BASE,
        token_provider: TokenProvider | None = None,
        transport: HttpTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
        max_retries: int = 4,
        poll_interval_seconds: int = 2,
        user_agent: str = "fabric-deploy-cli/1.0",
        token_resource: str = FABRIC_RESOURCE,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token_provider = token_provider or AzCliTokenProvider()
        self.transport = transport or UrllibHttpTransport()
        self.sleep = sleep
        self.max_retries = max_retries
        self.poll_interval_seconds = poll_interval_seconds
        self.user_agent = user_agent
        self.token_resource = token_resource
        self._access_token: str | None = None

    def build_url(self, path_or_url: str) -> str:
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            return path_or_url
        return f"{self.base_url}/{path_or_url.lstrip('/')}"

    def _get_access_token(self) -> str:
        if not self._access_token:
            self._access_token = self.token_provider.get_token(self.token_resource)
        return self._access_token

    def _send_request(
        self,
        method: str,
        path_or_url: str,
        *,
        payload: Any = None,
        expected_statuses: Iterable[int] | None = None,
        extra_headers: Mapping[str, str] | None = None,
        retry_transient: bool = True,
    ) -> HttpResponse:
        url = self.build_url(path_or_url)
        body: bytes | None = None
        headers: dict[str, str] = {
            "accept": "application/json",
            "user-agent": self.user_agent,
            "authorization": f"Bearer {self._get_access_token()}",
        }
        headers.update(dict(extra_headers or {}))
        if payload is not None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            headers["content-type"] = "application/json"
        allowed = set(expected_statuses or [])
        for attempt in range(self.max_retries):
            response = self.transport.request(method, url, headers=headers, body=body)
            if (
                retry_transient
                and response.status_code in TRANSIENT_STATUS_CODES
                and attempt < self.max_retries - 1
            ):
                self.sleep(parse_retry_after(response.headers, default=max(1, 2**attempt)))
                continue
            if allowed and response.status_code not in allowed:
                raise self._build_error(response, f"{method.upper()} {url} failed")
            return response
        raise FabricApiError(f"{method.upper()} {url} exhausted retries")

    def request_json(
        self,
        method: str,
        path_or_url: str,
        *,
        payload: Any = None,
        expected_statuses: Iterable[int] | None = None,
        extra_headers: Mapping[str, str] | None = None,
        retry_transient: bool = True,
    ) -> ApiResponse:
        response = self._send_request(
            method,
            path_or_url,
            payload=payload,
            expected_statuses=expected_statuses,
            extra_headers=extra_headers,
            retry_transient=retry_transient,
        )
        try:
            body = response.json_body()
        except json.JSONDecodeError as exc:
            raise FabricApiError(
                f"Expected JSON response from {method.upper()} {self.build_url(path_or_url)}",
                status_code=response.status_code,
                request_id=extract_request_id(response.headers),
            ) from exc
        return ApiResponse(
            status_code=response.status_code,
            headers=response.headers,
            body=body,
            request_id=extract_request_id(response.headers, body if isinstance(body, Mapping) else None),
        )

    def _build_error(self, response: HttpResponse, context: str) -> FabricApiError:
        payload: Any
        try:
            payload = response.json_body()
        except json.JSONDecodeError:
            payload = response.text
        request_id = extract_request_id(response.headers, payload if isinstance(payload, Mapping) else None)
        if isinstance(payload, Mapping):
            details = payload.get("error") if isinstance(payload.get("error"), Mapping) else payload
            error_code = details.get("errorCode")
            message = details.get("message") or context
            return FabricApiError(
                message,
                status_code=response.status_code,
                error_code=str(error_code) if error_code else None,
                request_id=request_id,
                details=payload,
            )
        return FabricApiError(
            redact_sensitive_text(f"{context}: {response.text.strip()}"),
            status_code=response.status_code,
            request_id=request_id,
            details=payload,
        )

    def _append_query(self, url: str, params: Mapping[str, Any]) -> str:
        parsed = urllib.parse.urlsplit(url)
        current = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
        for key, value in params.items():
            if value is None:
                continue
            current[str(key)] = str(value)
        query = urllib.parse.urlencode(current)
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))

    def iter_paginated(self, path: str, *, query: Mapping[str, Any] | None = None) -> Iterable[dict[str, Any]]:
        original_url = self._append_query(self.build_url(path), query or {})
        next_url: str | None = original_url
        while next_url:
            response = self.request_json("GET", next_url, expected_statuses={200})
            body = response.body or {}
            for item in body.get("value", []):
                yield item
            continuation_uri = body.get("continuationUri")
            continuation_token = body.get("continuationToken")
            if continuation_uri:
                next_url = str(continuation_uri)
            elif continuation_token:
                next_url = self._append_query(original_url, {"continuationToken": continuation_token})
            else:
                next_url = None

    def list_workspaces(self, *, roles: str | None = None) -> list[dict[str, Any]]:
        query = {"roles": roles} if roles else {}
        return list(self.iter_paginated("/workspaces", query=query))

    def list_items(
        self,
        workspace_id: str,
        *,
        item_type: str | None = None,
        root_folder_id: str | None = None,
        recursive: bool = True,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"recursive": str(recursive).lower()}
        if item_type:
            query["type"] = item_type
        if root_folder_id:
            query["rootFolderId"] = root_folder_id
        return list(self.iter_paginated(f"/workspaces/{workspace_id}/items", query=query))

    def find_workspace_by_display_name(
        self, display_name: str, *, allow_missing: bool = False
    ) -> dict[str, Any] | None:
        matches = [item for item in self.list_workspaces() if item.get("displayName") == display_name]
        return self._resolve_single_match(matches, display_name, "workspace", allow_missing=allow_missing)

    def find_item_by_display_name(
        self,
        workspace_id: str,
        display_name: str,
        item_type: str,
        *,
        allow_missing: bool = False,
    ) -> dict[str, Any] | None:
        matches = [
            item
            for item in self.list_items(workspace_id, item_type=item_type)
            if item.get("displayName") == display_name
        ]
        return self._resolve_single_match(
            matches,
            display_name,
            f"{item_type} item",
            allow_missing=allow_missing,
        )

    def _resolve_single_match(
        self,
        matches: list[dict[str, Any]],
        display_name: str,
        entity_name: str,
        *,
        allow_missing: bool,
    ) -> dict[str, Any] | None:
        if not matches:
            if allow_missing:
                return None
            raise FabricApiError(f"No {entity_name} found with displayName '{display_name}'")
        if len(matches) > 1:
            ids = ", ".join(str(match.get("id")) for match in matches)
            raise FabricApiError(
                f"Multiple {entity_name}s found with displayName '{display_name}': {ids}"
            )
        return matches[0]

    def create_item(
        self,
        workspace_id: str,
        *,
        display_name: str,
        item_type: str,
        definition: Mapping[str, Any],
        description: str | None = None,
        folder_id: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "displayName": display_name,
            "type": item_type,
            "definition": definition,
        }
        if description:
            payload["description"] = description
        if folder_id:
            payload["folderId"] = folder_id
        response = self.request_json(
            "POST",
            f"/workspaces/{workspace_id}/items",
            payload=payload,
            expected_statuses={201, 202},
        )
        if response.status_code == 202:
            return self.poll_operation(
                location=response.headers.get("location"),
                operation_id=response.headers.get("x-ms-operation-id"),
                result_required=True,
            )
        return response.body

    def get_item_definition(
        self, workspace_id: str, item_id: str, *, definition_format: str | None = None
    ) -> dict[str, Any]:
        path = f"/workspaces/{workspace_id}/items/{item_id}/getDefinition"
        if definition_format:
            path = self._append_query(self.build_url(path), {"format": definition_format})
        response = self.request_json("POST", path, payload={}, expected_statuses={200, 202})
        if response.status_code == 202:
            result = self.poll_operation(
                location=response.headers.get("location"),
                operation_id=response.headers.get("x-ms-operation-id"),
                result_required=True,
            )
            return result["definition"]
        return response.body["definition"]

    def update_item_definition(
        self,
        workspace_id: str,
        item_id: str,
        *,
        definition: Mapping[str, Any],
        update_metadata: bool = False,
    ) -> None:
        path = f"/workspaces/{workspace_id}/items/{item_id}/updateDefinition"
        if update_metadata:
            path = self._append_query(self.build_url(path), {"updateMetadata": "true"})
        response = self.request_json(
            "POST",
            path,
            payload={"definition": definition},
            expected_statuses={200, 202},
        )
        if response.status_code == 202:
            self.poll_operation(
                location=response.headers.get("location"),
                operation_id=response.headers.get("x-ms-operation-id"),
                result_required=False,
            )

    def poll_operation(
        self,
        *,
        location: str | None,
        operation_id: str | None,
        result_required: bool,
    ) -> Any:
        if not location and not operation_id:
            raise FabricApiError("Fabric API returned an LRO response without Location or operation ID")
        state_url = location or f"{self.base_url}/operations/{operation_id}"
        while True:
            response = self.request_json("GET", state_url, expected_statuses={200, 201, 202})
            body = response.body if isinstance(response.body, Mapping) else {}
            status = body.get("status")
            if response.status_code == 202 or status in RUNNING_OPERATION_STATUSES:
                self.sleep(parse_retry_after(response.headers, default=self.poll_interval_seconds))
                continue
            if status in FAILED_OPERATION_STATUSES:
                error = body.get("error") if isinstance(body.get("error"), Mapping) else body
                raise FabricApiError(
                    str(error.get("message") or "Fabric long-running operation failed"),
                    status_code=response.status_code,
                    error_code=str(error.get("errorCode")) if error.get("errorCode") else None,
                    request_id=extract_request_id(response.headers, error),
                    details=body,
                )
            if result_required:
                if not operation_id:
                    raise FabricApiError("Fabric long-running result requires x-ms-operation-id")
                result = self.request_json(
                    "GET",
                    f"/operations/{operation_id}/result",
                    expected_statuses={200, 201},
                )
                return result.body
            return response.body

    def run_item_job(
        self,
        workspace_id: str,
        item_id: str,
        *,
        job_type: str,
        execution_data: Mapping[str, Any] | None = None,
        parameters: list[dict[str, Any]] | None = None,
        wait: bool = True,
    ) -> dict[str, Any]:
        request_execution_data: MutableMapping[str, Any] = dict(execution_data or {})
        if parameters:
            request_execution_data["parameters"] = parameters
        path = self._append_query(
            self.build_url(f"/workspaces/{workspace_id}/items/{item_id}/jobs/instances"),
            {"jobType": job_type},
        )
        payload: MutableMapping[str, Any] = {}
        if request_execution_data:
            payload["executionData"] = request_execution_data
        response = self.request_json(
            "POST",
            path,
            payload=payload or None,
            expected_statuses={202},
        )
        location = response.headers.get("location")
        if not location:
            raise FabricApiError("Job submission response did not include a Location header")
        if not wait:
            return {
                "status": "Accepted",
                "location": location,
                "requestId": response.request_id,
            }
        return self.poll_job_instance(location)

    def poll_job_instance(self, location: str) -> dict[str, Any]:
        while True:
            response = self.request_json("GET", location, expected_statuses={200})
            body = response.body or {}
            status = body.get("status")
            if status in RUNNING_OPERATION_STATUSES:
                self.sleep(parse_retry_after(response.headers, default=self.poll_interval_seconds))
                continue
            if status in FAILED_OPERATION_STATUSES:
                failure = body.get("failureReason") if isinstance(body.get("failureReason"), Mapping) else body
                raise FabricApiError(
                    str(failure.get("message") or "Fabric job failed"),
                    error_code=str(failure.get("errorCode")) if failure.get("errorCode") else None,
                    request_id=extract_request_id(response.headers, failure),
                    details=body,
                )
            return body
