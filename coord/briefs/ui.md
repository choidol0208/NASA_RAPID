# Brief: ui role

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. Written by pm.*

You build the dashboard and put it on a public URL. The data is already in the repository. Text written by language models (cards, scenarios) arrives during the afternoon; until then you build against the examples.

## Start here

1. Check out branch `ui` and write `ui` into `.role` at the repository root.
2. Read `AGENTS.md` (all of it: it holds the competition rules), `coord/README.md`, `coord/board.md` and `contracts/README.md`.
3. `python3 scripts/coord.py brief`, then answer what is in your inbox.
4. Begin with U1.

## You own

`web/` and `.github/`. Your branch is `ui`. You decide the stack and the output format of every screen.

## Tasks

| Id | What | Due (KST) |
|---|---|---|
| U1 | Choose the stack, deploy a skeleton to a public URL, write the URL and the stack in your status | 12:00 |
| U2 | Catalog and Investigation screens on real data | 14:00 |
| U3 | Scenario and Coverage screens | 17:00 |
| U4 | Source links, labels, narrow screens | 19:00 |
| U5 | Screenshots and one GIF of the scenario flow in `web/media/` | 21:00 |

## The four screens

- **Catalog**: the 24 investigations, filterable by fire-safety pillar (prevention, detection, suppression), fuel phase, flight or ground, hardware. Data: `data/psi/manifest.json`, `data/psi/catalog/`, later `data/insights/cards.json`.
- **Investigation**: one investigation: objective, fuels, range of conditions tested, what was varied and measured, publications with DOI, related investigations, link to its PSI page.
- **Scenario**: pick `iss-class` or `lunar-habitat`. Show the ranked investigations with the score breakdown, then for each of the seven needs the evidence level, the statement and its sources, then the gaps. Data: `data/insights/scenarios.json`, `pipeline/spec/needs.json`, `data/pipeline/capability_matrix.csv`.
- **Coverage**: a grid of oxygen concentration against pressure, one panel per fuel phase, each cell showing how many tests exist, with the scenario's range drawn over it. Tests with no recorded pressure get their own "not recorded" column; never place them at an assumed pressure. Data: `data/pipeline/tests.csv`.

Switching between the two scenarios on the Coverage screen, so the grid goes from well covered to mostly empty, is the moment the demo is built around.

## Rules that shape the screens

- Everything visible is in English.
- Every number and statement links to its source: the PSI investigation page (`https://psi.nasa.gov/physci/repo/data/investigations/PSI-<n>`), a DOI, or the source file and row from `values_long.csv`.
- Text with `ai_generated: true` carries a visible label, and shows whether it was reviewed (`reviewed_by`).
- Rankings, scores, evidence levels and counts are the team's computation. Say so on the page, next to them.
- A footer or About line states that this is a research exploration tool and not operational safety guidance.
- No NASA logo or mission insignia, and nothing that suggests NASA endorsement.
- Static site: no server, no API key in the page, no call to a paid service when the page loads.
- Before adding a dependency, font or icon set, check its license (OSI-approved, CC0 or public domain) and add a row to `compliance/SOURCES.md` at that moment.
- Code you generate gets a short "AI-generated" header comment, and your session gets a row in `compliance/AI_USAGE_LOG.md`.

## Until the real files exist

`contracts/examples/cards.example.json` and `contracts/examples/scenarios.example.json` have the final shape with placeholder values. Read them through one loader so swapping in `data/insights/*.json` is a path change. Never ship the placeholders: when the real file is missing, show "not available yet".

## When you need something

- A file in another shape, a missing field, an index: request to `data` or `pm`.
- A repository setting such as GitHub Pages: request to `pm`, whose session has admin rights.
- Deploy from the `ui` branch so you control when the site updates. pm merges `ui` into `main` on every sync.
