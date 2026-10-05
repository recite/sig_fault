"""Match disclosed-error articles using pre-disclosure inputs only."""

from __future__ import annotations

import argparse
import collections

import i4r_registry as registry
import i4r_sources as sources
import numpy as np
import pilot
from sklearn.feature_extraction.text import TfidfVectorizer

MATCH_FIELDS = [
    "event_id",
    "article_id",
    "control_id",
    "rank",
    "distance",
    "weight",
    "horizon",
]
CANDIDATE_FIELDS = [
    "event_id",
    "article_id",
    "control_id",
    "distance",
    "eligible",
    "reason",
    "horizon",
]


def citation_index(rows):
    pilot.unique(rows, ["article_id", "year"])
    return {(r["article_id"], int(r["year"])): r for r in rows}


def count(index, article, year):
    row = index.get((article, year))
    if row is None or row["status"] != "complete":
        return None
    value = int(row["citations"])
    if value < 0:
        raise ValueError("Negative citation count")
    return value


def eligible_events(events, articles, cutoff, horizon):
    eligible, exclusions = [], []
    first = {}
    for r in sorted(
        events,
        key=lambda r: (
            int(r["year"]) if r.get("year") else 9999,
            r.get("date", ""),
            r["event_id"],
        ),
    ):
        if (
            r.get("year")
            and r["error_verified"] == "yes"
            and r["material"] == "yes"
            and r["publicity_verified"] == "yes"
        ):
            first.setdefault(r["article_id"], r["event_id"])
    by_id = {r["article_id"]: r for r in articles}
    for row in events:
        reason = ""
        if row["article_id"] in first and first[row["article_id"]] != row["event_id"]:
            reason = "subsequent_disclosure"
        elif row["error_verified"] != "yes" or row["material"] != "yes":
            reason = "error_not_verified_material"
        elif row["publicity_verified"] != "yes":
            reason = "publicity_unverified"
        elif row["already_retracted"] != "no":
            reason = "retraction_status_not_eligible"
        elif not row["year"]:
            reason = "unknown_event_year"
        elif row["article_id"] not in by_id:
            reason = "article_unresolved"
        elif by_id[row["article_id"]].get("identity_verified") != "yes":
            reason = "article_identity_unverified"
        elif int(row["year"]) + horizon > cutoff:
            reason = "incomplete_followup"
        elif not by_id[row["article_id"]].get("publication_date"):
            reason = "publication_date_unresolved"
        elif (
            int(by_id[row["article_id"]]["publication_date"][:4])
            >= int(row["year"]) - 2
        ):
            reason = "insufficient_article_age"
        if reason:
            exclusions.append(
                dict(
                    event_id=row["event_id"],
                    article_id=row["article_id"],
                    reason=reason,
                    horizon=horizon,
                )
            )
        else:
            eligible.append(row)
    # First disclosure per article, never one treated unit per repeated critique.
    earliest = {}
    for row in sorted(
        eligible, key=lambda r: (int(r["year"]), r.get("date", ""), r["event_id"])
    ):
        if row["article_id"] in earliest:
            exclusions.append(
                dict(
                    event_id=row["event_id"],
                    article_id=row["article_id"],
                    reason="subsequent_disclosure",
                    horizon=horizon,
                )
            )
        else:
            earliest[row["article_id"]] = row
    return list(earliest.values()), exclusions


