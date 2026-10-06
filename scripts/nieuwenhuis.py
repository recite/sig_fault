"""Resolve the complete Nieuwenhuis roster and compare frozen citation sources."""

import argparse
import collections
import hashlib
import json
import math
import re
import statistics
import time
import urllib.parse

import i4r_sources as acquisition
import pilot

DATA = pilot.ROOT / "data/nieuwenhuis"
CACHE = pilot.ROOT / "private-data/nieuwenhuis"
COVERAGE_FIELDS = [
    "paper_id",
    "target_doi",
    "api_count",
    "pages",
    "complete",
    "origin",
    "detail",
]


def history_complete(record, identity):
    return (
        record.get("complete") == "yes"
        and bool(identity.get("doi"))
        and record.get("target_doi") == identity["doi"]
        and identity.get("identity_status", "").startswith("verified")
    )


def read(name):
    path = DATA / name
    return pilot.read_csv(path) if path.exists() else []


def locator(row):
    journal = row["journal"]
    year = row["cohort"]
    match = re.search(r"\((\d+)\)", row["year_volume"])
    volume = match[1] if match else ""
    issue = row["issue"]
    url = row["link"]
    if not issue.isdigit():
        issue = ""
    if journal == "Neuron" and year == "2010":
        volume, issue = row.get("locator_volume", issue), ""
    if journal == "Neuron" and re.fullmatch(r"\d+-\d+", url):
        volume, issue = url.split("-")
    if journal in {"Science", "Journal of Neuroscience"} and url.isdigit():
        issue = url
    for pattern in [r"/(?:content|reprint)/(\d+)/(\d+)/", r"/v(\d+)/n(\d+)/"]:
        match = re.search(pattern, url)
        if match:
            volume, issue = match.groups()
    if not volume and journal == "Journal of Neuroscience":
        volume = str(int(year) - 1980)
    doi = ""
    if journal == "Nature" and url.isdigit():
        doi = "10.1038/nature" + url.zfill(5)
    elif journal == "Nature Neuroscience":
        match = re.search(r"/(nn\.\d+)\.pdf", url)
        if match:
            doi = "10.1038/" + match[1]
    return dict(
        journal=journal,
        year=year,
        volume=volume,
        issue=issue,
        page=row["page"],
        expected_doi=doi,
    )


def page_contains(pages, page):
    match = re.fullmatch(r"(\d+)(?:[-–](\d+))?", pages)
    source_pages = page.split("/")
    if not match or not all(p.isdigit() for p in source_pages):
        return False
    lo, hi = match.groups()
    if hi and len(hi) < len(lo):
        hi = lo[: len(lo) - len(hi)] + hi
    return all(int(lo) <= int(p) <= int(hi or lo) for p in source_pages)


def journal_key(value):
    return re.sub(r"[^a-z0-9]", "", value.lower()).removeprefix("the")


def matches(work, source):
    if (
        source.get("expected_doi")
        and pilot.normalize_doi(work.get("DOI", "")) != source["expected_doi"]
    ):
        return False
    journal = (work.get("container-title") or [""])[0]
    if journal_key(journal) != journal_key(source["journal"]):
        return False
    parts = (work.get("published-print") or work.get("published") or {}).get(
        "date-parts", [[]]
    )[0]
    if not parts or str(parts[0]) != source["year"]:
        return False
    for name in ["volume", "issue"]:
        if source[name] and str(work.get(name, "")) != source[name]:
            return False
    return page_contains(work.get("page", ""), source["page"])


def source_rows():
    rows = pilot.read_csv(pilot.ROOT / "data/derived/classification.csv")
    if len(rows) != 157:
        raise ValueError("Unexpected original assessment roster")
    pilot.unique(rows, ["article_id"])
    volume = ""
    for row in rows:
        if row["journal"] == "Neuron" and row["cohort"] == "2010":
            if row["issue"].isdigit():
                volume = row["issue"]
            row["locator_volume"] = volume
    return rows


