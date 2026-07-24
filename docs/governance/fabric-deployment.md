# Fabric deployment guidance

Deployment is where repository portability meets real environment constraints. This repository can document deployment patterns, but actual authentication, workspace permissions, item discovery, and approvals are configured in Fabric, Microsoft Entra, Azure, and GitHub settings.

## Customer outcome

Help customers understand how to move from portable repository content to environment-specific Fabric deployment without hardcoding secrets or identifiers.

## Recommended deployment pattern

- Keep canonical source files free of workspace IDs, item IDs, tenant names, and credentials.
- Resolve environment-specific identifiers at deploy time by approved name lookup or configuration.
- Use short-lived credentials, OIDC, or other approved federated patterns instead of long-lived shared secrets.
- Treat validation, dry-run planning, deployment, run, and verification as separate steps.
- Treat the item deployment automation as update-oriented, not as an empty-workspace bootstrap.

## Two separate deployment surfaces

The [on-demand demo capacity helper](../../scripts/fabric/README.md#on-demand-demo-capacity) can provision a dedicated `F2` capacity and a Fabric workspace, then suspend the capacity to control cost. The item deployment helper remains update-oriented and assumes its data prerequisites already exist.

## What the item deployment automation does not do

- It does not create the required lakehouse from a blank workspace.
- It does not seed OneLake landing data for you.

The item automation assumes a ready workspace, lakehouse, and prepared landing files. The capacity helper supplies only the capacity and workspace.

## External prerequisites

| Requirement | Why it matters | Where it is configured |
| --- | --- | --- |
| Fabric workspace access | Needed to create or update items | Fabric admin and workspace settings |
| Capacity-backed workspace | Needed for many live analytics experiences such as Direct Lake validation | Fabric platform configuration |
| Schema-enabled `RetailLakehouse` | Needed so notebooks, pipelines, and downstream model references have the expected lakehouse target | Fabric workspace item configuration |
| Synthetic landing files in OneLake | Needed so ingestion and downstream jobs have input data to process | Uploaded to `Files/landing/retail-purchases`, `Files/landing/iot-telemetry`, and `Files/landing/healthcare-claims` |
| Entra app or federated identity | Needed for non-interactive deployment paths | Entra and cloud identity administration |
| GitHub environment approvals | Needed for controlled release promotion | GitHub repository or organization settings |
| Network and endpoint allowance | Needed if customer policy restricts external calls | Customer network and platform policy |

## Workspace and environment selection

- Repository config can define a default environment or workspace mapping.
- Deployment override contract:
  - `inputs.environment` maps to CLI `--environment` and overrides the config `ENVIRONMENT` placeholder.
  - environment-scoped `FABRIC_WORKSPACE_NAME` maps to CLI `--workspace-name` and overrides config `workspace.displayName`.
- Use those overrides deliberately and document which GitHub environment owns each target workspace.
- Do not assume that item-deployment environment selection provisions missing capacity, lakehouse objects, or OneLake files. Capacity bootstrap is an explicit, separate command.

## What Copilot can help with

- drafting deployment checklists
- explaining dry-run or plan output
- generating portable config structures
- summarizing failure handling, retries, and validation steps

## What humans must still verify

- authentication method and token audience
- workspace and item mapping logic
- that the override contract is implemented correctly for both `inputs.environment` and environment-scoped `FABRIC_WORKSPACE_NAME`
- approval path for production deployment
- rollback and incident ownership
- whether the target tenant and capacity are ready for the scenario
- whether `RetailLakehouse` exists and is schema-enabled
- whether synthetic files are already present under the documented `Files/landing/...` paths

## Deployment anti-patterns to avoid

- hardcoded IDs in source-controlled notebooks, pipelines, or docs
- storing live client secrets in repository files or prompts
- assuming that a workflow file alone grants deployment access
- assuming the automation can start from an empty workspace with no lakehouse or landing files
- skipping dry-run review before a real deployment

## Related guidance

- [Data safety](data-safety.md)
- [Troubleshooting](../troubleshooting.md)
- [Architecture](../architecture.md)
