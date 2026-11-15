---
from: catalog
to: ui
opened: 2026-11-15 10:12 KST
needed_by: 13:00
closed: true
---
# Config 1.5.1 changes three demo top-3s and the tie rule; page note on near-ties

*AI-generated (Claude Code), catalog role.*

## What I need

1. **One sentence in `web/index.html`** (about line 154, the table note). It says "Scores within 3 points are ordered by evidence quality, so a slightly lower score can sit higher". Since config 1.5.1 the order is different. Suggested text: "Scores within 3 points of the best remaining score are ordered by how much of the score rests on recorded values (recorded share), then by evidence quality, so a slightly lower score can sit higher." The `tie_note` string of a result changed too: "within the tie margin of the best remaining score; ordered by recorded share, then evidence".
2. **Check any fixed text or capture that names a demo top 3.** Old (1.4.0 and 1.5.0) → new (1.5.1):

| Query | Old | New |
|---|---|---|
| ISS | BASS-II 93.4, BASS 93.4, SAFFIRE-II 92.1 | BASS-II 93.4, **SAFFIRE-I 92.1**, SAFFIRE-II 92.1 |
| lunar habitat | ACME-BRE 75.2, FLEX 75.2, ACME-CFI-G 71.6 | **FLEX 75.2, ACME-CFI-G 71.6, ACME-BRE 73.6** |
| ISS cotton fabric | BASS 94.6, SAFFIRE-III 94.6, BASS-II 93.5 | **BASS-II 93.5, SAFFIRE-I 93.7, SAFFIRE-II 92.7** |
| lunar habitat cotton fabric | SAFFIRE-II 75.0, SAFFIRE-I 74.5, ACME-BRE 63.9 | same order; ACME-BRE 62.6 |
| smoke detector on ISS | SAME, SAME-R, DAFT | SAME, SAME-R, **SAME-SIM** |

Nothing else for you to build. `web/scorer.js` is updated, parity is 104 of 104, and I ran your `web/check_integration.py` on 1.5.1: 33 results, 0 broken joins, 156 requirement cells. The statuses and bases are the same set you handle since 0945, so the deploy should not stop this time.

## Why

An AI review of the scorer (09:40) found three things, and the human lead asked catalog to fix them:
- **A1:** the ACME and SLICE tables have one row per test day, not per test. They are now `summary_table`, so their evidence factor is 0.95 instead of 0.97.
- **A2:** the old near-tie rule swapped neighbours once, by evidence and then by `has_1g_comparison`. That field is empty when the record does not mention a 1 g comparison, so silence lost. The rule was also not documented. Now, within 3 points of the best remaining score, the result whose score rests more on recorded values comes first. Investigations whose O2 and pressure are both assumed (BASS, SAFFIRE-III) no longer lead on ISS questions.
- **A3:** "solid" and 고체 (solid) are read as the fuel phase.

Following from A2: DAFT measured a dust aerosol, not a fire, so it no longer counts as fire-signature evidence. It falls out of the smoke top 3.

Method: `scoring/METHOD.md` 1.5 and 1.8.

## Until then

The page works with either config; only the note text and any fixed top-3 text would be out of date.
