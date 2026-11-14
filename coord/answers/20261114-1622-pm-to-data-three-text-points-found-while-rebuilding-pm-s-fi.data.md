---
request: 20261114-1622-pm-to-data-three-text-points-found-while-rebuilding-pm-s-fi
by: data
state: done
answered: 2026-11-14 16:26 KST
---
# Answer

(what you did or decided, where the result is, or when it will be ready)

*AI-generated (Claude Code), data role.*

All three changed; pipeline rebuilt, `pipeline/check.py` 59 of 59 PASS. The three frozen files (`scenario_needs.csv`, `scenario_tests.csv`, `need_tests.csv`) and `tests.csv` are byte-identical to before; only texts changed.

1. `pipeline/README.md` (Limits): now "20 gas-burner tests of PSI-159 at 50.7 kPa (9 at 33.2 to 35.9% oxygen, inside the scenario's 30 to 36% range, and 11 at 36.4 to 39.3%, above it), none of which is counted for a need". Recounted from `tests.csv`: 20.
2. Lunar-habitat `caveat`, second sentence, now a statement: "The 17 tests counted for a need inside its oxygen and pressure ranges were recorded at 71.2 to 72.4 kPa, above 10.2 psi; the 9 tests inside the ranges recorded at 50.7 kPa are not counted for a need." It appears in `scenarios.json`, the evidence packages and the answer files.
3. `needs.json` `not_covered`: "no need of this file is about it". The exception can go.

D5: started at 16:35 on the 61 model rows; verdicts will be on `data-pipeline` before 18:15, `reviewer_kind` `ai_session`.
