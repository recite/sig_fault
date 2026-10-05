"""Build a registry separating source review from verified exposure."""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import hashlib
import json
import re
import unicodedata
import urllib.parse

import i4r_sources as s
import pilot

ARTICLE_FIELDS = [
    "article_id",
    "title",
    "doi",
    "openalex_id",
    "journal",
    "journal_id",
    "publication_date",
    "publication_year",
    "indexed_publication_date",
    "indexed_publication_year",
    "publication_date_source",
    "type",
    "abstract",
    "identity_verified",
    "retracted",
    "retraction_date",
    "retraction_source",
]
LINK_FIELDS = ["source_id", "article_id", "relation", "evidence"]
REVIEW_FIELDS = [
    "source_id",
    "review_status",
    "classification",
    "target_title",
    "target_doi",
    "evidence_summary",
    "evidence_pages",
    "review_scope",
    "related_sources",
    "assessment_eligibility",
    "assessment_resolved",
    "canonical_source_id",
    "adjudicated_disposition",
    "adjudication_evidence",
    "adjudication_locator",
    "adjudication_limitations",
]
ASSESSMENT_FIELDS = [
    "assessment_id",
    "article_id",
    "source_id",
    "category",
    "material",
    "error_verified",
    "affected_claim",
    "evidence_summary",
    "evidence_locator",
    "dispute_status",
    "verification_scope",
    "public_year",
]
EVENT_FIELDS = [
    "event_id",
    "warning_id",
    "article_id",
    "assessment_id",
    "source_id",
    "date",
    "year",
    "date_precision",
    "publicity_verified",
    "date_evidence_url",
    "date_evidence",
    "error_verified",
    "material",
    "already_retracted",
]


def title_key(text):
    text = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    )
    return re.sub(r"[^a-z0-9]", "", text)


def identity_title_key(text):
    text = re.sub(r"^RETRACTED(?: ARTICLE)?\s*:\s*", "", text, flags=re.I)
    text = re.sub(r"\s*\(Team \d+\)\s*$", "", text, flags=re.I)
    text = re.sub(r"</?(?:i|b|sup|sub|em|strong)[^>]*>", "", text)
    return title_key(text)


def article_id(title):
    return "i4r_" + hashlib.sha256(title_key(title).encode()).hexdigest()[:14]


def normalize_review(r):
    def first(*names, default=""):
        return next((r[n] for n in names if r.get(n) not in [None, "", []]), default)

    pages = first("evidence_pages", "source_pdf_pages_1_based", "evidence_pdf_pages")
    related = first("linked_source_ids", "related_source_ids")
    return dict(
        source_id=r["source_id"],
        review_status=r["review_status"],
        classification=r["classification"],
        assessment_eligibility=first("assessment_eligibility", default="unresolved"),
        assessment_resolved=first("assessment_resolved", default="no"),
        target_title=first("original_title", "target_title", "original_title_hint"),
        target_doi=first("original_doi", "target_doi"),
        evidence_summary=first("evidence_summary", "assessment"),
        evidence_pages=json.dumps(pages) if isinstance(pages, list) else pages,
        review_scope=first("verification_scope", "review_limitations", "notes"),
        related_sources=";".join(related) if isinstance(related, list) else related,
    )


