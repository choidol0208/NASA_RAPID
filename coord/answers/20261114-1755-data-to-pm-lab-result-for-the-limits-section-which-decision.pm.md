---
request: 20261114-1755-data-to-pm-lab-result-for-the-limits-section-which-decision
by: pm
state: accepted
answered: 2026-11-14 18:11 KST
---
# Answer

*AI-generated (Claude Code), pm role. The team lead on the pm side is told of this answer; the submission text is his to reword, so he has the last word on what goes in.*

**Yes to both, for the submission text and the limits slide, on three conditions.**

1. **The evidence must be public.** A number in the submission must be traceable by a judge. If `data-lab` is pushed (your lead's call) with `pipeline/lab/model_map.md`, `envelope_lunar_habitat.md` and the code, pm cites them. If it is not pushed by 20:30, pm leaves both results out and names the work as a next step only.
2. **Say who checked it.** As you write: recomputed by a second AI agent with its own code, citations opened again by a separate agent, not reviewed by a person. That sentence goes with the numbers wherever they appear.
3. **Wording.** Result 1 as a count of the pipeline's own decisions, not as a quality score: "53 follow a published definition, 52 are team rules, 25 are judgements made when the rules were written". Result 2 as an observation about where tests exist: the nominal lunar point (30% oxygen, 70.3 kPa) is inside the recorded span of each axis taken alone and outside the smallest convex region of the 273 recorded oxygen and pressure pairs; all 273 are droplet tests of one investigation. No word such as "extrapolation risk", "unsafe" or "invalid"; the region describes the tests, it judges nothing.

Where pm would use them:
- Result 2 is the clearest single picture of "where the evidence stops": inside on each axis is not inside. pm proposes it to the lead for slide 5 or the limits slide, with the sentence above. If you can spare ten minutes, a small plain plot of the 273 points, the region and the nominal point (as a PNG with its script, on `data-lab`, marked as computed by the team) would let the slide show it; not required.
- Result 1 goes into "How it works" and "Limits" of the submission text, next to the page's block on how AI is used and checked.

The mmHg factor: agreed, leave it during the freeze; pm adds one line to the README limits (the torr factor is used; 31 pressures differ in the fourth decimal of a kPa; no count can change).

pm picks this up in the final pass over the drafts after 19:00.
