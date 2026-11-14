# NASA's on-screen readings from BASS-II video (PSI-25), transcribed by the team: 19 clips, one row per second

These are values copied once per second from NASA's on-screen display by code an AI assistant wrote. They are not measurements and not NASA files. No row is labelled as ignition, flame-out or blowoff. The last value in a clip, or its largest value, is not the flow at any event; the flow at blowoff is only what NASA's table states (for O9: "blowoff pt 4.0").

Source: the text overlay in NASA's own BASS-II videos (FUEL, AIR, FAN, RAD, clock). The team read the numbers off the picture with a fixed-font template reader. This is a transcription of NASA's display. It is not a NASA data file, and it contains no team measurement.

**Disclosure.** Transcribed by code that an AI assistant (Claude) wrote; not a NASA data file. Checked by AI sessions: an AI assistant (Claude) read 186 frames by eye before seeing the reader's values (80 random frames and 106 frames chosen as hard cases, in the pilot's two review passes; see "How it was checked" in `video/README.md`). A person: none yet. The files were written by `video/read_overlay.py` (see `video/README.md`).

"By eye" means that an AI assistant (Claude) looked at each frame image and wrote the numbers down before it saw the reader's values. No person has checked a frame.

## Caveats

1. Covers 19 clips only: B21, M17, O4, O7, O8a, O8b, O9, O11, O12, O14, O19, P1, P5, P9, P13a, P13b, P22a, P22b, P25. Not checked on any other clip.
2. Checked by eye on 186 frames (80 random, 106 chosen as hard cases): about 750 values compared, none wrong. From the 380 random values alone (80 frames, so not independent draws), fewer than about 1 value in 100 should be wrong (95%).
3. An empty cell means not read. It never means zero, and nothing is filled in. Cells are empty when the reader was unsure, when the picture behind the text is bright, or when NASA's feed shows the still-camera screen, a blue screen or colour bars instead of the experiment (O14 957-975 s, O19 533-651 s, P22b 422-450 s, P5 895-996 s, P9 796 s to the end).
4. One value per second. NASA states the display refreshes at 5 Hz, so faster changes are not in this file.
5. FAN is fan voltage x 10 (NASA ReadMe; nominal maximum 122). The screen itself shows 123 to 125 in 16 rows. Rows flagged half_updated show a frame caught while the display was changing (O9 at 576 s reads 198, between 98 and 102; two clock values). The same can happen unnoticed in any field while its value is changing.
6. AIR is NASA's duct flow reading in cm/s. NASA states its response time is about 1 minute. Read it only where FAN has been steady for several minutes; during and just after a fan change it lags far behind. At the lowest fan settings it reads 0, which means below what it can show, not proven still air.
7. RAD is NASA's radiometer reading, which NASA describes as uncalibrated. The screen shows two decimals; the last one is cut off by the edge of the picture, so this file gives one decimal, cut not rounded (0.99 appears as 0.9). 4.1 means saturated (988 rows, 828 of them in P5). In M17, P5 and P22a the crew changed the gain during the test and the reading jumps about five-fold with no change in the flame (M17: 4.1 to 1.0 at 421 s, 0.5 to 2.4 at 1325 s). Do not compare RAD between tests or across such a jump. RAD also rises with the igniter alone (O12 never ignited and reads up to 1.8).
8. FUEL is copied as shown. The NASA documents we hold do not say what it measures in these solid-fuel tests.
9. t_video_s is seconds from the start of the clip. clock_hhmmss is the on-screen clock (GMT). NASA's ReadMe: "Video display is one day later than actual date due to a leap year the on-board computer did not account for." Observed on 3 July 2014 clips; February 2014 clips not checked. No date is shifted by code.
10. Not in this file: when the flame was present or went out, flow speed at blowoff or extinction, calibrated radiation. Our automatic flame signal from picture brightness failed its check and was removed.

## Files

One CSV per clip (`B21.csv` ... `P25.csv`), 16,019 rows in all, plus `reading_manifest.json`. Every CSV here is the team's transcription of NASA's display, not a PSI file; if a CSV is offered for download on its own, name it as a team transcription, never as PSI data. The manifest names the settings file and reader state with their SHA-256, the ffmpeg, NumPy and Python versions, and per clip the rows, the grid origin used, the rows without overlay, the rows whose clock is off the line, and the flagged rows. `rows_all_values` in the manifest counts rows with FUEL, AIR, FAN, RAD and the clock (15,279); the table below counts the four values without the clock (15,292).

