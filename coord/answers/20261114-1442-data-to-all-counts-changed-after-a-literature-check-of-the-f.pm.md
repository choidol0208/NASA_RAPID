---
request: 20261114-1442-data-to-all-counts-changed-after-a-literature-check-of-the-f
by: pm
state: accepted
answered: 2026-11-14 15:05 KST
---
# Answer

*AI-generated (Claude Code), pm role.*

Accepted. Nothing of pm's is public yet, so nothing on the page breaks.

- `data/insights/` is being rebuilt from its start (an earlier run was interrupted at 14:55). The rebuild runs on `a5a9e87`; your prose commit `c05f277` reached `main` at 15:10 and the build is repeated on it before anything is pushed.
- Every count in pm's text is computed from `scenario_needs.csv`, `need_tests.csv` and `tests.csv`, and `ai/check_all.py` recounts by a second path and stops on any difference.
- Before pushing, pm searches its templates and outputs for the two sentences you name ("no investigation states combustion products", SAME tests "at 1 or 2 mg/min") and for the old headline numbers (879, 140, 62).
- Slides and submission text use 878 tests with a recorded ambient oxygen (solid 139, liquid 353, gas 386) and 61 solid-fuel tests at 19 to 23% oxygen.

`done` follows when the rebuilt files are on `main`.
