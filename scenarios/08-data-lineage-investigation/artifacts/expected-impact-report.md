# Expected downstream impact report

> Generated from `artifacts/lineage-manifest.json` using `scripts/build_lineage.py`.

## Change scenario: gold-sales-change

- Target asset: `gold.Sales` (table)
- Requested change: Change the published gross_margin_pct logic consumed by the RetailSales semantic model.
- Immediate downstream count: 1
- Full downstream count: 2

### Immediate downstream assets

- `RetailSales semantic model` (semantic_model)

### Full downstream impact

| Asset | Type | Owner | First downstream path |
| --- | --- | --- | --- |
| `RetailSales semantic model` | `semantic_model` | Retail Analytics | gold.Sales -> RetailSales semantic model |
| `RetailSales report scaffold` | `report` | Retail Analytics | gold.Sales -> RetailSales semantic model -> RetailSales report scaffold |

### Validation focus

- Refresh the semantic model and inspect impacted relationships and measures.
- Confirm the report scaffold still references the semantic model; add visual-level checks only after data-bound visuals are authored.

## Change scenario: purchase-schema-change

- Target asset: `purchases.csv` (source)
- Requested change: Add a nullable promo_code column to purchases.csv and preserve deterministic ordering.
- Immediate downstream count: 1
- Full downstream count: 18

### Immediate downstream assets

- `retail-medallion.DataPipeline` (pipeline)

### Full downstream impact

| Asset | Type | Owner | First downstream path |
| --- | --- | --- | --- |
| `retail-medallion.DataPipeline` | `pipeline` | Fabric Data Engineering | purchases.csv -> retail-medallion.DataPipeline |
| `01_bronze_ingestion` | `notebook` | Fabric Data Engineering | purchases.csv -> retail-medallion.DataPipeline -> 01_bronze_ingestion |
| `02_silver_transform` | `notebook` | Fabric Data Engineering | purchases.csv -> retail-medallion.DataPipeline -> 02_silver_transform |
| `03_gold_aggregations` | `notebook` | Fabric Data Engineering | purchases.csv -> retail-medallion.DataPipeline -> 03_gold_aggregations |
| `bronze.retail_purchases_raw` | `table` | Fabric Data Engineering | purchases.csv -> retail-medallion.DataPipeline -> 01_bronze_ingestion -> bronze.retail_purchases_raw |
| `bronze.retail_customers_raw` | `table` | Fabric Data Engineering | purchases.csv -> retail-medallion.DataPipeline -> 01_bronze_ingestion -> bronze.retail_customers_raw |
| `bronze.retail_products_raw` | `table` | Fabric Data Engineering | purchases.csv -> retail-medallion.DataPipeline -> 01_bronze_ingestion -> bronze.retail_products_raw |
| `silver.retail_customers` | `table` | Fabric Data Engineering | purchases.csv -> retail-medallion.DataPipeline -> 02_silver_transform -> silver.retail_customers |
| `silver.retail_products` | `table` | Fabric Data Engineering | purchases.csv -> retail-medallion.DataPipeline -> 02_silver_transform -> silver.retail_products |
| `silver.retail_sales_enriched` | `table` | Fabric Data Engineering | purchases.csv -> retail-medallion.DataPipeline -> 02_silver_transform -> silver.retail_sales_enriched |
| `silver.retail_purchases_quarantine` | `table` | Fabric Data Engineering | purchases.csv -> retail-medallion.DataPipeline -> 02_silver_transform -> silver.retail_purchases_quarantine |
| `gold.Date` | `table` | Retail Analytics | purchases.csv -> retail-medallion.DataPipeline -> 03_gold_aggregations -> gold.Date |
| `gold.Customer` | `table` | Retail Analytics | purchases.csv -> retail-medallion.DataPipeline -> 03_gold_aggregations -> gold.Customer |
| `gold.Product` | `table` | Retail Analytics | purchases.csv -> retail-medallion.DataPipeline -> 03_gold_aggregations -> gold.Product |
| `gold.Sales` | `table` | Retail Analytics | purchases.csv -> retail-medallion.DataPipeline -> 03_gold_aggregations -> gold.Sales |
| `gold.sales_monthly_summary` | `table` | Retail Analytics | purchases.csv -> retail-medallion.DataPipeline -> 03_gold_aggregations -> gold.sales_monthly_summary |
| `RetailSales semantic model` | `semantic_model` | Retail Analytics | purchases.csv -> retail-medallion.DataPipeline -> 03_gold_aggregations -> gold.Date -> RetailSales semantic model |
| `RetailSales report scaffold` | `report` | Retail Analytics | purchases.csv -> retail-medallion.DataPipeline -> 03_gold_aggregations -> gold.Date -> RetailSales semantic model -> RetailSales report scaffold |

### Validation focus

- Review pipeline parameters, dependencies, and retry behavior.
- Validate notebook schema handling, transformation logic, and logging.
- Re-run reconciliations and confirm row-level quality rules still pass.
- Refresh the semantic model and inspect impacted relationships and measures.
- Confirm the report scaffold still references the semantic model; add visual-level checks only after data-bound visuals are authored.

## Change scenario: silver-logic-change

- Target asset: `silver.retail_sales_enriched` (table)
- Requested change: Update margin handling when unit_cost is missing and the fallback cost calculation is used.
- Immediate downstream count: 1
- Full downstream count: 8

### Immediate downstream assets

- `03_gold_aggregations` (notebook)

### Full downstream impact

| Asset | Type | Owner | First downstream path |
| --- | --- | --- | --- |
| `03_gold_aggregations` | `notebook` | Fabric Data Engineering | silver.retail_sales_enriched -> 03_gold_aggregations |
| `gold.Date` | `table` | Retail Analytics | silver.retail_sales_enriched -> 03_gold_aggregations -> gold.Date |
| `gold.Customer` | `table` | Retail Analytics | silver.retail_sales_enriched -> 03_gold_aggregations -> gold.Customer |
| `gold.Product` | `table` | Retail Analytics | silver.retail_sales_enriched -> 03_gold_aggregations -> gold.Product |
| `gold.Sales` | `table` | Retail Analytics | silver.retail_sales_enriched -> 03_gold_aggregations -> gold.Sales |
| `gold.sales_monthly_summary` | `table` | Retail Analytics | silver.retail_sales_enriched -> 03_gold_aggregations -> gold.sales_monthly_summary |
| `RetailSales semantic model` | `semantic_model` | Retail Analytics | silver.retail_sales_enriched -> 03_gold_aggregations -> gold.Date -> RetailSales semantic model |
| `RetailSales report scaffold` | `report` | Retail Analytics | silver.retail_sales_enriched -> 03_gold_aggregations -> gold.Date -> RetailSales semantic model -> RetailSales report scaffold |

### Validation focus

- Validate notebook schema handling, transformation logic, and logging.
- Re-run reconciliations and confirm row-level quality rules still pass.
- Refresh the semantic model and inspect impacted relationships and measures.
- Confirm the report scaffold still references the semantic model; add visual-level checks only after data-bound visuals are authored.
