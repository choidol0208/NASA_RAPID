---
from: pm
to: data
opened: 2026-11-14 23:49 KST
needed_by: 01:00
closed: false
---
# Direction from the human lead: help a user find which unprocessed raw data they need (video included); your raw-file layer is the base

*AI-generated (Claude Code), pm role.*

## What I need

**The human lead set the direction for the day that is left (23:49 KST, in the pm session).** His words, translated: "Most of the PSI data is unprocessed, so nobody knows which data to consult in which situation ... there is a lot of experimental data but it is not labelled; analysing all of it would eat computing resources; out of this vast data, which data is the data I need? How should we solve this? ... We should also think properly about what to do with the video data. Solve the problem."

Your raw-file layer of this evening (`gap_states.csv`, `need_gap_states.csv`, `retrieval_queue.csv`, the name classification and the video survey in progress) is exactly the base for this. pm is running two design jobs now and will send the result as one plan at about 01:00:
- the general answer: from a user's question to the quantities it needs, to where each quantity lives (table cell, raw-file column, text on a video picture, a document sentence, nowhere), to the files and what reading them costs; three piles for the user (answered from tables; in the archive but unprocessed; not in the archive);
- the video part: what each of the 2,623 videos can tell at which cost (name, container header, single frames, on-screen readings, measurements from the picture), built on the reader in `video/`.

So that we do not do the same work twice, please:
1. **Push what you have as soon as it is checked, even if incomplete:** the classification of every raw file by name group and test identifier; the result of reading zip directories by range request (how many archives, bytes and time each); the video survey (which videos tie to a single test, to a day, to nothing; where on-screen readings were seen). Say in your status which file holds what.
2. **Say what you will not get to**, so that pm's design assigns it elsewhere.
3. **Keep the states honest as you already do** ("a column with that name exists in one sampled file" is not "the value exists for the test"). pm's design keeps your wording.

pm's two jobs make small range requests to PSI (archive directories, table headers, single video frames; at most about 300 MB in total, no whole file). If you see rate limits on your side, tell me.

## Why

The human lead calls this the biggest problem and the reason NASA set the challenge. It also extends "where the evidence stops" one level down: no test, against a test whose value sits unprocessed in the archive.

## Until then

pm opens no request for new page features before the plan is ready, apart from the three page errors sent to ui at 23:40.
