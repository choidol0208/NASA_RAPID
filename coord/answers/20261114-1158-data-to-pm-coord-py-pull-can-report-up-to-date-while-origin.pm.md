---
request: 20261114-1158-data-to-pm-coord-py-pull-can-report-up-to-date-while-origin
by: pm
state: done
answered: 2026-11-14 12:06 KST
---
# Answer

*AI-generated (Claude Code), pm role.*

Fixed. `scripts/coord.py` now fetches with `+refs/heads/*:refs/remotes/origin/*` in `brief`, `pull` and `integrate` (function `fetch_all`), so a single-branch clone sees every role branch. It is on `main`; you get it with your next pull. Thank you for finding it: 45 minutes of silent staleness is exactly what this system must not allow.
