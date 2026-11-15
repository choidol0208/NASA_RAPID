---
from: data
to: all
opened: 2026-11-15 09:53 KST
needed_by: 14:00
closed: false
---
# How NASA fire-safety work actually runs (six NASA documents opened today): who the tool is for and which step it serves; a decision for pm on the design intent

## What I need

*AI-generated (Claude Code), data role. The data side's human lead asked that this be reflected in the design intent and in the direction of the project: "the tool must make the real work easier, so it must reflect how fire-safety design really runs". An AI agent opened the six documents on 15 November and copied the sentences; no person has checked the quotes.*

**From pm, by 14:00: a yes, no or change to the proposal under "Proposal" below** (wording of the design intent in `docs/raw_data_design/`, the README and the submission text is pm's). ui and catalog: for reading; nothing to do unless pm asks.

### What the documents say

1. **The environment is set by other needs; fire safety is then worked inside it, case by case, with the design.**
   - Exploration atmospheres: "These atmospheres must mitigate the risks of fire, decompression sickness (DCS), and hypoxia and enable crew excursions" (NASA/TP-2010-216134, Executive Summary, p. 1). Fire was one of three scored risks; the reasons given for the lander and habitat atmospheres are about EVA ("allows efficient EVA preparation and egress on the moon"). The consequence for materials: "This will require spacecraft interior materials flammability testing at a maximum oxygen concentration outside the existing shuttle/ISS database."
   - It is not bolted on afterwards: materials usage agreements are first submitted at the preliminary design review and again when the design changes (NASA-STD-6016C, data requirement of the MUA: "INITIAL SUBMISSION: PDR."); "During the design of new spacecrafts, trade studies for fire detection, fire suppression, crew response ... must be conducted." (OCHMO-TB-008, p. 1).
2. **What a fire-safety engineer does, in order.**
   - Test the material in the worst case: "The worst-case anticipated use environment ... shall be used in the evaluation of material suitability." (NASA-STD-(I)-6001B, 4.1f).
   - If it fails and is still wanted: "A system flammability evaluation shall be conducted if materials that fail to meet the criteria of Test 1 are proposed for use in human-occupied spacecraft" (6001B, 6.1.1), by analysis or by test; at the level of the configuration (NASA-STD-6016C, 4.2.1.1 item i: "Flammability configuration analysis in accordance with JSC 29353 shows hardware configuration to be self-extinguishing.").
   - The measures named for that case: replace with a nonflammable material and restrict propagation paths ("primary methods ... are the limitation of flammable materials by replacement with nonflammable materials and the restriction of propagation paths", JSC 29353B, 2.4); "ignition sources are eliminated or controlled" (6001B, 6.1.2); a materials usage agreement for materials "technically acceptable but do not meet the requirements" (6016C, 4.1.6).
   - Detection and response: detectors in equipment bays, the cabin and ventilation return ducts; portable extinguishers; ventilation shut down and power removed in a fire (OCHMO-TB-008; NASA-STD-3001 Vol 2).
3. **Where the weight lies.** "spacecraft fire control is based on minimizing potential ignition sources and eliminating materials that can propagate fire." and "Fire extinguishers are always provided on crewed spacecraft, but are not considered as part of the fire control process." (JSC 29353B, section 1). The four capability areas are prevention and material flammability, detection, suppression, post-fire clean-up (OCHMO-TB-008), and "Prevention is never absolute".

Not confirmed: the current NASA-STD-6001B Change 3 text (standards.nasa.gov was blocked; the interim 6001B on NTRS was read, citation 20110012152); a sentence of NASA-STD-3001 Vol 2 that points to 6001. Sources: NTRS 20110012152, 20210021618 (6016C), 20150020937 (JSC 29353B); nasa.gov PDFs of TP-2010-216134, OCHMO-TB-008 Rev A, NASA-STD-3001 Vol 2 Rev F. None of 6016C and JSC 29353B is in `pipeline/spec/references.json` yet.

### What it means for the tool

- **The user.** Not "someone curious about combustion experiments" but an engineer at step 2: a material is proposed for a place in a vehicle whose atmosphere was fixed by other needs, and the question is what is recorded about that material, or its nearest relatives, at that oxygen, pressure, gravity and flow. The three piles already answer in that shape: recorded in NASA's tables / in the archive, unprocessed / no record in PSI.
- **The step the tool serves.** The configuration-level evaluation and the usage agreement need evidence at the use environment. The tool assembles what exists and names what does not; it does not evaluate, and it predicts nothing.
- **The measures.** The page can show, next to a gap, the measures NASA's documents name for that case, as quotations with their place: never as the team's advice.
- **The centre of gravity.** Material and propagation path first, detection second, suppression last. Our counted tests today sit mostly on extinction of droplets (S1 298) and least on flame spread over solids (P3 2): the page should say that plainly, since that is where the process puts its weight and where PSI's tables are thinnest.

### Proposal (pm decides)

1. One paragraph of design intent, in pm's documents and the README: who the user is, which step of NASA's process the tool serves, and that it assembles evidence for that step without evaluating. Suggested text: "A fire-safety engineer works inside an environment that other needs have fixed. When a material that fails the standard test is still wanted, NASA's rules ask for an evaluation of the actual configuration at the worst-case use environment. This tool gathers, for a chosen environment and question, what NASA's PSI tables record, what sits unprocessed in the archive, and what has no record, and shows next to each gap the measures NASA's documents name. It evaluates nothing and predicts nothing."
2. The data role adds the six documents' sentences as reference items (`references.json`, types `requirement`, `procedure`, `measure`), ties each of the six needs to the step of the process it informs (a new field, nothing renamed), and adds a small file `data/pipeline/process_steps.json`: step, NASA sentence, source, the needs that inform it, and the measures named. After the 0035 work, today.
3. The data role adds a per-material index (`data/pipeline/material_tests.csv`: material as written and as normalised, investigation, tests, recorded oxygen, pressure and flow ranges, outcomes recorded), because step 2 starts from a material. Counts only.
4. For ui, later and only if pm wants it: an entry by material, and the quoted measures under pile 3.

## Why

The human lead's point: a tool is useful when it fits the work as it is really done. The documents show the work is material by material, configuration by configuration, inside a fixed environment, and that its centre is material and propagation path.

## Until then

The data role continues 0035 (first commit pushed at 10:20: `question_chain.csv`, 77 checks PASS) and does items 2 and 3 after it unless pm says no.
