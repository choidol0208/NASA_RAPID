# Catalog against the NASA sources

*Written by `python3 validation/check_catalog_sources.py` (AI-generated code). Not a deploy step.*

- Ranking values (O2, pressure, flow ends): 115 checked, 107 found, 0 not found, 8 team readings.
- Range ends compared with the column of a table used by one configuration: 24 match, 0 differ.
- Test counts: 14 match, 1 differ with the reason in source_notes, 0 differ, 20 not compared (shared table or no table).
- Numbers in the text the page shows: 135 checked, 135 found, 0 not found.

'Found' means the number is written in the source, not that its meaning was checked.

## Ranking values

| Configuration | Field | Value | Source | Where | Range end |
|---|---|---|---|---|---|
| ACME-FLAME-DESIGN-C01 | o2_min_pct | 19.8 | table | PSI-10_Experimental table_Flame Design_Normal Flame.csv, row 188, 'XO2 (init)' = '0.198048193' (mole fraction) | end matches column |
| ACME-FLAME-DESIGN-C01 | o2_max_pct | 40 | table | PSI-10_Experimental table_Flame Design_Normal Flame.csv, row 189, 'XO2 (init)' = '0.4' (mole fraction) | end matches column |
| ACME-FLAME-DESIGN-C01 | pressure_min_kpa | 94.4 | table | PSI-10_Experimental table_Flame Design_Normal Flame.csv, row 189, 'pinit (atm)' = '0.931972789' (atm) | end matches column |
| ACME-FLAME-DESIGN-C01 | pressure_max_kpa | 131.4 | table | PSI-10_Experimental table_Flame Design_Normal Flame.csv, row 140, 'pinit (atm)' = '1.29559584' (atm) | end matches column |
| ACME-FLAME-DESIGN-C02 | o2_min_pct | 21.2 | table | PSI-10_Experimental table_Flame Design_Inverse Flame.csv, row 4, 'XO2' = '0.212319452' (mole fraction) | end matches column |
| ACME-FLAME-DESIGN-C02 | o2_max_pct | 85 | table | PSI-10_Experimental table_Flame Design_Inverse Flame.csv, row 5, 'XO2' = '0.849977932' (mole fraction) | end matches column |
| ACME-FLAME-DESIGN-C02 | pressure_min_kpa | 43 | table | PSI-10_Experimental table_Flame Design_Inverse Flame.csv, row 24, 'pinit (atm)' = '0.42460704' (atm) | end matches column |
| ACME-FLAME-DESIGN-C02 | pressure_max_kpa | 304.7 | table | PSI-10_Experimental table_Flame Design_Inverse Flame.csv, row 97, 'pinit (atm)' = '3.00491136' (atm) | end matches column |
| ACME-BRE-C01 | o2_min_pct | 21 | table | PSI-20_Experimental table_ACME BRE.csv, row 2, 'Oxygen Conc (percent)' = '21; 26.5; 40' (%) | end matches column (left out as not a reading: row 6 '3400%', row 9 '2100%') |
| ACME-BRE-C01 | o2_max_pct | 40 | table | PSI-20_Experimental table_ACME BRE.csv, row 2, 'Oxygen Conc (percent)' = '21; 26.5; 40' (%) | end matches column (left out as not a reading: row 6 '3400%', row 9 '2100%') |
| ACME-BRE-C01 | pressure_min_kpa | 56.5 | record | PSI record: 8.2 psi |  |
| ACME-BRE-C01 | pressure_max_kpa | 101.3 | record | PSI record: 1 atm |  |
| ACME-BRE-C01 | flow_min_cms | 0 | team | team reading (by design) |  |
| ACME-BRE-C01 | flow_max_cms | 0 | team | team reading (by design) |  |
| ACME-S-FLAME-C01 | o2_min_pct | 21 | table | PSI-23_Experimental table_ACME s-Flame.csv, row 2, 'Atmosphere*' = '~21% O2 with N2' (%) |  |
| ACME-S-FLAME-C01 | o2_max_pct | 30 | table | PSI-23_Experimental table_ACME s-Flame.csv, row 5, 'Atmosphere*' = '~30% O2 with N2' (%) |  |
| ACME-S-FLAME-C01 | pressure_min_kpa | 101.3 | table | PSI-23_Experimental table_ACME s-Flame.csv, row 3, 'Notes' = '*Atmosphere is ~1 atm but pressure increases and O2% drops with vitiation.' (atm) |  |
| ACME-S-FLAME-C01 | pressure_max_kpa | 101.3 | table | PSI-23_Experimental table_ACME s-Flame.csv, row 3, 'Notes' = '*Atmosphere is ~1 atm but pressure increases and O2% drops with vitiation.' (atm) |  |
| BASS-II-C01 | o2_min_pct | 15 | table | PSI-25_Experimental table_BASS-II.csv, row 15, 'Calibrated  initial O2 % by vol' = '15' (%) |  |
| BASS-II-C01 | o2_max_pct | 22.2 | table | PSI-25_Experimental table_BASS-II.csv, row 2, 'Calibrated  initial O2 % by vol' = '22.2' (%) |  |
| BASS-II-C01 | flow_min_cms | 0 | table | PSI-25_Experimental table_BASS-II.csv, row 9, 'Flow restrictor' = '0' (cm/s) |  |
| BASS-II-C01 | flow_max_cms | 10 | table | PSI-25_Experimental table_BASS-II.csv, row 7, 'Air display' = '3   5   approaching 10' (cm/s) |  |
| BASS-II-C02 | o2_min_pct | 17.9 | table | PSI-25_Experimental table_BASS-II.csv, row 45, 'Calibrated  initial O2 % by vol' = '17.9' (%) |  |
| BASS-II-C02 | o2_max_pct | 22.2 | table | PSI-25_Experimental table_BASS-II.csv, row 2, 'Calibrated  initial O2 % by vol' = '22.2' (%) |  |
| BASS-II-C02 | flow_min_cms | 0 | table | PSI-25_Experimental table_BASS-II.csv, row 9, 'Flow restrictor' = '0' (cm/s) |  |
| BASS-II-C02 | flow_max_cms | 20 | table | PSI-25_Experimental table_BASS-II.csv, row 29, 'Air display' = '20  15  13   14' (cm/s) |  |
| BASS-II-C03 | o2_min_pct | 13.6 | table | PSI-25_Experimental table_BASS-II.csv, row 62, 'Calibrated  initial O2 % by vol' = '13.6' (%) |  |
| BASS-II-C03 | o2_max_pct | 22.2 | table | PSI-25_Experimental table_BASS-II.csv, row 2, 'Calibrated  initial O2 % by vol' = '22.2' (%) |  |
| BASS-II-C03 | flow_min_cms | 0 | table | PSI-25_Experimental table_BASS-II.csv, row 9, 'Flow restrictor' = '0' (cm/s) |  |
| BASS-II-C03 | flow_max_cms | 38.5 | table | PSI-25_Experimental table_BASS-II.csv, row 72, 'Air display' = '5   8    incr to max 38.5' (cm/s) |  |
| BASS-II-C04 | o2_min_pct | 16.4 | table | PSI-25_Experimental table_BASS-II.csv, row 82, 'Calibrated  initial O2 % by vol' = '16.4' (%) |  |
| BASS-II-C04 | o2_max_pct | 20.8 | table | PSI-25_Experimental table_BASS-II.csv, row 22, 'Calibrated  initial O2 % by vol' = '20.8' (%) |  |
| BASS-II-C04 | flow_min_cms | 1 | table | PSI-25_Experimental table_BASS-II.csv, row 22, 'Flow restrictor' = '1' (cm/s) |  |
| BASS-II-C04 | flow_max_cms | 29 | table | PSI-25_Experimental table_BASS-II.csv, row 115, 'Air display' = '9   29' (cm/s) |  |
| BASS-II-C05 | o2_min_pct | 21 | table | PSI-25_Experimental table_BASS-II.csv, row 7, 'Calibrated  initial O2 % by vol' = '21' (%) |  |
| BASS-II-C05 | o2_max_pct | 22.2 | table | PSI-25_Experimental table_BASS-II.csv, row 2, 'Calibrated  initial O2 % by vol' = '22.2' (%) |  |
| BASS-II-C05 | flow_min_cms | 8 | table | PSI-25_Experimental table_BASS-II.csv, row 26, 'Air display' = '8' (cm/s) |  |
| BASS-II-C05 | flow_max_cms | 15 | table | PSI-25_Experimental table_BASS-II.csv, row 25, 'Air display' = '15' (cm/s) |  |
| BASS-II-C06 | o2_min_pct | 17.2 | table | PSI-25_Experimental table_BASS-II.csv, row 104, 'Calibrated  initial O2 % by vol' = '17.2' (%) |  |
| BASS-II-C06 | o2_max_pct | 17.4 | table | PSI-25_Experimental table_BASS-II.csv, row 19, 'Calibrated  initial O2 % by vol' = '17.4' (%) |  |
| BASS-II-C06 | flow_min_cms | 1 | table | PSI-25_Experimental table_BASS-II.csv, row 22, 'Flow restrictor' = '1' (cm/s) |  |
| BASS-II-C06 | flow_max_cms | 10 | table | PSI-25_Experimental table_BASS-II.csv, row 7, 'Air display' = '3   5   approaching 10' (cm/s) |  |
| BASS-C01 | flow_max_cms | 40 | record | PSI record: 40 cm/s |  |
| BASS-C02 | flow_max_cms | 40 | record | PSI record: 40 cm/s |  |
| BASS-C03 | flow_max_cms | 40 | record | PSI record: 40 cm/s |  |
| BASS-C04 | flow_max_cms | 40 | record | PSI record: 40 cm/s |  |
| BASS-C05 | flow_max_cms | 40 | record | PSI record: 40 cm/s |  |
| CFI-C01 | o2_min_pct | 17 | table | PSI-39_Experimental table_CFI.csv, row 8, 'Oxygen' = '0.17' (mole fraction) | end matches column |
| CFI-C01 | o2_max_pct | 21 | table | PSI-39_Experimental table_CFI.csv, row 2, 'Oxygen' = '0.21' (mole fraction) | end matches column |
| CFI-C01 | pressure_min_kpa | 50.7 | table | PSI-39_Experimental table_CFI.csv, row 64, 'Pressure' = '0.5 atm' (atm) | end matches column |
| CFI-C01 | pressure_max_kpa | 506.6 | table | PSI-39_Experimental table_CFI.csv, row 57, 'Pressure' = '5 atm' (atm) | end matches column |
| CFI-C01 | flow_min_cms | 0 | team | team reading (by design) |  |
| CFI-C01 | flow_max_cms | 0 | team | team reading (by design) |  |
| FLEX-2-C01 | o2_min_pct | 17 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Oxygen Mole Fraction' = '0.17; 0.21;0.25; 0.3' (mole fraction) |  |
| FLEX-2-C01 | o2_max_pct | 30 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Oxygen Mole Fraction' = '0.17; 0.21;0.25; 0.3' (mole fraction) |  |
| FLEX-2-C01 | pressure_min_kpa | 50.7 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Ambient Pressure (atm)' = '0.5; 1.0; 1.5; 2.0; or 3.0' (atm) |  |
| FLEX-2-C01 | pressure_max_kpa | 304 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Ambient Pressure (atm)' = '0.5; 1.0; 1.5; 2.0; or 3.0' (atm) |  |
| FLEX-2-C01 | flow_min_cms | 0.1 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Flow Velocity (cm/s)' = '0.1 - 5' (cm/s) |  |
| FLEX-2-C01 | flow_max_cms | 5 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Flow Velocity (cm/s)' = '0.1 - 5' (cm/s) |  |
| FLEX-2-C02 | o2_min_pct | 17 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Oxygen Mole Fraction' = '0.17; 0.21;0.25; 0.3' (mole fraction) |  |
| FLEX-2-C02 | o2_max_pct | 30 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Oxygen Mole Fraction' = '0.17; 0.21;0.25; 0.3' (mole fraction) |  |
| FLEX-2-C02 | pressure_min_kpa | 50.7 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Ambient Pressure (atm)' = '0.5; 1.0; 1.5; 2.0; or 3.0' (atm) |  |
| FLEX-2-C02 | pressure_max_kpa | 304 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Ambient Pressure (atm)' = '0.5; 1.0; 1.5; 2.0; or 3.0' (atm) |  |
| FLEX-2-C02 | flow_min_cms | 0.1 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Flow Velocity (cm/s)' = '0.1 - 5' (cm/s) |  |
| FLEX-2-C02 | flow_max_cms | 5 | test_matrix | PSI-68_Experimental table_Flex2.csv, row 2, 'Flow Velocity (cm/s)' = '0.1 - 5' (cm/s) |  |
| FLEX-C01 | o2_min_pct | 12 | table | PSI-69_Experimental table_FLEX.csv, row 84, 'O initial ambient composition; mole fraction' = '0.12' (mole fraction) |  |
| FLEX-C01 | o2_max_pct | 34 | table | PSI-69_Experimental table_FLEX.csv, row 20, 'O initial ambient composition; mole fraction' = '0.34' (mole fraction) |  |
| FLEX-C01 | pressure_min_kpa | 70.2 | table | PSI-69_Experimental table_FLEX.csv, row 122, 'Ambient pressure; mmHg' = '526.3' (mmHg) |  |
| FLEX-C01 | pressure_max_kpa | 309.3 | table | PSI-69_Experimental table_FLEX.csv, row 11, 'Ambient pressure; mmHg' = '2319.7' (mmHg) |  |
| FLEX-C01 | flow_min_cms | 0 | team | team reading (by design) |  |
| FLEX-C01 | flow_max_cms | 0 | team | team reading (by design) |  |
| FLEX-C02 | o2_min_pct | 13 | table | PSI-69_Experimental table_FLEX.csv, row 76, 'O initial ambient composition; mole fraction' = '0.13' (mole fraction) |  |
| FLEX-C02 | o2_max_pct | 34 | table | PSI-69_Experimental table_FLEX.csv, row 20, 'O initial ambient composition; mole fraction' = '0.34' (mole fraction) |  |
| FLEX-C02 | pressure_min_kpa | 70.4 | table | PSI-69_Experimental table_FLEX.csv, row 263, 'Ambient pressure; mmHg' = '527.6' (mmHg) |  |
| FLEX-C02 | pressure_max_kpa | 309.3 | table | PSI-69_Experimental table_FLEX.csv, row 11, 'Ambient pressure; mmHg' = '2319.7' (mmHg) |  |
| FLEX-C02 | flow_min_cms | 0 | team | team reading (by design) |  |
| FLEX-C02 | flow_max_cms | 0 | team | team reading (by design) |  |
| SAFFIRE-I-C01 | o2_min_pct | 21.5 | table | PSI-98_Experimental table_SAFFIRE-1.csv, row 2, 'Percent O2' = '21.5 - 21.7' (%) |  |
| SAFFIRE-I-C01 | o2_max_pct | 21.7 | table | PSI-98_Experimental table_SAFFIRE-1.csv, row 2, 'Percent O2' = '21.5 - 21.7' (%) |  |
| SAFFIRE-I-C01 | flow_min_cms | 20 | table | PSI-98_Experimental table_SAFFIRE-1.csv, row 2, 'Air Flow (cm/s)' = '20' (cm/s) |  |
| SAFFIRE-I-C01 | flow_max_cms | 20 | table | PSI-98_Experimental table_SAFFIRE-1.csv, row 2, 'Air Flow (cm/s)' = '20' (cm/s) |  |
| SAFFIRE-I-C02 | o2_min_pct | 21.5 | table | PSI-98_Experimental table_SAFFIRE-1.csv, row 2, 'Percent O2' = '21.5 - 21.7' (%) |  |
| SAFFIRE-I-C02 | o2_max_pct | 21.5 | table | PSI-98_Experimental table_SAFFIRE-1.csv, row 2, 'Percent O2' = '21.5 - 21.7' (%) |  |
| SAFFIRE-I-C02 | flow_min_cms | 20 | table | PSI-98_Experimental table_SAFFIRE-1.csv, row 2, 'Air Flow (cm/s)' = '20' (cm/s) |  |
| SAFFIRE-I-C02 | flow_max_cms | 20 | table | PSI-98_Experimental table_SAFFIRE-1.csv, row 2, 'Air Flow (cm/s)' = '20' (cm/s) |  |
| SAFFIRE-II-C01 | o2_min_pct | 21.5 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 2, 'Percent O2 (Note 1)' = '~ 21.5' (%) |  |
| SAFFIRE-II-C01 | o2_max_pct | 22.1 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 3, 'Percent O2 (Note 1)' = '~ 22.1' (%) |  |
| SAFFIRE-II-C01 | flow_min_cms | 20 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 2, 'Air Flow (cm/s)' = '20 cm/s' (cm/s) |  |
| SAFFIRE-II-C01 | flow_max_cms | 20 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 2, 'Air Flow (cm/s)' = '20 cm/s' (cm/s) |  |
| SAFFIRE-II-C02 | o2_min_pct | 22.1 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 3, 'Percent O2 (Note 1)' = '~ 22.1' (%) |  |
| SAFFIRE-II-C02 | o2_max_pct | 22.1 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 3, 'Percent O2 (Note 1)' = '~ 22.1' (%) |  |
| SAFFIRE-II-C02 | flow_min_cms | 20 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 2, 'Air Flow (cm/s)' = '20 cm/s' (cm/s) |  |
| SAFFIRE-II-C02 | flow_max_cms | 20 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 2, 'Air Flow (cm/s)' = '20 cm/s' (cm/s) |  |
| SAFFIRE-II-C03 | o2_min_pct | 21.9 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 10, 'Percent O2 (Note 1)' = '22.0 to 21.9' (%) |  |
| SAFFIRE-II-C03 | o2_max_pct | 22.1 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 3, 'Percent O2 (Note 1)' = '~ 22.1' (%) |  |
| SAFFIRE-II-C03 | flow_min_cms | 20 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 2, 'Air Flow (cm/s)' = '20 cm/s' (cm/s) |  |
| SAFFIRE-II-C03 | flow_max_cms | 20 | table | PSI-99_Experimental table_SAFFIRE-2.csv, row 2, 'Air Flow (cm/s)' = '20 cm/s' (cm/s) |  |
| SAFFIRE-III-C01 | flow_min_cms | 30 | table | PSI-100_Experimental table_SAFFIRE-3.csv, row 2, 'Air Flow' = '30 cm/s' (cm/s) |  |
| SAFFIRE-III-C01 | flow_max_cms | 30 | table | PSI-100_Experimental table_SAFFIRE-3.csv, row 2, 'Air Flow' = '30 cm/s' (cm/s) |  |
| SAFFIRE-III-C02 | flow_min_cms | 30 | table | PSI-100_Experimental table_SAFFIRE-3.csv, row 2, 'Air Flow' = '30 cm/s' (cm/s) |  |
| SAFFIRE-III-C02 | flow_max_cms | 30 | table | PSI-100_Experimental table_SAFFIRE-3.csv, row 2, 'Air Flow' = '30 cm/s' (cm/s) |  |
| SAME-R-C01 | flow_min_cms | 0 | table | PSI-101_Experimental table_SAME-R.csv, row 24, 'Inlet velocity (cm/s)' = '0' (cm/s) | end matches column |
| SAME-R-C01 | flow_max_cms | 8.1 | table | PSI-101_Experimental table_SAME-R.csv, row 2, 'Inlet velocity (cm/s)' = '8.1' (cm/s) | end matches column |
| SAME-C01 | flow_min_cms | 5 | table | PSI-102_Experimental table_SAME.csv, row 2, 'Air Flow (cm/s)' = '5' (cm/s) | end matches column |
| SAME-C01 | flow_max_cms | 10 | table | PSI-102_Experimental table_SAME.csv, row 5, 'Air Flow (cm/s)' = '10' (cm/s) | end matches column |
| SPICE-C01 | flow_min_cms | 0.66 | table | PSI-107_Experimental table_Spice.csv, row 297, 'Air Rate (cm/s)' = '0.66' (cm/s) | end matches column (left out as not a reading: row 296 '-0.28', row 298 '-0.28', row 299 '-0.28' …) |
| SPICE-C01 | flow_max_cms | 85.28 | table | PSI-107_Experimental table_Spice.csv, row 139, 'Air Rate (cm/s)' = '85.28' (cm/s) | end matches column (left out as not a reading: row 296 '-0.28', row 298 '-0.28', row 299 '-0.28' …) |
| ACME-CFI-G-C01 | o2_min_pct | 18 | table | PSI-159_Experimental table_CFI-G_Normal Flames.csv, row 14, 'XO2 before test' = '0.1802' (mole fraction) | end matches column |
| ACME-CFI-G-C01 | o2_max_pct | 40 | table | PSI-159_Experimental table_CFI-G_Normal Flames.csv, row 114, 'XO2 before test' = '0.3996' (mole fraction) | end matches column |
| ACME-CFI-G-C01 | pressure_min_kpa | 50.7 | table | PSI-159_Experimental table_CFI-G_Normal Flames.csv, row 32, 'approx p (bar)' = '0.50665' (bar) | end matches column |
| ACME-CFI-G-C01 | pressure_max_kpa | 304 | table | PSI-159_Experimental table_CFI-G_Normal Flames.csv, row 102, 'approx p (bar)' = '3.0399' (bar) | end matches column |
| ACME-CFI-G-C02 | o2_min_pct | 12 | table | PSI-159_Experimental table_CFI-G_Inverse Flames.csv, row 5, 'XO2' = '0.12' (mole fraction) | end matches column |
| ACME-CFI-G-C02 | o2_max_pct | 85 | table | PSI-159_Experimental table_CFI-G_Inverse Flames.csv, row 18, 'XO2' = '0.85' (mole fraction) | end matches column |
| ACME-CFI-G-C02 | pressure_min_kpa | 49.5 | table | PSI-159_Experimental table_CFI-G_Inverse Flames.csv, row 12, 'approx p (bar)' = '0.4953817' (bar) | end matches column |
| ACME-CFI-G-C02 | pressure_max_kpa | 331 | table | PSI-159_Experimental table_CFI-G_Inverse Flames.csv, row 42, 'approx p (bar)' = '3.3099' (bar) | end matches column |

