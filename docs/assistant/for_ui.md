# Adding the assistant to the public page (for the ui role)

*AI-generated (Claude Code, pm role, page builder) on 15 November 2026 for the NASA Space Apps Challenge 2026 hackathon. Read by a person: none yet.*

The assistant's page code is `ai/assistant/static/assistant.js` and `ai/assistant/static/assistant.css` (contract: `ai/assistant/DESIGN.md`, sections 11.2, 12 and 17). On the local install the server `python3 -m ai.assistant.server` adds it to `index.html` when it serves the page, so nothing under `web/` changes. The public GitHub Pages build needs the ui role to add it in `web/build.py`.

## The two lines in `dist/index.html`

Insert the first line before `</head>` and the second before `</body>`, with `{v}` the same version stamp that `web/build.py` already puts on `style.css` and `app.js`:

```html
<link rel="stylesheet" href="assistant/assistant.css?v={v}">
<script src="assistant/assistant.js?v={v}" defer></script>
```

## The files to copy into `dist/assistant/`

| Source | Published as | When |
|---|---|---|
| `ai/assistant/static/assistant.js` | `assistant/assistant.js` | always |
| `ai/assistant/static/assistant.css` | `assistant/assistant.css` | always |
| `data/insights/assistant_recorded.json` | `assistant/recorded.json` | when the file exists |
| `data/insights/assistant_eval.json` | `assistant/eval.json` | when the file exists |

List the four published paths in `build.json` `optional`. Do not copy `ai/assistant/static/mock/`: those files are test fixtures whose model sentences are hand-written examples.

## One input (changed 15 November, about 16:40 KST)

The page has one question box: the dashboard's own input (`#q` in `#ask-form`, and the app bar's `#shell-q`, which submits the same form). The assistant has no box of its own before a first answer. Where a server answers (live, no-model, mock), `assistant.js` changes the input's label and both placeholders to invite a question as well ("What are you building, and where? Or ask a question."); on the public page and without a server they keep the dashboard's own words from `index.html` ("What are you building, and where?"), because only the dashboard reads the input there.

- **A real submit of `#ask-form`** updates the dashboard at once, as before. In live and no-model mode the same text is also sent to the assistant, and `#assistant` (directly under the input) becomes "The assistant's answer": the steps as they run, the reading as chips, the answer with its citations and label, the panels beside it. In live mode a line says that the written answer takes about 1 to 2 minutes on this computer; the dashboard is usable meanwhile. Each submit of the input starts a new conversation.
- **After an answer** a follow-up box ("Ask a follow-up") is the last part of the conversation, under the suggestions "You could ask next". A follow-up continues the same conversation (the carried state); the earlier turn folds to its question (a click opens it again).
- **Before any question** the section is short: the title "The SI assistant", two sentences, the mode line and the example questions. On the start page the questions sit next to the page's own examples as one set ("Environments", "Questions"); a click puts the question into the input and submits it.
- **No turn nobody asked for**: an example environment, a tab, the back button and a page opened with `?q=` do not submit the form, so they start no turn. When the dashboard shows a request the conversation does not cover, the section offers one button, "Ask the assistant about this", next to the request in quotation marks. While a turn is running, a new request typed into the input updates the dashboard only; the offer then shows with its button off and the line "This can be asked when the current answer is done.", and the button turns on when the answer is in.
- **When the answer arrives**: for a turn asked from the input (a submit, an example question, "Ask the assistant about this", or a recorded question typed on the public page) the dashboard and the input stay on the visitor's own words; the answer's request (`dashboard.q`) is offered by its button "Show this on the dashboard below". For a follow-up, or a recording opened from the list, the dashboard follows the answer's request as before, but only while it still shows the request the turn started with, and without resetting the visitor's tab or scroll position (`data-quiet` on the form; see `web/SHELL.md`).
- **Recorded mode** (the public page): no model runs, so the input drives the dashboard only. The section is titled "Recorded answers of the SI assistant" and lists the recorded conversations to open, under the line "Recorded on {date} with the local language model (gpt-oss:20b) and replayed here; no model runs on this page." If the submitted text equals a recorded question, that recording is shown. No follow-up box and no example questions are shown.

No sentence of an answer, a label or a notice changed, and `ai/assistant/texts.py` was not edited. Words this change adds to the page: "What are you building, and where? Or ask a question." (label and app bar placeholder, where a server answers), the placeholder "e.g. moon cotton fabric, 30% O2 at 10.2 psi, or: where are the raw data for the ISS?", "Environments", "Questions", "The SI assistant", "The assistant's answer", "Recorded answers of the SI assistant", "Type what you are building, or a question, in the box at the top of the page. The written answer appears here.", "The written answer takes about 1 to 2 minutes on this computer. The dashboard below already shows this request.", "Ask a follow-up", "Ask the assistant about this", "This can be asked when the current answer is done." (the last only while a turn runs). The words that invite a question are set by `assistant.js` in live, no-model and mock mode only. No longer shown: "Ask the assistant", "Try one of these", "Your question", the old placeholder of the assistant's box, the sentence that told the two boxes apart, and the notice for text typed into the assistant's box on the public page (that box is not there any more). `ai/assistant/DESIGN.md` section 12 still describes the layout with two boxes.

## What the script does on the public page

- It finds no assistant server (the host is not `127.0.0.1` or `localhost`), so it runs no model and calls no API. It reads `assistant/recorded.json` and `assistant/eval.json` by relative paths, which also works under the `/NASA_RAPID/` prefix.
- It replays the recorded conversations. Each answer is marked "Recorded on {date} with the local language model (gpt-oss:20b) and replayed here; no model runs on this page."
- It shows no text box. Text typed into the page's input goes to the dashboard's own search, as without the assistant; if it equals a recorded question, that recording is also shown, marked as recorded.
- If `recorded.json` is missing, it shows "The assistant needs its local server (./run.sh). The dashboard below works without it."
- It inserts `<section id="assistant">` right after `main > section.ask`. It does not change the dashboard's markup. It reads `data/scenario_spec.json`, `data/scoring_config.json` and `data/needs.json` only to fill the editors of the reading chips, and only on the local install, since chips are not editable in recorded mode.
- It sends no request to another site. Every selector is prefixed with `#assistant` or `.as-`.

## Checks after the change

1. `python3 web/build.py`, then open `web/dist/index.html` through any static server that is not on `localhost`, or open the published site. The section "Recorded answers of the SI assistant" appears under the dashboard's input (on the start page, under the three cards), and the recorded conversations are listed.
2. At 390 px wide, the section has no horizontal scroll. Note that the dashboard itself is 404 px wide at a 390 px viewport, with or without the assistant (measured in headless Chrome on 15 November 2026). The extra width comes from outside `#assistant`.
