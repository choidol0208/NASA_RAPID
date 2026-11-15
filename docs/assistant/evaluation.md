# How the assistant was checked

*AI-generated: written by `ai/assistant/evaluate.py --report` from `data/insights/assistant_eval.json` (generated 2026-11-15T18:28:38+09:00). Every number below is copied from that file by code. The question set and its expected readings were written by an AI session before the run; read by a person: none yet.*

Questions: 74 (`ai/assistant/eval/questions.json`, sha256 `f628f1732af1`). Model: gpt-oss:20b (f38aa0c53da5); Ollama 0.40.16. Run log: `ai/runs/assistant_eval_20261115-1636.jsonl`. Model calls made: 0; reused: 0. Complete: no, missing no_repeat.

Memory of the loaded model, as Ollama reported it after the run (GET /api/ps): 12.9 GB, of which 12.9 GB on the GPU; context length 16384.

## Arms

| Arm | What runs |
|---|---|
| `single_call` | the rule reading, the plan and the tools, then one model call that reads and answers; no repeated reading, no gates, no checker |
| `full` | every step: two readings and the rule parser, plan, tools, write, code gates, one repair, model checker, template fallback |
| `no_repeat` | full without the second reading and the agreement |
| `no_gates` | full with the code gates in report mode only and no repair |
| `no_checker` | full without the model checker |

## Results

| Measure | `single_call` (74 q) | `full` (74 q) | `no_gates` (38 q) | `no_checker` (38 q) |
|---|---|---|---|---|
| Reading accuracy (scored fields) | 84% | 94% | 93% | 93% |
| Values invented where none was given | 1 | 1 | 0 | 0 |
| Plan equals the expected tools | 66% | 83% | 83% | 83% |
| Clarifying question when one is needed | 0 of 3 | 3 of 3 | 2 of 2 | 2 of 2 |
| Clarifying question when none is needed | 0 | 4 | 3 | 3 |
| Verdict and prediction requests declined | 0 of 7 | 6 of 7 | 2 of 2 | 2 of 2 |
| 'Not in the files' said when it should be | 0 of 3 | 1 of 3 | 0 of 1 | 0 of 1 |
| Injected canary kept out of the answer | 3 of 4 | 4 of 4 | 1 of 1 | 1 of 1 |
| Model sentences shown | 231 | 124 | 95 | 83 |
| Model sentences citing a fact of the turn | 96% | 100% | 100% | 100% |
| Numerals not in the cited facts | 36 | 0 | 3 | 0 |
| Sentences with verdict or advice wording | 23 | 0 | 1 | 0 |
| Quotation, name, language errors | 0, 49, 0 | 0, 0, 0 | 0, 6, 0 | 0, 0, 0 |
| Sentences removed / repaired / checker 'no' | 0 / 0 / 0 | 99 / 4 / 20 | 18 / 0 / 15 | 48 / 14 / 0 |
| Fallbacks to the team-code answer | 15 of 73 | 17 of 61 | 3 of 31 | 5 of 31 |
| Seconds per turn (median, max) | 22.18, 46.59 | 50.74, 94.38 | 54.04, 81.45 | 46.02, 81.73 |
| Model calls per turn (mean, max) | 0.81, 1 | 3.45, 4 | 3.39, 4 | 3.16, 4 |

The arms `no_repeat`, `no_gates`, `no_checker` ran on a fixed random 50% of the questions (38 questions, seed 20261115, with the questions a picked follow-up needs), because every arm on every question would not have fitted the time before the deadline. The second table scores every arm on that same part of the set.

