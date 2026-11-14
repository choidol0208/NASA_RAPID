---
from: pm
to: ui
opened: 2026-11-14 13:06 KST
needed_by: 16:30
closed: true
---
# First-screen decision keep the query box add Where the evidence stops

## What I need

*AI-generated (Claude Code), pm role.*

The human lead has decided (`coord/decisions.md`, 13:05): the project keeps its original topic and there is NO new first screen. Item 4 of request 1224 becomes the three items below, in priority order; stop wherever your time runs out.

1. **One section, "Where the evidence stops", in the results, after the needs.** This is the team's fourth goal and the one thing the page should make impossible to miss.
   - Picture: one oxygen axis with three lanes (gas flames, fuel droplets, solid fuels), one dot per recorded test, from `data/insights/evidence_map.json` (on `main` after pm's next push; add it to OPTIONAL in `web/build.py`). Read every count and label from the file; pm rebuilds it after data's audit fixes, so numbers such as the plotted total will change slightly.
   - On it: a marker "your atmosphere" at the oxygen value the query was read as (the same value shown under "How your input was read"), and per lane the number of recorded tests at or above that oxygen, from the file's points. For the solid lane the label with the highest recorded oxygen.
   - Under it: the existing gaps list with "data that would close it", and the count of tests the picture cannot place (no oxygen value, oxidizer-stream basis), with the reason.
   - Every dot or count links to its NASA table rows with your existing link helper. Mobile: the picture may scroll sideways inside its own box.
   - Fixed wording next to it: "Recorded tests in NASA's open PSI experimental tables. Counts and lanes are the team's computation." and "All tests were run in microgravity." Reference marks (the challenge text's 30% for a Moon base) are labelled with their source and are marks, not limits. No green-to-red colours, no safe or unsafe wording.
   - If data's reference item `SAF456.conditions` is on `main`, the five Saffire IV to VI conditions may appear as hollow marks labelled "published by NASA, not in PSI (checked 14 Nov 2026)"; they are never counted. If time is short, a sentence instead of marks.
2. **Say the topic in the first lines of the page.** Keep the title "Fire Evidence Explorer". Lede (edit the English as you see fit, keep the three promises in this order): "Tell us what you want to build: a spacecraft cabin, a Moon base, a rover. See which NASA microgravity fire investigations are closest, what their recorded tests say you should consider, and where the evidence stops." Label above the box: "What are you building, and where?"
3. **Name the result sections after the three promises, in this order:** "Closest NASA investigations" (ranking, with the summaries when `cards.json` lands), "What to consider, and what the recorded tests say" (the needs views), "Where the evidence stops" (item 1). No change to what they compute.

Then U5 (screenshots and the GIF) on the new order. Items 5 to 7 of request 1224 stay as they were, after these.

## Why

The organizers told the lead that the topic is interesting but nothing shows at once what is different. The team's own answer is its fourth goal: this tool says where the evidence stops and what data would close the gap. Today that is spread over a coverage table and a list; one picture in the result makes it visible in the first minute of the demo (query "lunar habitat": gas flames and droplets continue past the marker, the solid lane ends at 22.2%).

## Until then

pm merges data's audit fixes, rebuilds `data/insights/` (including `evidence_map.json`) and pushes; the push is announced in `coord/status/pm.md`. If the picture is not drawing by 16:30, say so in your status and pm supplies a static SVG of it for the page and the slides.
