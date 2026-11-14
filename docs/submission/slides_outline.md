DRAFT written by an AI assistant (Claude) for the team to rewrite in its own words before submitting. Every number is listed at the end with its source.

> **For the team lead.** Delete this box before use.
>
> **1. Fill in.** Search for `[FILL`. Two items remain.
> - S1. The team name (slide 1, in two places).
> - S2. Slide 6: keep version A or version B, and delete the other. Both are complete. pm recommends version A, "Four AI-built parts, each with its measured check". The reason is your concern of 17:05, as request 1705 records it: AI looked like "a language model writes summaries" and nothing more, which is neither the whole truth nor a reason to remember the project. Version B is the title of the 15:10 draft. For version A, one of the two readers proposed the title "AI used four ways, each with a measured check" instead; both titles fit the words on the slide.
>
> **2. State of this outline.** Brought up to date at about 19:40 KST on 14 November 2026, from `main` as it stood at 19:05 (commit `7239a2e`). The page was built from that commit and read in a headless browser for the queries `ISS` and `lunar habitat`. Every feature the slides name is on that page. The freeze was lifted at 19:20, so recheck the rows marked "yes" in "Numbers used" if the page changes. Corrected at about 20:15 KST for the findings of two independent AI readers: no wording of the challenge statement stands in quotation marks, slides 5 and 6 (version A) carry fewer words, three titles say more, and every slide lists its AI mark.
>
> **3. Captures.** The captures for slides 1, 4 and 5 are in `web/media/` now. Four are not there yet: those for slides 2, 3 and 7, which the ui role's capture script already defines, and one new one for slide 6, version A. See "Captures" below.
>
> **4. The AI mark.** An AI assistant wrote the words and notes of every slide below. So each slide lists the mark "Built with AI assistance (Claude)" for its footer. Keep the mark on every slide whose words the team has not rewritten itself. The judges do not see the "Use of SI" answer; they see the marks inside the deck.
>
> - Exactly seven slides, title slide included. A deck of more than seven slides is left out of global judging.
> - Each slide gives: a short title that is a claim (ten words at most), the words on the slide (35 at most; names, captions, footers and source lines do not count), one visual with its capture, and a speaker note (60 words at most).
> - The judges come from astronomy and space science, data science, cloud and space business, and computer science. None works in combustion. Say each term once in plain words: microgravity is near-weightlessness; PSI is NASA's archive of these experiments; a need is one fire-safety question; kPa is a unit of pressure, and 70.3 kPa is 10.2 psi.

## The story in seven titles

1. What NASA's fire tests say, and where the evidence stops
2. Habitat designers describe their build; get the closest NASA experiments
3. 1,824 NASA tests in one table, counted by one rule
4. Counted tests: ISS cabin 4 of 6 needs, lunar 1
5. Observed, stated, published, missing: four kinds of evidence kept apart
6. Version A: Four AI-built parts, each with its measured check. Version B: Code computes every number; one local model writes cited summaries
7. Designers see what exists, what is missing, what to cite

Slides 2 to 5 carry a thin strip at the top with the three steps of the page: FIND, COMPARE, INTERPRET. The current step is marked: FIND on slide 2, COMPARE on slides 3 and 4, INTERPRET on slide 5.

## Where a judge finds each part of the organisers' suggested structure

The organisers suggest seven parts. They are a recommendation, not a rule. Each part is in this deck:

| Suggested part | Where it is |
|---|---|
| Title, team, challenge and problem | Slide 1: the names, and the problem as the challenge statement describes it |
| Problem and target users | Slide 2: who the tool is for, in the title and in the first words on the slide |
| Solution and key features | Slides 2, 3 and 5: the three steps FIND, COMPARE, INTERPRET |
| Visuals and user experience | Slides 1, 2, 3 and 5: captures of the public page |
| NASA data use | Slide 3: the NASA data are named on the slide and in its source line |
| Implementation, design choices and results | Slide 4 (results), slide 6 (how it was built and checked) |
| Impact, next steps and references | Slide 7: one sentence on who uses it and what they can do next, the next step, the references line |

## Slide 1

