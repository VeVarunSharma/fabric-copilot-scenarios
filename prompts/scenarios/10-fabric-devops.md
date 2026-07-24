# 10 Fabric DevOps prompt pack

## Customer outcome

Plan portable deployment steps for Fabric artifacts across environments without hardcoded identifiers.

## Best when the customer asks for

- work in the area of environment discovery, dry-run planning, approvals, validation, and portability
- a strong first draft that still preserves human review
- clear explanation of what GitHub Copilot removes from the manual workflow

## Copy-ready prompt

```text
You are helping me with the repository scenario "10 Fabric DevOps".

Business outcome:
Plan portable deployment steps for Fabric artifacts across environments without hardcoded identifiers.

Context:
- Domain: multi-environment Fabric deployment
- Architecture backbone: synthetic sources -> Fabric pipeline -> bronze -> silver -> gold -> Direct Lake semantic model -> report
- The repository is customer-facing and portable.
- GitHub governance and security matter as much as artifact quality.

Constraints:
- Use only synthetic or placeholder data.
- Do not invent workspace IDs, item IDs, credentials, or customer details.
- Label assumptions and placeholders clearly.
- Emphasize what the human reviewer must still validate.
- Assume optional deployment automation does not provision capacity, create `RetailLakehouse`, or seed OneLake.
- Assume a capacity-backed workspace plus schema-enabled `RetailLakehouse` already exist.
- Assume synthetic files are already uploaded under `Files/landing/retail-purchases`, `Files/landing/iot-telemetry`, and `Files/landing/healthcare-claims`.
- If workflow environments are in play, use this exact deployment override contract:
  - `inputs.environment` maps to CLI `--environment` and overrides the config `ENVIRONMENT` placeholder.
  - environment-scoped `FABRIC_WORKSPACE_NAME` maps to CLI `--workspace-name` and overrides config `workspace.displayName`.

Deliver:
1. deployment pattern
2. environment checklist
3. approval and validation flow
4. review checklist

Acceptance criteria:
- no secrets or fixed IDs are invented
- dry-run and verification steps are included
- approval boundaries are explicit
- the answer states what Copilot eliminated

End with:
- the work GitHub Copilot eliminated
- the human review checklist
- open questions that should be resolved before implementation or approval
```

## Context worth pasting into Copilot

- the target persona
- the business goal for the scenario
- approved file excerpts or artifact descriptions
- constraints on environment portability and governance

## Human review required

- identity model
- workspace resolution logic
- rollback plan
- production approval requirements

## Related guidance

- [Prompt library README](../README.md)
- [Artifact reference](../../docs/artifact-reference.md)
- [Architecture](../../docs/architecture.md)
