# Brief: ui role

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. Written by pm.*

You already built the catalog, the catalog filter and its validation on `catalog-filter`. Nothing about how they work changes. What is new: your branch is now merged into `main` on every pm sync, the data role's pipeline is next to it, and you coordinate with the other two sessions through `coord/` instead of through your human. Your next piece is the dashboard.

## Start here

1. Commit your work, then merge `origin/main` into `catalog-filter` (the first time: `git fetch origin && git merge --no-edit origin/main`; afterwards `python3 scripts/coord.py pull`). If `compliance/*.md` conflicts on this first merge, keep the rows from both sides.
2. Write `ui` into `.role` at the repository root.
3. Read `AGENTS.md` section 9, `coord/README.md`, `coord/board.md`, `coord/decisions.md` and `contracts/README.md`.
4. `python3 scripts/coord.py brief`, then answer what is in your inbox.

## You own

`data/catalog/`, `scoring/`, `validation/`, `presentation/`, `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`, the dashboard (`app/` or `web/`, your choice) and `.github/`. Your branch is `catalog-filter`.

## Tasks

| Id | What | Due (KST) |
|---|---|---|
| U1 | Decide how the dashboard is served, deploy a skeleton to a public URL, write the URL and the choice in your status | 12:30 |
| U2 | A query box wired to `scoring.scorer.rank`: results 1 to 3 and the full ranking, the assumptions, the warnings, a link to each PSI page and DOI | 14:30 |
| U3 | For the ranked investigations, the needs view (what the recorded tests can say about each of the seven needs, from `data/pipeline/capability_matrix.csv` and `pipeline/spec/needs.json`) and the Coverage view (tests by oxygen, pressure and fuel phase, from the pipeline) | 17:00 |
| U4 | Labels, narrow screens | 19:00 |
| U5 | Screenshots and one GIF of the flow in the dashboard folder under `media/` | 21:00 |

The moment the demo is built around: ask about the ISS, then about a lunar habitat, and watch the evidence go from well covered to thin.

## Constraints on the dashboard

- Everything visible is in English.
- It opens from a public link with no login, and keeps working through judging, which runs into January. If the host puts idle apps to sleep, say so in your status so pm can plan the demo around it.
- No call to a paid service when a page loads, unless the human lead has decided otherwise (`AGENTS.md` section 8). No API key in the page or the repository.
- Every number and statement links to its source: the PSI page, a DOI, or the source file and row.
- Scores, rankings and counts carry a visible note that they are the team's computation, not NASA's conclusion. Text with `ai_generated: true` carries a visible label and shows whether it was reviewed.
- A line on the page says this is a research exploration tool and not operational safety guidance.
- No NASA logo or mission insignia, nothing that suggests NASA endorsement.
- Results that used the scorer's fallback for unreported atmosphere show the `fallback` warning. Counts on the Coverage view come from the pipeline and never fill in an empty cell (`coord/decisions.md`).
- Before adding a dependency, font or icon set: check the license and add the row to `compliance/SOURCES.md` at that moment.

## Working with the other two

- The data role's outputs are described in `contracts/README.md` and `pipeline/README.md`. If you want one in another shape (JSON, an index, a coverage grid), open a request to `data`.
- The pm role writes the model-generated text (investigation summaries, the explanation under a ranking result, the gaps). Say in your answer to pm's open request what text you want and in what shape; until the files exist, show "not available yet" in those places.
- A repository setting (GitHub Pages, a workflow permission, a secret): request to `pm`, whose session has admin rights.
- If you change a catalog column, a field of the `rank()` output, a preset id or a warning code: request to `all` first.
