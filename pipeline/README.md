# Pipeline: PSI raw tables → fire-safety information needs

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. The spec files are drafts and have not been reviewed by a combustion expert.*

The pipeline starts from the question side: what does spacecraft fire safety need to know, and which recorded variables can answer it? It then checks every NASA PSI experimental table against that list. It links tests to questions; it does not answer the questions and draws no conclusion from the values.

```
spec/needs.json      what fire safety needs to know (7 questions: prevention, detection, suppression)
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
| `need_tests.csv` | For each need, the tests that can be used as evidence |
| `coverage_grid.csv` | Recorded tests per fuel phase, oxygen basis, oxygen bin and pressure bin; `not_recorded` is its own bin |
| `scenario_tests.csv` | Scenario × test: whether the recorded oxygen, pressure, flow and gravity fall in the scenario ranges; match tier |
| `scenario_needs.csv` | Scenario × need: usable tests by match tier, investigations, status, and gap codes |
| `indicators.csv` | Per need and group: count, min, median, max of a recorded variable, with the indicator's reading and reference items |
| `indicator_tests.csv` | The tests behind every indicator row |
| `objective_links.csv` | Need × investigation: the sentence in the PSI record that states the need as an objective |
| `need_references.csv` | For each need, the reference items (criterion text, values, document, section, URL) |
| `run_report.json` | Row counts, flags, unmapped source columns, fill count per variable |

Status in the capability matrix: `measured`, `partial` (an outcome exists but a required condition is missing), `conditions_only`, `none`, `out_of_scope`, `not_test_level` (the table's rows are not individual tests).

## Rules the engine follows

- A value is copied from a NASA source cell or computed by a formula in `variables.json`. Nothing is estimated.
- A cell that a rule cannot read stays empty and gets a flag (`variable:reason`). Problems are flagged, not fixed.
- Every value keeps its source file, row and column.
- To add a table, a variable or a need, edit the spec files; `run.py` does not change.

## Why a test counts for a need

Recording the right variables is not enough. A test counts as evidence for a need only if the PSI record of its investigation states that need as an objective; the sentence is copied into `needs.json` (`stated_by`) and the engine checks that it is in the record. `capability_matrix.csv` and `need_tests.csv` carry `objective_link` (`stated` or `not_stated`). Scenario counts and indicators use `stated` tests only; the others are reported as recorded outside the stated objective. Example: the CFI-G burner tests record oxygen, pressure and how the flame ended, but the investigation studies cool flames, so they are not counted for the extinction need. The combustion-products need (D1) has no investigation that states it; its indicators are side measurements and say so.

The needs themselves are the team's wording. `needs.json` says which parts come from NASA documents and lists the areas NASA names that the PSI tables cannot address (`not_covered`).

## Indicators

`indicators.json` declares what is computed for each need. The engine has three templates (`summary`, `count_by`, `count`); the spec only chooses the variable, the filter and the grouping, so no number comes from anything but recorded values. Each indicator carries a `reading` that says what it does not mean (for example, the lowest oxygen tested is not a flammability limit), the reference items that define the concept, and, where the investigators published a result for the same investigation, a `compare_with` pointer. The pipeline does not make that comparison.

## Scenarios

A scenario is a set of ranges (`scenarios.json`), not a prediction. A test is marked `in`, `out` or `not_recorded` for each variable. Tier `atmosphere` means oxygen and pressure are both recorded and inside the ranges; `oxygen_only` means oxygen is inside and the table records no pressure. Status per need: `in_atmosphere`, `oxygen_only`, `pressure_only`, `other_atmosphere`, `not_measured`. Gap codes say which variable has no usable test in range or is not recorded, including gravity. All PSI tests in the tables are microgravity tests, so a lunar or Martian scenario always carries a gravity gap.

## References

`references.json` lists each document with the items taken from it: requirements, acceptance criteria, definitions, exposure limits, design values, knowledge gaps and published results. Each item records where in the document it is, and how the document was read (`full_text_read`, `abstract_only`, `cited_not_read`, `read_from_copy`). The pipeline does not compute with these values and does not judge any test against them. Crew exposure limits (SMAC) apply to cabin air, not to a test chamber.

## Limits

- Only the experimental tables (layer 2 of PSI) are mapped. Publications, analyzed data and raw data are not.
- Eight tables are not test-level and are listed in `sources.json` with the reason.
- The needs, their required variables and their scope are a team draft, not a NASA standard.
