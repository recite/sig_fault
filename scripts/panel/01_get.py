"""Preserve the dated panel-audit source before assigning historical diagnostics."""

import argparse
import hashlib
import io
import json
import tarfile

from scripts.research_pipeline import ROOT, Run, digest, read_csv, write_json

SOURCES = {
    "arxiv_v1_source": (
        "https://arxiv.org/src/2309.15983v1",
        "60d0453c01f78b434460cd41af28f6fbe23e068b27d7e2704dd85080a65d8d54",
    ),
    "arxiv_v1_pdf": (
        "https://arxiv.org/pdf/2309.15983v1",
        "137b6c064e6d6a9369a228a375ad00ceb3b190ed65f157866840f6291dd0f1ac",
    ),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    with Run("panel", "01_get", __file__, args.offline) as run:
        for source in read_csv(run.input(ROOT / "data/cohorts/panel/sources.csv")):
            path = run.input(ROOT / source["local_path"])
            run.check("final_source_hash", digest(path) == source["sha256"], path.name)
        members = []
        for name, (url, expected) in SOURCES.items():
            body = run.fetch(url, "historical", False)
            run.check(
                "dated_source_hash", hashlib.sha256(body).hexdigest() == expected, name
            )
            if name != "arxiv_v1_source":
                continue
            with tarfile.open(fileobj=io.BytesIO(body)) as archive:
                for member in ["main.tex", "sm.tex", "tscs.bib"]:
                    payload = archive.extractfile(member).read()
                    path = run.cache / "extracted" / member
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(payload)
                    run.output(path)
                    members.append(
                        dict(
                            member=member,
                            bytes=len(payload),
                            sha256=hashlib.sha256(payload).hexdigest(),
                        )
                    )
        metadata = run.fetch(
            "https://api.crossref.org/works/10.1017/S0003055425000243", "metadata"
        )
        path = run.data / "journal_metadata.json"
        write_json(path, metadata)
        run.output(path)
        path = run.data / "historical_source_members.json"
        write_json(path, members)
        run.output(path)
        run.record["metrics"] = dict(historical_version="arxiv_v1", extracted_members=3)
        run.record["unresolved"] = [
            "Historical original identities and overlap require verification",
            "Public availability before 2023 has not been established",
            "Final 49-paper diagnoses cannot be backdated to the 37-paper version",
        ]
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
