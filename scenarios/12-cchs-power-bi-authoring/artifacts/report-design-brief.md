# PBIR report design brief

Use this brief with the Power BI Report Authoring skill. Do not ask Desktop Bridge to create visuals.

## Canvas and style

- Canvas: 16:9, `1280 x 720`.
- Page order: `BC Overview`, `Trend and Demographics`, `Data Quality and Methodology`.
- Palette: neutral public-sector blue, teal, orange caution, dark text, and high-contrast white cards.
- Do not use BC Government logos, wordmarks, or a visual treatment that implies endorsement.
- Every data visual needs descriptive alt text and a visible title.
- Use text labels in addition to color for estimate quality.
- Avoid maps, Q&A visuals, external images, and external content in custom HTML.

## Page 1 - BC Overview

Header:

- Title: `Canadian Community Health Survey | British Columbia`.
- Banner: `HISTORICAL DEMONSTRATION | Public aggregate estimates, 2015-2022. The 2022 survey redesign creates a comparability break.`

Default dropdown slicers:

| Slicer | Field | Default |
| --- | --- | --- |
| Indicator | `Indicator[Indicator Name]` | `Perceived Health` |
| Age group | `Age Group[Age Group Name]` | `Total, 12 years and over` |
| Sex | `Sex[Sex Name]` | `Both sexes` |
| Reference year | `Period[Reference Year]` | `2022` |
| Published characteristic | `Characteristic[Characteristic Name]` | `Percent Estimate` |

Visuals:

- HTML Content (lite), visual type `htmlContent443BE3AD55E043BF878BED274D3A6865`, role `content`, bound to `Health Observation[HTML Spotlight Card]`.
- Native fallback card bound to `Health Observation[Percent Estimate]` and filtered to `Geography[Geography Name] = British Columbia`.
- Canada card bound to `Percent Estimate` and filtered to `Canada (excluding territories)`.
- Difference card bound to `BC vs Canada Difference`.
- Rank card bound to `British Columbia Province Rank`.
- Status card bound to `Estimate Status Label` and filtered to British Columbia.
- Province bar chart: category `Geography[Geography Name]`, value `Health Estimate`, filtered to `Geography[Geography Type] = Province`, sorted descending.
- Footer with the exact required Statistics Canada attribution.

The custom visual is a showcase, not a dependency. Do not package or commit a third-party `.pbiviz`.

## Page 2 - Trend and Demographics

Header warning:

`CAUTION | 2022 used a redesigned survey methodology. Treat the line break as a comparability boundary, not as evidence of a year-over-year change.`

Visuals:

- Indicator slicer synchronized with Page 1.
- Line chart: year category, geography series, `Percent Estimate` value; filter geography to British Columbia and Canada excluding territories, age to total 12 years and over, and sex to both sexes.
- Age bar chart: age-group category and `Percent Estimate`; filter to British Columbia, 2022, both sexes, and age-group type `Age band`.
- Sex bar chart: sex category and `Percent Estimate`; filter to British Columbia, 2022, total age 12 years and over, and females/males.
- Detail table: age group, sex, `Percent Estimate`, and `Quality Status[Status Label]`; use the same 2022 BC demographic scope.
- Interpretation note stating aggregate estimates, no causal interpretation, E caution, and blank F/x values.
- Footer with the exact required attribution.

## Page 3 - Data Quality and Methodology

Cards:

- `Use With Caution Count`
- `Suppressed Observation Count`
- `Latest Reference Year`
- `Observation Count`

Visuals:

- Quality-status bar chart: `Quality Status[Status Label]` by `Observation Count`.
- Definitions table: source status, status label, status description, and observation count.
- Methodology text: source table, 2015-2022 coverage, archived status, provinces and national comparator, aggregate grain, and 2022 redesign warning.
- Licence and attribution text with the Statistics Canada Open Licence URL and exact required attribution.
- Replacement-contract text describing the eight-file star contract and the decisions that remain practitioner-owned.

## Validation

- Validate the PBIR definition against the supported report, page, and visual-container schemas.
- Confirm all query references match the committed semantic-model object names.
- Confirm the custom visual uses role `content`.
- Confirm the native fallback is present.
- Confirm default slicer filters are serialized.
- Confirm no visual exceeds page bounds or shares a duplicate tab order.
- Confirm every data visual has alt text.
- Confirm the report contains the exact attribution and the 2022 redesign warning.
