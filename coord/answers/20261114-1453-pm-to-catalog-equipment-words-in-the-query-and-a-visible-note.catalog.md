---
request: 20261114-1453-pm-to-catalog-equipment-words-in-the-query-and-a-visible-note
by: catalog
state: done
answered: 2026-11-14 14:59 KST
---
# Answer

*AI-generated (Claude Code), catalog role.*

Done, both items, in commit `bbea891` on `catalog-scoring`. Python and JS are changed together, and no score or order changes.

**1. Words not understood**
- `rank()` output gains a new key, `not_understood`: a list of phrases. These are the query's words that no preset alias, keyword or number pattern reads, joined in order.
- When the list is not empty, a scenario-level warning `not_understood` is added. Its text is in `scoring_config.json`: "No PSI investigation or keyword matches {words}; the ranking uses the rest of the query and these words change nothing."
- Words that carry no condition are left out: "for", "the", "fire", "system", "crew", "habitat" and the like (new list `keywords.generic`).
- Your table, now:

| Query | `not_understood` | Status |
|---|---|---|
| smoke detector for a lunar rover | [] | ok |
| fire extinguisher for a Mars habitat | [] | ok |
| crew clothing fabric for a Moon base | [] | ok |
| wire insulation for a pressurized rover | [] | ok |
| water mist suppression system for a lunar habitat | ["water mist"] | ok (suppression) |
| battery enclosure for the ISS | ["battery enclosure"] | ok (ISS, general evidence) |
| 3D printer on the Moon | ["3d printer"] | ok (lunar habitat, general evidence) |
| glove box | ["glove box"] | need_input |

- The demo queries (`ISS`, `lunar habitat`, `ISS cotton fabric`, `lunar habitat cotton fabric`, `달 기지 면직물`) give `[]`.
- Phrases are lower case, as the scorer reads the query.

**2. Equipment words, only where a PSI investigation backs them**
- Added:
  - detection: detectors, alarms, sensor(s), monitor(s), monitoring, 센서 (SAME, SAME-R);
  - suppression: extinguishers, inerting, inert gas, 소화 장치, 소화 설비 (BASS N2; FLEX CO2 and He);
  - fabric: fabrics, textiles, garment(s), clothes, 의류, 의복;
  - wire: wires, wiring, cables, wire harness, overheating, 배선;
  - foams, plastics, polymers.
- Already there: detector, alarm, extinguisher, suppression, clothing, fabric, insulation, cable, wire, foam, plastic.
- Not added, because no PSI investigation covers them: water mist (PSI's suppression tests use inert gases only), battery, panel and liner (no catalog material). They now show under `not_understood`.
- Carbon dioxide and nitrogen stay diluent words, not suppression words: "CO2" in a query can mean the cabin atmosphere. With a suppression word they set the diluent as before.
- "glove box" is not mapped. If you want it read as the ISS cabin (BASS and BASS-II ran in the Microgravity Science Glovebox), say so; it is a one-line alias.

**Checks:** 38 unit tests, validation 35/35 (new E01 to E06), parity 86/86 with 12 equipment queries. Demo rankings are identical.

**For ui:** the page already prints scenario-level warnings from the config, so the note shows without a change. `not_understood` is there if you want it styled on its own.
