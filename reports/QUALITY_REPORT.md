# Data quality report

```text
DATA QUALITY
────────────

Observations: 4,352 (4,032 with a value)
Territories:  32
Years:        2020–2027
Variables:    17

Index indicator cells (state × year × indicator):
  Complete:     64.1%
  Partial:      28.1%   (present, but carried forward, partial-year, undated or projected)
  Missing:      7.8%

Coverage tiers (territory-years): {'moderate': 224, 'limited': 32}
Checks: 30 pass · 0 warn · 0 fail
Last validation: 2026-10-04 (data as of 2026-10-04)
```

| Check | Status | Count | Detail |
|---|---|---|---|
| duplicate_observations | pass | 0 | territory × year × variable must be unique |
| geographic_identifiers | pass | 0 | unknown territory ids: [] |
| variables_registered | pass | 0 | variables not in config/variables.yaml: [] |
| units_consistent | pass | 0 | variables with inconsistent units: [] |
| impossible_values | pass | 0 | values outside plausible_range:  |
| missing_years | pass | 10 | years with no value at all, by variable: {"d_cloud_regions": [2027], "d_cloud_regions_announced": [2027], "w_aquifer_deficit_share": [2020, 2021, 2022], "w_aquifer_deficit_volume_pc": [2020, 2021, 2022], "w_drought_intensity": [2027], "w_drought_share": [2027]} |
| unknown_never_has_value | pass | 0 | rows marked unknown must have an empty value |
| missing_never_zero | pass | 0 | empty values must be marked unknown (never silently zero) |
| outliers_flagged | pass | 88 | robust z > 5 within variable-year (flagged for review, NOT removed) |
| source_registry_match | pass | 0 | source ids not in registry: [] |
| variable_sources_registered | pass | 0 | variable source ids not in registry: [] |
| source_metadata_complete | pass | 0 | missing: [] |
| variable_metadata_complete | pass | 0 | variables lacking EN/ES definitions: [] |
| normalization_range | pass | 0 | normalized indicators must lie in [0, 100] |
| composite_range | pass | 0 | composite values must lie in [0, 100] |
| no_illustrative_rows | pass | 0 | observations not flagged public (illustrative/restricted) |
| geometry_valid | pass | 0 | invalid geometries (repaired with make_valid when used): 0 |
| coordinates_in_mexico | pass |  | bounds [np.float64(-118.37), np.float64(14.55), np.float64(-86.7), np.float64(32.71)] |
| ingest:S01:INFO_MAPS | pass |  | 435 drought maps, 2478 municipalities, last map 2026-09-15 |
| ingest:S03:INFO_AQUIFERS | pass |  | 653 aquifers; 286 with negative availability |
| ingest:S07:UNMATCHED_STATE | pass | 161 | permits without a recognisable state (e.g. 'PERMISO RENUNCIADO', 'sin dato'); excluded: ['PERMISO RENUNCIADO', 'Texas', 'sin dato'] |
| ingest:S07:EXCLUDED_IMPORT_EXPORT | pass | 77 | import/export permits excluded |
| ingest:S07:MISSING_CAPACITY | pass | 4 | permits with no authorized capacity; excluded |
| ingest:S07:IMPOSSIBLE_VALUE | pass | 12 | authorized capacity > 5,000 MW for a single permit (max 3,304,269 MW); excluded as data-entry error |
| ingest:S07:SUSPECT_UNIT | pass | 16 | permits > 100 MW whose estimated annual generation implies a capacity factor < 0.2% (likely kW recorded as MW); excluded |
| ingest:S07:OP_DATE_IMPUTED | pass | 1091 | ended permits without an operation date: grant date used as start (flagged) |
| ingest:S07:ENDED_WITHOUT_DATE | pass | 99 | permits marked ended but with no end date; excluded from all years |
| ingest:S07:INFO_PERMITS | pass |  | 2545 permits in file; 2176 usable after exclusions |
| ingest:S09:INFO_MUNICIPALITIES | pass |  | 2463 municipalities; rows with any missing component: 0 |
| ingest:S10:NO_PUBLICATION_YEAR | pass | 35 | available instruments without publication year; not counted |

