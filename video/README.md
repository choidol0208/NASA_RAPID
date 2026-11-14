# Video

This folder holds the team's work on NASA's combustion videos in PSI. It does two things. First, `index_by_name.py` lists every one of the 2,623 video files in PSI's combustion listings (426.05 GB, in 14 of the 24 investigations) and ties each to a NASA test, a test day or nothing, by the identifiers NASA wrote into file and folder names, without reading a video byte; for a question and an environment it gives a short list of files instead of the whole archive. Second, `read_overlay.py` copies NASA's on-screen readings from 19 BASS-II clips (the "Video overlay reader" below). Code, settings, tests and documents were written with an AI assistant (Claude) during the hackathon. Checked by AI sessions; a person: none yet. A research exploration tool, not safety guidance; nothing here predicts an untested condition.

Three words used below:

- **Main view**: the test picture of the main camera. By the words in the file name: not a second view, not a still-camera sequence, not a post-burn picture, not a rack, monitor or other-camera clip. Portions recorded during loss of signal stay in.
- **Second view**: a file whose name says `2ND_VIEW`: a second camera view of the same test.
- **On-screen readings**: text that NASA's equipment wrote onto the picture. In BASS-II: FUEL, AIR, FAN, RAD, a date and a clock.

## The ladder: what a video tells at which cost

Pick an environment and a question; the shortlist file names the NASA files to open. ISS, flammability limit: 49 files, 3.52 GB of the 426 GB archive (7 of them transcribed). Lunar habitat: no counted test inside its ranges has a video, and the sentence written for the page says so (`docs/video_design/video_wording.md`, template `video_lunar_habitat_S1`).

| Tier | What you learn | Cost per video (measured) | All 2,623 (estimate) | Done so far |
|---|---|---|---|---|
| 0. Name | which test, run or day, by which labels; clip kind; size | 0 bytes of video | 0 bytes of video | all 2,623 |
| 1. Header | duration, picture size, codec; not the recording date | about 0.42 MB, 4 s | 1.1 to 2.7 GB (range 0.2 to 9.0) | 37 sampled files |
| 2. Three frames | what this one file shows, text burned in or not; never a statement about its group | about 2.4 MB, 19 s | 6.4 to 8.4 GB (range 2.3 to 24) | 22 sampled files |
| 3. Transcription | NASA's FAN, AIR, RAD and clock once per second; a copy of NASA's display, not a measurement, not a NASA data file | the whole file (about 95 MB per BASS-II clip) | not meant for all; at most 457 files, 46.6 GB | 19 BASS-II clips |
| 4. Measured from the picture | nothing | not estimated | not estimated | none; not derived |

The detailed table follows.

Do not process the videos. Index them by name, tie them to tests, and look deeper only where a question needs it. Each step down the ladder reads more of a file, costs more, and says more about fewer files. Every statement keeps the level it was made at.

### The five tiers

Costs were measured by the design job on a sample of 37 files (one for each of 37 name groups; headers of all 37, frames of 22) and 66 frames; the figures for all 2,623 videos are estimates from that sample (`docs/video_design/design.md` section 5, `docs/video_design/prototype/video_sample.csv`). Tiers 0 to 2 were done by the design job; this build redid tier 0 in `index_by_name.py`.

