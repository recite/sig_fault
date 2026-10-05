"""Collect the full Lal et al. audit cohort and its annual citation histories."""

import argparse
import collections
import difflib
import json
import re
import unicodedata

import pilot

DATA = pilot.ROOT / "data/lal"
CACHE = pilot.ROOT / "private-data/lal"


def title_key(title):
    text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


def book_family(doi):
    match = re.match(r"^10\.1093/(?:oso/)?(97[89]\d{10})(?:[./]|$)", doi)
    return "10.1093/" + match.group(1) if match else ""


def adjudicate_duplicates(edges):
    path = DATA / "citation_identity_decisions.csv"
    decisions = pilot.read_csv(path) if path.exists() else []
    pilot.unique(decisions, ["paper_id", "doi"])
    selected = {(r["paper_id"], r["doi"]): r["canonical_work_id"] for r in decisions}
    available = {(r["paper_id"], r["doi"], r["citing_work_id"]) for r in edges}
    if any((pid, doi, work) not in available for (pid, doi), work in selected.items()):
        raise ValueError("Adjudicated citation identity is absent from frame")
    result = []
    for row in edges:
        canonical = selected.get((row["paper_id"], row["doi"]))
        result.append(
            row
            | {"duplicate_of": "" if canonical == row["citing_work_id"] else canonical}
            if canonical
            else row
        )
    return result


def registry():
    designs = pilot.read_csv(pilot.DATA / "iv_diagnostics.csv")
    groups = collections.defaultdict(list)
    checked = {
        r["paper_id"]: r for r in pilot.read_csv(pilot.DATA / "iv_verification.csv")
    }
    corrections = []
    for row in designs:
        item = row.copy()
        pid = "iv_" + row["name"]
        ar = float(row["AR_p"])
        if pid == "iv_Alt2015":
            ar = float(checked[pid]["ar_p"])
        dimensions = (
            int(checked[pid]["excluded_columns"])
            if pid in checked
            else int(row["p_iv"])
        )
        tf_eligible = dimensions == 1 and bool(row["tF_p"])
        positive = float(row["iv_analy_p"]) < 0.05
        item.update(
            weak=int(float(row["f_effective"]) < 10),
            ar_loss=int(positive and ar >= 0.05),
            tf_loss=int(positive and tf_eligible and float(row["tF_p"]) >= 0.05),
            analytic_positive=int(positive),
        )
        item["sensitive"] = int(item["ar_loss"] or item["tf_loss"])
        item["screen"] = int(item["weak"] or item["sensitive"])
        groups[row["title"]].append(item)
        corrections.append(
            dict(
                design_id=row["name"],
                source_ar_p=row["AR_p"],
                used_ar_p=ar,
                excluded_columns=dimensions,
                dimension_source="replicated"
                if pid in checked
                else "audit_metadata_unverified",
                tf_eligible=int(tf_eligible),
            )
        )
    papers = []
    for title, rows in groups.items():
        first = rows[0]
        paper = dict(
            paper_id="iv_" + first["name"],
            title=title,
            authors=first["authors"],
            year=first["year"],
            journal=first["journal"],
            designs=";".join(r["name"] for r in rows),
        )
        paper.update(
            {
                field: int(any(r[field] for r in rows))
                for field in [
                    "weak",
                    "sensitive",
                    "screen",
                    "ar_loss",
                    "analytic_positive",
                ]
            }
        )
        papers.append(paper)
    if len(designs) != 70 or len(papers) != 67:
        raise ValueError("Audit frame changed")
    pilot.write_csv(DATA / "papers.csv", papers, list(papers[0]))
    pilot.write_csv(DATA / "diagnostic_checks.csv", corrections, list(corrections[0]))