- **Title:** What NASA's fire tests say, and where the evidence stops
- **Words on the slide:** NASA's fire data: hard to find, harder to compare, harder yet to interpret (challenge statement). Lunar habitat, at 30% oxygen or more and a pressure of 70.3 kPa (10.2 psi) or less: no counted test.
- **Names on the slide:** Fire Evidence Explorer. [FILL S1: team name]. Challenge: Flame in Freefall.
- **Mark on the slide (footer, small type):** Built with AI assistance (Claude)
- **Visual:** A capture of the top of the public page: the title, the notice line ("Research exploration tool built on NASA Physical Sciences Informatics (PSI) data. It is not operational fire-safety guidance, and it is not endorsed by NASA."), the question "What are you building, and where?", the six example buttons and the at-a-glance line. The notice line must be readable. It is a capture of the team's own page, not an AI-generated image. Use no NASA logo.
- **Capture:** `web/media/02_lunar_first_screen.png` (in the folder; its at-a-glance line reads "ISS cabin 4 of 6 · Lunar base or pressurized rover 1 of 6"). The ui role's `slide1_top.png` shows the same top without the at-a-glance line; it is not in the folder yet.
- **Speaker note:** We are [FILL S1: team name]. NASA publishes its microgravity (near-weightlessness) fire experiments as open data; the challenge calls them hard to find, compare and interpret. Type what you are building and where. The page shows what the recorded tests say, and where the evidence stops. Lunar habitat, at 30% oxygen or more and 70.3 kPa or less: no counted test.

## Slide 2

- **Title:** Habitat designers describe their build; get the closest NASA experiments
- **Words on the slide:** For engineers who design a crewed habitat, and for combustion researchers. Type rough words. Code ranks 24 NASA investigations and shows reasons, the largest gap and the dataset DOI. Scores are ours, not NASA's.
- **Mark on the slide (footer, small type):** Built with AI assistance (Claude)
- **Visual:** A capture of the first result card for the query "ISS": BASS-II, team score 94, the strip of similarities, "Why", the links, the raw-data line and the "Weight check" line. Keep the page's note above the cards in the capture ("Scores (0–100) and order are the team's similarity computation, not a NASA result, and not operational safety guidance."). If "What the record says" is open in the capture, the summary shows its label "AI-generated, reviewed by second AI session (data role)"; leave the label visible.
- **Capture:** `slide2_iss_result.png`. Not in `web/media/` yet. The ui role's capture script defines it (`node web/capture_media.mjs`). No file in the folder shows a result card.
- **Speaker note:** For engineers who design crew equipment or habitats, and for researchers. Step one, FIND. Type rough words, such as "ISS". Code compares your conditions with 24 NASA investigations and shows the closest, with reasons, the largest gap and the dataset DOI, the permanent identifier that NASA's archive asks users to cite. No language model ranks anything. The scores are ours.

## Slide 3

- **Title:** 1,824 NASA tests in one table, counted by one rule
- **Words on the slide:** NASA's PSI archive: 24 combustion investigations, 22 tables. 14 read into one, same columns and units. Six fire-safety questions (needs). A test counts for one only if investigators or a NASA document state that purpose.
- **Mark on the slide (footer, small type):** Built with AI assistance (Claude)
- **Source line on the slide:** Data: NASA Physical Sciences Informatics (PSI), psi.nasa.gov, 24 combustion investigations, each cited by its dataset DOI. Criteria: NASA, ISO and ASTM standards, NASA reports and papers, listed on the page with their documents.
- **Visual:** A capture of the needs table for the query "ISS": one row per investigation, the column groups Prevention, Suppression and Detection, and the cell statuses such as "Measured" and "Outside stated objective". Keep the page's note in the capture ("Status is the team's pipeline reading of each PSI experimental table, not a NASA assessment.").
- **Capture:** `slide3_iss_needs.png`. Not in `web/media/` yet. The ui role's capture script defines it.
- **Speaker note:** Step two, COMPARE. We read 14 tables of NASA's PSI archive into one: 1,824 tests, each value with its NASA row. A test counts for a question only if the investigators or a NASA document state that purpose. 92 gas-flame tests at high oxygen record how the flame ended, but no document read states a fire-safety purpose: shown, not counted.

## Slide 4

