---
role: ui
updated: 2026-11-14 18:38 KST
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

- 16:29, pm's and data's files are on the page, live with this push:
  - The evidence map draws (0 to 45% oxygen; the solid lane ends at 22.2%; the challenge's 30% and the two presets marked, the rest behind a switch).
  - The model-written cards show with their AI label.
  - The scenario frame shows its first two sentences, the rest folded.
  - Raw-data sentences appear under each result.
  - Constraints run need by need from data's answer files.
- pm 1622 done (all four fixes plus both optional items), so 1306 item 1 is now live. 1449 item 3 (raw-data line) done.
- 16:31, U5 done: final media in `web/media/`, taken from the public page with its real web fonts. pm, for the slides and the project page:
  - `01_iss_first_screen.png` and `02_lunar_first_screen.png` (each with the at-a-glance line);
  - `03_compare_iss_lunar.png` (ISS 4 of 6, lunar habitat 1 of 6);
  - `04_lunar_evidence_map.png` (the solid lane ends at 22.2%, the lunar 30% marked);
  - `05_lunar_constraints.png` (need by need, the first need open);
  - `06_lunar_coverage_solid.png`;
  - `07_lunar_phone.png` (390 px);
  - `demo_iss_to_lunar.gif` (2.3 MB: ISS, then lunar habitat, the comparison, the evidence map);
  - `og.png` (1200x630 link preview; the build now serves it).
  - The six 11:28 drafts (`01_iss_top.png` … `06_lunar_phone.png`) are removed: old layout and results from before catalog 1.1.0. Retake any time with `node web/capture_media.mjs`.
- 16:42: 1306, 1449 and 1453 marked done. pm 1630 accepted: the four slide captures (slide1_top, slide2_iss_result, slide3_iss_needs, slide7_iss_tests; 2216 to 2560 px wide) plus the evidence map are in the capture script, and a trial run on the live page passed. The final run is after the 19:00 freeze and the switch to main (about 19:15); the status will name the build commit.
- 17:15, pm 1705 done: a new section, "How AI is used here, and how it was checked", above "How the score works". It has three parts, read from pm's files:
  - the model's sentences at each check (70 · 5 · 4 · 28 · 33; reviewed by a second AI session 61, by a person 0);
  - the model-readiness rows with their verdicts and the one metric line;
  - the weight-sampling note, plus a "Weight check" line on each result card of the sampled queries (ISS, lunar habitat, spacesuit, Mars base).
  - A run of another config version shows no line.
- 17:15, pm 1656 done for ui:
  - the slide's speaker notes are in English, in the script and in the built .pptx (swapped in place: the build's npm packages are not on this PC);
  - the theme font name is in Latin letters;
  - glosses were added in the 1332 answer;
  - no Korean is left in ui's files.
- Correction: the unmatched-words line has been live since catalog's `bbea891` (14:59). The `not_understood` scenario warning prints under "How your input was read". My earlier "waits for catalog" was wrong; nothing is open on 1453.
- 17:56, pm 1709 done:
  - The video side pilot's sentence, word for word, with a link to `video/README.md` at the built commit, sits under the "Raw data in PSI" line of the BASS-II (PSI-25) card.
  - It shows only when BASS-II is a result and the build has the README; the page reads nothing under `video/`.
  - Merged `main` at `1042ef1` (pm's review findings applied, data's 17:30 freeze); the AI block reads the rebuilt files with no change: 70 · 5 · 4 · 28 · 33.
- 17:59: merged catalog's `3615213` (reviewer written as "the human lead"; all values of config 1.1.0 approved, no specialist review). The method section now says the same: "The weights and the other scoring values are the team's proposal, not NASA guidance. A team member approved all of them as they are, after an AI review of each value; no combustion specialist has reviewed them." Checks: unit tests 38/38, parity 86/86, integration 33 results with 0 broken joins, build.
- 18:04, the human lead's decision: the page no longer says that no combustion specialist reviewed the scoring values. The method line now reads "The weights and the other scoring values are the team's proposal, not NASA guidance. A team member approved all of them as they are, after an AI review of each value." The text in pm's files (the AI block) is unchanged.
- 18:10, the human lead's decision, extended: no sentence saying that no specialist or expert reviewed the work.
  - The page no longer prints `quality.json` `description` under part 1 of the AI block. It was ui's addition, not part of pm 1705.
  - A search of the rendered page for both demo queries, every fold open, finds no "specialist" or "expert".
  - Request 1809 to all: each role rewords its own files (places listed). Keep "not a NASA conclusion", "not safety guidance", the AI labels and the other limits; write any next step as a plan.
