#!/usr/bin/env python3
"""Validate and refresh the governed BC regional-district population snapshot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Callable

PACKAGE_ID = "86839277-986a-4a29-9f70-fa9b1166f6cb"
RESOURCE_ID = "36610a52-6f90-4ed6-946d-587641a490df"
CATALOGUE_URL = (
    "https://catalogue.data.gov.bc.ca/dataset/"
    "bc-sub-provincial-population-estimates-and-projections"
)
PACKAGE_URL = "https://catalogue.data.gov.bc.ca/dataset/" + PACKAGE_ID
RESOURCE_URL = PACKAGE_URL + "/resource/" + RESOURCE_ID
PACKAGE_SHOW_URL = (
    "https://catalogue.data.gov.bc.ca/api/3/action/package_show?id=" + PACKAGE_ID
)
DOWNLOAD_URL = (
    "https://catalogue.data.gov.bc.ca/dataset/"
    f"{PACKAGE_ID}/resource/{RESOURCE_ID}/download/"
    "regional-district-population.csv"
)
ATTRIBUTION = (
    "Contains information licensed under the Open Government Licence "
    "\N{EN DASH} British Columbia."
)
FILENAME = "regional-district-population.csv"
PROVENANCE_FILENAME = "provenance.json"
CHECKSUM_FILENAME = "SHA256SUMS"

BASE_COLUMNS = [
    "Region",
    "Region.Name",
    "Region.Type",
    "Year",
    "Type",
    "Gender",
    "Total",
]
AGE_COLUMNS = [str(age) for age in range(90)] + ["90+"]
EXPECTED_COLUMNS = BASE_COLUMNS + AGE_COLUMNS
EXPECTED_ROWS = 4_230
EXPECTED_REGIONS = 30
EXPECTED_SOURCE_YEARS = set(range(1971, 2047))
EXPECTED_NONZERO_YEARS = set(range(2001, 2047))
EXPECTED_GENDER_ROWS = 1_410
EXPECTED_RETAINED_WIDE_ROWS = 2_668
EXPECTED_RETAINED_LONG_ROWS = 242_788
USER_AGENT = "fabric-with-github-bc-population-refresh/1.0"

OpenUrl = Callable[..., BinaryIO]


class DatasetError(RuntimeError):
    """Base error for snapshot validation and refresh."""


class ValidationError(DatasetError):
    """The source or committed snapshot violates its contract."""


class UpstreamDriftError(DatasetError):
    """The upstream resource differs from the pinned snapshot."""


def _integer(row_number: int, column: str, value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValidationError(
            f"row {row_number}: {column} must be an integer, got {value!r}"
        ) from exc
    if parsed < 0:
        raise ValidationError(
            f"row {row_number}: {column} must not be negative, got {parsed}"
        )
    return parsed


def validate_csv(path: Path) -> dict[str, Any]:
    """Validate the raw source contract and return derived statistics."""
    rows_by_key: dict[tuple[int, int, str, str], dict[str, int]] = {}
    regions: set[int] = set()
    source_years: set[int] = set()
    nonzero_years: set[int] = set()
    years_by_type: dict[str, set[int]] = {"Estimate": set(), "Projection": set()}
    gender_counts: Counter[str] = Counter()
    retained_wide_rows = 0

    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise ValidationError(f"cannot read CSV {path}: {exc}") from exc

    with handle:
        reader = csv.DictReader(handle)
        columns = list(reader.fieldnames or [])
        if columns != EXPECTED_COLUMNS:
            raise ValidationError(
                "CSV columns changed; expected "
                f"{EXPECTED_COLUMNS!r}, got {columns!r}"
            )

        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValidationError(f"row {row_number}: unexpected extra fields")

            region = _integer(row_number, "Region", row["Region"])
            year = _integer(row_number, "Year", row["Year"])
            population_type = row["Type"]
            gender = row["Gender"]

            if row["Region.Type"] != "Regional District":
                raise ValidationError(
                    f"row {row_number}: unexpected Region.Type "
                    f"{row['Region.Type']!r}"
                )
            if population_type not in years_by_type:
                raise ValidationError(
                    f"row {row_number}: unexpected Type {population_type!r}"
                )
            if gender not in {"F", "M", "T"}:
                raise ValidationError(
                    f"row {row_number}: unexpected Gender {gender!r}"
                )

            values = {
                column: _integer(row_number, column, row[column])
                for column in ["Total", *AGE_COLUMNS]
            }
            age_sum = sum(values[column] for column in AGE_COLUMNS)
            if age_sum != values["Total"]:
                raise ValidationError(
                    f"row {row_number}: age sum {age_sum} does not equal "
                    f"Total {values['Total']}"
                )

            key = (region, year, population_type, gender)
            if key in rows_by_key:
                raise ValidationError(f"row {row_number}: duplicate key {key!r}")
            rows_by_key[key] = values
            regions.add(region)
            source_years.add(year)
            years_by_type[population_type].add(year)
            gender_counts[gender] += 1
            if region != 0:
                nonzero_years.add(year)
                if gender != "T":
                    retained_wide_rows += 1

    if len(rows_by_key) != EXPECTED_ROWS:
        raise ValidationError(
            f"expected {EXPECTED_ROWS:,} rows, got {len(rows_by_key):,}"
        )
    if len(regions) != EXPECTED_REGIONS or 0 not in regions:
        raise ValidationError(
            f"expected {EXPECTED_REGIONS} region codes including 0, got "
            f"{len(regions)}"
        )
    if source_years != EXPECTED_SOURCE_YEARS:
        raise ValidationError(
            "source years changed; expected continuous 1971-2046"
        )
    if nonzero_years != EXPECTED_NONZERO_YEARS:
        raise ValidationError(
            "nonzero regional-district years changed; expected continuous "
            "2001-2046"
        )
    if gender_counts != Counter(
        {"F": EXPECTED_GENDER_ROWS, "M": EXPECTED_GENDER_ROWS, "T": EXPECTED_GENDER_ROWS}
    ):
        raise ValidationError(
            f"expected 1,410 rows per gender, got {dict(gender_counts)!r}"
        )

    estimate_years = years_by_type["Estimate"]
    projection_years = years_by_type["Projection"]
    if (
        not estimate_years
        or not projection_years
        or min(estimate_years) != 1971
        or max(projection_years) != 2046
        or estimate_years & projection_years
        or estimate_years | projection_years != EXPECTED_SOURCE_YEARS
        or estimate_years != set(range(1971, max(estimate_years) + 1))
        or projection_years
        != set(range(min(projection_years), 2047))
        or max(estimate_years) + 1 != min(projection_years)
    ):
        raise ValidationError(
            "Estimate and Projection years must form one continuous, "
            "non-overlapping 1971-2046 scope"
        )

    expected_keys = {
        (region, year, population_type, gender)
        for region in regions
        for year in (EXPECTED_SOURCE_YEARS if region == 0 else EXPECTED_NONZERO_YEARS)
        for population_type in (
            "Estimate"
            if year in estimate_years
            else "Projection",
        )
        for gender in ("F", "M", "T")
    }
    if set(rows_by_key) != expected_keys:
        missing = len(expected_keys - set(rows_by_key))
        unexpected = len(set(rows_by_key) - expected_keys)
        raise ValidationError(
            f"region/year/type/gender coverage changed: {missing} missing and "
            f"{unexpected} unexpected keys"
        )

    for region, year, population_type, gender in rows_by_key:
        if gender != "T":
            continue
        total_values = rows_by_key[(region, year, population_type, "T")]
        female_values = rows_by_key[(region, year, population_type, "F")]
        male_values = rows_by_key[(region, year, population_type, "M")]
        for column in ["Total", *AGE_COLUMNS]:
            expected_total = female_values[column] + male_values[column]
            if total_values[column] != expected_total:
                raise ValidationError(
                    f"Region {region}, year {year}, column {column}: "
                    f"T={total_values[column]} but F+M={expected_total}"
                )

    if retained_wide_rows != EXPECTED_RETAINED_WIDE_ROWS:
        raise ValidationError(
            f"expected {EXPECTED_RETAINED_WIDE_ROWS:,} retained wide rows, got "
            f"{retained_wide_rows:,}"
        )
    retained_long_rows = retained_wide_rows * len(AGE_COLUMNS)
    if retained_long_rows != EXPECTED_RETAINED_LONG_ROWS:
        raise ValidationError(
            f"expected {EXPECTED_RETAINED_LONG_ROWS:,} retained long rows, got "
            f"{retained_long_rows:,}"
        )

    return {
        "age_column_count": len(AGE_COLUMNS),
        "estimate_year_end": max(estimate_years),
        "estimate_year_start": min(estimate_years),
        "gender_rows": dict(sorted(gender_counts.items())),
        "nonzero_year_end": max(nonzero_years),
        "nonzero_year_start": min(nonzero_years),
        "projection_year_end": max(projection_years),
        "projection_year_start": min(projection_years),
        "region_count": len(regions),
        "retained_long_rows": retained_long_rows,
        "retained_wide_rows": retained_wide_rows,
        "row_count": len(rows_by_key),
        "source_year_count": len(source_years),
        "source_year_end": max(source_years),
        "source_year_start": min(source_years),
    }


def _request_json(
    url: str, *, opener: OpenUrl = urllib.request.urlopen, timeout: float = 60.0
) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener(request, timeout=timeout) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValidationError("CKAN response must be a JSON object")
    return payload


def locate_resource(
    package_payload: dict[str, Any], *, expected_download_url: str = DOWNLOAD_URL
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return the pinned package and resource, rejecting substitutions."""
    if package_payload.get("success") is not True:
        raise ValidationError("CKAN package_show did not report success")
    package = package_payload.get("result")
    if not isinstance(package, dict) or package.get("id") != PACKAGE_ID:
        raise ValidationError(f"CKAN response is not for package {PACKAGE_ID}")
    resources = package.get("resources")
    if not isinstance(resources, list):
        raise ValidationError("CKAN package resources are missing")
    matches = [
        resource
        for resource in resources
        if isinstance(resource, dict) and resource.get("id") == RESOURCE_ID
    ]
    if len(matches) != 1:
        raise ValidationError(
            f"expected exactly one resource {RESOURCE_ID}, found {len(matches)}"
        )
    resource = matches[0]
    if resource.get("package_id") != PACKAGE_ID:
        raise ValidationError("pinned resource belongs to a different package")
    if resource.get("url") != expected_download_url:
        raise ValidationError(
            "pinned resource download URL changed; refusing to select another "
            f"resource or URL: {resource.get('url')!r}"
        )
    required_text_fields = {
        "package metadata_modified": package.get("metadata_modified"),
        "package title": package.get("title"),
        "licence title": package.get("license_title"),
        "licence URL": package.get("license_url"),
        "resource last_modified": resource.get("last_modified"),
        "resource name": resource.get("name"),
    }
    missing = [name for name, value in required_text_fields.items() if not value]
    if missing:
        raise ValidationError(
            "CKAN metadata is missing required fields: " + ", ".join(missing)
        )
    return package, resource


