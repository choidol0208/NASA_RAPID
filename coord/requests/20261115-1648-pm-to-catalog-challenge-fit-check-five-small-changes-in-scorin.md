---
from: pm
to: catalog
opened: 2026-11-15 16:48 KST
needed_by: 17:40
closed: false
---
# Challenge-fit check: five small changes in scoring_config.json (partial-gravity notice with its NASA source, investigation names, the artemis alias, Mars text, combustion chamber)

## What I need

*AI-generated (Claude Code), pm role.*

The human lead asked for a final check of the product against the challenge statement. The result is `docs/submission/challenge_fit.md` on `main` (`19f9a45`): 14 points covered, 17 partly, 1 not covered, 2 where the product contradicts the statement. Five of the ranked fixes are in `scoring/scoring_config.json`, which is yours. Each was tried on a scratch copy by the checking agent; please make them with your own checks (unit tests, parity) and push. The lead reviews the page at 18:00.

1. **`warnings.partial_gravity` (the most important one).** The statement says "Microgravity and normal-gravity results could bound what occurs at intermediate gravity levels"; the page says only "they are not bounds", with no source, so a NASA reader sees a flat contradiction. The evidence is already in `pipeline/spec/references.json` (NTRS-20130010991, Olson and Ferkul, items `OF2012.table1` and `OF2012.margin`): at lunar gravity the oxygen limits (ULOI and MOC) are lower than at both 0 g and 1 g for all three materials; at Martian gravity for two of the three (Mylar G lies between). pm checked the twelve values against the file. Proposed text, clean under `ai.checks.lint_text`:

   > PSI has no partial-gravity (lunar or Martian) combustion data; every result here is a microgravity test. The challenge statement suggests that results at the two ends of the gravity scale could bound intermediate levels. This page does not treat them as bounds: in NASA drop-tower tests of three materials (Olson and Ferkul 2012, Table I), the oxygen limits at lunar gravity were lower than at both 0 g and 1 g, and at Martian gravity lower for two of the three. Those drops lasted 5.18 s and used extinction criteria that differ from the 1 g test. NASA names partial-gravity material flammability a major gap (OCHMO-TB-008).

   and, appended or as a second notice: "The challenge statement names the Lunar-g Combustion Investigation (LUCI) and the Flammability of Materials on the Moon (FM2) experiment as expected future sources, and ACME's E-FIELD Flames (PSI-22) as an experiment in which an electric field mimicked partial gravity."
2. **`warnings.not_understood`.** Typing an investigation name (BASS, FLEX, SAME) gives "No PSI investigation or keyword matches 'bass'", which is false: the investigation is in PSI; the ranking does not take names as terms. Proposed: "The ranking does not read these words: {words}. It reads an environment, a material, a purpose and conditions; investigation names are not ranking terms, and every investigation is listed under All investigations."
3. **`presets.lunar_habitat.aliases`: remove `artemis`.** The statement's own example is the Artemis II smoke alarm in a spacecraft; today "Artemis II smoke alarm" is read as a lunar base. Without the alias it reads as detection with no environment assumed (SAME and SAME-R first on the scratch copy). No test pins the alias.
4. **`presets.mars_habitat.source`**: replace "ask the user for O2 and pressure" with "type an oxygen and a pressure to place tests (for example 34% O2 at 8.2 psi, a NASA exploration atmosphere)".
5. **`keywords.out_of_scope`: remove "combustion chamber" and its Korean pair.** "ACME combustion chamber 40% oxygen" is in scope (the statement itself speaks of the combustion chamber of CFI-G); "hybrid rocket combustion chamber fire" stays out of scope through "rocket".

Smaller, if time allows: the 85% oxidizer-stream clause in `warnings.o2_above_all`; `scoring/METHOD.md` line 175 ("129 of 136"; `validation/report.md` gives 124 of 136); a header line in `scoring/__init__.py`; the hardware cell of SLICE in `data/catalog/investigations.csv` ("Microgravity Science Glovebox (MSG), SPICE fan-driven flow duct", as the statement says).

## Why

Items 1 to 3 are what a judge with the statement in hand meets first. Item 1 also goes into the deck's limits slide and the submission text (done on `main`).

## Until then

The texts and the deck carry the sourced wording; the page keeps the old notice until your push. If you cannot take this before 17:40, say so in your status and pm makes the five edits on `main` under the lead's instruction to finish the page for the 18:00 review.
