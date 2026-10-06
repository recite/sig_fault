"""Decompose paired citation counts and audit conflicting publication years."""

import argparse
import collections
import json
import time
import urllib.parse

import nieuwenhuis as nw
import pilot

COMPONENTS = [
    "shared_year_shift",
    "shared_type_exclusion",
    "shared_predate_exclusion",
    "openalex_only_doi",
    "wos_only_doi",
    "openalex_no_doi",
    "wos_no_doi",
]


def decompose(panel, links, historical, edges):
    """Attribute OA minus WoS counts, preserving the exact paired population."""
    complete = {r["paper_id"] for r in panel if r["status"] == "complete"}
    cells = collections.defaultdict(collections.Counter)
    for row in links:
        pid = row["paper_id"]
        if pid not in complete:
            raise ValueError("Link lies outside complete paired cohort")
        wy, oy = row["wos_year"], row["openalex_year"]
        article = row["openalex_type"] in {"article", "review"}
        dated = row["openalex_before_original_date"] == "no"
        if row["presence"] == "both":
            if not article:
                cells[pid, wy]["shared_type_exclusion"] -= 1
            elif not dated:
                cells[pid, wy]["shared_predate_exclusion"] -= 1
            else:
                cells[pid, oy]["shared_year_shift"] += 1
                cells[pid, wy]["shared_year_shift"] -= 1
        elif row["presence"] == "openalex_only":
            if article and dated:
                cells[pid, oy]["openalex_only_doi"] += 1
        elif row["presence"] == "wos_only":
            cells[pid, wy]["wos_only_doi"] -= 1
        else:
            raise ValueError("Unknown link presence")
    for row in historical:
        pid = "nw_" + row["article_id"]
        if (
            pid in complete
            and not row["doi"]
            and row["duplicate"] == "FALSE"
            and row["false_link"] == "FALSE"
        ):
            cells[pid, row["year"]]["wos_no_doi"] -= 1
    for row in nw.eligible_edges(edges, {"article", "review"}):
        if row["paper_id"] in complete and not row["doi"]:
            cells[row["paper_id"], row["publication_year"]]["openalex_no_doi"] += 1
    result = []
    for row in panel:
        if row["status"] != "complete":
            continue
        parts = cells[row["paper_id"], row["year"]]
        difference = int(row["openalex"]) - int(row["wos"])
        if sum(parts.values()) != difference:
            raise ValueError(
                "Decomposition does not reproduce source counts: " + str(row)
            )
        result.append(
            {k: row[k] for k in ["paper_id", "year", "flag", "wos", "openalex"]}
            | dict(difference=difference)
            | {k: parts[k] for k in COMPONENTS}
        )
    return result


def reconcile_links(links, reviews):
    """Correct evidenced DOI transcription errors, retaining source identifiers."""
    merged = {
        (r["paper_id"], r["doi"]): r
        | {
            "wos_original_doi": r["doi"] if r["wos_year"] else "",
            "match_method": "exact_doi",
        }
        for r in links
    }
    for review in reviews:
        if review["classification"] != "doi_transcription_error":
            continue
        pid = review["paper_id"]
        old_key, new_key = (pid, review["wos_doi"]), (pid, review["openalex_doi"])
        old, new = merged[old_key], merged[new_key]
        if old["presence"] != "wos_only" or new["presence"] != "openalex_only":
            raise ValueError("DOI correction is not a unique unmatched pair")
        if not review["source_url"] or not review["evidence"]:
            raise ValueError("DOI correction lacks source evidence")
        merged[new_key] = new | dict(
            wos_year=old["wos_year"],
            wos_original_doi=review["wos_doi"],
            presence="both",
            year_agrees=str(old["wos_year"] == new["openalex_year"]).lower(),
            match_method="verified_doi_correction",
        )
        del merged[old_key]
    return [merged[key] for key in sorted(merged)]


def date_string(work, field):
    parts = (work.get(field) or {}).get("date-parts", [[]])[0]
    return "-".join(str(x).zfill(4 if i == 0 else 2) for i, x in enumerate(parts))


def fetch_dates():
    dois = sorted(
        {r["doi"] for r in nw.read("doi_overlap.csv") if r["year_agrees"] == "false"}
    )
    records = {r["doi"]: r for r in nw.read("date_metadata.csv")}
    for i, doi in enumerate(dois, 1):
        if records.get(doi, {}).get("status") == "verified":
            continue
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
        path = nw.CACHE / "citing_dates" / (pilot.sha256(doi.encode()) + ".json")
        row = dict(
            doi=doi,
            online_date="",
            print_date="",
            published_date="",
            status="",
            source_url=url,
            detail="",
        )
        try:
            if not path.exists():
                time.sleep(1)
            work = nw.acquisition.fetch(url, path)["message"]
            if pilot.normalize_doi(work.get("DOI", "")) != doi:
                raise ValueError("Publisher DOI mismatch")
            row.update(
                online_date=date_string(work, "published-online"),
                print_date=date_string(work, "published-print"),
                published_date=date_string(work, "published"),
                status="verified",
            )
        except Exception as exc:
            row.update(status="unavailable", detail=str(exc)[:200])
        records[doi] = row
        pilot.write_csv(
            nw.DATA / "date_metadata.csv", list(records.values()), list(row)
        )
        if i % 25 == 0:
            print(f"Date metadata: {i}/{len(dois)}", flush=True)