- **Title:** Counted tests: ISS cabin 4 of 6 needs, lunar 1
- **Words on the slide:** ISS cabin: 4 of 6 needs, 3 of them on oxygen alone, because their tables record no pressure. Lunar habitat: 1, from 17 droplet tests at 71 to 72 kPa, just above 70.3 kPa.
- **Mark on the slide (footer, small type):** Built with AI assistance (Claude)
- **Visual:** A table built in the slide tool, with six rows and two columns, from the numbers below. Source line under the table: "Team counts from NASA PSI tables, 14 November 2026. Not NASA conclusions." Caption: "Shown on the page as 'Lunar base or pressurized rover' (the Lunar habitat button)."

  | Need | ISS cabin | Lunar habitat |
  |---|---|---|
  | Flammability limit | 55, oxygen only | 0 |
  | Ignition | 0 | 0 |
  | Flame spread and growth | 2, oxygen only | 0 |
  | Extinction conditions | 63, 56 with oxygen and pressure | 17, at 71 to 72 kPa |
  | Combustion products | 45, oxygen only | 0 |
  | Smoke generation conditions | 0 | 0 |

- **Capture:** `web/media/03_compare_iss_lunar.png` (in the folder), small, next to the table, to show that the page holds the same counts. Its counts are current. The note under its table was reworded on the page after the capture: retake it, or crop the capture to the table.
- **Speaker note:** Same page, two environments. ISS cabin: counted tests for four of six needs, three of them on oxygen alone. Lunar habitat: one need. Its 17 droplet tests were recorded at 71 to 72 kPa, just above the 70.3 kPa that the challenge names. Our lunar range is our own choice and reaches 85.8 kPa, so these tests fall inside it.

## Slide 5

- **Title:** Observed, stated, published, missing: four kinds of evidence kept apart
- **Words on the slide:** Observed: values from NASA's recorded tests. Not limits. Stated: criteria in standards and studies. No test judged against them. Published: results outside the archive, quoted. Not counted. Missing: conditions with no counted test. Not predicted.
- **Mark on the slide (footer, small type):** Built with AI assistance (Claude)
- **Visual:** A table built in the slide tool, with four columns, for the lunar habitat. The four parts of the words above are the column headers, so the words stand on the slide once. Under each header, one cell with one sentence:
  - Observed: "17 droplet tests at 30 or 34% oxygen, just above 70.3 kPa."
  - Stated: "34 items for the flammability need, mostly definitions and requirements, each with its document."
  - Published: "A paper's table includes two solid-fuel samples of a later flight at about 30 to 31% oxygen and about 54 kPa."
  - Missing: "0 counted tests at 30% oxygen or more and at or below 70.3 kPa."

  The detail behind each cell is in the submission text, "A worked example".
- **Capture:** `web/media/04_lunar_evidence_map.png` (in the folder), under the table: the evidence map for "lunar habitat", with the solid-fuel lane ending at 22.2% oxygen and the input marked at 30%. Keep a caption: "Recorded tests by oxygen. Team plot from NASA PSI tables." Other choices in the folder: the head of `05_lunar_constraints.png` (the need-by-need block with its four parts; the file is very tall and must be cropped, and its text changed after the capture) or `06_lunar_coverage_solid.png` (the grid for solid fuels: 0 recorded tests at 30 to 36% oxygen at any pressure).
- **Optional line under the visual (data-lab):** "The lunar point lies inside the tested range of oxygen and inside the tested range of pressure, each taken alone, and outside the region covered when both are taken together (273 droplet tests of one investigation). Recomputed by a second AI agent. Reviewed by a person: 0." Use it only if the branch `data-lab` opens logged out.
- **Speaker note:** Step three, INTERPRET. For each question the page keeps four things apart. What the tests showed: observed values, not limits. What standards and studies state: we judge no test against them. What was published outside the archive: quoted, never counted. And where the evidence stops. Twenty gas-flame tests exist at 50.7 kPa and high oxygen, but none is counted.

## Slide 6

[FILL S2: keep version A or version B and delete the other. pm recommends A.]

### Version A (recommended by pm)

