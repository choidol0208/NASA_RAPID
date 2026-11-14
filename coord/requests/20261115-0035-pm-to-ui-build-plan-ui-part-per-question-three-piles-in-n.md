---
from: pm
to: ui
opened: 2026-11-15 00:35 KST
needed_by: 08:00
closed: false
---
# Build plan, ui part: per question, three piles (in NASA's tables / in the archive unprocessed / no record in PSI) and the files of a test

*AI-generated (Claude Code), pm role.*

**The design is in `docs/raw_data_design/design.md`** (English; sections: 3 the design, 6 the build plan, 7 the lunar-habitat screen, 8 claims, 10 fixtures for the checks, 12 risks). It answers the human lead's question of 23:49 ("out of this vast, unlabelled data, which data is the data I need?"). In one sentence: for an environment and a fire-safety question, code places every recorded test as inside the ranges, outside by a recorded value, or not placeable from the table; follows NASA's own test identifiers to the files (a link counts as confirmed only when two labels agree); and shows three piles per question: in NASA's tables / in the archive but unprocessed (which files, how many bytes, how many were opened, what the next read costs) / no record in PSI (with its ground). No AI is needed for any of it. Measured on the lunar habitat: of 60,866 files, 398 (104.4 GB, 0.77% of the bytes) carry the name of one of the 26 tests recorded inside the ranges; the 17 test sheets of the counted tests are 15 kB.

Working decisions (pm took the design's recommendations, on the human lead's instruction to solve the problem; he may overturn any of them): pile 3 is worded "no record in PSI (listing of 14 November 2026)", never "NASA did not test" or "a new test is needed"; values read from raw files are shown as "read from NASA's file, not adopted, not counted", as written (nan and 0.00 included); the order of pile 2 is a fixed public rule, with no probabilities; no test is placed in an environment from the BASS as-run workbook; the lunar habitat and the ISS get the full screen, the other four environments the bars only; counted tests stay P1 133, P2 0, P3 2, S1 298, D1 122, D2 0.

## What I need

Step 8 of the build plan (design.md section 6; the full text of the lunar-habitat screen is section 7). After the three page errors of request 2340, and nothing else new before it.

1. **A header line under the environment title:** the ranges, then "PSI holds 60,866 files (13.47 TB) of 24 combustion investigations. N of them (x GB, y% of the bytes) carry the NASA identifier or the test number of one of the n tests recorded inside these ranges." with the split into small files and archives or recordings, and how many links have two agreeing labels. Numbers from the data role's `file_links_summary.json`; until it lands use `docs/raw_data_design/prototype/lunar_summary.json`.
2. **One bar per question:** tests inside the ranges | not placeable from the table | oxygen given for an oxidizer stream | outside by a recorded value. From `question_chain.csv` (prototype: `docs/raw_data_design/prototype/chain_lunar_habitat.csv`).
3. **Three piles inside each question block, as plain lists:** (1) in NASA's tables; (2) in the archive but not in the table, with two parts: lines actually read ("read from NASA's file, not adopted, not counted", values as written) and lines not yet read (file group, files, bytes, "n of N opened", in the fixed order of `data/catalog/reading_order.csv` when it lands), plus a box "not found in the files opened"; (3) no record in PSI (listing of 14 November 2026), with its ground. Where a gap is a missing test and not unprocessed data, the fixed sentence of `docs/raw_data_design/pile_wording.md` sections 5.2 and 6: "This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of 14 November 2026)."
4. **The files of one test:** pressing a test inside the ranges lists its files (name, bytes, the ground of the link, what was read), with "Download file list (CSV)".
5. **Small print under the block** (design.md section 7, last paragraph): built by code from the PSI file listing of 14 November 2026 and the team's tables; "column seen" is one opened file per group, read by an AI session and read again by the data role, and is not a measurement of the test; values from raw files are not counted; recomputed by a second AI session (lines read by a team member: n); no safety verdict, no prediction.

The lunar habitat and the ISS get everything; the other four environments get the bars only. Not to build: a file search box, an index of all files.

The smallest version that still matters: the header line, the bars, and the three piles as plain lists for the two demo environments (about 2 h).

## Why

It is the answer to "which data do I need out of all this" that a user can act on in five minutes: 0.77% of the archive names their tests; here is what 15 kB of it already says; here is where PSI's tables hold no counted test.

## Until then

pm sends the fixed sentences for pile 3 and the claims wording as soon as the data role's files show their final field names.

## Addendum 01:10: video rows inside the same blocks (video design, build step 8)

No separate video block. In the per-test file list, a video row shows: NASA's file name, bytes, the tie phrase for its link state ("video of this test" only for two agreeing labels; otherwise "tied by the file name only", "tied to the recording day only"), the kind of clip from its name, and either "on-screen readings transcribed (link)" or "on-screen readings per NASA's ReadMe, not transcribed". Per question, one line in pile 2 for video, generated from the chain counts; for the lunar habitat it says that none of the 17 counted tests has a linked video. The transcription warning stands next to every transcription link ("a transcription of NASA's display, not a measurement"). This replaces the single side-pilot sentence now shown for PSI-25. No minimum, maximum or last value of a transcribed column is shown anywhere. Sentences and counts come from the data role's files; pm sends the wording. About 0.75 h on top of the block; if it is not merged and checked by late afternoon, leave it out.


## Correction 01:40: wording (a checking session found three things)

- The sentence "This gap is a missing test, not unprocessed data" is **not** to be used: it implies that a test was not done or should be done, which the human lead's wording for the third pile rules out. Use the sentence now in item 3 above (`pile_wording.md` sections 5.2 and 6).
- File names carry "the NASA identifier or the test number" (102 of the 398 lunar files carry the FLEX test number, 296 an identifier).
- All fixed sentences, with their slots and the ground each needs, are in `docs/raw_data_design/pile_wording.md`; what may be said after which build step is in `docs/raw_data_design/claims.md`. Please take sentences from there and not from `design.md` where the two differ.
