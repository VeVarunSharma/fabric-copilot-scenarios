from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.fabric import deploy
from scripts.fabric.fabric_api import (
    FabricApiClient,
    FabricApiError,
    HttpResponse,
    decode_definition_parts,
    redact_sensitive_text,
)


class FakeTokenProvider:
    def get_token(self, resource: str = "") -> str:
        return "fake-token"


class FakeTransport:
    def __init__(self, responses: list[HttpResponse]) -> None:
        self.responses = list(responses)
        self.requests: list[tuple[str, str, dict[str, str], bytes | None]] = []

    def request(self, method: str, url: str, *, headers, body=None) -> HttpResponse:
        self.requests.append((method, url, dict(headers), body))
        if not self.responses:
            raise AssertionError(f"No fake response left for {method} {url}")
        return self.responses.pop(0)


class FakeFabricClient:
    def __init__(self, *, empty: bool = False) -> None:
        self.workspace = {"id": "workspace-1", "displayName": "Demo Workspace"}
        self.items = {} if empty else {
            ("Notebook", "Notebook One"): {"id": "nb-1", "displayName": "Notebook One", "type": "Notebook"},
            ("Lakehouse", "Shared Lakehouse"): {
                "id": "lh-1",
                "displayName": "Shared Lakehouse",
                "type": "Lakehouse",
            },
        }
        self.definitions: dict[str, dict[str, object]] = {}
        self.created: list[dict[str, object]] = []
        self.updated: list[str] = []

    def find_workspace_by_display_name(self, display_name: str, *, allow_missing: bool = False):
        if display_name == self.workspace["displayName"]:
            return self.workspace
        if allow_missing:
            return None
        raise FabricApiError("workspace missing")

    def find_item_by_display_name(
        self,
        workspace_id: str,
        display_name: str,
        item_type: str,
        *,
        allow_missing: bool = False,
    ):
        item = self.items.get((item_type, display_name))
        if item is None and not allow_missing:
            raise FabricApiError("item missing")
        return item

    def get_item_definition(self, workspace_id: str, item_id: str, definition_format: str | None = None):
        return self.definitions[item_id]

    def create_item(
        self,
        workspace_id: str,
        *,
        display_name: str,
        item_type: str,
        definition,
        description=None,
        folder_id=None,
    ):
        item_id = f"created-{len(self.created) + 1}"
        item = {"id": item_id, "displayName": display_name, "type": item_type}
        self.items[(item_type, display_name)] = item
        self.definitions[item_id] = definition
        self.created.append(
            {
                "workspace_id": workspace_id,
                "display_name": display_name,
                "item_type": item_type,
                "item_id": item_id,
                "definition": definition,
                "description": description,
                "folder_id": folder_id,
            }
        )
        return item

    def update_item_definition(self, workspace_id: str, item_id: str, *, definition, update_metadata=False):
        self.updated.append(item_id)
        self.definitions[item_id] = definition

    def run_item_job(self, workspace_id: str, item_id: str, *, job_type: str, execution_data=None, parameters=None, wait=True):
        return {"status": "Completed", "id": "job-1", "jobType": job_type}


