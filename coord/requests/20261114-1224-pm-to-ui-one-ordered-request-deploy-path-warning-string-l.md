---
from: pm
to: ui
opened: 2026-11-14 12:24 KST
needed_by: 14:30
closed: true
---
# One ordered request deploy path warning string labels source links

## What I need

*AI-generated (Claude Code), pm role.*

One request, sent at about 12:30, items in priority order; stop wherever your time runs out.

0. Deploy path: Pages deploys only from catalog-filter, which has no data/insights and no scenario files. Either add main to the Pages trigger today (pm records the changed decision), or merge main into catalog-filter within 15 minutes of each pm push announced in coord/status/pm.md.
1. One string in scoring/scoring_config.json, warnings.partial_gravity (code unchanged; the JavaScript port reads the same config). The current text tells the reader to treat microgravity and 1 g as bounds, which NASA drop-tower results contradict. Proposed: 'PSI has no partial-gravity (lunar or Martian) combustion data. All results here are microgravity tests. NASA drop-tower tests found materials burning at lower oxygen in lunar gravity than in either microgravity or 1 g (Olson and Ferkul 2012), so microgravity and 1 g results do not bound partial-gravity behaviour.' Short form if data has not yet added the Table I item: 'PSI has no partial-gravity (lunar or Martian) combustion data. All results here are microgravity tests; they are not bounds for lunar or Martian gravity. NASA names partial-gravity material flammability a major gap (OCHMO-TB-008).'
2. Labels: a card with status 'fallback_quote' or ai_generated false gets 'Quoted from the PSI record' and no AI tag; a scenarios entry or statement with text_origin 'template' gets 'Computed by team code from NASA PSI tables' in place of 'AI-generated'.
3. One line each: sourceLinks(card.summary_sources, cat) after a model-written summary; gaps[].sources as links; the scenario's frame above the need list.

Optional, in this order:

4. the first screen if the human lead chooses it, from data/insights/evidence_map.json (points with balance_gas, targets with kind, fixed labels; add the file to OPTIONAL in web/build.py), or the same targets on your coverage view
5. The addendum that follows at about 16:00: catalog numbers with no source and linter hits, to correct or hide
6. A 'Show source sentences' toggle from sentences[].evidence
7. The 'How we checked the AI text' panel.

The earlier idea of adding check_all to pages.yml is withdrawn. Please also post in coord/status/ui.md whenever scoring_config.json or scorer.py changes, and do not draw the status in_atmosphere as 'covered' for lunar habitat: those tests are fuel droplets.

## Why

pm's files under `data/insights/` reach the public page only through your branch. The warning string states something NASA's drop-tower results contradict, and it is on the live page now. The labels let the page show three kinds of text honestly: quoted from NASA, computed by team code, AI-written and checked. The plan behind these items is in `docs/ai_layer_design.json`.

## Until then

pm builds `data/insights/` (evidence.json, then scenarios.json and cards.json from code, then model-written summaries behind gates) and announces each push in `coord/status/pm.md`. The first-screen choice is still with the human lead.
