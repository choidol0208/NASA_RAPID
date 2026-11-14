# Catalog filter (the ranking)

> **How it works, in one document:** `scoring/METHOD.md` (weighting rules, validation, data preprocessing).

> AI-generated code and data: written with Claude (an AI assistant) on 2026-11-14. Catalog values are `ai_extracted`; a person still has to compare them with the originals. Scores and rankings are the team's method, not NASA's conclusion. The values of config 1.4.0 were approved by a team member: the literature-based judgements behind the weights and the pooling of the suppression weights with NASA FLEX data (`scoring/BUILDUP.md`), and the other values (`scoring/PARAMETER_REVIEW.md`).

From the environment and conditions a user gives, the filter finds the most similar PSI test configurations and picks the top 1 to 3 investigations. Code computes the scores, so the same input always gives the same result. A language model may explain a result; it never produces or changes a score.

## Files

| File | Content |
| --- | --- |
| `data/catalog/investigations.csv` | Investigation table: 24 PSI combustion investigations, one row each |
| `data/catalog/configurations.csv` | Configuration table: 41 test configurations, one row each; the unit the ranking scores |
| `data/catalog/catalog.xlsx` | A copy for people (shaded headers, column meanings, data dictionary) |
| `data/catalog/data_dictionary.csv` | Column name, meaning, allowed values, where it is used |
| `scoring/scoring_config.json` | Weight profiles, similarity scales, presets, keywords, warning texts. The dashboard reads the same file. Korean keywords are user input; `keywords._gloss_ko` gives their English |
| `scoring/scorer.py` | Reading the query, scoring, picking the top 1 to 3 (standard library only) |
| `scoring/test_scorer.py` | 56 unit tests, hand-calculated examples included |
| `scoring/ahp_judgements.json` | The 51 pairwise judgements (AHP) behind the profile weights, each with its basis |
| `scoring/derive_weights.py` | Derives the profile weights from the judgements (eigenvector, consistency ratio) and pools them with the streams in `scoring/weight_streams.json`; `--check` and `--write` |
| `scoring/derive_data_weights.py` | NASA data stream: relative importance of each condition in the FLEX measurements (LMG, bootstrap), with theory checks; writes `scoring/data_weights.json` |
| `scoring/literature_evidence.json`, `scoring/derive_literature_weights.py` | Literature stream (used in 1.4.0): evidence classes per question type with cited sources, turned into the 51 AHP judgements (`scoring/literature_judgements.csv`) and weights (`scoring/literature_weights.json`) |
| `scoring/derive_expert_weights.py`, `scoring/expert_form.csv` | Expert stream: the AHP form for team members with combustion training, and group aggregation; writes `scoring/expert_weights.json` |
| `scoring/flame_temperature.py` | Atmosphere flame temperature (oxygen consumption, NIST-JANAF enthalpies) and its check on FLEX. The JANAF tables (NIST SRD 13, copyright U.S. Secretary of Commerce) are not in the repository; the script reads a local download |
| `scoring/BUILDUP.md` | The build-up of the weighting model: what was added, the concepts and techniques, and the papers and textbooks behind them |
| `validation/scenarios.json` | 38 validation scenarios with expected results |
| `validation/run_validation.py` | Runs the scenarios, the weight stability check and the sensitivity checks; writes `validation/report.md` |
| `validation/sensitivity.py` | Each weight and each other value halved and raised by half; weighting by purpose against equal and rank-order-centroid weights; SMAA over the order of importance |
| `validation/check_catalog_sources.py` | Checks the catalog against the NASA records and tables directly; writes `validation/catalog_source_check.md` |
| `validation/build_verification_sheet.py` | Writes `validation/verification_sheet.csv`: the catalog values behind the demo rankings, with the NASA rows to check them against |
| `web/scorer.js`, `web/parity_check.py` | The JavaScript port used by the page, and the check that Python and JavaScript give the same results (99 queries) |
| `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py` | Rebuild the catalog from the PSI sources |
| `scoring/MODEL_BASIS.md` | What each scoring rule rests on, checked against a combustion textbook (Turns 2012), what stays the team's choice, and the two changes applied in config 1.1.0 |
| `scoring/PARAMETER_REVIEW.md` | AI review of every value other than the weights: role, basis, demo sensitivity, two findings, open questions |
| `scoring/METHOD.md` | **Start here.** The weighting rules, how they were validated, and the data preprocessing for the catalog, in one place |
| `scoring/WEIGHTING.md` | Weighting by purpose in depth: the technique, the AHP derivation, the NASA record sentences behind each judgement, and the checks |

## Running it

```bash
python3 -m scoring.scorer "lunar habitat cotton fabric"     # output for people
python3 -m scoring.scorer "ISS" --json                       # JSON for the dashboard
python3 -m unittest scoring.test_scorer -v                    # unit tests
python3 validation/run_validation.py                          # scenarios, stability, sensitivity -> validation/report.md
python3 web/parity_check.py                                   # Python and JavaScript agree (needs Node.js 18+)
python3 validation/check_catalog_sources.py                   # catalog against the NASA sources
python3 scripts/build_catalog.py && python3 scripts/export_catalog_xlsx.py   # rebuild the catalog
```

