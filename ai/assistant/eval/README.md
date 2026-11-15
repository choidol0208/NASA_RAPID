# The assistant's question set

*AI-generated (Claude Code, builder C session of the pm role) on 15 November 2026 for the NASA Space Apps Challenge 2026 hackathon. Read by a person: none yet.*

`questions.json` is the fixed set of questions the assistant is measured on (`python3 -m ai.assistant.evaluate`). An AI assistant (Claude Code) wrote every question and every expected value. No person has read them yet, and no person wrote them.

## How the set was made

1. **Before any model run.** The questions and their expected readings were written from the build contract (`ai/assistant/DESIGN.md`) and the team's data files, before the assistant's model steps ran even once. `questions.sha256` holds the file's sha256. It was written when the set was final and before the first live run, and `evaluate.py` refuses to run when the file no longer matches it (unless `--allow-changed-questions` is given; the result then says `questions_changed_after_freeze: true`).
2. **Expected values come from the files, not from a run.** Each question's `source_of_truth` (under `_meta.annotations`) names where its expected values come from:
   - the preset names and aliases in `scoring/scoring_config.json` (for example "rover" is an alias of `lunar_habitat`);
   - the material keys in the same file (for example "paper" maps to `lampwick`, "foam" to `pyrell`);
   - the six fire-safety questions in `pipeline/spec/needs.json`;
   - the investigation names in `data/catalog/investigations.csv` and the acronyms in `data/insights/evidence.json`;
   - the test ids in `data/pipeline/tests.csv` and `data/pipeline/test_files.csv`;
   - the plan table (section 5), the needed fields (4.6) and the fixed texts (9.5) of `DESIGN.md`.

   One expectation was read from code output: q65 ("the second one" after q01) expects PSI-98, because `scoring.scorer.rank('lunar habitat cotton')` returned PSI-99, PSI-98 and PSI-20 on 15 November 2026.
3. **What the expectation is about.** An expected reading says what the user said, not what code adds afterwards. An oxygen or pressure value that comes from a preset is therefore counted as "not given". The scoring rules are listed in `_meta.scoring_rules`.

## What the set covers (74 questions)

| Group | Questions | What is checked |
|---|---|---|
| Objective 1: closest investigations for a crewed environment | q01-q10 | intent, environment, material; the plan |
| Objective 1: comparison of environments | q11-q14, q66 | the set of environments |
| Objective 1: what the recorded tests hold for a fire-safety question | q15-q17 | the question ids P1 to D2 |
| Objective 2: where the data are, raw files | q18-q26, q64, q68 | intent, environment, question, test ids |
| Objective 2: data for predictive modelling | q27-q34, q67 | intent, question; a request for data is not a request for a prediction |
| Objective 3: research behind fire-safety equipment | q35-q42 | the kind of equipment |
| Applications on Earth | q43-q45 | intent; a named project group resolves to its investigations |
| Explanations, help, out of scope | q46-q50, q73, q74 | intent and term; the out-of-scope notice |
| Vague requests that must lead to one clarifying question | q51-q53 | the turn ends with a question |
| Requests for a safety verdict | q54-q57 | the fixed refusal notice; no verdict wording in the answer |
| Requests for a prediction at conditions | q58-q60 | the fixed refusal notice |
| Questions the files cannot answer | q61-q63 | the "not in the team's files" notice |
| Follow-ups that start from an earlier answer (`after`) | q64-q68 | values carried as structured state |
| Instructions hidden in quoted text | q69-q72 | the reading is the user's question; a canary word must not appear |
| Not in English | 10 Korean, 3 Japanese, 4 Spanish | the same fields as in English |

Six entries have `example: true` and a `label`. The local page shows them as "Try one of these" buttons (`GET /api/examples`).

## Known weak points of the set

- An AI session wrote the set, from a contract that the same team's AI sessions wrote. It is a small check, not a benchmark.
- q20 and q25 ask for the raw files of one test and name no environment. The contract (4.6) says `where_data` needs an environment and asks for one. The expectation records the answer a user would want, so these two count as plan misses if the assistant asks.
- Some fields are left out of the scoring on purpose where two readings are both correct. Examples: the intent of a verdict question, and the environment of "a spacecraft", which is only a weak alias. Each case says so in its `note`.
- Five questions expect `asks_verdict` or `asks_prediction` to be false where a rule word or the oxygen rule fires: q07, q31, q45, q69 and q72. Examples are 34% oxygen in a request for the closest experiments, "predictive model", "fire safety" as a field, and a verdict inside a quoted injection. The pipeline as built sets a flag whenever the rule parser sees it, as a stated precaution in `request.agree`. These five therefore count as reading misses, and each such turn shows an extra notice; that cost is what they measure.
- The DESIGN.md contract asked for 24 to 30 questions, with a schema limit of 40. The pm task for this build asked for at least 48, and the task wins, so `evaluate.py` checks the task's coverage instead of the contract's.
