---
role: catalog
updated: 2026-11-14 14:25 KST
state: working
blocked_on: none
---
Now: owner of `data/catalog/`, `scoring/`, `validation/`, `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`, `web/scorer.js`, `web/parity_check.*` (in `roles.json` since pm's 14:08 sync). Review fixes from the human lead's request are done; pm's two decisions are applied; ui's request 1409 is done.

**pm: the scorer, its config and `data/catalog/` changed in this push. Please rerun `python3 ai/audit_catalog.py` and `python3 ai/check_all.py`.**

Done since last sync (branch `catalog-scoring`):
- 14:24 **Scoring config 1.1.0: changes A and B applied (the human lead's decision).**
  - A: the O2 distance is the log of the O2 ratio. Near air it is the same as before.
  - B: a different inert diluent is compared by molar heat capacity at 298 K (CO2, N2, He).
  - Python and JS together.
  - `config_version` in `rank()` output is now `1.1.0`.
  - ui, pm:
    - `ISS` and `lunar habitat` keep their top 3; scores move by less than 2 points.
    - Typed demo queries changed: `ISS cotton fabric` swaps ranks 2 and 3 (SAFFIRE-III, then BASS-II-C04). `lunar habitat cotton fabric` and `달 기지 면직물` rank SAFFIRE-I-C01 second, where BASS-II-C05 was.
    - If a slide or a screenshot shows those two queries, retake it.
  - `validation/verification_sheet.csv` rebuilt: 12 configurations; BASS-II-C05 is no longer in a demo result.
- 14:19 `scoring/MODEL_BASIS.md` (new, English). It checks each scoring rule against a combustion textbook the human lead supplied: Turns, *An Introduction to Combustion*, 3rd ed., McGraw-Hill 2012. The book is copyrighted, so it was read as background only; nothing from it is reproduced, and it is listed in `compliance/SOURCES.md`.
  - Supported: the direction of the oxygen rule, the log form of the pressure rule, the gravity warnings, quiescent against forced flow, the fuel-phase gate, and the oxidizer-stream rule.
  - Not covered by the book: flame spread over solids (thin or thick, opposed or concurrent), which rests on the PSI records.
  - Two candidate changes, A and B, applied at 14:24 (above).
  - pm: it may help the Validity part of the write-up. No code changed.
- Review fixes asked by the human lead (14:00):
  - `74b206e` "CO2 30%" is no longer read as 30% oxygen; "천장" (ceiling) is no longer read as cloth.
  - `5f1627e` Confidence counts only values compared with a recorded value. Assumed (fallback) O2 and pressure no longer count.
    - ISS #2 BASS-C01 now shows low confidence (0.3).
    - ISS cotton fabric #1 BASS-C01 now shows medium (0.65).
  - `93b193a` A flow speed inside a one-sided range ("up to 40 cm/s", PSI-26) scores unknown (0.5), not a miss. There is no jump at 40.
  - `8d39b1c` "tested" is used only for table values. New catalog columns `o2_source`, `pressure_source`, `flow_source` (table | record | test_matrix | team). The reasons word non-table values by source:
    - ACME-BRE-C01 pressure is "named in the PSI record, not a test value". The objective names 8.2 to 14.7 psia, and the table says pressures "are not identified".
    - FLEX-2 values are "from the test matrix".
    - 0 cm/s for FLEX, CFI and BRE is a "team reading".
- pm decisions 14:15, `8a352cd`:
  - `human_verified` scores like `ai_extracted` (0.7).
  - New result warning `ranges_separate`. It is on all three lunar-habitat results; it is not on ISS, whose atmosphere is assumed.
- ui request 1409 (pm's audit), `1d361b2`: FLEX-2 objectives, FLEX-2-C02 and SAFFIRE-III labels, and SAFFIRE-II key findings now read as the NASA sources write them. Answered `done`.
- Closed my requests 1332 and 1345 (pm answered both).
- Checks: 35 unit tests, validation 29/29, parity 68/68, catalog against tests.csv OK, `catalog.xlsx` rebuilt.

Next:
- Sync every 20 minutes until the 19:00 freeze; fixes only after that.
- Rerun `validation/build_verification_sheet.py` if the demo top results change.

Published for others:
- `data/catalog/configurations.csv`: three new columns after `atmosphere_basis` (additive), `o2_source`, `pressure_source`, `flow_source`. Values: `table`, `record`, `test_matrix`, `team`, or empty. The other columns are unchanged in name and order.
  - Text changes: `config_label` of FLEX-2-C02, SAFFIRE-III-C01 and C02.
  - Value change: BASS-II-C04 `flow_max_cms` 29.
- `data/catalog/investigations.csv`: text of FLEX-2 `objectives` and SAFFIRE-II `key_findings`.
- `scoring.scorer.rank`:
  - Same shape.
  - New warning code `ranges_separate` (text in `scoring_config.json`).
  - `coverage` and `confidence` now leave out assumed values.
  - The text of `why` and `main_gap` changed: "named in the PSI record, not a test value", "from the test matrix, not individual tests", "team reading, not in the table", "up to 40 cm/s".
- Demo rankings:
  - Up to 14:19 (review fixes): `ISS`, `lunar habitat`, `spacesuit`, `Mars base`, `ISS cotton fabric` and `lunar habitat cotton fabric` kept their top 3 and scores. Only confidence labels and warnings changed.
  - Since config 1.1.0 (14:24): `ISS`, `lunar habitat`, `spacesuit` and `Mars base` keep their top 3. `ISS cotton fabric` and `lunar habitat cotton fabric` changed (see above).
- `scoring_config.json` 1.1.0: `similarity.o2` uses `above_scale_ln` and `below_scale_ln` in place of `above_scale_pct` and `below_scale_pct`. `similarity.diluent` gains `molar_cp_298K_kJ_per_kmolK` and `cp_ratio_exponent`. If the page draws anything from the old o2 keys, it needs the new ones.
- Queries with a flow speed changed, for example "SIBAL 45 cm/s" and "PMMA rod 35 cm/s": BASS's "up to 40 cm/s" is no longer treated as a test at 40.

Notes for other roles:
- ui: the page prints the new warning from the config. A result can now carry `ranges_separate` next to `outside_range`.
- data: the scorer still reads catalog ranges, not test rows, so `ranges_separate` is a caveat, not a joint check. A joint check would need `tests.csv` in the browser.
