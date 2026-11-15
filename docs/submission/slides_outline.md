DRAFT written by an AI assistant (Claude Code, pm role) for the team to rewrite in its own words before submitting. Brought up to date on 15 November 2026, about 12:00 KST, from the working copy of the repository (scoring config 1.5.1). Every number is listed at the end with its file and the way it was recounted. Checked by AI sessions; reviewed by a person: 0.

> **For the team lead.** Delete this box before use.
>
> **1. What this is.** One deck plan of seven slides, title slide included (the limit is seven). Each slide has a title that is a full-sentence claim, the words on the slide, the picture and where it comes from, and a speaker note of 60 words or fewer. The next job can build it without further decisions, except the markers below.
>
> **2. Markers left.** `[FILL: ...]` is for what only a person can supply (none is left in this file: the team name, RAPID, came from the human lead). `[ASSISTANT-MEASURED: ...]` is for a measured result of the conversational assistant, which is not final yet; fill it from `data/insights/assistant_eval.json` once the evaluation has run, never by estimate. `[NOT RECOUNTED: ...]` marks a number this job could not recount from a file. All markers are listed under "Open points".
>
> **3. Slide 6.** The earlier outline kept two versions of slide 6. The pm role now takes version A, "Four kinds of SI, each with its measured check", extended by the conversational assistant. You can still switch to version B ("Code computes every number; one local model writes cited summaries"); its plan is kept, short, under "Appendix: slide 6, version B". If the assistant markers of box 3 are not filled before you submit, retitle slide 6 "Four uses of SI and how each is checked" and write "measurement in progress" in box 3, so that the title claims no more than the slide shows.
>
> **4. Captures.** Every capture in `web/media/` was taken on 14 November, before scoring config 1.5.1. A capture that shows a score shows an old one, so slides 3 and 5 need new captures (see "Captures"). Captures of the team's own page are not AI-generated images; no NASA logo appears on any slide.
>
> **5. The AI mark.** An AI assistant wrote the words and notes below. Every slide carries "Built with AI assistance (Claude)" in its footer until the team has rewritten its words.

## Rules for the whole deck

- English only. Seven slides at most. No NASA logo, flag or mission mark; nothing that implies NASA endorsement.
- Research exploration tool, not safety guidance. Counts and rankings are the team's computation, not NASA's conclusions. No prediction for untested conditions. Results at 0 g and 1 g are not bounds for lunar or Martian gravity.
- Scores are compared only within one question. Never set a score of one question against a score of another question or environment, on a slide or in a note. Compare environments by counted tests.
- The lunar gap always carries both conditions: "no counted test at 30% oxygen or more and 70.3 kPa (10.2 psi) or less". Never "no recorded test": 20 gas-flame tests are recorded there and none is counted.
- The third pile is "No record in PSI (listing of 14 November 2026)". Never "NASA did not test", "a test is missing" or "a new test is needed". A file-to-test link is "two labels agree". A file name carries "the NASA identifier or the test number". A value read from a raw file is "read from NASA's file, not adopted, not counted".
- ISS, if asked: BASS-II leads (93.4); SAFFIRE-I and SAFFIRE-II are level (92.1). BASS and SAFFIRE-III also score 93.4 but rest on an assumed oxygen and pressure, so the near-tie rule lists them after the three.
- Say who checked: code and AI sessions. "Reviewed by a person: 0" stays as a count. Review by combustion researchers is said as the next step, on slide 7. Nothing may suggest that a person, a specialist or NASA reviewed or approved the work.
- No wording of the challenge statement stands in quotation marks on a slide.
- Terms, said once in plain words: microgravity is near-weightlessness; PSI (Physical Sciences Informatics) is NASA's archive of these experiments; a fire-safety question is one of six the team drafted from NASA and standards documents; a counted test is a recorded test whose investigators or a NASA document state that purpose; kPa is a unit of pressure (70.3 kPa is 10.2 psi); SI is the challenge's word for AI.

## The deck in seven titles

