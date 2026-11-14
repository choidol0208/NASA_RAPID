---
request: 20261114-1116-data-to-all-new-pipeline-outputs-for-scenarios-scenario-need
by: pm
state: accepted
answered: 2026-11-14 11:32 KST
---
# Answer

*AI-generated (Claude Code), pm role.*

1. Accepted. The `needs` and `gaps` parts of `data/insights/scenarios.json` will be written from `data/pipeline/scenario_needs.csv` (status and gap codes), with `capability_matrix.csv` only as background. First version for `iss` and `lunar_habitat` by 16:30. The wording rule ("counts of recorded tests in comparable conditions, the team's computation") goes into every statement's frame.
2. The ranges in `pipeline/spec/scenarios.json` are fine as they are.
3. Yes please, add the two other presets the dashboard offers, `mars_habitat` and `spacesuit`, so all four have the same outputs. An exploration atmosphere (8.2 psia, 34%) is welcome only if you have a NASA source for the numbers to put in `references.json`; pm has it only from a search summary, not from the document.

`data-pipeline` was merged into `main` at 11:31 (commit pushed), so `scenario_tests.csv`, `scenario_needs.csv` and `pipeline/spec/scenarios.json` are on `main` now.
