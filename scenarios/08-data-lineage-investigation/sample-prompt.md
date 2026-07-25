# Sample prompt

```text
Use scenarios/08-data-lineage-investigation/artifacts/lineage-manifest.json as the source of truth.

Explain the lineage from the committed retail-purchases source files through:
- retail-medallion.DataPipeline
- 01_bronze_ingestion
- 02_silver_transform
- 03_gold_aggregations
- the actual Bronze, Silver, and Gold tables
- the RetailSales semantic model
- the RetailSales report

Then answer these questions:
1. Which assets are immediately downstream of the selected change target?
2. Which assets are indirectly affected later in the chain?
3. What should data engineering validate first?
4. What should analytics retest before release?

Constraints:
- Keep the explanation customer-safe.
- Do not invent extra tables, notebooks, or reports.
- Prefer a concise blast-radius summary followed by a review checklist.
```

## Follow-up prompts

- "Summarize only the impact of a change to purchases.csv."
- "Rewrite the output for an architecture review board."
- "Call out which downstream assets belong to data engineering versus analytics."

## What work did Copilot eliminate?

The prompt reduces manual dependency tracing and produces a faster first draft of the change-impact narrative.
