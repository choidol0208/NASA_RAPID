# The page shell

*AI-generated (Claude Code, pm role) on 15 November 2026 during the NASA Space Apps Challenge 2026 hackathon. Read by a person: none yet.*

The shell is the frame around the dashboard: how the page looks and how a visitor moves in it. It changes no sentence, number, label or link of a section. Files: `web/shell.css`, `web/shell.js`, `web/how.html`, and small edits in `web/index.html`, `web/app.js`, `web/build.py` and `web/capture_media.mjs`.

## What it adds

- **App bar** (both pages, sticky): the product name as text, the search input in compact form once a query is shown, "Copy link", "How it works", "Source code".
- **Start page** (no `?q=`): the headline sentence, the notice, the input and the examples, and the three verbs (Find, Compare, Interpret) as cards. The cards are built by `shell.js` from the page's own kickers and headings (`#top`, `#needs`, `#stops`), so they cannot drift. `app.js` still runs its ISS example in the background; the shell only keeps it out of view until a query is given.
- **After a query**: the hero folds to the notice line (it stays visible under the app bar), "At a glance" becomes a row of tiles (the tile with the evidence statement carries the blue accent), and a sticky tab bar replaces the "On this page" list (`#jump` stays in the page, not displayed; its two method entries now lead to `how.html`). One tab's sections are shown at a time.
- **Cautions under every tab**: the cautions of "How your input was read" (`#scenario-warnings`, for example "not bounds for lunar or Martian gravity") are copied by `shell.js` between the summary row and the tab bar (`.shell-warnings`), rebuilt whenever `app.js` renders them; the soft "no material" line is not copied. The originals stay in `#read`. The copy is not printed.
- **Closest investigations**: the ranked cards come first, "How your input was read" follows them (CSS `order`; the DOM order is unchanged).
- **Result cards**: name, team score, dimension strip, "Why", "Largest gap", the team note (it opens with a caution), the cautions, the tags and the "Weight check … (team computation)" line stay open, in their old order. Only the source links and the raw-data lines open in place behind "Details and sources"; "What the record says" keeps its own disclosure, closed as before (`app.js`, `renderResults`).
- **No other folds**: the requirements table and the two note lists ("For this scenario", "Other investigations") are open as before, because they state limits and carry team-computation labels. Nothing that states a limit, a caution, a team-computation or AI-generated label, or the not-safety-guidance notice is behind a closed disclosure that was open before.
- **Method page** `how.html`: the sections `#ai-use` and `#method`, moved from `index.html` unchanged. It loads `app.js` with `<html data-page="how">`; `app.js` then fills the two sections from the same data files as before and runs no query. Links between the two pages keep `?q=`. An old link to `index.html#method` or `#ai-use` is sent to `how.html`.
- **Strip above the footer** of the dashboard (`#how`): two sentences copied from the method page and a button to it. `build.py` stops the build if a strip sentence is not on `how.html` word for word.
- **Footer** (the same on both pages; `build.py` checks that): the page's notices, "Team RAPID · NASA Space Apps Challenge 2026", the two existing paragraphs, the licence, and the build stamp (commit and time from `data/build.json`).
- **States and keys**: a loading placeholder that keeps its place, the page's own empty and error sentences in one style, `/` puts the cursor in the input, the title carries the query, print shows every tab, `prefers-reduced-motion` is respected.

## Tab map

