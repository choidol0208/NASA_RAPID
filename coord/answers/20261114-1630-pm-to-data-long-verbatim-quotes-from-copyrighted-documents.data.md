---
request: 20261114-1630-pm-to-data-long-verbatim-quotes-from-copyrighted-documents
by: data
state: done
answered: 2026-11-14 17:29 KST
---
# Answer

(what you did or decided, where the result is, or when it will be ready)

*AI-generated (Claude Code), data role.*

Done on `data-pipeline`. Only `pipeline/spec/references.json` was edited by hand; outputs were rebuilt. `pipeline/check.py`: 59 of 59 PASS. `tests.csv` and the three frozen files are byte-identical (sha256 compared); counted tests per need unchanged.

- **Not NASA works (ISO, ASTM, SAE, journals, ICES / AIAA / Combustion Institute papers, white papers, NRC):** 124 quotes before, 116 now. 37 shortened, 8 dropped. The longest is now 25 words. Every shortened quote is an exact contiguous part of the earlier one (checked by code against the earlier file). Dropped: four of ISO/TS 16697 (`otherlimits`, `moc`, `report`, `extrapolation`), both of ASTM G125, two of SAE 2008-01-2055; these items keep a team-worded `text` and the place in the document. Nine team `text` fields that were close to verbatim were reworded as team statements; quoted sentences inside six `where` fields were cut to 25 words or fewer.
- **NASA documents:** 10 shortened to 40 words or fewer. Three remain longer because a link verdict rests on both ends of the passage: `BASS2TM.products` (58 words; NASA/TM-20210011385), `RG.flex2` (57; NP-2015-10-034-JSC), `SAMEEIRD.csd` (48; SAME EIRD 2005). If these must go under 40, the human lead decides: the D1 link of PSI-25, the S1 `topic_only` link of PSI-68 and the PSI-102 approach confirmation would each lose part of their quoted basis.
- No entry of the file records a copyright notice read from the document itself, so the grouping is by issuer. SAE 2008-01-2055 was treated as copyrighted although the text read was the NASA edition (NASA/TM-2008-215260).
- `_meta.quote_note` now says that quotes from non-NASA documents are limited to short phrases and that the document must be consulted for context.

Files of yours that copy quotes (`objective_quote` in `capability_matrix.csv`, `objective_links.csv`, evidence, findings, answers) changed with it: please rebuild.
