# Board

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. Written by pm only; other roles report through their status files.*

Last updated: 2026-11-14 13:10 KST

## What we are building

The team's original topic (decision 13:05). An English web dashboard on NASA PSI combustion data that does four things: classifies and summarizes the investigations; extracts the fire-safety elements from their test tables; for what the user wants to build ("moon base", "ISS cotton fabric"), gives the points to consider with the recorded evidence; and says whether the data are sufficient and what is missing.

The pitch in one sentence: tell it what you want to build on the Moon or Mars, and it tells you what NASA's microgravity fire tests say you should consider, and where that evidence stops.

It is a research exploration tool. It does not give operational safety guidance, and anything the team computes is labelled as the team's computation, not NASA's conclusion (`AGENTS.md` section 5).

## What exists (on `main` at 11:10)

| Part | Where | By |
|---|---|---|
| PSI records and the 22 experimental tables | `data/psi/` | data |
| Pipeline: 1,867 tests in standard variables, 7 information needs, capability matrix | `pipeline/`, `data/pipeline/` | data |
| Catalog: 24 investigations, 41 test configurations | `data/catalog/` | ui |
| Catalog filter: rule-based ranking with presets, assumptions and warnings; 22 validation scenarios pass | `scoring/`, `validation/` | ui |
| Collaboration system | `coord/`, `contracts/` | pm |

Live: https://choidol0208.github.io/NASA_RAPID/ (ranking, needs view, coverage view, labels).

Not built yet: the model-written explanations, an attention-grabbing first screen (organizer feedback, 11:30), the demo deck, the submission text.

## Checkpoints (KST, Saturday 14 November)

| Time | Checkpoint | Done when |
|---|---|---|
| 12:30 | Public URL | ui has a deployed skeleton and its URL is in `coord/status/ui.md` |
| 14:30 | Ranking live | a query typed into the public page returns the ranked investigations with assumptions and warnings |
| 17:00 | One scenario end to end | "lunar habitat" goes from query to the ranking with summaries, to what to consider with sources, to the picture of where the evidence stops |
| 19:00 | Feature freeze | bug fixes and wording only after this |
| 21:30 | Submission rehearsal | every link opens logged out; form fields drafted in English |
| 22:30 | Submit | "Project Submitted for Judging" shown on the team page |

Official close is Sunday 15 November 23:59 KST. Sunday is for corrections only.

Human-only items (`AGENTS.md` section 7): Seoul check-ins 11:00–12:00, 16:00–18:00, 19:00–22:00 today; one team meeting; pressing Submit.

## Tasks

Status values: todo, doing, done, cut.

| Id | Role | Task | Due | Status |
|---|---|---|---|---|
| D1 | data | Fetch 24 investigations and 22 experimental tables | — | done |
| D2 | data | Spec-driven pipeline: tests, values, 7 needs, capability matrix | — | done |
| D3 | data | Confirm the coverage numbers and publish a coverage grid (request from pm) | 12:30 | done |
| D4 | data | In status: which outputs are stable to read; add what ui asks for | 12:30 | done |
| D5 | data | Check model-written summaries against the PSI text | 18:30 | todo |
| D6 | data | Final pass on `compliance/SOURCES.md` for the References field | 21:00 | doing |
| U0 | ui | Catalog, catalog filter, validation scenarios | — | done |
| U1 | ui | Static site in `web/` on GitHub Pages: deploy a skeleton, publish the URL | 12:30 | done |
| U2 | ui | Query box wired to `scoring.scorer.rank`: results, assumptions, warnings, source links | 14:30 | done |
| U3 | ui | Needs view from `capability_matrix.csv` and Coverage view from the pipeline | 17:00 | done |
| U4 | ui | Labels (AI-generated, team computation, not safety guidance), narrow screens | 19:00 | done |
| U5 | ui | Screenshots and one GIF of the scenario flow for the project page (after the differentiator decision) | 21:00 | todo |
| U6 | ui | "Where the evidence stops" section with the oxygen-axis picture; lede and section names for the three promises (request 1310) | 16:30 | todo |
| P1 | pm | Collaboration system and contracts | 11:15 | done |
| P2 | pm | Agree with ui what model-written text the dashboard shows and in what shape | 12:30 | done |
| P3 | pm | Design of the AI layer (methods beyond a language model alone), then `data/insights/`: summaries and scenario explanations, every statement with its source | 16:30 | doing |
| P4 | pm | Review every model-written statement against its source | 19:00 | todo |
| P5 | pm | Seven slides and the project page text | 21:30 | todo |

## If a checkpoint is at risk, cut in this order

1. Free-text explanations for arbitrary queries (keep them for the presets)
2. Side-by-side comparison of two investigations
3. GIF (use still screenshots)
4. Coverage view as a chart (show it as a table)

Never cut: the ranking with its assumptions and warnings, the lunar-habitat scenario shown against the ISS one, source links on every statement.