| Column | Meaning |
|---|---|
| `t_video_s` | Seconds from the start of the clip (one frame per second; see `video/settings/bass2.json`, `sampling`). |
| `clock_hhmmss` | On-screen clock as six digits HHMMSS (GMT), written only when all six digits were read and form a valid time. |
| `overlay_present` | `True` when the header line FUEL AIR FAN RAD is clearly brighter than the gaps between its words. It is `False` on 7 rows where the overlay is on screen over a bright picture (B21 0, 163, 164 s; O8a 80, 81 s; O19 988 s; P5 1608 s) and on 2 rows at P22b 378-379 s where the overlay is displaced for two frames while the feed glitches (no values there); values that passed their own character test are kept. |
| `FUEL` | As shown. |
| `AIR_cm_s` | As shown (NASA: duct flow speed, cm/s). |
| `FAN_display` | As shown (NASA: fan voltage x 10). |
| `RAD_trunc1` | First three characters of the radiometer display (d.d), cut not rounded. |
| `flag` | `half_updated` where a rule of the settings says the frame was caught while the display was changing: FAN above 125 (O9 576 s), or a clock off the line between two rows on the line (O11 923 s, P22b 411 s). The value is kept as shown. Empty otherwise. |

Coverage: 15,292 of the 16,019 rows have all four of FUEL, AIR, FAN and RAD. 524 rows are marked overlay_present False: 515 in the intervals of caveat 3, 7 with the overlay on screen over a bright picture, and 2 at P22b 378-379 s where the overlay is displaced for two frames. O11 at 0 s shows a clock 2 s off the line of the rest of the clip; it is real screen content at the start of the clip and is not flagged.

## Clips and NASA table tests

"NASA table" is NASA's PSI-25 experimental table (`PSI-25_Experimental table_BASS-II.csv`). Its Fan display and Air display text is copied with runs of spaces collapsed. The outcome column is the team's reading of that text, not a NASA column.

| Clip | NASA table test | GMT day (date) | NASA table: Fan display | NASA table: Air display | Outcome (team reading of the table) | Rows | Rows with FUEL, AIR, FAN, RAD | Rows without overlay |
|---|---|---|---|---|---|---|---|---|
| B21 | B21 | 216 (2014-08-04) | 53 and down | 5 down to ext | extinction | 167 | 161 | 3 |
| M17 | M17 | 196 (2014-07-15) | Fan pot 3.7 1.7 1.5 1.3 0.8 0.6 0.5 0.3ext | 10 5 3 0ext | extinction | 1889 | 1888 | 0 |
| O4 | O4 | 189 (2014-07-08) | 5 0.7 0.5 0.4 0.36 ext | 5 down to ext | extinction | 1228 | 1217 | 0 |
| O7 | O7 | 177 (2014-06-26) | 5 .36 .32 ..305 blowoff fan max 10 | (empty) | blowoff | 862 | 860 | 0 |
| O8a | O8a | 177 (2014-06-26) | 5 .36 .32 .31 extinguished | (empty) | extinction | 531 | 526 | 2 |
| O8b | O8b | 177 (2014-06-26) | 5 .36 .32 .31 blowoff fan pot 6.0 | (empty) | blowoff | 538 | 538 | 0 |
| O9 | O9 | 177 (2014-06-26) | 5 .36 .32 blowoff pt 4.0 | (empty) | blowoff | 594 | 594 | 0 |
| O11 | O11 | 189 (2014-07-08) | ign 5 0.36 0.32 0.31 0.305 blowoff 6.0 | 5 down then blowoff | blowoff | 1034 | 1031 | 0 |
| O12 | O12 | 189 (2014-07-08) | pots 1.4 3 0.9 0.7 | no ign at any flow | no_ignition | 521 | 521 | 0 |
| O14 | O14 | 213 (2014-08-01) | 52 and down | 5 down to ext | extinction | 986 | 966 | 19 |
| O19 | O19 | 213 (2014-08-01) | 52 and down | 5 down to ext | extinction | 1032 | 904 | 120 |
| P1 | P1 | 167 (2014-06-16) | (empty) | 5 2 slow decr to ext | extinction | 381 | 369 | 0 |
| P5 | P5 | 195 (2014-07-14) | Fan pot 1.5 (5cm/s) 0.9 0.4 0.36 0.32 0.308 0.3 0.29 0.28 0 ext | 5 down to ext | extinction | 1610 | 1471 | 103 |
| P9 | P9 | 195 (2014-07-14) | Fan pot 1.5 (5cm/s) 0.9 0.4 0.36 0.32 0.3 0.28 ext | 5 down to ext | extinction | 1042 | 754 | 246 |
| P13a | P13a | 195 (2014-07-14) | Fan pot 1.1 (5cm/s) 0.4 0.36 0.32 0.3 0.28 0.26 0 ext | 5 down to ext | extinction | 1433 | 1408 | 0 |
| P13b | P13b | 195 (2014-07-14) | Fan pot 1.3 (5cm/s) 0.4 0.36 0.32 ext | 5 down to ext | extinction | 467 | 448 | 0 |
| P22a | P22a | 189 (2014-07-08) | 5 0.36 0.32 ext after some time | 5 down to ext | extinction | 249 | 233 | 0 |
| P22b | P22b | 189 (2014-07-08) | 5 p.36 0.34 0.33 0.32 0.31 ext | 5 down to ext | extinction | 619 | 579 | 31 |
| P25 | P25 | 189 (2014-07-08) | 5 p.36 0.34 0.33 0.32 0.31 ext | 5 down to ext | extinction | 836 | 824 | 0 |

