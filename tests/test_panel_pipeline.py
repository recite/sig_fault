import importlib
import unittest

parse_summary = importlib.import_module("scripts.panel.02_assessments").parse_summary


def table(rows):
    return "\n".join([r"\label{tb:summary}", *rows, r"\end{tabular}"])


class HistoricalPanelTests(unittest.TestCase):
    def test_commented_papers_and_unavailable_diagnostics_are_not_controls(self):
        text = table(
            [
                r"\citet{A} & JOP & CP & 2 & 3 & 6 & General & u+t & "
                r"x & n.a. & n.a. & n.a & x \\",
                r"\citet{B} & AJPS & CP & 2 & 3 & 6 & General & u+t & "
                r"x & & x & & x \\",
                r"% \citet{Excluded} & AJPS & CP & 2 & 3 & 6 & General & u+t & "
                r"x & x & x & x & x \\",
            ]
        )
        rows = parse_summary(text)
        self.assertEqual([r["citation_key"] for r in rows], ["A", "B"])
        self.assertEqual([r["primary_flag"] for r in rows], ["unknown", "flagged"])
        self.assertEqual(rows[0]["placebo_p_above_05"], "not_applicable")

    def test_unrecognized_marks_stop_extraction(self):
        text = table(
            [
                r"\citet{A} & JOP & CP & 2 & 3 & 6 & General & u+t & "
                r"x & ? & x & x & x \\",
            ]
        )
        with self.assertRaisesRegex(ValueError, "Unrecognized diagnostic"):
            parse_summary(text)


if __name__ == "__main__":
    unittest.main()
