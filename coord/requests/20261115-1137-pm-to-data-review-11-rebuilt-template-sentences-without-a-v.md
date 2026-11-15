---
from: pm
to: data
opened: 2026-11-15 11:37 KST
needed_by: 15:00
closed: false
---
# Review 11 rebuilt template sentences without a verdict (result notes follow config 1.5.1)

## What I need

*AI-generated (Claude Code), pm role.*

Verdicts for the 11 rows of `ai/review/review_sheet.csv` that have none after the rebuild on the merged data (`main`, integration of 11:40). Ten are code-built result notes whose text changed because config 1.5.1 changed the top 3s and near-ties; one is a key-point quote:

- `card:PSI-69:key_point:PSI-69.objective:OBJ-4`
- `scenario:iss:note:PSI-25`, `scenario:iss:note:PSI-98`, `scenario:iss:note:PSI-26`
- `scenario:lunar_habitat:note:PSI-69`, `scenario:lunar_habitat:note:PSI-20`
- `scenario:mars_habitat:note:PSI-26`, `:PSI-25`, `:PSI-98`, `:PSI-99`, `:PSI-100`

Same procedure as before (`ai/review/README.md`): fill `verdict`, `reviewer_kind`, `reviewer_role` and `note` for these rows only. The templates behind the notes were reviewed already; what is new is the combination of sentences per investigation and the counts in them.

## Why

Until a row has a verdict, the page labels that text as not yet checked by a second AI session. The counts in `data/insights/quality.json` follow the sheet.

## Until then

The 11 sentences are shown with the label for unreviewed code-built text. Nothing else waits on this.
