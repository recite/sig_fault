"""Connect adjudicated external disclosures to the shared citation workflow."""

import argparse
import collections
import csv
import datetime as dt
import hashlib
import io
import json
import time
from pathlib import Path

import audit_inventories as inventory
import i4r_citations as citations
import i4r_match as matching
import i4r_registry as registry
import i4r_sources as sources
import inventory_events
import nieuwenhuis_opencitations as oc
import nieuwenhuis_validation as oc_validation
import pilot

DATA = inventory.ROOT / "data/external"


def identifier(doi, record_id):
    return "external_" + hashlib.sha256((doi or record_id).encode()).hexdigest()[:14]


def original_dois(review):
    journal = review.get("original_journal_doi") or review["original_doi"]
    if review.get("identity_relationship") == "mislinked_original":
        if not review.get("identity_decision_evidence"):
            raise ValueError("Corrected original lacks identity evidence")
        return {journal} - {""}
    return {journal, review["original_doi"]} - {""}


def merge_article(old, new):
    if not old:
        return new
    for key in registry.ARTICLE_FIELDS:
        if key in {"identity_verified", "retracted"}:
            continue
        if old[key] and new[key] and old[key] != new[key]:
            if key == "title" and registry.identity_title_key(
                old[key]
            ) == registry.identity_title_key(new[key]):
                continue
            raise ValueError("Conflicting metadata for repeated original: " + key)
    result = {k: old[k] or new[k] for k in registry.ARTICLE_FIELDS}
    result["identity_verified"] = (
        "yes"
        if "yes" in {old["identity_verified"], new["identity_verified"]}
        else "pending"
    )
    result["retracted"] = next(
        v for v in ["yes", "no", "unknown"] if v in {old["retracted"], new["retracted"]}
    )
    return result