| Tab (`?tab=`) | Sections |
|---|---|
| Closest investigations (`closest`) | `#read`, `#top` |
| What was found (`found`) | `#results-first` (the ui role's section "What NASA's experiments and documents report", shown first in this tab), `#needs`, `#tests`, `#answers`, `#shown`, `#criteria` |
| Where the data are (`data`) | `#piles` |
| Where the evidence stops (`stops`) | `#stops` |
| All investigations (`all`) | `#all` |

`#status`, `#glance`, `#assistant` and `#how` are outside the tabs. A tab whose sections are all hidden is not offered. An address with `#<id>` (a section, or anything inside one, for example `#compare`) opens the tab that holds it and scrolls there at once; the shell keeps the target in place for up to 8 s while `app.js` renders content above it, and lets go when the visitor scrolls, clicks or types. `?tab=<name>` opens a tab; the back button steps through tabs; a tab click while scrolled down (and always on a phone) brings the tab bar back under the app bar.

`#compare` is a block inside `#needs`, so it is under "What was found", not "Where the evidence stops": moving it would change the order inside `#needs` (left for the pm to decide).

For scripts (`capture_media.mjs`, the assistant): `window.feeShell.reveal(selector or element)` opens the tab that holds it and scrolls there; for a section this query does not show it opens the first tab; on the start page it first shows the example run that `app.js` has already made (`?q=ISS` is pushed), as the page without the shell showed it. A plain `section.scrollIntoView()` on a section whose tab is closed, or on the start page, does the same (the shell wraps `scrollIntoView` on the tab sections), so the assistant's `#top` fallback and an assistant without the `feeShell` call still work. A submit of `#ask-form` that carries `data-quiet` (the assistant's own) keeps the visitor's tab and scroll position. After a query `#assistant` follows the open tab's sections and comes before the How-it-works strip; on the start page it stays under the input.

## Putting a new section into a tab

Either add its id to `TAB_OF` at the top of `shell.js`, or give the section the attribute `data-tab="found"` (or another tab name) in `index.html`. A section that does neither stays visible under every tab, so nothing is hidden by accident. For a place inside a tab other than the document order, add a line next to the `order` rules in `shell.css` ("the input" block).

## Turning the shell off

Remove the two tags marked in the `<head>` of `index.html` (and of `how.html`):

```html
<link rel="stylesheet" href="shell.css">
<script src="shell.js"></script>
```

The page then renders with `style.css` alone: every section visible, one column. The app bar and the footer blocks stay in the markup, unstyled; the method stays on `how.html`. Without JavaScript the shell sets no state, so every section is visible as well.

## What was checked (15 November 2026, 17:20 KST, on the build of this branch, by an AI session)

- Text: for six queries ("lunar habitat", "ISS", "lunar habitat cotton fabric", "smoke detector on ISS", "Mars base", "spacesuit"), every section's text blocks, links and titles were compared with the baseline build (the ui role's page without the shell), with every tab and every `<details>` opened (90 section comparisons, 17,861 text blocks), and the two method sections of `how.html` against the baseline's `index.html`. The only differences: the label "Details and sources" (once per card), the links "How the score works" and "(team computation)" that now lead to `how.html#method` and `how.html#ai-use` (with the query), and the query links of `#ai-use` on `how.html`, which lead to `./?q=…`.
- Addresses: `#piles`, `#stops`, `#top`, `#needs`, `#all`, `#tests`, `#answers`, `#results-first`, `#compare`, `#coverage` ("lunar habitat"), `#criteria`, `#shown`, `#needs` ("Mars base"), `#needs` ("ISS"), loaded directly and clicked after load, with and without reduced motion: the target ends 8 to 14 px under the bars in every case.
- Layout: no horizontal scroll of the page at 1440, 768 and 390 px, for the start page, the six queries (every tab), the empty and out-of-scope inputs and `how.html`; no console error on these pages. Controls on a phone are at least 40 px tall. The shell makes no DOM change while the page is idle.
- Layout shift while a page opened with `?q=lunar habitat` loads: 0.05 at 1440 px (0.12 without the shell), 0.14 at 768 px and 0.18 at 390 px; what remains is mostly the web font replacing the fallback font in the masthead.
- Behaviour: tabs, `#id` and `?tab=` addresses, the back button, `/`, the app bar search, the links between the two pages, the old `#method` address, `feeShell.reveal` on the start page and for a hidden section, `scrollIntoView` on a section whose tab is closed.
- `python3 web/build.py`, `python3 web/check_integration.py`, `python3 web/parity_check.py`.
- Checked in headless Chrome only. Not checked: Safari, Firefox, a real phone, a screen reader, the assistant widget inside this build (the build of this branch does not include it; the shell side of its hooks was checked by calling them).
