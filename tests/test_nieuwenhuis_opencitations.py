"""Check source-specific missingness, identity merging, and collection checkpoints."""

import http.client
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import nieuwenhuis_opencitations as oc  # noqa: E402
import nieuwenhuis_validation as validation  # noqa: E402
import pilot  # noqa: E402


def edge(oci, citing, year="2012", paper="nw_1"):
    return dict(
        paper_id=paper,
        oci=oci,
        citing=citing,
        cited="doi:10.1/target",
        creation=year,
        timespan="",
    )


class OpenCitationsTests(unittest.TestCase):
    def test_shared_identifiers_merge_transitively_within_target(self):
        rows = [
            edge("1", "omid:a doi:10.1/x", ""),
            edge("2", "omid:a doi:10.1/y"),
            edge("3", "omid:b doi:10.1/Y", "2012-06"),
            edge("4", "omid:a doi:10.1/x", paper="nw_2"),
        ]
        result = oc.merge_works(rows)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["raw_relationships"], 3)
        self.assertEqual(result[0]["year"], 2012)
        self.assertEqual(result[0]["date_status"], "dated")
        self.assertEqual(result[0]["ocis"], "1;2;3")

    def test_conflicting_and_absent_years_stay_unresolved(self):
        rows = [
            edge("1", "omid:a", "2010"),
            edge("2", "omid:a", "2012"),
            edge("3", "omid:b", ""),
        ]
        result = oc.merge_works(rows)
        self.assertEqual([r["year"] for r in result], ["", ""])
        self.assertEqual(
            [r["date_status"] for r in result], ["conflicting_years", "undated"]
        )
        with self.assertRaisesRegex(ValueError, "OMID"):
            oc.merge_works([edge("4", "doi:10.1/only")])

    def test_missing_acquisition_is_not_zero_and_oa_status_is_irrelevant(self):
        historical = [
            dict(
                article_id=str(i),
                paper_id=f"nw_{i}",
                year="2010",
                flag="1",
                cohort="2009",
                journal="J",
                wos="5",
                status="missing_history",
            )
            for i in [1, 2]
        ]
        works = oc.merge_works([edge("1", "omid:a", ""), edge("2", "omid:b", "2012")])
        result = oc.make_panel(
            historical, works, [dict(paper_id="nw_1", complete="yes")]
        )
        self.assertEqual(result[0]["opencitations"], 0)
        self.assertEqual(result[0]["undated_works"], 1)
        self.assertEqual(result[0]["status"], "complete")
        self.assertEqual(result[1]["opencitations"], "")
        self.assertEqual(result[1]["undated_works"], "")
        self.assertEqual(result[1]["status"], "missing_history")

    def test_truncated_json_falls_back_to_complete_csv(self):
        raw = b"oci,citing,cited,creation,timespan\n1,omid:a,doi:10.1/x,2012,P1Y\n"
        with tempfile.TemporaryDirectory() as directory, patch.object(
            validation, "CACHE", Path(directory)
        ), patch.object(validation.time, "sleep"), patch.object(
            validation.acquisition,
            "fetch",
            side_effect=[http.client.IncompleteRead(b"partial", 100), raw],
        ) as fetch:
            result = validation.fetch_links("nw_1", "10.1/x")
            validation.validate_response(result, 1, "10.1/x")
            self.assertTrue(fetch.call_args.args[0].endswith("?format=csv"))
            self.assertFalse(fetch.call_args.kwargs["json_response"])

    def test_opencitations_rate_limit_has_own_checkpoint_and_no_other_token(self):
        source = validation.acquisition
        captured = []

        def limited(request, **kwargs):
            captured.append(request)
            raise urllib.error.HTTPError(
                request.full_url, 429, "limited", {"Retry-After": "120"}, None
            )

        with tempfile.TemporaryDirectory() as directory, patch.object(
            source, "CACHE", Path(directory)
        ), patch.dict(
            os.environ, {"OPENALEX_API_KEY": "unrelated", "OSF_TOKEN": "other"}
        ), patch.object(
            source.urllib.request, "urlopen", side_effect=limited
        ) as request:
            path = Path(directory) / "response.json"
            url = "https://api.opencitations.net/index/v2/citations/doi:10.1/x"
            with self.assertRaises(urllib.error.HTTPError) as raised:
                source.fetch(url, path)
            raised.exception.close()
            self.assertIsNone(captured[0].get_header("Authorization"))
            with self.assertRaisesRegex(RuntimeError, "rate limit"):
                source.fetch(url, path)
            self.assertEqual(request.call_count, 1)
            self.assertFalse(path.exists())

    def test_checkpoint_preserves_histories_outside_current_visit(self):
        old = {
            "nw_1": dict(
                paper_id="nw_1",
                doi="10.1/one",
                records=1,
                reported_count=1,
                undated_records=0,
                complete="yes",
                detail="",
            )
        }
        fresh = dict(
            paper_id="nw_2",
            doi="10.1/two",
            records=0,
            reported_count=0,
            undated_records=0,
            complete="yes",
            detail="",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            with patch.object(validation, "DATA", path), patch.object(
                validation, "CACHE", path
            ), patch.object(validation.nw, "read", return_value=[]):
                validation.checkpoint([], [fresh], [edge("1", "omid:a")], old)
            covered = pilot.read_csv(path / "validation_coverage.csv")
            self.assertEqual({r["paper_id"] for r in covered}, {"nw_1", "nw_2"})
            self.assertEqual(len(pilot.read_csv(path / "validation_edges.csv")), 1)


if __name__ == "__main__":
    unittest.main()
