DRAFT written by an AI assistant (Claude Code, pm role) on 15 November 2026 for the team lead to rewrite in his own words before use. Backup material for questions on the raw data, and two paragraphs for "Project Details". Brought up to date at about 12:00 KST on 15 November from the data role's files in `data/pipeline/`, the catalog role's reading order and recount, and the page block built by `web/raw_piles.py`. Checked by AI sessions; reviewed by a person: 0. Every number is listed at the end with its file.

> **For the team lead.** Delete this box before use.
>
> **1. Where this sits.** The deck in `slides_outline.md` has seven slides, the limit. The raw-data answer is on its slide 5 ("For each question, the page shows where the data are"). This file is backup: the slide below is for questions, or to replace slide 5 if you prefer its picture.
>
> **2. What has landed since the earlier draft.** Every build step of `docs/raw_data_design/design.md` section 6 has landed except the person's spot check (step 11):
> - the question chain, `data/pipeline/question_chain.csv` and `question_chain_counts.csv` (step 2);
> - the file-to-test links with the two-label rule, `file_links.csv`, `file_links_summary.json` and `test_files.json`, for PSI-10, PSI-25, PSI-39, PSI-69, PSI-99 and PSI-159 (step 3);
> - all 272 FLEX test sheets and the BASS as-run cabin block read into `raw_values.csv`, compared in `flex_sheet_vs_table.csv` and `raw_values_effect.json` (steps 4 and 5);
> - the reading order, `data/catalog/reading_order.csv`, 53 rows (step 6);
> - the independent recount, `validation/raw_chain_recount.py`: 62 of 71 fixtures reproduce, the 9 others are video link states (step 7);
> - the page block "Where the data are: in NASA's tables, in the archive, or no record" (section `#piles`, step 8).
>
> Beyond the plan, the data role also classified all 60,866 files by name (`raw_file_groups.csv`, `raw_layers_summary.json`) and listed the central directories of 12,600 of the 12,689 zip archives by range request (`archive_summary.csv`, `archive_summary_totals.json`).
>
> **3. Limits kept in every sentence.** The numbers are the team's computation, not NASA's conclusions. The page is a research exploration tool, not safety guidance. Pile 3 says "no record in PSI (listing of 14 November 2026)" and nothing about what NASA tested. A value read from a raw file is "read from NASA's file, not adopted, not counted". A link is "two labels agree", never "confirmed". The 26 tests are microgravity tests whose recorded oxygen and pressure lie inside the ranges the team set for the lunar habitat; nothing here calls them lunar tests. The 17 droplet tests were recorded at 71.2 to 72.4 kPa, above 70.3 kPa (10.2 psi).
>
> **4. The AI mark.** Keep "Built with AI assistance (Claude)" in the slide footer until you have rewritten the words. Only on this backup slide, the mark counts toward the 35 visible words.

## The backup slide

- **Title (10 words):** From 13.47 TB to 398 files that name your tests
- **Words on the slide (6 words):** Lunar habitat: code follows NASA's identifiers.
- **Numbers in the picture (15 words):** 60,866 files · 13.47 TB / 398 · 104.4 GB / 316 · 86.9 MB / 17 · 15 kB / archives 96.49%
- **Source line under the picture (9 words):** Team computation, not NASA's. PSI listing, 14 November 2026.
- **Mark on the slide (footer, small type; 5 words):** Built with AI assistance (Claude)
- **Speaker note (60 words):** NASA's archive holds 13.47 terabytes for 24 investigations; 96 percent is zip archives. We do not process it. For a lunar habitat, 26 microgravity tests sit inside our oxygen and pressure ranges. 398 files carry their NASA identifier or test number; two labels agree for 336. Code read the 17 test sheets against NASA's table. No AI model runs here.

Visible words besides the title: 6 + 15 + 9 + 5 = 35. In the "Numbers in the picture" line the slashes separate the five pieces of text and are not on the slide. "Your tests" stands for the tests recorded inside the oxygen and pressure ranges the team set for an environment; the line of words names the lunar habitat.

### The picture

Built in the slide tool from the numbers below; it is not a capture of the page. Four stacked boxes on the left (about two thirds of the width) and one bar on the right.

Left: four boxes of equal size, joined by down arrows, one colour that gets darker downwards. They are equal on purpose: to scale, every box below the first would be invisible (the second is 0.77% of the bytes of the first).

| Box | Text in the box | What the box is (not written on the slide) |
|---|---|---|
| 1 | 60,866 files · 13.47 TB | NASA's PSI archive for the 24 combustion investigations (listing of 14 November 2026) |
| 2 | 398 · 104.4 GB | Files whose name carries the NASA identifier or the test number of one of the 26 tests recorded inside the oxygen and pressure ranges of the lunar habitat; 0.77% of the bytes |
| 3 | 316 · 86.9 MB | Of these, the files that are not a zip archive or a `.ts` video recording |
| 4 | 17 · 15 kB | The test sheets of the 17 counted droplet tests, one per test; all 17 read |

