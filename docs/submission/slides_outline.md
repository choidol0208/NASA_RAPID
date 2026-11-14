DRAFT written by an AI assistant (Claude) for the team to rewrite in its own words before submitting. Every number is listed at the end with its source.

> Notes for the team. Delete this box before use.
> - Exactly seven slides, title slide included. A deck of more than seven slides is left out of global judging.
> - Facts were read from the main branch at about 15:10 KST on 14 November 2026. The page was read from its code. The live site was not opened.
> - Each slide gives: a short title that is a claim, the words on the slide (35 at most; names, captions and source lines do not count), one visual, and a speaker note (60 words at most).
> - Before use, search this file for `[FILL`. No such mark may remain. "Depends on" names a feature that was planned before the freeze and was not on the page at 15:10. The letters A to F are the same as in `submission_text.md`. Each such slide has a fallback.
> - Pressures are in kPa. 70.3 kPa is 10.2 psi; the deck says so once, on slide 1.
> - The files in `web/media/` are drafts from 11:28 and show older results. Take new captures after the freeze (board task U5).

## The story in seven titles

1. What NASA's fire tests say, and where the evidence stops
2. Type a rough description; get the closest NASA investigations
3. 1,824 NASA tests in one table, counted by one rule
4. Counted tests: ISS cabin 4 of 6 needs, lunar habitat 1 of 6
5. Three kinds kept apart: observed, stated, missing
6. Code computes every number; one local model writes cited summaries
7. Each test links to its NASA row; specialist review next

Slides 2 to 5 carry a thin strip at the top with the three steps of the page: FIND, COMPARE, INTERPRET. The current step is marked: FIND on slide 2, COMPARE on slides 3 and 4, INTERPRET on slide 5.

## Slide 1

- **Title:** What NASA's fire tests say, and where the evidence stops
- **Words on the slide:** ISS cabin: counted tests in the oxygen range for 4 of 6 fire-safety needs. Lunar habitat, at 30% oxygen or more and 70.3 kPa (10.2 psi) or less: no counted test.
- **Names on the slide:** Fire Evidence Explorer. [FILL: team name]. Flame in Freefall.
- **Visual:** A capture of the top of the public page: the title, the notice line ("Research exploration tool built on NASA Physical Sciences Informatics (PSI) data. It is not operational fire-safety guidance, and it is not endorsed by NASA."), the question "What are you building, and where?" and the six example buttons. The notice line must be readable. It is a capture of the team's own page, not an AI-generated image. Use no NASA logo.
- **Speaker note:** We are [FILL: team name]. You type what you want to build and where. The page shows what NASA's recorded fire tests say for it, and where the evidence stops. ISS cabin: counted tests in the oxygen range for four of six fire-safety needs. Lunar habitat, at 30% oxygen or more and 70.3 kPa or less: no counted test.
- **Depends on:** nothing planned.

## Slide 2

- **Title:** Type a rough description; get the closest NASA investigations
- **Words on the slide:** The closest of 24 NASA investigations, each with a team score, the reasons, the largest gap and its dataset DOI. Code ranks them; no language model does. Scores are ours, not NASA's.
- **Visual:** A capture of the first result card for the query "ISS": BASS-II, team score 94, the strip of similarities, "Why", "Largest gap" and the links. Keep the page's note above the cards in the capture ("Scores (0–100) and order are the team's similarity computation, not a NASA result, and not operational safety guidance."). It is a capture of the team's own page.
- **Speaker note:** NASA publishes these experiments in its Physical Sciences Informatics archive, PSI. The challenge calls the data hard to find, harder to compare and harder yet to interpret. We take those three steps. Step one: type rough words, for example "ISS". Code compares your conditions with 24 investigations and shows the closest, with reasons, gaps and the dataset DOI.
- **Depends on:** nothing planned. If the written card summaries (C) are on the page, the capture will show one with its "AI-generated" label; leave the label visible.

## Slide 3

- **Title:** 1,824 NASA tests in one table, counted by one rule
- **Words on the slide:** 14 NASA tables, same columns and units. Six needs: flammability limit, ignition, flame spread, extinction, combustion products, smoke. A test counts for a need only if the investigators or a NASA document state that purpose.
- **Visual:** A capture of the needs table for the query "ISS": one row per investigation, the column groups Prevention, Suppression and Detection, and the cell statuses such as "Measured" and "Outside stated objective". Keep the page's note in the capture ("Status is the team's pipeline reading of each PSI experimental table, not a NASA assessment."). It is on the page now.
- **Speaker note:** Step two. We put 1,824 recorded tests into one table. A test counts for a need only if the investigators or a NASA document state that purpose. For example, 92 gas-flame tests at 30 to 40% oxygen record how the flame ended. No document we read states a fire-safety purpose, so they are shown, not counted.
- **Depends on:** nothing planned.

