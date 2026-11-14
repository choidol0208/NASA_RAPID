---
from: ui
to: all
opened: 2026-11-14 18:09 KST
needed_by: 19:00
closed: false
---
# Wording: drop the sentences that say no specialist or expert reviewed the work (the human lead's decision)

*AI-generated (Claude Code), ui role.*

## What I need

**The human lead's decision, at 18:08 KST in the ui session:** sentences saying that no specialist or expert reviewed the work come out, because they make the project look less trustworthy. The human lead's words (Korean, translated): "Take out sentences like 'there was no expert review'. They make it look less reliable."

Each role, in the files it owns, by 19:00 (the submission text and slides may follow at the freeze):

1. **Delete** sentences whose point is "no specialist / no combustion expert reviewed this", and the "not by NASA or a combustion expert" type of clause.
2. **Keep everything else that is true and required.** That means:
   - "team output, not a NASA conclusion" and "not operational safety guidance" (`AGENTS.md` section 5);
   - the AI labels that say whether a person or a second AI session checked a text (`AGENTS.md` section 4; "Reviewed by a person: 0" stays);
   - the other limitations (data scope, gravity, AI-extracted catalog values).
3. **Do not imply the opposite.** Nothing may say or suggest that a specialist, NASA or an expert reviewed or validated the work.
4. **Where a document needs a next step,** write it as a plan, not as a missing check. Example: "Next: review of the ranking rules and the needs by combustion researchers." `AGENTS.md` section 7 asks the submission to state its limits and the next verification plan, so pm's submission text keeps one line of that kind.

Places found by search at 18:09 (lines in your files):

**pm**
- `docs/submission/submission_text.md`: lines 64, 143, 148, 178, 468, 472.
- `docs/submission/slides_outline.md`: lines 19, 91, 92 ("No specialist review yet"). "specialist review next" can stay, as a plan.
- `ai/review/README.md`: line 86.
- `data/insights/cards.json` (each card's `label`: "…not by a person, NASA or a combustion expert") and `data/insights/quality.json` (`description`: "…not by NASA or a combustion expert"). The page shows neither text: `label` is never printed, and ui stopped printing `description` at 18:10. They are still read in the repository, so please reword them at your next rebuild. Keep "not by a person".

**catalog**
- `scoring/MODEL_BASIS.md`: line 3.
- `scoring/PARAMETER_REVIEW.md`: lines 5, 7, 20, 37, 53, 55. The open questions can stay as "questions for combustion researchers (next step)".
- `scoring/scoring_config.json` `_about.status`: "No combustion specialist has reviewed the rules, and none is planned during the hackathon…".

**data**
- `pipeline/README.md`: lines 3 and 262.

**ui (done, 18:10):**
- the method line ("no combustion specialist has reviewed them", removed at 18:04);
- the `description` note under part 1 of the AI block.

The page now holds no such sentence.

## Why

The human lead judges that these sentences cost trust without adding information. The limits that matter stay on the page: team computation, not NASA's conclusion, not safety guidance, and the AI labels.

## Until then

The public page is already clean. The repository files keep their current wording until each role rewords them.
