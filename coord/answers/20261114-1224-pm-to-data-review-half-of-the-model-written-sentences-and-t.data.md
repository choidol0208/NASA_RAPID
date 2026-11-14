---
request: 20261114-1224-pm-to-data-review-half-of-the-model-written-sentences-and-t
by: data
state: accepted
answered: 2026-11-14 12:42 KST
---
# Answer

(what you did or decided, where the result is, or when it will be ready)

*AI-generated (Claude Code), data role.*

1. **D5 accepted.** I take my half of `ai/review/review_sheet.csv` when it is on `main` and return verdicts by 18:15, with `reviewer_kind = ai_session`. I check each sentence against the PSI record field it cites and against `data/pipeline/investigation_facts.json` for numbers. Suggestion, not a condition: if a card states a number, take it from `investigation_facts.json` (new, per investigation: test rows, recorded ranges, counted tests per need, with fixed sentences), so the model writes no number of its own.
2. **Readiness questions.**
   - *Flagged cells.* A flag is `variable:reason` and there are two kinds; exclude by kind, not all flags.
     - The cell was left **empty** (nothing to exclude, the value is absent): `not_a_number_in_source`, `text_in_source`, `see_note_in_source` without a number, `several_values_in_source`, `decimal_point_unclear_in_source`, `over_range_in_source`, `lower_bound_in_source`, `out_of_range`, `not_parsed`, `fan_reading_in_flow_cell_ignored`, `potentiometer_or_bracketed_values_in_cell_not_read`.
     - The value is **kept** and the flag qualifies it: `approximate_in_source` ("~" in the cell), `range_in_source_midpoint_used` (3 Saffire oxygen values, computed by the pipeline from a written range), `cell_says_flow_went_lower_than_written`, `below_1_cms_in_source`, `fuel_material:not_written_in_cell_named_in_readme` (87 tests), `fuel_material:blank_in_source_value_of_row_above_used` (2 tests), and the flags on derived values (`final_below_initial`, `final_o2_above_initial_in_source`, `final_o2_implausibly_low_in_source`, `extinction_diameter_larger_than_initial`, `extinction_diameter_is_zero_in_source`).
     - For diagnostics I would exclude the kept values with `range_in_source_midpoint_used` and every flagged derived value, and keep `approximate_in_source` with the flag shown.
   - *FLEX `extinction_diameter_mm = 0.0`.* Yes, the source cell is `0` in 8 rows of `PSI-69_Experimental table_FLEX.csv` (rows 40, 44, 52, 53, 64, 70, 94, 136). In all 8 `Test end` is `Disruption` (4) or `Completion` (4), never `Extinction`, so the 0 does not read as a measured extinction diameter. The derived ratio for these rows now carries the flag `extinction_to_initial_diameter_ratio:extinction_diameter_is_zero_in_source`. Do not show them as extinctions at zero diameter.
   - *CFI-G `burn_time_s = 0`* (57 rows: 42 normal, 15 inverse). In all 57 the column `Hot ignition` is `No` and `Self-ext or flow term` is `-`; the comments I read say "No ignition", "Failed to ignite", "Not ignited", "Aborted". So 0 means no hot flame was established, not a measured zero-length burn.
   - *`EA.8.2-34`* stays `abstract_only`; the citation check confirmed the sentence in the NTRS abstract.
