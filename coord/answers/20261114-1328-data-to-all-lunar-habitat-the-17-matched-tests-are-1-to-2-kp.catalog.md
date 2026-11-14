---
request: 20261114-1328-data-to-all-lunar-habitat-the-17-matched-tests-are-1-to-2-kp
by: catalog
state: done
answered: 2026-11-14 13:45 KST
---
# Answer

*AI-generated (Claude Code), catalog role (new since 13:20: catalog, scorer and validation, branch `catalog-scoring`).*

Done for catalog's part. Nothing in the catalog or the scorer has to change for option 1. I checked the same point in the ranking.

**The ranking shows the same pattern, in its reasons.**
- `rank("lunar habitat")` puts FLEX-C01 second. Its reason reads "O2 match 1.00 (O2 tested 12–34%); pressure match 1.00 (pressure tested 70.2–309.3 kPa)".
- Each range is true for the configuration's 274 FLEX tests (`tests.csv`). The two are not true together:
  - The 70.2 kPa tests are at 18 to 21% oxygen.
  - The 24 FLEX tests at 30% oxygen or more are at 71.2 to 102.8 kPa.
- The scorer compares each variable separately, so the score barely moves (70.3 against 71.2 kPa). What can mislead a reader is the reason text.

**pm: one decision, if you want it changed before 19:00.** I can add a result warning `ranges_separate` (additive code, Python and JS together, parity checked) on results where both oxygen and pressure are compared:

> O2 and pressure ranges are each taken over all tests of this configuration; they do not say a test was run at both.

It would not change any score or order. Say yes or no in your answer to my request `20261114-1332-catalog-to-pm-...` or in `coord/decisions.md`. Without an answer I leave it as is.

**On ui's request 1319 to data (now catalog's), the catalog changed since it was written.** Commit `727d271` on `catalog-scoring`:
- The catalog no longer reads 53 (row 117) or "max(47)" (row 121) as air speeds.
- Reasons:
  - the PSI-25 record says the tunnel could impose "airflow speeds up to 40 cm/s";
  - the table puts fan readings in brackets;
  - 53 is the size of row 121's fan reading (52).
- BASS-II-C04 (SIBAL) is 1 to 29 cm/s; BASS-II-C03 (rods) stays 0 to 38.5 (row 72, "incr to max 38.5").
- A `flow_max_cms` column is still welcome but not needed: `validation/check_catalog_pipeline.py` documents the difference against your starting values, and passes.
