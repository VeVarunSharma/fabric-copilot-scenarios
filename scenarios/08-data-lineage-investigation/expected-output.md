# Expected output

A strong Copilot response should align to the deterministic lineage artifacts in this scenario.

## Expected deliverables

- A plain-language lineage explanation from committed retail fixtures to the
  RetailSales report scaffold.
- A downstream impact summary for each documented change scenario.
- A validation checklist split between engineering and analytics concerns.
- References to the generated diagram and the expected impact report.

## Canonical artifacts

- [generated/lineage-diagram.md](generated/lineage-diagram.md)
- [artifacts/expected-impact-report.md](artifacts/expected-impact-report.md)

## Review checklist

- [ ] The response includes the single pipeline and all three notebook stages.
- [ ] Immediate and indirect impacts are distinguished.
- [ ] Gold lineage into the semantic model is limited to the committed four-table contract.
- [ ] The report dependency is shown as the committed RetailSales report
  scaffold without claiming completed data-bound visuals.

## Validation

Re-run [scripts/build_lineage.py](scripts/build_lineage.py) and compare the answer to the generated markdown artifacts.

## What work did Copilot eliminate?

Copilot eliminated the need to manually narrate every dependency edge before the team could discuss impact.
