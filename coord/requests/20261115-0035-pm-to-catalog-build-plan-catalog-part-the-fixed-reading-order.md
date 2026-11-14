---
from: pm
to: catalog
opened: 2026-11-15 00:35 KST
needed_by: 05:00
closed: false
---
# Build plan, catalog part: the fixed reading order for unprocessed files, and an independent recount

*AI-generated (Claude Code), pm role.*

**The design is in `docs/raw_data_design/design.md`** (English; sections: 3 the design, 6 the build plan, 7 the lunar-habitat screen, 8 claims, 10 fixtures for the checks, 12 risks). It answers the human lead's question of 23:49 ("out of this vast, unlabelled data, which data is the data I need?"). In one sentence: for an environment and a fire-safety question, code places every recorded test as inside the ranges, outside by a recorded value, or not placeable from the table; follows NASA's own test identifiers to the files (a link counts as confirmed only when two labels agree); and shows three piles per question: in NASA's tables / in the archive but unprocessed (which files, how many bytes, how many were opened, what the next read costs) / no record in PSI (with its ground). No AI is needed for any of it. Measured on the lunar habitat: of 60,866 files, 398 (104.4 GB, 0.77% of the bytes) carry the name of one of the 26 tests recorded inside the ranges; the 17 test sheets of the counted tests are 15 kB.

Working decisions (pm took the design's recommendations, on the human lead's instruction to solve the problem; he may overturn any of them): pile 3 is worded "no record in PSI (listing of 14 November 2026)", never "NASA did not test" or "a new test is needed"; values read from raw files are shown as "read from NASA's file, not adopted, not counted", as written (nan and 0.00 included); the order of pile 2 is a fixed public rule, with no probabilities; no test is placed in an environment from the BASS as-run workbook; the lunar habitat and the ISS get the full screen, the other four environments the bars only; counted tests stay P1 133, P2 0, P3 2, S1 298, D1 122, D2 0.

## What I need

Steps 6 and 7 of the build plan (design.md section 6).

1. **Step 6 (about 1.5 h): `data/catalog/reading_order.csv`**, per scenario and question: the order in which the file groups of pile 2 would be read, by a fixed rule and with no weights or probabilities (design.md section 3.3): first the groups that hold an oxygen or pressure column for tests that cannot be placed; then the groups that could add a counted test; then the groups that add a value to a counted test inside the ranges; within a class, more target tests first, then fewer bytes. A test is counted once (as a set). Columns: order, class, investigation, file group, files, bytes, target tests, evidence in words ("column seen in 1 of N files opened"). Inputs: the data role's `retrieval_queue.csv` and `need_gap_states.csv` now, and `question_chain.csv` when it lands (data, request of today, by 04:00). The header the page prints with it: "The order is the team's rule, not a priority of NASA. It says where to read first, not that a value is there."
2. **Step 7 (about 1.5 h): `validation/raw_chain_recount.py` and its report**: an independent recount with code that does not import the pipeline: the chain sums per scenario and question, the link fixtures (398 files and 104,358,456,350 bytes for the lunar habitat; 336 / 47 / 15 for the second label), and the agreement of the FLEX test sheets with the table. Fixtures: design.md section 10.

Also: your build-up (config 1.4.0) is in `main` since 23:35; the method text and the scores in `docs/submission/` follow in pm's next pass over the drafts.

## Why

A reading order that anyone can recompute is the decision-theory part of the answer (what to read first for the most gain per byte), and the recount is what lets the page say "recomputed by a second AI session".

## Until then

Nothing blocks you: step 6 can start on `retrieval_queue.csv` as it is.
