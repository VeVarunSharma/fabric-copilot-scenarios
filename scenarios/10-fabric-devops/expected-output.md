# Expected output

## Expected response shape
A strong answer should contain:
1. A dev, test, and prod matrix that matches the workflow input names exactly.
2. A precise statement that workflow `inputs.environment` flows to CLI `--environment` and overrides config `ENVIRONMENT`.
3. A precise statement that selected GitHub environment variable `FABRIC_WORKSPACE_NAME` flows to CLI `--workspace-name` and overrides `workspace.displayName`.
4. The correct example display names listed separately: `Fabric Copilot Scenarios - Dev`, `Fabric Copilot Scenarios - Test`, and `Fabric Copilot Scenarios - Prod`, plus `RetailLakehouse`, `Retail Medallion Pipeline`, and `RetailSales`.
5. External prerequisites covering capacity-backed workspaces, existing schema-enabled lakehouses, and uploaded landing files before `run` jobs.
6. A reminder that the deployment automation creates or updates item definitions only.

## Canonical artifacts
- Environment matrix: [artifacts/environment-matrix.json](artifacts/environment-matrix.json)
- Deployment checklist: [artifacts/deployment-checklist.md](artifacts/deployment-checklist.md)

## Important design choices
- The source config remains a safe dev or local example rather than a production-specific file.
- The workflow has two separate runtime overrides: one for `ENVIRONMENT`, one for `workspace.displayName`.
- No workspace ID or item ID is committed; item discovery still happens by display name.
- `plan`, `deploy`, and `verify` depend on an existing workspace and external items. `run` additionally depends on preloaded landing files.
- OIDC and GitHub environment approvals stay outside source-controlled Markdown.

## Review checklist
- The answer keeps the GitHub environment names aligned to the current workflow contract.
- The answer states both override chains exactly.
- The answer does not imply `FABRIC_WORKSPACE_NAME` overrides the selected environment.
- The workspace examples are listed separately, not collapsed into slash shorthand.
- The external prerequisites are explicit and operationally realistic.
- The response makes it clear that rollout automation is not provisioning Fabric capacity or data.
