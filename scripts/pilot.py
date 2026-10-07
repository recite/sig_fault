"""Collect, freeze, and document a citation-reliance pilot (Python standard library)."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/pilot"
CACHE = ROOT / "private-data/pilot"
SEED = "20261004"
CUTOFF = "2025-12-31"
ALLOWED_TYPES = {"article", "review", "preprint", "book-chapter", "proceedings-article"}
EDGE_FIELDS = [
    "paper_id",
    "target_work_id",
    "citing_work_id",
    "doi",
    "title",
    "publication_date",
    "publication_year",
    "type",
    "reference_verified",
    "oa_urls",
    "pmcid",
    "before_original_date",
    "duplicate_of",
    "eligible_type",
]
SAMPLE_FIELDS = EDGE_FIELDS + [
    "pair_id",
    "period",
    "stratum_size",
    "stratum_sample_size",
    "conditional_inclusion_probability",
    "sample_rank",
]
RATING_FIELDS = [
    "pair_id",
    "reader_id",
    "valid_link",
    "fulltext_read",
    "claim_identified",
    "relies_on_claim",
    "qualification",
    "use_role",
    "evidence_locator",
    "evidence_excerpt",
    "notes",
]
RETRIEVAL_FIELDS = [
    "pair_id",
    "status",
    "url",
    "local_path",
    "sha256",
    "attempts",
    "checked_at",
]


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows, fields):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def write_frozen_csv(path, rows, fields):
    path = Path(path)
    if path.exists():
        comparable = [{key: str(row[key]) for key in fields} for row in rows]
        if read_csv(path) != comparable:
            raise ValueError(f"Frozen data differ: {path.name}; use a new named wave")
        return
    write_csv(path, rows, fields)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def normalize_doi(value):
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", value.strip().lower())


def unique(rows, fields):
    keys = [tuple(row[field] for field in fields) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError(f"Duplicate key: {fields}")


def openalex_api_key():
    """Load credentials from the environment or the user's private config."""
    key = os.environ.get("OPENALEX_API_KEY", "").strip()
    if key:
        return key
    config = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    path = config / "openalex" / "api_key"
    if not path.is_file():
        return None
    return path.read_text().strip() or None


