---
role: ui
updated: 2026-11-14 14:58 KST
state: working
blocked_on: none
---
Now: the catalog, the scorer and validation moved to the new `catalog` role (branch `catalog-scoring`, human lead's decision at 13:28). ui answered the handover request 20261114-1332 `done`:
- items (1) and (2) are done;
- items (3) to (6) were already done and pushed before the split, and are now catalog's to review;
- (7) and (8) were not started.

ui no longer edits `data/catalog/`, `scoring/`, `validation/`, `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`, `web/scorer.js` or `web/parity_check.*`. ui merges `origin/catalog-scoring` at every sync.

1306 item 1 (the "Where the evidence stops" picture) is built and pushed.
- It was tested against a stand-in file in the shape documented in `docs/ai_layer_design.json`; the stand-in was never committed.
- It switches on by itself when pm's `data/insights/evidence_map.json` reaches this branch; `web/build.py` now copies it. Until then the page says "Evidence map: not available yet."
- pm, the page reads these fields:
  - `labels.title`, `labels.lane_notes.{gas,liquid,solid}`, `labels.caption[]`, `labels.saffire_note`;
  - `axes.o2_pct.max`;
  - `points[]`: `fuel_phase`, `investigation_id`, `o2_pct`, `pressure_kpa`, `balance_gas`, `n_tests`, `test_ids[]`;
  - `targets[]`: `id`, `kind`, `label`, `o2_pct` or `o2_min`, `source`, `access`;
  - `not_plotted.oxidizer_stream.{n,why}`, `not_plotted.no_ambient_oxygen_value.{n,rule}`, `not_plotted.psi20_test_day_table.{days,flames_ignited}`;
  - `flight_tests_not_in_psi[]` (`o2_pct`, `label`).
  - Tell me if a name differs. Since 12:45 the ui role runs in a session on the human lead's computer, which can open github.io, so I check the public page after every push.

- 14:24: a loading line shows from the first paint until the first result (it was blank for 1 to 2 s); pm request 1406 forwarded to catalog (1409), done by catalog and closed.
- 14:27: every page asset and data file is fetched as file?v=<build commit>. A new deploy (pm 15:00 push included) is read at once instead of after the 10-minute Pages cache, and a page never mixes two builds.
- 14:33: integration check asked by the human lead.
  - New web/check_integration.py: for 11 queries, all 33 top-3 results reach their data with 0 broken joins. Checked: manifest and DOI, table file, catalog row line, capability_matrix rows, per-configuration test count and ranges in tests.csv.
  - A Playwright reading of the live page matched the data in 70 of 70 result cards and needs rows.
  - All 1,824 test links point at an existing NASA table row; the 1,050 whose table has a test-number column match it.
  - It replaces the catalog-vs-pipeline step in pages.yml (catalog request 1429, done).

- 14:58, pm 1449 items 1 and 2 and pm 1453 built, with the page reading in the challenge's three steps:
  - The masthead quotes the challenge ("hard to find, harder to compare, and harder yet to interpret").
  - Find · Information you need: closest investigations plus "Take the data with you". This holds the matched-tests CSV per demo scenario (written by `web/build.py` from data's files, values copied with source file, row and flags), a link to data's evidence package and to all tests and values at the built commit, and "How to cite" with the DOI of every investigation in the top results and the download.
  - Compare · Points to consider: one line per need, with what the recorded tests say for this environment and the need's `reading`, then the comparison strip and the needs table.
  - Interpret · Constraints, part 1: "Criteria in NASA documents" (59 items from `need_references.csv`, per need, with document, section and link). The label says the page judges no test against them; the crew exposure limit carries its own note.
  - Interpret · Constraints, part 2: the limits of the evidence (where the evidence stops).
  - Still open: 1449 item 3 (raw-data line, when data's file lands) and the unmatched-words line (when catalog's 1505 lands).
- 14:56: answered data 1442 (done: nothing breaks on the new counts) and pm 1449 and 1453 (accepted as one structure: Find = information you need, Compare = points to consider, Interpret = constraints, with NASA criteria and limits of the evidence kept apart). Labels by 16:00, export by 16:30, blocks by 17:30.
- 14:36, from a judge-view review (live as f0ef011):
  - The first screen (1280x800) ends with an at-a-glance line: the top 3 with team scores and, for the demo queries, "ISS cabin 3 of 6 · Lunar habitat 1 of 6" needs with counted tests.
  - "All 24 investigations" and the method text are folded by default; the AI-use paragraph stays visible.
  - build.json lists the optional files the build has, and the page fetches only those (no 404s).
- U5 retake list, after pm's 15:00 push. og.png and web/media/* are the 11:28 drafts from before catalog config 1.1.0 (14:24), which changed "ISS cotton fabric" and "lunar habitat cotton fabric". Retake:
  - shots 01 to 06;
  - the GIF, which runs both cotton queries;
  - og.png.
  - Add the comparison strip and the evidence map.

Done since last sync (pushed 13:54, asked by the human lead):
- **ISS against lunar habitat, side by side** at the top of the needs section, for either demo query:
  - counted tests matched per need, with the breakdown by tier;
  - a button that runs the other query;
  - a summary line: "ISS cabin: matched tests for 3 of 6 needs. Lunar base or pressurized rover: 1 of 6."
- **Lighter first load:** `web/build.py` writes slim copies of `tests.csv` and `scenario_tests.csv`, 1.5 MB down to 334 KB. They keep only the columns the page reads and only `iss` and `lunar_habitat`. Values are unchanged, and each test keeps its line in the full file so row links still point at the right row (checked for all 1,824).
- **Link check (`web/check_links.py`, run by hand):**
  - 58 of 58 linked repository files exist.
  - 61 of 67 external links answer a script.
  - The other 6 refuse scripts (hdl.handle.net, ASTM, ISO, the NASA Task Book, the GRC PDF, the challenge page). All 6 opened by hand in a browser.
- **Link preview card:** Open Graph and Twitter tags, a small icon, and `og.png`, the U5 draft screenshot until U5 replaces it.

Earlier:
- **Scorer:** an atmosphere value filled in by the fallback is no longer worded as "tested". It now reads "O2 not recorded, assumed 21%", and reasons from recorded values come first. Scores and order unchanged (65 queries compared).
- **Scorer:** the oxidizer-stream O2 of inverse flames (ACME-FLAME-DESIGN-C02, ACME-CFI-G-C02) is never matched with the user's O2. It is scored as unknown, with the `oxidizer_stream` warning. `o2_above_all` now uses the highest surrounding-atmosphere O2 tested (40%, reached by ACME-FLAME-DESIGN-C01, ACME-BRE-C01 and ACME-CFI-G-C01; the warning names the first, ACME-FLAME-DESIGN-C01), not the 85% burner stream.
- **Scorer:** "gas", "gas jet", "jet flame" and "gaseous fuel" are read as gas fuel; "droplet" is read as liquid. Four validation scenarios added (F01 to F04).
- **Catalog**, checked against the PSI tables and tests.csv, with the rows in each row's `source_notes`:
  - BASS-II-C03 flow is 0 to 38.5 cm/s (row 72), C04 is 1 to 53 cm/s (rows 115, 117, 121). Both rest on the 'Air display' cells with the flow restrictor out.
  - SPICE-C01 flow is 0.66 to 85.28 cm/s (the table's Air Rate column; 8 negative cells left out).
  - Test counts: CFI 79 and SPICE 435 (exact repeated rows dropped), SAME 4 (rows 6 to 9 record no values).
- **New check, run before every deploy:** `validation/check_catalog_pipeline.py` compares the catalog with tests.csv for all 12 investigations with test-level tables (counts, O2, pressure, flow). It passes now and failed on the old catalog.
- Request 20261114-1305 (challenge text) closed. The follow-up gives data a short verbatim fragment for `CH.moonbase` and confirms `CH.pillars`.
- Opened request 20261114-1319 to data: BASS-II flow increases with the restrictor out are not in tests.csv.
- data request 1328 done (option 1, range kept):
  - The scenario `caveat` is shown under the scenario ranges and above the tests list.
  - "In your atmosphere" wording replaced by "in the scenario range".
  - Each count in the tests list states its recorded O2 and pressure (lunar FLEX: 30.0 to 34.0% O2; 71.2 to 72.4 kPa).
- Checks: unit tests 24/24, validation 26/26, parity 65/65, catalog check 12/12, build.

Next:
- 1306 item 1: the picture, live by 16:30 if `evidence_map.json` is on `main` by about 15:00.
- 1224 items 5 to 7.
- U5 on the new section order (target 21:00).
- Switch the Pages trigger to `main` only at the 19:00 freeze.

Published for others:
- Public URL: https://choidol0208.github.io/NASA_RAPID/ . Demo links: `?q=ISS` and `?q=lunar%20habitat`.
- **Demo rankings (pm, for slides and text):**
  - "ISS" is unchanged (BASS-II, BASS, SAFFIRE-II).
  - "lunar habitat" keeps its top 3 (ACME-BRE, FLEX, ACME-CFI-G). At #4, ACME-FLAME-DESIGN is now represented by its normal flames (C01, 70.3) instead of the inverse flames (C02, 71.6).
  - "50% O2" no longer ranks inverse flames at 97. It shows ambient tests (ACME-BRE, ACME-CFI-G normal, ACME-FLAME-DESIGN normal, about 31) and warns that 50% is above every surrounding atmosphere tested (40%).
  - "gas jet flame ISS" now ranks gas-fuel investigations (ACME-BRE, SLICE, SPICE) instead of solids.
- `scoring/scoring_config.json` changed:
  - text of the `o2_above_all` and `oxidizer_stream` warnings;
  - new fuel keywords;
  - preset source strings (13:10).
  - No weight, preset value or warning code changed.
- `scoring.scorer.rank`: same output fields. `why` and `main_gap` text changes for assumed values.
- `data/catalog/configurations.csv`: values in 5 rows changed as above; columns unchanged. `data/catalog/catalog.xlsx` is not regenerated (needs openpyxl, not installed here) and still shows the old 5 values.
- For the slides, after data's 14:42 literature check:
  - Solid fuels per `coverage_grid.csv`: at 19 to 23% oxygen, 61 recorded tests (was 62), all with no pressure recorded.
  - The page's at-a-glance line now reads "ISS cabin 4 of 6 · Lunar habitat 1 of 6" (was 3 of 6), because D1 gained 45 ISS tests. At 30 to 36% oxygen, 0 recorded tests at any pressure.

Notes for other roles:
- **pm, before your 15:00 push to `main`:** Pages deploys from `main` too, and the last push wins. `main` has none of ui's work since 13:06, including the comparison strip, the evidence-map view, the caveats, the slim files and the preview card. Please merge `origin/catalog-filter` (and `origin/catalog-scoring`) into `main` in the same push. If you can't, the public page steps back until ui's next sync re-deploys `catalog-filter` (within about 15 minutes).
- pm: the official challenge title is "Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data". The page is https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/ . `AGENTS.md` line 10 has the old title.
- pm: set `frame_text_origin` (or the entry's `text_origin`) to `template` for code-built frames, or the frame is tagged AI-generated.
- Any change to `data/pipeline/tests.csv` that moves a count or range of a catalogued investigation now stops the deploy until the catalog follows. data: tell ui in a request, and I'll update `scripts/build_catalog.py` the same sync.
- Any change to `scoring/scorer.py` or `scoring_config.json` must keep `python3 web/parity_check.py` green, or the deploy stops.
