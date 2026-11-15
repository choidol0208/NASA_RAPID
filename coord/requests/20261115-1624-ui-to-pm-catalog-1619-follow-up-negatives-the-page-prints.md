---
from: ui
to: pm
opened: 2026-11-15 16:24 KST
needed_by: 17:30
closed: false
---
# Catalog 1619 follow-up: negatives the page prints from pm and data wording files; team score in scenarios.json

*AI-generated (Claude Code), ui role.*

## What I need

ui did catalog's request 1619 at 16:24: "match score", shorter AI tags, and positive notes in the ui sections. See the answer `coord/answers/20261115-1619-catalog-to-ui-human-lead-16-18-rename-team-score-to-match-scor.ui.md`.

Some sentences of the same kind remain. The page prints them word for word from files that you own or that the data role owns. One decision or wording from you:

1. **`data/insights/scenarios.json`** (yours): "team score" appears 8 times. On the ISS page it shows twice, in the "Other investigations" notes: "Listed because its team score is level with or close to the results shown …". The new name is "match score".
2. **`docs/raw_data_design/pile_wording.md`** (yours). `web/raw_piles.py` fills these templates as written:
   - Section 10, the small print of the three piles: "A research exploration tool, not safety guidance. Counts and the reading order are the team's computation, not NASA's conclusions. …"
   - Section 3, header: "… The counts are the team's computation from PSI's file listing and NASA's tables, not NASA's conclusions."

   Send me the new wording, or say "ui may word it". In that case I would use "Counts and the reading order are Team RAPID's computation from PSI's file listing and NASA's tables." I would keep "Nothing here says what happens at a condition that was not tested", because it is the limit of the block and not a disclaimer.
3. **The data role's `results_by_need.json` `_meta`**. The results-first section prints it as its small print:
   - `team_output`: "… they are not NASA's conclusions."
   - `not_research_guidance`: "A research exploration tool, not safety guidance. Read by an AI agent; not checked by a person."

   Data said at 15:55 that no further data change is coming. If the data role should not change its file now, I can print a positive line of my own instead: "Groups, order, headlines and counts are Team RAPID's computation. Read by an AI agent." Say which.

## Why

The human lead's rule of 16:18, as catalog passed it on: keep the AI labels and one §5 statement, and drop sentences whose only job is to say what the tool is not. These are the last such sentences inside the ui sections, and ui does not own their wording.

## Until then

They stay as they are. Nothing is wrong in them, and they only repeat the footer.
