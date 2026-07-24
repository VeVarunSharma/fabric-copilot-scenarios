# Scenario 06 - DAX generation

Generate a KPI starter pack that matches the committed RetailSales semantic model.

## Business problem

The RetailSales semantic model already exposes `Date`, `Customer`, `Product`, and `Sales`, and business measures live on `Sales`. The team wants Copilot to draft and validate the required KPI measures while staying aligned to the exact finalized column names already present in the canonical TMDL.

## Reference assets

- Semantic model: [../../semantic-models/RetailSales/](../../semantic-models/RetailSales/)
- Measure file: [artifacts/measures.dax](artifacts/measures.dax)
- Validation query file: [artifacts/validation-queries.dax](artifacts/validation-queries.dax)

## Actual modeling contract

- Tables used in this scenario: `Sales`, `Date`, and `Product`
- Measure home: `Sales`
- Core columns: `Sales[Revenue Amount]`, `Sales[Cost Amount]`, `Sales[Order ID]`, `Sales[Store ID]`, `Date[Date]`, `Date[Year]`, `Date[Month Number]`, `Date[Month Name]`, and `Product[Category]`

## Learning objectives

- Prompt Copilot with the exact finalized DAX surface instead of placeholder names.
- Apply safe DAX patterns such as `DIVIDE`, reusable helper measures, and readable `VAR` names.
- Keep measure references unqualified and column references qualified.
- Validate KPI output with DAX Query View scripts that use `ORDER BY` for multi-row results.
- Document format-string and description expectations for the model owner.

## Manual baseline

Without Copilot, an analyst writes each KPI and validation query by hand, double-checks time-intelligence syntax, and repeatedly cross-references the TMDL to avoid naming drift.

## Copilot-assisted workflow

1. Ground Copilot with the exact table and column names from the finalized canonical model.
2. Ask for the required KPI set plus only the helper measures that improve reuse.
3. Require `DIVIDE`, `_`-prefixed variables, qualified columns, and unqualified measures.
4. Ask for validation queries grouped by year, `Product[Category]`, and `Sales[Store ID]`.
5. Compare the result with [artifacts/measures.dax](artifacts/measures.dax) and [artifacts/validation-queries.dax](artifacts/validation-queries.dax).

## Validation steps

1. Add the measures to the `Sales` table in the RetailSales model.
2. Run the queries in [artifacts/validation-queries.dax](artifacts/validation-queries.dax).
3. Confirm currency measures use the expected currency format string.
4. Confirm percent measures render as percentages with two decimals.
5. Confirm store-level validation uses `Sales[Store ID]` because there is no separate store dimension.

## Human review checklist

- [ ] Column references use the finalized canonical names.
- [ ] Measure references are unqualified.
- [ ] Ratio logic uses `DIVIDE`.
- [ ] Time-intelligence measures use `Date[Date]`.
- [ ] Validation queries use `ORDER BY` for multi-row results.

## What work did Copilot eliminate?

Copilot eliminated the repetitive KPI scaffolding, the syntax lookups for time intelligence, and the first draft of the validation queries so reviewers could focus on business correctness.
