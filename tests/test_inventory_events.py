import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import inventory_events as events  # noqa: E402


class EventTests(unittest.TestCase):
    def setUp(self):
        self.review = dict(
            record_id="a",
            original_doi="10.1234/wp",
            original_journal_doi="10.1234/article",
        )
        self.metadata = dict(
            record_id="a",
            inventory_doi="10.1234/wp",
            journal_doi="10.1234/article",
            title="Original",
            publication_date="2010-05",
        )
        self.decision = dict(
            record_id="a",
            material_error_verified="yes",
            publicity_verified="yes",
            date="2013",
            date_precision="year",
            date_evidence="Public institutional report",
            date_sources=[
                dict(url="https://example.org", locator="Table 1", sha256="a" * 64)
            ],
            affected_claim="Magnitude",
            original_value="0.2",
            corrected_value="0.1",
            correction_scope="Same model",
            decision_evidence="Table 2",
            limitations="Matching and retraction screen pending",
        )

    def rows(self, decisions=None, metadata=None):
        return events.make_rows(
            [self.review],
            metadata or [self.metadata],
            decisions if decisions is not None else [self.decision],
        )

    def test_year_precision_supports_collection_but_not_effect_estimation(self):
        row = self.rows()[0]
        self.assertEqual(row["ready_for_citation_collection"], "yes")
        self.assertEqual(row["analysis_eligible"], "pending")
        self.assertEqual(row["journal_doi"], "10.1234/article")

    def test_early_disclosure_prevents_two_full_preyears(self):
        row = self.rows([self.decision | dict(date="2012")])[0]
        self.assertEqual(row["ready_for_citation_collection"], "no")
        self.assertIn("too_recent", row["collection_exclusion"])

    def test_pending_review_does_not_become_negative_or_eligible(self):
        row = self.rows([])[0]
        self.assertEqual(row["material_error_verified"], "pending")
        self.assertEqual(row["ready_for_citation_collection"], "no")
        self.assertEqual(row["public_year"], "")

    def test_date_and_consequence_evidence_required(self):
        for change in [
            dict(date="2013-13", date_precision="month"),
            dict(date_sources=[]),
            dict(corrected_value=""),
            dict(material_error_verified="maybe"),
            dict(date="2013-04", date_precision="year"),
        ]:
            with self.assertRaises(ValueError):
                self.rows([self.decision | change])

    def test_unknown_duplicate_and_changed_identities_rejected(self):
        for rows in [
            [self.decision, self.decision],
            [self.decision | dict(record_id="b")],
        ]:
            with self.assertRaises(ValueError):
                self.rows(rows)
        with self.assertRaises(ValueError):
            self.rows(metadata=[self.metadata | dict(journal_doi="10.1234/wrong")])

    def test_incomplete_postyear_excluded(self):
        row = self.rows([self.decision | dict(date="2025")])[0]
        self.assertIn("postyear_unavailable", row["collection_exclusion"])


if __name__ == "__main__":
    unittest.main()
