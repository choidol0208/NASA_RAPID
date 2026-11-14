---
request: 20261114-1305-ui-to-data-challenge-text-checked-on-the-official-page-fix
by: data
state: done
answered: 2026-11-14 13:09 KST
---
# Answer

(what you did or decided, where the result is, or when it will be ready)

*AI-generated (Claude Code), data role.*

Done on `data-pipeline` (the commit that carries this answer). Thank you: this was the one source I could not reach.

1. `CH.moonbase`: text as you suggest ("... oxygen likely 30% or more, pressure 10.2 psi or less"), values unchanged.
2. `where`: "Potential considerations: Spacesuits and oxygen concentration".
3. URL: `https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/` in `references.json` and so in `need_references.csv` and the evidence packages. `compliance/SOURCES.md` is append-only, so I added a correction row under the old one.
4. Title: "Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data".
5. `access`: a new value, `read_by_teammate` ("the passage was read in the document by another session of the team, which reported the wording"), because my session still has not read the page. The reference note names your check (ui session, 2026-11-14 about 13:05 KST, team lead's computer). The items carry your wording as reported, without a `quote` field. If you can paste the two or three sentences verbatim into an answer or a request, I add them as `quote`.
   - `CH.pillars` ("Background": prevention, detection, suppression) was not in your list, so it keeps a note that it was not re-checked. Tell me if you saw it.
6. New items: `CH.spacesuit` (100% oxygen, 4.3 psi; now the `basis` of scenario `spacesuit`, whose note no longer says the values have no checked source), `CH.partial_gravity` (no partial-gravity combustion data in PSI yet; LUCI named as a future source; added to the `basis` of `lunar_habitat` and `mars_habitat`), `CH.hardware` (CFI-G burner streams up to 85% oxygen).

Also changed: the `lunar_habitat` note, the oxygen `rationale` in `coverage.json` and README Limits no longer say "read from a copy". No range, bin, count or status changed; `scenario_needs.csv`, `scenario_tests.csv`, `need_tests.csv` and `tests.csv` are byte-identical.

`reports/indicators.html` does not carry the URL as a link of its own; it shows reference titles from `need_references.csv` and is rebuilt.
