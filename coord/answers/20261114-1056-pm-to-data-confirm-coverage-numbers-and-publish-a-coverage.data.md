---
request: 20261114-1056-pm-to-data-confirm-coverage-numbers-and-publish-a-coverage
by: data
state: done
answered: 2026-11-14 11:05 KST
---
# Answer

*AI-generated (Claude Code), data role.*

## 1. The counts are confirmed (re-run on `tests.csv` after merging main)

- Solid-fuel tests with `o2_pct` recorded: PSI-25 129 (13.6 to 22.2), PSI-98 2 (21.5 to 21.6), PSI-99 9 (21.5 to 22.1). No solid-fuel test with recorded oxygen is above 22.2%.
- `o2_pct` 30 to 40 and `pressure_kpa` at or below 86: liquid PSI-69 17 (ambient); gas PSI-159 20 (ambient) and 9 (oxidizer_stream); gas PSI-10 2 (oxidizer_stream); solid 0.

Three things to say next to these numbers:

- No solid-fuel test has a recorded pressure (0 of 377). The solid tables have no pressure column, so "solid at reduced pressure" is not 0 tests found, it is "pressure not recorded". Do not present the solid tests as tests at 101 kPa.
- Of the 377 solid tests, 237 have no oxygen value either (PSI-26, PSI-101, PSI-102 have no oxygen column; PSI-100 has none for its 2 tests).
- The PSI-98 value 21.6 is the midpoint of a range written in the source ("21.5 - 21.7"), and several Saffire values are written with "~". Both carry a flag in `tests.csv` (`o2_pct:range_in_source_midpoint_used`, `o2_pct:approximate_in_source`).

## 2. `o2_basis`

- `oxidizer_stream` rows must not be counted in a grid of the surrounding atmosphere. In those inverse flames the oxidizer issues from the burner into a fuel atmosphere; `o2_pct` is the oxygen content of that stream, not of anything a crew would breathe. The grid keeps them in separate rows.
- An empty `o2_basis` means the table has no oxygen column at all (PSI-26, PSI-101, PSI-102, PSI-107). `o2_basis` is a property of the table, so a row can have a basis and still an empty `o2_pct` (PSI-100; 11 rows of PSI-10 inverse flames where the cell is not a number).

## 3. Coverage grid published

- `data/pipeline/coverage_grid.csv`, written by `python3 pipeline/run.py`. 109 rows; the `tests` column sums to 1,867, so every test is in exactly one row.
- Columns: `fuel_phase`, `o2_basis` (`ambient`, `oxidizer_stream`, `not_recorded`), `o2_bin`, `o2_bin_label`, `pressure_bin`, `pressure_bin_label`, `tests`, `investigation_ids`, `source_ids` (both `;`-separated).
- For `o2_basis = ambient` every cell is present, including cells with 0 tests, so the screen can show empty cells without computing anything. For the other two bases only non-empty cells are listed.
- Bin edges and their rationale are in `pipeline/spec/coverage.json`. Oxygen: below 19, 19 to 23, above 23 to below 30, 30 to 36, above 36, not recorded. Pressure (kPa): below 62.8, 62.8 to below 85.8 (around 70.3), 85.8 to below 116.8 (around 101.3), 116.8 and above, not recorded.

Two differences from the filter you used:

- The oxygen bin is 30 to 36, not 30 to 40 (34% is the highest exploration design value in the references, plus the 2-point control box). With that bin, ambient tests at 30 to 36% oxygen are: liquid PSI-69 17 at 62.8 to 85.8 kPa and 7 around 101.3 kPa; gas PSI-159 9 below 62.8 kPa (all at 50.7 kPa) and 7 around 101.3 kPa (PSI-10, PSI-159); solid 0 in every pressure bin.
- The pressure bin is "around 70.3 kPa", not "at or below 70.3". The FLEX tests set to 0.7 atm are recorded between 70.2 and 72.6 kPa; a strict "at or below 70.3 kPa" would keep 2 of them. If the screen says "10.2 psi or less", word it as "around 10.2 psi or lower" or show the kPa range.

The bins are the team's choice, not NASA's. Please label the grid as a count of recorded tests, and keep the `not_recorded` column visible: it is where all the solid tests are.
