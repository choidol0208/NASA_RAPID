# Board

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. Written by pm only; other roles report through their status files.*

Last updated: 2026-11-14 11:00 KST

## What we are building

An English, static web dashboard on NASA PSI combustion data. The user picks a crewed-environment scenario; the dashboard shows which investigations are most relevant and why, what the data says about each fire-safety information need (with the PSI source for every statement), and where the data stops.

It is a research exploration tool. It does not give operational safety guidance, and anything the team computes is labelled as the team's computation, not NASA's conclusion (`AGENTS.md` section 5).

## Checkpoints (KST, Saturday 14 November)

| Time | Checkpoint | Done when |
|---|---|---|
| 12:00 | Public URL | ui has a deployed skeleton and its URL is in `coord/status/ui.md` |
| 14:00 | Catalog live | the 24 investigations are browsable at the public URL from real data |
| 17:00 | One scenario end to end | `lunar-habitat` works from selection to the list of gaps |
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
| D3 | data | Confirm the numbers behind the coverage story (request from pm) | 12:00 | todo |
| D4 | data | Say which outputs are stable for ui and pm to read; add what ui asks for | 12:30 | todo |
| D5 | data | Fact-check the 24 investigation cards against PSI text | 18:30 | todo |
| D6 | data | Final pass on `compliance/SOURCES.md` for the References field | 21:00 | todo |
| U1 | ui | Choose the stack, deploy a skeleton, publish the URL | 12:00 | todo |
| U2 | ui | Catalog and Investigation screens on real data | 14:00 | todo |
| U3 | ui | Scenario and Coverage screens | 17:00 | todo |
| U4 | ui | Source links, AI and team-computation labels, narrow screens | 19:00 | todo |
| U5 | ui | Screenshots and one GIF of the scenario flow for the project page | 21:00 | todo |
| P1 | pm | Collaboration system, contracts for AI outputs | 11:15 | doing |
| P2 | pm | `data/insights/cards.json`: 24 investigation cards | 14:00 | todo |
| P3 | pm | Rule-based ranking and `data/insights/scenarios.json` for `lunar-habitat` and `iss-class` | 16:30 | todo |
| P4 | pm | Review scenario text against sources; `pressurized-rover` if time allows | 19:00 | todo |
| P5 | pm | Seven slides and the project page text | 21:30 | todo |

## If a checkpoint is at risk, cut in this order

1. `pressurized-rover` scenario
2. Side-by-side comparison of two investigations
3. Tables that are not test-level (they stay in the Catalog only)
4. GIF (use still screenshots)

Never cut: the Catalog, the `lunar-habitat` and `iss-class` scenarios shown against each other, source links on every statement.
