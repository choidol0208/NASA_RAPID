---
from: pm
to: data
opened: 2026-11-14 16:30 KST
needed_by: 18:30
closed: false
---
# Long verbatim quotes from copyrighted documents in references.json: shorten before the freeze

*AI-generated (Claude Code), pm role.*

## What I need

**Shorten the long verbatim quotes that come from documents the team has no right to reproduce, by 18:30.**

A rules check of the submission draft counted 264 verbatim quotes in `pipeline/spec/references.json`, 24 of them longer than 40 words (pm recounted: the same 24). The repository is public and will be linked from the submission. `AGENTS.md` section 6 says a submission with material the team does not hold the rights to is not accepted.

The 24 by document, longest quote in words:
- Not NASA works, so treat as copyrighted: `ISO-14624-1` (49), `ASTM-D2863` (45), `ASTM-G125` (41), `FSJ-2018-SAME` (50 and 45), `ICES-2012-SAME2` (59 and 44), `ICES-2015-196` (57), `ICES-2016-SAFFIRE` (43), `ICES-2014-179` (42), `CSSCI-2014-ACME` (41), `NTRS-20130010991` (41, issuer "AIAA / NASA GRC").
- NASA documents (usually free of copyright as US Government works, but check the notice on each): `NASA-TM-20210011385` (58 and 48), `NP-2015-10-034-JSC` (57 and 45), `NASA-STD-6001B` (55 and 41), `NASA-TM-2011-217036` (55), `SAME-EIRD-2005` (48 and 43), `SAMER-FR-2014` (48 and 44), `SAME-FSR-2010` (42).

Please:
1. For the documents in the first group, cut each quote to the shortest phrase that carries the point (one sentence, 25 words or fewer as a guide), or replace it by a statement in the team's words marked as such, with the place in the document. Where several quotes come from one paid standard, keep as few as the need definitions really use.
2. For every document that is not a NASA work, look over its shorter quotes too: many short quotes from one standard add up.
3. Keep `check.py` checking quotes against the text you hold; a shortened quote is still verbatim.
4. Tell pm when it is on `data-pipeline`: pm's statements cite reference items, so pm rebuilds after the merge.

If a quote cannot be shortened without changing what the need definition rests on, say which, and pm brings it to the human lead.

## Why

It is a rule of the competition, and long passages from ISO, ASTM and journal texts in a public repository are the most likely place for a complaint. Short, attributed quotations are what the page needs anyway.

## Until then

pm keeps the current text. The submission draft says that the repository holds verbatim quotes and how many; pm updates that sentence when you answer.
