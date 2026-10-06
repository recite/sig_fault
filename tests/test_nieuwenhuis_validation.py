"""Behavioral checks for the third-source citation-link comparison."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import nieuwenhuis_validation as validation  # noqa: E402


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.edge = dict(
            paper_id="nw_1",
            oci="1-2",
            citing="omid:br/1 doi:10.1/extra",
            cited="omid:br/2 doi:10.1/original",
            creation="",
            timespan="",
        )
        self.link = dict(paper_id="nw_1", doi="10.1/extra", presence="openalex_only")

    def test_target_identity_completeness_and_duplicate_gates(self):
        validation.validate_response([self.edge], 1, "10.1/original")
        with self.assertRaisesRegex(ValueError, "target DOI"):
            validation.validate_response([self.edge], 1, "10.1/wrong")
        with self.assertRaisesRegex(ValueError, "length"):
            validation.validate_response([self.edge], 2, "10.1/original")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validation.validate_response([self.edge, self.edge], 2, "10.1/original")

    def test_undated_links_can_validate_presence_without_imputing_a_year(self):
        coverage = [dict(paper_id="nw_1", complete="yes")]
        result = validation.crosswalk([self.link], [self.edge], coverage)[0]
        self.assertEqual(result["validation_status"], "present")
        self.assertEqual(result["opencitations_dates"], "")
        self.assertEqual(result["matching_records"], 1)

    def test_partial_retrieval_does_not_become_evidence_of_absence(self):
        result = validation.crosswalk(
            [self.link], [], [dict(paper_id="nw_1", complete="no")]
        )
        self.assertEqual(result[0]["validation_status"], "not_collected")
        result = validation.crosswalk(
            [self.link], [], [dict(paper_id="nw_1", complete="yes")]
        )
        self.assertEqual(result[0]["validation_status"], "not_found")

    def test_matching_preserves_target_identity_and_all_known_aliases(self):
        coverage = [dict(paper_id="nw_1", complete="yes")]
        result = validation.crosswalk(
            [self.link], [self.edge | dict(paper_id="nw_2")], coverage
        )
        self.assertEqual(result[0]["validation_status"], "not_found")
        alias = self.edge | dict(citing="omid:br/1 doi:10.1/other doi:10.1/EXTRA")
        result = validation.crosswalk([self.link], [alias], coverage)
        self.assertEqual(result[0]["validation_status"], "present")
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
