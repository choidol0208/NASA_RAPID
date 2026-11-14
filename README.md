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
