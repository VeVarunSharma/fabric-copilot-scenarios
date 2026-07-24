from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, List

Transaction = Dict[str, object]


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def build_silver_batch(records: Iterable[Transaction], batch_date: str) -> List[Transaction]:
    """Keep only transactions whose business date matches the batch date."""
    target_date = _parse_date(batch_date)
    output: List[Transaction] = []

    for record in records:
        business_date = _parse_date(str(record['business_date']))
        if business_date != target_date:
            continue

        output.append(
            {
                'transaction_id': str(record['transaction_id']),
                'store_id': str(record['store_id']),
                'amount_cents': int(record['amount_cents']),
                'business_date': business_date.isoformat(),
                'arrival_date': str(record['arrival_date']),
                'ingest_sequence': int(record['ingest_sequence']),
                'is_late_arrival': False,
            }
        )

    return sorted(output, key=lambda item: (str(item['store_id']), str(item['transaction_id'])))


def summarize_sales(records: Iterable[Transaction]) -> Dict[str, int]:
    items = list(records)
    return {
        'transaction_count': len(items),
        'gross_sales_cents': sum(int(item['amount_cents']) for item in items),
    }
