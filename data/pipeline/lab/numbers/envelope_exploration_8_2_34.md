# Envelope position: Exploration atmosphere 8.2 psia / 34% O2 (`exploration_8_2_34`)

*AI-generated (Claude Code), 2026-11-14. Not human-reviewed. Experiment on branch data-lab.*

Nominal point: o2_pct = 34, pressure_kpa = 56.5. Gravity level: not set.
Ranges: o2_pct [32, 36]; pressure_kpa (-inf, 62.8).
Conversions by the pipeline (pipeline/spec/sources.json): o2_pct of bass2: 'Calibrated  initial O2 % by vol' rule number; o2_pct of flex: 'O initial ambient composition; mole fraction' rule number factor 100; o2_pct of saffire1: 'Percent O2' rule o2_text; o2_pct of saffire2: 'Percent O2 (Note 1)' rule o2_text; pressure_kpa of flex: 'Ambient pressure; mmHg' rule number factor 0.133322368.

## Notes

- Every value is the pipeline's standardized value in data/pipeline/tests.csv (with source file and row); where the source unit differs, it is the product of the source cell and the unit factor listed under 'conversions', rounded to 4 decimals by the pipeline. Every other number is a count, minimum, maximum or difference of those values.
- These numbers say where tests were run, not what happened in them; no outcome variable is read.
- Inside (interior or boundary) means that the nominal point lies in the smallest convex region containing the tested (o2_pct, pressure_kpa) points. It does not mean that a test was run close to it: the deltas of the Pareto table give the distance to the closest tests on each axis. It says nothing about the outcome at this point.
- Outside means that the nominal point is not in that region: it lies on the outer side of at least one edge of the hull.
- No hull: no counted test of this need records both an ambient oxygen and a pressure, so the nominal point has no position.
- The hull and the Pareto set pool all counted tests that record both values, whatever the fuel, geometry, flow or investigation; the summary table names what was pooled.
- The nearest value of each axis is taken over that axis alone and can come from a different test on each axis; the Pareto table is a separate answer.
- A value flagged in tests.csv (for example 'approximate in source', or the start value of a range written in the source) is used as held; such tests are listed under 'flagged tests' and counted at min, max, nearest and in the Pareto table.
- Counts of different needs are not added: one test can be counted for several needs.
- The nominal point is the one written in scenarios.json; its note there says what it is.
- The nominal values are rounded figures as written in scenarios.json; a gap smaller than half a unit of their last written digit is marked, and the rounding box corners show whether the position depends on that rounding.
- gravity_level in tests.csv is not a column of any PSI table: it is a constant that the team's source mapping (pipeline/spec/sources.json, 'constants') sets for the whole table. The gravity count therefore equals the number of tests of tables the team mapped to the scenario's level and is not a match found in the data.
- The scenario sets no gravity level.

## Choices (spec parameters)

