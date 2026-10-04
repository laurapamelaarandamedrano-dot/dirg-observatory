"""Stage 1: acquire raw source files and record provenance.

Usage:
    python -m src.ingest            # verify files already in data/raw against MANIFEST.csv
    python -m src.ingest --fetch    # download every source with a fetch URL, then write MANIFEST.csv

Raw files are never edited. Each file's SHA-256, size, URL and access date are written to
data/raw/MANIFEST.csv, which IS committed, so a later run can prove it used the same bytes.
"""
from __future__ import annotations

import argparse
import csv
import sys
import urllib.request
from datetime import date

from .common import RAW, GEO, load_yaml, sha256, get_logger

log = get_logger("ingest")
MANIFEST = RAW / "MANIFEST.csv"
FIELDS = ["file", "source_id", "url", "bytes", "sha256", "access_date", "acquisition_note"]

# Files that are vendored in geo/ rather than data/raw/
GEO_FILES = {"world_land_110m.topo.json", "ne_10m_admin1_mexico.geojson"}


def _targets():
    reg = load_yaml("sources.yaml")
    for s in reg["sources"]:
        f = s.get("fetch")
        if not f:
            continue
        if "file" in f:
            yield s["id"], f["url"], f["file"], s.get("access_date")
        for spec in f.get("files", []):
            remote, local = [x.strip() for x in spec.split("->")]
            yield s["id"], f["url"].rstrip("/") + "/" + remote, local, s.get("access_date")


def fetch(timeout: int = 120) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for sid, url, local, _ in _targets():
        if local in GEO_FILES or local == "ne_10m_admin_1_states_provinces.geojson":
            continue  # geometry is vendored; see geo/README
        dest = RAW / local
        log.info("fetching %s -> %s", url, dest.name)
        req = urllib.request.Request(url, headers={"User-Agent": "dirgo-observatory/0.1 (research)"})
        with urllib.request.urlopen(req, timeout=timeout) as r, open(dest, "wb") as out:
            out.write(r.read())


def read_manifest() -> dict[str, dict]:
    if not MANIFEST.exists():
        return {}
    with open(MANIFEST, newline="", encoding="utf-8") as fh:
        return {row["file"]: row for row in csv.DictReader(fh)}


def write_manifest(note: str) -> list[dict]:
    old = read_manifest()
    rows = []
    for sid, url, local, access in _targets():
        path = (GEO / local) if local in GEO_FILES else (RAW / local)
        if local == "ne_10m_admin_1_states_provinces.geojson":
            path = GEO / "ne_10m_admin1_mexico.geojson"
            local = path.name
        if not path.exists():
            log.warning("missing raw file for %s: %s", sid, local)
            continue
        prev = old.get(local, {})
        digest = sha256(path)
        same = prev.get("sha256") == digest
        rows.append({
            "file": local, "source_id": sid, "url": url, "bytes": path.stat().st_size,
            "sha256": digest,
            "access_date": prev.get("access_date") if same and prev.get("access_date") else (access or date.today().isoformat()),
            "acquisition_note": prev.get("acquisition_note") if same and prev.get("acquisition_note") else note,
        })
    with open(MANIFEST, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    log.info("manifest written: %d files", len(rows))
    return rows


def verify() -> list[str]:
    """Return a list of problems (empty if every manifest entry matches the bytes on disk)."""
    problems = []
    man = read_manifest()
    if not man:
        return ["MANIFEST.csv missing"]
    for name, row in man.items():
        path = GEO / name if name in GEO_FILES else RAW / name
        if not path.exists():
            problems.append(f"missing: {name}")
        elif sha256(path) != row["sha256"]:
            problems.append(f"checksum changed: {name} (source updated upstream? re-run with --refresh and record in CHANGELOG)")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download from official URLs")
    ap.add_argument("--refresh", action="store_true", help="rewrite MANIFEST.csv from files on disk")
    a = ap.parse_args(argv)
    if a.fetch:
        fetch()
        write_manifest("fetched by src/ingest.py --fetch")
        return 0
    if a.refresh or not MANIFEST.exists():
        write_manifest("downloaded from the official URL via a desktop browser session (see docs/SOURCES.md)")
        return 0
    probs = verify()
    for p in probs:
        log.error(p)
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
