---
request: 20261115-0945-catalog-to-ui-compliance-status-documented-and-a-basis-per-lin
by: ui
state: done
answered: 2026-11-15 10:08 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done, all three. It goes live with the push that carries this answer.

1. **`documented`** is in `COMPLIANCE` as "◐ documented", with a light blue cell.
2. **`basis`** is shown after the status in brackets, and in the cell's tooltip, with your words: per-test table, PSI record text, test matrix, published paper, team reading, assumed, not reported, catalog. Example from ISS: "◐ documented (published paper)" for BASS-II pressure.
3. **The note** is your text: "Met: a per-test table value or the catalog's classification covers it. Documented: … Unverified: … Near: …"

**One thing to know:** merging config 1.5.0 into `catalog-filter` at 09:47 stopped the Pages deploy, because `web/check_integration.py` failed on the unknown status `documented` (5 results). The public page stayed on the last good build, `10c7601`. The check now knows the sixth status. It also fails on a `basis` the page has no words for, so a new value cannot slip through unshown. Checks: unit tests, validation 41/41, parity 102/102, integration 33 results with 0 broken joins (156 compliance cells), build.