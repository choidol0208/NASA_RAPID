---
request: 20261114-1442-data-to-all-counts-changed-after-a-literature-check-of-the-f
by: catalog
state: done
answered: 2026-11-14 14:56 KST
---
# Answer

*AI-generated (Claude Code), catalog role.*

Done; nothing on the catalog side breaks. The scorer reads only the catalog, never `need_tests.csv`, `scenario_needs.csv` or the counts, so no ranking changes.

One catalog text followed your point 3:
- SAME-C01 `key_findings` said "weight-loss rate 1–2 mg/min" as if it were a condition the tests ran at.
- It now reads: "Conditions in the table: air flow 5–10 cm/s and aging 1–20 min. Its weight-loss rate (1–2 mg/min) is a planned target of the test matrix, not a measured result". The reference is `SAMEEIRD.target` in `pipeline/spec/references.json`.

Point 4: SAFFIRE-I-C01 keeps O2 21.5–21.7%, the cell as written ("21.5 - 21.7"), and makes no midpoint. Its reasons say "O2 tested 21.5–21.7%".
- If you want the catalog to name 21.7% as the initial O2 the investigators report (`SAF17.o2_initial_I`), say so and I change the text.
- The ranking would not move: both values are within 2 points of air.

The catalog holds no sentence on combustion products or on need counts.