1. Fire Evidence Explorer shows which NASA fire tests fit what you build, and where their evidence stops.
2. NASA's combustion archive holds 13.47 TB in 60,866 files; its experimental tables are 22 small files.
3. For a lunar habitat, rules rank FLEX, ACME-CFI-G and ACME-BRE closest, and say why.
4. A lunar habitat has counted tests for one of six fire-safety questions; the ISS cabin has four.
5. For each question, the page shows where the data are: NASA's tables, the archive, or no record.
6. Four kinds of SI, each with its measured check.
7. The page says where the evidence stops; review by combustion researchers comes next.

The four goals, and where each is shown: (1) classify and summarise the data: slides 2 and 3; (2) extract the usable fire-safety elements: slides 4 and 5; (3) points to consider for what the user builds: slide 3; (4) whether the data are enough and what more would be needed: slides 4, 5 and 7. The differentiator, saying where the evidence stops: slides 4, 5 and 7.

## Slide 1

- **Title:** Fire Evidence Explorer shows which NASA fire tests fit what you build, and where their evidence stops.
- **Names on the slide:** Fire Evidence Explorer · Team RAPID · NASA Space Apps Challenge 2026, challenge "Flame in Freefall".
- **Words on the slide:** Type what you build and where. See the closest NASA investigations, what their recorded tests hold for six fire-safety questions, where the data are, and where the evidence stops.
- **Footer (small type):** Research exploration tool, not safety guidance. Not endorsed by NASA. Built with AI assistance (Claude).
- **Picture:** the top of the public page: title, notice line, the question "What are you building, and where?" and the six example buttons. File `web/media/slide1_top.png` (2560 x 1084; it holds no score, so config 1.5.1 does not change it). Check it against the live page before use, and retake it with the ui role's `web/capture_media.mjs` if the top has changed. The capture prints a phrase of the challenge statement in quotation marks: crop that line off, or compare it with the official challenge page first.
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

- **Title:** For a lunar habitat, rules rank FLEX, ACME-CFI-G and ACME-BRE closest, and say why.
- **Words on the slide:**
  - Input "lunar habitat", read as: oxygen 30%, 70.3 kPa (10.2 psi) and ventilated from the preset; lunar gravity from your words; all shown and editable.
  - Closest of 24 investigations (team score 0 to 100, for this question only): FLEX 75.2 · ACME-CFI-G 71.6 · ACME-BRE 73.6. Within 3 points, the larger share of recorded values goes first, then the stronger evidence.
  - Points to consider: gravity: all tests ran in microgravity, none at lunar gravity; oxygen and pressure: no counted test at 30% oxygen or more and 70.3 kPa (10.2 psi) or less (slide 4); ACME-BRE's pressure is documented in its record, not a table value; airflow: none of the three matches a ventilated cabin.
- **Picture:** a capture of the first three result cards for the query "lunar habitat" under config 1.5.1 (page section "Closest NASA investigations", `#top`), with the page's note that scores and order are the team's computation, the reason line ("Why") and the largest gap of each card. Not in `web/media/` yet: ask the ui role for `slide3_lunar_result.png`, defined like `slide2_iss_result.png` in `web/capture_media.mjs` but for "lunar habitat" and the first three cards.
- **Footer:** Scores and order are the team's computation, not a NASA result. Built with AI assistance (Claude).
- **Speaker note (59 words):** Type lunar habitat. The page fills 30 percent oxygen and 70.3 kilopascals from a preset and shows it. Rules, not a language model, compare the input with 41 test configurations. FLEX ranks first. ACME-CFI-G precedes ACME-BRE: within three points, with equal shares of recorded values, stronger evidence goes first. Each card names its reason, largest gap and dataset DOI.

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

  "Oxygen only": the test's oxygen is in range and NASA's table records no pressure for it. Optional, small beside the table: `web/media/03_compare_iss_lunar.png` (page section "ISS and lunar habitat, side by side", `#compare`), only after checking that the page still prints the same counts; retake it if not.
- **Footer:** Team counts from NASA PSI tables, not NASA conclusions. Microgravity results are not bounds for lunar gravity. Built with AI assistance (Claude).
- **Speaker note (59 words):** Compared by counted tests, not by scores. A test counts for a question only if its investigators or a NASA document state that purpose. ISS cabin: four of six questions, three on oxygen alone, as their tables record no pressure. Lunar habitat: one, from 17 droplet tests just above 70.3 kilopascals. Ignition and smoke: no counted test in either.

## Slide 5