class FabricApiTests(unittest.TestCase):
    def make_client(self, responses: list[HttpResponse], sleeps: list[float] | None = None) -> tuple[FabricApiClient, FakeTransport]:
        sleep_calls = sleeps if sleeps is not None else []
        transport = FakeTransport(responses)
        client = FabricApiClient(
            token_provider=FakeTokenProvider(),
            transport=transport,
            sleep=lambda seconds: sleep_calls.append(seconds),
            max_retries=3,
            poll_interval_seconds=1,
        )
        return client, transport

    def test_pagination_uses_continuation_uri(self) -> None:
        client, _ = self.make_client(
            [
                HttpResponse(
                    200,
                    {},
                    json.dumps(
                        {
                            "value": [{"displayName": "A"}],
                            "continuationUri": "https://api.fabric.microsoft.com/v1/workspaces?continuationToken=next",
                        }
                    ).encode("utf-8"),
                ),
                HttpResponse(200, {}, json.dumps({"value": [{"displayName": "B"}]}).encode("utf-8")),
            ]
        )
        items = list(client.iter_paginated("/workspaces"))
        self.assertEqual(["A", "B"], [item["displayName"] for item in items])

    def test_client_uses_configured_token_resource(self) -> None:
        resources: list[str] = []

        class RecordingTokenProvider:
            def get_token(self, resource: str = "") -> str:
                resources.append(resource)
                return "fake-token"

        transport = FakeTransport(
            [HttpResponse(200, {}, json.dumps({"value": []}).encode("utf-8"))]
        )
        client = FabricApiClient(
            token_provider=RecordingTokenProvider(),
            token_resource="https://analysis.windows.net/powerbi/api",
            transport=transport,
        )
        client.request_json("GET", "/capacities", expected_statuses={200})
        self.assertEqual(
            ["https://analysis.windows.net/powerbi/api"],
            resources,
        )

    def test_find_item_raises_on_multiple_matches(self) -> None:
        class DuplicateClient(FabricApiClient):
            def list_items(self, workspace_id: str, *, item_type=None, root_folder_id=None, recursive=True):
                return [
                    {"id": "1", "displayName": "Same", "type": item_type},
                    {"id": "2", "displayName": "Same", "type": item_type},
                ]

        client = DuplicateClient(token_provider=FakeTokenProvider(), transport=FakeTransport([]))
        with self.assertRaises(FabricApiError):
            client.find_item_by_display_name("workspace-1", "Same", "Notebook")

    def test_get_item_definition_posts_empty_json_with_format(self) -> None:
        client, transport = self.make_client(
            [
                HttpResponse(
                    200,
                    {},
                    json.dumps({"definition": {"format": "ipynb", "parts": []}}).encode("utf-8"),
                )
            ]
        )
        definition = client.get_item_definition("w1", "i1", definition_format="ipynb")
        self.assertEqual("ipynb", definition["format"])
        method, url, _headers, body = transport.requests[0]
        self.assertEqual("POST", method)
        self.assertIn("format=ipynb", url)
        self.assertEqual(b"{}", body)

    def test_lro_success_fetches_result(self) -> None:
        sleep_calls: list[float] = []
        client, _ = self.make_client(
            [
                HttpResponse(
                    202,
                    {"location": "https://api.fabric.microsoft.com/v1/operations/op-1", "x-ms-operation-id": "op-1"},
                    b"",
                ),
                HttpResponse(200, {"retry-after": "1"}, json.dumps({"status": "Running"}).encode("utf-8")),
                HttpResponse(200, {}, json.dumps({"status": "Succeeded"}).encode("utf-8")),
                HttpResponse(200, {}, json.dumps({"definition": {"parts": []}}).encode("utf-8")),
            ],
            sleep_calls,
        )
        result = client.request_json(
            "POST",
            "/workspaces/w1/items/i1/getDefinition",
            payload={},
            expected_statuses={200, 202},
        )
        definition = client.poll_operation(
            location=result.headers.get("location"),
            operation_id=result.headers.get("x-ms-operation-id"),
            result_required=True,
        )
        self.assertEqual({"definition": {"parts": []}}, definition)
        self.assertEqual([1], sleep_calls)

    def test_lro_failure_raises_explicit_error(self) -> None:
        client, _ = self.make_client(
            [
                HttpResponse(
                    200,
                    {},
                    json.dumps(
                        {
                            "status": "Failed",
                            "error": {"errorCode": "BadThing", "message": "boom", "requestId": "req-1"},
                        }
                    ).encode("utf-8"),
                )
            ]
        )
        with self.assertRaises(FabricApiError) as caught:
            client.poll_operation(
                location="https://api.fabric.microsoft.com/v1/operations/op-1",
                operation_id="op-1",
                result_required=False,
            )
        self.assertIn("boom", str(caught.exception))
        self.assertIn("requestId=req-1", str(caught.exception))

    def test_transient_retry_honors_retry_after(self) -> None:
        sleep_calls: list[float] = []
        client, transport = self.make_client(
            [
                HttpResponse(429, {"retry-after": "3"}, json.dumps({"message": "slow down"}).encode("utf-8")),
                HttpResponse(200, {}, json.dumps({"value": []}).encode("utf-8")),
            ],
            sleep_calls,
        )
        result = client.request_json("GET", "/workspaces", expected_statuses={200})
        self.assertEqual([], result.body["value"])
        self.assertEqual([3], sleep_calls)
        self.assertEqual(2, len(transport.requests))

    def test_run_item_job_uses_query_endpoint_and_nested_parameters(self) -> None:
        client, transport = self.make_client(
            [
                HttpResponse(202, {"location": "https://api.fabric.microsoft.com/job/1"}, b""),
            ]
        )
        result = client.run_item_job(
            "w1",
            "i1",
            job_type="Run Notebook",
            execution_data={"mode": "full"},
            parameters=[{"name": "ENVIRONMENT", "value": "dev", "type": "Text"}],
            wait=False,
        )
        self.assertEqual("Accepted", result["status"])
        method, url, _headers, body = transport.requests[0]
        self.assertEqual("POST", method)
        self.assertIn("/jobs/instances?", url)
        self.assertIn("jobType=Run+Notebook", url)
        payload = json.loads(body.decode("utf-8"))
        self.assertEqual("full", payload["executionData"]["mode"])
        self.assertEqual("ENVIRONMENT", payload["executionData"]["parameters"][0]["name"])
        self.assertNotIn("parameters", payload)

    def test_redaction_removes_bearer_token(self) -> None:
        raw = 'Authorization: Bearer abc.def.ghi "accessToken":"secret-value"'
        redacted = redact_sensitive_text(raw)
        self.assertNotIn("abc.def.ghi", redacted)
        self.assertNotIn("secret-value", redacted)
        self.assertIn("<redacted>", redacted)

    def test_definition_encoding_round_trips(self) -> None:
        definition = deploy.encode_definition_parts({"a.txt": b"hello", "b.json": b'{"x":1}'})
        decoded = decode_definition_parts(definition)
        self.assertEqual(b"hello", decoded["a.txt"])
        self.assertEqual(b'{"x":1}', decoded["b.json"])


