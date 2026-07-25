# Sample prompt

```text
You are reviewing the committed RetailSales semantic model in this repository.

Compare:
- ../../semantic-models/RetailSales/
- ../../semantic-models/RetailSales/baseline/

Use only the actual model contract in source control:
- Tables: Date, Customer, Product, Sales
- Measures live on Sales
- Direct Lake sources: gold.Date, gold.Customer, gold.Product, gold.Sales

Use baseline names only when you are explicitly describing the baseline:
- CustomerKey, CustomerName, LoyaltyTier
- ProductKey, ProductName, Category
- SalesKey, DateKey, CustomerKey, ProductKey, PurchaseId, Revenue, Cost
- Measures Revenue and MarginPct

Use finalized canonical names when you describe the current model:
- Date Key, Date, Year, Quarter, Month Number, Month Name, Year Month
- Customer Key, Customer ID, Customer Name, Loyalty Tier, Home Region, Signup Date, Email Domain
- Product Key, Product ID, Product Name, Category, Subcategory, Unit Price, Unit Cost, Is Active
- Sales Key, Date Key, Customer Key, Product Key, Order ID, Order Date, Store ID, Channel, hidden financial base columns, and the committed measures

Produce:
1. A table-by-table inventory for Date, Customer, Product, and Sales.
2. A relationship review covering cardinality and filter direction.
3. A hidden-key review that compares baseline naming and exposure with the canonical model.
4. A measure review focused on Sales naming, committed measures, and release readiness.
5. A prioritized finding list with P1, P2, and P3 severities.
6. A remediation mapping tied to the exact committed artifacts.

Constraints:
- Do not invent a store dimension or any extra fact table.
- Make baseline-vs-canonical naming differences explicit.
- Keep the baseline customer, product, and sales field lists aligned to the committed baseline TMDL.
- Keep the canonical customer, product, and sales field lists aligned to the committed canonical TMDL.
- Call out the baseline use of bothDirections where present.
- Keep the output customer-safe and easy to hand to a model owner.
```

## Follow-up prompts

- "Summarize only the naming and field-surface changes between baseline and canonical."
- "Rewrite the findings as a semantic-model release checklist that uses canonical names only."
- "Map each remediation item to a likely owner: modeler, BI developer, or reviewer."

## What work did Copilot eliminate?

The prompt turns a manual TMDL diff into a structured first draft of the inventory, issue log, and remediation plan.
