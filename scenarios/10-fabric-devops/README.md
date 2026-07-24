# Scenario 10 - Fabric DevOps for multi-environment deployment

## Business problem
A customer wants one Fabric deployment workflow for development, test, and production without hardcoded workspace IDs or stored credentials. The workflow must select the GitHub environment `dev`, `test`, or `prod`, pass precise runtime overrides into the CLI, and keep `scripts/fabric/config.example.json` as a safe dev or local example instead of a production-specific config file.

## Target personas and prerequisites
- Fabric platform engineer
- GitHub Actions workflow maintainer
- Security or cloud administrator approving OIDC and environment protections

Prerequisites:
- The shared deployment helper exists under `scripts/fabric/` and the workflow exists under `.github/workflows/fabric-deploy.yml`.
- GitHub environments named exactly `dev`, `test`, and `prod` exist.
- Each selected GitHub environment provides `FABRIC_WORKSPACE_NAME` plus the Azure OIDC variables required by the workflow.
- A capacity-backed workspace already exists for each environment.
- The exact workspace examples are `Fabric Copilot Scenarios - Dev`, `Fabric Copilot Scenarios - Test`, and `Fabric Copilot Scenarios - Prod`.
- A schema-enabled `RetailLakehouse` already exists in each target workspace.
- Sample files are already uploaded before any `run` job to the documented OneLake paths: `Files/landing/retail-purchases`, `Files/landing/iot-telemetry`, and `Files/landing/healthcare-claims`.

## Manual baseline or starting state
Without Copilot, teams often duplicate release notes, rewrite the same environment mapping by hand, and accidentally mix safe local config examples with production-specific values. That drift makes reviews harder and increases the chance that someone hardcodes a workspace name or forgets an external prerequisite.

## Copilot-assisted workflow
1. Start from the safe repository example at `scripts/fabric/config.example.json`, which keeps `ENVIRONMENT=dev` and `workspace.displayName=Fabric Copilot Scenarios - Dev` as local defaults.
2. Use Copilot to summarize the override contract precisely:
   - workflow `inputs.environment` -> CLI `--environment` -> overrides config `ENVIRONMENT`
   - selected GitHub environment variable `FABRIC_WORKSPACE_NAME` -> CLI `--workspace-name` -> overrides `workspace.displayName`
3. Review the generated environment matrix and checklist to confirm the environment override and workspace-name override are described as separate runtime inputs.
4. Confirm the external prerequisites before remote operations: existing capacity-backed workspace, existing schema-enabled `RetailLakehouse`, and uploaded landing files before any `run` step.
5. Use the checklist during change review so the team remembers that deployment creates or updates item definitions only. It does not provision Fabric capacity, create the lakehouse, or upload sample data.

## Scenario artifacts
- Environment contract: [artifacts/environment-matrix.json](artifacts/environment-matrix.json)
- Deployment checklist: [artifacts/deployment-checklist.md](artifacts/deployment-checklist.md)
- Prompt examples: [sample-prompt.md](sample-prompt.md)
- Expected answer shape: [expected-output.md](expected-output.md)
- Stretch work: [extension-exercises.md](extension-exercises.md)

## Validation
Validate the JSON contract locally. Then run a wording sweep to confirm the override chain is stated consistently.

```bash
python3 -m json.tool scenarios/10-fabric-devops/artifacts/environment-matrix.json >/dev/null
rg -n 'workflow `inputs.environment`|CLI `--environment`|overrides config `ENVIRONMENT`|`FABRIC_WORKSPACE_NAME`|CLI `--workspace-name`|overrides `workspace.displayName`|Fabric Copilot Scenarios - Dev|Fabric Copilot Scenarios - Test|Fabric Copilot Scenarios - Prod' scenarios/10-fabric-devops
```

## Learning objectives
- Explain how the workflow uses GitHub environments `dev`, `test`, and `prod` instead of custom environment names.
- Distinguish the environment override from the workspace-name override.
- Capture the real external prerequisites for remote Fabric operations.
- Reinforce that deployment automation creates or updates item definitions, not capacity, lakehouse provisioning, or landing data uploads.

## Review checklist
- The docs use GitHub environment names exactly `dev`, `test`, and `prod`.
- The override contract is stated precisely and consistently:
  - `inputs.environment` -> `--environment` -> `ENVIRONMENT`
  - `FABRIC_WORKSPACE_NAME` -> `--workspace-name` -> `workspace.displayName`
- Workspace examples are listed separately as `Fabric Copilot Scenarios - Dev`, `Fabric Copilot Scenarios - Test`, and `Fabric Copilot Scenarios - Prod`.
- `RetailLakehouse`, `Retail Medallion Pipeline`, and `RetailSales` are the referenced display names.
- The docs state that capacity-backed workspaces, schema-enabled lakehouses, and landing files already exist before remote runs.

## What work did Copilot eliminate?
Copilot removes the repetitive documentation work: turning the workflow and config contract into a customer-ready environment matrix, checklist, and review summary. Humans still verify the actual GitHub environment variables, Fabric prerequisites, approval policy, and release readiness.
