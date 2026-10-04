"""Stage 7: assemble the public data layer and the static observatory.

Inputs : data/processed/*, config/*, data/documentary/*, reports/quality_report.json
Outputs: data/public/*.csv (the published dataset)
         site/                (GitHub Pages artifact: index.html + assets + data)
Every sentence of the per-territory explanations is generated here from the underlying values
by fixed templates; no explanation is written by hand.
"""
from __future__ import annotations

import json
import shutil
from datetime import date

import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader

from .common import (PROCESSED, PUBLIC, INTERIM, REPORTS, DOCUMENTARY, SITE, SITE_SRC, DOCS, STATES,
                     load_yaml, get_logger, write_json)

log = get_logger("site")
VARS = load_yaml("variables.yaml")
CFG = load_yaml("scenarios.yaml")
REG = load_yaml("sources.yaml")
PILLARS = ["W", "E", "D", "V"]
VERSION = "0.1.0"
PL = VARS["pillars"]


def _fmt(v, unit=""):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    a = abs(v)
    if float(v).is_integer():
        return f"{int(v):,}"
    s = f"{v:,.0f}" if a >= 100 else (f"{v:,.1f}" if a >= 10 else f"{v:,.2f}")
    return s


def public_tables(obs, res, cov):
    PUBLIC.mkdir(parents=True, exist_ok=True)
    obs.to_csv(PUBLIC / "observations.csv", index=False)
    res.to_csv(PUBLIC / "index_results.csv", index=False)
    cov.to_csv(PUBLIC / "coverage.csv", index=False)
    rows = []
    for k, v in VARS["variables"].items():
        rows.append({"variable_id": k, "pillar": v["pillar"], "in_index": v["in_index"], "direction": v["direction"],
                     "transform": v["transform"], "unit": v["unit"], "default_status": v["epistemic_status"],
                     "source_ids": "|".join(v["source_ids"]), "label_en": v["label"]["en"], "label_es": v["label"]["es"],
                     "definition_en": v["definition"]["en"], "definition_es": v["definition"]["es"],
                     "plausible_min": v["plausible_range"][0], "plausible_max": v["plausible_range"][1]})
    pd.DataFrame(rows).to_csv(PUBLIC / "variables.csv", index=False)
    pd.DataFrame(rows)[["variable_id", "definition_en"]].rename(columns={"variable_id": "method_id", "definition_en": "method"}).to_csv(PUBLIC / "methods.csv", index=False)
    src = []
    for s in REG["sources"]:
        src.append({k: s.get(k, "") for k in ("id", "institution", "title", "url_landing", "publication_date", "access_date",
                                               "license", "dataset_type", "geographic_coverage", "temporal_coverage",
                                               "redistribution", "notes")} | {"fetch_url": (s.get("fetch") or {}).get("url", "")})
    pd.DataFrame(src).to_csv(PUBLIC / "sources.csv", index=False)
    pd.read_csv(PROCESSED / "territories.csv", dtype={"cve_ent": str}).to_csv(PUBLIC / "territories.csv", index=False)
    for f in ("digital_infrastructure_register.csv", "governance_instruments.csv", "infrastructure_context.csv"):
        shutil.copy(DOCUMENTARY / f, PUBLIC / f)
    shutil.copy(PROCESSED / "sensitivity.csv", PUBLIC / "sensitivity.csv")


def reference_percentiles(obs):
    """Percentile of each raw value within the pooled 2020-2025 distribution of its variable."""
    ref = obs[obs.year.between(*CFG["reference_period"])].dropna(subset=["value"])
    dist = {k: np.sort(g.value.to_numpy()) for k, g in ref.groupby("variable_id")}

    def pct(var, v):
        d = dist.get(var)
        if d is None or v is None or np.isnan(v):
            return None
        return float(np.floor(np.searchsorted(d, v, "left") / len(d) * 100))   # share strictly below v
    return pct


