# Weighting by purpose: technique, derivation and checks

*AI-generated (Claude Code, catalog role), 2026-11-14, config 1.2.0. Written for the team, in answer to the questions "how are the weights set for each purpose, by which technique, and on what basis?"*

> **Update, config 1.4.0 (20:19):** the scorer's judgement stream is now the literature-based one (`scoring/BUILDUP.md` B3): prevention o2 0.251, flow 0.250, fuel 0.250, pressure, geometry and role 0.083 each; detection role 0.334, fuel 0.335, flow 0.151, the others 0.060; suppression, after pooling with FLEX, o2 0.256, fuel 0.253, role 0.235, diluent 0.094, flow 0.086, pressure 0.039, geometry 0.037. The AI judgements and weights below are the earlier stream (configs 1.2.0 and 1.3.0), kept for comparison.
>
> **Update, config 1.3.0 (20:06):** the AHP weights below became the *judgement stream*. For suppression the scorer pools them with the NASA FLEX measurements, and uses o2 0.204, fuel 0.202, diluent 0.124, pressure 0.036, role 0.286, flow 0.089, geometry 0.059. Prevention and detection are unchanged. The checks in section 5 were run with 1.2.0; with 1.3.0 every top 3 of the 38 scenarios is the same, and suppression's one-at-a-time check gives 54 of 56. See `scoring/BUILDUP.md`.

Scores and rankings are the team's computation, not NASA's conclusion, and not safety guidance. The weights are in `scoring/scoring_config.json` (`profiles`). They are derived from `scoring/ahp_judgements.json` by `scoring/derive_weights.py`. The ranking code is `scoring/scorer.py` and its port `web/scorer.js`. `scoring/METHOD.md` gives the whole ranking in short; this file goes deeper into the weights.

---

## 0. Short answer

- **What "purpose" means:** each question is one of three types (profiles), and each type has its own seven weights:
  - **prevention:** will this material burn, how does a fire spread;
  - **detection:** smoke and detectors;
  - **suppression:** putting a fire out.
- **How the score uses the weights:**
  - The score is a weighted sum (simple additive weighting) of similarities on a common 0–1 scale.
  - The weights are rescaled over the conditions the user gave.
  - A gate stops a wrong fuel or a far-off oxygen level from being made up by other matches.
  - An evidence factor scales the result by data quality.
- **How the weights are derived (config 1.2.0):** by the **analytic hierarchy process (AHP)**.
  1. For each profile, every pair of dimensions is compared on Saaty's 1–9 scale: 51 judgements in all, each with its basis in a NASA record sentence, the textbook or the team's reasoning.
  2. The weights are the principal eigenvector of each comparison matrix.
  3. The consistency ratio checks that the judgements fit together: 0.012, 0.014 and 0.006, far below Saaty's limit of 0.10.
  4. A unit test checks that the config holds exactly the derived weights.
- **Who made the judgements:** an AI session made them from the evidence in section 4. The human lead approved them as they are and decided to apply them (19:26 KST). Earlier configs (1.0.0, 1.1.0) used directly allocated weights; section 3.4 compares the two.
- **What the checks show:**
  - The derived weights give the same top 3 as the earlier weights in all 12 purpose test queries.
  - Rank 1 changes in 1 of 152 variants where one weight is halved or raised by half.
  - When only the order of importance is kept (SMAA, 300 random weight sets per profile), rank 1 holds in 100% of draws for 9 of 12 queries.
  - The weakest result is `lunar habitat cotton fabric`: SAFFIRE-II stays rank 1 in only 46% of draws, and ACME-BRE takes it in the other 54% (section 5.5).
  - The purpose matters: prevention weights used on detection or suppression questions change the top 3 in 5 of 8 queries.

---

## 1. How the purpose is chosen and where it acts

### 1.1 Choosing the profile

