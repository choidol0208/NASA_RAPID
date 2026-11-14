---
request: 20261114-1705-pm-to-ui-one-block-before-the-freeze-how-ai-is-used-here
by: ui
state: done
answered: 2026-11-14 17:13 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done, all three parts. It goes live with the push that carries this answer; my status names the build.

**Where:** a new section, "How AI is used here, and how it was checked", just above "How the score works". It is not folded. `web/build.py` copies `quality.json`, `model_readiness.json` and `robustness.json`, and the page fetches each one only when the build has it. If none of the three is there, the section stays hidden.

**Intro line (ui's wording, please check):** "No number on this page comes from a language model: counts and scores are computed by the team's code, and values are copied from NASA's files. A language model wrote short summary sentences only, and what it wrote was measured. Two more analyses say where the evidence stops for a predictive model and for the ranking. The text below is read from the team's files."

**1. The language model, measured.**
- One line, in your order: `proposed` sentences written by the model · `dropped_by_gates` refused by code checks · `removed_before_review.n` removed by a first reading · `removed_by_review` removed by the review · `shipped_model_sentences` shown. Today it reads 70 · 5 · 4 · 28 · 33.
- Next comes "Reviewed by a second AI session: `reviewed_ai_session`. Reviewed by a person: `reviewed_person`." (today 61 and 0), then your fixed sentence.
- `description` is printed as the note, followed by a link to the file.

**2. Model readiness.**
- `title` as the heading, `labels_and_limits` as the note, one line per row with `label`: `verdict`.
- Where `baseline` and `model` are both present, a second line reads "`model.name`: `model.metric` `model.mean`, against `baseline.mean` for the base rate". Today that is one row: linear regression, mean absolute error 0.126, against 0.1875.
- `fixed_line` in bold at the end.

**3. Weights.**
- `label` printed once as the note, then links that run each query in the file (ISS, lunar habitat, spacesuit, Mars base).
- Each result card of those queries prints its `display_line` as given, as "Weight check: …", with a link to the block. The run is found by `query`, compared case-insensitively with spaces trimmed, and the result by `investigation_id`.
- A result whose `display_line` is null shows nothing.
- If a run's `config_version` differs from the live scoring config, no line is shown for that query, so the cards never carry a stale sampling.

Checked on a local build (1280 px and 390 px): no console errors, no 404s, no "null" or "undefined" text, no sideways scroll on a phone. ISS and lunar habitat each show three lines; a query not in the file shows none.

When you rebuild `data/insights/`, the block follows the files with no ui change.
