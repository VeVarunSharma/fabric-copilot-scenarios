# Scenario 05 - Semantic model analysis

Review the committed RetailSales semantic model before it is used in customer-facing reporting.

## Business problem

A retail analytics team has a Direct Lake semantic model in source control and needs a release-ready review of the actual table inventory, relationship behavior, hidden keys, measure quality, and Copilot-friendly metadata. The goal is to compare the baseline model with the finalized canonical model without inventing fields that do not exist in the committed TMDL.

## Reference assets

- Canonical semantic model: [../../semantic-models/RetailSales/](../../semantic-models/RetailSales/)
- Baseline semantic model: [../../semantic-models/RetailSales/baseline/](../../semantic-models/RetailSales/baseline/)
- Approved findings benchmark: [artifacts/analysis-findings.md](artifacts/analysis-findings.md)

## Actual model contract

The committed semantic model contains four tables only:

- `Date`
- `Customer`
- `Product`
- `Sales`

All business measures live on `Sales`, and the Direct Lake source tables are `gold.Date`, `gold.Customer`, `gold.Product`, and `gold.Sales`.

## Baseline versus canonical naming

Use baseline names only when explicitly describing the baseline files:

- Baseline `Customer`: `CustomerKey`, `CustomerName`, `LoyaltyTier`
- Baseline `Product`: `ProductKey`, `ProductName`, `Category`
- Baseline `Sales`: `SalesKey`, `DateKey`, `CustomerKey`, `ProductKey`, `PurchaseId`, `Revenue`, `Cost`, plus measures `Revenue` and `MarginPct`

Use finalized canonical names when describing the current model surface:

- Canonical `Date`: `Date Key`, `Date`, `Year`, `Quarter`, `Month Number`, `Month Name`, `Year Month`
- Canonical `Customer`: `Customer Key`, `Customer ID`, `Customer Name`, `Loyalty Tier`, `Home Region`, `Signup Date`, `Email Domain`
- Canonical `Product`: `Product Key`, `Product ID`, `Product Name`, `Category`, `Subcategory`, `Unit Price`, `Unit Cost`, `Is Active`
- Canonical `Sales`: `Sales Key`, `Date Key`, `Customer Key`, `Product Key`, `Order ID`, `Order Date`, `Store ID`, `Channel`, hidden financial base columns, and the committed measures

## Learning objectives

- Inventory the real baseline and canonical tables without drifting into hypothetical objects.
- Review the `Sales`-to-dimension star schema used by the committed model.
- Compare baseline technical names with the finalized canonical names accurately.
- Confirm surrogate keys are hidden in the canonical model and exposed in the baseline where relevant.
- Compare baseline bidirectional filtering with the canonical single-direction design.
- Review how committed measures and business-friendly naming improve Copilot grounding.

## Manual baseline

Without Copilot, a model owner must click through each table, compare TMDL files by hand, inspect every relationship, list exposed technical keys, translate baseline names into finalized canonical names, and document gaps from scratch.

## Copilot-assisted workflow

1. Open the baseline and canonical TMDL folders.
2. Ask Copilot to inventory the committed `Date`, `Customer`, `Product`, and `Sales` tables.
3. Request a comparison of baseline names such as `LoyaltyTier` and `PurchaseId` with canonical names such as `Loyalty Tier` and `Order ID`.
4. Ask for a severity-ranked remediation list tied to the exact artifacts in source control.
5. Compare the response with [artifacts/analysis-findings.md](artifacts/analysis-findings.md) before sign-off.

## Validation steps

1. Confirm the inventory names only `Date`, `Customer`, `Product`, and `Sales`.
2. Verify the baseline relationship file uses `bothDirections` and the canonical file uses `oneDirection`.
3. Verify the baseline uses `LoyaltyTier`, `Category`, and `PurchaseId` where applicable.
4. Verify the canonical review uses `Loyalty Tier`, `Category`, `Order ID`, `Home Region`, `Signup Date`, and `Email Domain` when describing the finalized model.
5. Confirm Direct Lake partitions point to the `gold` schema tables used by the model.
6. Run the stale-term check:

```bash
cd '/Users/ve/Work Documents/code/fabric-with-github' && if grep -R -nE 'Customer[S]egment|Customer[I]d|Product[I]d|Product[C]ategory|Order[I]d|Is[A]ctiveCustomer|Customer Is [A]ctive' scenarios/05-semantic-model-analysis; then echo 'scenario-05-stale-term-check-failed'; exit 1; else echo 'scenario-05-stale-term-check-ok'; fi
```

## Human review checklist

- [ ] No nonexistent tables or dimensions are referenced.
- [ ] Baseline and canonical differences are tied to actual TMDL content.
- [ ] Baseline wording uses `LoyaltyTier`, `Category`, and `PurchaseId` where appropriate.
- [ ] Canonical wording uses `Customer ID`, `Loyalty Tier`, `Order ID`, `Home Region`, and `Is Active` only where those fields really exist.
- [ ] Measure and metadata recommendations stay on the `Sales` table where appropriate.

## What work did Copilot eliminate?

Copilot eliminated the first-pass TMDL comparison, the repetitive relationship inspection, and the blank-page remediation draft so the reviewer could focus on approval-quality decisions.
