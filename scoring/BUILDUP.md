# Weighting model build-up: what was added, which concepts and techniques, and where they come from

*AI-generated (Claude Code, catalog role), 2026-11-14. Written for the team after the human lead's direction at 19:40 KST:*
- *depend less on AI judgement;*
- *read the user's question as requirements, in a systems-engineering way;*
- *set the weights from data science and combustion engineering;*
- *cite papers and textbooks that a reader can open.*

Scores and rankings are the team's computation, not NASA's conclusion, and not safety guidance. Each reference is listed in section 7 with a link; "open" marks a free full text.

---

## 0. The model after the build-up

```
user's question
  │  B1 requirements (systems engineering): one requirement per condition, with its source and how the catalog verifies it
  ▼
weights per question type (prevention, detection, suppression), from three streams:
  ├─ B2 NASA data stream: how much each condition explains of a measured combustion response (FLEX, PSI-69)
  ├─ B3 judgement stream: AHP pairwise judgements from evidence classes in cited textbooks, papers and NASA records
  │                       (config 1.4.0); a filled form by team members would take precedence
  └─ combustion theory: checks the sign and size of every data result (d² law), and backs each judgement
  │  B4 pooling: log-linear (geometric) pool of the streams over the dimensions each covers
  ▼
weighted similarity score (Gower-type [M5], rescaled over the conditions given; case retrieval [M6]) × gate × evidence factor
  ▼
top 1 to 3 investigations + a compliance line per requirement (B1)
  │  B5 robustness: one-at-a-time, rank-order centroid, SMAA over the order of importance
```

**Where an AI judgement still enters, and what replaces it:**

| Part | Before the build-up | Now | Still open |
|---|---|---|---|
| Reading the question | Keyword rules (no model at run time) | The same rules, now shown as explicit requirements with their source | — |
| Weights, suppression | AI session's AHP judgements | Literature-based judgements (B3a), pooled with NASA FLEX measurements (B2, B4); config 1.4.0 | Team members' judgements (B3b) |
| Weights, prevention and detection | AI session's AHP judgements | Literature-based judgements (B3a); no NASA table records a response (spread rate, smoke size) to learn from; config 1.4.0 | Team members' judgements (B3b). The evidence classes were assigned by an AI session from the cited findings |
| Similarity rules | AI proposal, checked against a textbook (`MODEL_BASIS.md`) | Unchanged. Checked against an atmosphere flame temperature on NASA data (B6): it supports separate O2 and diluent dimensions and shows that heat capacity alone is incomplete for helium | A data-based diluent similarity. Rerun B6 with NASA Glenn coefficients (licence) |

### Before and after, in numbers

Three configurations, run through the same code and the same checks; only the weights differ (2026-11-14 21:36):
- **1.1.0:** direct point allocation by an AI session, until 19:26;
- **1.2.0:** AHP over the AI session's judgements, just before the build-up;
- **1.4.0:** now.

**Weights**

| Question type | Dimension | 1.1.0 | 1.2.0 | 1.4.0 |
|---|---|---|---|---|
| prevention | o2 / flow / fuel | 0.25 / 0.20 / 0.25 | 0.285 / 0.166 / 0.267 | 0.251 / 0.250 / 0.250 |
| | pressure / geometry / role | 0.10 / 0.10 / 0.10 | 0.090 / 0.111 / 0.081 | 0.083 / 0.083 / 0.083 |
| detection | role / fuel / flow | 0.40 / 0.30 / 0.10 | 0.458 / 0.221 / 0.136 | 0.334 / 0.335 / 0.151 |
| | o2 / pressure / geometry | 0.10 / 0.05 / 0.05 | 0.085 / 0.049 / 0.051 | 0.060 / 0.060 / 0.060 |
| suppression | role / o2 / fuel | 0.30 / 0.15 / 0.20 | 0.286 / 0.162 / 0.162 | 0.235 / 0.256 / 0.253 |
| | diluent / flow / pressure / geometry | 0.15 / 0.10 / 0.05 / 0.05 | 0.162 / 0.089 / 0.080 / 0.059 | 0.094 / 0.086 / 0.039 / 0.037 |

**What each weight rests on**

| | 1.1.0 | 1.2.0 | 1.4.0 |
|---|---|---|---|
| Unit of judgement | 19 weights set directly, one rationale sentence per question type | 51 pairwise judgements by an AI session | 19 evidence classes; the 51 judgements follow by rule |
| Cited basis | none per weight | 35 of 51 judgements cite a NASA record or the textbook; 16 rest on the team's reasoning | 15 of 19 classes cite a paper, textbook or report; 2 cite a NASA record only; 2 have no source, which is why they are class 3. 12 of 19 include a finding checked only in an abstract |
| NASA measurements in the weights | none | none | the 0.642 of suppression weight on o2, pressure, diluent and fuel is pooled with 274 FLEX tests |
| Consistency check | none | CR 0.012, 0.014, 0.006 | CR 0, 0.009, 0.008 |

**Results and checks**

