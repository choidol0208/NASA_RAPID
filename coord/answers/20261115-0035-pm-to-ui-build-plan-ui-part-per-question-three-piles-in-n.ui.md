---
request: 20261115-0035-pm-to-ui-build-plan-ui-part-per-question-three-piles-in-n
by: ui
state: accepted
answered: 2026-11-15 09:09 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

## Progress (09:09): reading order and the table's own codes

- **Reading order (step 6):** catalog's `data/catalog/reading_order.csv` (`e8c5bc5`) is in pile 2 under "Where to read first", for both demo environments. It has the two fixed sentences of section 9 above it and one `order.row` per line, with the evidence words from the closed list ("header seen in n of N files" from `state` and `evidence`, or "not opened"). A state outside the list stops the build.
  - ISS S1, row 3: "BASS-II Summary Report.pdf (BASS-II, PSI-25): 1 file, 48.97 MB; target tests 44; not opened." This matches the fixture of design.md section 6.
  - So the ISS now has pile 2 content too.
- **`pile1.codes` (08:23):** the extinction diameter as NASA's table file writes it. Lunar habitat 4 / 2 / 8 / 3, checked as fixture F5; ISS 40 / 1 / 10 / 5.
- **Still waiting for data's 0035 files** (none on a branch at 09:09): the header links for the ISS, the per-test file list with "Download file list (CSV)", the raw values read from the 17 test sheets, and the video rows.

## Progress (08:18): the smallest version is live for both demo environments

It goes live with the push that carries this answer; my status names the build. It is a new section, "Where the data are: in NASA's tables, in the archive, or no record" (kicker "Interpret · Which raw data each question needs"), after "What is known for this environment".

**How it is built.**
- `web/raw_piles.py`, run by `web/build.py`, fills the templates of `pile_wording.md` from the files and writes `data/piles/<scenario>.json`.
- The page prints those sentences and adds only the labels. No model is involved anywhere.
- Placements come from `scenario_tests.csv`, with the rule:
  - oxygen and pressure in → inside;
  - either recorded out → outside;
  - `not_ambient` oxygen → oxidizer stream;
  - else → cannot be placed.
  This reproduces fixture F1 exactly: lunar 26 / 676 / 63 / 1,059 and solid fuels 0 / 237 / 139; ISS 179 / 739 / 106 / 800. The build stops if it does not.
- Locations (pile 2) come from the chain: data's `question_chain.csv` when it lands, the prototype until then, so lunar only. Where both exist, the chain's inside and counted numbers are cross-checked with mine.

**Build checks (B8), all passing.** The build stops on any of these failing:
- F1;
- bar segments summing to the tests in scope;
- the line for counted tests carrying fuel form, gravity and kPa (the "17" rule);
- a whole-word scan for safe, unsafe, will, predict, likely and `answers.json` `forbidden_words`;
- no unfilled slot (`{`, `}`, "None");
- a test inside but not counted for a third reason (as 4.4 asks).

**What the page shows now.**
- **Header:**
  - both environments: 1.1 and 1.2;
  - lunar habitat only, from the prototype links: 1.3, 1.4 and 1.6 with the scenario caveat — "398 of them (104.4 GB, 0.77% of the bytes) … 316 files … and 82 archives and video recordings", and the 336 / 47 / 15 line, the FLEX-20 / FLEX-21 case named;
  - 1.5 for both, for example "The 26 tests are 17 fuel-droplet tests (FLEX, 71.2 to 72.4 kPa) and 9 gas flames (ACME-CFI-G, 50.7 kPa), all in microgravity."
- **A bar per question:** 2.1, the text line plus a stacked bar with a legend. The first question of the user's kind and any question with tests inside are open.
- **Pile 1:**
  - 4.1 and 4.2;
  - 4.3 as the outcome counts: "how the burn ended 17 of 17 (15 disruption, 2 completion); extinction diameter 6 of 17; flow event 0 of 17";
  - 4.4, with the 7 + 2 split for CFI-G on the lunar habitat. For the ISS the 71 ACME-FLAME-DESIGN, 25 CFI and 8 of the 27 CFI-G tests "hold no outcome", and 19 CFI-G are `not_stated`.
- **Pile 2 (lunar):**
  - the extinction-diameter line for the 11 FLEX tests ("A header Dext (mm) or Dext = was seen in 5 opened files of the file groups these belong to (650 files, 102.5 MB). Not read.");
  - lower-shelf lines (8.2) with the not-mapped clause, for example the four FLOW_NOZZLE headers with "unit written as N/A";
  - the "cannot be placed" line for each question, on both environments.
- **Pile 3:**
  - ground 1 (lunar gravity, with the Flight Platform values parsed from the table in `psi_metadata_summary.md`);
  - ground 2 for lunar P1, P3 and D1, with the source columns from `values_long.csv`.
  - Neither ground holds for the ISS, so pile 3 is not printed there, as section 6 says.
- **Small print:** all five sentences, with "Recount by a second AI session: not yet. Read by a person: none yet."

**Deviations, please check:**
- The extinction-diameter line in pile 2 joins the first clause of 8.2 with the evidence sentence of 8.1. 8.1's own slots ("files" and "n of N opened" for the tests' own files) need data's step-3 links.
- Sizes use one rule for the whole block: two decimals below 100, one from 100 up. That gives 86.85 MB where your example rounds to 86.9 MB.
- Lunar pressure reads "below 85.8 kPa", from `range_words` with `max_inclusive` false in `scenarios.json`; your example writes "up to".

**Not yet:**
- `pile1.codes` (blank and dash counts from the table file);
- ground 3 (the BASS-II pressure sentence);
- ISS pile 2 (it needs data's chain for the ISS);
- the per-test file list with "Download file list (CSV)";
- the reading order (catalog step 6);
- the video rows.

Each follows when its file lands. Data's 0035 outputs (`question_chain.csv`, `file_links_summary.json`, `test_files.json`) are not on any branch at 08:18. When they land I switch the header links and pile 2 to them in one sync.

## Accepted (08:10)

Accepted, late. The ui session was off from about 00:25 to 08:05; 2340 was done at 00:13.
