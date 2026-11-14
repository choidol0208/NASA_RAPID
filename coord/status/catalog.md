---
role: catalog
updated: 2026-11-14 19:38 KST
state: working
blocked_on: none
---
*AI-generated (Claude Code), catalog role.*

Now: owner of `data/catalog/`, `scoring/`, `validation/`, `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`, `web/scorer.js` and `web/parity_check.*`. **Config 1.2.0 is on `catalog-scoring`, waiting for pm's integration** (request 1933, no answer yet). The freeze is lifted (pm 1920; answered `done` with the plan for the extra day). Inbox empty.

**19:38 check of `main` and the live site against `catalog-scoring`:**
- `git log origin/main..HEAD` on the catalog paths lists `11c307a` (config 1.2.0) and `3ef2ae8` (status). Both are covered by request 1933 to pm; no new request. `origin/catalog-filter` does not have them yet either.
- `.github/workflows/pages.yml` deploys on pushes to `catalog-filter` and `main`:
  - on `main` it was never switched;
  - on `catalog-filter`, ui switched it to `main` only at 19:05 and back to both at 19:25, after the freeze was lifted;
  - so 1.2.0 goes live with whichever of the two branches first merges `catalog-scoring`.
- 11 demo queries on a worktree of `origin/main` (1.1.0) against HEAD (1.2.0):
  - same status, warnings, `not_understood`, configurations, confidence and result warnings in all 11;
  - scores differ as 1.2.0 intends, by at most 3.1 points here (`spacesuit` 19.4 → 16.3);
  - one reason text changes order (`ISS cotton fabric`, BASS-II-C04: the O2 match now comes first).
- Live site: `data/scoring_config.json` is 1.1.0 and equals `main` outside `_about`. `scorer.js` and `data/configurations.csv` are byte-identical to the local files.
- Checks on HEAD: 45 of 45 unit tests, 38 of 38 scenarios, parity 99 of 99, source check clean. The demo top results are unchanged, so the verification sheet was not rebuilt.

Done since last sync:
- **19:26 config 1.2.0: the profile weights are derived by AHP (the human lead's decision).**
  - `scoring/ahp_judgements.json` holds 51 pairwise judgements on Saaty's 1–9 scale, each with its basis: a NASA PSI record sentence, a textbook point or the team's reasoning. An AI session wrote them; the human lead approved them as they are.
  - `scoring/derive_weights.py` takes the principal eigenvector of each matrix as the weights. CR is 0.012 (prevention), 0.014 (detection) and 0.006 (suppression), against a limit of 0.10.
  - A unit test locks the config to the derivation.
  - New weights:
    - prevention: o2 0.285, fuel 0.267, flow 0.166, geometry 0.111, pressure 0.090, role 0.081;
    - detection: role 0.458, fuel 0.221, flow 0.136, o2 0.085, geometry 0.051, pressure 0.049;
    - suppression: role 0.286; fuel, o2 and diluent 0.162 each; flow 0.089, pressure 0.080, geometry 0.059.
  - Effect:
    - the four presets keep their top 3 and confidence levels; scores move by at most 3.3 points (`ISS` 94.4, 94.4, 92.8);
    - 35 of 38 scenarios keep their top 3, and the other 3 change at rank 2 or 3; all 38 pass.
- **New checks** in `validation/sensitivity.py`, also in `validation/report.md`:
  - every profile with each weight ×0.5 and ×1.5: 146 of 152 keep the top 3, and rank 1 changes once;
  - equal weights and rank-order-centroid weights;
  - each profile's queries with the other profiles' weights: the purpose changes the top 3 in 5 of 8 detection and suppression queries;
  - SMAA keeping only the order of importance: rank 1 holds in every draw for 9 of 12 queries;
  - `lunar habitat cotton fabric` has no clear winner (SAFFIRE-II 46%, ACME-BRE 54%).
- **`scoring/WEIGHTING.md` (new; teammates asked):** how the purpose is read, the technique (weighted sum, rescaling, gate, evidence factor), the AHP derivation, the record sentences behind each judgement, the checks, the limits and next steps. `METHOD.md`, the README, `MODEL_BASIS.md` and `PARAMETER_REVIEW.md` are updated to 1.2.0.
- Checks: 45 of 45 unit tests, 38 of 38 scenarios, parity 99 of 99, source check clean. The verification sheet was rebuilt: 96 checks; `lunar habitat` rank 4–5 now brings ACME-S-FLAME-C01 in place of FLEX-2-C01. No row had a human entry.
- Requests opened:
  - pm 1933: merge, rebuild the AI layer (`robustness.json` hashes the old config), and update the four preset scores and the weighting sentence in `docs/submission/`;
  - ui 1933: check the page after integration and retake score captures at the final freeze; optional wording for the close call.

Next:
- After pm says the English compliance logs are on `main`: merge `main`, then append my rows to `AI_USAGE_LOG.md` (AHP and SMAA work, 19:00–19:36) and `SOURCES.md` (Saaty 1980; Lahdelma, Hokkanen and Salminen 1998; Barron and Barrett 1996, method references).
- After pm's integration: check that `main` and the live site give the 1.2.0 scores for the four presets.
- Extra day (as in my answer to 1920): more detection and suppression scenarios; a rank-1 acceptability field for close calls, if ui agrees; the human check of the verification sheet, which needs a person.
- Weights change only through `scoring/ahp_judgements.json` and `scoring/derive_weights.py --write`, with the human lead's decision. After any change, rerun the tests, validation, sensitivity, parity and the verification sheet, and tell pm the numbers.

Published for others:
- `scoring/scoring_config.json` 1.2.0: same keys and shape; the seven weights of each profile changed, plus the `_about` and `rationale` text. `config_version` in `rank()` output is `1.2.0`.
- `scoring.scorer.rank` and `web/scorer.js`: unchanged code, same output shape.
- `data/catalog/*.csv`: unchanged since 19:00.

Notes for other roles:
- pm: the submission text can say "the weights of each question type are derived by the analytic hierarchy process from 51 pairwise judgements (consistency ratio 0.006 to 0.014, limit 0.10), each citing a NASA PSI record sentence, a textbook point or the team's reasoning; an AI session wrote the judgements and the human lead approved them".
- pm: earlier numbers that changed: unit tests 39 → 45; weight sensitivity "45 of 48, rank 1 never changes" → "146 of 152 over all three profiles, rank 1 changes once"; other values 129/136 → 127/136. In that last check `ISS` now changes at rank 3 in 2 runs.
- Earlier history of this status is in git (`git log -p coord/status/catalog.md`).
