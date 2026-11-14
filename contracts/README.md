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

## From the pm role (agreed with ui on 11/14 11:12; examples in `contracts/examples/`)

Where a file is missing the dashboard shows "Not available yet". Arbitrary queries get no model-written text; the page shows the scorer's own `why` and `main_gap` lines.

A `source` (in every file below) is one of three forms, or an array of them, so the page can turn each into a link:

- `PSI-25.objective`: a field of the PSI record JSON in `data/psi/catalog/`
- `doi:10.xxxx/yyyy`: a publication
- `data/pipeline/tests.csv#FLEX-12`: a file and a test id

### `data/insights/cards.json`

One entry per investigation: a short model-written summary shown next to the catalog row.

| Field | Type | Meaning |
|---|---|---|
| `investigation_id` | string | PSI accession, `PSI-25`. The page joins it to `rank()` results through their `psi_accession` |
| `summary` | string | at most 3 English sentences written from the PSI record only |
| `key_points` | array of `{ "text", "source" }` | at most 4, each with its source |
| `ai_generated` | boolean | `true` |
| `model` | string | the model that wrote the text |
| `reviewed_by` | string or null | who checked it against the PSI text; `null` until checked. The page shows "Reviewed by <name>" or "Not reviewed yet" |
| `updated` | string | ISO time |

### `data/insights/scenarios.json`

One entry per preset scenario. Order of writing: `iss` and `lunar_habitat` (the demo), then `spacesuit` and `mars_habitat`.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | preset id from `scoring/scoring_config.json` |
| `query` | string | exactly the string the page passes to `rank()`: `"ISS"`, `"lunar habitat"`, `"spacesuit"`, `"Mars base"` |
| `ranking_source` | string | always `scoring.scorer.rank`; the page computes the ranking live and scores are not copied here |
| `result_notes` | array of `{ "investigation_id", "text", "sources" }` | plain-language explanation of why a result ranks where it does. A note whose investigation is not in the live top 3 is shown under "Other investigations" |
| `needs` | array of `{ "need_id", "statement", "sources" }` | one per need id in `needs.json` (`P1`–`P3`, `S1`, `D1`, `D2`): what the recorded tests can and cannot say for this scenario, counted from `scenario_needs.csv` (tests with a stated objective only) |
| `gaps` | array of `{ "text", "needed_data" }` | what PSI does not contain for this scenario |
| `ai_generated`, `model`, `reviewed_by`, `updated` | as above | |

Pressure is in kPa everywhere (14.7 psi = 101.3 kPa, 10.2 psi = 70.3 kPa).
