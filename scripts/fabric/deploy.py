from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Mapping

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.fabric.fabric_api import (
    FabricApiClient,
    FabricApiError,
    decode_definition_parts,
    encode_definition_parts,
)


SUPPORTED_ARTIFACT_TYPES = {"Notebook", "DataPipeline", "SemanticModel"}
SUPPORTED_JOB_TYPES = {"RunNotebook", "Pipeline", "Refresh"}
JOB_TYPE_TO_ITEM_TYPE = {
    "RunNotebook": "Notebook",
    "Pipeline": "DataPipeline",
    "Refresh": "SemanticModel",
}
PLACEHOLDER_NAME_PATTERN = r"[A-Za-z0-9_.-]+"
PLACEHOLDER_PATTERN = re.compile(
    r"\{\{(" + PLACEHOLDER_NAME_PATTERN + r")\}\}|\$\{(" + PLACEHOLDER_NAME_PATTERN + r")\}"
)
JSON_STRING_TOKEN_PATTERN = re.compile(
    r'"(?:\{\{(?P<brace>' + PLACEHOLDER_NAME_PATTERN + r')\}\}|\$\{(?P<dollar>' + PLACEHOLDER_NAME_PATTERN + r')\})"(?=\s*(?:[,}\]]|$))'
)
PLANNED_VALUE_PREFIX = "__planned__"


class FabricDeployError(RuntimeError):
    pass


@dataclass(frozen=True)
class ArtifactConfig:
    display_name: str
    item_type: str
    source: Path
    description: str = ""
    folder_id: str | None = None
    update_metadata: bool = False
    format: str | None = None
    part_path: str | None = None


@dataclass(frozen=True)
class JobConfig:
    name: str
    display_name: str
    item_type: str
    job_type: str
    wait: bool = True
    execution_data: dict[str, Any] | None = None
    parameters: list[dict[str, Any]] | None = None


@dataclass(frozen=True)
class DeploymentConfig:
    workspace_display_name: str
    placeholders: dict[str, Any]
    artifacts: list[ArtifactConfig]
    jobs: list[JobConfig]
    config_path: Path
    repo_root: Path


@dataclass
class DeploymentAction:
    artifact: ArtifactConfig
    action: str
    definition: dict[str, Any]
    existing_item: dict[str, Any] | None
    reason: str


def artifact_key(item_type: str, display_name: str) -> tuple[str, str]:
    return (item_type, display_name)


def artifact_config_key(artifact: ArtifactConfig) -> tuple[str, str]:
    return artifact_key(artifact.item_type, artifact.display_name)


def apply_cli_overrides(
    config: DeploymentConfig,
    *,
    environment: str | None = None,
    workspace_name: str | None = None,
) -> DeploymentConfig:
    placeholders = dict(config.placeholders)
    if environment is not None:
        placeholders["ENVIRONMENT"] = {"value": environment}
    return replace(
        config,
        workspace_display_name=workspace_name or config.workspace_display_name,
        placeholders=placeholders,
    )


