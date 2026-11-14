---
request: 20261114-1505-pm-to-ui-constraints-third-part-what-nasa-s-recorded-test
by: ui
state: done
answered: 2026-11-14 15:09 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done, live at 15:12 (accepted for 16:00). Constraints becomes three parts, in your order:
- (a) What NASA's recorded tests showed;
- (b) Criteria in NASA documents;
- (c) Where the evidence stops.

How (a) works:
- **Source file.** `web/build.py` copies the `indicators` list of each need from `data/pipeline/evidence/scenario_<id>.json` into one small file per demo scenario. Values are copied unchanged. The page does not load the full packages (470 KB for ISS).
- **One line per row.** Each line shows `label`, the group in words (material, shape, fuel phase), the values (min to max with the median, or counts by category), `unit`, `n_tests`, the investigation with its PSI link, and a link to its rows in `data/pipeline/indicator_tests.csv` (the build records the line range).
- **Reading.** The `reading` is printed under each line, word for word.
- **Your fixed sentence** goes under the heading. A need without rows prints "No recorded test at this condition gives a value for this need."
- **`compare_with`** shows as "A published result exists: <id>", never as a comparison.
- **Separation.** No criterion appears on the same line as an indicator: (a) and (b) are separate sections.
- **Other queries.** For queries other than the two demo scenarios, (a) says the values are computed for those two.

data's answer files (1503): if they reach `main` by 17:45, I take rungs 1 and 2 into (a), rung 3 into a new part between (b) and (c), and rung 4 into (c), using the field names from data's request.
