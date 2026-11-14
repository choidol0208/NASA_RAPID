# Raw-file gaps per investigation and variable

*AI-generated (Claude Code), 2026-11-14. Not human-reviewed.*

For every PSI investigation and every standard variable that the six needs use, one state decided by rule from the counts in tests.csv and the spec pipeline/spec/raw_columns.json, after the checker review of 2026-11-14.

A header in a sampled raw file says only that the file has such a column or key. One file per group was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table.

Only one file per group was opened; other files of a group may have other columns. Archives (.zip) and videos were not downloaded or opened; what they hold is not known. No file read states why a quantity is not in the experimental table.

Checker review of 2026-11-14: 58 of 97 header mappings were removed (a different quantity, location or event, or an empty column) and are listed under related_columns_not_mapped; 41 mappings remain. PSI-101 smoke particle size was one mapping with three headers; it is now three mappings, one per statistic. PSI-39 extinction diameter keeps the hot-flame column only. The PSI-10, PSI-159 workbook findings were applied to the PSI-20 and PSI-21 workbooks of the same layout after a team check of those files.

PSI-69: 229 listing rows have a video extension (228 .mp4, 1 .mpg). 46 of them repeat an earlier row with the same file id, and raw_inventory.json counts a repeated row once ('counting_rule'), so the count used here is 183 video files (182 .mp4, 1 .mpg), which is also the number of distinct names.

The survey downloaded 159 PSI files (180483501 bytes) and opened one sample per group; this step re-opened the header lines of 58 of them.

## States

- `in_table`: recorded for n of N mapped tests (tests.csv)
- `column_in_sampled_raw_file`: empty in the table; one sampled file of a group has a column (or a key in a text file) whose header names the quantity; 'column_is' says what kind of column
- `documented_only`: a document sentence states it for the whole table (sources.json 'documented_elsewhere')
- `not_in_sampled_files`: empty in the table and in the mapped columns of the sampled files; the unopened files are listed by kind; where the quantity is, if anywhere, is not stated
- `no_test_table`: the investigation has no per-test table

`column_is`:

- `sensor_reading_series`: a time series of an instrument channel
- `value_per_test_in_a_results_file`: one value per test row or per-test file in a file of results or test records
- `setting_or_set_point`: a setting, set point or planned value
- `calculated_by_the_workbook`: a value the workbook calculates (formula cells)
- `event_timestamp`: the time of an event or step
- `operator_entry`: a choice entered by the operators
- `free_text`: a comment field
- `calibration_example`: a calibration or a worked example, not a value per test
- `clock`: an elapsed-time counter
- `unclear`: the file does not say which of the above

States are tried in this order: in_table, column_in_sampled_raw_file, documented_only, not_in_sampled_files; no_test_table applies before all of them.

## Per need: states of the required variables

### P1 Flammability limit

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 135. All tests in the scope of the need (tests.csv): 376.

| variable | tests | in_table | column_in_sampled_raw_file | column_in_sampled_raw_file by column_is | documented_only | not_in_sampled_files |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 135 | 0 | - | 0 | 0 |
| o2_pct | counted or recorded | 135 | 0 | - | 0 | 0 |
| pressure_kpa | counted or recorded | 0 | 10 | sensor_reading_series 10 | 125 | 0 |
| gravity_level | counted or recorded | 135 | 0 | - | 0 | 0 |
| fuel_material | in scope | 376 | 0 | - | 0 | 0 |
| o2_pct | in scope | 139 | 124 | sensor_reading_series 3; value_per_test_in_a_results_file 121 | 0 | 113 |
| pressure_kpa | in scope | 0 | 134 | sensor_reading_series 13; value_per_test_in_a_results_file 121 | 129 | 113 |
| gravity_level | in scope | 376 | 0 | - | 0 | 0 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

### P2 Ignition

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 0. All tests in the scope of the need (tests.csv): 376.

| variable | tests | in_table | column_in_sampled_raw_file | column_in_sampled_raw_file by column_is | documented_only | not_in_sampled_files |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 0 | 0 | - | 0 | 0 |
| o2_pct | counted or recorded | 0 | 0 | - | 0 | 0 |
| fuel_material | in scope | 376 | 0 | - | 0 | 0 |
| o2_pct | in scope | 139 | 124 | sensor_reading_series 3; value_per_test_in_a_results_file 121 | 0 | 113 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

### P3 Flame spread and growth

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 11. All tests in the scope of the need (tests.csv): 376.

| variable | tests | in_table | column_in_sampled_raw_file | column_in_sampled_raw_file by column_is | documented_only | not_in_sampled_files |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 11 | 0 | - | 0 | 0 |
| flow_cms | counted or recorded | 11 | 0 | - | 0 | 0 |
| flow_direction | counted or recorded | 11 | 0 | - | 0 | 0 |
| fuel_material | in scope | 376 | 0 | - | 0 | 0 |
| flow_cms | in scope | 245 | 10 | calibration_example 10 | 0 | 121 |
| flow_direction | in scope | 13 | 0 | - | 0 | 363 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

### S1 Extinction conditions

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 570. All tests in the scope of the need (tests.csv): 1824.

| variable | tests | in_table | column_in_sampled_raw_file | column_in_sampled_raw_file by column_is | documented_only | not_in_sampled_files |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 570 | 0 | - | 0 | 0 |
| o2_pct | counted or recorded | 570 | 0 | - | 0 | 0 |
| pressure_kpa | counted or recorded | 545 | 0 | - | 25 | 0 |
| fuel_material | in scope | 1824 | 0 | - | 0 | 0 |
| o2_pct | in scope | 1141 | 124 | sensor_reading_series 3; value_per_test_in_a_results_file 121 | 0 | 559 |
| pressure_kpa | in scope | 1012 | 570 | sensor_reading_series 13; unclear 435; value_per_test_in_a_results_file 122 | 129 | 113 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

### D1 Combustion products

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 122. All tests in the scope of the need (tests.csv): 376.

| variable | tests | in_table | column_in_sampled_raw_file | column_in_sampled_raw_file by column_is | documented_only | not_in_sampled_files |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 122 | 0 | - | 0 | 0 |
| fuel_material | in scope | 376 | 0 | - | 0 | 0 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

