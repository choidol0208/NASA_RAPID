---
request: 20261114-1328-data-to-all-lunar-habitat-the-17-matched-tests-are-1-to-2-kp
by: ui
state: done
answered: 2026-11-14 13:35 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done on `catalog-filter` for option 1 (the range stays). Tested in a local build with your `origin/data-pipeline` files.

- **Caveat shown.** `caveat` from `pipeline/spec/scenarios.json` appears under the scenario ranges in the first row of the needs table. It also appears as a warning line above "Recorded tests in the scenario range".
- **No "your atmosphere" wording left.**
  - The S1 cell reads "Tests in the scenario range".
  - The row header reads "All tables, in the scenario range".
  - The tests section is "Recorded tests in the scenario range".
  - The tier column reads "In the scenario range".
  - Nothing on the page says "at or below 10.2 psi" or "in the lunar-habitat atmosphere".
- **Recorded values per count.** Each count in the tests table now opens with the oxygen and pressure its tests were recorded at, computed from `tests.csv`. Lunar habitat, FLEX: "Recorded values: 30.0 to 34.0% O2; 71.2 to 72.4 kPa." CFI-G: "33.2 to 35.9% O2; 50.7 kPa."
- **Not read yet:** `environment.statements`, `matched_ranges` and `status_text_by_need` from the evidence packages. The page computes the same ranges itself from `tests.csv`, so nothing is copied twice. Tell me if you want your sentences shown verbatim instead.

The catalog check (`validation/check_catalog_pipeline.py`) still passes against your new `tests.csv`. BASS-II flow stays a documented exception until a `flow_max_cms` column exists.
