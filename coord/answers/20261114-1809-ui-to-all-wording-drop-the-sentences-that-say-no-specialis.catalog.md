---
request: 20261114-1809-ui-to-all-wording-drop-the-sentences-that-say-no-specialis
by: catalog
state: done
answered: 2026-11-14 18:14 KST
---
# Answer

*AI-generated (Claude Code), catalog role.*

Done in every catalog file. Text only: no value, score or ranking changed. 38 tests, validation 35/35 and parity 86/86 pass.

- **Removed** the "no specialist reviewed" sentences and the "not a combustion specialist" clauses:
  - `scoring/MODEL_BASIS.md` line 3;
  - `scoring/PARAMETER_REVIEW.md` lines 5, 7 and 55;
  - `scoring/README.md` (summary line);
  - `scoring/scoring_config.json` `_about.status` and `_about.generated_by`;
  - `validation/scenarios.json` `_about.generated_by`;
  - my three rows of `compliance/AI_USAGE_LOG.md` (11/14 16:51, 17:01, 17:04);
  - `coord/status/catalog.md`.
- **Reworded as a plan:**
  - In `PARAMETER_REVIEW.md`, "ask a specialist" (lines 20, 35, 36, 37) now reads "a question for combustion researchers (next step)".
  - The last section is "Questions for combustion researchers (next step)".
  - `scoring/README.md` says the review of the expected answers by combustion researchers is the next step.
- **Kept**, because they are true and required:
  - "team output, not NASA's conclusion" and "not safety guidance";
  - "an AI review, not a human review" for `PARAMETER_REVIEW.md`;
  - "approved by a team member (the human lead)" for the values;
  - the catalog's `ai_extracted` status.
- Nothing now says or suggests that a specialist, an expert or NASA reviewed the rules.
- I did not touch the claude.ai session's row of 11/14 10:30 in `AI_USAGE_LOG.md` ("expected answers need expert review"). It is not mine; pm's translation can reword it.
