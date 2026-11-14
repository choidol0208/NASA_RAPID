# NASA_RAPID

A project for the 2026 NASA Space Apps Challenge (Seoul), challenge **Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data**.

*Work in progress during the hackathon (14–15 November 2026). Large parts of this repository are AI-generated with Claude Code; `compliance/AI_USAGE_LOG.md` lists what, and each generated file says so at the top.*

## What we are building

A web dashboard on NASA's Physical Sciences Informatics (PSI) combustion data. You pick a crewed-environment scenario, such as a spacecraft at sea-level atmosphere or a lunar habitat at elevated oxygen and reduced pressure. The dashboard then shows:

1. which of the 24 PSI combustion investigations are most relevant, and why;
2. what the data can and cannot say about each fire-safety information need (prevention, detection, suppression), with the PSI source of every statement;
3. where the data stops: the conditions no recorded test covers.

It is a research exploration tool. It is not operational safety guidance. Rankings, counts and evidence levels are computed by the team and are not conclusions by NASA.

## Repository map

| Path | Content |
|---|---|
| `pipeline/` | Spec-driven pipeline from the PSI experimental tables to standard variables and fire-safety information needs. See `pipeline/README.md` |
| `data/psi/` | PSI records and experimental tables as downloaded |
| `data/pipeline/` | Pipeline outputs: one row per test, capability matrix, tests per need |
| `data/catalog/` | Catalog of the 24 investigations and 41 test configurations |
| `scoring/`, `validation/` | Rule-based ranking (catalog filter) and its validation scenarios |
| `data/insights/` | Model-written summaries and explanations, each statement with its source |
| `contracts/` | Which file is produced by whom and read by whom |
| `coord/` | How the team's three working sessions coordinate |
| `compliance/` | Source list and AI usage log |

## Data and license

Data: NASA PSI Data Repository, https://psi.nasa.gov/ (records are CC0-1.0 where a license is stated; see `compliance/SOURCES.md`). PSI asks that each investigation be cited by its DOI; the DOIs are in `data/psi/manifest.json`.

Code and documents in this repository: Apache-2.0, see `LICENSE`.

## AI layer (`ai/`)

All code in `ai/` is AI-generated: it was written with an AI assistant (Claude Code) during the hackathon, and every file says so in its first line. Every data file it writes to `data/insights/` carries a disclosure block (`_meta`: which script built it, that the code was written with an AI assistant, and which language model, if any, ran at build time); the same blocks are collected in `data/insights/_meta.json`.

The product uses one language model: OpenAI **gpt-oss:20b** (Apache-2.0), run locally through Ollama before publishing. It writes at most three summary sentences per card (`data/insights/cards.json`) and nothing else; the public site never calls a model. Every model call goes through `ai/llm.py`, which refuses any other model before opening a network connection, checks the installed model digest, validates the reply against a JSON schema and logs each call to `ai/runs/` (call logs, not product content; the model's thinking text is never stored). Scenario text, gaps, counts, quotes and the evidence map are built by code from the NASA PSI tables and records and the data role's pipeline outputs.

Rebuild everything with one command, with no model call:

```
python3 ai/build_all.py                                   # every step in order, then ai/check_all.py
python3 -m unittest discover -s ai -p "test_*.py"         # the tests
```

`ai/build_all.py` runs, in this order, `ai/evidence.py`, `ai/build_baseline.py`, `ai/evidence_map.py`, `ai/apply_cards.py` (from the logged model output in `ai/runs/`), `ai/audit_catalog.py`, `ai/apply_review.py` and `ai/check_all.py`, sets `AI_NO_MODEL_CALLS=1` so that `ai/llm.py` refuses any model call, stops at the first failure and exits non-zero. The order matters: `ai/build_baseline.py` rewrites `cards.json` with the quoted cards, so the card and review steps must run after it.

| File | What it does | Language model |
|---|---|---|
| `ai/build_all.py` | Runs every build step in order, then `ai/check_all.py`; stops and exits non-zero on the first failure; checks that no run log in `ai/runs/` changed | none (forbids calls) |
| `ai/__init__.py` | Marks `ai/` as a package (`python3 -m ai.llm`, `ai.test_*`) | none |
| `ai/config.py` | The one allowed model, its digest and the call defaults | none |
| `ai/llm.py` | Model guard, JSON validation and call log; `python3 -m ai.llm --smoke` runs three test calls | gpt-oss:20b (only when called directly or by `ai/cards_llm.py`, `ai/apply_cards.py --repair`) |
| `ai/meta.py` | The AI-generation disclosure block and `write_json()` | none |
| `ai/resolve.py` | Resolves every source string used in `data/insights/` (`PSI-25.objective`, `doi:...`, `path#id`, `path#need/statement`) to the real text or row, or fails | none |
| `ai/evidence.py` | Splits the prose of the 24 PSI records into numbered sentences with exact character offsets; writes `data/insights/evidence.json` | none |
| `ai/templates.py` | The fixed wording of every code-built sentence (need statements, frames, gaps, result notes, quoted cards) | none |
| `ai/build_baseline.py` | Writes `data/insights/scenarios.json` (four scenarios: frame, one statement per need, gaps, result notes for the live ranking) from the pipeline CSVs and the data role's evidence packages, and the 24 quoted cards of `cards.json`; recounts every count and stops on any difference | none |
| `ai/evidence_map.py` | Writes `data/insights/evidence_map.json` for "Where the evidence stops": recorded tests on the oxygen axis per fuel lane, cited atmospheres, the team's ranges and the Saffire IV to VI samples as cited, uncounted marks | none |
| `ai/cards_llm.py` | Sends each record's numbered sentences to gpt-oss:20b and logs the raw candidate summaries in `ai/runs/` (prompts in `ai/prompts/`); never writes `data/insights/` | gpt-oss:20b |
| `ai/checks.py`, `ai/lint_patterns.py` | The code gates for model sentences (ids, verbatim quote, numbers, names, advice and prediction wording, misconception linter, length, sources, modality, hedges) and the checks for template text; quoted verbatim NASA text is not read by the wording gates, team and model text always is | none |
| `ai/apply_cards.py` | Gates the logged candidates, applies the reviewed removals of `ai/review/pm_prereview.json`, writes `cards.json` with quotes taken by code and the review sheet `ai/review/review_sheet.csv`; without `--repair` it only reads the logs | none by default; gpt-oss:20b only with `--repair` |
| `ai/audit_catalog.py` | Traces every number of the catalog text the page shows to a NASA source; writes `data/insights/catalog_trace.json` | none |
| `ai/apply_review.py` | Applies the verdicts of `ai/review/review_sheet.csv` (removes sentences marked `not`, `partly` or modality `no`; sets `reviewed_by`); writes `data/insights/quality.json` | none |
| `ai/check_all.py` | One check over everything in `data/insights/`: headers, disclosure blocks, append-only compliance files, evidence offsets, a second-path recount against `scenario_needs.csv` and a third path (evidence packages), every card and scenario statement re-gated, labels, sources, freshness | none |
| `ai/test_*.py` | Unit tests: `test_llm`, `test_evidence`, `test_checks`, `test_baseline`, `test_evidence_map`, `test_cards` | none |

`ai/review/README.md` explains the review sheet and how another session adds a reviewed removal to `ai/review/pm_prereview.json`.

Text quoted from a PSI record is shown with the label of the record field it came from (for example "Stated hypothesis:"), as what the record states, not as a measured result. Counts are recorded tests in NASA's open PSI experimental tables, the team's computation; they are not predictions, limits or safety verdicts.
