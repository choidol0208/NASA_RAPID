---
request: 20261114-1630-pm-to-ui-u5-captures-the-four-page-captures-the-seven-sli
by: ui
state: accepted
answered: 2026-11-14 16:40 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Accepted. I take the captures from the public page right after the 19:00 freeze and the switch of the Pages trigger to `main`, about 19:15. They go in `web/media/` as PNG, at least 1600 px wide, taken at 2x on a 1280 px wide page. My status will name the build commit they show.

| File | Slide | What it shows |
|---|---|---|
| `slide1_top.png` | 1 | The masthead (title, lede, the challenge sentence, the notice line), "What are you building, and where?" and the example buttons. There is no logo on the page. |
| `slide2_iss_result.png` | 2 | The section head with the team-computation note, then BASS-II with its team score, the strip, Why, Largest gap and the links. |
| `slide3_iss_needs.png` | 3 | The section head with the "team's reading" note, then the needs table for `ISS`: Prevention, Suppression and Detection column groups, one row per investigation. |
| `slide7_iss_tests.png` | 7 | "Recorded tests in the scenario range" for `ISS`, with the first list of test ids opened and the line of links under the table. |
| `04_lunar_evidence_map.png` | 5 (option) | Already taken at 16:31 with the axis ending at 45%; I retake it with the others. |

The capture script (`web/capture_media.mjs`) already has these four views; a trial run from the live page passed.
