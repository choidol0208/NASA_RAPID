---
role: catalog
updated: 2026-11-14 13:48 KST
state: working
blocked_on: none
---
Now: owner of `data/catalog/`, `scoring/`, `validation/`, `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`, `web/scorer.js`, `web/parity_check.*`. ui handed them over at 13:40; it had already done items 1 to 6 of the 13:10 list. I reviewed those against the NASA tables, fixed two points, and did items 7 and 8.

Done since last sync (branch `catalog-scoring`):
- Merged `catalog-filter` (ui's items 1 to 6) and reviewed them:
  - 1, 3, 4 and 6 kept as they are.
  - 2 and 5 corrected (below).
- `727d271` catalog: BASS-II air speeds above 40 cm/s are not read as air.
  - Sources: the PSI-25 record says "airflow speeds up to 40 cm/s"; the table puts fan readings in brackets; row 121's fan cell reads 52.
  - BASS-II-C04 (SIBAL) flow is now 1–29 cm/s (row 115), not 1–53. BASS-II-C03 (rods) stays 0–38.5 (row 72, "incr to max 38.5").
- `894a049` scorer: bare "gas" and "가스" are no longer fuel keywords; compound forms instead ("gas jet", "jet flame", "gaseous fuel", "gas fire", "가스 누출", ...).
  - Before, "inert gas suppression ISS", "CO2 gas extinguisher ISS" and "combustion gas detection" were scored as gas-fuel questions.
  - Validation F05, F06.
- `9498c10` scorer: a range with one recorded end reads "up to 40 cm/s" or "at least …" (BASS, PSI-26). The text changed only; scores are the same. 2 unit tests.
- Item 7: `validation/verification_sheet.csv` and `validation/build_verification_sheet.py`. 104 checks for the 13 configurations behind the demo queries, with NASA table rows and raw cells.
- Answered data 1328 (to all). Closed my handover request to ui.
- Request to pm: two scorer decisions before the freeze (whether human checks change the score; `ranges_separate` warning).
- Checks: unit tests 26/26, validation 28/28, parity 67/67, catalog against tests.csv OK.
- `data/catalog/catalog.xlsx` rebuilt (openpyxl 3.1.5, MIT, already in `compliance/SOURCES.md`, installed with the human lead's approval). Both sheets match the CSV files cell for cell.
- Live: ui merged `catalog-scoring` at 6e15ead into `catalog-filter` (acf8f85). The Pages run is green.
- data request 1319: closed by ui; the catalog needs nothing more from data.

Next:
- pm's answers: the new role in `roles.json` (request 1332) and the two scorer decisions (request 1345, item 1 defaults at 16:00).
- Sync every 20 minutes (:07, :27, :47) until the 19:00 freeze; fixes only after that.

Published for others:
- `data/catalog/configurations.csv`: BASS-II-C04 `flow_max_cms` 53 → 29, plus `source_notes` text for C03 and C04. Same columns.
- `scoring.scorer.rank` output: same shape. Text of `why` and `main_gap` changed for open ranges ("up to 40 cm/s").
- Demo rankings: `ISS`, `lunar habitat`, `spacesuit`, `Mars base`, `ISS cotton fabric` and `lunar habitat cotton fabric` have the same top 3 and the same scores.
- `validation/verification_sheet.csv`: new file, for people.

Notes for other roles:
- pm: `catalog-scoring` needs integrating into `main` (the site already has it through `catalog-filter`, acf8f85).
- ui: thanks for the clean handover. I changed your BASS-II reading: "max(47)" and "6 53" are fan readings, so SIBAL is 1–29. Your request 1319 to data can be closed from your side. Nothing more is needed from data.
- data: the catalog's BASS-II flow tops (38.5 rods, 29 SIBAL) are now both within the record's 40 cm/s.
