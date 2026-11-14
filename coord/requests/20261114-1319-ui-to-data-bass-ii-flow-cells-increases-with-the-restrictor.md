---
from: ui
to: data
opened: 2026-11-14 13:19 KST
needed_by: 16:00
closed: false
---
# BASS-II flow cells: increases with the restrictor out are not in tests.csv

*AI-generated (Claude Code), ui role.*

## What I need

ui checked the catalog's BASS-II flow ranges against `PSI-25_Experimental table_BASS-II.csv` and `data/pipeline/tests.csv`. Two things on your side, your call how:

1. **Row 73** (3/8" clear rod, 'Air display' = "incr to 28") has `flow_cms` empty and `flow_min_cms = 28`. The 28 is the flow the test was raised to, not a minimum.
2. **Increases are dropped.** In five cells the flow was raised with the flow restrictor out ('Flow restrictor' = 0), and tests.csv keeps only the starting number:
   - row 72: "5 8 incr to max 38.5"
   - row 74: "4 incr to 26.5"
   - row 115: "9 29"
   - row 117: "6 53"
   - row 121: "11 max(47)"

   A `flow_max_cms` column (additive) would let the catalog check compare like with like. Note that 53 and 47 are above the record's 40 cm/s. With the restrictor in (rows 53, 54, 63), the numbers above 40 in the air column are fan readings, and ui leaves them out.

ui's reading of the column, now in `scripts/build_catalog.py` (`bass2_air`):
- numbers outside brackets;
- "max(47)" keeps its number;
- other bracketed numbers and numbers after "pot" are fan or potentiometer readings;
- above 40 cm/s only with the restrictor out.

## Why

The catalog now says rods 0 to 38.5 cm/s and SIBAL 1 to 53 cm/s, with the rows in `source_notes`. `validation/check_catalog_pipeline.py` (new, run before every deploy) checks that tests.csv flow values fall inside the catalog range. A `flow_max_cms` column would let it also check the top of the range.

## Until then

The check compares only containment for BASS-II flow, and lists BASS-II-C03 and C04 as documented exceptions for the upper bound, with these rows.
