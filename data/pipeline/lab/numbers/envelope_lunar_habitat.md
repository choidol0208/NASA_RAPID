# Envelope position: Lunar base or pressurized rover (`lunar_habitat`)

*AI-generated (Claude Code), 2026-11-14. Not human-reviewed. Experiment on branch data-lab.*

Nominal point: o2_pct = 30, pressure_kpa = 70.3. Gravity level: lunar.
Ranges: o2_pct [30, 36]; pressure_kpa (-inf, 85.8).

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
| P1 Flammability limit | 133 | 133 | 0 | none | outside | 0 of 133 | 0 of 0 | 0 | 0 |
| P2 Ignition | 0 | 0 | - | - | - | 0 of 0 | 0 of 0 | 0 | 0 |
| P3 Flame spread and growth | 2 | 2 | 0 | none | outside | 0 of 2 | 0 of 0 | 0 | 0 |
| S1 Extinction conditions | 298 | 298 | 273 | area | outside | 24 of 298 | 103 of 273 | 17 | 0 |
| D1 Combustion products | 122 | 122 | 0 | none | outside | 0 of 122 | 0 of 0 | 0 | 0 |
| D2 Smoke generation conditions | 0 | 0 | - | - | - | 0 of 0 | 0 of 0 | 0 | 0 |

## P1 Flammability limit

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value |
|---|---|---|---|---|---|
| o2_pct | 133 | 13.6 | 22.2 | no | 22.2 (gap -7.8, 13 tests) |
| pressure_kpa | 0 | - | - | - | - |

Tests with both recorded: 0 (0 distinct points; none). Hull: none (no area). Nominal point: outside, inside = false.


## P2 Ignition

No counted test of this need has a recorded ambient oxygen.

## P3 Flame spread and growth

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value |
|---|---|---|---|---|---|
| o2_pct | 2 | 21.5 | 21.7 | no | 21.7 (gap -8.3, 1 tests) |
| pressure_kpa | 0 | - | - | - | - |

Tests with both recorded: 0 (0 distinct points; none). Hull: none (no area). Nominal point: outside, inside = false.


## S1 Extinction conditions

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value |
|---|---|---|---|---|---|
| o2_pct | 298 | 12 | 34 | yes | 30 (gap 0, 15 tests) |
| pressure_kpa | 273 | 70.1676 | 309.2946 | yes | 70.3409 (gap 0.0409, 1 tests) |

Tests with both recorded: 273 (250 distinct points; PSI-69). Hull: area. Nominal point: outside, inside = false.

Nearest tests (Pareto set in |delta o2_pct|, |delta pressure_kpa|):

| test | investigation | o2_pct | pressure_kpa | delta o2_pct | delta pressure_kpa | source |
|---|---|---|---|---|---|---|
| FLEX-41 | PSI-69 | 30 | 71.2341 | 0 | 0.9341 | PSI-69_Experimental table_FLEX.csv row 42 |
| FLEX-174 | PSI-69 | 24 | 70.8875 | -6 | 0.5875 | PSI-69_Experimental table_FLEX.csv row 175 |
| FLEX-259 | PSI-69 | 21 | 70.5275 | -9 | 0.2275 | PSI-69_Experimental table_FLEX.csv row 260 |
| FLEX-262 | PSI-69 | 20 | 70.3409 | -10 | 0.0409 | PSI-69_Experimental table_FLEX.csv row 263 |

## D1 Combustion products

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value |
|---|---|---|---|---|---|
| o2_pct | 122 | 13.6 | 22.2 | no | 22.2 (gap -7.8, 13 tests) |
| pressure_kpa | 0 | - | - | - | - |

Tests with both recorded: 0 (0 distinct points; none). Hull: none (no area). Nominal point: outside, inside = false.


## D2 Smoke generation conditions

No counted test of this need has a recorded ambient oxygen.
