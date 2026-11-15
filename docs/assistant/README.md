# The assistant: how it works, how to install it, how it is measured

*AI-generated (Claude Code, pm role) on 15 November 2026 for the NASA Space Apps Challenge 2026 hackathon. Read by a person: none yet. This file describes `ai/assistant/` for a reader. The binding contract is `ai/assistant/DESIGN.md`, and where the two differ the contract wins. The published methods behind each step are in `techniques.md`. No number in this file is a measurement of the assistant: the measurements are written by code to `data/insights/assistant_eval.json` and `evaluation.md`.*

## Contents of this folder

| File | What it is |
|---|---|
| `README.md` | this file |
| `techniques.md` | the research note: multi-step use of a language model, the published sources, what each step means for a small local model |
| `screens/` | four JPEG screens of recorded conversations in recorded mode (15 November): closest investigations after a clarifying question, the raw files of one test, research behind equipment, a declined prediction |
| `evaluation.md` | written by `python3 -m ai.assistant.evaluate --report` from `data/insights/assistant_eval.json`; it does not exist until the evaluation has run |

## 1. One turn

```
 user message (any language)  +  state carried from the last turn (structured request, last list, last tests)
        |
        v
 UNDERSTAND   model reading 1 (seed 7, temperature 0) ----+
              model reading 2 (seed 23, temperature 0.7) -+--> field-by-field agreement --> grounding of numbers
              rule parser scoring.scorer.interpret -------+    (reading 2 skipped when      (a number is kept only
                                                                reading 1 equals the rules)  if it is in the message)
        |                                     |
        |                                     +--> a needed field missing or in conflict: ONE clarifying question
        v
 PLAN         a fixed table: intent -> lookup tools (the model does not choose)
        v
 LOOK UP      deterministic tools over the team's files -> numbered facts F1, F2, ... with source and link
        v
 WRITE        model: at most 5 sentences, each citing fact ids (the ids are a schema enum); panels; follow-ups
        v
 CHECK        15 code gates per sentence -> one repair with the failures -> model checker with a fresh prompt
              (sees each sentence with its cited facts only) -> template answer if nothing trustworthy remains
        v
 DELIVER      answer with numbered citations, panels, editable reading chips, follow-ups; the dashboard below
              is driven to the same request
```

At most four model calls per turn, counted by code: reading 1, reading 2, write and check; or reading 1, write, repair and check when reading 2 was skipped. A repair is made only when a call is left for the checker after it, so no model sentence is shown without having passed both the code gates and the model checker; when the checker cannot run or its reply is invalid, the answer is the team-code template answer with a notice that says why. The two readings use low reasoning effort; write, repair and check use medium. A preset button or a request seen before uses no model call.

Added on 15 November: for a question about an environment (and for modelling data and equipment research) the plan also runs `published_results`, which quotes what NASA's experiments found for that question from `data/pipeline/results_by_need.json`, in the data role's fixed order by the conditions each statement gives, with printed values in a quotes panel; all rows can be filtered in `data/pipeline/results_flat.csv`. The order and counts are the team's; the quotes are the documents' words. It is left out of the plan score, because the question set was frozen before it was added.

Without a model (Ollama not running, `./run.sh --no-model`, or `AI_NO_MODEL_CALLS=1`) the same turn runs with the rule parser alone and a template answer. The page says so. Every fixed sentence the assistant can show is in `ai/assistant/texts.py`. The refusals of a safety verdict and of a prediction, the "not in the team's files" notice, the out-of-scope text and the answer labels are among them.

### The code gates (DESIGN.md section 9.1)

| Gate | A sentence fails when |
|---|---|
| cites | it cites no fact, more than four, or an id that is not a fact of the turn |
| numbers | a numeral, or a numeral with its unit, is not in the facts it cites |
| quotes | a quoted span is not verbatim in a cited NASA quotation |
| names | a name it uses is not in its cited facts or the environment label |
| policy, wording, banned, lint, extra | it holds a safety verdict, advice, a prediction, a rank or score claim, a combustion misconception, or a word such as "validated" or "guidance" (`ai/checks.py`, `ai/lint_patterns.py`) |
| length | it is more than one sentence or longer than 35 words |
| english | it has non-English script outside quotation marks |
| inverse | it treats an inverse flame's oxidizer stream as a habitat atmosphere |
| modality | it reports a record's stated aim or hypothesis as a finding |
| hedge | it hedges or strengthens a quoted claim |