Between the boxes (for the speaker; not on the slide): from 1 to 2, a join on the labels NASA wrote, from the file listing alone, nothing downloaded; from 2 to 3, by file extension (82 archives and recordings, 104.3 GB, set aside); from 3 to 4, the one sheet per test that states its conditions and result.

Right: one vertical bar to scale, the archive by kind of file. Label only the largest segment: "archives 96.49%".

| Segment | Files | Bytes | Share of the bytes |
|---|---|---|---|
| Zip archives | 12,689 | 13.00 TB | 96.49% |
| Video | 2,623 | 426 GB | 3.16% |
| All other kinds | 45,554 | 46.4 GB | 0.34% |

Kinds are read from file names and PSI categories; no file was opened for this bar.

## Two paragraphs for "Project Details"

**Finding the raw data a question needs.** Most of NASA's PSI combustion archive is raw files: 60,866 files and 13.47 TB for 24 investigations (PSI's file listing of 14 November 2026). By file name and PSI category, 96.49% of the bytes are zip archives and 3.16% are video. PSI's experimental tables are 22 files of 0.2 MB, and the team's 1,824 tests come from 14 of them. We do not process the archive. Instead, code classified every listed file by its name: 12,934 files carry the identifier of a test, 30,634 that of a test day or session, and 17,298 neither. It also listed the contents of 12,600 of the 12,689 zip archives by reading only their directories, 2.05 GB fetched for 12.8 TB, with no archive downloaded. For a chosen environment and fire-safety question, code places every recorded test: inside the environment's oxygen and pressure ranges, outside by a recorded value, oxygen recorded for an oxidizer stream, or not placeable from the tables. For the lunar habitat that gives 26 inside, 1,059 outside, 63 with oxidizer-stream oxygen and 676 not placeable. For six investigations, code ties each test to the PSI files whose names carry its NASA identifier or test number. A link counts as "two labels agree" only when a second label, the PSI folder or the identifier inside a test sheet, names the same test; the other cases are listed, not resolved. The page then shows three piles per question: in NASA's tables; in the archive, not in a table; and no record in PSI (listing of 14 November 2026), each with its ground. For a lunar habitat, the 26 tests inside the ranges are 17 fuel-droplet tests at 71.2 to 72.4 kPa and 9 gas flames at 50.7 kPa, all in microgravity. From the file listing alone, 398 files (104.4 GB, 0.77% of the bytes) carry the NASA identifier or the test number of one of them; two labels agree for 336, 47 carry one label, and for 15 the labels name different tests. A file that names a test is not shown to hold what a question needs. Code read all 272 FLEX test sheets (250 kB), among them the 17 of the counted droplet tests, against NASA's table: the identifier inside equals the table's in 17 of 17, the pressure in 16 and the oxygen in 16. Where the table has no number for the extinction diameter (11 tests), the sheet writes a number for 3, 0.00 for 1 and nan for 7. These values are read from NASA's file, not adopted, not counted. For solid fuels the page says something different: all 133 tests counted for the flammability limit have their oxygen in NASA's table, between 13.6 and 22.2%, below the 30% of this environment. This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of 14 November 2026).

**The practices it uses, and where AI is.** The chain borrows simple, documented practices; their sources are in the References. A catalogue of files built from name patterns. Joins on exact keys that need two agreeing labels. Reading only a file's head, or an archive's directory, by HTTP range request. A value looked up by the header text as NASA wrote it, with no embeddings and no ranking by a model. "n of N files opened" on every statement about raw files, and a small file group read whole instead of sampled, as the 272 FLEX test sheets were. A fixed, published reading-order rule over target tests and bytes, with no probabilities; it is the team's rule, not a NASA priority. For each question, the conditions and outcomes it needs, units converted as written, and the caveats that a droplet is not a solid material and that microgravity is not lunar gravity. The source, the bytes read and the checker on every row, following the FAIR principles, NASA's SPD-41a and the ISA-Tab format. No AI model runs in the chain: placement, links, piles, reading order and every sentence are code and fixed templates, and nothing is generated when the page loads. AI was used around it: AI coding sessions (Claude Code) wrote the code and drafted this text; an earlier AI reading of file headers is kept with its label; `pipeline/check.py` recomputes the outputs with separate code (90 of 90 checks pass); and a second AI session recounted the chain with code that imports none of the pipeline: 62 of 71 fixtures reproduce, and the 9 that do not are video link states. Reviewed by a person: 0. Review by combustion researchers, and a person's spot check of the file links, are next steps. The counts are the team's computation, not NASA's conclusions, and the page is a research exploration tool, not safety guidance.

## Numbers used

