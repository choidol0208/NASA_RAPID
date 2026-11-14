# Review of the scoring values other than the weights

*AI-generated (Claude Code, catalog role), 2026-11-14 17:01 KST, config 1.1.0.*

**This is an AI review, not a human review and not a combustion specialist's review.** It explains each value, says what it rests on, and measures how much the demo rankings depend on it.
- **Approved 2026-11-14 17:03 KST:** a team member read this review and approved all values as they are, findings 1 and 2 included, with no change. The approval is recorded in `scoring/scoring_config.json` `_about`; the weights were approved at 16:51.
- No combustion specialist review is planned during the hackathon: the human lead decided at 17:04 KST that the team has no specialist to ask. The questions at the end stay open, as limitations and as the next validation step.

Sensitivity is measured by `python3 validation/sensitivity.py` and reported in `validation/report.md`:
- Each value or table is scaled by 0.5 and by 1.5. Similarities are capped at 1, and full matches (1.0) are left alone.
- Each variant is run on four demo queries: `ISS`, `lunar habitat`, `ISS cotton fabric` and `lunar habitat cotton fabric`.

## Result in one paragraph

- Of 136 runs, 129 keep the same top 3 in the same order, 3 keep the same three in another order, and rank 1 changes in 3.
- **The two preset queries the page shows (`ISS`, `lunar habitat`) do not change under any value.**
- All changes come from the two cotton-fabric queries, and from two values:
  - how steeply oxygen above a test's maximum is penalised;
  - the fuel similarity table.
- Both decide the same trade-off: a test of the same material at lower oxygen, against a test of another fuel at the user's oxygen. That trade-off is the one point a specialist should settle.

## Values

| Value (config key) | What it does | What it rests on | Demo runs unchanged (of 8) | AI assessment |
|---|---|---|---|---|
| O2 decay above the tested maximum (`similarity.o2.above_scale_ln` = ln 26/21) | How fast similarity falls when the user's O2 is above a test's maximum | Direction and ratio form: Turns 2012, ch. 9 and 10 (`MODEL_BASIS.md`). Size: team choice, set equal to 5 points near air | 5 | **Sensitive.** At x0.5, lunar habitat cotton fabric puts the gas burner ACME-BRE first. Keep, and ask a specialist. |
| O2 decay below the tested minimum (`below_scale_ln` = ln 21/11) | The same below a test's minimum, gentler (a test at more oxygen than the user's is conservative) | As above; size equal to 10 points near air | 7 | Keep. |
| Pressure width (`similarity.pressure.sigma_ln` = ln 2) | A factor of 2 in pressure gives similarity 0.61 | Log form: power laws of pressure (Turns, ch. 8). Size: team | 8 | Keep. |
| Flow-speed width and offset (`flow_speed.sigma_ln` = ln 2, `offset_cms` = 1) | Distance between flow speeds; the offset allows 0 cm/s | Sub-linear effect of flow: Turns, ch. 10 (droplets). Size: team | 8 (the demo queries give no speed) | Keep; untested by the demo. |
| Not recorded (`similarity.unknown_value` = 0.5) | Similarity when the catalog has no value; for O2 and fuel it is capped at the best recorded match | Team convention: neither a match nor a miss | 8 | Keep. |
| Gate (`gate.min_similarity` = 0.2, `gate.factor` = 0.5) | Below 0.2 on fuel or O2, the score is cut, by up to half | Separate combustion modes (Turns, ch. 8–10, 14). Sizes: team | threshold 7, floor 8 | Keep. |
| Evidence factor (`evidence.base` 0.7, `span` 0.3, data-availability table) | Up to 30% for data quality: raw table, long microgravity | Team choice; data quality, not physics | 8 | Keep. Human checks do not change it (pm decision 14:15). |
| Tie margin (`selection.tie_points` = 3) | Within 3 points, the stronger evidence goes first | Team choice | 8 | Keep. At low scores 3 points is a large share; this is a known limit. |
| Complementary slot (`complementary_slot.min_score_ratio` = 0.4) | If no top result was tested at the user's O2, the third place goes to one that was | Product rule | 8 | Keep. |
| Flow configuration matrix (`similarity.flow_config_matrix`) | Quiescent, opposed, concurrent and other flows compared | Quiescent against forced is supported (Turns, ch. 10). Opposed against concurrent for solids is not covered by the textbook | 8 | Keep. The solid-flow values need a specialist. |
| Fuel table (`similarity.fuel`: same class 0.7, same phase 0.5, solid surrogate 0.5, liquid–gas 0.3, other 0.1) | How close two fuels are | Phase gate supported; the values are the team's | 6 | **Sensitive.** At x1.5, both cotton-fabric queries change rank 1 to BASS-II. Keep, and ask a specialist. |
| Sample-shape table (`similarity.geometry`) | Thin against thick, sheet against rod | Not covered by the textbook | 8 | Keep; ask a specialist. |
| Research-purpose table (`similarity.role`) | Prevention, detection, suppression or fundamental | Team classification of the PSI records | 8 | Keep. |
| Diluent exponent (`diluent.cp_ratio_exponent` = 2) | Inert gases compared by heat capacity | Thermal action of inerts (Turns, ch. 8); exponent: team | 8 (no diluent in the demo) | Keep; untested by the demo. |
| Not varied: confidence thresholds (0.75, 0.45), `outside_range_threshold` (0.9), atmosphere fallback (21% O2, 101.3 kPa), `top_k` (3) | Labels and warnings only, or decisions rather than scales | Fallback: pm decision 11/14 11:10 | — | See finding 2 for the fallback. |

