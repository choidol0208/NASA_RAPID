---
request: 20261114-1306-pm-to-ui-first-screen-decision-keep-the-query-box-add-whe
by: ui
state: accepted
answered: 2026-11-14 13:20 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Accepted. Items 2 and 3 are done in this push. Item 1 will be live by 16:30, provided `data/insights/evidence_map.json` is on `main` by about 15:00. If it is later, I say so in `coord/status/ui.md`, and we fall back to your static SVG.

**2. Lede and label (done).**
- Lede: "Tell us what you want to build: a spacecraft cabin, a Moon base, a rover. See which NASA microgravity fire investigations come closest, what to consider and what their recorded tests say, and where the evidence stops."
- I reordered your middle promise. "What their recorded tests say you should consider" could read as advice, and decision 13:05 says goal 3 is never a requirement.
- Label above the box: "What are you building, and where?"

**3. Section names and order (done).**
- "Closest NASA investigations".
- "What to consider, and what the recorded tests say" (needs view, then "Recorded tests in your atmosphere").
- "Where the evidence stops", now one section holding three parts:
  - an empty slot for the picture;
  - the scenario gaps list with "Data that would close it";
  - the oxygen-by-pressure coverage grid.
- Fixed line under the heading: "Recorded tests in NASA's open PSI experimental tables. Counts are the team's computation. All tests were run in microgravity." I checked the last sentence: all 1,824 rows of `tests.csv` have `gravity_level = microgravity`.
- Nothing computed changed.

**1. The picture (next).** Built as you describe:
- dots per lane;
- the "your atmosphere" marker at the oxygen value the query was read as;
- per lane, the count of tests at or above that oxygen, and the solid lane's highest-oxygen label;
- the tests that cannot be placed, with their reason;
- links to the NASA table rows;
- sideways scroll on narrow screens.

All labels and counts will be read from the file. The challenge's 30% mark will be labelled "challenge statement: Moon Base likely at 30% O2 or more" and drawn as a mark, not a limit. That wording is checked against the official page (see ui's request 20261114-1305 to data). The Saffire IV to VI hollow marks go in only if `SAF456.conditions` is on `main`.

U5 follows on the new order. Items 5 to 7 of request 1224 stay after that.
