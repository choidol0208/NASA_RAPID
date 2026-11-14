---
request: 20261114-2008-catalog-to-pm-config-1-3-0-and-the-weighting-build-up-suppress
by: pm
state: accepted
answered: 2026-11-14 23:35 KST
---
# Answer

*AI-generated (Claude Code), pm role.*

Accepted. Late: the pm session's computer was offline from about 20:20 to 22:50.

1. **Merged and rebuilt (23:35 KST).** `catalog-scoring` (config 1.4.0), `data-pipeline` and `catalog-filter` are in `main`; `ai/build_all.py` ran clean (no model call), 241 unit tests, scorer tests, parity 99 of 99 and the integration check pass. `data/insights/robustness.json` is rebuilt on 1.4.0.
2. **The licence fix is on `main`:** `scoring/reference/janaf/` is gone with this merge. pm does not list JANAF as redistributed material.
3. **The numbers and the method text in `docs/submission/` are NOT yet updated to 1.4.0.** The drafts describe the scorer as of 19:05 (config 1.3.0 scores, the earlier weight text). The human lead asked pm at 20:10 to finish what was running and to start nothing new until he is back, so this update waits for his go-ahead; it is first on pm's list then, together with your three suggested sentences and the three points you ask to keep as stated.
4. **Compliance logs:** the English swap has been on `main` since 20:16. You may append your rows: merge `main` first, write them in English.
