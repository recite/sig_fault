"""Check paired citation links against the OpenCitations Index."""

import argparse
import collections
import csv
import http.client
import io
import json
import re
import time

import i4r_sources as acquisition
import nieuwenhuis as nw
import pilot

DATA = nw.DATA
CACHE = nw.CACHE / "validation"
BASE = "https://api.opencitations.net/index/v2/"
EDGE_FIELDS = ["paper_id", "oci", "citing", "cited", "creation", "timespan"]
COVERAGE_FIELDS = [
    "paper_id",
    "doi",
    "records",
    "reported_count",
    "undated_records",
    "complete",
    "detail",
]


def identifiers(value, prefix):
    return {t.removeprefix(prefix) for t in value.split() if t.startswith(prefix)}


def validate_response(rows, count, doi, scheme="doi"):
    if scheme not in {"doi", "pmid"}:
        raise ValueError("Unsupported target identifier scheme")
    if not isinstance(rows, list) or len(rows) != count:
        raise ValueError("Citation-list length differs from reported count")
    pilot.unique(rows, ["oci"])
    for row in rows:
        cited = identifiers(row["cited"], scheme + ":")
        if scheme == "doi":
            cited = {pilot.normalize_doi(d) for d in cited}
        if doi not in cited:
            raise ValueError(
                f"Citation target {scheme.upper()} differs from queried original"
            )
        if not identifiers(row["citing"], "omid:"):
            raise ValueError("Citing work lacks OpenCitations identity")
        if row["creation"] and not re.fullmatch(r"\d{4}(-\d{2}){0,2}", row["creation"]):
            raise ValueError("Unexpected citation date representation")


def fetch_links(pid, doi, cache=None, scheme="doi"):
    if scheme not in {"doi", "pmid"}:
        raise ValueError("Unsupported target identifier scheme")
    cache = CACHE if cache is None else cache
    url = BASE + "citations/" + scheme + ":" + doi
    csv_path = cache / (pid + "_opencitations.csv")
    if not csv_path.exists():
        try:
            return acquisition.fetch(url, cache / (pid + "_opencitations.json"))
        except http.client.IncompleteRead:
            time.sleep(0.4)
    payload = acquisition.fetch(url + "?format=csv", csv_path, json_response=False)
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
    if not set(EDGE_FIELDS[1:]).issubset(reader.fieldnames or []):
        raise ValueError("OpenCitations CSV lacks required relationship fields")
    return list(reader)


def fetch(full_cohort=False):
    panel = pilot.read_csv(DATA / "paired_panel.csv")
    selected = {
        r["paper_id"] for r in panel if full_cohort or r["status"] == "complete"
    }
    identities = {r["paper_id"]: r for r in pilot.read_csv(DATA / "identities.csv")}
    old_coverage = {r["paper_id"]: r for r in nw.read("validation_coverage.csv")}
    old_edges = nw.read("validation_edges.csv")
    edges = [r for r in old_edges if r["paper_id"] not in selected]
    coverage = [r for pid, r in old_coverage.items() if pid not in selected]
    for pid in sorted(selected):
        doi = identities[pid]["doi"]
        previous = old_coverage.get(pid, {})
        if previous.get("complete") == "yes" and previous.get("doi") == doi:
            coverage.append(previous)
            edges.extend(r for r in old_edges if r["paper_id"] == pid)
            continue
        status = dict(
            paper_id=pid,
            doi=doi,
            records="",
            reported_count="",
            undated_records="",
            complete="no",
            detail="",
        )
        try:
            rows = fetch_links(pid, doi)
            time.sleep(0.4)
            total = acquisition.fetch(
                BASE + "citation-count/doi:" + doi,
                CACHE / (pid + "_opencitations_count.json"),
            )
            count = int(total[0]["count"])
            validate_response(rows, count, doi)
            edges.extend(
                {k: row[k] for k in EDGE_FIELDS if k != "paper_id"} | {"paper_id": pid}
                for row in rows
            )
            status.update(
                records=len(rows),
                reported_count=count,
                undated_records=sum(not r["creation"] for r in rows),
                complete="yes",
            )
        except Exception as exc:
            status["detail"] = str(exc)[:200]
        coverage.append(status)
        print(pid, status["complete"], status["records"], status["detail"], flush=True)
        checkpoint(edges, coverage, old_edges, old_coverage)
        if "429" in status["detail"] or "rate limit" in status["detail"]:
            break
        time.sleep(0.4)
    checkpoint(edges, coverage, old_edges, old_coverage)