- **Title:** For each question, the page shows where the data are: NASA's tables, the archive, or no record.
- **Words on the slide:** three columns for the lunar habitat, one sentence each.
  - **In NASA's tables:** extinction conditions, 17 counted droplet tests.
  - **In the archive, not in a table:** 398 files (104.4 GB, 0.77% of the bytes) carry the NASA identifier or the test number of the 26 tests inside the ranges; two labels agree for 336. The 17 test sheets were read: read from NASA's file, not adopted, not counted.
  - **No record in PSI (listing of 14 November 2026):** flammability limit; all 133 counted tests have oxygen 13.6 to 22.2% in NASA's table.
  - Under the third column, small: "This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of 14 November 2026)."
  - Strip along the bottom: Tied by name, nothing transferred: 2,623 videos (426 GB), two labels agree for 662; directories of 12,600 archives listed, 2.05 GB fetched for 12.8 TB.
- **Picture:** a capture of the page section "Where the data are: in NASA's tables, in the archive, or no record" (`#piles`, built by `web/raw_piles.py`) for "lunar habitat", with the header lines and the blocks for extinction conditions and the flammability limit. Not in `web/media/` yet: ask the ui role for `slide5_lunar_piles.png`. If it does not arrive, build the three columns above as boxes in the slide tool; the slide works without the capture.
- **Footer:** Team computation from PSI's file listing and NASA's tables, not NASA's conclusions. Built with AI assistance (Claude).
- **Speaker note (59 words):** The page sorts each question's data into three piles. Code follows NASA's identifiers in file and folder names, without downloading the files; a link counts only where two labels agree. Videos are tied the same way. For the lunar habitat, the flammability gap is not unprocessed data: every counted test has its oxygen in NASA's table, below 30 percent.

## Slide 6 (version A, the pm role's choice)

- **Title:** Four kinds of SI, each with its measured check.
- **Words on the slide:** four boxes built in the slide tool; each box holds only its name and its numbers.
  1. **Ranking by rules (no language model):** 43 of 43 test scenarios pass (expected answers written by an AI session); the page's scorer equals Python on 104 of 104 queries.
  2. **Local language model, card summaries:** 70 sentences written, each citing NASA sentences; code gates and AI reviews removed 37; 33 shown, labelled "AI-generated".
  3. **Conversational assistant (being built):** understand, plan, look up, write, check, deliver. Correct on [ASSISTANT-MEASURED: share correct, full pipeline] of [ASSISTANT-MEASURED: questions in the set] questions; one-call baseline [ASSISTANT-MEASURED: share correct, single_call arm].
  4. **Video reader:** 19 BASS-II clips, 16,019 rows copied from NASA's on-screen display; none wrong in 186 frames checked by an AI session [NOT RECOUNTED: the per-frame check sheet is not in the repository; figure stated in video/README.md]. Flame timing failed; removed.
- **Footer:** Model: OpenAI gpt-oss:20b (Apache-2.0), run locally through Ollama; no paid API; the public page runs no model. Code written with Claude Code (Anthropic); every file says so. Model sentences reviewed by a second AI session: 61; by a person: 0. Built with AI assistance (Claude).
- **Picture:** none needed besides the boxes. Optional, small: a capture of the page block "How AI is used here, and how it was checked" (`#ai-use`), which prints the sentence funnel. Not in `web/media/` and not defined in the capture script: ask the ui role for `slide6_ai_use.png`. If the page build replays recorded assistant conversations by then, a capture of one recorded answer with its citations can replace it, marked as recorded.
- **Speaker note (59 words):** We use SI only where a check can measure it. Rules rank; no model touches a number. One local open-weight model wrote card sentences; code gates and AI reviews removed 37 of 70. The assistant chains small model steps with code checks between them. The video reader copies NASA's on-screen numbers; its flame timing failed, so we dropped it.

What each box rests on, for questions (not on the slide):

