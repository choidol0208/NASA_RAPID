# What to do with the video data: final plan

*AI-generated (Claude Code) on 2026-11-15 for the pm role, from four research sheets, one candidate design and two reviews of this workflow. Not reviewed by a person. The repository (`/Users/choidol/Desktop/NASA/NASA_RAPID`, state `2d503de`) and the pilot disk were read only. This final step made no network request (0 bytes). It recounted every figure it relies on with its own code: `final/video_final.py`, outputs `final/video_final.json`, `final/video_links_states.csv`, `final/shortlist_iss_P1_main_view.csv`.*

Working folder: the design job's scratch folder on the pm session's computer (not in the repository). The tables a role needs are copied to `docs/video_design/prototype/`: `video_index_names.csv` (all 2,623 videos by name), `video_links_states.csv` (link state per video), `video_final.json` and `video_final.py` (the final recount), `shortlist_iss_P1_main_view.csv`, `need_video_map.csv`, `video_sample.csv`. No frame of NASA video is in the repository. Paths below that do not start with `/` or with a repository folder are relative to it.

This plan is the video part of the design the team adopted at 00:35 (`docs/raw_data_design/design.md`). It uses that design's words (placements, locations, link states, piles) and adds no second vocabulary, no second page block and no second set of sentences.

---

## 1. The answer

**Do not process the videos. Index them, tie them to tests, and look deeper only where a question needs it.**

1. All 2,623 video files (426,053,691,302 bytes, 14 of the 24 investigations) are indexed from PSI's public listing by the identifiers NASA wrote into file and folder names. No video byte was read for this.
2. Under the adopted two-label rule, 662 videos (152.3 GB) are a "video of this test" for 463 tests: the file name and the PSI folder name the same test. 374 more are tied by one label, 10 have labels that disagree, 1,217 reach only a test day, 330 carry an identifier the table does not list, 30 carry none.
3. A question therefore maps to a short, named list of files. ISS, flammability limit: 49 main-view recordings, 3.52 GB, instead of 426 GB. Lunar habitat: none of the 17 counted tests has a video tied to it, and the page says so.
4. What a video can add is narrow and known. In the files sampled, NASA's on-screen readings (FUEL, AIR, FAN, RAD, date, clock) appear in BASS-II, BASS, SLICE and SPICE only. For BASS-II a NASA document says what three of them are. They carry no oxygen, pressure, CO, CO2 or smoke value. 19 BASS-II clips are transcribed; a transcription is not a measurement.
5. Nothing is measured from the picture. The one automatic signal tried (brightness as flame-out) was right in at most 1 of 19 clips, and the investigators took their published numbers from still cameras, science cameras and sensors, not from this video.

**One sentence.** For a chosen environment and question, the page shows which counted tests have a NASA video, by which labels the tie holds, which files and bytes that is, what their screen carries for the question and what it cannot tell; deeper reading (header, sample frames, on-screen text) is done only for the files a question needs, and each statement says at which depth it was made.

**Today's path costs 0 bytes of transfer.** It moves the name ties into the adopted chain, adds fixed sentences, and ships one shortlist file. One small header read (about 25 MB) is offered to the team lead; everything larger is recommended against for today.

---

## 2. What this step changed after the two reviews

Every `must_fix` and `should_fix` was applied. Three points were applied in a changed form; the reason is given.

| Review point | What was done |
|---|---|
| Scientist 1 (must): the shortlist left out clips that hold the end of a test | Main view is now "no `2ND_VIEW`, no `Still_Sequence`, not a post-burn picture, not a rack, monitor or other-camera clip". Portions recorded during loss of signal stay in, marked. ISS flammability: 49 files, 3,515,643,202 bytes, 45 tests (was 44 files, 44 tests). BASS2-P18 enters; its only main-view file runs "to end of test". |
| Scientist 2 (must): a transcription invites reading the last or largest FAN value as the blowoff flow | The warning of section 7.1 is printed, word for word, on every transcription link and in the README. The page shows no minimum, maximum or last value of any transcribed column. A row flagged `half_updated` is shown with its flag. |
| Scientist 3 / Builder 1 (must): ties shown as certain still included disagreeing labels; own tie words; team resolved B15 to B17 | Video ties now use the adopted link states (section 4). "Video of this test" is used only for `two_labels_agree`. The B15-to-B17 correction is withdrawn: those 2 files are `labels_disagree` and listed. So are the 2 O10 files (day in the name 203, table 213), B3 in folder B1, CFI-1323 (2 files), FLEX-13 and the 2 CFI-G names with a mistyped test point. The agreement of the data role's table with the scratch index is described as "two tables built separately by two AI sessions from the same PSI listing agree on 803 tests" and is used as a recount check, not as a label. |
| Builder 1, changed: "use the sample number and GMT day in the name as the BASS-II second label" | The second label is the PSI folder name (it is on the adopted list of labels). Day and sample are kept as a consistency check only, because they do not single out a row: in NASA's BASS-II table 14 pairs of day and sample belong to two tests each (28 tests; for example P5 and P9, O12 and P25, and every a/b pair). With day and sample as the second label, 47 files of a/b runs would count as confirmed although nothing but the letter in the file name separates run a from run b. They are `one_label`, with the reason printed. |
| Scientist 4: RAD shown as "the radiometer" | The sentence of section 7.2 is on the card, word for word. |
| Scientist 5: the one-day date offset | NASA's sentence is quoted for BASS-II only, with "observed on 3 July 2014 clips; February 2014 clips not checked". No code converts a screen date into a test date, for any investigation. |
| Scientist 5, changed: "do not shift any date for BASS" | Applied to screen dates. The BASS day tie uses the date in the *file name*; NASA's As-Run matrix carries both dates per row (`Actual Date`, `Date on videos and images`). The data role should replace the arithmetic "name date minus one day" by a lookup in that column and list any tie that changes. Until then the 113 day ties stand as computed and say so. |
| Scientist 6: overlay inside the ACME outreach clip | Recorded as "edited outreach video; contains a clip with an on-screen display dated 2012, before the ACME recording dates in this record; not tied to any test". It is not counted as readings on screen for PSI-20. |
| Scientist 7 / Builder 6: header and frame reads without a lead decision | Both need the lead's yes. The frame step is off today's path. The header step is offered for the 49 shortlist files only (section 9). Each read stops when its byte counter passes its estimate by 50%. |
| Scientist 8 / Builder 7: transcribing 37 more clips | Not today (recommendation). With the corrected main view it would be 42 files, 2,867,152,457 bytes. If the lead overrules: only after the adopted steps 2, 3 and 8 are merged by about 14:00, with the README's own pass rule (0 wrong in at least 300 values per recording-day group) written first, and nothing ships if the audit is not finished by 20:00. |
| Builder 2 (must): separate index, counts file and page block | Folded into the adopted chain: video rows in `file_links.csv` and `test_files.json`, one `video_on_screen_text` row per question in `question_chain.csv`, counts as a view over the chain. On the page: video files in the per-test file list that the ui role builds anyway, and one pile-2 line per question. The 2,623-row index goes into the repository as a file for the README and the recount, not as page data. |
| Builder 3 (must): the lunar sentence | Scoped and generated from counts: none of the 17 counted tests; 8 of the 9 CFI-G gas-flame tests inside the ranges have a video (8 files, 2,640,554,564 bytes, name and folder agree), and CFI-G counts for no question. |
| Builder 4 (must): starting files sit in this session's scratch folder | First pm action: commit the prototype under `docs/video_design/prototype/`. The file version comes from the adopted `listing_snapshot.json`; the scratch index has the PSI file id but no version column. |
| Builder 5: two tie bases and two matching schemes | One basis: tests are counted by link state (`two_labels_agree` first, the others beside it) and by the adopted placement (inside / cannot be placed / outside). The old tier words ("matched on oxygen") are gone. |
| Builder 8: two separate asks of a person | One sitting: the 30 seeded links of the adopted step 11, 10 of them drawn from video rows. |
| Builder 9: a third source of sentences | The video sentences are templates in the same place as the pile-3 wording (`pipeline/spec/answers.json`, through a request to data). |
| Minor points | 22 sampled videos have frames (66 frames) and 15 a header only, from `video_sample.csv`; the "20 / 60" of one sheet is dropped. "Could carry" sentences start with "Not derived:". The FLEX 2013-2014 sentence says their atmosphere is not stated. |

