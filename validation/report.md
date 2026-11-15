# Catalog filter validation report

- Run: 2026-11-15 10:07 · target `scoring.scorer:rank`
- Result: **43/43 scenarios passed**

| ID | Group | Query | Top 3 | Warnings | Result |
|---|---|---|---|---|---|
| R01 | rough_input | ISS | BASS-II, SAFFIRE-I, SAFFIRE-II |  | PASS |
| R02 | rough_input | 우주정거장 (Korean: space station) | BASS-II, SAFFIRE-I, SAFFIRE-II |  | PASS |
| R03 | rough_input | moon | FLEX, ACME-CFI-G, ACME-BRE | partial_gravity | PASS |
| R04 | rough_input | fabric | BASS, BASS-II, SAFFIRE-I |  | PASS |
| R05 | rough_input | smoke | SAME, SAME-R, SAME-SIM |  | PASS |
| R06 | rough_input | (empty) |  | need_input | PASS |
| R07 | rough_input | ISS at 30% O2 and 10.2 psi | FLEX, ACME-CFI-G, ACME-BRE |  | PASS |
| P01 | prevention | ISS cotton fabric | BASS-II, SAFFIRE-I, SAFFIRE-II |  | PASS |
| P02 | prevention | lunar habitat cotton fabric | SAFFIRE-II, SAFFIRE-I, ACME-BRE | partial_gravity | PASS |
| P03 | prevention | 달 기지 면직물 (Korean: lunar base cotton fabric) | SAFFIRE-II, SAFFIRE-I, ACME-BRE | partial_gravity | PASS |
| P04 | prevention | stagnant PMMA | BASS-II, ACME-BRE, BASS-FGM-MODEL |  | PASS |
| P05 | prevention | 달 기지 아크릴 정체 구역 (Korean: lunar base acrylic stagnant zone) | ACME-BRE, BASS-II, FLEX | partial_gravity | PASS |
| P06 | prevention | propane 40% oxygen | ACME-CFI-G, ACME-FLAME-DESIGN, ACME-BRE |  | PASS |
| D01 | detection | smoke detector on ISS | SAME, SAME-R, SAME-SIM |  | PASS |
| D02 | detection | wire insulation overheating smoke | SAME, SAME-R, SAME-SIM |  | PASS |
| D03 | detection | CO detection on ISS | BASS-II, SAFFIRE-I, SAFFIRE-II |  | PASS |
| D04 | detection | toxic gas and smoke detection in a spacecraft | BASS-II, SAME, SAME-R |  | PASS |
| S01 | suppression | CO2 suppression of heptane fire | FLEX, FLEX-2, CFI |  | PASS |
| S02 | suppression | nitrogen extinguish fabric fire ISS | BASS, BASS-II, ACME-BRE |  | PASS |
| L01 | liquid | liquid fuel leak heptane ISS | FLEX, FLEX-2, CFI |  | PASS |
| F01 | fuel_phase | gas jet flame ISS | ACME-CFI-G, ACME-BRE, ACME-FLAME-DESIGN |  | PASS |
| F02 | fuel_phase | gaseous fuel | ACME-CFI-G, ACME-BRE, ACME-FLAME-DESIGN |  | PASS |
| F03 | fuel_phase | droplet | FLEX, CFI, FLEX-2 |  | PASS |
| F04 | fuel_phase | liquid fuel lunar habitat | FLEX, FLEX-2, ACME-CFI-G | partial_gravity | PASS |
| F05 | fuel_phase | inert gas suppression ISS | BASS, FLEX, BASS-II |  | PASS |
| F06 | fuel_phase | combustion gas detection | BASS-II, DAFT, SAFFIRE-I |  | PASS |
| F09 | fuel_phase | lunar habitat solid | ACME-BRE, BASS-II, SAFFIRE-II | partial_gravity | PASS |
| F10 | fuel_phase | 고체 연료 화재 | BASS, BASS-II, SAFFIRE-I |  | PASS |
| F08 | fuel_phase | CO2 detection | BASS-II, DAFT, SAFFIRE-I |  | PASS |
| F07 | rough_input | CO2 30% suppression ISS | FLEX, BASS, BASS-II | not_understood | PASS |
| E01 | equipment | smoke detector for a lunar rover | SAME, SAME-R, FLEX-2 | partial_gravity | PASS |
| E02 | equipment | fire extinguisher for a Mars habitat | BASS, FLEX, BASS-II | partial_gravity, mars_atmosphere | PASS |
| E03 | equipment | crew garment for a Moon base | BASS-II, SAFFIRE-II, ACME-BRE | partial_gravity | PASS |
| E04 | equipment | battery enclosure for the ISS | BASS-II, SAFFIRE-I, SAFFIRE-II | not_understood | PASS |
| E05 | equipment | water mist suppression system for a lunar habitat | FLEX, ACME-CFI-G, ACME-FLAME-DESIGN | not_understood, partial_gravity | PASS |
| E06 | equipment | glove box |  | need_input, not_understood | PASS |
| Q01 | sentence | 산소 30% 기압 70 kPa의 달 기지 (Korean: lunar base at 30% oxygen and air pressure 70 kPa) | FLEX, ACME-CFI-G, ACME-BRE | partial_gravity | PASS |
| Q02 | sentence | spacecraft cabin | BASS-II, SAFFIRE-I, SAFFIRE-II |  | PASS |
| Q03 | sentence | a base on a planet whose atmosphere has 30% oxygen | ACME-CFI-G, FLEX, ACME-BRE | partial_gravity | PASS |
| T01 | trap | spacesuit | ACME-BRE, ACME-CFI-G, FLEX | o2_above_all | PASS |
| T02 | trap | Mars base | BASS, BASS-II, SAFFIRE-I | partial_gravity, mars_atmosphere | PASS |
| T03 | trap | hybrid rocket combustion chamber fire |  | out_of_scope | PASS |
| T04 | trap | 로켓 추진제 화재 위험 (Korean: rocket propellant fire hazard) |  | out_of_scope | PASS |