def find_identity(row):
    pid = "nw_" + row["article_id"]
    source = locator(row)
    query = " ".join(source.values())
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {
            "query.bibliographic": query,
            "rows": 20,
            "filter": f"from-pub-date:{source['year']}-01-01,"
            f"until-pub-date:{source['year']}-12-31,type:journal-article",
        }
    )
    try:
        if source["expected_doi"]:
            url = "https://api.crossref.org/works/" + urllib.parse.quote(
                source["expected_doi"], safe=""
            )
        cache_key = hashlib.sha256(url.encode()).hexdigest()[:12]
        path = CACHE / "crossref" / f"{pid}_{cache_key}.json"
        if not path.exists():
            time.sleep(1)
        payload = acquisition.fetch(url, path)
        message = payload["message"]
        works = message.get("items", [message])
        valid = [w for w in works if matches(w, source)]
        distinct = {pilot.normalize_doi(w["DOI"]): w for w in valid}
        status = "verified_locator" if len(distinct) == 1 else "unresolved"
        work = next(iter(distinct.values())) if len(distinct) == 1 else {}
        identity = dict(
            paper_id=pid,
            article_id=row["article_id"],
            flag=row["flag"],
            cohort=row["cohort"],
            journal=row["journal"],
            doi=pilot.normalize_doi(work.get("DOI", "")),
            title=" ".join(work.get("title", [])),
            volume=work.get("volume", ""),
            issue=work.get("issue", ""),
            pages=work.get("page", ""),
            identity_status=status,
            identity_evidence=(
                "Unique agreement on journal, issue year, available "
                "volume/issue and containing page range."
                if work
                else f"{len(distinct)} unique DOI matches among returned candidates; "
                "review required."
            ),
            source_url=row["link"],
            metadata_url=url,
        )
        candidates = [
            dict(
                paper_id=pid,
                doi=w.get("DOI", ""),
                title=" ".join(w.get("title", [])),
                journal=" ".join(w.get("container-title", [])),
                volume=w.get("volume", ""),
                issue=w.get("issue", ""),
                pages=w.get("page", ""),
                locator_match=matches(w, source),
            )
            for w in works
        ]
        return identity, candidates
    except Exception as exc:
        return (
            dict(
                paper_id=pid,
                article_id=row["article_id"],
                flag=row["flag"],
                cohort=row["cohort"],
                journal=row["journal"],
                doi="",
                title="",
                volume="",
                issue="",
                pages="",
                identity_status="retrieval_failed",
                identity_evidence=str(exc)[:200],
                source_url=row["link"],
                metadata_url=url,
            ),
            [],
        )


def resolve():
    known = {r["paper_id"]: r for r in read("identities.csv")}
    results = []
    for row in source_rows():
        pid = "nw_" + row["article_id"]
        if known.get(pid, {}).get("identity_status", "").startswith("verified"):
            results.append((known[pid], []))
        else:
            results.append(find_identity(row))
    identities = [r[0] for r in results]
    candidates = [r for _, group in results for r in group]
    pilot.write_csv(DATA / "identities.csv", identities, list(identities[0]))
    if candidates:
        pilot.write_csv(
            DATA / "identity_candidates.csv", candidates, list(candidates[0])
        )
    print(dict(collections.Counter(r["identity_status"] for r in identities)))