def build():
    reviews = json.loads((inventory.DATA / "primary_reviews.json").read_text())["cases"]
    metadata = {
        r["record_id"]: r
        for r in json.loads((inventory.DATA / "original_metadata.json").read_text())
    }
    decisions = {
        r["record_id"]: r
        for r in json.loads(
            (inventory.DATA / "disclosure_adjudications.json").read_text()
        )["cases"]
    }
    inventory_events.make_rows(
        reviews, list(metadata.values()), list(decisions.values())
    )
    previous = {r["article_id"]: r for r in sources.read("verified_metadata.csv")}
    screen_path = DATA / "retraction_screen.json"
    screen = json.loads(screen_path.read_text()) if screen_path.exists() else {}
    notices = sources.read("retractions.csv")
    i4r_dois = {
        r["doi"]
        for r in pilot.read_csv(inventory.ROOT / "data/i4r/articles.csv")
        if r["doi"]
    }
    articles, assessments, events, links = {}, [], [], []
    for review in reviews:
        rid = review["record_id"]
        m = metadata.get(rid, {})
        doi = review.get("original_journal_doi") or review["original_doi"]
        aid = identifier(doi, rid)
        title = review.get("verified_original_title") or review["original_title"]
        article = dict.fromkeys(registry.ARTICLE_FIELDS, "") | dict(
            article_id=aid,
            doi=doi,
            title=title,
            identity_verified="yes" if m else "pending",
            retracted="unknown",
        )
        if m:
            if m["journal_doi"] != doi:
                raise ValueError("Original metadata identity mismatch")
            article.update(
                title=m["title"],
                journal=m["journal"],
                publication_date=m["publication_date"],
                publication_year=m["publication_date"][:4],
                publication_date_source=m["source_url"],
            )
        if aid in previous:
            frozen = previous[aid]
            if frozen["doi"] != doi or registry.identity_title_key(
                frozen["title"]
            ) != registry.identity_title_key(title):
                raise ValueError("Frozen OpenAlex identity changed")
            article.update(
                {
                    k: frozen[k]
                    for k in [
                        "openalex_id",
                        "journal_id",
                        "indexed_publication_date",
                        "indexed_publication_year",
                        "type",
                        "abstract",
                    ]
                }
            )
        aliases = original_dois(review)
        relevant = [n for n in notices if n["doi"] in aliases]
        screened = aliases <= set(screen.get("screened_dois", []))
        if screened:
            article["retracted"] = "yes" if relevant else "no"
        if relevant:
            first = min(relevant, key=lambda n: n["date"])
            article.update(
                retraction_date=first["date"], retraction_source=first["source_url"]
            )
        articles[aid] = merge_article(articles.get(aid, {}), article)
        links.append(
            dict(
                record_id=rid,
                article_id=aid,
                inventory_doi=review["original_doi"],
                journal_doi=doi,
                already_in_i4r="yes" if aliases & i4r_dois else "no",
            )
        )
        d = decisions.get(rid)
        if not d:
            continue
        assessment_id = rid + "_error"
        material = d["material_error_verified"]
        assessments.append(
            dict.fromkeys(registry.ASSESSMENT_FIELDS, "")
            | dict(
                assessment_id=assessment_id,
                article_id=aid,
                source_id=rid,
                category=(
                    "demonstrated_material_error" if material == "yes" else "unresolved"
                ),
                material=material,
                error_verified="yes" if material == "yes" else "pending",
                affected_claim=d.get("affected_claim", ""),
                evidence_summary=d["decision_evidence"],
                evidence_locator="data/inventories/disclosure_adjudications.json: "
                + rid,
                dispute_status=review["response_status"],
                verification_scope=d["limitations"],
                public_year=d.get("date", "")[:4],
            )
        )
        year = d.get("date", "")[:4]
        already = "unknown"
        if screened and year:
            already = (
                "yes"
                if any(int(n["date"][:4]) <= int(year) for n in relevant)
                else "no"
            )
        # An existing I4R original must not contribute twice to the synthesis.
        if aliases & i4r_dois:
            continue
        events.append(
            dict.fromkeys(registry.EVENT_FIELDS, "")
            | dict(
                event_id=rid + "_disclosure",
                warning_id="external_warning_"
                + hashlib.sha256((review["report_doi"] or rid).encode()).hexdigest()[
                    :14
                ],
                article_id=aid,
                assessment_id=assessment_id,
                source_id=rid,
                date=d.get("date", ""),
                year=year,
                date_precision=d.get("date_precision", ""),
                publicity_verified=d["publicity_verified"],
                date_evidence_url=";".join(s["url"] for s in d["date_sources"]),
                date_evidence=d["date_evidence"],
                error_verified="yes" if material == "yes" else "pending",
                material=material,
                already_retracted=already,
            )
        )
    sources.write("articles.csv", list(articles.values()), registry.ARTICLE_FIELDS)
    sources.write("assessments.csv", assessments, registry.ASSESSMENT_FIELDS)
    sources.write("events.csv", events, registry.EVENT_FIELDS)
    sources.write(
        "inventory_links.csv",
        links,
        ["record_id", "article_id", "inventory_doi", "journal_doi", "already_in_i4r"],
    )
    if not (DATA / "citations.csv").exists():
        sources.write(
            "citations.csv", [], ["article_id", "year", "citations", "status"]
        )
    print(
        "External originals:",
        len(articles),
        "; adjudicated disclosure records:",
        len(events),
    )


def resolve():
    frozen = {r["article_id"]: r for r in sources.read("verified_metadata.csv")}
    log = {r["article_id"]: r for r in sources.read("identity_resolution.csv")}
    candidates = pilot.read_csv(inventory.DATA / "disclosure_candidates.csv")
    wanted = {
        identifier(r["journal_doi"], r["record_id"])
        for r in candidates
        if r["ready_for_citation_collection"] == "yes"
    }
    for article in sources.read("articles.csv"):
        aid = article["article_id"]
        if aid not in wanted:
            continue
        path = sources.CACHE / "identities" / (aid + ".json")
        try:
            w = sources.fetch(
                "https://api.openalex.org/works/https://doi.org/" + article["doi"], path
            )
            if inventory.doi(w.get("doi")) != article[
                "doi"
            ] or registry.identity_title_key(w["title"]) != registry.identity_title_key(
                article["title"]
            ):
                raise ValueError("OpenAlex DOI/title mismatch")
            frozen[aid] = registry.article_from_work(w, aid)
            log[aid] = dict(article_id=aid, status="complete", detail="")
        except Exception as e:
            log[aid] = dict(article_id=aid, status="incomplete", detail=str(e)[:200])
            if "429" in str(e) or "rate limit" in str(e):
                break
    sources.write(
        "verified_metadata.csv", list(frozen.values()), registry.ARTICLE_FIELDS
    )
    sources.write(
        "identity_resolution.csv",
        list(log.values()),
        ["article_id", "status", "detail"],
    )
    build()


