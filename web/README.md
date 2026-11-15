# Fire Evidence Explorer (dashboard)

Live: https://choidol0208.github.io/NASA_RAPID/

*The code in this folder was written with an AI assistant (Claude Code, model Claude Opus) during the NASA Space Apps Challenge 2026 hackathon, under the team's direction. Each file says so in its first lines.*

A static web page. You describe a crewed environment ("ISS", "lunar habitat cotton fabric", "30% O2 at 10.2 psi"); the page shows which NASA PSI microgravity combustion investigations come closest, why, what their recorded tests can say about six fire-safety information needs, and where the recorded tests stop.

It is a research exploration tool. It is not operational fire-safety guidance and it is not endorsed by NASA. Scores, rankings, statuses and counts are the team's computation.

## How it works

| Part | File | Source of truth |
|---|---|---|
| Ranking | `scorer.js` | A JavaScript port of `scoring/scorer.py`. It reads the same `scoring/scoring_config.json` and `data/catalog/*.csv`. |
| Same answer as Python | `parity_check.py`, `parity_check.mjs` | Runs every validation scenario plus extra queries (106 in all at 15:40 KST on 15 Nov 2026) through both and fails on any difference. |
| Page | `index.html`, `style.css`, `app.js` | Renders the `rank()` output, `data/pipeline/capability_matrix.csv` (needs view, and ISS against lunar habitat from `scenario_needs.csv`), `data/pipeline/coverage_grid.csv` (coverage view) and, when present, `data/insights/*.json` (team and model-written text, labelled; the evidence map). |
| Build | `build.py` | Copies the page and the data files into `web/dist/` and records the commit, so every link to a source file points at the exact version the page reads. `tests.csv` and `scenario_tests.csv` are copied slimmed: only the columns the page reads, and only the two demo scenarios, values unchanged, with each test's line in the full file kept for links. |
| Deploy | `.github/workflows/pages.yml` | On every push to `catalog-filter` or `main`: unit tests, validation, integration check, parity, build, then GitHub Pages. |
| Three piles | `raw_piles.py` | Run by `build.py`: for the lunar habitat and the ISS, the header line, a bar per question and the three piles (in NASA's tables / in the archive, not in a table / no record in PSI), as the fixed sentences of `docs/raw_data_design/pile_wording.md` filled from the team's files; stops the build when fixture F1, a bar sum, the word scan or a slot fails. |
| Integration | `check_integration.py` | For representative queries, every top-3 result must reach its data: manifest entry and DOI, the experimental-table file, the catalog row the page links to, its rows in `capability_matrix.csv`, and the configuration's own tests in `tests.csv` (count equal, O2/pressure/flow inside the catalog range). It also checks that each scenario frame, shown as a lead and a folded rest, keeps all of its text. `--emit` writes what the page should show, for a browser comparison. |
| Captures | `capture_media.mjs` | Run by hand on the public page (`node web/capture_media.mjs <url> [folder]`, Playwright from `NODE_PATH`): the stills, the slide captures (slides 1, 2, 3, 5, 6 and 7 of `docs/submission/slides_outline.md`; slide 6 from `how.html`) and the demo GIF, into `web/media/`. `CAPTURE_ONLY=a.png,b.png` retakes only the named files. Captures of the team's own page, not AI-generated images. |
| Links | `check_links.py` | Run by hand before the freeze: every repository file the page links to exists; external pages answer (publishers that refuse scripts are listed to open by hand). |

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
