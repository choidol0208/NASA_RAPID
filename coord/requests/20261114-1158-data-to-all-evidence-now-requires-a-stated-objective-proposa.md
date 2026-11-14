---
from: data
to: all
opened: 2026-11-14 11:58 KST
needed_by: 13:30
closed: false
---
# Evidence now requires a stated objective; proposal to drop need P4; three more scenarios

*AI-generated (Claude Code), data role.*

## What I need

1. **ui, pm: read `objective_link` where you count evidence.** New rule in the pipeline: a test counts as evidence for a need only if the PSI record of its investigation states that need as an objective. The sentence is copied into `pipeline/spec/needs.json` (`stated_by`), checked against the record by the engine, and listed in the new `data/pipeline/objective_links.csv`.
   - `capability_matrix.csv`: two new columns, `objective_link` (`stated` / `not_stated`) and `objective_quote`. `status` and the count columns are unchanged, so nothing breaks; but a row with `status = measured` and `objective_link = not_stated` should be shown as "recorded, outside the investigation's stated objective", not as evidence.
   - `need_tests.csv`: new column `objective_link`. Filter on `stated` when you count.
   - `scenario_needs.csv`: counts now use `stated` tests only (numbers changed, see below); new column `tests_recorded_outside_objective`; new status value `atmosphere_not_specified` (only for `mars_habitat`).
   - `indicators.csv`: `usable` indicators use `stated` tests only; the D1 indicators are marked as side measurements in `reading`.
2. **pm: decide whether need P4 (Exploration atmosphere) is removed.** It is not an information need but a condition that applies to every need, and it is already handled by `scenarios.json` and `coverage_grid.csv`. If you agree, I remove P4 from `needs.json`, and the P4 rows disappear from `capability_matrix.csv`, `need_tests.csv`, `scenario_needs.csv` and `need_references.csv`. The other ids (P1, P2, P3, S1, D1, D2) do not change. Until you decide, P4 stays.
3. **pm: scenarios you asked for are in.** `mars_habitat`, `spacesuit` and `exploration_8_2_34` (source: NTRS 20150021491 abstract and JSC 20584 Rev D page 7, items `EA.8.2-34` and `SMAC.atmospheres` in `references.json`). ui asked not to add scenarios to the dashboard; the rows are there for pm's text, ui can ignore every `scenario_id` other than `iss` and `lunar_habitat`.

## Why

The team lead of the data side asked how the needs are backed. Checking the PSI records showed that the earlier counts used tests for purposes their investigations never stated: the CFI-G burner tests (PSI-159, cool flames) and Flame Design (PSI-10, soot inception) were counted for extinction and exploration atmosphere only because they record oxygen, pressure and burn time. With the rule, what changes for the two demo scenarios:

- S1 Extinction: lunar habitat 17 tests in the atmosphere, all PSI-69 (was 24 with PSI-159); ISS 56 (was 75).
- P4: lunar habitat 17 (was 26); ISS 56 (was 154).
- D1 Combustion products: no investigation states it as an objective, so `usable_tests` is 0 and the 126 BASS-II/SAME tests are `tests_recorded_outside_objective`. The need itself rests on the NASA-STD-3001 monitoring requirement. Status is `not_measured` with gap `need:no_usable_test`.
- P2 Ignition: only BASS-II states it, and its table has no ignition result; the 9 Saffire tests with igniter settings are outside the stated objective. Status `not_measured`.
- P1, P3, D2: unchanged.

`needs.json` now also says which parts of the needs are the team's wording and which come from NASA documents (`_meta.authorship`), and lists the areas NASA names that the PSI tables cannot address (`_meta.not_covered`: post-fire clean-up, agent transport, partial gravity, toxic products other than CO). Please use that list for the "where the data stops" text.

## Until then

I keep P4 in place and continue with the per-scenario evidence package (one JSON per scenario: status, tests, indicators on the matched tests, gaps, reference items).
