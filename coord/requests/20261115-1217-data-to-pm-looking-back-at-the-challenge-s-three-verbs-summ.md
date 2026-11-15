---
from: data
to: pm
opened: 2026-11-15 12:17 KST
needed_by: 14:00
closed: false
---
# Looking back at the challenge's three verbs (summarize, rank, interpret results): results should lead the page; what the data role adds and what already exists

## What I need

*AI-generated (Claude Code), data role. Written after a talk with the data side's human lead, who agreed that it be shared.*

**A decision from pm and the leads by 14:00: should results lead the page, with the raw-data piles after them?** The order of the page and the submission text are yours; this is the data side's reading and what it can deliver today.

### The reading

The challenge is titled "SI-Powered Fire Safety Insights from Microgravity Combustion Data" and asks for a dashboard that summarizes, ranks and interprets the results of the experiments. Measured against those three verbs (the data session has not read the official page itself; it works from the five sentences in `references.json`, `CHALLENGE-2026`; a person should re-read the page's objectives today):

| The challenge asks | What the page does today | Gap |
|---|---|---|
| summarize the **results** | cards summarize what an investigation set out to do; counts say how many tests are recorded | what the experiments found is in a list of quoted items, not in front |
| **rank** | ranks investigations by closeness to an environment, with assumed atmospheres and weights | nothing ranks the results themselves |
| **interpret** for fire safety | no judgement, by rule | NASA's own interpretation (process steps, criteria) was absent until this morning |

What the team did well: every number is traceable, checked by a second path, and the page says where the record stops. What drifted: since yesterday afternoon most of the data side's work went into the raw archive. It was worth knowing (12.8 TB of the 13.47 TB are archives whose members are about 12.66 million images and camera frames; the numbers that exist are in the tables, a few workbooks and the papers), but it is the last chapter of the story, not the first. The processed results of these experiments are in the investigators' papers and NASA's reports: `material_published.csv` shows that of 18 materials printed in three reference tables only one has the same name as a material of the PSI tables.

### What already exists for "results first" (no new work)

- `data/pipeline/findings.csv`: 211 quoted statements; 89 are of kind `result`, each with the conditions its own words state (oxygen, pressure, gravity, flow, fuel phase, material), the quote, the place and the source.
- `data/pipeline/findings_by_environment.json` and rung 3 of every answer file: per scenario and need, the results in three groups by a fixed rule, no weights: at the oxygen and pressure of the environment / about one of its stated conditions / general. That is a ranking of results that needs no assumption.
- `process_steps.json` and the `process` field: which step of NASA's process a need informs, and the measures NASA's documents name, as quotations.
- `need_recorded_summary.csv`: per need, how many tests are in the tables, how many have an outcome in a cell, how many are counted, how many have a video tied by two labels.

### What the data role adds today (inside its paths; starts now, does not wait for the decision)

`data/pipeline/results_by_need.json` (and a flat CSV): per need and scenario, in page order, (1) what NASA's experiments found: the quoted results with their printed numbers taken from the items' `values` where an item holds a table, ordered by the fixed rule above, then by material; (2) the criterion or reference line NASA's documents state for that need, as a quotation; (3) what PSI's tables record; (4) what sits unprocessed; (5) no record in PSI. Counts and quotations only; no arithmetic between a result and a criterion; every entry with its source and place.

### Suggested order of the page (pm and ui decide)

For an environment and a question: what was found (quoted results, nearest conditions first) -> what NASA's rules say about it -> what the tables record -> where the record stops (the three piles) -> what is in the archive. The ranking of investigations stays as a way in, labelled as the team's.

## Why

A judge reads Impact and Relevance from what the page tells about fire safety. The results are what tell it; the piles tell where the telling ends.

## Until then

The data role builds `results_by_need.json` and reviews the 11 sentences of your request 1137.
