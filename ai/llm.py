# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""The one audited entry point to the local language model.

Every script in ai/ that needs a model calls chat() here and nothing else.

- Only models in config.ALLOWED (gpt-oss:20b) can be called. The check runs
  before any network call, and again inside the HTTP helper for every payload
  that names a model, so qwen2.5 and gemma3 (installed on the same machine,
  excluded by AGENTS.md section 6) can never be reached through this module.
- On first use the installed digest of the model is read from GET /api/tags
  and compared with config.EXPECT_DIGEST_PREFIX.
- The reply is parsed as JSON and checked with a small standard-library
  validator (no jsonschema or pydantic dependency).
- The model's thinking text is discarded and never written to disk.
- Every call appends one line to ai/runs/<run>.jsonl. The first line of each
  run log is a _meta record: these are model candidates and call logs, not
  product content.

Standard library only (urllib, json, hashlib).

    python3 -m ai.llm --smoke    # three smoke calls, written to ai/runs/smoke.jsonl
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

if __package__ in (None, ""):
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from ai import config  # noqa: E402


class ModelNotAllowed(PermissionError):
    """Raised before any network call when a model outside config.ALLOWED is named."""


class DigestMismatch(RuntimeError):
    """Raised when the installed model's digest is not the expected one."""


class LLMError(RuntimeError):
    """Raised when the Ollama server cannot be reached or answers with an error."""


class ModelCallsDisabled(PermissionError):
    """Raised before any network call while AI_NO_MODEL_CALLS=1 (set by ai/build_all.py)."""


NO_CALLS_ENV = "AI_NO_MODEL_CALLS"


# ---------------------------------------------------------------------- guard

def check_model(model):
    """Raise ModelNotAllowed unless `model` is exactly one of config.ALLOWED."""
    if not isinstance(model, str) or model not in config.ALLOWED:
        raise ModelNotAllowed(
            f"model {model!r} is not allowed; only {sorted(config.ALLOWED)} may be called "
            "(AGENTS.md section 6: no Chinese-made models, no Gemma in the product)"
        )
    return model


def _http(method, path, payload=None, timeout=None):
    """The only place that opens a network connection."""
    if os.environ.get(NO_CALLS_ENV) == "1":
        raise ModelCallsDisabled(f"{NO_CALLS_ENV}=1: this run makes no model call (ai/build_all.py rebuilds "
                                 "from the logged model output only)")
    if payload is not None and "model" in payload:
        check_model(payload["model"])
    url = config.OLLAMA_URL.rstrip("/") + path
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout or config.DEFAULTS["timeout_s"]) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:500]
        raise LLMError(f"Ollama {method} {path} returned HTTP {e.code}: {body}") from e
    except urllib.error.URLError as e:
        raise LLMError(f"Ollama at {config.OLLAMA_URL} not reachable: {e.reason}") from e


_DIGESTS = {}


def model_digest(model=config.MODEL):
    """Return the installed digest of `model`, checked against the expected prefix."""
    check_model(model)
    if model in _DIGESTS:
        return _DIGESTS[model]
    tags = _http("GET", "/api/tags")
    found = [m for m in tags.get("models", []) if m.get("name") == model or m.get("model") == model]
    if not found:
        raise DigestMismatch(f"{model} is not installed on the Ollama server")
    digest = found[0].get("digest", "")
    if not digest.startswith(config.EXPECT_DIGEST_PREFIX):
        raise DigestMismatch(
            f"{model} has digest {digest[:12]!r}; expected prefix {config.EXPECT_DIGEST_PREFIX!r}")
    _DIGESTS[model] = digest
    return digest


# ---------------------------------------------------------------------- validator

_TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool, "null": type(None),
}


def _type_ok(value, t):
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[t])