def adjudicate_reviews(reviews, decisions):
    pilot.unique(decisions, ["source_id"])
    lookup = {r["source_id"]: dict(r) for r in reviews}
    for decision in decisions:
        sid = decision["source_id"]
        if sid not in lookup:
            raise ValueError("Adjudication outside frozen catalog: " + sid)
        eligibility = decision["assessment_eligibility"]
        resolved = decision["assessment_resolved"]
        if eligibility not in {"yes", "no", "unresolved"} or resolved not in {
            "yes",
            "no",
        }:
            raise ValueError("Invalid adjudication status")
        if resolved == "yes" and eligibility != "yes":
            raise ValueError("Resolved assessment must be eligible")
        if (eligibility != "unresolved" or resolved == "yes") and not decision.get(
            "evidence"
        ):
            raise ValueError("Adjudication lacks evidence")
        if decision.get("canonical_source_id", sid) != sid and not decision.get(
            "evidence"
        ):
            raise ValueError("Assessment equivalence lacks evidence")
        row = lookup[sid]
        row.update(
            assessment_eligibility=eligibility,
            assessment_resolved=resolved,
            canonical_source_id=decision.get("canonical_source_id") or sid,
            adjudicated_disposition=decision["disposition"],
            adjudication_evidence=decision.get("evidence", ""),
            adjudication_locator=decision.get("evidence_locator", ""),
            adjudication_limitations=decision.get("limitations", ""),
        )
    for sid, row in lookup.items():
        row.setdefault("canonical_source_id", sid)
        if not row["canonical_source_id"]:
            row["canonical_source_id"] = sid
    for sid, row in lookup.items():
        seen, current = set(), sid
        while lookup[current]["canonical_source_id"] != current:
            if current in seen:
                raise ValueError("Cyclic assessment equivalence")
            seen.add(current)
            current = lookup[current]["canonical_source_id"]
            if current not in lookup:
                raise ValueError("Canonical assessment outside frozen catalog")
        row["canonical_source_id"] = current
    grouped = collections.defaultdict(list)
    for row in lookup.values():
        grouped[row["canonical_source_id"]].append(row)
    units = []
    for sid, members in sorted(grouped.items()):
        statuses = {r.get("assessment_eligibility", "unresolved") for r in members}
        eligibility = (
            "yes" if "yes" in statuses else "no" if statuses == {"no"} else "unresolved"
        )
        resolved = [r for r in members if r.get("assessment_resolved") == "yes"]
        labels = {
            r.get("adjudicated_disposition") or r.get("classification", "unresolved")
            for r in resolved
        }
        conflict = len(labels) > 1 or {"yes", "no"}.issubset(statuses)
        if conflict:
            eligibility = "unresolved"
        units.append(
            dict(
                canonical_source_id=sid,
                source_ids=";".join(sorted(r["source_id"] for r in members)),
                catalog_entries=len(members),
                assessment_eligibility=eligibility,
                assessment_resolved="yes" if resolved and not conflict else "no",
                disposition=";".join(sorted(labels)),
                adjudication_conflict="yes" if conflict else "no",
            )
        )
    return list(lookup.values()), units


def metadata_provenance(aid, path, provider):
    sidecar = path.with_suffix(path.suffix + ".source.json")
    if not sidecar.exists() and provider == "openalex":
        path = s.CACHE / "identity_search" / (aid + ".json")
        sidecar = path.with_suffix(path.suffix + ".source.json")
    if not sidecar.exists():
        raise ValueError("Verified metadata lacks source provenance: " + aid)
    origin = json.loads(sidecar.read_text())
    return dict(
        article_id=aid,
        provider=provider,
        path=str(path.relative_to(s.ROOT)),
        url=origin["url"],
        sha256=pilot.sha256(path.read_bytes()),
        retrieved_at=origin["retrieved_at"],
    )


