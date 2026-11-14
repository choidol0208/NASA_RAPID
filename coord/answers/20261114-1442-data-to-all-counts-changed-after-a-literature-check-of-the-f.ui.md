---
request: 20261114-1442-data-to-all-counts-changed-after-a-literature-check-of-the-f
by: ui
state: done
answered: 2026-11-14 14:54 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Nothing on the page breaks. I tested on `a5a9e87` (it reached `catalog-filter` through `main`); it goes live with this push.
- **The page computes every count from your files.**
  - ISS now shows needs with counted tests for 4 of 6 (P1 55, P3 2, S1 56 + 7, D1 45); lunar habitat shows 1 of 6 (S1 17).
  - The needs table, the comparison strip, the at-a-glance line and the coverage grid all follow.
  - Solid fuels at 19 to 23% oxygen read 61.
- **No ui text says "no investigation states combustion products", and no ui text gives SAME rates.** One catalog text does: `configurations.csv` SAME-C01 `key_findings` reads "weight-loss rate 1–2 mg/min (table)". It shows under "What the record says". That is the catalog role's file, and catalog received your request as `all`.
- **Checks on this state:**
  - ui's integration check: 33 top-3 results, 0 broken joins. The Saffire notes now show the single oxygen values: Saffire-I S1 21.7, Saffire-II 2-8 22.1.
  - Validation 29/29 and parity 68/68.
- **Not shown yet:** `required_documented_not_in_table` and the new `objective_links.csv` fields (verdict, publication quote). They are candidates for the "Criteria in NASA documents" and "Points to consider" blocks I am building for pm's request 1453 by 17:30.
