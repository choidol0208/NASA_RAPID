# Fixed sentences for video, as templates

*AI-generated (Claude Code, pm role) on 15 November 2026, build step 4 of `docs/video_design/design.md`. Checked by AI sessions; a person: none yet. For the data role's answers file (`pipeline/spec/answers.json`, keyed by location `video_on_screen_text` and variable); the data session compares each NASA quotation with its document before it adopts a template.*

Every template below is a JSON block that code can load as it is. Fields:

- `id`: the key; `keyed_by`: what selects the template (variable, question or link state).
- `template`: the sentence. A slot is written `{name}`; text outside slots is fixed and must not be changed.
- `slots`: for each slot, where its value comes from. Files are under the repository root; `summary` means `video/data/video_links_summary.json`, written by `video/index_by_name.py`.
- `ground`: where the sentence comes from. `quotes`: NASA's words used in it, each with its file and place.
- `example`: the template filled with today's values.

Rules for all templates, from the design and the team lead's wording decisions:

1. "video of this test" only for the link state `two_labels_agree`.
2. A transcription is a copy of NASA's display, not a measurement and not a NASA data file.
3. No flame-out time, ignition delay, burn duration, spread rate or flow speed at an event is derived. A sentence about what a video could carry starts with "Not derived:".
4. Nothing is said about a whole name group from one sampled file.
5. Nothing is called validated or confirmed without naming the check.
6. A variable whose form on video is "nothing" (pressure, oxygen, CO, CO2, CO to CO2 ratio, smoke particle size, aging time) gets only its "cannot tell" sentence, never a video count.
7. The page shows no minimum, maximum or last value of a transcribed column.

## NASA quotations used

All BASS-II quotations are from `PSI-25_Science Documents_BASS-II_ReadMe.docx` (PSI-25, doi 10.60555/4qc4-de67), section "Columns in test matrix". They were copied in this step from the copy of that file on the pilot disk (`/Users/choidol/Desktop/NASA/video_pilot/raw_bass2/`, read locally, no network), compared with `docs/video_design/design.md` section 7.3 (equal, including the double spaces), and the short phrases held in `video/settings/bass2.json` (`fields[].nasa_readme.quote`: "instantaneous fan voltagex10", "Uncalibrated radiometer gain", "one day later than actual date") occur in them word for word.

| id | Place | Quotation |
|---|---|---|
| `Q_FAN` | field "Fan display" | "Fan display:  instantaneous fan voltagex10 on the video display.  Maximum was 122, or 12.2 volts." |
| `Q_AIR` | field "Air display" | "Air display:  flow speed measured in the duct in cm/s on the video display.  Response time is very slow (~ 1 min), so reading is only steady for long times at the same flow setting." |
| `Q_RAD` | field "Radiometer gain" | "Radiometer gain:   Uncalibrated radiometer gain, radiometer is displayed on the video.   Adjusted to avoid saturation.  Useful for relative flame intensity readings and flame dynamics (like pre-extinction oscillations).  Video display data rate is 5 Hz." |
| `Q_DATE` | field "Date" | "Date:  actual date of experiment.  Video display is one day later than actual date due to a leap year the on-board computer did not account for." |
| `Q_CO2` | field "CO2 readings" | "CO2 readings:  CDM sensor readings." |
| `Q_CO` | field "CO readings" | "CO readings:  CSA-CP sensor readings." |
| `Q_TEST` | field "Test number" | "Test number:   Initial of PI name followed by test number from the initial matrix.   If multiple runs with same sample on same day, a and b are used to designate." |
| `Q_VIDEOS` | field "Videos" | "Videos:   most test videos have the test number (PI initial+ # from test matrix)  In the Misc video folder, there are backup test recordings, recordings of crew operations, etc." |
| `Q_TABLE_O9` | NASA's BASS-II table (`data/psi/experimental_tables/PSI-25_Experimental table_BASS-II.csv`), row O9, column `Fan display` | "5   .36  .32 blowoff pt 4.0" (the cell read in this step, with its spaces, equal to the design's quotation; `video/settings/bass2.json`, clip O9, `nasa_table_fan_display`, holds it with the inner spaces collapsed: "5 .36 .32 blowoff pt 4.0") |

