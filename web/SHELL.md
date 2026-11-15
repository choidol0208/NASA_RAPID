# The page shell

*AI-generated (Claude Code, pm role) on 15 November 2026 during the NASA Space Apps Challenge 2026 hackathon. Read by a person: none yet.*

The shell is the frame around the dashboard: how the page looks and how a visitor moves in it. It changes no sentence, number, label or link of a section. Files: `web/shell.css`, `web/shell.js`, `web/how.html`, and small edits in `web/index.html`, `web/app.js`, `web/build.py` and `web/capture_media.mjs`.

## What it adds

- **App bar** (both pages, sticky): the product name as text, the search input in compact form once a query is shown, "Copy link", "How it works", "Source code".
- **Start page** (no `?q=`): the headline sentence, the notice, the input and the examples, and the three verbs (Find, Compare, Interpret) as cards. The cards are built by `shell.js` from the page's own kickers and headings (`#top`, `#needs`, `#stops`), so they cannot drift. `app.js` still runs its ISS example in the background; the shell only keeps it out of view until a query is given.
- **After a query**: the hero folds to the notice line (it stays visible under the app bar), "At a glance" becomes a row of tiles, and a sticky tab bar replaces the "On this page" list (`#jump` stays in the page, not displayed). One tab's sections are shown at a time.
- **Result cards**: name, team score, dimension strip, "Why", "Largest gap", the cautions and the tags stay open. The team note, the source links, the raw-data lines, the weight check and "What the record says" open in place behind one disclosure per card, "Details and sources" (`app.js`, `renderResults`).
- **Three more disclosures**, made by `shell.js` from the nodes `app.js` renders, in the same order, each under its own existing heading: "Requirements read from your question" (`#requirements`), "For this scenario" (`#needs-notes`), "Other investigations" (`#other-notes`). The one label that follows a list ("AI-generated…", "Computed by team code…") stays outside the disclosure, visible; where `app.js` labels each item instead, the labels stay on their items.
- **Method page** `how.html`: the sections `#ai-use` and `#method`, moved from `index.html` unchanged. It loads `app.js` with `<html data-page="how">`; `app.js` then fills the two sections from the same data files as before and runs no query. Links between the two pages keep `?q=`. An old link to `index.html#method` or `#ai-use` is sent to `how.html`.
- **Strip above the footer** of the dashboard (`#how`): two sentences copied from the method page and a button to it. `build.py` stops the build if a strip sentence is not on `how.html` word for word.
- **Footer** (the same on both pages; `build.py` checks that): the page's notices, "Team RAPID · NASA Space Apps Challenge 2026", the two existing paragraphs, the licence, and the build stamp (commit and time from `data/build.json`).
- **States and keys**: a loading placeholder that keeps its place, the page's own empty and error sentences in one style, `/` puts the cursor in the input, the title carries the query, print shows every tab, `prefers-reduced-motion` is respected.

## Tab map

| Tab (`?tab=`) | Sections |
|---|---|
| Closest investigations (`closest`) | `#read`, `#top` |
| What was found (`found`) | `section#results` (first, when it exists), `#needs`, `#tests`, `#answers`, `#shown`, `#criteria` |
| Where the data are (`data`) | `#piles` |
| Where the evidence stops (`stops`) | `#stops` |
| All investigations (`all`) | `#all` |

`#status`, `#glance`, `#assistant` and `#how` are outside the tabs. A tab whose sections are all hidden is not offered. An address with `#<id>` (a section, or anything inside one, for example `#compare`) opens the tab that holds it and scrolls there; `?tab=<name>` opens a tab; the back button steps through tabs. `window.feeShell.reveal(selector)` does the same from a script (used by `capture_media.mjs`).

## Putting a new section into a tab

Either add its id to `TAB_OF` at the top of `shell.js`, or give the section the attribute `data-tab="found"` (or another tab name) in `index.html`. A section that does neither stays visible under every tab, so nothing is hidden by accident. For a place inside a tab other than the document order, add a line next to the `order` rules in `shell.css` ("the input" block).

## Turning the shell off

Remove the two tags marked in the `<head>` of `index.html` (and of `how.html`):

```html
<link rel="stylesheet" href="shell.css">
<script src="shell.js"></script>
```

The page then renders with `style.css` alone: every section visible, one column. The app bar and the footer blocks stay in the markup, unstyled; the method stays on `how.html`. Without JavaScript the shell sets no state, so every section is visible as well.

## What was checked (15 November 2026, on the build of this branch)

- Text: for six queries ("lunar habitat", "ISS", "lunar habitat cotton fabric", "smoke detector on ISS", "Mars base", "spacesuit"), every section's text blocks, links and titles were compared with a build of `a8ece28`, with every tab and every `<details>` opened (84 section comparisons). The differences are the ones listed in the commit message: the label "Details and sources", the team note's place on a card, and the links that now lead to `how.html`.
- Layout: no horizontal scroll of the page at 1440, 768 and 390 px, for the start page, the six queries (every tab), the empty and out-of-scope inputs and `how.html`; no console error on these pages.
- Behaviour: tabs, `#id` and `?tab=` addresses, the back button, `/`, the app bar search, the links between the two pages, the old `#method` address, print.
- `python3 web/build.py`, `python3 web/check_integration.py`, `python3 web/parity_check.py`.
- Checked in headless Chrome only, by an AI session. Not checked: Safari, Firefox, a real phone, a screen reader. `capture_media.mjs` was edited (it opens the tab that holds the element it photographs; the first slide shows the start page) and passes a syntax check, but was not run: Playwright is not installed on the machine this was built on.
