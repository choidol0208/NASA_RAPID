# How the ranking works: weighting rules, validation, data preprocessing

*AI-generated (Claude Code, catalog role), 2026-11-14, config 1.4.0. Written for the team. How the weights are derived (AHP), with the evidence and the checks for each purpose, is in `scoring/WEIGHTING.md`; the build-up of the weighting model (requirements layer, NASA data stream, expert form, pooling) and its sources are in `scoring/BUILDUP.md`.*

Scores and rankings are the team's computation, not NASA's conclusion, and not safety guidance. All values live in `scoring/scoring_config.json`; the code is `scoring/scorer.py` (Python) and its port `web/scorer.js` (the page).

---

## 1. Weighting rules

### 1.1 What is scored

- **Unit of scoring:** the unit is a **test configuration** in `data/catalog/configurations.csv`: 41 groups of tests that share a range of conditions, from 24 PSI investigations.
- **Each investigation:** it is represented by its best configuration.
- **Results:** the top 1 to 3 investigations are the result.

### 1.2 The score

```
score = 100 × M × G × Σ_d ( w_d × S_d )
```

| Symbol | Meaning |
|---|---|
| `S_d` | Similarity of dimension d between the user's conditions and the configuration, from 0 to 1 |
| `w_d` | Weight of dimension d for the question type (profile). The weights of the dimensions the user gave are rescaled to sum to 1 |
| `G` | Gate, 0.5 to 1: cuts the score when fuel or oxygen is far off, because other dimensions must not make up for it |
| `M` | Evidence factor: data availability and microgravity duration of the investigation. The formula allows 0.7 to 1, but because the verification term is fixed at 0.7 (1.5), the reachable range is 0.85 to 0.97. The catalog's investigations take 0.88, 0.95 or 0.97 |