def resolve():
    papers = pilot.read_csv(DATA / "papers.csv")
    known = {r["paper_id"]: r for r in pilot.read_csv(pilot.DATA / "identities.csv")}
    rows = []
    for paper in papers:
        pid = paper["paper_id"]
        if pid in known:
            work = pilot.request(
                "https://api.openalex.org/works/https://doi.org/" + known[pid]["doi"],
                CACHE / "identities" / f"{pid}.json",
            )
            candidates = [work]
        else:
            result = pilot.request(
                pilot.api_url(
                    "works", search=re.sub(r"[?*]", "", paper["title"]), per_page=5
                ),
                CACHE / "search" / f"{pid}.json",
            )
            candidates = result["results"]
        for work in candidates:
            rows.append(
                {
                    "paper_id": pid,
                    "source_title": paper["title"],
                    "work_id": work["id"],
                    "doi": pilot.normalize_doi(work.get("doi") or ""),
                    "title": work["title"],
                    "publication_date": work["publication_date"],
                    "source_year": paper["year"],
                    "journal": (
                        (work.get("primary_location") or {}).get("source") or {}
                    ).get("display_name", ""),
                    "authors": ";".join(
                        x["author"]["display_name"] for x in work.get("authorships", [])
                    ),
                    "title_score": difflib.SequenceMatcher(
                        None, title_key(paper["title"]), title_key(work["title"])
                    ).ratio(),
                    "previously_checked": "yes" if pid in known else "no",
                }
            )
        print(pid, "identity candidates cached", flush=True)
    pilot.write_csv(CACHE / "identity_candidates.csv", rows, list(rows[0]))


FIELDS = [
    "paper_id",
    "target_work_id",
    "citing_work_id",
    "doi",
    "title",
    "publication_date",
    "publication_year",
    "type",
    "reference_verified",
    "duplicate_of",
]


def manifests():
    rows = []
    for path in sorted(CACHE.rglob("*.source.json")):
        item = json.loads(path.read_text())
        rows.append(
            {
                "cache_path": str(path.relative_to(pilot.ROOT)).removesuffix(
                    ".source.json"
                ),
                **item,
            }
        )
    if rows:
        pilot.write_csv(DATA / "source_manifest.csv", rows, list(rows[0]))


def fetch():
    papers = pilot.read_csv(DATA / "identities.csv")
    pilot.unique(papers, ["paper_id"])
    edges, coverage = [], []
    for paper in papers:
        pid, target = paper["paper_id"], paper["work_id"]
        cursor, seen, works, totals, page = "*", set(), [], [], 0
        while cursor:
            if cursor in seen:
                raise ValueError("Repeated cursor")
            seen.add(cursor)
            page += 1
            response = pilot.request(
                pilot.api_url(
                    "works",
                    filter=f"cites:{target.rsplit('/', 1)[-1]},to_publication_date:{pilot.CUTOFF}",
                    per_page=100,
                    cursor=cursor,
                    select="id,doi,title,publication_date,publication_year,type,referenced_works",
                    sort="publication_date",
                ),
                CACHE / "citations" / pid / f"{page:04d}.json",
            )
            works.extend(response["results"])
            totals.append(response["meta"]["count"])
            cursor = response["meta"].get("next_cursor")
            if not response["results"]:
                break
        if len(set(totals)) != 1 or len(works) != totals[0]:
            raise ValueError(f"Incomplete citation frame for {pid}")
        pilot.unique(works, ["id"])
        dois = {}
        for work in sorted(works, key=lambda w: (w["publication_date"], w["id"])):
            if target not in work["referenced_works"]:
                raise ValueError("Returned work does not reference target")
            date = work["publication_date"]
            if date > pilot.CUTOFF or int(date[:4]) != work["publication_year"]:
                raise ValueError("Citation date inconsistency")
            doi = pilot.normalize_doi(work.get("doi") or "")
            duplicate = dois.get(doi, "") if doi else ""
            if doi and not duplicate:
                dois[doi] = work["id"]
            edges.append(
                dict(
                    paper_id=pid,
                    target_work_id=target,
                    citing_work_id=work["id"],
                    doi=doi,
                    title=work["title"] or "",
                    publication_date=date,
                    publication_year=work["publication_year"],
                    type=work["type"],
                    reference_verified="yes",
                    duplicate_of=duplicate,
                )
            )
        coverage.append(
            dict(paper_id=pid, api_count=totals[0], pages=page, complete="yes")
        )
        print(pid, len(works), "links", flush=True)
    pilot.unique(edges, ["paper_id", "citing_work_id"])
    pilot.write_frozen_csv(DATA / "citation_edges.csv", edges, FIELDS)
    pilot.write_frozen_csv(DATA / "coverage.csv", coverage, list(coverage[0]))
    manifests()


