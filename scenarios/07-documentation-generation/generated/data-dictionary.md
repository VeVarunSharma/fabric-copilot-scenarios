# Retail purchases data dictionary

> Generated draft - human approval required before this document is shared outside the delivery team.

## Source fixture summary

The committed retail-purchases backbone uses three CSV fixtures:

- `datasets/synthetic/retail-purchases/purchases.csv`
- `datasets/synthetic/retail-purchases/customers.csv`
- `datasets/synthetic/retail-purchases/products.csv`

Together they support the Bronze, Silver, and Gold pipeline flow that feeds the RetailSales semantic model.

## Purchases fields

| Field | Type | Description | Consumer guidance |
| --- | --- | --- | --- |
| `purchase_id` | `string` | Stable synthetic purchase identifier. | Use for traceability and deduplication. |
| `customer_id` | `string` | Synthetic customer identifier used for joins. | Join to the conformed customer outputs rather than reporting directly on the raw file. |
| `product_id` | `string` | Synthetic product identifier used for joins. | Join to the conformed product outputs before report use. |
| `purchase_ts` | `datetime` | UTC purchase timestamp. | Drives the Gold `Date` dimension and purchase-date filtering. |
| `ingest_ts` | `datetime` | UTC ingestion timestamp. | Supports deduplication and late-arrival analysis. |
| `quantity` | `integer` | Purchased unit count. | Use in basket-size and unit-volume analysis. |
| `unit_price` | `number` | Synthetic selling price per unit. | Used to derive revenue in Silver and Gold. |
| `store_id` | `string` | Store identifier carried into the Sales table. | Store-level analysis stays on `Sales[Store ID]` because there is no store dimension. |
| `channel` | `string` | Retail sales channel such as store, online, or pickup. | Safe for channel-level reporting. |
| `synthetic_record` | `string` | Safety marker with the constant value `SYNTHETIC`. | Confirms the file is demo-safe. |
| `anomaly_label` | `string` | Injected quality label used by the notebooks. | Drives quarantine and validation scenarios. |

## Customer lookup fields

| Field | Type | Description |
| --- | --- | --- |
| `customer_id` | `string` | Stable synthetic customer identifier. |
| `customer_name` | `string` | Fictional customer display name. |
| `loyalty_tier` | `string` | Loyalty segmentation attribute. |
| `home_region` | `string` | Synthetic customer region. |
| `signup_date` | `date` | Customer signup date. |
| `email_domain` | `string` | Safe demo-only email domain. |
| `synthetic_record` | `string` | Safety marker with the constant value `SYNTHETIC`. |

## Product lookup fields

| Field | Type | Description |
| --- | --- | --- |
| `product_id` | `string` | Stable synthetic product identifier. |
| `product_name` | `string` | Fictional product display name. |
| `category` | `string` | Top-level retail category. |
| `subcategory` | `string` | Retail subcategory. |
| `unit_cost` | `number` | Synthetic cost per unit. |
| `unit_price` | `number` | Synthetic selling price per unit. |
| `is_active` | `string` | Source flag converted to a boolean in Silver. |
| `synthetic_record` | `string` | Safety marker with the constant value `SYNTHETIC`. |

## Curated table catalog

| Table | Purpose | Grain | Quality highlights |
| --- | --- | --- | --- |
| `bronze.retail_purchases_raw` | Raw purchase landing table with ingestion metadata. | Purchase event | Required purchase fields must exist and `source_file` must be populated. |
| `bronze.retail_customers_raw` | Raw customer lookup landing table. | Customer | Required customer fields must exist. |
| `bronze.retail_products_raw` | Raw product lookup landing table. | Product | Required product fields must exist. |
| `silver.retail_customers` | Conformed customer dimension feed. | Customer | Latest row per `customer_id`; `customer_key` is populated. |
| `silver.retail_products` | Conformed product dimension feed. | Product | Latest row per `product_id`; `product_key` is populated. |
| `silver.retail_sales_enriched` | Purchase-level Silver sales table with derived financial metrics. | Purchase | Duplicate purchases removed and valid rows retain customer and product keys. |
| `silver.retail_purchases_quarantine` | Purchase rows blocked by quality or referential checks. | Purchase | `quarantine_reason` must be populated. |
| `gold.Date` | Direct Lake calendar dimension. | Date | `date_key` is unique and `year_month` is populated. |
| `gold.Customer` | Direct Lake customer dimension. | Customer | `customer_key` is unique. |
| `gold.Product` | Direct Lake product dimension. | Product | `product_key` is unique. |
| `gold.Sales` | Direct Lake fact table for the semantic model. | Purchase line | `date_key` is populated and financial columns reconcile to Silver. |
| `gold.sales_monthly_summary` | Supplemental monthly by-channel aggregate. | Year-month x channel | `gross_margin_pct` is populated when revenue is nonzero. |

## Semantic-model usage

The RetailSales semantic model consumes `gold.Date`, `gold.Customer`, `gold.Product`, and `gold.Sales`. The committed `gold.sales_monthly_summary` table is a supporting analytics output and is not currently wired into the semantic model.

## Human approval checklist

- [ ] Field definitions match the committed schemas and fixtures.
- [ ] Curated table purposes reflect the actual notebooks.
- [ ] Semantic-model notes match the committed TMDL.
- [ ] Customer-safe wording is approved before publication.
