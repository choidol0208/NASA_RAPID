---
request: 20261115-1619-catalog-to-ui-human-lead-16-18-rename-team-score-to-match-scor
by: ui
state: done
answered: 2026-11-15 16:24 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done at 16:24 KST on `catalog-filter`. It is on the public page with the push that carries this answer.

1. **"match score".**
   - On the cards (`web/app.js`), in "At a glance" ("(match scores 75.2, 71.6, 73.6)") and in the table header ("Match score").
   - The tooltip you proposed is on the card score and on the table header, word for word.
2. **Card AI tag:** "catalog values AI-extracted". The "catalog checked by a person" variant is unchanged.
3. **Model-written text:** "AI-generated". The "AI-generated, reviewed by …" variant is unchanged.
4. **Citation note:** "…The page's own computations (match scores, counts, bins) are Team RAPID's."
5. **Note above the cards:** "Match scores (0–100) and the order are Team RAPID's computation from NASA PSI data. A match score ranks the investigations within this question."
   - Its first sentence repeated the footer's old negative sentence. I gave it the positive wording you proposed to pm for the footer, so the §5 statement also sits next to the scores.

**The same rule in other ui sections:**
- **The table note** now begins "Order is Team RAPID's ranking. Match scores within 3 points …"; "not a NASA result" is dropped.
- **The results-first note** now ends "they and the counts are Team RAPID's computation. Printed values are quoted as written, and criteria are quoted next to them, not applied to them." "Not safety guidance." is dropped.

**Checked on the local build:**
- `build.py` exit 0, `check_integration.py` 0 broken joins.
- For "lunar habitat" and "ISS", with every disclosure open: no "not yet checked", "not reviewed yet" or "cannot be compared" on the page, and no console error.

**Left to their owners (told to pm in request 1624):**
- **The footer notice** (index.html line 211): pm, your request to pm.
- **Two "team score" sentences** in the "Other investigations" notes of the ISS query ("Listed because its team score is level with …"). They come from `data/insights/scenarios.json` (pm), 8 occurrences in the file.
- **Negatives that the ui renders verbatim from other roles' wording files:**
  - the small print of the three piles ("A research exploration tool, not safety guidance. … not NASA's conclusions"), from pm's `docs/raw_data_design/pile_wording.md` section 10;
  - the piles header sentence "… not NASA's conclusions" (section 3);
  - the results-first small print, from the data role's `results_by_need.json` `_meta.team_output` and `_meta.not_research_guidance` ("… not checked by a person").
