---
request: 20261114-1656-pm-to-all-english-only-before-submission-translate-the-kor
by: data
state: done
answered: 2026-11-14 17:30 KST
---
# Answer

(what you did or decided, where the result is, or when it will be ready)

*AI-generated (Claude Code), data role.*

Taken out of the repository (the option you offered), not translated: `reports/indicators.html`, `reports/indicators.template.html`, `reports/indicators_ko.json`, `reports/build_indicators_page.py`, `reports/data-map.html`, `reports/data-map.template.html`, `data/derived/annotations_ko.json`, `scripts/build_data_map.py`. They were the team's internal Korean pages and their two builders; the builders have no input left, so they went too. All are in the git history.

A scan for Hangul over every tracked file under `pipeline/`, `data/pipeline/`, `data/derived/`, `reports/` and the data role's scripts now finds none. `pipeline/check.py` 59 of 59 PASS; no pipeline output changed.

Three places outside the data role's paths still name these files; yours to change:
- `coord/roles.json` lists `scripts/build_data_map.py` among the data role's paths.
- `docs/submission/submission_text.md` line 421 (pandas use: `reports/build...`) and line 436 (IBM Plex Sans KR font, used only by the removed pages; the font is no longer used by any data-role file).
- `compliance/SOURCES.md` rows for that font and for the pages, if any: mark as no longer in the repository when you replace the file by its translation.

New compliance rows from the data role will be in English and appended after merging `main`.
