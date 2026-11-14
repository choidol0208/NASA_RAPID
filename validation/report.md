# Catalog filter validation report

- Run: 2026-11-14 20:06 · target `scoring.scorer:rank`
- Result: **38/38 scenarios passed**

| ID | Group | Query | Top 3 | Warnings | Result |
|---|---|---|---|---|---|
| R01 | rough_input | ISS | BASS-II, BASS, SAFFIRE-II |  | PASS |
| R02 | rough_input | 우주정거장 (Korean: space station) | BASS-II, BASS, SAFFIRE-II |  | PASS |
| R03 | rough_input | moon | ACME-BRE, FLEX, ACME-CFI-G | partial_gravity | PASS |
| R04 | rough_input | fabric | BASS-II, SAFFIRE-II, BASS |  | PASS |
| R05 | rough_input | smoke | SAME, SAME-R, DAFT |  | PASS |
| R06 | rough_input | (empty) |  | need_input | PASS |
| R07 | rough_input | ISS at 30% O2 and 10.2 psi | ACME-BRE, FLEX, ACME-CFI-G |  | PASS |
| P01 | prevention | ISS cotton fabric | BASS, SAFFIRE-III, BASS-II |  | PASS |
| P02 | prevention | lunar habitat cotton fabric | SAFFIRE-II, SAFFIRE-I, ACME-BRE | partial_gravity | PASS |
| P03 | prevention | 달 기지 면직물 (Korean: lunar base cotton fabric) | SAFFIRE-II, SAFFIRE-I, ACME-BRE | partial_gravity | PASS |
| P04 | prevention | stagnant PMMA | BASS-II, BASS, ACME-BRE |  | PASS |
| P05 | prevention | 달 기지 아크릴 정체 구역 (Korean: lunar base acrylic stagnant zone) | ACME-BRE, BASS-II, SAFFIRE-II | partial_gravity | PASS |
| P06 | prevention | propane 40% oxygen | ACME-CFI-G, ACME-BRE, ACME-FLAME-DESIGN |  | PASS |
| D01 | detection | smoke detector on ISS | SAME, SAME-R, DAFT |  | PASS |
| D02 | detection | wire insulation overheating smoke | SAME, SAME-R, SAME-SIM |  | PASS |
| S01 | suppression | CO2 suppression of heptane fire | FLEX, FLEX-2, CFI |  | PASS |
| S02 | suppression | nitrogen extinguish fabric fire ISS | BASS, BASS-II, ACME-BRE |  | PASS |
| L01 | liquid | liquid fuel leak heptane ISS | FLEX, FLEX-2, CFI |  | PASS |
| F01 | fuel_phase | gas jet flame ISS | ACME-BRE, SLICE, SPICE |  | PASS |
| F02 | fuel_phase | gaseous fuel | ACME-BRE, ACME-CFI-G, ACME-CLD |  | PASS |
| F03 | fuel_phase | droplet | FLEX, CFI, FLEX-2 |  | PASS |
| F04 | fuel_phase | liquid fuel lunar habitat | FLEX, FLEX-2, ACME-BRE | partial_gravity | PASS |
| F05 | fuel_phase | inert gas suppression ISS | BASS, FLEX, BASS-II |  | PASS |
| F06 | fuel_phase | combustion gas detection | SAME, SAME-R, DAFT | not_understood | PASS |
| F07 | rough_input | CO2 30% suppression ISS | FLEX, BASS, BASS-II | not_understood | PASS |
| E01 | equipment | smoke detector for a lunar rover | SAME, SAME-R, FLEX-2 | partial_gravity | PASS |
| E02 | equipment | fire extinguisher for a Mars habitat | BASS, FLEX, BASS-II | partial_gravity, mars_atmosphere | PASS |
| E03 | equipment | crew garment for a Moon base | BASS-II, SAFFIRE-II, ACME-BRE | partial_gravity | PASS |
| E04 | equipment | battery enclosure for the ISS | BASS-II, BASS, SAFFIRE-II | not_understood | PASS |
| E05 | equipment | water mist suppression system for a lunar habitat | FLEX, ACME-BRE, ACME-CFI-G | not_understood, partial_gravity | PASS |
| E06 | equipment | glove box |  | need_input, not_understood | PASS |
| Q01 | sentence | 산소 30% 기압 70 kPa의 달 기지 (Korean: lunar base at 30% oxygen and air pressure 70 kPa) | ACME-BRE, FLEX, ACME-CFI-G | partial_gravity | PASS |
| Q02 | sentence | spacecraft cabin | BASS-II, BASS, SAFFIRE-II |  | PASS |
| Q03 | sentence | a base on a planet whose atmosphere has 30% oxygen | ACME-BRE, FLEX, ACME-CFI-G | partial_gravity | PASS |
| T01 | trap | spacesuit | ACME-BRE, ACME-CFI-G, FLEX | o2_above_all | PASS |
| T02 | trap | Mars base | BASS-II, SAFFIRE-II, BASS | partial_gravity, mars_atmosphere | PASS |
| T03 | trap | hybrid rocket combustion chamber fire |  | out_of_scope | PASS |
| T04 | trap | 로켓 추진제 화재 위험 (Korean: rocket propellant fire hazard) |  | out_of_scope | PASS |

