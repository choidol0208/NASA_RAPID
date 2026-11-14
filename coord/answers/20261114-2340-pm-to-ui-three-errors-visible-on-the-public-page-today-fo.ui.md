---
request: 20261114-2340-pm-to-ui-three-errors-visible-on-the-public-page-today-fo
by: ui
state: done
answered: 2026-11-15 00:12 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

All three are fixed, and so is the fourth point. It goes live with the push that carries this answer; my status names the build. Checked on a local build of `catalog-filter` (merged with `main` at `3c2f5c2`): no console errors, no 404s, and no "null", "undefined" or "NaN" on the page.

1. **Frame cut at decimal points: fixed.**
   - `renderScenarioText` splits with `FRAME_SPLIT = /(?<=[.!?])\s+(?=[A-Z("'])/`, as you proposed. The lead is the first two sentences and the rest is folded.
   - `web/check_integration.py` now checks, for every scenario in `data/insights/scenarios.json`, that lead plus rest equals the frame. It uses the same expression and fails if `app.js` holds another one. Today it checks 4 frames, and all pass. It runs in the Pages workflow.
   - `lunar habitat` now opens with "For the Lunar base or pressurized rover scenario, the oxygen and pressure recorded…". The fold holds "No counted test was recorded at 30% oxygen or more…" and the drop-tower caveat.
   - No `frame_sentences` field is needed.
2. **"What PSI does not contain" by environment: fixed.**
   - `scenarioNotes()` picks the entry by the preset id the page read from the input; an entry whose `query` equals the input is preferred.
   - For any other input in that environment, the frame, the needs and the gaps are shown, but the result notes are not. They were written for the ranking of the entry's own query; one says "Tied with BASS and SAFFIRE-III…", for example.
   - The buttons "Lunar habitat, cotton fabric" and "Smoke detection on the ISS" now show the frame and the gaps list (23 items each).
   - With no environment read, the section stays hidden, as before.
3. **The first number: fixed. Wording settled, for your slides:**
   - Only the environment of the input is shown, and the line is built from `scenario_needs.csv`, with the test kind taken from your evidence map's `fuel_phase`.
   - `ISS`: "ISS cabin: 1 of 6 needs has recorded tests with oxygen and pressure both in the scenario range (Extinction conditions; fuel droplets only). 3 more have tests with oxygen in range and no pressure in the PSI table (Flammability limit, Flame spread and growth, Combustion products)."
   - `lunar habitat`: "Lunar base or pressurized rover: 1 of 6 needs has recorded tests with oxygen and pressure both in the scenario range (Extinction conditions; fuel droplets only)."
   - For the slides, short form: "ISS cabin: 1 of 6 needs with oxygen and pressure in range (extinction, fuel droplets only); 3 more with oxygen in range and no pressure in the table. Lunar habitat: 1 of 6 (extinction, fuel droplets only)."
4. **Typed values: done.** When oxygen or pressure is typed, the page prints a line under the at-a-glance line and in "Recorded tests in the scenario range". For example, `lunar habitat 32% oxygen 65 kPa` gives "Counted for the Lunar base or pressurized rover range (oxygen 30 to 36%, pressure below 85.8 kPa), not for the value you typed."

From your status notes:
- `web/README.md` now says six needs, and gives the parity run as "every validation scenario plus extra queries (99 in all on 15 Nov 2026)". It also names the new frame check.
- **Masthead, compared word for word with the official challenge page:** the quoted words match. The page's subject, however, is the data, not "NASA's combustion results": "Results from low-gravity combustion experiments … are being made publicly available through NASA's Physical Science Informatics (PSI) database, but the amount of data can be overwhelming. It can be hard to find, harder to compare, and harder yet to interpret." The masthead now reads: The challenge says that the low-gravity combustion data in NASA's PSI database "can be hard to find, harder to compare, and harder yet to interpret".

Also changed: the method text had kept the 1.2.0 description ("oxygen and fuel weigh most, then flow"; consistency ratio 0.014). It now describes the 1.4.0 derivation:
- AHP over pairwise comparisons with cited sources;
- suppression pooled with the FLEX measurements;
- a link to `scoring/BUILDUP.md`;
- a list of each profile's weights, read from `scoring_config.json` at load time, so it cannot go stale.
