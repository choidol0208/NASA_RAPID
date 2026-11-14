---
from: pm
to: ui
opened: 2026-11-14 14:53 KST
needed_by: 18:30
closed: false
---
# Three output blocks information to consider constraints

## What I need

*AI-generated (Claude Code), pm role.*

The human lead describes the main use as: a user says what equipment they want to develop, and the page returns (1) the information they need, (2) the points to consider, (3) the constraints. The page already computes all three; this request is about saying them in those words. After requests 1306 and 1500, where they overlap do the smaller change.

Within the result, make these three blocks recognisable (a heading or a sub-label each; wording is yours):

1. **Information you need**: the closest NASA investigations with their checked summaries, the raw-data line and the export (the "Find" and "Compare" parts).
2. **Points to consider**: for each fire-safety need that applies (flammability limit, ignition, flame spread, extinction conditions, combustion products, smoke), what the recorded tests say for this environment, with the need's `reading`.
3. **Constraints**, in two parts kept visibly apart:
   - "Criteria in NASA documents": the reference items behind each need from `data/pipeline/need_references.csv` (59 items: acceptance criteria, requirements, definitions), quoted with document title and link, for example NASA-STD-6001 Test 1's 15 cm burn-length criterion. Label them as what the NASA document states. The page does not judge any test against them and does not turn them into requirements of its own; data asked earlier not to compare BASS-II CO readings with the cabin exposure limits.
   - "Limits of the evidence": where the evidence stops (the section from request 1306) and the warnings (no partial-gravity data, pressure not in the table).

If catalog adds a list of query words that were not understood (request 1505 to catalog), print it near "How your input was read", for example: "No match for 'battery enclosure'; showing general evidence for this environment." 

## Why

A user who types "smoke detector for a lunar rover" should find the three things they asked for under those names. "Constraints" must not read as requirements issued by this tool (`AGENTS.md` section 5), which is why the two parts stay apart and each criterion carries its NASA source.

## Until then

pm delivers `cards.json`, `scenarios.json` and `evidence_map.json` and announces the push.
