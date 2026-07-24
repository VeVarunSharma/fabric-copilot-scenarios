# Extension exercises - Scenario 04

## Persona-specific variants

| Persona | Exercise | Expected outcome |
| --- | --- | --- |
| Data steward | Ask Copilot to add business definitions for each rule in reviewer-friendly language. | The steward gets first-draft governance text tied to technical rules. |
| Data engineer | Extend the prompt so warning metrics also roll up by source_file and process_date. | Copilot drafts the aggregation logic while the engineer reviews threshold policy. |
| Analytics lead | Add a requirement for trend metrics that compare current quarantine rate with the previous 7 runs. | Copilot produces a first-pass metric design that the lead validates against reporting needs. |

## Production-hardening variants
- Add a pipeline branch that automatically creates a remediation ticket when critical failures exceed a threshold.
- Generate a review checklist for quarantine retention, access control, and downstream replay handling.
- Ask Copilot to add rule-version metadata so future policy changes are auditable.
- Introduce a no-PHI guardrail checklist for prompt review before any workshop delivery.
