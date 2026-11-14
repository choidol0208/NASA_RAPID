---
role: pm
updated: 2026-11-14 11:35 KST
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

Notes for other roles:
- Feedback from the Seoul organizers to the human lead: the topic is interesting, but the project lacks a differentiator that catches the eye at once; awards are judged across all challenges. pm is working out options and the human lead will choose. Expect a request about the landing view and the demo flow early this afternoon. Until then, please keep the current plan; nothing built so far is wasted.
- ui: U5 screenshots and GIF should wait for that decision, since the first screen may change.
- data: `cards.json` is not written yet; D5 can start when it lands on main.
