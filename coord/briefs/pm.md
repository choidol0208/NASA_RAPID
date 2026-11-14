# Brief: pm role

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon.*

You lead, integrate, and produce the model-written layer of the product.

## You own

Listed in `coord/roles.json` under `pm`. Your branch is `main`.

## On every sync

`coord/README.md`, section "What pm does on every sync". In short: `python3 scripts/coord.py integrate`, push `main`, update `coord/board.md`, answer requests, decide and record, cut scope when a checkpoint is at risk.

## Tasks

| Id | What | Due (KST) |
|---|---|---|
| P2 | `ai/build_cards.py` and `data/insights/cards.json`: 24 investigation cards. Conditions and counts computed from `data/pipeline/tests.csv`; summary and key points written by a model from `data/psi/catalog/` only, each key point with its source | 14:00 |
| P3 | `ai/build_scenarios.py` and `data/insights/scenarios.json` for `iss-class` and `lunar-habitat`: rule-based score from `capability_matrix.csv`, `need_tests.csv` and `tests.csv`; evidence level per need; gaps | 16:30 |
| P4 | Review every model-written statement against its source; set `reviewed_by`. `pressurized-rover` if time allows | 19:00 |
| P5 | Seven slides (limit is seven including the title slide) and the English text for each field of the project page, from `compliance/` | 21:30 |

## Constraints

- A model writes text; it never produces a number, a score or a level.
- A statement without a source is dropped, not softened.
- Which model writes the text, and through which provider, is the human lead's choice (`AGENTS.md` sections 4 and 8). Record it in `compliance/AI_USAGE_LOG.md` under "제품 안에서 동작하는 AI" before the first run.
