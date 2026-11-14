<!--
Notes for the pm session. This comment is not part of the README section.

AI-generated (Claude Code, pm role) on 2026-11-15, step 9 of docs/raw_data_design/design.md section 6.
Checked by AI sessions: the session that wrote it, a second session against the repository, and a third
that corrected lines 1 and 8 at about 01:40 KST on 15 November (22 experimental tables, 14 of them read into
the team's tests; "tests inside the lunar-habitat ranges" in place of "lunar tests"). Read by a person: none yet.

Where to place it: after "What is implemented today" and before "How it is built".
The section below is twelve lines (title, mark and ten numbered lines; blank lines not counted).

Lines that wait for a build step. Do not place a line before its step has passed its check
(docs/raw_data_design/claims.md, section 2):
  line 1  "the page shows three piles"                      step 8 (page block)
  line 3  "n of N opened", file groups per question         steps 2 and 8
  line 5  398 files, 104.4 GB, 0.77%, 316 files, 86.9 MB    step 3 (today: prototype count; say "prototype" until then)
  line 6  "shown as written" for values of a test           step 4 (today: the design job read the first 700 bytes of each of 17 sheets)
  line 9  "a second AI session recomputes the numbers"      step 7; until then write "recount by a second AI session: not yet"
  line 10 the path validation/raw_chain_recount.py          step 7
Lines 2, 4, 7 and 8 hold today.

Every number is in docs/raw_data_design/claims.md with its file.
-->

## What the three piles claim

*Written with an AI assistant (Claude Code). Counts are the team's computation from NASA PSI's file listing of 14 November 2026 and PSI's tables, not NASA's conclusions.*

1. **The idea.** PSI lists 60,866 files (13.47 TB) for 24 combustion investigations; its experimental tables are 22 files of 0.2 MB, and the team's 1,824 tests come from 14 of them. Instead of processing the archive, code starts from a question and follows NASA's own test identifiers to the files, and the page shows three piles per question.
2. **Pile 1, "In NASA's tables":** the tests recorded inside an environment's oxygen and pressure ranges, and what the tables hold for them.
3. **Pile 2, "In the archive, not in a table":** a test is recorded, but a value the question needs is not in a table. The pile lists the file groups that name the test, with files, bytes and "n of N opened". A listed group is not shown to hold the value.
4. **Pile 3, "No record in PSI (listing of 14 November 2026)":** printed on three grounds only, each with its source: a value common to every mapped table (gravity), every counted test outside by a recorded value, or a quoted sentence about a whole investigation.
5. **What the numbers are.** Files and bytes come from PSI's listing; "n of N" counts files opened. For the lunar habitat, 398 files (104.4 GB, 0.77% of the bytes) carry the identifier or test number of one of the 26 tests inside the ranges; 316 of them are not archives or video recordings (86.9 MB).
6. **Values of a test** appear only where a file was read. They are shown as the file writes them and labelled "read from NASA's file, not adopted, not counted". Counted tests stay P1 133, P2 0, P3 2, S1 298, D1 122, D2 0.
7. **Not claimed:** that the archive was analysed or indexed as a whole; that a file naming a test holds the value; that "not found in the files opened" means absent from the archive; that pile 3 says what NASA tested; that the reading order is NASA's priority.
8. **Limits.** A research exploration tool, not safety guidance. Nothing here predicts an untested condition. The 17 counted tests inside the lunar-habitat ranges are fuel droplets in microgravity at 71.2 to 72.4 kPa.
9. **Who checked.** AI sessions wrote the code; a second AI session recomputes the numbers with separate code. Read by a person: none yet. Review by combustion researchers is a next step.
10. **Where it lives.** Design: `docs/raw_data_design/design.md`. Sentences and their grounds: `pile_wording.md`. Claims with numbers and files: `claims.md`. Check: `validation/raw_chain_recount.py`, against the fixtures of design section 10.
