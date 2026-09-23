#!/usr/bin/env python3
"""Download the public HostDealsHub snapshot after conservative validation."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "offers.json"
SOURCE_URL = "https://hostdealshub.com/data/offers.json"


def main() -> None:
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "hostdealshub-vps-data/1.0 (+https://hostdealshub.com/)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Snapshot returned HTTP {response.status}")
        payload = json.load(response)

    if payload.get("meta", {}).get("brand") != "HostDealsHub":
        raise ValueError("Snapshot brand did not match HostDealsHub")
    offers = payload.get("offers")
    providers = payload.get("providers")
    if not isinstance(offers, list) or not offers:
        raise ValueError("Snapshot did not contain any verified offers")
    if not isinstance(providers, list) or not providers:
        raise ValueError("Snapshot did not contain provider status records")
    if payload.get("meta", {}).get("offer_count") != len(offers):
        raise ValueError("Snapshot offer_count did not match the offers array")
    for index, offer in enumerate(offers):
        for field in ("provider", "price", "currency", "source_url", "fetched_at"):
            if not offer.get(field):
                raise ValueError(f"Offer {index} is missing {field}")

    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    temporary = OUTPUT.with_suffix(".json.tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(OUTPUT)
    print(f"Validated and wrote {len(offers)} offers from {SOURCE_URL}")


if __name__ == "__main__":
    main()
