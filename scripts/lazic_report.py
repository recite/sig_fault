"""Report the frozen Lazic audit comparisons and their measurement limits."""

import json

import lazic
import pilot


def main():
    absolute = {
        r["specification"]: r
        for r in pilot.read_csv(lazic.DATA / "absolute_changes.csv")
    }
    ratios = {
        r["specification"]: r for r in pilot.read_csv(lazic.DATA / "estimates.csv")
    }
    groups = {
        r["flag"]: r
        for r in pilot.read_csv(lazic.DATA / "summary.csv")
        if r["specification"] == "primary"
    }
    status = json.loads((lazic.DATA / "opencitations/status.json").read_text())
    registry = json.loads((lazic.DATA / "status.json").read_text())
    a, r = absolute["primary"], ratios["primary"]
    f, c = groups["1"], groups["0"]
    values = {
        "LazicFlagged": f["papers"],
        "LazicComparison": c["papers"],
        "LazicFlaggedBefore": f["mean_before"],
        "LazicFlaggedAfter": f["mean_after"],
        "LazicComparisonBefore": c["mean_before"],
        "LazicComparisonAfter": c["mean_after"],
        "LazicFlaggedMedianBefore": f["median_before"],
        "LazicFlaggedMedianAfter": f["median_after"],
        "LazicComparisonMedianBefore": c["median_before"],
        "LazicComparisonMedianAfter": c["median_after"],
        "LazicAbsolute": a["estimate"],
        "LazicAbsoluteLower": a["lower"],
        "LazicAbsoluteUpper": a["upper"],
        "LazicPercent": r["percent"],
        "LazicLower": r["lower"],
        "LazicUpper": r["upper"],
    }
    stratified = pilot.read_csv(lazic.DATA / "stratified.csv")[0]
    values.update(
        {
            "LazicLinks": status["raw_edges"],
            "LazicUndated": status["uncertain_date_works"],
            "LazicStratified": stratified["estimate"],
            "LazicStratifiedLower": stratified["lower"],
            "LazicStratifiedUpper": stratified["upper"],
        }
    )
    counts = {
        "LazicPapers": registry["source_papers"],
        "LazicAssessedFlagged": registry["classification_counts"]["pseudoreplication"],
        "LazicAssessedComparison": registry["classification_counts"][
            "correct_analysis"
        ],
        "LazicUnclear": registry["classification_counts"]["unclear"],
        "LazicClassified": registry["classified_comparison_papers"],
        "LazicDoiPapers": registry["with_doi"],
        "LazicNoDoiPapers": registry["source_papers"] - registry["with_doi"],
        "LazicZeroPapers": (
            len(r["excluded_papers"].split(";")) if r["excluded_papers"] else 0
        ),
        "LazicOlderFlagged": absolute["older_cohort"]["n_flagged"],
        "LazicOlderComparison": absolute["older_cohort"]["n_comparison"],
        "LazicReviewedChapters": len(pilot.read_csv(lazic.DATA / "book_review.csv")),
    }
    values.update(counts)
    formatted_values = {}
    for key, value in values.items():
        if (
            key in {"LazicFlagged", "LazicComparison", "LazicLinks", "LazicUndated"}
            or key in counts
            or "Median" in key
        ):
            formatted_values[key] = str(int(float(value)))
        else:
            precision = 1 if key in {"LazicPercent", "LazicLower", "LazicUpper"} else 2
            formatted_values[key] = f"{float(value):.{precision}f}"
    (pilot.ROOT / "tabs/lazic_macros.tex").write_text(
        "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in formatted_values.items())
    )
    (pilot.ROOT / "tabs/lazic_macros.json").write_text(
        json.dumps(formatted_values, indent=2) + "\n"
    )
    (lazic.DATA / "analysis_status.json").write_text(
        json.dumps(
            dict(
                status="estimated_first_known_publicity_comparison",
                baseline=2016,
                post_year=2019,
                flagged_papers=int(f["papers"]),
                comparison_papers=int(c["papers"]),
                primary_citation_source=(
                    "OpenCitations distinct indexed works, all types"
                ),
                prior_warning_excluded=["23449593"],
                interpretation=(
                    "Descriptive contrast; causal interpretation requires comparable"
                    " counterfactual trajectories"
                ),
                synthesis="data/meta/lazic_synthesis.csv",
            ),
            indent=2,
        )
        + "\n"
    )
    table = []
    for flag, label in [("1", "Flagged"), ("0", "Comparison")]:
        g = groups[flag]
        table.append(
            f"| {label} | {g['papers']} | {float(g['mean_before']):.2f} | "
            f"{float(g['mean_after']):.2f} | {float(g['median_before']):g} | "
            f"{float(g['median_after']):g} |"
        )
    variations = []
    for name, fit in absolute.items():
        ratio = ratios[name]
        variations.append(
            f"| {name} | {fit['n_flagged']} / {fit['n_comparison']} |"
            f" {float(fit['estimate']):.2f} [{float(fit['lower']):.2f},"
            f" {float(fit['upper']):.2f}] | {float(ratio['percent']):.1f}"
            f" [{float(ratio['lower']):.1f}, {float(ratio['upper']):.1f}] |"
        )
    text = "\n".join(
        [
            "# Citation changes after the pseudoreplication audit",
            "",
            (
                f"Citation histories are complete for {status['complete_histories']} of"
                f" 200 audited papers. The primary comparison includes {f['papers']}"
                f" flagged and {c['papers']} correctly analyzed papers. The 64 unclear"
                " assessments remain outside the comparison; one flagged paper had"
                " already received a public warning about the same statistical problem"
                " in 2013."
            ),
            "",
            (
                "The first public preprint appeared September 2, 2017, the identified"
                " dataset on September 6, and the journal article on April 4, 2018. The"
                " primary contrast compares 2016 with 2019."
            ),
            "",
            "| Group | Papers | Mean 2016 | Mean 2019 | Median 2016 | Median 2019 |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
            *table,
            "",
            (
                "Flagged papers' mean citation change minus comparison papers' mean"
                f" change is {float(a['estimate']):.2f} citations per paper (95% Welch"
                f" interval [{float(a['lower']):.2f}, {float(a['upper']):.2f}]). The"
                f" proportional contrast is {float(r['percent']):.1f}%"
                f" ([{float(r['lower']):.1f}, {float(r['upper']):.1f}]%), estimated by"
                " Poisson pseudo-maximum likelihood with article and year fixed"
                " effects and article-clustered uncertainty."
            ),
            "",
            (
                "The absolute contrast compares changes in citation counts. The"
                " proportional contrast compares the groups’ post/pre ratios. Both"
                " require comparable counterfactual citation trajectories for a causal"
                " interpretation. These are source-assessed methodological problems;"
                " corrected numerical results are not supplied. Citations do not"
                " establish endorsement or reliance on the affected finding."
            ),
            "",
            "![Mean and median citation trajectories](citation_paths.png)",
            "",
            "## Sensitivity checks",
            "",
            (
                "| Specification | Flagged / comparison | Absolute difference [95%"
                " interval] | Proportional difference, % [95% interval] |"
            ),
            "| --- | ---: | ---: | ---: |",
            *variations,
            "",
            (
                "The full-cohort sensitivity includes the earlier-warning paper. The"
                " erratum sensitivity excludes all papers with linked prior errata,"
                " including corrections unrelated to statistical results. The older"
                " cohort was published by 2013; its pretrend contrast compares 2014"
                " with 2016. The longer post period averages 2019–2021. The"
                " first-follow-up-year contrast uses 2018, the year after the first"
                " public release but the year of journal publication."
            ),
            "",
            (
                "See the [split-unit-standardized"
                " contrast](../../data/lazic/stratified.csv), [whole-paper bootstrap"
                " intervals](../../data/lazic/bootstrap.csv), and [analysis"
                " design](design.md). Uncertain citing-publication dates remain"
                " unassigned. Counts include all indexed document types, including"
                " chapters; collection completeness refers to the API response, not to"
                " every citation in the literature."
            ),
            "",
        ]
    )
    text += (
        f"The primary Poisson fit uses {r['n_flagged']} flagged and {r['n_comparison']}"
        " comparison papers. Ten papers have zero citations in both selected years and"
        " contribute no information to its proportional coefficient; they remain in"
        " the absolute contrast and descriptive summaries. The exported estimates list"
        " every excluded paper.\n"
    )
    (pilot.ROOT / "docs/lazic/results.md").write_text(text)


if __name__ == "__main__":
    main()