def panel():
    papers = pilot.read_csv(DATA / "papers.csv")
    identities = {r["paper_id"]: r for r in pilot.read_csv(DATA / "identities.csv")}
    coverage = pilot.read_csv(DATA / "coverage.csv")
    wanted = {r["paper_id"] for r in papers}
    if wanted != set(identities) or wanted != {
        r["paper_id"] for r in coverage if r["complete"] == "yes"
    }:
        raise ValueError(
            "All 67 paper identities and complete citation frames are required"
        )
    edges = pilot.read_csv(DATA / "citation_edges.csv")
    pilot.unique(edges, ["paper_id", "citing_work_id"])
    totals = collections.Counter(r["paper_id"] for r in edges)
    if set(totals) - wanted or any(
        totals[r["paper_id"]] != int(r["api_count"]) for r in coverage
    ):
        raise ValueError("Frozen frame disagrees with completed coverage totals")
    edges = adjudicate_duplicates(edges)
    counts, all_types, journals, exclusions = (
        collections.Counter(),
        collections.Counter(),
        collections.Counter(),
        [],
    )
    collapsed, seen_books, book_rows = collections.Counter(), set(), []
    for row in sorted(
        edges, key=lambda r: (r["paper_id"], r["publication_date"], r["citing_work_id"])
    ):
        if row["reference_verified"] != "yes" or row["publication_date"] > pilot.CUTOFF:
            raise ValueError("Unverified reference or cutoff violation")
        reason = ""
        if row["duplicate_of"]:
            reason = "duplicate_doi"
        elif row["citing_work_id"] == row["target_work_id"]:
            reason = "target_itself"
        elif int(row["publication_year"]) < int(
            identities[row["paper_id"]]["publication_date"][:4]
        ):
            reason = "before_target_publication_year"
        if reason:
            exclusions.append(row | {"reason": reason})
            continue
        key = row["paper_id"], int(row["publication_year"])
        all_types[key] += 1
        if row["type"] in {"article", "review"}:
            journals[key] += 1
        if row["type"] in pilot.ALLOWED_TYPES:
            counts[key] += 1
            family = book_family(row["doi"])
            family_key = row["paper_id"], family
            if not family or family_key not in seen_books:
                collapsed[key] += 1
            if family:
                seen_books.add(family_key)
                book_rows.append(
                    {
                        "paper_id": row["paper_id"],
                        "book_family": family,
                        "citing_work_id": row["citing_work_id"],
                        "doi": row["doi"],
                        "publication_year": row["publication_year"],
                        "title": row["title"],
                    }
                )
        if row["type"] not in {"article", "review"}:
            exclusions.append(row | {"reason": "type_excluded_from_primary"})
    rows = []
    for paper in papers:
        first = int(identities[paper["paper_id"]]["publication_date"][:4])
        for year in range(first, int(pilot.CUTOFF[:4]) + 1):
            key = paper["paper_id"], year
            rows.append(
                paper
                | {
                    "publication_year": first,
                    "citation_year": year,
                    "citations": journals[key],
                    "citations_broad": counts[key],
                    "citations_broad_book_collapsed": collapsed[key],
                    "citations_all_types": all_types[key],
                }
            )
    pilot.write_csv(DATA / "panel.csv", rows, list(rows[0]))
    pilot.write_csv(DATA / "edge_exclusions.csv", exclusions, FIELDS + ["reason"])
    pilot.write_csv(
        DATA / "oxford_book_records.csv",
        book_rows,
        [
            "paper_id",
            "book_family",
            "citing_work_id",
            "doi",
            "publication_year",
            "title",
        ],
    )
    print(
        f"Built {len(rows)} paper-years for {len(papers)} papers from {len(edges)} links"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["registry", "resolve", "fetch", "panel"])
    globals()[parser.parse_args().command]()
