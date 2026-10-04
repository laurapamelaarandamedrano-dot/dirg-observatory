"""Stage 2: parse each raw source and emit tidy state × year observations.

Output: data/processed/observations.csv in the long schema documented in docs/DATA_DICTIONARY.md.
Every expected (state, year, variable) combination gets a row; a missing value is written as an
empty `value` with epistemic_status `unknown` and a reason in `qa_flags`. Missing is never zero.
"""
from __future__ import annotations

import hashlib
import re
import zipfile
from datetime import date

import geopandas as gpd
import numpy as np
import pandas as pd

from .common import (RAW, GEO, DOCUMENTARY, PROCESSED, INTERIM, STATES, ISO_ALIASES, ISO_TO_CVE,
                     cve, cve_from_name, load_yaml, get_logger, write_json)

log = get_logger("clean")
CFG = load_yaml("scenarios.yaml")
VARS = load_yaml("variables.yaml")["variables"]
YEARS = CFG["years"]
AS_OF = pd.Timestamp(CFG["as_of_date"])
EQUAL_AREA = "+proj=aea +lat_1=14.5 +lat_2=32.5 +lat_0=24 +lon_0=-102 +datum=WGS84 +units=m +no_defs"
QA_NOTES: list[dict] = []   # ingestion-level findings, consumed by validate.py


def note(source, code, detail, count=None):
    QA_NOTES.append({"source": source, "code": code, "detail": detail, "count": count})


def row(cve_ent, year, var, value, status, source_ids, vintage, flags=(), ref_date=None):
    v = None if value is None or (isinstance(value, float) and np.isnan(value)) else float(value)
    return {
        "territory_id": cve_ent, "territory_level": "state", "territory_name": STATES[cve_ent][1],
        "year": int(year), "variable_id": var, "value": v,
        "unit": VARS[var]["unit"],
        "epistemic_status": status if v is not None else "unknown",
        "source_id": "|".join(source_ids), "method_id": var,
        "ci_low": None, "ci_high": None,
        "reference_date": ref_date or "", "vintage_year": vintage,
        "release_flag": "public", "qa_flags": "|".join(flags),
    }


# --------------------------------------------------------------------------- geometry / area
def state_geometry() -> gpd.GeoDataFrame:
    g = gpd.read_file(GEO / "ne_10m_admin1_mexico.geojson")
    g["iso"] = g["iso_3166_2"].replace(ISO_ALIASES)
    g["cve_ent"] = g["iso"].map(ISO_TO_CVE)
    if g["cve_ent"].isna().any():
        raise ValueError(f"unmatched NE states: {g[g.cve_ent.isna()].name.tolist()}")
    g["area_km2"] = g.to_crs(EQUAL_AREA).area / 1e6
    return g[["cve_ent", "name", "area_km2", "geometry"]]


# --------------------------------------------------------------------------- population (S02)
def population() -> pd.DataFrame:
    c = pd.read_csv(RAW / "conapo_indicadores.csv", usecols=["ANIO", "CVE_GEO", "POB_MIT_ANIO"])
    c = c[(c.CVE_GEO >= 1) & (c.CVE_GEO <= 32)].copy()
    c["cve_ent"] = c.CVE_GEO.map(cve)
    return c.rename(columns={"ANIO": "year", "POB_MIT_ANIO": "pop"})[["cve_ent", "year", "pop"]]


