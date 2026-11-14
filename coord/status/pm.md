---
role: pm
updated: 2026-11-14 16:25 KST
state: working
blocked_on: none
---
*AI-generated (Claude Code), pm role.*

Now: (1) packaging the one part of the video side track that passed its checks; (2) the draft of the submission text and the seven-slide outline (`docs/submission/`, lands when its checks are done).

Done since last sync:
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
- Rebuild and push after data's D5 verdicts.
- Submission text and slides for the human lead to rewrite; final numbers checked again at the 19:00 freeze.

Published for others:
- `data/insights/*.json` as above; shapes in `contracts/README.md` ("From the pm role") and `contracts/examples/`.
- `ai/review/review_sheet.csv` and `ai/review/README.md` for the review.
- `docs/ai_layer_design.json` (design of the AI layer).

Notes for other roles:
- ui: field names match your list; see request 1622 for the four fixes. Pages deploys from `main` and `catalog-filter`; `main` holds all role branches as of 16:15.
- data: D5 can start. The three CSVs freeze at 17:30 as agreed.
- catalog: nothing open from pm. `ai/robustness.py` now samples 8,000 weight vectors per query; its result agrees with your sensitivity run in kind (rank 1 is stable or level, never replaced).
