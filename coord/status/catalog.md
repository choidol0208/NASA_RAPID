---
role: catalog
updated: 2026-11-14 13:33 KST
state: working
blocked_on: 20261114-1332-catalog-to-ui-handover-of-catalog-scoring-and-validation
---
Now: new role, started 13:20 by the human lead. It takes over the catalog, the scorer and validation from ui on branch `catalog-scoring`. Until ui answers the handover request, I re-check the remaining fixes against the NASA tables without editing.

Done since last sync:
- Fetched `main`, `catalog-filter`, `data-pipeline`. Read `AGENTS.md`, `coord/`, `contracts/README.md`, `scoring/README.md`, `data/catalog/README.md`, `pipeline/README.md`.
- Baseline on `origin/catalog-filter` f4a521e: unit tests 18/18, validation 22/22, parity 61/61.
- Requests to pm (new role in `roles.json`) and to ui (handover after its two items in progress).

Next: once ui answers, merge `catalog-filter`, then items in this order:
1. Burner oxidizer-stream oxygen matched as cabin oxygen.
2. `o2_above_all` from ambient tests only.
3. Gas-jet and droplet keywords, with validation scenarios.
4. A catalog-against-pipeline check under `validation/`.
5. A human verification sheet.
6. "up to" for open ranges.

Each item is tested, validated and checked for parity before its push.

Published for others: nothing yet. `data/catalog/*.csv` and the `scoring.scorer.rank` output keep their shape. If a fix changes the demo rankings (`ISS`, `lunar habitat`), this file says so before the push.

Notes for other roles:
- The role is not in `roles.json` yet, so `coord.py` refuses `.role = catalog`. Until pm adds it, my request, answer and status files are written by hand in the same format.
