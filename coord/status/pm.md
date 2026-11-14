---
role: pm
updated: 2026-11-14 12:10 KST
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

Differentiator, state at 12:10: three options are with the human lead, who chooses with the team (target 13:00). The option that survived review is a new first screen: every test that records the oxygen of its atmosphere as a dot on one oxygen axis, in three lanes (gas flames, fuel droplets, solid fuels), with the solid lane ending at 22.2% and a line at the challenge's 30%. Nothing is decided; do not build it yet. If it is chosen, requests follow: ui for the view, data for a count check and a dated PSI search.
- Checked by pm at 12:05 KST through the PSI public search: 133 public investigations; the term "Saffire" matches PSI-98, PSI-99 and PSI-100 only (Saffire IV to VI are not in PSI).
- Local model ready: OpenAI gpt-oss:20b under Ollama 0.40.16; first test gave 12 of 12 supporting quotes found verbatim in the PSI record.

Notes for other roles:
- Feedback from the Seoul organizers to the human lead: the topic is interesting, but the project lacks a differentiator that catches the eye at once; awards are judged across all challenges. pm is working out options and the human lead will choose. Expect a request about the landing view and the demo flow early this afternoon. Until then, please keep the current plan; nothing built so far is wasted.
- ui: U5 screenshots and GIF should wait for that decision, since the first screen may change.
- data: `cards.json` is not written yet; D5 can start when it lands on main.
