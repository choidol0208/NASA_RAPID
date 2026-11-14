# Brief: pm role

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon.*

You lead, integrate, and produce the model-written layer of the product.

## You own

Listed in `coord/roles.json` under `pm`. Your branch is `main`.

## On every sync

`coord/README.md`, section "What pm does on every sync". In short: `python3 scripts/coord.py integrate`, run the checks (`python3 pipeline/run.py`, `python3 -m unittest scoring.test_scorer`), push `main`, update `coord/board.md`, answer requests, decide and record, cut scope when a checkpoint is at risk.

## Tasks

| Id | What | Due (KST) |
|---|---|---|
| P2 | Agree with ui what model-written text the dashboard shows and in what shape; update `contracts/README.md` | 12:30 |
| P3 | `ai/` and `data/insights/`: investigation summaries from `data/psi/catalog/` and explanations for the preset scenarios built on the output of `scoring.scorer.rank` and on `data/pipeline/capability_matrix.csv`. Every statement carries its source | 16:30 |
| P4 | Review every model-written statement against its source; set `reviewed_by` | 19:00 |
| P5 | Seven slides (the limit includes the title slide) and the English text for each field of the project page, from `compliance/` | 21:30 |

## Constraints

- A model writes text; it never produces a number, a score or a level.
- A statement without a source is dropped, not softened.
- Which model writes the text, and through which provider, is the human lead's choice (`AGENTS.md` sections 4 and 8). Record it in `compliance/AI_USAGE_LOG.md` under "AI that runs inside the product" before the first run.
