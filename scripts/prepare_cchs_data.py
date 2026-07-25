#!/usr/bin/env python3
"""Prepare a deterministic, attributed CCHS aggregate snapshot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from collections.abc import Iterable, Iterator
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "datasets/public/cchs-annual/selection.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "datasets/public/cchs-annual/snapshot"

EXPECTED_SOURCE_COLUMNS = (
    "REF_DATE",
    "GEO",
    "DGUID",
    "Age group",
    "Sex",
    "Indicators",
    "Characteristics",
    "UOM",
    "UOM_ID",
    "SCALAR_FACTOR",
    "SCALAR_ID",
    "VECTOR",
    "COORDINATE",
    "VALUE",
    "STATUS",
    "SYMBOL",
    "TERMINATED",
    "DECIMALS",
)

OUTPUT_COLUMNS = {
    "observations.csv": (
        "period_key",
        "geography_key",
        "age_group_key",
        "sex_key",
        "indicator_key",
        "characteristic_key",
        "quality_status_key",
        "value",
    ),
    "periods.csv": (
        "period_key",
        "reference_year",
        "period_start_date",
        "survey_era",
        "comparability_note",
        "is_latest",
    ),
    "geographies.csv": (
        "geography_key",
        "geography_name",
        "geography_code",
        "dguid",
        "geography_type",
        "is_british_columbia",
        "is_canada_comparator",
        "sort_order",
    ),
    "age-groups.csv": (
        "age_group_key",
        "age_group_name",
        "age_group_type",
        "sort_order",
    ),
    "sexes.csv": (
        "sex_key",
        "sex_name",
        "sort_order",
    ),
    "indicators.csv": (
        "indicator_key",
        "indicator_name",
        "source_indicator_name",
        "topic",
        "age_scope",
        "sort_order",
    ),
    "characteristics.csv": (
        "characteristic_key",
        "characteristic_name",
        "source_characteristic_name",
        "measure_family",
        "statistic_type",
        "unit",
        "decimals",
        "is_primary_estimate",
        "sort_order",
    ),
    "quality-statuses.csv": (
        "quality_status_key",
        "source_status",
        "status_label",
        "status_description",
        "is_usable",
        "is_caution",
        "is_suppressed",
        "sort_order",
    ),
}

AGE_GROUP_ORDER = {
    "Total, 12 years and over": (1, "Total"),
    "Total, 18 years and over": (2, "Total"),
    "12 to 17 years": (3, "Age band"),
    "18 to 34 years": (4, "Age band"),
    "35 to 49 years": (5, "Age band"),
    "50 to 64 years": (6, "Age band"),
    "65 years and over": (7, "Age band"),
}

SEX_ORDER = {
    "Both sexes": 1,
    "Females": 2,
    "Males": 3,
}

QUALITY_STATUSES = {
    "": {
        "status_label": "Publishable",
        "status_description": "No Statistics Canada quality symbol is attached.",
        "is_usable": True,
        "is_caution": False,
        "is_suppressed": False,
        "sort_order": 1,
    },
    "E": {
        "status_label": "Use with caution",
        "status_description": "Statistics Canada marks the estimate as use with caution.",
        "is_usable": True,
        "is_caution": True,
        "is_suppressed": False,
        "sort_order": 2,
    },
    "F": {
        "status_label": "Too unreliable to publish",
        "status_description": "Statistics Canada considers the estimate too unreliable to publish.",
        "is_usable": False,
        "is_caution": False,
        "is_suppressed": True,
        "sort_order": 3,
    },
    "x": {
        "status_label": "Suppressed",
        "status_description": "Statistics Canada suppresses the estimate for confidentiality.",
        "is_usable": False,
        "is_caution": False,
        "is_suppressed": True,
        "sort_order": 4,
    },
    "..": {
        "status_label": "Not available",
        "status_description": "The estimate is not available for this reference period.",
        "is_usable": False,
        "is_caution": False,
        "is_suppressed": False,
        "sort_order": 5,
    },
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Prepare a deterministic CCHS aggregate snapshot."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--input-zip",
        type=Path,
        help="Existing Statistics Canada full-table ZIP archive.",
    )
    source.add_argument(
        "--input-csv",
        type=Path,
        help="Existing extracted source CSV, primarily for offline tests.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Selection and contract configuration JSON.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for normalized CSV files and manifest.json.",
    )
    parser.add_argument(
        "--snapshot-date",
        default=date.today().isoformat(),
        help="UTC access date recorded in the manifest (YYYY-MM-DD).",
    )
    return parser.parse_args(argv)


def load_config(path: Path) -> dict[str, Any]:
    """Load and validate the selection configuration."""
    config = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "contractVersion",
        "source",
        "referenceYears",
        "geographies",
        "indicators",
        "characteristics",
    }
    missing = required.difference(config)
    if missing:
        raise ValueError(f"Selection config is missing: {sorted(missing)}")

    for collection_name, name_field in (
        ("geographies", "sourceName"),
        ("indicators", "sourceName"),
        ("characteristics", "sourceName"),
    ):
        names = [item[name_field] for item in config[collection_name]]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate {collection_name} source names in config")

    years = config["referenceYears"]
    if years != sorted(set(years)):
        raise ValueError("referenceYears must be unique and sorted")
    return config


def sha256_path(path: Path) -> str:
    """Return a file's SHA-256 digest."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bool_text(value: bool) -> str:
    """Return a stable CSV boolean representation."""
    return "true" if value else "false"