| Check | 1.1.0 | 1.2.0 | 1.4.0 |
|---|---|---|---|
| Validation scenarios passed | 38 of 38 | 38 of 38 | 38 of 38 |
| Scenarios whose top 3 differ from 1.2.0 | 3 | — | 2 |
| One weight ×0.5 or ×1.5: same top 3 | 146 of 152 | 146 of 152 | 146 of 152 |
| One weight ×0.5 or ×1.5: rank 1 changes | 0 | 1 | 1 (`lunar habitat`, O2 halved) |
| Order of importance only (rank-order centroid): same top 3 | 11 of 12 | 11 of 12 | 11 of 12 |
| Purpose changes the answer (prevention weights on detection or suppression queries) | 5 of 8 | 5 of 8 | 5 of 8 |
| SMAA: rank 1 in every draw | 8 of 12 | 9 of 12 | 8 of 12 |
| SMAA: rank 1 in 80% of draws or more | 11 of 12 | 11 of 12 | 11 of 12 |
| SMAA: `lunar habitat cotton fabric` keeps its rank 1 | 61% | 46% | 33% |
| Unit tests | 39 | 45 | 56 |

**Scores of the demo and test queries** (top 3 unchanged unless noted)

| Query | 1.1.0 | 1.2.0 | 1.4.0 |
|---|---|---|---|
| `ISS` | 94.0 / 94.0 / 92.7 | 94.4 / 94.4 / 92.8 | 93.4 / 93.4 / 92.1 |
| `lunar habitat` | 79.1 / 79.1 / 76.1 | 81.5 / 81.5 / 78.9 | 75.2 / 75.2 / 71.6 |
| `ISS cotton fabric` | 95.1 / 95.1 / 94.0 | 95.4 / 95.4 / 94.2 | 94.6 / 94.6 / 93.5 |
| `lunar habitat cotton fabric` | 75.3 / 74.9 / 65.5 | 73.2 / 72.7 / 65.8 | 75.0 / 74.5 / 63.9 |
| `smoke detector on ISS` | 95.5 / 95.5 / 89.5 | 95.2 / 95.2 / 87.9 | 94.6 / 94.6 / 84.9 |
| `CO2 suppression of heptane fire` | 97.0 / 74.9 / 68.1 | 97.0 / 73.9 / 68.4 | 97.0 / 78.6 / 68.3 |
| `stagnant PMMA` | BASS-II 79.4, ACME-BRE 75.0, BASS 70.5 | BASS-II 81.3, BASS 73.5, ACME-BRE 71.8 | ACME-BRE 76.2, BASS-II 76.2, BASS-FGM-MODEL 69.1 |

**Reading:**
- The build-up changed what the weights rest on much more than the rankings it produces.
- Robustness is about the same as before. One preset became more sensitive: `lunar habitat` changes rank 1 when the O2 weight is halved. The close call `lunar habitat cotton fabric` became closer.

---

## B1. Requirements identification (systems engineering)

**What it does.** `rank()` now returns `requirements`: one record per condition the scorer reads from the question. Each record holds:
- the dimension it constrains, its kind (environment, scenario, material or purpose) and its value;
- its source: **stated** (typed by the user), **implied** (by a preset such as the ISS cabin), **derived** (for example a flow state from a speed) or **assumed** (a default);
- the catalog columns that verify it (`verified_by`).

Each result carries a `compliance` line per requirement:
- **met:** the configuration's recorded conditions cover it;
- **near:** similarity of 0.9 or more;
- **not_met**;
- **unverified:** no recorded value, or an assumed atmosphere;
- **not_scored.**

Example, `ISS cotton fabric`:

| Requirement | Source | BASS | SAFFIRE-III | BASS-II |
|---|---|---|---|---|
| R1 gravity: microgravity | implied by ISS preset | met | met | met |
| R2 O2: 21% | implied by ISS preset | unverified | unverified | near |
| R3 pressure: 101.3 kPa | implied by ISS preset | unverified | unverified | unverified |
| R4 flow: ventilated | implied by ISS preset | near | near | near |
| R5 fuel: cotton | stated | met | met | met |
| R6 shape: thin flat sheet | stated | met | met | met |
| R7 purpose: prevention | assumed | met | met | met |

**Concepts and techniques:**
- **Stakeholder expectations to technical requirements.** A requirement must be verifiable and traceable [SE1]. Each requirement here names its source (backward trace to the question) and its verifying catalog columns (forward trace to the evidence).
- **Verification matrix** [SE1]: the compliance line is a small verification matrix. It records the evidence of each result for each requirement, so "why this experiment?" has an answer per requirement.
- **Requirement form:** each record keeps one condition and one value, in a fixed template and order, in the way structured requirement syntaxes such as EARS do [SE4].
- The layer changes no score; a unit test checks this.

**Code:** `requirements()` and `compliance()` in `scoring/scorer.py` and `web/scorer.js`; labels in `scoring_config.json` `requirements`.

---

## B2. NASA data stream: relative importance of conditions in measured combustion responses

