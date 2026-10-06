"""Source discrepancies must reconstruct observed count differences exactly."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import nieuwenhuis_diagnostics as diagnostics  # noqa: E402


class DecompositionTests(unittest.TestCase):
    def test_dates_filters_and_unmatched_records_have_distinct_contributions(self):
        shared = dict(
            paper_id="nw_1",
            wos_year="2011",
            openalex_year="2010",
            openalex_type="article",
            openalex_before_original_date="no",
            presence="both",
        )
        links = [
            shared,
            shared | dict(openalex_type="book-chapter"),
            shared | dict(openalex_before_original_date="yes"),
            shared | dict(presence="wos_only", wos_year="2010"),
            shared | dict(presence="openalex_only", openalex_year="2011"),
        ]
        raw = [
            dict(
                article_id="1",
                year="2011",
                doi="",
                duplicate="FALSE",
                false_link="FALSE",
            )
        ]
        edge = dict(
            paper_id="nw_1",
            publication_year="2010",
            doi="",
            type="article",
            reference_verified="yes",
            duplicate_of="",
            before_original_date="no",
            citing_work_id="W1",
            target_work_id="W0",
        )
        panel = [
            dict(
                paper_id="nw_1",
                year="2010",
                flag="1",
                wos="1",
                openalex="2",
                status="complete",
            ),
            dict(
                paper_id="nw_1",
                year="2011",
                flag="1",
                wos="4",
                openalex="1",
                status="complete",
            ),
            dict(
                paper_id="nw_2",
                year="2010",
                flag="0",
                wos="9",
                openalex="",
                status="missing_history",
            ),
        ]
        result = diagnostics.decompose(panel, links, raw, [edge])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["shared_year_shift"], 1)
        self.assertEqual(result[0]["wos_only_doi"], -1)
        self.assertEqual(result[0]["openalex_no_doi"], 1)
        self.assertEqual(result[1]["shared_year_shift"], -1)
        self.assertEqual(result[1]["shared_type_exclusion"], -1)
        self.assertEqual(result[1]["shared_predate_exclusion"], -1)
        self.assertEqual(result[1]["openalex_only_doi"], 1)
        self.assertEqual(result[1]["wos_no_doi"], -1)

    def test_window_crossings_and_zero_counts(self):
        panel = [
            dict(
                paper_id="nw_1",
                year="2015",
                flag="0",
                wos="0",
                openalex="1",
                status="complete",
            )
        ]
        link = dict(
            paper_id="nw_1",
            wos_year="2016",
            openalex_year="2015",
            openalex_type="review",
            openalex_before_original_date="no",
            presence="both",
        )
        result = diagnostics.decompose(panel, [link], [], [])
        self.assertEqual(result[0]["shared_year_shift"], 1)

    def test_mismatched_counts_fail_instead_of_becoming_residual(self):
        panel = [
            dict(
                paper_id="nw_1",
                year="2015",
                flag="0",
                wos="0",
                openalex="1",
                status="complete",
            )
        ]
        with self.assertRaisesRegex(ValueError, "does not reproduce"):
            diagnostics.decompose(panel, [], [], [])

    def test_links_outside_paired_cohort_fail(self):
        with self.assertRaisesRegex(ValueError, "outside complete paired cohort"):
            diagnostics.decompose([], [dict(paper_id="nw_2")], [], [])


class LinkReviewTests(unittest.TestCase):
    def test_only_verified_typos_are_reconciled_and_source_doi_survives(self):
        old = dict(
            paper_id="nw_1",
            doi="10.1/typo",
            wos_year="2011",
            openalex_year="",
            presence="wos_only",
        )
        new = dict(
            paper_id="nw_1",
            doi="10.1/correct",
            wos_year="",
            openalex_year="2011",
            presence="openalex_only",
        )
        review = dict(
            paper_id="nw_1",
            wos_doi="10.1/typo",
            openalex_doi="10.1/correct",
            classification="doi_transcription_error",
            source_url="https://publisher.example/article",
            evidence="Publisher-confirmed exact title and year",
        )
        result = diagnostics.reconcile_links([old, new], [review])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["wos_original_doi"], "10.1/typo")
        self.assertEqual(result[0]["doi"], "10.1/correct")
        self.assertEqual(result[0]["presence"], "both")
        self.assertEqual(
            len(
                diagnostics.reconcile_links(
                    [old, new], [review | dict(classification="translation")]
                )
            ),
            2,
        )
        with self.assertRaisesRegex(ValueError, "lacks source evidence"):
            diagnostics.reconcile_links([old, new], [review | dict(source_url="")])

    def test_correction_cannot_merge_already_shared_link(self):
        old = dict(
            paper_id="nw_1",
            doi="10.1/typo",
            wos_year="2011",
            openalex_year="",
            presence="wos_only",
        )
        new = dict(
            paper_id="nw_1",
            doi="10.1/correct",
            wos_year="2011",
            openalex_year="2011",
            presence="both",
        )
        review = dict(
            paper_id="nw_1",
            wos_doi="10.1/typo",
            openalex_doi="10.1/correct",
            classification="doi_transcription_error",
        )
        with self.assertRaisesRegex(ValueError, "unique unmatched pair"):
            diagnostics.reconcile_links([old, new], [review])


class DateTests(unittest.TestCase):
    def test_both_publication_years_are_required_for_date_explanation(self):
        link = dict(wos_year="2012", openalex_year="2011")
        both = dict(status="verified", online_date="2011-12-01", print_date="2012-02")
        self.assertEqual(
            diagnostics.classify_dates(link, both), "openalex_online_wos_print"
        )
        self.assertEqual(
            diagnostics.classify_dates(link, both | dict(print_date="")),
            "incomplete_dates",
        )
        self.assertEqual(diagnostics.classify_dates(link, {}), "metadata_unavailable")
        reverse = dict(wos_year="2011", openalex_year="2012")
        self.assertEqual(
            diagnostics.classify_dates(reverse, both), "wos_online_openalex_print"
        )

    def test_partial_dates_are_preserved(self):
        self.assertEqual(
            diagnostics.date_string(
                {"published-online": {"date-parts": [[2010, 2]]}}, "published-online"
            ),
            "2010-02",
        )
        self.assertEqual(diagnostics.date_string({}, "published-online"), "")


if __name__ == "__main__":
    unittest.main()
