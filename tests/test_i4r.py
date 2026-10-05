"""Numerical and acquisition-integrity checks for the I4R pipeline."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import i4r_citations as citations  # noqa: E402
import i4r_match as matching  # noqa: E402
import i4r_sources as sources  # noqa: E402


def article(aid, year=2010):
    return dict(
        article_id=aid,
        title="An empirical study of schooling and wages",
        abstract="",
        journal_id="S1",
        publication_year=str(year),
        publication_date=f"{year}-06-01",
        type="article",
        identity_verified="yes",
        retracted="no",
    )


def event(eid="e1", year=2015, aid="treated"):
    return dict(
        event_id=eid,
        warning_id=eid,
        article_id=aid,
        year=str(year),
        date="",
        error_verified="yes",
        material="yes",
        publicity_verified="yes",
        already_retracted="no",
    )


def counts(aid, values):
    return [
        dict(article_id=aid, year=str(y), citations=str(n), status="complete")
        for y, n in values.items()
    ]


class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.articles = [article("treated")] + [
            article("c" + str(i)) for i in range(1, 5)
        ]
        self.pre = sum(
            [counts(r["article_id"], {2013: 10, 2014: 12}) for r in self.articles], []
        )

    def test_identical_pre_histories_ties_weights_and_no_post_leakage(self):
        a = matching.match(self.articles, [event()], self.pre, [])
        extreme = self.pre + counts("treated", {2016: 100000}) + counts("c1", {2016: 0})
        b = matching.match(self.articles, [event()], extreme, [])
        self.assertEqual(a, b)
        self.assertEqual([r["control_id"] for r in a[0]], ["c1", "c2", "c3"])
        self.assertAlmostEqual(sum(r["weight"] for r in a[0]), 1)

    def test_first_disclosure_is_not_reset_when_baseline_is_short(self):
        eligible, exclusions = matching.eligible_events(
            [event("early", 2011), event("late", 2015)], self.articles, 2025, 1
        )
        self.assertEqual(eligible, [])
        self.assertIn("subsequent_disclosure", [r["reason"] for r in exclusions])

    def test_assessed_originals_cannot_reenter_vetted_control_pool(self):
        m, _, _, _ = matching.match(
            self.articles, [event()], self.pre, [], control_ids={"c4"}
        )
        self.assertEqual([r["control_id"] for r in m], ["c4"])

    def test_unknown_citations_are_not_zero(self):
        missing = [r for r in self.pre if r["article_id"] != "treated"]
        m, _, exclusions, _ = matching.match(self.articles, [event()], missing, [])
        self.assertFalse(m)
        self.assertEqual(exclusions[0]["reason"], "incomplete_pre_citations")
        zeros = [r | {"citations": "0"} for r in self.pre]
        self.assertEqual(len(matching.match(self.articles, [event()], zeros, [])[0]), 3)

    def test_future_assessment_censors_only_relevant_horizon(self):
        assessments = [dict(article_id="c1", public_year="2017")]
        short = matching.match(
            self.articles, [event()], self.pre, assessments, horizon=1
        )[0]
        long = matching.match(
            self.articles, [event()], self.pre, assessments, horizon=2
        )[0]
        self.assertIn("c1", [r["control_id"] for r in short])
        self.assertNotIn("c1", [r["control_id"] for r in long])

    def test_retraction_after_followup_is_not_baseline_exclusion(self):
        self.articles[1].update(retracted="yes", retraction_date="2020-06-01")
        m = matching.match(self.articles, [event()], self.pre, [])[0]
        self.assertIn("c1", [r["control_id"] for r in m])

    def test_incomplete_outcome_discards_whole_stack(self):
        matches = matching.match(self.articles, [event()], self.pre, [])[0]
        rows, omitted = matching.panel(matches, [event()], self.pre)
        self.assertFalse(rows)
        self.assertEqual(len(omitted), 1)

    def test_reused_controls_retain_original_identity(self):
        self.articles.append(article("treated2"))
        pre = self.pre + counts("treated2", {2013: 10, 2014: 12})
        ev = [event(), event("e2", aid="treated2")]
        matches = matching.match(self.articles, ev, pre, [], control_ids={"c1"})[0]
        full = pre + sum(
            [counts(r["article_id"], {2016: 15}) for r in self.articles], []
        )
        rows, _ = matching.panel(matches, ev, full)
        c = [r for r in rows if r["article_id"] == "c1"]
        self.assertEqual(len(c), 4)
        self.assertEqual(len({r["stack_id"] for r in c}), 2)


class AcquisitionTests(unittest.TestCase):
    def test_hidden_catalog_entries_are_included(self):
        entries = [{"title": "Visible"}, {"title": "Beyond show more"}]
        payload = '13:["$",null,{"reports":' + json.dumps(entries) + "}]"
        html = "<script>self.__next_f.push(" + json.dumps([1, payload]) + ")</script>"
        self.assertEqual(sources.flight_array(html, "reports"), entries)

    def test_osf_paths_resolve_same_node_not_same_article(self):
        self.assertEqual(sources.osf_node("https://osf.io/abc12/overview"), "abc12")
        self.assertEqual(
            sources.osf_node("https://osf.io/abc12/files/osfstorage"), "abc12"
        )
        self.assertEqual(sources.osf_node("https://example.com/abc12"), "")

    def test_doi_aliases_deduplicate_and_types_filter(self):
        works = [
            dict(
                id="W1",
                doi="https://doi.org/10.1/ABC",
                type="article",
                publication_year=2020,
                publication_date="2020-02-01",
            ),
            dict(
                id="W2",
                doi="10.1/abc",
                type="article",
                publication_year=2021,
                publication_date="2021-02-01",
            ),
            dict(
                id="W3",
                doi=None,
                type="book-chapter",
                publication_year=2021,
                publication_date="2021-02-01",
            ),
        ]
        out = citations.normalize_edges("target", works)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["publication_year"], 2020)

    def test_query_identity_changes_cache_path(self):
        paths = []

        def request(url, path):
            paths.append(path)
            return {"results": [], "meta": {"count": 0, "next_cursor": None}}

        with tempfile.TemporaryDirectory() as tmp, patch.object(
            sources, "fetch", request
        ):
            citations.all_works({"filter": "publication_year:2020"}, Path(tmp))
            citations.all_works({"filter": "publication_year:2010-2020"}, Path(tmp))
        self.assertNotEqual(paths[0], paths[1])

    def test_truncated_pagination_fails(self):
        with patch.object(
            sources,
            "fetch",
            return_value={"results": [], "meta": {"count": 20, "next_cursor": None}},
        ):
            with self.assertRaisesRegex(ValueError, "Incomplete"):
                citations.all_works({}, Path("/tmp/unused-i4r-test"))


class PipelineIntegrityTests(unittest.TestCase):
    def test_partial_pool_is_never_matched(self):
        articles = [article("treated"), article("control")]
        pre = counts("treated", {2013: 3, 2014: 4}) + counts(
            "control", {2013: 3, 2014: 4}
        )
        result = matching.match(articles, [event()], pre, [], complete_risk_sets=set())
        self.assertFalse(result[0])
        self.assertEqual(result[2][0]["reason"], "incomplete_risk_set_retrieval")

    def test_fixed_cohorts_require_both_horizons(self):
        members = [article("treated"), article("control")]
        pre = counts("treated", {2013: 3, 2014: 4}) + counts(
            "control", {2013: 3, 2014: 4}
        )
        matches = matching.match(members, [event()], pre, [], horizon=2)[0]
        for year in [2016, 2017]:
            incomplete = (
                pre + counts("treated", {year: 6}) + counts("control", {year: 5})
            )
            self.assertFalse(matching.panel(matches, [event()], incomplete)[0])
            self.assertFalse(
                matching.sensitivity_panels(matches, [event()], incomplete)
            )
        complete = (
            pre
            + counts("treated", {2016: 6, 2017: 7})
            + counts("control", {2016: 5, 2017: 5})
        )
        self.assertEqual(len(matching.panel(matches, [event()], complete)[0]), 4)
        self.assertEqual(
            {
                r["specification"]
                for r in matching.sensitivity_panels(matches, [event()], complete)
            },
            {"year1_fixed_h2_cohort", "average_post1_post2"},
        )

    def test_earlier_placebo_excludes_partial_publication_year(self):
        members = [article("treated", 2012), article("control", 2011)]
        values = sum(
            [
                counts(r["article_id"], {2012: 1, 2013: 3, 2014: 4, 2016: 6})
                for r in members
            ],
            [],
        )
        matches = matching.match(members, [event()], values, [])[0]
        specs = matching.sensitivity_panels(matches, [event()], values, members)
        self.assertNotIn("placebo_pre3_pre2", {r["specification"] for r in specs})
        members[0] = article("treated", 2011)
        specs = matching.sensitivity_panels(matches, [event()], values, members)
        self.assertIn("placebo_pre3_pre2", {r["specification"] for r in specs})

    def test_retraction_ledger_survives_csv_roundtrip(self):
        import i4r_registry as registry

        with tempfile.TemporaryDirectory() as tmp, patch.object(
            sources, "DATA", Path(tmp)
        ):
            sources.write(
                "retractions.csv",
                [
                    dict(
                        doi="10.1/test",
                        date="2014-01-01",
                        source_url="https://example.org/notice",
                    )
                ],
                ["doi", "date", "source_url"],
            )
            record = (
                dict.fromkeys(registry.ARTICLE_FIELDS, "")
                | article("control")
                | {"doi": "10.1/test"}
            )
            sources.write(
                "control_articles.csv",
                [registry.add_retraction(record)],
                registry.ARTICLE_FIELDS,
            )
            loaded = sources.read("control_articles.csv")[0]
            self.assertEqual(loaded["retraction_date"], "2014-01-01")
            members = [article("treated"), loaded]
            pre = counts("treated", {2013: 3, 2014: 4}) + counts(
                "control", {2013: 3, 2014: 4}
            )
            result = matching.match(members, [event()], pre, [])
            self.assertEqual(result[1][0]["reason"], "known_retraction_in_window")
            loaded["retraction_date"] = ""
            result = matching.match(members, [event()], pre, [])
            self.assertEqual(result[1][0]["reason"], "retraction_date_unresolved")

    def test_frozen_metadata_rebuild_needs_no_private_cache(self):
        import i4r_registry as registry

        with tempfile.TemporaryDirectory() as tmp, patch.object(
            sources, "DATA", Path(tmp)
        ), patch.object(sources, "CACHE", Path(tmp) / "absent"):
            title = "An empirical study"
            aid = registry.article_id(title)
            source = dict.fromkeys(sources.SOURCE_FIELDS, "") | {
                "source_id": "report_a",
                "title": title,
                "collection": "reports",
            }
            sources.write("sources.csv", [source], sources.SOURCE_FIELDS)
            frozen = (
                dict.fromkeys(registry.ARTICLE_FIELDS, "")
                | article(aid)
                | {"title": title, "doi": "10.1/test"}
            )
            sources.write("verified_metadata.csv", [frozen], registry.ARTICLE_FIELDS)
            registry.build()
            registry.validate()
            rebuilt = sources.read("articles.csv")[0]
            self.assertEqual(rebuilt["identity_verified"], "yes")
            self.assertEqual(rebuilt["publication_year"], "2010")

    def test_cached_hash_and_url_must_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "response.json"
            path.write_text("{}")
            path.with_suffix(".json.source.json").write_text(
                json.dumps({"url": "https://example.org/a", "sha256": "bad"})
            )
            with self.assertRaisesRegex(ValueError, "URL/hash mismatch"):
                sources.fetch("https://example.org/a", path)

    def test_control_work_aliases_are_one_original_and_all_queried(self):
        import i4r_registry as registry

        base = dict.fromkeys(registry.ARTICLE_FIELDS, "") | article("W1")
        first = base | {"doi": "10.1/control", "openalex_id": "https://openalex.org/W1"}
        second = first | {"article_id": "W2", "openalex_id": "https://openalex.org/W2"}
        controls, aliases = citations.canonical_controls([first, second], [])
        self.assertEqual(len(controls), 1)
        self.assertEqual(len(aliases), 2)
        with tempfile.TemporaryDirectory() as tmp, patch.object(
            sources, "DATA", Path(tmp)
        ):
            sources.write(
                "control_aliases.csv", aliases, ["alias_openalex_id", "article_id"]
            )
            self.assertEqual(
                citations.cited_ids(controls[0]),
                ["https://openalex.org/W1", "https://openalex.org/W2"],
            )
        self.assertFalse(citations.canonical_controls([first, second], [first])[0])

    def test_rate_limited_rerun_preserves_other_complete_histories(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(
            sources, "DATA", Path(tmp)
        ):
            import i4r_registry as registry

            for name, rows, fields in [
                ("events.csv", [event()], registry.EVENT_FIELDS),
                (
                    "articles.csv",
                    [
                        dict.fromkeys(registry.ARTICLE_FIELDS, "")
                        | article("treated")
                        | {"openalex_id": "https://openalex.org/W1"}
                    ],
                    registry.ARTICLE_FIELDS,
                ),
                (
                    "citations.csv",
                    counts("previous_control", {2016: 9}),
                    ["article_id", "year", "citations", "status"],
                ),
            ]:
                sources.write(name, rows, fields)
            with patch.object(
                citations, "all_works", side_effect=RuntimeError("429 rate limit")
            ):
                citations.collect()
            self.assertEqual(
                sources.read("citations.csv"), counts("previous_control", {2016: 9})
            )
            self.assertEqual(
                sources.read("citation_retrieval.csv")[0]["status"], "incomplete"
            )


if __name__ == "__main__":
    unittest.main()
