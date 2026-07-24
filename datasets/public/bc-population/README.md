# BC regional-district population

This directory pins the unmodified Regional District CSV from the BC
Sub-Provincial Population Estimates and Projections catalogue record. It is
reviewed public aggregate data: it contains no customer, tenant, person-level,
PII, PHI, credential, or confidential content.

## Source and licence

- Catalogue:
  <https://catalogue.data.gov.bc.ca/dataset/bc-sub-provincial-population-estimates-and-projections>
- CKAN package ID: `86839277-986a-4a29-9f70-fa9b1166f6cb`
- Resource ID: `36610a52-6f90-4ed6-946d-587641a490df`
- Resource:
  <https://catalogue.data.gov.bc.ca/dataset/86839277-986a-4a29-9f70-fa9b1166f6cb/resource/36610a52-6f90-4ed6-946d-587641a490df/download/regional-district-population.csv>
- Licence: [Open Government Licence - British Columbia](https://www2.gov.bc.ca/gov/content?id=A519A56BC2BF44E4A008B33FCF527F61)

**Contains information licensed under the Open Government Licence – British Columbia.**

`provenance.json` records the retrieval time, live CKAN metadata, source
contract, byte size, and SHA-256. `SHA256SUMS` pins the exact committed bytes.
The CSV is the source file as downloaded and is not transformed.

## Contract and downstream scope

The source has 4,230 rows, 30 region codes, 76 years, three genders, and 91
single-year age fields (`0` through `89`, plus `90+`). The current snapshot
classifies 1971-2025 as estimates and 2026-2046 as projections. Nonzero regional
districts cover every year from 2001 through 2046.

The documented downstream processing excludes province-wide region `0` and
total gender `T`. That retains 2,668 wide rows and produces 242,788 age-level
rows. The refresh validation requires every row's age fields to sum to `Total`
and every `T` value to equal `F + M`.

## Check and refresh

Check for upstream metadata or content drift without changing the snapshot:

```bash
python3 scripts/data/refresh_bc_population.py check
```

After reviewing the catalogue, licence, and expected contract changes, refresh
all governed files:

```bash
python3 scripts/data/refresh_bc_population.py refresh
```

Review the CSV, provenance, checksum, and documentation diff before merge.
