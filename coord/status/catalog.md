---
role: catalog
updated: 2026-11-14 20:03 KST
state: working
blocked_on: none
---
*AI-generated (Claude Code), catalog role.*

Now: owner of `data/catalog/`, `scoring/`, `validation/`, `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`, `web/scorer.js` and `web/parity_check.*`. Config 1.2.0 is live: ui merged it into `catalog-filter`, and Pages deploys from there again. **Building up the weighting model (the human lead's direction, 19:40): less dependence on AI judgement, requirements read in a systems-engineering way, weights from NASA data and combustion science.** Inbox empty.

**20:03 build-up, on `catalog-scoring` (no weight or score change yet):**
- `b353272` **Requirements layer.**
  - `rank()` returns `requirements`: one per condition the query sets, with its source (stated, implied by preset, derived, assumed) and the catalog columns that verify it.
  - Each result gets `compliance`: met, near, not_met, unverified or not_scored. Python and JS; parity 99 of 99 with both fields.
  - Request 2001 to ui: show it as a requirements table.
- `b353272` **Data stream** (`scoring/derive_data_weights.py` → `scoring/data_weights.json`).
  - Read from the NASA FLEX table (PSI-69, 274 ISS droplet tests).
  - Method: OLS on a log-linear model, LMG/Shapley share of R² per condition, 1000-sample bootstrap.
  - Burning-rate constant: O2 49%, diluent 34%, size 13%, fuel 2%, pressure 2%.
  - Extinction diameter ratio: O2 36%, fuel 35%, size 14%, diluent 13%, pressure 2%.
  - The four theory checks against the d² law hold: the O2 elasticity 0.88 lies between 0 and 1, the pressure effect is small, He raises K and CO2 lowers it.
- `0d1b086` **Expert stream.**
  - `scoring/expert_form.csv` holds the 51 AHP pairs for team members with combustion training. It shows the NASA evidence and hides the AI's answers.
  - `scoring/derive_expert_weights.py` computes each person's CR and the group geometric mean. Filled forms go in `scoring/expert_judgements/E1.csv` and so on, with no names.
- `0d1b086` **Pooling** (`scoring/weight_streams.json`, `apply` false). A log-linear pool of judgement and FLEX data over o2, pressure, diluent and fuel for suppression.
  - If applied, the weights become o2 .204, fuel .202, diluent .124, pressure .036.
  - All 38 scenarios keep their top 3; scores move by at most 2.8 points.
  - Applying it is the human lead's decision.
- Checks: 54 of 54 unit tests, 38 of 38 scenarios, parity 99 of 99.

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
- `scoring/scoring_config.json` 1.2.0: the seven weights of each profile changed (AHP), plus the `_about` and `rationale` text; new section `requirements` (labels and verifying columns of the requirements layer). Other keys unchanged. `config_version` in `rank()` output is `1.2.0`.
- `scoring.scorer.rank` and `web/scorer.js`: same scores; two additive output fields, `requirements` (top level) and `compliance` (per result), as described in request 2001.
- `data/catalog/*.csv`: unchanged since 19:00.

Notes for other roles:
- pm: the submission text can say "the weights of each question type are derived by the analytic hierarchy process from 51 pairwise judgements (consistency ratio 0.006 to 0.014, limit 0.10), each citing a NASA PSI record sentence, a textbook point or the team's reasoning; an AI session wrote the judgements and the human lead approved them".
- pm: earlier numbers that changed: unit tests 39 → 45; weight sensitivity "45 of 48, rank 1 never changes" → "146 of 152 over all three profiles, rank 1 changes once"; other values 129/136 → 127/136. In that last check `ISS` now changes at rank 3 in 2 runs.
- Earlier history of this status is in git (`git log -p coord/status/catalog.md`).
