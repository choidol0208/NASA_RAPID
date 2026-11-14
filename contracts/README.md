# Contracts: who produces which file, who reads it

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. Written by pm. The sections on `data/pipeline/`, `data/catalog/` and `scoring/` describe what the data and ui roles built; their own READMEs are the authority for those files.*

A consumer may rely on everything listed here. Adding a column or field is always allowed. Renaming, removing, or changing a unit, an id, a status value, a warning code or a path needs a request to `all` first (`coord/README.md`).

## From the data role (exists)

Authority: `pipeline/README.md`.

| File | What it is | Read by |
|---|---|---|
| `data/psi/manifest.json` | The 24 investigations: accession, acronym, title, DOI, license, experimental-table files | ui, pm |
| `data/psi/catalog/PSI-<n>.json` | Full PSI record of one investigation: `objective`, `approach`, `hypothesis`, `researchImpacts`, `publications`, `projectType` and more | ui (catalog build), pm (summaries) |
| `data/psi/experimental_tables/*.csv` | The 22 NASA tables, unchanged | ui (catalog build) |
| `pipeline/spec/needs.json` | The fire-safety information needs (`P1`–`P3` prevention, `S1` suppression, `D1`–`D2` detection; `P4` is being removed, see `coord/decisions.md`): question, required conditions, outcomes, scope, the objective sentence that backs each (`stated_by`) | ui (needs view), pm |
| `pipeline/spec/variables.json` | Standard variables, units, valid ranges, derived formulas | ui, pm |
| `data/pipeline/tests.csv` | One row per test (1,867). Keys `test_id`, `investigation_id`, `source_id`; conditions such as `fuel_material`, `fuel_phase`, `o2_pct`, `o2_basis`, `pressure_kpa`, `flow_cms`, `gravity_level`; outcomes; `flags`, `source_file`, `source_row` | ui (raw-data step, Coverage view), pm |
| `data/pipeline/values_long.csv` | One row per value with `source_file`, `source_row`, `source_column` | ui (show where a value comes from) |
| `data/pipeline/capability_matrix.csv` | Need × source: `status` (`measured`, `partial`, `conditions_only`, `none`, `out_of_scope`, `not_test_level`), test counts, what is missing | ui (needs view), pm |
| `data/pipeline/need_tests.csv` | For each need, the tests usable as evidence | ui, pm |
| `data/pipeline/run_report.json` | Row counts, flags, unmapped source columns | pm (limits) |

Rules that come with these files:

- A value is copied from a NASA cell or computed by a formula in `variables.json`. Nothing is estimated. An empty cell means the table does not record it.
- The pipeline links tests to needs. It draws no conclusion from the values.

## From the ui role (exists)

Authority: `data/catalog/README.md` and `scoring/README.md`.

| Thing | What it is | Read by |
|---|---|---|
| `data/catalog/investigations.csv` | The 24 investigations, one row each, with the team's classification columns and `verification_status` | pm (summaries), dashboard |
| `data/catalog/configurations.csv` | 41 test configurations; the unit the ranking scores | dashboard |
| `data/catalog/data_dictionary.csv` | Every column: meaning, allowed values, where it is used | pm, data |
| `scoring.scorer.rank(query)` | Takes a rough string or a structured input. Returns `status` (`ok`, `out_of_scope`, `need_input`), `assumptions`, `warnings`, `results` (ranks 1 to 3 with `investigation_id`, `config_id`, `score`, `similarity`, `why`, `main_gap`, `warnings`, `psi_url`, `dataset_doi`) and `ranking` (all investigations) | dashboard, pm (explanations) |
| `scoring/scoring_config.json` | Weight profiles, presets (such as `iss`, `lunar_habitat`), keywords, warning texts | dashboard, pm |
| `validation/scenarios.json`, `validation/report.md` | 22 scenarios with expected results; the report of the last run | pm (write-up) |
| Public URL of the dashboard | `coord/status/ui.md` | pm (submission, slides) |