def assessment_inventory(units, aliases):
    pilot.unique(units, ["unit_id"])
    catalog = {r["source_id"] for r in s.read("sources.csv")}
    docs = {r["document_id"]: r for r in s.read("documents.csv")}
    docs.update({r["member_id"]: r for r in s.read("archive_members.csv")})
    inventory, links, evidence = [], [], []
    for row in units:
        uid = row["unit_id"]
        if row["assessment_eligibility"] not in {"yes", "no", "unresolved"} or row[
            "assessment_resolved"
        ] not in {"yes", "no"}:
            raise ValueError("Invalid assessment unit status: " + uid)
        if (
            row["assessment_resolved"] == "yes"
            and row["assessment_eligibility"] != "yes"
        ):
            raise ValueError("Resolved assessment unit must be eligible: " + uid)
        roles = {d["role"] for d in row["document_ids"]}
        substantive = {
            "assessment",
            "assessment_report",
            "independent_assessment",
            "same_assessment_discussion_paper",
        }
        if row["assessment_resolved"] == "yes" and not (
            roles & substantive
            or any(role.startswith("assessment_revised_") for role in roles)
        ):
            raise ValueError("Resolved unit needs an assessment report: " + uid)
        if row.get("retrieval_source_ids") and not row.get("retrieval_alias_evidence"):
            raise ValueError("Retrieval alias lacks evidence: " + uid)
        declared_sources = set(
            row["source_ids"]
            + row.get("aggregate_context_source_ids", [])
            + row.get("retrieval_source_ids", [])
        )
        if not row.get("original_title") or not row.get("reviewer_team"):
            raise ValueError("Assessment unit lacks target/team: " + uid)
        if row["assessment_resolved"] == "yes" and not all(
            row.get(k) for k in ["evidence", "evidence_locator", "document_ids"]
        ):
            raise ValueError("Resolved assessment unit lacks evidence: " + uid)
        aid = article_id(row["original_title"])
        locator = row["evidence_locator"]
        inventory.append(
            dict(
                unit_id=uid,
                article_id=aliases.get(aid, aid),
                reviewer_team="; ".join(row["reviewer_team"]),
                assessment_eligibility=row["assessment_eligibility"],
                assessment_resolved=row["assessment_resolved"],
                disposition=row["disposition"],
                evidence_summary=row["evidence"],
                evidence_locator=(
                    json.dumps(locator, ensure_ascii=False)
                    if isinstance(locator, (dict, list))
                    else locator
                ),
                limitations=row["limitations"],
            )
        )
        for role, ids in [
            ("assessment_source", row["source_ids"]),
            ("aggregate_context", row.get("aggregate_context_source_ids", [])),
            ("verified_retrieval_alias", row.get("retrieval_source_ids", [])),
        ]:
            for sid in ids:
                if sid not in catalog:
                    raise ValueError("Assessment source outside catalog: " + sid)
                relation = (
                    "misdirected_catalog_attachment"
                    if row.get("catalog_mismatch", {}).get("source_id") == sid
                    else role
                )
                links.append(dict(unit_id=uid, source_id=sid, relation=relation))
        for document in row["document_ids"]:
            did = document["document_id"]
            if did not in docs:
                raise ValueError("Assessment document outside inventory: " + did)
            if docs[did]["source_id"] not in declared_sources:
                raise ValueError("Assessment document from undeclared source: " + did)
            evidence.append(
                dict(unit_id=uid, document_id=did, document_role=document["role"])
            )
    return inventory, links, evidence


