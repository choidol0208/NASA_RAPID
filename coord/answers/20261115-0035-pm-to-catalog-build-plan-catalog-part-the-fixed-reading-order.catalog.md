---
request: 20261115-0035-pm-to-catalog-build-plan-catalog-part-the-fixed-reading-order
by: catalog
state: done
answered: 2026-11-15 10:11 KST
---
# Answer

*AI-generated (Claude Code), catalog role.*

Done, both steps. The human lead gave the catalog role both steps at 08:33; the catalog and the scores did not change for this work.

## Step 6: `data/catalog/reading_order.csv` (09:09, `e8c5bc5`)

- 53 rows, built by `scoring/reading_order.py` from `retrieval_queue.csv` and `need_gap_states.csv`. It uses the fixed rule of design.md 3.3: class 1, class 2, class 3; within a class, more target tests first, then fewer bytes. Each test is counted once.
- The header sentence is yours; `reading_order.json` has the meta data and the input hashes.
- The fixture "S1 at the ISS: class 2 is only the BASS-II Summary Report, 44 tests" reproduces.
  - It reproduces only under one reading of class 2: at least one recorded atmosphere value inside the ranges and none outside. The meta file states that reading.
  - The narrow reading gives no row, and the wide reading includes BASS tests that have neither value.
- `question_chain.csv` has not been added yet. data pushed it at 10:20; I add it at the next sync.
- ui shows the order as "Where to read first".

## Step 7: `validation/raw_chain_recount.py` and its report (`52d927d`)

**62 of 71 fixtures reproduce.** The 9 that do not are all in the video block. The script computes every match; no rule was tuned to reach a number.

- It is written from the design documents and imports nothing from `pipeline/`, `video/`, `ai/`, `scripts/` or `scoring/`.
- An offline rerun by the catalog session at 10:08 gave identical figures.
- Report: `validation/raw_chain_recount_report.md`. Figures: `validation/raw_chain_recount.json` (about 0.8 MB, with every sheet's values). Network log: `validation/raw_chain_recount_netlog.jsonl`.

Reproduced:
- **Placement:**
  - lunar: 26 / 676 / 63 / 1,059;
  - solid: 0 / 237 / 139;
  - ISS: 179 / 739 / 106 / 800;
  - Mars: no range set for 1,824.
  - All 10,944 rows of `scenario_tests.csv` agree.
- **Chain sums:** all 186 keys of `need_gap_states.csv` sum correctly and equal the recomputed states. P1 pressure: 134 / 129 / 113.
- **Links:**
  - lunar: 398 files, 104,358,456,350 bytes; second label 336 / 47 / 15;
  - FLEX: 299 files, 24,954,842,492 bytes;
  - CFI-G: 99 files, 79,403,613,858 bytes.
- **FLEX sheets:** 272 sheets, 250,375 bytes. For the 17 lunar tests: identifier 17 of 17, pressure 16, oxygen 16, and the section 7 cross-table exactly.
- **Video:**
  - P1 99 / 18 / 2 / 14, D1 98 / 16 / 2 / 6, P3 0 / 0 / 0 / 2;
  - ISS P1 55 = 42 / 4 / 0 / 9; lunar 8 tests;
  - 11 of 14 investigations exactly.

Not reproduced (expected → recounted):
- Link states 662 / 374 / 10 / 1,217 / 330 / 30 → 662 / 374 / **15 / 1,201 / 341** / 30.
- PSI-26 day-only / not in table 113 / 1 → 101 / 13.
- PSI-39 disagree / day-only / not in table 2 / 20 / 118 → 7 / 16 / 117.
- Tests whose only video disagrees 6 → 8; S1 disagree-only 1 → 2 (also in the ISS and lunar S1 "outside" rows).

The four causes, kept as the recount's rules rather than tuned:
1. **PSI-26:** NASA's BASS table writes Date 6/1/2013 for rows whose GMT day is 150 (30 May). The recount matches on Date; the video design matched on GMT.
2. **PSI-39:** for 5 videos, the CIR code of the name is not in the table but the folder's is. The recount says `labels_disagree`; the design falls back to the name's day.
3. **FLEX-11:** a disagreeing video counts for every test any of its labels names, so `256R002.mpg` also counts for FLEX-11; the design counts it for FLEX-13 only.
4. **SAME-R:** the recount has no "run" scope, so 3 run files fall under "day".

How to attribute a disagreeing video is a team decision (pm or data). Other points:
- **Placement order:** "outside" comes before "oxidizer stream". The other order would read lunar 263 / 859 instead of 63 / 1,059.
- **Untied sheets:** FLEX-070 and FLEX-073 stay untied (same date and time).
- **No drift:** 60,866 files and 13,471,850,126,356 bytes are identical between the team's listing (11/14 05:57Z) and this job's (11/15 00:12Z).

**Network:** 568 calls, all within the scope the human lead approved: 24 listings, 272 signed links and 272 sheets, 31,335,089 bytes, 0 errors. Signed links are logged without their query string. The files stay git-ignored (`data/psi/file_listings/`, `data/psi/raw_cache/`).
