from __future__ import annotations

import io
import json
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, Mapping

from scripts.fabric.capacity import (
    CapacityConfig,
    CapacityError,
    FabricDemoManager,
    StateStore,
    _parse_github_remote,
    derive_capacity_name,
    load_capacity_config,
)
from scripts.fabric.fabric_api import ApiResponse, FabricApiError


def api_response(
    status_code: int,
    body: Any = None,
    headers: Mapping[str, str] | None = None,
) -> ApiResponse:
    return ApiResponse(
        status_code=status_code,
        headers=dict(headers or {}),
        body=body,
        request_id=None,
    )


def capacity_config() -> CapacityConfig:
    return CapacityConfig(
        subscription_id="00000000-1111-2222-3333-444444444444",
        location="westus3",
        resource_group_name="rg-fabric-github-demo",
        capacity_name="fcfabricgithub000000001111",
        administrator_upn="developer@example.com",
        workspace_name="fabric-with-github-demo",
        workspace_description="Demo workspace",
        github_owner="example",
        github_repository="fabric-with-github",
        github_branch="main",
        github_directory="/",
        github_connection_name="fabric-with-github-demo",
        initialize_from_git=True,
    )


class FakeAzure:
    def __init__(self) -> None:
        self.capacity = {
            "name": "fcfabricgithub000000001111",
            "properties": {"state": "Active"},
        }
        self.doctor_calls = 0
        self.validate_calls = 0
        self.deploy_calls = 0
        self.resume_calls = 0
        self.suspend_calls = 0
        self.delete_calls = 0
        self.group: dict[str, Any] | None = None

    def doctor(self, config: CapacityConfig) -> None:
        self.doctor_calls += 1

    def validate_bicep(self, template_file: Path) -> None:
        self.validate_calls += 1

    def deploy(self, config: CapacityConfig, template_file: Path) -> dict[str, Any]:
        self.deploy_calls += 1
        return {
            "capacityResourceId": (
                "/subscriptions/00000000-1111-2222-3333-444444444444/"
                "resourceGroups/rg-fabric-github-demo/providers/"
                "Microsoft.Fabric/capacities/fcfabricgithub000000001111"
            )
        }

    def capacity_exists(self, config: CapacityConfig) -> bool:
        return self.capacity is not None

    def show_capacity(self, config: CapacityConfig) -> dict[str, Any] | None:
        return self.capacity

    @staticmethod
    def capacity_state(capacity: Mapping[str, Any]) -> str:
        properties = capacity.get("properties", {})
        return str(properties.get("state", "Unknown"))

    def resume(self, config: CapacityConfig) -> None:
        self.resume_calls += 1
        self.capacity["properties"]["state"] = "Active"

    def suspend(self, config: CapacityConfig) -> None:
        self.suspend_calls += 1
        self.capacity["properties"]["state"] = "Paused"

    def show_resource_group(self, config: CapacityConfig) -> dict[str, Any] | None:
        return self.group

    def delete_resource_group(self, config: CapacityConfig) -> None:
        self.delete_calls += 1


class FailingSuspendAzure(FakeAzure):
    def suspend(self, config: CapacityConfig) -> None:
        self.suspend_calls += 1
        raise CapacityError("simulated suspend failure")


class FakePowerBiClient:
    def request_json(self, method: str, path: str, **kwargs: Any) -> ApiResponse:
        return api_response(
            200,
            {
                "value": [
                    {
                        "id": "capacity-data-plane-id",
                        "displayName": "fcfabricgithub000000001111",
                    }
                ]
            },
        )


class DeployFabricClient:
    def __init__(self, *, fail_create: bool = False) -> None:
        self.fail_create = fail_create
        self.requests: list[tuple[str, str, Any]] = []

    def find_workspace_by_display_name(
        self,
        display_name: str,
        *,
        allow_missing: bool = False,
    ) -> dict[str, Any] | None:
        return None

    def request_json(
        self,
        method: str,
        path: str,
        *,
        payload: Any = None,
        **kwargs: Any,
    ) -> ApiResponse:
        self.requests.append((method, path, payload))
        if self.fail_create and method == "POST" and path == "/workspaces":
            raise FabricApiError("workspace create failed")
        if method == "POST" and path == "/workspaces":
            return api_response(
                201,
                {
                    "id": "workspace-1",
                    "displayName": "fabric-with-github-demo",
                    "capacityId": "capacity-data-plane-id",
                },
            )
        raise AssertionError(f"Unexpected request: {method} {path}")


class ConnectFabricClient:
    def __init__(self) -> None:
        self.requests: list[tuple[str, str, Any]] = []

    def iter_paginated(self, path: str):
        return iter(())

    def request_json(
        self,
        method: str,
        path: str,
        *,
        payload: Any = None,
        **kwargs: Any,
    ) -> ApiResponse:
        self.requests.append((method, path, payload))
        if method == "GET" and path == "/workspaces/workspace-1":
            return api_response(
                200,
                {
                    "id": "workspace-1",
                    "displayName": "fabric-with-github-demo",
                },
            )
        if method == "POST" and path == "/connections":
            return api_response(
                201,
                {
                    "id": "connection-1",
                    "connectionDetails": {
                        "path": "https://github.com/example/fabric-with-github"
                    },
                },
            )
        if method == "GET" and path == "/workspaces/workspace-1/git/connection":
            return api_response(404, {"errorCode": "WorkspaceNotConnectedToGit"})
        if method == "POST" and path == "/workspaces/workspace-1/git/connect":
            return api_response(200)
        if method == "POST" and path.endswith("/git/initializeConnection"):
            return api_response(200, {"requiredAction": "None"})
        raise AssertionError(f"Unexpected request: {method} {path}")