def build(refresh_metadata=False):
    reviews = {}
    for path in sorted((s.DATA / "reviews").glob("*.json")):
        for row in json.loads(path.read_text()):
            if row["source_id"] in reviews:
                raise ValueError("Duplicate review: " + row["source_id"])
            reviews[row["source_id"]] = normalize_review(row)
    rows = []
    for source in s.read("sources.csv"):
        rows.append(
            reviews.get(
                source["source_id"],
                dict.fromkeys(REVIEW_FIELDS, "")
                | {
                    "source_id": source["source_id"],
                    "review_status": "pending",
                    "classification": "unresolved",
                },
            )
        )
    rows, units = adjudicate_reviews(rows, s.read("source_adjudications.csv"))
    s.write("source_reviews.csv", rows, REVIEW_FIELDS)
    s.write(
        "source_units.csv",
        units,
        [
            "canonical_source_id",
            "source_ids",
            "catalog_entries",
            "assessment_eligibility",
            "assessment_resolved",
            "disposition",
            "adjudication_conflict",
        ],
    )
    articles, links = {}, []
    for source in s.read("sources.csv"):
        r = reviews.get(source["source_id"], {})
        title = (
            source["title"]
            if source["collection"] == "reports"
            else r.get("target_title", "")
        )
        if not title:
            continue
        aid = article_id(title)
        if aid not in articles:
            articles[aid] = dict.fromkeys(ARTICLE_FIELDS, "") | dict(
                article_id=aid,
                title=title,
                doi=pilot.normalize_doi(r.get("target_doi", "")),
                journal=source["journal"],
                identity_verified="pending",
                retracted="unknown",
            )
        links.append(
            dict(
                source_id=source["source_id"],
                article_id=aid,
                relation="catalog_or_review_target_hint",
                evidence=(
                    "I4R report catalog target title"
                    if source["collection"] == "reports"
                    else "reviewed source target title"
                ),
            )
        )
    for roster_name in [
        "aggregate_article_roster.json",
        "psychology_article_roster.json",
    ]:
        path = s.DATA / roster_name
        if not path.exists():
            continue
        for r in json.loads(path.read_text()):
            title = r.get("title", r.get("original_title", ""))
            aid = article_id(title)
            if aid not in articles:
                articles[aid] = dict.fromkeys(ARTICLE_FIELDS, "") | dict(
                    article_id=aid,
                    title=title,
                    identity_verified="pending",
                    retracted="unknown",
                )
            doi = pilot.normalize_doi(r.get("doi", r.get("original_doi", "")))
            if doi:
                articles[aid]["doi"] = doi
            links.append(
                dict(
                    source_id=r["source_id"],
                    article_id=aid,
                    relation="assessed_article_roster",
                    evidence=r.get("evidence", r.get("evidence_pages", "")),
                )
            )
            for sid in r.get("related_source_ids", []):
                if sid in {x["source_id"] for x in s.read("sources.csv")}:
                    links.append(
                        dict(
                            source_id=sid,
                            article_id=aid,
                            relation="roster_linked_report_or_reply",
                            evidence=r["source_id"],
                        )
                    )
    inventory_path = s.DATA / "assessment_inventory.json"
    unit_records = (
        json.loads(inventory_path.read_text()) if inventory_path.exists() else []
    )
    for unit in unit_records:
        aid = article_id(unit["original_title"])
        if aid not in articles:
            articles[aid] = dict.fromkeys(ARTICLE_FIELDS, "") | dict(
                article_id=aid,
                title=unit["original_title"],
                identity_verified="pending",
                retracted="unknown",
            )
        if unit.get("original_doi"):
            doi = pilot.normalize_doi(unit["original_doi"])
            if articles[aid]["doi"] and articles[aid]["doi"] != doi:
                raise ValueError("Assessment target DOI conflicts with candidate")
            articles[aid]["doi"] = doi
        for sid in unit["source_ids"]:
            links.append(
                dict(
                    source_id=sid,
                    article_id=aid,
                    relation=(
                        "misdirected_catalog_attachment"
                        if unit.get("catalog_mismatch", {}).get("source_id") == sid
                        else "document_verified_assessment_target"
                    ),
                    evidence=unit["unit_id"],
                )
            )
    for r in s.read("curated_claims.csv"):
        aid = article_id(r["title"])
        if aid not in articles:
            articles[aid] = dict.fromkeys(ARTICLE_FIELDS, "") | dict(
                article_id=aid,
                title=r["title"],
                identity_verified="pending",
                retracted="unknown",
            )
        if r["doi"]:
            articles[aid]["doi"] = r["doi"]
        links.append(
            dict(
                source_id=r["source_id"],
                article_id=aid,
                relation="curated_error_evidence",
                evidence=r["evidence_locator"],
            )
        )
    # Explicit OSF links connect records, not necessarily new articles.
    by_source = collections.defaultdict(set)
    for r in links:
        by_source[r["source_id"]].add(r["article_id"])
    for r in s.read("source_links.csv"):
        if r["related_source_id"]:
            for aid in by_source[r["source_id"]]:
                if aid not in by_source[r["related_source_id"]]:
                    links.append(
                        dict(
                            source_id=r["related_source_id"],
                            article_id=aid,
                            relation="linked_assessment_or_reply",
                            evidence=r["source_id"] + ": " + r["url"],
                        )
                    )
                    by_source[r["related_source_id"]].add(aid)
    # Curated original DOI/title mappings take precedence over hints; retain a ledger.
    decisions = s.read("identity_decisions.csv")
    for r in decisions:
        aid = r["article_id"]
        if aid not in articles:
            articles[aid] = dict.fromkeys(ARTICLE_FIELDS, "") | dict(
                article_id=aid, identity_verified="pending", retracted="unknown"
            )
        for name in ["title", "doi"]:
            if r.get(name):
                articles[aid][name] = r[name]
    accepted_sources = []
    if not refresh_metadata:
        for frozen in s.read("verified_metadata.csv"):
            aid = frozen["article_id"]
            if aid in articles:
                if articles[aid]["doi"] and articles[aid]["doi"] != frozen["doi"]:
                    raise ValueError("Frozen metadata DOI mismatch: " + aid)
                articles[aid].update({k: frozen[k] for k in ARTICLE_FIELDS})
    for aid, record in (list(articles.items()) if refresh_metadata else []):
        path = s.CACHE / "identities" / (aid + ".json")
        if path.exists():
            work = json.loads(path.read_text())
            if (
                record["doi"]
                and pilot.normalize_doi(work.get("doi") or "") != record["doi"]
            ):
                raise ValueError("DOI mismatch " + aid)
            if title_key(record["title"]) != title_key(work["title"]) and not any(
                r["article_id"] == aid for r in decisions
            ):
                continue
            articles[aid] = article_from_work(work, aid) | {"title": record["title"]}
            accepted_sources.append(metadata_provenance(aid, path, "openalex"))
    for aid, record in (articles.items() if refresh_metadata else []):
        path = s.CACHE / "crossref" / (aid + ".json")
        if not path.exists():
            continue
        work = json.loads(path.read_text())["message"]
        title = (work.get("title") or [""])[0]
        combined = title + (": " + work["subtitle"][0] if work.get("subtitle") else "")
        accepted_title = identity_title_key(record["title"]) in {
            identity_title_key(title),
            identity_title_key(combined),
        }
        if not accepted_title and not any(r["article_id"] == aid for r in decisions):
            continue
        if not record["doi"]:
            search = s.CACHE / "crossref_search" / (aid + ".json")
            if not search.exists():
                continue
            matched = crossref_title_match(
                record["title"], json.loads(search.read_text())["message"]["items"]
            )
            if matched is None:
                continue
            record["doi"] = pilot.normalize_doi(matched["DOI"])
        if pilot.normalize_doi(work["DOI"]) != record["doi"]:
            raise ValueError("Crossref DOI mismatch")
        publisher_date(record, work)
        accepted_sources.append(metadata_provenance(aid, path, "crossref"))
        record["identity_verified"] = "yes"
        if re.match(r"^RETRACTED(?: ARTICLE)?\s*:", title, flags=re.I):
            record["retracted"] = "yes"
        record["journal"] = (work.get("container-title") or [record["journal"]])[0]
        if not record["type"]:
            record["type"] = (
                "article"
                if work.get("type") == "journal-article"
                else work.get("type", "")
            )
    if refresh_metadata:
        s.write(
            "metadata_provenance.csv",
            accepted_sources,
            ["article_id", "provider", "path", "url", "sha256", "retrieved_at"],
        )
        frozen = []
        for aid, record in articles.items():
            if record["identity_verified"] == "yes":
                path = s.CACHE / "crossref" / (aid + ".json")
                if not path.exists():
                    path = s.CACHE / "identities" / (aid + ".json")
                sidecar = path.with_suffix(path.suffix + ".source.json")
                provenance = json.loads(sidecar.read_text()) if sidecar.exists() else {}
                frozen.append(
                    record
                    | {
                        "metadata_source": provenance.get("url", ""),
                        "metadata_sha256": pilot.sha256(path.read_bytes()),
                        "retrieved_at": provenance.get("retrieved_at", ""),
                    }
                )
        s.write(
            "verified_metadata.csv",
            frozen,
            ARTICLE_FIELDS + ["metadata_source", "metadata_sha256", "retrieved_at"],
        )
    for record in articles.values():
        add_retraction(record)
    # Merge identical resolved DOIs; do not merge approximate titles automatically.
    doi_ids, aliases = {}, {}
    for aid, r in sorted(articles.items()):
        doi = r["doi"]
        if doi and doi in doi_ids:
            aliases[aid] = doi_ids[doi]
        elif doi:
            doi_ids[doi] = aid
    for r in links:
        r["article_id"] = aliases.get(r["article_id"], r["article_id"])
    links = list({(r["source_id"], r["article_id"]): r for r in links}.values())
    articles = {k: v for k, v in articles.items() if k not in aliases}
    s.write("articles.csv", list(articles.values()), ARTICLE_FIELDS)
    s.write(
        "source_articles.csv",
        sorted(links, key=lambda r: (r["source_id"], r["article_id"])),
        LINK_FIELDS,
    )
    s.write(
        "article_aliases.csv",
        [dict(alias=k, article_id=v) for k, v in aliases.items()],
        ["alias", "article_id"],
    )
    unit_rows, unit_links, unit_docs = assessment_inventory(unit_records, aliases)
    s.write(
        "assessment_inventory.csv",
        unit_rows,
        [
            "unit_id",
            "article_id",
            "reviewer_team",
            "assessment_eligibility",
            "assessment_resolved",
            "disposition",
            "evidence_summary",
            "evidence_locator",
            "limitations",
        ],
    )
    s.write("assessment_sources.csv", unit_links, ["unit_id", "source_id", "relation"])
    s.write(
        "assessment_documents.csv",
        unit_docs,
        ["unit_id", "document_id", "document_role"],
    )
    assessments, events = [], []
    for r in s.read("curated_claims.csv"):
        aid = aliases.get(article_id(r["title"]), article_id(r["title"]))
        assessment = {k: r.get(k, "") for k in ASSESSMENT_FIELDS}
        assessment.update(article_id=aid, public_year=r.get("year", ""))
        assessments.append(assessment)
        event = {k: r.get(k, "") for k in EVENT_FIELDS}
        event.update(article_id=aid)
        events.append(event)
    s.write("assessments.csv", assessments, ASSESSMENT_FIELDS)
    s.write("events.csv", events, EVENT_FIELDS)
    print("Article candidates:", len(articles), "; source reviews:", len(reviews))


