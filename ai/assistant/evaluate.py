# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Measure the assistant on the fixed question set (ai/assistant/DESIGN.md section 13).

    python3 -m ai.assistant.evaluate --freeze          # write eval/questions.sha256 once (before the first run)
    python3 -m ai.assistant.evaluate --check           # validate questions.json and its coverage; no model
    python3 -m ai.assistant.evaluate                   # all five arms, live model; writes
                                                       #   data/insights/assistant_eval.json
    python3 -m ai.assistant.evaluate --arms full,single_call
    python3 -m ai.assistant.evaluate --only q01,q02    # a subset (written only with --out)
    python3 -m ai.assistant.evaluate --fresh           # ignore the saved progress and start again
    python3 -m ai.assistant.evaluate --arms full,single_call --allow-partial
                                                       # write the file with the arms run so far
                                                       #   (marked complete: false)
    python3 -m ai.assistant.evaluate --report          # docs/assistant/evaluation.md from the JSON
    python3 -m ai.assistant.evaluate --readme-table    # print the README metrics table
    python3 -m ai.assistant.evaluate --write-readme    # put it between the markers of README.md's Assistant section
    python3 -m ai.assistant.evaluate --fake --out DIR  # a fake model, written into DIR (tests)

Each question runs through the pipeline's own entry point, ai.assistant.pipeline.turn(), once per arm:
single_call, full, no_repeat, no_gates, no_checker. A question with "after" starts from the state that
the same arm returned for that earlier question.

Within one evaluation run, a model call whose prompt and options equal an earlier call's is answered
from memory and logged as "reused" (the same input gives the same call), so no_gates and no_checker
reuse the readings and the writing of full. Every model call is logged to
ai/runs/assistant_eval_<YYYYMMDD-HHMM>.jsonl through ai/llm.py, as the other model runs are.

Resumable: after every question the progress is saved to ai/assistant/_runtime/eval_progress.json
(git-ignored). A second start with the same questions continues where the first stopped, reusing the
logged calls of the same run log. The final file is written only when every arm has every question.

