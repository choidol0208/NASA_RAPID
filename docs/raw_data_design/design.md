# Finding the raw data a question needs, without processing the archive

*AI-generated (Claude Code) on 2026-11-15 for the pm role, from five research sheets, three candidate designs and three reviews of this workflow. Not reviewed by a person. The repository was read only (state `3c2f5c2`). This final step made no request to PSI (0 bytes); it recounted the key figures with its own code from the repository and from the listings the earlier steps saved.*

Working folder: the design job's scratch folder on the pm session's computer (not in the repository). The files a role needs to start from are copied to `docs/raw_data_design/prototype/`: `chain_lunar_habitat.csv` and `chain_proto.py` (the question chain for the lunar habitat), `lunar_summary.json`, `lunar_links*.py` and their JSON results (files tied to the 26 tests inside the lunar ranges), `flex_two_label.py` and `.json` (the two-label check for FLEX). Paths below that start with `rawdesign/` refer to that scratch folder; ask pm for any other file named there.

---

## 1. The answer

**Yes, the problem can be solved, and mostly without AI.** It cannot be solved by analysing 13.47 TB or by having a model label every file. It is solved by going the other way: start from the user's question and follow NASA's own identifiers down to the files.

1. The archive is not unlabelled. NASA wrote test identifiers into file names, PSI folder names and small per-test text files. Nobody has joined them. PSI's own machine-readable description stops at the investigation level: in the three PSI metadata files read (PSI-159, PSI-25, PSI-99) the per-test file is one placeholder row, "Do not use this".
2. Joining them is ordinary code: a join on exact keys, a decision from metadata before any data is read, and a small read of the few kilobytes that matter. These are old methods from database research, statistics and decision theory.
3. Measured on the lunar-habitat example: of 60,866 files, 398 carry the name of one of the 26 tests recorded inside the oxygen and pressure ranges (104.4 GB, 0.77% of the bytes). 316 of them are small files (86.9 MB). The 17 per-test sheets of the counted tests are 15 kB together, and reading them against NASA's table shows what the raw files say where the table cell is empty.
4. In one day the team can ship this for the two demo environments (lunar habitat, ISS): per question, three piles on the page, each number recomputed by a second code path.
5. What stays out of reach in one day: the inside of the 12,689 archives (96.5% of the bytes), the videos, and the 12 investigations whose table has no row per test. The page says so in plain words.

**The design in one sentence.** For a chosen environment and fire-safety question, code places every recorded test (inside the ranges, outside by a recorded value, or cannot be placed from the tables), ties the tests to the PSI files that carry their NASA identifiers, and shows three piles: in NASA's tables; in the archive but unprocessed (which files, how many bytes, how many were opened, what the next read costs); and no record in PSI (with the ground for saying so).

**The pitch sentence** (from the third review): "Say what you are building. We show the 0.77% of NASA's 13.47 TB that names your tests, what 15 kB of it already says, and where no test exists at all."

---

## 2. What this step checked and corrected

All figures below were recomputed in this step with separate code (`final/flex_two_label.py`, `final/lunar_links.py`, `final/lunar_links_159.py`; outputs `final/*.json`) and by direct reads of the repository CSVs.

| Point | Result of the recount | Consequence for the design |
|---|---|---|
| `need_gap_states.csv` per scenario | The 71 rows are identical for all six scenarios. | The per-environment view does not exist yet. Step 2 of the plan adds it. |
| Placement of the 1,824 tests for `lunar_habitat` | inside 26; cannot be placed 676 (672 with neither oxygen nor pressure in a table, 4 with pressure only); oxygen of an oxidizer stream 63; outside by a recorded value 1,059. Solid fuels (376): outside 139, cannot be placed 237, inside 0. | Confirms design 1's bar. `mars_habitat` sets no range (`not_specified` for all 1,824), so a fifth state "no range set" is needed. |
| Files that name the 26 tests inside the lunar ranges | 398 files, 104,358,456,350 bytes (0.7746% of 13,471,850,126,356). PSI-69: 299 files, 24,954,842,492 bytes for 17 tests. PSI-159: 99 files, 79,403,613,858 bytes for 9 tests. | The figure holds. It is a count by file name. |
| Second label for those 398 links (PSI folder) | 336 files sit in a folder that names the same test. 47 FLEX image archives sit in a fuel-level folder that names no test. 15 files of FLEX-20 sit in a folder named after FLEX-21 (`FLEX_021_24_Oct_2009_MeOH_192F002`). | Publish the three numbers next to the count. Do not resolve the FLEX-20 case. |
| "Small files" | Two definitions were in use. Not an archive or a `.ts` recording: 316 files, 86,853,632 bytes. At most 10 MB: 315 files, 72,561,596 bytes. | Use the first everywhere and name it: "files that are not an image archive or a video recording". |
| FLEX numbering | The table numbers its rows 1 to 274 (`FLEX Test #`). File names carry `FLEX-001` to `FLEX-280` (272 test sheets; six numbers, 275 to 280, are above the table). Identifier `193F001` is on two table rows (70 and 73). In about half of the PSI folders that carry both a number and identifier-named files, the two point to different rows (115 of 248 here; 114 of 248 and 109 of 242 in the two earlier counts, with slightly different matching). `retrieval_queue.csv` rows 87 to 90 give three cases where the number in a name is 6 above the table row. | The number in a FLEX file name is a different numbering from the table's and must never be the join key on its own. The identifier alone is not always unique. A link needs two labels. The census of the test sheets (step 4) yields the crosswalk number to identifier, written by NASA. |
| Extinction diameter for the 17 lunar tests | The table cell is a number above zero for 4 tests, `0` for 2, blank for 8 and an en dash for 3. The table (274 rows) has 189 numbers, 8 zeros, 49 blanks and 28 en dashes; `tests.csv` turns blank and dash both into empty. | Show every code as written. See section 7 for the full cross-table. Earlier wording "a number for 4 more tests" was wrong: it counted a `0.00`. |
| Summary PDFs of the 11 tests without a number in the table | 11 PDFs for 10 tests (FLEX-22 has two, FLEX-24 has none). | Corrects "11 PDFs of 11 tests". The PDFs become a second, unread source; the test sheets are read first. |
| Counted tests | P1 133 (oxygen 13.6 to 22.2%), P3 2 (21.5 to 21.7%), D1 122 (13.6 to 22.2%), S1 298, P2 0, D2 0. No counted solid-fuel test has a pressure in a table. | Unchanged. No step of this design changes them. |

