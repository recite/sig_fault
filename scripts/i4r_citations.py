"""Collect I4R risk sets and deduplicated citation edges with resumable caches."""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import io
import json

import i4r_match as matching
import i4r_registry as registry
import i4r_sources as sources
import pilot

EDGE_FIELDS = [
    "article_id",
    "citing_work_id",
    "citing_doi",
    "publication_year",
    "publication_date",
    "type",
]


def all_works(params, folder):
    cursor = "*"
    seen = set()
    works = []
    while cursor:
        if cursor in seen:
            raise ValueError("Repeated API cursor")
        seen.add(cursor)
        query_key = hashlib.sha256(
            json.dumps(params, sort_keys=True).encode()
        ).hexdigest()[:16]
        path = (
            folder
            / query_key
            / (hashlib.sha256(cursor.encode()).hexdigest()[:16] + ".json")
        )
        payload = sources.fetch(
            pilot.api_url("works", **params, cursor=cursor, **{"per-page": 100}), path
        )
        works.extend(payload["results"])
        cursor = payload["meta"].get("next_cursor")
        if not payload["results"]:
            break
    unique = {w["id"]: w for w in works}
    if len(unique) != len(works):
        raise ValueError(
            "Duplicate work across cursor pages; refresh this query snapshot"
        )
    if len(works) != payload["meta"]["count"]:
        raise ValueError("Incomplete or changing API result set")
    return works


def canonical_controls(records, targets, prior_aliases=()):
    original_dois = {r["doi"] for r in targets if r.get("doi")}
    original_titles = {registry.title_key(r["title"]) for r in targets}
    groups = collections.defaultdict(list)
    for r in records:
        if (
            r["doi"] in original_dois
            or registry.title_key(r["title"]) in original_titles
        ):
            continue
        key = r["doi"] or r["openalex_id"]
        aid = "control_" + hashlib.sha256(key.encode()).hexdigest()[:14]
        groups[aid].append(r)
    controls, aliases = [], {}
    for aid, group in sorted(groups.items()):
        chosen = min(
            group,
            key=lambda r: (
                r.get("indexed_publication_date") or r["publication_date"],
                r["openalex_id"],
            ),
        )
        chosen = chosen | {"article_id": aid}
        dated = [
            r
            for r in group
            if r.get("publication_date_source") and r.get("publication_date")
        ]
        if dated:
            publisher = min(dated, key=lambda r: r["publication_date"])
            for name in [
                "publication_date",
                "publication_year",
                "publication_date_source",
            ]:
                chosen[name] = publisher[name]
        controls.append(chosen)
        for r in group:
            aliases[r["openalex_id"]] = aid
            for old in prior_aliases:
                if old["article_id"] == r["article_id"]:
                    aliases[old["alias_openalex_id"]] = aid
    return controls, [
        dict(alias_openalex_id=k, article_id=v) for k, v in sorted(aliases.items())
    ]


def cited_ids(article):
    ids = {article["openalex_id"]}
    ids.update(
        r["alias_openalex_id"]
        for r in sources.read("control_aliases.csv")
        if r["article_id"] == article["article_id"]
    )
    if article.get("doi"):
        ids.update(
            r["openalex_id"]
            for r in sources.read("verified_metadata.csv")
            if r["doi"] == article["doi"] and r["openalex_id"]
        )
    if len(ids) > 100:
        raise ValueError(
            "More than 100 cited aliases; explicit query batching required"
        )
    return sorted(ids)


