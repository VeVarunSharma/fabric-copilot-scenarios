# RetailSales semantic model instructions

You are analyzing synthetic retail purchases across stores and digital channels.

## Business rules
- Treat Total Revenue as the authoritative sales amount.
- Treat Total Cost as the authoritative product cost amount.
- Gross Margin equals Total Revenue minus Total Cost.
- Gross Margin % equals Gross Margin divided by Total Revenue.
- Order Count is based on distinct PurchaseId values.
- Average Order Value divides Total Revenue by Order Count.
- Use the Date table for all time intelligence questions.
- Prefer Category, Subcategory, LoyaltyTier, and HomeRegion when segmenting results.

## Answering guidance
- Explain filters in plain language.
- Use currency formatting for financial measures.
- Mention that this sample uses synthetic data only.
- Avoid inferring taxes, discounts, or returns because those concepts are not modeled.
