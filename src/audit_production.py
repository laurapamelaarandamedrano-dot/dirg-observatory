"""Production-data audit. Runs last; a failure blocks deployment.

Checks everything that is about to be published (data/public and site/) for:
  * rows or files flagged illustrative / development / restricted
  * personal-data patterns (CURP, RFC, e-mail, phone numbers)
  * fields that must never be public (permit-holder names, street addresses, coordinates)
  * precise point coordinates of infrastructure
  * sources whose redistribution status forbids publishing raw content
"""
from __future__ import annotations

import json
import re
import sys

import pandas as pd

from .common import PUBLIC, SITE, REPORTS, load_yaml, get_logger, write_json

log = get_logger("audit")
PATTERNS = {
    "curp": re.compile(r"\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b"),
    "rfc": re.compile(r"\b[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}\b"),
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "phone_mx": re.compile(r"(?<![\d.])(?:\+?52[\s-]?)?(?:\(?\d{2,3}\)?[\s-]?)\d{3,4}[\s-]\d{4}(?![\d.])"),
    "dms_coordinate": re.compile(r"\d{1,3}\s?°\s?\d{1,2}(?:[.,]\d+)?\s?['’′]\s?[NSOEW]"),
    "illustrative_marker": re.compile(r"ILLUSTRATIVE\s*/\s*DEVELOPMENT ONLY|\"release_flag\"\s*:\s*\"(?:illustrative|restricted)\"|,(?:illustrative|restricted)\s*$", re.M),
}
FORBIDDEN_COLUMNS = {"permisionario", "direccion", "pais_origen", "operator", "operador", "company", "empresa", "latitude", "longitude", "lat", "lon"}
ALLOWED_EMAIL_CONTEXT = set()   # none: the public layer should contain no e-mail addresses at all


def scan_text(name: str, text: str, findings: list):
    for key, pat in PATTERNS.items():
        for m in pat.finditer(text):
            findings.append({"file": name, "pattern": key, "match": m.group(0)[:60]})


def main() -> int:
    findings, problems = [], []
    REG = {s["id"]: s for s in load_yaml("sources.yaml")["sources"]}
    for f in sorted(PUBLIC.glob("*.csv")):
        df = pd.read_csv(f, dtype=str)
        bad_cols = FORBIDDEN_COLUMNS & {c.lower() for c in df.columns}
        if bad_cols:
            problems.append(f"{f.name}: forbidden columns {sorted(bad_cols)}")
        if "release_flag" in df.columns and (df.release_flag != "public").any():
            problems.append(f"{f.name}: rows not flagged public")
        scan_text(f.name, f.read_text(encoding="utf-8"), findings)
    payload = SITE / "data" / "observatory.json"
    if payload.exists():
        scan_text(payload.name, payload.read_text(encoding="utf-8"), findings)
        data = json.loads(payload.read_text(encoding="utf-8"))
        anchors = json.loads((SITE / "data" / "anchors.json").read_text())
        # infrastructure must only be located at state anchors
        for r in data.get("register", []):
            if any(k in r for k in ("lat", "lon", "latitude", "longitude", "address")):
                problems.append(f"register record {r.get('record_id')} carries location fields")
        if set(anchors) != {t["id"] for t in data["territories"]}:
            problems.append("anchors do not match territories")
    raw_files = list(SITE.rglob("*.xlsx")) + list(SITE.rglob("*.zip")) + [p for p in SITE.rglob("*.csv") if p.name.startswith(("cne_", "smn_"))]
    if raw_files:
        problems.append(f"raw source files inside site/: {[p.name for p in raw_files]}")
    # metadata_only / derived_only sources: no raw copies anywhere in the public layer
    for sid, s in REG.items():
        fname = (s.get("fetch") or {}).get("file")
        if s["redistribution"] != "raw_ok" and fname and ((PUBLIC / fname).exists() or (SITE / fname).exists()):
            problems.append(f"{sid}: raw file {fname} published despite redistribution={s['redistribution']}")
    real = [x for x in findings if x["pattern"] != "phone_mx" or not re.fullmatch(r"[\d\s-]+", x["match"]) or len(re.sub(r"\D", "", x["match"])) >= 10]
    for x in real:
        problems.append(f"{x['file']}: possible {x['pattern']}: {x['match']}")
    report = {"problems": problems, "files_scanned": len(list(PUBLIC.glob('*.csv'))) + 1, "status": "fail" if problems else "pass"}
    write_json(REPORTS / "production_audit.json", report)
    for p in problems:
        log.error(p)
    log.info("production audit: %s (%d problems)", report["status"], len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
