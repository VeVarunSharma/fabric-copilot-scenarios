# Retail medallion pipeline runbook

> Generated draft - human approval required before operational publication.

## Purpose

This runbook covers `pipelines/retail-medallion.DataPipeline/pipeline-content.json`, which orchestrates the retail-purchases medallion flow from committed source fixtures through Gold publishing.

## Invocation model

The committed pipeline definition does not include a schedule. Workspace orchestration is expected to supply the runtime invocation pattern.

## Runtime parameters

- `environment`
- `processing_date`
- `pipeline_run_id`

## Primary activities

1. `Run Bronze Ingestion`
   - Notebook: `notebooks/retail-medallion/01_bronze_ingestion.ipynb`
   - Writes Bronze raw tables for purchases, customers, and products plus `bronze.retail_ingestion_audit`.
2. `Run Silver Transform`
   - Notebook: `notebooks/retail-medallion/02_silver_transform.ipynb`
   - Produces `silver.retail_customers`, `silver.retail_products`, `silver.retail_sales_enriched`, and `silver.retail_purchases_quarantine`.
3. `Run Gold Aggregations`
   - Notebook: `notebooks/retail-medallion/03_gold_aggregations.ipynb`
   - Publishes `gold.Date`, `gold.Customer`, `gold.Product`, `gold.Sales`, and `gold.sales_monthly_summary`.
4. `Mark Pipeline Success`
   - Sets the pipeline status variable after Gold succeeds.

## Built-in failure paths

The committed definition includes these explicit failure activities:

- `Bronze Failure`
- `Silver Failure`
- `Gold Failure`

Each failure branch is triggered when its notebook stage fails or times out after the configured retry policy.

## Operator checks

- Confirm the expected source files are available in the retail-purchases landing area.
- Review Bronze audit output if a source-file or required-column problem is suspected.
- Review `silver.retail_purchases_quarantine` when anomalies or missing joins increase.
- Confirm `gold.Sales` row counts and the supporting Gold dimension row counts after Gold completes.
- Delay semantic-model validation if the Gold stage fails.

## Recovery guidance

- Re-run from the failed notebook stage only after confirming upstream tables are consistent.
- Preserve the `processing_date` and `pipeline_run_id` context when correlating notebook logs.
- If a schema mismatch is suspected, compare the retail-purchases fixtures with the documented source-file columns before replay.

## Human approval checklist

- [ ] Runtime expectations match the target Fabric workspace.
- [ ] Failure-handling guidance aligns with operational practice.
- [ ] Notebook names and table outputs match the committed artifacts.
- [ ] Escalation ownership is added before publication.
