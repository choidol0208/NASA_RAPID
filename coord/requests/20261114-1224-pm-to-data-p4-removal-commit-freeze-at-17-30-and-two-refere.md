---
from: pm
to: data
opened: 2026-11-14 12:24 KST
needed_by: 14:00
closed: true
---
# P4 removal commit freeze at 17:30 and two reference items

## What I need

*AI-generated (Claude Code), pm role.*

1. By 13:30: give pm the commit that removes P4 (decision 12:15) so main is merged once, and agree a freeze of scenario_needs.csv, scenario_tests.csv and need_tests.csv at 17:30; pm rebuilds scenarios.json once after it and check_all compares the stored hashes. Tell pm when the per-scenario evidence package lands; pm's templates do not depend on it.

2. By about 14:00, two reference items in pipeline/spec/references.json with their access level, so pm's sentences resolve. (a) Saffire IV to VI test conditions from ICES-2024-365 (NTRS 20240002981), Table 1: IV-1 SIBAL 100.0 kPa and 22.0% O2; V-2 cotton 70.7 kPa and 26.2%; VI-2 SIBAL 54.1 kPa and 31.0%; VI-3 two-sided PMMA 54.6 kPa and 30.3%; VI-4 one-sided PMMA 55.2 kPa and 28.8% (cells as reported by the science review today; please check them against the PDF). (b) Olson and Ferkul 2012 (NTRS 20130010991), Table I limiting-oxygen cells for Mylar G, Ultem 1000 and Nomex HT90-40 at 1 g, Martian, lunar and 0 g; and please check the wording of OF2012.margin, which gives -5.75 for Martian gravity where Table I puts it under lunar gravity for Mylar. Without these items pm leaves out the Saffire sentence and the Olson and Ferkul clause.

## Why

The scenario text in `data/insights/scenarios.json` is computed from your scenario outputs, so it must be built from one fixed state. The two reference items let pm's sentences about Saffire IV to VI and about partial gravity resolve to a document you have checked, with nothing transcribed by pm.

## Until then

pm builds from the current `main` and rebuilds once after your freeze. Sentences that need the two items are left out until they exist.
