# How the ranking works: weighting rules, validation, data preprocessing

*AI-generated (Claude Code, catalog role), 2026-11-14, config 1.1.0. Written for the team.*

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
| `M` | Evidence factor, 0.7 to 1: data availability and microgravity duration of the investigation |

**Seven dimensions:** oxygen (`o2`), pressure, flow, fuel, sample shape (`geometry`), research purpose (`role`), diluent gas.
- A dimension counts only if the user's query gives it; the research purpose always counts.
- The diluent counts only in suppression questions.

### 1.3 Weights by question type (profiles)

| Profile | o2 | pressure | flow | fuel | geometry | role | diluent | Why |
|---|---|---|---|---|---|---|---|---|
| prevention (default) | 0.25 | 0.10 | 0.20 | 0.25 | 0.10 | 0.10 | 0 | Microgravity flammability of solids is mapped on oxygen against flow speed, so O2 and flow carry 0.45. Fuel comes next. Pressure and shape refine the match |
| detection | 0.10 | 0.05 | 0.10 | 0.30 | 0.05 | 0.40 | 0 | Smoke depends mostly on the material and on whether the study measured smoke |
| suppression | 0.15 | 0.05 | 0.10 | 0.20 | 0.05 | 0.30 | 0.15 | Whether extinguishment was tested, and with which diluent, matters most; the O2 after dilution still governs extinction |

The question type comes from words in the query: "smoke" and "detector" give detection; "extinguish" and "suppression" give suppression. Otherwise the type is prevention.

### 1.4 Similarity of each dimension

| Dimension | Rule | Values |
|---|---|---|
| Oxygen | Inside the tested range: 1.<br>Outside: decays with the log of the ratio of O2 fractions, faster above the tested maximum (a fire may be worse than tested) than below the minimum | Scale above ln(26/21), below ln(21/11): near air these equal 5 and 10 percentage points |
| Pressure | Inside the range: 1.<br>Outside: Gaussian in the log of the pressure ratio | σ = ln 2 (a factor of 2 gives 0.61) |
| Flow | Flow type matrix: quiescent, opposed, concurrent, coflow, counterflow or radial.<br>Speed: Gaussian in log speed.<br>A one-sided range ("up to 40 cm/s") scores unknown on its open side | ventilated against opposed or concurrent: 0.9; ventilated against quiescent: 0.4; speed σ = ln 2, offset 1 cm/s |
| Fuel | A hierarchy | same material 1.0; same class and melt behaviour 0.8; same class 0.7; same phase 0.5; gas burner emulating a solid 0.5; liquid against gas 0.3; other 0.1 |
| Sample shape | Shape and thermal thickness (thin or thick) | same shape 1.0; other shape, same thickness 0.7; same shape, other thickness 0.6; other solid 0.4; solid against non-solid 0.2 |
| Research purpose | The investigation's fire-safety axis (team classification of the PSI record) | same axis 1.0; related focus 0.7; fundamental 0.4; other 0.2 |
| Diluent (suppression only) | Same gas: 1.<br>Another inert: the ratio of molar heat capacities at 298 K, squared | CO2 37.198, N2 29.071, He 20.786 kJ/kmol·K: CO2–N2 0.61, N2–He 0.51, CO2–He 0.31 |
| Not recorded | The catalog has no value | 0.5. For O2 and fuel it is capped at the best recorded match of the query ("unknown never beats measured") |

### 1.5 Gate, evidence factor and selection

- **Gate (non-compensatory):** if the fuel or the O2 similarity is below 0.2, the score is multiplied by 0.5 to 1.0. The factor rises linearly from 0.5 at a similarity of 0 to 1.0 at a similarity of 0.2.
- **Evidence factor:** `M = 0.7 + 0.3 × mean(data availability, microgravity duration, verification)`.
  - Data availability: raw table 1.0, summary table 0.8, derived analysis 0.6, images 0.5, papers only 0.3.
  - Microgravity duration: long 1.0, short 0.6, ground 0.5.
  - Verification: 0.7 whether or not a person has checked the row, so checking rows never reorders the ranking.
