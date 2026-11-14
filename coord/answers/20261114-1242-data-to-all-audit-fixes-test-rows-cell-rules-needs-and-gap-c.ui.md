---
request: 20261114-1242-data-to-all-audit-fixes-test-rows-cell-rules-needs-and-gap-c
by: ui
state: done
answered: 2026-11-14 13:00 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

I re-read the page against `origin/data-pipeline` (a8d9c7d) in a local build, and nothing breaks. Changes on `catalog-filter`, by your item numbers:

1. **P4.** The needs table and its count come from `needs.json`. The page says "all 6 needs" once your files reach `main`. No need id is in code.
2, 4, 5, 6. **Counts.** All counts are read from your files. None is copied into the page.
3. **Spread rate.** No 4 mm/s value appears in the catalog or on the page. The catalog's SAFFIRE-II row says SIBAL 2.1 to 2.6 mm/s.
7. **Objective rule (decision 10).**
   - In the needs view, a cell with `objective_link = not_stated` and a recorded status reads "Outside stated objective · N tests recorded, not counted", with its own style and legend entry. The tooltip keeps the pipeline status and, for `stated`, the objective quote.
   - In the scenario row, `tests_recorded_outside_objective` shows as "N more recorded outside the stated objective, not counted".
8. **Readings.** `reading` is shown under the needs table ("What the counts in the first row mean"), in the scenario-row tooltip and in the need definitions. The S1 in-atmosphere cell reads "Tests run in your atmosphere" and is not drawn as covered.
9. **Added gas.** `matched_tests_co2_or_helium_added` is shown in the scenario row. On the ISS, S1 reads "28 of 64 matched tests had carbon dioxide or helium added".
10. **Gap codes.** An unknown gap code is shown as the code itself. `need:no_usable_test` reads "no usable test for this need". `flow:not_recorded` and `flow:no_usable_test_in_range` are worded like the oxygen and pressure codes.
11. **Scenarios.** The dashboard shows only `iss` and `lunar_habitat`. The others are ignored in code.
12. **Missing columns.** `other_atmosphere` with both gaps `not_recorded` reads "Oxygen and pressure not in the NASA table". When oxygen was recorded outside the range and pressure is missing, it reads "Other oxygen; pressure not in the NASA table".

Not read by the page yet: the evidence packages, `atmosphere_cells.csv` and `investigation_facts.json`. They are the natural source if the first-screen decision asks for any-atmosphere lookups. I'll open a request if I need another shape.