**What it does.** `scoring/derive_data_weights.py` reads the FLEX experimental table (PSI-69, CC0-1.0) directly: 274 droplet tests on the ISS, methanol or heptane, in O2/N2/CO2/He atmospheres at 0.5 to 3 atm. For two measured responses it asks how much of their variation each condition explains.

| Response (n tests) | R² | O2 | diluent (CO2, He) | fuel | droplet size | pressure |
|---|---|---|---|---|---|---|
| ln K, burning-rate constant (257) | 0.655 | **49%** [37, 59] | **34%** [23, 45] | 2% [0, 8] | 13% [7, 22] | 2% [1, 4] |
| d_ext/d0, extinction diameter ratio (158) | 0.619 | **36%** [23, 48] | 13% [7, 23] | **35%** [21, 50] | 14% [6, 24] | 2% [1, 7] |

Shares of the explained variance; 95% bootstrap intervals in brackets.

**Concepts and techniques:**
- **Power-law (log-linear) regression.** Combustion scaling laws are power laws, so the model is linear in the logs. Example: the d² law K = (8 k_g / (ρ_l c_pg)) ln(1 + B) [C1, C2].
- **Relative importance by the LMG decomposition**, the Shapley value of R² [M8, M9]:
  - each condition's share is its gain in R² averaged over every order of entry;
  - this stays meaningful when conditions are correlated, as they are in a test matrix.
- **Nonparametric bootstrap** (1000 resamples, percentile intervals) for the uncertainty of every share and coefficient [M7].
- **Theory check (combustion engineering).** Each fitted coefficient is compared with what the d² law predicts [C1, C2]. All four hold:
  1. The elasticity of K to the O2 fraction is 0.88 [0.77, 1.00]. The law predicts a value between 0 and 1, because d ln(1+B) / d ln B = B / ((1+B) ln(1+B)) < 1.
  2. The pressure effect is small (0.14). The d² law has no first-order pressure dependence.
  3. Helium raises K (+0.95 per unit mole fraction) through its higher thermal conductivity. CO2 lowers it (−0.44) through its higher heat capacity and the lower O2 mass fraction at the same mole fraction.
  4. A lower O2 fraction makes the flame go out at a larger diameter (−0.65): it is nearer its extinction limit. FLEX found limiting oxygen indices of about 0.12 for methanol and 0.15 for heptane in O2/N2 [C3].

**What it tells the model:**
- For suppression, oxygen and fuel matter most, the diluent next, and **pressure little** over 0.5 to 3 atm.
- The AI judgements had raised pressure to 0.080 from a reading of the FLEX objective; the measurements do not support that.
- This is the first weight evidence in the model that does not come from a judgement.

**Limits:**
- FLEX is droplets in quiescent gas. It says nothing about flow, solid shape or the purpose of a study.
- Solid flame spread and smoke have no measured response in the PSI tables (BASS-II records O2 and flow but no spread rate; SAME records no particle size). Prevention and detection therefore get no data stream.
- The table writes the burning-rate unit as "mm"; it is read as K, conventionally mm²/s. Shares and elasticities do not depend on the unit.

---

## B3. Judgement stream

### B3a. Literature-based judgements (used since config 1.4.0)

**What it does.** At the human lead's request (20:16), the expert form is filled in from textbooks, papers and NASA records instead of by team members. To keep the AI session from inventing 51 separate opinions, the form is filled by a fixed rule.

1. **Evidence classes.** For each question type, each dimension gets one evidence class, with the cited finding beside it (`scoring/literature_evidence.json`):
   - **1, decisive:** the sources show that this condition alone can decide the outcome (burns or not, detected or not, extinguished or not) within habitat ranges;
   - **2, strong modifier:** the sources report a quantified or clearly documented change in the outcome, but not an on-off effect;
   - **3, weak or not documented:** no source in the list documents an effect on that outcome.
2. **Rule.** Each pairwise judgement follows from the class difference, on Saaty's verbal scale [M11]: same class 1 (equal), one class apart 3 (moderately more important), two classes apart 5 (strongly more important).
3. **Weights.** The same AHP eigenvector and consistency ratio as for every other stream. The filled form, with the class, finding and sources of both dimensions beside each pair, is `scoring/literature_judgements.csv`.

| Question type | Class 1 (decisive) | Class 2 (strong modifier) | Class 3 (weak or not documented) | CR |
|---|---|---|---|---|
| prevention | O2 [C17, C15, C7]; flow [C7, C8]; fuel [C18F, C17] | pressure [C16]; shape [C4, C6, C19]; purpose [G1] | — | 0 |
| detection | purpose [G1]; fuel [C13] | flow [C13] | O2, pressure, shape | 0.009 |
| suppression | purpose [G1]; O2 [C3, C11]; fuel [C3] | diluent [C3, C3H]; flow [C7, C8]; pressure [C16] | shape | 0.008 |

