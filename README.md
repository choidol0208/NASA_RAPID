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

The product uses one language model: OpenAI **gpt-oss:20b** (Apache-2.0), run locally through Ollama before publishing. The public site never calls a model. Every model call goes through `ai/llm.py`, which refuses any other model before opening a network connection, checks the installed model digest, validates the reply against a JSON schema and logs each call to `ai/runs/` (call logs, not product content; the model's thinking text is never stored).

| File | What it does | Language model |
|---|---|---|
| `ai/config.py` | The one allowed model, its digest and the call defaults | none |
| `ai/llm.py` | Model guard, JSON validation and call log; `python3 -m ai.llm --smoke` runs three test calls | gpt-oss:20b |
| `ai/meta.py` | The AI-generation disclosure block and `write_json()` | none |
| `ai/evidence.py` | Splits the prose of the 24 PSI records into numbered sentences with exact character offsets, writes `data/insights/evidence.json` | none |
| `ai/resolve.py` | Resolves every source string used in `data/insights/` (`PSI-25.objective`, `doi:...`, `path#id`) to the real text or row, or fails | none |
| `ai/test_llm.py`, `ai/test_evidence.py` | Tests: `python3 -m unittest ai.test_llm ai.test_evidence` | none |

Text quoted from a PSI record is shown with the label of the record field it came from (for example "Stated hypothesis:"), as what the record states, not as a measured result.
