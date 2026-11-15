DRAFT written by an AI assistant (Claude Code, pm role) on 15 November 2026 for the team lead to rewrite in his own words before use. Backup material: one slide line, its speaker note and one paragraph of the submission text on video. Brought up to date at about 12:00 KST on 15 November. Checked by AI sessions; reviewed by a person: 0. Every number is listed at the end with its file. Keep "Built with AI assistance (Claude)" in the slide footer until the words are rewritten.

> **For the team lead.** Delete this box before use.
>
> - **Where this sits.** The deck in `slides_outline.md` has seven slides. Video appears on slide 5 (one line in the bottom strip) and slide 6 (the video reader). This file is backup for questions.
> - **What exists now.** `video/index_by_name.py` with its tables and shortlists under `video/data/`; the ladder in `video/README.md`; the sentence templates in `docs/video_design/video_wording.md`. The data role copies the video rows into `data/pipeline/file_links.csv`. The page block `#piles` (built by `web/raw_piles.py`) prints the video sentence for the lunar habitat, extinction conditions; this job checked it in a local build, not on the public page.
> - **What an independent recount found.** A second AI session recounted the ties with its own code (`validation/raw_chain_recount.py`). It reproduces the 662 videos where two labels agree and the 374 with one label, and differs elsewhere: labels disagree 15 against 10, day only 1,201 against 1,217, identifier not in the table 341 against 330. The catalog role names four causes (a date against a GMT day in the BASS table, a fallback to the name's day for 5 CFI videos, the attribution of one disagreeing FLEX video, and no "run" scope for 3 SAME-R files). How to attribute a disagreeing video is a team decision; until then, quote only the two-label count without this note. Separately, `data/pipeline/video_tie_differences.csv` lists 59 videos where the data role's first name tie differs from this index; none is resolved.

## Slide line (12 words or fewer)

> 426 GB of video; 49 files (3.5 GB) for this question.

11 words. "This question" is the flammability limit at ISS oxygen; the slide shows it beside the line. A 12-word variant that adds the transcribed count: "426 GB video; 49 files (3.5 GB) for this question; 7 transcribed".

## Speaker note (40 words at most)

> PSI holds 2,623 combustion videos, 426 GB. Code compared their file and folder names with NASA's test tables, reading no video. For flammability tests at ISS oxygen: 49 main-view files, 3.5 GB; 7 transcribed. Nothing is measured from video.

39 words.

## Paragraph for the submission text

> PSI's combustion investigations hold 2,623 video files (426 GB) in 14 of 24 investigations, with no index of which file belongs to which test. We did not process them. Code that an AI assistant wrote reads the NASA identifier or the test number in each file name and PSI folder name and compares them with NASA's test tables, without reading a video byte. 662 videos are tied to one test where two labels agree (463 tests), and 374 more carry one label. An independent recount by a second AI session reproduces these two counts; for the other videos the two codes differ, and the cases are listed, not resolved. For a question and an environment this gives a short list: for flammability tests at ISS oxygen, 49 main-view recordings (3.5 GB) instead of 426 GB; for the lunar habitat, none of the 17 counted tests has a video tied to it, and the page states that rather than leaving it blank. Deeper reading is done only where a question needs it, and each statement says at which depth it was made: for 19 BASS-II clips a reader (code written with an AI assistant) copied NASA's on-screen fan, flow and radiometer readings, 16,019 rows (a copy of NASA's display, not a measurement and not a NASA data file). Nothing is measured from the picture: no flame-out time, ignition delay, burn duration or flow at an event. An automatic brightness signal was tried, was right in at most 1 of 19 clips [NOT RECOUNTED: stated in `video/README.md`; the brightness check is not in the repository], and was removed. Who checked the ties: separate code and AI sessions; a second AI session's recount reproduces the two-label and one-label counts and differs on the others, which are listed. Reviewed by a person: 0. This is a research exploration tool, not safety guidance; nothing here predicts an untested condition.

## Numbers and where they come from

Recounted by the pm role's AI session on 15 November 2026 with `recount_slides.py` (read-only, in the pm session's scratch folder `subtext/`) unless the row says otherwise.

| Number | Value | File and how |
|---|---|---|
| Video files, bytes | 2,623; 426,053,691,302 (426 GB) | `video/data/video_links.csv`: rows, sum of `bytes`; equal to `video_links_summary.json` `totals` and to `raw_inventory.json` `by_kind.video` |
| Investigations with a video file | 14 of 24 | `video_links.csv`: distinct `investigation` (14) |
| Two labels agree | 662 videos; 463 tests | `video_links.csv`: `link_state` = two_labels_agree; distinct `test_id` of those rows |
| One label | 374 | `video_links.csv` `link_state`. Not quoted in the paragraph: labels disagree 10 and day only 1,217, which the recount gives as 15 and 1,201 |
| ISS flammability shortlist | 49 files, 3,515,643,202 bytes (3.5 GB); 7 transcribed | `video/data/shortlist_iss_P1_main_view.csv`: rows, sum of `bytes`, `transcribed` = yes |
| Lunar habitat | 0 of 17 counted tests with a video tied | the 17 S1 counted tests inside the lunar ranges (`scenario_tests.csv`, `need_tests.csv`) against `video_links.csv` rows with a test-level link state |
| Transcribed clips | 19 BASS-II clips; 16,019 rows | `video/settings/bass2.json` `clips`; data rows of the 19 CSV files in `video/data/team_transcription_bass2_onscreen_readings/` |
| Brightness signal | right in at most 1 of 19 clips | `video/README.md`, "What failed and was dropped" (read; it adds that the one clip is doubtful). [NOT RECOUNTED: stated in `video/README.md`; the brightness check is not in the repository] |
| Independent recount | two labels agree 662 and one label 374 reproduced; labels disagree 15, day only 1,201, identifier not in the table 341 | `validation/raw_chain_recount_report.md`, summary (read) |
| Tie differences with the data role | 59 videos | `data/pipeline/file_links_summary.json` `video_tie_differences.rows` (read) |
