"""Build the complete, identified Lazic et al. pseudoreplication audit cohort."""

import argparse
import collections
import datetime as dt
import hashlib
import json
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import i4r_sources as sources
import pilot

DATA = pilot.ROOT / "data/lazic"
META_FIELDS = [
    "pmid",
    "doi",
    "title",
    "journal",
    "publication_date",
    "electronic_date",
    "issue_date",
    "publication_year",
    "issue_year",
    "pmc_id",
    "publication_types",
    "source_path",
    "source_sha256",
]
CLASSIFICATIONS = {"n": "pseudoreplication", "y": "correct_analysis", "u": "unclear"}


def verify_sources():
    for source in json.loads((DATA / "sources.json").read_text()):
        if source["path"].startswith("data/"):
            payload = (pilot.ROOT / source["path"]).read_bytes()
            if hashlib.sha256(payload).hexdigest() != source["sha256"]:
                raise ValueError("Source checksum mismatch: " + source["path"])


def survey():
    verify_sources()
    rows = pilot.read_csv(DATA / "raw/data.csv")
    pilot.unique(rows, ["PMID"])
    for row in rows:
        if not row["PMID"].isdigit() or row["Correct_analyis"] not in CLASSIFICATIONS:
            raise ValueError("Invalid source PMID or analysis classification")
        for field in ["Randomisation", "Blinding", "N_litters", "Split_unit"]:
            if row[field] not in {"y", "n"}:
                raise ValueError("Unexpected source code: " + field)
        if row["N_offspring"] not in {"y", "n", "mixed"}:
            raise ValueError("Unexpected offspring-count code")
    return rows


def publication_date(node):
    if node is None:
        return ""
    year = node.findtext("Year", "")
    if not year:
        match = re.search(r"\b(19|20)\d{2}\b", node.findtext("MedlineDate", ""))
        return match.group() if match else ""
    month = node.findtext("Month", "")
    day = node.findtext("Day", "")
    if not month:
        return year
    if not month.isdigit():
        try:
            month = str(dt.datetime.strptime(month[:3], "%b").month)
        except ValueError:
            return year
    value = f"{int(year):04d}-{int(month):02d}"
    if day:
        value += f"-{int(day):02d}"
    dt.date.fromisoformat(value + ("-01" if not day else ""))
    return value


def parse_pubmed(payload, source_path, source_sha256):
    result, notices = [], []
    for node in ET.fromstring(payload).findall("PubmedArticle"):
        pmid = node.findtext("MedlineCitation/PMID", "")
        article = node.find("MedlineCitation/Article")
        if article is None or not pmid:
            raise ValueError("Incomplete PubMed identity")
        ids = collections.defaultdict(set)
        for x in node.findall("PubmedData/ArticleIdList/ArticleId"):
            ids[x.get("IdType")].add(x.text or "")
        if len(ids["doi"]) > 1:
            raise ValueError("Conflicting PubMed DOIs")
        issue = publication_date(article.find("Journal/JournalIssue/PubDate"))
        electronic = [
            publication_date(x)
            for x in article.findall("ArticleDate")
            if x.get("DateType") == "Electronic"
        ]
        electronic = min((x for x in electronic if x), default="")
        date = electronic or issue
        if not date:
            raise ValueError("Missing PubMed publication date")
        title = article.find("ArticleTitle")
        result.append(
            dict(
                pmid=pmid,
                doi=pilot.normalize_doi(next(iter(ids["doi"]), "")),
                title="".join(title.itertext()) if title is not None else "",
                journal=article.findtext("Journal/Title", ""),
                publication_date=date,
                electronic_date=electronic,
                issue_date=issue,
                publication_year=date[:4],
                issue_year=issue[:4],
                pmc_id=";".join(sorted(ids["pmc"])),
                publication_types=";".join(
                    x.text or ""
                    for x in article.findall("PublicationTypeList/PublicationType")
                ),
                source_path=source_path,
                source_sha256=source_sha256,
            )
        )
        for x in node.findall(
            "MedlineCitation/CommentsCorrectionsList/CommentsCorrections"
        ):
            notices.append(
                dict(
                    pmid=pmid,
                    relation=x.get("RefType", ""),
                    related_pmid=x.findtext("PMID", ""),
                    citation=x.findtext("RefSource", ""),
                    note=x.findtext("Note", ""),
                    source_path=source_path,
                )
            )
    pilot.unique(result, ["pmid"])
    return result, notices


