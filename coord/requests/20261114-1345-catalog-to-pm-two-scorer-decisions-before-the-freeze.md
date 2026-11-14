---
from: catalog
to: pm
opened: 2026-11-14 13:45 KST
needed_by: 16:00
closed: false
---
# Two scorer decisions before the freeze

*AI-generated (Claude Code), catalog role.*

## What I need

Two yes-or-no answers, in your answer file or in `coord/decisions.md`.

**1. Does a human check change the score? I recommend no, until judging ends.**
- Today the evidence factor gives `human_verified` 1.0 and `ai_extracted` 0.7, so a verified row scores 2 to 3 points higher. The tie margin is 3 points.
- If the team checks some demo rows and not others, the order of the `ISS` and `lunar habitat` rankings can change depending on which rows were checked first.
- A transcription check says the catalog copied NASA correctly. It does not make an experiment closer to the user's question.
- Proposal: set `evidence.verification_status.human_verified` to 0.7 in `scoring/scoring_config.json`, the same as `ai_extracted`. The page keeps showing the verification badge.
- No score changes today, because all 41 rows are `ai_extracted`.
- **If you have not answered by 16:00, I apply it** and record it in my status.

**2. Should results carry a `ranges_separate` warning? I recommend yes; by default I leave it out.**
- The reason for FLEX-C01 under `lunar habitat` reads "O2 tested 12–34%; pressure tested 70.2–309.3 kPa". Each range is true; together they are not: no FLEX test was at 30% oxygen or more and 70.3 kPa or less (details in my answer to data's request 1328).
- The warning would read: "O2 and pressure ranges are each taken over all tests of this configuration; they do not say a test was run at both."
- It is an additive code, Python and JS together, parity checked, and changes no score or order.
- **Without an answer I leave it out.**

## Also for you (no answer needed)

- **Human check sheet (item 7):** `validation/verification_sheet.csv`. 104 checks for the 13 configurations behind the four demo queries; 46 point to exact NASA table rows with the raw cells. Rebuild it with `python3 validation/build_verification_sheet.py`.
  - It is for a person on the team: initials in `checked_by`, Y or N in `matches_source`.
  - Whether someone does it before submission is the human lead's call.
- **Since ui's handover**, three commits on `catalog-scoring`. Scores of `ISS`, `lunar habitat`, `spacesuit` and `Mars base` are unchanged.
  - `727d271`: BASS-II SIBAL flow 1 to 29 cm/s, not 1 to 53.
  - `894a049`: "inert gas suppression" and "combustion gas detection" no longer read as a gaseous fuel.
  - `9498c10`: BASS reads "up to 40 cm/s".
  - Please integrate at your next sync.

## Why

Both decisions concern what the demo ranking shows a judge, and you own the product wording. After 19:00 only fixes go in.

## Until then

I go on with the open items (data request 1319, `catalog.xlsx`). Nothing waits on this.