def checkpoint(edges, coverage, old_edges, old_coverage):
    visited = {r["paper_id"] for r in coverage}
    pilot.write_csv(
        DATA / "validation_edges.csv",
        edges + [r for r in old_edges if r["paper_id"] not in visited],
        EDGE_FIELDS,
    )
    pilot.write_csv(
        DATA / "validation_coverage.csv",
        coverage + [r for pid, r in old_coverage.items() if pid not in visited],
        COVERAGE_FIELDS,
    )
    sources = {r["path"]: r for r in nw.read("validation_sources.csv")}
    for path in sorted(CACHE.glob("*.source.json")):
        name = str(path.relative_to(pilot.ROOT)).removesuffix(".source.json")
        sources[name] = dict(path=name, **json.loads(path.read_text()))
    pilot.write_csv(
        DATA / "validation_sources.csv",
        [sources[k] for k in sorted(sources)],
        ["path", "url", "retrieved_at", "sha256", "bytes"],
    )


def crosswalk(overlap, edges, coverage):
    completed = {r["paper_id"] for r in coverage if r["complete"] == "yes"}
    lookup = collections.defaultdict(list)
    for row in edges:
        for doi in identifiers(row["citing"], "doi:"):
            lookup[row["paper_id"], pilot.normalize_doi(doi)].append(row)
    result = []
    for row in overlap:
        matches = lookup[row["paper_id"], row["doi"]]
        result.append(
            row
            | dict(
                validation_status=(
                    "not_collected"
                    if row["paper_id"] not in completed
                    else "present" if matches else "not_found"
                ),
                opencitations_oci=";".join(sorted({r["oci"] for r in matches})),
                opencitations_dates=";".join(
                    sorted({r["creation"] for r in matches if r["creation"]})
                ),
                matching_records=len(matches),
            )
        )
    return result


def build():
    overlap = pilot.read_csv(DATA / "reconciled_overlap.csv")
    edges = pilot.read_csv(DATA / "validation_edges.csv")
    coverage = pilot.read_csv(DATA / "validation_coverage.csv")
    pilot.unique(edges, ["paper_id", "oci"])
    pilot.unique(coverage, ["paper_id"])
    pilot.unique(overlap, ["paper_id", "doi"])
    if {r["paper_id"] for r in edges} - {r["paper_id"] for r in coverage}:
        raise ValueError("Citation edge lacks a collection-status record")
    identities = {r["paper_id"]: r for r in pilot.read_csv(DATA / "identities.csv")}
    for record in coverage:
        if record["doi"] != identities[record["paper_id"]]["doi"]:
            raise ValueError("Validation history belongs to another original")
        if record["complete"] == "yes":
            selected = [r for r in edges if r["paper_id"] == record["paper_id"]]
            validate_response(selected, int(record["reported_count"]), record["doi"])
            if len(selected) != int(record["records"]):
                raise ValueError("Exported coverage and edge counts disagree")
            if sum(not r["creation"] for r in selected) != int(
                record["undated_records"]
            ):
                raise ValueError("Undated-record count disagrees with exported edges")
    checked = crosswalk(overlap, edges, coverage)
    pilot.write_csv(DATA / "link_validation.csv", checked, list(checked[0]))
    counts = collections.Counter(
        (r["presence"], r["validation_status"]) for r in checked
    )
    rows = [
        dict(presence=p, validation_status=s, links=n)
        for (p, s), n in sorted(counts.items())
    ]
    pilot.write_csv(DATA / "validation_summary.csv", rows, list(rows[0]))
    report(checked, coverage)
    print(json.dumps(rows, indent=2))


