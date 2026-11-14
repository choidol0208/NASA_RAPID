# Relation cards and range gate (experiment, branch `data-lab`)

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon, 2026-11-14. This is an experiment on the branch `data-lab`. It is not merged into the pipeline, and no person or combustion specialist has reviewed it. The code, the card texts and the criteria were written by an AI coding assistant.*

The idea it tries: fire-safety information is judged by published mathematical or physical relations, not by a language model. The tool shows, for a condition, which relation our reference documents hold, what range the documents state for it, and what the recorded NASA data can and cannot check. It builds variants A (consistency cards) and B (range gate with per-phase counts) of the decision brief. It has no page and no number guard (variant C).

## Files

| File | What |
|---|---|
| `pipeline/spec/relation_cards.json` | The cards: one per published relation or value set held in `references.json`, with item ids, statement, validity per axis, needed columns, check and criterion, caption. Also the status list, the gate rule and every sentence template |
| `pipeline/lab/cardlib.py` | Shared code: loading, the verbatim checks, the forbidden-word scan, range arithmetic, JSON output |
| `pipeline/lab/run_cards.py` | Runs each card's check; writes `data/pipeline/cards/card_results.json` |
| `pipeline/lab/range_gate.py` | Compares each scenario of `scenarios.json` with each card; writes `data/pipeline/cards/gate_<scenario_id>.json` |

Run (needs `data/pipeline/tests.csv` and `data/pipeline/coverage_grid.csv`, which `pipeline/run.py` writes):

```
python3 pipeline/lab/run_cards.py
python3 pipeline/lab/range_gate.py
```

Python standard library and pandas only. The same input gives the same bytes: no timestamps, fixed order.

## What a card is

Each card names its reference items (`source_items`) and copies from them:

- `statement`: the relation or value set, verbatim from the item's `quote`, or from its `text` (the team's wording of the document in `references.json`; marked `field: text`).
- `validity`: gravity, pressure, oxygen, flow, material, criterion, geometry. Each axis holds the verbatim words with the item and field, and a normalized value (a range, single values, a list of levels or names), or the string `unstated`. Words from an item's `note` are never used; where a note names a condition, it is shown under `not_used` with the reason. An oxygen number that is a limit (LOI, MOC, a boundary minimum) is a result, not an atmosphere, and is not oxygen validity.
- `needs`: the columns of `tests.csv` the relation would need.
- `check`: what is compared with what, and the criterion, written in the spec before the outputs.
- `caption`: what the result means and what it does not mean.

The scripts stop if a word string is not verbatim in its item, if a normalized pressure is not the as-written number times the fixed unit factor (1 psia = 6.894757 kPa, 1 atm = 101.325 kPa), if a gravity level has no word of the vocabulary of `spec/findings.json`, or if a card marked `in_our_references: false` finds its own words in any item.

## Statuses (`card_results.json`)

| Status | Meaning |
|---|---|
| `columns_consistent_with_form` | The recorded columns of `tests.csv` agree with each other as the card's form or range says, by the card's criterion. This is not an independent test of a physical law |
| `inconsistent` | The recorded columns do not meet the card's criterion |
| `not_testable_here` | `tests.csv` or the item's values hold nothing the check could compare; recorded facts may be listed beside it |
| `matches_published_table` | Team arithmetic on the item's values agrees with what the same document prints |
| `differs_from_published_table` | It does not |
| `not_in_our_references` | No document of `references.json` states the relation. The card carries this badge whatever its check gives; the check result is in `check_outcome` |

Every number in the outputs is a NASA cell of `tests.csv`, a value of a reference item, or arithmetic that the card names; arithmetic carries `computation_label` ("team computation", "team arithmetic"). Criterion parameters (shares, bands) are team choices. The criteria were written after the scouts of the decision brief had computed the main numbers and after a first placebo run; they are fixed in the spec but this is not a pre-registration.

## Gate (`gate_<scenario_id>.json`)

For each scenario and each card, four axes are compared: oxygen, pressure, gravity, flow. Material, criterion and geometry are shown with the card and not compared, because no scenario states them.