def fetch_metadata(
    package_show_url: str = PACKAGE_SHOW_URL,
    *,
    expected_download_url: str = DOWNLOAD_URL,
    opener: OpenUrl = urllib.request.urlopen,
    timeout: float = 60.0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _request_json(package_show_url, opener=opener, timeout=timeout)
    return locate_resource(payload, expected_download_url=expected_download_url)


def _download(
    url: str,
    destination: Path,
    *,
    opener: OpenUrl = urllib.request.urlopen,
    timeout: float = 120.0,
) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with opener(request, timeout=timeout) as response:
        with destination.open("wb") as handle:
            shutil.copyfileobj(response, handle)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _provenance(
    path: Path,
    stats: dict[str, Any],
    package: dict[str, Any],
    resource: dict[str, Any],
    retrieved_at: str,
    package_show_url: str,
) -> dict[str, Any]:
    return {
        "attribution": ATTRIBUTION,
        "contract": {
            "gender_rows": stats["gender_rows"],
            "region_count": stats["region_count"],
            "retained_long_rows": stats["retained_long_rows"],
            "retained_wide_rows": stats["retained_wide_rows"],
            "source_year_count": stats["source_year_count"],
        },
        "file": {
            "byte_size": path.stat().st_size,
            "filename": FILENAME,
            "row_count": stats["row_count"],
            "sha256": _sha256(path),
        },
        "licence": {
            "title": package["license_title"],
            "url": package["license_url"],
        },
        "retrieved_at": retrieved_at,
        "schema": {
            "age_columns": AGE_COLUMNS,
            "columns": EXPECTED_COLUMNS,
        },
        "source": {
            "catalogue_url": CATALOGUE_URL,
            "download_url": resource["url"],
            "package_api_url": package_show_url,
            "package_id": PACKAGE_ID,
            "package_metadata_modified": package["metadata_modified"],
            "package_title": package["title"],
            "package_url": PACKAGE_URL,
            "resource_id": RESOURCE_ID,
            "resource_last_modified": resource["last_modified"],
            "resource_name": resource["name"],
            "resource_url": RESOURCE_URL,
            "source_url": resource["url"],
        },
        "year_scopes": {
            "estimate": {
                "end": stats["estimate_year_end"],
                "start": stats["estimate_year_start"],
            },
            "nonzero_regional_district": {
                "end": stats["nonzero_year_end"],
                "start": stats["nonzero_year_start"],
            },
            "projection": {
                "end": stats["projection_year_end"],
                "start": stats["projection_year_start"],
            },
            "source": {
                "end": stats["source_year_end"],
                "start": stats["source_year_start"],
            },
        },
    }


def _validate_retrieved_at(value: Any) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValidationError("retrieved_at must be a UTC ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError("retrieved_at must be a UTC ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValidationError("retrieved_at must be a UTC ISO 8601 timestamp")
    return value


def _stage_text(directory: Path, prefix: str, content: str) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=directory,
        prefix=prefix,
        delete=False,
    ) as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
        return Path(handle.name)


def _replace_snapshot(staged: dict[Path, Path]) -> None:
    """Replace all snapshot files with rollback if an OS operation fails."""
    backups: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for target in staged:
            if target.exists():
                with tempfile.NamedTemporaryFile(
                    dir=target.parent,
                    prefix=f".{target.name}.backup-",
                    delete=False,
                ) as handle:
                    backup = Path(handle.name)
                shutil.copy2(target, backup)
                backups[target] = backup

        for target, stage in staged.items():
            os.replace(stage, target)
            replaced.append(target)
    except OSError:
        for target in reversed(replaced):
            backup = backups.pop(target, None)
            if backup is not None:
                os.replace(backup, target)
            else:
                target.unlink(missing_ok=True)
        raise
    finally:
        for stage in staged.values():
            stage.unlink(missing_ok=True)
        for backup in backups.values():
            backup.unlink(missing_ok=True)


def _read_provenance(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read provenance {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError("provenance must be a JSON object")
    return value


def _metadata_projection(provenance: dict[str, Any]) -> dict[str, Any]:
    try:
        return {
            "attribution": provenance["attribution"],
            "licence": provenance["licence"],
            "source": provenance["source"],
            "year_scopes": provenance["year_scopes"],
        }
    except KeyError as exc:
        raise ValidationError(
            f"provenance is missing required field {exc.args[0]!r}"
        ) from exc


def refresh_snapshot(
    dataset_dir: Path,
    *,
    package_show_url: str = PACKAGE_SHOW_URL,
    expected_download_url: str = DOWNLOAD_URL,
    opener: OpenUrl = urllib.request.urlopen,
    timeout: float = 120.0,
    retrieved_at: str | None = None,
) -> dict[str, Any]:
    """Download, validate, and atomically replace the governed snapshot."""
    dataset_dir.mkdir(parents=True, exist_ok=True)
    package, resource = fetch_metadata(
        package_show_url,
        expected_download_url=expected_download_url,
        opener=opener,
        timeout=timeout,
    )
    with tempfile.NamedTemporaryFile(
        dir=dataset_dir, prefix=".bc-population-download-", delete=False
    ) as handle:
        csv_stage = Path(handle.name)

    provenance_stage: Path | None = None
    checksum_stage: Path | None = None
    try:
        _download(
            resource["url"], csv_stage, opener=opener, timeout=timeout
        )
        stats = validate_csv(csv_stage)
        timestamp = retrieved_at or datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        )
        _validate_retrieved_at(timestamp)
        provenance = _provenance(
            csv_stage,
            stats,
            package,
            resource,
            timestamp,
            package_show_url,
        )
        provenance_text = (
            json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n"
        )
        checksum_text = f"{provenance['file']['sha256']}  {FILENAME}\n"
        provenance_stage = _stage_text(
            dataset_dir, ".bc-population-provenance-", provenance_text
        )
        checksum_stage = _stage_text(
            dataset_dir, ".bc-population-checksum-", checksum_text
        )
        _replace_snapshot(
            {
                dataset_dir / FILENAME: csv_stage,
                dataset_dir / PROVENANCE_FILENAME: provenance_stage,
                dataset_dir / CHECKSUM_FILENAME: checksum_stage,
            }
        )
        return provenance
    finally:
        csv_stage.unlink(missing_ok=True)
        if provenance_stage is not None:
            provenance_stage.unlink(missing_ok=True)
        if checksum_stage is not None:
            checksum_stage.unlink(missing_ok=True)


def check_snapshot(
    dataset_dir: Path,
    *,
    package_show_url: str = PACKAGE_SHOW_URL,
    expected_download_url: str = DOWNLOAD_URL,
    opener: OpenUrl = urllib.request.urlopen,
    timeout: float = 120.0,
) -> dict[str, Any]:
    """Validate the committed snapshot and fail if upstream has drifted."""
    csv_path = dataset_dir / FILENAME
    provenance_path = dataset_dir / PROVENANCE_FILENAME
    checksum_path = dataset_dir / CHECKSUM_FILENAME
    committed_stats = validate_csv(csv_path)
    committed = _read_provenance(provenance_path)
    _validate_retrieved_at(committed.get("retrieved_at"))
    committed_hash = _sha256(csv_path)
    expected_checksum = f"{committed_hash}  {FILENAME}\n"
    try:
        actual_checksum = checksum_path.read_text(encoding="ascii")
    except OSError as exc:
        raise ValidationError(f"cannot read checksum file {checksum_path}: {exc}") from exc
    if actual_checksum != expected_checksum:
        raise ValidationError("SHA256SUMS does not match the committed CSV")
    try:
        committed_file = committed["file"]
        committed_schema = committed["schema"]
        committed_contract = committed["contract"]
    except KeyError as exc:
        raise ValidationError(
            f"provenance is missing required field {exc.args[0]!r}"
        ) from exc
    if committed_file != {
        "byte_size": csv_path.stat().st_size,
        "filename": FILENAME,
        "row_count": committed_stats["row_count"],
        "sha256": committed_hash,
    }:
        raise ValidationError("provenance file metadata does not match the CSV")
    if committed_schema != {
        "age_columns": AGE_COLUMNS,
        "columns": EXPECTED_COLUMNS,
    }:
        raise ValidationError("provenance schema does not match the CSV contract")
    if committed_contract != {
        "gender_rows": committed_stats["gender_rows"],
        "region_count": committed_stats["region_count"],
        "retained_long_rows": committed_stats["retained_long_rows"],
        "retained_wide_rows": committed_stats["retained_wide_rows"],
        "source_year_count": committed_stats["source_year_count"],
    }:
        raise ValidationError("provenance contract does not match the CSV")

    package, resource = fetch_metadata(
        package_show_url,
        expected_download_url=expected_download_url,
        opener=opener,
        timeout=timeout,
    )
    with tempfile.NamedTemporaryFile(
        dir=dataset_dir, prefix=".bc-population-check-", delete=False
    ) as handle:
        upstream_path = Path(handle.name)
    try:
        _download(resource["url"], upstream_path, opener=opener, timeout=timeout)
        upstream_stats = validate_csv(upstream_path)
        upstream = _provenance(
            upstream_path,
            upstream_stats,
            package,
            resource,
            committed.get("retrieved_at", ""),
            package_show_url,
        )
    finally:
        upstream_path.unlink(missing_ok=True)

    drift: list[str] = []
    if upstream["file"]["sha256"] != committed_hash:
        drift.append("resource SHA-256")
    if upstream["file"]["byte_size"] != csv_path.stat().st_size:
        drift.append("resource byte size")
    if _metadata_projection(upstream) != _metadata_projection(committed):
        drift.append("CKAN metadata")
    if drift:
        raise UpstreamDriftError(
            "upstream drift detected in " + ", ".join(drift) + "; run refresh "
            "and review the resulting diff"
        )
    return committed


def _default_dataset_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "datasets" / "public" / "bc-population"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)
    for mode in ("check", "refresh"):
        command = subparsers.add_parser(mode)
        command.add_argument(
            "--dataset-dir",
            type=Path,
            default=_default_dataset_dir(),
            help="snapshot directory (defaults to the repository dataset path)",
        )
        command.add_argument(
            "--package-show-url",
            default=PACKAGE_SHOW_URL,
            help="CKAN package_show URL; override only for isolated tests",
        )
        command.add_argument(
            "--expected-download-url",
            default=DOWNLOAD_URL,
            help="pinned resource URL; override only for isolated tests",
        )
        command.add_argument("--timeout", type=float, default=120.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.mode == "refresh":
            provenance = refresh_snapshot(
                args.dataset_dir,
                package_show_url=args.package_show_url,
                expected_download_url=args.expected_download_url,
                timeout=args.timeout,
            )
            print(
                f"refreshed {provenance['file']['filename']}: "
                f"{provenance['file']['row_count']:,} rows, "
                f"sha256 {provenance['file']['sha256']}"
            )
        else:
            provenance = check_snapshot(
                args.dataset_dir,
                package_show_url=args.package_show_url,
                expected_download_url=args.expected_download_url,
                timeout=args.timeout,
            )
            print(
                f"snapshot is current: {provenance['file']['filename']} "
                f"sha256 {provenance['file']['sha256']}"
            )
    except (
        DatasetError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        urllib.error.URLError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
