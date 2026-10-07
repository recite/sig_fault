"""Estimate and document comparisons within journal and publication year."""

import json
import os
import shlex
import subprocess

from scripts.research_pipeline import ROOT, Run, fingerprint


def main():
    with Run(
        "nieuwenhuis_design",
        "01_estimate",
        __file__,
        True,
        data_dir=ROOT / "data/nieuwenhuis/design",
    ) as run:
        for name in [
            "data/nieuwenhuis/paired_panel.csv",
            "docs/nieuwenhuis/journal-cohort-design.md",
            "renv.lock",
        ]:
            run.input(ROOT / name)
        for name in ["R/journal_cohort.R", "scripts/nieuwenhuis_design/estimate.R"]:
            run.record["code"].append(fingerprint(ROOT / name))
        command = shlex.split(os.environ.get("RSCRIPT", "Rscript --vanilla"))
        subprocess.run(
            command + ["scripts/nieuwenhuis_design/estimate.R"], cwd=ROOT, check=True
        )
        for name in [
            "support.csv",
            "weights.csv",
            "estimates.csv",
            "annual_estimates.csv",
            "annual_paths.csv",
            "status.json",
            "README.md",
        ]:
            run.output(run.data / name)
        for name in [
            "tabs/journal_cohort_estimates.tex",
            "tabs/journal_cohort_macros.json",
            "tabs/journal_cohort_macros.tex",
            "figs/journal_cohort_paths.pdf",
        ]:
            run.output(ROOT / name)
        status = json.loads((run.data / "status.json").read_text())
        run.check("all_groups_supported", status["supported"], status["strata"])
        run.check("original_population_retained", status["papers"] == 153, status)
        run.check("all_planned_models", status["specifications"] == 18, status)
        run.check("all_annual_models", status["annual_estimates"] == 20, status)
        run.record["metrics"] = status


if __name__ == "__main__":
    main()
