"""Tests for the curated public CCHS aggregate snapshot."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = REPO_ROOT / "datasets/public/cchs-annual/snapshot"
SCHEMA_ROOT = REPO_ROOT / "datasets/schemas"
PREPARE_SCRIPT = REPO_ROOT / "scripts/prepare_cchs_data.py"
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/cchs"

SCHEMA_FILE_MAP = {
    "cchs-observations.schema.json": "observations.csv",
    "cchs-periods.schema.json": "periods.csv",
    "cchs-geographies.schema.json": "geographies.csv",
    "cchs-age-groups.schema.json": "age-groups.csv",
    "cchs-sexes.schema.json": "sexes.csv",
    "cchs-indicators.schema.json": "indicators.csv",
    "cchs-characteristics.schema.json": "characteristics.csv",
    "cchs-quality-statuses.schema.json": "quality-statuses.csv",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_committed_snapshot_matches_schemas_and_manifest() -> None:
    manifest = json.loads((SNAPSHOT_ROOT / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["contractVersion"] == "1.0"
    assert manifest["source"]["productId"] == "13-10-0096-01"
    assert manifest["source"]["archived"] is True
    assert manifest["source"]["referenceYears"] == list(range(2015, 2023))
    assert "does not constitute an endorsement" in manifest["attribution"]

    for schema_name, csv_name in SCHEMA_FILE_MAP.items():
        schema = json.loads((SCHEMA_ROOT / schema_name).read_text(encoding="utf-8"))
        columns, rows = read_csv(SNAPSHOT_ROOT / csv_name)
        assert columns == schema["x-columnOrder"], schema_name
        assert rows, csv_name
        assert manifest["files"][csv_name]["rows"] == len(rows)
        assert manifest["files"][csv_name]["sha256"] == file_sha256(
            SNAPSHOT_ROOT / csv_name
        )


def test_snapshot_dimensions_and_fact_integrity() -> None:
    _, periods = read_csv(SNAPSHOT_ROOT / "periods.csv")
    _, geographies = read_csv(SNAPSHOT_ROOT / "geographies.csv")
    _, ages = read_csv(SNAPSHOT_ROOT / "age-groups.csv")
    _, sexes = read_csv(SNAPSHOT_ROOT / "sexes.csv")
    _, indicators = read_csv(SNAPSHOT_ROOT / "indicators.csv")
    _, characteristics = read_csv(SNAPSHOT_ROOT / "characteristics.csv")
    _, statuses = read_csv(SNAPSHOT_ROOT / "quality-statuses.csv")
    columns, observations = read_csv(SNAPSHOT_ROOT / "observations.csv")

    assert [int(row["reference_year"]) for row in periods] == list(range(2015, 2023))
    assert len(geographies) == 11
    assert sum(row["is_british_columbia"] == "true" for row in geographies) == 1
    assert sum(row["is_canada_comparator"] == "true" for row in geographies) == 1
    assert {row["geography_code"] for row in geographies} == {
        "CANX",
        "NL",
        "PE",
        "NS",
        "NB",
        "QC",
        "ON",
        "MB",
        "SK",
        "AB",
        "BC",
    }
    assert len(ages) == 7
    assert {row["sex_name"] for row in sexes} == {"Both sexes", "Females", "Males"}
    assert len(indicators) == 8
    assert len(characteristics) == 6
    assert len(observations) == 76032
    assert set(columns).isdisjoint(
        {"name", "address", "postal_code", "phone", "email", "respondent_id"}
    )

    key_sets = {
        "period_key": {row["period_key"] for row in periods},
        "geography_key": {row["geography_key"] for row in geographies},
        "age_group_key": {row["age_group_key"] for row in ages},
        "sex_key": {row["sex_key"] for row in sexes},
        "indicator_key": {row["indicator_key"] for row in indicators},
        "characteristic_key": {
            row["characteristic_key"] for row in characteristics
        },
        "quality_status_key": {
            row["quality_status_key"] for row in statuses
        },
    }
    for key_name, valid_keys in key_sets.items():
        assert {row[key_name] for row in observations}.issubset(valid_keys)

    grains = {
        tuple(
            row[column]
            for column in (
                "period_key",
                "geography_key",
                "age_group_key",
                "sex_key",
                "indicator_key",
                "characteristic_key",
            )
        )
        for row in observations
    }
    assert len(grains) == len(observations)

    status_by_key = {
        row["quality_status_key"]: row["source_status"] for row in statuses
    }
    for row in observations:
        status = status_by_key[row["quality_status_key"]]
        if status in {"F", "x", ".."}:
            assert row["value"] == ""
    assert any(
        status_by_key[row["quality_status_key"]] == "E" and row["value"]
        for row in observations
    )


def test_offline_cli_is_deterministic_and_preserves_status_policy() -> None:
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        command = [
            sys.executable,
            str(PREPARE_SCRIPT),
            "--input-csv",
            str(FIXTURE_ROOT / "13100096-mini.csv"),
            "--config",
            str(FIXTURE_ROOT / "selection-mini.json"),
            "--snapshot-date",
            "2026-07-24",
        ]
        subprocess.run(
            [*command, "--output-dir", first],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [*command, "--output-dir", second],
            check=True,
            capture_output=True,
            text=True,
        )

        first_files = sorted(path.name for path in Path(first).iterdir())
        second_files = sorted(path.name for path in Path(second).iterdir())
        assert first_files == second_files
        for filename in first_files:
            assert (Path(first) / filename).read_bytes() == (
                Path(second) / filename
            ).read_bytes()

        _, statuses = read_csv(Path(first) / "quality-statuses.csv")
        _, observations = read_csv(Path(first) / "observations.csv")
        status_by_key = {
            row["quality_status_key"]: row["source_status"] for row in statuses
        }
        values_by_status = {}
        for row in observations:
            values_by_status.setdefault(
                status_by_key[row["quality_status_key"]], []
            ).append(row["value"])

        assert values_by_status["E"] == ["3200000", "66.5"]
        assert values_by_status["F"] == [""]
        assert values_by_status["x"] == [""]
        assert values_by_status[".."] == [""]


def test_cli_rejects_source_column_drift() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        malformed = Path(temp_dir) / "malformed.csv"
        malformed.write_text("REF_DATE,GEO\n2022,British Columbia\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(PREPARE_SCRIPT),
                "--input-csv",
                str(malformed),
                "--config",
                str(FIXTURE_ROOT / "selection-mini.json"),
                "--output-dir",
                str(Path(temp_dir) / "output"),
                "--snapshot-date",
                "2026-07-24",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Unexpected source columns" in result.stderr