def match(
    articles,
    events,
    citations,
    assessments,
    cutoff=2025,
    horizon=1,
    k=3,
    control_ids=None,
    complete_risk_sets=None,
):
    pilot.unique(articles, ["article_id"])
    pilot.unique(events, ["event_id"])
    index = citation_index(citations)
    lookup = {r["article_id"]: r for r in articles}
    exposures = collections.defaultdict(list)
    for r in assessments:
        if r.get("public_year"):
            exposures[r["article_id"]].append(int(r["public_year"]))
    for r in events:
        if r.get("year"):
            exposures[r["article_id"]].append(int(r["year"]))
    selected, excluded = eligible_events(events, articles, cutoff, horizon)
    matches, candidates, balance = [], [], []
    for event in selected:
        if (
            complete_risk_sets is not None
            and event["event_id"] not in complete_risk_sets
        ):
            excluded.append(
                dict(
                    event_id=event["event_id"],
                    article_id=event["article_id"],
                    reason="incomplete_risk_set_retrieval",
                    horizon=horizon,
                )
            )
            continue
        treated = lookup[event["article_id"]]
        year = int(event["year"])
        past = [year - 2, year - 1]
        tv = [count(index, treated["article_id"], y) for y in past]
        if any(v is None for v in tv):
            excluded.append(
                dict(
                    event_id=event["event_id"],
                    article_id=treated["article_id"],
                    reason="incomplete_pre_citations",
                    horizon=horizon,
                )
            )
            continue
        pool = []
        for r in articles:
            if r["article_id"] == treated["article_id"]:
                continue
            if control_ids is not None and r["article_id"] not in control_ids:
                continue
            if (
                not r.get("journal_id")
                or r["journal_id"] != treated.get("journal_id")
                or r["type"] != treated["type"]
            ):
                continue
            if abs(int(r["publication_year"]) - int(treated["publication_year"])) > 1:
                continue
            reason = ""
            if r.get("identity_verified") != "yes":
                reason = "identity_unverified"
            elif any(y <= year + horizon for y in exposures[r["article_id"]]):
                reason = "known_public_assessment_in_window"
            elif (
                r.get("retraction_date")
                and int(r["retraction_date"][:4]) <= year + horizon
            ):
                reason = "known_retraction_in_window"
            elif r.get("retracted") == "yes" and not r.get("retraction_date"):
                reason = "retraction_date_unresolved"
            elif (
                not r.get("publication_date")
                or int(r["publication_date"][:4]) >= year - 2
            ):
                reason = "insufficient_article_age"
            cv = [count(index, r["article_id"], y) for y in past]
            if not reason and any(v is None for v in cv):
                reason = "incomplete_pre_citations"
            if reason:
                candidates.append(
                    dict(
                        event_id=event["event_id"],
                        article_id=treated["article_id"],
                        control_id=r["article_id"],
                        distance="",
                        eligible="no",
                        reason=reason,
                        horizon=horizon,
                    )
                )
            else:
                pool.append((r, cv))
        if not pool:
            excluded.append(
                dict(
                    event_id=event["event_id"],
                    article_id=treated["article_id"],
                    reason="no_eligible_risk_set",
                    horizon=horizon,
                )
            )
            continue
        records = [treated] + [r for r, _ in pool]
        raw = np.log1p(np.array([tv] + [v for _, v in pool], dtype=float))
        numeric = np.column_stack([raw, raw[:, 1] - raw[:, 0]])
        sd = numeric.std(axis=0, ddof=1)
        delta = np.divide(
            numeric[1:] - numeric[0], sd, out=np.zeros_like(numeric[1:]), where=sd > 0
        )
        text = [
            " ".join([r.get("title", ""), r.get("abstract", "")]).strip()
            for r in records
        ]
        try:
            vectors = TfidfVectorizer(stop_words="english").fit_transform(text)
            cosine = 1 - (vectors[1:] @ vectors[0].T).toarray().ravel()
        except ValueError:
            cosine = np.ones(len(pool))
        text_sd = np.std(np.r_[0, cosine], ddof=1)
        text_distance = cosine / text_sd if text_sd > 0 else np.zeros(len(pool))
        distance = np.sqrt((delta**2).sum(axis=1) + text_distance**2)
        accepted = []
        for j, (r, _) in enumerate(pool):
            valid = bool((np.abs(delta[j]) <= 1 + 1e-12).all())
            candidates.append(
                dict(
                    event_id=event["event_id"],
                    article_id=treated["article_id"],
                    control_id=r["article_id"],
                    distance=float(distance[j]),
                    eligible="yes" if valid else "no",
                    reason="" if valid else "citation_caliper",
                    horizon=horizon,
                )
            )
            if valid:
                accepted.append((float(distance[j]), r["article_id"], j))
        best = sorted(accepted)[:k]
        if not best:
            excluded.append(
                dict(
                    event_id=event["event_id"],
                    article_id=treated["article_id"],
                    reason="no_match_within_caliper",
                    horizon=horizon,
                )
            )
        for rank, (dist, cid, j) in enumerate(best, 1):
            matches.append(
                dict(
                    event_id=event["event_id"],
                    article_id=treated["article_id"],
                    control_id=cid,
                    rank=rank,
                    distance=dist,
                    weight=1 / len(best),
                    horizon=horizon,
                )
            )
            balance.append(
                dict(
                    event_id=event["event_id"],
                    control_id=cid,
                    pre2_smd=delta[j, 0],
                    pre1_smd=delta[j, 1],
                    change_smd=delta[j, 2],
                    text_cosine_distance=cosine[j],
                    horizon=horizon,
                )
            )
    return matches, candidates, excluded, balance