## Findings for a decision

1. **The material-against-atmosphere trade-off.** This is the only thing that moves rank 1 in the demo (above).
   - In `lunar habitat cotton fabric` the cotton tests (SAFFIRE-II, SAFFIRE-I) were run at about 22% oxygen, and the burner that ran at 30 to 40% (ACME-BRE) burns a gas, not cotton.
   - The current values put the cotton tests first and attach `o2_above_result` and `outside_range`.
   - This is a judgement, and the page already shows both kinds of evidence. No change proposed before the freeze.
2. **An assumed atmosphere can outscore a recorded one.** In `ISS cotton fabric`, ranks 1 and 2 (BASS-C01, SAFFIRE-III-C01) have no O2 in their records, so they are scored at the assumed 21% (similarity 1.0). Rank 3, BASS-II-C04, records 16.4 to 20.8% (similarity 0.96).
   - The page labels ranks 1 and 2 `fallback` with medium confidence, and rank 3 high confidence.
   - A possible change: cap the similarity of an assumed value at the best recorded match, as for unknown values. That would move BASS-II-C04 up in this query.
   - It changes a demo query, so it needs the human lead's decision. Without it, it stays as is and the confidence labels carry the difference.

## Open questions (limitations; for a combustion specialist after the hackathon)

No specialist review is planned now (human lead, 17:04). These are the points the rules rest on without a specialist's answer. They can be sent to one as they are.

1. If a material was tested at 22% oxygen and a crew uses 30%, is it right to rank a test of that material above a test of another fuel at 30%? How steeply should evidence lose value above the tested oxygen?
2. In microgravity, how close is opposed-flow spread over a thin fabric to concurrent-flow spread, and how close is quiescent burning to either? The team uses 0.6 between opposed and concurrent, and 0.3 to 0.5 with quiescent.
3. Is a porous gas burner that emulates a burning solid (ACME-BRE) a fair surrogate for a solid material? The team scores it at 0.5 of a same-material match.
4. Is a thin sheet of a material much closer to a thin sheet of another material than to a thick slab of the same material? The team scores the same shape at another thickness at 0.6, and another shape of the same thickness at 0.7.
5. Across 56 to 101 kPa, does a symmetric rule, where a factor of 2 in pressure gives 0.61, make sense for solid flammability?
6. For extinguishment by inert dilution, is molar heat capacity the right way to compare CO2, N2 and He? Should helium's high diffusivity count separately?
7. Where the record gives no atmosphere for an ISS-cabin or Cygnus experiment, is assuming 21% O2 and 101.3 kPa acceptable? Should such a value rank below a recorded near value (finding 2)?
8. Are the prevention weights a reasonable starting point: O2 0.25, fuel 0.25, flow 0.20, and pressure, sample shape and research purpose 0.10 each?
