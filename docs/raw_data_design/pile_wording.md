# Wording of the three piles: fixed sentences, grounds and slots

*AI-generated (Claude Code, pm role) on 2026-11-15, as step 9 of the build plan in `design.md` section 6. Checked by AI sessions: the session that wrote it, with a recount script over the repository files; a second session that checked it against the repository; and a third session that corrected it for the second's findings at about 01:40 KST (section 14). Read by a person: none yet. The sentences start from `design.md` section 7 and were changed where a wording decision of the team lead or a recount required it; every change is listed in section 12.*

This file fixes the sentences that the page (`web/app.js`, step 8) and the data files (`pipeline/spec/answers.json`, by request to the data role) print for the three piles. A sentence is printed only when its ground holds. Every number in a sentence is a slot filled from a named file. Nothing here is written by a language model when a page loads.

## 0. How to read this file

**Format of a template.** The format is the one `pipeline/spec/answers.json` and `pipeline/spec/statements.json` already use. `{slot}` is replaced by a field. `[slot|one|many]` prints `one` if the slot equals 1 and `many` otherwise. A template holds no digit: every number, date and size is a slot. A slot that is empty when the sentence is used stops the build.

**For each template this file gives:** the template, the slots with the file each is filled from, the ground that must hold before it is printed, one filled example for the lunar habitat, and the check that guards it.

**Slot names are proposals.** The files of steps 2, 3, 4 and 6 do not exist yet (15 November, 00:45 KST). Where the data role's field names differ, its names win, and this file is updated. Until a file lands, the stand-in named beside each slot is used.

| Planned file (step) | Stand-in today |
|---|---|
| `data/pipeline/question_chain.csv` (2) | `docs/raw_data_design/prototype/chain_lunar_habitat.csv`; `data/pipeline/scenario_tests.csv`, `tests.csv`, `need_tests.csv` |
| `data/pipeline/file_links_summary.json`, `test_files.json`, `listing_snapshot.json` (3) | `docs/raw_data_design/prototype/lunar_summary.json`, `lunar_links_PSI-69.json`, `lunar_links_PSI-159.json`; `data/pipeline/raw_inventory.json` |
| block `flex_test_sheets` of `data/pipeline/raw_values_effect.json`, rows of `raw_values.csv` (4) | `tiers/testsheets_vs_table.json` in the design job's scratch folder (not in the repository; see section 13) |
| `data/catalog/reading_order.csv` (6) | none |
| report of `validation/raw_chain_recount.py` (7) | none |
| `reports/spot_check_raw.csv` (11) | none |

**Sizes.** The byte count is the source. The rounded size is computed by the build with one rule for the whole page, in decimal units (1 MB = 10^6 bytes, 1 GB = 10^9 bytes, 1 TB = 10^12 bytes), as `raw_inventory.json` `_meta.units` says. The examples round as `design.md` section 7 does.

**Checks named below** (the fixtures of `design.md` section 10, in its order, and the step checks of section 6):

| Name | What it is |
|---|---|
| F1 | Placement fixture: lunar habitat 26 / 676 / 63 / 1,059 of 1,824; solid fuels 0 / 237 / 139 of 376; ISS 179 / 739 / 106 / 800; Mars habitat no range set for 1,824 |
| F2 | Chain sums: summed over placement, `question_chain.csv` equals `need_gap_states.csv` |
| F3 | Link fixture: 299 files and 24,954,842,492 bytes for the 17 FLEX tests inside the lunar ranges; 99 files and 79,403,613,858 bytes for the nine CFI-G tests; with step 3: 398 files, 104,358,456,350 bytes, second label 336 / 47 / 15. A second prototype rule arrives at 322 for the same 17 FLEX tests, as pairs of a file and a test (section 13); the check of step 3 decides |
| F4 | FLEX numbering: identifier `193F001` on rows 70 and 73; six test sheets numbered above 274; FLEX-19 has 17 files and 1,112,400,426 bytes |
| F5 | The cross-table of the 17 test sheets against NASA's table (`design.md` section 7) |
| F6 | Check O6: `tests.csv`, `need_tests.csv`, `scenario_needs.csv`, `scenario_tests.csv` unchanged, so the counted tests stay P1 133, P2 0, P3 2, S1 298, D1 122, D2 0 |
| B8 | Build checks of step 8: a number on the page equals its CSV cell; bar segments sum to the tests in scope; every place that shows "17" shows liquid droplets, microgravity and 71 to 72 kPa beside it; word scan; phone width |
| R7 | The independent recount of step 7 (`validation/raw_chain_recount.py`) |
| S11 | The spot check of step 11 (`reports/spot_check_raw.csv`) |

**Wording decisions of the team lead that every sentence here passes.**

| Decision | What it means in this file |
|---|---|
| Say who checked, not who did not | The labels say who checked: AI sessions, and "Read by a person: none yet" until a person has read a row. Review by combustion researchers is written as a next step. |
| A research exploration tool, not safety guidance | The small print says so (section 10). No sentence judges a material, an atmosphere or a design. |
| Counts and rankings are the team's computation, not NASA's conclusions | Said in the header line, the reading-order header and the small print. |
| Nothing says what happens at an untested condition | No sentence carries a result from one condition to another. |
| The third pile is "No record in PSI (listing of 14 November 2026)" | The label carries the listing date. No sentence says what NASA has or has not tested, none is built on a test being missing, and none asks for a test. |
| A value read from a raw file is "read from NASA's file, not adopted, not counted" | Section 7. The value is printed as the file writes it, beside the table cell as the table writes it. |
| The lunar wording of 14 November, 14:15 | The 17 droplet tests are shown with fuel form, gravity and 71.2 to 72.4 kPa beside the number, and the scenario's caveat is printed with the header. |

**Words that are not in any template or example** (checked as whole words by `pmpart/check_wording.py`, see section 13): the words the page scan of step 8 bans (`safe`, `unsafe`, `will`, `predict`, `likely`) and the `forbidden_words` of `pipeline/spec/answers.json` (among them `confirmed`, `sufficient`, `representative`, `recommended`). A link whose two labels agree is called "two labels agree", not "confirmed". The small print says "not safety guidance", the lead's wording: `safety` is not the word `safe`, so the page scan must check whole words.

---

## 1. Header line under the environment title

Six sentences, printed in this order as one paragraph.

### 1.1 `header.ranges`

```text
{scenario_label}: oxygen {o2_range_words}, pressure {pressure_range_words}, {gravity_words}.
```

- Slots: `scenario_label`, the two ranges and `gravity_level` from `pipeline/spec/scenarios.json`; range words by `range_words` of `pipeline/spec/answers.json`.
- Ground: the scenario sets an oxygen range and a pressure range. A scenario without ranges (Mars habitat) prints 1.7 instead.
- Example:

> Lunar base or pressurized rover: oxygen 30 to 36%, pressure up to 85.8 kPa, lunar gravity.