| Tier | What is read | What it yields | Measured cost per video | Estimated cost for all 2,623 | Done so far for |
|---|---|---|---|---|---|
| 0. Name | file name, folder, size and file id in PSI's listing; no video byte | which test, run or day a video belongs to, by which labels; what the name says the clip is (second view, still sequence, portion during loss of signal, ignition attempt, stream recording, calibration, outreach); size; format by extension | 0 bytes of video (the 24 listings were 30.6 MB, measured) | 0 bytes of video | all 2,623 (`index_by_name.py`) |
| 1. Container header | the first and, for some mp4 files, the last few hundred kilobytes, by `ffprobe` with range requests | duration, picture size, frame rate, container, codec. Not the recording date: the `creation_time` tag is the re-encode date in several sampled files | median 417,102 bytes and 3.86 s (37 videos) | 1.1 GB at the median, 2.7 GB weighted by name group; range 0.2 to 9.0 GB; about 3 to 6 hours one request at a time | 37 |
| 2. Three frames | frames at 10, 50 and 90% of the file | for the sampled file: what the picture shows and whether text is burned into it. For other files of its name group only "seen in 1 sampled file of this group" | median 762,519 bytes and 6.1 s per frame; 2.43 MB and 18.8 s per video | 6.4 GB at the median, 8.4 GB weighted; range 2.3 to 24 GB; about 13 hours one at a time | 22 videos, 66 frames |
| 3. On-screen readings, transcribed | the text on the picture, one frame per second, by `read_overlay.py`; needs the whole file | a table per clip: FUEL, AIR, FAN, RAD and the clock as shown. A copy of NASA's display, not a measurement and not a NASA data file | the whole file (the 19 clips hold 1,801,140,880 bytes, 94.8 MB per clip on average; reading all 19 took about 27 s) | not meant for all: at most the 457 files (46.6 GB) of the four investigations whose sampled frames show on-screen readings (BASS-II, BASS, SLICE, SPICE). BASS, SLICE and SPICE each need their own settings; BASS and SPICE a new reader state | 19 BASS-II clips |
| 4. Measured from the picture | flame edge, flame size, droplet size, the second of an event | nothing today | not estimated: whole files at full frame rate, a person to label, and for most quantities the science-camera images that sit in archives, not in these videos | not estimated | 0 |

In the sampled frames (three frames from each of 22 files; 15 more sampled files had their header read only), on-screen readings appear in BASS-II, BASS, SLICE and SPICE, and in no sampled frame of an ACME, CFI, FLEX, SAME-R or SAME recording. One ACME outreach video (PSI-20, Presentations) shows, in a split screen, a clip with such a display dated 2012; it is tied to no test and is not counted as readings on screen for PSI-20. That is a sample result, described by an AI agent: 15 of the 37 name groups sampled had no frame looked at, and 381 files are in groups with no sampled file. Nothing is said about a whole name group from its one sampled file.

### Tying a video to a test: the link states

Two labels count: the NASA identifier in the file name and the PSI folder name. For BASS-II the day and sample number in the name are compared with NASA's table as a check; a mismatch makes the link `labels_disagree`, a match adds no label, because in NASA's BASS-II table 14 pairs of day and sample belong to two tests each. The team never resolves a disagreement. The rules, each with the investigation it is for and its ground, are in `settings/name_rules.json`.

| Link state | Videos | Bytes | Phrase the page uses |
|---|---|---|---|
| `two_labels_agree` | 662 | 152,320,655,239 | "video of this test (file name and PSI folder name the same test)" |
| `one_label` | 374 | 81,527,352,372 | "tied by the file name only" or "tied by the folder name only"; for runs a and b of one sample: "tied by the file name only: the folder, the sample and the day name both runs of this sample" |
| `labels_disagree` | 10 | 5,118,358,115 | "tied by file name; folder or table disagrees", both labels printed (column `labels_values` of `data/video_links.csv`); the 10 files are listed |
| `day_only` | 1,217 | 102,112,670,418 | "a video of that test day (n tests that day; which one is not known)" |
| `id_not_in_table` | 330 | 83,454,932,324 | "carries an identifier that NASA's table does not list" |
| `none` | 30 | 1,519,722,834 | "not tied to a test" |

Sum: 2,623 videos, 426,053,691,302 bytes. 463 of the 1,824 test rows have at least one video of the test (two labels agree), 344 more are reached by one label at best and 6 by disagreeing labels only. Counted tests with a video of the test: flammability limit 99 of 133, combustion products 98 of 122, extinction conditions 19 of 298, flame spread 0 of 2; ignition and smoke have no counted test. Nearly all of these videos are BASS-II. Per investigation and per question: `data/video_links_summary.json`.

### What a user gets for a question