## Slide 4

- **Title:** Counted tests: ISS cabin 4 of 6 needs, lunar habitat 1 of 6
- **Words on the slide:** ISS cabin: 3 of the 4 on oxygen alone. Lunar habitat: 17 droplet tests at 71 to 72 kPa, for extinction. At 30% oxygen or more and 70.3 kPa or less: no counted test.
- **Visual:** A table built in the slide tool, with six rows and two columns, from the numbers below. Source line under the table: "Team counts from NASA PSI tables, 14 November 2026. Not NASA conclusions." Caption: "Shown on the page as 'Lunar base or pressurized rover' (the Lunar habitat preset)."

  | Need | ISS cabin | Lunar habitat |
  |---|---|---|
  | Flammability limit | 55, oxygen only | 0 |
  | Ignition | 0 | 0 |
  | Flame spread and growth | 2, oxygen only | 0 |
  | Extinction conditions | 63, 56 with oxygen and pressure | 17, at 71 to 72 kPa |
  | Combustion products | 45, oxygen only | 0 |
  | Smoke generation conditions | 0 | 0 |

  A small capture of the block "ISS and lunar habitat, side by side" can sit next to the table, to show that the page holds the same counts. It is on the page now.
- **Speaker note:** Same page, two environments. ISS cabin: counted tests for four of six needs, three of them on oxygen alone. Lunar habitat: one need. Its 17 droplet tests were recorded at 71 to 72 kPa, just above the 70.3 kPa that the challenge names. Our lunar range is a team bin that reaches 85.8 kPa, so these tests fall inside it.
- **Depends on:** nothing planned.

## Slide 5

- **Title:** Three kinds kept apart: observed, stated, missing
- **Words on the slide:** Observed: values from NASA's recorded tests, with test counts. Not limits. Stated: criteria in NASA standards and studies, with source. Not judged. Missing: conditions with no counted test. Not predicted.
- **Visual:** A table built in the slide tool, with three columns and one cell each, for the lunar habitat:
  - Observed: "17 droplet tests at 30 or 34% oxygen. The NASA table records how each ended: 'disruption' 15, 'completion' 2. It does not define these words, so we do not interpret them."
  - Stated: "Items from NASA standards and studies, listed for each need with links. Example: NASA-STD-6001B."
  - Missing: "0 counted tests at 30% oxygen or more and at or below 70.3 kPa. 0 solid-fuel tests with a recorded pressure. 0 tests at lunar gravity."

  A small capture of the grids under "Where the evidence stops" for the query "lunar habitat" can sit under the table. It is on the page now.
- **Speaker note:** Step three. Observed values describe the tests that were run. They are not limits. Stated criteria come from NASA standards and studies. We judge no test against them. Missing is where the evidence stops. Twenty gas-flame tests were recorded at 50.7 kPa and high oxygen, but no document we read states a fire-safety purpose, so they are not counted.
- **Depends on:** A. At 15:10 the page showed the second and third kind as their own sections. The first kind was in the evidence package download only. The slide holds in both cases. If the evidence map (B) lands, its capture for the lunar-habitat query can replace the capture of the grids. Check first that its counts agree with this slide.

## Slide 6

- **Title:** Code computes every number; one local model writes cited summaries
- **Words on the slide:** Built with an AI coding assistant (Claude); the code files say so. Code computes every number. One local open model, gpt-oss:20b, writes at most three cited sentences per card. No model on the site.
- **Visual:** A simple diagram with two lanes that end in one box. Lane 1: NASA PSI tables, then team code, then counts, ranks and statements. Lane 2: PSI record text, then gpt-oss:20b on the team's computer, then code checks, then review, then the label "AI-generated". End box: the public page, which calls no model. Build it in the slide tool.
- **Speaker note:** An AI coding assistant wrote most of our code, under our direction. Code computes every count and rank. One open-weight model, run locally, drafts card summaries. Code checks each sentence for its citation, its numbers and advice or prediction words. A second AI session, not a person, then reviews it. Any sentence either one flags is removed, never reworded.
- **Fill at the freeze:** [FILL: number of cards with a model-written summary]; [FILL: number of model sentences proposed, removed and shown]; [FILL: reviewer, a second AI session or a role named in the review sheet; change the speaker note if a person reviewed].
- **Depends on:** C. Fallback if the summaries are not on the page. Title: "Code computes every number; no language model writes page text". Words: "Built with an AI coding assistant (Claude); the code files say so. Code computes every number. No language model writes text on the page. The site calls no model." Diagram: lane 1 only. Speaker note: keep the first two sentences, then say "No text on the page comes from a language model."

