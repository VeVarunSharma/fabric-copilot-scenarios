"""Tests for the governed BC regional-district population snapshot."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.data import refresh_bc_population as refresh

REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = REPO_ROOT / "datasets" / "public" / "bc-population"
CSV_PATH = DATASET_DIR / refresh.FILENAME
PROVENANCE_PATH = DATASET_DIR / refresh.PROVENANCE_FILENAME
CHECKSUM_PATH = DATASET_DIR / refresh.CHECKSUM_FILENAME
EXPECTED_SHA256 = "177fee280301d12cbab8ea42e6485a1a5cb152b368fab7452e4f5afa3d535fae"
EXPECTED_SIZE = 1_851_056


class FixtureOpener:
    def __init__(
        self,
        package_url: str,
        download_url: str,
        package_payload: dict[str, Any],
        download_bytes: bytes,
    ) -> None:
        self.package_url = package_url
        self.download_url = download_url
        self.package_bytes = json.dumps(package_payload).encode("utf-8")
        self.download_bytes = download_bytes

    def __call__(self, request: Any, *, timeout: float) -> io.BytesIO:
        del timeout
        if request.full_url == self.package_url:
            return io.BytesIO(self.package_bytes)
        if request.full_url == self.download_url:
            return io.BytesIO(self.download_bytes)
        raise AssertionError(f"unexpected network URL {request.full_url}")


def package_payload(download_url: str) -> dict[str, Any]:
    return {
        "success": True,
        "result": {
            "id": refresh.PACKAGE_ID,
            "license_title": "Open Government Licence - British Columbia",
            "license_url": (
                "https://www2.gov.bc.ca/gov/content"
                "?id=A519A56BC2BF44E4A008B33FCF527F61"
            ),
            "metadata_modified": "2026-05-29T20:33:58.806567",
            "title": "BC Sub-Provincial Population Estimates and Projections",
            "resources": [
                {
                    "id": refresh.RESOURCE_ID,
                    "last_modified": "2026-05-20T00:08:11.220444",
                    "name": "Regional Districts (Census Divisions)",
                    "package_id": refresh.PACKAGE_ID,
                    "url": download_url,
                }
            ],
        },
    }


class BCPopulationSnapshotTests(unittest.TestCase):
    maxDiff = None

    def test_provenance_and_checksum_pin_exact_source(self) -> None:
        raw = CSV_PATH.read_bytes()
        provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
        digest = hashlib.sha256(raw).hexdigest()

        self.assertEqual(EXPECTED_SIZE, len(raw))
        self.assertEqual(EXPECTED_SHA256, digest)
        self.assertEqual(
            f"{EXPECTED_SHA256}  {refresh.FILENAME}\n",
            CHECKSUM_PATH.read_text(encoding="ascii"),
        )
        self.assertEqual(refresh.ATTRIBUTION, provenance["attribution"])
        self.assertEqual(
            "Contains information licensed under the Open Government Licence "
            "\N{EN DASH} British Columbia.",
            provenance["attribution"],
        )
        self.assertEqual(
            {
                "byte_size": EXPECTED_SIZE,
                "filename": refresh.FILENAME,
                "row_count": 4_230,
                "sha256": EXPECTED_SHA256,
            },
            provenance["file"],
        )
        self.assertEqual(refresh.EXPECTED_COLUMNS, provenance["schema"]["columns"])
        self.assertEqual(refresh.AGE_COLUMNS, provenance["schema"]["age_columns"])
        self.assertEqual(refresh.CATALOGUE_URL, provenance["source"]["catalogue_url"])
        self.assertEqual(refresh.PACKAGE_ID, provenance["source"]["package_id"])
        self.assertEqual(refresh.PACKAGE_URL, provenance["source"]["package_url"])
        self.assertEqual(
            refresh.PACKAGE_SHOW_URL, provenance["source"]["package_api_url"]
        )
        self.assertEqual(refresh.RESOURCE_ID, provenance["source"]["resource_id"])
        self.assertEqual(refresh.RESOURCE_URL, provenance["source"]["resource_url"])
        self.assertEqual(refresh.DOWNLOAD_URL, provenance["source"]["download_url"])
        self.assertEqual(refresh.DOWNLOAD_URL, provenance["source"]["source_url"])
        self.assertEqual(
            "2026-05-20T00:08:11.220444",
            provenance["source"]["resource_last_modified"],
        )
        self.assertEqual(
            "Open Government Licence - British Columbia",
            provenance["licence"]["title"],
        )
        self.assertEqual(
            "https://www2.gov.bc.ca/gov/content"
            "?id=A519A56BC2BF44E4A008B33FCF527F61",
            provenance["licence"]["url"],
        )
        self.assertEqual(
            {
                "estimate": {"start": 1971, "end": 2025},
                "nonzero_regional_district": {"start": 2001, "end": 2046},
                "projection": {"start": 2026, "end": 2046},
                "source": {"start": 1971, "end": 2046},
            },
            provenance["year_scopes"],
        )
        self.assertIsNotNone(
            datetime.fromisoformat(provenance["retrieved_at"].replace("Z", "+00:00"))
        )

    def test_raw_contract_age_sums_and_gender_totals(self) -> None:
        with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(refresh.EXPECTED_COLUMNS, reader.fieldnames)
            rows = list(reader)

        self.assertEqual(4_230, len(rows))
        self.assertEqual(30, len({row["Region"] for row in rows}))
        self.assertEqual(76, len({int(row["Year"]) for row in rows}))
        self.assertEqual(91, len(refresh.AGE_COLUMNS))
        self.assertEqual(
            set(range(2001, 2047)),
            {int(row["Year"]) for row in rows if row["Region"] != "0"},
        )
        self.assertEqual(
            Counter({"F": 1_410, "M": 1_410, "T": 1_410}),
            Counter(row["Gender"] for row in rows),
        )

        retained = [
            row for row in rows if row["Region"] != "0" and row["Gender"] != "T"
        ]
        self.assertEqual(2_668, len(retained))
        self.assertEqual(242_788, len(retained) * len(refresh.AGE_COLUMNS))
        for row in rows:
            self.assertEqual(
                int(row["Total"]),
                sum(int(row[column]) for column in refresh.AGE_COLUMNS),
            )

        by_key = {
            (row["Region"], row["Year"], row["Type"], row["Gender"]): row
            for row in rows
        }
        for key, total_row in by_key.items():
            region, year, population_type, gender = key
            if gender != "T":
                continue
            female = by_key[(region, year, population_type, "F")]
            male = by_key[(region, year, population_type, "M")]
            for column in ["Total", *refresh.AGE_COLUMNS]:
                self.assertEqual(
                    int(total_row[column]),
                    int(female[column]) + int(male[column]),
                    (region, year, column),
                )

        stats = refresh.validate_csv(CSV_PATH)
        self.assertEqual(2_668, stats["retained_wide_rows"])
        self.assertEqual(242_788, stats["retained_long_rows"])

    def test_refresh_and_check_use_only_pinned_resource(self) -> None:
        package_url = "https://fixtures.invalid/package_show"
        download_url = "https://fixtures.invalid/population.csv"
        source_bytes = CSV_PATH.read_bytes()
        opener = FixtureOpener(
            package_url,
            download_url,
            package_payload(download_url),
            source_bytes,
        )

        with tempfile.TemporaryDirectory(
            prefix=".bc-population-test-", dir=REPO_ROOT
        ) as temporary:
            dataset_dir = Path(temporary)
            provenance = refresh.refresh_snapshot(
                dataset_dir,
                package_show_url=package_url,
                expected_download_url=download_url,
                opener=opener,
                retrieved_at="2026-07-24T20:03:03Z",
            )
            self.assertEqual(EXPECTED_SHA256, provenance["file"]["sha256"])
            before = {
                path.name: path.read_bytes()
                for path in dataset_dir.iterdir()
                if path.is_file()
            }

            checked = refresh.check_snapshot(
                dataset_dir,
                package_show_url=package_url,
                expected_download_url=download_url,
                opener=opener,
            )
            after = {
                path.name: path.read_bytes()
                for path in dataset_dir.iterdir()
                if path.is_file()
            }
            self.assertEqual(provenance, checked)
            self.assertEqual(before, after)
            self.assertEqual(
                {
                    refresh.FILENAME,
                    refresh.PROVENANCE_FILENAME,
                    refresh.CHECKSUM_FILENAME,
                },
                set(after),
            )

    def test_check_detects_hash_drift_without_mutation(self) -> None:
        package_url = "https://fixtures.invalid/package_show"
        download_url = "https://fixtures.invalid/population.csv"
        source_bytes = CSV_PATH.read_bytes()
        initial_opener = FixtureOpener(
            package_url,
            download_url,
            package_payload(download_url),
            source_bytes,
        )
        changed_bytes = source_bytes.replace(
            b"British Columbia", b"British Columbiz", 1
        )
        changed_opener = FixtureOpener(
            package_url,
            download_url,
            package_payload(download_url),
            changed_bytes,
        )

        with tempfile.TemporaryDirectory(
            prefix=".bc-population-test-", dir=REPO_ROOT
        ) as temporary:
            dataset_dir = Path(temporary)
            refresh.refresh_snapshot(
                dataset_dir,
                package_show_url=package_url,
                expected_download_url=download_url,
                opener=initial_opener,
            )
            before = {
                path.name: path.read_bytes()
                for path in dataset_dir.iterdir()
                if path.is_file()
            }
            with self.assertRaisesRegex(
                refresh.UpstreamDriftError, "resource SHA-256"
            ):
                refresh.check_snapshot(
                    dataset_dir,
                    package_show_url=package_url,
                    expected_download_url=download_url,
                    opener=changed_opener,
                )
            after = {
                path.name: path.read_bytes()
                for path in dataset_dir.iterdir()
                if path.is_file()
            }
            self.assertEqual(before, after)

    def test_failed_refresh_leaves_existing_snapshot_untouched(self) -> None:
        package_url = "https://fixtures.invalid/package_show"
        download_url = "https://fixtures.invalid/population.csv"
        invalid_bytes = CSV_PATH.read_bytes().replace(
            b",1107468,", b",1107469,", 1
        )
        opener = FixtureOpener(
            package_url,
            download_url,
            package_payload(download_url),
            invalid_bytes,
        )

        with tempfile.TemporaryDirectory(
            prefix=".bc-population-test-", dir=REPO_ROOT
        ) as temporary:
            dataset_dir = Path(temporary)
            original = {
                refresh.FILENAME: b"existing csv\n",
                refresh.PROVENANCE_FILENAME: b'{"existing": true}\n',
                refresh.CHECKSUM_FILENAME: b"existing checksum\n",
            }
            for name, content in original.items():
                (dataset_dir / name).write_bytes(content)

            with self.assertRaisesRegex(refresh.ValidationError, "age sum"):
                refresh.refresh_snapshot(
                    dataset_dir,
                    package_show_url=package_url,
                    expected_download_url=download_url,
                    opener=opener,
                )
            self.assertEqual(
                original,
                {
                    name: (dataset_dir / name).read_bytes()
                    for name in original
                },
            )
            self.assertEqual(set(original), {path.name for path in dataset_dir.iterdir()})

    def test_resource_id_cannot_be_substituted(self) -> None:
        payload = package_payload("https://fixtures.invalid/population.csv")
        payload["result"]["resources"][0]["id"] = "different-resource"
        with self.assertRaisesRegex(refresh.ValidationError, refresh.RESOURCE_ID):
            refresh.locate_resource(
                payload,
                expected_download_url="https://fixtures.invalid/population.csv",
            )


if __name__ == "__main__":
    unittest.main()
