# Extension exercises

## Suggested variations

1. Ask Copilot to summarize only the `Customer` naming changes from baseline `LoyaltyTier` to canonical `Loyalty Tier` plus the added canonical customer attributes.
2. Request a focused review of how baseline `PurchaseId` becomes canonical `Order ID` in `Sales`.
3. Ask Copilot to draft release notes for the canonical `Product` expansion from `Category` to `Category`, `Subcategory`, `Unit Price`, `Unit Cost`, and `Is Active`.
4. Produce a release checklist that isolates relationship, hidden-key, and naming issues.

## Production-hardening ideas

- Add a review gate that rejects exposed surrogate keys in customer-facing tables.
- Validate that every visible measure on `Sales` includes approved naming and descriptions.
- Extend the review to check Copilot schema metadata whenever the semantic model changes.

## Facilitator review checklist

- [ ] The learner can name the four committed semantic-model tables.
- [ ] The learner can explain the difference between baseline `LoyaltyTier` and canonical `Loyalty Tier`.
- [ ] The learner can explain why baseline `PurchaseId` maps to canonical `Order ID`.
- [ ] The learner can identify which canonical columns should stay hidden, including `Date Key`, `Customer Key`, `Product Key`, and `Sales Key`.

## What work did Copilot eliminate?

Copilot removed the need to handcraft a semantic-model review from scratch and accelerated the comparison of baseline and canonical TMDL artifacts.
