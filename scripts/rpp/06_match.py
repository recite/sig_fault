"""Match on pre-publicity citation paths and fit constrained synthetic controls."""

import json

import numpy as np
from scipy.optimize import minimize

from scripts.research_pipeline import Run, read_csv, unique, write_csv

PRE_YEARS = range(2010, 2015)


def synthetic_weights(target, donors):
    """Ridge-stabilized simplex fit; inputs contain pre-event outcomes only."""
    n = len(donors)
    ridge = 1e-6
    initial = np.full(n, 1 / n)
    fit = minimize(
        lambda w: np.mean((w @ donors - target) ** 2) + ridge * np.sum(w**2),
        initial,
        jac=lambda w: 2 * donors @ (w @ donors - target) / donors.shape[1]
        + 2 * ridge * w,
        bounds=[(0, 1)] * n,
        constraints={
            "type": "eq",
            "fun": lambda w: w.sum() - 1,
            "jac": lambda w: np.ones(n),
        },
        method="SLSQP",
        options={"maxiter": 2000, "ftol": 1e-10},
    )
    if not fit.success or abs(fit.x.sum() - 1) > 1e-7 or min(fit.x) < -1e-9:
        raise ValueError("Synthetic-control optimization failed: " + fit.message)
    weights = np.maximum(fit.x, 0)
    weights /= weights.sum()
    return weights


def select_matches(papers, panel, coverage):
    unique(panel, ["paper_id", "year"])
    counts = {(x["paper_id"], int(x["year"])): x for x in panel}
    metadata = {x["paper_id"]: x for x in coverage}
    usable, exclusions = [], []
    for p in papers:
        missing = any(
            counts[p["paper_id"], y]["status"] != "complete" for y in PRE_YEARS
        )
        retracted = str(metadata[p["paper_id"]]["is_retracted"]).lower() == "true"
        nonarticle = metadata[p["paper_id"]]["target_type"] not in {"article", "review"}
        reason = "incomplete_pre_history" if missing else ""
        if p["role"] == "external_control":
            if retracted:
                reason = "currently_retracted_donor"
            elif nonarticle:
                reason = "nonarticle_donor"
        if reason:
            exclusions.append(
                dict(paper_id=p["paper_id"], role=p["role"], reason=reason)
            )
        else:
            usable.append(p)
    nearest, synthetic, fit_rows, candidates = [], [], [], []
    for journal in sorted({p["journal"] for p in usable}):
        donors = sorted(
            [
                p
                for p in usable
                if p["journal"] == journal and p["role"] == "external_control"
            ],
            key=lambda p: p["doi"],
        )
        targets = [
            p
            for p in usable
            if p["journal"] == journal and p["role"] != "external_control"
        ]
        if len(donors) < 3:
            raise ValueError("Fewer than three usable same-journal donors: " + journal)
        raw = np.array(
            [
                [float(counts[p["paper_id"], y]["citations"]) for y in PRE_YEARS]
                for p in donors
            ]
        )
        log = np.log1p(raw)
        scale = np.std(log, axis=0, ddof=1)
        scale[scale == 0] = 1
        raw_scale = np.std(raw, axis=0, ddof=1)
        raw_scale[raw_scale == 0] = 1
        for p in targets:
            actual = np.array(
                [float(counts[p["paper_id"], y]["citations"]) for y in PRE_YEARS]
            )
            target = np.log1p(actual) / scale
            donor_features = log / scale
            distance = np.sqrt(np.mean((donor_features - target) ** 2, axis=1))
            order = sorted(
                range(len(donors)), key=lambda i: (distance[i], donors[i]["doi"])
            )
            for rank, i in enumerate(order, 1):
                row = dict(
                    paper_id=p["paper_id"],
                    control_id=donors[i]["paper_id"],
                    journal=journal,
                    rank=rank,
                    distance=distance[i],
                )
                candidates.append(row)
                if rank <= 3:
                    nearest.append(row | dict(weight=1 / 3))
            weights = synthetic_weights(actual / raw_scale, raw / raw_scale)
            for i, w in enumerate(weights):
                synthetic.append(
                    dict(
                        paper_id=p["paper_id"],
                        control_id=donors[i]["paper_id"],
                        journal=journal,
                        weight=w,
                    )
                )
            matched = raw[order[:3]].mean(axis=0)
            predicted = weights @ raw
            fit_rows.append(
                dict(
                    paper_id=p["paper_id"],
                    journal=journal,
                    role=p["role"],
                    donors=len(donors),
                    original_pre_mean=actual.mean(),
                    matched_pre_mean=matched.mean(),
                    synthetic_pre_mean=predicted.mean(),
                    matched_pre_rmse=np.sqrt(np.mean((actual - matched) ** 2)),
                    synthetic_pre_rmse=np.sqrt(np.mean((actual - predicted) ** 2)),
                    synthetic_effective_donors=1 / np.sum(weights**2),
                )
            )
    return nearest, synthetic, fit_rows, candidates, exclusions


def main():
    with Run("rpp", "06_match", __file__, True) as run:
        run.require("05_citations")
        run.input(run.data / "design.md")
        papers = read_csv(run.data / "citation_targets.csv")
        panel = read_csv(run.data / "panel.csv")
        coverage = read_csv(run.data / "citation_coverage.csv")
        nearest, synthetic, fits, candidates, exclusions = select_matches(
            papers, panel, coverage
        )
        run.check(
            "matched_weight_sums",
            all(
                abs(
                    sum(
                        float(x["weight"])
                        for x in nearest
                        if x["paper_id"] == p["paper_id"]
                    )
                    - 1
                )
                < 1e-10
                for p in fits
            ),
            len(fits),
        )
        for name, rows, fields in [
            ("matches.csv", nearest, list(nearest[0])),
            ("synthetic_weights.csv", synthetic, list(synthetic[0])),
            ("match_fit.csv", fits, list(fits[0])),
            ("match_candidates.csv", candidates, list(candidates[0])),
            ("match_exclusions.csv", exclusions, ["paper_id", "role", "reason"]),
        ]:
            path = run.data / name
            write_csv(path, rows, fields)
            run.output(path)
        run.record["metrics"] = dict(
            matched_targets=len(fits),
            donor_exclusions=len(exclusions),
            matching_years=list(PRE_YEARS),
            nearest_neighbors=3,
            synthetic_ridge=1e-6,
        )
        run.record["unresolved"] = exclusions
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
