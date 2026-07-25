# Extension exercises

## Suggested variations

1. Add an audit-table branch and regenerate the diagram.
2. Add a second report artifact and compare the downstream blast radius.
3. Ask Copilot to summarize only the lineage that feeds `gold.Sales`.
4. Extend the impact report with owner-based action items.

## Production-hardening ideas

- Validate the manifest in CI before accepting lineage changes.
- Generate a machine-readable impact export for release management.
- Add a regression check that searches the scenario for stale table or dimension names.

## Facilitator review checklist

- [ ] The learner can explain why deterministic lineage output builds trust.
- [ ] The learner can describe immediate versus indirect impact.
- [ ] The learner can separate engineering validation from analytics retesting.
- [ ] The learner can safely run the script without writing outside the scenario.

## What work did Copilot eliminate?

Copilot removed the repetitive reasoning needed to translate raw dependency data into a customer-ready blast-radius summary.
