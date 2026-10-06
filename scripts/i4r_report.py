"""Generate coverage and a browsable evidence catalog from the I4R registry."""

from __future__ import annotations

import collections
import csv
import html
import json

import i4r_match
import i4r_sources as s


def dictionary(folder):
    schema = json.loads((s.DATA / "schema.json").read_text())
    lines = [
        "# I4R data dictionary",
        "",
        schema["missing"],
        "",
        (
            "Generated from the declared schema and current CSV contents. "
            "Row units, sources and transformations are explained in "
            "[the construction contract](data-construction.md)."
        ),
        "",
    ]
    profile = {}
    for path in sorted(s.DATA.glob("*.csv")):
        table = schema["tables"][path.name]
        with path.open(newline="") as stream:
            reader = csv.DictReader(stream)
            names = reader.fieldnames
            rows = list(reader)
        key = table["key"]
        keys = [tuple(r[k] for k in key) for r in rows] if key else []
        duplicates = len(keys) - len(set(keys))
        if duplicates:
            raise ValueError(f"Duplicate declared key in {path.name}")
        lines += [
            f"## {path.name}",
            "",
            (
                f"One row: {table['unit']}. Rows: {len(rows)}. "
                f"Key: {', '.join(key) or 'no unique key declared'}. "
                f"Producer: `{table['producer']}`."
            ),
            "",
            "| Column | Type | Meaning | Missing | Observed range / values |",
            "| --- | --- | --- | ---: | --- |",
        ]
        stats = {}
        for name in names:
            field = schema["fields"][name]
            values = [r[name] for r in rows if r[name] not in {"", "NA"}]
            missing = len(rows) - len(values)
            observed = ""
            if values and field["type"] in {"integer", "number"}:
                numbers = [float(v) for v in values]
                if field["type"] == "integer" and any(v != int(v) for v in numbers):
                    raise ValueError(f"Noninteger {path.name}:{name}")
                observed = f"{min(numbers):g} to {max(numbers):g}"
            elif len(set(values)) <= 12 and max(map(len, values), default=0) < 80:
                observed = "; ".join(sorted(set(values)))
            else:
                observed = f"{len(set(values))} distinct nonmissing values"
            stats[name] = dict(
                type=field["type"],
                missing=missing,
                distinct_nonmissing=len(set(values)),
            )
            meaning = field["meaning"].replace("|", "\\|")
            observed = observed.replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| `{name}` | {field['type']} | {meaning} | {missing} | {observed} |"
            )
        lines.append("")
        profile[path.name] = dict(
            rows=len(rows), duplicate_keys=duplicates, key=key, columns=stats
        )
    (folder / "codebook.md").write_text("\n".join(lines))
    (folder / "profile.json").write_text(json.dumps(profile, indent=2) + "\n")


def assessment_completion(units, population_enumerated, scope=(), catalog_ids=()):
    eligible = [r for r in units if r["assessment_eligibility"] != "no"]
    resolved = sum(
        r["assessment_eligibility"] == "yes" and r["assessment_resolved"] == "yes"
        for r in eligible
    )
    fraction = resolved / len(eligible) if eligible else None
    sources_complete = (
        bool(catalog_ids)
        and len(scope) == len(set(catalog_ids))
        and {r["source_id"] for r in scope} == set(catalog_ids)
        and all(
            r["status"] in {"fully_enumerated", "non_assessment", "supporting_document"}
            for r in scope
        )
    )
    return (
        population_enumerated is True
        and sources_complete
        and all(r.get("unit_equivalence", "verified") == "verified" for r in units)
        and fraction is not None
        and fraction >= 0.9
    )


