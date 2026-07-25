# 12 CCHS Power BI authoring prompt pack

## Customer outcome

Create and validate a source-controlled Power BI project from attributed historical Canadian Community Health Survey public aggregates, with a stable replacement contract for a future customer extract.

## Best when the customer asks for

- Modeling MCP-assisted Power BI semantic-model authoring
- PBIR page and visual authoring from a reviewed design brief
- a public-data demonstration that can later accept an approved customer extract
- quality-aware survey reporting with explicit methodology and attribution
- a concrete explanation of what Copilot removes and what the practitioner still decides

## Copy-ready prompt

```text
You are helping me with repository scenario "12 CCHS Power BI authoring".

Read:
- scenarios/12-cchs-power-bi-authoring/README.md
- datasets/public/cchs-annual/README.md
- datasets/public/cchs-annual/snapshot/manifest.json
- scenarios/12-cchs-power-bi-authoring/artifacts/model-authoring-prompt.md
- scenarios/12-cchs-power-bi-authoring/artifacts/report-design-brief.md
- scenarios/12-cchs-power-bi-authoring/artifacts/live-demo-checklist.md
- semantic-models/CCHSHealth/validation/model-validation.dax

Business outcome:
Demonstrate how GitHub Copilot accelerates a deterministic public-data extract, an Import-mode Power BI star schema, and an accessible three-page report for a BC Government data practitioner.

Constraints:
- Treat Statistics Canada table 13-10-0096-01 as archived historical data covering 2015-2022.
- Compare British Columbia with Canada (excluding territories) and the other provinces.
- Preserve the 2022 redesign as a visible comparability break.
- Keep E estimates with caution and keep F/x estimates blank.
- Use only aggregate public data. Do not introduce customer, respondent-level, PHI, PII, confidential, secret, credential, or tenant-specific content.
- Use Modeling MCP for semantic-model work.
- Use the Report Authoring skill for PBIR pages and visuals.
- Use Desktop Bridge only for open, reload, status, and screenshots.
- Use the certified HTML Content (lite) visual as an optional showcase with a native card fallback.
- Do not vendor a third-party pbiviz or imply BC Government or Statistics Canada endorsement.
- Keep CCHS Data Root portable in source control.

Deliver:
1. source and contract checks
2. model build or inspection sequence
3. report build or inspection sequence
4. automated and DAX validation evidence
5. Windows Desktop and screenshot acceptance steps
6. fallback path using the committed completed PBIP
7. the work Copilot eliminated
8. the decisions that remain practitioner-owned

Fail loudly on source, schema, grain, unit, quality-status, or model-object drift. Separate repository evidence from assumptions.
```

## Human review required

- public-source approval, licence, and attribution
- survey concept definitions and 2022 comparability interpretation
- model grain, units, relationships, and measure logic
- accessibility, custom-visual approval, and screenshot review
- customer-extract privacy classification and contract mapping
- final Windows refresh and release acceptance

## Related guidance

- [Scenario walkthrough](../../scenarios/12-cchs-power-bi-authoring/README.md)
- [Facilitator runbook](../../docs/demo-runbooks/bc-cchs-power-bi.md)
- [Data safety](../../docs/governance/data-safety.md)
- [Artifact reference](../../docs/artifact-reference.md)