- **ISS, flammability limit.** 55 counted tests have oxygen inside the ISS range (their pressure is not in NASA's table). 42 have a video of the test, 4 are tied by the file name only (runs a and b of one sample), 9 have no video file tied to them. Their main-view recordings are 49 files for 45 tests, 3,515,643,202 bytes (3.52 GB), instead of 426 GB: 44 by two labels, 4 tied by the file name only (P13a, P13b, P22a, P22b), 1 whose labels disagree (the B3 file in folder B1, listed, not resolved; it is not a "video of this test"); 44 whole recordings and 5 portions recorded during loss of signal. The 9 tests with no video: the 8 Saffire-II tests (no video file in PSI's listing) and BASS2-F2. BASS2-M3 has a video tied to it but only other-camera clips, so no file of it is in the list. File: `data/shortlist_iss_P1_main_view.csv`. 7 of the 49 are transcribed; 42 (2,867,152,457 bytes) are not on the team's disk.
- **ISS, combustion products.** `data/shortlist_iss_D1_main_view.csv`: 47 files (44 by two labels, 2 tied by the file name only, 1 whose labels disagree, the same B3 file). CO and CO2 are not on the screen of these videos; NASA's table takes them from sensor readings; a video adds nothing to this question's values.
- **ISS, extinction conditions.** `data/shortlist_iss_S1_main_view.csv`: 10 files for 9 tests: 8 BASS-II (4 tied by the file name only; 7 transcribed) and 2 FLEX (no readings were seen in the sampled FLEX frames). Not derived: the fan reading at the second a flame went out.
- **Lunar habitat.** The sentence for the page, generated from the counts (template `video_lunar_habitat_S1` in `docs/video_design/video_wording.md`): "Video. None of the 17 counted droplet tests recorded inside these ranges has a video file tied to it. FLEX holds 183 video files (35.9 GB); 163 of them carry 2013-2014 test points that NASA's table (2009 to 2011) does not list; their atmosphere is not stated in any file opened; they are not counted for any environment. 8 of the 9 gas-flame tests inside the ranges (CFI-G) have a video of the test (8 files, 2.64 GB), but CFI-G counts for no question, and no readings were seen in the sampled CFI-G frames." No shortlist is written for the lunar habitat: no counted test inside its ranges has a video.

### The command

```
python3 video/index_by_name.py            # rebuild video/data/video_links.csv, video_links_summary.json and the shortlists
python3 video/index_by_name.py --verify   # rebuild in memory; exit 1 on any difference from the files on disk
python3 video/test_index_by_name.py       # unit tests on small made-up listings, and --verify on the shipped files
```

