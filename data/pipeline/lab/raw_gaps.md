# Raw-file gaps per investigation and variable

*AI-generated (Claude Code), 2026-11-14. Not human-reviewed.*

For every PSI investigation and every standard variable that the six needs use, one state decided by rule from the counts in tests.csv and the spec pipeline/spec/raw_columns.json.

A column in a raw file says the quantity was logged; it does not say the log is complete, calibrated or usable.

Only one file per group was opened; other files of a group may have other columns. Archives (.zip) and videos were not downloaded or opened; what they hold is not known. No file read states why a quantity is not in the experimental table.

The survey downloaded 159 PSI files (180483501 bytes) and opened one sample per group; this step re-opened the header lines of 58 of them.

## States

- `in_table`: recorded for n of N mapped tests (tests.csv)
- `measured_not_summarised`: empty in the table, but a sampled raw file has a column for it
- `documented_only`: a document sentence states it for the whole table (sources.json 'documented_elsewhere')
- `video_or_archive_only`: no sampled table column; videos or unopened archives exist (counts from raw_inventory.json)
- `no_record_found`: none of the above in what was sampled
- `no_test_table`: the investigation has no per-test table

States are tried in this order: in_table, measured_not_summarised, documented_only, video_or_archive_only, no_record_found; no_test_table applies before all of them.

## Per need: states of the required variables

### P1 Flammability limit

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 135. All tests in the scope of the need (tests.csv): 376.

| variable | tests | in_table | measured_not_summarised | documented_only | video_or_archive_only | no_record_found |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 135 | 0 | 0 | 0 | 0 |
| o2_pct | counted or recorded | 135 | 0 | 0 | 0 | 0 |
| pressure_kpa | counted or recorded | 0 | 10 | 125 | 0 | 0 |
| gravity_level | counted or recorded | 135 | 0 | 0 | 0 | 0 |
| fuel_material | in scope | 376 | 0 | 0 | 0 | 0 |
| o2_pct | in scope | 139 | 124 | 0 | 113 | 0 |
| pressure_kpa | in scope | 0 | 247 | 129 | 0 | 0 |
| gravity_level | in scope | 376 | 0 | 0 | 0 | 0 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

### P2 Ignition

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 0. All tests in the scope of the need (tests.csv): 376.

| variable | tests | in_table | measured_not_summarised | documented_only | video_or_archive_only | no_record_found |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 0 | 0 | 0 | 0 | 0 |
| o2_pct | counted or recorded | 0 | 0 | 0 | 0 | 0 |
| fuel_material | in scope | 376 | 0 | 0 | 0 | 0 |
| o2_pct | in scope | 139 | 124 | 0 | 113 | 0 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

### P3 Flame spread and growth

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 11. All tests in the scope of the need (tests.csv): 376.

| variable | tests | in_table | measured_not_summarised | documented_only | video_or_archive_only | no_record_found |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 11 | 0 | 0 | 0 | 0 |
| flow_cms | counted or recorded | 11 | 0 | 0 | 0 | 0 |
| flow_direction | counted or recorded | 11 | 0 | 0 | 0 | 0 |
| fuel_material | in scope | 376 | 0 | 0 | 0 | 0 |
| flow_cms | in scope | 245 | 10 | 0 | 121 | 0 |
| flow_direction | in scope | 13 | 0 | 0 | 363 | 0 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

### S1 Extinction conditions

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 570. All tests in the scope of the need (tests.csv): 1824.

| variable | tests | in_table | measured_not_summarised | documented_only | video_or_archive_only | no_record_found |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 570 | 0 | 0 | 0 | 0 |
| o2_pct | counted or recorded | 570 | 0 | 0 | 0 | 0 |
| pressure_kpa | counted or recorded | 545 | 0 | 25 | 0 | 0 |
| fuel_material | in scope | 1824 | 0 | 0 | 0 | 0 |
| o2_pct | in scope | 1141 | 135 | 0 | 548 | 0 |
| pressure_kpa | in scope | 1012 | 683 | 129 | 0 | 0 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

### D1 Combustion products

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 122. All tests in the scope of the need (tests.csv): 376.

| variable | tests | in_table | measured_not_summarised | documented_only | video_or_archive_only | no_record_found |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 122 | 0 | 0 | 0 | 0 |
| fuel_material | in scope | 376 | 0 | 0 | 0 | 0 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