**Key findings behind the classes** (sources in section 7):
- **Fuel, prevention:** the heat release capacity of PMMA (about 460 to 510 J/(g·K)) is an order of magnitude above that of PTFE (35), Nomex (52) or a polyimide (25) [C18F].
- **O2 and flow, prevention:** in microgravity a solid burns only inside a region of the O2–flow map, bounded by low-flow quenching and high-flow blowoff [C7, C8].
- **Pressure:** for PTFE the oxygen threshold rises from about 42% to about 53% when pressure falls from 101.3 to 48.2 kPa [C16]. That is quantified, but smaller than the range of O2 fractions habitats use.
- **Fuel, detection:** in SAME the ionization detector often missed the small smoke particles of Teflon and Kapton [C13].
- **O2 and fuel, suppression:** the FLEX limiting oxygen index is about 0.12 for methanol and 0.15 for heptane [C3].
- **Diluent, suppression:** CO2 moves methanol's limit only from about 0.12 to about 0.14 [C3, C3H].
- **Purpose:** evidence on a different outcome is indirect evidence, which systematic reviews rate down [G1]. 16 of the 24 catalog investigations measured a flammability-related outcome, so for prevention a purpose mismatch is a modifier. For detection (10 of 24) and suppression (2 tested an agent) it is decisive.

**Resulting weights (config 1.4.0):**

| Question type | o2 | pressure | flow | fuel | geometry | role | diluent |
|---|---|---|---|---|---|---|---|
| prevention | 0.251 | 0.083 | 0.250 | 0.250 | 0.083 | 0.083 | 0 |
| detection | 0.060 | 0.060 | 0.151 | 0.335 | 0.060 | 0.334 | 0 |
| suppression (after pooling with FLEX, B4) | 0.256 | 0.039 | 0.086 | 0.253 | 0.037 | 0.235 | 0.094 |

**Effect against config 1.3.0:**
- All 38 validation scenarios pass. Two change their top 3:
  - `stagnant PMMA` now ranks ACME-BRE first, a quiescent burner that emulates a solid; flow weighs more, and a stagnant zone is a no-flow condition;
  - `달 기지 아크릴 정체 구역` (lunar base acrylic stagnant zone) changes at rank 3.
- The demo presets keep their top 3, with scores up to 7.3 points lower (`lunar habitat` 81.5 → 75.2; `ISS` 94.4 → 93.4).
- **New weak point:** `lunar habitat` changes rank 1 when the O2 weight is halved, although SMAA keeps its rank 1 in every draw.

**Limits:**
- Three classes are coarse.
- The classes were assigned by an AI session from the cited findings. Several findings were checked only in abstracts (marked † in section 7).
- A class says whether a condition can decide the outcome, not by how much one condition outweighs another.
- Review by combustion researchers, and the team members' form (B3b), are the next steps. A filled form takes precedence over this stream automatically, with the human lead's decision to apply it.

### B3b. Form for people: AHP form for the team's combustion-trained members

**What it does:**
- `scoring/expert_form.csv` holds the 51 pairwise questions of the AHP. For example: "For a question about suppression, how much more important is it that an experiment matches the user's oxygen fraction than the user's fuel?"
- Each question points to the NASA evidence in `WEIGHTING.md` section 4. **The AI's answers are not shown**, to avoid anchoring [M10].
- Each person saves a copy as `scoring/expert_judgements/E1.csv`, E2 and so on; no names go into the repository.
- `scoring/derive_expert_weights.py` computes each person's weights and consistency ratio, and combines the people.

**Concepts and techniques:**
- **AHP** [M11]: weights are the principal eigenvector of the pairwise matrix. The consistency ratio CR = ((λ_max − n)/(n − 1)) / RI flags incoherent answers above 0.10.
- **Aggregation of individual judgements:** the element-wise geometric mean of the matrices of several people, the rule that keeps the reciprocal property [M2, M2b].
- **Best-worst method** [M1]: a lighter alternative if 51 questions are too many. A person compares the best criterion with each other one and each other one with the worst: (n − 1) + (n − 1) − 1 = 2n − 3 comparisons per question type, 29 in all. It is not implemented; the form can be shortened to it.

**Status:** the form is ready and the code is tested; no person has filled it in yet. Until then the judgement stream is the literature-based one (B3a), and every output says so.

---

## B4. Pooling the streams

**What it does.**
- `scoring/weight_streams.json` names the streams.
- `derive_weights.final_weights()` combines them:
  - judgement: tried in order (`judgement.prefer`): the team members' group weights if they exist and are consistent, then the literature-based judgements (B3a), then the AI AHP of 1.2.0;
  - data: inside the dimensions the data cover, judgement and data shares are combined by a **log-linear (geometric) opinion pool** with equal say (λ = 0.5), s_d ∝ s_judgement^(1−λ) · s_data^λ [M12];
  - the subset keeps the total weight the judgement gave it, and the other dimensions keep theirs.
- `apply` is true since config 1.3.0 (20:06); the judgement stream is the literature one since 1.4.0 (20:19).

**Effect of the pooling when it was applied in 1.3.0** (suppression only; prevention and detection have no data stream). In 1.4.0 the same pooling acts on the literature judgements; the result is in B3a.