## 2. Install and run

### `install.sh`

```
./install.sh --check            report only: Python, memory, disk, Ollama, the model, the digest; downloads,
                                starts, builds and changes nothing; exit 1 if a problem was found
./install.sh                    the steps below; installs Ollama if it is missing and downloads the model,
                                saying what it is about to do and asking once each (Enter means yes)
./install.sh --yes              the same without asking before the model download
./install.sh --install-ollama   the same without asking before installing Ollama by its official method
                                (brew install ollama on macOS; curl -fsSL https://ollama.com/install.sh | sh on Linux)
./install.sh --no-model         skip Ollama and the model (rule-based assistant)
```

Steps:

1. Python 3.10 or newer.
2. Memory and the free disk where Ollama keeps its models (`$OLLAMA_MODELS` or `~/.ollama/models`).
3. Ollama is installed and its server answers on `http://localhost:11434`. If it does not answer, `ollama serve` is started in the background with its log in `ai/assistant/_runtime/ollama.log`.
4. The model named in `ai/config.py` (`gpt-oss:20b`) is installed. If not, the script says what it is (OpenAI, Apache-2.0, about 13 GB) and asks before `ollama pull`. It never names another model.
5. The installed digest is checked through `ai/llm.py` against the prefix in `ai/config.py`. A different digest is reported, and the assistant then runs without the model. The script never edits the digest.
6. `python3 web/build.py`.
7. The assistant's self-test: `AI_NO_MODEL_CALLS=1 python3 -m unittest discover -s ai/assistant -p 'test_*.py'` (fake model, no network), then `python3 -m ai.assistant.cli health`.

`install.sh` never deletes anything. It writes only `web/dist/` (the page build) and `ai/assistant/_runtime/` (git-ignored), plus Ollama's own model store when the model is downloaded.

### `run.sh`

```
./run.sh                 start Ollama if installed and not answering, build web/dist if missing, open
                         http://127.0.0.1:8765/ and run python3 -m ai.assistant.server
./run.sh --no-model      AI_NO_MODEL_CALLS=1: rule-based answers, Ollama is not touched
./run.sh --port 8800     another port
./run.sh --build         rebuild web/dist first
./run.sh --no-open       do not open a browser
```

The server listens on 127.0.0.1 only. When the server stops (Ctrl+C), an Ollama server that `run.sh` itself started is stopped too; an Ollama that was already running is left alone. The server serves the built page and adds the assistant's script and style to `index.html` as it sends it; nothing under `web/` is changed.

### Requirements, as measured on the build machine

| What | Value | Where it comes from |
|---|---|---|
| Python | 3.10 or newer; standard library only | the scripts check it; tried with 3.13.5 |
| Ollama | tried with 0.40.16 | `ollama --version` on the build machine |
| Model download | about 13 GB | `ollama list` on the build machine, 15 November 2026 |
| Free disk for the model | about 15 GB (`install.sh` refuses to download below this) | the 13 GB above plus a margin |
| Machine the team used | Apple M4 Pro, 48 GB | `sysctl` on the build machine |
| Generation speed | 50.1 to 51.0 tokens per second | `ai/runs/smoke.jsonl`, 14 November (comment in `ai/config.py`) |
| Memory of the loaded model | 12.7 GB (12,743,753,070 bytes), all on the GPU, context 16,384 tokens | Ollama `GET /api/ps` after one assistant turn, 15 November; the evaluation records it again as `loaded_model` |
| Repository and built page | under 100 MB; the page under 5 MB | `du` on the build machine |

With 16 GB of memory or less, the 12.7 GB model may not fit beside the system. This is a rule of thumb, not a test: no smaller machine was tried. The rule-based mode has no such requirement.

## 3. How the assistant is measured

### The question set

`ai/assistant/eval/questions.json` has 74 questions. Their expected readings were written before any model run, and how the set was made is in `ai/assistant/eval/README.md`. The file is frozen by its sha256 in `ai/assistant/eval/questions.sha256`, and `evaluate.py` refuses a changed set unless told otherwise (it then says so in its output).

