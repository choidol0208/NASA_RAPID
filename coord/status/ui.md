---
role: ui
updated: 2026-11-14 11:13 KST
state: working
blocked_on: none
---
Now: U1, static dashboard skeleton in `web/` with a GitHub Pages workflow.

Done since last sync:
- Merged `origin/main` into `catalog-filter` (fast-forward, no conflicts).
- Answered pm's request 20261114-1056: stack, settings to switch on, shape of the model-written text.

Next: push the skeleton and workflow (target 12:15), then U2 (query box wired to the ranking).

Published for others:
- `data/catalog/investigations.csv` (24 rows), `configurations.csv` (41 rows), `data_dictionary.csv` — stable shape.
- `scoring.scorer.rank` output — stable shape (fields listed in `contracts/README.md`).
- Public URL: not yet. Expected https://choidol0208.github.io/NASA_RAPID/ once pm turns on Pages (see the answer to 20261114-1056).

Notes for other roles:
- The dashboard is a static site (no server, no paid calls, does not sleep). The ranking runs in the browser as a JavaScript port of `scoring/scorer.py`, checked against the Python scorer on every deploy; any change to the scorer must keep that check green.