def request(url, path, json_response=True):
    """Cache successful responses; never print or persist authentication tokens."""
    path = Path(path)
    if path.exists():
        payload = path.read_bytes()
        return json.loads(payload) if json_response else payload
    headers = {"User-Agent": "sig-fault-citation-pilot/1.0"}
    key = openalex_api_key()
    if key and urllib.parse.urlparse(url).hostname == "api.openalex.org":
        headers["Authorization"] = f"Bearer {key}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers=headers), timeout=30
            ) as response:
                payload = response.read()
            parsed = json.loads(payload) if json_response else payload
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            manifest = {
                "url": url,
                "retrieved_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "sha256": sha256(payload),
                "bytes": len(payload),
            }
            path.with_suffix(path.suffix + ".source.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
            return parsed
        except urllib.error.HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 3:
                raise
            time.sleep(min(2 ** (attempt + 1), 8))
        except (TimeoutError, urllib.error.URLError):
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("Request attempts exhausted")


def api_url(endpoint, **params):
    return "https://api.openalex.org/" + endpoint + "?" + urllib.parse.urlencode(params)


def oa_urls(work):
    urls = []
    for location in [work.get("best_oa_location")] + work.get("locations", []):
        if not location or not location.get("is_oa"):
            continue
        for field in ("pdf_url", "landing_page_url"):
            url = location.get(field)
            if url and url not in urls:
                urls.append(url)
    return urls


def work_pmcid(work):
    candidates = list((work.get("ids") or {}).values()) + oa_urls(work)
    for candidate in candidates:
        match = re.search(r"\bPMC\d+\b", str(candidate), re.I)
        if match:
            return match.group().upper()
    return ""


def normalize_edges(paper, target, works):
    if normalize_doi(target.get("doi") or "") != paper["doi"]:
        raise ValueError(f"Target DOI mismatch: {paper['paper_id']}")
    result, ids, dois = [], set(), {}
    for work in sorted(works, key=lambda x: x["id"]):
        if work["id"] in ids:
            raise ValueError(f"Repeated work across API pages: {work['id']}")
        ids.add(work["id"])
        if target["id"] not in work.get("referenced_works", []):
            raise ValueError(
                f"Incoming citation not present in references: {work['id']}"
            )
        date = work.get("publication_date") or ""
        dt.date.fromisoformat(date)
        if date > CUTOFF:
            raise ValueError("API cutoff violation")
        doi = normalize_doi(work.get("doi") or "")
        duplicate = dois.get(doi, "") if doi else ""
        if doi and not duplicate:
            dois[doi] = work["id"]
        result.append(
            {
                "paper_id": paper["paper_id"],
                "target_work_id": target["id"],
                "citing_work_id": work["id"],
                "doi": doi,
                "title": work.get("title") or "",
                "publication_date": date,
                "publication_year": work["publication_year"],
                "type": work["type"],
                "reference_verified": "yes",
                "oa_urls": json.dumps(oa_urls(work)),
                "pmcid": work_pmcid(work),
                "before_original_date": (
                    "yes" if date < paper["publication_date"] else "no"
                ),
                "duplicate_of": duplicate,
                "eligible_type": "yes" if work["type"] in ALLOWED_TYPES else "no",
            }
        )
    return result


def fetch():
    papers = read_csv(DATA / "identities.csv")
    unique(papers, ["paper_id"])
    edges, coverage = [], []
    fields = (
        "id,doi,title,publication_date,publication_year,type,referenced_works,"
        "ids,locations,best_oa_location"
    )
    for paper in papers:
        pid = paper["paper_id"]
        target = request(
            "https://api.openalex.org/works/https://doi.org/" + paper["doi"],
            CACHE / "openalex" / f"{pid}.json",
        )
        cursor, works, seen_cursors, pages, totals = "*", [], set(), 0, []
        while cursor:
            if cursor in seen_cursors:
                raise ValueError("Repeated pagination cursor")
            seen_cursors.add(cursor)
            pages += 1
            url = api_url(
                "works",
                filter=(
                    f"cites:{target['id'].split('/')[-1]},"
                    f"to_publication_date:{CUTOFF}"
                ),
                per_page=100,
                cursor=cursor,
                select=fields,
                sort="publication_date",
            )
            batch = request(url, CACHE / "citations" / pid / f"{pages:04d}.json")
            totals.append(batch["meta"]["count"])
            works.extend(batch["results"])
            cursor = batch["meta"].get("next_cursor")
            if not batch["results"]:
                break
            print(f"{pid}: {len(works)}/{totals[0]} citation records", flush=True)
        if len(set(totals)) != 1 or len(works) != totals[0]:
            raise ValueError(f"Incomplete or changing citation frame: {pid}")
        edges.extend(normalize_edges(paper, target, works))
        coverage.append(
            {"paper_id": pid, "api_count": totals[0], "pages": pages, "complete": "yes"}
        )
    unique(edges, ["paper_id", "citing_work_id"])
    write_frozen_csv(DATA / "citation_edges.csv", edges, EDGE_FIELDS)
    write_frozen_csv(
        DATA / "coverage.csv", coverage, ["paper_id", "api_count", "pages", "complete"]
    )
    print(f"Saved {len(edges)} citation relationships across {len(papers)} papers")


def period_for(date, event):
    if date < event["possible_warning_from"]:
        return "pre"
    anniversary = dt.date.fromisoformat(event["public_record_by"])
    anniversary = anniversary.replace(year=anniversary.year + 1)
    if date >= anniversary.isoformat():
        return "post"
    return "transition"


def draw_sample(edges, registry, audits):
    selected = {row["paper_id"]: row for row in registry if row["selected"] == "TRUE"}
    events = {row["audit_id"]: row for row in audits}
    unique(edges, ["paper_id", "citing_work_id"])
    samples = []
    edge_lookup = {(row["paper_id"], row["citing_work_id"]): row for row in edges}
    for row in edges:
        if not row["duplicate_of"] or row["paper_id"] not in selected:
            continue
        canonical = edge_lookup[(row["paper_id"], row["duplicate_of"])]
        event = events[selected[row["paper_id"]]["audit_id"]]
        if period_for(row["publication_date"], event) != period_for(
            canonical["publication_date"], event
        ):
            raise ValueError(
                "Duplicate DOI has conflicting sampling periods; resolve identity first"
            )
    for pid, paper in sorted(selected.items()):
        event = events[paper["audit_id"]]
        for period, maximum in (("pre", 5), ("post", 10)):
            pool = [
                row
                for row in edges
                if row["paper_id"] == pid
                and not row["duplicate_of"]
                and row["before_original_date"] == "no"
                and row["eligible_type"] == "yes"
                and row["citing_work_id"] != row["target_work_id"]
                and row["publication_date"] <= CUTOFF
                and period_for(row["publication_date"], event) == period
            ]
            pool.sort(
                key=lambda row: sha256(
                    f"{SEED}|{pid}|{period}|{row['citing_work_id']}".encode()
                )
            )
            n = min(maximum, len(pool))
            for rank, row in enumerate(pool[:n], 1):
                pair_id = pid + "__" + row["citing_work_id"].split("/")[-1]
                samples.append(
                    dict(
                        row,
                        pair_id=pair_id,
                        period=period,
                        stratum_size=len(pool),
                        stratum_sample_size=n,
                        conditional_inclusion_probability=n / len(pool),
                        sample_rank=rank,
                    )
                )
    unique(samples, ["pair_id"])
    return samples


def sample():
    coverage = read_csv(DATA / "coverage.csv")
    selected = {
        row["paper_id"]
        for row in read_csv(DATA / "registry.csv")
        if row["selected"] == "TRUE"
    }
    if {row["paper_id"] for row in coverage if row["complete"] == "yes"} != selected:
        raise ValueError(
            "All selected papers need complete citation frames before sampling"
        )
    rows = draw_sample(
        read_csv(DATA / "citation_edges.csv"),
        read_csv(DATA / "registry.csv"),
        read_csv(DATA / "audits.csv"),
    )
    destination = DATA / "sample.csv"
    if destination.exists():
        old = read_csv(destination)
        if [(r["pair_id"], r["period"]) for r in old] != [
            (r["pair_id"], r["period"]) for r in rows
        ]:
            raise ValueError(
                "Frozen sample differs; create a new named wave instead of overwriting"
            )
    write_frozen_csv(destination, rows, SAMPLE_FIELDS)
    templates = []
    for row in rows:
        for reader in ("reader_1", "reader_2"):
            templates.append(
                dict.fromkeys(RATING_FIELDS, "")
                | {
                    "pair_id": row["pair_id"],
                    "reader_id": reader,
                }
            )
    write_frozen_csv(DATA / "coding_template.csv", templates, RATING_FIELDS)
    print(
        f"Frozen sample: {len(rows)} pairs; "
        f"blank independent-reader forms: {len(templates)}"
    )


def article_xml(payload):
    root = ET.fromstring(payload)
    if root.tag == "pmc-articleset":
        articles = root.findall("article")
        if len(articles) != 1:
            raise ValueError("Expected exactly one full-text article")
        root = articles[0]
    if root.tag != "article" or root.find("body") is None:
        raise ValueError("Not a complete JATS article")
    return root


def xml_text(payload):
    root = article_xml(payload)
    title = (
        " ".join(root.find("front").itertext())
        if root.find("front") is not None
        else ""
    )
    blocks = [title]
    for node in root.iter():
        if node.tag in {"p", "caption", "ref"}:
            blocks.append(" ".join("".join(node.itertext()).split()))
    return "\n\n".join(blocks)


def verify_xml_doi(payload, doi):
    root = article_xml(payload)
    identifiers = [
        normalize_doi(node.text or "")
        for node in root.findall("./front/article-meta/article-id")
        if node.attrib.get("pub-id-type") == "doi"
    ]
    if not doi or doi not in identifiers:
        raise ValueError("Full-text identity cannot be confirmed by article DOI")


def citation_passages(payload, target_doi):
    root = article_xml(payload)
    reference_ids = set()
    for ref in root.findall(".//ref"):
        dois = [
            normalize_doi(node.text or "")
            for node in ref.findall(".//pub-id")
            if node.attrib.get("pub-id-type") == "doi"
        ]
        for node in ref.findall(".//ext-link"):
            url = node.attrib.get("{http://www.w3.org/1999/xlink}href", "")
            if "doi.org/" in url:
                dois.append(normalize_doi(url))
        if target_doi in dois and ref.attrib.get("id"):
            reference_ids.add(ref.attrib["id"])
    passages = []
    for paragraph in root.iter("p"):
        if any(
            set(xref.attrib.get("rid", "").split()) & reference_ids
            for xref in paragraph.iter("xref")
        ):
            text = " ".join("".join(paragraph.itertext()).split())
            passages.append(
                {"paragraph_id": paragraph.attrib.get("id", ""), "text": text}
            )
    return sorted(reference_ids), passages


def contexts():
    papers = {row["paper_id"]: row for row in read_csv(DATA / "identities.csv")}
    retrieval = {row["pair_id"]: row for row in read_csv(DATA / "retrieval.csv")}
    index = []
    directory = CACHE / "contexts"
    directory.mkdir(parents=True, exist_ok=True)
    for row in read_csv(DATA / "sample.csv"):
        result = {
            "pair_id": row["pair_id"],
            "status": "no_verified_xml",
            "passages": "",
            "local_path": "",
        }
        record = retrieval.get(row["pair_id"], {})
        if record.get("status") == "retrieved_xml":
            payload = (ROOT / record["local_path"]).read_bytes()
            refs, passages = citation_passages(payload, papers[row["paper_id"]]["doi"])
            path = directory / (row["pair_id"] + ".txt")
            heading = (
                "Automatically located citation passages. "
                "Read the full paper for qualifications.\n\n"
            )
            path.write_text(
                heading + "\n\n".join(p["text"] for p in passages), encoding="utf-8"
            )
            result.update(
                status=(
                    "passages_located"
                    if passages
                    else "reference_only" if refs else "doi_reference_not_located"
                ),
                passages=len(passages),
                local_path=str(path.relative_to(ROOT)),
            )
        index.append(result)
    write_csv(
        DATA / "context_index.csv",
        index,
        ["pair_id", "status", "passages", "local_path"],
    )
    print(
        f"Located passages for {sum(r['status'] == 'passages_located' for r in index)} "
        "pairs; no outcome codes assigned"
    )


def resolve_pmcid(row):
    if row["pmcid"]:
        return row["pmcid"]
    for url in json.loads(row["oa_urls"]):
        match = re.search(r"/pmc/articles/(?:PMC)?(\d+)", url, re.I)
        if match:
            return "PMC" + match.group(1)
    if not row["doi"]:
        return ""
    url = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
        + urllib.parse.urlencode(
            {
                "query": 'DOI:"' + row["doi"] + '"',
                "format": "json",
                "pageSize": 10,
            }
        )
    )
    results = request(url, CACHE / "epmc" / (sha256(row["doi"].encode()) + ".json"))
    matches = [
        r
        for r in results["resultList"]["result"]
        if normalize_doi(r.get("doi", "")) == row["doi"] and r.get("pmcid")
    ]
    return matches[0]["pmcid"] if matches else ""


