"""Acquire and inventory I4R sources without inferring error classifications."""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import datetime as dt
import email.utils
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pilot
from bs4 import BeautifulSoup

ROOT = pilot.ROOT
DATA = ROOT / "data/i4r"
CACHE = ROOT / "private-data/i4r"
CUTOFF = "2026-10-05"
CATALOGS = {
    "reports": "https://www.i4replication.org/reports",
    "papers": "https://www.i4replication.org/papers",
    "repec": "https://ideas.repec.org/s/zbw/i4rdps.html",
    "repec2": "https://ideas.repec.org/s/zbw/i4rdps2.html",
}
SOURCE_FIELDS = [
    "source_id",
    "collection",
    "catalog_url",
    "url",
    "title",
    "authors",
    "journal",
    "status",
]
DOCUMENT_FIELDS = [
    "source_id",
    "document_id",
    "name",
    "url",
    "format",
    "created_at",
    "modified_at",
    "date_meaning",
]


def write(name, rows, fields):
    pilot.write_csv(DATA / name, rows, fields)


def read(name):
    path = DATA / name
    return pilot.read_csv(path) if path.exists() else []


OSF_LOCK = threading.Lock()


def fetch(url, path, json_response=True):
    path = Path(path)
    host = urllib.parse.urlparse(url).hostname
    if path.exists():
        sidecar = path.with_suffix(path.suffix + ".source.json")
        if sidecar.exists():
            record = json.loads(sidecar.read_text())
            if record["url"] != url or record["sha256"] != pilot.sha256(
                path.read_bytes()
            ):
                raise ValueError("Cached response URL/hash mismatch: " + str(path))
        return pilot.request(url, path, json_response=json_response)
    if host not in {"api.osf.io", "api.openalex.org", "api.opencitations.net"}:
        return pilot.request(url, path, json_response=json_response)
    with OSF_LOCK:
        token = None
        if host == "api.osf.io":
            token = os.environ.get("OSF_TOKEN") or os.environ.get("OSF_API_TOKEN")
        elif host == "api.openalex.org":
            token = pilot.openalex_api_key()
        scope = "authenticated" if token else "anonymous"
        blocked = CACHE / (host + "_" + scope + "_retry_after.json")
        if blocked.exists() and time.time() < json.loads(blocked.read_text())["until"]:
            raise RuntimeError(
                f"{host} rate limit: resume after time in {blocked.name}"
            )
        headers = {"User-Agent": "sig-fault-i4r-research/1.0"}
        if token:
            headers["Authorization"] = "Bearer " + token
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers=headers), timeout=40
            ) as response:
                payload = response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                retry = exc.headers.get("Retry-After", "3600")
                try:
                    seconds = float(retry)
                except ValueError:
                    try:
                        seconds = max(
                            1,
                            email.utils.parsedate_to_datetime(retry).timestamp()
                            - time.time(),
                        )
                    except (TypeError, ValueError):
                        seconds = 3600
                CACHE.mkdir(parents=True, exist_ok=True)
                blocked.write_text(
                    json.dumps(
                        {"until": time.time() + seconds, "retry_after_seconds": seconds}
                    )
                )
            raise
        parsed = json.loads(payload) if json_response else payload
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        path.with_suffix(path.suffix + ".source.json").write_text(
            json.dumps(
                dict(
                    url=url,
                    retrieved_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                    sha256=pilot.sha256(payload),
                    bytes=len(payload),
                ),
                indent=2,
            )
            + "\n"
        )
        return parsed


def flight_array(content, key):
    for match in re.finditer(r"self\.__next_f\.push\((.*?)\)</script>", content):
        item = json.loads(match[1])
        if len(item) < 2 or not isinstance(item[1], str):
            continue
        text = item[1]
        marker = '"' + key + '":['
        if marker in text:
            start = text.index(marker) + len(key) + 3
            rows, _ = json.JSONDecoder().raw_decode(text[start:])
            return rows
    raise ValueError(
        f"No complete {key} array in catalog; do not use only visible cards"
    )


