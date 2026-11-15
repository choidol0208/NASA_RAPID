---
from: data
to: pm
opened: 2026-11-15 10:37 KST
needed_by: 12:00
closed: false
---
# After the next merge of data-pipeline: rebuild data/insights (added fields make ai/check_all.py report stale files); four new data files are in

## What I need

*AI-generated (Claude Code), data role.*

**When you next merge `data-pipeline` (now at `35f0f45`), run `python3 ai/build_all.py` before `ai/check_all.py`.** On the data branch `ai/check_all.py` reports 9 hard failures: 5 were there before today's work (among them `model_readiness`, which cannot import `sklearn` in the data role's environment), the others are `data/insights/` files that are older than `references.json`, `needs.json` and the evidence packages, which gained fields. Nothing that existed was renamed or removed; `pipeline/check.py` is 90 of 90 PASS; the four frozen files equal `dd34a76`; counted tests unchanged.

What was added (details in `pipeline/README.md`):
1. `catalog_comparison.csv` and `catalog_comparison_summary.json`: all 41 catalog configurations against `tests.csv` for oxygen, pressure, flow and test count, with the mapping rule of `web/check_integration.py`. Test counts: 28 equal, none different. Oxygen: 13 equal exactly (16 with rounding to the catalog's printed digits), 4 where the catalog is wider. Pressure: 0 equal exactly, 7 with rounding. Flow: 14 equal, 2 where the catalog is wider (BASS-II-C03: catalog 0.0 to 38.5, table 0.0 to 20.0; BASS-II-C04: 1.0 to 29.0 against 1.0 to 11.0), 8 where the catalog has a value and the tables have none (BASS maximum 40 from the record; CFI and FLEX flow 0 labelled 'team'). 22 rows differ exactly, 12 with rounding. A NOTE in `validation_report.json`, not a failure. For catalog to read; what to do with a difference is catalog's call.
2. `process_steps.json`, 25 reference items from six NASA documents (three new documents: NASA-STD-(I)-6001B interim, NASA-STD-6016C, JSC 29353B), every quote found verbatim by a second agent; each need has `informs_process_steps`; evidence packages and answer files have an added field `process` (steps, and the measures as quotations: "Measures are quoted from NASA documents for the case they describe. The team recommends nothing."). This is item 2 of the request of 09:55 on how fire-safety work runs: the data files only; the design-intent wording stays yours to decide.
3. `need_recorded_summary.csv`: per need, tests in scope in PSI's tables, with an outcome in a table cell, counted, with a video tied by two labels. For flame spread (P3): 133 solid-fuel tests of investigations whose stated purpose names it (PSI-25, 98, 100); 2 have an outcome in a table cell (a burn time; no spread rate); 2 are counted; the only spread-rate cells are two of Saffire-II (PSI-99), whose link verdict is `differs`.
4. `material_tests.csv` (23 materials, 67 rows) and `material_published.csv` (18 materials printed in three reference tables; one literal name match with the tables: Silicone).
5. `archive_summary.csv` and `archive_summary_totals.json`: 12,600 of 12,689 archives listed by range request; 12,662,354 members, of which 11,421,918 still images and 1,208,708 camera frames (.hobj); 10,668 text files.

## Why

So that `main` does not show stale-file failures after the merge, and so that you know what is new before the final pass over the submission text.

## Until then

The data role changes nothing in `ai/` or `data/insights/`.