# --------------------------------------------------------------------------- drought (S01)
def drought() -> list[dict]:
    x = pd.read_excel(RAW / "smn_MunicipiosSequia.xlsx", sheet_name="MUNICIPIOS")
    date_cols = [c for c in x.columns if isinstance(c, (pd.Timestamp, date)) or re.match(r"^\d{4}-\d{2}-\d{2}", str(c))]
    note("S01", "INFO_MAPS", f"{len(date_cols)} drought maps, {x.shape[0]} municipalities, last map {pd.Timestamp(date_cols[-1]).date()}")
    vals = x[date_cols].astype("string").fillna("")
    allowed = {"", "D0", "D1", "D2", "D3", "D4"}
    bad = ~vals.isin(allowed)
    if bad.to_numpy().any():
        note("S01", "UNEXPECTED_CATEGORY", "cells with categories outside {blank,D0..D4} set to missing", int(bad.to_numpy().sum()))
    score = vals.replace({"": 0, "D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4}).where(~bad)
    score = score.apply(pd.to_numeric, errors="coerce")
    score["cve_ent"] = x["CVE_ENT"].map(cve)
    out = []
    last_map = pd.Timestamp(date_cols[-1])
    for y in YEARS:
        cols = [c for c in date_cols if pd.Timestamp(c).year == y]
        for ce in STATES:
            if not cols:
                out.append(row(ce, y, "w_drought_intensity", None, "unknown", ["S01"], None, ["NO_MAPS_FOR_YEAR"]))
                out.append(row(ce, y, "w_drought_share", None, "unknown", ["S01"], None, ["NO_MAPS_FOR_YEAR"]))
                continue
            sub = score.loc[score.cve_ent == ce, cols].to_numpy(dtype=float)
            if sub.size == 0 or np.isnan(sub).all():
                out.append(row(ce, y, "w_drought_intensity", None, "unknown", ["S01"], y, ["NO_MUNICIPALITIES"]))
                continue
            flags = [f"MAPS={len(cols)}"]
            if y == last_map.year and last_map.month < 12:
                flags.append("PARTIAL_YEAR")
            intensity = np.nanmean(sub) / 4 * 100
            share = np.nanmean(sub >= 1) * 100
            ref = f"{y}" if "PARTIAL_YEAR" not in flags else f"{y}-01..{last_map.date()}"
            out.append(row(ce, y, "w_drought_intensity", round(intensity, 3), "derived", ["S01"], y, flags, ref))
            out.append(row(ce, y, "w_drought_share", round(share, 3), "derived", ["S01"], y, flags, ref))
    return out


# --------------------------------------------------------------------------- aquifers (S03)
def aquifers(pop: pd.DataFrame) -> list[dict]:
    g = gpd.read_file(f"zip://{RAW / 'conagua_disponibilidad.zip'}")
    if g.CLV_ACUI.duplicated().any():
        note("S03", "DUPLICATE_AQUIFER", "duplicate aquifer codes", int(g.CLV_ACUI.duplicated().sum()))
    note("S03", "INFO_AQUIFERS", f"{len(g)} aquifers; {(g.DMA_NEGATI < 0).sum()} with negative availability")
    g["cve_ent"] = g.CLV_EDO.map(cve)
    agg = g.groupby("cve_ent").agg(n=("CLV_ACUI", "size"),
                                   deficit=("DMA_NEGATI", lambda s: int((s < 0).sum())),
                                   deficit_hm3=("DMA_NEGATI", lambda s: float(-s[s < 0].sum())))
    vintage = 2023
    out = []
    for y in YEARS:
        for ce in STATES:
            if y < vintage:
                out.append(row(ce, y, "w_aquifer_deficit_share", None, "unknown", ["S03"], None, ["NO_VINTAGE_FOR_YEAR"]))
                out.append(row(ce, y, "w_aquifer_deficit_volume_pc", None, "unknown", ["S03", "S02"], None, ["NO_VINTAGE_FOR_YEAR"]))
                continue
            if ce not in agg.index:
                out.append(row(ce, y, "w_aquifer_deficit_share", None, "unknown", ["S03"], None, ["NO_AQUIFERS_ASSIGNED"]))
                continue
            a = agg.loc[ce]
            flags = [f"AQUIFERS={int(a.n)}"] + (["CARRIED_FORWARD"] if y > vintage else [])
            out.append(row(ce, y, "w_aquifer_deficit_share", round(a.deficit / a.n * 100, 3), "administrative", ["S03"], vintage, flags, "2023"))
            p = pop[(pop.cve_ent == ce) & (pop.year == y)]["pop"]
            vol = a.deficit_hm3 * 1e6 / float(p.iloc[0]) if len(p) else None
            out.append(row(ce, y, "w_aquifer_deficit_volume_pc", None if vol is None else round(vol, 3), "derived", ["S03", "S02"], vintage, flags, "2023"))
    return out


# --------------------------------------------------------------------------- energy permits (S07)
COMBUSTION = re.compile(r"combusti|turbog|ciclo combinado|termoel|carbo|cogener|bioener|lecho", re.I)


def permits(pop: pd.DataFrame) -> list[dict]:
    p = pd.read_csv(RAW / "cne_permisos_gen_hist.csv")
    n0 = len(p)
    # Data minimisation: holder names, addresses and coordinates are dropped immediately.
    p = p.drop(columns=["permisionario", "direccion", "pais_origen"], errors="ignore")
    p["cve_ent"] = p["entidad"].map(cve_from_name)
    unk = p.cve_ent.isna()
    note("S07", "UNMATCHED_STATE", f"permits without a recognisable state (e.g. 'PERMISO RENUNCIADO', 'sin dato'); excluded: {sorted(p.loc[unk,'entidad'].astype(str).unique())[:6]}", int(unk.sum()))
    p = p[~unk]
    trade = p.modalidad.astype(str).str.contains(r"IMP|EXP", regex=True) | p.tecnologia.astype(str).str.contains("Importaci", na=False)
    note("S07", "EXCLUDED_IMPORT_EXPORT", "import/export permits excluded", int(trade.sum()))
    p = p[~trade]
    p["mw"] = pd.to_numeric(p.capacidad_autorizada, errors="coerce")
    miss = p.mw.isna()
    note("S07", "MISSING_CAPACITY", "permits with no authorized capacity; excluded", int(miss.sum()))
    p = p[~miss]
    impossible = p.mw > 5000
    if impossible.any():
        note("S07", "IMPOSSIBLE_VALUE", f"authorized capacity > 5,000 MW for a single permit (max {p.mw.max():,.0f} MW); excluded as data-entry error", int(impossible.sum()))
    p = p[~impossible]
    gen = pd.to_numeric(p.generacion_estimada, errors="coerce")
    cf = gen / (p.mw * 8.76)
    suspect = (p.mw > 100) & (cf < 0.002)
    note("S07", "SUSPECT_UNIT", "permits > 100 MW whose estimated annual generation implies a capacity factor < 0.2% (likely kW recorded as MW); excluded", int(suspect.sum()))
    p = p[~suspect]
    p["op"] = pd.to_datetime(p.fecha_operacion, errors="coerce", format="%Y-%m-%d")
    p["granted"] = pd.to_datetime(p.fecha_otorgamiento, errors="coerce", format="%Y-%m-%d")
    p["end"] = pd.to_datetime(p.fecha_termino, errors="coerce", dayfirst=True)
    ended_status = p.estatus.astype(str).str.lower().str.contains(r"termin|revoc|caduc|inactiv|conclus|desapar|migrad")
    imputed = p.op.isna() & p.end.notna()
    p.loc[imputed, "op"] = p.loc[imputed, "granted"]
    p["imputed"] = imputed
    note("S07", "OP_DATE_IMPUTED", "ended permits without an operation date: grant date used as start (flagged)", int(imputed.sum()))
    no_end = ended_status & p.end.isna()
    note("S07", "ENDED_WITHOUT_DATE", "permits marked ended but with no end date; excluded from all years", int(no_end.sum()))
    p = p[~no_end & p.op.notna()]
    p["combustion"] = p.tecnologia.astype(str).str.contains(COMBUSTION)
    p["selfsupply"] = p.modalidad.astype(str).str.startswith("AUT") | p.num_per.astype(str).str.contains("/AUTC/") | p.act_eco.astype(str).str.contains("utoconsumo")
    note("S07", "INFO_PERMITS", f"{n0} permits in file; {len(p)} usable after exclusions")
    out = []
    cutoff = pd.Timestamp("2026-02-28")  # last update of the permit file
    for y in YEARS:
        end_y = pd.Timestamp(f"{y}-12-31")
        active = p[(p.op <= end_y) & (p.end.isna() | (p.end > end_y))]
        status = "derived" if y <= cutoff.year - 1 else "estimated"
        for ce in STATES:
            a = active[active.cve_ent == ce]
            mw = float(a.mw.sum())
            popv = float(pop[(pop.cve_ent == ce) & (pop.year == y)]["pop"].iloc[0])
            flags = []
            if y > 2025:
                flags.append("INCLUDES_PLANNED_OPERATION_DATES")
            if a.imputed.any():
                flags.append("SOME_START_DATES_IMPUTED")
            out.append(row(ce, y, "e_capacity_per_100k", round(mw / popv * 1e5, 4), status, ["S07", "S02"], min(y, 2026), flags))
            share = (a.loc[a.combustion, "mw"].sum() / mw * 100) if mw > 0 else None
            out.append(row(ce, y, "e_combustion_share", None if share is None else round(share, 3), status, ["S07"], min(y, 2026),
                           flags if share is not None else ["NO_CAPACITY"]))
            win = p[(p.cve_ent == ce) & p.selfsupply & (p.op > pd.Timestamp(f"{y-3}-12-31")) & (p.op <= end_y)]
            out.append(row(ce, y, "e_selfsupply_new_mw_3y", round(float(win.mw.sum()), 3), status, ["S07"], min(y, 2026), flags))
    return out


# --------------------------------------------------------------------------- digital register (S20-S27)
def digital() -> list[dict]:
    r = pd.read_csv(DOCUMENTARY / "digital_infrastructure_register.csv", dtype=str).fillna("")
    r["cve_ent"] = r.cve_ent.map(cve)

    def as_date(s, end=True):
        if not s:
            return None
        if re.fullmatch(r"\d{4}", s):
            return pd.Timestamp(f"{s}-12-31" if end else f"{s}-01-01")
        if re.fullmatch(r"\d{4}-\d{2}", s):
            t = pd.Timestamp(s + "-01")
            return t + pd.offsets.MonthEnd(0) if end else t
        return pd.Timestamp(s)

    r["op"] = r.operational_date.map(as_date)
    r["ann"] = r.announced_date.map(lambda s: as_date(s, end=False))
    out = []
    for y in YEARS:
        ref = min(pd.Timestamp(f"{y}-12-31"), AS_OF)
        for ce in STATES:
            if y > AS_OF.year:
                out.append(row(ce, y, "d_cloud_regions", None, "unknown", ["S20"], None, ["FUTURE_YEAR_NOT_OBSERVABLE"]))
                out.append(row(ce, y, "d_cloud_regions_announced", None, "unknown", ["S20"], None, ["FUTURE_YEAR_NOT_OBSERVABLE"]))
                continue
            s = r[r.cve_ent == ce]
            on = s[s.op.notna() & (s.op <= ref)]
            ann = s[s.ann.notna() & (s.ann <= ref) & ~(s.op.notna() & (s.op <= ref))]
            srcs = sorted({x for ids in on.source_ids for x in ids.split("|")}) or ["S20"]
            flags = ["REGISTER_ABSENCE"] if len(on) == 0 else [f"RECORDS={'|'.join(on.record_id)}"]
            if y == AS_OF.year:
                flags.append(f"AS_OF={AS_OF.date()}")
            if (on.location_confidence == "secondary").any():
                flags.append("SECONDARY_SOURCE")
            out.append(row(ce, y, "d_cloud_regions", len(on), "documentary", srcs, y, flags, str(ref.date())))
            out.append(row(ce, y, "d_cloud_regions_announced", len(ann), "documentary", srcs, y, [], str(ref.date())))
    return out


# --------------------------------------------------------------------------- vulnerability (S02, S08, S09)
def vulnerability(pop: pd.DataFrame, geo: gpd.GeoDataFrame) -> list[dict]:
    out = []
    area = geo.set_index("cve_ent").area_km2
    ime = pd.read_csv(RAW / "conapo_ime_2020.csv")
    ime["cve_ent"] = ime.CVE_ENT.map(cve)
    ime = ime.set_index("cve_ent")
    frames = []
    for k in ("social", "economica", "ambiental"):
        f = pd.read_csv(RAW / f"pronacose_vuln_{k}.csv", dtype={"cve_concatenada": str})
        f["mun"] = f.cve_concatenada.str.zfill(5)
        frames.append(f.set_index("mun")["probabilidad"].rename(k))
    v = pd.concat(frames, axis=1)
    note("S09", "INFO_MUNICIPALITIES", f"{len(v)} municipalities; rows with any missing component: {int(v.isna().any(axis=1).sum())}")
    v["mean3"] = v[["social", "economica", "ambiental"]].mean(axis=1, skipna=False)
    v["cve_ent"] = v.index.str[:2]
    vstate = v.groupby("cve_ent").mean3.mean()
    for y in YEARS:
        for ce in STATES:
            pv = pop[(pop.cve_ent == ce) & (pop.year == y)]["pop"]
            p = float(pv.iloc[0])
            out.append(row(ce, y, "c_population", p, "modelled", ["S02"], y))
            p5 = pop[(pop.cve_ent == ce) & (pop.year == y - 5)]["pop"]
            out.append(row(ce, y, "c_pop_growth_5y", round((p / float(p5.iloc[0]) - 1) * 100, 4) if len(p5) else None, "modelled", ["S02"], y))
            out.append(row(ce, y, "v_pop_density", round(p / area[ce], 4), "modelled", ["S02", "S12"], y, ["AREA_FROM_GENERALIZED_BOUNDARIES"]))
            flags = ["CARRIED_FORWARD"] if y > 2020 else []
            out.append(row(ce, y, "v_marginalization", round(float(ime.loc[ce, "IMN_2020"]) * 100, 4), "derived", ["S08"], 2020, flags, "2020"))
            out.append(row(ce, y, "v_drought_vulnerability", round(float(vstate.get(ce, np.nan)), 4), "modelled", ["S09"], None, ["UNDATED_VINTAGE"]))
    return out


# --------------------------------------------------------------------------- governance (S04-S06, S10)
def governance(geo: gpd.GeoDataFrame) -> list[dict]:
    layers = []
    for z, key in (("conagua_vedas.zip", "veda"), ("conagua_reglamentos.zip", "reglamento"), ("conagua_suspension.zip", "suspension")):
        g = gpd.read_file(f"zip://{RAW / z}").to_crs(EQUAL_AREA)
        g["kind"] = key
        g["dof"] = pd.to_datetime(g.FECHA_DOF, errors="coerce")
        bad = g.dof.isna().sum()
        if bad:
            note({"veda": "S04", "reglamento": "S05", "suspension": "S06"}[key], "MISSING_DOF_DATE", "ordinance polygons without a DOF date; excluded", int(bad))
        g["geometry"] = g.geometry.make_valid()
        layers.append(g[g.dof.notna()][["kind", "dof", "geometry"]])
    ords = pd.concat(layers, ignore_index=True)
    states = geo.to_crs(EQUAL_AREA).set_index("cve_ent")
    inst = pd.read_csv(RAW / "inecc_instrumentos.csv", dtype=str)
    inst["cve_ent"] = pd.to_numeric(inst.clave_entidad_federativa, errors="coerce")
    inst = inst[inst.cve_ent.between(1, 32)]
    inst["cve_ent"] = inst.cve_ent.astype(int).map(cve)
    inst["yr"] = pd.to_numeric(inst.anio_publicacion, errors="coerce")
    no_year = (inst.disponibilidad.str.upper() == "SI") & inst.yr.isna()
    note("S10", "NO_PUBLICATION_YEAR", "available instruments without publication year; not counted", int(no_year.sum()))
    out = []
    for y in YEARS:
        cut = pd.Timestamp(f"{y}-12-31")
        cur = ords[ords.dof <= cut]
        u_all = cur.geometry.union_all() if len(cur) else None
        cur_v = cur[cur.kind == "veda"]
        u_veda = cur_v.geometry.union_all() if len(cur_v) else None
        for ce, srow in states.iterrows():
            a = srow.geometry.area
            sh_all = u_all.intersection(srow.geometry).area / a * 100 if u_all is not None else 0.0
            sh_v = u_veda.intersection(srow.geometry).area / a * 100 if u_veda is not None else 0.0
            flags = ["GEOMETRY_AS_OF_FILE_DATE"]
            out.append(row(ce, y, "g_groundwater_ordinance_area", round(min(sh_all, 100), 3), "geospatial", ["S04", "S05", "S06", "S12"], y, flags))
            out.append(row(ce, y, "g_veda_area", round(min(sh_v, 100), 3), "geospatial", ["S04", "S12"], y, flags))
            n = int(((inst.cve_ent == ce) & (inst.disponibilidad.str.upper() == "SI") & (inst.yr <= y)).sum())
            out.append(row(ce, y, "g_climate_instruments", n, "documentary", ["S10"], y))
    return out


# --------------------------------------------------------------------------- national context (S11)
def national_context() -> dict:
    c = pd.read_csv(RAW / "cfe_consumo_final.csv", parse_dates=["fecha"])
    c["year"] = c.fecha.dt.year
    a = c.groupby("year").agg(gwh=("consumo_final_electricidad_gwh", "sum"), months=("fecha", "size")).reset_index()
    return {"variable": "national_final_electricity_consumption", "unit": "TWh", "source_id": "S11",
            "epistemic_status": "administrative",
            "series": [{"year": int(r.year), "value": round(r.gwh / 1000, 2), "complete": bool(r.months == 12)} for r in a.itertuples()]}


def obs_id(r) -> str:
    return hashlib.sha1(f"{r['territory_id']}|{r['year']}|{r['variable_id']}".encode()).hexdigest()[:12]


def main() -> pd.DataFrame:
    geo = state_geometry()
    pop = population()
    rows = []
    for fn, args in ((drought, ()), (aquifers, (pop,)), (permits, (pop,)), (digital, ()),
                     (vulnerability, (pop, geo)), (governance, (geo,))):
        log.info("parsing %s", fn.__name__)
        rows += fn(*args)
    obs = pd.DataFrame(rows)
    obs.insert(0, "obs_id", obs.apply(obs_id, axis=1))
    obs = obs.sort_values(["variable_id", "territory_id", "year"]).reset_index(drop=True)
    obs.to_csv(PROCESSED / "observations.csv", index=False)
    geo.drop(columns="geometry").to_csv(PROCESSED / "territories.csv", index=False)
    write_json(INTERIM / "ingest_notes.json", QA_NOTES)
    write_json(INTERIM / "national_context.json", national_context())
    log.info("observations: %d rows, %d with values", len(obs), obs.value.notna().sum())
    return obs


if __name__ == "__main__":
    main()
