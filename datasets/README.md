# Governed datasets

## Safe-data statement

All records in `datasets/synthetic/` are fictional and generated for demos, tests,
and workshop walkthroughs. They do not contain real people, real organizations,
real account numbers, real device identifiers, PHI, or production business data.
Every fixture row includes the `synthetic_record` marker with the value
`SYNTHETIC`.

These guarantees remain unchanged by the narrow public-data exception below.

## Reviewed public aggregate data

`datasets/public/` may contain explicitly reviewed, non-sensitive public
aggregate/open data. Each public snapshot must be pinned and accompanied by
provenance, licence and attribution, checksum, contract validation, and a
human-reviewed refresh process. Transformations must be deterministic,
documented, and fail on source-contract drift. Public snapshots must never
contain customer, tenant, person-level, PII, PHI, credential, confidential, or
restricted data.

Governed public sources:

| Dataset | Purpose | Governance record |
| --- | --- | --- |
| BC regional-district population | Reviewed BC open-data source for regional population processing | [`public/bc-population/README.md`](public/bc-population/README.md) |
| Historical CCHS annual health characteristics | Scenario 12 Power BI model and report demonstration | [`public/cchs-annual/README.md`](public/cchs-annual/README.md) |

These exceptions do not permit changing synthetic-only persona or scenario
prompts.

## Generation instructions

Generate the committed fixtures with the default deterministic settings:

```bash
python3 scripts/generate_data.py
```

Common options:

```bash
python3 scripts/generate_data.py --output-dir datasets/synthetic --rows 12 --seed 4242
python3 scripts/generate_data.py --domain retail-purchases --output-dir datasets/synthetic
```

The generator uses only the Python standard library, a fixed default seed, and
stable record ordering so repeated runs reproduce the committed fixtures.

## Domain catalog

| Domain | Files | Purpose | Schemas |
| --- | --- | --- | --- |
| Customer transactions | `synthetic/customer-transactions/transactions.csv` | Payment-like transaction feed for ingestion, deduplication, and lateness demos. | [`transactions.schema.json`](schemas/transactions.schema.json) |
| Healthcare claims | `synthetic/healthcare-claims/claims.csv` | Fictional claims intake data for quality checks without PHI. | [`claims.schema.json`](schemas/claims.schema.json) |
| Retail purchases | `synthetic/retail-purchases/customers.csv`, `products.csv`, `purchases.csv` | Small retail backbone for Bronze/Silver/Gold style exercises, including customer and product display attributes for Direct Lake model demos. | [`customers.schema.json`](schemas/customers.schema.json), [`products.schema.json`](schemas/products.schema.json), [`purchases.schema.json`](schemas/purchases.schema.json) |
| IoT telemetry | `synthetic/iot-telemetry/telemetry.jsonl` | Time-series device feed for anomaly detection and ingestion exercises. | [`telemetry.schema.json`](schemas/telemetry.schema.json) |
| Financial reporting | `synthetic/financial-reporting/accounts.csv`, `general_ledger.csv` | Ledger-oriented sample data for reconciliation and referential quality demos. | [`accounts.schema.json`](schemas/accounts.schema.json), [`general_ledger.schema.json`](schemas/general_ledger.schema.json) |

## Known injected anomalies

These issues are intentional and labeled with `anomaly_label` or
`anomaly_labels` for demo-friendly validation scenarios.

| Domain | Injected anomaly | How to find it |
| --- | --- | --- |
| Customer transactions | Duplicate transaction | `anomaly_label=duplicate_transaction` and repeated `transaction_id` |
| Customer transactions | Late-arriving record | `anomaly_label=late_arrival` with delayed `ingest_ts` |
| Healthcare claims | Missing provider code | `anomaly_label=missing_provider_code` with blank `provider_code` |
| Healthcare claims | Invalid claim amount | `anomaly_label=invalid_claim_amount` with negative `claim_amount` |
| Retail purchases | Duplicate purchase | `anomaly_label=duplicate_purchase` and repeated `purchase_id` |
| Retail purchases | Null retail key | `anomaly_label=null_customer_id` with blank `customer_id` |
| Retail purchases | Invalid retail values | `anomaly_label=invalid_quantity_zero` with zero `quantity` and blank `store_id` |
| IoT telemetry | Out-of-range readings | `anomaly_labels=["out_of_range_reading"]` |
| Financial reporting | Orphan account reference | `anomaly_label=orphan_account` where `account_id` is not in `accounts.csv` |

## Data dictionaries

Use the schema files in `datasets/schemas/` as the machine-readable data
dictionaries. Each schema lists the required fields, field meanings, and column
order.

- Customer transactions: [`transactions.schema.json`](schemas/transactions.schema.json)
- Healthcare claims: [`claims.schema.json`](schemas/claims.schema.json)
- Retail customers: [`customers.schema.json`](schemas/customers.schema.json)
- Retail products: [`products.schema.json`](schemas/products.schema.json)
- Retail purchases: [`purchases.schema.json`](schemas/purchases.schema.json)
- IoT telemetry: [`telemetry.schema.json`](schemas/telemetry.schema.json)
- Financial accounts: [`accounts.schema.json`](schemas/accounts.schema.json)
- Financial ledger entries: [`general_ledger.schema.json`](schemas/general_ledger.schema.json)

Retail backbone notes:

- `customers.csv` includes a fictional `customer_name` field for readable dimensions.
- `products.csv` includes fictional `product_name`, plus positive numeric `unit_cost`
  values that remain below `unit_price`.
