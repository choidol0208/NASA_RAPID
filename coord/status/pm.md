---
role: pm
updated: 2026-11-14 23:49 KST
state: working
blocked_on: none
---
*AI-generated (Claude Code), pm role.*

Now: the human lead is back and set the direction for the remaining day (23:49; `coord/decisions.md`): let a user find which unprocessed raw data they need, video included, without processing all of it. pm is running two design jobs (the general question-to-files design; a video ladder) and sends one plan with work per role at about 01:00. No freeze today; submission on 15 November.

Done since last sync:
- **23:35: integration.** `catalog-scoring` (config 1.4.0, the weighting build-up, the JANAF tables removed), `data-pipeline` (raw-file layer) and `catalog-filter` are in `main`; AI layer rebuilt; all checks pass. The pm session was offline from about 20:20 to 22:50. Still to do when the human lead is back: `docs/submission/` to config 1.4.0 (scores, weights, method text), and requests to ui for three errors an analysis found on the page (the environment text cut at decimal points; the "not in the archive" list shown for four inputs only; the "4 of 6" line that reads wider than it is).
- **20:16: the two compliance logs are in English on `main`.** `compliance/SOURCES.md` and `compliance/AI_USAGE_LOG.md`: same rows, same cells, every link and number in place; the Korean rows added since 16:55 were translated and compared with the Korean by a second agent. **You may append again: merge `main` first, and write new rows in English.** If a row of yours reads wrong in translation, append a correcting row.
- `docs/submission/` is up to date with the page as built at 19:05: no `[PLANNED` mark left, seven `[FILL` items that only a person can supply, two complete versions of slide 6. `README.md` is rewritten for a first-time visitor (live link first, what is implemented, how to run it, limits).
- For ui, from the README check: `web/README.md` still says seven needs and 61 parity queries (now six and 99); the page's masthead quotes the challenge sentence in quotation marks with a subject the official page may word differently, please compare word for word.
- **19:01: freeze integration on `main` (`abff173`).** All three role branches merged; `ai/build_all.py` (9 steps, no model call), 241 unit tests, scorer tests, parity 99 of 99, the integration check and `pipeline/check.py` pass. It was announced as the freeze; the human lead lifted the freeze shortly after, so feature work continues.
- 18:27: request 1809 applied in pm's code-built texts (labels say who checked a text; the clause on expert review is gone). 18:11: data's second review round applied (226 template sentences `wording_ok`; 10 quotes not shown; one new quote row without a verdict: `card:PSI-69:key_point:PSI-69.objective:OBJ-4`).
- 18:14: answered data 1755: the two lab results may be used in the submission text and the limits slide if `data-lab` is public, with "recomputed by a second AI agent, not reviewed by a person".
- **17:10: `video/` is on `main` (`6779f26`)**: a one-command reader of NASA's on-screen values in the BASS-II videos, a settings file, tests, 19 CSV files and the procedure. An independent agent reproduced the files byte for byte and read 40 random frames blind (190 readings agree, 0 disagree). All frame checks were made by AI agents, not by a person, and the files say so. No flame-out time, burn duration or flow speed is derived. It is a side pilot: nothing from it enters a ranking, a count or a scenario text.
- **17:08: `AGENTS.md` is in English** (`b552946`): a faithful translation, compared line by line with the Korean by a second agent. Same sections, numbers and rules. The two compliance logs are translated and replace the Korean files right after the 19:00 freeze integration; write new rows in English, and after 19:05 merge `main` before you append.
- 17:05: request 1705 to ui: one block that shows the three AI analyses the page does not read yet (`quality.json`, `model_readiness.json`, `robustness.json`).
- **17:05: data's review (D5) is applied and on `main` (`c1d0c1c`).** Of the 61 model-written sentences, 33 were marked supported and stay; 28 were marked partly and are removed, each slot showing the NASA sentence it cited (rule: a sentence is shown or not shown, never reworded). 20 cards carry the label "checked by a second AI session"; 4 cards show NASA quotes only. No person has reviewed a sentence, and no label says so. In progress: the 8 quotes marked `not_relevant` will no longer be shown, and the 4 template sentences marked `wording_issue` are reworded; rows whose text changes come back to data without a verdict.
- 16:50: the human lead decided that Korean files are translated into English before submission (request 1656 to all roles).
- **16:21: pm's files are on `main` (`3691a69`).** `data/insights/cards.json` (24 cards, 61 model-written sentences, labelled as not reviewed; 4 more were removed by a second reading and show the NASA sentence instead), `scenarios.json` (frames, need statements, gaps and result notes built by code; `text_origin` = `template`), `evidence_map.json`, `model_readiness.json`, `robustness.json`, `ai/review/review_sheet.csv`.
- How they were checked: the run that was interrupted at 14:55 was repeated from its start. A repair step found and finished eight half-done edits; a second reader read all 65 gated model sentences against the PSI records and all code-built text for `iss` and `lunar_habitat`; an independent check recomputed every count, quote and number with its own code and found nothing blocking. After merging the three role branches at 16:15 the build was repeated: 9 steps, no model call, 223 unit tests, `ai/check_all.py`, `pipeline/check.py`, scorer tests and parity all pass. pm opened a local build of both demo queries: no console error.
- Merged `data-pipeline`, `catalog-filter` and `catalog-scoring` into `main` at 15:10 and again at 16:15.
- 15:14: the human lead confirmed pm's answer to data 1503 (go with changes).
- Requests: 1505 to ui (third part of Constraints; ui has built it), 1622 to ui (four small page fixes), 1622 to data (three text points; D5 can start). Answered data 1442 `done`. Closed 1431 and 1449 (data).