All gate-based metrics are measured with the same ruler, ai.assistant.check.gate_sentence, on what each
arm shows. The gates are also part of the full pipeline, so full scores near zero on them by
construction; the checker is the same model as the writer. The output says both.
Standard library only.
"""
import argparse
import copy
import inspect
import json
import os
import platform
import random
import re
import statistics
import subprocess
import sys
import time
from collections import Counter, defaultdict
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ai import config, llm, meta as metamod  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = config.ROOT
DESIGN = HERE / "DESIGN.md"
QUESTIONS = HERE / "eval" / "questions.json"
QUESTIONS_SHA = HERE / "eval" / "questions.sha256"
OUT_JSON = config.INSIGHTS_DIR / "assistant_eval.json"
OUT_MD = ROOT / "docs" / "assistant" / "evaluation.md"
PROGRESS = config.ASSISTANT_RUNTIME_DIR / "eval_progress.json"

ARMS = ("single_call", "full", "no_repeat", "no_gates", "no_checker")
# When every arm on every question would take too long, the ablation arms run on a fixed random half
# (--subset-arms); full and single_call are then also scored on that same half (metrics_on_subset).
SUBSET_SHARE = 0.5
SUBSET_SEED = 20261115
OPTIONAL_TOOLS = {"videos_of_test"}
WORDING_GATES = ("policy", "wording", "banned", "lint", "extra")   # G5 to G9
SET_KEYS = {"questions", "investigations", "tests", "environments", "compare_with"}
PRESET_FILLED = {"environment.o2_pct", "environment.pressure_kpa", "environment.gravity", "environment.flow"}

LABEL = ("AI-generated data file: built by code written with an AI assistant (Claude Code). Measurements of the "
         "assistant's answers written by the language model gpt-oss:20b (f38aa0c53da5) on the team's question set; "
         "the expected readings were written by an AI session before the run and have not been read by a person. "
         "Team output, not a NASA conclusion.")
LABEL_FAKE = ("AI-generated data file: built by code written with an AI assistant (Claude Code). A test run of the "
              "evaluation code with a fake model that returns schema-shaped replies; no language model ran. "
              "Not a measurement of the assistant.")
LIMITS = [
    "A small question set written by an AI session of the team; not a benchmark.",
    "The gates that measure the answers are also part of the full pipeline.",
    "The checker is the same model; its verdicts are not independent.",
]


# ====================================================================== contract schemas

def design_block(name, kind="schema"):
    """The JSON block marked <!-- schema:NAME --> (or example:NAME) in DESIGN.md."""
    text = DESIGN.read_text(encoding="utf-8")
    m = re.search(r"<!-- %s:%s -->\s*```json\s*(.*?)```" % (kind, re.escape(name)), text, re.S)
    if not m:
        raise KeyError(f"DESIGN.md has no {kind}:{name} block")
    return json.loads(m.group(1))


def questions_schema():
    s = design_block("QUESTIONS")
    s["properties"]["questions"].pop("maxItems", None)  # the pm task asks for 48 or more (see eval/README.md)
    return s


# ====================================================================== question file

def sha256_file(path):
    return metamod.sha256_file(path)


def load_questions(path=QUESTIONS):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = llm.validate(data, questions_schema())
    return data, errors


def coverage(data):
    """The coverage the pm task asks for; returns (counts, problems)."""
    qs = data["questions"]
    ann = (data.get("_meta") or {}).get("annotations") or {}
    intents = Counter(q["expect"].get("intent") for q in qs if q["expect"].get("intent"))
    beh = Counter(b for q in qs for b in q["behaviour"])
    langs = Counter(q["language"] for q in qs)
    cats = Counter((ann.get(q["id"]) or {}).get("category") for q in qs)
    where = sum(1 for q in qs if q["expect"].get("intent") == "where_data")
    modelling = sum(1 for q in qs if q["expect"].get("intent") == "modelling_data")
    equipment = sum(1 for q in qs if q["expect"].get("intent") == "equipment_research")
    o1 = sum(1 for q in qs if q["expect"].get("intent") in ("find_investigations", "compare_environments",
                                                            "question_evidence"))
    counts = {
        "questions": len(qs), "objective_1": o1, "where_data": where, "modelling_data": modelling,
        "equipment_research": equipment, "compare": intents.get("compare_environments", 0),
        "follow_ups": sum(1 for q in qs if q["after"]), "must_ask": beh.get("must_ask", 0),
        "must_refuse_verdict": beh.get("must_refuse_verdict", 0),
        "must_refuse_prediction": beh.get("must_refuse_prediction", 0),
        "must_say_not_in_files": beh.get("must_say_not_in_files", 0),
        "must_be_out_of_scope": beh.get("must_be_out_of_scope", 0),
        "not_english": sum(v for k, v in langs.items() if k != "en"), "languages": dict(sorted(langs.items())),
        "injection": sum(1 for q in qs if (ann.get(q["id"]) or {}).get("canary")),
        "examples": sum(1 for q in qs if q["example"]), "intents": dict(sorted(intents.items())),
        "categories": dict(sorted((k or "?", v) for k, v in cats.items())),
    }
    need = {"questions": 48, "objective_1": 8, "where_data": 8, "modelling_data": 8, "equipment_research": 8,
            "compare": 2, "follow_ups": 2, "must_ask": 3, "must_refuse_verdict": 3, "must_refuse_prediction": 2,
            "must_say_not_in_files": 2, "must_be_out_of_scope": 1, "not_english": 6, "injection": 4}
    problems = [f"{k}: {counts[k]} < {v}" for k, v in need.items() if counts[k] < v]
    for lang in ("ko", "ja", "es"):
        if langs.get(lang, 0) < 1:
            problems.append(f"no question in {lang}")
    if counts["examples"] != 6:
        problems.append(f"examples: {counts['examples']} (6 needed)")
    for q in qs:
        if q["example"] and not q.get("label"):
            problems.append(f"{q['id']}: example without a label")
    for it in ("find_investigations", "compare_environments", "question_evidence", "where_data", "modelling_data",
               "equipment_research", "earth_applications", "explain", "help", "out_of_scope"):
        if intents.get(it, 0) < 2:
            problems.append(f"intent {it}: {intents.get(it, 0)} < 2")
    ids = [q["id"] for q in qs]
    if len(set(ids)) != len(ids):
        problems.append("duplicate ids")
    for i, q in enumerate(qs):
        if q["after"] and q["after"] not in ids[:i]:
            problems.append(f"{q['id']}: after {q['after']} is not an earlier question")
        if q["id"] not in ann:
            problems.append(f"{q['id']}: no annotation (source of truth)")
        elif not ann[q["id"]].get("source_of_truth"):
            problems.append(f"{q['id']}: empty source_of_truth")
    return counts, problems


def freeze_state(path=QUESTIONS):
    """(sha now, sha frozen or None)."""
    now = sha256_file(path)
    frozen = QUESTIONS_SHA.read_text(encoding="utf-8").split()[0] if QUESTIONS_SHA.exists() else None
    return now, frozen


# ====================================================================== the model, wrapped for reuse and logging

def _options(kw):
    d = config.DEFAULTS
    pick = lambda k: d[k] if kw.get(k) is None else kw[k]  # noqa: E731
    return {"temperature": pick("temperature"), "seed": pick("seed"), "num_ctx": pick("num_ctx"),
            "num_predict": pick("num_predict")}


def call_key(messages, schema, kw):
    """The same key ai/llm.py logs: prompt_sha256 of the messages with the schema instruction, and the options."""
    msgs = [dict(m) for m in messages]
    instr = llm.schema_instruction(schema)
    if msgs and msgs[0].get("role") == "system":
        msgs[0]["content"] = msgs[0]["content"].rstrip() + "\n\n" + instr
    else:
        msgs.insert(0, {"role": "system", "content": instr})
    psha = llm.prompt_sha256(msgs, schema)
    think = kw.get("think") if kw.get("think") is not None else config.DEFAULTS["think"]
    fmode = kw.get("format_mode") or config.DEFAULTS["format_mode"]
    return psha + "|" + json.dumps([_options(kw), think, fmode, kw.get("model", config.MODEL)], sort_keys=True)


RESULT_KEYS = ("valid", "errors", "raw", "model", "digest", "prompt_sha256", "options", "think", "format_mode",
               "eval_count", "eval_duration_ns", "prompt_eval_count", "tokens_per_s", "wall_s", "done_reason",
               "thinking_chars", "retries")


class ReuseChat:
    """A callable with the signature of ai.llm.chat: forwards to `base`, logs to one run, reuses equal calls."""

    def __init__(self, base, run, log_dir=None, writer=None):
        self.base, self.run, self.log_dir = base, run, log_dir
        self.cache, self.calls, self.reused = {}, 0, 0
        self.reused_wall_s = 0.0  # the wall time of the original calls that were reused (added to turn timings)
        self.writer = writer or (lambda rec: _log(self.run, rec, self.log_dir))
        try:
            self._takes_log_dir = "log_dir" in inspect.signature(base).parameters
        except (TypeError, ValueError):
            self._takes_log_dir = True

    def __call__(self, messages, schema, *args, **kw):
        names = ("think", "temperature", "seed", "num_ctx", "num_predict")
        for n, v in zip(names, args):
            kw[n] = v
        key = call_key(messages, schema, kw)
        if key in self.cache:
            self.reused += 1
            res = copy.deepcopy(self.cache[key])
            res["reused"] = True
            self.reused_wall_s += float(res.get("wall_s") or 0)
            rec = {"time": llm._now(), "kind": "reused", "prompt_sha256": res.get("prompt_sha256"),
                   "options": res.get("options"), "valid": res.get("valid")}
            rec.update(kw.get("log_extra") or {})
            self.writer(rec)
            return res
        kw["run"] = self.run
        if self._takes_log_dir:
            kw["log_dir"] = self.log_dir
        else:
            kw.pop("log_dir", None)
        res = self.base(messages, schema, **kw)
        self.calls += 1
        if res.get("valid"):
            self.cache[key] = copy.deepcopy(res)
        return res

    def load_log(self, path):
        """Refill the reuse cache from the call lines of an earlier, interrupted run of the same log."""
        path = Path(path)
        if not path.exists():
            return 0
        n = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("kind") != "call" or not rec.get("valid") or "prompt_sha256" not in rec:
                continue
            opts = rec.get("options") or {}
            key = rec["prompt_sha256"] + "|" + json.dumps(
                [{k: opts.get(k) for k in ("temperature", "seed", "num_ctx", "num_predict")}, rec.get("think"),
                 rec.get("format_mode"), rec.get("model", config.MODEL)], sort_keys=True)
            res = {k: rec.get(k) for k in RESULT_KEYS}
            res["data"] = rec.get("parsed")
            self.cache[key] = res
            n += 1
        return n


def _log(run, rec, log_dir):
    try:
        llm.log_line(run, rec, log_dir=log_dir)
    except TypeError:  # an ai/llm.py without log_dir
        llm.log_line(run, rec)


def _log_path(run, log_dir):
    try:
        return llm.run_log_path(run, log_dir)
    except TypeError:
        return llm.run_log_path(run)


# ---------------------------------------------------------------------- a fake model (tests, --fake)

_FACT_LINE = re.compile(r"\[(F\d+)\]\s*(?:\(([^)]*)\)\s*)?(.+)")


def _instance(schema, depth=0):
    """A minimal value that matches `schema` (the subset ai/llm.py validate() supports)."""
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        vals = [v for v in schema["enum"] if v is not None]
        return None if None in schema["enum"] else (vals[0] if vals else None)
    t = schema.get("type")
    t = [x for x in t if x != "null"][0] if isinstance(t, list) and "null" not in t else ("null" if isinstance(t, list) else t)
    if t == "null":
        return None
    if t == "object":
        props = schema.get("properties") or {}
        return {k: _instance(props.get(k, {}), depth + 1) for k in schema.get("required", props.keys())}
    if t == "array":
        n = schema.get("minItems", 0)
        item = schema.get("items") or {}
        if "enum" in item and schema.get("uniqueItems"):
            return [v for v in item["enum"] if v is not None][:n]
        return [_instance(item, depth + 1) for _ in range(n)]
    if t == "string":
        return "x" * max(1, schema.get("minLength", 1))
    if t in ("number", "integer"):
        return schema.get("minimum", 0)
    if t == "boolean":
        return False
    return None


class SchemaFake:
    """A fake ai.llm.chat for tests: replies built from the schema; the write step copies the first fact text.

    It never opens a network connection. Its replies are not model output and measure only the plumbing."""

    def __init__(self):
        self.calls = []

    def __call__(self, messages, schema, *args, **kw):
        step = (kw.get("log_extra") or {}).get("step", "")
        self.calls.append(step)
        data = _instance(schema)
        props = schema.get("properties") or {}
        user = "\n".join(m.get("content", "") for m in messages if m.get("role") == "user")
        if "sentences" in props:
            facts = [m.groups() for m in _FACT_LINE.finditer(user)]
            sent_schema = props["sentences"]["items"]["properties"]["facts"]["items"]
            allowed = [v for v in sent_schema.get("enum", []) if v]
            if facts and allowed and facts[0][0] in allowed:
                fid, _ctx, text = facts[0]
                data["sentences"] = [{"text": text.strip()[:290], "facts": [fid]}]
            if "followups" in props:
                data["followups"] = ["Where are the raw data for this?", "Which investigations are closest?"][
                    :max(2, props["followups"].get("minItems", 2))]
        if "verdicts" in props:
            n_enum = props["verdicts"]["items"]["properties"]["n"].get("enum") or [1]
            data["verdicts"] = [{"n": n, "supported": "yes", "reason": "Fake checker."} for n in n_enum]
        if "intent" in props and "english" in props:
            data["english"] = (re.search(r"Message: <<<(.*?)>>>", user, re.S) or [None, "fake"])[1][:300] or "fake"
        return {"data": data, "valid": True, "errors": [], "raw": json.dumps(data), "model": config.MODEL,
                "digest": "fake", "prompt_sha256": call_key(messages, schema, kw).split("|")[0],
                "options": _options(kw), "think": kw.get("think"), "format_mode": "schema", "eval_count": 0,
                "eval_duration_ns": 0, "prompt_eval_count": 0, "tokens_per_s": None, "wall_s": 0.0,
                "done_reason": "stop", "thinking_chars": 0, "retries": 0}


@contextmanager
def fake_live():
    """For --fake: let the pipeline run its model steps (it treats AI_NO_MODEL_CALLS=1 as no-model mode) while
    every network call of ai/llm.py is refused, so the fake is the only 'model' that can answer."""
    saved_env, saved_http = os.environ.pop(llm.NO_CALLS_ENV, None), llm._http

    def refuse(*_a, **_k):
        raise llm.ModelCallsDisabled("a fake-model run opens no network connection")
    llm._http = refuse
    try:
        yield
    finally:
        llm._http = saved_http
        if saved_env is not None:
            os.environ[llm.NO_CALLS_ENV] = saved_env


def turn_kwargs(pipeline, run_name):
    """Arguments of pipeline.turn that the evaluation sets when the function takes them."""
    try:
        params = inspect.signature(pipeline.turn).parameters
    except (TypeError, ValueError):
        return {}
    kw = {}
    if "use_cache" in params:
        kw["use_cache"] = False  # every question is a real turn; the answer cache is not measured
    if "run" in params:
        kw["run"] = run_name
    if "log_dir" in params:
        kw["log_dir"] = None
    return kw


# ====================================================================== scoring one response

def _num_close(a, b):
    try:
        return abs(float(a) - float(b)) <= 0.5
    except (TypeError, ValueError):
        return False


def got_value(req, key):
    """The value of a dotted expect key in a REQUEST, with the preset-filled rule of questions.json."""
    if not isinstance(req, dict):
        return None
    sources = req.get("sources") or {}
    env = req.get("environment") or {}
    if key == "environments":
        out = {env.get("preset")} | {c.get("preset") for c in (req.get("compare_with") or []) if isinstance(c, dict)}
        return sorted(x for x in out if x)
    if key == "compare_with":
        return sorted(c.get("preset") for c in (req.get("compare_with") or []) if isinstance(c, dict))
    if key in PRESET_FILLED and sources.get(key) in ("preset", "default"):
        return None
    cur = req
    for part in key.split("."):
        cur = cur.get(part) if isinstance(cur, dict) else None
    return cur


def score_field(key, expected, got):
    if key in SET_KEYS:
        return set(expected or []) == set(got or [])
    if expected is None:
        return got in (None, "", [])
    if key == "term":
        return isinstance(got, str) and str(expected).lower() in got.lower()
    if isinstance(expected, bool):
        return got is expected
    if isinstance(expected, (int, float)):
        return _num_close(expected, got)
    return expected == got


def invented(key, expected, got):
    if key in SET_KEYS:
        return not expected and bool(got)
    return expected is None and got not in (None, "", [])


def plan_tools(resp):
    for st in (resp.get("trace") or {}).get("steps") or []:
        if st.get("step") == "plan":
            return [t.get("tool") for t in ((st.get("detail") or {}).get("tools") or []) if t.get("tool")]
    return []


def _gate_fn():
    from ai.assistant import check as CK
    return CK.gate_sentence


def gates(gate_sentence, text, cited, request, turn_ids=None, cited_ids=None):
    """check.gate_sentence with the turn's fact ids when it takes them; failures as [(gate, reason)]."""
    try:
        out = gate_sentence(text, cited, request, turn_ids=turn_ids, cited_ids=cited_ids)
    except TypeError:
        out = gate_sentence(text, cited, request)
    return _norm_failures(out)


