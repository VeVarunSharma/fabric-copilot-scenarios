"""Deterministic synthetic dataset generators."""

from pathlib import Path

from .common import DEFAULT_ROW_COUNT, DEFAULT_SEED
from .customer_transactions import DOMAIN as CUSTOMER_TRANSACTIONS_DOMAIN
from .customer_transactions import generate as generate_customer_transactions
from .financial_reporting import DOMAIN as FINANCIAL_REPORTING_DOMAIN
from .financial_reporting import generate as generate_financial_reporting
from .healthcare_claims import DOMAIN as HEALTHCARE_CLAIMS_DOMAIN
from .healthcare_claims import generate as generate_healthcare_claims
from .iot_telemetry import DOMAIN as IOT_TELEMETRY_DOMAIN
from .iot_telemetry import generate as generate_iot_telemetry
from .retail_purchases import DOMAIN as RETAIL_PURCHASES_DOMAIN
from .retail_purchases import generate as generate_retail_purchases


DOMAIN_GENERATORS = {
    CUSTOMER_TRANSACTIONS_DOMAIN: generate_customer_transactions,
    HEALTHCARE_CLAIMS_DOMAIN: generate_healthcare_claims,
    RETAIL_PURCHASES_DOMAIN: generate_retail_purchases,
    IOT_TELEMETRY_DOMAIN: generate_iot_telemetry,
    FINANCIAL_REPORTING_DOMAIN: generate_financial_reporting,
}


def generate_all(
    output_dir: Path,
    row_count: int = DEFAULT_ROW_COUNT,
    seed: int = DEFAULT_SEED,
    domains: list[str] | None = None,
) -> list[Path]:
    """Generate one or more synthetic dataset domains."""
    selected_domains = domains or list(DOMAIN_GENERATORS)
    invalid_domains = sorted(set(selected_domains) - set(DOMAIN_GENERATORS))
    if invalid_domains:
        raise ValueError(f"Unsupported domain selection: {', '.join(invalid_domains)}")

    written_files: list[Path] = []
    for domain in selected_domains:
        written_files.extend(DOMAIN_GENERATORS[domain](output_dir, row_count, seed))
    return written_files
