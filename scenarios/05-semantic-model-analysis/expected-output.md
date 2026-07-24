# Expected output

A strong Copilot response should stay anchored to the committed RetailSales artifacts.

## Expected response elements

1. **Table inventory** for `Date`, `Customer`, `Product`, and `Sales` only.
2. **Relationship review** that identifies baseline bidirectional filtering and canonical single-direction filtering.
3. **Naming review** that distinguishes baseline technical names from finalized canonical names factually.
4. **Measure review** focused on the `Sales` table, including baseline `Revenue` and `MarginPct` versus the committed canonical measure surface.
5. **Metadata review** covering hidden keys and user-facing business attributes that actually exist.
6. **Prioritized remediation plan** mapped to the exact baseline gaps.

## Canonical artifact

Use [artifacts/analysis-findings.md](artifacts/analysis-findings.md) as the benchmark.

## Review checklist

- [ ] Only real table names from the semantic model are used.
- [ ] Baseline terms remain clearly labeled as baseline-only.
- [ ] Baseline `Customer` references use `LoyaltyTier`.
- [ ] Baseline `Product` references use `Category`.
- [ ] Baseline `Sales` references use `PurchaseId`.
- [ ] Canonical `Customer` references use `Customer ID`, `Loyalty Tier`, `Home Region`, `Signup Date`, and `Email Domain`.
- [ ] Canonical `Product` references use `Product ID`, `Category`, `Subcategory`, `Unit Price`, `Unit Cost`, and `Is Active`.
- [ ] Direct Lake source references use `gold.Date`, `gold.Customer`, `gold.Product`, and `gold.Sales`.

## Validation

Compare the response against the approved findings benchmark and the committed TMDL files before accepting the analysis.

## What work did Copilot eliminate?

Copilot eliminated the repetitive discovery pass and produced a reviewable issue log instead of forcing the reviewer to start from a blank page.
