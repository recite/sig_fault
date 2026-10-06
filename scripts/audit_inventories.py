"""Freeze complete external assessment inventories; do not infer error exposures."""

import argparse
import collections
import csv
import datetime
import gzip
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/inventories"
ARCHIVE_URL = (
    "https://zenodo.org/api/records/59818/files/"
    "2016statcheck_data-v1.0.0.zip/content"
)
ARCHIVE_SHA256 = "798b6f14d3e37b19bfa1db3c5164a2ee0845cfa96152176e0061a2b192d2adc6"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def doi(value):
    value = (value or "").strip().lower()
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value)
    return value if re.fullmatch(r"10\.\d{4,9}/\S+", value) else ""


def present(value):
    return "" if value is None or value in ("", "NA") else str(value)


def write_csv(name, rows):
    if not rows:
        raise ValueError(f"Empty inventory: {name}")
    with (DATA / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_source(name):
    manifest = json.loads((DATA / "sources.json").read_text())
    record = next(r for r in manifest if r["source"] == name)
    raw = (DATA / record["path"]).read_bytes()
    if digest(raw) != record["sha256"]:
        raise ValueError(f"Source checksum mismatch: {name}")
    result = gzip.decompress(raw) if record["path"].endswith(".gz") else raw
    if digest(result) != record["uncompressed_sha256"]:
        raise ValueError(f"Uncompressed checksum mismatch: {name}")
    return result


def import_statcheck(path):
    """Reconstruct the unavailable LFS object from all archived result members."""
    raw = path.read_bytes()
    if digest(raw) != ARCHIVE_SHA256:
        raise ValueError("Unexpected statcheck archive version")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        prefix = "chartgerink-2016statcheck_data-c2dac72/"
        members = sorted(
            n
            for n in archive.namelist()
            if n.startswith(prefix + "statcheck/") and n.endswith(".csv")
        )
        if len(members) != 50845:
            raise ValueError("Incomplete statcheck result-member inventory")
        data = archive.read(prefix + "df_names_statcheck")
        data += b"".join(archive.read(n) for n in members)
        pointer = archive.read(prefix + "statcheck_dataset.csv").decode()
        expected = re.search(r"sha256:([0-9a-f]+)", pointer).group(1)
        expected_size = int(re.search(r"size (\d+)", pointer).group(1))
        if len(data) != expected_size:
            raise ValueError("Reconstruction differs from upstream LFS size")
        for name in ["README.md", "LICENSE", "report_gen.R", "statcheck_version"]:
            (DATA / "sources" / ("statcheck_" + name + ".gz")).write_bytes(
                gzip.compress(archive.read(prefix + name), mtime=0)
            )
    target = DATA / "sources/statcheck.csv.gz"
    target.write_bytes(gzip.compress(data, mtime=0))
    manifest = json.loads((DATA / "sources.json").read_text())
    manifest = [r for r in manifest if r["source"] != "statcheck"]
    manifest.append(
        dict(
            source="statcheck",
            path="sources/statcheck.csv.gz",
            url=ARCHIVE_URL,
            archive_sha256=ARCHIVE_SHA256,
            archive_members=len(members),
            archive_transform="df_names_statcheck + sorted statcheck/*.csv",
            upstream_lfs_sha256=expected,
            upstream_lfs_byte_match=digest(data) == expected,
            reconstruction_note=(
                "All 50,845 archived member files concatenated in lexical order. "
                "Size and published row/paper counts agree; combined-file hash differs "
                "from the unavailable LFS object. "
                "Original concatenation order is unknown."
            ),
            retrieved_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            sha256=digest(target.read_bytes()),
            uncompressed_sha256=digest(data),
            original_bytes=len(data),
            license="CC0 1.0",
            attribution="Chris H. J. Hartgerink (2016), doi:10.5281/zenodo.59818",
        )
    )
    (DATA / "sources.json").write_text(json.dumps(manifest, indent=2) + "\n")


def flora_records(raw):
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if not rows or "doi_o" not in rows[0]:
        raise ValueError("FLoRA schema or encoding mismatch")
    result = []
    for i, row in enumerate(rows, 1):
        result.append(
            dict(
                record_id=f"flora_{i:05d}",
                source_row=i,
                original_doi=doi(row["doi_o"]),
                report_doi=doi(row["doi_r"]),
                original_identifier=present(row["doi_o"]),
                report_identifier=present(row["doi_r"]),
                original_alternative_ids=present(row["alt_identifier_o"]),
                report_alternative_ids=present(row["alt_identifier_r"]),
                original_title=present(row["title_o"]),
                report_title=present(row["title_r"]),
                original_year=present(row["year_o"]),
                report_year=present(row["year_r"]),
                assessment_type=row["type"],
                source_outcome=present(row["outcome"]),
                source_collection=row["source"],
                evidence_quote=present(row["outcome_quote"]),
                evidence_location=present(row["outcome_quote_source"]),
                material_error_status="not_adjudicated",
                first_public_disclosure="",
                citation_analysis_eligible="not_assessed",
            )
        )
    return result


def statcheck_articles(raw):
    grouped = {}
    tests = 0
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        tests += 1
        key = doi(row["Source"])
        if not key:
            raise ValueError("Unresolved statcheck original identity")
        if key not in grouped:
            grouped[key] = dict(
                original_doi=key,
                original_title=row["title"],
                original_year=present(row["year"]),
                journal=row["journal"],
                tests=0,
                inconsistent_tests=0,
                decision_inconsistent_tests=0,
                missing_error_labels=0,
                missing_decision_labels=0,
                metadata_conflict="no",
                material_error_status="not_adjudicated",
                first_public_disclosure="",
                citation_analysis_eligible="not_assessed",
            )
        paper = grouped[key]
        if (paper["original_title"], paper["original_year"], paper["journal"]) != (
            row["title"],
            present(row["year"]),
            row["journal"],
        ):
            paper["metadata_conflict"] = "yes"
        paper["tests"] += 1
        for label, count, missing in [
            ("Error", "inconsistent_tests", "missing_error_labels"),
            ("DecisionError", "decision_inconsistent_tests", "missing_decision_labels"),
        ]:
            if row[label] not in ("TRUE", "FALSE", "NA"):
                raise ValueError(f"Unknown statcheck label {row[label]}")
            paper[count] += row[label] == "TRUE"
            paper[missing] += row[label] == "NA"
    return [grouped[k] for k in sorted(grouped)], tests


def crosswalk(inventories, i4r_dois):
    papers = collections.defaultdict(collections.Counter)
    for source, rows in inventories.items():
        for row in rows:
            key = row["original_doi"]
            if key:
                papers[key][source] += 1
    return [
        dict(
            original_doi=key,
            flora_rows=counts["flora"],
            fred_effects=counts["fred"],
            statcheck_article_rows=counts["statcheck"],
            in_i4r_registry="yes" if key in i4r_dois else "no",
        )
        for key, counts in sorted(papers.items())
    ]


def report(counts):
    rows = []
    for key, label, unit in [
        ("flora", "FLoRA", "Original–assessment reference pair as supplied"),
        ("fred", "FReD", "Effect nested within original and replication papers"),
        ("statcheck", "Statcheck 2016", "Extracted statistical result"),
    ]:
        n = counts["statcheck_tests"] if key == "statcheck" else counts[key]["records"]
        rows.append(f"| {label} | {n:,} | {counts[key]['original_dois']:,} | {unit} |")
    table_rows = "\n".join(rows)
    text = f"""# Larger assessment inventories

The four matched I4R papers remain a pilot. The next expansion starts from complete
external inventories, before selecting papers with verified consequential errors.
No citation outcomes were used to choose or classify these new records.

| Frozen source | Records retained | Distinct syntactically valid original DOIs | Unit |
| --- | ---: | ---: | --- |
{table_rows}

These are full snapshots of the named sources, not a census of scientific errors.
The source files, permanent version URLs, retrieval times and checksums are in
[`data/inventories/sources.json`](../data/inventories/sources.json).
The combined inventory contains {counts['combined_original_dois']:,} distinct valid
original DOI strings. Syntactic validity does not establish a correct bibliographic
match; aliases and publication versions still require review.

## First priority: same-data reproduction reports

FLoRA contains {counts['reproduction_records']:,} reproduction records covering
{counts['reproduction_original_dois']:,} valid original DOIs. Of these,
{counts['challenged_reproduction_records']:,} records concerning
{counts['challenged_reproduction_original_dois']:,} original DOIs describe computational
issues or robustness challenges. Among those originals,
{counts['challenged_reproduction_dois_absent_i4r']:,} do not occur in the current I4R
DOI registry. This is a larger and more relevant starting pool than repeatedly
changing the specification on four papers.

The [review queue](../data/inventories/reproduction_review_queue.csv) retains **all**
reproduction records, including favorable and technical-failure assessments.
Computational issues receive first review, followed by robustness challenges.
The outcome label alone cannot establish material error: minor rounding differences
can receive an adverse label, while a reproducible computation can contain a
consequential coding mistake. Record the actual mistake, affected claim, numerical
consequence, source passage, author response and earliest public disclosure.

## Second priority: the large statistical-reporting audit

The archived statcheck release supplies all {counts['statcheck']['original_dois']:,}
per-paper result files. Together they contain {counts['statcheck_tests']:,} tests,
matching the published inventory. At least one statistical inconsistency is flagged
in {counts['statcheck_papers_with_any_inconsistency']:,} papers;
{counts['statcheck_papers_with_decision_inconsistency']:,} have a flag that could change
statistical significance. These are automated flags, not verified consequential
errors. The [paper inventory](../data/inventories/statcheck_inventory.csv) retains
unflagged papers and counts of unresolved labels as well as flagged papers.

Before effect estimation, establish which reports were actually posted publicly,
their dates and their contents. The archive's report-generation script states a
scan date; that is not evidence of public posting. Public reports also existed for
papers without flagged inconsistencies, so flagged-versus-unflagged comparisons
would concern the content of the assessment, not publicity versus no publicity.
Inspect source text for extraction errors, one-sided tests, multiplicity corrections
and whether a flagged result supports a substantive claim.

## Replication evidence remains a separate question

FReD and FLoRA also identify failed and successful replications. A failed replication
can reflect sampling variation, a failed manipulation or different study conditions;
it does not by itself establish a mistake in the original paper. These records can
support a later study of the effect of publicizing unsuccessful replications, with
its own estimand. They do not enter the verified-error analysis automatically.

## Build and checks

Run `make inventories` to rebuild the inventories and this report offline, and
`make inventories-test` for the parser and identity checks. All source rows survive.
There are {counts['repeated_complete_assessment_keys']} repeated fully specified FLoRA
original/report/type keys, retained in a
[review ledger](../data/inventories/repeated_assessment_keys.csv).
An umbrella report can contain separate attempts, and one repeated key has conflicting
outcomes. No automatic deduplication or majority vote resolves those cases.

The [dictionary and construction notes](inventory-methods.md) define fields, joins,
missing values, attribution and the remaining eligibility checks. The newly imported
records contribute **zero newly adjudicated material errors and zero new eligible
citation comparisons** at this stage. The existing citation estimates are unchanged.
"""
    (ROOT / "docs/inventories.md").write_text(text)


def build():
    flora = flora_records(read_source("flora"))
    payload = json.loads(read_source("fred"))
    fred = [
        dict(
            record_id=f"fred_{i:05d}",
            source_row=i,
            source_id=r["id"],
            original_doi=doi(r["doi_o"]),
            report_doi=doi(r["doi_r"]),
            original_reference=r["ref_o"],
            report_reference=r["ref_r"],
            effect_description=r["description"],
            source_outcomes=json.dumps(r["outcomes"], sort_keys=True),
            material_error_status="not_adjudicated",
            first_public_disclosure="",
            citation_analysis_eligible="not_assessed",
        )
        for i, r in enumerate(payload["studies"], 1)
    ]
    if len(fred) != payload["metadata"]["studyCount"]:
        raise ValueError("Incomplete FReD effect inventory")
    statcheck, ntests = statcheck_articles(read_source("statcheck"))
    if ntests != 688112 or len(statcheck) != 50845:
        raise ValueError("Statcheck counts differ from published inventory")
    with (ROOT / "data/i4r/articles.csv").open() as f:
        i4r_dois = {doi(r["doi"]) for r in csv.DictReader(f)} - {""}
    inventories = dict(flora=flora, fred=fred, statcheck=statcheck)
    for source, rows in inventories.items():
        write_csv(source + "_inventory.csv", rows)
    linked = crosswalk(inventories, i4r_dois)
    write_csv("article_crosswalk.csv", linked)
    queue = [r.copy() for r in flora if r["assessment_type"] == "reproduction"]
    for r in queue:
        label = r["source_outcome"]
        r["review_priority"] = (
            1
            if "computational issues" in label
            else 2 if "robustness challenges" in label else 3
        )
        r["in_i4r_registry"] = (
            "unknown"
            if not r["original_doi"]
            else "yes" if r["original_doi"] in i4r_dois else "no"
        )
    queue.sort(key=lambda r: (r["review_priority"], r["record_id"]))
    write_csv("reproduction_review_queue.csv", queue)
    duplicate_groups = collections.defaultdict(list)
    for r in flora:
        if r["original_doi"] and r["report_doi"]:
            duplicate_groups[
                (r["original_doi"], r["report_doi"], r["assessment_type"])
            ].append(r)
    duplicates = [
        dict(
            original_doi=k[0],
            report_doi=k[1],
            assessment_type=k[2],
            record_ids=";".join(r["record_id"] for r in rows),
            outcomes=";".join(sorted({r["source_outcome"] for r in rows})),
            outcome_conflict=(
                "yes" if len({r["source_outcome"] for r in rows}) > 1 else "no"
            ),
        )
        for k, rows in sorted(duplicate_groups.items())
        if len(rows) > 1
    ]
    write_csv("repeated_assessment_keys.csv", duplicates)
    counts = {
        source: dict(
            records=len(rows),
            original_dois=len({r["original_doi"] for r in rows} - {""}),
            rows_without_valid_original_doi=sum(not r["original_doi"] for r in rows),
        )
        for source, rows in inventories.items()
    }
    challenged = [r for r in queue if r["review_priority"] < 3]
    counts.update(
        statcheck_tests=ntests,
        statcheck_papers_with_any_inconsistency=sum(
            r["inconsistent_tests"] > 0 for r in statcheck
        ),
        statcheck_papers_with_decision_inconsistency=sum(
            r["decision_inconsistent_tests"] > 0 for r in statcheck
        ),
        reproduction_records=len(queue),
        reproduction_original_dois=len({r["original_doi"] for r in queue} - {""}),
        challenged_reproduction_records=len(challenged),
        challenged_reproduction_original_dois=len(
            {r["original_doi"] for r in challenged} - {""}
        ),
        challenged_reproduction_dois_absent_i4r=len(
            {r["original_doi"] for r in challenged} - i4r_dois - {""}
        ),
        repeated_complete_assessment_keys=len(duplicates),
        combined_original_dois=len(linked),
        imported_verified_material_errors=0,
        new_estimation_ready_disclosures=0,
    )
    (DATA / "status.json").write_text(json.dumps(counts, indent=2) + "\n")
    report(counts)
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "import-statcheck"])
    parser.add_argument("archive", nargs="?", type=Path)
    args = parser.parse_args()
    if args.command == "build":
        build()
    elif args.archive is None:
        parser.error("import-statcheck requires the archived ZIP path")
    else:
        import_statcheck(args.archive)
