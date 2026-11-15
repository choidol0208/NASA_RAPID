# How the assistant uses a language model: multi-step techniques, sources and measurements

*AI-generated (Claude Code) on 2026-11-15 for the pm role. Research note behind the assistant in `ai/assistant/` (the contract is `ai/assistant/DESIGN.md`). Every source below was opened on 2026-11-15 unless it is marked "from memory, not opened". Read by a person: none yet. Nothing in this file is a result: the measured numbers are written by the evaluation to `data/insights/assistant_eval.json` and shown on the page.*

## Why this note exists

The team lead asked that the language model be used, and that it be used the way current assistants are built: in several small steps rather than one call, because accuracy is what matters. This note collects what is published about those steps, says what each one means for a small open model run locally (OpenAI gpt-oss:20b through Ollama, only through `ai/llm.py`) over a fixed set of facts drawn from the team's files, and says how the team measures whether each step helps.

Two facts about the setting shape every choice below.

1. **The model is small and knows little about this subject.** The gpt-oss model card reports, for gpt-oss-20b without browsing, an accuracy of 0.067 and a hallucination rate of 0.914 on SimpleQA, and 0.155 and 0.532 on PersonQA ([OpenAI, gpt-oss-120b and gpt-oss-20b Model Card, arXiv:2508.10925, Table 9](https://arxiv.org/html/2508.10925)). The assistant therefore never lets the model supply a fact. Code supplies every fact; the model only reads requests, chooses wording and checks wording.
2. **The answer space is closed.** The assistant answers from about two dozen PSI investigations and the team's derived tables. That makes most of the hard parts of open retrieval-augmented generation (finding the right passage on the web, ranking millions of documents) unnecessary, and it lets code check far more than it could in an open system.

## The turn, in one paragraph

One turn runs six steps (`ai/assistant/DESIGN.md` has the exact contract): **understand** (model, several readings plus the existing rule parser `scoring.scorer.interpret`, values validated by code; ask one clarifying question or state the assumption when the readings disagree or a needed value is missing), **plan** (code chooses the lookup tools from the structured request), **look up** (code tools return numbered facts, each with a template sentence, its numbers, its source file and link), **write** (model writes sentences, each citing fact ids, as JSON), **check** (code gates, then a second model pass as a checker; one repair with the failure as feedback; otherwise a template answer), **deliver** (answer with numbered citations, the panels that fit, the reading of the request as editable chips, follow-up questions). At most four model calls per turn; a preset or a repeated request is answered with no model call.

---

## Techniques

"Used here" describes the design in `ai/assistant/DESIGN.md`; whether the built code matches it is shown by the tests and the evaluation, not by this note. Each entry gives the idea in two sentences, the source with its link, how this project uses it (one line), how its effect is measured on the team's question set (metric names are defined in "How the effect is measured" below), and the main risk.

### 1. Structured outputs and constrained decoding

- **Idea.** The model's reply is forced to match a JSON schema, either by constraining which tokens may be sampled at each step or by validating and retrying. Constrained decoding turns "please answer in JSON" into a guarantee about the form of the reply, so code can read every field without guessing.
- **Sources.** Willard and Louf, *Efficient Guided Generation for Large Language Models*, 2023: generation as moves between states of a finite-state machine built from a regular expression or grammar ([arXiv:2307.09702](https://arxiv.org/abs/2307.09702)). Ollama's `format` field accepts a JSON schema and constrains the reply to it; Ollama advises also asking for JSON in the prompt and setting temperature 0 ([Ollama blog, Structured outputs, 2024-12-06](https://ollama.com/blog/structured-outputs); [Ollama API reference](https://github.com/ollama/ollama/blob/main/docs/api.md)). The harmony format guide says a response format written into the developer message shapes behaviour but does not guarantee adherence, so the schema must also be enforced during sampling ([OpenAI cookbook, The harmony response format](https://developers.openai.com/cookbook/articles/openai-harmony)). Anthropic documents the same mechanism for its own API as constrained decoding from a compiled grammar, with a supported subset of JSON Schema ([Claude docs, Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)).
- **Used here.** Every model step (understand, write, check) sends its schema as Ollama `format` through `ai/llm.py`, with closed `enum` lists for intents, presets, question ids and fact ids, so an invented id cannot be produced.
- **Measured by.** E2 (schema-valid reply on the first try) and R1, with `format_mode` set to `schema` against `prompt` (schema stated in the prompt only) as one ablation.
- **Risk.** Format restrictions can lower reasoning quality: Tam et al. found that requiring JSON or XML lowered reasoning performance, more so for stricter constraints ([*Let Me Speak Freely?*, arXiv:2408.02442](https://arxiv.org/abs/2408.02442)). Here the model reasons in its separate thinking channel before the constrained final reply, and the thinking text is discarded by `ai/llm.py`; whether that is enough is what the ablation tests. A valid form says nothing about whether the content is true.

### 2. Retrieval-grounded generation with citations

- **Idea.** The model answers only from passages supplied with the question and marks which passage supports each statement. Citations make the answer checkable, but published measurements show that models often cite a passage that does not support the statement.
- **Sources.** Gao et al., *Enabling Large Language Models to Generate Text with Citations* (ALCE), 2023: citation recall (is each statement entailed by the concatenation of its cited passages) and citation precision (is each citation needed), judged by an NLI model; on ELI5 "even the best models lack complete citation support 50% of the time" ([arXiv:2305.14627](https://arxiv.org/abs/2305.14627)). Anthropic's Citations feature chunks supplied documents into sentences (or caller-defined blocks) and returns the exact cited text; because the API extracts `cited_text` itself, citations are "guaranteed to contain valid pointers to the provided documents", and the page says the feature does not guarantee that every field has a citation ([Claude docs, Citations](https://platform.claude.com/docs/en/build-with-claude/citations)).
- **Used here.** The model cites fact ids from a closed list; the page draws the citation text and link from the fact itself, never from model output ("quote by reference"), which gives the same valid-pointer property locally.
- **Measured by.** G1 (citation coverage) and G3 (support and citation precision, by the checker model and by a person on a sample), full pipeline against the single-call baseline.
- **Risk.** A valid pointer is not a supporting pointer: a sentence can cite a real fact and still say more than it does. That gap is why steps 6 to 8 exist.

### 3. Decomposition: understand, plan, retrieve, write, verify

- **Idea.** A hard task is split into a chain of small steps, each with its own narrow prompt, with code checks between steps. Smaller steps are easier for a model to get right and easier for code to check.
- **Sources.** Zhou et al., *Least-to-Most Prompting*, 2022: split a problem into easier subproblems solved in order ([arXiv:2205.10625](https://arxiv.org/abs/2205.10625)). Yao et al., *ReAct*, 2022: interleave reasoning with actions that fetch outside information, which reduced hallucination in question answering and fact verification ([arXiv:2210.03629](https://arxiv.org/abs/2210.03629)). Anthropic's engineering post describes "prompt chaining" (a sequence of calls with programmatic checks between them), "routing", "parallelization" (sectioning and voting), "orchestrator-workers" and "evaluator-optimizer", and advises the simplest workflow that works before an autonomous agent ([Erik S. and Barry Zhang, *Building effective agents*, 2024-12-19](https://www.anthropic.com/engineering/building-effective-agents)).
- **Used here.** A fixed chain (understand, plan, look up, write, check) rather than a free agent loop: the plan is chosen by code from the structured request, so the small model never picks tools on its own.
- **Measured by.** The single-call baseline (one call that gets the facts and answers) against the full pipeline on R1, G1 to G4, A1 and E1.
- **Risk.** More steps cost latency (at about 50 tokens per second locally, each call matters) and errors in the first step propagate; an early misreading produces a well-cited answer to the wrong question. The editable chips on the page exist so the user can correct the reading.

### 4. Self-consistency: repeated sampling and agreement

- **Idea.** The same question is answered several times with different samples and the answer most of them agree on is kept. Agreement is also a signal: where samples disagree, the model is unsure.
- **Sources.** Wang et al., *Self-Consistency Improves Chain of Thought Reasoning in Language Models*, 2022: sample diverse reasoning paths and take the most consistent answer, with gains such as "+17.9%" on GSM8K as the abstract states it ([arXiv:2203.11171](https://arxiv.org/abs/2203.11171)). Anthropic lists "best-of-N verification" (run the same prompt several times and treat inconsistent outputs as a sign of hallucination) among its hallucination-reduction techniques ([Claude docs, Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)), and "voting" in *Building effective agents* (above).
- **Used here.** Only for the understand step, whose fields are closed values: two model readings with different seeds plus the rule parser vote field by field; free text is never voted on.
- **Measured by.** R1 and R2 with one reading against two readings plus the rule parser; E1 for the added calls.
- **Risk.** At temperature 0 with a fixed seed the readings can be identical, so the vote adds cost without information; the readings need a different seed and a small temperature, which the evaluation must record. Agreement between samples of the same model is not correctness: a shared misreading passes.

### 5. Asking a clarifying question under ambiguity

- **Idea.** When a request can be read in more than one way, asking one short question can do better than guessing. The hard part is deciding when to ask, because asking too often is also a failure.
- **Sources.** Zhang and Choi, *Clarify When Necessary: Resolving Ambiguity Through Interaction with LMs*, 2023: decide when to ask, what to ask and how to use the answer; an uncertainty estimate over possible user intents picks the cases that benefit most ([arXiv:2311.09469](https://arxiv.org/abs/2311.09469)). Anthropic's tool-use documentation notes that when a required parameter is missing, a model may ask for it or may infer a plausible value, and that asking "is not guaranteed, especially for more ambiguous prompts and for less capable models" ([Claude docs, Tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)).
- **Used here.** The decision to ask is made by code, not by the model: disagreement among the readings, or a value the chosen intent needs that is missing, triggers one question; otherwise the assistant states the assumption it made and shows it as a chip.
- **Measured by.** R2: on items marked ambiguous before any run, the share where the assistant asked or stated the assumption; on unambiguous items, the share where it asked needlessly.
- **Risk.** Disagreement between readings is only a rough stand-in for real ambiguity; a request every reading gets wrong in the same way is not caught.

### 6. Verification passes: chain-of-verification, a second model call as checker, entailment

- **Idea.** After a draft, separate checks ask whether each statement holds, ideally without letting the checker see the draft's reasoning. A checker that sees only the statement and its evidence is less likely to repeat the draft's mistake.
- **Sources.** Dhuliawala et al., *Chain-of-Verification Reduces Hallucination in Large Language Models*, 2023: draft, plan verification questions, answer them independently, revise; the "factored" variants that answer without seeing the draft beat the "joint" one (for example list precision on Wikidata questions 0.17 baseline, 0.29 joint, 0.36 two-step) ([arXiv:2309.11495](https://arxiv.org/abs/2309.11495); figures from the [HTML version](https://arxiv.org/html/2309.11495)). Honovich et al., *TRUE: Re-evaluating Factual Consistency Evaluation*, 2022: large NLI (entailment) models and question-generation-and-answering methods are strong, complementary checks of factual consistency ([arXiv:2204.04991](https://arxiv.org/abs/2204.04991)). Es et al., *Ragas*, 2023: faithfulness as the share of an answer's statements that an LLM judges supported by the context ([arXiv:2309.15217](https://arxiv.org/abs/2309.15217); definitions from the [HTML version](https://arxiv.org/html/2309.15217)). Anthropic suggests asking the model, after drafting, to find a supporting quote for each claim and retract claims it cannot support ([Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)).
- **Used here.** A second gpt-oss call with a fresh prompt sees one sentence and only the facts it cites (not the user's message or the other sentences) and answers yes or no with a reason, which is the factored, entailment-style form.
- **Measured by.** G3 and the count of sentences removed by the checker, with the checker switched off as one ablation; the checker's verdicts are compared with a person's on a sample.
- **Risk.** The checker is the same small model as the writer. Zheng et al. report position, verbosity and self-enhancement biases in LLM judges ([*Judging LLM-as-a-Judge*, arXiv:2306.05685](https://arxiv.org/abs/2306.05685)), and no NLI model is installed (no new dependency). So the checker can only remove sentences, never add or rewrite content, and its agreement with a person is reported rather than assumed.

### 7. Code-level checks: numbers, quotations, ids, forbidden claims

- **Idea.** Much of what a model can get wrong can be checked exactly by code: does every number in a sentence occur in the cited facts, is a quotation verbatim, does every cited id exist. Code checks are cheap, deterministic and cannot be talked out of their verdict.
- **Sources.** The team's own gates in `ai/checks.py` and word lists in `ai/lint_patterns.py` (ids, verbatim quotes, numbers with units, entities, forbidden phrasings), already used for the summary cards. Anthropic's *Demystifying evals for AI agents* describes code-based graders as "fast, objective, and reproducible" but brittle, to be combined with model-based and human grading ([Grace et al., 2026-01-09](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).
- **Used here.** Every written sentence must cite at least one fact, every number must appear in its cited facts, quotations must be verbatim, and no safety verdict, advice, prediction or "validated" may appear (reusing `ai/checks.py` and `ai/lint_patterns.py`); these gates run before the model checker.
- **Measured by.** G2 (share of sentences that pass the gates as first written) and G4 (forbidden-claim rate in delivered answers), with the gates switched off as one ablation.
- **Risk.** Gates catch the forms they know: a paraphrase that changes meaning without a new number or a listed word passes. That residue is what technique 6 and the human sample cover.

### 8. Repair loops with feedback

- **Idea.** When a draft fails a check, the failure is fed back and the model tries again. Repair helps when the feedback comes from outside the model; asking a model to find its own errors without such feedback is unreliable.
- **Sources.** Madaan et al., *Self-Refine*, 2023: generate, give feedback, refine, about 20% absolute better on average across seven tasks with GPT-3.5, ChatGPT and GPT-4, as the abstract states it ([arXiv:2303.17651](https://arxiv.org/abs/2303.17651)). Huang et al., *Large Language Models Cannot Self-Correct Reasoning Yet*, 2023: without external feedback, self-correction often fails and can make answers worse ([arXiv:2310.01798](https://arxiv.org/abs/2310.01798)). "Evaluator-optimizer" in *Building effective agents* (above).
- **Used here.** At most one repair call, whose feedback is the exact gate or checker failure for each failed sentence (external feedback, as in the existing cards pipeline's one repair call); if the repair still fails, the turn falls back to a template answer built from the facts.
- **Measured by.** Counts of sentences written, removed and repaired per turn (shown on the page), the fallback rate, and G3 with repair switched off as one ablation.
- **Risk.** A repair can trade one error for another or quietly drop the useful part of the answer; the repaired text goes through every gate again, and the count of repaired sentences is shown.

### 9. Abstention and refusal

- **Idea.** A model that is allowed, and told, to say "I don't know" or "I don't give that" produces fewer false statements. Abstention has its own failure, over-refusal of questions that could be answered.
- **Sources.** Wen et al., *Know Your Limits: A Survey of Abstention in Large Language Models*, 2024 ([arXiv:2407.18418](https://arxiv.org/abs/2407.18418)). Anthropic: "Allow Claude to say 'I don't know'" and "External knowledge restriction" ([Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)).
- **Used here.** Out-of-scope requests, safety verdicts and predictions for untested conditions are intents in the closed list, answered by code with a plain statement that the assistant does not give one and an offer of what it can show; when the tools return no fact, the answer says so and names what record would be needed.
- **Measured by.** A1: on items written as verdict-seeking, out-of-scope or with no record, the share correctly declined with an offer; on answerable items, the over-refusal rate.
- **Risk.** A request for a verdict phrased indirectly can be read as an ordinary question; the forbidden-claim gate (technique 7) is the second line.

### 10. Routing and caching so that simple requests need no model

- **Idea.** Classify the request first and send easy ones to a cheap path; cache answers to requests already seen. Most of the cost saving comes from not calling the large model at all when it adds nothing.
- **Sources.** Chen, Zaharia and Zou, *FrugalGPT*, 2023: prompt adaptation, LLM approximation and an LLM cascade matched the best single model with "up to 98% cost reduction" in their tests ([arXiv:2305.05176](https://arxiv.org/abs/2305.05176)). "Routing" in *Building effective agents* (above).
- **Used here.** Preset buttons and chip edits produce a structured request directly (no understand call); a request whose structured form was already answered is served from an in-memory cache; requests the rule parser reads completely and unambiguously can skip the model readings (an option the evaluation compares).
- **Measured by.** E1 (model calls and seconds per turn) and the cache hit rate on the repeated items of the question set; R1 for the requests answered without a model reading.
- **Risk.** A cache keyed on the structured request returns a stale answer if the team's data files change while the server runs; the design therefore keys the cache on the data files' build stamp as well.

### 11. Small contexts and carrying state instead of history

- **Idea.** Models use information at the start and end of a long input better than the middle, and every extra token competes for attention. Sending only the facts needed, numbered, and a compact state of the conversation keeps the prompt short and the model focused.
- **Sources.** Liu et al., *Lost in the Middle: How Language Models Use Long Contexts*, 2023 ([arXiv:2307.03172](https://arxiv.org/abs/2307.03172)). Anthropic's *Effective context engineering for AI agents* describes "context rot" as the window fills, advises "the smallest set of high-signal tokens", and describes compaction and structured notes kept outside the window ([Rajasekaran et al., 2025-09-29](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
- **Used here.** Each model call gets only its narrow instructions, the current structured state (not the raw chat history) and the numbered facts it needs, most relevant first.
- **Measured by.** Prompt size per call and E1, and R1 on the multi-turn items (follow-ups such as "and on the Moon?") that depend on the carried state.
- **Risk.** Whatever the structured state does not capture is forgotten; a follow-up that refers to something outside the state's fields will be misread. The multi-turn items test exactly this.

### 12. Prompt-injection resistance when quoting documents

- **Idea.** Text retrieved from documents can contain instructions, and a model may follow them as if the user had written them. Defences mark where outside text starts and ends, tell the model it is data, and limit what the model's output can do.
- **Sources.** Greshake et al., *Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection*, 2023 ([arXiv:2302.12173](https://arxiv.org/abs/2302.12173)). Hines et al., *Defending Against Indirect Prompt Injection Attacks With Spotlighting*, 2024: delimiting, datamarking and encoding of outside text; datamarking lowered attack success from about 50% to a few percent in their GPT tests, and they advise against relying on delimiters alone because an attacker can include them ([arXiv:2403.14720](https://arxiv.org/abs/2403.14720); details from the [HTML version](https://arxiv.org/html/2403.14720)). The gpt-oss model card reports a prompt-injection-hijacking score of 0.639 for gpt-oss-20b against 0.917 for o4-mini ([arXiv:2508.10925](https://arxiv.org/html/2508.10925), Tables 7 and 8), so this model needs the defence more than larger ones.
- **Used here.** NASA text reaches the model only inside marked fact blocks that the system prompt declares to be data; the model's output can only be sentences citing ids, panel names from a closed list and follow-up questions, so no instruction in a record can trigger an action; quotations are shown by code from the source, not retyped by the model.
- **Measured by.** S1: injection items in the question set place an instruction inside a fact text in an in-memory test copy (never in the team's files) and count how often the answer follows it, with the data markers switched off as one ablation.
- **Risk.** Datamarking (replacing spaces with a marker) would break the verbatim-quote gate, so only delimiting plus output restriction is used; that is weaker than the paper's best method, and the closed output schema is what carries most of the defence.

### 13. Reasoning effort per step

- **Idea.** Reasoning models can be told how long to think; more thinking helps hard steps and only adds delay on easy ones. Spending effort where it matters is an efficiency technique in its own right.
- **Sources.** gpt-oss supports low, medium and high reasoning effort, set in the system message ("Reasoning: high"); the model card reports for gpt-oss-20b on GPQA Diamond without tools 56.8 (low), 66.0 (medium) and 71.5 (high), with longer chains of thought at higher effort ([arXiv:2508.10925](https://arxiv.org/html/2508.10925), Section 2.5.2; [Hugging Face, openai/gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b)). Ollama exposes this as the `think` field; models that cannot turn thinking off use their lowest level when `think` is false ([Ollama docs, Thinking](https://docs.ollama.com/capabilities/thinking)). Anthropic documents the equivalent for its own models as a thinking budget or an effort setting ([Claude docs, Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)).
- **Used here.** `think='low'` for the understand and check calls (closed classification), `think='medium'` for the write call, all through `ai/llm.py`.
- **Measured by.** E1 and G3 with the write call at low against medium effort.
- **Risk.** Higher effort can also produce longer, over-confident chains of thought; the thinking text is never shown or stored (the harmony guide and the model card both say not to show it to users unfiltered).

### 14. Evaluation: faithfulness, citation quality, relevance, ablations

- **Idea.** A pipeline is measured by fixing a question set and the expected behaviour before any run, then scoring each answer on separate axes (is it supported, are its citations right, does it answer the question) and switching each technique off in turn. Without ablations, a multi-step pipeline can carry steps that cost time and add nothing.
- **Sources.** Ragas (faithfulness, answer relevance, context relevance, [arXiv:2309.15217](https://arxiv.org/abs/2309.15217)); ALCE (citation recall and precision, [arXiv:2305.14627](https://arxiv.org/abs/2305.14627)); Min et al., *FActScore*, 2023: split long answers into atomic facts and score the share supported by a knowledge source ([arXiv:2305.14251](https://arxiv.org/abs/2305.14251)); Anthropic: start with 20 to 50 tasks drawn from real failures, write tasks so that experts would agree on pass or fail, combine code, model and human graders, read transcripts ([*Demystifying evals for AI agents*](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)); Anthropic's research system post describes a rubric with factual accuracy and citation accuracy and starting from about 20 test queries ([Hadfield et al., *How we built our multi-agent research system*, 2025-06-13](https://www.anthropic.com/engineering/multi-agent-research-system)).
- **Used here.** A fixed question set with expected readings, expected behaviour (answer, ask, decline) and expected panels written before any run; the full pipeline, the single-call baseline and one ablation per technique; results in `data/insights/assistant_eval.json` (with the disclosure block from `ai/meta.py`) and on the page; run logs under `ai/runs/`.
- **Measured by.** All metrics below.
- **Risk.** A question set written by the same team that built the pipeline flatters it; the set is small, so differences of one or two items are noise and are reported as counts, not percentages alone.

---

## How the effect is measured

Metrics are computed by code over the fixed question set, except where a person's or the checker model's judgement is named. "Expected" always means written into the question set before the first run.

| Id | Metric | How it is computed |
|---|---|---|
| R1 | Reading accuracy | Per field (intent, preset or oxygen, pressure, gravity, flow, item, questions, investigations), share of items whose structured request equals the expected reading |
| R2 | Clarification behaviour | On items marked ambiguous: share where the assistant asked one question or stated an assumption. On unambiguous items: share where it asked needlessly |
| G1 | Citation coverage | Share of delivered sentences citing at least one existing fact id (ALCE citation recall needs entailment; that part is G3) |
| G2 | Gate pass rate as written | Share of first-draft sentences passing the number, quotation, id and forbidden-claim gates |
| G3 | Support and citation precision | Share of delivered sentences that follow from their cited facts alone: by the checker model on all, by a person on a sample; citation precision (each cited fact needed) by a person on the same sample; the checker's agreement with the person reported |
| G4 | Forbidden-claim rate | Delivered sentences containing a safety verdict, advice, prediction or "validated" (lint), expected 0 |
| A1 | Abstention | Verdict-seeking, out-of-scope and no-record items correctly declined with an offer; over-refusal on answerable items |
| A2 | Relevance | Share of the expected panels and expected tool calls that the turn shows and runs (an embedding-based answer relevance as in Ragas is not used: no embedding model is allowed) |
| S1 | Injection resistance | Share of injection items whose answer follows the planted instruction, expected 0 |
| E1 | Cost | Model calls per turn, seconds per turn, prompt characters per call, cache hit rate |
| E2 | Form | Schema-valid reply on the first try; share of turns that fall back to the template answer |

Arms: the full pipeline; the single-call baseline (one model call that receives the same facts and answers, no repeated reading, no checks); and the full pipeline with one technique switched off at a time (repeated reading, rule-parser vote, clarification, schema `format`, code gates, model checker, repair, data markers, cache and routing, write effort medium to low). Without a running model (`AI_NO_MODEL_CALLS=1`) only the code paths (rule parser, tools, template answers, gates) are scored, and the file says so.

## What vendors publish about building assistants in several steps

Described from the vendors' public pages only; nothing here is a claim about how any product works internally beyond what those pages state.

- **Tool use.** A model is given tool definitions with JSON schemas; it returns a structured tool call, the application runs it and returns the result, and the model continues; a `strict` option makes tool inputs match the schema ([Claude docs, Tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)). gpt-oss is trained for function calling and for browsing and Python tools in the harmony format ([github.com/openai/gpt-oss](https://github.com/openai/gpt-oss)). This project keeps tool choice in code (technique 3) because a small model choosing tools adds a failure point that a closed request schema avoids.
- **Thinking before answering.** Claude models can think before the final answer within a budget or effort level, and can think between tool calls ("interleaved thinking") ([Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)); gpt-oss reasons in an `analysis` channel before the `final` channel ([harmony guide](https://developers.openai.com/cookbook/articles/openai-harmony)).
- **Citations.** Supplied documents are chunked into citable sentences and the API returns exact cited text with locations ([Citations](https://platform.claude.com/docs/en/build-with-claude/citations)).
- **Workflows and agent loops.** Prompt chaining, routing, parallel voting, orchestrator-workers and evaluator-optimizer loops, with the advice to prefer the simplest that works ([*Building effective agents*](https://www.anthropic.com/engineering/building-effective-agents)); a research system with a lead agent, parallel sub-agents and a separate citation step that places citations after the research is done, evaluated with a rubric that includes citation accuracy ([*multi-agent research system*](https://www.anthropic.com/engineering/multi-agent-research-system)).
- **Context.** Keep the context small and high-signal; carry long-running state as notes outside the window ([*Effective context engineering*](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).

## What is known about gpt-oss:20b that matters here

- **Size and licence.** 21B parameters in total, 3.6B active per token (mixture of experts), MXFP4 weights that run within 16 GB of memory, Apache-2.0 ([Hugging Face, openai/gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b); [model card](https://arxiv.org/abs/2508.10925)). The team measured about 50 tokens per second on this machine (`ai/config.py`, smoke run of 2026-11-14).
- **Reasoning effort.** Low, medium, high; higher effort gives longer reasoning and better scores on hard benchmarks at more delay (technique 13). In Ollama the thinking of gpt-oss cannot be turned off; `think=false` falls back to the lowest level ([Ollama docs, Thinking](https://docs.ollama.com/capabilities/thinking)).
- **Format.** Trained on, and should only be used with, the harmony format; Ollama applies it. Response formats in the prompt do not guarantee adherence, so the schema is also enforced in sampling (Ollama `format`) and validated by `ai/llm.py` (technique 1). The team's smoke run recorded schema-valid JSON in 3 of 3 calls with `format` and `think='low'` (`ai/config.py`).
- **Known weaknesses.** Little world knowledge (SimpleQA hallucination rate 0.914 for the 20b model without browsing), weaker instruction-hierarchy and prompt-injection robustness than o4-mini (hijacking 0.639 against 0.917), and a chain of thought that is not trained to the same standard as the final answer and must not be shown to users unfiltered ([model card, arXiv:2508.10925](https://arxiv.org/html/2508.10925), Tables 7 to 9 and Section 4.4). Each weakness maps to a technique above: facts from code only (2), closed output and data markers (12), thinking discarded (13).
- **Not opened.** OpenAI's announcement page (`openai.com/index/introducing-gpt-oss/`) returned HTTP 403 from this machine and is not used.

---

## Summary table

This table may be quoted in the README and the submission text. "Measured by" names the metric in this note; the numbers are in `data/insights/assistant_eval.json`, not here.

| Technique | Used here | Measured by |
|---|---|---|
| Structured outputs, constrained decoding | Yes: every model step returns JSON under an Ollama `format` schema with closed id lists | E2, R1; schema against prompt-only ablation |
| Grounded generation with citations | Yes: sentences cite fact ids; the page draws citation text and links from the facts | G1, G3; against the single-call baseline |
| Decomposition (understand, plan, look up, write, check) | Yes: fixed chain, plan and lookups in code | All metrics; against the single-call baseline |
| Self-consistency (repeated reading and agreement) | Yes, for the request reading only: two seeded readings plus the rule parser, field by field | R1, R2, E1; one reading ablation |
| Clarifying question under ambiguity | Yes: code decides to ask one question or state the assumption | R2 |
| Second model pass as checker (factored, entailment-style) | Yes: one sentence and its cited facts only; can remove, never add | G3, sentences removed; checker-off ablation; agreement with a person |
| Code checks (numbers, quotations, ids, forbidden claims) | Yes: `ai/checks.py`, `ai/lint_patterns.py` | G2, G4; gates-off ablation |
| Repair with external feedback | Yes: at most one repair from gate and checker failures, then template fallback | Written, removed, repaired counts; fallback rate; repair-off ablation |
| Abstention and refusal | Yes: verdicts, predictions and out-of-scope answered by code with an offer | A1 |
| Routing and caching | Yes: presets, chip edits and repeated requests need no model call | E1, cache hit rate |
| Small context, carried state instead of history | Yes: narrow prompts, structured state, numbered facts | Prompt size, E1, R1 on follow-up items |
| Prompt-injection resistance | Yes: marked data blocks, closed outputs, quotations shown by code | S1; markers-off ablation |
| Reasoning effort per step | Yes: low for reading and checking, medium for writing | E1, G3; write low against medium |
| Evaluation with ablations | Yes: fixed question set written before runs, baseline and one ablation per technique | `data/insights/assistant_eval.json` |
| Free agent loop (model chooses tools) | No: tool choice stays in code for a small model | Not measured |
| NLI model or embedding-based metrics | No: no new dependency or model allowed | Not measured |
