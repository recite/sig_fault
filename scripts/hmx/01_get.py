"""Preserve audit metadata and public-release evidence before citation acquisition."""

import argparse
import hashlib
import io
import json
import zipfile

from scripts.research_pipeline import ROOT, Run, digest, read_csv, write_csv, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    with Run("hmx", "01_get", __file__, args.offline) as run:
        sources = read_csv(run.input(ROOT / "data/cohorts/hmx/sources.csv"))
        for source in sources:
            path = run.input(ROOT / source["local_path"])
            run.check(
                "original_checksum", digest(path) == source["sha256"], source["file"]
            )
        for name in [
            "papers.csv",
            "assessments.csv",
            "source_records/hmx.csv",
            "study.json",
        ]:
            run.input(ROOT / "data/cohorts/hmx" / name)
        endpoints = {
            "audit": "https://api.crossref.org/works/10.1017/pan.2018.46",
            "earlier_critique": "https://api.crossref.org/works/10.1596/1813-9450-6602",
            "archive": (
                "https://dataverse.harvard.edu/api/datasets/:persistentId/"
                "?persistentId=doi:10.7910/DVN/Q1V0OG"
            ),
        }
        for name, url in endpoints.items():
            value = run.fetch(url, "metadata")
            path = run.data / (name + "_metadata.json")
            write_json(path, value)
            run.output(path)
        run.fetch(
            "https://yiqingxu.org/packages/interflex/SI_update.pdf", "followup", False
        )
        archive = json.loads((run.data / "archive_metadata.json").read_text())["data"]
        files = archive["latestVersion"]["files"]
        members = []
        for file in files:
            item = file["dataFile"]
            payload = run.fetch(
                f"https://dataverse.harvard.edu/api/access/datafile/{item['id']}",
                "archive",
                False,
            )
            run.check("archive_size", len(payload) == item["filesize"], file["label"])
            run.check(
                "archive_version_checksum",
                hashlib.md5(payload).hexdigest() == item["md5"],
                item["id"],
            )
            run.check(
                "version_one_release",
                archive["latestVersion"]["versionNumber"] == 1
                and item["publicationDate"] == "2018-07-28",
                item["publicationDate"],
            )
            with zipfile.ZipFile(io.BytesIO(payload)) as bundle:
                members.extend(
                    dict(archive=file["label"], member=x.filename, bytes=x.file_size)
                    for x in bundle.infolist()
                )
        path = run.data / "archive_members.csv"
        write_csv(path, members, ["archive", "member", "bytes"])
        run.output(path)
        run.record["metrics"] = dict(original_papers=22, source_effects=46)
        run.record["unresolved"] = [
            "Earliest SSRN roster and diagnostic classifications not verified",
            "Formal-publication contrast must not be called first disclosure",
        ]
        print(json.dumps(run.record["metrics"]))


if __name__ == "__main__":
    main()