| Axis value | Meaning |
|---|---|
| `inside` | The scenario's whole range (or its gravity level) lies inside what the card states |
| `outside` | It does not; `overlap` is `partial` or `none`, and the card's verbatim words are given |
| `card_unstated` | The card's items state nothing on this axis |
| `scenario_unstated` | The scenario sets nothing on this axis |

A card that states single values (one pressure, "1 atmosphere") contains no scenario range, because every scenario sets a range. Overall: `not_applicable` for a card not in our references; else `outside_stated_range` if any axis is outside; else `not_applicable` if gravity is not `inside`; else `may_be_quoted_here`. If no card may be quoted, the headline is "No held relation covers this condition", a result of its own.

Each gate file also lists, per fuel phase, the recorded tests of the scenario's cells of the coverage grid (copied from `coverage_grid.csv`, ambient oxygen), the tests in the scenario's oxygen bins with no recorded pressure, and how many rows of the phase have a recorded pressure. There is no distance score, no hull and no nearest neighbour.

## Limits

- A consistency check between recorded columns is not validation of a law. In the d-squared card the burning rate K is a reported value of the same experiment, and no document we hold states the d-squared form. The placebo (K reversed in order within each fuel) shows how much of the agreement depends on each test's own K.
- In range means only that the relation may be quoted for the condition. It does not mean that the condition is acceptable, and the gate gives no verdict on any condition.
- An axis the card does not state does not block a card. A card can therefore be "may be quoted" while stating only its gravity level (the CO/CO2 card for the ISS cabin; the OF2012 card for the Mars habitat, which sets no atmosphere). The sentence names the unstated axes; read them.
- The containment rule is strict. The ISS cabin oxygen range is the team's bin up to 23 %, so the BASS-II boundary (13 to 22 %) is outside it; a different bin would change the result.
- Material names must match exactly. Nomex III (BASS-II) is not Nomex HT90-40 (OF2012); PSI "silicone" is not Hirsch's "Silicone". The gate does not substitute names; no scenario names a material, so materials are shown and not compared.
- No fitted boundary, no LOI estimate, no interpolation, no extrapolation, no prediction for any scenario. The FLEX card shows the lowest oxygen recorded beside the published LOI; the lowest oxygen tested is not an LOI. FLEX.mec is not applied.
- The validity of a card is what its own items state. Conditions stated by another item of the same paper (for example "Pressure was not varied from 1 atmosphere" next to the CO/CO2 range) are shown under `not_used` and not attached.
- The cards, their words and the criteria are an AI reading of `references.json`; items read as abstract only (MST14.loi) or as a summary of an unread paper (H2011.linear) keep that access level in `references.json`.

# Inference map (experiment, branch `data-lab`)

*AI-generated (Claude Code) on 2026-11-14. Not reviewed by a person or by a combustion specialist.*

The idea it tries: not a model that computes an answer, but the procedure by which a question about a new environment is carried from doubt to result. For one question, "what would have to be established before a material-flammability criterion could be set for a lunar habitat (oxygen 30% or more, pressure 10.2 psi or less, lunar gravity)?", the map lays out the claims the held documents state, and for each one what the held items and PSI tests already show.

| File | What |
|---|---|
| `pipeline/spec/inference_map.json` | The walked path, the environment, the root claim and the links, every text as a copy of a reference item or a PSI record field; the state rule; the year of each document |
| `pipeline/lab/inference_map.py` | Checks the spec, counts the PSI tests, assigns the states, writes the two outputs |
| `data/pipeline/lab/inference_map_lunar_habitat.json` | The map with the documents, conditions, counts and states filled in |
| `data/pipeline/lab/inference_map_lunar_habitat.md` | Plain-text rendering: the walked path, a tree with one line per link, then the quotes of each link |

Run: `python3 pipeline/lab/inference_map.py` (reads `data/pipeline/findings.csv`, `need_tests.csv`, `tests.csv` and `answers/lunar_habitat__<need>.json`, which `pipeline/run.py` writes). Standard library only; the same input gives the same bytes.

## What it holds

