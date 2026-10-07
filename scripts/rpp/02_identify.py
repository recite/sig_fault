"""Resolve original papers against publisher locators and retain every candidate."""

import collections
import html
import json
import re
import unicodedata

from scripts.research_pipeline import ROOT, Run, read_csv, unique, write_csv


def title_key(value):
    value = re.sub(r"<[^>]+>", "", html.unescape(value))
    value = unicodedata.normalize("NFKD", value).casefold()
    return "".join(x for x in value if x.isalnum())


def first_page(value):
    return re.split("[-–—]", value.strip())[0]


def publication_year(work):
    parts = (work.get("published-print") or work.get("published") or {}).get(
        "date-parts", [[]]
    )
    return str(parts[0][0]) if parts and parts[0] else ""


def candidate(work, source, known_doi):
    title = " ".join(work.get("title", []))
    locator = (
        all(
            str(work.get(field, "")) == source[key]
            for field, key in [("volume", "Volume.O"), ("issue", "Issue.O")]
        )
        and bool(source["Pages.O"])
        and (first_page(work.get("page", "")) == first_page(source["Pages.O"]))
    )
    exact_title = title_key(title) == title_key(source["Study.Title.O"])
    title_prefix = len(title_key(title)) >= 10 and title_key(
        source["Study.Title.O"]
    ).startswith(title_key(title))
    known_match = bool(known_doi) and work["DOI"].lower() == known_doi.lower()
    return dict(
        doi=work["DOI"].lower(),
        title=title,
        journal=source["Journal.O"],
        publication_year=publication_year(work),
        volume=work.get("volume", ""),
        issue=work.get("issue", ""),
        pages=work.get("page", ""),
        exact_title=exact_title,
        title_prefix=title_prefix,
        exact_locator=locator,
        previous_doi_match=known_match,
        accepted=publication_year(work) == "2008"
        and (exact_title or (locator and title_prefix)),
    )


def main():
    with Run("rpp", "02_identify", __file__, True) as run:
        run.require("01_get")
        publisher = json.loads((run.data / "publisher_records.json").read_text())
        base = ROOT / "data/cohorts/rpp"
        papers = read_csv(run.input(base / "papers.csv"))
        source = {
            x["Local.ID"]: x
            for x in read_csv(run.input(base / "source_records/rpp.csv"))
        }
        decisions = json.loads(
            run.input(run.data / "identity_decisions.json").read_text()
        )
        for decision in decisions:
            run.check(
                "sourced_identity_decision",
                bool(decision["evidence_urls"]) and bool(decision["reason"]),
                decision["paper_id"],
            )
            for field, replacement in decision["replace"].items():
                run.check(
                    "expected_original_value",
                    source[decision["paper_id"]][field] == replacement["from"],
                    field,
                )
                source[decision["paper_id"]][field] = replacement["to"]
            for path in decision.get("evidence_files", []):
                run.input(ROOT / path)
        assessments = read_csv(run.input(base / "assessments.csv"))
        groups = collections.defaultdict(list)
        for a in assessments:
            label = a["source_outcome"].strip().casefold()
            run.check(
                "known_replication_judgment", label in {"yes", "no"}, a["assessment_id"]
            )
            groups[a["paper_id"]].append(label)
        identities, candidates = [], []
        for paper in papers:
            pid = paper["paper_id"]
            comparisons = [
                candidate(w, source[pid], paper["doi"])
                for w in publisher[source[pid]["Journal.O"]]
            ]
            candidates.extend(
                dict(paper_id=pid, **c)
                for c in comparisons
                if c["exact_locator"] or c["exact_title"] or c["previous_doi_match"]
            )
            accepted = [c for c in comparisons if c["accepted"]]
            if len(accepted) == 1 and (
                not paper["doi"] or accepted[0]["doi"] == paper["doi"]
            ):
                result = accepted[0]
                status = "verified_publisher"
                evidence = "unique journal/year match with " + (
                    "title plus volume/issue/first page"
                    if result["exact_locator"]
                    else "normalized full title"
                )
            else:
                result = dict(
                    doi="",
                    title=paper["title"],
                    journal=source[pid]["Journal.O"],
                    publication_year="2008",
                    volume="",
                    issue="",
                    pages="",
                )
                status, evidence = (
                    "unresolved",
                    f"{len(accepted)} accepted candidates; check prior DOI agreement",
                )
                run.record["unresolved"].append(dict(paper_id=pid, reason=evidence))
            labels = set(groups[pid])
            classification = (
                "unsuccessful"
                if labels == {"no"}
                else "successful" if labels == {"yes"} else "mixed"
            )
            identities.append(
                dict(
                    paper_id=pid,
                    **{
                        k: result[k]
                        for k in [
                            "doi",
                            "title",
                            "journal",
                            "publication_year",
                            "volume",
                            "issue",
                            "pages",
                        ]
                    },
                    classification=classification,
                    assessment_count=len(groups[pid]),
                    project_url=paper["source_link"],
                    status=status,
                    evidence=evidence,
                )
            )
        unique(identities, ["paper_id"])
        unique([x for x in identities if x["doi"]], ["doi"])
        run.check(
            "paper_conservation",
            len(identities) == 98
            and sum(x["assessment_count"] for x in identities) == 100,
            "98 original papers, 100 completed source assessments",
        )
        for name, rows in [
            ("identities.csv", identities),
            ("identity_candidates.csv", candidates),
        ]:
            path = run.data / name
            write_csv(path, rows, list(rows[0]))
            run.output(path)
        run.record["metrics"] = dict(
            papers=len(identities),
            verified=sum(bool(x["doi"]) for x in identities),
            classifications=dict(
                collections.Counter(x["classification"] for x in identities)
            ),
        )
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
