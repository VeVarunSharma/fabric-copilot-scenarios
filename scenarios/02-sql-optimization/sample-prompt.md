# Sample prompt - Scenario 02

## Ready to copy prompt

```text
Optimize the following Microsoft Fabric Warehouse query without changing its result semantics.

Requirements:
- Keep the same output columns and meaning.
- Use Fabric Warehouse-compatible T-SQL only.
- Do not recommend or depend on user-managed indexes.
- Reduce repeated scans of the fact table.
- Push predicates down as early as possible.
- Replace SELECT * with explicit columns.
- Use safe division for percentage calculations.
- Return the optimized query and a short explanation of what changed.
- Also draft a validation query that proves the baseline and optimized results are identical.

Baseline query location:
- scenarios/02-sql-optimization/artifacts/baseline.sql

Reference schema:
- scenarios/02-sql-optimization/artifacts/schema.sql
```

## Follow-up prompts
- "Explain which filters were pushed down and why that matters in Fabric Warehouse."
- "Rewrite the explanation for a finance reviewer who cares about metric preservation, not SQL internals."
- "Show the minimum validation query I can run to compare baseline and optimized output sets."

## Acceptance criteria
- The rewrite scans the postings fact table once for actual and budget metrics.
- The result set matches the baseline exactly.
- The explanation stays within Fabric Warehouse constraints.
- Percentage calculations return `NULL` instead of failing on zero denominators.
