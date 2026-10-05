"""Behavioral tests for citation sampling and measurement safeguards."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "pilot", Path(__file__).resolve().parents[1] / "scripts/pilot.py"
)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


def edge(index, paper="p", date="2015-01-01"):
    row = dict.fromkeys(pilot.EDGE_FIELDS, "")
    row.update(
        paper_id=paper,
        citing_work_id=f"W{index}",
        target_work_id="W0",
        publication_date=date,
        publication_year=date[:4],
        type="article",
        eligible_type="yes",
        before_original_date="no",
        reference_verified="yes",
        oa_urls="[]",
    )
    return row


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.registry = [{"paper_id": "p", "audit_id": "a", "selected": "TRUE"}]
        self.audits = [
            {
                "audit_id": "a",
                "possible_warning_from": "2011-08-26",
                "public_record_by": "2011-08-26",
            }
        ]

    def test_exact_warning_and_lag_boundaries(self):
        event = self.audits[0]
        self.assertEqual(pilot.period_for("2011-08-25", event), "pre")
        self.assertEqual(pilot.period_for("2011-08-26", event), "transition")
        self.assertEqual(pilot.period_for("2012-08-25", event), "transition")
        self.assertEqual(pilot.period_for("2012-08-26", event), "post")

    def test_uncertain_warning_does_not_contaminate_pre_period(self):
        event = {
            "possible_warning_from": "2021-07-10",
            "public_record_by": "2024-02-17",
        }
        for date in ["2021-07-10", "2022-06-01", "2024-02-17", "2025-02-16"]:
            self.assertEqual(pilot.period_for(date, event), "transition")
        self.assertEqual(pilot.period_for("2025-02-17", event), "post")

    def test_sample_invariant_to_input_order(self):
        rows = [edge(i) for i in range(1, 101)]
        a = pilot.draw_sample(rows, self.registry, self.audits)
        b = pilot.draw_sample(list(reversed(rows)), self.registry, self.audits)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 10)
        self.assertTrue(all(r["conditional_inclusion_probability"] == 0.1 for r in a))

    def test_availability_does_not_determine_sampling(self):
        rows = [edge(i) for i in range(1, 30)]
        before = pilot.draw_sample(rows, self.registry, self.audits)
        for r in rows:
            r["oa_urls"] = '["https://example.org/available.pdf"]'
        after = pilot.draw_sample(rows, self.registry, self.audits)
        self.assertEqual([r["pair_id"] for r in before], [r["pair_id"] for r in after])

    def test_small_strata_are_censused_without_replacement(self):
        rows = [edge(i, date="2010-01-01") for i in range(1, 4)] + [edge(4)]
        sample = pilot.draw_sample(rows, self.registry, self.audits)
        self.assertEqual(len(sample), 4)
        self.assertTrue(
            all(r["conditional_inclusion_probability"] == 1 for r in sample)
        )

    def test_bad_dates_duplicates_and_self_links_stay_out(self):
        rows = [edge(i) for i in range(5)]
        rows[1]["duplicate_of"] = "W0"
        rows[2]["before_original_date"] = "yes"
        rows[3]["eligible_type"] = "no"
        rows[4]["publication_date"] = "2026-01-01"
        self.assertEqual(pilot.draw_sample(rows, self.registry, self.audits), [])

    def test_two_targets_are_two_relationships(self):
        rows = [edge(1), edge(1, paper="q")]
        pilot.unique(rows, ["paper_id", "citing_work_id"])
        with self.assertRaises(ValueError):
            pilot.unique(rows + [edge(1)], ["paper_id", "citing_work_id"])

    def test_metadata_only_xml_is_not_fulltext(self):
        with self.assertRaises(ValueError):
            pilot.xml_text(
                b"<pmc-articleset><article><front/></article></pmc-articleset>"
            )

    def test_doi_in_reference_list_does_not_verify_article_identity(self):
        payload = b'<article><front><article-meta><article-id pub-id-type="doi">10.1/a</article-id></article-meta></front><body><p>Text</p></body><back><ref>10.1/b</ref></back></article>'
        pilot.verify_xml_doi(payload, "10.1/a")
        with self.assertRaises(ValueError):
            pilot.verify_xml_doi(payload, "10.1/b")

    def test_blank_ratings_are_missing_not_negative(self):
        row = dict.fromkeys(pilot.RATING_FIELDS, "") | {
            "pair_id": "p__W1",
            "reader_id": "one",
        }
        pilot.validate_ratings([row], {"p__W1"})
        row["qualification"] = "no"
        with self.assertRaises(ValueError):
            pilot.validate_ratings([row], {"p__W1"})

    def test_reliance_needs_evidence_and_full_text(self):
        row = dict.fromkeys(pilot.RATING_FIELDS, "") | {
            "pair_id": "p__W1",
            "reader_id": "one",
            "valid_link": "yes",
            "fulltext_read": "yes",
            "claim_identified": "yes",
            "relies_on_claim": "yes",
        }
        with self.assertRaises(ValueError):
            pilot.validate_ratings([row], {"p__W1"})
        row.update(evidence_locator="p. 3", evidence_excerpt="Passage")
        pilot.validate_ratings([row], {"p__W1"})

    def test_doi_normalization(self):
        self.assertEqual(
            pilot.normalize_doi(" HTTPS://DOI.ORG/10.1038/NN.2599 "), "10.1038/nn.2599"
        )

    def test_negative_reliance_requires_an_assessable_claim_and_evidence(self):
        row = dict.fromkeys(pilot.RATING_FIELDS, "") | {
            "pair_id": "p__W1",
            "reader_id": "one",
            "relies_on_claim": "no",
        }
        with self.assertRaises(ValueError):
            pilot.validate_ratings([row], {"p__W1"})
        row.update(
            valid_link="yes",
            fulltext_read="yes",
            claim_identified="yes",
            evidence_locator="p. 4",
            evidence_excerpt="Uses a different finding",
        )
        pilot.validate_ratings([row], {"p__W1"})

    def test_graph_edges_require_target_identity_and_reference(self):
        paper = {"paper_id": "p", "doi": "10.1/a", "publication_date": "2009-01-01"}
        target = {"id": "W0", "doi": "https://doi.org/10.1/a"}
        work = {
            "id": "W1",
            "doi": "10.1/b",
            "publication_date": "2015-01-01",
            "publication_year": 2015,
            "type": "article",
            "referenced_works": ["W0"],
        }
        self.assertEqual(
            pilot.normalize_edges(paper, target, [work])[0]["reference_verified"], "yes"
        )
        with self.assertRaises(ValueError):
            pilot.normalize_edges(paper, target | {"doi": "10.1/wrong"}, [work])
        with self.assertRaises(ValueError):
            pilot.normalize_edges(paper, target, [work | {"referenced_works": []}])

    def test_duplicate_dates_cannot_change_sampling_period(self):
        a, b = edge(1), edge(2, date="2010-01-01")
        b["duplicate_of"] = "W1"
        with self.assertRaises(ValueError):
            pilot.draw_sample([a, b], self.registry, self.audits)
        b["publication_date"] = "2016-01-01"
        self.assertEqual(len(pilot.draw_sample([a, b], self.registry, self.audits)), 1)

    def test_context_extraction_keeps_multiple_mentions_and_exact_dois(self):
        payload = b'<article><front/><body><p id="p1">Uses <xref rid="r1 r2">1,2</xref>.</p><p id="p2">Qualifies <xref rid="r1">1</xref>.</p></body><back><ref id="r1"><pub-id pub-id-type="doi">10.1/a</pub-id></ref><ref id="r2"><pub-id pub-id-type="doi">10.1/ab</pub-id></ref></back></article>'
        refs, passages = pilot.citation_passages(payload, "10.1/a")
        self.assertEqual(refs, ["r1"])
        self.assertEqual([p["paragraph_id"] for p in passages], ["p1", "p2"])
        refs, passages = pilot.citation_passages(payload, "10.1/missing")
        self.assertEqual((refs, passages), ([], []))

    def test_frozen_file_cannot_be_replaced_by_changed_live_results(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame.csv"
            pilot.write_frozen_csv(path, [{"id": 1}], ["id"])
            pilot.write_frozen_csv(path, [{"id": 1}], ["id"])
            with self.assertRaises(ValueError):
                pilot.write_frozen_csv(path, [{"id": 2}], ["id"])
            self.assertEqual(pilot.read_csv(path), [{"id": "1"}])

    def test_agreement_uses_paired_initial_ratings_and_keeps_missing_separate(self):
        rows = [
            {"pair_id": "a", "relies_on_claim": "yes", "qualification": "no"},
            {"pair_id": "a", "relies_on_claim": "yes", "qualification": "yes"},
            {"pair_id": "b", "relies_on_claim": "", "qualification": ""},
            {"pair_id": "b", "relies_on_claim": "no", "qualification": ""},
        ]
        result = pilot.agreement(rows)
        self.assertEqual(result["relies_on_claim"]["paired_completed"], 1)
        self.assertEqual(result["relies_on_claim"]["yes_agreement"], 1)
        self.assertEqual(result["qualification"]["exact_agreement"], 0)
        self.assertIsNone(pilot.agreement([])["qualification"]["exact_agreement"])


if __name__ == "__main__":
    unittest.main()