Not used in a template: the sentence of NASA/TM-20210011385 section 1.2 that the design quotes. It was read by a research sheet, not in this step, and no file under `video/` holds it.

## 1. What a video cannot tell (per variable)

For a quantity that the on-screen text does not hold. Fixed text; the variable selects it. Ground: `docs/video_design/design.md` section 7.4, word for word.

```json
{"id": "video_cannot_tell", "keyed_by": "variable",
 "template": "{sentence}",
 "slots": {"sentence": "the entry of 'by_variable' for the variable"},
 "by_variable": {
  "pressure_kpa": "Not on the screen of any video sampled. For BASS-II the screen shows fan voltage, duct flow speed, a radiometer reading, a date and a clock (NASA's ReadMe).",
  "o2_pct": "Not on the screen of any video sampled. For BASS-II the screen shows fan voltage, duct flow speed, a radiometer reading, a date and a clock (NASA's ReadMe).",
  "co2_pct": "Not on the screen. NASA's table takes them from the CSA-CP and CDM sensor readings (ReadMe: 'CO2 readings:  CDM sensor readings.' 'CO readings:  CSA-CP sensor readings.').",
  "co_ppm": "Not on the screen. NASA's table takes them from the CSA-CP and CDM sensor readings (ReadMe: 'CO2 readings:  CDM sensor readings.' 'CO readings:  CSA-CP sensor readings.').",
  "co_to_co2_molar_ratio": "Not on the screen. NASA's table takes them from the CSA-CP and CDM sensor readings (ReadMe: 'CO2 readings:  CDM sensor readings.' 'CO readings:  CSA-CP sensor readings.').",
  "smoke_particle_size_um": "Not on the screen of any video sampled.",
  "aging_time_s": "Not on the screen of any video sampled.",
  "air_at_event": "The duct flow reading lags by about one minute (NASA's ReadMe); it is not the flow at the moment of an event.",
  "event_time_or_rate": "Not derived from video. An automatic brightness signal was tried and was right in at most 1 of 19 clips; it is not used."
 },
 "applies_to_event_time_or_rate": ["ignition time", "flame-out time", "burn duration", "spread rate", "flame size", "flow at blowoff", "flow at extinction"],
 "ground": "docs/video_design/design.md section 7.4; the brightness result: video/README.md, 'What failed and was dropped'",
 "quotes": ["Q_CO2", "Q_CO", "Q_AIR (paraphrased as 'lags by about one minute')"],
 "example": {"variable": "pressure_kpa", "text": "Not on the screen of any video sampled. For BASS-II the screen shows fan voltage, duct flow speed, a radiometer reading, a date and a clock (NASA's ReadMe)."}}
```

The variable names are the column names of `data/pipeline/tests.csv`; `air_at_event` and `event_time_or_rate` are not columns and are used where a page line would otherwise read a value at an event.

## 2. "Not derived:" sentences

For what a video could carry if a person labelled it. Fixed text; the question selects it. Ground: `docs/video_design/design.md` sections 7.5 and 6.4 (a).