---

## 3. The problem in numbers

| What | Value | Source |
|---|---|---|
| Video files in PSI's combustion listings | 2,623 files, 426,053,691,302 bytes (426.05 GB) | `video_index_names.csv`; equals `data/pipeline/raw_inventory.json` |
| Investigations with a video file | 14 of 24 (PSI-10, 20, 21, 22, 23, 25, 26, 39, 69, 101, 102, 106, 107, 159). Saffire-I/II/III list none; archives were not opened. | same |
| By container extension | mp4 1,847; ts 773; mpg 2; avi 1 | `final/video_final.json` `ext` |
| Largest holdings | PSI-39 CFI 246 files 128.71 GB; PSI-159 CFI-G 337 files 81.72 GB; PSI-10 Flame Design 317 files 75.06 GB | `video_index_summary.json` |
| Investigations whose sampled frames show NASA's on-screen readings | PSI-25, 26, 106, 107: 457 files, 46,570,199,389 bytes (46.6 GB) | `video_sample.csv`; `final/video_final.json` `overlay_investigations` |
| Test rows in NASA's tables (team's `tests.csv`) | 1,824 | `data/pipeline/tests.csv` |

---

## 4. Tying a video to a test: the adopted two-label rule

**Labels used.** (1) The NASA identifier in the file name. (2) The PSI folder name. Nothing else counts as a label today. For BASS-II the day (`GMT`) and sample number in the file name are compared with the tied table row as a consistency check; a mismatch makes the link `labels_disagree`, a match adds no label (see section 2).

**Scope and state.** Each video gets a tie scope (`test`, `run`, `day`, `several_days`, `none`) and one of the adopted link states. The team never resolves a disagreement.

| Link state | Videos | Bytes | Meaning for video | Phrase on the page |
|---|---|---|---|---|
| `two_labels_agree` | 662 | 152,320,655,239 | file name and folder name the same test | "video of this test (file name and PSI folder name the same test)" |
| `one_label` | 374 | 81,527,352,372 | only one label names the test | "tied by the file name only" or "tied by the folder name only"; for a/b runs: "tied by the file name only: the folder, the sample and the day name both runs of this sample" |
| `labels_disagree` | 10 | 5,118,358,115 | name, folder or table point to different rows | "tied by file name; folder or table disagrees", both labels printed, listed |
| `day_only` | 1,217 | 102,112,670,418 | 1,188 a test day, 26 a folder of several days, 3 the runs of one sample on one day | "a video of that test day (n tests that day; which one is not known)" |
| `id_not_in_table` | 330 | 83,454,932,324 | the name carries an identifier NASA's table does not list | "carries an identifier that NASA's table does not list" |
| `none` | 30 | 1,519,722,834 | outreach, calibration, engineering clips, no identifier | "not tied to a test" |

Sum: 2,623 videos. Tests reached at test scope: 813 of 1,824 (463 with at least one `two_labels_agree` video, 344 with `one_label` at best, 6 with `labels_disagree` only).

**Per investigation (videos).**

| Investigation | two labels agree | one label | labels disagree | day only | id not in table | none |
|---|---|---|---|---|---|---|
| PSI-10 ACME Flame Design | 0 | 306 (folder names the day only) | 0 | 11 | 0 | 0 |
| PSI-20 ACME BRE | 0 | 0 | 0 | 163 | 33 | 3 |
| PSI-21 CLD Flame | 0 | 0 | 0 | 358 | 2 | 3 |
| PSI-22 E-FIELD Flames | 0 | 0 | 0 | 215 | 0 | 6 |
| PSI-23 s-Flame | 0 | 0 | 0 | 285 | 1 | 4 |
| PSI-25 BASS-II | 244 | 47 (a/b runs) | 5 | 0 | 0 | 0 |
| PSI-26 BASS | 0 | 0 | 0 | 113 | 1 | 0 |
| PSI-39 CFI | 101 | 5 (folder only) | 2 | 20 | 118 | 0 |
| PSI-69 FLEX | 3 | 5 (folder only) | 1 | 0 | 163 | 11 |
| PSI-101 SAME-R | 0 | 0 | 0 | 8 | 0 | 0 |
| PSI-102 SAME | 0 | 0 | 0 | 0 | 0 | 2 |
| PSI-106 SLICE | 0 | 0 | 0 | 27 | 0 | 1 |
| PSI-107 SPICE | 0 | 0 | 0 | 7 | 12 | 0 |
| PSI-159 CFI-G | 314 | 11 (name only) | 2 | 10 | 0 | 0 |

**The 10 files whose labels disagree** (listed on the page, tied to no test as "video of this test"):

- `PSI-25_Raw Data_BASS_GMT183_SAMPLE_175_TESTB15.mp4` and `..._TESTB15_2ND_VIEW.mp4`: name says B15, folder says B17; day and sample fit the B17 row.
- `PSI-25_Raw Data_BASS_GMT203_SAMPLE_210_TEST_O10_2ND_VIEW.mp4` and `..._O10_Still_Sequence.mp4`: name and folder say O10; the name says day 203, the table says 213.
- `PSI-25_Raw Data_BASS_GMT50_SAMPLE_148_TEST_B3.mp4`: name says B3 (day and sample fit the B3 row), folder says B1.
- `PSI-39_Raw Data_vlc-record-2017-07-10-16h15m31s-udp_F191D05.mp4` and `.ts`: name F191D05, folder F195D01.
- `PSI-69_Raw Data__ISS_20090625_153031_256R002.mpg`: name 256R002 (table row 13, dated 6/25/2009), folder `FLEX 013_22_May_2009_MeOH_256R001` (identifier and date of table row 11). NASA's `256R002_Readme.txt` names this file as the ISS video of that test point; the folder still disagrees, so it is listed.
- `PSI-159_Raw Data_vlc-record-2021-05-05-16h29m30s-udp____211125A2.ts` and `...-udp____2117A4.ts`: the name's test point is not a valid one; the folders say 21125A2 and 21174A4.

Tests left without a "video of this test" by this: BASS2-B17, BASS2-O10, CFI-1323, FLEX-13, CFIG-N-21125A2, CFIG-N-21174A4.

**Counted tests with a video, per question** (`objective_link = stated`; best link state over all videos of the test):

