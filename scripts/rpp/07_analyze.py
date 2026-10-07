"""Estimate the frozen comparisons, check identities, and write the study report."""

import json
import os
import shlex
import subprocess
from string import Template

from scripts.research_pipeline import ROOT, Run, fingerprint, read_csv


def main():
    with Run("rpp", "07_analyze", __file__, True) as run:
        run.require("06_match")
        for name in [
            "design.md",
            "panel.csv",
            "identities.csv",
            "citation_coverage.csv",
        ]:
            run.input(run.data / name)
        run.record["code"].append(fingerprint(ROOT / "R/rpp.R"))
        run.input(ROOT / "renv.lock")
        run.input(ROOT / "requirements-i4r.txt")
        command = shlex.split(os.environ.get("RPP_RSCRIPT", "Rscript")) + [
            "R/rpp.R",
            str(run.data),
        ]
        run.record["estimation_command"] = command
        subprocess.run(command, cwd=ROOT, check=True)
        checks = json.loads((run.data / "analysis_checks.json").read_text())
        run.check(
            "full_original_cohort",
            checks["papers"] == 98 and checks["citation_history_complete"],
            checks,
        )
        run.check(
            "defined_bootstrap_draws",
            checks["bootstrap_undefined"] == 0,
            checks["bootstrap_undefined"],
        )
        run.check(
            "fixed_effects_identity",
            checks["raw_fe_identity_error"] < 1e-8,
            checks["raw_fe_identity_error"],
        )
        names = [
            "paper_periods.csv",
            "period_summary.csv",
            "journal_contrasts.csv",
            "estimates.csv",
            "leave_one_out.csv",
            "fixed_effects.csv",
            "event_study.csv",
            "annual_summary.csv",
            "external_estimates.csv",
            "external_paths.csv",
            "citation_paths.pdf",
            "citation_paths.png",
            "R-session.txt",
            "analysis_checks.json",
        ]
        for name in names:
            run.output(run.data / name)
        estimates = read_csv(run.data / "estimates.csv")
        main = next(x for x in estimates if x["specification"] == "primary")

        def interval(row, estimate, lower, upper, percent=False):
            suffix = "%" if percent else ""
            return (
                f"{float(row[estimate]):.2f}{suffix} "
                f"[{float(row[lower]):.2f}, {float(row[upper]):.2f}]"
            )

        levels = []
        for x in read_csv(run.data / "period_summary.csv"):
            values = " | ".join(
                f"{float(x[k]):.2f}"
                for k in ["pre_mean", "post_mean", "pre_median", "post_median"]
            )
            levels.append(f"| {x['role']} | {x['papers']} | {values} |")
        specifications = []
        labels = {
            "primary": "2016–2018, articles/reviews",
            "longer_followup": "2016–2025, articles/reviews",
            "all_document_types": "2016–2018, all document types",
            "pre_period_placebo": "Pre-announcement placebo",
        }
        for x in estimates:
            level = interval(
                x, "estimate_citations", "lower_citations", "upper_citations"
            )
            prop = interval(x, "percent", "lower_percent", "upper_percent", True)
            specifications.append(
                f"| {labels[x['specification']]} | {level} | {prop} |"
            )
        external = []
        for x in read_csv(run.data / "external_estimates.csv"):
            estimate = (
                interval(x, "estimate", "lower", "upper")
                if x["lower"]
                else f"{float(x['estimate']):.2f} (point estimate)"
            )
            external.append(f"| {x['role']} | {x['method']} | {estimate} |")
        template = Template(run.input(run.data / "README.in.md").read_text())
        report = template.substitute(
            level=interval(
                main, "estimate_citations", "lower_citations", "upper_citations"
            ),
            proportional=interval(
                main, "percent", "lower_percent", "upper_percent", True
            ),
            levels="\n".join(levels),
            specifications="\n".join(specifications),
            external="\n".join(external),
        )
        path = run.data / "README.md"
        path.write_text(report)
        run.output(path)
        run.record["metrics"] = checks
        print(json.dumps(main))


if __name__ == "__main__":
    main()
