"""IoT telemetry fixture generation."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from .common import SYNTHETIC_MARKER, ensure_minimum_rows, format_timestamp, make_rng, write_jsonl

DOMAIN = "iot-telemetry"


def _base_record(index: int, seed: int) -> dict[str, object]:
    rng = make_rng(seed, 401 + index)
    event_time = datetime(2026, 4, 12, 8, 0, 0) + timedelta(minutes=index * 7)
    return {
        "device_id": f"DEV-{120 + (index % 5)}",
        "site_id": f"SITE-{10 + (index % 3)}",
        "event_time": format_timestamp(event_time),
        "ingest_time": format_timestamp(event_time + timedelta(seconds=45 + (index % 4) * 10)),
        "temperature_c": round(21.5 + (index % 4) * 1.4 + rng.random(), 2),
        "vibration_mm_s": round(1.2 + (index % 3) * 0.5 + rng.random() * 0.2, 2),
        "humidity_pct": round(42.0 + (index % 5) * 3.1 + rng.random(), 2),
        "battery_pct": round(78.0 - index * 1.5, 2),
        "status": ["nominal", "nominal", "warning"][index % 3],
        "synthetic_record": SYNTHETIC_MARKER,
        "anomaly_labels": [],
    }


def generate(output_dir: Path, row_count: int, seed: int) -> list[Path]:
    """Generate the IoT telemetry fixture."""
    ensure_minimum_rows(row_count)
    records = [_base_record(index, seed) for index in range(row_count - 1)]
    records.append(
        {
            "device_id": "DEV-999",
            "site_id": "SITE-11",
            "event_time": format_timestamp(datetime(2026, 4, 12, 9, 35, 0)),
            "ingest_time": format_timestamp(datetime(2026, 4, 12, 9, 35, 55)),
            "temperature_c": 118.4,
            "vibration_mm_s": 14.8,
            "humidity_pct": 104.2,
            "battery_pct": 101.0,
            "status": "critical",
            "synthetic_record": SYNTHETIC_MARKER,
            "anomaly_labels": ["out_of_range_reading"],
        }
    )

    path = output_dir / DOMAIN / "telemetry.jsonl"
    return [write_jsonl(path, records)]
