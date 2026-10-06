import csv
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_inventories as inventory  # noqa: E402


class InventoryTests(unittest.TestCase):
    def test_identifiers_are_not_invented(self):
        self.assertEqual(inventory.doi("https://doi.org/10.1234/ABC"), "10.1234/abc")
        for value in [
            None,
            "NA",
            "thekeep.eiu.edu/theses/4783",
            "0.1162/0033553053327524",
            "10.1234/with space",
        ]:
            self.assertEqual(inventory.doi(value), "")

    def test_full_source_preserves_conflicting_assessments_and_unknown_dates(self):
        fields = [
            "doi_o",
            "doi_r",
            "alt_identifier_o",
            "alt_identifier_r",
            "title_o",
            "title_r",
            "year_o",
            "year_r",
            "type",
            "outcome",
            "source",
            "outcome_quote",
            "outcome_quote_source",
        ]
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        for label in ["mixed", "failed"]:
            row = dict.fromkeys(fields, "NA")
            row.update(
                doi_o="10.1234/a",
                doi_r="10.1234/b",
                type="replication",
                outcome=label,
                year_r="2024",
            )
            writer.writerow(row)
        rows = inventory.flora_records(out.getvalue().encode("utf-8-sig"))
        self.assertEqual(len(rows), 2)
        self.assertEqual([r["source_outcome"] for r in rows], ["mixed", "failed"])
        self.assertTrue(
            all(
                r["material_error_status"] == "not_adjudicated"
                and r["first_public_disclosure"] == ""
                for r in rows
            )
        )
        self.assertNotEqual(rows[0]["record_id"], rows[1]["record_id"])

    def test_missing_labels_are_not_clean_tests(self):
        raw = (
            "Source,title,year,journal,Error,DecisionError\n"
            "10.1234/a,A,2010,J,TRUE,TRUE\n"
            "10.1234/A,A,2010,J,NA,NA\n"
            "10.1234/b,B,2011,J,FALSE,FALSE\n"
        ).encode()
        rows, n = inventory.statcheck_articles(raw)
        self.assertEqual(n, 3)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["tests"], 2)
        self.assertEqual(rows[0]["decision_inconsistent_tests"], 1)
        self.assertEqual(rows[0]["missing_decision_labels"], 1)
        with self.assertRaises(ValueError):
            inventory.statcheck_articles(raw.replace(b"FALSE", b"maybe"))

    def test_cross_source_overlap_does_not_create_independent_papers(self):
        data = dict(
            flora=[dict(original_doi="10.1234/a")] * 2,
            fred=[dict(original_doi="10.1234/a"), dict(original_doi="")],
            statcheck=[dict(original_doi="10.1234/b")],
        )
        rows = inventory.crosswalk(data, {"10.1234/a"})
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["flora_rows"], 2)
        self.assertEqual(rows[0]["fred_effects"], 1)
        self.assertEqual(rows[0]["in_i4r_registry"], "yes")


if __name__ == "__main__":
    unittest.main()
