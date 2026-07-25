# Expected output - Scenario 02

## Canonical files
- [Schema and sample data](artifacts/schema.sql)
- [Baseline query](artifacts/baseline.sql)
- [Optimized query](artifacts/optimized.sql)
- [Validation query](artifacts/validation.sql)

The ideal Copilot response should point the user to the optimized SQL artifact and summarize the rewrite, not dump every line of SQL into chat without explanation.

## Key generated structures

### Baseline pattern to improve
The baseline query intentionally shows common manual-reporting issues:
- a broad `filtered_postings` CTE that keeps unnecessary columns
- separate scans for actuals and budgets
- a final `SELECT *` from a presentation CTE
- safe division expressed with repetitive `CASE` logic

### Fabric Warehouse-compatible rewrite
The optimized query should call out four improvements:

| Rewrite area | Expected change |
| --- | --- |
| Predicate pushdown | Filter fiscal year, active business units, region, scenarios, and account categories before aggregation |
| Reduced scans | Aggregate actual and budget metrics in one grouped pass over the fact table |
| Explicit columns | Project only the reporting columns needed downstream |
| Safe division | Use `NULLIF` on denominators so zero-budget rows return `NULL` instead of raising errors |

### Validation shape
The validation script should compare baseline and optimized result sets in both directions with `EXCEPT`. A strong answer highlights that zero differences are required before the rewrite can move forward.

## Human review checklist
- Confirm every output column retains the original business meaning.
- Check that active-business-unit filtering did not remove valid rows.
- Review zero-denominator behavior for finance approval.
- Inspect whether all pushed-down predicates are semantically safe.
- Run the validation query before discussing performance wins.
