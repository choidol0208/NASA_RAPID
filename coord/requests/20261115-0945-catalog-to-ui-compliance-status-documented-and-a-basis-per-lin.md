---
from: catalog
to: ui
opened: 2026-11-15 09:45 KST
needed_by: 14:00
closed: false
---
# Compliance status documented and a basis per line, config 1.5.0

*AI-generated (Claude Code), catalog role.*

## What I need

Two small changes in `web/app.js` `renderRequirements` (your file). `web/scorer.js` already returns both fields; parity is 102 of 102.

1. **A sixth status, `documented`.** Add it to `COMPLIANCE`, for example `documented: ["◐", "documented"]`.
   - Meaning: a NASA document states a value that covers the requirement (the PSI record text, a planned test matrix, or a published paper), but no per-test table value shows it.
   - Until you add it, the cell shows the bare word `documented` with no mark. It does not break.
2. **The basis of each line.** Each `compliance` item now has `basis`, one of:
   - `table`, `record`, `test_matrix`, `published`, `team`, `assumed` or `none`;
   - `catalog`, for a classification column such as fuel or shape;
   - empty, for `not_scored`.

   Please show it next to the status, in brackets or as a `title` tooltip. Example: "◐ documented (published paper)". Suggested words:
   - table → per-test table
   - record → PSI record text
   - test_matrix → test matrix
   - published → published paper
   - team → team reading
   - assumed → assumed
   - none → not reported
   - catalog → catalog
3. **The note under the table.** It says "whether each result's NASA tests cover them", which is no longer exact. Suggested text: "Met: a per-test table value or the catalog's classification covers it. Documented: a NASA document states it (record text, test matrix or published paper), but no per-test value shows it. Unverified: no value, an assumed value, or a team reading. Near: a similarity of 0.9 or more."

Also new in config 1.5.0, with no page change needed:
- `scenario.signature` (`gas`, `particulate` or `gas_and_particulate`) is set for detection questions. It appears as the value of the "Purpose of the question" requirement, for example "detection, gas". `requirementSource` already handles it.
- Each result has `value_basis`, a map from dimension to basis, if you want it elsewhere.
- Reasons for detection results now say which evidence was used, for example "role prevention; NASA-stated gas measurement purpose; measured gas signature".

## Why

The catalog and the data role's raw-file method disagreed on three points. The human lead asked catalog to judge them on theory and combine the two (`scoring/METHOD.md` 1.7).

One of the three points: the page said "met" for values that no per-test table shows. Examples: BASS-II pressure (stated in a paper), ACME-BRE pressure (record text), BASS flow (record text). That contradicts the data role's counts, which use table values only. The new status keeps the ranking, which uses documented values on purpose, but stops the word "met" from claiming test evidence that does not exist.

Ranking changes that you may see in the demo:
- Gas-signature detection questions ("CO detection on ISS", "combustion gas detection") now rank BASS-II first.
- Smoke questions are unchanged.
- FLEX and CFI show lower confidence on quiescent questions (their flow is a team reading).

## Until then

The page works as is: unknown statuses show their bare word. pm integrates `catalog-scoring` into `main` as usual.
