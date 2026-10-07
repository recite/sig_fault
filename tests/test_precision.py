"""Check the paired-count variance independently of fitted model artifacts."""

import importlib
import unittest

precision = importlib.import_module("scripts.meta.02_precision")


class PrecisionTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            dict(paper_id="a", flag=0, before=10, after=20),
            dict(paper_id="b", flag=0, before=20, after=10),
            dict(paper_id="c", flag=1, before=10, after=10),
            dict(paper_id="d", flag=1, before=10, after=20),
        ]

    def test_scale_invariance(self):
        original, _ = precision.diagnose(self.rows)
        scaled, _ = precision.diagnose(
            [
                dict(r, before=r["before"] * 100, after=r["after"] * 100)
                for r in self.rows
            ]
        )
        for key in ["estimate", "se"]:
            self.assertAlmostEqual(original[key], scaled[key])

    def test_reversing_comparison(self):
        original, _ = precision.diagnose(self.rows)
        reversed_result, influences = precision.diagnose(
            [dict(r, flag=1 - r["flag"]) for r in self.rows]
        )
        self.assertAlmostEqual(original["estimate"], -reversed_result["estimate"])
        self.assertAlmostEqual(original["se"], reversed_result["se"])
        self.assertAlmostEqual(sum(r["variance_share"] for r in influences), 1)

    def test_zero_pair_has_no_information(self):
        original, _ = precision.diagnose(self.rows)
        extra, _ = precision.diagnose(
            self.rows + [dict(paper_id="e", flag=1, before=0, after=0)]
        )
        self.assertEqual(original, extra)

    def test_invalid_histories_fail(self):
        for changes in [{"before": -1}, {"after": float("nan")}, {"flag": 2}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                precision.diagnose([dict(self.rows[0], **changes)] + self.rows[1:])
        with self.assertRaises(ValueError):
            precision.diagnose(self.rows + [self.rows[0]])

    def test_pair_integrity(self):
        rows = [dict(id="a", year=2010, flag=1, citations=2)]
        with self.assertRaises(ValueError):
            precision.paired(rows, "id", "year", "flag", 2010, 2012)
        rows.append(dict(id="a", year=2012, flag=0, citations=3))
        with self.assertRaises(ValueError):
            precision.paired(rows, "id", "year", "flag", 2010, 2012)
        rows[1]["flag"] = 1
        self.assertEqual(
            len(precision.paired(rows, "id", "year", "flag", 2010, 2012)), 1
        )
        with self.assertRaises(ValueError):
            precision.paired(rows + [rows[0]], "id", "year", "flag", 2010, 2012)


if __name__ == "__main__":
    unittest.main()