- Ranking: seven dimensions (oxygen, pressure, flow, fuel, sample shape, research purpose, diluent), weights per question type from an analytic hierarchy process over literature evidence classes (config 1.4.0), detection matched by fire signature, gas or particulate (1.5.0), compliance lines with a basis and the status "documented" (1.5.0), the near-tie rule and the day tables as summary tables (1.5.1). Its consistency ratio near 0 follows from the class rule (1, 3, 5); it is not a measure of judgement quality, so do not present it as one. For the lunar habitat, FLEX stays first in 88.4% of 8,000 weightings sampled near the team's weights (`data/insights/robustness.json`); that is the sensitivity of the team's ranking to its own weights, not a probability.
- Card sentences: 5 refused by code gates, 4 removed by a first reading, 28 removed by the review (`data/insights/quality.json`).
- Assistant: the model reads the request twice and a rule parser reads it a third time; one clarifying question when they disagree; code picks the lookup tools; tools return numbered facts; the model writes sentences that cite fact numbers; code gates, then a second model pass as checker, one repair, a fixed-text fallback; at most four model calls per turn (`ai/assistant/DESIGN.md`). The checker is the same model as the writer, so its verdicts are not independent; the question set was written by an AI session and is not a benchmark (`docs/assistant/README.md`).
- Prediction test (goal 4, said on slide 7): of 9 outcome labels in NASA's tables, 1 lets a simple model beat the base rate; no model is shipped (`data/insights/model_readiness.json`).

## Slide 7

- **Title:** The page says where the evidence stops; review by combustion researchers comes next.
- **Words on the slide:**
  - Limits: microgravity tests only; no prediction for untested conditions; counts and rankings are the team's, not NASA's. Checked by code and AI sessions; reviewed by a person: 0.
  - Enough for a model? 1 of 9 outcome labels passes a first test; no model shipped.
  - Next: review by combustion researchers; a person's spot check of file links; the assistant's measured results.
- **Picture:** the evidence map for "lunar habitat": recorded tests on the oxygen axis by kind of fuel; the solid-fuel tests end at 22.2% oxygen, the input is marked at 30% (page section "Where the evidence stops", `#stops`). File `web/media/04_lunar_evidence_map.png` (2160 x 778, taken 14 November; the tests it plots did not change with config 1.5.1; check against the page before use). Caption: "Recorded tests by oxygen. Team plot from NASA PSI tables." Under it, the public link: https://choidol0208.github.io/NASA_RAPID/
- **Footer:** Research exploration tool, not safety guidance; not endorsed by NASA. References: the NASA PSI dataset DOI on every result; the full list is on the project page. Built with AI assistance (Claude).
- **Speaker note (58 words):** This is a research exploration tool, not safety guidance. Every test here ran in microgravity, so nothing bounds lunar or Martian gravity, and we predict nothing outside the tests. Only one of nine outcome labels supports even a simple model. Next: review by combustion researchers, a person's spot check of the file links, and the assistant's measured results.

## Appendix: slide 6, version B

If the team lead switches back, slide 6 becomes:

- **Title:** Code computes every number; one local model writes cited summaries.
- **Words on the slide:** Code computes every count and rank. One local open-weight model, gpt-oss:20b, wrote 70 cited sentences; 33 are shown. The assistant chains model steps with code checks. No model runs on the public page.
- **Picture:** two lanes ending in one box. Lane 1: NASA PSI tables, team code, counts, ranks and fixed sentences. Lane 2: PSI record text, gpt-oss:20b on the team's computer (70), code gates (5 refused), first reading (4 removed), review by a second AI session (28 removed), 33 shown with the label "AI-generated". End box: the public page, which calls no model.
- **Speaker note (43 words):** Code computes every count and rank. One open-weight model, run locally, wrote 70 summary sentences: code refused 5, a first reading removed 4, a second AI session removed 28, and 33 are shown, none reworded. The assistant is measured separately: [ASSISTANT-MEASURED: one-line result].

The video reader then moves to the speaker note of slide 5.

## Backup material

For questions from judges, not part of the seven slides:

- `docs/submission/raw_data_slide.md`: the raw-data answer in full (the question chain, the three piles, the file links, the FLEX test sheets, the archive directories, the independent recount), with a backup slide and two paragraphs for "Project Details".
- `docs/submission/video_slide.md`: how the 2,623 videos are tied to tests by name, the ISS shortlist, the lunar habitat line, the video reader and its check.

## Captures