| Dimension | AHP 1.2.0 | Pooled with FLEX |
|---|---|---|
| role | 0.286 | 0.286 |
| o2 | 0.162 | 0.204 |
| fuel | 0.162 | 0.202 |
| diluent | 0.162 | 0.124 |
| flow | 0.089 | 0.089 |
| geometry | 0.059 | 0.059 |
| pressure | 0.080 | 0.036 |

- All 38 validation scenarios keep their top 3, and scores move by at most 2.8 points.
- The judgement and the NASA data give different weights but the **same rankings**: a triangulation of the model.

**Why a geometric pool:**
- It is the rule AHP itself uses to combine judgements (B3).
- A dimension that one stream rates near zero stays low.
- Its result does not depend on which stream is applied first.

---

## B5. Robustness (already in the model, now with sources)

- **One weight at a time**, ×0.5 and ×1.5: 146 of 152 variants keep the top 3 (config 1.4.0).
- **Rank-order-centroid weights**, which keep only the order of importance [M13].
- **SMAA** over the order of importance [M14]: rank 1 holds in every draw for 8 of 12 test queries and in 80% or more for 11 of 12. `lunar habitat cotton fabric` has no clear winner (ACME-BRE 67%, SAFFIRE-II 33%).

All are in `python3 validation/sensitivity.py` and `validation/report.md`.

---

## 6. Combustion concepts the model uses, and the next combustion build-up

| Concept | Where in the model | Source |
|---|---|---|
| Oxygen fraction controls flame temperature and structure; the effect is nonlinear | O2 similarity on the log of the ratio; O2 weight | [C1] |
| Pressure and flammability | Droplets: little effect over 0.5 to 3 atm in FLEX (B2), as the d² law predicts [C1]. Solids: the maximum oxygen concentration for burning rises as total pressure falls; for PTFE it goes from about 42% at 101.3 kPa to about 53% at 48.2 kPa [C16]. So prevention keeps a pressure weight (0.090) that the droplet data alone would not give | [C1], [C16] |
| d² law, transfer number, burning-rate constant | data stream theory check | [C1], [C2] |
| Droplet flame extinction in diluted atmospheres on the ISS | data stream response | [C3] |
| Opposed against concurrent flame spread; thermally thin against thick fuels | flow configuration matrix; shape similarity | [C4], [C5], [C6] |
| Microgravity flammability boundary: low-flow (radiative) quenching | why flow matters in microgravity; prevention weights | [C7], [C8], [C9] |
| Inert diluents act mainly thermally (heat capacity) | diluent similarity | [C1] |
| Smoke particles grow larger in low gravity; detector response | detection purpose weight | [C13] |
| Material flammability screening and its limits for space | prevention questions; the gate on fuel | [C15], [C19], [C17] |

### B6. Atmosphere flame temperature (built as a check; it changes no score)

**What it does.** `scoring/flame_temperature.py` computes the stoichiometric adiabatic flame temperature of an atmosphere for a generic organic fuel:
- **Heat:** about 13.1 kJ is released per gram of O2 consumed, for most organic fuels [C10].
- **Products:** a generic CH2 fuel unit, so each mol of O2 consumed gives 2/3 mol CO2 and 2/3 mol H2O.
- **Temperature:** the NIST-JANAF enthalpies [C12] of the products are raised from 298 K until they absorb that heat.
- **Licence of the input:**
  - NIST-JANAF is NIST Standard Reference Database 13, copyrighted by the U.S. Secretary of Commerce under the Standard Reference Data Act. It is therefore not public-domain material.
  - The five tables were in the repository from 20:08 to 21:32 and were removed when this was noticed. They stay in earlier commits, since pushed history is not rewritten.
  - The script now reads tables that a user downloads locally (ignored by git).
  - Next step: rerun with the NASA Glenn coefficients [C12b], a NASA publication.
- **Neglected:** dissociation, so values above about 2200 K are upper bounds, and radiation.

| Atmosphere | Flame temperature (K) |
|---|---|
| 15% O2 in N2 | 1970 |
| air, 21% O2 (ISS cabin) | 2464 |
| 21% O2, 30% CO2, rest N2 | 2196 |
| 21% O2, 30% He, rest N2 | 2672 |
| 30% O2 in N2 (lunar habitat preset) | 3100 |
| 34% O2 in N2 | 3350 |

**Concept.** Flames fail near a limiting flame temperature [C11]. In CO2-diluted cup-burner flames, for example, the maximum flame temperature falls to about 1600 K at extinction. One physical number might therefore stand for both the oxygen fraction and the diluent, which the scorer treats as two dimensions. The values here neglect dissociation, so they are not comparable one to one with that threshold; only the ranking of atmospheres is used.

**Test on NASA data.** FLEX extinction diameter ratio, 158 tests, each model with fuel, droplet size and pressure as controls:

| Atmosphere described by | R² | AIC (lower is better) |
|---|---|---|
| O2 fraction only | 0.534 | −606.6 |
| flame temperature only | 0.553 | −613.3 |
| O2 fraction and the CO2 and He fractions | **0.619** | **−634.5** |

