---
from: data
to: all
opened: 2026-11-14 14:42 KST
needed_by: 16:00
closed: true
---
# Counts changed after a literature check of the four open questions; link rule and required pressure

# Counts changed after a literature check of the four open questions; link rule and required pressure

*AI-generated (Claude Code), data role.*

## What I need

**pm, ui, catalog: take the counts and the wording below from `data-pipeline` commit `a5a9e87` or later, and tell me by 16:00 if anything you show breaks. This is the last planned change to the three files frozen at 17:30.**

The human lead of the data side ruled that four open points must be settled by standards and by the investigators' publications, not by the team's judgment, and without claiming more than a document says. Four literature checks ran (each with verbatim quotes, now reference items in `pipeline/spec/references.json`, 66 documents). What they changed:

1. **Which investigation counts for which need.** A need is now linked to an investigation by a sentence in which the investigators or a NASA project document state the purpose of that experiment (a reference item), with a verdict: `supported`, `differs`, `topic_only`. Only `supported` links are counted. `objective_links.csv` lists all links with `publication_item`, `publication_quote`, `verdict`; `objective_link` in `need_tests.csv` and `capability_matrix.csv` is `stated` for supported links only.
   - Saffire-I and -III no longer count for P1; Saffire-II no longer counts for P3. The investigators give fire growth to Saffire-I and -III and flammability limits to Saffire-II (`SAF16.saffire1`, `SAF16b.saffire13`, `SAF16.saffire2`); the three PSI records share one joint sentence.
   - **D1 Combustion products now has counted tests: 122 BASS-II tests.** The investigators state the gas measurement as a purpose: "To evaluate the levels of combustion products produced during microgravity fires, BASS-II requested the use of ... onboard sensors" (`BASS2TM.products`, `ICES15.purpose`). They frame it as completeness of combustion, not as detection. The old sentence "no investigation states combustion products" is wrong; please drop it.
   - S1 keeps PSI-69, PSI-25, PSI-26. The burner and droplet investigations whose record has the word "extinction" (PSI-10, 20, 21, 23, 39, 68) are no longer linked: the stated purpose in the documents read is not fire suppression. No count changes from this.
2. **Pressure is a required condition of P1 and S1** (ISO/TS 16697: an oxygen threshold holds "at a given constant total pressure, temperature, convective flow, and gravity-level conditions"; `CP2004.supp.q3` for S1). Where the table has no pressure, the condition is met by a sentence about the whole table: BASS-II "Pressure was not varied from 1 atmosphere." (nominal, for the investigation, not per test). No pressure value is created; bins, tiers and `pressure:not_recorded` are unchanged. One FLEX test whose pressure cell is `0` is no longer counted for S1.
3. **SAME "Weight loss rate" is a planned target value, not a result** (SAME requirements document, 2005: "Two target mass loss rates are specified in the test matrix"). The SAME and SAME-R tables hold conditions only; the measured smoke properties are in the final reports and papers. **D2 has no counted test.** Do not write that SAME tests were run at 1 or 2 mg/min.
4. **Oxygen cells with two numbers: no midpoint any more.** Saffire-I S1 is 21.7% and Saffire-II 2-8 is 22.1%, the values the investigators give as the initial oxygen reported by the ISS when the vehicle departed (`SAF17.o2_initial_I`, `SAF17.o2_initial_II`); Saffire-II 2-9 has no single value (new text column `o2_range_as_written` keeps the cell). These oxygen values are not readings at ignition.

**Counts now** (`need_tests.csv`, `scenario_needs.csv`):

| Need | Counted | ISS | Lunar habitat |
|---|---|---|---|
| P1 Flammability limit | 133 (was 136) | `oxygen_only` 55 | `other_atmosphere` |
| P2 Ignition | 0 | `not_measured` | `not_measured` |
| P3 Flame spread and growth | 2 (was 11) | `oxygen_only` 2 | `other_atmosphere` |
| S1 Extinction conditions | 298 (was 299) | `in_atmosphere` 56 + 7 | `in_atmosphere` 17 |
| D1 Combustion products | 122 (was 0) | `oxygen_only` 45 | `other_atmosphere` |
| D2 Smoke generation conditions | 0 (was 4) | `not_measured` | `not_measured` |

The headline counts by fuel phase and oxygen bin did not change, except one: solid fuels at 19 to 23% oxygen are 61 recorded tests (was 62), because Saffire-II sample 2-9 has no single oxygen value now.

**New columns and fields** (additive): `tests.csv` `o2_range_as_written`, `smoke_particle_size_um` (always empty; the outcome the literature names for smoke tests); `capability_matrix.csv` `required_documented_not_in_table`; `objective_links.csv` as above; package `objective` entries carry `verdict`, `publication_item`, `publication_quote`.

**What is the team's own** is now written down in `needs.json` `_meta.authorship` (being reworded in the next commit): no NASA document read gives these six needs as a list; the three pillars are backed; the split below them is the team's.

## Why

So that a reader can follow every count to a NASA table cell and every definition to a quoted sentence of a standard or of the investigators.

## Until then

`python3 pipeline/check.py` passes 46 of 46 checks on this state. A prose-only commit follows (questions, notes and README brought in line with the quotes); it changes no count.
