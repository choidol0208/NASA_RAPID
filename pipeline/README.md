# Pipeline: PSI raw tables → fire-safety information needs

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. The spec files are drafts and have not been reviewed by a combustion expert.*

The pipeline starts from the question side: what does spacecraft fire safety need to know, and which recorded variables can answer it? It then checks every NASA PSI experimental table against that list. It links tests to questions; it does not answer the questions and draws no conclusion from the values.

```
spec/needs.json      what fire safety needs to know (6 questions: prevention, detection, suppression)
        │             each need = required condition variables + any-of outcome variables + scope
spec/references.json standards, requirements and published results each need rests on (21 documents)
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

Run: `python3 pipeline/run.py` (after `python3 scripts/fetch_psi.py`).

## Outputs (`data/pipeline/`)

| File | Content |
|---|---|
| `tests.csv` | One row per test, all standard and derived variables, flags, source file and row |
| `values_long.csv` | One row per value, with the source column it came from |
| `capability_matrix.csv` | Need × source: how many tests carry the required conditions and an outcome; status |
| `need_tests.csv` | For each need, the tests that record its variables, with `objective_link` |
| `coverage_grid.csv` | Recorded tests per fuel phase, oxygen basis, oxygen bin and pressure bin; `not_recorded` is its own bin |
| `scenario_tests.csv` | Scenario × test: whether the recorded oxygen, pressure, flow and gravity fall in the scenario ranges; match tier |
| `scenario_needs.csv` | Scenario × need: usable tests by match tier, investigations, status, and gap codes |
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

Status in the capability matrix: `measured`, `partial` (an outcome exists but a required condition is missing), `conditions_only`, `none`, `out_of_scope`, `not_test_level` (the table's rows are not individual tests).

## Rules the engine follows

- A value is copied from a NASA source cell, multiplied by a unit factor declared in `sources.json`, or computed by a formula in `variables.json`. Nothing is estimated.
- A cell that a rule cannot read stays empty and gets a flag (`variable:reason`). Problems are flagged, not fixed. A number is never taken from a pointer such as "Note 4" or "See Fig. 5"; a cell with several numbers, or a number whose decimal point is unclear ("037 mm"), gives no value.
- Every value keeps its source file, row and column.
- To add a table, a variable or a need, edit the spec files; `run.py` does not change.

Values that are not literally in a NASA cell, all flagged on the test:

| What | Where | Flag |
|---|---|---|
| Midpoint of an oxygen range written in the cell ("21.5 - 21.7") | 3 Saffire tests | `o2_pct:range_in_source_midpoint_used` |
| Material name PMMA where the cell gives only a shape or a thickness (BASS-II ReadMe) | 87 BASS and BASS-II tests | `fuel_material:not_written_in_cell_named_in_readme` |
| Material of the row above where the cell is blank | 2 Saffire-II tests | `fuel_material:blank_in_source_value_of_row_above_used` |
| Shape words ("film", "slab", "rod", "fabric sheet") chosen by keyword from the sample cell | BASS and BASS-II | none; the keywords are in `sources.json` (`sample_keywords`) |
| Constants of a whole table (gravity level, fuel phase, oxygen basis) | `sources.json` `constants` | source column reads "(constant in sources.json)" |

Rows that are not read: a row with a required cell empty, a row named in `sources.json` as not a test (one maintenance entry in PSI-26), and a row that repeats an earlier row cell for cell (8 in PSI-39, 34 in PSI-107). `run_report.json` lists them.

## Why a test counts for a need

Recording the right variables is not enough to be counted. A test is counted for a need only if a sentence in the `objective` field of the PSI record of its investigation names the topic of the need as something the investigation set out to determine. The sentence is copied into `needs.json` (`stated_by`) and the engine checks that it is in the record. `capability_matrix.csv` and `need_tests.csv` carry `objective_link` (`stated` or `not_stated`). Scenario counts and indicators use `stated` tests; the others are reported next to them as recorded outside the stated objective.

This link is a property of the catalogue text and was made by the team. It does not show that a test can or cannot inform the need. The combustion-products need (D1) has no record that names a gas species as something to determine; the BASS-II CO and CO2 readings are reported as recorded outside the stated objective, with the investigators' own description of the sensor (`ICES19.sensors`).

Each need has a `reading`: what a counted test records and what the count does not mean (for example, a test counted for "Extinction conditions" records how the burn ended, which may be disruption or completion and not extinction). It is shown wherever the count is shown.

The needs themselves are the team's wording. `needs.json` says which parts come from NASA documents and lists the areas NASA names that the PSI tables cannot address (`not_covered`), and the PSI records that make a fire-safety statement but contribute no counted test.

## Indicators

`indicators.json` declares what is computed for each need. The engine has three templates (`summary`, `count_by`, `count`); the spec only chooses the variable, the filter and the grouping, so no number comes from anything but recorded values. Each indicator carries a `reading` that says what it does not mean (for example, the lowest oxygen tested is not a flammability limit), the reference items that define the concept, and, where the investigators published a result for the same investigation, a `compare_with` pointer. The pipeline does not make that comparison.

## Scenarios

A scenario is a set of ranges (`scenarios.json`), not a prediction. A test is marked `in`, `out` or `not_recorded` for each variable. Tier `atmosphere` means oxygen and pressure are both recorded and inside the ranges; `oxygen_only` means oxygen is inside and the table records no pressure. Status per need: `in_atmosphere`, `oxygen_only`, `pressure_only`, `other_atmosphere`, `not_measured`. Gap codes say which variable (oxygen, pressure, flow, gravity) has no usable test in range or is not in the table. "Not recorded" always means that the experimental table holds no value; where a NASA record or a paper of the investigators says something about the missing variable, the sentence is carried next to the gap (`documented_elsewhere` in `sources.json`) and is never used as a value. Each test is also marked for carbon dioxide or helium added to the atmosphere (`added_gas`); the mark does not change the tier. A scenario can point to records or table cells that name its atmosphere and are not in the counts (`see_also`). All PSI tests in the tables are microgravity tests, so a lunar or Martian scenario always carries a gravity gap.

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

`references.json` lists each document with the items taken from it: requirements, acceptance criteria, definitions, exposure limits, design values, knowledge gaps and published results. Each item records where in the document it is, and how the document was read (`full_text_read`, `abstract_only`, `cited_not_read`, `read_from_copy`). The pipeline does not compute with these values and does not judge any test against them. Crew exposure limits (SMAC) apply to cabin air, not to a test chamber.

## Checking

`python3 pipeline/check.py` recomputes every output from the raw tables and the rules written in the spec files, with code that does not import `run.py`, `rules.py`, `evidence.py` or `facts.py`, and writes `data/pipeline/validation_report.json`. `python3 pipeline/check.py --spot-check` writes `reports/spot_check.csv`: 20 values per table with the raw cell, for a person to compare with the NASA page.

## Limits

- Only the experimental tables (layer 2 of PSI) are mapped. Publications, analyzed data and raw data are not.
- Eight tables are not test-level and are listed in `sources.json` with the reason. Two of them belong to investigations whose records name exploration atmospheres (PSI-20) or list days at about 30% oxygen (PSI-23); scenarios point to them under `see_also`.
- A "test" is one row of a NASA table. In SAME-R (PSI-101) 42 of the 109 rows are a second reading of the same smoke after aging; in SPICE (PSI-107) a row is one flow setting of a flame. In SAME (PSI-102) four rows say "same conditions as 1-4" for four more materials and are not read.
- Results written as text are not carried: the 1-g columns of Saffire-II ("Complete" in normal gravity next to "~ 0" in microgravity), the comment columns of CFI-G, the fan-display notes of BASS-II other than the event word.
- "Pressure not in the table" for the solid-fuel tests does not mean the pressure is unknown to NASA: BASS-II ran in the ISS glovebox at 1 atmosphere per the investigators' paper. The pipeline does not turn such a sentence into a value.
- Oxygen and pressure in range do not make a test representative of a habitat: the counted tests in elevated oxygen and reduced pressure are fuel droplets and burner flames in microgravity, some with carbon dioxide or helium added.
- The needs, their required variables, their scope and the link between a record sentence and a need are a team draft, not a NASA standard, and have not been reviewed by a combustion specialist.
- The challenge statement was read from a copy; the lunar-habitat bound (30% oxygen or more, 10.2 psi or less) has not been checked on the official page.
