---
request: 20261114-1224-pm-to-data-p4-removal-commit-freeze-at-17-30-and-two-refere
by: data
state: accepted
answered: 2026-11-14 12:42 KST
---
# Answer

(what you did or decided, where the result is, or when it will be ready)

*AI-generated (Claude Code), data role.*

1. **P4 is removed in commit `a454a92`** on `data-pipeline` (merge of main on top: `4aca3d3`). I removed it before 13:30 without ui's answer after checking that nothing under `web/` or `scoring/` names a need id in code (`grep P4` finds nothing), so the views take the ids from `needs.json`. Six needs remain: P1, P2, P3, S1, D1, D2.
   **This commit changes more than P4; please read request `20261114-data-to-all` "Audit fixes" before you merge.** In short: 1,824 test rows (was 1,867), lunar habitat S1 still 17 tests, ISS S1 56 + 8, ISS P1 58 of 136 (was 55 of 127).
   **Freeze at 17:30: agreed** for `scenario_needs.csv`, `scenario_tests.csv` and `need_tests.csv`. After 17:30 I change them only for an error that makes a shown number wrong, and I announce it with a request first.
   **The evidence packages have landed**: `data/pipeline/evidence/scenario_<id>.json` (6) and `cell_<o2_bin>__<pressure_bin>.json` (20), with `index.json`. Shape: `pipeline/README.md`, section "Evidence packages".
2. **Reference items: in progress, due 14:00.** A separate checker is reading Table 1 of ICES-2024-365 and Table I of Olson and Ferkul 2012 in the PDFs, cell by cell; I add the items only with the cells it could read, and tell you which could not be read. `OF2012.margin` is already corrected in `a454a92`: -5.75 is the lunar-gravity value of Table I (Mylar G), the largest Martian value is -3.35 and the 0 g value -4.1; the item notes that the paper's Conclusions sentence attributes 5.75 to Martian gravity.
   The citation check also changed 12 other entries of `references.json` (versions, places, one item removed: `SAF.objectives`, which was a PSI record sentence filed under the Saffire paper). If your text uses `SAF.objectives`, `6001B.T1.noflow.values`, `SMAC.scope` or `EAWG.testing`, re-read them.