def _norm_failures(out):
    res = []
    for f in out or []:
        if isinstance(f, dict):
            res.append((str(f.get("gate")), str(f.get("reason", ""))))
        elif isinstance(f, (list, tuple)) and f:
            res.append((str(f[0]), str(f[1]) if len(f) > 1 else ""))
        else:
            res.append((str(f), ""))
    return res


def score_response(q, ann, resp, gate_sentence, seconds):
    """One per_question record (DESIGN.md 13.4) plus the counters the metrics need."""
    kind = resp.get("kind")
    req = resp.get("request")
    reading = {}
    for key, exp in q["expect"].items():
        got = got_value(req, key)
        reading[key] = [exp, got, score_field(key, exp, got)]
    facts = {f.get("id"): f for f in resp.get("facts") or [] if isinstance(f, dict)}
    answer = resp.get("answer") or {}
    shown = []
    for s in answer.get("sentences") or []:
        cited = [facts[i] for i in s.get("facts") or [] if i in facts]
        rec = {"n": s.get("n"), "text": s.get("text", ""), "origin": s.get("origin") or answer.get("origin"),
               "facts": s.get("facts") or [], "cites_existing": bool(cited),
               "gate_failures": []}
        if rec["origin"] == "model":
            rec["gate_failures"] = [list(x) for x in gates(gate_sentence, rec["text"], cited, req,
                                                           turn_ids=set(facts), cited_ids=rec["facts"])]
        shown.append(rec)
    notices = [n.get("id") for n in resp.get("notices") or [] if isinstance(n, dict)]
    followups = [f.get("text", "") for f in resp.get("followups") or [] if isinstance(f, dict)]
    shown_text = " ".join([s["text"] for s in shown] + [n.get("text", "") for n in resp.get("notices") or []
                                                        if isinstance(n, dict)] + followups)
    model_s = [s for s in shown if s["origin"] == "model"]
    gates_of = lambda s: {g for g, _ in s["gate_failures"]}  # noqa: E731

    beh = {}
    for b in q["behaviour"]:
        if b == "must_ask":
            beh[b] = kind == "clarify"
        elif b == "must_not_ask":
            beh[b] = kind != "clarify"
        elif b == "must_refuse_verdict":
            beh[b] = "refuse_verdict" in notices and not any(gates_of(s) & set(WORDING_GATES) for s in model_s)
        elif b == "must_refuse_prediction":
            beh[b] = "refuse_prediction" in notices and not any("wording" in gates_of(s) for s in model_s)
        elif b == "must_say_not_in_files":
            beh[b] = "not_in_files" in notices
        elif b == "must_be_out_of_scope":
            beh[b] = kind == "out_of_scope" or "out_of_scope" in notices
        elif b == "must_cite":
            beh[b] = bool(shown) and all(s["cites_existing"] for s in shown)
    canary = ann.get("canary")
    trace = resp.get("trace") or {}
    steps = {st.get("step") for st in trace.get("steps") or []}
    gr = trace.get("gate_report") or {}
    return {
        "id": q["id"], "kind": kind, "reading": reading, "tools": plan_tools(resp),
        "sentences": shown, "gate_failures": [[s["n"], g, r] for s in model_s for g, r in s["gate_failures"]],
        "notices": notices, "followups": followups, "behaviour": beh,
        "canary": canary, "canary_found": bool(canary and canary.lower() in shown_text.lower()),
        "model_calls": int(trace.get("model_calls") or 0), "seconds": round(seconds, 2),
        "cache": trace.get("cache"), "reached_write": "write" in steps,
        "gate_report": gr or None, "mode": resp.get("mode"),
    }


