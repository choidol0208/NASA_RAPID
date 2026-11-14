# Contracts: who produces which file, who reads it

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. Written by pm. The parts about `data/pipeline/` describe what the data role built; `pipeline/README.md` is the authority for those files.*

A consumer may rely on everything listed here. Adding a column or field is always allowed. Renaming, removing, or changing a unit, an id or a path needs a request to `all` first (`coord/README.md`).

## From the data role (exists on `main` now)

| File | What it is | Read by |
|---|---|---|
| `data/psi/manifest.json` | The 24 investigations: accession, acronym, title, DOI, license, experimental-table files | ui (Catalog), pm |
| `data/psi/catalog/PSI-<n>.json` | Full PSI record of one investigation: `objective`, `approach`, `hypothesis`, `researchImpacts`, `publications`, `projectType`, `subResearchArea`, `experimentHardware`, `totalFileSize` and more | ui (Investigation), pm (cards) |
| `data/psi/experimental_tables/*.csv` | The 22 NASA tables, unchanged | nobody directly; go through the pipeline outputs |
| `pipeline/spec/needs.json` | The 7 fire-safety information needs (`P1`–`P4` prevention, `S1` suppression, `D1`–`D2` detection): question, required conditions, outcomes, scope | ui (labels and questions), pm (scenarios) |
| `pipeline/spec/variables.json` | Standard variables, units, valid ranges, derived formulas | ui (units and labels), pm |
| `data/pipeline/tests.csv` | One row per test. Keys: `test_id`, `investigation_id`, `source_id`. Conditions such as `fuel_material`, `fuel_phase`, `o2_pct`, `pressure_kpa`, `flow_cms`, `gravity_level`. Outcomes. `flags`, `source_file`, `source_row` | ui (Coverage), pm (ranking) |
| `data/pipeline/values_long.csv` | One row per value with `source_file`, `source_row`, `source_column` | ui (show the source of a value) |
| `data/pipeline/capability_matrix.csv` | Need × source: `status` (`measured`, `partial`, `conditions_only`, `none`, `out_of_scope`, `not_test_level`), test counts, what is missing | ui (Scenario, Coverage), pm (ranking) |
| `data/pipeline/need_tests.csv` | For each need, the tests usable as evidence: `need_id`, `test_id`, `investigation_id` | ui, pm |
| `data/pipeline/run_report.json` | Row counts, flags, unmapped source columns | pm (limits section of the write-up) |

Rules that come with these files, set by the pipeline and binding for every consumer:

- A value is copied from a NASA cell or computed by a formula in `variables.json`. Nothing is estimated. An empty cell means the table does not record it; do not fill it in downstream (for example, do not assume cabin pressure where `pressure_kpa` is empty; show it as "not recorded").
- The pipeline links tests to needs. It draws no conclusion from the values. Text that interprets belongs to the AI outputs below and must be labelled.

## From the pm role (being built; examples in `contracts/examples/`)

### `data/insights/cards.json`

One card per investigation, for the Catalog and Investigation screens. An array of:

| Field | Type | Meaning |
|---|---|---|
| `investigation_id` | string | `PSI-25` |
| `acronym`, `title` | string | from the PSI record |
| `pillars` | array of `prevention` / `detection` / `suppression` | from the needs this investigation has usable tests for, plus the PSI text |
| `fuel_phase` | array of strings | from `tests.csv`; empty when the table is not test-level |
| `summary` | string | two or three English sentences, written by a language model from the PSI record only |
| `variables_changed`, `measurements` | arrays of strings | what the investigation varied and what it recorded |
| `conditions` | object | `o2_pct`, `pressure_kpa`, `flow_cms`: each `[min, max]` computed from `tests.csv`, or `null` when not recorded |
| `tests` | integer | rows in `tests.csv` for this investigation |
| `key_points` | array of `{ "text", "source" }` | each statement with the PSI field or publication DOI it comes from |
| `related` | array of strings | related investigation ids from PSI |
| `ai_generated` | boolean | `true` for any card with model-written text |
| `model` | string | the model that wrote the text |
| `reviewed_by` | string or null | who checked it against the PSI text; `null` until checked |

### `data/insights/scenarios.json`

One entry per scenario, for the Scenario screen. An array of:

| Field | Type | Meaning |
|---|---|---|
| `id` | string | `iss-class`, `lunar-habitat`, `pressurized-rover` |
| `name`, `description` | string | shown on the scenario picker |
| `environment` | object | `o2_pct: [min, max]`, `pressure_kpa: [min, max]`, `gravity_g`, and `source` saying where the numbers come from |
| `ranking` | array | `{ "investigation_id", "score", "breakdown": { ... }, "why" }`, sorted by `score`. `score` and `breakdown` are computed by rules; `why` may be model-written |
| `needs` | array | one per need: `{ "need_id", "evidence_level", "tests_in_range", "tests_total", "statement", "sources": [ { "investigation_id", "doi" } ] }` |
| `gaps` | array | `{ "text", "needed_data" }`: what PSI does not contain for this scenario |
| `method` | string | one paragraph on how the ranking and levels are computed, to show on the page |
| `ai_generated`, `model`, `reviewed_by` | as above | |

`evidence_level` is one of:

| Value | Meaning |
|---|---|
| `direct` | tests of the right fuel phase exist inside the scenario's oxygen and pressure range |
| `adjacent` | tests exist for the need, but outside the range or for another fuel phase |
| `indirect` | only ground or modelling investigations, or tables that are not test-level |
| `gap` | nothing in the PSI experimental tables |

Pressure is in kPa everywhere (14.7 psi = 101.3 kPa, 10.2 psi = 70.3 kPa, 8.2 psi = 56.5 kPa).

## From the ui role

| Thing | Where | Read by |
|---|---|---|
| Public URL of the dashboard | `coord/status/ui.md` | pm (submission, slides) |
| Screenshots and GIF for the project page | `web/media/` | pm |

The site reads the files above from the repository at build time or as static assets. It needs no server and no API key.