```json
{"id": "video_not_derived", "keyed_by": "question",
 "template": "{sentence}",
 "slots": {"sentence": "the entry of 'by_question' for the question"},
 "by_question": {
  "P1": "Not derived: the screen carries the fan reading every second; no one has labelled the second a flame went out or blew off, and a fan reading becomes a flow speed only through NASA's fan calibration for that day.",
  "S1": "Not derived: the screen carries the fan reading every second; no one has labelled the second a flame went out or blew off, and a fan reading becomes a flow speed only through NASA's fan calibration for that day.",
  "P2": "Not derived: the picture shows the igniter and the on-screen clock; no one has labelled ignition or flame-out times.",
  "P3": "Not derived: a spread rate would need a person measuring the flame edge against a known scale; NASA's report publishes spread rates for 20 tests (NASA/TM-20210011385, Table 5.1).",
  "any": "Not derived: no one has labelled ignition, flame-out or blowoff times in any video."
 },
 "ground": "docs/video_design/design.md section 7.5 (P1, S1, P2, P3) and the ISS P1 line of section 6.4 (a) ('any'). The P3 reference to Table 5.1 is the design's; the report was read by a research sheet, not in this step.",
 "quotes": [],
 "example": {"question": "P2", "text": "Not derived: the picture shows the igniter and the on-screen clock; no one has labelled ignition or flame-out times."}}
```

## 3. The transcription warning

Printed word for word on every link to a transcription and at the top of the transcription README. No slot: the design fixes the O9 example in it.

```json
{"id": "video_transcription_warning", "keyed_by": "every link to a file under video/data/team_transcription_bass2_onscreen_readings/",
 "template": "These are values copied once per second from NASA's on-screen display by code an AI assistant wrote. They are not measurements and not NASA files. No row is labelled as ignition, flame-out or blowoff. The last value in a clip, or its largest value, is not the flow at any event; the flow at blowoff is only what NASA's table states (for O9: \"blowoff pt 4.0\").",
 "slots": {},
 "ground": "docs/video_design/design.md section 7.1. Why: in O9.csv (594 rows) the clip ends at FAN 122, NASA's stated maximum; the smallest value is 40; the one flagged row (576 s) reads 198.",
 "quotes": ["Q_TABLE_O9 (its last three words)"],
 "example": {"text": "These are values copied once per second from NASA's on-screen display by code an AI assistant wrote. They are not measurements and not NASA files. No row is labelled as ignition, flame-out or blowoff. The last value in a clip, or its largest value, is not the flow at any event; the flow at blowoff is only what NASA's table states (for O9: \"blowoff pt 4.0\")."}}
```

## 4. Tie phrases, per link state

One per video row in a per-test file list. The link state comes from `video/data/video_links.csv` (`link_state`, `labels_agreeing`, `labels_against`, `second_label_scope`, `tests_that_day`).

