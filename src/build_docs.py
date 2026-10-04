"""Generate docs/DATA_DICTIONARY.md and docs/SOURCES.md from config (so they can never drift)."""
from __future__ import annotations

import csv

from .common import DOCS, RAW, load_yaml, get_logger

log = get_logger("docs")


def data_dictionary() -> str:
    V = load_yaml("variables.yaml")
    L = ["# Data dictionary", "", "_Generated from `config/variables.yaml` by `src/build_docs.py`. Do not edit by hand._", "",
         "## Observation schema (`data/public/observations.csv`)", "",
         "| Field | Type | Description |", "|---|---|---|",
         "| obs_id | string | First 12 hex characters of SHA-1(territory_id, year, variable_id); stable across runs |",
         "| territory_id | string | INEGI state code (CVE_ENT), two digits |",
         "| territory_level | enum | `state` in this release (`municipality`, `aquifer`, `basin`, `region` reserved) |",
         "| territory_name | string | Short official state name |",
         "| year | int | 2020–2027 |",
         "| variable_id | string | Key into the variable list below |",
         "| value | float, empty | Empty means unknown. Never zero-filled |",
         "| unit | string | Canonical unit for the variable |",
         "| epistemic_status | enum | observed, administrative, documentary, geospatial, derived, estimated, modelled, hypothesized, unknown |",
         "| source_id | string | Pipe-separated keys into `sources.csv` |",
         "| method_id | string | Key into `methods.csv` (method = the variable definition) |",
         "| ci_low, ci_high | float, empty | Source-reported intervals when they exist (none in this release) |",
         "| reference_date | string | Period or date the value describes |",
         "| vintage_year | int, empty | Edition year of the underlying source, used for recency penalties |",
         "| release_flag | enum | `public` only in the public layer; `illustrative` and `restricted` are blocked by the production audit |",
         "| qa_flags | string | Pipe-separated flags, e.g. PARTIAL_YEAR, CARRIED_FORWARD, UNDATED_VINTAGE, REGISTER_ABSENCE |",
         "", "## Index results (`data/public/index_results.csv`)", "",
         "One row per territory × year × scenario: `value` (composite 0–100), `n_pillars`, `flags`, `rank`, pillar scores `W E D V`; "
         "baseline rows add Monte Carlo `mc_low`, `mc_high`, `rank_p05`, `rank_median`, `rank_p95`.", "",
         "## Coverage (`data/public/coverage.csv`)", "",
         "`coverage` (0–1), `coverage_W…V`, `tier` (high / moderate / limited / insufficient), and counts of index indicators by ledger class (`n_known`, `n_derived`, `n_estimated`, `n_modelled`, `n_unknown`).", "",
         "## Variables", ""]
    for p, lab in V["pillars"].items():
        rows = [(k, v) for k, v in V["variables"].items() if v["pillar"] == p]
        if not rows:
            continue
        L += [f"### {p} · {lab['en']} / {lab['es']}", "", "| id | in index | direction | transform | unit | default status | sources | definition |", "|---|---|---|---|---|---|---|---|"]
        for k, v in rows:
            L.append(f"| `{k}` | {'yes' if v['in_index'] else 'no'} | {v['direction']:+d} | {v['transform']} | {v['unit']} | {v['epistemic_status']} | {', '.join(v['source_ids'])} | {v['definition']['en']} |")
        L.append("")
    return "\n".join(L) + "\n"


def sources() -> str:
    R = load_yaml("sources.yaml")
    man = {}
    if (RAW / "MANIFEST.csv").exists():
        with open(RAW / "MANIFEST.csv", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                man.setdefault(row["source_id"], []).append(row)
    L = ["# Source registry", "", "_Generated from `config/sources.yaml` and `data/raw/MANIFEST.csv` by `src/build_docs.py`._", "",
         "Publicly accessible does not mean freely redistributable. `redistribution` states what this project publishes for each source: "
         "`raw_ok` (raw file could be redistributed, still fetched by script rather than committed), `derived_only` (only aggregates), `metadata_only` (citation and transformation notes only).", "",
         "**Acquisition note for release 0.1.0.** The cloud environment that ran the pipeline could not reach `.gob.mx` hosts. "
         "Official files were therefore downloaded from the official URLs below in a desktop browser session on 2026-10-04 and their SHA-256 checksums recorded. "
         "`python -m src.ingest --fetch` downloads the same URLs directly; a checksum mismatch means the source changed upstream and must be logged in CHANGELOG.md.", ""]
    for s in R["sources"]:
        L += [f"## {s['id']} · {s['title']}", "",
              f"- **Institution / author:** {s['institution']}",
              f"- **URL:** {s['url_landing']}" + (f" (secondary: {s['url_secondary']})" if s.get("url_secondary") else ""),
              f"- **Publication date:** {s.get('publication_date', '')}",
              f"- **Access date:** {s.get('access_date', '')}",
              f"- **License / terms:** {s.get('license', '')}",
              f"- **Dataset type:** {s.get('dataset_type', '')}",
              f"- **Geographic coverage:** {s.get('geographic_coverage', '')}",
              f"- **Temporal coverage:** {s.get('temporal_coverage', '')}",
              f"- **Redistribution:** `{s.get('redistribution', '')}`"]
        if s.get("notes"):
            L.append(f"- **Methodological notes:** {s['notes']}")
        for m in man.get(s["id"], []):
            L.append(f"- **File:** `{m['file']}` · {int(m['bytes']):,} bytes · SHA-256 `{m['sha256']}`")
        L.append("")
    return "\n".join(L) + "\n"


def main():
    DOCS.mkdir(exist_ok=True)
    (DOCS / "DATA_DICTIONARY.md").write_text(data_dictionary(), encoding="utf-8")
    (DOCS / "SOURCES.md").write_text(sources(), encoding="utf-8")
    log.info("docs generated")


if __name__ == "__main__":
    main()