Recounted by the pm role's AI session on 15 November 2026 between 11:40 and 12:00 KST with `recount_slides.py` (read-only, in the pm session's scratch folder `subtext/`) unless the row says otherwise.

| Number | Value | File and how |
|---|---|---|
| Archive | 60,866 files; 13,471,850,126,356 bytes; 24 investigations | `data/pipeline/raw_inventory.json` `_meta.totals`; equal to the sum of `files` in `raw_file_groups.csv` |
| Zip archives | 12,689 files; 12,999,389,379,194 bytes; 96.49% | same, `by_kind.archive` |
| Video | 2,623 files; 426,053,691,302 bytes (426 GB); 3.16% | same, `by_kind.video` |
| All other kinds | 45,554 files; 46,407,055,860 bytes; 0.34% | same, sum of the six other kinds |
| Experimental tables | 22 files; 211,116 bytes | same, `by_kind.experimental_table` |
| Tables read into tests | 14 of 22; 1,824 tests | `data/pipeline/tests.csv`: rows; distinct `source_file` |
| Files by name | test 12,934; day or session 30,634; neither 17,298 | `raw_file_groups.csv`: sums of `files_tied_to_a_test`, `files_tied_to_a_day_or_session`, `files_not_tied`; equal to `raw_layers_summary.json` `overall.names` |
| Archive directories | 12,600 of 12,689 archives; 2,053,572,781 bytes fetched; 12,808,926,048,063 bytes of those archives; 12,662,319 members (12,662,354 entries less 35 directories) | `data/pipeline/archive_summary.csv`: rows, sums of `bytes_fetched`, `listing_bytes`, `members`, `directories`; equal to `archive_summary_totals.json` |
| Placement, lunar habitat | inside 26; outside by a recorded value 1,059; oxidizer-stream oxygen 63; not placeable 676 | `scenario_tests.csv`: `o2_match` and `pressure_match`, order inside, outside, oxidizer stream, not placeable; equal to the page block and to `validation/raw_chain_recount.json` (block A) |
| Tests inside the lunar ranges | 26: 17 PSI-69 (liquid, 71.2341 to 72.3674 kPa), 9 PSI-159 (gas, 50.665 kPa) | `scenario_tests.csv`, `tests.csv` |
| Linked investigations | PSI-10, PSI-25, PSI-39, PSI-69, PSI-99, PSI-159; 17,737 file rows | `data/pipeline/file_links.csv`: distinct `investigation_id`, rows |
| Files naming the 26 tests | 398 files; 104,358,456,350 bytes; 0.7746% of the archive | `data/pipeline/test_files.json` `scenarios.lunar_habitat`: distinct `psi_file_id` over the 26 tests; equal to `file_links_summary.json` |
| Second label | two labels agree 336; one label 47; labels disagree 15 | same, `link_state` of the distinct files |
| Not an archive or a video recording | 316 files; 86,853,632 bytes; the other 82 files 104,271,602,718 bytes | same, names not ending in `.zip` or `.ts`; `file_links_summary.json` `small_files`, `archive_and_video_files` |
| ISS (if asked) | 179 tests inside; 2,399 files; 440,743,142,674 bytes; 3.27% | `file_links_summary.json` `scenarios.iss` (read) |
| FLEX test sheets | 272 files; 250,375 bytes | `raw_values.csv`, extraction `flex_test_sheet`: distinct `psi_file_id` and their `bytes` |
| The 17 sheets | 15,369 bytes; identifier agrees 17, pressure 16, oxygen 16 | `flex_sheet_vs_table.csv`, rows of the 17 tests, keys `CIR Test Number`, `Pressure (atm)`, `O2 Mole Fraction` |
| Extinction diameter, table against sheet | table blank or dash (11): sheet number 3, zero 1, nan 7; table number or zero (6): same form 5, nan 1 | `flex_sheet_vs_table.csv`, key `Dext (mm)`: blank/nan 6, blank/number 2, dash/number 1, dash/zero 1, dash/nan 1; number/number 3, zero/zero 2, number/nan 1 |
| BASS as-run cabin block | 1 file; 111,886 bytes; 121 runs | `raw_values.csv` extraction `bass_as_run_cabin_block` (242 rows, two columns); `raw_values_effect.json` |
| Counted tests, flammability limit | 133 (125 PSI-25, 8 PSI-99); oxygen 13.6 to 22.2% | `need_tests.csv` (P1, stated), `tests.csv` |
| Reading order | 53 rows | `data/catalog/reading_order.csv` rows |
| Pipeline checks | 90 of 90 pass | `data/pipeline/validation_report.json` `summary` |
| Independent recount | 62 of 71 fixtures; the 9 others in the video block | `validation/raw_chain_recount.json` `fixtures_summary` |
| 10.2 psi | 70.3 kPa | `scoring.scorer.rank('lunar habitat')` scenario; `pipeline/spec/scenarios.json` |
