---
from: pm
to: data
opened: 2026-11-15 00:35 KST
needed_by: 04:00
closed: false
---
# Build plan, data part: the question chain, file-to-test links, the FLEX test sheets (design in docs/raw_data_design/)

*AI-generated (Claude Code), pm role.*

**The design is in `docs/raw_data_design/design.md`** (English; sections: 3 the design, 6 the build plan, 7 the lunar-habitat screen, 8 claims, 10 fixtures for the checks, 12 risks). It answers the human lead's question of 23:49 ("out of this vast, unlabelled data, which data is the data I need?"). In one sentence: for an environment and a fire-safety question, code places every recorded test as inside the ranges, outside by a recorded value, or not placeable from the table; follows NASA's own test identifiers to the files (a link counts as confirmed only when two labels agree); and shows three piles per question: in NASA's tables / in the archive but unprocessed (which files, how many bytes, how many were opened, what the next read costs) / no record in PSI (with its ground). No AI is needed for any of it. Measured on the lunar habitat: of 60,866 files, 398 (104.4 GB, 0.77% of the bytes) carry the name of one of the 26 tests recorded inside the ranges; the 17 test sheets of the counted tests are 15 kB.

Working decisions (pm took the design's recommendations, on the human lead's instruction to solve the problem; he may overturn any of them): pile 3 is worded "no record in PSI (listing of 14 November 2026)", never "NASA did not test" or "a new test is needed"; values read from raw files are shown as "read from NASA's file, not adopted, not counted", as written (nan and 0.00 included); the order of pile 2 is a fixed public rule, with no probabilities; no test is placed in an environment from the BASS as-run workbook; the lunar habitat and the ISS get the full screen, the other four environments the bars only; counted tests stay P1 133, P2 0, P3 2, S1 298, D1 122, D2 0.

## What I need

Steps 2, 3, 4, 5 and 12 of the build plan (design.md section 6), in this order. You are already doing part of step 3 and of step 12; please fold what you have into these outputs.

1. **Step 2, the question chain (about 2.5 h): `data/pipeline/question_chain.csv`.** One placement per test and environment (`inside`, `outside_by_recorded_value`, `oxygen_of_oxidizer_stream`, `cannot_be_placed_from_table`, `no_range_set`) and one location per needed quantity (`table_cell`, `raw_file_value_read`, `raw_file_column_seen`, `video_on_screen_text`, `document_sentence`, `not_found_in_files_opened`), extending `pipeline/raw_gaps.py`. Prototype: `docs/raw_data_design/prototype/chain_proto.py` and `chain_lunar_habitat.csv` (561 rows). Check in `pipeline/check.py` with the fixtures of design.md section 10 (lunar habitat 26 / 676 / 63 / 1,059; solid 0 / 237 / 139; ISS 179 / 739 / 106 / 800; sums equal `need_gap_states.csv`; the four frozen files unchanged).
2. **Step 3, file-to-test links (about 1.5 h): `data/pipeline/file_links.csv`, `file_links_summary.json`, `test_files.json`, `listing_snapshot.json`** for PSI-69, PSI-159, PSI-10, PSI-25, PSI-99, with the two-label rule (number in the name, NASA identifier in the name, PSI folder label, identifier inside the file) and the states `two_labels_agree`, `one_label`, `labels_disagree`, `id_not_in_table`, `day_only`, `none`. FLEX is never linked by the number in the name alone: a judge of the design recounted that the name number and the identifier in the same PSI folder disagree in 114 of 248 folders. Conflicts are listed, not resolved. `listing_snapshot.json` is needed because `data/psi/file_listings/` is not in the repository.
3. **Step 4, the 272 FLEX test sheets (about 1.5 h; 250,375 bytes in all).** Parse the key = value lines, tie each sheet by the identifier printed inside plus a second field, compare every field with the table row, keep nan, 0.00, blank and dash as written (the table has 49 blank and 28 en-dash extinction-diameter cells; `tests.csv` turns both into empty). Output as rows of `raw_values.csv` with the state "read from NASA's file, not adopted" and a block in `raw_values_effect.json`. Fixture: the 17 lunar sheets (identifier 17 of 17; pressure 16 of 17; oxygen 16 of 17).
4. **Step 5 (0.5 h): the BASS as-run workbook** (`PSI-26 As Run_Test Matrix.xlsx`, 111,886 bytes): the two cabin-block columns for 121 runs, with the codes `location_not_stated` and `magnitude_not_as_unit_written`. No test is placed from it.
5. **Step 12, optional:** the zip directories of the 47 FLEX image archives of the 17 lunar tests by range request (about 6 MB), as `data/pipeline/archive_members.csv`.

The smallest version that still matters is items 1, the 17 lunar sheets of item 3, and the file list of the 26 lunar tests of item 2. If time runs short, deliver those first and say so.

Field names: ui starts on the prototype file today; if you change a column name of `question_chain.csv`, tell ui in a request.

## Why

It turns one undivided gap into three: no test recorded at the condition; a test exists and the value sits in a raw file, a document or on a video picture; a test exists and the value was not found in the files opened. That is the human lead's question, answered for the demo environments with files and bytes.

## Until then

pm writes the wording for pile 3 and the claims section of the README, reads the 24 PSI metadata archives (0.3 MB) for what their per-test files hold, and finishes the video part of the design.