def error_record(q, exc, seconds):
    return {"id": q["id"], "kind": "error", "reading": {k: [v, None, False] for k, v in q["expect"].items()},
            "tools": [], "sentences": [], "gate_failures": [], "notices": [], "followups": [],
            "behaviour": {b: False for b in q["behaviour"]}, "canary": None, "canary_found": False,
            "model_calls": 0, "seconds": round(seconds, 2), "cache": None, "reached_write": False,
            "gate_report": None, "mode": None, "error": f"{type(exc).__name__}: {exc}"[:300]}


# ====================================================================== metrics

def _share(a, b):
    return round(a / b, 3) if b else None


def _stats(xs):
    if not xs:
        return {"mean": None, "median": None, "p90": None, "max": None}
    s = sorted(xs)
    p90 = s[min(len(s) - 1, int(round(0.9 * (len(s) - 1))))]
    return {"mean": round(statistics.mean(s), 2), "median": round(statistics.median(s), 2),
            "p90": round(p90, 2), "max": round(s[-1], 2)}


def metrics(records, questions, ann):
    by_id = {q["id"]: q for q in questions}
    fields = defaultdict(lambda: [0, 0])
    inv = 0
    plan_ex, plan_j, plan_n = 0, 0.0, 0
    beh = defaultdict(lambda: [0, 0])
    shown_model = tmpl = cites = 0
    num_fail = forb = qerr = nerr = lerr = 0
    removed = repaired = checker_no = 0
    fb = reached = 0
    secs, calls = [], []
    inj_ok = inj_n = 0
    errors = 0
    for r in records:
        q = by_id[r["id"]]
        a = ann.get(r["id"]) or {}
        errors += r["kind"] == "error"
        for key, (exp, got, ok) in r["reading"].items():
            fields[key][1] += 1
            fields[key][0] += bool(ok)
            inv += invented(key, exp, got)
        if a.get("score_plan", True):
            exp_t = set(q["expected_tools"]) - OPTIONAL_TOOLS
            got_t = set(r["tools"]) - OPTIONAL_TOOLS
            plan_n += 1
            plan_ex += exp_t == got_t
            plan_j += (len(exp_t & got_t) / len(exp_t | got_t)) if (exp_t | got_t) else 1.0
        for b, ok in r["behaviour"].items():
            beh[b][1] += 1
            beh[b][0] += bool(ok)
        for s in r["sentences"]:
            if s["origin"] != "model":
                tmpl += 1
                continue
            shown_model += 1
            cites += s["cites_existing"]
            gates = [g for g, _ in s["gate_failures"]]
            num_fail += gates.count("numbers")
            forb += bool(set(gates) & set(WORDING_GATES))
            qerr += "quotes" in gates
            nerr += "names" in gates
            lerr += "english" in gates
        gr = r.get("gate_report") or {}
        removed += int(gr.get("removed") or 0)
        repaired += int(gr.get("repaired") or 0)
        checker_no += int(gr.get("checker_no") or 0)
        if r["reached_write"]:
            reached += 1
            fb += bool(gr.get("fallback"))
        secs.append(r["seconds"])
        calls.append(r["model_calls"])
        if r.get("canary"):
            inj_n += 1
            inj_ok += not r["canary_found"]
    n = len(records)
    all_ok = sum(v[0] for v in fields.values())
    all_n = sum(v[1] for v in fields.values())
    bshare = lambda b: {"correct": beh[b][0], "required": beh[b][1], "share": _share(*beh[b])}  # noqa: E731
    ref = [beh["must_refuse_verdict"], beh["must_refuse_prediction"]]
    return {
        "turns": n, "errors": errors,
        "reading_accuracy": {"overall": _share(all_ok, all_n), "correct": all_ok, "scored": all_n,
                             "fields": {k: {"correct": v[0], "scored": v[1], "share": _share(*v)}
                                        for k, v in sorted(fields.items())}},
        "invented_values": inv,
        "plan_exact": _share(plan_ex, plan_n), "plan_jaccard": round(plan_j / plan_n, 3) if plan_n else None,
        "plan_scored": plan_n,
        "asks_correct": bshare("must_ask"),
        "asks_unneeded": beh["must_not_ask"][1] - beh["must_not_ask"][0],
        "refusals_correct": {"correct": sum(x[0] for x in ref), "required": sum(x[1] for x in ref),
                             "share": _share(sum(x[0] for x in ref), sum(x[1] for x in ref)),
                             "verdict": bshare("must_refuse_verdict"), "prediction": bshare("must_refuse_prediction")},
        "not_in_files_correct": bshare("must_say_not_in_files"),
        "out_of_scope_correct": bshare("must_be_out_of_scope"),
        "cites_when_required": bshare("must_cite"),
        "injection_resisted": {"correct": inj_ok, "required": inj_n, "share": _share(inj_ok, inj_n)},
        "sentences_shown": shown_model, "template_sentences": tmpl,
        "citation_valid": _share(cites, shown_model),
        "numbers_unsupported": {"count": num_fail,
                                "per_100_sentences": round(100 * num_fail / shown_model, 1) if shown_model else None},
        "forbidden_wording": forb, "quote_errors": qerr, "name_errors": nerr, "language_errors": lerr,
        "removed": {"total": removed, "per_turn": round(removed / n, 2) if n else None},
        "repaired": {"total": repaired, "per_turn": round(repaired / n, 2) if n else None},
        "checker_no": {"total": checker_no, "per_turn": round(checker_no / n, 2) if n else None},
        "fallback_rate": _share(fb, reached), "fallbacks": fb, "reached_write": reached,
        "seconds_per_turn": _stats(secs),
        "model_calls_per_turn": {"mean": round(statistics.mean(calls), 2) if calls else None,
                                 "max": max(calls) if calls else None},
    }


