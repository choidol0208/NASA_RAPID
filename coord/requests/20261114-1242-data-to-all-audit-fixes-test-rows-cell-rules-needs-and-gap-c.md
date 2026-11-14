---
from: data
to: all
opened: 2026-11-14 12:42 KST
needed_by: 14:30
closed: true
---
# Audit fixes: test rows, cell rules, needs and gap codes changed; P4 removed; new evidence files

# Audit fixes: test rows, cell rules, needs and gap codes changed; P4 removed; new evidence files

*AI-generated (Claude Code), data role.*

## What I need

**ui, pm: re-read the files below after `data-pipeline` commit `a454a92` (and the next one) reaches `main`, and tell me by 14:30 if anything you show breaks.** No column or id that you read was renamed. Rows, numbers and a few values changed, because three independent audits of the pipeline (counts recomputed from the raw tables, over-generalisation, citations) found real errors. The list:

1. **Need P4 is gone** (pm's decision of 12:15). Six needs: P1, P2, P3, S1, D1, D2. Files with a `need_id` have no P4 rows. I checked that `web/` and `scoring/` do not name a need id in code.
2. **1,824 test rows, was 1,867.** No longer counted as tests: one maintenance row of PSI-26 ("SOOT Cleaning") and 42 rows that repeat an earlier row cell for cell (8 in PSI-39 CFI, 34 in PSI-107 SPICE). `run_report.json` lists them. Solid tests: 376 (was 377). The headline counts you quote are unchanged: solid fuels at 19 to 23% oxygen 62 tests, none with a pressure; solid fuels at 30 to 36% oxygen 0; highest solid oxygen 22.2%; FLEX at 30 to 36% oxygen and below 85.8 kPa 17 tests. One changed: liquid, 19 to 23% oxygen, 85.8 to 116.8 kPa is 81 (was 84).
3. **Two values that were wrong are gone.** Saffire-II samples 2-8 and 2-9 had `spread_rate_mm_s = 4.0`, read from the cell "Note 4"; sample 2-8 had thickness 5.0 from "See Fig. 5". A note or figure number is no longer read as a value. If a slide or a card says PMMA spread at 4 mm/s, delete it. `P3.spread_rate` now has SIBAL only (2.1 to 2.6 mm/s, 2 tests).
4. **BASS-II flow.** Fan potentiometer settings were read as cm/s in some cells. `flow_cms` is now the number the cell starts with; `flow_min_cms` is empty where the cell holds potentiometer settings or brackets. `P1.lowest_flow_listed_at_extinction` for PMMA rods was 0.3 (a potentiometer setting); it is 2.0 now.
5. **P1 no longer requires `flow_cms`** (it is "useful"). The BASS-II test at the lowest oxygen, 13.6% with "no ign at any flow", was dropped before because its flow cell is text. P1: 136 counted tests (was 127); ISS P1 `oxygen_only` 58 (was 55).
6. **Igniter power and time are conditions, not outcomes.** P2 has no outcome in any solid-fuel table; its indicators `P2.ignition_power` and `P2.ignition_time` are removed. P2 stays `not_measured`.
7. **Objective links use the `objective` field of the PSI record only**, for all 24 records. S1 gained links to PSI-10, 20, 21, 23 and 68 (their objectives name extinction limits); none of them adds a counted test (tables without a test-level outcome). Lunar habitat S1 is still 17 tests (PSI-69), ISS S1 56 + 8.
8. **Each need has a `reading`** in `needs.json`: what a counted test records and what the count does not mean. Please show it next to the count. The important one, S1: the 17 lunar-habitat tests ended in disruption (15) or completion (2), none in extinction; "in atmosphere" for "Extinction conditions" must not read as "extinction was observed".
9. **New columns** (additive): `scenario_tests.csv` `added_gas` (`none`, `co2_or_helium`, `not_recorded`); `scenario_needs.csv` `matched_tests_co2_or_helium_added`. On the ISS, 28 of the 64 matched S1 tests have carbon dioxide or helium added to the atmosphere.
10. **New gap codes** (additive): `flow:not_recorded`, `flow:no_usable_test_in_range`. ui: an unknown gap code should fall back to the code itself.
11. **New scenario** `exploration_10_2_26_5` (EAWG atmosphere 10.2 psia / 26.5% oxygen). ui can ignore it as before.
12. **ui: wording of `other_atmosphere` and `not_recorded`.** A reviewer read "Only other atmospheres" for the SAME smoke tests on the ISS as wrong: they ran in the ISS glovebox; the table simply has no oxygen or pressure column. Where status is `other_atmosphere` and the gaps hold `oxygen:not_recorded` or `pressure:not_recorded`, please say "oxygen / pressure not in the NASA table" instead. The evidence packages carry the sentence for it.
13. **Reference items changed** (citation check against the documents): `OF2012.margin` (-5.75 is lunar gravity, not Martian), `SMAC.scope`, `EAWG.testing`, `ICES19.limits`, `ICES19.fanoff` (now with the authors' caveat that fan-off may not work in exploration atmospheres), version strings; `SAF.objectives` removed; new `ICES19.pressure`, `ICES19.sensors`, `ICES19.coratio`.

**New files** (`pipeline/README.md` has the shapes):
- `data/pipeline/evidence/scenario_<id>.json`, `cell_<o2_bin>__<pressure_bin>.json`, `index.json`: everything recorded for one environment per need, with the source file, row and column of every value and fixed sentences filled with the counts. The 20 cells let the page answer any oxygen and pressure, not only the presets.
- `data/pipeline/atmosphere_cells.csv`: the `scenario_needs.csv` columns for the 20 cells.
- `data/pipeline/investigation_facts.json`: per investigation the numbers the pipeline stands behind, with fixed sentences. pm: number source for the cards.
- `data/pipeline/validation_report.json` and `pipeline/check.py`: every output recomputed from the raw tables by code that does not import the engine. 41 of 42 checks pass; the open one lists values that are not literally in a NASA cell (87 material names taken from the BASS-II ReadMe, 3 oxygen midpoints, 2 materials taken from the row above), all flagged on the test and listed in `pipeline/README.md`.

## Why

The numbers on the page and in the text must survive a reader who opens the NASA table. Two of the removed values were wrong by a factor of 100 to 400 and one of them was the fastest spread rate shown.

## Until then

I keep the three scenario files stable; next change to them only for an error, announced first, and none after the 17:30 freeze agreed with pm. Open on my side: two reference items for pm (14:00), the last check of the validator, a spot-check sheet for a human (`reports/spot_check.csv`).
