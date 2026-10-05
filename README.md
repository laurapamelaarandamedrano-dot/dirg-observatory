# Digital Infrastructure & Resource Governance Observatory

**Water, energy, digital infrastructure and environmental pressure in Mexico, 2020–2027**

A reproducible research instrument for studying where digital infrastructure, water pressure, energy systems and the institutions that allocate resources coincide in Mexico's 32 states. Python builds every number from official open data; a static site on GitHub Pages lets anyone explore it on a rotating globe, year by year, with the source, status and uncertainty of each value one click away.

> This observatory describes and models relationships among digital infrastructure, resource pressure and territorial conditions. It does not by itself establish causal relationships, legal violations or corporate responsibility.

| | |
|---|---|
| **Why it matters** | Cloud and data-centre investment in Mexico is growing while drought, aquifer deficits and energy-system reforms reshape how water and electricity are allocated. Public debate often moves faster than the evidence. This project builds the evidence base without assuming the answer. |
| **Data** | CONAGUA/SMN drought monitor and aquifer availability, CONAGUA groundwater ordinances, CNE generation permits, CONAPO population and marginalization, CONAGUA-PRONACOSE vulnerability, INECC climate instruments, CFE national consumption, and a documentary register of hyperscale cloud regions. 31 sources registered with license and redistribution status. |
| **The index** | The **Sociotechnical Resource Tension Index (SRTI)** averages four pillars (water, energy-system intensity, digital infrastructure, territorial vulnerability) on pooled 0–100 scales. The **Resource Baseline Index (RBI)** drops the digital pillar so resource pressure can be read without assuming infrastructure is part of it. |
| **Uncertainty** | Every value carries an epistemic status (observed, administrative, documentary, geospatial, derived, estimated, modelled, unknown). Every territory-year has a coverage score and tier, shown on the map as texture. Eight alternative specifications and 2,000 random weightings give rank intervals. |
| **What it does not claim** | Causation, harm, illegality or responsibility of any actor. The data model has no company field, and operator identities are not collected. |
| **Observatory** | <https://laurapamelaarandamedrano-dot.github.io/dirg-observatory/> |

## Reproduce

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.run_pipeline --fetch     # download official sources, verify checksums, rebuild everything
pytest -q
python -m http.server -d site 8000     # open http://localhost:8000
```

`data/raw/MANIFEST.csv` stores the SHA-256 of every raw file used in the current release. If an official source has changed upstream, `--fetch` stops and reports it; review the change, re-run with `--fetch --accept-updates`, and log it in `CHANGELOG.md`.

`python -m src.run_pipeline --from-processed` rebuilds the validation report, documentation and site from the committed processed data without network access. The deploy workflow uses it, because official `.gob.mx` hosts are not always reachable from CI runners; a monthly scheduled job re-fetches the sources and fails loudly if anything changed.

## Pipeline

```text
src/ingest.py           official URLs → data/raw (+ MANIFEST.csv checksums)
src/clean.py            raw → tidy state × year × variable observations (missing ≠ 0; names/addresses dropped)
src/calculate_index.py  orientation, transforms, pooled normalization, pillars, SRTI/RBI, scenarios, Monte Carlo
src/uncertainty.py      coverage scores, tiers, epistemic ledger
src/validate.py         30 automated checks → reports/QUALITY_REPORT.md
src/build_geojson.py    simplified TopoJSON for display (analysis uses full geometry)
src/build_docs.py       DATA_DICTIONARY.md and SOURCES.md generated from config
src/build_site.py       public CSVs, site payload, generated explanations, static HTML
src/audit_production.py privacy / redistribution / illustrative-data audit (blocks deployment)
```

The browser code (`site_src/assets/js/observatory.js`) is a renderer only: every number, label and explanatory sentence on the site is produced by Python into `site/data/observatory.json`.

## Repository layout

```text
config/         variables, scenarios (all methodological parameters), sources, interface text (EN/ES)
data/raw/       raw downloads (not committed) + MANIFEST.csv
data/documentary/ hand-coded registers: cloud regions (no operators, no coordinates), legal instruments
data/processed/ pipeline outputs
data/public/    the published dataset (CSV)
geo/            Natural Earth Mexico states, world-atlas land
site_src/       HTML template, CSS, renderer JS, vendored d3 7.9.0 and topojson-client 3.1.0
site/           built static site (GitHub Pages artifact)
docs/           methodology, data dictionary, sources, governance audit, legal layer, research design, roadmap, deposit
tests/          pytest suite for the methodological rules
```

## Methodology and governance

- [Methodology](docs/METHODOLOGY.md): question, unit of analysis, normalization, index, weighting, sensitivity, uncertainty, missing data, resolution, legal method, reproducibility
- [Data dictionary](docs/DATA_DICTIONARY.md) and [source registry](docs/SOURCES.md) (both generated)
- [Data governance audit](docs/DATA_GOVERNANCE_AUDIT.md): what is published, what is never published, and why
- [Legal layer](docs/LEGAL_LAYER.md): neutral categories; no legal conclusions in data
- [Research design](docs/RESEARCH_DESIGN.md), [roadmap and known limitations](docs/ROADMAP.md)
- [Quality report](reports/QUALITY_REPORT.md)

## Three layers

GitHub (this repository) is the computational layer. A scholarly repository such as Harvard Dataverse is the archival data layer: `python scripts/make_deposit.py` packages the public dataset, documentation, quality reports and manifest (no raw files) as described in [docs/DATAVERSE_DEPOSIT.md](docs/DATAVERSE_DEPOSIT.md). GitHub Pages is the public visualization layer.

## License and citation

Code: MIT ([LICENSE](LICENSE)). Derived data: CC BY 4.0 ([LICENSE-DATA](LICENSE-DATA)). Source data keep their own licenses.

Aranda Medrano, L. P. (2026). *Digital Infrastructure & Resource Governance Observatory: Mexico, 2020–2027* (Version 0.1.0) [Data set and software]. See [CITATION.cff](CITATION.cff).
