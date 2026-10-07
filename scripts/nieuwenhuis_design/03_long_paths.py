"""Extend Figure 1's descriptive OpenAlex series through the frozen cutoff."""

import collections
import os
import shlex
import statistics
import subprocess
import sys

from scripts.research_pipeline import (
    ROOT,
    Run,
    fingerprint,
    read_csv,
    unique,
    write_csv,
)

sys.path.insert(0, str(ROOT / "scripts"))
import nieuwenhuis as nw  # noqa: E402
import pilot  # noqa: E402


def main():
    data = ROOT / "data/nieuwenhuis"
    with Run(
        "nieuwenhuis_paths", "03_long_paths", __file__, True, data_dir=data / "paths"
    ) as run:
        inputs = {}
        for name in [
            "identities",
            "coverage",
            "citation_edges",
            "duplicate_resolutions",
            "paired_panel",
        ]:
            inputs[name] = read_csv(run.input(data / f"{name}.csv"))
        run.input(ROOT / "renv.lock")
        for name in [
            "scripts/nieuwenhuis.py",
            "scripts/nieuwenhuis_design/long_paths.R",
            "R/reporting.R",
        ]:
            run.record["code"].append(fingerprint(ROOT / name))
        paired = inputs["paired_panel"]
        unique(paired, ["paper_id", "year"])
        ids = {r["paper_id"] for r in paired}
        identities = {r["paper_id"]: r for r in inputs["identities"]}
        complete = {
            r["paper_id"]
            for r in inputs["coverage"]
            if nw.history_complete(r, identities.get(r["paper_id"], {}))
        }
        run.check("full_original_cohort", len(ids) == 153, len(ids))
        run.check("complete_downloads", ids <= complete, sorted(ids - complete))
        edges = nw.resolve_duplicate_edges(
            inputs["citation_edges"], inputs["duplicate_resolutions"]
        )
        unique(edges, ["paper_id", "citing_work_id"])
        run.check(
            "frozen_cutoff",
            all(r["publication_date"] <= pilot.CUTOFF for r in edges),
            pilot.CUTOFF,
        )
        eligible = [
            r
            for r in nw.eligible_edges(edges, {"article", "review"})
            if r["paper_id"] in ids
        ]
        unique([r for r in eligible if r["doi"]], ["paper_id", "doi"])
        counts = collections.Counter(
            (r["paper_id"], int(r["publication_year"])) for r in eligible
        )
        run.check(
            "historical_overlap_exact",
            all(
                r["status"] == "complete"
                and counts[r["paper_id"], int(r["year"])] == int(r["openalex"])
                for r in paired
            ),
            {"article_years": len(paired), "years": "2009-2015"},
        )
        end = int(pilot.CUTOFF[:4])
        panel = [
            dict(
                paper_id=pid,
                year=year,
                flag=int(identities[pid]["flag"]),
                citations=counts[pid, year],
            )
            for pid in sorted(ids)
            for year in range(2009, end + 1)
        ]
        summary = []
        for year in range(2009, end + 1):
            for flag in (0, 1):
                values = [
                    r["citations"]
                    for r in panel
                    if r["year"] == year and r["flag"] == flag
                ]
                summary.append(
                    dict(
                        year=year,
                        flag=flag,
                        papers=len(values),
                        total=sum(values),
                        mean=statistics.mean(values),
                        median=statistics.median(values),
                    )
                )
        run.check(
            "fixed_denominators",
            all(r["papers"] == (76 if r["flag"] else 77) for r in summary),
            {"flagged": 76, "comparison": 77},
        )
        for name, rows in [("panel", panel), ("annual_summary", summary)]:
            path = run.data / f"{name}.csv"
            write_csv(path, rows, list(rows[0]))
            run.output(path)
        command = shlex.split(os.environ.get("RSCRIPT", "Rscript --vanilla"))
        subprocess.run(
            command + ["scripts/nieuwenhuis_design/long_paths.R"], cwd=ROOT, check=True
        )
        for name in [
            "figs/citation_paths_openalex.pdf",
            "figs/citation_paths_openalex_body.pdf",
            "tabs/nieuwenhuis_paths_macros.tex",
            "tabs/nieuwenhuis_paths_macros.json",
        ]:
            run.output(ROOT / name)
        run.record["metrics"] = dict(
            papers=len(ids),
            start_year=2009,
            end_year=end,
            article_years=len(panel),
            citations=sum(r["citations"] for r in panel),
            citation_types=["article", "review"],
            cutoff=pilot.CUTOFF,
        )


if __name__ == "__main__":
    main()