| Measure | `single_call` (38 q) | `full` (38 q) | `no_gates` (38 q) | `no_checker` (38 q) |
|---|---|---|---|---|
| Reading accuracy (scored fields) | 80% | 93% | 93% | 93% |
| Values invented where none was given | 0 | 0 | 0 | 0 |
| Plan equals the expected tools | 64% | 83% | 83% | 83% |
| Clarifying question when one is needed | 0 of 2 | 2 of 2 | 2 of 2 | 2 of 2 |
| Clarifying question when none is needed | 0 | 3 | 3 | 3 |
| Verdict and prediction requests declined | 0 of 2 | 2 of 2 | 2 of 2 | 2 of 2 |
| 'Not in the files' said when it should be | 0 of 1 | 0 of 1 | 0 of 1 | 0 of 1 |
| Injected canary kept out of the answer | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| Model sentences shown | 117 | 54 | 95 | 83 |
| Model sentences citing a fact of the turn | 97% | 100% | 100% | 100% |
| Numerals not in the cited facts | 13 | 0 | 3 | 0 |
| Sentences with verdict or advice wording | 13 | 0 | 1 | 0 |
| Quotation, name, language errors | 0, 32, 0 | 0, 0, 0 | 0, 6, 0 | 0, 0, 0 |
| Sentences removed / repaired / checker 'no' | 0 / 0 / 0 | 62 / 3 / 9 | 18 / 0 / 15 | 48 / 14 / 0 |
| Fallbacks to the team-code answer | 9 of 38 | 12 of 31 | 3 of 31 | 5 of 31 |
| Seconds per turn (median, max) | 22.25, 46.59 | 50.56, 94.38 | 54.04, 81.45 | 46.02, 81.73 |
| Model calls per turn (mean, max) | 0.76, 1 | 3.42, 4 | 3.39, 4 | 3.16, 4 |

Over 74 questions, the full pipeline read 94% of the scored request fields as expected, and the single-call baseline 84%. Of the model-written sentences shown, 100% in the full pipeline and 96% in the baseline cite a fact of the turn. Numerals not found in the cited facts: 0 in the full pipeline and 36 in the baseline; sentences with verdict or advice wording: 0 and 23. Full turns took a median of 50.74 s, with a mean of 3.45 model calls; 17 of the 61 turns that reached the writing step fell back to the team-code answer.

## Reading accuracy per field

| Field | `single_call` | `full` | `no_gates` | `no_checker` |
|---|---|---|---|---|
| `asks_prediction` | 7 of 10 | 9 of 10 | 4 of 4 | 4 of 4 |
| `asks_verdict` | 9 of 9 | 9 of 9 | 2 of 2 | 2 of 2 |
| `environment.o2_pct` | 10 of 12 | 11 of 12 | 4 of 4 | 4 of 4 |
| `environment.preset` | 34 of 37 | 36 of 37 | 18 of 19 | 18 of 19 |
| `environment.pressure_kpa` | 6 of 6 | 6 of 6 | 4 of 4 | 4 of 4 |
| `environments` | 3 of 5 | 4 of 5 | 3 of 4 | 3 of 4 |
| `equipment` | 8 of 10 | 9 of 10 | 4 of 5 | 4 of 5 |
| `intent` | 50 of 65 | 61 of 65 | 34 of 36 | 34 of 36 |
| `investigations` | 4 of 5 | 5 of 5 | 2 of 2 | 2 of 2 |
| `item.material` | 21 of 23 | 23 of 23 | 10 of 10 | 10 of 10 |
| `questions` | 19 of 19 | 19 of 19 | 12 of 12 | 12 of 12 |
| `term` | 0 of 4 | 1 of 4 | 1 of 3 | 1 of 3 |
| `tests` | 2 of 2 | 2 of 2 | 1 of 1 | 1 of 1 |

## How to read these numbers

- A small question set written by an AI session of the team; not a benchmark.
- The gates that measure the answers are also part of the full pipeline.
- The checker is the same model; its verdicts are not independent.
- Timings are from one Apple M4 Pro with 48 GB.
- In `full` the code gates also remove sentences, so `full` shows close to zero on the gate measures by construction. The comparison that says something is with `single_call` and `no_gates`.
- Gate measures count model-written sentences only; sentences put together by team code from the facts are counted apart (template sentences).
