# Pipeline: PSI raw tables → fire-safety information needs

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. The spec files are drafts and have not been reviewed by a combustion expert.*

The pipeline starts from the question side: six questions about spacecraft fire safety that the team wrote from the documents in `spec/references.json` (no fire-safety engineer was asked), each with the variables a test must hold to be counted for it. The list of six is the team's construction, not a NASA list; the section "What is the team's own" says which parts the documents back. The pipeline then checks every NASA PSI experimental table against that list. It links tests to questions; it does not answer the questions and draws no conclusion from the values.

```
spec/needs.json      6 fire-safety questions written by the team (prevention, detection, suppression)
        │             each need = required condition variables + any-of outcome variables + scope
spec/references.json standards, requirements, stated objectives and published results each need rests on (66 documents)
        │
spec/coverage.json   bin edges of the coverage grid (oxygen, pressure), placed around named atmospheres
        │
spec/scenarios.json  crewed environments (ISS cabin, lunar habitat) as ranges of oxygen, pressure, flow and gravity
        │
spec/materials.json  one id per material; the names each table uses for it
        │
spec/indicators.json what is computed per need from the linked tests: variable, filter, grouping; three fixed templates
        │
spec/variables.json  standard variables, units, valid ranges, derived formulas
        │
spec/sources.json    22 PSI tables: source column → standard variable → named rule
        │
run.py               1 ingest → 2 standardize → 3 validate → 4 derive → 5 assess → 6 export
rules.py             the named cell rules (unit factors, text-with-unit, BASS material and flow)
```

Run: `python3 pipeline/run.py` (after `python3 scripts/fetch_psi.py`) writes every output except the validation report; `python3 pipeline/check.py` then recomputes them and writes `validation_report.json`.

## Outputs (`data/pipeline/`)

| File | Content |
|---|---|
| `tests.csv` | One row per test, all standard and derived variables, flags, source file and row |
| `values_long.csv` | One row per value, with the source column it came from |
| `capability_matrix.csv` | Need × source: how many tests meet the required conditions and hold an outcome; status; `required_documented_not_in_table` names a required condition that is met by a document and has no value in the table |
| `need_tests.csv` | For each need, the tests that meet its required conditions and hold an outcome, with `objective_link` |
| `coverage_grid.csv` | Recorded tests per fuel phase, oxygen basis, oxygen bin and pressure bin; `not_recorded` is its own bin |
| `scenario_tests.csv` | Scenario × test: whether the recorded oxygen, pressure, flow and gravity fall in the scenario ranges; match tier |
| `scenario_needs.csv` | Scenario × need: counted tests (column `usable_tests`) by match tier, investigations, status, and gap codes |
| `indicators.csv` | Per need and group: count, min, median, max of a recorded variable, with the indicator's reading and reference items |
| `indicator_tests.csv` | The tests behind every indicator row |
| `objective_links.csv` | Need × investigation: every link of `needs.json` (`stated_by`) with the sentence of the PSI record where there is one, the reference item that holds the purpose sentence, its quote, and the verdict |
| `need_references.csv` | For each need, the reference items (criterion text, values, document, section, URL) |
| `run_report.json` | Row counts, flags, unmapped source columns, fill count per variable |
| `atmosphere_cells.csv` | Oxygen bin × pressure bin × need: the columns of `scenario_needs.csv` for the 20 cells of the coverage grid, plus `o2_bin` and `pressure_bin` |
| `evidence/scenario_<id>.json` | Evidence package of a scenario: per need, counts by match tier, the matched tests with values and source columns, indicators over the matched tests, gaps, fixed sentences, references |
| `evidence/cell_<o2_bin>__<pressure_bin>.json` | The same package for one cell of the coverage grid |
| `evidence/index.json` | The list of packages (scenarios in spec order, then cells in bin order) with ranges and status per need |
| `investigation_facts.json` | Per investigation (24): tables, test rows, recorded range or value counts of every variable, linked needs with the record sentence, the purpose sentence and the verdict, counted tests per need, flags, unmapped columns, and fixed sentences filled with these numbers (`facts.py`, templates in `spec/fact_statements.json`) |
| `findings.csv` | One row per published finding: an entry of `spec/findings.json`, that is a reference item (or one row of it) with the needs it is about, its kind (result, criterion, gap, caveat), the conditions the item itself states (oxygen, pressure in kPa and as written, gravity level, flow, fuel phase, material), and the item's text, quote, place and document with its access level, copied unchanged (`findings.py`; see "Published findings") |
| `findings_by_environment.json` | For each scenario and each need: the published findings in three lists (`at_environment`, `about_a_stated_condition_of_the_environment`, `general`) with what matched, the counts, and fixed sentences; `findings` holds each entry once (`findings.py`, rules and templates in `spec/findings.json`) |
| `answers/<scenario_id>__<need_id>.json`, `answers/index.json` | Answer file of one scenario and one need (6 × 6 = 36): what is known and how well, as a rule-chosen top line, the frame (criteria and questions of NASA documents) and four rungs: recorded at the condition, recorded near it, published, not known; every sentence is a template of `spec/answers.json`. `index.json` lists the files with their top line and the number of entries per rung (`answers.py`; see "Answer files") |
| `validation_report.json` | Result of `python3 pipeline/check.py`: every output recomputed from the raw tables and the spec rules by code that does not import the engine |
| `raw_inventory.json` | Per investigation (24): what the PSI file listing names, without any file being downloaded: files and bytes per PSI category (names as PSI gives them) and per kind (video, still image, archive with what its name states, table named as sensor, telemetry or data, experimental table, document, document table, other), the extensions and the largest file name of each kind, id patterns carried by the raw file names, and one fixed sentence filled with these numbers (`raw_inventory.py`, rules and template in `spec/raw_kinds.json`) |