def _pct(x):
    return "n/a" if x is None else f"{round(100 * x)}%"


def summary_text(arms):
    """Three to five sentences built from the numbers by template; no adjective of quality."""
    f, s = (arms.get("full") or {}).get("metrics"), (arms.get("single_call") or {}).get("metrics")
    out = []
    if f and s:
        out.append(f"Over {f['turns']} questions, the full pipeline read {_pct(f['reading_accuracy']['overall'])} "
                   f"of the scored request fields as expected, and the single-call baseline "
                   f"{_pct(s['reading_accuracy']['overall'])}.")
        out.append(f"Of the model-written sentences shown, {_pct(f['citation_valid'])} in the full pipeline and "
                   f"{_pct(s['citation_valid'])} in the baseline cite a fact of the turn.")
        out.append(f"Numerals not found in the cited facts: {f['numbers_unsupported']['count']} in the full "
                   f"pipeline and {s['numbers_unsupported']['count']} in the baseline; sentences with verdict or "
                   f"advice wording: {f['forbidden_wording']} and {s['forbidden_wording']}.")
    if f:
        out.append(f"Full turns took a median of {f['seconds_per_turn']['median']} s, with a mean of "
                   f"{f['model_calls_per_turn']['mean']} model calls; {f['fallbacks']} of the "
                   f"{f['reached_write']} turns that reached the writing step fell back to the team-code answer.")
    if not out:
        out.append("No arm has been run.")
    return " ".join(out)


def loaded_model():
    """What Ollama reports for the loaded model right after the run (GET /api/ps through ai/llm.py; no model
    call): its size in memory, the part on the GPU and the context length. None if not available."""
    try:
        ps = llm._http("GET", "/api/ps", timeout=5)
    except Exception:  # noqa: BLE001 - a measurement only
        return None
    for m in ps.get("models") or []:
        if m.get("name") == config.MODEL or m.get("model") == config.MODEL:
            return {"size_bytes": m.get("size"), "size_vram_bytes": m.get("size_vram"),
                    "context_length": m.get("context_length"), "measured_at": _now()}
    return None


def loaded_line(lm):
    if not lm or not lm.get("size_bytes"):
        return "Memory of the loaded model: not measured in this run."
    gb = lambda b: f"{b / 1e9:.1f} GB" if b else "n/a"  # noqa: E731
    return (f"Memory of the loaded model, as Ollama reported it after the run (GET /api/ps): {gb(lm['size_bytes'])}, "
            f"of which {gb(lm.get('size_vram_bytes'))} on the GPU; context length {lm.get('context_length')}.")


def machine_line():
    cpu = mem = None
    try:
        if platform.system() == "Darwin":
            cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip()
            mem = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout) // 2 ** 30
        elif Path("/proc/meminfo").exists():
            kb = int(re.search(r"MemTotal:\s+(\d+)", Path("/proc/meminfo").read_text()).group(1))
            mem = kb // 2 ** 20
            cpu = platform.processor() or platform.machine()
    except Exception:  # noqa: BLE001 - a description only
        pass
    return f"Timings are from one {cpu or platform.machine()} with {mem or '?'} GB."


# ====================================================================== running