```python
from scoring.scorer import rank
out = rank("lunar habitat cotton fabric")                     # a rough string, or
out = rank({"preset": "iss", "fuel": "PMMA", "o2_pct": 25})   # a structured input
out["status"]          # ok | out_of_scope | need_input
out["assumptions"]     # values the user did not give, filled from a preset or a default (shown on the page)
out["warnings"]        # partial gravity, extrapolation, words not understood, ...
out["not_understood"]  # query words the scorer could not read, e.g. ["battery enclosure"]
out["results"]         # ranks 1 to 3: investigation_id, config_id, score, confidence, similarity, why, main_gap, warnings, psi_url, dataset_doi
out["ranking"]         # every investigation in order (tables, charts)
```

## What happens after the ranking

The page (ui role) shows the processed data of each ranked investigation. The join key is the result's `psi_accession` (for example PSI-69), which is `investigation_id` in `data/pipeline/tests.csv`. `tests_table_ref` in the configuration table names the PSI table file and the condition that selects the configuration's rows.

## Reading a rough query

A query is read in layers, each later one overriding the earlier: default < preset < words and numbers in the text < explicit fields.

| Input | Read as |
| --- | --- |
| `ISS` | 21% O2, 101.3 kPa, ventilated, microgravity, prevention question (each shown as an assumption) |
| `moon`, `달` (Korean: Moon) | 30% O2 and 70.3 kPa (challenge text), ventilated, partial-gravity warning |
| `Mars base` | no atmosphere values: a request for input, partial-gravity warning |
| `spacesuit` | 100% O2, 29.6 kPa (challenge text): above the highest surrounding-atmosphere O2 tested in PSI (40%), extrapolation warning |
| One word such as `fabric` or `smoke` | ranked by the material or the question alone |
| `ISS at 30% O2 and 10.2 psi` | numbers in the text override the preset |
| `battery enclosure for the ISS` | the ISS environment; `not_understood` = ["battery enclosure"] and a warning that these words change nothing |
| `spacecraft cabin` | the ISS cabin preset, only when no other environment is named |
| `a base on a planet whose atmosphere has 30% oxygen` | 30% O2 and gravity `planetary`: the partial-gravity warning, no pressure guessed |
| Empty input | no ranking; says what to enter (`need_input`) |
| `로켓 추진제` (Korean: rocket propellant) and the like | out of scope (`out_of_scope`) |

Dimensions the user did not give are left out of the score, and the remaining weights are rescaled to sum to 1. Each result's `confidence` (high, medium, low) is the share of the profile's weight that was compared with a recorded value; assumed values do not count.

## Scoring rules

`score = 100 × M × G × Σ wᵢ·Sᵢ`, where S is the similarity of each dimension, w its weight, G the gate and M the evidence factor. The formula for each dimension and its basis are in the `why` entries of `scoring_config.json`, in `scoring/MODEL_BASIS.md` and in `scoring/PARAMETER_REVIEW.md`. In short:

1. **Oxygen** is compared on the log of the ratio of mole fractions, and it falls faster above a test's maximum than below its minimum (config 1.1.0).
2. **Pressure and flow speed** are compared on a log scale. A one-sided range such as "up to 40 cm/s" scores as unknown on its open side.
3. **Gate, a ramp rather than a step:** when the fuel or the O2 similarity is below 0.2, the score is cut to between 0.5 and 1.0 of its value (0.5 at 0, 1.0 at 0.2).
4. **Unreported atmosphere:** when the record gives no O2, it is scored as ordinary air (21%). Pressure is filled as 101.3 kPa only for experiments that ran in the ISS cabin, the MSG or a Cygnus cabin. The catalog stays empty, and a result that uses the assumption carries the `fallback` warning.
5. **Unknown never beats measured:** an empty fuel or O2 value scores the smaller of 0.5 and the best real match of the query.
6. **Complementary slot:** if the user's O2 is not ordinary air (21 ± 2%) and none of the top 3 was tested at that O2, the third place goes to the best result that was, with the `complementary` warning.
7. **Ties:** scores within 3 points count as tied and are ordered by evidence quality and by whether a 1 g comparison exists.
8. **Reasons:** the reason text says "tested" only for values from an experimental table. Values from the record text, a test matrix or a team reading say so, and assumed values read "not recorded, assumed". When oxygen and pressure are both ranges, a result carries `ranges_separate`.

## Checks (2026-11-14, config 1.4.0)

- Validation scenarios 38 of 38 pass.
- Unit tests 56 of 56 pass.
- AHP consistency ratio of the literature judgements 0, 0.009 and 0.008 (limit 0.10); the config holds exactly the derived weights.
- Python and JavaScript give the same results on 99 of 99 queries.
- Each weight of each profile halved and raised by half: 146 of 152 variants keep the same top 3, and rank 1 changes in 1.
- SMAA with only the order of importance: rank 1 holds in every draw for 8 of 12 queries; `lunar habitat cotton fabric` has no clear winner.
- Each other value halved and raised by half: 129 of 136 runs keep the same top 3. The `ISS` and `lunar habitat` presets never change.
- Against the NASA sources: 107 ranking values written in the source and 8 team readings; 24 of 24 range ends match; 135 of 135 numbers in the shown text are written in the source.

The expected answers were written by an AI session for the team; their review by combustion researchers is the next step. Details are in `validation/report.md` and `validation/catalog_source_check.md`.
