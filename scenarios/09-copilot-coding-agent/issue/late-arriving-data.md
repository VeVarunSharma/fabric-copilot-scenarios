# Issue: Support late-arriving retail transactions and idempotent deduplication

## Summary
Update the retail Silver transformation so a daily load can keep transactions that arrive on the current batch date even when the business date is up to two days older. The load must also be idempotent when the same transaction is replayed during a rerun.

## Business context
Store systems occasionally resend files after network interruptions. Today's implementation only keeps rows whose business date exactly equals the batch date, so late-arriving revenue is missed. When an upstream file is replayed, duplicate transaction IDs can be counted twice.

## Current files in scope
- `scenarios/09-copilot-coding-agent/starter/retail_transactions.py`
- `scenarios/09-copilot-coding-agent/starter/test_retail_transactions.py`

## Desired outcome
Create the equivalent of the files under `scenarios/09-copilot-coding-agent/expected/`:
- keep records whose `arrival_date` equals the batch date
- accept `business_date` values from the batch date back through two prior days
- reject future-dated rows and rows older than the grace window
- deduplicate repeated `transaction_id` values idempotently by keeping the highest `ingest_sequence`
- expose an `is_late_arrival` flag on kept rows

## Acceptance criteria
- [ ] `build_silver_batch(records, batch_date, late_arrival_days=2)` exists and stays stdlib-only.
- [ ] Only records with `arrival_date == batch_date` are considered for the batch.
- [ ] Records with `business_date` older than `late_arrival_days` are dropped.
- [ ] Records with future `business_date` values are dropped.
- [ ] Replayed rows with the same `transaction_id` collapse to one output record.
- [ ] The kept duplicate is the row with the highest `ingest_sequence`.
- [ ] Kept late records include `is_late_arrival = True`; same-day records use `False`.
- [ ] Unit tests cover on-time, late, stale, future, and replayed inputs.

## Non-goals
- No new external dependencies.
- No Fabric API calls, notebooks, or pipeline orchestration changes.
- No warehouse writes or file I/O.

## Implementation notes
- Keep output ordering deterministic for easy review.
- Prefer readable helper functions over framework code.
- Do not change paths outside `scenarios/09-copilot-coding-agent/`.

## Validation plan
```bash
python3 -m unittest discover -s scenarios/09-copilot-coding-agent/expected -p 'test_*.py'
```

## Expected pull request behavior
The pull request should summarize the code change, link back to this issue, show passing tests, and leave merge approval to a human reviewer.
