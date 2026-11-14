---
request: 20261114-1503-data-to-pm-review-a-proposal-answer-safety-type-questions-w
by: pm
state: accepted
answered: 2026-11-14 15:05 KST
---
# Answer

*AI-generated (Claude Code), pm role. The team lead on the pm side is told of this answer and may change it before the 19:00 freeze.*

**Go, with changes.** Build A and B. B's fixed sentences are shown inside the existing Constraints block. No model wording, no new input box and no new card today.

**1. Go or no.** Go for steps A and B. At 15:05 the human lead on the pm side asked that the constraints for a piece of equipment come from the PSI data as well as from NASA documents. Your four rungs are that, in order.
- Step C (free question text): not before the freeze. The query box, the presets and catalog's `not_understood` note cover it.
- Step D (model wording): no. The fixed sentences are shown as they are. An answer to a safety-type question is where a reworded hedge does the most harm, and no review time is left for it.
- Step E: no new card. ui places the rungs in the Constraints block (pm's request 1505 to ui): rungs 1 and 2 under "What NASA's recorded tests showed", the frame under "Criteria in NASA documents", rung 3 under a new part "Published by NASA and the investigators (not in PSI's experimental tables)", rung 4 under "Where the evidence stops". Please send ui the field names in a request of your own once B's shape is fixed.

**2. Decision 13:05 changes as follows** (recorded in `coord/decisions.md`, 15:10). Published results may be shown in rung 3 for any topic, partial gravity included, on these conditions:
- each one is a quoted reference item with its document, place and `access` level on screen (an `abstract_only` or `read_by_teammate` item says so);
- values are those of the item, cell for cell, with no arithmetic by the team: no difference, average, interpolation or trend;
- they are never added to a count, never drawn as PSI tests and never used to clear a gap code;
- the heading says they are not in PSI's experimental tables.

What stays from 13:05: no prediction for an untested condition, results at 0 g and 1 g are not called bounds, and the project is not presented as a partial-gravity result.

**3. Scope.** Both presets and all six needs if one piece of code writes them all. Otherwise in this order: `lunar_habitat` S1, P1, P3; `iss` P1, S1, D1; then the rest. An answer file whose rungs 1 to 3 are empty is still wanted: its top line is the finding.

**4. Wording conditions.**
- The top line never contains safe, unsafe, acceptable, sufficient, adequate or recommended, and gives no spread rate or limit for a condition without a test. "Not judged here." first is right.
- Each line of rung 2 states how its condition differs from the one asked (for example "at 21% oxygen, not 30% or more"), and the rung says once that a neighbouring condition is not evidence for this one.
- Rung 4 keeps your wording "has not been found in these sources", with the date of the search where there is one (Saffire IV to VI: not in PSI on 14 November 2026, 12:05 KST).
- On the page and in the pitch this is "what is known for this environment, and how well", not "answers to safety questions".
- `check.py` checks every number and quote of an answer file against the reference item or the CSV row it cites, as it does for the packages.

**5. Timing.** A at 16:15 and B at 17:30, as you propose. If B is not on `data-pipeline` by 17:45, the write-up describes it as the next step and the page keeps the indicator list of request 1505. The 17:30 freeze of the three CSVs stands.

**For the AI-use record.** The direction came from the human leads (data side: answer safety-type questions; pm side: constraints from the data too). The four-rung structure was proposed by the data role's AI session and reviewed by pm's AI session.
