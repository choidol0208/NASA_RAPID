---
from: data
to: all
opened: 2026-11-15 09:27 KST
needed_by: 13:00
closed: false
---
# One PSI value reaches the page by two roads (pipeline and catalog): what the code shows, and a full comparison the data role will add

## What I need

*AI-generated (Claude Code), data role. Asked for by the data side's human lead: keep the data structures of the pipeline and of the catalog consistent, share the problem here, start with what costs least, and do not overlap with work already under way.*

**Nothing from anyone before 13:00 except a reading and, from catalog, a yes or no to point 3.** This note shares what a trace of the code found (an AI agent followed every script from `scripts/fetch_psi.py` to `web/build.py`; no person checked it).

**The finding.** A PSI value reaches the page by two roads that do not meet:
- Road A (data): PSI table -> `pipeline/run.py` -> `tests.csv` and the scenario files -> counts, test lists, gaps, the three piles. `pipeline/check.py` (73 checks) guards this road only.
- Road B (catalog): PSI table and record -> `scripts/build_catalog.py` (its own parsing, some values typed in the script) -> `data/catalog/configurations.csv` -> `scoring/scorer.py` and `web/scorer.js` -> the ranking and its "why" line.
- The oxygen, pressure and flow ranges of an investigation are therefore computed twice. What compares them today: `web/check_integration.py` for the top three results of 11 fixed queries (fails only if the catalog range does not contain the `tests.csv` span); `validation/check_catalog_sources.py` compares the catalog with the raw tables, not with the pipeline, and is not in CI. Nothing in `pipeline/check.py` or `ai/check_all.py` compares the two. `test_count` of a configuration and the rows of `tests.csv` have the same partial cover.
- Scenario nominal values exist twice as well (`scoring_config.json` presets and `pipeline/spec/scenarios.json`); `run.py` writes a mismatch list into `run_report.json` (empty today) and nothing fails on it.
- Small things seen on the way: `web/check_integration.py` line 173 tests the flag `range_in_source_midpoint_used`, which no longer exists anywhere (removed 14 November, 14:40); `raw_values.csv` has no generator in the repository (a verifier exists); several documents name files that are gone (`scripts/build_data_map.py`, `validation/check_catalog_pipeline.py`).

**What the data role does about it, cheapest first, inside its own paths:**
1. Now: pm's build plan 0035 (question chain, file links, FLEX test sheets), which is the shared structure the page and catalog's `validation/raw_chain_recount.py` already build on. Smallest version first.
2. Then: a full comparison, all 41 configurations, of the catalog's oxygen, pressure, flow ranges and test counts with `tests.csv`, written by the data role to `data/pipeline/catalog_comparison.csv` (per configuration and variable: catalog value, source label, pipeline min and max, tests, and one of `equal`, `catalog_wider`, `catalog_narrower`, `pipeline_has_no_value`, `catalog_has_no_value`, `not_comparable`) and reported in `validation_report.json` as a NOTE, not a failure: the data role's checker will not go red on another role's file. It changes nothing in `data/catalog/` or `scoring/`.
3. **For catalog, a yes or no:** is the mapping from a configuration to its tests the one `web/check_integration.py` uses (`source_id` and the configuration's table)? If you have a better key, name it and I use it. The comparison is information for you: what to do with a difference is the catalog role's call.

Not proposed: changing where the catalog takes its numbers from. That is a structural change the day of the submission; if the leads want it, it is a decision for them.

## Why

A judge sees the ranking first and the counts second; if the two show different ranges for one investigation, neither is trusted. A full comparison costs the data role one small file and no one else anything.

## Until then

The data role works on 0035. The comparison file follows it; catalog's answer to point 3 can come any time before 13:00.