def retrieve_one(row):
    result = dict.fromkeys(RETRIEVAL_FIELDS, "")
    result.update(
        pair_id=row["pair_id"],
        status="unavailable",
        checked_at=dt.date.today().isoformat(),
    )
    attempts = []
    try:
        pmcid = resolve_pmcid(row)
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        pmcid = ""
        attempts.append(f"Europe PMC lookup: {type(error).__name__}")
    if pmcid:
        endpoints = [
            (
                "pmc",
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
                + urllib.parse.urlencode(
                    {"db": "pmc", "id": pmcid.removeprefix("PMC"), "retmode": "xml"}
                ),
            ),
            (
                "epmc",
                f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML",
            ),
        ]
        for provider, url in endpoints:
            path = CACHE / "fulltext" / (pmcid + "_" + provider + ".xml")
            try:
                payload = request(url, path, json_response=False)
                verify_xml_doi(payload, row["doi"])
                text = xml_text(payload)
                path.with_suffix(".txt").write_text(text, encoding="utf-8")
                result.update(
                    status="retrieved_xml",
                    url=url,
                    local_path=str(path.relative_to(ROOT)),
                    sha256=sha256(payload),
                    attempts=json.dumps(attempts),
                )
                return result
            except (
                urllib.error.URLError,
                TimeoutError,
                ValueError,
                ET.ParseError,
            ) as error:
                attempts.append(f"{url}: {type(error).__name__}")
    urls = json.loads(row["oa_urls"])
    for url in urls:
        # Download PDF endpoints; retain landing pages in the reviewer packet.
        if not re.search(r"(\.pdf(?:[?#]|$)|/pdf(?:[/?#]|$))", url, re.I):
            continue
        path = CACHE / "fulltext" / (sha256(url.encode()) + ".pdf")
        try:
            payload = request(url, path, json_response=False)
            if not payload.startswith(b"%PDF-"):
                attempts.append(f"{url}: response is not PDF")
                continue
            result.update(
                status="downloaded_pdf_unchecked",
                url=url,
                local_path=str(path.relative_to(ROOT)),
                sha256=sha256(payload),
                attempts=json.dumps(attempts),
            )
            return result
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            attempts.append(f"{url}: {type(error).__name__}")
    result["attempts"] = json.dumps(attempts)
    return result


class PdfMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name", "").lower() == "citation_pdf_url":
            self.links.append(attrs.get("content", ""))
        if tag == "link" and attrs.get("type") == "application/pdf":
            self.links.append(attrs.get("href", ""))


def landing_fulltext(row, old):
    """Follow advertised OA landing pages and their standard PDF metadata."""
    attempts = json.loads(old["attempts"])
    for url in json.loads(row["oa_urls"]):
        path = CACHE / "landing" / (sha256(url.encode()) + ".bin")
        try:
            payload = request(url, path, json_response=False)
            if payload.startswith(b"%PDF-"):
                candidates = [(url, payload)]
            else:
                parser = PdfMetadata()
                parser.feed(payload.decode("utf-8", errors="replace"))
                candidates = []
                for link in parser.links:
                    pdf_url = urllib.parse.urljoin(url, link)
                    pdf_path = CACHE / "fulltext" / (sha256(pdf_url.encode()) + ".pdf")
                    try:
                        candidates.append(
                            (pdf_url, request(pdf_url, pdf_path, json_response=False))
                        )
                    except (urllib.error.URLError, TimeoutError, ValueError):
                        attempts.append(f"{pdf_url}: PDF metadata link failed")
            for pdf_url, data in candidates:
                if data.startswith(b"%PDF-"):
                    pdf_path = CACHE / "fulltext" / (sha256(pdf_url.encode()) + ".pdf")
                    pdf_path.parent.mkdir(parents=True, exist_ok=True)
                    pdf_path.write_bytes(data)
                    return dict(
                        old,
                        status="downloaded_pdf_unchecked",
                        url=pdf_url,
                        local_path=str(pdf_path.relative_to(ROOT)),
                        sha256=sha256(data),
                        attempts=json.dumps(attempts),
                        checked_at=dt.date.today().isoformat(),
                    )
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            attempts.append(f"{url}: landing page {type(error).__name__}")
    return dict(
        old, attempts=json.dumps(attempts), checked_at=dt.date.today().isoformat()
    )


