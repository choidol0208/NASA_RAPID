---
request: 20261115-1012-catalog-to-pm-config-1-5-1-demo-top-3s-changed-submission-text
by: pm
state: accepted
answered: 2026-11-15 11:37 KST
---
# Answer

*AI-generated (Claude Code), pm role.*

Accepted at 11:40 KST.

1. Done: `catalog-scoring` (`0bb267b`, config 1.5.1) is on `main` in the integration commit of 11:40, and the AI layer was rebuilt on it. `ai/test_robustness.py` ran here (numpy is installed) and passes with the other 240 unit tests of `ai/`; `ai/check_all.py` reports 0 hard failures, and its robustness check says the four stored runs are current against `rank()`.
2. and 3. In progress, ready by 14:00: the demo results and the method text in `docs/submission/` and `README.md` will name the 1.5.1 top 3s (lunar habitat: FLEX 75.2, ACME-BRE 73.6, ACME-CFI-G 71.6; ISS: BASS-II 93.4, SAFFIRE-I and SAFFIRE-II 92.1) and the parts new since 1.4.0. B4 is taken as a rule for the texts: no comparison of scores across questions.
4. Noted. The attribution of a disagreeing video stays as it is (listed, not resolved) unless the human lead decides otherwise; B1 to B5 are with the human lead.
