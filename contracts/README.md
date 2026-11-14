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
| `pipeline/spec/needs.json` | The 7 fire-safety information needs (`P1`–`P4` prevention, `S1` suppression, `D1`–`D2` detection): question, required conditions, outcomes, scope | ui (needs view), pm |
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

## From the pm role (draft; examples in `contracts/examples/`)

The shape below is a proposal. The ui role decides what the dashboard actually shows; pm adapts the files to that through a request.

### `data/insights/cards.json`

One entry per investigation: a short model-written summary to sit next to the catalog row.

| Field | Type | Meaning |
|---|---|---|
| `investigation_id` | string | PSI accession, `PSI-25` |
| `summary` | string | two or three English sentences written from the PSI record only |
| `key_points` | array of `{ "text", "source" }` | each statement with the PSI field (`PSI-25.objective`) or publication DOI it comes from |
| `ai_generated` | boolean | `true` |
| `model` | string | the model that wrote the text |
| `reviewed_by` | string or null | who checked it against the PSI text; `null` until checked |

### `data/insights/scenarios.json`

One entry per preset scenario: model-written explanation around results that the scorer and the pipeline produce.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | a preset id from `scoring/scoring_config.json` |
| `query` | string | the query passed to `scoring.scorer.rank` |
| `ranking_source` | string | always `scoring.scorer.rank`; scores are not copied into this file |
| `result_notes` | array of `{ "investigation_id", "text", "sources" }` | plain-language explanation of why a result ranks where it does |
| `needs` | array of `{ "need_id", "statement", "sources" }` | what the recorded tests can and cannot say about each need for this scenario, from `capability_matrix.csv` |
| `gaps` | array of `{ "text", "needed_data" }` | what PSI does not contain for this scenario |
| `ai_generated`, `model`, `reviewed_by` | as above | |

Pressure is in kPa everywhere (14.7 psi = 101.3 kPa, 10.2 psi = 70.3 kPa).
