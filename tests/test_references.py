import copy
import importlib
import unittest

from pybtex.database import Entry, Person

references = importlib.import_module("scripts.references.02_validate")


class BibliographyTests(unittest.TestCase):
    def test_wrong_metadata_is_detected(self):
        entry = Entry(
            "article",
            fields=dict(
                doi="10.1234/a",
                title="A test",
                journal="Journal",
                year="2021",
                volume="2",
                number="1",
                pages="1--9",
            ),
            persons={"author": [Person("Jane Doe")]},
        )
        work = {
            "DOI": "10.1234/a",
            "title": ["A test"],
            "container-title": ["Journal"],
            "published": {"date-parts": [[2021]]},
            "volume": "2",
            "issue": "1",
            "page": "1-9",
            "author": [{"given": "Jane", "family": "Doe"}],
        }
        self.assertTrue(all(references.fields_match(entry, work).values()))
        for field, replacement in [("title", "Wrong title"), ("year", "2020")]:
            changed = copy.deepcopy(entry)
            changed.fields[field] = replacement
            self.assertFalse(references.fields_match(changed, work)[field])
        changed = copy.deepcopy(work)
        changed["author"].append({"given": "John", "family": "Roe"})
        self.assertFalse(references.fields_match(entry, changed)["authors_in_order"])

    def test_comments_and_optional_citation_arguments(self):
        source = r"""\citep[see][p. 3]{a,b} \citet*{c} % \citep{ignored}
        escaped \% \citep{d}"""
        self.assertEqual(references.citation_keys(source), {"a", "b", "c", "d"})


if __name__ == "__main__":
    unittest.main()
