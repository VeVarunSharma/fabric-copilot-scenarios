"""Financial reporting fixture generation."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from .common import SYNTHETIC_MARKER, ensure_minimum_rows, format_date, make_rng, money, write_csv

DOMAIN = "financial-reporting"
ACCOUNT_FIELDS = [
    "account_id",
    "account_name",
    "account_type",
    "reporting_line",
    "normal_balance",
    "synthetic_record",
]
LEDGER_FIELDS = [
    "entry_id",
    "posting_date",
    "account_id",
    "cost_center",
    "journal_source",
    "debit_amount",
    "credit_amount",
    "description",
    "synthetic_record",
    "anomaly_label",
]


def _account_rows() -> list[dict[str, str]]:
    return [
        {
            "account_id": "ACCT-1000",
            "account_name": "Cash Clearing",
            "account_type": "asset",
            "reporting_line": "balance_sheet",
            "normal_balance": "debit",
            "synthetic_record": SYNTHETIC_MARKER,
        },
        {
            "account_id": "ACCT-1100",
            "account_name": "Trade Receivables",
            "account_type": "asset",
            "reporting_line": "balance_sheet",
            "normal_balance": "debit",
            "synthetic_record": SYNTHETIC_MARKER,
        },
        {
            "account_id": "ACCT-2100",
            "account_name": "Accounts Payable",
            "account_type": "liability",
            "reporting_line": "balance_sheet",
            "normal_balance": "credit",
            "synthetic_record": SYNTHETIC_MARKER,
        },
        {
            "account_id": "ACCT-4000",
            "account_name": "Product Revenue",
            "account_type": "revenue",
            "reporting_line": "income_statement",
            "normal_balance": "credit",
            "synthetic_record": SYNTHETIC_MARKER,
        },
        {
            "account_id": "ACCT-5000",
            "account_name": "Cost of Sales",
            "account_type": "expense",
            "reporting_line": "income_statement",
            "normal_balance": "debit",
            "synthetic_record": SYNTHETIC_MARKER,
        },
        {
            "account_id": "ACCT-6100",
            "account_name": "Operating Expense",
            "account_type": "expense",
            "reporting_line": "income_statement",
            "normal_balance": "debit",
            "synthetic_record": SYNTHETIC_MARKER,
        },
    ]


def _ledger_row(index: int, seed: int) -> dict[str, str]:
    rng = make_rng(seed, 501 + index)
    posting_date = datetime(2026, 5, 1) + timedelta(days=index)
    account_cycle = [
        ("ACCT-1000", "cash_receipt"),
        ("ACCT-1100", "invoice"),
        ("ACCT-4000", "revenue"),
        ("ACCT-5000", "cogs"),
        ("ACCT-6100", "expense"),
        ("ACCT-2100", "ap"),
    ]
    account_id, journal_source = account_cycle[index % len(account_cycle)]
    amount = 180.0 + index * 34.5 + rng.random() * 20.0
    is_debit = account_id in {"ACCT-1000", "ACCT-1100", "ACCT-5000", "ACCT-6100"}
    return {
        "entry_id": f"GL-{8000 + index}",
        "posting_date": format_date(posting_date),
        "account_id": account_id,
        "cost_center": f"CC-{10 + (index % 4)}",
        "journal_source": journal_source,
        "debit_amount": money(amount if is_debit else 0.0),
        "credit_amount": money(0.0 if is_debit else amount),
        "description": [
            "monthly settlement",
            "channel billing",
            "product sale",
            "inventory release",
            "operations spend",
            "supplier accrual",
        ][index % 6],
        "synthetic_record": SYNTHETIC_MARKER,
        "anomaly_label": "none",
    }


def generate(output_dir: Path, row_count: int, seed: int) -> list[Path]:
    """Generate the financial reporting fixtures."""
    ensure_minimum_rows(row_count)
    accounts = _account_rows()
    ledger_entries = [_ledger_row(index, seed) for index in range(row_count - 1)]
    ledger_entries.append(
        {
            "entry_id": "GL-8999",
            "posting_date": "2026-05-19",
            "account_id": "ACCT-9999",
            "cost_center": "CC-99",
            "journal_source": "manual_adjustment",
            "debit_amount": money(250.00),
            "credit_amount": money(0.00),
            "description": "unmapped workshop adjustment",
            "synthetic_record": SYNTHETIC_MARKER,
            "anomaly_label": "orphan_account",
        }
    )

    domain_dir = output_dir / DOMAIN
    return [
        write_csv(domain_dir / "accounts.csv", ACCOUNT_FIELDS, accounts),
        write_csv(domain_dir / "general_ledger.csv", LEDGER_FIELDS, ledger_entries),
    ]
