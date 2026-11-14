---
role: data
updated: 2026-11-14 23:40 KST
state: working
blocked_on: none
---
Raw-file layer (21:25): it is on `data-pipeline` (`f3048f4`, merged with `main` at `e0794ba`). Nothing that existed was renamed or removed; `tests.csv` and the three scenario files are byte-identical to the 17:30 state; counted tests unchanged. Checks: 67 of 67 PASS. Run order now: `run.py`, `raw_gaps.py`, `findings.py`, `answers.py`, `check.py`.

New files in `data/pipeline/` (described in `pipeline/README.md`, section "What is in the raw files"):
- `gap_states.csv`: per investigation and variable, one of `in_table`, `column_in_sampled_raw_file` (with the kind of column), `documented_only`, `not_in_sampled_files`, `no_test_table`.
- `need_gap_states.csv`: the same per scenario, need and required or outcome variable, with the numbers of in-scope and counted tests in each state.
- `retrieval_queue.csv`: which raw file groups hold or may hold a value the table lacks, with files and bytes; the order is a fixed rule without weights, not a priority of the team or of NASA. `retrievable_by_reading` is `yes` on 3 of 135 rows.
- `raw_values.csv` and `raw_values_effect.json`: two groups read in full (the "Ambient Pressure" series of the 13 Saffire sensor workbooks; three particle-size statistics of SAME-R, 6,536 values tied to 108 of 109 tests). Not adopted: no value entered `tests.csv`; D2 stays at 0 counted tests either way.
- Evidence packages: every need block and gap has an added `raw_state` (state, tests, file group, fixed sentence).
For ui and pm: a gap can now say more than "not recorded": for example P1 pressure, of 376 in-scope tests: 13 have a pressure column in a sensor workbook, 121 a per-run value in an as-run matrix (cabin block), 129 only a document sentence. Read the README limits before showing them: the state comes from one opened file per group, and a column is not a measurement of the test.

Name layer (23:40, `b9468e3`; 73 of 73 checks PASS; frozen files and counts unchanged; only columns and files added). Every one of the 60,866 raw files is classified by its name, without opening it:
- tied by name to one test: 12,934 files (5.34 TB), reaching 1,179 of the 1,824 mapped tests; tied to a day or session: 30,634 files; not tied: 17,298 files. By kind and investigation: `data/pipeline/raw_layers_summary.json`, `raw_file_groups.csv`, `test_files.csv`.
- name codes: 109 of 289 have a meaning quoted from a NASA document; 180 say "no stated meaning found" (`pipeline/spec/raw_names.json`).
- zip archives: PSI serves range requests, so the member list of an archive can be read without downloading it (`pipeline/zip_directory.py`; 23 of 12,689 archives listed as a sample, 4.4 MB fetched for 52.5 GB).
- videos: all 2,623 names compared with the tables; on-screen readings (FUEL, AIR, FAN, RAD, clock) seen in opened videos of BASS-II, BASS, SPICE and SLICE.
- `gap_states.csv` and `retrieval_queue.csv` gained columns: videos and archives tied by name to the tests that lack a value. A tie by name means the name carries the test's identifier; the content was not checked.
Open points a person decides are listed in `raw_names.json` `_meta.open_points` and `name_tie_alternatives.csv` (20 files whose name could tie to another row).

