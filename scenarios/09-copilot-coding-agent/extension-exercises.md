# Extension exercises

## Guided variations
1. Add a second acceptance criterion that quarantines records with negative sales amounts instead of loading them.
2. Expand the deduplication key to include `store_id` if the business later allows transaction ID reuse across banners.
3. Add a markdown release note that Copilot should update when the pull request lands.

## Persona-specific extensions
- **Data engineer**: Ask Copilot to emit a second helper that returns metrics for dropped stale rows.
- **Engineering manager**: Ask Copilot to draft the reviewer guidance for required checks and CODEOWNERS coverage.
- **Platform admin**: Ask Copilot to summarize which repository policies must remain human controlled.

## Production-hardening exercises
- Add structured logging without leaking row contents.
- Require coverage for invalid dates and malformed ingest sequences.
- Introduce a dry-run mode that reports what would be deduplicated before a pipeline rerun.