def explain(state, year, rec, lang, pct):
    V = VARS["variables"]
    T = {
        "en": {"none": "No composite value is shown for {s} in {y}: {why}.",
               "lead": "In {y}, {s} has an SRTI of {v} (rank {r} of 32; under 2,000 alternative weightings its rank ranges from {lo} to {hi}).",
               "drivers": "The highest pillar is {p1} ({v1}); the lowest is {p2} ({v2}).",
               "ind": "{lab}: {raw} {unit}{pc}.",
               "pc": ", higher than {p:.0f}% of state-years in 2020–2025",
               "ren": "This value uses {n} of 4 pillars with weights renormalized ({miss} could not be computed), so it is not directly comparable with years that use all four.",
               "brk": "The set of available indicators differs from the previous year ({chg}); part of any change may reflect data availability rather than conditions.",
               "led": "Index indicators ({t}): recorded directly by a source {k}; derived {d}; estimated {e}; modelled {m}; unknown {u}. Data coverage: {tier}.",
               "caveat": "These values describe the co-location of indicators. They do not establish causal relationships, legal violations or responsibility.",
               "why_pillars": "fewer than 3 pillars could be computed", "added": "added", "removed": "missing"},
        "es": {"none": "No se muestra valor compuesto para {s} en {y}: {why}.",
               "lead": "En {y}, {s} tiene un SRTI de {v} (lugar {r} de 32; con 2,000 ponderaciones alternativas su lugar varía entre {lo} y {hi}).",
               "drivers": "El pilar más alto es {p1} ({v1}); el más bajo es {p2} ({v2}).",
               "ind": "{lab}: {raw} {unit}{pc}.",
               "pc": ", mayor que el {p:.0f}% de los estado-año de 2020–2025",
               "ren": "Este valor usa {n} de 4 pilares con pesos renormalizados ({miss} no pudo calcularse), por lo que no es directamente comparable con años que usan los cuatro.",
               "brk": "El conjunto de indicadores disponibles difiere del año anterior ({chg}); parte del cambio puede deberse a la disponibilidad de datos y no a las condiciones.",
               "led": "Indicadores del índice ({t}): registrados directamente por una fuente {k}; derivados {d}; estimados {e}; modelados {m}; desconocidos {u}. Cobertura de datos: {tier}.",
               "caveat": "Estos valores describen la coincidencia territorial de indicadores. No establecen relaciones causales, violaciones legales ni responsabilidades.",
               "why_pillars": "se calcularon menos de 3 pilares", "added": "se agrega", "removed": "falta"},
    }[lang]
    tiers = {"en": {"high": "high", "moderate": "moderate", "limited": "limited", "insufficient": "insufficient"},
             "es": {"high": "alta", "moderate": "moderada", "limited": "limitada", "insufficient": "insuficiente"}}[lang]
    name = STATES[state][1]
    out = []
    if rec["srti"] is None:
        out.append(T["none"].format(s=name, y=year, why=T["why_pillars"]))
    else:
        r = rec["rank_iv"]
        out.append(T["lead"].format(y=year, s=name, v=_fmt(rec["srti"]), r=int(rec["rank"]),
                                    lo=int(r[0]) if r[0] is not None else "—", hi=int(r[2]) if r[2] is not None else "—"))
        ps = {p: rec["P"][p] for p in PILLARS if rec["P"][p] is not None}
        if len(ps) >= 2:
            hi_p = max(ps, key=ps.get); lo_p = min(ps, key=ps.get)
            out.append(T["drivers"].format(p1=PL[hi_p][lang], v1=_fmt(ps[hi_p]), p2=PL[lo_p][lang], v2=_fmt(ps[lo_p])))
            for p in (hi_p,):
                for k, v in V.items():
                    if v["pillar"] == p and v["in_index"]:
                        raw = rec["ind"][k][0]
                        if raw is None:
                            continue
                        pc = pct(k, raw)
                        out.append(T["ind"].format(lab=v["label"][lang], raw=_fmt(raw), unit=v["unit"],
                                                   pc=T["pc"].format(p=pc) if pc is not None else ""))
        if "PILLARS_RENORMALIZED" in rec["flags"]:
            miss = ", ".join(PL[p][lang] for p in PILLARS if rec["P"][p] is None)
            out.append(T["ren"].format(n=rec["n_pillars"], miss=miss))
    if rec.get("set_change"):
        chg = "; ".join(f"{T['added' if s == '+' else 'removed']}: {V[k]['label'][lang]}" for s, k in rec["set_change"])
        out.append(T["brk"].format(chg=chg))
    L = rec["ledger"]
    out.append(T["led"].format(t=sum(len(v) for v in L.values()), k=len(L["known"]), d=len(L["derived"]), e=len(L["estimated"]),
                               m=len(L["modelled"]), u=len(L["unknown"]), tier=tiers[rec["tier"]]))
    out.append(T["caveat"])
    return " ".join(out)


def nn(v, nd=3):
    if v is None:
        return None
    try:
        if np.isnan(v):
            return None
    except TypeError:
        return v
    return round(float(v), nd)


