"""Acquire citation links and build a panel from complete histories."""

import argparse
import collections
import concurrent.futures
import json

from scripts import pilot
from scripts.research_pipeline import Run, query, read_csv, unique, write_csv

CUTOFF = "2025-12-31"
FIELDS = "id,doi,title,publication_date,publication_year,type,referenced_works"


def normalize_history(paper, target, works, canonical=None):
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
                project_summary=doi == "10.1126/science.aac4716",
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
    edges = normalize_history(paper, target, works, canonical)
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


def make_panel(papers, coverage, edges):
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
        for y in range(2008, 2026)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    with Run("rpp", "05_citations", __file__, args.offline) as run:
        run.require("04_controls")
        run.require("03_disclosures")
        run.input(run.data / "design.md")
        papers = read_csv(run.data / "citation_targets.csv")
        edges, decisions, coverage = [], [], []
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(acquire, run, p): p for p in papers}
            for future in concurrent.futures.as_completed(futures):
                paper = futures[future]
                try:
                    found, resolved, status = future.result()
                    edges.extend(found)
                    decisions.extend(resolved)
                except (OSError, ValueError, KeyError, RuntimeError) as error:
                    status = dict(
                        paper_id=paper["paper_id"],
                        doi=paper["doi"],
                        target_work_id="",
                        complete=False,
                        reported_records="",
                        pages="",
                        detail=str(error)[:180],
                        is_retracted="",
                        target_type="",
                    )
                    run.record["unresolved"].append(status)
                coverage.append(status)
                print(
                    len(coverage),
                    "/",
                    len(papers),
                    paper["paper_id"],
                    status["complete"],
                    status["reported_records"],
                    status["detail"],
                    flush=True,
                )
        edges.sort(key=lambda x: (x["paper_id"], x["citing_work_id"]))
        coverage.sort(key=lambda x: x["paper_id"])
        panel = make_panel(papers, coverage, edges)
        unique(edges, ["paper_id", "citing_work_id"])
        unique(panel, ["paper_id", "year"])
        run.check("panel_row_conservation", len(panel) == len(papers) * 18, len(panel))
        path = run.data / "citation_identity_decisions.csv"
        write_csv(
            path,
            sorted(decisions, key=lambda x: (x["paper_id"], x["doi"])),
            [
                "paper_id",
                "doi",
                "canonical_id",
                "candidate_ids",
                "candidate_years",
                "basis",
            ],
        )
        run.output(path)
        for name, rows in [
            ("citation_edges.csv", edges),
            ("citation_coverage.csv", coverage),
            ("panel.csv", panel),
        ]:
            path = run.data / name
            write_csv(path, rows, list(rows[0]))
            run.output(path)
        run.record["metrics"] = dict(
            targets=len(papers),
            completed=sum(x["complete"] for x in coverage),
            edges=len(edges),
            panel_rows=len(panel),
        )
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