| Question | Counted tests | two labels agree | one label | labels disagree only | no video tied to the test |
|---|---|---|---|---|---|
| P1 Flammability limit | 133 | 99 | 18 | 2 | 14 (6 BASS-II, 8 Saffire-II) |
| D1 Combustion products | 122 | 98 | 16 | 2 | 6 |
| S1 Extinction conditions | 298 | 19 (16 BASS-II, 3 FLEX) | 10 (6 BASS-II, 4 FLEX) | 1 (FLEX-13) | 268 (265 FLEX, 3 BASS-II) |
| P3 Flame spread | 2 | 0 | 0 | 0 | 2 (Saffire-I: no video file in the listing) |
| P2 Ignition, D2 Smoke | 0 | | | | no counted test |

Videos tied at test scope to a counted test of any question: 298 files, 17,993,880,758 bytes (289 BASS-II, 9 FLEX).

**By placement for the two demo environments** (adopted placement rule; tests can be counted for several questions, so rows must not be added):

| Environment, question, placement | Counted tests | two labels agree | one label | disagree only | none |
|---|---|---|---|---|---|
| ISS, P1, oxygen inside and pressure not in the table | 55 (47 BASS-II, 8 Saffire-II) | 42 | 4 | 0 | 9 |
| ISS, P1, outside by a recorded value | 78 | 57 | 14 | 2 | 5 |
| ISS, D1, oxygen inside and pressure not in the table | 45 | 42 | 2 | 0 | 1 |
| ISS, D1, outside | 77 | 56 | 14 | 2 | 5 |
| ISS, S1, inside | 56 (FLEX) | 2 (2 files, 65,710,958 bytes) | 0 | 0 | 54 |
| ISS, S1, oxygen inside and pressure not in the table | 7 (BASS-II) | 3 | 4 | 0 | 0 |
| ISS, S1, outside | 235 | 14 | 6 | 1 | 214 |
| ISS, P3, oxygen inside and pressure not in the table | 2 (Saffire-I) | 0 | 0 | 0 | 2 |
| Lunar habitat, S1, inside | 17 (FLEX) | 0 | 0 | 0 | 17 |
| Lunar habitat, S1, outside | 281 | 19 | 10 | 1 | 251 |
| Lunar habitat, P1 / D1 / P3 | 133 / 122 / 2, all outside by a recorded oxygen value | 99 / 98 / 0 | 18 / 16 / 0 | 2 / 2 / 0 | 14 / 6 / 2 |

All tests inside the lunar ranges (26: 17 FLEX, 9 CFI-G): 8 have a `two_labels_agree` video, all CFI-G (8 `.ts` files, 2,640,554,564 bytes); 18 have none. All tests inside the ISS ranges (179): 41 two labels agree, 54 one label, 84 none.

**Name rules and their documents** (unchanged from the names sheet; rules in `scripts/video_names.py`):

| Investigation | Rule in short | Rests on |
|---|---|---|
| ACME (PSI-10, 20, 21, 22, 23, 159) | test point `YYDDDX#` after `udp_` or at the start of the name; `vlc-record-YYYY-MM-DD-HHhMMmSSs` is the start of a stream recording | ACME BRE Readme (PSI-20): test names are formatted YYDDDX#. Applying it to Flame Design and CFI-G is the team's extension; the PSI-10 as-run file carries `testpointName:19137K1`. |
| BASS-II (PSI-25) | `BASS_GMT{day}_SAMPLE_{n}_TEST_{PI initial + number + a/b}` | BASS-II ReadMe, field "Videos" and field "Test number" (quoted in 7.3). |
| BASS (PSI-26) | `{YYYYMMDD} {hh.mm.ss} iss0..m...`; day tie only | As-Run Test Matrix columns `Actual Date` and `Date on videos and images`. The meaning of the `iss035m` code is from memory, not opened. |
| FLEX (PSI-69) | test point in the name (`_ISS_{date}_{time} {testpoint}`) or at the end of the folder name; the folder's FLEX number is never used | `256R002_Readme.txt`. 163 names carry 2013-2014 test points; the table ends in 2011. |
| CFI (PSI-39) | CIR test point `F{ddd}{A-E}{nn}` against the table's `CIR` column | team reading, checked against the table (digits 2-4 equal the day of year in 86 of 87 rows). No ReadMe. |
| SAME-R, SLICE, SPICE | recording date and material; folder day ranges; `GMT{day}` | team reading, no document. Day ties only. |

**Checks of the ties so far** (all by AI sessions; no person has opened a tie):

