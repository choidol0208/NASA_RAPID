---
request: 20261114-1224-pm-to-data-p4-removal-commit-freeze-at-17-30-and-two-refere
by: data
state: done
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

**Update 12:47 KST: both reference items are in `pipeline/spec/references.json`** (commit after `e92bfc7` on `data-pipeline`). Each table was read from the PDF text layer and from a page image, and every number in the items was compared with the text layer again by script.

- `SAF456.conditions` under the new reference `ICES-2024-365` ("Preliminary Results from the Saffire VI Experiment", NTRS 20240002981, Table 1, p. 3), `access: full_text_read`. All five of your claimed cells match: IV-1 SIBAL cloth 100.0 kPa, 22.0 mol % oxygen; V-2 cotton jersey 70.7 kPa, 26.2; VI-2 SIBAL cloth 54.1 kPa, 31.0; VI-3 two-sided PMMA 54.6 kPa, 30.3; VI-4 one-sided PMMA 55.2 kPa, 28.8. All five at 20 cm/s concurrent flow. `values.rows` holds the whole table.
  - Do not call the values "measured" or "set point": the paper does not say which they are. Its only description is "vented the spacecraft to the requested pressure and ... released oxygen to bring the spacecraft to the desired condition (Table 1)".
  - The table covers the five samples considered in that paper, not every Saffire IV to VI sample.
  - NTRS marks this paper "may include copyright material": cite numbers, do not reproduce figures or long passages.
- `OF2012.table1` under `NTRS-20130010991` (Table I, p. 6). The table gives two limits per gravity level, ULOI and MOC (ULOI*/MOC* in low gravity), for Mylar G (10.2 psia), Ultem 1000 (10.2 psia) and Nomex HT90-40 (14.7 psia), and the oxygen margin of safety. Keys in `values.rows`: `uloi_o2_pct_1g`, `moc_o2_pct_1g`, `uloi_star_o2_pct_martian`, `moc_star_o2_pct_martian`, the same for `lunar` and `0g`, `delta_o2_pct_martian`, `delta_o2_pct_lunar`, `delta_o2_pct_0g`, `pressure_psia`.
  - Confirmed: -5.75 is the lunar value for Mylar G; the largest Martian value is -3.35 (Nomex HT90-40). The paper's Conclusions sentence says "at Martian gravity ... (up to 5.75% O2 lower)", which its own table does not support. Use the table.
  - The low-gravity limits come from 5.18 s drop-tower tests with criteria that the paper says "are not the same as 1g"; the item text carries this. Please keep that caveat in any sentence built on it.
  - Do not quote the Fig. 6 caption averages ("-2.6%", "2.7%"): they do not reproduce from Table I.
  - The number "AIAA 2012-3492" is not printed in the NTRS copy; NTRS lists the 42nd ICES, San Diego, July 2012. Noted on the reference as not verified.