| Slide | File | State |
|---|---|---|
| 1 | `web/media/slide1_top.png` | In the folder (14 November, 20:14). Holds no score. Check against the live page. |
| 3 | `slide3_lunar_result.png` | Needed. Not defined in `web/capture_media.mjs`; ask the ui role (section `#top`, query "lunar habitat", first three cards, config 1.5.1). |
| 4 | `web/media/03_compare_iss_lunar.png` | Optional. In the folder (14 November, 20:14). Retake if the page's counts or note differ. |
| 5 | `slide5_lunar_piles.png` | Wanted. Not defined; ask the ui role (section `#piles`, "lunar habitat", extinction conditions and flammability limit open). Slide works with boxes instead. |
| 6 | `slide6_ai_use.png` | Optional. Not defined; ask the ui role (section `#ai-use`). |
| 7 | `web/media/04_lunar_evidence_map.png` | In the folder (14 November, 20:14). Check against the page. |

Not to be used without a retake: `02_lunar_first_screen.png` and `01_iss_first_screen.png` (they print the config 1.1.0 top 3 and scores), `slide2_iss_result.png` (BASS-II score from before 1.5.1), and `demo_iss_to_lunar.gif` (14 November, 20:14, built by `web/capture_media.mjs` from the ISS and lunar queries before config 1.5.1, so it probably shows the old top 3s and scores; `README.md` links it: a note for the ui role and the README job). Images in the body of the project page must be JPG, PNG or GIF of 10 MB or less.

## Open points

1. The team name, RAPID, was given by the human lead on 15 November 2026 at 15:15 KST; it stands on slide 1 and in its speaker note.
2. `[ASSISTANT-MEASURED: share correct, full pipeline]`: slide 6, box 3.
3. `[ASSISTANT-MEASURED: questions in the set]`: slide 6, box 3.
4. `[ASSISTANT-MEASURED: share correct, single_call arm]`: slide 6, box 3.
5. `[ASSISTANT-MEASURED: one-line result]`: appendix, version B speaker note.
6. `[NOT RECOUNTED: the per-frame check sheet is not in the repository; figure stated in video/README.md]`: slide 6, box 4 (186 frames, none wrong). Keep the figure only with this label resolved by the team lead, or cut it to "19 clips, 16,019 rows".
7. Whether the public page replays recorded assistant conversations is open (`docs/assistant/README.md` section 4); the number of recorded conversations is not on any slide until measured: [ASSISTANT-MEASURED: number of recorded conversations].
8. Captures for slides 3 and 5 (and optionally 6) must be asked of the ui role.
9. The task's phrase "most of it unlabelled raw files" does not hold by name: 12,934 files name a test and 30,634 a test day or session; 17,298 carry neither. Slide 2 says so with the counts.
10. Slide 6 title: if the `[ASSISTANT-MEASURED ...]` markers of box 3 are not filled before submitting, retitle it "Four uses of SI and how each is checked" and write "measurement in progress" in box 3.
11. The page section `#piles` still prints "Recount by a second AI session: not yet" (small print of `web/raw_piles.py`), although `validation/raw_chain_recount.py` reports 62 of 71 fixtures reproduced. For the ui role to correct; no slide quotes that line.

## Numbers used

