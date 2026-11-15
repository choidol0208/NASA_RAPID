# Independent recount of the raw-data chain

*AI-generated (Claude Code): code and report by a second AI session independent of the pipeline, 2026-11-15. No language model runs when the script runs.*

Recomputed by a second AI session with code that does not import the pipeline; not checked by a person.

Script: `validation/raw_chain_recount.py` (offline run of 2026-11-15T01:08:39Z). Figures: `validation/raw_chain_recount.json`. It imports no module of `pipeline/`, `video/`, `ai/`, `scripts/` or `scoring/`; their source and the design documents were read as text to learn the rules. Every 'match' below is computed by the script from the expected value typed from the design and the recounted value; no rule was changed to reach a number. A research exploration aid, not safety guidance; the counts are the team's, not NASA's.

**Summary: 62 of 71 fixtures reproduce.** Fixtures that do not reproduce:

- E: link states: two agree / one / disagree / day only / id not in table / none: expected 662 / 374 / 10 / 1,217 / 330 / 30, recounted 662 / 374 / 15 / 1,201 / 341 / 30
- E: link state bytes (same order): expected 152,320,655,239 / 81,527,352,372 / 5,118,358,115 / 102,112,670,418 / 83,454,932,324 / 1,519,722,834, recounted 152,320,655,239 / 81,527,352,372 / 7,305,710,080 / 97,172,521,694 / 86,207,729,083 / 1,519,722,834
- E: tie scope: test / run / day / several days / none: expected 1,046 / 3 / 1,188 / 26 / 360, recounted 1,051 / 0 / 1,175 / 26 / 371
- E: PSI-26 videos by link state (six states): expected 0 / 0 / 0 / 113 / 1 / 0, recounted 0 / 0 / 0 / 101 / 13 / 0
- E: PSI-39 videos by link state (six states): expected 101 / 5 / 2 / 20 / 118 / 0, recounted 101 / 5 / 7 / 16 / 117 / 0
- E: tests by best state: two agree / one / disagree only: expected 463 / 344 / 6, recounted 463 / 344 / 8
- E: S1 counted tests: total / two agree / one / disagree only / none: expected 298 / 19 / 10 / 1 / 268, recounted 298 / 19 / 10 / 2 / 267
- E: iss, S1, outside_by_recorded_value: counted / two agree / one / disagree only / none: expected 235 / 14 / 6 / 1 / 214, recounted 235 / 14 / 6 / 2 / 213
- E: lunar_habitat, S1, outside_by_recorded_value: counted / two agree / one / disagree only / none: expected 281 / 19 / 10 / 1 / 251, recounted 281 / 19 / 10 / 2 / 250

## Inputs and definitions

- Listings: the 24 saved listings in `data/psi/file_listings/` (git-ignored) were fetched for this recount on 2026-11-15T00:12:50Z to 2026-11-15T00:15:00Z (the 24 listing calls of the network log), not the team's listing of 2026-11-14T05:57:17Z; section F compares the two. The FLEX test sheets are in `data/psi/raw_cache/PSI-69/test_sheets/` (git-ignored).
- A file is one record of a listing, counted once per PSI file id; bytes are `bytes_size` as PSI reports them.
- Placement (A) uses `o2_pct`, `o2_basis` and `pressure_kpa` of `data/pipeline/tests.csv` and the ranges of `pipeline/spec/scenarios.json` (minimum inclusive; maximum inclusive only where `max_inclusive` is set). Order: no range set; inside; outside by a recorded value; oxygen of an oxidizer stream; otherwise cannot be placed.
- **Counted tests** are the rows of `data/pipeline/need_tests.csv` with `objective_link = stated`.
- A test of `tests.csv` is tied to its NASA table row by `source_file` and `source_row` (CSV record, header = 1). Check where the test id carries the row's identifier (PSI-10, 25, 39, 69, 159): consistent: 1,142; not checkable: 682.
- Tables are read as UTF-8, except `PSI-69_Experimental table_FLEX.csv`, which is not valid UTF-8 and is read as cp1252 (its 0x96 bytes are en dashes), so its cells are compared exactly as written.
- The claimed side (`scenario_tests.csv`, `need_gap_states.csv`, `raw_inventory.json`, `video/data/video_links.csv`) is read only to compare; no count uses it.

## Fixtures, expected against recounted

### A. Placement per scenario

| Fixture | Expected | Recounted | Match |
|---|---|---|---|
| lunar_habitat, all tests: inside / cannot be placed / oxidizer stream / outside | 26 / 676 / 63 / 1,059 | 26 / 676 / 63 / 1,059 | yes |
| lunar_habitat, solid-fuel tests: inside / cannot be placed / outside | 0 / 237 / 139 | 0 / 237 / 139 | yes |
| iss, all tests: inside / cannot be placed / oxidizer stream / outside | 179 / 739 / 106 / 800 | 179 / 739 / 106 / 800 | yes |
| mars_habitat: no range set | 1,824 | 1,824 | yes |
| per-test o2_match and pressure_match differing from scenario_tests.csv | 0 | 0 | yes |

