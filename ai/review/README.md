# Review sheet for the AI-written card sentences

*AI-generated: this file, `pm_prereview.json` (written by an AI session of the pm role) and `review_sheet.csv` (written by code that an AI assistant, Claude Code, wrote) were made during the NASA Space Apps Challenge 2026 hackathon. The sentences with origin `model` were written by the language model gpt-oss:20b (OpenAI, run locally through Ollama). No row in the sheet has been reviewed yet unless its `verdict` column is filled in.*

## What the sheet is

`review_sheet.csv` lists every sentence the dashboard shows from `data/insights/cards.json` and `data/insights/scenarios.json`. It is written by `ai/apply_cards.py` (through `ai/apply_review.py`'s `write_sheet`) and read back by `ai/apply_review.py`. Rebuild everything, in order and with no model call, with `python3 ai/build_all.py`. A sentence removed through `pm_prereview.json` (below) is not in the sheet.

| origin | what it is | what the reviewer checks |
|---|---|---|
| `model` | a summary sentence written by gpt-oss:20b. It passed the code gates of `ai/checks.py` (ids, exact quote, numbers, names, no advice or prediction wording, misconception linter, length, sources, modality, hedges) | Is the sentence faithful to the cited PSI sentences? Does an objective, hypothesis or plan still read as one, with its hedge words? |
| `quote` | a verbatim NASA sentence with its field label (a key point, or the quoted summary of a card that shows no model text) | Relevance only: is this a sensible sentence to show for this record? |
| `template` | a sentence filled by team code from counts (frames, need statements, gaps, result notes) | Wording only: could a reader take it as a verdict, a prediction or a claim the counts do not support? |

Rows are ordered: model sentences first, lowest `lexical_support` first (a rough share of the sentence's content words found in its cited sentences; it only orders the work), then quotes, then template text. Every model sentence is reviewed; this is not a sample.

`cited_text` shows each cited PSI sentence as `[ID] <field label> "<text>"`. The sentence's own bracket, for example `(PSI-25 record: objective)`, is the source the page prints after it.

## How to fill it in

Fill only these columns: `verdict`, `modality_kept`, `reviewer_kind`, `reviewer_role`, `note`. Leave every other column as it is. `second_opinion_score` stays empty (no fact-check model is used; decision 11/14 13:05).

- `verdict` for a `model` row: `supported` (everything the sentence says is in the cited sentences), `partly` (some of it is not, or a qualifier or comparison was lost), `not` (wrong or unsupported).
- `modality_kept` for a `model` row: `yes` or `no`. `no` when an objective, hypothesis or planned approach reads as a result or finding, or a hedge word (may, could, expected, ...) of the source was dropped.
- `verdict` for a `quote` row: `relevant` or `not_relevant`. For a `template` row: `wording_ok` or `wording_issue`. Leave `modality_kept` empty for both.
- `reviewer_kind`: `person` for a team member who read the row, `ai_session` for an AI session (for example the data role's session, board task D5). Never write `person` for a row an AI session read.
- `reviewer_role`: the team role of the reviewer (`pm`, `data`, `ui`, `human lead`). No names.
- `note`: why, when the verdict is not `supported`, `relevant` or `wording_ok`.

A row whose sentence text changes on a rebuild loses its verdict (rows are matched by `item` and `sentence_sha`); unchanged rows keep it.

## Reviewed removals before the review: `pm_prereview.json`

`ai/review/pm_prereview.json` lists model sentences that passed every code gate and were found wrong by the pm session before the review sheet is filled in. `ai/apply_cards.py` reads it on every build (also through `ai/apply_review.py` and `ai/build_all.py`):

- a listed sentence is dropped from its card, whatever the gates said;
- its slot in the summary shows, in its place and order, the NASA sentence it cited first, verbatim with its field label (for example `Stated hypothesis: "..."`); that sentence is not repeated as a key point;
- the card's `status` becomes `generated_partial` (or `fallback_quote` if no model sentence is left), `ai_generated` stays true only while a model sentence is shown, and the card lists the removal under `removed_before_review`;
- the removal is counted in `data/insights/quality.json` under `removed_before_review` (with `reviewer_kind` `ai_session_pm`), apart from the review: it is not part of `removed_by_review`, the verdict counts or the support rate, and it never sets `reviewed_by`. The page's "checked by a second AI session" label still comes only from the review sheet.

The file is a JSON list. Each entry has exactly these fields, all required and non-empty:

| field | value |
|---|---|
| `investigation_id` | the card, for example `PSI-159` |
| `sentence` | the exact text of the sentence as `data/insights/cards.json` shows it in `sentences[].text`, with its bracketed source (`... kinetics. (PSI-159 record: hypothesis)`); the text without the bracket also matches. Copy it from cards.json; do not retype it |
| `reason` | why it is removed: what the cited PSI sentence says and how the model sentence differs. Quote the record only in short phrases |
| `reviewer_kind` | always `ai_session_pm` (an AI session of the pm role). A person or the data role's session uses the review sheet instead |

To add an entry, append an object to the list, then run `python3 ai/build_all.py` (no model call). The build reports an entry that matches no sentence (`entries_matching_no_sentence` in `quality.json`); such an entry removes nothing, so check the text. A sentence is never reworded by an entry; it is only removed.

Entries of 14 November: four, written by a pm session that was stopped at about 14:55 while it was reading the sentences (PSI-159 sentence 1, PSI-26 sentence 0, PSI-99 sentence 1, PSI-117 sentence 1; each `reason` says what the cited record sentence says). All four match a shown sentence and are applied. The reading was not finished: the next pm step re-reads every model sentence and decides the list again (entries may be added or taken out); until then the four stand as written. For example, PSI-159 sentence 1: the record says testing "can demonstrate the following for the first time, contributing to an improved understanding of cool flame kinetics"; the model sentence made the improvement itself the first-time result.

## What happens to the verdicts

`python3 ai/apply_review.py` rebuilds the cards from the logged model output (no model call) and:

- removes every model sentence marked `not` or `partly`, or with `modality_kept` = `no`. Nothing is reworded. A card whose summary empties shows its NASA quote again (`status` `fallback_quote`, `ai_generated` false);
- writes the review into each remaining model sentence and sets the card's `reviewed_by` only when every model sentence of the card was reviewed. The card label then says "read by a hackathon team member" or "checked by a second AI session";
- writes `data/insights/quality.json`: sentences proposed, rejected by each gate, repaired, removed by review, shipped, cards by status, rows reviewed by a person and by an AI session (counted separately), verdict counts and the support rate (supported / reviewed, before removal, with n).

`python3 ai/apply_review.py --final` (pre-freeze sync) also reverts to its quote every card that still has an unreviewed model sentence, so no unreviewed model text is on the submitted site. Then run `python3 ai/check_all.py --final`.

`quote` and `template` verdicts are counted in `quality.json` but never change text: a `not_relevant` or `wording_issue` row is a request to the code that builds that text (`ai/build_baseline.py`, `ai/templates.py`).

Reviewed by hackathon team members or a second AI session, not by NASA or a combustion expert.
