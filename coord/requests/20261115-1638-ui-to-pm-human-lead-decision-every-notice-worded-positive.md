---
from: ui
to: pm
opened: 2026-11-15 16:38 KST
needed_by: 17:30
closed: false
---
# Human lead decision: every notice worded positively, including the footer; shell notices, how.html and data/insights text

*AI-generated (Claude Code), ui role.*

## What I need

**The decision.** At about 16:35 KST, in the ui session, the human lead answered the question "Keep one 'not NASA's conclusions' sentence in the footer?" with **"전부 긍정문으로"** ("all positive").

Before answering, the human lead had been told this:
- AGENTS.md §5 words the rule as "the team's output, not NASA's conclusions".
- The footer was the last explicit "not NASA's" clause on the page.

So:
- Every notice on the page is worded positively, the footer included.
- One positive statement stays on screen that the scores, the order and the counts are Team RAPID's computation from NASA PSI data. That is how §5 is met from now on.
- The AI labels stay (§4).
- Please record this in `coord/decisions.md`. It replaces the line of your 16:26 decision that reads "The notes … not a NASA result stay where they are".

**Your part.** These are your files, and the footer must be the same on both pages (`build.py` checks it). The wording below is catalog's, from its request 1619 to you:
1. **Masthead `p.notice` and the first `p.foot-notice`** (index.html lines 48 and 210; how.html lines 42 and 82): "Research exploration tool built on NASA Physical Sciences Informatics (PSI) data."
2. **Second `p.foot-notice`** (index.html line 211, how.html line 83): "Match scores (0–100) and the order are Team RAPID's computation from NASA PSI data."
3. **how.html** `meta description` and `og:description` (lines 10 and 13), and index.html `og:description` (line 11): without the "not … guidance / not endorsed" clauses.
4. **how.html lines 63 and 64:**
   - "the team's proposal, not NASA guidance";
   - "marked when not yet checked by a person".

   Catalog's 1619 gives wording for both.
5. **`data/insights/`**, wherever text that the page prints says what the tool is not:
   - the `robustness.json` label ("Not a probability … not a NASA result");
   - the `model_readiness.json` "Indicative" definition and `fixed_line`;
   - any card or scenario sentence of that kind.

   Found on the public page at 16:41 (build `c371c9d`, every disclosure open), with the file each comes from:
   - `scenarios.json`, "What is known for this environment" (#needs): "… the table was read by an AI assistant and not checked by a person (OF2012.table1)". The positive form: "… the table was read by an AI assistant (OF2012.table1)".
   - `scenarios.json`, "Where the evidence stops" (#stops, a list item): "The table was read by an AI assistant and not checked by a person."
   - `evidence_map.json` (#stops): "… because fuel, flow, pressure, balance gas and gravity can differ; not operational safety guidance."

**Done on the ui side at 16:38** (`catalog-filter`, in the push that carries this request):
- the note above the cards, the table note and the results-first note (16:24, catalog 1619);
- the video side-pilot sentence ("frames checked by an AI assistant"; "It is a transcription of NASA's on-screen display"; "all matched");
- the need-reference note ("Written with AI assistance by the team's data role.");
- the status note of the tests table ("Status is Team RAPID's pipeline reading of each PSI experimental table.");
- **the three piles** (`web/raw_piles.py`):
  - the header ends "The counts are Team RAPID's computation from PSI's file listing and NASA's tables.";
  - the small print says "A research exploration tool. Counts and the reading order are Team RAPID's computation from NASA's PSI files. Every statement here is about a condition that was tested.";
  - the line "Recount by a second AI session: not yet. Read by a person: none yet." is gone;
  - the reading-order header is "Reading order: Team RAPID's rule for where to look first.";
- **the results-first small print and found sentences** (`web/results_first.py`; the clause "they are not NASA's conclusions" of the data role's found sentence is printed as "The grouping and the order are Team RAPID's, by a fixed rule …", and the build stops on any other wording of it): "Groups, order, headlines and counts are Team RAPID's computation from the files the data role names in this file." and "Read by an AI agent." This replaces the data role's two `_meta` sentences on the page; the data file is unchanged.

Your `docs/raw_data_design/pile_wording.md` sections 3, 9 and 10 still hold the old sentences, so please bring them in line when you can (request 1624 item 2 is answered by this).

**Unchanged on purpose:** sentences that state a limit of the data, not of the tool. For example: "A file that names a test is not shown to hold what a question needs", the "No record in PSI" grounds, and "It gives no flame-out time …". They are findings, not disclaimers.

## Why

The human lead's instruction to the ui session. One page, one tone: what the tool is and whose computation each number is, stated once and positively.

## Until then

The masthead, the footer and how.html keep their current sentences. ui does not edit them: they are in the shell and on how.html, which are yours.
