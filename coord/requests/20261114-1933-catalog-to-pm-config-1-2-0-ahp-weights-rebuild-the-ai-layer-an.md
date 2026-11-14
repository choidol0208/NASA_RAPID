---
from: catalog
to: pm
opened: 2026-11-14 19:33 KST
needed_by: 21:00
closed: true
---
# config 1.2.0 AHP weights - rebuild the AI layer and update the scores in the submission text

*AI-generated (Claude Code), catalog role.*

## What I need

`catalog-scoring` (`11c307a`, merged with `main`) changes `scoring/scoring_config.json` to **1.2.0**. The human lead decided at 19:26 KST to apply profile weights derived by the analytic hierarchy process (AHP). Only the seven weights of each profile change.

Please, at the next integration:
1. **Merge `catalog-scoring` into `main`.**
2. **Rebuild the AI layer.** `data/insights/robustness.json` records the sha256 of the old `scoring_config.json` in `_meta.inputs_sha256`, and its Dirichlet draws are centred on the old weights. Run `ai/build_all.py` after the merge.
3. **Update the scores in `docs/submission/`.** `submission_text.md`, about line 522, cites the ISS scores "94, 94, 92.7". The top 3 and the confidence levels are unchanged in all four presets; the scores move:

| Query | 1.1.0 | 1.2.0 |
|---|---|---|
| ISS | BASS-II 94.0, BASS 94.0, SAFFIRE-II 92.7 | 94.4, 94.4, 92.8 |
| lunar habitat | ACME-BRE 79.1, FLEX 79.1, ACME-CFI-G 76.1 | 81.5, 81.5, 78.9 |
| ISS cotton fabric | BASS 95.1, SAFFIRE-III 95.1, BASS-II 94.0 | 95.4, 95.4, 94.2 |
| lunar habitat cotton fabric | SAFFIRE-II 75.3, SAFFIRE-I 74.9, ACME-BRE 65.5 | 73.2, 72.7, 65.8 |

4. **Where the text says how the weights were set,** use this, or point to `scoring/WEIGHTING.md`. Please keep the last sentence:
   > The weights of each question type are derived by the analytic hierarchy process from 51 pairwise judgements (consistency ratio 0.006 to 0.014, limit 0.10). Each judgement cites a NASA PSI record sentence, a textbook point or the team's reasoning. An AI session wrote the judgements, and the human lead approved them.

## Why

- The pm role owns the AI layer and the submission drafts. If they are not rebuilt and updated, the robustness file and the submission text no longer match the scorer.
- Checks on `catalog-scoring`: 45 of 45 unit tests, 38 of 38 scenarios, parity 99 of 99, source check clean.

## Until then

- Nothing on `main` is broken; it keeps the 1.1.0 weights until the merge.
- I will append my rows to the two compliance logs only after you say the English swap is on `main`.
