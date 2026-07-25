"""Customer transaction fixture generation."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from .common import SYNTHETIC_MARKER, ensure_minimum_rows, format_timestamp, make_rng, money, write_csv

DOMAIN = "customer-transactions"
FIELDNAMES = [
    "transaction_id",
    "customer_id",
    "transaction_ts",
    "ingest_ts",
    "merchant_category",
    "channel",
    "amount",
    "currency",
    "region",
    "payment_method",
    "synthetic_record",
    "anomaly_label",
]


def _base_record(index: int, seed: int) -> dict[str, str]:
    rng = make_rng(seed, 101 + index)
    transaction_time = datetime(2026, 1, 10, 9, 0, 0) + timedelta(minutes=index * 11)
    ingest_time = transaction_time + timedelta(minutes=2 + (index % 4))
    return {
        "transaction_id": f"TXN-{1000 + index}",
        "customer_id": f"CUST-{200 + (index % 7)}",
        "transaction_ts": format_timestamp(transaction_time),
        "ingest_ts": format_timestamp(ingest_time),
        "merchant_category": ["grocery", "travel", "software", "fuel", "dining"][index % 5],
        "channel": ["card_present", "ecommerce", "mobile_wallet"][index % 3],
        "amount": money(23.50 + (index * 6.75) + rng.random() * 3.0),
        "currency": "USD",
        "region": ["north", "south", "east", "west"][index % 4],
        "payment_method": ["credit", "debit", "prepaid"][index % 3],
        "synthetic_record": SYNTHETIC_MARKER,
        "anomaly_label": "none",
    }


def generate(output_dir: Path, row_count: int, seed: int) -> list[Path]:
    """Generate the customer transactions fixture."""
    ensure_minimum_rows(row_count)
    records = [_base_record(index, seed) for index in range(row_count - 2)]

    late_transaction_time = datetime(2026, 1, 9, 16, 40, 0)
    records.append(
        {
            "transaction_id": "TXN-2099",
            "customer_id": "CUST-207",
            "transaction_ts": format_timestamp(late_transaction_time),
            "ingest_ts": format_timestamp(late_transaction_time + timedelta(days=2, hours=3)),
            "merchant_category": "travel",
            "channel": "ecommerce",
            "amount": money(148.20),
            "currency": "USD",
            "region": "west",
            "payment_method": "credit",
            "synthetic_record": SYNTHETIC_MARKER,
            "anomaly_label": "late_arrival",
        }
    )

    duplicate_record = records[2].copy()
    duplicate_record["anomaly_label"] = "duplicate_transaction"
    records.append(duplicate_record)

    path = output_dir / DOMAIN / "transactions.csv"
    return [write_csv(path, FIELDNAMES, records)]
