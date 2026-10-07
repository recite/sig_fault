"""Freeze publisher-deposited metadata for every manuscript reference."""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor

from scripts.research_pipeline import ROOT, Run, read_csv, unique, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    with Run(
        "references",
        "01_get",
        __file__,
        args.offline,
        data_dir=ROOT / "data/references",
    ) as run:
        registry = read_csv(run.input(run.data / "registry.csv"))
        unique(registry, ["key"])
        unique(registry, ["doi"])

        def get(row):
            value = run.fetch(
                "https://api.crossref.org/works/" + row["doi"], "crossref"
            )
            run.check(
                "doi_identity",
                value["message"]["DOI"].lower() == row["doi"].lower(),
                row["key"],
            )
            return row["key"], value["message"]

        with ThreadPoolExecutor(max_workers=4) as pool:
            values = dict(pool.map(get, registry))
        path = run.data / "crossref.json"
        write_json(path, values)
        run.output(path)
        run.record["metrics"] = dict(references=len(values))
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
