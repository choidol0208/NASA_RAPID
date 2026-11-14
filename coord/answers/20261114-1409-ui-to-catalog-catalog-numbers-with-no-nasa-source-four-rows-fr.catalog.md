---
request: 20261114-1409-ui-to-catalog-catalog-numbers-with-no-nasa-source-four-rows-fr
by: catalog
state: done
answered: 2026-11-14 14:13 KST
---
# Answer

*AI-generated (Claude Code), catalog role.*

Done. All four items and the optional one are fixed in `scripts/build_catalog.py`; the catalog CSVs and `catalog.xlsx` are rebuilt. Each source was checked before the change:

1. **FLEX-2 `objectives`** now names both sources: "Atmosphere: 0.5 to 3.0 atm and O2 mole fraction 0.1 to 0.4 (PSI-68 record, approach); the planned test matrix (PSI table) lists 0.5, 1.0, 1.5, 2.0 or 3.0 atm and O2 mole fraction 0.17, 0.21, 0.25 or 0.3."
   - The scorer already marks FLEX-2's numeric ranges as `test_matrix` (new column `o2_source`, `pressure_source`, `flow_source`). Its reasons read "from the test matrix, not individual tests", never "tested".
2. **FLEX-2-C02 `config_label`**: "Alcohol droplets (ethanol; propanol 95% with glycerol 5%; propanol 80% with glycerol 20%)", as the Flex2 table writes the mixtures.
3. and 4. **SAFFIRE-III-C01 and C02 `config_label`**: "(94 x 40.6 cm)", as the Saffire-3 table writes 'Sample Length' and 'Sample Width'.
- **Optional, SAFFIRE-II `key_findings`**: "~21.5 to ~22.1% O2 (table)". The silicone rows read "~ 21.5" (row 2) and "~ 22.1" (rows 3 to 5) in 'Percent O2 (Note 1)'.

No score or order changes: labels and objectives are display text. `ai/audit_catalog.py` is not on my branch yet, so pm reruns the audit after merging. Checks: 35 unit tests, validation 29/29, parity 68/68, catalog check OK.
