---
request: 20261114-1224-pm-to-data-review-half-of-the-model-written-sentences-and-t
by: data
state: done
answered: 2026-11-14 16:34 KST
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

## D5 done (16:35 KST), on `data-pipeline` at `49982b4`

All 385 rows of `ai/review/review_sheet.csv` (as on `main` at `3691a69`) carry a verdict, `reviewer_kind = ai_session`, `reviewer_role = data`. Only the five reviewer columns changed; the file round-trips byte-identically otherwise.

- **Model rows (61):** each read by two independent AI readers against the cited field of the PSI record, neither seeing the other. Where they differ the stricter verdict is recorded and the note gives both. Result: 33 `supported`, 28 `partly` (one of them with `modality_kept = no`: PSI-23 summary 1, "is proposed / will be issued" turned into "involved issuing"), 0 `not`. Both readers agreed on 18 of the 28; 10 are one reader only. Most `partly` rows are of one kind: the first of several listed objectives worded as the investigation's aim, or a scope word lost (PSI-60 "ground", PSI-101 "Along with the results from the original SAME investigation", PSI-22 "investigates" to "investigated"). If you think the one-reader rows are too strict, the notes say what each reader saw; I recorded the stricter one because a removed sentence falls back to the NASA quote.
- **Quote rows (98):** 90 `relevant`, 8 `not_relevant` (all verbatim; the field label misdescribes the sentence or it has no antecedent alone: PSI-20 APP-1, PSI-21 IMP-6 and APP-1, PSI-23 HYP-1, PSI-26 OBJ-3, PSI-68 HYP-1, PSI-99 HYP-4, PSI-159 summary HYP-1).
- **Template rows (226):** 222 `wording_ok`, 4 `wording_issue`: `scenario:spacesuit:gap:5` ("every test in the PSI tables is a microgravity test": `gravity_level` is a constant of the team's source mapping for the 1,824 mapped tests, not a table column; say "every counted test"), `scenario:spacesuit:note:PSI-68` and `note:PSI-62` (closing boilerplate speaks of listed results and inverse flames for records that have none), `scenario:mars_habitat:gap:5` ("Required monitoring targets" without naming who requires them).

One correction to my answer above: the flag `range_in_source_midpoint_used` no longer exists. Since 14:40 the pipeline computes no midpoint; a Saffire oxygen cell written as a range is left empty unless a publication names the value, and the range is kept as written in `o2_range_as_written`.
