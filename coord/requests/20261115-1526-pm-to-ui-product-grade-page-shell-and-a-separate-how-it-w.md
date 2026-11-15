---
from: pm
to: ui
opened: 2026-11-15 15:26 KST
needed_by: 17:45
closed: false
---
# Product-grade page shell and a separate How-it-works page (the human lead's request): pm builds it on branch pm/ui-polish for you to merge

## What I need

*AI-generated (Claude Code), pm role.*

**The human lead asked the pm session at 15:22 KST for two things on the page: (1) the look and feel of a service that is really in use, and (2) the long explanation at the bottom ("How AI is used here, and how it was checked", "How the score works") on a page of its own, reached by a button, so that a visitor who does not want the method does not have to scroll past it.** `web/` is yours, so pm does not push this to `main`. To save you the time while you build the results block (1513), pm builds it as a proposal on the branch **`pm/ui-polish`**, cut from `catalog-filter` at `a8ece28`, and asks you to **merge it into `catalog-filter` when it arrives (about 17:30) if it passes your checks**. If you would rather do it yourself from a design note, say so in `coord/status/ui.md` in the next minutes and pm sends the note instead.

How the proposal is built so that it merges cleanly with your work in progress:
- **New files carry almost everything:** `web/shell.css` (loaded after `style.css`; overrides, nothing deleted from `style.css`), `web/shell.js` (app bar, tabs, disclosure), `web/how.html` (the method page). `web/build.py` copies them and builds `how.html`.
- **Small edits to your files:** `web/index.html` (the header, the footer, two tags, and the two method sections moved out), `web/app.js` only where a card's long notes and source links go behind a "Details and sources" disclosure, `web/build.py` for the new files, `web/check_integration.py` and `web/capture_media.mjs` only if a check or a capture needs to open a tab.
- **Nothing computed changes:** no text, number, label or link of a section is changed, added or removed; a script compares the text of every section for six queries before and after. Every section keeps its `id`; `main > section.ask`, `#q`, `#ask-form`, `#glance` and `#jump` stay, so the assistant widget and your checks work as before. No new font, icon set or library.

What it changes for a visitor: a slim sticky bar with the product name, the sections as tabs once a query is shown (Closest investigations / What was found / Where the data are / Where the evidence stops / All investigations), a "How it works" button to the method page, calmer cards with the long notes one click away, a real footer, and a layout that holds at 390 px.

**Two things that help now:**
1. For the results block of 1513, please use a section of its own with the id **`results`**, rendered by its own function, placed in `index.html` before `#piles`. The tab map of the proposal puts `#results` first in the tab "What was found". If you have already chosen another id, tell me the id.
2. Push the results block as soon as it stands, even unfinished, so that the proposal is rebased on it before you merge.

## Why

The lead's request; Presentation is one of the five judging criteria, and the page is what the judges open.

## Until then

pm builds and checks the proposal in a separate working copy (the page build, `check_integration.py`, `parity_check.py`, the text comparison, no console error at 390, 768 and 1440 px, with and without the assistant widget), then pushes the branch and tells you in `coord/status/pm.md`. The deck's captures are retaken from the merged page.

## Change at 15:30 (the human lead's decision, `coord/decisions.md`)

The human lead told pm to do this work directly because it has to be quick. So pm will **merge `pm/ui-polish` into `main` itself** as soon as the page checks and the text comparison pass (expected between 16:30 and 17:00), and push fixes from the independent checks after that. What pm asks of you now:
1. **Merge `main` into `catalog-filter` right after that push** (pm writes the time in `coord/status/pm.md`), so that a later push of `catalog-filter` does not put the old layout back on the public page. Until then, please keep pushing as usual.
2. Keep the results block (1513) in a section of its own with the id `results`, before `#piles`; it lands in the tab "What was found". If a conflict appears when you merge, the shell lives in `web/shell.css`, `web/shell.js` and `web/how.html` (see `web/SHELL.md`); your sections and their texts are yours and win.
3. If you see the shell break one of your checks or texts, tell pm in your status: pm fixes it at once.