def candidates():
    targets = {r["article_id"]: r for r in sources.read("articles.csv")}
    controls = {r["article_id"]: r for r in sources.read("control_articles.csv")}
    queries = {r["event_id"]: r for r in sources.read("risk_set_retrieval.csv")}
    eligible, _ = matching.eligible_events(
        sources.read("events.csv"), list(targets.values()), 2025, 1
    )
    for event in eligible:
        r = targets[event["article_id"]]
        if (
            event["error_verified"] != "yes"
            or event["publicity_verified"] != "yes"
            or event["material"] != "yes"
        ):
            continue
        if not r["journal_id"] or not registry.matching_year(r):
            queries[event["event_id"]] = dict(
                event_id=event["event_id"],
                status="unresolved_target_metadata",
                candidates=0,
                query_filter="",
            )
            continue
        params = {"filter": registry.risk_filter(r)}
        key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[
            :16
        ]
        try:
            works = all_works(params, sources.CACHE / "risk_sets" / key)
            for w in works:
                record = registry.add_retraction(registry.article_from_work(w))
                # Exclude any resolved original study, even if its internal ID differs.
                if any(
                    (t.get("doi") and t["doi"] == record["doi"])
                    or registry.title_key(t["title"])
                    == registry.title_key(record["title"])
                    for t in targets.values()
                ):
                    continue
                controls[record["article_id"]] = record
            queries[event["event_id"]] = dict(
                event_id=event["event_id"],
                status="complete",
                candidates=len(works),
                query_filter=params["filter"],
            )
        except Exception as exc:
            queries[event["event_id"]] = dict(
                event_id=event["event_id"],
                status=str(exc)[:180],
                candidates=0,
                query_filter=params["filter"],
            )
            if "429" in str(exc) or "rate limit" in str(exc):
                break
    controls, aliases = canonical_controls(
        controls.values(), targets.values(), sources.read("control_aliases.csv")
    )
    sources.write("control_aliases.csv", aliases, ["alias_openalex_id", "article_id"])
    sources.write(
        "control_articles.csv",
        controls,
        registry.ARTICLE_FIELDS,
    )
    sources.write(
        "risk_set_retrieval.csv",
        list(queries.values()),
        ["event_id", "status", "candidates", "query_filter"],
    )


def control_metadata():
    rows = sources.read("control_articles.csv")
    log = {r["article_id"]: r for r in sources.read("control_metadata_retrieval.csv")}
    provenance = {
        r["article_id"]: r for r in sources.read("control_metadata_provenance.csv")
    }
    for record in rows:
        aid, status = registry.crossref_record(record)
        path = sources.CACHE / "crossref" / (aid + ".json")
        if status == "retrieved":
            work = json.loads(path.read_text())["message"]
            matched = registry.crossref_title_match(
                record["title"], [work], known_doi=True
            )
            if matched and pilot.normalize_doi(work["DOI"]) == record["doi"]:
                registry.publisher_date(record, work)
                provenance[aid] = registry.metadata_provenance(aid, path, "crossref")
            else:
                status = "publisher_identity_mismatch"
        log[aid] = dict(article_id=aid, status=status)
        if "429" in status or "rate limit" in status:
            break
    sources.write("control_articles.csv", rows, registry.ARTICLE_FIELDS)
    sources.write(
        "control_metadata_retrieval.csv", list(log.values()), ["article_id", "status"]
    )
    sources.write(
        "control_metadata_provenance.csv",
        list(provenance.values()),
        ["article_id", "provider", "path", "url", "sha256", "retrieved_at"],
    )


def normalize_edges(article_id, works):
    # DOI aliases count once, choosing the earliest indexed publication date.
    unique = {}
    for w in works:
        if w["type"] not in {"article", "review"}:
            continue
        doi = pilot.normalize_doi(w.get("doi") or "")
        row = dict(
            article_id=article_id,
            citing_work_id=w["id"],
            citing_doi=doi,
            publication_year=int(w["publication_year"]),
            publication_date=w["publication_date"],
            type=w["type"],
        )
        key = doi or w["id"]
        if key not in unique or (row["publication_date"], row["citing_work_id"]) < (
            unique[key]["publication_date"],
            unique[key]["citing_work_id"],
        ):
            unique[key] = row
    return list(unique.values())


