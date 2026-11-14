---
request: 20261114-1920-pm-to-all-no-freeze-today-keep-working-until-the-human-lea
by: catalog
state: done
answered: 2026-11-14 19:33 KST
---
# Answer

*AI-generated (Claude Code), catalog role.*

Read and applied. Feature work goes on in `catalog-scoring`.

- **Done since the freeze was lifted:** config 1.2.0.
  - The profile weights are derived by AHP. The human lead decided at 19:26 to apply them.
  - The details are in `scoring/WEIGHTING.md`. What pm and ui need to update is in requests `20261114-1933-catalog-to-pm-...` and `20261114-1933-catalog-to-ui-...`.
- **What I would do with the extra day, most valuable first:**
  1. More detection and suppression validation scenarios: 2 each today, against 6 for prevention. The profiles with the largest research-purpose weights rest on the fewest checks.
  2. A short note and a result field for close calls under weight uncertainty. SMAA acceptability of rank 1 per result, so the page can say "no clear winner" (for example `lunar habitat cotton fabric`, 46% against 54%). This needs ui's agreement on a field name.
  3. Human check of the 96 demo rows in `validation/verification_sheet.csv`. Only a person can do this; it turns `ai_extracted` into `human_verified` badges and changes no score.
- **Compliance logs:** I hold my rows until you say the English swap is on `main`.
