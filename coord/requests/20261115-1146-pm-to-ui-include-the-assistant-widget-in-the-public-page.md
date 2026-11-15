---
from: pm
to: ui
opened: 2026-11-15 11:46 KST
needed_by: 14:30
closed: false
---
# Include the assistant widget in the public page build (two tags, four files; docs/assistant/for_ui.md)

## What I need

*AI-generated (Claude Code), pm role.*

In `web/build.py`: publish the assistant's page files and add its two tags, exactly as `docs/assistant/for_ui.md` describes (on `main` from the pm commit of 11:50).

1. Copy into `dist/assistant/`: `ai/assistant/static/assistant.js`, `ai/assistant/static/assistant.css`, and, when they exist, `data/insights/assistant_recorded.json` (as `assistant/recorded.json`) and `data/insights/assistant_eval.json` (as `assistant/eval.json`). Do not copy `ai/assistant/static/mock/`.
2. Add to `dist/index.html`: `<link rel="stylesheet" href="assistant/assistant.css?v={v}">` before `</head>` and `<script src="assistant/assistant.js?v={v}" defer></script>` before `</body>`.
3. List the four published paths as optional in `build.json`.

The script inserts its own `<section id="assistant">` after `main > section.ask` and changes none of your markup; every selector is prefixed with `#assistant` or `.as-`. On the public page it finds no server, runs no model and calls no API: it replays the recorded conversations, each marked as recorded, and typed text goes to your own search (`#q`, `#ask-form`).

**The two JSON files do not exist yet.** They are written when the evaluation and the recording finish on the merged data (expected by about 13:30). Until then the section shows the line "The assistant needs its local server (./run.sh). The dashboard below works without it." If you would rather not show that line in the meantime, add the include only when `data/insights/assistant_recorded.json` exists; that is your call.

To see it with a model: `./install.sh --check`, then `./run.sh` (the local server adds the same two tags when it serves the page, so nothing under `web/` is needed for the local install).

## Why

The challenge asks for an SI-powered dashboard, and the human lead decided at 09:33 that the product gets a conversational assistant with a local model (`coord/decisions.md`). Judges open the public page; without the include they see the assistant only if they install it.

## Until then

The assistant works in the local install. pm finishes the evaluation and the recording, and tells you in `coord/status/pm.md` when the two JSON files are on `main`.
