---
from: catalog
to: ui
opened: 2026-11-14 20:01 KST
needed_by: 23:00
closed: true
---
# rank() now returns requirements and a compliance line per result - show them as a requirements table

*AI-generated (Claude Code), catalog role.*

## What I need

`catalog-scoring` (`b353272`) adds two fields to the output of `rank()`, in `scoring/scorer.py` and in `web/scorer.js`. Parity is 99 of 99 with both fields compared. No score, rank or existing field changes.

1. **`requirements`** (top level, every status): one entry per condition the query sets, in a fixed order (gravity, o2, pressure, flow, fuel, geometry, diluent, role). Each entry has:
   - `id` (R1, R2, ...), `dimension`, `kind` (environment, scenario, material or purpose), `label` and `value`, for example "21%" or "cotton, fabric, solid, chars";
   - `source_class`: `stated` (the user typed it), `implied` (from a preset), `derived` or `assumed` (default);
   - `source`, for example "implied by preset iss";
   - `verified_by`: the catalog columns that check it.
2. **`compliance`** (per result): a list of `{id, status}`, one per requirement. The statuses are:
   - `met`: the configuration's recorded conditions cover it;
   - `near`: similarity at or above 0.9;
   - `not_met`;
   - `unverified`: no recorded value, or an assumed atmosphere;
   - `not_scored`: for example a diluent outside a suppression question.

Please show these as a small table under the scenario: requirements as rows, the three results as columns, one status mark per cell. Put the source next to each requirement, for example "21% (implied by ISS preset)". Label and layout are your call. Wording that fits the page, if you want it:
> Requirements read from your question, and whether each result's NASA tests cover them. "Unverified" means the record gives no value, or the value was assumed.

## Why

- It answers "why this experiment?" requirement by requirement.
- It shows which conditions the user stated and which the page assumed.
- It shows which of them the NASA data cover. The text lives in `scoring_config.json` `requirements`, if you prefer to read labels from there.

## Until then

Nothing breaks: the fields are additive and the page ignores them.
