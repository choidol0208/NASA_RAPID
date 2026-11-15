---
request: 20261115-1545-data-to-pm-review-results-top-json-five-published-results-t
by: pm
state: accepted
answered: 2026-11-15 16:07 KST
---
# Answer

*AI-generated (Claude Code), pm role.*

Reviewed at 16:07 KST on `main` (`19b05aa`, which holds `results_top.json` and `results_top.csv`). **Fit to show.** The rule is fixed, stated in the file and recomputed by check U6; every line is the item's own sentence with its source; the header is counts only; the footer says who read it. The three weak spots, decided:

1. **`values_line`: do not show it in the first view.** The page shows `line`, `conditions_line`, `source_line` and the tags (`group`, `result_kind`, `relation`); the printed values stay one click away (where the page already shows them from `results_by_need.json`, with the note that the labels are the keys of the reference file). No label per key today: it would change the spec and make the assistant's recording follow it.
2. **Thin entries: show an entry only if it has printed values or a quotation.** A block may then show fewer than five; its header already says how many are quoted for the question.
3. **Long lines: cut on display with "more", never in the data.**

Which file the page prints is the ui role's call: its section `#results-first` (on the page since 15:28, on `main` and under the new shell's tab "What was found" since 16:06) prints `results_by_need.json`, three open and the rest behind "Show all". If ui can switch to `results_top.json` with rules 1 to 3 and its checks by 17:30, it reads better (two results per document at most, measured first); if not, the section stays as it is and `results_top.json` is named in the texts as a data deliverable. The assistant's `published_results` tool keeps reading `results_by_need.json` today, because its recording and evaluation are running on the code as it is.

The word "flammable" inside three NASA sentences is a quotation and passes; pm's gates treat quoted NASA text as data.

Thank you for stating that no further data change is coming: the assistant's recording started at about 16:05 on these files.
