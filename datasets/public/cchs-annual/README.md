# Historical CCHS annual estimates

This directory contains a curated, aggregated public-data snapshot for the
BC-focused Power BI authoring demo. It does not contain respondent-level
microdata, personal information, or customer data.

## Source

- Statistics Canada table: `13-10-0096-01`
- Title: *Health characteristics, annual estimates, inactive*
- Coverage used here: 2015 through 2022
- Full-table CSV:
  <https://www150.statcan.gc.ca/n1/tbl/csv/13100096-eng.zip>
- Product page:
  <https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1310009601>
- Licence:
  <https://www.statcan.gc.ca/en/terms-conditions/open-licence>

The source table is archived and no longer updated. The 2022 CCHS redesign
limits comparison with earlier periods. The report therefore labels this as a
historical demonstration and does not imply current coverage.

## Attribution

> Adapted from Statistics Canada, Health characteristics, annual estimates,
> inactive, 2015 to 2022. This does not constitute an endorsement by
> Statistics Canada of this product.

## Snapshot contract

`selection.json` defines the approved years, geographies, indicators, and
characteristics. `snapshot/manifest.json` records source lineage, hashes, row
counts, the licence, and the contract version.

The normalized files form a stable star-schema boundary:

- `observations.csv`
- `periods.csv`
- `geographies.csv`
- `age-groups.csv`
- `sexes.csv`
- `indicators.csv`
- `characteristics.csv`
- `quality-statuses.csv`

A later customer data-product adapter can replace these files if it preserves
the documented schemas and semantics. Public and customer extracts must never
be mixed in the same committed snapshot.

## Refresh

Refresh from the official archive:

```bash
python3 scripts/prepare_cchs_data.py --snapshot-date 2026-07-24
```

Refresh from an already downloaded archive:

```bash
python3 scripts/prepare_cchs_data.py \
  --input-zip /path/to/13100096-eng.zip \
  --snapshot-date 2026-07-24
```

The utility fails when the source columns, selected labels, age groups, sex
members, or quality symbols drift. It keeps `E` estimates with a caution flag
and leaves `F`, `x`, and unavailable values blank rather than converting them
to zero.
