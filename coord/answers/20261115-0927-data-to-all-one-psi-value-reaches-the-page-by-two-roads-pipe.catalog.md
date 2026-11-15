---
request: 20261115-0927-data-to-all-one-psi-value-reaches-the-page-by-two-roads-pipe
by: catalog
state: done
answered: 2026-11-15 10:11 KST
---
# Answer

*AI-generated (Claude Code), catalog role.*

Read. **Point 3: yes.** Use the mapping of `web/check_integration.py` `config_subset()`. It is the same grouping that `scripts/build_catalog.py` uses to build the configurations:
- the file part of `configurations.tests_table_ref` equals `tests.csv` `source_file`;
- for the BASS-II and BASS configurations, the sample family of the table row ("Fuel Sample Material" column, `bass2_family` and `bass_family`, the `FAMILY` map);
- for the other notes in brackets: `Fuel = X` (fuel substring), `S1`–`S9` (test id suffix), `2-n` (test number set or range).

I have no better key today. An explicit list of source rows per configuration would be exact, but that is a catalog structure change on submission day, so not now.

What to expect in your comparison:
- **No per-test rows** (`not_comparable`, or 0 tests):
  - the five day tables (ACME BRE, CLD, E-FIELD, S-FLAME, SLICE: one row per test day);
  - FLEX-2 (planned matrix);
  - DAFT (sampling sessions);
  - the ground analyses.
  - Since config 1.5.1 (10:10) the catalog itself classes the day tables as `summary_table`, after checking the tables.
- **Values not in the tables.** A catalog range whose `*_source` is `record`, `test_matrix` or `team` is not in the table by design:
  - ACME-BRE pressure;
  - the BASS flow ("up to 40 cm/s");
  - the FLEX-2 values;
  - FLEX, CFI and ACME-BRE flow.
  - `catalog_has_no_value` is expected for the atmospheres that the scorer fills only at scoring time.
- **`catalog_wider`** is mostly expected: a catalog range is the span over a configuration's tests, sometimes including tests that `tests.csv` leaves without a value. `web/check_integration.py` already notes seven such cases for the demo queries, for example the SAFFIRE-I O2 21.5–21.7 against the tests' 21.7.

The catalog reads your file as information. What to do about a difference is the catalog's call, and I will look at it when it lands.
