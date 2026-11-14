---
request: 20261114-1056-pm-to-ui-publish-the-public-url-and-say-which-repository
by: ui
state: done
answered: 2026-11-14 11:16 KST
---
# Answer

## 1. Stack and URL (ready by 12:15)

- A static site in `web/`: plain HTML, CSS and JavaScript, no framework, no runtime dependency, no call to any paid service. Served by **GitHub Pages**, which does not sleep, so it stays up through judging.
- The ranking runs in the browser: a JavaScript port of `scoring/scorer.py` that reads the same `scoring/scoring_config.json` and `data/catalog/*.csv`. The deploy workflow first runs a parity check (`web/parity_check.py`): both implementations rank every validation scenario plus extra queries, and the deploy fails if any result differs. So the page shows exactly what `scoring.scorer.rank` returns, as decided at 11:10.
  - Why not Python in the browser (Pyodide): this session cannot reach npm or the CDN to test it, it adds about 10 MB to the first load, and it would depend on a CDN through January.
- Expected URL once Pages is on: **https://choidol0208.github.io/NASA_RAPID/**. I will write it into `coord/status/ui.md` when the first deploy is green.

## 2. Repository settings needed (pm has admin rights)

1. Settings → Pages → Build and deployment → Source: **GitHub Actions**.
2. Settings → Environments → `github-pages` → Deployment branches and tags: add **`catalog-filter`**. The workflow `.github/workflows/pages.yml` deploys from `catalog-filter` on every push. If you prefer deploying only from `main`, answer with that and I switch the trigger to `main` (the URL then updates after each integration).
3. Nothing else: no secret, no extra workflow permission. The workflow declares `pages: write` and `id-token: write` itself.

## 3. Model-written text: keep the draft shapes, with these specifics

Where the files are missing, the page shows "Not available yet" in that place.

`data/insights/cards.json` (one entry per investigation)
- `investigation_id` = PSI accession (`PSI-25`), as in the draft. The page joins it to `rank()` results through their `psi_accession` field.
- `summary`: at most 3 sentences. `key_points`: at most 4.
- `source` in one of three forms, so the page can turn each into a link: `PSI-25.objective` (a field of the PSI record JSON), `doi:10.xxxx/yyyy`, or `data/pipeline/tests.csv#FLEX-12` (file and test id). Several sources: an array.
- Add `updated` (ISO time). The page shows "AI-generated" and either "Reviewed by <name>" or "Not reviewed yet" from `reviewed_by`.

`data/insights/scenarios.json` (presets only)
- Write `iss` and `lunar_habitat` first (the demo), then `spacesuit` and `mars_habitat`.
- `query` must be the exact string the page passes to `rank()`: use `"ISS"`, `"lunar habitat"`, `"spacesuit"`, `"Mars base"`. The page computes the ranking live and places each `result_notes` entry next to the matching investigation (by PSI accession); a note whose investigation is not in the live top 3 is shown under "Other investigations".
- `needs`: one entry per need id (`P1`–`P4`, `S1`, `D1`, `D2`), sources in the same three forms.
- `gaps`: as drafted.

Arbitrary queries get no model-written text. The page shows the scorer's deterministic `why` and `main_gap` lines instead (board cut list, item 1).

## Update (2026-11-14 11:16 KST): done

- The skeleton is live at **https://choidol0208.github.io/NASA_RAPID/** (Actions run 43545276180 for commit fb02c26: tests, validation, parity and build green, deploy green).
- Thanks for switching Pages on. I follow the 11:20 decision: deploy from `catalog-filter` until the 19:00 freeze, then switch the trigger to `main`.
- This session cannot open github.io through its proxy, so the logged-out check of the live URL is still for a person (see my status).
