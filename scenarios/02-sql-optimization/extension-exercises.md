# Extension exercises - Scenario 02

## Persona-specific variants

| Persona | Exercise | Expected outcome |
| --- | --- | --- |
| Finance analyst | Ask Copilot to explain the optimized query in plain language for a report sign-off meeting. | The analyst gets reviewer-ready rationale without manually translating each SQL change. |
| Analytics engineer | Extend the query to include quarter-to-date metrics while preserving the validation pattern. | Copilot drafts the additional aggregation logic and the engineer reviews semantics. |
| Data engineer | Parameterize region and fiscal year for pipeline-driven execution. | Copilot produces a reusable execution pattern instead of one-off report SQL. |

## Production-hardening variants
- Add threshold checks that flag unexpected variance swings after the query rewrite.
- Generate a warehouse deployment checklist that covers permissions, dependency order, and rollback planning.
- Ask Copilot for a second-pass rewrite that prepares the optimized query for a view or stored procedure wrapper.
- Add a reviewer note explaining why unsupported index recommendations were intentionally excluded.
