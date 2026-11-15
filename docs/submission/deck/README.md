<!-- AI-generated text: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon. -->
# The seven-slide deck (Project Demo)

This folder builds the deck for the "Project Demo" field of the submission form: 7 slides, title slide included, in English. The result is `docs/submission/slides.pdf`.

**Made with AI.** The build script, the capture script, the refresh script, the words on the slides, the speaker notes and this file were written with an AI assistant (Claude Code, pm role) on 15 November 2026, from the plan in `docs/submission/slides_outline.md` (as rewritten at about 16:15 KST). Checked by code and AI sessions; reviewed by a person: 0. Every slide carries the mark "Built with AI assistance (Claude)" in its footer. The words are a draft for the team to rewrite in its own words. No language model runs when the deck is built.

The deck describes a research exploration tool. It is not safety guidance and it is not endorsed by NASA. Counts, scores and rankings on the slides are the team's computation, not NASA's conclusions. The results quoted on slide 4 are quotations; nothing is computed from them.

## What the folder holds

| File | What it is | Written by |
|---|---|---|
| `refresh.sh` | One command: builds the page in a scratch copy, takes the captures, builds the deck and the PDF | AI-generated code |
| `build_deck.py` | The build script (Python standard library only). Reads every number from the repository's files, checks them, and writes the files below | AI-generated code |
| `capture.mjs` | Takes the captures of the team's own page (headless Chrome over the DevTools protocol, Node's built-in WebSocket; no library) | AI-generated code |
| `numbers.json` | Every number shown on a slide or said in a note, with its source file and the way it was computed; the cross-checks that passed; the state of the placeholders; the captures on the slides with their time and SHA-256 | `build_deck.py` |
| `slides.html` | The deck: one page, 7 slides of 1920 x 1080 CSS pixels, inline CSS, inline SVG charts, captures taken from `img/crop/`. On screen the slides are stacked and scaled to the window; `slides.html?only=3` shows slide 3 alone. It needs the network for its fonts (see "Fonts") | `build_deck.py` |
| `speaker_notes.md` | One note per slide, 60 words or fewer, with the same numbers | `build_deck.py` |
| `../slides.pdf` | The deck as a PDF: 7 pages, 16:9, text selectable, fonts embedded. This is the file to upload and link | `build_deck.py --pdf` (headless Chrome) |
| `preview/slide-1.png` to `slide-7.png` | One picture per slide, 1920 x 1080 | `build_deck.py --pdf` (headless Chrome) |
| `img/*.png`, `img/captures.json` | Captures of the team's own page and their manifest (see "Captures") | `capture.mjs` |
| `img/crop/*.png` | The part of each capture that a slide shows, cut out of the capture so that `slides.html` and the PDF hold nothing else. The name carries the source, the pixel box and the start of the source's SHA-256 | `build_deck.py` |

## How to refresh and rebuild

From the repository root:

```
bash docs/submission/deck/refresh.sh                 # the page changed, or the data: retake every capture, then build the deck and the PDF
DECK_ONLY=cotton_top3.png bash docs/submission/deck/refresh.sh   # retake only the captures named (comma separated), then build
python3 docs/submission/deck/build_deck.py --pdf     # only words or constants changed: build the deck and the PDF from the captures in img/
python3 docs/submission/deck/build_deck.py           # the same without the PDF and the previews
```

`refresh.sh` does six things: (1) copies the working tree (the files of `git ls-files -co --exclude-standard`) to a scratch folder and runs `web/build.py` there, so the repository's own `web/dist` is never written; (2) serves that build on `127.0.0.1`, on a free port from 8821 to 8829; (3) runs `capture.mjs`; (4) stops the server; (5) runs `build_deck.py --pdf`; (6) prints the page count and the size of the PDF. It can be run again at any time. It leaves no server and no browser running, also when a step fails, and says so in its last line. It takes about 45 seconds. `DECK_SCRATCH=<folder>` keeps the scratch copy in a folder of your choice (outside the repository); without it a temporary folder is used and removed.

