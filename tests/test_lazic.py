"""Protect the complete audit cohort and the meaning of its classifications."""

import collections
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lazic  # noqa: E402
import pilot  # noqa: E402


class LazicTests(unittest.TestCase):
    def setUp(self):
        self.raw = lazic.survey()
        self.metadata = pilot.read_csv(lazic.DATA / "metadata.csv")

    def test_complete_cohort_retains_unclear_and_missing_dois(self):
        rows = lazic.build_rows(self.raw, self.metadata)
        self.assertEqual(len(rows), 200)
        self.assertEqual(
            collections.Counter(r["classification"] for r in rows),
            {"pseudoreplication": 91, "correct_analysis": 45, "unclear": 64},
        )
        self.assertEqual(sum(r["flagged"] == "" for r in rows), 64)
        self.assertEqual(
            {r["pmid"] for r in rows if not r["doi"]}, {"22648583", "25031729"}
        )
        self.assertTrue(
            all(r["full_baseline_year"] == "yes" for r in rows if r["flagged"])
        )

    def test_join_fails_on_loss_duplicates_and_unrequested_records(self):
        for metadata in [
            self.metadata[:-1],
            self.metadata + self.metadata[:1],
            self.metadata + [self.metadata[0] | {"pmid": "99999999"}],
        ]:
            with self.assertRaises(ValueError):
                lazic.build_rows(self.raw, metadata)
        duplicate = [dict(r) for r in self.metadata]
        duplicate[1]["doi"] = duplicate[0]["doi"]
        with self.assertRaises(ValueError):
            lazic.build_rows(self.raw, duplicate)

    def test_dates_preserve_precision_and_validate_calendar(self):
        for text, expected in [
            ("<Year>2015</Year>", "2015"),
            ("<Year>2015</Year><Month>Sep</Month>", "2015-09"),
            ("<MedlineDate>2015 Sep-Oct</MedlineDate>", "2015"),
            ("<Year>2015</Year><Month>9</Month><Day>6</Day>", "2015-09-06"),
        ]:
            self.assertEqual(
                lazic.publication_date(ET.fromstring("<Date>" + text + "</Date>")),
                expected,
            )
        with self.assertRaises(ValueError):
            lazic.publication_date(
                ET.fromstring("<D><Year>2015</Year><Month>13</Month></D>")
            )

    def test_pubmed_uses_online_date_and_keeps_correction_links(self):
        payload = b"""<PubmedArticleSet><PubmedArticle><MedlineCitation>
          <PMID>1</PMID><Article><ArticleTitle>A <i>nested</i> title</ArticleTitle>
          <Journal><Title>Journal</Title><JournalIssue><PubDate><Year>2016</Year>
          </PubDate></JournalIssue></Journal>
          <ArticleDate DateType="Electronic"><Year>2015</Year>
          <Month>12</Month><Day>15</Day></ArticleDate></Article>
          <CommentsCorrectionsList><CommentsCorrections RefType="ErratumIn">
          <PMID>2</PMID></CommentsCorrections></CommentsCorrectionsList>
          </MedlineCitation><PubmedData><ArticleIdList>
          <ArticleId IdType="doi">10.1234/TEST</ArticleId>
          </ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>"""
        rows, notices = lazic.parse_pubmed(payload, "source.xml", "checksum")
        self.assertEqual(rows[0]["publication_date"], "2015-12-15")
        self.assertEqual(rows[0]["issue_year"], "2016")
        self.assertEqual(rows[0]["issue_date"], "2016")
        self.assertEqual(rows[0]["electronic_date"], "2015-12-15")
        self.assertEqual(rows[0]["title"], "A nested title")
        self.assertEqual(rows[0]["doi"], "10.1234/test")
        self.assertEqual(notices[0]["relation"], "ErratumIn")
        self.assertEqual(notices[0]["related_pmid"], "2")
        conflicting = payload.replace(
            b"</ArticleIdList>",
            b'<ArticleId IdType="doi">10.1234/other</ArticleId></ArticleIdList>',
        )
        with self.assertRaises(ValueError):
            lazic.parse_pubmed(conflicting, "source.xml", "checksum")
        same_year = payload.replace(b"<Year>2016</Year>", b"<Year>2015</Year>")
        rows, _ = lazic.parse_pubmed(same_year, "source.xml", "checksum")
        self.assertEqual(rows[0]["publication_date"], "2015-12-15")


if __name__ == "__main__":
    unittest.main()
