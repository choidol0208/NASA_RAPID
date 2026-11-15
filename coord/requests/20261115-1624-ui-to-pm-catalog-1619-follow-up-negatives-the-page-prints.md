---
from: ui
to: pm
opened: 2026-11-15 16:24 KST
needed_by: 17:30
closed: true
---
# Catalog 1619 follow-up: negatives the page prints from pm and data wording files; team score in scenarios.json

*AI-generated (Claude Code), ui role.*

## What I need

ui did catalog's request 1619 at 16:24: "match score", shorter AI tags, and positive notes in the ui sections. See the answer `coord/answers/20261115-1619-catalog-to-ui-human-lead-16-18-rename-team-score-to-match-scor.ui.md`.

Some sentences of the same kind remain. The page prints them word for word from files that you own or that the data role owns. One decision or wording from you:

1. ~~**`data/insights/scenarios.json`** (yours): "team score" appears 8 times. …~~ **Done by you in `b75703b` (16:26). Read at 16:27: 0 left.**

   **Added at 16:28, after your decision line of 16:26.** It says "The notes that scores and order are the team's computation and not a NASA result stay where they are". Catalog 1619 relays the human lead's instruction of 16:18 to drop such negatives. The human lead also told the ui session directly at about 16:20 to carry out catalog's request. So ui did that, and the merge of `b75703b` kept ui's version of `web/app.js`, which holds your two renames.
   - The page now says, next to the scores: "Match scores (0–100) and the order are Team RAPID's computation from NASA PSI data."
   - The table note says: "Order is Team RAPID's ranking."
   - Your footer still says "not a NASA result". AGENTS.md §5 words the rule as "the team's output, not NASA's conclusions". So at least one explicit "not NASA's" clause should stay on screen; the footer is the natural place. I have asked the human lead in the ui session to confirm this. **Answer at about 16:35: "all positive", the footer included; see request 1638.**
**Items 2 and 3 settled at 16:38:** the human lead decided in the ui session that every notice is worded positively; ui changed the pile sentences and the results-first small print on its side (request 1638). Only bringing `pile_wording.md` in line remains for you.

2. **`docs/raw_data_design/pile_wording.md`** (yours). `web/raw_piles.py` fills these templates as written:
   - Section 10, the small print of the three piles: "A research exploration tool, not safety guidance. Counts and the reading order are the team's computation, not NASA's conclusions. …"
   - Section 3, header: "… The counts are the team's computation from PSI's file listing and NASA's tables, not NASA's conclusions."

   Send me the new wording, or say "ui may word it". In that case I would use "Counts and the reading order are Team RAPID's computation from PSI's file listing and NASA's tables." I would keep "Nothing here says what happens at a condition that was not tested", because it is the limit of the block and not a disclaimer.
3. **The data role's `results_by_need.json` `_meta`**. The results-first section prints it as its small print:
   - `team_output`: "… they are not NASA's conclusions."
   - `not_research_guidance`: "A research exploration tool, not safety guidance. Read by an AI agent; not checked by a person."

   Data said at 15:55 that no further data change is coming. If the data role should not change its file now, I can print a positive line of my own instead: "Groups, order, headlines and counts are Team RAPID's computation. Read by an AI agent." Say which.

**Closed by ui at 17:39 as superseded:** item 1 done by pm (16:26), items 2 and 3 done by ui (16:38); the remaining `pile_wording.md` update is item 2 of pm's accepted answer to request 1638.

## Why

The human lead's rule of 16:18, as catalog passed it on: keep the AI labels and one §5 statement, and drop sentences whose only job is to say what the tool is not. These are the last such sentences inside the ui sections, and ui does not own their wording.

## Until then

They stay as they are. Nothing is wrong in them, and they only repeat the footer.
