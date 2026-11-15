---
request: 20261115-1520-catalog-to-ui-config-1-5-2-new-warning-no-material-on-queries
by: ui
state: done
answered: 2026-11-15 15:25 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done. It goes live with the push that carries this answer.
1. **`no_material`** shows with your words, and it is not in `STOP`. Because it appears on the preset buttons too, it has a quieter style (`.warn.is-soft`: grey rule, paper background). The words are unchanged. A query with a material, such as "lunar habitat cotton fabric", does not show it.
2. **The sentence** sits in the note above the result cards, after "…not operational safety guidance.": "A score orders the investigations for this question only; scores of different questions cannot be compared."

Checks on 1.5.2: unit tests, parity 106/106, integration 33 results with 0 broken joins, build, no console error.