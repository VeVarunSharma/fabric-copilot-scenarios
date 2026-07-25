# Extension exercises

## Suggested variations

1. Replace the public snapshot with a mock customer extract that conforms to the same eight-file contract and prove that the model and report need no structural changes.
2. Add a tooltip page that explains the selected indicator definition, denominator, age scope, and quality status without introducing external web content.
3. Create a report variant that excludes 2022 from the trend and compare the resulting narration with the redesign-aware default.
4. Add confidence-interval visuals using the lower and upper published characteristics while preventing mixed-unit aggregation.
5. Add a second native fallback for the HTML spotlight and test the report with the custom visual removed.
6. Extend the adapter contract with a new geography hierarchy only after documenting how keys, grain, and privacy classification change.

## Production-hardening ideas

- Add a signed source approval record and licence review date to the manifest workflow.
- Run PBIR schema validation and the focused CCHS tests in continuous integration.
- Add screenshot baselines after final Windows acceptance and review them for tenant or customer identifiers.
- Add a source-to-contract reconciliation query for each customer extract load.
- Define release gates for survey methodology changes, revised indicator labels, and new quality symbols.
- Keep source credentials and customer files outside Git; pass approved locations at runtime.

## Facilitator review checklist

- [ ] The learner can explain why Modeling MCP, report authoring, and Desktop Bridge have different jobs.
- [ ] The learner can explain why a single published-cell grain prevents invalid aggregation.
- [ ] The learner can identify where `E`, `F`, and `x` are handled.
- [ ] The learner can explain why the 2022 line is a comparability boundary.
- [ ] The learner can describe how the native fallback protects the demo.
- [ ] The learner can list the decisions that remain human-owned when the customer extract arrives.

## What work did Copilot eliminate?

Copilot makes alternative report and contract designs cheap to draft and compare. It does not approve a public source, decide privacy classification, validate survey methodology, or accept production reporting on behalf of the practitioner.