**What it tells the model:**
- Flame temperature explains part of the diluent effect, namely its thermal part through heat capacity. It does better than oxygen alone.
- It does not explain all of it: the separate O2 and diluent model is clearly better.
- Helium is the clearest case. It raises the flame temperature (low molar heat capacity), yet it does not delay extinction in FLEX: its coefficient is +0.20 [−0.07, 0.43]. A transport effect (its high diffusivity) outweighs the thermal one.
- So the measurements support keeping O2 and diluent as **separate dimensions**.
- They also show that the diluent similarity by heat capacity alone (config 1.1.0, change B) is incomplete for helium. That is a limit to state, and a candidate for a data-based diluent similarity.

---

## 7. References

Each entry gives where to read it; **open** = free full text.
- Bibliographic details of M8, M9, M12, M13 and M14 were checked by this session; all others by a separate AI agent against Crossref, NTRS, publisher or library records (2026-11-14). M10 was not checked by either.
- Content points marked † were checked only in an abstract or a secondary source.

**Systems engineering**
- [SE1] NASA (2016). *NASA Systems Engineering Handbook*, NASA/SP-2016-6105 Rev2. Sections 4.1 Stakeholder Expectations Definition, 4.2 Technical Requirements Definition, 4.1.1.2.7 and 6.2.1.2.3 bidirectional traceability, Appendix C "How to Write a Good Requirement". **Open:** https://ntrs.nasa.gov/citations/20170001761 ; https://www.nasa.gov/reference/4-0-system-design-processes
- [SE4] Mavin, A., Wilkinson, P., Harwood, A., Novak, M. (2009). Easy Approach to Requirements Syntax (EARS). *17th IEEE International Requirements Engineering Conference*, 317–322. doi:10.1109/RE.2009.9

**Decision analysis and data science**
- [G1] Guyatt, G. H. et al. (2011). GRADE guidelines: 8. Rating the quality of evidence – indirectness. *Journal of Clinical Epidemiology* 64(12), 1303–1310. doi:10.1016/j.jclinepi.2011.04.014. Indirectness of population, intervention or outcome; indirect evidence is rated down†.
- [M1] Rezaei, J. (2015). Best-worst multi-criteria decision-making method. *Omega* 53, 49–57. doi:10.1016/j.omega.2014.11.009
- [M2] Forman, E., Peniwati, K. (1998). Aggregating individual judgments and priorities with the analytic hierarchy process. *European Journal of Operational Research* 108(1), 165–169. doi:10.1016/S0377-2217(97)00244-0. Geometric-mean aggregation of judgements suits a group that acts as one unit†.
- [M2b] Aczél, J., Saaty, T. L. (1983). Procedures for synthesizing ratio judgements. *Journal of Mathematical Psychology* 27(1), 93–102. doi:10.1016/0022-2496(83)90028-7
- [M5] Gower, J. C. (1971). A general coefficient of similarity and some of its properties. *Biometrics* 27(4), 857–871. doi:10.2307/2528823
- [M6] Aamodt, A., Plaza, E. (1994). Case-based reasoning: foundational issues, methodological variations, and system approaches. *AI Communications* 7(1), 39–59. doi:10.3233/AIC-1994-7104
- [M7] Efron, B., Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall, Monographs on Statistics and Applied Probability 57. Reissue doi:10.1201/9780429246593
- [M8] Grömping, U. (2006). Relative importance for linear regression in R: the package relaimpo. *Journal of Statistical Software* 17(1), 1–27. doi:10.18637/jss.v017.i01. LMG (averaging over orderings) and bootstrap intervals. **Open:** https://www.jstatsoft.org/v17/i01
- [M9] Lipovetsky, S., Conklin, M. (2001). Analysis of regression in game theory approach. *Applied Stochastic Models in Business and Industry* 17(4), 319–330. doi:10.1002/asmb.446. The Shapley value of R²†.
- [M10] Tversky, A., Kahneman, D. (1974). Judgment under uncertainty: heuristics and biases. *Science* 185(4157), 1124–1131. doi:10.1126/science.185.4157.1124. Anchoring.
- [M11] Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill. Open overview by the author: https://www.isahp-org.creativedecisions.net/uploads/1-how-to-make-a-decision-the-analytic-hierarchy-process-t-l-saaty.pdf
- [M12] Genest, C., Zidek, J. V. (1986). Combining probability distributions: a critique and an annotated bibliography. *Statistical Science* 1(1), 114–135. doi:10.1214/ss/1177013825. Survey of pooling rules for expert opinions†. **Open:** https://projecteuclid.org/journals/statistical-science/volume-1/issue-1/Combining-Probability-Distributions-A-Critique-and-an-Annotated-Bibliography/10.1214/ss/1177013825.full
- [M13] Barron, F. H., Barrett, B. E. (1996). Decision quality using ranked attribute weights. *Management Science* 42(11), 1515–1523. doi:10.1287/mnsc.42.11.1515
- [M14] Lahdelma, R., Hokkanen, J., Salminen, P. (1998). SMAA – Stochastic multiobjective acceptability analysis. *European Journal of Operational Research* 106(1), 137–143. doi:10.1016/S0377-2217(97)00163-X

