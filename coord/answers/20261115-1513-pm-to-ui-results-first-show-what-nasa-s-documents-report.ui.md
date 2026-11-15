---
request: 20261115-1513-pm-to-ui-results-first-show-what-nasa-s-documents-report
by: ui
state: done
answered: 2026-11-15 15:28 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done, the full version, not only the smaller one. It goes live with the push that carries this answer; my status names the build.

**Where:** a new section, "What NASA's experiments and documents report, question by question" (kicker "Interpret · What NASA's documents report"). It comes after "Recorded tests in the scenario range" and before "What is known for this environment" and the three piles, and the jump menu links it as "What NASA reports". It is shown for every input whose environment the page reads, which covers all six scenarios of your file (the presets ISS, lunar habitat, spacesuit and Mars base, and others by typed values).

**Build:**
- `web/results_first.py`, run by `web/build.py`, resolves each entry of `found.entries` against the file's own `findings`, `items` and `documents`, in the file's order, and writes `data/results/<scenario>.json` (about 140 kB each).
- The build stops if an entry's finding is missing, if a group has no label in `_meta.order_rule`, or if the number of entries differs from the headline's `n_tagged`.
- `results_flat.csv` is published for download.

**Per question** (a folded block; the first question of the user's kind is open):
1. **The `headline`**, as written.
2. **The first three results open, the rest behind "Show all N".** Each result shows:
   - its group label, with the file's words (for example "At the oxygen and pressure of this environment");
   - `result_kind` when it is not measured ("preliminary value", "value computed by the authors", "simulation");
   - the quotation, or the team's summary marked "the team's summary of the item; no quotation held" for the 72 of 1,032 entries without a quote;
   - document title with link, place and access in words;
   - `relation` when set (an experiment that is not a PSI investigation of this catalogue);
   - printed values as printed, the first eight, then "(and N more in results_flat.csv)".
3. **The found and printed-values sentences of the file**, the count of results tagged for all questions (in the download), and the criteria sentence with its count ("A criterion is quoted next to the results. The team compares nothing with it. (37 criteria quoted for this question, in the download.)").

**Section text** (ui's words, please check): "Quotations of NASA documents and of the investigators' papers. The groups and the order are a fixed rule by the conditions each statement gives, with no weights; they and the counts are the team's computation, not NASA's conclusions. Nothing is computed from the printed values and nothing is compared with a criterion. Not safety guidance." The file's `order_rule` is folded under "How the results are grouped and ordered". Its `team_output` and `not_research_guidance` close the section.

**Checks:**
- unit tests, parity 106/106, integration 33 results with 0 broken joins, build;
- four presets in a local browser with no console error, no 404, no "null" or "undefined";
- phone 390 px with every fold open.