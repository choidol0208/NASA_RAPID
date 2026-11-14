---
from: catalog
to: pm
opened: 2026-11-14 20:08 KST
needed_by: 22:00
closed: false
---
# config 1.3.0 and the weighting build-up - suppression scores and new method text for the submission

*AI-generated (Claude Code), catalog role.*

## What I need

The human lead asked at 19:40 to build up the weighting model. The aims: less dependence on AI judgement, the question read as requirements, and weights from NASA data and combustion science. `catalog-scoring` (`99f8a25`, `6202f9a`) has it. Please do two things.

1. **Merge, rebuild, update numbers.** Merge `catalog-scoring` at your next integration and rebuild the AI layer: `robustness.json` hashes the config, which is now **1.3.0**.
   - Only the suppression weights changed: o2 .204, fuel .202, diluent .124, pressure .036, role .286, flow .089, geometry .059. They are pooled with NASA FLEX measurements by the human lead's decision at 20:06.
   - The prevention presets (`ISS`, `lunar habitat`, the cotton-fabric pair) are unchanged from 1.2.0.
   - Suppression queries keep their top 3; scores now read:
     - `CO2 suppression of heptane fire`: FLEX 97.0, FLEX-2 76.0, CFI 68.9;
     - `fire extinguisher for a Mars habitat`: BASS 94.7, FLEX 83.2, BASS-II 72.5;
     - `nitrogen extinguish fabric fire ISS`: BASS 92.2, BASS-II 83.9, ACME-BRE 69.1.
   - Check numbers: 55 unit tests, 38 of 38 scenarios, parity 99 of 99, weights one at a time 147 of 152.
2. **Use in the submission text if you wish** (Project Details, Validity, Use of SI). `scoring/BUILDUP.md` lists each build-up with its concepts, techniques and sources (papers and textbooks with links). Suggested sentences, all true as of now:
   > The question is first turned into explicit requirements, each with its source (stated by the user, implied by a preset, or assumed) and the catalog columns that verify it. Every result shows, requirement by requirement, whether NASA's recorded test conditions cover it.
   > For suppression questions, the weights combine pairwise (AHP) judgements with NASA's own FLEX measurements from 274 ISS droplet tests. A regression with Shapley (LMG) importance and bootstrap intervals shows how much each condition explains of when a flame goes out: oxygen 36%, fuel 35%, diluent 13%, pressure 2%. The fitted coefficients agree with droplet-combustion theory (the d² law) on all four checks.
   > A pairwise-comparison form lets the team's combustion-trained members replace the AI session's judgements.

   Please keep these as a plan, not a result, until someone has filled the form:
   - the form: no person has filled it yet;
   - prevention and detection weights: still the AI session's AHP, since no NASA table records a spread rate or smoke size to learn from.

## Why

- The method text and the numbers in `docs/submission/` must match the live scorer.
- The build-up answers the Validity criterion with NASA data rather than AI judgement.

## Until then

`main` keeps 1.1.0 until your merge. The live page has 1.2.0 through `catalog-filter`, and gets 1.3.0 when ui next merges `catalog-scoring`. I hold my compliance-log rows until you say the English swap is on `main`.
