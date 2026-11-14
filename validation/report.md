# Catalog filter validation report

- Run: 2026-11-14 17:15 · target `scoring.scorer:rank`
- Result: **35/35 scenarios passed**

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
| P04 | prevention | stagnant PMMA | BASS-II, ACME-BRE, BASS |  | PASS |
| P05 | prevention | 달 기지 아크릴 정체 구역 (Korean: lunar base acrylic stagnant zone) | ACME-BRE, BASS-II, FLEX | partial_gravity | PASS |
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
| E05 | equipment | water mist suppression system for a lunar habitat | FLEX, ACME-BRE, BASS | not_understood, partial_gravity | PASS |
| E06 | equipment | glove box |  | need_input, not_understood | PASS |
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

## Weight sensitivity (each prevention weight x0.5 and x1.5, rescaled to sum 1; config 1.1.0)

- 45 of 48 variants keep the same top 3 in the same order; 1 keep the same three in another order; rank 1 changes in 0.

| Query | Weight | Factor | Top 3 | Result |
|---|---|---|---|---|
| lunar habitat | o2 | x0.5 | ACME-BRE, FLEX, BASS-II (was ACME-BRE, FLEX, ACME-CFI-G) | changed |
| lunar habitat cotton fabric | o2 | x1.5 | SAFFIRE-II, ACME-BRE, SAFFIRE-I (was SAFFIRE-II, SAFFIRE-I, ACME-BRE) | same set |
| lunar habitat cotton fabric | fuel | x0.5 | SAFFIRE-II, BASS-II, ACME-BRE (was SAFFIRE-II, SAFFIRE-I, ACME-BRE) | changed |

## Sensitivity to the other values (each x0.5 and x1.5 on the four demo queries; config 1.1.0)

- 129 of 136 runs keep the same top 3 in the same order; 3 keep the same three in another order; rank 1 changes in 3.

| Value | Same top 3 (of 8) | Changes |
|---|---|---|
| O2 decay above the tested maximum (`similarity.o2.above_scale_ln`) | 5 | x0.5 ISS cotton fabric: BASS, SAFFIRE-III, SAFFIRE-II; x0.5 lunar habitat cotton fabric: ACME-BRE, SAFFIRE-II, BASS-II (rank 1); x1.5 ISS cotton fabric: BASS, BASS-II, SAFFIRE-III |
| O2 decay below the tested minimum (`similarity.o2.below_scale_ln`) | 7 | x0.5 ISS cotton fabric: BASS, BASS-II, SAFFIRE-III |
| pressure width (log) (`similarity.pressure.sigma_ln`) | 8 | — |
| flow-speed width (log) (`similarity.flow_speed.sigma_ln`) | 8 | — |
| flow-speed offset (`similarity.flow_speed.offset_cms`) | 8 | — |
| value for 'not recorded' (`similarity.unknown_value`) | 8 | — |
| gate threshold (`gate.min_similarity`) | 7 | x1.5 lunar habitat cotton fabric: SAFFIRE-II, ACME-BRE, BASS-II |
| gate floor (`gate.factor`) | 8 | — |
| evidence factor span (base = 1 - span) (`evidence.span`) | 8 | — |
| tie margin (`selection.tie_points`) | 8 | — |
| complementary slot minimum score (`complementary_slot.min_score_ratio`) | 8 | — |
| diluent heat-capacity exponent (`similarity.diluent.cp_ratio_exponent`) | 8 | — |
| flow configuration matrix (off-diagonal) (`similarity.flow_config_matrix`) | 8 | — |
| fuel similarity table (`similarity.fuel`) | 6 | x1.5 ISS cotton fabric: BASS-II, BASS, SAFFIRE-III (rank 1); x1.5 lunar habitat cotton fabric: BASS-II, SAFFIRE-II, ACME-BRE (rank 1) |
| sample-shape table (`similarity.geometry`) | 8 | — |
| research-purpose table (`similarity.role`) | 8 | — |
| data-availability table (`evidence.data_availability`) | 8 | — |
