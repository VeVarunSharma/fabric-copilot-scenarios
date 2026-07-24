# Fabric administrator prompt guide

## Customer outcome

Prepare environments, controls, and deployment paths faster while keeping governance explicit.

## Best use cases

- workspace readiness, deployment constraints, approvals, feature availability, and security posture
- first-draft planning that still needs expert review
- workshop or demo sessions that need portable prompts instead of tool-specific files

## Copy-ready prompt

```text
Act as a senior Microsoft Fabric fabric administrator working in a GitHub-governed analytics repository.

Business outcome:
Prepare environments, controls, and deployment paths faster while keeping governance explicit.

Context:
- The repository demonstrates a synthetic retail and customer-transactions medallion architecture.
- The end-to-end path is synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report.
- I want help with workspace readiness, deployment constraints, approvals, feature availability, and security posture.
- The response must stay portable across environments.

Constraints:
- Do not invent workspace IDs, item IDs, secrets, tokens, tenant names, or customer data.
- Use synthetic data only.
- Keep GitHub governance in mind: changes should be reviewable, explainable, and safe.
- If you suggest implementation detail, label assumptions and placeholders clearly.
- Assume the target workspace is already capacity-backed and already contains a schema-enabled `RetailLakehouse`.
- Assume synthetic files are already uploaded under `Files/landing/retail-purchases`, `Files/landing/iot-telemetry`, and `Files/landing/healthcare-claims`.
- If GitHub Actions environments are used, use this exact deployment override contract:
  - `inputs.environment` maps to CLI `--environment` and overrides the config `ENVIRONMENT` placeholder.
  - environment-scoped `FABRIC_WORKSPACE_NAME` maps to CLI `--workspace-name` and overrides config `workspace.displayName`.

Deliver:
1. environment readiness checklist
2. deployment and approval guidance
3. security and governance caveats
4. human sign-off points

Acceptance criteria:
- The answer is specific to Microsoft Fabric and GitHub delivery workflows.
- The answer calls out what GitHub Copilot eliminates.
- The answer ends with a human review checklist and open questions.
```

## Human review required

- Validate business definitions, thresholds, and schema assumptions.
- Validate any generated code, DAX, SQL, or workflow step before reuse.
- Confirm feature availability and permissions in the target tenant or organization.

## Recommended scenario prompt packs

- [10 Fabric DevOps](../scenarios/10-fabric-devops.md)
- [11 GitHub Advanced Security](../scenarios/11-github-advanced-security.md)
- [08 Data lineage investigation](../scenarios/08-data-lineage-investigation.md)

## What Copilot should eliminate first

- repetitive scaffolding work
- first-draft documentation and explanation work
- option comparison and checklist drafting

## Related guidance

- [Prompt library README](../README.md)
- [Persona paths](../../docs/persona-paths.md)
