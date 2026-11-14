---
from: data
to: pm
opened: 2026-11-14 15:03 KST
needed_by: 16:15
closed: false
---
# Review a proposal: answer safety-type questions with an evidence ladder set in NASA's own procedure

# Review a proposal: answer safety-type questions with an evidence ladder set in NASA's own procedure

*AI-generated (Claude Code), data role. The direction below was raised by the human lead in the data session; the plan is laid out for review, and the choice is the lead's and pm's.*

## What I need

**pm: review this proposal and answer by 16:15 with go, go with changes, or no. If go, decide the three points at the end. Nothing here is built into the product until you answer; one data file (step A) is being built now because it is additive and useful either way.**

### The question behind it

The human lead asked: a judge or a researcher will type "is this material safe?" or "how does fire spread in a lunar habitat?". Today the page answers "N recorded tests, here is where the data stops". Can the dashboard answer such questions, and how, without inventing anything?

### The proposal: an answer in four rungs, set inside NASA's own procedure

A verdict ("safe", "spreads at x mm/s on the Moon") cannot be produced from these data and must not be. What can be produced is the answer a fire-safety engineer would give: how NASA decides this kind of question, what has been recorded toward it, what has been published, what is not known.

1. **The frame: how NASA decides the question.** From standards already in `references.json`, quoted:
   - Flammability is judged by a pass/fail test "in the worst-case atmosphere to which the material could be exposed" (`6001B.T1.focr59`), "currently 30% oxygen at 10.2 psia" (`TB14639.worstcase`), and the result "is pass-fail and is only valid at the atmosphere tested" (`ICES14.onlyvalid`).
   - The alternative is a measured limit with a margin: "A modified Test 1 measures the actual upward flammability limit ... so that the margin of safety in the use environment can be assessed" (`TB14639.modified`); the threshold holds "at a given constant total pressure, temperature, convective flow, and gravity-level conditions" (`ISO16697.scope`).
   - Why the procedure cannot simply be reused for exploration: the ground test "may not be conservative" in low gravity (`OF2012.margin`, `RG.test1`), and in Table I of Olson and Ferkul the lowest limiting oxygen of each of the three materials is at a partial-gravity level, below both the 1 g and the 0 g value (`OF2012.table1`: Mylar G lunar 15.6 against 0 g 17.0 and 1 g 21.2). So a result at 1 g or 0 g does not bound lunar or Martian gravity; a test at the condition itself is needed, and "material flammability in partial gravity remains a major gap" (`TB008.gaps`).
2. **Rung 1, recorded at the condition:** the evidence package of the environment and need (exists).
3. **Rung 2, recorded near the condition:** the neighbouring oxygen and pressure cells with their counts and recorded ranges, and how they differ from the condition asked (data exist in `evidence/cell_*.json`; needs assembling).
4. **Rung 3, published by NASA and the investigators:** the quoted reference items that state the same oxygen, pressure or gravity, by need (step A below). Examples for the lunar habitat: Saffire VI test conditions at 54 to 55 kPa and 29 to 31% oxygen (`SAF456.conditions`; results not yet extracted), limiting oxygen in lunar gravity (`OF2012.table1`), flames persisting without flow in elevated oxygen (PSI-20 record, preliminary), the investigators' caveat that stopping ventilation "may not be applicable in future exploration missions" (`ICES19.fanoff`).
5. **Rung 4, not known:** the gap codes, `not_covered`, and the quoted research needs (`CP2003.*`, `TB008.gaps`), worded as "the test that would answer this has not been found in these sources".

The top line of every answer is chosen by rule from the rungs, never written freely: for example "Not judged here. No test at this condition is in the PSI tables; NASA publications report the following for it; the following is not known." The model's part is the same as in your current design: it may rephrase and order sentences of an answer file, and every number and quote is checked by code against that file.

### What each role would do

| Step | What | Who | When |
|---|---|---|---|
| A | `data/pipeline/findings.csv`, `findings_by_environment.json`: reference items tagged by need and by the conditions their own words state; lists per scenario and need of findings at the environment, about one of its conditions, and general | data | in progress, 16:15 |
| B | `data/pipeline/answers/<scenario>__<need>.json` for `iss` and `lunar_habitat`: the frame items, rungs 1 to 4, fixed sentences, a rule-chosen top line; checked by `check.py` | data | 17:30 if go |
| C | question text to (scenario, material, need): a keyword table next to the scorer presets | catalog | if time |
| D | answer text from the answer file through your existing gates | pm | your call |
| E | an answer card: top line, four rungs, a source link on every sentence | ui | your call |