Numbers for slides and text (all recomputed by the independent check):
- 1,824 recorded tests, all in microgravity, from 14 PSI tables of 12 investigations; 0 at lunar or Martian gravity.
- 878 with a recorded ambient oxygen: gas 386 (18.0 to 40%), fuel droplets 353 (12 to 34%), solid 139 (13.6 to 22.2%). At 30% oxygen or more: gas 246, droplets 24, solid 0.
- Solid-fuel tests with a pressure value in the PSI experimental tables: 0 of 376.
- Lunar habitat: 17 counted tests in the team bins, all FLEX fuel droplets, 30 to 34% oxygen, 71.2 to 72.4 kPa (1 to 2 kPa above 10.2 psi); 15 ended in disruption, 2 in completion, none in extinction. Counted tests at 30% oxygen or more and at or below 10.2 psi: 0.
- Do not call the ISS top three an order: BASS-II, BASS and SAFFIRE-III are level under the team weights in every weight draw.

Video side track (not on the critical path), result of three independent passes:
- Passed: reading NASA's on-screen values (FUEL, AIR, FAN, RAD, clock) from the BASS-II videos. About 750 values compared by eye in 186 frames, none wrong. It ships only as "NASA's on-screen readings, transcribed by the team", 19 clips, with its limits stated, under `video/`.
- Failed and dropped: an automatic flame-out time from picture brightness (right in at most 1 of 19 clips). No flame-out time, burn duration or flow speed at blowoff or extinction is claimed.

Next:
- Submission text and slides for the human lead to rewrite; final numbers checked again at the 19:00 freeze.

Published for others:
- `data/insights/*.json` as above; shapes in `contracts/README.md` ("From the pm role") and `contracts/examples/`.
- `ai/review/review_sheet.csv` and `ai/review/README.md` for the review.
- `docs/ai_layer_design.json` (design of the AI layer).

Notes for other roles:
- ui: field names match your list; see request 1622 for the four fixes. Pages deploys from `main` and `catalog-filter`; `main` holds all role branches as of 16:15.
- data: D5 can start. The three CSVs freeze at 17:30 as agreed.
- catalog: nothing open from pm. `ai/robustness.py` now samples 8,000 weight vectors per query and reports how often each shown result stays in the top three; for `lunar habitat`, with weights drawn near the team's, the three shown results stay there in 97%, 97% and 86% of the draws (`data/insights/robustness.json`). It measures top-three membership, not rank 1, so it does not replace your sensitivity run.
