# Sample prompt

```text
Create a customer-ready Power BI demonstration from the approved public Canadian Community Health Survey assets in this repository.

Read:
- scenarios/12-cchs-power-bi-authoring/README.md
- datasets/public/cchs-annual/README.md
- datasets/public/cchs-annual/snapshot/manifest.json
- scenarios/12-cchs-power-bi-authoring/artifacts/model-authoring-prompt.md
- scenarios/12-cchs-power-bi-authoring/artifacts/report-design-brief.md
- semantic-models/CCHSHealth/validation/model-validation.dax

Business outcome:
Show a BC Government data practitioner how Copilot can accelerate a deterministic public-data extract, an Import-mode semantic model, and an accessible three-page Power BI report while keeping provenance, quality handling, and interpretation decisions human-owned.

Requirements:
- Use Statistics Canada table 13-10-0096-01 only as an archived historical public source.
- Compare British Columbia with Canada (excluding territories) and the other provinces.
- Preserve the eight-file versioned star contract.
- Keep E estimates visible with caution; keep F and x estimates blank.
- Use a portable CCHS Data Root parameter and no committed absolute paths.
- Build model objects with the Power BI Modeling MCP server.
- Build PBIR pages and visuals with the Power BI Report Authoring skill.
- Use Desktop Bridge only to open or reload the PBIP, inspect status, and capture screenshots.
- Include a certified HTML Content (lite) showcase card and a native Power BI fallback card.
- Do not vendor a third-party pbiviz binary.
- Do not use BC Government branding or imply endorsement.
- Do not use customer, respondent-level, PHI, PII, confidential, or tenant-specific data.

Deliver:
1. the model build or inspection plan
2. the report build plan
3. validation evidence mapped to the acceptance criteria
4. explicit Windows-only steps
5. a fallback path using the committed completed PBIP
6. the work Copilot eliminated
7. the decisions and checks that remain practitioner-owned

Before changing files, identify any assumption that could alter source scope, quality handling, model grain, or the report comparison logic. Fail loudly on source or schema drift instead of silently dropping data.
```

## Focused follow-up prompts

- "Use the Modeling MCP prompt to inspect the committed TMDL and report any mismatch with the eight-file contract before refreshing."
- "Use the report design brief to validate page order, visual types, default slicer selections, source attribution, and the native custom-visual fallback."
- "Explain why the 2022 redesign warning prevents a simple year-over-year interpretation."
- "Map a proposed customer extract to the versioned contract without changing the semantic model or report."

## What work did Copilot eliminate?

The prompt removes the need to reconstruct the architecture, safety boundary, tool sequence, and acceptance criteria for each demo run.
