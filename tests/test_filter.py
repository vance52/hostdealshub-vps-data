import argparse
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from filter_offers import filter_rows, load_rows  # noqa: E402


class FilterOffersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = load_rows(ROOT / "data" / "vps_offers.csv")

    def test_snapshot_contains_rows(self) -> None:
        self.assertGreater(len(self.rows), 0)

    def test_snapshot_count_and_provenance(self) -> None:
        payload = json.loads((ROOT / "data" / "offers.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["meta"]["offer_count"], len(payload["offers"]))
        self.assertTrue(all(row.get("source_url") and row.get("fetched_at") for row in payload["offers"]))

    def test_provider_filter(self) -> None:
        args = argparse.Namespace(provider="DigitalOcean", currency=None, max_price=None)
        selected = filter_rows(self.rows, args)
        self.assertTrue(selected)
        self.assertTrue(all(row["provider"] == "DigitalOcean" for row in selected))

    def test_max_price_filter(self) -> None:
        args = argparse.Namespace(provider=None, currency="USD", max_price=Decimal("5"))
        selected = filter_rows(self.rows, args)
        self.assertTrue(selected)
        self.assertTrue(all(Decimal(row["price"]) <= Decimal("5") for row in selected))


if __name__ == "__main__":
    unittest.main()