### D2 Smoke generation conditions

Counted or recorded tests of the need (data/pipeline/need_tests.csv): 0. All tests in the scope of the need (tests.csv): 376.

| variable | tests | in_table | measured_not_summarised | documented_only | video_or_archive_only | no_record_found |
|---|---|---|---|---|---|---|
| fuel_material | counted or recorded | 0 | 0 | 0 | 0 | 0 |
| flow_cms | counted or recorded | 0 | 0 | 0 | 0 | 0 |
| aging_time_s | counted or recorded | 0 | 0 | 0 | 0 | 0 |
| fuel_material | in scope | 376 | 0 | 0 | 0 | 0 |
| flow_cms | in scope | 245 | 10 | 0 | 121 | 0 |
| aging_time_s | in scope | 108 | 0 | 0 | 268 | 0 |

Investigations with no per-test table, not counted here: PSI-20, PSI-21, PSI-22, PSI-23, PSI-47, PSI-60, PSI-62, PSI-68, PSI-106, PSI-115, PSI-117, PSI-142.

## Per need: states of the outcome variables, all tests in scope

| need | variable | in_table | measured_not_summarised | documented_only | video_or_archive_only | no_record_found |
|---|---|---|---|---|---|---|
| P1 | flow_event | 25 | 121 | 0 | 230 | 0 |
| P1 | o2_consumed_pct_points | 122 | 13 | 0 | 241 | 0 |
| P1 | burn_time_s | 7 | 125 | 0 | 244 | 0 |
| P1 | burn_length_cm | 8 | 0 | 0 | 368 | 0 |
| P2 | hot_ignition | 0 | 121 | 0 | 255 | 0 |
| P3 | spread_rate_mm_s | 2 | 0 | 0 | 374 | 0 |
| P3 | burn_length_cm | 8 | 0 | 0 | 368 | 0 |
| P3 | burn_time_s | 7 | 125 | 0 | 244 | 0 |
| S1 | test_end | 546 | 388 | 0 | 890 | 0 |
| S1 | extinction_diameter_mm | 197 | 156 | 0 | 1471 | 0 |
| S1 | flow_event | 25 | 121 | 0 | 1678 | 0 |
| D1 | co_produced_ppm | 118 | 0 | 0 | 258 | 0 |
| D1 | co2_produced_pct_points | 121 | 13 | 0 | 242 | 0 |
| D1 | co_to_co2_molar_ratio | 87 | 0 | 0 | 289 | 0 |
| D2 | smoke_particle_size_um | 0 | 109 | 0 | 267 | 0 |

## Per investigation

### PSI-10

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 327 of 327 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 316 of 327 mapped tests. For the other 11 tests: measured_not_summarised. |
| pressure_kpa | in_table | Recorded in the experimental table for 327 of 327 mapped tests. |
| gravity_level | in_table | Recorded in the experimental table for 327 of 327 mapped tests. |
| flow_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| sample_geometry | in_table | Recorded in the experimental table for 327 of 327 mapped tests. |
| sample_thickness_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| flow_direction | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| flow_event | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| o2_consumed_pct_points | in_table | Recorded in the experimental table for 187 of 327 mapped tests. For the other 140 tests: measured_not_summarised. |
| burn_time_s | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Ignition and retraction / Extinction detected' in tp_txt (314 files in the group; single_value_per_test; event timestamps). |
| burn_length_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| ignition_power_w | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Igniter Wattage' in chamber_calculator (2 files in the group; single_value_per_test; setting). |
| ignition_time_s | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Igniter On Time (ms)' in chamber_calculator (2 files in the group; single_value_per_test; setting). |
| hot_ignition | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Ignite' in chamber_calculator (2 files in the group; single_value_per_test; reading). |
| sample_width_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| spread_rate_mm_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| co2_pct | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: '_CO2 (block Finish Mixture (Percent))' in chamber_calculator (2 files in the group; single_value_per_test; reading). |
| he_pct | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: '_He (block Finish Mixture (Percent))' in chamber_calculator (2 files in the group; single_value_per_test; reading). |
| flow_min_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| test_end | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Extinction detected' in tp_txt (314 files in the group; single_value_per_test; event timestamp). |
| extinction_diameter_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| co_produced_ppm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| co2_produced_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| co_to_co2_molar_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| aging_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| heating_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| mass_loss_rate_mg_min | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |
| smoke_particle_size_um | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 317 videos and 1183 archives that were not opened. |

