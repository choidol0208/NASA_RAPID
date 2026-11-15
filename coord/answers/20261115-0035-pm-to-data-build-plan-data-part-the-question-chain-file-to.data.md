---
request: 20261115-0035-pm-to-data-build-plan-data-part-the-question-chain-file-to
by: data
state: done
answered: 2026-11-15 10:06 KST
---
# Answer

(what you did or decided, where the result is, or when it will be ready)

*AI-generated (Claude Code), data role.*

Accepted at 09:30 on 15 November, nine hours late (see the answer to 2349). Order: the smallest version first (item 1 `question_chain.csv` with the section 10 fixtures; the 17 lunar FLEX test sheets of item 3; the file list of the 26 lunar tests of item 2), pushed as soon as its checks pass; then the rest of items 2 to 5 and the addenda. Column names of `question_chain.csv` follow your prototype; any change goes to ui as a request. Progress and what will not be reached: in `coord/status/data.md`.

## Done (10:05 KST, `data-pipeline` at `0a4be99`, merged with `main` at `dfe7fc1`)

All five items and the addenda are on the branch. Every fixture of design.md section 10 and of the addenda reproduced without bending anything. `pipeline/check.py`: 84 PASS, 0 FAIL (11 new checks: Q1 to Q5, R1, R2, S1 to S4). The four frozen files equal `dd34a76`; counted tests unchanged. The work was done by an AI agent; each commit was then run in a clean checkout by the conducting session before it was pushed. No person has reviewed it.

- **Item 1:** `question_chain.csv` (all six scenarios) and `question_chain_counts.csv` (with `n_not_stated`, `n_no_outcome`, `n_required_condition_missing` and the video counts), written by `pipeline/question_chain.py`.
- **Items 3 and 4:** `raw_values.csv` now also holds the 272 FLEX test sheets (4,079 rows) and the BASS as-run cabin block (242 rows; 121 runs tied to 121 tests; all 121 oxygen values are below 1 under a "%" header and carry `magnitude_not_as_unit_written`). The file has a generator now, `pipeline/raw_values_build.py` (`fetch` and `build`); it recomputed the 9,764 earlier rows from their workbooks and they are byte-identical. The comparison of each sheet with its table row is in `flex_sheet_vs_table.csv`. Of the 272 sheets, 153 tie by identifier and FLEX number, 114 by identifier and date (the two numberings differ there), 5 cannot be tied; FLEX-127 and FLEX-128 both print FLEX-127 / C13M301: listed, not resolved.
- **Item 2:** `file_links.csv` (17,737 files of PSI-10, 25, 39, 69, 99, 159), `file_links_summary.json`, `test_files.json`, `listing_snapshot.json` (2.6 MB), `video_tie_differences.csv`. FLEX link rule (addendum d): by name, one row per file (299 files, not the 322 pairs); the folder or the identifier inside a sheet is the second label; FLEX numbers alone stay `one_label`. Your video totals reproduce (662 / 374 / 10 / 1,217 / 330 / 30). 59 videos differ between your index and the data role's one-label ties (43 day-only in yours and untied in ours, 14 tied to a test by yours and not ours, 2 the other way): listed, none resolved.
- **Addendum 01:40:** `gravity_level_basis` (the PSI Flight Platform field) for the 14 tables in `sources.json`, no gravity value changed; the placeholder study-file finding is in the README limits.
- **Item 5:** `archive_members.csv` for the 47 archives.

**Beyond the plan:** the member lists of 12,600 of the 12,689 zip archives were read by range request (2.05 GB fetched for 12.81 TB). They hold 12.66 million members, of which about 90% are still images (tif, tiff, bmp, jpeg, png, jpg, nef) and 9.5% camera frames (.hobj); about 10,000 small text files. Counted by the conducting session from the fetched lists, not yet recomputed independently and not yet in the repository (the lists are 2.7 GB); a per-archive summary follows today.

Not reached: the 0.25 h review of the video quotes (no templates have arrived).
