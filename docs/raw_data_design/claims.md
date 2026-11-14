# What the team may say about the three piles, and what it may not

*AI-generated (Claude Code, pm role) on 2026-11-15, as step 9 of the build plan in `design.md` section 6. It restates `design.md` section 8 after checking each claim against section 9 and against the files in the repository at 00:45 KST. Checked by AI sessions: the session that wrote it, with a recount script; a second session that checked it against the repository; and a third session that corrected it for the second's findings at about 01:40 KST (section 5). Read by a person: none yet.*

## The idea, in one paragraph

NASA's PSI archive lists 60,866 files (13.47 TB) for 24 combustion investigations. PSI's experimental tables are 22 files of 0.2 MB, and the team's 1,824 tests come from 14 of them. Nobody processes the rest in a weekend, and a user does not need all of it. So the code starts from the user's question and follows the identifiers that NASA wrote into file and folder names down to the files. For each fire-safety question in a chosen environment it shows three piles: what is in NASA's tables; what is in the archive but not in a table (which files, how many bytes, how many were opened, what was read); and what has no record in PSI, with the ground for saying so. For a lunar habitat, 398 files (0.77% of the bytes) name one of the 26 tests recorded inside the oxygen and pressure ranges, and the 17 test sheets of the counted tests are 15 kB together. No AI model runs in this chain; AI sessions wrote its code, and pile 2 prints earlier AI readings of file headers with their label. The counts are the team's computation, not NASA's conclusions, and the page is a research exploration tool, not safety guidance.

## How to read this file

- A claim is said together with the number that carries it. The file is where a second person finds that number.
- Section 1 holds today. Section 2 lists what may be said once a build step has passed its check; until then the sentence is not on the page, the slide or the submission text.
- Section 3 lists what may not be said at all.
- Section 4 records where this check changed a sentence of `design.md` section 8. Section 5 lists the corrections made after a second AI session checked this file.
- State of the build at 00:45 KST on 15 November: the design and its prototype files exist (`docs/raw_data_design/`). None of the output files of steps 2 to 8, 11 and 12 exists yet (still so at 01:40 KST). The files of step 10 are in `docs/raw_data_design/` (`psi_metadata_fields.csv`, `psi_metadata_summary.md`); two further AI sessions recomputed them from the same archive bytes (T10).
- Step numbers are those of `design.md` section 6. Fixtures F1 to F6 are those of section 10, named in `pile_wording.md` section 0.

---

## 1. May be said today

Each row was recounted by this job from the file named (script `pmpart/verify_numbers.py`, read-only).