### D2 Smoke generation conditions

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 0. All tests in the scope of the need (tests.csv): 376.

| variable | tests | in_table | column_in_sampled_raw_file | column_in_sampled_raw_file by column_is | documented_only | not_in_sampled_files |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 0 | 0 | - | 0 | 0 |
| flow_cms | counted or recorded | 0 | 0 | - | 0 | 0 |
| aging_time_s | counted or recorded | 0 | 0 | - | 0 | 0 |
| fuel_material | in scope | 376 | 0 | - | 0 | 0 |
| flow_cms | in scope | 245 | 10 | calibration_example 10 | 0 | 121 |
| aging_time_s | in scope | 108 | 0 | - | 0 | 268 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

## Per need: states of the outcome variables, all tests in scope

| need | variable | in_table | column_in_sampled_raw_file | column_in_sampled_raw_file by column_is | documented_only | not_in_sampled_files |
|---|---|---|---|---|---|---|
| P1 | flow_event | 25 | 0 | - | 0 | 351 |
| P1 | o2_consumed_pct_points | 122 | 0 | - | 0 | 254 |
| P1 | burn_time_s | 7 | 0 | - | 0 | 369 |
| P1 | burn_length_cm | 8 | 0 | - | 0 | 368 |
| P2 | hot_ignition | 0 | 0 | - | 0 | 376 |
| P3 | spread_rate_mm_s | 2 | 0 | - | 0 | 374 |
| P3 | burn_length_cm | 8 | 0 | - | 0 | 368 |
| P3 | burn_time_s | 7 | 0 | - | 0 | 369 |
| S1 | test_end | 546 | 0 | - | 0 | 1278 |
| S1 | extinction_diameter_mm | 197 | 156 | value_per_test_in_a_results_file 156 | 0 | 1471 |
| S1 | flow_event | 25 | 0 | - | 0 | 1799 |
| D1 | co_produced_ppm | 118 | 0 | - | 0 | 258 |
| D1 | co2_produced_pct_points | 121 | 0 | - | 0 | 255 |
| D1 | co_to_co2_molar_ratio | 87 | 0 | - | 0 | 289 |
| D2 | smoke_particle_size_um | 0 | 109 | value_per_test_in_a_results_file 109 | 0 | 267 |

## Per investigation

### PSI-10

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 317 videos, 1183 archives, 389 documents, 319 tables, 1596 other files; the survey opened one file in each of 8 groups and no video or archive. Unopened groups the checker named: logs: 'GC_Coverter_*.log' (10); documents: '<id> test parameter notes.pdf' (18), '<id> test sheets.pdf' (18), '<id> flow traces etc.pdf' (18), '<id> Daily Test Point Log.pdf' (14); text files: '<id>.txt as-run settings, letter groups other than the one opened' (49 in all), '<id>_Comments.txt, files other than the one opened' (313 in the group); other: 'ACME_<id>.mdipsug' (250), 'INTNS_<id>.mdipsug' (240). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 327 of 327 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 316 of 327 mapped tests. For the other 11 tests: not_in_sampled_files. |
| pressure_kpa | in_table | Recorded in the experimental table for 327 of 327 mapped tests. |
| gravity_level | in_table | Recorded in the experimental table for 327 of 327 mapped tests. |
| flow_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'MFCA1StaticMixerFlow, MFCA2BypassFlow, MFCA3FuelFlow' in data_csv (controller flow signals with no unit written, not a velocity in cm/s); 'fuelBottleTestFlowRateN2Slpm' in as_run (a volume flow setting in Slpm, not a velocity). |
| sample_geometry | in_table | Recorded in the experimental table for 327 of 327 mapped tests. |
| sample_thickness_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_direction | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_event | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| o2_consumed_pct_points | in_table | Recorded in the experimental table for 187 of 327 mapped tests. For the other 140 tests: not_in_sampled_files. |
| burn_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Ignition and retraction / Extinction detected' in tp_txt (Two step timestamps written as keys in a text file. 'Ignition and retraction' is the igniter retraction step, not flame ignition; a duration from two timestamps would be a team computation. In the sampled file the step 'Extinction detected' did not occur). |
| burn_length_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_power_w | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Igniter Wattage' in chamber_calculator (The column has no value in the data rows of the sampled workbook). |
| ignition_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Igniter On Time (ms)' in chamber_calculator (The column has no value in the data rows of the sampled workbook). |
| hot_ignition | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Ignite' in chamber_calculator (A Yes/No pick list that the Notes sheet calls the decision during operations; it sets the workbook's burn fraction. No file read says that Yes means that a hot flame was seen). |
| sample_width_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| spread_rate_mm_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: '_CO2 (block Finish Mixture (Percent))' in chamber_calculator (The block 'Finish Mixture (Percent)' is the mixture at the end of the event row, calculated by the workbook (its cells hold formulas; the Notes sheet says the calculator assumes that all fuel or oxygen of the test point was consumed when Ignite is Yes). The variable is the atmosphere at the start of the test, and the sheet has no start-percent block. The values are fractions under a heading that says Percent, and a row can cover several tests). |
| he_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: '_He (block Finish Mixture (Percent))' in chamber_calculator (The block 'Finish Mixture (Percent)' is the mixture at the end of the event row, calculated by the workbook (its cells hold formulas; the Notes sheet says the calculator assumes that all fuel or oxygen of the test point was consumed when Ignite is Yes). The variable is the atmosphere at the start of the test, and the sheet has no start-percent block. The values are fractions under a heading that says Percent, and a row can cover several tests). |
| flow_min_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| test_end | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Extinction detected' in tp_txt (A timestamp of the step 'Extinction detected' ('***' where the step did not occur), written as a key in a text file. It says at most whether extinction was detected, not how the test ended). |
| extinction_diameter_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_produced_ppm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_produced_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_to_co2_molar_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| aging_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| heating_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| mass_loss_rate_mg_min | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| smoke_particle_size_um | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |

### PSI-20

The investigation has no per-test table: PSI-20_Experimental table_ACME BRE.csv: one row per test_day (One row per test day; oxygen is a list of the settings used that day).

