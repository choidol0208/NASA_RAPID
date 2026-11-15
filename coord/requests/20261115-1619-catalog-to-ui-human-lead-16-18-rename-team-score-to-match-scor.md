---
from: catalog
to: ui
opened: 2026-11-15 16:19 KST
needed_by: 17:30
closed: false
---
# Human lead 16:18: rename team score to match score on the cards and table; shorter AI tags

*AI-generated (Claude Code), catalog role.*

## What I need

The human lead (16:18) asked to rename "team score" and to take out negative statements that the page does not need. pm gets the shell notices, `how.html` and `data/insights/` (request 1619 to pm), so please change only `web/app.js` and the table header:

1. **"team score" → "match score".**
   - `web/app.js` line 244: `h("small", {}, "team score")` → `"match score"`.
   - `web/app.js` line 927: "(team scores …)" → "(match scores …)".
   - `web/index.html` line 190: the column header "Score" → "Match score".
   - A tooltip on the score is welcome: "How closely this investigation's recorded conditions match your question, weighted by how much each condition matters (0–100)."
2. **The result-card AI tag**, `web/app.js` line 257:
   - now: "catalog values AI-extracted, not yet checked"
   - new: "catalog values AI-extracted"

   The AI mark stays (AGENTS.md §4).
3. **The AI tag of model-written text**, line 197:
   - now: "AI-generated, not reviewed yet"
   - new: "AI-generated" (keep the "reviewed by …" variant as it is).
4. **The citation note**, line 682:
   - now: "…The page's own computations (scores, counts, bins) are the team's, not NASA's."
   - new: "…The page's own computations (match scores, counts, bins) are Team RAPID's."
5. **The B4 sentence above the cards:**
   - now: "A score orders the investigations for this question only; scores of different questions cannot be compared."
   - new, the same rule said positively: "A match score ranks the investigations within this question."

## Why

The human lead finds the repeated negatives ("not yet checked", "not reviewed yet", "not NASA's", "cannot be compared") make the tool read as less credible, and "team score" does not say what is measured. The score is a weighted similarity, so "match score" names it.

The AI marks and one statement that the computations are the team's stay, as AGENTS.md §4 and §5 require. pm keeps that statement once in the footer.

## Until then

Nothing breaks. The scorer's output field stays `score`; only the words on the page change.
