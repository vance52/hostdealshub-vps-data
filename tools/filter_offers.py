#!/usr/bin/env python3
"""Filter the verified VPS snapshot without third-party dependencies."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "vps_offers.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="CSV snapshot path")
    parser.add_argument("--provider", help="case-insensitive provider substring")
    parser.add_argument("--currency", help="exact currency code, such as USD")
    parser.add_argument("--max-price", type=Decimal, help="maximum numeric price in the row currency")
    parser.add_argument("--format", choices=("table", "csv", "json"), default="table")
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def numeric_price(row: dict[str, str]) -> Decimal | None:
    try:
        return Decimal(row.get("price", ""))
    except InvalidOperation:
        return None


def filter_rows(rows: list[dict[str, str]], args: argparse.Namespace) -> list[dict[str, str]]:
    selected = []
    for row in rows:
        if args.provider and args.provider.casefold() not in row.get("provider", "").casefold():
            continue
        if args.currency and args.currency.upper() != row.get("currency", "").upper():
            continue
        if args.max_price is not None:
            price = numeric_price(row)
            if price is None or price > args.max_price:
                continue
        selected.append(row)
    return sorted(selected, key=lambda row: (row.get("provider", ""), numeric_price(row) or Decimal("Infinity"), row.get("title", "")))


def print_table(rows: list[dict[str, str]]) -> None:
    columns = ("provider", "title", "price", "currency", "billing_period", "source_url")
    if not rows:
        print("No matching verified offers.")
        return
    widths = {column: len(column) for column in columns}
    for row in rows:
        for column in columns:
            widths[column] = min(68, max(widths[column], len(row.get(column, ""))))
    print("  ".join(column.ljust(widths[column]) for column in columns))
    print("  ".join("-" * widths[column] for column in columns))
    for row in rows:
        print("  ".join(row.get(column, "")[: widths[column]].ljust(widths[column]) for column in columns))


def main() -> None:
    args = parse_args()
    rows = filter_rows(load_rows(args.data), args)
    if args.format == "json":
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
        print()
    elif args.format == "csv":
        if rows:
            writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    else:
        print_table(rows)


if __name__ == "__main__":
    main()
