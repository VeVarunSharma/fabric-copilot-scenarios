import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from retail_transactions import build_silver_batch, summarize_sales


class StarterRetailTransactionTests(unittest.TestCase):
    def test_keeps_same_day_business_records(self) -> None:
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
                'business_date': '2026-05-03',
                'arrival_date': '2026-05-04',
                'ingest_sequence': 1,
            },
        ]

        batch = build_silver_batch(records, batch_date='2026-05-04')

        self.assertEqual(['A100'], [item['transaction_id'] for item in batch])
        self.assertFalse(batch[0]['is_late_arrival'])

    def test_summarize_sales_totals_matching_records(self) -> None:
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
            {'transaction_count': 2, 'gross_sales_cents': 1200},
            summarize_sales(batch),
        )


if __name__ == '__main__':
    unittest.main()
