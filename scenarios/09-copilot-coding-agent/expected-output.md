# Expected output

## Expected response shape
A strong Copilot-assisted outcome should describe:
1. The code change to accept late-arriving transactions within a grace window.
2. The idempotent deduplication rule for replayed transaction IDs.
3. The unit tests added or updated to prove the behavior.
4. A brief PR summary that points reviewers back to the issue acceptance criteria.

## Canonical generated artifact
- Baseline: [starter/](starter/)
- Expected target after the PR: [expected/](expected/)

## Important design choices
- The enhanced implementation only processes records that arrived in the current batch.
- It accepts business dates up to two days older than the batch date.
- It keeps the highest `ingest_sequence` for a repeated transaction ID so reruns are idempotent.
- It marks late arrivals explicitly so downstream logic can audit them.
- The example stays stdlib-only and deterministic for workshop use.

## Example PR summary
```text
## Summary
- allow transactions that arrive on the batch date to be up to two business days late
- deduplicate replayed transaction IDs by keeping the highest ingest_sequence
- extend unit tests for late-arriving and replayed retail transactions

## Validation
- python3 -m unittest discover -s scenarios/09-copilot-coding-agent/expected -p 'test_*.py'
```

## Review checklist
- The implementation rejects future-dated and stale transactions.
- Duplicate transaction IDs collapse to one output record.
- The kept duplicate is deterministic and easy to explain to reviewers.
- Tests cover on-time, late-arriving, stale, and replayed inputs.
- The PR summary is short and maps directly to the issue.