def validate(value, schema, path="$"):
    """Check `value` against a small subset of JSON Schema. Returns a list of error strings.

    Supported keywords: type (string or list), enum, const, required, properties,
    additionalProperties (false or a schema), items, minItems, maxItems, uniqueItems,
    minLength, maxLength, minimum, maximum.
    """
    errors = []
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_type_ok(value, x) for x in types):
            return [f"{path}: expected {'/'.join(types)}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in enum")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: longer than {schema['maxLength']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: above {schema['maximum']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: more than {schema['maxItems']} items")
        if schema.get("uniqueItems"):
            seen = [json.dumps(v, sort_keys=True) for v in value]
            if len(set(seen)) != len(seen):
                errors.append(f"{path}: items not unique")
        if isinstance(schema.get("items"), dict):
            for i, v in enumerate(value):
                errors += validate(v, schema["items"], f"{path}[{i}]")
    if isinstance(value, dict):
        for k in schema.get("required", []):
            if k not in value:
                errors.append(f"{path}: missing required key {k!r}")
        props = schema.get("properties", {})
        for k, v in value.items():
            if k in props:
                errors += validate(v, props[k], f"{path}.{k}")
            else:
                extra = schema.get("additionalProperties", True)
                if extra is False:
                    errors.append(f"{path}: unexpected key {k!r}")
                elif isinstance(extra, dict):
                    errors += validate(v, extra, f"{path}.{k}")
    return errors


def parse_json(content):
    """Parse a model reply as JSON: plain, fenced in ``` or the first {...} span."""
    text = (content or "").strip()
    if not text:
        raise ValueError("empty content")
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.S)
    if fence:
        text = fence.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if 0 <= start < end:
            return json.loads(text[start:end + 1])
        raise


# ---------------------------------------------------------------------- run logs

RUN_LOG_META = {
    "_meta": {
        "what": "model candidates and call logs, not product content",
        "detail": ("One line per model call or candidate sentence, including rejected output. "
                   "The model's thinking text is never stored. Not copied to the public site."),
        "code_written_with": config.CODE_WRITTEN_WITH,
        "built_by": "ai/llm.py",
        "model": config.MODEL,
        "runner": config.RUNNER,
    }
}


def run_log_path(run):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", run or ""):
        raise ValueError(f"bad run name {run!r}")
    return config.RUNS_DIR / f"{run}.jsonl"


def log_line(run, record, fresh=False):
    """Append one JSON line to ai/runs/<run>.jsonl, writing the _meta line first if needed."""
    path = run_log_path(run)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fresh or not path.exists() or path.stat().st_size == 0:
        meta = dict(RUN_LOG_META["_meta"], created=_now())
        path.write_text(json.dumps({"_meta": meta}, ensure_ascii=False) + "\n", encoding="utf-8")
    if "thinking" in record:
        raise ValueError("thinking text must never be logged")
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, sort_keys=False) + "\n")


