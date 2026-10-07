"""Build paper-level diagnostic labels, sample rules and verified timing evidence."""

import collections
import json

from scripts.research_pipeline import ROOT, Run, read_csv, unique, write_csv, write_json


def paper_status(values):
    if not values:
        raise ValueError("Missing assessment records for paper and diagnostic")
    if "1" in values:
        return "flagged"
    if all(x == "0" for x in values):
        return "comparison"
    return "unknown"


def main():
    with Run("hmx", "03_design", __file__, True) as run:
        run.require("02_identify")
        run.input(run.data / "design.md")
        identities = read_csv(run.data / "identities.csv")
        assessments = read_csv(run.input(ROOT / "data/cohorts/hmx/assessments.csv"))
        unique(assessments, ["paper_id", "assessment_id"])
        grouped = collections.defaultdict(list)
        for row in assessments:
            grouped[row["paper_id"], row["assessment_type"]].append(
                row["source_outcome"]
            )
        overlap = {x["paper_id"] for x in read_csv(run.data / "overlap.csv")}
        papers, targets = [], []
        for paper in identities:
            labels = {
                diagnostic: paper_status(grouped[paper["paper_id"], diagnostic])
                for diagnostic in [
                    "severe_extrapolation",
                    "linearity_rejected",
                    "low_high_not_rejected",
                ]
            }
            papers.append(
                dict(
                    paper_id=paper["paper_id"],
                    doi=paper["doi"],
                    journal=paper["journal"],
                    **labels,
                    meta_eligible=paper["paper_id"] not in overlap,
                    earlier_critique=paper["paper_id"] == "hmx_14"
                )
            )
            targets.append(
                dict(
                    paper,
                    role=labels["severe_extrapolation"],
                    assessment_doi="10.1017/pan.2018.46",
                )
            )
        counts = collections.Counter(p["severe_extrapolation"] for p in papers)
        run.check(
            "complete_primary_diagnostic",
            dict(counts) == {"flagged": 14, "comparison": 8},
            dict(counts),
        )
        run.check("single_meta_overlap", overlap == {"hmx_21"}, sorted(overlap))
        for name, rows in [
            ("paper_assessments.csv", papers),
            ("citation_targets.csv", targets),
        ]:
            path = run.data / name
            write_csv(path, rows, list(rows[0]))
            run.output(path)
        audit = json.loads((run.data / "audit_metadata.json").read_text())["message"]
        date = audit["published-online"]["date-parts"][0]
        run.check("publication_date", date == [2018, 12, 18], date)
        timing = dict(
            event="2018-12-18",
            event_definition="online journal publication",
            archive_release="2018-07-28",
            first_disclosure_verified=False,
            earlier_draft_posted="2016-02-29",
            followup_update="2019-12-29",
            updated_appendix="https://yiqingxu.org/packages/interflex/SI_update.pdf",
            earlier_critique_doi="10.1596/1813-9450-6602",
            interpretation="additional 2018 audit publicity; not first disclosure",
        )
        path = run.data / "timing.json"
        write_json(path, timing)
        run.output(path)
        run.record["metrics"] = dict(
            papers=len(papers), primary_counts=dict(counts), meta_papers=21
        )
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
