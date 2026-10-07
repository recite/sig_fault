"""Reproduce the broader synthesis from frozen public data and record its inputs."""

import json
import os
import shlex
import subprocess

from scripts.research_pipeline import ROOT, Run, fingerprint


def main():
    with Run(
        "meta", "01_synthesize", __file__, True, data_dir=ROOT / "data/meta"
    ) as run:
        inputs = [
            "docs/meta/assessment-design.md",
            "docs/meta/assessments.in.md",
            "data/meta/lazic_components.csv",
            "data/meta/lazic_component_identities.csv",
            "data/meta/audit_contrasts.csv",
            "data/lazic/estimates.csv",
            "data/nieuwenhuis/source_models.csv",
            "data/nieuwenhuis/status.json",
            "data/cohorts/rpp/pipeline/panel.csv",
            "data/cohorts/rpp/pipeline/identities.csv",
            "data/cohorts/rpp/pipeline/estimates.csv",
            "data/cohorts/rpp/pipeline/external_estimates.csv",
            "renv.lock",
        ]
        for path in inputs:
            run.input(ROOT / path)
        for path in ["scripts/meta/synthesize.R", "R/meta.R", "R/rpp.R"]:
            run.record["code"].append(fingerprint(ROOT / path))
        command = shlex.split(os.environ.get("META_RSCRIPT", "Rscript")) + [
            "scripts/meta/synthesize.R"
        ]
        run.record["estimation_command"] = command
        subprocess.run(command, cwd=ROOT, check=True)
        status = json.loads((run.data / "assessment_status.json").read_text())
        for name in [
            "four_distinct_studies",
            "no_known_original_overlap",
            "rpp_reproduced",
        ]:
            run.check(name, status[name], status[name])
        for name in [
            "assessment_components.csv",
            "assessment_synthesis.csv",
            "assessment_sensitivity.csv",
            "assessment_leave_one_out.csv",
            "assessment_identities.csv",
            "rpp_timing.csv",
            "assessment_status.json",
            "assessment_session.txt",
        ]:
            run.output(run.data / name)
        for path in [
            "tabs/assessment_macros.tex",
            "tabs/assessment_macros.json",
            "tabs/assessment_summary.tex",
            "tabs/assessment_components.tex",
            "tabs/rpp_summary.tex",
            "docs/meta/assessments.md",
        ]:
            run.output(ROOT / path)
        run.record["metrics"] = status
        print(json.dumps(status))


if __name__ == "__main__":
    main()
