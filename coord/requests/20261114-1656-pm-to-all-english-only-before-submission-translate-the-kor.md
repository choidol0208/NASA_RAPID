---
from: pm
to: all
opened: 2026-11-14 16:56 KST
needed_by: 20:00
closed: false
---
# English only before submission: translate the Korean files you own by 20:00 (the human lead's decision)

*AI-generated (Claude Code), pm role.*

## What I need

**Each role: by 20:00, no file you own in the public repository holds Korean text that a reader must understand.** The competition's guide applies its English requirement to the submission page and to everything linked from it (`AGENTS.md` section 8). A rules check of the submission draft found 28 tracked files with Korean text. The human lead decided at 16:50: translate them. This is documentation work, so it may be done after the 19:00 freeze.

What counts:
- **Translate** everything a person reads to understand the project: READMEs, reports, data dictionaries, comments, labels, docstrings, slide text, spreadsheet headings.
- **May stay in Korean:** words the product matches as user input (the scorer's Korean keywords and the Korean queries in validation scenarios and tests). They are a feature: the page accepts Korean input. Wherever a reader meets one, put an English gloss next to it, for example `"달 기지"` (lunar base).
- **An internal aid that was never meant for a judge** may be taken out of the repository instead (kept on your own computer), if translating it is not worth the time.

Files found (lines with Korean / lines in the file):

**catalog** (13)
- `scripts/export_catalog_xlsx.py` (86/228), `scoring/README.md` (52/80), `data/catalog/data_dictionary.csv` (69/71), `data/catalog/README.md` (14/29): translate.
- `validation/scenarios.json` (40/159), `scoring/scoring_config.json` (151/992), `scoring/test_scorer.py` (4), `scoring/scorer.py` (5), `web/scorer.js` (4), `web/parity_check.py` (2), `validation/report.md` (4), `scoring/MODEL_BASIS.md` (1), `coord/status/catalog.md` (2): Korean input words may stay with an English gloss; translate anything else. `data/catalog/catalog.xlsx` is built by the export script, so rebuild it after the translation.
- Your answer file to pm 1453 (5 lines): add a gloss to the Korean example words.

**data** (7)
- `reports/indicators.html`, `reports/data-map.html`, their two templates, `reports/indicators_ko.json`, `data/derived/annotations_ko.json`, `reports/build_indicators_page.py` (1 line): the Korean team page. Translate it, or take it out of the repository; your call. If it stays, it must be English.

**ui** (1)
- `presentation/build_catalog_filter_slide.js` (4/148): translate; if the built slide file holds Korean text, rebuild it.
- Your answer file to catalog 1332 (1 line): add a gloss.

**pm** (5): `AGENTS.md`, `compliance/SOURCES.md`, `compliance/AI_USAGE_LOG.md`, one line in `coord/briefs/pm.md`, three in `docs/ai_layer_design.json`. A translation with a line-by-line check against the Korean is running now.

Two things change for everyone:
1. **`AGENTS.md` becomes English** as soon as its translation has passed the check (about 17:30). Same sections, same numbers, same rules; the phase line keeps its value. No Korean copy stays in the repository.
2. **The two compliance logs.** From now on, write new rows in English. pm replaces both files by their English translation at about 19:05, right after the freeze integration. After that, **merge `main` before you append a row**: the files use a union merge, and a row appended to an old copy would bring the Korean text back. pm checks both files for Korean after every integration.

When you are done, answer `done` and say what you translated and what you took out.

## Why

A submission with linked material in another language can be refused, and a judge who opens the repository must be able to read it.

## Until then

pm checks at the 19:00 freeze and again at 20:00 which tracked files still hold Korean (`git ls-files` scanned for Hangul) and writes the list into `coord/status/pm.md`.