**Combustion and spacecraft fire safety**
- [C1] Turns, S. R. (2012). *An Introduction to Combustion: Concepts and Applications*, 3rd ed. McGraw-Hill. ISBN 978-0-07-338019-3:
  - Ch. 2: adiabatic flame temperature;
  - Ch. 8: flammability limits and quenching;
  - Ch. 9: diffusion flames;
  - Ch. 10: droplet burning (d² law, burning-rate constant, transfer number).

  Not reproduced; see `MODEL_BASIS.md`.
- [C2] Law, C. K. (1982). Recent advances in droplet vaporization and combustion. *Progress in Energy and Combustion Science* 8(3), 171–201. doi:10.1016/0360-1285(82)90011-9
- [C3] FLEX results:
  - Dietrich, D. L. et al. (2015). *Detailed Results from the Flame Extinguishment Experiment (FLEX), March 2009 to December 2011*. NASA/TP-2015-216046. **Open:** https://ntrs.nasa.gov/citations/20150023456
  - Dietrich, D. L., Nayagam, V., Hicks, M. C., Ferkul, P. V., Dryer, F. L., Farouk, T., Shaw, B. D., Suh, H. K., Choi, M. Y., Liu, Y. C., Avedisian, C. T., Williams, F. A. (2014). Droplet combustion experiments aboard the International Space Station. *Microgravity Science and Technology* 26(2), 65–76. doi:10.1007/s12217-014-9372-2. Limiting oxygen index about 0.12 for methanol and 0.15 for heptane in O2/N2†.
  - Nayagam, V., Dietrich, D. L., Ferkul, P. V., Hicks, M. C., Williams, F. A. (2012). Can cool flames support quasi-steady alkane droplet burning? *Combustion and Flame* 159(12), 3583–3588. doi:10.1016/j.combustflame.2012.07.012
  - Nayagam, V. et al. (2011). Methanol droplet extinction in oxygen/carbon-dioxide/nitrogen mixtures in microgravity: results from the ISS experiments. Eastern States Section of the Combustion Institute, Fall Meeting. **Open:** https://ntrs.nasa.gov/citations/20120016855
- [C3H] Hicks, M. C., Nayagam, V., Williams, F. A. (2010). Methanol droplet extinction in carbon-dioxide-enriched environments in microgravity. *Combustion and Flame* 157(8), 1439–1445. doi:10.1016/j.combustflame.2010.05.007. At 21% O2, more CO2 slightly lowered the extinction diameter†.
- [C4] de Ris, J. N. (1969). Spread of a laminar diffusion flame. *Symposium (International) on Combustion* 12(1), 241–252. doi:10.1016/S0082-0784(69)80407-8
- [C5] Fernandez-Pello, A. C., Ray, S. R., Glassman, I. (1981). Flame spread in an opposed forced flow: the effect of ambient oxygen concentration. *Symposium (International) on Combustion* 18(1), 579–589. doi:10.1016/S0082-0784(81)80063-X
- [C6] Wichman, I. S. (1992). Theory of opposed-flow flame spread. *Progress in Energy and Combustion Science* 18(6), 553–593. doi:10.1016/0360-1285(92)90039-4
- [C7] Olson, S. L. (1991). Mechanisms of microgravity flame spread over a thin solid fuel: oxygen and opposed flow effects. *Combustion Science and Technology* 76(4–6), 233–249. doi:10.1080/00102209108951711. A flame-spread map in O2 against flow, with low-flow quenching, high-flow blowoff and a flow of maximum flammability†. Also Olson, S. L., Ferkul, P. V., T'ien, J. S. (1989). Near-limit flame spread over a thin solid fuel in microgravity. *Symposium (International) on Combustion* 22(1), 1213–1222. doi:10.1016/S0082-0784(89)80132-8
- [C8] T'ien, J. S. (1986). Diffusion flame extinction at small stretch rates: the mechanism of radiative loss. *Combustion and Flame* 65(1), 31–34. doi:10.1016/0010-2180(86)90069-6. Also Chen, C. H. (1986). *Diffusion Flame Extinction in Slow Convective Flow under Microgravity Environment*. NASA-TM-88799. **Open:** https://ntrs.nasa.gov/citations/19860018906
- [C9] Fujita, O. (2015). Solid combustion research in microgravity as a basis of fire safety in space. *Proceedings of the Combustion Institute* 35(3), 2487–2502. doi:10.1016/j.proci.2014.08.010
- [C10] Huggett, C. (1980). Estimation of rate of heat release by means of oxygen consumption measurements. *Fire and Materials* 4(2), 61–65. doi:10.1002/fam.810040202. About 13.1 MJ per kg of O2 consumed.
  - Open commentary: NIST SP 958, pp. 280–282, https://nvlpubs.nist.gov/nistpubs/sp958-lide/html/280-282.html
  - The rule goes back to Thornton, W. M. (1917). *Philosophical Magazine* 33(194), 196–203. doi:10.1080/14786440208635627
