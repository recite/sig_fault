"""Checks for publication units, complete coverage, and paper-level diagnostics."""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lal_citations as lal
import pilot


class LalTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        self.patcher = patch.object(lal, "DATA", self.path)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.write("papers.csv", [{"paper_id": "p"}])
        self.write(
            "identities.csv", [{"paper_id": "p", "publication_date": "2022-01-01"}]
        )

    def write(self, name, rows):
        pilot.write_csv(self.path / name, rows, list(rows[0]))

    def edge(self, id_, type_="article", doi="", year="2025"):
        return dict.fromkeys(lal.FIELDS, "") | dict(
            paper_id="p",
            target_work_id="W0",
            citing_work_id=id_,
            doi=doi,
            publication_date=year + "-01-01",
            publication_year=year,
            type=type_,
            reference_verified="yes",
        )

    def prepare(self, rows, count=None, complete="yes"):
        self.write("citation_edges.csv", rows)
        self.write(
            "coverage.csv",
            [
                {
                    "paper_id": "p",
                    "api_count": len(rows) if count is None else count,
                    "complete": complete,
                }
            ],
        )

    def test_primary_counts_articles_and_reviews_and_collapses_book_sensitivity(self):
        rows = [
            self.edge("W1"),
            self.edge("W2", "review"),
            self.edge("W3", "book-chapter", "10.1093/9780197816479.003.0001"),
            self.edge("W4", "book-chapter", "10.1093/9780197816479.003.0002"),
            self.edge("W5", "preprint"),
            self.edge("W6", "paratext"),
            self.edge("W7", year="2021"),
        ]
        self.prepare(rows)
        with contextlib.redirect_stdout(io.StringIO()):
            lal.panel()
        panel = pilot.read_csv(self.path / "panel.csv")
        self.assertEqual(
            [r["citation_year"] for r in panel], ["2022", "2023", "2024", "2025"]
        )
        self.assertEqual([r["citations"] for r in panel], ["0", "0", "0", "2"])
        self.assertEqual(panel[-1]["citations_broad"], "5")
        self.assertEqual(panel[-1]["citations_broad_book_collapsed"], "4")
        self.assertEqual(panel[-1]["citations_all_types"], "6")

    def test_incomplete_or_mismatched_frame_cannot_become_zeros(self):
        for count, complete in [(2, "yes"), (1, "no")]:
            self.prepare([self.edge("W1")], count=count, complete=complete)
            with self.assertRaises(ValueError):
                lal.panel()

    def test_repeated_edges_and_unverified_links_are_rejected(self):
        for rows in [
            [self.edge("W1"), self.edge("W1")],
            [self.edge("W1") | {"reference_verified": "no"}],
        ]:
            self.prepare(rows)
            with self.assertRaises(ValueError):
                lal.panel()

    def test_book_family_requires_same_isbn(self):
        self.assertEqual(
            lal.book_family("10.1093/9780197816479.003.0002"),
            lal.book_family("10.1093/9780197816479.001.0001"),
        )
        self.assertNotEqual(
            lal.book_family("10.1093/9780197816479.003.0002"),
            lal.book_family("10.1093/9780197820209.003.0001"),
        )
        self.assertEqual(lal.book_family("10.1093/poq/nfab001"), "")

    def test_reviewed_journal_record_overrides_misattributed_dissertation_doi(self):
        a = self.edge("W1", "dissertation", "10.1093/jleo/ewaa020", year="2014")
        b = self.edge("W2", "article", "10.1093/jleo/ewaa020", year="2025")
        b["duplicate_of"] = "W1"
        self.write(
            "citation_identity_decisions.csv",
            [{"paper_id": "p", "doi": a["doi"], "canonical_work_id": "W2"}],
        )
        result = lal.adjudicate_duplicates([a, b])
        self.assertEqual(result[0]["duplicate_of"], "W2")
        self.assertEqual(result[1]["duplicate_of"], "")
        self.assertEqual(a["duplicate_of"], "")
        self.assertEqual(b["duplicate_of"], "W1")
        with self.assertRaises(ValueError):
            lal.adjudicate_duplicates([a])

    def test_any_design_classification_keeps_dower_and_excludes_invalid_alt_tf(self):
        with patch.object(lal, "DATA", pilot.ROOT / "data/lal"):
            papers = {r["paper_id"]: r for r in pilot.read_csv(lal.DATA / "papers.csv")}
            checks = {
                r["design_id"]: r
                for r in pilot.read_csv(lal.DATA / "diagnostic_checks.csv")
            }
        self.assertEqual(papers["iv_Dower2018a"]["analytic_positive"], "1")
        self.assertEqual(sum(int(r["analytic_positive"]) for r in papers.values()), 55)
        self.assertEqual(checks["Alt2015"]["tf_eligible"], "0")
        self.assertAlmostEqual(
            float(checks["Alt2015"]["used_ar_p"]), 0.174675820839, places=10
        )


if __name__ == "__main__":
    unittest.main()
