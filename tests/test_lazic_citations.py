"""Citation identity, completeness, and missing-date checks for the Lazic cohort."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lazic_citations as citations  # noqa: E402
import nieuwenhuis_validation as validation  # noqa: E402


class CitationTests(unittest.TestCase):
    def setUp(self):
        self.article = dict(
            article_id="a",
            doi="",
            pmid="123",
            publication_year="2015",
            classification="pseudoreplication",
            flagged="1",
        )
        self.edge = dict(
            paper_id="a",
            oci="1-2",
            citing="omid:br/1 doi:10.1/citing",
            cited="omid:br/2 pmid:123",
            creation="2019",
            timespan="",
        )
        self.coverage = dict(
            paper_id="a",
            doi="",
            scheme="pmid",
            identifier="123",
            reported_count="1",
            records="1",
            undated_records="0",
            complete="yes",
        )

    def test_pmid_targets_are_validated_without_fabricating_a_doi(self):
        validation.validate_response([self.edge], 1, "123", scheme="pmid")
        with self.assertRaisesRegex(ValueError, "target PMID"):
            validation.validate_response([self.edge], 1, "456", scheme="pmid")
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            validation.validate_response([], 0, "123", scheme="title")

    def test_book_screen_does_not_collapse_unrelated_chapters(self):
        a = citations.book_family("doi:10.1007/978-981-97-5730-5_3")
        b = citations.book_family("doi:10.1007/978-981-97-5730-5_7")
        self.assertEqual(a, b)
        self.assertEqual(a, "10.1007/978-981-97-5730-5")
        self.assertEqual(citations.book_family("doi:10.1038/nature19780"), "")
        self.assertEqual(citations.book_family("doi:10.1016/j.test.2019.01978"), "")

    def test_missing_history_is_not_a_zero(self):
        panel, works = citations.panel([self.article], [], [])
        self.assertEqual(works, [])
        self.assertTrue(all(r["citations"] == "" for r in panel))
        self.assertEqual(min(r["year"] for r in panel), 2015)
        panel, _ = citations.panel([self.article], [self.coverage], [self.edge])
        self.assertEqual(sum(r["citations"] for r in panel), 1)
        self.assertEqual(next(r["citations"] for r in panel if r["year"] == 2016), 0)

    def test_duplicate_identity_edges_count_once_and_conflicts_stay_unassigned(self):
        second = self.edge | dict(oci="3-2", citing="omid:br/3 doi:10.1/citing")
        coverage = self.coverage | dict(records="2", reported_count="2")
        panel, works = citations.panel([self.article], [coverage], [self.edge, second])
        self.assertEqual(len(works), 1)
        self.assertEqual(sum(r["citations"] for r in panel), 1)
        second["creation"] = "2020"
        panel, works = citations.panel([self.article], [coverage], [self.edge, second])
        self.assertEqual(works[0]["date_status"], "conflicting_years")
        self.assertEqual(sum(r["citations"] for r in panel), 0)

    def test_incomplete_or_changed_target_claims_fail(self):
        for coverage in [
            self.coverage | dict(identifier="456"),
            self.coverage | dict(records="0"),
            self.coverage | dict(undated_records="1"),
        ]:
            with self.assertRaises(ValueError):
                citations.panel([self.article], [coverage], [self.edge])
        with self.assertRaises(ValueError):
            citations.panel([self.article], [self.coverage], [])

    def test_undated_edges_remain_in_work_ledger(self):
        panel, works = citations.panel(
            [self.article],
            [self.coverage | dict(undated_records="1")],
            [self.edge | dict(creation="")],
        )
        self.assertEqual(works[0]["date_status"], "undated")
        self.assertEqual(sum(r["citations"] for r in panel), 0)


if __name__ == "__main__":
    unittest.main()
