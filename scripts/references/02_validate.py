"""Validate cited BibTeX records against frozen publisher metadata."""

import codecs
import html
import json
import re
import unicodedata

import latexcodec  # noqa: F401
from pybtex.database import parse_file

from scripts.research_pipeline import ROOT, Run, write_csv, write_json


def normalize(value):
    value = codecs.decode(str(value), "ulatex")
    value = html.unescape(re.sub(r"<[^>]+>", "", value))
    value = unicodedata.normalize("NFKD", value)
    return "".join(x.lower() for x in value if x.isalnum())


def fields_match(entry, work):
    fields = entry.fields
    year = work.get("published-print", work["published"])["date-parts"][0][0]
    expected = dict(
        doi=work["DOI"],
        title=work["title"][0],
        journal=work["container-title"][0],
        year=str(year),
        volume=work.get("volume", ""),
        number=work.get("issue", ""),
        pages=work.get("page", work.get("article-number", "")),
    )
    checks = {
        name: normalize(fields.get(name, "")) == normalize(value)
        for name, value in expected.items()
    }
    authors = [
        normalize(
            " ".join(
                p.first_names
                + p.middle_names
                + p.prelast_names
                + p.last_names
                + p.lineage_names
            )
        )
        for p in entry.persons.get("author", [])
    ]
    recorded = [
        normalize(x.get("name") or (x.get("given", "") + " " + x.get("family", "")))
        for x in work.get("author", [])
    ]
    checks["authors_in_order"] = authors == recorded
    return checks


def citation_keys(text):
    text = re.sub(r"(?<!\\)%[^\n]*", "", text)
    groups = re.findall(r"\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}", text)
    return {key.strip() for group in groups for key in group.split(",")}


def main():
    with Run(
        "references", "02_validate", __file__, True, data_dir=ROOT / "data/references"
    ) as run:
        bib = parse_file(run.input(ROOT / "ms/references.bib"))
        metadata = json.loads(run.input(run.data / "crossref.json").read_text())
        text = run.input(ROOT / "ms/main.tex").read_text()
        run.input(ROOT / "requirements-i4r.txt")
        keys = citation_keys(text)
        run.check(
            "all_citations_resolve",
            keys <= set(bib.entries),
            sorted(keys - set(bib.entries)),
        )
        run.check(
            "no_unused_references",
            set(bib.entries) <= keys,
            sorted(set(bib.entries) - keys),
        )
        run.check(
            "all_metadata_present", set(bib.entries) == set(metadata), len(metadata)
        )
        dois = [normalize(e.fields.get("doi", "")) for e in bib.entries.values()]
        run.check(
            "distinct_nonempty_dois",
            all(dois) and len(dois) == len(set(dois)),
            len(dois),
        )
        rows = []
        for key, entry in bib.entries.items():
            checks = fields_match(entry, metadata[key])
            rows.append(dict(key=key, source_doi=entry.fields["doi"], **checks))
        path = run.data / "validation.csv"
        write_csv(path, rows, list(rows[0]))
        run.output(path)
        failures = {
            row["key"]: [k for k, v in row.items() if isinstance(v, bool) and not v]
            for row in rows
        }
        failures = {k: v for k, v in failures.items() if v}
        run.check("publisher_metadata_agrees", not failures, failures)
        status = dict(
            references=len(rows),
            cited_keys=len(keys),
            validated=True,
            year_rule="Print year when supplied; otherwise publication year",
            semantic_review="docs/literature-and-target.md",
        )
        path = run.data / "status.json"
        write_json(path, status)
        run.output(path)
        run.record["metrics"] = status
        print(json.dumps(status))


if __name__ == "__main__":
    main()
