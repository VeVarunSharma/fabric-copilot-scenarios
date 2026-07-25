# Fabric environment and deployment helpers

Optional, standard-library-only tooling for creating an on-demand Fabric demo environment and deploying source-controlled items from this repository.

## No-live-deployment disclaimer

This tooling is intended for dry-runs, example automation, and controlled development environments. Repository tests do not call a live Fabric tenant.

## On-demand demo capacity

The capacity lifecycle helper creates a dedicated Azure resource group, an `F2`
Fabric capacity, and a Fabric workspace. Deployment ends by suspending the
capacity. The workspace and its configuration persist while suspended.

### Capacity prerequisites

- Python 3.10+
- Azure CLI 2.61.0 or newer
- An Azure subscription that can create `Microsoft.Fabric/capacities`
- A Fabric tenant user who can administer the capacity and create workspaces
- An Azure region where `F2` is available

The helper installs the `microsoft-fabric` Azure CLI extension and registers the
`Microsoft.Fabric` resource provider when required.

### Capacity setup and lifecycle

```bash
az login
make configure
```

Review `scripts/fabric/capacity.local.json`. Blank `subscriptionId`,
`administratorUpn`, and `capacityName` values are inferred from the active Azure
CLI account. Then validate and deploy:

```bash
make doctor
make deploy
```

`make deploy` creates paid Azure resources, creates or reuses the Fabric workspace,
and suspends the capacity before returning. Normal use is:

```bash
make up
make status
make down
```

Always run `make down` when the demo ends. Resuming restarts billing; suspending
stops ongoing capacity usage billing but can bill accumulated overage.

### Optional GitHub connection

Enable Git integration in the Fabric tenant, push the configured branch to
GitHub, and use a PAT with repository Contents read/write access:

```bash
make fabric-connect
```

The PAT is read with a hidden prompt and is sent directly to the Fabric connection
API. It is never written to the local config or `.fabric-demo.state.json`.

To remove the workspace and dedicated Azure resource group:

```bash
make fabric-destroy
```

The command validates ownership tags and requires typing the exact resource-group
name. It never deletes or modifies the GitHub repository.

## Fabric item deployment

The item deployment helper is separate from the capacity lifecycle helper. It can
create and update supported Fabric items, but it does not create the required
`RetailLakehouse` or upload OneLake landing files.

### Prerequisites

- Python 3.10+
- Azure CLI (`az`)
- Access to a Microsoft Fabric workspace
- Fabric permissions appropriate for the operations you run

### Authentication

Sign in before invoking the CLI:

```bash
az login
az account show
```

Use the Fabric audience, not ARM:

```text
https://api.fabric.microsoft.com
```

The CLI acquires tokens with:

```bash
az account get-access-token --resource https://api.fabric.microsoft.com
```

### Config

Start from `scripts/fabric/config.example.json`.

- `workspace.displayName`: target workspace
- `placeholders`: deploy-time values or dynamic lookups
- `artifacts`: ordered deployment list
- `jobs`: optional run targets

Global CLI overrides:

- `--environment` overrides the `ENVIRONMENT` placeholder
- `--workspace-name` overrides `workspace.displayName`

These overrides work for `validate`, `plan`, `deploy`, `run`, and `verify`. This is the recommended workflow-level override mechanism for dev/test/prod promotion.

### Artifact order and dependencies

Artifact order matters.

- Deploy notebooks before pipelines that reference their IDs.
- Deploy upstream items before downstream placeholders that resolve `from: item`.
- The example config is intentionally ordered so notebooks are created before the pipelines that consume their IDs.
- Use `updateMetadata: true` only for sources that actually include a `.platform` file, such as the pipeline folders in this repository. Single notebook `.ipynb` sources do not include `.platform` and must not enable `updateMetadata`.

`plan` can show an empty item set in a prepared workspace by substituting planned/deferred values for earlier config artifacts that do not exist yet. `deploy` does not rely on deferred values; it re-resolves placeholders after each create/update so later artifacts can use IDs returned earlier in the same run.

### Supported placeholder syntax

Source files may use either form:

```text
{{WORKSPACE_ID}}
${WORKSPACE_ID}
```

Rules:

- names are case-sensitive
- names must match keys under `placeholders`
- exact JSON string tokens preserve typed substitution for `{{NAME}}`
- exact JSON string tokens also preserve typed substitution for `${NAME}` when safely detected as a standalone JSON value
- embedded tokens like `prefix-${NAME}` render as text

The tool substitutes in memory only and never rewrites canonical source files.

### Exact source-format expectations

- **Notebook**: source is a single `.ipynb` file deployed as definition part `notebook-content.ipynb` with definition `format: "ipynb"`
- **DataPipeline**: source is the full pipeline folder, preserving paths such as `.platform` and `pipeline-content.json`
- **SemanticModel**: source is the full semantic model folder, preserving nested TMDL paths and using definition `format: "TMDL"`

The helper does not currently deploy `Report` items. The RetailSales report
scaffold remains source-controlled and must be published manually, or the helper
must be extended with Fabric `Report`/PBIR support before automated deployment.

### Commands

Validate local config and placeholder coverage:

```bash
python scripts/fabric/deploy.py \
  --config scripts/fabric/config.example.json \
  --environment test \
  --workspace-name "Fabric Copilot Scenarios - Test" \
  validate
```

Dry-run plan:

```bash
python scripts/fabric/deploy.py \
  --config scripts/fabric/config.example.json \
  plan
```

Deploy create/update changes:

```bash
python scripts/fabric/deploy.py \
  --config scripts/fabric/config.example.json \
  deploy
```

Run configured jobs:

```bash
python scripts/fabric/deploy.py \
  --config scripts/fabric/config.example.json \
  run
```

Verify rendered local definitions against deployed items:

```bash
python scripts/fabric/deploy.py \
  --config scripts/fabric/config.example.json \
  verify
```

## Fabric semantics used

- API base: `https://api.fabric.microsoft.com/v1`
- Workspace discovery: `GET /workspaces`
- Item discovery: `GET /workspaces/{workspaceId}/items?type=...`
- Definition read: `POST /workspaces/{workspaceId}/items/{itemId}/getDefinition`
- Definition update: `POST /workspaces/{workspaceId}/items/{itemId}/updateDefinition`
- On-demand jobs: `POST /workspaces/{workspaceId}/items/{itemId}/jobs/instances?jobType=...`

Client behavior:

- pagination via `continuationUri` or `continuationToken`
- create/update/no-op planning by comparing rendered and remote definitions
- format-aware definition comparison
- long-running operation polling
- `Retry-After` honoring
- retries only for `429`, `503`, and `504`
- request ID capture in raised errors
- bearer-token redaction in surfaced messages

## OIDC workflow notes

For GitHub Actions, prefer workload identity federation over stored credentials:

1. Configure an Azure application or managed identity for Fabric access.
2. Configure GitHub environment protections separately.
3. Use `azure/login` with OIDC.
4. Run this CLI after login so it can request a Fabric token from Azure CLI.

High-level workflow pattern:

```yaml
- uses: azure/login@<pinned-sha>
  with:
    client-id: ${{ vars.AZURE_CLIENT_ID }}
    tenant-id: ${{ vars.AZURE_TENANT_ID }}
    subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}

- run: python scripts/fabric/deploy.py --config scripts/fabric/config.json plan
```

This repository does not ship live tenant credentials, workspace IDs, item IDs, or active deployment wiring.
