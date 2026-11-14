# Order changes: `OF2012.table1`

*AI-generated (Claude Code), 2026-11-14. Not human-reviewed. Experiment on branch data-lab.*

Item `OF2012.table1` of `NTRS-20130010991` (Table I, p. 6); https://ntrs.nasa.gov/citations/20130010991.
Printed title: "Table I: Limiting Oxygen Molar Concentrations and Oxygen Margin of Safety for Different Gravity Levels"
Condition columns: gravity level.

## Notes

- Values are shown with the digits held in the item's 'values' (for example 18.0); comparisons read them as exact decimals.
- Measurement uncertainty or step size: not stated in the item. A difference of one printed unit may or may not be resolved by the test method.
- These counts describe the order of printed values; they say nothing about why the order changes.
- ULOI and MOC are reported separately and are not compared with each other.
- The item states that the low-gravity limits come from 5.18 s drop tower tests and that their criteria are not the same as in 1g.
- The delta O2 rows of the table are a difference the paper computes from the other rows and are not used here.
- The item's note says that the 0g values were obtained with a concurrent flow of 30 cm/s (p. 4), that the Lunar and 0g data are from ref. 8 (Ferkul and Olson 2011), and that the asterisk on '0g*' is not defined anywhere in the paper.
- Pairs of columns with different criteria (marked 'same criterion: no') compare a 1g limit with a drop-tower limit; the item says these criteria are not the same.
- The held values say that the materials were tested at different pressures; a pair of materials at different pressures compares two conditions at once. The count of such pairs is given per class beside the counts.

## Choices (spec parameters)

- `classes`: for materials a, b and condition columns c1, c2: s1 = sign(a[c1] - b[c1]), s2 = sign(a[c2] - b[c2]); concordant if s1 = s2 != 0; discordant if s1 = -s2 != 0; tied_first_column_only if s1 = 0 and s2 != 0 (T_x); tied_second_column_only if s2 = 0 and s1 != 0 (T_y); tied_both_columns if both are 0. Concordant, discordant, tie, T_x and T_y as defined on the NIST Dataplot KENDALLS TAU page; tied_both_columns is the remaining class and enters neither T_x nor T_y
- `column_pairs`: every unordered pair of condition columns, in the column order of the spec
- `criterion`: each condition column carries the criterion named in the spec; a column pair is marked same criterion yes or no; pairs with different criteria are counted like all others and marked
- `held`: where the item holds a per-material condition (OF2012: test pressure), each class count is also given for the pairs whose held values differ
- `kendall_tau_b`: tau_b = (N_c - N_d) / sqrt((N_c + N_d + T_x)(N_c + N_d + T_y)) as defined on the NIST Dataplot KENDALLS TAU page (https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/kendell.htm); N_c = concordant pairs, N_d = discordant pairs, T_x, T_y = pairs tied in one column only; the script stops if the denominator differs from (n_0 - n_1)(n_0 - n_2); given exactly as numerator and the integer under the square root, and as a decimal rounded half-even to 'tau_b_digits' digits; undefined where the square root is 0
- `material_pairs`: every unordered pair of materials, in the row order of the item
- `tau_b_digits`: 6
- `values`: values are read as printed in the reference item's 'values' (exact decimals; JSON numbers read as decimal strings), no tolerance

## Governed by (pipeline/lab/model_map.json)

- M06a: KENDALL_B, NIST Dataplot Reference Manual, KENDALLS TAU (https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/kendell.htm; opened by ranking scout (via Exa); verifier (via Exa web fetch, 2026-11-14); lab session (via Exa, 2026-11-14))
- M06b: KENDALL_B, NIST Dataplot Reference Manual, KENDALLS TAU (https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/kendell.htm; opened by ranking scout (via Exa); verifier (via Exa web fetch, 2026-11-14); lab session (via Exa, 2026-11-14))
- M06c: team rule, no established model found
- M06d: team rule, no established model found
- M06e: team rule, no established model found
- M08: ELEM, elementary mathematics (the definition is the model)

## ULOI: upward limiting oxygen index (1g) and ULOI* (low gravity), % O2

Values as held:

| material | 1g | martian | lunar | 0g | held: test pressure (psia, as printed) |
|---|---|---|---|---|---|
| Mylar G | 21.2 | 18.0 | 15.6 | 17.0 | 10.2 |
| Ultem 1000 | 23.5 | 22.0 | 21.0 | 24.0 | 10.2 |
| Nomex HT90-40 | 23.5 | 19.9 | 21.0 | 23.0 | 14.7 |

