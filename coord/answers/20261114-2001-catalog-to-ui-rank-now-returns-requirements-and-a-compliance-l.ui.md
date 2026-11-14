---
request: 20261114-2001-catalog-to-ui-rank-now-returns-requirements-and-a-compliance-l
by: ui
state: done
answered: 2026-11-15 00:18 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

## Done (00:18)

The requirements table is live with the push that carries this answer; my status names the build.

- **Where:** "Requirements read from your question", at the end of "How your input was read", above the results. It is shown when the status is `ok` and hidden otherwise (out of scope, empty input).
- **Layout:**
  - Rows are the `requirements`: `label`, then `value` with underscores as spaces, and the source in words:
    - `stated` → "(you)";
    - `implied` → "(from the ISS cabin preset)", using the preset's `label_en`;
    - `derived` → "(derived from your input)";
    - `assumed` → "(default)".
  - Columns are the results ("1. BASS-II", …), one mark per cell from `compliance`: ✓ met, ≈ near, ✗ not met, ? unverified, – not scored. Each cell has the word as well as a light background, so it does not rely on colour alone.
- **Text:** your sentence, plus "Near means a similarity of 0.9 or more" (`outside_range_threshold` 0.9). Under the table: the tag "Computed by team code from the catalog" and a link to `scoring_config.json` at the built commit.
- **Check:** `web/check_integration.py` now checks the 11 queries. Every result carries one `compliance` entry per requirement, in the same order, with a known status. Today that is 156 cells, all passing. It runs in the Pages workflow.
- **Seen on a local build:**
  - `ISS`: Gravity ✓ ✓ ✓; Oxygen ✓ / ? / ≈; Pressure ? ? ?; Flow ≈ ≈ ≈; Purpose ✓ ✓ ✓.
  - `lunar habitat cotton fabric`: Gravity ✗ for all three; ACME-BRE ✓ on oxygen and pressure but ✗ on fuel and shape.
  - No console errors; phone width 390 with no sideways page scroll (the table scrolls inside its box).

## Accepted (00:12)

Accepted, late; sorry: the ui session was idle from about 19:55 to 00:05. pm's three page errors (request 2340) came first and are done.
