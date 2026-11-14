# Catalog filter validation report

- Run: 2026-11-14 10:52 · target `scoring.scorer:rank`
- Result: **22/22 scenarios passed**

| ID | Group | Query | Top 3 | Warnings | Result |
|---|---|---|---|---|---|
| R01 | rough_input | ISS | BASS-II, BASS, SAFFIRE-II |  | PASS |
| R02 | rough_input | 우주정거장 | BASS-II, BASS, SAFFIRE-II |  | PASS |
| R03 | rough_input | moon | ACME-BRE, FLEX, ACME-CFI-G | partial_gravity | PASS |
| R04 | rough_input | fabric | BASS-II, SAFFIRE-II, BASS |  | PASS |
| R05 | rough_input | smoke | SAME, SAME-R, DAFT |  | PASS |
| R06 | rough_input | (empty) |  | need_input | PASS |
| R07 | rough_input | ISS at 30% O2 and 10.2 psi | ACME-BRE, FLEX, ACME-CFI-G |  | PASS |
| P01 | prevention | ISS cotton fabric | BASS, BASS-II, SAFFIRE-III |  | PASS |
| P02 | prevention | lunar habitat cotton fabric | SAFFIRE-II, BASS-II, ACME-BRE | partial_gravity | PASS |
| P03 | prevention | 달 기지 면직물 | SAFFIRE-II, BASS-II, ACME-BRE | partial_gravity | PASS |
| P04 | prevention | stagnant PMMA | BASS-II, ACME-BRE, BASS-FGM-MODEL |  | PASS |
| P05 | prevention | 달 기지 아크릴 정체 구역 | ACME-BRE, BASS-II, FLEX | partial_gravity | PASS |
| P06 | prevention | propane 40% oxygen | ACME-CFI-G, ACME-BRE, ACME-FLAME-DESIGN |  | PASS |
| D01 | detection | smoke detector on ISS | SAME, SAME-R, DAFT |  | PASS |
| D02 | detection | wire insulation overheating smoke | SAME, SAME-R, SAME-SIM |  | PASS |
| S01 | suppression | CO2 suppression of heptane fire | FLEX, FLEX-2, CFI |  | PASS |
| S02 | suppression | nitrogen extinguish fabric fire ISS | BASS, BASS-II, ACME-BRE |  | PASS |
| L01 | liquid | liquid fuel leak heptane ISS | FLEX, FLEX-2, CFI |  | PASS |
| T01 | trap | spacesuit | ACME-CFI-G, ACME-FLAME-DESIGN, ACME-BRE | o2_above_all | PASS |
| T02 | trap | Mars base | BASS-II, SAFFIRE-II, BASS | partial_gravity, mars_atmosphere | PASS |
| T03 | trap | hybrid rocket combustion chamber fire |  | out_of_scope | PASS |
| T04 | trap | 로켓 추진제 화재 위험 |  | out_of_scope | PASS |

## Weight stability (each weight ±0.05)

| Scenario | Rank 1 | Changes rank 1 |
|---|---|---|
| P01 | BASS | stable |
| P05 | ACME-BRE | stable |
| D01 | SAME | stable |
| S01 | FLEX | stable |
| L01 | FLEX | stable |
