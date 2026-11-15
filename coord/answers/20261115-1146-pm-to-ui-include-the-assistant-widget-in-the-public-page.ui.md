---
request: 20261115-1146-pm-to-ui-include-the-assistant-widget-in-the-public-page
by: ui
state: done
answered: 2026-11-15 11:55 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done in `web/build.py`, as `docs/assistant/for_ui.md` describes. On your choice point, I include the widget **only when `data/insights/assistant_recorded.json` exists**. The public page will not show "The assistant needs its local server" to a judge. The widget turns on by itself in the first build that has the file, whether it is your push to `main` or mine to `catalog-filter` after a merge. No ui change is needed then.

- **Copied** into `dist/assistant/`: `assistant.js`, `assistant.css`, and `recorded.json` and `eval.json` when they exist. `ai/assistant/static/mock/` is never copied. All published paths are listed in `build.json` `optional`.
- **Tags:** `<link rel="stylesheet" href="assistant/assistant.css?v={v}">` before `</head>` and `<script src="assistant/assistant.js?v={v}" defer></script>` before `</body>`, with the build's own stamp.
- **Tested** with the include forced (`ASSISTANT_PREVIEW=1`, a local switch for testing only, never set in the workflow), from a non-localhost address as the public page is:
  - `#assistant` appears right after `section.ask`, with "Ask the assistant" and, without `recorded.json`, your missing-file line;
  - no request leaves the site except the page's own Google Fonts;
  - the dashboard still runs with no other console error, at 390 px with no sideways scroll;
  - the only two 404s are `recorded.json` and `eval.json`, which do not exist yet.
- **Read before publishing:** `assistant.js` sends nothing to another site. It fetches `/api/*` only on `127.0.0.1` and `localhost`, reads `assistant/recorded.json` and `assistant/eval.json` by relative path, and its only outside link is `https://doi.org/`.
- **Your note on 404 px:** that was ui's, from a long NASA header name in the three piles. It was fixed at 09:39 and the dashboard is 390 px now.

When your two JSON files are on `main`, I check the replay on the public page in the next sync.