```json
{"id": "video_tie_phrase", "keyed_by": "link_state",
 "by_link_state": {
  "two_labels_agree": {"template": "video of this test (file name and PSI folder name the same test)", "slots": {}},
  "one_label": {"template": "tied by the {label} only",
                "slots": {"label": "'file name' when labels_agreeing is name_id; 'folder name' when it is folder_id"},
                "when_second_label_scope_is_filled": "tied by the file name only: the folder, the sample and the day name both runs of this sample"},
  "labels_disagree": {"template": "tied by {tie_label}; {other_label} disagrees. Labels: {labels_values}.",
                      "slots": {"tie_label": "'file name' when labels_agreeing is name_id, 'folder name' when it is folder_id",
                                "other_label": "'folder or table' when the tie is by the file name; 'file name' when the tie is by the folder",
                                "labels_values": "column labels_values of video/data/video_links.csv: both labels as read (the identifier in the file name, with day and sample for BASS-II, and the identifier in the PSI folder name) and, where the day or sample disagrees with NASA's table, the table value as looked up in the saved listing"},
                      "note": "The design's phrase is 'tied by file name; folder or table disagrees', both labels printed. 4 of the 10 files (2 BASS-II B15 files, 2 CFI-G files) are tied by the folder; for them the design's phrase would be wrong, so the two label slots are swapped. This generalisation is the pm session's; the data role decides."},
  "day_only": {"template": "a video of that test day ({n} tests that day; which one is not known)",
               "slots": {"n": "tests_that_day"},
               "when_n_is_empty": "a video of that test day (NASA's table has one row per test day, not per test)",
               "when_tie_scope_is_several_days": "a video from a folder that spans several test days (which test is not known)",
               "note": "tests_that_day is empty for 1,048 of the 1,217 day_only videos: all of ACME BRE, CLD Flame, E-FIELD and s-Flame (1,021; their tables have one row per test day) and all 27 of SLICE (PSI-106; 26 of them in folders that span several days, tie_scope several_days). The ACME fallback is the saved listing's own note for those rows; the several-days phrase and its use for SLICE are proposed by the pm session. The data role decides, or fills n from the per-day tables."},
  "id_not_in_table": {"template": "carries an identifier that NASA's table does not list", "slots": {}},
  "none": {"template": "not tied to a test", "slots": {}}
 },
 "ground": "docs/video_design/design.md section 4, table 'Link state', column 'Phrase on the page'; video/settings/name_rules.json, 'link_states'",
 "quotes": ["Q_TEST and Q_VIDEOS are the ground of the BASS-II name rule behind these ties"],
 "example": [
  {"file": "PSI-25_Raw Data_BASS_GMT177_SAMPLE_209_TEST_O9.mp4", "link_state": "two_labels_agree", "text": "video of this test (file name and PSI folder name the same test)"},
  {"file": "PSI-25_Raw Data_BASS_GMT195_SAMPLE_203_TEST_P13a.mp4", "link_state": "one_label", "text": "tied by the file name only: the folder, the sample and the day name both runs of this sample"},
  {"file": "PSI-25_Raw Data_BASS_GMT50_SAMPLE_148_TEST_B3.mp4", "link_state": "labels_disagree", "text": "tied by file name; folder or table disagrees. Labels: file name: B3, day 50, sample 148; folder: B1."},
  {"file": "PSI-25_Raw Data_BASS_GMT203_SAMPLE_210_TEST_O10_2ND_VIEW.mp4", "link_state": "labels_disagree", "text": "tied by file name; folder or table disagrees. Labels: file name: O10, day 203, sample 210; folder: O10; NASA's table (as looked up in the saved listing): GMT in name 203 vs table 213."}
 ]}
```

The `labels_values` text of all 10 files is also in `video/data/video_links_summary.json`, `labels_disagree_files`.

## 5. The lunar-habitat sentence

Generated from the counts, never typed. Ground: `docs/video_design/design.md` section 6.4 (a), "Lunar habitat, Extinction conditions (S1)"; claim 4 of section 11.

```json
{"id": "video_lunar_habitat_S1", "keyed_by": "scenario lunar_habitat, question S1",
 "template": "Video. None of the {counted_inside} counted droplet tests recorded inside these ranges has a video file tied to it. FLEX holds {flex_files} video files ({flex_gb} GB); {flex_not_in_table} of them carry 2013-2014 test points that NASA's table (2009 to 2011) does not list; their atmosphere is not stated in any file opened; they are not counted for any environment. {gas_with_video} of the {gas_inside} gas-flame tests inside the ranges (CFI-G) have a video of the test ({gas_files} files, {gas_gb} GB), but CFI-G counts for no question, and no readings were seen in the sampled CFI-G frames.",
 "slots": {
  "counted_inside": "summary.scenarios.lunar_habitat.by_question_and_placement.S1.inside.tests (and its no_video_tied_to_the_test must equal it; otherwise this template does not apply)",
  "flex_files": "summary.by_investigation['PSI-69'].files",
  "flex_gb": "summary.by_investigation['PSI-69'].bytes / 1e9, one decimal",
  "flex_not_in_table": "summary.by_investigation['PSI-69'].id_not_in_table",
  "gas_inside": "summary.scenarios.lunar_habitat.tests_inside_the_ranges.by_investigation['PSI-159']",
  "gas_with_video": "count of tests in summary.scenarios.lunar_habitat.tests_inside_the_ranges.two_labels_agree_files (all PSI-159 today)",
  "gas_files": "summary.scenarios.lunar_habitat.tests_inside_the_ranges.videos.by_link_state.two_labels_agree.files",
  "gas_gb": "summary.scenarios.lunar_habitat.tests_inside_the_ranges.videos.by_link_state.two_labels_agree.bytes / 1e9, two decimals"
 },
 "fixed_parts_not_from_code": ["'2009 to 2011': the years of NASA's FLEX table, from the design", "'their atmosphere is not stated in any file opened' and 'no readings were seen in the sampled CFI-G frames': design sections 6.4 and 5 (sample result, described by an AI agent)"],
 "quotes": [],
 "example": {"text": "Video. None of the 17 counted droplet tests recorded inside these ranges has a video file tied to it. FLEX holds 183 video files (35.9 GB); 163 of them carry 2013-2014 test points that NASA's table (2009 to 2011) does not list; their atmosphere is not stated in any file opened; they are not counted for any environment. 8 of the 9 gas-flame tests inside the ranges (CFI-G) have a video of the test (8 files, 2.64 GB), but CFI-G counts for no question, and no readings were seen in the sampled CFI-G frames."}}
```

