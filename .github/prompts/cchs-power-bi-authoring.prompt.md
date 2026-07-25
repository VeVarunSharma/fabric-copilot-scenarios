---
description: Build or review the historical CCHS Power BI demo using the approved public-data contract and explicit tool boundaries.
mode: edit
tools:
  - codebase
---

Read:

- `scenarios/12-cchs-power-bi-authoring/README.md`
- `scenarios/12-cchs-power-bi-authoring/artifacts/model-authoring-prompt.md`
- `scenarios/12-cchs-power-bi-authoring/artifacts/report-design-brief.md`
- `datasets/public/cchs-annual/snapshot/manifest.json`
- `semantic-models/CCHSHealth/`

Create or review the CCHSHealth PBIP as an archived 2015-2022 public-data demonstration.

Requirements:

- preserve the eight-file star contract and portable `CCHS Data Root` parameter;
- use Modeling MCP for tables, relationships, measures, refresh, and DAX validation;
- use report authoring for PBIR pages, visuals, filters, formatting, and alt text;
- use Desktop Bridge only for open, reload, status, and screenshots;
- keep `E` values with caution and keep `F`/`x` values blank;
- show the 2022 redesign comparability warning;
- include exact Statistics Canada attribution;
- include HTML Content (lite) only as an optional showcase with a native fallback;
- do not add customer data, secrets, tenant IDs, official BC Government branding, or a third-party `.pbiviz` binary.

Run the focused CCHS tests and summarize:

1. changed artifacts;
2. validation evidence;
3. Windows-only acceptance still required;
4. work Copilot eliminated; and
5. practitioner-owned decisions.
