"""Extract auditable all-type annual totals from cached OpenAlex work metadata."""

from __future__ import annotations

import argparse
import datetime as dt
import json

import i4r_citations
import i4r_sources as sources
import pilot

OUTPUT = sources.DATA / "aggregate"
FIELDS = ["article_id", "year", "citations", "status"]
PROVENANCE = [
    "article_id",
    "openalex_id",
    "doi",
    "status",
    "first_year",
    "last_year",
    "source_path",
    "source_url",
    "source_sha256",
    "retrieved_at",
    "work_updated_at",
]


def annual_counts(work, retrieved_at):
    """Return supported bins; missing fields and stale vintages are not zeros."""
    vintage = dt.datetime.fromisoformat(retrieved_at.replace("Z", "+00:00"))
    updated = dt.datetime.fromisoformat(work["updated_date"].replace("Z", "+00:00"))
    if updated.year != vintage.year or updated.date() > vintage.date():
        raise ValueError("stale_or_inconsistent_work_vintage")
    bins = work.get("counts_by_year")
    if not isinstance(bins, list):
        raise ValueError("annual_counts_unavailable")
    counts = {}
    for row in bins:
        year, value = row.get("year"), row.get("cited_by_count")
        if (
            type(year) is not int
            or type(value) is not int
            or value < 0
            or year > vintage.year
            or year in counts
        ):
            raise ValueError("invalid_annual_count_bin")
        counts[year] = value
    first, last = vintage.year - 9, vintage.year - 1
    return {year: counts.get(year, 0) for year in range(first, last + 1)}


def cached_works():
    found = {}
    for folder in ["identities", "identity_search", "risk_sets"]:
        for path in sorted((sources.CACHE / folder).rglob("*.json")):
            if path.name.endswith(".source.json"):
                continue
            sidecar = path.with_suffix(path.suffix + ".source.json")
            if not sidecar.exists():
                # Extracted work objects inherit provenance from the search response.
                continue
            origin = json.loads(sidecar.read_text())
            payload = path.read_bytes()
            if pilot.sha256(payload) != origin["sha256"]:
                raise ValueError("Source checksum mismatch: " + str(path))
            data = json.loads(payload)
            for work in data.get("results", [data]):
                if work.get("id"):
                    found.setdefault(work["id"], []).append((work, origin, path))
    return found


def extract():
    snapshots = cached_works()
    articles = sources.read("articles.csv") + sources.read("control_articles.csv")
    annual, provenance = [], []
    for article in articles:
        aid, wid = article["article_id"], article["openalex_id"]
        record = dict.fromkeys(PROVENANCE, "") | {
            "article_id": aid,
            "openalex_id": wid,
            "doi": article["doi"],
        }
        try:
            if article["identity_verified"] != "yes":
                raise ValueError("identity_unverified")
            if len(i4r_citations.cited_ids(article)) != 1:
                raise ValueError("multiple_work_identities_require_edge_deduplication")
            candidates = snapshots.get(wid, [])
            if not candidates:
                raise ValueError("metadata_unavailable")
            histories = []
            for work, origin, path in candidates:
                if article["doi"] and (
                    pilot.normalize_doi(work.get("doi") or "") != article["doi"]
                ):
                    raise ValueError("metadata_doi_mismatch")
                histories.append(annual_counts(work, origin["retrieved_at"]))
            if any(history != histories[0] for history in histories):
                raise ValueError("conflicting_annual_count_snapshots")
            values = histories[0]
            work, origin, path = candidates[0]
            record.update(
                status="complete",
                first_year=min(values),
                last_year=max(values),
                source_path=str(path.relative_to(sources.ROOT)),
                source_url=origin["url"],
                source_sha256=origin["sha256"],
                retrieved_at=origin["retrieved_at"],
                work_updated_at=work["updated_date"],
            )
            for year, count in values.items():
                annual.append(
                    dict(article_id=aid, year=year, citations=count, status="complete")
                )
        except (ValueError, KeyError) as exc:
            record["status"] = str(exc)
        provenance.append(record)
    pilot.write_csv(OUTPUT / "citations.csv", annual, FIELDS)
    pilot.write_csv(OUTPUT / "provenance.csv", provenance, PROVENANCE)
    validate()


def validate():
    rows = pilot.read_csv(OUTPUT / "citations.csv")
    provenance = pilot.read_csv(OUTPUT / "provenance.csv")
    pilot.unique(rows, ["article_id", "year"])
    pilot.unique(provenance, ["article_id"])
    articles = {
        r["article_id"]: r
        for r in sources.read("articles.csv") + sources.read("control_articles.csv")
    }
    if {r["article_id"] for r in provenance} != set(articles):
        raise ValueError("Aggregate provenance must account for the article inventory")
    for row in provenance:
        article = articles[row["article_id"]]
        if any(row[k] != article[k] for k in ["doi", "openalex_id"]):
            raise ValueError("Aggregate provenance identity mismatch")
    groups = {}
    for row in rows:
        if row["status"] != "complete" or int(row["citations"]) < 0:
            raise ValueError("Invalid public annual count")
        groups.setdefault(row["article_id"], set()).add(int(row["year"]))
    complete = {r["article_id"]: r for r in provenance if r["status"] == "complete"}
    if set(groups) != set(complete):
        raise ValueError("Annual history/provenance mismatch")
    for aid, record in complete.items():
        if not all(record[k] for k in PROVENANCE if k != "doi"):
            raise ValueError("Incomplete source provenance")
        expected = set(range(int(record["first_year"]), int(record["last_year"]) + 1))
        vintage = dt.datetime.fromisoformat(record["retrieved_at"]).year
        if expected != set(range(vintage - 9, vintage)):
            raise ValueError("Annual window does not match retrieval vintage")
        if groups[aid] != expected:
            raise ValueError("Incomplete supported annual window")
    index = {(r["article_id"], r["year"]): int(r["citations"]) for r in rows}
    comparisons = []
    for row in sources.read("citations.csv"):
        key = (row["article_id"], row["year"])
        if row["status"] == "complete" and key in index:
            value = int(row["citations"])
            comparisons.append(
                dict(
                    article_id=key[0],
                    year=key[1],
                    aggregate_all_types=index[key],
                    edges_articles_reviews=value,
                    difference=index[key] - value,
                )
            )
    pilot.write_csv(
        OUTPUT / "measurement_comparison.csv",
        comparisons,
        [
            "article_id",
            "year",
            "aggregate_all_types",
            "edges_articles_reviews",
            "difference",
        ],
    )
    print("Validated aggregate histories:", len(complete))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["extract", "validate"])
    args = parser.parse_args()
    {"extract": extract, "validate": validate}[args.command]()
