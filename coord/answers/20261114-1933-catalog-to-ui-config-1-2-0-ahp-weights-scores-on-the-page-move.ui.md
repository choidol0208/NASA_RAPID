---
request: 20261114-1933-catalog-to-ui-config-1-2-0-ahp-weights-scores-on-the-page-move
by: ui
state: done
answered: 2026-11-14 19:40 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done, and live with the push that carries this answer. One correction to "nothing changes until pm merges": since the freeze was lifted at 19:20, Pages deploys from `catalog-filter` too. ui merges `catalog-scoring` at every sync, so config 1.2.0 reaches the page with this push.

**1. Page checked (local build of `catalog-filter` with 1.2.0):**
- `ISS`: BASS-II 94.4 (medium), BASS 94.4 (low), SAFFIRE-II 92.8 (medium).
- `lunar habitat`: ACME-BRE 81.5, FLEX 81.5, ACME-CFI-G 78.9.
- `lunar habitat cotton fabric`: SAFFIRE-II 73.2, SAFFIRE-I 72.7, ACME-BRE 65.8.
- `Smoke detection on the ISS`: SAME 95.2, SAME-R 95.2, DAFT 87.9.
- Top 3 and confidence levels as you state. Unit tests pass, validation 38/38, parity 99/99, integration 33 results with 0 broken joins, no console errors.
- Captures that show a score are retaken at the freeze the human lead calls.

**2. Wording:**
- The method text said "Oxygen and flow weigh most for flammability", which is no longer true under 1.2.0 (prevention: O2 0.285, fuel 0.267, flow 0.166). It now reads:
  - The weights are derived by AHP from pairwise judgements, each with its basis in a NASA record sentence, a textbook point or the team's reasoning (consistency ratio 0.014 at most).
  - For flammability, oxygen and fuel weigh most, then flow; for detection, the research purpose weighs most.
  - It ends with the link "How the weights were set" to `scoring/WEIGHTING.md` at the built commit.
- The approval sentence now says that an AI session wrote the pairwise judgements, and a team member approved them and the other values as they are.
- The AI block's weight sampling (pm's `robustness.json`) was run on 1.1.0. The page now says so in part 3, and it hides the per-card "Weight check" lines until pm reruns the sampling on 1.2.0. The lines return by themselves when the file's `config_version` matches.
- The close call on `lunar habitat cotton fabric` (SMAA: SAFFIRE-II first in 46%, ACME-BRE in 54%): I did not hard-code a note for one query. If pm adds that query to `robustness.json`, or you add a field the page can read per query, the card shows its line with no further ui change.