def load_config(config_path: str | os.PathLike[str], repo_root: str | os.PathLike[str]) -> DeploymentConfig:
    config_file = Path(config_path).resolve()
    if not config_file.is_file():
        raise FabricDeployError(f"Config file not found: {config_file}")
    with config_file.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, Mapping):
        raise FabricDeployError("Config root must be a JSON object")

    workspace = raw.get("workspace")
    if not isinstance(workspace, Mapping) or not str(workspace.get("displayName", "")).strip():
        raise FabricDeployError("Config.workspace.displayName is required")

    placeholders = raw.get("placeholders", {})
    if placeholders is None:
        placeholders = {}
    if not isinstance(placeholders, Mapping):
        raise FabricDeployError("Config.placeholders must be a JSON object")

    artifacts_raw = raw.get("artifacts")
    if not isinstance(artifacts_raw, list) or not artifacts_raw:
        raise FabricDeployError("Config.artifacts must be a non-empty array")

    root = Path(repo_root).resolve()
    artifacts: list[ArtifactConfig] = []
    seen_artifacts: set[tuple[str, str]] = set()
    for index, entry in enumerate(artifacts_raw, start=1):
        if not isinstance(entry, Mapping):
            raise FabricDeployError(f"Artifact #{index} must be an object")
        display_name = str(entry.get("displayName", "")).strip()
        item_type = str(entry.get("type", "")).strip()
        source_value = str(entry.get("source", "")).strip()
        if not display_name:
            raise FabricDeployError(f"Artifact #{index} is missing displayName")
        if item_type not in SUPPORTED_ARTIFACT_TYPES:
            raise FabricDeployError(
                f"Artifact '{display_name}' has unsupported type '{item_type}'. "
                f"Supported types: {', '.join(sorted(SUPPORTED_ARTIFACT_TYPES))}"
            )
        if not source_value:
            raise FabricDeployError(f"Artifact '{display_name}' is missing source")
        source = (root / source_value).resolve()
        if not source.exists():
            raise FabricDeployError(f"Artifact '{display_name}' source does not exist: {source}")
        key = artifact_key(item_type, display_name)
        if key in seen_artifacts:
            raise FabricDeployError(f"Duplicate artifact mapping for {item_type} '{display_name}'")
        seen_artifacts.add(key)
        artifacts.append(
            ArtifactConfig(
                display_name=display_name,
                item_type=item_type,
                source=source,
                description=str(entry.get("description", "")).strip(),
                folder_id=str(entry.get("folderId")).strip() if entry.get("folderId") else None,
                update_metadata=bool(entry.get("updateMetadata", False)),
                format=str(entry.get("format")).strip() if entry.get("format") else None,
                part_path=str(entry.get("partPath")).strip() if entry.get("partPath") else None,
            )
        )

    jobs: list[JobConfig] = []
    for index, entry in enumerate(raw.get("jobs", []), start=1):
        if not isinstance(entry, Mapping):
            raise FabricDeployError(f"Job #{index} must be an object")
        name = str(entry.get("name", "")).strip()
        display_name = str(entry.get("displayName", "")).strip()
        item_type = str(entry.get("itemType", "")).strip()
        job_type = str(entry.get("jobType", "")).strip()
        if not name or not display_name or not item_type or not job_type:
            raise FabricDeployError(
                f"Job #{index} requires name, displayName, itemType, and jobType"
            )
        if job_type not in SUPPORTED_JOB_TYPES:
            raise FabricDeployError(
                f"Job '{name}' has unsupported jobType '{job_type}'. "
                f"Supported types: {', '.join(sorted(SUPPORTED_JOB_TYPES))}"
            )
        expected_item_type = JOB_TYPE_TO_ITEM_TYPE[job_type]
        if item_type != expected_item_type:
            raise FabricDeployError(
                f"Job '{name}' jobType '{job_type}' requires itemType '{expected_item_type}'"
            )
        parameters = entry.get("parameters")
        execution_data = entry.get("executionData")
        if parameters is not None and not isinstance(parameters, list):
            raise FabricDeployError(f"Job '{name}' parameters must be an array")
        if execution_data is not None and not isinstance(execution_data, Mapping):
            raise FabricDeployError(f"Job '{name}' executionData must be an object")
        jobs.append(
            JobConfig(
                name=name,
                display_name=display_name,
                item_type=item_type,
                job_type=job_type,
                wait=bool(entry.get("wait", True)),
                execution_data=dict(execution_data) if execution_data is not None else None,
                parameters=list(parameters) if parameters is not None else None,
            )
        )

    config = DeploymentConfig(
        workspace_display_name=str(workspace["displayName"]).strip(),
        placeholders=dict(placeholders),
        artifacts=artifacts,
        jobs=jobs,
        config_path=config_file,
        repo_root=root,
    )
    validate_placeholder_coverage(config)
    return config