- **Title:** Four AI-built parts, each with its measured check
- **Words on the slide:** Ranking by rules: 38 of 38 cases; browser matches Python, 99 of 99. Language model: 70 sentences, 33 shown. Prediction test: 9 outcomes, 1 passed, no model shipped. Video reader: about 750 values, none wrong.
- **Mark on the slide (footer, small type):** Built with AI assistance (Claude)
- **Visual:** Four boxes built in the slide tool, one per part. Each box carries only its part of the words above: the name of the part and its numbers. Nothing else stands in a box. What each part does and how it was checked is said in the speaker note and written in the submission text, "Use of SI", parts 1 to 4.

  Footer under the boxes: "Checks by code and by AI sessions. Model sentences reviewed by a second AI session: 61. Reviewed by a person: 0. Built with an AI coding assistant (Claude); the code files say so. The site calls no model."
- **Capture:** the block "How AI is used here, and how it was checked" of the public page, small, next to the boxes. It prints "70 sentences written by the model, 5 refused by code checks, 4 removed by a first reading, 28 removed by the review, 33 shown" and "Reviewed by a second AI session: 61. Reviewed by a person: 0." No capture of this block is in `web/media/`, and the capture script does not define one: ask the ui role for it (page section `#ai-use`). The slide also works without it.
- **Speaker note:** We used AI in four ways and measured each. The ranking is rules, not a language model. One local model wrote 70 sentences; code checks and AI sessions removed 37, and 33 are shown. A prediction test passed for one of nine outcomes; we ship no model. A reader copied on-screen numbers from 19 NASA videos; its flame timing failed.

### Version B (the title of the 15:10 draft)

- **Title:** Code computes every number; one local model writes cited summaries
- **Words on the slide:** Built with an AI coding assistant (Claude); the code files say so. Code computes every number. One local open model, gpt-oss:20b, wrote 70 cited sentences; 33 are shown. No model on the site.
- **Mark on the slide (footer, small type):** Built with AI assistance (Claude)
- **Visual:** A simple diagram with two lanes that end in one box, built in the slide tool. Lane 1: NASA PSI tables, then team code, then counts, ranks and fixed sentences. Lane 2: PSI record text, then gpt-oss:20b on the team's computer (70 sentences), then code checks (5 refused), then a first reading (4 removed), then the review by a second AI session (28 removed), then 33 sentences with the label "AI-generated". End box: the public page, which calls no model. Footer: "Reviewed by a second AI session: 61. Reviewed by a person: 0."
- **Capture:** none needed. The same capture as in version A can sit next to the diagram.
- **Speaker note:** An AI coding assistant wrote most of our code, under our direction. Code computes every count and rank. One open-weight model, run locally, wrote 70 summary sentences. Code checks refused 5. A first reading removed 4. A second AI session reviewed 61 and removed 28. Reviewed by a person: 0. 33 are shown. None is reworded.

## Slide 7

- **Title:** Designers see what exists, what is missing, what to cite
- **Words on the slide:** An engineer planning a crewed habitat sees which NASA fire tests exist, downloads them with NASA source rows and DOIs, and sees which conditions have no counted test. Next: review by combustion researchers.
- **Footer on the slide (small type):** Research exploration tool, not safety guidance. Counts and rankings are the team's computation, not NASA's conclusions. References: NASA PSI dataset DOIs on every result; the full list is on the project page.
- **Mark on the slide (footer, small type):** Built with AI assistance (Claude)
- **Visual:** A capture of one opened list of test ids in the section "Recorded tests in the scenario range" for the query "ISS"; each id is a link to its row in the repository copy of the NASA table. Under it, the public link: https://choidol0208.github.io/NASA_RAPID/
- **Capture:** `slide7_iss_tests.png`. Not in `web/media/` yet. The ui role's capture script defines it.
- **Speaker note:** An engineer can take the matched tests, with their NASA rows and citations, into their own tools, and sees which conditions still lack a counted test. All 1,824 tests link to their row in our copy of the NASA table. Next: review of the ranking rules and of the fire-safety questions by combustion researchers. A research tool, not safety guidance.

## Captures