## Slide 7

- **Title:** Each test links to its NASA row; specialist review next
- **Words on the slide:** All 1,824 tests link to their NASA table row. Python and browser rankings agree: 86 of 86 queries. 35 of 35 cases pass. No specialist review yet. Not safety guidance. Counts are ours, not NASA's.
- **Visual:** A capture of one opened list of test ids in the section "Recorded tests in the scenario range" for the query "ISS"; each id is a link. It is on the page now. Under it, the public link: https://choidol0208.github.io/NASA_RAPID/
- **Speaker note:** All 1,824 tests link to their row in our copy of the NASA table. The ranking gives the same answers in Python and in the browser. It passes 35 of 35 cases whose expected answers an AI session wrote for us. No combustion specialist has reviewed the work; that comes next. This is a research tool, not safety guidance.
- **Depends on:** nothing planned. If the four "what is known" sentences (E) do not land, the team may name them as a next step in the speaker note.

## Rules for the whole deck

- English only. Seven slides at most.
- No NASA logo, flag or mission mark. Nothing that implies NASA endorsement.
- Any image or diagram made by an AI tool carries a visible "AI-generated" mark. If an AI assistant writes a slide or the code that draws it, that slide carries a visible "Built with AI assistance (Claude)" mark. Captures of the team's own page are not AI-generated images; the page itself states that it was built with AI assistance.
- Every capture that shows a score or a count keeps the page's note that the value is the team's computation.
- Say "counted tests", not "tests", for the 4 of 6 and 1 of 6 lines. Wherever the lunar count is shown, also say that its 17 tests lie just above 70.3 kPa.
- Say "no counted test", never "no recorded test", for 30% oxygen or more at or below 70.3 kPa. 20 gas-flame tests are recorded there. Always give both conditions: one counted test lies just below 70.3 kPa at 18% oxygen.
- Say "solid fuels" for any line about 22.2% oxygen or about pressure that is not recorded.
- Do not say "validated", "safe", "unsafe" or "NASA found". Do not say what would happen in an untested condition.
- The full disclaimer is said once, on slide 7. Slide 1 shows it in the capture of the page's notice line.
- The deck link must open without a login.

## Numbers used

"Snapshot" means the main branch at about 15:10 KST on 14 November 2026. Paths are relative to the repository root. The same numbers, with the same sources, are in `submission_text.md`.