## Flagged outliers (robust z > 5; retained)

| Variable | Year | Territory | Value | z |
|---|---|---|---|---|
| c_pop_growth_5y | 2020 | Quintana Roo | 22.067 | 6.8 |
| c_pop_growth_5y | 2021 | Quintana Roo | 19.380 | 5.6 |
| c_pop_growth_5y | 2022 | Quintana Roo | 16.729 | 5.5 |
| c_population | 2020 | Estado de México | 17236788.000 | 7.0 |
| c_population | 2021 | Estado de México | 17291050.000 | 7.0 |
| c_population | 2022 | Estado de México | 17379644.000 | 7.0 |
| c_population | 2023 | Estado de México | 17501220.000 | 6.9 |
| c_population | 2024 | Estado de México | 17616018.000 | 6.9 |
| c_population | 2025 | Estado de México | 17723173.000 | 6.9 |
| c_population | 2026 | Estado de México | 17822420.000 | 6.8 |
| c_population | 2027 | Estado de México | 17914087.000 | 6.8 |
| e_capacity_per_100k | 2022 | Colima | 509.294 | 5.2 |
| e_combustion_share | 2023 | Aguascalientes | 0.737 | -5.6 |
| e_combustion_share | 2023 | Chiapas | 1.912 | -5.5 |
| e_combustion_share | 2023 | Michoacán | 5.136 | -5.3 |
| e_combustion_share | 2023 | Nayarit | 2.671 | -5.4 |
| e_combustion_share | 2023 | Oaxaca | 6.340 | -5.2 |
| e_combustion_share | 2023 | Zacatecas | 5.373 | -5.3 |
| g_groundwater_ordinance_area | 2020 | Baja California | 97.463 | -11.7 |
| g_groundwater_ordinance_area | 2020 | Baja California Sur | 98.670 | -5.8 |
| g_groundwater_ordinance_area | 2020 | Colima | 96.190 | -17.9 |
| g_groundwater_ordinance_area | 2020 | Oaxaca | 95.774 | -19.9 |
| g_groundwater_ordinance_area | 2020 | Quintana Roo | 98.312 | -7.5 |
| g_groundwater_ordinance_area | 2021 | Baja California | 97.463 | -12.0 |
| g_groundwater_ordinance_area | 2021 | Baja California Sur | 98.670 | -6.0 |
| g_groundwater_ordinance_area | 2021 | Colima | 96.190 | -18.4 |
| g_groundwater_ordinance_area | 2021 | Quintana Roo | 98.312 | -7.8 |
| g_groundwater_ordinance_area | 2021 | Tamaulipas | 98.841 | -5.1 |
| g_groundwater_ordinance_area | 2022 | Baja California | 97.463 | -12.0 |
| g_groundwater_ordinance_area | 2022 | Baja California Sur | 98.670 | -6.0 |
| g_groundwater_ordinance_area | 2022 | Colima | 96.190 | -18.4 |
| g_groundwater_ordinance_area | 2022 | Quintana Roo | 98.312 | -7.8 |
| g_groundwater_ordinance_area | 2022 | Tamaulipas | 98.841 | -5.1 |
| g_groundwater_ordinance_area | 2023 | Baja California | 97.463 | -12.0 |
| g_groundwater_ordinance_area | 2023 | Baja California Sur | 98.670 | -6.0 |
| g_groundwater_ordinance_area | 2023 | Colima | 96.190 | -18.4 |
| g_groundwater_ordinance_area | 2023 | Quintana Roo | 98.312 | -7.8 |
| g_groundwater_ordinance_area | 2023 | Tamaulipas | 98.841 | -5.1 |
| g_groundwater_ordinance_area | 2024 | Baja California | 97.463 | -12.0 |
| g_groundwater_ordinance_area | 2024 | Baja California Sur | 98.670 | -6.0 |
| g_groundwater_ordinance_area | 2024 | Colima | 96.190 | -18.4 |
| g_groundwater_ordinance_area | 2024 | Quintana Roo | 98.312 | -7.8 |
| g_groundwater_ordinance_area | 2024 | Tamaulipas | 98.841 | -5.1 |
| g_groundwater_ordinance_area | 2025 | Baja California | 97.463 | -12.0 |
| g_groundwater_ordinance_area | 2025 | Baja California Sur | 98.670 | -6.0 |
| g_groundwater_ordinance_area | 2025 | Colima | 96.190 | -18.4 |
| g_groundwater_ordinance_area | 2025 | Quintana Roo | 98.312 | -7.8 |
| g_groundwater_ordinance_area | 2025 | Tamaulipas | 98.841 | -5.1 |
| g_groundwater_ordinance_area | 2026 | Baja California | 97.463 | -12.0 |
| g_groundwater_ordinance_area | 2026 | Baja California Sur | 98.670 | -6.0 |
| g_groundwater_ordinance_area | 2026 | Colima | 96.190 | -18.4 |
| g_groundwater_ordinance_area | 2026 | Quintana Roo | 98.312 | -7.8 |
| g_groundwater_ordinance_area | 2026 | Tamaulipas | 98.841 | -5.1 |
| g_groundwater_ordinance_area | 2027 | Baja California | 97.463 | -12.0 |
| g_groundwater_ordinance_area | 2027 | Baja California Sur | 98.670 | -6.0 |
| g_groundwater_ordinance_area | 2027 | Colima | 96.190 | -18.4 |
| g_groundwater_ordinance_area | 2027 | Quintana Roo | 98.312 | -7.8 |
| g_groundwater_ordinance_area | 2027 | Tamaulipas | 98.841 | -5.1 |
| v_pop_density | 2020 | Ciudad de México | 6786.623 | 94.2 |
| v_pop_density | 2020 | Estado de México | 789.746 | 10.1 |
| v_pop_density | 2021 | Ciudad de México | 6743.032 | 92.3 |
| v_pop_density | 2021 | Estado de México | 792.232 | 10.0 |
| v_pop_density | 2022 | Ciudad de México | 6717.576 | 90.6 |
| v_pop_density | 2022 | Estado de México | 796.292 | 9.9 |
| v_pop_density | 2023 | Ciudad de México | 6705.936 | 89.1 |
| v_pop_density | 2023 | Estado de México | 801.862 | 9.8 |
| v_pop_density | 2024 | Ciudad de México | 6693.123 | 87.7 |
| v_pop_density | 2024 | Estado de México | 807.122 | 9.7 |
| v_pop_density | 2025 | Ciudad de México | 6678.318 | 86.3 |
| v_pop_density | 2025 | Estado de México | 812.031 | 9.6 |
| v_pop_density | 2026 | Ciudad de México | 6661.089 | 84.9 |
| v_pop_density | 2026 | Estado de México | 816.579 | 9.6 |
| v_pop_density | 2027 | Ciudad de México | 6641.286 | 83.6 |
| v_pop_density | 2027 | Estado de México | 820.779 | 9.5 |
| w_aquifer_deficit_volume_pc | 2023 | Chihuahua | 775.860 | 14.8 |
| w_aquifer_deficit_volume_pc | 2024 | Chihuahua | 766.431 | 14.7 |
| w_aquifer_deficit_volume_pc | 2025 | Chihuahua | 757.593 | 14.6 |
| w_aquifer_deficit_volume_pc | 2026 | Chihuahua | 749.404 | 14.6 |
| w_aquifer_deficit_volume_pc | 2027 | Chihuahua | 741.861 | 14.5 |
| w_drought_intensity | 2025 | Baja California | 38.393 | 10.0 |
| w_drought_intensity | 2025 | Coahuila | 27.988 | 7.1 |
| w_drought_intensity | 2025 | Chihuahua | 44.154 | 11.6 |
| w_drought_intensity | 2025 | Durango | 24.653 | 6.2 |
| w_drought_intensity | 2025 | Sinaloa | 41.354 | 10.8 |
| w_drought_intensity | 2025 | Sonora | 53.053 | 14.1 |
| w_drought_intensity | 2026 | Coahuila | 16.331 | 13.3 |
| w_drought_intensity | 2026 | Tamaulipas | 10.123 | 8.0 |
| w_drought_share | 2026 | Coahuila | 31.734 | 6.5 |
