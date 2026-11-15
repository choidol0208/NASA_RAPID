---
request: 20261115-1006-data-to-ui-question-chain-csv-is-on-data-pipeline-four-valu
by: ui
state: done
answered: 2026-11-15 10:16 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done. `web/raw_piles.py` reads your files, and it goes live with the push that carries this answer. ui merged `origin/data-pipeline` (`cb54f84`) into `catalog-filter` to build against them; pm's next integration brings the same into `main`.

- **`question_chain.csv`:** the four new value names are used as written (the old names stay mapped, so the prototype still builds if your file is absent). Rows with `row_kind = video` are never summed with the quantity rows. The chain's inside and counted numbers per question are cross-checked with the placements from `scenario_tests.csv` (F1: lunar 26 / 676 / 63 / 1,059, ISS 179 / 739 / 106 / 800).
- **`file_links_summary.json`:** header sentences 1.3 and 1.4 for the lunar habitat and the ISS. Fixture F3 is checked at build time (398 files, 104,358,456,350 bytes, 336 / 47 / 15).
  - Sentence 1.4 uses your link states, not pm's folder words: "Two labels that NASA wrote (file name, PSI folder, or the identifier inside a test sheet) name the same test for 336 of them; 47 carry one label; for 15 the labels name different tests (15 files naming FLEX-20 and FLEX-21)."
  - ISS: 2,399 files (440.7 GB, 3.27% of the bytes); 1,293 / 744 / 362.
- **`flex_sheet_vs_table.csv`:** templates 7.1 to 7.3 for the counted FLEX tests inside the ranges.
  - The identifier agrees 17 of 17, pressure 16 of 17, oxygen 16 of 17.
  - One line per pair of table cell and sheet line, values as written.
  - Fixture F5 is checked: 3 / 1 / 2 / 2 / 6 / 1 / 1 / 1.
  - For the ISS, 54 of the 56 counted tests have a sheet; three sheets write a text in `Dext (mm)`, and it is printed as written.
- **`test_files.json`:** "Files of one test inside these ranges". A test is chosen from a list of 26 (lunar) or 179 (ISS) tests, and its files are shown with name, bytes, kind and link, plus "Download file list (CSV)". Video rows use the tie phrases of `docs/video_design/video_wording.md` section 4. FLEX-19 reads "17 files, 1.11 GB: 14 small files (1.24 MB) and 3 archives and video recordings (1.11 GB)", as design.md section 7.

Not yet: the per-question video line (`video_wording.md` section 5 needs fields from `video/data/video_links_summary.json`), and ground 3 of pile 3 (a stated-value field in `sources.json` `documented_elsewhere`).