def catalog_records(contents):
    sources = {}
    for row in flight_array(contents["reports"], "reports"):
        # Slug identifies a catalog entry, not necessarily a distinct article/node.
        slug = row["slug"]["current"]
        sid = "report_" + hashlib.sha256(slug.encode()).hexdigest()[:12]
        sources[sid] = dict(
            source_id=sid,
            collection="reports",
            catalog_url=CATALOGS["reports"],
            url=row["reportUrl"],
            title=row["title"],
            authors="",
            journal=row["journal"],
            status=row.get("status", ""),
        )
    for row in flight_array(contents["papers"], "papers"):
        sid = "dp_" + str(row["number"]).zfill(3)
        sources[sid] = dict(
            source_id=sid,
            collection="discussion_papers",
            catalog_url=CATALOGS["papers"],
            url=f"https://ideas.repec.org/p/zbw/i4rdps/{row['number']}.html",
            title=row["title"],
            authors=row["authors"],
            journal="",
            status="listed",
        )
    for name in ["repec", "repec2"]:
        soup = BeautifulSoup(contents[name], "html.parser")
        for a in soup.find_all("a", href=True):
            match = re.fullmatch(r"/p/zbw/i4rdps/(\d+)\.html", a["href"])
            if match:
                sid = "dp_" + match[1].zfill(3)
                if sid not in sources:
                    sources[sid] = dict(
                        source_id=sid,
                        collection="discussion_papers",
                        catalog_url=CATALOGS[name],
                        url="https://ideas.repec.org" + a["href"],
                        title=a.get_text(" ", strip=True),
                        authors="",
                        journal="",
                        status="listed",
                    )
    return sorted(sources.values(), key=lambda row: row["source_id"])


def discover():
    contents = {}
    for name, url in CATALOGS.items():
        path = CACHE / (name + ".html")
        contents[name] = fetch(url, path, False).decode()
        sidecar = path.with_suffix(".html.source.json")
        if not sidecar.exists():
            sidecar.write_text(
                json.dumps(
                    dict(
                        url=url,
                        sha256=pilot.sha256(path.read_bytes()),
                        retrieved_at=dt.datetime.fromtimestamp(
                            path.stat().st_mtime, dt.timezone.utc
                        ).isoformat(),
                        bytes=path.stat().st_size,
                    ),
                    indent=2,
                )
                + "\n"
            )
    rows = catalog_records(contents)
    write("sources.csv", rows, SOURCE_FIELDS)
    print(
        "Catalog:",
        len(rows),
        "entries;",
        sum(r["collection"] == "reports" for r in rows),
        "report entries",
        flush=True,
    )


