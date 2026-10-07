"""Collect complete citation histories for the frozen interaction-audit roster."""

import argparse
import concurrent.futures
import json

from scripts.citation_history import acquire, make_panel
from scripts.research_pipeline import (
    ROOT,
    Run,
    fingerprint,
    read_csv,
    unique,
    write_csv,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    with Run("hmx", "04_citations", __file__, args.offline) as run:
        run.require("03_design")
        run.record["code"].append(fingerprint(ROOT / "scripts/citation_history.py"))
        papers = read_csv(run.data / "citation_targets.csv")
        edges, decisions, coverage = [], [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(acquire, run, p): p for p in papers}
            for future in concurrent.futures.as_completed(futures):
                found, resolved, status = future.result()
                edges.extend(found)
                decisions.extend(resolved)
                coverage.append(status)
                print(
                    len(coverage),
                    "/",
                    len(papers),
                    status["paper_id"],
                    status["reported_records"],
                    flush=True,
                )
        edges.sort(key=lambda x: (x["paper_id"], x["citing_work_id"]))
        decisions.sort(key=lambda x: (x["paper_id"], x["doi"]))
        coverage.sort(key=lambda x: x["paper_id"])
        panel = make_panel(papers, coverage, edges, start_year=2006)
        unique(panel, ["paper_id", "year"])
        run.check(
            "complete_cohort",
            len(coverage) == 22 and all(x["complete"] for x in coverage),
            len(coverage),
        )
        for name, rows in [
            ("citation_edges.csv", edges),
            ("citation_coverage.csv", coverage),
            ("panel.csv", panel),
        ]:
            path = run.data / name
            write_csv(path, rows, list(rows[0]))
            run.output(path)
        path = run.data / "citation_identity_decisions.csv"
        write_csv(
            path,
            decisions,
            [
                "paper_id",
                "doi",
                "canonical_id",
                "candidate_ids",
                "candidate_years",
                "basis",
            ],
        )
        run.output(path)
        run.record["metrics"] = dict(
            papers=len(coverage), links=len(edges), paper_years=len(panel)
        )
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
