---
request: 20261114-1116-data-to-all-new-pipeline-outputs-for-scenarios-scenario-need
by: ui
state: accepted
answered: 2026-11-14 11:22 KST
---
# Answer

Accepted. Ready by 14:30, counted from the moment both files are on `main` (I merge only `main` into `catalog-filter`).

1. "Show the tests": the dashboard will read `data/pipeline/scenario_tests.csv` when the query resolves to the `iss` or `lunar_habitat` preset, and list the tests by `tier`, filtered in the browser, each test linked to its `source_file` and `source_row` through `tests.csv`. Queries without a matching scenario id show "Test list: available for the ISS and lunar habitat scenarios" instead of a computed match.
2. I will also use `data/pipeline/scenario_needs.csv` in the needs view: for those two presets, a row "In your atmosphere" above the per-investigation matrix, with `status`, the counts per tier and the `gaps` codes in plain words. Your wording goes with it: counts of recorded tests in comparable conditions, the team's computation, not a statement about how a material behaves.
3. Ranges in `pipeline/spec/scenarios.json`: no change needed from ui. They agree with the scorer presets (ISS 21% and 101.3 kPa; lunar habitat 30% and 70.3 kPa, lunar gravity) and with the coverage bins the page already marks. Please do not add more scenarios for the dashboard; two keep the demo story clear.

Already live (from `main` as of 11:10): needs view from `capability_matrix.csv` and coverage view from `coverage_grid.csv` at https://choidol0208.github.io/NASA_RAPID/ . I will pick up your D2 change in `capability_matrix.csv` with the next merge of `main`.
