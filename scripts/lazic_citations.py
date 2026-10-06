"""Collect and validate citation histories for every identified Lazic audit paper."""

import argparse
import collections
import hashlib
import json
import re
import time

import i4r_sources as acquisition
import lazic
import nieuwenhuis_opencitations as oc
import nieuwenhuis_validation as validation
import pilot

DATA = lazic.DATA / "opencitations"
CACHE = pilot.ROOT / "private-data/lazic/opencitations"
COVERAGE_FIELDS = validation.COVERAGE_FIELDS + ["scheme", "identifier"]


def read(name):
    path = DATA / name
    return pilot.read_csv(path) if path.exists() else []


def target(article):
    return ("doi", article["doi"]) if article["doi"] else ("pmid", article["pmid"])


def book_family(identifiers):
    families = set()
    for doi in validation.identifiers(identifiers, "doi:"):
        match = re.match(
            r"(10\.1007/978[-\d]+|10\.1016/b978[-\d]+|10\.1093/oxfordhb/978\d+)",
            doi.lower(),
        )
        if match:
            families.add(match.group(1))
    if len(families) > 1:
        raise ValueError("A citing work maps to conflicting book families")
    return next(iter(families), "")


def manifest():
    rows = []
    for path in sorted(CACHE.glob("*.source.json")):
        raw = path.with_name(path.name.removesuffix(".source.json"))
        record = json.loads(path.read_text())
        if hashlib.sha256(raw.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("OpenCitations source checksum mismatch")
        rows.append(dict(path=str(raw.relative_to(pilot.ROOT)), **record))
    pilot.write_csv(
        DATA / "sources.csv", rows, ["path", "url", "retrieved_at", "sha256", "bytes"]
    )


def fetch(limit=None):
    articles = pilot.read_csv(lazic.DATA / "articles.csv")
    coverage = {r["paper_id"]: r for r in read("coverage.csv")}
    edges = read("edges.csv")
    attempted = 0
    for article in articles:
        aid = article["article_id"]
        scheme, identifier = target(article)
        prior = coverage.get(aid, {})
        if prior.get("complete") == "yes":
            if (prior["scheme"], prior["identifier"]) != (scheme, identifier):
                raise ValueError("Completed history has a changed target identity")
            continue
        if limit is not None and attempted >= limit:
            break
        attempted += 1
        row = dict.fromkeys(COVERAGE_FIELDS, "") | dict(
            paper_id=aid,
            doi=article["doi"],
            scheme=scheme,
            identifier=identifier,
            complete="no",
        )
        try:
            records = validation.fetch_links(
                aid, identifier, cache=CACHE, scheme=scheme
            )
            time.sleep(0.4)
            total = acquisition.fetch(
                validation.BASE + "citation-count/" + scheme + ":" + identifier,
                CACHE / (aid + "_opencitations_count.json"),
            )
            count = int(total[0]["count"])
            validation.validate_response(records, count, identifier, scheme=scheme)
            if count == 0:
                raise ValueError("zero_records_require_index_coverage_verification")
            edges = [r for r in edges if r["paper_id"] != aid] + [
                {k: r[k] for k in validation.EDGE_FIELDS if k != "paper_id"}
                | dict(paper_id=aid)
                for r in records
            ]
            row.update(
                records=count,
                reported_count=count,
                undated_records=sum(not r["creation"] for r in records),
                complete="yes",
            )
        except Exception as exc:
            row["detail"] = str(exc)[:200]
        coverage[aid] = row
        pilot.write_csv(DATA / "edges.csv", edges, validation.EDGE_FIELDS)
        pilot.write_csv(DATA / "coverage.csv", list(coverage.values()), COVERAGE_FIELDS)
        manifest()
        print(aid, row["complete"], row["records"], row["detail"], flush=True)
        if "429" in row["detail"] or "rate limit" in row["detail"]:
            break
        time.sleep(0.4)
    build()


def panel(articles, coverage, edges):
    pilot.unique(articles, ["article_id"])
    pilot.unique(coverage, ["paper_id"])
    pilot.unique(edges, ["paper_id", "oci"])
    targets = {r["article_id"]: r for r in articles}
    if any(r["paper_id"] not in targets for r in coverage + edges):
        raise ValueError("Unknown citation target")
    complete, checked = set(), []
    for row in coverage:
        aid = row["paper_id"]
        scheme, identifier = target(targets[aid])
        if (row["scheme"], row["identifier"], row["doi"]) != (
            scheme,
            identifier,
            targets[aid]["doi"],
        ):
            raise ValueError("Changed citation target")
        if row["complete"] != "yes":
            continue
        records = [r for r in edges if r["paper_id"] == aid]
        validation.validate_response(
            records, int(row["reported_count"]), identifier, scheme=scheme
        )
        if not records or len(records) != int(row["records"]):
            raise ValueError("Empty or inconsistent completed citation history")
        if sum(not r["creation"] for r in records) != int(row["undated_records"]):
            raise ValueError("Undated citation count mismatch")
        complete.add(aid)
        checked.extend(records)
    works = oc.merge_works(checked)
    counts = collections.Counter(
        (r["paper_id"], r["year"]) for r in works if r["date_status"] == "dated"
    )
    rows = []
    for a in articles:
        aid = a["article_id"]
        for year in range(int(a["publication_year"]), 2026):
            rows.append(
                dict(
                    article_id=aid,
                    year=year,
                    classification=a["classification"],
                    flagged=a["flagged"],
                    citations=counts[aid, year] if aid in complete else "",
                    status="complete" if aid in complete else "missing_history",
                )
            )
    return rows, works


def build():
    articles = pilot.read_csv(lazic.DATA / "articles.csv")
    coverage, edges = read("coverage.csv"), read("edges.csv")
    rows, works = panel(articles, coverage, edges)
    pilot.write_csv(DATA / "panel.csv", rows, list(rows[0]))
    pilot.write_csv(DATA / "works.csv", works, oc.WORK_FIELDS)
    books = [
        dict(**r, book_family=book_family(r["identifiers"]))
        for r in works
        if book_family(r["identifiers"])
    ]
    pilot.write_csv(DATA / "book_records.csv", books, oc.WORK_FIELDS + ["book_family"])
    complete = {r["paper_id"] for r in coverage if r["complete"] == "yes"}
    status = dict(
        target_papers=len(articles),
        complete_histories=len(complete),
        complete_by_classification=dict(
            collections.Counter(
                a["classification"] for a in articles if a["article_id"] in complete
            )
        ),
        raw_edges=len(edges),
        distinct_citing_works=len(works),
        uncertain_date_works=sum(r["date_status"] != "dated" for r in works),
        measurement="All indexed document types; shared DOI/OMID records deduplicated",
        analysis_status_file="data/lazic/analysis_status.json",
    )
    (DATA / "status.json").write_text(json.dumps(status, indent=2) + "\n")
    print(json.dumps(status), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["fetch", "build"])
    p.add_argument("--limit", type=int)
    args = p.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    fetch(args.limit) if args.command == "fetch" else build()