- Guarded by: B8 (number on the page equals the spec value).

### 1.2 `header.archive`

```text
NASA's PSI archive lists {archive_files} files ({archive_size}) for {n_investigations} combustion investigations (listing of {listing_date}).
```

- Slots: `data/pipeline/raw_inventory.json`, `_meta.totals.files`, `.bytes`, `.investigations` and `_meta.listings_fetched_at`; after step 3 the date and the sha256 of the listing come from `listing_snapshot.json`.
- Ground: all listings were available (`listings_available` equals `investigations`).
- Example:

> NASA's PSI archive lists 60,866 files (13.47 TB) for 24 combustion investigations (listing of 14 November 2026).

- Guarded by: the check of step 3 (files and bytes per investigation equal `raw_inventory.json`).

### 1.3 `header.links`

```text
{linked_files} of them ({linked_size}, {linked_share}% of the bytes) carry in their name the NASA identifier or the test number of one of the {tests_inside} tests recorded inside these oxygen and pressure ranges: {small_files} files that are not an archive or a video recording ({small_size}) and {big_files} archives and video recordings ({big_size}).
```

- Slots: `file_links_summary.json` (today: `lunar_summary.json`, `files_naming_inside_tests.total`, and the two `lunar_links_*.json` files); `tests_inside` from `question_chain.csv` (today: `scenario_tests.csv`, oxygen and pressure both `in`).
- Ground: the link file of step 3 exists for every investigation that has a test inside the ranges, and its check has passed. "Archive" is a `.zip` file and "video recording" a `.ts` file, by extension; the sentence does not say what an archive holds.
- Example:

> 398 of them (104.4 GB, 0.77% of the bytes) carry in their name the NASA identifier or the test number of one of the 26 tests recorded inside these oxygen and pressure ranges: 316 files that are not an archive or a video recording (86.9 MB) and 82 archives and video recordings (104.3 GB).

- Guarded by: F3 and the check of step 3.
- Note: 296 of the 398 names carry a NASA identifier (197 FLEX, 99 CFI-G) and 102 carry the FLEX test number (`FLEX-nnn`). `design.md` section 7 says "the NASA identifier" for all 398; this template names both labels.

### 1.4 `header.second_label`

```text
File name and PSI folder name the same test for {folder_agrees} of them; {folder_no_test} [folder_no_test|sits|sit] in a folder that names no test; {folder_other_test} [folder_other_test|sits|sit] in a folder that names another test ({other_test_detail}). The team lists these cases and does not resolve them.
```

- Slots: `file_links_summary.json`, link states by second label (today: `by_label_and_folder` and `by_folder` of the two `lunar_links_*.json` files); `other_test_detail` from the list `folder_names_another_test`.
- Ground: printed whenever 1.3 is printed. If a count is zero its clause is dropped by the build, not reworded.
- Example:

> File name and PSI folder name the same test for 336 of them; 47 sit in a folder that names no test; 15 sit in a folder that names another test (15 files of FLEX-20 in a folder named after FLEX-21). The team lists these cases and does not resolve them.

- Guarded by: the check of step 3 (336 / 47 / 15) and F4.

### 1.5 `header.tests`

```text
The {tests_inside} tests are {group_list}, all in {gravity_of_tables}.
```

`group_list` joins one fragment per investigation: `{n} {fuel_form_words} ({investigation_short}, {pressure_words})`.

- Slots: `question_chain.csv` (today: `scenario_tests.csv` joined with `tests.csv`: `fuel_phase`, `sample_geometry`, `pressure_kpa`, `gravity_level`).
- Ground: `gravity_level` has one value over the tests inside; otherwise the last clause lists the values with their counts. The gravity level is a constant that the team's mapping sets per table (`pipeline/spec/sources.json`); NASA's tables have no gravity column, so the sentence does not say "recorded".
- Example:

> The 26 tests are 17 fuel-droplet tests (FLEX, 71.2 to 72.4 kPa) and 9 gas flames (CFI-G, 50.7 kPa), all in microgravity.

- Guarded by: F1 and B8 (the "17" rule).

### 1.6 `header.limit` and the scenario caveat

```text
A file that names a test is not shown to hold what a question needs. The counts are the team's computation from PSI's file listing and NASA's tables, not NASA's conclusions.
```

- Slots: none. Printed whenever 1.3 is printed.
- After it, the `caveat` of the scenario in `pipeline/spec/scenarios.json` is printed unchanged where the scenario has one. For the lunar habitat that text says that the pressure range reaches up to 85.8 kPa, above the 70.3 kPa of the challenge statement, and that the 17 counted tests were recorded at 71.2 to 72.4 kPa. This keeps the lead's decision of 14 November, 14:15.
- Guarded by: B8.

### 1.7 `header.no_range`

```text
{scenario_label}: this environment sets no oxygen range and no pressure range, so no test is placed and no file is listed.
```

- Ground: the scenario has no ranges (`placement` is `no_range_set` for every test). Sentences 1.3 to 1.5 are not printed.
- Example: none for the lunar habitat. For the Mars habitat the placement is `no_range_set` for all 1,824 tests (F1).

---

## 2. The bar and the placements

One bar per question. The segment labels are fixed:

| Placement in `question_chain.csv` | Label on the page | One-line meaning |
|---|---|---|
| `inside` | Inside the ranges | Oxygen and pressure are both in NASA's table and inside the ranges. |
| `cannot_be_placed_from_table` | Cannot be placed from the tables | Oxygen or pressure is not in NASA's table, and neither is recorded outside. |
| `oxygen_of_oxidizer_stream` | Oxygen recorded for an oxidizer stream | The table's oxygen is that of a gas stream, not of the atmosphere around the flame. |
| `outside_by_recorded_value` | Outside by a recorded value | Oxygen or pressure is in NASA's table and lies outside the range. |
| `no_range_set` | No range set | This environment sets no oxygen range and no pressure range. |

### 2.1 `bar.line`

```text
{need_label} ({need_id}), {tests_in_scope} tests of {scope_words}: inside {inside} | cannot be placed from the tables {cannot} | oxygen recorded for an oxidizer stream {stream} | outside by a recorded value {outside}.
```

