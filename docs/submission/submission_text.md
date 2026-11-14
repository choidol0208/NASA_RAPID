DRAFT written by an AI assistant (Claude) for the team to rewrite in its own words before submitting. Every number is listed at the end with its source.

> Notes for the team. Delete this box before submitting.
> - Facts were read from the main branch at about 15:10 KST on 14 November 2026 (commit 583b3d4). The page was read from its code. The live site was not opened.
> - Before submitting, search this file for `[PLANNED` and for `[FILL`. Neither mark may remain.
>   - `[PLANNED X: ...]` wraps one sentence about a feature that was not on the page at 15:10. If the feature is on the page at the freeze, keep the sentence and remove the mark. If it is not, delete the sentence. The letters A to F are explained under "Open points".
>   - `[FILL: ...]` marks a value or a choice that only the team has, or that exists only after the 19:00 freeze. Fill it in, or delete its sentence.
> - Do not submit this box, the first line, "Numbers used" or "Open points". They are for the team.
> - If feature A is on the page at the freeze, replace the summary sentence "INTERPRET lists what NASA standards and studies state and shows where the evidence stops." with: "INTERPRET keeps apart what the tests showed, what standards and studies state, and where the evidence stops." The summary then has 193 words.
> - "SI" (Super Intelligence) is the challenge's word for AI. The text keeps "AI" only where it is a label printed on the page or in a file.
> - Pressures are in kPa. 70.3 kPa is 10.2 psi.

# Fire Evidence Explorer

- Final Project (public page): https://choidol0208.github.io/NASA_RAPID/
- Two example queries: https://choidol0208.github.io/NASA_RAPID/?q=ISS and https://choidol0208.github.io/NASA_RAPID/?q=lunar%20habitat
- Source code: https://github.com/choidol0208/NASA_RAPID [FILL: keep this link only after a person has decided what to do about the Korean-language files in the repository; see "Open points".]
- Project Demo (slides): [FILL: public link to the seven-slide deck; it must open without a login]
- Challenge: Flame in Freefall, https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/

## High-Level Summary

Fire Evidence Explorer is a web dashboard. Describe what you want to build and where. It shows what NASA's recorded microgravity fire tests say for that environment, and where the evidence stops.

For an ISS cabin, counted tests fall in the oxygen range for four of six fire-safety needs, and in the pressure range for one. For a lunar habitat, they fall in range for one need: 17 droplet tests recorded just above 70.3 kPa (10.2 psi). At 30% oxygen or more and at or below that pressure, no test is counted. A test counts only when the investigators or a NASA document state that purpose.

The challenge calls NASA's fire data "hard to find, harder to compare, and harder yet to interpret". FIND ranks 24 investigations of NASA's Physical Sciences Informatics (PSI) archive against your environment. COMPARE puts 1,824 recorded tests into one table with shared columns and units. INTERPRET lists what NASA standards and studies state and shows where the evidence stops. Gaps are shown as plainly as results.

It is a research exploration tool, not safety guidance. Counts and rankings are the team's computation, not NASA's conclusions.

## Project Details

### What it does

Fire Evidence Explorer is one static web page. It loads its own data files and calls no language model.

You type what you are building and where. Rough input is fine, for example "moon cotton fabric" or "30% O2 at 10.2 psi". Six buttons give ready examples: "ISS cabin", "Lunar habitat", "Lunar habitat, cotton fabric", "Smoke detection on the ISS", "Spacesuit" and "Mars base".

The page first shows how it read your input. Each condition is marked as typed by you, taken from a preset, or a default. Words that match nothing in PSI are named, so you know they changed nothing. For an environment with lunar or Martian gravity, the page warns that PSI holds no partial-gravity combustion data.

Then the page answers in three steps.

**Step 1. FIND: the information you need.**

- Three result cards, for the closest of the 24 PSI combustion investigations.
- On each card: a team score from 0 to 100, the closest test configuration, the similarity on each dimension, why it matched and the largest gap.
- Links to the PSI page, the dataset DOI and the source table.
- What the record says: the objective, as summarised in the team's catalog, and the findings stated in the record or table.
- A full ranking of all 24 investigations, folded.
- For the ISS-cabin and lunar-habitat presets, downloads: the matched tests (CSV), an evidence package (JSON), all recorded tests (CSV) and the list of dataset DOIs to cite.

[PLANNED C: Each card also carries a short written summary, labelled as AI-generated, in which every sentence cites numbered sentences of the PSI record.]

[PLANNED F: Each investigation also has one line that says which raw data files the PSI archive holds for it.]

**Step 2. COMPARE: the points to consider.**

The page works with six fire-safety information needs:

- Prevention: flammability limit; ignition; flame spread and growth.
- Suppression: extinction conditions.
- Detection: combustion products; smoke generation conditions.

The six needs were written with an AI assistant (Claude Code) from NASA standards and studies, under the team's direction. The list is the team's, not NASA's. A combustion specialist has not yet reviewed it.

One rule decides what is counted. A test counts for a need only when the investigators or a NASA project document state that need as a purpose of the experiment. A test that records the right values without such a statement is marked "Outside stated objective" and is not counted. Below, "counted test" always has this meaning.

The page shows:

- A table with one row per ranked investigation and one column per need. Each cell says whether the PSI table records the conditions and the outcome that the need asks for.
- For the ISS-cabin and lunar-habitat presets, for each need: how many counted tests fall in the scenario range, and what such a count means.
- For the same two presets, a side-by-side block of the two environments. Each count links to its row in the team's data file.
- For the same two presets, the section "Recorded tests in the scenario range". Each count there opens a list of test ids. Each test id links to its row in the repository copy of the NASA PSI table.

For any other input, the page shows the table and says that counts per environment exist for the two presets only.

**Step 3. INTERPRET: the constraints.**

Constraints are of three kinds, kept apart. A constraint here is something a designer has to take into account. The page sets no design limit of its own.

1. **What NASA's recorded tests showed.** Code computes these values from the PSI tables, for example how many tests ended in each recorded way. Each value comes with its number of tests and a note that says what the value is and what it is not. These are observed values. They are not limits, thresholds or requirements. For the two presets, they are in the evidence package download.

   [PLANNED A: On the page, they are the first part of the Constraints block.]

2. **Criteria in published documents.** For each need, the page lists what NASA standards and studies state. Each item has a type (for example requirement, acceptance criterion, definition, published result or stated knowledge gap), a document and a link. The wording of each item was transcribed with an AI assistant and has not yet been checked by a person. The page does not judge any test against these criteria.

3. **Where the evidence stops.** Grids show the recorded tests by oxygen and pressure for each fuel phase, with your input marked. A cell with no tests is a gap in the data, and the page shows it as such.

   [PLANNED B: An evidence map puts gas flames, fuel droplets and solid fuels on one oxygen axis and marks your input on it.]

   [PLANNED D: A list names what PSI does not contain for the environment and the data that would close each gap.]

   [PLANNED E: Fixed sentences then say, for each need, what is recorded at the condition, what is recorded near it, what NASA and the investigators have published, and what is not known.]

### A worked example: an ISS cabin and a lunar habitat

Everything below is an observation about the recorded tests in PSI's open tables on 14 November 2026. Nothing below is a limit, a prediction or a safety verdict.

**The input.** You press "Lunar habitat". The challenge statement expects lunar oxygen "likely" at 30% or more, with a pressure of 70.3 kPa (10.2 psi) or less. The page counts tests against its own lunar range: 30 to 36% oxygen and a pressure below 85.8 kPa. The edges of this range are the team's bins. Gravity is reported next to the count and does not change it.

**FIND.** The three result cards are ACME-BRE (team score 79.1), FLEX (79.1) and ACME-CFI-G (76.1). The page warns that PSI has no partial-gravity combustion data. All results are microgravity tests. They are not bounds for lunar gravity.

**COMPARE.** Counted tests fall in the lunar range for 1 of the 6 needs: extinction conditions. They are 17 droplet tests of the FLEX investigation, recorded at 30.0% or 34.0% oxygen and at 71.2 to 72.4 kPa. That is about 1 to 2 kPa above 70.3 kPa. For the other five needs there is no counted test in the range.

Now press "ISS cabin". The page's ISS-cabin range is 19 to 23% oxygen and 85.8 to below 116.8 kPa. The three result cards are BASS-II (team score 94), BASS (94) and SAFFIRE-II (92.7). Counted tests fall in the range for 4 of the 6 needs:

| Need | ISS cabin | Lunar habitat |
|---|---|---|
| Flammability limit | 55 tests, on oxygen alone | 0 |
| Ignition | 0 | 0 |
| Flame spread and growth | 2 tests, on oxygen alone | 0 |
| Extinction conditions | 63 tests, 56 of them on oxygen and pressure | 17 tests, at 71.2 to 72.4 kPa |
| Combustion products | 45 tests, on oxygen alone | 0 |
| Smoke generation conditions | 0 | 0 |

For the ISS cabin, too, the match is partial. For three of the four needs the tests match on oxygen alone, because their tables record no pressure.

**INTERPRET, kind 1: what the recorded tests showed.** The 17 lunar-range tests burned droplets of methanol (9 tests) or heptane (8 tests). The FLEX table records how each test ended: "disruption" for 15 tests and "completion" for 2. The table does not define these words, so the page does not interpret them. These values describe the tests that were run.

**INTERPRET, kind 2: criteria in published documents.** For the flammability need, for example, the page lists items from NASA-STD-6001B, NASA's standard on flammability, offgassing and compatibility requirements and test procedures. The page does not compare the 17 tests with any of these items.

**INTERPRET, kind 3: where the evidence stops.**