def panel(matches, events, citations):
    index = citation_index(citations)
    event_map = {r["event_id"]: r for r in events}
    stacks, omissions = [], []
    grouped = collections.defaultdict(list)
    for row in matches:
        grouped[(row["event_id"], int(row["horizon"]))].append(row)
    for (eid, horizon), rows in grouped.items():
        e = event_map[eid]
        year = int(e["year"])
        members = [(e["article_id"], 1, 1.0)] + [
            (r["control_id"], 0, float(r["weight"])) for r in rows
        ]
        periods = [-1, horizon]
        required = sorted(set([-1, 1, horizon]))
        if any(
            count(index, aid, year + t) is None
            for aid, _, _ in members
            for t in required
        ):
            omissions.append(
                dict(
                    event_id=eid, horizon=horizon, reason="incomplete_outcome_retrieval"
                )
            )
            continue
        for aid, treated, weight in members:
            for t in periods:
                stacks.append(
                    dict(
                        stack_id=eid + "_h" + str(horizon),
                        event_id=eid,
                        warning_id=e["warning_id"],
                        article_id=aid,
                        year=year + t,
                        event_time=t,
                        horizon=horizon,
                        treated=treated,
                        post=int(t > 0),
                        weight=weight,
                        citations=count(index, aid, year + t),
                    )
                )
    return stacks, omissions


def sensitivity_panels(matches, events, citations, articles=()):
    article_map = {r["article_id"]: r for r in articles}
    index = citation_index(citations)
    event_map = {r["event_id"]: r for r in events}
    groups = collections.defaultdict(list)
    for r in matches:
        groups[(r["event_id"], int(r["horizon"]))].append(r)
    out = []
    for (eid, horizon), rows in groups.items():
        e = event_map[eid]
        year = int(e["year"])
        full_members = [e["article_id"]] + [r["control_id"] for r in rows]
        if any(
            count(index, aid, year + t) is None
            for aid in full_members
            for t in set([-1, 1, horizon])
        ):
            continue
        specs = []
        if horizon == 1:
            specs += [
                ("placebo_pre2_pre1", [-2], [-1], rows),
                ("average_pre2_pre1", [-2, -1], [1], rows),
                ("one_control", [-1], [1], [min(rows, key=lambda r: int(r["rank"]))]),
            ]
        if horizon == 1 and all(
            article_map.get(aid, {}).get("publication_year")
            and int(article_map[aid]["publication_year"]) < year - 3
            for aid in full_members
        ):
            specs.append(("placebo_pre3_pre2", [-3], [-2], rows))
        if horizon == 1 and len(e.get("date", "")) == 10:
            half = "first" if int(e["date"][5:7]) <= 6 else "second"
            specs.append(("disclosure_" + half + "_half", [-1], [1], rows))
        if horizon in [2, 3]:
            specs.append((f"year1_fixed_h{horizon}_cohort", [-1], [1], rows))
        if horizon == 2:
            specs.append(("average_post1_post2", [-1], [1, 2], rows))
        for name, before, after, selected in specs:
            members = [(e["article_id"], 1, 1.0)] + [
                (r["control_id"], 0, 1 / len(selected)) for r in selected
            ]
            if any(
                count(index, aid, year + t) is None
                for aid, _, _ in members
                for t in before + after
            ):
                continue
            for aid, treated, weight in members:
                for post, periods in [(0, before), (1, after)]:
                    out.append(
                        dict(
                            specification=name,
                            stack_id=eid + "_" + name,
                            event_id=eid,
                            warning_id=e["warning_id"],
                            article_id=aid,
                            horizon=horizon,
                            treated=treated,
                            post=post,
                            weight=weight,
                            citations=sum(count(index, aid, year + t) for t in periods)
                            / len(periods),
                        )
                    )
    return out


