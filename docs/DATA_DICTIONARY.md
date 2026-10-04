# Data dictionary

_Generated from `config/variables.yaml` by `src/build_docs.py`. Do not edit by hand._

## Observation schema (`data/public/observations.csv`)

| Field | Type | Description |
|---|---|---|
| obs_id | string | First 12 hex characters of SHA-1(territory_id, year, variable_id); stable across runs |
| territory_id | string | INEGI state code (CVE_ENT), two digits |
| territory_level | enum | `state` in this release (`municipality`, `aquifer`, `basin`, `region` reserved) |
| territory_name | string | Short official state name |
| year | int | 2020–2027 |
| variable_id | string | Key into the variable list below |
| value | float, empty | Empty means unknown. Never zero-filled |
| unit | string | Canonical unit for the variable |
| epistemic_status | enum | observed, administrative, documentary, geospatial, derived, estimated, modelled, hypothesized, unknown |
| source_id | string | Pipe-separated keys into `sources.csv` |
| method_id | string | Key into `methods.csv` (method = the variable definition) |
| ci_low, ci_high | float, empty | Source-reported intervals when they exist (none in this release) |
| reference_date | string | Period or date the value describes |
| vintage_year | int, empty | Edition year of the underlying source, used for recency penalties |
| release_flag | enum | `public` only in the public layer; `illustrative` and `restricted` are blocked by the production audit |
| qa_flags | string | Pipe-separated flags, e.g. PARTIAL_YEAR, CARRIED_FORWARD, UNDATED_VINTAGE, REGISTER_ABSENCE |

## Index results (`data/public/index_results.csv`)

One row per territory × year × scenario: `value` (composite 0–100), `n_pillars`, `flags`, `rank`, pillar scores `W E D V`; baseline rows add Monte Carlo `mc_low`, `mc_high`, `rank_p05`, `rank_median`, `rank_p95`.

## Coverage (`data/public/coverage.csv`)

`coverage` (0–1), `coverage_W…V`, `tier` (high / moderate / limited / insufficient), and counts of index indicators by ledger class (`n_known`, `n_derived`, `n_estimated`, `n_modelled`, `n_unknown`).

## Variables

### W · Water pressure / Presión hídrica

| id | in index | direction | transform | unit | default status | sources | definition |
|---|---|---|---|---|---|---|---|
| `w_drought_intensity` | yes | +1 | none | score 0-100 | derived | S01 | Mean drought category across all municipalities of the state and all Drought Monitor maps issued in the year (none/D0 = 0, D1 = 1 … D4 = 4), rescaled to 0-100. Municipalities are weighted equally. |
| `w_drought_share` | no | +1 | none | % | derived | S01 | Share of municipality × map observations in the year classified D1 or worse. |
| `w_aquifer_deficit_share` | yes | +1 | none | % of aquifers | administrative | S03 | Share of the aquifers that CONAGUA assigns to the state whose mean annual availability (DMA) is negative, per the 2023 publication. |
| `w_aquifer_deficit_volume_pc` | no | +1 | none | m³ per person per year | derived | S03, S02 | Sum of negative DMA volumes of the state's aquifers divided by mid-year population. |

### E · Energy-system intensity / Intensidad del sistema energético

| id | in index | direction | transform | unit | default status | sources | definition |
|---|---|---|---|---|---|---|---|
| `e_capacity_per_100k` | yes | +1 | log1p | MW per 100,000 people | derived | S07, S02 | Authorized capacity (MW) of CNE generation permits whose stated operation date is on or before 31 December of the year and that had not ended by then, per 100,000 inhabitants. Import/export permits excluded. Authorized ≠ installed or dispatched. |
| `e_combustion_share` | yes | +1 | none | % of authorized MW | derived | S07 | Share of the capacity above that uses combustion technologies (combined cycle, conventional thermal, gas turbine, internal combustion, coal, cogeneration, bioenergy). These technologies are the ones that typically require cooling water and emit at the point of generation. |

### D · Digital infrastructure / Infraestructura digital

| id | in index | direction | transform | unit | default status | sources | definition |
|---|---|---|---|---|---|---|---|
| `d_cloud_regions` | yes | +1 | log1p | regions | documentary | S20, S21, S22, S23, S24, S25, S26, S27 | Number of public-cloud regions of hyperscale providers reported operational in the state by 31 December of the year (by 4 October for 2026). Built from a documentary register; operator identities are not part of the dataset. |

### V · Territorial vulnerability / Vulnerabilidad territorial

| id | in index | direction | transform | unit | default status | sources | definition |
|---|---|---|---|---|---|---|---|
| `v_pop_density` | yes | +1 | log1p | people per km² | modelled | S02, S12 | CONAPO mid-year population divided by state area computed from generalized Natural Earth boundaries (equal-area projection). |
| `v_marginalization` | yes | -1 | none | index 0-100 (higher = less marginalized) | derived | S08 | CONAPO normalized marginalization index 2020 (IMN_2020) × 100. In CONAPO's 2020 method a HIGHER value means LOWER marginalization, so the index uses direction -1. Single vintage; carried forward with a recency penalty in the coverage score. |
| `v_drought_vulnerability` | yes | +1 | none | probability 0-100 | modelled | S09 | Mean across municipalities of the average of CONAGUA-PRONACOSE social, economic and environmental drought-vulnerability probabilities. Undated vintage. |

### G · Governance context / Contexto de gobernanza

| id | in index | direction | transform | unit | default status | sources | definition |
|---|---|---|---|---|---|---|---|
| `g_groundwater_ordinance_area` | no | +0 | none | % of state area | geospatial | S04, S05, S06, S12 | Share of state area covered by the union of groundwater vedas, regulations/reserves and suspension-of-free-pumping agreements whose DOF date is on or before the year, as mapped by CONAGUA. Descriptive; implies no legal assessment. |
| `g_veda_area` | no | +0 | none | % of state area | geospatial | S04, S12 | Share of state area under groundwater vedas with DOF date on or before the year. |
| `g_climate_instruments` | no | +0 | none | instruments | documentary | S10 | Number of state climate-policy instruments in the INECC register reported as available, with publication year on or before the year. Counts presence, not quality or enforcement. |

### C · Context / Contexto

| id | in index | direction | transform | unit | default status | sources | definition |
|---|---|---|---|---|---|---|---|
| `e_selfsupply_new_mw_3y` | no | +1 | none | MW | derived | S07 | Authorized MW of self-supply/autoconsumo permits (AUT., AUTC) whose operation date falls in the 3 years ending in the given year. |
| `d_cloud_regions_announced` | no | +1 | none | regions | documentary | S23, S25, S26 | Regions publicly announced by year end but not yet operational. |
| `c_population` | no | +1 | none | people | modelled | S02 | CONAPO mid-year population (projection from 2020). |
| `c_pop_growth_5y` | no | +1 | none | % over 5 years | modelled | S02 | Percent change in CONAPO mid-year population over the previous 5 years. |

