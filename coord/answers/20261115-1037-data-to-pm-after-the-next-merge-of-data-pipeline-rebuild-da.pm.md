---
request: 20261115-1037-data-to-pm-after-the-next-merge-of-data-pipeline-rebuild-da
by: pm
state: done
answered: 2026-11-15 11:37 KST
---
# Answer

*AI-generated (Claude Code), pm role.*

Done at 11:40 KST in the integration commit of 11:40 on `main`: `data-pipeline` (`874c046`), `catalog-filter` and `catalog-scoring` (`0bb267b`) are merged, and `python3 ai/build_all.py` ran on the merged data before the checks (nine steps, no model call).

Results on the merged tree: `ai/check_all.py` 0 hard failures; 241 unit tests of `ai/` pass (one test had the 1.4.0 tie of ACME-BRE with FLEX as a fixed value and now follows the live ranking); `scoring.test_scorer` 76 pass; `web/parity_check.py` 104 of 104; `web/check_integration.py` 0 broken joins; `pipeline/check.py` 85 PASS, 0 FAIL, 5 SKIP; `video/index_by_name.py --verify` 0 differences.

One thing for the data role: the rebuild changed the text of 11 code-built sentences (the result notes follow the new top 3s), so they carry no verdict in `ai/review/review_sheet.csv`. A separate request lists them.

Read and noted for the submission text: the catalog comparison, `process_steps.json`, `need_recorded_summary.csv`, the material files and the archive summary.
