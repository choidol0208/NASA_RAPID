---
from: pm
to: catalog
opened: 2026-11-14 14:53 KST
needed_by: 17:30
closed: false
---
# Equipment words in the query and a visible note for words not understood

## What I need

*AI-generated (Claude Code), pm role.*

The human lead describes the main use as: a user says what equipment they want to develop, and the page returns the information they need, the points to consider and the constraints. pm tried equipment-style queries on `scoring.scorer.rank` at commit 12d35b4:

| Query | Read as | Top results |
|---|---|---|
| smoke detector for a lunar rover | lunar habitat, detection | SAME, SAME-R, FLEX-2 |
| fire extinguisher for a Mars habitat | Mars habitat, suppression | BASS, FLEX, BASS-II |
| crew clothing fabric for a Moon base | lunar habitat, prevention, fabric | BASS-II, SAFFIRE-II, ACME-BRE |
| wire insulation for a pressurized rover | lunar habitat, prevention, pyrolyzing solid | ACME-BRE, BASS-II, SAFFIRE-II |
| water mist suppression system for a lunar habitat | lunar habitat, suppression | FLEX, ACME-BRE, BASS |
| battery enclosure for the ISS | ISS, prevention (assumed) | BASS-II, BASS, SAFFIRE-II |
| 3D printer on the Moon | lunar habitat, prevention (assumed) | ACME-BRE, FLEX, ACME-CFI-G |
| glove box | need_input | none |

The first five are read well. Two things would make the equipment use honest and clear; do what fits before the freeze, in this order:

1. **Say which words were not understood.** For "battery enclosure" and "3D printer" the result is the generic reading of the environment, and nothing tells the user that the equipment word had no effect. Add to the output (Python and JS together) a list such as `not_understood: ["battery enclosure"]`, or a warning code with the words, so the page can print "No PSI investigation or keyword matches 'battery enclosure'; showing general evidence for this environment." No score change.
2. **Equipment vocabulary, only where a PSI investigation backs it.** Check that common equipment words map to the concern they belong to: detector, alarm, sensor, monitor (detection); extinguisher, suppression system, water mist, carbon dioxide, nitrogen, inerting (suppression); clothing, garment, fabric, panel, liner, insulation, cable, wire, foam, plastic part (prevention, with a fuel class where the catalog has one). Add what is missing to the keyword lists in `scoring_config.json`. Do not add words for which PSI holds nothing (batteries, propellants): those belong under item 1.

## Why

The page should answer "I want to develop this piece of equipment" for the equipment PSI can speak to, and say plainly when it cannot, instead of returning a confident-looking generic ranking.

## Until then

pm writes the model-checked summaries and tells ui how to group the output (request 1505 to ui).
