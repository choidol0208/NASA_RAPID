---
request: 20261114-1332-catalog-to-ui-handover-of-catalog-scoring-and-validation
by: ui
state: done
answered: 2026-11-14 13:40 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done. Items (1) and (2) are pushed and live. The paths are yours from now on.

**One thing first: items (3) to (6) are already done and live.** The human lead asked this session for the whole 13:10 list (verify each item against the NASA tables, then fix). I pushed (1) to (6) at 13:27 (`fc29e12`), one minute before the 13:28 split reached me. They are yours now: review, change or revert as you see fit.

| Item | Commit | What it does |
|---|---|---|
| (1) assumed atmosphere wording | `2a0f083` | The old session's patch, checked. 65 queries keep the same scores, order and warnings; only `why`/`main_gap` text changes. Three unit tests (`AssumedAtmosphereWording`), which fail on the old wording. |
| (2) catalog vs NASA tables | `98428d3` | See below. |
| (3) oxidizer-stream O2 | `4136f90` | `s_o2` returns unknown for `o2_reference = oxidizer_stream` (Python and JS). The result carries the `oxidizer_stream` warning, and no `not_reported` or `o2_above_result`. ISS unchanged. Lunar habitat keeps its top 3; #4 ACME-FLAME-DESIGN is now C01 (70.3) instead of C02 (71.6). |
| (4) `o2_above_all` | `4136f90` | Uses the highest surrounding-atmosphere O2 (40%; the warning names ACME-FLAME-DESIGN-C01). Warning texts in `scoring_config.json` reworded. Three unit tests (`OxidizerStream`). |
| (5) gas and droplet keywords | `d2f9189` | Keywords "gas", "gas jet", "jet flame", "gaseous fuel", "기체 연료" (gaseous fuel) and "제트 화염" (jet flame) are read as gas; "droplet(s)", "fuel droplet", "액적" (droplet) as liquid. Validation scenarios F01 to F04; T01 now expects ACME-BRE or ACME-CFI-G. Validation 26/26, parity 65/65. |
| (6) catalog vs pipeline check | `2e50a15` | `validation/check_catalog_pipeline.py`, plus the step "Catalog agrees with the data pipeline (tests.csv)" in `pages.yml`, already in place; you don't need to send that request. It passes on `main`'s tests.csv and on `origin/data-pipeline`'s. It failed on the catalog as it was before (2). |
| (7) verification sheet | — | Not started. No `verification_status` changed; all 41 rows are `ai_extracted`. |
| (8) "up to" wording | — | Not started. BASS (PSI-26) still reads "at 40 cm/s". |

**(2) in detail**, in `scripts/build_catalog.py` then regenerated (each row's `source_notes` names the NASA rows):
- **BASS-II-C03 flow: 0 to 38.5 cm/s.** The 13:10 note suggested 0 to 20, but row 72 says "incr to max 38.5". 20 is only the largest starting number, which is what tests.csv keeps.
- **BASS-II-C04 flow: 1 to 53 cm/s.** The source rows are 115, 117 and 121, all with 'Flow restrictor' = 0.
  - Rule in `bass2_air()`: numbers outside brackets; "max(47)" keeps its number; numbers after "pot" are dropped; above 40 cm/s only with the restrictor out.
  - Rows 53, 54 and 63 carry fan readings in the air column.
- **SPICE-C01 flow: 0.66 to 85.28 cm/s**, from the Air Rate column. 8 negative cells are left out.
- **Test counts.** CFI is 79 and SPICE 435, after dropping exact repeated rows (`unique_rows()`). SAME is 4, because rows 6 to 9 record no values.
- **Notes.** PSI-25 and PSI-107 investigation notes updated.

**Left open in (2):**
- **Request 1319 to data, partly answered.** data stopped reading row 73 "incr to 28" as a minimum. There is no `flow_max_cms` column yet, so the check lists PSI-25 flow as a documented wider range (`FLOW_WIDER`). With data's new tests.csv that reads catalog 0 to 53 against pipeline 0 to 20. Close 1319 or carry it on as you like; it is now yours.
- **`data/catalog/catalog.xlsx` is not regenerated.** It needs openpyxl, which is not installed on this PC, so it still shows the old five values.

**From now on**
- ui no longer edits `data/catalog/`, `scoring/`, `validation/`, `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`, `web/scorer.js`, `web/parity_check.py` or `web/parity_check.mjs`. For a change there, ui opens a request to catalog.
- `web/app.js` relies on `createScorer` and `parseCSV` exported by `web/scorer.js`, and on the `rank()` output fields. Please keep those, or send a request first.
- `.github/workflows/pages.yml` stays with ui. Send a request if you want a step changed.
- At every sync ui merges `origin/catalog-scoring` into `catalog-filter`. This sync already did, and it merged cleanly.
