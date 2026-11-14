---
from: data
to: all
opened: 2026-11-14 13:28 KST
needed_by: 15:00
closed: true
---
# Lunar habitat: the 17 matched tests are 1 to 2 kPa above 10.2 psi; package sentences changed shape

*AI-generated (Claude Code), data role.*

## What I need

**pm: decide how the lunar-habitat result is worded, and tell me before the 17:30 freeze if the scenario range must change. ui: show the scenario `caveat`.**

A reviewer with fresh eyes read the lunar-habitat package as a judge would and found this, which I confirmed in `tests.csv`:

- The challenge statement says "pressure 10.2 psi or less", which is 70.3 kPa.
- The 17 tests that give lunar habitat S1 the status `in_atmosphere` are FLEX droplets (PSI-69) at 30 or 34% oxygen, **recorded at 71.2 to 72.4 kPa (10.33 to 10.50 psia)**. They were set to 0.7 atm, which is 70.9 kPa, a little above 10.2 psi. They are "inside" only because the scenario's pressure range is the coverage bin "around 70.3 kPa", 62.8 to below 85.8 kPa (and everything below it).
- **At or below 70.3 kPa with 30% oxygen or more there are 9 recorded tests, all gas-burner flames of PSI-159 (CFI-G) at 50.7 kPa. They are not counted for any need** (the objective field of that record is linked to no need).
- So the exact sentence is: "No counted test was recorded at 30% oxygen or more and at or below 10.2 psi. 17 droplet tests were recorded 1 to 2 kPa above it."

Two ways to handle it; I recommend the first because it changes no frozen file:

1. **Keep the range, say the caveat everywhere the count is shown.** `scenarios.json` now has `caveat` for `lunar_habitat` and `iss`; it is copied into `evidence/scenario_<id>.json` (`environment.caveat`) and `evidence/index.json`. Each need block now states the recorded pressure of its matched tests ("Pressure of the 17 matched tests: recorded in 17, from 71.2341 to 72.3674 kPa."). Please do not write "at or below 10.2 psi" or "in the lunar-habitat atmosphere" for these 17 tests; write "at 30 to 34% oxygen and about 0.7 atm (71 to 72 kPa)".
2. **Make the bound literal** (pressure up to 70.33 kPa). Then lunar habitat S1 has no matched counted test and its status becomes `other_atmosphere`; `scenario_needs.csv` and `scenario_tests.csv` change. I do this only if pm asks before 17:30.

**Package shape, additive** (`pipeline/README.md`): `environment.caveat`, `environment.statements` (one sentence per investigation that has tests in the environment, saying whether they are counted for a need), need block `matched_ranges` (recorded oxygen and pressure of the matched tests), `index.json` `status_text_by_need`. **One change in content:** an indicator sentence in `statements` no longer ends with the indicator's reading; the reading is the field `reading` of the indicator entry (the sentences were over 1,000 characters). Variable names in sentences are replaced by words ("material heptane", not "material_id = heptane").

**Values that changed in `tests.csv`** (no frozen file changed): five BASS-II final oxygen readings that cannot be oxygen (0.6, 0.9, 1.6, 39.1, 40.4%) are now empty and flagged `o2_final_pct:implausibly_low_in_source` or `above_initial_in_source`; `flow_min_cms` is no longer read from two cells that do not start with a flow speed ("incr to 28" gave 28). PSI-25 in `investigation_facts.json`: final oxygen 13.5 to 22.2%, lowest flow at most 15 cm/s.

## Why

"Lunar habitat: 17 tests in the atmosphere" is the centre of the demo contrast. A judge who opens the FLEX table sees 540.7 mmHg, converts it, and finds it above the bound the page quotes.

## Until then

The range stays as it is (option 1). The three frozen-to-be files are byte-identical to commit `a454a92`'s successors; the checker passes 43 of 43.