def screen_retractions():
    reviews = json.loads((inventory.DATA / "primary_reviews.json").read_text())["cases"]
    dois = set().union(*(original_dois(r) for r in reviews))
    path = sources.CACHE / "retraction_watch.csv"
    payload = sources.fetch(citations.RETRACTIONS_URL, path, False)
    rows = []
    for r in csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))):
        doi = inventory.doi(r["OriginalPaperDOI"])
        if doi not in dois or r["RetractionNature"] != "Retraction":
            continue
        date = (
            dt.datetime.strptime(r["RetractionDate"].split()[0], "%m/%d/%Y")
            .date()
            .isoformat()
        )
        if date > sources.CUTOFF:
            continue
        notice = inventory.doi(r["RetractionDOI"])
        rows.append(
            dict(
                doi=doi,
                date=date,
                source_url="https://doi.org/" + notice if notice else r["URLS"],
                notice_doi=notice,
                record_id=r["Record ID"],
                dataset_url=citations.RETRACTIONS_URL,
            )
        )
    sources.write(
        "retractions.csv",
        rows,
        ["doi", "date", "source_url", "notice_doi", "record_id", "dataset_url"],
    )
    provenance = json.loads(path.with_suffix(".csv.source.json").read_text())
    if provenance["sha256"] != hashlib.sha256(payload).hexdigest():
        raise ValueError("Retraction source hash mismatch")
    (DATA / "retraction_screen.json").write_text(
        json.dumps(
            dict(
                source=provenance,
                cutoff=sources.CUTOFF,
                screened_dois=sorted(dois),
                matched_retractions=len(rows),
                limitation=(
                    "Exact DOI screen of the frozen Retraction Watch release; "
                    "no match is not proof of exhaustive notice coverage."
                ),
            ),
            indent=2,
        )
        + "\n"
    )
    build()


def opencitations_targets():
    articles = sources.read("articles.csv")
    events, _ = matching.eligible_events(sources.read("events.csv"), articles, 2025, 1)
    selected = {r["article_id"] for r in events}
    return [r for r in articles if r["article_id"] in selected]


def opencitations_fetch():
    folder = DATA / "opencitations"
    cache = sources.CACHE / "external_opencitations"
    coverage = {r["paper_id"]: r for r in sources.read("opencitations/coverage.csv")}
    edges = sources.read("opencitations/edges.csv")
    for article in opencitations_targets():
        aid, doi = article["article_id"], article["doi"]
        prior = coverage.get(aid, {})
        if prior.get("complete") == "yes" and prior.get("doi") == doi:
            continue
        row = dict.fromkeys(oc_validation.COVERAGE_FIELDS, "") | dict(
            paper_id=aid, doi=doi, complete="no"
        )
        try:
            records = oc_validation.fetch_links(aid, doi, cache=cache)
            time.sleep(0.4)
            count = int(
                sources.fetch(
                    oc_validation.BASE + "citation-count/doi:" + doi,
                    cache / (aid + "_opencitations_count.json"),
                )[0]["count"]
            )
            oc_validation.validate_response(records, count, doi)
            if count == 0:
                raise ValueError("zero_records_require_index_coverage_verification")
            edges = [r for r in edges if r["paper_id"] != aid] + [
                {k: r[k] for k in oc_validation.EDGE_FIELDS if k != "paper_id"}
                | dict(paper_id=aid)
                for r in records
            ]
            row.update(
                records=len(records),
                reported_count=count,
                undated_records=sum(not r["creation"] for r in records),
                complete="yes",
            )
        except Exception as exc:
            row["detail"] = str(exc)[:200]
        coverage[aid] = row
        pilot.write_csv(folder / "edges.csv", edges, oc_validation.EDGE_FIELDS)
        pilot.write_csv(
            folder / "coverage.csv",
            list(coverage.values()),
            oc_validation.COVERAGE_FIELDS,
        )
        manifest = []
        for path in sorted(cache.glob("*.source.json")):
            raw = path.with_name(path.name.removesuffix(".source.json"))
            record = json.loads(path.read_text())
            if hashlib.sha256(raw.read_bytes()).hexdigest() != record["sha256"]:
                raise ValueError("OpenCitations source hash mismatch")
            manifest.append(
                dict(
                    path="private-data/i4r/" + str(raw.relative_to(sources.CACHE)),
                    **record
                )
            )
        pilot.write_csv(
            folder / "sources.csv",
            manifest,
            ["path", "url", "retrieved_at", "sha256", "bytes"],
        )
        print(aid, row["complete"], row["records"], row["detail"], flush=True)
        if "429" in row["detail"] or "rate limit" in row["detail"]:
            break
        time.sleep(0.4)
    opencitations_build()