## Weight stability (each weight ±0.05)

| Scenario | Rank 1 | Changes rank 1 |
|---|---|---|
| P01 | BASS | stable |
| P05 | ACME-BRE | stable |
| D01 | SAME | stable |
| S01 | FLEX | stable |
| L01 | FLEX | stable |

## Weight sensitivity (each prevention weight x0.5 and x1.5, rescaled to sum 1; config 1.3.0)

- 45 of 48 variants keep the same top 3 in the same order; 2 keep the same three in another order; rank 1 changes in 1.

| Query | Weight | Factor | Top 3 | Result |
|---|---|---|---|---|
| lunar habitat cotton fabric | o2 | x1.5 | ACME-BRE, SAFFIRE-II, SAFFIRE-I (was SAFFIRE-II, SAFFIRE-I, ACME-BRE) | same set; rank 1 changed |
| lunar habitat cotton fabric | fuel | x0.5 | SAFFIRE-II, ACME-BRE, BASS-II (was SAFFIRE-II, SAFFIRE-I, ACME-BRE) | changed |
| lunar habitat cotton fabric | geometry | x0.5 | SAFFIRE-II, ACME-BRE, SAFFIRE-I (was SAFFIRE-II, SAFFIRE-I, ACME-BRE) | same set |

## Sensitivity to the other values (each x0.5 and x1.5 on the four demo queries; config 1.3.0)

- 127 of 136 runs keep the same top 3 in the same order; 3 keep the same three in another order; rank 1 changes in 4.

| Value | Same top 3 (of 8) | Changes |
|---|---|---|
| O2 decay above the tested maximum (`similarity.o2.above_scale_ln`) | 5 | x0.5 ISS cotton fabric: BASS, SAFFIRE-III, SAFFIRE-II; x0.5 lunar habitat cotton fabric: ACME-BRE, SAFFIRE-II, FLEX (rank 1); x1.5 ISS cotton fabric: BASS, BASS-II, SAFFIRE-III |
| O2 decay below the tested minimum (`similarity.o2.below_scale_ln`) | 6 | x0.5 ISS: BASS-II, BASS, SAFFIRE-III; x0.5 ISS cotton fabric: BASS, BASS-II, SAFFIRE-III |
| pressure width (log) (`similarity.pressure.sigma_ln`) | 8 | — |
| flow-speed width (log) (`similarity.flow_speed.sigma_ln`) | 8 | — |
| flow-speed offset (`similarity.flow_speed.offset_cms`) | 8 | — |
| value for 'not recorded' (`similarity.unknown_value`) | 8 | — |
| gate threshold (`gate.min_similarity`) | 7 | x1.5 lunar habitat cotton fabric: ACME-BRE, SAFFIRE-II, BASS-II (rank 1) |
| gate floor (`gate.factor`) | 8 | — |
| evidence factor span (base = 1 - span) (`evidence.span`) | 8 | — |
| tie margin (`selection.tie_points`) | 7 | x0.5 ISS: BASS-II, BASS, SAFFIRE-III |
| complementary slot minimum score (`complementary_slot.min_score_ratio`) | 8 | — |
| diluent heat-capacity exponent (`similarity.diluent.cp_ratio_exponent`) | 8 | — |
| flow configuration matrix (off-diagonal) (`similarity.flow_config_matrix`) | 8 | — |
| fuel similarity table (`similarity.fuel`) | 6 | x1.5 ISS cotton fabric: BASS-II, BASS, SAFFIRE-III (rank 1); x1.5 lunar habitat cotton fabric: BASS-II, SAFFIRE-II, ACME-BRE (rank 1) |
| sample-shape table (`similarity.geometry`) | 8 | — |
| research-purpose table (`similarity.role`) | 8 | — |
| data-availability table (`evidence.data_availability`) | 8 | — |

## Weighting by purpose (config 1.3.0)

| Profile | Queries read as this purpose | One-at-a-time x0.5/x1.5: same top 3 | rank 1 changes | Scheme | Same top 3 | Same rank 1 |
|---|---|---|---|---|---|---|
| prevention | 4 of 4 | 45 of 48 | 1 | equal weights | 3 of 4 | 4 of 4 |
| | | | | rank-order centroid | 3 of 4 | 3 of 4 |
| | | | | detection weights | 3 of 4 | 4 of 4 |
| | | | | suppression weights | 4 of 4 | 4 of 4 |
| detection | 4 of 4 | 48 of 48 | 0 | equal weights | 3 of 4 | 3 of 4 |
| | | | | rank-order centroid | 4 of 4 | 4 of 4 |
| | | | | prevention weights | 2 of 4 | 3 of 4 |
| | | | | suppression weights | 3 of 4 | 3 of 4 |
| suppression | 4 of 4 | 54 of 56 | 0 | equal weights | 1 of 4 | 4 of 4 |
| | | | | rank-order centroid | 4 of 4 | 4 of 4 |
| | | | | prevention weights | 1 of 4 | 3 of 4 |
| | | | | detection weights | 4 of 4 | 4 of 4 |

