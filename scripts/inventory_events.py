"""Build an external disclosure registry from explicit source adjudications."""

import argparse
import datetime as dt
import json
import re
import urllib.parse

import audit_inventories as inventory

DATA = inventory.DATA
CACHE = inventory.ROOT / "private-data/inventories/original-metadata"


def fetch_metadata():
    import i4r_registry as registry
    import i4r_sources as acquisition

    reviews = json.loads((DATA / "primary_reviews.json").read_text())["cases"]
    records = []
    for review in reviews:
        doi = review.get("original_journal_doi") or review["original_doi"]
        path = CACHE / (review["record_id"] + ".json")
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
        work = acquisition.fetch(url, path)["message"]
        title = (work.get("title") or [""])[0]
        if inventory.doi(work["DOI"]) != doi:
            raise ValueError("Crossref DOI differs from requested identity")
        if registry.identity_title_key(title) != registry.identity_title_key(
            review["original_title"]
        ):
            raise ValueError("Original title requires manual identity adjudication")
        date = registry.publisher_date({"doi": doi}, work).get("publication_date", "")
        if not date:
            raise ValueError("Original lacks publication date")
        records.append(
            dict(
                record_id=review["record_id"],
                inventory_doi=review["original_doi"],
                journal_doi=doi,
                title=title,
                publication_date=date,
                journal=(work.get("container-title") or [""])[0],
                type=work["type"],
                source_url=url,
                sha256=inventory.digest(path.read_bytes()),
                retrieved_at=json.loads(
                    path.with_suffix(".json.source.json").read_text()
                )["retrieved_at"],
            )
        )
    (DATA / "original_metadata.json").write_text(json.dumps(records, indent=2) + "\n")


def date_year(value, precision):
    patterns = {"year": r"\d{4}", "month": r"\d{4}-\d{2}", "day": r"\d{4}-\d{2}-\d{2}"}
    if precision not in patterns or not re.fullmatch(patterns[precision], value):
        raise ValueError("Date and precision disagree")
    dt.date.fromisoformat(
        value + {"year": "-01-01", "month": "-01", "day": ""}[precision]
    )
    return int(value[:4])


def make_rows(reviews, metadata, decisions, last_complete_year=2025):
    lookup = {r["record_id"]: r for r in reviews}
    if len(lookup) != len(reviews):
        raise ValueError("Repeated review identity")
    meta = {r["record_id"]: r for r in metadata}
    if len(meta) != len(metadata) or set(meta) != set(lookup):
        raise ValueError("Metadata must cover each reviewed original exactly once")
    choices = {r["record_id"]: r for r in decisions}
    if len(choices) != len(decisions) or not set(choices).issubset(lookup):
        raise ValueError("Repeated or unknown disclosure adjudication")
    rows = []
    for rid, review in lookup.items():
        m = meta[rid]
        if m["inventory_doi"] != review["original_doi"] or m["journal_doi"] != (
            review.get("original_journal_doi") or review["original_doi"]
        ):
            raise ValueError("Metadata DOI linkage changed")
        d = choices.get(rid, {})
        status = d.get("material_error_verified", "pending")
        if status not in {"yes", "no", "pending"}:
            raise ValueError("Unknown material-error status")
        year = ""
        if d.get("publicity_verified") == "yes":
            year = date_year(d["date"], d["date_precision"])
            if not d.get("date_evidence") or not d.get("date_sources"):
                raise ValueError("Verified disclosure lacks date evidence")
            for source in d["date_sources"]:
                if (
                    not source.get("url")
                    or not source.get("locator")
                    or not re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", ""))
                ):
                    raise ValueError("Date source lacks located, hashed evidence")
        if status == "yes" and not all(
            d.get(k)
            for k in [
                "affected_claim",
                "original_value",
                "corrected_value",
                "correction_scope",
                "decision_evidence",
            ]
        ):
            raise ValueError("Verified material error lacks its numerical consequence")
        publication_year = int(m["publication_date"][:4])
        age = bool(year and publication_year < year - 2)
        followup = bool(year and year + 1 <= last_complete_year)
        reasons = []
        if status != "yes":
            reasons.append("material_error_" + status)
        if not year:
            reasons.append("disclosure_year_unresolved")
        elif not age:
            reasons.append("original_too_recent_for_two_full_preyears")
        if year and not followup:
            reasons.append("first_full_postyear_unavailable")
        rows.append(
            dict(
                record_id=rid,
                inventory_doi=review["original_doi"],
                journal_doi=m["journal_doi"],
                original_title=m["title"],
                original_publication_date=m["publication_date"],
                material_error_verified=status,
                affected_claim=d.get("affected_claim", ""),
                original_value=d.get("original_value", ""),
                corrected_value=d.get("corrected_value", ""),
                correction_scope=d.get("correction_scope", ""),
                disclosure_date=d.get("date", ""),
                date_precision=d.get("date_precision", ""),
                public_year=year,
                date_evidence=d.get("date_evidence", ""),
                date_source_urls=";".join(s["url"] for s in d.get("date_sources", [])),
                age_and_followup_supported="yes" if age and followup else "no",
                ready_for_citation_collection="no" if reasons else "yes",
                collection_exclusion=";".join(reasons),
                analysis_eligible="pending",
                limitations=d.get(
                    "limitations", "Primary-source adjudication incomplete"
                ),
            )
        )
    return rows


