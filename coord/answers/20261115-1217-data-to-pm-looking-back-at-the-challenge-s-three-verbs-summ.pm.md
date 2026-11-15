---
request: 20261115-1217-data-to-pm-looking-back-at-the-challenge-s-three-verbs-summ
by: pm
state: accepted
answered: 2026-11-15 15:13 KST
---
# Answer

*AI-generated (Claude Code), pm role.*

**Decision (pm, 15:13 KST, under the human lead's standing instruction of 09:33 to put the challenge's Objectives first; the human lead is told and can reverse it): yes, results lead.** For an environment and a fire-safety question the order becomes: what NASA's documents report (quoted, nearest stated conditions first) -> what NASA's rules say (quoted criteria) -> what the tables record -> where the record stops (the three piles) -> what is in the archive. The ranking of investigations stays as the way in, labelled as the team's computation. Sorry for the late answer: pm was paused from 12:36 to 15:00.

What pm does with it today:
1. `main` holds your results files since the integration of 15:08 (`ccfcbed`); `data/insights` was rebuilt.
2. The page: request to ui (opened now, by 18:30) for one block per question that renders `results_by_need.json`. If it is not on the page by 18:30, the results stay a data deliverable and the text says so.
3. The assistant: a lookup tool `published_results` is being added now, so that an answer about a fire-safety question quotes the results with their sources (quote facts; the order is your fixed rule; printed values only in the panel; no arithmetic with a criterion). It reads `results_by_need.json` and `findings.csv` and changes none of your files.
4. The submission text and the deck name the results layer with its counts from `results_summary.json`.

Two things pm asks of the data role, inside this answer rather than as new requests:
- The check of the submission text found 39 of the 69 entries of `pipeline/spec/references.json` without a row in `compliance/SOURCES.md`, and correction rows needed for rows 76 (NTRS 20110008636: authors and title) and 137 ("19 investigations"; `archive_summary.csv` holds 24). The list is in `docs/submission/submission_text.md`, "Open points", "For the team to do in the source log". pm appends rows built from what `references.json` itself records (document, address, access) and marks the terms as not read; where you have read a document's terms, please append the row with the terms, and correct rows 76 and 137, which are yours.
- Say in `coord/status/data.md` when no further data change is coming, so that the assistant's recorded conversations (which go stale when an answer file changes) are recorded once on the final files. The recording starts at about 16:40.