def validate_source_columns(fieldnames: list[str] | None) -> None:
    """Fail when the Statistics Canada source contract changes."""
    actual = tuple(fieldnames or ())
    if actual != EXPECTED_SOURCE_COLUMNS:
        raise ValueError(
            "Unexpected source columns. "
            f"Expected {EXPECTED_SOURCE_COLUMNS}; received {actual}"
        )


def iter_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    """Yield source rows from an extracted CSV."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        validate_source_columns(reader.fieldnames)
        yield from reader


def iter_zip_rows(path: Path) -> Iterator[dict[str, str]]:
    """Yield source rows from a Statistics Canada full-table ZIP."""
    with zipfile.ZipFile(path) as archive:
        candidates = sorted(
            name
            for name in archive.namelist()
            if name.endswith(".csv") and "_MetaData" not in name
        )
        if len(candidates) != 1:
            raise ValueError(
                f"Expected one source CSV in {path.name}; found {candidates}"
            )
        with archive.open(candidates[0]) as raw:
            with io.TextIOWrapper(raw, encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                validate_source_columns(reader.fieldnames)
                yield from reader


def download_source(url: str, target: Path) -> None:
    """Download the official source archive."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "fabric-copilot-scenarios-cchs-demo/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        if response.status != 200:
            raise ValueError(f"Source download returned HTTP {response.status}")
        target.write_bytes(response.read())


def normalized_value(row: dict[str, str]) -> str:
    """Preserve usable estimates and keep unavailable cells blank."""
    status = row["STATUS"]
    raw_value = row["VALUE"].strip()
    if status not in QUALITY_STATUSES:
        raise ValueError(f"Unmapped Statistics Canada status: {status!r}")
    if not QUALITY_STATUSES[status]["is_usable"] or not raw_value:
        return ""
    try:
        Decimal(raw_value)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid numeric value: {raw_value!r}") from exc
    return raw_value


