# Modeling MCP prompt

Use this prompt with the local Power BI Modeling MCP server on the Windows demo machine.

```text
Build or validate the CCHSHealth semantic model for the PBIP in:
semantic-models/CCHSHealth/CCHSHealth.pbip

First inspect the Modeling MCP server's available operations and the committed model definition. Do not guess operation names. Do not change report pages or visuals.

Data contract:
- datasets/public/cchs-annual/snapshot/observations.csv
- datasets/public/cchs-annual/snapshot/periods.csv
- datasets/public/cchs-annual/snapshot/geographies.csv
- datasets/public/cchs-annual/snapshot/age-groups.csv
- datasets/public/cchs-annual/snapshot/sexes.csv
- datasets/public/cchs-annual/snapshot/indicators.csv
- datasets/public/cchs-annual/snapshot/characteristics.csv
- datasets/public/cchs-annual/snapshot/quality-statuses.csv

Set the CCHS Data Root parameter to the absolute local path of that snapshot folder for this session. Do not persist a developer-specific absolute path back into source control.

Required tables:
- Health Observation
- Period
- Geography
- Age Group
- Sex
- Indicator
- Characteristic
- Quality Status

Required model behavior:
- Import mode for all tables.
- One published Statistics Canada cell per fact row.
- Seven one-to-many, single-direction relationships from dimensions to Health Observation.
- Hidden integer keys and hidden raw estimate.
- Explicit measures only; implicit measures discouraged.
- E estimates remain numeric with a caution label.
- F and x estimates remain blank and are never converted to zero.
- Percent values are percentage points such as 51.3, so use a literal-percent format string rather than multiplying by 100.
- No auto date/time tables.
- Business descriptions, source notes, display folders, and synonyms remain aligned with the committed TMDL.

Required measures:
- Health Estimate
- Percent Estimate
- Population Estimate
- British Columbia Estimate
- Canada Estimate
- BC vs Canada Difference
- Latest Reference Year
- British Columbia Province Rank
- Valid Province Count
- Use With Caution Count
- Suppressed Observation Count
- Observation Count
- Estimate Status Label
- HTML Spotlight Card

Validation:
1. Refresh all eight Import tables.
2. Execute each EVALUATE block in semantic-models/CCHSHealth/validation/model-validation.dax independently.
3. Confirm the row-count query returns 76032 fact rows, 8 periods, 11 geographies, 8 indicators, 6 characteristics, and 5 quality statuses.
4. Confirm the 2022 Perceived Health spot check returns BC 51.3, Canada excluding territories 55.3, and a -4.0 percentage-point difference for total age 12 years and over and both sexes.
5. Confirm E rows can have values and F/x rows have no nonblank estimate values.
6. Confirm ambiguous context returns a blank Health Estimate and a multiple-observations status.

Return:
- changes made, grouped by model object
- validation results
- any mismatch with the committed contract
- Windows-only steps that remain
- decisions that require model-owner approval

Fail instead of silently changing source scope, indicator labels, grain, units, quality handling, or relationship direction.
```
