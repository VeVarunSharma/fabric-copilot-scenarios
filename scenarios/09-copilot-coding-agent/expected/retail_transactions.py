from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, List

Transaction = Dict[str, object]


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _normalize_record(record: Transaction, business_date: date, is_late_arrival: bool) -> Transaction:
    return {
        'transaction_id': str(record['transaction_id']),
        'store_id': str(record['store_id']),
        'amount_cents': int(record['amount_cents']),
        'business_date': business_date.isoformat(),
        'arrival_date': str(record['arrival_date']),
        'ingest_sequence': int(record['ingest_sequence']),
        'is_late_arrival': is_late_arrival,
    }


def build_silver_batch(
    records: Iterable[Transaction],
    batch_date: str,
    late_arrival_days: int = 2,
) -> List[Transaction]:
    """Keep current arrivals, allow a grace window, and deduplicate replays."""
    target_date = _parse_date(batch_date)
    latest_by_transaction_id: Dict[str, Transaction] = {}

    for record in records:
        arrival_date = _parse_date(str(record['arrival_date']))
        if arrival_date != target_date:
            continue

        business_date = _parse_date(str(record['business_date']))
        age_in_days = (target_date - business_date).days
        if age_in_days < 0 or age_in_days > late_arrival_days:
            continue

        normalized = _normalize_record(
            record,
            business_date=business_date,
            is_late_arrival=age_in_days > 0,
        )
        transaction_id = str(normalized['transaction_id'])
        current = latest_by_transaction_id.get(transaction_id)
        if current is None or int(normalized['ingest_sequence']) > int(current['ingest_sequence']):
            latest_by_transaction_id[transaction_id] = normalized

    return sorted(
        latest_by_transaction_id.values(),
        key=lambda item: (str(item['store_id']), str(item['transaction_id'])),
    )


def summarize_sales(records: Iterable[Transaction]) -> Dict[str, int]:
    items = list(records)
    return {
        'transaction_count': len(items),
        'gross_sales_cents': sum(int(item['amount_cents']) for item in items),
    }
