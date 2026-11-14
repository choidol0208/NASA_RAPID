---
request: 20261114-1630-pm-to-ui-u5-captures-the-four-page-captures-the-seven-sli
by: ui
state: done
answered: 2026-11-14 19:07 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

## Done (19:07)

**Captured from the public page at 19:06–19:07, build `7239a2e`** (`data/build.json` commit `7239a2e364ec959102dddf339e57861f45872b2d`). That is your `main` build after the freeze integration (`abff173`), and since 19:06 Pages deploys from `main` only. All files are PNG at 2x on a 1280 px page, in `web/media/` on `catalog-filter`, and reach `main` with your next merge.

| File | Slide | Size | What it shows |
|---|---|---|---|
| `slide1_top.png` | 1 | 2560 x 1084 | The title, lede, challenge sentence and the notice line ("…not operational fire-safety guidance, and it is not endorsed by NASA."), then "What are you building, and where?" and the six example buttons. No logo. |
| `slide2_iss_result.png` | 2 | 2216 x 2194 | The section head with the team-computation note, then BASS-II: team score 94, the strip, Why, the team note, the warning, the tags, the links, the raw-data line, the video side-pilot line and the weight-check line. |
| `slide3_iss_needs.png` | 3 | 2216 x 1488 | The section head with the "team's pipeline reading" note, then the needs table for `ISS`: the scenario row, then BASS-II, BASS and SAFFIRE-II under Prevention, Suppression and Detection. |
| `slide7_iss_tests.png` | 7 | 2216 x 2292 | "Recorded tests in the scenario range" for `ISS`, with FLEX's 56 test ids opened and the line under the table ("1578 more recorded tests… Each test id links to its row in the NASA PSI table. Matching: data/pipeline/scenario_tests.csv"). |
| `04_lunar_evidence_map.png` | 5 (option) | 2160 x 778 | "Where the evidence stops" for `lunar habitat`: the axis ends at 45%, the solid lane ends at 22.2%, and "your input: 30% O2" is marked. |

The other U5 files were retaken in the same run: `01` to `07`, `og.png` (1200 x 630) and `demo_iss_to_lunar.gif` (2.4 MB). Every file is under 10 MB.

Two things to know:
- Slide 2's card is taller than in the 16:40 trial. Since then the card has gained the video side-pilot line (your 1709) and the weight-check line (your 1705). If the slide has no room for them, crop under "Raw data in PSI"; nothing above that line changed.
- If a later push of yours changes something these slides show, tell me and I retake that capture. Run `node web/capture_media.mjs https://choidol0208.github.io/NASA_RAPID/`, with `NODE_PATH` set to `npm root -g`.

## Accepted (16:40)

Accepted. I take the captures from the public page right after the 19:00 freeze and the switch of the Pages trigger to `main`, about 19:15. They go in `web/media/` as PNG, at least 1600 px wide, taken at 2x on a 1280 px wide page. My status will name the build commit they show.
