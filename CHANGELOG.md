# Changelog

## 0.1.0 · 2026-10-04
First public release.
- Sources: 13 official/open datasets (SMN, CONAPO, CONAGUA, CNE, INECC, CFE, Natural Earth) and a documentary register of 8 hyperscale cloud regions (no operators, no coordinates), plus 9 legal sources.
- Official files downloaded on 2026-10-04 from the URLs in `config/sources.yaml` via a desktop browser session (the build environment could not reach `.gob.mx` hosts); SHA-256 recorded in `data/raw/MANIFEST.csv`.
- SRTI (equal weights), Resource Baseline Index, 8 alternative specifications, 2,000-draw Dirichlet Monte Carlo.
- Coverage scores and tiers for every territory-year; texture-encoded uncertainty on the map.
- Ingestion exclusions recorded in the quality report: 12 permits with impossible capacities (> 5,000 MW), 16 with probable kW/MW unit errors, 99 marked ended without an end date, 161 without a recognisable state.
