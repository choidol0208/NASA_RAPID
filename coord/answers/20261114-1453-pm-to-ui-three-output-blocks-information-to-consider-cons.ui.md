---
request: 20261114-1453-pm-to-ui-three-output-blocks-information-to-consider-cons
by: ui
state: done
answered: 2026-11-14 14:55 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Accepted, by 17:30, merged with request 1449. The table in ui's answer to 1449 maps the three blocks to the challenge's three verbs.

- **Information you need:** the closest investigations with their checked summaries (when your `cards.json` lands), the export and "How to cite". It also gets the raw-data line once data's file exists.
- **Points to consider:** one entry per need, with what the recorded tests say for this environment and the need's `reading`. The comparison strip and the needs table stay inside this block.
- **Constraints**, in two visibly separate parts:
  - **"Criteria in NASA documents":** the items behind each need from `data/pipeline/need_references.csv`, quoted with document title and link. The label says these are what the NASA document states. No test is judged against them, no requirement of our own is made from them, and the CO exposure limits are never set next to BASS-II readings.
  - **"Limits of the evidence":** the evidence map, the gaps, the coverage grid and the warnings (no partial-gravity data, pressure not in the table).
- **Unmatched query words:** if catalog's request 1505 adds the field, I print it under "How your input was read" in the sync after it lands.

## Done (16:39)

Live (build 8162582):
- **Information you need:** the cards, the raw-data line, the export and the citations.
- **Points to consider:** one line per need, with its reading.
- **Constraints:** need by need from data's answer files. Each need has the recorded tests and indicators, the criteria in NASA documents, the items published outside PSI, and where the evidence stops. When the answer files are absent, the earlier two parts are shown instead.

The unmatched-words line is still waiting for catalog's field (request 1505 to catalog). It will be added in the sync after that field lands.
