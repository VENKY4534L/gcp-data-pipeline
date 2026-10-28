"""Unit tests for the local transformation step."""
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from transform import transform_dataframe  # noqa: E402


class TransformTests(unittest.TestCase):
    def test_trims_text_and_drops_invalid_rows(self):
        frame = pd.DataFrame([
            {"record_id": 1, "customer": "  Asha ", "amount": "10.50",
             "event_date": "2026-01-01", "region": " South "},
            {"record_id": 2, "customer": "", "amount": "3",
             "event_date": "2026-01-02", "region": "West"},
            {"record_id": 3, "customer": "Raj", "amount": "bad",
             "event_date": "2026-01-03", "region": "East"},
        ])
        result = transform_dataframe(frame)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["customer"], "Asha")
        self.assertEqual(result.iloc[0]["region"], "South")

    def test_deduplicates_record_ids(self):
        frame = pd.DataFrame([
            {"record_id": 1, "customer": "A", "amount": 10,
             "event_date": "2026-01-01", "region": "South"},
            {"record_id": 1, "customer": "A duplicate", "amount": 12,
             "event_date": "2026-01-02", "region": "South"},
        ])
        result = transform_dataframe(frame)
        self.assertEqual(len(result), 1)

    def test_missing_required_column_raises(self):
        frame = pd.DataFrame([{"record_id": 1, "customer": "A"}])
        with self.assertRaises(ValueError):
            transform_dataframe(frame)


if __name__ == "__main__":
    unittest.main()
