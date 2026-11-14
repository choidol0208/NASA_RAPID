# Review sheet for the AI-written card sentences

*AI-generated: this file, `pm_prereview.json` (written by an AI session of the pm role) and `review_sheet.csv` (written by code that an AI assistant, Claude Code, wrote) were made during the NASA Space Apps Challenge 2026 hackathon. The sentences with origin `model` were written by the language model gpt-oss:20b (OpenAI, run locally through Ollama). No row in the sheet has been reviewed yet unless its `verdict` column is filled in.*

## What the sheet is

`review_sheet.csv` lists every sentence the dashboard shows from `data/insights/cards.json` and `data/insights/scenarios.json` (column `shown` = `yes`), and keeps one row (`shown` = `no`) for each sentence that is not shown because of a verdict in the sheet (a model sentence marked `not`, `partly` or modality `no`, a quote marked `not_relevant`) or of `--final`, so that its verdict stays and the next build leaves it out again. It is written by `ai/apply_cards.py` and again by `ai/apply_review.py` (both through `ai/apply_review.py`'s `refresh_sheet`/`write_sheet`), from the cards as they are once the sheet's own verdicts are applied, and read back by `ai/apply_review.py`; `ai/check_all.py` (section `sheet`) fails when a shown sentence has no row with `shown` = `yes` or a row with `shown` = `yes` is not on the page. Rebuild everything, in order and with no model call, with `python3 ai/build_all.py`. A sentence removed through `pm_prereview.json` (below) is not in the sheet.

Why the sheet is written from the reviewed cards (fixed 14 Nov after an independent check at 17:10): the key points of a card are picked after the model sentences are removed (`ai/apply_cards.py` `assemble`: the first cited unit of each remaining sentence, then the baseline key points for fields not yet shown, then the model's `key_ids`). Removing a sentence by review therefore changes the key points, but the sheet used to be written by `ai/apply_cards.py` from the cards before the verdicts were applied, and `ai/apply_review.py` did not rewrite it. The sheet then listed quotes the page did not show (PSI-20 OBJ-3, PSI-23 IMP-2, PSI-62 IMP-3, PSI-69 IMP-2 and others) and missed some it did (PSI-20, PSI-23, PSI-62 and PSI-69 researchImpacts IMP-1, and the quoted summaries of PSI-22, PSI-23, PSI-101 and PSI-115, which had become `fallback_quote` cards).

| origin | what it is | what the reviewer checks |
|---|---|---|
| `model` | a summary sentence written by gpt-oss:20b. It passed the code gates of `ai/checks.py` (ids, exact quote, numbers, names, no advice or prediction wording, misconception linter, length, sources, modality, hedges) | Is the sentence faithful to the cited PSI sentences? Does an objective, hypothesis or plan still read as one, with its hedge words? |
| `quote` | a verbatim NASA sentence with its field label (a key point, or the quoted summary of a card that shows no model text) | Relevance only: is this a sensible sentence to show for this record? |
| `template` | a sentence filled by team code from counts (frames, need statements, gaps, result notes) | Wording only: could a reader take it as a verdict, a prediction or a claim the counts do not support? |

Rows are ordered: model sentences first, lowest `lexical_support` first (a rough share of the sentence's content words found in its cited sentences; it only orders the work), then quotes, then template text. Every model sentence is reviewed; this is not a sample.

`cited_text` shows each cited PSI sentence as `[ID] <field label> "<text>"`. The sentence's own bracket, for example `(PSI-25 record: objective)`, is the source the page prints after it.

## How to fill it in

Fill only these columns: `verdict`, `modality_kept`, `reviewer_kind`, `reviewer_role`, `note`. Leave every other column as it is (`shown` is written by the build). Rows with `shown` = `no` are not on the page; their verdict is what keeps them off it. `second_opinion_score` stays empty (no fact-check model is used; decision 11/14 13:05).

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

Entries of 14 November: four. A first pm session was stopped at about 14:55 while it was reading the sentences, so a second pm session started again from the beginning and read all 65 gated model sentences against the cited PSI record text. It removed four (PSI-26 sentence 0, PSI-99 sentence 1, PSI-117 sentence 2, PSI-159 sentence 1; each `reason` says what the cited record sentence says and how the model sentence differs) and kept 61. An independent check then compared every quote and number in the cards with the PSI records by its own code and read eight cards in full; it found nothing that changes a record's meaning and noted small wording losses that the review should look at (PSI-60 drops "ground", PSI-62 drops "On Earth", PSI-22 turns "investigates" into "investigated"; PSI-22, PSI-101 and PSI-159 give only the first of several objectives; PSI-101 sentence 2, PSI-115 sentence 1, PSI-47 sentence 0 and PSI-102 sentence 2 deserve a second look). None of the 61 sentences has a review verdict until the sheet is filled in.

## What happens to the verdicts

`python3 ai/apply_review.py` rebuilds the cards from the logged model output (no model call) and:

- removes every model sentence marked `not` or `partly`, or with `modality_kept` = `no`. Nothing is reworded. A card whose summary empties shows its NASA quote again (`status` `fallback_quote`, `ai_generated` false);
- writes the review into each remaining model sentence and sets the card's `reviewed_by` only when every model sentence of the card was reviewed. The card label then says "read by a hackathon team member" or "checked by a second AI session";
- writes `data/insights/quality.json`: sentences proposed, rejected by each gate, repaired, removed by review, shipped, cards by status, rows reviewed by a person and by an AI session (counted separately), verdict counts and the support rate (supported / reviewed, before removal, with n).

`python3 ai/apply_review.py --final` (pre-freeze sync) also reverts to its quote every card that still has an unreviewed model sentence, so no unreviewed model text is on the submitted site. Then run `python3 ai/check_all.py --final`.

### Quotes marked `not_relevant`

A quote row marked `not_relevant` by a reviewer is not shown on its card (rule of 14 Nov; matched by `item` and `sentence_sha`, so a row whose text changed hides nothing). Nothing is reworded: the NASA sentence is shown or not shown.

- A key point is dropped. No other sentence is chosen in its place, except that the existing pick rule goes on to its next candidate if it has one that is not itself marked (the baseline key point of a field not yet shown, then the model's `key_ids`). On 14 Nov this put PSI-20 `objective` OBJ-3 (`key_ids`; the place left by APP-1 was the fourth; its row kept its earlier verdict, `relevant`), PSI-21 `researchImpacts` IMP-1 (baseline key point; IMP-6 had marked the field as shown) and PSI-26 `objective` OBJ-5 (`key_ids`) on their cards; PSI-21 APP-1, PSI-23 HYP-1, PSI-68 HYP-1 and PSI-99 HYP-4 have no replacement. The PSI-21 and PSI-26 rows are new and have no verdict.
- The quoted slot of a sentence removed through `pm_prereview.json` uses the next unit that sentence cited, if one is quotable and not marked; otherwise the card shows no slot and its label says that the cited NASA sentence is not shown. PSI-159 sentence 1 cited only HYP-1, so PSI-159 shows no slot (`removed_before_review[].replaced_by` is `null`).
- A card never ends with an empty summary. If nothing else is left, a card falls back to its quoted summary by the existing rule; if that quote is itself marked, it stays shown and is listed in `quality.json` under `quotes_not_shown_by_review.kept_although_marked` (none on 14 Nov).
- A model sentence whose first cited unit is a marked key point stays (its own verdict decides); the card lists the unit under `hidden_by_review` and `ai/check_all.py` accepts the missing key point for that unit only (PSI-21 sentence 2, IMP-6).
- Each card lists what it leaves out under `hidden_by_review`; `quality.json` counts these under `quotes_not_shown_by_review`, apart from `removed_by_review`, the verdict counts and the support rate.

### Templates marked `wording_issue`

A `wording_issue` row is counted in `quality.json` and is a request to the code that builds the sentence (`ai/templates.py`, `ai/build_baseline.py`); the template is fixed, not one scenario, and the rewritten rows come back with no verdict. The four rows of 14 Nov were fixed so:

- `scenario:spacesuit:gap:5` (also `scenario:iss:gap:6`): the copied `not_covered` line of `pipeline/spec/needs.json` for `TB008.gaps` is now built by code (`gap_partial_gravity`): it speaks of the mapped tests (the count of `data/pipeline/tests.csv`) and says that the team's source mapping sets the gravity level per table, as a table constant and not from a column (`pipeline/spec/sources.json` `constants`); the build stops if a table with tests is not mapped to microgravity or reads gravity from a column.
- `scenario:mars_habitat:gap:5` (also `iss:gap:7`, `lunar_habitat:gap:7`, `spacesuit:gap:6`): the `3001.T6.2-3` line is built by code (`gap_monitoring_targets`): "Required" is dropped, the document is named from the cited reference item (its parent `NASA-STD-3001-V2`, NASA Spaceflight Human-System Standard), the gases are checked against the item, and "the mapped PSI tables record carbon monoxide and carbon dioxide only" is checked against the gas readings of `pipeline/spec/variables.json` that have a value in `tests.csv`.
- `scenario:spacesuit:note:PSI-68` and `note:PSI-62` (the template is used for every spacesuit note): the closing clause no longer speaks of "the results listed" and "the inverse flames among them"; it says only that no test in the mapped PSI tables has oxygen in the bin and that this investigation is listed for completeness. Where an investigation's table has inverse-flame tests, the note's own sentence before it already says so, with their count.

The data role's text in `pipeline/spec/needs.json` is unchanged (pm does not own it); the two lines are no longer copied as written.

Reviewed by a second AI session, or by a hackathon team member where a row says `person`. On 14 November every reviewed row was read by an AI session and none by a person.
