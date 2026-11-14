---
role: ui
updated: 2026-11-14 13:10 KST
state: working
blocked_on: none
---
Now: the ui role moved at 12:45 to a new session on the human lead's own computer. The earlier web session stopped syncing after 11:28. This session can open github.io, so I check the public page myself after every push. Next: the optional items of pm's request 1224, then U5 after the first-screen decision.

Done since last sync:
- Merged `main` (14 commits behind). The scenario section (row per need for "your atmosphere", recorded tests by tier) goes live with this push.
- pm request 1224, items 0 to 3 done:
  - Pages also deploys from `main`.
  - Partial-gravity warning no longer says "bounds".
  - Three provenance labels: quoted from the PSI record, computed by team code, AI-generated.
  - `summary_sources`, `gaps[].sources` and `frame` are rendered with links.
- data request 1242 done:
  - Evidence rule shown: `objective_link = not_stated` reads "Outside stated objective, not counted".
  - Need count read from `needs.json` (6 once data's files reach `main`); `reading` shown with the counts.
  - Only `iss` and `lunar_habitat` are shown.
  - "Oxygen and pressure not in the NASA table" wording.
  - Unknown gap codes shown as codes.
  - CO2 or helium added count.
- Answered 1158 for the record (already closed by data).
- Live since 13:00 (build eeff116, Pages run green).
- Challenge statement checked on the official page at the human lead's request. The lunar bound holds: oxygen likely 30% or more, 10.2 psi or less, under "Spacesuits and oxygen concentration". The spacesuit preset matches (100%, 4.3 psi). Fixes to the URL, title and section go to data in request 20261114-1305. The `lunar_habitat` and `spacesuit` preset source strings in `scoring_config.json` now name the section; no values changed.
- Checks: unit tests 18/18, validation 22/22, parity 61/61, build. Local test with `main` data (7 needs) and with `origin/data-pipeline` data (6 needs). 375 px with no sideways scroll.

Next:
- 1224 item 4: the first screen, if the human lead chooses it.
- 1224 items 5 to 7: the 16:00 addendum, the source-sentence toggle, the "How we checked the AI text" panel.
- U5 screenshots and GIF after the first-screen decision, retaken with the real fonts from this machine (target 21:00).
- Switch the Pages trigger to `main` only at the 19:00 freeze.

Published for others:
- Public URL: https://choidol0208.github.io/NASA_RAPID/ . Demo links: `?q=ISS` and `?q=lunar%20habitat`.
- Deploy: `.github/workflows/pages.yml` runs on pushes to `catalog-filter` and `main`. It applies on `main` once pm merges this branch. pm, please record the change to decision 8.
- `scoring/scoring_config.json` changed: `warnings.partial_gravity` text only (pm's short form). No code, weight, preset or warning code changed.
- For the slides, solid fuels per `coverage_grid.csv`: at 19 to 23% oxygen, 62 recorded tests, all with no pressure recorded. At 30 to 36% oxygen, 0 recorded tests at any pressure.
- `data/catalog/*.csv` and the `scoring.scorer.rank` output: stable shape.

Notes for other roles:
- pm: the official challenge title is "Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data" ("SI-Powered", not "AI-Powered"). The page is https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/ ; the long URL in `compliance/SOURCES.md` returns "Page Not Found". Use the official title in the submission text and slides. `AGENTS.md` line 10 has the old title.
- pm: set `frame_text_origin` (or the entry's `text_origin`) to `template` for code-built frames, or the frame is tagged AI-generated.
- pm: scenario text appears only when the query equals the entry's `query` (case and spaces ignored) and the preset matches.
- Any change to `scoring/scorer.py` or `scoring_config.json` must keep `python3 web/parity_check.py` green, or the deploy stops.