- `ambient_oxygen`: o2_pct recorded and o2_basis equal to 'ambient' (the rule of match_environments in pipeline/run.py: any other basis is marked not_ambient); the numbers of counted tests left out because o2_pct is empty and because o2_basis is not 'ambient' are reported per need (excluded_o2_not_recorded, excluded_basis_not_ambient)
- `axes`: ['o2_pct', 'pressure_kpa']
- `counted_tests`: need_tests.csv rows with objective_link equal to 'stated'
- `degenerate_hull`: fewer than 3 non-collinear distinct points: hull kind 'point' or 'segment', reported as 'no area'; inside is true only where the nominal point coincides with the point or lies on the segment
- `flagged_values`: a value whose test carries a flag on that axis in the 'flags' column of tests.csv (for example o2_pct:approximate_in_source, o2_pct:range_in_source_start_value_named_in_publication) is used as the number held in tests.csv, like every other value, and is not left out; per need and axis, every counted test with such a flag is listed with its flags and o2_range_as_written, and min, max, nearest and each Pareto test give the number of flagged tests at that value
- `gap_sign`: gap = nearest recorded value minus nominal value; positive means the nearest recorded value is above the nominal value; 0 means a test has exactly the nominal value; where two recorded values are equally near (one above, one below), both are listed
- `gravity`: count of tests whose gravity_level string equals the scenario's gravity_level string; a scenario with gravity_level null sets none; where gravity_level of every test used is a table constant of the team's source mapping, the count equals the number of tests of tables mapped to that level and carries no information beyond that mapping
- `hull`: convex hull of the distinct recorded (o2_pct, pressure_kpa) points, monotone chain, exact rational arithmetic, no tolerance
- `hull_boundary`: a point on an edge or a vertex of the hull is reported as position 'boundary' and counted as inside
- `nearest_per_axis`: the nearest recorded value of each axis is taken over that axis alone; the two axes can have their nearest value in different tests, and neither need be a test of the Pareto set: they are separate answers
- `no_hull`: where no counted test records both values, hull kind is 'none', position is 'no hull' and inside is null (no position is defined)
- `nominal_rounding`: h = half a unit of the last digit written for the nominal value in scenarios.json (70.3 gives 0.05; 21.0 gives 0.05); a gap or Pareto delta with absolute value below h is marked below_nominal_rounding; the 4 corners (nominal +- h on each axis) are placed relative to the hull like the nominal point and the number inside is reported, so a reader sees whether the position changes within the written rounding of the nominal
- `notes_per_need`: every per-need sentence that applies is shown (no_tests where no counted test has ambient oxygen, no_nominal where the scenario has no nominal point); there is no precedence
- `number_reading`: every cell and every spec number is read as the exact decimal it is written as (Python fractions.Fraction of the written string); differences are exact. The cells are the pipeline's standardized values: where a source column has another unit, the pipeline multiplied the cell by a unit factor of pipeline/spec/sources.json and rounded the product to 4 decimals (rule 'number' of pipeline/rules.py); the factor of every source column used is copied under 'conversions'. The nominal values are read as written in scenarios.json and are themselves rounded figures: see 'nominal_rounding'
- `pareto`: a test is listed when no other test of the set has |delta o2_pct| <= its |delta o2_pct| and |delta pressure_kpa| <= its |delta pressure_kpa| with at least one of the two strictly smaller; deltas = test value minus nominal value; no combined distance, no weight, no scaling; tests with identical deltas are all listed; dominance is decided per axis, so a change of unit on either axis does not change the set
- `pooling`: the hull and the Pareto set pool every counted test with ambient oxygen and pressure both recorded, whatever its fuel, flow, geometry or investigation; the tests pooled are reported per investigation_id, fuel_phase and sample_geometry (joint.composition) and in the summary table
- `ranges`: the in_range rule of pipeline/run.py (RANGE_DEFAULTS: min inclusive, max exclusive unless stated) applied to the scenario's ranges; a range the scenario does not set is reported as not set; the joint count requires oxygen and pressure both inside and is asserted equal to tests_atmosphere of scenario_needs.csv
- `ranges_not_on_axes`: a scenario range of a variable that is not one of 'axes' (flow_cms for the ISS) is printed with 'not applied' and enters no count
- `scenarios_without_nominal`: a scenario whose nominal is empty gets no nominal-point numbers; its ranges are reported where set

## Governed by (pipeline/lab/model_map.json)

Labels in brackets next to the column names below name the decision point and its governing model key, or 'team rule'.

