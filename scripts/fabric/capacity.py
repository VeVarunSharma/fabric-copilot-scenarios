from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, TextIO
from urllib.parse import urlparse

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.fabric.fabric_api import (
    FABRIC_API_BASE,
    FabricApiClient,
    FabricApiError,
    redact_sensitive_text,
)


POWER_BI_API_BASE = "https://api.powerbi.com/v1.0/myorg"
POWER_BI_RESOURCE = "https://analysis.windows.net/powerbi/api"
MINIMUM_AZURE_CLI_VERSION = (2, 61, 0)
OWNERSHIP_TAGS = {
    "environment": "demo",
    "workload": "fabric-with-github",
    "managed-by": "bicep",
    "cost-control": "suspend-when-idle",
}
ACTIVE_STATES = {"active"}
SUSPENDED_STATES = {"paused", "suspended"}


class CapacityError(RuntimeError):
    pass


class CommandRunner(Protocol):
    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        ...


@dataclass(frozen=True)
class CapacityConfig:
    location: str
    resource_group_name: str
    workspace_name: str
    workspace_description: str
    subscription_id: str | None = None
    capacity_name: str | None = None
    administrator_upn: str | None = None
    github_owner: str | None = None
    github_repository: str | None = None
    github_branch: str = "main"
    github_directory: str = "/"
    github_connection_name: str = "fabric-with-github-demo"
    initialize_from_git: bool = True


