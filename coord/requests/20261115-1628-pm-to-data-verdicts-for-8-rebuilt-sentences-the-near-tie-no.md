---
from: pm
to: data
opened: 2026-11-15 16:28 KST
needed_by: 19:00
closed: false
---
# Verdicts for 8 rebuilt sentences: the near-tie note now says 'match score' (the human lead's decision)

## What I need

*AI-generated (Claude Code), pm role.*

Verdicts for the 8 rows of `ai/review/review_sheet.csv` that have none after the rebuild of 16:28 (`main`, `b75703b`). They are the result notes that end with the near-tie sentence; its wording changed in one word pair: "Listed because its **match score** is level with or close to the results shown, under the team's current weights." (it said "team score"). Nothing else in those notes changed. Find them with an empty `verdict` cell; same procedure as before.

## Why

The human lead decided at about 16:25 that the number on a result is called "match score" on the page, in the assistant, in the deck and in the texts (`coord/decisions.md`): "team score" says who computed the number, not what it measures. The notes that scores and order are the team's computation and not a NASA result are unchanged. If your files or texts say "team score" anywhere a visitor reads it, please use "match score" too; `pipeline/` and `data/pipeline/` were searched and hold no such string.

## Until then

The 8 sentences are shown with the label for code-built text that has no verdict yet.
