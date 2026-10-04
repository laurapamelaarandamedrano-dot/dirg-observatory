# Methodology

Release 0.1.0 · data as of 2026-10-04 · all parameters in `config/scenarios.yaml` and `config/variables.yaml`

This document explains, in plain language, what the observatory measures, how each number is produced, and what it cannot tell you. Numbers that depend on the data (rank intervals, correlations, coverage counts) are not repeated here; they are generated in `reports/QUALITY_REPORT.md`, `data/public/sensitivity.csv` and on the site, so this text cannot drift from the results.

## 1. Research question

How does the expansion of digital infrastructure relate to energy demand, water pressure and resource governance in Mexico?

The question is relational and descriptive. The design does not presuppose that digital infrastructure causes resource pressure, that any territory is harmed, or that any actor has breached any rule. The object of study is the structural co-location of four things in territory and time: digital infrastructure, water, energy and the institutions that allocate them.

## 2. Conceptual framework

The observatory treats digital infrastructure as a territorial land use embedded in two resource systems (electricity and water) that are allocated through public institutions (concessions, permits, ordinances, planning law). Tension, in the sense used here, is the simultaneous presence of high values in several of these dimensions in the same territory and year. It is a descriptive construct. High tension is a reason to look more closely, not a finding of harm.

## 3. Unit of analysis

One observation is **one variable for one state in one year**. The public layer has 32 states × 8 years (2020–2027) × 17 variables = 4,352 rows, every one of which exists even when its value is unknown.

Facilities appear only in the documentary register (`data/documentary/digital_infrastructure_register.csv`) and are aggregated to the state before any computation. The register has no operator field, and a test (`tests/test_pipeline.py::test_company_agnostic`) checks that no public file contains operator or permit-holder names.

## 4. The three-layer architecture

```text
                 OBSERVATORY
                     │
          GitHub Pages / visualization
                     │
                     ▼
             PUBLIC DATA LAYER
                     │
          processed + documented data      data/public/*.csv, site/data/*.json
                     │
                     ▼
             RESEARCH PIPELINE
                     │
       Python + validation + modelling     src/*.py, config/*.yaml, tests/
                     │
                     ▼
              SOURCE LAYER
     official + academic + public sources  data/raw/ (checksummed, not committed), data/documentary/
```

The scholarly repository (e.g. Harvard Dataverse) archives the public data layer plus documentation for a tagged release; see `docs/DATAVERSE_DEPOSIT.md`.

## 5. Data

| Pillar | Indicator (in index) | Source | Status |
|---|---|---|---|
| W Water | Drought intensity | SMN-CONAGUA Drought Monitor, municipal file | derived (from administrative) |
| W Water | Aquifers without availability | CONAGUA availability 2023 | administrative |
| E Energy | Authorized generation capacity in operation per 100k people | CNE permit register + CONAPO | derived; estimated for 2026–2027 |
| E Energy | Combustion-based share of capacity | CNE permit register | derived; estimated for 2026–2027 |
| D Digital | Hyperscale cloud regions in operation | documentary register (provider notes, press) | documentary |
| V Territory | Population density | CONAPO + Natural Earth areas | modelled |
| V Territory | Marginalization index 2020 (direction −1) | CONAPO | derived |
| V Territory | Drought vulnerability | CONAGUA-PRONACOSE | modelled, undated |

Context and governance variables (never in the index): share of municipality-maps in drought, groundwater deficit per person, new self-supply capacity, announced cloud regions, population, five-year population growth, area under groundwater ordinances, area under vedas, number of state climate-policy instruments, and the national electricity-consumption series.

**What is not in the data, and why.** Facility-level electricity and water use of data centres is not published in Mexico, so no such variable exists in the dataset. State-level electricity consumption is published by SENER's SIE only behind a login, and CFE's open series is national, so the energy pillar measures the energy *system* hosted by each state (authorized capacity and its combustion share), not consumption. Compute, training or inference energy, PUE and cooling efficiency have no reliable Mexico-specific public measurements; they are documented as gaps rather than modelled.

## 6. Normalization

