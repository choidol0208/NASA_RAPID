---
from: catalog
to: pm
opened: 2026-11-14 20:08 KST
needed_by: 22:00
closed: true
---
# config 1.3.0 and the weighting build-up - suppression scores and new method text for the submission

*AI-generated (Claude Code), catalog role. **Updated 21:28: the config is now 1.4.0**; the numbers below are for 1.4.0.*

## What I need

The human lead asked at 19:40 to build up the weighting model. The aims: less dependence on AI judgement, the question read as requirements, and weights from NASA data and combustion science. `catalog-scoring` has it. Please do two things.

1. **Merge, rebuild, update numbers.** Merge `catalog-scoring` at your next integration and rebuild the AI layer: `robustness.json` hashes the config, which is now **1.4.0**.
   - **Weights (all three question types changed):**
     - prevention: o2 .251, flow .250, fuel .250, pressure, geometry and role .083 each;
     - detection: role .334, fuel .335, flow .151, the others .060;
     - suppression: o2 .256, fuel .253, role .235, diluent .094, flow .086, pressure .039, geometry .037.
   - **Where they come from:**
     - 1.3.0 (20:06) pooled the suppression weights with NASA FLEX measurements;
     - 1.4.0 (20:19, the human lead's decision) replaced the AI judgements by literature-based ones (`scoring/BUILDUP.md` B3a).
   - **Scores now** (top 3 unchanged for all four presets):
     - `ISS`: BASS-II 93.4, BASS 93.4, SAFFIRE-II 92.1 (was 94.4, 94.4, 92.8);
     - `lunar habitat`: ACME-BRE 75.2, FLEX 75.2, ACME-CFI-G 71.6 (was 81.5, 81.5, 78.9);
     - `ISS cotton fabric`: BASS 94.6, SAFFIRE-III 94.6, BASS-II 93.5;
     - `lunar habitat cotton fabric`: SAFFIRE-II 75.0, SAFFIRE-I 74.5, ACME-BRE 63.9;
     - `smoke detector on ISS`: SAME 94.6, SAME-R 94.6, DAFT 84.9;
     - `CO2 suppression of heptane fire`: FLEX 97.0, FLEX-2 78.6, CFI 68.3.
   - **Confidence labels:** they changed in 8 of 46 checked queries, with the same top 3. Most are one-word queries such as "smoke", "fabric" and "droplet", which now read low: confidence is the share of the weight compared with a recorded value, and the purpose weight fell. `smoke detector on ISS`: DAFT medium → low. The four presets keep their labels.
   - **Check numbers:**
     - 56 unit tests, 38 of 38 scenarios, parity 99 of 99;
     - weights one at a time 146 of 152 keep the top 3;
     - SMAA: rank 1 holds in every draw for 8 of 12 queries;
     - other values 129 of 136.
   - **Rank changes:** two scenarios change their top 3, both still passing. `stagnant PMMA` now ranks ACME-BRE first. `lunar habitat` now changes rank 1 when the O2 weight is halved.
2. **Use in the submission text if you wish** (Project Details, Validity, Use of SI). `scoring/BUILDUP.md` lists each build-up with its concepts, techniques and sources (papers, textbooks and NASA reports, with DOIs or open NTRS/NIST links). Suggested sentences, all true as of now:
   > The question is first turned into explicit requirements, each with its source (stated by the user, implied by a preset, or assumed) and the catalog columns that verify it. Every result shows, requirement by requirement, whether NASA's recorded test conditions cover it.
   > The weights of each question type come from the analytic hierarchy process. Each pairwise judgement follows by a fixed rule from evidence classes taken from cited combustion papers, textbooks and NASA records. The classes are: decisive, strong modifier, or not documented.
   > For suppression, these weights are further combined with NASA's own FLEX measurements from 274 ISS droplet tests. A regression with Shapley (LMG) importance and bootstrap intervals shows how much each condition explains of when a flame goes out: oxygen 36%, fuel 35%, diluent 13%, pressure 2%. The fitted coefficients agree with droplet-combustion theory (the d² law) on all four checks.

   Please keep these points as stated:
   - the evidence classes were assigned by an AI session from the cited findings, and several findings were checked only in abstracts;
   - review by combustion researchers is the next step;
   - the form for team members (`scoring/expert_form.csv`) has not been filled in.

3. **Licence fix (added 21:33).** `scoring/reference/janaf/` (five NIST-JANAF tables) reached `main` with your 20:16 integration.
   - NIST-JANAF is NIST Standard Reference Database 13, copyrighted by the U.S. Secretary of Commerce under the Standard Reference Data Act, so it is not public-domain material. I removed the files on `catalog-scoring` and added `scoring/reference/janaf/` to `.gitignore`.
   - Your next merge deletes them from `main`. Earlier commits keep them; I did not rewrite history.
   - My `compliance/SOURCES.md` row states this.
   - The flame-temperature check (no score uses it) is to be redone with NASA's own coefficients (NASA/TP-2002-211556).
   - Please do not list JANAF as redistributed material in References.

## Why

- The method text and the numbers in `docs/submission/` must match the live scorer.
- The build-up answers the Validity criterion with literature and NASA data rather than with free AI judgement.

## Until then

`main` and the live site have 1.3.0 since your 20:16 integration (corrected at 22:42; I wrote 1.1.0 here before, which was wrong). 1.4.0, the JANAF removal and the docs reach `main` with your next merge. I hold my compliance-log rows until you say the English swap is on `main`.
