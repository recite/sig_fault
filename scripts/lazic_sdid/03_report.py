"""Render synthetic DiD estimates and validation checks without re-estimation."""

import json
import os
import shlex
import subprocess

from scripts.research_pipeline import ROOT, Run, fingerprint, read_csv


def main():
    with Run(
        "lazic_sdid",
        "03_report",
        __file__,
        True,
        data_dir=ROOT / "data/lazic/sdid",
    ) as run:
        run.require("02_estimate")
        run.record["code"].append(fingerprint(ROOT / "scripts/lazic_sdid/report.R"))
        command = shlex.split(os.environ.get("RSCRIPT", "Rscript --vanilla"))
        subprocess.run(command + ["scripts/lazic_sdid/report.R"], cwd=ROOT, check=True)
        estimates = read_csv(run.data / "estimates.csv")
        main = next(r for r in estimates if r["specification"] == "main")
        macros = json.loads((ROOT / "tabs/lazic_sdid_macros.json").read_text())
        for field, macro in [
            ("estimate", "LazicSdidEstimate"),
            ("lower", "LazicSdidLower"),
            ("upper", "LazicSdidUpper"),
        ]:
            run.check(
                "generated_" + field,
                float(macros[macro]) == round(float(main[field]), 2),
                dict(model=main[field], displayed=macros[macro]),
            )
        for name in [
            "data/lazic/sdid/README.md",
            "tabs/lazic_sdid.tex",
            "tabs/lazic_sdid_macros.tex",
            "tabs/lazic_sdid_macros.json",
            "figs/lazic_sdid.pdf",
        ]:
            run.output(ROOT / name)


if __name__ == "__main__":
    main()
