---
from: pm
to: ui
opened: 2026-11-14 14:49 KST
needed_by: 18:30
closed: false
---
# Find Compare Interpret labels export with citations raw data line

## What I need

*AI-generated (Claude Code), pm role.*

Direction from the human lead (`coord/decisions.md`, 15:00): the page should read as the answer to the challenge's sentence that the data are "hard to find, harder to compare, and harder yet to interpret". Three small items, after request 1306, in this order; stop wherever time runs out.

1. **The three verbs as section labels.** Put a short label above each result section, using the challenge's words: "Find" over "Closest NASA investigations", "Compare" over the recorded-tests views (the needs table and "Recorded tests in your atmosphere"), "Interpret" over "What to consider" and "Where the evidence stops". One sentence under the title can quote the challenge: "NASA's combustion data are hard to find, harder to compare, and harder yet to interpret." Wording is yours.
2. **Export with citations**, so a researcher can leave with the data: on a result, links or buttons to download (a) the matched tests of the current scenario as CSV with their source file, row and flags, (b) the scenario's evidence package (`data/pipeline/evidence/scenario_<id>.json`), and (c) a "How to cite" block listing the dataset DOI of every investigation in the download (PSI asks for citation by DOI; they are in `data/psi/manifest.json`). Plain links to the repository files at the built commit are enough where a file already exists.
3. **One line of raw-data inventory per investigation**, when data's `raw_inventory` file reaches `main` (request 1500 to data): for example "Raw data in PSI: 296 videos (17.7 GB), 264 archives of stills and original video (257 GB), no sensor log". Read it from the file; show nothing if the file is absent.

## Why

Analysis happens in the researcher's own tools (decision 15:00), so the page must hand over clean, cited data and say what else the archive holds. The three labels make the structure of the page match the challenge text a judge has just read.

## Until then

pm finishes the model-written summaries and the evidence-map file and announces the push in its status.
