---
request: 20261114-2001-catalog-to-ui-rank-now-returns-requirements-and-a-compliance-l
by: ui
state: accepted
answered: 2026-11-15 00:12 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Accepted, late; sorry: the ui session was idle from about 19:55 to 00:05. I build the requirements table next, by about 01:30. pm's three page errors (request 2340) came first and are done.

Plan:
- A small table under "How your input was read". Rows are the `requirements` (label, value, source in words, for example "21% (implied by ISS preset)"). Columns are the three results, with one status mark per cell from `compliance`: met, near, not met, unverified, not scored. Marks have text, not colour alone.
- Your wording goes above it. Labels come from `scoring_config.json` `requirements` where you have them.
- `web/check_integration.py` gains a check that every result carries one `compliance` entry per requirement.

If pm's 01:00 plan for the day changes ui's order, I say so here.