| # | Claim | Number that carries it | File |
|---|---|---|---|
| T1 | PSI lists this many files for the combustion investigations. | 60,866 files; 13,471,850,126,356 bytes (13.47 TB); 24 investigations; listing fetched 2026-11-14T05:57:17Z | `data/pipeline/raw_inventory.json` `_meta` |
| T2 | By file name and PSI category, almost all bytes are archives, and the experimental tables are a tiny part. Nothing was opened for this count. | archives (.zip) 12,689 files, 12,999,389,379,194 bytes, 96.49%; video 2,623 files, 426,053,691,302 bytes, 3.16%; all other kinds 45,554 files, 46,407,055,860 bytes, 0.34%; among them the experimental tables, 22 files, 211,116 bytes (0.0000016% of the bytes, about 1 part in 64 million: 13,471,850,126,356 / 211,116 = 63,812,549) | same, `totals.by_kind` |
| T3 | The team's tables hold 1,824 tests of 12 investigations, read from 14 of PSI's 22 experimental tables; 12 investigations have no row per test. | 1,824 rows; 12 distinct investigations; 14 distinct source files | `data/pipeline/tests.csv`; `pipeline/spec/sources.json` (22 tables) |
| T4 | Placement of the 1,824 tests for the lunar habitat, from the tables alone. | inside 26; cannot be placed 676; oxygen of an oxidizer stream 63; outside by a recorded value 1,059 | `data/pipeline/scenario_tests.csv` |
| T5 | For solid fuels, none of the 139 tests with a recorded oxygen value is at 30% or above; 237 more have neither oxygen nor pressure in a table. | 139 tests, oxygen 13.6 to 22.2%; 237 tests; inside 0 | `scenario_tests.csv`, `tests.csv` |
| T6 | Every test of the per-test tables is a microgravity test in the team's mapping. The level is a constant the team set for each of the 14 tables; the tables have no gravity column. The PSI record's Flight Platform field names the ISS for 11 of the 12 mapped investigations and the Cygnus spacecraft for PSI-99. | `gravity_level` is `microgravity` for 1,824 of 1,824 tests; Flight Platform `International Space Station (ISS)` 11, `Cygnus Spacecraft` 1 | `tests.csv`; `pipeline/spec/sources.json` (`constants`); field `Comment[Flight Platform]` of the metadata archives of step 10 (`psi_metadata_summary.md`) |
| T7 | The counted tests per question. | P1 133, P2 0, P3 2, S1 298, D1 122, D2 0; no counted solid-fuel test has a pressure in a table | `data/pipeline/need_tests.csv`, `tests.csv` |
| T8 | The 26 tests inside the lunar ranges are 17 fuel-droplet tests and 9 gas flames. The 17 are counted for extinction conditions; they are liquid heptane or methanol, in microgravity, at 71.2 to 72.4 kPa and 30% or 34% oxygen. | 17 PSI-69, 9 PSI-159; pressure 71.2341 to 72.3674 kPa; test end 15 disruption, 2 completion; burn time 16; flow 0 | `scenario_tests.csv`, `tests.csv`, `need_tests.csv` |
| T9 | NASA's FLEX table writes the extinction diameter in four ways, and the team's table merges two of them. | 274 rows: 189 numbers above zero, 8 zeros, 49 blanks, 28 en dashes; `tests.csv` turns blank and dash into empty | `data/psi/experimental_tables/PSI-69_Experimental table_FLEX.csv` |
| T10 | In all 24 PSI metadata archives of the combustion investigations, the per-test study file is one placeholder row, and none has an assay file. Said with the label: recomputed by AI sessions from the same archive bytes; a fresh re-fetch of five archives has not run; read by a person: none yet. | 24 of 24: file `s_PSI-<n>.txt` holds a header and one row whose two cells are the placeholder text (56 bytes, the same in all 24); no assay file in 24 of 24; `Study Assay File Name` empty in 24 of 24; SHA-256 of each archive equal to the CSV in 24 of 24 | `docs/raw_data_design/psi_metadata_fields.csv`, `psi_metadata_summary.md`; the archives (302,059 bytes) are in the pm session's scratch folder, not in the repository |
| T11 | As a measurement of the design work, labelled as a prototype count by file name: the files whose name carries the identifier or the test number of one of the 26 tests inside the lunar-habitat ranges. | 398 files; 104,358,456,350 bytes (0.7746% of the archive); 316 files that are not a `.zip` or `.ts` file, 86,853,632 bytes; second label 336 / 47 / 15. For the 17 FLEX tests: 299 files, 24,954,842,492 bytes, by `lunar_links.py` (label in the file name, PSI folder as the second label) | `docs/raw_data_design/prototype/lunar_links_PSI-69.json`, `lunar_links_PSI-159.json`, `lunar_summary.json` |

T11 may be said today only with the words "prototype" or "design measurement". Without them it waits for step 3.

