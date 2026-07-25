# Sample prompt

## Ready-to-copy prompt
```text
I need a customer-facing explanation of the Fabric deployment workflow in this repository. Use scenarios/10-fabric-devops/, scripts/fabric/config.example.json, and .github/workflows/fabric-deploy.yml. State the override contract precisely and consistently: workflow inputs.environment -> CLI --environment -> overrides config ENVIRONMENT; selected GitHub environment variable FABRIC_WORKSPACE_NAME -> CLI --workspace-name -> overrides workspace.displayName. Keep those as separate overrides. The source config stays a safe dev or local example. List the workspace examples separately as Fabric Copilot Scenarios - Dev, Fabric Copilot Scenarios - Test, and Fabric Copilot Scenarios - Prod. Refer to RetailLakehouse, Retail Medallion Pipeline, and RetailSales by display name. Also call out that capacity-backed workspaces, schema-enabled RetailLakehouse items, and landing files under Files/landing/retail-purchases, Files/landing/iot-telemetry, and Files/landing/healthcare-claims must already exist before remote jobs run.
```

## Context supplied to Copilot
- The shared deployment scripts live under `scripts/fabric/`.
- The reusable workflow lives under `.github/workflows/fabric-deploy.yml`.
- `scripts/fabric/config.example.json` is intentionally a safe dev or local example.
- Remote operations create or update item definitions; they do not provision capacity, create the lakehouse, or upload fixture data.

## Constraints and acceptance criteria
- Use GitHub environment names exactly `dev`, `test`, and `prod`.
- Describe the two runtime override chains separately and exactly.
- Do not imply `FABRIC_WORKSPACE_NAME` overrides the environment selection.
- Mention OIDC, long-running operation handling, and approval boundaries.
- Include the explicit external prerequisites for workspace, lakehouse, and landing files.

## Follow-up prompts
```text
Convert that override contract into a release reviewer checklist for dev, test, and prod.
```

```text
What values still live outside source control on the selected GitHub environment?
```
