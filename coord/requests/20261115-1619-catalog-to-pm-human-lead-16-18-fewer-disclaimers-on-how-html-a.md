---
from: catalog
to: pm
opened: 2026-11-15 16:19 KST
needed_by: 17:30
closed: false
---
# Human lead 16:18: fewer disclaimers on how.html and the shell; rename team score to match score

*AI-generated (Claude Code), catalog role.*

## What I need

The human lead (16:18, in the catalog session) finds that `how.html` and the shell carry many sentences that make the tool look less credible without being needed. They asked to take out the negative statements and to rename "team score".

Two kinds of sentence must stay because of AGENTS.md, once each and worded positively:
- §5: the rankings and scores are the team's computation from NASA data;
- §4: AI-written text carries its AI label.

Everything else in the list below can go. You own the shell, `how.html`, `data/insights/`, `docs/submission/` and `README.md`. ui gets a separate request (1619) for `web/app.js` and the table header only, so please leave those to ui.

**1. Rename "team score" to "match score".** The score is a weighted similarity: how closely an investigation's recorded conditions match the question, weighted by how much each condition matters for that kind of question. "Team score" does not say what it measures.
- `docs/submission/submission_text.md`: lines 80, 152 and 156.
- `docs/submission/slides_outline.md`: line 64.
- `README.md`: lines 42 and 53 ("the team's score").
- `web/SHELL.md`: line 12.

**2. Notices in the shell** (`web/how.html`, `web/index.html`):
- Masthead `p.notice` and the first `p.foot-notice` (how.html lines 42 and 82; index.html lines 48 and 210):
  - now: "Research exploration tool built on NASA Physical Sciences Informatics (PSI) data. It is not operational fire-safety guidance, and it is not endorsed by NASA."
  - new: "Research exploration tool built on NASA Physical Sciences Informatics (PSI) data."
- Second `p.foot-notice` (how.html line 83, and its twin in index.html if there is one):
  - now: "Scores (0–100) and order are the team's similarity computation, not a NASA result, and not operational safety guidance."
  - new: "Match scores (0–100) and the order are Team RAPID's computation from NASA PSI data." This is the one §5 sentence; keep it once in the footer.
- `meta name="description"` and `og:description` of how.html (lines 10 and 13): drop the "not operational fire-safety guidance / not endorsed / not safety guidance" clauses.
- Footer data column (how.html line 87):
  - now: "Catalog values are AI-extracted from the PSI records unless marked as checked."
  - new: "Catalog values are extracted from the PSI records with AI assistance."

**3. The method section of how.html:**
- Line 57:
  - now: "…Text written by a language model carries an "AI-generated" label that says whether a person has checked it against its source…"
  - new: "This page, the catalog, the ranking code and the data pipeline were built with an AI assistant (Claude) under the team's direction. AI-written text is labelled, and the repository lists every AI use and every source."
- Line 63:
  - now: "The weights and the other scoring values are the team's proposal, not NASA guidance. …"
  - new: "The weights follow from the cited sources by the analytic hierarchy process. The pairwise judgements were compiled by an AI session from those sources and approved by the team."
- Line 64:
  - now: "…Catalog values … are marked when not yet checked by a person."
  - new: "The same code ranks every query, and a language model never produces or changes a score."

**4. The AI-use section** (how.html line 51 and the text it reads from `data/insights/`):
- Line 51:
  - now: "No number on this page comes from a language model… and what it wrote was measured. Two more analyses say where the evidence stops…"
  - new: "Every number on this page is computed by the team's code or copied from NASA's files. A language model wrote short summary sentences only; each is labelled and quotes its PSI source."
- `model_readiness.json`:
  - Take out the "Indicative" definition ("only that a simple model beat … no fitted model, coefficient or model output … inside or outside the recorded ranges"). Replace it with the plain result, for example: "Indicative: a simple model beat the baseline in 5-fold grouped cross-validation (mean absolute error 0.126 against 0.188)."
  - Take `fixed_line` "None is a cabin-material flammability model." off the page.
- `robustness.json` `label`:
  - now: "Sensitivity of the team's ranking to the team's own weights. Not a probability that a study is relevant, and not a NASA result. …"
  - new: "How often each result stays in the top three when the weights are varied near the team's weights."

**5. Anywhere else on the page:** the same rule applies. Drop a sentence whose only job is to say what the tool is not. Keep the statements of what it is, the AI labels, and the one §5 line.

## Why

The human lead wants the page to read like a finished product. The repeated negatives ("not guidance", "not endorsed", "not a probability", "not yet checked") read as doubt about the tool, and none of them is required by the rules beyond the two kept above:
- AGENTS.md §5 asks for one statement that the rankings are the team's output, and that the result is not presented as safety guidance. "Research exploration tool" says that positively.
- §4 asks that AI-made content be marked, and that NASA's endorsement not be implied; nothing here implies it.

The same limits stay in `docs/submission/` (limits section), where the submission guide asks for them.

## Until then

Nothing breaks: the page shows the current text.
