"""Healthcare claims fixture generation."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from .common import SYNTHETIC_MARKER, ensure_minimum_rows, format_date, make_rng, money, write_csv

DOMAIN = "healthcare-claims"
FIELDNAMES = [
    "claim_id",
    "member_id",
    "claim_received_date",
    "service_date",
    "provider_code",
    "procedure_code",
    "place_of_service",
    "claim_amount",
    "allowed_amount",
    "claim_status",
    "synthetic_record",
    "anomaly_label",
]


def _base_record(index: int, seed: int) -> dict[str, str]:
    rng = make_rng(seed, 201 + index)
    service_date = datetime(2026, 2, 1) + timedelta(days=index)
    claim_received_date = service_date + timedelta(days=2 + (index % 3))
    claim_amount = 95.00 + index * 18.0 + rng.random() * 12.0
    allowed_amount = claim_amount * 0.82
    return {
        "claim_id": f"CLM-{5000 + index}",
        "member_id": f"MBR-{300 + (index % 9)}",
        "claim_received_date": format_date(claim_received_date),
        "service_date": format_date(service_date),
        "provider_code": f"PRV-{700 + (index % 5)}",
        "procedure_code": f"PROC-{110 + (index % 6)}",
        "place_of_service": ["clinic", "telehealth", "outpatient", "lab"][index % 4],
        "claim_amount": money(claim_amount),
        "allowed_amount": money(allowed_amount),
        "claim_status": ["approved", "pending", "approved", "denied"][index % 4],
        "synthetic_record": SYNTHETIC_MARKER,
        "anomaly_label": "none",
    }


def generate(output_dir: Path, row_count: int, seed: int) -> list[Path]:
    """Generate the healthcare claims fixture."""
    ensure_minimum_rows(row_count)
    records = [_base_record(index, seed) for index in range(row_count - 2)]

    missing_provider = _base_record(row_count + 20, seed)
    missing_provider.update(
        {
            "claim_id": "CLM-6198",
            "provider_code": "",
            "claim_status": "pending",
            "anomaly_label": "missing_provider_code",
        }
    )
    records.append(missing_provider)

    invalid_claim = _base_record(row_count + 21, seed)
    invalid_claim.update(
        {
            "claim_id": "CLM-6199",
            "claim_amount": money(-125.00),
            "allowed_amount": money(0.00),
            "claim_status": "rejected",
            "anomaly_label": "invalid_claim_amount",
        }
    )
    records.append(invalid_claim)

    path = output_dir / DOMAIN / "claims.csv"
    return [write_csv(path, FIELDNAMES, records)]
