"""Reconstruct two-period clustered uncertainty from article citation changes."""

import math
from collections import defaultdict

from scripts.research_pipeline import ROOT, Run, read_csv, unique, write_csv, write_json


def paired(rows, id_key, year_key, flag_key, before, after):
    selected = [r for r in rows if int(r[year_key]) in {before, after}]
    unique(selected, [id_key, year_key])
    groups = defaultdict(dict)
    for row in selected:
        groups[row[id_key]][int(row[year_key])] = row
    result = []
    for key, years in groups.items():
        if set(years) != {before, after}:
            raise ValueError("Incomplete paired history: " + key)
        a, b = years[before], years[after]
        if a[flag_key] != b[flag_key]:
            raise ValueError("Time-varying classification: " + key)
        result.append(
            dict(
                paper_id=key,
                flag=int(a[flag_key]),
                before=float(a["citations"]),
                after=float(b["citations"]),
            )
        )
    return result


def diagnose(rows):
    unique(rows, ["paper_id"])
    if any(r["flag"] not in {0, 1} for r in rows):
        raise ValueError("Classification must be binary")
    if any(not math.isfinite(r[t]) for r in rows for t in ["before", "after"]):
        raise ValueError("Non-finite citations")
    if any(r["before"] < 0 or r["after"] < 0 for r in rows):
        raise ValueError("Negative citations")
    rows = [dict(r) for r in rows if r["before"] + r["after"] > 0]
    totals = {
        g: {t: sum(r[t] for r in rows if r["flag"] == g) for t in ["before", "after"]}
        for g in [0, 1]
    }
    if any(value <= 0 for group in totals.values() for value in group.values()):
        raise ValueError("Undefined group citation ratio")
    for row in rows:
        group = totals[row["flag"]]
        row["influence"] = (1 if row["flag"] else -1) * (
            row["after"] / group["after"] - row["before"] / group["before"]
        )
    variance = sum(r["influence"] ** 2 for r in rows)
    n = len(rows)
    if n <= 2:
        raise ValueError("Too few articles")
    adjustment = n / (n - 1) * (2 * n - 1) / (2 * n - 3)
    for row in rows:
        row["variance_share"] = row["influence"] ** 2 / variance if variance else 0
    rows.sort(key=lambda r: (-r["variance_share"], r["paper_id"]))
    beta = math.log(totals[1]["after"] / totals[1]["before"]) - math.log(
        totals[0]["after"] / totals[0]["before"]
    )
    return (
        dict(
            estimate=beta,
            se=math.sqrt(variance * adjustment),
            flagged=sum(r["flag"] for r in rows),
            comparison=sum(1 - r["flag"] for r in rows),
            finite_sample_adjustment=adjustment,
            flagged_variance_share=sum(r["variance_share"] for r in rows if r["flag"]),
            top_one_variance_share=rows[0]["variance_share"],
            top_five_variance_share=sum(r["variance_share"] for r in rows[:5]),
        ),
        rows,
    )


