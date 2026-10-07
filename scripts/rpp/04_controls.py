"""Freeze the same-journal, same-print-year donor universe before citation matching."""

import importlib
import json
import re

from scripts.research_pipeline import ROOT, Run, read_csv, unique, write_csv

identity = importlib.import_module("scripts.rpp.02_identify")


def main():
    with Run("rpp", "04_controls", __file__, True) as run:
        run.require("02_identify")
        run.input(run.data / "design.md")
        run.input(ROOT / "scripts/rpp/02_identify.py")
        decisions = json.loads(
            run.input(run.data / "control_decisions.json").read_text()
        )
        manual = {d["doi"]: d for d in decisions}
        publication_types = {
            x["doi"]: x["publication_types"]
            for x in read_csv(run.input(run.data / "publication_types.csv"))
        }
        run.check(
            "sourced_control_decisions",
            len(manual) == len(decisions)
            and all(d["evidence_url"] and d["reason"] for d in decisions),
            len(decisions),
        )
        records = json.loads((run.data / "publisher_records.json").read_text())
        assessed = {
            r["doi"].lower()
            for r in read_csv(run.input(ROOT / "data/cohorts/papers.csv"))
            if r["doi"]
        }
        for name in ["flora_inventory.csv", "fred_inventory.csv"]:
            assessed.update(
                r["original_doi"].lower()
                for r in read_csv(run.input(ROOT / "data/inventories" / name))
                if r["original_doi"]
            )
        targets = read_csv(run.data / "identities.csv")
        target_dois = {r["doi"] for r in targets if r["doi"]}
        run.check("all_targets_identified", len(target_dois) == 98, len(target_dois))
        candidates, controls = [], []
        for journal, works in records.items():
            for work in works:
                if identity.publication_year(work) != "2008":
                    continue
                doi = work["DOI"].lower()
                title = " ".join(work.get("title", []))
                reasons = []
                if doi in manual:
                    reasons.append("reviewed_nonresearch: " + manual[doi]["reason"])
                elif any(
                    label in publication_types.get(doi, "").split(";")
                    for label in ["Comment", "Review", "Editorial"]
                ):
                    reasons.append("pubmed_nonresearch_publication_type")
                if doi in target_dois:
                    reasons.append("rpp_target")
                elif doi in assessed:
                    reasons.append("known_replication_assessed_at_any_date")
                if re.search(
                    r"\b(correction|corrigendum|erratum|retraction|retracted)\b",
                    title,
                    re.I,
                ):
                    reasons.append("correction_or_retraction_notice")
                if re.search(
                    r"^(editorial|acknowledg|reviewers|index to|contents|"
                    r"in memoriam|obituary)",
                    title,
                    re.I,
                ):
                    reasons.append("nonresearch_front_matter")
                if not work.get("author"):
                    reasons.append("no_named_author")
                item = dict(
                    paper_id="control_" + doi,
                    doi=doi,
                    title=title,
                    journal=journal,
                    publication_year="2008",
                    volume=work.get("volume", ""),
                    issue=work.get("issue", ""),
                    pages=work.get("page", ""),
                    eligible=not reasons,
                    exclusion_reason=";".join(reasons),
                )
                candidates.append(item)
                if not reasons:
                    controls.append(
                        {
                            k: item[k]
                            for k in [
                                "paper_id",
                                "doi",
                                "title",
                                "journal",
                                "publication_year",
                            ]
                        }
                    )
        unique(candidates, ["doi"])
        run.check(
            "disjoint_donor_pool",
            not target_dois.intersection(x["doi"] for x in controls),
            dict(targets=len(targets), controls=len(controls)),
        )
        analysis_targets = [
            {
                k: x[k]
                for k in ["paper_id", "doi", "title", "journal", "publication_year"]
            }
            | dict(role=x["classification"])
            for x in targets
        ]
        analysis_targets += [x | dict(role="external_control") for x in controls]
        for name, rows in [
            ("control_candidates.csv", candidates),
            ("citation_targets.csv", analysis_targets),
        ]:
            path = run.data / name
            write_csv(path, rows, list(rows[0]))
            run.output(path)
        run.record["metrics"] = dict(
            screened=len(candidates),
            eligible_controls=len(controls),
            citation_targets=len(analysis_targets),
        )
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