Rules that come with these:

- Catalog numbers come from a PSI table or record; empty stays empty. Classification columns are the team's.
- Scores are computed by code. A language model explains a result and never changes it.
- For an atmosphere the record does not report, the scorer uses a fallback and attaches a `fallback` warning. Whoever shows the result shows the warning.

## From the pm role (agreed with ui on 11/14 11:12; shape-only examples in `contracts/examples/`)

*Rewritten 11/14 after the data role's audit, to describe the files as `python3 ai/build_all.py` writes them now (written by an AI session of the pm role; additions to the earlier list, no field renamed or removed). Updated 11/14 after the 14:59 merge (literature check of the need links, the lunar wording of the 14:15 decision, the ui page reading `evidence_map.json`): two `evidence_map.json` label fields became the strings `web/app.js` prints (below), and `model_readiness.json` and `robustness.json` are built by `ai/build_all.py`. The files are the authority; `contracts/examples/*.json` show the shape only, with placeholder values that must never be displayed or cited.*

Where a file is missing the dashboard shows "Not available yet". Arbitrary queries get no model-written text; the page shows the scorer's own `why` and `main_gap` lines.

Every file in `data/insights/` is built by a script in `ai/` (code written with an AI assistant). `python3 ai/build_all.py` rebuilds all of them in order with no language-model call and ends with `ai/check_all.py`. Each file's disclosure block is in `data/insights/_meta.json` under the file name, and also inside the file under `_meta` when the file is a JSON object (`cards.json` and `scenarios.json` are arrays, so their block is only in `_meta.json`).

| File | `built_by` (in `_meta.json`) | Language model at build | Read by the page today |
|---|---|---|---|
| `scenarios.json` | `ai/build_baseline.py` | none | yes |
| `cards.json` | `ai/apply_cards.py`, or `ai/apply_review.py` once review verdicts are applied (`ai/build_baseline.py` writes the quoted cards first; the later steps replace them) | `gpt-oss:20b (f38aa0c53da5)` when a model sentence is shipped, else `none` | yes |
| `evidence.json` | `ai/evidence.py` | none | no |
| `evidence_map.json` | `ai/evidence_map.py` | none | yes ("Where the evidence stops"; `web/build.py` `OPTIONAL`) |
| `model_readiness.json` | `ai/model_readiness.py` | none (scikit-learn cross-validation, no fitted output shipped) | no |
| `robustness.json` | `ai/robustness.py` | none (NumPy weight sampling over `scoring.scorer.rank`) | no |
| `catalog_trace.json` | `ai/audit_catalog.py` | none | no |
| `quality.json` | `ai/apply_review.py` | none | no |

### Sources: three forms

A `source` (in every file below) is a string, or an array of strings, so the page can turn each into a link (`sourceLinks()` in `web/app.js`). `ai/resolve.py` resolves every one to the text or row it names, and a build stops on a source that does not resolve.

1. **A PSI record**: `PSI-25.objective` is a field of `data/psi/catalog/PSI-25.json` (`title`, `objective`, `approach`, `hypothesis`, `researchImpacts`); `PSI-25` alone is the whole record (the page links it to the PSI page).
2. **A DOI**: `doi:10.xxxx/yyyy`, a dataset DOI of `data/psi/manifest.json`, a publication DOI listed in a PSI record, or a DOI in a `references.json` url.
3. **A file and an id**: `<repo path>#<id>`. CSV: the rows whose first column is the id, or whose first two columns are `a/b` (`data/pipeline/scenario_needs.csv#lunar_habitat/S1`). JSON: the object whose `id` is the id at any depth (`pipeline/spec/references.json#SAF456.conditions`), a top-level key, a key of `_meta`, a dotted key path (`scoring/scoring_config.json#presets.mars_habitat`), or `a/b`: the one object with id `b` inside the object whose `id`, `need_id`, `scenario_id` or `investigation_id` is `a`. The last form cites the data role's fixed sentences: `data/pipeline/evidence/scenario_lunar_habitat.json#S1/status.in_atmosphere`. A fixed sentence whose id is not unique in its need block (`documented.elsewhere`), the scenario caveat and the matched ranges are cited by key path: `...scenario_iss.json#needs.0.statements.14`, `...scenario_lunar_habitat.json#environment.caveat`, `...scenario_lunar_habitat.json#needs.3.matched_ranges`. A cited sentence (a string, or an object with `text`) is in the text as written; a cited structured value (matched ranges) backs the numbers in `facts`, which may be rounded from it by code (`ai/check_all.py`).

