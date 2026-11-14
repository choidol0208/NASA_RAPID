---
role: ui
updated: 2026-11-14 11:16 KST
state: working
blocked_on: none
---
Now: U2, the query box and results. Most of it is already in the skeleton; next is the evidence links in the full table, the assumptions list and checking every warning code on screen.

Done since last sync:
- U1 done. Dashboard skeleton live at **https://choidol0208.github.io/NASA_RAPID/**, deployed by `.github/workflows/pages.yml` from `catalog-filter` (run 43545276180 green).
- Stack: static site in `web/` (HTML, CSS, JavaScript; no framework, no server, no paid call, GitHub Pages does not sleep). Ranking runs in the browser as `web/scorer.js`, a port of `scoring/scorer.py`; `web/parity_check.py` compares both on 61 queries and blocks the deploy on any difference.
- The page already has: free-text box and six example buttons (ISS, lunar habitat, lunar habitat with cotton fabric, smoke detection on the ISS, spacesuit, Mars base), "how your input was read" with the source of each condition, scenario warnings, top 3 with a match strip per dimension, warnings including `fallback`, PSI page, DOI and source-table links, the full 24-row ranking, the team-computation and not-safety-guidance notes, and `?q=` links.
- Answered and closed my side of 20261114-1056 (done).
- Merged `origin/main` (Pages decision, coverage wording, insight shapes).

Next: U2 polish (target 14:30), then U3 needs view and Coverage view from `capability_matrix.csv`, `needs.json` and `coverage_grid.csv` (target 17:00).

Published for others:
- Public URL: https://choidol0208.github.io/NASA_RAPID/ . A link to a query: `?q=lunar%20habitat`.
- `data/catalog/investigations.csv` (24 rows), `configurations.csv` (41 rows), `data_dictionary.csv` — stable shape.
- `scoring.scorer.rank` output — stable shape (fields listed in `contracts/README.md`).

Notes for other roles:
- pm: this session's proxy blocks github.io, so nobody has opened the live URL logged out yet. Please open it once in a private window.
- pm: `data/insights/cards.json` and `scenarios.json` are read when present on `catalog-filter` (merged from `main`); until then the page says "Written summary: not available yet."
- Any change to `scoring/scorer.py` or `scoring_config.json` must keep `python3 web/parity_check.py` green, or the deploy stops.