- Slots: `question_chain.csv`, summed per scenario and need (today: `scenario_tests.csv`, `tests.csv`, the need's `scope` in `pipeline/spec/needs.json`). A segment with zero tests is dropped.
- Ground: the four counts sum to `tests_in_scope`.
- Examples:

> Extinction conditions (S1), 1,824 tests of all fuel phases: inside 26 | cannot be placed from the tables 676 | oxygen recorded for an oxidizer stream 63 | outside by a recorded value 1,059.

> Flammability limit (P1), 376 tests of solid fuels: inside 0 | cannot be placed from the tables 237 | outside by a recorded value 139.

- Guarded by: F1, F2 and B8 (segments sum to the tests in scope).

---

## 3. The three piles: label and one-line meaning

### 3.1 Pile 1

Label:

```text
In NASA's tables
```

Meaning:

```text
Tests recorded inside this environment's oxygen and pressure ranges, and what NASA's per-test tables hold for them.
```

### 3.2 Pile 2

Label:

```text
In the archive, not in a table
```

Meaning:

```text
A test is recorded, and a value this question needs is not in NASA's table. Listed here: the file groups that name these tests, how many files were opened, and what was read. A listed file group is not shown to hold the value.
```

Lower shelf, label:

```text
Not found in the files opened
```

Lower shelf, meaning:

```text
Not in a table, and no header accepted for it in any file opened so far. This is a statement about the files opened, not about the archive.
```

### 3.3 Pile 3

Label:

```text
No record in PSI (listing of {listing_date})
```

Meaning:

```text
No test at this condition is in PSI's per-test tables as the team mapped them ({tests_mapped} tests of {investigations_mapped} investigations), on one of three stated grounds, each printed with its source. The statement describes PSI's record on that date. The {investigations_without_rows} investigations that have no row per test are outside it.
```

- Slots: `listing_date` as in 1.2; `tests_mapped` and `investigations_mapped` from `data/pipeline/tests.csv` (rows; distinct `investigation_id`); `investigations_without_rows` is `n_investigations` minus `investigations_mapped`.
- Ground for the label: at least one of the three grounds of section 5 holds for the question. If none holds, pile 3 is not printed for that question.
- Example:

> No record in PSI (listing of 14 November 2026)

> No test at this condition is in PSI's per-test tables as the team mapped them (1,824 tests of 12 investigations), on one of three stated grounds, each printed with its source. The statement describes PSI's record on that date. The 12 investigations that have no row per test are outside it.

- Guarded by: F1 (1,824 tests) and F6. `design.md` section 1 names "the 12 investigations whose table has no row per test"; `tests.csv` holds rows of 12 of the 24 investigations.
- The label is never shortened to a sentence about what NASA tested, and no line of pile 3 asks for a test.

---

## 4. Pile 1 lines

### 4.1 `pile1.none`

```text
{inside} of the {tests_in_scope} tests of {scope_words} are recorded inside these ranges.
```

- Ground: `inside` is 0 for the question's scope.
- Example:

> 0 of the 376 tests of solid fuels are recorded inside these ranges.

- Guarded by: F1.

### 4.2 `pile1.counted`

```text
{counted_inside} [counted_inside|test|tests] counted for this question: {investigation_label} {fuel_form_words}, {fuel_list}, {gravity_of_tables}, oxygen {o2_values_words}, {pressure_min} to {pressure_max} kPa.
```

- Slots: `question_chain.csv` rows with placement `inside` and counted tests above zero (today: `scenario_tests.csv`, `need_tests.csv` with `objective_link` `stated`, `tests.csv`).
- Ground: `counted_inside` is above zero. Fuel form, gravity and pressure are always in the sentence (rule of B8).
- Example:

> 17 tests counted for this question: FLEX (PSI-69) fuel-droplet tests, liquid heptane or methanol, microgravity, oxygen 30% or 34%, 71.2 to 72.4 kPa.

- Guarded by: F1, F6 and B8.

### 4.3 `pile1.outcomes` and `pile1.codes`

```text
Recorded for them in NASA's table: {outcome_list}.
```

```text
{variable_label} as the table writes it: a number above zero for {n_number}, a zero for {n_zero}, blank for {n_blank}, a dash for {n_dash}.
```

- Slots: `outcome_list` from `tests.csv` (one fragment per outcome of the need in `needs.json`: label, tests with a value, of the counted tests inside). The four code counts come from the cell text of NASA's table file itself (`data/psi/experimental_tables/`), because `tests.csv` turns blank and dash both into empty; after step 4 from the block `flex_test_sheets`.
- Ground for `pile1.codes`: the table column holds a blank or a dash for at least one counted test inside.
- Examples:

> Recorded for them in NASA's table: how the burn ended 17 of 17 (15 disruption, 2 completion); burn time 16 of 17; flow speed 0 of 17.

> Extinction diameter as the table writes it: a number above zero for 4, a zero for 2, blank for 8, a dash for 3.

- Guarded by: F5 and F6.

### 4.4 `pile1.not_counted`

```text
{n_more} more [n_more|test|tests] inside the ranges: {fuel_form_words} of {investigation_label}, recorded at {pressure_words} and oxygen {o2_min} to {o2_max}%. Not counted: {reason_list}.
```

`reason_list` joins the fragments that apply, with a semicolon. There are two fragments, and a fragment with a count of zero is dropped:

```text
for {n_not_stated} of them the PSI record of that investigation does not state this purpose, as the team read it
```

```text
{n_no_outcome} [n_no_outcome|holds|hold] no outcome of this question in NASA's table
```

- Slots: `question_chain.csv` (placement `inside`, counted tests zero). `n_not_stated`: the tests among them with a row in `need_tests.csv` for the need whose `objective_link` is `not_stated`. `n_no_outcome`: the tests among them with no row in `need_tests.csv` for the need, for which `tests.csv` holds every required condition of the need and none of the outcomes of `outcomes_any` (`pipeline/spec/needs.json`). `need_tests.csv` holds a row only for a test that meets the need's required conditions and holds one of its outcomes (`pipeline/README.md`).
- Ground: tests inside the ranges exist that are not counted for the need, and `n_not_stated` plus `n_no_outcome` equals `n_more`. If a test is not counted for a third reason (a required condition other than oxygen and pressure is not in the table, or a row carries another `objective_link`), the build stops; the sentence is not reworded by hand.
- Example:

> 9 more tests inside the ranges: gas flames of CFI-G (PSI-159), recorded at 50.7 kPa and oxygen 33.2 to 35.9%. Not counted: for 7 of them the PSI record of that investigation does not state this purpose, as the team read it; 2 hold no outcome of this question in NASA's table.

- Guarded by: F1 and F6. Proposed addition for `pipeline/check.py` and R7: of the 9 CFI-G tests inside the lunar ranges, 7 have an S1 row with `not_stated` and 2 have no row (true today).
- Note: the two tests without a row are `CFIG-N-21106F2` and `CFIG-N-21106F5`. NASA's table gives no burn time for them, writes a dash for how the flame ended and comments "direct cool - no hot ignition" (rows 37 and 40 of `PSI-159_Experimental table_CFI-G_Normal Flames.csv`). The first version of this template gave the purpose of the record as the reason for all nine.

---

## 5. Pile 3: the three grounds

Pile 3 is printed on these three grounds and on no other. Anything else belongs in pile 2 or on its lower shelf. Each ground prints its source.

### 5.1 Ground 1, `pile3.common_value`: a value common to every mapped table

```text
{scenario_level_label}: {tests_at_level} of {tests_in_scope} tests. Ground: the team's mapping sets {common_value} for each of the {tables_mapped} per-test tables ({tests_with_common_value} of {tests_in_scope} tests); no table has a column for it; the PSI record's {record_field_label} field names {record_values_list}. {second_source_sentence}
```

`record_values_list` joins one fragment per value of the field, the most frequent first: `{value_words} for {n} of the {investigations_mapped} mapped investigations`, or `{value_words} for {investigation_id}` where the value stands in one record. `value_words` are fixed words for a value as the record writes it: "the ISS" for `International Space Station (ISS)`, "the Cygnus spacecraft" for `Cygnus Spacecraft`.

`second_source_sentence`, when a reference item of the challenge statement speaks of data at the scenario's level:

```text
The challenge statement says that {item_text} (reference item {reference_item}, the team's summary).
```

- Slots: `data/pipeline/tests.csv`, column of the variable (`gravity_level`), restricted to the question's scope; `tables_mapped` is the number of distinct `source_file` values; the source of the value is `pipeline/spec/sources.json`, `constants` of each table (in `values_long.csv` the `source_column` reads "(constant in sources.json)"); `scenario_level_label` from `gravity_level` of `scenarios.json`. `record_field_label` and `record_values_list`: the basis of the constant, a field the data role is asked to add to `pipeline/spec/sources.json`; today the field `Comment[Flight Platform]` of `i_Investigation.txt` in PSI's metadata archive of each mapped investigation (step 10; the values are listed in `psi_metadata_summary.md`). `reference_item` from `pipeline/spec/references.json`; `item_text` is the first clause of the item's `text`, which is the team's summary of the challenge statement, not a quotation, and is printed without quotation marks.
- Ground: the variable has exactly one distinct value over all tests in scope (`tests_with_common_value` equals `tests_in_scope`), and that value differs from the scenario's level. If one test has no value or another value, the ground does not hold. Where the value is a table constant and not a column, the sentence says so, as below. The record field is printed as NASA's record writes it; it names a platform, not a gravity level, and the sentence does not turn it into one. If the field is empty for a mapped investigation, the fragment list says so with its count.
- Example:

> Lunar gravity: 0 of 1,824 tests. Ground: the team's mapping sets microgravity for each of the 14 per-test tables (1,824 of 1,824 tests); no table has a column for it; the PSI record's Flight Platform field names the ISS for 11 of the 12 mapped investigations and the Cygnus spacecraft for PSI-99. The challenge statement says that PSI holds no partial-gravity combustion data yet (reference item CH.partial_gravity, the team's summary).

- Guarded by: F1 for the 1,824 tests. Section 10 of the design has no fixture for the common value itself. Proposed addition for `pipeline/check.py` and R7: `gravity_level` is `microgravity` for 1,824 of 1,824 rows of `tests.csv`, over 14 source files (true today); the Flight Platform field reads `International Space Station (ISS)` in 11 of the 12 mapped records and `Cygnus Spacecraft` in the record of PSI-99 (true in the archives fetched on 15 November).
- Note: `design.md` writes "every per-test table records microgravity". The tables hold no gravity column; `sources.json` sets the level as a constant of each table and names no document for it. The Flight Platform field is the document found for it. It is printed as written: the records of PSI-98 (Saffire-I) and PSI-100 (Saffire-III) read `International Space Station (ISS)`, and their hardware fields read `Saffire 1 enclosure in Cygnus` and `Saffire III enclosure in Cygnus`. The request to the data role is to add this field to `sources.json` as the basis of the constant.
- Note: the first version of the second sentence said that the challenge statement "says the same of PSI as a whole". The reference item is about partial-gravity data, not about microgravity, so the sentence now says what the item says.

### 5.2 Ground 2, `pile3.all_counted_outside`: every counted test lies outside by a recorded value

```text
This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of {listing_date}). All {counted} counted tests ({by_investigation}) have their {variable_label} in NASA's table, between {recorded_min} and {recorded_max}{unit}, {side_word} this environment's {bound}{unit}. Placement uses the table value, so reading raw files does not move one of them in. Source: {source_list}.
```

`source_list` joins one fragment per table: `column {source_column} of {source_file} ({n} tests)`.

- Slots: `listing_date` as in 1.2; `question_chain.csv` rows of the need with counted tests above zero (today: `need_tests.csv`, `scenario_tests.csv`, `tests.csv`); `source_column` and `source_file` as written, from `data/pipeline/values_long.csv`; `bound` and `unit` from `scenarios.json` and `variables.json`; `side_word` is `below` or `above`.
- Ground, all of: the question has at least one counted test; every counted test has placement `outside_by_recorded_value`; every one of them is outside by the named variable, on the same side of the range. If one counted test is inside, cannot be placed, or has its oxygen recorded for an oxidizer stream, the ground does not hold and the sentence is not printed.
- Example (P1, flammability limit):

> This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of 14 November 2026). All 133 counted tests (125 BASS-II, 8 Saffire-II) have their oxygen in NASA's table, between 13.6 and 22.2%, below this environment's 30%. Placement uses the table value, so reading raw files does not move one of them in. Source: column Calibrated initial O2 % by vol of PSI-25_Experimental table_BASS-II.csv (125 tests); column Percent O2 (Note 1) of PSI-99_Experimental table_SAFFIRE-2.csv (8 tests).

- The same ground holds for P3 (2 counted tests, 21.5 to 21.7%) and D1 (122 counted tests, 13.6 to 22.2%) in the lunar habitat.
- Guarded by: F1 (solid fuels 0 / 237 / 139), F2 and F6.

### 5.3 Ground 3, `pile3.investigation_sentence`: a quoted sentence about a whole investigation

```text
{variable_label} {range_words} in {investigation_label} ({tests_in_table} tests in the table, {counted} counted for this question): no record in PSI. Ground: {source_kind} says: "{quote}" (source: {reference_item}, {document_label}, {where}). The sentence is about the whole investigation and is not used as a value of any test.
```

- Slots: `question_chain.csv` rows with location `document_sentence` (today: `need_gap_states.csv` state `documented_only`, and `documented_by`); `quote`, `reference_item`, `where` and the document from `pipeline/spec/references.json` and `pipeline/spec/sources.json` (`documented_elsewhere`). `source_kind` is one of two fixed phrases: `The PSI record` when the quote is a field of the PSI record, `A paper of the investigators` when it is a publication. It is never "NASA says" for a publication.
- Ground, all of: the quote is verbatim in a document the team read in full text; it states the variable for the whole investigation; the stated value lies outside the scenario's range (the data file carries the stated value and the comparison as fields); the table of the investigation has no column for the variable.
- Example:

> Pressure up to 85.8 kPa in BASS-II (PSI-25) (129 tests in the table, 125 counted for this question): no record in PSI. Ground: A paper of the investigators says: "Pressure was not varied from 1 atmosphere." (source: ICES19.pressure, ICES-2019-BASS2, Section II). The sentence is about the whole investigation and is not used as a value of any test.

- Guarded by: F2 (P1 pressure: document only 129) and the existing rule of `statements.json` (`documented.elsewhere`: the sentence is not used as a value of any test).
- Note: `design.md` section 3.2 calls this "a NASA sentence". In the repository the quote comes from a conference paper of the investigators (reference `ICES-2019-BASS2`, read in full text), so the template names the kind of source.

---

## 6. The sentence "This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges."

```text
This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of {listing_date}).
```

- **When it applies.** Only where ground 2 (5.2) holds, as the first sentence of that ground, inside pile 3, under the label "No record in PSI (listing of {listing_date})". It is always followed by the sentence that gives the count, the recorded range and the bound.
- **What it says.** Two things about PSI's record on the listing date: the gap is not of the kind that reading raw files can close, and no counted test of the question is recorded inside the ranges, for the reason that a recorded value lies outside, not that a cell is empty. It says nothing about what was or was not tested, inside or outside PSI's record, and it does not ask for a test.
- **When it does not apply.** Where a counted test cannot be placed, or is inside. Lunar habitat, S1: 17 counted tests are inside, so it is not printed. ISS, P1: of 133 counted tests 78 are outside by a recorded oxygen value and 55 cannot be placed because the table holds no pressure, so it is not printed. P2 and D2 have no counted test in any environment, so it is not printed there either; what the files opened hold for them goes on the lower shelf of pile 2.
- Lunar habitat, where it is printed: P1 (133 of 133 counted tests outside by oxygen), P3 (2 of 2), D1 (122 of 122).
- Guarded by: F1, F2, F6.
- Not used, in any form: "This gap is a missing test" and "a test that PSI's tables do not hold". Both are built on a test being missing and read as a statement that a test was not done or should be done. That breaks the lead's wording for pile 3. The first version of this file had the first as the template and the second as a replacement.

---

## 7. Pile 2: a value read from a raw file

### 7.1 `raw.group_read`: the file group that was read

```text
{group_label} of these {tests} tests ({name_pattern}, {files} [files|file|files], {bytes} bytes; {files_read} of {files} read). The identifier printed inside equals the table's in {id_agree} of {files_read}.
```

### 7.2 `raw.value`: one value

```text
Read from NASA's file, not adopted, not counted: {file_name} ({file_bytes} bytes) writes {key_as_written} = {value_as_written}; NASA's table cell: {table_cell_as_written}.
```

### 7.3 `raw.codes`: what the codes mean

```text
Read from NASA's raw files by the team's code. Not a table value, not counted. No file opened so far says what {codes_list} mean, or whether the sheet's line is the {table_column_label} of the table.
```

- Slots: rows of `data/pipeline/raw_values.csv` for the test sheets and the block `flex_test_sheets` of `raw_values_effect.json` (step 4). Today: `tiers/testsheets_vs_table.json` and `tiers/testsheets_read.json` of the design job, which read the first 700 bytes of each of the 17 sheets (11,871 of 15,369 bytes; the `key = value` lines are in that part).
- Ground, all of: the file was read by code; it is tied to the table row by the identifier printed inside it and a second field (date, or oxygen and pressure); the value is printed exactly as the file writes it (`nan`, `0.00` included) beside the table cell exactly as the table writes it (`blank` and `dash` named as such); the value is in no count and not in `tests.csv` (F6).
- `table_cell_as_written` is the cell text, or the word `blank` for an empty cell, or the word `dash` for an en dash.
- Examples:

> Per-test sheets of these 17 tests (FLEX-nnn_TestSheet.txt, 17 files, 15,369 bytes; 17 of 17 read). The identifier printed inside equals the table's in 17 of 17.

> Read from NASA's file, not adopted, not counted: FLEX-023_TestSheet.txt (735 bytes) writes Dext (mm) = 1.32; NASA's table cell: blank.

> Read from NASA's raw files by the team's code. Not a table value, not counted. No file opened so far says what nan, 0.00, a blank or a dash mean, or whether the sheet's line is the visible-flame extinction diameter of the table.

- Guarded by: F5, F6 and the check of step 4 (every field compared with the table; codes kept as written).
- The words "read from NASA's file, not adopted, not counted" are fixed and are not shortened to "raw value" or "new value".

---

## 8. Pile 2: a file group not yet read, and the lower shelf

### 8.1 `group.not_read`: "n of N opened"

```text
{group_label} ({name_pattern}): {files} [files|file|files], {size}; {opened} of {files} opened. {evidence_sentence} Not read.
```

`evidence_sentence` is one of three fixed forms:

```text
A header {header_as_written} was seen in {seen_files} opened [seen_files|file|files] of the file [groups_n|group|groups] these belong to ({group_files} files, {group_size}).
```

```text
No file of this group was opened.
```

```text
Directory read for {dirs_read} of {files} ({dir_bytes} bytes requested): {members_words}. It adds no value and no test.
```

- Slots: `question_chain.csv` (file groups, files, bytes, files opened n of N) and `pipeline/spec/raw_columns.json` (`files_in_listing`, `bytes_in_listing`, `sample_file`, `header_as_written`); for archive directories `data/pipeline/archive_members.csv` (step 12).
- Ground: `opened` counts files of exactly the listed set that were opened. A header seen in another file of the group is said to be seen in the group, never in the listed files.
- Examples:

> One-page summary PDFs of the 11 tests without a number in the table (FLEX-nnn_Summary.pdf, FLEX_nnn_Summary.pdf): 11 files, 2.45 MB; 0 of 11 opened. A header Dext = was seen in 2 opened files of the file groups these belong to (370 files, 100.3 MB). Not read.

> Archives of these 17 tests (identifier followed by a letter, .zip): 47 files, 24.92 GB; 0 of 47 opened. Directory read for 3 of 47 (370,662 bytes requested): 886 tif, 852 tif and 122 bmp frames for FLEX-19. It adds no value and no test. Not read.

- Guarded by: F3 (47 zip files, 24,923,186,032 bytes), the check of step 2 (files opened n of N is a column of the chain) and, for directories, the check of step 12.
- Note: the 11 summary PDFs belong to 10 tests (FLEX-22 has two, FLEX-24 has none). The two opened files are `FLEX-242_Summary.pdf` and `FLEX_254_Summary.pdf` (`raw_columns.json`); neither names a lunar test.

### 8.2 `shelf.line`: the lower shelf

```text
{variable_label}: not in NASA's table for {tests_lacking} of the {tests_inside} tests; no header in the files opened so far was accepted for it{seen_not_mapped_clause}. Not opened: {unopened_files} [unopened_files|file|files] ({unopened_size}) in {unopened_groups} document [unopened_groups|group|groups] of {investigation_label}.
```

`seen_not_mapped_clause` is empty where no header for the variable was seen. Where one was seen and not mapped:

```text
 ({related_headers} [related_headers|header|headers] seen in {related_files} opened [related_files|file|files] and not mapped: {headers_as_written}; {not_mapped_reason})
```

```text
{tests_cannot} tests cannot be placed: {by_investigation_list}. The tables hold neither their oxygen nor their pressure, or only one of the two.
```

- Slots: `question_chain.csv` rows with location `not_found_in_files_opened` (today: `data/pipeline/gap_states.csv`, state `not_in_sampled_files`, columns `tests_in_state`, `files`, `bytes`, `file_groups`; placement counts as in F1). The clause is filled from `pipeline/spec/raw_columns.json`, list `related_columns_not_mapped` of the investigation, entries whose `for_variable` is the variable: `headers_as_written` is `header_as_written`, `related_headers` the number of headers in it, `related_files` the number of sample files of the entry's `group`, and `not_mapped_reason` the first part of `not_mapped_because`, as written.
- Ground: the variable has no table value for the listed tests, and no opened file of the investigation has a header mapped to it. A header that was seen and rejected is named, so the line never says that nothing was seen when something was.
- Examples:

> Flow speed: not in NASA's table for 17 of the 17 tests; no header in the files opened so far was accepted for it (4 headers seen in 1 opened file and not mapped: FLOW_NOZZLE_1_SPEED(N/A), FLOW_NOZZLE_2_SPEED(N/A), TP_PARAMETER_FLOW_NOZZLE_1_SPEED(N/A), TP_PARAMETER_FLOW_NOZZLE_2_SPEED(N/A); unit written as N/A). Not opened: 32 files (14.4 MB) in 4 document groups of FLEX (PSI-69).

> 676 tests cannot be placed: 435 SPICE (PSI-107), 121 BASS (PSI-26), 109 SAME-R (PSI-101) and 11 others. The tables hold neither their oxygen nor their pressure, or only one of the two.

- Guarded by: F1 (676) and F2.
- A lower-shelf line never says that a value is absent from the archive.
- Note: the four flow headers stand in one entry of `related_columns_not_mapped` for PSI-69 (group `r2_testpoint_settings`: 11 files, 29,688 bytes, one sample file opened, `PSI-69_Raw Data_256R002_Testpoint_Settings.txt`). The data role's reason in full: "unit written as N/A; the file does not say which flow the nozzle speed is or in which unit; not accepted". The opened file belongs to another test than the 17. The first version of this line said "not seen in any file opened so far".

---

## 9. Header of the reading order

```text
Reading order: the team's rule, not a NASA priority. It says where to read first, not that the value is there.
```

```text
Rule: first, file groups in which a column for oxygen or pressure was seen for tests that cannot be placed; then file groups that could add a counted test; then file groups that could add a value to a test already counted inside. Within a class: more target tests first, then fewer bytes.
```

Row of the list, `order.row`:

```text
{order}. {group_label} ({investigation_label}): {files} [files|file|files], {size}; target tests {target_tests}; {evidence_words}.
```

- Slots: `data/catalog/reading_order.csv` (step 6). `evidence_words` is one of the closed list `value read for {k} tests`, `header seen in {seen} of {files} files`, `not opened`.
- Ground: `reading_order.csv` exists and its check has passed (deterministic; a test counted once; bytes counted once per group). The header has no slot and is printed above every list. No probability, expected gain or interval is printed.
- Example of the header: the two sentences above, unchanged. Example of a row, with the numbers of `design.md` section 7; the order number comes from `reading_order.csv`, which does not exist yet, so it is left as a slot:

> {order}. One-page summary PDFs (FLEX, PSI-69): 11 files, 2.45 MB; target tests 10; not opened.

- Guarded by: the check of step 6 and R7.

---

## 10. Small print under the block

Five sentences, in this order.

```text
Built by code from PSI's file listing of {listing_date} and NASA's per-test tables as the team mapped them. No language model writes or changes a line of this block.
```

```text
"Column seen" means a header that an AI agent read in one opened file of a file group and that the data role's AI session opened again. It is not a measurement of the test, and the other files of the group were not opened.
```

```text
No value read from a raw file has entered a count. Counted tests: {counted_list}.
```

```text
{recount_label}. {person_label}.
```

```text
A research exploration tool, not safety guidance. Counts and the reading order are the team's computation, not NASA's conclusions. Nothing here says what happens at a condition that was not tested.
```

- Slots: `listing_date` as in 1.2; `counted_list` from `need_tests.csv` (`objective_link` `stated`, per need); `recount_label` and `person_label` from section 11.
- Ground: the first sentence holds as long as no model call is in `pipeline/raw_gaps.py`, `web/build.py` or the page code of this block; the third as long as F6 passes.
- Example:

> Built by code from PSI's file listing of 14 November 2026 and NASA's per-test tables as the team mapped them. No language model writes or changes a line of this block.

> No value read from a raw file has entered a count. Counted tests: P1 133, P2 0, P3 2, S1 298, D1 122, D2 0.

> Recount by a second AI session: not yet. Read by a person: none yet.

- Guarded by: F6, R7, S11 and B8.
- Optional sixth sentence, a plan, printed only if the lead wants a next step on the page: `Next step: review of the placement rule and the three grounds by combustion researchers.`

---

## 11. Labels for who recomputed or read what

One label per row or block, from this closed list. A label is printed only when its ground holds.

```text
Read by the team's code
```

- Ground: the value was parsed by code from the file named in the row (test sheets, step 4). Filled from `raw_values.csv`.

```text
AI reading of the header; opened again by the data role's AI session; {opened} of {files} files opened
```

- Ground: the entry is in `pipeline/spec/raw_columns.json`, where an AI agent read a header in one sample file per group.

```text
Recomputed by a second AI session
```

- Ground: the number is reproduced in the report of `validation/raw_chain_recount.py`, which does not import the pipeline (step 7).

```text
Recount by a second AI session: not yet
```

- Ground: no such report covers the number. This is the default.

```text
Read by a person: {rows} [rows|row|rows]
```

- Ground: rows of `reports/spot_check_raw.csv` whose reviewer kind is a person (step 11).

```text
Read by a person: none yet
```

- Ground: no such row. This is the default.

The spot-check sentence, `who.sample`, printed only for a seeded random sample in which no link was wrong:

```text
A team member opened {sample} links drawn at random on the PSI page; {wrong} were wrong. With none wrong in {sample}, fewer than {bound}% of all links are wrong, at {level}% confidence.
```

- Slots: `reports/spot_check_raw.csv`; `bound` is 100 x (1 - 0.05^(1/sample)), rounded up to one decimal: 9.6 for 30 links (the value is 9.503), 4.9 for 60 (the value is 4.870).
- Ground: the sample was drawn with a recorded seed; `wrong` is 0; `level` is 95. With one or more wrong links the sentence gives the count only, and no bound.
- Example (lunar habitat, today): none can be filled; no person has read a row. The labels printed today are:

> Recount by a second AI session: not yet

> Read by a person: none yet

- Example of the header-reading label, for the FLEX test sheets before step 4:

> AI reading of the header; opened again by the data role's AI session; 1 of 272 files opened

- Guarded by: R7 and S11.
- No label says that a specialist did or did not review the work, and none implies a review by NASA. "The data role" is named as an AI session, because `compliance/AI_USAGE_LOG.md` records that work as done and recomputed by AI agents.
- Note on the bound: `design.md` writes "fewer than 9.5%" for 30 links. The exact value is 9.503%, so "fewer than 9.5%" is not strictly true; the label rounds up to 9.6. For 60 links the value is 4.870%, and "fewer than 4.9%" holds.

---

## 12. Changes against `design.md` section 7

The left column quotes `design.md` as it stood at 00:35 KST on 15 November (commit `2d503de`). Three of the sentences were also corrected in `design.md` itself at about 01:40 KST; those rows say so.

| Sentence in the design | Change here | Reason |
|---|---|---|
| "carry in their name the NASA identifier of one of the 26 tests" | "the NASA identifier or the test number" | 102 of the 398 names carry the FLEX test number, not the identifier (`lunar_links_PSI-69.json`: `name_number` 95 + 7). |
| "316 files that are not an image archive or a video recording" and "82 image archives and video recordings" | "an archive or a video recording" | The split is by extension (`.zip`, `.ts`). What an archive holds is known for 3 of the 74 archives (the FLEX-19 directories). |
| Pile-3 ground: "a NASA sentence about a whole investigation" | "{source_kind} says", with two allowed kinds | The BASS-II sentence is from a paper of the investigators (`ICES-2019-BASS2`), not from a PSI record field. |
| "the challenge statement says PSI holds no partial-gravity combustion data yet" | "The challenge statement says that PSI holds no partial-gravity combustion data yet (reference item CH.partial_gravity, the team's summary)", without quotation marks on the page | The repository holds the team's summary of that passage, not its wording. The item is about partial-gravity data; it does not say that every test is a microgravity test. |
| "This gap is a missing test, not unprocessed data: every counted test of this question has its oxygen in NASA's table, and reading raw files cannot move one in." | First sentence: "This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of 14 November 2026)." Last sentence: "Placement uses the table value, so reading raw files does not move one of them in." Also corrected in `design.md` sections 3.2 and 7. | "A missing test" says or implies that a test was not done or should be done; pile 3 says only "no record in PSI (listing of 14 November 2026)". A raw file can write another oxygen value (FLEX-28: sheet 0.29, table 0.3); what is fixed is the team's rule that placement uses the table. |
| "17 of 17 read" for the test sheets | Kept, with the note that the design job read the first 700 bytes of each sheet (11,871 of 15,369 bytes) | `tiers/testsheets_read.json`. Step 4 reads the sheets whole. |
| "A header `Dext =` was seen in one opened file of this group" | "seen in 2 opened files of the file groups these belong to (370 files, 100.3 MB)"; "0 of 11 opened" | `raw_columns.json`: the 11 PDFs lie in two groups, one sample file opened in each, neither among the 11. |
| "A column 'seen' was read in one opened file of its group by an AI and re-read by the data role" | "the data role's AI session opened again" | The log records that work as done and recomputed by AI agents; the label must not read as a person's check. |
| "Recomputed by a second AI session; <read by a team member: n rows>" | Two labels with defaults "not yet" and "none yet" | The lead's decision: say who checked. |
| "This panel gives no safety judgement and predicts nothing." | "A research exploration tool, not safety guidance. ... Nothing here says what happens at a condition that was not tested." | The lead's wording; no word of the page scan as a whole word. |
| "9 more tests ... their investigation does not state this purpose, so they are not counted" | "Not counted: for 7 of them the PSI record of that investigation does not state this purpose, as the team read it; 2 hold no outcome of this question in NASA's table." Also corrected in `design.md` section 7. | `need_tests.csv` `objective_link` is the team's reading of the record, and it has a row for 7 of the 9 tests only. The other 2 hold no outcome in the table, so the purpose of the record is not their reason. |
| "Flow speed: missing for all 17; nothing opened holds it." | "no header in the files opened so far was accepted for it", with the headers that were seen and not mapped. Also corrected in `design.md` section 7. | `raw_columns.json` lists four nozzle-speed headers for PSI-69, seen in one opened file and not mapped because the unit is written as N/A. |
| "0 wrong in 30: fewer than 9.5%" | "fewer than 9.6%" | The exact bound is 9.503%. |
| "Ground: every per-test table records microgravity" | "the team's mapping sets microgravity for each of the 14 per-test tables; no table has a column for it; the PSI record's Flight Platform field names the ISS for 11 of the 12 mapped investigations and the Cygnus spacecraft for PSI-99" | `values_long.csv`: the gravity level of all 1,824 tests is a constant of `sources.json`, not a table column. The Flight Platform field of PSI's metadata archives is the document behind it. |
| Ground 2 without a source | Adds "Source: column ... of ... (n tests)" | Each ground prints its source. |
| Pile-3 meaning | Adds the reach: 1,824 tests of 12 investigations; 12 investigations without a row per test are outside | Ground 1 holds for the mapped tables only. |

---

## 13. Numbers used in the examples

Recounted on 15 November 2026 by `pmpart/verify_numbers.py` (in the pm session's scratch folder, read-only on the repository) unless another source is named.

| Number | Value | Source |
|---|---|---|
| Archive | 60,866 files; 13,471,850,126,356 bytes; 24 investigations; listing fetched 2026-11-14T05:57:17Z | `data/pipeline/raw_inventory.json` `_meta` |
| Placement, lunar habitat | inside 26; cannot be placed 676; oxidizer stream 63; outside 1,059; solid fuels 0 / 237 / 139 | `scenario_tests.csv`, `tests.csv` |
| Cannot be placed, by investigation | PSI-107 435; PSI-26 121; PSI-101 109; PSI-10 4; PSI-102 4; PSI-100 2; PSI-99 1 | same |
| Tests inside | 17 FLEX (PSI-69), liquid, 71.2341 to 72.3674 kPa, oxygen 30 or 34%; 9 CFI-G (PSI-159), gas, 50.665 kPa, oxygen 33.2446 to 35.8532% | same |
| The 17 counted tests | heptane 8, methanol 9; test end: disruption 15, completion 2; burn time 16; flow 0 | `tests.csv` |
| Counted tests | P1 133 (125 PSI-25, 8 PSI-99; oxygen 13.6 to 22.2%); P3 2 (21.5 to 21.7%); D1 122 (13.6 to 22.2%); S1 298; P2 0; D2 0 | `need_tests.csv`, `tests.csv` |
| ISS, P1 counted tests | 78 outside by a recorded value; 55 cannot be placed | `scenario_tests.csv`, `need_tests.csv` |
| Gravity | `microgravity` for 1,824 of 1,824 tests, as a constant of each of the 14 tables | `tests.csv`; `values_long.csv` (`source_column` "(constant in sources.json)"); `pipeline/spec/sources.json` |
| Oxygen columns of the P1 counted tests | `Calibrated  initial O2 % by vol` (PSI-25, 125 tests); `Percent O2 (Note 1)` (PSI-99, 8 tests) | `data/pipeline/values_long.csv` |
| Mapped tests | 1,824 rows, 12 investigations, 14 tables | `tests.csv` |
| BASS-II pressure | document only: 129 tests in scope, 125 counted (P1) | `need_gap_states.csv` |
| Files naming the 26 tests | 398 files; 104,358,456,350 bytes (0.7746%); 316 files, 86,853,632 bytes; 82 files, 104,271,602,718 bytes. For the 17 FLEX tests: 299 files, 24,954,842,492 bytes, by `lunar_links.py` (label in the file name and PSI folder) | `prototype/lunar_links_PSI-69.json`, `lunar_links_PSI-159.json`, `lunar_summary.json` |
| Labels in the name | identifier 296 (FLEX 197, CFI-G 99); FLEX test number 102 | same |
| Second label | 336 / 47 / 15 (FLEX: 142 + 95 agree, 47 name no test, 8 + 7 name another test; CFI-G: 99 agree) | same |
| The other prototype count for the same 17 FLEX tests | 322; 24,957,498,055 bytes; two labels agree 237, one label 47, labels disagree 38. It is 23 and 2,655,563 bytes more than the count above, by another rule: `flex_two_label.py` also takes a file in when only its PSI folder number names one of the 17 tests, and it adds the tests up, so 322 counts pairs of a file and a test, not files. Recounted on the saved listing: 307 distinct files (24,955,424,694 bytes); the 15 files of FLEX-20 in the folder named after FLEX-21 are counted for both tests (2,073,361 bytes), and 8 files named after identifier `264F003` come in through the folder `Flex-022` (582,202 bytes). The check of step 3 decides which rule the pipeline uses. Its state name for two agreeing labels is `confirmed`, a word of `forbidden_words`; it becomes `two_labels_agree` when step 3 lands | `prototype/flex_two_label.json` (`lunar_17`), written by `flex_two_label.py`; recount `pmpart/fix/two_counts.py` on the design job's `out/files.csv` (not in the repository) |
| The nine CFI-G tests inside the ranges | 7 with an S1 row and `objective_link` `not_stated`; 2 without a row (`CFIG-N-21106F2`, `CFIG-N-21106F5`: no burn time, a dash for how the flame ended) | `need_tests.csv`, `tests.csv`; `data/psi/experimental_tables/PSI-159_Experimental table_CFI-G_Normal Flames.csv`, rows 37 and 40 |
| Flight Platform field of the PSI record | `International Space Station (ISS)` for 11 of the 12 mapped investigations; `Cygnus Spacecraft` for PSI-99; filled in 21 of the 24 records | field `Comment[Flight Platform]` of `i_Investigation.txt` in the 24 metadata archives of step 10 (`psi_metadata_summary.md`; archives in the pm session's scratch folder, not in the repository) |
| Extinction diameter in NASA's table, 17 tests | number above zero 4; zero 2; blank 8; dash 3 | `tiers/testsheets_vs_table.json` (design job), re-tabulated by this job |
| FLEX-23 test sheet | 735 bytes; `Dext  (mm) = 1.32`; table cell blank | `tiers/testsheets_read.json`, `tiers/dl/testsheets/FLEX-023.head.txt` (design job) |
| Test sheets read | 17 files, 15,369 bytes; 11,871 bytes read | `tiers/testsheets_read.json` (design job) |
| Summary PDFs | 11 files, 2,451,356 bytes, 10 tests; two groups of 260 and 110 files, 64,279,279 and 36,061,618 bytes; one sample opened in each | `lunar_summary.json`, `lunar_links_PSI-69.json`, `pipeline/spec/raw_columns.json` |
| Archives of the 17 tests | 47 files, 24,923,186,032 bytes; 3 directories read, 370,662 bytes requested | `lunar_links_PSI-69.json`; `tiers/zip_lunar_FLEX19.json` (design job) |
| Flow speed, FLEX | not in sampled files; 4 unopened document groups, 32 files, 14,424,058 bytes; one entry of four nozzle-speed headers seen in one opened file and not mapped (unit written as N/A) | `data/pipeline/gap_states.csv`; `raw_columns.json` (`unopened_groups`, `related_columns_not_mapped`) |
| FLEX test sheet group | 272 files, 250,375 bytes; 1 sample file opened in the header survey | `raw_columns.json` |

The files named `tiers/...` are in the design job's scratch folder on the pm session's computer and are not in the repository. Step 4 replaces them with `raw_values.csv` and `raw_values_effect.json`.

The rules of section 0 (no digit in a template, no banned whole word in a template or an example) were checked by `pmpart/check_wording.py`, in the same scratch folder as `pmpart/verify_numbers.py`: after the corrections of section 14, 53 templates and 31 example lines, no finding.

---

## 14. Corrections of 15 November, about 01:40 KST

A second AI session checked this file against the repository. A third AI session (pm role) checked each point in its source (`pmpart/fix/confirm.py` and `pmpart/fix/two_counts.py`, read-only) and corrected the file. Read by a person: none yet.

| Section | What was wrong | What it says now | Checked in |
|---|---|---|---|
| 5.2, 6, P1 example | "This gap is a missing test, not unprocessed data", and the replacement "a test that PSI's tables do not hold", say or imply that a test was not done or should be done. | "This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of {listing_date})." Section 6 is renamed. | the lead's wording for pile 3 (decision row of 11/15 00:35 and the design's decision 1) |
| 4.4 | One reason was given for all nine CFI-G tests. | Two reasons with their counts: 7 by the purpose of the record, 2 with no outcome in NASA's table. | `need_tests.csv` (7 rows `not_stated`, 2 tests without a row); NASA's table, rows 37 and 40 |
| 8.2, 3.2 (lower shelf) | "not seen in any file opened so far" for flow speed, although four nozzle-speed headers were seen and rejected. | "no header in the files opened so far was accepted for it", with the headers that were seen and not mapped. | `raw_columns.json`, PSI-69, `related_columns_not_mapped` |
| 5.1 | The ground named no document, and the second sentence said the challenge statement "says the same of PSI as a whole". | The ground adds the Flight Platform field of the PSI record (ISS for 11 of the 12 mapped investigations, Cygnus spacecraft for PSI-99); the second sentence says what the reference item says. | the 24 metadata archives of step 10; `references.json`, item `CH.partial_gravity` |
| 0 (F3), 13 | The prototype folder holds two counts for the 17 FLEX tests (299 and 322), and nothing said why. | Both are named with their rules; 322 counts pairs of a file and a test (307 distinct files). | `lunar_links_PSI-69.json`, `flex_two_label.json`, recount on the saved listing |
| 11, 12 | Two notes described the log's entry for the data role's work by who had not looked at it. | They say who did and recomputed the work: AI agents. | `compliance/AI_USAGE_LOG.md`, row of 11/14 19:40-21:20 |
