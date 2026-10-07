"""Build a dated-work source comparison on the fixed historical paper cohort."""

import argparse
import collections
import json
import math

import nieuwenhuis as nw
import nieuwenhuis_validation as validation
import pilot

WORK_FIELDS = [
    "paper_id",
    "work_id",
    "identifiers",
    "raw_relationships",
    "year",
    "date_status",
    "ocis",
]
PANEL_FIELDS = [
    "article_id",
    "paper_id",
    "year",
    "flag",
    "cohort",
    "journal",
    "wos",
    "opencitations",
    "status",
    "undated_works",
    "conflicting_year_works",
]


def merge_works(edges):
    """Merge within a target by shared OMID or DOI; never choose conflicting years."""
    grouped = collections.defaultdict(list)
    for row in edges:
        grouped[row["paper_id"]].append(row)
    result = []
    for pid, records in sorted(grouped.items()):
        parent = list(range(len(records)))

        def root(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        seen = {}
        tokens = []
        for i, row in enumerate(records):
            ids = {"omid:" + v for v in validation.identifiers(row["citing"], "omid:")}
            if not ids:
                raise ValueError("Citing work lacks OMID")
            ids |= {
                "doi:" + pilot.normalize_doi(v)
                for v in validation.identifiers(row["citing"], "doi:")
            }
            tokens.append(ids)
            for token in ids:
                if token in seen:
                    parent[root(i)] = root(seen[token])
                seen[token] = i
        components = collections.defaultdict(list)
        for i in range(len(records)):
            components[root(i)].append(i)
        for indices in components.values():
            years = {
                int(records[i]["creation"][:4])
                for i in indices
                if records[i]["creation"]
            }
            ids = sorted(set().union(*(tokens[i] for i in indices)))
            result.append(
                dict(
                    paper_id=pid,
                    work_id=min(v for v in ids if v.startswith("omid:")),
                    identifiers=" ".join(ids),
                    raw_relationships=len(indices),
                    year=next(iter(years)) if len(years) == 1 else "",
                    date_status=(
                        "dated"
                        if len(years) == 1
                        else "conflicting_years" if years else "undated"
                    ),
                    ocis=";".join(sorted(records[i]["oci"] for i in indices)),
                )
            )
    pilot.unique(result, ["paper_id", "work_id"])
    return result


def make_panel(historical, works, coverage):
    pilot.unique(historical, ["paper_id", "year"])
    pilot.unique(coverage, ["paper_id"])
    complete = {r["paper_id"] for r in coverage if r["complete"] == "yes"}
    counts = collections.Counter(
        (r["paper_id"], str(r["year"])) for r in works if r["date_status"] == "dated"
    )
    missing = collections.Counter(
        r["paper_id"] for r in works if r["date_status"] != "dated"
    )
    conflicts = collections.Counter(
        r["paper_id"] for r in works if r["date_status"] == "conflicting_years"
    )
    return [
        {
            k: r[k]
            for k in [
                "article_id",
                "paper_id",
                "year",
                "flag",
                "cohort",
                "journal",
                "wos",
            ]
        }
        | dict(
            opencitations=(
                counts[r["paper_id"], r["year"]] if r["paper_id"] in complete else ""
            ),
            status="complete" if r["paper_id"] in complete else "missing_history",
            undated_works=missing[r["paper_id"]] if r["paper_id"] in complete else "",
            conflicting_year_works=(
                conflicts[r["paper_id"]] if r["paper_id"] in complete else ""
            ),
        )
        for r in historical
    ]


def build():
    historical = nw.read("paired_panel.csv")
    frame = {r["paper_id"] for r in historical}
    identities = {r["paper_id"]: r for r in nw.read("identities.csv")}
    coverage = [r for r in nw.read("validation_coverage.csv") if r["paper_id"] in frame]
    complete = {r["paper_id"] for r in coverage if r["complete"] == "yes"}
    edges = [r for r in nw.read("validation_edges.csv") if r["paper_id"] in complete]
    by_paper = collections.defaultdict(list)
    for r in edges:
        by_paper[r["paper_id"]].append(r)
    for r in coverage:
        if r["doi"] != identities[r["paper_id"]]["doi"]:
            raise ValueError("Coverage belongs to another target DOI")
        if r["complete"] == "yes":
            selected = by_paper[r["paper_id"]]
            validation.validate_response(selected, int(r["reported_count"]), r["doi"])
            if len(selected) != int(r["records"]):
                raise ValueError("Coverage count differs from raw relationships")
    works = merge_works(edges)
    panel = make_panel(historical, works, coverage)
    pilot.write_csv(nw.DATA / "opencitations_works.csv", works, WORK_FIELDS)
    pilot.write_csv(nw.DATA / "opencitations_panel.csv", panel, PANEL_FIELDS)
    metadata = {r["paper_id"]: r for r in historical}
    status = dict(
        historical_papers=len(frame),
        complete_histories=len(complete),
        complete_flagged=sum(metadata[p]["flag"] == "1" for p in complete),
        complete_comparison=sum(metadata[p]["flag"] == "0" for p in complete),
        full_cohort_available=complete == frame,
        raw_relationships=len(edges),
        distinct_citing_work_relationships=len(works),
        merged_relationships=len(edges) - len(works),
        undated_works=sum(r["date_status"] != "dated" for r in works),
        conflicting_year_works=sum(
            r["date_status"] == "conflicting_years" for r in works
        ),
        outcome=(
            "Distinct dated citing works recorded by OpenCitations, "
            "all document types"
        ),
        limitation=(
            "Undated works remain unassigned; API completeness is not "
            "completeness of real citations."
        ),
    )
    (nw.DATA / "opencitations_status.json").write_text(
        json.dumps(status, indent=2) + "\n"
    )
    print(json.dumps(status))


def report():
    status = json.loads((nw.DATA / "opencitations_status.json").read_text())
    contrasts = nw.read("opencitations_contrasts.csv")
    periods = nw.read("opencitations_period_summary.csv")
    main = [
        r
        for r in contrasts
        if r["sample"] == "Available histories" and r["cohort"] == "Historical cohort"
    ]
    full = next(
        r for r in main if r["estimand"] == "log_ratio" and r["post"] == "2012-2015"
    )
    if not status["full_cohort_available"]:
        raise ValueError("Full-cohort report requires all historical histories")

    def pct(value):
        return 100 * math.expm1(float(value))

    macros = dict(
        NwOcPapers=status["complete_histories"],
        NwOcUndated=status["undated_works"],
        NwOcPercent=f"{pct(full['alternative']):.1f}",
        NwOcWosPercent=f"{pct(full['wos']):.1f}",
        NwOcDifference=f"{pct(full['difference']):.1f}",
        NwOcDifferenceLower=f"{pct(full['lower']):.1f}",
        NwOcDifferenceUpper=f"{pct(full['upper']):.1f}",
    )
    (pilot.ROOT / "tabs/nieuwenhuis_opencitations_macros.tex").write_text(
        "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in macros.items())
    )
    lines = [
        "# The neuroscience comparison using OpenCitations",
        "",
        f"Changing the citation source leaves the full-cohort growth comparison "
        f"almost unchanged: {pct(full['alternative']):.1f}% using OpenCitations "
        f"and {pct(full['wos']):.1f}% using the historical Web of Science exports.",
        "These estimates compare flagged and comparison papers' post/pre citation "
        "ratios, with 2010 as baseline and the 2012–2015 annual average afterward.",
        "",
        f"All {status['historical_papers']} historical papers have complete API "
        f"histories: {status['complete_flagged']} flagged and "
        f"{status['complete_comparison']} comparison papers. The index supplies "
        f"{status['raw_relationships']:,} incoming relationships across all years. "
        f"Of these, {status['undated_works']} have no resolved publication year "
        "and remain unassigned to annual outcomes. Complete acquisition does not "
        "mean complete real-world citation coverage.",
        "",
        "## Citation levels on the same papers",
        "",
        "| Source | Group | Papers | Mean 2010 | Mean 2012–15 | "
        "Median 2010 | Median of paper post averages |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in periods:
        if (r["sample"], r["cohort"], r["post"]) != (
            "Available histories",
            "Historical cohort",
            "2012-2015",
        ):
            continue
        label = "Web of Science" if r["source"] == "wos" else "OpenCitations"
        group = "Flagged" if r["flag"] == "1" else "Comparison"
        cells = [label, group, r["papers"]] + [
            f"{float(r[k]):.2f}"
            for k in ["mean_before", "mean_after", "median_before", "median_after"]
        ]
        lines.append("| " + " | ".join(cells) + " |")
    lines += [
        "",
        "Both sources record continued citation in both groups. "
        "OpenCitations records more citations in the baseline and post periods. "
        "That difference does not translate into a large change in their "
        "relative-growth comparison. Post medians above summarize each paper's "
        "annual post-period average; annual medians are available separately.",
        "",
        "## Paired source discrepancies",
        "",
        "| Post years | Contrast | Web of Science | OpenCitations | "
        "Source discrepancy | Paired 95% interval |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for r in main:
        transform = float if r["estimand"] == "absolute" else pct
        values = [
            transform(r[k])
            for k in ["wos", "alternative", "difference", "lower", "upper"]
        ]
        unit = (
            "Absolute citation change"
            if r["estimand"] == "absolute"
            else "Growth ratio (%)"
        )
        lines.append(
            f"| {r['post']} | {unit} | {values[0]:.2f} | {values[1]:.2f} | "
            f"{values[2]:.2f} | [{values[3]:.2f}, {values[4]:.2f}] |"
        )
    lines += [
        "",
        "The absolute discrepancy subtracts the two difference-in-changes "
        "estimates. The proportional discrepancy is the percentage change in the "
        "estimated growth ratio when replacing Web of Science with OpenCitations; "
        "it is not the percentage-point difference between displayed estimates. "
        "Intervals use 9,999 paired paper resamples within flag groups, seed "
        "20261006. They condition on this cohort and the frozen database records.",
        "",
        "## Dating and scope",
        "",
        "The [full results](../../data/nieuwenhuis/opencitations_contrasts.csv) "
        "also restrict both sources to the same histories without unresolved "
        "publication years and separately to the 2009 publication cohort. "
        "The date-complete subset is selected; it is not another full-cohort estimate. "
        "No missing year is imputed or assumed to lie outside the analysis window.",
        "",
        "OpenCitations counts dated citing works across document types. This is "
        "different from the OpenAlex article/review comparison. Shared "
        "upstream records, coverage, vintage and dating differences prevent "
        "calling either index ground truth. Similar aggregate contrasts do not "
        "validate every citation link or establish that publicity had no effect. "
        "This is another measurement of the same audit, not another independent "
        "study for the meta-analysis.",
        "",
        "## Reproduce",
        "",
        "```sh",
        "make nieuwenhuis-opencitations",
        "```",
        "",
        "Acquisition is separate: `make nieuwenhuis-opencitations-fetch`. "
        "The collector uses the documented CSV representation when a large JSON "
        "response arrives truncated. Both formats undergo the same target-DOI, "
        "unique-relationship and count-endpoint checks. Cached raw responses, "
        "URLs, retrieval times and hashes are preserved.",
        "",
        "See [design](design.md), [dictionary](data.md), "
        "[annual summaries](../../data/nieuwenhuis/opencitations_annual_summary.csv), "
        "[panel](../../data/nieuwenhuis/opencitations_panel.csv), and "
        "[API documentation](https://api.opencitations.net/index/v2).",
    ]
    (pilot.ROOT / "docs/nieuwenhuis/opencitations.md").write_text(
        "\n".join(lines) + "\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["build", "report"], default="build", nargs="?"
    )
    args = parser.parse_args()
    build() if args.command == "build" else report()
