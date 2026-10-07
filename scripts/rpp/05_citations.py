"""Acquire citation links and build a panel from complete histories."""

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
    with Run("rpp", "05_citations", __file__, args.offline) as run:
        run.record["code"].append(fingerprint(ROOT / "scripts/citation_history.py"))
        run.require("04_controls")
        run.require("03_disclosures")
        run.input(run.data / "design.md")
        papers = read_csv(run.data / "citation_targets.csv")
        for paper in papers:
            paper["assessment_doi"] = "10.1126/science.aac4716"
        edges, decisions, coverage = [], [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(acquire, run, p): p for p in papers}
            for future in concurrent.futures.as_completed(futures):
                paper = futures[future]
                try:
                    found, resolved, status = future.result()
                    edges.extend(found)
                    decisions.extend(resolved)
                except (OSError, ValueError, KeyError, RuntimeError) as error:
                    status = dict(
                        paper_id=paper["paper_id"],
                        doi=paper["doi"],
                        target_work_id="",
                        complete=False,
                        reported_records="",
                        pages="",
                        detail=str(error)[:180],
                        is_retracted="",
                        target_type="",
                    )
                    run.record["unresolved"].append(status)
                coverage.append(status)
                print(
                    len(coverage),
                    "/",
                    len(papers),
                    paper["paper_id"],
                    status["complete"],
                    status["reported_records"],
                    status["detail"],
                    flush=True,
                )
        edges.sort(key=lambda x: (x["paper_id"], x["citing_work_id"]))
        coverage.sort(key=lambda x: x["paper_id"])
        panel = make_panel(papers, coverage, edges)
        unique(edges, ["paper_id", "citing_work_id"])
        unique(panel, ["paper_id", "year"])
        run.check("panel_row_conservation", len(panel) == len(papers) * 18, len(panel))
        path = run.data / "citation_identity_decisions.csv"
        write_csv(
            path,
            sorted(decisions, key=lambda x: (x["paper_id"], x["doi"])),
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
        for name, rows in [
            ("citation_edges.csv", edges),
            ("citation_coverage.csv", coverage),
            ("panel.csv", panel),
        ]:
            path = run.data / name
            write_csv(path, rows, list(rows[0]))
            run.output(path)
        run.record["metrics"] = dict(
            targets=len(papers),
            completed=sum(x["complete"] for x in coverage),
            edges=len(edges),
            panel_rows=len(panel),
        )
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
