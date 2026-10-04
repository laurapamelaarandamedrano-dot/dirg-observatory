"""Stage 3: normalization, pillar scores, SRTI / RBI, scenarios and Monte Carlo sensitivity.

SRTI_it = Σ_p w_p · P_pit   for p in {W, E, D, V}
P_pit   = mean of the normalized indicators of pillar p available for territory i in year t
          (computed only if ≥ 50% of the pillar's indicators are available)
Missing pillars are never imputed: the composite is computed from ≥ 3 pillars with weights
renormalized over the available ones, and the row is flagged `PILLARS_RENORMALIZED`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from .common import PROCESSED, load_yaml, get_logger, write_json

log = get_logger("index")
CFG = load_yaml("scenarios.yaml")
VARS = load_yaml("variables.yaml")["variables"]
PILLARS = ["W", "E", "D", "V"]
REF = CFG["reference_period"]


def _prepare(obs: pd.DataFrame) -> pd.DataFrame:
    idx = [k for k, v in VARS.items() if v.get("in_index")]
    w = obs[obs.variable_id.isin(idx)].pivot_table(index=["territory_id", "year"], columns="variable_id",
                                                     values="value", aggfunc="first", dropna=False)
    w = w.reindex(columns=idx)
    for k in idx:
        x = w[k].astype(float)
        if VARS[k].get("transform") == "log1p":
            x = np.log1p(x)
        w[k] = x * (1 if VARS[k].get("direction", 1) >= 0 else -1)
    return w


def normalize(w: pd.DataFrame, method: str) -> tuple[pd.DataFrame, dict]:
    out = pd.DataFrame(index=w.index, columns=w.columns, dtype=float)
    params = {}
    ref_mask = w.index.get_level_values("year").to_series().between(*REF).to_numpy()
    lo_q, hi_q = CFG["normalization"]["winsorize"]
    for k in w.columns:
        x = w[k].astype(float)
        ref = x[ref_mask].dropna()
        if ref.empty:
            continue
        zero_inflated = (ref == ref.min()).mean() > 0.5
        if method == "minmax_pooled":
            lo, hi = (ref.min(), ref.max()) if zero_inflated else (ref.quantile(lo_q), ref.quantile(hi_q))
            out[k] = ((x.clip(lo, hi) - lo) / (hi - lo) * 100) if hi > lo else 50.0
            params[k] = {"method": method, "lo": float(lo), "hi": float(hi), "winsorized": not zero_inflated}
        elif method == "zscore_pooled":
            mu, sd = ref.mean(), ref.std(ddof=0)
            z = ((x - mu) / sd).clip(-3, 3) if sd > 0 else x * 0
            out[k] = (z + 3) / 6 * 100
            params[k] = {"method": method, "mean": float(mu), "sd": float(sd)}
        elif method == "percentile_pooled":
            srt = np.sort(ref.to_numpy())
            out[k] = x.map(lambda v: np.nan if pd.isna(v) else
                           (np.searchsorted(srt, v, "left") + np.searchsorted(srt, v, "right")) / 2 / len(srt) * 100)
            params[k] = {"method": method, "n_ref": int(len(srt))}
    return out, params


def pillar_scores(norm: pd.DataFrame) -> pd.DataFrame:
    thr = CFG["rules"]["min_indicator_share_per_pillar"]
    res = {}
    for p in PILLARS:
        cols = [k for k in norm.columns if VARS[k]["pillar"] == p]
        sub = norm[cols]
        share = sub.notna().sum(axis=1) / len(cols)
        res[p] = sub.mean(axis=1).where(share >= thr)
        res[f"{p}_n"] = sub.notna().sum(axis=1)
    return pd.DataFrame(res)


def composite(ps: pd.DataFrame, weights: dict, aggregation: str = "arithmetic") -> pd.DataFrame:
    weighted = [p for p in PILLARS if weights.get(p, 0) > 0]
    need = min(CFG["rules"]["min_pillars_for_composite"], len(weighted))
    vals = ps[weighted]
    wv = np.array([weights[p] for p in weighted])
    avail = vals.notna()
    wsum = (avail * wv).sum(axis=1)
    if aggregation == "geometric":
        logs = np.log(vals + 1).fillna(0) * wv
        comp = np.exp(logs.sum(axis=1) / wsum) - 1
    else:
        comp = (vals.fillna(0) * wv).sum(axis=1) / wsum
    n = avail.sum(axis=1)
    comp = comp.where(n >= need)
    flags = np.where(n < need, "INSUFFICIENT_PILLARS", np.where(n < len(weighted), "PILLARS_RENORMALIZED", ""))
    return pd.DataFrame({"value": comp.round(3), "n_pillars": n, "flags": flags}, index=ps.index)


def monte_carlo(ps: pd.DataFrame) -> pd.DataFrame:
    mc = CFG["monte_carlo"]
    rng = np.random.default_rng(mc["seed"])
    W = rng.dirichlet([mc["dirichlet_alpha"]] * 4, size=mc["draws"])
    vals = ps[PILLARS].to_numpy()
    avail = ~np.isnan(vals)
    v0 = np.nan_to_num(vals)
    num = v0 @ W.T
    den = avail.astype(float) @ W.T
    comp = num / den
    ok = avail.sum(axis=1) >= CFG["rules"]["min_pillars_for_composite"]
    comp[~ok, :] = np.nan
    lo_q, hi_q = mc["interval"]
    out = pd.DataFrame(index=ps.index)
    out["mc_low"] = np.nanquantile(comp, lo_q, axis=1) if ok.any() else np.nan
    out["mc_high"] = np.nanquantile(comp, hi_q, axis=1)
    out.loc[~ok, ["mc_low", "mc_high"]] = np.nan
    # rank intervals within each year (1 = highest tension)
    years = ps.index.get_level_values("year").to_numpy()
    rank_lo = np.full(len(ps), np.nan); rank_med = np.full(len(ps), np.nan); rank_hi = np.full(len(ps), np.nan)
    for y in np.unique(years):
        m = (years == y) & ok
        if m.sum() < 2:
            continue
        c = comp[m]
        ranks = (-c).argsort(axis=0).argsort(axis=0) + 1
        rank_lo[m] = np.quantile(ranks, lo_q, axis=1)
        rank_med[m] = np.median(ranks, axis=1)
        rank_hi[m] = np.quantile(ranks, hi_q, axis=1)
    out["rank_p05"], out["rank_median"], out["rank_p95"] = rank_lo, rank_med, rank_hi
    return out.round(3)


def main() -> dict:
    obs = pd.read_csv(PROCESSED / "observations.csv", dtype={"territory_id": str})
    prepared = _prepare(obs)
    results, norm_params, sensitivity = [], {}, []
    pillars_by_norm = {}
    for method in sorted({s["normalization"] for s in CFG["scenarios"].values()}):
        norm, params = normalize(prepared, method)
        norm_params[method] = params
        pillars_by_norm[method] = (norm, pillar_scores(norm))
    base_norm, base_ps = pillars_by_norm["minmax_pooled"]
    base_norm.round(3).reset_index().to_csv(PROCESSED / "normalized_indicators.csv", index=False)
    for key, sc in CFG["scenarios"].items():
        _, ps = pillars_by_norm[sc["normalization"]]
        c = composite(ps, sc["weights"], sc["aggregation"])
        c["scenario"] = key
        c["rank"] = c.groupby(level="year")["value"].rank(ascending=False, method="min")
        for p in PILLARS:
            c[p] = ps[p].round(3)
        results.append(c.reset_index())
    res = pd.concat(results, ignore_index=True)
    mc = monte_carlo(base_ps).reset_index()
    base = res[res.scenario == "baseline"].merge(mc, on=["territory_id", "year"], how="left")
    res = pd.concat([base, res[res.scenario != "baseline"]], ignore_index=True)
    res.to_csv(PROCESSED / "index_results.csv", index=False)
    # scenario agreement with baseline (Spearman rho of values within each year)
    piv = res.pivot_table(index=["territory_id", "year"], columns="scenario", values="value")
    for key in CFG["scenarios"]:
        if key == "baseline":
            continue
        for y, g in piv.groupby(level="year"):
            g = g[["baseline", key]].dropna()
            if len(g) >= 5:
                rho = spearmanr(g["baseline"], g[key]).statistic
                sensitivity.append({"scenario": key, "year": int(y), "spearman_vs_baseline": round(float(rho), 4), "n": int(len(g))})
    write_json(PROCESSED / "normalization_params.json", norm_params)
    pd.DataFrame(sensitivity).to_csv(PROCESSED / "sensitivity.csv", index=False)
    log.info("index computed: %d rows, %d scenarios", len(res), res.scenario.nunique())
    return {"results": res, "sensitivity": sensitivity}


if __name__ == "__main__":
    main()