def main():
    with Run(
        "meta", "02_precision", __file__, True, data_dir=ROOT / "data/meta"
    ) as run:

        def read(name):
            return read_csv(run.input(ROOT / name))

        nw = paired(
            read("data/derived/panel.csv"), "article_id", "year", "flag", 2010, 2012
        )
        lal = paired(
            read("data/lal/panel.csv"), "paper_id", "citation_year", "weak", 2023, 2025
        )
        lazic = [
            dict(
                paper_id=r["paper_id"],
                flag=int(r["flag"]),
                before=float(r["before"]),
                after=float(r["after"]),
            )
            for r in read("data/lazic/paper_changes.csv")
            if r["specification"] == "first_followup_year"
        ]
        labels = {
            r["paper_id"]: r
            for r in read("data/cohorts/hmx/pipeline/paper_assessments.csv")
        }
        hmx = [
            dict(
                r, flag=int(labels[r["paper_id"]]["severe_extrapolation"] == "flagged")
            )
            for r in read("data/cohorts/hmx/pipeline/panel.csv")
            if labels[r["paper_id"]]["meta_eligible"] == "True"
        ]
        hmx = paired(hmx, "paper_id", "year", "flag", 2017, 2019)
        published = {
            r["audit"]: r
            for r in read("data/meta/methodological_components.csv")
            if r["lal_diagnostic"] == "Effective F below 10"
            and r["nieuwenhuis_source"] == "historical"
        }
        estimates, influences = [], []
        for audit, pairs in [
            ("Nieuwenhuis", nw),
            ("Lal", lal),
            ("Lazic", lazic),
            ("HMX", hmx),
        ]:
            estimate, rows = diagnose(pairs)
            run.check(
                "coefficient_reproduced",
                abs(estimate["estimate"] - float(published[audit]["estimate"])) < 1e-7,
                audit,
            )
            run.check(
                "clustered_se_reproduced",
                abs(estimate["se"] - float(published[audit]["se"])) < 1e-7,
                audit,
            )
            estimates.append(
                dict(audit=audit, weight=float(published[audit]["weight"]), **estimate)
            )
            influences.extend(dict(audit=audit, **r) for r in rows)
        for name, rows in [
            ("precision_components.csv", estimates),
            ("precision_article_influence.csv", influences),
        ]:
            write_csv(run.data / name, rows, list(rows[0]))
            run.output(run.data / name)
        precision = sum(1 / x["se"] ** 2 for x in estimates)
        beta = sum(x["estimate"] / x["se"] ** 2 for x in estimates) / precision
        se = 1 / math.sqrt(precision)
        status = dict(
            log_contrast=beta,
            se=se,
            percent=100 * math.expm1(beta),
            lower=100 * math.expm1(beta - 1.959963984540054 * se),
            upper=100 * math.expm1(beta + 1.959963984540054 * se),
            source="Independent paired-count sandwich calculation",
            interpretation=(
                "Sampling/model uncertainty conditional on comparison assumptions; "
                "not a bound on confounding"
            ),
        )
        write_json(run.data / "precision_status.json", status)
        run.output(run.data / "precision_status.json")
        report = [
            "# Where the uncertainty comes from",
            "",
            (
                "This check reconstructs the four article-clustered standard "
                "errors directly"
            ),
            (
                "from paired citation counts. It does not assume the publicity "
                "comparisons are causal."
            ),
            "",
            (
                "| Audit | Flagged / comparison | Log-scale SE | Weight, % | "
                "Variance from top article, % | Variance from top five, % |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
        report.extend(
            (
                f'| {r["audit"]} | {r["flagged"]} / {r["comparison"]} | '
                f'{r["se"]:.3f} | {100*r["weight"]:.1f} | '
                f'{100*r["top_one_variance_share"]:.1f} | '
                f'{100*r["top_five_variance_share"]:.1f} |'
            )
            for r in estimates
        )
        report.extend(
            [
                "",
                (
                    "The independent calculation gives a pooled contrast of "
                    f'{status["percent"]:.1f}% [{status["lower"]:.1f}, '
                    f'{status["upper"]:.1f}]%, with log-scale SE {se:.4f}.'
                ),
                (
                    "The fixed-effect interval uses a normal critical value. It is not "
                    "wide because"
                ),
                (
                    "a four-study t critical value was applied or because "
                    "random-effects heterogeneity"
                ),
                (
                    "was added. Most uncertainty comes from variation in article-level "
                    "citation changes."
                ),
                "",
                (
                    "For article i in group g, the normalized change is its share of "
                    "the group's"
                ),
                (
                    "post citations minus its share of the group's pre citations. The "
                    "squared"
                ),
                (
                    "normalized changes sum to the unadjusted variance of the log "
                    "ratio contrast."
                ),
                "Multiplying by G/(G−1) × (2G−1)/(2G−3) reproduces the fitted model's",
                (
                    "article-clustered finite-sample adjustment, where G counts "
                    "contributing articles."
                ),
                (
                    "All-zero pairs do not identify that coefficient. Variance shares "
                    "diagnose"
                ),
                "concentration; they are not a reason to delete influential papers.",
                "",
                (
                    "These intervals condition on the model and comparison. They do "
                    "not include"
                ),
                (
                    "uncertainty from unobserved earlier disclosure, confounding "
                    "trends, or treating"
                ),
                (
                    "different diagnostic labels as a common exposure. Reproducible "
                    "calculation is"
                ),
                "separate from identification of a publicity effect.",
            ]
        )
        path = ROOT / "docs/meta/precision.md"
        path.write_text("\n".join(report) + "\n")
        run.output(path)
        run.record["metrics"] = status


if __name__ == "__main__":
    main()
