---
request: 20261114-1656-pm-to-all-english-only-before-submission-translate-the-kor
by: catalog
state: done
answered: 2026-11-14 17:18 KST
---
# Answer

*AI-generated (Claude Code), catalog role.*

Done for all 13 catalog files; nothing taken out. No score changes. 38 tests, validation 35/35, parity 86/86, and the source check are all clean.

**Translated**
- `scoring/README.md` and `data/catalog/README.md`: rewritten in English, with the current numbers (38 tests, 35 scenarios, 86 parity queries, the sensitivity and source-check results).
- `scripts/export_catalog_xlsx.py`: every column meaning, group name, use and the README sheet are now in English. `data/catalog/data_dictionary.csv` and `catalog.xlsx` are rebuilt with no Korean left.
  - The dictionary column `meaning_ko` is now `meaning`. No code reads it.
- `validation/scenarios.json`: `why_ko` becomes `why` in English for all 35 scenarios and the stability block. `validation/run_validation.py` reads it.
- `scoring/scoring_config.json`: the 8 `label_ko` fields are removed. The page reads `label_en` only.
- `scripts/build_catalog.py`: one docstring line.

**Kept as Korean input, with an English gloss**
- `scoring/scoring_config.json`: the 138 Korean keywords and preset aliases are user input (the page accepts Korean queries).
  - A new map, `keywords._gloss_ko`, gives the English of each word.
  - The scorer does not read it; its `_about` explains this.
- `validation/scenarios.json`: the 4 Korean queries carry `query_en`. `validation/report.md` prints them as, for example, "달 기지 면직물 (Korean: lunar base cotton fabric)".
- `scoring/scorer.py`, `web/scorer.js`: the Korean words in the oxygen pattern are glossed in a comment (산소 = oxygen, 농도 = concentration), and so is the docstring example.
- `scoring/test_scorer.py`, `web/parity_check.py`: a gloss comment next to each Korean query.
- `scoring/MODEL_BASIS.md`, `scoring/README.md`, `coord/status/catalog.md`, my answer to 1453: a gloss next to each Korean word.

**One item left for the human lead**
- `scoring/scoring_config.json` `_about.generated_by` names the weight reviewer in Hangul, because the human lead asked for their name to be recorded.
- I have asked them for the Latin spelling they want. Until they answer, your Hangul scan will show this one line.

**Note on the compliance logs:** I will merge `main` before appending any new row to `compliance/SOURCES.md` or `AI_USAGE_LOG.md`, and write new rows in English.
