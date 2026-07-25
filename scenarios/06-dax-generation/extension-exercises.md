# Extension exercises

## Suggested variations

1. Replace the rolling 90-day measure with a rolling 12-month measure.
2. Add a channel-level validation query that groups by `Sales[Sales Channel]` if the finalized model exposes that column.
3. Ask Copilot to draft descriptions for every existing measure on `Sales`.
4. Produce a release checklist for adding the rolling measure to the canonical model.

## Production-hardening ideas

- Align generated measures with the existing `Financial`, `Orders`, and `Time Intelligence` display folders.
- Add a fiscal-calendar variant if the `Date` table is extended.
- Extend validation queries with product and store spot checks before deployment.

## Facilitator review checklist

- [ ] The learner can explain why helper measures improve reuse.
- [ ] The learner can identify when `DIVIDE` is safer than `/`.
- [ ] The learner can explain why store grouping stays on `Sales[Store ID]` in this model.
- [ ] The learner can distinguish production measures from validation queries.

## What work did Copilot eliminate?

Copilot removed repetitive formula drafting and made it easier to explore several KPI variants quickly without naming drift.