def report(checked, coverage):
    observed = [r for r in checked if r["validation_status"] != "not_collected"]
    primary_extra = [
        r
        for r in observed
        if r["presence"] == "openalex_only"
        and r["openalex_type"] in {"article", "review"}
        and r["openalex_before_original_date"] == "no"
    ]
    all_extra = [r for r in observed if r["presence"] == "openalex_only"]
    macros = {
        "NwValidationPapers": len({r["paper_id"] for r in observed}),
        "NwExtraPrimary": len(primary_extra),
        "NwExtraPrimaryCorroborated": sum(
            r["validation_status"] == "present" for r in primary_extra
        ),
        "NwExtraAll": len(all_extra),
        "NwExtraCorroborated": sum(
            r["validation_status"] == "present" for r in all_extra
        ),
    }
    (pilot.ROOT / "tabs/nieuwenhuis_validation_macros.tex").write_text(
        "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in macros.items())
    )
    lines = [
        "# Checking citation links against OpenCitations",
        "",
        f"OpenCitations also records {macros['NwExtraPrimaryCorroborated']} of "
        f"the {macros['NwExtraPrimary']} OpenAlex-only links eligible for our "
        "primary article/review count. Across all document types in the "
        f"comparison frame, it records {macros['NwExtraCorroborated']} of "
        f"{macros['NwExtraAll']} OpenAlex-only links.",
        "",
        "The frame consists of DOI-bearing relationships dated 2009–2015 in "
        "at least one of the two original sources, after documented DOI "
        "transcription repairs. This is the same selected, flagged-only "
        "paired sample used in the source comparison; it cannot estimate "
        "coverage for comparison papers or the full cohort.",
        "Headline fractions include only targets with complete OpenCitations "
        "retrieval. The table also identifies any links whose target's "
        "third-source retrieval is incomplete.",
        "",
        "| Original sources | Links | Also in OpenCitations | Not found | "
        "Collection incomplete |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    labels = {
        "both": "Both",
        "openalex_only": "OpenAlex only",
        "wos_only": "Web of Science only",
    }
    for group, label in labels.items():
        subset = [r for r in checked if r["presence"] == group]
        counts = collections.Counter(r["validation_status"] for r in subset)
        lines.append(
            f"| {label} | {len(subset)} | {counts['present']} | "
            f"{counts['not_found']} | {counts['not_collected']} |"
        )
    observed_papers = {r["paper_id"] for r in observed}
    undated = sum(
        int(r["undated_records"])
        for r in coverage
        if r["complete"] == "yes" and r["paper_id"] in observed_papers
    )
    lines += [
        "",
        "OpenCitations and OpenAlex can share upstream records. Agreement "
        "corroborates a recorded link but does not independently verify the "
        "citing bibliography, establish a common publication year, or show "
        "that the citation endorses the affected claim. A link not found "
        "in this index is not thereby false. These records do not replace "
        "either database's annual citation counts.",
        "",
        f"The responses for these paired pilot papers include {undated} undated "
        "relationships across all years. They remain in the link data with "
        "empty dates. Every accepted response matches the separate count "
        "endpoint, has unique citation identifiers, and identifies the "
        "queried target DOI in every record. Completeness refers to the API "
        "response, not all citations that exist in the literature.",
        "",
        "The separate [full-cohort source comparison](opencitations.md) "
        "collects both flagged and comparison papers from the historical frame.",
        "",
        "## Reproduce",
        "",
        "```sh",
        "make nieuwenhuis-validation",
        "```",
        "",
        "This offline target rebuilds the crosswalk, summary, report and "
        "manuscript macros from frozen public inputs. To collect links for "
        "the complete paired-paper sample, run "
        "`python3 scripts/nieuwenhuis_validation.py fetch`. Successful "
        "responses retain source URLs, retrieval dates and SHA-256 hashes.",
        "",
        "See the [record-level crosswalk](../../data/nieuwenhuis/link_validation.csv), "
        "[retrieval status](../../data/nieuwenhuis/validation_coverage.csv), "
        "[source manifest](../../data/nieuwenhuis/validation_sources.csv), and "
        "[OpenCitations API documentation](https://api.opencitations.net/index/v2).",
    ]
    (pilot.ROOT / "docs/nieuwenhuis/validation.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["fetch", "build"])
    parser.add_argument("--full-cohort", action="store_true")
    args = parser.parse_args()
    if args.command == "fetch":
        fetch(full_cohort=args.full_cohort)
    else:
        build()
