#!/usr/bin/env python3
"""Export the verified HostDealsHub JSON snapshot to reusable flat files."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SOURCE = DATA_DIR / "offers.json"
CSV_OUTPUT = DATA_DIR / "vps_offers.csv"
PROVIDERS_OUTPUT = DATA_DIR / "providers.md"
CSV_FIELDS = [
    "provider",
    "title",
    "price",
    "currency",
    "billing_period",
    "offer_url",
    "source_url",
    "fetched_at",
    "extraction",
    "valid_until",
    "id",
]


def escape_markdown(value: object) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    offers = payload.get("offers", [])
    providers = payload.get("providers", [])

    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=CSV_FIELDS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for offer in offers:
            writer.writerow({field: offer.get(field, "") for field in CSV_FIELDS})

    generated_at = payload.get("meta", {}).get("generated_at", "not recorded")
    lines = [
        "# Provider source status",
        "",
        f"Snapshot generated at `{escape_markdown(generated_at)}`.",
        "",
        "| Provider | Official source | Checked at | HTTP status | Result | Verified offers |",
        "| --- | --- | --- | ---: | --- | ---: |",
    ]
    for provider in providers:
        source_url = provider.get("source_url", "")
        source_link = f"[official page]({source_url})" if source_url else "not recorded"
        http_status = provider.get("http_status", "not returned")
        lines.append(
            "| {name} | {source} | {checked} | {http_status} | {status} | {count} |".format(
                name=escape_markdown(provider.get("name", "")),
                source=source_link,
                checked=escape_markdown(provider.get("checked_at", "")),
                http_status=escape_markdown(http_status),
                status=escape_markdown(provider.get("status", "")),
                count=escape_markdown(provider.get("offer_count", 0)),
            )
        )
    lines.extend(
        [
            "",
            "A zero count is preserved as data. It does not mean that the provider has no plans; it means this snapshot did not publish a price from that source.",
            "",
        ]
    )
    PROVIDERS_OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {len(offers)} offers to {CSV_OUTPUT.relative_to(ROOT)}")
    print(f"Wrote {len(providers)} provider records to {PROVIDERS_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
