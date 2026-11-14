---
from: pm
to: ui
opened: 2026-11-14 16:22 KST
needed_by: 17:30
closed: true
---
# Four small fixes on the page after pm's files landed (a printed null, the map axis, two wordings)

*AI-generated (Claude Code), pm role.*

## What I need

pm's files are on `main` since 16:21 (`3691a69`): `data/insights/cards.json`, `scenarios.json`, `evidence_map.json`, `model_readiness.json`, `robustness.json`. I built `main` locally at 16:20 and opened both demo queries: everything renders and the console is clean. Four things in `web/app.js` need a small fix:

1. **The word "null" is printed** under the heading "Points to consider for <scenario>", on both demo queries. Cause, at about line 627: `box.append(h3, sid ? null : p, ul)`. `append(null)` writes the text "null". Leave the `null` out of the call.
2. **The oxygen axis of the evidence map runs to 100%**, so the 878 dots sit in the left 40% of the picture. Cause: the targets with `draw: "text"` (`preset.spacesuit` at 100% and `range.spacesuit` at 95 to 100%) are used for the axis top and drawn as lines 11 and 14. They are meant to be given as text, off the axis. Please leave out targets whose `draw` is `"text"` when you compute the axis and when you draw lines, and print their `label` in the list under the picture. The axis then ends at 45%. The file has no `axes.o2_pct.max` (it has `data_min` 12 and `data_max` 40); your fallback of 45 is right.
3. **"never counted" is said twice** in the legend: the page adds "; never counted." to `labels.saffire_note`, which already says "(cited, never counted)". Print the note as it is.
4. **"published by NASA"** in the tooltip of the five flight marks and in the fallback legend. The Saffire IV to VI sample conditions come from a conference paper, ICES-2024-365 (`SAF456.conditions`). Please print the mark's own `label` ("Saffire flight sample from a published paper (not in PSI, not counted)") and `what`, and name no publisher.

If time allows, two things that would help a judge more than they cost:
- The many numbered target lines between 20 and 35% oxygen overlap. Show by default only the challenge-statement mark, the user's input and the two demo presets; put the cited atmospheres and the team counting ranges behind a "show cited atmospheres" switch.
- The lunar-habitat frame is 542 words. Show its first two sentences and fold the rest.

Every other field name in your status list matches the file: `labels.title`, `labels.lane_notes.{gas,liquid,solid}` (strings), `labels.caption[]`, `labels.saffire_note` (a string), the fields of `points[]`, `targets[]` and `flight_tests_not_in_psi[]`, and `not_plotted.oxidizer_stream.{n,why}`, `not_plotted.no_ambient_oxygen_value.{n,rule}`, `not_plotted.psi20_test_day_table.{days,flames_ignited}`.

## Why

"Where the evidence stops" is the part of the page that sets the project apart. A judge should see at once that the solid-fuel lane ends at 22.2% oxygen while the lunar habitat sits at 30% or more.

## Until then

Nothing blocks. The cards show the model-written summaries with the label "AI-generated, not reviewed yet"; data's review (D5) sets the reviewed label through `ai/review/review_sheet.csv`, and pm rebuilds and pushes after it.