A NASA experimental table is cited through its `pipeline/spec/sources.json` entry, never by its file name (the names contain spaces).

### Three kinds of text and how the page labels them

| Kind | How a consumer recognises it | Tag the page shows (`web/app.js`) |
|---|---|---|
| Quoted from NASA | card `status` = `fallback_quote` or `ai_generated` = `false`; sentence `origin` = `quote`; every key point | "Quoted from the PSI record" |
| Computed by team code from fixed templates and the data role's fixed sentences | `text_origin` = `template` on every scenario entry and on every need statement, gap and result note; the frame carries `frame_text_origin` = `template` (the page reads `frame_text_origin`, then the entry's `text_origin`); scenario entries have `ai_generated` = `false` | "Computed by team code from NASA PSI tables" |
| Written by the language model gpt-oss:20b and checked by code gates | card `status` = `generated` or `generated_partial` and `ai_generated` = `true` (true exactly when at least one model sentence is shown); sentence `origin` = `model` | the page's AI tag with `model` and `reviewed_by` |

That the code itself was written with an AI assistant is said in each file's `_meta` block and in the `label` strings, not by `ai_generated`.

Field labels: a quoted sentence is always shown after the label of the record field it comes from: `Record title:`, `Stated objective:`, `Planned approach:`, `Stated hypothesis:`, `Impact statement in the record:`.

### Need list

Read from `pipeline/spec/needs.json`: six needs, `P1` Flammability limit, `P2` Ignition, `P3` Flame spread and growth, `S1` Extinction conditions, `D1` Combustion products, `D2` Smoke generation conditions (P4 was removed by the decision of 11/14 12:15). A test counts for a need only if its investigation states that need as an objective (`objective_link` = `stated` in `need_tests.csv`). Since the data role's literature check (commit `a5a9e87`) the link rests on a purpose sentence of the PSI record or of a publication (`objective_links.csv`: `record_field`, `quote`, `publication_item`, `verdict`), and only links with verdict `supported` count; `D1`/`PSI-25` has a publication item and no record field, so it is cited as `pipeline/spec/references.json#BASS2TM.products`. Other tests that record the variables are reported as "recorded outside the stated objective" and are not counted. Each need has a `reading`: what a counted test records and what the count does not mean; every need statement ends with it, as written. (The `D1` reading in `needs.json` still says that no test is counted while 122 are; `ai/build_baseline.py` prints a warning and `ai/check_all.py` an info line until the data role changes it.)

### `data/insights/cards.json`

Array of 24, one entry per investigation, shown next to the result. The page reads `summary`, `summary_sources`, `key_points[].text`, `key_points[].source`, `status`, `ai_generated`, `reviewed_by` and `model`.

