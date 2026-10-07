"""Behavioral checks for the citation-source bridge."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import nieuwenhuis as nw  # noqa: E402
import pilot  # noqa: E402


class IdentityTests(unittest.TestCase):
    def test_overloaded_locators_are_parsed_by_journal(self):
        base = dict(
            journal="Neuron",
            cohort="2009",
            year_volume="2009",
            issue="24-Dec",
            page="914",
            link="64-6",
        )
        self.assertEqual(nw.locator(base)["volume"], "64")
        self.assertEqual(nw.locator(base)["issue"], "6")
        jn = base | dict(journal="Journal of Neuroscience", link="49")
        self.assertEqual(nw.locator(jn)["volume"], "29")
        self.assertEqual(nw.locator(jn)["issue"], "49")
        modern = base | dict(cohort="2010", issue="", locator_volume="65", link="")
        self.assertEqual(nw.locator(modern)["volume"], "65")
        self.assertEqual(nw.locator(modern)["issue"], "")

    def test_nature_suffix_prevents_same_page_in_wrong_volume(self):
        row = dict(
            journal="Nature",
            cohort="2009",
            year_volume="2009",
            issue="17-Dec",
            page="916",
            link="8389",
        )
        source = nw.locator(row)
        work = {
            "DOI": "10.1038/nature08538",
            "container-title": ["Nature"],
            "page": "916-922",
            "published-print": {"date-parts": [[2009, 10]]},
        }
        self.assertFalse(nw.matches(work, source))
        self.assertTrue(
            nw.matches(work | {"DOI": "10.1038/nature08389", "page": "915-919"}, source)
        )

    def test_internal_and_abbreviated_pages(self):
        self.assertTrue(nw.page_contains("13074-80", "13076/13077"))
        self.assertFalse(nw.page_contains("13074-80", "13076/13081"))
        self.assertFalse(nw.page_contains("e10001", "10001"))
        self.assertFalse(nw.page_contains("31-33", ""))

    def test_print_year_and_issue_are_required(self):
        source = dict(
            journal="Journal of Neuroscience",
            year="2009",
            volume="29",
            issue="49",
            page="15410",
            expected_doi="",
        )
        work = {
            "container-title": ["The Journal of Neuroscience"],
            "volume": "29",
            "issue": "49",
            "page": "15409-15418",
            "published-print": {"date-parts": [[2009]]},
        }
        self.assertTrue(nw.matches(work, source))
        self.assertFalse(nw.matches(work | {"issue": "48"}, source))
        self.assertFalse(
            nw.matches(work | {"published-print": {"date-parts": [[2010]]}}, source)
        )


class BridgeTests(unittest.TestCase):
    def test_counts_preserve_missing_histories_and_shared_year_disagreement(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = root / "data/nieuwenhuis"
            history = []
            for aid in range(1, 154):
                for year in range(2009, 2016):
                    history.append(
                        dict(
                            article_id=aid,
                            year=year,
                            flag=int(aid == 1),
                            cohort=2009,
                            journal="Journal",
                            citations=int(aid == 1 and year == 2011),
                        )
                    )
            pilot.write_csv(root / "data/derived/panel.csv", history, list(history[0]))
            raw = [
                dict(
                    article_id=1,
                    doi="10.1/shared",
                    duplicate="FALSE",
                    false_link="FALSE",
                    year=2011,
                )
            ]
            pilot.write_csv(root / "data/derived/raw.csv", raw, list(raw[0]))
            edge = dict(
                paper_id="nw_1",
                target_work_id="W0",
                citing_work_id="W1",
                doi="10.1/shared",
                publication_year="2010",
                type="article",
                reference_verified="yes",
                duplicate_of="",
                before_original_date="no",
            )
            pilot.write_csv(
                data / "citation_edges.csv",
                [
                    edge,
                    edge | dict(paper_id="nw_999", doi="10.1/outside"),
                    edge | dict(paper_id="nw_2", doi="10.1/incomplete"),
                ],
                list(edge),
            )
            ids = [
                dict(
                    paper_id=pid, doi="10.1/target", identity_status="verified_locator"
                )
                for pid in ["nw_1", "nw_2", "nw_999"]
            ]
            pilot.write_csv(data / "identities.csv", ids, list(ids[0]))
            pilot.write_csv(
                data / "coverage.csv",
                [
                    dict(
                        paper_id=pid,
                        complete="no" if pid == "nw_2" else "yes",
                        target_doi="10.1/target",
                    )
                    for pid in ["nw_1", "nw_2", "nw_999"]
                ],
                ["paper_id", "complete", "target_doi"],
            )
            with patch.object(nw, "DATA", data), patch.object(
                pilot, "ROOT", root
            ), patch.object(nw, "import_pilot"):
                nw.compare()
            panel = pilot.read_csv(data / "paired_panel.csv")
            lookup = {(r["article_id"], r["year"]): r for r in panel}
            self.assertEqual(lookup["1", "2010"]["openalex"], "1")
            self.assertEqual(lookup["1", "2012"]["openalex"], "0")
            self.assertEqual(lookup["2", "2012"]["openalex"], "")
            self.assertEqual(len(panel), 153 * 7)
            overlap = pilot.read_csv(data / "doi_overlap.csv")
            self.assertEqual(len(overlap), 1)
            self.assertEqual(overlap[0]["presence"], "both")
            self.assertEqual(overlap[0]["year_agrees"], "false")
            status = json.loads((data / "status.json").read_text())
            self.assertFalse(status["full_bridge_available"])
            self.assertEqual(status["complete_comparison"], 0)

    def test_completed_history_is_bound_to_verified_target_doi(self):
        record = dict(complete="yes", target_doi="10.1/old")
        identity = dict(doi="10.1/old", identity_status="verified_locator")
        self.assertTrue(nw.history_complete(record, identity))
        self.assertFalse(nw.history_complete(record, identity | dict(doi="10.1/new")))
        self.assertFalse(
            nw.history_complete(record, identity | dict(identity_status="unresolved"))
        )

    def test_duplicate_year_conflicts_block_only_affected_bridge_window(self):
        edge = dict(
            paper_id="nw_1",
            doi="10.1/citing",
            publication_year="2010",
            type="article",
            before_original_date="no",
        )
        conflict = nw.duplicate_checks([edge, edge | dict(publication_year="2011")])
        self.assertEqual(conflict[0]["bridge_review_required"], "yes")
        later = nw.duplicate_checks(
            [edge | dict(publication_year="2020"), edge | dict(publication_year="2021")]
        )
        self.assertEqual(later[0]["bridge_review_required"], "no")
        types = nw.duplicate_checks([edge, edge | dict(type="editorial")])
        self.assertEqual(types[0]["bridge_review_required"], "yes")

    def test_canonical_duplicate_resolution_moves_one_count_without_changing_raw(self):
        base = dict(
            paper_id="nw_1",
            doi="10.1/citing",
            publication_year="2010",
            publication_date="2010-02-01",
            type="article",
            before_original_date="no",
            reference_verified="yes",
            target_work_id="W0",
        )
        edges = [
            base | dict(citing_work_id="W1", duplicate_of=""),
            base
            | dict(
                citing_work_id="W2",
                duplicate_of="W1",
                publication_date="2011-02-01",
                publication_year="2011",
            ),
        ]
        review = dict(
            paper_id="nw_1",
            doi="10.1/citing",
            work_ids="W1;W2",
            canonical_work_id="W2",
            publication_date="2011-02-01",
            type="article",
        )
        actual = nw.resolve_duplicate_edges(edges, [review])
        selected = nw.eligible_edges(actual, {"article", "review"})
        self.assertEqual([r["publication_year"] for r in selected], ["2011"])
        self.assertEqual(edges[0]["duplicate_of"], "")
        self.assertEqual(
            nw.duplicate_checks(actual, [review])[0]["bridge_review_required"], "no"
        )
        for invalid in [
            review | dict(canonical_work_id="W3"),
            review | dict(work_ids="W1;W2;W3"),
            review | dict(publication_date="2012-01-01"),
        ]:
            with self.assertRaises(ValueError):
                nw.resolve_duplicate_edges(edges, [invalid])
        with self.assertRaises(ValueError):
            nw.resolve_duplicate_edges(edges, [review, review])

    def test_type_and_invalid_link_exclusions(self):
        edge = dict(
            reference_verified="yes",
            duplicate_of="",
            before_original_date="no",
            citing_work_id="W1",
            target_work_id="W0",
            type="article",
        )
        variants = [
            edge,
            edge | dict(type="book-chapter"),
            edge | dict(duplicate_of="W2"),
            edge | dict(before_original_date="yes"),
            edge | dict(citing_work_id="W0"),
            edge | dict(reference_verified="no"),
        ]
        self.assertEqual(nw.eligible_edges(variants, {"article", "review"}), [edge])


if __name__ == "__main__":
    unittest.main()
