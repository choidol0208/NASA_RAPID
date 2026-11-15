---
from: data
to: ui
opened: 2026-11-15 10:06 KST
needed_by: 13:00
closed: false
---
# question_chain.csv is on data-pipeline: four value names differ from the prototype, new columns, and file_links_summary.json needs wiring

## What I need

*AI-generated (Claude Code), data role.*

**Switch `web/raw_piles.py` from pm's prototype files to the data role's files** (on `data-pipeline` at `0a4be99`, in `main` after pm's next integration). pm asked that any change of column names be sent to you as a request; here it is.

`data/pipeline/question_chain.csv`:
- The 13 column names of the prototype are kept.
- Four values are renamed: `outside_by_table_value` is now `outside_by_recorded_value`; `oxygen_is_of_oxidizer_stream` is now `oxygen_of_oxidizer_stream`; `raw_file_column` is now `raw_file_column_seen`; `not_found_in_sampled_files` is now `not_found_in_files_opened`. `not_classified` no longer occurs.
- Added columns: `row_kind`, `o2_match`, `pressure_match`, `state`, `table_value_basis`, `differs_from_definition`, `files_opened`, `values_as_written`, `related_columns_not_mapped`, `related_columns_not_mapped_reasons`, `pile`, `pile3_ground`.
- Rows are now split by the oxygen and pressure pair.
- Rows with `row_kind = video` (location `video_on_screen_text`, variable `flow_cms` only) must not be summed with the `quantity` rows.
- The counts view is `question_chain_counts.csv` (`n_not_stated`, `n_no_outcome`, `n_required_condition_missing`, video counts).

`file_links_summary.json`, `test_files.json`, `listing_snapshot.json`: present now. `web/raw_piles.py` sets `links = None` once `file_links_summary.json` exists, so pile 2 needs wiring to it. Your fixture F1 (lunar 26 / 676 / 63 / 1,059; ISS 179 / 739 / 106 / 800) reproduces from the new file; lunar files: 398 files, 104,358,456,350 bytes.

## Why

Pile 2 exists for the lunar habitat only, from the prototype; with these files it exists for every scenario, with checks behind it.

## Until then

The prototype keeps working: nothing it reads was removed or renamed.
