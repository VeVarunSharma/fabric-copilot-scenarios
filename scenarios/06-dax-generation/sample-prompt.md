# Sample prompt

```text
Generate DAX for the committed RetailSales semantic model in ../../semantic-models/RetailSales/.

Use the exact finalized names already present in the model:
- Sales[Revenue Amount]
- Sales[Cost Amount]
- Sales[Order ID]
- Sales[Store ID]
- Date[Date]
- Date[Year]
- Date[Month Number]
- Date[Month Name]
- Product[Category]

Measures must live on Sales.

Required measures:
- Total Revenue
- Gross Margin %
- Average Order Value
- Revenue YTD
- Revenue Previous Year
- Revenue YoY %
- A rolling revenue measure

Constraints:
- Use supporting helper measures only when they improve reuse.
- Use qualified column references and unqualified measure references.
- Use VAR names prefixed with an underscore.
- Use DIVIDE for every ratio.
- Include description and format-string expectations in the explanation.
- Also generate DAX Query View validation queries with ORDER BY for every multi-row result.
- Use Sales[Store ID] for store-level grouping because there is no store dimension in this model.
```

## Follow-up prompts

- "Rewrite the rolling measure as a rolling 12-month measure."
- "Add display-folder suggestions that match the current Sales table organization."
- "Explain which measures depend on the Date table being marked correctly."

## What work did Copilot eliminate?

The prompt removes the need to author each KPI and validation query from scratch while keeping the output aligned to the committed TMDL.