| Field | Type | Meaning |
|---|---|---|
| `investigation_id` | string | PSI accession, `PSI-25`. The page joins it to `rank()` results through their `psi_accession` |
| `status` | string | `generated`: every model sentence the model proposed is shown. `generated_partial`: at least one was dropped (by a code gate, by a reviewed removal of `ai/review/pm_prereview.json`, or by the review). `fallback_quote`: no model sentence is shown; the card is the quoted baseline |
| `summary` | string | at most 3 sentences. A `fallback_quote` card begins `Quoted from the PSI record.` and quotes with field labels. A model card has model sentences, each ending with its source in brackets, `(PSI-25 record: objective)`; a sentence removed before the review is replaced in place by the NASA sentence it cited, as `<field label> "<verbatim text>"` |
| `summary_sources` | array of sources | the record fields the summary comes from; the page links them after the summary |
| `key_points` | array of `{ "text", "source" }` | at most 4, each a verbatim quote with its field label (`Planned approach: "..."`) and its record field as source |
| `ai_generated` | boolean | `true` exactly when at least one model sentence is shown |
| `model` | string | `none: verbatim NASA text chosen by team code`, or `gpt-oss:20b (f38aa0c53da5) via Ollama 0.40.16` |
| `reviewed_by` | string or null | `null` until every model sentence of the card has a review verdict in `ai/review/review_sheet.csv`; then `second AI session (data role)`, `hackathon team member (...)` or both. A reviewed removal never sets it |
| `updated` | string | ISO time of the last change of the entry |
| `built_by` | string | `ai/build_baseline.py`, `ai/apply_cards.py` or `ai/apply_review.py` (the step that wrote the entry) |
| `label` | string | the disclosure sentence for this card |
| `record_title`, `dataset_doi`, `license_note` | string | from `data/psi/manifest.json` and the record |
| `prompt_sha256`, `params` | string or null, object | prompt file hash and model settings, log files and sentence counts (`sentences_proposed`, `sentences_shipped`, `sentences_removed_by_prereview`); `null` and `{}` for a `fallback_quote` card |
| `pick_rule` | object | the fixed rules that chose the quoted sentences |
| `shared_text_note` | string, optional | when the cited PSI text is word for word the same in other records |
| `removed_before_review` | array, optional | `[{ n, sentence, reason, reviewer_kind: "ai_session_pm", replaced_by }]`, the reviewed removals applied to this card. `replaced_by` is the record field of the quote shown in the slot, or `null` when no slot is shown (every unit the sentence cited is marked `not_relevant` in the review sheet; PSI-159 since 14 Nov) |
| `hidden_by_review` | array, optional | `[{ item, role, source, unit_ids[], verdict: "not_relevant", reviewer_kind, reviewer_role, replaced_by, slot_of_removed_sentence? }]`: verbatim quotes this card does not show because a reviewer marked their row of `ai/review/review_sheet.csv` `not_relevant` (added 14 Nov; the page need not read it). A model sentence whose first cited unit is listed here keeps its bracketed source but has no key point for that unit |
| `sentences` | array | one per shown sentence, below |

`sentences[]`: `role` (`summary`, `key_point`), `origin` (`quote`, `model`), `text`, `field_label` (`null` for a model sentence), `evidence`, `checks{}`, `lexical_support`, `shared_with[]`, `review` (`null` until reviewed). A quote also has `source`, `char_start`, `char_end` (offsets in the record field); a quote that fills the slot of a removed model sentence has `n` and `replaces { n, removed_by, reviewer_kind }`. A model sentence also has `n`, `cited_fields[]`, `repaired`, `first_pass_reasons[]`.

`evidence[]`: `{ id, source, quote, char_start, char_end }`. `id` is a unit of `evidence.json`; `quote` is the exact text of that unit, taken by code (`record[field][char_start:char_end]`), never the model's copy. A model sentence's evidence also has `field`, `quote_from` and `model_quote`: the model's own copy of the quote, which code gate 2 checks and `ai/check_all.py` re-runs. `model_quote` is not for display.

### `data/insights/scenarios.json`

