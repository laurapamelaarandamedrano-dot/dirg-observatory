# Research design (Phase 1)

## Question
How does the expansion of digital infrastructure relate to energy demand, water pressure and resource governance in Mexico, 2020–2027?

## Sub-questions the instrument is built to support
1. Where does documented digital infrastructure locate, and how has that changed since 2019?
2. Do those territories coincide with high water pressure (drought, aquifers without availability)?
3. What energy systems do those territories host (capacity, combustion share, self-supply growth)?
4. Under which groundwater ordinances and policy instruments are resources allocated there?
5. How robust are any such coincidences to the weighting, normalization and aggregation choices?

None of these sub-questions is causal. Causal designs (e.g. event studies around region openings using municipal water-concession or electricity data) are listed in `docs/ROADMAP.md` and require data the open record does not yet provide.

## Agnostic design rules
- Variables measure conditions, not conclusions. No variable is named or oriented to imply harm.
- The digital pillar is reported both inside (SRTI) and outside (RBI) the composite.
- The dataset works with operator identity removed; operator identity is not collected.
- Hypotheses live in this file, not in the data. The status `hypothesized` exists in the schema but carries weight 0 and no hypothesized value is published.

## Working hypotheses (to be tested, not assumed)
- H1: Hyperscale cloud regions concentrate in states with above-median water pressure. (Testable descriptively with the current data.)
- H2: States receiving cloud regions show growth in self-supply generation capacity after opening dates. (Needs facility-to-permit linkage that this project deliberately does not make; would require a separate ethics and data-governance review.)
- H3: Groundwater ordinances do not differentiate digital infrastructure from other industrial and service uses. (Legal analysis.)

## Unit of analysis
State × year (32 × 8). Facility × state × year exists only inside the documentary register and is aggregated before use. Municipal, aquifer and basin levels are reserved in the schema (`territory_level`) for future releases.

## Variables
See `docs/DATA_DICTIONARY.md` (generated). Status taxonomy: observed, administrative, documentary, geospatial, derived, estimated, modelled, hypothesized, unknown.

## Source strategy
Official open data first (CONAGUA, SMN, CONAPO, CNE, INECC, CFE via datos.gob.mx), then provider documentation, then trade press, each tagged with its type and redistribution status. No source is used before it is registered.

## Index architecture, uncertainty, reproducibility
See `docs/METHODOLOGY.md` sections 6–10 and 15.
