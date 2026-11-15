---
from: data
to: pm
opened: 2026-11-15 15:45 KST
needed_by: 17:30
closed: false
---
# Review results_top.json: five published results to show first per scenario and question, as ready lines (and three weak spots to decide)

## What I need

*AI-generated (Claude Code), data role. Asked for by the data side's human lead: a small file the page can print as is, and a review by pm.*

**A review by 17:30 of `data/pipeline/results_top.json` (and `results_top.csv`), on `data-pipeline` at `2a30689` and in `main` after your next merge: is it fit to show, and what should change in the three weak spots below?** It adds files only; no answer file, count or existing field changed, so it does not make a recording stale. The data role's status says that no further data change is coming.

What it is: for every scenario (6) and question (6), the five published results to show first, each with `line` (the item's own sentence, unchanged), `values_line` (the printed values, at most six cells, then "and n more in the source table"), `conditions_line` (only the conditions the result's own words state), `group`, `result_kind`, `relation`, `source_line`, `url`, `access`; a `header` made of counts ("41 quoted results for this question; showing 5. 0 at the oxygen and pressure of this environment, 2 about one of its stated conditions.") and a fixed footer ("Quoted from NASA documents with the numbers as printed. Read by an AI agent, not checked by a person. The team compares nothing and recommends nothing."). All 36 blocks have five entries. 96 of 96 checks PASS; check U6 recomputes the choice from `results_by_need.json` with separate code.

The rule, fixed and without weights (verbatim in the file's `_meta` and in `pipeline/spec/results.json`, key `top_five`): the question's own results only; ordered by (1) condition group: at the oxygen and pressure of the environment, about one of its stated conditions, without these conditions stated, other conditions; (2) measured before computed by the authors, simulation, preliminary; (3) results of a PSI investigation of this catalogue before results of a related NASA experiment; (4) with printed values before without; (5) item id; at most two results per document.

Examples as they stand in the file:
- Lunar habitat, flame spread: 1 and 2, LUCI in simulated lunar gravity (PMMA rod 1.5 mm/s; cotton-fiberglass fabric .92 and 1.1 mm/s; a related NASA experiment, not a PSI investigation); 3, Saffire-I 1.8 mm/s concurrent and 1.3 mm/s opposed at 20 cm/s; 4, none of the Saffire-2 silicone samples burned; 5, a correlation statement without values.
- Lunar habitat, extinction: BASS-II thin PMMA sheets went out at about 1 cm/s (100 to 300 micrometres) and about 1.5 cm/s (400 micrometres); LOI 0.12 for methanol and 0.15 for heptane in oxygen and nitrogen.

**Three weak spots, yours to decide:**
1. **`values_line` uses the keys of the reference file as labels** (for example `flame_spread_rate_mm_s: 1.5 mm/s`), and one cell reads "~6cm cm" because the stored value already holds its unit. Readable for an engineer, not polished. Options: show `line` and `source_line` only and leave the values to the panel; or tell me to add a label per key (a spec change, about an hour, and then your recording must follow it).
2. **Some fifth entries are thin**: a sentence with no value (lunar habitat P3 number 5; lunar habitat S1 number 5 reads "Result of the nitrogen jet on thick solids."). They are in because the rule fills five. Option: show only entries that have printed values or a quotation; the file has what is needed to filter (`values_line` empty).
3. **Long lines**: `line` is never cut; the longest is about 1,300 characters (a table description). Option for the page: cut on display with "more", never in the data.

Also for your wording gate: three `line` fields contain the word "flammable" from a NASA sentence (listed in `_meta.forbidden_word_hits_in_lines`); none contains safe, acceptable, sufficient, representative or proven.

## Why

You decided at 15:13 that results lead. This file is the shortest road from that decision to a block on the page: ui prints five lines per question with no selection logic of its own, and the assistant's `published_results` tool can quote the same five first.

## Until then

The data role changes nothing under `data/pipeline/`. It answers questions on the file at once.
