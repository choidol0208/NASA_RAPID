---
from: catalog
to: ui
opened: 2026-11-15 15:20 KST
needed_by: 17:30
closed: true
---
# Config 1.5.2: new warning no_material on queries without a material; one line that scores compare within a question only

*AI-generated (Claude Code), catalog role.*

## What I need

1. **Check that the new top-level warning `no_material` reads well on the page.**
   - Its text is in `scoring_config.json` `warnings.no_material`: "No material is named, so the fuel is not compared: this ranking rests on the atmosphere, the flow and the purpose only. Name a material (for example cotton fabric, PMMA or wire insulation) for a closer match."
   - `renderWarnings` shows it as is. It is not a stop warning, so leave it out of `STOP`.
   - It appears on every query that names no material, including the presets "ISS" and "lunar habitat" and "smoke detector on ISS".
   - If it is too loud on the preset buttons, a softer style is your call. Please keep the words.
2. **One sentence near the scores**, for example under the result cards or in the table note: "A score orders the investigations for this question only; scores of different questions cannot be compared."

No other change for you:
- Scores, top 3s, compliance statuses and bases are the same as 1.5.1.
- Parity is 106 of 106.
- I ran your `web/check_integration.py` on 1.5.2: 11 queries, 33 results, 0 broken joins.

## Why

The human lead took catalog's recommendations on the five decision items of the 09:40 review (B1–B5):
- **B3:** without a material, the fuel is not compared at all, so "lunar habitat" ranks droplets and gas burners. The warning says so and asks for a material. The ranking itself is unchanged.
- **B4:** the weights are rescaled over the dimensions each question sets, so a score is meaningful only within its question.
- **B1, B2, B5:** the rules stay, and only the documents change.

Reasons: `scoring/METHOD.md` 1.2, 1.5, 1.7 and 1.8.

## Until then

The page works as it is; the warning simply shows with the default style.
