---
from: pm
to: ui
opened: 2026-11-14 15:05 KST
needed_by: 17:30
closed: false
---
# Constraints, third part: what NASA's recorded tests showed (from the indicators)

*AI-generated (Claude Code), pm role.*

## What I need

**A third part in the Constraints block, placed first: "What NASA's recorded tests showed".** The human lead asked at 15:05 that constraints come from the PSI data as well, not only from NASA documents. The data role already computes these values; they need a place of their own.

1. **Source:** the `indicators` list of each need in `data/pipeline/evidence/scenario_<id>.json` (on `main` now). For `iss`: P1 19 rows, P3 7, S1 11, D1 9. For `lunar_habitat`: S1 5 rows and no row for the other needs.
2. **One line per indicator row:** `label`; the group in plain words (material, geometry, fuel phase); the values (`min` to `max` with `median`, or the counts by category); `unit`; **`n_tests`**; the investigation with its link; and a link to the tests behind it (`data/pipeline/indicator_tests.csv`, or the NASA table rows you already link).
3. **Under each line, its `reading`, word for word.** It says what the value is and what it is not (for example: the lowest oxygen tested is not a flammability limit).
4. **Fixed sentence under the heading:** "Values computed by the team from NASA's PSI experimental tables. They describe the tests that were run. They are not limits, thresholds or requirements, and this page does not judge them against the criteria below."
5. **A need with no indicator row for the scenario** prints: "No recorded test at this condition gives a value for this need." Please do not leave it blank: the empty list is what the user needs to know.
6. **Keep data's rules.** No indicator value on the same line as a criterion from `need_references.csv` (above all the CO readings and the crew exposure limits). `compare_with` is shown as a pointer ("A published result exists: <reference>"), never as a comparison made by the page.

Constraints then has three parts, in this order: (a) What NASA's recorded tests showed, (b) Criteria in NASA documents, (c) Where the evidence stops.

**Later today, only if it lands in time.** data proposed (request 1503) one answer file per scenario and need, `data/pipeline/answers/<scenario>__<need>.json`, with fixed sentences in four rungs: recorded at the condition, recorded near it, published by NASA and the investigators, not known. pm answered go with changes: no new card, no model, no new input box. If those files are on `main` by 17:45:
- part (a) takes its sentences from rungs 1 and 2 (the indicator lines stay below them);
- a new part "Published by NASA and the investigators (not in PSI's experimental tables)" shows rung 3 between (b) and (c), each line with its document, place and access level;
- part (c) takes rung 4.

If they are later, items 1 to 6 stand as they are. data will send you the field names in its own request; this request does not depend on it.

## Why

The main use is: the user names the equipment, and the page returns information, points to consider and constraints. Today the constraints come from documents and from the gaps. The human lead wants the third source, the recorded data, shown as such. It is also the most direct use of NASA data on the page.

## Until then

pm is repeating an interrupted build of `data/insights/` from its start, on the current counts. `cards.json`, `scenarios.json` and `evidence_map.json` reach `main` only after an independent check, at about 16:30; pm says so in `coord/status/pm.md` if it is later. Before pushing, pm compares the field list in your status with `evidence_map.json` and tells you of any name that differs.
