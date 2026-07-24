# Expected output

A high-quality Copilot response should match the canonical RetailSales semantic model.

## Expected KPI matrix

| Measure | Purpose | Format expectation | Description expectation |
| --- | --- | --- | --- |
| `Total Revenue` | Base sales amount | Currency, 2 decimals | Curated revenue from completed retail purchase lines. |
| `Gross Margin` | Helper profitability measure | Currency, 2 decimals | Revenue minus cost. |
| `Gross Margin %` | Profitability ratio | Percentage, 2 decimals | Gross margin divided by total revenue. |
| `Order Count` | Helper order measure | Whole number | Distinct count of retail purchase orders. |
| `Average Order Value` | Basket KPI | Currency, 2 decimals | Revenue divided by order count. |
| `Revenue YTD` | Time intelligence | Currency, 2 decimals | Year-to-date revenue using `Date[Date]`. |
| `Revenue Previous Year` | Time comparison | Currency, 2 decimals | Revenue for the same period in the prior year. |
| `Revenue YoY %` | Trend ratio | Percentage, 2 decimals | Percentage change versus prior-year revenue. |
| `Revenue Rolling 90 Days` | Short-term trend | Currency, 2 decimals | Revenue across the latest visible 90-day window. |

## Canonical artifacts

- [artifacts/measures.dax](artifacts/measures.dax)
- [artifacts/validation-queries.dax](artifacts/validation-queries.dax)

## Review checklist

- [ ] The measure set uses `Sales`, `Date`, and `Product` exactly as committed.
- [ ] Helper measures are justified and reusable.
- [ ] Finalized column references use `Sales[Revenue Amount]`, `Sales[Cost Amount]`, `Sales[Order ID]`, `Sales[Store ID]`, `Date[Month Number]`, `Date[Month Name]`, and `Product[Category]`.
- [ ] Time-intelligence logic uses `Date[Date]` consistently.
- [ ] Store-level validation groups by `Sales[Store ID]`.

## Validation

Load the measures into the semantic model, execute the validation queries, and compare the results with a trusted baseline or spot-check output from the gold tables.

## What work did Copilot eliminate?

Copilot eliminated the boilerplate for common KPI patterns and produced a testable draft instead of isolated snippets.