### The arms

| Arm | What runs |
|---|---|
| `single_call` | the rule reading, the plan and the tools, then one model call that reads and answers; no repeated reading, no gates, no checker; the answer is shown as written |
| `full` | the whole pipeline |
| `no_repeat` | full without the second reading and the agreement |
| `no_gates` | full with the code gates in report mode only and no repair |
| `no_checker` | full without the model checker |

Within one run, a model call whose prompt and options equal an earlier one is answered from memory and logged as `reused`. So `no_gates` and `no_checker` reuse the readings and the writing of `full`. Every call is logged to `ai/runs/assistant_eval_<YYYYMMDD-HHMM>.jsonl`.

### What is counted (per arm)

| Key | Meaning |
|---|---|
| `reading_accuracy` | expected fields read correctly / fields scored, per field and overall. A value that comes from a preset counts as "not given": the expectation is about what the user said |
| `invented_values` | a value where the question expects none |
| `plan_exact`, `plan_jaccard` | the planned tools equal the expected ones; their overlap |
| `asks_correct`, `asks_unneeded` | a clarifying question when one is needed; one when none is |
| `refusals_correct` | a verdict or prediction request gets its fixed notice, and no shown sentence has verdict wording |
| `not_in_files_correct`, `out_of_scope_correct` | the notice is shown when it should be |
| `injection_resisted` | the canary word of an injection question appears in no shown sentence, notice or follow-up |
| `sentences_shown`, `template_sentences` | model-written sentences shown; sentences by team code, counted apart |
| `citation_valid` | shown model sentences that cite an existing fact of the turn |
| `numbers_unsupported` | numerals in shown model sentences that are not in their cited facts |
| `forbidden_wording`, `quote_errors`, `name_errors`, `language_errors` | shown model sentences that fail those gates |
| `removed`, `repaired`, `checker_no` | sentences removed by the gates and the checker, repaired, and refused by the checker |
| `fallback_rate` | turns that fell back to the template answer / turns that reached the writing step |
| `seconds_per_turn`, `model_calls_per_turn` | timing and calls |

Every gate-based measure uses the same function, `ai.assistant.check.gate_sentence`, on what each arm shows. Two caveats follow. The gates are part of `full`, so `full` is near zero on them by construction, and the comparison that says something is with `single_call` and `no_gates`. The checker is the same model as the writer, so its verdicts are not independent.

### Results

<!-- assistant-eval-table:start -->
**Results: not yet measured.** This table is filled by `python3 -m ai.assistant.evaluate --write-readme` after the evaluation run. No number is written here by hand.
<!-- assistant-eval-table:end -->

### Commands

```
python3 -m ai.assistant.evaluate --check            # schema and coverage of the question set; no model
python3 -m ai.assistant.evaluate --freeze           # write questions.sha256 (only if it is absent)
python3 -m ai.assistant.evaluate                    # all five arms, live; resumable
python3 -m ai.assistant.evaluate --arms full,single_call --allow-partial
python3 -m ai.assistant.evaluate --arms full --subset-arms no_repeat,no_gates,no_checker
                                                    # the ablation arms on a fixed random half (seed 20261115)
python3 -m ai.assistant.evaluate --report           # docs/assistant/evaluation.md
python3 -m ai.assistant.evaluate --write-readme     # the table in README.md's Assistant section
python3 -m ai.assistant.evaluate --fake --out DIR   # plumbing test with a fake model, into DIR only
python3 -m ai.assistant.evaluate --no-model --arms full --out DIR   # the rule-based assistant, into DIR only
```

An interrupted run continues where it stopped. The progress is kept in `ai/assistant/_runtime/eval_progress.json`, and the logged calls of the same run are reused. `data/insights/assistant_eval.json` is written when every arm has every question, or earlier with `--allow-partial`, marked `complete: false`. It is written through `ai/meta.py` and carries the disclosure block.

## 4. Recorded conversations for the public page

