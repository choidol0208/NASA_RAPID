# Board

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. Written by pm only; other roles report through their status files.*

Last updated: 2026-11-14 11:10 KST

## What we are building

An English web dashboard on NASA PSI combustion data. The user describes a crewed environment, roughly or precisely ("moon", "ISS cotton fabric", "30% O2 at 10.2 psi"). The dashboard shows which investigations are most relevant and why, what the recorded tests can say about each fire-safety information need (with the PSI source for every statement), and where the data stops.

It is a research exploration tool. It does not give operational safety guidance, and anything the team computes is labelled as the team's computation, not NASA's conclusion (`AGENTS.md` section 5).

## What exists (on `main` at 11:10)

| Part | Where | By |
|---|---|---|
| PSI records and the 22 experimental tables | `data/psi/` | data |
| Pipeline: 1,867 tests in standard variables, 7 information needs, capability matrix | `pipeline/`, `data/pipeline/` | data |
| Catalog: 24 investigations, 41 test configurations | `data/catalog/` | ui |
| Catalog filter: rule-based ranking with presets, assumptions and warnings; 22 validation scenarios pass | `scoring/`, `validation/` | ui |
| Collaboration system | `coord/`, `contracts/` | pm |

Not built yet: the dashboard, the model-written explanations, the demo deck, the submission text.

## Checkpoints (KST, Saturday 14 November)

| Time | Checkpoint | Done when |
|---|---|---|
| 12:30 | Public URL | ui has a deployed skeleton and its URL is in `coord/status/ui.md` |
| 14:30 | Ranking live | a query typed into the public page returns the ranked investigations with assumptions and warnings |
| 17:00 | One scenario end to end | "lunar habitat" goes from query to ranking, to the needs with sources, to the gaps |
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
| D3 | data | Confirm the coverage numbers and publish a coverage grid (request from pm) | 12:30 | todo |
| D4 | data | In status: which outputs are stable to read; add what ui asks for | 12:30 | todo |
| D5 | data | Check model-written summaries against the PSI text | 18:30 | todo |
| D6 | data | Final pass on `compliance/SOURCES.md` for the References field | 21:00 | todo |
| U0 | ui | Catalog, catalog filter, validation scenarios | — | done |
| U1 | ui | Choose how the dashboard is served, deploy a skeleton, publish the URL | 12:30 | todo |
| U2 | ui | Query box wired to `scoring.scorer.rank`: results, assumptions, warnings, source links | 14:30 | todo |
| U3 | ui | Needs view from `capability_matrix.csv` and Coverage view from the pipeline | 17:00 | todo |
| U4 | ui | Labels (AI-generated, team computation, not safety guidance), narrow screens | 19:00 | todo |
| U5 | ui | Screenshots and one GIF of the scenario flow for the project page | 21:00 | todo |
| P1 | pm | Collaboration system and contracts | 11:15 | done |
| P2 | pm | Agree with ui what model-written text the dashboard shows and in what shape | 12:30 | doing |
| P3 | pm | `data/insights/`: investigation summaries and explanations for the preset scenarios, every statement with its source | 16:30 | todo |
| P4 | pm | Review every model-written statement against its source | 19:00 | todo |
| P5 | pm | Seven slides and the project page text | 21:30 | todo |

## If a checkpoint is at risk, cut in this order

1. Free-text explanations for arbitrary queries (keep them for the presets)
2. Side-by-side comparison of two investigations
3. GIF (use still screenshots)
4. Coverage view as a chart (show it as a table)

Never cut: the ranking with its assumptions and warnings, the lunar-habitat scenario shown against the ISS one, source links on every statement.