No network. Paths in this paragraph are relative to the repository root. Inputs: `video/data/psi_video_names_2026-11-14.csv` (PSI's file listing of 14 November 2026 as read into identifiers by the design job, copied from `docs/video_design/prototype/video_index_names.csv`), `data/pipeline/tests.csv`, `data/pipeline/need_tests.csv`, `data/pipeline/scenario_tests.csv`, and the 19 clip names in `video/settings/bass2.json`.

What the command reads again with the rules of `video/settings/name_rules.json`, stopping if any value differs from the saved reading (counts in `video/data/video_links_summary.json`, `checks`):

- the clip words of all 2,623 names;
- the name and folder labels of every investigation with a label rule (BASS-II, CFI, FLEX and the six ACME investigations), including the 163 FLEX 2013-2014 test points;
- the day key of every one of the 1,217 `day_only` videos (ACME, CFI, BASS, SAME-R, SLICE, SPICE) and the start time of every stream recording;
- so each of the 330 `id_not_in_table` videos has at least one identifier read again.

What it takes from the saved listing without reading it again: which table row an identifier points to (looked up by the design job in NASA's experimental tables, in columns such as CIR, FLEX Identifier, GMT and Sample # that `tests.csv` does not carry; the command checks that every test it names is a row of `tests.csv`), the BASS-II day-and-sample check against NASA's table, and the identifier parts listed under `identifier_keys_taken_from_saved_listing_without_reading_again` (for example the BASS `iss035m` code, SAME-R materials, SLICE DIMS numbers, SPICE ignition numbers). SAME (PSI-102) has no rule: its two clips carry no identifier.

Checks, all by AI sessions on 15 November 2026, run by `video/test_index_by_name.py`: the values read again, 0 differences; `tie_scope`, `link_state`, `test_id` and both label columns of all 2,623 rows equal the design job's separate recount (`docs/video_design/prototype/video_links_states.csv`), 0 differences; the fixtures of `docs/video_design/design.md` section 12 for totals, tie scopes, link states with bytes, link states per investigation, tests by best state (463 / 344 / 6; BASS-II 101 / 20 / 2), counted tests per question, the ISS flammability shortlist (49 files, 3,515,643,202 bytes, 45 tests; 44 / 4 / 1; 44 whole recordings and 5 portions; 7 transcribed), the lunar-habitat counts and the BASS-II clip kinds, all reproduced. A person: none yet.

### What is deliberately not done

Tier 4. Nothing is measured from the picture: no flame-out time, ignition delay, burn duration, spread rate, flame size or flow speed at blowoff or extinction. The one automatic signal tried, picture brightness as flame-out, was right in at most 1 of 19 clips and was removed. For ACME, the method papers the design read describe science cameras and sensors separate from the one camera whose video was sent down (`docs/video_design/design.md` section 14); for SLICE, the investigators read their own on-screen display (same section). Those papers were read by the design's research sheets, not in this build. Tiers 1 and 2 are not run for more files today; a header read of the 49 shortlist files (about 25 MB, an estimate) needs the team lead's yes.

### What may and may not be said

Shortened from `docs/video_design/design.md` section 11.

May be said, with its numbers and source:

1. All 2,623 video files (426.05 GB, 14 of 24 investigations) are indexed by name and compared with NASA's test tables, without reading a video byte. The other 10 investigations list no file with a video extension; archives were not opened.
2. 662 videos (152.3 GB) are tied to one test by two labels NASA wrote, the file name and the PSI folder name, for 463 of the 1,824 tests; 374 more by one label, 10 have labels that disagree and are listed, 1,217 reach only a test day, 330 carry an identifier the table does not list, 30 carry none.
3. The counted tests with a video of the test per question, as above.
4. ISS: 42 of the 55 counted flammability tests with oxygen inside the range have a video of the test, 4 more by the file name only; their main-view recordings are 49 files, 3.52 GB. Lunar habitat: none of the 17 counted tests has a video tied to it.
5. In the sampled frames (22 files, three frames each), on-screen readings appear in BASS-II, BASS, SLICE and SPICE only; a sample result, described by an AI agent.
6. NASA's on-screen readings are transcribed for 19 BASS-II clips (16,019 rows); AI agents compared about 750 values with the picture and found none wrong.
7. What the BASS-II screen shows, in the words of NASA's ReadMe; and that it shows no oxygen, pressure, CO or CO2.
8. The measured cost of looking deeper (tiers 1 and 2), labelled as estimates from 37 files.

May not be said:

1. That the videos were analysed, watched or understood by AI.
2. Any flame-out time, ignition delay, burn duration, spread rate, flame size or flow speed at an event from video.
3. That a video tied to a day is the video of a particular test; that a `one_label` tie is confirmed; that a disagreement was resolved.
4. That a whole name group has or lacks on-screen readings.
5. That a transcription is a measurement, a NASA data file or checked by a person; that the last or largest value of a clip is the flow at an event.
6. That video closes a gap for pressure, oxygen, CO, CO2 or smoke particle size, or changes any count of the six questions. It changes none.
7. That the name rules for CFI, SAME-R, SLICE and SPICE are NASA's; that FUEL is the nitrogen flow; that the on-screen date offset holds outside BASS-II or outside the July 2014 clips observed; that the display inside the ACME outreach clip is an ACME reading.
8. "Validated" or "verified" for ties, labels or readings without naming the check; that a person checked something.
9. The total hours of video in the archive; that Saffire has no video (only that no video file is listed); that the two tables that agree on 803 tests are independent evidence.
10. Any prediction for an untested condition or any safety verdict.

# Video overlay reader

**What it is.** NASA's BASS-II videos (PSI-25) show five readings as text on the picture: FUEL, AIR, FAN, RAD and a clock. This tool copies those numbers into a table, one row per second, for 19 clips. It is a transcription of NASA's display. It is not a NASA data file and it measures nothing.

**Why.** As far as the PSI-25 files the team holds show, PSI has no numeric log of these readings.

**How far it was checked.** 186 frames (80 random, 106 hard cases), about 750 values, none wrong; from the 380 random values alone (80 frames, so not independent draws), fewer than about 1 value in 100 should be wrong (95%). The frames were read by an AI assistant, not by a person. Checked on these 19 clips only.

**What it does not give.** No flame-out time, ignition time, burn duration or flow speed at blowoff or extinction. Our automatic flame signal from picture brightness failed its check (right in at most 1 of 19 clips) and was removed. Before using any number, read the ten caveats in [`data/team_transcription_bass2_onscreen_readings/README.md`](data/team_transcription_bass2_onscreen_readings/README.md).

> These are values copied once per second from NASA's on-screen display by code an AI assistant wrote. They are not measurements and not NASA files. No row is labelled as ignition, flame-out or blowoff. The last value in a clip, or its largest value, is not the flow at any event; the flow at blowoff is only what NASA's table states (for O9: "blowoff pt 4.0").

**Made with AI.** Code, settings, tests and documents were written with an AI assistant (Claude) during the hackathon. The readings are transcribed by code that an AI assistant wrote; they are not a NASA data file. Checked by AI sessions: an AI assistant (Claude) read 186 frames by eye before seeing the reader's values (see "How it was checked"). A person: none yet. "By eye" means that an AI assistant (Claude) looked at each frame image and wrote the numbers down before it saw the reader's values. No person has checked a frame.

Values are read from video only where PSI has no numeric file for them. NASA's ReadMe (`PSI-25_Science Documents_BASS-II_ReadMe.docx`) says fan voltage and duct flow are "on the video display" and that the radiometer is shown on the video. Oxygen, CO2, CO and the test settings are in NASA's experimental table and are not read from video.

## The command

```
python3 video/read_overlay.py --settings video/settings/bass2.json --clips <folder with the mp4 files> --out <folder>
```

It reads every clip named in the settings that is present in the clips folder (a file whose size differs from the settings is skipped and reported) and writes one CSV per clip plus `reading_manifest.json`. It exits non-zero when no clip of the settings was found in the clips folder. A clip whose frame size differs from the settings (another layout, such as BASS or SPICE) is skipped and listed under `clips_other_frame_size` in `reading_manifest.json`; the other clips are still read. Reading all 19 clips (16,019 rows) took about 27 s on a 12-core laptop.

- `--verify <folder>` reads again and compares with the CSV files there; exits 1 on any difference or when nothing could be compared.
- `--fetch` first downloads the clips named in the settings from NASA PSI into the clips folder (PSI's public listing and download service; sizes checked against the listing). `--fetch --dry-run` only asks PSI for its file listing and prints names and sizes; nothing is downloaded. The download path of `--fetch` has not been run from this package; only `--fetch --dry-run` was (PSI listed 695 files for PSI-25 and all 19 clips were found with the sizes and versions of the settings). The 19 clips used here were downloaded earlier by the pilot's script.
- `--list` prints the clips of the settings with their NASA table test.
- `--jobs N` sets how many clips are read in parallel.

"The pilot" in this folder means the team's first, exploratory reading of these 19 clips, which this package was cleaned up from.

Needs: Python 3 with NumPy, and `ffmpeg` and `ffprobe` on the PATH. Pillow is needed only for the tests and the fixture tool. Used here: Python 3.13.5, NumPy 2.1.3, Pillow 11.1.0, ffmpeg 9.0.1 (Homebrew build). SciPy and scikit-learn are not used by anything in this folder (scikit-learn and pandas were used once in the pilot to make the cluster files the reader state was derived from; see "Sources and licences"). Tests: `python3 video/test_read_overlay.py`.

## How it was checked

The evidence comes from the pilot reading and two separate review passes, all done with an AI assistant. "By eye" means that an AI assistant (Claude) looked at each frame image and wrote the numbers down before it saw the reader's values. No person has checked a frame.

1. The on-screen clock is a second check on the reader's digits and grid position: on the 15,487 of 16,019 rows where a clock was read it advances with video time to within 1 s in every clip; 3 rows are off the line. Each of the 3 was looked at and shows real screen content (O11 923 s and P22b 411 s are frames caught while the clock was changing; O11 0 s is a 2 s offset at the start of the clip). It does not check FUEL, AIR, FAN or RAD directly.
2. First review (random frames): 80 frames chosen at random, 380 readings compared by eye, 0 wrong. From the random sample alone, fewer than about 1 value in 100 should be wrong (95%). The 380 values come from 80 frames, so they are not 380 independent draws.
3. Second review (hard cases): 106 frames chosen as hard cases (FAN above 122, fan ramps, frames at or next to still-camera intervals, random frames, frames the reader had rejected), read by eye before the reader's values were opened: 376 readings agreed, 0 disagreed, 28 fields were left empty by the reader although they can be read. On all 23 sampled frames showing the still-camera screen, a blue screen, colour bars or black, and on 2 frames where the overlay is displaced, the reader gives no values. This review also re-ran the pilot code on three clips and got the same values (B21, P22a, O9; 1,010 rows, 0 differences).

Together: 186 frames, about 750 values compared, none wrong.

This package was then checked against the pilot. The code here, run with the one command on the 19 NASA clips, gives the same values as the checked pilot output on every row: 19 files, 16,019 rows, 96,114 values compared (overlay_present, FUEL, AIR, FAN, RAD and clock on every row), 0 differences. In 532 clock cells the pilot stored text that is not a time (six blanks in 473, text with ? in 59, such as `14413?`); these cells are empty here. `--verify` on the result: 16,019 rows, 0 differences. The flag rules mark exactly the three rows the second review named (O9 576 s, O11 923 s, P22b 411 s).

### What failed and was dropped

- The automatic flame-present signal from picture brightness. The first review found it right in 1 of 19 clips, and that one (O8a) is doubtful, so it counts as right in 0 or 1 of 19. It was removed: no image column and no ignition, flame-out or burn-duration time from the pilot is shipped.
- Timing flame-out by looking at sheets of frames was not reliable either (15 to 30 s off in 2 of 17 clips, too wide in 2, missing for 1). No flame timing of any kind is shipped.
- Not fixed: `overlay_present` is `False` on 7 rows where the overlay is on screen over a bright picture (B21 0, 163, 164 s; O8a 80, 81 s; O19 988 s; P5 1608 s). This loses values there; it does not produce wrong ones.

## Limits

Shortened from the second review's list of what cannot be claimed.

### About the columns

- AIR 0 does not mean still air, and an AIR value read during or within a few minutes after a fan change is not the flow at that moment (NASA: response time about 1 minute).
- RAD as transcribed here must not be used as a measure of flame intensity, heat flux or radiative loss, and RAD levels cannot be compared between tests or across a gain change. NASA's ReadMe calls the radiometer uncalibrated and useful for relative readings; this file has one decimal, cut not rounded, once per second; the reading saturates at 4.1 and responds to the igniter and to the hot sample after the flame is gone. RAD above its pre-ignition level does not mean a flame is present (O12 never ignited and reads up to 1.8).
- A cm/s number derived from FAN through NASA's calibration file is a calibration estimate, not a measurement: day and restrictor specific, off by about 30% where it could be tested, with no same-day calibration for P1 and only one point for B21.

### Not derived from this file

- No blowoff or extinction (quenching) velocity in cm/s: at blowoff the flow was changing and unmeasured; at extinction it was below what the display and NASA's calibration resolve.
- No flame-out time, ignition time or burn duration, whether from picture brightness, by-eye windows or RAD. None is validated.
- Not the oxygen level at the moment of flame-out: the table gives only initial and final O2 per test, and two table entries cannot be right as oxygen percentages (P22a final O2 0.6; P22b final O2 39.1); they are flagged, not used.
- Not a flammability limit found, confirmed or improved: NASA's team published that analysis from their own records (Olson and Ferkul, Combustion and Flame 180, 2017, listed in the NASA ReadMe).
- Nothing about the other 277 clips of PSI-25, or about the reader's accuracy on them.
- This is not NASA data or a NASA log. It is the team's transcription of NASA's display.

## Contents

| Path | What |
|---|---|
| `read_overlay.py` | The one command. Common reading code. BASS-II specifics are in the settings; the code assumes one fixed-pitch text grid, one frame size and a six-digit HHMMSS clock. |
| `settings/bass2.json` | Everything specific to BASS-II: PSI accession and DOI, the 19 clips with their NASA table test and recording day, frame sampling, overlay strip and character grid, the fields with their cells, pixel boxes, formats and a short phrase from NASA's ReadMe, the rule for a missing overlay, the clock check, the flag rules, the disclosure sentence written into the manifest, and the reader state with its SHA-256. |
| `reader_state/bass2_reader_state.npz` | Frozen reader state (38,637 bytes): 33 normalised 14 x 22 pixel character templates, each with its character, and the grid origin x0 of each clip. No training sample. |
| `tools/export_reader_state.py` | Built the reader state from the pilot's labelled clusters. Run once, on 2026-11-14. |
| `tools/make_fixtures.py` | Cut the test fixtures from the clips. Run once. |
| `test_read_overlay.py`, `fixtures/` | Unit tests that run without the videos, on six overlay strips (text strip only) cut from the clips. |
| `data/team_transcription_bass2_onscreen_readings/` | The 19 CSV files written by the command (the team's transcription, not PSI files), with their README (caveats, clip table, source). These are values copied once per second from NASA's on-screen display by code an AI assistant wrote. They are not measurements and not NASA files. No row is labelled as ignition, flame-out or blowoff. The last value in a clip, or its largest value, is not the flow at any event; the flow at blowoff is only what NASA's table states (for O9: "blowoff pt 4.0"). |
| `index_by_name.py` | The name index: one command, no network, that rebuilds the video link tables and shortlists from the saved PSI listing and the team's test tables; `--verify` compares with the files on disk. |
| `settings/name_rules.json` | Every rule `index_by_name.py` uses: how a name and a folder are read per investigation, the day keys, what each part means and its ground, the clip words and kinds, the link states and their phrases, the placement rule. |
| `test_index_by_name.py` | Unit tests of the name index on small made-up listings, and `--verify` on the shipped files. |
| `data/psi_video_names_2026-11-14.csv` | PSI's file listing of 14 November 2026 as read into identifiers (2,623 videos), with its provenance line. |
| `data/video_links.csv`, `data/video_links_summary.json`, `data/shortlist_*.csv` | Written by `index_by_name.py`: one row per video with its link state (and, where labels disagree, both labels in `labels_values`); totals, counts and the checks of the command; one shortlist per demo scenario and question that has videos. |

## How the reading works

ffmpeg decodes each clip with its fps=2 filter and every second frame is kept, which gives one frame per second and is the frame choice of the checked pilot; only the overlay strip (frame rows 30-85, columns 140-719) is turned to gray, and nothing else of the picture is read.
The overlay is a fixed-pitch character grid (28.65 px), and the grid origin of each clip was measured once from the clip-averaged header line FUEL AIR FAN RAD and is frozen in the reader state.
Each character cell of a field (14 x 22 px) is normalised and correlated with the 33 frozen templates, each labelled with its character, at every shift of up to 1 px in x and y.
A character is accepted only when its best correlation is at least 0.80 and beats every other character by at least 0.05; otherwise the cell counts as blank when it is dark compared with the header text, or as unreadable.
A value is written only when every cell of the field was read and the text fits the field's format (for example two or three digits for FAN, d.d for RAD, a valid HHMMSS for the clock); otherwise the cell stays empty, and nothing is interpolated or filled in.
Last, the clock self-check compares the on-screen clock with video time, and the flag rules of the settings mark frames caught while the display was changing (`half_updated`) without changing any value.

## For another experiment

Not tried on any other experiment. The design intends that another experiment with the same kind of overlay needs a new settings file and a new reader state, not new reading code; building the reader state needs a grouping step that is not in this package, and an overlay without a clock is not supported yet. The BASS-II reader state will not read another font. The steps:

1. Check that the values are needed from video: PSI has no numeric file for them. Values PSI holds as numbers are taken from PSI, not from video.
2. Describe the overlay in a settings file, `settings/<experiment>.json`, with the same keys as `bass2.json`: the clips (PSI file names, versions, sizes, NASA table test, recording day), video size, frame sampling, the overlay strip, the character grid (pitch, cell size, text lines), each field with its cells, format and a short phrase from the experiment's documents with the file name plus a paraphrase, the overlay-present rule, the clock check, the flag rules and the disclosure sentence for the manifest (naming the by-eye samples of that experiment). Write the columns list. Measure the grid by hand on a clip-averaged frame: the pitch (distance from one character to the next on a text line), the cell size of one character, the top row of each text line, and a search range for the origin around the first character of the header line. The pilot's own measuring step is not in this package.
3. Build the reader state from that experiment's own frames. Cut character cells from a random sample of frames of every recording day, group them (the pilot used k-means clustering) and label each group by eye from a montage of its members; write the groups as `.npz` files with `labels` and `raw` (the cell images) and the grid origin per clip as JSON. That grouping step is not part of this package. Put the labels into `reader_state.build` of the settings, run `tools/export_reader_state.py` once, and copy the SHA-256 it prints into `reader_state.sha256`. Never re-group after labelling: group numbers change and the labels would silently point at the wrong characters.
4. Run a blind by-eye audit with a pass rule written down beforehand: for example 0 wrong in at least 300 random values per recording-day group, plus every value above the nominal maximum, read by eye before the reader's values are opened. Wrong means the reader wrote a value that differs from the picture; a cell the reader left empty although a person can read it is lost data and is counted separately. Draw frames with a fixed random seed over all rows of a recording day, cut numbered overlay crops without the reader's values, write the readings down, and only then open the reader's values. If the rule fails: publish nothing, find the character or field that failed, rebuild the reader state from new groups with a new checksum, and audit again on newly drawn frames. Honest note: the 19 BASS-II clips were checked on 380 random values over 7 recording days in total, which is less than this rule asks per day. The scripts the pilot used to draw the audit sheets and to group the cells are not in this package.
5. Check `rows_clock_off_line` in `reading_manifest.json` by hand; the command does not reject a clip by itself. Decide beforehand how many off-line rows reject a clip.
6. Cut a few fixtures with `tools/make_fixtures.py`, add tests for them, and run `--verify` on the output.

## When PSI adds data (design only, not built)

A watcher would, on a schedule, ask PSI for the file listing of each accession that has a settings file (the same listing call `--fetch --dry-run` makes) and compare names, sizes and versions with the last saved listing. It would report new clips and changed versions; it would not download or read anything on its own. A person would map each new clip to its NASA table row and add it to the settings. Then `--fetch` and the one command would read it, a clock gate (not built; today the command only counts off-line rows in `reading_manifest.json`) would reject a clip whose clock does not advance one second per second, and a clip from a recording day not yet audited would wait for a blind by-eye audit under the written pass rule. A changed version of a clip already read would mark its CSV as stale until it is read and audited again. If a new listing shows a numeric file for fan voltage, flow or radiometer, the watcher would report it, and the video transcription would stop being the record and become a cross-check of that file. None of this exists yet.

## Sources and licences

- NASA PSI investigation PSI-25 (BASS-II), DOI [10.60555/4qc4-de67](https://doi.org/10.60555/4qc4-de67), CC0-1.0 as given in PSI's investigation record: 19 mp4 clips (named in the data README and in `settings/bass2.json`), `PSI-25_Science Documents_BASS-II_ReadMe.docx`, `PSI-25_Experimental table_BASS-II.csv`; six fixture strips in `fixtures/` cut from the clips. File listing and download through PSI's public service (`https://psi.nasa.gov/geode-py/ws`).
- FFmpeg 9.0.1, Homebrew build configured with `--enable-gpl --enable-version3`, so GPL-3.0-or-later as built; called as a separate program, no FFmpeg code is in the repository.
- NumPy 2.1.3, BSD-3-Clause.
- Pillow 11.1.0, MIT-CMU (tests and fixture tool only).
- Python 3.13.5, PSF-2.0.
- Pilot step that made the cluster files (not shipped): scikit-learn 1.6.1 KMeans, BSD-3-Clause; pandas 2.2.3, BSD-3-Clause.

Before `video/` is pushed or linked, the pm appends matching lines to `compliance/SOURCES.md` and one line to `compliance/AI_USAGE_LOG.md` (append only).