def report():
    sources = s.read("sources.csv")
    reviews = s.read("source_reviews.csv")
    articles = s.read("articles.csv")
    events = s.read("events.csv")
    documents = s.read("document_retrieval.csv")
    direct = i4r_match.eligible_events(events, articles, 2025, 1)
    primary = [
        r
        for r in events
        if r["error_verified"] == "yes"
        and r["material"] == "yes"
        and r["publicity_verified"] == "yes"
    ]
    units = s.read("source_units.csv")
    eligible_reviews = [r for r in units if r["assessment_eligibility"] == "yes"]
    unknown_units = sum(r["assessment_eligibility"] == "unresolved" for r in units)
    unresolved_eligibility = sum(
        r["assessment_eligibility"] not in {"yes", "no"} for r in reviews
    )
    resolved = sum(r["assessment_resolved"] == "yes" for r in eligible_reviews)
    coverage = resolved / len(eligible_reviews) if eligible_reviews else None
    denominator_bound = len(eligible_reviews) + unknown_units
    lower_bound = resolved / denominator_bound if denominator_bound else None
    scope = json.loads((s.DATA / "coverage_scope.json").read_text())
    enumerated = scope["assessment_population_enumerated"] is True
    assessment_scope = s.read("assessment_scope.csv")
    complete = assessment_completion(
        s.read("assessment_inventory.csv"),
        enumerated,
        assessment_scope,
        [r["source_id"] for r in sources],
    )
    counts = dict(
        catalog_entries=len(sources),
        discussion_papers=sum(r["collection"] == "discussion_papers" for r in sources),
        report_entries=sum(r["collection"] == "reports" for r in sources),
        retrieved_documents=sum(r["status"] == "retrieved" for r in documents),
        distinct_retrieved_urls=len(
            {
                r["url"]
                for r in s.read("documents.csv")
                if r["document_id"]
                in {d["document_id"] for d in documents if d["status"] == "retrieved"}
            }
        ),
        retrieved_source_metadata=sum(
            r["status"] == "retrieved" for r in s.read("retrieval.csv")
        ),
        article_candidates=len(articles),
        verified_article_identities=sum(
            r["identity_verified"] == "yes" for r in articles
        ),
        source_review_records=len(reviews),
        enumerated_assessment_units=len(s.read("assessment_inventory.csv")),
        unresolved_assessment_equivalences=sum(
            r["unit_equivalence"] == "unresolved"
            for r in s.read("assessment_inventory.csv")
        ),
        enumerated_assessment_articles=len(
            {r["article_id"] for r in s.read("assessment_inventory.csv")}
        ),
        catalog_sources_with_enumerated_scope=sum(
            r["status"] in {"fully_enumerated", "non_assessment", "supporting_document"}
            for r in assessment_scope
        ),
        inventoried_archives=sum(
            r["status"] == "inventoried" for r in s.read("archive_retrieval.csv")
        ),
        archive_files=len(s.read("archive_retrieval.csv")),
        archive_member_records=len(s.read("archive_members.csv")),
        repository_sources_checked=len(
            {r["source_id"] for r in s.read("repository_queries.csv")}
        ),
        candidate_controls=len(s.read("control_articles.csv")),
        controls_with_verified_publisher_dates=sum(
            bool(r["publication_date_source"] and r["publication_date"])
            for r in s.read("control_articles.csv")
        ),
        complete_citation_histories=sum(
            r["status"] == "complete" for r in s.read("citation_retrieval.csv")
        ),
        collected_citation_edges=len(s.read("citation_edges.csv")),
        curated_error_candidates=len(s.read("assessments.csv")),
        verified_dated_disclosures=len(primary),
        date_age_eligible_disclosures=len(direct[0]),
        matched_events=len({r["event_id"] for r in s.read("matches.csv")}),
        complete_panel_rows=len(s.read("analysis_panel.csv")),
        unresolved_assessment_eligibility=unresolved_eligibility,
        source_units=len(units),
        assessment_population_enumerated=enumerated,
        unresolved_unit_eligibility=unknown_units,
        verified_duplicate_listings=len(reviews) - len(units),
        eligible_assessments=len(eligible_reviews),
        resolved_assessments=resolved,
        source_resolution_fraction=coverage,
        source_resolution_unknown_inclusive_fraction=lower_bound,
        substantially_complete_assessment_coverage=complete,
    )
    folder = s.ROOT / "docs/i4r"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "coverage.json").write_text(json.dumps(counts, indent=2) + "\n")
    lines = [
        "# I4R coverage and analysis readiness",
        "",
        "The inventory covers both discovered catalogs. "
        + (
            "The 90% assessment-resolution gate is met."
            if complete
            else (
                "Assessment coverage remains incomplete; the 90% completion gate has"
                " not been met."
            )
        )
        + " Review dispositions include unresolved cases and limited screens, not just"
        " verified findings.",
        "",
        "| Stage | Count |",
        "| --- | ---: |",
    ]
    labels = {
        "catalog_entries": "Catalog entries",
        "discussion_papers": "Discussion papers",
        "report_entries": "Report listings",
        "retrieved_documents": (
            "Retrieved documents (including separate replies and repeated files)"
        ),
        "distinct_retrieved_urls": "Distinct retrieved document URLs",
        "retrieved_source_metadata": "Retrieved listing metadata records",
        "article_candidates": (
            "Candidate article identities (not a final distinct-paper count)"
        ),
        "verified_article_identities": "Publisher/OpenAlex-verified article identities",
        "source_review_records": "Source review/disposition records",
        "enumerated_assessment_units": "Assessment records explicitly enumerated",
        "unresolved_assessment_equivalences": (
            "Assessment records with unresolved reviewer-team equivalence"
        ),
        "enumerated_assessment_articles": "Articles in those enumerated assessments",
        "catalog_sources_with_enumerated_scope": (
            "Catalog entries with assessment scope accounted for"
        ),
        "inventoried_archives": "ZIP archives inventoried",
        "archive_files": "Root ZIP files listed",
        "archive_member_records": "Archive members, including code/data/plots",
        "repository_sources_checked": "OSF sources checked for components/providers",
        "candidate_controls": "Distinct candidate control articles",
        "controls_with_verified_publisher_dates": (
            "Controls with verified publisher dates"
        ),
        "complete_citation_histories": "Complete affected/control citation histories",
        "collected_citation_edges": "Deduplicated article–citing-work relationships",
        "source_units": "Source units after verified duplicate links",
        "verified_duplicate_listings": "Verified duplicate listings collapsed",
        "eligible_assessments": (
            "Source units containing article-specific assessments"
        ),
        "resolved_assessments": ("Source units with resolved target classification"),
        "unresolved_unit_eligibility": (
            "Units whose assessment eligibility remains unresolved"
        ),
        "curated_error_candidates": "Curated material-error candidate records",
        "verified_dated_disclosures": (
            "Source-verified material-error disclosures with verified public year"
        ),
        "date_age_eligible_disclosures": (
            "Disclosures satisfying the primary date/age window"
        ),
        "matched_events": "Events with selected controls",
        "complete_panel_rows": "Complete matched article-period observations",
    }
    for key, label in labels.items():
        lines.append(f"| {label} | {counts[key]} |")
    lines += [
        "",
        "The source-level resolution fraction among confirmed assessment listings is "
        + (f"{coverage:.1%}." if coverage is not None else "not yet defined.")
        + " Including unresolved-eligibility source units in the denominator gives "
        + (f"{lower_bound:.1%}." if lower_bound is not None else "no defined bound."),
        "",
        "These are source-listing progress measures, not coverage of all independent"
        " article assessments. Shared projects can contain several assessment teams or"
        " articles. The 90% gate remains blocked until those units are enumerated and"
        " reviewed. Explicitly enumerated assessments are not yet a census of the"
        " total assessment population. The source-by-source enumeration ledger is"
        " `data/i4r/assessment_scope.csv`. See"
        " `data/i4r/coverage_scope.json` for resolved and unresolved scope.",
        "",
        "## Current scope review",
        "",
        "This review asks how many assessments each source contains and which"
        " versions belong together. An unresolved source has been examined but"
        " still lacks sufficient evidence to close that question.",
        "",
        "| Status | Catalog entries |",
        "| --- | ---: |",
    ]
    for status, n in sorted(
        collections.Counter(r["status"] for r in assessment_scope).items()
    ):
        lines.append(f'| {status.replace("_", " ")} | {n} |')
    roster_links = s.read("aggregate_assessment_links.csv")
    if roster_links:
        matched = sum(r["link_status"] == "matched" for r in roster_links)
        lines += [
            "",
            f"The two economics/political-science overviews (DP107 and DP287)"
            f" describe the same {len(roster_links)} assessment entries. Explicit"
            f" report links and target identities connect {matched} entries to"
            f" existing assessments; {len(roster_links) - matched} remain unmatched."
            " These links add no assessments or verified errors. The two entries"
            " for the monetary-policy uncertainty paper refer to different teams"
            " and remain separate. See the [row-level crosswalk]"
            "(../../data/i4r/aggregate_assessment_links.csv). Both overview sources"
            " retain unresolved scope until the remaining entries are reconciled.",
        ]
    lines += [
        "",
        "## Initial screening depth",
        "",
        "| Status | Catalog entries |",
        "| --- | ---: |",
    ]
    for status, n in sorted(
        collections.Counter(r["review_status"] for r in reviews).items()
    ):
        lines.append(f'| {status.replace("_", " ")} | {n} |')
    lines += [
        "",
        "## What is and is not established",
        "",
        (
            f"The {len(sources)} entries are documents/listings, not distinct original"
            " articles. Reports, replies, aggregate rosters and repeated assessments"
            " overlap. The article table still contains unresolved identities; DOI"
            " aliases are merged only when supported."
        ),
        "",
        (
            "Source review means the recorded passages were read. It does not mean the"
            " original analysis was rerun. Full-text availability, screening, a"
            " material-error assessment and a verified disclosure date are separate"
            " fields."
        ),
        "",
        (
            "Anonymous OSF and OpenAlex access was rate-limited during acquisition. The"
            " cached sources are retained and retrieval resumes from checkpoints."
            " Crossref verifies source-supplied DOIs and unique exact-title matches."
            " Missing article"
            " metadata, citations or control pools are never filled with zeros."
        ),
        "",
        (
            "The aggregate economics/political-science package anonymizes article"
            " identities; it cannot supply the missing crosswalk. Its Appendix B roster"
            " identifies articles separately. The registry retains the 110 roster rows"
            " (109 distinct titles) rather than assuming 110 distinct papers. The"
            " psychology roster has 67 report rows and 64 distinct DOIs."
        ),
        "",
        (
            "The strict primary window requires two complete calendar years after"
            " publication before disclosure and one complete year afterward. Recent"
            " errors remain in the registry but cannot enter that comparison. Do not"
            " substitute a later I4R report date to obtain a longer baseline."
        ),
        "",
        (
            "The primary article/review analysis remains pending until verified"
            " identities,"
            " complete risk sets and complete citation retrieval produce supported"
            " matched panels. The separately matched [annual-total analysis]"
            "(aggregate-results.md) reports secondary contrasts from cached"
            " all-type totals."
        ),
        "",
        (
            "See [the evidence catalog](catalog.html), [design](design.md), [data"
            " dictionary](codebook.md), and [analysis status](results.md)."
        ),
    ]
    (folder / "coverage.md").write_text("\n".join(lines) + "\n")
    by_id = {r["source_id"]: r for r in sources}
    scope_by_id = {r["source_id"]: r for r in assessment_scope}
    rows = []
    for r in reviews:
        source = by_id[r["source_id"]]
        cells = [
            source["source_id"],
            source["title"],
            source["collection"],
            r["review_status"],
            r.get("adjudicated_disposition") or r["classification"],
            r.get("adjudication_evidence") or r["evidence_summary"],
            r.get("adjudication_locator") or r["evidence_pages"],
            r.get("assessment_resolved"),
            r.get("canonical_source_id"),
            scope_by_id[r["source_id"]]["status"],
            scope_by_id[r["source_id"]]["evidence"],
        ]
        esc = [html.escape(str(x)) for x in cells]
        esc[1] = (
            '<a href="'
            + html.escape(source["url"], quote=True)
            + '">'
            + esc[1]
            + "</a>"
            if source["url"].startswith("https://")
            else esc[1]
        )
        rows.append("<tr>" + "".join("<td>" + x + "</td>" for x in esc) + "</tr>")
    doc = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>I4R evidence catalog</title>
