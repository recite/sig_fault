"""Estimate synthetic DiD with complete article bootstrap and source receipts."""

import json
import os
import shlex
import subprocess

from scripts.research_pipeline import ROOT, Run, fingerprint


def main():
    with Run(
        "lazic_sdid", "02_estimate", __file__, True, data_dir=ROOT / "data/lazic/sdid"
    ) as run:
        run.require("01_prepare")
        run.input(ROOT / "renv.lock")
        for name in ["R/synthetic_did.R", "scripts/lazic_sdid/estimate.R"]:
            run.record["code"].append(fingerprint(ROOT / name))
        command = shlex.split(os.environ.get("RSCRIPT", "Rscript --vanilla"))
        subprocess.run(
            command + ["scripts/lazic_sdid/estimate.R"], cwd=ROOT, check=True
        )
        for name in [
            "estimates.csv",
            "placebos.csv",
            "paths.csv",
            "paper_weights.csv",
            "time_weights.csv",
            "balance.csv",
            "bootstrap.csv",
            "bootstrap_indices.csv",
            "models.rds",
            "R-session.txt",
            "estimation_status.json",
        ]:
            run.output(run.data / name)
        status = json.loads((run.data / "estimation_status.json").read_text())
        run.check("all_specifications", status["models"] == 4, status)
        run.check("bootstrap_complete", status["bootstrap_draws"] == 7996, status)
        run.record["metrics"] = status


if __name__ == "__main__":
    main()
