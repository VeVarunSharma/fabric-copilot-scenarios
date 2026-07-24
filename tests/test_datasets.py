"""Tests for deterministic synthetic dataset generation."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATASETS_ROOT = REPO_ROOT / "datasets"
SYNTHETIC_ROOT = DATASETS_ROOT / "synthetic"
SCHEMA_ROOT = DATASETS_ROOT / "schemas"
GENERATOR_SCRIPT = REPO_ROOT / "scripts" / "generate_data.py"
WORK_ROOT = REPO_ROOT / ".dataset-test-output"

CSV_SCHEMA_FIXTURE_MAP = {
    "transactions.schema.json": SYNTHETIC_ROOT / "customer-transactions" / "transactions.csv",
    "claims.schema.json": SYNTHETIC_ROOT / "healthcare-claims" / "claims.csv",
    "customers.schema.json": SYNTHETIC_ROOT / "retail-purchases" / "customers.csv",
    "products.schema.json": SYNTHETIC_ROOT / "retail-purchases" / "products.csv",
    "purchases.schema.json": SYNTHETIC_ROOT / "retail-purchases" / "purchases.csv",
    "accounts.schema.json": SYNTHETIC_ROOT / "financial-reporting" / "accounts.csv",
    "general_ledger.schema.json": SYNTHETIC_ROOT / "financial-reporting" / "general_ledger.csv",
}
JSONL_SCHEMA_FIXTURE_MAP = {
    "telemetry.schema.json": SYNTHETIC_ROOT / "iot-telemetry" / "telemetry.jsonl",
}
EXPECTED_GENERATED_FILES = [
    Path("customer-transactions/transactions.csv"),
    Path("healthcare-claims/claims.csv"),
    Path("retail-purchases/customers.csv"),
    Path("retail-purchases/products.csv"),
    Path("retail-purchases/purchases.csv"),
    Path("iot-telemetry/telemetry.jsonl"),
    Path("financial-reporting/accounts.csv"),
    Path("financial-reporting/general_ledger.csv"),
]


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="ascii", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_jsonl_rows(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="ascii") as handle:
        return [json.loads(line) for line in handle if line.strip()]


class DatasetFixtureTests(unittest.TestCase):
    maxDiff = None

    def tearDown(self) -> None:
        if WORK_ROOT.exists():
            shutil.rmtree(WORK_ROOT)

    def test_readme_documents_safety_and_anomalies(self) -> None:
        readme_text = (DATASETS_ROOT / "README.md").read_text(encoding="ascii")
        self.assertIn("All records in `datasets/synthetic/` are fictional", readme_text)
        self.assertIn("duplicate_transaction", readme_text)
        self.assertIn("orphan_account", readme_text)

    def test_schema_column_order_matches_fixtures(self) -> None:
        for schema_name, fixture_path in CSV_SCHEMA_FIXTURE_MAP.items():
            schema = json.loads((SCHEMA_ROOT / schema_name).read_text(encoding="ascii"))
            columns, rows = read_csv_rows(fixture_path)
            self.assertEqual(schema["x-columnOrder"], columns, schema_name)
            self.assertTrue(rows, fixture_path.as_posix())
            self.assertEqual(set(schema["required"]), set(schema["properties"]), schema_name)

        for schema_name, fixture_path in JSONL_SCHEMA_FIXTURE_MAP.items():
            schema = json.loads((SCHEMA_ROOT / schema_name).read_text(encoding="ascii"))
            records = read_jsonl_rows(fixture_path)
            self.assertTrue(records, fixture_path.as_posix())
            self.assertEqual(
                set(schema["required"]),
                set(records[0].keys()),
                schema_name,
            )

    def test_all_fixtures_include_synthetic_markers(self) -> None:
        for fixture_path in CSV_SCHEMA_FIXTURE_MAP.values():
            _, rows = read_csv_rows(fixture_path)
            self.assertTrue(all(row["synthetic_record"] == "SYNTHETIC" for row in rows))

        telemetry_rows = read_jsonl_rows(
            JSONL_SCHEMA_FIXTURE_MAP["telemetry.schema.json"]
        )
        self.assertTrue(
            all(record["synthetic_record"] == "SYNTHETIC" for record in telemetry_rows)
        )

        claims_columns, _ = read_csv_rows(
            CSV_SCHEMA_FIXTURE_MAP["claims.schema.json"]
        )
        self.assertTrue(
            {"claim_id", "member_id", "provider_code"}.issubset(set(claims_columns))
        )
        self.assertFalse(
            {"first_name", "last_name", "address", "phone"}.intersection(claims_columns)
        )

    def test_retail_dimension_fields_support_model_usage(self) -> None:
        customer_columns, customer_rows = read_csv_rows(
            CSV_SCHEMA_FIXTURE_MAP["customers.schema.json"]
        )
        self.assertIn("customer_name", customer_columns)
        self.assertTrue(all(row["customer_name"] for row in customer_rows))
        self.assertTrue(all(" " in row["customer_name"] for row in customer_rows))

        product_columns, product_rows = read_csv_rows(
            CSV_SCHEMA_FIXTURE_MAP["products.schema.json"]
        )
        self.assertTrue(
            {"product_name", "unit_cost", "unit_price"}.issubset(set(product_columns))
        )
        self.assertTrue(all(row["product_name"] for row in product_rows))
        self.assertTrue(
            all(
                float(row["unit_cost"]) > 0.0
                and float(row["unit_cost"]) < float(row["unit_price"])
                for row in product_rows
            )
        )

    def test_expected_anomalies_are_present(self) -> None:
        _, transaction_rows = read_csv_rows(
            CSV_SCHEMA_FIXTURE_MAP["transactions.schema.json"]
        )
        transaction_counts = Counter(row["transaction_id"] for row in transaction_rows)
        self.assertTrue(any(count > 1 for count in transaction_counts.values()))
        self.assertTrue(
            any(row["anomaly_label"] == "late_arrival" for row in transaction_rows)
        )

        _, claim_rows = read_csv_rows(CSV_SCHEMA_FIXTURE_MAP["claims.schema.json"])
        self.assertTrue(
            any(
                row["anomaly_label"] == "missing_provider_code"
                and row["provider_code"] == ""
                for row in claim_rows
            )
        )
        self.assertTrue(
            any(
                row["anomaly_label"] == "invalid_claim_amount"
                and float(row["claim_amount"]) < 0
                for row in claim_rows
            )
        )

        _, purchase_rows = read_csv_rows(CSV_SCHEMA_FIXTURE_MAP["purchases.schema.json"])
        purchase_counts = Counter(row["purchase_id"] for row in purchase_rows)
        self.assertTrue(any(count > 1 for count in purchase_counts.values()))
        self.assertTrue(
            any(
                row["anomaly_label"] == "null_customer_id" and row["customer_id"] == ""
                for row in purchase_rows
            )
        )
        self.assertTrue(
            any(
                row["anomaly_label"] == "invalid_quantity_zero"
                and row["quantity"] == "0"
                and row["store_id"] == ""
                for row in purchase_rows
            )
        )

        telemetry_rows = read_jsonl_rows(
            JSONL_SCHEMA_FIXTURE_MAP["telemetry.schema.json"]
        )
        self.assertTrue(
            any(
                "out_of_range_reading" in record["anomaly_labels"]
                and (
                    float(record["temperature_c"]) > 85.0
                    or float(record["humidity_pct"]) > 100.0
                    or float(record["battery_pct"]) > 100.0
                )
                for record in telemetry_rows
            )
        )

        _, account_rows = read_csv_rows(CSV_SCHEMA_FIXTURE_MAP["accounts.schema.json"])
        known_accounts = {row["account_id"] for row in account_rows}
        _, ledger_rows = read_csv_rows(
            CSV_SCHEMA_FIXTURE_MAP["general_ledger.schema.json"]
        )
        self.assertTrue(
            any(
                row["anomaly_label"] == "orphan_account"
                and row["account_id"] not in known_accounts
                for row in ledger_rows
            )
        )

    def test_cli_regenerates_committed_fixtures(self) -> None:
        subprocess.run(
            [
                sys.executable,
                str(GENERATOR_SCRIPT),
                "--output-dir",
                str(WORK_ROOT),
                "--rows",
                "12",
                "--seed",
                "4242",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        generated_files = sorted(path.relative_to(WORK_ROOT) for path in WORK_ROOT.rglob("*") if path.is_file())
        self.assertEqual(sorted(EXPECTED_GENERATED_FILES), generated_files)

        for relative_path in EXPECTED_GENERATED_FILES:
            committed_text = (SYNTHETIC_ROOT / relative_path).read_text(encoding="ascii")
            generated_text = (WORK_ROOT / relative_path).read_text(encoding="ascii")
            self.assertEqual(committed_text, generated_text, relative_path.as_posix())


if __name__ == "__main__":
    unittest.main()
