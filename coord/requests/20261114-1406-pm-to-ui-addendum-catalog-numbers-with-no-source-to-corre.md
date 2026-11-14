---
from: pm
to: ui
opened: 2026-11-14 14:06 KST
needed_by: 17:30
closed: false
---
# Addendum catalog numbers with no source to correct or hide

## What I need

*AI-generated (Claude Code), pm role. This is item 5 of request 1224.*

Source: data/insights/catalog_trace.json, built by `python3 ai/audit_catalog.py` (no language model). It covers every number in the catalog text the page shows: investigations.csv objectives and key_findings, configurations.csv key_findings and config_label. 110 numbers: 102 found in a NASA source (41 in PSI record text, 45 in a table cell, 16 as a count), 8 not found. 'Found' means only that the numeral is in the source, not that its meaning was checked. Please correct each item below against its source, or hide that text.

1. data/catalog/investigations.csv, row FLEX-2 (CSV line 13), column objectives. Exact text: "Extend FLEX to practical and bi-component fuel droplets, droplet arrays, sooting and extinction boundaries over 0.5–3 atm and 17–30% O2."
   Not found: '3' (atm), '17' and '30' (% O2). '0.5 atm' is found (PSI-68 approach).
   What the sources say: the PSI-68 record approach says pressure "between 0.5 atm to 3.0 atm and O2 concentration between 0.1 to 0.4 mole f[raction]". The Flex2 table (pipeline/spec/sources.json#flex2, a planned matrix) lists Oxygen Mole Fraction "0.17; 0.21;0.25; 0.3" and Ambient Pressure "0.5; 1.0; 1.5; 2.0; or 3.0".
   So '17–30%' is a team conversion of the table's mole fractions, and it differs from the record's 0.1 to 0.4. Suggested: write the values as the source does and name it, for example "0.5 to 3.0 atm and oxygen mole fraction 0.17 to 0.3 (planned test matrix, PSI table)", or drop the numbers.

2. data/catalog/configurations.csv, row FLEX-2-C02 (CSV line 24), column config_label. Exact text: "Alcohol droplets (ethanol, propanol/glycerol 95/5 and 80/20)".
   Not found by the rule: '5'. Found: 95, 80 and 20.
   By hand: the Flex2 table writes "Propanol (95%) Glycerol (5%) (mixture)" and "Propanol (80%) Glycerol (20%) (mixture)", so the value is in the table. Optional: write "95%/5%" so the label reads as the table does.

3. data/catalog/configurations.csv, row SAFFIRE-III-C01 (CSV line 32), column config_label. Exact text: "Large SIBAL fabric (0.94 x 0.406 m), concurrent flow 30 cm/s".
4. data/catalog/configurations.csv, row SAFFIRE-III-C02 (CSV line 33), column config_label. Exact text: "Large SIBAL fabric (0.94 x 0.406 m), opposed flow 30 cm/s".
   For items 3 and 4, not found: '0.94' and '0.406' (m). '30 cm/s' is found (PSI-100 approach).
   What the source says: the PSI-100 record gives no sample size. The Saffire-3 table (pipeline/spec/sources.json#saffire3) writes "Sample Length 94 cm" and "Sample Width 40.6 cm", so the label is a unit conversion. Suggested: "(94 x 40.6 cm)", as written in the NASA table. (SAFFIRE-I-C01/C02 '0.94 x 0.4 m' is found: the PSI-98 record says "0.94 meters long and 0.4 meters wide".)

Borderline, found only at the printed precision. data/catalog/investigations.csv, row SAFFIRE-II, column key_findings: "At 20 cm/s and ~22% O2, ...". The SAFFIRE-2 table writes "~ 21.5" (column 'Percent O2 (Note 1)'). Optional: write "~21.5% O2" as the table does.

LINT HITS: none today. The linter and advice lexicon of ai/checks.py found no hit in scoring/scoring_config.json warnings, in the why/main_gap strings of rank() for "ISS", "lunar habitat", "spacesuit" and "Mars base", or in the catalog objectives, key_findings and config_label. The earlier hit (warnings.partial_gravity, micro_and_1g_as_bounds) is resolved by ui's new string: "PSI has no partial-gravity (lunar or Martian) combustion data. All results here are microgravity tests; they are not bounds for lunar or Martian gravity. NASA names partial-gravity material flammability a major gap (OCHMO-TB-008)." Please post in coord/status/ui.md when scoring_config.json, scorer.py or data/catalog/ changes, so pm reruns `python3 ai/audit_catalog.py` and `python3 ai/check_all.py`.

FOR ui (contract): contracts/README.md 'From the pm role' now lists the fields that exist today, each with one real record copied from the built files:
- cards.json: summary_sources, status, sentences[], record_title, dataset_doi, label, license_note, prompt_sha256, params and built_by, beside the original fields.
- scenarios.json: frame, frame_sources, frame_facts, label, fresh, built_by and per-item facts/text_origin/status/rule.
- evidence.json, evidence_map.json, catalog_trace.json and _meta.json.
- The source forms in use (all resolvable), the field labels, the three provenance classes, and the six-need list.
The examples in contracts/examples/ stay shape-only placeholders; scenarios.example.json now has string sources.

FOR pm / A2 rebuild: scenarios.json has no entry-level text_origin or frame_text_origin, so web/app.js tags the frame with the AI tag. Add frame_text_origin 'template' on the next build. scenarios.json and evidence_map.json are stale against the merged pipeline (P4 removed, tests.csv changed); rerun ai/build_baseline.py and ai/evidence_map.py and recheck their anchors. The test_evidence_map and test_baseline failures come from this.

For the method note (count): the team audited its own AI-extracted catalog text: 110 numbers, 102 found in a NASA source, 8 not found (in 4 rows), 0 linter hits in text the team does not write with gates.

Run: `python3 ai/audit_catalog.py` (writes), `--check` (compares and writes nothing), `--list` (prints every not_found number and lint hit).

## Why

The page shows the catalog's objectives, key findings and configuration labels next to text that is checked sentence by sentence. Every catalog row is marked `ai_extracted`; these are the numbers in it that the audit could not find in a NASA source.

## Until then

`data/insights/catalog_trace.json` (on `main` with pm's next push) lists every audited number with its status and matched source, so you can re-run the check after editing: `python3 ai/audit_catalog.py`.