## Weight stability (each weight ±0.05)

| Scenario | Rank 1 | Changes rank 1 |
|---|---|---|
| P01 | BASS-II | stable |
| P05 | ACME-BRE | stable |
| D01 | SAME | stable |
| S01 | FLEX | stable |
| L01 | FLEX | stable |

## Weight sensitivity (each prevention weight x0.5 and x1.5, rescaled to sum 1; config 1.5.1)

- 44 of 48 variants keep the same top 3 in the same order; 1 keep the same three in another order; rank 1 changes in 3.

| Query | Weight | Factor | Top 3 | Result |
|---|---|---|---|---|
| lunar habitat | o2 | x0.5 | BASS-II, SAFFIRE-II, FLEX (was FLEX, ACME-CFI-G, ACME-BRE) | changed; rank 1 changed |
| lunar habitat | flow | x1.5 | FLEX, BASS-II, ACME-BRE (was FLEX, ACME-CFI-G, ACME-BRE) | changed |
| lunar habitat cotton fabric | o2 | x1.5 | ACME-BRE, SAFFIRE-II, SAFFIRE-I (was SAFFIRE-II, SAFFIRE-I, ACME-BRE) | same set; rank 1 changed |
| lunar habitat cotton fabric | fuel | x0.5 | BASS-II, SAFFIRE-II, ACME-BRE (was SAFFIRE-II, SAFFIRE-I, ACME-BRE) | changed; rank 1 changed |

## Sensitivity to the other values (each x0.5 and x1.5 on the four demo queries; config 1.5.1)

- 124 of 136 runs keep the same top 3 in the same order; 3 keep the same three in another order; rank 1 changes in 5.

