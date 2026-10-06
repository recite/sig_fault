"""Pre-period-validated synthetic controls for the supported annual-total cases."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import osqp
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/i4r"
OUT = BASE / "synthetic"


def read(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def write(name, rows):
    if not rows:
        raise ValueError(f"Empty output: {name}")
    with (OUT / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fit_weights(target, donors, ridge=1e-6):
    """Fit a convex combination; inputs contain fitting years only."""
    target, donors = np.asarray(target, float), np.asarray(donors, float)
    if (
        target.ndim != 1
        or donors.ndim != 2
        or len(target) != len(donors)
        or not len(target)
        or not donors.shape[1]
        or not np.isfinite(target).all()
        or not np.isfinite(donors).all()
        or (target < 0).any()
        or (donors < 0).any()
        or ridge <= 0
    ):
        raise ValueError("Invalid citation matrix or ridge penalty")
    scale = float(np.sqrt(np.mean(target**2))) or 1.0
    y, x = target / scale, donors / scale
    uniform = np.full(x.shape[1], 1 / x.shape[1])

    def objective(w):
        residual = x @ w - y
        return np.mean(residual**2) + ridge * (w @ w)

    def gradient(w):
        return 2 * x.T @ (x @ w - y) / len(y) + 2 * ridge * w

    n, t = x.shape[1], len(y)
    # Explicit residuals avoid subtracting nearly equal Gram-matrix terms.
    solver = osqp.OSQP()
    solver.setup(
        P=sparse.diags(np.r_[np.full(n, 2 * ridge), np.full(t, 2 / t)], format="csc"),
        q=np.zeros(n + t),
        A=sparse.vstack(
            [
                sparse.hstack([sparse.csc_matrix(x), -sparse.eye(t)]),
                sparse.csc_matrix(np.r_[np.ones(n), np.zeros(t)].reshape(1, -1)),
                sparse.hstack([sparse.eye(n), sparse.csc_matrix((n, t))]),
            ],
            format="csc",
        ),
        l=np.r_[y, 1, np.zeros(n)],
        u=np.r_[y, 1, np.full(n, np.inf)],
        verbose=False,
        eps_abs=1e-10,
        eps_rel=1e-10,
        max_iter=1000000,
        polishing=True,
        polish_refine_iter=10,
        delta=1e-12,
        adaptive_rho_interval=50,
    )
    result = solver.solve(raise_error=True)
    raw = result.x[:n]
    if np.min(raw) < -1e-8 or abs(raw.sum() - 1) > 1e-8:
        raise RuntimeError("Synthetic fit violates simplex constraints")
    w = np.maximum(raw, 0)
    w /= w.sum()
    grad = gradient(w)
    dual_gap = float(grad @ w - np.min(grad))
    if objective(w) > objective(uniform) + 1e-10 or dual_gap > ridge * 1e-4:
        raise RuntimeError(f"Synthetic fit fails optimality check: {dual_gap}")
    return w


def fit_case(target, donors, pre_count, ridge=1e-6):
    """Last row is +1; last pre-year is held out before the full refit."""
    if pre_count < 3:
        raise ValueError("At least three pre-years required")
    target, donors = np.asarray(target, float), np.asarray(donors, float)
    if len(target) != pre_count + 1 or len(donors) != len(target):
        raise ValueError("Expected pre-years and one post-year")
    if not np.isfinite(target).all() or not np.isfinite(donors).all():
        raise ValueError("Missing annual counts cannot be zero-filled")
    held_weights = fit_weights(target[: pre_count - 1], donors[: pre_count - 1], ridge)
    weights = fit_weights(target[:pre_count], donors[:pre_count], ridge)
    synthetic = donors @ weights
    gaps = target - synthetic
    return (
        weights,
        held_weights,
        synthetic,
        {
            "pre_rmspe": np.sqrt(np.mean(gaps[:pre_count] ** 2)),
            "heldout_actual": target[pre_count - 1],
            "heldout_prediction": donors[pre_count - 1] @ held_weights,
            "heldout_gap": target[pre_count - 1] - donors[pre_count - 1] @ held_weights,
            "post_actual": target[-1],
            "post_synthetic": synthetic[-1],
            "post_gap": gaps[-1],
            "gap_change": gaps[-1] - gaps[pre_count - 1],
            "max_weight": np.max(weights),
            "effective_donors": 1 / (weights @ weights),
        },
    )


def annual_matrix(index, ids, years):
    rows = []
    for year in years:
        values = []
        for article in ids:
            row = index.get((article, year))
            if row is None or row["status"] != "complete":
                raise ValueError(f"Incomplete annual history: {article}, {year}")
            value = int(row["citations"])
            if value < 0:
                raise ValueError("Negative annual count")
            values.append(value)
        rows.append(values)
    return np.array(rows, dtype=float)


def build():
    OUT.mkdir(exist_ok=True)
    articles = {
        r["article_id"]: r
        for name in ["articles.csv", "control_articles.csv"]
        for r in read(BASE / name)
    }
    counts = read(BASE / "aggregate/citations.csv")
    index = {(r["article_id"], int(r["year"])): r for r in counts}
    if len(index) != len(counts):
        raise ValueError("Duplicate annual counts")
    matched = {
        r["event_id"]
        for r in read(BASE / "aggregate/matches.csv")
        if r["horizon"] == "1"
    }
    candidates = read(BASE / "aggregate/match_candidates.csv")
    events = [r for r in read(BASE / "events.csv") if r["event_id"] in matched]
    summaries, weights, paths, support, eligibility = [], [], [], [], []
    for event in sorted(events, key=lambda r: r["event_id"]):
        eid, aid, year = event["event_id"], event["article_id"], int(event["year"])
        first = max(2017, int(articles[aid]["publication_date"][:4]) + 1)
        pre = list(range(first, year))
        pool = [r for r in candidates if r["event_id"] == eid and r["horizon"] == "1"]
        donors = []
        for row in pool:
            cid = row["control_id"]
            reason = row["reason"]
            if row["eligible"] == "yes" or reason == "citation_caliper":
                reason = (
                    "published_during_fitting_window"
                    if int(articles[cid]["publication_date"][:4]) >= first
                    else "eligible"
                )
            eligibility.append(dict(event_id=eid, control_id=cid, reason=reason))
            if reason == "eligible":
                donors.append(cid)
        donors.sort()
        if len(set(donors)) != len(donors):
            raise ValueError("Duplicate donor")
        state = "fit" if len(pre) >= 3 and len(donors) >= 2 else "insufficient_support"
        support.append(
            dict(
                event_id=eid,
                article_id=aid,
                title=articles[aid]["title"],
                disclosure_year=year,
                pre_years=";".join(map(str, pre)),
                n_pre=len(pre),
                donors=len(donors),
                status=state,
            )
        )
        if state != "fit":
            continue
        years = pre + [year + 1]
        matrix = annual_matrix(index, [aid] + donors, years)
        target, controls = matrix[:, 0], matrix[:, 1:]
        main = fit_case(target, controls, len(pre))
        largest = int(np.argmax(main[0]))
        for specification, penalty, keep in [
            ("main", 1e-6, list(range(len(donors)))),
            ("ridge_0.01", 0.01, list(range(len(donors)))),
            (
                "omit_largest_donor",
                1e-6,
                [i for i in range(len(donors)) if i != largest],
            ),
        ]:
            result = (
                main
                if specification == "main"
                else fit_case(target, controls[:, keep], len(pre), penalty)
            )
            w, held_w, synthetic, diagnostics = result
            summaries.append(
                dict(event_id=eid, specification=specification, **diagnostics)
            )
            for i, weight, holdout_weight in zip(keep, w, held_w):
                weights.append(
                    dict(
                        event_id=eid,
                        specification=specification,
                        control_id=donors[i],
                        weight=weight,
                        holdout_weight=holdout_weight,
                    )
                )
            for i, y in enumerate(years):
                paths.append(
                    dict(
                        event_id=eid,
                        specification=specification,
                        year=y,
                        event_time=y - year,
                        actual=target[i],
                        synthetic=synthetic[i],
                    )
                )
    for name, rows in [
        ("support.csv", support),
        ("donor_eligibility.csv", eligibility),
        ("estimates.csv", summaries),
        ("weights.csv", weights),
        ("paths.csv", paths),
    ]:
        write(name, rows)
    report(support, summaries)


def report(support, summaries):
    lines = [
        "# Synthetic controls for the supported I4R cases",
        "",
        "These retrospective checks use the same annual all-type citation data as "
        "the matched-case analysis. We replace three nearest controls with convex "
        "combinations of all structurally eligible donors, without the citation "
        "caliper or text ranking. The disclosure year is omitted. Each target has "
        "its own citation scale and counterfactual; the case gaps are not pooled.",
        "",
        "| Paper | Pre-years | Donors | Pre-fit RMS error | Held-out year: actual / "
        "predicted | Post year: actual / synthetic | Post gap | Change in gap |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    labels = {
        "dp_021_disclosure": "Parental leave",
        "dp_148_disclosure": "Fast internet",
        "dp_292_disclosure": "Inventor clusters",
        "dp_294_disclosure": "Electrification",
    }
    for row in support:
        eid = row["event_id"]
        if row["status"] != "fit":
            lines.append(
                f"| {labels.get(eid, eid)} | {row['pre_years']} | {row['donors']} | "
                "Not fit: fewer than three pre-years | — | — | — | — |"
            )
            continue
        r = next(
            s
            for s in summaries
            if s["event_id"] == eid and s["specification"] == "main"
        )
        lines.append(
            f"| {labels.get(eid, eid)} | {row['pre_years']} | {row['donors']} | "
            f"{r['pre_rmspe']:.2f} | {r['heldout_actual']:.1f} / "
            f"{r['heldout_prediction']:.1f} | {r['post_actual']:.1f} / "
            f"{r['post_synthetic']:.1f} | {r['post_gap']:+.1f} | "
            f"{r['gap_change']:+.1f} |"
        )
    main = {r["event_id"]: r for r in summaries if r["specification"] == "main"}
    tex = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Paper & Pre-fit RMSE & Held-out: actual / predicted "
        r"& Post: actual / synthetic & Gap \\",
        r"\midrule",
    ]
    for eid, r in main.items():
        tex.append(
            f"{labels[eid]} & {r['pre_rmspe']:.1f} & "
            f"{r['heldout_actual']:.1f} / {r['heldout_prediction']:.1f} & "
            f"{r['post_actual']:.1f} / {r['post_synthetic']:.1f} & "
            f"{r['post_gap']:+.1f} " + r"\\"
        )
    tex += [r"\bottomrule", r"\end{tabular}"]
    (ROOT / "tabs/i4r_synthetic.tex").write_text("\n".join(tex) + "\n")
    omit = next(
        r
        for r in summaries
        if r["event_id"] == "dp_148_disclosure"
        and r["specification"] == "omit_largest_donor"
    )
    macros = {
        "ScInternetGap": main["dp_148_disclosure"]["post_gap"],
        "ScInternetOmit": omit["post_gap"],
    }
    (ROOT / "tabs/i4r_synthetic_macros.tex").write_text(
        "\n".join(
            f"\\newcommand{{\\{key}}}{{{value:+.1f}}}" for key, value in macros.items()
        )
        + "\n"
    )
    lines += [
        "",
        "The held-out prediction fits weights on all but the last pre-disclosure "
        "year. The final synthetic path refits weights using every pre-year. "
        "Pre-fit error measures this final fit; it is not out-of-sample accuracy. "
        "Post gap is actual minus synthetic citations in the year after disclosure; "
        "change in gap subtracts the final pre-year gap. None is a significance test.",
        "",
        "## Sensitivity to donor weights",
        "",
        "| Paper | Specification | Post gap | Held-out prediction | Largest weight | "
        "Effective donors |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for r in summaries:
        lines.append(
            f"| {labels.get(r['event_id'], r['event_id'])} | {r['specification']} | "
            f"{r['post_gap']:+.1f} | {r['heldout_prediction']:.1f} | "
            f"{r['max_weight']:.3f} | {r['effective_donors']:.1f} |"
        )
    lines += [
        "",
        "The largest-donor check removes the donor with the largest weight in the "
        "full-pre-period main fit. Its held-out prediction therefore is a sensitivity "
        "calculation, not a clean validation prediction: that donor removal uses "
        "the last pre-year. The main held-out prediction and fixed-ridge prediction "
        "do not use that year's citations to fit or select donors.",
        "",
        "All donor weights and eligibility decisions are saved in "
        "[data/i4r/synthetic](../../data/i4r/synthetic). "
        "The [design](synthetic-design.md) defines the fitting, validation and "
        "sensitivity rules. Short histories and many possible donor combinations "
        "limit identification even when in-sample fit is close. A causal reading "
        "also requires no anticipation, no coincident target-specific shock and "
        "unexposed donors. These assumptions are not established by the optimization.",
    ]
    (ROOT / "docs/i4r/synthetic-results.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    build()
