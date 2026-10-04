# Legal and governance layer

The governance layer describes the institutional context in which water, energy, land and digital infrastructure are allocated. It is separate from the index and never converted into a numerical risk score, because there is no defensible methodological basis yet for scoring legal interpretation.

## Neutral categories

| Category | Use |
|---|---|
| `applicable_framework` | Norm that frames the subject (rights, definitions, methods) |
| `regulatory_constraint` | Norm that conditions an activity (permits, impact assessment, technical requirements) |
| `institutional_competence` | Norm that assigns powers to an authority or order of government |
| `policy_priority` | Plan, program or norm that sets priorities |
| `resource_allocation` | Mechanism that assigns a resource (concessions, fees by availability zone, reallocation) |
| `legal_question` | Open interpretive question relevant to the research |
| `data_insufficient` | The information needed to describe the situation is not available |
| `requires_legal_analysis` | The question cannot be answered descriptively and needs formal legal analysis |

The layer never labels anything unconstitutional, illegal, abusive, exploitative or harmful. Those are conclusions of legal and/or empirical analysis, not data.

## Contents in release 0.1.0

**Federal instruments** (`data/documentary/governance_instruments.csv`, 16 entries): constitutional articles 4, 6, 25/27/28, 27 and 115; Ley General de Aguas and the 2025 amendments to the Ley de Aguas Nacionales; NOM-011-CONAGUA-2015; Ley Federal de Derechos; the March 2025 electricity laws (Ley del Sector Eléctrico, Ley de la CNE, Ley de Planeación y Transición Energética); the July 2025 telecommunications law; LGEEPA; LGAHOTDU; LGCC. Each entry has a date, level, domains, neutral category, source, a neutral description, and where relevant an open question.

**Territorial governance descriptors** (state × year, not in the index):

- `g_groundwater_ordinance_area`: share of state area under at least one CONAGUA groundwater ordinance (veda, regulation/reserve, suspension of free pumping) with DOF date on or before the year;
- `g_veda_area`: share under vedas only;
- `g_climate_instruments`: number of state climate-policy instruments in the INECC register reported available.

These are descriptive. The near-universal ordinance coverage, for example, says that groundwater extraction everywhere in Mexico requires a concession; it says nothing about compliance.

## Verification status

| Item | Status |
|---|---|
| DOF date of the Ley General de Aguas (2025-12-11) | From the SCJN DOF synthesis; verify against the DOF edition before formal citation |
| Content of the 2025 water reform (no transfers between private parties; no change of use) | From law-firm summaries; verify against the decree |
| Date of the 2024 constitutional energy reform (2024-10-31) | To be verified against the DOF |
| Data-centre-specific federal regime | Not identified in secondary summaries; coded `data_insufficient` |
| State land-use, water and environmental laws | Not yet coded (roadmap) |

## Method for extending the layer

1. Add the instrument with its official source to `config/sources.yaml` first.
2. Add a row to `governance_instruments.csv` with a neutral description in English and Spanish and one category from the list above.
3. If the instrument has territorial expression in open data (polygons, lists of municipalities), add a governance variable to `config/variables.yaml` with `pillar: G` and `in_index: false`.
4. Record questions as questions. Never resolve them in the data.