def journals():
    """Acquire publisher journal indexes to resolve weak bibliographic searches."""
    needed = {
        r["journal"]
        for r in read("identities.csv")
        if not r["identity_status"].startswith("verified")
    }
    issns = collections.defaultdict(set)
    for path in (CACHE / "crossref").glob("*.json"):
        if path.name.endswith(".source.json"):
            continue
        message = json.loads(path.read_text())["message"]
        for work in message.get("items", [message]):
            for journal in needed:
                if any(
                    journal_key(t) == journal_key(journal)
                    for t in work.get("container-title", [])
                ):
                    issns[journal].update(work.get("ISSN", []))
    for journal in sorted(needed):
        if not issns[journal]:
            continue
        issn = min(issns[journal])
        cursor, seen, works, pages, totals = "*", set(), [], 0, set()
        while cursor:
            if cursor in seen:
                raise ValueError("Repeated Crossref journal cursor")
            seen.add(cursor)
            url = (
                f"https://api.crossref.org/journals/{issn}/works?"
                + urllib.parse.urlencode(
                    {
                        "filter": (
                            "from-pub-date:2008-01-01,until-pub-date:2010-12-31,"
                            "type:journal-article"
                        ),
                        "rows": 1000,
                        "cursor": cursor,
                        "select": (
                            "DOI,title,container-title,volume,issue,page,"
                            "published-print,published,ISSN"
                        ),
                    }
                )
            )
            key = pilot.sha256(url.encode())[:16]
            path = CACHE / "journals" / issn / (key + ".json")
            if not path.exists():
                time.sleep(1)
            message = acquisition.fetch(url, path)["message"]
            pages += 1
            totals.add(message["total-results"])
            works.extend(message["items"])
            print(journal, len(works), "/", message["total-results"], flush=True)
            if not message["items"] or len(works) >= message["total-results"]:
                break
            cursor = message.get("next-cursor")
        if len(totals) != 1 or len(works) != next(iter(totals)):
            raise ValueError("Incomplete or changing journal metadata index")
        pilot.unique(works, ["DOI"])


def reconcile():
    """Match corrected source locators against acquired publisher metadata."""
    candidates = []
    for path in sorted(
        list((CACHE / "crossref").glob("nw_*.json"))
        + list((CACHE / "journals").rglob("*.json"))
    ):
        if path.name.endswith(".source.json"):
            continue
        url = json.loads(path.with_suffix(".json.source.json").read_text())["url"]
        message = json.loads(path.read_text())["message"]
        for work in message.get("items", [message]):
            candidates.append((work, url))
    known = {r["paper_id"]: r for r in pilot.read_csv(pilot.DATA / "identities.csv")}
    old = {r["paper_id"]: r for r in read("identities.csv")}
    for source in source_rows():
        pid = "nw_" + source["article_id"]
        choices = {
            pilot.normalize_doi(w["DOI"]): (w, url)
            for w, url in candidates
            if matches(w, locator(source))
        }
        row = old[pid]
        if len(choices) == 1:
            doi, (work, url) = next(iter(choices.items()))
            if pid in known and doi != known[pid]["doi"]:
                raise ValueError("Independent identity disagrees with pilot: " + pid)
            row.update(
                doi=doi,
                title=" ".join(work.get("title", [])),
                volume=work.get("volume", ""),
                issue=work.get("issue", ""),
                pages=work.get("page", ""),
                identity_status="verified_locator",
                identity_evidence="Unique cached publisher DOI matching normalized "
                "journal, print year, available volume/issue and containing pages.",
                metadata_url=url,
            )
        elif pid in known:
            item = known[pid]
            row.update(
                doi=item["doi"],
                title=item["title"],
                volume=item["volume"],
                issue=item["issue"],
                pages=item["pages"],
                identity_status="verified_pilot",
                identity_evidence=item["identity_evidence"],
                metadata_url=item["identity_source"],
            )
        else:
            row.update(
                doi="",
                title="",
                volume="",
                issue="",
                pages="",
                identity_status="unresolved",
                identity_evidence=f"{len(choices)} matching DOIs in cached metadata; "
                "additional source review required.",
            )
    for decision in read("identity_decisions.csv"):
        pid = decision["paper_id"]
        choices = [
            (w, url)
            for w, url in candidates
            if pilot.normalize_doi(w["DOI"]) == decision["doi"]
        ]
        if not choices or not decision["evidence"]:
            raise ValueError("Identity decision lacks publisher evidence: " + pid)
        work, url = choices[0]
        if journal_key(" ".join(work.get("title", []))) != journal_key(
            decision["title"]
        ):
            raise ValueError("Adjudicated title differs from publisher title: " + pid)
        old[pid].update(
            doi=decision["doi"],
            title=decision["title"],
            volume=work.get("volume", ""),
            issue=work.get("issue", ""),
            pages=work.get("page", ""),
            identity_status="verified_adjudication",
            identity_evidence=decision["evidence"],
            metadata_url=url,
        )
    rows = list(old.values())
    pilot.unique([r for r in rows if r["doi"]], ["doi"])
    pilot.write_csv(DATA / "identities.csv", rows, list(rows[0]))
    print(dict(collections.Counter(r["identity_status"] for r in rows)))