1. **Orientation.** Each indicator is multiplied by its `direction` so that higher always means more pressure. Marginalization is the only indicator with direction −1, because CONAPO's 2020 normalized index rises as marginalization falls.
2. **Transformation.** Strongly right-skewed indicators (density, capacity per capita, cloud-region counts) are `log1p`-transformed.
3. **Winsorization.** Values are clipped to the 2nd and 98th percentiles of the pooled reference distribution, except for zero-inflated indicators (more than half of reference values at the minimum), where clipping would erase the information the indicator carries.
4. **Scaling.** Min–max to 0–100 over the **pooled 2020–2025 distribution** of all states and years. Pooling makes years comparable: a change between years is a change in conditions, not a rescaling. Values outside the reference range (2026–2027) are clipped to [0, 100].

Alternative normalizations (pooled z-score clipped at ±3, pooled percentile rank) are run as sensitivity scenarios.

## 7. The Sociotechnical Resource Tension Index (SRTI)

```text
P_pit  = mean of available normalized indicators of pillar p for territory i, year t
         (computed only if ≥ 50% of the pillar's index indicators are available)

SRTI_it = Σ_p w_p · P_pit / Σ_p∈available w_p          p ∈ {W, E, D, V}
         (computed only if ≥ 3 pillars are available; otherwise empty)
```

When a pillar is missing, the weights of the remaining pillars are renormalized and the row carries the flag `PILLARS_RENORMALIZED`. Such values are not directly comparable with rows that use all four pillars; the site says so in the territory panel. In this release this happens in 2027, when the digital pillar cannot be observed.

**Weighting.** The baseline gives each pillar 25%. This is a transparent default chosen because no defensible empirical basis for other weights exists yet; it is not a claim that the four dimensions matter equally.

**Resource Baseline Index (RBI).** Including the digital pillar in an additive index quietly encodes the hypothesis that digital infrastructure *is* resource pressure. The RBI drops that pillar (W, E, V at one third each) so that resource pressure can be read on its own, and digital infrastructure can be examined as a separate layer that does or does not coincide with it.

## 8. Sensitivity analysis

| Specification | W | E | D | V | Aggregation | Normalization |
|---|---|---|---|---|---|---|
| Baseline | .25 | .25 | .25 | .25 | arithmetic | pooled min–max |
| Water-heavy | .40 | .20 | .20 | .20 | arithmetic | pooled min–max |
| Energy-heavy | .20 | .40 | .20 | .20 | arithmetic | pooled min–max |
| Digital-heavy | .20 | .20 | .40 | .20 | arithmetic | pooled min–max |
| Vulnerability-heavy | .20 | .20 | .20 | .40 | arithmetic | pooled min–max |
| RBI | .33 | .33 | 0 | .33 | arithmetic | pooled min–max |
| Geometric | .25 | .25 | .25 | .25 | geometric (on P + 1) | pooled min–max |
| Z-score | .25 | .25 | .25 | .25 | arithmetic | pooled z, clipped ±3 |
| Percentile | .25 | .25 | .25 | .25 | arithmetic | pooled percentile |

In addition, 2,000 weight vectors are drawn from a Dirichlet(4, 4, 4, 4) distribution (seed fixed in config). For every territory-year the pipeline reports the 5th–95th percentile of the composite and of its within-year rank. Agreement between each specification and the baseline is reported as Spearman's ρ per year in `data/public/sensitivity.csv`.

**Reading the sensitivity results.** A territory whose rank interval is narrow is ranked similarly under most plausible weightings. A wide interval means the ranking depends on value judgements about weights and should not be quoted without them.

## 9. Uncertainty and data coverage

Every index indicator in every territory-year gets a weight:

```text
weight = status_weight × recency × partial_year × undated_vintage
status_weight: observed / administrative 1.0 · geospatial 0.9 · derived 0.85 · documentary 0.7 ·
               estimated 0.6 · modelled 0.5 · hypothesized / unknown 0
recency:       1 − 0.15 × max(0, year − vintage − 1), floor 0.4
partial_year:  0.75 (2026 drought maps end in September)
undated:       0.7 (PRONACOSE vulnerability has no stated vintage)
```

