# RetailSales semantic model analysis findings

This artifact is the approved benchmark for Scenario 05.

## Reference assets

- Current semantic model: [../../../semantic-models/RetailSales/](../../../semantic-models/RetailSales/)
- Baseline semantic model: [../../../semantic-models/RetailSales/baseline/](../../../semantic-models/RetailSales/baseline/)

## Actual model inventory

| Table | Baseline state | Canonical state | Direct Lake source |
| --- | --- | --- | --- |
| `Date` | Baseline uses `DateKey`, `Date`, `Year`, and `MonthName`. | Canonical review language should use `Date Key`, `Date`, `Year`, `Quarter`, `Month Number`, `Month Name`, and `Year Month`. | `gold.Date` |
| `Customer` | Baseline uses `CustomerKey`, `CustomerName`, and `LoyaltyTier`. | Canonical review language should use `Customer Key`, `Customer ID`, `Customer Name`, `Loyalty Tier`, `Home Region`, `Signup Date`, and `Email Domain`. | `gold.Customer` |
| `Product` | Baseline uses `ProductKey`, `ProductName`, and `Category`. | Canonical review language should use `Product Key`, `Product ID`, `Product Name`, `Category`, `Subcategory`, `Unit Price`, `Unit Cost`, and `Is Active`. | `gold.Product` |
| `Sales` | Baseline uses `SalesKey`, `DateKey`, `CustomerKey`, `ProductKey`, `PurchaseId`, `Revenue`, and `Cost`, with measures `Revenue` and `MarginPct`. | Canonical review language should use `Sales Key`, `Date Key`, `Customer Key`, `Product Key`, `Order ID`, `Order Date`, `Store ID`, `Channel`, hidden financial base columns, and the committed measures. | `gold.Sales` |

## Relationship inventory

| Relationship | Baseline | Canonical | Review goal |
| --- | --- | --- | --- |
| `Sales to Date` | `bothDirections` | `oneDirection` | Confirm the `Date` table filters `Sales` without ambiguous back-propagation. |
| `Sales to Customer` | `bothDirections` | `oneDirection` | Keep `Customer` as a conformed dimension with predictable filtering. |
| `Sales to Product` | `bothDirections` | `oneDirection` | Prevent ambiguous product filtering and simplify report behavior. |

## Prioritized findings and remediation mapping

| Priority | Area | Expected baseline finding | Customer impact | Expected remediation | Validation signal |
| --- | --- | --- | --- | --- | --- |
| P1 | Relationship behavior | The baseline uses `bothDirections` on all three `Sales` relationships. | Ambiguous filtering can confuse report authors and produce harder-to-explain totals. | Align relationship filtering with the canonical `oneDirection` design in `relationships.tmdl`. | The canonical relationship file shows `oneDirection` for all three joins. |
| P1 | Hidden technical keys | The baseline exposes `SalesKey`, `DateKey`, `CustomerKey`, and `ProductKey`. | Users can drag meaningless keys into visuals and Copilot can ground on technical fields instead of business attributes. | In canonical review language, treat `Sales Key`, `Date Key`, `Customer Key`, and `Product Key` as hidden technical fields while keeping the business-facing columns visible. | The canonical checklist explicitly describes the key columns as hidden technical fields. |
| P2 | Customer shape changes | The baseline customer surface stops at `CustomerKey`, `CustomerName`, and `LoyaltyTier`. | Reviewers may miss the added business attributes needed for richer analysis and better grounding. | Describe the canonical customer surface with `Customer ID`, `Loyalty Tier`, `Home Region`, `Signup Date`, and `Email Domain`. | The review notes use only those committed canonical customer fields. |
| P2 | Product shape changes | The baseline product surface stops at `ProductKey`, `ProductName`, and `Category`. | Analysts cannot see the full business context available in the canonical product table. | Describe the canonical product surface with `Product ID`, `Category`, `Subcategory`, `Unit Price`, `Unit Cost`, and `Is Active`. | The review notes reflect the committed canonical product fields only. |
| P2 | Sales naming transition | The baseline uses `PurchaseId`, while the canonical model presents `Order ID` sourced from `purchase_id`. | Review narratives can become confusing if they mix baseline and canonical identifiers. | Make the baseline-to-canonical name transition explicit whenever `Sales` is discussed. | The review cleanly distinguishes `PurchaseId` from canonical `Order ID`. |
| P2 | Measure coverage on `Sales` | The baseline exposes only `Revenue` and `MarginPct`. | Reviewers cannot validate the full KPI surface without comparing against the canonical measure set. | Compare baseline measures with the committed canonical measures on `Sales` and use Scenario 06 for measure-specific validation. | The findings note baseline `Revenue` and `MarginPct` accurately and defer detailed KPI validation to Scenario 06. |
| P3 | Direct Lake review discipline | Both baseline and canonical models point to the `gold` schema, but the baseline gives less reviewer context about why those four tables are the approved consumption boundary. | Teams may discuss extra tables that are not actually in the semantic model. | Keep review output anchored to `gold.Date`, `gold.Customer`, `gold.Product`, and `gold.Sales` only. | The inventory and review notes reference only those four Direct Lake sources. |

## Suggested remediation sequence

1. Standardize all three `Sales` relationships on single-direction filtering.
2. Hide surrogate and foreign keys in the customer-facing model surface and describe them with canonical spaced names.
3. Promote factual canonical naming such as `Customer ID`, `Loyalty Tier`, `Order ID`, `Home Region`, and `Email Domain` into the approved review language.
4. Compare baseline `Revenue` and `MarginPct` with the committed canonical measures on `Sales`.
5. Re-run the stale-term check before publishing the scenario documentation.

## Deterministic stale-term check

```bash
cd '/Users/ve/Work Documents/code/fabric-with-github' && if grep -R -nE 'Customer[S]egment|Customer[I]d|Product[I]d|Product[C]ategory|Order[I]d|Is[A]ctiveCustomer|Customer Is [A]ctive' scenarios/05-semantic-model-analysis; then echo 'scenario-05-stale-term-check-failed'; exit 1; else echo 'scenario-05-stale-term-check-ok'; fi
```

## Expected handoff outcome

A reviewer should be able to convert this document into a short release backlog for the RetailSales model owner without re-reading every TMDL file manually.