def classify_dates(link, metadata):
    if metadata.get("status") != "verified":
        return "metadata_unavailable"
    online = metadata.get("online_date", "")[:4]
    printed = metadata.get("print_date", "")[:4]
    wy, oy = link["wos_year"], link["openalex_year"]
    if online == oy and printed == wy and online != printed:
        return "openalex_online_wos_print"
    if online == wy and printed == oy and online != printed:
        return "wos_online_openalex_print"
    return "incomplete_dates" if not online or not printed else "dates_disagree"


def build():
    panel = nw.read("paired_panel.csv")
    exact = nw.read("doi_overlap.csv")
    reviews = nw.read("link_review.csv")
    links = reconcile_links(exact, reviews)
    pilot.write_csv(
        nw.DATA / "reconciled_overlap.csv",
        links,
        list(links[0]) if links else ["paper_id", "doi"],
    )
    rows = decompose(
        panel,
        links,
        pilot.read_csv(pilot.ROOT / "data/derived/raw.csv"),
        nw.read("citation_edges.csv"),
    )
    fields = ["paper_id", "year", "flag", "wos", "openalex", "difference"] + COMPONENTS
    pilot.write_csv(nw.DATA / "count_decomposition.csv", rows, fields)
    groups = collections.defaultdict(list)
    for row in rows:
        groups[row["year"], row["flag"]].append(row)
    annual = []
    for (year, flag), group in sorted(groups.items()):
        annual.append(
            dict(year=year, flag=flag, papers=len(group))
            | {k: sum(int(r[k]) for r in group) for k in fields[3:]}
        )
    pilot.write_csv(
        nw.DATA / "decomposition_summary.csv",
        annual,
        ["year", "flag", "papers"] + fields[3:],
    )
    metadata = {r["doi"]: r for r in nw.read("date_metadata.csv")}
    disagreements = []
    for row in links:
        if row["year_agrees"] != "false":
            continue
        dates = metadata.get(row["doi"], {})
        disagreements.append(
            {k: row[k] for k in ["paper_id", "doi", "wos_year", "openalex_year"]}
            | {k: dates.get(k, "") for k in ["online_date", "print_date", "source_url"]}
            | dict(explanation=classify_dates(row, dates))
        )
    pilot.write_csv(
        nw.DATA / "date_disagreements.csv",
        disagreements,
        [
            "paper_id",
            "doi",
            "wos_year",
            "openalex_year",
            "online_date",
            "print_date",
            "source_url",
            "explanation",
        ],
    )
    status = dict(
        paired_papers=len({r["paper_id"] for r in rows}),
        reconciled_doi_links=dict(collections.Counter(r["presence"] for r in links)),
        link_reviews=dict(collections.Counter(r["classification"] for r in reviews)),
        shared_year_disagreements=len(disagreements),
        openalex_earlier=sum(
            int(r["openalex_year"]) < int(r["wos_year"]) for r in disagreements
        ),
        date_explanations=dict(
            collections.Counter(r["explanation"] for r in disagreements)
        ),
    )
    (nw.DATA / "diagnostic_status.json").write_text(json.dumps(status, indent=2) + "\n")
    baseline = [r for r in annual if r["year"] == "2010"]
    macros = dict(
        NwPairedPapers=status["paired_papers"],
        NwPairedFlagged=len({r["paper_id"] for r in rows if r["flag"] == "1"}),
        NwPairedComparison=len({r["paper_id"] for r in rows if r["flag"] == "0"}),
        NwYearMismatch=status["shared_year_disagreements"],
        NwEarlier=status["openalex_earlier"],
        NwDateExplained=status["date_explanations"].get("openalex_online_wos_print", 0),
        NwBaselineShift=sum(r["shared_year_shift"] for r in baseline),
        NwBaselineGap=sum(r["difference"] for r in baseline),
    )
    (pilot.ROOT / "tabs/nieuwenhuis_macros.tex").write_text(
        "".join(
            "\\newcommand{\\" + k + "}{" + str(v) + "}\n" for k, v in macros.items()
        )
    )
    lines = [
        "# Why the citation counts differ",
        "",
        f"The paired comparison covers {status['paired_papers']} original papers. "
        "The decomposition holds those identities fixed and exactly reconstructs "
        "OpenAlex article/review counts minus the historical Web of Science counts "
        "for every included paper-year. It does not estimate the publicity effect.",
        "",
        "## Annual count decomposition",
        "",
        "Entries are total citing relationships across the paired papers, not "
        "per-paper means. "
        "Positive entries raise OpenAlex relative to Web of Science.",
        "",
    ]
    labels = {
        "wos": "Web of Science counts",
        "openalex": "OpenAlex article/review counts",
        "difference": "Difference (OpenAlex minus WoS)",
        "shared_year_shift": "Shared-link publication years",
        "shared_type_exclusion": "Shared-link type exclusions",
        "shared_predate_exclusion": "Shared-link predating exclusions",
        "openalex_only_doi": "OpenAlex-only DOI",
        "wos_only_doi": "Web of Science-only DOI",
        "openalex_no_doi": "OpenAlex without DOI",
        "wos_no_doi": "Web of Science without DOI",
    }
    for flag in sorted({r["flag"] for r in annual}):
        group = [r for r in annual if r["flag"] == flag]
        lines += [
            "Flagged papers" if flag == "1" else "Comparison papers",
            "",
            "| Component | " + " | ".join(r["year"] for r in group) + " |",
            "| --- | " + " | ".join("---:" for _ in group) + " |",
        ]
        for key, label in labels.items():
            lines.append(
                "| " + label + " | " + " | ".join(str(r[key]) for r in group) + " |"
            )
        lines.append("")
    lines += [
        "",
        "Shared-link dating moves an eligible citation between years while keeping the "
        "citing DOI fixed. A shared link excluded by OpenAlex's article/review rule is "
        "assigned to type exclusions at its historical year; a remaining shared link "
        "dated before the original is assigned to predating exclusions. Only shared "
        "links eligible for the primary OpenAlex count enter the dating component. "
        "This ordering prevents double counting but is one accounting convention.",
        "",
        "DOI-only terms are unmatched identifiers, not verified missing or "
        "erroneous references. "
        "Malformed DOIs, books versus chapters and different publication versions"
        " can create "
        "unmatched records. Non-DOI records are also unresolved across sources. "
        "The historical source lacks the document-type detail needed for an "
        "identical restriction.",
        "",
        "## Publisher-date check",
        "",
        f"Among {status['shared_year_disagreements']} shared links with different "
        f"years, OpenAlex assigns {status['openalex_earlier']} an earlier year. "
        "Publisher-deposited Crossref metadata supplies a separate check of "
        "online and print dates.",
        "",
        "| Date evidence | Citation relationships |",
        "| --- | ---: |",
    ]
    labels = {
        "openalex_online_wos_print": (
            "OpenAlex matches online year; WoS matches print year"
        ),
        "wos_online_openalex_print": (
            "WoS matches online year; OpenAlex matches print year"
        ),
        "incomplete_dates": "Online or print date is missing",
        "dates_disagree": "Both dates available but do not explain the difference",
        "metadata_unavailable": "Publisher metadata unavailable",
    }
    for key, count in sorted(status["date_explanations"].items()):
        lines.append(f"| {labels[key]} | {count} |")
    lines += [
        "",
        "Date agreement supports a dating-convention explanation for those "
        "specific records. "
        "It does not prove that every date is correct, establish when authors "
        "became aware of "
        "the critique, or determine which date best measures that response. "
        "Records counted "
        "here are original–citing DOI relationships; the same citing paper may "
        "link to more "
        "than one original.",
        "",
        "`python3 scripts/nieuwenhuis_diagnostics.py build` rebuilds these "
        "results offline. "
        "The `fetch-dates` command retrieves metadata only for shared links with "
        "conflicting "
        "years and retains cached responses. The date check is "
        "diagnostic-selected, not a "
        "representative audit of all citations. Original counts and citation "
        "dates remain unchanged.",
        "",
        "See [paired counts](README.md), [record-level "
        "decomposition](../../data/nieuwenhuis/count_decomposition.csv), "
        "[date records](../../data/nieuwenhuis/date_disagreements.csv), and "
        "[metadata](../../data/nieuwenhuis/date_metadata.csv).",
    ]
    lines += [
        "",
        "## Review of unmatched historical identifiers",
        "",
        "The decomposition reconciles documented DOI transcription errors. "
        "Both original and corrected identifiers remain in the reconciled crosswalk. "
        "Translations and book components remain separate records. "
        "The [review ledger](../../data/nieuwenhuis/link_review.csv) records evidence "
        "and unresolved cases; no case is called a false citation merely because "
        "it lacks an exact match.",
        "",
        "| Review finding | Historical relationships |",
        "| --- | ---: |",
    ]
    for key, count in sorted(status["link_reviews"].items()):
        lines.append(f"| {key.replace('_', ' ')} | {count} |")
    lines += [
        "",
        "After verified identifier corrections, matched-DOI relationships number "
        f"{status['reconciled_doi_links'].get('both', 0)}. "
        "The [original exact-DOI crosswalk](../../data/nieuwenhuis/doi_overlap.csv) "
        "retains the source identifiers for comparison.",
    ]
    (pilot.ROOT / "docs/nieuwenhuis/diagnostics.md").write_text("\n".join(lines) + "\n")
    print(status)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "fetch-dates"])
    args = parser.parse_args()
    {"build": build, "fetch-dates": fetch_dates}[args.command]()