- **Walked path.** How the question "is the normal-gravity screening test conservative in microgravity?" went from doubt to result in the held documents: existing criterion, doubt stated, hypothesis (PSI-25 record), test designed to discriminate, result, scale-up designed, scale-up result, fed back to the criterion, criterion revised, still open. Two steps are "no item held": no held item states a Saffire-II low-gravity limit, and none states a change of Test 1 made on the basis of the results. The steps follow the procedure, not the years.
- **Map.** A root claim (`TB008.assess`) and links. Each link has a claim (a NASA question or requirement), `why_needed` (the item that makes it a precondition of a criterion), the conditions it requires (oxygen, pressure, gravity, flow; the team's choice, with the basis written), the evidence items, the PSI needs whose counted tests are compared, items that state it open, `what_would_close_it` (only quoted research needs or planned work) and `verification` (only quoted statements about what limits or supports such a result). A field with no supporting item is "no item held".
- **State.** Assigned by code by the rule in `_meta.state_rule`: `established` if one result item (its conditions as tagged in `findings.csv`) or one counted PSI test is inside the environment on every required condition of the link; `partly` if items or tests are held but none is; `missing` if none is held. L1 (the atmosphere) is a specification link and is established only by an item of type requirement. The environment bounds are read from `CH.moonbase` (30% oxygen, 10.2 psia converted with the factor of `relation_cards.json`) and the gravity level from `scenarios.json`.

## What it is and is not

- It is a map of what the held documents say must be known and of what is known in the held items and PSI tests. It is not a criterion, not a flammability limit, not a research plan of the team, and not advice on any material or atmosphere.
- The choice of links, their parents and their required conditions is the team's (AI) reading. The documents do not arrange their questions as a tree; another reading would give another tree.
- The state of a link is the team's reading of the items by a mechanical rule. It counts presence, not strength: one 5 s drop-tower paper on three materials (`OF2012.table1`) is enough to make L2 `established`, and its caveat is shown beside it under verification. `established` does not mean that NASA considers the question closed.
- Quotes marked "team wording" are the `text` field of an item (the team's wording of the document in `references.json`), not the sentence as printed. Items read as abstract only or by another session keep that access mark.
- The documents are from 2003 to 2024 (plus the 2026 challenge page). They do not say what NASA considers open today, and documents not in `references.json` were not read.

# Structured argument (experiment, branch `data-lab`)

*AI-generated (Claude Code) on 2026-11-14. Not reviewed by a person or by a combustion specialist.*

The inference map shows what the documents ask and what is held. It cannot show reasoning. This step writes the lunar-habitat material-flammability case as a structured argument in the claim–argument–evidence form of assurance cases (the Goal Structuring Notation elements goal, strategy, solution, assumption and undeveloped entity; warrants and assumptions in the text form of NASA/TM-2017-219650; sources in `_meta.method_sources` of the spec). The team's reasoning is written out and labelled so that it can be attacked. The top claim is about evidence, not about any material or atmosphere: *a ranking of materials by flammability obtained in normal-gravity ground tests can be carried over, in the same order, to the lunar-habitat atmosphere and to lunar gravity.*

| File | What |
|---|---|
| `pipeline/spec/argument_lunar_habitat.json` | The nodes |
| `pipeline/lab/argument.py` | Checks the spec, copies the evidence, writes the outputs |
| `data/pipeline/lab/argument_lunar_habitat.json` / `.md` | The argument with every item and count filled in, and a summary of counts |

Run: `python3 pipeline/lab/argument.py` (reads `references.json` and `data/pipeline/evidence/scenario_lunar_habitat.json`). Standard library only; same input, same bytes.

## Node kinds

| Kind | What it holds |
|---|---|
| `claim` | A sentence that can be true or false, with `children` (claims, evidence, undeveloped claims) and one `inference`. No numbers |
| `inference` | Why the children would support the claim: `text`, `assumptions`, `authorship` ("team reasoning (AI-drafted), not a NASA statement"), `basis` (`documented` with the item that states the step, or `team`), `defeaters`. Each assumption is an object: `text`, and `added_by` ("review pass") when a later review added it |
| `evidence` | Only a reference item id (text, quote, where, url and access are copied) or a count pointer (file + path; the number is copied). `covers` records materials, gravity, facility, oxygen, pressure and flow as verbatim words of the item, or "not stated in the item" |
| `defeater` | A way an inference, or one of its numbered assumptions, could fail: `basis` `documented` (item id) or `logical`. Optional: `item_words` (the words of the item that carry the doubt, verbatim from its text, quote or where; required for a documented defeater of the review pass), `cites` (pointers into the item's `values` or into a data file; the values are copied into the output, so the sentence holds no hand-typed number), `added_by` ("review pass") |
| `undeveloped` | A claim with no evidence held, with the items that ask for the study, or "no item held" |

## The script stops if

- a node kind is unknown, an id is duplicated or missing, a node has two parents or cannot be reached from the top claim;
- an evidence node names an unknown item, carries any field of its own besides `covers`, or a count pointer does not resolve to a number;
- a `covers` entry is not verbatim in the item field it names;
- an inference (text or assumptions) contains a numeric token that is not in an evidence child of its claim; a documented defeater contains a number that is not in its item; a logical defeater, a claim or an undeveloped claim contains any number (item ids, node ids and the listed identifiers such as "Test 1" are removed first);
- a `documented` basis has no item id or an unknown one;
- an assumption is not an object with `text`; a defeater's `item_words` are not verbatim in its item, or one of its `cites` does not resolve;
- a claim has no children (it must be written as `undeveloped`), or has children but no inference;
- a word of `_meta.forbidden_words` (safe, acceptable, sufficient, representative, ...) appears in a team-written string.

The summary counts claims, undeveloped claims, evidence leaves, inferences by basis, assumptions, defeaters by basis and the access levels of the evidence, and, per inference, the assumptions, the defeaters by basis, those added by the review pass, and the assumptions with no recorded defeater. An assumption with no recorded defeater has not been shown to hold. It computes no verdict, and none should be read into the counts.

## Limits

- Seven of the eight inferences have basis `team`: no held document states the step. These are the weakest joints, and their assumptions are listed so that they can be attacked.
- The split of the top claim (atmosphere, pressure, gravity with flow, combination) is the team's. Temperature, thickness, sample size and the ignition source are not developed; defeaters D0a to D0d say so.
- A defeater with basis `documented` cites an item that supports the doubt; its sentence is still the team's wording. The defeater list is open.
- Review pass (2026-11-14, AI): reviewer sessions (model output) proposed defeaters, missing assumptions and evidence misuse per inference; one editing session checked each against `references.json` and added those it could verify, marked `added_by: "review pass"`. Evidence leaves were kept; where an item is used beyond its own words, a defeater on the inference says so. Fact checks of held values added defeaters on I3 (`H2006.table2`: the order of some materials changes between pressure columns) and I4 (`OF2012.table1`: a strict normal-gravity order by MOC becomes a tie at lunar gravity), and one on I2 naming the two definitions of the lunar habitat (`CH.moonbase` and the scenario in `pipeline/spec/scenarios.json`, which is unchanged). The review is AI work, not a review by a person or a combustion specialist, and the added assumptions have no defeater recorded yet.
- `covers` copies only what the item states. "not stated in the item" may mean that the paper states it elsewhere; the item was not re-read for this step.
- The defeater kind is not defined in the three method sources that could be read; it is described in the team's own words.
- The argument shows where the case rests on documents, on team reasoning, or on nothing held. It does not say whether the top claim is true, and it is not a criterion or a judgement on any material.

# Lab numbers: envelope position and order changes (experiment, branch `data-lab`)

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon, 2026-11-14. Not human-reviewed. Experiment on the branch `data-lab`, not merged into the pipeline.*

Numbers that follow from the data by arithmetic alone: no model, no fitted relation, no weight, no interpolation, no probability, and no sentence written by a language model at run time. Every number is a value copied from `data/pipeline/tests.csv` or from a reference item's `values`, or a count, minimum, maximum, difference or the stated rank statistic (Kendall tau-b) of such values. Every choice is a parameter of `pipeline/spec/lab_numbers.json`, and every output copies the choices it used under `choices`. All sentences of the outputs are fixed sentences of that spec.

## Files

| File | What |
|---|---|
| `pipeline/spec/lab_numbers.json` | Parameters (choices), fixed sentences, tables to read, items looked at and rejected, forbidden words, the README lists below |
| `pipeline/lab/numlib.py` | Exact decimal reading and writing (fractions), forbidden-word scan, deterministic output |
| `pipeline/lab/envelope.py` | Envelope position per scenario and need; writes `data/pipeline/lab/numbers/envelope_<scenario_id>.json` and `.md` |
| `pipeline/lab/order_changes.py` | Order changes per held table; writes `data/pipeline/lab/numbers/order_<table_id>.json` and `.md` |
| `pipeline/lab/run_numbers.py` | Runs both and writes `data/pipeline/lab/numbers/index.json` |

Run (after `python3 pipeline/run.py`): `python3 pipeline/lab/run_numbers.py`. Python standard library; the range rule is imported from `pipeline/run.py` (`in_range`), which loads pandas. The same input gives the same bytes (sorted keys, fixed order, no timestamps; checked by two runs, one with a different `PYTHONHASHSEED`).

The script stops if: the joint range count of a scenario and need differs from `tests_atmosphere` of `scenario_needs.csv`; the float reading of the pipeline and the exact decimal reading put a different set of tests inside the ranges; a test of `need_tests.csv` is missing from `tests.csv`; the counted value of `objective_link` is not among the values of the column; a reference item with `values` is neither a table of the spec nor listed as rejected; a table has fewer than 3 materials or 2 columns; a forbidden word (safe, acceptable, sufficient, representative, proven) appears in an output.

## What each number is

- `counted_tests`: Number of tests of need_tests.csv with objective_link 'stated' for the need.
- `counted_tests_with_ambient_oxygen`: Of those, the tests with o2_pct recorded and o2_basis 'ambient'.
- `axes.tests_recorded`: Of the tests with ambient oxygen, the number with the axis (o2_pct or pressure_kpa) recorded.
- `axes.min, axes.max`: Smallest and largest recorded value of the axis over those tests.
- `axes.nominal_within_min_max`: Whether min <= nominal value <= max.
- `axes.nearest`: The recorded value(s) closest to the nominal value on that axis alone, the gap (value minus nominal) and the number of tests at that value.
- `joint.tests_with_both_recorded, joint.distinct_points`: Tests with ambient oxygen and pressure both recorded, and the number of distinct (o2_pct, pressure_kpa) points among them.
- `joint.hull_kind, joint.hull_vertices_ccw`: Convex hull of those points: 'area', 'segment', 'point' or 'none', with its vertices counter-clockwise.
- `joint.nominal_position, joint.nominal_inside_hull`: 'interior', 'boundary' or 'outside' of the nominal point relative to the hull; boundary counts as inside.
- `joint.nearest_tests_pareto`: Tests not dominated in (|delta o2_pct|, |delta pressure_kpa|), each with both deltas and its source file and row.
- `gravity.*`: Number of tests whose gravity_level equals the scenario's, and where gravity_level in tests.csv comes from.
- `ranges.*`: Number of tests inside the scenario's oxygen range, inside its pressure range, and inside both; the last equals tests_atmosphere of scenario_needs.csv (checked).
- `order.counts`: For one table, one quantity and one pair of condition columns: the number of material pairs in each class (same_order, reversed, tie_in_one, tie_in_both).
- `order.kendall_tau_b`: Kendall tau-b of the two columns over all material pairs, as numerator, integer under the square root and rounded decimal.
- `order.reversed_and_tie_in_one_pairs`: Every material pair that is reversed or tied in one column only, with the four printed values.

## Choices made (each a parameter of `lab_numbers.json`)

- `envelope.choices.counted_tests`: need_tests.csv rows with objective_link equal to 'stated'
- `envelope.choices.ambient_oxygen`: o2_pct recorded and o2_basis equal to 'ambient' (the rule of match_environments in pipeline/run.py: any other basis is marked not_ambient)
- `envelope.choices.axes`: ['o2_pct', 'pressure_kpa']
- `envelope.choices.number_reading`: every cell and every spec number is read as the exact decimal it is written as (Python fractions.Fraction of the written string); differences are exact
- `envelope.choices.gap_sign`: gap = nearest recorded value minus nominal value; positive means the nearest recorded value is above the nominal value; 0 means a test has exactly the nominal value; where two recorded values are equally near (one above, one below), both are listed
- `envelope.choices.hull`: convex hull of the distinct recorded (o2_pct, pressure_kpa) points, monotone chain, exact rational arithmetic, no tolerance
- `envelope.choices.hull_boundary`: a point on an edge or a vertex of the hull is reported as position 'boundary' and counted as inside
- `envelope.choices.degenerate_hull`: fewer than 3 non-collinear distinct points: hull kind 'point' or 'segment', reported as 'no area'; inside is true only where the nominal point coincides with the point or lies on the segment
- `envelope.choices.pareto`: a test is listed when no other test of the set has |delta o2_pct| <= its |delta o2_pct| and |delta pressure_kpa| <= its |delta pressure_kpa| with at least one of the two strictly smaller; deltas = test value minus nominal value; no combined distance, no weight, no scaling; tests with identical deltas are all listed
- `envelope.choices.gravity`: count of tests whose gravity_level string equals the scenario's gravity_level string; a scenario with gravity_level null sets none
- `envelope.choices.ranges`: the in_range rule of pipeline/run.py (RANGE_DEFAULTS: min inclusive, max exclusive unless stated) applied to the scenario's ranges; a range the scenario does not set is reported as not set; the joint count requires oxygen and pressure both inside and is asserted equal to tests_atmosphere of scenario_needs.csv
- `envelope.choices.scenarios_without_nominal`: a scenario whose nominal is empty gets no nominal-point numbers; its ranges are reported where set
- `order_changes.choices.values`: values are read as printed in the reference item's 'values' (exact decimals; JSON numbers read as decimal strings), no tolerance
- `order_changes.choices.classes`: for materials a, b and condition columns c1, c2: s1 = sign(a[c1] - b[c1]), s2 = sign(a[c2] - b[c2]); same_order if s1 = s2 != 0; reversed if s1 = -s2 != 0; tie_in_one if exactly one of s1, s2 is 0; tie_in_both if both are 0
- `order_changes.choices.kendall_tau_b`: tau_b = (n_c - n_d) / sqrt((n_0 - n_1)(n_0 - n_2)), n_0 = n(n-1)/2 material pairs, n_c = same_order pairs, n_d = reversed pairs, n_1 = pairs tied in c1 (tie_in_both included), n_2 = pairs tied in c2; given exactly as numerator and the integer under the square root, and as a decimal rounded half-even to 'tau_b_digits' digits; undefined where the square root is 0
- `order_changes.choices.tau_b_digits`: 6
- `order_changes.choices.column_pairs`: every unordered pair of condition columns, in the column order of the spec
- `order_changes.choices.material_pairs`: every unordered pair of materials, in the row order of the item

Tables read: `H2006.table2`, `OF2012.table1`. Every other reference item with `values` (53 items) is listed in the spec under `order_changes.search.rejected` with its reason and copied into `index.json`.

Fixed sentences shown with the envelope numbers:

- Inside the hull of tested conditions means only that tests exist on several sides of this point; it says nothing about the outcome at this point.
- Outside means no arithmetic on these tests reaches this point.

## What these numbers cannot say

- Whether a material burns, or how, at a scenario's nominal point: no outcome variable is read by the envelope numbers.
- Anything about a point inside the hull beyond the existence of tests on several sides of it: no value is interpolated.
- Anything about gravity levels other than the ones in tests.csv: every test there carries a gravity level that the team's source mapping sets as a constant per table.
- Which of two materials is more flammable in a scenario: the order tables are normal-gravity or drop-tower results printed by the authors, at the printed conditions only.
- Whether a difference of one printed unit is a real difference: the items state no measurement uncertainty or step size.
- Whether the counted tests are the right tests for a need: that is the pipeline's linking rule (needs.json, stated_by), not arithmetic.