In `web/media/` now (all taken from the public page by the ui role's script and committed at 16:31 on 14 November):

| File | Size in pixels | What it shows | Slide |
|---|---|---|---|
| `01_iss_first_screen.png` | 2560 x 1600 | First screen for "ISS": title, notice line, question, six buttons, at-a-glance line, start of "How your input was read" | 1, as an alternative |
| `02_lunar_first_screen.png` | 2560 x 1600 | The same first screen for "lunar habitat" | 1 |
| `03_compare_iss_lunar.png` | 2160 x 920 | The block "ISS and lunar habitat, side by side" with its counts | 4; retake or crop, because the note under the table changed |
| `04_lunar_evidence_map.png` | 2160 x 778 | The evidence map for "lunar habitat": three lanes on one oxygen axis, the input marked | 5 |
| `05_lunar_constraints.png` | 2160 x 9232 | The need-by-need block for "lunar habitat" with the first need open | 5, as an alternative; crop it; retake, because its text changed |
| `06_lunar_coverage_solid.png` | 2160 x 912 | The grid of solid-fuel tests by oxygen and pressure for "lunar habitat cotton fabric" | 5, as an alternative |
| `07_lunar_phone.png` | 1170 x 2532 | The first screen on a phone | none; for the project page |
| `demo_iss_to_lunar.gif` | not measured | The demo story: ISS, then lunar habitat, the comparison, the evidence map | none; for the project page |
| `og.png` | 1200 x 630 | The link preview | none |

Not in `web/media/` yet:

| File | Slide | State |
|---|---|---|
| `slide1_top.png` | 1, as an alternative | Defined in `web/capture_media.mjs`; the ui role planned to take it after the freeze |
| `slide2_iss_result.png` | 2 | Defined in `web/capture_media.mjs`; needed, no other file shows a result card |
| `slide3_iss_needs.png` | 3 | Defined in `web/capture_media.mjs`; needed, no other file shows the needs table |
| `slide7_iss_tests.png` | 7 | Defined in `web/capture_media.mjs`; needed, no other file shows the list of test ids |
| a capture of the block "How AI is used here, and how it was checked" | 6, version A | Not defined in the script; ask the ui role |

Images in the body of the project page must be JPG, PNG or GIF of 10 MB or less. All files above are below that.

## Rules for the whole deck

- English only. Seven slides at most.
- No NASA logo, flag or mission mark. Nothing that implies NASA endorsement.
- Any image or diagram made by an AI tool carries a visible "AI-generated" mark. If an AI assistant writes a slide or the code that draws it, that slide carries a visible "Built with AI assistance (Claude)" mark. An AI assistant wrote the words of all seven slides of this outline, so each slide lists the mark for its footer; it stays on every slide whose words the team has not rewritten itself. Captures of the team's own page are not AI-generated images; the page itself states that it was built with AI assistance.
- Every capture that shows a score or a count keeps the page's note that the value is the team's computation.
- Say "counted tests", not "tests", for the 4 of 6 and 1 of 6 lines. Wherever the lunar count is shown, also say that its 17 tests lie just above 70.3 kPa.
- Say "no counted test", never "no recorded test", for 30% oxygen or more at or below 70.3 kPa. 20 gas-flame tests with a surrounding oxygen of 30% or more are recorded there. Always give both conditions: one counted test lies just below 70.3 kPa at 18% oxygen.
- Say "solid fuels" for any line about 22.2% oxygen or about pressure that is not recorded.
- Do not call the ISS top three an order. BASS-II, BASS and SAFFIRE-III are level under the team's weights.
- Do not say "validated", "safe", "unsafe" or "NASA found". Do not say what would happen in an untested condition. Do not treat results at 0 g and 1 g as bounds for lunar or Martian gravity.
- Say who checked: code and AI sessions. "Reviewed by a person: 0" stays as a count where the model sentences are counted and after the optional data-lab line of slide 5; no other line says who did not check. Review by combustion researchers is said once, on slide 7, as the next step: in the words on the slide and in its speaker note. Nothing may suggest that a person, a specialist or NASA reviewed or approved the work.
- No wording of the challenge statement stands in quotation marks. No file in the repository holds the challenge text word for word; to quote it, compare the phrase with the official challenge page first.
- The full disclaimer is said once, on slide 7. Slide 1 shows it in the capture of the page's notice line.
- The deck link must open without a login.

## Numbers used

Each value was read from the named file in the working copy of `main` at 19:05 KST on 14 November 2026 (commit `7239a2e`), or from the page built from it, or was printed by a command run for this draft. The rows changed by the corrections of 20:15 were confirmed in the same files in the working copy of commit `30c1301`, which differs from `7239a2e` in coordination files only. Paths are relative to the repository root. The same numbers, with the same sources, are in `submission_text.md`.

| Number | Where it is used | Source file and filter | Recheck before submitting |
|---|---|---|---|
| 30% oxygen or more; 70.3 kPa (10.2 psi) or less | Slides 1, 4, 5: what the challenge statement expects for the Moon (likely; wording as reported in `pipeline/spec/references.json`, item CH.moonbase, not a verbatim quote) | `pipeline/spec/references.json`, CH.moonbase; `pipeline/spec/scenarios.json`, lunar_habitat `note`; the page's preset source line | no |
| no counted test (0) | Slides 1, 5: counted tests at 30% oxygen or more and at or below 70.3 kPa | `data/pipeline/tests.csv` joined to `need_tests.csv`, ambient `o2_pct` >= 30 and `pressure_kpa` <= 70.3 | yes |
| one counted test at 18% oxygen | Deck rules: the only counted test at or below 70.3 kPa (FLEX, 70.2 kPa); it is why both conditions must be said | `data/pipeline/tests.csv` joined to `need_tests.csv` (`objective_link` = stated), `pressure_kpa` <= 70.3 | yes |
| six | Slide 1: example buttons in the capture. Slide 3: fire-safety questions (information needs) | the built page; `pipeline/spec/needs.json` | yes |
| 4 of 6; 1 of 6 | Slide 1 capture, slide 4: needs with counted tests in the ISS-cabin range and in the lunar range | `data/pipeline/scenario_needs.csv`, needs where `tests_atmosphere` + `tests_oxygen_only` + `tests_pressure_only` > 0; the page's at-a-glance line | yes |
| 24 | Slides 2, 3: investigations in the catalog | `data/psi/manifest.json`; `data/catalog/investigations.csv` rows | no |
| 94 | Slide 2: team score of BASS-II for the query "ISS", as the page prints it | the built page for `?q=ISS`; `scoring/scoring_config.json` version 1.1.0 | yes |
| 22; 14 | Slide 3: experimental tables in PSI; tables read into the common table | `data/psi/manifest.json`, sum of `experimental_tables`; `data/pipeline/tests.csv`, distinct `source_id` | yes |
| 1,824 | Slides 3, 7: recorded tests | `data/pipeline/tests.csv` rows | yes |
| 92 | Slide 3 speaker note: gas-flame tests with a surrounding oxygen of 30% or more that record a test end and are not counted | `data/pipeline/tests.csv` (`fuel_phase` = gas, `o2_basis` = ambient, `o2_pct` >= 30) joined to `need_tests.csv` (S1, `objective_link` = not_stated) | yes |
| 3 of them; four of six; three | Slide 4: ISS cabin, P1, P3 and D1 match through `tests_oxygen_only` only, because none of the 376 solid-fuel tests records a pressure | `data/pipeline/scenario_needs.csv`, `scenario_id` = iss, `tests_atmosphere` = 0 and `tests_oxygen_only` > 0 | yes |
| 55, 2, 63, 45; 56 | Slide 4 table: ISS cabin, counted tests in range for P1, P3, S1, D1; S1 tests with oxygen and pressure in range | `data/pipeline/scenario_needs.csv`, `scenario_id` = iss; the page's side-by-side block | yes |
| 17 | Slides 4, 5: FLEX droplet tests in the lunar range | `data/pipeline/scenario_needs.csv`, lunar_habitat, `need_id` = S1, `tests_atmosphere` | yes |
| 71 to 72 kPa; just above 70.3 kPa | Slides 4, 5: pressure of the 17 tests (71.23 to 72.37) | `data/pipeline/tests.csv`, `pressure_kpa` of the 17 tests; decision 14:15 in `coord/decisions.md` | yes |
| 85.8 kPa | Slide 4 speaker note: upper edge of the team's lunar range | `pipeline/spec/scenarios.json`, id = lunar_habitat, `ranges` | no |
| 30 or 34% | Slide 5: oxygen of the 17 tests | `data/pipeline/tests.csv`, `o2_pct` of the 17 tests | yes |
| 34; mostly definitions and requirements | Slide 5: items the page lists for the flammability need of the lunar habitat, under the fold "Criteria, requirements and definitions": 21 definitions, 8 requirements, 3 recommendations, 1 acceptance criterion, 1 design value; 20 from NASA documents, 7 from ISO and ASTM standards, 7 from papers | `data/pipeline/answers/lunar_habitat__P1.json`, `frame.criteria`; the `type` of each item in `pipeline/spec/references.json` | yes |
| two samples; about 30 to 31% oxygen; about 54 kPa | Slide 5: Saffire-VI samples VI-2 (31.0% oxygen, 54.1 kPa) and VI-3 (30.3%, 54.6 kPa), two of the five samples in Table 1 of a paper (ICES-2024-365) | `data/pipeline/answers/lunar_habitat__P1.json`, `rung3_published.at_the_environment`; `pipeline/spec/references.json`, item SAF456.conditions | yes |
| 22.2%; 30% | Slide 5 capture: highest recorded oxygen of a solid-fuel test; the marked input | `data/pipeline/tests.csv`, `fuel_phase` = solid, `o2_basis` = ambient; the capture | yes |
| 0 at 30 to 36% | Slide 5, alternative capture: solid-fuel tests at 30 to 36% oxygen at any pressure | the page's grid for solid fuels; `data/pipeline/coverage_grid.csv` | yes |
| twenty (20); 50.7 kPa | Slide 5 speaker note and deck rules: recorded, uncounted gas-flame tests with a surrounding oxygen of 30% or more and at or below 70.3 kPa (33.2 to 39.3% oxygen) | `data/pipeline/tests.csv`, `o2_basis` = ambient, `o2_pct` >= 30, `pressure_kpa` <= 70.3 | yes |
| 273 | Slide 5, optional line: tests counted for S1 that record both oxygen and pressure | branch `data-lab`, `data/pipeline/lab/numbers/envelope_lunar_habitat.md`; recomputed for this draft from `data/pipeline/tests.csv` | yes (branch public?) |
| four kinds of evidence; four AI-built parts | Slide 5: the four parts of each need on the page. Slide 6, version A: ranking by rules, language model, prediction test, video reader, all written with an AI coding assistant | `web/app.js`, `renderNeedAnswer`; `submission_text.md`, "Use of SI", "In short" | no |
| 38 of 38 | Slide 6: ranking test cases with an expected answer | `validation/report.md` (run 18:34); not re-run | yes |
| 99 of 99 | Slide 6: queries with the same ranking in Python and JavaScript | run for this draft: `python3 -B web/parity_check.py` | yes |
| 70; 5; 4; 28; 33; 37 | Slide 6: model sentences written; refused by code checks; removed by a first reading; removed by the review; shown; removed in all (5 + 4 + 28). Version A shows 70 and 33 and says 37 in its note; version B and the capture give 5, 4 and 28 | `data/insights/quality.json`: `proposed`, `dropped_by_gates`, `removed_before_review.n`, `removed_by_review`, `shipped_model_sentences`; the page prints the first five | yes |
| 61; 0 | Slide 6: model sentences reviewed by a second AI session; by a person | `data/insights/quality.json`, `reviewed_ai_session`, `reviewed_person`; the page prints both | yes |
| 9; 1 | Slide 6, version A: outcomes tried in the prediction test; passed a first test (the other verdicts: 6 too few, 1 counts only, 1 cannot be modelled) | `data/insights/model_readiness.json`, `rows`, `verdict` | yes |
| 19 clips; about 750 values; none wrong | Slide 6, version A: the video reader and its check; its flame timing failed (right in at most 1 of 19 clips) | `video/README.md` | no |
| gpt-oss:20b | Slide 6, version B: the model | `ai/config.py`; the page's label on each summary | no |
| 1,824 links | Slide 7: tests whose source row is a number and lies inside an existing table file | recomputed for this draft from `data/pipeline/tests.csv` against `data/psi/experimental_tables/` | yes |
| 16:31; pixel sizes | Captures table: time of the commit that holds the captures; sizes | `git log -- web/media`; PNG headers of the files in `web/media/` | no |
