# Scenario 07 - Documentation generation

Generate draft technical documentation from the committed retail purchases Fabric artifacts.

## Business problem

The repository contains realistic retail-purchases fixtures, notebook definitions, a Fabric pipeline, Gold tables, and a Direct Lake semantic model. The team wants Copilot to turn those committed artifacts into reviewable draft documentation without drifting into unrelated file names or invented runtime behavior.

## Scenario assets

- Input manifest: [input-manifest.json](input-manifest.json)
- Generated draft data dictionary: [generated/data-dictionary.md](generated/data-dictionary.md)
- Generated draft runbook: [generated/pipeline-runbook.md](generated/pipeline-runbook.md)
- Generated draft architecture notes: [generated/architecture-notes.md](generated/architecture-notes.md)

## Learning objectives

- Ground Copilot with the committed retail-purchases contract instead of a generic example.
- Reuse one manifest to generate documentation for analytics, operations, and architecture audiences.
- Keep generated content clearly labeled as draft material pending human approval.
- Document the actual notebook, pipeline, Bronze, Silver, and Gold artifact names used in the repository.
- Show where the semantic model consumes the Gold outputs and how the report
  scaffold references that model.

## Manual baseline

Without Copilot, an engineer or technical writer would read the fixtures, notebook code, pipeline JSON, and semantic-model files one by one, then draft several documents manually.

## Copilot-assisted workflow

1. Provide Copilot with [input-manifest.json](input-manifest.json).
2. Ask for separate outputs tailored to data consumers, operators, and architects.
3. Require every generated document to carry a draft notice.
4. Review the draft content against the committed artifacts before publication.
5. Promote only human-approved text into customer-facing documentation.

## Validation steps

1. Confirm the generated docs reference `purchases.csv`, `customers.csv`, and `products.csv`.
2. Confirm the runbook uses `01_bronze_ingestion`, `02_silver_transform`, and `03_gold_aggregations`.
3. Confirm the docs reference actual table names such as `bronze.retail_purchases_raw`, `silver.retail_sales_enriched`, and `gold.Sales`.
4. Confirm the semantic-model notes name `gold.Date`, `gold.Customer`, `gold.Product`, and `gold.Sales` only.
5. Confirm every generated document begins with a draft notice.

## Human review checklist

- [ ] Source files and field names match the committed retail fixtures.
- [ ] Notebook and pipeline names match the repository.
- [ ] Bronze, Silver, and Gold table names are accurate.
- [ ] The semantic-model consumption notes are limited to the real Gold tables.
- [ ] No fabricated schedules, credentials, or environment-specific identifiers appear.

## What work did Copilot eliminate?

Copilot eliminated the blank-page documentation step and accelerated cross-artifact summarization into reviewable drafts grounded in the actual repository.
