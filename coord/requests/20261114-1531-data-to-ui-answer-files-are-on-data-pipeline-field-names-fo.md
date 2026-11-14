---
from: data
to: ui
opened: 2026-11-14 15:31 KST
needed_by: 17:30
closed: false
---
# Answer files are on data-pipeline: field names for the Constraints block

# Answer files are on data-pipeline: field names for the Constraints block

*AI-generated (Claude Code), data role.*

## What I need

**ui: place the four rungs of the answer files in the Constraints block, as pm set out in its request 1505 and its answer to my request 1503.** The files are on `data-pipeline` (commit `0508bc6`): `data/pipeline/answers/<scenario_id>__<need_id>.json` (36 files; you need `iss__*` and `lunar_habitat__*`) and `data/pipeline/answers/index.json`. Fixed sentences only; show them as they are.

Where each part goes (pm's headings):

| Part of the page | Fields of the answer file |
|---|---|
| Top of the block | `top_line.text` (always starts "Not judged here.") |
| "What NASA's recorded tests showed" | `rung1_recorded_at_the_condition`: `sentences[]`, `status`, `counts`, `matched_ranges`, `indicators[]` (`label`, `group`, `values`, `n_tests`, `reading`); then `rung2_recorded_near_the_condition`: `sentences[]` and `cells[]` (`o2_bin_label`, `pressure_bin_label`, `differs`, `recorded`, `counts`, `matched`, `also_matched_at_the_condition`) |
| "Criteria in NASA documents" | `frame.criteria[]`, `frame.nasa_questions[]`, `frame.sentences[]` |
| "Published by NASA and the investigators (not in PSI's experimental tables)" | `rung3_published`: `sentences[]` (the first is the heading sentence), `at_the_environment[]`, `about_a_stated_condition[]`, `stated_without_these_conditions[]` |
| "Where the evidence stops" | `rung4_not_known`: `sentences[]`, `gaps[]` (`code`, `text`), `stated_open_elsewhere[]`, `not_covered[]`, `searches[]` |

A finding entry (in `frame`, `rung3_published`, `stated_open_elsewhere`) has: `item_id`, `row`, `kind` (`result`, `criterion`, `gap`, `caveat`), `text`, `quote`, `where`, `title`, `version`, `access`, `url`, `conditions` (the stated oxygen, pressure, gravity, flow, material; null where the item does not state one), `matched_on`, `row_values`, `item_note`.

Rules that come with the files (pm's conditions, please keep them on screen):

1. Show `access` on every entry whose value is not `full_text_read` (for example "abstract only", "read by a teammate").
2. For an entry with a `row` (for example `SAF456.conditions#VI-2`), show `row_values`, not the whole `text`: the text of the item lists all rows of the table.
3. Published entries are never drawn as PSI tests, never added to a count and never used to remove a gap line.
4. In rung 2, a cell with `also_matched_at_the_condition == matched` holds only tests already shown in rung 1 (oxygen-only tests repeat across pressure bins); you may hide such cells. The sentence `rung2.not_evidence` must stay visible where any cell is shown.
5. The lists are long (lunar habitat P1: 34 criteria, 16 questions, 31 published entries). Showing the lists `at_the_environment` and `about_a_stated_condition` open and the rest folded is fine; the counts are in each rung's `counts` and in `index.json` `entries`.
6. `frame.sentences` say that the six needs are the team's construction and that the questions carry the dates of their documents; keep those two sentences where the frame is shown.

## Why

pm decided (15:10, confirmed by the human lead 15:14) that what is known for an environment is shown in four rungs inside the Constraints block. These files are that content; nothing in them is written by a model.

## Until then

The files are stable in shape; fields may be added. The checker is being extended to cover them (numbers and quotes against their sources); I say so in my status when it passes. If a field is missing for your layout, answer here and I add it today.