- 18:18, sentence queries tested on the live page (the human lead asked). Oxygen, Mars, Moon base, fabric, detection and suppression are read well. Request 1817 to catalog, three reading gaps: a pressure followed by a Korean particle (`70 kPa의`, `70kPa인`) is not read and the preset value is shown instead; `spacecraft cabin` / `우주선 선실` (spacecraft cabin) read no environment; a base on an unnamed planet gets no partial-gravity warning.
- 18:24: merged catalog's answer to 1809 (wording only in `scoring/` and `validation/`, no value changed). Checks: unit tests 38/38, parity 86/86, integration 33 results with 0 broken joins, build. 1817 (sentence-query reading gaps) has no answer yet.
- 18:38: catalog's fix for 1817 merged (`9769982`), checked on a local build, request closed.
  - `기압 70 kPa의` and `70 kPa인` now read 70 kPa from the user.
  - `우주선 선실` (spacecraft cabin) and `spacecraft cabin` read as the ISS cabin.
  - A base on an unnamed planet reads gravity "partial (planet not named)" (ui's label for catalog's `planetary`) and shows the partial-gravity warning.
  - Demo queries unchanged (ISS 94, 94, 92.7; lunar habitat 79.1, 79.1, 76.1). Checks: unit tests 39, parity 99/99, integration 33 results with 0 broken joins, build, no console errors.
- Open: the 19:00 switch of the Pages trigger to `main` only; pm 1630 slide captures after the freeze.
- 16:54: merged catalog's weight review (`1ff56df`, no value changed). The method section now says: "The weights are the team's proposal, not NASA guidance. A team member approved them as they are; no combustion specialist has reviewed them." No name on the page. Checks: unit tests 38/38, integration 33 results with 0 broken joins, build.
- pm: on the board, U5, U6 and U7 are done (U5's media at 16:31, the 1630 slide captures follow at about 19:15); D7's raw-data file is already on the page.
- 16:08, for pm request 1306 (due 16:30): the evidence-map view is built and tested, but `data/insights/evidence_map.json` is not on `main` yet, so the picture is not drawing on the public page.
  - It switches on in the first build that has the file. Any push to `main` or `catalog-filter` builds it, so no ui change is needed.
  - Proposal: if the file is not on `main` by 18:00, pm puts its static SVG at `data/insights/evidence_map.svg`. I would show that image in the same place, with the same fixed labels, and I can wire the fallback in one sync.
  - U5 capture script is ready; the final run happens right after the file lands.
- 15:41, data 1531 done (built and tested on data-pipeline 0508bc6):
  - When `data/pipeline/answers/` reaches `main`, Constraints switches to need by need. Each need is folded, with its `top_line` ("Not judged here. …") as the summary, and its file loads on opening.
  - Inside are four parts: recorded tests (rung 1 with indicators, rung 2 cells minus repeats), criteria in NASA documents (all frame sentences kept), published by NASA and the investigators (not PSI tests, never counted), and where the evidence stops for this need. The global map and grid stay after them.
  - `access` is shown when not full_text_read, and row entries show `row_values`.
  - Until the files are on `main`, the page keeps parts (a) and (b) as now.
  - pm: please merge `data-pipeline` when you can; no ui push is needed for it to switch on, because any build that has the files turns it on.
- 15:11, pm 1505 done: Constraints now has three parts. Part (a), "What NASA's recorded tests showed", comes first.
  - Per need, one line per indicator from data's evidence package, copied by `web/build.py` into `data/indicators/scenario_<id>.json` (54 KB for ISS, instead of the 470 KB package).
  - Each line shows label, group in words, values, unit, n_tests, the investigation and a link to its exact rows in `indicator_tests.csv` (1,193 lines checked, 0 off). Its reading appears word for word.
  - ISS has P1 19, P3 7, S1 11 and D1 9 values; lunar habitat has S1 5. Empty needs print "No recorded test at this condition gives a value for this need."
  - `compare_with` shows only as a pointer. Part (b) is the criteria and part (c) is where the evidence stops.
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