def _now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def prompt_sha256(messages, schema):
    blob = json.dumps({"messages": messages, "schema": schema}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def schema_instruction(schema):
    return ("Reply with only one JSON object, no other text. It must match this JSON schema:\n"
            + json.dumps(schema, ensure_ascii=False))


# ---------------------------------------------------------------------- chat

def chat(messages, schema, think=None, temperature=None, seed=None, num_ctx=None,
         num_predict=None, *, model=config.MODEL, format_mode=None, retries=None,
         run="calls", log_extra=None, timeout=None):
    """Call the local model once (plus up to `retries` format retries) and return a result dict.

    messages     list of {"role": "system"|"user"|"assistant", "content": str}
    schema       JSON schema (subset, see validate()) the reply must match
    think        'low' | 'medium' | 'high' | True | False (gpt-oss reasoning effort)
    format_mode  'schema': the schema is sent as Ollama's `format` and also stated in the prompt;
                 'prompt': no `format`, the schema is stated in the prompt only
    run          log file name under ai/runs/ (without .jsonl)
    log_extra    dict merged into the log line (for example {"record": "PSI-25", "step": "select"})

    Returns {"data", "valid", "errors", "raw", "model", "digest", "prompt_sha256", "options",
    "think", "format_mode", "eval_count", "eval_duration_ns", "tokens_per_s", "wall_s",
    "done_reason", "retries"}. `data` is the parsed object or None. Never raises for an
    invalid reply (valid is False); raises ModelNotAllowed, DigestMismatch or LLMError.
    """
    check_model(model)  # before anything else, in particular before any network call
    d = config.DEFAULTS
    think = d["think"] if think is None else think
    temperature = d["temperature"] if temperature is None else temperature
    seed = d["seed"] if seed is None else seed
    num_ctx = d["num_ctx"] if num_ctx is None else num_ctx
    num_predict = d["num_predict"] if num_predict is None else num_predict
    format_mode = d["format_mode"] if format_mode is None else format_mode
    retries = d["retries"] if retries is None else retries
    if format_mode not in ("schema", "prompt"):
        raise ValueError("format_mode must be 'schema' or 'prompt'")

    digest = model_digest(model)
    msgs = [dict(m) for m in messages]
    instruction = schema_instruction(schema)
    if msgs and msgs[0].get("role") == "system":
        msgs[0]["content"] = msgs[0]["content"].rstrip() + "\n\n" + instruction
    else:
        msgs.insert(0, {"role": "system", "content": instruction})
    psha = prompt_sha256(msgs, schema)
    options = {"temperature": temperature, "seed": seed, "num_ctx": num_ctx, "num_predict": num_predict}

    attempt, result = 0, None
    convo = list(msgs)
    while True:
        payload = {"model": model, "messages": convo, "stream": False, "think": think, "options": options}
        if format_mode == "schema":
            payload["format"] = schema
        t0 = time.monotonic()
        resp = _http("POST", "/api/chat", payload, timeout=timeout)
        wall = time.monotonic() - t0
        msg = resp.get("message") or {}
        content = msg.get("content") or ""
        thinking_chars = len(msg.get("thinking") or "")
        msg.pop("thinking", None)  # discarded, never stored
        data, errors = None, []
        try:
            data = parse_json(content)
            errors = validate(data, schema)
        except (ValueError, json.JSONDecodeError) as e:
            errors = [f"not JSON: {e}"]
        ec, ed = resp.get("eval_count") or 0, resp.get("eval_duration") or 0
        tps = round(ec / (ed / 1e9), 2) if ed else None
        result = {
            "data": data if not errors else None,
            "valid": not errors,
            "errors": errors,
            "raw": content,
            "model": model,
            "digest": digest,
            "prompt_sha256": psha,
            "options": options,
            "think": think,
            "format_mode": format_mode,
            "eval_count": ec,
            "eval_duration_ns": ed,
            "prompt_eval_count": resp.get("prompt_eval_count"),
            "tokens_per_s": tps,
            "wall_s": round(wall, 2),
            "done_reason": resp.get("done_reason"),
            "thinking_chars": thinking_chars,
            "retries": attempt,
        }
        line = {"time": _now(), "kind": "call"}
        line.update({k: v for k, v in result.items() if k != "data"})
        line["parsed"] = data
        if log_extra:
            line.update(log_extra)
        log_line(run, line)
        if result["valid"] or attempt >= retries:
            return result
        attempt += 1
        convo = msgs + [
            {"role": "assistant", "content": content},
            {"role": "user", "content": "That reply was not valid (" + "; ".join(errors[:5])
             + "). Reply again with only the JSON object that matches the schema."},
        ]


# ---------------------------------------------------------------------- smoke test

SMOKE_RECORDS = ("PSI-25", "PSI-69", "PSI-115")


def _smoke_prompt(inv, units):
    lines = "\n".join(f"[{u['id']}] {u['prefix']} {u['text']}" for u in units)
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["selected"],
        "properties": {
            "selected": {
                "type": "array", "minItems": 1, "maxItems": 3,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["id", "quote"],
                    "properties": {
                        "id": {"type": "string", "enum": [u["id"] for u in units]},
                        "quote": {"type": "string", "minLength": 1, "maxLength": 300},
                    },
                },
            }
        },
    }
    messages = [
        {"role": "system", "content": (
            "You select sentences from a NASA PSI record. Use only the numbered sentences given. "
            "Do not add facts, numbers or wording that is not in them.")},
        {"role": "user", "content": (
            f"Numbered sentences from NASA PSI record {inv}:\n{lines}\n\n"
            "Select up to 3 sentence IDs that state what the investigation set out to study. "
            "For each, copy a quote of 6 to 25 words exactly, character for character, from that sentence.")},
    ]
    return messages, schema