class DeployModuleTests(unittest.TestCase):
    def test_find_placeholders_in_text_supports_both_forms(self) -> None:
        found = deploy.find_placeholders_in_text(
            "a={{WORKSPACE_ID}} b=${WORKSPACE_ID} c=${LAKEHOUSE_ID}"
        )
        self.assertEqual(["LAKEHOUSE_ID", "WORKSPACE_ID"], found)

    def test_placeholder_substitution_and_unresolved_detection(self) -> None:
        rendered, unresolved = deploy.render_template_string(
            "workspace={{WORKSPACE_ID}} suffix=${WORKSPACE_ID} missing=${MISSING}",
            {"WORKSPACE_ID": "abc"},
        )
        self.assertEqual("workspace=abc suffix=abc missing=${MISSING}", rendered)
        self.assertEqual(["MISSING"], unresolved)

    def test_render_json_like_preserves_typed_full_value_for_both_forms(self) -> None:
        rendered, unresolved = deploy.render_json_like(
            {
                "number1": "{{PORT}}",
                "number2": "${PORT}",
                "flag1": "{{ENABLED}}",
                "flag2": "${ENABLED}",
                "suffix": "port-${PORT}",
            },
            {"PORT": 443, "ENABLED": True},
        )
        self.assertEqual([], unresolved)
        self.assertEqual(443, rendered["number1"])
        self.assertEqual(443, rendered["number2"])
        self.assertIs(True, rendered["flag1"])
        self.assertIs(True, rendered["flag2"])
        self.assertEqual("port-443", rendered["suffix"])

    def test_render_artifact_definition_renames_notebook_and_sets_format(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            notebook_file = root / "01_bronze_ingestion.ipynb"
            notebook_file.write_text(
                json.dumps({"workspaceId": "${WORKSPACE_ID}", "enabled": "${ENABLED}"}),
                encoding="utf-8",
            )
            artifact = deploy.ArtifactConfig(
                display_name="Notebook One",
                item_type="Notebook",
                source=notebook_file,
                format="ipynb",
                part_path="notebook-content.ipynb",
            )
            definition, unresolved = deploy.render_artifact_definition(
                artifact,
                {"WORKSPACE_ID": 123, "ENABLED": True},
            )
            self.assertEqual([], unresolved)
            self.assertEqual("ipynb", definition["format"])
            decoded = decode_definition_parts(definition)
            self.assertEqual(["notebook-content.ipynb"], sorted(decoded))
            payload = json.loads(decoded["notebook-content.ipynb"].decode("utf-8"))
            self.assertEqual(123, payload["workspaceId"])
            self.assertIs(True, payload["enabled"])

    def test_definition_signature_includes_format(self) -> None:
        definition_ipynb = {"format": "ipynb", **deploy.encode_definition_parts({"a.txt": b"same"})}
        definition_tmdl = {"format": "TMDL", **deploy.encode_definition_parts({"a.txt": b"same"})}
        self.assertNotEqual(
            deploy.definition_signature(definition_ipynb),
            deploy.definition_signature(definition_tmdl),
        )

    def test_config_validation_rejects_missing_placeholder_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "notebooks" / "demo"
            source.mkdir(parents=True)
            (source / "notebook.ipynb").write_text(
                '{"workspace":"${WORKSPACE_ID}"}',
                encoding="utf-8",
            )
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "workspace": {"displayName": "Demo Workspace"},
                        "placeholders": {},
                        "artifacts": [
                            {"displayName": "Notebook One", "type": "Notebook", "source": "notebooks/demo"}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(deploy.FabricDeployError) as caught:
                deploy.load_config(config_path, root)
            self.assertIn("WORKSPACE_ID", str(caught.exception))

    def test_config_validation_rejects_update_metadata_without_platform(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            notebook_file = root / "notebook.ipynb"
            notebook_file.write_text('{"workspace":"${WORKSPACE_ID}"}', encoding="utf-8")
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "workspace": {"displayName": "Demo Workspace"},
                        "placeholders": {
                            "WORKSPACE_ID": {"from": "workspace", "property": "id"}
                        },
                        "artifacts": [
                            {
                                "displayName": "Notebook One",
                                "type": "Notebook",
                                "source": "notebook.ipynb",
                                "format": "ipynb",
                                "partPath": "notebook-content.ipynb",
                                "updateMetadata": True
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(deploy.FabricDeployError) as caught:
                deploy.load_config(config_path, root)
            self.assertIn(".platform", str(caught.exception))

    def test_apply_cli_overrides_updates_environment_and_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            notebook_file = root / "notebook.ipynb"
            notebook_file.write_text('{"environment":"${ENVIRONMENT}"}', encoding="utf-8")
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "workspace": {"displayName": "Demo Workspace"},
                        "placeholders": {"ENVIRONMENT": {"value": "dev"}},
                        "artifacts": [
                            {
                                "displayName": "Notebook One",
                                "type": "Notebook",
                                "source": "notebook.ipynb",
                                "format": "ipynb",
                                "partPath": "notebook-content.ipynb"
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            config = deploy.load_config(config_path, root)
            overridden = deploy.apply_cli_overrides(
                config,
                environment="test",
                workspace_name="Override Workspace",
            )
            self.assertEqual("Demo Workspace", config.workspace_display_name)
            self.assertEqual("dev", config.placeholders["ENVIRONMENT"]["value"])
            self.assertEqual("Override Workspace", overridden.workspace_display_name)
            self.assertEqual("test", overridden.placeholders["ENVIRONMENT"]["value"])

    def test_validate_reports_external_prerequisites_and_overrides(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        config_path = repo_root / "scripts" / "fabric" / "config.example.json"
        out = io.StringIO()
        err = io.StringIO()
        result = deploy.run_cli(
            [
                "--config",
                str(config_path),
                "--repo-root",
                str(repo_root),
                "--environment",
                "test",
                "--workspace-name",
                "Fabric Copilot Scenarios - Test",
                "validate",
            ],
            out=out,
            err=err,
        )
        self.assertEqual(0, result)
        output = out.getvalue()
        self.assertIn("Workspace: Fabric Copilot Scenarios - Test", output)
        self.assertIn("Validate is local only", output)
        self.assertIn("Plan/deploy require the target workspace", output)
        self.assertIn("Run additionally requires seeded landing files", output)
        self.assertIn("- Workspace: Fabric Copilot Scenarios - Test", output)
        self.assertIn("- Lakehouse: RetailLakehouse", output)
        self.assertEqual("", err.getvalue())

    def test_cli_plan_reports_noop(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "notebooks" / "demo"
            source.mkdir(parents=True)
            (source / "notebook.ipynb").write_text(
                '{"lakehouse":"${LAKEHOUSE_ID}","workspace":"{{WORKSPACE_ID}}"}',
                encoding="utf-8",
            )
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "workspace": {"displayName": "Demo Workspace"},
                        "placeholders": {
                            "WORKSPACE_ID": {"from": "workspace", "property": "id"},
                            "LAKEHOUSE_ID": {
                                "from": "item",
                                "type": "Lakehouse",
                                "displayName": "Shared Lakehouse",
                                "property": "id",
                            }
                        },
                        "artifacts": [
                            {
                                "displayName": "Notebook One",
                                "type": "Notebook",
                                "source": "notebooks/demo/notebook.ipynb",
                                "format": "ipynb",
                                "partPath": "notebook-content.ipynb"
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            client = FakeFabricClient()
            config = deploy.load_config(config_path, root)
            workspace = client.find_workspace_by_display_name("Demo Workspace")
            replacements = deploy.resolve_placeholders(config, client, workspace)
            definition, unresolved = deploy.render_artifact_definition(config.artifacts[0], replacements)
            self.assertEqual([], unresolved)
            client.definitions["nb-1"] = definition
            workspace, replacements, actions = deploy.build_plan(config, client)
            out = io.StringIO()
            err = io.StringIO()
            result = deploy.run_cli(
                [
                    "--config",
                    str(config_path),
                    "--repo-root",
                    str(root),
                    "plan",
                ],
                client=client,
                out=out,
                err=err,
            )
            self.assertEqual(0, result)
            self.assertEqual("Demo Workspace", workspace["displayName"])
            self.assertEqual("lh-1", replacements["LAKEHOUSE_ID"])
            self.assertEqual("noop", actions[0].action)
            self.assertIn("NOOP", out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_cli_plan_honors_workspace_name_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            notebook_file = root / "notebook.ipynb"
            notebook_file.write_text('{"workspace":"${WORKSPACE_ID}"}', encoding="utf-8")
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "workspace": {"displayName": "Demo Workspace"},
                        "placeholders": {
                            "WORKSPACE_ID": {"from": "workspace", "property": "id"},
                        },
                        "artifacts": [
                            {
                                "displayName": "Notebook One",
                                "type": "Notebook",
                                "source": "notebook.ipynb",
                                "format": "ipynb",
                                "partPath": "notebook-content.ipynb"
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            client = FakeFabricClient()
            client.workspace["displayName"] = "Override Workspace"
            config = deploy.load_config(config_path, root)
            workspace = client.find_workspace_by_display_name("Override Workspace")
            replacements = deploy.resolve_placeholders(config, client, workspace)
            definition, unresolved = deploy.render_artifact_definition(config.artifacts[0], replacements)
            self.assertEqual([], unresolved)
            client.definitions["nb-1"] = definition
            out = io.StringIO()
            err = io.StringIO()
            result = deploy.run_cli(
                [
                    "--config",
                    str(config_path),
                    "--repo-root",
                    str(root),
                    "--workspace-name",
                    "Override Workspace",
                    "plan",
                ],
                client=client,
                out=out,
                err=err,
            )
            self.assertEqual(0, result)
            self.assertIn("Workspace 'Override Workspace' (workspace-1)", out.getvalue())
            self.assertEqual("", err.getvalue())

    def test_plan_and_deploy_handle_empty_workspace_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            notebooks_dir = root / "notebooks"
            notebooks_dir.mkdir()
            pipeline_dir = root / "pipeline"
            pipeline_dir.mkdir()
            (notebooks_dir / "bronze.ipynb").write_text(
                json.dumps({"workspaceId": "${WORKSPACE_ID}"}),
                encoding="utf-8",
            )
            (pipeline_dir / ".platform").write_text("{}", encoding="utf-8")
            (pipeline_dir / "pipeline-content.json").write_text(
                json.dumps({"notebookId": "${NOTEBOOK_ID_BRONZE}", "workspaceId": "${WORKSPACE_ID}"}),
                encoding="utf-8",
            )
            config_path = root / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "workspace": {"displayName": "Demo Workspace"},
                        "placeholders": {
                            "WORKSPACE_ID": {"from": "workspace", "property": "id"},
                            "NOTEBOOK_ID_BRONZE": {
                                "from": "item",
                                "type": "Notebook",
                                "displayName": "Bronze Notebook",
                                "property": "id"
                            }
                        },
                        "artifacts": [
                            {
                                "displayName": "Bronze Notebook",
                                "type": "Notebook",
                                "source": "notebooks/bronze.ipynb",
                                "format": "ipynb",
                                "partPath": "notebook-content.ipynb"
                            },
                            {
                                "displayName": "Retail Pipeline",
                                "type": "DataPipeline",
                                "source": "pipeline"
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            client = FakeFabricClient(empty=True)
            config = deploy.load_config(config_path, root)

            _workspace, _replacements, actions = deploy.build_plan(config, client)
            self.assertEqual(["create", "create"], [action.action for action in actions])
            planned_pipeline = json.loads(
                decode_definition_parts(actions[1].definition)["pipeline-content.json"].decode("utf-8")
            )
            self.assertTrue(
                str(planned_pipeline["notebookId"]).startswith(deploy.PLANNED_VALUE_PREFIX)
            )

            out = io.StringIO()
            result = deploy.command_deploy(config, client, out)
            self.assertEqual(0, result)
            self.assertEqual(
                ["Bronze Notebook", "Retail Pipeline"],
                [entry["display_name"] for entry in client.created],
            )
            pipeline_definition = client.created[1]["definition"]
            pipeline_payload = json.loads(
                decode_definition_parts(pipeline_definition)["pipeline-content.json"].decode("utf-8")
            )
            self.assertEqual("created-1", pipeline_payload["notebookId"])
            self.assertEqual("workspace-1", pipeline_payload["workspaceId"])

    def test_shipped_config_is_safe_and_consistent(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        config_path = repo_root / "scripts" / "fabric" / "config.example.json"
        config = deploy.load_config(config_path, repo_root)

        self.assertEqual(8, len(config.artifacts))
        for artifact in config.artifacts:
            self.assertTrue(artifact.source.exists(), msg=str(artifact.source))

        notebooks = [artifact for artifact in config.artifacts if artifact.item_type == "Notebook"]
        self.assertEqual(5, len(notebooks))
        for artifact in notebooks:
            self.assertEqual("ipynb", artifact.format)
            self.assertEqual("notebook-content.ipynb", artifact.part_path)
            self.assertFalse(artifact.update_metadata)

        pipelines = [artifact for artifact in config.artifacts if artifact.item_type == "DataPipeline"]
        self.assertEqual(2, len(pipelines))
        for artifact in pipelines:
            self.assertTrue(artifact.update_metadata)
            self.assertTrue(deploy.artifact_has_platform_file(artifact))

        placeholders = config.placeholders
        self.assertNotIn("GOLD_LAKEHOUSE_NAME", placeholders)
        self.assertEqual("RetailLakehouse", placeholders["DEFAULT_LAKEHOUSE_ID"]["displayName"])
        self.assertEqual("RetailLakehouse", placeholders["GOLD_LAKEHOUSE_ID"]["displayName"])
        self.assertEqual("RetailLakehouse", placeholders["LAKEHOUSE_ID"]["displayName"])

        iot_job = next(job for job in config.jobs if job.name == "iot-telemetry-notebook")
        self.assertEqual("IoT Telemetry Processing", iot_job.display_name)
        self.assertEqual(
            ["ENVIRONMENT", "PROCESSING_DATE", "PIPELINE_RUN_ID"],
            [parameter["name"] for parameter in (iot_job.parameters or [])],
        )
        self.assertTrue(all(parameter["type"] == "string" for parameter in (iot_job.parameters or [])))
        default_lakehouse = (iot_job.execution_data or {})["configuration"]["defaultLakehouse"]
        self.assertEqual("${DEFAULT_LAKEHOUSE_ID}", default_lakehouse["id"])
        self.assertEqual("${DEFAULT_LAKEHOUSE_NAME}", default_lakehouse["name"])


if __name__ == "__main__":
    unittest.main()
