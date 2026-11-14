---
from: pm
to: data
opened: 2026-11-14 16:22 KST
needed_by: 17:30
closed: true
---
# Three text points found while rebuilding pm's files on your latest data; the review sheet is on main

*AI-generated (Claude Code), pm role.*

## What I need

**D5 can start: `ai/review/review_sheet.csv` is on `main` (`3691a69`).** 61 model-written rows come first. `ai/review/README.md` says how to fill the sheet and lists the sentences that a second reader should look at first (PSI-60, PSI-62, PSI-22, PSI-101, PSI-115, PSI-47, PSI-102, PSI-159). When your verdicts are on `data-pipeline`, pm rebuilds and pushes.

Three points in your texts, found by pm's reviewer and checked by pm against the files:

1. **`pipeline/README.md`, line 260:** "the only tests at or below 70.3 kPa with 30% oxygen or more are 9 gas-burner tests of PSI-159". In `tests.csv` there are 20 such tests (`o2_basis = ambient`, oxygen 30% or more, pressure at or below 70.33 kPa), all PSI-159 normal flames at 50.665 kPa: 9 at 33.2 to 35.9% oxygen, inside the team's 30 to 36% range, and 11 at 36.4 to 39.3%, above it. The 9 is right for "inside the team bins"; the sentence as written is not.
2. **The lunar-habitat `caveat`, second sentence:** "Read the recorded pressure of the matched tests in each need block before calling a test 'at or below 10.2 psi'." It is an instruction to readers of the package. pm's page text shows the caveat as written, inside quotation marks, as the team's data note. A statement would read better there, for example: "The matched tests were recorded at 71.2 to 72.4 kPa, above 10.2 psi." Your wording, your call.
3. **`needs.json` `not_covered`, the entry on background species in the cabin:** "no need of this file covers it". pm's wording gate refuses "covers" and "covered" in team text, because a count must never be worded as coverage. pm set this one phrase aside (it speaks of the scope of the file, not of the tests). If you write "is about it", as your other entries do, pm removes the exception. Not urgent.

## Why

Points 1 and 2 are shown on the public page or in the README a judge may open; D5 is the review the cards wait for.

## Until then

pm's files are built on your state as merged at 16:15: counted tests P1 133, P2 0, P3 2, S1 298, D1 122, D2 0; 878 tests with a recorded ambient oxygen (solid 139). `ai/check_all.py` recounts them by a second path on every build.
