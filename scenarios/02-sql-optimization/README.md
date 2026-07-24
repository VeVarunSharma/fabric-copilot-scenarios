# Scenario 02 - Financial reporting SQL optimization

This scenario shows how GitHub Copilot can rewrite a slow financial reporting query into a Fabric Warehouse-friendly version while preserving business meaning.

- [Sample prompt](sample-prompt.md)
- [Expected output](expected-output.md)
- [Extension exercises](extension-exercises.md)
- [Artifacts](artifacts/schema.sql)

## Business problem
A finance team runs a monthly variance report by business unit. The baseline query works, but it scans the fact table multiple times, carries unnecessary columns, and mixes filtering with presentation logic.

## Target personas and prerequisites
**Primary personas**
- Analytics engineers tuning Warehouse queries
- BI developers preparing finance-serving tables
- Data engineers reviewing query rewrites before production rollout

**Prerequisites**
- Familiarity with Fabric Warehouse T-SQL
- Ability to compare query semantics before and after optimization
- Understanding of variance and percentage calculations in financial reporting

## Manual baseline
Without Copilot, a practitioner typically:
1. Reads the baseline query and traces every repeated scan by hand.
2. Rewrites CTEs to push filters closer to the source.
3. Replaces `SELECT *` with explicit columns.
4. Rechecks safe-division behavior for percentage metrics.
5. Builds a result-equivalence query to prove the rewrite did not change finance outputs.

That work is careful but repetitive, especially when many reports follow the same pattern.

## Copilot-assisted workflow
1. Provide Copilot with the baseline query and the Fabric Warehouse constraints.
2. Ask for a rewrite that preserves result semantics and avoids unsupported advice such as user-managed index tuning.
3. Review the generated query for predicate pushdown, fewer scans, explicit columns, and safe division.
4. Run the validation script to confirm that the baseline and optimized outputs match.

## Sample Fabric artifact
This scenario keeps its canonical artifacts in the scenario folder:
- [Schema and sample data](artifacts/schema.sql)
- [Baseline query](artifacts/baseline.sql)
- [Optimized query](artifacts/optimized.sql)
- [Validation query](artifacts/validation.sql)

The optimized query should demonstrate:
- Predicate pushdown on fiscal year, region, scenario, and account category
- Reduced repeated scans of the financial postings fact table
- Explicit projection instead of `SELECT *`
- Safe division with `NULLIF` for percentage metrics

## Validation
Run the scripts in this order:
1. `artifacts/schema.sql`
2. `artifacts/baseline.sql`
3. `artifacts/optimized.sql`
4. `artifacts/validation.sql`

A successful validation run returns zero differences in both comparison directions.

## Learning objectives
- Recognize query patterns that are safe for Copilot to rewrite and easy for a human to verify.
- Apply Fabric Warehouse-compatible optimizations instead of generic database advice.
- Preserve finance-report semantics while reducing repeated work in the query plan.
- Use a repeatable validation pattern for before-and-after SQL changes.

## What work did Copilot eliminate?
Copilot eliminates the first pass of repetitive query restructuring: splitting filters from presentation logic, consolidating repeated scans, expanding `SELECT *` into explicit columns, and drafting the validation script. The analyst still owns semantic review and performance confirmation.

## Responsible use/security
- Do not paste confidential financial values into prompts unless the workspace and policy allow it.
- Require human review for every metric definition, especially variance percentages.
- Avoid recommendations that assume user-managed indexes or unsupported Fabric Warehouse knobs.
- Validate access controls separately; a query rewrite must not widen data exposure.