def publisher_date(record, work):
    dates = []
    for key in ["published-online", "published-print", "published"]:
        parts = work.get(key, {}).get("date-parts", [[]])[0]
        if parts:
            dates.append(
                "-".join(str(n).zfill(4 if i == 0 else 2) for i, n in enumerate(parts))
            )
    if dates:
        record["publication_date"] = min(dates)
        record["publication_year"] = record["publication_date"][:4]
        record["publication_date_source"] = (
            "https://api.crossref.org/works/" + record["doi"]
        )
    return record


def matching_year(article):
    return article.get("indexed_publication_year", article.get("publication_year", ""))


def risk_filter(article):
    year = int(matching_year(article))
    return (
        f"primary_location.source.id:{article['journal_id']},"
        f"publication_year:{year-1}-{year+1},type:{article['type']}"
    )


def abstract(work):
    inverted = work.get("abstract_inverted_index") or {}
    words = {i: word for word, positions in inverted.items() for i in positions}
    return " ".join(words[i] for i in sorted(words))


def article_from_work(work, aid=None):
    loc = work.get("primary_location") or {}
    journal = loc.get("source") or {}
    return dict(
        article_id=aid or work["id"].rsplit("/", 1)[-1],
        title=work["title"],
        doi=pilot.normalize_doi(work.get("doi") or ""),
        openalex_id=work["id"],
        journal=journal.get("display_name", ""),
        journal_id=journal.get("id", ""),
        publication_date="",
        publication_year="",
        indexed_publication_date=work["publication_date"],
        indexed_publication_year=work["publication_year"],
        publication_date_source="",
        type=work["type"],
        abstract=abstract(work),
        identity_verified="yes",
        retracted="yes" if work.get("is_retracted") else "no",
        retraction_date="",
        retraction_source="",
    )


