DRAFT written by an AI assistant (Claude Code, pm role) on 15 November 2026 for the team lead to rewrite in his own words before use. Material for one slide line, its speaker note and one paragraph of the submission text on video. Checked by AI sessions; a person: none yet. Every number is listed at the end with its file. Keep "Built with AI assistance (Claude)" in the slide footer until the words are rewritten.

> **For the team lead.** Delete this box before use. What exists now: `video/index_by_name.py` and its tables and shortlists under `video/data/`, the ladder in `video/README.md`, the sentence templates in `docs/video_design/video_wording.md`. Not yet built: the video rows and the pile-2 video line on the page (design steps 5, 6 and 8, data and ui roles). Until they land, do not say the page shows the video list; say the repository does.

## Slide line (12 words or fewer)

> 426 GB of video; 49 files (3.5 GB) for this question.

11 words. "This question" is the flammability limit at ISS oxygen; the slide shows it beside the line. A 12-word variant that adds the transcribed count: "426 GB video; 49 files (3.5 GB) for this question; 7 transcribed". The 13-word form "426 GB of video; 49 files (3.5 GB) for this question; 7 transcribed" is over the limit.

## Speaker note (40 words at most)

> PSI holds 2,623 combustion videos, 426 GB. Code compared their file and folder names with NASA's test tables, reading no video. For flammability tests at ISS oxygen: 49 main-view files, 3.5 GB; 7 transcribed. Nothing is measured from video.

39 words.

## Paragraph for the submission text

> PSI's combustion investigations hold 2,623 video files (426 GB) in 14 of 24 investigations, with no index of which file belongs to which test. We did not process them. Code that an AI assistant wrote reads the NASA identifiers in each file name and PSI folder name and compares them with NASA's test tables, without reading a video byte. 662 videos are tied to one test by two labels that agree (463 tests); 374 more by one label; 10 whose labels disagree are listed, not resolved; 1,217 reach only a test day. For a question and an environment this gives a short list: for flammability tests at ISS oxygen, 49 main-view recordings (3.5 GB) instead of 426 GB; for the lunar habitat, none of the 17 counted tests has a video tied to it, and that is stated rather than left blank. Deeper reading is done only where a question needs it, and each statement says at which depth it was made: for 19 BASS-II clips the team copied NASA's on-screen fan, flow and radiometer readings (a copy of NASA's display, not a measurement and not a NASA data file). Nothing is measured from the picture: no flame-out time, ignition delay, burn duration or flow at an event. An automatic brightness signal was tried, was right in at most 1 of 19 clips, and was removed. Who checked the ties: separate code and AI sessions; a person: none yet. This is a research exploration tool, not safety guidance; nothing here predicts an untested condition.

## Numbers and where they come from

| Number | Value | File |
|---|---|---|
| Video files, bytes | 2,623; 426,053,691,302 (426 GB) | `video/data/video_links_summary.json` `totals` |
| Investigations with a video file | 14 of 24 | `video/data/video_links_summary.json` `by_investigation` (14 keys); 24 from `docs/video_design/design.md` section 3 |
| Two labels agree | 662 videos, 463 tests | `by_link_state`, `tests_with_video_by_best_link_state` |
| One label; labels disagree; day only | 374; 10; 1,217 | `by_link_state` |
| ISS flammability shortlist | 49 files, 3,515,643,202 bytes (3.5 GB); 7 transcribed | `video/data/shortlist_iss_P1_main_view.csv`; `scenarios.iss.shortlists.P1` |
| Lunar habitat | 0 of 17 counted tests with a video tied | `scenarios.lunar_habitat.by_question_and_placement.S1.inside` |
| Transcribed clips | 19 BASS-II clips | `video/settings/bass2.json` `clips` |
| Brightness signal | right in at most 1 of 19 clips | `video/README.md`, "What failed and was dropped" |
