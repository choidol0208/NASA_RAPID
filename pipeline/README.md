# Pipeline: PSI raw tables → fire-safety information needs

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. The spec files are drafts and have not been reviewed by a combustion expert.*

The pipeline starts from the question side: six questions about spacecraft fire safety that the team wrote from the documents in `spec/references.json` (no fire-safety engineer was asked), each with the recorded variables a test must hold to be counted for it. It then checks every NASA PSI experimental table against that list. It links tests to questions; it does not answer the questions and draws no conclusion from the values.

```
spec/needs.json      6 fire-safety questions written by the team (prevention, detection, suppression)
        │             each need = required condition variables + any-of outcome variables + scope
spec/references.json standards, requirements and published results each need rests on (22 documents)
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
| `capability_matrix.csv` | Need × source: how many tests carry the required conditions and an outcome; status |
| `need_tests.csv` | For each need, the tests that record its variables, with `objective_link` |
| `coverage_grid.csv` | Recorded tests per fuel phase, oxygen basis, oxygen bin and pressure bin; `not_recorded` is its own bin |
| `scenario_tests.csv` | Scenario × test: whether the recorded oxygen, pressure, flow and gravity fall in the scenario ranges; match tier |
| `scenario_needs.csv` | Scenario × need: counted tests (column `usable_tests`) by match tier, investigations, status, and gap codes |
| `indicators.csv` | Per need and group: count, min, median, max of a recorded variable, with the indicator's reading and reference items |
| `indicator_tests.csv` | The tests behind every indicator row |
| `objective_links.csv` | Need × investigation: the sentence in the PSI record that states the need as an objective |
| `need_references.csv` | For each need, the reference items (criterion text, values, document, section, URL) |
| `run_report.json` | Row counts, flags, unmapped source columns, fill count per variable |
| `atmosphere_cells.csv` | Oxygen bin × pressure bin × need: the columns of `scenario_needs.csv` for the 20 cells of the coverage grid, plus `o2_bin` and `pressure_bin` |
| `evidence/scenario_<id>.json` | Evidence package of a scenario: per need, counts by match tier, the matched tests with values and source columns, indicators over the matched tests, gaps, fixed sentences, references |
| `evidence/cell_<o2_bin>__<pressure_bin>.json` | The same package for one cell of the coverage grid |
| `evidence/index.json` | The list of packages (scenarios in spec order, then cells in bin order) with ranges and status per need |
| `investigation_facts.json` | Per investigation (24): tables, test rows, recorded range or value counts of every variable, stated needs with the record sentence, counted tests per need, flags, unmapped columns, and fixed sentences filled with these numbers (`facts.py`, templates in `spec/fact_statements.json`) |
| `validation_report.json` | Result of `python3 pipeline/check.py`: every output recomputed from the raw tables and the spec rules by code that does not import the engine |

Status in the capability matrix: `measured`, `partial` (an outcome exists but a required condition is missing), `conditions_only`, `none`, `out_of_scope`, `not_test_level` (the table's rows are not individual tests). `measured` is a status name, not a judgement: it says that every required condition and at least one outcome variable has a value in the table, not that the question of the need was measured or answered.

## Rules the engine follows

- A value is copied from a NASA source cell, multiplied by a unit factor declared in `sources.json`, or computed by a formula in `variables.json`. The values that are not literally in a cell, and the choices made when reading a cell, are listed below; no other value is added.
- A cell that a rule cannot read stays empty and gets a flag (`variable:reason`). Problems are flagged, not fixed. A number is never taken from a pointer such as "Note 4" or "See Fig. 5"; a cell with several numbers, or a number whose decimal point is unclear ("037 mm"), gives no value.
- Every value keeps its source file, row and column.
- To add a table, a variable or a need, edit the spec files; `run.py` does not change.

Values that are not literally in a NASA cell. The first three kinds are flagged on the test:

| What | Where | Flag |
|---|---|---|
| One of the two oxygen numbers written in a cell ("21.5 - 21.7"), namely the one a publication of the investigators gives as the initial oxygen (`documented_start` in `sources.json`) | 2 Saffire tests | `o2_pct:range_in_source_start_value_named_in_publication` |
| Material name PMMA where the cell gives only a shape or a thickness (BASS-II ReadMe) | 87 BASS and BASS-II tests | `fuel_material:not_written_in_cell_named_in_readme` |
| Material of the row above where the cell is blank | 2 Saffire-II tests | `fuel_material:blank_in_source_value_of_row_above_used` |
| Shape words ("film", "slab", "rod", "fabric sheet") chosen by keyword from the sample cell | BASS and BASS-II | none; the keywords are in `sources.json` (`sample_keywords`) |
| Constants of a whole table (gravity level, fuel phase, oxygen basis) | `sources.json` `constants` | source column reads "(constant in sources.json)" |

Readings that take a number written in the cell and still involve a choice: a value written with "~" ("~ 21.5", "~ 0") is read as the number (flag `<variable>:approximate_in_source`); a length followed by a note pointer ("~ 10 cm (note 3)") is read as the number (flag `burn_length_cm:see_note_in_source`); the flow at the start of a BASS-II test is the first number of the "Air display" cell, and where the cell says the flow was reduced further ("5 down to ext") the test carries `flow_min_cms:cell_says_flow_went_lower_than_written`.

Rows that are not read: a row with a required cell empty, a row named in `sources.json` as not a test (one maintenance entry in PSI-26), and a row that repeats an earlier row cell for cell (8 in PSI-39, 34 in PSI-107). `run_report.json` lists them.

## Why a test counts for a need

Recording the right variables is not enough to be counted. A test is counted for a need only if a sentence in the `objective` field of the PSI record of its investigation names the topic of the need as something the investigation set out to determine. The sentence is copied into `needs.json` (`stated_by`) and the engine checks that it is in the record. `capability_matrix.csv` and `need_tests.csv` carry `objective_link` (`stated` or `not_stated`). Scenario counts and indicators use `stated` tests; the others are reported next to them as recorded outside the stated objective. Two kinds of indicator are declared exceptions in `indicators.json`: the three D1 indicators use every test that records the variables (population `recorded`), because no record states D1, and `D2.flow` and `D2.aging` use the tests of stating investigations that record the required conditions, with or without an outcome (population `in_scope`).

In file columns and field names the counted tests are called `usable_tests` and the population `usable`. The names are kept for the other sessions. They mean counted under the two rules above (variables recorded, topic named in the record), not that a test can answer the question.

One sentence of the PSI-25 record is the link for P1, P2, P3 and S1, and the BASS-II tests with an event word beside the flow settings are counted under both P1 and S1. Counts of different needs must not be added.

This link is a property of the catalogue text and was made by the team. It does not show that a test can or cannot inform the need. The combustion-products need (D1) has no record that names a gas species as something to determine; the BASS-II CO and CO2 readings are reported as recorded outside the stated objective, with the investigators' own description of the sensor (`ICES19.sensors`).

Each need has a `reading`: what a counted test records and what the count does not mean (for example, a test counted for "Extinction conditions" records how the burn ended, which may be disruption or completion and not extinction). It is shown wherever the count is shown.

The needs themselves are the team's wording. `needs.json` says which parts come from NASA documents, lists areas named in the reference items that the mapped tables cannot address (`not_covered`), and says which PSI records contribute no counted test and why (`not_counted_but_fire_safety`; the table is at the end of this file).

## Indicators

`indicators.json` declares what is computed for each need. The engine has three templates (`summary`, `count_by`, `count`); the spec only chooses the variable, the filter and the grouping, so no number comes from anything but recorded values. Each indicator carries a `reading` that says what it does not mean (for example, the lowest oxygen tested is not a flammability limit), the reference items that define the concept, and, where the investigators published a result for the same investigation, a `compare_with` pointer. The pipeline does not make that comparison.

## Scenarios

A scenario is a set of ranges (`scenarios.json`), not a prediction. A test is marked `in`, `out` or `not_recorded` for each variable. Tier `atmosphere` means oxygen and pressure are both recorded and inside the ranges; `oxygen_only` means oxygen is inside and the table records no pressure. Status per need: `in_atmosphere`, `oxygen_only`, `pressure_only`, `other_atmosphere`, `not_measured`, and `atmosphere_not_specified` for a scenario that sets no oxygen and no pressure range. The status names are kept for the other sessions and say less than they seem to: `in_atmosphere` says only that at least one counted test has oxygen and pressure inside the ranges, whatever its fuel, flow, gravity or added gas; `not_measured` says that the need has no counted test, while tests recorded outside the stated objective may exist (D1). Gap codes say which variable (oxygen, pressure, flow, gravity) has no usable test in range or is not in the table. "Not recorded" always means that the experimental table holds no value; where a NASA record or a paper of the investigators says something about the missing variable, the sentence is carried next to the gap (`documented_elsewhere` in `sources.json`) and is never used as a value. Each test is also marked for carbon dioxide or helium added to the atmosphere (`added_gas`); the mark does not change the tier. A scenario can point to records or table cells that name its atmosphere and are not in the counts (`see_also`). All PSI tests in the tables are microgravity tests, so a lunar or Martian scenario always carries a gravity gap.

## Evidence packages

`evidence.py` (called at the end of `run.py`) writes one JSON file per environment to `data/pipeline/evidence/`, so that a reader, a page or a language model can be handed everything recorded for one environment without joining the tables. An environment is a scenario of `scenarios.json`, or a cell: one oxygen bin × one pressure bin of `coverage.json` (5 × 4 = 20; `not_recorded` is not an environment). A cell is matched exactly like a scenario whose oxygen and pressure ranges are the bin edges, with no flow range and no gravity level. `atmosphere_cells.csv` is `scenario_needs.csv` for the cells. The cells do not appear in `scenario_tests.csv` or `scenario_needs.csv`.

A package holds `environment` (label, ranges with their inclusive flags written out, `null` for a range the environment does not set, gravity level, basis items, note, `see_also` pointers, and `recorded_tests`: every test matched to the environment per investigation and fuel phase, whatever need it is counted for) and one block for each need:

| Field | Content |
|---|---|
| `status`, `counts` | The values of the environment's row in `scenario_needs.csv` or `atmosphere_cells.csv` |
| `reading`, `note` | What a counted test of the need records and what the count does not mean; limits of the need (`needs.json`) |
| `objective` | The sentences of the PSI records that state the need (`objective_links.csv`) |
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
- The sentences say what was recorded and what was not, with the number of tests and the unit. They do not judge a material, an atmosphere or the amount of evidence. Tests recorded outside the stated objective are reported as not counted. Indicators of population `recorded` (need D1) are computed over such tests, and their sentence says so.
- "Matched" means tier `atmosphere`, `oxygen_only` or `pressure_only`. The flow and gravity counts cover tiers `atmosphere` and `oxygen_only` only, as in `scenario_needs.csv`.
- Reading the cells: a test that records oxygen but no pressure has tier `oxygen_only` in all four pressure bins of its oxygen bin (and a test with pressure but no oxygen has `pressure_only` in all five oxygen bins), so those counts repeat along a row or column and must not be summed over cells. Only tier `atmosphere` places a test in exactly one cell.
- The files are deterministic: fixed key order, tests sorted by investigation number and test id, no timestamps. A package whose environment is no longer in the specs is deleted on the next run.

## References

`references.json` lists each document with the items taken from it: requirements, acceptance criteria, definitions, exposure limits, design values, knowledge gaps and published results. Each item records where in the document it is, and how the document was read (`full_text_read`, `abstract_only`, `cited_not_read`, `read_from_copy`, `read_by_teammate`). The pipeline does not compute with these values and does not judge any test against them. Some documents were read as an abstract only, through a citation or from a copy; `need_references.csv` and the evidence packages carry the `access` value of every item. Crew exposure limits (SMAC) were established for human spaceflight (`SMAC.scope`); the pipeline does not compare a sensor reading of an experiment with them.

## Checking

`python3 pipeline/check.py` recomputes every output from the raw tables and the rules written in the spec files, with code that does not import `run.py`, `rules.py`, `evidence.py` or `facts.py`, and writes `data/pipeline/validation_report.json`. `python3 pipeline/check.py --spot-check` writes `reports/spot_check.csv`: up to 20 values per table (268 rows; row 1 is the header) with the raw cell, for a person to compare with the NASA page. The check on wording covers the template sentences; readings and notes copied from the spec files are not scanned. The raw tables are compared with the manifest by size, not by hash.

## Limits

- Only the experimental tables (layer 2 of PSI) are mapped. Publications, analyzed data and raw data are not.
- Eight tables are not test-level and are listed in `sources.json` with the reason. Two of them belong to investigations whose records name exploration atmospheres (PSI-20) or list days at about 30% oxygen (PSI-23); scenarios point to them under `see_also`.
- A "test" is one row of a NASA table. In SAME-R (PSI-101) 42 of the 109 rows are a second reading of the same smoke after aging; in SPICE (PSI-107) a row is one flow setting of a flame. In SAME (PSI-102) four rows say "same conditions as 1-4" for four more materials and are not read.
- Results written as text are not carried: the 1-g columns of Saffire-II ("Complete" in normal gravity next to "~ 0" in microgravity), the comment columns of CFI-G, the fan-display notes of BASS-II other than the event word.
- "Pressure not in the table" for the solid-fuel tests does not mean the pressure is unknown to NASA: BASS-II ran in the ISS glovebox at 1 atmosphere per the investigators' paper. The pipeline does not turn such a sentence into a value.
- The lunar-habitat scenario counts as "inside" every recorded pressure below 85.8 kPa. The 17 counted tests in its oxygen range are FLEX droplets recorded at 71.2 to 72.4 kPa, that is 1 to 2 kPa above the 70.3 kPa (10.2 psi) of the challenge statement; the only tests at or below 70.3 kPa with 30% oxygen or more are 9 gas-burner tests of PSI-159 at 50.7 kPa, which are not counted for a need. The scenario carries this as `caveat`.
- Oxygen and pressure in range do not make a test representative of a habitat: the counted tests in elevated oxygen and reduced pressure are fuel droplets and burner flames in microgravity, some with carbon dioxide or helium added.
- The needs, their required variables, their scope and the link between a record sentence and a need are a team draft, not a NASA standard, and have not been reviewed by a combustion specialist.
- The challenge statement cannot be opened from the work environment of the data role. Its Moon Base bound (oxygen likely 30% or more, pressure 10.2 psi or less) and spacesuit values were checked on the official page by another session of the team on 2026-11-14 (`access: read_by_teammate`); the items give the wording as reported, not a verbatim quote.
- Five of the six needs are limited to solid fuels by the team (`scope`). Of the 1,824 test rows, 1,095 are gas-fuel rows, 353 liquid-fuel rows and 376 solid-fuel rows. Liquid-fuel and gas-fuel rows can be counted for S1 only, and no gas-fuel row is counted for any need. 414 rows are counted for at least one need; they come from five investigations (PSI-25, 69, 98, 99, 102). A record that names a topic for another fuel phase stays outside, for example PSI-10 ("Evaluate whether pseudo-flammability limits can be obtained for these flames").
- The one PSI investigation of an extinguishing agent on solid fuels (PSI-26, BASS) has an experimental table with sample names only. For the extinction need (S1) the counted solid-fuel tests are BASS-II tests with an event word beside the flow settings, and every counted test with added carbon dioxide or helium is a FLEX droplet test. In the FLEX table "extinction" is one of the recorded ways a droplet burn ends, with or without an added gas.
- The cited definition of a flammability threshold holds at a given total pressure, flow and gravity level (`ISO16697.threshold`). Pressure is not a required variable of need P1, and no counted test of P1 records a pressure.
- The ISS ranges are bins, not an ISS operating range: 19 to 23% oxygen and 85.8 to below 116.8 kPa. No reference item gives an ISS operating range for oxygen or pressure. The scenarios below 62.8 kPa accept any recorded pressure below that edge.
- The variables `o2_consumed_pct_points`, `co2_produced_pct_points` and `co_produced_ppm` are differences between a final and an initial sensor reading. The names say "consumed" and "produced"; the values are not amounts consumed or produced by one test, and many BASS-II tests start with a CO reading above zero.
- The SAME table does not say whether its "Weight loss rate (mg/min)" is a set value or a result; the pipeline lists it as the outcome of need D2. The aging time of D2 merges two source columns, "Aging Duration (minutes)" (SAME) and "Net aging time (sec)" (SAME-R).
- `reports/indicators_ko.json` holds a Korean rendering of the labels and readings for the team's internal page; the English texts in `spec/` are the authority.

## Investigations with no counted test

Five of the 24 PSI records contribute counted tests (PSI-25, 69, 98, 99, 102). The other 19 contribute none. "Linked" means that `needs.json` (`stated_by`) links a sentence of the record's `objective` field to the need. The last column quotes fire-safety wording of the record where there is any; it is a property of the catalogue text, not a judgement of the investigation.

| Record | Linked to | Why no test is counted | Fire-safety wording in the record (field) |
|---|---|---|---|
| PSI-10 Flame Design | S1 | no column mapped to an outcome variable of S1 | the words "fire" and "safety" do not occur |
| PSI-20 ACME BRE | S1 | table is one row per test day | "BRE yielded important data relevant to spacecraft fire safety." (`researchImpacts`) |
| PSI-21 CLD Flame | S1 | table is one row per test day | "an understanding of those factors that affect flame extinction in diffusion flames is critical in the suppression of fires" (`researchImpacts`) |
| PSI-22 E-FIELD Flames | none | table is one row per test day | none: "The E-FIELD Flames research is not being conducted to serve any space applications" (`researchImpacts`) |
| PSI-23 s-Flame | S1 | table is one row per test day | the words "fire" and "safety" do not occur |
| PSI-26 BASS | P1, S1 | table lists samples only: no oxygen column, no outcome column | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-39 CFI | S1 | no column mapped to an outcome variable of S1 | "support the design of safer spacecraft systems" (`researchImpacts`) |
| PSI-47 DAFT | none | table is one row per sampling session | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-60 SPICE analysis | none | no experimental table | "the results support safer fire detection, suppression, and cleaner combustion technologies" (`researchImpacts`) |
| PSI-62 flame-spread model | none | no experimental table | "enable accurate prediction of flammability limits for spacecraft materials" (`objective`) |
| PSI-68 FLEX-2 | S1 | table is one row per fuel with planned ranges | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-100 Saffire-III | P1, P3 | no oxygen column and no outcome column | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-101 SAME-R | D2 | no mass loss rate column, so no outcome of D2 | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-106 SLICE | none | table is one row per test day | "Insights into flame stability and behavior to enhance fire safety" (`researchImpacts`) |
| PSI-107 SPICE | none | rows are flow settings of gas jet flames; outside the solid-fuel scope of D2 | "Fire Safety" (`subResearchArea`); "help design safer spacecraft environments" (`researchImpacts`) |
| PSI-115 SAME data study | none | no experimental table | "This would directly lead to better smoke detection devices" (`researchImpacts`) |
| PSI-117 cool-flame study | none | no experimental table | "Potential to improve spacecraft fire-safety modeling" (`researchImpacts`) |
| PSI-142 cool-flame transitions | none | table is an index of figures in publications | "Spacecraft Fire Safety" (`subResearchArea`) |
| PSI-159 CFI-G | none | its tests record the S1 variables and are reported as recorded outside the stated objective | the words "fire" and "safety" do not occur |