### PSI-20

The investigation has no per-test table: PSI-20_Experimental table_ACME BRE.csv: one row per test_day (One row per test day; oxygen is a list of the settings used that day).

- fuel_material: 'Fuel Type' in chamber_calculator (single_value_per_test)
- o2_pct: '_O2 (block Finish Mixture (Percent))' in chamber_calculator (single_value_per_test)
- pressure_kpa: 'Pstart (psia)' in chamber_calculator (single_value_per_test)
- burn_time_s: 'Ignition and retraction / MFCs off' in tp_txt (single_value_per_test)
- ignition_power_w: 'Igniter Wattage' in chamber_calculator (single_value_per_test)
- ignition_time_s: 'Igniter On Time (ms)' in chamber_calculator (single_value_per_test)
- hot_ignition: 'Ignite' in chamber_calculator (single_value_per_test)
- co2_pct: '_CO2 (block Finish Mixture (Percent))' in chamber_calculator (single_value_per_test)
- he_pct: '_He (block Finish Mixture (Percent))' in chamber_calculator (single_value_per_test)
- test_end: 'Extinction detected' in tp_txt (single_value_per_test)

### PSI-21

The investigation has no per-test table: PSI-21_Experimental table_CLD Flame.csv: one row per test_day (One row per test day).

- fuel_material: 'Fuel Type' in chamber_calculator (single_value_per_test)
- o2_pct: '_O2 (block Finish Mixture (Percent))' in chamber_calculator (single_value_per_test)
- pressure_kpa: 'FCU_MP_PT28(PSIA)' in fcu_readings (time_series_per_test)
- flow_cms: 'velocityAirFinalMPerSec / velocityMixFinalMPerSec' in tp_settings (single_value_per_test)
- ignition_power_w: 'Igniter Wattage' in chamber_calculator (single_value_per_test)
- ignition_time_s: 'igniterIgnitionDurationMs' in tp_settings (single_value_per_test)
- hot_ignition: 'Ignite' in chamber_calculator (single_value_per_test)
- co2_pct: '_CO2 (block Finish Mixture (Percent))' in chamber_calculator (single_value_per_test)
- he_pct: '_He (block Finish Mixture (Percent))' in chamber_calculator (single_value_per_test)
- test_end: 'Extinction detected' in tp_txt (single_value_per_test)

### PSI-22

The investigation has no per-test table: PSI-22_Experimental table_ACME E-FIELD Flames.csv: one row per test_day (One row per test day).

- flow_cms: 'velocityMixFinalMPerSec / velocityAirFinalMPerSec' in voltage_sweep (single_value_per_test)
- ignition_time_s: 'igniterIgnitionDurationMs' in voltage_sweep (single_value_per_test)
- test_end: 'Extinction detected' in tp_txt (single_value_per_test)

### PSI-23

The investigation has no per-test table: PSI-23_Experimental table_ACME s-Flame.csv: one row per test_day (One row per test day).

- burn_time_s: 'Ignition and retraction / MFCs off' in tp_txt (single_value_per_test)
- ignition_time_s: 'igniterIgnitionDurationMs' in as_run (single_value_per_test)
- test_end: 'Extinction detected' in tp_txt (single_value_per_test)