def collect():
    rows = sources.read("citations.csv")
    logs = {r["article_id"]: r for r in sources.read("citation_retrieval.csv")}
    edges = sources.read("citation_edges.csv")
    events = [
        r
        for r in sources.read("events.csv")
        if r["year"]
        and r["error_verified"] == "yes"
        and r["publicity_verified"] == "yes"
    ]
    if not events:
        sources.write("citation_retrieval.csv", [], ["article_id", "status", "detail"])
        sources.write(
            "citations.csv", [], ["article_id", "year", "citations", "status"]
        )
        sources.write("citation_edges.csv", [], EDGE_FIELDS)
        return
    minimum = min(int(r["year"]) - 3 for r in events)
    target_ids = {r["article_id"] for r in events}
    articles = [
        r for r in sources.read("articles.csv") if r["article_id"] in target_ids
    ]
    for article in articles + sources.read("control_articles.csv"):
        aid = article["article_id"]
        if (
            not article["openalex_id"]
            or article["identity_verified"] != "yes"
            or not article["publication_year"]
        ):
            logs[aid] = dict(article_id=aid, status="unresolved_identity", detail="")
            continue
        try:
            target_ids = cited_ids(article)
            target_filter = "|".join(target_ids)
            params = {
                "filter": (
                    f"cites:{target_filter},type:article|review,"
                    f"from_publication_date:{minimum}-01-01,"
                    "to_publication_date:2025-12-31"
                ),
                "select": (
                    "id,doi,title,publication_year,publication_date,"
                    "type,referenced_works"
                ),
            }
            works = all_works(params, sources.CACHE / "citations" / aid)
            if any(
                not set(target_ids).intersection(w.get("referenced_works", []))
                for w in works
            ):
                raise ValueError("Unverified citation relationship in query response")
            normalized = normalize_edges(aid, works)
            rows = [r for r in rows if r["article_id"] != aid]
            edges = [r for r in edges if r["article_id"] != aid] + normalized
            counts = collections.Counter(r["publication_year"] for r in normalized)
            for year in range(max(minimum, int(article["publication_year"])), 2026):
                rows.append(
                    dict(
                        article_id=aid,
                        year=year,
                        citations=counts[year],
                        status="complete",
                    )
                )
            logs[aid] = dict(article_id=aid, status="complete", detail="")
        except Exception as exc:
            logs[aid] = dict(article_id=aid, status="incomplete", detail=str(exc)[:200])
            for row in rows:
                if row["article_id"] == aid:
                    row["status"] = "incomplete"
            if "429" in str(exc) or "rate limit" in str(exc):
                break
    sources.write("citations.csv", rows, ["article_id", "year", "citations", "status"])
    sources.write("citation_edges.csv", edges, EDGE_FIELDS)
    sources.write(
        "citation_retrieval.csv",
        list(logs.values()),
        ["article_id", "status", "detail"],
    )


RETRACTIONS_URL = (
    "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv"
)


def retractions():
    payload = sources.fetch(
        RETRACTIONS_URL, sources.CACHE / "retraction_watch.csv", False
    )
    targets = sources.read("articles.csv") + sources.read("control_articles.csv")
    dois = {r["doi"] for r in targets if r["doi"]}
    rows = []
    for r in csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))):
        doi = pilot.normalize_doi(r["OriginalPaperDOI"])
        if doi not in dois or r["RetractionNature"] != "Retraction":
            continue
        date = (
            dt.datetime.strptime(r["RetractionDate"].split()[0], "%m/%d/%Y")
            .date()
            .isoformat()
        )
        if date > sources.CUTOFF:
            continue
        notice = pilot.normalize_doi(r["RetractionDOI"])
        rows.append(
            dict(
                doi=doi,
                date=date,
                source_url="https://doi.org/" + notice if notice else r["URLS"],
                notice_doi=notice,
                record_id=r["Record ID"],
                dataset_url=RETRACTIONS_URL,
            )
        )
    sources.write(
        "retractions.csv",
        rows,
        ["doi", "date", "source_url", "notice_doi", "record_id", "dataset_url"],
    )
    controls = [
        registry.add_retraction(r) for r in sources.read("control_articles.csv")
    ]
    sources.write("control_articles.csv", controls, registry.ARTICLE_FIELDS)
    registry.build()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["candidates", "control-metadata", "fetch", "retractions"]
    )
    args = parser.parse_args()
    {
        "candidates": candidates,
        "control-metadata": control_metadata,
        "fetch": collect,
        "retractions": retractions,
    }[args.command]()