- No counted test was recorded at 30% oxygen or more and at or below 70.3 kPa.
- Recorded there, but not counted: 20 gas-flame tests of the ACME CFI-G investigation, at 33 to 39% surrounding oxygen and 50.7 kPa. For 18 of them the table records how the test ended, but no investigator or NASA project document that was read states a fire-safety purpose for the experiment. The other 2 record no such outcome. The page's grid for gas flames shows all 20.
- None of the 376 solid-fuel tests records a pressure.
- 139 solid-fuel tests record the surrounding oxygen. The highest value is 22.2%. None is at 30% or more.
- All 1,824 recorded tests were run in microgravity. None was run at lunar or Martian gravity.
- Ignition and smoke generation conditions have no counted test at all.

The page does not say what would happen in these conditions. It shows which recorded tests exist there, and which of them are counted.

### How it works

**Data pipeline.** Written specifications (JSON files) say which column of each PSI table maps to which standard variable, by which rule and in which unit. Code then reads 14 tables of 12 investigations into one table with one row per test: 1,824 tests and 18,445 values. Each value keeps its NASA source file and row. 9,226 values are read from a named column of the table. The others are facts that the mapping sets once for a whole table (6,384, for example the fuel phase or the gravity level), uniform material names (1,824) and values computed from other values (1,011). A cell that the rules cannot read stays empty with a flag and is never filled in.

**Needs and the counting rule.** Each of the six needs lists the conditions and outcomes a test must record, and says what a count means. Five of the six needs are limited to solid fuels by the team. Droplet and gas-flame tests can count for extinction conditions only. The counting rule of Step 2 then applies. For example, 246 gas-flame tests were recorded at 30 to 40% surrounding oxygen, and none is counted. 92 of them record how the flame ended, but no document that was read states a fire-safety purpose for the experiment. The other 154 record no outcome that the extinction need asks for. Counted tests on 14 November: flammability limit 133, ignition 0, flame spread and growth 2, extinction conditions 298, combustion products 122, smoke generation conditions 0. These are 408 different tests, because a test can count for more than one need.

**Ranking.** Code reads your words into conditions: oxygen, pressure, flow, fuel, sample shape, research purpose and, for suppression questions, the diluent gas. It compares them with each of the 41 test configurations in the team's catalog. Each condition gets a similarity from 0 to 1. The score is a weighted sum of these, from 0 to 100. The weights depend on the type of question. The score is cut by up to half when the fuel or the oxygen is far off. A factor for evidence quality is applied last. The page keeps one configuration per investigation and shows three. Scores within 3 points are ordered by evidence quality, and one place can go to a test run at your oxygen. No language model produces or changes a score.

**Evidence packages.** For each environment, the pipeline writes one evidence package: for each need, the matched tests, their values, the gaps, the values the tests showed and the reference items. There are 6 environment packages and 20 packages for single cells of oxygen and pressure. The page offers the ISS-cabin and lunar-habitat packages as JSON, next to a CSV of the matched tests (246 and 30 tests on 14 November) and the list of dataset DOIs.

**The checks that were run.** The checks in the table were run on 14 November 2026: all but the last by code, the last as a reading by an AI session. No combustion specialist took part in any of them. The publishing workflow stops if the unit tests, the validation scenarios, the integration check or the Python-and-browser comparison fails.

| Check | Result | What it does not show |
|---|---|---|
| Unit tests of the ranking code | 38 of 38 pass | That the rules are right; only that the code follows them |
| Validation scenarios of the ranking | 35 of 35 give the expected answer | The expected answers were written by an AI session for the team, not by a specialist |
| Same ranking in Python and in the browser | 86 of 86 queries identical | Correctness; only that the two versions agree |
| Each weight moved by 0.05 up and down | First place unchanged in 5 of 5 scenarios | Larger changes |
| Each prevention weight halved and raised by half, on four example queries | 45 of 48 variants keep the same top three in the same order; 1 keeps the same three in another order; 2 change; first place never changes | Other queries |
| Catalog values against the NASA sources | 107 of 115 ranking values are written in the source; 8 are the team's readings; 24 of 24 range ends match; 135 of 135 numbers in shown text are written in the source | That each number's meaning was checked |
| Pipeline outputs recomputed by separate code | 46 of 46 checks pass | The checker itself was not reviewed by a person |
| Page against data | For 11 queries, all 33 top-three results reach their data with 0 broken joins; 70 of 70 cards and table rows on the page match; all 1,824 test links point at an existing row of the repository copy of a NASA PSI table | Queries outside the 11 |
| Ranking rules against one combustion textbook (Turns, 2012) | Each rule was compared for direction and form; the textbook does not cover the rules for solid flame spread (sample shape, thickness, flow direction) | A specialist's review |

### Benefits and who it is for

The tool is for people who develop equipment or a habitat for a crewed environment, and for researchers who work with NASA's combustion data.

- One description leads to the closest investigations, their data and the way to cite them.
- Tests from 14 different tables can be compared in one table with the same columns and units. Every value traces back to its NASA table row. Values read from a cell also name its column.
- The three kinds of constraints stay apart. A reader can tell an observed value from a stated criterion and from a gap.
- Gaps are shown as plainly as results. A reader sees which conditions have no counted test.
- The data leave the page as CSV and JSON, so the analysis can continue in the user's own tools.

### Goals and what is next

The team set four goals. The page serves them as follows.

1. Classify and summarise the experiment data: the catalog of 24 investigations, the result cards and the common test table.
2. Extract the elements usable for fire safety: the six information needs, the counted tests and the values the tests showed.
3. Give the points to consider for what the user wants to build: the COMPARE step and the criteria in published documents.
4. Judge whether the data are sufficient and what further data are needed: the "Where the evidence stops" part.

What is next:

- Review by people. Every catalog row and every reference item still needs a human check. The ranking rules and the needs need a review by a combustion specialist.
- [FILL: keep this line only if the PLANNED E sentence above was deleted.] Fixed sentences that say, for each need, what is recorded at the condition, what is recorded near it, what is published and what is not known.
- Data from NASA video where PSI holds no numeric file. A pilot on BASS-II video runs outside the repository. Its reading of NASA's on-screen values held in a check (0 wrong in 80 random frames). Its automatic flame-out timing failed its check (right in 1 of 19 clips) and will not ship. Nothing from the pilot is in the product.
- New PSI data. The pipeline is re-run with the same commands. A command that lists what is new in PSI is optional work. Detection on a schedule is a design only.

### Tools, languages, hardware and software

- Languages: Python 3 (mostly the standard library), JavaScript (ES modules, no framework), HTML and CSS.
- Data work: pandas. NumPy and scikit-learn are used only in analysis scripts of the AI layer. No trained predictor ships in the product.
- Checks and media: Node.js (comparison of the Python and browser rankings), Playwright with Chromium (page checks and screenshots), FFmpeg (the demo GIF).
- Other libraries: openpyxl (one spreadsheet export); PptxGenJS, React, react-icons, sharp and Tabler Icons (one slide).
- Fonts: Atkinson Hyperlegible and Barlow Semi Condensed, from Google Fonts.
- Hosting and automation: GitHub Pages and GitHub Actions.
- Language model and its runtime: gpt-oss:20b, run locally with Ollama 0.40.16.
- SI tools used in development: Claude Code and claude.ai (Anthropic), and the Exa web-search tool inside Claude Code.
- Data: NASA PSI, 24 combustion investigations and their 22 experimental tables.
- Hardware: one team member's own computer ran the language model. [FILL: computer type, chip and memory only; no owner name and no device name. No project file states the hardware.]

## Use of SI

"SI" (Super Intelligence) is the challenge's word for AI.

### In short

- Most of the repository's code, data specifications and coordination text were written with an AI coding assistant. The team's human leads set the direction and made the main design decisions. AI sessions made many detailed judgments, such as which purpose sentence supports which need and how to read the literature. No person has reviewed those judgments yet.
- In the product, code computes every count, every rank and every scenario statement. One open-weight language model, run locally, drafts only short card summaries. The public page calls no model.

### SI in development

Tools:

- Claude Code (Anthropic) with Claude models. The team's usage log records them as Claude Opus 5.5, "Opus" and "Fable" (the last for review agents). Several sessions ran in parallel, one per team role (pm, data, ui, catalog). They often used sub-agents and separate review agents.
- Claude (Opus) in claude.ai chat sessions. These designed and extracted the first catalog and wrote the first ranking rules, the validation scenarios with their expected answers, and one slide.
- The Exa web-search tool, used inside Claude Code to find the standards and papers behind the information needs.
- gpt-oss:20b (OpenAI, Apache-2.0), run locally through Ollama 0.40.16, to test cited summaries and to build the card drafts of the AI layer.

What these tools wrote:

- The scripts that fetch the PSI records and tables and profile their columns.
- The specification-driven pipeline: the six information needs and their links to the experiments' purpose sentences, the standard variables, the column mappings, the scenario ranges, the indicators, the coverage grid, the evidence packages and the separate checker.
- The reference list: the search, the reading and the record of each item with its place in the document and how much of the document was read.
- The catalog and the rule-based ranking, with its validation scenarios and their expected answers.
- The dashboard: the browser version of the ranking, the comparison with the Python version, the page and the publishing workflow.
- The code of the AI layer: the model gateway, the sentence index of the PSI records, the code-written scenario text, the code checks and the evidence-map data.
- An analysis script in the AI layer (`ai/model_readiness.py`) that uses scikit-learn to test whether the tables hold enough data for a predictive model. No trained predictor ships.
- A pilot that times flame duration from BASS-II video with image processing and a small prediction model. It runs outside the repository and is not in the product.
- The team's coordination files and helper scripts.
- Audits by separate AI agents: recomputation from the raw tables, checks of quotations against the documents, and a search for over-general statements. Their findings led to fixes.
- The first draft of this text and of the slide outline. [FILL: add "The team then rewrote both." only if that is true.]

What the human leads decided: the topic, the four goals, the FIND, COMPARE and INTERPRET frame, the main use, the three kinds of constraints, and the rules for model use. Some structures were proposed by an AI session and then accepted by the leads. One example is the four-step "what is known for an environment" structure. An AI session also listed ideas for how the project could differ. The leads chose the direction and kept the team's original topic.

How SI output is marked:

- Code: the first lines of each code file say it was written with an AI assistant (Claude). One empty file has no header. The README files say the same.
- Data: each JSON output carries a field that says it is AI-generated. The CSV outputs are described as AI-generated in `pipeline/README.md`. Every catalog row is marked "ai_extracted" until a person checks it. The reference file says it is AI-generated and not yet checked by a human.
- Page: the section "How the score works" says the page, the catalog, the ranking code and the pipeline were written with an AI assistant (Claude) under the team's direction. The footer says "Built during the hackathon with AI assistance (Claude)".
- Slide: the catalog filter slide says "Built with AI assistance (Claude)" in its footer.

What review there was: the team's usage log marks almost every entry as not reviewed by a person. Two entries say the user confirmed the work in conversation. The automatic checks are listed under Project Details. No combustion specialist reviewed the work.

### SI in the product

[FILL: keep exactly one of the two versions below and delete the other. Version 1 applies if the card summaries are on the public page at the freeze. At 15:10 the AI layer was in the lead's working copy and not on the main branch.]

Version 1:

- Model: gpt-oss:20b by OpenAI, an open-weight model under the Apache-2.0 licence. It runs locally through Ollama 0.40.16 before publishing.
- Role: it writes at most three summary sentences for each investigation card. Each sentence must cite numbered sentences of the PSI record. Code splits the 24 records into these numbered sentences first.
- Single entry point: one gateway file handles every model call. It refuses any other model, checks the installed model's digest, checks each reply against a fixed format and logs each call.
- Code checks: code checks every model sentence for its cited sentence numbers, its quoted source text, numbers, names, advice wording, prediction wording, known misconceptions, length and hedge words.
- Review: every model sentence goes to a review sheet. A sentence marked as not supported, as partly supported or as having lost a hedge is removed, never reworded. The sheet records whether the reviewer was a person or an AI session. An AI session is never recorded as a person. Reviewer of the shipped sentences: [FILL: "a second AI session, not a person", or a role named in the review sheet].
- Label on the page: "AI-generated, not reviewed yet" or "AI-generated, reviewed by ..." with the model name. NASA text is tagged "Quoted from the PSI record". Team counts are tagged "Computed by team code from NASA PSI tables".
- Counts: [FILL: number of cards that show a model-written summary]; [FILL: number of model sentences proposed, removed by the code checks or the review, and shown].

Version 2:

The product shows no text written by a language model. Code computes every count, rank and statement, and the public page calls no model. In development, gpt-oss:20b drafted card summaries; they were not published.

### What SI was not allowed to do

- Produce or change a ranking score.
- Write a number, a count, a need statement, a gap or a scenario statement in the product.
- Run in the public page.
- Give a safe or unsafe verdict, predict an untested condition or give operational safety guidance.
- Add text that is not in the cited source.
- Claim a human review that did not happen.
- Be a model or service from a maker the team's rule excludes. The team's rule of 14 November, taken from its reading of the event's participation terms, allows no AI model or AI service made by a Chinese or Chinese-owned organisation, in development or in the product. The checks behind this: the product's model gateway (`ai/llm.py`) refuses every model except gpt-oss:20b, and the team's usage log lists only Anthropic and OpenAI models and the Exa search tool. [FILL: the maker and country of the Exa tool, once checked on its own site. Until then, write only: "The team found no AI model or AI service whose maker is Chinese or Chinese-owned."]

## Space Agency Data

### What we used

1. NASA PSI combustion investigations: 24 records and their 22 experimental tables. 23 records carry the CC0-1.0 licence. The PSI-10 record states no licence.
2. Documents filed with the PSI investigations: BASS-II, BASS and FLEX documents that explain the table columns; SAME and SAME-R requirements documents and final reports; Saffire-I and Saffire-II telemetry documents and Readme.
3. NASA standards, technical briefs and reports, among them NASA-STD-6001B, NASA-STD-3001 Volume 2, OCHMO-TB-008, JSC 20584, NASA/TP-2010-216134, NASA/CP-2003-212103, NASA/TP-2015-216046 and the Researcher's Guide to Combustion Science.
4. Papers by NASA researchers and their partners, mostly from the NASA Technical Reports Server.
5. The challenge statement on the Space Apps site.

### How each is used

- PSI records: the catalog of all 24 investigations, the ranking for a described environment, and the dataset DOIs and links on every result. [PLANNED C: The records are also the numbered sentences behind the written card summaries.]
- PSI experimental tables: 14 tables of 12 investigations are read into one common test table with standard variables and units. Each value keeps its source file and row. From this table, code counts which recorded tests match each need and each environment, and builds the grid of recorded oxygen and pressure.
- Standards, reports and papers: the six information needs rest on items from these documents. The page lists the items for each need under Constraints, each with its type, document and link. The wording of each item was transcribed with an AI assistant and has not yet been checked by a person. The page never judges a test against a criterion.
- Challenge statement: the lunar-habitat preset (oxygen likely 30% or more at 10.2 psi or less) and the spacesuit preset (100% oxygen at 4.3 psi), the warning that PSI holds no partial-gravity data, and the FIND, COMPARE and INTERPRET frame.

### How the data shaped the project

- The challenge text says the data are hard to find, harder to compare and harder yet to interpret. That gave the three steps of the page.
- The tables differ in columns, units and notes. That led to the common test table and to a written column mapping for each table, so every value can be traced to its table row.
- Counted tests fall in range for 4 of 6 needs for an ISS cabin, for 3 of them on oxygen alone, and for 1 of 6 for the lunar range. That contrast became the main thing the page shows: where the evidence stops. No counted test was recorded at 30% oxygen or more and at or below 70.3 kPa (10.2 psi). The 17 counted droplet tests lie about 1 to 2 kPa above that pressure.
- The records and the investigators' papers state each experiment's purpose. That led to the counting rule: a test counts for a need only when that need is a stated purpose of the experiment.
- Every test in the common test table was run in microgravity. So the page warns that there are no partial-gravity data. Results at 0 g and 1 g are not bounds for lunar or Martian gravity.

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

Other NASA data, used locally only (not in the repository, not on the page):

- PSI-25 BASS-II raw videos: 19 of the 296 MP4 files (the tests whose flame events are recorded in the table, about 1.8 GB), plus 4 science documents (ReadMe, Test Matrices, Ops, Fan calibration). https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 . Licence: CC0-1.0 (licence field of the PSI-25 record). Use: a pilot that reads NASA's on-screen values from the videos (0 wrong in 80 random frames). Its automatic flame-out timing failed its check (right in 1 of 19 clips) and will not ship. Nothing from the pilot is in the product.
- PSI-25, PSI-26 and PSI-69 documents (BASS-II ReadMe, Test Matrices, Fan calibration data; FLEX DoD and Test Plan; BASS Planned Test Matrix and DLD). https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 (and PSI-26, PSI-69). Licence: CC0-1.0. Use: reading what the table columns mean (for example, BASS-II "Air display" is in cm/s).

### B. NASA and other documents

These are the documents behind the six information needs (`pipeline/spec/references.json`: 66 entries, one paper listed twice, so 65 references here).

- "Access" says how much of each document was read.
- "Cited only" means that the page shows no text of the document. The needs specification in the repository keeps verbatim quotes of the cited passages (264 quotes; 24 are longer than 40 words).
- For 28 documents on the NASA Technical Reports Server (NTRS), the terms are those in the copyright field of the NTRS record, read on 14 November 2026.
- For 7 other documents no open licence was found or read. They are treated as copyrighted.

**B1. Documents with items listed on the page under Constraints (37)**

- Flammability, Offgassing, and Compatibility Requirements and Test Procedures. NASA, NASA-STD-6001B w/Change 3 (Revision B approved 2011-08-26; Change 3 revalidated 2025-06-09, administrative change). https://standards.nasa.gov/sites/default/files/standards/NASA/B-w/CHANGE-3/3/2025_06_25_NASA-STD-6001B_w_Change_3_FINAL_Admin-Change-FINAL.pdf. Terms: Public to read; cited only, text not redistributed. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-STD-6001B).
- Space systems - Safety and compatibility of materials - Method to determine the flammability thresholds of materials. ISO, ISO/TS 16697:2012 (status: withdrawn). https://www.iso.org/standard/57450.html. Terms: Paid standard, copyright with the publisher; only bibliographic data and the public abstract cited. Access: abstract or catalogue page only. Use: an information need and the Constraints list on the page (specification item ISO-TS-16697).
- Standard Test Method for Measuring the Minimum Oxygen Concentration to Support Candle-Like Combustion of Plastics (Oxygen Index). ASTM International, ASTM D2863-23e1 (per Note 2, technically equivalent to ISO 4589-2 when the gas measurement and control device of 6.3.1 is used with direct oxygen concentration measurement). https://www.astm.org/d2863.html. Terms: Paid standard, copyright with the publisher; only bibliographic data and the public abstract cited. Access: abstract or catalogue page only. Use: an information need and the Constraints list on the page (specification item ASTM-D2863).
- NASA Spaceflight Human-System Standard, Volume 2: Human Factors, Habitability, and Environmental Health. NASA Office of the Chief Health and Medical Officer, Revision F, approved 2026-07-14 (Table 6.2-3 also read in Revision E, 2025-05-01). https://standards.nasa.gov/standard/NASA/NASA-STD-3001_VOL_2. Terms: Public to read; cited only, text not redistributed. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-STD-3001-V2).
- NASA-STD-3001 Technical Brief: Fire Protection. NASA Office of the Chief Health and Medical Officer, OCHMO-TB-008 Rev A. https://www.nasa.gov/wp-content/uploads/2023/12/ochmo-tb-008-fire-protection.pdf. Terms: US Government work, public. Access: read in full. Use: an information need and the Constraints list on the page (specification item OCHMO-TB-008).
- Spacecraft Maximum Allowable Concentrations for Airborne Contaminants. NASA JSC Toxicology, JSC 20584 Rev D, 02/2026. https://www.nasa.gov/wp-content/uploads/2026/02/jsc-20584-smacs-rev-d.pdf. Terms: US Government work, public. Access: read in full. Use: an information need and the Constraints list on the page (specification item JSC-20584).
- Recommendations for Exploration Spacecraft Internal Atmospheres: The Final Report of the NASA Exploration Atmospheres Working Group. NASA JSC, NASA/TP-2010-216134, October 2010. https://www.nasa.gov/wp-content/uploads/2023/03/henninger-8.2-34-atm-tp216134-2010.pdf. Terms: US Government work, public. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-TP-2010-216134).
- Correlation of Normal Gravity Aerospace Materials Flammability Data with Flammability in Microgravity Environments (NASA Task Book, PI S. Olson). NASA, Task Book report, FY2022. https://taskbook.nasaprs.com/tbp/tbpdf.cfm?id=14639. Terms: US Government work, public. Access: read in full. Use: an information need and the Constraints list on the page (specification item TASKBOOK-14639).
- Flammability Limits from BASS-II Testing in Microgravity Compared to Normal Gravity Limits (Olson, Ferkul, Fernandez-Pello, Miller, Wichman, Bhattacharjee, T'ien). 49th International Conference on Environmental Systems, ICES-2019-101 (7-11 July 2019, Boston). https://hdl.handle.net/2346/84505. Terms: Copyright with publisher or authors; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item ICES-2019-BASS2).
- Evaluating Material Flammability in Microgravity and Martian Gravity Compared to the NASA Standard Normal Gravity Test (Olson, Ferkul). AIAA / NASA GRC, AIAA 2012-3492. https://ntrs.nasa.gov/citations/20130010991. Terms: Copyright with publisher or authors; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item NTRS-20130010991).
- Microgravity Flame Spread in Exploration Atmospheres: Pressure, Oxygen, and Velocity Effects on Opposed and Concurrent Flame Spread (Olson, Ruff, Miller). SAE, SAE Technical Paper 2008-01-2055. https://doi.org/10.4271/2008-01-2055. Terms: Copyright with publisher or authors; cited only. Access: abstract or catalogue page only. Use: an information need and the Constraints list on the page (specification item SAE-2008-01-2055).
- Research Needs in Fire Safety for the Human Exploration and Utilization of Space: Proceedings and Research Plan (Ruff, ed.). NASA GRC, NASA/CP-2003-212103. https://ntrs.nasa.gov/citations/20030053425. Terms: US Government work, public. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-CP-2003-212103).
- The Saffire Experiment: Large-Scale Combustion aboard Spacecraft (Ferkul, Urban, Olson, Ruff, et al.). 10th U.S. National Combustion Meeting, College Park, Maryland, April 23-26, 2017, 2017. http://hdl.handle.net/20.500.11820/9397b059-72ed-41aa-8b7a-3ea8ba1bc795. Terms: Copyright with publisher or authors; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item SAFFIRE-2017).
- Evaluation of Spacecraft Smoke Detector Performance in the Low-Gravity Environment (Meyer, Urban, Mulholland, Bryg, Yuan, Ruff, Cleary, Yang). Fire Safety Journal, 2018. https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/. Terms: Copyright with publisher or authors; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item FSJ-2018-SAME).
- Research Requirements Document: Droplet Flame Extinguishment in Microgravity (FLEX). NASA GRC, November 4, 2005 (file name FLEX_EIRD_v4.pdf). https://www1.grc.nasa.gov/wp-content/uploads/FLEX_EIRD_v4.pdf. Terms: US Government work, public. Access: read in full. Use: an information need and the Constraints list on the page (specification item FLEX-EIRD).
- Droplet Combustion Experiments Aboard the International Space Station (Dietrich, Nayagam, Hicks, Ferkul, Dryer, et al.). Microgravity Science and Technology, 2014. https://link.springer.com/article/10.1007/s12217-014-9372-2. Terms: Copyright with publisher or authors; cited only. Access: abstract or catalogue page only. Use: an information need and the Constraints list on the page (specification item MST-2014-FLEX).
- Detailed Results From the Flame Extinguishment Experiment (FLEX) March 2009 to December 2011. NASA GRC, NASA/TP-2015-216046, November 2015. https://ntrs.nasa.gov/citations/20150023456. Terms: US Government work, public. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-TP-2015-216046).
- A Researcher's Guide to: Combustion Science. NASA ISS Program Science Office, NP-2015-10-034-JSC. https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf. Terms: US Government work, public. [FILL: recheck these terms; the team's source log asks for it.] Access: read in full. Use: an information need and the Constraints list on the page (specification item NP-2015-10-034-JSC).
- Results of Large-Scale Spacecraft Flammability Tests (Ferkul, Olson, Urban, Ruff, Easton, T'ien, Liao, Fernandez-Pello, Torero, Eigenbrod, Legros, Smirnov, Fujita, Rouvreau, Toth, Jomaas). 47th International Conference on Environmental Systems, ICES-2017-224 (16-20 July 2017, Charleston, South Carolina). https://hdl.handle.net/2346/73020. Terms: no licence statement read (the repository page did not open on 14 November 2026); treated as copyright with authors or publisher; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item ICES-2017-224).
- NASA PSI, Saffire-I (PSI-98) and Saffire-II (PSI-99): telemetry graph documents, operations notes and Readme. NASA Physical Sciences Informatics (PSI), PSI-98 version 4, PSI-99 version 5 (files version 1). https://psi.nasa.gov/physci/repo/data/investigations/PSI-99. Terms: CC0-1.0 (licence fields of the PSI-98 and PSI-99 records). Access: read in full. Use: an information need and the Constraints list on the page (specification item PSI-SAFFIRE-FILES).
- Exploration Investigation Requirements Document for SAME a.k.a. Smoke Aerosol Measurement Experiment (PI D. Urban; Co-Is G. Mulholland, Z.-G. Yuan, J. Yang, T. Cleary). NASA GRC, Rev. 2.0, February 25, 2005 (PSI file PSI-102_Engineering Documents_SAME_EIRD.pdf, 72 pages). https://doi.org/10.60555/gd4k-8h62. Terms: CC0-1.0 (licence field of the PSI-102 record; file hosted on PSI). Access: read in full. Use: an information need and the Constraints list on the page (specification item SAME-EIRD-2005).
- Smoke Aerosol Measurement Experiment (SAME), Final Report, November 1, 2000 - April 14, 2009 (Urban, Ruff, Sheredy, Cleary, Yang, Mulholland, Yuan). NASA GRC, March 15, 2010 (PSI file PSI-102_Reports_SAME_Final Science Report.pdf, 68 pages; appendices B to E reprint SAE 2009-01-2468, AIAA 2009 'Properties of Smoke from Overheated Materials in Low-Gravity', SAE 2008-01-2089 and AIAA 2008 'Spacecraft Fire Detection: Smoke Properties and Transport in Low-Gravity'). https://doi.org/10.60555/gd4k-8h62. Terms: CC0-1.0 (licence field of the PSI-102 record; file hosted on PSI). Access: read in full. Use: an information need and the Constraints list on the page (specification item SAME-FSR-2010).
- Smoke Aerosol Measurement Experiment Re-flight (SAMER), Final Report, 01 November 2000 - June 2, 2014 (Urban, Ruff, Sheredy, Meyer, Cleary, Yang, Mulholland, Yuan). NASA GRC, June 2, 2014 (PSI file PSI-101_Reports_SAME-R_Final Report.pdf, 89 pages). https://doi.org/10.60555/2np7-jv14. Terms: CC0-1.0 (licence field of the PSI-101 record; file hosted on PSI). Access: read in full. Use: an information need and the Constraints list on the page (specification item SAMER-FR-2014).
- Pyrolysis Smoke Generated Under Low-Gravity Conditions (Mulholland, Meyer, Urban, Ruff, Yuan, Bryg, Cleary, Yang). Aerosol Science and Technology 49(5), 310-321, 2015. https://doi.org/10.1080/02786826.2015.1025125. Terms: journal article; licence not read on the landing page; treated as copyright with publisher or authors; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item AST-2015-PYROLYSIS).
- Final Report: Fire Prevention, Detection, and Suppression Project, Exploration Technology Development Program (Ruff). NASA GRC, NASA/TM-2011-217036, September 2011. https://ntrs.nasa.gov/citations/20110020262. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-TM-2011-217036).
- Strategic Research to Enable NASA's Exploration Missions Conference and Workshop: Presentations (Nahra, ed.); presentations 'Fire Prevention, Detection, and Suppression', 'Fire Suppression and Response' and 'Research Plan for Fire Signatures and Detection' (Ruff) and 'Organizing Questions for Reduced-Gravity Flammability' (Miller and NASA/NCMR project scientists). NASA GRC, NASA/CP-2004-213205/VOL1, August 2004 (conference of June 22-23, 2004, Cleveland). https://ntrs.nasa.gov/citations/20040142351. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-CP-2004-213205-VOL1).
- Operation and Development Status of the Spacecraft Fire Experiments (Saffire) (Ruff, Urban). 46th International Conference on Environmental Systems, 2016 (NTRS 20170000230; the paper number is not printed in the NTRS copy). https://ntrs.nasa.gov/citations/20170000230. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item ICES-2016-SAFFIRE).
- The Spacecraft Fire Experiment (Saffire) - Objectives, Development and Status (Schoren, Ruff, Urban). International Association for the Advancement of Space Safety conference, 2016, 2016 (NTRS 20170001636). https://ntrs.nasa.gov/citations/20170001636. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item IAASS-2016-SAFFIRE).
- Research Questions and Challenges for Improved Spacecraft Fire Detection (Fortenberry, Wang, Cleary, Easton, Berger, Meyer). Topical white paper submitted to the NASEM Biological and Physical Sciences Decadal Survey 2022-2032, 2021-10-31 (NTRS 20210022143). https://ntrs.nasa.gov/citations/20210022143. Terms: NTRS notes that portions may include copyright-protected material; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item WP-2021-FIRE-DETECTION).
- Fire Safety in the Low-Gravity Spacecraft Environment (Friedman). NASA GRC, NASA/TM-1999-209285 (29th International Conference on Environmental Systems, July 1999). https://ntrs.nasa.gov/citations/19990063738. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-TM-1999-209285).
- Results from on-board CSA-CP and CDM Sensor Readings during the Burning and Suppression of Solids - II (BASS-II) Experiment in the Microgravity Science Glovebox (MSG) (Olson, Ferkul, Bhattacharjee, Miller, Fernandez-Pello, Link, T'ien, Wichman). 45th International Conference on Environmental Systems, ICES-2015-196 (12-16 July 2015, Bellevue, Washington; NTRS 20150019858). https://ntrs.nasa.gov/citations/20150019858. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item ICES-2015-196).
- Burning and Suppression of Solids-II (BASS-II) Summary Report (Olson, Ferkul, Bhattacharjee, Miller, Fernandez-Pello, Link, T'ien, Wichman). NASA GRC, NASA/TM-20210011385, October 2021. https://ntrs.nasa.gov/citations/20210011385. Terms: NTRS permits use by or on behalf of the US Government and gives no public-use statement; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item NASA-TM-20210011385).
- Thickness and Fuel Preheating Effects on Material Flammability in Microgravity from the BASS Experiment (Ferkul, Olson, Takahashi, Endo, Johnston, T'ien). American Society for Gravitational and Space Research 2013 Annual Meeting (presentation), 2013 (NTRS 20140011099). https://ntrs.nasa.gov/citations/20140011099. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item ASGSR-2013-BASS).
- Particle Morphology and Size Results from the Smoke Aerosol Measurement Experiment-2 (Urban, Ruff, Greenberg, Fischer, Meyer, Mulholland, Yuan, Bryg, Cleary, Yang). 42nd International Conference on Environmental Systems, AIAA 2012-3536 (15-19 July 2012, San Diego; NTRS 20130000422). https://ntrs.nasa.gov/citations/20130000422. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item AIAA-2012-3536). (The specification lists this paper twice, as AIAA-2012-3536 and ICES-2012-SAME2; it is one reference here.)
- Gaseous Non-Premixed Flame Research Planned for the International Space Station (Stocker, Takahashi, Hickman, Suttles). 2014 Spring Technical Meeting of the Central States Section of the Combustion Institute, March 16-18, 2014 (NTRS 20140009169). https://ntrs.nasa.gov/citations/20140009169. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item CSSCI-2014-ACME).
- Cool-flame extinction during n-alkane droplet combustion in microgravity (Nayagam, Dietrich, Hicks, Williams). Spring Technical Meeting of the Central States Section of the Combustion Institute, March 16-18, 2014 (NTRS 20140006750); conference version of the Combustion and Flame paper listed in PSI-39. https://ntrs.nasa.gov/citations/20140006750. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item CSSCI-2014-COOLFLAME).
- Applying Flammability Limit Probabilities and the Normoxic Upward Limiting Pressure Concept to NASA STD-6001 Test 1 (Olson, Beeson, Fernandez-Pello). 44th International Conference on Environmental Systems, ICES-2014-179 (13-17 July 2014, Tucson, Arizona). https://ntrs.nasa.gov/citations/20150004099. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: an information need and the Constraints list on the page (specification item ICES-2014-179).

**B2. Documents in the needs specification only (28)**

- Space systems - Safety and compatibility of materials - Part 1: Determination of upward flammability of materials. ISO, ISO 14624-1:2003. Link: none recorded; no catalogue page was checked. Terms: Paid standard, copyright with the publisher; only bibliographic data and the public abstract cited. Access: known only through a citation. Use: the needs specification only, not shown on the page (specification item ISO-14624-1).
- Evidence Report: Risk of Hypobaric Hypoxia from the Exploration Atmosphere. NASA Human Research Program, 2015. https://ntrs.nasa.gov/citations/20150021491. Terms: US Government work, public. Access: abstract or catalogue page only. Use: the needs specification only, not shown on the page (specification item NTRS-20150021491).
- Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data (challenge statement). NASA Space Apps Challenge, 2026. https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/. Terms: Public challenge statement. Access: read by a teammate session. Use: the needs specification only, not shown on the page (specification item CHALLENGE-2026).
- Preliminary Results from the Saffire VI Experiment (Urban, Ruff, Ferkul, Easton, Johnston, Owens, Olson, Fortenberry, Graf, George, Toth, Meyer, Eigenbrod, T'ien, Liao, Fernandez-Pello, Legros, Guibaud, Smirnov, Fujita, Rojas Alva, Jomaas). 53rd International Conference on Environmental Systems, ICES-2024-365 (21-25 July 2024, Louisville, Kentucky). https://ntrs.nasa.gov/citations/20240002981. Terms: NTRS public record that may include copyrighted material; only Table 1 values cited. Access: read in full. Use: the needs specification only, not shown on the page (specification item ICES-2024-365).
- Results of Large-Scale Spacecraft Flammability Tests, presentation slides (Ferkul, Olson, Urban, Ruff, Easton, T'ien, Liao, Fernandez-Pello, Torero, Eigenbrod, Legros, Smirnov, Fujita, Rouvreau, Toth, Jomaas). NASA Technical Reports Server; 47th International Conference on Environmental Systems, 2017 (36 slides). https://ntrs.nasa.gov/citations/20170008805. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item NTRS-20170008805).
- Saffire: A Novel Approach to Study of Spacecraft Fire Safety Using Un-Manned Spacecraft (Urban, Ferkul, Olson, Ruff, Easton, and the international topical team). NASA Technical Reports Server; 33rd Annual Meeting of the American Society for Gravitational and Space Research, October 25-28, 2017, 2017 (32 slides). https://ntrs.nasa.gov/citations/20180005168. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item NTRS-20180005168).
- Analysis of Saffire II two-sided concurrent flame spread over a thick PMMA slab (Olson, Urban, Ruff, Ferkul, Toth, Eigenbrod, Meyer). 48th International Conference on Environmental Systems, 2018 (ICES paper number not verified). http://hdl.handle.net/2346/74099. Terms: the repository page shows no licence statement; treated as copyright with authors or publisher; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item ICES-2018-SAFFIRE2-PMMA).
- The effect of duct size, sample size, and fuel composition on concurrent flame spread over large cellulose samples in microgravity (Olson, Ruff, Ferkul, Owens, Easton, Liao, T'ien, Toth, Jomaas, Fernandez-Pello, Legros, Guibaud, Fujita, Smirnov, Urban). Combustion and Flame, 248 (2023) 112559; read in the accepted manuscript. https://discovery.ucl.ac.uk/id/eprint/10164340/. Terms: author accepted manuscript; the repository page refers re-use to the publisher's terms; cited only. Access: read from an unofficial copy. Use: the needs specification only, not shown on the page (specification item CNF-2023-SAFFIRE).
- Fire Safety Implications of Preliminary Results from Saffire IV and V Experiments on Large Scale Spacecraft Fires (Urban, Ruff, Ferkul, Easton, et al.). 50th International Conference on Environmental Systems, ICES-2021-266 (12-15 July 2021). https://ntrs.nasa.gov/citations/20210011521. Terms: NTRS notes that portions may include copyright-protected material; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item ICES-2021-266).
- Buoyancy Effects on Concurrent Flame Spread Over Thick PMMA (Thomsen, Fernandez-Pello, Ruff, Urban). Combustion and Flame 199 (2019) 279-291; author manuscript on the NASA Technical Reports Server, 2018 manuscript (25 pages). https://ntrs.nasa.gov/citations/20200000557. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item NTRS-20200000557).
- SAME Baseline Concept Description Document, SAME-DOC-001 Rev. A (ZIN Technologies for NASA GRC). NASA GRC / ZIN Technologies, Rev. A, approvals dated June 2005 (PSI file PSI-102_Science Documents_SAME_Baseline Concept Description Doc.pdf, 15 pages). https://doi.org/10.60555/gd4k-8h62. Terms: CC0-1.0 (licence field of the PSI-102 record; file hosted on PSI). Access: read in full. Use: the needs specification only, not shown on the page (specification item SAME-BCD-2005).
- Smoke Aerosol Measurement Experiment (SAME) Operations Manual, SAME-DOC-007 (ZIN Technologies for NASA GRC). NASA GRC / ZIN Technologies, January 2007 (PSI file PSI-102_Science Documents_SAME_Operations Manual_007.pdf, 33 pages). https://doi.org/10.60555/gd4k-8h62. Terms: CC0-1.0 (licence field of the PSI-102 record; file hosted on PSI). Access: read in full. Use: the needs specification only, not shown on the page (specification item SAME-OPS-2007).
- SAME Software Requirements Document, SAME-DOC-004 Rev. D (ZIN Technologies for NASA GRC). NASA GRC / ZIN Technologies, Rev. D (PSI file PSI-102_Reference Data_SAME_Software Req Document.pdf, 29 pages). https://doi.org/10.60555/gd4k-8h62. Terms: CC0-1.0 (licence field of the PSI-102 record; file hosted on PSI). Access: read in full. Use: the needs specification only, not shown on the page (specification item SAME-SRD-2005).
- Topical: Recommendations for Fire Extinguisher Research for Crewed Missions (Easton, Berger, Fortenberry, Padilla). Topical white paper submitted to the Decadal Survey 2023-2032, 2021-10-31 (NTRS 20210023340). https://ntrs.nasa.gov/citations/20210023340. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item WP-2021-FIRE-EXTINGUISHER).
- Recent Research on Flames of Gaseous Fuel Aboard the International Space Station (Stocker). 33rd Japanese Conference on Microgravity Science and Application (presentation), 13-15 October 2021 (NTRS 20210022542). https://ntrs.nasa.gov/citations/20210022542. Terms: NTRS permits use by or on behalf of the US Government and gives no public-use statement; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item JASMAC-33-ACME).
- Recapturing a Future for Space Exploration: Life and Physical Sciences Research for a New Era (National Research Council). National Academies Press, 2011. https://www.nationalacademies.org/read/13048/chapter/2. Terms: licence not read on the landing page; treated as copyright with the publisher; cited only. Access: abstract or catalogue page only. Use: the needs specification only, not shown on the page (specification item NRC-2011-DECADAL).
- Pressure Effects on Oxygen Concentration Flammability Thresholds of Materials for Aerospace Applications (Hirsch, Williams, Beeson). NASA JSC White Sands Test Facility; preprint for the Journal of Testing and Evaluation, NTRS 20070005041, preprint headed 'Journal of Testing and Evaluation, October 2006'. https://ntrs.nasa.gov/citations/20070005041. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item JTE-2006-HIRSCH).
- Oxygen Concentration Flammability Thresholds of Selected Aerospace Materials Considered for the Constellation Program (Hirsch, Williams, Harper, Beeson, Pedley). 2nd IAASS Conference 'Space Safety in a Global World' (meeting named in the NTRS record, May 2007), NTRS 20070018178. https://ntrs.nasa.gov/citations/20070018178. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item NTRS-20070018178).
- Pressure Flammability Thresholds of Selected Aerospace Materials (Hirsch, Williams, Harper, Beeson, Ruff, Pedley). AIAA (per the NTRS record); NASA White Sands Test Facility, NTRS 20100015582, JSC-CN-20193, 2010. https://ntrs.nasa.gov/citations/20100015582. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item NTRS-20100015582).
- Selected Parametric Effects on Materials Flammability Limits (Hirsch, Juarez, Peyton, Harper, Olson). 41st International Conference on Environmental Systems (AIAA), NTRS 20110008636, JSC-CN-23164, 2011. https://ntrs.nasa.gov/citations/20110008636. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item AIAA-2011-5067).
- Bounding the Spacecraft Atmosphere Design Space for Future Exploration Missions (Lange, Perka, Duffield, Jeng). NASA JSC (Jacobs Sverdrup ESC Group), NASA/CR-2005-213689, June 2005. https://ntrs.nasa.gov/citations/20050185597. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item NASA-CR-2005-213689).
- Microgravity Flammability of PMMA Rods in Concurrent Flow (Olson, Ferkul). 9th U.S. National Combustion Meeting, Cincinnati, Ohio, May 17-20, 2015, NTRS 20150008961. https://ntrs.nasa.gov/citations/20150008961. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item NTRS-20150008961).
- An Overview of the Microgravity Science Glovebox (MSG) Facility and the Research Performed in the MSG on the International Space Station (ISS) (Jordan). NASA Marshall Space Flight Center, NTRS 20140011630, M13-2964 (abstract, November 2013). https://ntrs.nasa.gov/citations/20140011630. Terms: NTRS marks the record as a work of the US Government, public use permitted; cited only. Access: abstract or catalogue page only. Use: the needs specification only, not shown on the page (specification item NTRS-20140011630).
- On Simulating Concurrent Flame Spread in Reduced Gravity by Reducing Ambient Pressure (Thomsen, Fernandez-Pello, Urban, Ruff, Olson). Proceedings of the Combustion Institute, 37(3):3793-3800, doi 10.1016/j.proci.2018.05.004; author manuscript PMC6907022. https://pmc.ncbi.nlm.nih.gov/articles/PMC6907022/. Terms: author manuscript in PubMed Central; licence section not read; treated as copyright with publisher or authors; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item PROCI-2018-THOMSEN).
- Buoyant Effects on the Flammability of Silicone Samples Planned for the Spacecraft Fire Experiment (Saffire) (Niehaus, Ferkul, Gokoglu, Ruff). 45th International Conference on Environmental Systems, ICES-2015-[293] (12-16 July 2015, Bellevue, Washington). https://ntrs.nasa.gov/citations/20150022421. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item ICES-2015-293).
- Large-Scale Spacecraft Fire Safety Tests (Urban, Ruff, Ferkul, Olson, Fernandez-Pello, T'ien, Torero, Cowlard, Rouvreau, Minster, Toth, Legros, Eigenbrod, Smirnov, Fujita, Jomaas). Poster; the NTRS record names the International Symposium on Combustion, San Francisco, August 2014, NTRS 20150000894, GRC-E-DAA-TN17050. https://ntrs.nasa.gov/citations/20150000894. Terms: NTRS marks the record as public use permitted; cited only. Access: read in full. Use: the needs specification only, not shown on the page (specification item NTRS-20150000894).
- Standard Test Method for Measuring Liquid and Solid Material Fire Limits in Gaseous Oxidants. ASTM International, ASTM G125-00 (Reapproved 2023), as indicated by the page address g0125-00r23; edition not otherwise verified. https://www.astm.org/g0125-00r23.html. Terms: standard sold by its publisher, as ASTM D2863 above; treated as copyright with the publisher; only bibliographic data and the public catalogue page cited. Access: abstract or catalogue page only. Use: the needs specification only, not shown on the page (specification item ASTM-G125).
- NASA PSI, BASS-II (PSI-25) raw-data documents: SRD_BASS-II.pdf, BASS-II Procedure.docx, BASS-II data FAQ.docx, BASS-II Test Matrix by PI Final.xlsx. NASA Physical Sciences Informatics (PSI), PSI-25 version 4 (files version 1). https://psi.nasa.gov/physci/repo/data/investigations/PSI-25. Terms: CC0-1.0 (licence field of the PSI-25 record). Access: read in full. Use: the needs specification only, not shown on the page (specification item PSI-BASS2-FILES).

**B3. Other documents**

- The challenge statement (item CHALLENGE-2026 above), other uses. https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/ . Terms: public web page. Use: the information needs, two scenario presets (lunar habitat, oxygen likely 30% or more at 10.2 psi or less; spacesuit, 100% oxygen at 4.3 psi), the warning that PSI holds no partial-gravity data.
- 2026 NASA Space Apps Project Submission Guide. https://www.spaceappschallenge.org/resources/project-submission-guide/ . Terms: public guide. Use: team rules (AGENTS.md) and the submission plan.
- 2026 NASA Space Apps Judging and Awards Guide. https://www.spaceappschallenge.org/resources/judging-awards-guide/ . Terms: public guide. Use: team rules and planning.
- Apache License 2.0, text. Apache Software Foundation. https://www.apache.org/licenses/LICENSE-2.0 . Licence: Apache-2.0. Use: the repository LICENSE file.
- Turns, S. R., An Introduction to Combustion: Concepts and Applications, 3rd ed., McGraw-Hill, 2012, ISBN 978-0-07-338019-3. Publisher page https://www.mheducation.com/ (no public full text). Terms: copyrighted by McGraw-Hill; read as background; no file in the repository. Use: scoring/MODEL_BASIS.md checks the direction and form of the ranking rules (chapter names cited). scoring/scoring_config.json also cites its Appendix A for two molar heat capacities (CO2 and N2 at 298 K).

### C. Software libraries and fonts

- Python 3 standard library (csv, json, re, urllib and others). Python Software Foundation. https://www.python.org/ . Licence: PSF License (OSI approved). Use: pipeline/, scripts/, ai/ (the model gateway ai/llm.py uses only the standard library).
- pandas (2.2.3 in ai/). pandas development team. https://github.com/pandas-dev/pandas . Licence: BSD-3-Clause. Use: pipeline/run.py and pipeline/evidence.py (tables), reports/build_indicators_page.py, ai/model_readiness.py.
- NumPy 2.1.3. NumPy developers. https://github.com/numpy/numpy . Licence: BSD-3-Clause. Use: ai/model_readiness.py, ai/robustness.py (numeric work, fixed-seed random samples).
- scikit-learn 1.6.1. scikit-learn developers. https://github.com/scikit-learn/scikit-learn . Licence: BSD-3-Clause. Use: ai/model_readiness.py only, to test whether the tables hold enough data for a predictive model (cross-validation by experiment). No trained predictor ships in the product.
- openpyxl. openpyxl project. https://foss.heptapod.net/openpyxl/openpyxl . Licence: MIT. Use: scripts/export_catalog_xlsx.py (data/catalog/catalog.xlsx).
- Node.js. OpenJS Foundation. https://nodejs.org/ . Licence: MIT. Use: web/parity_check.mjs (the JavaScript ranking gives the same answers as the Python one), continuous integration.
- PptxGenJS. gitbrent. https://github.com/gitbrent/PptxGenJS . Licence: MIT. Use: presentation/build_catalog_filter_slide.js.
- React. The React project. https://github.com/react/react . Licence: MIT (repository page, read on 14 November 2026). Use: rasterising slide icons (no code in the output).
- react-icons. https://github.com/react-icons/react-icons . Licence: MIT. Use: rasterising slide icons (no code in the output).
- sharp. lovell/sharp on GitHub. https://github.com/lovell/sharp . Licence: Apache-2.0 (repository page, read on 14 November 2026). Use: rasterising slide icons (no code in the output).
- Tabler Icons (TbFlame, TbAdjustmentsHorizontal, TbCircleCheck, through react-icons). Tabler. https://github.com/tabler/tabler-icons . Licence: MIT. Use: presentation/catalog_filter_slide.pptx.
- Playwright and Chromium. Microsoft; The Chromium Authors. https://github.com/microsoft/playwright . Licence: Apache-2.0 (Playwright), BSD-3-Clause (Chromium). Use: local screen checks and the screenshots in web/media/ (no code in the output).
- FFmpeg. FFmpeg project. https://ffmpeg.org/ . Licence: LGPL-2.1-or-later (parts GPL-2.0-or-later). Use: web/capture_media.mjs encodes web/media/*.gif (no code in the output).
- GitHub Actions: actions/checkout, setup-python, setup-node, configure-pages, upload-pages-artifact, deploy-pages. GitHub. https://github.com/actions . Licence: MIT. Use: .github/workflows/pages.yml (tests, build, deploy of the page).
- Atkinson Hyperlegible font, through Google Fonts. Braille Institute of America. https://fonts.google.com/specimen/Atkinson+Hyperlegible . Licence: SIL Open Font License 1.1. Use: body text of the page (web/).
- Barlow Semi Condensed font, through Google Fonts. Jeremy Tribby. https://fonts.google.com/specimen/Barlow+Semi+Condensed . Licence: SIL Open Font License 1.1. Use: headings and numbers of the page (web/).
- IBM Plex Sans KR and IBM Plex Mono fonts, through Google Fonts. IBM. https://fonts.google.com/specimen/IBM+Plex+Sans+KR . Licence: SIL Open Font License 1.1. Use: the team's internal pages reports/data-map.html and reports/indicators.html (not part of the product).

### D. Models

- gpt-oss:20b (20.9B parameters, MXFP4 quantisation, Ollama build, digest prefix f38aa0c53da5). OpenAI (United States). https://ollama.com/library/gpt-oss . Licence: Apache-2.0 (checked in the licence text shipped with the model). Use: run locally, in development and before publishing; drafts at most three summary sentences per investigation card, from numbered sentences of the PSI record. [PLANNED C: Its summaries are shown on the public page.]
- Claude models of Anthropic (United States), used through Claude Code and claude.ai. The team's usage log records them as Claude Opus 5.5, "Opus" and "Fable" (the last for review agents). https://claude.com/claude-code . Terms: Anthropic's commercial terms (not open source). Use: development only. No Claude model runs in the product.

### E. Tools and services

- Claude Code (AI coding assistant). Anthropic. https://claude.com/claude-code . Terms: Anthropic commercial terms. Use: wrote most of the repository's code, data specifications and coordination text (see Use of SI).
- claude.ai (Claude chat sessions, Opus). Anthropic. https://claude.ai/ . Terms: Anthropic commercial terms. Use: catalog design and extraction, ranking rules, validation scenarios, one slide (see Use of SI).
- Exa web search, used as a tool inside Claude Code. [FILL: maker, country, link and terms, checked on the tool's own site; the team's source log does not record them.] Use: finding the standards and papers behind the information needs.
- Ollama 0.40.16 (installed with Homebrew). Ollama (United States). https://github.com/ollama/ollama . Licence: MIT. Use: runs gpt-oss:20b on the lead's computer. Not part of the product.
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
- It gives counts per environment for two presets only: the ISS cabin and the lunar habitat.

What was not checked:

- No combustion specialist reviewed the ranking rules, the needs or the results. The rules were compared with one textbook, which does not cover flame spread over solid materials.
- The six needs, and the links between purpose sentences and needs, were written with an AI assistant. No person has reviewed them.
- All 24 catalog rows were extracted with an AI assistant and are not yet checked by a person.
- The reference items were transcribed with an AI assistant and are not yet checked by a person. Of the 65 documents (66 entries; one paper is listed twice), 54 were read in full, 8 as an abstract or catalogue page only, 1 is known only through a citation, 1 was read by a teammate session and 1 from an unofficial copy.
- The expected answers of the validation scenarios were written by an AI session for the team, not by a specialist.
- "Written in the source" means the number appears there. It does not mean its meaning was checked.
- The oxygen and pressure ranges of each scenario are the team's bins. The lunar range reaches up to 85.8 kPa, above the 70.3 kPa (10.2 psi) that the challenge statement names.
- [PLANNED C: The written card summaries were reviewed by a second AI session, not by a person.]

## Numbers used

Every number in the text above, outside the References list. "Snapshot" means the main branch at about 15:10 KST on 14 November 2026. Paths are relative to the repository root. Bibliographic values inside the References list (record versions, DOIs, report numbers, dates, page counts, library versions) were generated by script from `data/psi/manifest.json`, `pipeline/spec/references.json` and `compliance/SOURCES.md`; they are not repeated here. Document names such as NASA-STD-6001B or NASA/TP-2015-216046 are identifiers, not counts.

| Number | What it is | Source file and filter | Recheck at freeze |
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
| 133, 0, 2, 298, 122, 0 | Counted tests per need (P1, P2, P3, S1, D1, D2) | `data/pipeline/need_tests.csv`, `objective_link` = stated, by `need_id` | yes |
| 408 | Different tests counted for at least one need | `data/pipeline/need_tests.csv`, distinct `test_id` where `objective_link` = stated | yes |
| 246; 30 to 40% | Gas-flame tests with a surrounding oxygen of 30% or more (30.03 to 40.0%); none counted | `data/pipeline/tests.csv`, `fuel_phase` = gas, `o2_basis` = ambient, `o2_pct` >= 30; none in `need_tests.csv` with `objective_link` = stated | yes |
| 92 and 154 | Of the 246: tests in `need_tests.csv` for S1 with `objective_link` = not_stated (all ACME CFI-G); tests in no need (131 Flame Design, 23 ACME CFI-G) | same filter, joined to `data/pipeline/need_tests.csv` | yes |
| 4 of 6 | Needs with counted tests in the ISS-cabin range | `data/pipeline/scenario_needs.csv`, `scenario_id` = iss, needs where `tests_atmosphere` + `tests_oxygen_only` + `tests_pressure_only` > 0 | yes |
| 55, 2, 63, 45 | ISS cabin: counted tests in range for P1, P3, S1, D1 | same file and filter, sum of the three columns per need | yes |
| 56 of the 63; one need | ISS cabin, S1: tests with both oxygen and pressure in range; S1 is the only need with such tests | `data/pipeline/scenario_needs.csv`, `scenario_id` = iss, `tests_atmosphere` (56 for S1, 0 for the others) | yes |
| three needs on oxygen alone (3 of the 4) | ISS cabin: P1, P3 and D1 match through `tests_oxygen_only` only | same file, `scenario_id` = iss, `tests_atmosphere` = 0 and `tests_oxygen_only` > 0 | yes |
| 1 of 6 | Needs with counted tests in the lunar range | `data/pipeline/scenario_needs.csv`, `scenario_id` = lunar_habitat, same rule | yes |
| 17 | Lunar range, S1: FLEX droplet tests | same file, `need_id` = S1, `tests_atmosphere` | yes |
| 9 and 8 | Of the 17: methanol and heptane tests | `data/pipeline/scenario_tests.csv` joined to `tests.csv` and `need_tests.csv`, by material | yes |
| 30.0% or 34.0% | Oxygen of the 17 tests | same join, `o2_pct` | yes |
| 71.2 to 72.4 kPa | Pressure of the 17 tests (71.23 to 72.37) | same join, `pressure_kpa` minimum and maximum | yes |
| about 1 to 2 kPa; "just above" | Distance of the 17 tests above 70.3 kPa (0.93 to 2.07) | computed from the line above; wording of decision 14:15 in `coord/decisions.md` | yes |
| 15 and 2 | Of the 17: "disruption" and "completion" in the "Test end" column | same join, `test_end`; also `data/pipeline/evidence/scenario_lunar_habitat.json`, need S1, indicator `S1.test_end` | yes |
| 0 | Counted tests at 30% oxygen or more and at or below 70.3 kPa | `data/pipeline/tests.csv` joined to `need_tests.csv`, ambient `o2_pct` >= 30 and `pressure_kpa` <= 70.3 | yes |
| 1 (18% oxygen, 70.2 kPa) | Counted tests at or below 70.3 kPa at any oxygen: one FLEX test (Open points only) | same join, `pressure_kpa` <= 70.3 | yes |
| 20; 33 to 39%; 50.7 kPa | Recorded tests at 30% oxygen or more and at or below 70.3 kPa: ACME CFI-G gas flames (33.2 to 39.3% oxygen, 50.665 kPa) | `data/pipeline/tests.csv`, `o2_basis` = ambient, `o2_pct` >= 30, `pressure_kpa` <= 70.3 | yes |
| 18 and 2 | Of the 20: tests with a recorded test end, in `need_tests.csv` for S1 as not_stated; tests in no need | same filter, joined to `data/pipeline/need_tests.csv`; `test_end` | yes |
| all 20 on the gas grid | 9 in the cell 30 to 36% oxygen, below 62.8 kPa; 11 in the cell above 36%, below 62.8 kPa | `data/pipeline/coverage_grid.csv`, `fuel_phase` = gas, `o2_basis` = ambient | yes |
| 0 of 376 | Solid-fuel tests with a recorded pressure | `data/pipeline/tests.csv`, `fuel_phase` = solid, numeric `pressure_kpa` | yes |
| 139; 22.2%; 0 at 30% or more | Solid-fuel tests with a recorded surrounding oxygen; highest value; number at 30% or more | `data/pipeline/tests.csv`, `fuel_phase` = solid, `o2_basis` = ambient, numeric `o2_pct` | yes |
| 19 to 23% oxygen; 85.8 to below 116.8 kPa | ISS-cabin scenario range | `pipeline/spec/scenarios.json`, id = iss, `ranges` | no |
| 30 to 36% oxygen; below 85.8 kPa | Lunar scenario range | `pipeline/spec/scenarios.json`, id = lunar_habitat, `ranges` | no |
| 30% oxygen or more; 70.3 kPa (10.2 psi) or less | What the challenge statement expects for the Moon ("likely") | `pipeline/spec/scenarios.json`, lunar_habitat `note`; `coord/requests/20261114-1305-ui-to-data-...md`; challenge statement | no |
| 100% oxygen; 4.3 psi | Spacesuit preset, from the challenge statement | `scoring/scoring_config.json`, presets, spacesuit `source` | no |
| 79.1, 79.1, 76.1 | Team scores of the lunar-habitat result cards (ACME-BRE, FLEX, ACME-CFI-G) | `scoring/scorer.py` rank("lunar habitat") with `scoring/scoring_config.json` version 1.1.0 | yes |
| 94, 94, 92.7 | Team scores of the ISS result cards (BASS-II, BASS, SAFFIRE-II), as the page prints them (Python prints 94.0) | `scoring/scorer.py` rank("ISS"), same configuration; `web/app.js` prints `String(r.score)` | yes |
| 41 | Test configurations in the catalog | `data/catalog/configurations.csv` rows | no |
| 0 to 100; 0 to 1; up to half; three cards; 3 points | Score scale; similarity scale; largest cut by the gate; results shown; margin inside which evidence quality sets the order | `scoring/scoring_config.json` (profiles, gate, evidence, selection: `top_k` 3, `tie_points` 3.0; `complementary_slot`); `scoring/scorer.py`. Full formula: score = 100 x evidence factor x gate x weighted sum; gate between 0.5 and 1.0 when fuel or oxygen similarity is below 0.2; evidence factor = 0.7 + 0.3 x mean of three ratings | no |
| six (6) buttons | Preset buttons on the page | `web/index.html`, the `presets` group | yes |
| two presets | Environments with counts per need on the page (ISS cabin, lunar habitat) | `web/app.js`, `DASH_SCENARIOS` | yes |
| 6 and 20 | Evidence packages: environments and single oxygen-and-pressure cells | `data/pipeline/evidence/index.json`, packages by kind | yes |
| 246 and 30 | Tests in the downloadable "matched tests" CSV, ISS cabin and lunar habitat | `data/pipeline/scenario_tests.csv`, tiers other than "other", as written by `web/build.py` | yes |
| 38 of 38 | Unit tests of the ranking code that pass | `scoring/test_scorer.py`; run read-only for this draft: `python3 -B -m unittest scoring.test_scorer` | yes |
| 35 of 35 | Validation scenarios that pass | `validation/report.md` (run 14:59); not re-run for this draft | yes |
| 86 of 86 | Queries with the same ranking in Python and JavaScript | `coord/status/catalog.md` (14:59); `web/parity_check.py`; as reported, not re-run for this draft | yes |
| 0.05; 5 of 5 | Weight change; scenarios where first place stays | `validation/report.md` | yes |
| 45 of 48; 1; 2; four queries | Weight sensitivity (each prevention weight x 0.5 and x 1.5) | `validation/report.md`, sensitivity section; `validation/sensitivity.py` | yes |
| 107 of 115; 8; 24 of 24; 135 of 135 | Catalog values against the NASA sources | `validation/catalog_source_check.md`; not re-run | yes |
| 46 of 46 | Checks of the separate pipeline checker | `data/pipeline/validation_report.json`, summary; not re-run | yes |
| 11; 33; 0; 70 of 70 | Integration check and page reading | `coord/status/ui.md` (14:33); as reported, not re-run | yes |
| 1,824 test links | Tests whose source row is a number and lies inside an existing table file | `data/pipeline/tests.csv`, `source_file` and `source_row`, against the 14 files in `data/psi/experimental_tables/`; also `coord/status/ui.md` (14:33) | yes |
| 2012 | Year of the textbook used for the rule check | `scoring/MODEL_BASIS.md` | no |
| 0 wrong in 80 frames; 1 of 19 clips | Checks of the BASS-II video pilot | `coord/status/pm.md` (15:10); as reported | yes |
| gpt-oss:20b; Ollama 0.40.16 | Model and runtime | `ai/config.py`; `compliance/SOURCES.md`; `README.md`, "AI layer" (lead's working tree) | yes |
| at most three | Summary sentences the model may write per card | `README.md`, "AI layer" (lead's working tree) | yes |
| 23 of 24; PSI-10 | PSI records with the CC0-1.0 licence; the record with no licence stated | `data/psi/manifest.json`, licence field per investigation | no |
| 66 entries; 65 documents; 54, 8, 1, 1, 1 | Reference entries; documents (AIAA-2012-3536 and ICES-2012-SAME2 are one paper, both read in full); how much of each was read | `pipeline/spec/references.json`, entries and `access` field (55 entries read in full, minus the duplicate) | yes |
| 264; 24 | Verbatim quotes in the needs specification; quotes longer than 40 words | `pipeline/spec/references.json`, items with a `quote` field, by word count | yes |
| 28 and 7 | Reference lines whose terms come from the NTRS copyright field; lines with no open licence found or read | `https://ntrs.nasa.gov/api/citations/<id>`, field `copyright.determinationType`, read on 14 November 2026; not in the repository | no |
| 15:10; 19:00; 14 November 2026 | Time of the snapshot; time of the freeze; date | task brief; `coord/status/pm.md` | no |
| 583b3d4 | Commit of the main branch that was read | product fact sheet (snapshot of main at 15:14 KST) | no |
| Claude Opus 5.5 | Model name in the team's usage log (a name, not a count) | `compliance/AI_USAGE_LOG.md` | no |
| two entries | Usage-log rows that say the user confirmed the work in conversation | `compliance/AI_USAGE_LOG.md`, rows of 11/13 and 11/14 10:30 (review column) | no |
| 190 (193 if A lands) | Words in the High-Level Summary (limit: 50 to 200) | counted with a script after the last edit | yes |
| [FILL] | Cards with a model-written summary; model sentences proposed, removed and shown; reviewer kind | `data/insights/cards.json`, `data/insights/quality.json`, `ai/review/review_sheet.csv` after the final build | yes |

## Open points

Sentences marked PLANNED in this draft. Each letter marks sentences to keep or delete at the freeze.

- A. The Constraints part "What NASA's recorded tests showed" on the page. Request 20261114-1505-pm-to-ui; decision 15:10. Due 17:30. At 15:10 the page had two Constraints parts, and the values were in the evidence package only. If A lands, also change the summary sentence named in the notes box.
- B. The evidence map. The page code exists and prints "Evidence map: not available yet." until `data/insights/evidence_map.json` lands. Request 20261114-1306-pm-to-ui; pm status 15:10.
- C. The written card summaries and the AI layer in the public repository. `data/insights/cards.json`; pm status 15:10; board tasks P3, P4, D5; decision 13:05 (review by a second AI session by default). C also decides which version of "SI in the product" stays.
- D. The list "What PSI does not contain for this environment" with "Data that would close it". Needs `data/insights/scenarios.json`; pm status 15:10.
- E. The four fixed "what is known" sentences. Decisions 15:10 and 15:14; pm's answer to request 20261114-1503. Only if the data files are ready by 17:45. Otherwise it stays under "What is next".
- F. The raw-data inventory line per investigation. Requests 20261114-1449-pm-to-ui (item 3) and 20261114-1449-pm-to-data; decision 15:00.

Not a sentence, but still open: new screenshots and GIF (board task U5, 21:00). The files in `web/media/` are drafts from 11:28 and show older results.

For a person to decide before submitting:

- Korean-language files in the linked repository. The English rule covers linked material. The repository holds Korean text in `AGENTS.md`, `compliance/SOURCES.md`, `compliance/AI_USAGE_LOG.md`, internal reports and other files. Either add English versions, or remove the repository link from the submission and from the page footer. The Korean words in `web/scorer.js` are input keywords, not prose; the README can say so.
- Quotes from copyrighted documents in the public repository. `pipeline/spec/references.json` holds 264 verbatim quotes, 24 of them longer than 40 words, some from paid standards and journal papers. The page does not show them. Shorten them or replace them with a paraphrase and a section number, except for US Government works and CC0 PSI files.
- The sentence on Chinese-made models under "What SI was not allowed to do" is a team rule. Decide whether it belongs in the public text. The maker of the Exa tool is not recorded, so the sentence has no check behind it for that tool yet.

For the team to do in the source log (`compliance/SOURCES.md`, append only; the job that wrote this draft could not touch it):

- Add rows for the reference documents that have none (43 of the 66 entries, by a count made for this draft), with the terms now given in the References list.
- Add rows for Claude Code, claude.ai, the Exa tool, React and sharp (links checked on 14 November: github.com/react/react, MIT; github.com/lovell/sharp, Apache-2.0).
- Add a correction row for the textbook: two property values (heat capacities of CO2 and N2) were taken from its Appendix A; the existing row says no numbers were copied.
- Check the edition of ASTM D2863. The References list says D2863-23e1; the source log says D2863-23.

Reference details still missing:

- The NTRS copyright field gives no public-use statement for 2 documents (NASA/TM-20210011385 and the JASMAC presentation) and notes possible copyright-protected material for 2 (ICES-2021-266 and the 2021 fire-detection white paper). All four are cited only.
- For 7 documents outside NTRS no open licence was found or read. One repository page (ICES-2017-224) did not open on 14 November.
- ISO 14624-1 has no link. PSI-10 states no licence. Google Fonts, Claude Code and claude.ai have no terms link.
- The terms page of the Exa tool answered with a file download when it was opened for this draft, so it was not read.

Wording choices in this draft:

- The brief says criteria are "quoted". The page shows a transcription of each item with its document and link, not the document's own words. This draft says "lists", not "quotes".
- The page heads the list "Criteria in NASA documents", but the list also holds items from ISO, ASTM, SAE and journal papers. This draft says "NASA standards and studies" (the page's own note) and "published documents".
- The draft pitch says "in minutes". No timing was measured. This draft does not say it.
- The page prints "Lunar base or pressurized rover" for the lunar preset in the at-a-glance and side-by-side lines. The button says "Lunar habitat". This draft says "lunar habitat".
- The page's method text says oxygen and flow weigh most and that a human check scales the score. Neither matches the current configuration. This draft does not repeat them.
- The challenge statement gives the lunar values as an expectation ("likely"), not as a stated bound. This draft says "expects" and "names", not "bound".
- "No recorded test" would be false for 30% oxygen or more at or below 70.3 kPa: 20 gas-flame tests are recorded there. This draft says "no counted test" and names the 20.
- "No counted test at or below 70.3 kPa" would also be false without the oxygen condition: one counted FLEX test lies at 18% oxygen and 70.2 kPa. This draft always gives both conditions.

Still to add by the team:

- The slide-deck link and the hardware.
- A row in `compliance/AI_USAGE_LOG.md` for this draft and for `slides_outline.md`. Both were written by an AI assistant.
