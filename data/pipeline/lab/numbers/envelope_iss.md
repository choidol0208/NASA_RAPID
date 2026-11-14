# Envelope position: ISS cabin (`iss`)

*AI-generated (Claude Code), 2026-11-14. Not human-reviewed. Experiment on branch data-lab.*

Nominal point: o2_pct = 21, pressure_kpa = 101.3. Gravity level: microgravity.
Ranges: flow_cms [5, 30]; o2_pct [19, 23]; pressure_kpa [85.8, 116.8).

## Notes

- Every value is copied from data/pipeline/tests.csv (the pipeline's standardized value, with source file and row); every other number is a count, minimum, maximum or difference of those values.
- These numbers say where tests were run, not what happened in them; no outcome variable is read.
- Inside the hull of tested conditions means only that tests exist on several sides of this point; it says nothing about the outcome at this point.
- Outside means no arithmetic on these tests reaches this point.
- Counts of different needs are not added: one test can be counted for several needs.
- The nominal point is the one written in scenarios.json; its note there says what it is.
- gravity_level in tests.csv is not a column of any PSI table: it is a constant that the team's source mapping (pipeline/spec/sources.json, 'constants') sets for the whole table. The count below therefore counts tests of tables the team mapped as microgravity.

## Choices (spec parameters)

- `ambient_oxygen`: o2_pct recorded and o2_basis equal to 'ambient' (the rule of match_environments in pipeline/run.py: any other basis is marked not_ambient)
- `axes`: ['o2_pct', 'pressure_kpa']
- `counted_tests`: need_tests.csv rows with objective_link equal to 'stated'
- `degenerate_hull`: fewer than 3 non-collinear distinct points: hull kind 'point' or 'segment', reported as 'no area'; inside is true only where the nominal point coincides with the point or lies on the segment
- `gap_sign`: gap = nearest recorded value minus nominal value; positive means the nearest recorded value is above the nominal value; 0 means a test has exactly the nominal value; where two recorded values are equally near (one above, one below), both are listed
- `gravity`: count of tests whose gravity_level string equals the scenario's gravity_level string; a scenario with gravity_level null sets none
- `hull`: convex hull of the distinct recorded (o2_pct, pressure_kpa) points, monotone chain, exact rational arithmetic, no tolerance
- `hull_boundary`: a point on an edge or a vertex of the hull is reported as position 'boundary' and counted as inside
- `number_reading`: every cell and every spec number is read as the exact decimal it is written as (Python fractions.Fraction of the written string); differences are exact
- `pareto`: a test is listed when no other test of the set has |delta o2_pct| <= its |delta o2_pct| and |delta pressure_kpa| <= its |delta pressure_kpa| with at least one of the two strictly smaller; deltas = test value minus nominal value; no combined distance, no weight, no scaling; tests with identical deltas are all listed
- `ranges`: the in_range rule of pipeline/run.py (RANGE_DEFAULTS: min inclusive, max exclusive unless stated) applied to the scenario's ranges; a range the scenario does not set is reported as not set; the joint count requires oxygen and pressure both inside and is asserted equal to tests_atmosphere of scenario_needs.csv
- `scenarios_without_nominal`: a scenario whose nominal is empty gets no nominal-point numbers; its ranges are reported where set

## Summary per need

| Need | counted tests | with ambient O2 | with O2 and pressure | hull | nominal position | O2 in range | pressure in range | both in range | same gravity (O2 and pressure tests) |
|---|---|---|---|---|---|---|---|---|---|
| P1 Flammability limit | 133 | 133 | 0 | none | outside | 55 of 133 | 0 of 0 | 0 | 0 |
| P2 Ignition | 0 | 0 | - | - | - | 0 of 0 | 0 of 0 | 0 | 0 |
| P3 Flame spread and growth | 2 | 2 | 0 | none | outside | 2 of 2 | 0 of 0 | 0 | 0 |
| S1 Extinction conditions | 298 | 298 | 273 | area | interior | 116 of 298 | 161 of 273 | 56 | 273 |
| D1 Combustion products | 122 | 122 | 0 | none | outside | 45 of 122 | 0 of 0 | 0 | 0 |
| D2 Smoke generation conditions | 0 | 0 | - | - | - | 0 of 0 | 0 of 0 | 0 | 0 |

## P1 Flammability limit

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value |
|---|---|---|---|---|---|
| o2_pct | 133 | 13.6 | 22.2 | yes | 21 (gap 0, 9 tests) |
| pressure_kpa | 0 | - | - | - | - |

Tests with both recorded: 0 (0 distinct points; none). Hull: none (no area). Nominal point: outside, inside = false.


## P2 Ignition

No counted test of this need has a recorded ambient oxygen.

## P3 Flame spread and growth

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value |
|---|---|---|---|---|---|
| o2_pct | 2 | 21.5 | 21.7 | no | 21.5 (gap 0.5, 1 tests) |
| pressure_kpa | 0 | - | - | - | - |

Tests with both recorded: 0 (0 distinct points; none). Hull: none (no area). Nominal point: outside, inside = false.


## S1 Extinction conditions

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value |
|---|---|---|---|---|---|
| o2_pct | 298 | 12 | 34 | yes | 21 (gap 0, 54 tests) |
| pressure_kpa | 273 | 70.1676 | 309.2946 | yes | 101.2983 (gap -0.0017, 6 tests) |

Tests with both recorded: 273 (250 distinct points; PSI-69). Hull: area. Nominal point: interior, inside = true.

Nearest tests (Pareto set in |delta o2_pct|, |delta pressure_kpa|):

| test | investigation | o2_pct | pressure_kpa | delta o2_pct | delta pressure_kpa | source |
|---|---|---|---|---|---|---|
| FLEX-4 | PSI-69 | 21 | 101.325 | 0 | 0.025 | PSI-69_Experimental table_FLEX.csv row 5 |
| FLEX-5 | PSI-69 | 21 | 101.325 | 0 | 0.025 | PSI-69_Experimental table_FLEX.csv row 6 |
| FLEX-6 | PSI-69 | 21 | 101.325 | 0 | 0.025 | PSI-69_Experimental table_FLEX.csv row 7 |
| FLEX-9 | PSI-69 | 21 | 101.325 | 0 | 0.025 | PSI-69_Experimental table_FLEX.csv row 10 |
| FLEX-197 | PSI-69 | 20 | 101.2983 | -1 | -0.0017 | PSI-69_Experimental table_FLEX.csv row 198 |

## D1 Combustion products

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value |
|---|---|---|---|---|---|
| o2_pct | 122 | 13.6 | 22.2 | yes | 21 (gap 0, 9 tests) |
| pressure_kpa | 0 | - | - | - | - |

Tests with both recorded: 0 (0 distinct points; none). Hull: none (no area). Nominal point: outside, inside = false.


## D2 Smoke generation conditions

No counted test of this need has a recorded ambient oxygen.
