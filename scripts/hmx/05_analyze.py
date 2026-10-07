"""Reproduce the interaction-audit estimates from the frozen public panel."""

import json
import os
import shlex
import subprocess

from scripts.research_pipeline import ROOT, Run, fingerprint


def main():
    with Run("hmx", "05_analyze", __file__, True) as run:
        for name in [
            "design.md",
            "panel.csv",
            "paper_assessments.csv",
            "citation_coverage.csv",
            "timing.json",
        ]:
            run.input(run.data / name)
        run.input(ROOT / "renv.lock")
        for name in ["R/analysis.R", "R/hmx.R"]:
            run.record["code"].append(fingerprint(ROOT / name))
        command = shlex.split(os.environ.get("HMX_RSCRIPT", "Rscript")) + [
            "R/hmx.R",
            str(run.data),
        ]
        run.record["estimation_command"] = command
        subprocess.run(command, cwd=ROOT, check=True)
        checks = json.loads((run.data / "analysis_checks.json").read_text())
        run.check(
            "cohort_and_labels",
            checks["papers"] == 22
            and checks["flagged"] == 14
            and checks["comparison"] == 8
            and checks["complete"],
            checks,
        )
        run.check("nonoverlap", checks["nonoverlap_papers"] == 21, checks)
        run.check("journal_support", checks["journal_supported_papers"] == 19, checks)
        run.check("defined_bootstrap", checks["bootstrap_undefined"] == 0, checks)
        run.check("independent_ratio", checks["raw_fe_identity_error"] < 1e-8, checks)
        for name in [
            "specifications.csv",
            "estimates.csv",
            "absolute_estimates.csv",
            "paper_periods.csv",
            "bootstrap.csv",
            "period_summary.csv",
            "annual_summary.csv",
            "journal_support.csv",
            "leave_one_out.csv",
            "analysis_checks.json",
            "R-session.txt",
        ]:
            run.output(run.data / name)
        run.record["metrics"] = checks
        print(json.dumps(checks))


if __name__ == "__main__":
    main()
