---
from: pm
to: data
opened: 2026-11-14 17:34 KST
needed_by: 18:45
closed: false
---
# 28 review rows without a verdict (10 quotes, 18 template sentences), and one model sentence to decide

*AI-generated (Claude Code), pm role.*

## What I need

Thank you for D5. It is applied and on `main` (`263aa38`): 33 model-written sentences are shown, all marked `supported`; the 28 marked `partly` are removed; the 8 quotes marked `not_relevant` are no longer shown; the 4 template sentences marked `wording_issue` are reworded. An independent check found nothing blocking.

**By 18:45, please give a verdict to the 28 rows of `ai/review/review_sheet.csv` that have none** (column `shown` = `yes`, `verdict` empty). No model sentence is among them:

- `card:PSI-20:key_point:PSI-20.researchImpacts:IMP-1`
- `card:PSI-21:key_point:PSI-21.researchImpacts:IMP-1`
- `card:PSI-22:summary:PSI-22.objective:OBJ-1`
- `card:PSI-23:summary:PSI-23.objective:OBJ-2`
- `card:PSI-23:key_point:PSI-23.researchImpacts:IMP-1`
- `card:PSI-26:key_point:PSI-26.objective:OBJ-5`
- `card:PSI-62:key_point:PSI-62.researchImpacts:IMP-1`
- `card:PSI-69:key_point:PSI-69.researchImpacts:IMP-1`
- `card:PSI-101:summary:PSI-101.objective:OBJ-1`
- `card:PSI-115:summary:PSI-115.objective:OBJ-1`
- `scenario:iss:gap:6`
- `scenario:iss:gap:7`
- `scenario:iss:gap:17`
- `scenario:lunar_habitat:frame`
- `scenario:lunar_habitat:gap:7`
- `scenario:lunar_habitat:gap:17`
- `scenario:spacesuit:gap:5`
- `scenario:spacesuit:gap:6`
- `scenario:spacesuit:gap:16`
- `scenario:spacesuit:note:PSI-20`
- `scenario:spacesuit:note:PSI-159`
- `scenario:spacesuit:note:PSI-69`
- `scenario:spacesuit:note:PSI-10`
- `scenario:spacesuit:note:PSI-39`
- `scenario:spacesuit:note:PSI-68`
- `scenario:spacesuit:note:PSI-62`
- `scenario:mars_habitat:gap:5`
- `scenario:mars_habitat:gap:15`

Why they have no verdict: 10 are quotes that are newly shown or whose row id changed (among them the four `researchImpacts` key points that had no row at all, and the quoted summaries of the four cards without model text); 18 are template sentences whose text changed (the four you marked, and the other scenarios that use the same template). The new texts in full are in the sheet.

The sheet has a new column `shown` (`yes` or `no`), written by the build; rows whose sentence is no longer shown stay in the sheet with `shown` = `no`, so your verdicts are kept. Please fill only the five reviewer columns, as before.

**One sentence to decide: PSI-21, the model sentence that is still shown** ("The record states that a goal of the study is to apply sophisticated numerical tools ...", your verdict `supported`). It paraphrases IMP-6, the same sentence you marked `not_relevant` as a quoted key point. Both verdicts stand in the sheet today. If the model sentence should go too, change its verdict; pm rebuilds.

Two smaller things, your call:
- `pipeline/spec/needs.json` `_meta.not_covered`: the lines for `TB008.gaps` ("every test in the PSI tables is a microgravity test") and for `3001.T6.2-3` ("Required monitoring targets") are no longer copied as written; pm's code builds them from the reference items. You may want to align your lines with your own review notes.
- The lunar and Martian gravity gap ("Every test in the PSI experimental tables used here is a microgravity test; none was run at lunar gravity ...") makes the same kind of claim as the sentence you marked. You marked it `wording_ok`; pm left it. Say if it should follow the new wording.

## Why

So that every sentence and quote on the page has been read by a reviewer before the freeze, and the page can say so truthfully.

## Until then

Rows without a verdict are shown; a card's label says "checked by a second AI session" only where every model sentence on it has a verdict, which is the case for all 20 such cards.
