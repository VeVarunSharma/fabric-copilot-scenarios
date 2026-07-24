# Expected output

A high-quality result is a working, source-controlled PBIP plus review evidence, not only a narrative or a set of disconnected DAX snippets.

## Expected artifact matrix

| Layer | Expected output | Acceptance signal |
| --- | --- | --- |
| Public data | Deterministic eight-file star snapshot, manifest, schemas, and refresh utility | Offline fixture transforms reproducibly; source drift fails loudly |
| Semantic model | Eight Import tables, seven single-direction relationships, hidden keys, explicit measures, parameterized partitions | Model tests pass; no developer-specific absolute path is committed |
| BC Overview | Historical banner, five defaulted slicers, HTML spotlight, native fallback, KPI cards, province comparison | Default state is BC perceived health, 2022, total age 12+, both sexes, percent estimate |
| Trend and Demographics | BC vs Canada trend, visible 2022 redesign warning, age and sex comparisons, detailed status table | No causal wording; suppressed values remain blank |
| Data Quality and Methodology | Quality counts, status distribution, definitions, source, licence, attribution, scope, and replacement contract | `E`, `F`, and `x` handling is explicit and non-color labels are present |
| Validation | Data, model, report, DAX, Desktop, and clean-clone checks | Automated checks pass and Windows screenshots show no broken visuals |

## Expected default comparison

For `Perceived Health`, reference year `2022`, `Total, 12 years and over`, `Both sexes`, and `Percent Estimate`:

| Metric | Expected value |
| --- | ---: |
| British Columbia | 51.3% |
| Canada (excluding territories) | 55.3% |
| BC minus Canada | -4.0 percentage points |

These values are a deterministic spot check for the committed historical snapshot, not a current CCHS statement.

## Expected model behavior

- `Health Estimate` returns a value only when the current context resolves to one published fact cell.
- `Percent Estimate` and `Population Estimate` select the matching primary characteristic.
- `British Columbia Estimate` and `Canada Estimate` use explicit geography flags.
- Province rank excludes the Canada aggregate and ignores unusable estimates.
- `E` rows can retain numeric estimates.
- `F` and `x` rows have blank estimates.
- `HTML Spotlight Card` contains inline sanitized markup and no scripts, iframes, or external content.

## Expected report behavior

- Page order is `BC Overview`, `Trend and Demographics`, and `Data Quality and Methodology`.
- The custom visual uses HTML Content (lite) role `content`.
- A native card renders the same selected BC percentage when the custom visual is unavailable.
- Visuals include descriptive alt text.
- The exact Statistics Canada adapted-product attribution appears in the report.
- Neutral styling is used; no official BC Government visual identity is implied.

## Review checklist

- [ ] The public source, archive status, licence, and attribution are explicit.
- [ ] The 2022 redesign warning is visible on trend surfaces.
- [ ] Data, model, and report tests pass.
- [ ] DAX validation blocks return the expected shape and spot-check values.
- [ ] The custom visual dependency is optional and documented.
- [ ] The completed PBIP remains the live-demo fallback.
- [ ] Windows refresh and Desktop Bridge screenshots are retained as acceptance evidence.

## What work did Copilot eliminate?

Copilot produced a coherent, testable first draft across data, model, report, validation, and documentation so the reviewer can focus on source fitness, semantic correctness, visual interpretation, and release approval.
