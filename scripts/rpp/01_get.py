"""Verify the original cohort files and acquire publisher bibliographic records."""

import argparse
import json
import xml.etree.ElementTree as ET

from scripts.research_pipeline import (
    ROOT,
    Run,
    digest,
    query,
    unique,
    write_csv,
    write_json,
)

JOURNALS = {"PS": "0956-7976", "JPSP": "0022-3514", "JEPLMC": "0278-7393"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    with Run("rpp", "01_get", __file__, args.offline) as run:
        manifest = json.loads(
            run.input(ROOT / "private-data/cohorts/manifest.json").read_text()
        )
        source = next(x for x in manifest if x["cohort"] == "rpp")
        path = run.input(ROOT / source["local_path"])
        run.check("original_checksum", digest(path) == source["sha256"], source["file"])
        for name in [
            "papers.csv",
            "assessments.csv",
            "paper_crosswalk.csv",
            "source_records/rpp.csv",
        ]:
            run.input(ROOT / "data/cohorts/rpp" / name)
        records = {}
        for journal, issn in JOURNALS.items():
            cursor, seen, works, totals = "*", set(), [], set()
            while cursor:
                run.check("distinct_cursor", cursor not in seen, journal)
                seen.add(cursor)
                url = query(
                    f"https://api.crossref.org/journals/{issn}/works",
                    filter=(
                        "from-pub-date:2007-01-01,until-pub-date:2009-12-31,"
                        "type:journal-article"
                    ),
                    rows=1000,
                    cursor=cursor,
                    select=(
                        "DOI,title,container-title,volume,issue,page,published-print,"
                        "published,ISSN,author,type,relation"
                    ),
                )
                message = run.fetch(url, "crossref")["message"]
                works.extend(message["items"])
                totals.add(message["total-results"])
                if not message["items"] or len(works) >= message["total-results"]:
                    break
                cursor = message.get("next-cursor")
            unique(works, ["DOI"])
            run.check(
                "complete_journal",
                len(totals) == 1 and len(works) == next(iter(totals)),
                dict(journal=journal, records=len(works), reported=sorted(totals)),
            )
            records[journal] = works
            print(journal, len(works), flush=True)
        path = run.data / "publisher_records.json"
        write_json(path, records)
        run.output(path)
        term = (
            "(0956-7976[ISSN] OR 0022-3514[ISSN] OR 0278-7393[ISSN]) AND "
            "2008[dp] AND (Review[pt] OR Comment[pt] OR Editorial[pt])"
        )
        search = run.fetch(
            query(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                db="pubmed",
                term=term,
                retmode="json",
                retmax=200,
            ),
            "pubmed",
        )["esearchresult"]
        run.check(
            "complete_publication_type_search",
            len(search["idlist"]) == int(search["count"]),
            search["count"],
        )
        ids = sorted(set(search["idlist"]) | {"18605863"})
        xml = run.fetch(
            query(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                db="pubmed",
                id=",".join(ids),
                retmode="xml",
            ),
            "pubmed",
            False,
        )
        types = []
        for record in ET.fromstring(xml).findall("PubmedArticle"):
            doi = record.findtext(".//ArticleId[@IdType='doi']", default="").lower()
            types.append(
                dict(
                    pmid=record.findtext(".//PMID"),
                    doi=doi,
                    title="".join(record.find(".//ArticleTitle").itertext()),
                    publication_types=";".join(
                        x.text for x in record.findall(".//PublicationType")
                    ),
                )
            )
        run.check(
            "complete_publication_type_records",
            {x["pmid"] for x in types} == set(ids),
            len(types),
        )
        path = run.data / "publication_types.csv"
        write_csv(path, types, ["pmid", "doi", "title", "publication_types"])
        run.output(path)
        run.record["metrics"] = {k: len(v) for k, v in records.items()}


if __name__ == "__main__":
    main()
