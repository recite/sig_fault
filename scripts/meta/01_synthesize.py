"""Synthesize methodological audits independently of replication outcomes."""

import json
import os
import shlex
import subprocess

from scripts.research_pipeline import ROOT, Run, fingerprint


def main():
    with Run(
        "meta", "01_synthesize", __file__, True, data_dir=ROOT / "data/meta"
    ) as run:
        for name in [
            "docs/meta/assessment-design.md",
            "data/meta/lazic_components.csv",
            "data/meta/lazic_component_identities.csv",
            "data/meta/audit_contrasts.csv",
            "data/nieuwenhuis/source_models.csv",
            "data/lazic/estimates.csv",
            "data/cohorts/hmx/pipeline/panel.csv",
            "data/cohorts/hmx/assessments.csv",
            "data/cohorts/hmx/pipeline/paper_assessments.csv",
            "renv.lock",
        ]:
            run.input(ROOT / name)
        for name in [
            "scripts/meta/methodological.R",
            "R/meta.R",
            "R/analysis.R",
            "R/hmx.R",
        ]:
            run.record["code"].append(fingerprint(ROOT / name))
        command = shlex.split(os.environ.get("META_RSCRIPT", "Rscript --vanilla")) + [
            "scripts/meta/methodological.R"
        ]
        subprocess.run(command, cwd=ROOT, check=True)
        for name in [
            "components",
            "synthesis",
            "sensitivity",
            "leave_one_out",
            "identities",
        ]:
            run.output(run.data / f"methodological_{name}.csv")
        run.output(run.data / "methodological_status.json")
        for name in [
            "tabs/methodological_macros.tex",
            "tabs/methodological_macros.json",
            "tabs/methodological_components.tex",
            "docs/meta/assessments.md",
        ]:
            run.output(ROOT / name)
        status = json.loads((run.data / "methodological_status.json").read_text())
        run.check("four_audits", len(status["studies"]) == 4, status["studies"])
        run.check(
            "no_replication_cohort", status["replication_cohorts_excluded"], status
        )
        run.record["metrics"] = status


if __name__ == "__main__":
    main()
