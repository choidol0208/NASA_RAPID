---
from: ui
to: catalog
opened: 2026-11-14 18:17 KST
needed_by: 19:00
closed: false
---
# Sentence queries: three reading gaps found in a test by the human lead

*AI-generated (Claude Code), ui role.*

## What I need

The human lead asked whether the query box handles a description instead of a keyword. Their example, translated: "I want to build a base on a planet with X% oxygen and design for fire; give me insights." I ran these sentences on the live page (build f23cd58, config 1.1.0) at 18:12–18:16. Oxygen, Mars, Moon base, fabric, detection and suppression are read well. Three gaps remain, all in the reading of the input. The fixes are yours (`scoring/scorer.py` and `web/scorer.js` together); please fix them before the 19:00 freeze if you can.

1. **Pressure followed by a Korean particle is not read.**
   - `산소 30% 기압 70 kPa의 달 기지` gives "Pressure 70.3 kPa (from the preset)": the typed 70 is ignored.
   - `산소 30%, 70kPa인 기지` gives no pressure.
   - `산소 농도 25%, 기압 70 kPa인 화성 기지에서 화재 감지 장치를 설계하려고 해` gives no pressure, and the unmatched words list "기압 70 kpa인".
   - By contrast, `압력 70 kPa 환경` and `Moon base at 30% oxygen and 70 kPa` are read, and oxygen with a particle (`30%의`) is read too.
   - A guess: in `scorer.py` line 201 the pattern ends in `\b`. In Python a Hangul letter counts as a word character, so `kpa인` has no word boundary; `(?![a-z])` would not have this problem. Please check the JS side as well, since the live page uses it.
   - Expected: "Pressure 70 kPa (you)" for all three.
2. **"Spacecraft cabin" is not read as an environment.**
   - `spacecraft cabin`, `우주선 선실` (spacecraft cabin) and `A spacecraft cabin at 21% oxygen and 101 kPa…` read no environment.
   - The first two show nothing at all ("Add an environment or a material to start").
   - Suggestion, your call: read `spacecraft`, `spacecraft cabin`, `우주선` (spacecraft) and `선실` (cabin) as the `iss` preset ("ISS cabin"), and say so in the assumptions line.
3. **A base on an unnamed planet gets no gravity reading.**
   - `산소 농도 30%의 행성에서 기지를 건설하려고 하는데 …` (a base on a planet at 30% oxygen) and its English version (`a base on a planet whose atmosphere has 30% oxygen`) read only "Oxygen 30%".
   - "행성" (planet), "planet", "기지" (base) and "base" are listed as unmatched, and no partial-gravity warning is shown. A user may read the microgravity results as valid on their planet.
   - Suggestion, your call: "planet" or "행성" (planet), or "base" or "기지" (base) without Moon or Mars, sets no preset. It does mark gravity as not microgravity, so the existing warning "PSI has no partial-gravity (lunar or Martian) combustion data…" is shown. No value is guessed.

Please keep the demo queries (`ISS`, `lunar habitat`, `ISS cotton fabric`, `lunar habitat cotton fabric`) ranked and scored as now. Add validation scenarios for the new cases, and keep parity green.

## Why

The first screen invites a description ("What are you building, and where?"), and judges will type sentences. Today, a typed pressure can be silently replaced by the preset value (gap 1), which is a wrong reading shown as the user's input. A common phrase can also give an empty page (gap 2).

## Until then

The page is unchanged. Each gap shows on the page as it is: the unmatched words are named, and the preset values are marked "(from the preset)". If a fix lands before 19:00, ui takes the freeze captures after it.
