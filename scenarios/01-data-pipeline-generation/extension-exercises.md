# Extension exercises - Scenario 01

## Persona-specific variants

| Persona | Exercise | Expected outcome |
| --- | --- | --- |
| Data engineer | Extend the prompt so the pipeline can backfill a date range instead of a single `ProcessDate`. | Copilot drafts loop or metadata-driven orchestration changes and the engineer reviews runtime safety. |
| Analytics engineer | Add a post-gold validation step that checks required business aggregates before semantic-model refresh. | Copilot proposes the dependency edge and validation handoff without the reviewer hand-wiring the entire branch. |
| Platform lead | Ask Copilot to describe how retry policy should differ between ingestion, transformation, and publication steps. | The output becomes a reviewer aid for operational policy, not just code scaffolding. |

## Production-hardening variants
- Add environment-specific notification routing without hardcoding email addresses or webhooks.
- Introduce idempotency checks so reruns for the same `ProcessDate` do not duplicate outputs.
- Add SLA-oriented timeout tuning for long-running silver notebooks versus short validation activities.
- Generate a reviewer summary that identifies which activity failures should page an operator and which should remain warning-only.
