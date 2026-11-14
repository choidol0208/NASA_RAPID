---
from: ui
to: data
opened: 2026-11-14 13:05 KST
needed_by: 15:00
closed: false
---
# Challenge text checked on the official page: fix URL, title, section and hedge of CHALLENGE-2026

*AI-generated (Claude Code), ui role.*

## What I need

The human lead asked ui to check the challenge statement against the official page, which data could not reach. ui opened it on 2026-11-14 at about 13:05 KST, from the human lead's computer. Please update `CHALLENGE-2026` in `pipeline/spec/references.json` (and the rows built from it in `data/pipeline/need_references.csv`, and `reports/indicators.html` if it carries the same text):

1. **Bound confirmed, with a hedge.** The official text says the Moon Base and pressurized rovers will be between spacesuit and Earth conditions: oxygen likely 30% or greater, pressure 10.2 psi or less. Suggested `CH.moonbase` text: "Moon Base and pressurized-rover atmosphere expected between spacesuit and Earth conditions: oxygen likely 30% or more, pressure 10.2 psi or less." Values unchanged.
2. **Section.** The numbers are under "Potential considerations", sub-heading "Spacesuits and oxygen concentration", not "Background". "Background" only says increased oxygen and reduced pressure, without numbers. Suggested `where`: "Potential considerations: Spacesuits and oxygen concentration".
3. **URL.** The official page is https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/ . The long URL in `references.json`, `need_references.csv`, `compliance/SOURCES.md` (row 14) and `reports/indicators.html` returns "Page Not Found".
4. **Title.** The official title is "Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data" ("SI" is the page's term, super intelligence), not "AI-Powered".
5. **Access.** `access` can change from `read_from_copy` to checked against the official page on 2026-11-14. The `note` and the "Still not verified" line in `coord/status/data.md` can drop the challenge item.
6. **Optional new items, same section of the page.**
   - Spacesuits run at 100% oxygen and 4.3 psi, against 14.7 psi at sea level. The scorer's `spacesuit` preset already uses 100% and 29.6 kPa.
   - "Partial-gravity data": the page says PSI holds no partial-gravity combustion data yet, and names LUCI as a future source. This supports the corrected warning.
   - "Hardware": the page says CFI-G burner streams reached up to 85% oxygen, which matches the `oxidizer_stream` rule.

## Why

The lunar-habitat scenario, the coverage bins (`coverage.json` cites `CH.moonbase`) and the demo story rest on this bound. A reviewer who follows the link should land on the page and find the sentence where we say it is.

## Until then

ui changed only its own text: the `lunar_habitat` and `spacesuit` preset `source` strings in `scoring/scoring_config.json` now name the section and carry the "likely". No values changed. Parity 61/61.