### PSI-25

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 129 of 129 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 129 of 129 mapped tests. |
| pressure_kpa | documented_only | Empty in the table; a document sentence states it for the whole table (ICES19.pressure): 'Pressure was not varied from 1 atmosphere.'. |
| gravity_level | in_table | Recorded in the experimental table for 129 of 129 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 119 of 129 mapped tests. For the other 10 tests: measured_not_summarised. |
| sample_geometry | in_table | Recorded in the experimental table for 129 of 129 mapped tests. |
| sample_thickness_mm | in_table | Recorded in the experimental table for 42 of 129 mapped tests. For the other 87 tests: video_or_archive_only. |
| flow_direction | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| flow_event | in_table | Recorded in the experimental table for 25 of 129 mapped tests. For the other 104 tests: video_or_archive_only. |
| o2_consumed_pct_points | in_table | Recorded in the experimental table for 122 of 129 mapped tests. For the other 7 tests: video_or_archive_only. |
| burn_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| burn_length_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| ignition_power_w | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| ignition_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| hot_ignition | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| sample_width_cm | in_table | Recorded in the experimental table for 71 of 129 mapped tests. For the other 58 tests: video_or_archive_only. |
| spread_rate_mm_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| co2_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| he_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| flow_min_cms | in_table | Recorded in the experimental table for 103 of 129 mapped tests. For the other 26 tests: video_or_archive_only. |
| test_end | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| extinction_diameter_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| co_produced_ppm | in_table | Recorded in the experimental table for 118 of 129 mapped tests. For the other 11 tests: video_or_archive_only. |
| co2_produced_pct_points | in_table | Recorded in the experimental table for 121 of 129 mapped tests. For the other 8 tests: video_or_archive_only. |
| co_to_co2_molar_ratio | in_table | Recorded in the experimental table for 87 of 129 mapped tests. For the other 42 tests: video_or_archive_only. |
| aging_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| heating_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| mass_loss_rate_mg_min | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |
| smoke_particle_size_um | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 296 videos and 264 archives that were not opened. |

### PSI-26

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 121 of 121 mapped tests. |
| o2_pct | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'O2 % by volume' in as_run_matrix (1 files in the group; single_value_per_test; reading). |
| pressure_kpa | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'pressure, atm' in as_run_matrix (1 files in the group; single_value_per_test; reading). |
| gravity_level | in_table | Recorded in the experimental table for 121 of 121 mapped tests. |
| flow_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| sample_geometry | in_table | Recorded in the experimental table for 101 of 121 mapped tests. For the other 20 tests: video_or_archive_only. |
| sample_thickness_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| flow_direction | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| flow_event | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Test Observations and Anomalies (ignited, spread, extinguished, burn time, color, etc.)' in as_run_matrix (1 files in the group; single_value_per_test; free text). |
| o2_consumed_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| burn_time_s | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Test Observations and Anomalies (ignited, spread, extinguished, burn time, color, etc.)' in as_run_matrix (1 files in the group; single_value_per_test; free text). |
| burn_length_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| ignition_power_w | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| ignition_time_s | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Ignition time   -  seconds' in planned_matrix (1 files in the group; single_value_per_test; planned value). |
| hot_ignition | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Test Observations and Anomalies (ignited, spread, extinguished, burn time, color, etc.)' in as_run_matrix (1 files in the group; single_value_per_test; free text). |
| sample_width_cm | in_table | Recorded in the experimental table for 79 of 121 mapped tests. For the other 42 tests: video_or_archive_only. |
| spread_rate_mm_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| co2_pct | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'CO2, mm Hg' in as_run_matrix (1 files in the group; single_value_per_test; reading). |
| he_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| flow_min_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| test_end | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| extinction_diameter_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| co_produced_ppm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| co2_produced_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| co_to_co2_molar_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| aging_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| heating_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| mass_loss_rate_mg_min | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |
| smoke_particle_size_um | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 114 videos and 59 archives that were not opened. |

### PSI-39

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| pressure_kpa | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| gravity_level | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| flow_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| sample_geometry | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| sample_thickness_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| flow_direction | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| flow_event | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| o2_consumed_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| burn_time_s | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'HF Burn Time' in cfi_data_summary (1 files in the group; single_value_per_test; investigator analysis). |
| burn_length_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| ignition_power_w | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Ignition Power ( W )' in cfi_data_summary (1 files in the group; single_value_per_test; setting). |
| ignition_time_s | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Ignition Time ( ms )' in cfi_data_summary (1 files in the group; single_value_per_test; setting). |
| hot_ignition | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| sample_width_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| spread_rate_mm_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| co2_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| he_pct | in_table | Recorded in the experimental table for 79 of 79 mapped tests. |
| flow_min_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| test_end | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| extinction_diameter_mm | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Dext, hot ( mm ) / Dext,cool ( mm )' in cfi_data_summary (1 files in the group; single_value_per_test; investigator analysis). |
| co_produced_ppm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| co2_produced_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| co_to_co2_molar_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| aging_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| heating_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| mass_loss_rate_mg_min | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |
| smoke_particle_size_um | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 246 videos and 337 archives that were not opened. |

### PSI-47

The investigation has no per-test table: PSI-47_Experimental table_DAFT.csv: one row per session (One row per sampling session; no combustion test).