## Test counts

| Configuration | Catalog | Source | Result |
|---|---|---|---|
| ACME-FLAME-DESIGN-C01 | 207 | 207 distinct rows in PSI-10_Experimental table_Flame Design_Normal Flame.csv | match |
| ACME-FLAME-DESIGN-C02 | 120 | 120 distinct rows in PSI-10_Experimental table_Flame Design_Inverse Flame.csv | match |
| ACME-BRE-C01 | 194 | sum of 'Flames Ignited' in PSI-20_Experimental table_ACME BRE.csv = 194 | match |
| ACME-CLD-C01 | 344 | sum of 'Flames Ignited' in PSI-21_Experimental table_CLD Flame.csv = 344 | match |
| ACME-E-FIELD-C01 | 230 | sum of 'Flames Ignited' in PSI-22_Experimental table_ACME E-FIELD Flames.csv = 230 | match |
| ACME-S-FLAME-C01 | 276 | sum of 'Flames Ignited' in PSI-23_Experimental table_ACME s-Flame.csv = 276 | match |
| BASS-II-C01 | 22 | table shared with BASS-II-C02, BASS-II-C03, BASS-II-C04, BASS-II-C05, BASS-II-C06 | not compared |
| BASS-II-C02 | 20 | table shared with BASS-II-C01, BASS-II-C03, BASS-II-C04, BASS-II-C05, BASS-II-C06 | not compared |
| BASS-II-C03 | 54 | table shared with BASS-II-C01, BASS-II-C02, BASS-II-C04, BASS-II-C05, BASS-II-C06 | not compared |
| BASS-II-C04 | 27 | table shared with BASS-II-C01, BASS-II-C02, BASS-II-C03, BASS-II-C05, BASS-II-C06 | not compared |
| BASS-II-C05 | 3 | table shared with BASS-II-C01, BASS-II-C02, BASS-II-C03, BASS-II-C04, BASS-II-C06 | not compared |
| BASS-II-C06 | 3 | table shared with BASS-II-C01, BASS-II-C02, BASS-II-C03, BASS-II-C04, BASS-II-C05 | not compared |
| BASS-C01 | 12 | table shared with BASS-C02, BASS-C03, BASS-C04, BASS-C05 | not compared |
| BASS-C02 | 28 | table shared with BASS-C01, BASS-C03, BASS-C04, BASS-C05 | not compared |
| BASS-C03 | 50 | table shared with BASS-C01, BASS-C02, BASS-C04, BASS-C05 | not compared |
| BASS-C04 | 23 | table shared with BASS-C01, BASS-C02, BASS-C03, BASS-C05 | not compared |
| BASS-C05 | 8 | table shared with BASS-C01, BASS-C02, BASS-C03, BASS-C04 | not compared |
| CFI-C01 | 79 | 79 distinct rows in PSI-39_Experimental table_CFI.csv | match |
| DAFT-C01 | 2 | 2 distinct rows in PSI-47_Experimental table_DAFT.csv | match |
| FLEX-C01 | 157 | table shared with FLEX-C02 | not compared |
| FLEX-C02 | 117 | table shared with FLEX-C01 | not compared |
| SAFFIRE-I-C01 | 1 | table shared with SAFFIRE-I-C02 | not compared |
| SAFFIRE-I-C02 | 1 | table shared with SAFFIRE-I-C01 | not compared |
| SAFFIRE-II-C01 | 4 | table shared with SAFFIRE-II-C02, SAFFIRE-II-C03 | not compared |
| SAFFIRE-II-C02 | 2 | table shared with SAFFIRE-II-C01, SAFFIRE-II-C03 | not compared |
| SAFFIRE-II-C03 | 3 | table shared with SAFFIRE-II-C01, SAFFIRE-II-C02 | not compared |
| SAFFIRE-III-C01 | 1 | table shared with SAFFIRE-III-C02 | not compared |
| SAFFIRE-III-C02 | 1 | table shared with SAFFIRE-III-C01 | not compared |
| SAME-R-C01 | 109 | 109 distinct rows in PSI-101_Experimental table_SAME-R.csv | match |
| SAME-C01 | 4 | 8 distinct rows in PSI-102_Experimental table_SAME.csv; source_notes: rows 2 to 5 (samples 1 to 4, Teflon) record air flow, weight-loss rate and aging time | documented |
| SLICE-C01 | 12 | 12 distinct rows in PSI-106_Experimental table_Slice.csv | match |
| SPICE-C01 | 435 | 435 distinct rows in PSI-107_Experimental table_Spice.csv | match |
| COOLFLAME-COUNTERFLOW-C01 | 8 | 8 distinct rows in PSI-142_Experimental table_Data Summary Table.csv | match |
| ACME-CFI-G-C01 | 179 | 179 distinct rows in PSI-159_Experimental table_CFI-G_Normal Flames.csv | match |
| ACME-CFI-G-C02 | 154 | 154 distinct rows in PSI-159_Experimental table_CFI-G_Inverse Flames.csv | match |
