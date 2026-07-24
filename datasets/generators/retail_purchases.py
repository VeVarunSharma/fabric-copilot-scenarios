"""Retail backbone fixture generation."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from .common import SYNTHETIC_MARKER, ensure_minimum_rows, format_date, format_timestamp, make_rng, money, write_csv

DOMAIN = "retail-purchases"
CUSTOMER_FIELDS = [
    "customer_id",
    "customer_name",
    "loyalty_tier",
    "home_region",
    "signup_date",
    "email_domain",
    "synthetic_record",
]
PRODUCT_FIELDS = [
    "product_id",
    "product_name",
    "category",
    "subcategory",
    "unit_cost",
    "unit_price",
    "is_active",
    "synthetic_record",
]
PURCHASE_FIELDS = [
    "purchase_id",
    "customer_id",
    "product_id",
    "purchase_ts",
    "ingest_ts",
    "quantity",
    "unit_price",
    "store_id",
    "channel",
    "synthetic_record",
    "anomaly_label",
]


def _customer_rows(row_count: int) -> list[dict[str, str]]:
    customer_count = max(6, min(8, (row_count // 2) + 2))
    tiers = ["bronze", "silver", "gold", "platinum"]
    regions = ["north", "south", "east", "west"]
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Riley", "Casey", "Avery", "Parker"]
    last_names = ["Harper", "Quinn", "Sawyer", "Kendall", "Monroe", "Reese", "Bailey", "Lane"]
    return [
        {
            "customer_id": f"RCUST-{100 + index}",
            "customer_name": f"{first_names[index % len(first_names)]} {last_names[index % len(last_names)]}",
            "loyalty_tier": tiers[index % len(tiers)],
            "home_region": regions[index % len(regions)],
            "signup_date": format_date(datetime(2025, 8, 1) + timedelta(days=index * 17)),
            "email_domain": ["example-retail.test", "sample-shop.test"][index % 2],
            "synthetic_record": SYNTHETIC_MARKER,
        }
        for index in range(customer_count)
    ]


def _product_rows(row_count: int) -> list[dict[str, str]]:
    product_count = max(6, min(8, (row_count // 2) + 1))
    categories = [
        ("apparel", "outerwear", "Summit Jacket"),
        ("electronics", "audio", "Pulse Speaker"),
        ("home", "decor", "Harbor Lamp"),
        ("grocery", "beverage", "Cedar Tea"),
    ]
    rows: list[dict[str, str]] = []
    for index in range(product_count):
        category, subcategory, product_name = categories[index % len(categories)]
        base_price = 14.00 + index * 5.50
        unit_cost = 5.60 + index * 2.10
        rows.append(
            {
                "product_id": f"SKU-{1000 + index}",
                "product_name": f"{product_name} {index + 1}",
                "category": category,
                "subcategory": subcategory,
                "unit_cost": money(unit_cost),
                "unit_price": money(base_price),
                "is_active": "true",
                "synthetic_record": SYNTHETIC_MARKER,
            }
        )
    return rows


def _purchase_row(
    index: int,
    customer_ids: list[str],
    product_rows: list[dict[str, str]],
    seed: int,
) -> dict[str, str]:
    rng = make_rng(seed, 301 + index)
    purchase_time = datetime(2026, 3, 2, 10, 0, 0) + timedelta(minutes=index * 23)
    product = product_rows[index % len(product_rows)]
    return {
        "purchase_id": f"PUR-{9000 + index}",
        "customer_id": customer_ids[index % len(customer_ids)],
        "product_id": product["product_id"],
        "purchase_ts": format_timestamp(purchase_time),
        "ingest_ts": format_timestamp(purchase_time + timedelta(minutes=5 + (index % 4))),
        "quantity": str(1 + (index % 4)),
        "unit_price": money(float(product["unit_price"]) + rng.random()),
        "store_id": f"STORE-{1 + (index % 3):02d}",
        "channel": ["store", "online", "pickup"][index % 3],
        "synthetic_record": SYNTHETIC_MARKER,
        "anomaly_label": "none",
    }


def generate(output_dir: Path, row_count: int, seed: int) -> list[Path]:
    """Generate the retail backbone fixtures."""
    ensure_minimum_rows(row_count)
    customers = _customer_rows(row_count)
    products = _product_rows(row_count)
    customer_ids = [row["customer_id"] for row in customers]

    purchases = [
        _purchase_row(index, customer_ids, products, seed) for index in range(row_count - 3)
    ]

    purchases.append(
        {
            "purchase_id": "PUR-9197",
            "customer_id": "",
            "product_id": products[0]["product_id"],
            "purchase_ts": format_timestamp(datetime(2026, 3, 2, 15, 25, 0)),
            "ingest_ts": format_timestamp(datetime(2026, 3, 2, 15, 31, 0)),
            "quantity": "1",
            "unit_price": products[0]["unit_price"],
            "store_id": "STORE-04",
            "channel": "online",
            "synthetic_record": SYNTHETIC_MARKER,
            "anomaly_label": "null_customer_id",
        }
    )
    purchases.append(
        {
            "purchase_id": "PUR-9198",
            "customer_id": customer_ids[1],
            "product_id": products[1]["product_id"],
            "purchase_ts": format_timestamp(datetime(2026, 3, 2, 15, 48, 0)),
            "ingest_ts": format_timestamp(datetime(2026, 3, 2, 15, 53, 0)),
            "quantity": "0",
            "unit_price": products[1]["unit_price"],
            "store_id": "",
            "channel": "store",
            "synthetic_record": SYNTHETIC_MARKER,
            "anomaly_label": "invalid_quantity_zero",
        }
    )
    duplicate_purchase = purchases[1].copy()
    duplicate_purchase["anomaly_label"] = "duplicate_purchase"
    purchases.append(duplicate_purchase)

    domain_dir = output_dir / DOMAIN
    return [
        write_csv(domain_dir / "customers.csv", CUSTOMER_FIELDS, customers),
        write_csv(domain_dir / "products.csv", PRODUCT_FIELDS, products),
        write_csv(domain_dir / "purchases.csv", PURCHASE_FIELDS, purchases),
    ]