- lunar_habitat: cannot be placed by pair: o2 not_recorded, pressure in: 4; o2 not_recorded, pressure not_recorded: 672; by investigation: PSI-107: 435; PSI-26: 121; PSI-101: 109; PSI-10: 4; PSI-102: 4; PSI-100: 2; PSI-99: 1. Inside by investigation: PSI-69: 17; PSI-159: 9. Solid-fuel pairs: o2 not_recorded, pressure not_recorded: 237; o2 out, pressure not_recorded: 139.
- lunar_habitat, if an oxidizer-stream test were never 'outside' (other reading of the order): inside: 26; cannot_be_placed_from_table: 676; oxygen_of_oxidizer_stream: 263; outside_by_recorded_value: 859; no_range_set: 0. The fixtures follow 'outside first'.
- iss: cannot be placed by pair: o2 in, pressure not_recorded: 62; o2 not_recorded, pressure in: 5; o2 not_recorded, pressure not_recorded: 672; by investigation: PSI-107: 435; PSI-26: 121; PSI-101: 109; PSI-25: 51; PSI-99: 9; PSI-10: 5; PSI-102: 4; PSI-100: 2; PSI-98: 2; PSI-69: 1. Inside by investigation: PSI-10: 71; PSI-69: 56; PSI-159: 27; PSI-39: 25. Solid-fuel pairs: o2 in, pressure not_recorded: 61; o2 not_recorded, pressure not_recorded: 237; o2 out, pressure not_recorded: 78.
- iss, if an oxidizer-stream test were never 'outside' (other reading of the order): inside: 179; cannot_be_placed_from_table: 739; oxygen_of_oxidizer_stream: 263; outside_by_recorded_value: 643; no_range_set: 0. The fixtures follow 'outside first'.
- Per test: 10,944 (scenario, test) rows of `scenario_tests.csv` compared on `o2_match` and `pressure_match`; 0 differ; 0 recounted pairs are missing from the claimed file.

### B. Chain sums (states per need and variable)

| Fixture | Expected | Recounted | Match |
|---|---|---|---|
| need_gap_states.csv keys whose states do not sum to in-scope / counted totals | 0 | 0 | yes |
| need_gap_states.csv keys differing from the recomputed states | 0 | 0 | yes |
| P1 pressure: raw column / document only / not found (in-scope tests) | 134 / 129 / 113 | 134 / 129 / 113 | yes |

- `need_gap_states.csv`: 426 rows, 186 (scenario, need, role, variable) keys over 6 scenarios; for every key the states sum to the in-scope and the counted totals, and every key's states equal the states recomputed from `tests.csv`, `raw_columns.json` and `sources.json` (README 'State rule').
- P1 pressure, in-scope tests by state (counted tests in brackets): column_in_sampled_raw_file|sensor_reading_series: 13 / 8; column_in_sampled_raw_file|value_per_test_in_a_results_file: 121 / 0; documented_only|: 129 / 125; not_in_sampled_files|: 113 / 0.
- `question_chain.csv`: not in data/pipeline/ (not compared).

### C. Files that name the tests inside the lunar ranges

