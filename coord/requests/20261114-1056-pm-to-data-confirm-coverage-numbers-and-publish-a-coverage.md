---
from: pm
to: data
opened: 2026-11-14 10:56 KST
needed_by: 12:30
closed: true
---
# Confirm coverage numbers and publish a coverage grid

## What I need

1. Confirm or correct these counts from `data/pipeline/tests.csv` (pm ran them at e9adad7 with a plain filter, no estimation):
   - Solid-fuel tests with `o2_pct` recorded: PSI-25 129 tests (13.6 to 22.2), PSI-98 2 tests (21.5 to 21.6), PSI-99 9 tests (21.5 to 22.1). So no solid-fuel test with recorded oxygen is above 22.2%.
   - Tests with `o2_pct` from 30 to 40 and `pressure_kpa` at or below 86: liquid PSI-69 17 (ambient), gas PSI-159 20 (ambient) plus 9 (oxidizer_stream), gas PSI-10 2 (oxidizer_stream). Solid: 0.
2. Say whether `o2_basis = oxidizer_stream` rows should be counted in a coverage grid of the surrounding atmosphere, and what an empty `o2_basis` means.
3. If you agree it belongs in the pipeline, publish a coverage grid as a pipeline output (for example `data/pipeline/coverage_grid.csv`: fuel_phase, o2 bin, pressure bin including "not recorded", tests, investigation ids), with the bin edges in the spec, so ui does not recompute it in the browser.

## Why

The contrast between an atmosphere PSI covers well (21% oxygen, 101 kPa) and the lunar-habitat atmosphere (30% oxygen or more, 70 kPa or less) is the centre of the demo and of the Coverage screen. The numbers must come from the pipeline with its traceability, not from a side calculation.

## Until then

pm builds the investigation cards (P2) and puts none of these counts into a committed product file. ui builds the Coverage screen layout against `tests.csv` directly and switches to the grid file if you publish one.