def fetch_metadata(cache):
    ids = [r["PMID"] for r in survey()]
    records, notices, manifest = [], [], []
    for offset in range(0, len(ids), 100):
        end = offset + 100
        subset = ids[offset:end]
        url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
            + urllib.parse.urlencode(
                dict(db="pubmed", id=",".join(subset), retmode="xml")
            )
        )
        path = cache / f"lazic_pubmed_{offset // 100 + 1}.xml"
        payload = sources.fetch(url, path, False)
        origin = json.loads(path.with_suffix(".xml.source.json").read_text())
        name = "private-data/lazic/" + path.name
        rows, links = parse_pubmed(payload, name, hashlib.sha256(payload).hexdigest())
        if {r["pmid"] for r in rows} != set(subset):
            raise ValueError("PubMed response does not cover requested identifiers")
        records.extend(rows)
        notices.extend(links)
        manifest.append(dict(path=name, **origin))
        time.sleep(0.4)
    pilot.write_csv(DATA / "metadata.csv", records, META_FIELDS)
    pilot.write_csv(
        DATA / "notice_links.csv",
        notices,
        ["pmid", "relation", "related_pmid", "citation", "note", "source_path"],
    )
    (DATA / "metadata_sources.json").write_text(json.dumps(manifest, indent=2) + "\n")


def build_rows(raw, metadata):
    pilot.unique(raw, ["PMID"])
    pilot.unique(metadata, ["pmid"])
    by_id = {r["pmid"]: r for r in metadata}
    if set(by_id) != {r["PMID"] for r in raw}:
        raise ValueError("Metadata must cover the complete source cohort")
    rows = []
    for r in raw:
        m = by_id[r["PMID"]]
        category = CLASSIFICATIONS[r["Correct_analyis"]]
        rows.append(
            dict(
                article_id="lazic_" + r["PMID"],
                **m,
                source_correct_analysis=r["Correct_analyis"],
                classification=category,
                flagged={"n": "1", "y": "0", "u": ""}[r["Correct_analyis"]],
                randomisation=r["Randomisation"],
                blinding=r["Blinding"],
                litter_count_reported=r["N_litters"],
                offspring_count_reported=r["N_offspring"],
                split_unit=r["Split_unit"],
                audit_year=2017,
                full_baseline_year="yes" if int(m["publication_year"]) < 2016 else "no",
                two_full_preyears="yes" if int(m["publication_year"]) < 2015 else "no",
            )
        )
    dois = [r["doi"] for r in rows if r["doi"]]
    if len(dois) != len(set(dois)):
        raise ValueError(
            "Multiple source PMIDs resolve to one DOI; review before deduplication"
        )
    return rows


def build():
    rows = build_rows(survey(), pilot.read_csv(DATA / "metadata.csv"))
    pilot.write_csv(DATA / "articles.csv", rows, list(rows[0]))
    counts = collections.Counter(r["classification"] for r in rows)
    statuses = dict(
        source_papers=len(rows),
        classification_counts=dict(counts),
        verified_pubmed_identities=len(rows),
        with_doi=sum(bool(r["doi"]) for r in rows),
        audit_year=2017,
        primary_comparison_papers=sum(r["flagged"] != "" for r in rows),
        classified_full_baseline=sum(
            r["flagged"] != "" and r["full_baseline_year"] == "yes" for r in rows
        ),
        citation_histories=0,
        estimation_status="pending_citation_collection_and_notice_review",
        classification_scope=(
            "Published audit assessments, not independent reanalyses "
            "or demonstrated corrected effect sizes"
        ),
    )
    (DATA / "status.json").write_text(json.dumps(statuses, indent=2) + "\n")
    fields = [
        "source_correct_analysis",
        "flagged",
        "publication_year",
        "issue_year",
        "randomisation",
        "blinding",
        "litter_count_reported",
        "offspring_count_reported",
        "split_unit",
        "full_baseline_year",
        "two_full_preyears",
    ]
    profile = {
        category: {
            field: dict(
                collections.Counter(
                    r[field] for r in rows if r["classification"] == category
                )
            )
            for field in fields
        }
        for category in CLASSIFICATIONS.values()
    }
    (DATA / "profile.json").write_text(json.dumps(profile, indent=2) + "\n")
    print(json.dumps(statuses))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "fetch-metadata"])
    parser.add_argument(
        "--cache-dir", type=Path, default=pilot.ROOT / "private-data/lazic"
    )
    args = parser.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    fetch_metadata(args.cache_dir) if args.command == "fetch-metadata" else build()
