import importlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import research_pipeline as pipeline

identities = importlib.import_module("scripts.rpp.02_identify")
disclosures = importlib.import_module("scripts.rpp.03_disclosures")
citations = importlib.import_module("scripts.rpp.05_citations")


class ReceiptTests(unittest.TestCase):
    def test_receipts_can_use_a_shared_analysis_directory(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
            pipeline, "ROOT", Path(tmp)
        ), patch.object(pipeline, "fingerprint", return_value={}):
            with patch.object(pipeline.subprocess, "check_output", return_value="abc"):
                run = pipeline.Run(
                    "meta",
                    "01_synthesize",
                    __file__,
                    True,
                    data_dir=Path(tmp) / "data/meta",
                )
            self.assertEqual(
                run.receipt_path, Path(tmp) / "data/meta/receipts/01_synthesize.json"
            )

    def test_transitive_staleness_even_with_unchanged_outputs(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
            pipeline, "ROOT", Path(tmp)
        ):
            root = Path(tmp)
            code, output = root / "code.py", root / "output.txt"
            code.write_text("original code")
            output.write_text("unchanged output")
            parent = dict(
                status="complete",
                inputs=[],
                outputs=[pipeline.fingerprint(output)],
                code=[pipeline.fingerprint(code)],
                parents=[],
                checks=[dict(passed=True)],
            )
            pipeline.write_json(root / "parent.json", parent)
            child = dict(
                status="complete",
                inputs=[],
                outputs=[],
                code=[],
                parents=[pipeline.fingerprint(root / "parent.json")],
                checks=[dict(passed=True)],
            )
            pipeline.write_json(root / "child.json", child)
            pipeline.verify_receipt(root / "child.json")
            code.write_text("changed code")
            with self.assertRaisesRegex(ValueError, "Stale or changed"):
                pipeline.verify_receipt(root / "child.json")

    def test_failed_receipt_is_not_reusable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text(json.dumps(dict(status="failed")))
            with self.assertRaisesRegex(ValueError, "incomplete"):
                pipeline.verify_receipt(path)

    def test_duplicate_or_missing_join_keys_fail(self):
        for rows in [[dict(id="")], [dict(id="1"), dict(id="1")]]:
            with self.assertRaises(ValueError):
                pipeline.unique(rows, ["id"])


class IdentityAndTimingTests(unittest.TestCase):
    def test_locator_does_not_override_conflicting_title(self):
        source = {
            "Journal.O": "JPSP",
            "Volume.O": "95",
            "Issue.O": "5",
            "Pages.O": "1019-28",
            "Study.Title.O": "The face of success",
        }
        work = {
            "DOI": "10.x/other",
            "title": ["Accuracy and awareness"],
            "volume": "95",
            "issue": "5",
            "page": "1019-1028",
            "published-print": {"date-parts": [[2008]]},
        }
        match = identities.candidate(work, source, "")
        self.assertTrue(match["exact_locator"])
        self.assertFalse(match["accepted"])

    def test_legacy_update_is_only_a_report_candidate(self):
        self.assertTrue(
            disclosures.report_candidate("file_updated", "/Payne.final.report.pdf")
        )
        self.assertFalse(
            disclosures.report_candidate(
                "file_added", "/Replication_Report_Pre-Data_Collection.pdf"
            )
        )
        self.assertFalse(
            disclosures.report_candidate("made_public", "/Final.report.pdf")
        )