- smoke_particle_size_um: 'D (micon) / Average D (micron)' in summary (per_session_or_day)

### PSI-60

The investigation has no per-test table: no experimental table in the PSI listing.

### PSI-62

The investigation has no per-test table: no experimental table in the PSI listing.

### PSI-68

The investigation has no per-test table: PSI-68_Experimental table_Flex2.csv: one row per planned_matrix (One row per fuel with the planned ranges of conditions, not tests).

- pressure_kpa: 'FCU_MP_PT16(PSIA) ... FCU_MP_PT29(PSIA)' in chamber_readings (time_series_per_test)
- flow_cms: 'FLOW_NOZZLE_1_SPEED(N/A) / FLOW_NOZZLE_2_SPEED(N/A)' in chamber_readings (time_series_per_test)
- ignition_power_w: 'IGNITER_WATTAGE(Watts) / TP_PARAMETER_IGNITER_WATTAGE(Watts)' in chamber_readings (time_series_per_test)
- ignition_time_s: 'TP_PARAMETER_IGNITER_ON_TIME(N/A)' in chamber_readings (single_value_per_test)

### PSI-69

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| pressure_kpa | in_table | Recorded in the experimental table for 273 of 274 mapped tests. For the other 1 tests: measured_not_summarised. |
| gravity_level | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| flow_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| sample_geometry | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| sample_thickness_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| flow_direction | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| flow_event | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| o2_consumed_pct_points | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'O2' in mixture (31 files in the group; unclear; reading). Each input of the team formula 'o2_pct - o2_final_pct' is in the table or in a sampled raw column. |
| burn_time_s | in_table | Recorded in the experimental table for 268 of 274 mapped tests. For the other 6 tests: video_or_archive_only. |
| burn_length_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| ignition_power_w | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Igniter Wattage' in tp_log (666 files in the group; single_value_per_test; setting). |
| ignition_time_s | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Igniter On Time (milliseconds)' in tp_log (666 files in the group; single_value_per_test; setting). |
| hot_ignition | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| sample_width_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| spread_rate_mm_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| co2_pct | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| he_pct | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| flow_min_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| test_end | in_table | Recorded in the experimental table for 274 of 274 mapped tests. |
| extinction_diameter_mm | in_table | Recorded in the experimental table for 197 of 274 mapped tests. For the other 77 tests: measured_not_summarised. |
| co_produced_ppm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| co2_produced_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| co_to_co2_molar_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| aging_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| heating_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| mass_loss_rate_mg_min | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |
| smoke_particle_size_um | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 183 videos and 1419 archives that were not opened. |

### PSI-98

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| pressure_kpa | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Ambient Pressure' in sample_sensors (2 files in the group; time_series_per_test; reading). |
| gravity_level | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| sample_geometry | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| sample_thickness_mm | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_direction | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_event | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| o2_consumed_pct_points | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'O2' in sample_sensors (2 files in the group; time_series_per_test; reading). Each input of the team formula 'o2_pct - o2_final_pct' is in the table or in a sampled raw column. |
| burn_time_s | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| burn_length_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| ignition_power_w | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| ignition_time_s | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| hot_ignition | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| sample_width_cm | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| spread_rate_mm_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| co2_pct | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'CO2' in sample_sensors (2 files in the group; time_series_per_test; reading). |
| he_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| flow_min_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| test_end | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| extinction_diameter_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| co_produced_ppm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| co2_produced_pct_points | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'CO2' in sample_sensors (2 files in the group; time_series_per_test; reading). Each input of the team formula 'co2_final_pct - co2_initial_pct' is in the table or in a sampled raw column. |
| co_to_co2_molar_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| aging_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| heating_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| mass_loss_rate_mg_min | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |
| smoke_particle_size_um | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 61 archives that were not opened. |