def fulltext(limit=None, landing=False):
    rows = read_csv(DATA / "sample.csv")
    path = DATA / "retrieval.csv"
    previous = {row["pair_id"]: row for row in read_csv(path)} if path.exists() else {}
    new = 0
    for row in rows:
        old = previous.get(row["pair_id"])
        if old and (not landing or old["status"] != "unavailable"):
            continue
        if limit is not None and new >= limit:
            break
        previous[row["pair_id"]] = (
            landing_fulltext(row, old) if landing and old else retrieve_one(row)
        )
        new += 1
        write_csv(path, list(previous.values()), RETRIEVAL_FIELDS)
        print(row["pair_id"], previous[row["pair_id"]]["status"], flush=True)


def validate_ratings(rows, sample_ids):
    unique(rows, ["pair_id", "reader_id"])
    valid = {"", "yes", "no", "unclear"}
    roles = {
        "hypothesis",
        "design",
        "effect_size",
        "meta_analysis",
        "substantive_evidence",
        "unaffected_finding",
        "method_background",
        "critical_discussion",
        "unclear",
    }
    for row in rows:
        if row["pair_id"] not in sample_ids or not row["reader_id"]:
            raise ValueError("Unknown pair or missing reader")
        for field in (
            "valid_link",
            "fulltext_read",
            "claim_identified",
            "relies_on_claim",
            "qualification",
        ):
            if row[field] not in valid:
                raise ValueError(f"Invalid {field}")
        if row["relies_on_claim"] in {"yes", "no"}:
            if any(
                row[f] != "yes"
                for f in ("valid_link", "fulltext_read", "claim_identified")
            ):
                raise ValueError(
                    "A reliance judgment requires verified link, full text, "
                    "and identified claim"
                )
            if not row["evidence_locator"] or not row["evidence_excerpt"]:
                raise ValueError("A reliance judgment requires passage evidence")
        if row["qualification"] in {"yes", "no"}:
            if row["fulltext_read"] != "yes":
                raise ValueError("A qualification judgment requires full-text review")
            if not row["evidence_locator"] or not row["evidence_excerpt"]:
                raise ValueError("A qualification judgment requires passage evidence")
        if row["use_role"] and not set(row["use_role"].split(";")) <= roles:
            raise ValueError("Unknown use role")


