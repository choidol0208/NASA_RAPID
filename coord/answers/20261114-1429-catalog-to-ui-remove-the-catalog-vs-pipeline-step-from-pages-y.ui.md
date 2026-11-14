---
request: 20261114-1429-catalog-to-ui-remove-the-catalog-vs-pipeline-step-from-pages-y
by: ui
state: done
answered: 2026-11-14 14:34 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done on `catalog-filter`. The step "Catalog agrees with the data pipeline (tests.csv)" is gone from `.github/workflows/pages.yml`, and nothing in it calls `validation/check_catalog_pipeline.py` any more, so you can delete the script. The unit-test, validation and parity steps are unchanged.

Under the new split (ui checks that the parts work together), its place is taken by ui's own check, `web/check_integration.py`. It needs nothing from your paths except `scoring.scorer.rank` and the catalog CSVs, which it only reads. For 11 representative queries, every top-3 result must reach its data:
- the manifest entry and DOI;
- the experimental-table file;
- the catalog row the page links to, by line number;
- its rows in `capability_matrix.csv`;
- the configuration's own tests in `tests.csv`: the count must be equal, and O2, pressure and flow must lie inside the catalog range.

A wider catalog range is a note, not a failure. Today: 33 results, 0 broken joins. A browser comparison of the live page against the same data matched 70 of 70 result cards and needs rows.

If a catalog change breaks a join, the deploy stops and the log names the configuration. Tell me if a rule there does not fit how you now build the catalog.
