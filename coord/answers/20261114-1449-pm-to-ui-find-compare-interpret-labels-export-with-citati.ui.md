---
request: 20261114-1449-pm-to-ui-find-compare-interpret-labels-export-with-citati
by: ui
state: accepted
answered: 2026-11-14 14:55 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Accepted, together with request 1453, as one structure (the smaller change where they overlap):

| Label (challenge verb) | Block (1453) | Sections inside |
|---|---|---|
| Find | Information you need | Closest NASA investigations, summaries, export and "How to cite" |
| Compare | Points to consider | the side-by-side strip, the needs table with each need's `reading`, recorded tests in the scenario range |
| Interpret | Constraints | "Criteria in NASA documents" (new, from `need_references.csv`) and "Limits of the evidence" (the evidence map, gaps, coverage grid, warnings) |

The challenge sentence goes under the title, quoted as the challenge text.

Times:
- **Item 1 (labels): by 16:00.**
- **Item 2 (export): by 16:30.**
  - The matched tests of the scenario as CSV, with source file, row and flags. `web/build.py` writes the CSV from your and data's files; values are copied, nothing is computed.
  - A link to `data/pipeline/evidence/scenario_<id>.json` at the built commit.
  - A "How to cite" block with the DOI of every investigation in the download, from `data/psi/manifest.json`.
- **Item 3 (raw-data line):** the same sync in which data's `raw_inventory` file reaches `main`. Nothing shows while it is absent.
