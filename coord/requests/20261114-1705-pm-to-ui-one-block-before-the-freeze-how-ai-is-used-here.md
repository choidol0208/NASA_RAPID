---
from: pm
to: ui
opened: 2026-11-14 17:05 KST
needed_by: 18:45
closed: false
---
# One block before the freeze: how AI is used here and how it was checked (three files that are already built)

*AI-generated (Claude Code), pm role.*

## What I need

**One block on the page, by 18:45, titled "How AI is used here, and how it was checked".** The human lead's concern at 17:05: on the page, AI looks like "a language model writes summaries" and nothing more, which is neither the whole truth nor a reason to remember the project. Three analyses are built, checked and on `main`, and the page reads none of them. All text below comes from the files; the page computes nothing.

1. **The language model, measured** (`data/insights/quality.json`). One line of five numbers, in this order: `proposed` (70 sentences written by the model), `dropped_by_gates` (5 refused by code checks), `removed_before_review.n` (4 removed by a first reading), `removed_by_review` (28 removed by the review), `shipped_model_sentences` (33 shown). Under it: "Reviewed by a second AI session: `reviewed_ai_session`. Reviewed by a person: `reviewed_person`." Fixed sentence: "A sentence is shown or not shown; none is reworded. Every shown sentence cites the NASA sentences it rests on."
2. **Can a predictive model be trained on these tables?** (`data/insights/model_readiness.json`). Print `title`, then `labels_and_limits` as the note, then one line per entry of `rows`: `label` and `verdict`; where `baseline` and `model` are not null, add "`model.name`: `model.metric` `model.mean`, against `baseline.mean` for the base rate". End with `fixed_line`. Today that is nine outcomes: one "simple model beats the base rate on held-out conditions (indicative)", one counts only, one not modelable, six "too few". No fitted model is shipped, and the block must not suggest one.
3. **Does the ranking depend on the team's weights?** (`data/insights/robustness.json`). Under each of the three result cards of a demo query, print that result's `display_line` (find the run by `query`, the result by `investigation_id`). Print the file's `label` once as the note. The lines already pass pm's wording gates; please print them as they are.

`web/build.py` needs to copy the three files. Where the block goes is your call; next to "How the score works" would do, folded or not. If time is short, parts 1 and 2 matter more than part 3.

Priority among pm's open requests: the map axis (1622, item 2) first, then this block, then the rest of 1622.

## Why

It shows what the project actually did with AI: code computes every number; the language model is measured and more than half of what it wrote was refused; a cross-validated test says for which outcomes these tables can and cannot support a predictive model; the ranking's stability is sampled. That is the same idea as the rest of the page: say where the evidence stops, also for our own AI.

## Until then

pm is rebuilding `data/insights/` once more today (eight quotes that the review marked not relevant will no longer be shown, four template sentences are reworded); the numbers in `quality.json` then change slightly, which is why the block should read them from the file.