- **Selection:**
  - One configuration per investigation.
  - The top 3 are the result; scores within 3 points count as a tie and are ordered by evidence.
  - If the user's O2 is not air (outside 21 ± 2%) and none of the top 3 was tested at that O2, the third place goes to the best result that was.
- **Unreported atmosphere:**
  - When a record gives no O2, it is scored as 21%.
  - Pressure is filled as 101.3 kPa only for experiments that ran in the ISS cabin, the MSG or a Cygnus cabin.
  - Such a result carries the `fallback` warning. Its confidence leaves the assumed values out, and its reasons say "not recorded, assumed".
- **Confidence:** the share of the profile's weight that was compared with a recorded value: high 0.75 or more, medium 0.45 or more, low below.

### 1.6 Reading the query

- **Layers:** a query is read in layers, each later one overriding the earlier: default < preset (ISS, lunar habitat, Mars habitat, spacesuit, Earth) < words and numbers in the text < explicit fields.
- **Words:** they are matched against keyword lists in English and Korean. The Korean words are glossed in `keywords._gloss_ko`.
- **Numbers:**
  - "30% O2" and "O2 30%" are read, but not "CO2 30%".
  - Pressure is read in kPa, psi, psia, atm, bar or mmHg; flow speed in cm/s, mm/s or m/s.
- **Words not read:** they are listed in `not_understood`, and the page says they change nothing.

---

## 2. How it was validated

Every check below can be rerun with the command given. Numbers are from 2026-11-14, config 1.1.0.

| Check | What it shows | Result | Command |
|---|---|---|---|
| Unit tests | Each similarity formula, hand-calculated examples, the reading of queries, the wording of reasons and warnings | 39 of 39 pass | `python3 -m unittest scoring.test_scorer` |
| Validation scenarios | 38 typed questions with an expected answer: rough inputs, prevention, detection, suppression, liquids, fuel phase, equipment, sentences, traps such as "spacesuit" or "rocket" | 38 of 38 pass | `python3 validation/run_validation.py` |
| Weight stability | Each weight moved by ±0.05 in five key scenarios | Rank 1 unchanged in 5 of 5 | in `validation/report.md` |
| Weight sensitivity | Each prevention weight halved and raised by half (rescaled to 1) on four demo queries | 45 of 48 variants keep the same top 3 in order; rank 1 never changes | `python3 validation/sensitivity.py` |
| Sensitivity to the other values | Each similarity scale, the gate, the evidence factor, the tie margin and each similarity table halved and raised by half | 129 of 136 runs keep the same top 3. The `ISS` and `lunar habitat` presets never change. The changes are in the two cotton-fabric queries, through the O2 decay above a test's maximum and the fuel table | `python3 validation/sensitivity.py` |
| Python against JavaScript | The page gives exactly what the reference code gives | 99 of 99 queries identical; the deploy stops on any difference | `python3 web/parity_check.py` |
| Catalog against the NASA sources | An independent second reading of the PSI records and tables, without the build script or the data pipeline | 107 ranking values written in their source, plus 8 team readings; 24 of 24 range ends match the source column; 14 test counts match, and 1 differs with its reason in `source_notes`; 135 of 135 numbers in the shown text are in the source | `python3 validation/check_catalog_sources.py` |
| Rules against a combustion textbook | Direction and form of each rule (Turns 2012, chapter and section) | Consistent; flame spread over solids is not covered by the book | `scoring/MODEL_BASIS.md` |
| Review of every value | Role, basis and sensitivity of each value; approval by the human lead | Weights approved 16:51, all other values 17:03 | `scoring/PARAMETER_REVIEW.md` |
| Human check sheet | The catalog values behind the demo, with the NASA rows to compare | 96 checks for 12 configurations, ready for a person | `validation/verification_sheet.csv` |

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