def import_pilot():
    coverage = {r["paper_id"]: r for r in read("coverage.csv")}
    edges = read("citation_edges.csv")
    identities = {r["paper_id"]: r for r in read("identities.csv")}
    known = {r["paper_id"]: r for r in pilot.read_csv(pilot.DATA / "identities.csv")}
    old_edges = pilot.read_csv(pilot.DATA / "citation_edges.csv")
    for record in pilot.read_csv(pilot.DATA / "coverage.csv"):
        pid = record["paper_id"]
        if not pid.startswith("nw_") or record["complete"] != "yes":
            continue
        if identities.get(pid, {}).get("doi") not in {None, "", known[pid]["doi"]}:
            raise ValueError("Pilot/full-roster DOI disagreement: " + pid)
        if history_complete(coverage.get(pid, {}), identities.get(pid, {})):
            continue
        selected = [r for r in old_edges if r["paper_id"] == pid]
        if len(selected) != int(record["api_count"]):
            raise ValueError("Incomplete frozen pilot history: " + pid)
        edges = [r for r in edges if r["paper_id"] != pid] + selected
        coverage[pid] = record | dict(
            origin="frozen_pilot", detail="", target_doi=known[pid]["doi"]
        )
    pilot.unique(edges, ["paper_id", "citing_work_id"])
    pilot.write_csv(DATA / "citation_edges.csv", edges, pilot.EDGE_FIELDS)
    pilot.write_csv(
        DATA / "coverage.csv",
        list(coverage.values()),
        COVERAGE_FIELDS,
    )


def fetch():
    import_pilot()
    edges = read("citation_edges.csv")
    coverage = {r["paper_id"]: r for r in read("coverage.csv")}
    fields = (
        "id,doi,title,publication_date,publication_year,type,referenced_works,"
        "ids,locations,best_oa_location"
    )
    for paper in read("identities.csv"):
        pid = paper["paper_id"]
        if history_complete(coverage.get(pid, {}), paper) or not paper["doi"]:
            continue
        pages, total = 0, 0
        try:
            target = acquisition.fetch(
                "https://api.openalex.org/works/https://doi.org/" + paper["doi"],
                CACHE
                / "openalex"
                / pid
                / (pilot.sha256(paper["doi"].encode()) + ".json"),
            )
            if pilot.normalize_doi(target.get("doi") or "") != paper["doi"]:
                raise ValueError("Target DOI mismatch")
            cursor, seen, totals, works = "*", set(), set(), []
            while cursor:
                if cursor in seen:
                    raise ValueError("Repeated citation cursor")
                seen.add(cursor)
                pages += 1
                url = pilot.api_url(
                    "works",
                    filter=f"cites:{target['id'].split('/')[-1]},"
                    f"to_publication_date:{pilot.CUTOFF}",
                    per_page=100,
                    cursor=cursor,
                    select=fields,
                    sort="publication_date",
                )
                batch = acquisition.fetch(
                    url,
                    CACHE
                    / "citations"
                    / pid
                    / target["id"].split("/")[-1]
                    / f"{pages:04d}.json",
                )
                totals.add(batch["meta"]["count"])
                works.extend(batch["results"])
                cursor = batch["meta"].get("next_cursor")
                if not batch["results"]:
                    break
            total = len(works)
            if len(totals) != 1 or total != next(iter(totals)):
                raise ValueError("Incomplete or changing citation history")
            normalized = pilot.normalize_edges(
                paper | dict(publication_date=target["publication_date"]), target, works
            )
            edges = [r for r in edges if r["paper_id"] != pid] + normalized
            coverage[pid] = dict(
                paper_id=pid,
                target_doi=paper["doi"],
                api_count=total,
                pages=pages,
                complete="yes",
                origin="full_roster",
                detail="",
            )
        except Exception as exc:
            coverage[pid] = dict(
                paper_id=pid,
                target_doi=paper["doi"],
                api_count=total,
                pages=pages,
                complete="no",
                origin="full_roster",
                detail=str(exc)[:200],
            )
            if "rate limit" in str(exc) or "429" in str(exc):
                break
    pilot.unique(edges, ["paper_id", "citing_work_id"])
    pilot.write_csv(DATA / "citation_edges.csv", edges, pilot.EDGE_FIELDS)
    pilot.write_csv(
        DATA / "coverage.csv",
        list(coverage.values()),
        COVERAGE_FIELDS,
    )


