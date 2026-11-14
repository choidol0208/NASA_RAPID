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
| `pipeline/lab/model_map.json` | The model map: every decision point of the pipeline and the lab, its class and the model that governs it (see "Model map" below) |
| `pipeline/lab/model_map_md.py` | Recounts and checks the map and writes `pipeline/lab/model_map.md` from the JSON |
| `pipeline/lab/governance.py` | Builds the `governed_by` block that every lab output carries, from the map |

Run (needs `data/pipeline/tests.csv` and `data/pipeline/coverage_grid.csv`, which `pipeline/run.py` writes):

```
python3 pipeline/lab/model_map_md.py
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
| `described_without_criterion` | A team computation over recorded columns is described (count, minimum, quartiles, median, maximum); no criterion is applied and no agreement status is given (the d-squared card) |

Every number in the outputs is a NASA cell of `tests.csv`, a value of a reference item, or arithmetic that the card names; arithmetic carries `computation_label` ("team computation", "team arithmetic"). Criterion parameters (shares, bands) are team choices. The criteria were written after the scouts of the decision brief had computed the main numbers and after a first placebo run; they are fixed in the spec but this is not a pre-registration.

## Gate (`gate_<scenario_id>.json`)

For each scenario and each card, four axes are compared: oxygen, pressure, gravity, flow. Material, criterion and geometry are shown with the card and not compared, because no scenario states them.

| Axis value | Meaning |
|---|---|
| `inside` | The scenario's whole range (or its gravity level) lies inside what the card states |
| `outside` | It does not; `overlap` is `partial` or `none`, and the card's verbatim words are given |
| `domain_not_defined` | The scenario sets a range or a level on this axis and the card's items state no comparable domain there |
| `card_unstated` | Neither the card nor the scenario states anything on this axis |
| `scenario_unstated` | The scenario sets nothing on this axis |

A card that states single values (one pressure, "1 atmosphere") contains no scenario range, because every scenario sets a range. Overall: `not_applicable` for a card not in our references; else `outside_stated_range` if any axis is outside; else `domain_not_defined` if any axis is `domain_not_defined`; else `not_applicable` if gravity is not `inside`; else `may_be_quoted_here`. The `domain_not_defined` step follows OECD Principle 3 as cited in the model map (ENV/JM/MONO(2007)2 para 92: "it is important to know whether its AD is known, and whether it is being used inside or outside of this boundary"); applying it to the stated validity of a published relation, and the order of the list, are team rules. If no card may be quoted, the headline is "No held relation covers this condition", a result of its own.

Each gate file also lists, per fuel phase, the recorded tests of the scenario's cells of the coverage grid (copied from `coverage_grid.csv`, ambient oxygen), the tests in the scenario's oxygen bins with no recorded pressure, and how many rows of the phase have a recorded pressure. There is no distance score, no hull and no nearest neighbour.

## Limits

- The d-squared card describes a team ratio over recorded FLEX columns and gives no agreement status. Its earlier criterion, bands and reversal placebo were removed on 2026-11-14: they were chosen after the numbers were seen and no held or opened source defines them. The held K is defined by NASA/TP-2015-216046 (Appendix) as a fit "from shortly after ignition to extinction"; that sentence is not yet an item of `references.json`, so the card stays `not_in_our_references`.
- The Hirsch 2011 card applies the linear form only to materials whose every held MOC lies in the range 25-35 % the paper states (both ends included is the lab's reading). All eleven `H2006.table2` materials are refused; only the paper's own unnamed example pair is inside.
- In range means only that the relation may be quoted for the condition. It is not a judgement of the condition, and the gate gives no verdict on any condition.
- An axis the card does not state blocks the card when the scenario sets that axis (`domain_not_defined`). Since 2026-11-14 the CO/CO2 card is no longer "may be quoted" for the ISS cabin (it states only its gravity level). The OF2012 card is still "may be quoted" for the Mars habitat, because that scenario sets no atmosphere; the sentence names the axes neither side states.
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

Numbers that follow from the data by arithmetic and the two established models named in the model map (convex hull, OECD ENV/JM/MONO(2007)2 para 110; Kendall tau-b, NIST Dataplot): no fitted relation, no weight, no interpolation, no probability, and no sentence written by a language model at run time. Next to every number the outputs name the decision point of `pipeline/lab/model_map.json` and its governing model key, or "team rule". Every number is a standardized value of `data/pipeline/tests.csv` or a value of a reference item's `values`, or a count, minimum, maximum, difference or the stated rank statistic (Kendall tau-b) of such values. The standardized values are themselves the pipeline's arithmetic: where a source column has another unit, `pipeline/rules.py` (rule `number`) multiplied the cell by the unit factor of `pipeline/spec/sources.json` (for example mmHg x 0.133322368, mole fraction x 100) and rounded the product to 4 decimals; every envelope output lists the factors used under `conversions`. Every choice is a parameter of `pipeline/spec/lab_numbers.json`, and every output copies the choices it used under `choices`. The outputs contain only fixed sentences of that spec and fixed templates of the two scripts (table headers, labels such as 'Nominal point: interior, inside = true', filled with the computed numbers); no text is composed at run time beyond filling those templates.

## Files

| File | What |
|---|---|
| `pipeline/spec/lab_numbers.json` | Parameters (choices), fixed sentences, tables to read, items looked at and rejected, forbidden words, the README lists below |
| `pipeline/lab/numlib.py` | Exact decimal reading and writing (fractions), forbidden-word scan, deterministic output |
| `pipeline/lab/envelope.py` | Envelope position per scenario and need; writes `data/pipeline/lab/numbers/envelope_<scenario_id>.json` and `.md` |
| `pipeline/lab/order_changes.py` | Order changes per held table; writes `data/pipeline/lab/numbers/order_<table_id>.json` and `.md` |
| `pipeline/lab/run_numbers.py` | Runs both and writes `data/pipeline/lab/numbers/index.json` |

Run (after `python3 pipeline/run.py`): `python3 pipeline/lab/run_numbers.py`. Python standard library; the range rule is imported from `pipeline/run.py` (`in_range`), which loads pandas. The same input gives the same bytes (sorted keys, fixed order, no timestamps; checked by two runs, one with a different `PYTHONHASHSEED`).

The script stops if: the joint range count of a scenario and need differs from `tests_atmosphere` of `scenario_needs.csv`; the float reading of the pipeline and the exact decimal reading put a different set of tests inside the ranges; a test of `need_tests.csv` is missing from `tests.csv`; the counted value of `objective_link` is not among the values of the column; a reference item with `values` is neither a table of the spec nor listed as rejected; a table has fewer than 3 materials or 2 columns; a sentence of the spec attributed to an item's note is not verbatim in that note; a value filled by the pipeline's rule `number` has more than 4 decimals; a forbidden word (safe, acceptable, sufficient, representative, proven) appears in an output.

## What each number is

- `counted_tests`: Number of tests of need_tests.csv with objective_link 'stated' for the need.
- `counted_tests_with_ambient_oxygen`: Of those, the tests with o2_pct recorded and o2_basis 'ambient'.
- `axes.tests_recorded`: Of the tests with ambient oxygen, the number with the axis (o2_pct or pressure_kpa) recorded.
- `axes.min, axes.max`: Smallest and largest recorded value of the axis over those tests.
- `axes.nominal_within_min_max`: Whether min <= nominal value <= max.
- `axes.nearest`: The recorded value(s) closest to the nominal value on that axis alone, the gap (value minus nominal) and the number of tests at that value.
- `joint.tests_with_both_recorded, joint.distinct_points`: Tests with ambient oxygen and pressure both recorded, and the number of distinct (o2_pct, pressure_kpa) points among them.
- `joint.hull_kind, joint.hull_vertices_ccw`: Convex hull of those points: 'area', 'segment', 'point' or 'none', with its vertices counter-clockwise.
- `joint.nominal_position, joint.nominal_inside_hull`: 'interior', 'boundary', 'outside' or 'no hull' of the nominal point relative to the hull; boundary counts as inside; inside is null where there is no hull.
- `joint.nearest_tests_pareto`: Tests not dominated in (|delta o2_pct|, |delta pressure_kpa|), each with both deltas and its source file and row.
- `gravity.*`: Number of tests whose gravity_level equals the scenario's, and where gravity_level in tests.csv comes from.
- `ranges.*`: Number of tests inside the scenario's oxygen range, inside its pressure range, and inside both; the last equals tests_atmosphere of scenario_needs.csv (checked).
- `order.counts`: For one table, one quantity and one pair of condition columns: the number of material pairs in each class (concordant, discordant, tied_first_column_only, tied_second_column_only, tied_both_columns; terms of the NIST Dataplot KENDALLS TAU page, the last is the remaining class).
- `order.kendall_tau_b`: Kendall tau-b of the two columns over all material pairs as defined on the NIST Dataplot KENDALLS TAU page, as numerator, integer under the square root and rounded decimal.
- `order.discordant_and_tied_one_column_pairs`: Every material pair that is discordant or tied in one column only, with the four printed values.
- `excluded_o2_not_recorded, excluded_basis_not_ambient`: Counted tests left out because o2_pct is empty, and because o2_basis is not 'ambient'.
- `axes.flagged_tests`: Counted tests with a flag on the axis in tests.csv, with the flags and o2_range_as_written; min, max and nearest carry flagged_tests_at_value.
- `axes.nearest.below_nominal_rounding`: Whether |gap| is smaller than half a unit of the last digit written for the nominal value.
- `joint.composition`: Number of pooled tests per investigation_id, fuel_phase and sample_geometry.
- `joint.rounding_box_corners_inside`: Of the 4 corners nominal +- h (h = half a unit of the last written digit, per axis), the number inside the hull.
- `conversions`: Per axis and source of the counted tests: the source column, the pipeline rule and its parameters (unit factor) from sources.json.
- `order.counts_held_differs`: The same class counts restricted to material pairs whose held condition (test pressure) differs.
- `order.same_criterion`: Whether the two condition columns carry the same criterion (spec).
- `governed_by`: Every output carries a 'governed_by' block: per decision point of pipeline/lab/model_map.json, the governing model key, source title, URL and opened_by, or 'team rule, no established model found'. Envelope and order fields carry the short label (point: model key or 'team rule') next to the number.

## Choices made (each a parameter of `lab_numbers.json`)

- `envelope.choices.counted_tests`: need_tests.csv rows with objective_link equal to 'stated'
- `envelope.choices.ambient_oxygen`: o2_pct recorded and o2_basis equal to 'ambient' (the rule of match_environments in pipeline/run.py: any other basis is marked not_ambient); the numbers of counted tests left out because o2_pct is empty and because o2_basis is not 'ambient' are reported per need (excluded_o2_not_recorded, excluded_basis_not_ambient)
- `envelope.choices.axes`: ['o2_pct', 'pressure_kpa']
- `envelope.choices.number_reading`: every cell and every spec number is read as the exact decimal it is written as (Python fractions.Fraction of the written string); differences are exact. The cells are the pipeline's standardized values: where a source column has another unit, the pipeline multiplied the cell by a unit factor of pipeline/spec/sources.json and rounded the product to 4 decimals (rule 'number' of pipeline/rules.py); the factor of every source column used is copied under 'conversions'. The nominal values are read as written in scenarios.json and are themselves rounded figures: see 'nominal_rounding'
- `envelope.choices.gap_sign`: gap = nearest recorded value minus nominal value; positive means the nearest recorded value is above the nominal value; 0 means a test has exactly the nominal value; where two recorded values are equally near (one above, one below), both are listed
- `envelope.choices.hull`: convex hull of the distinct recorded (o2_pct, pressure_kpa) points, monotone chain, exact rational arithmetic, no tolerance
- `envelope.choices.hull_boundary`: a point on an edge or a vertex of the hull is reported as position 'boundary' and counted as inside
- `envelope.choices.degenerate_hull`: fewer than 3 non-collinear distinct points: hull kind 'point' or 'segment', reported as 'no area'; inside is true only where the nominal point coincides with the point or lies on the segment
- `envelope.choices.pareto`: a test is listed when no other test of the set has |delta o2_pct| <= its |delta o2_pct| and |delta pressure_kpa| <= its |delta pressure_kpa| with at least one of the two strictly smaller; deltas = test value minus nominal value; no combined distance, no weight, no scaling; tests with identical deltas are all listed; dominance is decided per axis, so a change of unit on either axis does not change the set
- `envelope.choices.gravity`: count of tests whose gravity_level string equals the scenario's gravity_level string; a scenario with gravity_level null sets none; where gravity_level of every test used is a table constant of the team's source mapping, the count equals the number of tests of tables mapped to that level and carries no information beyond that mapping
- `envelope.choices.ranges`: the in_range rule of pipeline/run.py (RANGE_DEFAULTS: min inclusive, max exclusive unless stated) applied to the scenario's ranges; a range the scenario does not set is reported as not set; the joint count requires oxygen and pressure both inside and is asserted equal to tests_atmosphere of scenario_needs.csv
- `envelope.choices.scenarios_without_nominal`: a scenario whose nominal is empty gets no nominal-point numbers; its ranges are reported where set
- `envelope.choices.flagged_values`: a value whose test carries a flag on that axis in the 'flags' column of tests.csv (for example o2_pct:approximate_in_source, o2_pct:range_in_source_start_value_named_in_publication) is used as the number held in tests.csv, like every other value, and is not left out; per need and axis, every counted test with such a flag is listed with its flags and o2_range_as_written, and min, max, nearest and each Pareto test give the number of flagged tests at that value
- `envelope.choices.nominal_rounding`: h = half a unit of the last digit written for the nominal value in scenarios.json (70.3 gives 0.05; 21.0 gives 0.05); a gap or Pareto delta with absolute value below h is marked below_nominal_rounding; the 4 corners (nominal +- h on each axis) are placed relative to the hull like the nominal point and the number inside is reported, so a reader sees whether the position changes within the written rounding of the nominal
- `envelope.choices.pooling`: the hull and the Pareto set pool every counted test with ambient oxygen and pressure both recorded, whatever its fuel, flow, geometry or investigation; the tests pooled are reported per investigation_id, fuel_phase and sample_geometry (joint.composition) and in the summary table
- `envelope.choices.ranges_not_on_axes`: a scenario range of a variable that is not one of 'axes' (flow_cms for the ISS) is printed with 'not applied' and enters no count
- `envelope.choices.nearest_per_axis`: the nearest recorded value of each axis is taken over that axis alone; the two axes can have their nearest value in different tests, and neither need be a test of the Pareto set: they are separate answers
- `envelope.choices.no_hull`: where no counted test records both values, hull kind is 'none', position is 'no hull' and inside is null (no position is defined)
- `envelope.choices.notes_per_need`: every per-need sentence that applies is shown (no_tests where no counted test has ambient oxygen, no_nominal where the scenario has no nominal point); there is no precedence
- `order_changes.choices.values`: values are read as printed in the reference item's 'values' (exact decimals; JSON numbers read as decimal strings), no tolerance
- `order_changes.choices.classes`: for materials a, b and condition columns c1, c2: s1 = sign(a[c1] - b[c1]), s2 = sign(a[c2] - b[c2]); concordant if s1 = s2 != 0; discordant if s1 = -s2 != 0; tied_first_column_only if s1 = 0 and s2 != 0 (T_x); tied_second_column_only if s2 = 0 and s1 != 0 (T_y); tied_both_columns if both are 0. Concordant, discordant, tie, T_x and T_y as defined on the NIST Dataplot KENDALLS TAU page; tied_both_columns is the remaining class and enters neither T_x nor T_y
- `order_changes.choices.kendall_tau_b`: tau_b = (N_c - N_d) / sqrt((N_c + N_d + T_x)(N_c + N_d + T_y)) as defined on the NIST Dataplot KENDALLS TAU page (https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/kendell.htm); N_c = concordant pairs, N_d = discordant pairs, T_x, T_y = pairs tied in one column only; the script stops if the denominator differs from (n_0 - n_1)(n_0 - n_2); given exactly as numerator and the integer under the square root, and as a decimal rounded half-even to 'tau_b_digits' digits; undefined where the square root is 0
- `order_changes.choices.tau_b_digits`: 6
- `order_changes.choices.column_pairs`: every unordered pair of condition columns, in the column order of the spec
- `order_changes.choices.material_pairs`: every unordered pair of materials, in the row order of the item
- `order_changes.choices.criterion`: each condition column carries the criterion named in the spec; a column pair is marked same criterion yes or no; pairs with different criteria are counted like all others and marked
- `order_changes.choices.held`: where the item holds a per-material condition (OF2012: test pressure), each class count is also given for the pairs whose held values differ

Tables read: `H2006.table2`, `OF2012.table1`. Every other reference item with `values` (53 items) is listed in the spec under `order_changes.search.rejected` with its reason and copied into `index.json`. Items without `values` are not looked at: `SAE2008.table1` (NASA/TM-2008-215260 Table 1, 1g and 0g limits of three fuels) holds only a description and would have to be entered as values first; its 1g and 0g cells differ in pressure and flow.

Fixed sentences shown with the envelope numbers (`envelope.sentences`):

- `hull_inside`: Inside (interior or boundary) means that the nominal point lies in the smallest convex region containing the tested (o2_pct, pressure_kpa) points. It does not mean that a test was run close to it: the deltas of the Pareto table give the distance to the closest tests on each axis. It says nothing about the outcome at this point.
- `hull_outside`: Outside means that the nominal point is not in that region: it lies on the outer side of at least one edge of the hull.
- `counts_not_added`: Counts of different needs are not added: one test can be counted for several needs.
- `values_source`: Every value is the pipeline's standardized value in data/pipeline/tests.csv (with source file and row); where the source unit differs, it is the product of the source cell and the unit factor listed under 'conversions', rounded to 4 decimals by the pipeline. Every other number is a count, minimum, maximum or difference of those values.
- `no_outcome`: These numbers say where tests were run, not what happened in them; no outcome variable is read.
- `nominal_not_design`: The nominal point is the one written in scenarios.json; its note there says what it is.
- `no_nominal`: scenarios.json gives no nominal point for this environment, so no nominal-point numbers are computed.
- `gravity_constant`: gravity_level in tests.csv is not a column of any PSI table: it is a constant that the team's source mapping (pipeline/spec/sources.json, 'constants') sets for the whole table. The gravity count therefore equals the number of tests of tables the team mapped to the scenario's level and is not a match found in the data.
- `gravity_column`: gravity_level in tests.csv comes from a column of the PSI table for at least one of these tests.
- `gravity_not_set`: The scenario sets no gravity level.
- `no_tests`: No counted test of this need has a recorded ambient oxygen.
- `no_hull`: No hull: no counted test of this need records both an ambient oxygen and a pressure, so the nominal point has no position.
- `flagged`: A value flagged in tests.csv (for example 'approximate in source', or the start value of a range written in the source) is used as held; such tests are listed under 'flagged tests' and counted at min, max, nearest and in the Pareto table.
- `nearest_separate`: The nearest value of each axis is taken over that axis alone and can come from a different test on each axis; the Pareto table is a separate answer.
- `nominal_rounding`: The nominal values are rounded figures as written in scenarios.json; a gap smaller than half a unit of their last written digit is marked, and the rounding box corners show whether the position depends on that rounding.
- `pooled`: The hull and the Pareto set pool all counted tests that record both values, whatever the fuel, geometry, flow or investigation; the summary table names what was pooled.
- `ranges_not_applied`: A range marked 'not applied' is printed as written in scenarios.json and enters no count: it is not one of the axes.

## What these numbers cannot say

- Whether a material burns, or how, at a scenario's nominal point: no outcome variable is read by the envelope numbers.
- Anything about a point inside the hull beyond the existence of tests on several sides of it: no value is interpolated.
- Anything about gravity levels other than the ones in tests.csv: every test there carries a gravity level that the team's source mapping sets as a constant per table.
- Which of two materials is more flammable in a scenario: the order tables are normal-gravity or drop-tower results printed by the authors, at the printed conditions only.
- Whether a difference of one printed unit is a real difference: the items state no measurement uncertainty or step size.
- Whether the counted tests are the right tests for a need: that is the pipeline's linking rule (needs.json, stated_by), not arithmetic.

## Review of 2026-11-14 (two independent recomputations, model output)

No numerical disagreement was found. Changes made after the review: flagged values are a named choice and listed per need; the unit factors of the pipeline are listed; a need without joint data reports 'no hull' instead of 'outside'; the inside and outside sentences state the convex-hull definition; the pooled investigations, phases and geometries are shown in the summary; the gravity column says it counts a table constant; ranges that are not axes are marked 'not applied'; the nominal rounding is reported; every applicable per-need note is shown (no precedence); OF2012 column pairs carry 'same criterion' and the class counts at different test pressure; held digits are shown as held (18.0, not 18); the item's note on the 0g flow (30 cm/s) and on ref. 8 is quoted.
Left open: the 0g and drop-tower columns of OF2012 still enter the counts with the 1g column (marked, not removed); `SAE2008.table1` is not computable until its cells are entered; the ambient-oxygen rule has no effect on the present counted tests (all 408 distinct counted tests are ambient), so it is untested by the data.

# Model map (experiment, branch `data-lab`)

*AI-generated (Claude Code), 2026-11-14. Not human-reviewed.*

`pipeline/lab/model_map.json` lists every decision point of the main pipeline and of this lab (130 points) with its class and governing model; `pipeline/lab/model_map.md` is written from it by `pipeline/lab/model_map_md.py`. It is the mapper's map after the independent verifier's findings were applied (stretched mappings downgraded, citation details fixed, missing lab points M01-M09 added). A mapping is "established" only if an opened source defines exactly that operation (or it is elementary mathematics whose definition is the model).

Counts: established 53 (elementary mathematics 45, named external model 8), team rule 52 (of which 20 name a candidate model that defines a related but different operation), spec-time judgement 25.

Named external models that govern a lab or pipeline step: NIST SP 811 B.8 factors (inch, atm, bar, psi conversions: D14, D16, D73); NIST e-Handbook 7.2.6.2 percentiles, method R6 (median D63; d-squared quartiles M07); OECD ENV/JM/MONO(2007)2 para 110, smallest convex area containing the points (envelope hull, M01a); NIST Dataplot Kendall tau-b (order classes and tau-b, M06a, M06b). Each lab output names them under `governed_by`.

Finding D15: the pipeline's FLEX factor 0.133322368 kPa per mmHg equals 101325/760 Pa (1 torr); the conventional millimetre of mercury is 133.322387 Pa; SP 811 B.8 prints 1.333 224 E+02 Pa for both. With the conventional value, 31 of the 273 FLEX pressures of `tests.csv` would differ in the 4th decimal (by 0.0001 kPa). Nothing in the main pipeline was changed.

What mathematics cannot remove (each a choice someone made):

- Which established model governs each decision point (this map): AI mapper (Claude Code), not reviewed by a person.
- Which candidate models were searched and opened: AI scout sessions; their search terms bound what could be found.
- Axes compared in the gate (O2, pressure, flow, gravity) and axes shown but not compared (material, criterion, geometry): AI lab session (relation_cards.json/README), team rule.
- Scenario ranges and coverage bins (D45, D48): AI sessions at spec time from EAWG/CH nominal values; team rule.
- Variables of the hull (o2_pct, pressure_kpa) and their units; per-axis linear scaling does not change hull membership, but the choice of variables does: AI lab session (lab_numbers.json), team rule.
- Thresholds: 0.5 share (CO/CO2 card), 5 % O2 floor, 0.5-point tolerance, 0.05-point denominator, 40 cm/s, 0.001 kPa (the d-squared bands were removed on 2026-11-14): AI sessions; some set after seeing the numbers.
- Need taxonomy, required/outcome variables, objective-link verdicts, findings tags, relation cards, inference map, argument: AI readings of documents at spec time; not reviewed by a person.
- Treating documented validity words as the domain instead of the source data's min/max: AI lab session; OECD defines the domain from data.
- Treating a publication's single tested pressure as a point that contains no scenario range: AI lab session; consistent with the range method but makes most cards refuse.
- Which tests form the hull and the Pareto set (pooled across investigations, counted by the pipeline's linking rule, flagged values kept): AI lab session (lab_numbers.json), team rule.
- Boundary counted inside; degenerate hulls; nominal rounding band: AI lab session, team rule.
- Reading 'in the range 25-35% oxygen' (Hirsch 2011) with both ends included: AI lab session, 2026-11-14.
- Order of the gate decision list (outside before domain_not_defined before gravity): AI lab session, 2026-11-14, team rule.
- Which verifier findings to apply and how to classify each point (this corrected map): AI lab session (Claude Code), from verify.json; not reviewed by a person.
- Which verifier findings exist at all: the verifier and the scouts opened what the session proxy let them reach; sources they did not open are listed in the map under `not_rechecked`.

# Raw-file gaps (experiment, branch `data-lab`)

*AI-generated (Claude Code) on 2026-11-14. Not reviewed by a person. The survey of the raw files and the mapping of headers to standard variables were done by AI agents.*

The question it answers: for each PSI investigation and each standard variable that the six needs use, is the quantity in the experimental table, in a raw file that the table does not summarise, only in a document sentence, possibly only in videos or archives, or nowhere in what was sampled?

## Files

| File | What |
|---|---|
| `pipeline/spec/raw_columns.json` | The survey as a spec: per investigation the file groups, the sample file with its PSI file id and listing size, the headers as written (re-opened on 2026-11-14 where `header_check` says so), what one file is per, the link to the experimental table, and the header-to-variable mappings (`mapping_by`: AI reading of the header, not confirmed by a document). Also the fixed sentences of the outputs |
| `pipeline/lab/raw_gaps.py` | Decides one state per investigation and variable by rule; writes the two outputs |
| `data/pipeline/lab/raw_gaps.json`, `raw_gaps.md` | States per investigation and variable; per need, the states of the required variables over the counted or recorded tests (`need_tests.csv`) and over all tests in scope, and the states of the outcome variables over all tests in scope |

Run: `python3 pipeline/lab/raw_gaps.py` (needs `data/pipeline/tests.csv`, `need_tests.csv` and `raw_inventory.json`). Standard library only; the same inputs give the same bytes.

## What was opened

- The survey (AI agents, 2026-11-14) downloaded 159 PSI files, 180,483,501 bytes in all, from 19 investigations, and read one sample file per group of files (the smallest in most groups). The list with PSI file ids and sizes is `_meta.downloaded_files` of `raw_columns.json`. The total is above the 150 MB that the task allowed; the largest single files were 24.9 MB (Saffire-I Sample 2) and 21.3 MB (Saffire-III 1 Hz telemetry).
- This step re-opened the header lines (not the values) of 58 of those files to check the headers of the spec. Every mapped header of a re-opened group was found in the re-read text.
- No `.zip` archive and no video was downloaded or opened. PDFs, Word and PowerPoint files were not opened.
- Five investigations were not surveyed: PSI-60, PSI-62, PSI-115 and PSI-117 have no experimental table; PSI-142 is an index of figures. The survey result for PSI-39 and PSI-107 was empty; their entries were written from the agents' `reading.json` files and the header re-check.

## Limits

- One file per group. Other files of a group may have other columns (two header variants were seen in PSI-68 Chamber_Readings; the three smallest PSI-20 data files have no header row).
- A mapping is a judgement on header text. Headers of a related but different quantity (a voltage for a power, a volume flow for a velocity, a total mass for a rate) are listed under `related_not_mapped` and are not counted.
- `measured_not_summarised` says that a column exists. A column in a raw file says the quantity was logged; it does not say the log is complete, calibrated or usable. Many columns are time series, settings, event timestamps or free text (`column_is`), and turning them into one value per test would be a team computation.
- `video_or_archive_only` is decided from counts in `raw_inventory.json`. It does not say that a video or an archive holds the quantity.
- Links of raw files to table rows are those the survey reported; several are by day or by time only, and some are unsettled (PSI-69 FLEX numbers, PSI-98/99/100 sample labels).
- No file read states why a quantity is not in the experimental table.
- The PSI-26 planned test matrix holds a note cell that appears to contain account names and passwords. Its text is not reproduced anywhere, and the file should not be published.
