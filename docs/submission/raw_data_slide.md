DRAFT written by an AI assistant (Claude Code, pm role) on 15 November 2026 for the team lead to rewrite in his own words before use. It is material for one slide and for two paragraphs of "Project Details". Checked by AI sessions: the session that wrote it, a second session that recounted its numbers and its words, and a third session that corrected it for the second's findings (about 01:40 KST). Read by a person: none yet. Every number is listed at the end with its file.

> **For the team lead.** Delete this box before use.
>
> **1. What has not landed yet.** At 01:40 KST on 15 November the design (`docs/raw_data_design/design.md`) and its prototype files exist. The pipeline files and the page block of the build plan do not. These sentences and numbers wait for a build step (steps as in `design.md` section 6; the full list is `docs/raw_data_design/claims.md` section 2):
>
> | Where | Sentence or number, by its first words | Waits for |
> |---|---|---|
> | Title | "From 13.47 TB to 398 files ..." (and the 0.77% of the other title) | step 3 (link files); today a prototype count by file name |
> | Slide words | "Lunar habitat: code follows NASA's identifiers." | step 3; today a prototype does it for the lunar habitat |
> | Picture, boxes 2 and 3 | 398 · 104.4 GB; 316 · 86.9 MB | step 3; today a prototype count by file name |
> | Picture, box 4 | 17 · 15 kB | the count of files and bytes holds today (prototype link file); "Code read the 17 test sheets" in the speaker note waits for step 4 |
> | Speaker note | "Code read the 17 test sheets ..." | step 4; today the design job read the first 700 bytes of each sheet (11,871 of 15,369 bytes) |
> | Speaker note | "No AI model runs in the chain." | steps 2, 3 and 8 for the chain as built; it holds for the prototype code today |
> | Paragraph 1 | "For the two demo environments, it ties ..." and "From the file listing alone ..." | step 3. Its five investigations hold all 26 tests inside the lunar ranges; of the 179 tests inside the ISS ranges, 25 belong to PSI-39, which step 3 does not link |
> | Paragraph 1 | "The page then shows three piles ..." | steps 2 and 8 |
> | Paragraph 1 | "Code read the 17 test sheets ..." and the sentence after it | step 4 |
> | Paragraph 2 | "what to read first is a fixed, published rule ..." | step 6 |
> | Paragraph 2 | "a person's spot check gets an exact bound" | step 11; delete the clause if no person does the spot check |
> | Paragraph 2 | "a second AI session recomputes the numbers with separate code" | step 7; until then write "a recount by a second AI session is planned" |
>
> The first box of the picture and the bar on the right hold today. So do the sentences about the archive by kind of file and about solid fuels (133 counted tests, oxygen 13.6 to 22.2%).
>
> **2. Seven slides.** The deck in `slides_outline.md` already has seven slides, the limit. This slide replaces one of them or its picture goes onto an existing slide. Suggestion of the pm role's AI session: it replaces slide 3, because it shows the same step (COMPARE) with a stronger picture; the count of 1,824 tests can move into its speaker note.
>
> **3. The AI mark.** An AI assistant wrote these words. Keep "Built with AI assistance (Claude)" in the footer of the slide until you have rewritten them. The mark is counted among the words on the slide.
>
> **4. Limits kept in every sentence.** The numbers are the team's computation, not NASA's conclusions. The page is a research exploration tool, not safety guidance. Pile 3 says "no record in PSI (listing of 14 November 2026)" and nothing about what NASA tested. A value read from a raw file is "read from NASA's file, not adopted, not counted". The 26 tests are microgravity tests whose recorded oxygen and pressure lie inside the ranges the team set for the lunar habitat. Nothing here calls them lunar tests or says they were run in the lunar-habitat atmosphere (decision of 14 November, 14:15): the 17 droplet tests were recorded at 71.2 to 72.4 kPa, 1 to 2 kPa above 10.2 psi.
>
> **5. The word budget.** Every word a reader sees on the slide counts toward the limit of 35, except the title, which has its own limit of ten words: the line of words, the numbers in the picture, the label of the bar, the source line and the AI mark. This is stricter than the rule of `slides_outline.md`, which leaves captions, footers and source lines out. A number or a unit counts as one word; the dot between two numbers does not. Counted by code (`pmpart/fix/count_words.py` in the pm session's scratch folder): 35. To add a word, take one out. The three piles and the sentence about AI no longer fit on the slide; they are in the speaker note and in the two paragraphs.

## The slide

- **Title (10 words):** From 13.47 TB to 398 files that name your tests
- **Other title (10 words):** 0.77% of NASA's 13.47 TB names tests inside our ranges
- **Words on the slide (6 words):** Lunar habitat: code follows NASA's identifiers.
- **Numbers in the picture (15 words):** 60,866 files · 13.47 TB / 398 · 104.4 GB / 316 · 86.9 MB / 17 · 15 kB / archives 96.49%
- **Source line under the picture (9 words):** Team computation, not NASA's. PSI listing, 14 November 2026.
- **Mark on the slide (footer, small type; 5 words):** Built with AI assistance (Claude)
- **Speaker note (60 words):** NASA's archive holds 13.47 terabytes for 24 investigations; 96 percent is zip archives. We do not process it. For a lunar habitat, 26 microgravity tests sit inside our oxygen and pressure ranges. 398 files name them; 316 are not archives or video. Code read the 17 test sheets, 15 kilobytes, against NASA's table. No AI model runs in the chain.

Visible words besides the title: 6 + 15 + 9 + 5 = 35. In the "Numbers in the picture" line the slashes separate the five pieces of text and are not on the slide.

On the titles. "Your tests" and "our ranges" stand for the tests recorded inside the oxygen and pressure ranges the team set for an environment; the numbers are those of the lunar habitat, which the line of words names. Two earlier titles are not used: "names the lunar tests" reads as tests run at lunar conditions, and "names tests at lunar-base atmospheres", proposed by the checking session, comes too close to "in the lunar-habitat atmosphere", which the decision of 14 November, 14:15 rules out for the 17 droplet tests.

## The picture

Built in the slide tool from the numbers below; it is not a capture of the page. Two parts side by side: four stacked boxes on the left (about two thirds of the width) and one bar on the right. The only text in the picture is the 15 words listed above.

### Left: four boxes, from the archive down to the test sheets

Four boxes of equal size, stacked from top to bottom and joined by down arrows, in one colour that gets darker downwards. Each box holds one line: a count of files, the dot, a size. Only the first box carries the word "files". The boxes are equal on purpose. A funnel with shrinking widths would not be to scale and would need a caption that says so, and the word budget has no room for it. To scale, every box below the first would be invisible: the second is 0.77% of the bytes of the first, the third 0.00064%, the fourth about one part in 877 million.

| Box | Text in the box | What the box is (not written on the slide) |
|---|---|---|
| 1 | 60,866 files · 13.47 TB | NASA's PSI archive for the 24 combustion investigations (listing of 14 November 2026) |
| 2 | 398 · 104.4 GB | Files whose name carries the identifier or the test number of one of the 26 tests recorded inside the oxygen and pressure ranges of the lunar habitat; 0.77% of the bytes |
| 3 | 316 · 86.9 MB | Of these, the files that are not a `.zip` archive or a `.ts` video recording |
| 4 | 17 · 15 kB | The test sheets of the 17 counted droplet tests, one sheet per test |

What leads from one box to the next (for the speaker; not written on the slide):

- from 1 to 2: a join on the labels NASA wrote, from the file listing alone; nothing downloaded;
- from 2 to 3: by file extension; `.zip` and `.ts` files are set aside (82 files, 104.3 GB);
- from 3 to 4: the one sheet per test that states its conditions and result.

### Right: the archive by kind of file

One vertical stacked bar, to scale, with three segments. One label stands beside the largest segment: "archives 96.49%". The other two segments carry no text; the third is a hairline.

| Segment (for drawing the bar) | Files | Bytes | Share of the bytes | Text on the slide |
|---|---|---|---|---|
| Archives (.zip) | 12,689 | 13.00 TB | 96.49% | archives 96.49% |
| Video | 2,623 | 426.1 GB | 3.16% | none |
| All other kinds | 45,554 | 46.4 GB | 0.34% | none |

Kinds are read from file names and PSI categories. No file was opened for this bar.

### Taken off the slide on 15 November, and where it is now

By the checking session's count, the first version of the slide carried about 376 visible words, most of them labels, captions and tables of the picture. They are off the slide:

| Text of the first version | Where it is now |
|---|---|
| What each band is, and the labels between the bands | The table and the list above, for whoever builds the picture; the speaker note; the first paragraph below |
| The callout on the 17 test sheets (identifier 17 of 17; a number for 3, 0.00 for 1, nan for 7) | The first paragraph below |
| The caption on the 26 tests and on what a file name does not show | The first paragraph below |
| The list of kinds of file and the label on the experimental tables | The first paragraph below, as three shares and one sentence on the experimental tables; the six smaller kinds are no longer used |
| The three piles and "No AI in the chain" in the line of words | The piles: the first paragraph below. The sentence, corrected to "No AI model runs in the chain": the speaker note and the second paragraph |

## Two paragraphs for "Project Details"

**Finding the raw data a question needs.** Most of NASA's PSI combustion archive is raw files: 60,866 files and 13.47 TB for 24 investigations (PSI's file listing of 14 November 2026). By file name and PSI category, 96.49% of the bytes are zip archives and 3.16% are video; all other kinds together are 0.34%. PSI's experimental tables are 22 files of 0.2 MB, about one part in 64 million of the bytes, and the team's 1,824 tests come from 14 of them. We do not process the archive. For a chosen environment and fire-safety question, code follows five links. It takes the conditions and outcomes the question needs. It places every recorded test: inside the environment's oxygen and pressure ranges, outside by a recorded value, oxygen recorded for an oxidizer stream, or not placeable from the tables. It says where each needed value is: in a table cell, in a raw file that was read, in a raw file where only a column header was seen, as on-screen text of a video, in a document sentence, or not found in the files opened. For the two demo environments, it ties each test inside the ranges to the PSI files whose names carry its NASA identifier or test number. The build plan does this for five investigations (PSI-69, PSI-159, PSI-10, PSI-25 and PSI-99); today a prototype does it for the lunar habitat. A link counts as agreed only when two labels name the same test. It adds the bytes and the smallest reading step. The page then shows three piles per question: in NASA's tables; in the archive, not in a table; and no record in PSI (listing of 14 November 2026), each with its ground. For a lunar habitat, 26 tests are recorded inside the ranges: 17 fuel-droplet tests at 71.2 to 72.4 kPa, which is 1 to 2 kPa above 10.2 psi, and 9 gas flames at 50.7 kPa, all in microgravity. From the file listing alone, with nothing downloaded, 398 files (104.4 GB, 0.77% of the bytes) name one of these tests; 316 of them are not zip archives or .ts video recordings (86.9 MB). A file that names a test is not shown to hold what a question needs. Code read the 17 test sheets of the counted droplet tests (15 kB) against NASA's table: the identifier inside equals the table's in 17 of 17, and where the table has no number for the extinction diameter (11 tests) the sheet writes a number for 3, 0.00 for 1 and nan for 7. These values are shown as read from NASA's file, not adopted and not counted. For solid fuels the same page says something different: all 133 tests counted for the flammability limit have their oxygen in NASA's table, between 13.6 and 22.2%, below the 30% of this environment. That gap is not unprocessed data: PSI's tables (listing of 14 November 2026) hold no counted flammability-limit test inside this environment's oxygen range.