def eligible_edges(edges, types):
    return [
        r
        for r in edges
        if r["reference_verified"] == "yes"
        and not r["duplicate_of"]
        and r["before_original_date"] == "no"
        and r["citing_work_id"] != r["target_work_id"]
        and r["type"] in types
    ]


def duplicate_checks(edges):
    groups = collections.defaultdict(list)
    for row in edges:
        if row["doi"]:
            groups[row["paper_id"], row["doi"]].append(row)
    checks = []
    for (pid, doi), rows in sorted(groups.items()):
        if len(rows) < 2:
            continue
        signatures = {
            (
                r["publication_year"],
                r["type"] in {"article", "review"},
                r["type"] in pilot.ALLOWED_TYPES,
                r["before_original_date"],
            )
            for r in rows
        }
        affected = any(2009 <= int(r["publication_year"]) <= 2015 for r in rows)
        checks.append(
            dict(
                paper_id=pid,
                doi=doi,
                records=len(rows),
                years=";".join(sorted({r["publication_year"] for r in rows})),
                types=";".join(sorted({r["type"] for r in rows})),
                bridge_review_required=(
                    "yes" if affected and len(signatures) > 1 else "no"
                ),
            )
        )
    return checks


def compare():
    import_pilot()
    historical = pilot.read_csv(pilot.ROOT / "data/derived/panel.csv")
    historical_ids = {str(r["article_id"]) for r in historical}
    if len(historical_ids) != 153:
        raise ValueError("Historical bridge cohort changed")
    identities = {r["paper_id"]: r for r in read("identities.csv")}
    complete = {
        r["paper_id"]
        for r in read("coverage.csv")
        if history_complete(r, identities.get(r["paper_id"], {}))
    }
    edges = read("citation_edges.csv")
    checks = duplicate_checks(edges)
    pilot.write_csv(
        DATA / "duplicate_checks.csv",
        checks,
        ["paper_id", "doi", "records", "years", "types", "bridge_review_required"],
    )
    blocked = {r["paper_id"] for r in checks if r["bridge_review_required"] == "yes"}
    complete -= blocked
    primary = eligible_edges(edges, {"article", "review"})
    broad = eligible_edges(edges, pilot.ALLOWED_TYPES)
    counts = collections.Counter(
        (r["paper_id"], r["publication_year"]) for r in primary
    )
    broad_counts = collections.Counter(
        (r["paper_id"], r["publication_year"]) for r in broad
    )
    panel = []
    for row in historical:
        pid = "nw_" + row["article_id"]
        key = (pid, row["year"])
        observed = pid in complete
        panel.append(
            dict(
                article_id=row["article_id"],
                paper_id=pid,
                year=row["year"],
                flag=row["flag"],
                cohort=row["cohort"],
                journal=row["journal"],
                wos=int(row["citations"]),
                openalex=counts[key] if observed else "",
                openalex_broad=broad_counts[key] if observed else "",
                status="complete" if observed else "missing_history",
            )
        )
    pilot.write_csv(DATA / "paired_panel.csv", panel, list(panel[0]))
    summaries = []
    for year in range(2009, 2016):
        for flag in ["0", "1"]:
            group = [
                r
                for r in panel
                if r["year"] == str(year)
                and r["flag"] == flag
                and r["status"] == "complete"
            ]
            if not group:
                continue
            for source in ["wos", "openalex", "openalex_broad"]:
                values = [r[source] for r in group]
                summaries.append(
                    dict(
                        year=year,
                        flag=flag,
                        source=source,
                        papers=len(group),
                        total=sum(values),
                        mean=statistics.mean(values),
                        median=statistics.median(values),
                    )
                )
    pilot.write_csv(
        DATA / "paired_summary.csv",
        summaries,
        ["year", "flag", "source", "papers", "total", "mean", "median"],
    )
    # DOI matching is a diagnostic of shared links, not a completeness certificate.
    original = pilot.read_csv(pilot.ROOT / "data/derived/raw.csv")
    wos = {}
    for r in original:
        pid = "nw_" + r["article_id"]
        if (
            pid in complete
            and r["article_id"] in historical_ids
            and r["doi"]
            and r["duplicate"] == "FALSE"
            and r["false_link"] == "FALSE"
        ):
            key = (pid, pilot.normalize_doi(r["doi"]))
            if key in wos:
                raise ValueError("Repeated historical DOI")
            wos[key] = r
    oa = {
        (r["paper_id"], r["doi"]): r
        for r in edges
        if r["doi"]
        and r["paper_id"] in complete
        and r["paper_id"].removeprefix("nw_") in historical_ids
        and r["reference_verified"] == "yes"
        and not r["duplicate_of"]
        and r["citing_work_id"] != r["target_work_id"]
    }
    links = []
    for key in sorted(wos.keys() | oa.keys()):
        left, right = wos.get(key), oa.get(key)
        wy, oy = left["year"] if left else "", (
            right["publication_year"] if right else ""
        )
        if not any(y and 2009 <= int(y) <= 2015 for y in [wy, oy]):
            continue
        links.append(
            dict(
                paper_id=key[0],
                doi=key[1],
                wos_year=wy,
                openalex_year=oy,
                openalex_type=right["type"] if right else "",
                openalex_before_original_date=(
                    right["before_original_date"] if right else ""
                ),
                presence=(
                    "both"
                    if left and right
                    else "wos_only" if left else "openalex_only"
                ),
                year_agrees=str(wy == oy).lower() if left and right else "",
            )
        )
    pilot.write_csv(
        DATA / "doi_overlap.csv",
        links,
        [
            "paper_id",
            "doi",
            "wos_year",
            "openalex_year",
            "openalex_type",
            "openalex_before_original_date",
            "presence",
            "year_agrees",
        ],
    )
    paired = [r for r in panel if r["year"] == "2010" and r["status"] == "complete"]
    status = dict(
        historical_papers=len(historical_ids),
        complete_paired_papers=len(paired),
        complete_flagged=sum(r["flag"] == "1" for r in paired),
        complete_comparison=sum(r["flag"] == "0" for r in paired),
        full_bridge_available=len(paired) == len(historical_ids),
        doi_links=dict(collections.Counter(r["presence"] for r in links)),
        shared_doi_year_disagreements=sum(r["year_agrees"] == "false" for r in links),
    )
    (DATA / "status.json").write_text(json.dumps(status, indent=2) + "\n")
    print(status)


