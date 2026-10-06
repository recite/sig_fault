"""Annual-rollup support, missingness and vintage checks."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from i4r_aggregate import annual_counts, cached_works  # noqa: E402


class AnnualCountsTest(unittest.TestCase):
    def work(self, bins):
        return {"updated_date": "2026-10-01T12:00:00", "counts_by_year": bins}

    def test_supported_zeros_and_excluded_years(self):
        work = self.work(
            [
                {"year": 2015, "cited_by_count": 12},
                {"year": 2025, "cited_by_count": 8},
                {"year": 2026, "cited_by_count": 4},
            ]
        )
        counts = annual_counts(work, "2026-10-05T10:00:00Z")
        self.assertEqual(set(counts), set(range(2017, 2026)))
        self.assertEqual(counts[2025], 8)
        self.assertEqual(counts[2024], 0)

    def test_empty_list_is_observed_zero(self):
        self.assertEqual(sum(annual_counts(self.work([]), "2026-10-05").values()), 0)

    def test_unavailable_is_not_zero(self):
        for work in [self.work(None), {"updated_date": "2026-10-01"}]:
            with self.assertRaisesRegex(ValueError, "unavailable"):
                annual_counts(work, "2026-10-05")

    def test_stale_update_blocks_completed_year_assumption(self):
        work = self.work([]) | {"updated_date": "2025-12-01"}
        with self.assertRaisesRegex(ValueError, "vintage"):
            annual_counts(work, "2026-10-05")

    def test_future_update_is_invalid(self):
        work = self.work([]) | {"updated_date": "2026-10-07"}
        with self.assertRaisesRegex(ValueError, "vintage"):
            annual_counts(work, "2026-10-05")

    def test_malformed_counts_are_rejected(self):
        for count in [-1, 1.5, True, None, "2"]:
            with self.subTest(count=count), self.assertRaises(ValueError):
                annual_counts(
                    self.work([{"year": 2025, "cited_by_count": count}]), "2026-10-05"
                )

    def test_duplicate_and_future_bins_are_rejected(self):
        for years in [[2025, 2025], [2027], [True]]:
            with self.subTest(years=years), self.assertRaises(ValueError):
                annual_counts(
                    self.work([{"year": y, "cited_by_count": 1} for y in years]),
                    "2026-10-05",
                )

    def test_window_uses_retrieval_vintage(self):
        work = {"updated_date": "2024-06-01", "counts_by_year": []}
        self.assertEqual(set(annual_counts(work, "2024-07-01")), set(range(2015, 2024)))

    def test_unprovenanced_objects_are_not_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "identities"
            folder.mkdir()
            (folder / "work.json").write_text('{"id":"https://openalex.org/W1"}')
            with patch("i4r_aggregate.sources.CACHE", Path(tmp)):
                self.assertEqual(cached_works(), {})


if __name__ == "__main__":
    unittest.main()
