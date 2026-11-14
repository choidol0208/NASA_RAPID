# Decisions

*AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon. Written by pm only. Newest at the bottom.*

| When (KST) | Decision | Why |
|---|---|---|
| 11/14 11:10 | Three roles, one branch each: pm on `main`, data on `data-pipeline`, ui on `catalog-filter`. pm integrates into `main`. | The two role branches already exist. Sessions can work without waiting for each other, and a session that may push only to its own branch still takes part. |
| 11/14 11:10 | The data contract is what `pipeline/README.md` documents. The catalog and ranking contract is what `data/catalog/README.md` and `scoring/README.md` document. | Both already exist and keep every value traceable to a PSI source. Nothing is re-derived elsewhere. |
| 11/14 11:10 | Ranking is `scoring.scorer.rank`. A language model may explain a result, never produce or change a score. | Already the rule in `scoring/README.md` and in the pipeline; rankings must be reproducible and labelled as the team's computation. |
| 11/14 11:10 | Unreported atmosphere: the pipeline leaves the cell empty and counts on the Coverage view never fill it in. The scorer may use its flagged fallback (`scoring/README.md`, rule 2); any screen that shows such a result shows the `fallback` warning. | The two parts answer different questions. Counting needs recorded values only; finding the nearest experiment needs a comparison value, and it is shown as an assumption. |
| 11/14 11:10 | The dashboard must open from a public link without login, and keep working through judging (into January). It makes no call to a paid service when a page loads unless the human lead has decided so. How it is served is the ui role's choice. | `AGENTS.md` sections 7 and 8. |
| 11/14 11:10 | Demo story: the same tool asked about the ISS and about a lunar habitat (30% oxygen or more, 10.2 psi or less, per the challenge text). | PSI covers the first well and the second thinly; that contrast shows what the data can and cannot support. |
