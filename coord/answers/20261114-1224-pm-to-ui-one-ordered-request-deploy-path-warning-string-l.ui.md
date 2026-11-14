---
request: 20261114-1224-pm-to-ui-one-ordered-request-deploy-path-warning-string-l
by: ui
state: done
answered: 2026-11-14 13:00 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Items 0 to 3 are done on `catalog-filter` and go live with this push. Checks: unit tests 18/18, validation 22/22, JavaScript/Python parity 61/61, build.

0. **Deploy path.** `.github/workflows/pages.yml` now deploys on pushes to `main` as well as `catalog-filter`. On `main` this starts once you merge `catalog-filter`, because the workflow file on `main` decides. Please record the change to decision 8 (11:20): both branches deploy until the 19:00 freeze, then `main` only (I switch the trigger at the freeze). Each role pulls before it pushes, so either branch carries the other's latest work.
1. **Warning string.** `warnings.partial_gravity` now uses your short form, because data has not added the Table I item yet: "PSI has no partial-gravity (lunar or Martian) combustion data. All results here are microgravity tests; they are not bounds for lunar or Martian gravity. NASA names partial-gravity material flammability a major gap (OCHMO-TB-008)." No code changed. I switch to the long form when data's Olson and Ferkul Table I item reaches `main`, unless you say otherwise.
2. **Labels.**
   - A card with `status: "fallback_quote"` or `ai_generated: false` is tagged "Quoted from the PSI record" and has no AI tag.
   - A scenarios entry or item with `text_origin: "template"` is tagged "Computed by team code from NASA PSI tables".
   - When a list mixes origins, each item carries its own tag. Otherwise one tag follows the list.
3. **Source links and frame.**
   - `sourceLinks(card.summary_sources)` follows the summary.
   - `gaps[].sources` are shown as links.
   - `frame` (with `frame_sources`) sits at the top of the needs section, above the needs table and the need list. Its tag follows `frame_text_origin`, else the entry's `text_origin`. With neither it is tagged AI-generated, so please set one.

Also done from your note: `in_atmosphere` is no longer drawn as a full ("covered") cell. It reads "Tests run in your atmosphere" in a lighter colour. The need's `reading` (from data's `needs.json`) is under the table and in the cell tooltip.

Optional items:
- 4 waits for the human lead's choice. I add `data/insights/evidence_map.json` to OPTIONAL in `web/build.py` when you announce it.
- 5 when your 16:00 addendum arrives.
- 6 and 7 after that, in order.

Tested in a local build with `main` data (7 needs) and with `origin/data-pipeline` data (6 needs, readings, objective links), and at 375 px (no sideways scroll). The scenario section appears on the public page with this push, because `scenario_needs.csv`, `scenario_tests.csv` and `pipeline/spec/scenarios.json` are now on this branch.
