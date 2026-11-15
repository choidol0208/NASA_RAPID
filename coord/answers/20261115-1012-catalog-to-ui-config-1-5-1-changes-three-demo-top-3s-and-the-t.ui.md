---
request: 20261115-1012-catalog-to-ui-config-1-5-1-changes-three-demo-top-3s-and-the-t
by: ui
state: done
answered: 2026-11-15 10:24 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done.
1. **The table note** in `web/index.html` now reads your sentence: "Scores within 3 points of the best remaining score are ordered by how much of the score rests on recorded values (recorded share), then by evidence quality, so a slightly lower score can sit higher." The near-tie tag on a result card now reads "near-tie, ordered by recorded share, then evidence", with your `tie_note` string as its tooltip.
2. **Fixed text naming a demo top 3:** none in ui's files. The page builds every top 3 from `rank()`, and `web/README.md` names no result. The captures in `web/media/` (14 Nov, 19:07, build `7239a2e`) show the 1.1 to 1.4 results and are retaken at the freeze the human lead calls.
3. **Also seen:** pm's `robustness.json` was sampled on an earlier config, so the page hides the per-card weight-check lines and says why (as since 19:41 yesterday) until pm reruns it on 1.5.1.

Checks after merging 1.5.1: unit tests, parity 104/104, integration 33 results with 0 broken joins and 156 requirement cells, build.