- M01a: OECD_HULL, OECD ENV/JM/MONO(2007)2, Guidance Document on the Validation of (Q)SAR Models, Chapter 4, para 110 (https://www.oecd.org/content/dam/oecd/en/publications/reports/2014/09/guidance-document-on-the-validation-of-quantitative-structure-activity-relationship-q-sar-models_g1ghcc68/9789264085442-en.pdf; opened by applicability scout (via Exa); verifier (via Exa web fetch, 2026-11-14); para 110 text re-read by the lab session from the saved Exa copy)
- M01b: team rule, no established model found
- M01c: team rule, no established model found
- M02a: team rule, no established model found
- M02b: ELEM, elementary mathematics (the definition is the model)
- M03: team rule, no established model found
- M04: team rule, no established model found
- M05a: team rule, no established model found
- M05b: team rule, no established model found
- M05c: ELEM, elementary mathematics (the definition is the model)
- M05d: team rule, no established model found
- M05e: team rule, no established model found
- M08: ELEM, elementary mathematics (the definition is the model)

## Summary per need

| Need | counted tests [M05a: team rule] | with ambient O2 [M05b: team rule] | with O2 and pressure [M03: team rule] | pooled tests (investigation, phase, geometry: tests) | hull [M01a: OECD_HULL; M01c: team rule] | nominal position [M01a: OECD_HULL; M01b: team rule] | O2 in range [M05e: team rule] | pressure in range | both in range | gravity_level string equal to scenario's (table constant, not a match in data) [M05c: ELEM] |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 Flammability limit | 133 | 133 | 0 | - | none | no hull | 0 of 133 | 0 of 0 | 0 | not set |
| P2 Ignition | 0 | 0 | - | - | - | - | 0 of 0 | 0 of 0 | 0 | not set |
| P3 Flame spread and growth | 2 | 2 | 0 | - | none | no hull | 0 of 2 | 0 of 0 | 0 | not set |
| S1 Extinction conditions | 298 | 298 | 273 | PSI-69 liquid droplet: 273 | area | outside | 9 of 298 | 0 of 273 | 0 | not set |
| D1 Combustion products | 122 | 122 | 0 | - | none | no hull | 0 of 122 | 0 of 0 | 0 | not set |
| D2 Smoke generation conditions | 0 | 0 | - | - | - | - | 0 of 0 | 0 of 0 | 0 | not set |

gravity_level in tests.csv is not a column of any PSI table: it is a constant that the team's source mapping (pipeline/spec/sources.json, 'constants') sets for the whole table. The gravity count therefore equals the number of tests of tables the team mapped to the scenario's level and is not a match found in the data. The scenario sets no gravity level.

## P1 Flammability limit

Counted tests left out: 0 without o2_pct, 0 with o2_basis not ambient.

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value [M02b: ELEM; rounding mark M04: team rule] |
|---|---|---|---|---|---|
| o2_pct | 133 | 13.6 (0 flagged) | 22.2 (0 flagged) | no | 22.2 (gap -11.8, 13 tests, 0 flagged) |
| pressure_kpa | 0 | - | - | - | - |

- flagged test (o2_pct): SAFFIRE-2-2-1 value 21.5, flags o2_pct:approximate_in_source
- flagged test (o2_pct): SAFFIRE-2-2-2 value 22.1, flags o2_pct:approximate_in_source
- flagged test (o2_pct): SAFFIRE-2-2-3 value 22.1, flags o2_pct:approximate_in_source
- flagged test (o2_pct): SAFFIRE-2-2-4 value 22.1, flags o2_pct:approximate_in_source
- flagged test (o2_pct): SAFFIRE-2-2-5 value 22.1, flags o2_pct:approximate_in_source
- flagged test (o2_pct): SAFFIRE-2-2-6 value 22.1, flags o2_pct:approximate_in_source
- flagged test (o2_pct): SAFFIRE-2-2-7 value 22.1, flags o2_pct:approximate_in_source
- flagged test (o2_pct): SAFFIRE-2-2-8 value 22.1, flags o2_pct:range_in_source_start_value_named_in_publication, written in source as '22.1 to 22.0'

Tests with both recorded: 0. Hull: none. Nominal point: no position.

No hull: no counted test of this need records both an ambient oxygen and a pressure, so the nominal point has no position.

## P2 Ignition

Counted tests left out: 0 without o2_pct, 0 with o2_basis not ambient.

No counted test of this need has a recorded ambient oxygen.

## P3 Flame spread and growth

Counted tests left out: 0 without o2_pct, 0 with o2_basis not ambient.

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value [M02b: ELEM; rounding mark M04: team rule] |
|---|---|---|---|---|---|
| o2_pct | 2 | 21.5 (1 flagged) | 21.7 (1 flagged) | no | 21.7 (gap -12.3, 1 tests, 1 flagged) |
| pressure_kpa | 0 | - | - | - | - |

- flagged test (o2_pct): SAFFIRE-1-S1 value 21.7, flags o2_pct:range_in_source_start_value_named_in_publication, written in source as '21.5 - 21.7'
- flagged test (o2_pct): SAFFIRE-1-S2 value 21.5, flags o2_pct:approximate_in_source

Tests with both recorded: 0. Hull: none. Nominal point: no position.

No hull: no counted test of this need records both an ambient oxygen and a pressure, so the nominal point has no position.

## S1 Extinction conditions

Counted tests left out: 0 without o2_pct, 0 with o2_basis not ambient.

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value [M02b: ELEM; rounding mark M04: team rule] |
|---|---|---|---|---|---|
| o2_pct | 298 | 12 (0 flagged) | 34 (0 flagged) | yes | 34 (gap 0, below nominal rounding, 9 tests, 0 flagged) |
| pressure_kpa | 273 | 70.1676 (0 flagged) | 309.2946 (0 flagged) | no | 70.1676 (gap 13.6676, 1 tests, 0 flagged) |

Tests with both recorded: 273 (250 distinct points; PSI-69). Hull: area. Nominal point: outside, inside = false. Rounding box (nominal +- 0.05 o2_pct, +- 0.05 pressure_kpa): 0 of 4 corners inside. [hull M01a: OECD_HULL; position M01a: OECD_HULL; M01b: team rule; rounding box M04: team rule]

Nearest tests (Pareto set in |delta o2_pct|, |delta pressure_kpa|) [M02a: team rule]:

| test | investigation | o2_pct | pressure_kpa | delta o2_pct | delta pressure_kpa | flags on axes | source |
|---|---|---|---|---|---|---|---|
| FLEX-37 | PSI-69 | 34 | 71.2341 | 0 (below nominal rounding) | 14.7341 | - | PSI-69_Experimental table_FLEX.csv row 38 |
| FLEX-174 | PSI-69 | 24 | 70.8875 | -10 | 14.3875 | - | PSI-69_Experimental table_FLEX.csv row 175 |
| FLEX-259 | PSI-69 | 21 | 70.5275 | -13 | 14.0275 | - | PSI-69_Experimental table_FLEX.csv row 260 |
| FLEX-262 | PSI-69 | 20 | 70.3409 | -14 | 13.8409 | - | PSI-69_Experimental table_FLEX.csv row 263 |
| FLEX-121 | PSI-69 | 18 | 70.1676 | -16 | 13.6676 | - | PSI-69_Experimental table_FLEX.csv row 122 |

## D1 Combustion products

Counted tests left out: 0 without o2_pct, 0 with o2_basis not ambient.

| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value [M02b: ELEM; rounding mark M04: team rule] |
|---|---|---|---|---|---|
| o2_pct | 122 | 13.6 (0 flagged) | 22.2 (0 flagged) | no | 22.2 (gap -11.8, 13 tests, 0 flagged) |
| pressure_kpa | 0 | - | - | - | - |

Tests with both recorded: 0. Hull: none. Nominal point: no position.

No hull: no counted test of this need records both an ambient oxygen and a pressure, so the nominal point has no position.

## D2 Smoke generation conditions

Counted tests left out: 0 without o2_pct, 0 with o2_basis not ambient.

No counted test of this need has a recorded ambient oxygen.