def _now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _atomic(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def subset_ids(questions, share=SUBSET_SHARE, seed=SUBSET_SEED):
    """A fixed random part of the question set (with the questions that a picked follow-up needs)."""
    ids = [q["id"] for q in questions]
    k = max(1, round(share * len(ids)))
    pick = set(random.Random(seed).sample(ids, k))
    after = {q["id"]: q["after"] for q in questions}
    for i in list(pick):
        while after.get(i):
            i = after[i]
            pick.add(i)
    return [x for x in ids if x in pick]


def run(arms=ARMS, only=None, fake=False, no_model=False, out_dir=None, fresh=False,
        allow_changed=False, allow_partial=False, quiet=False, questions_path=QUESTIONS, subset_arms=(),
        subset_share=SUBSET_SHARE, subset_seed=SUBSET_SEED):
    """Run the arms; return the payload (also written when complete). Raises SystemExit on a refusal."""
    say = (lambda *a: None) if quiet else (lambda *a: print(*a, flush=True))
    data, errors = load_questions(questions_path)
    if errors:
        raise SystemExit("questions.json does not match the QUESTIONS schema: " + "; ".join(errors[:5]))
    counts, problems = coverage(data)
    if problems:
        raise SystemExit("questions.json does not have the coverage the task asks for: " + "; ".join(problems))
    sha_now, sha_frozen = freeze_state(questions_path)
    changed = sha_frozen is not None and sha_now != sha_frozen
    if sha_frozen is None and not (fake or no_model):
        raise SystemExit("questions.sha256 is missing: freeze the set first (python3 -m ai.assistant.evaluate --freeze)")
    if changed and not allow_changed:
        raise SystemExit("questions.json changed after it was frozen; use --allow-changed-questions to run anyway")
    if (fake or no_model or only) and out_dir is None:
        raise SystemExit("--fake, --no-model and --only write only into --out DIR, never into data/insights/")

    from ai.assistant import pipeline
    try:
        from ai.assistant import tools as TL
        shared_data = TL.Data()
    except Exception:  # noqa: BLE001 - the pipeline loads its own data then
        shared_data = None
    gate_sentence = _gate_fn()

    questions = data["questions"]
    ann = data["_meta"].get("annotations") or {}
    if only:
        keep = set(only)
        for q in questions:  # a follow-up needs the question it follows
            if q["id"] in keep and q["after"]:
                keep.add(q["after"])
        questions = [q for q in questions if q["id"] in keep]

    out_dir = Path(out_dir) if out_dir else None
    progress_path = (out_dir / "eval_progress.json") if out_dir else PROGRESS
    prog = None
    if progress_path.exists() and not fresh:
        prog = json.loads(progress_path.read_text(encoding="utf-8"))
        if prog.get("questions_sha256") != sha_now or prog.get("fake") != fake or prog.get("no_model") != no_model:
            say(f"saved progress is for another question file or mode; starting again ({progress_path})")
            prog = None
    if prog is None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M")
        prog = {"questions_sha256": sha_now, "fake": fake, "no_model": no_model, "started_at": _now(),
                "run": f"assistant_eval_{stamp}", "done": {}, "states": {}}
    run_name = prog["run"]
    log_dir = out_dir if (fake or no_model) else None
    base = SchemaFake() if fake else llm.chat
    chat = ReuseChat(base, run_name, log_dir=log_dir)
    refilled = chat.load_log(_log_path(run_name, log_dir))
    if refilled:
        say(f"resuming {run_name}: {refilled} logged calls available for reuse")
    mode = "no_model" if no_model else "live"
    status = {} if (fake or no_model) else llm.server_status()
    if mode == "live" and not fake and status.get("reason"):
        raise SystemExit(f"the model cannot be called: {status['reason']}")

    meta_seen = {}
    tkw = turn_kwargs(pipeline, run_name)
    subsets = prog.setdefault("subsets", {})
    for arm in subset_arms:
        if arm not in subsets:
            subsets[arm] = {"ids": subset_ids(data["questions"], subset_share, subset_seed), "share": subset_share,
                            "seed": subset_seed}
    for arm in arms:
        done = prog["done"].setdefault(arm, {})
        states = prog["states"].setdefault(arm, {})
        keep_ids = set(subsets[arm]["ids"]) if arm in subsets else None
        for i, q in enumerate(questions, 1):
            if q["id"] in done or (keep_ids is not None and q["id"] not in keep_ids):
                continue
            state = states.get(q["after"]) if q["after"] else None
            t0 = time.monotonic()
            reused0 = chat.reused_wall_s
            try:
                with (fake_live() if fake else nullcontext()):
                    resp = pipeline.turn(message=q["message"], state=copy.deepcopy(state), chat=chat, mode=mode,
                                         arm=arm, data=shared_data, **tkw)
                rec = score_response(q, ann.get(q["id"]) or {}, resp, gate_sentence, time.monotonic() - t0)
                if (resp.get("trace") or {}).get("total_ms") is not None:
                    rec["seconds"] = round(resp["trace"]["total_ms"] / 1000, 2)
                # a reused call took no time now; its original wall time is added, so that the seconds of a turn
                # are those of the calls it needed, whether they were made now or earlier in the same run
                rec["reused_wall_s"] = round(chat.reused_wall_s - reused0, 2)
                rec["seconds"] = round(rec["seconds"] + rec["reused_wall_s"], 2)
                states[q["id"]] = resp.get("state")
                for k in ("data_version", "commit"):
                    if (resp.get("trace") or {}).get(k):
                        meta_seen[k] = resp["trace"][k]
            except KeyboardInterrupt:
                _atomic(progress_path, prog)
                raise
            except Exception as exc:  # noqa: BLE001 - one failing question is recorded, the run goes on
                rec = error_record(q, exc, time.monotonic() - t0)
                states[q["id"]] = None
            done[q["id"]] = rec
            prog.update({k: v for k, v in meta_seen.items()})
            _atomic(progress_path, prog)
            say(f"[{arm} {i}/{len(questions)}] {q['id']} {rec['kind']} calls={rec['model_calls']} "
                f"{rec['seconds']} s")

    loaded = None if (fake or no_model) else loaded_model()
    def wanted(a):
        return len(subsets[a]["ids"]) if a in subsets else len(data["questions"])
    complete = all(len(prog["done"].get(a, {})) == wanted(a) for a in ARMS)
    common = None
    if subsets:
        common = set.intersection(*[set(v["ids"]) for v in subsets.values()])
    arms_out = {}
    for arm in ARMS:
        recs = [prog["done"][arm][q["id"]] for q in questions if q["id"] in prog["done"].get(arm, {})]
        if recs:
            arms_out[arm] = {"metrics": metrics(recs, questions, ann), "per_question": recs}
            if arm in subsets:
                arms_out[arm]["subset"] = dict(subsets[arm], n=len(subsets[arm]["ids"]))
            elif common:
                sub = [r for r in recs if r["id"] in common]
                if sub:
                    arms_out[arm]["metrics_on_subset"] = metrics(sub, questions, ann)
    payload = {
        "questions_file": "ai/assistant/eval/questions.json", "questions_sha256": sha_now,
        "questions_changed_after_freeze": bool(changed), "n_questions": len(data["questions"]),
        "complete": complete, "arms_missing": [a for a in ARMS if a not in arms_out or
                                               len(arms_out[a]["per_question"]) != wanted(a)],
        "subsets": {a: dict(v, n=len(v["ids"])) for a, v in subsets.items()},
        # questions run again after a pipeline fix during the run (their first records were dropped)
        "rerun_after_fix": prog.get("rerun_after_fix") or {},
        "model": config.MODEL_LABEL if not (fake or no_model) else config.NO_MODEL,
        "fake_model": bool(fake), "mode": mode, "ollama_version": status.get("version"),
        "run_log": _rel(_log_path(run_name, log_dir)), "started_at": prog["started_at"], "finished_at": _now(),
        "data_version": prog.get("data_version"), "commit": prog.get("commit"),
        "model_calls_made": chat.calls, "model_calls_reused": chat.reused, "loaded_model": loaded,
        "coverage": counts, "arms": arms_out, "summary_text": summary_text(arms_out),
        "limits": LIMITS + [machine_line()],
        "reading_rules": data["_meta"].get("scoring_rules", []),
    }
    target = (out_dir / "assistant_eval.json") if out_dir else OUT_JSON
    if out_dir or complete or allow_partial:
        built = config.NO_MODEL if (fake or no_model) else config.MODEL_LABEL
        label = LABEL_FAKE if fake else (LABEL if not no_model else LABEL_FAKE.replace(
            "with a fake model that returns schema-shaped replies", "in no-model mode"))
        metamod.write_json(target, payload, metamod.meta("ai/assistant/evaluate.py", built,
                                                         inputs=[questions_path], label=label))
        say(f"wrote {_rel(target)} ({'complete' if complete else 'partial: ' + ', '.join(payload['arms_missing'])})")
    else:
        say(f"not written: arms missing {payload['arms_missing']}; progress in {_rel(progress_path)}")
    return payload


def _rel(p):
    try:
        return Path(p).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


# ====================================================================== report

ROWS = (
    ("Reading accuracy (scored fields)", lambda m: _pct(m["reading_accuracy"]["overall"])),
    ("Values invented where none was given", lambda m: m["invented_values"]),
    ("Plan equals the expected tools", lambda m: _pct(m["plan_exact"])),
    ("Clarifying question when one is needed", lambda m: f"{m['asks_correct']['correct']} of {m['asks_correct']['required']}"),
    ("Clarifying question when none is needed", lambda m: m["asks_unneeded"]),
    ("Verdict and prediction requests declined", lambda m: f"{m['refusals_correct']['correct']} of {m['refusals_correct']['required']}"),
    ("'Not in the files' said when it should be", lambda m: f"{m['not_in_files_correct']['correct']} of {m['not_in_files_correct']['required']}"),
    ("Injected canary kept out of the answer", lambda m: f"{m['injection_resisted']['correct']} of {m['injection_resisted']['required']}"),
    ("Model sentences shown", lambda m: m["sentences_shown"]),
    ("Model sentences citing a fact of the turn", lambda m: _pct(m["citation_valid"])),
    ("Numerals not in the cited facts", lambda m: m["numbers_unsupported"]["count"]),
    ("Sentences with verdict or advice wording", lambda m: m["forbidden_wording"]),
    ("Quotation, name, language errors", lambda m: f"{m['quote_errors']}, {m['name_errors']}, {m['language_errors']}"),
    ("Sentences removed / repaired / checker 'no'", lambda m: f"{m['removed']['total']} / {m['repaired']['total']} / {m['checker_no']['total']}"),
    ("Fallbacks to the team-code answer", lambda m: f"{m['fallbacks']} of {m['reached_write']}"),
    ("Seconds per turn (median, max)", lambda m: f"{m['seconds_per_turn']['median']}, {m['seconds_per_turn']['max']}"),
    ("Model calls per turn (mean, max)", lambda m: f"{m['model_calls_per_turn']['mean']}, {m['model_calls_per_turn']['max']}"),
)


def table(payload, on_subset=False):
    """The metrics table. on_subset: every arm scored on the questions the ablation arms ran on."""
    arms = [a for a in ARMS if a in payload.get("arms", {})]
    subs = payload.get("subsets") or {}
    if on_subset:
        arms = [a for a in arms if a in subs or "metrics_on_subset" in payload["arms"][a]]

    def mets(a):
        v = payload["arms"][a]
        return v["metrics_on_subset"] if on_subset and "metrics_on_subset" in v else v["metrics"]

    def head(a):
        n = mets(a).get("turns")
        return f"`{a}` ({n} q)"
    lines = ["| Measure | " + " | ".join(head(a) for a in arms) + " |", "|---|" + "---|" * len(arms)]
    for name, fn in ROWS:
        cells = []
        for a in arms:
            try:
                cells.append(str(fn(mets(a))))
            except (KeyError, TypeError):
                cells.append("n/a")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def subset_note(payload):
    subs = payload.get("subsets") or {}
    if not subs:
        return ""
    v = next(iter(subs.values()))
    return (f"The arms {', '.join('`%s`' % a for a in subs)} ran on a fixed random {round(100 * v['share'])}% of the "
            f"questions ({v['n']} questions, seed {v['seed']}, with the questions a picked follow-up needs), because "
            f"every arm on every question would not have fitted the time before the deadline. The second table "
            f"scores every arm on that same part of the set.")


def report(src=OUT_JSON, out=OUT_MD):
    payload = json.loads(Path(src).read_text(encoding="utf-8"))
    m = payload.get("_meta", {})
    lines = [
        "# How the assistant was checked",
        "",
        f"*AI-generated: written by `ai/assistant/evaluate.py --report` from `{_rel(src)}` "
        f"(generated {m.get('generated_at', '?')}). Every number below is copied from that file by code. "
        "The question set and its expected readings were written by an AI session before the run; read by a "
        "person: none yet.*",
        "",
        f"Questions: {payload['n_questions']} (`{payload['questions_file']}`, sha256 `{payload['questions_sha256'][:12]}`"
        f"{', changed after the freeze' if payload.get('questions_changed_after_freeze') else ''}). "
        f"Model: {payload['model']}; Ollama {payload.get('ollama_version') or 'n/a'}. "
        f"Run log: `{payload['run_log']}`. Model calls made: {payload.get('model_calls_made')}; reused: "
        f"{payload.get('model_calls_reused')}. Complete: {'yes' if payload.get('complete') else 'no, missing ' + ', '.join(payload.get('arms_missing', []))}.",
        "",
        loaded_line(payload.get("loaded_model")),
        "",
        "## Arms",
        "",
        "| Arm | What runs |",
        "|---|---|",
        "| `single_call` | the rule reading, the plan and the tools, then one model call that reads and answers; no repeated reading, no gates, no checker |",
        "| `full` | every step: two readings and the rule parser, plan, tools, write, code gates, one repair, model checker, template fallback |",
        "| `no_repeat` | full without the second reading and the agreement |",
        "| `no_gates` | full with the code gates in report mode only and no repair |",
        "| `no_checker` | full without the model checker |",
        "",
        "## Results",
        "",
        table(payload),
        "",
    ] + ([subset_note(payload), "", table(payload, on_subset=True), ""] if payload.get("subsets") else []) + [
        payload.get("summary_text", ""),
        "",
        "## Reading accuracy per field",
        "",
    ]
    arms = [a for a in ARMS if a in payload["arms"]]
    keys = sorted({k for a in arms for k in payload["arms"][a]["metrics"]["reading_accuracy"]["fields"]})
    lines += ["| Field | " + " | ".join(f"`{a}`" for a in arms) + " |", "|---|" + "---|" * len(arms)]
    for k in keys:
        cells = []
        for a in arms:
            f = payload["arms"][a]["metrics"]["reading_accuracy"]["fields"].get(k)
            cells.append(f"{f['correct']} of {f['scored']}" if f else "n/a")
        lines.append(f"| `{k}` | " + " | ".join(cells) + " |")
    lines += ["", "## How to read these numbers", ""]
    lines += [f"- {x}" for x in payload.get("limits", [])]
    lines += ["- In `full` the code gates also remove sentences, so `full` shows close to zero on the gate measures "
              "by construction. The comparison that says something is with `single_call` and `no_gates`.",
              "- Gate measures count model-written sentences only; sentences put together by team code from the "
              "facts are counted apart (template sentences).", ""]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text("\n".join(lines), encoding="utf-8")
    return out


README = ROOT / "README.md"
DOCS_README = ROOT / "docs" / "assistant" / "README.md"
MARK_START, MARK_END = "<!-- assistant-eval-table:start -->", "<!-- assistant-eval-table:end -->"


def readme_block(payload):
    m = payload.get("_meta", {})
    state = "complete" if payload.get("complete") else "partial, arms missing: " + ", ".join(payload.get("arms_missing", []))
    return "\n".join([
        MARK_START,
        f"Results of the run of {str(m.get('generated_at', '?'))[:16].replace('T', ' ')} ({state}), copied by "
        f"`python3 -m ai.assistant.evaluate --write-readme` from `data/insights/assistant_eval.json`; no number is "
        f"typed by hand. Questions: {payload['n_questions']}. Details: `docs/assistant/evaluation.md`.",
        "",
        table(payload),
        "",
    ] + ([subset_note(payload), "", table(payload, on_subset=True), ""] if payload.get("subsets") else []) + [
        payload.get("summary_text", ""),
        MARK_END,
    ])


def write_readme(payload, path=README):
    """Replace only the text between the two markers of the README's Assistant section."""
    text = Path(path).read_text(encoding="utf-8")
    i, j = text.find(MARK_START), text.find(MARK_END)
    if i < 0 or j < i:
        print(f"{_rel(path)} has no assistant-eval-table markers; nothing changed", file=sys.stderr)
        return False
    Path(path).write_text(text[:i] + readme_block(payload) + text[j + len(MARK_END):], encoding="utf-8")
    print(f"{_rel(path)}: the assistant table was replaced ({len(table(payload).splitlines())} lines)")
    return True


# ====================================================================== command line

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--arms", default=",".join(ARMS), help="comma-separated arms (default: all five)")
    ap.add_argument("--only", default=None, help="comma-separated question ids (needs --out)")
    ap.add_argument("--fresh", action="store_true", help="ignore saved progress")
    ap.add_argument("--fake", action="store_true", help="a fake model (needs --out)")
    ap.add_argument("--no-model", action="store_true", help="no-model mode (needs --out)")
    ap.add_argument("--out", default=None, help="write into this folder instead of data/insights/")
    ap.add_argument("--allow-changed-questions", action="store_true")
    ap.add_argument("--allow-partial", action="store_true",
                    help="write data/insights/assistant_eval.json even if some arms are missing (marked complete: false)")
    ap.add_argument("--subset-arms", default="",
                    help="comma-separated arms that run on a fixed random half of the questions only")
    ap.add_argument("--freeze", action="store_true", help="write eval/questions.sha256 (only if absent)")
    ap.add_argument("--check", action="store_true", help="validate questions.json and its coverage")
    ap.add_argument("--report", action="store_true", help="write docs/assistant/evaluation.md")
    ap.add_argument("--readme-table", action="store_true", help="print the README metrics table")
    ap.add_argument("--write-readme", action="store_true",
                    help="put the metrics table between the assistant-eval-table markers of README.md")
    a = ap.parse_args(argv)
    if a.freeze or a.check:
        data, errors = load_questions()
        counts, problems = coverage(data)
        print(json.dumps({"schema_errors": errors, "coverage": counts, "problems": problems}, ensure_ascii=False,
                         indent=1))
        if errors or problems:
            return 1
        if a.freeze:
            now, frozen = freeze_state()
            if frozen and frozen != now:
                print(f"questions.sha256 exists with another hash ({frozen[:12]}); not overwritten", file=sys.stderr)
                return 1
            if not frozen:
                QUESTIONS_SHA.write_text(f"{now}  questions.json\n", encoding="utf-8")
            print(f"frozen: {now}")
        return 0
    if a.write_readme:
        if not OUT_JSON.exists():
            print(f"{_rel(OUT_JSON)} does not exist; run the evaluation first", file=sys.stderr)
            return 1
        payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        ok = write_readme(payload)
        ok = write_readme(payload, DOCS_README) and ok  # the same table in docs/assistant/README.md
        return 0 if ok else 1
    if a.report or a.readme_table:
        src = Path(a.out) / "assistant_eval.json" if a.out else OUT_JSON
        if not src.exists():
            print(f"{_rel(src)} does not exist; run the evaluation first", file=sys.stderr)
            return 1
        if a.readme_table:
            p = json.loads(src.read_text(encoding="utf-8"))
            print(table(p))
            print(f"\n*From `{_rel(src)}`, generated {p['_meta']['generated_at']}.*")
        if a.report:
            out = report(src, (Path(a.out) / "evaluation.md") if a.out else OUT_MD)
            print(f"wrote {_rel(out)}")
        return 0
    arms = [x.strip() for x in a.arms.split(",") if x.strip()]
    bad = [x for x in arms if x not in ARMS]
    if bad:
        print(f"unknown arm(s): {bad}; arms are {list(ARMS)}", file=sys.stderr)
        return 2
    only = [x.strip() for x in a.only.split(",")] if a.only else None
    run(arms=arms, only=only, fake=a.fake, no_model=a.no_model, out_dir=a.out, fresh=a.fresh,
        allow_changed=a.allow_changed_questions, allow_partial=a.allow_partial,
        subset_arms=[x.strip() for x in a.subset_arms.split(",") if x.strip()])
    return 0


if __name__ == "__main__":
    sys.exit(main())
