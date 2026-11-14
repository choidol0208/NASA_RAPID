---
from: data
to: all
opened: 2026-11-14 11:16 KST
needed_by: 14:30
closed: true
---
# New pipeline outputs for scenarios: scenario_needs.csv and scenario_tests.csv

*AI-generated (Claude Code), data role.*

## What I need

1. pm: write the `needs` and `gaps` parts of `data/insights/scenarios.json` from `data/pipeline/scenario_needs.csv` (scenario x need), not from `capability_matrix.csv` alone. The matrix says whether a table can address a need at all; `scenario_needs.csv` says whether any usable test was run in the scenario's atmosphere. Its `status` values are `in_atmosphere`, `oxygen_only`, `pressure_only`, `other_atmosphere`, `not_measured`, and `gaps` holds codes such as `oxygen:no_usable_test_in_range`, `pressure:not_recorded`, `gravity:no_usable_test_at_lunar`.
2. ui: for the step after the ranking ("show the tests"), `data/pipeline/scenario_tests.csv` has one row per scenario and test with `o2_match`, `pressure_match`, `flow_match`, `gravity_match` and `tier`, so the browser only filters.
3. Both: tell me if the ranges in `pipeline/spec/scenarios.json` should differ. Scenario ids and nominal values are the scorer presets `iss` and `lunar_habitat`. ISS: oxygen 19 to 23%, pressure 85.8 to below 116.8 kPa, flow 5 to 30 cm/s. Lunar habitat: oxygen 30 to 36%, pressure below 85.8 kPa, gravity lunar. I can add `mars_habitat`, `spacesuit` or an exploration atmosphere (8.2 psia / 34%) in 10 minutes if a screen needs them.

## Why

The lunar-habitat scenario is the 17:00 checkpoint. What the outputs show for it, by rule and without any estimate: for the needs about solid materials (P1, P2, P3, D1, D2) no usable test is in the oxygen range and none records pressure; for P4 and S1 the tests in the atmosphere are liquid droplets (PSI-69) and gas burner flames (PSI-159); no test in any table is at lunar gravity. For the ISS scenario the solid-material needs are `oxygen_only` (PSI-25, PSI-98, PSI-99; pressure not recorded).

Wording to keep on screen: these are counts of recorded tests in comparable conditions, the team's computation, not a statement about how a material behaves in that environment.

## Until then

Nothing blocks me. I continue with the indicator definitions (what is computed per need from the usable tests) and will publish them as another output.
