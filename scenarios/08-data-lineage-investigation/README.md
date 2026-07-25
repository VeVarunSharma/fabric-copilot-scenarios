# Scenario 08 - Data lineage investigation

Investigate downstream impact across the committed retail-purchases Fabric flow.

## Business problem

A Fabric team needs a repeatable way to explain how committed retail-purchases
source files flow through the `retail-medallion.DataPipeline`, the three
notebooks, the Bronze and Silver layers, the Gold Direct Lake tables, the
RetailSales semantic model, and the source-controlled RetailSales report
scaffold. They want Copilot to help with the narrative, but they also need
deterministic local outputs they can regenerate.

## Scenario assets

- Lineage manifest: [artifacts/lineage-manifest.json](artifacts/lineage-manifest.json)
- Generated lineage diagram: [generated/lineage-diagram.md](generated/lineage-diagram.md)
- Expected downstream impact report: [artifacts/expected-impact-report.md](artifacts/expected-impact-report.md)
- Local builder script: [scripts/build_lineage.py](scripts/build_lineage.py)

## Learning objectives

- Represent real repository lineage in a small, reviewable manifest.
- Generate deterministic Mermaid output for customer conversations.
- Trace committed retail sources through the pipeline, notebooks, tables,
  semantic model, and report scaffold.
- Keep a safe local CLI that reads JSON and writes Markdown only inside the scenario directory.
- Use Copilot for reasoning while preserving reproducible outputs.

## Manual baseline

Without Copilot or a helper script, engineers must trace dependencies across
source files, notebooks, Gold tables, the semantic model, and the report
scaffold by hand.

## Copilot-assisted workflow

1. Ground Copilot with the lineage manifest.
2. Ask for a downstream impact summary for a specific change target.
3. Run the local script to regenerate the approved Mermaid diagram and impact report.
4. Review the generated blast-radius summary with engineering and analytics owners before approving a change.

## Validation steps

1. Run `python3 scripts/build_lineage.py` from this scenario directory.
2. Confirm the regenerated diagram includes `purchases.csv`, `customers.csv`,
   `products.csv`, the pipeline, the three notebooks, actual Bronze and Silver
   tables, the Gold tables, the RetailSales semantic model, and the RetailSales
   report scaffold.
3. Confirm the impact report distinguishes immediate downstream assets from the broader dependency chain.
4. Confirm the script refuses output paths that escape the scenario directory.

## Human review checklist

- [ ] The manifest reflects the committed retail-purchases artifacts.
- [ ] The diagram shows the single pipeline and the three notebook stages.
- [ ] Gold lineage into the semantic model is limited to `gold.Date`, `gold.Customer`, `gold.Product`, and `gold.Sales`.
- [ ] The report node is explicitly identified as the committed RetailSales
  report scaffold, not a completed data-bound report.
- [ ] The CLI remains deterministic and customer-safe.

## What work did Copilot eliminate?

Copilot eliminated much of the manual dependency reasoning and made it easier to explain blast radius before implementation begins.