Coverage is the mean of the four pillar means of these weights, so each pillar counts equally. Tiers: **high** ≥ 0.75, **moderate** ≥ 0.50, **limited** ≥ 0.25, otherwise **insufficient**, in which case no composite value is shown at all.

The map encodes coverage as texture, never only as colour: solid (high), stipple (moderate), diagonal hatch (limited), dashed outline with no fill (insufficient or no value). Every territory panel lists the index indicators by ledger class: what we know (observed, administrative, documentary, geospatial), what we derived, what we estimated, what we modelled, and what remains unknown.

## 10. Missing data

Missing is never zero. The pipeline writes a row for every expected (state, year, variable) combination; a missing value has an empty `value`, status `unknown`, and a reason flag (for example `NO_VINTAGE_FOR_YEAR`, `NO_MAPS_FOR_YEAR`, `FUTURE_YEAR_NOT_OBSERVABLE`). Validation fails the build if an empty value is not marked unknown, or an unknown row carries a value.

Two cases need explicit judgement:

- **Single-vintage sources** (aquifer availability 2023, marginalization 2020) are carried forward only forward in time, with the recency penalty and the flag `CARRIED_FORWARD`. They are never carried backward: aquifer availability is unknown for 2020–2022 in this release, so the water pillar for those years rests on drought alone, and its set of indicators changes in 2023. The territory panel flags such changes.
- **Documentary absence.** A state with no cloud region in the register is coded 0 with the flag `REGISTER_ABSENCE`. Hyperscale providers publish their region lists, so for the providers reviewed a zero is defensible; providers not yet reviewed are a known gap (`docs/ROADMAP.md`). A zero would not be defensible for data centres in general, which is why the indicator is restricted to hyperscale cloud regions.

## 11. Geographic resolution

States (32), identified by INEGI CVE_ENT codes. Drought and vulnerability are aggregated from municipalities with equal municipal weights; area- or population-weighted aggregation is planned. Aquifers are assigned to the state CONAGUA publishes for each, so no spatial crosswalk is needed for the water indicators. State areas and display geometry come from Natural Earth's generalized 1:10m boundaries; INEGI's Marco Geoestadístico should replace them for analytical use (`docs/ROADMAP.md`). State-level results hide within-state concentration.

## 12. Temporal resolution

Annual, 2020–2027. Drought maps are biweekly and averaged within each calendar year. 2026 includes drought maps up to 15 September 2026 (flag `PARTIAL_YEAR`), permits with operation dates planned after the February 2026 file date (status `estimated`), and the register as of 4 October 2026. 2027 is a projection year: drought and cloud regions are unknown, capacity rests on planned operation dates, and population on CONAPO projections.

## 13. Legal and institutional methodology

See `docs/LEGAL_LAYER.md`. The governance layer is kept separate from the index. It records instruments, dates, competences and neutral categories, and two geospatial descriptors (area under groundwater ordinances; area under vedas) plus a count of state climate-policy instruments. It never converts legal interpretation into a score, and it never labels anything unconstitutional, illegal, abusive, exploitative or harmful.

## 14. What the observatory does not claim

This observatory describes and models relationships among digital infrastructure, resource pressure and territorial conditions. It does not by itself establish causal relationships, legal violations or corporate responsibility. Correlation between pillars is not evidence that one drives another; a high SRTI is not evidence of harm; a governance instrument's existence is not evidence of its enforcement.

## 15. Reproducibility

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m src.run_pipeline --fetch     # download sources, verify, rebuild everything
pytest -q
```

`data/raw/MANIFEST.csv` records the SHA-256 of every raw file used in this release. Without `--fetch`, the pipeline refuses to run if any raw file differs from the manifest. Random elements (Monte Carlo) use a fixed seed. Outputs are deterministic given the raw files and config.

## References

- OECD & European Commission JRC (2008). *Handbook on Constructing Composite Indicators: Methodology and User Guide.* OECD Publishing.
- NOM-011-CONAGUA-2015, method for determining mean annual availability of national waters.
- Source-specific references: `docs/SOURCES.md`.
