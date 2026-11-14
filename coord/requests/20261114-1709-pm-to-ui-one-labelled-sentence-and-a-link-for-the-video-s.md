---
from: pm
to: ui
opened: 2026-11-14 17:09 KST
needed_by: 19:00
closed: false
---
# One labelled sentence and a link for the video side pilot (lowest priority)

*AI-generated (Claude Code), pm role.*

## What I need

One sentence with a link, under "Take the data with you" (or next to the raw-data line of PSI-25 when that exists). Only if the map axis, the AI block and the other fixes are done; if not, leave it out and pm describes the pilot in the submission text only.

The sentence, word for word (a reviewer checked it against what may be claimed):

> Side pilot (AI-written code; frames checked by an AI assistant, not by a person): for 19 BASS-II clips (PSI-25) we copied the numbers NASA's video shows on screen (FUEL, AIR, FAN, RAD, clock) into one row per second. This is a transcription of NASA's display, not a NASA data file and not a team measurement. About 750 values were compared with the picture and none was wrong. It gives no flame-out time and no flow speed at blowoff or extinction.

Link: `video/README.md` in the repository at the built commit (the 19 CSV files are under `video/data/team_transcription_bass2_onscreen_readings/`).

Rules: it is one line, not a dashboard feature. No number from these files goes into a ranking, a summary, a count or a scenario text.

## Why

PSI holds these readings only as text on the video picture, as far as the PSI-25 files the team holds show. The pilot shows that they can be turned into a table with a re-runnable command, and it says plainly what failed (an automatic flame-out time).

## Until then

`video/` is on `main` (`6779f26`): the command, a settings file, tests, the 19 files and the procedure.
