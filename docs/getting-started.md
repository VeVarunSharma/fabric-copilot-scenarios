# Getting started

This guide helps customers start with a business outcome, choose the right persona path, and use the prompt library in a way that keeps human review in the loop.

## Start with the outcome

The fastest way to get value from this repository is to decide which problem you want to accelerate first:

- stand up a medallion pipeline
- optimize warehouse SQL
- draft or review a Fabric notebook
- improve a semantic model or DAX measure set
- build and validate a historical public-data Power BI report
- explain governance, deployment, or security decisions to stakeholders

Copilot is most valuable when the desired output, constraints, and acceptance criteria are clear before prompting begins.

## Recommended first path

1. Review the [architecture overview](architecture.md).
2. Pick a role path in [persona paths](persona-paths.md).
3. Open the matching prompt guide in [prompts](../prompts/README.md).
4. Paste only synthetic or approved demo context. The Scenario 12 public-data
   snapshot is approved only under the controls in
   [data safety](governance/data-safety.md).
5. Review the answer against your acceptance criteria before you reuse any generated content.

## What to prepare before a demo or workshop

- A clear customer outcome such as faster pipeline authoring or safer release governance.
- A small set of approved repository files, screenshots, or excerpts to ground the prompt.
- A decision on whether the audience is executive, practitioner, or mixed.
- A list of non-negotiable constraints such as no hardcoded IDs, no real
  secrets, and synthetic data only except for a specifically approved governed
  public aggregate snapshot.

## Deployment prerequisites before running jobs

The item deployment automation is not a complete tenant bootstrap path. The separate [on-demand capacity helper](../scripts/fabric/README.md#on-demand-demo-capacity) can create an `F2` capacity and Fabric workspace, but it does not create a lakehouse or seed OneLake.

Before running deployment or workload jobs, confirm that:

- a capacity-backed Fabric workspace already exists, or has been created with the on-demand capacity helper
- a schema-enabled `RetailLakehouse` already exists in that workspace
- synthetic files have already been uploaded to OneLake under:
  - `Files/landing/retail-purchases`
  - `Files/landing/iot-telemetry`
  - `Files/landing/healthcare-claims`

If the capacity and workspace are missing, run the cost-safe bootstrap first. If the lakehouse or landing files are missing, prepare them before running the item deployment or workload jobs.

## Quick-start lanes

| If you are a... | Start here | Then use |
| --- | --- | --- |
| Executive sponsor | [Executive briefing runbook](demo-runbooks/executive-briefing.md) | [Architecture](architecture.md) |
| Facilitator | [Facilitator guide](facilitator-guide.md) | [Demo runbooks](demo-runbooks/fabric-workshop.md) |
| Data builder | [Persona paths](persona-paths.md) | [Scenario prompt packs](../prompts/scenarios/README.md) |
| Power BI practitioner | [CCHS Power BI runbook](demo-runbooks/bc-cchs-power-bi.md) | [Scenario 12](../scenarios/12-cchs-power-bi-authoring/) |
| Governance owner | [GitHub Enterprise guidance](governance/github-enterprise.md) | [Repository rulesets](governance/repository-rulesets.md) |
| Security lead | [GHAS guidance](governance/github-advanced-security.md) | [Data safety](governance/data-safety.md) |

## Demo-safe defaults

- Use synthetic data and sanitized screenshots by default. Use public aggregate
  data only when it is explicitly reviewed, pinned, attributed, checksummed, and
  governed by the [public-data exception](governance/data-safety.md#narrow-public-data-exception).
- Keep synthetic fixture guarantees and synthetic-only persona/scenario prompts
  unchanged.
- Keep tenant, workspace, subscription, and credential details out of prompts.
- Ask Copilot for first drafts, option sets, checklists, or explanations before asking it to produce implementation detail.
- Require a human to validate generated code, DAX, deployment steps, and governance choices.
- Deployment override contract:
  - `inputs.environment` maps to CLI `--environment` and overrides the config `ENVIRONMENT` placeholder.
  - environment-scoped `FABRIC_WORKSPACE_NAME` maps to CLI `--workspace-name` and overrides config `workspace.displayName`.

## Suggested first session

1. Choose one scenario prompt pack.
2. Add the customer context, constraints, and success definition.
3. Ask Copilot to show assumptions and open questions.
4. Ask Copilot to explain what work it eliminated.
5. End with a review checklist and next actions for the human team.

## Need help?

- [Troubleshooting](troubleshooting.md)
- [Artifact reference](artifact-reference.md)
- [Data safety](governance/data-safety.md)
- [Fabric deployment guidance](governance/fabric-deployment.md)
