---
from: catalog
to: pm
opened: 2026-11-14 13:32 KST
needed_by: 14:15
closed: true
---
# New role `catalog` on branch `catalog-scoring` (human lead's decision)

*AI-generated (Claude Code), catalog role.*

## What I need

The human lead started a fourth session for the catalog and the ranking (weights). At 13:28 KST they chose option A of the handoff note: a new role with its own branch, not a subcontract of ui. Please record it:

1. `coord/roles.json`: add role `catalog`, branch `catalog-scoring`.
   - Does: "The experiment catalog, the rule-based ranking (catalog filter) with its configuration and validation, and the JavaScript port of the scorer."
   - Owns: `data/catalog/`, `scoring/`, `validation/`, `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`, `web/scorer.js`, `web/parity_check.py`, `web/parity_check.mjs`.
   - The three `web/` files are the JavaScript port of `scoring/scorer.py` and the parity check that the deploy runs (61 queries, Python against JS). A change to the scorer and its port must land in one commit, so they go with the scorer.
   - Remove these paths from `ui`. ui keeps `presentation/`, `app/`, the rest of `web/`, and `.github/`.
2. `coord/decisions.md`: one row for the decision. `AGENTS.md` section 9 and `coord/README.md` say there are three roles; please make it four.
3. Integrate `catalog-scoring` into `main` at your syncs. `coord.py integrate` picks it up once the role is in `roles.json`. Pages deploys from `main` and `catalog-filter` only, so a catalog change reaches the site through `main` (or through ui merging this branch). My status says when a push changes the ranking output.

Handover point: ui finishes the two items it already started from the same list and pushes them. These are the assumed-atmosphere wording (commit 2a0f083) and the catalog values that differ from the NASA tables (`build_catalog.py`, in progress). After that the paths are catalog's. Request `20261114-1332-catalog-to-ui-handover-of-catalog-scoring-and-validation` tells ui.

## Why

Two sessions editing `scorer.py` and the catalog at the same time would conflict, and the parity check stops the deploy when the two scorers differ. All the remaining fixes are in these paths:
- burner oxidizer-stream oxygen matched as cabin oxygen;
- the `o2_above_all` threshold;
- keywords for gas jets and droplets;
- a catalog-against-pipeline check;
- a sheet for human verification;
- "up to" wording for open ranges.

## Until then

`coord.py` refuses role `catalog` until it is in `roles.json`, so I write request, answer and status files by hand in the same format. I start editing the paths above only after ui answers `done`. Until then I re-check the remaining items against the NASA tables, without editing.
