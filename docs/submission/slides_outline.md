DRAFT written by an AI assistant (Claude Code, pm role) for the team to rewrite in its own words before submitting. Brought up to date on 15 November 2026, about 16:30 KST, from the working copy of the repository (scoring config 1.5.2; the page shell on `main` since 16:03). Every number is listed at the end with its file and the way it was recounted. Checked by AI sessions; reviewed by a person: 0.

> **For the team lead.** Delete this box before use.
>
> **1. What this is.** One deck plan of seven slides, title slide included (the limit is seven). Each slide has a title that is a full-sentence claim, the words on the slide, the picture and where it comes from, and a speaker note of 60 words or fewer. The next job can build it without further decisions, except the markers below.
>
> **2. Markers left.** The team name, RAPID, came from the human lead; no person-only gap is left. `measured on 15 November 2026 on the 74 questions of the frozen set (`data/insights/assistant_eval.json`; the table is in `README.md`): the full pipeline against one model call read 94% against 84% of the scored fields correctly, planned the expected lookups in 83% against 66% of the questions, showed 0 against 36 numerals outside the cited facts and 0 against 23 sentences with verdict or advice wording, and declined 6 of 7 against 0 of 7 requests for a verdict or a prediction; the arms without the code gates and without the model checker ran on a fixed half of 38 questions, and the arm without the repeated reading was not run for time` is for a measured result of the conversational assistant, which is not final yet; fill it from `data/insights/assistant_eval.json` once the evaluation has run, never by estimate. `[NOT RECOUNTED: ...]` marks a number this job could not recount from a file. All markers are listed under "Open points".
>
> **3. Slide 6.** The earlier outline kept two versions of slide 6. The pm role now takes version A, "Four kinds of SI, each with its measured check", extended by the conversational assistant. You can still switch to version B ("Code computes every number; one local model writes cited summaries"); its plan is kept, short, under "Appendix: slide 6, version B". If the assistant markers of box 3 are not filled before you submit, retitle slide 6 "Four uses of SI and how each is checked" and write "measurement in progress" in box 3, so that the title claims no more than the slide shows.
>
> **4. Captures.** Every capture comes from the new page (app bar, summary tiles, five tabs, compact result cards); the captures in `web/media/` were taken on 14 November under the old layout and are not used. Each slide names the address to open and the element to capture (see "Captures"). Captures of the team's own page are not AI-generated images; no NASA logo appears on any slide.
>
> **5. The AI mark.** An AI assistant wrote the words and notes below. Every slide carries "Built with AI assistance (Claude)" in its footer until the team has rewritten its words.

## Rules for the whole deck

- English only. Seven slides at most. No NASA logo, flag or mission mark; nothing that implies NASA endorsement.
- Research exploration tool, not safety guidance. Counts and rankings are the team's computation, not NASA's conclusions. No prediction for untested conditions. Gravity: every test ran in microgravity. The challenge statement suggests that results at the two ends of the gravity scale could bound intermediate levels, and the deck names that suggestion. It does not treat them as bounds: in NASA drop-tower tests of three materials (Olson and Ferkul 2012, Table I), the oxygen limits at lunar gravity were lower than at both 0 g and 1 g.
- Scores are compared only within one question. Never set a score of one question against a score of another question or environment, on a slide or in a note. Compare environments by counted tests.
- The lunar gap always carries both conditions: "no counted test at 30% oxygen or more and 70.3 kPa (10.2 psi) or less". Never "no recorded test": 20 gas-flame tests are recorded there and none is counted.
- The third pile is "No record in PSI (listing of 14 November 2026)". Never "NASA did not test", "a test is missing" or "a new test is needed". A file-to-test link is "two labels agree". A file name carries "the NASA identifier or the test number". A value read from a raw file is "read from NASA's file, not adopted, not counted".
- A query without a material ranks without a fuel comparison, and the page warns so ("the fuel is not compared"). The top 3 of "lunar habitat" (droplets and gas burners) is that ranking, never "the best evidence for a habitat"; the worked example on slide 3 is therefore "lunar habitat cotton fabric".
- Published results (slide 4) are quotations of NASA documents and of the investigators' papers. Their order is a fixed rule with no weights; the team computes nothing from them and compares nothing with a criterion; a result is not carried from the condition where it was stated to another one.
- ISS, if asked: BASS-II leads (93.4); SAFFIRE-I and SAFFIRE-II are level (92.1). BASS and SAFFIRE-III also score 93.4 but rest on an assumed oxygen and pressure, so the near-tie rule lists them after the three.
- Say who checked: code and AI sessions. "Reviewed by a person: 0" stays as a count. Review by combustion researchers is said as the next step, on slide 7. Nothing may suggest that a person, a specialist or NASA reviewed or approved the work.
- No wording of the challenge statement stands in quotation marks on a slide.
- Terms, said once in plain words: microgravity is near-weightlessness; PSI (Physical Sciences Informatics) is NASA's archive of these experiments; a fire-safety question is one of six the team drafted from NASA and standards documents; a counted test is a recorded test whose investigators or a NASA document state that purpose; kPa is a unit of pressure (70.3 kPa is 10.2 psi); SI is the challenge's word for AI.

## The deck in seven titles