def validate():
    registry = read_csv(DATA / "registry.csv")
    identities = read_csv(DATA / "identities.csv")
    unique(registry, ["claim_id"])
    unique(identities, ["paper_id"])
    selected = {r["paper_id"] for r in registry if r["selected"] == "TRUE"}
    if selected != {r["paper_id"] for r in identities} or len(selected) != 20:
        raise ValueError("Selected-paper identity join is not 1:1")
    for source in read_csv(DATA / "source_manifest.csv"):
        if sha256((ROOT / source["path"]).read_bytes()) != source["sha256"]:
            raise ValueError(f"Source checksum mismatch: {source['path']}")
    claims = read_csv(DATA / "claims.csv")
    unique(claims, ["claim_id"])
    if {r["paper_id"] for r in claims} != selected:
        raise ValueError("Claim records do not cover the selected papers")
    allowed = {
        "",
        "verified_inferential_error",
        "assumption_sensitive",
        "not_sustained",
        "unresolved",
    }
    for row in claims:
        if row["final_claim_status"] not in allowed:
            raise ValueError("Unknown final claim status")
        if row["final_claim_status"] and (
            not row["independent_reader_1"]
            or not row["independent_reader_2"]
            or row["independent_reader_1"] == row["independent_reader_2"]
        ):
            raise ValueError(
                "Final claim status requires two distinct independent readers"
            )
    if (DATA / "sample.csv").exists():
        rows = read_csv(DATA / "sample.csv")
        unique(rows, ["pair_id"])
        expected = draw_sample(
            read_csv(DATA / "citation_edges.csv"),
            registry,
            read_csv(DATA / "audits.csv"),
        )
        if rows != [{k: str(v) for k, v in r.items()} for r in expected]:
            raise ValueError("Stored sample differs from deterministic draw")
        for file in ("coding_template.csv", "ratings.csv"):
            if (DATA / file).exists():
                validate_ratings(read_csv(DATA / file), {r["pair_id"] for r in rows})
    print("Pilot joins, sample, and any completed ratings validated")


def agreement(ratings):
    """Describe paired judgments without treating missingness as disagreement."""
    by_pair = {}
    for row in ratings:
        by_pair.setdefault(row["pair_id"], []).append(row)
    out = {}
    for field in ("relies_on_claim", "qualification"):
        pairs = [
            values
            for values in by_pair.values()
            if len(values) == 2 and all(value[field] for value in values)
        ]
        cells = {}
        for a, b in pairs:
            key = a[field] + "/" + b[field]
            cells[key] = cells.get(key, 0) + 1
        out[field] = {
            "paired_completed": len(pairs),
            "confusion": cells,
            "exact_agreement": (
                sum(a[field] == b[field] for a, b in pairs) / len(pairs)
                if pairs
                else None
            ),
        }
        binary_pairs = [
            (a[field], b[field])
            for a, b in pairs
            if a[field] in {"yes", "no"} and b[field] in {"yes", "no"}
        ]
        discordant = sum(a != b for a, b in binary_pairs)
        for label in ("yes", "no"):
            concordant = sum(a == label and b == label for a, b in binary_pairs)
            denominator = 2 * concordant + discordant
            out[field][label + "_agreement"] = (
                2 * concordant / denominator if denominator else None
            )
    return out


