---
from: catalog
to: ui
opened: 2026-11-14 13:32 KST
needed_by: 14:15
closed: false
---
# Handover of the catalog, the scorer and validation to the new `catalog` role

*AI-generated (Claude Code), catalog role.*

## What I need

The human lead started a fourth session for the catalog and the ranking: role `catalog`, branch `catalog-scoring`. At 13:28 KST they decided:

1. **ui finishes the two items it already started** from the handoff list of 13:10, then pushes them:
   - (1) assumed atmosphere is never worded as tested (your commit 2a0f083);
   - (2) catalog values that differ from the NASA tables (`build_catalog.py`, in progress, with your question to data in request 1319).
2. **Then answer this request `done`** with the commit. From then on, leave these paths to catalog:
   - `data/catalog/`, `scoring/`, `validation/`
   - `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`
   - `web/scorer.js`, `web/parity_check.py`, `web/parity_check.mjs`

   pm is asked to move them in `roles.json` (request `20261114-1332-catalog-to-pm-new-role-catalog-on-branch-catalog-scoring`). For a change there, open a request to catalog.
3. **Please do not start the other items of that list**; catalog does them:
   - (3) burner oxidizer-stream oxygen matched as ambient
   - (4) `o2_above_all` threshold
   - (5) gas-jet and droplet keywords
   - (6) catalog-against-pipeline check
   - (7) verification sheet
   - (8) "up to" wording

   If you already changed any of them, say which in the answer.
4. **In the answer, list anything in (2) that is left open**, for example a value that waits for data's answer to 1319. catalog picks it up from there.
5. **At each sync, merge `origin/catalog-scoring` into `catalog-filter`** (`coord.py pull catalog` once `roles.json` has the role). Otherwise a deploy from `catalog-filter` would put the site behind `main` for the catalog and the scorer.

Item (6) wants the new check in `.github/workflows/pages.yml` next to the parity check. That file stays yours; I will send the one step as a separate request when the script exists.

## Why

Two sessions in the same files at once break the merge and the parity check.

## Until then

catalog re-checks items (3) to (8) against the NASA tables, without editing these paths.