| Fixture | Expected | Recounted | Match |
|---|---|---|---|
| 17 lunar FLEX tests: files, bytes | 299 / 24,954,842,492 | 299 / 24,954,842,492 | yes |
| 17 lunar FLEX tests: zip files, bytes | 47 / 24,923,186,032 | 47 / 24,923,186,032 | yes |
| 17 lunar FLEX tests: other files, bytes | 252 / 31,656,460 | 252 / 31,656,460 | yes |
| 17 lunar FLEX tests by extension: .txt / .zip / .pdf / .rtf | 212 / 47 / 23 / 17 | 212 / 47 / 23 / 17 | yes |
| 9 lunar CFI-G tests: files, bytes | 99 / 79,403,613,858 | 99 / 79,403,613,858 | yes |
| 9 lunar CFI-G tests: zip or ts files | 35 | 35 | yes |
| 26 lunar tests: files, bytes | 398 / 104,358,456,350 | 398 / 104,358,456,350 | yes |
| 26 lunar tests: second label folder agrees / names no test / names another test | 336 / 47 / 15 | 336 / 47 / 15 | yes |
| 26 lunar tests: small files, bytes; archives and recordings, bytes | 316 / 86,853,632 / 82 / 104,271,602,718 | 316 / 86,853,632 / 82 / 104,271,602,718 | yes |
| FLEX identifier 193F001 on table rows (FLEX Test #) | 70 / 73 | 70 / 73 | yes |
| FLEX test sheets numbered above the last table row | 6 | 6 | yes |
| FLEX-19: files, bytes | 17 / 1,112,400,426 | 17 / 1,112,400,426 | yes |

- Name matching. The PSI prefix (`PSI-69_Raw Data_`) is removed first. A PSI-69 file names a test when its name carries the test's FLEX number (`FLEX-nnn`, `FLEX_nnn`, `FLEX nnn` or `FLEXnnn`, any case) or its NASA identifier (any shape of the table's `FLEX Identifier` column: `dddFddd`, `dddRddd`, `ddCALdd`, `[C, H or N]dd[H or M]ddd`; optionally followed by one camera letter A-D, as `196F001A.zip`), with no letter or digit next to it. A PSI-159 file names a test when its name carries the test point (`YYDDD`, an optional space, a letter, one or two digits). The second label is the PSI folder path (subcategory): 'agrees' when every FLEX number and identifier (CFI-G: test point) in it points to the same test, 'names no test' when it holds none, 'names another test' otherwise.
- Two-label rule: the name number of a FLEX file is never taken alone. Of the 299 FLEX files, by the labels in the name: name_identifier: 197; name_number: 102; by all four labels (name number, name identifier, folder number, folder identifier): labels_disagree: 15; one_label: 47; two_or_more_labels_agree: 237; files whose only label is the name number: 0. The 47 archives carry the identifier in the name and sit in a folder that names no test (one label). For these 17 tests the file number equals the table row (block D, read from the sheets), but block D also shows 120 sheets whose file number is ahead of the table's FLEX Test #, so a FLEX file number is a label only where a second label agrees.
- Files in a folder that names another test: 15, tests FLEX-20, folder(s) `Reduced Gravity/MeOH/FLEX_021_24_Oct_2009_MeOH_192F002`.
- Per FLEX test (files, bytes, zip): FLEX-19 17, 1,112,400,426, 3; FLEX-20 18, 1,342,202,750, 3; FLEX-21 19, 1,325,793,225, 3; FLEX-22 17, 2,954,440, 0; FLEX-23 17, 1,028,727,355, 3; FLEX-24 14, 174,487,403, 2; FLEX-25 19, 1,389,227,929, 3; FLEX-26 19, 1,313,249,751, 3; FLEX-27 18, 1,244,502,347, 3; FLEX-28 18, 1,382,842,295, 3; FLEX-37 18, 2,191,287,012, 3; FLEX-38 18, 2,161,410,728, 3; FLEX-39 18, 2,006,869,714, 3; FLEX-40 17, 2,211,853,480, 3; FLEX-41 17, 2,109,625,992, 3; FLEX-42 17, 1,813,737,464, 3; FLEX-43 18, 2,143,670,181, 3.
- CFI-G per test (files): CFIG-N-21106F1: 11; CFIG-N-21106F2: 12; CFIG-N-21106F3: 11; CFIG-N-21106F4: 10; CFIG-N-21106F5: 11; CFIG-N-21153A4: 11; CFIG-N-21153A5: 11; CFIG-N-21153F1: 11; CFIG-N-21174B1: 11; by extension: .csv: 18; .mdipsug: 18; .next: 1; .ts: 8; .txt: 27; .zip: 27. 26 tests: 0.7746% of the archive's bytes.
- FLEX table: 274 rows, 273 distinct identifiers; repeated: 193F001: 70 / 73 (FLEX Test #), CSV lines 193F001: 71 / 74. Sheets numbered above row 274: 275 / 276 / 277 / 278 / 279 / 280.
- FLEX-19: 14 small files (1,243,765 bytes) and archives 196F001A.zip 952,278,112 / 196F001B.zip 109,527,990 / 196F001D.zip 49,350,559.

### D. FLEX test sheets against the FLEX table

| Fixture | Expected | Recounted | Match |
|---|---|---|---|
| FLEX test sheets in the listing: files, bytes | 272 / 250,375 | 272 / 250,375 | yes |
| 17 lunar sheets: files, bytes | 17 / 15,369 | 17 / 15,369 | yes |
| 17 lunar sheets (by file number): identifier inside equals the table's | 17 | 17 | yes |
| 17 lunar sheets: tied to one row (identifier + second field), row = file number | 17 / 17 | 17 / 17 | yes |
| 17 lunar sheets: pressure agrees within rounding | 16 | 16 | yes |
| 17 lunar sheets: oxygen agrees | 16 | 16 | yes |
| 17 lunar sheets: Dext cross-table of design.md section 7 | table 0, sheet 0.00: FLEX-39 / FLEX-43; table blank, sheet a number: FLEX-23 / FLEX-38; table blank, sheet nan: FLEX-19 / FLEX-22 / FLEX-24 / FLEX-27 / FLEX-28 / FLEX-37; table dash, sheet 0.00: FLEX-41; table dash, sheet a number: FLEX-40; table dash, sheet nan: FLEX-42; table number above zero, sheet nan: FLEX-20; table number above zero, sheet the same number: FLEX-21 / FLEX-25 / FLEX-26 | table 0, sheet 0.00: FLEX-39 / FLEX-43; table blank, sheet a number: FLEX-23 / FLEX-38; table blank, sheet nan: FLEX-19 / FLEX-22 / FLEX-24 / FLEX-27 / FLEX-28 / FLEX-37; table dash, sheet 0.00: FLEX-41; table dash, sheet a number: FLEX-40; table dash, sheet nan: FLEX-42; table number above zero, sheet nan: FLEX-20; table number above zero, sheet the same number: FLEX-21 / FLEX-25 / FLEX-26 | yes |
| FLEX table extinction column: numbers / zeros / blanks / en dashes (274 rows) | 189 / 8 / 49 / 28 / 274 | 189 / 8 / 49 / 28 / 274 | yes |

- Each sheet is read in full; lines `key = value` and `key: value` above `COMMENTS:` are kept exactly as written (only surrounding blanks removed). A sheet is tied to a table row by `CIR Test Number` equal to `FLEX Identifier` together with the test date (else oxygen and pressure). Pressure agrees when the table's mmHg / 760 is within half a unit of the last digit the sheet writes in atm; other numbers agree when they are the same decimal number (`0.4` = `0.40`, `0` = `0.00`); `nan`, a blank or a dash are not comparable.
- All 272 sheets (250,375 bytes; size on disk equals the listing for 272): tied to one row 270 (identifier + date: 265; identifier + oxygen and pressure: 5); identifier not in the table 0; name number against tied row: equal: 150; not tied: 2; differ: 120.
- All sheets, field by field (agree / differ / not comparable): name_number_equals_table_test_number: agree: 150; differ: 120; date: agree: 265; differ: 5; time: agree: 265; differ: 5; pressure: agree: 269; differ: 1; O2 Mole Fraction: agree: 257; differ: 13; N2 Mole Fraction: agree: 258; differ: 12; CO2 Mole Fraction: agree: 263; differ: 7; He Mole Fraction: agree: 266; not comparable: 1; differ: 3; D0 (mm): agree: 258; differ: 1; not comparable: 11; kavg (mm2/s): agree: 251; differ: 5; not comparable: 14; Dext (mm): differ: 12; agree: 179; not comparable: 79; Fuel: agree: 267; differ: 3.
- All tied sheets, extinction diameter, table cell against sheet line `Dext (mm)`: table 0, sheet 0.00: 7; table 0, sheet nan: 1; table blank, sheet a number: 13; table blank, sheet missing: 1; table blank, sheet nan: 28; table blank, sheet other text: 5; table dash, sheet 0.0: 1; table dash, sheet 0.00: 1; table dash, sheet a number: 9; table dash, sheet nan: 12; table dash, sheet other text: 4; table number above zero, sheet a different number: 12; table number above zero, sheet nan: 4; table number above zero, sheet the same number: 172.
- 17 lunar sheets, the cross-table with the values as written:

  | Table cell | Sheet line `Dext (mm)` | Tests |
  |---|---|---|
  | 0 | 0.00 | FLEX-39 (table 0, sheet 0.00); FLEX-43 (table 0, sheet 0.00) |
  | blank | a number | FLEX-23 (table blank, sheet 1.32); FLEX-38 (table blank, sheet 1.88) |
  | blank | nan | FLEX-19 (table blank, sheet nan); FLEX-22 (table blank, sheet nan); FLEX-24 (table blank, sheet nan); FLEX-27 (table blank, sheet nan); FLEX-28 (table blank, sheet nan); FLEX-37 (table blank, sheet nan) |
  | dash | 0.00 | FLEX-41 (table –, sheet 0.00) |
  | dash | a number | FLEX-40 (table –, sheet 1.77) |
  | dash | nan | FLEX-42 (table –, sheet nan) |
  | number above zero | nan | FLEX-20 (table 1.56, sheet nan) |
  | number above zero | the same number | FLEX-21 (table 0.95, sheet 0.95); FLEX-25 (table 0.59, sheet 0.59); FLEX-26 (table 0.4, sheet 0.40) |

- 17 lunar sheets, fields that differ (sheet as written / table as written): FLEX-23: pressure 0.70 / 541.8; FLEX-28: O2 Mole Fraction 0.29 / 0.3.
- Crosswalk of the two FLEX numberings: the sheet's file number equals the FLEX Test # of the row it is tied to for 150 sheets. For 120 sheets (file numbers 128, 157 to 204, 206 to 212, 214 to 215, 217 to 227, 229, 231 to 280; some numbers have no sheet) the file number is ahead of the row by 1 (49 sheets), 2 (7 sheets), 3 (2 sheets), 4 (11 sheets), 5 (1 sheets), 6 (50 sheets). The full list is in the JSON (`crosswalk_where_name_number_differs`). So a FLEX file number is not, in general, the table's FLEX Test #.
- Sheets not tied to one row: 2: FLEX-070_TestSheet.txt (identifier 193F001 is on rows [70, 73]; sheet date and time ['Tuesday, March 23, 2010', '07:25:43 (GMT)']; rows 70: 3/23/2010 / 7:25:43; 73: 3/23/2010 / 7:25:43); FLEX-073_TestSheet.txt (identifier 193F001 is on rows [70, 73]; sheet date and time ['Tuesday, March 23, 2010', '07:25:43 (GMT)']; rows 70: 3/23/2010 / 7:25:43; 73: 3/23/2010 / 7:25:43). The two rows write the same date and the same time, so no field of the tie rule separates them and both sheets stay untied (listed, not resolved).

### E. Videos (two-label rule)

| Fixture | Expected | Recounted | Match |
|---|---|---|---|
| videos: files, bytes | 2,623 / 426,053,691,302 | 2,623 / 426,053,691,302 | yes |
| link states: two agree / one / disagree / day only / id not in table / none | 662 / 374 / 10 / 1,217 / 330 / 30 | 662 / 374 / 15 / 1,201 / 341 / 30 | **no** |
| link state bytes (same order) | 152,320,655,239 / 81,527,352,372 / 5,118,358,115 / 102,112,670,418 / 83,454,932,324 / 1,519,722,834 | 152,320,655,239 / 81,527,352,372 / 7,305,710,080 / 97,172,521,694 / 86,207,729,083 / 1,519,722,834 | **no** |
| tie scope: test / run / day / several days / none | 1,046 / 3 / 1,188 / 26 / 360 | 1,051 / 0 / 1,175 / 26 / 371 | **no** |
| PSI-10 videos by link state (six states) | 0 / 306 / 0 / 11 / 0 / 0 | 0 / 306 / 0 / 11 / 0 / 0 | yes |
| PSI-20 videos by link state (six states) | 0 / 0 / 0 / 163 / 33 / 3 | 0 / 0 / 0 / 163 / 33 / 3 | yes |
| PSI-21 videos by link state (six states) | 0 / 0 / 0 / 358 / 2 / 3 | 0 / 0 / 0 / 358 / 2 / 3 | yes |
| PSI-22 videos by link state (six states) | 0 / 0 / 0 / 215 / 0 / 6 | 0 / 0 / 0 / 215 / 0 / 6 | yes |
| PSI-23 videos by link state (six states) | 0 / 0 / 0 / 285 / 1 / 4 | 0 / 0 / 0 / 285 / 1 / 4 | yes |
| PSI-25 videos by link state (six states) | 244 / 47 / 5 / 0 / 0 / 0 | 244 / 47 / 5 / 0 / 0 / 0 | yes |
| PSI-26 videos by link state (six states) | 0 / 0 / 0 / 113 / 1 / 0 | 0 / 0 / 0 / 101 / 13 / 0 | **no** |
| PSI-39 videos by link state (six states) | 101 / 5 / 2 / 20 / 118 / 0 | 101 / 5 / 7 / 16 / 117 / 0 | **no** |
| PSI-69 videos by link state (six states) | 3 / 5 / 1 / 0 / 163 / 11 | 3 / 5 / 1 / 0 / 163 / 11 | yes |
| PSI-101 videos by link state (six states) | 0 / 0 / 0 / 8 / 0 / 0 | 0 / 0 / 0 / 8 / 0 / 0 | yes |
| PSI-102 videos by link state (six states) | 0 / 0 / 0 / 0 / 0 / 2 | 0 / 0 / 0 / 0 / 0 / 2 | yes |
| PSI-106 videos by link state (six states) | 0 / 0 / 0 / 27 / 0 / 1 | 0 / 0 / 0 / 27 / 0 / 1 | yes |
| PSI-107 videos by link state (six states) | 0 / 0 / 0 / 7 / 12 / 0 | 0 / 0 / 0 / 7 / 12 / 0 | yes |
| PSI-159 videos by link state (six states) | 314 / 11 / 2 / 10 / 0 / 0 | 314 / 11 / 2 / 10 / 0 / 0 | yes |
| tests by best state: two agree / one / disagree only | 463 / 344 / 6 | 463 / 344 / 8 | **no** |
| BASS-II tests by best state | 101 / 20 / 2 | 101 / 20 / 2 | yes |
| P1 counted tests: total / two agree / one / disagree only / none | 133 / 99 / 18 / 2 / 14 | 133 / 99 / 18 / 2 / 14 | yes |
| D1 counted tests: total / two agree / one / disagree only / none | 122 / 98 / 16 / 2 / 6 | 122 / 98 / 16 / 2 / 6 | yes |
| S1 counted tests: total / two agree / one / disagree only / none | 298 / 19 / 10 / 1 / 268 | 298 / 19 / 10 / 2 / 267 | **no** |
| P3 counted tests: total / two agree / one / disagree only / none | 2 / 0 / 0 / 0 / 2 | 2 / 0 / 0 / 0 / 2 | yes |
| iss, P1, oxygen_inside_pressure_not_in_table: counted / two agree / one / disagree only / none | 55 / 42 / 4 / 0 / 9 | 55 / 42 / 4 / 0 / 9 | yes |
| iss, P1, outside_by_recorded_value: counted / two agree / one / disagree only / none | 78 / 57 / 14 / 2 / 5 | 78 / 57 / 14 / 2 / 5 | yes |
| iss, D1, oxygen_inside_pressure_not_in_table: counted / two agree / one / disagree only / none | 45 / 42 / 2 / 0 / 1 | 45 / 42 / 2 / 0 / 1 | yes |
| iss, D1, outside_by_recorded_value: counted / two agree / one / disagree only / none | 77 / 56 / 14 / 2 / 5 | 77 / 56 / 14 / 2 / 5 | yes |
| iss, S1, inside: counted / two agree / one / disagree only / none | 56 / 2 / 0 / 0 / 54 | 56 / 2 / 0 / 0 / 54 | yes |
| iss, S1, oxygen_inside_pressure_not_in_table: counted / two agree / one / disagree only / none | 7 / 3 / 4 / 0 / 0 | 7 / 3 / 4 / 0 / 0 | yes |
| iss, S1, outside_by_recorded_value: counted / two agree / one / disagree only / none | 235 / 14 / 6 / 1 / 214 | 235 / 14 / 6 / 2 / 213 | **no** |
| iss, P3, oxygen_inside_pressure_not_in_table: counted / two agree / one / disagree only / none | 2 / 0 / 0 / 0 / 2 | 2 / 0 / 0 / 0 / 2 | yes |
| lunar_habitat, S1, inside: counted / two agree / one / disagree only / none | 17 / 0 / 0 / 0 / 17 | 17 / 0 / 0 / 0 / 17 | yes |
| lunar_habitat, S1, outside_by_recorded_value: counted / two agree / one / disagree only / none | 281 / 19 / 10 / 1 / 251 | 281 / 19 / 10 / 2 / 250 | **no** |
| lunar_habitat, P1, outside_by_recorded_value: counted / two agree / one / disagree only / none | 133 / 99 / 18 / 2 / 14 | 133 / 99 / 18 / 2 / 14 | yes |
| lunar_habitat, D1, outside_by_recorded_value: counted / two agree / one / disagree only / none | 122 / 98 / 16 / 2 / 6 | 122 / 98 / 16 / 2 / 6 | yes |
| lunar_habitat, P3, outside_by_recorded_value: counted / two agree / one / disagree only / none | 2 / 0 / 0 / 0 / 2 | 2 / 0 / 0 / 0 / 2 | yes |
| lunar inside: tests, with a two-labels-agree video, its files, bytes | 26 / 8 / 8 / 2,640,554,564 | 26 / 8 / 8 / 2,640,554,564 | yes |
| videos tied at test scope to a counted test: files, bytes, BASS-II, FLEX | 298 / 17,993,880,758 / 289 / 9 | 298 / 17,993,880,758 / 289 / 9 | yes |

- Rule as implemented (from `docs/video_design/design.md` section 4 and the rule table at its end): two labels only, the NASA identifier in the file name and the PSI folder name. Outreach, reference and engineering clips (categories Presentations, Reference Data, Engineering Documents; names with `wo66...` or `Interviews`) are `none`. ACME (PSI-10, 20, 21, 22, 23, 159): test points `YYDDDX#` in the name; the folder label is the first test point in the last folder, else the one before; per-day tables (PSI-20 to 23) give day ties only. BASS-II: `BASS_GMT{day}_SAMPLE_{n}_TEST_{test}` or `{test}-...`, folder `/{test}`; a run letter in the name with the folder naming the test without it is one label; day or sample of the name not fitting the tied row is `labels_disagree`. CFI: `F{ddd}{A-E}{nn}` against `CIR`. FLEX: a `FLEX Identifier` of the table in the name or at the end of the leaf folder; the folder's FLEX number is never used; 2013-2014 test points are `id_not_in_table`. BASS: name date minus one day against `Date`; SAME-R: recording date against `Date`; SLICE: folder day or day range; SPICE: `GMT` day. A test point that ties no row falls back to its day; an identifier or day not in the table is `id_not_in_table`. A `labels_disagree` video is counted for every test one of its labels names.
- Per investigation, six states in the order two agree / one / disagree / day only / not in table / none: PSI-10 0 / 306 / 0 / 11 / 0 / 0; PSI-20 0 / 0 / 0 / 163 / 33 / 3; PSI-21 0 / 0 / 0 / 358 / 2 / 3; PSI-22 0 / 0 / 0 / 215 / 0 / 6; PSI-23 0 / 0 / 0 / 285 / 1 / 4; PSI-25 244 / 47 / 5 / 0 / 0 / 0; PSI-26 0 / 0 / 0 / 101 / 13 / 0; PSI-39 101 / 5 / 7 / 16 / 117 / 0; PSI-69 3 / 5 / 1 / 0 / 163 / 11; PSI-101 0 / 0 / 0 / 8 / 0 / 0; PSI-102 0 / 0 / 0 / 0 / 0 / 2; PSI-106 0 / 0 / 0 / 27 / 0 / 1; PSI-107 0 / 0 / 0 / 7 / 12 / 0; PSI-159 314 / 11 / 2 / 10 / 0 / 0.
- `labels_disagree` files: `PSI-25_Raw Data_BASS_GMT50_SAMPLE_148_TEST_B3.mp4` (BASS2-B1, BASS2-B3); `PSI-25_Raw Data_BASS_GMT183_SAMPLE_175_TESTB15.mp4` (BASS2-B15, BASS2-B17); `PSI-25_Raw Data_BASS_GMT183_SAMPLE_175_TESTB15_2ND_VIEW.mp4` (BASS2-B15, BASS2-B17); `PSI-25_Raw Data_BASS_GMT203_SAMPLE_210_TEST_O10_Still_Sequence.mp4` (BASS2-O10); `PSI-25_Raw Data_BASS_GMT203_SAMPLE_210_TEST_O10_2ND_VIEW.mp4` (BASS2-O10); `PSI-39_Raw Data_FLEX-1303_2017-06-29-15h53m44s_F180D04.mp4` (CFI-1290); `PSI-39_Raw Data_FLEX-1303_2017-06-29-15h53m44s_F180D04.ts` (CFI-1290); `PSI-39_Raw Data_vlc-record-2017-07-10-16h15m31s-udp_F191D05.mp4` (CFI-1323, CFI-1328); `PSI-39_Raw Data_vlc-record-2017-07-10-16h15m31s-udp_F191D05.ts` (CFI-1323, CFI-1328); `PSI-39_Raw Data_vlc-record-2017-07-27-16h11m15s-udp_F208D05.mp4` (CFI-1338); `PSI-39_Raw Data_vlc-record-2017-07-27-16h11m15s-udp_F208D05.ts` (CFI-1338); `PSI-39_Raw Data_FLEX-1274_2017-05-31-19h12m06s_F151A05.mp4` (CFI-1225); `PSI-69_Raw Data__ISS_20090625_153031_256R002.mpg` (FLEX-11, FLEX-13); `PSI-159_Raw Data_vlc-record-2021-05-05-16h29m30s-udp____211125A2.ts` (CFIG-N-21125A2); `PSI-159_Raw Data_vlc-record-2021-06-23-14h52m10s-udp____2117A4.ts` (CFIG-N-21174A4).
- Per file against the claimed `video/data/video_links.csv` (compared, not used): same state 2,606 of 2,623; differing by pair: PSI-26: recount id_not_in_table / claimed day_only: 12; PSI-39: recount labels_disagree / claimed day_only: 4; PSI-39: recount labels_disagree / claimed id_not_in_table: 1. The differing files are in the JSON.
- **Why the video fixtures that differ differ** (readings this recount keeps; none was changed to reach a number):
  1. BASS (PSI-26), 12 videos named `20130531 ...` in folder `2012_05_02`: the name date minus one day is 30 May 2013. NASA's BASS table has no row whose `Date` is 5/30/2013; its rows with `GMT` 150 (which is 30 May 2013) write `Date` 6/1/2013. This recount compares with `Date` as written, so they are `id_not_in_table`; the claimed side reaches them through `GMT` (`day_only`, 5 tests). The table's two columns disagree for these rows; the team does not resolve it.
  2. CFI (PSI-39), 5 videos whose name carries a CIR test point that is not a table row while the folder's CIR test point is one (for example name `F180D04`, folder `FLEX-1290 - F177D01`). This recount calls that `labels_disagree` (name and folder name different test points); the claimed side falls back to the day of the name (4 `day_only`, 1 `id_not_in_table`). One more test, CFI-1225, then has a disagreeing video only.
  3. A `labels_disagree` video is counted here for every test that one of its labels names; the claimed side gives each such file one test. Only `_ISS_20090625_153031_256R002.mpg` moves a count: it is counted for FLEX-13 (name) and FLEX-11 (folder), FLEX-11 has no other video and is counted for S1, so S1 has 2 tests with a disagreeing video only, not 1 (and so do the ISS and lunar S1 'outside' rows).
  4. Scope: this recount has no `run` scope; the 3 SAME-R videos whose date and material reach the two runs of one sample are `day` here (the date alone is used). Link states are not affected.

### F. Listing against raw_inventory.json

| Fixture | Expected | Recounted | Match |
|---|---|---|---|
| listing files, bytes against raw_inventory.json | 60,866 / 13,471,850,126,356 | 60,866 / 13,471,850,126,356 | yes |
| listing rows, repeated rows against raw_inventory.json | 66,567 / 5,701 | 66,567 / 5,701 | yes |
| investigations whose listing differs from raw_inventory.json | 0 | 0 | yes |

- Team listing fetched 2026-11-14T05:57:17Z; this recount's listing fetched 2026-11-15T00:12:50Z to 2026-11-15T00:15:00Z. Per investigation, files, bytes, rows, repeated rows, row bytes and records beyond one per key were compared with `raw_inventory.json`; 0 investigations differ (no drift in these figures between the two fetches). Row bytes, repeats included: 13,496,753,397,871 (inventory 13,496,753,397,871).

### O6. Frozen files

| Fixture | Expected | Recounted | Match |
|---|---|---|---|
| frozen files with the sha256 of the check.py snapshot (of 4) | 4 | 4 | yes |

- `tests.csv`: sha256 b8acc1073fbc33a37563eb7f7cd12811e602fb7363ee69982d97860f05522211, equal to the snapshot after reading the working tree's CRLF line ends as LF (Windows checkout with core.autocrlf; the bytes as written on disk give bfbc0e53cc7a...).
- `need_tests.csv`: sha256 8f2cf847728016c6669a95931c89d06286ce7030214cece1d65d66a93d119a77, equal to the snapshot after reading the working tree's CRLF line ends as LF (Windows checkout with core.autocrlf; the bytes as written on disk give 07ca5d97e528...).
- `scenario_needs.csv`: sha256 ad7fcfeba56661d448b8c8bef9fb66667e749d58a2e5d84a450988725e535796, equal to the snapshot after reading the working tree's CRLF line ends as LF (Windows checkout with core.autocrlf; the bytes as written on disk give 7de491c19193...).
- `scenario_tests.csv`: sha256 6581e840553a2d4197d90ecc2ad94b5b307747112f81b4d418a2e357ae45eaab, equal to the snapshot after reading the working tree's CRLF line ends as LF (Windows checkout with core.autocrlf; the bytes as written on disk give af0d83f67b73...).

## Corrections made after the first run

- First offline run (2026-11-15): 59 of 71 fixtures reproduced. Four things were then corrected; in each the code did not do what its own rule, as written in this file and in the design, says. No rule was added or loosened to reach a number, and the fixtures that still differ are explained under E.
- FLEX test points were read in one shape only (`ddd[F|R]ddd`), although the rule ties the name and the folder to the `FLEX Identifier` column, which also holds `ddCALdd` and `[C|H|N]dd[H|M]ddd` identifiers. Now every shape of that column is read. Effect: 5 PSI-69 videos in folders that end with such an identifier (for example `FLEX 116_01_Sep_2010_MeOH_C11M401`) moved from `none` to `one_label`; the figures of block C did not change.
- An ACME or CFI-G test point written with a `_n` suffix was cut to its base, although the CFI-G table lists `21196M2_1` as a test of its own. The suffix is now kept where the table lists the suffixed form. Effect: 1 video moved from test CFIG-I-21196M2 to CFIG-I-21196M2_1 (tests with a two-labels video 462 to 463); no link state and no figure of block C changed.
- Sheet against table: the test time was compared as text, so `05:02:52 (GMT)` and `5:02:52` differed. It is now compared as hours, minutes and seconds. No fixture uses the time.
- The sha256 of the four frozen files was taken of the working-tree bytes, which on this Windows checkout (git `core.autocrlf`) end lines with CRLF. The check now also hashes the bytes with CRLF read as LF, which are the committed bytes, and prints both.

## What this recount does not cover

- Nothing here reads a raw file other than the 272 FLEX test sheets; no archive, video or document was opened.
- Placement uses the table values of `tests.csv` only; no raw value enters any count (as the design requires).
- Link fixtures (C) cover the 26 tests inside the lunar ranges (17 FLEX, 9 CFI-G) only; no link total for other tests or investigations, and no claim that a file which names a test holds what a question needs.
- The ISS screen's link totals, pile 2 reading order (`reading_order.csv`) and the cost ladder (reading steps and their unit costs) are not recounted.
- `question_chain.csv` is not in the repository, so its sums against `need_gap_states.csv` are not checked.
- Video: the scope split of 'day' into a test day, a folder of several days and runs, the BASS-II clip kinds, the ISS P1 shortlist (49 files), the transcriptions (`O9.csv`) and the BASS-II day/sample pairs are not recounted.
- The FLEX sheet comparison says what the sheet and the table write; it does not say which is right, nor what `nan`, `0.00`, a blank or a dash mean.
- No person has checked any figure of this recount.

## Network log totals

This session made no network call. Every call below was made by the first session of this job (the 24 listings, then the 272 FLEX test sheets, two calls each: a signed link from psi.nasa.gov, then the file from PSI's storage host; a fetch it had started was still running when this session began and finished the last sheets). Only FLEX test sheets were downloaded; no other raw file.

All calls of this recount job are in `validation/raw_chain_recount_netlog.jsonl`: 568 calls from 2026-11-15T00:12:50Z to 2026-11-15T00:33:31Z, 31,335,089 bytes received, 2,418 bytes sent, 0 errors; hosts psi-curation-prod.s3.amazonaws.com, psi.nasa.gov.

| Kind | Calls | Bytes received | Bytes sent |
|---|---|---|---|
| listing (POST files/v2) | 24 | 30,609,224 | 2,418 |
| sheet download (GET signed S3 link) | 272 | 250,375 | 0 |
| signed link (GET studies/PSI-69/download) | 272 | 475,490 | 0 |

This run: 0 sheet downloads (offline unless `--fetch`).

Recomputed by a second AI session with code that does not import the pipeline; not checked by a person.
