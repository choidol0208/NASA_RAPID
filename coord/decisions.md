# Decisions

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. Written by pm only. Newest at the bottom.*

| When (KST) | Decision | Why |
|---|---|---|
| 11/14 11:00 | Three roles, one branch each (`main`, `data-pipeline`, `ui`); pm integrates into `main`. | Sessions can work without waiting for each other, and a session that may push only to its own branch still takes part. |
| 11/14 11:00 | The data contract is what `pipeline/README.md` documents: the files in `data/pipeline/`, `data/psi/catalog/` and `pipeline/spec/`. | The pipeline already exists and keeps every value traceable to a source cell. Nothing is re-derived elsewhere. |
| 11/14 11:00 | The dashboard is a static site that reads committed files. Language models run when the files are built, not when a judge opens the page. | Judging runs into January; a page that calls a paid API at view time can break, and `AGENTS.md` section 8 leaves paid APIs inside the product undecided. |
| 11/14 11:00 | Ranking scores come from rules over pipeline outputs. A language model may write the explanation, never the number. | Same rule the pipeline follows; rankings must be reproducible and labelled as the team's computation. |
| 11/14 11:00 | Demo scenarios: `iss-class` (baseline) and `lunar-habitat` (O2 30% or more, 10.2 psi or less, per the challenge text). `pressurized-rover` only if time allows. | PSI has no partial-gravity data, so the contrast between a well-covered and a poorly covered atmosphere is the story. |
