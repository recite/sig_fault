"""Check external identities and use of the shared matching pipeline."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