def add_retraction(record):
    matches = [r for r in s.read("retractions.csv") if r["doi"] == record.get("doi")]
    if matches:
        earliest = min(matches, key=lambda r: r["date"])
        record.update(
            retracted="yes",
            retraction_date=earliest["date"],
            retraction_source=earliest["source_url"],
        )
    return record


def resolve(doi_only=False):
    outcomes = []
    for i, r in enumerate(s.read("articles.csv"), 1):
        aid = r["article_id"]
        if doi_only and not r["doi"]:
            continue
        try:
            if r["doi"]:
                work = s.fetch(
                    "https://api.openalex.org/works/https://doi.org/" + r["doi"],
                    s.CACHE / "identities" / (aid + ".json"),
                )
                status = "doi_resolved"
            else:
                path = s.CACHE / "identity_search" / (aid + ".json")
                payload = s.fetch(
                    pilot.api_url("works", search=r["title"], **{"per-page": 5}), path
                )
                matches = [
                    w
                    for w in payload["results"]
                    if title_key(w.get("title", "")) == title_key(r["title"])
                    and w.get("type") in {"article", "review"}
                    and w.get("doi")
                ]
                # Prefer a journal-published work; multiple DOIs remain ambiguous.
                matches = [
                    w
                    for w in matches
                    if ((w.get("primary_location") or {}).get("source") or {}).get(
                        "type"
                    )
                    == "journal"
                ]
                if len({pilot.normalize_doi(w["doi"]) for w in matches}) == 1:
                    work = matches[0]
                    path = s.CACHE / "identities" / (aid + ".json")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(work) + "\n")
                    status = "exact_title_resolved"
                else:
                    status = "ambiguous" if matches else "no_exact_title_match"
            outcomes.append(dict(article_id=aid, status=status, detail=""))
        except Exception as exc:
            outcomes.append(
                dict(article_id=aid, status="failed", detail=str(exc)[:200])
            )
            if "429" in str(exc) or "rate limit" in str(exc):
                print("Acquisition checkpointed at API rate limit", flush=True)
                break
        s.write("identity_resolution.csv", outcomes, ["article_id", "status", "detail"])
        if i % 25 == 0:
            print("Article resolution:", i, flush=True)
    s.write("identity_resolution.csv", outcomes, ["article_id", "status", "detail"])
    build(refresh_metadata=True)


