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
| `need_references.csv` | For each need, the reference items (criterion text, values, document, section, URL) |
| `run_report.json` | Row counts, flags, unmapped source columns, fill count per variable |

Status in the capability matrix: `measured`, `partial` (an outcome exists but a required condition is missing), `conditions_only`, `none`, `out_of_scope`, `not_test_level` (the table's rows are not individual tests).

## Rules the engine follows

- A value is copied from a NASA source cell or computed by a formula in `variables.json`. Nothing is estimated.
- A cell that a rule cannot read stays empty and gets a flag (`variable:reason`). Problems are flagged, not fixed.
- Every value keeps its source file, row and column.
- To add a table, a variable or a need, edit the spec files; `run.py` does not change.

## Scenarios

A scenario is a set of ranges (`scenarios.json`), not a prediction. A test is marked `in`, `out` or `not_recorded` for each variable. Tier `atmosphere` means oxygen and pressure are both recorded and inside the ranges; `oxygen_only` means oxygen is inside and the table records no pressure. Status per need: `in_atmosphere`, `oxygen_only`, `pressure_only`, `other_atmosphere`, `not_measured`. Gap codes say which variable has no usable test in range or is not recorded, including gravity. All PSI tests in the tables are microgravity tests, so a lunar or Martian scenario always carries a gravity gap.

## References

`references.json` lists each document with the items taken from it: requirements, acceptance criteria, definitions, exposure limits, design values, knowledge gaps and published results. Each item records where in the document it is, and how the document was read (`full_text_read`, `abstract_only`, `cited_not_read`, `read_from_copy`). The pipeline does not compute with these values and does not judge any test against them. Crew exposure limits (SMAC) apply to cabin air, not to a test chamber.

## Limits

- Only the experimental tables (layer 2 of PSI) are mapped. Publications, analyzed data and raw data are not.
- Eight tables are not test-level and are listed in `sources.json` with the reason.
- The needs, their required variables and their scope are a team draft, not a NASA standard.
