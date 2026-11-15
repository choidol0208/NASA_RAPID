# Challenge fit: the product against the challenge statement

*AI-generated (Claude Code, pm role) on 15 November 2026 for the NASA Space Apps Challenge 2026 hackathon. Read by a person: none yet.*

What this is: a check of the product (the page in `web/`, the ranking in `scoring/`, the data, the assistant and the submission texts) against the challenge statement "Flame in Freefall", as pasted by the team lead on 15 November 2026. Three auditors compared the two; the pm session re-checked every gap below against the files and the built page (scratch build of `web/dist`, rendered with headless Chrome) before keeping it. Items that did not hold were dropped or re-rated.

Ratings: **covered**, **partly**, **not covered**, **contradicts**. "Owner" follows the team's split: pm owns `ai/`, `docs/`, `README.md` and the page shell and labels; catalog owns `scoring/` and `data/catalog/`; data owns `pipeline/` and `data/pipeline/`; ui owns the rest of `web/`.

## 1. The challenge's words, and where the product answers them

In the statement's order. "Fix" points to the numbered gap in section 2.

### Objectives

| Challenge's words | Where the product answers | Rating | Fix |
|---|---|---|---|
| "Results ... are being made publicly available through NASA's Physical Science Informatics (PSI) database, but the amount of data can be overwhelming." | Tab "Where the data are": the three piles (in NASA's tables, in the archive, no record) and a reading order over 60,866 files. Lunar query: "26 tests are recorded inside these ranges; 398 of the 60,866 files in PSI (0.77% of the bytes) carry their names." | covered | – |
| "It can be hard to find, harder to compare, and harder yet to interpret." | Masthead and landing strip: "Find, Compare, Interpret". Section kickers. | partly: the tab labels ("Closest investigations", "What was found", ...) carry no verb, and inside "What was found" an "Interpret" block comes before "Compare". | G14 |
| "build an SI-powered, web-based dashboard" | Four SI uses, each labelled: cited card summaries (how.html section 1: "70 sentences written by the model ... 33 shown ... Reviewed by a person: 0"); the assistant replay ("This public page runs no language model"); deck slide 6. | partly: how.html measures only the card sentences and never describes the assistant; the page's "How the assistant was checked" fold is rendered `hidden` because no evaluation file exists; `docs/assistant/README.md` line 158: "Results: not yet measured." | G6 |
| "... that summarizes ..." | Top-3 result cards ("What the record says": objective, findings, cited AI summary); "At a glance"; "What is known for <environment>, need by need". | partly: typing an investigation the statement names gives a false message (G2). | G2 |
| "... ranks ..." | "Closest NASA investigations" cards with a per-dimension strip, "Why", "Largest gap", weight check ("First in 88.4% of the 8,000 sampled weightings"); "All investigations" (all 24); how.html "How the score works". | covered (small: the glance prints scores out of order, "75.2, 71.6, 73.6", without the reason). | G15 |
| "... and interprets combustion science investigations to deliver critical foundational insights for fire safety." | "What was found" (quotes with printed values, by question); "Where the evidence stops" (oxygen map, "What PSI does not contain"). | partly: the most important lunar insight ("no solid-sample test with a recorded oxygen value above 22.2%", against 30% in the environment) sits deep in "Where the evidence stops"; the glance gives counts only. Printed values lose their quantity names (G9). | G9, G11 |
| "Identify investigations most relevant to the fire safety needs of habitable crew environments, including spacecraft, space stations, bases on the lunar and Martian surfaces, and pressurized rovers." | Presets and aliases in `scoring/scoring_config.json` (ISS, lunar base or pressurized rover, Mars base, spacesuit); the Ask box presets; "Closest investigations". | partly: "Artemis" is read as the lunar base (G3); the Mars notice is a developer instruction (G12); investigation names are refused with a false message (G2). | G2, G3, G12 |
| "Extract data that supports predictive modeling of flammability and fire scenarios in space exploration." | "Take the data with you": matched-tests CSV, evidence package, `tests.csv` (1,824 rows, units in column names, source file and row), `values_long.csv`, `results_flat.csv`; how.html section 2 "Can these NASA tables support an outcome model?". | partly: the export block never says which file serves a modeller, and does not link the readiness verdict. | G7 |
| "Highlight research that informs the development of next-generation fire safety controls and equipment." | Needs grouped under Prevention, Suppression, Detection; detection and suppression questions reweight the ranking; FLEX diluent quotes; SAME particle sizes; NASA-STD-6001B criteria. The ventilation caveat (ICES19.lowpressure: "deactivating the ventilation, as is currently done on the ISS, may not be sufficient to extinguish a flame in high oxygen lower pressure atmospheres") is on the lunar page, but only after opening "need by need" > Extinction conditions > the closed fold "Stated without these conditions". | partly: the instruments behind each investigation are not shown (G5); the one control-related caveat is three clicks deep. | G5 |
| "In this challenge, you'll help turn complex data into clear answers ..." | Glance lines; fixed sentences per need. | partly: the rendered lunar page holds 596 paragraphs and list items; the longest (502 words) is the scenario frame. Covered by G1 and G11, not a separate fix. | G1, G11 |
| "Your dashboard could also address potential applications of the PSI data to fire safety on Earth. Fine-water-mist extinguishers ... smoke detection and firefighter gear ..." | Only the recorded assistant conversation "Applications on Earth". | partly: the current recording (16:36) shows two sentences, both about combustors and coal power plants (PSI-10). The PSI records hold fire-safety sentences it skips (PSI-102 SAME: "smoke detectors ... useful in other extreme environments on Earth, such as submarines or underwater laboratories"; PSI-98, PSI-25, PSI-69). No PSI record mentions water mist or firefighter gear. `submission_text.md` line 318 says so honestly. | G8 |
| Footnote: "Fire safety involving rockets and propellants is generally beyond the scope ... The high velocities within rocket engines render the combustion effectively independent of gravity" | `keywords.out_of_scope` and `warnings.out_of_scope`; page status "Out of scope for this tool."; assistant notice. | covered, with one false refusal: "ACME combustion chamber 40% oxygen" returns out_of_scope because "combustion chamber" is an out-of-scope keyword, though the statement itself describes the CFI-G combustion chamber. | G13 |

### Background (one item a judge will try)

| Challenge's words | Where the product answers | Rating | Fix |
|---|---|---|---|
| "a smoke alarm that went off during the recent Artemis II mission ... in your spacecraft" | `presets.lunar_habitat.aliases` includes "artemis". | contradicts: `scorer.rank('Artemis II smoke alarm')` reads lunar gravity, 30% O2 and 70.3 kPa, with the partial-gravity notice, and "ii" not understood. The statement's example is a spacecraft in flight. | G3 |

### Potential Considerations

| Challenge's words | Where the product answers | Rating | Fix |
|---|---|---|---|
| "target audience can include professors, graduate students, undergraduate students, aerospace researchers, and aerospace engineers" | `submission_text.md` line 295: "for engineers who design equipment or a habitat ... and for researchers". Plain-word definitions on the page. | partly: students and professors are not named anywhere (0 hits in README, submission, outline, page). | G16 |
| Attributes: "Experimental objectives" | Every card: "Objective (catalog summary)" and the stated objective quoted from the PSI record; 24 of 24 catalog objectives filled. | covered | – |
| Attributes: "Fuels, including shape and size of the samples or burners" | Card "Closest test configuration", requirement row "Sample shape and thickness"; `configurations.csv` geometry and sizes. | covered for solids, droplets, BRE and SPICE; burner sizes empty for some ACME burners and SLICE, shown as "Not reported". Not a gap for today. | – |
| Attributes: "Other test conditions, such as oxygen concentration and airflow speed" | Dimension strip, "Why", "Largest gap", the oxygen map; `tests.csv` o2_pct with o2_basis, flow_cms. | covered | – |
| Attributes: "Variables: how did tests from the same investigation differ and how were they the same?" | `data/pipeline/investigation_facts.json` holds constants and varied values per investigation table. | partly: no page or assistant file reads it, and it is not copied to `web/dist/data`. The page shows only the tests inside the scenario range. | G10 |
| Attributes: "Sensors or types of measurements" | `configurations.csv` measured_outputs, 41 of 41 filled (video, extinction condition, flame spread rate, radiant flux, gas species, soot volume fraction, ion current ...). | not covered on the page: 0 hits for "radiant flux", "soot volume fraction", "ion current" in the rendered ISS, lunar and smoke pages; the card (`web/app.js` "What the record says") shows objective and findings only. | G5 |
| "how to summarize and display similarities and differences between different investigations" | Dimension strips on the top 3; "All investigations" with "Match by dimension"; "ISS and lunar habitat, side by side" (compares environments). | partly: every comparison is against the query; nothing shows that investigations share a project or hardware. | G5 (hardware line) |
| "One of the instruments used for smoke detection in the SAME and SAME-R studies was instead used to detect dust in ... DAFT and DAFT-2" | Catalog row DAFT (PSI-47): hardware "TSI P-Trak", objective "Risk reduction for SAME ..."; scored as not from a fire, so it ranks below SAME, SAME-R and SAME-SIM for smoke detection. | covered | – |
| "the Burning Rate Emulator (BRE) ... was a study of materials flammability in still atmospheres as a function of material properties" | ACME-BRE: tier 1, prevention, quiescent; card: "Evidence comes from gaseous-fuel tests; apply to solid materials with caution." | covered | – |
| "Other combustion investigations within the PSI database ... are still relevant to fire safety, just not as strongly or directly." | All 24 investigations ranked for every query; tiers and role weights in `scoring_config.json` (fundamental 0.4). | covered | – |
| Hardware: "six experiments in the ACME project ... same modular set of ACME hardware in the Combustion Integrated Rack (CIR)" | `investigations.csv` hardware for the six ACME rows. | partly: in the data, not on the page (0 hits for "Combustion Integrated Rack"). | G5 |
| Hardware: "FLEX, FLEX-2, and ... CFI ... Multi-user Droplet Combustion Apparatus (MDCA) in the CIR" | `investigations.csv` hardware. | partly: in the data, not on the page (0 hits for "MDCA"). | G5 |
| Hardware: "BASS, BASS-II, SPICE, and SLICE ... within the Microgravity Science Glovebox (MSG) using the modular fan-driven flow duct built for SPICE" | `investigations.csv` hardware; SLICE hardware cell empty, source_notes "Uses the SPICE fan-driven flow duct in the MSG." | partly: not on the page (0 hits for "flow duct"); SLICE cell empty; the duct is not named for BASS, BASS-II or SPICE. | G5 |
| "spacesuits are filled with 100% oxygen to only 4.3 psi ... sea level is 14.7 psi" | Preset spacesuit: 100% O2, 29.6 kPa, source "spacesuits at 100% O2 and 4.3 psi (29.6 kPa)"; Earth 21%, 101.3 kPa. | covered | – |
| "astronauts pre-breathe 100% oxygen to expel absorbed nitrogen" | Background only; no product action expected. | covered (no action needed) | – |
| "Moon Base and pressurized rover(s) will be at a pressure and oxygen concentration between those in a spacesuit and the Earth's atmosphere" | Preset lunar_habitat "Lunar base or pressurized rover", alias "rover". | covered | – |
| "30% or greater, with a corresponding pressure of 10.2 psi or less ... more than a 40% increase" | Preset 30% / 70.3 kPa with the statement as source; the page says where its counting range goes above 10.2 psi. | covered | – |
| "Microgravity tests with the highest oxygen concentrations ... CFI-G ... up to 85% oxygen ... inside-out flame" | CFI-G card: "oxidizer up to 85% O2 ... O2 here is the oxidizer stream of an inverse flame, not the surrounding atmosphere"; `tests.csv` max: 85.0 (oxidizer_stream), 40.0 (ambient). | covered; one clarity fix: the spacesuit warning says "highest surrounding-atmosphere O2 ... 40%" with no mention of the 85% a judge has just read. | G17 |
| "there is currently no partial-gravity combustion data available in PSI. We expect such data will be added in the future, for example from ... LUCI and ... FM2" | `warnings.partial_gravity` on every lunar, Mars and rover query; `tests.csv` gravity_level microgravity for 1,824 of 1,824 rows. LUCI results quoted as "related NASA experiment, not a PSI investigation". | covered for "no data"; partly for the future sources: FM2 0 hits, "Lunar-g" 0 hits, and no sentence calls LUCI a future PSI source (though `references.json` CH.partial_gravity says the page does). | G4 |
| "Partial gravity was mimicked in ACME's ... (E-FIELD Flames) experiment through the effect of the electric field on the ions" | `investigations.csv` ACME-E-FIELD key_findings: "relevant as a partial-gravity analog". | partly: not on the page; E-FIELD ranks 20th for "lunar habitat" with no note. | G4 |
| "Microgravity and normal-gravity results could bound what occurs at intermediate gravity levels." | Page notice: "they are not bounds for lunar or Martian gravity"; deck slide 4 footer; slide 7 note; `submission_text.md` lines 153, 496, 730; README line 320; `model_readiness.json`. | contradicts as worded: the product states the opposite with no source and without naming the statement. The decision itself is supported by NASA data (section 3). | G1 |

## 2. Gaps, most important first

**G1. The partial-gravity wording contradicts the statement and cites no reason.** (pm and catalog, 25 minutes, worth high)
The notice reads "All results here are microgravity tests; they are not bounds for lunar or Martian gravity. NASA names partial-gravity material flammability a major gap (OCHMO-TB-008)." TB-008 supports the gap, not the "not bounds" clause. Speaker note 7 says "Every test here ran in microgravity, so nothing bounds lunar or Martian gravity", which links two facts that do not follow from each other. The NASA evidence is in the repository (`pipeline/spec/references.json` OF2012.table1) and is already used by the lunar frame (`ai/templates.py`).
Fix: replace the wording with the three sentences in section 3 (all pass `ai.checks.lint_text`). Places: `scoring/scoring_config.json` warnings.partial_gravity (catalog); `docs/submission/deck/build_deck.py` WORDING footer of slide 4 and note of slide 7, then rebuild the deck (pm); `docs/submission/slides_outline.md` lines 18, 94, 139 (pm); `docs/submission/submission_text.md` lines 153, 496, 730 (pm); `README.md` line 320 (pm); `data/insights/model_readiness.json` last caveat (pm, at its generator if it has one). Then run `python3 -m unittest scoring.test_scorer` and rebuild `web/dist`.

**G2. Typing an investigation the statement names gives a false message.** (catalog, 5 minutes; pm, 2 minutes; worth high)
`scorer.rank('BASS')` and the page for `?q=BASS` say: "No PSI investigation or keyword matches 'bass'; the ranking uses the rest of the query and these words change nothing." BASS is PSI-26. The same holds for BASS-II, FLEX, SAME, CFI-G, DAFT and the others. This is likely the first thing a judge holding the statement types.
Fix: `scoring/scoring_config.json` warnings.not_understood to: "The ranking does not read these words: {words}. It reads an environment, a material, a purpose and conditions; investigation names are not ranking terms, and every investigation is listed under All investigations." (lint-clean). `docs/submission/submission_text.md` line 76: "Words that match nothing in PSI are named" to "Words the ranking does not read are named".

**G3. "Artemis" is read as the lunar base.** (catalog, 5 minutes, worth high)
The statement's first example is a smoke alarm in a spacecraft in flight; the product answers it with lunar gravity, 30% O2, 70.3 kPa and the partial-gravity notice.
Fix: remove "artemis" from `presets.lunar_habitat.aliases`. Tried on a scratch copy: "Artemis II smoke alarm" then reads as a detection question with no environment assumed (SAME and SAME-R 97.0), and "smoke alarm in a spacecraft" reads the ISS cabin (SAME 94.6). No test pins "artemis".

**G4. The statement's future sources and the E-FIELD analog are not named.** (catalog, 5 minutes; pm, 5 minutes; data, 5 minutes; worth medium)
FM2 appears nowhere; LUCI is quoted but never called a future source; the E-FIELD analog lives only in the catalog CSV.
Fix: append to the partial-gravity notice (lint-clean): "The challenge statement names the Lunar-g Combustion Investigation (LUCI) and the Flammability of Materials on the Moon (FM2) experiment as expected future sources, and ACME's E-FIELD Flames (PSI-22) as an experiment in which an electric field mimicked partial gravity." Put the same sentence in the submission's "what is next". Data: correct CH.partial_gravity in `pipeline/spec/references.json`, which claims "the page names LUCI as a future source".

**G5. Measurements and hardware are in the catalog but not on the cards.** (ui, 15 minutes; catalog, 3 minutes; worth high)
The statement asks for "Sensors or types of measurements" and describes the CIR, MDCA and MSG flow duct; the page shows neither (0 hits for "Combustion Integrated Rack", "MDCA", "flow duct", "radiant flux", "soot volume fraction").
Fix: `web/app.js`, card "What the record says", after the objective line, two lines: "Measured (catalog): " from `conf.measured_outputs` (split on ";", underscores to spaces, or "not stated"), and "Hardware (catalog): " from `inv.hardware` (or "not stated"). Catalog: fill SLICE hardware with "Microgravity Science Glovebox (MSG), SPICE fan-driven flow duct (source_notes; challenge statement)".

**G6. The assistant has no measured check on the public page.** (pm, 15 minutes, worth high)
how.html section 1 counts only the card sentences; the fold "How the assistant was checked" is rendered `hidden`; `docs/assistant/README.md` says "Results: not yet measured."
Fix: add a point "The assistant" to how.html "How AI is used here": the page replays conversations recorded on 15 November with gpt-oss:20b run locally; each model sentence was checked by code against its cited facts and removed if it failed (the recording lists removed sentences and why); the 74-question evaluation is "not yet measured", or its numbers if the run lands before 18:00. Keep deck slide 6 on "Four uses of SI and how each is checked" with "measurement in progress" until then.

**G7. The export block does not say which file serves a modeller.** (ui, 10 minutes, worth high)
Fix: one sentence in "Take the data with you": "For a predictive model: tests.csv has one row per test, units in the column names, and each row's NASA file and row. Whether these tables can support an outcome model is in How it works, section 2: 1 of 9 outcome labels is indicative, and none is a cabin-material flammability model." Link to the how.html section.

**G8. Earth applications lead with combustors, not fire safety.** (pm, 20 minutes, worth medium)
Fix: in `ai/assistant/tools.py` earth_units (currently sorted by accession only), sort units whose text matches fire, smoke, safety or detector first, then re-record only the "earth" conversation. If re-recording is not possible today, add a static fold to `web/index.html` quoting the four record sentences (PSI-102, PSI-98, PSI-25, PSI-69) with their ids, and the line "Water mist (MIST, STS-107) and firefighter gear are not in the PSI records used here." Update `submission_text.md` line 318 if the page gains the fold.

**G9. Printed values lose their quantity names.** (ui, 5 minutes, worth high)
The lunar page prints "Printed values: sample=M1: 1 mm; sample=M1: 2.2 cm; sample=M1: 1; sample=M1: [9] cm/s ...". Cause: `web/results_first.py` `_value_label` takes `row_label` before `column` or `quantity`.
Fix: `lab = " ".join(x for x in (v.get("material_as_printed") or v.get("row_label"), v.get("column") or v.get("quantity")) if x)`, then rebuild.

**G10. What varied between tests is computed but not shipped.** (ui, 10 minutes for the quick version, worth medium)
Fix (quick): copy `data/pipeline/investigation_facts.json` to `web/dist/data` in `web/build.py` and add a card link "What stayed the same and what varied between tests (JSON)". A one-line rendering of constants and ranges is a 30-minute follow-up.

**G11. The lunar glance omits the oxygen fact that matters most.** (ui, 15 minutes, worth medium)
Fix: when the environment's oxygen is above the highest solid-sample oxygen, add to the glance the sentence the evidence map already prints: "No solid-sample test in PSI's tables records oxygen above 22.2%; this environment is at 30%." Link it to "Where the evidence stops". It is a recount, not a prediction.

**G12. The Mars notice is a developer instruction.** (catalog, 5 minutes, worth medium)
The page shows: "The challenge text gives no Mars atmosphere; ask the user for O2 and pressure."
Fix: `presets.mars_habitat.source` to "The challenge text gives no Mars atmosphere; type an oxygen and a pressure to place tests (for example 34% O2 at 8.2 psi, a NASA exploration atmosphere)."

**G13. "Combustion chamber" is refused as rocketry.** (catalog, 5 minutes, worth medium)
Fix: remove "combustion chamber" and "연소실" from `keywords.out_of_scope`. Tried on a scratch copy: "ACME combustion chamber 40% oxygen" then ranks (97.0 first), and "hybrid rocket combustion chamber fire" stays out of scope. Optional, 3 minutes: give the statement's reason in `warnings.out_of_scope`: "Rocket and propellant fire safety is generally outside the scope of PSI research: combustion inside rocket engines is effectively independent of gravity (challenge statement)."

**G14. The Find, Compare, Interpret promise does not reach the tabs.** (pm, 10 minutes, worth medium)
Fix: change the `#results-first` kicker in `web/index.html` to "Compare · What NASA's documents report", so the order inside "What was found" reads Compare before Interpret.

**G15. The glance prints scores out of order with no reason.** (ui, 10 minutes, worth low)
"FLEX, ACME-CFI-G, ACME-BRE (match scores 75.2, 71.6, 73.6)". Fix: when the scores are not descending, add "(third place goes to the closest result tested at your oxygen; see All investigations)".

**G16. Students and professors are not named as users.** (pm, 5 minutes, worth medium)
Fix: `submission_text.md` line 295 and the summary: add "and for professors and students who teach or learn microgravity combustion: each card quotes the investigation's stated objective, and every value links to its NASA table row."

**G17. The 85% and the 40% read as a conflict.** (catalog, 5 minutes, worth low)
Fix: append to `warnings.o2_above_all`: "The highest O2 in PSI, up to 85% in ACME CFI-G, was the oxidizer stream of an inverse flame, not the surrounding atmosphere."

Also seen, not worth time today: the assistant does not resolve "CFI-G", "BRE", "E-FIELD" or "DAFT-2" (`resolve_names` returns [] because the PSI acronyms are "ACME CFI-G" and "DAFT / DAFT-2"); deck slide 4 says "Smoke ... no counted test" without saying SAME and SAME-R tested detection but their PSI tables list conditions only; `references.json` CH.pillars still says "read from a copy" (the pasted text matches it).

## 3. Where the product differs from the statement on purpose

**Partial gravity: 0 g and 1 g results are not treated as bounds.** The statement suggests that "Microgravity and normal-gravity results could bound what occurs at intermediate gravity levels." NASA's own drop-tower data, in the repository, show why the page does not use them that way. Olson and Ferkul (NTRS 20130010991, AIAA 2012-3492), Table I, limiting oxygen (% O2):

| Material | 1 g (ULOI / MOC) | 0 g | Lunar | Martian |
|---|---|---|---|---|
| Mylar G, 10.2 psia | 21.2 / 20.0 | 17.0 / 16.0 | 15.6 / 14.1 | 18.0 / 17.0 |
| Ultem 1000, 10.2 psia | 23.5 / 23.0 | 24.0 / 23.0 | 21.0 / 19.9 | 22.0 / 21.1 |
| Nomex HT90-40, 14.7 psia | 23.5 / 22.1 | 23.0 / 22.0 | 21.0 / 19.9 | 19.9 / 19.0 |

Recount: at lunar gravity both limits lie below both the 0 g and the 1 g values for all three materials. At Martian gravity this holds for Ultem and Nomex; Mylar G lies between. The low-gravity values come from 5.18 s drops with extinction criteria that the paper says are not the same as in 1 g, and the paper concludes "Normal-gravity screening tests may not be conservative." NASA OCHMO-TB-008 calls material flammability in partial gravity "a major gap for exploration missions." So the page does not claim the statement is wrong; it says that for oxygen limits of these materials the recorded NASA data fall outside the 0 g to 1 g span, and it shows those data. The current wording does not do this yet (G1).

**No safety verdicts.** The product is a research exploration tool. It shows NASA's criteria (for example NASA-STD-6001B 7.1.3a, "A material is self-extinguishing if no specimen burns more than 15 cm") next to the tests, and does not judge a material or a habitat against them. Source: the standard's acceptance tests are run by NASA test facilities under defined conditions; a similarity score from PSI tables is not such a test.

**No prediction for untested conditions.** The statement asks for data that "supports predictive modeling"; the product supplies the data and the team's readiness check, and offers no model output. Source: the team's diagnostics on the PSI tables (how.html section 2): 1 of 9 outcome labels beats the base rate, and that one is a droplet-flame outcome, "not a cabin-material flammability model". For a lunar habitat no solid-sample test in PSI's tables records oxygen above 22.2%, so any number at 30% would be an extrapolation; the page says so instead.

## 4. What we decided not to do

- No new view comparing two investigations side by side; the hardware line on each card (G5) carries the shared projects and facilities.
- No ranking by investigation name; names lead to "All investigations", and the false message is fixed (G2).
- No burner sizes added where no PSI record states them; the page keeps "Not reported".
- No water-mist or firefighter-gear claims: the PSI records used here do not mention them.
- No re-wording of the challenge's own numbers; the presets cite them as they are.
- No change to the lunar order of results: it follows the documented oxygen rule, and G11 explains why solids rank lower.