Rows where another scheme changes the top 3:

- prevention, equal weights, "lunar habitat cotton fabric": SAFFIRE-II, BASS-II, ACME-BRE (configured: SAFFIRE-II, SAFFIRE-I, ACME-BRE)
- prevention, rank-order centroid, "lunar habitat cotton fabric": ACME-BRE, SAFFIRE-II, SAFFIRE-I (configured: SAFFIRE-II, SAFFIRE-I, ACME-BRE)
- prevention, detection weights, "lunar habitat": ACME-BRE, FLEX, BASS-II (configured: ACME-BRE, FLEX, ACME-CFI-G)
- detection, equal weights, "smoke detector for a lunar rover": ACME-FLAME-DESIGN, FLEX-2, SAME (configured: SAME, SAME-R, FLEX-2)
- detection, prevention weights, "smoke detector on ISS": SAME, SAME-R, BASS-II (configured: SAME, SAME-R, DAFT)
- detection, prevention weights, "smoke detector for a lunar rover": ACME-FLAME-DESIGN, FLEX-2, ACME-BRE (configured: SAME, SAME-R, FLEX-2)
- detection, suppression weights, "smoke detector for a lunar rover": ACME-FLAME-DESIGN, FLEX-2, SAME (configured: SAME, SAME-R, FLEX-2)
- suppression, equal weights, "nitrogen extinguish fabric fire ISS": BASS, BASS-II, SAFFIRE-III (configured: BASS, BASS-II, ACME-BRE)
- suppression, equal weights, "fire extinguisher for a Mars habitat": BASS, BASS-II, FLEX (configured: BASS, FLEX, BASS-II)
- suppression, equal weights, "inert gas suppression ISS": BASS, BASS-II, FLEX (configured: BASS, FLEX, BASS-II)
- suppression, prevention weights, "nitrogen extinguish fabric fire ISS": BASS-II, BASS, SAFFIRE-III (configured: BASS, BASS-II, ACME-BRE)
- suppression, prevention weights, "fire extinguisher for a Mars habitat": BASS, BASS-II, SAFFIRE-II (configured: BASS, FLEX, BASS-II)
- suppression, prevention weights, "inert gas suppression ISS": BASS, BASS-II, SAME (configured: BASS, FLEX, BASS-II)

## Weight uncertainty: SMAA with the order of importance only (config 1.3.0, 300 draws per profile, seed 20261114)

| Profile | Query | Top 3 with the profile's weights | Same rank 1 | Same top 3 (as a set) | Top-3 acceptability of each investigation (10% or more) |
|---|---|---|---|---|---|
| prevention | ISS | BASS-II, BASS, SAFFIRE-II | 100% | 63% | BASS-II 100%, BASS 99%, SAFFIRE-II 63%, SAME 37% |
| prevention | lunar habitat | ACME-BRE, FLEX, ACME-CFI-G | 100% | 100% | ACME-BRE 100%, FLEX 100%, ACME-CFI-G 100% |
| prevention | ISS cotton fabric | BASS, SAFFIRE-III, BASS-II | 100% | 100% | BASS 100%, SAFFIRE-III 100%, BASS-II 100% |
| prevention | lunar habitat cotton fabric | SAFFIRE-II, SAFFIRE-I, ACME-BRE | 46% | 70% | ACME-BRE 100%, SAFFIRE-II 91%, SAFFIRE-I 70%, BASS-II 16%, FLEX 14% |
| detection | smoke detector on ISS | SAME, SAME-R, DAFT | 100% | 91% | SAME 100%, SAME-R 100%, DAFT 91% |
| detection | wire insulation overheating smoke | SAME, SAME-R, SAME-SIM | 100% | 100% | SAME 100%, SAME-R 100%, SAME-SIM 100% |
| detection | smoke detector for a lunar rover | SAME, SAME-R, FLEX-2 | 100% | 82% | SAME 100%, SAME-R 100%, FLEX-2 82%, ACME-FLAME-DESIGN 18% |
| detection | kapton teflon smoke | SAME, SAME-R, SAME-SIM | 100% | 100% | SAME 100%, SAME-R 100%, SAME-SIM 100% |
| suppression | CO2 suppression of heptane fire | FLEX, FLEX-2, CFI | 100% | 99% | FLEX 100%, CFI 100%, FLEX-2 99% |
| suppression | nitrogen extinguish fabric fire ISS | BASS, BASS-II, ACME-BRE | 100% | 100% | BASS 100%, BASS-II 100%, ACME-BRE 100% |
| suppression | fire extinguisher for a Mars habitat | BASS, FLEX, BASS-II | 91% | 100% | BASS 100%, FLEX 100%, BASS-II 100% |
| suppression | inert gas suppression ISS | BASS, FLEX, BASS-II | 79% | 100% | BASS 100%, FLEX 100%, BASS-II 100% |
