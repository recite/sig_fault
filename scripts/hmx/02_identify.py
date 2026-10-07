"""Resolve the complete audit roster using its deposited reference DOIs."""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor

from scripts.research_pipeline import ROOT, Run, read_csv, unique, write_csv, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    with Run("hmx", "02_identify", __file__, args.offline) as run:
        run.require("01_get")
        roster = read_csv(run.input(ROOT / "data/cohorts/hmx/papers.csv"))
        roster = {x["paper_id"]: x for x in roster}
        crosswalk = read_csv(run.input(run.data / "reference_crosswalk.csv"))
        unique(crosswalk, ["paper_id"])
        run.check(
            "complete_crosswalk",
            {x["paper_id"] for x in crosswalk} == set(roster),
            len(roster),
        )
        audit = json.loads((run.data / "audit_metadata.json").read_text())["message"]
        references = {x["key"]: x for x in audit["reference"]}

        def identify(row):
            doi = references[row["publisher_reference_key"]]["DOI"].lower()
            work = run.fetch("https://api.crossref.org/works/" + doi, "originals")[
                "message"
            ]
            print_year = work.get("published-print", {}).get("date-parts", [[None]])[0][
                0
            ]
            first_author = work.get("author", [{}])[0].get("family", "")
            run.check(
                "reference_identity",
                work["DOI"].lower() == doi
                and first_author.casefold() == row["first_author"].casefold()
                and print_year == int(row["publication_year"])
                and row["issn"] in work.get("ISSN", []),
                row["paper_id"],
            )
            return (
                dict(
                    row,
                    doi=doi,
                    title=work["title"][0],
                    source_reference=roster[row["paper_id"]]["source_reference"],
                    status="verified_publisher_reference",
                ),
                work,
            )

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(identify, crosswalk))
        identities, metadata = zip(*results)
        unique(identities, ["doi"])
        path = run.data / "identities.csv"
        write_csv(path, identities, list(identities[0]))
        run.output(path)
        path = run.data / "original_metadata.json"
        write_json(path, metadata)
        run.output(path)
        existing = read_csv(run.input(ROOT / "data/meta/assessment_identities.csv"))
        overlap = [
            dict(
                paper_id=x["paper_id"],
                doi=x["doi"],
                other_study=y["component"],
                other_paper_id=y["article_id"],
            )
            for x in identities
            for y in existing
            if x["doi"] == y["doi"].lower()
        ]
        path = run.data / "overlap.csv"
        write_csv(path, overlap, ["paper_id", "doi", "other_study", "other_paper_id"])
        run.output(path)
        run.record["metrics"] = dict(
            verified_originals=len(identities), overlaps=len(overlap)
        )
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