| columns | pairs | concordant [M06a: KENDALL_B] | discordant | tied in first column only (T_x) | tied in second column only (T_y) | tied in both | tau-b [M06b: KENDALL_B; digits M06c: team rule] | tau-b exact form | same criterion [M06d: team rule] | of these, pairs at different test pressure (psia, as printed) (conc / disc / T_x / T_y / both) [M06e: team rule] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1g vs martian | 3 | 2 | 0 | 1 | 0 | 0 | 0.816497 | 2 / sqrt(6) | no | 1 / 0 / 1 / 0 / 0 |
| 1g vs lunar | 3 | 2 | 0 | 0 | 0 | 1 | 1.000000 | 2 / sqrt(4) | no | 1 / 0 / 0 / 0 / 1 |
| 1g vs 0g | 3 | 2 | 0 | 1 | 0 | 0 | 0.816497 | 2 / sqrt(6) | no | 1 / 0 / 1 / 0 / 0 |
| martian vs lunar | 3 | 2 | 0 | 0 | 1 | 0 | 0.816497 | 2 / sqrt(6) | yes | 1 / 0 / 0 / 1 / 0 |
| martian vs 0g | 3 | 3 | 0 | 0 | 0 | 0 | 1.000000 | 3 / sqrt(9) | yes | 2 / 0 / 0 / 0 / 0 |
| lunar vs 0g | 3 | 2 | 0 | 1 | 0 | 0 | 0.816497 | 2 / sqrt(6) | yes | 1 / 0 / 1 / 0 / 0 |

1g vs martian:

| class | a | b | a at 1g | b at 1g | a at martian | b at martian | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tied_first_column_only | Ultem 1000 | Nomex HT90-40 | 23.5 | 23.5 | 22.0 | 19.9 | 10.2 | 14.7 |

1g vs 0g:

| class | a | b | a at 1g | b at 1g | a at 0g | b at 0g | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tied_first_column_only | Ultem 1000 | Nomex HT90-40 | 23.5 | 23.5 | 24.0 | 23.0 | 10.2 | 14.7 |

martian vs lunar:

| class | a | b | a at martian | b at martian | a at lunar | b at lunar | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tied_second_column_only | Ultem 1000 | Nomex HT90-40 | 22.0 | 19.9 | 21.0 | 21.0 | 10.2 | 14.7 |

lunar vs 0g:

| class | a | b | a at lunar | b at lunar | a at 0g | b at 0g | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tied_first_column_only | Ultem 1000 | Nomex HT90-40 | 21.0 | 21.0 | 24.0 | 23.0 | 10.2 | 14.7 |

## MOC: maximum oxygen concentration (1g) and MOC* (low gravity), % O2

Values as held:

| material | 1g | martian | lunar | 0g | held: test pressure (psia, as printed) |
|---|---|---|---|---|---|
| Mylar G | 20.0 | 17.0 | 14.1 | 16.0 | 10.2 |
| Ultem 1000 | 23.0 | 21.1 | 19.9 | 23.0 | 10.2 |
| Nomex HT90-40 | 22.1 | 19.0 | 19.9 | 22.0 | 14.7 |

| columns | pairs | concordant [M06a: KENDALL_B] | discordant | tied in first column only (T_x) | tied in second column only (T_y) | tied in both | tau-b [M06b: KENDALL_B; digits M06c: team rule] | tau-b exact form | same criterion [M06d: team rule] | of these, pairs at different test pressure (psia, as printed) (conc / disc / T_x / T_y / both) [M06e: team rule] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1g vs martian | 3 | 3 | 0 | 0 | 0 | 0 | 1.000000 | 3 / sqrt(9) | no | 2 / 0 / 0 / 0 / 0 |
| 1g vs lunar | 3 | 2 | 0 | 0 | 1 | 0 | 0.816497 | 2 / sqrt(6) | no | 1 / 0 / 0 / 1 / 0 |
| 1g vs 0g | 3 | 3 | 0 | 0 | 0 | 0 | 1.000000 | 3 / sqrt(9) | no | 2 / 0 / 0 / 0 / 0 |
| martian vs lunar | 3 | 2 | 0 | 0 | 1 | 0 | 0.816497 | 2 / sqrt(6) | yes | 1 / 0 / 0 / 1 / 0 |
| martian vs 0g | 3 | 3 | 0 | 0 | 0 | 0 | 1.000000 | 3 / sqrt(9) | yes | 2 / 0 / 0 / 0 / 0 |
| lunar vs 0g | 3 | 2 | 0 | 1 | 0 | 0 | 0.816497 | 2 / sqrt(6) | yes | 1 / 0 / 1 / 0 / 0 |

1g vs lunar:

| class | a | b | a at 1g | b at 1g | a at lunar | b at lunar | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tied_second_column_only | Ultem 1000 | Nomex HT90-40 | 23.0 | 22.1 | 19.9 | 19.9 | 10.2 | 14.7 |

martian vs lunar:

| class | a | b | a at martian | b at martian | a at lunar | b at lunar | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tied_second_column_only | Ultem 1000 | Nomex HT90-40 | 21.1 | 19.0 | 19.9 | 19.9 | 10.2 | 14.7 |

lunar vs 0g:

| class | a | b | a at lunar | b at lunar | a at 0g | b at 0g | held a | held b |
|---|---|---|---|---|---|---|---|---|
| tied_first_column_only | Ultem 1000 | Nomex HT90-40 | 19.9 | 19.9 | 23.0 | 22.0 | 10.2 | 14.7 |