1. Listing totals equal `raw_inventory.json` (2,623 files, 426,053,691,302 bytes).
2. A second script with a different method (plain substring search, `scripts/recount.py`) reproduces the name ties.
3. Two tables built separately by two AI sessions from the same PSI listing (the data role's `test_files.csv` in its commit `56d5afa`, and the scratch index) agree on 803 tests tied by the file name (`design/compare_data_role.py`, rerun in this step).
4. BASS-II: day and sample in the name agree with the tied row on 283 of 285 single ties that carry them.
5. This step: the link states were derived by separate code from the index's own columns (`final/video_final.py`); the totals by scope equal the names sheet (1,046 test, 3 run, 1,188 day, 26 several days, 360 none).

---

## 5. The ladder: how deep a video is read, what it yields, what it costs

| Tier | What is read | What it yields | Cost for all 2,623 videos | Done today for |
|---|---|---|---|---|
| 0. Name | file name, folder, size and file id in PSI's listing; no video byte | which test, run or day a video belongs to, by which labels; what the name says the clip is (second view, still sequence, portion during loss of signal, ignition attempt, stream recording, calibration, outreach); size; format by extension | 0 bytes of video; 30.6 MB for the 24 listings (measured) | all 2,623 (done in the scratch folder; today it moves into the repository) |
| 1. Container header | the first and, for some mp4 files, the last few hundred kilobytes, through `ffprobe` on PSI's signed address with range requests | duration, picture size, frame rate, container, codec. Not the recording date: the `creation_time` tag is the re-encode date in several sampled files. | measured on 37 videos: median 417,102 bytes and 3.86 s per video (mp4 0.33 MB, transport stream 1.32 MB). Estimates for all: 1.1 GB at the median, 2.7 GB weighted by name group, range 0.2 to 9.0 GB; about 3 to 6 hours one request at a time | 37 measured. With the lead's yes: the 49 files of the ISS flammability shortlist, about 25 MB (estimate) |
| 2. Three frames | frames at 10, 50 and 90% of the file (mp4 by time seek; transport streams by byte offset) | for the sampled file: what the picture shows and whether text is burned into it. Shown for other files of its name group only as "seen in 1 sampled file of this group" | measured: median 762,519 bytes and 6.1 s per frame; 2.43 MB and 18.8 s per video. Estimates for all: 6.4 GB at the median, 8.4 GB weighted, range 2.3 to 24 GB; about 13 hours one at a time | 22 sampled videos, 66 frames. No more today |
| 3. On-screen readings, transcribed | the text on the picture, one frame per second, by `video/read_overlay.py`; needs the whole clip | a table per clip: FUEL, AIR, FAN, RAD and the clock as shown. A transcription of NASA's display; not a measurement, not a NASA file | whole files. At most 457 files, 46.6 GB (the four investigations with the overlay in a sampled frame). BASS, SPICE and SLICE each need their own settings; BASS and SPICE a new reader state | 19 BASS-II clips (1,801,140,880 bytes on disk). No more today |
| 4. Measured from the picture | flame edge, flame size, droplet size, the second of an event | nothing today | not estimated; whole files at full frame rate, a person to label, and for most quantities the science-camera images that sit in archives, not in these videos | 0 videos; listed on the page only as "not derived" |

The header step works on every container met (37 of 37 `ffprobe` exits were 0: 30 mp4, 5 MPEG-TS, 1 MPEG-PS, 1 AVI). Seeking transport streams by time cost 5.7 to 9.8 MB per frame and was dropped; cutting by byte offset costs 0.67 to 1.88 MB and gave a keyframe each time. Signed addresses were valid for 3,599 s.

The sample: 37 files, one for each of 37 name groups as `video_sample.csv` lists them (33 distinct group names over 14 investigations; one sheet's summary says 34). Those groups hold 2,242 of the 2,623 files (333.2 GB). 381 files are in groups with no sampled file.

**What the sampled frames show** (described by an AI agent; three of them looked at again in this step, also by an AI agent; no person has checked a description):

- On-screen readings with date and clock: BASS-II (720x480), BASS (640x360), SLICE (720x480, text about 12 to 13 px lower, FUEL with three digits, a clock that jumps), SPICE (a 4:3 picture inside 1920x1080).
- No burned-in text in any sampled frame of the ACME recordings (PSI-10, 20, 21, 22, 23, 159), CFI, FLEX, SAME-R or SAME: 42 frames of apparatus, flames, droplets on fibres, a glowing coil, or black.
- A BASS-II `Still_Sequence` file is a video of the still camera's playback screen (camera text, not test readings).
- One ACME presentation video holds, in half of a split screen, a clip with the same kind of on-screen display dated 2012. It is an edited outreach video and is tied to no test.

**The reader on other layouts** (`vsample/readertest/`): on 3 SLICE frames it wrote no value; on BASS and SPICE frame sizes it refuses, and that refusal stops a whole batch (a five-clip run wrote no CSV). On two BASS-II clips outside the 19 (B13, T21) all 30 values equal the by-eye readings.

---

## 6. How video enters the adopted chain

No new page block, no new file family.

### 6.1 Chain rows (`question_chain.csv`, adopted step 2)

Location `video_on_screen_text`, one row per question that has counted BASS-II tests, in pile 2 ("In the archive, not in a table"):

- file group: "BASS-II main-view recordings" (135 files, 8,148,259,876 bytes: 114 whole recordings and 21 portions, attempts and excerpts);
- files opened: "19 of 135 transcribed";
- what was read: "NASA's on-screen readings, one row per second, 16,019 rows; a transcription";
- evidence in words: "the BASS-II ReadMe states fan voltage x10, duct flow speed and the radiometer are on the video display".

Variables whose form on video is "nothing" (pressure, oxygen, CO, CO2, CO to CO2 ratio, smoke particle size, aging time) get **no** video row. They get the fixed "cannot tell" sentence of 7.4 instead. This replaces the columns of `gap_states.csv` that pair every gap with every tied video.

### 6.2 File links (`file_links.csv`, `test_files.json`, adopted step 3)

One row per video of PSI-69, PSI-159, PSI-10 and PSI-25 (PSI-99 lists no video), with the adopted columns plus: `clip_kind_from_name`, `second_label_scope` (filled for a/b runs), `transcribed` (yes for 19 files). The rule and the fixtures are in sections 4 and 12.

### 6.3 Counts (`video_need_counts`, a view)

Per scenario, question and placement: counted tests; tests with a `two_labels_agree` video; with `one_label`; with `labels_disagree` only; without; files and bytes of the main-view recordings; files transcribed. Computed from `question_chain.csv` and `file_links.csv`, never by a second join. The catalog's independent recount (adopted step 7) reproduces it.

### 6.4 On the page

**(a) One pile-2 line per question**, filled by the build. Expected texts for the two demo environments:

- ISS, Flammability limit (P1): "Video (BASS-II). Of the 55 counted tests with oxygen inside this range (their pressure is not in NASA's table), 42 have a video of the test (file name and PSI folder name the same test), 4 are tied by the file name only (runs a and b of one sample), and 9 have no video file tied to them (the 8 Saffire-II tests: no video file in PSI's listing; BASS2-F2). Main-view recordings of these tests: 49 files, 3.52 GB (44 whole recordings, 5 portions recorded during loss of signal). On the screen, in NASA's words: fan voltage x10, duct flow speed in cm/s, an uncalibrated radiometer; also a date and a clock. Not on the screen: oxygen, pressure. Transcribed by the team: 7 of the 49. Not derived: no one has labelled ignition, flame-out or blowoff times in any video."
- ISS, Combustion products (D1): "Video (BASS-II). 44 of the 45 counted tests with oxygen inside this range have a video tied at test level (42 by two labels, 2 by the file name only). CO and CO2 are not on the screen of these videos; a video adds nothing to this question."
- ISS, Extinction conditions (S1): "Video. Of the 56 counted droplet tests inside the ranges (FLEX), 2 have a video of the test (2 files, 65.7 MB; no readings were seen in the sampled FLEX frames). 7 BASS-II tests have oxygen inside the range and no pressure in the table: 3 have a video of the test, 4 are tied by the file name only; the main-view recording of all 7 is transcribed. Not derived: the fan reading at the second a flame went out."
- ISS, Flame spread (P3): "Video. Neither of the 2 counted tests (Saffire-I) has a video file in PSI's listing."
- Lunar habitat, Extinction conditions (S1): "Video. None of the 17 counted droplet tests recorded inside these ranges has a video file tied to it. FLEX holds 183 video files (35.9 GB); 163 of them carry 2013-2014 test points that NASA's table (2009 to 2011) does not list; their atmosphere is not stated in any file opened; they are not counted for any environment. 8 of the 9 gas-flame tests inside the ranges (CFI-G) have a video of the test (8 files, 2.64 GB), but CFI-G counts for no question, and no readings were seen in the sampled CFI-G frames."
- Lunar habitat, P1 / D1 / P3: no video line. The adopted sentence stands ("This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of 14 November 2026)"); a video cannot move a test into the range.
- Ignition (P2), Smoke (D2): no counted test, so no video count. One fixed line for P2: "Not derived: the picture shows the igniter and the on-screen clock; no one has labelled ignition or flame-out times."

**(b) Video rows in the per-test file list** (the list the ui role builds in the adopted step 8). Per file: NASA's file name; bytes; the tie phrase for its link state; the clip kind from the name; for BASS-II main-view files "on-screen readings: transcribed (link)" or "on screen per NASA's ReadMe, not transcribed"; for a transcription link the warning of 7.1. Example, BASS2-O9: main view 61,078,814 bytes and second view 88,666,756 bytes, both "video of this test"; NASA's table text `Fan display`: "5   .36  .32 blowoff pt 4.0"; main view transcribed (594 rows, one row flagged `half_updated`); "Not derived: when the flame blew off and the flow at that moment". A FLEX test of the lunar set shows "no video file is tied to this test".

Statements made at tier 1 or 2 keep their level: "read from this file's header on (date)", "seen in this file", "seen in 1 sampled file of the same name group (1 of n files)", or "not looked at".

**(c) The shortlist file.** `final/shortlist_iss_P1_main_view.csv`: 49 rows (test, NASA file name, bytes, investigation, clip kind from the name, link state, labels, on the team's disk and transcribed, PSI file id). The page links to the PSI record and prints the exact file name; it does not link to a signed address (it expires after about an hour). Composition: 44 `two_labels_agree`, 4 `one_label` (P13a, P13b, P22a, P22b), 1 `labels_disagree` (the B3 file in folder B1); 7 on disk and transcribed (B21, P5, P13a, P13b, P22a, P22b, P25); 42 not on disk, 2,867,152,457 bytes, on 10 recording days by the name (8 of them not among the pilot's 7 days) and one file with no day in its name. The 5 portions: `...TEST_P5-LOS-portion.mp4`, `...TEST_M10_LOS_Portion_1754-1756.mp4`, `M10experimentvideo-LOS.mp4`, `...TEST_P18_LOS_Portion_10h52m52s_to_end_of_test.mp4`, `...TEST_P20_LOS_Portion_15h33m45s_to_end_of_test.ts.mp4`. Tests of the 47 with no main-view file: BASS2-F2 (no video) and BASS2-M3 (two other-camera clips only).

---

## 7. Fixed sentences and caveats, word for word

Each is a template in `pipeline/spec/answers.json` (request to data), keyed by location `video_on_screen_text` and variable. Each NASA quote names its file.

### 7.1 On every link to a transcription, and at the top of the transcription README

> These are values copied once per second from NASA's on-screen display by code an AI assistant wrote. They are not measurements and not NASA files. No row is labelled as ignition, flame-out or blowoff. The last value in a clip, or its largest value, is not the flow at any event; the flow at blowoff is only what NASA's table states (for O9: "blowoff pt 4.0").

Why: in `O9.csv` (594 rows) the clip ends at FAN 122, NASA's stated maximum; the smallest value is 40; the one flagged row (576 s) reads 198, above the possible maximum; NASA's table row for O9 reads `Fan display` = "5   .36  .32 blowoff pt 4.0". The page shows no minimum, maximum or last value of a transcribed column.

### 7.2 RAD

> RAD is copied once per second from a display NASA updates 5 times per second; it cannot show pre-extinction oscillations. It is uncalibrated, its gain was changed during tests (see the table's Radiometer gain column), and it rises with the igniter alone, so it is not a flame signal and not comparable between tests or across a gain change.

### 7.3 What the BASS-II screen shows, in NASA's words

From `PSI-25_Science Documents_BASS-II_ReadMe.docx`, section "Columns in test matrix" (read again in this step from the copy on the pilot disk):

- "Fan display:  instantaneous fan voltagex10 on the video display.  Maximum was 122, or 12.2 volts."
- "Air display:  flow speed measured in the duct in cm/s on the video display.  Response time is very slow (~ 1 min), so reading is only steady for long times at the same flow setting."
- "Radiometer gain:   Uncalibrated radiometer gain, radiometer is displayed on the video.   Adjusted to avoid saturation.  Useful for relative flame intensity readings and flame dynamics (like pre-extinction oscillations).  Video display data rate is 5 Hz."
- "Date:  actual date of experiment.  Video display is one day later than actual date due to a leap year the on-board computer did not account for." Shown for BASS-II only, with: "observed on 3 July 2014 clips; February 2014 clips not checked". No date is shifted by code.
- "Test number:   Initial of PI name followed by test number from the initial matrix.   If multiple runs with same sample on same day, a and b are used to designate."
- "Videos:   most test videos have the test number (PI initial+ # from test matrix)  In the Misc video folder, there are backup test recordings, recordings of crew operations, etc."

From NASA/TM-20210011385, section 1.2 (read by a research sheet, not in this step): "The video camera had an overlay that displayed the N2 flow rate (cm3/min), fan voltage (10× V), air velocity transducer reading (cm/s), and the radiometer signal."

FUEL is not interpreted. No document says what it shows; BASS frames show 495 to 496 and BASS-II clips -5 to 1.

For BASS, SLICE and SPICE the card says: "an on-screen display with the same field names was seen in 1 sampled file; no document was matched to its fields; not transcribed".

### 7.4 What a video cannot tell (fixed, per variable)

- Pressure, oxygen: "Not on the screen of any video sampled. For BASS-II the screen shows fan voltage, duct flow speed, a radiometer reading, a date and a clock (NASA's ReadMe)."
- CO, CO2, CO to CO2 ratio: "Not on the screen. NASA's table takes them from the CSA-CP and CDM sensor readings (ReadMe: 'CO2 readings:  CDM sensor readings.' 'CO readings:  CSA-CP sensor readings.')."
- Smoke particle size, aging time: "Not on the screen of any video sampled."
- AIR at an event: "The duct flow reading lags by about one minute (NASA's ReadMe); it is not the flow at the moment of an event."
- Any event time, burn duration, spread rate, flame size, flow at blowoff or extinction: "Not derived from video. An automatic brightness signal was tried and was right in at most 1 of 19 clips; it is not used."

### 7.5 "Could carry" sentences always start with "Not derived:"

- P1 and S1, flow at an event: "Not derived: the screen carries the fan reading every second; no one has labelled the second a flame went out or blew off, and a fan reading becomes a flow speed only through NASA's fan calibration for that day."
- P2: "Not derived: the picture shows the igniter and the on-screen clock; no one has labelled ignition or flame-out times."
- P3: "Not derived: a spread rate would need a person measuring the flame edge against a known scale; NASA's report publishes spread rates for 20 tests (NASA/TM-20210011385, Table 5.1)."

### 7.6 Other fixed marks

- Loss-of-signal clips: "portion recorded during loss of signal; part of this test's recording". ("Loss of signal" is the team's reading of `LOS`; no document opened.)
- Frame descriptions: "AI-labelled (Claude); not checked by a person."
- The outreach clip of PSI-20: "edited outreach video; contains a clip with an on-screen display dated 2012, before the ACME recording dates in this record; not tied to any test".
- The two-table check: "two tables built separately by two AI sessions from the same PSI listing agree on 803 tests".
- Saffire: "no video file is listed for this investigation in PSI's listing of 14 November 2026; archives were not opened".

---

## 8. Where AI is used, and how each use is checked

The only AI model in this work is Claude (Anthropic; that Anthropic is a US company is from memory, not opened). No vision-language or segmentation model was run on any frame, none is downloaded, and no model runs when the page loads. The methods sheet listed candidate open models and excluded those with a Chinese maker or base model by the Hugging Face `author` and `base_model` fields (`scripts/hfmeta_out.txt`); none is used.

| Use | What the AI does | Check |
|---|---|---|
| Name rules | An AI session wrote the regular expressions; code applies them, so the same listing gives the same ties | Checks 1 to 5 of section 4; the list of 10 disagreeing files; one person's sitting (10 video ties among 30 seeded links) |
| Meaning of a name part | An AI session proposes it | Shown as NASA's only with a quoted NASA sentence and its file; otherwise "team reading, no NASA document" (CFI, SAME-R, SLICE, SPICE; `LOS`, `udp`, `iss035m`) |
| Describing a sampled frame | An AI session looks at the frame and writes what it shows | Marked "AI-labelled (Claude); not checked by a person"; shown with the level "this file" or "1 sampled file of the group"; never a measurement or an event time. Three frames were looked at a second time in this step. |
| The overlay reader | An AI session wrote the code and labelled the character templates; no model at run time | Blind by-eye audits by AI agents (186 frames, about 750 values, none wrong); the clock self-check (15,487 of 16,019 rows within 1 s); byte-for-byte reproduction; control on two other clips (30 of 30); negative controls (nothing written on SLICE; BASS and SPICE refused). No person has checked a frame. The README's own rule (300 values per recording-day group) is not met: 380 values over 7 days. |
| Fixed sentences | An AI session drafted them from NASA documents | Each carries its quote; the data role's session compares each quote with the document; the lead reads them once |

No AI is used for sizes, durations, counts, transfer figures, the join to the tables, any ranking, or any flame event or measurement (none is produced).

---

## 9. Decisions for the team lead

The adopted design left one point open for this plan (its decision 7: "Does any new video reading go on today's path?"). Recommendation: **no new reading on today's path; one small optional read.**

| # | Question | Size | Why | Recommendation |
|---|---|---|---|---|
| 1 | Read the headers of the 49 files of the ISS flammability shortlist (range reads; no whole file)? | about 25 MB (estimate: 49 x 502,729 bytes of the one sampled BASS-II main-view file, plus 49 signed addresses of 8.3 kB); possible range 4 to 131 MB; about 4 minutes of requests; stops at 37.5 MB | the shortlist shows how long each recording is; the remote header is checked against the 7 clips on disk | yes, but only after steps 1 to 8 are done; skip if not started by 16:00 |
| 2 | Read the headers of all 298 videos tied to a counted test? | about 173 MB (estimate: one sampled file per name group, times the files of that kind, plus the signed addresses) | durations in every per-test file list | no today |
| 3 | Three frames for the 15 sampled videos that have a header only? | about 36 MB at the median, up to about 140 MB | would settle whether the BASS-II second view (102 files, 9.04 GB) carries the readings | no today: no page line needs it, and it needs a second labelling pass and a person |
| 4 | Headers of all 2,623 videos? | 1.1 to 2.7 GB (estimates; range 0.2 to 9.0 GB), 3 to 6 hours | total hours of video; durations everywhere | no today; a background job after submission |
| 5 | Download the 42 main-view clips of the ISS flammability tests that are not on disk, and transcribe them? | 2,867,152,457 bytes (2.87 GB), whole files | 49 of 49 shortlist files transcribed instead of 7 | no today: 8 new recording days, and the README's audit rule cannot be met in the time left; it adds no count |
| 6 | Store sample frames of NASA video in the repository? | 66 JPEG files, about 2.2 MB | pictures in the README | no: the frames are described in words; the licence field of PSI-10 is empty in `data/psi/manifest.json` (the other 13 say CC0-1.0) |

**Two reports the lead should hear.**

1. *Transfer of the design work.* From PSI: about 214 to 226 MB (names sheet 30.9 MB measured from saved responses; measuring sheet 130.95 MB measured plus 52 to 63 MB estimated for one stopped run). From public pages: about 148 MB of papers and model cards and 0.36 MB from NTRS. That is under 250 MB for PSI alone and about 362 to 374 MB if the cap covers every source. This final step: 0 bytes.
2. *One rule incident.* One research sheet ran `git fetch --dry-run` once in the read-only repository. No branch moved and the working tree is clean; objects of the data role's commit `56d5afa` may now be in `.git` while `origin/data-pipeline` still points to `449a5ef`. No action is needed unless the lead wants it undone.

Already settled by the adopted rule, so not asked again: files whose labels disagree are listed and tied to no test as "video of this test" (BASS2-B17 is held back).

---

## 10. Build plan, in the builder's order

Extra work on top of the adopted plan: pm about 2.1 h, data about 1.5 h, ui about 0.75 h, catalog about 0.25 h, the lead 0.2 h. Transfer on today's path: 0 bytes.

| # | Step | Role | Hours | Output | Check | Transfer | Lead first |
|---|---|---|---|---|---|---|---|
| 1 | Commit this design and the prototype | pm | 0.3 | `docs/video_design/design.md`; `docs/video_design/prototype/`: `video_index_names.csv`, `video_names.py`, `recount.py`, `video_final.py`, `video_final.json`, `video_links_states.csv`, `shortlist_iss_P1_main_view.csv`, `need_video_map.csv`, `video_sample.csv`. No frames. | sha256 of each committed copy equals the scratch file; each file says it is AI-generated | 0 | no |
| 2 | Decisions and the two reports of section 9 | team lead | 0.2 | answers in `coord/decisions.md` | recorded before step 10 starts | 0 | yes |
| 3 | Video ladder in `video/README.md`; the ISS shortlist as a file built by code; one slide line; rows in the two compliance logs | pm | 1.0 | README section "Which videos, how deep" with the ladder and the number of files reached per tier; `video/data/shortlist_iss_P1_main_view.csv`; slide line "426 GB of video; 49 files (3.5 GB) for this question; 7 transcribed" | every number equals a cell of `video_final.json`; a second session recomputes it; no "validated" without a named check | 0 | no |
| 4 | Fixed sentences of section 7 as templates | pm writes, data reviews | 0.75 + 0.25 | request to data for `pipeline/spec/answers.json`: sentences keyed by `video_on_screen_text` and variable, each with its quote and file | the data session compares each quote with the document; a variable whose form is "nothing" yields only a "cannot tell" sentence, never a video count | 0 | no |
| 5 | Video rows in the file links (inside the adopted step 3) | data | 0.75 | `file_links.csv` and `test_files.json` with kind = video for PSI-25, 69, 159, 10; columns `clip_kind_from_name`, `second_label_scope`, `transcribed`; version and file id from `listing_snapshot.json` | fixtures of section 12; "video of this test" only for `two_labels_agree`; the 10 disagreeing files listed, none resolved; video files and bytes per investigation equal `raw_inventory.json` | 0 | no |
| 6 | Chain rows and the counts view (inside the adopted step 2) | data | 0.5 | `question_chain.csv` rows with location `video_on_screen_text` ("19 of 135 transcribed"); the counts view per scenario, question and placement | counts equal the table of section 4 for `iss` and `lunar_habitat`; no video row for pressure, oxygen, CO, CO2, particle size | 0 | no |
| 7 | Independent recount of the video counts (inside the adopted step 7) | catalog | 0.25 | a block in `validation/raw_chain_recount.py` and its report | reproduces section 12 without importing the pipeline | 0 | no |
| 8 | Page (inside the adopted step 8) | ui | 0.75 | video rows in the per-test file list; the pile-2 video line per question; the lunar sentence generated from the chain; the warning of 7.1 beside every transcription link. Replaces the single pilot sentence now shown for PSI-25. No separate block. | the build fails when a number differs from its CSV cell; the banned-word scan; the phrase "video of this test" appears only for `two_labels_agree`; no minimum, maximum or last value of a transcribed column anywhere | 0 | no |
| 9 | One sitting of a person (the adopted step 11) | a team member with pm | within the adopted 1.0 | `reports/spot_check_raw.csv`: 30 seeded links, 10 of them video rows; the video sentences read once | a tie that fails is removed together with the other ties of its rule; reported as "10 video ties opened by a person"; if nobody comes the page says "recomputed by a second AI session; not read by a person" | 0 | no |
| 10 | Optional: headers of the 49 shortlist files | pm | 1.0 | `video/data/video_headers.csv`: duration, picture size, frame rate, container, codec, bytes read; script from `vsample/scripts/measure.py` with its counting proxy | for the 7 clips on disk the remote header equals `ffprobe` on the local file; exit code 0 or the file is listed as failed; transfer from the proxy counter; stop at 37.5 MB | about 25 MB (estimate) | yes |
| 11 | Optional cleanup, not needed today: the reader skips a clip of another frame size instead of stopping the batch | pm | 0.5 | `video/read_overlay.py` reports such a clip in `reading_manifest.json` and goes on; one unit test | existing tests pass; `--verify` on the 19 clips gives 0 differences | 0 | no |

**Order that always leaves something to show.**

- By about 3 h: steps 1 and 3 (pm alone). The repository holds the index of all 2,623 videos, the ladder with measured costs and the 49-file shortlist; the slide line is ready.
- By about 6 h: steps 4, 5, 6 and 8. The page shows video files under each test and one video line per question.
- By about 10 h, only with the lead's yes: step 10.

**Smallest version that still matters** (about 2 h, pm alone, 0 bytes): steps 1, 3 and 4. The page keeps its one existing PSI-25 video sentence and links to the README and the shortlist file.

**Fallback.** If step 5 or 8 is not merged and checked by late afternoon, ship the smallest version. No half-wired page block.

**Not built today.** A card or index page for all 2,623 videos; a separate video block; frame labels on the page; scene-cut detection; any vision-language model; any measurement from the picture; transcription of BASS, SLICE or SPICE.

---

## 11. Claims

### May be claimed (each with its numbers and source)

1. Every one of the 2,623 video files in PSI's combustion listings (426.05 GB, in 14 of the 24 investigations) is indexed by name and compared with NASA's test tables, without reading a video byte. The other 10 investigations list no file with a video extension; archives were not opened. (`video_index_names.csv`; `raw_inventory.json`)
2. 662 videos (152.3 GB) are tied to one test by two labels NASA wrote, the file name and the PSI folder name, for 463 of the 1,824 tests. 374 more are tied by one label, 10 have labels that disagree and are listed, 1,217 reach only a test day, 330 carry an identifier the table does not list, 30 carry none. (`final/video_final.json`)
3. Counted tests with a video of the test: Flammability limit 99 of 133 (18 more by the file name only), Combustion products 98 of 122 (16 more), Extinction conditions 19 of 298 (10 more), Flame spread 0 of 2. Ignition and Smoke have no counted test. Nearly all of these videos are BASS-II. (same)
4. For the ISS example, 42 of the 55 counted flammability tests with oxygen inside the range have a video of the test and 4 more are tied by the file name only; their main-view recordings are 49 files, 3.52 GB. For the lunar-habitat example, none of the 17 counted tests has a video tied to it; 8 of the 9 gas-flame tests inside the ranges have one, and they count for no question. (same; `final/shortlist_iss_P1_main_view.csv`)
5. In the files sampled (37 files, one per name group; three frames from each of 22), NASA's on-screen readings appear in BASS-II, BASS, SLICE and SPICE and in no sampled frame of the ACME, CFI, FLEX and SAME recordings. A sample result, described by an AI agent. (`video_sample.csv`)
6. NASA's on-screen readings are transcribed for 19 BASS-II clips, one row per second (16,019 rows); AI agents compared about 750 values with the picture and found none wrong; on layouts it was not set up for, the reader wrote no value in the three cases tried. (`video/README.md`; `vsample/readertest/`)
7. What the BASS-II screen shows, in NASA's words: fan voltage x10, duct flow speed with about one minute of response, an uncalibrated radiometer, a date one day later than the actual date; and that it shows no oxygen, pressure, CO or CO2. (BASS-II ReadMe; NASA/TM-20210011385 section 1.2)
8. The measured cost of looking deeper: about 0.4 MB per video for the header and about 0.8 MB per frame (37 and 66 measurements). For the whole archive that is an estimated 1 to 3 GB for headers and 6 to 8 GB for three frames per video, against 426 GB for a full download. Labelled as estimates from 37 files. (`video_sample.csv`; `vsample/scripts/stats.py`)

### May not be claimed

1. That the videos were analysed, watched or understood by AI. Names were parsed; 37 files were sampled; 19 clips were transcribed.
2. Any flame-out time, ignition delay, burn duration, spread rate, flame size or flow speed at blowoff or extinction from video. None was derived; the brightness signal failed and stays out.
3. That a video tied to a day is the video of a particular test; that a `one_label` tie is confirmed; that a disagreement was resolved. The run letter of an a/b run rests on the file name alone.
4. That a whole name group has or lacks on-screen readings. One file per group was looked at, and 381 files are in groups with no sampled file.
5. That the transcription is a measurement, a NASA data file, or checked by a person; that the last or largest value of a clip is the flow at an event; anything about the reader's accuracy beyond the 19 clips and the 30 control values.
6. That video closes a gap for pressure, oxygen, CO, CO2 or smoke particle size, or changes any count of the six questions. It changes none.
7. That the name rules for CFI, SAME-R, SLICE and SPICE are NASA's; that FUEL on the screen is the nitrogen flow; that the on-screen date offset holds outside BASS-II or outside the July 2014 clips observed; that the display inside the ACME outreach clip is an ACME reading.
8. The words "validated" or "verified" for ties, labels or readings without naming the check; any statement that a person checked something unless step 9 was done by a person.
9. The total hours of video in the archive (no full header pass was run); that Saffire has no video (only that no video file is listed); that the two tables that agree on 803 tests are independent evidence.
10. Any prediction for an untested condition or any safety verdict.

---

## 12. Fixtures for the checks

A second code path must reproduce these from the listing and the repository tables.

- Totals: 2,623 videos, 426,053,691,302 bytes. Scope: test 1,046 (238,966,365,726 bytes), run 3, day 1,188, several days 26, none 360.
- Link states: `two_labels_agree` 662 (152,320,655,239 bytes); `one_label` 374 (81,527,352,372); `labels_disagree` 10 (5,118,358,115); `day_only` 1,217 (102,112,670,418); `id_not_in_table` 330 (83,454,932,324); `none` 30 (1,519,722,834).
- Per investigation: the table of section 4. PSI-25: 244 / 47 / 5. PSI-159: 314 / 11 / 2 and 10 day only. PSI-39: 101 / 5 / 2, 20 day only, 118 not in table. PSI-69: 3 / 5 / 1, 163 not in table, 11 none. PSI-10: 306 one label, 11 day only.
- Tests by best state: 463 / 344 / 6 (sum 813). BASS-II: 101 / 20 / 2.
- Counted tests: P1 99 / 18 / 2 / 14; D1 98 / 16 / 2 / 6; S1 19 / 10 / 1 / 268; P3 0 / 0 / 0 / 2.
- ISS, P1, oxygen inside and pressure not in the table: 55 tests; 42 / 4 / 0 / 9. Shortlist: 49 files, 3,515,643,202 bytes, 45 tests; 44 whole recordings (3,406,968,026 bytes) and 5 portions (108,675,176 bytes); link states 44 / 4 / 1; 7 on disk; 42 not on disk, 2,867,152,457 bytes.
- Lunar habitat: 26 tests inside; 8 with a `two_labels_agree` video (8 files, 2,640,554,564 bytes), all CFI-G; 0 of the 17 counted S1 tests.
- BASS-II by clip kind from the name: whole main-view recordings 114 files (7,547,979,401 bytes, 114 tests); other main-view clips 21 (7 portions during loss of signal, 5 ignition attempts, 2 parts, 7 excerpts or other named clips; 600,280,475 bytes); second view 102 (9,044,985,674 bytes, 94 tests); still sequence 52 (450,216,042 bytes, 50 tests); rack, monitor or other camera 4; post-burn picture 3. Sum 296.
- BASS-II table: 14 pairs of day and sample belong to two tests each; 20 tests carry a run letter.
- `O9.csv`: 594 rows; FAN minimum 40, maximum 198 (the flagged row at 576 s), last 122. Table row O9, `Fan display`: "5   .36  .32 blowoff pt 4.0".
- sha256 of `tests.csv`, `need_tests.csv`, `scenario_needs.csv`, `scenario_tests.csv` unchanged (adopted check O6). The counts stay P1 133, P2 0, P3 2, S1 298, D1 122, D2 0.

---

## 13. Risks

1. **A statement about a name or a sample read as a fact about a file.** One wrong "video of this test" link is visible to any judge who clicks it. Guards: the phrase only for two agreeing labels; the level of every statement printed; the 10 disagreements listed; a person opens 10 video ties.
2. **A transcription read as a measurement.** Guards: the sentence of 7.1 on every link; no minimum, maximum or last value shown; "Not derived:" in front of everything a video could carry.
3. **Time.** This is extra page work on the submission day, beside three open page errors and the adopted plan. Guard: the smallest version needs only pm; the page block ships only if merged and checked by late afternoon.
4. **Transfer.** The design work is already at or above its cap. Guard: today's path is 0 bytes; the one optional read is 25 MB with a hard stop.
5. **The a/b runs.** 6 of the 19 transcribed clips (O8a, O8b, P13a, P13b, P22a, P22b) are tied by the file name only. Guard: the reason is printed; the lead may decide later that the letter in a NASA file name is enough.

---

## 14. Sources

**NASA documents and files.**

- BASS-II ReadMe, `PSI-25_Science Documents_BASS-II_ReadMe.docx` (PSI-25, doi 10.60555/4qc4-de67); read again in this step from `/Users/choidol/Desktop/NASA/video_pilot/raw_bass2/`.
- BASS-II experimental table, `data/psi/experimental_tables/PSI-25_Experimental table_BASS-II.csv` (read in this step); FLEX table `PSI-69_Experimental table_FLEX.csv` (read in this step).
- Olson et al., NASA/TM-20210011385, BASS-II Summary Report: https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf (read by the research sheets; saved text `dl_ntrs/bass2tm.txt`).
- ACME BRE Readme (`PSI-20_Science Documents_ACME_BRE_Readme.docx`), BASS As-Run Test Matrix (`PSI-26_Science Documents_As Run_Test Matrix.xlsx`), FLEX `PSI-69_Raw Data_256R002_Readme.txt`, PSI-10 `as run19137K1.txt`: read by the names sheet through one range read each (`transfer_log.jsonl`, `docs/`).
- PSI listing: POST https://psi.nasa.gov/geode-py/ws/files/v2 ; signed address: https://psi.nasa.gov/geode-py/ws/studies/PSI-<n>/download?file=<name>&version=<v>&redirect=false .

**Methods** (opened by the methods sheet, not in this step; saved copies under `papers/`).

- Stocker, "Recent Research on Flames of Gaseous Fuel Aboard the ISS", JASMAC 2021: https://ntrs.nasa.gov/api/citations/20210021781/downloads/JASMAC%20ACME%20paper%2020210921.pdf (one analog camera downlinked in near real time; science cameras separate).
- Dietrich et al., NASA/TP-2015-216046, Detailed Results From FLEX: https://ntrs.nasa.gov/api/citations/20150023456/downloads/20150023456.pdf
- Olson et al., Saffire IV/V spread rates (accepted manuscript): https://discovery.ucl.ac.uk/id/eprint/10164340/1/SIBAL-cotton%20revised%20Sept%20per%20review%20track%20changes%20accepted.pdf ; Klimek and Wright, Spotlight-8, NASA/TM-2006-214084: https://ntrs.nasa.gov/api/citations/20060011194/downloads/20060011194.pdf
- Thomsen et al., two-colour pyrometry: https://ntrs.nasa.gov/api/citations/20220012861/downloads/Volume_39_LaTeX_Template_Final_SFS.pdf
- Wright, MS thesis, Univ. of Maryland 2021 (BRE; flame height by hand in ImageJ, results from the OH* PMT): https://api.drum.lib.umd.edu/server/api/core/bitstreams/87c81c92-a4f9-4f44-a306-3ce3469f0e65/content
- Kim et al., Proc. Combust. Inst. 39 (2023) 1647-1656 (CFI-G): https://par.nsf.gov/servlets/purl/10426596
- Ma et al., NTRS 20140017780 (SLICE; the investigators read their overlay with OCR): https://ntrs.nasa.gov/api/citations/20140017780/downloads/20140017780.pdf
- NASA experiment summary, SPICE, NTRS 20090014827: https://ntrs.nasa.gov/api/citations/20090014827/downloads/20090014827.pdf
- Çetin et al., "Video fire detection: Review", Digital Signal Processing 23 (2013): https://repository.bilkent.edu.tr/bitstream/11693/38125/1/Video%20fire%20detection%20-%20Review.pdf
- PySceneDetect detectors: https://www.scenedetect.com/docs/latest/api/detectors.html ; TransNet V2: https://arxiv.org/abs/2008.04838 (considered, not used).
- Vision-language model reliability: https://arxiv.org/abs/2407.06581 , https://arxiv.org/abs/2405.08807 , https://arxiv.org/abs/2305.10355 (reason no such model is used).
- FFmpeg 9.0.1 (`ffprobe`, `ffmpeg`), range options from the local `ffmpeg -h protocol=https` output. The 188-byte transport packet behind the byte-offset cut is from memory, not opened.

**Repository files read in this step** (under `/Users/choidol/Desktop/NASA/NASA_RAPID/`): `docs/raw_data_design/design.md` and `prototype/chain_proto.py`; `coord/decisions.md`; `coord/status/pm.md`; `data/pipeline/tests.csv`, `need_tests.csv`, `scenario_tests.csv`; `data/psi/manifest.json`; `data/psi/experimental_tables/` (PSI-25, PSI-69, PSI-10, PSI-159); `video/README.md`; `video/data/team_transcription_bass2_onscreen_readings/README.md` and `O9.csv`.

---

## 15. Files of the video design (absolute paths)

- This design: `(scratch folder)/design_video.md`
- The Korean section for the lead's report: `(scratch folder)/video_section_ko.html`
- Final recount: `(scratch folder)/final/video_final.py`, `video_final.json`, `video_links_states.csv` (2,623 rows with scope, link state, labels), `shortlist_iss_P1_main_view.csv` (49 rows) in the same folder.
- Name index: `(scratch folder)/video_index_names.csv`, `video_index_summary.json`, `scripts/video_names.py`, `scripts/recount.py`.
- Sample of headers and frames: `(scratch folder)/video_sample.csv`, `frames/`, `vsample/` (scripts, logs, reader tests).
- Question-to-video map: `(scratch folder)/need_video_map.csv`.
- Earlier joins of this workflow: `(scratch folder)/design/` (`scenario_video.py`, `bass2_scope.py`, `compare_data_role.py`).
