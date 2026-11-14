# Brief: data role

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. Written by pm.*

You already built the pipeline on `data-pipeline`. Nothing about how it works changes. What is new is that two other sessions now depend on its outputs, and that you coordinate with them through `coord/` instead of through your human.

## Start here

1. Merge `origin/main` into `data-pipeline` (`python3 scripts/coord.py pull` after you have `scripts/coord.py`; the first time, `git fetch origin && git merge --no-edit origin/main`). If `compliance/*.md` conflicts on this first merge, keep the rows from both sides.
2. Write `data` into `.role` at the repository root.
3. Read `AGENTS.md` section 9, `coord/README.md`, `coord/board.md` and `contracts/README.md`.
4. `python3 scripts/coord.py brief`, then answer what is in your inbox.

## You own

`pipeline/`, `data/psi/`, `data/derived/`, `data/pipeline/`, `reports/`, `scripts/fetch_psi.py`, `scripts/profile_tables.py`, `scripts/build_data_map.py`. Your branch is `data-pipeline`.

## What the others need from you

| Id | What | Due (KST) |
|---|---|---|
| D3 | Confirm or correct the coverage numbers pm asked about (see your inbox) | 12:00 |
| D4 | In your status, list which outputs and columns are stable. Add what ui asks for through requests (for example a JSON copy of a CSV, or a per-investigation index) | 12:30 |
| D5 | Check the 24 investigation cards in `data/insights/cards.json` against the PSI text and report errors through a request to pm | 18:30 |
| D6 | Make `compliance/SOURCES.md` complete for the References field of the submission | 21:00 |

## Things only you can judge

- Whether a number shown on the dashboard is traceable to a source cell. If ui or pm derive something from your files in a way that breaks your "nothing is estimated" rule, say so in a request.
- The scope and required variables of the seven needs. They drive the Scenario screen, so tell pm before you change a need id or a status value.

## When you change an output

Adding columns or files: just note it under "Published for others" in your status. Renaming or removing a column, changing a unit, a status value, an id or a path: request to `all` first.
