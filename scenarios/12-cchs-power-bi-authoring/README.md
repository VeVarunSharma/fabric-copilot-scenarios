# Scenario 12 - CCHS Power BI authoring

Create and validate a source-controlled Power BI project from approved public Canadian Community Health Survey aggregates, then show how the same model and report can accept a future customer data-product extract.

## Business problem

A BC Government data practitioner wants to reduce the repetitive work involved in preparing survey extracts, building a semantic model, authoring report visuals, and documenting review decisions. The demo must remain useful without customer data, use an attributed public source, preserve Statistics Canada quality symbols, and avoid implying that the archived 2015-2022 table is current.

## Customer outcome

The completed demo provides:

- a deterministic, attributed public-data snapshot;
- an Import-mode star schema in PBIP/TMDL;
- a three-page PBIR report with native visuals and an optional HTML Content (lite) card;
- reusable Modeling MCP, report-authoring, and validation prompts;
- a versioned adapter contract for a later customer extract; and
- an explicit human review boundary for source approval, survey comparability, privacy, and business interpretation.

## Public source and limitations

- Source: Statistics Canada table `13-10-0096-01`, *Health characteristics, annual estimates, inactive*.
- Coverage: 2015-2022, `Canada (excluding territories)`, and the ten provinces.
- Product page: <https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1310009601>.
- Licence: <https://www.statcan.gc.ca/en/reference/licence>.
- This is an adapted historical demonstration, not current CCHS reporting.
- The 2022 survey redesign creates a comparability break. Do not make unsupported year-over-year claims across it.
- Only aggregate published estimates are used. No respondent-level data, PUMF, PHI, PII, or customer records are included.

Required attribution:

> Adapted from Statistics Canada, Health characteristics, annual estimates, inactive, 2015 to 2022. This does not constitute an endorsement by Statistics Canada of this product.

## Reference assets

- Completed project: [../../semantic-models/CCHSHealth/](../../semantic-models/CCHSHealth/)
- Public data contract: [../../datasets/public/cchs-annual/](../../datasets/public/cchs-annual/)
- Data preparation utility: [../../scripts/prepare_cchs_data.py](../../scripts/prepare_cchs_data.py)
- Model-authoring prompt: [artifacts/model-authoring-prompt.md](artifacts/model-authoring-prompt.md)
- Report design brief: [artifacts/report-design-brief.md](artifacts/report-design-brief.md)
- DAX validation queries: [artifacts/model-validation.dax](artifacts/model-validation.dax)
- Live-demo checklist: [artifacts/live-demo-checklist.md](artifacts/live-demo-checklist.md)
- Facilitator runbook: [../../docs/demo-runbooks/bc-cchs-power-bi.md](../../docs/demo-runbooks/bc-cchs-power-bi.md)

## Tool boundary

The demo deliberately assigns each tool one clear job:

| Tool | Job in the demo | Not its job |
| --- | --- | --- |
| Power BI Modeling MCP server | Set the data-root parameter; create or inspect model objects; refresh; execute DAX validation | Author page layouts or visuals |
| Power BI Report Authoring skill | Create and validate PBIR pages, visuals, bindings, filters, formatting, and accessibility metadata | Refresh the semantic model |
| Power BI Desktop Bridge | Open or reload the PBIP, report status, and capture screenshots for visual verification | Create report visuals |

If live tooling is unavailable, use the committed completed PBIP and the canonical validation assets instead of improvising a different architecture.

## Learning objectives

- Ground Copilot in an approved public-data contract with provenance, licence, attribution, and limitations.
- Build an Import-mode star schema with portable parameterized partitions.
- Preserve `E` estimates with caution labels and keep `F` and `x` estimates blank.
- Author a report that remains useful when the optional custom visual is unavailable.
- Separate deterministic checks from practitioner-owned interpretation and acceptance.
- Explain how a future customer extract replaces the public snapshot without redesigning the report.

## Manual baseline

Without the assisted workflow, a practitioner manually downloads and reshapes the source archive, creates dimensions and relationships, writes measures, wires every visual, repeats formatting, tests quality-symbol behavior, and assembles methodology and attribution text. They also have to keep model, report, prompts, and review evidence synchronized.

## Copilot-assisted workflow

1. Review the public source, licence, historical scope, and approved indicator list.
2. Regenerate or inspect the normalized eight-file snapshot and manifest.
3. Open a blank or copied PBIP work folder on Windows.
4. Use the Modeling MCP prompt to set `CCHS Data Root`, build or inspect the eight-table star schema, refresh, and execute the five DAX checks.
5. Use the Report Authoring brief to create `BC Overview`, `Trend and Demographics`, and `Data Quality and Methodology`.
6. Validate the PBIR definition before opening it in Desktop.
7. Use Desktop Bridge to open or reload the project and capture each page.
8. Compare the live result with the committed completed project.
9. Confirm the native fallback remains usable if HTML Content (lite) is not installed.

## Validation

Run the repository checks:

```bash
python3 -m pytest tests/test_cchs_data.py tests/test_cchs_model.py tests/test_cchs_report.py
python3 scripts/validate_repository.py
```

On Windows, also:

1. Install the certified HTML Content (lite) visual from AppSource if the showcase card is required.
2. Set `CCHS Data Root` to the clean-clone snapshot folder.
3. Refresh all eight Import tables.
4. Execute each block in [artifacts/model-validation.dax](artifacts/model-validation.dax) independently.
5. Run report-authoring validation.
6. Open or reload with Desktop Bridge and capture all three pages.
7. Confirm the default state shows British Columbia perceived health for 2022, total age 12 years and over, and both sexes.
8. Confirm there are no broken, empty, or overlapping visuals at the default state.

## Human review checklist

- [ ] Public source use, licence, attribution, and historical labeling are approved.
- [ ] The 2022 redesign warning is visible wherever trends are shown.
- [ ] Indicator, age, sex, geography, characteristic, and quality definitions match the source contract.
- [ ] `E`, `F`, and `x` behavior is correct and non-color labels remain visible.
- [ ] Measures do not aggregate incompatible published cells.
- [ ] No customer, confidential, PHI, PII, respondent-level, or tenant-specific data is present.
- [ ] The custom visual is certified and installed locally, or the native fallback is used.
- [ ] Screenshots and narration do not imply endorsement by Statistics Canada or BC Government.
- [ ] A clean clone can refresh after setting only the local data-root parameter.

## What work did Copilot eliminate?

Copilot eliminated first-draft transformation scaffolding, star-schema and measure boilerplate, repetitive PBIR visual wiring, accessibility text drafting, validation-query setup, and facilitator documentation. The practitioner still decides whether the source is appropriate, how survey concepts should be interpreted, whether years are comparable, how a customer extract maps to the contract, and whether the final model and report are acceptable for use.
