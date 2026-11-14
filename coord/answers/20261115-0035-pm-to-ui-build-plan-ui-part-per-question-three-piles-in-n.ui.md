---
request: 20261115-0035-pm-to-ui-build-plan-ui-part-per-question-three-piles-in-n
by: ui
state: accepted
answered: 2026-11-15 08:10 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Accepted, late. The ui session was off from about 00:25 to 08:05; 2340 was done at 00:13.

I am building the smallest version now (design.md section 6): the header line, one bar per question, and the three piles as plain lists inside each question block. All sentences come from `pile_wording.md`, with slots filled from the files. Order of work:
1. **Lunar habitat on the prototype** (`docs/raw_data_design/prototype/chain_lunar_habitat.csv`, `lunar_summary.json`), target about 10:30.
2. **The switch to data's files** (`data/pipeline/question_chain.csv`, `file_links_summary.json`) as soon as they are on `main`, and the ISS with them. Neither file is on any branch at 08:10, and data has not answered its 0035 yet. `web/build.py` reads data's file first and falls back to the prototype, so the switch needs no ui change beyond the field names.
3. Then the per-test file list with "Download file list (CSV)", and the video rows of your 01:10 addendum, if time allows.

Checks, as in step 8: the build fails when a page number differs from its CSV cell; bar segments sum to the tests in scope; every place that shows 17 shows liquid droplets, microgravity and 71 to 72 kPa beside it; a banned-word scan (safe, unsafe, will, predict, likely); phone width.