- pressure_kpa: 'Pstart (psia)' (column header) in chamber_calculator (one_value_per_row_or_key; unclear)
- fuel_material, not mapped: 'Fuel Type' in chamber_calculator (A column of the sheet 'Stoich Table' (one row per fuel), not one value per test)
- o2_pct, not mapped: '_O2 (block Finish Mixture (Percent))' in chamber_calculator (The block 'Finish Mixture (Percent)' is the mixture at the end of the event row, calculated by the workbook (its cells hold formulas; the Notes sheet says the calculator assumes that all fuel or oxygen of the test point was consumed when Ignite is Yes). The variable is the atmosphere at the start of the test, and the sheet has no start-percent block. The values are fractions under a heading that says Percent, and a row can cover several tests)
- flow_cms, not mapped: 'MFCA1StaticMixerFlow, MFCA2BypassFlow, MFCA3FuelFlow' in data_csv (no unit written; not a velocity)
- burn_time_s, not mapped: 'Ignition and retraction / MFCs off' in tp_txt (Two step timestamps written as keys in a text file. 'Ignition and retraction' is the igniter retraction step, not flame ignition; a duration from two timestamps would be a team computation. 'MFCs off' is a flow step)
- ignition_power_w, not mapped: 'igniterIgnitionPowerV' in as_run (a voltage, not a power in W); 'Igniter Wattage' in chamber_calculator (The column has no value in the data rows of the sampled workbook)
- ignition_time_s, not mapped: 'Igniter On Time (ms)' in chamber_calculator (The column has no value in the data rows of the sampled workbook)
- hot_ignition, not mapped: 'Ignite' in chamber_calculator (A Yes/No pick list that the Notes sheet calls the decision during operations; it sets the workbook's burn fraction. No file read says that Yes means that a hot flame was seen)
- co2_pct, not mapped: '_CO2 (block Finish Mixture (Percent))' in chamber_calculator (The block 'Finish Mixture (Percent)' is the mixture at the end of the event row, calculated by the workbook (its cells hold formulas; the Notes sheet says the calculator assumes that all fuel or oxygen of the test point was consumed when Ignite is Yes). The variable is the atmosphere at the start of the test, and the sheet has no start-percent block. The values are fractions under a heading that says Percent, and a row can cover several tests)
- he_pct, not mapped: '_He (block Finish Mixture (Percent))' in chamber_calculator (The block 'Finish Mixture (Percent)' is the mixture at the end of the event row, calculated by the workbook (its cells hold formulas; the Notes sheet says the calculator assumes that all fuel or oxygen of the test point was consumed when Ignite is Yes). The variable is the atmosphere at the start of the test, and the sheet has no start-percent block. The values are fractions under a heading that says Percent, and a row can cover several tests)
- test_end, not mapped: 'Extinction detected' in tp_txt (A timestamp of the step 'Extinction detected' ('***' where the step did not occur), written as a key in a text file. It says at most whether extinction was detected, not how the test ended)

### PSI-21

The investigation has no per-test table: PSI-21_Experimental table_CLD Flame.csv: one row per test_day (One row per test day).

- pressure_kpa: 'FCU_MP_PT28(PSIA)' (column header) in fcu_readings (time_series_per_file; sensor_reading_series)
- flow_cms: 'velocityAirFinalMPerSec / velocityMixFinalMPerSec' (key in a text file) in tp_settings (one_value_per_row_or_key; setting_or_set_point)
- ignition_time_s: 'igniterIgnitionDurationMs' (key in a text file) in tp_settings (one_value_per_row_or_key; setting_or_set_point)
- fuel_material, not mapped: 'Fuel Type' in chamber_calculator (A column of the sheet 'Stoich Table' (one row per fuel), not one value per test)
- o2_pct, not mapped: '_O2 (block Finish Mixture (Percent))' in chamber_calculator (The block 'Finish Mixture (Percent)' is the mixture at the end of the event row, calculated by the workbook (its cells hold formulas; the Notes sheet says the calculator assumes that all fuel or oxygen of the test point was consumed when Ignite is Yes). The variable is the atmosphere at the start of the test, and the sheet has no start-percent block. The values are fractions under a heading that says Percent, and a row can cover several tests)
- ignition_power_w, not mapped: 'igniterIgnitionPowerV' in tp_settings (a voltage, not a power in W); 'Igniter Wattage' in chamber_calculator (The column has no value in the data rows of the sampled workbook)
- hot_ignition, not mapped: 'Ignite' in chamber_calculator (A Yes/No pick list that the Notes sheet calls the decision during operations; it sets the workbook's burn fraction. No file read says that Yes means that a hot flame was seen)
- co2_pct, not mapped: '_CO2 (block Finish Mixture (Percent))' in chamber_calculator (The block 'Finish Mixture (Percent)' is the mixture at the end of the event row, calculated by the workbook (its cells hold formulas; the Notes sheet says the calculator assumes that all fuel or oxygen of the test point was consumed when Ignite is Yes). The variable is the atmosphere at the start of the test, and the sheet has no start-percent block. The values are fractions under a heading that says Percent, and a row can cover several tests)
- he_pct, not mapped: '_He (block Finish Mixture (Percent))' in chamber_calculator (The block 'Finish Mixture (Percent)' is the mixture at the end of the event row, calculated by the workbook (its cells hold formulas; the Notes sheet says the calculator assumes that all fuel or oxygen of the test point was consumed when Ignite is Yes). The variable is the atmosphere at the start of the test, and the sheet has no start-percent block. The values are fractions under a heading that says Percent, and a row can cover several tests)
- test_end, not mapped: 'Extinction detected' in tp_txt (A timestamp of the step 'Extinction detected' ('***' where the step did not occur), written as a key in a text file. It says at most whether extinction was detected, not how the test ended)

### PSI-22

The investigation has no per-test table: PSI-22_Experimental table_ACME E-FIELD Flames.csv: one row per test_day (One row per test day).

- flow_cms: 'velocityMixFinalMPerSec / velocityAirFinalMPerSec' (key in a text file) in voltage_sweep (one_value_per_row_or_key; setting_or_set_point)
- ignition_time_s: 'igniterIgnitionDurationMs' (key in a text file) in voltage_sweep (one_value_per_row_or_key; setting_or_set_point)
- flow_cms, not mapped: 'Coflow Velocity (cm/s)' in conversion_templates (a formula column of a template; no test values in it)
- ignition_power_w, not mapped: 'igniterIgnitionPowerV' in voltage_sweep (a voltage, not a power in W)
- test_end, not mapped: 'Extinction detected' in tp_txt (A timestamp of the step 'Extinction detected' ('***' where the step did not occur), written as a key in a text file. It says at most whether extinction was detected, not how the test ended)

### PSI-23

The investigation has no per-test table: PSI-23_Experimental table_ACME s-Flame.csv: one row per test_day (One row per test day).

- ignition_time_s: 'igniterIgnitionDurationMs' (key in a text file) in as_run (one_value_per_row_or_key; setting_or_set_point)
- pressure_kpa, not mapped: 'PTA1, PTA2, PTA3' in data_csv (no unit written and the file does not say what quantity the column holds)
- flow_cms, not mapped: 'fuelBottleTestFlowRateN2Slpm' in as_run (a volume flow setting in Slpm, not a velocity)
- burn_time_s, not mapped: 'constantFlowTimeSec' in as_run (a planned duration, not a burn time); 'Ignition and retraction / MFCs off' in tp_txt (Two step timestamps written as keys in a text file. 'Ignition and retraction' is the igniter retraction step, not flame ignition; a duration from two timestamps would be a team computation. 'MFCs off' is a flow step)
- test_end, not mapped: 'Extinction detected' in tp_txt (A timestamp of the step 'Extinction detected' ('***' where the step did not occur), written as a key in a text file. It says at most whether extinction was detected, not how the test ended)

### PSI-25

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 296 videos, 264 archives, 130 documents, 2 tables, 1 other files; the survey opened one file in each of 2 groups and no video or archive. Unopened groups the checker named: documents: 'BASS-II Summary Report.pdf, BASS-II_SRD.pdf, BASS-II_Ops.docx, BASS-II_ReadMe.docx' (4), 'ProofSheet.pdf images' (about 130). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 129 of 129 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 129 of 129 mapped tests. |
| pressure_kpa | documented_only | Empty in the table; a document sentence states it for the whole table (ICES19.pressure): 'Pressure was not varied from 1 atmosphere.'. |
| gravity_level | in_table | Recorded in the experimental table for 129 of 129 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 119 of 129 mapped tests. For the other 10 tests: column_in_sampled_raw_file:calibration_example. |
| sample_geometry | in_table | Recorded in the experimental table for 129 of 129 mapped tests. |
| sample_thickness_mm | in_table | Recorded in the experimental table for 42 of 129 mapped tests. For the other 87 tests: not_in_sampled_files. |
| flow_direction | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_event | in_table | Recorded in the experimental table for 25 of 129 mapped tests. For the other 104 tests: not_in_sampled_files. |
| o2_consumed_pct_points | in_table | Recorded in the experimental table for 122 of 129 mapped tests. For the other 7 tests: not_in_sampled_files. |
| burn_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_length_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_power_w | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| hot_ignition | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_width_cm | in_table | Recorded in the experimental table for 71 of 129 mapped tests. For the other 58 tests: not_in_sampled_files. |
| spread_rate_mm_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| he_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_min_cms | in_table | Recorded in the experimental table for 103 of 129 mapped tests. For the other 26 tests: not_in_sampled_files. |
| test_end | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| extinction_diameter_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_produced_ppm | in_table | Recorded in the experimental table for 118 of 129 mapped tests. For the other 11 tests: not_in_sampled_files. |
| co2_produced_pct_points | in_table | Recorded in the experimental table for 121 of 129 mapped tests. For the other 8 tests: not_in_sampled_files. |
| co_to_co2_molar_ratio | in_table | Recorded in the experimental table for 87 of 129 mapped tests. For the other 42 tests: not_in_sampled_files. |
| aging_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| heating_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| mass_loss_rate_mg_min | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| smoke_particle_size_um | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |

### PSI-26

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 114 videos, 59 archives, 33 documents, 2 tables, 0 other files; the survey opened one file in each of 2 groups and no video or archive. Unopened groups the checker named: documents: 'Drawing_PMMA.Flat.Fuel.Sample2mm.pdf, Drawing_Sibal.Flat.Sample.pdf, Drawing_Flat.Sample.Frame_#cm.pdf and other drawings' (count not given), 'SRD_BASS.pdf, DLD_BASS.pdf, BASS ERD.pptx' (3). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 121 of 121 mapped tests. |
| o2_pct | column_in_sampled_raw_file (value_per_test_in_a_results_file) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header: 'O2 % by volume' in group as_run_matrix (1 files in the group; one_value_per_row_or_key); column_is value_per_test_in_a_results_file; under the group label 'ISS environment', which is the cabin; the file does not say that the test volume had the same atmosphere; written as a fraction. |
| pressure_kpa | column_in_sampled_raw_file (value_per_test_in_a_results_file) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header: 'pressure, atm' in group as_run_matrix (1 files in the group; one_value_per_row_or_key); column_is value_per_test_in_a_results_file; under the group label 'ISS environment', which is the cabin; the file does not say that the test volume had the same pressure; unit atm. |
| gravity_level | in_table | Recorded in the experimental table for 121 of 121 mapped tests. |
| flow_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Fan display; Air display' in as_run_matrix (Display settings with no cm/s unit. The comment text of the same file writes flows in cm/s beside display values, and the PSI-25 fan calibration relates the fan and air display to U cm/s, but no column of this file holds a flow in cm/s (checker re-opening of 2026-11-14)). |
| sample_geometry | in_table | Recorded in the experimental table for 101 of 121 mapped tests. For the other 20 tests: not_in_sampled_files. |
| sample_thickness_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_direction | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_event | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Test Observations and Anomalies (ignited, spread, extinguished, burn time, color, etc.)' in as_run_matrix (One free-text comment column for all observations. The checker found words such as 'burn time' in 19 of 124 rows of the sheet 'as run matrix'. A comment field is not a column for this variable). |
| o2_consumed_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Test Observations and Anomalies (ignited, spread, extinguished, burn time, color, etc.)' in as_run_matrix (One free-text comment column for all observations. The checker found words such as 'burn time' in 19 of 124 rows of the sheet 'as run matrix'. A comment field is not a column for this variable). |
| burn_length_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_power_w | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_time_s | column_in_sampled_raw_file (setting_or_set_point) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header: 'Ignition time   -  seconds' in group planned_matrix (1 files in the group; one_value_per_row_or_key); column_is setting_or_set_point; planned test points, not runs; the values are written as ranges of seconds, not single numbers; not linked to table rows one by one. |
| hot_ignition | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Test Observations and Anomalies (ignited, spread, extinguished, burn time, color, etc.)' in as_run_matrix (One free-text comment column for all observations. The checker found words such as 'burn time' in 19 of 124 rows of the sheet 'as run matrix'. A comment field is not a column for this variable). |
| sample_width_cm | in_table | Recorded in the experimental table for 79 of 121 mapped tests. For the other 42 tests: not_in_sampled_files. |
| spread_rate_mm_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'CO2, mm Hg' in as_run_matrix (A partial pressure in mm Hg under the group label 'ISS environment' (the cabin), not CO2 added to the test atmosphere in % by volume). |
| he_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_min_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| test_end | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| extinction_diameter_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_produced_ppm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_produced_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_to_co2_molar_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| aging_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| heating_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| mass_loss_rate_mg_min | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| smoke_particle_size_um | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |

### PSI-39

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 246 videos, 337 archives, 216 documents, 336 tables, 1675 other files; the survey opened one file in each of 9 groups and no video or archive. Unopened groups the checker named: text files: 'F<id>_MDCA_CFI_Testpoint_Settings.txt' (about 170), 'F<id>_Comments.txt' (about 190), 'F<id>A.txt, C.txt, D.txt' (about 215); documents: 'FLEX-<id>_TestSheet.txt and .rtf' (22 each), 'Analyzed Data_FLEX-<id>_Summary.pdf' (about 30), 'CFI Science Final Report.pdf' (1). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| pressure_kpa | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| gravity_level | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| flow_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_geometry | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| sample_thickness_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_direction | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_event | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| o2_consumed_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_time_s | column_in_sampled_raw_file (value_per_test_in_a_results_file) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header: 'HF Burn Time' in group cfi_data_summary (1 files in the group; one_value_per_row_or_key); column_is value_per_test_in_a_results_file; hot-flame burn time; unit not written. |
| burn_length_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_power_w | column_in_sampled_raw_file (setting_or_set_point) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header: 'Ignition Power ( W )' in group cfi_data_summary (1 files in the group; one_value_per_row_or_key); column_is setting_or_set_point; sheet 'Igniter'. |
| ignition_time_s | column_in_sampled_raw_file (setting_or_set_point) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header: 'Ignition Time ( ms )' in group cfi_data_summary (1 files in the group; one_value_per_row_or_key); column_is setting_or_set_point; sheet 'Igniter'; unit ms. |
| hot_ignition | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_width_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| spread_rate_mm_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| he_pct | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| flow_min_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| test_end | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| extinction_diameter_mm | column_in_sampled_raw_file (value_per_test_in_a_results_file) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header: 'Dext, hot ( mm )' in group cfi_data_summary (1 files in the group; one_value_per_row_or_key); column_is value_per_test_in_a_results_file; hot-flame extinction diameter only; the cool-flame column is listed under related_columns_not_mapped. Related columns not mapped: 'DropletDiameter_mm' in droplet_data (a diameter history; an extinction diameter would be a team reading of it); 'Dext,cool ( mm )' in cfi_data_summary (The droplet diameter at cool-flame extinction, a different event from the visible (hot) flame going out; the two columns hold different values in the same row). |
| co_produced_ppm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_produced_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_to_co2_molar_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| aging_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| heating_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| mass_loss_rate_mg_min | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| smoke_particle_size_um | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |

### PSI-47

The investigation has no per-test table: PSI-47_Experimental table_DAFT.csv: one row per session (One row per sampling session; no combustion test).

- smoke_particle_size_um, not mapped: 'D (micon) / Average D (micron)' in summary (Particle sizes of a dust aerosol, one per bag sample (the survey note); not smoke from a burn)

### PSI-60

The investigation has no per-test table: no experimental table in the PSI listing.

### PSI-62

The investigation has no per-test table: no experimental table in the PSI listing.

### PSI-68

The investigation has no per-test table: PSI-68_Experimental table_Flex2.csv: one row per planned_matrix (One row per fuel with the planned ranges of conditions, not tests).

- pressure_kpa, not mapped: 'FCU_MP_PT16(PSIA) ... FCU_MP_PT29(PSIA)' in chamber_readings (Several pressure transducers; the file does not say which one is the ambient or chamber pressure)
- flow_cms, not mapped: 'FLOW_NOZZLE_1_SPEED(N/A) / FLOW_NOZZLE_2_SPEED(N/A)' in chamber_readings (The sampled file of this header variant has a header line and no data rows, so the column is empty in what was opened. Unit written N/A)
- burn_time_s, not mapped: 'TP_PARAMETER_BURN_TO_COMPLETION_TIME(N/A)' in chamber_readings (a test point setting, not a burn time)
- ignition_power_w, not mapped: 'IGNITER_WATTAGE(Watts) / TP_PARAMETER_IGNITER_WATTAGE(Watts)' in chamber_readings (The sampled file of this header variant has a header line and no data rows, so the column is empty in what was opened)
- ignition_time_s, not mapped: 'TP_PARAMETER_IGNITER_ON_TIME(N/A)' in chamber_readings (The sampled file of this header variant has a header line and no data rows, so the column is empty in what was opened)

### PSI-69

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 183 videos, 1419 archives, 1195 documents, 1375 tables, 2279 other files; the survey opened one file in each of 10 groups and no video or archive. Unopened groups the checker named: text files: 'Calibration_<id>_Chamber_Gases.txt' (8), '<id>_Chamber_Contents.txt' (1), '<id>_Comments.txt' (230), '<id>_Testpoint_Settings.txt variants and LCTF#_MDCA_Testpoint_Settings.txt' (18), '<id>_Readme.txt' (count not given); documents: 'FLEX-<id>_Summary.pdf' (260), 'FLEX_<id>_Summary.pdf' (110), 'FLEX-<id>_ResultsSummary.pdf' (7). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| pressure_kpa | in_table | Recorded in the experimental table for 273 of 274 mapped tests. For the other 1 tests: column_in_sampled_raw_file:value_per_test_in_a_results_file. |
| gravity_level | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| flow_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_geometry | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| sample_thickness_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_direction | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_event | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| o2_consumed_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_time_s | in_table | Recorded in the experimental table for 268 of 274 mapped tests. For the other 6 tests: not_in_sampled_files. |
| burn_length_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_power_w | column_in_sampled_raw_file (setting_or_set_point) | A sampled file of this group has a key with this name in a text file. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Key in a text file: 'Igniter Wattage' in group tp_log (666 files in the group; one_value_per_row_or_key); column_is setting_or_set_point; unit not written; W is assumed from the word 'Wattage'. |
| ignition_time_s | column_in_sampled_raw_file (setting_or_set_point) | A sampled file of this group has a key with this name in a text file. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Key in a text file: 'Igniter On Time (milliseconds)' in group tp_log (666 files in the group; one_value_per_row_or_key); column_is setting_or_set_point; unit ms in the key name. |
| hot_ignition | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_width_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| spread_rate_mm_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_pct | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| he_pct | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| flow_min_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| test_end | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| extinction_diameter_mm | in_table | Recorded in the experimental table for 197 of 274 mapped tests. For the other 77 tests: column_in_sampled_raw_file:value_per_test_in_a_results_file. |
| co_produced_ppm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_produced_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_to_co2_molar_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| aging_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| heating_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| mass_loss_rate_mg_min | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| smoke_particle_size_um | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |

### PSI-98

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 0 videos, 61 archives, 9 documents, 4 tables, 0 other files; the survey opened one file in each of 3 groups and no video or archive. Unopened groups the checker named: documents: 'SAFFIRE Offgassing Testing Strategy.pdf' (1), 'Saffire-I Sample 1 and 2 TM graphs.docx' (2), 'SAFFIRE-I Operations.pdf' (1). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| pressure_kpa | column_in_sampled_raw_file (sensor_reading_series) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header with the unit in the next row: 'Ambient Pressure' in group sample_sensors (2 files in the group; time_series_per_file); column_is sensor_reading_series; sheet 'Calibrated Data'; unit row 'PSIA'; one file per sample (the survey links a sample to a test). |
| gravity_level | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| sample_geometry | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| sample_thickness_mm | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_direction | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_event | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| o2_consumed_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_time_s | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| burn_length_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_power_w | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| ignition_time_s | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| hot_ignition | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_width_cm | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| spread_rate_mm_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_pct | column_in_sampled_raw_file (sensor_reading_series) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header with the unit in the next row: 'CO2' in group sample_sensors (2 files in the group; time_series_per_file); column_is sensor_reading_series; sheet 'Calibrated Data'; unit row '%'; one file per sample (the survey links a sample to a test). |
| he_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_min_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| test_end | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| extinction_diameter_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_produced_ppm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_produced_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_to_co2_molar_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| aging_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| heating_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| mass_loss_rate_mg_min | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| smoke_particle_size_um | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |

### PSI-99

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 0 videos, 186 archives, 15 documents, 11 tables, 0 other files; the survey opened one file in each of 2 groups and no video or archive. Unopened groups the checker named: tables: 'Saffire-II Telemetry Data.xlsx (the only telemetry workbook of PSI-99)' (1); documents: 'SaffireIIStitchedCO2V7.pdf' (1), 'Saffire-II Sample <N> TM Graphs.docx' (9), 'SAFFIRE-II Operations.pdf' (1). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 8 of 9 mapped tests. For the other 1 tests: column_in_sampled_raw_file:sensor_reading_series. |
| pressure_kpa | column_in_sampled_raw_file (sensor_reading_series) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header with the unit in the next row: 'Ambient Pressure' in group sample_sensors (9 files in the group; time_series_per_file); column_is sensor_reading_series; sheet 'Calibrated Data'; unit row 'PSIA'; one file per sample (the survey links a sample to a test). |
| gravity_level | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| sample_geometry | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| sample_thickness_mm | in_table | Recorded in the experimental table for 4 of 9 mapped tests. For the other 5 tests: not_in_sampled_files. |
| flow_direction | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| flow_event | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| o2_consumed_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_time_s | in_table | Recorded in the experimental table for 5 of 9 mapped tests. For the other 4 tests: not_in_sampled_files. |
| burn_length_cm | in_table | Recorded in the experimental table for 8 of 9 mapped tests. For the other 1 tests: not_in_sampled_files. |
| ignition_power_w | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| ignition_time_s | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| hot_ignition | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_width_cm | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| spread_rate_mm_s | in_table | Recorded in the experimental table for 2 of 9 mapped tests. For the other 7 tests: not_in_sampled_files. |
| co2_pct | column_in_sampled_raw_file (sensor_reading_series) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header with the unit in the next row: 'CO2' in group sample_sensors (9 files in the group; time_series_per_file); column_is sensor_reading_series; sheet 'Calibrated Data'; unit row '%'; one file per sample (the survey links a sample to a test). |
| he_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_min_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| test_end | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| extinction_diameter_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_produced_ppm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_produced_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_to_co2_molar_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| aging_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| heating_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| mass_loss_rate_mg_min | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| smoke_particle_size_um | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |

### PSI-100

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 0 videos, 67 archives, 10 documents, 8 tables, 0 other files; the survey opened one file in each of 4 groups and no video or archive. Unopened groups the checker named: tables: 'Saffire-III 1 Hz Telemetry Data.xlsx and Raw telemetry file.csv (downloaded by the survey but not recorded as a sample group)' (2); documents: 'SAFFIRE Offgassing Testing Strategy.pdf' (1), 'SAFFIRE-III Operations.pdf' (1). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| o2_pct | column_in_sampled_raw_file (sensor_reading_series) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header with the unit in the next row: 'O2' in group sample_sensors (2 files in the group; time_series_per_file); column_is sensor_reading_series; sheet 'Calibrated Data'; unit row '%'; one file per sample (the survey links a sample to a test). |
| pressure_kpa | column_in_sampled_raw_file (sensor_reading_series) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header with the unit in the next row: 'Ambient Pressure' in group sample_sensors (2 files in the group; time_series_per_file); column_is sensor_reading_series; sheet 'Calibrated Data'; unit row 'PSIA'; one file per sample (the survey links a sample to a test). |
| gravity_level | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| sample_geometry | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| sample_thickness_mm | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_direction | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_event | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| o2_consumed_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_length_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_power_w | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Igniter Current / Igniter Voltage' in sample_sensors (Current and voltage series of the igniter, not a power or an on-time; a power or duration from them would be a team computation). |
| ignition_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| hot_ignition | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_width_cm | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| spread_rate_mm_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_pct | column_in_sampled_raw_file (sensor_reading_series) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header with the unit in the next row: 'CO2' in group sample_sensors (2 files in the group; time_series_per_file); column_is sensor_reading_series; sheet 'Calibrated Data'; unit row '%'; one file per sample (the survey links a sample to a test). |
| he_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_min_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| test_end | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| extinction_diameter_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_produced_ppm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_produced_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_to_co2_molar_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| aging_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| heating_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| mass_loss_rate_mg_min | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| smoke_particle_size_um | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |

### PSI-101

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 8 videos, 79 archives, 116 documents, 47 tables, 92 other files; the survey opened one file in each of 6 groups and no video or archive. Unopened groups the checker named: tables: 'HKPData_gmt#_#.csv, files other than the one opened' (43), 'Analyzed Data_*_run#.xls per-run workbooks for kapton (16), pyrell (11), teflon (11) and silicone (about 12); only lampwick opened' (about 50), 'SAME-R_ThermalPrecipitatorUsage.xlsx' (1); documents: 'SAME_Wire_Report.pdf' (1), 'Sample descriptions tables.docx' (1). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 109 of 109 mapped tests. |
| o2_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| pressure_kpa | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'SampleSidePressure[AT20](PSIA)' in hkp_csv (The sample-side pressure, one location among several pressures in the file (MFC, GN2 main, vacuum, drive side, sample side); the variable is the ambient pressure). |
| gravity_level | in_table | Recorded in the experimental table for 109 of 109 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 109 of 109 mapped tests. |
| sample_geometry | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_thickness_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_direction | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_event | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| o2_consumed_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_length_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_power_w | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| hot_ignition | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_width_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| spread_rate_mm_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| he_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_min_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| test_end | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| extinction_diameter_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_produced_ppm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_produced_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_to_co2_molar_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| aging_time_s | in_table | Recorded in the experimental table for 104 of 109 mapped tests. For the other 5 tests: not_in_sampled_files. |
| heating_ratio | in_table | Recorded in the experimental table for 109 of 109 mapped tests. |
| mass_loss_rate_mg_min | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Mass Loss (mg)' in results (a total mass, not a rate in mg/min). |
| smoke_particle_size_um | column_in_sampled_raw_file (value_per_test_in_a_results_file) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header: 'M1/M0 (micro-m)--AMD' in group results (1 files in the group; one_value_per_row_or_key); column_is value_per_test_in_a_results_file; sheets 'SAME R Results' and 'Reduced data sheet'; one of three different size statistics in this file, each under its own header; they give different numbers for the same row and are not one variable; the checker found zeros in 23 to 24 rows of each of the three columns on sheet 'Reduced data sheet'; written 'M1/M0 (micro-m)--CMD' on the sheets DBP, Pyrell, Lampwick, Silicone, Teflon and Kapton. Column header: 'Diameter of Average mass (micro-m)' in group results (1 files in the group; one_value_per_row_or_key); column_is value_per_test_in_a_results_file; sheets 'SAME R Results' and 'Reduced data sheet'; one of three different size statistics in this file, each under its own header; they give different numbers for the same row and are not one variable; the checker found zeros in 23 to 24 rows of each of the three columns on sheet 'Reduced data sheet'. Column header: 'Hatch Choate Dg' in group results (1 files in the group; one_value_per_row_or_key); column_is value_per_test_in_a_results_file; sheets 'SAME R Results' and 'Reduced data sheet'; one of three different size statistics in this file, each under its own header; they give different numbers for the same row and are not one variable; the checker found zeros in 23 to 24 rows of each of the three columns on sheet 'Reduced data sheet'. |

### PSI-102

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 2 videos, 3 archives, 33 documents, 2 tables, 59 other files; the survey opened one file in each of 5 groups and no video or archive. Unopened groups the checker named: tables: 'GMT#<material>#.xls, GMT# ... hkp.xls and Run # GMT# testlog.xls/.xlsx' (about 60); documents: 'SAME_IgnitorWireCharacterizationReport.pdf' (1), 'SAME_Final Science Report.pdf' (1). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 4 of 4 mapped tests. |
| o2_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| pressure_kpa | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'SampleSidePressure[AT20](PSIA)' in hkp_workbooks (The sample-side pressure, one location among several pressures in the file; the variable is the ambient pressure. The sheet of the sampled workbook is named 'Copy of GMT255hkp'). |
| gravity_level | in_table | Recorded in the experimental table for 4 of 4 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 4 of 4 mapped tests. |
| sample_geometry | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_thickness_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_direction | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_event | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| o2_consumed_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'ElapsedTestTime(Secs)' in hkp_workbooks (A housekeeping test clock, not a burn time). |
| burn_length_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_power_w | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| hot_ignition | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_width_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| spread_rate_mm_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| he_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_min_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| test_end | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| extinction_diameter_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_produced_ppm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_produced_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_to_co2_molar_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| aging_time_s | in_table | Recorded in the experimental table for 4 of 4 mapped tests. |
| heating_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'SampleResistance(Ohms)' in hkp_workbooks (a resistance, not the heating ratio). |
| mass_loss_rate_mg_min | in_table | Recorded in the experimental table for 4 of 4 mapped tests. |
| smoke_particle_size_um | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'PTrakMeasurement(PtPerCC); DustTrakAMeasurement(MgPerM3)' in hkp_workbooks (concentrations, not a particle size). |

### PSI-106

The investigation has no per-test table: PSI-106_Experimental table_Slice.csv: one row per test_day (One row per test day; no per-test conditions).

### PSI-107

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 19 videos, 100 archives, 31 documents, 2 tables, 34 other files; the survey opened one file in each of 5 groups and no video or archive. Unopened groups the checker named: tables: 'SPICE Flow settings_w chart.xls, SPICE_FuelFlow_MFC_settings.xlsx, SPICE_Airflow_Test_VelocityData.xlsx, VelocityComparison.xlsx, Duct Velocity Profiles.xls, MASS_FLOW_CALIBRATION.xls' (6), 'SPICE Flow Duct Cal ... .xls' (18), 'GMT052nikon_propy.xls' (1); text files: '<id>_SPICE_num.txt, the file not opened' (1 of 2); documents: 'SPICE_ScienceVerificationReport.pdf, SPICE_Phase III Flight Safety Data Package.pdf, SPICE_FinalReport.pdf' (3). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 435 of 435 mapped tests. |
| o2_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| pressure_kpa | column_in_sampled_raw_file (unclear) | A sampled file of this group has a column with this header. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Column header with the unit in the next row: 'Pressure (Pa)' in group flight_test_data (1 files in the group; one_value_per_row_or_key); column_is unclear; unit Pa in the next row; the sheet does not say whether the value is a reading or a nominal set point. |
| gravity_level | in_table | Recorded in the experimental table for 435 of 435 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 407 of 435 mapped tests. For the other 28 tests: column_in_sampled_raw_file:unclear. |
| sample_geometry | in_table | Recorded in the experimental table for 435 of 435 mapped tests. |
| sample_thickness_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_direction | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_event | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| o2_consumed_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| burn_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'GMT ignition / GMT  Flame Off ' in flight_test_data (Two event timestamps ('GMT ignition', 'GMT  Flame Off ', the second with a trailing space); a duration from them would be a team computation). |
| burn_length_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_power_w | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| hot_ignition | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| sample_width_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| spread_rate_mm_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| he_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_min_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| test_end | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| extinction_diameter_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_produced_ppm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_produced_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_to_co2_molar_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| aging_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| heating_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| mass_loss_rate_mg_min | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| smoke_particle_size_um | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |

### PSI-115

The investigation has no per-test table: no experimental table in the PSI listing.

### PSI-117

The investigation has no per-test table: no experimental table in the PSI listing.

### PSI-142

The investigation has no per-test table: PSI-142_Experimental table_Data Summary Table.csv: one row per dataset_index (Index of figures in publications).

### PSI-159

For every variable in state not_in_sampled_files below (full sentence in raw_gaps.json): Files of this investigation by kind (raw_inventory.json listing counts): 337 videos, 986 archives, 411 documents, 340 tables, 1679 other files; the survey opened one file in each of 8 groups and no video or archive. Unopened groups the checker named: documents: '<id> test parameter notes.pdf, test sheets.pdf, flow traces etc.pdf, daily test point log.pdf' (21 to 23 each); text files: 'as run<id>.txt in 13 letter families, only 'D' opened' (count not given), '<id>_Comments.txt, files other than the one opened' (317 in the group), '<id>ImageComments.txt' (count not given). The files read do not say whether any unopened file holds this quantity.

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| pressure_kpa | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| gravity_level | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| flow_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'fuelTestFlow1Slpm' in as_run (a volume flow setting in Slpm, not a velocity). |
| sample_geometry | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| sample_thickness_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_direction | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| flow_event | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| o2_consumed_pct_points | in_table | Recorded in the experimental table for 179 of 333 mapped tests. For the other 154 tests: not_in_sampled_files. |
| burn_time_s | in_table | Recorded in the experimental table for 329 of 333 mapped tests. For the other 4 tests: not_in_sampled_files. |
| burn_length_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| ignition_power_w | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: 'Igniter Wattage' in chamber_calculator (The column has no value in the data rows of the sampled workbook). |
| ignition_time_s | column_in_sampled_raw_file (setting_or_set_point) | A sampled file of this group has a key with this name in a text file. One file was opened; the files do not say whether the values are complete, calibrated, or for the same test as a row of the table. Key in a text file: 'igniterIgnitionDurationMs' in group as_run (339 files in the group; one_value_per_row_or_key); column_is setting_or_set_point; unit ms in the key name. |
| hot_ignition | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| sample_width_cm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| spread_rate_mm_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: '_CO2 (block Finish Mixture (Percent))' in chamber_calculator (The block 'Finish Mixture (Percent)' is the mixture at the end of the event row, calculated by the workbook (its cells hold formulas; the Notes sheet says the calculator assumes that all fuel or oxygen of the test point was consumed when Ignite is Yes). The variable is the atmosphere at the start of the test, and the sheet has no start-percent block. The values are fractions under a heading that says Percent, and a row can cover several tests). |
| he_pct | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. Related columns not mapped: '_He (block Finish Mixture (Percent))' in chamber_calculator (The block 'Finish Mixture (Percent)' is the mixture at the end of the event row, calculated by the workbook (its cells hold formulas; the Notes sheet says the calculator assumes that all fuel or oxygen of the test point was consumed when Ignite is Yes). The variable is the atmosphere at the start of the test, and the sheet has no start-percent block. The values are fractions under a heading that says Percent, and a row can cover several tests). |
| flow_min_cms | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| test_end | in_table | Recorded in the experimental table for 272 of 333 mapped tests. For the other 61 tests: not_in_sampled_files. |
| extinction_diameter_mm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_produced_ppm | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co2_produced_pct_points | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| co_to_co2_molar_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| aging_time_s | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| heating_ratio | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| mass_loss_rate_mg_min | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |
| smoke_particle_size_um | not_in_sampled_files | Empty in the table, and no sampled file has a column mapped to it; the unopened files are listed above this table. The files read do not say whether any unopened file holds this quantity. |