Raw-data inventory. `raw_inventory.json` answers "what does the archive hold for this investigation?" from the PSI file listings alone. It is written by `python3 pipeline/raw_inventory.py`, which is separate from `run.py` and is not covered by `check.py`. The script reads the listings saved in `data/psi/file_listings/` (`--offline`, the default when they are there) or fetches them again with the public listing call that `scripts/fetch_psi.py` uses (`--refresh`); the fetch date is kept in `data/psi/file_listings/_fetched.json` and copied to `_meta`. That folder is in `.gitignore`, so on a fresh clone the script fetches the listings first. The script never downloads a data file. Its limits: the kind of a file is decided from its name and its PSI category only, by the ordered rules of `spec/raw_kinds.json`, so a kind says what the name says and not what the file holds; a file whose name carries no mark is `other`, and an archive whose name does not state its content is counted as "not stated in the name"; a listing says nothing about the content or the quality of a file; sizes are the bytes PSI reports, and the sentences use decimal units (1 GB = 10^9 bytes); rows that a listing repeats for the same file id are counted once (`listing_rows` and `repeated_rows` keep the difference); the id patterns state what the file names show and are not mapped to rows of an experimental table.

Status in the capability matrix: `measured`, `partial` (an outcome exists but a required condition is missing), `conditions_only`, `none`, `out_of_scope`, `not_test_level` (the table's rows are not individual tests). `measured` is a status name, not a judgement: it says that at least one test meets every required condition (by a value in the table or, for pressure in P1 and S1, by a document about the whole table) and has a value for an outcome variable, not that the question of the need was measured or answered.

## Rules the engine follows

- A value is copied from a NASA source cell, multiplied by a unit factor declared in `sources.json`, or computed by a formula in `variables.json`. The values that are not literally in a cell, and the choices made when reading a cell, are listed below; no other value is added.
- A cell that a rule cannot read stays empty and gets a flag (`variable:reason`). Problems are flagged, not fixed. A number is never taken from a pointer such as "Note 4" or "See Fig. 5"; a cell with several numbers, or a number whose decimal point is unclear ("037 mm"), gives no value.
- Every value keeps its source file, row and column.
- A sentence of a document never becomes a value. Where a need allows a required condition to be met by a document about the whole table (`conditions_documented_ok` in `needs.json`, `documented_elsewhere` in `sources.json`), the test still has no value for that variable: scenario matching, bins and indicators use recorded values only.
- A cell with two oxygen numbers gives a value only where a publication of the investigators names the initial oxygen for that cell; otherwise it gives none. No midpoint or average is computed.
- To add a table, a variable or a need, edit the spec files; `run.py` does not change.

Values that are not literally in a NASA cell, and one case where a cell gives no value. The first four kinds are flagged on the test:

| What | Where | Flag |
|---|---|---|
| One of the two oxygen numbers written in a cell ("21.5 - 21.7"), namely the one a publication of the investigators gives as the initial oxygen (`documented_start` in `sources.json`) | 2 Saffire tests | `o2_pct:range_in_source_start_value_named_in_publication` |
| No oxygen value for a two-number cell that no publication settles ("22.0 to 21.9"); the cell text is kept in `o2_range_as_written` | 1 Saffire-II test | `o2_pct:range_in_source_start_value_not_documented` |
| Material name PMMA where the cell gives only a shape or a thickness (BASS-II ReadMe) | 87 BASS and BASS-II tests | `fuel_material:not_written_in_cell_named_in_readme` |
| Material of the row above where the cell is blank | 2 Saffire-II tests | `fuel_material:blank_in_source_value_of_row_above_used` |
| Shape words ("film", "slab", "rod", "fabric sheet") chosen by keyword from the sample cell | BASS and BASS-II | none; the keywords are in `sources.json` (`sample_keywords`) |
| Constants of a whole table (gravity level, fuel phase, oxygen basis) | `sources.json` `constants` | source column reads "(constant in sources.json)" |

Readings that take a number written in the cell and still involve a choice: a value written with "~" ("~ 21.5", "~ 0") is read as the number (flag `<variable>:approximate_in_source`); a length followed by a note pointer ("~ 10 cm (note 3)") is read as the number (flag `burn_length_cm:see_note_in_source`); the flow at the start of a BASS-II test is the first number of the "Air display" cell, and where the cell says the flow was reduced further ("5 down to ext") the test carries `flow_min_cms:cell_says_flow_went_lower_than_written`.

Rows that are not read: a row with a required cell empty, a row named in `sources.json` as not a test (one maintenance entry in PSI-26), and a row that repeats an earlier row cell for cell (8 in PSI-39, 34 in PSI-107). `run_report.json` lists them.

## Why a test counts for a need

A test is counted for a need when three things hold.

1. **Variables.** The test meets every required condition of the need and has a value for at least one outcome variable. A required condition is met by a value in the table. Pressure, for P1 and S1, may also be met by a sentence of a NASA record or of a paper about the whole table (`conditions_documented_ok` in `needs.json`, `documented_elsewhere` in `sources.json`). The sentence never becomes a value: the test still has no pressure, and `capability_matrix.csv` names the condition under `required_documented_not_in_table`. That a statement about the whole table can meet a condition is the team's rule; no document sets it.
2. **Scope.** The test is within the `scope` of the need. Five of the six needs are limited to solid fuels by the team.
3. **Link.** `needs.json` (`stated_by`) links the investigation to the need with verdict `supported`. A link names a reference item (`publication`; type `stated_objective` or `framework` in `references.json`) that holds, verbatim, a sentence in which the investigators or a NASA project document state the purpose of the experiment. Where the `objective` field of the PSI record names the topic, the record sentence is kept beside it (`field`, `quote`), and the engine checks that it is in the record. The engine stops if the reference item does not exist or has no quote.

| Verdict | Meaning | Counted |
|---|---|---|
| `supported` | the purpose is stated for this investigation | yes |
| `differs` | the investigators give this objective to another flight or another area | no |
| `topic_only` | the record names the phenomenon; the stated purpose of the experiment is not spacecraft fire safety, or no purpose sentence was found in what was read | no |

The verdicts are the team's reading (AI, not checked by a person) of the documents listed in `references.json`. They say nothing about documents that were not read. The link is made from the wording of documents; it does not show that a test can or cannot inform the need.

What the link rule does in the current outputs:

- Saffire. The PSI records of the three flights share two objective sentences. The investigators give the fire-growth objective to Saffire-I and Saffire-III (`SAF16.saffire1`, `SAF16b.saffire13`) and the flammability-limit objective to Saffire-II (`SAF16.saffire2`, `SAF16b.saffire2`). Saffire-II tests are counted for P1 and not for P3; Saffire-I tests are counted for P3 and not for P1.
- Extinction (S1). Six records name extinction in their objective field and are not counted (PSI-10, 20, 21, 23, 39, 68). NASA's project scientists write that the ACME experiments "are primarily focused on energy and environmental concerns" and name BRE (PSI-20) as the one focused on spacecraft fire prevention (`ACME14.focus`, `ACME14.bre`); the Researcher's Guide gives energy conversion as the motivation of FLEX-2 (`RG.flex2`); a paper of the CFI investigators gives liquid-fuel combustion as its motivation (`CFI14.motivation`).
- Combustion products (D1). No objective field names a gas species. BASS-II is linked through the investigators' purpose sentence for the gas measurements (`BASS2TM.products`; the same purpose is in `ICES15.purpose`). The investigators frame the readings as levels of combustion products and completeness of combustion (`ICES19.sensors`), not as detection.

`capability_matrix.csv` and `need_tests.csv` carry `objective_link`: `stated` for a supported link, `not_stated` otherwise. In `capability_matrix.csv` the column `usable_tests` counts the tests that meet rules 1 and 2 whatever the link; the counted tests are those of the rows with `objective_link` = `stated`, and they are what `usable_tests` holds in `scenario_needs.csv`. Tests that meet rules 1 and 2 without a supported link are reported next to the counts as recorded outside the stated objective: in the current outputs the Saffire-I tests for P1, the Saffire-II tests for P3 and the CFI-G tests (PSI-159) for S1.

Indicators of population `usable` are computed over the counted tests. `D2.flow`, `D2.aging` and `D2.mass_loss` use population `in_scope`: the tests of the linked investigations that record the required conditions, with or without an outcome. No indicator uses population `recorded` (every test that meets rules 1 and 2, whatever the link) at present.

In file columns and field names the counted tests are called `usable_tests` and the population `usable`. The names are kept for the other sessions. They mean counted under the three rules above, not that a test can answer the question.

One sentence of the PSI-25 record is the record sentence of the links for P1, P2, P3 and S1. The BASS-II tests with an event word beside the flow settings are counted under both P1 and S1, and the BASS-II tests counted for D1 are also counted for P1. Counts of different needs must not be added.

Each need has a `reading`: what a counted test records and what the count does not mean (for example, a test counted for "Extinction conditions" records how the burn ended, which may be disruption or completion and not extinction). It is shown wherever the count is shown.

### What is the team's own

The six needs are the team's construction (AI draft), not a NASA list. `needs.json` (`_meta.authorship`) gives the reference items for each point below.

- The list of six. The documents give three or four areas (`CP2003.groups`, `TM217036.areas`, `TB008.areas`) and, under them, lists of questions that cut differently.
- The split of prevention into flammability limit, ignition, and flame spread and growth. The documents join them in single items (`CP2003.prev.o2flow`); the split follows the BASS-II goal sentence (`ICES19.goal`).
- P2 as a need of its own. The separate ignition items of the documents are about ignition sources and mechanisms (`CP2003.prev.ignition`, `CP2004.flam.q8`); for a material they name a time to ignition and a critical heat flux, not an energy (`RG.ignition`, `CP2004.flam.fist`).
- P3 under prevention only. The documents list flame spread under material flammability and under response (`CP2003.roadmap.spread`, `CP2003.resp.spread`).
- S1 as "extinction conditions" with three routes, under suppression only. The oxygen limit is stated under prevention and under suppression (`CP2003.roadmap.limit`, `CP2004.supp.q3`).
- D1 under detection only. The documents place combustion products under detection, under crew exposure and response, and under post-fire monitoring (`TM217036.signatures`, `3001.V2-6024.rationale`, `SMT.gap.postfire`).
- D2 as a need at all, and the split of detection into gases and smoke. No document read states "smoke generation conditions" as a need; what is stated as needed is the particle size of smoke and the response of detectors (`SMT.gap.detection`, `SAME12.need`). D2 is the team's index of the SAME test conditions.
- The scope "solid" of five needs. The documents tie the limiting oxygen of liquid fuels to spacecraft fire safety (`TP216046.loi`, `RG.droplet`).
- Which variables are required and which useful: flow for P1, oxygen for P3 and heating for D2 are named by the documents as governing variables and are listed as useful.
- Outcome variables with no document behind them: the burn time and the oxygen consumed for P1, the burn time for P3, the CO/CO2 ratio as a quantity of the detection need (`BASS2TM.coratio`), and `hot_ignition` as a name.
- The verdicts of the links and the rule that only `supported` links are counted.
- The rule that a required pressure may be met by a document about the whole table.

What the documents back, as worded: the three areas; the P1 question in its two variables, limiting oxygen and flow for a material (`CP2003.roadmap.limit`, `TM217036.threshold`, `ICES19.minimum`); the P3 name and question (`SAF16.saffire1`, `BASS2TM.growth`); the three routes of the S1 question taken one by one (`CP2004.supp.q3`, `FLEX.objective2`, `CP2003.resp.passive`); the D1 name (`CP2004.det.products`).

`needs.json` also lists areas named in the reference items that the mapped tables cannot address (`not_covered`), and says which PSI records contribute no counted test and why (`not_counted_but_fire_safety`; the table is at the end of this file).

## Indicators

`indicators.json` declares what is computed for each need. The engine has three templates (`summary`, `count_by`, `count`); the spec only chooses the variable, the filter and the grouping, so no number comes from anything but recorded values. Each indicator carries a `reading` that says what it does not mean (for example, the lowest oxygen tested is not a flammability limit), the reference items that define the concept, and, where the investigators published a result for the same investigation, a `compare_with` pointer. The pipeline does not make that comparison.

## Scenarios

A scenario is a set of ranges (`scenarios.json`), not a prediction. A test is marked `in`, `out` or `not_recorded` for each variable. Tier `atmosphere` means oxygen and pressure are both recorded and inside the ranges; `oxygen_only` means oxygen is inside and the table records no pressure. Status per need: `in_atmosphere`, `oxygen_only`, `pressure_only`, `other_atmosphere`, `not_measured`, and `atmosphere_not_specified` for a scenario that sets no oxygen and no pressure range. The status names are kept for the other sessions and say less than they seem to: `in_atmosphere` says only that at least one counted test has oxygen and pressure inside the ranges, whatever its fuel, flow, gravity or added gas; `not_measured` says that the need has no counted test (P2 and D2 in the current outputs). Gap codes say which variable (oxygen, pressure, flow, gravity) has no usable test in range or is not in the table. "Not recorded" always means that the experimental table holds no value; where a NASA record or a paper of the investigators says something about the missing variable, the sentence is carried next to the gap (`documented_elsewhere` in `sources.json`) and is never used as a value; for P1 and S1 it can meet the required pressure condition (see "Why a test counts for a need"). Each test is also marked for carbon dioxide or helium added to the atmosphere (`added_gas`); the mark does not change the tier. A scenario can point to records or table cells that name its atmosphere and are not in the counts (`see_also`). All PSI tests in the tables are microgravity tests, so a lunar or Martian scenario always carries a gravity gap.

## Evidence packages

`evidence.py` (called at the end of `run.py`) writes one JSON file per environment to `data/pipeline/evidence/`, so that a reader, a page or a language model can be handed everything recorded for one environment without joining the tables. An environment is a scenario of `scenarios.json`, or a cell: one oxygen bin × one pressure bin of `coverage.json` (5 × 4 = 20; `not_recorded` is not an environment). A cell is matched exactly like a scenario whose oxygen and pressure ranges are the bin edges, with no flow range and no gravity level. `atmosphere_cells.csv` is `scenario_needs.csv` for the cells. The cells do not appear in `scenario_tests.csv` or `scenario_needs.csv`.

A package holds `environment` (label, ranges with their inclusive flags written out, `null` for a range the environment does not set, gravity level, basis items, note, `see_also` pointers, and `recorded_tests`: every test matched to the environment per investigation and fuel phase, whatever need it is counted for) and one block for each need:

| Field | Content |
|---|---|
| `status`, `counts` | The values of the environment's row in `scenario_needs.csv` or `atmosphere_cells.csv` |
| `reading`, `note` | What a counted test of the need records and what the count does not mean; limits of the need (`needs.json`) |
| `objective` | The links of the need (`objective_links.csv`): the sentence of the PSI record where there is one, the reference item with its purpose sentence, and the verdict |
| `matched_by_fuel_phase` | The matched tests per fuel phase |
| `documented_elsewhere` | Sentences of a PSI record or a paper about a variable the table does not hold; never a value |
| `investigations` | Usable tests per investigation and tier, with the investigation title from the PSI record |
| `matched_tests` | The usable tests of tier `atmosphere`, `oxygen_only` or `pressure_only`: match marks, flags, source file and row, and the recorded values of the need's variables, each with unit and source column (the same origin as `values_long.csv`) |
| `usable_elsewhere` | The usable tests of tier `other`: how many, and the lowest and highest recorded oxygen and pressure (`null` where none is recorded). Oxygen counts ambient values only; `not_ambient` counts the others |
| `indicators` | The need's indicators recomputed over the tests of their population that are matched to this environment; one entry per indicator and group, with `template`, `population`, the values and the test ids. An indicator with no such test is left out |
| `gaps` | The gap codes of the row, each with its sentence |
| `statements` | Fixed sentences filled with the numbers of the block: status, need-level counts, gaps, then one per indicator entry (these carry `indicator_id` and `group`) |
| `references` | The need's reference items with document title, version, URL and access |

Rules:

- One code path. Status and counts are the rows that `match_environments` in `run.py` returns, which are also what is written to the two CSV files. After writing, `evidence.py` reads the files back and stops the run if a package and its CSV row differ, or if the tests listed in a block do not add up to its counts.
- No text in the code. Every sentence, the cell label and note, and the package `_meta` are templates in `spec/statements.json`. `{field}` is replaced by a field of the block and `[field|one|many]` chooses a singular or plural form; `when` is a list of `[field, operator, value]` conditions with the operators of `OPS` in `run.py`. The fields are listed in the spec. A template that names a field the block does not have, a field that is empty where the sentence is used, or a status, gap code or indicator with no sentence stops the run.
- The sentences say what was recorded and what was not, with the number of tests and the unit. They do not judge a material, an atmosphere or the amount of evidence. Tests recorded outside the stated objective are reported as not counted. An indicator sentence names the population it is computed over.
- "Matched" means tier `atmosphere`, `oxygen_only` or `pressure_only`. The flow and gravity counts cover tiers `atmosphere` and `oxygen_only` only, as in `scenario_needs.csv`.
- Reading the cells: a test that records oxygen but no pressure has tier `oxygen_only` in all four pressure bins of its oxygen bin (and a test with pressure but no oxygen has `pressure_only` in all five oxygen bins), so those counts repeat along a row or column and must not be summed over cells. Only tier `atmosphere` places a test in exactly one cell.
- The files are deterministic: fixed key order, tests sorted by investigation number and test id, no timestamps. A package whose environment is no longer in the specs is deleted on the next run.

## References

`references.json` lists each document with the items taken from it: requirements, acceptance criteria, definitions, exposure limits, design values, knowledge gaps and published results. Each item records where in the document it is, and how the document was read (`full_text_read`, `abstract_only`, `cited_not_read`, `read_from_copy`, `read_by_teammate`). The pipeline does not compute with these values and does not judge any test against them. Some documents were read as an abstract only, through a citation or from a copy; `need_references.csv` and the evidence packages carry the `access` value of every item. Crew exposure limits (SMAC) were established for human spaceflight (`SMAC.scope`); the pipeline does not compare a sensor reading of an experiment with them.

## Published findings

`spec/findings.json` and `findings.py` make the items of `references.json` retrievable by environment and by need, so that an answer about an environment can say "not in the PSI tables; a document reports ..." and give the quote and its source. The layer stands beside the engine: `findings.py` does not import `run.py` and is not imported by it, nothing of it enters the counts, tiers, statuses or indicators, and `check.py` recomputes its lists and compares every text and quote with `references.json` (checks L1 to L4).

What it is. An entry of `spec/findings.json` points to one reference item, or to one row of an item that states several condition sets (211 entries from 180 items in the current files). An entry adds tags only: the needs the item is about (`P1` to `D2`, or `general`), a kind (`result`, `criterion`, `gap`, `caveat`) and the conditions. The text, quote and place of the item are copied unchanged into the outputs, with the access level of the document, so a statement from a document that was not read in full text is always shown as such. Tagged are the items of type `published_result`, `knowledge_gap` and `limitation` (those left out are listed with the reason under `_meta.left_out`) and those definitions, requirements, criteria, design values and recommendations that state how fire or smoke behaves or what a test requires in a condition.

The attachment rule. A condition (oxygen, pressure, gravity level, flow, fuel phase, material) is attached to an entry only if the item states it in its own `text`, `quote` or `values`, as a number or as an explicit word. The `note` of the item, its `where` and the title of the document are not used. A condition that is not stated is absent; absent does not mean any. Words without a value that can be compared ("elevated oxygen", "reduced pressure", "low gravity") are copied under `condition_words` and no number is supplied for them. An oxygen number that is a reported limit (LOI, ULOI, MOC) is a result, not the atmosphere of a test, and is not normalized as oxygen. Pressure is normalized to kPa with fixed factors (1 psi = 6.894757 kPa, 1 atm = 101.325 kPa) and the item's own words are kept in `pressure_as_written`. `condition_basis` gives, for every normalized condition, the exact words or the `values` key that state it. `findings.py` stops if an item does not exist, if words given as basis are not in the item, if a normalized number is not literally in its basis (for a pressure: a number of the as-written words times the factor of its unit), if a gravity level or a fuel phase has no word of the vocabulary behind it, or if an item of the three types above is neither tagged nor listed as left out.

The three lists, for each scenario of `scenarios.json` and each need (the full rule is in `spec/findings.json`, `_meta.lists`, and is copied into the output):

| List | Rule |
|---|---|
| `at_environment` | The entry states an oxygen and a pressure and both are inside the scenario's ranges (with their inclusive flags). If the scenario sets a gravity level and the entry states a different one, the entry is not listed; it is recorded under `other_conditions.moved_for_gravity` with the reason. An entry that states no gravity level stays, with `gravity_level` under `not_stated` |
| `about_a_stated_condition_of_the_environment` | The entry states at least one of oxygen, pressure and gravity level inside the scenario's range (or as a range that overlaps it, marked `overlaps`; or the same gravity level), and none outside. An entry that states partial gravity is taken as about a lunar or Martian scenario and marked `finding_states_partial_gravity` |
| `general` | The entry has no normalized oxygen, pressure or gravity level: criteria, gaps and caveats that apply as written. Where it names a condition in words, it carries `states_conditions_in_words` |

Everything else is counted under `other_conditions` and not listed. Each listed entry carries `matched_on` (the conditions that matched, with the entry's own value and words) and `not_stated` (the scenario's conditions the entry does not state). Entries tagged `general` are under the key `general` of each scenario and are not repeated under the six needs. Each block has two fixed sentences filled with its counts (templates in `_meta.sentences`); `findings.py` stops if a sentence holds a word of `_meta.forbidden_words`.

Rebuild: `python3 pipeline/findings.py`. It reads `spec/findings.json`, `references.json`, `scenarios.json` and `needs.json`, needs no raw data and no other output, and writes the two files; the same input gives the same bytes.

Limits:

- The entries are quotes and paraphrases of documents, not results of the pipeline. They were not checked against the PSI tables or the raw data, and no test is counted or matched because of them. Some describe tests that the PSI tables also hold (the Saffire-I to -III and BASS-II test conditions); they are what a document says about those tests.
- Every tag (needs, kind, conditions, the words given as basis, which items are included) comes from an AI reading of the items of `references.json` and was not checked by a person. Entries where the tagger was unsure, or made a choice, carry `unsure` in the spec (`tagging_note` in the output).
- A finding at the environment's oxygen and pressure may still differ from it in material, scale, gravity level or flow. The entry shows what the item states and, under `not_stated`, what it does not: the Saffire IV to VI test conditions (`SAF456.conditions`) state no gravity level in the item, so they can be listed for the lunar scenario; the pressures of `H2006.pressures` and `H2007.fixedpressure` are listed without a gravity level, which text and quote of these items do not state (the notes of `H2006.depends` and `H2007.fixedpressure` say normal gravity).
- The lists say which statements name the conditions of an environment. They do not say what happens in the environment, and a limit or a result is not carried from the condition where it was stated to another one.
- The check on wording covers the template sentences. The quotes are carried verbatim and some contain words the sentences avoid ("safe", "sufficient").
- Items of type `stated_objective` and `framework` are not tagged, even where their quote states fire behaviour (for example `WP21X.atmosphere`, `TM217036.threshold`); items of type `operational_practice`, `monitoring_range` and `exposure_limit` are not tagged either.

## Answer files

`answers.py` writes one file per scenario and need to `data/pipeline/answers/`: what is known for this environment and this need, and how well. It is a post-processing step like `facts.py`: it reads the evidence packages, `atmosphere_cells.csv`, `scenario_needs.csv`, `findings.csv`, `findings_by_environment.json` and the specs, imports none of the other scripts, and recomputes no count, status, gap or indicator. Every text and rule is in `spec/answers.json`. `check.py` recomputes the near cells, the placement of every entry, the top line and the numbers of every sentence (checks M1 to M7); the same checks are also inside `answers.py` and stop the run.

| Part | Content |
|---|---|
| `top_line` | One line chosen by rule, starting with "Not judged here." |
| `frame` | How NASA documents treat the question: the published findings of kind `criterion` (`criteria`) and those of kind `gap` that are a quoted question or research need of one of the NASA documents listed in the spec (`nasa_questions`) |
| `rung1_recorded_at_the_condition` | The block of the evidence package for the need, copied: status, counts, matched ranges, indicators, and the package's status, tier, matched, flow, gravity and documented sentences |
| `rung2_recorded_near_the_condition` | The neighbouring cells of the coverage grid that hold a matched counted test of the need, each with the counts of its row in `atmosphere_cells.csv`, the recorded ranges of its package, and a sentence that says how its condition differs from the one asked |
| `rung3_published` | The published findings of kind `result` and `caveat`, in the three lists of `findings_by_environment.json`: at the environment, about one of its stated conditions, stated without these conditions |
| `rung4_not_known` | The gap codes of the package with their sentences; the other findings of kind `gap` (`stated_open_elsewhere`); the areas of `needs.json` `_meta.not_covered` (they carry no need id, so all are listed for every need and marked general); the dated searches with no result (`searches` in the spec) |
| `sentences` | Every sentence of the file in reading order, with rung, id and sources |

Rules:

- Placement. Every finding that `findings_by_environment.json` lists for the scenario under the need or under `general` is placed exactly once, by its kind. Entries from `general` carry `applies: general`. Each entry carries the item's `text`, `quote` and place, the document with its access level, the stated conditions as in `findings.csv`, `matched_on`, and `row_values`, `item_note` and `tagging_note` where they exist. `answers.py` stops if a `text` or `quote` differs from `references.json`.
- No arithmetic on a published value: no difference, average, interpolation or trend. The only numbers made here are counts of the entries of a list. A published statement is never added to a count of tests and never changes a status or a gap; rung 1 is checked against `scenario_needs.csv` and stops the run on a difference.
- Near (`near` in the spec). The scenario's cells are the cells (oxygen bin × pressure bin of `coverage.json`) that its oxygen and pressure ranges intersect, with the inclusive flags. A candidate is a cell that is not a scenario cell and is one step from a scenario cell in the oxygen bin order with the same pressure bin, or one step in the pressure bin order with the same oxygen bin. A candidate is listed for a need if its row of `atmosphere_cells.csv` has at least one test of tier `atmosphere`, `oxygen_only` or `pressure_only`. A scenario without both ranges (the Mars habitat) has no cells, and the rung says so. Tier `oxygen_only` repeats across the pressure bins of an oxygen bin, so a cell that differs from the environment in pressure only can hold the very tests of rung 1: each cell gives `also_matched_at_the_condition` (the number of its matched test ids that are also matched to the scenario), the rung says once that counts of cells are not to be added, and nothing is summed across cells.
- Top line (`top_line` in the spec). The fixed start, then the first sentence of `tests` whose condition holds (one per rung-1 status), then the first of `published` (rungs 1 to 3 hold nothing for the condition; no result or caveat at or about the environment; some). It states counts only: counted tests by tier, results and caveats at the environment and about one of its conditions, and that what has not been found is listed. It gives no value of a test or of a publication.
- Wording. A template holds no digit and none of `forbidden_words` (safe, acceptable, sufficient, adequate, recommended, proves, confirms, representative, flammable, dangerous and their variants), checked as whole words on the templates and on the filled sentences. Quotes and item texts are fields of an entry and are never merged into a sentence. A placeholder that is not a field of the block stops the run, and so does a sentence with a number that is not found in the block it was built from.
- The files are deterministic: fixed key order, findings sorted by reference id, item id and row, cells in bin order, no timestamps. A file in `answers/` that the run did not write is removed.

Rebuild: `python3 pipeline/run.py`, then `python3 pipeline/findings.py`, then `python3 pipeline/answers.py`.

Limits:

- An answer file is not a judgement of a material or an atmosphere and not a prediction for a condition without a test. It says what the sources hold.
- Rung 2 is not evidence for the condition: a test in a neighbouring cell was recorded at another oxygen or pressure, and the cells are wide bins chosen by the team.
- Rung 3 and the frame are quotes, tagged by an AI reading that no person checked. An entry made from one row of an item carries the `text` of the whole item; its own values are in `row_values`. A statement at the environment's oxygen and pressure may differ from it in material, scale, flow or gravity level.
- The lists of NASA questions are from the dates of their documents and do not say what NASA considers open today. Which documents count as NASA question lists is the team's choice (`placement.nasa_questions` in the spec).
- "Not found in these sources" means the mapped PSI tables and the documents of the reference list, not that no test or document exists.

## Checking

`python3 pipeline/check.py` recomputes every output from the raw tables and the rules written in the spec files, with code that does not import `run.py`, `rules.py`, `evidence.py` or `facts.py`, and writes `data/pipeline/validation_report.json`. `python3 pipeline/check.py --spot-check` writes `reports/spot_check.csv`: up to 20 values per table (268 rows; row 1 is the header) with the raw cell, for a person to compare with the NASA page. The check on wording covers the template sentences; readings and notes copied from the spec files are not scanned. The raw tables are compared with the manifest by size, not by hash.

## Limits

- Only the experimental tables (layer 2 of PSI) are mapped. Publications, analyzed data and raw data are not.
- Eight tables are not test-level and are listed in `sources.json` with the reason. Two of them belong to investigations whose records name exploration atmospheres (PSI-20) or list days at about 30% oxygen (PSI-23); scenarios point to them under `see_also`.
- A "test" is one row of a NASA table. In SAME-R (PSI-101) 42 of the 109 rows are a second reading of the same smoke after aging; in SPICE (PSI-107) a row is one flow setting of a flame. In SAME (PSI-102) four rows say "same conditions as 1-4" for four more materials and are not read.
- Results written as text are not carried: the 1-g columns of Saffire-II ("Complete" in normal gravity next to "~ 0" in microgravity), the comment columns of CFI-G, the fan-display notes of BASS-II other than the event word.
- Pressure of the solid-fuel tests. The BASS-II and Saffire experimental tables have no pressure column, so no counted test of P1 records a pressure. Pressure and gravity level are required variables of P1, and pressure of S1, because the cited definition of an oxygen threshold holds at a given total pressure, flow and gravity level (`ISO16697.scope`) and the one sentence found that states S1 names oxygen and pressure (`CP2004.supp.q3`). The condition is met by a document, and what the documents say sets what may be written:
  - BASS-II: the investigators state "Pressure was not varied from 1 atmosphere." (`ICES19.pressure`). This is a nominal statement for the investigation, not a reading per test. One section of the Summary Report gives a monitored range of 99.2 to 99.5 kPa for the thin PMMA opposed-flow tests it reports (`BASS2SUM.pressure_range`). The PSI-25 documents that were opened list no pressure reading (`PSIBASS2.measured`, `PSIBASS2.procedure`). Not to be written: a kPa or psia value for each BASS-II test; that the pressure was measured for each test; that the glovebox working volume was at cabin pressure (the facility description says the working volume is held at a negative pressure with respect to the crew living area and gives no magnitude, `MSG.negative`).
  - Saffire-I and Saffire-II: the investigators state "normal pressure (1 atm)" (`SAF17.pressure`); later papers print 100 kPa (`SAF45.table2`) and values at hatch closure (`SAF2PMMA.hatch`, `CNF23.table1`). These are nominal or hatch-closure statements, not readings at ignition. A reading per sample is in the PSI raw data (column "Ambient Pressure", in psia; `PSISAF.pressure_column`), which the pipeline does not map. Not to be written: that the Saffire tests were run at exactly 100 kPa or exactly 1 atm as a measured value; that the pressure was not measured or is not available from NASA.
  - Not to be written for either: that the pressure is missing and the test conditions are therefore unknown. The condition is documented, at the level stated above.
  - Other atmospheres. A paper on the normal-gravity test says that Test 1 "is pass-fail and is only valid at the atmosphere tested" (`ICES14.onlyvalid`; said of Test 1, not of the microgravity tests). No document read carries a BASS-II or Saffire result to another pressure or to an exploration atmosphere, and the pipeline does not: it computes no corrected or converted limit and no oxygen partial pressure for these tests. Not to be written: that a limit found in BASS-II or Saffire applies at another pressure.
  - Not to be written: that flammability limits do not depend on pressure, or depend only on oxygen concentration or only on oxygen partial pressure. The documents read differ on how strongly normal-gravity limits depend on total pressure (`H2006.depends`, `SAE2008.mocpressure`, `LANGE.lesser`), and none says that the dependence is zero.
  - No document read says that BASS-II or Saffire were run under ISO/TS 16697 (`ISO16697.record`). Flow, which the same definition names, is listed as useful for P1: the team's choice.
- Oxygen of the Saffire tests. The value is the oxygen the ISS reported when the vehicle departed, about one day before the tests, carried forward from the measured CO2 production (`SAF17.o2_initial_I`, `SAF17.o2_initial_II`, `SAF17.table1_note_i`, `PSISAF.delay`). It is not a sensor reading at ignition. The on-board oxygen sensor traces in the PSI raw data show other levels (`PSISAF.o2_traces`, read by eye from graphs), and the files do not comment on the difference. The papers do not define the "~" written before most of these values. The PSI-99 table has "~ 21.5" for sample 2-1 where the investigators' table has "~ 22.1" (`SAF17.table1_o2`); the pipeline reads the PSI cell.
- The lunar-habitat scenario counts as "inside" every recorded pressure below 85.8 kPa. The 17 counted tests in its oxygen range are FLEX droplets recorded at 71.2 to 72.4 kPa, that is 1 to 2 kPa above the 70.3 kPa (10.2 psi) of the challenge statement; the only tests at or below 70.3 kPa with 30% oxygen or more are 20 gas-burner tests of PSI-159 at 50.7 kPa (9 at 33.2 to 35.9% oxygen, inside the scenario's 30 to 36% range, and 11 at 36.4 to 39.3%, above it), none of which is counted for a need. The scenario carries this as `caveat`.
- Oxygen and pressure in range say nothing else about a test: the tests recorded in elevated oxygen and reduced pressure are fuel droplets and burner flames in microgravity, some with carbon dioxide or helium added.
- The needs, their required variables, their scope, the verdicts of the links and the rule for documented conditions are a team draft (AI), not a NASA list or standard, and have not been reviewed by a combustion specialist. See "What is the team's own".
- The challenge statement cannot be opened from the work environment of the data role. Its Moon Base bound (oxygen likely 30% or more, pressure 10.2 psi or less) and spacesuit values were checked on the official page by another session of the team on 2026-11-14 (`access: read_by_teammate`); the items give the wording as reported, not a verbatim quote.
- Five of the six needs are limited to solid fuels by the team (`scope`). Of the 1,824 test rows, 1,095 are gas-fuel rows, 353 liquid-fuel rows and 376 solid-fuel rows. Liquid-fuel and gas-fuel rows can be counted for S1 only, and no gas-fuel row is counted for any need. 408 rows are counted for at least one need; they come from four investigations (PSI-25, 69, 98, 99). The documents tie the limiting oxygen of liquid fuels to spacecraft fire safety (`TP216046.loi`, `RG.droplet`); under the team's scope the FLEX tests are counted for S1 only. A record that names a topic for another fuel phase stays outside, for example PSI-10 ("Evaluate whether pseudo-flammability limits can be obtained for these flames").
- The one PSI investigation of an extinguishing agent on solid fuels (PSI-26, BASS) has an experimental table with sample names only. For the extinction need (S1) the counted solid-fuel tests are BASS-II tests with an event word beside the flow settings, and every counted test with added carbon dioxide or helium is a FLEX droplet test. In the FLEX table "extinction" is one of the recorded ways a droplet burn ends, with or without an added gas.
- The ISS ranges are bins, not an ISS operating range: 19 to 23% oxygen and 85.8 to below 116.8 kPa. No reference item gives an ISS operating range for oxygen or pressure. The scenarios below 62.8 kPa accept any recorded pressure below that edge.
- The variables `o2_consumed_pct_points`, `co2_produced_pct_points` and `co_produced_ppm` are differences between a final and an initial sensor reading. The names say "consumed" and "produced"; the values are not amounts consumed or produced by one test, and many BASS-II tests start with a CO reading above zero.
- The SAME and SAME-R tables hold conditions of the smoke tests and no measured smoke property; the particle sizes and detector signals are in the investigators' reports and papers (`SAMEFSR.results`, `SAME.sizes`, `SAME.detector`). The only outcome variable of D2 is the smoke particle size, so D2 has no counted test. The four value rows of the SAME table (PSI-102) carry the values of the planned test matrix of the 2005 requirements document (`SAMEEIRD.matrix`): they are planned test points, and whether tests were flown at exactly these conditions was not verified. The weight loss rate is a target value of that matrix (`SAMEEIRD.target`, `SAME.massloss`) and is listed as a condition; the mass actually lost was determined by weighing and is not in the table (`AST15P.balance`). Not to be written: that the SAME tests were run at 1 or 2 mg/min; that Rt/R0 is the sample temperature (`SAMER.rtr0.limit`). The aging time of D2 merges two source columns, "Aging Duration (minutes)" (SAME) and "Net aging time (sec)" (SAME-R).
- No mapped table column holds an ignition result for a solid fuel, so P2 has no counted test. This holds for the mapped columns, not for the investigations: the BASS-II Summary Report reports ignition delays of PMMA rods (`BASS2TM.igndelay`), which the PSI-25 experimental table does not hold.
- `reports/indicators_ko.json` holds a Korean rendering of the labels and readings for the team's internal page; the English texts in `spec/` are the authority.

## Investigations with no counted test

Four of the 24 PSI records contribute counted tests (PSI-25, 69, 98, 99). The other 20 contribute none. "Linked" means that `needs.json` (`stated_by`) holds a link between the investigation and the need; the verdict of the link is given in parentheses, and only `supported` links are counted. The last column quotes fire-safety wording of the record where there is any; it is a property of the catalogue text, not a judgement of the investigation.

| Record | Linked to (verdict) | Why no test is counted | Fire-safety wording in the record (field) |
|---|---|---|---|
| PSI-10 Flame Design | S1 (topic_only) | link not counted; no column mapped to an outcome variable of S1 | the words "fire" and "safety" do not occur |
| PSI-20 ACME BRE | S1 (differs) | link not counted; table is one row per test day | "BRE yielded important data relevant to spacecraft fire safety." (`researchImpacts`) |
| PSI-21 CLD Flame | S1 (topic_only) | link not counted; table is one row per test day | "an understanding of those factors that affect flame extinction in diffusion flames is critical in the suppression of fires" (`researchImpacts`) |
| PSI-22 E-FIELD Flames | none | table is one row per test day | none: "The E-FIELD Flames research is not being conducted to serve any space applications" (`researchImpacts`) |
| PSI-23 s-Flame | S1 (topic_only) | link not counted; table is one row per test day | the words "fire" and "safety" do not occur |
| PSI-26 BASS | P1, S1 (supported) | table lists samples only: no oxygen column, no outcome column | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-39 CFI | S1 (topic_only) | link not counted; no column mapped to an outcome variable of S1 | "support the design of safer spacecraft systems" (`researchImpacts`) |
| PSI-47 DAFT | none | table is one row per sampling session | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-60 SPICE analysis | none | no experimental table | "the results support safer fire detection, suppression, and cleaner combustion technologies" (`researchImpacts`) |
| PSI-62 flame-spread model | none | no experimental table | "enable accurate prediction of flammability limits for spacecraft materials" (`objective`) |
| PSI-68 FLEX-2 | S1 (topic_only) | link not counted; table is one row per fuel with planned ranges | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-100 Saffire-III | P3 (supported), P1 (differs) | no oxygen column and no outcome column | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-101 SAME-R | D2 (supported) | the table holds test conditions; no column holds a smoke particle size, the outcome of D2 | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-102 SAME | D2 (supported) | the table holds planned test conditions; no column holds a smoke particle size, the outcome of D2 | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-106 SLICE | none | table is one row per test day | "Insights into flame stability and behavior to enhance fire safety" (`researchImpacts`) |
| PSI-107 SPICE | none | rows are flow settings of gas jet flames; outside the solid-fuel scope of D2 | "Fire Safety" (`subResearchArea`); "help design safer spacecraft environments" (`researchImpacts`) |
| PSI-115 SAME data study | none | no experimental table | "This would directly lead to better smoke detection devices" (`researchImpacts`) |
| PSI-117 cool-flame study | none | no experimental table | "Potential to improve spacecraft fire-safety modeling" (`researchImpacts`) |
| PSI-142 cool-flame transitions | none | table is an index of figures in publications | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-159 CFI-G | none | its tests hold the S1 variables and are reported as recorded outside the stated objective | the words "fire" and "safety" do not occur |

Two records that do contribute counted tests also have a link that is not counted: PSI-98 (Saffire-I) for P1 and PSI-99 (Saffire-II) for P3, both with verdict `differs`. Their tests are reported for that need as recorded outside the stated objective.
