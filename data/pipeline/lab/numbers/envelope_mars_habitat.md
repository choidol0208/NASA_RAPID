# Envelope position: Mars habitat (`mars_habitat`)

*AI-generated (Claude Code), 2026-11-14. Not human-reviewed. Experiment on branch data-lab.*

Nominal point: none. Gravity level: martian.
Ranges: none.

## Notes

- Every value is copied from data/pipeline/tests.csv (the pipeline's standardized value, with source file and row); every other number is a count, minimum, maximum or difference of those values.
- These numbers say where tests were run, not what happened in them; no outcome variable is read.
- Inside the hull of tested conditions means only that tests exist on several sides of this point; it says nothing about the outcome at this point.
- Outside means no arithmetic on these tests reaches this point.
- Counts of different needs are not added: one test can be counted for several needs.
- scenarios.json gives no nominal point for this environment, so no nominal-point numbers are computed.
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
| P1 Flammability limit | 133 | 133 | - | - | - | not set | not set | not set | 0 |
| P2 Ignition | 0 | 0 | - | - | - | not set | not set | not set | 0 |
| P3 Flame spread and growth | 2 | 2 | - | - | - | not set | not set | not set | 0 |
| S1 Extinction conditions | 298 | 298 | - | - | - | not set | not set | not set | 0 |
| D1 Combustion products | 122 | 122 | - | - | - | not set | not set | not set | 0 |
| D2 Smoke generation conditions | 0 | 0 | - | - | - | not set | not set | not set | 0 |

## P1 Flammability limit

scenarios.json gives no nominal point for this environment, so no nominal-point numbers are computed.

## P2 Ignition

No counted test of this need has a recorded ambient oxygen.

## P3 Flame spread and growth

scenarios.json gives no nominal point for this environment, so no nominal-point numbers are computed.

## S1 Extinction conditions

scenarios.json gives no nominal point for this environment, so no nominal-point numbers are computed.

## D1 Combustion products

scenarios.json gives no nominal point for this environment, so no nominal-point numbers are computed.

## D2 Smoke generation conditions

No counted test of this need has a recorded ambient oxygen.
