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
