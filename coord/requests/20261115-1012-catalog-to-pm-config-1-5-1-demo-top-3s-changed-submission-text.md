---
from: catalog
to: pm
opened: 2026-11-15 10:12 KST
needed_by: 14:00
closed: false
---
# Config 1.5.1: demo top-3s changed; submission text and slide notes to update; AI layer rebuild

*AI-generated (Claude Code), catalog role.*

## What I need

At your next integration of `catalog-scoring` (config 1.5.1, weights unchanged since 1.4.0):

1. **Rebuild the AI layer.** Rankings changed for detection questions (1.5.0) and for the demo queries (1.5.1). `ai/test_robustness.py` was not run in the catalog checkout (no numpy). The functions it calls kept their signatures.
2. **Update the texts that quote demo results** (`docs/submission/`, `README.md`):
   - `submission_text.md` line 131: "ACME-BRE (team score 79.1), FLEX (79.1) and ACME-CFI-G (76.1)". Already out of date under 1.4.0, which gives 75.2 / 75.2 / 71.6. Under 1.5.1: **FLEX 75.2, ACME-CFI-G 71.6, ACME-BRE 73.6**.
   - Line 135 and line 629: "BASS-II (94), BASS (94) and SAFFIRE-II (92.7)". Under 1.5.1: **BASS-II 93.4, SAFFIRE-I 92.1, SAFFIRE-II 92.1**.
   - `slides_outline.md` line 180: "Do not call the ISS top three an order: BASS-II, BASS and SAFFIRE-III are level". New: BASS-II leads; SAFFIRE-I and SAFFIRE-II are level (92.1). BASS and SAFFIRE-III are no longer in the ISS top 3: their O2 and pressure are both assumed.
   - Line 199: "94 … version 1.1.0" → 93.4, config 1.5.1.
   - `ISS cotton fabric`: **BASS-II 93.5, SAFFIRE-I 93.7, SAFFIRE-II 92.7** (was BASS, SAFFIRE-III, BASS-II).
   - Detection: "CO detection on ISS" ranks BASS-II first (1.5.0); "smoke detector on ISS" is SAME, SAME-R, SAME-SIM.
3. **Method text, if the submission describes the ranking.** These parts are new since 1.4.0:
   - detection by fire signature, gas or particulate (1.5.0);
   - compliance lines with a basis and the status `documented` (1.5.0; ui shows them since 0945);
   - the near-tie rule: recorded share, then evidence (1.5.1);
   - the five day tables as summary tables (1.5.1).

   Short version in `scoring/METHOD.md` 1.5 and 1.7, limits in 1.8. One caution for slides: CR ≈ 0 of the literature AHP follows from the class rule (1, 3, 5). It is not a measure of judgement quality (`scoring/WEIGHTING.md` 6).
4. **For your notes:** 0035 is answered `done`: step 7, 62 of 71 fixtures reproduce, and the 9 misses are video link states with four causes. Attributing a disagreeing video is a team decision, see the answer.

## Why

The human lead asked catalog to check and fix an AI review of the scorer (09:40; items A1 to A3). The demo queries are what judges see first, and the texts must name the same top 3 as the page.

Five more review items (B1 to B5) need the human lead's decision, and the catalog does not change them before that decision:
- B1: gating the decisive conditions;
- B2: lower similarity for non-table values;
- B3: assuming solid materials in the presets;
- B4: scores of different questions are not comparable;
- B5: pressure in detection.

B4 matters for your texts now: never compare scores across questions ("ISS 94 against lunar 75"). Compare test counts instead, as the submission already does.

## Until then

`main` runs 1.4.0. `catalog-filter`, which also deploys the page, runs 1.5.0 (ui merged it at 09:47) and gets 1.5.1 when ui merges `catalog-scoring` again. Until then the page and the texts may name different top 3s for ISS and the lunar habitat.
