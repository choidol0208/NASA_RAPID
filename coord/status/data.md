---
role: data
updated: 2026-11-14 11:35 KST
state: working
blocked_on: none
---
Now: checking the indicator rows against the source tables; then the D6 pass.

Done since last sync:
- Merged `origin/main` into `data-pipeline` (fast-forward).
- Indicators: `indicators.csv`, `indicator_tests.csv`, spec `pipeline/spec/indicators.json` (20 indicators over 7 needs, three fixed templates).
- Material vocabulary: `pipeline/spec/materials.json`; new column `material_id` in `tests.csv` (the same fabric was written three ways in BASS, Saffire-I/III and Saffire-II). `fuel_material` is unchanged.
- Need D2 now also requires `aging_time_s`, so flame tests are no longer counted as smoke tests. In `capability_matrix.csv` the D2 rows for PSI-25, PSI-26, PSI-98, PSI-99, PSI-100 changed from `conditions_only` to `none`. No id or status value changed.
- Scenario matching: `scenario_needs.csv`, `scenario_tests.csv` (request 20261114-1116-data-to-all).
- D3: confirmed pm's coverage counts and published `data/pipeline/coverage_grid.csv` with its bin spec `pipeline/spec/coverage.json` (answer to request 20261114-1056-pm-to-data).
- Reference spec: `pipeline/spec/references.json` (21 documents, 56 items) and `data/pipeline/need_references.csv`.

Next: D5 when `data/insights/cards.json` exists on main; final D6 pass before 21:00.

Published for others (all written by `python3 pipeline/run.py`; shapes below are stable, I will only add columns):
- `data/pipeline/tests.csv` — 1,867 rows, one per test. Stable: `test_id`, `investigation_id`, `source_id`, every variable name in `pipeline/spec/variables.json` (36 standard including the new `material_id`, 5 derived), `flags`, `source_file`, `source_row`.
- `data/pipeline/values_long.csv` — 18,741 rows, one per value: `test_id`, `investigation_id`, `variable`, `kind`, `value`, `unit`, `source_file`, `source_row`, `source_column`. Stable.
- `data/pipeline/capability_matrix.csv` — 154 rows (7 needs x 22 tables): `need_id`, `pillar`, `need`, `investigation_id`, `source_id`, `row_unit`, `status`, `tests`, `tests_with_required_conditions`, `tests_with_outcome`, `usable_tests`, `required_missing`, `outcomes_present`, `note`. Status values: `measured`, `partial`, `conditions_only`, `none`, `out_of_scope`, `not_test_level`. Stable.
- `data/pipeline/need_tests.csv` — 1,632 rows: `need_id`, `test_id`, `investigation_id`. Stable.
- `data/pipeline/coverage_grid.csv` — NEW, 109 rows: `fuel_phase`, `o2_basis`, `o2_bin`, `o2_bin_label`, `pressure_bin`, `pressure_bin_label`, `tests`, `investigation_ids`, `source_ids`. Bin ids may still change today if pm or ui ask for other edges; column names are stable.
- `data/pipeline/scenario_needs.csv` — NEW, 14 rows (2 scenarios x 7 needs): `scenario_id`, `need_id`, `need`, `usable_tests`, `tests_<tier>` and `investigations_<tier>` for tiers `atmosphere`, `oxygen_only`, `pressure_only`, `other`, `status`, `matched_tests_flow_in_range`, `matched_tests_flow_not_recorded`, `matched_tests_same_gravity`, `gaps`, `scenario_gravity_level`. Column names stable; more scenarios may be added as rows.
- `data/pipeline/scenario_tests.csv` — NEW, 3,734 rows (2 scenarios x 1,867 tests): `scenario_id`, `test_id`, `investigation_id`, `source_id`, `fuel_phase`, `o2_match`, `pressure_match`, `flow_match`, `gravity_match`, `tier`. Stable.
- `data/pipeline/indicators.csv` — NEW, 197 rows: `indicator_id`, `need_id`, `label`, `group` (`key=value;key=value`), `stat` (`min`, `median`, `max`, `count`), `category`, `value`, `unit`, `n_tests`, `investigation_ids`, `variable`, `definition_ref`, `compare_with`, `reading`. Column names stable; indicator ids may grow.
- `data/pipeline/indicator_tests.csv` — NEW, 1,850 rows: `indicator_id`, `group`, `test_id`, `value`. The tests behind each indicator row.
- `pipeline/spec/indicators.json`, `pipeline/spec/materials.json` — NEW.
- `pipeline/spec/scenarios.json` — NEW: the scenario ranges and their basis. Ids equal the scorer presets `iss`, `lunar_habitat`.
- `data/pipeline/need_references.csv` — NEW, 56 rows: for each need, the standard or published item behind it (`item_type`, `text`, `where`, `values`, `reference_id`, `title`, `version`, `access`, `url`). Stable.
- `pipeline/spec/needs.json` — need ids `P1`-`P4`, `S1`, `D1`, `D2` are stable. Each need now also has `scope` and `references`.
- `pipeline/spec/references.json`, `pipeline/spec/coverage.json` — NEW.
- `data/pipeline/run_report.json` — row counts, flags, unmapped source columns.

Notes for other roles:
- An investigation can have more than one table (`source_id`): PSI-10 and PSI-159 have a normal-flame and an inverse-flame table. Join on `investigation_id` to reach the catalog, on `source_id` to reach a table.
- Eight tables are not test-level and have no rows in `tests.csv` (PSI-20, 21, 22, 23, 47, 68, 106, 142). They appear in `capability_matrix.csv` with status `not_test_level`. PSI-60, 62, 115, 117 have no experimental table at all.
- `o2_basis = oxidizer_stream` is not a habitat atmosphere; do not mix those rows with `ambient` (see the answer file).
- No solid-fuel test has a recorded pressure. Empty means not recorded, never 101 kPa.
- `flags` is a `;`-separated list of `variable:reason`. A flagged value is either kept as written (approximate, range midpoint) or left empty (unreadable, out of range). Show the flag where you show the value.
- Values in `references.json` (for example the 15 cm burn length of NASA-STD-6001B Test 1, or the CO exposure limits of JSC 20584) are carried next to the data. The pipeline does not judge any test against them, and the CO limits are crew exposure limits for cabin air, not limits for a test duct. Please do not compare BASS-II CO readings with them on screen.
- Indicators describe what was recorded. Show `reading` with the value: for example `P1.o2_tested` min is the lowest oxygen tested, not a flammability limit. `compare_with` points to a published result in `references.json`; the pipeline does not make the comparison, and neither should a screen without saying so.
- Many indicator rows rest on one or two tests (`n_tests`). Show `n_tests` next to every value.
- If you need a JSON copy of a CSV or a per-investigation index, open a request; it is a 10-minute job.