def smoke():
    """Three real calls on PSI-25, PSI-69 and PSI-115; decide format mode and temperature."""
    from ai import evidence
    ev = evidence.build()["records"]
    out_lines = []
    log_line("smoke", {"time": _now(), "kind": "start", "records": list(SMOKE_RECORDS),
                       "ollama_version": _http("GET", "/api/version").get("version")}, fresh=True)

    def run_three(format_mode, temperature):
        res = []
        for inv in SMOKE_RECORDS:
            units = [u for u in ev[inv]["units"] if u["field"] in ("objective", "hypothesis") and u["quotable"]]
            messages, schema = _smoke_prompt(inv, units)
            r = chat(messages, schema, format_mode=format_mode, temperature=temperature, retries=0,
                     run="smoke", log_extra={"record": inv, "trial": f"{format_mode}/t={temperature}"})
            verbatim = None
            if r["valid"]:
                by_id = {u["id"]: u["text"] for u in units}
                checks = [s["quote"] in by_id[s["id"]] for s in r["data"]["selected"]]
                verbatim = f"{sum(checks)}/{len(checks)}"
            res.append({"record": inv, "valid": r["valid"], "errors": r["errors"][:3],
                        "empty": not r["raw"].strip(), "done_reason": r["done_reason"],
                        "eval_count": r["eval_count"], "tokens_per_s": r["tokens_per_s"],
                        "wall_s": r["wall_s"], "quotes_verbatim": verbatim})
            print(json.dumps(res[-1]))
        return res

    trials = []
    fmt, temp = "schema", 0
    res = run_three(fmt, temp)
    trials.append({"format_mode": fmt, "temperature": temp, "results": res})
    if not all(x["valid"] for x in res):
        fmt = "prompt"
        res = run_three(fmt, temp)
        trials.append({"format_mode": fmt, "temperature": temp, "results": res})
    if any(x["empty"] or x["done_reason"] == "length" for x in res):
        temp = 0.3
        res = run_three(fmt, temp)
        trials.append({"format_mode": fmt, "temperature": temp, "results": res})
    final = trials[-1]["results"]
    loaded = [{"name": m.get("name"), "digest": (m.get("digest") or "")[:12],
               "gpu_share": round(m["size_vram"] / m["size"], 3) if m.get("size") else None,
               "context_length": m.get("context_length")}
              for m in _http("GET", "/api/ps").get("models", [])]
    tps = [x["tokens_per_s"] for x in final if x["tokens_per_s"]]
    walls = [x["wall_s"] for x in final]
    mean_wall = sum(walls) / len(walls)
    calls_per_record = 3  # component C: select, write, at most one repair
    projected_min = round(24 * calls_per_record * mean_wall / 60, 1)
    decision = {
        "time": _now(), "kind": "decision",
        "format_mode": fmt, "temperature": temp, "seed": config.DEFAULTS["seed"],
        "think": config.DEFAULTS["think"], "num_ctx": config.DEFAULTS["num_ctx"],
        "num_predict": config.DEFAULTS["num_predict"],
        "all_valid": all(x["valid"] for x in final),
        "tokens_per_s_mean": round(sum(tps) / len(tps), 2) if tps else None,
        "tokens_per_s": tps,
        "mean_wall_s_per_call": round(mean_wall, 2),
        "projected_24_record_batch_min": projected_min,
        "projection_assumes": f"{calls_per_record} calls per record at the mean wall time of these calls",
        "over_40_min": projected_min > 40,
        "trials": [{"format_mode": t["format_mode"], "temperature": t["temperature"],
                    "valid": sum(x["valid"] for x in t["results"])} for t in trials],
        "quotes_verbatim": {x["record"]: x["quotes_verbatim"] for x in final},
        "quote_note": ("quotes_verbatim counts model-copied quotes found character for character in the cited "
                       "unit; a model-copied quote is not trusted, code prints the unit text instead"),
        "loaded": loaded,
    }
    log_line("smoke", decision)
    print(json.dumps(decision, indent=1))
    return decision


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        smoke()
    else:
        print(__doc__)
