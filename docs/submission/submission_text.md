DRAFT written by an AI assistant (Claude) for the team to rewrite in its own words before submitting. Every number is listed at the end with its source.

> **For the team lead.** Delete this box before submitting.
>
> **1. Fill in.** Search for `[FILL`. Five items remain, in six places (F4 stands twice). Each needs something only a person has.
> - F1. Project Demo: the public link to the seven-slide deck. It must open without a login.
> - F2. Hardware: computer type, chip and memory of the machine that ran the language model. No owner name and no device name.
> - F3. "The team then rewrote both." Keep it only if it is true when you submit.
> - F4. The Exa search tool: maker, country, link and terms, checked on the tool's own site. With it, your decision whether the sentence on Chinese-made models belongs in the public text. F4 stands in two places: "What a language model was not allowed to do" and References, group E.
> - F5. The terms of the Researcher's Guide to Combustion Science: the team's source log asks for a recheck.
>
> **2. Choose slide 6** in `slides_outline.md`: version A, "Four AI-built parts, each with its measured check" (recommended by pm, because of your concern of 17:05 that a language model writing summaries is not a reason to remember the project), or version B, "Code computes every number; one local model writes cited summaries". Both are complete. The section "Use of SI" below fits both.
>
> **3. The three sentences most worth rewriting in your own words.**
> - The first sentence of the High-Level Summary: what the thing is.
> - The first sentence under "Benefits and who it is for": who uses it and what they can do next.
> - The first sentence under "Use of SI", "In short": the four uses of AI and their checks.
>
> **Before you submit.**
> - This draft was brought up to date at about 19:40 KST on 14 November 2026, from `main` as it stood at 19:05 (commit `7239a2e`, the integration of 19:01; the commit of 19:20 changed coordination files only). The page was built from that commit and read in a headless browser for the queries `ISS` and `lunar habitat`. The live site was not opened. No PLANNED mark is left.
> - It was corrected at about 20:15 KST for the findings of two independent AI readers. Each corrected number was confirmed in its source file in the working copy of `main` (commit `30c1301`). The page was not opened again for this pass.
> - The freeze was lifted at 19:20 and work continues. If the page or the data change after this draft, recheck the rows marked "yes" in "Numbers used"; the commands are given above that table.
> - Two passages cite the branch `data-lab`. Each ends with "(data-lab)". Open the branch logged out. If it does not open, delete both passages and group B4 of the References.
> - The repository is linked, so the two compliance logs must be in English on `main`. At 20:00 the English versions are in the pm working copy and not yet committed to `main`; the last commit still holds 63 and 59 lines with Korean text. In the working copy, `AI_USAGE_LOG.md` still quotes one Korean word in each of 2 lines. Commit the logs before submitting.
> - In the form's tool-selection field, select Claude Code, claude.ai, the Exa search tool and gpt-oss:20b (Ollama). The section "Use of SI" says where each was used.
> - The summary gives the challenge's description of the data (hard to find, harder to compare, harder yet to interpret) without quotation marks, because no file in the repository holds the challenge text word for word. To quote it, open the challenge page logged out and compare the phrase and its subject word for word.
> - The section "Use of SI" is the summary of the usage log. If you copy rows of the log itself into the form, leave out the empty "(to be decided)" row of its product table, and say who did check where a row says "Not reviewed" or "need expert review".
> - Do not submit this box, the first line, "Numbers used" or "Open points".
> - "SI" (Super Intelligence) is the challenge's word for AI. The form field is "Use of SI". The running text says "AI", as the page does. Pressures are in kPa; 70.3 kPa is 10.2 psi.

# Fire Evidence Explorer

- Final Project (public page): https://choidol0208.github.io/NASA_RAPID/
- Two example queries: https://choidol0208.github.io/NASA_RAPID/?q=ISS and https://choidol0208.github.io/NASA_RAPID/?q=lunar%20habitat
- Source code: https://github.com/choidol0208/NASA_RAPID
- Project Demo (slides): [FILL F1: public link to the seven-slide deck; it must open without a login]
- Challenge: Flame in Freefall, https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/

## High-Level Summary

Fire Evidence Explorer is a web dashboard that shows what NASA's fire experiments in microgravity (near-weightlessness) recorded for an environment you describe, and where that evidence stops.

The challenge describes NASA's combustion data as hard to find, harder to compare and harder yet to interpret. FIND ranks the 24 combustion investigations of NASA's Physical Sciences Informatics (PSI) archive against your environment. COMPARE puts 1,824 recorded tests into one table with shared columns and units. INTERPRET keeps apart what the tests showed, what standards and studies state, and where the evidence stops.

For an ISS cabin, counted tests fall in the oxygen range for four of six fire-safety questions. For a lunar habitat, for one: 17 fuel-droplet tests recorded just above 70.3 kPa (10.2 psi). At 30% oxygen or more and at or below 70.3 kPa, there is no counted test. A test counts only when the investigators or a NASA document state that purpose.

AI is used in four ways, each with a measured check. Of 70 sentences a local language model wrote, 33 are shown.

It is a research exploration tool, not safety guidance. Counts and rankings are the team's computation, not NASA's conclusions.

## Project Details

### What it does

Fire Evidence Explorer is one web page of fixed files, with no server program behind it. It loads its own data files and calls no language model.

Words used below, each explained once:

- **Microgravity**: near-weightlessness, as on the International Space Station (ISS). A flame there has no buoyancy: hot gas does not rise away from it.
- **PSI**: Physical Sciences Informatics, the archive where NASA publishes the data of these experiments. An **investigation** is one experiment programme in PSI, for example BASS-II or FLEX. A **test** is one run of an experiment: one row of a NASA table.
- **kPa**: kilopascal, a unit of pressure. Air at sea level has 21% oxygen at 101.3 kPa (14.7 psi).
- **Need**: one fire-safety question a designer asks, for example "down to what oxygen level does this material keep burning?". The page works with six needs.
- **Counted test**: a test that the page counts for a need. The rule is under Step 2.

You type what you are building and where. Rough input is fine, for example "moon cotton fabric" or "30% O2 at 10.2 psi". Six buttons give ready examples: "ISS cabin", "Lunar habitat", "Lunar habitat, cotton fabric", "Smoke detection on the ISS", "Spacesuit" and "Mars base".

The page first shows how it read your input. Each condition is marked as typed by you, taken from a preset, or a default. Words that match nothing in PSI are named, so you know they changed nothing. For an environment with lunar or Martian gravity, the page warns that PSI holds no partial-gravity combustion data.

Then the page answers in three steps.

**Step 1. FIND: the information you need.**

- Three result cards, for the closest of the 24 PSI combustion investigations.
- On each card: a team score from 0 to 100, the closest test configuration, the similarity on each dimension, why it matched and the largest gap.
- Links to the PSI page, the dataset DOI (the permanent identifier that PSI asks users to cite), the source table and the catalog row.
- One line that says which raw data files the PSI archive lists for the investigation, for example videos, archives and sensor tables. The team counted them from PSI's file listing.
- For the four example environments, a "Weight check" line: how often the result keeps its place when the team's weights are drawn at random.
- "What the record says": the objective as summarised in the team's catalog, the findings stated in the record or table, a short written summary, and NASA's own sentences, each quoted with the name of the record field it comes from.
- The written summary is labelled as AI-generated, with the model's name and with who checked it. Every sentence of it cites the NASA sentences it rests on. 20 of the 24 cards carry such a summary. The other 4 show NASA's sentences only.
- A full ranking of all 24 investigations, folded.
- For the ISS cabin and the lunar habitat, downloads: the matched tests (CSV), an evidence package (JSON), all recorded tests (CSV), every value with its source column (CSV) and the list of dataset DOIs to cite.

**Step 2. COMPARE: the points to consider.**

The page works with six fire-safety information needs:

- Prevention: flammability limit; ignition; flame spread and growth.
- Suppression: extinction conditions (when does a flame go out).
- Detection: combustion products; smoke generation conditions.

The six needs were written with an AI assistant (Claude Code) from NASA standards and studies, under the team's direction. The list is the team's, not NASA's.

One rule decides what is counted. A test counts for a need only when the investigators or a NASA project document state that need as a purpose of the experiment. A test that records the right values without such a statement is marked "Outside stated objective" and is not counted. Below, "counted test" always has this meaning.

The page shows:

- A table with one row per ranked investigation and one column per need. Each cell says whether the PSI table records the conditions and the outcome that the need asks for.
- For the ISS cabin and the lunar habitat, for each need: how many counted tests fall in the range of the environment, and what such a count means.
- For the same two environments, a side-by-side block. Each count links to its row in the team's data file.
- For the same two environments, the section "Recorded tests in the scenario range". Each count there opens a list of test ids. Each test id links to its row in the repository copy of the NASA PSI table.

Counts per environment exist for these two environments only. For any other input, the page still ranks the investigations and shows the needs table, the criteria list and the grids.

**Step 3. INTERPRET: the constraints.**

A constraint here is something a designer has to take into account. The page sets no design limit of its own and judges no test against a criterion.

For the ISS cabin and the lunar habitat, the page goes need by need. Each need opens into four parts, kept apart:

1. **What NASA's recorded tests showed.** Code computes these values from the PSI tables, for example how many tests ended in each recorded way. Each value comes with its number of tests and a note that says what the value is and what it is not. These are observed values. They are not limits, thresholds or requirements.
2. **Criteria in NASA documents.** What NASA standards and studies state for the need, in two lists: criteria, requirements and definitions; and questions and research needs named in the documents. Each item carries a tag (criterion or stated gap), its document and the place in it, with a link where the entry has one. The wording of each item was transcribed with an AI assistant.
3. **Published by NASA and the investigators (not in PSI's experimental tables).** Results and caveats from papers and reports, quoted with the document and with how much of it was read. They are quotes. They are never counted as tests.
4. **Where the evidence stops for this need.** The gaps in oxygen, pressure and gravity, the statements in documents that something is not known, and the searches that found nothing.

The sentences that frame these four parts are fixed sentences written by code. The product's language model wrote none of them.

Then, for all needs together, the section "Where the evidence stops" shows:

- An evidence map. It puts gas flames, fuel droplets and solid fuels on one oxygen axis. Each dot is one or more recorded tests. Your input is marked on it.
- A list, "What PSI does not contain for this environment". Each entry names the data that would close the gap.
- Grids of the recorded tests by oxygen and pressure for each fuel phase (gas, liquid, solid), with your input marked. A cell with no tests is a gap in the data, and the page shows it as such.

Near the end, the block "How AI is used here, and how it was checked" prints the measured counts that are given under "Use of SI" below.

### A worked example: an ISS cabin and a lunar habitat

Everything below is an observation about the recorded tests in PSI's open tables on 14 November 2026. Nothing below is a limit, a prediction or a safety verdict.

**The input.** You press "Lunar habitat". The challenge statement expects lunar oxygen likely at 30% or more, with a pressure of 70.3 kPa (10.2 psi) or less. The page counts tests against its own lunar range: 30 to 36% oxygen and a pressure below 85.8 kPa. The edges of this range are the team's choice. Gravity is reported next to the count and does not change it.

**FIND.** The three result cards are ACME-BRE (team score 79.1), FLEX (79.1) and ACME-CFI-G (76.1). ACME-BRE and FLEX are level: a tie, not an order. The page warns that PSI has no partial-gravity combustion data. All results are microgravity tests. They are not bounds for lunar gravity.

**COMPARE.** Counted tests fall in the lunar range for 1 of the 6 needs: extinction conditions. They are 17 tests of the FLEX investigation, which burned single droplets of liquid fuel. They were recorded at 30.0% or 34.0% oxygen and at 71.2 to 72.4 kPa. That is about 1 to 2 kPa above 70.3 kPa. For the other five needs there is no counted test in the range.

Now press "ISS cabin". The page's ISS-cabin range is 19 to 23% oxygen and 85.8 to below 116.8 kPa. The three result cards are BASS-II (team score 94), BASS (94) and SAFFIRE-II (92.7). BASS-II and BASS are level with a fourth investigation, SAFFIRE-III; the page says so and lists SAFFIRE-III under "Other investigations". Counted tests fall in the range for 4 of the 6 needs:

| Need | ISS cabin | Lunar habitat |
|---|---|---|
| Flammability limit | 55 tests, on oxygen alone | 0 |
| Ignition | 0 | 0 |
| Flame spread and growth | 2 tests, on oxygen alone | 0 |
| Extinction conditions | 63 tests, 56 of them on oxygen and pressure | 17 tests, at 71.2 to 72.4 kPa |
| Combustion products | 45 tests, on oxygen alone | 0 |
| Smoke generation conditions | 0 | 0 |

For the ISS cabin, too, the match is partial. For three of the four needs the tests match on oxygen alone, because their tables record no pressure.

**INTERPRET, what the recorded tests showed.** The 17 lunar-range tests burned droplets of methanol (9 tests) or heptane (8 tests). The FLEX table records how each test ended: "disruption" for 15 tests and "completion" for 2. The table does not define these words, so the page does not interpret them. These values describe the tests that were run.

**INTERPRET, criteria in NASA documents.** For the flammability need, the page lists 34 items under "Criteria, requirements and definitions". By the item types in the team's reference file, they are 21 definitions, 8 requirements, 3 recommendations, 1 acceptance criterion and 1 design value. 20 come from NASA documents (standards, a technical brief and reports), 7 from ISO and ASTM standards and 7 from papers. One of the documents is NASA-STD-6001B, NASA's standard on flammability, offgassing and compatibility requirements and test procedures. The page does not compare the 17 tests with any of these items.

**INTERPRET, published outside PSI's tables.** Table 1 of a paper on the later Saffire-VI flight lists the test conditions of five solid-fuel samples of the Saffire IV to VI flights. Two of them, both of Saffire VI, are at about 30 to 31% oxygen and about 54 kPa. These flights are not in PSI. The page quotes these two rows of the paper's table as published conditions and counts neither.

**INTERPRET, where the evidence stops.**

- No counted test was recorded at 30% oxygen or more and at or below 70.3 kPa.
- Recorded there, but not counted: 20 gas-flame tests of the ACME CFI-G investigation, at 33 to 39% surrounding oxygen and 50.7 kPa. For 18 of them the table records how the test ended, but no investigator or NASA project document that was read states a fire-safety purpose for the experiment. The other 2 record no such outcome. The page's grid for gas flames shows all 20.
- None of the 376 solid-fuel tests records a pressure.
- 139 solid-fuel tests record the surrounding oxygen. The highest value is 22.2%. None is at 30% or more.
- All 1,824 recorded tests were run in microgravity. None was run at lunar or Martian gravity.
- Ignition and smoke generation conditions have no counted test at all.

The page does not say what would happen in these conditions. It shows which recorded tests exist there, and which of them are counted.

### How it works

**Data pipeline.** Written specifications (JSON files) say which column of each PSI table maps to which standard variable, by which rule and in which unit. Code then reads 14 tables of 12 investigations into one table with one row per test: 1,824 tests and 18,445 values. Each value keeps its NASA source file and row. 9,226 values are read from a named column of the table. The others are facts that the mapping sets once for a whole table (6,384, for example the fuel phase or the gravity level), uniform material names (1,824) and values computed from other values (1,011). A cell that the rules cannot read stays empty with a flag and is never filled in.

**Needs and the counting rule.** Each of the six needs lists the conditions and outcomes a test must record, and says what a count means. Five of the six needs are limited to solid fuels by the team. Droplet and gas-flame tests can count for extinction conditions only. The counting rule of Step 2 then applies. The team's files hold 24 links between a need and an investigation. Each rests on a purpose sentence of the investigators or of a NASA project document, with a verdict. 15 links are marked as supported, and only these count. For example, 246 gas-flame tests were recorded at 30 to 40% surrounding oxygen, and none is counted. 92 of them record how the flame ended, but no document that was read states a fire-safety purpose for the experiment. The other 154 record no outcome that the extinction need asks for. Counted tests on 14 November: flammability limit 133, ignition 0, flame spread and growth 2, extinction conditions 298, combustion products 122, smoke generation conditions 0. These are 408 different tests, because a test can count for more than one need.

**Ranking.** Code reads your words into conditions: oxygen, pressure, flow, fuel, sample shape, research purpose and, for suppression questions, the diluent gas (a gas added to thin the air, such as carbon dioxide). It compares them with each of the 41 test configurations in the team's catalog. A configuration is a group of tests of one investigation that share a range of conditions. Each condition gets a similarity from 0 to 1. The score is a weighted sum of these, from 0 to 100. The weights depend on the type of question: prevention, detection or suppression. The score is cut by up to half when the fuel or the oxygen is far off. A factor for evidence quality is applied last. The page keeps one configuration per investigation and shows three. Scores within 3 points count as a tie and are ordered by evidence quality, and one place can go to a test run at your oxygen. No language model produces or changes a score. The full rules, with every check and its command, are in `scoring/METHOD.md`.

**Evidence packages and answer files.** For each environment, the pipeline writes one evidence package: for each need, the matched tests, their values, the gaps, the values the tests showed and the reference items. There are 6 environment packages and 20 packages for single cells of oxygen and pressure. The need-by-need text of Step 3 comes from answer files that code writes from the same tables and from 211 published statements, each tagged by the conditions its own words state. The page offers the ISS-cabin and lunar-habitat packages as JSON, next to a CSV of the matched tests (246 and 30 tests on 14 November) and the list of dataset DOIs.

**Which steps follow a published definition.** On a separate branch of the repository, the decisions that the data pipeline and the code of that branch make were counted: reading a cell, converting a unit, matching a test to an environment, counting, and so on. Of 130 decisions, 53 follow a published definition, 52 are team rules and 25 are judgements made when the rules were written. Of the 53, 45 are elementary mathematics such as counting, and 8 follow a named outside definition, for example a unit conversion factor. This is a count of the pipeline's own decisions, not a quality score. It was recomputed by a second AI agent. Reviewed by a person: 0. Files: `pipeline/lab/model_map.md` on the branch `data-lab`. (data-lab)

### How the solution evolved

The numbers in this text were tested during the day, and several of them changed.

- **The test count fell from 1,867 to 1,824.** Three audits by separate AI agents recomputed the counts from NASA's raw tables without the pipeline, and compared quotations with the documents. They found cells that had been read wrongly. A flame spread rate of 4.0 mm/s was in fact the cell "Note 4". Fan settings had been read as air speed. One maintenance row and 42 rows that repeat an earlier row had been counted as tests.
- **One need was removed.** "Exploration atmosphere" was a seventh need. It is a condition that applies to every need, and counting it as a need doubled the same tests. Six needs remain.
- **The link rule moved to stated purposes.** After a check of the literature, a test counts for a need only when a sentence of the investigators or of a NASA project document states that purpose. The counted tests changed: flammability limit from 136 to 133, flame spread from 11 to 2, extinction from 299 to 298, combustion products from 0 to 122, smoke from 4 to 0.
- **The lunar count got its caveat.** A review by a separate AI agent found that the 17 lunar-range tests lie 1 to 2 kPa above the 70.3 kPa of the challenge statement. The page now says so wherever it shows the count.
- **28 of 61 model-written sentences were removed.** A second AI session read the 61 model sentences that had passed the code checks and the first reading. It marked 28 as only partly supported by the NASA text. They are not shown.
- **A video signal failed and was dropped.** An automatic flame-out time from picture brightness was right in at most 1 of 19 clips. Only the reading of on-screen numbers was kept.

The team reads these changes as evidence that the numbers were tested: each check could fail, and some did.

**The checks that were run.** The checks in the table were run on 14 November 2026, by code or by AI sessions. The publishing workflow stops if the unit tests, the ranking test cases, the integration check or the Python-and-browser comparison fails.

| Check | Result | What it does not show |
|---|---|---|
| Unit tests of the ranking code | 39 of 39 pass | That the rules are right; only that the code follows them |
| Ranking test cases with an expected answer | 38 of 38 give the expected answer | The expected answers were written by an AI session for the team |
| Same ranking in Python and in the browser | 99 of 99 queries identical | Correctness; only that the two versions agree |
| Each weight moved by 0.05 up and down | First place unchanged in 5 of 5 scenarios | Larger changes |
| Each prevention weight halved and raised by half, on four demo queries (ISS, lunar habitat, and each with cotton fabric) | 45 of 48 variants keep the same top three in the same order; 1 keeps the same three in another order; 2 change one of the three; first place never changes | Other queries |
| Each other ranking value halved and raised by half, on the same four demo queries | 129 of 136 runs keep the same top three in the same order; first place changes in 3; the queries "ISS" and "lunar habitat" never change | Other queries |
| 8,000 random weightings near the team's weights, for each of four example environments: ISS, lunar habitat, spacesuit, Mars base (and 8,000 more with no preference) | Lunar habitat: ACME-BRE and FLEX are level in every draw and first together in 96%; ACME-CFI-G is among the first three in 85.6%. ISS cabin: BASS-II, BASS and SAFFIRE-III are level in every draw | That the weights are right; only how much the result depends on them |
| Ranking rules against one combustion textbook (Turns, 2012) | Each rule was compared for direction and form. The textbook does not cover flame spread over solid materials; those rules rest on the PSI records and the investigators' papers | The size of each value, which is the team's choice |
| Catalog values against the NASA sources | 107 of 115 ranking values are written in the source; 8 are the team's readings; 24 of 24 range ends match; 135 of 135 numbers in shown text are written in the source | That each number's meaning was checked |
| Pipeline outputs recomputed by separate code | 59 of 59 checks pass | The checker is AI-written code, like the pipeline |
| Page against data | For 11 queries, all 33 top-three results reach their data with 0 broken joins; all 1,824 test links point at an existing row of the repository copy of a NASA PSI table | Queries outside the 11 |
| Model-written sentences | 70 written; 5 refused by code checks; 4 removed by a first reading; 28 removed by the review; 33 shown. Reviewed by a second AI session: 61. Reviewed by a person: 0 | That a shown sentence is the best summary; only that it rests on the NASA sentences it cites |
| Code-written sentences and NASA quotes on the page | 226 of 226 code-written sentences read by a second AI session and marked as worded correctly; of 102 quoted NASA sentences, 10 were marked not relevant and are not shown | One quoted sentence added later has no verdict yet. Reviewed by a person: 0 |
| Video reader | 186 frames, about 750 values compared with the picture, none wrong. The frames were read by an AI assistant | Other clips: it was checked on these 19 only |

### Benefits and who it is for

The tool is for engineers who design equipment or a habitat for a crewed spacecraft or base, and for researchers who work with NASA's combustion data: from one description they get the closest NASA experiments, the matching tests to download with their source rows and citations, and the conditions for which no counted test exists, so they know what to read first and which data are still missing.

- One description leads to the closest investigations, their data and the way to cite them.
- Tests from 14 different tables can be compared in one table with the same columns and units. Every value traces back to its NASA table row. Values read from a cell also name its column.
- What the tests showed, what documents state and where the evidence stops stay apart. A reader can tell an observed value from a stated criterion and from a gap.
- Gaps are shown as plainly as results. A reader sees which conditions have no counted test, and which data would close each gap.
- The data leave the page as CSV and JSON, so the analysis can continue in the user's own tools.

### Goals and what is next

The team set four goals. The page serves them as follows.

1. Classify and summarise the experiment data: the catalog of 24 investigations, the result cards with their summaries, and the common test table.
2. Extract the elements usable for fire safety: the six information needs, the counted tests and the values the tests showed.
3. Give the points to consider for what the user wants to build: the COMPARE step and the criteria in NASA documents.
4. Judge whether the data are sufficient and what further data are needed: the parts "Where the evidence stops" and "What PSI does not contain for this environment".

What is next:

- Next: review of the ranking rules and of the fire-safety questions by combustion researchers. Eight questions for them are written down in `scoring/PARAMETER_REVIEW.md`.
- A reading by a person of a sample of values against the cells of NASA's tables. The sample sheet is prepared (`reports/spot_check.csv`, up to 20 values per table).
- Counts per environment for more environments. The data files hold six; the page shows two.
- The video reader on another experiment. That needs a new settings file and new character templates, not new reading code. It has not been tried on another experiment, and its download step has not been run from the repository.
- New PSI data. The pipeline is re-run with the same commands. One command lists what is new in PSI (`scripts/psi_whats_new.py`). Detection on a schedule is a design only.

### Tools, languages, hardware and software

- Languages: Python 3 (mostly the standard library), JavaScript (ES modules, no framework), HTML and CSS.
- Data work: pandas. NumPy and scikit-learn are used in the analysis scripts of the AI layer; NumPy also in the video reader. No trained predictor ships in the product.
- Checks and media: Node.js (comparison of the Python and browser rankings), Playwright with Chromium (page checks and screenshots), FFmpeg (the demo GIF, and decoding the video clips), Pillow (tests of the video reader).
- Other libraries: openpyxl (one spreadsheet export); PptxGenJS, React, react-icons, sharp and Tabler Icons (one slide).
- Fonts: Atkinson Hyperlegible and Barlow Semi Condensed, from Google Fonts.
- Hosting and automation: GitHub Pages and GitHub Actions.
- Language model and its runtime: gpt-oss:20b, run locally with Ollama 0.40.16.
- AI tools used in development: Claude Code and claude.ai (Anthropic), and the Exa web-search tool inside Claude Code.
- Data: NASA PSI, 24 combustion investigations and their 22 experimental tables; 19 video clips of one investigation; PSI's file listings.
- Hardware: one team member's own computer ran the language model. [FILL F2: computer type, chip and memory only; no owner name and no device name. No project file states the hardware.]

## Use of SI

"SI" (Super Intelligence) is the challenge's word for AI.

### In short

The project uses AI in four ways: two parts built with an AI coding assistant that run without any model (the ranking by rules and the video reader), one local language model and one prediction test. Each has a check whose result is a number on the page or in the repository.

1. **A ranking computed by rules.** No language model produces or changes a score. The rules were compared with a combustion textbook, the weights are the team's choice, and the ranking was tested: 38 of 38 test cases, 99 of 99 queries identical in Python and in the browser, and 8,000 random weightings for each of four example environments.
2. **One language model for short summaries.** An open-weight model, run on the team's own computer, wrote 70 sentences. Every sentence cites the NASA sentences it rests on. 33 are shown.
3. **A test of whether a prediction model could be trained on these tables at all.** Nine outcomes were tried. One passed a first test. No model is shipped.
4. **A reader that copies the numbers NASA's videos show on screen into tables.** 19 clips. About 750 values were compared with the picture, and none was wrong.

Besides these four, most of the repository's code, data specifications and coordination text were written with an AI coding assistant, under the direction of the team's human leads. The checks named here were made by code and by AI sessions. Reviewed by a person: 0 of the model-written sentences. The public page calls no model.

### 1. The ranking: rules, not a language model

- What it is: the weighted comparison described under "How it works". Code computes every score.
- Where the rules come from: each rule was compared with one combustion textbook (Turns, 2012) for its direction and its form. Two rules were changed after that comparison, at the human lead's request: oxygen is compared on a ratio scale, and diluent gases by their heat capacity. The textbook does not cover flame spread over solid materials. The rules for sample shape, thickness and flow direction rest on the PSI records and the investigators' papers.
- What is the team's choice: the weights and the size of every other value. The team kept them as they are after an AI review of each value (`scoring/PARAMETER_REVIEW.md`). Review by combustion researchers is the next step.
- How it was tested: 39 of 39 unit tests; 38 of 38 test cases with an expected answer; first place unchanged in 5 of 5 scenarios when each weight moves by 0.05; 45 of 48 variants keep the same top three in order when each prevention weight is halved or raised by half on four demo queries (ISS, lunar habitat, and each with cotton fabric); the same ranking in Python and in the browser for 99 of 99 queries.
- 8,000 random weightings: for each of four example environments (ISS, lunar habitat, spacesuit, Mars base), the weights were drawn 8,000 times near the team's weights and 8,000 times with no preference. Each result card shows the outcome as its "Weight check" line. For the lunar habitat, ACME-BRE and FLEX are level in every draw and first together in 96% of the draws near the team's weights; ACME-CFI-G is among the first three in 85.6%. For the ISS cabin, BASS-II, BASS and SAFFIRE-III are level in every draw: a tie, not an order.

### 2. The language model: short summaries, each sentence cited

- Model: gpt-oss:20b by OpenAI, an open-weight model under the Apache-2.0 licence. "Open-weight" means that the model's files can be downloaded and run on one's own computer. It ran locally through Ollama 0.40.16 before publishing. The public page calls no model.
- Role: it writes at most three summary sentences for each investigation card. Each sentence must cite numbered sentences of the PSI record. Code splits the 24 records into these numbered sentences first.
- Single entry point: one gateway file handles every model call. It refuses any other model, checks the installed model's digest, checks each reply against a fixed format and logs each call.
- Code checks: code checks every model sentence for its cited sentence numbers, its quoted source text, numbers, names, advice wording, prediction wording, known misconceptions, length and hedge words.
- Shown or not shown: no reader, human or AI, rewords a model sentence. A sentence marked as not supported, as partly supported or as having lost a hedge is removed. Its place shows the NASA sentence it cited, unless the review also left that quote out.
- The funnel: 70 sentences written by the model; 5 refused by the code checks; 4 removed by a first reading (an AI session of the pm role); 28 removed by the review (a second AI session, of the data role); 33 shown. Of the 70, 14 failed a code check at first. The model was asked again for 13 of them, and 9 then passed.
- Who read them: reviewed by a second AI session: 61. Reviewed by a person: 0. The review sheet records the kind of reviewer, and an AI session is never recorded as a person.
- NASA quotes: the review also read the NASA sentences that the cards quote. 10 were marked not relevant and are not shown.
- On the page: 20 cards carry a model-written summary and 4 show NASA's sentences only. The label reads "AI-generated, reviewed by second AI session (data role)" with the model name. NASA text is tagged with its record field, for example "Stated objective". Team counts are tagged "Computed by team code from NASA PSI tables".

### 3. Could a prediction model be trained on these tables at all?

- The question: do NASA's tables hold enough tests to train a model that predicts an outcome? For each outcome column, code asked whether a simple model beats a plain guess (the average) on recorded test conditions held out from its training.
- The rule was fixed in code before any number was computed: at least 100 tests, at least 20 groups of conditions, then a five-fold test in which repeat tests of one condition are never split between training and testing.
- Outcomes tried: nine.
- Verdicts: one outcome passed. For the FLEX droplet tests that ended in extinction, a simple model estimates the ratio of the droplet's size at extinction to its size at the start better than the average does on held-out test conditions inside the table's recorded ranges (mean error 0.126 against 0.1875, 157 tests in 65 groups of conditions). The page calls this "indicative", nothing more. Six outcomes have too few tests or groups. One is listed with its counts only. One cannot be modelled: flow events in BASS-II are noted only when they happened, and an empty cell is not a "no".
- Shipped: counts, recorded ranges, errors and verdicts in words. No fitted model, coefficient or model output is shipped, and none is offered for any condition. As the page says: "None is a cabin-material flammability model."

### 4. The video reader: numbers NASA shows on screen, copied into tables

- What it is: NASA's BASS-II videos show five readings as text on the picture: FUEL, AIR, FAN, RAD and a clock. NASA's ReadMe says that fan voltage and duct flow are "on the video display". As far as the PSI files the team holds show, PSI has no numeric log of these readings. The reader copies them into a table, one row per second, for 19 clips (16,019 rows).
- How it reads: each character cell is compared with 33 stored character templates. A value is written only when every character of the field was read. Otherwise the cell stays empty. It is pattern matching, not a language model.
- The check: 186 frames (80 random and 106 hard cases), about 750 values compared with the picture, none wrong. The frames were read by an AI assistant. It was checked on these 19 clips only.
- What failed: an automatic flame-out time from picture brightness was right in at most 1 of 19 clips. It was removed. No flame-out time, ignition time, burn duration or flow speed at blowoff is derived.
- Where it is: the folder `video/` of the repository, with the command, the settings, the tests and the 19 tables. It is a transcription of NASA's display, not a NASA data file. Nothing from it enters a ranking, a count or a scenario text. The page names it in one labelled sentence on the BASS-II card.

### AI in development

Tools:

- Claude Code (Anthropic) with Claude models. The team's usage log records them as Claude Opus 5.5, Opus-family, Sonnet-family and Fable 5.2 agents. Several sessions ran in parallel, one per team role (pm, data, ui, catalog). They often used sub-agents and separate review agents.
- Claude (Opus) in claude.ai chat sessions. These designed and extracted the first catalog and wrote the first ranking rules, the first test cases with their expected answers, and one slide.
- The Exa web-search tool, used inside Claude Code to find the standards and papers behind the information needs.
- gpt-oss:20b (OpenAI, Apache-2.0), run locally through Ollama 0.40.16, to write the card summaries.

What these tools wrote:

- The scripts that fetch the PSI records, tables and file listings and profile their columns.
- The specification-driven pipeline: the six information needs and their links to the experiments' purpose sentences, the standard variables, the column mappings, the scenario ranges, the indicators, the coverage grid, the evidence packages, the answer files and the separate checker.
- The reference list: the search, the reading and the record of each item with its place in the document and how much of the document was read.
- The catalog and the rule-based ranking, with its test cases, their expected answers and the review of each ranking value.
- The dashboard: the browser version of the ranking, the comparison with the Python version, the page and the publishing workflow.
- The AI layer: the model gateway, the sentence index of the PSI records, the code-written scenario text, the code checks, the evidence-map data, the model-readiness test and the weight sampling.
- The video reader in `video/`, with its settings, tests and procedure.
- Audits and reviews by separate AI agents: recomputation from the raw tables, checks of quotations against the documents, a search for over-general statements, and the review of the model-written sentences. Their findings led to the changes listed under "How the solution evolved".
- The English translation of the team's Korean working documents, compared line by line by a second agent.
- The team's coordination files and helper scripts.
- The first draft of this text and of the slide outline. [FILL F3: add "The team then rewrote both." only if that is true.]

What the human leads decided: the topic, the four goals, the FIND, COMPARE and INTERPRET frame, the main use, that constraints also come from the PSI data and stay apart from criteria in documents, the rules for model use, that values are read from video only where PSI holds no numeric file, and that the pipeline's decisions should rest on published definitions where such definitions exist. Some structures were proposed by an AI session and then accepted by the leads. One example is the four-part "what is known for an environment" structure. An AI session also listed ideas for how the project could differ. The leads chose the direction and kept the team's original topic.

How AI output is marked:

- Code: the first lines of each code file say it was written with an AI assistant (Claude). One empty file has no header. The README files say the same.
- Data: the JSON outputs of the pipeline and of the AI layer carry a field that says they were built by AI-written code and, for the AI layer, which language model ran, if any. The CSV outputs are described as AI-generated in `pipeline/README.md`. Every catalog row is marked "ai_extracted" until a person checks it. The reference file says it is AI-generated.
- Page: the section "How the score works" says the page, the catalog, the ranking code and the pipeline were written with an AI assistant (Claude) under the team's direction. The block "How AI is used here, and how it was checked" prints the counts given above. Model-written text carries the label "AI-generated" with the model's name and the kind of reviewer. The footer says "Built during the hackathon with AI assistance (Claude)".
- Slide: the catalog filter slide says "Built with AI assistance (Claude)" in its footer.

Who checked the work: code checks and AI sessions, as listed in the table under "How the solution evolved". The team's usage log records, entry by entry, who checked what. For the model-written sentences the count is: reviewed by a second AI session 61, reviewed by a person 0.

### What a language model was not allowed to do

- Produce or change a ranking score.
- Write a number, a count, a need statement, a gap or a scenario statement in the product.
- Run in the public page.
- Give a safe or unsafe verdict, predict an untested condition or give operational safety guidance.
- Add text that is not in the cited source.
- Be recorded as a person in a review.
- Be a model or service from a maker the team's rule excludes. The team's rule of 14 November, taken from its reading of the event's participation terms, allows no AI model or AI service made by a Chinese or Chinese-owned organisation, in development or in the product. The checks behind this: the product's model gateway (`ai/llm.py`) refuses every model except gpt-oss:20b, and the team's usage log lists only Anthropic and OpenAI models and the Exa search tool. [FILL F4: the maker and country of the Exa tool, once checked on its own site, and the decision whether this sentence belongs in the public text. Until then, write only: "The team found no AI model or AI service whose maker is Chinese or Chinese-owned."]

## Space Agency Data

### What we used

1. NASA PSI combustion investigations: 24 records and their 22 experimental tables. 23 records carry the CC0-1.0 licence. The PSI-10 record states no licence.
2. PSI's file listings for the same 24 investigations: the names, sizes and categories of 60,866 files. No raw data file was downloaded for this.
3. NASA's BASS-II videos in PSI (PSI-25): 19 of its 296 video clips.
4. Documents filed with the PSI investigations: BASS-II, BASS and FLEX documents that explain the table columns; SAME and SAME-R requirements documents and final reports; Saffire-I and Saffire-II telemetry documents and Readme.
5. NASA standards, technical briefs and reports, among them NASA-STD-6001B, NASA-STD-3001 Volume 2, OCHMO-TB-008, JSC 20584, NASA/TP-2010-216134, NASA/CP-2003-212103, NASA/TP-2015-216046 and the Researcher's Guide to Combustion Science.
6. Papers by NASA researchers and their partners, mostly from the NASA Technical Reports Server (NTRS).
7. The challenge statement on the Space Apps site.

### How each is used

- PSI records: the catalog of all 24 investigations, the ranking for a described environment, and the dataset DOIs and links on every result. The records are also the numbered sentences behind the written card summaries and the quoted NASA sentences on each card.
- PSI experimental tables: 14 tables of 12 investigations are read into one common test table with standard variables and units. Each value keeps its source file and row. From this table, code counts which recorded tests match each need and each environment, and builds the evidence map and the grids of recorded oxygen and pressure.
- PSI file listings: the line on each card that says which raw data files PSI lists for the investigation.
- BASS-II videos: the video reader copies the numbers shown on screen into tables for 19 clips. The tables are in the repository. They enter no count and no ranking.
- Standards, reports and papers: the six information needs rest on items from these documents. The page lists the items for each need, each with its type, document and link, and quotes short passages with their source. The wording of each item was transcribed with an AI assistant. The page never judges a test against a criterion.
- Challenge statement: the lunar-habitat preset (oxygen likely 30% or more at 10.2 psi or less) and the spacesuit preset (100% oxygen at 4.3 psi), the warning that PSI holds no partial-gravity data, and the FIND, COMPARE and INTERPRET frame.

### How the data shaped the project

- The challenge text says the data are hard to find, harder to compare and harder yet to interpret. That gave the three steps of the page.
- The tables differ in columns, units and notes. That led to the common test table and to a written column mapping for each table, so every value can be traced to its table row.
- Counted tests fall in range for 4 of 6 needs for an ISS cabin, for 3 of them on oxygen alone, and for 1 of 6 for the lunar range. That contrast became the main thing the page shows: where the evidence stops. No counted test was recorded at 30% oxygen or more and at or below 70.3 kPa (10.2 psi). The 17 counted droplet tests lie about 1 to 2 kPa above that pressure.
- The records and the investigators' papers state each experiment's purpose. That led to the counting rule: a test counts for a need only when that need is a stated purpose of the experiment.
- Every test in the common test table was run in microgravity. So the page warns that there are no partial-gravity data. Results at 0 g and 1 g are not bounds for lunar or Martian gravity.
- For BASS-II, PSI holds videos and no numeric log of the readings shown on screen. That led to the video reader.

## References

Grouped as: A. NASA data; B. NASA and other documents; C. software libraries and fonts; D. models; E. tools and services. Each line gives the link, the licence or terms, and where the item is used. The page's own computations (scores, counts, bins) are the team's, not NASA's.

### A. NASA data: Physical Sciences Informatics (PSI)

PSI asks users to cite each investigation by its DOI. Portal: NASA Physical Sciences Informatics (PSI), https://psi.nasa.gov/ . NASA Biological and Physical Sciences. Used: the 24 combustion investigation records (JSON) and their 22 experimental tables (CSV), fetched on 14 November 2026 by scripts/fetch_psi.py into data/psi/.

- PSI-10 ACME/Flame Design, Advanced Combustion via Microgravity Experiments / Flame Design. NASA Physical Sciences Informatics (PSI), record version 1. https://doi.org/10.60555/w4zy-bt45. Licence: none stated (the licence field of the PSI record is empty). Use: record and 2 experimental tables: catalog, ranking, and its tests in the common test table.
- PSI-20 ACME BRE, Advanced Combustion via Microgravity Experiments - Burning Rate Emulator. NASA Physical Sciences Informatics (PSI), record version 4. https://doi.org/10.60555/vb93-3y72. Licence: CC0-1.0. Use: record and 1 experimental table: catalog and ranking (table not in the common test table).
- PSI-21 ACME CLD Flame, Advanced Combustion via Microgravity Experiments / Coflow Laminar Diffusion Flame. NASA Physical Sciences Informatics (PSI), record version 4. https://doi.org/10.60555/23e1-9950. Licence: CC0-1.0. Use: record and 1 experimental table: catalog and ranking (table not in the common test table).
- PSI-22 ACME E-FIELD Flames, Advanced Combustion via Microgravity Experiments Electric-Field Effects on Laminar Diffusion Flames. NASA Physical Sciences Informatics (PSI), record version 7. https://doi.org/10.60555/se5a-8c73. Licence: CC0-1.0. Use: record and 1 experimental table: catalog and ranking (table not in the common test table).
- PSI-23 ACME s-Flame, Advanced Combustion via Microgravity Experiments-Structure and Response of Spherical Diffusion Flames. NASA Physical Sciences Informatics (PSI), record version 4. https://doi.org/10.60555/k57n-p030. Licence: CC0-1.0. Use: record and 1 experimental table: catalog and ranking (table not in the common test table).
- PSI-25 BASS-II, Burning and Suppression of Solids - II. NASA Physical Sciences Informatics (PSI), record version 4. https://doi.org/10.60555/4qc4-de67. Licence: CC0-1.0. Use: record and 1 experimental table: catalog, ranking, and its tests in the common test table.
- PSI-26 BASS, Burning and Suppression of Solids. NASA Physical Sciences Informatics (PSI), record version 4. https://doi.org/10.60555/58h4-dy80. Licence: CC0-1.0. Use: record and 1 experimental table: catalog, ranking, and its tests in the common test table.
- PSI-39 CFI, Cool Flames Investigation. NASA Physical Sciences Informatics (PSI), record version 4. https://doi.org/10.60555/m6pj-a914. Licence: CC0-1.0. Use: record and 1 experimental table: catalog, ranking, and its tests in the common test table.
- PSI-47 DAFT / DAFT-2, Dust and Aerosol Measurement Feasibility Test / Dust and Aerosol Measurement Feasibility Test-2. NASA Physical Sciences Informatics (PSI), record version 5. https://doi.org/10.60555/ztgj-d202. Licence: CC0-1.0. Use: record and 1 experimental table: catalog and ranking (table not in the common test table).
- PSI-60 Computational and Experimental Analysis of SPICE Data Sets. NASA Physical Sciences Informatics (PSI), record version 1. https://doi.org/10.60555/mzjm-yv57. Licence: CC0-1.0. Use: record only (no experimental table): catalog and ranking.
- PSI-62 Concurrent Flame Spread Modeling using Flamelet Generated Manifolds in Microgravity with Comparison to BASS Experiments using Two-Color Tomography. NASA Physical Sciences Informatics (PSI), record version 1. https://doi.org/10.60555/e9xp-ex83. Licence: CC0-1.0. Use: record only (no experimental table): catalog and ranking.
- PSI-68 FLEX-2, Flame Extinguishment Experiment - 2. NASA Physical Sciences Informatics (PSI), record version 6. https://doi.org/10.60555/byp8-h018. Licence: CC0-1.0. Use: record and 1 experimental table: catalog and ranking (table not in the common test table).
- PSI-69 FLEX, Flame Extinguishment Experiment. NASA Physical Sciences Informatics (PSI), record version 5. https://doi.org/10.60555/mbq8-0451. Licence: CC0-1.0. Use: record and 1 experimental table: catalog, ranking, and its tests in the common test table.
- PSI-98 SAFFIRE-I, Spacecraft Fire Safety Experiment-I. NASA Physical Sciences Informatics (PSI), record version 4. https://doi.org/10.60555/0t15-1z43. Licence: CC0-1.0. Use: record and 1 experimental table: catalog, ranking, and its tests in the common test table.
- PSI-99 SAFFIRE-II, Spacecraft Fire Experiment-II. NASA Physical Sciences Informatics (PSI), record version 5. https://doi.org/10.60555/2chp-m469. Licence: CC0-1.0. Use: record and 1 experimental table: catalog, ranking, and its tests in the common test table.
- PSI-100 SAFFIRE-III, Spacecraft Fire Experiment-III. NASA Physical Sciences Informatics (PSI), record version 4. https://doi.org/10.60555/040q-4h36. Licence: CC0-1.0. Use: record and 1 experimental table: catalog, ranking, and its tests in the common test table.
- PSI-101 SAME-R, Smoke Aerosol Measurement Experiment-Reflight. NASA Physical Sciences Informatics (PSI), record version 4. https://doi.org/10.60555/2np7-jv14. Licence: CC0-1.0. Use: record and 1 experimental table: catalog, ranking, and its tests in the common test table.
- PSI-102 SAME, Smoke and Aerosol Measurement Experiment. NASA Physical Sciences Informatics (PSI), record version 4. https://doi.org/10.60555/gd4k-8h62. Licence: CC0-1.0. Use: record and 1 experimental table: catalog, ranking, and its tests in the common test table.
- PSI-106 SLICE, Structure and Liftoff In Combustion Experiment. NASA Physical Sciences Informatics (PSI), record version 3. https://doi.org/10.60555/pm12-rg61. Licence: CC0-1.0. Use: record and 1 experimental table: catalog and ranking (table not in the common test table).
- PSI-107 SPICE, Smoke Point In Co-flow Experiment. NASA Physical Sciences Informatics (PSI), record version 4. https://doi.org/10.60555/9kbh-e962. Licence: CC0-1.0. Use: record and 1 experimental table: catalog, ranking, and its tests in the common test table.
- PSI-115 Utilization of the Smoke Aerosol Measurement Experiment Data for Advanced Modeling and Simulation of Smoke Generation in Micro-Gravity. NASA Physical Sciences Informatics (PSI), record version 3. https://doi.org/10.60555/q0v5-1v28. Licence: CC0-1.0. Use: record only (no experimental table): catalog and ranking.
- PSI-117 Effect of External Thermo-Convective Perturbation on Cool Flame Dynamics: A Multidimensional Multi-Physics CFD Analysis. NASA Physical Sciences Informatics (PSI), record version 2. https://doi.org/10.60555/gz0q-b577. Licence: CC0-1.0. Use: record only (no experimental table): catalog and ranking.
- PSI-142 Quantitative Studies of Cool Flame Transitions at Radiation / Stretch Extinction Using Counterflow Flames. NASA Physical Sciences Informatics (PSI), record version 2. https://doi.org/10.60555/80qf-vj95. Licence: CC0-1.0. Use: record and 1 experimental table: catalog and ranking (table not in the common test table).
- PSI-159 ACME CFI-G, Advanced Combustion via Microgravity Experiments / Cool Flames Investigation with Gases. NASA Physical Sciences Informatics (PSI), record version 1. https://doi.org/10.60555/cyt1-kh64. Licence: CC0-1.0. Use: record and 2 experimental tables: catalog, ranking, and its tests in the common test table.

Other NASA data:

- PSI-25 BASS-II raw videos: 19 of the 296 MP4 files (the tests whose flame events are recorded in the table, about 1.8 GB), plus 4 science documents (ReadMe, Test Matrices, Ops, Fan calibration). https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 and https://doi.org/10.60555/4qc4-de67 . Licence: CC0-1.0 (licence field of the PSI-25 record). Use: the video reader in `video/`. The 19 clips stay outside the repository. In the repository: the team's transcription of NASA's on-screen readings (19 CSV files in `video/data/team_transcription_bass2_onscreen_readings/`) and six small strips of the text overlay cut from the frames, used as test fixtures (`video/fixtures/`). The page names the reader in one sentence on the BASS-II card.
- PSI file listings of the 24 investigations: name, size and category of each file (60,866 files). https://psi.nasa.gov/ . Licence: CC0-1.0 per investigation (the PSI-10 record states none). Use: `pipeline/raw_inventory.py` and `data/pipeline/raw_inventory.json`; the raw-data line on each result card. No raw data file was downloaded for this.
- PSI-25, PSI-26 and PSI-69 documents (BASS-II ReadMe, Test Matrices, Fan calibration data; FLEX DoD and Test Plan; BASS Planned Test Matrix and DLD). https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 (and PSI-26, PSI-69). Licence: CC0-1.0. Use: reading what the table columns mean (for example, BASS-II "Air display" is in cm/s).

### B. NASA and other documents

These are the documents behind the six information needs (`pipeline/spec/references.json`: 66 entries, one paper listed twice, so 65 references here).

- "Access" says how much of each document was read.
- For each item the page shows the team's short wording, the document and the place in it. For 47 documents it also shows short verbatim quotes with their source, in the need-by-need blocks, in scenario notes or as the note of a table cell: 25 words at most from a document that is not NASA's, and 58 words at most from a NASA document. Such a line says "Quoted on the page". No document file is redistributed.
- "Cited only" means that the page shows no verbatim text of the document.
- The needs specification in the repository keeps the verbatim quotes of the cited passages (256 quotes; 3 are longer than 40 words, all three from NASA documents).
- For 28 documents on the NASA Technical Reports Server (NTRS), the terms are those in the copyright field of the NTRS record, read on 14 November 2026.
- For 7 other documents no open licence was found or read. They are treated as copyrighted.

**B1. Documents with items shown on the page (59)**

- Flammability, Offgassing, and Compatibility Requirements and Test Procedures. NASA, NASA-STD-6001B w/Change 3 (Revision B approved 2011-08-26; Change 3 revalidated 2025-06-09, administrative change). https://standards.nasa.gov/sites/default/files/standards/NASA/B-w/CHANGE-3/3/2025_06_25_NASA-STD-6001B_w_Change_3_FINAL_Admin-Change-FINAL.pdf. Terms: Public to read; document not redistributed. Quoted on the page: 11 passages, 38 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-STD-6001B).
- Space systems - Safety and compatibility of materials - Method to determine the flammability thresholds of materials. ISO, ISO/TS 16697:2012 (status: withdrawn). https://www.iso.org/standard/57450.html. Terms: Paid standard, copyright with the publisher; only bibliographic data and text of the publisher's public catalogue page cited. Quoted on the page: 1 passage, 25 words at most. Access: abstract or catalogue page only. Use: an information need and the Constraints list on the page (specification item ISO-TS-16697).
- Standard Test Method for Measuring the Minimum Oxygen Concentration to Support Candle-Like Combustion of Plastics (Oxygen Index). ASTM International, ASTM D2863-23e1 (per Note 2, technically equivalent to ISO 4589-2 when the gas measurement and control device of 6.3.1 is used with direct oxygen concentration measurement). https://www.astm.org/d2863.html. Terms: Paid standard, copyright with the publisher; only bibliographic data and text of the publisher's public page cited. Quoted on the page: 1 passage, 15 words at most. Access: abstract or catalogue page only. Use: an information need and the Constraints list on the page (specification item ASTM-D2863).
- NASA Spaceflight Human-System Standard, Volume 2: Human Factors, Habitability, and Environmental Health. NASA Office of the Chief Health and Medical Officer, Revision F, approved 2026-07-14 (Table 6.2-3 also read in Revision E, 2025-05-01). https://standards.nasa.gov/standard/NASA/NASA-STD-3001_VOL_2. Terms: Public to read; document not redistributed. Quoted on the page: 3 passages, 30 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-STD-3001-V2).
- NASA-STD-3001 Technical Brief: Fire Protection. NASA Office of the Chief Health and Medical Officer, OCHMO-TB-008 Rev A. https://www.nasa.gov/wp-content/uploads/2023/12/ochmo-tb-008-fire-protection.pdf. Terms: US Government work, public. Quoted on the page: 8 passages, 26 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item OCHMO-TB-008).
- Spacecraft Maximum Allowable Concentrations for Airborne Contaminants. NASA JSC Toxicology, JSC 20584 Rev D, 02/2026. https://www.nasa.gov/wp-content/uploads/2026/02/jsc-20584-smacs-rev-d.pdf. Terms: US Government work, public. Access: read in full. Use: an information need and the Constraints list on the page (specification item JSC-20584).
- Recommendations for Exploration Spacecraft Internal Atmospheres: The Final Report of the NASA Exploration Atmospheres Working Group. NASA JSC, NASA/TP-2010-216134, October 2010. https://www.nasa.gov/wp-content/uploads/2023/03/henninger-8.2-34-atm-tp216134-2010.pdf. Terms: US Government work, public. Quoted on the page: 7 passages, 34 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-TP-2010-216134).
- Correlation of Normal Gravity Aerospace Materials Flammability Data with Flammability in Microgravity Environments (NASA Task Book, PI S. Olson). NASA, Task Book report, FY2022. https://taskbook.nasaprs.com/tbp/tbpdf.cfm?id=14639. Terms: US Government work, public. Access: read in full. Use: an information need and the Constraints list on the page (specification item TASKBOOK-14639).
- Flammability Limits from BASS-II Testing in Microgravity Compared to Normal Gravity Limits (Olson, Ferkul, Fernandez-Pello, Miller, Wichman, Bhattacharjee, T'ien). 49th International Conference on Environmental Systems, ICES-2019-101 (7-11 July 2019, Boston). https://hdl.handle.net/2346/84505. Terms: Copyright with publisher or authors. Quoted on the page: 7 passages, 24 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item ICES-2019-BASS2).
- Evaluating Material Flammability in Microgravity and Martian Gravity Compared to the NASA Standard Normal Gravity Test (Olson, Ferkul). AIAA / NASA GRC, AIAA 2012-3492. https://ntrs.nasa.gov/citations/20130010991. Terms: Copyright with publisher or authors. Quoted on the page: 3 passages, 25 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item NTRS-20130010991).
- Microgravity Flame Spread in Exploration Atmospheres: Pressure, Oxygen, and Velocity Effects on Opposed and Concurrent Flame Spread (Olson, Ruff, Miller). SAE, SAE Technical Paper 2008-01-2055. https://doi.org/10.4271/2008-01-2055. Terms: Copyright with publisher or authors; cited only. Access: abstract or catalogue page only. Use: an information need and the Constraints list on the page (specification item SAE-2008-01-2055).
- Research Needs in Fire Safety for the Human Exploration and Utilization of Space: Proceedings and Research Plan (Ruff, ed.). NASA GRC, NASA/CP-2003-212103. https://ntrs.nasa.gov/citations/20030053425. Terms: US Government work, public. Quoted on the page: 20 passages, 27 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-CP-2003-212103).
- The Saffire Experiment: Large-Scale Combustion aboard Spacecraft (Ferkul, Urban, Olson, Ruff, et al.). 10th U.S. National Combustion Meeting, College Park, Maryland, April 23-26, 2017, 2017. http://hdl.handle.net/20.500.11820/9397b059-72ed-41aa-8b7a-3ea8ba1bc795. Terms: Copyright with publisher or authors. Quoted on the page: 2 passages, 18 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item SAFFIRE-2017).
- Evaluation of Spacecraft Smoke Detector Performance in the Low-Gravity Environment (Meyer, Urban, Mulholland, Bryg, Yuan, Ruff, Cleary, Yang). Fire Safety Journal, 2018. https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/. Terms: Copyright with publisher or authors. Quoted on the page: 2 passages, 23 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item FSJ-2018-SAME).
- Research Requirements Document: Droplet Flame Extinguishment in Microgravity (FLEX). NASA GRC, November 4, 2005 (file name FLEX_EIRD_v4.pdf). https://www1.grc.nasa.gov/wp-content/uploads/FLEX_EIRD_v4.pdf. Terms: US Government work, public. Quoted on the page: 2 passages, 22 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item FLEX-EIRD).
- Droplet Combustion Experiments Aboard the International Space Station (Dietrich, Nayagam, Hicks, Ferkul, Dryer, et al.). Microgravity Science and Technology, 2014. https://link.springer.com/article/10.1007/s12217-014-9372-2. Terms: Copyright with publisher or authors; cited only. Access: abstract or catalogue page only. Use: an information need and the Constraints list on the page (specification item MST-2014-FLEX).
- Detailed Results From the Flame Extinguishment Experiment (FLEX) March 2009 to December 2011. NASA GRC, NASA/TP-2015-216046, November 2015. https://ntrs.nasa.gov/citations/20150023456. Terms: US Government work, public. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-TP-2015-216046).
- A Researcher's Guide to: Combustion Science. NASA ISS Program Science Office, NP-2015-10-034-JSC. https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf. Terms: US Government work, public. [FILL F5: recheck these terms; the team's source log asks for it.] Quoted on the page: 5 passages, 40 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item NP-2015-10-034-JSC).
- Results of Large-Scale Spacecraft Flammability Tests (Ferkul, Olson, Urban, Ruff, Easton, T'ien, Liao, Fernandez-Pello, Torero, Eigenbrod, Legros, Smirnov, Fujita, Rouvreau, Toth, Jomaas). 47th International Conference on Environmental Systems, ICES-2017-224 (16-20 July 2017, Charleston, South Carolina). https://hdl.handle.net/2346/73020. Terms: no licence statement read (the repository page did not open on 14 November 2026); treated as copyright with authors or publisher. Quoted on the page: 6 passages, 25 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item ICES-2017-224).
- NASA PSI, Saffire-I (PSI-98) and Saffire-II (PSI-99): telemetry graph documents, operations notes and Readme. NASA Physical Sciences Informatics (PSI), PSI-98 version 4, PSI-99 version 5 (files version 1). https://psi.nasa.gov/physci/repo/data/investigations/PSI-99. Terms: CC0-1.0 (licence fields of the PSI-98 and PSI-99 records). Quoted on the page: 1 passage, 2 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item PSI-SAFFIRE-FILES).
- Exploration Investigation Requirements Document for SAME a.k.a. Smoke Aerosol Measurement Experiment (PI D. Urban; Co-Is G. Mulholland, Z.-G. Yuan, J. Yang, T. Cleary). NASA GRC, Rev. 2.0, February 25, 2005 (PSI file PSI-102_Engineering Documents_SAME_EIRD.pdf, 72 pages). https://doi.org/10.60555/gd4k-8h62. Terms: CC0-1.0 (licence field of the PSI-102 record; file hosted on PSI). Quoted on the page: 1 passage, 48 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item SAME-EIRD-2005).
- Smoke Aerosol Measurement Experiment (SAME), Final Report, November 1, 2000 - April 14, 2009 (Urban, Ruff, Sheredy, Cleary, Yang, Mulholland, Yuan). NASA GRC, March 15, 2010 (PSI file PSI-102_Reports_SAME_Final Science Report.pdf, 68 pages; appendices B to E reprint SAE 2009-01-2468, AIAA 2009 'Properties of Smoke from Overheated Materials in Low-Gravity', SAE 2008-01-2089 and AIAA 2008 'Spacecraft Fire Detection: Smoke Properties and Transport in Low-Gravity'). https://doi.org/10.60555/gd4k-8h62. Terms: CC0-1.0 (licence field of the PSI-102 record; file hosted on PSI). Quoted on the page: 2 passages, 26 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item SAME-FSR-2010).
- Smoke Aerosol Measurement Experiment Re-flight (SAMER), Final Report, 01 November 2000 - June 2, 2014 (Urban, Ruff, Sheredy, Meyer, Cleary, Yang, Mulholland, Yuan). NASA GRC, June 2, 2014 (PSI file PSI-101_Reports_SAME-R_Final Report.pdf, 89 pages). https://doi.org/10.60555/2np7-jv14. Terms: CC0-1.0 (licence field of the PSI-101 record; file hosted on PSI). Quoted on the page: 2 passages, 31 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item SAMER-FR-2014).
- Pyrolysis Smoke Generated Under Low-Gravity Conditions (Mulholland, Meyer, Urban, Ruff, Yuan, Bryg, Cleary, Yang). Aerosol Science and Technology 49(5), 310-321, 2015. https://doi.org/10.1080/02786826.2015.1025125. Terms: journal article; licence not read on the landing page; treated as copyright with publisher or authors; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item AST-2015-PYROLYSIS).
- Final Report: Fire Prevention, Detection, and Suppression Project, Exploration Technology Development Program (Ruff). NASA GRC, NASA/TM-2011-217036, September 2011. https://ntrs.nasa.gov/citations/20110020262. Terms: NTRS marks the record as a work of the US Government, public use permitted. Quoted on the page: 2 passages, 28 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-TM-2011-217036).
- Strategic Research to Enable NASA's Exploration Missions Conference and Workshop: Presentations (Nahra, ed.); presentations 'Fire Prevention, Detection, and Suppression', 'Fire Suppression and Response' and 'Research Plan for Fire Signatures and Detection' (Ruff) and 'Organizing Questions for Reduced-Gravity Flammability' (Miller and NASA/NCMR project scientists). NASA GRC, NASA/CP-2004-213205/VOL1, August 2004 (conference of June 22-23, 2004, Cleveland). https://ntrs.nasa.gov/citations/20040142351. Terms: NTRS marks the record as a work of the US Government, public use permitted. Quoted on the page: 13 passages, 26 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-CP-2004-213205-VOL1).
- Operation and Development Status of the Spacecraft Fire Experiments (Saffire) (Ruff, Urban). 46th International Conference on Environmental Systems, 2016 (NTRS 20170000230; the paper number is not printed in the NTRS copy). https://ntrs.nasa.gov/citations/20170000230. Terms: NTRS marks the record as a work of the US Government, public use permitted. Quoted on the page: 6 passages, 25 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item ICES-2016-SAFFIRE).
- The Spacecraft Fire Experiment (Saffire) - Objectives, Development and Status (Schoren, Ruff, Urban). International Association for the Advancement of Space Safety conference, 2016, 2016 (NTRS 20170001636). https://ntrs.nasa.gov/citations/20170001636. Terms: NTRS marks the record as a work of the US Government, public use permitted. Quoted on the page: 1 passage, 20 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item IAASS-2016-SAFFIRE).
- Research Questions and Challenges for Improved Spacecraft Fire Detection (Fortenberry, Wang, Cleary, Easton, Berger, Meyer). Topical white paper submitted to the NASEM Biological and Physical Sciences Decadal Survey 2022-2032, 2021-10-31 (NTRS 20210022143). https://ntrs.nasa.gov/citations/20210022143. Terms: NTRS notes that portions may include copyright-protected material. Quoted on the page: 6 passages, 25 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item WP-2021-FIRE-DETECTION).
- Fire Safety in the Low-Gravity Spacecraft Environment (Friedman). NASA GRC, NASA/TM-1999-209285 (29th International Conference on Environmental Systems, July 1999). https://ntrs.nasa.gov/citations/19990063738. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-TM-1999-209285).
- Results from on-board CSA-CP and CDM Sensor Readings during the Burning and Suppression of Solids - II (BASS-II) Experiment in the Microgravity Science Glovebox (MSG) (Olson, Ferkul, Bhattacharjee, Miller, Fernandez-Pello, Link, T'ien, Wichman). 45th International Conference on Environmental Systems, ICES-2015-196 (12-16 July 2015, Bellevue, Washington; NTRS 20150019858). https://ntrs.nasa.gov/citations/20150019858. Terms: NTRS marks the record as public use permitted. Quoted on the page: 1 passage, 19 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item ICES-2015-196).
- Burning and Suppression of Solids-II (BASS-II) Summary Report (Olson, Ferkul, Bhattacharjee, Miller, Fernandez-Pello, Link, T'ien, Wichman). NASA GRC, NASA/TM-20210011385, October 2021. https://ntrs.nasa.gov/citations/20210011385. Terms: NTRS permits use by or on behalf of the US Government and gives no public-use statement. Quoted on the page: 8 passages, 58 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-TM-20210011385).
- Thickness and Fuel Preheating Effects on Material Flammability in Microgravity from the BASS Experiment (Ferkul, Olson, Takahashi, Endo, Johnston, T'ien). American Society for Gravitational and Space Research 2013 Annual Meeting (presentation), 2013 (NTRS 20140011099). https://ntrs.nasa.gov/citations/20140011099. Terms: NTRS marks the record as public use permitted. Quoted on the page: 1 passage, 13 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item ASGSR-2013-BASS).
- Particle Morphology and Size Results from the Smoke Aerosol Measurement Experiment-2 (Urban, Ruff, Greenberg, Fischer, Meyer, Mulholland, Yuan, Bryg, Cleary, Yang). 42nd International Conference on Environmental Systems, AIAA 2012-3536 (15-19 July 2012, San Diego; NTRS 20130000422). https://ntrs.nasa.gov/citations/20130000422. Terms: NTRS marks the record as public use permitted. Quoted on the page: 2 passages, 22 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item AIAA-2012-3536). (The specification lists this paper twice, as AIAA-2012-3536 and ICES-2012-SAME2; it is one reference here.)
- Gaseous Non-Premixed Flame Research Planned for the International Space Station (Stocker, Takahashi, Hickman, Suttles). 2014 Spring Technical Meeting of the Central States Section of the Combustion Institute, March 16-18, 2014 (NTRS 20140009169). https://ntrs.nasa.gov/citations/20140009169. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item CSSCI-2014-ACME).
- Cool-flame extinction during n-alkane droplet combustion in microgravity (Nayagam, Dietrich, Hicks, Williams). Spring Technical Meeting of the Central States Section of the Combustion Institute, March 16-18, 2014 (NTRS 20140006750); conference version of the Combustion and Flame paper listed in PSI-39. https://ntrs.nasa.gov/citations/20140006750. Terms: NTRS marks the record as public use permitted. Quoted on the page: 1 passage, 12 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item CSSCI-2014-COOLFLAME).
- Applying Flammability Limit Probabilities and the Normoxic Upward Limiting Pressure Concept to NASA STD-6001 Test 1 (Olson, Beeson, Fernandez-Pello). 44th International Conference on Environmental Systems, ICES-2014-179 (13-17 July 2014, Tucson, Arizona). https://ntrs.nasa.gov/citations/20150004099. Terms: NTRS marks the record as public use permitted. Quoted on the page: 4 passages, 23 words at most. Access: read in full. Use: an information need and the Constraints list on the page (specification item ICES-2014-179).
- Space systems - Safety and compatibility of materials - Part 1: Determination of upward flammability of materials. ISO, ISO 14624-1:2003. Link: none recorded for the entry; one item names the ISO catalogue page https://www.iso.org/standard/28953.html (status: withdrawn). Terms: Paid standard, copyright with the publisher; only bibliographic data and text of the publisher's public catalogue page cited. Quoted on the page: 1 passage, 23 words at most. Access: known only through a citation. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item ISO-14624-1).
- Evidence Report: Risk of Hypobaric Hypoxia from the Exploration Atmosphere. NASA Human Research Program, 2015. https://ntrs.nasa.gov/citations/20150021491. Terms: US Government work, public. Access: abstract or catalogue page only. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item NTRS-20150021491).
- Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data (challenge statement). NASA Space Apps Challenge, 2026. https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/. Terms: Public challenge statement. Access: read by a teammate session. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item CHALLENGE-2026).
- Preliminary Results from the Saffire VI Experiment (Urban, Ruff, Ferkul, Easton, Johnston, Owens, Olson, Fortenberry, Graf, George, Toth, Meyer, Eigenbrod, T'ien, Liao, Fernandez-Pello, Legros, Guibaud, Smirnov, Fujita, Rojas Alva, Jomaas). 53rd International Conference on Environmental Systems, ICES-2024-365 (21-25 July 2024, Louisville, Kentucky). https://ntrs.nasa.gov/citations/20240002981. Terms: NTRS public record that may include copyrighted material; only Table 1 values and its caption cited. Quoted on the page: 1 passage, 11 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item ICES-2024-365).
- Results of Large-Scale Spacecraft Flammability Tests, presentation slides (Ferkul, Olson, Urban, Ruff, Easton, T'ien, Liao, Fernandez-Pello, Torero, Eigenbrod, Legros, Smirnov, Fujita, Rouvreau, Toth, Jomaas). NASA Technical Reports Server; 47th International Conference on Environmental Systems, 2017 (36 slides). https://ntrs.nasa.gov/citations/20170008805. Terms: NTRS marks the record as public use permitted. Quoted on the page: 3 passages, 10 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item NTRS-20170008805).
- Saffire: A Novel Approach to Study of Spacecraft Fire Safety Using Un-Manned Spacecraft (Urban, Ferkul, Olson, Ruff, Easton, and the international topical team). NASA Technical Reports Server; 33rd Annual Meeting of the American Society for Gravitational and Space Research, October 25-28, 2017, 2017 (32 slides). https://ntrs.nasa.gov/citations/20180005168. Terms: NTRS marks the record as public use permitted. Quoted on the page: 1 passage, 10 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item NTRS-20180005168).
- Analysis of Saffire II two-sided concurrent flame spread over a thick PMMA slab (Olson, Urban, Ruff, Ferkul, Toth, Eigenbrod, Meyer). 48th International Conference on Environmental Systems, 2018 (ICES paper number not verified). http://hdl.handle.net/2346/74099. Terms: the repository page shows no licence statement; treated as copyright with authors or publisher. Quoted on the page: 2 passages, 16 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item ICES-2018-SAFFIRE2-PMMA).
- The effect of duct size, sample size, and fuel composition on concurrent flame spread over large cellulose samples in microgravity (Olson, Ruff, Ferkul, Owens, Easton, Liao, T'ien, Toth, Jomaas, Fernandez-Pello, Legros, Guibaud, Fujita, Smirnov, Urban). Combustion and Flame, 248 (2023) 112559; read in the accepted manuscript. https://discovery.ucl.ac.uk/id/eprint/10164340/. Terms: author accepted manuscript; the repository page refers re-use to the publisher's terms. Quoted on the page: 1 passage, 24 words at most. Access: read from an unofficial copy. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item CNF-2023-SAFFIRE).
- Fire Safety Implications of Preliminary Results from Saffire IV and V Experiments on Large Scale Spacecraft Fires (Urban, Ruff, Ferkul, Easton, et al.). 50th International Conference on Environmental Systems, ICES-2021-266 (12-15 July 2021). https://ntrs.nasa.gov/citations/20210011521. Terms: NTRS notes that portions may include copyright-protected material. Quoted on the page: 1 passage, 10 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item ICES-2021-266).
- Buoyancy Effects on Concurrent Flame Spread Over Thick PMMA (Thomsen, Fernandez-Pello, Ruff, Urban). Combustion and Flame 199 (2019) 279-291; author manuscript on the NASA Technical Reports Server, 2018 manuscript (25 pages). https://ntrs.nasa.gov/citations/20200000557. Terms: NTRS marks the record as public use permitted. Quoted on the page: 1 passage, 15 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item NTRS-20200000557).
- Topical: Recommendations for Fire Extinguisher Research for Crewed Missions (Easton, Berger, Fortenberry, Padilla). Topical white paper submitted to the Decadal Survey 2023-2032, 2021-10-31 (NTRS 20210023340). https://ntrs.nasa.gov/citations/20210023340. Terms: NTRS marks the record as public use permitted. Quoted on the page: 1 passage, 24 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item WP-2021-FIRE-EXTINGUISHER).
- Recent Research on Flames of Gaseous Fuel Aboard the International Space Station (Stocker). 33rd Japanese Conference on Microgravity Science and Application (presentation), 13-15 October 2021 (NTRS 20210022542). https://ntrs.nasa.gov/citations/20210022542. Terms: NTRS permits use by or on behalf of the US Government and gives no public-use statement; cited only. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item JASMAC-33-ACME).
- Pressure Effects on Oxygen Concentration Flammability Thresholds of Materials for Aerospace Applications (Hirsch, Williams, Beeson). NASA JSC White Sands Test Facility; preprint for the Journal of Testing and Evaluation, NTRS 20070005041, preprint headed 'Journal of Testing and Evaluation, October 2006'. https://ntrs.nasa.gov/citations/20070005041. Terms: NTRS marks the record as a work of the US Government, public use permitted. Quoted on the page: 3 passages, 25 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item JTE-2006-HIRSCH).
- Oxygen Concentration Flammability Thresholds of Selected Aerospace Materials Considered for the Constellation Program (Hirsch, Williams, Harper, Beeson, Pedley). 2nd IAASS Conference 'Space Safety in a Global World' (meeting named in the NTRS record, May 2007), NTRS 20070018178. https://ntrs.nasa.gov/citations/20070018178. Terms: NTRS marks the record as a work of the US Government, public use permitted. Quoted on the page: 1 passage, 15 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item NTRS-20070018178).
- Pressure Flammability Thresholds of Selected Aerospace Materials (Hirsch, Williams, Harper, Beeson, Ruff, Pedley). AIAA (per the NTRS record); NASA White Sands Test Facility, NTRS 20100015582, JSC-CN-20193, 2010. https://ntrs.nasa.gov/citations/20100015582. Terms: NTRS marks the record as a work of the US Government, public use permitted. Quoted on the page: 1 passage, 16 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item NTRS-20100015582).
- Selected Parametric Effects on Materials Flammability Limits (Hirsch, Juarez, Peyton, Harper, Olson). 41st International Conference on Environmental Systems (AIAA), NTRS 20110008636, JSC-CN-23164, 2011. https://ntrs.nasa.gov/citations/20110008636. Terms: NTRS marks the record as a work of the US Government, public use permitted. Quoted on the page: 3 passages, 25 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item AIAA-2011-5067).
- Bounding the Spacecraft Atmosphere Design Space for Future Exploration Missions (Lange, Perka, Duffield, Jeng). NASA JSC (Jacobs Sverdrup ESC Group), NASA/CR-2005-213689, June 2005. https://ntrs.nasa.gov/citations/20050185597. Terms: NTRS marks the record as a work of the US Government, public use permitted. Quoted on the page: 2 passages, 32 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item NASA-CR-2005-213689).
- Microgravity Flammability of PMMA Rods in Concurrent Flow (Olson, Ferkul). 9th U.S. National Combustion Meeting, Cincinnati, Ohio, May 17-20, 2015, NTRS 20150008961. https://ntrs.nasa.gov/citations/20150008961. Terms: NTRS marks the record as public use permitted. Quoted on the page: 1 passage, 15 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item NTRS-20150008961).
- On Simulating Concurrent Flame Spread in Reduced Gravity by Reducing Ambient Pressure (Thomsen, Fernandez-Pello, Urban, Ruff, Olson). Proceedings of the Combustion Institute, 37(3):3793-3800, doi 10.1016/j.proci.2018.05.004; author manuscript PMC6907022. https://pmc.ncbi.nlm.nih.gov/articles/PMC6907022/. Terms: author manuscript in PubMed Central; licence section not read; treated as copyright with publisher or authors. Quoted on the page: 2 passages, 24 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item PROCI-2018-THOMSEN).
- Buoyant Effects on the Flammability of Silicone Samples Planned for the Spacecraft Fire Experiment (Saffire) (Niehaus, Ferkul, Gokoglu, Ruff). 45th International Conference on Environmental Systems, ICES-2015-[293] (12-16 July 2015, Bellevue, Washington). https://ntrs.nasa.gov/citations/20150022421. Terms: NTRS marks the record as public use permitted. Quoted on the page: 1 passage, 19 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item ICES-2015-293).
- Large-Scale Spacecraft Fire Safety Tests (Urban, Ruff, Ferkul, Olson, Fernandez-Pello, T'ien, Torero, Cowlard, Rouvreau, Minster, Toth, Legros, Eigenbrod, Smirnov, Fujita, Jomaas). Poster; the NTRS record names the International Symposium on Combustion, San Francisco, August 2014, NTRS 20150000894, GRC-E-DAA-TN17050. https://ntrs.nasa.gov/citations/20150000894. Terms: NTRS marks the record as public use permitted. Quoted on the page: 2 passages, 25 words at most. Access: read in full. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item NTRS-20150000894).
- Standard Test Method for Measuring Liquid and Solid Material Fire Limits in Gaseous Oxidants. ASTM International, ASTM G125-00 (Reapproved 2023), as indicated by the page address g0125-00r23; edition not otherwise verified. https://www.astm.org/g0125-00r23.html. Terms: standard sold by its publisher, as ASTM D2863 above; treated as copyright with the publisher; only bibliographic data and the public catalogue page cited. Access: abstract or catalogue page only. Use: the needs specification; shown on the page as a cited item (published statements of a need, a marked atmosphere or a scenario note) (specification item ASTM-G125).

**B2. Documents in the needs specification only (6)**

- SAME Baseline Concept Description Document, SAME-DOC-001 Rev. A (ZIN Technologies for NASA GRC). NASA GRC / ZIN Technologies, Rev. A, approvals dated June 2005 (PSI file PSI-102_Science Documents_SAME_Baseline Concept Description Doc.pdf, 15 pages). https://doi.org/10.60555/gd4k-8h62. Terms: CC0-1.0 (licence field of the PSI-102 record; file hosted on PSI). Access: read in full. Use: the needs specification only, not shown on the page (specification item SAME-BCD-2005).
- Smoke Aerosol Measurement Experiment (SAME) Operations Manual, SAME-DOC-007 (ZIN Technologies for NASA GRC). NASA GRC / ZIN Technologies, January 2007 (PSI file PSI-102_Science Documents_SAME_Operations Manual_007.pdf, 33 pages). https://doi.org/10.60555/gd4k-8h62. Terms: CC0-1.0 (licence field of the PSI-102 record; file hosted on PSI). Access: read in full. Use: the needs specification only, not shown on the page (specification item SAME-OPS-2007).
- SAME Software Requirements Document, SAME-DOC-004 Rev. D (ZIN Technologies for NASA GRC). NASA GRC / ZIN Technologies, Rev. D (PSI file PSI-102_Reference Data_SAME_Software Req Document.pdf, 29 pages). https://doi.org/10.60555/gd4k-8h62. Terms: CC0-1.0 (licence field of the PSI-102 record; file hosted on PSI). Access: read in full. Use: the needs specification only, not shown on the page (specification item SAME-SRD-2005).
- Recapturing a Future for Space Exploration: Life and Physical Sciences Research for a New Era (National Research Council). National Academies Press, 2011. https://www.nationalacademies.org/read/13048/chapter/2. Terms: licence not read on the landing page; treated as copyright with the publisher; cited only. Access: abstract or catalogue page only. Use: the needs specification only, not shown on the page (specification item NRC-2011-DECADAL).
- An Overview of the Microgravity Science Glovebox (MSG) Facility and the Research Performed in the MSG on the International Space Station (ISS) (Jordan). NASA Marshall Space Flight Center, NTRS 20140011630, M13-2964 (abstract, November 2013). https://ntrs.nasa.gov/citations/20140011630. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: abstract or catalogue page only. Use: the needs specification only, not shown on the page (specification item NTRS-20140011630).
- NASA PSI, BASS-II (PSI-25) raw-data documents: SRD_BASS-II.pdf, BASS-II Procedure.docx, BASS-II data FAQ.docx, BASS-II Test Matrix by PI Final.xlsx. NASA Physical Sciences Informatics (PSI), PSI-25 version 4 (files version 1). https://psi.nasa.gov/physci/repo/data/investigations/PSI-25. Terms: CC0-1.0 (licence field of the PSI-25 record). Access: read in full. Use: the needs specification only, not shown on the page (specification item PSI-BASS2-FILES).

**B3. Other documents**

- The challenge statement (item CHALLENGE-2026 above), other uses. https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/ . Terms: public web page. Use: the information needs, two scenario presets (lunar habitat, oxygen likely 30% or more at 10.2 psi or less; spacesuit, 100% oxygen at 4.3 psi), the warning that PSI holds no partial-gravity data.
- 2026 NASA Space Apps Project Submission Guide. https://www.spaceappschallenge.org/resources/project-submission-guide/ . Terms: public guide. Use: team rules (AGENTS.md) and the submission plan.
- 2026 NASA Space Apps Judging and Awards Guide. https://www.spaceappschallenge.org/resources/judging-awards-guide/ . Terms: public guide. Use: team rules and planning.
- Apache License 2.0, text. Apache Software Foundation. https://www.apache.org/licenses/LICENSE-2.0 . Licence: Apache-2.0. Use: the repository LICENSE file.
- Turns, S. R., An Introduction to Combustion: Concepts and Applications, 3rd ed., McGraw-Hill, 2012, ISBN 978-0-07-338019-3. Publisher page https://www.mheducation.com/ (no public full text). Terms: copyrighted by McGraw-Hill; read as background; no file in the repository. Use: scoring/MODEL_BASIS.md checks the direction and form of the ranking rules (chapter names cited). scoring/scoring_config.json also cites its Appendix A for two molar heat capacities (CO2 and N2 at 298 K).
- Lahdelma, R., and Salminen, P., SMAA-2, Operations Research 49(3), 2001. Link: none recorded in the repository. Terms: journal article; not read for terms; treated as copyrighted. Use: named in `data/insights/robustness.json` as the idea behind sampling the weights ("method idea only"); no text or number of it is used.

**B4. Documents opened for the two results on the branch `data-lab`** (data-lab)

Opened by an AI agent; cited as the definition of a method; no text reproduced beyond a short phrase. The model map on that branch (`pipeline/lab/model_map.md`) lists every source it opened.

- OECD, Guidance Document on the Validation of (Q)SAR Models, ENV/JM/MONO(2007)2, paragraphs 92, 109 and 110. https://www.oecd.org/content/dam/oecd/en/publications/reports/2014/09/guidance-document-on-the-validation-of-quantitative-structure-activity-relationship-q-sar-models_g1ghcc68/9789264085442-en.pdf . Terms: not stated on the page. Use: the definition of the smallest convex region of tested conditions.
- NIST SP 811, Guide for the Use of the SI, Appendix B (B.3, B.7, B.8). https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b8 . Terms: not stated on the page (NIST, US Government). Use: unit conversion factors and the rounding rule, to audit the pipeline's factors.
- NIST/SEMATECH e-Handbook of Statistical Methods, 7.2.6.2 Percentiles. https://www.itl.nist.gov/div898/handbook/prc/section2/prc262.htm . Terms: not stated on the page (NIST, US Government). Use: the definition of the median and quartiles.
- NIST Dataplot Reference Manual, Kendall's tau. https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/kendell.htm . Terms: not stated on the page (NIST, US Government). Use: the definition of Kendall tau-b.

### C. Software libraries and fonts

- Python 3 standard library (csv, json, re, urllib and others). Python Software Foundation. https://www.python.org/ . Licence: PSF License (OSI approved). Version used: Python 3.13.5. Use: pipeline/, scripts/, ai/, scoring/, web/ and video/ (the model gateway ai/llm.py uses only the standard library).
- pandas (2.2.3 in ai/). pandas development team. https://github.com/pandas-dev/pandas . Licence: BSD-3-Clause. Use: pipeline/run.py and pipeline/evidence.py (tables), ai/model_readiness.py.
- NumPy 2.1.3. NumPy developers. https://github.com/numpy/numpy . Licence: BSD-3-Clause. Use: ai/model_readiness.py, ai/robustness.py (numeric work, fixed-seed random samples); video/read_overlay.py (comparing character cells with the stored templates).
- scikit-learn 1.6.1. scikit-learn developers. https://github.com/scikit-learn/scikit-learn . Licence: BSD-3-Clause. Use: ai/model_readiness.py only, to test whether the tables hold enough data for a predictive model (cross-validation by experiment). No trained predictor ships in the product. Also used once, with pandas, in the video pilot (k-means grouping of character images, from which the stored character templates were made); not used by any code in video/.
- openpyxl. openpyxl project. https://foss.heptapod.net/openpyxl/openpyxl . Licence: MIT. Use: scripts/export_catalog_xlsx.py (data/catalog/catalog.xlsx).
- Node.js. OpenJS Foundation. https://nodejs.org/ . Licence: MIT. Use: web/parity_check.mjs (the JavaScript ranking gives the same answers as the Python one), continuous integration.
- PptxGenJS. gitbrent. https://github.com/gitbrent/PptxGenJS . Licence: MIT. Use: presentation/build_catalog_filter_slide.js.
- React. The React project. https://github.com/react/react . Licence: MIT (repository page, read on 14 November 2026). Use: rasterising slide icons (no code in the output).
- react-icons. https://github.com/react-icons/react-icons . Licence: MIT. Use: rasterising slide icons (no code in the output).
- sharp. lovell/sharp on GitHub. https://github.com/lovell/sharp . Licence: Apache-2.0 (repository page, read on 14 November 2026). Use: rasterising slide icons (no code in the output).
- Tabler Icons (TbFlame, TbAdjustmentsHorizontal, TbCircleCheck, through react-icons). Tabler. https://github.com/tabler/tabler-icons . Licence: MIT. Use: presentation/catalog_filter_slide.pptx.
- Playwright and Chromium. Microsoft; The Chromium Authors. https://github.com/microsoft/playwright . Licence: Apache-2.0 (Playwright), BSD-3-Clause (Chromium). Use: local screen checks and the screenshots in web/media/ (no code in the output).
- FFmpeg. FFmpeg project. https://ffmpeg.org/ . Licence: LGPL-2.1-or-later (parts GPL-2.0-or-later). Use: web/capture_media.mjs encodes web/media/*.gif (no code in the output). FFmpeg 9.0.1 (Homebrew build, GPL-3.0-or-later as built) is also called as a separate program by video/read_overlay.py and video/tools/make_fixtures.py to decode the clips; no FFmpeg code is in the repository.
- Pillow 11.1.0. Jeffrey A. Clark and contributors. https://github.com/python-pillow/Pillow . Licence: MIT-CMU. Use: video/test_read_overlay.py and video/tools/make_fixtures.py only (tests and the fixture tool); not bundled.
- GitHub Actions: actions/checkout, setup-python, setup-node, configure-pages, upload-pages-artifact, deploy-pages. GitHub. https://github.com/actions . Licence: MIT. Use: .github/workflows/pages.yml (tests, build, deploy of the page).
- Atkinson Hyperlegible font, through Google Fonts. Braille Institute of America. https://fonts.google.com/specimen/Atkinson+Hyperlegible . Licence: SIL Open Font License 1.1. Use: body text of the page (web/).
- Barlow Semi Condensed font, through Google Fonts. Jeremy Tribby. https://fonts.google.com/specimen/Barlow+Semi+Condensed . Licence: SIL Open Font License 1.1. Use: headings and numbers of the page (web/).

### D. Models

- gpt-oss:20b (20.9B parameters, MXFP4 quantisation, Ollama build, digest prefix f38aa0c53da5). OpenAI (United States). https://ollama.com/library/gpt-oss . Licence: Apache-2.0 (checked in the licence text shipped with the model). Use: run locally, in development and before publishing; writes at most three summary sentences per investigation card, from numbered sentences of the PSI record. 33 of its sentences are shown on the public page, on 20 cards, each labelled as AI-generated.
- Claude models of Anthropic (United States), used through Claude Code and claude.ai. The team's usage log records them as Claude Opus 5.5, Opus-family, Sonnet-family and Fable 5.2 agents. https://claude.com/claude-code . Terms: Anthropic's commercial terms (not open source). Use: development only. No Claude model runs in the product.

### E. Tools and services

- Claude Code (AI coding assistant). Anthropic. https://claude.com/claude-code . Terms: Anthropic commercial terms. Use: wrote most of the repository's code, data specifications and coordination text (see Use of SI).
- claude.ai (Claude chat sessions, Opus). Anthropic. https://claude.ai/ . Terms: Anthropic commercial terms. Use: catalog design and extraction, ranking rules, the first ranking test cases, one slide (see Use of SI).
- Exa web search, used as a tool inside Claude Code. [FILL F4: maker, country, link and terms, checked on the tool's own site; the team's source log does not record them.] Use: finding the standards and papers behind the information needs.
- Ollama 0.40.16 (installed with Homebrew). Ollama (United States). https://github.com/ollama/ollama . Licence: MIT. Use: runs gpt-oss:20b on a team member's computer. Not part of the product.
- GitHub Pages. GitHub. https://pages.github.com/ . Terms: free hosting service (no code included). Use: the public page.
- GitHub (repository hosting). https://github.com/choidol0208/NASA_RAPID . Licence of the repository: Apache-2.0 (LICENSE file). Use: source code and data, linked from the page.
- Google Fonts (font delivery service). Google. https://fonts.google.com/ . Use: the page loads its two fonts from it; nothing else is called on page load.

## Limits

What the tool does not do:

- It is a research exploration tool. It is not operational safety guidance and gives no safe or unsafe verdict.
- It makes no prediction for an untested condition.
- It does not treat results at 0 g and 1 g as bounds for lunar or Martian gravity. Every recorded test in the tables was run in microgravity.
- It does not judge any test against a criterion and sets no requirements of its own.
- Its rankings, counts and statuses are the team's computation. They are not conclusions by NASA. NASA does not endorse the tool, and it uses no NASA logo.
- Its test counts cover only PSI's open experimental tables that have one row per test: 14 tables of 12 investigations. 8 more tables are not in the common table. 4 investigations have no experimental table in PSI. The ranking covers all 24 investigations through their records.
- It counts a test for a need only when that need is a stated purpose of the experiment. Other tests are marked "Outside stated objective" and are not counted.
- It gives counts per environment for two environments only: the ISS cabin and the lunar habitat.

How far the checks reach (the next step is under "Goals and what is next"):

- The ranking rules were compared with one textbook. It does not cover flame spread over solid materials; those rules rest on the PSI records and the investigators' papers. The weights and the size of every value are the team's choice.
- The six needs, and the links between purpose sentences and needs, were written with an AI assistant from the documents in the reference list. What is the team's own construction is listed in `pipeline/spec/needs.json`.
- All 24 catalog rows were extracted with an AI assistant. The page marks them "catalog values AI-extracted, not yet checked".
- The reference items were transcribed with an AI assistant. Of the 65 documents (66 entries; one paper is listed twice), 54 were read in full, 8 as an abstract or catalogue page only, 1 is known only through a citation, 1 was read by a teammate session and 1 from an unofficial copy. The page names the level where a document was not read in full.
- The expected answers of the ranking test cases were written by an AI session for the team.
- "Written in the source" means the number appears there. It does not mean its meaning was checked.
- The model-written summaries: reviewed by a second AI session 61, reviewed by a person 0.
- The video reader was checked on 19 clips only, and its frames were read by an AI assistant.
- The oxygen and pressure ranges of each environment are the team's choice. The lunar range reaches up to 85.8 kPa, above the 70.3 kPa (10.2 psi) that the challenge statement names.
- Inside each range is not inside both. For the extinction need, the lunar point (30% oxygen, 70.3 kPa) lies inside the recorded range of oxygen (12 to 34%) and inside the recorded range of pressure (70.2 to 309.3 kPa), each taken alone. Taken together, it lies outside the smallest convex region (the smallest outline without dents) that holds the 273 recorded pairs of oxygen and pressure. All 273 are droplet tests of one investigation, FLEX. The nearest test at 30% oxygen is 0.93 kPa higher in pressure. The region describes where tests were run; it judges nothing. Recomputed by a second AI agent. Reviewed by a person: 0. Files: `data/pipeline/lab/numbers/envelope_lunar_habitat.md` on the branch `data-lab`. (data-lab)
- Pressures that NASA's table gives in mmHg are converted with the torr factor (0.133322368 kPa per mmHg). With the conventional millimetre of mercury, 31 of the 273 FLEX pressures would differ by 0.0001 kPa. No count can change by that difference.

## Numbers used

Every number in the text above, outside the References list. Each value was read from the named file in the working copy of `main` at 19:05 KST on 14 November 2026 (commit `7239a2e`), or from the page built from it, or was printed by a command run for this draft. Paths are relative to the repository root. Bibliographic values inside the References list (record versions, DOIs, report numbers, dates, page counts, library versions) come from `data/psi/manifest.json`, `pipeline/spec/references.json` and `compliance/SOURCES.md`; they are not repeated here. Document names such as NASA-STD-6001B or NASA/TP-2015-216046 are identifiers, not counts.

Commands to repeat before submitting, all read-only:

- `python3 -B -m unittest scoring.test_scorer` (expect "Ran 39 tests ... OK")
- `python3 -B web/parity_check.py` (expect "parity: 99/99 queries identical")
- `python3 -B web/check_integration.py` (expect "11 queries, 33 results checked, 0 broken joins")
- `python3 web/build.py`, then open `web/dist/index.html?q=ISS` and `?q=lunar%20habitat` through a local web server and compare the scores and counts with the worked example.

| Number | What it is | Source file and filter | Recheck before submitting |
|---|---|---|---|
| 24 | PSI combustion investigations in the catalog | `data/psi/manifest.json` (investigations); `data/catalog/investigations.csv` rows | no |
| 22 | Experimental tables in PSI for these investigations | `data/psi/manifest.json`, sum of `experimental_tables` | no |
| 4 | Investigations with no experimental table (PSI-60, 62, 115, 117) | `data/psi/manifest.json`, empty `experimental_tables` | no |
| 14 tables of 12 investigations | Tables read into the common test table | `data/pipeline/tests.csv`, distinct `source_id` and `investigation_id` | yes |
| 8 | Tables that are not one row per test (PSI-20, 21, 22, 23, 47, 68, 106, 142) | 22 tables minus the 14 in `data/pipeline/tests.csv` | yes |
| 1,824 | Recorded tests, one row each | `data/pipeline/tests.csv` rows | yes |
| 376 | Solid-fuel tests | `data/pipeline/tests.csv`, `fuel_phase` = solid | yes |
| 18,445 | Values, each with a source file and a source row | `data/pipeline/values_long.csv` rows; `data/pipeline/run_report.json` | yes |
| 9,226; 6,384; 1,824; 1,011 | Values by origin: named table column; fact set once for a table; uniform material name; computed from other values | `data/pipeline/values_long.csv`, `source_column`: a column name; starts with "(constant"; starts with "(materials"; `kind` = derived | yes |
| 1,824 of 1,824 in microgravity; 0 at lunar or Martian gravity | Gravity level of the tests | `data/pipeline/tests.csv`, `gravity_level` | yes |
| six (6) | Information needs: P1, P2, P3, S1, D1, D2 | `pipeline/spec/needs.json` | no |
| five of six | Needs limited to solid fuels (all but S1, extinction conditions) | `pipeline/spec/needs.json`, `scope` of each need | no |
| 24 and 15 | Links between a need and an investigation; links with the verdict "supported" (5 are "topic only", 4 "differs") | `data/pipeline/objective_links.csv`, `verdict` | yes |
| 133, 0, 2, 298, 122, 0 | Counted tests per need (P1, P2, P3, S1, D1, D2) | `data/pipeline/need_tests.csv`, `objective_link` = stated, by `need_id` | yes |
| 408 | Different tests counted for at least one need | `data/pipeline/need_tests.csv`, distinct `test_id` where `objective_link` = stated | yes |
| 246; 30 to 40% | Gas-flame tests with a surrounding oxygen of 30% or more (30.03 to 40.0%); none counted | `data/pipeline/tests.csv`, `fuel_phase` = gas, `o2_basis` = ambient, `o2_pct` >= 30; none in `need_tests.csv` with `objective_link` = stated | yes |
| 92 and 154 | Of the 246: tests in `need_tests.csv` for S1 with `objective_link` = not_stated (all ACME CFI-G); tests in no need (131 Flame Design, 23 ACME CFI-G) | same filter, joined to `data/pipeline/need_tests.csv` | yes |
| 4 of 6; four of six | Needs with counted tests in the ISS-cabin range | `data/pipeline/scenario_needs.csv`, `scenario_id` = iss, needs where `tests_atmosphere` + `tests_oxygen_only` + `tests_pressure_only` > 0; the page prints "ISS cabin 4 of 6" | yes |
| 55, 2, 63, 45 | ISS cabin: counted tests in range for P1, P3, S1, D1 | same file and filter, sum of the three columns per need; the page's side-by-side block | yes |
| 56 of the 63; one need | ISS cabin, S1: tests with both oxygen and pressure in range; S1 is the only need with such tests | `data/pipeline/scenario_needs.csv`, `scenario_id` = iss, `tests_atmosphere` (56 for S1, 0 for the others) | yes |
| three needs on oxygen alone (3 of the 4) | ISS cabin: P1, P3 and D1 match through `tests_oxygen_only` only | same file, `scenario_id` = iss, `tests_atmosphere` = 0 and `tests_oxygen_only` > 0 | yes |
| 1 of 6; one | Needs with counted tests in the lunar range | `data/pipeline/scenario_needs.csv`, `scenario_id` = lunar_habitat, same rule; the page prints "1 of 6" | yes |
| 17 | Lunar range, S1: FLEX droplet tests | same file, `need_id` = S1, `tests_atmosphere` | yes |
| 9 and 8 | Of the 17: methanol and heptane tests | `data/pipeline/scenario_tests.csv` joined to `tests.csv` and `need_tests.csv`, by material | yes |
| 30.0% or 34.0% | Oxygen of the 17 tests | same join, `o2_pct` | yes |
| 71.2 to 72.4 kPa | Pressure of the 17 tests (71.23 to 72.37) | same join, `pressure_kpa` minimum and maximum | yes |
| about 1 to 2 kPa; "just above" | Distance of the 17 tests above 70.3 kPa (0.93 to 2.07) | computed from the line above; wording of decision 14:15 in `coord/decisions.md` | yes |
| 15 and 2 | Of the 17: "disruption" and "completion" in the "Test end" column | same join, `test_end`; the page prints "disruption 8" for heptane and "completion 2, disruption 7" for methanol | yes |
| 0 ("no counted test") | Counted tests at 30% oxygen or more and at or below 70.3 kPa | `data/pipeline/tests.csv` joined to `need_tests.csv`, ambient `o2_pct` >= 30 and `pressure_kpa` <= 70.3 | yes |
| 1 (18% oxygen, 70.2 kPa) | Counted tests at or below 70.3 kPa at any oxygen: one FLEX test (Open points only) | same join, `pressure_kpa` <= 70.3 | yes |
| 20; 33 to 39%; 50.7 kPa | Recorded tests with a surrounding oxygen of 30% or more and at or below 70.3 kPa: ACME CFI-G gas flames (33.2 to 39.3% oxygen, 50.665 kPa). 46 more gas-flame tests at 30% or more and at or below 70.3 kPa give the oxygen of the burner stream, not of the surroundings (ACME CFI-G 28, Flame Design 18); the text does not use them | `data/pipeline/tests.csv`, `o2_basis` = ambient (20) or oxidizer_stream (46), `o2_pct` >= 30, `pressure_kpa` <= 70.3 | yes |
| 18 and 2 | Of the 20: tests with a recorded test end, in `need_tests.csv` for S1 as not_stated; tests in no need | same filter, joined to `data/pipeline/need_tests.csv`; `test_end` | yes |
| all 20 on the gas grid | 9 in the cell 30 to 36% oxygen, below 62.8 kPa; 11 in the cell above 36%, below 62.8 kPa | the page's grid for gas fuels; `data/pipeline/coverage_grid.csv`, `fuel_phase` = gas, `o2_basis` = ambient | yes |
| 0 of 376 | Solid-fuel tests with a recorded pressure | `data/pipeline/tests.csv`, `fuel_phase` = solid, numeric `pressure_kpa` | yes |
| 139; 22.2%; 0 at 30% or more | Solid-fuel tests with a recorded surrounding oxygen; highest value; number at 30% or more | `data/pipeline/tests.csv`, `fuel_phase` = solid, `o2_basis` = ambient, numeric `o2_pct` | yes |
| 19 to 23% oxygen; 85.8 to below 116.8 kPa | ISS-cabin range | `pipeline/spec/scenarios.json`, id = iss, `ranges` | no |
| 30 to 36% oxygen; below 85.8 kPa | Lunar range | `pipeline/spec/scenarios.json`, id = lunar_habitat, `ranges` | no |
| 30% oxygen or more; 70.3 kPa (10.2 psi) or less | What the challenge statement expects for the Moon (likely; wording as reported in `pipeline/spec/references.json`, item CH.moonbase, not a verbatim quote) | `pipeline/spec/references.json`, CH.moonbase; `pipeline/spec/scenarios.json`, lunar_habitat `note`; the page's preset source line | no |
| 21% oxygen; 101.3 kPa (14.7 psi) | Air at sea level; the page's ISS-cabin preset | the page, "How your input was read" for the query `ISS`; `scoring/scoring_config.json`, presets | no |
| 100% oxygen; 4.3 psi | Spacesuit preset, from the challenge statement | `scoring/scoring_config.json`, presets, spacesuit `source` | no |
| 79.1, 79.1, 76.1 | Team scores of the lunar-habitat result cards (ACME-BRE, FLEX, ACME-CFI-G) | the built page for `?q=lunar%20habitat`; `scoring/scoring_config.json` version 1.1.0 | yes |
| 94, 94, 92.7 | Team scores of the ISS result cards (BASS-II, BASS, SAFFIRE-II) | the built page for `?q=ISS`, same configuration | yes |
| a fourth investigation, SAFFIRE-III | Level with BASS-II and BASS for the query `ISS`; listed under "Other investigations" | the built page for `?q=ISS`; `data/insights/robustness.json`, run iss, `structural_ties` | yes |
| 41 | Test configurations in the catalog | `data/catalog/configurations.csv` rows | no |
| 0 to 100; 0 to 1; up to half; three cards; 3 points | Score scale; similarity scale; largest cut when fuel or oxygen is far off; results shown; margin inside which evidence quality sets the order | `scoring/METHOD.md`, sections 1.2 and 1.5; `scoring/scoring_config.json` (`top_k` 3, `tie_points` 3.0) | no |
| six (6) buttons | Example buttons on the page | the built page; `web/index.html` | yes |
| two environments | Environments with counts per need on the page (ISS cabin, lunar habitat) | `web/app.js`, `DASH_SCENARIOS` | yes |
| 20 and 4 | Cards with a model-written summary; cards with NASA sentences only | `data/insights/cards.json`, `status` (1 generated, 19 generated_partial, 4 fallback_quote); `reviewed_by` | yes |
| four example environments | Queries with a "Weight check" line: ISS, lunar habitat, spacesuit, Mars base | the page, block "How AI is used here", part 3; `data/insights/robustness.json`, `runs` | yes |
| four parts | Parts of each need in the need-by-need block | `web/app.js`, `renderNeedAnswer`; capture `web/media/05_lunar_constraints.png` | yes |
| 34 | Items the page lists for the flammability need of the lunar habitat, under the fold "Criteria, requirements and definitions" | `data/pipeline/answers/lunar_habitat__P1.json`, `frame.criteria`; `web/app.js`, `renderNeedAnswer`, prints the fold with its count | yes |
| 21, 8, 3, 1, 1 | Of the 34: definitions, requirements, recommendations, acceptance criterion, design value | the `type` of each of the 34 items in `pipeline/spec/references.json`, joined by `item_id` | yes |
| 20, 7, 7 | Of the 34: items from NASA documents (NASA-STD-6001B 11, NASA-STD-3001 Volume 2 2, OCHMO-TB-008 2, the Task Book report 2, the FLEX requirements document 1, NASA/CR-2005-213689 1, NASA/TP-2010-216134 1); from ISO and ASTM standards (ISO/TS 16697 4, ISO 14624-1 1, ASTM D2863 1, ASTM G125 1); from papers | `reference_id` of each of the 34 items, with `issuer` and `kind` in `pipeline/spec/references.json` | yes |
| about 30 to 31% oxygen; about 54 kPa; two of five samples | Saffire-VI samples VI-2 (31.0% oxygen, 54.1 kPa) and VI-3 (30.3%, 54.6 kPa), quoted from Table 1 of ICES-2024-365; the table lists five samples (IV-1, V-2, VI-2, VI-3, VI-4) | `data/pipeline/answers/lunar_habitat__P1.json`, `rung3_published.at_the_environment`; `pipeline/spec/references.json`, item SAF456.conditions | yes |
| 6 and 20 | Evidence packages: environments and single oxygen-and-pressure cells | `data/pipeline/evidence/index.json`, packages by kind | yes |
| 211 | Published statements tagged by condition | `data/pipeline/findings.csv` rows (from 180 reference items) | yes |
| 246 and 30 | Tests in the downloadable "matched tests" CSV, ISS cabin and lunar habitat | the built page, "Take the data with you"; `data/pipeline/scenario_tests.csv`, tiers other than "other" | yes |
| 60,866 | Files in PSI's listings of the 24 investigations | `data/pipeline/raw_inventory.json`, `_meta.totals.files` | no |
| 19 of 296 | BASS-II video clips read; video files PSI lists for PSI-25 | `video/settings/bass2.json`; the page's raw-data line for PSI-25 ("296 videos") | no |
| 130; 53, 52, 25; 45 and 8 | Decisions of the pipeline; by class; of the 53, elementary mathematics and named outside definitions | branch `data-lab`, `pipeline/lab/model_map.md`, first paragraph | yes (branch public?) |
| 1,867 to 1,824; 1 and 42 | Test rows before and after the audits; maintenance row and repeated rows no longer counted | `coord/requests/20261114-1242-data-to-all-audit-fixes-...md`, item 2; `pipeline/README.md` | no |
| 4.0 mm/s; "Note 4" | A cell read wrongly before the audits | `coord/status/data.md`, "Three independent audits" | no |
| seventh need; six remain | Need P4 "Exploration atmosphere", removed | `coord/decisions.md`, 11/14 12:15 | no |
| 136 to 133; 11 to 2; 299 to 298; 0 to 122; 4 to 0 | Counted tests per need before and after the literature check | `coord/requests/20261114-1442-data-to-all-counts-changed-...md`, table "Counts now" | no |
| 28 of 61 | Model-written sentences removed by the review | `data/insights/quality.json`, `removed_by_review`, `model_rows_in_sheet` | yes |
| 39 of 39 | Unit tests of the ranking code | run for this draft: `python3 -B -m unittest scoring.test_scorer` | yes |
| 38 of 38 | Ranking test cases with an expected answer | `validation/report.md` (run 18:34); not re-run for this draft | yes |
| 99 of 99 | Queries with the same ranking in Python and JavaScript | run for this draft: `python3 -B web/parity_check.py` | yes |
| 0.05; 5 of 5 | Weight change; scenarios where first place stays | `validation/report.md`, "Weight stability" | yes |
| 45 of 48; 1; 2; four demo queries | Weight sensitivity (each prevention weight x 0.5 and x 1.5) on the queries `ISS`, `lunar habitat`, `ISS cotton fabric` and `lunar habitat cotton fabric` | `validation/report.md`, "Weight sensitivity"; `validation/sensitivity.py`, `DEMO` | yes |
| 129 of 136; 3 | Sensitivity to the other values; runs where first place changes | `validation/report.md`, "Sensitivity to the other values"; `scoring/PARAMETER_REVIEW.md` | yes |
| 8,000; 96%; 85.6% | Random weightings per example environment (ISS, lunar habitat, spacesuit, Mars base) and per kind of draw; share of draws in which ACME-BRE and FLEX are first together; share in which ACME-CFI-G is among the first three | `data/insights/robustness.json`, run lunar_habitat: `draws`, `first_or_tied_share_local` 0.9604, `top3_share_local` 0.8561; the page's "Weight check" lines | yes |
| 2012 | Year of the textbook used for the rule check | `scoring/MODEL_BASIS.md` | no |
| two rules | Rules changed after the textbook comparison (oxygen on a ratio scale; diluent by heat capacity) | `scoring/MODEL_BASIS.md`, "Changes made from this check" | no |
| up to 20 values per table | Sample sheet for a reading by a person | `pipeline/README.md`, "Checking"; `reports/spot_check.csv` | no |
| eight questions | Questions for combustion researchers | `coord/status/catalog.md` (17:03); `scoring/PARAMETER_REVIEW.md`, end of file | no |
| 107 of 115; 8; 24 of 24; 135 of 135 | Catalog values against the NASA sources | `validation/catalog_source_check.md`; not re-run | yes |
| 59 of 59 | Checks of the separate pipeline checker | `data/pipeline/validation_report.json`, summary; not re-run | yes |
| 11; 33; 0 | Integration check | run for this draft: `python3 -B web/check_integration.py` | yes |
| 1,824 test links | Tests whose source row is a number and lies inside an existing table file | recomputed for this draft from `data/pipeline/tests.csv` against the 14 files in `data/psi/experimental_tables/` | yes |
| 70; 5; 4; 28; 33 | Model sentences written; refused by code checks; removed by a first reading; removed by the review; shown | `data/insights/quality.json`: `proposed`, `dropped_by_gates`, `removed_before_review.n`, `removed_by_review`, `shipped_model_sentences`; the page prints the same five numbers | yes |
| 14; 13; 9 | Model sentences that failed a code check at first; sent back to the model once; passed after that | `data/insights/quality.json`: `rejected_first_pass`, `repair_attempted`, `repaired` | yes |
| 61; 0 | Model sentences reviewed by a second AI session; by a person | `data/insights/quality.json`, `reviewed_ai_session`, `reviewed_person`; the page prints both | yes |
| 226 of 226; 102; 10 | Code-written sentences marked `wording_ok`; quoted NASA sentences in the review sheet; quotes marked not relevant and not shown | `data/insights/quality.json`, `template_verdicts`, `quote_rows`, `quotes_not_shown_by_review.n`; one quote row has no verdict | yes |
| at most three | Summary sentences the model may write per card | `README.md`, "AI layer" | no |
| nine; one, six, one, one | Outcomes tried in the model-readiness test; verdicts: indicative, too few, counts only, not modelable | `data/insights/model_readiness.json`, `rows`, `verdict`; the page prints the nine lines | yes |
| 0.126 against 0.1875; 157; 65 | Mean absolute error of the simple model and of the average; tests; groups of conditions (FLEX diameter ratio) | `data/insights/model_readiness.json`, row `flex_extinction_diameter_ratio` | yes |
| 100; 20; five-fold | Smallest number of tests and of groups; folds of the test | `data/insights/model_readiness.json`, `thresholds` | no |
| five readings; 19 clips; 16,019 rows; 33 templates | What the video reader copies; clips; rows written; stored character templates | `video/README.md` | no |
| 186 (80 and 106); about 750; none wrong | Frames compared by eye (random and hard cases); values compared | `video/README.md`, "How it was checked" | no |
| at most 1 of 19 | Clips in which the automatic flame-out time was right | `video/README.md`, "What failed and was dropped" | no |
| 12 to 34%; 70.2 to 309.3 kPa; 273; 0.93 kPa | Recorded oxygen and pressure of the tests counted for S1; tests with both; distance of the nearest test at 30% oxygen | branch `data-lab`, `data/pipeline/lab/numbers/envelope_lunar_habitat.md`, section S1; the same spans recomputed for this draft from `data/pipeline/tests.csv` | yes (branch public?) |
| 0.133322368; 31 of 273; 0.0001 kPa | Conversion factor for mmHg; FLEX pressures that would differ with the other factor; size of the difference | `pipeline/README.md`, "Limits" | no |
| gpt-oss:20b; Ollama 0.40.16 | Model and runtime | `ai/config.py`; `compliance/SOURCES.md`; the page's label on each summary | no |
| 23 of 24; PSI-10 | PSI records with the CC0-1.0 licence; the record with no licence stated | `data/psi/manifest.json`, licence field per investigation | no |
| 66 entries; 65 documents; 54, 8, 1, 1, 1 | Reference entries; documents (AIAA-2012-3536 and ICES-2012-SAME2 are one paper, both read in full); how much of each was read | `pipeline/spec/references.json`, entries and `access` field (55 entries read in full, minus the duplicate) | yes |
| 59 and 6 | Reference documents with items in the data the page loads; documents in the needs specification only | recomputed for this draft: ids of `pipeline/spec/references.json` searched in the files of `web/dist/data/` | yes |
| 256; 3; 47; 25 and 58 words | Verbatim quotes in the needs specification; quotes longer than 40 words; documents with a quote in the data the page loads; longest such quote from a document that is not NASA's, and from a NASA document | `pipeline/spec/references.json`, items with a `quote` field, searched as text in the files of `web/dist/data/` | yes |
| 28 and 7 | Reference lines whose terms come from the NTRS copyright field; lines with no open licence found or read | from the 15:10 draft (`https://ntrs.nasa.gov/api/citations/<id>`, field `copyright.determinationType`); not rechecked for this draft | no |
| 14 November 2026; 19:05; 19:20; 19:40; 20:00; 20:15 | Date; time of the state of `main` that was read; time the freeze was lifted; time of this draft; time the compliance logs were looked at; time of the corrections | `git log`; `coord/decisions.md`, 11/14 19:20; the clock of the correction pass | no |
| 7239a2e; 30c1301 | Commit of the main branch that was read at 19:05; the commit of 19:20, which changed coordination files only and is the one the corrections were confirmed on | `git log -2`; `git diff --stat 7239a2e 30c1301` (three files under `coord/`) | no |
| 63 and 59; 2 | Lines with Korean text in `compliance/SOURCES.md` and `compliance/AI_USAGE_LOG.md` at the last commit; lines of the working copy of `AI_USAGE_LOG.md` that quote a Korean word (the box only) | counted at 20:00 with `git show HEAD:<file>` and on the working copy | yes |
| Claude Opus 5.5; Fable 5.2 | Model names in the team's usage log (names, not counts) | `compliance/AI_USAGE_LOG.md` | no |
| four ways; two without any model | The uses of AI described under "Use of SI": ranking by rules, language model, prediction test, video reader. The ranking and the video reader run without a model; the prediction test fits a linear regression and ships none | this text's own grouping; `scoring/scorer.py` and `video/read_overlay.py` (their imports name no model library); `video/README.md` (33 character templates); `data/insights/model_readiness.json` (`model`, `shipped`); the page's block "How AI is used here, and how it was checked" shows the model counts, the prediction test and the weight sampling, and the BASS-II card names the video reader | no |
| 195 | Words in the High-Level Summary (limit: 50 to 200) | counted with a script after the last edit of the correction pass | yes |

## Open points

How the marks of the 15:10 draft were resolved. All six planned features are on the page as built from `main` at 19:05, so every marked sentence was kept as a plain statement.

- A. "What NASA's recorded tests showed": on the page. For the ISS cabin and the lunar habitat it is the first part of each need in the block "What is known for ..., need by need".
- B. The evidence map: on the page, under "Where the evidence stops".
- C. The written card summaries: on the page, on 20 of 24 cards, with the label "AI-generated, reviewed by second AI session (data role)".
- D. The list "What PSI does not contain for this environment" with "Data that would close it": on the page.
- E. The fixed "what is known" sentences: on the page, as the need-by-need block of the two environments.
- F. The raw-data line per investigation: on the page, on each result card.

Facts of the 15:10 draft that were dropped:

- "70 of 70 cards and table rows on the page match": measured at 14:33 on an earlier layout of the page and not repeated since. The integration check (11 queries, 33 results, 0 broken joins) was repeated for this draft and stays.
- The IBM Plex fonts: the two internal pages that used them were taken out of the repository. The source log keeps its two rows, because it is append only.
- `reports/build_indicators_page.py` as a use of pandas: the file no longer exists.

For a person to decide before submitting:

- The challenge's description of the data. The summary gives it without quotation marks. To quote it, compare the phrase and its subject with the official challenge page, word for word.
- Quotes on the page. The page now shows short verbatim quotes from 47 reference documents, each with its source: 25 words at most from documents that are not NASA's, 58 words at most from NASA documents. The final submission asks you to confirm that no copyrighted material was used without permission. Decide whether short attributed quotes are acceptable, or ask the data role to show the team's wording only.
- Three NASA quotes in `pipeline/spec/references.json` are still longer than 40 words (`BASS2TM.products`, `RG.flex2`, `SAMEEIRD.csd`). The data role left the decision to the human lead (answer to request 1630).
- ISO/TS 16697: the entry says only the abstract or catalogue page was read, yet the specification holds a sentence placed in Clause 7. Ask the data role where that sentence was read.
- The branch `data-lab`. It was on the remote at the last fetch, with the files this text cites. Two passages and group B4 of the References depend on it.

For the team to do in the source log (`compliance/SOURCES.md`, append only; this job could not touch it):

- Add rows for the reference documents that have none: 42 of the 66 entries, by a count made for this draft on the English working copy. They are the entries ICES-2017-224, NTRS-20170008805, NTRS-20180005168, ICES-2018-SAFFIRE2-PMMA, CNF-2023-SAFFIRE, ICES-2021-266, NTRS-20200000557, PSI-SAFFIRE-FILES, SAME-EIRD-2005, SAME-BCD-2005, SAME-FSR-2010, SAMER-FR-2014, SAME-OPS-2007, SAME-SRD-2005, ICES-2012-SAME2, AST-2015-PYROLYSIS, NASA-TM-2011-217036, NASA-CP-2004-213205-VOL1, ICES-2016-SAFFIRE, IAASS-2016-SAFFIRE, WP-2021-FIRE-DETECTION, WP-2021-FIRE-EXTINGUISHER, NASA-TM-1999-209285, ICES-2015-196, NASA-TM-20210011385, ASGSR-2013-BASS, AIAA-2012-3536, CSSCI-2014-ACME, JASMAC-33-ACME, CSSCI-2014-COOLFLAME, NRC-2011-DECADAL, ICES-2014-179, JTE-2006-HIRSCH, NTRS-20070018178, NTRS-20100015582, NASA-CR-2005-213689, NTRS-20150008961, NTRS-20140011630, PROCI-2018-THOMSEN, ICES-2015-293, NTRS-20150000894 and ASTM-G125.
- Add rows for Claude Code, claude.ai and the Exa tool, and for the paper named in `data/insights/robustness.json` as the idea behind the weight sampling (Lahdelma and Salminen, 2001).
- React and sharp share one row with react-icons and have no link of their own (links checked for the 15:10 draft: github.com/react/react, MIT; github.com/lovell/sharp, Apache-2.0).
- The model map on `data-lab` names more opened sources than the log has rows for. The log has rows for the OECD guidance, three NIST pages and Hirsch et al. 2011.
- Check the edition of ASTM D2863. The References list says D2863-23e1; the source log says D2863-23.
- Done since 15:10: the correction row for the textbook (two heat capacities taken from its Appendix A) is in the log.

For the team to do in the usage log (`compliance/AI_USAGE_LOG.md`, append only):

- One row for the final pass over the two drafts (19:05 to 19:40, pm role, AI-written) and one for the correction pass after two AI readers (about 19:55 to 20:15, pm role, AI-written), if they are not there yet. The row of 15:15 to 16:30 covers the first drafts.
- The product table still has an empty "(to be decided)" row. The log is append only, so add a note line that the row is superseded by the gpt-oss:20b row.
- Two rows quote one Korean word each: a mark in a data file and a query keyword. Many rows say "Not reviewed" in the column "What a person reviewed", and one says "need expert review". The section "Use of SI" does not copy these phrases.

Reference details still missing:

- The NTRS copyright field gives no public-use statement for 2 documents (NASA/TM-20210011385 and the JASMAC presentation) and notes possible copyright-protected material for 2 (ICES-2021-266 and the 2021 fire-detection white paper).
- For 7 documents outside NTRS no open licence was found or read. One repository page (ICES-2017-224) did not open on 14 November.
- ISO 14624-1 has no link. PSI-10 states no licence. Google Fonts, GitHub, GitHub Pages, Claude Code and claude.ai have no terms link. Add a terms link only after reading it on the service's own site.
- Homebrew, with which Ollama and FFmpeg were installed, has no line of its own in group C or E and no row in the source log. Add one with its link and licence once both are read on its own site.
- The terms page of the Exa tool answered with a file download when it was opened for the 15:10 draft, so it was not read.
- The paper behind the weight sampling has no link and no terms in the repository.

Points on the page and in the repository that this draft works around; they belong to other roles:

- The page prints "Lunar base or pressurized rover" for the lunar preset. The button says "Lunar habitat". This draft says "lunar habitat".
- The page heads one list "Criteria in NASA documents", but the list also holds items from ISO, ASTM, SAE and journal papers. This draft uses the page's heading and says "NASA standards and studies" in running text, as the page's own note does. The worked example gives the 34 items of the flammability need by type and by kind of document.
- The page's masthead gives the challenge's description of the data in quotation marks, with "NASA's combustion results" as its subject. No file in the repository holds the challenge text word for word (`pipeline/spec/references.json`, CHALLENGE-2026, gives the wording as reported). The ui role can compare it with the official page or drop the marks.
- The page's method text says the score is scaled by "raw data, flight duration, human check". By the decision of 14:15 a human check does not change the score (`scoring/METHOD.md`, 1.5). This draft says "evidence quality" only.
- `data/derived/data_profile.json` carries no field that says it was written by AI-written code.
- The captures in `web/media/` were committed at 16:31. The note under the side-by-side block and the card summaries changed after that. See `slides_outline.md` for which captures to retake.

Wording rules kept in this draft:

- "No recorded test" would be false for 30% oxygen or more at or below 70.3 kPa: 20 gas-flame tests with a surrounding oxygen of 30% or more are recorded there. This draft says "no counted test" and names the 20.
- "No counted test at or below 70.3 kPa" would also be false without the oxygen condition: one counted FLEX test lies at 18% oxygen and 70.2 kPa. This draft always gives both conditions.
- The challenge statement, as reported in `pipeline/spec/references.json` (item CH.moonbase, not a verbatim quote), gives the lunar values as an expectation (likely), not as a stated bound. This draft says "expects" and "names", not "bound". Apart from the term "SI" and the challenge's title, it gives no wording of the challenge statement as a word-for-word quotation.
- The ISS top three are not called an order: BASS-II, BASS and SAFFIRE-III are level under the team's weights.
- No timing was measured for a user. This draft does not say "in minutes".
- Review by combustion researchers is written as a next step only: under "Goals and what is next", and in one sentence under "Use of SI", part 1.
- Who checked is said in the positive: code, AI sessions, an AI assistant. "Reviewed by a person: 0" stands as a count where the model-written sentences are counted and after the two passages from the branch `data-lab`.

Still to add by the team: F1 to F5 (see the box at the top).
