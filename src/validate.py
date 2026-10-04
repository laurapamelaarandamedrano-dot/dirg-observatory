"""Stage 5: automated data-quality checks and the quality report.

Writes reports/quality_report.json and reports/QUALITY_REPORT.md. Exits non-zero if any
check with severity `error` fails. Every number in the report is computed here, from the files.
"""
from __future__ import annotations

import json
import sys
from datetime import date

import geopandas as gpd
import numpy as np
import pandas as pd

from .common import PROCESSED, INTERIM, REPORTS, GEO, STATES, load_yaml, get_logger, write_json

log = get_logger("validate")
VARS = load_yaml("variables.yaml")["variables"]
REG = {s["id"]: s for s in load_yaml("sources.yaml")["sources"]}
CFG = load_yaml("scenarios.yaml")


def check(results, name, ok, severity, detail, count=None):
    results.append({"check": name, "status": "pass" if ok else ("fail" if severity == "error" else "warn"),
                    "severity": severity, "detail": detail, "count": count})


def main() -> int:
    obs = pd.read_csv(PROCESSED / "observations.csv", dtype={"territory_id": str, "qa_flags": str})
    res_idx = pd.read_csv(PROCESSED / "index_results.csv", dtype={"territory_id": str})
    norm = pd.read_csv(PROCESSED / "normalized_indicators.csv", dtype={"territory_id": str})
    cov = pd.read_csv(PROCESSED / "coverage.csv", dtype={"territory_id": str})
    weights = pd.read_csv(PROCESSED / "indicator_weights.csv", dtype={"territory_id": str})
    R = []

    dup = obs.duplicated(["territory_id", "year", "variable_id"]).sum()
    check(R, "duplicate_observations", dup == 0, "error", "territory × year × variable must be unique", int(dup))

    bad_ids = set(obs.territory_id) - set(STATES)
    check(R, "geographic_identifiers", not bad_ids, "error", f"unknown territory ids: {sorted(bad_ids)}", len(bad_ids))

    unk_vars = set(obs.variable_id) - set(VARS)
    check(R, "variables_registered", not unk_vars, "error", f"variables not in config/variables.yaml: {sorted(unk_vars)}", len(unk_vars))

    units = obs.groupby("variable_id").unit.nunique()
    mism = [v for v in units.index if units[v] != 1 or obs.loc[obs.variable_id == v, "unit"].iloc[0] != VARS[v]["unit"]]
    check(R, "units_consistent", not mism, "error", f"variables with inconsistent units: {mism}", len(mism))

    out_of_range = []
    for v, g in obs.dropna(subset=["value"]).groupby("variable_id"):
        lo, hi = VARS[v]["plausible_range"]
        n = int(((g.value < lo) | (g.value > hi)).sum())
        if n:
            out_of_range.append(f"{v}: {n}")
    check(R, "impossible_values", not out_of_range, "error", "values outside plausible_range: " + "; ".join(out_of_range), len(out_of_range))

    expected = len(STATES) * len(CFG["years"])
    missing_years = {}
    for v, g in obs.groupby("variable_id"):
        have = g.dropna(subset=["value"]).groupby("year").size()
        miss = [int(y) for y in CFG["years"] if have.get(y, 0) == 0]
        if miss:
            missing_years[v] = miss
        if len(g) != expected:
            check(R, f"row_completeness:{v}", False, "error", f"{len(g)} rows, expected {expected}", len(g))
    check(R, "missing_years", True, "info", "years with no value at all, by variable: " + json.dumps(missing_years), sum(len(x) for x in missing_years.values()))

    unknown_with_value = obs[(obs.epistemic_status == "unknown") & obs.value.notna()]
    check(R, "unknown_never_has_value", unknown_with_value.empty, "error", "rows marked unknown must have an empty value", len(unknown_with_value))
    value_without_status = obs[obs.value.isna() & (obs.epistemic_status != "unknown")]
    check(R, "missing_never_zero", value_without_status.empty, "error", "empty values must be marked unknown (never silently zero)", len(value_without_status))

    outliers = []
    for (v, y), g in obs.dropna(subset=["value"]).groupby(["variable_id", "year"]):
        x = g.value.to_numpy()
        med = np.median(x); mad = np.median(np.abs(x - med))
        if mad == 0:
            continue
        z = 0.6745 * (x - med) / mad
        for tid, zz, val in zip(g.territory_id, z, x):
            if abs(zz) > 5:
                outliers.append({"variable": v, "year": int(y), "territory": STATES[tid][1], "value": float(val), "robust_z": round(float(zz), 1)})
    check(R, "outliers_flagged", True, "info", "robust z > 5 within variable-year (flagged for review, NOT removed)", len(outliers))

    src_ids = {s for ids in obs.source_id.dropna() for s in str(ids).split("|")}
    missing_src = src_ids - set(REG)
    check(R, "source_registry_match", not missing_src, "error", f"source ids not in registry: {sorted(missing_src)}", len(missing_src))
    cfg_src = {s for v in VARS.values() for s in v["source_ids"]} - set(REG)
    check(R, "variable_sources_registered", not cfg_src, "error", f"variable source ids not in registry: {sorted(cfg_src)}", len(cfg_src))

    meta_fields = ["institution", "title", "url_landing", "access_date", "license", "dataset_type", "redistribution"]
    meta_missing = [f"{sid}.{f}" for sid, s in REG.items() for f in meta_fields if not s.get(f)]
    check(R, "source_metadata_complete", not meta_missing, "error", f"missing: {meta_missing}", len(meta_missing))
    var_meta = [k for k, v in VARS.items() if not (v.get("definition", {}).get("en") and v.get("definition", {}).get("es"))]
    check(R, "variable_metadata_complete", not var_meta, "error", f"variables lacking EN/ES definitions: {var_meta}", len(var_meta))

    num = norm.drop(columns=["territory_id", "year"])
    bad_norm = int(((num < -1e-9) | (num > 100 + 1e-9)).sum().sum())
    check(R, "normalization_range", bad_norm == 0, "error", "normalized indicators must lie in [0, 100]", bad_norm)
    bad_comp = int(((res_idx.value < -1e-9) | (res_idx.value > 100 + 1e-9)).sum())
    check(R, "composite_range", bad_comp == 0, "error", "composite values must lie in [0, 100]", bad_comp)

    illustrative = int((obs.release_flag != "public").sum())
    check(R, "no_illustrative_rows", illustrative == 0, "error", "observations not flagged public (illustrative/restricted)", illustrative)

    g = gpd.read_file(GEO / "ne_10m_admin1_mexico.geojson")
    invalid = int((~g.geometry.is_valid).sum())
    minx, miny, maxx, maxy = g.total_bounds
    in_bounds = -119 < minx and maxx < -86 and 14 < miny and maxy < 33.5
    check(R, "geometry_valid", invalid == 0, "warn", f"invalid geometries (repaired with make_valid when used): {invalid}", invalid)
    check(R, "coordinates_in_mexico", in_bounds, "error", f"bounds {[round(v, 2) for v in (minx, miny, maxx, maxy)]}", None)

    notes = json.loads((INTERIM / "ingest_notes.json").read_text(encoding="utf-8"))
    for n in notes:
        check(R, f"ingest:{n['source']}:{n['code']}", True, "info", n["detail"], n["count"])

    # completeness of index-indicator cells
    idx_cells = weights.copy()
    full = idx_cells.weight > 0
    sw = CFG["coverage"]["status_weights"]
    nominal = idx_cells.epistemic_status.map(sw).fillna(0)
    complete = int((full & np.isclose(idx_cells.weight, nominal)).sum())
    partial = int((full & ~np.isclose(idx_cells.weight, nominal)).sum())
    missing = int((~full).sum())
    total = len(idx_cells)

    summary = {
        "generated": date.today().isoformat(),
        "as_of_date": CFG["as_of_date"],
        "observations": int(len(obs)),
        "observations_with_value": int(obs.value.notna().sum()),
        "territories": int(obs.territory_id.nunique()),
        "years": [int(min(obs.year)), int(max(obs.year))],
        "variables": int(obs.variable_id.nunique()),
        "sources_registered": len(REG),
        "index_cells": {"total": total, "complete": complete, "partial": partial, "missing": missing,
                        "complete_pct": round(complete / total * 100, 1), "partial_pct": round(partial / total * 100, 1),
                        "missing_pct": round(missing / total * 100, 1)},
        "coverage_tiers": {k: int(v) for k, v in cov.tier.value_counts().items()},
        "checks": {s: sum(1 for r in R if r["status"] == s) for s in ("pass", "warn", "fail")},
    }
    report = {"summary": summary, "checks": R, "outliers": outliers}
    write_json(REPORTS / "quality_report.json", report)
    md = ["# Data quality report", "",
          "```text", "DATA QUALITY", "────────────", "",
          f"Observations: {summary['observations']:,} ({summary['observations_with_value']:,} with a value)",
          f"Territories:  {summary['territories']}", f"Years:        {summary['years'][0]}–{summary['years'][1]}",
          f"Variables:    {summary['variables']}", "",
          "Index indicator cells (state × year × indicator):",
          f"  Complete:     {summary['index_cells']['complete_pct']}%",
          f"  Partial:      {summary['index_cells']['partial_pct']}%   (present, but carried forward, partial-year, undated or projected)",
          f"  Missing:      {summary['index_cells']['missing_pct']}%",
          "", f"Coverage tiers (territory-years): {summary['coverage_tiers']}",
          f"Checks: {summary['checks']['pass']} pass · {summary['checks']['warn']} warn · {summary['checks']['fail']} fail",
          f"Last validation: {summary['generated']} (data as of {summary['as_of_date']})", "```", "",
          "| Check | Status | Count | Detail |", "|---|---|---|---|"]
    for r in R:
        md.append(f"| {r['check']} | {r['status']} | {'' if r['count'] is None else r['count']} | {r['detail'].replace('|', '/')} |")
    md += ["", "## Flagged outliers (robust z > 5; retained)", "", "| Variable | Year | Territory | Value | z |", "|---|---|---|---|---|"]
    for o in outliers[:200]:
        md.append(f"| {o['variable']} | {o['year']} | {o['territory']} | {o['value']:.3f} | {o['robust_z']} |")
    (REPORTS / "QUALITY_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    fails = [r for r in R if r["status"] == "fail"]
    for f in fails:
        log.error("%s: %s", f["check"], f["detail"])
    log.info("quality: %s", summary["checks"])
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