---

## 3. The design

### 3.1 The chain

Five links. Each is a join over files that exist or that the plan writes. None needs a model.

1. **Question to quantities.** `pipeline/spec/needs.json` already lists, per question, the required conditions, the useful conditions and the outcomes, each with its NASA or ISO reference item.
2. **Test to environment (new).** One placement per scenario and test, from `scenario_tests.csv`:
   - `inside`: oxygen and pressure both recorded inside the ranges;
   - `outside_by_recorded_value`: oxygen or pressure recorded outside;
   - `oxygen_of_oxidizer_stream`: oxygen is that of an oxidizer stream, not of the atmosphere;
   - `cannot_be_placed_from_table`: oxygen or pressure is not in the table and neither is recorded outside (a second column keeps the pair, so the page can say "oxygen inside, pressure not in the table");
   - `no_range_set`: the scenario sets no range.
3. **Quantity to location.** Where a needed value of a test is, from `gap_states.csv`, `raw_columns.json`, `raw_values.csv` and `video/`:
   - `table_cell`;
   - `raw_file_value_read` (read from the test's own file, compared with the table, not adopted);
   - `raw_file_column_seen` (a header seen in n of N opened files of the group; values not read);
   - `video_on_screen_text` (the 19 BASS-II clips);
   - `document_sentence`;
   - `not_found_in_files_opened`.
4. **Test to files.** A file is tied to a test by labels NASA wrote: the number in the name, the NASA identifier in the name, the PSI folder label, and the identifier printed inside the file where it was read. Link states: `two_labels_agree`, `one_label`, `labels_disagree`, `id_not_in_table`, `day_only`, `none`. Disagreements are listed, never resolved by the team.
5. **Files to cost.** Bytes from the listing, and a reading step from a closed list with its measured unit cost (section 9): listing only; small file read whole; head by range request; zip directory by range request; PDF text; on-screen video text; blocked (no text layer, over the size limit, download failed).

### 3.2 The three piles

Per scenario and question:

- **Pile 1, "In NASA's tables".** The tests placed inside, with their fuel phase, gravity and pressure beside the number, and for each quantity the question needs, how many of them have a table value.
- **Pile 2, "In the archive, not in a table".** Two kinds of rows, ordered by the rule in 3.3:
  - a quantity that the tests inside lack in the table, with its location, file group, files, bytes, "n of N files opened", and what was read;
  - tests that cannot be placed because the tables lack their oxygen or pressure, with the file groups where a column for it was seen, if any.
  A lower shelf holds "not found in the files opened", with the number of unopened files.
- **Pile 3, "No record in PSI (listing of 14 November 2026)".** Allowed on three grounds only, each printed with its source:
  1. a constant of every per-test table (gravity: every test is recorded in microgravity);
  2. every counted test of the question has a recorded value outside the range (P1: oxygen 13.6 to 22.2% against 30% or more);
  3. a NASA sentence about a whole investigation (BASS-II: "Pressure was not varied from 1 atmosphere.").
  Anything else belongs in pile 2.

One fixed sentence separates the two kinds of gap wherever ground 2 applies: "This gap is a missing test, not unprocessed data: every counted test of this question has its oxygen in NASA's table, and reading raw files cannot move one in."

### 3.3 The order of pile 2

A fixed rule, printed with the list as "the team's ordering, not a NASA priority; it does not say the value is there":

1. file groups in which a column for oxygen or pressure was seen for tests that cannot be placed;
2. file groups that could add a counted test (an outcome for a test inside that has none);
3. file groups that could add a value to a test already counted inside.

Within a class: more target tests first, then fewer bytes. Target tests are sets, so a test is counted once; the bytes of a group are counted once. The evidence is printed in words ("value read for k tests", "header seen in 1 of N files", "not opened"). No probability, no expected gain and no interval appears on the page.

### 3.4 One "read it and it answered" example

The 272 FLEX per-test sheets (`FLEX-nnn_TestSheet.txt`, 250,375 bytes in the listing) are read in full by code. Each sheet holds `key = value` lines (`CIR Test Number`, `Pressure (atm)`, `O2 Mole Fraction`, `D0 (mm)`, `kavg (mm2/s)`, `Dext (mm)`) and a comment paragraph by the investigators. The sheet is tied to a table row by the identifier printed inside it together with a second field (date or oxygen and pressure), and each field is compared with the table row. This is a census, not a sample, so no interval is needed. It gives, per test, what the raw sheet writes where the table cell is blank or a dash, and it gives the crosswalk between the two FLEX numberings.

### 3.5 What is deliberately not built

Taken from the three reviews:

- no index or card for all 60,866 files, no search panel with tabs, no rules for the 18 investigations that have none;
- no run over all 12,689 archive directories, no parallel range requests, no read of the 49 MB BASS-II Summary Report;
- no new video work (mp4 indexes, key frames, `.ts` probes), no flame or ignition signal from pictures;
- no model labelling on the critical path (name legends, comment tags);
- no probabilities, expected gains or intervals from one hand-picked file on the page;
- no tier badges (T0 to T4) on the page; "n of N opened" in words instead;
- no value from a raw file in `tests.csv` or in any count.

---

## 4. What each field of knowledge does here

| Field | What it does in this design |
|---|---|
| Database research | Builds the catalogue after the fact from name patterns (Goods); ties files to table rows on exact keys with two agreeing labels (record linkage); decides from metadata whether a file can matter before reading it (data skipping); reads a file's head or a zip's directory by HTTP Range request. |
| Information retrieval | Looks a quantity up by the header text as NASA wrote it (exact tokens, the team's `variables.json` as the vocabulary). No embeddings and no relevance ranking by a model. A search box over files is not built. |
| Statistics and sampling | Prints "n of N files opened" beside every raw-file statement; reads a whole group where it is small (272 sheets, 250 kB) instead of sampling; gives a person's spot check an exact bound (0 wrong in 30 means fewer than 9.5% wrong at 95%; 0 in 60 means fewer than 4.9%). An interval is given only for a seeded random sample. |
| Decision theory | Orders what to read next by what a read could change against what it costs (value of information), as a fixed published rule over sets of tests and bytes. No probabilities. |
| Computer vision | Kept to transcription: NASA's on-screen numbers in the 19 BASS-II clips are the deepest and dearest reading step and appear as one location, "on-screen text". No flame state from pictures; the team's own picture signal was right in at most 1 of 19 clips. |
| Checked language-model labelling | Not on today's path. The header readings the data role already made with AI stay labelled as such and are replaced by a value check where the test's own file was read. Any later model label must copy a NASA string and pass a code gate. |
| Combustion science | Says what each question needs (conditions and outcomes with reference items), converts units as written (atm, mmHg, psia, mole fraction), and sets the caveats: a droplet is not a solid material, microgravity is not lunar gravity, a cabin reading is not the test's condition, and what `nan`, `0.00`, blank and a dash mean for an extinction diameter is not stated in what was read. |
| Library and archive practice | Supplies the frame (FAIR, NASA SPD-41a, ISA-Tab) and the finding that PSI's per-test metadata layer is empty in the three files read; keeps provenance on every row (file, bytes read, who read it, who checked it); publishes the remainder lists; marks the team's links as a team description, not NASA's record. |

---

## 5. Where AI is and is not used

**No AI** in what answers the question: the placement of tests, the chain, the file links, the three piles, the order, the parsing of the test sheets, the comparison with the table, and every sentence on the page (fixed templates filled with counts). Nothing is generated when a page loads.

**AI is used in two places, both already disclosed:**

1. *AI coding sessions write the code.* Check: every output is recomputed by a second session with separate code (step 7), against the fixtures in section 10; the existing check O6 proves that `tests.csv`, `need_tests.csv`, `scenario_needs.csv` and `scenario_tests.csv` are byte-identical.
2. *Header readings in `raw_columns.json`* (made earlier by the data role: an AI read a header and proposed which variable it is). Check already done: an independent re-read removed 58 of 97 proposals in round 1 and accepted 19 of 68 in round 2. New check: where the test's own file is read (FLEX sheets), the values are compared with the table row by code, and the row says `raw_file_value_read` instead of `raw_file_column_seen`. Every remaining AI-read row keeps the label "AI reading of the header, re-read by the data role" and "n of N files opened".

**Not used:** a model that maps a header to a standard variable for the page, judges a flame from a picture, ranks relevance, or guesses what an identifier code means.

**Labels on the page.** "Recomputed by a second AI session" for what a session checked. "Read by a team member" only for rows a person read.

---

## 6. Build plan for the day

Four lanes run in parallel. Total about 16 session-hours; the longest lane (data) is 6 hours. The ui role starts step 8 against the prototype files while data writes step 2.

| # | Step | Role | Hours | Output | Check | Lead decides first |
|---|---|---|---|---|---|---|
| 1 | Fix the three page errors of request `20261114-2340` (frame cut at decimal points; the "not in the archive" list for four inputs only; the "4 of 6" line) | ui | 1.0 | `web/app.js`, live page | The check that lead plus rest equals the frame text; both demo queries opened on the public page | no |
| 2 | Question chain with placement per test and environment | data | 2.5 | `data/pipeline/question_chain.csv`, written by `pipeline/raw_gaps.py`: scenario, need, role, variable, investigation, placement, placement pair, location, column kind, difference codes, file groups, files, bytes, files opened n of N, tests in scope, counted tests, pile, pile-3 ground | New check in `check.py`: rows of each scenario, need and variable sum to the tests in scope (376 or 1,824); summed over placement they equal `need_gap_states.csv`; `inside` equals `scenario_needs.csv`; fixtures of section 10; O6 unchanged | no |
| 3 | File links for the demo investigations with the two-label rule (**the data role's name classification, already in progress, is the base**) | data | 1.5 | `data/pipeline/file_links.csv` (PSI-69, PSI-159, PSI-10, PSI-25, PSI-99; one row per file: file id, name, bytes, kind, name group, labels found, link state, test, rule id), `file_links_summary.json`, `test_files.json` (tests inside a scenario to their files), `listing_snapshot.json` (per investigation: listing date, rows, bytes, sha256 of the saved listing, because `data/psi/file_listings/` is not in the repository) | Files and bytes per investigation equal `raw_inventory.json`; lunar fixture: 398 files, 104,358,456,350 bytes, 336 / 47 / 15 by second label; FLEX is never linked by the name number alone; conflicts listed | no |
| 4 | Census of the 272 FLEX test sheets | data | 1.5 | Rows in `data/pipeline/raw_values.csv` (test, file id, key, value and unit as written, table value as written, agreement class), a block `flex_test_sheets` in `raw_values_effect.json` with the cross-table and the number crosswalk; state "read from NASA's file, not adopted" | The 17-test fixture of section 7; every field compared with the table; `nan`, `0.00`, blank and dash kept as written; O6 unchanged; counts stay 133, 0, 2, 298, 122, 0 | reading: no; showing on the page: decision 2 |
| 5 | Read the BASS as-run workbook (`As Run_Test Matrix.xlsx`, 111,886 bytes) | data | 0.5 | Rows in `raw_values.csv` for 121 runs with the codes `location_not_stated` and `magnitude_not_as_unit_written`; the written range of the two columns in `raw_values_effect.json` | Row count equals the 121 table tests; nothing adopted; no test placed | decision 4 |
| 6 | Order of pile 2 (rule of 3.3) | catalog | 1.5 | `data/catalog/reading_order.csv` per scenario and need: order, class, investigation, file group, files, bytes, target tests, evidence in words | Deterministic; sets counted once; bytes once per group; for S1 at the ISS the only group in class 2 is the BASS-II Summary Report (up to 44 tests) | decision 3 |
| 7 | Independent recount with separate code | catalog | 1.5 | `validation/raw_chain_recount.py` and its report: chain sums, link fixtures, sheet-against-table agreement | Must reproduce sections 7 and 10 without importing the pipeline | no |
| 8 | Page: header line; one bar per question; three piles as plain lists; the two-kinds-of-gap sentence; per test inside the ranges a file list with "Download file list (CSV)" | ui | 3.0 | `web/build.py` copies the chain into `web/dist/data/chain/<scenario>__<need>.json` and the file lists into `files/<scenario>.json`; blocks inside `renderNeeds` and `renderTests` in `web/app.js` | Build fails when a number on the page differs from its CSV cell; bar segments sum to the tests in scope; every place that shows "17" shows liquid droplets, microgravity and 71 to 72 kPa beside it; banned-word scan (safe, unsafe, will, predict, likely); phone width | decisions 1, 2, 5 |
| 9 | Wording and claims | pm | 1.5 | Pile-3 templates with ground and source (request to data for `pipeline/spec/answers.json`); README section "What the three piles claim"; one slide (archive breakdown and the lunar funnel); rows in `compliance/SOURCES.md` and `compliance/AI_USAGE_LOG.md` | Every slide number read from a data file by a second session; wording compared with section 8 | decision 1 |
| 10 | Read all 24 PSI metadata zips (302,059 bytes) | pm | 0.5 | `reports/isa_metadata_fields.csv`: per investigation, which ISA-Tab fields are filled, and the study file as written | A second session re-reads five | decision 8 |
| 11 | Spot check and final read | pm with one team member | 1.0 | `reports/spot_check_raw.csv` with reviewer kind; the label on the page | 30 seeded-random links opened on the PSI page and every pile-3 sentence of the two demo environments read; the bound printed (0 wrong in 30: fewer than 9.5%) | decision 6 |
| 12 | Optional: directories of the 47 FLEX archives of the 17 lunar tests (about 6 MB, 2 minutes; **the data role is already testing these range reads**) | data | 0.5 | `data/pipeline/archive_members.csv`: members, kinds, first and last inner name, bytes read | Members parsed equal the count in the end record; total transfer logged | no |

**Already in progress on the data role's side** (per `coord/status/data.md`, not yet in the repository): the classification of every raw file by name group and test identifier; what NASA's documents say the name codes mean; the test of zip directories by range request; the survey of the 2,623 video names. Steps 3 and 12 build on them and should take over their output rather than repeat it.

**Order.** ui: 1, then 8 on the prototype (`chain/out/chain_lunar_habitat.csv`, `final/lunar_links_PSI-69.json`, `final/lunar_links_PSI-159.json`, `tiers/testsheets_vs_table.json`), then switch to the pipeline files. data: 2, 4, 3, 5, then 12. catalog: 6, 7. pm: 9, 10, 11.

**PSI traffic of the plan.** Step 4: 250 kB plus 272 signing calls. Step 5: 112 kB. Step 10: 0.3 MB. Step 12: about 6 MB. All sequential, all logged. Under 10 MB in total.

### Smallest version that still matters (about 6.5 hours)

1. ui, 1.0 h: step 1.
2. data, 2.0 h: `question_chain.csv` for all scenarios (the prototype already writes 561 rows for the lunar habitat).
3. data, 0.5 h: the 17 lunar test sheets re-read by the pipeline (15,369 bytes) and written as "read, not adopted" with the cross-table of section 7.
4. data, 0.5 h: file lists for the 26 lunar tests from the saved listing (PSI-69 and PSI-159 only), with the second-label counts.
5. ui, 2.0 h: the header line, the bar and the three piles as plain lists in each question block for the lunar habitat and the ISS; no click-through list.
6. pm, 0.5 h: pile-3 wording with grounds, and the claim lists in the README.

Even this version takes a lunar user from 13.47 TB to 398 files, shows what 15 kB of NASA's own sheets say where the table is empty, and separates "no test" from "tested, value unread". Dropped: the census of all 272 sheets, the BASS workbook, the reading order, the file download, the ISA census and the person's spot check (so the page must say "recomputed by a second AI session; not read by a person").

---

## 7. The lunar-habitat screen

Expected texts. Numbers in angle brackets come from the build.

**Header line, under the environment title.**
"Lunar base or pressurized rover: oxygen 30 to 36%, pressure up to 85.8 kPa, lunar gravity. NASA's PSI archive lists 60,866 files (13.47 TB) for 24 combustion investigations. 398 of them (104.4 GB, 0.77% of the bytes) carry in their name the NASA identifier of one of the 26 tests recorded inside these oxygen and pressure ranges: 316 files that are not an image archive or a video recording (86.9 MB) and 82 image archives and video recordings (104.3 GB). File name and PSI folder agree for 336; 47 archives sit in a folder that names no test; 15 files of FLEX-20 sit in a folder named after FLEX-21. The 26 tests are 17 fuel-droplet tests and 9 gas flames, all in microgravity. A file that names a test is not shown to hold what a question needs."

**One bar per question.** Extinction conditions (S1), 1,824 tests of all fuel phases: inside 26 | cannot be placed from the tables 676 | oxygen recorded for the oxidizer stream 63 | outside by a recorded value 1,059. Each of the five solid-fuel questions (P1, P2, P3, D1, D2), 376 tests: inside 0 | cannot be placed 237 | outside by a recorded oxygen value 139.

**S1, pile 1, "In NASA's tables".**
"17 tests counted for this question: FLEX (PSI-69) fuel-droplet tests, liquid heptane or methanol, microgravity, oxygen 30% or 34%, 71.2 to 72.4 kPa (1 to 2 kPa above 10.2 psi). Recorded for them: how the burn ended 17 of 17 (15 disruption, 2 completion); burn time 16; flow speed 0. Extinction diameter as the table writes it: a number above zero for 4, `0` for 2, blank for 8, a dash for 3. 9 more tests inside the ranges are CFI-G gas flames (PSI-159, 50.7 kPa, 33 to 36% oxygen); their investigation does not state this purpose, so they are not counted."

**S1, pile 2, "In the archive, not in a table"**, with the label "Order: the team's rule, not a NASA priority. It says where to read first, not that the value is there."

- "Per-test sheets of these 17 tests (`FLEX-nnn_TestSheet.txt`, 17 files, 15,369 bytes; 17 of 17 read). The identifier printed inside equals the table's in 17 of 17. Pressure agrees within rounding in 16 of 17 (FLEX-23: sheet 0.70 atm, table 541.8 mmHg). Oxygen agrees in 16 of 17 (FLEX-28: sheet 0.29, table 0.3). Line `Dext (mm)` against the table cell, both as written:"

  | Table cell | Sheet line `Dext (mm)` | Tests |
  |---|---|---|
  | number above zero | the same number | FLEX-21 (0.95), FLEX-25 (0.59), FLEX-26 (0.4) |
  | number above zero | `nan` | FLEX-20 (table 1.56) |
  | `0` | `0.00` | FLEX-39, FLEX-43 |
  | blank | a number | FLEX-23 (1.32), FLEX-38 (1.88) |
  | blank | `nan` | FLEX-19, 22, 24, 27, 28, 37 |
  | dash | a number | FLEX-40 (1.77) |
  | dash | `0.00` | FLEX-41 |
  | dash | `nan` | FLEX-42 |

  "Read from NASA's raw files by the team's code. Not a table value, not counted. No file opened so far says what `nan`, `0.00`, a blank or a dash mean, or whether the sheet's line is the visible-flame extinction diameter of the table."
- "Flow speed: missing for all 17; nothing opened holds it. Smallest unopened document: `FLEX_Test_Plan.pdf`, 1 file, 185,799 bytes."
- "One-page summary PDFs: 11 files for 10 of the 11 tests without a number in the table (FLEX-22 has two, FLEX-24 has none), 2.45 MB. A header `Dext =` was seen in one opened file of this group. Not read."
- "One step deeper: directories of the 47 image archives of these tests, about 6 MB and 2 minutes (from three read: 886 tif, 852 tif and 122 bmp frames for FLEX-19, 370,662 bytes). It adds frame counts. It adds no value and no test. Reading the frames themselves: 24.92 GB; no reader exists; not planned."
- Lower shelf, "Not found in the files opened": "676 tests cannot be placed: 435 SPICE (PSI-107), 121 BASS (PSI-26), 109 SAME-R (PSI-101) and 11 others. For the 121 BASS tests a workbook has an oxygen and a pressure column under a cabin label (1 file, 111,886 bytes); whether that is the test's value is not stated."

**S1, pile 3, "No record in PSI (listing of 14 November 2026)".**
"Lunar gravity: 0 of 1,824 tests. Ground: every per-test table records microgravity; the challenge statement says PSI holds no partial-gravity combustion data yet."

**P1 (flammability limit).** Pile 1: "0 tests inside." Pile 3: "This gap is a missing test, not unprocessed data. All 133 counted tests (125 BASS-II, 8 Saffire-II) have their oxygen in NASA's table, between 13.6% and 22.2%, below this environment's 30%. Reading raw files cannot move one in. Lunar gravity: 0 tests." Pile 2: "237 solid-fuel tests cannot be placed: the tables hold neither their oxygen nor their pressure. 121 BASS tests: columns under a cabin label in one workbook (111,886 bytes), not adopted; none of them has an outcome in the table. 3 Saffire tests: oxygen and pressure series in sensor workbooks, no reading marked as the test's. 113 SAME and SAME-R tests: not found in the files opened."

**P3, D1.** The same placement and the same two-kinds-of-gap sentence (P3: 2 counted tests at 21.5 to 21.7% oxygen; D1: 122 at 13.6 to 22.2%).

**P2 (ignition).** "No counted test in any environment. No table and no opened file records an ignition outcome for any of the 376 solid-fuel tests. The BASS-II Summary Report (1 PDF, 48,972,416 bytes) was not opened."

**D2 (smoke).** "No counted test. Particle size for 108 SAME-R tests was read from a results workbook: three statistics, one without a unit; the two workbooks disagree for all 15 tests both hold. Read, not adopted. None of these tests can be placed in this environment."

**File list on clicking a test**, example FLEX-19: "17 files, 1.11 GB: 14 small files (1.24 MB) and 3 image archives (1.11 GB)." One row per file with name, bytes, link state and what was read: the test sheet (882 bytes, read: pressure 0.71 atm, oxygen 0.34, D0 3.39 mm, kavg 0.90 mm2/s, Dext nan); the test point log (11,919 bytes); chamber readings (281,757 bytes); radiometer readings (202,235 bytes); the summary PDF (128,893 bytes, not read); `196F001A.zip` (952,278,112 bytes, 886 tif), `196F001B.zip` (109,527,990 bytes, 852 tif), `196F001D.zip` (49,350,559 bytes, 122 bmp). Button: "Download file list (CSV)".

**Small print under the panel.** "Built by code from PSI's file listing of 14 November 2026 and the team's tables. A column 'seen' was read in one opened file of its group by an AI and re-read by the data role; it is not a measurement of the test. No value from a raw file has entered the counts. Recomputed by a second AI session; <read by a team member: n rows>. This panel gives no safety judgement and predicts nothing."

**For the ISS** the same blocks are filled by the build. Known from the files today: 179 tests inside the ranges (PSI-10 71, PSI-69 56, PSI-159 27, PSI-39 25); S1 counts 56 of them, all FLEX droplets; of the 376 solid-fuel tests none is inside, 61 have oxygen inside and no pressure in a table, 237 have neither in a table and 78 are outside by a recorded oxygen value; the only file group that could add a counted S1 test is the BASS-II Summary Report (up to 44 tests; not opened).

---

## 8. Claims

### May be claimed (after the named step passes its check)

1. For a chosen question and environment the page lists the PSI files that carry the names of the tests recorded inside that environment, with sizes and what was read. Lunar habitat: 398 of 60,866 files, 104.4 GB of 13.47 TB (0.77%), 86.9 MB of it in files that are not archives or video.
2. The page separates three situations that used to read as one gap: no test recorded at the condition; a test recorded whose value sits in a raw file, a document or on a video picture; a test recorded with nothing found in the files opened.
3. For the lunar habitat: none of the 139 solid-fuel tests with a recorded oxygen value is at 30% or above (13.6 to 22.2%); 237 more cannot be placed from the tables; no test in the per-test tables is recorded at lunar gravity.
4. For the 17 counted lunar tests NASA's per-test sheets were read (15 kB): the identifier inside equals the table's in 17 of 17; where the table has no number for the extinction diameter (11 tests), the sheet writes a number for 3, `0.00` for 1 and `nan` for 7; where both write a value they are the same in 5 of 6. Stated as what the files say, read by the team, not adopted.
5. The chain is deterministic code over PSI's public listing and the team's tables. Only transfers that were run and logged are quoted: the design work used about 27.9 MB in total, including five listings, 18 archive directories read without download (8 kB to 32.9 GB each) and 17 test sheets.
6. The order of what to read first is a published rule over counts and bytes, with the evidence for each row in words.
7. In the three PSI metadata files that were read (PSI-159, PSI-25, PSI-99) the per-test file is a placeholder row. After step 10: the figure for all 24.
8. AI sessions wrote the code and earlier read file headers; what a second session recomputed and what a person read is labelled as such, with the bound from the sample size.

### May not be claimed

1. That the archive was analysed, labelled or indexed as a whole. Link rules exist for six investigations; the inside of 12,689 archives was read for 18; no video content was analysed beyond 19 clips.
2. That a file which names a test holds the quantity a question needs, or that all files of a group share the header seen in the one file opened.
3. That any value read from a raw file is the test's result or NASA's table value. Counts stay P1 133, P2 0, P3 2, S1 298, D1 122, D2 0.
4. That `nan`, `0.00`, a blank or a dash mean "no extinction" or "not measured". No file read says which.
5. That the BASS as-run workbook places 121 tests. It holds cabin-block columns whose location is not stated.
6. That "not found in the files opened" means absent from the archive, or that pile 3 means NASA never ran such a test or should run one.
7. That the reading order is NASA's priority or that the next read will yield the value.
8. That the 17 droplet tests cover a lunar habitat. They are liquid droplets in microgravity at 71.2 to 72.4 kPa; the wording of 14 November 14:15 stays.
9. Any link total built on the FLEX name number alone (5,075 FLEX files; 12,992 of 15,263 files in six investigations). Those figures need the two-label rule first.
10. That the team's links are NASA metadata, or that a person checked what an AI session checked.
11. Any safety verdict, limit or prediction for an untested condition.

---

## 9. Measurements the design rests on

| What | Value | Source |
|---|---|---|
| Archive | 60,866 files, 13,471,850,126,356 bytes, 24 investigations; listing fetched 2026-11-14T05:57:17Z | `data/pipeline/raw_inventory.json` `_meta` |
| Archives (.zip) | 12,689 files, 12,999,389,379,194 bytes (96.49%) | same |
| Archives whose name does not state the content | 10,501 files, 11,831,316,797,688 bytes (87.82%) | sheet "archive-and-raw-layer" (`analyze.py`) |
| Experimental tables | 22 files, 211,116 bytes (0.0016%) | `raw_inventory.json` |
| Missing (test, variable) cells by state | 41,024 cells: not found 94.13%, raw column 5.56%, document only 0.31% | `data/pipeline/gap_states.csv` |
| Tests inside the lunar ranges | 26 (17 PSI-69 liquid, 9 PSI-159 gas); S1 counts 17 | `scenario_tests.csv`, `need_tests.csv` (this step) |
| Files naming those 26 tests | 398 files, 104,358,456,350 bytes; 316 small (86,853,632 bytes); 82 archives and recordings (104,271,602,718 bytes) | `final/lunar_links_PSI-69.json`, `final/lunar_links_PSI-159.json` |
| Second label for those links | 336 folder agrees; 47 folder names no test; 15 folder names another test | same |
| FLEX test sheets | 272 files, 250,375 bytes; the 17 lunar sheets 15,369 bytes (11,871 read) | `final/flex_two_label.json`, `tiers/testsheets_read.json` |
| Sheet against table, 17 lunar tests | identifier 17 of 17; pressure 16 of 17; oxygen 16 of 17; extinction diameter cross-table of section 7 | `tiers/testsheets_vs_table.json` (re-tabulated in this step) |
| FLEX table, extinction diameter column | 189 numbers, 8 zeros, 49 blanks, 28 en dashes (274 rows) | `data/psi/experimental_tables/PSI-69_Experimental table_FLEX.csv` |
| Zip directory by range request | 18 of 18 distinct archives, 8 kB to 32.9 GB, one zip64; 14 of them: 2,887,213 bytes requested for 45.7 GB, mean 2.25 s | `out/zipdirs.json`, `net/zipdir_TPM7.json`, `tiers/zip_lunar_FLEX19.json` |
| Listing cost | 5 listings, 5.55 MB for 11,618 rows (478 bytes a row) | `net/transfer_log.jsonl` |
| AI header readings kept | round 1: 41 of 97; round 2: 19 of 68 | `pipeline/spec/raw_columns.json` `_meta` |
| PSI traffic of the whole design work | about 27.9 MB of 60 MB: 12,321,565 + 2,714,901 + 873,259 + about 1,986,000 + 395,315 + 9,565,376 bytes; this step 0. One read (an mp4 index, 1,413,824 bytes) was larger than "a few hundred kilobytes". | `net/`, `tiers/` and `files_angle/transfer_log.jsonl`; the sheets' own totals |

---

## 10. Fixtures for the checks

A second code path must reproduce these.

- `lunar_habitat`, all 1,824 tests: inside 26, cannot be placed 676, oxidizer stream 63, outside 1,059. Solid: 0, 237, 139. `iss`: inside 179, cannot be placed 739, oxidizer stream 106, outside 800. `mars_habitat`: no range set for 1,824.
- Summed over placement, `question_chain.csv` equals `need_gap_states.csv` (for example P1 pressure: raw column 134, document only 129, not found 113).
- Files naming the 17 lunar FLEX tests: 299 files, 24,954,842,492 bytes; 47 zip (24,923,186,032 bytes); 252 others (31,656,460 bytes); by extension .txt 212, .zip 47, .pdf 23, .rtf 17. The nine CFI-G tests: 99 files, 79,403,613,858 bytes; 35 zip or ts.
- FLEX: `193F001` on rows 70 and 73; six test sheets numbered above 274; FLEX-19 has 17 files and 1,112,400,426 bytes.
- The cross-table of section 7 for the 17 sheets.
- sha256 of `tests.csv`, `need_tests.csv`, `scenario_needs.csv`, `scenario_tests.csv` unchanged (check O6).

---

## 11. Decisions only the team lead can take

1. **Wording of pile 3.** May the page say "No record in PSI (listing of 14 November 2026)" on the three grounds of 3.2 and nothing wider? *Recommendation: yes. Never "NASA did not test this" or "a new test is needed".*
2. **Raw values on the page.** May values read from NASA's raw files (the FLEX test sheets) be shown as "read from NASA's file, not adopted, not counted", every code as written? *Recommendation: yes. It is the one place where the page shows that reading a few kilobytes answers something. Nothing enters `tests.csv`.*
3. **Order rule for pile 2.** Is the fixed rule of 3.3 the team's rule, shown without probabilities? *Recommendation: yes.*
4. **The BASS as-run workbook.** Read it today and show its two columns only as "cabin label, location not stated; not used to place a test"? *Recommendation: yes to reading and to that wording; no to any count of tests that "would be inside". Placing a test stays your decision, and today the answer should be no.*
5. **The ui role's order of work.** The three page errors first, then this panel, and nothing else (no tab panel, no index of all files)? *Recommendation: yes.*
6. **Who checks.** Can one team member spend about 30 minutes on 30 random links and the pile-3 sentences of the two demo environments? *Recommendation: yes, after step 8. If nobody can, the page says "recomputed by a second AI session; not read by a person".*
7. **Video today.** Does any new video reading go on today's path? *Recommendation: no. The page keeps the 19 clips as the deepest reading step, "on-screen text", and the slide shows the measured ladder (name; index for about 1% of a clip's bytes; key frames for 2 to 6%; every second for 19 clips, 1.80 GB). Decide on more only with pm's separate video design in hand.*
8. **The 24 metadata files.** Should pm open all 24 PSI metadata zips (0.3 MB, 30 minutes) so the slide can say how many have an empty per-test layer? *Recommendation: yes; otherwise the sentence stays "in the three files read".*
9. **Scope of the full panel.** Lunar habitat and ISS with all blocks; the other four environments with the bar only? *Recommendation: yes.*

---

## 12. Risks

1. **A wrong link shown with authority.** The FLEX numbering shows how easily it happens. Guard: two labels before a link is called confirmed; the three second-label numbers printed with the count; disagreements listed; the person's sample with its bound.
2. **Pile 2 read as "the data is there".** Guard: "n of N opened" and "values not read" on every row; raw values only as "read, not adopted"; codes as written.
3. **The ui lane.** It carries the three open fixes and the panel. Guard: plain lists, no new components, start on the prototype now.
4. **The 17 droplet tests read as coverage.** Guard: fuel phase, gravity and pressure beside the number, and the solid-fuel line with equal weight.
5. **Reproducibility from the public repository.** The listings are not committed. Guard: commit the derived link file for the demo investigations and `listing_snapshot.json`.

---

## 13. Sources

**Methods.** Opened by the research steps of this workflow; this step re-checked the quoted words in the saved copies where a file is named, and opened nothing new.

- Halevy et al., "Goods: Organizing Google's Datasets", SIGMOD 2016. https://research.google/pubs/goods-organizing-googles-datasets/ (saved text `lit_cs/goods.txt`; "over 26 billion datasets" found).
- Binette and Steorts, "(Almost) All of Entity Resolution". https://arxiv.org/abs/2008.04443 (abstract opened by the research sheet).
- Koutras et al., "Valentine: Evaluating Matching Techniques for Dataset Discovery", ICDE 2021. https://arxiv.org/abs/2010.07386 (`lit_cs/valentine.txt`; "One size does not fit all" found).
- Abedjan, Golab, Naumann, "Profiling relational data: a survey", VLDB Journal 2015. https://dspace.mit.edu/handle/1721.1/106176 (abstract).
- Parquet page index. https://parquet.apache.org/docs/file-format/pageindex/ ; PKWARE APPNOTE. https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT ; HTTP Range requests (MDN). https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Range_requests ; RFC 9110 section 14.1.2. https://www.rfc-editor.org/rfc/rfc9110.html
- Leskovec et al., "Cost-effective Outbreak Detection in Networks", KDD 2007. https://www.cs.cmu.edu/~jure/pubs/detect-kdd07.pdf (`celf.txt`; "arbitrarily worse than the optimal solution" found).
- Settles, "Active Learning Literature Survey", 2010. https://burrsettles.com/pub/settles.activelearning.pdf (`settles.txt`).
- Sahigara et al., Molecules 17(5):4791, 2012, doi 10.3390/molecules17054791. https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6268288/fullTextXML (`sahigara.xml`; "defined domain of applicability" found).
- Binomial intervals and the rule of three. https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval ; https://en.wikipedia.org/wiki/Rule_of_three_(statistics) (the primary papers were not opened).
- Sawadogo and Darmont, "On data lake architectures and metadata management", 2021. https://ar5iv.labs.arxiv.org/html/2107.11152
- Wilkinson et al., FAIR principles, Scientific Data 2016. https://pmc.ncbi.nlm.nih.gov/articles/PMC4792175/
- NASA SPD-41a. https://science.nasa.gov/spd-41/ (`lit_cs/spd41a.txt`; "robust, standards-compliant metadata" found).
- ISA-Tab specification. https://isa-specs.readthedocs.io/en/latest/isatab.html ; W3C PROV primer. https://www.w3.org/TR/prov-primer/
- Korini and Bizer, "Column Type Annotation using ChatGPT". https://arxiv.org/abs/2306.00745 (abstract; cited for why AI header readings need a gate).

**PSI.** Listing: POST https://psi.nasa.gov/geode-py/ws/files/v2 . Signed link: https://psi.nasa.gov/geode-py/ws/studies/PSI-<n>/download?file=<name>&version=<v>&redirect=false , then a Range header.

**Repository files read** (under `/Users/choidol/Desktop/NASA/NASA_RAPID/`): `data/pipeline/tests.csv`, `scenario_tests.csv`, `need_tests.csv`, `need_gap_states.csv`, `gap_states.csv`, `retrieval_queue.csv`, `raw_inventory.json`, `raw_values_effect.json`; `pipeline/spec/scenarios.json`, `needs.json`, `raw_columns.json`; `pipeline/README.md`; `data/psi/experimental_tables/PSI-69_Experimental table_FLEX.csv`; `coord/status/*.md`, `coord/decisions.md`, `coord/requests/20261114-2340-*`, `20261114-2349-*`; `web/app.js`, `web/dist/data/build.json`; `video/README.md`.

**Working files of this step:** `final/flex_two_label.py` and `.json`, `final/lunar_links.py`, `final/lunar_links_PSI-69.json`, `final/lunar_links_159.py`, `final/lunar_links_PSI-159.json`. Earlier steps: `chain/chain_proto.py`, `chain/out/chain_lunar_habitat.csv`, `chain/out/lunar_summary.json`, `tiers/testsheets_vs_table.json`, `tiers/code/testsheets.py`, `scripts/join.py`, `scripts/zipdir.py`, `code/gain_by_group.py`, `out/files.csv`, `out/zipdirs.json`.