def osf_node(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname not in {"osf.io", "www.osf.io"}:
        return ""
    match = re.match(r"/([a-z0-9]{5,})(?:/.*)?$", parsed.path)
    return match[1] if match else ""


def acquire_source(row):
    sid = row["source_id"]
    folder = CACHE / "sources" / sid
    try:
        if row["collection"] == "discussion_papers":
            fetch(row["url"], folder / "landing.html", False)
        else:
            node = osf_node(row["url"])
            if not node:
                fetch(row["url"], folder / "landing.html", False)
                return sid, "non_osf_landing", ""
            fetch(f"https://api.osf.io/v2/nodes/{node}/", folder / "node.json")
            queue = [
                (
                    (
                        f"https://api.osf.io/v2/nodes/{node}/files/osfstorage/"
                        "?page[size]=100"
                    ),
                    "files",
                )
            ]
            seen = set()
            while queue:
                url, name = queue.pop(0)
                if url in seen:
                    continue
                seen.add(url)
                payload = fetch(url, folder / (name + ".json"))
                for item in payload["data"]:
                    if item["attributes"]["kind"] == "folder":
                        link = item["relationships"]["files"]["links"]["related"][
                            "href"
                        ]
                        queue.append((link, "folder_" + item["id"]))
                if payload.get("links", {}).get("next"):
                    link = payload["links"]["next"]
                    if isinstance(link, dict):
                        link = link["href"]
                    queue.append((link, name + "_next"))
        return sid, "retrieved", ""
    except Exception as exc:
        return sid, "failed", str(exc)[:250]


def acquire(workers=4):
    outcomes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for i, result in enumerate(pool.map(acquire_source, read("sources.csv")), 1):
            outcomes.append(dict(zip(["source_id", "status", "detail"], result)))
            if i % 25 == 0:
                print("Source metadata:", i, flush=True)
    write("retrieval.csv", outcomes, ["source_id", "status", "detail"])
    print(
        "Source retrieval failures:",
        sum(r["status"] == "failed" for r in outcomes),
        flush=True,
    )


def related_url(item, name):
    link = item.get("relationships", {}).get(name, {}).get("links", {}).get("related")
    return link.get("href", "") if isinstance(link, dict) else link or ""


def expand_repositories(source_ids=()):
    known = {}
    for sidecar in (CACHE / "sources").glob("*/*.source.json"):
        record = json.loads(sidecar.read_text())
        known[record["url"]] = Path(str(sidecar).removesuffix(".source.json"))
    present = {r["source_id"] for r in read("documents.csv") if r["format"] == "pdf"}
    chosen = [
        r
        for r in read("sources.csv")
        if r["collection"] == "reports"
        and osf_node(r["url"])
        and (r["source_id"] in source_ids if source_ids else True)
    ]
    chosen.sort(key=lambda r: (r["source_id"] in present, r["source_id"]))
    extra = {r["document_id"]: r for r in read("repository_documents.csv")}
    logs = {(r["source_id"], r["url"]): r for r in read("repository_queries.csv")}
    for source in chosen:
        sid, root = source["source_id"], osf_node(source["url"])
        queue = [
            (f"https://api.osf.io/v2/nodes/{root}/files/?page[size]=100", "providers"),
            (
                f"https://api.osf.io/v2/nodes/{root}/children/?page[size]=100",
                "children",
            ),
        ]
        seen = set()
        while queue:
            url, kind = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)
            path = known.get(
                url,
                CACHE
                / "repositories"
                / (hashlib.sha256(url.encode()).hexdigest() + ".json"),
            )
            log = dict(
                source_id=sid, url=url, query_kind=kind, status="", items=0, detail=""
            )
            logs[sid, url] = log
            try:
                payload = fetch(url, path)
                if not isinstance(payload.get("data"), list):
                    raise ValueError("Expected OSF relationship collection")
                log.update(status="retrieved", items=len(payload["data"]))
                for item in payload["data"]:
                    if kind == "children":
                        for relationship, next_kind in [
                            ("files", "providers"),
                            ("children", "children"),
                        ]:
                            link = related_url(item, relationship)
                            if link:
                                queue.append(
                                    (
                                        link
                                        + ("&" if "?" in link else "?")
                                        + "page[size]=100",
                                        next_kind,
                                    )
                                )
                        continue
                    attr = item.get("attributes", {})
                    if attr.get("kind") == "folder":
                        link = related_url(item, "files")
                        if link:
                            queue.append(
                                (
                                    link
                                    + ("&" if "?" in link else "?")
                                    + "page[size]=100",
                                    "files",
                                )
                            )
                    elif attr.get("kind") == "file":
                        fid = item["id"]
                        if not re.fullmatch(r"[A-Za-z0-9_]+", fid):
                            fid = hashlib.sha256(fid.encode()).hexdigest()[:24]
                        did = sid + "_" + fid
                        extra[did] = dict(
                            source_id=sid,
                            document_id=did,
                            name=attr["name"],
                            url=item["links"].get("download", ""),
                            format=Path(attr["name"]).suffix.lower().lstrip("."),
                            created_at=attr.get("date_created", ""),
                            modified_at=attr.get("date_modified", ""),
                            date_meaning=(
                                "Repository upload/modification; "
                                "not established public disclosure"
                            ),
                        )
                link = payload.get("links", {}).get("next")
                if isinstance(link, dict):
                    link = link.get("href")
                if link:
                    if link in seen:
                        raise ValueError(
                            "Pagination cycle: repository listing incomplete"
                        )
                    queue.append((link, kind))
            except Exception as exc:
                log.update(status="failed", detail=str(exc)[:250])
                if "429" in log["detail"] or "rate limit" in log["detail"]:
                    write(
                        "repository_documents.csv",
                        list(extra.values()),
                        DOCUMENT_FIELDS,
                    )
                    write(
                        "repository_queries.csv",
                        list(logs.values()),
                        ["source_id", "url", "query_kind", "status", "items", "detail"],
                    )
                    print("Repository expansion paused at rate limit", flush=True)
                    return
        print("Expanded repository:", sid, "queries:", len(seen), flush=True)
    write("repository_documents.csv", list(extra.values()), DOCUMENT_FIELDS)
    write(
        "repository_queries.csv",
        list(logs.values()),
        ["source_id", "url", "query_kind", "status", "items", "detail"],
    )