def report():
    papers = {r["paper_id"]: r for r in read_csv(DATA / "identities.csv")}
    rows = read_csv(DATA / "sample.csv") if (DATA / "sample.csv").exists() else []
    retrieval = (
        read_csv(DATA / "retrieval.csv") if (DATA / "retrieval.csv").exists() else []
    )
    status = {r["pair_id"]: r for r in retrieval}
    context_path = DATA / "context_index.csv"
    context_index = (
        {r["pair_id"]: r for r in read_csv(context_path)}
        if context_path.exists()
        else {}
    )
    ratings = read_csv(DATA / "ratings.csv") if (DATA / "ratings.csv").exists() else []
    validate_ratings(ratings, {r["pair_id"] for r in rows})
    counts = {
        s: sum(r["status"] == s for r in retrieval)
        for s in ("retrieved_xml", "downloaded_pdf_unchecked", "unavailable")
    }
    summary = {
        "status": "awaiting_independent_claim_verification_and_citation_coding",
        "selected_papers": len(papers),
        "sampled_pairs": len(rows),
        "pre_pairs": sum(r["period"] == "pre" for r in rows),
        "post_pairs": sum(r["period"] == "post" for r in rows),
        "retrieval_attempted": len(retrieval),
        "retrieval_status": counts,
        "rating_rows": len(ratings),
        "initial_agreement": agreement(ratings),
        "continued_reliance_estimate": None,
        "seed": SEED,
        "citation_cutoff": CUTOFF,
    }
    (DATA / "status.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    availability = []
    for audit in ("iv", "nw"):
        for period in ("pre", "post"):
            subset = [
                r
                for r in rows
                if r["paper_id"].startswith(audit + "_") and r["period"] == period
            ]
            states = [
                status.get(r["pair_id"], {}).get("status", "not_attempted")
                for r in subset
            ]
            availability.append(
                {
                    "audit": audit,
                    "period": period,
                    "sampled": len(subset),
                    "xml_doi_checked": states.count("retrieved_xml"),
                    "pdf_unchecked": states.count("downloaded_pdf_unchecked"),
                    "not_retrieved": states.count("unavailable"),
                    "not_attempted": states.count("not_attempted"),
                }
            )
    write_csv(DATA / "availability.csv", availability, list(availability[0]))
    edges = read_csv(DATA / "citation_edges.csv")
    edge_lookup = {(r["paper_id"], r["citing_work_id"]): r for r in edges}
    duplicate_dates = []
    for row in edges:
        if row["duplicate_of"]:
            canonical = edge_lookup[(row["paper_id"], row["duplicate_of"])]
            if row["publication_date"] != canonical["publication_date"]:
                duplicate_dates.append(
                    {
                        "paper_id": row["paper_id"],
                        "doi": row["doi"],
                        "canonical_work_id": row["duplicate_of"],
                        "canonical_date": canonical["publication_date"],
                        "duplicate_work_id": row["citing_work_id"],
                        "duplicate_date": row["publication_date"],
                        "decision": (
                            "count_once_same_period_version_date_review_pending"
                        ),
                    }
                )
    write_csv(
        DATA / "duplicate_date_checks.csv",
        duplicate_dates,
        [
            "paper_id",
            "doi",
            "canonical_work_id",
            "canonical_date",
            "duplicate_work_id",
            "duplicate_date",
            "decision",
        ],
    )
    acquired = counts["retrieved_xml"] + counts["downloaded_pdf_unchecked"]
    findings = [
        "# Pilot feasibility results",
        "",
        f"The pilot selected {len(papers)} original papers and sampled {len(rows)} "
        f"citation relationships: {summary['pre_pairs']} pre-warning and "
        f"{summary['post_pairs']} post-warning. Independent claim verification and "
        "citation coding are pending; there is no estimate of continued reliance.",
        "",
        f"Automated retrieval obtained files for {acquired}/{len(rows)} "
        "relationships "
        f"({acquired / len(rows):.1%}). Of these, {counts['retrieved_xml']} have "
        "an XML article body and a matching article DOI; "
        f"{counts['downloaded_pdf_unchecked']} are PDFs awaiting identity "
        "and readability "
        "checks. File acquisition is an upper bound on verified readable coverage. "
        + (
            "The 80% availability criterion is not met by the present retrieval."
            if acquired < 0.8 * len(rows)
            else (
                "The 80% availability criterion still requires "
                "manual readability checks."
            )
        ),
        "",
        "| Audit | Period | Sampled | DOI-checked XML | "
        "Unchecked PDF | Not retrieved |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in availability:
        findings.append(
            f"| {row['audit']} | {row['period']} | {row['sampled']} | "
            f"{row['xml_doi_checked']} | {row['pdf_unchecked']} | "
            f"{row['not_retrieved'] + row['not_attempted']} |"
        )
    findings += [
        "",
        "Next steps are targeted full-text acquisition and two independent readers. "
        "Keep the sample fixed; do not replace inaccessible papers. "
        "[Two first-pass examples](examples.md) illustrate the distinction between "
        "reliance on a challenged comparison and use of another contribution. "
        "The [protocol](README.md) records the IV replication findings and the "
        "remaining claim-verification work.",
    ]
    (ROOT / "docs/pilot/findings.md").write_text("\n".join(findings) + "\n")
    chunks = [
        "<!doctype html><html lang='en'><meta charset='utf-8'>",
        "<title>Citation-reliance pilot: reader packet</title>",
        "<style>body{font:17px/1.5 system-ui;max-width:1000px;"
        "margin:40px auto;padding:20px}"
        "article{border-top:1px solid #ccc;padding:20px 0}a{color:#174b87}"
        "code{font-size:14px}h1,h2{line-height:1.2}</style>",
        "<h1>Citation-reliance pilot</h1><p>Independent coding is pending. "
        "Downloaded files are not evidence of reliance. Read all relevant passages, "
        "including qualifications elsewhere in each paper.</p>",
        "<p>Record judgments in a copy of <code>data/pilot/coding_template.csv</code>. "
        "See <a href='codebook.md'>the coding protocol</a>. "
        "Full texts are cached locally; "
        "they are not redistributed with this packet.</p>",
    ]
    claims = {r["paper_id"]: r for r in read_csv(DATA / "claims.csv")}
    for pid, claim in claims.items():
        chunks.append(
            f"<article id='{html.escape(pid)}'>"
            f"<h2>Claim record: {html.escape(pid)}</h2>"
        )
        for field in (
            "claim_paraphrase",
            "original_locator",
            "source_assessment",
            "qualification",
            "verification_status",
        ):
            chunks.append(
                f"<p><strong>{html.escape(field.replace('_', ' '))}:</strong> "
                f"{html.escape(claim[field])}</p>"
            )
        chunks.append("</article>")
    for row in rows:
        original = papers[row["paper_id"]]
        chunks.append(f"<article><h2>{html.escape(row['pair_id'])}</h2>")
        chunks.append(f"<a href='#{html.escape(row['paper_id'])}'>Claim record</a>")
        chunks.append(
            f"<p>Original: <a href='https://doi.org/{html.escape(original['doi'])}'>"
            f"{html.escape(original['title'])}</a></p>"
        )
        chunks.append(
            f"<p>Citing paper: {html.escape(row['title'])} "
            f"({html.escape(row['publication_date'])})</p>"
        )
        record = status.get(row["pair_id"], {})
        chunks.append(
            f"<p>Retrieval: {html.escape(record.get('status', 'not_attempted'))}</p>"
        )
        urls = (["https://doi.org/" + row["doi"]] if row["doi"] else []) + json.loads(
            row["oa_urls"]
        )
        for i, url in enumerate(dict.fromkeys(urls), 1):
            chunks.append(
                f"<a href='{html.escape(url, quote=True)}'>Source {i}</a> &nbsp; "
            )
        if record.get("local_path"):
            chunks.append(
                f"<a href='../../{html.escape(record['local_path'], quote=True)}'>"
                "Local full text</a>"
            )
        context = context_index.get(row["pair_id"], {})
        if context.get("local_path"):
            chunks.append(
                " &nbsp; <a "
                f"href='../../{html.escape(context['local_path'], quote=True)}'>"
                "Located citation passages</a>"
            )
        chunks.append("</article>")
    chunks.append("</html>")
    (ROOT / "docs/pilot/reader-packet.html").write_text(
        "\n".join(chunks), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "fetch",
            "sample",
            "fulltext",
            "landing",
            "contexts",
            "validate",
            "report",
        ],
    )
    parser.add_argument(
        "--limit", type=int, help="Maximum new full-text retrieval attempts"
    )
    args = parser.parse_args()
    if args.command in {"fulltext", "landing"}:
        fulltext(args.limit, landing=args.command == "landing")
    else:
        globals()[args.command]()


if __name__ == "__main__":
    main()