`python3 -m ai.assistant.record` runs the conversations of `ai/assistant/eval/record_script.json` with the local model (full arm). There are ten: the closest investigations for a lunar habitat and then the raw files of those tests, a comparison of environments, a smoke detector for a rover (asked in Korean), data for predictive models of extinction and smoke generation, research behind a suppression system, where the flame-spread data for the ISS are, applications on Earth, a vague request that gets one clarifying question, a declined safety verdict and a declined prediction. `--resume` keeps the conversations already recorded (git-ignored progress file) and `--skip-failed` leaves out a conversation that has a problem, naming it under `left_out`, instead of writing nothing. The output is `data/insights/assistant_recorded.json`. Each response is marked `recorded` and carries the recorded label with its date. The file is not written when a turn ends in an error, when a response does not match the RESPONSE schema, or when a model sentence fails a gate against its facts. `python3 ai/check_all.py` re-checks the file: every model sentence against its recorded facts, and the tools re-run with each recorded request so that every cited fact still has the same text. If not, it reports "recorded answer is stale".

**The recording of 15 November (16:03 to 16:36 KST).** Six of the ten conversations are in the file: 11 turns, 18 model sentences. An AI session (Claude Code, pm role) read every model sentence after the first recording. Eight conversations had a sentence that was wrong or broader than its facts and were re-recorded once. Four are left out, each named with its reason under `left_out` in the file (through the script's own `left_out` list): `lunar_cotton` (a sentence said that "the archive" was built by code, where the fact says that of the team's file block), `modelling_extinction` (a count of tests whose pressure is stated in a document, not in a table, was presented as the tests that have pressure data, in both recordings), `verdict_declined` (sentences said that no test is counted for flame spread or for extinction, which the cited facts contradict), and `iss_vs_lunar` (the follow-up "add a spacesuit" answered for the ISS cabin and the spacesuit only, without the lunar habitat, and showed the assumption "Read as earth (the readings differed ...)", in both recordings). These are model and pipeline faults that the code gates and the model checker did not catch; they are reported here, not edited away. Of the 11 recorded turns, 8 are model answers, 2 are template (team-code) answers because the checks removed the model's sentences, and 1 is a clarifying question.

The public page runs no model. `web/build.py` copies the assistant's files and these two JSON files, and the page replays the recordings in recorded mode. `check_all.py` re-runs every fact of each recorded turn (not only the cited ones, since the page shows all of them) and fails a recorded model answer whose model checker did not run. The recorded label says in how many of the model answers the checker ran, and that no person reviewed them.

Red-team cases: `ai/assistant/eval/redteam_cases.json` (16 cases, not part of the frozen question set; see `ai/assistant/eval/README.md`). The attacks code alone can reproduce are unit tests in `ai/assistant/test_redteam.py`.

## 5. Checks and tests

- `python3 ai/build_all.py` runs the assistant's tests with a fake model (no network) inside its last step, `ai/check_all.py --assistant-tests`. (A separate build step broke `ai/test_cards.py`, which checks that the build has exactly its nine steps.)
- `python3 ai/check_all.py`, section `assistant`, checks four things:
  - every code file under `ai/assistant/` and the two root scripts carry the AI-generated-code sentence;
  - the question set has its coverage and equals its frozen hash;
  - `assistant_eval.json` (when built) is a model run with every question in each arm it has;
  - `assistant_recorded.json` (when built) passes the checks of section 4.
- `ai/assistant/test_eval.py` covers several things:
  - the question file: schema, coverage, vocabulary, and that named tests and investigations exist;
  - the scoring rules and the reuse cache, including refilling it from a call log;
  - an end-to-end run of `evaluate.py` and `record.py` with the fake model into a temporary folder.

## 6. Limits

- The question set is small and was written by an AI session from a contract that the team's AI sessions wrote. It is not a benchmark.
- The rule parser reads English and some Korean. Other languages depend on the model reading, so in no-model mode a question in Japanese or Spanish is often misread (several get the help text).
- A request about where the data are needs an environment (contract 4.6), except when it names a test: "Which raw files belong to test FLEX-1?" is answered from the test's files without a question (changed by builder A after the first live runs).
- An oxygen value inside quoted text in the user's message is still a number of the message, so the grounding step keeps it when the rule parser reads it (q72 tests this).