Recounted by this job on 15 November 2026 between 11:40 and 12:00 KST with `recount_slides.py` (read-only; in the pm session's scratch folder `subtext/`), unless the row says otherwise. Paths are relative to the repository root.

| Number | Slide | File | How it was recounted |
|---|---|---|---|
| 24 investigations | 1, 2, 3 | `data/pipeline/raw_inventory.json`; `data/catalog/investigations.csv` | investigations in the inventory; rows of the catalog (24) |
| six fire-safety questions | 1, 4 | `pipeline/spec/needs.json`; `data/pipeline/scenario_needs.csv` | 6 rows per scenario in `scenario_needs.csv` |
| 60,866 files; 13.47 TB (13,471,850,126,356 bytes) | 2, 5 | `data/pipeline/raw_inventory.json` `_meta.totals` | read; equal to the total of `raw_file_groups.csv` (60,866) |
| 96.49%; 3.16%; 0.34% | 2 | same, `by_kind` | archive 12,999,389,379,194 bytes; video 426,053,691,302; the six other kinds 46,407,055,860; each divided by the total |
| 22 files, 0.2 MB | 2 | same, `by_kind.experimental_table` | 22 files, 211,116 bytes |
| 14 tables; 1,824 tests | 2 | `data/pipeline/tests.csv` | rows (1,824); distinct `source_file` (14) |
| 12,934; 30,634; 17,298 | 2 | `data/pipeline/raw_file_groups.csv`; `raw_layers_summary.json` `overall.names` | sums of `files_tied_to_a_test`, `files_tied_to_a_day_or_session`, `files_not_tied`; equal in both files |
| 30%; 70.3 kPa (10.2 psi); lunar gravity; ventilated | 3, 4 | `scoring.scorer.rank('lunar habitat')` `scenario` and `sources` | printed by the scorer: `o2_pct`, `pressure_kpa` and `flow_state` from `preset:lunar_habitat`; `gravity` from `text` |
| FLEX 75.2, ACME-CFI-G 71.6, ACME-BRE 73.6; config 1.5.1 | 3 | `scoring/scoring_config.json` (version 1.5.1); `scoring/scorer.py` | `python3 -c "from scoring import scorer; print(scorer.rank('lunar habitat')['results'])"` |
| 3 points; recorded share first, then evidence | 3 | `scoring_config.json` `selection.tie_points` (3.0); `scoring/METHOD.md` 1.5 | read; ACME-CFI-G and ACME-BRE both have recorded share 0.67; evidence factor 0.97 against 0.95; `tie_note` on ACME-CFI-G. On the ISS query SAFFIRE-I (92.1, share 0.58) precedes BASS (93.4, share 0.33) by recorded share, both with evidence 0.97 |
| points to consider | 3 | the scorer's `compliance` per result | FLEX and ACME-CFI-G: R1 gravity not met, R2 oxygen met, R3 pressure met, R4 flow not met; ACME-BRE: R3 documented; warning `partial_gravity` |
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
| 43 of 43 | 6 | `validation/report.md` (run 10:07) | rerun by this job: `python3 -B validation/run_validation.py --report <scratch>/val_report.md`: "43/43 scenarios passed" |
| 104 of 104 | 6 | `web/parity_check.py` | run by this job: "parity: 104/104 queries identical" |
| 70; 37; 33; 5; 4; 28 | 6 | `data/insights/quality.json`; `ai/review/review_sheet.csv` | `proposed` 70, `dropped_by_gates` 5, `removed_before_review.n` 4, `removed_by_review` 28, `shipped_model_sentences` 33; 70 - 5 - 4 - 28 = 33; 37 = 5 + 4 + 28. Sheet: 61 model rows, verdicts 33 supported and 28 partly, 33 shown |
| 61; 0 | 6 | `quality.json`; `review_sheet.csv` | `reviewed_ai_session` 61, `reviewed_person` 0; sheet `reviewer_kind` ai_session for 61 of 61 |
| 19 clips; 16,019 rows | 6 | `video/settings/bass2.json`; `video/data/team_transcription_bass2_onscreen_readings/*.csv` | clips in the settings (19); CSV files (19) and their data rows (16,019) |
| 186 frames, none wrong | 6 | `video/README.md`, "How it was checked" | [NOT RECOUNTED: the per-frame check sheet is not in the repository] |
| flame timing failed | 6 | `video/README.md`, "What failed and was dropped" | read: failed its check and was removed. The slide quotes no figure; the figure in `video/README.md` (right in at most 1 of 19 clips) is [NOT RECOUNTED: stated in `video/README.md`; the brightness check is not in the repository] |
| at most four model calls per turn | 6, for questions | `ai/assistant/DESIGN.md` section 1 | read (a design limit, not a measurement) |
| 88.4% | 6, for questions | `data/insights/robustness.json` (config 1.5.1, seed 42) | read from the run's `display_line` for FLEX; not re-run (the build rewrites `data/insights/`) |
| 9 outcome labels; 1 passes | 6 (questions), 7 | `data/insights/model_readiness.json` | rows (9); verdicts: 1 indicative, 6 too few, 1 counts only, 1 not modelable |
| 22.2%; 30% | 7 | `tests.csv` (solid, ambient oxygen); the capture | maximum oxygen of a solid-fuel test: 22.2; input 30 |
| ISS 93.4, 92.1, 92.1; BASS and SAFFIRE-III 93.4 | rules | `scoring.scorer.rank('ISS')` | printed by the scorer; BASS and SAFFIRE-III have recorded share 0.33 and assumed oxygen and pressure |
