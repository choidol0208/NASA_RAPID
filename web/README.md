# Fire Evidence Explorer (dashboard)

Live: https://choidol0208.github.io/NASA_RAPID/

*The code in this folder was written with an AI assistant (Claude Code, model Claude Opus) during the NASA Space Apps Challenge 2026 hackathon, under the team's direction. Each file says so in its first lines.*

A static web page. You describe a crewed environment ("ISS", "lunar habitat cotton fabric", "30% O2 at 10.2 psi"); the page shows which NASA PSI microgravity combustion investigations come closest, why, what their recorded tests can say about seven fire-safety information needs, and where the recorded tests stop.

It is a research exploration tool. It is not operational fire-safety guidance and it is not endorsed by NASA. Scores, rankings, statuses and counts are the team's computation.

## How it works

| Part | File | Source of truth |
|---|---|---|
| Ranking | `scorer.js` | A JavaScript port of `scoring/scorer.py`. It reads the same `scoring/scoring_config.json` and `data/catalog/*.csv`. |
| Same answer as Python | `parity_check.py`, `parity_check.mjs` | Runs 61 queries (the 22 validation scenarios plus 39 more) through both and fails on any difference. |
| Page | `index.html`, `style.css`, `app.js` | Renders the `rank()` output, `data/pipeline/capability_matrix.csv` (needs view), `data/pipeline/coverage_grid.csv` (coverage view) and, when present, `data/insights/*.json` (model-written text, labelled). |
| Build | `build.py` | Copies the page and the data files into `web/dist/` and records the commit, so every link to a source file points at the exact version the page reads. |
| Deploy | `.github/workflows/pages.yml` | On every push to `catalog-filter`: unit tests, validation, parity, build, then GitHub Pages. |

No language model runs in the page. No paid service, API key or server is involved; nothing is called on page load except the page's own files and Google Fonts.

## Run it locally

```
python3 web/build.py
cd web/dist && python3 -m http.server 8000
# open http://localhost:8000/?q=lunar%20habitat
```

Checks before a change to the ranking:

```
python3 -m unittest scoring.test_scorer
python3 validation/run_validation.py
python3 web/parity_check.py        # needs Node.js 18 or later
```

## Links

`?q=<query>` opens the page with that query, for example `?q=ISS` and `?q=lunar%20habitat` for the demo.

## Sources and licences

Data: NASA Physical Sciences Informatics (CC0-1.0 where the record states it; each result links its PSI page and dataset DOI). Fonts: Atkinson Hyperlegible and Barlow Semi Condensed (SIL Open Font License 1.1, served by Google Fonts). Deploy: GitHub Actions (MIT). The full list is in `compliance/SOURCES.md`.
