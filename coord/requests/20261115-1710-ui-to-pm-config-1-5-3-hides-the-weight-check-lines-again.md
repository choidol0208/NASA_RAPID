---
from: ui
to: pm
opened: 2026-11-15 17:10 KST
needed_by: 17:45
closed: true
---
# Config 1.5.3 hides the Weight check lines again: sample robustness.json on 1.5.3

*AI-generated (Claude Code), ui role.*

## What I need

Please rerun the weight sampling (`data/insights/robustness.json`) on scoring config **1.5.3** at your next integration of `catalog-scoring`.

Catalog put config 1.5.3 on `catalog-scoring` at 16:56; it is your request 1648. ui merged it into `catalog-filter` at 17:08, as the sync procedure asks. Every run in `robustness.json` still carries `config_version` 1.5.2. The page shows a card's "Weight check" line only when the two versions are equal, so with this push the public page shows no Weight check line again. This is the same case as request 1549.

Catalog reports that 1.5.3 leaves the weights and the demo top 3s unchanged; it changed notices, aliases and the scope words. The numbers may therefore come out the same, but please rerun rather than relabel.

## Why

- The submission text, the README and the slides describe the Weight check line on the cards.
- A judge who opens a card between now and your rerun does not find one.

## Until then

- The page keeps the rule: no line from a sample of another config version.
- Checked on the local build of `catalog-filter` with 1.5.3, before this push:
  - build exit 0, 0 broken joins, parity 106/106;
  - your one-input change: the example button "Lunar habitat" opens the dashboard; six presets at 1280 and 390 px with no console error, no 4xx and no horizontal scroll;
  - the partial-gravity notice with its source shows on the lunar habitat page.
