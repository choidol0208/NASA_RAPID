# Order changes: `OF2012.table1`

*AI-generated (Claude Code), 2026-11-14. Not human-reviewed. Experiment on branch data-lab.*

Item `OF2012.table1` of `NTRS-20130010991` (Table I, p. 6); https://ntrs.nasa.gov/citations/20130010991.
Printed title: "Table I: Limiting Oxygen Molar Concentrations and Oxygen Margin of Safety for Different Gravity Levels"
Condition columns: gravity level.

## Notes

- Values are as printed.
- Measurement uncertainty or step size: not stated in the item. A difference of one printed unit may or may not be resolved by the test method.
- These counts describe the order of printed values; they say nothing about why the order changes.
- ULOI and MOC are reported separately and are not compared with each other.
- The item states that the low-gravity limits come from 5.18 s drop tower tests and that their criteria are not the same as in 1g.
- The delta O2 rows of the table are a difference the paper computes from the other rows and are not used here.
- The held values say that the materials were tested at different pressures; a pair of materials at different pressures compares two conditions at once.

## Choices (spec parameters)

- `classes`: for materials a, b and condition columns c1, c2: s1 = sign(a[c1] - b[c1]), s2 = sign(a[c2] - b[c2]); same_order if s1 = s2 != 0; reversed if s1 = -s2 != 0; tie_in_one if exactly one of s1, s2 is 0; tie_in_both if both are 0
- `column_pairs`: every unordered pair of condition columns, in the column order of the spec
- `kendall_tau_b`: tau_b = (n_c - n_d) / sqrt((n_0 - n_1)(n_0 - n_2)), n_0 = n(n-1)/2 material pairs, n_c = same_order pairs, n_d = reversed pairs, n_1 = pairs tied in c1 (tie_in_both included), n_2 = pairs tied in c2; given exactly as numerator and the integer under the square root, and as a decimal rounded half-even to 'tau_b_digits' digits; undefined where the square root is 0
- `material_pairs`: every unordered pair of materials, in the row order of the item
- `tau_b_digits`: 6
- `values`: values are read as printed in the reference item's 'values' (exact decimals; JSON numbers read as decimal strings), no tolerance

## ULOI: upward limiting oxygen index (1g) and ULOI* (low gravity), % O2

Values as held:

| material | 1g | martian | lunar | 0g | held: test pressure (psia, as printed) |
|---|---|---|---|---|---|
| Mylar G | 21.2 | 18 | 15.6 | 17 | 10.2 |
| Ultem 1000 | 23.5 | 22 | 21 | 24 | 10.2 |
| Nomex HT90-40 | 23.5 | 19.9 | 21 | 23 | 14.7 |

| columns | pairs | same order | reversed | tie in one | tie in both | tau-b | tau-b exact form |
|---|---|---|---|---|---|---|---|
| 1g vs martian | 3 | 2 | 0 | 1 | 0 | 0.816497 | 2 / sqrt(6) |
| 1g vs lunar | 3 | 2 | 0 | 0 | 1 | 1.000000 | 2 / sqrt(4) |
| 1g vs 0g | 3 | 2 | 0 | 1 | 0 | 0.816497 | 2 / sqrt(6) |
| martian vs lunar | 3 | 2 | 0 | 1 | 0 | 0.816497 | 2 / sqrt(6) |
| martian vs 0g | 3 | 3 | 0 | 0 | 0 | 1.000000 | 3 / sqrt(9) |
| lunar vs 0g | 3 | 2 | 0 | 1 | 0 | 0.816497 | 2 / sqrt(6) |

1g vs martian:

| class | a | b | a at 1g | b at 1g | a at martian | b at martian | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tie_in_one | Ultem 1000 | Nomex HT90-40 | 23.5 | 23.5 | 22 | 19.9 | 10.2 | 14.7 |

1g vs 0g:

| class | a | b | a at 1g | b at 1g | a at 0g | b at 0g | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tie_in_one | Ultem 1000 | Nomex HT90-40 | 23.5 | 23.5 | 24 | 23 | 10.2 | 14.7 |

martian vs lunar:

| class | a | b | a at martian | b at martian | a at lunar | b at lunar | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tie_in_one | Ultem 1000 | Nomex HT90-40 | 22 | 19.9 | 21 | 21 | 10.2 | 14.7 |

lunar vs 0g:

| class | a | b | a at lunar | b at lunar | a at 0g | b at 0g | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tie_in_one | Ultem 1000 | Nomex HT90-40 | 21 | 21 | 24 | 23 | 10.2 | 14.7 |

## MOC: maximum oxygen concentration (1g) and MOC* (low gravity), % O2

Values as held:

| material | 1g | martian | lunar | 0g | held: test pressure (psia, as printed) |
|---|---|---|---|---|---|
| Mylar G | 20 | 17 | 14.1 | 16 | 10.2 |
| Ultem 1000 | 23 | 21.1 | 19.9 | 23 | 10.2 |
| Nomex HT90-40 | 22.1 | 19 | 19.9 | 22 | 14.7 |

| columns | pairs | same order | reversed | tie in one | tie in both | tau-b | tau-b exact form |
|---|---|---|---|---|---|---|---|
| 1g vs martian | 3 | 3 | 0 | 0 | 0 | 1.000000 | 3 / sqrt(9) |
| 1g vs lunar | 3 | 2 | 0 | 1 | 0 | 0.816497 | 2 / sqrt(6) |
| 1g vs 0g | 3 | 3 | 0 | 0 | 0 | 1.000000 | 3 / sqrt(9) |
| martian vs lunar | 3 | 2 | 0 | 1 | 0 | 0.816497 | 2 / sqrt(6) |
| martian vs 0g | 3 | 3 | 0 | 0 | 0 | 1.000000 | 3 / sqrt(9) |
| lunar vs 0g | 3 | 2 | 0 | 1 | 0 | 0.816497 | 2 / sqrt(6) |

1g vs lunar:

| class | a | b | a at 1g | b at 1g | a at lunar | b at lunar | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tie_in_one | Ultem 1000 | Nomex HT90-40 | 23 | 22.1 | 19.9 | 19.9 | 10.2 | 14.7 |

martian vs lunar:

| class | a | b | a at martian | b at martian | a at lunar | b at lunar | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tie_in_one | Ultem 1000 | Nomex HT90-40 | 21.1 | 19 | 19.9 | 19.9 | 10.2 | 14.7 |

lunar vs 0g:

| class | a | b | a at lunar | b at lunar | a at 0g | b at 0g | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tie_in_one | Ultem 1000 | Nomex HT90-40 | 19.9 | 19.9 | 23 | 22 | 10.2 | 14.7 |