The prototype folder holds a second count for the same 17 FLEX tests: `flex_two_label.py` arrives at 322 (24,957,498,055 bytes; 237 / 47 / 38 by its states) with another rule. It also takes a file in when only its PSI folder number names one of the 17 tests, and it adds the tests up, so 322 counts pairs of a file and a test: 307 distinct files, of which 15 (the files of FLEX-20 in the folder named after FLEX-21) are counted for two tests and 8 (named after identifier `264F003`, in folder `Flex-022`) come in through the folder number (recount `pmpart/fix/two_counts.py` on the design job's saved listing). T11 uses the count by name. The check of step 3 decides which rule the pipeline uses. The state that `flex_two_label.json` calls `confirmed`, a word the answer files forbid, becomes `two_labels_agree` when step 3 lands.

---

## 2. May be said after a build step has passed its check

| Step | Claim | Number that carries it | File the number comes from | Check that must pass | Today |
|---|---|---|---|---|---|
| 2 | For each question and environment, every recorded test is placed as inside, outside by a recorded value, oxygen of an oxidizer stream, cannot be placed from the tables, or no range set. | Lunar habitat 26 / 676 / 63 / 1,059; solid fuels 0 / 237 / 139; ISS 179 / 739 / 106 / 800; Mars habitat no range set for 1,824 | `data/pipeline/question_chain.csv` | F1, F2, F6 | file not there; the numbers hold in `scenario_tests.csv` |
| 2 | The page separates three situations that used to read as one gap: no test recorded at the condition; a test recorded whose value is in a raw file, a document or on a video picture; a test recorded with nothing found in the files opened. | For P1 pressure: raw column 134 (121 + 13), document only 129, not found 113 | `question_chain.csv`, equal to `need_gap_states.csv` | F2 | not built; `need_gap_states.csv` is the same for all six scenarios |
| 3 | For a chosen question in the two demo environments the page lists the PSI files that carry the identifier or test number of the tests recorded inside that environment, with their sizes, for the five investigations that step 3 links (PSI-69, PSI-159, PSI-10, PSI-25, PSI-99). They hold all 26 tests inside the lunar ranges; of the 179 tests inside the ISS ranges, 25 belong to PSI-39, which step 3 does not link. | Lunar habitat: 398 of 60,866 files; 104.4 GB of 13.47 TB (0.77%); 86.9 MB in files that are not archives or video recordings | `data/pipeline/file_links_summary.json`, `test_files.json` | F3; files and bytes per investigation equal `raw_inventory.json` | prototype only (T11) |
| 3 | A link counts as agreed only when two labels that NASA wrote name the same test; the other cases are listed, not resolved. | 336 files where name and folder agree; 47 archives in a folder that names no test; 15 files of FLEX-20 in a folder named after FLEX-21 | `data/pipeline/file_links.csv`, `file_links_summary.json` | step 3 check (336 / 47 / 15); F4 | prototype only |
| 4 | For the 17 counted tests inside the lunar-habitat ranges, NASA's per-test sheets were read and compared with NASA's table. | 17 files, 15,369 bytes; identifier inside equals the table's in 17 of 17; pressure agrees within rounding in 16 of 17; oxygen in 16 of 17 | rows of `data/pipeline/raw_values.csv`; block `flex_test_sheets` of `raw_values_effect.json` | F5; step 4 check | design job only: first 700 bytes of each sheet (11,871 bytes) |
| 4 | Where the table has no number for the extinction diameter (11 tests), the sheet writes a number for 3, `0.00` for 1 and `nan` for 7. Where the table writes a number or a zero (6 tests), the sheet writes the same for 5 and `nan` for 1. Said as what the files write: read from NASA's file, not adopted, not counted. | 3 (FLEX-23, 38, 40); 1 (FLEX-41); 7 (FLEX-19, 22, 24, 27, 28, 37, 42); 5 (FLEX-21, 25, 26, 39, 43); 1 (FLEX-20, table 1.56) | same | F5, F6 | design job only |
| 4 | All 272 FLEX test sheets were read (a census, not a sample), which gives the crosswalk between the number in a file name and NASA's identifier. | 272 files, 250,375 bytes | same | step 4 check | not done |
| 5 | The BASS as-run workbook was read; its two columns stand under a cabin label, and no test was placed from it. | 1 file, 111,886 bytes; 121 runs | rows of `raw_values.csv` | row count equals 121; nothing adopted | not done |
| 6 | The order of what to read first is a published rule over counts and bytes, with the evidence for each row in words. It is the team's rule, not a NASA priority. | per row: files, bytes, target tests | `data/catalog/reading_order.csv` | step 6 check (deterministic; a test counted once; bytes once per group) | not built |
| 7 | The numbers of the chain, the links and the sheets were recomputed by a second AI session with code that does not import the pipeline. | every fixture of `design.md` section 10 reproduced | report of `validation/raw_chain_recount.py` | R7 | not built |
| 8 | The page shows the header line, one bar per question and the three piles for the lunar habitat and the ISS; the other four environments show the bars. | every number equals its CSV cell | `web/dist/data/chain/<scenario>__<need>.json` | B8 | not built |
| 10 | In how many of the 24 PSI metadata archives the per-test file is a placeholder. | 24 of 24 | `reports/isa_metadata_fields.csv` in the plan; written as `docs/raw_data_design/psi_metadata_fields.csv` with `psi_metadata_summary.md` | a second session re-reads five | `psi_metadata_fields.csv`: placeholder study file in 24 of 24, no assay file in 24 of 24; recomputed by a second and a third AI session from the same archive bytes (SHA-256 equal to the CSV for 24 of 24); a fresh re-fetch of five archives has not run. Read by a person: none yet. The design's check is met for the parsing, not for the fetching; T10 says the figure with that label |
| 11 | A team member opened a random sample of links on the PSI page and read the pile-3 sentences of the two demo environments. | sample size, wrong links, and the bound: with none wrong in 30, fewer than 9.6% | `reports/spot_check_raw.csv` | S11 | not done; the label is "Read by a person: none yet" |
| 12 | The directories of the 47 archives of the 17 counted tests inside the lunar-habitat ranges were read without downloading the archives. | members and kinds per archive; bytes requested | `data/pipeline/archive_members.csv` | members parsed equal the count in the end record | 3 of 47 read by the design job (370,662 bytes) |

Claims that describe how the work was done, and hold when the steps above have landed:

| Claim | Number that carries it | File |
|---|---|---|
| The chain is deterministic code over PSI's public listing and the team's tables. No language model is called in it, and nothing is generated when a page loads. | 0 model calls in `pipeline/raw_gaps.py`, `web/build.py` and the page block | the code itself |
| The design work read PSI by listing and by small range requests instead of downloading the archive. | about 27.9 MB in all, of which 22,282,256 bytes are in three transfer logs: listings of five investigations (5,553,233 bytes), range reads, signing calls and four documents; the directories of 18 archives of 8 kB to 32.9 GB were read without download | `design.md` section 9; `net/`, `tiers/` and `files_angle/transfer_log.jsonl` of the design job |
| AI sessions wrote the code. An earlier AI reading of file headers is kept with its label and with "n of N files opened". What a second AI session recomputed and what a person read are labelled apart. | round 1 of the header reading: 97 mappings, 58 removed after an independent re-read, 41 kept | `pipeline/spec/raw_columns.json` `_meta.review_2026_11_14`; `compliance/AI_USAGE_LOG.md` |

The pitch sentence of `design.md` section 1, in a form that passes the wording decisions (after steps 3 and 4):

> Say what you are building. We show the 0.77% of NASA's 13.47 TB whose names carry your tests, what 15 kB of it already says, and where PSI holds no record (listing of 14 November 2026).

The 0.77% and the 15 kB are the lunar-habitat figures. The design's ending "where no test exists at all" is not used: it would speak about more than PSI's record. The ending carries the listing date, as the label of pile 3 does.

---

## 3. May not be said

| # | Not to be said | Why, with the number |
|---|---|---|
| N1 | That the archive was analysed, labelled or indexed as a whole. | Rules that tie a file name to a test exist for six of the 24 investigations. The directory of 18 of 12,689 archives was read, and no archive content was opened. On-screen values were transcribed for 19 BASS-II clips only. |
| N2 | That a file which names a test holds the quantity a question needs, or that all files of a group share the header seen in the one file opened. | One sample file per group was opened in the header survey (`raw_columns.json`). |
| N3 | That a value read from a raw file is the test's result or NASA's table value. | Counts stay P1 133, P2 0, P3 2, S1 298, D1 122, D2 0 (F6). |
| N4 | That `nan`, `0.00`, a blank or a dash mean "no extinction" or "not measured". | No file read says which. |
| N5 | That the BASS as-run workbook places 121 tests. | Its columns stand under a cabin label; the location is not stated. |
| N6 | That "not found in the files opened" means absent from the archive. | It is a statement about the files opened. |
| N7 | That pile 3 says what NASA tested or did not test, or that a test is needed. This includes "this gap is a missing test" and "a test that PSI's tables do not hold". | Pile 3 is "No record in PSI (listing of 14 November 2026)", on three grounds, for the 1,824 tests of the mapped tables. The sentence for the second ground is "This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of 14 November 2026)" (`pile_wording.md` sections 5.2 and 6). |
| N8 | That the reading order is NASA's priority, or that the next read yields the value. | It is the team's rule over counts and bytes. |
| N9 | That the 17 droplet tests cover a lunar habitat. | They are liquid droplets in microgravity at 71.2 to 72.4 kPa, above the 70.3 kPa of the challenge statement; the wording of 14 November 14:15 stays. |
| N10 | Any link total built on the number in a FLEX file name alone. | The name number and the table's number are two numberings: in 115 of 248 PSI folders they point to different rows, and the identifier `193F001` is on two rows (`prototype/flex_two_label.json`). An earlier name join tied 5,075 of 6,452 FLEX files this way. |
| N11 | That the team's links are NASA metadata. | They are the team's description, built from labels NASA wrote. |
| N12 | That a person checked what an AI session checked, or that a specialist or NASA reviewed the work. | Read by a person: none yet. Review by combustion researchers is a next step. |
| N13 | Any safety verdict, limit or statement about an untested condition. | The page is a research exploration tool. |
| N14 | That all 398 files carry "the NASA identifier". | 296 names carry an identifier (197 FLEX, 99 CFI-G); 102 carry the FLEX test number. Say "the identifier or the test number". |
| N15 | That the 82 large files are "image archives". | They are 74 `.zip` files and 8 `.ts` files by extension. Frames were seen in the directories of 3 archives. |
| N16 | That the sentence about BASS-II pressure is NASA's statement. | It is quoted from a paper of the investigators (`ICES-2019-BASS2`, Section II), read in full text. |
| N17 | That the test sheets were read in full, before step 4 has run. | The design job read the first 700 bytes of each of the 17 sheets: 11,871 of 15,369 bytes. |
| N19 | That NASA's tables record the gravity level of a test, or that the PSI record states it. | The tables have no gravity column. `sources.json` sets microgravity as a constant of each of the 14 tables and names no document for it. The Flight Platform field of the PSI record names a platform (the ISS for 11 of the 12 mapped investigations, the Cygnus spacecraft for PSI-99), not a gravity level. |
| N18 | "Fewer than 9.5%" for a spot check of 30 links with none wrong. | The exact bound is 9.503%. Say "fewer than 9.6%". |
| N20 | That the 26 tests are "lunar tests", or that they were run at lunar conditions or in the lunar-habitat atmosphere. | They are microgravity tests whose recorded oxygen and pressure lie inside the ranges the team set for the lunar habitat. The 17 droplet tests were recorded at 71.2 to 72.4 kPa, 1 to 2 kPa above 10.2 psi (decision of 14 November, 14:15). Say "tests recorded inside the lunar-habitat ranges". |
| N21 | "No AI in the chain." | Pile 2 prints AI readings of file headers from `raw_columns.json` ("column seen"), and AI sessions wrote the code. What holds is that no model is called while the chain runs. Say "No AI model runs in the chain". |
| N22 | That the nine CFI-G tests inside the lunar ranges are all left out for the purpose of the record. | 7 have an S1 row with `objective_link` `not_stated`; 2 (`CFIG-N-21106F2`, `CFIG-N-21106F5`) hold no outcome in NASA's table and have no row in `need_tests.csv`. |
| N23 | That no file opened holds a flow header for FLEX. | Four nozzle-speed headers were seen in one opened file and not mapped, because the unit is written as N/A (`raw_columns.json`, PSI-69). Say that no header was accepted for the variable. |
| N24 | That PSI's metadata archives name no test, no sample and no file. | The study file name is filled, and the free-text fields were not read for content. What holds: the per-sample layer is one placeholder row and there is no assay file, so no structured field names a test or a raw data file (`psi_metadata_summary.md`). |

---

## 4. `design.md` section 8 checked against section 9 and the repository

| Claim in section 8 | Result of the check | What changes |
|---|---|---|
| 1. Files that carry the names of the tests: 398 of 60,866; 104.4 GB of 13.47 TB (0.77%); 86.9 MB | The numbers agree with section 9 and with the prototype files. The link files of step 3 do not exist yet. | Said as a prototype count today (T11); "the identifier or the test number" (N14). |
| 2. Three situations kept apart | `need_gap_states.csv` has the same 71 rows for each of the six scenarios, so the per-environment view is not in the repository yet. | Waits for step 2. |
| 3. Solid fuels: 139 with oxygen 13.6 to 22.2%; 237 cannot be placed; no test at lunar gravity | Reproduced from `scenario_tests.csv` and `tests.csv`. | Holds today (T5, T6). "No test at lunar gravity" is said for the per-test tables: 1,824 tests of 12 investigations. The gravity level is a constant of the team's mapping, not a table column, so "recorded at" becomes "in the team's mapping". |
| 4. Test sheets: identifier 17 of 17; 3 / 1 / 7 where the table has no number; "the same in 5 of 6 where both write a value" | Reproduced from the design job's saved comparison. In the sixth case the sheet writes `nan`, so "both write a value" does not describe it. | Reworded: where the table writes a number or a zero (6 tests), the sheet writes the same for 5 and `nan` for 1. The saved comparison is not in the repository; step 4 writes it. |
| 5. Transfers: about 27.9 MB, "five listings", 18 archive directories, 17 test sheets | The six terms of section 9 sum to 27,856,416 bytes. Three transfer logs of the design job sum to 22,282,256 bytes; for the other 5.57 MB this job found no log file, only the totals in section 9. One log holds the five listings; listings of a sixth investigation (PSI-159) are saved in another folder of the job. | Said as "about 27.9 MB (design section 9)", with the logged part named. |
| 6. Reading order is a published rule | No file yet. | Waits for step 6. |
| 7. Three metadata files with a placeholder row | The row was found in the saved reads of PSI-159, PSI-25 and PSI-99. Step 10 then fetched all 24 archives, and two further AI sessions recomputed its table from the same bytes: placeholder in 24 of 24, no assay file in 24 of 24. | The figure for all 24 holds today with its label (T10). |
| 8. AI sessions wrote the code; labels say who checked | The label wording is fixed in `pile_wording.md` section 11. | "Read by a person: none yet" until step 11. |
| May not 1: "the inside of 12,689 archives was read for 18" | 18 directories were read; no member of an archive was opened. | "The directory of 18 of 12,689 archives" (N1). |
| May not 9: "5,075 FLEX files; 12,992 of 15,263 files in six investigations" | 5,075 of 6,452 FLEX files is in the design job's `out/join_summary.json`. That file covers five investigations (11,507 files, 9,514 tied to a test); this job did not find the source of 12,992 of 15,263. | N10 uses the FLEX figure only. |
| Section 5, "accepted 19 of 68 in round 2" | `raw_columns.json` records 19 accepted entries in round 2; this job did not find the 68 there. | The claims above use the round 1 figures only. |
| Section 4, "0 wrong in 30 means fewer than 9.5%" | 1 - 0.05^(1/30) is 9.503%. | "Fewer than 9.6%" (N18). |

Everything else in section 8 agrees with section 9 and with the repository files this job could read.

---

## 5. Corrections of 15 November, about 01:40 KST

A second AI session checked this file against the repository. A third AI session (pm role) checked each point in its source (`pmpart/fix/confirm.py`, `pmpart/fix/two_counts.py`, read-only) and corrected the file. Read by a person: none yet.

| Where | What was wrong | What it says now |
|---|---|---|
| T2 (and `design.md` section 9, where the figure came from) | The experimental tables were given as 0.0016% of the bytes. 211,116 / 13,471,850,126,356 is 1.567e-8. | 0.0000016% of the bytes, about 1 part in 64 million. `design.md` section 9 is corrected the same way. |
| The idea paragraph, T2, T3 | "The per-test tables ... are 22 files": 22 is the number of PSI's experimental tables; the team's tests come from 14 of them. | "PSI's experimental tables are 22 files of 0.2 MB, and the team's 1,824 tests come from 14 of them." |
| T10 and the row of step 10 | They said the 24-archive figure was not checked. | Recomputed by a second and a third AI session from the same archive bytes; the label says that a fresh re-fetch of five archives has not run. |
| T11 | Nothing said that the prototype folder holds a second count (322) for the 17 FLEX tests. | Both counts with their rules; 322 counts pairs of a file and a test (307 distinct files). |
| T6, N19 | The gravity constant had no document behind it. | The Flight Platform field of the PSI record is named, as a platform and not as a gravity level. |
| T11, rows of steps 4 and 12 | "lunar tests". | "tests inside the lunar-habitat ranges" (N20). |
| Row of step 3 | "For a chosen question and environment the page lists the PSI files": step 3 links five investigations only. | The claim is scoped to the two demo environments and the five investigations; PSI-39 (25 of the 179 tests inside the ISS ranges) is named as not linked. |
| The pitch sentence | "where PSI holds no record of a test", without the date. | "where PSI holds no record (listing of 14 November 2026)". |
| N7, N20 to N24 | Not listed. | Added from the check: the "missing test" sentences, "lunar tests", "No AI in the chain", the reason for the nine CFI-G tests, the flow header, and what the metadata archives do not name. |
