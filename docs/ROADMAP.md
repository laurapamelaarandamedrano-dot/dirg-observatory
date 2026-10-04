# Roadmap and known limitations

## Known limitations of release 0.1.0
1. **Digital pillar rests on one indicator** (hyperscale cloud regions), concentrated in three states. Most states score 0 on it, which is why the digital-heavy scenario barely changes rankings. Colocation and enterprise data centres are not yet covered.
2. **Energy pillar measures the energy system, not consumption.** State electricity sales are behind a login on SENER's SIE; CFE's open series is national.
3. **Aquifer availability has a single vintage (2023).** 2020–2022 water scores rest on drought alone.
4. **Equal municipal weights** when aggregating drought and vulnerability to states.
5. **Generalized boundaries** (Natural Earth) for areas and display.
6. **Projection years.** 2026 is partial; 2027 is mostly unobservable.
7. **Legal layer** is federal only and partly based on secondary summaries pending DOF verification.

## Next releases
- Add CONAGUA availability vintages 2018 and 2020 (DOF) to remove the 2022/2023 break.
- Request SIE access or use PRODESEN state-consumption tables (documentary) for an electricity-consumption indicator.
- Extend the documentary register to colocation facilities with a written search protocol and review of more providers; keep the no-operator, no-coordinate rule.
- Municipal resolution for Querétaro, Nuevo León, Estado de México and Jalisco, with INEGI Marco Geoestadístico boundaries.
- REPDA concession volumes by use and municipality (industrial and service uses).
- State-level legal coding (water, environment, urban development laws).
- Population- or area-weighted municipal aggregation as a sensitivity scenario.