Filled from today's summary: `counted_inside` 17, `flex_files` 183, `flex_gb` 35.9 (35,883,054,431 bytes), `flex_not_in_table` 163, `gas_inside` 9, `gas_with_video` 8, `gas_files` 8, `gas_gb` 2.64 (2,640,554,564 bytes). Equal to the design's sentence.

## 6. The radiometer sentence

On the card of any BASS-II transcription and wherever RAD is shown. Fixed text.

```json
{"id": "video_rad", "keyed_by": "column RAD_trunc1",
 "template": "RAD is copied once per second from a display NASA updates 5 times per second; it cannot show pre-extinction oscillations. It is uncalibrated, its gain was changed during tests (see the table's Radiometer gain column), and it rises with the igniter alone, so it is not a flame signal and not comparable between tests or across a gain change.",
 "slots": {},
 "ground": "docs/video_design/design.md section 7.2, word for word. '5 times per second' and 'uncalibrated' rest on Q_RAD; 'rises with the igniter alone' on video/README.md, 'Limits' (the reading responds to the igniter; O12 never ignited and reads up to 1.8).",
 "quotes": ["Q_RAD"],
 "example": {"text": "RAD is copied once per second from a display NASA updates 5 times per second; it cannot show pre-extinction oscillations. It is uncalibrated, its gain was changed during tests (see the table's Radiometer gain column), and it rises with the igniter alone, so it is not a flame signal and not comparable between tests or across a gain change."}}
```

## 7. What the BASS-II screen shows (for the card)

```json
{"id": "video_bass2_screen", "keyed_by": "investigation PSI-25",
 "template": "On the screen, in NASA's words: fan voltage x10, duct flow speed in cm/s, an uncalibrated radiometer; also a date and a clock. Not on the screen: oxygen, pressure.",
 "slots": {},
 "date_line": "\"Video display is one day later than actual date due to a leap year the on-board computer did not account for.\" (BASS-II ReadMe) observed on 3 July 2014 clips; February 2014 clips not checked",
 "other_investigations": "an on-screen display with the same field names was seen in 1 sampled file; no document was matched to its fields; not transcribed",
 "other_investigations_for": ["PSI-26", "PSI-106", "PSI-107"],
 "ground": "docs/video_design/design.md sections 6.4 (a) and 7.3. No date is shifted by code, for any investigation. FUEL is not interpreted.",
 "quotes": ["Q_FAN", "Q_AIR", "Q_RAD", "Q_DATE"],
 "example": {"text": "On the screen, in NASA's words: fan voltage x10, duct flow speed in cm/s, an uncalibrated radiometer; also a date and a clock. Not on the screen: oxygen, pressure."}}
```