def write_csv(path: Path, columns: tuple[str, ...], rows: Iterable[dict[str, Any]]) -> int:
    """Write a deterministic UTF-8 CSV and return its row count."""
    count = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(columns),
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def build_snapshot(
    rows: Iterable[dict[str, str]],
    config: dict[str, Any],
    output_dir: Path,
    source_sha256: str,
    snapshot_date: str,
) -> dict[str, Any]:
    """Filter the source cube and write the normalized star contract."""
    years = {str(year) for year in config["referenceYears"]}
    geography_config = {
        item["sourceName"]: item for item in config["geographies"]
    }
    indicator_config = {
        item["sourceName"]: item for item in config["indicators"]
    }
    characteristic_config = {
        item["sourceName"]: item for item in config["characteristics"]
    }

    selected_rows: list[dict[str, str]] = []
    observed_years: set[str] = set()
    observed_geographies: set[str] = set()
    observed_indicators: set[str] = set()
    observed_characteristics: set[str] = set()
    observed_age_groups: set[str] = set()
    observed_sexes: set[str] = set()
    observed_statuses: set[str] = set()
    geography_dguids: dict[str, set[str]] = {}

    for row in rows:
        if (
            row["REF_DATE"] not in years
            or row["GEO"] not in geography_config
            or row["Indicators"] not in indicator_config
            or row["Characteristics"] not in characteristic_config
        ):
            continue

        age_group = row["Age group"]
        sex = row["Sex"]
        status = row["STATUS"]
        if age_group not in AGE_GROUP_ORDER:
            raise ValueError(f"Unmapped age group: {age_group!r}")
        if sex not in SEX_ORDER:
            raise ValueError(f"Unmapped sex: {sex!r}")
        if status not in QUALITY_STATUSES:
            raise ValueError(f"Unmapped Statistics Canada status: {status!r}")

        selected_rows.append(
            {
                "year": row["REF_DATE"],
                "geography": row["GEO"],
                "age_group": age_group,
                "sex": sex,
                "indicator": row["Indicators"],
                "characteristic": row["Characteristics"],
                "status": status,
                "value": normalized_value(row),
            }
        )
        observed_years.add(row["REF_DATE"])
        observed_geographies.add(row["GEO"])
        observed_indicators.add(row["Indicators"])
        observed_characteristics.add(row["Characteristics"])
        observed_age_groups.add(age_group)
        observed_sexes.add(sex)
        observed_statuses.add(status)
        geography_dguids.setdefault(row["GEO"], set()).add(row["DGUID"])

    expected_sets = {
        "reference years": years,
        "geographies": set(geography_config),
        "indicators": set(indicator_config),
        "characteristics": set(characteristic_config),
    }
    observed_sets = {
        "reference years": observed_years,
        "geographies": observed_geographies,
        "indicators": observed_indicators,
        "characteristics": observed_characteristics,
    }
    for label, expected in expected_sets.items():
        observed = observed_sets[label]
        if observed != expected:
            raise ValueError(
                f"Source drift for {label}: missing={sorted(expected - observed)}, "
                f"unexpected={sorted(observed - expected)}"
            )
    if not selected_rows:
        raise ValueError("Selection produced no observations")

    output_dir.mkdir(parents=True, exist_ok=True)
    latest_year = max(config["referenceYears"])

    period_rows = [
        {
            "period_key": year,
            "reference_year": year,
            "period_start_date": f"{year}-01-01",
            "survey_era": "2022 redesign" if year == 2022 else "2015 redesign",
            "comparability_note": (
                "The 2022 CCHS redesign limits comparison with earlier periods."
                if year == 2022
                else "Part of the 2015-designed CCHS series."
            ),
            "is_latest": bool_text(year == latest_year),
        }
        for year in config["referenceYears"]
    ]

    geography_keys: dict[str, int] = {}
    geography_rows = []
    for key, item in enumerate(config["geographies"], start=1):
        source_name = item["sourceName"]
        dguids = geography_dguids[source_name]
        if len(dguids) != 1:
            raise ValueError(f"Multiple DGUID values for {source_name}: {sorted(dguids)}")
        geography_keys[source_name] = key
        geography_rows.append(
            {
                "geography_key": key,
                "geography_name": source_name,
                "geography_code": item["code"],
                "dguid": next(iter(dguids)),
                "geography_type": item["type"],
                "is_british_columbia": bool_text(item["code"] == "BC"),
                "is_canada_comparator": bool_text(item["code"] == "CANX"),
                "sort_order": item["sortOrder"],
            }
        )

    age_group_keys: dict[str, int] = {}
    age_group_rows = []
    for key, source_name in enumerate(
        sorted(observed_age_groups, key=lambda value: AGE_GROUP_ORDER[value][0]),
        start=1,
    ):
        age_group_keys[source_name] = key
        age_group_rows.append(
            {
                "age_group_key": key,
                "age_group_name": source_name,
                "age_group_type": AGE_GROUP_ORDER[source_name][1],
                "sort_order": AGE_GROUP_ORDER[source_name][0],
            }
        )

    sex_keys: dict[str, int] = {}
    sex_rows = []
    for key, source_name in enumerate(
        sorted(observed_sexes, key=lambda value: SEX_ORDER[value]), start=1
    ):
        sex_keys[source_name] = key
        sex_rows.append(
            {
                "sex_key": key,
                "sex_name": source_name,
                "sort_order": SEX_ORDER[source_name],
            }
        )

    indicator_keys: dict[str, int] = {}
    indicator_rows = []
    for key, item in enumerate(config["indicators"], start=1):
        indicator_keys[item["sourceName"]] = key
        indicator_rows.append(
            {
                "indicator_key": key,
                "indicator_name": item["name"],
                "source_indicator_name": item["sourceName"],
                "topic": item["topic"],
                "age_scope": item["ageScope"],
                "sort_order": item["sortOrder"],
            }
        )

    characteristic_keys: dict[str, int] = {}
    characteristic_rows = []
    for key, item in enumerate(config["characteristics"], start=1):
        characteristic_keys[item["sourceName"]] = key
        characteristic_rows.append(
            {
                "characteristic_key": key,
                "characteristic_name": item["name"],
                "source_characteristic_name": item["sourceName"],
                "measure_family": item["measureFamily"],
                "statistic_type": item["statisticType"],
                "unit": item["unit"],
                "decimals": item["decimals"],
                "is_primary_estimate": bool_text(item["statisticType"] == "Estimate"),
                "sort_order": item["sortOrder"],
            }
        )

    status_order = sorted(
        observed_statuses, key=lambda value: QUALITY_STATUSES[value]["sort_order"]
    )
    quality_status_keys = {
        source_status: key for key, source_status in enumerate(status_order, start=1)
    }
    quality_status_rows = []
    for source_status in status_order:
        policy = QUALITY_STATUSES[source_status]
        quality_status_rows.append(
            {
                "quality_status_key": quality_status_keys[source_status],
                "source_status": source_status,
                "status_label": policy["status_label"],
                "status_description": policy["status_description"],
                "is_usable": bool_text(policy["is_usable"]),
                "is_caution": bool_text(policy["is_caution"]),
                "is_suppressed": bool_text(policy["is_suppressed"]),
                "sort_order": policy["sort_order"],
            }
        )

    observation_rows = []
    grains: set[tuple[int, ...]] = set()
    for row in selected_rows:
        grain = (
            int(row["year"]),
            geography_keys[row["geography"]],
            age_group_keys[row["age_group"]],
            sex_keys[row["sex"]],
            indicator_keys[row["indicator"]],
            characteristic_keys[row["characteristic"]],
        )
        if grain in grains:
            raise ValueError(f"Duplicate observation grain: {grain}")
        grains.add(grain)
        observation_rows.append(
            {
                "period_key": grain[0],
                "geography_key": grain[1],
                "age_group_key": grain[2],
                "sex_key": grain[3],
                "indicator_key": grain[4],
                "characteristic_key": grain[5],
                "quality_status_key": quality_status_keys[row["status"]],
                "value": row["value"],
            }
        )
    observation_rows.sort(
        key=lambda row: tuple(
            int(row[column])
            for column in (
                "period_key",
                "geography_key",
                "age_group_key",
                "sex_key",
                "indicator_key",
                "characteristic_key",
            )
        )
    )

    output_rows = {
        "observations.csv": observation_rows,
        "periods.csv": period_rows,
        "geographies.csv": geography_rows,
        "age-groups.csv": age_group_rows,
        "sexes.csv": sex_rows,
        "indicators.csv": indicator_rows,
        "characteristics.csv": characteristic_rows,
        "quality-statuses.csv": quality_status_rows,
    }

    file_details = {}
    for filename, file_rows in output_rows.items():
        path = output_dir / filename
        row_count = write_csv(path, OUTPUT_COLUMNS[filename], file_rows)
        file_details[filename] = {
            "rows": row_count,
            "sha256": sha256_path(path),
        }

    attribution = (
        "Adapted from Statistics Canada, Health characteristics, annual estimates, "
        "inactive, 2015 to 2022. This does not constitute an endorsement by "
        "Statistics Canada of this product."
    )
    manifest = {
        "contractVersion": config["contractVersion"],
        "snapshotDate": snapshot_date,
        "source": {
            "productId": config["source"]["productId"],
            "downloadRoot": config["source"]["downloadRoot"],
            "title": config["source"]["title"],
            "archived": True,
            "downloadUrl": config["source"]["downloadUrl"],
            "productUrl": config["source"]["productUrl"],
            "sha256": source_sha256,
            "referenceYears": config["referenceYears"],
        },
        "selection": {
            "geographies": [item["sourceName"] for item in config["geographies"]],
            "indicators": [item["sourceName"] for item in config["indicators"]],
            "characteristics": [
                item["sourceName"] for item in config["characteristics"]
            ],
        },
        "files": file_details,
        "licenceUrl": config["source"]["licenceUrl"],
        "attribution": attribution,
        "notes": [
            "This is an aggregated public-data snapshot, not respondent-level microdata.",
            "The 2022 survey redesign limits comparison with earlier periods.",
            "Suppressed and unavailable observations remain blank and are never zero-filled.",
        ],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    """Prepare the configured CCHS snapshot."""
    args = parse_args(argv)
    config = load_config(args.config.resolve())
    output_dir = args.output_dir.resolve()

    try:
        date.fromisoformat(args.snapshot_date)
        with tempfile.TemporaryDirectory(prefix="cchs-source-") as temp_dir:
            if args.input_csv:
                source_path = args.input_csv.resolve()
                source_sha256 = sha256_path(source_path)
                rows = iter_csv_rows(source_path)
            else:
                if args.input_zip:
                    source_path = args.input_zip.resolve()
                else:
                    source_path = Path(temp_dir) / "source.zip"
                    download_source(config["source"]["downloadUrl"], source_path)
                source_sha256 = sha256_path(source_path)
                rows = iter_zip_rows(source_path)

            manifest = build_snapshot(
                rows=rows,
                config=config,
                output_dir=output_dir,
                source_sha256=source_sha256,
                snapshot_date=args.snapshot_date,
            )
    except (
        OSError,
        ValueError,
        zipfile.BadZipFile,
        urllib.error.URLError,
        json.JSONDecodeError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Prepared {manifest['files']['observations.csv']['rows']} observations "
        f"under {output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
