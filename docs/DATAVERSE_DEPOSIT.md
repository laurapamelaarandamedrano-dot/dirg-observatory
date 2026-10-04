# Scholarly deposit package (Harvard Dataverse)

The GitHub repository is the computational layer; the scholarly repository is the archival data layer; GitHub Pages is the public visualization layer.

## Build the package
```bash
python -m src.run_pipeline
python scripts/make_deposit.py      # writes dist/dirg-observatory-v0.1.0-dataverse.zip
```

## Contents
| File | Description |
|---|---|
| `observations.csv` | Long table, state × year × variable, with status, sources, flags |
| `index_results.csv` | SRTI, RBI and all sensitivity scenarios; Monte Carlo intervals |
| `coverage.csv` | Coverage scores and tiers |
| `variables.csv`, `methods.csv` | Data dictionary and method definitions |
| `sources.csv` | Source registry with licenses and redistribution status |
| `territories.csv` | State codes, names, areas |
| `digital_infrastructure_register.csv` | Documentary register (no operators, no coordinates) |
| `governance_instruments.csv` | Federal legal and institutional instruments |
| `sensitivity.csv` | Spearman correlations of each scenario with the baseline |
| `QUALITY_REPORT.md`, `production_audit.json` | Validation and audit outputs |
| `METHODOLOGY.md`, `DATA_DICTIONARY.md`, `SOURCES.md`, `DATA_GOVERNANCE_AUDIT.md`, `LEGAL_LAYER.md` | Documentation |
| `MANIFEST.csv` | SHA-256 of each raw input (raw files themselves are not deposited) |
| `CITATION.cff`, `CHANGELOG.md`, `LICENSE-DATA` | Citation, version history, license |

Raw source files are **not** deposited; restricted or unclear-license material stays out, and the manifest lets anyone verify that a re-download matches.

## Suggested metadata
- **Title:** Digital Infrastructure & Resource Governance Observatory: Mexico, 2020–2027 (v0.1.0)
- **Author:** Aranda Medrano, Laura Pamela
- **Subject:** Earth and Environmental Sciences; Law; Social Sciences
- **Keywords:** digital infrastructure; data centres; water governance; energy; Mexico; composite indicators; uncertainty
- **Description:** use the first paragraph of README.md plus the disclaimer.
- **License:** CC BY 4.0 for derived data; source data keep their own licenses as listed in `sources.csv`.
- **Related material:** GitHub repository URL and release tag; observatory URL.
- **Version:** 0.1.0; data as of 2026-10-04.