| Value | Same top 3 (of 8) | Changes |
|---|---|---|
| O2 decay above the tested maximum (`similarity.o2.above_scale_ln`) | 6 | x0.5 lunar habitat cotton fabric: ACME-BRE, BASS-II, SAFFIRE-II (rank 1); x1.5 lunar habitat cotton fabric: BASS-II, SAFFIRE-II, ACME-BRE (rank 1) |
| O2 decay below the tested minimum (`similarity.o2.below_scale_ln`) | 7 | x0.5 ISS cotton fabric: BASS-II, SAFFIRE-I, BASS |
| pressure width (log) (`similarity.pressure.sigma_ln`) | 8 | — |
| flow-speed width (log) (`similarity.flow_speed.sigma_ln`) | 8 | — |
| flow-speed offset (`similarity.flow_speed.offset_cms`) | 8 | — |
| value for 'not recorded' (`similarity.unknown_value`) | 8 | — |
| gate threshold (`gate.min_similarity`) | 6 | x0.5 lunar habitat cotton fabric: BASS-II, SAFFIRE-II, ACME-BRE (rank 1); x1.5 lunar habitat cotton fabric: SAFFIRE-II, BASS-II, ACME-BRE |
| gate floor (`gate.factor`) | 7 | x1.5 lunar habitat cotton fabric: SAFFIRE-II, BASS-II, ACME-BRE |
| evidence factor span (base = 1 - span) (`evidence.span`) | 8 | — |
| tie margin (`selection.tie_points`) | 5 | x0.5 lunar habitat: FLEX, ACME-BRE, ACME-CFI-G; x0.5 ISS cotton fabric: BASS-II, SAFFIRE-I, BASS; x1.5 lunar habitat cotton fabric: SAFFIRE-II, BASS-II, ACME-BRE |
| complementary slot minimum score (`complementary_slot.min_score_ratio`) | 8 | — |
| diluent heat-capacity exponent (`similarity.diluent.cp_ratio_exponent`) | 8 | — |
| flow configuration matrix (off-diagonal) (`similarity.flow_config_matrix`) | 7 | x1.5 lunar habitat: FLEX, ACME-BRE, ACME-CFI-G |
| fuel similarity table (`similarity.fuel`) | 7 | x1.5 lunar habitat cotton fabric: BASS-II, SAFFIRE-II, ACME-BRE (rank 1) |
| sample-shape table (`similarity.geometry`) | 8 | — |
| research-purpose table (`similarity.role`) | 8 | — |
| data-availability table (`evidence.data_availability`) | 7 | x1.5 lunar habitat: ACME-BRE, FLEX, ACME-CFI-G (rank 1) |

## Weighting by purpose (config 1.5.1)

| Profile | Queries read as this purpose | One-at-a-time x0.5/x1.5: same top 3 | rank 1 changes | Scheme | Same top 3 | Same rank 1 |
|---|---|---|---|---|---|---|
| prevention | 4 of 4 | 44 of 48 | 3 | equal weights | 3 of 4 | 4 of 4 |
| | | | | rank-order centroid | 3 of 4 | 3 of 4 |
| | | | | detection weights | 3 of 4 | 3 of 4 |
| | | | | suppression weights | 3 of 4 | 3 of 4 |
| detection | 4 of 4 | 48 of 48 | 0 | equal weights | 2 of 4 | 3 of 4 |
| | | | | rank-order centroid | 4 of 4 | 4 of 4 |
| | | | | prevention weights | 2 of 4 | 3 of 4 |
| | | | | suppression weights | 3 of 4 | 3 of 4 |
| suppression | 4 of 4 | 54 of 56 | 0 | equal weights | 2 of 4 | 4 of 4 |
| | | | | rank-order centroid | 4 of 4 | 4 of 4 |
| | | | | prevention weights | 1 of 4 | 3 of 4 |
| | | | | detection weights | 3 of 4 | 4 of 4 |

Rows where another scheme changes the top 3:

