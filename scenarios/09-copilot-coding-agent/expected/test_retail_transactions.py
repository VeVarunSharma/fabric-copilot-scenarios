import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from retail_transactions import build_silver_batch, summarize_sales


class ExpectedRetailTransactionTests(unittest.TestCase):
    def test_keeps_late_arrivals_within_grace_window(self) -> None:
        records = [
            {
                'transaction_id': 'A100',
                'store_id': 'SEA-01',
                'amount_cents': 1200,
                'business_date': '2026-05-04',
                'arrival_date': '2026-05-04',
                'ingest_sequence': 1,
            },
            {
                'transaction_id': 'A101',
                'store_id': 'SEA-01',
                'amount_cents': 900,
                'business_date': '2026-05-02',
                'arrival_date': '2026-05-04',
                'ingest_sequence': 1,
            },
            {
                'transaction_id': 'A102',
                'store_id': 'SEA-01',
                'amount_cents': 500,
                'business_date': '2026-05-01',
                'arrival_date': '2026-05-04',
                'ingest_sequence': 1,
            },
            {
                'transaction_id': 'A103',
                'store_id': 'SEA-01',
                'amount_cents': 400,
                'business_date': '2026-05-05',
                'arrival_date': '2026-05-04',
                'ingest_sequence': 1,
            },
        ]

        batch = build_silver_batch(records, batch_date='2026-05-04', late_arrival_days=2)

        self.assertEqual(['A100', 'A101'], [item['transaction_id'] for item in batch])
        flags = {item['transaction_id']: item['is_late_arrival'] for item in batch}
        self.assertEqual({'A100': False, 'A101': True}, flags)

    def test_replayed_transaction_id_keeps_highest_ingest_sequence(self) -> None:
        batch = build_silver_batch(
            [
                {
                    'transaction_id': 'B200',
                    'store_id': 'PDX-02',
                    'amount_cents': 500,
                    'business_date': '2026-05-04',
                    'arrival_date': '2026-05-04',
                    'ingest_sequence': 1,
                },
                {
                    'transaction_id': 'B200',
                    'store_id': 'PDX-02',
                    'amount_cents': 650,
                    'business_date': '2026-05-04',
                    'arrival_date': '2026-05-04',
                    'ingest_sequence': 3,
                },
                {
                    'transaction_id': 'B201',
                    'store_id': 'PDX-02',
                    'amount_cents': 700,
                    'business_date': '2026-05-04',
                    'arrival_date': '2026-05-04',
                    'ingest_sequence': 2,
                },
            ],
            batch_date='2026-05-04',
        )

        self.assertEqual(
            [
                {
                    'transaction_id': 'B200',
                    'store_id': 'PDX-02',
                    'amount_cents': 650,
                    'business_date': '2026-05-04',
                    'arrival_date': '2026-05-04',
                    'ingest_sequence': 3,
                    'is_late_arrival': False,
                },
                {
                    'transaction_id': 'B201',
                    'store_id': 'PDX-02',
                    'amount_cents': 700,
                    'business_date': '2026-05-04',
                    'arrival_date': '2026-05-04',
                    'ingest_sequence': 2,
                    'is_late_arrival': False,
                },
            ],
            batch,
        )
        self.assertEqual(
            {'transaction_count': 2, 'gross_sales_cents': 1350},
            summarize_sales(batch),
        )


if __name__ == '__main__':
    unittest.main()
