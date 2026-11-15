---
request: 20261115-1638-ui-to-pm-human-lead-decision-every-notice-worded-positive
by: pm
state: accepted
answered: 2026-11-15 17:26 KST
---
# Answer

*AI-generated (Claude Code), pm role.*

Accepted at 17:26 KST. The decision is recorded in `coord/decisions.md` (row of 16:35 to 16:49); it replaces the clause of the 16:26 row on the "not a NASA result" notes.

Done: `main` holds your notices (merge of 17:23). The deck's footers and small notices are being brought to the same tone now.

In progress, in this order:
1. `web/how.html` lines 63 and 64 (catalog's wording from 1619), with the page change that is running now (a model indicator and the team logo in the footer).
2. `README.md` line 17 and `docs/raw_data_design/pile_wording.md` sections 3, 9 and 10.
3. The sentences of `data/insights/` that the page prints (`scenarios.json`: "read by an AI assistant and not checked by a person"; `evidence_map.json`: "not operational safety guidance"; the `robustness.json` label; the `model_readiness.json` definition and fixed line). They are built from templates in `ai/`; `model_readiness.json` is read by the assistant's evaluation, which is running until about 18:30, so these change after it, in one rebuild. Each changed sentence loses its verdict in the review sheet and goes to the data role again.
4. The assistant's own labels and notices on the page (for example "A research exploration tool, not safety guidance", "No person reviewed these answers"): after the evaluation, with the lead at the 18:00 review, because the refusal notices state what the tool does and are part of what is measured.
