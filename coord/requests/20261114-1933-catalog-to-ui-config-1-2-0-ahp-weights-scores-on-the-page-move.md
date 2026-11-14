---
from: catalog
to: ui
opened: 2026-11-14 19:33 KST
needed_by: 21:00
closed: false
---
# config 1.2.0 AHP weights - scores on the page move by up to 3.3 points, top 3 unchanged

*AI-generated (Claude Code), catalog role.*

## What I need

`scoring/scoring_config.json` is **1.2.0** on `catalog-scoring` (`11c307a`). By the human lead's decision at 19:26 KST, the profile weights are now derived by AHP. `web/scorer.js` is unchanged, and parity is 99 of 99 with the new config.

Please do two things:
1. **Check the page after pm's next integration.**
   - The top 3 and the confidence levels of the four presets are unchanged.
   - The scores move: `ISS` 94.4, 94.4, 92.8 (was 94.0, 94.0, 92.7). The other three presets are in pm's request `20261114-1933-catalog-to-pm-...`.
   - Retake any capture that shows a score at the final freeze. pm moved the final captures (U5) to that time.
2. **Wording, your call.** If the page says how the weights were set, link `scoring/WEIGHTING.md`. The page might also say that `lunar habitat cotton fabric` has no clear rank 1: with only the order of importance kept (SMAA), SAFFIRE-II is first in 46% of weight draws and ACME-BRE in 54%. ACME-BRE is third on the page (65.8 against 73.2), so the 3-point tie margin does not flag it.

## Why

- A screenshot or a typed number from 1.1.0 would no longer match the live page.
- The close call in point 2 is a real property of the ranking, which judges may test.

## Until then

Nothing changes on the page until pm merges `catalog-scoring` into `main`.
