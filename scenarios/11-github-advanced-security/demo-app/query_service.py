"""Safe SQLite query baseline for the disposable CodeQL workshop branch."""

from __future__ import annotations

import sqlite3


def fetch_transactions(
    connection: sqlite3.Connection, customer_id: str
) -> list[tuple[str, int]]:
    cursor = connection.execute(
        """
        SELECT transaction_id, amount_cents
        FROM retail_transactions
        WHERE customer_id = ?
        """,
        (customer_id,),
    )
    return [(str(row[0]), int(row[1])) for row in cursor.fetchall()]
