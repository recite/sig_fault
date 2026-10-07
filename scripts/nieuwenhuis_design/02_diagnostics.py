"""Check predetermined balance and expose weighting in the citation design."""

import json
import os
import shlex
import subprocess

from scripts.research_pipeline import ROOT, Run, fingerprint


def main():
    with Run(
        "nieuwenhuis_design",
        "02_diagnostics",
        __file__,
        True,
        data_dir=ROOT / "data/nieuwenhuis/design",
    ) as run:
        run.require("01_estimate")
        for name in [
            "data/nieuwenhuis/paired_panel.csv",
            "data/01_nieuwenhuis/from_nieuwenhuis/nieuwenhuis_with_id.csv",
            "data/01_nieuwenhuis/from_nieuwenhuis/nieuwenhuis_with_id.xls",
            "docs/nieuwenhuis/design-diagnostics.md",
            "renv.lock",
        ]:
            run.input(ROOT / name)
        for name in [
            "R/data.R",
            "R/journal_cohort.R",
            "R/design_diagnostics.R",
            "scripts/nieuwenhuis_design/diagnostics.R",
        ]:
            run.record["code"].append(fingerprint(ROOT / name))
        command = shlex.split(os.environ.get("RSCRIPT", "Rscript --vanilla"))
        subprocess.run(
            command + ["scripts/nieuwenhuis_design/diagnostics.R"], cwd=ROOT, check=True
        )
        for name in [
            "design_characteristics.csv",
            "study_type_support.csv",
            "species_support.csv",
            "design_models.csv",
            "equal_flagged_estimates.csv",
            "equal_flagged_influence.csv",
            "balance.csv",
            "estimation_weights.csv",
            "diagnostics.md",
            "diagnostics_status.json",
        ]:
            run.output(run.data / name)
        for name in [
            "tabs/design_diagnostics_estimates.tex",
            "tabs/design_diagnostics_macros.json",
            "tabs/design_diagnostics_macros.tex",
        ]:
            run.output(ROOT / name)
        status = json.loads((run.data / "diagnostics_status.json").read_text())
        run.check("full_roster", status["full_papers"] == 153, status)
        run.check("supported_target", status["matched_flagged"] == 68, status)
        run.check("supported_comparisons", status["matched_comparison"] == 52, status)
        run.check(
            "species_population",
            status["species_flagged"] == 49 and status["species_comparison"] == 46,
            status,
        )
        run.check("model_grid", status["models"] == 20, status)
        run.check("equal_flagged_grid", status["equal_flagged_estimates"] == 10, status)
        run.record["metrics"] = status


if __name__ == "__main__":
    main()
