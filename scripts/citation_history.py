"""Shared OpenAlex citation acquisition, link validation, and annual counts."""

import collections

from scripts import pilot
from scripts.research_pipeline import query, unique

CUTOFF = "2025-12-31"
FIELDS = "id,doi,title,publication_date,publication_year,type,referenced_works"


def normalize_history(paper, target, works, canonical=None, summary_doi=""):
    if pilot.normalize_doi(target.get("doi") or "") != paper["doi"]:
        raise ValueError("Target DOI mismatch: " + paper["paper_id"])
    unique(works, ["id"])
    edges, by_doi = [], collections.defaultdict(set)
    for work in works:
        doi = pilot.normalize_doi(work.get("doi") or "")
        date, year = work.get("publication_date"), work.get("publication_year")
        reasons = []
        if target["id"] not in work.get("referenced_works", []):
            reasons.append("reference_not_verified")
        if not date or not year or str(year) != date[:4]:
            reasons.append("missing_or_conflicting_date")
        elif date > CUTOFF or date < target["publication_date"]:
            reasons.append("outside_date_window")
        if work["id"] == target["id"]:
            reasons.append("same_work")
        if doi:
            by_doi[doi].add((str(year), work["type"]))
        edges.append(
            dict(
                paper_id=paper["paper_id"],
                target_work_id=target["id"],
                citing_work_id=work["id"],
                doi=doi,
                title=work.get("title") or "",
                publication_date=date or "",
                publication_year=year or "",
                type=work["type"],
                project_summary=bool(summary_doi) and doi == summary_doi,
                exclusion_reason=";".join(reasons),
                duplicate_of="",
            )
        )
    canonical = canonical or {}
    conflicts = {doi for doi, values in by_doi.items() if len(values) > 1}
    for doi in conflicts:
        chosen = canonical.get(doi)
        eligible = [r for r in edges if r["doi"] == doi and not r["exclusion_reason"]]
        if not chosen or chosen not in {r["citing_work_id"] for r in eligible}:
            raise ValueError(
                "Conflicting DOI lacks a verified canonical citing work: " + doi
            )
    seen = dict(canonical)
    for row in sorted(edges, key=lambda x: x["citing_work_id"]):
        if row["exclusion_reason"]:
            continue
        if row["doi"] in seen:
            if row["citing_work_id"] != seen[row["doi"]]:
                row["duplicate_of"] = seen[row["doi"]]
        elif row["doi"]:
            seen[row["doi"]] = row["citing_work_id"]
    return edges


def acquire(run, paper):
    target = run.fetch(
        "https://api.openalex.org/works/https://doi.org/" + paper["doi"],
        "openalex_targets",
    )
    cursor, seen, totals, works = "*", set(), set(), []
    while cursor:
        if cursor in seen:
            raise ValueError("Repeated citation cursor")
        seen.add(cursor)
        url = query(
            "https://api.openalex.org/works",
            filter=f"cites:{target['id'].split('/')[-1]},"
            f"to_publication_date:{CUTOFF}",
            per_page=100,
            cursor=cursor,
            select=FIELDS,
            sort="publication_date",
        )
        payload = run.fetch(url, "citation_pages")
        totals.add(payload["meta"]["count"])
        works.extend(payload["results"])
        cursor = payload["meta"].get("next_cursor")
        if not payload["results"]:
            break
    if len(totals) != 1 or len(works) != next(iter(totals)):
        raise ValueError("Incomplete or changing citation history")
    by_doi = collections.defaultdict(list)
    for w in works:
        doi = pilot.normalize_doi(w.get("doi") or "")
        if doi:
            by_doi[doi].append(w)
    canonical, decisions = {}, []
    for doi, group in by_doi.items():
        if len({(w.get("publication_year"), w.get("type")) for w in group}) > 1:
            record = run.fetch(
                "https://api.openalex.org/works/https://doi.org/" + doi,
                "canonical_citing_works",
            )
            if pilot.normalize_doi(record.get("doi") or "") != doi:
                raise ValueError("Canonical citing DOI disagreement")
            canonical[doi] = record["id"]
            decisions.append(
                dict(
                    paper_id=paper["paper_id"],
                    doi=doi,
                    canonical_id=record["id"],
                    candidate_ids=";".join(sorted(w["id"] for w in group)),
                    candidate_years=";".join(
                        str(w.get("publication_year")) for w in group
                    ),
                    basis=(
                        "OpenAlex DOI singleton; selected ID must have "
                        "verified target reference"
                    ),
                )
            )
    edges = normalize_history(
        paper, target, works, canonical, paper.get("assessment_doi", "")
    )
    return (
        edges,
        decisions,
        dict(
            paper_id=paper["paper_id"],
            doi=paper["doi"],
            target_work_id=target["id"],
            complete=True,
            reported_records=len(works),
            pages=len(seen),
            detail="",
            is_retracted=target.get("is_retracted", ""),
            target_type=target.get("type", ""),
        ),
    )


def make_panel(papers, coverage, edges, start_year=2008):
    unique(papers, ["paper_id"])
    unique(coverage, ["paper_id"])
    unique(edges, ["paper_id", "citing_work_id"])
    ids = {p["paper_id"] for p in papers}
    if ids != {r["paper_id"] for r in coverage} or any(
        e["paper_id"] not in ids for e in edges
    ):
        raise ValueError("Citation panel has unknown or missing target identities")
    edge_counts = collections.Counter(e["paper_id"] for e in edges)
    for c in coverage:
        if str(c["complete"]).lower() == "true" and edge_counts[c["paper_id"]] != int(
            c["reported_records"]
        ):
            raise ValueError("Completed history count does not match citation links")
    complete = {r["paper_id"] for r in coverage if str(r["complete"]).lower() == "true"}
    counts, broad = collections.Counter(), collections.Counter()
    for e in edges:
        if e["exclusion_reason"] or e["duplicate_of"]:
            continue
        key = e["paper_id"], int(e["publication_year"])
        broad[key] += 1
        if e["type"] in {"article", "review"}:
            counts[key] += 1
    return [
        dict(
            paper_id=p["paper_id"],
            journal=p["journal"],
            role=p["role"],
            year=y,
            citations=counts[p["paper_id"], y] if p["paper_id"] in complete else "",
            all_types=broad[p["paper_id"], y] if p["paper_id"] in complete else "",
            status="complete" if p["paper_id"] in complete else "missing_history",
        )
        for p in papers
        for y in range(start_year, 2026)
    ]
