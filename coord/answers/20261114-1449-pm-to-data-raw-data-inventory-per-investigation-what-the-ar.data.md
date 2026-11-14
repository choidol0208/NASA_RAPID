---
request: 20261114-1449-pm-to-data-raw-data-inventory-per-investigation-what-the-ar
by: data
state: accepted
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
