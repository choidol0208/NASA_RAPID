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

## What the script does on the public page

- It finds no assistant server (the host is not `127.0.0.1` or `localhost`), so it runs no model and calls no API. It reads `assistant/recorded.json` and `assistant/eval.json` by relative paths, which also works under the `/NASA_RAPID/` prefix.
- It replays the recorded conversations. Each answer is marked "Recorded on {date} with the local language model (gpt-oss:20b) and replayed here; no model runs on this page."
- Text typed into its box goes to the dashboard's own search: it sets `#q` and submits `#ask-form`, and the chat says that no language model runs on the page.
- If `recorded.json` is missing, it shows "The assistant needs its local server (./run.sh). The dashboard below works without it."
- It inserts `<section id="assistant">` right after `main > section.ask`. It does not change the dashboard's markup. It reads `data/scenario_spec.json`, `data/scoring_config.json` and `data/needs.json` only to fill the editors of the reading chips, and only on the local install, since chips are not editable in recorded mode.
- It sends no request to another site. Every selector is prefixed with `#assistant` or `.as-`.

## Checks after the change

1. `python3 web/build.py`, then open `web/dist/index.html` through any static server that is not on `localhost`, or open the published site. The section "Ask the assistant" appears under the dashboard's input, and the recorded conversations are listed.
2. At 390 px wide, the section has no horizontal scroll. Note that the dashboard itself is 404 px wide at a 390 px viewport, with or without the assistant (measured in headless Chrome on 15 November 2026). The extra width comes from outside `#assistant`.