## Source

- NASA Physical Sciences Informatics (PSI), investigation PSI-25, BASS-II (Burning and Suppression of Solids - II), DOI [10.60555/4qc4-de67](https://doi.org/10.60555/4qc4-de67), licence CC0-1.0 (as given in PSI's investigation record, saved in `data/psi/manifest.json`).
- The 19 NASA video files read, all PSI file version 2, as named in PSI's file listing:
  `PSI-25_Raw Data_BASS_GMT216_SAMPLE_174_TEST_B21.mp4`, `PSI-25_Raw Data_BASS_GMT196_SAMPLE_166_TEST_M17.mp4`, `PSI-25_Raw Data_BASS_GMT189_SAMPLE_216_TEST_O4.mp4`, `PSI-25_Raw Data_BASS_GMT177_SAMPLE_214_TEST_O7.mp4`, `PSI-25_Raw Data_BASS_GMT177_SAMPLE_208_TEST_O8a.mp4`, `PSI-25_Raw Data_BASS_GMT177_SAMPLE_208_TEST_O8b.mp4`, `PSI-25_Raw Data_BASS_GMT177_SAMPLE_209_TEST_O9.mp4`, `PSI-25_Raw Data_BASS_GMT189_SAMPLE_184_TEST_O11.mp4`, `PSI-25_Raw Data_BASS_GMT189_SAMPLE_217_TEST_O12.mp4`, `PSI-25_Raw Data_BASS_GMT213_SAMPLE_183_TEST_O14.mp4`, `PSI-25_Raw Data_BASS_GMT213_SAMPLE_213_TEST_O19.mp4`, `PSI-25_Raw Data_BASS_GMT167_SAMPLE_185_TEST_P1.mp4`, `PSI-25_Raw Data_BASS_GMT195_SAMPLE_202_TEST_P5.mp4`, `PSI-25_Raw Data_BASS_GMT195_SAMPLE_202_TEST_P9.mp4`, `PSI-25_Raw Data_BASS_GMT195_SAMPLE_203_TEST_P13a.mp4`, `PSI-25_Raw Data_BASS_GMT195_SAMPLE_203_TEST_P13b.mp4`, `PSI-25_Raw Data_BASS_GMT189_SAMPLE_200_TEST_P22a.mp4`, `PSI-25_Raw Data_BASS_GMT189_SAMPLE_200_TEST_P22b.mp4`, `PSI-25_Raw Data_BASS_GMT189_SAMPLE_217_TEST_P25.mp4`.
- NASA documents: `PSI-25_Science Documents_BASS-II_ReadMe.docx` (what each display field is) and `PSI-25_Experimental table_BASS-II.csv` (test numbers, dates and the table text above).
- As far as the PSI-25 files the team holds show, PSI has no numeric log of the fan voltage, duct flow and radiometer readings; the NASA ReadMe says they are on the video display. That is why these values are read from video. Values that PSI does hold as numbers (oxygen, CO2, CO and the test settings in the experimental table) are not read from video.
