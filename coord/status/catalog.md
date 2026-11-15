---
role: catalog
updated: 2026-11-15 16:56 KST
state: working
blocked_on: none
---
*AI-generated (Claude Code), catalog role.*

**16:56: config 1.5.3 (pm 1648, challenge-fit check; weights unchanged; no demo top-3 change).**
- `partial_gravity` notice with its NASA source (Olson and Ferkul 2012, Table I, checked; OCHMO-TB-008) and the challenge's future sources (LUCI, FM2, E-FIELD).
- `not_understood` names what the ranking reads. "artemis" is no longer a lunar alias. "combustion chamber" is in scope.
- Mars hint with the sourced 8.0 psia / 32% O2 example. pm's "34% at 8.2 psi" is not the atmosphere that TP-2010-216134 recommends.
- `o2_above_all` names both 85% oxidizer streams. SLICE hardware comes from the PSI-106 record text.
- Answered 1648 `done`. Merged `main` and `catalog-filter`.
- pm 1619 and 1520 are open (by 17:30).
- Checks: 83 unit tests, 45 of 45 scenarios, parity 106 of 106, source check clean, integration 0 broken joins.

**Sync 16:33:**
- Merged `main` (pm: "match score" in the texts) and `catalog-filter` (ui's 1619 work).
- ui answered 1619 `done` (closed): "match score" with its tooltip on the cards and the table header; the AI tags shortened; the negatives dropped from ui's notes. The §5 line now also sits next to the scores.
- ui forwarded the remaining negatives to pm (1624): the footer notice, "team score" in `data/insights/scenarios.json`, the small print of the three piles, and the data role's `results_by_need.json`.
- pm 1619 (by 17:30) and pm 1520 (texts by 17:30) are open. Inbox empty.
- Checks: 79 unit tests, 45 of 45 scenarios, parity 106 of 106, source check clean, reading order up to date.

**16:20: the human lead asked (16:18) for fewer disclaimers on `how.html` and the shell, and for a clearer name than "team score".**
- Requests 1619 to pm (shell notices, `how.html`, `data/insights/` labels, submission texts, README) and to ui (`web/app.js` labels, the table header), with exact replacement text.
- The negatives go. Kept once each, worded positively:
  - the line that match scores and order are Team RAPID's computation from NASA PSI data (AGENTS.md §5);
  - the AI labels on AI-written text (§4).
- Name: **match score** (0–100, weighted similarity to the question), in `scoring/METHOD.md` 1.2. The scorer's output field stays `score`. No code or score change.

**Sync 16:16:**
- Merged `main`: pm's integrations of 16:03 and 16:06 (the new page shell, ui's results-first section, data's `results_top`). Config 1.5.2 is now on `main`, and the AI layer was rebuilt on it. Nothing new on `catalog-filter`.
- pm accepted 1520: the texts follow by 17:30, and B3 is taken as a rule for the deck. The request stays open until `done`.
- Fixed the two points pm found:
  - The validation numbers in `scoring/METHOD.md` 2 and `scoring/README.md` were from 1.2.0 and 1.4.0. They now come from the current `validation/report.md`: 124 of 136, rank 1 changes in 3 and 5, SMAA 7 of 12, 79 unit tests, 45 scenarios, parity 106.
  - `scoring/__init__.py` has an AI-generated header.
  - `scoring/WEIGHTING.md` 5.x is now marked as the numbers of config 1.2.0.
- Inbox empty.
- Checks: 79 unit tests, 45 of 45 scenarios, parity 106 of 106, source check clean, reading order up to date.

**15:22: config 1.5.2 on `catalog-scoring`: the human lead's decisions on review items B1–B5 (recommendations taken at 15:16; weights unchanged).**
- B3: a new top-level warning `no_material` when no fuel is named. The ranking is unchanged.
- B1: the gate is kept; "decisive is a large weight, not a veto" (`gate.decisive_is_not_a_veto`).
- B2: documented values keep their similarity (no 0.8 cap).
- B4: scores are compared within one question only (`_about.formula_scope`).
- B5: detection pressure stays in class 3, with the scope stated: smoke of overheated materials (`profiles.detection.scope`).
- Reasons are in METHOD 1.2, 1.5, 1.7 and 1.8, WEIGHTING 4.2 and 6, and BUILDUP B7.
- Requests 1520 to ui (show the warning; one line on comparing scores) and pm (texts; rebuild the AI layer).
- Checks: 79 unit tests, 45 of 45 scenarios (F11, F12 new), parity 106 of 106, source check clean, `web/check_integration.py` 0 broken joins. No demo top-3 change.

**10:13: config 1.5.1 on `catalog-scoring` (weights unchanged since 1.4.0).**
- **1.5.0 (09:52):** the combined model of the catalog and the data role's raw-file method, at the human lead's request. Reasoning: `scoring/METHOD.md` 1.7, `scoring/BUILDUP.md` B7.
  - Detection is matched per fire signature (gas or particulate). Gas questions rank BASS-II first.
  - Compliance lines carry a basis and the status `documented`. ui shows both (0945, done and closed).
  - The BASS-II pressure is `published` (ICES 2019). Team readings leave the confidence.
- **1.5.1 (10:10):** an AI review of the scorer (09:40) checked against the tables and the code; items A1–A3 fixed at the human lead's request.
  - A1: the five day tables (ACME PSI-20 to 23, SLICE PSI-106) are `summary_table`. The review named two.
  - A2: near-ties are ordered by recorded share, then evidence, then score (order-independent; `has_1g_comparison` dropped).
  - A3: "solid" and 고체 (solid) are read as the fuel phase.
  - DAFT measured a dust aerosol, not a fire, so it is no longer fire-signature evidence.
  - Part C is in METHOD 1.5 and 1.8, WEIGHTING 6 and BUILDUP B2 and B3a.
  - **Demo top 3s change:** ISS: BASS-II, SAFFIRE-I, SAFFIRE-II. lunar habitat: FLEX, ACME-CFI-G, ACME-BRE. ISS cotton fabric: BASS-II, SAFFIRE-I, SAFFIRE-II. Requests 1012 to ui and pm.
  - B1–B5 (gate, non-table values, solid default, cross-question scores, detection pressure) wait for the human lead's decision. The catalog changes nothing there before it.
- **pm 0035 done:** step 6 at 09:09; step 7 `validation/raw_chain_recount.py` at 10:12. 62 of 71 fixtures reproduce; the 9 misses are video link states, with four causes in the answer.
- **Inbox:** data 0927 answered: yes, the configuration-to-tests key of `web/check_integration.py`. data 0953 read.
- **Checks:**
  - 76 unit tests; 43 of 43 scenarios (D03 and F01 expectations changed, with reasons in `scenarios.json`; F09, F10 new);
  - parity 104 of 104; source check clean;
  - `web/check_integration.py` 0 broken joins;
  - weights match the derivation; reading order up to date.
- **For pm:** rebuild the AI layer at integration. `ai/test_robustness.py` was not run here (no numpy).

Now: owner of `data/catalog/`, `scoring/`, `validation/`, `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`, `web/scorer.js` and `web/parity_check.*`. Read at 16:56: `main` and `catalog-filter` run config 1.5.2; `catalog-scoring` runs 1.5.3.

**21:33 licence fix:** the five NIST-JANAF tables (`scoring/reference/janaf/`) are removed from the repository and ignored by git.
- NIST SRD 13 is copyrighted by the U.S. Secretary of Commerce, not public domain.
- They had reached `main` with pm's 20:16 integration; pm's next merge removes them, and request 2008 says so. History is not rewritten.
- `scoring/flame_temperature.py` now reads a local download. Next: redo it with NASA/TP-2002-211556.

**Compliance logs:** my rows are appended (3 in `AI_USAGE_LOG.md`, 23 in `SOURCES.md`), after merging `main` with pm's English logs.

**21:28 build-up, on `catalog-scoring`:**
- **Config 1.4.0: literature-based judgement stream** (the human lead's request at 20:16 and decision at 20:19).
  - The expert form is filled in from textbooks, papers and NASA records instead of by team members.
  - Each dimension has an evidence class per question type (decisive, strong modifier, not documented) with its cited finding, in `scoring/literature_evidence.json`.
  - The 51 pairwise judgements follow by a fixed rule (1, 3, 5) → `scoring/literature_judgements.csv` and `scoring/literature_weights.json`; CR 0, 0.009, 0.008.
  - Weights:
    - prevention: o2 .251, flow .250, fuel .250, others .083;
    - detection: role .334, fuel .335, flow .151, others .060;
    - suppression, after FLEX pooling: o2 .256, fuel .253, role .235, diluent .094, flow .086, pressure .039, geometry .037.
  - Effect: 38 of 38 scenarios pass; 2 change their top 3 (`stagnant PMMA` rank 1 is now ACME-BRE). The presets keep their top 3 with lower scores (`lunar habitat` 75.2, was 81.5). Confidence labels change in 8 one-word or short queries.
  - Checks: 56 of 56 unit tests, parity 99 of 99, weights one at a time 146 of 152, SMAA rank 1 in every draw for 8 of 12.
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
- `99f8a25` **Config 1.3.0: pooling applied** (the human lead's decision, 20:06). `scoring/weight_streams.json` sets `apply` true.
  - The suppression weights pool AHP and FLEX data (log-linear pool over o2, pressure, diluent and fuel): o2 .204, fuel .202, diluent .124, pressure .036; role, flow and geometry are unchanged.
  - Prevention and detection keep the 1.2.0 weights.
  - All 38 scenarios keep their top 3; suppression scores move by at most 2.8 points.
- `6202f9a` **Atmosphere flame temperature** (check only, no score uses it): `scoring/flame_temperature.py` uses 13.1 kJ per g of O2 and NIST-JANAF enthalpies.
  - The JANAF tables are in `scoring/reference/janaf/`; the human lead approved the download.
  - On FLEX extinction, flame temperature alone gives R² .553, against .534 for O2 alone and .619 for O2 plus the diluent fractions. So O2 and diluent stay separate, and heat capacity alone is incomplete for helium.
- **`scoring/BUILDUP.md` (new):** the five build-ups with their concepts and techniques, and about 40 references to papers, textbooks and NASA reports. Each reference has a DOI or an open NTRS/NIST link; a separate AI agent checked their bibliographic details.
- Checks: 55 of 55 unit tests, 38 of 38 scenarios, parity 99 of 99, source check clean, `derive_weights.py --check` matches.

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
- Redo the flame-temperature check with NASA/TP-2002-211556 (downloading it needs the human lead's OK).
- Needs a human: team members with combustion training fill in `scoring/expert_form.csv`. Using their judgements in the weights is the human lead's decision.
- Next build-ups (in `BUILDUP.md`): a data-based diluent similarity (helium); a partial-gravity flow scale; material flammability properties.
- Weights change only through the stream files and `scoring/derive_weights.py --write`, with the human lead's decision. After any change, rerun the tests, validation, sensitivity, parity and the verification sheet, and tell pm the numbers.

Published for others:
- `scoring/scoring_config.json` 1.5.3. Weights are unchanged from 1.4.0: AHP over literature-based judgements; suppression pooled with FLEX. New since 1.4.0:
  - `similarity.role.signatures` (keywords, outputs, stated purpose, `not_from_a_fire`);
  - `keywords.signature`;
  - a generic `solid` material entry;
  - `atmosphere_fallback.pressure_published`;
  - `selection.tie_rule`;
  - `confidence.why`;
  - the role requirement fields `concern, signature`;
  - since 1.5.2: `warnings.no_material`, `gate.decisive_is_not_a_veto`, `profiles.detection.scope`, `_about.formula_scope`.
- `scoring.scorer.rank` and `web/scorer.js`: the same code path (parity 104 of 104). Output fields:
  - `requirements`;
  - `compliance` per result, now `{id, status, basis}`, with the statuses met, documented, near, not_met, unverified and not_scored;
  - `value_basis` per result;
  - `scenario.signature` for detection questions;
  - `tie_note` with the new wording;
  - since 1.5.2, a top-level warning `no_material` when no fuel is named.
- `data/catalog/investigations.csv`: `data_availability` of PSI-20 to 23 and PSI-106 is `summary_table` (10:05). `data/catalog/reading_order.csv` and `.json` (pm 0035 step 6).
- `validation/raw_chain_recount.py`, `_report.md`, `.json` and `_netlog.jsonl` (pm 0035 step 7).

Notes for other roles:
- pm, two points on step 6.
  - (1) Class 2: design.md 3.3 says "for a test inside", but the fixture of sections 6 and 7 (S1 at the ISS, the BASS-II Summary Report, 44 tests) are BASS-II tests with oxygen inside and no pressure in a table. The script uses that wider reading: not counted, no outcome value, recorded oxygen or pressure inside and none outside. It is written in `reading_order.json` `interpretation`; tell me if you meant the narrow one.
  - (2) The first class-1 row in most scenarios is the BASS As-Run workbook (121 tests that cannot be placed). Your decision 4 says no test is placed from it. If the page should not show it as "read first", say so and I will drop groups that decision 4 rules out.
- pm, for the 01:00 plan: the catalog already reaches part of the way from a question to the quantities it needs.
  - `rank()` returns `requirements`: one per condition the question sets, with its source and the catalog columns that verify it.
  - Per result it returns `compliance`: met, near, not_met, unverified or not_scored.
  - Each configuration says where its numbers come from (`o2_source`, `pressure_source`, `flow_source`: table, record, test_matrix or team).
  - An `unverified` requirement is the natural pointer to "tested, but the value is not in the tables". If your plan needs a field per requirement, such as where to look in the raw files, tell me its name and I will add it to `requirements` in Python and JS together, with parity.
- pm, for the submission text:
  - Since 1.4.0 the 51 pairwise judgements follow by a fixed rule (1, 3, 5) from evidence classes compiled by an AI session from cited sources (CR 0, 0.009, 0.008).
  - CR near 0 follows from that rule. Do not present it as a measure of judgement quality (`scoring/WEIGHTING.md` 6).
- pm: earlier numbers that changed: unit tests 39 → 45; weight sensitivity "45 of 48, rank 1 never changes" → "146 of 152 over all three profiles, rank 1 changes once"; other values 129/136 → 127/136. In that last check `ISS` now changes at rank 3 in 2 runs.
- Earlier history of this status is in git (`git log -p coord/status/catalog.md`).