<style>body{font:16px/1.5 system-ui;
max-width:1500px;
margin:40px auto;
padding:0 24px;
color:#202830}
h1{font-family:Georgia,serif}
input{padding:10px;
width:min(600px,95%);
font:inherit}
table{border-collapse:collapse;
width:100%;
margin-top:24px}
td,th{text-align:left;
border-bottom:1px solid #ddd;
padding:12px;
vertical-align:top}
th{position:sticky;
top:0;
background:#f0f3f5}
td:nth-child(2){min-width:200px}
td:nth-child(6){min-width:250px}
a{color:#17597c}</style>
<h1>Publicizing significant errors: I4R evidence catalog</h1>
<p>This catalog records sources and review dispositions.
A source-screening label is not a verified error finding
or a treatment-effect estimate.
<a href="coverage.md">Coverage</a> · <a href="design.md">Design</a>
</p>
<label for="search">Filter by article, source, error or review status</label>
<p>
<input id="search" type="search">
</p>
<p id="count">
</p>
<table>
<thead>
<tr>
<th>Source</th>
<th>Title</th>
<th>Collection</th>
<th>Initial screening depth</th>
<th>Classification</th>
<th>Evidence summary</th>
<th>Location</th><th>Assessment resolved</th><th>Canonical source</th>
<th>Current scope status</th><th>Scope evidence</th>
</tr>
</thead>
<tbody>"""
    doc += "\n".join(rows)
    doc += """</tbody>
</table>
<script>const input=document.querySelector('#search');
const rows=[...document.querySelectorAll('tbody tr')];
function filter(){const q=input.value.toLowerCase();
let n=0;
rows.forEach(r=>{r.hidden=!r.textContent.toLowerCase().includes(q);
if(!r.hidden)n++});
document.querySelector('#count').textContent=n+' of '+rows.length+' entries';
}
input.addEventListener('input',filter);
filter();
</script>
</html>"""
    (folder / "catalog.html").write_text(doc)
    dictionary(folder)
    print(json.dumps(counts))


if __name__ == "__main__":
    report()