1. An explicit `profile` (or `concern`) field in the query wins.
2. Otherwise the query text is matched against `keywords.concern`. The lists are checked in the order **detection, suppression, prevention**, and the first list with a match decides.
   - detection: smoke, detector, detection, alarm, aerosol, particle, sensor, monitor; Korean 연기 (smoke), 감지 (detection), 탐지 (detection), 경보 (alarm), 센서 (sensor);
   - suppression: suppress, extinguish, extinguisher, put out, CO2 flood, inerting, inert gas; Korean 소화 (extinguishing), 진압 (suppression), 소화기 (extinguisher), 끄 (put out);
   - prevention: flammability, flame spread, fire spread, material selection; Korean 가연성 (flammability), 재료 선정 (material selection), 확산 (spread), 예방 (prevention).
3. With no match the profile is **prevention**, the default. The result lists this as an assumption (`concern` with source `default`).

Why this order:
- A detection or suppression question usually also names a fire, a material or an atmosphere, which are prevention words in a wide sense.
- The narrower purpose is therefore checked first. "Smoke from an overheated wire" is a detection question, even though it names a material.

### 1.2 Where the profile acts

The profile changes three things:

| Where | What changes | Code |
|---|---|---|
| Weight vector `w_d` | The seven weights of the profile (section 3.3) | `rank()`, `profiles[...].weights` |
| Research-purpose similarity `S_role` | The investigation's fire-safety axis is compared with the question's purpose: same axis 1.0, related research focus 0.7, fundamental study 0.4, other 0.2. The related foci are prevention: flammability boundary, flame spread, ignition, burning rate, extinction limit; detection: smoke and soot, detection; suppression: suppression, extinction limit | `s_role()`, `similarity.role` |
| Diluent dimension | Scored only in a suppression question that names a diluent gas | `similarities()` |

- The fire-safety axis (`fire_safety_role`) and the research focus (`research_focus`) of each investigation are the **team's classification** of the PSI record, not NASA's. They are in `data/catalog/investigations.csv`.
- So the purpose enters twice: through how much the research-purpose dimension weighs, and through which investigations score high on it.

---

## 2. The scoring technique, step by step

The ranking is a multi-criteria decision model (MCDA). Each step below has a standard name; the right column says why that choice was made here.

```
score = 100 × M × G × Σ_d ( w_d × S_d )
```

| Step | Standard technique | What it does here | Why this choice |
|---|---|---|---|
| 1. Common scale | Single-attribute value functions | Each condition becomes a similarity `S_d` from 0 to 1 (rules in `METHOD.md` 1.4). An oxygen gap and a fuel gap can then be added | Weights only mean something when every criterion is on the same scale |
| 2. Weighted sum | Simple additive weighting (SAW), also called the weighted-sum or additive value model | `Σ w_d S_d` | Transparent: each term `w_d S_d` is returned as `contributions`, so the page can show why a result ranks where it does |
| 3. Rescaling over active criteria | Renormalisation of weights over the criteria that are present | A dimension counts only if the query gives it (research purpose always counts). The weights of the active dimensions are divided by their sum | A condition the user did not give is not a mismatch. Scoring it as 0 would punish short queries, and scoring it as 1 would reward them. Rescaling keeps the **ratios** between the given conditions, which is exactly what AHP weights express |
| 4. Gate | Non-compensatory screening (conjunctive rule, similar to a veto threshold in outranking methods) | If fuel or oxygen similarity is below 0.2, the score is multiplied by 0.5 to 1.0 (linear ramp) | A weighted sum is compensatory: a perfect pressure match could make up for a liquid fuel in a question about fabric. Combustion does not work that way for fuel phase and oxygen. The ramp avoids a cliff at 0.2 |
| 5. Evidence factor | Multiplicative quality modifier, outside the weighted sum | `M = 0.7 + 0.3 × mean(data availability, microgravity duration, verification)` | Data quality should scale a close match, never replace one. The floor 0.7 means evidence can cut at most 30%, so a close but poorly documented study still beats a distant, well documented one |
| 6. Ties | Tie-breaking on a secondary criterion | Scores within 3 points are ordered by evidence, then by a 1 g comparison | A difference of a few points is inside the precision of the weights (section 5) |