1. Fire Evidence Explorer shows which NASA fire tests fit what you build, and where their evidence stops.
2. NASA's combustion archive holds 13.47 TB in 60,866 files; its experimental tables are 22 small files.
3. For cotton fabric in a lunar habitat, rules show SAFFIRE-II and SAFFIRE-I closest, and ACME-BRE as the closest tested at 30% oxygen, and say why.
4. A lunar habitat has counted tests for one of six fire-safety questions; the ISS cabin has four.
5. For each question, the page shows where the data are: NASA's tables, the archive, or no record.
6. Four kinds of SI, each with its measured check.
7. The page says where the evidence stops; review by combustion researchers comes next.

The four goals, and where each is shown: (1) classify and summarise the data: slides 2 and 3, and the quoted results on slide 4; (2) extract the usable fire-safety elements: slides 4 and 5; (3) points to consider for what the user builds: slide 3; (4) whether the data are enough and what more would be needed: slides 4, 5 and 7. The differentiator, saying where the evidence stops: slides 4, 5 and 7.

## Slide 1

- **Title:** Fire Evidence Explorer shows which NASA fire tests fit what you build, and where their evidence stops.
- **Names on the slide:** Fire Evidence Explorer · Team RAPID · NASA Space Apps Challenge 2026, challenge "Flame in Freefall".
- **Words on the slide:** Type what you build and where. See the closest NASA investigations, what their recorded tests hold for six fire-safety questions, where the data are, and where the evidence stops.
- **Footer (small type):** Research exploration tool, not safety guidance. Not endorsed by NASA. Built with AI assistance (Claude).
- **Picture:** the start page of the new shell. Open https://choidol0208.github.io/NASA_RAPID/ with no query and capture from the app bar (the product name, "How it works", "Source code"; the search and "Copy link" appear there only after a query) down to the three cards Find, Compare, Interpret: the title, the notice line, the question "What are you building, and where?" and the six example buttons. It holds no score. The start page prints a phrase of the challenge statement in quotation marks (the line after the lede, starting "The challenge says"): crop that line off, or compare it with the official challenge page first. The 14 November capture `web/media/slide1_top.png` shows the old layout and is not used.
- **Speaker note (55 words):** We are team RAPID. NASA publishes its microgravity fire experiments as open data, but a designer cannot easily find, compare or interpret them. Our page starts from what you want to build. It finds the closest NASA investigations, shows what their recorded tests hold and where the data are, and says where the evidence stops.

## Slide 2

- **Title:** NASA's combustion archive holds 13.47 TB in 60,866 files; its experimental tables are 22 small files.
- **Words on the slide:** NASA PSI: 24 combustion investigations, 60,866 files, 13.47 TB (file listing of 14 November 2026). Experimental tables: 22 files, 0.2 MB. We read 14 of them into 1,824 tests. The rest are raw files and documents, tied to tests only by NASA identifiers in their names.
- **Picture:** two horizontal bars to scale, built in the slide tool.
  - Bar 1, bytes by kind of file: zip archives 96.49%, video 3.16%, all other kinds 0.34%. Label only the first segment.
  - Bar 2, files by what the name carries: a test 12,934, a test day or session 30,634, nothing 17,298.
  - Caption: "By file name and PSI category; no file opened. Team computation, not NASA's."
- **Footer:** Source: NASA PSI file listing, 14 November 2026. Built with AI assistance (Claude).
- **Speaker note (58 words):** NASA's PSI archive lists 13.47 terabytes for 24 combustion investigations. Almost all of it is zip archives and video. The tables that list tests are 22 small files; we read 14 of them into 1,824 tests. For everything else, the only link to a test is a NASA identifier in a file name. Nobody needs all of it.

## Slide 3