def opencitations_panel(articles, edges, coverage, last_year=2025):
    """Keep missing acquisitions out of annual counts and unresolved dates visible."""
    targets = {r["article_id"]: r for r in articles}
    pilot.unique(coverage, ["paper_id"])
    pilot.unique(edges, ["paper_id", "oci"])
    if any(r["paper_id"] not in targets for r in coverage + edges):
        raise ValueError("Citation history belongs to an unknown target")
    complete = set()
    selected_edges = []
    for row in coverage:
        aid = row["paper_id"]
        if row["doi"] != targets[aid]["doi"]:
            raise ValueError("Citation history target DOI changed")
        if row["complete"] != "yes":
            continue
        records = [r for r in edges if r["paper_id"] == aid]
        oc_validation.validate_response(records, int(row["reported_count"]), row["doi"])
        if len(records) != int(row["records"]) or not records:
            raise ValueError("Completed history has inconsistent or empty records")
        complete.add(aid)
        selected_edges.extend(records)
    works = oc.merge_works(selected_edges)
    counts = collections.Counter(
        (r["paper_id"], r["year"]) for r in works if r["date_status"] == "dated"
    )
    annual = [
        dict(article_id=aid, year=year, citations=counts[aid, year], status="complete")
        for aid in sorted(complete)
        for year in range(int(targets[aid]["publication_year"]), last_year + 1)
    ]
    return works, annual, complete


def opencitations_build():
    folder = DATA / "opencitations"
    coverage = sources.read("opencitations/coverage.csv")
    edges = sources.read("opencitations/edges.csv")
    articles = sources.read("articles.csv")
    works, annual, complete = opencitations_panel(articles, edges, coverage)
    pilot.write_csv(folder / "works.csv", works, oc.WORK_FIELDS)
    pilot.write_csv(
        folder / "citations.csv", annual, ["article_id", "year", "citations", "status"]
    )
    selected = {r["article_id"] for r in opencitations_targets()}
    status = dict(
        eligible_targets=len(selected),
        complete_eligible_targets=len(selected & complete),
        raw_relationships=sum(int(r["raw_relationships"]) for r in works),
        distinct_citing_works=len(works),
        undated_works=sum(r["date_status"] == "undated" for r in works),
        conflicting_year_works=sum(
            r["date_status"] == "conflicting_years" for r in works
        ),
        control_histories=0,
        matched_effect_estimates=0,
        outcome="Distinct dated citing works in OpenCitations, all document types",
        limitation=(
            "Unresolved years remain unassigned. Complete API acquisition does not "
            "establish complete real-world citation coverage. No effect estimate "
            "without controls."
        ),
    )
    (folder / "status.json").write_text(json.dumps(status, indent=2) + "\n")
    print(json.dumps(status))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "build",
            "resolve",
            "screen-retractions",
            "candidates",
            "control-metadata",
            "fetch",
            "opencitations-fetch",
            "opencitations-build",
        ],
    )
    parser.add_argument("--cache-dir", type=Path, default=sources.CACHE)
    args = parser.parse_args()
    sources.DATA = DATA
    sources.CACHE = args.cache_dir
    DATA.mkdir(parents=True, exist_ok=True)
    {
        "build": build,
        "resolve": resolve,
        "screen-retractions": screen_retractions,
        "candidates": citations.candidates,
        "control-metadata": citations.control_metadata,
        "fetch": citations.collect,
        "opencitations-fetch": opencitations_fetch,
        "opencitations-build": opencitations_build,
    }[args.command]()