**Example of step 3** (query `smoke detector on ISS`, detection profile). The ISS preset gives oxygen, pressure and flow; no fuel or shape is named. The active weights sum to 0.728 and are rescaled:

| Dimension | Profile weight | Weight used |
|---|---|---|
| o2 | 0.085 | 0.117 |
| pressure | 0.049 | 0.067 |
| flow | 0.136 | 0.187 |
| role | 0.458 | 0.629 |

**What the weighted sum assumes, and how the model handles it.** An additive model assumes that the criteria act independently: how much a good oxygen match is worth does not depend on how well the fuel matched.
- The two strongest exceptions are handled outside the sum, by the gate (fuel and oxygen).
- Oxygen fraction and pressure are compared separately. When the user's pair of values falls inside both tested ranges, but the ranges come from different tests, the result says so (`ranges_separate` warning).
- Other interactions are not modelled. This is listed in section 6.

---

## 3. How the weights are derived: the analytic hierarchy process

### 3.1 Why AHP, and why not learning from data

- **Learning from data is not possible here.** Supervised learning, or fitting weights by regression, needs examples of correct answers: questions with the investigations an expert would rank first. No such set exists for the NASA PSI investigations, and inventing one would only fit the weights to the team's own guesses. Section 6 says what such a set would take.
- **AHP turns judgements into weights in a checkable way.** It is a standard technique for deriving criteria weights when the weights express relative importance rather than a measured quantity (Saaty 1980).
  - It asks one small question at a time: is A more important than B for this purpose, and how much?
  - It computes the weights from all answers together.
  - It measures how well the answers agree with each other (consistency ratio).
  - Each pairwise answer carries its own reason, so a reviewer can disagree with one pair without redoing everything.

### 3.2 The procedure

1. **Pairwise judgements** (`scoring/ahp_judgements.json`). For each profile, every pair of its dimensions is compared on Saaty's scale:
   - 1 equal; 3 moderately; 5 strongly; 7 very strongly; 9 extremely more important; 2, 4, 6, 8 in between;
   - prevention and detection compare 6 dimensions (15 pairs each), suppression 7 dimensions (21 pairs): 51 judgements;
   - each judgement has a reason that points to the evidence in section 4.
