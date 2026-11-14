# Experiment catalog

> AI-generated data: extracted by Claude (an AI assistant) on 2026-11-14 from the PSI records and experimental tables in `data/psi/`. Every row has `verification_status = ai_extracted`. Only a row that a person has compared with the original becomes `human_verified`, and that changes no score.

- `investigations.csv`: 24 PSI combustion-science investigations (one row per investigation, 26 columns).
- `configurations.csv`: 41 test configurations (one row per group of tests that share a range of conditions, 43 columns). The ranking scores this table.
- `catalog.xlsx`: a copy for people to review. Row 1 is the column group band, row 2 the column name (shaded), row 3 its meaning; data start at row 4.
- `data_dictionary.csv`: for each column, its meaning, allowed values and where it is used.

How the catalog is built from the PSI tables (grouping, ranges, unit conversion, repeated rows, cells that are not readings) is described step by step in `scoring/METHOD.md`, section 3.

## Rules

- **Where numbers come from:**
  - A number is taken only from a PSI experimental table (`table`) or the PSI record text (`record`), and `atmosphere_basis` says which.
  - `o2_source`, `pressure_source` and `flow_source` give the source of each range: `table`, `record`, `test_matrix` (a planned matrix, not individual tests) or `team` (the team's reading).
  - A value not in the record stays empty and is never filled with 0.
- **Team classification:** `tier`, `fire_safety_role`, `research_focus`, `fire_scenario_tags`, `fuel_class`, `thermal_regime` and `sooting_tendency` are the team's classification, not NASA's.
- **Columns added to the original design:**
  - investigations: `psi_accession`, `license`;
  - configurations: `psi_accession`, `o2_reference` (`ambient` or `oxidizer_stream`), `atmosphere_basis`, and the three source columns.
- **Disagreements:** where the catalog differs from an original, or two records disagree, `source_notes` says so (for example the Saffire-I record's dates, or the thickness units in the Saffire tables).
- **Independent check:** `python3 validation/check_catalog_sources.py` compares the catalog with the NASA records and tables directly and writes `validation/catalog_source_check.md`.

## Human verification

`validation/verification_sheet.csv` lists the catalog values behind the demo rankings (`ISS`, `lunar habitat`, `ISS cotton fabric`, `lunar habitat cotton fabric`): fuel, oxygen, pressure and flow ranges, and test counts. Each value comes with the NASA table rows and raw cells, or the PSI record text, where a person can check it.
- Rebuild it with `python3 validation/build_verification_sheet.py` after any catalog or scorer change.
- A person fills in `checked_by`, `matches_source` and `comment`.
- A row becomes `human_verified` only through `scripts/build_catalog.py`.
- Row numbers are CSV row numbers (header = row 1), the same numbers that `source_notes` and `data/pipeline/*.csv` use.

## Rebuilding

```bash
python3 scripts/build_catalog.py        # the two CSV files
python3 scripts/export_catalog_xlsx.py  # catalog.xlsx and data_dictionary.csv
```

Source: NASA Physical Sciences Informatics (https://psi.nasa.gov/). Each experiment's DOI is in the `dataset_doi` column and its license in the `license` column (the PSI-10 record states no license).
