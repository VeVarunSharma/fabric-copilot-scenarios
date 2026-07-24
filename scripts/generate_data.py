"""CLI for deterministic synthetic fixture generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from datasets.generators import DOMAIN_GENERATORS, DEFAULT_ROW_COUNT, DEFAULT_SEED, generate_all
from datasets.generators.common import default_output_dir


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate deterministic synthetic datasets for local demos."
    )
    parser.add_argument(
        "--output-dir",
        default=str(default_output_dir()),
        help="Root directory where domain folders will be written.",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROW_COUNT,
        help="Base row count for each fact-like fixture. Minimum 10.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Deterministic seed used by all generators.",
    )
    parser.add_argument(
        "--domain",
        action="append",
        choices=sorted(DOMAIN_GENERATORS),
        help="Optional domain to generate. Repeat to generate multiple domains.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Generate one or more synthetic datasets."""
    args = parse_args(argv)
    output_dir = Path(args.output_dir).resolve()
    written_files = generate_all(
        output_dir=output_dir,
        row_count=args.rows,
        seed=args.seed,
        domains=args.domain,
    )
    print(
        f"Generated {len(written_files)} files for "
        f"{len(args.domain or DOMAIN_GENERATORS)} domain(s) under {output_dir}"
    )
    for path in written_files:
        print(path.relative_to(output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