### PSI-99

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 8 of 9 mapped tests. For the other 1 tests: measured_not_summarised. |
| pressure_kpa | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Ambient Pressure' in sample_sensors (9 files in the group; time_series_per_test; reading). |
| gravity_level | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| sample_geometry | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| sample_thickness_mm | in_table | Recorded in the experimental table for 4 of 9 mapped tests. For the other 5 tests: video_or_archive_only. |
| flow_direction | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| flow_event | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |
| o2_consumed_pct_points | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'O2' in sample_sensors (9 files in the group; time_series_per_test; reading). Each input of the team formula 'o2_pct - o2_final_pct' is in the table or in a sampled raw column. |
| burn_time_s | in_table | Recorded in the experimental table for 5 of 9 mapped tests. For the other 4 tests: video_or_archive_only. |
| burn_length_cm | in_table | Recorded in the experimental table for 8 of 9 mapped tests. For the other 1 tests: video_or_archive_only. |
| ignition_power_w | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| ignition_time_s | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| hot_ignition | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |
| sample_width_cm | in_table | Recorded in the experimental table for 9 of 9 mapped tests. |
| spread_rate_mm_s | in_table | Recorded in the experimental table for 2 of 9 mapped tests. For the other 7 tests: video_or_archive_only. |
| co2_pct | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'CO2' in sample_sensors (9 files in the group; time_series_per_test; reading). |
| he_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |
| flow_min_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |
| test_end | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |
| extinction_diameter_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |
| co_produced_ppm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |
| co2_produced_pct_points | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'CO2' in sample_sensors (9 files in the group; time_series_per_test; reading). Each input of the team formula 'co2_final_pct - co2_initial_pct' is in the table or in a sampled raw column. |
| co_to_co2_molar_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |
| aging_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |
| heating_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |
| mass_loss_rate_mg_min | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |
| smoke_particle_size_um | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 186 archives that were not opened. |

### PSI-100

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| o2_pct | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'O2' in sample_sensors (2 files in the group; time_series_per_test; reading). |
| pressure_kpa | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Ambient Pressure' in sample_sensors (2 files in the group; time_series_per_test; reading). |
| gravity_level | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| sample_geometry | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| sample_thickness_mm | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_direction | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| flow_event | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| o2_consumed_pct_points | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'O2' in sample_sensors (2 files in the group; time_series_per_test; reading). Each input of the team formula 'o2_pct - o2_final_pct' is in the table or in a sampled raw column. |
| burn_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| burn_length_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| ignition_power_w | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| ignition_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| hot_ignition | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| sample_width_cm | in_table | Recorded in the experimental table for 2 of 2 mapped tests. |
| spread_rate_mm_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| co2_pct | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'CO2' in sample_sensors (2 files in the group; time_series_per_test; reading). |
| he_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| flow_min_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| test_end | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| extinction_diameter_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| co_produced_ppm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| co2_produced_pct_points | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'CO2' in sample_sensors (2 files in the group; time_series_per_test; reading). Each input of the team formula 'co2_final_pct - co2_initial_pct' is in the table or in a sampled raw column. |
| co_to_co2_molar_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| aging_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| heating_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| mass_loss_rate_mg_min | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |
| smoke_particle_size_um | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 0 videos and 67 archives that were not opened. |

### PSI-101

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 109 of 109 mapped tests. |
| o2_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| pressure_kpa | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'SampleSidePressure[AT20](PSIA)' in hkp_csv (44 files in the group; time_series_per_test; reading). |
| gravity_level | in_table | Recorded in the experimental table for 109 of 109 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 109 of 109 mapped tests. |
| sample_geometry | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| sample_thickness_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| flow_direction | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| flow_event | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| o2_consumed_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| burn_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| burn_length_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| ignition_power_w | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| ignition_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| hot_ignition | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| sample_width_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| spread_rate_mm_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| co2_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| he_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| flow_min_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| test_end | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| extinction_diameter_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| co_produced_ppm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| co2_produced_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| co_to_co2_molar_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| aging_time_s | in_table | Recorded in the experimental table for 104 of 109 mapped tests. For the other 5 tests: video_or_archive_only. |
| heating_ratio | in_table | Recorded in the experimental table for 109 of 109 mapped tests. |
| mass_loss_rate_mg_min | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 8 videos and 79 archives that were not opened. |
| smoke_particle_size_um | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'M1/M0 (micro-m)--AMD / Diameter of Average mass (micro-m) / Hatch Choate Dg' in results (1 files in the group; single_value_per_test; investigator analysis). |

