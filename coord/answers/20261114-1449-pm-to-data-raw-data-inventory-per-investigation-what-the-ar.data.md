---
request: 20261114-1449-pm-to-data-raw-data-inventory-per-investigation-what-the-ar
by: data
state: done
answered: 2026-11-14 14:56 KST
---
# Answer

(what you did or decided, where the result is, or when it will be ready)

*AI-generated (Claude Code), data role.*

Accepted, in progress, target 16:30. A sub-agent builds it now from the PSI file listings only (no data file is downloaded):

- `data/pipeline/raw_inventory.json`: one entry per investigation with files and bytes by PSI category (names as PSI gives them) and by kind (video, still image, archive, sensor or telemetry table, experimental table, document, other), one example name per kind, the test-id pattern in file names where the names show one (no mapping to table rows), and one fixed sentence filled with those numbers.
- The kinds are decided from file names and PSI categories by rules in `pipeline/spec/raw_kinds.json`; no file is opened. A name that does not say what it is stays "other".
- `pipeline/raw_inventory.py` rebuilds it; the listings are saved under `data/psi/file_listings/`.
- Your quick look for PSI-25 and PSI-98/99/100 is checked against the listings; I report the numbers when it lands.
- The optional `scripts/psi_whats_new.py` only if time remains before the freeze.

I change this answer to `done` with the commit.

**Update 15:25 KST: done** (commit with this answer on `data-pipeline`).

- `data/pipeline/raw_inventory.json`: 24 entries; each has `files`, `bytes`, `by_category` (PSI category names), `by_kind`, one example name per kind, `test_id_in_file_names` where the names show a pattern, and `sentence`. Rebuild: `python3 pipeline/raw_inventory.py` (offline from saved listings; `--refresh` fetches the listings again). Name rules: `pipeline/spec/raw_kinds.json`. One paragraph in `pipeline/README.md`.
- Totals over the 24 investigations: 60,866 files, 13.47 TB (each file id counted once; six listings repeat rows, kept as `listing_rows`). Archives hold 96% of the bytes, and 10,501 of them (11.83 TB) have names that do not state what they hold.
- Your quick look, checked against the listings:
  - PSI-25 "685 raw files": agrees for the category Raw Data (the whole listing has 695). "296 MP4 (17.7 GB)": agrees. "264 archives, 257 GB": agrees (256.7 GB). "125 proof-sheet PDFs": agrees, all 125 names contain "ProofSheet". "No sensor log": agrees for Raw Data.
  - "Original .ts video and Nikon .NEF stills": the names confirm this only in part. 113 archive names say "original videos" (25.5 GB), one says `original_NEF_images` (2.8 GB), and 150 archives (228.4 GB) do not state their content; 91 of those are named like ISS photo numbers (`iss038e051108.zip`). No PSI-25 name contains ".ts". Please do not write that the 257 GB are video and stills.
  - PSI-98, 99, 100: spreadsheets named "Sensor Data" or "Telemetry Data" under Raw Data: 3 (52.7 MB), 10 (210.1 MB), and 4 xlsx + 2 csv (64.8 MB). Image archives by name: 48 of 61, 168 of 186, 63 of 67. CSV only in PSI-100.
- Limits, also in the README: kinds come from file names and PSI categories only, no file was opened; 35,738 files (34.5 GB) are "other", among them 18,248 `.dat` files of PSI-106 and unmarked spreadsheets under Analyzed Data of PSI-101 and PSI-102, so a sentence that says "no file is named as a sensor, telemetry or data table" means only that no name says so. `by_category` shows where such files sit.
- The saved listings (30 MB) are in `data/psi/file_listings/`, which `.gitignore` already excludes; a fresh clone fetches them again with `--refresh`.
- Optional item: `scripts/psi_whats_new.py` exists (read-only; compares the live PSI study list and listings with the manifest and the saved listings; prints differences; never downloads data). Run at 15:00 KST: 24 combustion investigations of 133, no difference.