Array, one entry per preset scenario: `iss`, `lunar_habitat`, `spacesuit`, `mars_habitat`. Built by `ai/build_baseline.py` from the data role's scenario matching (`scenario_needs.csv`, `scenario_tests.csv`, `need_tests.csv`, `tests.csv`) and evidence packages (`data/pipeline/evidence/scenario_<id>.json`); no language model. The dashboard shows `iss` and `lunar_habitat`. The page reads `id`, `query`, `frame`, `frame_sources`, `frame_text_origin`, `text_origin`, `needs[]` (`need_id`, `statement`, `sources`, `text_origin`), `gaps[]` (`text`, `sources`, `needed_data`, `text_origin`), `result_notes[]` (`investigation_id`, `text`, `sources`, `text_origin`), `reviewed_by` and `model`.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | preset id from `scoring/scoring_config.json` |
| `query` | string | exactly the string the page passes to `rank()`: `"ISS"`, `"lunar habitat"`, `"spacesuit"`, `"Mars base"` |
| `ranking_source` | string | always `scoring.scorer.rank`; the page computes the ranking live and scores are not copied here |
| `frame` | string | what the counts mean for this scenario: the team bins (and the flow range where the scenario sets one), the evidence rule, the burner-stream rule and, for lunar and Martian gravity, the gravity sentence with NASA's quoted gap (`TB008.gaps`) and one cited sentence from Olson and Ferkul's Table I (`OF2012.table1`, with its 5.18 s drop-tower caveat); ends with `label`. For `lunar_habitat` (decision 11/14 14:15) it also gives the challenge statement in the wording of `CH.moonbase` (hedges kept, not in quotation marks), the data role's `environment.caveat` as written, and the sentence "No counted test was recorded at 30% oxygen or more and at or below 10.2 psi; the 17 counted tests inside the bins are fuel-droplet tests recorded 1 to 2 kPa above it, at 30 to 34% oxygen and about 0.7 atm (71 to 72 kPa)" (numbers computed, not typed in). The same oxygen and pressure follow the count in the S1 statement, the droplet gap and the PSI-69 result note |
| `frame_sources`, `frame_facts` | array of sources, object | sources of the frame; the values it prints |
| `frame_text_origin`, `text_origin` | string | `template` |
| `ai_generated` | boolean | `false` (every sentence is built by team code) |
| `needs` | array | one per need id in `needs.json`: `{ need_id, need, statement, sources, status, facts{}, text_origin, rule[] }`. `statement` begins `Recorded tests (team count; team bins: ...)`, then the data role's fixed status sentence, the team's clauses (investigations, missing columns, fuel phase, balance gas checked against the pipeline's `added_gas` mark, test ends for S1), the data role's fixed flow and gap sentences (oxygen, pressure, flow, gravity), the data role's `documented.elsewhere` sentences for a table whose missing variable the statement names (what a record or paper says, never a value), the tests outside the stated objective, and `What a count of this need means (the pipeline's reading): <reading>`. Every fixed sentence is used as written and cited as `data/pipeline/evidence/scenario_<id>.json#<need>/<statement id>`. `status` is the pipeline value (`in_atmosphere`, `oxygen_only`, `pressure_only`, `other_atmosphere`, `not_measured`, `atmosphere_not_specified`); `in_atmosphere` means tests were run there, never that the need is covered |
| `gaps` | array | `{ text, needed_data, sources, facts{}, text_origin, status, rule, copied_from? }`; `status` is `from_rule` (gravity, solid fuels at the atmosphere, droplets only for S1, detection: the counted tests of D1 and D2 as they are, with the tables' missing columns) or `copied` (a `not_covered` line of `needs.json`, with `copied_from`). The solid-fuel gap names the Saffire IV to VI samples of `SAF456.conditions` that fall in the team bins, with their Table 1 numbers; they are never counted |
| `result_notes` | array | `{ investigation_id, config_id, text, sources, facts{}, text_origin, status, rule[] }`; `status` is `top3` or `near_tie` (within 3 points of the third result). A note whose investigation is not in the live top 3 is shown under "Other investigations" |
| `fresh` | object | `ranker_config_version`, `scoring_config_sha256`, `catalog_sha256`, `scenario_inputs_sha256`, `hash_rule`; `ai/check_all.py` fails when they no longer match the files (the scenario inputs include the evidence packages) |
| `model`, `built_by`, `reviewed_by`, `label`, `updated` | string | `model` is `none: counts and fixed sentences filled by team code`; `reviewed_by` is `null` |

Gap codes the build knows (from `pipeline/spec/statements.json`): `oxygen:not_recorded`, `oxygen:no_usable_test_in_range`, `pressure:not_recorded`, `pressure:no_usable_test_in_range`, `flow:not_recorded`, `flow:no_usable_test_in_range`, `gravity:no_usable_test_at_lunar`, `gravity:no_usable_test_at_martian`, `need:no_usable_test`. An unknown status or gap code stops the build. Every number printed in a `statement`, `text` or `frame` is a value in that item's `facts` (or `frame_facts`); `ai/check_all.py` recounts them from the pipeline CSVs by a second code path, or finds them in a cited source.

### `data/insights/evidence.json`

Object, built by `ai/evidence.py` (no language model). The PSI record prose of the 24 investigations, split into numbered sentences ("units") that cards cite by id.

`{ _meta, records: { "PSI-<n>": { title, acronym, license, dataset_doi, pub_count, dois[], related[], units[] } } }`. A unit is `{ id, field, prefix, source, text, char_start, char_end, words, quotable, reference_like, hedged, hedge_words[], list_marker, under_heading, shared_with[] }`. Ids are `TTL-1`, `OBJ-k`, `APP-k`, `HYP-k`, `IMP-k`; `prefix` is the field label; `text` equals `record[field][char_start:char_end]`.

### `data/insights/evidence_map.json`

Object, built by `ai/evidence_map.py` (no language model): the data for "Where the evidence stops" (oxygen axis, three fuel lanes). `{ _meta, labels{}, axes{}, points[], pressure_column{}, not_plotted{}, targets[], flight_tests_not_in_psi, sums{} }`.

- A point is `{ fuel_phase, investigation_id, source_id, o2_pct, pressure_kpa, balance_gas, n_tests, test_ids[] }` plus optional fields. `pressure_kpa` `null` means no value (never 0, never 101 kPa); `balance_gas` is `n2_only`, `co2_added`, `he_added` or `not_recorded`. Only ambient oxygen is plotted; oxidizer-stream tests are in `not_plotted`.
- A target is `{ id, kind, label, as_written, source, access, draw, ... }` with `kind` one of `nasa_design_atmosphere`, `nasa_test_environment`, `challenge_statement`, `team_preset`, `team_counting_range`.
- `flight_tests_not_in_psi`: the five Saffire IV to VI samples of `SAF456.conditions` (ICES-2024-365, Table 1) as cited marks `{ o2_pct, pressure_kpa, flight_sample, flight, material, label, marker: "cross", counted: false, what, source, access }`, or `null` when the item is absent. They are never counted; `labels.saffire_note` describes them.
- `sums.lanes`: per lane (`gas`, `liquid`, `solid`) `{ label, plotted, max_o2_pct, at_or_above_30_pct_o2, not_plotted, not_plotted_oxidizer_stream, not_plotted_no_ambient_oxygen_value }`.
- `labels`: `title`, `caption[]` with `caption_sources[]` (one list per caption line), `lane_notes{lane: string}`, `lane_details{lane: {name, text, short, end_label?, pressure_note?}}`, `saffire_note` (string or `null`), `saffire_note_source`, `saffire_status`, `hollow_marker_meaning`. `web/app.js` prints `lane_notes[lane]` after the lane's count (it capitalises the first letter and adds the full stop, so the string has neither the lane name nor a final full stop) and `saffire_note` inside its legend (no final full stop); both were objects before the 14:59 merge and are strings now.
- The page reads `points`, `targets` (`o2_pct` or `o2_min`, `label`, `kind`, `source`, `access`), `flight_tests_not_in_psi`, `labels` and `not_plotted` (`oxidizer_stream.n/why`, `no_ambient_oxygen_value.n/rule`, `psi20_test_day_table.days/flames_ignited`). It does not read a target's `draw`, so the spacesuit preset and range (`draw` `text`, 95 to 100% oxygen) stretch its axis to 100%; that is ui's choice to make.

### `data/insights/model_readiness.json`

Object, built by `ai/model_readiness.py` (no language model; design component J): can these NASA tables support an outcome model? `{ _meta, title, fixed_line, labels_and_limits, counts_note, flag_rule, basis_rule, verdict_rule, thresholds, tests_csv_rows, rows[], outcome_columns_not_assessed, tables_without_outcome_column, not_covered[], not_covered_facts, shipped }`. A row is one candidate label of one table: counts, classes, grouping rule and group count, recorded ranges, and, where the fixed rule allows it, grouped cross-validation against the base rate (two fold means with their spread) and a verdict in words. No coefficient, curve, grid or fitted value is written. `ai/check_all.py` rebuilds it and fails when the file differs.

### `data/insights/robustness.json`

Object, built by `ai/robustness.py` (no language model; design component K): how firm each top rank of the team's ranking is under the team's own weights, for the four page queries. `{ _meta, description, label, method, runs[] }`; a run has `scenario_id`, `query`, `config_version`, `seed`, `draws` (8,000 per run since the 14:59 merge; 2,000 in the design), `live_top3`, `results[]` (`first_or_tied_share_local`, `top3_share_local`, `first_or_tied_share_uniform`, `tied_for_first_with[]`, `assumed_dims[]`, `display_line`), `structural_ties`, `parity` and `seed_check`. Not a probability that a study is relevant; a rank that rests on an assumed atmosphere gets no stability figure.

### `data/insights/catalog_trace.json`

Object, built by `ai/audit_catalog.py` (no language model): for every number in the catalog text the page shows (`investigations.csv` `objectives` and `key_findings`, `configurations.csv` `key_findings` and `config_label`), whether it was found in a NASA source. `{ _meta, description, fields_audited[], rules{}, counts{}, numbers[], not_audited[], lint_hits[] }`. A number is `{ table, row_id, csv_line, investigation_id, field, number, unit, unit_from_range, follower, context, status, matched_source, rule }`; `status` is `found_in_psi_text`, `found_in_table_cell`, `found_as_count` or `not_found`, and says only that the number was found, not that its meaning was checked.

### `data/insights/quality.json`

Object, built by `ai/apply_review.py` (no language model): measured counts of the model sentences and their checks. Sentences proposed, passed and rejected by each gate, repaired, `removed_before_review` (`{ n, reviewer_kind: "ai_session_pm", file, sentences[], ... }`, the reviewed removals, counted apart from the review), `removed_by_review`, shipped, cards by status, rows reviewed by a person and by an AI session (separately), verdicts, `support_rate` with its `n`, and `recount_ok`. Added 14 Nov: `quotes_not_shown_by_review` (`{ n, rows[], kept_although_marked[], marked_rows_matching_no_quote[], rule }`, quotes left out because a reviewer marked them `not_relevant`, counted apart from the model-sentence counts), `quote_rows_shown` and `rows_without_verdict` (`{ n, by_origin, items[], rule }`, the sheet rows that go back to the reviewer).

### `data/insights/_meta.json`

Object keyed by file name (plus its own `_meta`): `{ built_by, code_written_with, language_model_used_at_build, generated_at, inputs_sha256{}, label, content_sha256, ... }` for every file in `data/insights/`. `language_model_used_at_build` is `none` or `gpt-oss:20b (f38aa0c53da5)`.

### Planned, not built yet

`ai_method.json` (the "How we checked the AI text" panel), `data_health.json`. Their shapes are in `docs/ai_layer_design.json` (`file_contracts`); the page must not rely on them until they are listed here.

Pressure is in kPa everywhere (14.7 psi = 101.3 kPa, 10.2 psi = 70.3 kPa).
