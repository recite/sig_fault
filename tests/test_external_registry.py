"""Check external identities and use of the shared matching pipeline."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import external_registry as external  # noqa: E402
import i4r_registry as registry  # noqa: E402
import pilot  # noqa: E402


class ExternalTests(unittest.TestCase):
    def test_wrong_inventory_link_is_not_an_alias(self):
        row = dict(
            original_doi="10.1234/wrong",
            original_journal_doi="10.1234/right",
            identity_relationship="mislinked_original",
            identity_decision_evidence="Primary report introduction",
        )
        self.assertEqual(external.original_dois(row), {"10.1234/right"})
        row["identity_relationship"] = "same_work_version"
        self.assertEqual(
            external.original_dois(row), {"10.1234/wrong", "10.1234/right"}
        )

    def test_duplicate_reports_share_one_original_without_losing_metadata(self):
        base = dict.fromkeys(registry.ARTICLE_FIELDS, "") | dict(
            article_id="a",
            doi="10.1234/a",
            title="A study",
            identity_verified="pending",
            retracted="unknown",
        )
        verified = base | dict(
            publication_date="2010-01-01", identity_verified="yes", retracted="no"
        )
        result = external.merge_article(base, verified)
        self.assertEqual(result["publication_date"], "2010-01-01")
        self.assertEqual(result["identity_verified"], "yes")
        with self.assertRaises(ValueError):
            external.merge_article(
                verified, verified | dict(publication_date="2011-01-01")
            )

    def test_fresh_failed_collection_keeps_history_missing(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            article = dict(article_id="a", doi="10.1234/a", publication_year="2010")
            with (
                patch.object(external, "DATA", folder),
                patch.object(external.sources, "DATA", folder),
                patch.object(external.sources, "CACHE", folder / "cache"),
                patch.object(external, "opencitations_targets", return_value=[article]),
                patch.object(
                    external.oc_validation,
                    "fetch_links",
                    side_effect=TimeoutError("unavailable"),
                ),
                patch.object(external.time, "sleep"),
            ):
                pilot.write_csv(folder / "articles.csv", [article], list(article))
                external.opencitations_fetch()
                coverage = pilot.read_csv(folder / "opencitations/coverage.csv")
                self.assertEqual(coverage[0]["complete"], "no")
                self.assertEqual(
                    pilot.read_csv(folder / "opencitations/citations.csv"), []
                )

    def test_citation_panel_preserves_missing_and_ambiguous_dates(self):
        articles = [
            dict(article_id=a, doi="10.1234/" + a, publication_year="2010")
            for a in ["observed", "missing"]
        ]
        edges = [
            dict(
                paper_id="observed",
                oci=str(i),
                cited="doi:10.1234/observed",
                citing=citing,
                creation=year,
                timespan="",
            )
            for i, (citing, year) in enumerate(
                [
                    ("omid:1 doi:10.1234/citing", "2011"),
                    ("omid:2 doi:10.1234/citing", "2011"),
                    ("omid:3", "2012"),
                    ("omid:3", "2013"),
                    ("omid:4", ""),
                ]
            )
        ]
        coverage = [
            dict(
                paper_id="observed",
                doi="10.1234/observed",
                complete="yes",
                records=5,
                reported_count=5,
            )
        ]
        works, panel, complete = external.opencitations_panel(
            articles, edges, coverage, 2013
        )
        self.assertEqual(complete, {"observed"})
        self.assertEqual([r["citations"] for r in panel], [0, 1, 0, 0])
        self.assertEqual(len(works), 3)
        self.assertEqual(
            {r["date_status"] for r in works}, {"dated", "undated", "conflicting_years"}
        )
        self.assertFalse(any(r["article_id"] == "missing" for r in panel))

    def test_citation_panel_rejects_changed_identity_and_empty_completion(self):
        article = dict(article_id="a", doi="10.1234/a", publication_year="2010")
        row = dict(paper_id="a", doi="10.1234/other", complete="no")
        with self.assertRaisesRegex(ValueError, "DOI changed"):
            external.opencitations_panel([article], [], [row])
        row.update(doi="10.1234/a", complete="yes", records=0, reported_count=0)
        with self.assertRaisesRegex(ValueError, "empty records"):
            external.opencitations_panel([article], [], [row])

    def test_external_directory_runs_real_matcher_and_completeness_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)

            def write(name, rows, fields):
                pilot.write_csv(root / name, rows, fields)

            def article(aid):
                return dict.fromkeys(registry.ARTICLE_FIELDS, "") | dict(
                    article_id=aid,
                    title="Research study " + aid,
                    doi="10.98765/" + aid,
                    journal_id="S1",
                    publication_year="2010",
                    publication_date="2010-05-01",
                    indexed_publication_year="2010",
                    indexed_publication_date="2010-05-01",
                    type="article",
                    identity_verified="yes",
                    retracted="no",
                )

            treated, control = article("treated"), article("control")
            write("articles.csv", [treated], registry.ARTICLE_FIELDS)
            write("control_articles.csv", [control], registry.ARTICLE_FIELDS)
            event = dict.fromkeys(registry.EVENT_FIELDS, "") | dict(
                event_id="event",
                warning_id="warning",
                article_id="treated",
                year="2015",
                date_precision="year",
                error_verified="yes",
                material="yes",
                publicity_verified="yes",
                already_retracted="no",
            )
            write("events.csv", [event], registry.EVENT_FIELDS)
            rows = []
            for aid, post in [("treated", 20), ("control", 15)]:
                rows += [
                    dict(article_id=aid, year=year, citations=value, status="complete")
                    for year, value in [(2013, 10), (2014, 12), (2016, post)]
                ]
            write("citations.csv", rows, ["article_id", "year", "citations", "status"])
            cmd = [
                sys.executable,
                str(Path(pilot.ROOT) / "scripts/i4r_match.py"),
                "--data-dir",
                str(root),
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            self.assertEqual(pilot.read_csv(root / "analysis_panel.csv"), [])
            exclusions = pilot.read_csv(root / "match_exclusions.csv")
            self.assertTrue(
                all(r["reason"] == "incomplete_risk_set_retrieval" for r in exclusions)
            )
            write(
                "risk_set_retrieval.csv",
                [
                    dict(
                        event_id="event",
                        status="complete",
                        query_filter=registry.risk_filter(treated),
                    )
                ],
                ["event_id", "status", "query_filter"],
            )
            subprocess.run(cmd, check=True, capture_output=True)
            panel = [
                r
                for r in pilot.read_csv(root / "analysis_panel.csv")
                if r["horizon"] == "1"
            ]
            self.assertEqual(len(panel), 4)
            counts = {
                (r["article_id"], int(r["event_time"])): float(r["citations"])
                for r in panel
            }
            self.assertEqual(
                (counts["treated", 1] - counts["treated", -1])
                - (counts["control", 1] - counts["control", -1]),
                5,
            )


if __name__ == "__main__":
    unittest.main()
