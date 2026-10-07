"""Extract the historical 37-paper diagnostic table without backdating later labels."""

import collections
import json
import re
from string import Template

from scripts.research_pipeline import ROOT, Run, read_csv, unique, write_csv

DIAGNOSTICS = [
    "att_p_below_05",
    "pretrend_p_above_05",
    "equivalence_p_below_05",
    "placebo_p_above_05",
    "carryover_p_above_05",
]


def parse_summary(text):
    table = text.split(r"\label{tb:summary}", 1)[1].split(r"\end{tabular}", 1)[0]
    rows = []
    values = {
        "x": "true",
        "": "false",
        "n.a.": "not_applicable",
        "n.a": "not_applicable",
    }
    for line in table.splitlines():
        line = line.split("%", 1)[0].strip()
        key = re.search(r"\\citet\{([^}]+)\}", line)
        if not key:
            continue
        cells = [x.strip() for x in line.rstrip("\\").split("&")]
        if len(cells) != 13:
            raise ValueError("Unexpected diagnostic-table width: " + key[1])
        row = dict(citation_key=key[1], journal=cells[1])
        for diagnostic, value in zip(DIAGNOSTICS, cells[8:]):
            if value not in values:
                raise ValueError("Unrecognized diagnostic: " + repr(value))
            row[diagnostic] = values[value]
        row["primary_flag"] = {
            "true": "comparison",
            "false": "flagged",
            "not_applicable": "unknown",
        }[row["pretrend_p_above_05"]]
        rows.append(row)
    unique(rows, ["citation_key"])
    return rows


def main():
    with Run("panel", "02_assessments", __file__, True) as run:
        run.require("01_get")
        path = run.input(run.cache / "extracted/sm.tex")
        rows = parse_summary(path.read_text())
        counts = collections.Counter(x["primary_flag"] for x in rows)
        run.check("historical_roster", len(rows) == 37, len(rows))
        run.check(
            "historical_pretrend_groups",
            counts == {"flagged": 8, "comparison": 25, "unknown": 4},
            dict(counts),
        )
        path = run.data / "historical_assessments.csv"
        write_csv(path, rows, list(rows[0]))
        run.output(path)
        summary = []
        for name in DIAGNOSTICS:
            for value, count in sorted(
                collections.Counter(x[name] for x in rows).items()
            ):
                summary.append(
                    dict(diagnostic=name, source_outcome=value, papers=count)
                )
        path = run.data / "historical_diagnostic_counts.csv"
        write_csv(path, summary, ["diagnostic", "source_outcome", "papers"])
        run.output(path)
        run.check(
            "roundtrip",
            read_csv(run.data / "historical_assessments.csv") == rows,
            len(rows),
        )
        template = Template(run.input(run.data / "README.in.md").read_text())
        final = read_csv(run.input(ROOT / "data/cohorts/panel/papers.csv"))
        path = run.data / "README.md"
        path.write_text(
            template.substitute(historical=len(rows), final=len(final), **dict(counts))
        )
        run.output(path)
        run.record["metrics"] = dict(
            historical_papers=len(rows), primary_counts=dict(counts)
        )
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