Needs: Python 3, Node.js 22 or later (built-in `WebSocket`; `web/parity_check.py` also runs the page's JavaScript scorer), Google Chrome (at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, or set `CHROME`), `git`, `rsync`, `curl`, `lsof`, and a network connection for the two font hosts.

The build stops with an error (`CANNOT BUILD`) when a file is missing; when two files that should agree do not; when a sentence on a slide would no longer be true (for example a counted test appears at 30% oxygen or more and 70.3 kPa or less, or the third result no longer holds its place by the oxygen rule); when a capture was taken under another scoring config than `scoring/scoring_config.json`, is not the file its manifest entry describes, was taken without the page's fonts, or shows other values than the files (names, scores, reasons, largest gaps, the quoted result, the counted tests, the end of the solid-fuel tests); when a speaker note is longer than 60 words; when the PDF does not have exactly 7 pages of 16:9, is over 10 MB, or embeds a font other than the page's two families.

Run twice on the same captures, the build gives the same `slides.html`, `speaker_notes.md`, crops and previews. `numbers.json` differs in `_meta.built_at` and, after a commit, `_meta.git_commit`; the PDF differs in its creation date. After `refresh.sh`, the captures carry a new time and may differ by a few pixels of text smoothing.

## What a person edits

Near the top of `build_deck.py`. Edit, then rebuild with `--pdf`.

1. **`TEAM_NAME`** (section 1). Now `"RAPID"`, the name given by the human lead on 15 November 2026. `None` shows the placeholder chip "[team name]" on slide 1 and in the first speaker note.
2. **`ASSISTANT_MEASURED`** (section 1). Three values of the conversational assistant's evaluation, all `None` now, because `data/insights/assistant_eval.json` does not exist yet. While any is `None`, slide 6 shows the chip "to be measured" in its place, takes the title "Four uses of SI and how each is checked" and says "Measurement in progress". When all three are filled (from `data/insights/assistant_eval.json`, never by estimate), the title becomes "Four kinds of SI, each with its measured check." and the note of slide 6 changes with it.
3. **`WORDING`** (section 2). Every word on the slides and in the notes. `{names}` are filled with values computed from files, so no number from a file is typed there. `**text**` is bold; `[[text]]` stays on one line.
4. **`QUOTED_EXAMPLE`**. The id of the quoted result shown on slide 4 (`LUCI25.sibal_spread` in `data/pipeline/results_by_need.json`). Its quotation, conditions, group and source are read from that file, and the build checks that the page's capture shows the same quotation.
5. **`VIDEO_FRAME_CHECK_ON_SLIDE`**. The video reader's frame check (186 frames, none wrong) is stated in `video/README.md`, and its per-frame sheet is not in the repository. `True` shows the figure with the visible tag "stated in video/README.md, not recounted"; `False` leaves it out. It is `False`: the outline (Open point 6) keeps the figure only once the team lead has resolved the label.

At the top of `capture.mjs`:

6. **`RECORDED_CONVERSATION` and `RECORDED_TURN`**: the recorded answer of the assistant shown on slide 6 (the turn is counted from 1). Now conversation `where_data_iss`, turn 2, "Which raw files belong to test FLEX-1?", from `data/insights/assistant_recorded.json` (written 15 November 2026, 16:36 KST; 6 conversations, 11 turns). It was chosen because both sentences of its answer are written by the local model, both were kept by the checks, each carries the numbers of the facts it cites, and the question is in English. The capture is taken only when `ai/assistant/_runtime/RECORDED_READY` exists, which marks the recording as finished (it exists since 16:37 KST), and only when the chosen answer is written by the model with cited facts; otherwise slide 6 keeps its four rows at full width without a picture, and `img/captures.json` says why (`_meta.not_taken`). `capture.mjs` types the recorded questions of the conversation up to the chosen turn into the assistant's box; the page replays the recording and calls no model. The slide shows two parts of the capture: the question, and the answer with its citation numbers, the "Recorded on ..." label and the line of the checks. The steps, the reading of the request and the panels are in the capture and not on the slide. To change the turn, edit the two constants and run `DECK_ONLY=assistant_recorded.png bash docs/submission/deck/refresh.sh`.
7. **`QUERY`**: the worked example, "lunar habitat cotton fabric". It must equal `WORDING["s3"]["input_value"]` in `build_deck.py`; the build stops if a capture was taken for another query.

## Rules the deck follows

They come from `docs/submission/slides_outline.md`, "Rules for the whole deck". In short: English only; exactly 7 slides; no NASA logo or mission mark; a research exploration tool, not safety guidance; no prediction for untested conditions; results at 0 g and 1 g are not bounds for lunar or Martian gravity; scores are not compared across questions or environments; the lunar gap is always "no counted test at 30% oxygen or more and 70.3 kPa (10.2 psi) or less"; the third pile is "No record in PSI (listing of 14 November 2026)"; a file-to-test link is "two labels agree"; a value read from a raw file is "read from NASA's file, not adopted, not counted"; a query without a material ranks without a fuel comparison, so the worked example names a material; published results are quotations, their order is a fixed rule, nothing is computed from them; checked by code and AI sessions, reviewed by a person: 0.

## Captures

All captures are pictures of the team's own page as it was when `refresh.sh` last ran (15 November 2026; the new shell with the app bar, the summary tiles, five tabs and compact result cards; scoring config 1.5.2). They are taken from a build of `web/build.py` made in a scratch copy of the working tree and served on `127.0.0.1`, at 1440 CSS pixels wide and device scale 2, with the page's own fonts. They are not AI-generated images, and none shows a NASA logo. `img/captures.json` gives, for each one, what it shows, the address, the page elements, the named boxes that `build_deck.py` crops by, the size, the time, the scoring config and build time of the page, the fonts that were loaded, the SHA-256 of the picture, and what was changed only for the capture.

| Capture | On slide | Shows | Address (after the base) |
|---|---|---|---|
| `img/top.png` | 1 | The start page before a query: app bar, title, notice line, the input "What are you building, and where?" with its example buttons, the three cards Find, Compare, Interpret. The line that quotes the challenge statement is hidden for the capture, and the slide's caption says so. Retaken at 17:07 KST on 15 November 2026, after the page's input label changed at 16:57 | (none) |
| `img/cotton_top3.png` | 3 | Tab "Closest investigations" for "lunar habitat cotton fabric": the note that scores and order are the team's computation and the three compact result cards, whole, with "Details and sources" closed. The slide shows each card's head (name, match score, closest test configuration), cut above its dimension strip, which is too small to read at slide size; the reason and the largest gap of each card stand under it in words, from the scorer | `?q=lunar%20habitat%20cotton%20fabric&tab=closest` |
| `img/lunar_found.png` | not shown (checked) | Tab "What was found", first section "What NASA's experiments and documents report, question by question": the block "Flame spread and growth" with its first three quoted results. Not on slide 4 (too small to read there); the build checks that the page prints the example quotation of slide 4 in its group | `...&tab=found` |
| `img/lunar_piles_s1.png` | not shown (checked) | Tab "Where the data are": the block "Extinction conditions" with its three piles. Not on slide 5 (too small to read there; the slide names the tab in one line); the build checks that the page prints the counted extinction tests and the third pile's name | `...&tab=data` |
| `img/lunar_evidence_map.png` | 7 | Tab "Where the evidence stops": the evidence map (solid-fuel tests end at 22.2% oxygen; the input at 30%). The slide shows the map with its title line | `...&tab=stops` |
| `img/cotton_glance.png`, `img/cotton_read.png`, `img/lunar_piles_head.png`, `img/lunar_piles_p1.png` | not used | The summary tiles, the chips of "How your input was read", the header lines of the piles section and the block "Flammability limit". Taken from the same page for the team's use; slide 3 writes the reading of the input in words, and slide 5 draws the three piles as columns | as above |
| `img/assistant_recorded.png` | 6 | The section "Recorded answers of the SI assistant" on the start page after the recorded turn was replayed: the notice that the page runs no model, the question, the steps, the reading of the request, the answer with its citation numbers, the "Recorded on ..." label, the line of the checks, and the start of the panels. The slide shows the question and the answer with its label (see point 6 above) | (none); the recorded questions are typed into the assistant's box |

The charts (the two bars of slide 2, the table of slide 4, the two range strips of slide 5) are drawn by `build_deck.py` from the team's files; each slide says that they are the team's computation, not NASA's. The older captures of this folder, taken before the new shell, were removed from `img/`; the captures in `web/media/` of 14 November are not used.

The page was still being changed by another session while this deck was built (between two refreshes the label under a score changed from "team score" to "match score"; slide 3 takes that label from `web/app.js`). Run `refresh.sh` once more after the last change to the page.

## Fonts

The deck uses the page's own two fonts: Barlow Semi Condensed for headings and numbers and Atkinson Hyperlegible for text. Both are under the SIL Open Font License 1.1 and are logged in `compliance/SOURCES.md` (14 November, 11:15). They are loaded from Google Fonts with the same `<link>` as `web/index.html`, which `build_deck.py` copies from that file; the system font stack is only the fallback.

- `slides.html` needs the network for its fonts (`fonts.googleapis.com`, `fonts.gstatic.com`). Without it, a browser shows the fallback font and lines may wrap differently.
- `slides.pdf` embeds the fonts and is self-contained. Checked again on 15 November 2026 at 17:13 KST with `pdffonts docs/submission/slides.pdf`: five subsets, all embedded (BarlowSemiCondensed-Bold, -SemiBold and -Medium; AtkinsonHyperlegible-Regular and -Bold), and no system font. The build repeats this check each time (with `pdffonts` when it is installed, otherwise from the font names inside the PDF) and stops if any other font is embedded.
- While it builds the PDF, the previews and the captures, Chrome may reach `127.0.0.1` and those two hosts; every other host name is made unresolvable. The public page does the same when a visitor opens it.
- No font file is stored in the repository. The arrows on slide 6 are drawn as small SVG shapes, because the two fonts have no arrow character.

## Open points

Listed in the build's report to the pm session: the three assistant values of slide 6 (still placeholders), the last refresh after the page stops changing, and the differences from the outline.
