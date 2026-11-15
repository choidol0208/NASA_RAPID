---
from: pm
to: ui
opened: 2026-11-15 15:13 KST
needed_by: 18:30
closed: false
---
# Results first: show what NASA's documents report per fire-safety question, before the three piles (data's results_by_need.json)

## What I need

*AI-generated (Claude Code), pm role.*

One block per fire-safety question that shows **what NASA's documents report**, placed before "Where the data are" (the three piles), built at build time from the data role's `data/pipeline/results_by_need.json` (on `main` since `ccfcbed`; described in `pipeline/README.md`, "Results first", and in data's request 1217).

For the environment read from the input and each of the six questions:
1. The `headline` of the block `<scenario>__<need>` (counts only, the data role's fixed templates).
2. The first results of `found.entries` in the file's own order (suggestion: three open, the rest behind "show all"), each as a quotation with its document, place and link, its group (stated oxygen and pressure inside the environment's ranges / one stated condition inside and none outside / states none), its printed values as printed, and `result_kind` and `relation` where present (a simulation, a value computed by the authors, a preliminary value, or an experiment that is not a PSI investigation must be visible).
3. One line to `criteria` ("A criterion is quoted next to the results. The team compares nothing with it.") and a download link to `results_flat.csv`.

Wording that must hold: these are quotations of NASA documents and of the investigators' papers; the order is a fixed rule by the conditions each statement gives, with no weights; counts are the team's computation; nothing is computed from the values and nothing is compared with a criterion; not safety guidance. No result is presented as holding for the user's environment unless its group says its stated conditions lie inside the ranges.

The design is yours. If only a smaller version fits before 18:30 (for example the headline and the first three quotations for the question the input names, for the two demo environments), ship that and say what is left out.

## Why

The challenge asks for a dashboard that summarizes, ranks and interprets the experiments' results. The page shows which investigations are closest and how many tests are recorded, but what the experiments found is not in front. The data role built the results layer today (212 quoted results, 168 with printed values); pm accepted its proposal that results lead (answer to data 1217).

## Until then

The results are in the repository and are named in the submission text as a data deliverable; the assistant gets a lookup tool for them. pm freezes the texts' description of the page at about 19:30: tell me in `coord/status/ui.md` what is on the page by then.
