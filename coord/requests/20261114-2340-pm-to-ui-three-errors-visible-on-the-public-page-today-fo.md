---
from: pm
to: ui
opened: 2026-11-14 23:40 KST
needed_by: 01:00
closed: false
---
# Three errors visible on the public page today (found by an analysis, each reproduced by a second agent)

*AI-generated (Claude Code), pm role.*

## What I need

The human lead asked pm for an analysis of the weak points of the features as they are. Five kinds of readers tried the real page; every finding was then reproduced by a second agent. Three of the findings are errors a judge can see today. Please fix them first; none needs a decision.

1. **The environment text (the frame) is cut at every decimal point.** `web/app.js`, `renderScenarioText`, about line 418: `sc.frame.match(/[^.!?]+(?:[.!?]+(?=\s|$)|$)/g)` drops everything up to a decimal point. For `lunar habitat` 1,457 of the frame's 3,184 characters are not shown and the first visible line starts "8 kPa); the bins ...". The lost part holds the sentence "No counted test was recorded at 30% oxygen or more and at or below 10.2 psi" and the drop-tower caveat. Both demo queries are affected.
   - Reproduce: build, open `?q=lunar%20habitat`, read the box under "ISS and lunar habitat, side by side" and its "Read the rest of the frame" fold; or run the regular expression on the frame in `data/insights/scenarios.json` and compare the joined matches with the frame.
   - Fix: split only at a sentence end followed by white space and a capital letter or an opening bracket or quote, for example `sc.frame.split(/(?<=[.!?])\s+(?=[A-Z("'])/)`. Add a check to `web/check_integration.py` that lead plus rest equals the frame text for every scenario. If you prefer, pm can also write the frame as a list of sentences (`frame_sentences`) next to `frame`; say so and it is in the next build.
2. **The list "What PSI does not contain for this environment" appears only for four exact inputs.** `scenarioNotes()` in `web/app.js` matches `e.query.trim().toLowerCase() === q`, and `data/insights/scenarios.json` holds the queries "ISS", "lunar habitat", "spacesuit" and "Mars base" only. The example buttons "Lunar habitat, cotton fabric" and "Smoke detection on the ISS" show the heading with nothing under it, so the answer to goal 4 and the caveat that the 17 tests are all fuel-droplet tests disappear.
   - Fix: choose the entry by the environment the page read from the input (the preset id), not by the input text; hide the heading when no environment was read.
3. **The first number on the page, "ISS cabin 4 of 6 · Lunar habitat 1 of 6", is the same for every input and reads wider than it is.** `scenarioCoverage` (about line 811) adds `tests_atmosphere + tests_oxygen_only + tests_pressure_only`. For `iss`, only S1 has tests with oxygen and pressure both in range (56, all FLEX fuel droplets); P1 (55), P3 (2) and D1 (45) match on oxygen only, with no pressure in the table.
   - Fix: show the environment of the user's input only; split "oxygen and pressure both in range" from "oxygen in range, pressure not in the table"; name the kind of test where all are of one kind (fuel droplets). For example: "ISS cabin: 1 of 6 questions with oxygen and pressure in range (extinction, fuel droplets only); 3 more with oxygen in range and no pressure in the table."
   - pm's slides quote "4 of 6" and "1 of 6"; pm changes them with you. Tell me the wording you settle on.

One line that costs little and answers a fourth finding: where a typed oxygen or pressure is shown as "(you)" but the counts are those of a preset range, print under the counts "Counted for the range 30 to 36% oxygen, not for the value you typed." (ranges from the scenario spec).

The full analysis (32 points, ranked, with a plan for the extra day) goes to the human lead tonight in his report; after he has chosen, pm opens requests for the rest. Please do not start on those yet.

## Why

Each of the three hides or blurs the project's main statement on the two pages the demo uses.

## Until then

pm changes nothing in `data/insights/scenarios.json` that would move these texts.
