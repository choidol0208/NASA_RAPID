---
role: pm
updated: 2026-11-14 11:20 KST
state: working
blocked_on: none
---
Now: P3. Researching and designing the AI layer (language model plus retrieval, statistics and checks by code), then building `data/insights/`.

Done since last sync:
- GitHub Pages is ON (source: GitHub Actions). Branches `main` and `catalog-filter` may deploy to the `github-pages` environment. URL: https://choidol0208.github.io/NASA_RAPID/
- `contracts/README.md`: the shape of `data/insights/cards.json` and `scenarios.json` is now the one ui asked for (three source forms, `updated`, exact query strings, preset order).
- Closed the coverage request to data; the wording rules from its answer are in `coord/decisions.md`.
- New rule from the human lead: no AI model or service of Chinese origin (`AGENTS.md` section 6).

Next: first version of `data/insights/cards.json` on main (target 14:00), then `scenarios.json` for `iss` and `lunar_habitat`.

Published for others:
- `contracts/README.md`, `contracts/examples/*.example.json` (shape only, placeholders).

Notes for other roles:
- ui: deploy from `catalog-filter` until the freeze at 19:00, then switch the Pages trigger to `main` (`coord/decisions.md`).
- The model that writes product text will be a local open model (planned: OpenAI gpt-oss:20b, Apache-2.0, run with Ollama). Nothing calls a model when a page loads.
- data: `cards.json` is not written yet; D5 can start when it lands on main.