- **Title:** For cotton fabric in a lunar habitat, rules show SAFFIRE-II and SAFFIRE-I closest, and ACME-BRE as the closest tested at 30% oxygen, and say why.
- **Words on the slide:**
  - Input "lunar habitat cotton fabric" (the page's example button "Lunar habitat, cotton fabric"), read as: oxygen 30%, 70.3 kPa (10.2 psi) and ventilated from the lunar-habitat preset; lunar gravity and cotton fabric (a solid that chars, a thin flat sheet) from your words; purpose "prevention" by default. All shown and editable.
  - Closest of 24 investigations (match score 0 to 100, for this question only):
    - SAFFIRE-II 75.0. Why: fuel match 1.00 (SIBAL, 75% cotton, 25% fiberglass); flow match 0.90 (concurrent at 20 cm/s). Largest gap: oxygen 0.24 (tested 22.1%).
    - SAFFIRE-I 74.5. Why: the same fuel and flow matches. Largest gap: oxygen 0.22 (tested 21.5 to 21.7%).
    - ACME-BRE 62.6, tagged "tested at your oxygen". Why: oxygen match 1.00 (tested 21 to 40%); fuel match 0.50 (methane; ethylene). Largest gap: sample shape 0.20 (a porous gas burner that emulates a burning solid).
  - Third place rule: when your oxygen is not air and none of the top 3 was tested at it, the third place goes to the best result that was.
  - Points to consider: gravity: none of the three meets lunar gravity; every PSI test ran in microgravity. Oxygen and pressure: no counted test at 30% oxygen or more and 70.3 kPa (10.2 psi) or less (slide 4); the two Saffire fabrics were tested below 30% oxygen, and their pressure is a team assumption (unverified); ACME-BRE's oxygen is met and its pressure is documented in its record, not a table value. Airflow: the Saffire runs are near a ventilated cabin; ACME-BRE's is not. Fuel: the Saffire fabric matches; ACME-BRE burns gas.
- **Picture:** one capture of the new page. Open https://choidol0208.github.io/NASA_RAPID/?q=lunar%20habitat%20cotton%20fabric&tab=closest (tab "Closest investigations") and capture the summary tiles ("At a glance") and the three compact result cards of `#results` (name, match score, dimension strip, "Why", "Largest gap", cautions and tags; "Details and sources" closed): with compact cards the three fit in one capture. Optional, beside it: the section "How your input was read" (`#read`) of the same address, with "Filled in for you, not typed" (`#assumptions`) left out or cropped, because it quotes a section title of the challenge statement.
- **Footer:** Scores and order are the team's computation, not a NASA result. Built with AI assistance (Claude).
- **Speaker note (59 words):** Type lunar habitat cotton fabric. The preset fills 30 percent oxygen and 70.3 kilopascals; your words give lunar gravity and the fabric. Rules, not a language model, compare it with 41 test configurations. Two Saffire fabric tests lead; ACME-BRE follows, tested at your oxygen. A query without a material ranks without a fuel comparison, and the page says so.

## Slide 4

- **Title:** A lunar habitat has counted tests for one of six fire-safety questions; the ISS cabin has four.
- **Words on the slide:** Lunar habitat at 30% oxygen or more and 70.3 kPa or less: no counted test. Its 17 counted tests are fuel droplets at 71.2 to 72.4 kPa.
- **Picture:** a table built in the slide tool, six rows and two columns. Header: "Counted tests in the environment's range".

  | Fire-safety question | ISS cabin | Lunar habitat |
  |---|---|---|
  | Flammability limit | 55, oxygen only | 0 |
  | Ignition | 0 | 0 |
  | Flame spread and growth | 2, oxygen only | 0 |
  | Extinction conditions | 63, of which 56 with oxygen and pressure | 17 |
  | Combustion products | 45, oxygen only | 0 |
  | Smoke generation | 0 | 0 |

  "Oxygen only": the test's oxygen is in range and NASA's table records no pressure for it. Optional, small beside the table: a capture of the block "ISS and lunar habitat, side by side" (`#compare`, tab "What was found"), opened at https://choidol0208.github.io/NASA_RAPID/?q=lunar%20habitat%20cotton%20fabric#compare, only after checking that it prints the counts of the table; the 14 November capture `web/media/03_compare_iss_lunar.png` shows the old layout and is not used.
- **One line under the table (the team's count from `data/pipeline/results_summary.json`; the page itself prints one headline of counts per question under "What was found"):** Quoted results from NASA documents and the investigators' papers: 212, 168 with printed values; for the lunar habitat, 5 state its oxygen and pressure, 9 one of its conditions. Example, flame spread: "Flame base spread rate = .92 mm/s." (cotton-fiberglass fabric, simulated lunar gravity, air at normal pressure; LUCI slides, NTRS 20250010653; group "About one stated condition of this environment").
  - For the builder, not on the slide: the line is quoted from the section "What NASA's experiments and documents report, question by question" (`#results-first`, built by `web/results_first.py` from `data/pipeline/results_by_need.json`), shown first in the tab "What was found": per question a headline of counts, three quoted results open and the rest behind "Show all", the printed values, the group, the source and a CSV download. The LUCI result is a related NASA experiment, not a PSI investigation of the catalogue; it is quoted, not carried to the habitat's oxygen and pressure, and the team computes nothing from it.
- **Footer:** Team counts from NASA PSI tables, not NASA conclusions. Quoted results in their authors' words; their order is the team's fixed rule, with no weights. Every test ran in microgravity; the page does not treat that as a bound for lunar gravity (slide 7). Built with AI assistance (Claude).
- **Speaker note (59 words):** Compared by counted tests, not by scores. A test counts for a question only if its investigators or a NASA document state that purpose. ISS cabin: four of six questions, three on oxygen alone, as their tables record no pressure. Lunar habitat: one, from 17 droplet tests just above 70.3 kilopascals. Ignition and smoke: no counted test in either.

## Slide 5

- **Title:** For each question, the page shows where the data are: NASA's tables, the archive, or no record.
- **Words on the slide:** three columns for the lunar habitat, one sentence each.
  - **In NASA's tables:** extinction conditions, 17 counted droplet tests.
  - **In the archive, not in a table:** 398 files (104.4 GB, 0.77% of the bytes) carry the NASA identifier or the test number of the 26 tests inside the ranges; two labels agree for 336. The 17 test sheets were read: read from NASA's file, not adopted, not counted.
  - **No record in PSI (listing of 14 November 2026):** flammability limit; all 133 counted tests have oxygen 13.6 to 22.2% in NASA's table.
  - Under the third column, small: "This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of 14 November 2026)."
  - Strip along the bottom: Tied by name, nothing transferred: 2,623 videos (426 GB), two labels agree for 662; directories of 12,600 archives listed, 2.05 GB fetched for 12.8 TB.
- **Picture:** a capture of the section "Where the data are: in NASA's tables, in the archive, or no record" (`#piles`, built by `web/raw_piles.py`), the only section of the tab "Where the data are". Open https://choidol0208.github.io/NASA_RAPID/?q=lunar%20habitat%20cotton%20fabric&tab=data (the piles are those of the lunar-habitat environment, the same as for "lunar habitat") and capture the header lines and the blocks for extinction conditions and the flammability limit. The whole section is too tall for a slide (the ui role measured 2216 x 6983 px with both blocks open), so capture the two blocks as two crops, or build the three columns above as boxes in the slide tool; the slide works without the capture.
- **Footer:** Team computation from PSI's file listing and NASA's tables, not NASA's conclusions. Built with AI assistance (Claude).
- **Speaker note (59 words):** The page sorts each question's data into three piles. Code follows NASA's identifiers in file and folder names, without downloading the files; a link counts only where two labels agree. Videos are tied the same way. For the lunar habitat, the flammability gap is not unprocessed data: every counted test has its oxygen in NASA's table, below 30 percent.

## Slide 6 (version A, the pm role's choice)

- **Title:** Four kinds of SI, each with its measured check.
- **Words on the slide:** four boxes built in the slide tool; each box holds only its name and its numbers.
  1. **Ranking by rules (no language model):** 45 of 45 test scenarios pass (expected answers written by an AI session); the page's scorer equals Python on 106 of 106 queries.
  2. **Local language model, card summaries:** 70 sentences written, each citing NASA sentences; code gates and AI reviews removed 37; 33 shown, labelled "AI-generated".
  3. **Conversational assistant (prototype, measured):** understand, plan, look up (counts, tests and the results quoted from NASA's documents), write, check, deliver. On 74 questions the request was read correctly in 94% of the scored fields (one model call: 84%); numerals outside the cited facts: 0 (one call: 36); verdict or advice wording: 0 (one call: 23).
  4. **Video reader:** 19 BASS-II clips, 16,019 rows copied from NASA's on-screen display; none wrong in 186 frames checked by an AI session [NOT RECOUNTED: the per-frame check sheet is not in the repository; figure stated in video/README.md]. Flame timing failed; removed.
- **Footer:** Model: OpenAI gpt-oss:20b (Apache-2.0), run locally through Ollama; no paid API; the public page runs no model. Code written with Claude Code (Anthropic); every file says so. Model sentences reviewed by a second AI session: 61; by a person: 0. Built with AI assistance (Claude).
- **Picture:** none needed besides the boxes. Small: one recorded answer of the assistant with its citations, in the new layout, marked as recorded. It can be taken only when the new recording exists (the conversations are being recorded again now); until then use none, or a capture of the section "How AI is used here, and how it was checked" (`#ai-use`), which prints the sentence funnel and is now on the page of its own: https://choidol0208.github.io/NASA_RAPID/how.html#ai-use (the "How it works" button in the app bar).
- **Speaker note (59 words):** We use SI only where a check can measure it. Rules rank; no model touches a number. One local open-weight model wrote card sentences; code gates and AI reviews removed 37 of 70. The assistant chains small model steps with code checks between them. The video reader copies NASA's on-screen numbers; its flame timing failed, so we dropped it.

What each box rests on, for questions (not on the slide):

- Ranking: seven dimensions (oxygen, pressure, flow, fuel, sample shape, research purpose, diluent), weights per question type from an analytic hierarchy process over literature evidence classes (config 1.4.0), detection matched by fire signature, gas or particulate (1.5.0), compliance lines with a basis and the status "documented" (1.5.0), the near-tie rule and the day tables as summary tables (1.5.1), the warning `no_material` (1.5.2: "the fuel is not compared"). Its consistency ratio near 0 follows from the class rule (1, 3, 5); it is not a measure of judgement quality, so do not present it as one. The human lead's decisions on the review of 15 November (`scoring/METHOD.md` 1.5 and 1.8, `scoring/WEIGHTING.md` 4.2 and 6): a "decisive" condition gets a large weight, not a veto; only fuel and oxygen have a gate (below a similarity of 0.2), kept as it was, because a stricter oxygen gate would rank a gas burner first for "lunar habitat cotton fabric" (no solid test reached 30% oxygen; the counts show that absence); a documented value that is not a per-test table value keeps its full similarity and is marked "documented"; without a material the page warns that the fuel is not compared; scores are never compared across questions; the detection profile covers the smoke of materials overheated without a flame (SAME, SAME-R). For the query "lunar habitat" (no material named), FLEX stays first in 88.4% of 8,000 weightings sampled near the team's weights (`data/insights/robustness.json`, config 1.5.2); that is the sensitivity of the team's ranking to its own weights, not a probability. No sampling run exists for "lunar habitat cotton fabric", so its cards show no "Weight check" line.
- Card sentences: 5 refused by code gates, 4 removed by a first reading, 28 removed by the review (`data/insights/quality.json`).
- Assistant: the model reads the request twice and a rule parser reads it a third time; one clarifying question when they disagree; code picks the lookup tools; tools return numbered facts; the model writes sentences that cite fact numbers; code gates, then a second model pass as checker, one repair, a fixed-text fallback; at most four model calls per turn (`ai/assistant/DESIGN.md`). The checker is the same model as the writer, so its verdicts are not independent; the question set was written by an AI session and is not a benchmark (`docs/assistant/README.md`).
- Prediction test (goal 4, said on slide 7): of 9 outcome labels in NASA's tables, 1 lets a simple model beat the base rate; no model is shipped (`data/insights/model_readiness.json`).

## Slide 7

- **Title:** The page says where the evidence stops; review by combustion researchers comes next.
- **Words on the slide:**
  - Limits: microgravity tests only; no prediction for untested conditions; counts and rankings are the team's, not NASA's. Checked by code and AI sessions; reviewed by a person: 0.
  - Gravity: the challenge suggests that the two ends of the gravity scale could bound partial gravity. We do not treat them as bounds: NASA drop-tower tests found lower oxygen limits at lunar gravity than at both 0 g and 1 g, for all three materials tested (Olson and Ferkul 2012).
  - Enough for a model? 1 of 9 outcome labels passes a first test; no model shipped.
  - Next: review by combustion researchers; a person's spot check of file links; the assistant's measured results.
  - Method: on the page's "How it works" (how.html): how AI is used here and how it was checked, and how the score works.
- **Picture:** the evidence map of the lunar habitat: recorded tests on the oxygen axis by kind of fuel; the solid-fuel tests end at 22.2% oxygen, the input is marked at 30%. Open https://choidol0208.github.io/NASA_RAPID/?q=lunar%20habitat%20cotton%20fabric&tab=stops (tab "Where the evidence stops") and capture the map `#stops-map` with its caption line. The 14 November capture `web/media/04_lunar_evidence_map.png` shows the old layout and is not used. Caption: "Recorded tests by oxygen. Team plot from NASA PSI tables." Under it, the public links: https://choidol0208.github.io/NASA_RAPID/ and, for the method, https://choidol0208.github.io/NASA_RAPID/how.html
- **Footer:** Research exploration tool, not safety guidance; not endorsed by NASA. References: the NASA PSI dataset DOI on every result; the full list is on the project page. Built with AI assistance (Claude).
- **Speaker note (60 words):** This is a research exploration tool, not safety guidance. Every test here ran in microgravity. The challenge suggests the two ends of the gravity scale could bound partial gravity; NASA drop-tower tests found lower oxygen limits at lunar gravity than at both, so we do not treat them as bounds. Next: review by combustion researchers and the assistant's measured results.

## Appendix: slide 6, version B

If the team lead switches back, slide 6 becomes:

- **Title:** Code computes every number; one local model writes cited summaries.
- **Words on the slide:** Code computes every count and rank. One local open-weight model, gpt-oss:20b, wrote 70 cited sentences; 33 are shown. The assistant chains model steps with code checks. No model runs on the public page.
- **Picture:** two lanes ending in one box. Lane 1: NASA PSI tables, team code, counts, ranks and fixed sentences. Lane 2: PSI record text, gpt-oss:20b on the team's computer (70), code gates (5 refused), first reading (4 removed), review by a second AI session (28 removed), 33 shown with the label "AI-generated". End box: the public page, which calls no model.
- **Speaker note (43 words):** Code computes every count and rank. One open-weight model, run locally, wrote 70 summary sentences: code refused 5, a first reading removed 4, a second AI session removed 28, and 33 are shown, none reworded. The assistant is measured separately: on 74 questions, 94% of the scored fields read correctly against 84% for one model call, and no numeral outside the cited facts against 36.

The video reader then moves to the speaker note of slide 5.

## Backup material

For questions from judges, not part of the seven slides:

- `docs/submission/raw_data_slide.md`: the raw-data answer in full (the question chain, the three piles, the file links, the FLEX test sheets, the archive directories, the independent recount), with a backup slide and two paragraphs for "Project Details".
- `docs/submission/video_slide.md`: how the 2,623 videos are tied to tests by name, the ISS shortlist, the lunar habitat line, the video reader and its check.
- `data/pipeline/results_top.json` and `results_top.csv` (data role; rule in `pipeline/README.md` and `pipeline/spec/results.json`, key `top_five`): five quoted results to show first per scenario and question, by a fixed rule with no weights. A data deliverable; the page does not print it today (it prints `results_by_need.json`).
- The method page, https://choidol0208.github.io/NASA_RAPID/how.html: "How AI is used here, and how it was checked" and "How the score works".

## Captures

Every capture is taken from the new page (shell on `main` since 16:03) under config 1.5.2. Base address: https://choidol0208.github.io/NASA_RAPID/ (written `BASE` below; `%20` is a space). An address with `#<id>` opens the tab that holds that element; `&tab=<name>` opens a tab (`web/SHELL.md`, "Tab map"). The deck's capture script is `docs/submission/deck/capture.mjs` (another job): its lunar captures use the query "lunar habitat" today, so slide 3 needs the query "lunar habitat cotton fabric" there.

| Slide | Address | Element to capture | State |
|---|---|---|---|
| 1 | `BASE` (no query) | the start page from the app bar to the three cards Find, Compare, Interpret; crop the line that quotes the challenge statement (the line after the lede, starting "The challenge says") | To take. No score on it. |
| 3 | `BASE?q=lunar%20habitat%20cotton%20fabric&tab=closest` | the summary tiles (`#glance`) and the three compact cards of `#results`, "Details and sources" closed; optional `#read` without `#assumptions` | To take. Must show SAFFIRE-II 75.0, SAFFIRE-I 74.5, ACME-BRE 62.6. |
| 4 | `BASE?q=lunar%20habitat%20cotton%20fabric#compare` (tab "What was found") | the block "ISS and lunar habitat, side by side" | Optional. Check that it prints the counts of the slide's table. |
| 5 | `BASE?q=lunar%20habitat%20cotton%20fabric&tab=data` | `#piles`: the header lines, then the blocks for extinction conditions and the flammability limit as two crops | Wanted. The slide works with boxes instead. |
| 6 | when the new recording exists: the assistant panel (`#assistant`) on `BASE` with one recorded answer; until then `BASEhow.html#ai-use` | one recorded answer with its citations, marked as recorded; or the section "How AI is used here, and how it was checked" | Optional. The recording is running now. |
| 7 | `BASE?q=lunar%20habitat%20cotton%20fabric&tab=stops` | the evidence map `#stops-map` | To take. Check that the solid-fuel tests end at 22.2% and the input is marked at 30%. |

Not to be used: every capture in `web/media/` taken on 14 November (`slide1_top.png`, `03_compare_iss_lunar.png`, `04_lunar_evidence_map.png`, `01_iss_first_screen.png`, `02_lunar_first_screen.png`, `slide2_iss_result.png`, `demo_iss_to_lunar.gif`): they show the old layout, and the ones with scores show old ones. Images in the body of the project page must be JPG, PNG or GIF of 10 MB or less.

## Open points

1. The deck goes to `docs/submission/slides.pdf`; its public address, https://github.com/choidol0208/NASA_RAPID/blob/main/docs/submission/slides.pdf, opens only once that file is committed (not yet). Check it logged out before it goes into "Project Demo".
2. `measured on 15 November 2026 on the 74 questions of the frozen set (`data/insights/assistant_eval.json`; the table is in `README.md`): the full pipeline against one model call read 94% against 84% of the scored fields correctly, planned the expected lookups in 83% against 66% of the questions, showed 0 against 36 numerals outside the cited facts and 0 against 23 sentences with verdict or advice wording, and declined 6 of 7 against 0 of 7 requests for a verdict or a prediction; the arms without the code gates and without the model checker ran on a fixed half of 38 questions, and the arm without the repeated reading was not run for time`: slide 6, box 3.
3. `measured on 15 November 2026 on the 74 questions of the frozen set (`data/insights/assistant_eval.json`; the table is in `README.md`): the full pipeline against one model call read 94% against 84% of the scored fields correctly, planned the expected lookups in 83% against 66% of the questions, showed 0 against 36 numerals outside the cited facts and 0 against 23 sentences with verdict or advice wording, and declined 6 of 7 against 0 of 7 requests for a verdict or a prediction; the arms without the code gates and without the model checker ran on a fixed half of 38 questions, and the arm without the repeated reading was not run for time`: slide 6, box 3.
4. `measured on 15 November 2026 on the 74 questions of the frozen set (`data/insights/assistant_eval.json`; the table is in `README.md`): the full pipeline against one model call read 94% against 84% of the scored fields correctly, planned the expected lookups in 83% against 66% of the questions, showed 0 against 36 numerals outside the cited facts and 0 against 23 sentences with verdict or advice wording, and declined 6 of 7 against 0 of 7 requests for a verdict or a prediction; the arms without the code gates and without the model checker ran on a fixed half of 38 questions, and the arm without the repeated reading was not run for time`: slide 6, box 3.
5. `on 74 questions, 94% of the scored fields read correctly against 84% for one model call, and no numeral outside the cited facts against 36`: appendix, version B speaker note.
6. `[NOT RECOUNTED: the per-frame check sheet is not in the repository; figure stated in video/README.md]`: slide 6, box 4 (186 frames, none wrong). Keep the figure only with this label resolved by the team lead, or cut it to "19 clips, 16,019 rows".
7. The assistant's conversations are being recorded again now; the slide 6 picture of a recorded answer waits for that recording, and the number of recorded conversations is not on any slide until measured: the recorded conversations of `data/insights/assistant_recorded.json` (recorded again on 15 November 2026 after the fixes; only conversations whose every sentence was read against its facts are published).
8. Every capture is to be taken from the new page (see "Captures"); none of the 14 November captures is used.
9. The task's phrase "most of it unlabelled raw files" does not hold by name: 12,934 files name a test and 30,634 a test day or session; 17,298 carry neither. Slide 2 says so with the counts.
10. Slide 6: the measured values of box 3 are filled (15 November, 18:30 KST, from `data/insights/assistant_eval.json`).
11. The page section `#piles` still prints "Recount by a second AI session: not yet" (small print of `web/raw_piles.py`), although `validation/raw_chain_recount.py` reports 62 of 71 fixtures reproduced (still so in `web/raw_piles.py` at 16:12). For the ui role to correct; no slide quotes that line; crop it off the slide 5 capture.
12. "Lunar habitat cotton fabric" is not all solid fuel: its third card, ACME-BRE, is a porous gas burner that emulates a burning solid, shown third by the oxygen rule of `scoring/METHOD.md` 1.5 (by score, BASS-II 70.3, BASS 71.6 and SAFFIRE-III 71.6 come before it in "All investigations"). Slide 3 says so; say it if asked.

## Numbers used

Recounted by this job on 15 November 2026 between 16:00 and 16:30 KST with `recount_slides.py` and `recount_results.py` (read-only; in the pm session's scratch folder `texts3/`) and the scorer, unless the row says otherwise. Paths are relative to the repository root.

| Number | Slide | File | How it was recounted |
|---|---|---|---|
| 24 investigations | 1, 2, 3 | `data/pipeline/raw_inventory.json`; `data/catalog/investigations.csv` | investigations in the inventory; rows of the catalog (24) |
| six fire-safety questions | 1, 4 | `pipeline/spec/needs.json`; `data/pipeline/scenario_needs.csv` | 6 rows per scenario in `scenario_needs.csv` |
| 60,866 files; 13.47 TB (13,471,850,126,356 bytes) | 2, 5 | `data/pipeline/raw_inventory.json` `_meta.totals` | read; equal to the total of `raw_file_groups.csv` (60,866) |
| 96.49%; 3.16%; 0.34% | 2 | same, `by_kind` | archive 12,999,389,379,194 bytes; video 426,053,691,302; the six other kinds 46,407,055,860; each divided by the total |
| 22 files, 0.2 MB | 2 | same, `by_kind.experimental_table` | 22 files, 211,116 bytes |
| 14 tables; 1,824 tests | 2 | `data/pipeline/tests.csv` | rows (1,824); distinct `source_file` (14) |
| 12,934; 30,634; 17,298 | 2 | `data/pipeline/raw_file_groups.csv`; `raw_layers_summary.json` `overall.names` | sums of `files_tied_to_a_test`, `files_tied_to_a_day_or_session`, `files_not_tied`; equal in both files |
| 30%; 70.3 kPa (10.2 psi); ventilated; lunar gravity; cotton fabric; prevention | 3, 4 | `scoring.scorer.rank('lunar habitat cotton fabric')` `scenario` and `sources` | printed by the scorer: `o2_pct` 30.0, `pressure_kpa` 70.3 and `flow_state` ventilated from `preset:lunar_habitat`; `gravity` lunar, `fuel_material` cotton, `fuel_class` fabric, `fuel_phase` solid, `melt_behavior` chars, `thermal_regime` thin, `sample_geometry` flat_sheet from `text`; `concern` prevention from `default` (R7 `source_class` assumed) |
| SAFFIRE-II 75.0, SAFFIRE-I 74.5, ACME-BRE 62.6; config 1.5.2 | 3 | `scoring/scoring_config.json` (version 1.5.2); `scoring/scorer.py` | `python3 -c "from scoring import scorer; print([(r['config_id'], round(r['score'],1)) for r in scorer.rank('lunar habitat cotton fabric')['results']])"` printed `[('SAFFIRE-II-C02', 75.0), ('SAFFIRE-I-C01', 74.5), ('ACME-BRE-C01', 62.6)]`; `config_version` 1.5.2 |
| Why and Largest gap of each card | 3 | the scorer's `why` and `main_gap` per result | SAFFIRE-II: "fuel match 1.00 (fuel SIBAL (75% cotton, 25% fiberglass)); flow match 0.90 (flow concurrent at 20 cm/s)", "O2 0.24 (O2 tested 22.1%)"; SAFFIRE-I: same `why`, "O2 0.22 (O2 tested 21.5–21.7%)"; ACME-BRE: "O2 match 1.00 (O2 tested 21–40%); fuel match 0.50 (fuel methane; ethylene (100% or 50% in N2))", "sample shape 0.20 (porous_burner (regime n/a))", `complementary` "o2", page tag "tested at your oxygen" (`web/app.js` line 258) |
| third place by oxygen | 3 | `scoring/METHOD.md` 1.5, "Selection"; `rank(...)['ranking']` | rule read; in the full ranking ACME-BRE is sixth (BASS-II 70.3, BASS 71.6, SAFFIRE-III 71.6 before it) and fills third place with the warning `complementary` |
| points to consider | 3 | the scorer's `requirements` and `compliance` per result | SAFFIRE-II and SAFFIRE-I: R1 gravity not met, R2 oxygen not met (table), R3 pressure unverified (assumed; warning `fallback`, "scored as ordinary cabin air"), R4 flow near, R5 fuel met, R6 shape met; ACME-BRE: R1 not met, R2 met (table), R3 documented (record), R4 not met, R5 not met, R6 not met; top-level warning `partial_gravity` only (no `no_material`) |
| `no_material` on queries without a material | 3 note, rules | `rank('lunar habitat')`, `rank('ISS')` `warnings` | both carry `no_material`: "No material is named, so the fuel is not compared"; the "lunar habitat" top 3 is still FLEX 75.2, ACME-CFI-G 71.6, ACME-BRE 73.6 |
| 41 test configurations | 3 note | `data/catalog/configurations.csv` | rows |
| 55, 0, 2, 63 (56), 45, 0; 0, 0, 0, 17, 0, 0; four of six; one of six | 4 | `data/pipeline/scenario_needs.csv` | per need: `tests_atmosphere` + `tests_oxygen_only` + `tests_pressure_only`; needs with a sum above 0 |
| no counted test at 30% or more and 70.3 kPa or less | 4 | `tests.csv` joined to `need_tests.csv` (`objective_link` = stated) | ambient `o2_pct` >= 30 and `pressure_kpa` <= 70.3: 0. The only counted test at or below 70.3 kPa is FLEX-121 (18% oxygen, 70.17 kPa) |
| 20 recorded gas-flame tests there (deck rules) | rules | `tests.csv` | ambient `o2_pct` >= 30 and `pressure_kpa` <= 70.3: 20, all gas, 50.665 kPa, oxygen 33.2 to 39.3% |
| 17 tests; 71.2 to 72.4 kPa | 4, 5 | `scenario_tests.csv`, `need_tests.csv`, `tests.csv` | S1 counted tests with oxygen and pressure inside: 17, all PSI-69; pressure 71.2341 to 72.3674 |
| 26 tests inside the lunar ranges | 5 | `scenario_tests.csv`; `test_files.json` | `o2_match` = in and `pressure_match` = in: 26 (PSI-69 17, PSI-159 9); 26 keys in `test_files.json` |
| 398 files; 104.4 GB; 0.77%; 336 | 5 | `data/pipeline/test_files.json` `scenarios.lunar_habitat`; `file_links_summary.json` | distinct file ids over the 26 tests: 398, 104,358,456,350 bytes, 0.7746% of 13,471,850,126,356; link states 336 / 47 / 15 |
| 17 test sheets read | 5 | `data/pipeline/flex_sheet_vs_table.csv` | 17 sheets, 15,369 bytes; identifier agrees 17, pressure 16, oxygen 16 |
| 133; 13.6 to 22.2% | 5 | `need_tests.csv` (P1, stated), `tests.csv` | 133 tests (PSI-25 125, PSI-99 8); oxygen min 13.6, max 22.2 |
| 2,623 videos; 426 GB; 662 | 5 | `video/data/video_links.csv` | rows (2,623); sum of `bytes` (426,053,691,302); `link_state` = two_labels_agree (662) |
| 12,600 archive directories; 2.05 GB of 12.8 TB | 5 | `data/pipeline/archive_summary.csv` | rows (12,600); sum of `bytes_fetched` (2,053,572,781); sum of `listing_bytes` (12,808,926,048,063) |
| 212 results; 168 with printed values; lunar habitat 5 and 9 | 4 | `data/pipeline/results_summary.json` `counts`; `data/pipeline/results_by_need.json` | read: `results` 212, `results_with_printed_values` 168, `per_scenario_group.lunar_habitat` `at_environment` 5, `about_a_stated_condition` 9. Recounted from `results_by_need.json`: findings of kind `result` 212, with `printed_values` 168; distinct entries of the lunar-habitat blocks (`entries` and `entries_tagged_for_all_questions`) by group: 5, 9, 86, 112 |
| "Flame base spread rate = .92 mm/s." | 4 | `results_by_need.json` `findings["LUCI25.sibal_spread"]` | `quote` copied exactly; group `about_a_stated_condition` (matched on gravity level lunar; oxygen and pressure not stated), second entry of the lunar habitat's flame-spread block; document `ASGSR-2025-LUCI` (Ferkul, Johnston, Kralik, Liao; NTRS 20250010653; slide 19); `relation` "related NASA experiment, not a PSI investigation of this catalogue" |
| 45 of 45 | 6 | `validation/report.md` (run 15:20) | rerun by this job: `python3 -B validation/run_validation.py --report <scratch>/val_report.md`: "45/45 scenarios passed" |
| 106 of 106 | 6 | `web/parity_check.py` | run by this job: "parity: 106/106 queries identical" |
| 70; 37; 33; 5; 4; 28 | 6 | `data/insights/quality.json`; `ai/review/review_sheet.csv` | `proposed` 70, `dropped_by_gates` 5, `removed_before_review.n` 4, `removed_by_review` 28, `shipped_model_sentences` 33; 70 - 5 - 4 - 28 = 33; 37 = 5 + 4 + 28. Sheet: 61 model rows, verdicts 33 supported and 28 partly, 33 shown |
| 61; 0 | 6 | `quality.json`; `review_sheet.csv` | `reviewed_ai_session` 61, `reviewed_person` 0; sheet `reviewer_kind` ai_session for 61 of 61 |
| 19 clips; 16,019 rows | 6 | `video/settings/bass2.json`; `video/data/team_transcription_bass2_onscreen_readings/*.csv` | clips in the settings (19); CSV files (19) and their data rows (16,019) |
| 186 frames, none wrong | 6 | `video/README.md`, "How it was checked" | [NOT RECOUNTED: the per-frame check sheet is not in the repository] |
| flame timing failed | 6 | `video/README.md`, "What failed and was dropped" | read: failed its check and was removed. The slide quotes no figure; the figure in `video/README.md` (right in at most 1 of 19 clips) is [NOT RECOUNTED: stated in `video/README.md`; the brightness check is not in the repository] |
| at most four model calls per turn | 6, for questions | `ai/assistant/DESIGN.md` section 1 | read (a design limit, not a measurement) |
| 88.4% | 6, for questions | `data/insights/robustness.json` (query "lunar habitat", config 1.5.2, seed 42) | read from the run's `display_line` for FLEX; not re-run (the build rewrites `data/insights/`). The file holds runs for ISS, lunar habitat, spacesuit and Mars base only |
| 9 outcome labels; 1 passes | 6 (questions), 7 | `data/insights/model_readiness.json` | rows (9); verdicts: 1 indicative, 6 too few, 1 counts only, 1 not modelable |
| 22.2%; 30% | 7 | `tests.csv` (solid, ambient oxygen); the capture | maximum oxygen of a solid-fuel test: 22.2; input 30 |
| ISS 93.4, 92.1, 92.1; BASS and SAFFIRE-III 93.4 | rules | `scoring.scorer.rank('ISS')` | printed by the scorer; BASS and SAFFIRE-III have recorded share 0.33 and assumed oxygen and pressure |