- prevention, equal weights, "lunar habitat cotton fabric": SAFFIRE-II, BASS-II, ACME-BRE (configured: SAFFIRE-II, SAFFIRE-I, ACME-BRE)
- prevention, rank-order centroid, "lunar habitat cotton fabric": ACME-BRE, SAFFIRE-II, BASS-II (configured: SAFFIRE-II, SAFFIRE-I, ACME-BRE)
- prevention, detection weights, "lunar habitat": BASS-II, SAFFIRE-II, FLEX (configured: FLEX, ACME-CFI-G, ACME-BRE)
- prevention, suppression weights, "lunar habitat cotton fabric": ACME-BRE, SAFFIRE-II, SAFFIRE-I (configured: SAFFIRE-II, SAFFIRE-I, ACME-BRE)
- detection, equal weights, "smoke detector on ISS": SAME, SAME-R, BASS-II (configured: SAME, SAME-R, SAME-SIM)
- detection, equal weights, "smoke detector for a lunar rover": ACME-FLAME-DESIGN, FLEX-2, SAME (configured: SAME, SAME-R, FLEX-2)
- detection, prevention weights, "smoke detector on ISS": SAME, SAME-R, BASS-II (configured: SAME, SAME-R, SAME-SIM)
- detection, prevention weights, "smoke detector for a lunar rover": FLEX-2, ACME-FLAME-DESIGN, FLEX (configured: SAME, SAME-R, FLEX-2)
- detection, suppression weights, "smoke detector for a lunar rover": ACME-FLAME-DESIGN, FLEX-2, ACME-CFI-G (configured: SAME, SAME-R, FLEX-2)
- suppression, equal weights, "fire extinguisher for a Mars habitat": BASS, BASS-II, FLEX (configured: BASS, FLEX, BASS-II)
- suppression, equal weights, "inert gas suppression ISS": BASS, BASS-II, FLEX (configured: BASS, FLEX, BASS-II)
- suppression, prevention weights, "nitrogen extinguish fabric fire ISS": BASS-II, BASS, SAFFIRE-I (configured: BASS, BASS-II, ACME-BRE)
- suppression, prevention weights, "fire extinguisher for a Mars habitat": BASS, BASS-II, SAFFIRE-I (configured: BASS, FLEX, BASS-II)
- suppression, prevention weights, "inert gas suppression ISS": BASS, BASS-II, SAFFIRE-I (configured: BASS, FLEX, BASS-II)
- suppression, detection weights, "nitrogen extinguish fabric fire ISS": BASS, BASS-II, SAFFIRE-I (configured: BASS, BASS-II, ACME-BRE)

## Weight uncertainty: SMAA with the order of importance only (config 1.5.1, 300 draws per profile, seed 20261114)

| Profile | Query | Top 3 with the profile's weights | Same rank 1 | Same top 3 (as a set) | Top-3 acceptability of each investigation (10% or more) |
|---|---|---|---|---|---|
| prevention | ISS | BASS-II, SAFFIRE-I, SAFFIRE-II | 100% | 100% | BASS-II 100%, SAFFIRE-I 100%, SAFFIRE-II 100% |
| prevention | lunar habitat | FLEX, ACME-CFI-G, ACME-BRE | 100% | 77% | FLEX 100%, ACME-CFI-G 100%, ACME-BRE 77%, ACME-FLAME-DESIGN 23% |
| prevention | ISS cotton fabric | BASS-II, SAFFIRE-I, SAFFIRE-II | 95% | 61% | BASS-II 100%, SAFFIRE-I 100%, SAFFIRE-II 61%, BASS 39% |
| prevention | lunar habitat cotton fabric | SAFFIRE-II, SAFFIRE-I, ACME-BRE | 25% | 47% | ACME-BRE 100%, SAFFIRE-II 89%, SAFFIRE-I 47%, BASS-II 44%, FLEX 12% |
| detection | smoke detector on ISS | SAME, SAME-R, SAME-SIM | 100% | 90% | SAME 100%, SAME-R 100%, SAME-SIM 90% |
| detection | wire insulation overheating smoke | SAME, SAME-R, SAME-SIM | 100% | 100% | SAME 100%, SAME-R 100%, SAME-SIM 100% |
| detection | smoke detector for a lunar rover | SAME, SAME-R, FLEX-2 | 94% | 74% | SAME 100%, SAME-R 99%, FLEX-2 76%, ACME-FLAME-DESIGN 26% |
| detection | kapton teflon smoke | SAME, SAME-R, SAME-SIM | 100% | 100% | SAME 100%, SAME-R 100%, SAME-SIM 100% |
| suppression | CO2 suppression of heptane fire | FLEX, FLEX-2, CFI | 100% | 98% | FLEX 100%, FLEX-2 100%, CFI 98% |
| suppression | nitrogen extinguish fabric fire ISS | BASS, BASS-II, ACME-BRE | 93% | 97% | BASS 100%, BASS-II 100%, ACME-BRE 97% |
| suppression | fire extinguisher for a Mars habitat | BASS, FLEX, BASS-II | 100% | 100% | BASS 100%, FLEX 100%, BASS-II 100% |
| suppression | inert gas suppression ISS | BASS, FLEX, BASS-II | 80% | 100% | FLEX 100%, BASS-II 100%, BASS 100% |