def inventory():
    documents, metadata, links = [], [], []
    for row in read("sources.csv"):
        sid = row["source_id"]
        folder = CACHE / "sources" / sid
        meta = dict(
            source_id=sid,
            abstract="",
            stated_date="",
            date_meaning="",
            original_title_hint="",
        )
        if (
            row["collection"] == "discussion_papers"
            and (folder / "landing.html").exists()
        ):
            soup = BeautifulSoup((folder / "landing.html").read_text(), "html.parser")
            section = soup.find(id="abstract-body")
            meta["abstract"] = section.get_text(" ", strip=True) if section else ""
            tags = {
                t.get("name", "").lower(): t.get("content", "")
                for t in soup.find_all("meta")
            }
            meta["stated_date"] = tags.get(
                "citation_publication_date", tags.get("citation_date", "")
            )
            meta["date_meaning"] = (
                "RePEc current record publication date; first disclosure unverified"
            )
            for i, tag in enumerate(soup.find_all("input", attrs={"name": "url"})):
                url = tag.get("value", "")
                if url.startswith("http"):
                    documents.append(
                        dict(
                            source_id=sid,
                            document_id=sid + "_download_" + str(i),
                            name="linked_fulltext",
                            url=url,
                            format="pdf" if ".pdf" in url.lower() else "unknown",
                            created_at="",
                            modified_at="",
                            date_meaning="No public disclosure date inferred",
                        )
                    )
        elif (folder / "node.json").exists():
            node = json.loads((folder / "node.json").read_text())["data"]["attributes"]
            meta["abstract"] = node.get("description") or ""
            meta["stated_date"] = node["date_created"]
            meta["date_meaning"] = (
                "OSF node creation; not established public disclosure"
            )
            meta["original_title_hint"] = row["title"]
            for url in re.findall(r"https?://[^\s<>]+", meta["abstract"]):
                url = url.rstrip(".,;)")
                match = re.search(
                    r"(?:/i4rdps/|/paper/zbwi4rdps/)(\d+)(?:\.html?|/|$)", url
                )
                links.append(
                    dict(
                        source_id=sid,
                        url=url,
                        related_source_id="dp_" + match[1].zfill(3) if match else "",
                        relation="explicit_link_in_OSF_description",
                    )
                )
            for p in sorted(folder.glob("*.json")):
                if p.name.endswith(".source.json") or p.name == "node.json":
                    continue
                payload = json.loads(p.read_text())
                for item in payload.get("data", []):
                    attr = item["attributes"]
                    if attr["kind"] != "file":
                        continue
                    name = attr["name"]
                    suffix = Path(name).suffix.lower().lstrip(".")
                    documents.append(
                        dict(
                            source_id=sid,
                            document_id=sid + "_" + item["id"],
                            name=name,
                            url=item["links"].get("download", ""),
                            format=suffix,
                            created_at=attr.get("date_created", ""),
                            modified_at=attr.get("date_modified", ""),
                            date_meaning=(
                                "File upload/modification, not established public"
                                " disclosure"
                            ),
                        )
                    )
        elif row["url"].lower().split("?")[0].endswith(".pdf"):
            url = row["url"]
            if url.startswith("https://github.com/") and "/blob/" in url:
                url = url.replace(
                    "https://github.com/", "https://raw.githubusercontent.com/"
                ).replace("/blob/", "/", 1)
            documents.append(
                dict(
                    source_id=sid,
                    document_id=sid + "_download_0",
                    name=Path(urllib.parse.urlparse(url).path).name,
                    url=url,
                    format="pdf",
                    created_at="",
                    modified_at="",
                    date_meaning="No disclosure date inferred from URL",
                )
            )
        metadata.append(meta)
    (CACHE / "extracted_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    )
    public_metadata = [
        {k: v for k, v in r.items() if k != "abstract"} for r in metadata
    ]
    write("source_metadata.csv", public_metadata, list(public_metadata[0]))
    known_ids = {r["document_id"] for r in documents}
    documents += [
        r for r in read("repository_documents.csv") if r["document_id"] not in known_ids
    ]
    write("documents.csv", documents, DOCUMENT_FIELDS)
    write(
        "source_links.csv", links, ["source_id", "url", "related_source_id", "relation"]
    )
    print(
        "Documents:",
        len(documents),
        "PDFs:",
        sum(r["format"] == "pdf" for r in documents),
        flush=True,
    )


def acquire_document(row):
    path = CACHE / "documents" / (row["document_id"] + "." + (row["format"] or "bin"))
    try:
        payload = fetch(row["url"], path, False)
        is_pdf = payload.startswith(b"%PDF")
        if row["format"] == "pdf" or is_pdf:
            if not is_pdf:
                raise ValueError("Response is not a PDF")
            text_path = path.with_suffix(".txt")
            if not text_path.exists():
                subprocess.run(
                    ["pdftotext", "-layout", str(path), str(text_path)],
                    check=True,
                    capture_output=True,
                )
        elif row["format"] == "docx":
            namespace = {
                "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            }
            paragraphs = []
            with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                for name in [
                    "word/document.xml",
                    "word/footnotes.xml",
                    "word/endnotes.xml",
                ]:
                    if name not in archive.namelist():
                        continue
                    tree = ET.fromstring(archive.read(name))
                    paragraphs.extend(
                        "".join(
                            node.text or ""
                            for node in paragraph.findall(".//w:t", namespace)
                        )
                        for paragraph in tree.findall(".//w:p", namespace)
                    )
            path.with_suffix(".txt").write_text("\n".join(paragraphs) + "\n")
        return dict(
            document_id=row["document_id"],
            status="retrieved",
            detail="",
            sha256=pilot.sha256(payload),
        )
    except Exception as exc:
        return dict(
            document_id=row["document_id"],
            status="failed",
            detail=str(exc)[:250],
            sha256="",
        )


def acquire_document_group(rows):
    def local_path(row):
        return (
            CACHE / "documents" / (row["document_id"] + "." + (row["format"] or "bin"))
        )

    representative = next((r for r in rows if local_path(r).exists()), rows[0])
    result = acquire_document(representative)
    if result["status"] == "retrieved":
        original = local_path(representative)
        for row in rows:
            target = local_path(row)
            if target == original:
                continue
            for old, new in [
                (original, target),
                (
                    original.with_suffix(original.suffix + ".source.json"),
                    target.with_suffix(target.suffix + ".source.json"),
                ),
                (original.with_suffix(".txt"), target.with_suffix(".txt")),
            ]:
                if old.exists():
                    shutil.copy2(old, new)
    return [result | {"document_id": r["document_id"]} for r in rows]


def documents(workers=4):
    rows = [
        r
        for r in read("documents.csv")
        if r["format"]
        in {"pdf", "docx", "txt", "tex", "rmd", "csv", "xlsx", "", "unknown"}
    ]
    grouped = collections.defaultdict(list)
    for row in rows:
        grouped[(row["url"], row["format"])].append(row)
    outcomes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for i, result in enumerate(
            pool.map(acquire_document_group, grouped.values()), 1
        ):
            outcomes.extend(result)
            if i % 25 == 0:
                print("Distinct downloads:", i, "/", len(grouped), flush=True)
    write(
        "document_retrieval.csv",
        outcomes,
        ["document_id", "status", "detail", "sha256"],
    )


ARCHIVE_FIELDS = [
    "source_id",
    "archive_document_id",
    "member_id",
    "member_path",
    "format",
    "uncompressed_bytes",
    "crc32",
    "status",
    "local_path",
    "sha256",
    "archive_sha256",
]


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_archive(url, path, max_bytes):
    sidecar = path.with_suffix(path.suffix + ".source.json")
    if path.exists():
        origin = json.loads(sidecar.read_text())
        if origin["url"] != url or origin["sha256"] != file_sha256(path):
            raise ValueError("Cached archive URL/hash mismatch")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".part")
    request = urllib.request.Request(
        url, headers={"User-Agent": "sig-fault-i4r-research/1.0"}
    )
    digest, size = hashlib.sha256(), 0
    try:
        with urllib.request.urlopen(request, timeout=60) as response, partial.open(
            "wb"
        ) as stream:
            declared = response.headers.get("Content-Length")
            if declared and int(declared) > max_bytes:
                raise ValueError("archive_size_limit")
            while chunk := response.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise ValueError("archive_size_limit")
                digest.update(chunk)
                stream.write(chunk)
        os.replace(partial, path)
        sidecar.write_text(
            json.dumps(
                dict(
                    url=url,
                    retrieved_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                    sha256=digest.hexdigest(),
                    bytes=size,
                ),
                indent=2,
            )
            + "\n"
        )
        return path
    finally:
        partial.unlink(missing_ok=True)


def archive_members(row, payload, member_limit=30 * 1024 * 1024):
    records = []
    archive_hash = (
        file_sha256(payload) if isinstance(payload, Path) else pilot.sha256(payload)
    )
    archive_source = payload if isinstance(payload, Path) else io.BytesIO(payload)
    with zipfile.ZipFile(archive_source) as archive:
        for index, info in enumerate(archive.infolist()):
            if info.is_dir():
                continue
            suffix = Path(info.filename).suffix.lower().lstrip(".")
            mid = (
                row["document_id"]
                + "_member_"
                + hashlib.sha256(
                    (str(index) + ":" + info.filename).encode()
                ).hexdigest()[:12]
            )
            record = dict(
                source_id=row["source_id"],
                archive_document_id=row["document_id"],
                member_id=mid,
                member_path=info.filename,
                format=suffix,
                uncompressed_bytes=info.file_size,
                crc32=f"{info.CRC:08x}",
                status="inventory_only",
                local_path="",
                sha256="",
                archive_sha256=archive_hash,
            )
            records.append(record)
            if "__MACOSX" in Path(info.filename).parts or Path(
                info.filename
            ).name.startswith("._"):
                record["status"] = "metadata_sidecar"
                continue
            if suffix == "zip":
                record["status"] = "nested_archive_unresolved"
            if (
                suffix
                not in {
                    "pdf",
                    "docx",
                    "txt",
                    "md",
                    "html",
                    "",
                }
                or "__MACOSX" in Path(info.filename).parts
                or Path(info.filename).name.startswith("._")
            ):
                continue
            if info.file_size > member_limit:
                record["status"] = "member_size_limit"
                continue
            try:
                data = archive.read(info)
                if not suffix:
                    if not data.startswith(b"%PDF"):
                        continue
                    suffix = "pdf"
                    record["format"] = suffix
                path = CACHE / "documents" / (mid + "." + suffix)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                record.update(
                    status="extracted",
                    local_path=str(path.relative_to(ROOT)),
                    sha256=pilot.sha256(data),
                )
                if suffix == "pdf":
                    if not data.startswith(b"%PDF"):
                        raise ValueError("Archive member is not a PDF")
                    subprocess.run(
                        [
                            "pdftotext",
                            "-layout",
                            str(path),
                            str(path.with_suffix(".txt")),
                        ],
                        check=True,
                        capture_output=True,
                    )
            except Exception as exc:
                record["status"] = "extraction_failed: " + str(exc)[:180]
    return records


def archives(workers=4, max_archive_mb=300):
    sizes = {}
    for path in (CACHE / "sources").glob("*/*.json"):
        if path.name.endswith(".source.json"):
            continue
        data = json.loads(path.read_text()).get("data")
        if isinstance(data, list):
            for item in data:
                if item.get("attributes", {}).get("kind") == "file":
                    sizes[item["id"]] = item["attributes"].get("size")
    rows = [r for r in read("documents.csv") if r["format"] == "zip"]

    def acquire_archive(row):
        size = sizes.get(row["document_id"].rsplit("_", 1)[-1])
        status = dict(
            archive_document_id=row["document_id"], status="", detail="", members=0
        )
        archive_path = CACHE / "archives" / (row["document_id"] + ".zip")
        if (
            size is not None
            and size > max_archive_mb * 1024 * 1024
            and not archive_path.exists()
        ):
            status.update(status="archive_size_limit", detail=str(size))
            return status, []
        try:
            path = fetch_archive(
                row["url"],
                CACHE / "archives" / (row["document_id"] + ".zip"),
                max_archive_mb * 1024 * 1024,
            )
            members = archive_members(row, path)
            status.update(status="inventoried", members=len(members))
            return status, members
        except Exception as exc:
            status.update(
                status=(
                    "archive_size_limit"
                    if str(exc) == "archive_size_limit"
                    else "failed"
                ),
                detail=str(exc)[:250],
            )
            return status, []

    statuses, members = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for i, (status, extracted) in enumerate(pool.map(acquire_archive, rows), 1):
            statuses.append(status)
            members.extend(extracted)
            print("Archives:", i, "/", len(rows), status["status"], flush=True)
    write(
        "archive_retrieval.csv",
        statuses,
        ["archive_document_id", "status", "detail", "members"],
    )
    write("archive_members.csv", members, ARCHIVE_FIELDS)


def manifest():
    rows = []
    for p in sorted(CACHE.rglob("*.source.json")):
        record = json.loads(p.read_text())
        rows.append(
            dict(path=str(p.relative_to(ROOT)).removesuffix(".source.json"), **record)
        )
    write(
        "source_manifest.csv", rows, ["path", "url", "retrieved_at", "sha256", "bytes"]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "discover",
            "fetch",
            "inventory",
            "documents",
            "archives",
            "expand",
            "manifest",
        ],
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--max-archive-mb", type=int, default=300)
    parser.add_argument("--source-id", action="append", default=[])
    args = parser.parse_args()
    if args.command == "expand":
        expand_repositories(args.source_id)
    elif args.command == "archives":
        archives(args.workers, args.max_archive_mb)
    elif args.command in {"fetch", "documents"}:
        {"fetch": acquire, "documents": documents}[args.command](args.workers)
    else:
        {"discover": discover, "inventory": inventory, "manifest": manifest}[
            args.command
        ]()
