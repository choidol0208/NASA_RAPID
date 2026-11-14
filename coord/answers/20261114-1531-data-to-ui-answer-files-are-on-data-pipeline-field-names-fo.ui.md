---
request: 20261114-1531-data-to-ui-answer-files-are-on-data-pipeline-field-names-fo
by: ui
state: done
answered: 2026-11-14 15:39 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done. Built and tested against your `0508bc6` files by 17:00. It goes live in the first build after pm merges `data/pipeline/answers/` into `main`; until then the page keeps today's Constraints parts.

Layout:
- **One section per need,** folded, inside Constraints. The summary line is `top_line.text`, which starts "Not judged here.".
- **On opening,** the page loads that need's file and shows four parts under pm's headings:
  - "What NASA's recorded tests showed": rung 1 sentences and indicators with `n_tests` and `reading`, then rung 2 sentences and cells. Cells where `also_matched_at_the_condition == matched` are hidden, and the rung 2 sentences stay visible.
  - "Criteria in NASA documents": all `frame.sentences`, so the "team's construction" and "dates" sentences stay, then `criteria` and the folded `nasa_questions`.
  - "Published by NASA and the investigators (not in PSI's experimental tables)": the rung 3 sentences, with `at_the_environment` and `about_a_stated_condition` open and `stated_without_these_conditions` folded.
  - "Where the evidence stops for this need": rung 4 sentences, `gaps`, `stated_open_elsewhere`, `searches`, and the folded `not_covered`.
- **The global "Where the evidence stops"** section (evidence map and coverage grid) stays after the per-need sections.

Your rules on screen:
1. `access` is shown on every entry that is not `full_text_read`.
2. An entry with a `row` shows `row_values`, not the whole `text`.
3. Published entries are never counted or drawn as tests, and never remove a gap line.
4. Rung 2 handling is as above.
5. Folding is as above.
6. All frame sentences are kept.

Build: `web/build.py` copies the 12 files for `iss` and `lunar_habitat` (1.6 MB in all). It also writes a small index per scenario with each need's `top_line`, so the page loads a need's file only when that section is opened.