- [C11] Takahashi, F., Linteris, G. T., Katta, V. R. (2008). Extinguishment of methane diffusion flames by carbon dioxide in coflow air and oxygen-enriched microgravity environments. *Combustion and Flame* 155(1–2), 37–53. doi:10.1016/j.combustflame.2008.03.005. Maximum flame temperature at extinction about 1600 K†. Abstract: https://www.nist.gov/node/601146
  - Background: Macek, A. (1976). *Flammability Limits: Thermodynamics and Kinetics*. NBSIR 76-1076. doi:10.6028/NBS.IR.76-1076. **Open:** https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nbsir76-1076.pdf
- [C12] Chase, M. W. Jr. (1998). NIST-JANAF Thermochemical Tables, 4th ed. *Journal of Physical and Chemical Reference Data*, Monograph 9. NIST SRD 13, doi:10.18434/T42S31. **Open:** https://janaf.nist.gov/tables/N-023.html and tables O-029, C-095, H-064, He-001. NIST SRD, copyright U.S. Secretary of Commerce; not redistributed here.
- [C12b] McBride, B. J., Zehe, M. J., Gordon, S. (2002). *NASA Glenn Coefficients for Calculating Thermodynamic Properties of Individual Species*. NASA/TP-2002-211556. **Open:** https://ntrs.nasa.gov/citations/20020085330
- [C13] Spacecraft smoke:
  - Urban, D. L. et al. (2008). Spacecraft fire detection: smoke properties and transport in low-gravity. AIAA Aerospace Sciences Meeting. **Open:** https://ntrs.nasa.gov/citations/20080012612
  - Meyer, M. E., Urban, D. L., Mulholland, G. W., Bryg, V., Yuan, Z.-G., Ruff, G. A., Cleary, T., Yang, J. (2018). Evaluation of spacecraft smoke detector performance in the low-gravity environment. *Fire Safety Journal* 98, 74–81. doi:10.1016/j.firesaf.2018.04.004
- [C15] NASA-STD-6001B. *Flammability, Offgassing, and Compatibility Requirements and Test Procedures.* **Open:** https://standards.nasa.gov/standard/NASA/NASA-STD-6001
- [C16] Hirsch, D., Williams, J., Beeson, H. (2008). Pressure effects on oxygen concentration flammability thresholds of polymeric materials for aerospace applications. *Journal of Testing and Evaluation* 36(1), 69–72. doi:10.1520/JTE100975. Preprint, **open:** https://ntrs.nasa.gov/citations/20070005041
- [C17] Fenimore, C. P., Martin, F. J. (1966). Flammability of polymers. *Combustion and Flame* 10(2), 135–139. doi:10.1016/0010-2180(66)90059-9. The limiting oxygen index.
- [C18F] Walters, R. N., Lyon, R. E. (2001). *Calculating Polymer Flammability from Molar Group Contributions*. DOT/FAA/AR-01/31, US Federal Aviation Administration. Table 1: heat release capacity of PMMA (about 460 to 510 J/(g·K)), PTFE (35), Nomex (52) and polyimide (25). **Open:** https://rosap.ntl.bts.gov/view/dot/92724
- [C19] Jomaas, G. et al. (2015). Fire safety in space – beyond flammability testing of small samples. *Acta Astronautica* 109, 208–216. doi:10.1016/j.actaastro.2014.11.025

**NASA data**
- NASA Physical Sciences Informatics, FLEX experimental table, PSI-69 (CC0-1.0): https://psi.nasa.gov/
- Records PSI-25, 26, 98, 99, 101 and 102, for the evidence in `WEIGHTING.md`.

**Further reading for the next build-ups (not used yet)**
- **Partial gravity:** Ronney, P. D. (1998). Understanding combustion processes through microgravity research. *Symposium (International) on Combustion* 27(2), 2485–2506. doi:10.1016/S0082-0784(98)80101-X. A buoyant flow scale. **Open:** https://ntrs.nasa.gov/citations/20000000185
- **Objective weighting:** Diakoulaki, D., Mavrotas, G., Papayannakis, L. (1995). Determining objective weights in multiple criteria problems: the CRITIC method. *Computers & Operations Research* 22(7), 763–770. doi:10.1016/0305-0548(94)00059-H
- **Variance-based sensitivity:** Saltelli, A. et al. (2008). *Global Sensitivity Analysis: The Primer*. Wiley. doi:10.1002/9780470725184
- **Quality function deployment, for requirement-importance roll-ups:** Hauser, J. R., Clausing, D. (1988). The house of quality. *Harvard Business Review* 66(3), 63–73. Open NASA source: Dean, E. B. (1992). *Quality Function Deployment for Large Systems*. NASA Langley. https://ntrs.nasa.gov/api/citations/20040129650/downloads/20040129650.pdf