**The fields it draws on, and where AI is.** The chain uses established methods from six fields. Database research: a catalogue built after the fact from name patterns, exact-key joins that need two agreeing labels, and reading only a file's head or an archive's directory by HTTP range request; the directories of 18 archives of 8 kB to 32.9 GB were read without a download. Information retrieval: a value is looked up by the header text as NASA wrote it, with no embeddings and no ranking by a model. Sampling: every statement about raw files carries "n of N files opened", a small file group is read whole instead of sampled, and a person's spot check gets an exact bound. Decision theory: what to read first is a fixed, published rule over target tests and bytes, with no probabilities. Combustion science: which conditions and outcomes each question needs, units converted as written, and the caveats that a droplet is not a solid material and that microgravity is not lunar gravity. Archive practice: the FAIR principles, NASA's SPD-41a and ISA-Tab as the frame, and the source, the bytes read and the checker on every row. No AI model runs in the chain: placement, links, piles, reading order and every sentence are code and fixed templates, and nothing is generated when the page loads. AI was used around it: AI coding sessions (Claude Code) wrote the code and drafted this text, an earlier AI reading of file headers is kept with its label, and a second AI session recomputes the numbers with separate code. Read by a person: none yet. Review by combustion researchers is a next step. The counts are the team's computation, not NASA's conclusions, and the page is a research exploration tool, not safety guidance.