2. **Comparison matrix.** `A[a][b] = v`, `A[b][a] = 1/v`, `A[i][i] = 1`. The script rejects a missing or repeated pair and a value outside 1/9 to 9.
3. **Weights = principal eigenvector** of `A`, normalised to sum to 1, found by power iteration (Saaty's eigenvector method).
4. **Consistency.**
   - `λ_max` is the principal eigenvalue; for a perfectly consistent matrix it equals n.
   - Consistency index `CI = (λ_max − n) / (n − 1)`.
   - Consistency ratio `CR = CI / RI`, with Saaty's random index RI = 1.24 for n = 6 and 1.32 for n = 7. Published RI tables differ slightly; with CR near 0.01 the conclusion does not depend on which is used.
   - A matrix with CR above 0.10 is rejected and must be revised.
5. **Cross-check.** The row geometric-mean method, the other standard AHP estimate, gives weights within 0.004 of the eigenvector for every dimension.
6. **Rounding.** Weights are rounded to 3 decimals; the rounding remainder goes to the largest weight, so each profile sums to exactly 1.
7. **Lock.** `python3 scoring/derive_weights.py --write` writes the weights into the config. The unit test `AhpWeights.test_config_weights_are_the_derivation` fails if anyone edits a weight in the config without changing a judgement.

### 3.3 Result

| Profile | λ_max | CI | CR | o2 | pressure | flow | fuel | geometry | role | diluent |
|---|---|---|---|---|---|---|---|---|---|---|
| prevention | 6.077 | 0.015 | 0.012 | 0.285 | 0.090 | 0.166 | 0.267 | 0.111 | 0.081 | 0 |
| detection | 6.088 | 0.018 | 0.014 | 0.085 | 0.049 | 0.136 | 0.221 | 0.051 | 0.458 | 0 |
| suppression | 7.051 | 0.008 | 0.006 | 0.162 | 0.080 | 0.089 | 0.162 | 0.059 | 0.286 | 0.162 |

Rerun: `python3 scoring/derive_weights.py` (prints this table and both estimates).

### 3.4 Compared with the earlier weights (config 1.0.0 to 1.1.0)

The earlier weights were set by direct point allocation: an AI session shared 1.0 per profile in steps of 0.05 (commit `8acc033`, 10:52), and the human lead approved them at 16:51.

| Profile | Dimension | Direct (1.1.0) | AHP (1.2.0) | Main reason for the change |
|---|---|---|---|---|
| prevention | o2 | 0.25 | 0.285 | O2 was judged more important than flow, pressure, shape and purpose; fuel loses a little against geometry |
| | flow | 0.20 | 0.166 | Judged below both O2 and fuel |
| | fuel | 0.25 | 0.267 | |
| | pressure | 0.10 | 0.090 | |
| | geometry | 0.10 | 0.111 | Geometry is a primary variable of BASS-II; judged above research purpose |
| | role | 0.10 | 0.081 | |
| detection | role | 0.40 | 0.458 | A study that did not measure smoke cannot answer at all |
| | fuel | 0.30 | 0.221 | |
| | flow | 0.10 | 0.136 | The SAME record names flow and mixing for particle growth, not oxygen |
| | o2 | 0.10 | 0.085 | |
| | pressure, geometry | 0.05, 0.05 | 0.049, 0.051 | |
| suppression | role | 0.30 | 0.286 | |
| | fuel, o2, diluent | 0.20, 0.15, 0.15 | 0.162 each | Fuel, oxygen and diluent were judged equal: the limiting oxygen belongs to a fuel and a suppressant together (FLEX record) |
| | flow | 0.10 | 0.089 | |
| | pressure | 0.05 | 0.080 | FLEX measures the limiting oxygen as a function of pressure, which the direct weights under-rated |
| | geometry | 0.05 | 0.059 | |

What the change does to the results:
- **Purpose test queries:** the top 3 are the same in all 12 (section 5).
- **Validation scenarios:**
  - the top 3 are the same in 35 of 38;
  - three change at rank 2 or 3: `stagnant PMMA` swaps ACME-BRE and BASS; `달 기지 아크릴 정체 구역` (lunar base acrylic stagnant zone) has SAFFIRE-II third instead of FLEX; `water mist suppression system for a lunar habitat` has ACME-CFI-G third instead of BASS;
  - all 38 still pass.
- **Scores:** they move by at most 3.3 points. `ISS` gives 94.4, 94.4, 92.8 (was 94.0, 94.0, 92.7).

### 3.5 What the derivation does and does not add

- **It adds:**
  - each weight now follows from explicit pairwise statements that can be checked one by one against the evidence;
  - the statements are shown to be consistent (CR about 0.01);
  - the weights cannot drift from the judgements, because a test locks them.
- **It does not add independence.** The judgements were written by an AI session that knew the earlier weights, from the same evidence. AHP makes the judgement explicit and checked; it does not make it more than a judgement.
- **The next step** is to have combustion researchers fill in the same 51 pairs (section 6).

---

## 4. Evidence behind the judgements, profile by profile

Each row gives the basis of the judgements about a dimension and its type:
- **record:** a sentence from a NASA PSI record (all CC0-1.0; the field name is given);
- **textbook:** a section of Turns 2012 (`MODEL_BASIS.md`);
- **team:** the team's reasoning.

The pair-by-pair values and reasons are in `scoring/ahp_judgements.json`.

### 4.1 Prevention (default): o2 0.285, fuel 0.267, flow 0.166, geometry 0.111, pressure 0.090, role 0.081

| Dimension | Weight | Basis | Type |
|---|---|---|---|
| o2 and flow | 0.285, 0.166 | BASS-II (PSI-25), `approach`: "Main variables are airflow speed and oxygen concentration". `hypothesis`: testing at constant O2 "permits studying flame spread and extinction at low and high flow speed". Its publications report a microgravity flammability boundary and a critical flow velocity for radiative extinction. Saffire-II (PSI-99), `objective`: to "investigate the low-g flammability limits"; `approach`: air flow of 20 or 30 cm/s, concurrent or opposed | record |
| | | Oxygen in the oxidizer has a strong, nonlinear effect on flames (Ch. 9). Convection raises heat and mass transfer, sub-linearly with speed (Ch. 10) | textbook |
| | | O2 above flow (judgement 2): oxygen is set by the habitat design, and its effect is the one the gate also protects. Flow below fuel (1/2): cabin flow varies with location and is often not known | team |
| fuel | 0.267 | Saffire-I and -II (PSI-98, 99), `researchImpacts`: results "determine microgravity flammability limits for several spacecraft materials, help to validate NASA's material selection criteria". Prevention is decided material by material | record |
| | | Fuel was judged equal to O2. Its derived weight is a little lower because geometry was judged closer to fuel (2) than to O2 (3): thin and thick samples of one material behave differently | team |
| geometry | 0.111 | BASS-II (PSI-25), `objective`: the primary variables include "Sample geometry (rods, spherical section, slabs, films, and fabric sheets", listed after flow velocity and oxygen | record |
| pressure | 0.090 | The lean flammability limit depends only weakly on pressure, while oxygen content changes flame structure strongly (Ch. 8 and 9). O2 against pressure: 3 | textbook |
| role | 0.081 | Most investigations that match a prevention question are flame-spread or flammability studies already. The research purpose here mainly separates them from fundamental studies | team |

### 4.2 Detection: role 0.458, fuel 0.221, flow 0.136, o2 0.085, geometry 0.051, pressure 0.049

| Dimension | Weight | Basis | Type |
|---|---|---|---|
| role | 0.458 | SAME (PSI-102), `hypothesis`: a change in smoke particle size and number "will, in turn, affect the response of the smoke detectors and possibly result in some detectors not producing an alarm". `researchImpacts`: SAME gives "quantitative data on the sensitivity of these detectors to reduced gravity smokes". A detection question can only be answered by a study that measured smoke or detector response; a flame-spread study did not. Role against fuel: 3 | record |
| fuel | 0.221 | SAME (PSI-102), `approach`: measurements used "smoke generated by overheated spacecraft materials". SAME-R (PSI-101), `objective`: the reflight added "new materials". Smoke comes from the material that pyrolyses or smoulders | record |
| flow | 0.136 | SAME (PSI-102), `hypothesis`: larger particles are favoured by "the reduced velocities and mixing at μg conditions"; the droplet-growth model takes "the flow environment" as an input. Flow against O2: 2 | record |
| o2 | 0.085 | The SAME tests heat materials until they smoke rather than burning them in a flame, so the oxygen level matters less than for flame spread | team |
| pressure, geometry | 0.049, 0.051 | Refine only: no detection record names them as a main variable | team |

### 4.3 Suppression: role 0.286, fuel 0.162, o2 0.162, diluent 0.162, flow 0.089, pressure 0.080, geometry 0.059

| Dimension | Weight | Basis | Type |
|---|---|---|---|
| role | 0.286 | BASS (PSI-26), `objective`: "Assess the effectiveness of an inert, gaseous extinguishing agent (similar to that used on ISS)". FLEX (PSI-69), `objective`: "measure the effectiveness of various gaseous fire suppressants such as CO2, He, and SF6". The first question is whether extinguishment was tested at all. Role against each of fuel, O2 and diluent: 2 | record |
| fuel, o2, diluent | 0.162 each | FLEX (PSI-69), `approach`: "determine the Limiting Oxygen Index (LOI) as a function of ambient pressure and determine how the presence of a suppressant influences the LOI". The limiting oxygen belongs to a fuel and a suppressant together, so the three were judged equal. BASS (PSI-26), `objective`: the agent's effect is assessed "over different materials, geometries, preheating, and flow" | record |
| | | Inert diluents act mainly thermally (Ch. 8), so another inert is compared by molar heat capacity (`MODEL_BASIS.md`) | textbook |
| flow | 0.089 | BASS (PSI-26): flow is one of the conditions in the objective above | record |
| pressure | 0.080 | The FLEX sentence above makes pressure a variable of the limiting oxygen. O2 against pressure: 2 | record |
| geometry | 0.059 | One of several BASS conditions | record, team |

---

## 5. Checks of the weights

All numbers come from `python3 validation/sensitivity.py`, sections "Weighting by purpose" and "Weight uncertainty: SMAA"; the same tables are at the end of `validation/report.md`. Config 1.2.0.

Each profile was tested on four queries that the scorer reads as that purpose:
- **prevention:** `ISS`, `lunar habitat`, `ISS cotton fabric`, `lunar habitat cotton fabric`;
- **detection:** `smoke detector on ISS`, `wire insulation overheating smoke`, `smoke detector for a lunar rover`, `kapton teflon smoke`;
- **suppression:** `CO2 suppression of heptane fire`, `nitrogen extinguish fabric fire ISS`, `fire extinguisher for a Mars habitat`, `inert gas suppression ISS`.

### 5.1 One weight at a time

Each non-zero weight of the profile is halved, then raised by half, and the weights are rescaled to sum to 1.

| Profile | Same top 3 | Rank 1 changes |
|---|---|---|
| prevention | 45 of 48 | 1: `lunar habitat cotton fabric` with O2 ×1.5 puts ACME-BRE first (same three) |
| detection | 48 of 48 | 0 |
| suppression | 53 of 56 | 0 |

### 5.2 Other ways to weight

| Profile | Equal weights: same top 3 / rank 1 | Rank-order centroid: same top 3 / rank 1 | Other profiles' weights: same top 3 / rank 1 |
|---|---|---|---|
| prevention | 3 of 4 / 4 of 4 | 3 of 4 / 3 of 4 | detection 3 of 4 / 4 of 4; suppression 4 of 4 / 4 of 4 |
| detection | 3 of 4 / 3 of 4 | 4 of 4 / 4 of 4 | prevention 2 of 4 / 3 of 4; suppression 3 of 4 / 3 of 4 |
| suppression | 1 of 4 / 4 of 4 | 4 of 4 / 4 of 4 | prevention 1 of 4 / 3 of 4; detection 4 of 4 / 4 of 4 |

- **Equal weights** over the profile's non-zero dimensions.
- **Rank-order centroid (ROC)** weights keep only the order of importance: `w_i = (1/n) Σ_{j≥i} 1/j`, with tied dimensions sharing the mean (Barron and Barrett 1996). From the AHP order:
  - prevention: o2 0.408, fuel 0.242, flow 0.158, geometry 0.103, pressure 0.061, role 0.028;
  - detection: role 0.408, fuel 0.242, flow 0.158, o2 0.103, geometry 0.061, pressure 0.028;
  - suppression: role 0.370; fuel, o2 and diluent 0.164 each; flow 0.073, pressure 0.044, geometry 0.020.

### 5.3 Does the purpose change the answer?

Prevention weights change the top 3 in 2 of 4 detection queries and 3 of 4 suppression queries. Two examples:

- **`smoke detector on ISS`:**
  - with detection weights: SAME 95.2, SAME-R 95.2, DAFT 87.9;
  - with prevention weights, the research purpose weighs only 0.13. Three flame-spread studies (BASS-II, BASS, Saffire-III) tie at 84.3 for third place, BASS-II takes it on the tie-break, and the dust and aerosol study DAFT drops out.
- **`nitrogen extinguish fabric fire ISS`:**
  - with suppression weights: BASS 93.0, BASS-II 84.7, ACME-BRE 71.1;
  - with prevention weights the diluent is not scored and the research purpose weighs 0.081. Saffire-III (83.9), a flame-spread test with no extinguishing agent, comes third; with suppression weights it scores 55.1.

Detection and suppression weights leave the prevention queries almost unchanged: one change, rank 3 of `lunar habitat`. In those queries every top candidate is a prevention study that also matches fuel and atmosphere. The research-purpose dimension still compares with the prevention purpose, because only the weights were swapped.

### 5.4 Uncertainty of the weights: SMAA

Stochastic multicriteria acceptability analysis (SMAA; Lahdelma, Hokkanen and Salminen 1998) explores the weight space instead of trusting one weight vector. Here only the **order of importance** from AHP is kept:
- 300 weight vectors per profile are drawn uniformly from the simplex, sorted, and given to the dimensions in the AHP order;
- tied dimensions share their ranks in random order;
- the share of draws that keeps an investigation at rank 1, or in the top 3, is its acceptability.

The AI layer's `data/insights/robustness.json` (`ai/build_all.py`, pm role) runs a different SMAA-style check: Dirichlet draws centred on the profile weights. It shows how stable a rank is near the chosen weights. The check below keeps only their order, so it is the wider test.

| Profile | Query | Top 3 (AHP weights) | Same rank 1 | Same top 3 as a set |
|---|---|---|---|---|
| prevention | ISS | BASS-II, BASS, SAFFIRE-II | 100% | 63% (SAME enters in 37%) |
| prevention | lunar habitat | ACME-BRE, FLEX, ACME-CFI-G | 100% | 100% |
| prevention | ISS cotton fabric | BASS, SAFFIRE-III, BASS-II | 100% | 100% |
| prevention | lunar habitat cotton fabric | SAFFIRE-II, SAFFIRE-I, ACME-BRE | 46% | 70% |
| detection | smoke detector on ISS | SAME, SAME-R, DAFT | 100% | 91% |
| detection | wire insulation overheating smoke | SAME, SAME-R, SAME-SIM | 100% | 100% |
| detection | smoke detector for a lunar rover | SAME, SAME-R, FLEX-2 | 100% | 82% |
| detection | kapton teflon smoke | SAME, SAME-R, SAME-SIM | 100% | 100% |
| suppression | CO2 suppression of heptane fire | FLEX, FLEX-2, CFI | 100% | 99% |
| suppression | nitrogen extinguish fabric fire ISS | BASS, BASS-II, ACME-BRE | 100% | 100% |
| suppression | fire extinguisher for a Mars habitat | BASS, FLEX, BASS-II | 90% | 100% |
| suppression | inert gas suppression ISS | BASS, FLEX, BASS-II | 80% | 100% |

### 5.5 What the checks show

- **Precision of the numbers.** One change of ±50% in one weight moves rank 1 once in 152 variants.
- **Order over numbers.** With only the order of importance kept, rank 1 holds in every draw for 9 of 12 queries and in 80% or more for 11 of 12. The ranking is carried mainly by the order of importance, which the judgements in section 4 justify, rather than by the exact values.
- **One close call.** In `lunar habitat cotton fabric`, rank 1 is ACME-BRE in 54% of draws and SAFFIRE-II in 46%; ACME-BRE is in the top 3 in every draw. With the AHP weights ACME-BRE is third (65.8 against 73.2 for SAFFIRE-II), so the 3-point tie margin does not flag it. This query has no clear winner, and should not be presented as having one.
- **Weighting matters.** Equal weights change the top 3 in 5 of 12 queries, mostly in suppression: they give geometry and pressure as much weight as extinguishment.
- **The purpose matters** for detection and suppression (section 5.3).

Earlier checks that also bear on the weights:
- `validation/run_validation.py`: each weight ±0.05 in five scenarios (P01, P05, D01, S01, L01), rank 1 unchanged in 5 of 5;
- 38 of 38 validation scenarios pass, including 2 detection and 2 suppression scenarios with expected answers.

**What these checks do not show:** that the weights are the best ones. They show that the weights follow consistent judgements, that the result is stable under reasonable changes, and that the purpose changes the answer where it should.

---

## 6. Limits and next steps

**Limits**
- The 51 pairwise judgements are an AI session's judgements from the evidence in section 4, approved as they are by the human lead. AHP checks their consistency, not their truth. There is no ground-truth ranking to test them against.
- The weighted sum treats the criteria as independent. Only fuel and oxygen are handled non-additively (the gate). Other interactions, such as flow and oxygen together setting a flammability boundary, are not modelled as interactions.
- Purpose is read from keywords. A query that mixes purposes gets the first one in the order detection, suppression, prevention. A query with no purpose word gets prevention, and the assumption is shown.
- Each profile was checked on four queries. The validation set has 6 prevention, 2 detection and 2 suppression scenarios. The detection and suppression profiles rest on fewer examples.
- The research-purpose similarity uses the team's classification of each investigation. A different classification would change `S_role` and, through the large role weights, the detection and suppression rankings.
- `lunar habitat cotton fabric` has an unstable rank 1 (section 5.5).
- **What the consistency ratio does not show (config 1.4.0 and later).**
  - The judgements follow from evidence classes by a fixed rule: 1 for the same class, 3 for one class apart, 5 for two apart.
  - The prevention weights therefore reduce to "decisive : supporting = 3 : 1", and a CR near 0 follows from the construction.
  - CR shows that the rule was applied consistently. It is not a measure of the quality of the judgements, so do not present it as one.
- **The FLEX data stream** (`scoring/data_weights.json`; for the method see `scoring/BUILDUP.md` B2).
  - Its shares of explained variance (LMG) depend on the ranges that FLEX chose to test and on droplet burning.
  - The burning-rate unit in the table is "not confirmed".
  - Carrying the shares over to the suppression of solid fires is an assumption.

**Next steps (plan)**
1. **Researchers' judgements.**
   - Ask combustion researchers to fill in the same 51 pairs: `scoring/ahp_judgements.json` is the form, with the evidence beside each pair.
   - Combine several researchers by the geometric mean of their judgements, the usual group-AHP rule.
   - Rederive with `scoring/derive_weights.py --write` and compare the rankings with the tables in section 5.
2. **A reference set.**
   - For 10 to 20 questions, researchers rank the investigations they would consult.
   - Measure agreement with the scorer, for example with a rank correlation.
   - With enough such examples, weights could also be fitted to the reference set and compared with the AHP weights: the "learning from data" that is not possible today.
3. **More scenarios.** Add detection and suppression scenarios to `validation/scenarios.json`, so each profile rests on as many checks as prevention.
4. **Weights on the page.** Let users see, or change, the weights on the page. `scoring_config.json` is written so that the page can read the weights, for example to draw sliders.

---

## 7. References for the methods

- Saaty, T. L. *The Analytic Hierarchy Process.* McGraw-Hill, 1980. Pairwise comparisons, eigenvector weights, consistency ratio and the 0.10 limit.
- Lahdelma, R., Hokkanen, J., Salminen, P. "SMAA – Stochastic multiobjective acceptability analysis." *European Journal of Operational Research* 106(1), 137–143, 1998. doi:10.1016/S0377-2217(97)00163-X.
- Barron, F. H., Barrett, B. E. "Decision quality using ranked attribute weights." *Management Science* 42(11), 1515–1523, 1996. doi:10.1287/mnsc.42.11.1515. Rank-order centroid weights.
- Combustion background: Turns, S. R. *An Introduction to Combustion*, 3rd ed., McGraw-Hill, 2012, as used in `scoring/MODEL_BASIS.md`. No text or figure from it is reproduced.
- NASA PSI records PSI-25, 26, 69, 98, 99, 101 and 102 (https://psi.nasa.gov/), CC0-1.0.