def build():
    reviews = json.loads((DATA / "primary_reviews.json").read_text())["cases"]
    metadata = json.loads((DATA / "original_metadata.json").read_text())
    decisions = json.loads((DATA / "disclosure_adjudications.json").read_text())[
        "cases"
    ]
    rows = make_rows(reviews, metadata, decisions)
    inventory.write_csv("disclosure_candidates.csv", rows)
    counts = dict(
        reviewed=len(rows),
        adjudicated=len(decisions),
        material_errors=sum(r["material_error_verified"] == "yes" for r in rows),
        dated=sum(bool(r["public_year"]) for r in rows),
        ready_for_citation_collection=sum(
            r["ready_for_citation_collection"] == "yes" for r in rows
        ),
        analysis_eligible=0,
    )
    (DATA / "disclosure_status.json").write_text(json.dumps(counts, indent=2) + "\n")
    lines = [
        "# External error disclosures",
        "",
        f"Of {counts['reviewed']} primary-source reviews, "
        f"{counts['material_errors']} have an adjudicated material error and "
        f"{counts['dated']} have a supported public disclosure year. "
        f"{counts['ready_for_citation_collection']} pass both these checks and the "
        "article-age/follow-up restrictions for citation collection. None yet "
        "contributes a new matched effect estimate.",
        "",
        "| Original paper | Public year | Material error | Collection status |",
        "| --- | ---: | --- | --- |",
    ]
    for r in rows:
        if r["record_id"] not in {d["record_id"] for d in decisions}:
            continue
        labels = {
            "disclosure_year_unresolved": "Disclosure year unresolved",
            "original_too_recent_for_two_full_preyears": (
                "Insufficient pre-disclosure history"
            ),
            "first_full_postyear_unavailable": "Follow-up incomplete",
        }
        status = (
            "; ".join(
                labels.get(v, v.replace("_", " "))
                for v in r["collection_exclusion"].split(";")
                if v
            )
            or "Ready"
        )
        lines.append(
            f"| {r['original_title']} | {r['public_year'] or 'Unresolved'} "
            f"| {r['material_error_verified']} | {status} |"
        )
    lines += [
        "",
        "## Definition and evidence",
        "",
        "The exposure is the earliest substantiated public disclosure of a "
        "demonstrated material error in the original article. A correction can "
        "qualify when it changes a substantive magnitude without reversing the "
        "conclusion. The registry separates correcting a mistake from changing "
        "the specification or recalibrating a model.",
        "",
        "Year precision supports annual analysis when that public year is "
        "established. An earlier manuscript or degree date alone does not. "
        "Dates are the earliest supported versions found, not proof that no "
        "earlier public warning existed. Search scope and uncertainty remain "
        "attached to each decision.",
        "",
        "The original journal article must predate January 1 of disclosure "
        "year minus two. The first full post-disclosure year must be complete "
        "through 2025. Readiness for citation collection does not establish "
        "retraction eligibility, complete control acquisition, a usable match "
        "or parallel counterfactual citation trends. Those remain separate "
        "requirements under the [analysis design](i4r/design.md).",
        "",
        "The [decisions](../data/inventories/disclosure_adjudications.json) "
        "record numerical consequences and hashed date sources. The "
        "[complete candidate table](../data/inventories/disclosure_candidates.csv) "
        "retains every reviewed case, including pending decisions and age "
        "exclusions. [Original metadata](../data/inventories/original_metadata.json) "
        "preserve inventory and journal DOIs separately. The underlying "
        "[primary reviews](../data/inventories/primary_reviews.json) contain "
        "error mechanisms and author responses; original analyses were not rerun.",
        "",
        "Run `make inventories-test` for an offline rebuild and eligibility "
        "tests. `python3 scripts/inventory_events.py fetch-metadata` separately "
        "refreshes publication metadata from Crossref, checking DOI and title "
        "agreement. Error and disclosure decisions require source review and "
        "are never inferred from citation outcomes.",
        "",
    ]
    (inventory.ROOT / "docs/external-disclosures.md").write_text("\n".join(lines))
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["fetch-metadata", "build"])
    args = parser.parse_args()
    {"fetch-metadata": fetch_metadata, "build": build}[args.command]()
