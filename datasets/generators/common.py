"""Shared helpers for deterministic synthetic dataset generation."""

from __future__ import annotations

import csv
import json
import random
from datetime import datetime
from pathlib import Path

DEFAULT_SEED = 4242
DEFAULT_ROW_COUNT = 12
MINIMUM_ROW_COUNT = 10
SYNTHETIC_MARKER = "SYNTHETIC"


def ensure_minimum_rows(row_count: int) -> None:
    """Require enough rows to include the documented anomalies."""
    if row_count < MINIMUM_ROW_COUNT:
        raise ValueError(
            f"row_count must be at least {MINIMUM_ROW_COUNT} to preserve anomalies"
        )


def money(value: float) -> str:
    """Format a currency-like value with stable precision."""
    return f"{value:.2f}"


def format_date(value: datetime) -> str:
    """Return an ISO date string."""
    return value.strftime("%Y-%m-%d")


def format_timestamp(value: datetime) -> str:
    """Return an ISO timestamp string in UTC-like notation."""
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def make_rng(seed: int, offset: int) -> random.Random:
    """Create a deterministic RNG per dataset domain."""
    return random.Random(seed + offset)


def repo_root() -> Path:
    """Resolve the repository root from the generators package."""
    return Path(__file__).resolve().parents[2]


def default_output_dir() -> Path:
    """Return the default output directory for committed fixtures."""
    return repo_root() / "datasets" / "synthetic"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> Path:
    """Write a CSV file with ASCII-safe output and a fixed column order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> Path:
    """Write a JSON Lines file with stable key ordering."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=False))
            handle.write("\n")
    return path