## Numbers used

Each number was recounted from the file named, on 15 November 2026, by the session that wrote the first version (script `pmpart/verify_numbers.py` in the pm session's scratch folder), by the checking session, and again by the correcting session (`pmpart/fix/confirm.py`). Every number on the slide is in `design.md` section 9.

| Number | Value | File |
|---|---|---|
| Archive | 60,866 files; 13,471,850,126,356 bytes; 24 investigations; listing fetched 2026-11-14T05:57:17Z | `data/pipeline/raw_inventory.json` `_meta.totals` |
| Archives (.zip) | 12,689 files; 12,999,389,379,194 bytes; 96.49% | same, `by_kind.archive` |
| Video | 2,623 files; 426,053,691,302 bytes; 3.16% | same, `by_kind.video` |
| All other kinds | 45,554 files; 46,407,055,860 bytes; 0.34% | same, sum of the six other kinds of `by_kind` |
| Experimental tables | 22 files; 211,116 bytes; 0.0000016% of the bytes, 1 part in 63,812,549 | same, `by_kind.experimental_table` |
| Experimental tables read into the team's tests | 14 of the 22 files; 1,824 tests | `data/pipeline/tests.csv` (`source_file`); `pipeline/spec/sources.json` |
| Tests inside the lunar ranges | 26: 17 of PSI-69 (liquid, 71.2341 to 72.3674 kPa), 9 of PSI-159 (gas, 50.665 kPa); all microgravity in the team's mapping | `data/pipeline/scenario_tests.csv`, `tests.csv` |
| Tests inside the ISS ranges | 179: PSI-10 71, PSI-69 56, PSI-159 27, PSI-39 25 (named in the box for the team lead only) | `data/pipeline/scenario_tests.csv`, `tests.csv` |
| 10.2 psi | 70.3 kPa; the 17 tests lie 0.9 to 2.1 kPa above it | `pipeline/spec/scenarios.json` (`lunar_habitat`, nominal pressure); `tests.csv` |
| Files naming those tests | 398 files; 104,358,456,350 bytes; 0.7746% of the archive | `docs/raw_data_design/prototype/lunar_links_PSI-69.json` (299 files; 24,954,842,492 bytes), `lunar_links_PSI-159.json` (99 files; 79,403,613,858 bytes) |
| Not an archive or a video recording | 316 files; 86,853,632 bytes | same (`not_zip` 252 files, 31,656,460 bytes; `other` 64 files, 55,197,172 bytes) |
| Archives and video recordings | 82 files; 104,271,602,718 bytes | same (`zip` 47; `zip_or_ts` 35) |
| Test sheets of the 17 tests | 17 files; 15,369 bytes; 11,871 bytes read by the design job | `lunar_links_PSI-69.json` `per_test.*.testsheet`; `tiers/testsheets_read.json` of the design job (not in the repository) |
| Sheet against table | identifier 17 of 17; table without a number 11 tests: sheet number 3, `0.00` 1, `nan` 7 | `tiers/testsheets_vs_table.json` of the design job (not in the repository); after step 4 `data/pipeline/raw_values_effect.json` |
| Counted tests, flammability limit | 133 (125 PSI-25, 8 PSI-99); oxygen 13.6 to 22.2% | `data/pipeline/need_tests.csv`, `tests.csv` |
| Solid-fuel tests with a recorded oxygen value | 139, all between 13.6 and 22.2%; 237 more without oxygen in a table | `scenario_tests.csv`, `tests.csv` |
| Archive directories read without download | 18 archives; 8,060 bytes to 32,911,249,730 bytes | `out/zipdirs.json` (14), `net/zipdir_TPM7.json` (1), `tiers/zip_lunar_FLEX19.json` (3) of the design job |
| Shares named in the note on the four boxes | 316 files: 0.00064% of the bytes; 17 sheets: 1 part in 876,559,967 | computed from the byte counts above |

The file `lunar_links_PSI-69.json` counts 299 files for the 17 droplet tests: the files whose name carries the test number or the identifier of one of them. A second prototype file, `flex_two_label.json`, arrives at 322 (24,957,498,055 bytes) for the same 17 tests with another rule: it also takes a file in when only its PSI folder number names one of the tests, and it adds the tests up, so 15 files are counted for two tests and 8 come in through a folder number (307 distinct files; recount `pmpart/fix/two_counts.py`). The slide uses the first count; the check of step 3 decides which rule the pipeline uses.

## Sources behind the second paragraph

The methods named in the second paragraph rest on the sources of `design.md` section 13. The rows for `compliance/SOURCES.md` were handed to the pm session with this draft; they go into "References" of the submission text with their links and terms. The paragraph itself quotes no source.