class CitationTests(unittest.TestCase):
    def work(self, id="W2", year=2012, doi="https://doi.org/10.x/citing"):
        return dict(
            id="https://openalex.org/" + id,
            doi=doi,
            publication_year=year,
            publication_date=f"{year}-01-01",
            type="article",
            title="Citing work",
            referenced_works=["https://openalex.org/W1"],
        )

    def normalize(self, works, canonical=None):
        return citations.normalize_history(
            dict(paper_id="a", doi="10.x/original"),
            dict(
                id="https://openalex.org/W1",
                doi="https://doi.org/10.x/original",
                publication_date="2008-01-01",
            ),
            works,
            canonical,
        )

    def test_duplicate_doi_does_not_double_count(self):
        rows = self.normalize([self.work(), self.work(id="W3")])
        self.assertEqual(sum(not x["duplicate_of"] for x in rows), 1)

    def test_conflicting_year_requires_verified_canonical_record(self):
        works = [self.work(), self.work(id="W3", year=2014)]
        with self.assertRaisesRegex(ValueError, "canonical"):
            self.normalize(works)
        rows = self.normalize(works, {"10.x/citing": "https://openalex.org/W3"})
        kept = [x for x in rows if not x["duplicate_of"]]
        self.assertEqual(kept[0]["publication_year"], 2014)
        with self.assertRaisesRegex(ValueError, "canonical"):
            self.normalize(works, {"10.x/citing": "https://openalex.org/W99"})

    def test_reference_and_date_failures_are_excluded(self):
        work = self.work(year=2007)
        work["referenced_works"] = []
        row = self.normalize([work])[0]
        self.assertIn("reference_not_verified", row["exclusion_reason"])
        self.assertIn("outside_date_window", row["exclusion_reason"])

    def test_incomplete_history_is_missing_not_zero(self):
        papers = [
            dict(paper_id="a", journal="J", role="successful"),
            dict(paper_id="b", journal="J", role="unsuccessful"),
        ]
        coverage = [
            dict(paper_id="a", complete=True, reported_records=0),
            dict(paper_id="b", complete=False),
        ]
        panel = citations.make_panel(papers, coverage, [])
        self.assertTrue(all(x["citations"] == 0 for x in panel if x["paper_id"] == "a"))
        self.assertTrue(
            all(x["citations"] == "" for x in panel if x["paper_id"] == "b")
        )

    def test_completed_panel_rejects_missing_edges(self):
        with self.assertRaisesRegex(ValueError, "count does not match"):
            citations.make_panel(
                [dict(paper_id="a")],
                [dict(paper_id="a", complete=True, reported_records=1)],
                [],
            )


class MatchTests(unittest.TestCase):
    def test_synthetic_fit_predicts_on_the_same_count_scale(self):
        matching = importlib.import_module("scripts.rpp.06_match")
        papers = [
            dict(
                paper_id=str(i),
                doi=f"10.x/{i}",
                journal="J",
                role="successful" if i == 0 else "external_control",
            )
            for i in range(4)
        ]
        levels = [5, 0, 10, 100]
        panel = [
            dict(paper_id=str(i), year=y, citations=levels[i], status="complete")
            for i in range(4)
            for y in range(2010, 2015)
        ]
        coverage = [
            dict(paper_id=p["paper_id"], is_retracted=False, target_type="article")
            for p in papers
        ]
        fit = matching.select_matches(papers, panel, coverage)[2][0]
        self.assertAlmostEqual(fit["synthetic_pre_mean"], 5, places=3)

    def test_post_outcomes_do_not_enter_matching(self):
        matching = importlib.import_module("scripts.rpp.06_match")
        papers = [
            dict(paper_id=x, doi="10.x/" + x, journal="J", role=role)
            for x, role in [
                ("target", "successful"),
                ("a", "external_control"),
                ("b", "external_control"),
                ("c", "external_control"),
            ]
        ]
        panel = [
            dict(
                paper_id=p["paper_id"],
                year=y,
                citations=i + y - 2010,
                status="complete",
            )
            for i, p in enumerate(papers)
            for y in range(2010, 2020)
        ]
        coverage = [
            dict(paper_id=p["paper_id"], is_retracted=False, target_type="article")
            for p in papers
        ]
        first = matching.select_matches(papers, panel, coverage)
        for row in panel:
            if row["year"] >= 2015:
                row["citations"] += 100000
        second = matching.select_matches(papers, panel, coverage)
        self.assertEqual(first, second)
        self.assertAlmostEqual(sum(x["weight"] for x in first[1]), 1)


if __name__ == "__main__":
    unittest.main()
