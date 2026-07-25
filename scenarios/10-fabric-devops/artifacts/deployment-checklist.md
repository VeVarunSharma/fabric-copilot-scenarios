# Deployment checklist

## Shared assets
- Deployment scripts: [../../../scripts/fabric/](../../../scripts/fabric/)
- GitHub Actions workflow: [../../../.github/workflows/fabric-deploy.yml](../../../.github/workflows/fabric-deploy.yml)

## Workflow contract
- Trigger the workflow with GitHub environment `dev`, `test`, or `prod`.
- Treat `scripts/fabric/config.example.json` as a safe dev or local example, not as the final environment binding.
- State the override chains precisely:
  - workflow `inputs.environment` -> CLI `--environment` -> overrides config `ENVIRONMENT`
  - selected GitHub environment variable `FABRIC_WORKSPACE_NAME` -> CLI `--workspace-name` -> overrides `workspace.displayName`
- Keep the two override chains separate. Do not describe the workspace variable as overriding the environment selection.

## Pre-flight
- Confirm the selected GitHub environment exists and is named exactly `dev`, `test`, or `prod`.
- Confirm the selected GitHub environment exposes `FABRIC_WORKSPACE_NAME` and the required Azure OIDC variables.
- Confirm `FABRIC_WORKSPACE_NAME` is set to the expected exact workspace name for the run.
- The workspace examples are `Fabric Copilot Scenarios - Dev`, `Fabric Copilot Scenarios - Test`, and `Fabric Copilot Scenarios - Prod`.
- Confirm the target workspace is already capacity-backed.
- Confirm a schema-enabled `RetailLakehouse` already exists in that workspace.
- Confirm the landing files are already uploaded before any `run` job to `Files/landing/retail-purchases`, `Files/landing/iot-telemetry`, and `Files/landing/healthcare-claims`.

## Plan or dry-run
- Run `validate` or `plan` before remote deployment.
- Resolve workspace and item IDs dynamically by display name.
- Expect the workflow to target `RetailLakehouse`, `Retail Medallion Pipeline`, and `RetailSales` by display name.
- Record request IDs for supportability and release evidence.
- Fail fast if the selected workspace or referenced display names do not resolve uniquely.

## Deploy
- Require the approval policy configured on the selected GitHub environment.
- Execute create or update operations idempotently for item definitions.
- Treat Fabric long-running operations as first-class: poll until terminal state, honor `Retry-After`, and surface request IDs in logs.
- Never print bearer tokens, client secrets, or raw secret values.
- Remember the scope boundary: deployment creates or updates item definitions only. It does not create Fabric capacity, create `RetailLakehouse`, or upload sample data.

## Verify and run
- Confirm the deployed definitions are discoverable by the expected names.
- Run `verify` after deployment and capture evidence.
- Only run pipeline or notebook jobs after landing files are confirmed in the documented `Files/landing/...` paths.

## Rollback
- Stop the rollout if verify fails or if prerequisite checks were wrong.
- Redeploy the last known good item definitions.
- Rerun verify after rollback and document the incident path.
- Do not patch in hardcoded IDs during an incident; fix the GitHub environment variable or source discovery inputs instead.
