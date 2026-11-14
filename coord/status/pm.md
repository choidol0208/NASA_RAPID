---
role: pm
updated: 2026-11-14 14:10 KST
state: working
blocked_on: none
---
Now: (1) research and design of the AI layer, (2) a stronger differentiator for the project, after feedback from the Seoul organizers (see notes). Both report back within the hour; then P3.

Done since last sync:
- Merged `data-pipeline` and `catalog-filter` into `main` at 11:31; pipeline run and scorer tests pass.
- Opened the live site logged out from a normal browser: https://choidol0208.github.io/NASA_RAPID/?q=lunar%20habitat returns the page and the ranking renders (HTTP 200, checked 11:33). ui could not check this from its side.
- Answered data's request 1116 (accepted); closed the request to ui.
- Local model: Ollama upgraded to 0.40.16; OpenAI gpt-oss:20b (Apache-2.0) is downloading.

Next: `data/insights/cards.json`, then `scenarios.json` for `iss` and `lunar_habitat` from `scenario_needs.csv` (16:30).

Published for others:
- `contracts/README.md`, `contracts/examples/*.example.json` (shape only, placeholders).

Decision at 13:05 (`coord/decisions.md`): the project keeps the team's original topic; no new first screen. The differentiator is the fourth goal, shown as one section "Where the evidence stops". ui has the request (1310). The alternative framings explored this morning are dropped.
- Checked by pm at 12:05 KST through the PSI public search: 133 public investigations; the term "Saffire" matches PSI-98, PSI-99 and PSI-100 only (Saffire IV to VI are not in PSI).
- Local model ready: OpenAI gpt-oss:20b under Ollama 0.40.16; first test gave 12 of 12 supporting quotes found verbatim in the PSI record.

AI layer, state at 12:30: the design is in `docs/ai_layer_design.json` (code-computed facts first; one local model writes only card summaries, each sentence citing a numbered PSI sentence, behind code gates and a review). Building now under `ai/` and `data/insights/`. Three requests are out: one ordered request to ui, two to data.
- Science correction for everyone: microgravity and 1 g results do NOT bound lunar or Martian gravity (NASA drop-tower work, Olson and Ferkul 2012, as read by the design's science review; data is asked to add the item). The live page's partial-gravity warning says the opposite and is item 1 of the request to ui.

State at 14:10: the AI layer is built (model guard, 556 numbered PSI sentences, code-written scenario text, gates and linter, model-written card summaries, catalog audit, evidence-map data) and is being rebuilt on data's audited outputs (1,824 tests, six needs), with a second reading of every model sentence. An independent verification found one model sentence that changed the meaning of its record (PSI-159); it is removed. Nothing under `ai/` or `data/insights/` is on `main` yet; the push is announced here, target 15:00. Until then pm does not merge (the working tree is in use), so `main` may lag your branches by up to an hour.
- data: the review sheet `ai/review/review_sheet.csv` lands with that push. Model rows first; the code-built rows are for a second look if time allows.
- ui: `data/insights/evidence_map.json`, `cards.json` and `scenarios.json` land with that push. Scenario entries will carry `text_origin` and `frame_text_origin` = `template`. Request 1410 is the catalog addendum (item 5 of 1224).

Notes for other roles:
- Feedback from the Seoul organizers to the human lead: the topic is interesting, but the project lacks a differentiator that catches the eye at once; awards are judged across all challenges. pm is working out options and the human lead will choose. Expect a request about the landing view and the demo flow early this afternoon. Until then, please keep the current plan; nothing built so far is wasted.
- ui: U5 screenshots and GIF should wait for that decision, since the first screen may change.
- data: `cards.json` is not written yet; D5 can start when it lands on main.
