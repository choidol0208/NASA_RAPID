# Order changes: `H2006.table2`

*AI-generated (Claude Code), 2026-11-14. Not human-reviewed. Experiment on branch data-lab.*

Item `H2006.table2` of `JTE-2006-HIRSCH` (Table 2, p. 4 (page viewed as an image; all cells agree with the text layer)); https://ntrs.nasa.gov/citations/20070005041.
Printed title: "TABLE 2 — Oxygen concentration, oxygen partial pressure and total pressure flammability limits for selected materials at ambient initial temperatures"
Condition columns: total pressure (kPa).

## Notes

- Values are shown with the digits held in the item's 'values' (for example 18.0); comparisons read them as exact decimals.
- Measurement uncertainty or step size: not stated in the item. A difference of one printed unit may or may not be resolved by the test method.
- These counts describe the order of printed values; they say nothing about why the order changes.
- The item states normal gravity and quiescent conditions for every cell.

## Choices (spec parameters)

- `classes`: for materials a, b and condition columns c1, c2: s1 = sign(a[c1] - b[c1]), s2 = sign(a[c2] - b[c2]); same_order if s1 = s2 != 0; reversed if s1 = -s2 != 0; tie_in_one if exactly one of s1, s2 is 0; tie_in_both if both are 0
- `column_pairs`: every unordered pair of condition columns, in the column order of the spec
- `criterion`: each condition column carries the criterion named in the spec; a column pair is marked same criterion yes or no; pairs with different criteria are counted like all others and marked
- `held`: where the item holds a per-material condition (OF2012: test pressure), each class count is also given for the pairs whose held values differ
- `kendall_tau_b`: tau_b = (n_c - n_d) / sqrt((n_0 - n_1)(n_0 - n_2)), n_0 = n(n-1)/2 material pairs, n_c = same_order pairs, n_d = reversed pairs, n_1 = pairs tied in c1 (tie_in_both included), n_2 = pairs tied in c2; given exactly as numerator and the integer under the square root, and as a decimal rounded half-even to 'tau_b_digits' digits; undefined where the square root is 0
- `material_pairs`: every unordered pair of materials, in the row order of the item
- `tau_b_digits`: 6
- `values`: values are read as printed in the reference item's 'values' (exact decimals; JSON numbers read as decimal strings), no tolerance

## MOC: maximum oxygen concentration, vol %

Values as held:

| material | 48.2 | 85.3 | 101.3 |
|---|---|---|---|
| PTFE | 53 | 46 | 42 |
| Kel-F 81 | 76 | 56 | 53 |
| Silicone | 28 | 23 | 21 |
| Zytel 42 | 25 | 23 | 23 |
| Viton A | 29 | 21 | 21 |
| Buna S | 18 | 17 | 16 |
| Neoprene | 18 | 17 | 16 |
| Buna N | 18 | 16 | 15 |
| EPDM Rubber | 18 | 16 | 16 |
| Polyethylene | 18 | 18 | 17 |
| Delrin | 13 | 12 | 11 |

| columns | pairs | same order | reversed | tie in one | tie in both | tau-b | tau-b exact form |
|---|---|---|---|---|---|---|---|
| 48.2 vs 85.3 | 55 | 42 | 2 | 9 | 2 | 0.826898 | 40 / sqrt(2340) |
| 48.2 vs 101.3 | 55 | 42 | 2 | 8 | 3 | 0.834966 | 40 / sqrt(2295) |
| 85.3 vs 101.3 | 55 | 49 | 0 | 5 | 1 | 0.951501 | 49 / sqrt(2652) |

48.2 vs 85.3:

| class | a | b | a at 48.2 | b at 48.2 | a at 85.3 | b at 85.3 |
|---|---|---|---|---|---|---|
| tie_in_one | Silicone | Zytel 42 | 28 | 25 | 23 | 23 |
| reversed | Silicone | Viton A | 28 | 29 | 23 | 21 |
| reversed | Zytel 42 | Viton A | 25 | 29 | 23 | 21 |
| tie_in_one | Buna S | Buna N | 18 | 18 | 17 | 16 |
| tie_in_one | Buna S | EPDM Rubber | 18 | 18 | 17 | 16 |
| tie_in_one | Buna S | Polyethylene | 18 | 18 | 17 | 18 |
| tie_in_one | Neoprene | Buna N | 18 | 18 | 17 | 16 |
| tie_in_one | Neoprene | EPDM Rubber | 18 | 18 | 17 | 16 |
| tie_in_one | Neoprene | Polyethylene | 18 | 18 | 17 | 18 |
| tie_in_one | Buna N | Polyethylene | 18 | 18 | 16 | 18 |
| tie_in_one | EPDM Rubber | Polyethylene | 18 | 18 | 16 | 18 |

48.2 vs 101.3:

| class | a | b | a at 48.2 | b at 48.2 | a at 101.3 | b at 101.3 |
|---|---|---|---|---|---|---|
| reversed | Silicone | Zytel 42 | 28 | 25 | 21 | 23 |
| tie_in_one | Silicone | Viton A | 28 | 29 | 21 | 21 |
| reversed | Zytel 42 | Viton A | 25 | 29 | 23 | 21 |
| tie_in_one | Buna S | Buna N | 18 | 18 | 16 | 15 |
| tie_in_one | Buna S | Polyethylene | 18 | 18 | 16 | 17 |
| tie_in_one | Neoprene | Buna N | 18 | 18 | 16 | 15 |
| tie_in_one | Neoprene | Polyethylene | 18 | 18 | 16 | 17 |
| tie_in_one | Buna N | EPDM Rubber | 18 | 18 | 15 | 16 |
| tie_in_one | Buna N | Polyethylene | 18 | 18 | 15 | 17 |
| tie_in_one | EPDM Rubber | Polyethylene | 18 | 18 | 16 | 17 |

85.3 vs 101.3:

| class | a | b | a at 85.3 | b at 85.3 | a at 101.3 | b at 101.3 |
|---|---|---|---|---|---|---|
| tie_in_one | Silicone | Zytel 42 | 23 | 23 | 21 | 23 |
| tie_in_one | Silicone | Viton A | 23 | 21 | 21 | 21 |
| tie_in_one | Buna S | EPDM Rubber | 17 | 16 | 16 | 16 |
| tie_in_one | Neoprene | EPDM Rubber | 17 | 16 | 16 | 16 |
| tie_in_one | Buna N | EPDM Rubber | 16 | 16 | 15 | 16 |