def report():
    status = json.loads((DATA / "status.json").read_text())
    identities = read("identities.csv")
    summaries = read("paired_summary.csv")
    verified = sum(r["identity_status"].startswith("verified") for r in identities)
    n = status["complete_paired_papers"]
    lines = [
        "# Nieuwenhuis citation-source comparison",
        "",
        "This comparison holds the original papers and years fixed while replacing "
        "the historical Web of Science exports with OpenAlex records. It measures "
        "source discrepancies; neither database is assumed to be ground truth.",
        "",
        f"The roster retains {len(identities)} classified papers; "
        f"{verified} identities "
        f"are resolved. Complete paired histories currently cover {n} of the "
        f"{status['historical_papers']} historical analysis papers "
        f"({status['complete_flagged']} flagged, "
        f"{status['complete_comparison']} comparison).",
        "",
        (
            "A full-cohort database comparison is still pending."
            if not status["full_bridge_available"]
            else "The historical cohort has complete paired histories."
        ),
        "These counts measure download progress, not OpenAlex's coverage of "
        "the literature. An uncollected history says nothing about how many "
        "citations the database contains for that paper.",
        "",
        "## Same-paper annual counts",
        "",
        "Web of Science retains the historical counting rules. OpenAlex's primary "
        "count includes articles and reviews; its broader count also includes "
        "preprints, book chapters and proceedings articles. The historical exports "
        "lack the document-type detail needed to make these restrictions identical.",
        "",
        "| Year | Group | Source | Papers | Mean citations | Median citations |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    names = {
        "wos": "Web of Science",
        "openalex": "OpenAlex, articles/reviews",
        "openalex_broad": "OpenAlex, broader types",
    }
    for row in summaries:
        group = "Flagged" if row["flag"] == "1" else "Comparison"
        lines.append(
            f"| {row['year']} | {group} | {names[row['source']]} | "
            f"{row['papers']} | {float(row['mean']):.1f} | {float(row['median']):.1f} |"
        )
    lines += [
        "",
        "The table includes only papers with complete histories in both "
        "sources. Missing histories are not zero. These are descriptive counts "
        "for the available paired sample, not an estimate of publicity's effect.",
    ]
    contrasts = read("source_contrasts.csv")
    lines += [
        "",
        "## Does the source change the growth comparison?",
        "",
        "The paired estimator compares the flagged-minus-comparison change in "
        "each database, then subtracts the Web of Science contrast from the "
        "OpenAlex contrast. It uses the same papers, a 2010 baseline, and either "
        "2012 or the annual average over 2012–2015. The 2009 publication cohort "
        "is also reported separately.",
        "",
    ]
    if not contrasts or all(r["status"] == "missing_group" for r in contrasts):
        lines += [
            "The source contrast is not yet estimable: no comparison-group "
            "paper has a complete OpenAlex history. The available flagged "
            "histories cannot establish whether switching databases changes "
            "the relative citation growth of flagged and comparison papers.",
            "",
        ]
    else:
        lines += [
            "The absolute contrast uses citations per paper per year. The "
            "proportional contrast is the ratio of flagged post/pre growth to "
            "comparison post/pre growth. Its source discrepancy below is the "
            "percentage change in that ratio when switching to OpenAlex, not "
            "a percentage-point difference between effect estimates.",
            "",
            "| Cohort | Post years | OpenAlex types | Contrast | Flagged / "
            "comparison | Source discrepancy [95% interval] | Status |",
            "| --- | --- | --- | --- | ---: | ---: | --- |",
        ]
        for row in contrasts:
            proportional = row["estimand"] == "log_ratio"

            def display(value):
                if value == "":
                    return "pending"
                number = float(value)
                if proportional:
                    return f"{100 * math.expm1(number):.1f}%"
                return f"{number:.2f}"

            estimate = display(row["difference"])
            interval = f"[{display(row['lower'])}, {display(row['upper'])}]"
            kind = "Growth ratio" if proportional else "Absolute change"
            lines.append(
                f"| {row['cohort']} | {row['post']} | {names[row['source']]} | "
                f"{kind} | {row['n_flagged']} / {row['n_comparison']} | "
                f"{estimate} {interval} | {row['status']} |"
            )
        lines.append("")
    lines += [
        "Intervals use 9,999 paired paper resamples within flag groups. Each "
        "draw retains the same paper's counts in both databases. Missing groups "
        "produce no contrast; undefined proportional draws are counted and "
        "withhold that interval rather than being silently discarded. These "
        "intervals describe variation across observed papers, not uncertainty "
        "about missing citations or the causal effect of publicizing errors.",
        "",
        "See [source contrasts](../../data/nieuwenhuis/source_contrasts.csv) "
        "and [period means and medians](../../data/nieuwenhuis/period_summary.csv).",
        "",
        "## Citation links and publication years",
        "",
    ]
    links = status["doi_links"]
    shared = links.get("both", 0)
    disagreement = status["shared_doi_year_disagreements"]
    lines += [
        f"Among DOI-bearing relationships dated 2009–2015 in at least one source, "
        f"{shared:,} occur in both, {links.get('wos_only', 0):,} occur only in "
        f"the historical frame, and {links.get('openalex_only', 0):,} occur only "
        f"in OpenAlex. Of the shared relationships, {disagreement:,} have different "
        "publication years. This link diagnostic includes all retrieved OpenAlex "
        "types and preserves links dated before the target paper; those records "
        "can be excluded from annual counts without being called missing links.",
        "",
        "The DOI crosswalk retains both years and the OpenAlex document type. "
        "Non-DOI records remain in citation counts but cannot enter this exact-DOI "
        "crosswalk. A link absent from one frame can reflect a metadata typo, "
        "index coverage, publication/version dating or a reference error; absence "
        "alone does not establish which.",
        "",
        "## Reproduce and resume",
        "",
        "```sh",
        "make nieuwenhuis",
        "make nieuwenhuis-test",
        "make nieuwenhuis-fetch",
        "```",
        "",
        "The first two commands run offline from frozen public inputs. The fetch "
        "target resumes publisher identity checks and incoming OpenAlex citations, "
        "retaining completed pilot histories and respecting the shared rate-limit "
        "checkpoint. Set OPENALEX_API_KEY in the environment for authenticated "
        "requests. No key is stored in the data.",
        "",
        "See [design](design.md), [construction and dictionary](data.md), "
        "[source-discrepancy diagnostics](diagnostics.md), "
        "[OpenCitations link check](validation.md), "
        "[status JSON](../../data/nieuwenhuis/status.json), and "
        "[paired records](../../data/nieuwenhuis/paired_panel.csv).",
    ]
    folder = pilot.ROOT / "docs/nieuwenhuis"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "README.md").write_text("\n".join(lines) + "\n")
    inputs = [
        pilot.ROOT / "data/derived" / name
        for name in ["classification.csv", "raw.csv", "panel.csv"]
    ]
    inputs += [
        pilot.DATA / name
        for name in ["identities.csv", "coverage.csv", "citation_edges.csv"]
    ]
    (DATA / "input_hashes.json").write_text(
        json.dumps(
            {
                "normalization": "CRLF to LF; otherwise unchanged bytes",
                "sha256": {
                    str(path.relative_to(pilot.ROOT)): pilot.sha256(
                        path.read_bytes().replace(b"\r\n", b"\n")
                    )
                    for path in inputs
                },
            },
            indent=2,
        )
        + "\n"
    )


def manifest():
    rows = []
    for path in sorted(CACHE.rglob("*.source.json")):
        row = json.loads(path.read_text())
        rows.append(
            dict(
                path=str(path.relative_to(pilot.ROOT)).removesuffix(".source.json"),
                **row,
            )
        )
    pilot.write_csv(
        DATA / "source_manifest.csv",
        rows,
        ["path", "url", "retrieved_at", "sha256", "bytes"],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "resolve",
            "manifest",
            "fetch",
            "compare",
            "reconcile",
            "report",
            "journals",
        ],
    )
    args = parser.parse_args()
    {
        "resolve": resolve,
        "manifest": manifest,
        "fetch": fetch,
        "compare": compare,
        "reconcile": reconcile,
        "journals": journals,
        "report": report,
    }[args.command]()