def iter_source_files(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
        return
    for candidate in sorted(path.rglob("*")):
        if candidate.is_file():
            yield candidate


def artifact_has_platform_file(artifact: ArtifactConfig) -> bool:
    return any(source_file.name == ".platform" for source_file in iter_source_files(artifact.source))


def _match_placeholder_name(match: re.Match[str]) -> str:
    return str(match.group(1) or match.group(2) or match.group("brace") or match.group("dollar"))


def find_placeholders_in_text(value: str) -> list[str]:
    return sorted({_match_placeholder_name(match) for match in PLACEHOLDER_PATTERN.finditer(value)})


def scan_placeholders_in_object(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str):
        found.update(find_placeholders_in_text(value))
    elif isinstance(value, list):
        for item in value:
            found.update(scan_placeholders_in_object(item))
    elif isinstance(value, Mapping):
        for item in value.values():
            found.update(scan_placeholders_in_object(item))
    return found


def validate_placeholder_coverage(config: DeploymentConfig) -> None:
    declared = set(config.placeholders.keys())
    missing: list[str] = []
    for artifact in config.artifacts:
        if artifact.update_metadata and not artifact_has_platform_file(artifact):
            raise FabricDeployError(
                f"Artifact '{artifact.display_name}' sets updateMetadata=true but its source "
                "does not include a .platform file"
            )
        for source_file in iter_source_files(artifact.source):
            try:
                text = source_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for placeholder in find_placeholders_in_text(text):
                if placeholder not in declared:
                    missing.append(f"{placeholder} in {source_file}")
    for job in config.jobs:
        for placeholder in scan_placeholders_in_object(
            {"executionData": job.execution_data, "parameters": job.parameters}
        ):
            if placeholder not in declared:
                missing.append(f"{placeholder} in job '{job.name}'")
    if missing:
        raise FabricDeployError(
            "Unmapped placeholders were found:\n- " + "\n- ".join(sorted(missing))
        )


def collect_artifact_placeholders(artifact: ArtifactConfig) -> set[str]:
    found: set[str] = set()
    for source_file in iter_source_files(artifact.source):
        try:
            text = source_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        found.update(find_placeholders_in_text(text))
    return found


def collect_external_item_prerequisites(config: DeploymentConfig) -> list[tuple[str, str]]:
    declared = {artifact_config_key(artifact) for artifact in config.artifacts}
    external: set[tuple[str, str]] = set()
    for spec in config.placeholders.values():
        if not isinstance(spec, Mapping):
            continue
        if str(spec.get("from", "")).strip() != "item":
            continue
        item_type = str(spec.get("type", "")).strip()
        display_name = str(spec.get("displayName", "")).strip()
        if not item_type or not display_name:
            continue
        key = artifact_key(item_type, display_name)
        if key not in declared:
            external.add(key)
    return sorted(external)


def render_template_string(value: str, replacements: Mapping[str, Any]) -> tuple[str, list[str]]:
    unresolved: set[str] = set()

    def replacement(match: re.Match[str]) -> str:
        name = _match_placeholder_name(match)
        if name not in replacements:
            unresolved.add(name)
            return match.group(0)
        current = replacements[name]
        if isinstance(current, (dict, list)):
            return json.dumps(current, separators=(",", ":"))
        return str(current)

    rendered = PLACEHOLDER_PATTERN.sub(replacement, value)
    unresolved.update(find_placeholders_in_text(rendered))
    return rendered, sorted(unresolved)


def render_json_token_values(value: str, replacements: Mapping[str, Any]) -> tuple[str, list[str]]:
    unresolved: set[str] = set()

    def replacement(match: re.Match[str]) -> str:
        name = _match_placeholder_name(match)
        if name not in replacements:
            unresolved.add(name)
            return match.group(0)
        return json.dumps(replacements[name], separators=(",", ":"))

    rendered = JSON_STRING_TOKEN_PATTERN.sub(replacement, value)
    return rendered, sorted(unresolved)


def render_json_like(value: Any, replacements: Mapping[str, Any]) -> tuple[Any, list[str]]:
    unresolved: set[str] = set()
    if isinstance(value, str):
        full_match = PLACEHOLDER_PATTERN.fullmatch(value)
        if full_match:
            name = _match_placeholder_name(full_match)
            if name in replacements:
                return replacements[name], []
            unresolved.add(name)
            return value, sorted(unresolved)
        rendered, missing = render_template_string(value, replacements)
        unresolved.update(missing)
        return rendered, sorted(unresolved)
    if isinstance(value, list):
        rendered_items = []
        for item in value:
            rendered, missing = render_json_like(item, replacements)
            unresolved.update(missing)
            rendered_items.append(rendered)
        return rendered_items, sorted(unresolved)
    if isinstance(value, Mapping):
        rendered_items: dict[str, Any] = {}
        for key, item in value.items():
            rendered, missing = render_json_like(item, replacements)
            unresolved.update(missing)
            rendered_items[str(key)] = rendered
        return rendered_items, sorted(unresolved)
    return value, []


def is_probably_json_text(value: str) -> bool:
    stripped = value.strip()
    return (stripped.startswith("{") and stripped.endswith("}")) or (
        stripped.startswith("[") and stripped.endswith("]")
    )


def render_text_template(value: str, replacements: Mapping[str, Any]) -> tuple[str, list[str]]:
    rendered = value
    if is_probably_json_text(value):
        rendered, _ = render_json_token_values(rendered, replacements)
    rendered, _ = render_template_string(rendered, replacements)
    return rendered, find_placeholders_in_text(rendered)


def render_bytes_template(
    raw_bytes: bytes, replacements: Mapping[str, Any]
) -> tuple[bytes, list[str]]:
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return raw_bytes, []
    rendered_text, unresolved = render_text_template(text, replacements)
    return rendered_text.encode("utf-8"), unresolved


def make_relative_part_path(artifact: ArtifactConfig, file_path: Path) -> str:
    if artifact.source.is_file():
        if artifact.part_path:
            return artifact.part_path
        if artifact.item_type == "Notebook":
            return "notebook-content.ipynb"
        return artifact.source.name
    return file_path.relative_to(artifact.source).as_posix()


def render_artifact_definition(
    artifact: ArtifactConfig, replacements: Mapping[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    parts: dict[str, bytes] = {}
    unresolved: set[str] = set()
    for source_file in iter_source_files(artifact.source):
        rendered_bytes, missing = render_bytes_template(source_file.read_bytes(), replacements)
        unresolved.update(missing)
        parts[make_relative_part_path(artifact, source_file)] = rendered_bytes
    definition = encode_definition_parts(parts)
    if artifact.format:
        definition["format"] = artifact.format
    return definition, sorted(unresolved)


def definition_signature(definition: Mapping[str, Any]) -> dict[str, str]:
    decoded = decode_definition_parts(definition)
    signature = {
        path: hashlib.sha256(content).hexdigest()
        for path, content in sorted(decoded.items())
    }
    signature["__format__"] = str(definition.get("format") or "")
    return signature


def planned_placeholder_value(
    *,
    item_type: str,
    display_name: str,
    property_name: str,
) -> Any:
    if property_name == "displayName":
        return display_name
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", display_name)
    return f"{PLANNED_VALUE_PREFIX}{item_type}.{safe_name}.{property_name}"


def resolve_placeholders(
    config: DeploymentConfig,
    client: FabricApiClient,
    workspace: Mapping[str, Any],
    *,
    deferred_items: set[tuple[str, str]] | None = None,
    required_names: set[str] | None = None,
) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    planned_items = deferred_items or set()
    for name, spec in config.placeholders.items():
        if required_names is not None and name not in required_names:
            continue
        if isinstance(spec, Mapping):
            if "value" in spec:
                resolved[name] = spec["value"]
                continue
            source_kind = str(spec.get("from", "")).strip()
            property_name = str(spec.get("property", "id")).strip() or "id"
            if source_kind == "workspace":
                if property_name not in workspace:
                    raise FabricDeployError(
                        f"Placeholder '{name}' requested missing workspace property '{property_name}'"
                    )
                resolved[name] = workspace[property_name]
                continue
            if source_kind == "item":
                item_type = str(spec.get("type", "")).strip()
                display_name = str(spec.get("displayName", "")).strip()
                if not item_type or not display_name:
                    raise FabricDeployError(
                        f"Placeholder '{name}' with from=item requires type and displayName"
                    )
                item = client.find_item_by_display_name(
                    str(workspace["id"]),
                    display_name,
                    item_type,
                    allow_missing=True,
                )
                if item is not None:
                    if property_name not in item:
                        raise FabricDeployError(
                            f"Placeholder '{name}' requested missing item property '{property_name}'"
                        )
                    resolved[name] = item[property_name]
                    continue
                if artifact_key(item_type, display_name) in planned_items:
                    resolved[name] = planned_placeholder_value(
                        item_type=item_type,
                        display_name=display_name,
                        property_name=property_name,
                    )
                    continue
                raise FabricDeployError(
                    f"Placeholder '{name}' could not resolve {item_type} '{display_name}'"
                )
            raise FabricDeployError(
                f"Placeholder '{name}' must define either value, from=workspace, or from=item"
            )
        resolved[name] = spec
    return resolved


def definition_contains_planned_values(definition: Mapping[str, Any]) -> bool:
    return any(
        PLANNED_VALUE_PREFIX.encode("utf-8") in payload
        for payload in decode_definition_parts(definition).values()
    )


def build_plan(
    config: DeploymentConfig,
    client: FabricApiClient,
) -> tuple[dict[str, Any], dict[str, Any], list[DeploymentAction]]:
    workspace = client.find_workspace_by_display_name(
        config.workspace_display_name, allow_missing=False
    )
    if workspace is None:
        raise FabricDeployError(f"Workspace '{config.workspace_display_name}' was not found")

    planned_items: set[tuple[str, str]] = set()
    replacements: dict[str, Any] = {}
    actions: list[DeploymentAction] = []
    workspace_id = str(workspace["id"])
    for artifact in config.artifacts:
        required_names = collect_artifact_placeholders(artifact)
        replacements = resolve_placeholders(
            config,
            client,
            workspace,
            deferred_items=planned_items,
            required_names=required_names,
        )
        definition, unresolved = render_artifact_definition(artifact, replacements)
        if unresolved:
            raise FabricDeployError(
                f"Artifact '{artifact.display_name}' still has unresolved placeholders: "
                + ", ".join(sorted(unresolved))
            )
        existing = client.find_item_by_display_name(
            workspace_id,
            artifact.display_name,
            artifact.item_type,
            allow_missing=True,
        )
        if existing is None:
            reason = "Item not found in target workspace"
            if definition_contains_planned_values(definition):
                reason += "; earlier config dependencies are represented as planned values"
            actions.append(
                DeploymentAction(
                    artifact=artifact,
                    action="create",
                    definition=definition,
                    existing_item=None,
                    reason=reason,
                )
            )
        else:
            remote_definition = client.get_item_definition(
                workspace_id,
                str(existing["id"]),
                definition_format=artifact.format,
            )
            if definition_signature(definition) == definition_signature(remote_definition):
                action_name = "noop"
                reason = "Definition already matches remote item"
            else:
                action_name = "update"
                reason = "Definition differs from remote item"
                if definition_contains_planned_values(definition):
                    reason += "; earlier config dependencies are represented as planned values"
            actions.append(
                DeploymentAction(
                    artifact=artifact,
                    action=action_name,
                    definition=definition,
                    existing_item=existing,
                    reason=reason,
                )
            )
        planned_items.add(artifact_config_key(artifact))
    return workspace, replacements, actions


def command_validate(config: DeploymentConfig, out: Any) -> int:
    print(f"Config: {config.config_path}", file=out)
    print(f"Workspace: {config.workspace_display_name}", file=out)
    print(f"Artifacts: {len(config.artifacts)}", file=out)
    print(f"Jobs: {len(config.jobs)}", file=out)
    print("Validate is local only; no live Fabric calls are made.", file=out)
    print("Plan/deploy require the target workspace and referenced external items.", file=out)
    print("Run additionally requires seeded landing files for the sample data flows.", file=out)
    print("External prerequisites:", file=out)
    print(f"- Workspace: {config.workspace_display_name}", file=out)
    for item_type, display_name in collect_external_item_prerequisites(config):
        print(f"- {item_type}: {display_name}", file=out)
    print("Validation succeeded.", file=out)
    return 0


def command_plan(config: DeploymentConfig, client: FabricApiClient, out: Any) -> int:
    workspace, replacements, actions = build_plan(config, client)
    print(
        f"Workspace '{workspace['displayName']}' ({workspace['id']}) with "
        f"{len(replacements)} resolved placeholders",
        file=out,
    )
    for action in actions:
        print(
            f"{action.action.upper():6} {action.artifact.item_type:13} "
            f"{action.artifact.display_name} :: {action.reason}",
            file=out,
        )
    return 0


def command_deploy(config: DeploymentConfig, client: FabricApiClient, out: Any) -> int:
    workspace = client.find_workspace_by_display_name(
        config.workspace_display_name, allow_missing=False
    )
    if workspace is None:
        raise FabricDeployError(f"Workspace '{config.workspace_display_name}' was not found")

    workspace_id = str(workspace["id"])
    for artifact in config.artifacts:
        replacements = resolve_placeholders(
            config,
            client,
            workspace,
            required_names=collect_artifact_placeholders(artifact),
        )
        definition, unresolved = render_artifact_definition(artifact, replacements)
        if unresolved:
            raise FabricDeployError(
                f"Artifact '{artifact.display_name}' still has unresolved placeholders: "
                + ", ".join(sorted(unresolved))
            )
        existing = client.find_item_by_display_name(
            workspace_id,
            artifact.display_name,
            artifact.item_type,
            allow_missing=True,
        )
        if existing is None:
            created = client.create_item(
                workspace_id,
                display_name=artifact.display_name,
                item_type=artifact.item_type,
                definition=definition,
                description=artifact.description or None,
                folder_id=artifact.folder_id,
            )
            print(f"CREATE {artifact.display_name} :: id={created.get('id')}", file=out)
            continue
        remote_definition = client.get_item_definition(
            workspace_id,
            str(existing["id"]),
            definition_format=artifact.format,
        )
        if definition_signature(definition) == definition_signature(remote_definition):
            print(f"SKIP   {artifact.display_name} :: already current", file=out)
            continue
        client.update_item_definition(
            workspace_id,
            str(existing["id"]),
            definition=definition,
            update_metadata=artifact.update_metadata,
        )
        print(f"UPDATE {artifact.display_name} :: id={existing['id']}", file=out)
    return 0


def command_run(
    config: DeploymentConfig,
    client: FabricApiClient,
    out: Any,
    *,
    job_name: str | None = None,
) -> int:
    workspace = client.find_workspace_by_display_name(
        config.workspace_display_name, allow_missing=False
    )
    if workspace is None:
        raise FabricDeployError(f"Workspace '{config.workspace_display_name}' was not found")
    selected_jobs = [job for job in config.jobs if job_name in (None, job.name)]
    if not selected_jobs:
        raise FabricDeployError("No jobs matched the requested filter")
    for job in selected_jobs:
        required_names = scan_placeholders_in_object(
            {"executionData": job.execution_data, "parameters": job.parameters}
        )
        replacements = resolve_placeholders(
            config,
            client,
            workspace,
            required_names=required_names,
        )
        item = client.find_item_by_display_name(
            str(workspace["id"]),
            job.display_name,
            job.item_type,
            allow_missing=False,
        )
        if item is None:
            raise FabricDeployError(
                f"Run target {job.item_type} '{job.display_name}' was not found"
            )
        execution_data, unresolved_execution = render_json_like(job.execution_data, replacements)
        parameters, unresolved_parameters = render_json_like(job.parameters, replacements)
        unresolved = sorted(set(unresolved_execution) | set(unresolved_parameters))
        if unresolved:
            raise FabricDeployError(
                f"Job '{job.name}' still has unresolved placeholders: {', '.join(unresolved)}"
            )
        result = client.run_item_job(
            str(workspace["id"]),
            str(item["id"]),
            job_type=job.job_type,
            execution_data=execution_data if isinstance(execution_data, Mapping) else None,
            parameters=parameters if isinstance(parameters, list) else None,
            wait=job.wait,
        )
        print(
            f"RUN    {job.name} :: {job.job_type} on {job.display_name} -> {result.get('status')}",
            file=out,
        )
    return 0


def command_verify(config: DeploymentConfig, client: FabricApiClient, out: Any) -> int:
    workspace = client.find_workspace_by_display_name(
        config.workspace_display_name, allow_missing=False
    )
    if workspace is None:
        raise FabricDeployError(f"Workspace '{config.workspace_display_name}' was not found")

    workspace_id = str(workspace["id"])
    verified = 0
    for artifact in config.artifacts:
        replacements = resolve_placeholders(
            config,
            client,
            workspace,
            required_names=collect_artifact_placeholders(artifact),
        )
        definition, unresolved = render_artifact_definition(artifact, replacements)
        if unresolved:
            raise FabricDeployError(
                f"Artifact '{artifact.display_name}' still has unresolved placeholders: "
                + ", ".join(sorted(unresolved))
            )
        existing = client.find_item_by_display_name(
            workspace_id,
            artifact.display_name,
            artifact.item_type,
            allow_missing=False,
        )
        if existing is None:
            raise FabricDeployError(
                f"Verify target {artifact.item_type} '{artifact.display_name}' was not found"
            )
        remote_definition = client.get_item_definition(
            workspace_id,
            str(existing["id"]),
            definition_format=artifact.format,
        )
        if definition_signature(definition) != definition_signature(remote_definition):
            raise FabricDeployError(
                f"Definition mismatch for {artifact.item_type} '{artifact.display_name}'"
            )
        verified += 1
        print(f"OK     {artifact.item_type:13} {artifact.display_name}", file=out)
    print(f"Verified {verified} artifact(s).", file=out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Optional Microsoft Fabric deployment helper")
    parser.add_argument(
        "--config",
        default="scripts/fabric/config.json",
        help="Path to deployment config JSON",
    )
    parser.add_argument(
        "--repo-root",
        default=os.getcwd(),
        help="Repository root used to resolve artifact source paths",
    )
    parser.add_argument(
        "--environment",
        help="Override the ENVIRONMENT placeholder value for this invocation",
    )
    parser.add_argument(
        "--workspace-name",
        help="Override workspace.displayName for this invocation",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate local config and source mappings")
    subparsers.add_parser("plan", help="Dry-run deployment plan")
    subparsers.add_parser("deploy", help="Create or update configured Fabric items")
    run_parser = subparsers.add_parser("run", help="Run configured Fabric jobs")
    run_parser.add_argument("--job", help="Optional job name filter")
    subparsers.add_parser("verify", help="Compare local rendered definitions to remote items")
    return parser


def run_cli(
    argv: list[str] | None = None,
    *,
    client: FabricApiClient | None = None,
    out: Any = None,
    err: Any = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    stdout = out or sys.stdout
    stderr = err or sys.stderr
    try:
        config = load_config(args.config, args.repo_root)
        config = apply_cli_overrides(
            config,
            environment=getattr(args, "environment", None),
            workspace_name=getattr(args, "workspace_name", None),
        )
        if args.command == "validate":
            return command_validate(config, stdout)
        active_client = client or FabricApiClient()
        if args.command == "plan":
            return command_plan(config, active_client, stdout)
        if args.command == "deploy":
            return command_deploy(config, active_client, stdout)
        if args.command == "run":
            return command_run(config, active_client, stdout, job_name=getattr(args, "job", None))
        if args.command == "verify":
            return command_verify(config, active_client, stdout)
        parser.error(f"Unknown command: {args.command}")
        return 2
    except (FabricDeployError, FabricApiError) as exc:
        print(f"ERROR: {exc}", file=stderr)
        return 1


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
