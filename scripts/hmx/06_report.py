"""Generate the study report and manuscript numbers from verified estimates."""

import json
import math
from string import Template

from scripts.research_pipeline import ROOT, Run, read_csv, write_json


def main():
    with Run("hmx", "06_report", __file__, True) as run:
        run.require("05_analyze")
        estimates = read_csv(run.data / "estimates.csv")
        primary = next(x for x in estimates if x["specification"] == "primary")
        pooled = next(x for x in estimates if x["specification"] == "nonoverlap")
        levels = read_csv(run.data / "period_summary.csv")
        omitted = read_csv(run.data / "leave_one_out.csv")
        absolute = read_csv(run.data / "absolute_estimates.csv")[0]
        bootstrap = read_csv(run.data / "bootstrap.csv")[0]
        macros = {}
        for prefix, row in [("Hmx", primary), ("HmxMeta", pooled)]:
            for suffix, column in [
                ("Percent", "percent"),
                ("Lower", "percent_lower"),
                ("Upper", "percent_upper"),
            ]:
                macros[prefix + suffix] = f"{float(row[column]):.1f}"
        macros["HmxReduction"] = f"{-float(primary['percent']):.1f}"
        for prefix, row in [("Hmx", primary), ("HmxMeta", pooled)]:
            macros[prefix + "Contributing"] = str(
                int(row["n_flagged"]) + int(row["n_comparison"])
            )
        for x in levels:
            prefix = "HmxFlagged" if x["flag"] == "1" else "HmxComparison"
            macros[prefix + "Papers"] = x["papers"]
            for suffix, column in [
                ("MeanBefore", "before_mean"),
                ("MeanAfter", "after_mean"),
                ("MedianBefore", "before_median"),
                ("MedianAfter", "after_median"),
            ]:
                macros[prefix + suffix] = f"{float(x[column]):.1f}"
        for suffix, column in [
            ("Absolute", "estimate"),
            ("AbsoluteLower", "lower"),
            ("AbsoluteUpper", "upper"),
        ]:
            macros["Hmx" + suffix] = f"{float(absolute[column]):.1f}"
        macros["HmxBootLower"] = f"{float(bootstrap['percent_lower']):.1f}"
        macros["HmxBootUpper"] = f"{float(bootstrap['percent_upper']):.1f}"
        for suffix, function in [("LooMin", min), ("LooMax", max)]:
            macros["Hmx" + suffix] = (
                f"{function(float(x['percent']) for x in omitted):.1f}"
            )
        labels = {
            "primary": "Primary: 2017 versus 2019",
            "nonoverlap": "Exclude paper already in IV audit",
            "longer_followup": "Follow-up averaged over 2019–2021",
            "all_types": "All citing document types",
            "prior_trend": "Earlier trend: 2015 versus 2017",
            "linearity": "Linearity diagnostic",
            "low_high": "Low/high nonrejection diagnostic",
            "journal_support": "Journal/year effects on supported journals",
            "no_earlier_critique": "Exclude Malesky's previously criticized paper",
        }
        rows = []
        for x in estimates:
            rows.append(
                f"| {labels[x['specification']]} | "
                f"{x['n_flagged']} / {x['n_comparison']} | "
                f"{float(x['percent']):.1f} "
                f"[{float(x['percent_lower']):.1f}, "
                f"{float(x['percent_upper']):.1f}] |"
            )
        template = Template(run.input(run.data / "README.in.md").read_text())
        report = template.substitute(**macros, specifications="\n".join(rows))
        run.check(
            "finite_numeric_macros",
            all(math.isfinite(float(value)) for value in macros.values()),
            len(macros),
        )
        run.check(
            "ordered_model_intervals",
            all(
                float(x["percent_lower"])
                <= float(x["percent"])
                <= float(x["percent_upper"])
                for x in estimates
            ),
            len(estimates),
        )
        path = run.data / "README.md"
        path.write_text(report)
        run.output(path)
        path = ROOT / "tabs/hmx_macros.json"
        write_json(path, macros)
        run.output(path)
        path = ROOT / "tabs/hmx_macros.tex"
        path.write_text(
            "".join(
                f"\\newcommand{{\\{name}}}{{{value}}}\n"
                for name, value in macros.items()
            )
        )
        run.output(path)
        run.record["metrics"] = dict(reported_specifications=len(estimates))
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
