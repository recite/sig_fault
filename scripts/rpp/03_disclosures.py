"""Document 2015 publicity and preserve earlier report/visibility evidence."""

import argparse
import collections
import json
import re

from scripts.research_pipeline import ROOT, Run, read_csv, unique, write_csv

ANNOUNCEMENT = (
    "https://www.cos.io/about/news/"
    "massive-collaboration-testing-reproducibility-"
    "psychology-studies-publishes-findings"
)


def report_candidate(action, path):
    return (
        action
        in {
            "file_added",
            "file_updated",
            "osf_storage_file_added",
            "osf_storage_file_updated",
        }
        and bool(re.search(r"report|result|summary|replication", path, re.I))
        and not re.search(
            r"protocol|proposal|plan|prereg|blank|template|pre[-_ ]data", path, re.I
        )
        and bool(re.search(r"\.(pdf|docx?|txt|md|html?)$", path, re.I))
    )


def project_logs(run, node):
    url = f"https://api.osf.io/v2/nodes/{node}/logs/?page%5Bsize%5D=100"
    logs, seen, totals = [], set(), set()
    while url:
        run.check("distinct_log_page", url not in seen, node)
        seen.add(url)
        payload = run.fetch(url, "osf_logs")
        totals.add(payload["links"]["meta"]["total"])
        logs.extend(payload["data"])
        url = payload["links"].get("next")
    unique(logs, ["id"])
    run.check(
        "complete_project_logs",
        len(totals) == 1 and len(logs) == next(iter(totals)),
        dict(node=node, records=len(logs), expected=sorted(totals)),
    )
    return sorted(logs, key=lambda x: (x["attributes"]["date"], x["id"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    with Run("rpp", "03_disclosures", __file__, args.offline) as run:
        run.require("02_identify")
        run.input(run.data / "design.md")
        announcement = run.fetch(ANNOUNCEMENT, "announcement", False).decode("utf-8")
        run.check(
            "announcement_date_present",
            "2015-08-27" in announcement
            or bool(re.search(r"Aug(?:ust|\.)?\s+27,?\s+2015", announcement)),
            ANNOUNCEMENT,
        )
        identities = read_csv(run.data / "identities.csv")
        source = read_csv(run.input(ROOT / "data/cohorts/rpp/source_records/rpp.csv"))
        crosswalk = {
            x["source_study_id"]: x["paper_id"]
            for x in read_csv(run.input(ROOT / "data/cohorts/rpp/paper_crosswalk.csv"))
        }
        projects = collections.defaultdict(set)
        for row in source:
            projects[crosswalk[row["Local.ID"]]].add(
                row["Project.URL"].rstrip("/").split("/")[-1]
            )
        events, disclosures = [], []
        for paper in identities:
            pid = paper["paper_id"]
            complete, candidates, errors = True, [], []
            for node in sorted(projects[pid]):
                try:
                    logs = project_logs(run, node)
                except (OSError, ValueError, KeyError) as exc:
                    complete = False
                    errors.append(f"{node}: {type(exc).__name__}: {str(exc)[:120]}")
                    continue
                visibility = "unknown"
                for row in logs:
                    a = row["attributes"]
                    params = a.get("params") or {}
                    if (params.get("params_node") or {}).get("id") != node:
                        continue
                    action, date = a["action"], a["date"]
                    if action == "made_public":
                        visibility = "public"
                    elif action == "made_private":
                        visibility = "private"
                    path = params.get("path") or ""
                    candidate = report_candidate(action, path)
                    if candidate or action in {
                        "made_public",
                        "made_private",
                        "project_registered",
                    }:
                        events.append(
                            dict(
                                paper_id=pid,
                                node_id=node,
                                log_id=row["id"],
                                date=date,
                                action=action,
                                path=path,
                                visibility_at_event=visibility,
                                report_candidate=candidate,
                                evidence_url=f"https://api.osf.io/v2/logs/{row['id']}/",
                            )
                        )
                    if candidate and date[:10] < "2015-08-27":
                        candidates.append(date[:10])
            disclosures.append(
                dict(
                    paper_id=pid,
                    announcement_date="2015-08-27",
                    announcement_source=ANNOUNCEMENT,
                    event_meaning="additional_project_publicity",
                    first_disclosure_date="",
                    first_disclosure_status="requires_content_and_visibility_review",
                    earliest_report_candidate=min(candidates, default=""),
                    logs_complete=complete,
                    retrieval_errors="; ".join(errors),
                )
            )
            print(
                pid,
                "logs",
                complete,
                "earlier_report_candidates",
                len(candidates),
                flush=True,
            )
        unique(disclosures, ["paper_id"])
        run.check(
            "paper_conservation", len(disclosures) == len(identities), len(disclosures)
        )
        for name, rows, fields in [
            ("disclosures.csv", disclosures, list(disclosures[0])),
            (
                "disclosure_evidence.csv",
                events,
                [
                    "paper_id",
                    "node_id",
                    "log_id",
                    "date",
                    "action",
                    "path",
                    "visibility_at_event",
                    "report_candidate",
                    "evidence_url",
                ],
            ),
        ]:
            path = run.data / name
            write_csv(path, rows, fields)
            run.output(path)
        run.record["metrics"] = dict(
            papers=len(disclosures),
            complete_project_logs=sum(x["logs_complete"] for x in disclosures),
            papers_with_earlier_report_candidates=sum(
                bool(x["earliest_report_candidate"]) for x in disclosures
            ),
        )
        run.record["unresolved"] = [
            dict(
                paper_id=x["paper_id"],
                reason=x["first_disclosure_status"],
                retrieval_errors=x["retrieval_errors"],
            )
            for x in disclosures
        ]
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