def build_payload(obs, res, cov, weights):
    V = VARS["variables"]
    pct = reference_percentiles(obs)
    norm = pd.read_csv(PROCESSED / "normalized_indicators.csv", dtype={"territory_id": str}).set_index(["territory_id", "year"])
    base = res[res.scenario == "baseline"].set_index(["territory_id", "year"])
    scen = res.pivot_table(index=["territory_id", "year"], columns="scenario", values="value")
    covi = cov.set_index(["territory_id", "year"])
    ob = obs.set_index(["territory_id", "year", "variable_id"])
    wl = weights.set_index(["territory_id", "year", "variable_id"])
    idx_vars = [k for k, v in V.items() if v["in_index"]]
    anchors = json.loads((SITE / "data" / "anchors.json").read_text())
    data, explanations = {}, {}
    for ce in STATES:
        data[ce], explanations[ce] = {}, {}
        prev_set = None
        for y in CFG["years"]:
            b = base.loc[(ce, y)]
            c = covi.loc[(ce, y)]
            ind = {}
            ledger = {"known": [], "derived": [], "estimated": [], "modelled": [], "unknown": []}
            for k in V:
                o = ob.loc[(ce, y, k)]
                raw = nn(o.value, 4)
                nv = nn(norm.loc[(ce, y), k], 2) if k in norm.columns else None
                ind[k] = [raw, nv, o.epistemic_status, o.qa_flags if isinstance(o.qa_flags, str) else "", str(o.source_id),
                          None if pd.isna(o.vintage_year) else int(o.vintage_year)]
                if k in idx_vars:
                    ledger[wl.loc[(ce, y, k)].ledger].append(k)
            avail = {k for k in idx_vars if ind[k][0] is not None}
            set_change = None
            if prev_set is not None and avail != prev_set:
                set_change = [("+", k) for k in sorted(avail - prev_set)] + [("-", k) for k in sorted(prev_set - avail)]
            prev_set = avail
            rec = {
                "srti": nn(b.value, 2) if c.tier != "insufficient" else None,
                "rbi": nn(scen.loc[(ce, y)].get("rbi"), 2),
                "flags": b["flags"] if isinstance(b["flags"], str) else "",
                "n_pillars": int(b.n_pillars),
                "P": {p: nn(b[p], 2) for p in PILLARS},
                "mc": [nn(b.mc_low, 2), nn(b.mc_high, 2)],
                "rank": nn(b["rank"], 0),
                "rank_iv": [nn(b.rank_p05, 1), nn(b.rank_median, 1), nn(b.rank_p95, 1)],
                "cov": nn(c.coverage, 3), "tier": c.tier,
                "covP": {p: nn(c[f"coverage_{p}"], 3) for p in PILLARS},
                "ledger": ledger, "set_change": set_change,
                "scen": {k: nn(v, 2) for k, v in scen.loc[(ce, y)].items()},
                "ind": ind,
            }
            data[ce][y] = rec
            explanations[ce][y] = {"en": explain(ce, y, rec, "en", pct), "es": explain(ce, y, rec, "es", pct)}
    sens = pd.read_csv(PROCESSED / "sensitivity.csv")
    sens_summary = sens.groupby("scenario").spearman_vs_baseline.agg(["min", "median"]).round(3).reset_index().to_dict("records")
    qa = json.loads((REPORTS / "quality_report.json").read_text(encoding="utf-8"))
    gov = pd.read_csv(DOCUMENTARY / "governance_instruments.csv").fillna("").to_dict("records")
    reg = pd.read_csv(DOCUMENTARY / "digital_infrastructure_register.csv", dtype=str).fillna("").to_dict("records")
    ctx = pd.read_csv(DOCUMENTARY / "infrastructure_context.csv", dtype=str).fillna("").to_dict("records")
    payload = {
        "meta": {"title": "Digital Infrastructure & Resource Governance Observatory", "version": VERSION,
                 "as_of": CFG["as_of_date"], "generated": date.today().isoformat(), "years": CFG["years"],
                 "reference_period": CFG["reference_period"],
                 "scenarios": {k: {"label": v["label"], "weights": v["weights"], "aggregation": v["aggregation"], "normalization": v["normalization"]}
                               for k, v in CFG["scenarios"].items()},
                 "coverage": CFG["coverage"], "rules": CFG["rules"], "monte_carlo": CFG["monte_carlo"], "pillars": PL},
        "variables": {k: {f: v[f] for f in ("pillar", "in_index", "unit", "label", "definition", "direction", "source_ids", "transform", "epistemic_status")} for k, v in V.items()},
        "sources": {s["id"]: {k: s.get(k, "") for k in ("institution", "title", "url_landing", "publication_date", "access_date", "license", "dataset_type", "redistribution", "notes", "temporal_coverage")} for s in REG["sources"]},
        "territories": [{"id": ce, "name": STATES[ce][1], "iso": STATES[ce][0], "anchor": anchors[ce]} for ce in STATES],
        "data": data, "explanations": explanations,
        "national": json.loads((INTERIM / "national_context.json").read_text()),
        "sensitivity": sens_summary, "qa": qa["summary"],
        "qa_checks": [{k: r[k] for k in ("check", "status", "count", "detail")} for r in qa["checks"]],
        "governance": gov, "register": reg, "context": ctx,
    }
    return payload