def crossref_title_match(title, works, *, known_doi=False):
    if not known_doi and len(re.findall(r"\w+", title)) < 4:
        return None
    matches = []
    for work in works:
        if work.get("type") != "journal-article" or not work.get("DOI"):
            continue
        base = (work.get("title") or [""])[0]
        combined = base + (": " + work["subtitle"][0] if work.get("subtitle") else "")
        if identity_title_key(title) in {
            identity_title_key(base),
            identity_title_key(combined),
        }:
            matches.append(work)
    return (
        matches[0]
        if len({pilot.normalize_doi(w["DOI"]) for w in matches}) == 1
        else None
    )


def crossref_record(article, search_titles=False):
    doi = article["doi"]
    try:
        if not doi:
            if not search_titles:
                return article["article_id"], "no_doi"
            payload = s.fetch(
                "https://api.crossref.org/works?"
                + urllib.parse.urlencode(
                    {
                        "query.title": article["title"],
                        "filter": "type:journal-article",
                        "rows": 5,
                    }
                ),
                s.CACHE / "crossref_search" / (article["article_id"] + ".json"),
            )
            matched = crossref_title_match(
                article["title"], payload["message"]["items"]
            )
            if matched is None:
                return article["article_id"], "no_unambiguous_exact_title_match"
            doi = pilot.normalize_doi(matched["DOI"])
        s.fetch(
            "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""),
            s.CACHE / "crossref" / (article["article_id"] + ".json"),
        )
        return article["article_id"], (
            "retrieved" if article["doi"] else "exact_title_resolved"
        )
    except Exception as exc:
        return article["article_id"], str(exc)[:150]


