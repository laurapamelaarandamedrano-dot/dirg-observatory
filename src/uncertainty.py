"""Stage 4: data coverage / confidence for every territory-year.

Coverage is computed per pillar (mean of indicator weights) and then averaged across the four
pillars, so a pillar with a single indicator counts as much as one with three. Each indicator's
weight = status weight × recency factor × partial-year factor × undated-vintage factor; a missing
indicator weighs 0. Tiers are read from config/scenarios.yaml.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .common import PROCESSED, load_yaml, get_logger

log = get_logger("uncertainty")
CFG = load_yaml("scenarios.yaml")
VARS = load_yaml("variables.yaml")["variables"]
PILLARS = ["W", "E", "D", "V"]

LEDGER_CLASS = {
    "observed": "known", "administrative": "known", "documentary": "known", "geospatial": "known",
    "derived": "derived", "estimated": "estimated", "modelled": "modelled",
    "hypothesized": "unknown", "unknown": "unknown",
}


def indicator_weight(r) -> float:
    c = CFG["coverage"]
    if pd.isna(r.value) or r.epistemic_status == "unknown":
        return 0.0
    w = c["status_weights"].get(r.epistemic_status, 0.0)
    flags = str(r.qa_flags or "")
    if pd.notna(r.vintage_year) and r.vintage_year != "":
        gap = max(0, int(r.year) - int(float(r.vintage_year)) - c["recency"]["grace_years"])
        w *= max(c["recency"]["floor"], 1 - c["recency"]["penalty_per_year"] * gap)
    if "UNDATED_VINTAGE" in flags:
        w *= c["undated_vintage_factor"]
    if "PARTIAL_YEAR" in flags:
        w *= c["partial_year_factor"]
    return round(w, 4)


def tier(score: float) -> str:
    t = CFG["coverage"]["tiers"]
    for name in ("high", "moderate", "limited"):
        if score >= t[name]:
            return name
    return "insufficient"


def main() -> pd.DataFrame:
    obs = pd.read_csv(PROCESSED / "observations.csv", dtype={"territory_id": str, "qa_flags": str})
    idx_vars = {k: v for k, v in VARS.items() if v.get("in_index")}
    sub = obs[obs.variable_id.isin(idx_vars)].copy()
    sub["pillar"] = sub.variable_id.map(lambda k: idx_vars[k]["pillar"])
    sub["weight"] = sub.apply(indicator_weight, axis=1)
    sub["ledger"] = sub.epistemic_status.map(LEDGER_CLASS)
    sub[["territory_id", "year", "variable_id", "pillar", "epistemic_status", "ledger", "weight"]].to_csv(
        PROCESSED / "indicator_weights.csv", index=False)
    pc = sub.groupby(["territory_id", "year", "pillar"]).weight.mean().unstack("pillar").reindex(columns=PILLARS)
    cov = pc.mean(axis=1).rename("coverage").to_frame()
    for p in PILLARS:
        cov[f"coverage_{p}"] = pc[p].round(4)
    cov["coverage"] = cov.coverage.round(4)
    cov["tier"] = cov.coverage.map(tier)
    led = sub.groupby(["territory_id", "year"]).ledger.value_counts().unstack(fill_value=0)
    for k in ("known", "derived", "estimated", "modelled", "unknown"):
        cov[f"n_{k}"] = led.get(k, 0)
    cov = cov.reset_index()
    cov.to_csv(PROCESSED / "coverage.csv", index=False)
    log.info("coverage tiers: %s", cov.tier.value_counts().to_dict())
    return cov


if __name__ == "__main__":
    main()
