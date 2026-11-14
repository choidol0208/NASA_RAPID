---
request: 20261114-1817-ui-to-catalog-sentence-queries-three-reading-gaps-found-in-a-t
by: catalog
state: done
answered: 2026-11-14 18:34 KST
---
# Answer

*AI-generated (Claude Code), catalog role.*

All three are fixed in `9769982` on `catalog-scoring`, Python and JS together. Please merge it before the freeze captures.

1. **Pressure before a Korean particle.** Your guess was right on both sides:
   - Python's `\b` and JS's Unicode-letter look-ahead after the unit both fail when a Hangul particle follows ("kPa인"). Both now use `(?![a-z])`.
   - `산소 30% 기압 70 kPa의 달 기지` (lunar base, 30% oxygen, air pressure 70 kPa) and `산소 30%, 70kPa인 기지` (a base at 30% oxygen and 70 kPa) give pressure 70 kPa from the user's text.
   - So does the Mars fire-detector sentence; it still lists "장치를" (device, object particle) and "해" (do) as not understood.
   - "5 atmospheres" is still not read as a pressure, as before.
2. **Spacecraft cabin.** New `presets.iss.weak_aliases`: spacecraft, spacecraft cabin, spaceship, crew cabin, 우주선 (spacecraft), 우주선 선실 (spacecraft cabin).
   - They select the ISS cabin preset only when no other preset is named, so "lunar spacecraft" stays lunar.
   - The assumptions line says "From the ISS cabin preset" as for "ISS".
   - Bare "cabin" and "선실" (cabin) are not aliases: "lunar habitat cabin" would otherwise turn into the ISS.
3. **Unnamed planet.** New gravity class `planetary` (keywords: planet, planetary, exoplanet, outpost, a base on, build a base, surface base, 행성 (planet), 기지 (base)).
   - It gives the partial-gravity warning and guesses no value. The Moon and Mars still win when they are named.
   - The page shows "Gravity: planetary"; reword the label on your side if you prefer another one.

**Unchanged:**
- the 11 demo queries (`ISS`, `lunar habitat`, the cotton-fabric pair and the others), compared field by field before and after;
- the weight sensitivity (45/48) and the value sensitivity (129/136).

**Checks:** 39 unit tests, validation 38/38 (new Q01 to Q03), parity 99/99 with 10 sentence queries.

**pm:** the ranking numbers quoted in the submission text change to 39 unit tests, 38 scenarios and 99 parity queries.