def crossref(search_titles=False):
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for aid, status in pool.map(
            lambda a: crossref_record(a, search_titles), s.read("articles.csv")
        ):
            rows.append(dict(article_id=aid, status=status))
    s.write("crossref_retrieval.csv", rows, ["article_id", "status"])
    build(refresh_metadata=True)


def validate():
    sources = {r["source_id"] for r in s.read("sources.csv")}
    articles = {r["article_id"] for r in s.read("articles.csv")}
    for name, fields in [
        ("sources.csv", ["source_id"]),
        ("articles.csv", ["article_id"]),
        ("source_articles.csv", ["source_id", "article_id"]),
        ("assessments.csv", ["assessment_id"]),
        ("events.csv", ["event_id"]),
        ("source_reviews.csv", ["source_id"]),
        ("source_adjudications.csv", ["source_id"]),
        ("source_units.csv", ["canonical_source_id"]),
        ("assessment_inventory.csv", ["unit_id"]),
        ("assessment_sources.csv", ["unit_id", "source_id", "relation"]),
        ("assessment_documents.csv", ["unit_id", "document_id"]),
    ]:
        pilot.unique(s.read(name), fields)
    for r in (
        s.read("source_articles.csv") + s.read("assessments.csv") + s.read("events.csv")
    ):
        if r["source_id"] not in sources or r["article_id"] not in articles:
            raise ValueError("Broken source/article foreign key")
    unit_ids = {r["unit_id"] for r in s.read("assessment_inventory.csv")}
    document_ids = {r["document_id"] for r in s.read("documents.csv")} | {
        r["member_id"] for r in s.read("archive_members.csv")
    }
    for r in s.read("assessment_inventory.csv"):
        if r["article_id"] not in articles:
            raise ValueError("Missing assessment-unit article")
    for r in s.read("assessment_sources.csv"):
        if r["unit_id"] not in unit_ids or r["source_id"] not in sources:
            raise ValueError("Broken assessment-unit source link")
    for r in s.read("assessment_documents.csv"):
        if r["unit_id"] not in unit_ids or r["document_id"] not in document_ids:
            raise ValueError("Broken assessment-unit document link")
    assessments = {r["assessment_id"]: r for r in s.read("assessments.csv")}
    for r in s.read("events.csv"):
        if r["assessment_id"] not in assessments:
            raise ValueError("Missing event assessment")
        a = assessments[r["assessment_id"]]
        if a["article_id"] != r["article_id"]:
            raise ValueError("Event/assessment article mismatch")
        if r["material"] == "yes" and a["material"] != "yes":
            raise ValueError("Event overstates materiality")
        if not r["warning_id"]:
            raise ValueError("Missing shared disclosure identifier")
        if r["error_verified"] == "yes" and a["error_verified"] != "yes":
            raise ValueError("Event overstates error verification")
        if r["publicity_verified"] == "yes" and not (
            r["year"] and r["date_evidence_url"] and r["date_evidence"]
        ):
            raise ValueError("Verified exposure lacks dated evidence")
    for r in s.read("assessments.csv"):
        if r["error_verified"] == "yes" and not all(
            r[k]
            for k in [
                "affected_claim",
                "evidence_summary",
                "evidence_locator",
                "verification_scope",
            ]
        ):
            raise ValueError("Verified error lacks evidence")
    print("Registry keys and evidence gates passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "resolve", "crossref", "validate"])
    parser.add_argument("--doi-only", action="store_true")
    parser.add_argument("--refresh-metadata", action="store_true")
    parser.add_argument("--search-titles", action="store_true")
    args = parser.parse_args()
    if args.command == "resolve":
        resolve(args.doi_only)
    elif args.command == "build":
        build(args.refresh_metadata)
    elif args.command == "crossref":
        crossref(args.search_titles)
    else:
        validate()