| Number | Where it is used | Source file and filter | Recheck at freeze |
|---|---|---|---|
| 4 of 6; four of six | Slides 1, 4: needs with counted tests in the ISS-cabin range | `data/pipeline/scenario_needs.csv`, `scenario_id` = iss, needs where `tests_atmosphere` + `tests_oxygen_only` + `tests_pressure_only` > 0 | yes |
| in the oxygen range; 3 of the 4 on oxygen alone | Slides 1, 4: ISS cabin, P1, P3 and D1 match through `tests_oxygen_only` only | same file, `scenario_id` = iss, `tests_atmosphere` = 0 and `tests_oxygen_only` > 0 | yes |
| 30% oxygen or more; 70.3 kPa (10.2 psi) or less | Slides 1, 4, 5: what the challenge statement expects for the Moon ("likely") | `pipeline/spec/scenarios.json`, lunar_habitat `note`; challenge statement | no |
| no counted test (0) | Slides 1, 4, 5: counted tests at 30% oxygen or more and at or below 70.3 kPa | `data/pipeline/tests.csv` joined to `need_tests.csv`, ambient `o2_pct` >= 30 and `pressure_kpa` <= 70.3 | yes |
| one counted test at 18% oxygen | Deck rules: the only counted test at or below 70.3 kPa (FLEX, 70.2 kPa); it is why both conditions must be said | `data/pipeline/tests.csv` joined to `need_tests.csv` (`objective_link` = stated), `pressure_kpa` <= 70.3 | yes |
| six | Slide 1: example buttons in the capture. Slide 3: information needs | `web/index.html`, the `presets` group; `pipeline/spec/needs.json` | yes |
| 24 | Slide 2: investigations in the catalog | `data/psi/manifest.json`; `data/catalog/investigations.csv` rows | no |
| 94 | Slide 2: team score of BASS-II for the query "ISS", as the page prints it | `scoring/scorer.py` rank("ISS") with `scoring/scoring_config.json` version 1.1.0 | yes |
| 1,824 | Slides 3, 7: recorded tests | `data/pipeline/tests.csv` rows | yes |
| 14 | Slide 3: NASA tables in the common table | `data/pipeline/tests.csv`, distinct `source_id` | yes |
| 92; 30 to 40% | Slide 3 speaker note: gas-flame tests with a surrounding oxygen of 30% or more that record a test end and are not counted | `data/pipeline/tests.csv` (`fuel_phase` = gas, `o2_basis` = ambient, `o2_pct` >= 30) joined to `need_tests.csv` (S1, `objective_link` = not_stated) | yes |
| 1 of 6; one need | Slide 4: needs with counted tests in the lunar range | `data/pipeline/scenario_needs.csv`, `scenario_id` = lunar_habitat, same rule as for 4 of 6 | yes |
| 55, 2, 63, 45; 56 | Slide 4 table: ISS cabin, counted tests in range for P1, P3, S1, D1; S1 tests with oxygen and pressure in range | `data/pipeline/scenario_needs.csv`, `scenario_id` = iss, sum of the three columns per need; `tests_atmosphere` for S1 | yes |
| 17 | Slides 4, 5: FLEX droplet tests in the lunar range | `data/pipeline/scenario_needs.csv`, lunar_habitat, `need_id` = S1, `tests_atmosphere` | yes |
| 71 to 72 kPa | Slide 4: pressure of the 17 tests (71.23 to 72.37) | `data/pipeline/tests.csv`, `pressure_kpa` of the 17 tests; decision 14:15 in `coord/decisions.md` | yes |
| 85.8 kPa | Slide 4 speaker note: upper edge of the team's lunar range | `pipeline/spec/scenarios.json`, id = lunar_habitat, `ranges` | no |
| 30 or 34% | Slide 5: oxygen of the 17 tests | `data/pipeline/tests.csv`, `o2_pct` of the 17 tests | yes |
| 15 and 2 | Slide 5: "disruption" and "completion" among the 17 | `data/pipeline/evidence/scenario_lunar_habitat.json`, need S1, indicator `S1.test_end` | yes |
| 0 solid-fuel tests with a recorded pressure | Slide 5: of 376 solid-fuel tests | `data/pipeline/tests.csv`, `fuel_phase` = solid, numeric `pressure_kpa` | yes |
| 0 tests at lunar gravity | Slide 5: all 1,824 tests are microgravity | `data/pipeline/tests.csv`, `gravity_level` | yes |
| twenty (20); 50.7 kPa | Slide 5 speaker note: recorded, uncounted gas-flame tests at 30% oxygen or more and at or below 70.3 kPa (33.2 to 39.3% oxygen) | `data/pipeline/tests.csv`, `o2_basis` = ambient, `o2_pct` >= 30, `pressure_kpa` <= 70.3 | yes |
| three kinds | Slide 5: kinds of constraints | decision 15:10 in `coord/decisions.md` | no |
| gpt-oss:20b; at most three sentences | Slide 6: model and its limit per card | `ai/config.py`; `README.md`, "AI layer" (lead's working tree) | yes |
| 86 of 86 | Slide 7: queries with the same ranking in Python and JavaScript | `coord/status/catalog.md` (14:59); `web/parity_check.py`; as reported, not re-run for this draft | yes |
| 35 of 35 | Slide 7: validation scenarios of the ranking | `validation/report.md` (run 14:59); not re-run | yes |
| 1,824 links | Slide 7: tests whose source row is a number and lies inside an existing table file | `data/pipeline/tests.csv`, `source_file` and `source_row`, against `data/psi/experimental_tables/`; also `coord/status/ui.md` (14:33) | yes |
| [FILL] | Slide 6: cards with a model summary; sentences proposed, removed, shown; reviewer | `data/insights/cards.json`, `data/insights/quality.json`, `ai/review/review_sheet.csv` after the final build | yes |
