# Retail purchases architecture notes

> Generated draft - human approval required before design review circulation.

## Solution overview

The committed retail-purchases solution uses a Fabric medallion flow. Three
synthetic fixture files land into Bronze raw tables, Silver produces conformed
customer, product, and enriched sales outputs, and Gold publishes the Direct Lake
tables consumed by the RetailSales semantic model. The associated report is a
source-controlled scaffold that references the model by path.

## Primary components

| Component | Role | Reference |
| --- | --- | --- |
| Source fixtures | Synthetic retail purchases, customers, and products | `datasets/synthetic/retail-purchases/` |
| Pipeline | Sequential orchestration of Bronze, Silver, and Gold notebooks | `pipelines/retail-medallion.DataPipeline/pipeline-content.json` |
| Bronze notebook | Reads retail-purchases source files into Bronze raw tables | `notebooks/retail-medallion/01_bronze_ingestion.ipynb` |
| Silver notebook | Deduplicates purchases, handles anomalies, and produces conformed Silver outputs | `notebooks/retail-medallion/02_silver_transform.ipynb` |
| Gold notebook | Publishes Gold Date, Customer, Product, Sales, and monthly summary tables | `notebooks/retail-medallion/03_gold_aggregations.ipynb` |
| Semantic model | Direct Lake RetailSales model using four Gold tables | `semantic-models/RetailSales/` |
| Report scaffold | RetailSales report source scaffold with a model reference and placeholder visual | `semantic-models/RetailSales/RetailSales.Report/` |

## Medallion flow summary

- Bronze captures the landed purchase, customer, and product files with ingestion metadata.
- Silver creates conformed customer and product outputs plus the enriched sales table used for Gold publication.
- Gold publishes `gold.Date`, `gold.Customer`, `gold.Product`, and `gold.Sales` for Direct Lake consumption.
- `gold.sales_monthly_summary` is a supplemental aggregate and is not the current semantic-model source.

## Semantic-model notes

The committed semantic model exposes the `Date`, `Customer`, `Product`, and
`Sales` tables only. Measures live on `Sales`, and the report scaffold references
that semantic model by path. It does not yet demonstrate data-bound RetailSales
visuals.

## Operating-model notes

- Fabric Data Engineering owns the medallion notebooks and pipeline definition.
- Retail Analytics owns semantic-model usability and report validation.
- Platform Operations owns runtime invocation, monitoring, and incident handling.

## Assumptions requiring approval

- The workspace-specific triggering pattern is intentionally omitted from source control and must be approved separately.
- Gold table validation remains the release gate before semantic-model review.
- Customer-facing documentation should describe only the committed artifacts, not unpublished extensions.

## Human approval checklist

- [ ] Architecture terminology matches the customer vocabulary.
- [ ] Ownership boundaries are approved.
- [ ] The semantic-model consumption notes remain limited to the real Gold tables.
- [ ] Any environment-specific operational detail is added by the owning team before publication.
