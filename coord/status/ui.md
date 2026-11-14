---
role: ui
updated: 2026-11-14 11:24 KST
state: working
blocked_on: none
---
Now: the "show the tests" step for the ISS and lunar-habitat presets (data request 1116), built against `scenario_tests.csv` and `scenario_needs.csv`; it goes live once those files are on `main`.

Done since last sync:
- U2 done: assumptions listed with the preset and its stated source, catalog and investigation links to the exact CSV row, DOI column in the full ranking.
- U3 done: needs view from `capability_matrix.csv` (top 3 or all 24, status per need, usable tests, missing conditions, link to the exact row; need definitions and basis documents) and coverage view from `coverage_grid.csv` (oxygen x pressure per fuel phase, ambient basis only, the input's cell marked, every count linked to its row).
- U4 done: labels (team computation, not safety guidance, AI-generated with review status) and narrow screens (checked at 375 px, no page-level sideways scroll).
- The page reads `data/insights/cards.json` and `scenarios.json` in the agreed shape. Tested with a throwaway fixture that was never committed.
- `web/README.md` (how it works, AI-generated note).
- Accepted data request 1116.

Next: scenario tests and scenario needs (by 14:30 after they reach `main`), then U5 screenshots and GIF once pm's insight files are in (target 21:00, earlier if possible).

Published for others:
- Public URL: https://choidol0208.github.io/NASA_RAPID/ . Demo links: `?q=ISS` and `?q=lunar%20habitat`.
- For the slides and the project text, what the page shows for solid fuels, from `coverage_grid.csv`: at 19 to 23% oxygen, 62 recorded tests, all with no pressure recorded; at 30 to 36% oxygen, 0 recorded tests at any pressure.
- `data/catalog/*.csv` and the `scoring.scorer.rank` output — stable shape.

Notes for other roles:
- pm: scenario text appears only when the query equals the entry's `query` exactly (case and spaces ignored) and the preset matches, so write `"ISS"` and `"lunar habitat"` as agreed. `result_notes[].investigation_id` may be the PSI accession or the catalog id.
- pm: links to repository files use the commit the site was built from, so they keep working after later changes.
- pm: nobody has opened the live URL logged out yet; this session's proxy blocks github.io.
- Any change to `scoring/scorer.py` or `scoring_config.json` must keep `python3 web/parity_check.py` green, or the deploy stops.
