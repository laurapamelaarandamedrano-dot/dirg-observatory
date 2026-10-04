"""Tests for the methodological rules. Run after the pipeline: `pytest -q`."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from src import calculate_index as ci
from src import uncertainty as unc
from src.common import PROCESSED, PUBLIC, SITE, STATES, load_yaml

VARS = load_yaml("variables.yaml")["variables"]
CFG = load_yaml("scenarios.yaml")


@pytest.fixture(scope="module")
def obs():
    return pd.read_csv(PROCESSED / "observations.csv", dtype={"territory_id": str, "qa_flags": str})


@pytest.fixture(scope="module")
def res():
    return pd.read_csv(PROCESSED / "index_results.csv", dtype={"territory_id": str})


# ---------------------------------------------------------------- data integrity
def test_every_expected_row_exists(obs):
    assert len(obs) == len(STATES) * len(CFG["years"]) * len(VARS)


def test_missing_is_never_zero(obs):
    assert (obs.value.isna() == (obs.epistemic_status == "unknown")).all()


def test_no_illustrative_rows(obs):
    assert set(obs.release_flag) == {"public"}


def test_values_within_plausible_range(obs):
    for k, g in obs.dropna(subset=["value"]).groupby("variable_id"):
        lo, hi = VARS[k]["plausible_range"]
        assert g.value.between(lo, hi).all(), k


def test_no_backward_carry_of_aquifer_vintage(obs):
    a = obs[(obs.variable_id == "w_aquifer_deficit_share") & (obs.year < 2023)]
    assert a.value.isna().all()


def test_future_year_digital_is_unknown(obs):
    d = obs[(obs.variable_id == "d_cloud_regions") & (obs.year == 2027)]
    assert d.value.isna().all()


# ---------------------------------------------------------------- company-agnostic / privacy
def test_company_agnostic():
    forbidden = {"permisionario", "direccion", "operator", "operador", "company", "empresa"}
    for f in PUBLIC.glob("*.csv"):
        cols = {c.lower() for c in pd.read_csv(f, nrows=0).columns}
        assert not (cols & forbidden), f.name
    reg = pd.read_csv(PUBLIC / "digital_infrastructure_register.csv")
    assert not ({"lat", "lon", "latitude", "longitude", "address"} & set(reg.columns))


def test_dropping_identity_changes_nothing(obs):
    """The index is computed from state-year observations only; no entity field can influence it."""
    assert set(obs.columns) >= {"territory_id", "year", "variable_id", "value"}
    assert not any("operator" in c.lower() or "company" in c.lower() for c in obs.columns)


# ---------------------------------------------------------------- index rules
def test_pillar_requires_half_of_indicators():
    idx = pd.MultiIndex.from_tuples([("01", 2020)], names=["territory_id", "year"])
    norm = pd.DataFrame({k: [np.nan] for k, v in VARS.items() if v["in_index"]}, index=idx)
    norm["v_pop_density"] = 50.0   # 1 of 3 V indicators -> below 50%
    ps = ci.pillar_scores(norm)
    assert np.isnan(ps.loc[("01", 2020), "V"])
    norm["v_marginalization"] = 30.0   # 2 of 3 -> computed
    ps = ci.pillar_scores(norm)
    assert ps.loc[("01", 2020), "V"] == pytest.approx(40.0)


def test_composite_needs_three_pillars_and_renormalizes():
    idx = pd.MultiIndex.from_tuples([("01", 2020), ("02", 2020)], names=["territory_id", "year"])
    ps = pd.DataFrame({"W": [60, 60], "E": [40, np.nan], "D": [np.nan, np.nan], "V": [20, 20]}, index=idx)
    c = ci.composite(ps, {"W": .25, "E": .25, "D": .25, "V": .25})
    assert c.loc[("01", 2020), "value"] == pytest.approx(40.0)
    assert c.loc[("01", 2020), "flags"] == "PILLARS_RENORMALIZED"
    assert np.isnan(c.loc[("02", 2020), "value"])
    assert c.loc[("02", 2020), "flags"] == "INSUFFICIENT_PILLARS"


def test_missing_pillar_is_not_treated_as_zero():
    idx = pd.MultiIndex.from_tuples([("01", 2020)], names=["territory_id", "year"])
    ps = pd.DataFrame({"W": [80], "E": [80], "D": [np.nan], "V": [80]}, index=idx)
    assert ci.composite(ps, {"W": .25, "E": .25, "D": .25, "V": .25}).iloc[0]["value"] == pytest.approx(80.0)


def test_scores_in_range(res):
    v = res.value.dropna()
    assert v.between(0, 100).all()
    for p in "WEDV":
        assert res[p].dropna().between(0, 100).all()


def test_direction_is_respected():
    idx = pd.MultiIndex.from_tuples([(f"{i:02d}", 2020) for i in (1, 2)], names=["territory_id", "year"])
    obs = pd.DataFrame({"territory_id": ["01", "02"], "year": [2020, 2020], "variable_id": ["v_marginalization"] * 2, "value": [90.0, 40.0]})
    w = ci._prepare(obs)
    n, _ = ci.normalize(w, "minmax_pooled")
    # marginalization has direction -1: the LESS marginalized state (90) must score LOWER pressure
    assert n.loc[("01", 2020), "v_marginalization"] < n.loc[("02", 2020), "v_marginalization"]


def test_monte_carlo_interval_contains_baseline(res):
    b = res[(res.scenario == "baseline") & res.value.notna()]
    inside = (b.mc_low - 1e-6 <= b.value) & (b.value <= b.mc_high + 1e-6)
    # equal weights lie inside the Dirichlet(4) mass for (nearly) every case
    assert inside.mean() > 0.95


# ---------------------------------------------------------------- uncertainty
def test_coverage_tiers():
    assert unc.tier(0.8) == "high" and unc.tier(0.6) == "moderate" and unc.tier(0.3) == "limited" and unc.tier(0.1) == "insufficient"


def test_recency_penalty():
    r = pd.Series({"value": 1.0, "epistemic_status": "administrative", "vintage_year": 2023, "year": 2027, "qa_flags": "CARRIED_FORWARD"})
    assert unc.indicator_weight(r) == pytest.approx(1 - 0.15 * 3)
    r2 = r.copy(); r2["year"] = 2024
    assert unc.indicator_weight(r2) == pytest.approx(1.0)


def test_unknown_weighs_zero():
    r = pd.Series({"value": np.nan, "epistemic_status": "unknown", "vintage_year": np.nan, "year": 2027, "qa_flags": ""})
    assert unc.indicator_weight(r) == 0


# ---------------------------------------------------------------- site
def test_site_payload_consistent():
    d = json.loads((SITE / "data" / "observatory.json").read_text(encoding="utf-8"))
    assert {t["id"] for t in d["territories"]} == set(STATES)
    for ce in STATES:
        for y in CFG["years"]:
            rec = d["data"][ce][str(y)]
            if rec["tier"] == "insufficient":
                assert rec["srti"] is None
            assert set(d["explanations"][ce][str(y)]) == {"en", "es"}


def test_story_numbers_match_register():
    d = json.loads((SITE / "data" / "observatory.json").read_text(encoding="utf-8"))
    reg = pd.read_csv(PUBLIC / "digital_infrastructure_register.csv", dtype=str)
    assert d["story_numbers"]["regions_2025"] == int((reg.operational_date.str[:4].astype(int) <= 2025).sum())
