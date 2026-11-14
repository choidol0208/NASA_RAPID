---
role: data
updated: 2026-11-14 13:07 KST
state: working
blocked_on: none
---
Now: a final acceptance review of the evidence layer by a reviewer that was not involved (reproduce, trace 35 values to the raw cells, read two packages as a judge); then D5 when `ai/review/review_sheet.csv` lands.

Done since last sync (details and before/after numbers: request 20261114-1242-data-to-all "Audit fixes"):
- Evidence layer is on `data-pipeline` (commit `a454a92` and later): `data/pipeline/evidence/` (6 scenarios, 20 oxygen x pressure cells, `index.json`), `atmosphere_cells.csv`, `investigation_facts.json`, `pipeline/check.py` with `validation_report.json`.
- Three independent audits by sub-agents (counts recomputed from the raw tables without the pipeline; over-generalisation of the needs; citations against the documents) found real errors, now fixed: note and figure numbers read as values (Saffire-II spread rate 4.0 mm/s was the cell "Note 4"), BASS-II fan potentiometer settings read as flow, a maintenance row and 42 repeated rows counted as tests, paraffin labelled Japan wax, the lowest-oxygen BASS-II test dropped from P1, igniter settings treated as outcomes, objective links applied unevenly, 13 reference entries.
- Need P4 removed (pm's decision). Six needs. 1,824 test rows (was 1,867).
- Objective links use the `objective` field of the PSI record only. Each need has a `reading`: what a counted test records and what the count does not mean.
- New: scenario `exploration_10_2_26_5`; `added_gas` mark; gap codes `flow:not_recorded`, `flow:no_usable_test_in_range`; `see_also` pointers from scenarios to PSI-20 and PSI-23 (records and cells that name exploration atmospheres and are not in the counts); `documented_elsewhere` sentences (for example BASS-II: "Pressure was not varied from 1 atmosphere.", from the investigators' paper, shown next to the pressure gap and never used as a value).
- Checker: 43 of 43 checks pass (`python3 pipeline/check.py`). Values that are not literally in a NASA cell (87 material names from the BASS-II ReadMe, 3 oxygen midpoints, 2 materials from the row above) pass only because each carries its flag; they are listed in `pipeline/README.md`.
- pm's two reference items are in `references.json`: `SAF456.conditions` (ICES-2024-365, Table 1) and `OF2012.table1` (Olson and Ferkul 2012, Table I), both read cell by cell from the PDFs. See the answer to request 1224.
- Wording pass over the remaining audit findings (commit `d9f5846`): `label`, `reading`, `note` and `_meta` texts only; no id, range, link or number changed, and `tests.csv`, `values_long.csv`, `need_tests.csv`, `scenario_needs.csv`, `scenario_tests.csv`, `coverage_grid.csv`, `capability_matrix.csv` are byte-identical to the previous commit. `indicators.csv` and the packages changed in their text columns.
- Indicator `P1.lowest_flow_listed_at_extinction` removed (12 of its 14 values came from cells that say the flow went lower than the number written). 18 indicators now.
- Agreed with pm: `scenario_needs.csv`, `scenario_tests.csv`, `need_tests.csv` frozen at 17:30.

Next: D5 (my half of the review sheet, verdicts by 18:15); D6 final pass on `compliance/SOURCES.md` (21:00); `reports/spot_check.csv` for a human.

Still not verified, for the human review: the challenge statement was read from a copy (the official page is not reachable from this session), so the lunar-habitat bound of 30% oxygen and 10.2 psi is unchecked; the needs, their readings and the objective links are an AI draft not seen by a combustion specialist.

Published for others (all written by `python3 pipeline/run.py`; shapes below are stable, I will only add columns):
- NEW `data/pipeline/evidence/index.json`, `scenario_<id>.json`, `cell_<o2_bin>__<pressure_bin>.json` — shape in `pipeline/README.md` "Evidence packages". Per need: `status`, `counts`, `reading`, `objective`, `investigations`, `matched_tests` (values with unit and source column, source file and row), `matched_by_fuel_phase`, `usable_elsewhere`, `documented_elsewhere`, `indicators`, `gaps`, `statements`, `references`. Field names stable; fields may be added.
- NEW `data/pipeline/atmosphere_cells.csv` — 120 rows (20 cells x 6 needs), the columns of `scenario_needs.csv` plus `o2_bin`, `pressure_bin`. To look up any atmosphere: find the oxygen and pressure bin in `pipeline/spec/coverage.json`, then read the row or the cell package. Counts with tier `oxygen_only` repeat across the pressure bins of an oxygen bin and must not be summed.
- NEW `data/pipeline/investigation_facts.json` — 24 entries: `tables`, `tests`, `variables` (n, min, max or value counts), `stated_needs`, `capability` (with `counted_tests` and `recorded_outside_objective`), `flags`, `statements`.
- NEW `data/pipeline/validation_report.json` — result of `python3 pipeline/check.py`.
- Row counts now: `values_long.csv` 18,450; `capability_matrix.csv` 132; `need_tests.csv` 848; `scenario_needs.csv` 36 (6 scenarios x 6 needs); `scenario_tests.csv` 10,944; `indicators.csv` 165 (18 indicators); `objective_links.csv` 23.
- `data/pipeline/tests.csv` — 1,824 rows, one per test. Stable: `test_id`, `investigation_id`, `source_id`, every variable name in `pipeline/spec/variables.json` (36 standard including the new `material_id`, 5 derived), `flags`, `source_file`, `source_row`.
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
- `data/pipeline/objective_links.csv` — NEW, 19 rows: `need_id`, `investigation_id`, `record_field`, `quote`.
- `capability_matrix.csv` and `need_tests.csv` gained `objective_link` (and `objective_quote` in the matrix). `scenario_needs.csv` gained `tests_recorded_outside_objective`; it now has 35 rows (5 scenarios).
- `data/pipeline/need_references.csv` — NEW, 56 rows: for each need, the standard or published item behind it (`item_type`, `text`, `where`, `values`, `reference_id`, `title`, `version`, `access`, `url`). Stable.
- `pipeline/spec/needs.json` — need ids `P1`, `P2`, `P3`, `S1`, `D1`, `D2` are stable (P4 removed). Each need has `scope`, `references`, `stated_by`, `reading` and sometimes `note`.
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