**Name on the page: match score** (0–100; the human lead's naming, 2026-11-15). It says how closely an investigation's recorded conditions match the question, weighted by how much each condition matters for that kind of question. The output field of `rank()` stays `score`.

**Seven dimensions:** oxygen (`o2`), pressure, flow, fuel, sample shape (`geometry`), research purpose (`role`), diluent gas.
- A dimension counts only if the user's query gives it; the research purpose always counts.
- **A score orders the investigations for one question only.**
  - Scores of different questions are not comparable, because the weights are rescaled over the dimensions each question sets. "ISS" sets 4 dimensions and "lunar habitat cotton fabric" 6.
  - Compare questions by their test counts, not by their scores (review of 2026-11-15, B4; the human lead's decision).
- **No material named** (since 1.5.2, review B3).
  - Without a material the fuel is not compared, so the ranking rests on the atmosphere, the flow and the purpose; for "lunar habitat" the top 3 are fuel droplets (FLEX) and gas burners (ACME-CFI-G, ACME-BRE).
  - The result carries the `no_material` warning and asks for a material. The ranking itself is unchanged.
- The diluent counts only in suppression questions.

### 1.3 Weights by question type (profiles)

| Profile | o2 | pressure | flow | fuel | geometry | role | diluent | Why |
|---|---|---|---|---|---|---|---|---|
| prevention (default) | 0.251 | 0.083 | 0.250 | 0.250 | 0.083 | 0.083 | 0 | Oxygen, flow and the material can each decide whether a solid burns in microgravity (decisive in the literature); pressure, shape and purpose shift the outcome (strong modifiers) |
| detection | 0.060 | 0.060 | 0.151 | 0.335 | 0.060 | 0.334 | 0 | Only a study that measured smoke can answer, and detector response depends on the material (decisive); flow shapes the particles (modifier); no source documents an effect of O2, pressure or shape |
| suppression | 0.256 | 0.039 | 0.086 | 0.253 | 0.037 | 0.235 | 0.094 | Whether extinguishment was tested, the oxygen and the fuel each decide extinction (literature); the NASA FLEX measurements confirm oxygen and fuel and give pressure little weight |

**How the weights are derived (config 1.4.0, the human lead's decision at 20:19).**
- Judgement stream, the analytic hierarchy process (AHP) on literature-based judgements:
  - for each question type, each dimension has an evidence class from cited textbooks, papers and NASA records: 1 decisive, 2 strong modifier, 3 weak or not documented (`scoring/literature_evidence.json`);
  - the 51 pairwise judgements follow from the class difference on Saaty's scale (1, 3, 5);
  - consistency ratio 0, 0.009 and 0.008.
- Suppression is then pooled with the NASA FLEX measurements, as in 1.3.0.
- Details and the sources are in `scoring/BUILDUP.md` B3 and B4.

**Earlier judgement stream (config 1.2.0):** by the analytic hierarchy process (AHP). For each profile every pair of dimensions is compared on Saaty's 1–9 scale (51 judgements, each with its basis in a NASA record sentence, the textbook or the team's reasoning, in `scoring/ahp_judgements.json`). `scoring/derive_weights.py` takes the principal eigenvector of each matrix as the weights and checks consistency: CR 0.012, 0.014 and 0.006, below the 0.10 limit. The judgements were written by an AI session; the human lead approved them as they are and decided to apply them (19:26). Configs 1.0.0 and 1.1.0 used directly allocated weights (0.25, 0.10, 0.20, 0.25, 0.10, 0.10 for prevention); the comparison is in `scoring/WEIGHTING.md` 3.4.

**Config 1.3.0 (20:06, the human lead's decision):** the suppression weights of o2, pressure, diluent and fuel are pooled (log-linear opinion pool) with the share of variance each explains in the NASA FLEX extinction measurements (274 ISS droplet tests, LMG decomposition with bootstrap intervals; `scoring/data_weights.json`). Prevention and detection keep the AHP weights: no NASA table records a response for them. Details in `scoring/BUILDUP.md` B2 and B4.

The question type comes from words in the query: "smoke" and "detector" give detection; "extinguish" and "suppression" give suppression. Otherwise the type is prevention.

### 1.4 Similarity of each dimension

| Dimension | Rule | Values |
|---|---|---|
| Oxygen | Inside the tested range: 1.<br>Outside: decays with the log of the ratio of O2 fractions, faster above the tested maximum (a fire may be worse than tested) than below the minimum | Scale above ln(26/21), below ln(21/11): near air these equal 5 and 10 percentage points |
| Pressure | Inside the range: 1.<br>Outside: Gaussian in the log of the pressure ratio | σ = ln 2 (a factor of 2 gives 0.61) |
| Flow | Flow type matrix: quiescent, opposed, concurrent, coflow, counterflow or radial.<br>Speed: Gaussian in log speed.<br>A one-sided range ("up to 40 cm/s") scores unknown on its open side | ventilated against opposed or concurrent: 0.9; ventilated against quiescent: 0.4; speed σ = ln 2, offset 1 cm/s |
| Fuel | A hierarchy | same material 1.0; same class and melt behaviour 0.8; same class 0.7; same phase 0.5; gas burner emulating a solid 0.5; liquid against gas 0.3; other 0.1 |
| Sample shape | Shape and thermal thickness (thin or thick) | same shape 1.0; other shape, same thickness 0.7; same shape, other thickness 0.6; other solid 0.4; solid against non-solid 0.2 |
| Research purpose | The investigation's fire-safety axis (team classification of the PSI record).<br>Detection questions (since 1.5.0) are matched per fire signature, gas or particulate: purpose (detection label, or a NASA-stated purpose of measuring that signature) × outcome (that signature was measured). See 1.7 | same axis 1.0 (purpose and outcome); related focus 0.7 (one of the two); fundamental 0.4; other 0.2 |
| Diluent (suppression only) | Same gas: 1.<br>Another inert: the ratio of molar heat capacities at 298 K, squared | CO2 37.198, N2 29.071, He 20.786 kJ/kmol·K: CO2–N2 0.61, N2–He 0.51, CO2–He 0.31 |
| Not recorded | The catalog has no value | 0.5. For O2 and fuel it is capped at the best recorded match of the query ("unknown never beats measured") |

### 1.5 Gate, evidence factor and selection

- **Gate (non-compensatory):** if the fuel or the O2 similarity is below 0.2, the score is multiplied by 0.5 to 1.0. The factor rises linearly from 0.5 at a similarity of 0 to 1.0 at a similarity of 0.2.
  - Evidence class 1 ("decisive", WEIGHTING.md) means a large weight. It is not a veto. A weighted sum lets the other conditions make up for part of a mismatch; the gate stops that only when fuel or oxygen is far off.
  - The review of 2026-11-15 (B1) proposed an oxygen gate at 0.37 and a flow gate (0.5). The human lead kept the current gate. With the stricter oxygen gate, "lunar habitat cotton fabric" ranks a gas burner first (ACME-BRE 62.6), because no solid test reached 30% O2. That absence is shown by the test counts, not by the ranking (`gate.decisive_is_not_a_veto`).
- **Evidence factor:** `M = 0.7 + 0.3 × mean(data availability, microgravity duration, verification)`.
  - Data availability: raw table 1.0, summary table 0.8, derived analysis 0.6, images 0.5, papers only 0.3.
  - A table whose rows are not individual tests is a summary table. This covers the FLEX-2 planned matrix and, since the review of 2026-11-15 (A1), the day tables: the four ACME tables (PSI-20 to 23, "Flames Ignited" per day) and SLICE (PSI-106, fuel per test date). They were `raw_table` before, so their M is now 0.95 instead of 0.97.
  - Microgravity duration: long 1.0, short 0.6, ground 0.5.
  - Verification: 0.7 whether or not a person has checked the row, so checking rows never reorders the ranking.
- **Selection:**
  - One configuration per investigation.
  - The top 3 are the result.
  - Near-ties (`selection.tie_points`, 3 points), rule of 2026-11-15 (review A2). Each place is filled in the same way. The results within 3 points of the best remaining score form a group, and they are ordered by:
    1. the larger recorded share (`coverage`: the share of the weight compared with a value that a NASA source states);
    2. the stronger evidence factor;
    3. the higher score.

    The rule does not depend on the order the results arrive in. Before, neighbours were swapped once, by evidence and then by `has_1g_comparison`. That field is empty when the record does not mention a 1 g comparison, so the old rule penalised silence and was not in this document.
  - If the user's O2 is not air (outside 21 ± 2%) and none of the top 3 was tested at that O2, the third place goes to the best result that was.
- **Unreported atmosphere:**
  - When a record gives no O2, it is scored as 21%.
  - Pressure is filled as 101.3 kPa only for experiments that ran in the ISS cabin, the MSG or a Cygnus cabin.
  - Such a result carries the `fallback` warning. Its confidence leaves the assumed values out, and its reasons say "not recorded, assumed".
  - Exception (1.5.0): for BASS-II a published paper states the pressure ("Pressure was not varied from 1 atmosphere", ICES 2019, Section II). It is filled as 101.3 kPa with the basis `published`. It is not an assumption, and no `fallback` warning is raised (`atmosphere_fallback.pressure_published`).
- **Confidence:** the share of the profile's weight compared with a value that a NASA source states (a table, the record text, a test matrix or a published paper). High is 0.75 or more, medium 0.45 or more, low below. Assumed values and team readings are scored but not counted (1.5.0; team readings were counted before).
- **Compliance lines** (requirements layer; no score effect): each line gives a status and the `basis` of the value it checked.
  - `met`: a per-test table value, or a catalog classification, covers the requirement.
  - `documented`: a NASA document covers it (record text, test matrix or published paper), but no per-test table value shows it.
  - `near`, `not_met`.
  - `unverified`: no value, an assumed atmosphere, or a team reading.
  - `not_scored`.

### 1.6 Reading the query

- **Layers:** a query is read in layers, each later one overriding the earlier: default < preset (ISS, lunar habitat, Mars habitat, spacesuit, Earth) < words and numbers in the text < explicit fields.
- **Words:** they are matched against keyword lists in English and Korean. The Korean words are glossed in `keywords._gloss_ko`.
- **Numbers:**
  - "30% O2" and "O2 30%" are read, but not "CO2 30%".
  - Pressure is read in kPa, psi, psia, atm, bar or mmHg; flow speed in cm/s, mm/s or m/s.
- **Words not read:** they are listed in `not_understood`, and the page says they change nothing.
- **Fire signature (detection questions only, 1.5.0):** `keywords.signature`.
  - Gas words: CO, CO2, HCN, HCl, combustion gases or products, toxic gas, gas sensor.
  - Particulate words: smoke, aerosol, particle, soot.
  - Both kinds give `gas_and_particulate`, which accepts either signature.
  - In a detection question "CO2" names the signature and is not read as a diluent.
  - "co-flow" is not read as CO.

### 1.7 Combined model 1.5.0: the catalog and the data role's raw-file method

The data role's raw-file layer ranks and counts NASA tests from table values only. The catalog ranks experiments with the best documented value. They differed in three places. Each was judged on theory, and the combined rule keeps what holds on each side. No weight changed.

1. **Detection purpose: one label against an outcome-specific link.**
   - NASA defines fire signatures as "the gaseous species and particulate properties produced by a fire" (Ruff, NASA/TM-2011-217036, 1.2.2). Detection evidence therefore has two outcomes.
   - Under the GRADE indirectness domain (Guyatt et al. 2011), evidence is direct when it measures the outcome asked about.
   - The catalog's one-word label is a good test of purpose, but it ignored the outcome. BASS-II (measured CO and CO2, with a stated purpose of evaluating combustion products) scored 0.2 for a CO question. SAME (smoke particles only) scored 1.0. In 1.4.0 particulate evidence (soot focus) already earned 0.7 for detection and gas evidence earned nothing. That asymmetry contradicts the NASA definition.
   - The data role's per-need link (`objective_link = stated`) is outcome-specific, so it is more valid for a named signature.
   - Combined rule: purpose × outcome, as in the table above. Purpose is a union (OR) of the label and a NASA-stated purpose, because a missing label is not evidence against a stated purpose. Its evidence is in `similarity.role.signatures`.
2. **Compliance "met": ranking against counting.**
   - The two methods answer different questions.
   - For ranking, the catalog is more valid. Constant conditions are often not tabulated *because* they were constant. That missingness depends on the value itself (not missing at random, Rubin 1976). A complete-case rule would drop exactly the constant-pressure ISS experiments.
   - For the word "met", the data role is more valid. NASA/SP-2016-6105 Rev2 (5.3) names the verification method of each requirement. A test value per test is not the same evidence as a document read by inspection.
   - Combined rule: scores keep the documented values. The compliance line says `documented` instead of `met` when the value is not a per-test table value, and it names the basis. A team reading is not a NASA statement, so it is `unverified` and leaves the confidence.
   - The review of 2026-11-15 (B2) proposed capping the similarity of non-table values at 0.8. The human lead kept this rule. The value 0.8 has no source, and a cap would lower exactly the constant-condition experiments described above. On "ISS" it would also move BASS-II, whose pressure a paper states, from first to third.
3. **BASS-II pressure: assumption against "cannot be placed".**
   - A published paper states the value, so the catalog's "assumed" was too weak.
   - The data role's "cannot be placed from the table" stays right for table placement.
   - Combined rule: basis `published`; the score is unchanged.

Effects on the demo queries:
- Gas-signature detection questions now rank BASS-II first, with SAME second or third (validation D03, F06, F08). Smoke questions are unchanged.
- FLEX and CFI drop from medium to low confidence on quiescent questions (their flow is a team reading).
- ACME-BRE pressure and BASS flow read `documented`.
- The full list is in `validation/report.md`.

---

### 1.8 Limits of the similarity rules

- **Detection covers the smoke of overheated materials** (`profiles.detection.scope`, review B5).
  - SAME and SAME-R heated samples without a flame (pyrolysis), so oxygen and pressure stay in evidence class 3 for detection.
  - The review noted that soot production in flames rises with pressure. That concerns flaming combustion. Pressure would move to class 2 only with a checked source on the smoke or detector response of overheated materials. A simulated class 2 moves no detection rank 1 and changes one rank 3 ("smoke detector for a lunar rover").

These are known limits, not yet changed (review of 2026-11-15, part C):
- **Thermal thickness labels on ranges.**
  - SAFFIRE-II-C03 (PMMA, 0.85 to 10 mm) is labelled thick, and SAFFIRE-II-C01 (silicone, 0.27 to 1.03 mm) thin. Each range crosses the thin–thick boundary.
  - BASS-II-C06 holds a PMMA spherical section and a wax candle in one configuration, so a PMMA query finds it as "same material".
  - Of the SIBAL configurations, only SAFFIRE-II-C02 records a thickness (0.37 mm).
  - Next: a `mixed` label or split configurations.
- **Inside a range scores 1.** A query value inside a tested range scores 1.0 even if the tests sit only at the two ends. The `ranges_separate` warning covers only O2 and pressure ranges compared together.
- **The diluent rule is a first-order approximation.**
  - It compares molar heat capacities at 298 K, squared.
  - At flame temperatures the heat capacity of CO2 is much larger than at 298 K, and helium's high thermal diffusivity is not captured (MODEL_BASIS.md B).
  - The direction agrees with the FLEX regression (`scoring/data_weights.json`): helium raises the burning-rate constant, CO2 lowers it.
- **Scale numbers are not comparable between dimensions.** The shapes were chosen per dimension (MODEL_BASIS.md, rows on oxygen and pressure).
  - Oxygen is asymmetric: a fire above the tested O2 may be worse. So it decays exponentially in the log ratio, with its own scale on each side.
  - Pressure and flow speed act through power laws with no safe side. So they use a symmetric Gaussian in the log ratio.
  - "σ = ln 2" and "scale ln(26/21)" are therefore not on one scale.

## 2. How it was validated

Every check below can be rerun with the command given. Numbers are from 2026-11-15, config 1.5.2.

| Check | What it shows | Result | Command |
|---|---|---|---|
| Unit tests | Each similarity formula, hand-calculated examples, the reading of queries, the wording of reasons and warnings, and that the config holds exactly the AHP weights | 79 of 79 pass | `python3 -m unittest scoring.test_scorer` |
| AHP consistency | Whether the 51 pairwise judgements fit together | Literature judgements (used): CR 0, 0.009, 0.008. AI judgements of 1.2.0: 0.012, 0.014, 0.006. Limit 0.10 | `python3 scoring/derive_literature_weights.py`, `python3 scoring/derive_weights.py --check` |
| Validation scenarios | 45 typed questions with an expected answer: rough inputs, prevention, detection, suppression, liquids, fuel phase, equipment, sentences, traps such as "spacesuit" or "rocket" | 45 of 45 pass | `python3 validation/run_validation.py` |
| Weight stability | Each weight moved by ±0.05 in five key scenarios | Rank 1 unchanged in 5 of 5 | in `validation/report.md` |
| Weight sensitivity | Each weight of each profile halved and raised by half (rescaled to 1), on four queries per profile | 146 of 152 variants keep the same top 3 in order; rank 1 changes in 3, all in prevention: `lunar habitat` with the O2 weight halved, `lunar habitat cotton fabric` with the O2 weight raised by half or the fuel weight halved (1 before the tie rule of 1.5.1) | `python3 validation/sensitivity.py` |
| Weighting by purpose | Equal weights, rank-order centroid weights, and the other profiles' weights on each profile's queries | Rank-order centroid keeps the same top 3 in 11 of 12. Prevention weights change the top 3 in 5 of 8 detection and suppression queries: the purpose changes the answer | `python3 validation/sensitivity.py` |
| NASA data stream (FLEX) | Share of the explained variance of the measured burning-rate constant and extinction diameter that each condition accounts for; coefficients checked against the d² law | O2 36%, fuel 35%, size 14%, diluent 13%, pressure 2% of extinction; four of four theory checks hold | `python3 scoring/derive_data_weights.py` |
| Weight uncertainty (SMAA) | 300 random weight vectors per profile that keep only the order of importance | Rank 1 holds in every draw for 7 of 12 queries and in 80% or more for 11 of 12; `lunar habitat cotton fabric` has no clear winner (its rank 1, SAFFIRE-II, holds in 25% of the draws) | `python3 validation/sensitivity.py` |
| Sensitivity to the other values | Each similarity scale, the gate, the evidence factor, the tie margin and each similarity table halved and raised by half, on the four demo queries | 124 of 136 runs keep the same top 3 in order; rank 1 changes in 5. `ISS` never changes. The changes are in `lunar habitat` (tie margin, flow-configuration matrix, data-availability table), `ISS cotton fabric` (O2 decay below the tested minimum, tie margin) and `lunar habitat cotton fabric` (O2 decay above the tested maximum, gate, fuel table, tie margin). Under 1.4.0 it was 129 of 136, with `ISS` and `lunar habitat` never changing; the tie rule of 1.5.1 orders near-ties by recorded share, so a small change of a score can now change their order | `python3 validation/sensitivity.py` |
| Python against JavaScript | The page gives exactly what the reference code gives | 106 of 106 queries identical; the deploy stops on any difference | `python3 web/parity_check.py` |
| Catalog against the NASA sources | An independent second reading of the PSI records and tables, without the build script or the data pipeline | 107 ranking values written in their source, plus 8 team readings; 24 of 24 range ends match the source column; 14 test counts match, and 1 differs with its reason in `source_notes`; 135 of 135 numbers in the shown text are in the source | `python3 validation/check_catalog_sources.py` |
| Rules against a combustion textbook | Direction and form of each rule (Turns 2012, chapter and section) | Consistent; flame spread over solids is not covered by the book | `scoring/MODEL_BASIS.md` |
| Review of every value | Role, basis and sensitivity of each value; approval by the human lead | Direct weights approved 16:51, all other values 17:03; AHP judgements approved and applied 19:26; FLEX pooling 20:06; literature stream 20:19 | `scoring/PARAMETER_REVIEW.md`, `scoring/WEIGHTING.md` |
| Human check sheet | The catalog values behind the demo, with the NASA rows to compare | 104 checks for 13 configurations, ready for a person | `validation/verification_sheet.csv` |

**What these checks do not show:**
- There is no measured "right answer" for a ranking. The expected answers of the scenarios were written for the team by an AI session from combustion reasoning and the challenge text.
- The checks show that the code follows the rules, that the rules behave stably, and that the catalog copies NASA correctly. They do not show that the rules are the best possible ones.
- Next step: review of the rules and the expected answers by combustion researchers (the questions are at the end of `scoring/PARAMETER_REVIEW.md`).

---

## 3. Data preprocessing for the catalog

The catalog is built by `scripts/build_catalog.py` from the PSI records (`data/psi/catalog/PSI-*.json`) and the 22 experimental tables (`data/psi/experimental_tables/*.csv`). It is not hand-edited: to change a value, change the script and rebuild.

### 3.1 From PSI tables to one row per configuration

1. **Reading the tables.**
   - Encoding: UTF-8 is tried first, then Windows-1252, then Latin-1.
   - Blank rows are dropped.
   - Numbers are parsed with thousands separators removed.
2. **Grouping into configurations.** Tests that share a fuel, a sample family and a flow configuration form one configuration:
   - FLEX by fuel (methanol, heptane);
   - BASS-II by sample family (film, slab, rod, SIBAL fabric, Nomex, other), a keyword rule on the sample-material cell;
   - Saffire by sample and flow direction;
   - ACME by burner (normal or inverse flame).
3. **Ranges.** For each configuration, the lowest and highest value of each condition becomes the range, for example `o2_min_pct` and `o2_max_pct`, rounded (usually to one decimal).
4. **Unit conversion**, by fixed factors:
   - mole fraction × 100 gives %;
   - atm × 101.325, bar × 100 and mmHg × 0.133322 give kPa.
   - Partial pressure of O2 is computed as O2 fraction × total pressure for ambient oxygen only.
5. **Repeated rows.**
   - A row that repeats an earlier row cell for cell is the same test entered twice, and is dropped: 8 rows in CFI, 34 in SPICE.
   - SAME rows 6 to 9 say "same conditions as 1-4" and record no values, so they are not counted as tests.
6. **Cells that are not readings.** These are left out, and each case is noted in `source_notes`:
   - negative air speeds in SPICE;
   - a pressure cell of 0 in FLEX (row 115);
   - "3400%" and "2100%" in the ACME BRE oxygen column;
   - in the BASS-II "Air display" column, numbers in brackets or after "pot" (fan or potentiometer readings) and numbers above the 40 cm/s that the record gives as the tunnel's limit.
7. **Counts.**
   - Test counts are distinct table rows.
   - The ACME day tables count flames ignited (the sum of "Flames Ignited"), labelled as flames, not tests.

### 3.2 Rules that keep every number traceable

- **Only sourced numbers.**
  - A number comes only from a PSI table or the PSI record text.
  - An empty value stays empty and is never filled with 0. The scorer's fallback for an unreported atmosphere is applied at scoring time, flagged, and never written into the catalog.
- **Where each value comes from.**
  - `atmosphere_basis` says where the numbers come from.
  - `o2_source`, `pressure_source` and `flow_source` mark each range as `table`, `record` (named in the record text, not a test value), `test_matrix` (planned conditions) or `team` (a team reading, such as 0 cm/s for quiescent droplets). The reasons on the page say "tested" only for `table` values.
- **Oxidizer streams.** `o2_reference = oxidizer_stream` marks inverse flames, whose O2 is the burner's oxidizer stream, not an atmosphere. It is never compared with the user's O2.
- **Team classification, not NASA's:** `tier`, `fire_safety_role`, `research_focus`, `fire_scenario_tags`, `fuel_class`, `thermal_regime` and `sooting_tendency`.
- **Verification state.** Every row is `ai_extracted` until a person checks it against the source (`validation/verification_sheet.csv`).

### 3.3 The processed test data shown with each result

The page shows the processed test-by-test data of each ranked investigation from the data pipeline (`data/pipeline/tests.csv` and the evidence packages). That processing belongs to the data role, and its rules are in `pipeline/README.md`: standard variables, unit factors declared in the spec, cells a rule cannot read left empty and flagged, and every value kept with its source file, row and column. The ranking does not read the pipeline's files.