def trajectories(matches, events, citations, articles=()):
    article_map = {r["article_id"]: r for r in articles}
    index = citation_index(citations)
    event_map = {r["event_id"]: r for r in events}
    groups = collections.defaultdict(list)
    for r in matches:
        if int(r["horizon"]) == 1:
            groups[r["event_id"]].append(r)
    rows = []
    for eid, selected in groups.items():
        e = event_map[eid]
        members = [(e["article_id"], 1, 1.0)] + [
            (r["control_id"], 0, float(r["weight"])) for r in selected
        ]
        for aid, treated, weight in members:
            for t in range(-3, 4):
                value = count(index, aid, int(e["year"]) + t)
                rows.append(
                    dict(
                        event_id=eid,
                        article_id=aid,
                        treated=treated,
                        weight=weight,
                        event_time=t,
                        citations="" if value is None else value,
                        status=(
                            "missing"
                            if value is None
                            else (
                                "partial_publication_year"
                                if article_map.get(aid, {}).get("publication_year")
                                and int(article_map[aid]["publication_year"])
                                >= int(e["year"]) + t
                                else "complete"
                            )
                        ),
                        disclosure_date=e.get("date", ""),
                        date_precision=e.get("date_precision", ""),
                    )
                )
    return rows


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cutoff", type=int, default=2025)
    p.add_argument("--controls", type=int, default=3)
    args = p.parse_args()
    articles = sources.read("articles.csv") + sources.read("control_articles.csv")
    events, citations = sources.read("events.csv"), sources.read("citations.csv")
    article_lookup = {r["article_id"]: r for r in articles}
    event_lookup = {r["event_id"]: r for r in events}
    all_matches, all_candidates, all_excluded, all_balance = [], [], [], []
    for horizon in [1, 2, 3]:
        m, c, e, b = match(
            articles,
            events,
            citations,
            sources.read("assessments.csv"),
            args.cutoff,
            horizon,
            args.controls,
            control_ids={r["article_id"] for r in sources.read("control_articles.csv")},
            complete_risk_sets={
                r["event_id"]
                for r in sources.read("risk_set_retrieval.csv")
                if r["status"] == "complete"
                and r["event_id"] in event_lookup
                and r.get("query_filter")
                == registry.risk_filter(
                    article_lookup[event_lookup[r["event_id"]]["article_id"]]
                )
            },
        )
        all_matches.extend(m)
        all_candidates.extend(c)
        all_excluded.extend(e)
        all_balance.extend(b)
    sources.write("matches.csv", all_matches, MATCH_FIELDS)
    sources.write("match_candidates.csv", all_candidates, CANDIDATE_FIELDS)
    sources.write(
        "match_exclusions.csv",
        all_excluded,
        ["event_id", "article_id", "reason", "horizon"],
    )
    sources.write(
        "match_balance.csv",
        all_balance,
        [
            "event_id",
            "control_id",
            "pre2_smd",
            "pre1_smd",
            "change_smd",
            "text_cosine_distance",
            "horizon",
        ],
    )
    rows, omissions = panel(all_matches, events, citations)
    sources.write(
        "analysis_panel.csv",
        rows,
        [
            "stack_id",
            "event_id",
            "warning_id",
            "article_id",
            "year",
            "event_time",
            "horizon",
            "treated",
            "post",
            "weight",
            "citations",
        ],
    )
    sources.write("panel_exclusions.csv", omissions, ["event_id", "horizon", "reason"])
    sensitivity = sensitivity_panels(all_matches, events, citations, articles)
    sources.write(
        "sensitivity_panel.csv",
        sensitivity,
        [
            "specification",
            "stack_id",
            "event_id",
            "warning_id",
            "article_id",
            "horizon",
            "treated",
            "post",
            "weight",
            "citations",
        ],
    )
    sources.write(
        "event_trajectories.csv",
        trajectories(all_matches, events, citations, articles),
        [
            "event_id",
            "article_id",
            "treated",
            "weight",
            "event_time",
            "citations",
            "status",
            "disclosure_date",
            "date_precision",
        ],
    )
    print(
        "Matched events:",
        len({r["event_id"] for r in all_matches}),
        "panel rows:",
        len(rows),
    )
