# Data governance audit

Release 0.1.0 · audited 2026-10-04 · automated checks: `src/audit_production.py` (blocks deployment on failure)

This file records explicit decisions about what may and may not be published. The public dataset contains only public, public-aggregated, derived and modelled information.

## 1. Decisions by source

| Source | Raw content | Decision | Reason |
|---|---|---|---|
| S01 SMN drought monitor | Municipality × date drought categories | Publish state-year aggregates only (`derived_only`). Raw file fetched by script, not committed. | No explicit license stated on the file; aggregates are the project's own derived work. |
| S02 CONAPO projections | State-year demographics | Publish the values used. | CC BY 4.0. |
| S03 CONAGUA aquifer availability | Aquifer polygons and volumes | Publish state aggregates; raw fetched by script. | CC BY 4.0; repository size. |
| S04–S06 CONAGUA groundwater ordinances | Polygons, decree names, DOF links | Publish state area shares only. | CC BY 4.0; geometry not needed publicly. |
| S07 CNE generation permits | **Permit-holder names, street addresses with coordinates**, capacities, technologies | **Names, addresses and country of origin are dropped at ingestion** (first lines of `clean.permits`). Publish only state-year sums of authorized MW and shares. | Data minimisation; the project is company-agnostic; coordinates of energy assets are unnecessary for state-level analysis. |
| S08 CONAPO marginalization | State indices | Publish values used. | CC BY 4.0. |
| S09 PRONACOSE vulnerability | Municipal probabilities | Publish state means. | CC BY 4.0. |
| S10 INECC climate instruments | Instrument names, links | Publish state-year counts; instrument names are public policy documents but are not needed. | CC BY 4.0. |
| S11 CFE national consumption | National monthly series | Publish annual totals. | CC BY 4.0. |
| S12–S13 Natural Earth / world-atlas | Boundaries | Publish simplified display geometry. | Public domain / ISC. |
| S20–S28 documentary web sources | Copyrighted articles and provider pages | `metadata_only`: cite, record dates and facts; never copy text. | Copyright. |
| S40–S48 legal texts | Official legal texts | Cite and summarize neutrally. | Official texts are public; law-firm summaries are cited, not reproduced. |

Publicly accessible is not treated as freely redistributable. Where terms are unclear (S01), the project publishes only its own aggregates.

## 2. Digital-infrastructure register

| Field | Published? | Decision |
|---|---|---|
| Operator / company name | **No. Not collected.** | The research object is the structural phenomenon. Deduplication was done during desk research; the record keeps an opaque id. Source citations remain public, so the evidence trail is auditable. |
| Facility coordinates or address | **No. Not collected.** | Precise locations of critical infrastructure create security concerns and add nothing at state resolution. Map markers sit at the state's representative point, and the legend says so. |
| State, dates, availability zones, location confidence, source ids | Yes | Needed for the indicator and its audit trail. |
| Reported capacity (MW) | Context only (one record, S28) | Unattributed trade-press figure; never in the index. |

## 3. Personal and sensitive data

The public layer must not contain: personal data, CURP, RFC, phone numbers, private e-mail addresses, credentials, passwords, access tokens, confidential government information, industrial secrets, restricted internal information, unauthorized company information, private addresses, or unnecessarily precise coordinates of sensitive infrastructure.

Automated checks on every build (`src/audit_production.py`):

- regex scans of every public CSV and of `observatory.json` for CURP, RFC, e-mail, Mexican phone-number and degree-minute coordinate patterns;
- forbidden column names (`permisionario`, `direccion`, `pais_origen`, `operator`, `company`, `lat`, `lon`, …);
- no raw source files (`.xlsx`, `.zip`, raw CNE/SMN CSVs) inside `site/`;
- no source with `redistribution ≠ raw_ok` has its raw file in the public layer;
- no row with `release_flag` other than `public`; no `ILLUSTRATIVE / DEVELOPMENT ONLY` label;
- register records carry no location fields; map anchors match the 32 states exactly.

Result for this release: see `reports/production_audit.json` (status `pass`, 0 problems at build time).

## 4. Illustrative data

No illustrative or synthetic value exists in this release. The schema supports `release_flag = illustrative` for development fixtures; the validator and the production audit both fail the build if such a row reaches `data/public` or `site/`.

## 5. Secrets

The pipeline needs no API key or token. The GitHub Actions workflow uses only the built-in `GITHUB_TOKEN` scoped to Pages deployment.

## 6. Open items

- Confirm SMN terms of use for the municipal drought file (S01) and upgrade to `raw_ok` if permitted.
- Before adding any facility-level layer (e.g. municipal resolution), repeat this audit; default decision for coordinates remains **exclude**.
