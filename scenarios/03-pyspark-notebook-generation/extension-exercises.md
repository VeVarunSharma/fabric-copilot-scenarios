# Extension exercises - Scenario 03

## Persona-specific variants

| Persona | Exercise | Expected outcome |
| --- | --- | --- |
| Data engineer | Extend the prompt to support multi-file ingestion with separate raw and replay paths. | Copilot drafts reusable parameter and ingest scaffolding that the engineer reviews for operational safety. |
| Operations analyst | Ask Copilot to add derived device-health bands based on rolling metrics. | The analyst gets a first-pass transformation without hand-writing every conditional expression. |
| Platform owner | Request notebook logging that is easy to route into centralized monitoring. | Copilot drafts the structure while the owner validates naming and telemetry policy. |

## Production-hardening variants
- Add watermark logic for late-arriving events and require a review of replay behavior.
- Ask Copilot to draft merge logic for slowly changing device metadata alongside telemetry facts.
- Generate a notebook review checklist for schema drift, Delta table retention, and checkpoint design.
- Add a variant that writes summary metrics for pipeline alerting without exposing raw payloads.
