---
from: pm
to: data
opened: 2026-11-14 14:49 KST
needed_by: 17:00
closed: false
---
# Raw data inventory per investigation what the archive holds

## What I need

*AI-generated (Claude Code), pm role.*

The human lead has set the project's direction in the challenge's own words (`coord/decisions.md`, 15:00): help a researcher FIND, COMPARE and INTERPRET NASA's combustion data fast. "Fast" starts with knowing what the archive holds without downloading it.

1. **A raw-data inventory**, one entry per investigation, from the PSI file listings you already fetch (no file download): for each of the 24, the number of files and total bytes by kind (video, still images, archives of either, sensor or telemetry tables, documents, experimental table), the PSI category names as given, and for the largest kinds one example file name. Where file names carry a test id (BASS-II: `..._SAMPLE_147_TEST_B1.mp4`), say so and give the pattern; do not guess a mapping. A file such as `data/pipeline/raw_inventory.json` plus one line in `pipeline/README.md`; shape is yours. Kinds you cannot classify from the name stay "other".
   - pm's quick look, for you to check: PSI-25 lists 685 raw files: 296 MP4 (17.7 GB), 264 archives (original `.ts` video and Nikon `.NEF` stills, 257 GB), 125 proof-sheet PDFs, and no sensor log; PSI-98, 99 and 100 list telemetry spreadsheets and CSV next to image archives.
2. **Optional, only if time remains:** a read-only command that compares the live PSI listing with `data/psi/manifest.json` and prints what is new (investigations, tables, raw files), for example `python3 scripts/psi_whats_new.py`. No automatic fetching.

## Why

A researcher today cannot tell what is inside 13.5 TB without opening each record's file tree. One line per investigation ("296 videos named by test, no sensor log" or "telemetry spreadsheets at 1 Hz") tells them where the analysable material is. It also backs the team's rule that data are read from video only where no numeric file exists.

## Until then

ui shows the line on each investigation once the file is on `main`; until then the page says nothing about raw data.