def story_numbers(payload):
    """Numbers quoted in the narrative, computed from the payload (never typed by hand)."""
    reg = pd.DataFrame(payload["register"])
    op_year = reg.operational_date.str[:4].astype(int)
    by_state = reg.cve_ent.str.zfill(2).value_counts()
    top = by_state.index[0]
    cov = pd.DataFrame([{"tier": payload["data"][c][y]["tier"]} for c in payload["data"] for y in payload["data"][c]])
    idx = [k for k, v in VARS["variables"].items() if v["in_index"]]
    direct = [k for k in idx if VARS["variables"][k]["epistemic_status"] in ("observed", "administrative", "documentary", "geospatial")]
    return {"regions_2019": int((op_year <= 2019).sum()), "regions_2025": int((op_year <= 2025).sum()),
            "region_states": int(by_state.size), "top_state": STATES[top][1],
            "top_share": f"{int(by_state.iloc[0])}/{int(by_state.sum())}",
            "n_index": len(idx), "n_direct": len(direct),
            "ord_year": 2025,
            "min_ord": str(int(np.floor(min(payload['data'][c][2025]['ind']['g_groundwater_ordinance_area'][0] for c in payload['data'])))),
            "n_high": int((cov.tier == "high").sum()), "n_limited": int((cov.tier == "limited").sum()), "n_ty": int(len(cov))}


def i18n_payload(nums):
    t = load_yaml("i18n.yaml")
    for lang in t:
        for item in t[lang]["story"]:
            item["p"] = item["p"].format(**nums)
    return t


def main():
    obs = pd.read_csv(PROCESSED / "observations.csv", dtype={"territory_id": str, "qa_flags": str})
    res = pd.read_csv(PROCESSED / "index_results.csv", dtype={"territory_id": str})
    cov = pd.read_csv(PROCESSED / "coverage.csv", dtype={"territory_id": str})
    weights = pd.read_csv(PROCESSED / "indicator_weights.csv", dtype={"territory_id": str})
    public_tables(obs, res, cov)
    payload = build_payload(obs, res, cov, weights)
    payload["story_numbers"] = story_numbers(payload)
    payload["i18n"] = i18n_payload(payload["story_numbers"])
    write_json(SITE / "data" / "observatory.json", payload, compact=True)
    # static assets
    for sub in ("assets",):
        dst = SITE / sub
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(SITE_SRC / sub, dst)
    (SITE / "downloads").mkdir(exist_ok=True)
    for f in PUBLIC.glob("*.csv"):
        shutil.copy(f, SITE / "downloads" / f.name)
    shutil.copy(REPORTS / "QUALITY_REPORT.md", SITE / "downloads" / "QUALITY_REPORT.md")
    (SITE / "docs").mkdir(exist_ok=True)
    for f in DOCS.glob("*.md"):
        shutil.copy(f, SITE / "docs" / f.name)
    env = Environment(loader=FileSystemLoader(SITE_SRC / "templates"), autoescape=True)
    ctx = {"version": VERSION, "as_of": CFG["as_of_date"], "qa": payload["qa"], "years": CFG["years"]}
    (SITE / "index.html").write_text(env.get_template("index.html.j2").render(standalone=True, **ctx), encoding="utf-8")
    # Same page without the document skeleton, for hosts that add their own (e.g. a claude.ai Artifact)
    (SITE / "embed.html").write_text(env.get_template("index.html.j2").render(standalone=False, **ctx), encoding="utf-8")
    (SITE / ".nojekyll").write_text("")
    size = sum(f.stat().st_size for f in SITE.rglob("*") if f.is_file())
    log.info("site built: %.0f KB total; observatory.json %.0f KB", size / 1024, (SITE / "data" / "observatory.json").stat().st_size / 1024)


if __name__ == "__main__":
    main()
