---
from: data
to: pm
opened: 2026-11-14 17:55 KST
needed_by: 20:30
closed: false
---
# Lab result for the limits section: which decisions follow a published definition, and one worked example (not for the product before the freeze)

## What I need

*AI-generated (Claude Code), data role.*

**A decision by 20:30: may the submission text or the "limits and next steps" slide use the two results below?** Nothing here touches the product or the frozen files; a "no" costs nothing.

The data side's human lead asked whether the decisions of the pipeline can pass through established mathematical models instead of through a language model or team-made rules. This was tried on the branch `data-lab` (local to the data session, not pushed; the lead decides whether it is pushed). Three workflows of AI agents; every number was recomputed by a second agent with its own code, and every citation was opened again by a separate agent. No person has reviewed it.

**Result 1: where a published definition governs, and where it does not.** The pipeline and the lab code make 130 decisions (reading a cell, converting a unit, matching a test to a scenario, counting, summarising, linking a need to an investigation, ...). Each was matched to a source that someone opened and that defines exactly that operation:
- 53 follow a definition: 45 are elementary mathematics (counting, interval membership, subtraction), 8 follow a named external model (NIST SP 811 conversion factors; NIST e-Handbook percentiles; Kendall tau-b as defined in the NIST Dataplot manual; the convex region of tested conditions of the OECD guidance on model validation, ENV/JM/MONO(2007)2).
- 52 are team rules for which no opened source defines the operation (scenario ranges, bins, tolerances, which tests are pooled).
- 25 are judgements made when the specs were written (need definitions, link verdicts); mathematics cannot replace them.
- 13 published physical relations were checked against the scenarios: none has every stated axis of its validity range inside any scenario (all mapped tests are microgravity; published pressures are one or two points). So the tool quotes published values at their stated conditions and predicts nothing. Example: the linear form of Hirsch et al. 2011 is stated for materials with a limit of 25 to 35% oxygen; all 11 materials of the held 2006 table have a value outside that range, so the lab code refuses to apply it.

Suggested sentence (yours to reword): "Of the 130 decisions the data pipeline makes, 53 follow a published definition, 52 are team rules and 25 are judgements made when the rules were written; no published physical relation we examined has its stated validity range inside any of the scenarios, so the tool shows where tests exist and predicts nothing."

**Result 2: one worked example, lunar habitat, need S1 (extinction conditions).** Nominal point 30% oxygen, 70.3 kPa. Among the 298 counted tests, oxygen is recorded from 12 to 34% and pressure (273 tests) from 70.17 to 309.29 kPa, so the nominal point lies inside the recorded span of each axis taken alone. Taken together it lies outside the smallest convex region that holds the 273 recorded (oxygen, pressure) points: on the lower edge of that region the pressure at 30% oxygen is about 70.97 kPa. All 273 are FLEX droplet tests of one investigation (PSI-69). The nearest test at 30% oxygen is 0.93 kPa higher in pressure. This agrees with your caveat (the 17 counted tests are at 71.2 to 72.4 kPa) and adds that "inside on each axis" is not "inside".

Files, if you want to read them (on `data-lab`): `pipeline/lab/model_map.md`, `data/pipeline/lab/numbers/envelope_lunar_habitat.md`, `pipeline/lab/README.md`.

One finding about the main pipeline, for after the submission or for the README limits only: the factor used for mmHg to kPa (0.133322368) is the torr (101325/760 Pa); the conventional millimetre of mercury is 133.322387 Pa. 31 of the 273 FLEX pressures would differ by 0.0001 kPa in the fourth decimal. No count can change by that amount; I do not touch it during the freeze.

## Why

The submission guide asks for limits and the next validation plan, and Validity is a judging criterion. These two results say, with numbers, what the tool decides by definition and what it does not.

## Until then

Nothing of this is in `data-pipeline` or on the page. The sources are logged in `compliance/SOURCES.md` as lab-only, the AI use in `compliance/AI_USAGE_LOG.md`.
