# Video overlay reader

**What it is.** NASA's BASS-II videos (PSI-25) show five readings as text on the picture: FUEL, AIR, FAN, RAD and a clock. This tool copies those numbers into a table, one row per second, for 19 clips. It is a transcription of NASA's display. It is not a NASA data file and it measures nothing.

**Why.** As far as the PSI-25 files the team holds show, PSI has no numeric log of these readings.

**How far it was checked.** 186 frames (80 random, 106 hard cases), about 750 values, none wrong; from the random frames alone, fewer than about 1 value in 100 should be wrong. The frames were read by an AI assistant, not by a person. Checked on these 19 clips only.

**What it does not give.** No flame-out time, ignition time, burn duration or flow speed at blowoff or extinction. Our automatic flame signal from picture brightness failed its check (right in at most 1 of 19 clips) and was removed. Before using any number, read the ten caveats in [`data/team_transcription_bass2_onscreen_readings/README.md`](data/team_transcription_bass2_onscreen_readings/README.md).

**Made with AI.** Code, settings, tests and documents were written with an AI assistant (Claude) during the hackathon. The readings are transcribed by code that an AI assistant wrote; they are not a NASA data file and have not been reviewed by a person beyond the by-eye samples named under "How it was checked". "By eye" means that an AI assistant (Claude) looked at each frame image and wrote the numbers down before it saw the reader's values. No person has checked a frame.

Values are read from video only where PSI has no numeric file for them. NASA's ReadMe (`PSI-25_Science Documents_BASS-II_ReadMe.docx`) says fan voltage and duct flow are "on the video display" and that the radiometer is shown on the video. Oxygen, CO2, CO and the test settings are in NASA's experimental table and are not read from video.

## The command

```
python3 video/read_overlay.py --settings video/settings/bass2.json --clips <folder with the mp4 files> --out <folder>
```

It reads every clip named in the settings that is present in the clips folder (a file whose size differs from the settings is skipped and reported) and writes one CSV per clip plus `reading_manifest.json`. It exits non-zero when no clip of the settings was found in the clips folder. Reading all 19 clips (16,019 rows) took about 27 s on a 12-core laptop.

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
| `data/team_transcription_bass2_onscreen_readings/` | The 19 CSV files written by the command (the team's transcription, not PSI files), with their README (caveats, clip table, source). |

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