### PSI-102

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 4 of 4 mapped tests. |
| o2_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| pressure_kpa | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'SampleSidePressure[AT20](PSIA)' in hkp_workbooks (42 files in the group; time_series_per_test; reading). |
| gravity_level | in_table | Recorded in the experimental table for 4 of 4 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 4 of 4 mapped tests. |
| sample_geometry | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| sample_thickness_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| flow_direction | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| flow_event | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| o2_consumed_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| burn_time_s | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'ElapsedTestTime(Secs)' in hkp_workbooks (42 files in the group; time_series_per_test; elapsed test time). |
| burn_length_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| ignition_power_w | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| ignition_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| hot_ignition | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| sample_width_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| spread_rate_mm_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| co2_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| he_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| flow_min_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| test_end | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| extinction_diameter_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| co_produced_ppm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| co2_produced_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| co_to_co2_molar_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| aging_time_s | in_table | Recorded in the experimental table for 4 of 4 mapped tests. |
| heating_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |
| mass_loss_rate_mg_min | in_table | Recorded in the experimental table for 4 of 4 mapped tests. |
| smoke_particle_size_um | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 2 videos and 3 archives that were not opened. |

### PSI-106

The investigation has no per-test table: PSI-106_Experimental table_Slice.csv: one row per test_day (One row per test day; no per-test conditions).

### PSI-107

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 435 of 435 mapped tests. |
| o2_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| pressure_kpa | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Pressure (Pa)' in flight_test_data (1 files in the group; single_value_per_test; reading). |
| gravity_level | in_table | Recorded in the experimental table for 435 of 435 mapped tests. |
| flow_cms | in_table | Recorded in the experimental table for 407 of 435 mapped tests. For the other 28 tests: measured_not_summarised. |
| sample_geometry | in_table | Recorded in the experimental table for 435 of 435 mapped tests. |
| sample_thickness_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| flow_direction | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| flow_event | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| o2_consumed_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| burn_time_s | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'GMT ignition / GMT  Flame Off ' in flight_test_data (1 files in the group; single_value_per_test; event timestamps). |
| burn_length_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| ignition_power_w | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| ignition_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| hot_ignition | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| sample_width_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| spread_rate_mm_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| co2_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| he_pct | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| flow_min_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| test_end | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| extinction_diameter_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| co_produced_ppm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| co2_produced_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| co_to_co2_molar_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| aging_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| heating_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| mass_loss_rate_mg_min | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |
| smoke_particle_size_um | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 19 videos and 100 archives that were not opened. |

### PSI-115

The investigation has no per-test table: no experimental table in the PSI listing.

### PSI-117

The investigation has no per-test table: no experimental table in the PSI listing.

### PSI-142

The investigation has no per-test table: PSI-142_Experimental table_Data Summary Table.csv: one row per dataset_index (Index of figures in publications).

### PSI-159

| variable | state | text |
|---|---|---|
| fuel_material | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| o2_pct | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| pressure_kpa | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| gravity_level | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| flow_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| sample_geometry | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| sample_thickness_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| flow_direction | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| flow_event | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| o2_consumed_pct_points | in_table | Recorded in the experimental table for 179 of 333 mapped tests. For the other 154 tests: video_or_archive_only. |
| burn_time_s | in_table | Recorded in the experimental table for 329 of 333 mapped tests. For the other 4 tests: video_or_archive_only. |
| burn_length_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| ignition_power_w | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'Igniter Wattage' in chamber_calculator (1 files in the group; single_value_per_test; setting). |
| ignition_time_s | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: 'igniterIgnitionDurationMs' in as_run (339 files in the group; single_value_per_test; setting). |
| hot_ignition | in_table | Recorded in the experimental table for 333 of 333 mapped tests. |
| sample_width_cm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| spread_rate_mm_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| co2_pct | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: '_CO2 (block Finish Mixture (Percent))' in chamber_calculator (1 files in the group; single_value_per_test; reading). |
| he_pct | measured_not_summarised | Empty in the table; a sampled raw file has a column for it: '_He (block Finish Mixture (Percent))' in chamber_calculator (1 files in the group; single_value_per_test; reading). |
| flow_min_cms | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| test_end | in_table | Recorded in the experimental table for 272 of 333 mapped tests. For the other 61 tests: measured_not_summarised. |
| extinction_diameter_mm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| co_produced_ppm | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| co2_produced_pct_points | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| co_to_co2_molar_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| aging_time_s | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| heating_ratio | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| mass_loss_rate_mg_min | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |
| smoke_particle_size_um | video_or_archive_only | Empty in the table and in every sampled table column; the listing has 337 videos and 986 archives that were not opened. |

