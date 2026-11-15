---
from: catalog
to: pm
opened: 2026-11-15 15:20 KST
needed_by: 17:30
closed: true
---
# Config 1.5.2: decisions on review B1-B5 for the submission text

*AI-generated (Claude Code), catalog role.*

## What I need

At your next integration of `catalog-scoring` (config 1.5.2, weights unchanged):

1. **Rebuild the AI layer if it stores warnings.** Queries without a material now carry a new top-level warning, `no_material`. Scores, top 3s and compliance lines are unchanged from 1.5.1.
2. **Wording for the submission text and slides**, where they describe the ranking. The human lead took catalog's recommendations at 15:16:
   - **B1:** "decisive" conditions (evidence class 1) get a large weight; that is not a veto.
     - Only fuel and oxygen have a gate (non-compensatory below a similarity of 0.2).
     - The gate was not made stricter: with an oxygen gate at 0.37, "lunar habitat cotton fabric" would rank a gas burner first, because no solid test reached 30% O2.
     - The missing solid tests are shown by the counts.
   - **B2:** documented values that are not per-test table values keep their full similarity. The page marks them `documented`, with their basis.
   - **B3:** without a material the page warns that the fuel is not compared and asks for one. Please correct any sentence that reads the "lunar habitat" top 3 (droplets, gas burners) as "the best evidence for a habitat". It is the ranking without a fuel comparison.
   - **B4:** never compare scores across questions. You took this as a rule already.
   - **B5:** the detection profile covers the smoke of overheated materials, heated without a flame, as in SAME and SAME-R. Pressure stays a minor factor there until a source on that smoke is found.
3. Sources for these sentences: `scoring/METHOD.md` 1.2, 1.5, 1.7 and 1.8; `scoring/WEIGHTING.md` 4.2 and 6.

## Why

These were the five decision items of the 09:40 review. The texts should state the choices and their reasons, and not suggest that a rule was never questioned.

## Until then

`main` runs 1.5.1, and the only difference is the new warning.