For pm (request 1755, your three conditions): `data-lab` is pushed (`b2d7010`). It holds `pipeline/lab/model_map.md` (130 decisions: 53 follow a published definition, 52 team rules, 25 judgements made when the rules were written), `data/pipeline/lab/numbers/envelope_lunar_habitat.md`, and the figure you asked for: `data/pipeline/lab/numbers/envelope_lunar_habitat_S1.png` and `.svg`, written by `pipeline/lab/plot_envelope.py` (standard library only; the caption inside the image says it is computed by the team's code and is not a NASA figure). Who checked: every number recomputed by a second AI agent with its own code, citations opened again by a separate agent, no person.

New on `data-lab` (19:00 to 19:20), a survey of the raw files behind the tables: 159 small PSI files of 19 investigations were opened for their column names only (no archive, no video). Per investigation and variable it says: in the table / a column with that name exists in one sampled raw file (and what kind: sensor series, value per test in a results file, set point, calculation, free text, ...) / stated only by a document / not found in the sampled files. Examples: the Saffire sensor workbooks have an "Ambient Pressure" column (PSIA) that the PSI tables lack; the SAME-R results workbook has smoke particle size per test (three different statistics); the BASS as-run matrix has cabin oxygen and pressure per run. An independent AI check removed 58 of 97 first mappings as a different quantity, location or event. Files: `pipeline/spec/raw_columns.json`, `data/pipeline/lab/raw_gaps.md`.

What the data role would do with the extra day, most valuable first (the data side's human lead decides tonight):
1. Show, per need and scenario, the difference between "no test" and "tested, but the value is in a raw file and not in the table", from the survey above. It changes no count; it adds a state next to each gap.
2. Read the few raw values that a need requires and that a sampled file holds unambiguously (Saffire ambient pressure for 13 tests; SAME-R particle size for 109 tests), each with file, sheet, column and rule, behind the same checker. This would reopen the three frozen CSVs: the pressure tier of the Saffire tests and the D2 count could change.
3. Correct the mmHg factor (31 pressures change by 0.0001 kPa) and bring the envelope position (inside each axis / inside the region) into the evidence packages.

Done 16:25 to 17:30:
- D5 (request 1224): verdicts for all 385 rows of `ai/review/review_sheet.csv`, `reviewer_kind = ai_session`; 61 model rows read by two independent AI readers, the stricter verdict recorded (33 supported, 28 partly).
- Request 1622: three wording fixes (README count of tests at or below 70.3 kPa is 20, the lunar caveat is a statement, `not_covered` phrase).
- Request 1630: quotes from non-NASA documents cut to 25 words or fewer (37 shortened, 8 dropped), 10 NASA quotes cut to 40; three NASA quotes stay longer and are named in the answer.
- Request 1656: the internal Korean pages and their builders are out of the repository; no Hangul left in the data role's tracked files.
- `pipeline/check.py`: 59 of 59 PASS after each change; counted tests unchanged (P1 133, P2 0, P3 2, S1 298, D1 122, D2 0).

Done since last sync (details: request 20261114-1442-data-to-all "Counts changed after a literature check"):
- **Literature check of four open points** (commit `a5a9e87`; 66 documents in `references.json`, quotes verbatim): (1) links between a need and an investigation now rest on a purpose sentence of the investigators or of a NASA project document, with a verdict, and only `supported` links count; (2) pressure is a required condition of P1 and S1 by definition, met by a sentence about the whole table where the table has no pressure, never by a created value; (3) the SAME "weight loss rate" is a planned target value, so D2 has no counted test; (4) oxygen cells with two numbers give the value the investigators name as the initial oxygen, or none; no midpoint.
- Counted tests now: P1 133, P2 0, P3 2, S1 298, D1 122 (BASS-II, by the investigators' stated purpose), D2 0. Solid fuels at 19 to 23% oxygen: 61 recorded tests (was 62).
- Step B of proposal 1503 is done (commit `0508bc6`, checker `bcb628e`): `data/pipeline/answers/<scenario>__<need>.json` (36) and `index.json`; four rungs, fixed sentences, rule-chosen top line. Rebuild after `run.py`: `python3 pipeline/findings.py`, `python3 pipeline/answers.py`. Field names for ui: request 1531 (ui: done).
- Checker: 59 of 59 checks pass; it now also covers the published findings, the answer files and the raw inventory.
- Step A of proposal 1503 is on `data-pipeline` (commit `50d0bae`): `data/pipeline/findings.csv` (211 published statements from 180 reference items, tagged by need and by the conditions their own words state) and `findings_by_environment.json` (per scenario and need: at the environment, about one of its conditions, general). Rebuild: `python3 pipeline/findings.py`. Quotes of documents, not results of the pipeline; tagging by an AI reading.
- Raw-data inventory for pm (request 1449, done): `data/pipeline/raw_inventory.json`, `pipeline/raw_inventory.py`, `scripts/psi_whats_new.py`. 60,866 files, 13.47 TB; kinds decided from file names only.
- Prose pass (commit `c05f277`): questions, reasons, notes and README say no more than the quoted sources; `needs.json` `_meta.authorship` lists twelve points that are the team's own construction and what the documents back. P2 and S1 questions reworded (S1 now names pressure). `P3.spread_rate` and `P3.burn_length` show the Saffire-II values as recorded outside the stated objective. No count changed.
- Saffire raw data: per-sample sensor workbooks in PSI hold "Ambient Pressure" in psia (14.825 to 14.935 over the eleven samples of Saffire-I and -II); not mapped, carried as a sentence. See the answer to request 1431.
Earlier today (request 20261114-1242-data-to-all "Audit fixes"):
- Evidence layer is on `data-pipeline` (commit `a454a92` and later): `data/pipeline/evidence/` (6 scenarios, 20 oxygen x pressure cells, `index.json`), `atmosphere_cells.csv`, `investigation_facts.json`, `pipeline/check.py` with `validation_report.json`.
- Three independent audits by sub-agents (counts recomputed from the raw tables without the pipeline; over-generalisation of the needs; citations against the documents) found real errors, now fixed: note and figure numbers read as values (Saffire-II spread rate 4.0 mm/s was the cell "Note 4"), BASS-II fan potentiometer settings read as flow, a maintenance row and 42 repeated rows counted as tests, paraffin labelled Japan wax, the lowest-oxygen BASS-II test dropped from P1, igniter settings treated as outcomes, objective links applied unevenly, 13 reference entries.
- Need P4 removed (pm's decision). Six needs. 1,824 test rows (was 1,867).
- Objective links use the `objective` field of the PSI record only. Each need has a `reading`: what a counted test records and what the count does not mean.
- New: scenario `exploration_10_2_26_5`; `added_gas` mark; gap codes `flow:not_recorded`, `flow:no_usable_test_in_range`; `see_also` pointers from scenarios to PSI-20 and PSI-23 (records and cells that name exploration atmospheres and are not in the counts); `documented_elsewhere` sentences (for example BASS-II: "Pressure was not varied from 1 atmosphere.", from the investigators' paper, shown next to the pressure gap and never used as a value).
- Checker: 43 of 43 checks pass (`python3 pipeline/check.py`). Values that are not literally in a NASA cell (87 material names from the BASS-II ReadMe, 3 oxygen midpoints, 2 materials from the row above) pass only because each carries its flag; they are listed in `pipeline/README.md`.
- pm's two reference items are in `references.json`: `SAF456.conditions` (ICES-2024-365, Table 1) and `OF2012.table1` (Olson and Ferkul 2012, Table I), both read cell by cell from the PDFs. See the answer to request 1224.
- Wording pass over the remaining audit findings (commit `d9f5846`): `label`, `reading`, `note` and `_meta` texts only; no id, range, link or number changed, and `tests.csv`, `values_long.csv`, `need_tests.csv`, `scenario_needs.csv`, `scenario_tests.csv`, `coverage_grid.csv`, `capability_matrix.csv` are byte-identical to the previous commit. `indicators.csv` and the packages changed in their text columns.
- Indicator `P1.lowest_flow_listed_at_extinction` removed (12 of its 14 values came from cells that say the flow went lower than the number written). 18 indicators now.
- Acceptance review by a reviewer that was not involved (commit `eb0a8da` holds the fixes): reproduction byte for byte, 49 values traced to the raw cells with none wrong, 12 mutations all caught by the checker. Its main finding: the 17 lunar-habitat tests are recorded at 71.2 to 72.4 kPa, above the 70.3 kPa of the challenge bound (request 1328). Also fixed: five implausible BASS-II final-oxygen readings emptied and flagged, shorter package sentences, a `caveat` per scenario, the status sentence in `index.json`.
- Agreed with pm: `scenario_needs.csv`, `scenario_tests.csv`, `need_tests.csv` frozen at 17:30.

Next: D5 (my half of the review sheet, verdicts by 18:15); D6 final pass on `compliance/SOURCES.md` (21:00); `reports/spot_check.csv` for a human.

Counts pm asked for: tests with a recorded oxygen of the surrounding atmosphere (`o2_basis = ambient`): 878 = solid 139, liquid 353, gas 386 (solid was 140 until Saffire-II sample 2-9 lost its single oxygen value at 14:30). (Liquid was 361 before; 8 CFI rows repeated earlier rows.) A further 263 gas tests record the oxygen of an oxidizer stream, not of the atmosphere.

Challenge statement: ui checked it on the official page (request 1305); `CHALLENGE-2026` now has the official URL and title, `CH.moonbase` says "oxygen likely 30% or more", and there are new items `CH.spacesuit`, `CH.partial_gravity`, `CH.hardware`. `access` is `read_by_teammate`.

Still open for the human review: the verdicts on the links are an AI reading of the documents listed in `references.json` (several papers were reached only as abstracts or text extractions; `access` says which); what remains the team's own construction is listed in `needs.json` `_meta.authorship`.

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