If C to E do not fit before 19:00, the fixed sentences of B can be shown as they are under the existing scenario row: no model and no new input box.

### Decisions I need from you

1. **Go or no.** If no, step A still stands as a data file and nothing else changes.
2. **Your decision of 13:05** says published results on partial gravity appear "at most as one cited sentence". Rung 3 puts published results, quoted and labelled as such, at the centre of the answer. Does that decision change, and for which topics?
3. **Scope before the freeze:** both presets and all six needs, or the lunar habitat with P1 and P3 only (the demo contrast)?

## Why

The organisers' feedback was that the project lacks something that catches the eye. "Ask a fire-safety question, get an answer that shows what is recorded, what is published and what nobody knows, each with its source" is closer to the challenge title than a count of tests, and it uses the 66 documents and about 309 quoted items collected today, which the page does not show yet.

## Until then

I finish step A, the raw-data inventory you asked for (request 1449) and D5 when the review sheet lands. The three files to be frozen at 17:30 do not change through any of this.

## Addendum, 15:15 KST: use NASA's own open questions as the index

The human lead added a point that sharpens the proposal: the team does not set criteria, but NASA will, on the existing base; so the tool should show (a) what else has to be considered before a criterion can be set, and (b) what a user can stand on while no criterion exists. Both already exist in NASA documents, and we hold them as quoted reference items:

- **What must be determined before criteria can be set: NASA's own question and gap lists.**
  - 2004 organizing questions of the fire prevention, detection and suppression project (`CP2004.*`), for example "How do the flammability and ignitability of materials change in high-O2 mole fraction, low-pressure, reduced gravity environments?" (`CP2004.flam.q6`), "How does the flammability, ignitability and Limiting Oxygen Index (LOI) of a material change with gravitational level?" (`CP2004.flam.q4`), "What are the O2 mole fraction and absolute pressure below which a fire cannot exist?" (`CP2004.supp.q3`), "What are the appropriate pre-fire and fire signatures for fire detection in low and partial gravity?" (`CP2004.det.q2`).
  - The 2003 research plan (`CP2003.roadmap.*`, `CP2003.prev.*`, `CP2003.resp.*`, `CP2003.det.*`), for example "Augment existing go/no go criteria with a quantitative test method which provides ranking or indication of flammability margin" (`CP2003.prev.margin`).
  - The gaps named by the Spacecraft Fire Safety Systems Maturation Team (`SMT.gap.*`), as reported in the 2016 Saffire paper.
- **What a user stands on meanwhile: the existing procedure.** Test in the worst-case atmosphere (`6001B.T1.focr59`); where flammable material is used, control its amount and arrangement and isolate a potential fire by firebreaks (`6001B.6.1.2.spread`, which points to JSC 29353; we have not read that document); the four areas of fire protection (`TB008.areas`); testing and certification to 34% oxygen for exploration atmospheres (`EAWG.testing`).

**Proposed change to the plan:** the index of the answer view is these NASA questions, verbatim with document and year, instead of the team's six needs (the literature check found that no NASA document gives our six as a list; they stay underneath as the mapping to variables). For each NASA question the tool shows: recorded PSI tests that bear on it (through the mapped need and the stated conditions), published statements that bear on it (step A), and what none of the sources hold. That is an evidence map on NASA's own agenda, not a criterion.

Limits to state on the page: the lists are from 2003, 2004 and 2013; the page shows what the sources we read hold against each question, not whether NASA today considers a question open or closed; the mapping from a NASA question to variables and scenarios is the team's reading and is labelled so.

If you agree, step B becomes `data/pipeline/nasa_questions.json` (one entry per quoted question: source, year, mapped needs and conditions with the words that justify the mapping, counts of recorded tests by scenario, lists of published findings, what is missing) for the questions about material flammability, flame spread, extinction and detection: about 25 questions. Same deadline, 17:30.
