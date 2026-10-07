"""Shared, auditable file and acquisition operations for numbered study pipelines."""

import csv
import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
import threading
import urllib.parse
from pathlib import Path

from scripts import pilot

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows, fields):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def unique(rows, keys):
    values = [tuple(row[key] for key in keys) for row in rows]
    if any(any(x in (None, "") for x in row) for row in values):
        raise ValueError(f"Missing key: {keys}")
    if len(values) != len(set(values)):
        raise ValueError(f"Duplicate key: {keys}")


def fingerprint(path):
    path = Path(path)
    result = dict(
        path=str(path.relative_to(ROOT)), sha256=digest(path), bytes=path.stat().st_size
    )
    if path.suffix == ".csv" and "private-data" not in path.parts:
        result["rows"] = len(read_csv(path))
    return result


class Run:
    """A receipt records actual inputs, checks and outputs, including failed runs."""

    def __init__(self, study, stage, script, offline=False, *, data_dir=None):
        self.study, self.stage, self.offline = study, stage, offline
        self._input_paths = set()
        self._lock = threading.Lock()
        self._source_locks = {}
        self.data = (
            Path(data_dir) if data_dir else ROOT / "data/cohorts" / study / "pipeline"
        )
        self.cache = ROOT / "private-data/cohorts" / study / "pipeline"
        self.receipt_path = self.data / "receipts" / (stage + ".json")
        self.record = dict(
            schema_version=1,
            study=study,
            stage=stage,
            started_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            command=[sys.executable, *sys.argv],
            python=platform.python_version(),
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            inputs=[],
            outputs=[],
            code=[],
            parents=[],
            checks=[],
            sources=[],
            metrics={},
            unresolved=[],
            status="running",
        )
        for path in [Path(script), Path(__file__), ROOT / "scripts/pilot.py"]:
            self.record["code"].append(fingerprint(path.resolve()))

    def __enter__(self):
        write_json(self.receipt_path, self.record)
        return self

    def __exit__(self, kind, error, traceback):
        self.record["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        self.record["status"] = "failed" if kind else "complete"
        if error:
            self.record["error"] = f"{kind.__name__}: {error}"
        write_json(self.receipt_path, self.record)
        return False

    def input(self, path):
        path = Path(path)
        relative = str(path.relative_to(ROOT))
        with self._lock:
            if relative not in self._input_paths:
                self.record["inputs"].append(fingerprint(path))
                self._input_paths.add(relative)
        return path

    def output(self, path):
        self.record["outputs"].append(fingerprint(path))
        return path

    def check(self, name, passed, detail):
        self.record["checks"].append(
            dict(name=name, passed=bool(passed), detail=detail)
        )
        if not passed:
            raise ValueError(name + ": " + str(detail))

    def require(self, stage):
        path = self.data / "receipts" / (stage + ".json")
        verify_receipt(path)
        receipt = json.loads(path.read_text())
        self.record["parents"].append(fingerprint(path))
        for item in receipt["outputs"]:
            self.input(ROOT / item["path"])

    def fetch(self, url, category, json_response=True):
        with self._lock:
            lock = self._source_locks.setdefault(url, threading.Lock())
        with lock:
            return self._fetch_locked(url, category, json_response)

    def _fetch_locked(self, url, category, json_response):
        key = hashlib.sha256(url.encode()).hexdigest()
        suffix = ".json" if json_response else ".html"
        if not json_response and urllib.parse.urlparse(url).path.lower().endswith(
            ".pdf"
        ):
            suffix = ".pdf"
        if not json_response and "retmode=xml" in url:
            suffix = ".xml"
        path = self.cache / category / (key + suffix)
        sidecar = path.with_suffix(path.suffix + ".source.json")
        cached = path.exists()
        if cached:
            record = json.loads(sidecar.read_text())
            self.check(
                "cached_source_integrity",
                record["url"] == url and record["sha256"] == digest(path),
                str(path.relative_to(ROOT)),
            )
        elif self.offline:
            raise FileNotFoundError("Source is not cached: " + url)
        value = pilot.request(url, path, json_response=json_response)
        self.input(path)
        self.input(sidecar)
        record = json.loads(sidecar.read_text())
        self.record["sources"].append(
            dict(path=str(path.relative_to(ROOT)), cache_hit=cached, **record)
        )
        return value


def verify_receipt(path, visiting=None):
    visiting = set() if visiting is None else set(visiting)
    path = Path(path)
    if path.resolve() in visiting:
        raise ValueError("Cyclic receipt dependency: " + str(path))
    visiting.add(path.resolve())
    record = json.loads(Path(path).read_text())
    if record["status"] != "complete":
        raise ValueError("Upstream stage is incomplete: " + str(path))
    for item in (
        record["inputs"]
        + record["outputs"]
        + record["code"]
        + record.get("parents", [])
    ):
        file = ROOT / item["path"]
        if not file.exists() or digest(file) != item["sha256"]:
            raise ValueError("Stale or changed artifact: " + item["path"])
    for parent in record.get("parents", []):
        verify_receipt(ROOT / parent["path"], visiting)
    if not record["checks"] or not all(x["passed"] for x in record["checks"]):
        raise ValueError("Receipt has no passing checks: " + str(path))
    return record


def query(base, **params):
    return base + "?" + urllib.parse.urlencode(params)