class CapacityConfigurationTests(unittest.TestCase):
    def test_example_configuration_loads(self) -> None:
        config = load_capacity_config("scripts/fabric/capacity.example.json")
        self.assertEqual("westus3", config.location)
        self.assertEqual("fabric-with-github-demo", config.workspace_name)
        self.assertIsNone(config.subscription_id)
        self.assertIsNone(config.capacity_name)

    def test_capacity_name_matches_bicep_expression(self) -> None:
        self.assertEqual(
            "fcfabricgithub0123456789ab",
            derive_capacity_name("01234567-89ab-cdef-0123-456789abcdef"),
        )

    def test_github_remote_parser_supports_https_and_ssh(self) -> None:
        self.assertEqual(
            ("octo", "demo"),
            _parse_github_remote("https://github.com/octo/demo.git"),
        )
        self.assertEqual(
            ("octo", "demo"),
            _parse_github_remote("git@github.com:octo/demo.git"),
        )


class StateStoreTests(unittest.TestCase):
    def test_state_file_is_owner_only_and_contains_no_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".fabric-demo.state.json"
            store = StateStore(path)
            store.save({"workspaceId": "workspace-1", "connectionId": "connection-1"})
            mode = stat.S_IMODE(path.stat().st_mode)
            self.assertEqual(0o600, mode)
            self.assertNotIn("token", path.read_text(encoding="utf-8").lower())


class FabricDemoManagerTests(unittest.TestCase):
    def make_manager(
        self,
        directory: str,
        *,
        azure: FakeAzure,
        fabric: Any,
        secret_prompt=lambda _message: "github-secret-token",
        prompt=lambda _message: "",
    ) -> tuple[FabricDemoManager, StateStore, io.StringIO, io.StringIO]:
        state = StateStore(Path(directory) / ".fabric-demo.state.json")
        stdout = io.StringIO()
        stderr = io.StringIO()
        manager = FabricDemoManager(
            config=capacity_config(),
            repo_root=Path(directory),
            azure=azure,
            fabric=fabric,
            power_bi=FakePowerBiClient(),
            state=state,
            out=stdout,
            err=stderr,
            sleep=lambda _seconds: None,
            prompt=prompt,
            secret_prompt=secret_prompt,
            command_runner=lambda command, **kwargs: subprocess.CompletedProcess(
                command,
                0,
                stdout="remote-commit\trefs/heads/main\n",
                stderr="",
            ),
        )
        return manager, state, stdout, stderr

    def test_deploy_creates_workspace_then_suspends_capacity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            azure = FakeAzure()
            fabric = DeployFabricClient()
            manager, state, stdout, _ = self.make_manager(
                directory,
                azure=azure,
                fabric=fabric,
            )
            manager.deploy()
            saved = state.load()
            self.assertEqual("workspace-1", saved["workspaceId"])
            self.assertEqual("capacity-data-plane-id", saved["capacityId"])
            self.assertEqual(1, azure.suspend_calls)
            self.assertIn("suspended ongoing capacity usage", stdout.getvalue())

    def test_deploy_failure_still_suspends_capacity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            azure = FakeAzure()
            manager, _, _, _ = self.make_manager(
                directory,
                azure=azure,
                fabric=DeployFabricClient(fail_create=True),
            )
            with self.assertRaises(FabricApiError):
                manager.deploy()
            self.assertEqual(1, azure.suspend_calls)

    def test_successful_deploy_surfaces_failed_final_suspend(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            azure = FailingSuspendAzure()
            manager, state, _, _ = self.make_manager(
                directory,
                azure=azure,
                fabric=DeployFabricClient(),
            )
            with self.assertRaisesRegex(CapacityError, "Run 'make down' immediately"):
                manager.deploy()
            self.assertEqual("workspace-1", state.load()["workspaceId"])
            self.assertEqual(1, azure.suspend_calls)

    def test_connect_resumes_then_resuspends_without_persisting_pat(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            azure = FakeAzure()
            azure.capacity["properties"]["state"] = "Paused"
            fabric = ConnectFabricClient()
            manager, state, _, _ = self.make_manager(
                directory,
                azure=azure,
                fabric=fabric,
            )
            state.save(
                {
                    "workspaceId": "workspace-1",
                    "workspaceName": "fabric-with-github-demo",
                }
            )
            manager.connect()
            saved_text = state.path.read_text(encoding="utf-8")
            self.assertEqual(1, azure.resume_calls)
            self.assertEqual(1, azure.suspend_calls)
            self.assertNotIn("github-secret-token", saved_text)
            self.assertEqual("connection-1", state.load()["connectionId"])

    def test_destroy_refuses_resource_group_without_ownership_tags(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            azure = FakeAzure()
            azure.group = {"name": "rg-fabric-github-demo", "tags": {"environment": "demo"}}
            manager, _, _, _ = self.make_manager(
                directory,
                azure=azure,
                fabric=DeployFabricClient(),
            )
            with self.assertRaisesRegex(CapacityError, "ownership tags"):
                manager.destroy()
            self.assertEqual(0, azure.delete_calls)


if __name__ == "__main__":
    unittest.main()