def _optional_string(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise CapacityError(f"{field_name} must be a string")
    value = value.strip()
    return value or None


def _required_string(value: Any, field_name: str) -> str:
    parsed = _optional_string(value, field_name)
    if not parsed:
        raise CapacityError(f"{field_name} is required")
    return parsed


def load_capacity_config(path: str | Path) -> CapacityConfig:
    config_path = Path(path)
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CapacityError(
            f"Capacity config not found: {config_path}. "
            "Run 'make fabric-configure' and review the generated local config."
        ) from exc
    except json.JSONDecodeError as exc:
        raise CapacityError(f"Invalid JSON in capacity config {config_path}: {exc}") from exc
    if not isinstance(raw, Mapping):
        raise CapacityError("Capacity config must contain a JSON object")

    workspace = raw.get("workspace", {})
    github = raw.get("github", {})
    if not isinstance(workspace, Mapping):
        raise CapacityError("workspace must be a JSON object")
    if not isinstance(github, Mapping):
        raise CapacityError("github must be a JSON object")

    initialize_from_git = github.get("initializeFromGit", True)
    if not isinstance(initialize_from_git, bool):
        raise CapacityError("github.initializeFromGit must be a boolean")

    config = CapacityConfig(
        subscription_id=_optional_string(raw.get("subscriptionId"), "subscriptionId"),
        location=_required_string(raw.get("location"), "location"),
        resource_group_name=_required_string(raw.get("resourceGroupName"), "resourceGroupName"),
        capacity_name=_optional_string(raw.get("capacityName"), "capacityName"),
        administrator_upn=_optional_string(raw.get("administratorUpn"), "administratorUpn"),
        workspace_name=_required_string(workspace.get("displayName"), "workspace.displayName"),
        workspace_description=str(workspace.get("description", "")).strip(),
        github_owner=_optional_string(github.get("owner"), "github.owner"),
        github_repository=_optional_string(github.get("repository"), "github.repository"),
        github_branch=_required_string(github.get("branch", "main"), "github.branch"),
        github_directory=_required_string(github.get("directory", "/"), "github.directory"),
        github_connection_name=_required_string(
            github.get("connectionName", "fabric-with-github-demo"),
            "github.connectionName",
        ),
        initialize_from_git=initialize_from_git,
    )
    _validate_config(config)
    return config


def _validate_config(config: CapacityConfig) -> None:
    if not re.fullmatch(r"[A-Za-z0-9._()\-]{1,90}", config.resource_group_name):
        raise CapacityError("resourceGroupName contains unsupported characters")
    if config.capacity_name and not re.fullmatch(r"[a-z][a-z0-9]{2,62}", config.capacity_name):
        raise CapacityError(
            "capacityName must be 3-63 lowercase alphanumeric characters and start with a letter"
        )
    if len(config.workspace_name) > 256:
        raise CapacityError("workspace.displayName cannot exceed 256 characters")
    if len(config.workspace_description) > 4000:
        raise CapacityError("workspace.description cannot exceed 4000 characters")
    if len(config.github_directory) > 256:
        raise CapacityError("github.directory cannot exceed 256 characters")


def derive_capacity_name(subscription_id: str) -> str:
    normalized = re.sub(r"[^a-z0-9]", "", subscription_id.lower())
    if len(normalized) >= 12:
        return f"fcfabricgithub{normalized[:12]}"
    digest = hashlib.sha256(subscription_id.encode("utf-8")).hexdigest()[:12]
    return f"fcfabricgithub{digest}"


def _version_tuple(version: str) -> tuple[int, int, int]:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise CapacityError(f"Unable to parse Azure CLI version: {version}")
    return tuple(int(part) for part in match.groups())


def _json_object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise CapacityError(f"{context} returned an unexpected response")
    return dict(value)


class AzureCli:
    def __init__(
        self,
        *,
        runner: CommandRunner = subprocess.run,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.runner = runner
        self.sleep = sleep

    def _invoke(
        self,
        arguments: list[str],
        *,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command = ["az", *arguments]
        if "-o" not in arguments and "--output" not in arguments:
            command.extend(["-o", "json"])
        if "--only-show-errors" not in arguments:
            command.append("--only-show-errors")
        try:
            completed = self.runner(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise CapacityError("Azure CLI is required but was not found on PATH") from exc
        if check and completed.returncode != 0:
            detail = redact_sensitive_text((completed.stderr or completed.stdout or "").strip())
            raise CapacityError(f"Azure CLI command failed: {' '.join(command[1:])}: {detail}")
        return completed

    def _json(self, arguments: list[str]) -> Any:
        completed = self._invoke(arguments)
        try:
            return json.loads(completed.stdout or "null")
        except json.JSONDecodeError as exc:
            raise CapacityError(
                f"Azure CLI returned invalid JSON for: {' '.join(arguments)}"
            ) from exc

    def resolve_config(self, config: CapacityConfig) -> CapacityConfig:
        if config.subscription_id:
            self._invoke(
                ["account", "set", "--subscription", config.subscription_id, "-o", "none"]
            )
        account = _json_object(self._json(["account", "show"]), "az account show")
        subscription_id = _required_string(account.get("id"), "Azure subscription ID")
        administrator_upn = config.administrator_upn
        if not administrator_upn:
            user = account.get("user")
            if isinstance(user, Mapping) and str(user.get("type", "user")).lower() == "user":
                administrator_upn = _optional_string(user.get("name"), "Azure account user")
        if not administrator_upn:
            raise CapacityError(
                "administratorUpn is required when Azure CLI cannot infer a signed-in user"
            )
        return replace(
            config,
            subscription_id=subscription_id,
            capacity_name=config.capacity_name or derive_capacity_name(subscription_id),
            administrator_upn=administrator_upn,
        )

    def doctor(self, config: CapacityConfig) -> None:
        version_payload = _json_object(self._json(["version"]), "az version")
        version = _required_string(
            version_payload.get("azure-cli") or version_payload.get("azureCli"),
            "Azure CLI version",
        )
        if _version_tuple(version) < MINIMUM_AZURE_CLI_VERSION:
            required = ".".join(str(part) for part in MINIMUM_AZURE_CLI_VERSION)
            raise CapacityError(f"Azure CLI {required} or newer is required; found {version}")

        extension = self._invoke(["extension", "show", "--name", "microsoft-fabric"], check=False)
        if extension.returncode != 0:
            self._invoke(["extension", "add", "--name", "microsoft-fabric", "-o", "none"])

        provider = _json_object(
            self._json(["provider", "show", "--namespace", "Microsoft.Fabric"]),
            "Microsoft.Fabric provider lookup",
        )
        if str(provider.get("registrationState", "")).lower() != "registered":
            self._invoke(
                [
                    "provider",
                    "register",
                    "--namespace",
                    "Microsoft.Fabric",
                    "--wait",
                    "-o",
                    "none",
                ]
            )

        self._ensure_f2_available(config.location)
        if not self.capacity_exists(config):
            availability = _json_object(
                self._json(
                    [
                        "fabric",
                        "capacity",
                        "check-name-availability",
                        "--location",
                        config.location,
                        "--name",
                        str(config.capacity_name),
                        "--type",
                        "Microsoft.Fabric/capacities",
                    ]
                ),
                "Fabric capacity name check",
            )
            if not availability.get("nameAvailable", availability.get("name_available", False)):
                reason = availability.get("message") or availability.get("reason") or "name unavailable"
                raise CapacityError(f"Fabric capacity name is unavailable: {reason}")

    def _ensure_f2_available(self, location: str) -> None:
        payload = self._json(["fabric", "capacity", "list-skus"])
        candidates: Any = payload.get("value", []) if isinstance(payload, Mapping) else payload
        if not isinstance(candidates, list):
            raise CapacityError("Unable to determine Fabric F2 SKU availability")
        normalized_location = location.lower().replace(" ", "")
        for item in candidates:
            if not isinstance(item, Mapping):
                continue
            sku_name = str(item.get("name") or item.get("skuName") or "").upper()
            if sku_name != "F2":
                continue
            locations = item.get("locations") or item.get("location") or []
            if isinstance(locations, str):
                locations = [locations]
            if not locations or any(
                str(value).lower().replace(" ", "") == normalized_location for value in locations
            ):
                return
        raise CapacityError(f"Fabric F2 is not available in Azure region '{location}'")

    def validate_bicep(self, template_file: Path) -> None:
        self._invoke(["bicep", "build", "--file", str(template_file), "--stdout"], check=True)

    def deploy(self, config: CapacityConfig, template_file: Path) -> dict[str, Any]:
        deployment_name = f"fabric-demo-{hashlib.sha256(str(config.subscription_id).encode()).hexdigest()[:8]}"
        result = _json_object(
            self._json(
                [
                    "deployment",
                    "sub",
                    "create",
                    "--name",
                    deployment_name,
                    "--location",
                    config.location,
                    "--template-file",
                    str(template_file),
                    "--parameters",
                    f"location={config.location}",
                    f"resourceGroupName={config.resource_group_name}",
                    f"capacityName={config.capacity_name}",
                    f"adminMembers={json.dumps([config.administrator_upn])}",
                ]
            ),
            "subscription deployment",
        )
        properties = result.get("properties")
        outputs = properties.get("outputs", {}) if isinstance(properties, Mapping) else {}
        if not isinstance(outputs, Mapping):
            raise CapacityError("Subscription deployment did not return outputs")
        return {
            key: value.get("value") if isinstance(value, Mapping) else value
            for key, value in outputs.items()
        }

    def capacity_exists(self, config: CapacityConfig) -> bool:
        completed = self._invoke(
            [
                "fabric",
                "capacity",
                "show",
                "--capacity-name",
                str(config.capacity_name),
                "--resource-group",
                config.resource_group_name,
            ],
            check=False,
        )
        return completed.returncode == 0

    def show_capacity(self, config: CapacityConfig) -> dict[str, Any] | None:
        completed = self._invoke(
            [
                "fabric",
                "capacity",
                "show",
                "--capacity-name",
                str(config.capacity_name),
                "--resource-group",
                config.resource_group_name,
            ],
            check=False,
        )
        if completed.returncode != 0:
            return None
        try:
            return _json_object(json.loads(completed.stdout or "{}"), "Fabric capacity lookup")
        except json.JSONDecodeError as exc:
            raise CapacityError("Fabric capacity lookup returned invalid JSON") from exc

    @staticmethod
    def capacity_state(capacity: Mapping[str, Any]) -> str:
        properties = capacity.get("properties")
        if isinstance(properties, Mapping) and properties.get("state"):
            return str(properties["state"])
        return str(capacity.get("state") or capacity.get("provisioningState") or "Unknown")

    def resume(self, config: CapacityConfig) -> None:
        capacity = self.show_capacity(config)
        if not capacity:
            raise CapacityError("Fabric capacity does not exist; run the deploy command first")
        if self.capacity_state(capacity).lower() not in ACTIVE_STATES:
            self._invoke(
                [
                    "fabric",
                    "capacity",
                    "resume",
                    "--capacity-name",
                    str(config.capacity_name),
                    "--resource-group",
                    config.resource_group_name,
                    "-o",
                    "none",
                ]
            )
            self.wait_for_state(config, ACTIVE_STATES)

    def suspend(self, config: CapacityConfig) -> None:
        capacity = self.show_capacity(config)
        if not capacity:
            raise CapacityError("Fabric capacity does not exist; run the deploy command first")
        if self.capacity_state(capacity).lower() not in SUSPENDED_STATES:
            self._invoke(
                [
                    "fabric",
                    "capacity",
                    "suspend",
                    "--capacity-name",
                    str(config.capacity_name),
                    "--resource-group",
                    config.resource_group_name,
                    "-o",
                    "none",
                ]
            )
            self.wait_for_state(config, SUSPENDED_STATES)

    def wait_for_state(
        self,
        config: CapacityConfig,
        expected_states: set[str],
        *,
        attempts: int = 60,
    ) -> None:
        for _ in range(attempts):
            capacity = self.show_capacity(config)
            if not capacity:
                raise CapacityError("Fabric capacity disappeared while waiting for its state")
            state = self.capacity_state(capacity).lower()
            if state in expected_states:
                return
            self.sleep(10)
        expected = ", ".join(sorted(expected_states))
        raise CapacityError(f"Timed out waiting for Fabric capacity state: {expected}")

    def show_resource_group(self, config: CapacityConfig) -> dict[str, Any] | None:
        completed = self._invoke(
            ["group", "show", "--name", config.resource_group_name],
            check=False,
        )
        if completed.returncode != 0:
            return None
        try:
            return _json_object(json.loads(completed.stdout or "{}"), "resource group lookup")
        except json.JSONDecodeError as exc:
            raise CapacityError("Resource group lookup returned invalid JSON") from exc

    def delete_resource_group(self, config: CapacityConfig) -> None:
        self._invoke(
            [
                "group",
                "delete",
                "--name",
                config.resource_group_name,
                "--yes",
                "--no-wait",
                "-o",
                "none",
            ]
        )


class StateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CapacityError(f"Invalid lifecycle state file {self.path}: {exc}") from exc
        return _json_object(data, "lifecycle state file")

    def save(self, state: Mapping[str, Any]) -> None:
        temporary = self.path.with_name(f"{self.path.name}.tmp")
        temporary.write_text(
            json.dumps(dict(state), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.chmod(stat.S_IRUSR | stat.S_IWUSR)
        os.replace(temporary, self.path)

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)


def _parse_github_remote(remote_url: str) -> tuple[str, str]:
    value = remote_url.strip()
    if value.startswith("git@github.com:"):
        path = value.removeprefix("git@github.com:")
    else:
        parsed = urlparse(value)
        if parsed.hostname != "github.com":
            raise CapacityError("The Git remote must point to github.com")
        path = parsed.path.lstrip("/")
    path = path.removesuffix(".git").strip("/")
    parts = path.split("/")
    if len(parts) != 2 or not all(parts):
        raise CapacityError(f"Unable to parse GitHub owner and repository from remote: {remote_url}")
    return parts[0], parts[1]


def resolve_github_repository(
    config: CapacityConfig,
    repo_root: Path,
    *,
    runner: CommandRunner = subprocess.run,
) -> CapacityConfig:
    if config.github_owner and config.github_repository:
        return config
    if bool(config.github_owner) != bool(config.github_repository):
        raise CapacityError("github.owner and github.repository must be set together")
    completed = runner(
        ["git", "-C", str(repo_root), "remote", "get-url", "origin"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise CapacityError(
            "No GitHub repository is configured. Set github.owner and github.repository "
            "or add a GitHub origin remote."
        )
    owner, repository = _parse_github_remote(completed.stdout)
    return replace(config, github_owner=owner, github_repository=repository)


def _connection_path(connection: Mapping[str, Any]) -> str:
    details = connection.get("connectionDetails")
    if not isinstance(details, Mapping):
        return ""
    return str(details.get("path") or "")


def _is_workspace_on_capacity(workspace: Mapping[str, Any], capacity_id: str) -> bool:
    workspace_capacity_id = workspace.get("capacityId")
    return not workspace_capacity_id or str(workspace_capacity_id).lower() == capacity_id.lower()


class FabricDemoManager:
    def __init__(
        self,
        *,
        config: CapacityConfig,
        repo_root: Path,
        azure: AzureCli,
        fabric: FabricApiClient,
        power_bi: FabricApiClient,
        state: StateStore,
        out: TextIO,
        err: TextIO,
        sleep: Callable[[float], None] = time.sleep,
        prompt: Callable[[str], str] = input,
        secret_prompt: Callable[[str], str] = getpass.getpass,
        command_runner: CommandRunner = subprocess.run,
    ) -> None:
        self.config = config
        self.repo_root = repo_root
        self.azure = azure
        self.fabric = fabric
        self.power_bi = power_bi
        self.state = state
        self.out = out
        self.err = err
        self.sleep = sleep
        self.prompt = prompt
        self.secret_prompt = secret_prompt
        self.command_runner = command_runner

    def doctor(self) -> None:
        self.azure.doctor(self.config)
        print(
            f"Ready: subscription={self.config.subscription_id} "
            f"location={self.config.location} capacity={self.config.capacity_name}",
            file=self.out,
        )

    def deploy(self) -> None:
        template_file = self.repo_root / "infra" / "main.bicep"
        capacity_created = False
        try:
            self.azure.doctor(self.config)
            self.azure.validate_bicep(template_file)
            outputs = self.azure.deploy(self.config, template_file)
            capacity_created = True
            capacity_uuid = self._wait_for_capacity_uuid()
            workspace = self._create_or_reuse_workspace(capacity_uuid)
            state = {
                "schemaVersion": 1,
                "subscriptionId": self.config.subscription_id,
                "location": self.config.location,
                "resourceGroupName": self.config.resource_group_name,
                "capacityName": self.config.capacity_name,
                "capacityResourceId": outputs.get("capacityResourceId"),
                "capacityId": capacity_uuid,
                "workspaceId": workspace["id"],
                "workspaceName": workspace["displayName"],
            }
            self.state.save(state)
        except Exception:
            if capacity_created or self.azure.capacity_exists(self.config):
                try:
                    self.azure.suspend(self.config)
                except CapacityError as suspend_error:
                    print(
                        f"WARNING: deployment failed and automatic suspension also failed: "
                        f"{suspend_error}",
                        file=self.err,
                    )
            raise
        try:
            self.azure.suspend(self.config)
        except CapacityError as exc:
            raise CapacityError(
                "Deployment succeeded, but automatic suspension failed. "
                "Run 'make down' immediately to stop ongoing capacity usage. "
                f"Details: {exc}"
            ) from exc
        print(
            f"Deployed workspace '{self.config.workspace_name}' on F2 capacity "
            f"'{self.config.capacity_name}' and suspended ongoing capacity usage.",
            file=self.out,
        )

    def up(self) -> None:
        self.azure.resume(self.config)
        print(f"Fabric capacity '{self.config.capacity_name}' is active.", file=self.out)

    def down(self) -> None:
        self.azure.suspend(self.config)
        print(f"Fabric capacity '{self.config.capacity_name}' is suspended.", file=self.out)

    def status(self) -> None:
        capacity = self.azure.show_capacity(self.config)
        if not capacity:
            print("Capacity: not deployed", file=self.out)
            return
        state = self.azure.capacity_state(capacity)
        print(
            f"Capacity: {self.config.capacity_name} (F2, {self.config.location}) - {state}",
            file=self.out,
        )
        saved = self.state.load()
        workspace_id = saved.get("workspaceId")
        if not workspace_id:
            print("Workspace: not recorded; run deploy to create it", file=self.out)
            return
        try:
            response = self.fabric.request_json(
                "GET",
                f"/workspaces/{workspace_id}",
                expected_statuses={200, 404},
            )
        except FabricApiError as exc:
            print(f"Workspace: unavailable while capacity is {state}: {exc}", file=self.out)
            return
        if response.status_code == 404:
            print("Workspace: not found", file=self.out)
        else:
            workspace = _json_object(response.body, "Fabric workspace lookup")
            print(
                f"Workspace: {workspace.get('displayName')} ({workspace.get('id')})",
                file=self.out,
            )

    def connect(self) -> None:
        config = resolve_github_repository(
            self.config,
            self.repo_root,
            runner=self.command_runner,
        )
        self._ensure_remote_branch(config)
        capacity = self.azure.show_capacity(config)
        if not capacity:
            raise CapacityError("Fabric capacity does not exist; run deploy first")
        was_suspended = self.azure.capacity_state(capacity).lower() in SUSPENDED_STATES
        if was_suspended:
            self.azure.resume(config)
        try:
            workspace = self._require_workspace()
            connection = self._get_or_create_github_connection(config)
            self._connect_workspace_to_github(config, workspace, connection)
            saved = self.state.load()
            saved["connectionId"] = connection["id"]
            saved["github"] = {
                "owner": config.github_owner,
                "repository": config.github_repository,
                "branch": config.github_branch,
                "directory": config.github_directory,
            }
            self.state.save(saved)
        finally:
            if was_suspended:
                self.azure.suspend(config)
        print(
            f"Connected workspace '{config.workspace_name}' to "
            f"{config.github_owner}/{config.github_repository}:{config.github_branch}.",
            file=self.out,
        )

    def destroy(self) -> None:
        group = self.azure.show_resource_group(self.config)
        if not group:
            self.state.clear()
            print("Demo resource group is already absent.", file=self.out)
            return
        tags = group.get("tags")
        if not isinstance(tags, Mapping) or any(
            str(tags.get(key)) != value for key, value in OWNERSHIP_TAGS.items()
        ):
            raise CapacityError(
                f"Refusing to delete resource group '{self.config.resource_group_name}': "
                "ownership tags do not match this demo."
            )
        confirmation = self.prompt(
            f"Type '{self.config.resource_group_name}' to delete the Fabric workspace "
            "and demo resource group: "
        )
        if confirmation != self.config.resource_group_name:
            raise CapacityError("Destroy cancelled: confirmation did not match")

        saved = self.state.load()
        capacity = self.azure.show_capacity(self.config)
        if capacity and self.azure.capacity_state(capacity).lower() in SUSPENDED_STATES:
            self.azure.resume(self.config)
        workspace_id = saved.get("workspaceId")
        if workspace_id:
            response = self.fabric.request_json(
                "DELETE",
                f"/workspaces/{workspace_id}",
                expected_statuses={200, 202, 204, 404},
            )
            if response.status_code == 202:
                self.fabric.poll_operation(
                    location=response.headers.get("location"),
                    operation_id=response.headers.get("x-ms-operation-id"),
                    result_required=False,
                )
        connection_id = saved.get("connectionId")
        if connection_id:
            self.fabric.request_json(
                "DELETE",
                f"/connections/{connection_id}",
                expected_statuses={200, 202, 204, 404},
            )
        self.azure.delete_resource_group(self.config)
        self.state.clear()
        print(
            f"Deletion started for resource group '{self.config.resource_group_name}'.",
            file=self.out,
        )

    def _wait_for_capacity_uuid(self, *, attempts: int = 60) -> str:
        for _ in range(attempts):
            response = self.power_bi.request_json(
                "GET",
                "/capacities",
                expected_statuses={200},
            )
            body = _json_object(response.body, "Power BI capacity lookup")
            values = body.get("value", [])
            if isinstance(values, list):
                matches = [
                    item
                    for item in values
                    if isinstance(item, Mapping)
                    and item.get("displayName") == self.config.capacity_name
                ]
                if len(matches) > 1:
                    raise CapacityError(
                        f"Multiple Fabric capacities are named '{self.config.capacity_name}'"
                    )
                if matches and matches[0].get("id"):
                    return str(matches[0]["id"])
            self.sleep(10)
        raise CapacityError(
            f"Timed out waiting for capacity '{self.config.capacity_name}' "
            "to appear in the Fabric data plane"
        )

    def _create_or_reuse_workspace(self, capacity_id: str) -> dict[str, Any]:
        workspace = self.fabric.find_workspace_by_display_name(
            self.config.workspace_name,
            allow_missing=True,
        )
        if workspace:
            response = self.fabric.request_json(
                "GET",
                f"/workspaces/{workspace['id']}",
                expected_statuses={200},
            )
            workspace = _json_object(response.body, "Fabric workspace lookup")
            if not _is_workspace_on_capacity(workspace, capacity_id):
                response = self.fabric.request_json(
                    "POST",
                    f"/workspaces/{workspace['id']}/assignToCapacity",
                    payload={"capacityId": capacity_id},
                    expected_statuses={200, 202},
                )
                if response.status_code == 202:
                    self.fabric.poll_operation(
                        location=response.headers.get("location"),
                        operation_id=response.headers.get("x-ms-operation-id"),
                        result_required=False,
                    )
            return workspace
        response = self.fabric.request_json(
            "POST",
            "/workspaces",
            payload={
                "displayName": self.config.workspace_name,
                "description": self.config.workspace_description,
                "capacityId": capacity_id,
            },
            expected_statuses={201},
        )
        return _json_object(response.body, "Fabric workspace creation")

    def _require_workspace(self) -> dict[str, Any]:
        saved = self.state.load()
        workspace_id = saved.get("workspaceId")
        if not workspace_id:
            raise CapacityError("Workspace state is missing; run deploy first")
        response = self.fabric.request_json(
            "GET",
            f"/workspaces/{workspace_id}",
            expected_statuses={200},
        )
        return _json_object(response.body, "Fabric workspace lookup")

    def _ensure_remote_branch(self, config: CapacityConfig) -> None:
        completed = self.command_runner(
            [
                "git",
                "-C",
                str(self.repo_root),
                "ls-remote",
                "--exit-code",
                "origin",
                f"refs/heads/{config.github_branch}",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise CapacityError(
                f"Remote branch '{config.github_branch}' was not found on origin. "
                "Push the branch before connecting Fabric."
            )

    def _get_or_create_github_connection(
        self,
        config: CapacityConfig,
    ) -> dict[str, Any]:
        repo_url = f"https://github.com/{config.github_owner}/{config.github_repository}"
        matches = [
            connection
            for connection in self.fabric.iter_paginated("/connections")
            if _connection_path(connection).rstrip("/") == repo_url
        ]
        if len(matches) > 1:
            raise CapacityError(f"Multiple Fabric GitHub connections target {repo_url}")
        if matches:
            return matches[0]
        token = self.secret_prompt(
            f"GitHub PAT for {config.github_owner}/{config.github_repository}: "
        ).strip()
        if not token:
            raise CapacityError("GitHub PAT cannot be empty")
        response = self.fabric.request_json(
            "POST",
            "/connections",
            payload={
                "connectivityType": "ShareableCloud",
                "displayName": config.github_connection_name,
                "connectionDetails": {
                    "type": "GitHubSourceControl",
                    "creationMethod": "GitHubSourceControl.Contents",
                    "parameters": [
                        {
                            "dataType": "Text",
                            "name": "url",
                            "value": repo_url,
                        }
                    ],
                },
                "credentialDetails": {
                    "credentials": {
                        "credentialType": "Key",
                        "key": token,
                    }
                },
            },
            expected_statuses={201},
        )
        return _json_object(response.body, "Fabric GitHub connection creation")

    def _connect_workspace_to_github(
        self,
        config: CapacityConfig,
        workspace: Mapping[str, Any],
        connection: Mapping[str, Any],
    ) -> None:
        workspace_id = str(workspace["id"])
        existing = self.fabric.request_json(
            "GET",
            f"/workspaces/{workspace_id}/git/connection",
            expected_statuses={200, 404},
        )
        if existing.status_code == 200:
            body = _json_object(existing.body, "Fabric Git connection lookup")
            details = body.get("gitProviderDetails")
            if not isinstance(details, Mapping):
                raise CapacityError("Existing Fabric Git connection has an unexpected response")
            expected = {
                "ownerName": config.github_owner,
                "repositoryName": config.github_repository,
                "branchName": config.github_branch,
                "directoryName": config.github_directory,
            }
            mismatches = [
                key for key, value in expected.items() if str(details.get(key) or "") != str(value)
            ]
            if mismatches:
                raise CapacityError(
                    "Workspace is already connected to a different Git target "
                    f"({', '.join(mismatches)} differ)"
                )
            return
        self.fabric.request_json(
            "POST",
            f"/workspaces/{workspace_id}/git/connect",
            payload={
                "gitProviderDetails": {
                    "ownerName": config.github_owner,
                    "gitProviderType": "GitHub",
                    "repositoryName": config.github_repository,
                    "branchName": config.github_branch,
                    "directoryName": config.github_directory,
                },
                "myGitCredentials": {
                    "source": "ConfiguredConnection",
                    "connectionId": connection["id"],
                },
            },
            expected_statuses={200},
        )
        initialize = self.fabric.request_json(
            "POST",
            f"/workspaces/{workspace_id}/git/initializeConnection",
            payload=(
                {"initializationStrategy": "PreferRemote"}
                if config.initialize_from_git
                else None
            ),
            expected_statuses={200, 202},
        )
        initialization = initialize.body
        if initialize.status_code == 202:
            initialization = self.fabric.poll_operation(
                location=initialize.headers.get("location"),
                operation_id=initialize.headers.get("x-ms-operation-id"),
                result_required=True,
            )
        initialization = _json_object(initialization or {}, "Fabric Git initialization")
        required_action = str(initialization.get("requiredAction") or "None")
        if required_action == "None":
            return
        if required_action != "UpdateFromGit":
            raise CapacityError(
                f"Git initialization requires '{required_action}'. "
                "The command will not write workspace content back to Git automatically."
            )
        if not config.initialize_from_git:
            print(
                "Git connection initialized; update from Git is disabled in the capacity config.",
                file=self.out,
            )
            return
        remote_commit_hash = initialization.get("remoteCommitHash")
        if not remote_commit_hash:
            raise CapacityError("Git initialization did not return remoteCommitHash")
        payload: dict[str, Any] = {
            "remoteCommitHash": remote_commit_hash,
            "workspaceHead": initialization.get("workspaceHead"),
            "conflictResolution": {
                "conflictResolutionType": "Workspace",
                "conflictResolutionPolicy": "PreferRemote",
            },
            "options": {"allowOverrideItems": True},
        }
        update = self.fabric.request_json(
            "POST",
            f"/workspaces/{workspace_id}/git/updateFromGit",
            payload=payload,
            expected_statuses={200, 202},
        )
        if update.status_code == 202:
            self.fabric.poll_operation(
                location=update.headers.get("location"),
                operation_id=update.headers.get("x-ms-operation-id"),
                result_required=False,
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage the on-demand Microsoft Fabric demo capacity"
    )
    parser.add_argument(
        "--config",
        default="scripts/fabric/capacity.local.json",
        help="Path to the local capacity configuration",
    )
    parser.add_argument(
        "--repo-root",
        default=os.getcwd(),
        help="Repository root containing infra/main.bicep",
    )
    parser.add_argument(
        "--state-file",
        default=".fabric-demo.state.json",
        help="Path to non-secret local lifecycle state",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="Validate local, Azure, SKU, and naming prerequisites")
    subparsers.add_parser("deploy", help="Deploy F2, create the workspace, then suspend F2")
    subparsers.add_parser("up", help="Resume the Fabric capacity")
    subparsers.add_parser("down", help="Suspend the Fabric capacity")
    subparsers.add_parser("status", help="Show capacity and workspace status")
    subparsers.add_parser("connect", help="Connect the workspace to this GitHub repository")
    subparsers.add_parser("destroy", help="Delete the workspace and demo resource group")
    return parser


def run_cli(
    argv: list[str] | None = None,
    *,
    azure: AzureCli | None = None,
    fabric: FabricApiClient | None = None,
    power_bi: FabricApiClient | None = None,
    out: TextIO | None = None,
    err: TextIO | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    stdout = out or sys.stdout
    stderr = err or sys.stderr
    try:
        repo_root = Path(args.repo_root).resolve()
        config = load_capacity_config(args.config)
        active_azure = azure or AzureCli()
        config = active_azure.resolve_config(config)
        active_fabric = fabric or FabricApiClient(
            base_url=FABRIC_API_BASE,
            user_agent="fabric-capacity-cli/1.0",
        )
        active_power_bi = power_bi or FabricApiClient(
            base_url=POWER_BI_API_BASE,
            token_resource=POWER_BI_RESOURCE,
            user_agent="fabric-capacity-cli/1.0",
        )
        state_path = Path(args.state_file)
        if not state_path.is_absolute():
            state_path = repo_root / state_path
        manager = FabricDemoManager(
            config=config,
            repo_root=repo_root,
            azure=active_azure,
            fabric=active_fabric,
            power_bi=active_power_bi,
            state=StateStore(state_path),
            out=stdout,
            err=stderr,
        )
        command = getattr(manager, args.command)
        command()
        return 0
    except (CapacityError, FabricApiError) as exc:
        print(f"ERROR: {exc}", file=stderr)
        return 1


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
