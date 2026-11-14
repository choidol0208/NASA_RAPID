# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Component C, first half: raw card candidates from gpt-oss:20b.

For each PSI record this script sends the record's numbered evidence units
(data/insights/evidence.json) to gpt-oss:20b through ai/llm.py and keeps the
model's raw candidate in ai/runs/cards_<timestamp>.jsonl. It does NOT write
data/insights/cards.json: gating (ai/checks.py), the one repair call and the
writer (ai/apply_cards.py) are later steps.

Method
- Prompt: ai/prompts/card_v2.txt (system and user sections). card_v1.txt was run once on
  PSI-25, PSI-69 and PSI-99 (ai/runs/cards_20261114-v1-trial3.jsonl); after reading those outputs
  v2 asks for one kind of statement per sentence (v1 joined an objective and a hypothesis),
  complete sentences of 15 to 30 words (v1 gave 39 and 44 words), a hypothesis sentence when
  the record has one, and plain hyphens (v1 typed U+2011).
- Schema (passed to Ollama as `format`, and stated in the prompt by ai/llm.py):
    {key_ids: [enum of eligible ids] 2..4,
     summary: [{evidence: [{id: enum of evidence ids, quote}] 1..3, text}] 1..3,
     abstain: boolean, abstain_reason: string}
  `evidence` comes before `text` inside each item, so the model picks the IDs
  and copies the quotes before it writes the sentence (attribute first).
  The enums make an invented ID impossible.
  Eligible key ids: quotable units of 8 to 45 words from objective, approach,
  hypothesis, researchImpacts. Evidence ids: every unit except the title,
  reference-like units and units shorter than 20 characters.
- Field-name guard. A quick test of this model put the field name where the
  statement text belongs. Here: the evidence lines carry no field label at all
  (only '[OBJ-3] sentence'); `text` has minLength 40 and `quote` minLength 20,
  so 'objective' or 'Stated hypothesis:' cannot fill either field; and a code
  shape check (shape_problems) rejects a field name, field label, heading or ID
  in place of text, and asks the model once more (shape retry, logged). That
  retry is about the reply's form only; the content repair belongs to
  ai/apply_cards.py.
- Pre-checks (informational only, logged next to the candidate; the real gates
  are ai/checks.py): ids valid, quote verbatim (exact, and after normalising
  quotes and whitespace), quote words, numbers and names in the sentence that
  are not in the cited quotes or units, modality frame and result verbs,
  hedge words kept, sentence length.

    python3 ai/cards_llm.py --records PSI-25,PSI-69,PSI-99
    python3 ai/cards_llm.py --all
    python3 ai/cards_llm.py --report ai/runs/cards_<timestamp>.jsonl
"""
import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import config, evidence, llm  # noqa: E402

PROMPT_DIR = config.AI_DIR / "prompts"
PROMPT_PATH = PROMPT_DIR / "card_v2.txt"  # v1 was the first trial (PSI-25, PSI-69, PSI-99); see the module docstring
BUILT_BY = "ai/cards_llm.py"

KEY_FIELDS = ("objective", "approach", "hypothesis", "researchImpacts")
KEY_MIN_WORDS, KEY_MAX_WORDS = 8, 45
MIN_EVIDENCE_CHARS = 20
# TEXT_MAX is a safety cap well above 35 words: with Ollama's grammar a maxLength cuts a sentence mid-clause
# (v1 trial: PSI-99 sentence 1 stopped at exactly 300 characters), so the 35-word limit is left to the gates.
TEXT_MIN, TEXT_MAX = 40, 420
QUOTE_MIN, QUOTE_MAX = 20, 520
MAX_WORDS = 35
SHAPE_RETRIES = 1

FIELD_WORDS = {"title", "record title", "objective", "objectives", "stated objective", "approach",
               "planned approach", "hypothesis", "stated hypothesis", "researchimpacts", "research impacts",
               "impact", "impacts", "impact statement", "impact statement in the record",
               "objectives include", "evidence", "end evidence"}
ID_RE = re.compile(r"\b(?:TTL|OBJ|APP|HYP|IMP)-\d+\b")
FRAMES = ("aims to", "aimed to", "was designed to", "sought to", "the objective was", "the record hypothesizes",
          "hypothesized that", "the hypothesis is", "the planned approach", "planned to", "proposes to")
RESULT_VERBS = ("showed", "shows", "found", "demonstrated", "confirmed", "observed", "revealed", "proved",
                "established")
GATE_HEDGES = ("may", "might", "could", "would", "expected", "potential", "suggest", "preliminary")
NUMBER_WORDS = ("one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
                "sixteen seventeen eighteen nineteen twenty").split()
NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")


# ---------------------------------------------------------------------- prompt and schema

def load_prompt(path=PROMPT_PATH):
    raw = Path(path).read_text(encoding="utf-8")
    body = raw[raw.index("### SYSTEM"):]
    system, user = body.split("### USER", 1)
    return system.replace("### SYSTEM", "", 1).strip(), user.strip(), hashlib.sha256(raw.encode("utf-8")).hexdigest()


def eligible_key_units(us):
    return [u for u in us if u["quotable"] and u["field"] in KEY_FIELDS
            and KEY_MIN_WORDS <= u["words"] <= KEY_MAX_WORDS]


def evidence_units(us):
    return [u for u in us if u["field"] != "title" and not u["reference_like"]
            and len(u["text"]) >= MIN_EVIDENCE_CHARS]


def build_schema(us):
    key_ids = [u["id"] for u in eligible_key_units(us)]
    ev_ids = [u["id"] for u in evidence_units(us)]
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["key_ids", "summary", "abstain", "abstain_reason"],
        "properties": {
            "key_ids": {
                "description": "IDs of the 2 to 4 evidence sentences that best say what the investigation studies and why",
                "type": "array", "minItems": min(2, len(key_ids)), "maxItems": min(4, len(key_ids)),
                "uniqueItems": True,
                "items": {"type": "string", "enum": key_ids},
            },
            "summary": {
                "description": "2 or 3 summary items; in each, choose evidence first, then write text from it",
                "type": "array", "minItems": 1, "maxItems": 3,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["evidence", "text"],
                    "properties": {
                        "evidence": {
                            "description": "the 1 to 3 evidence sentences this summary sentence rests on",
                            "type": "array", "minItems": 1, "maxItems": 3,
                            "items": {
                                "type": "object", "additionalProperties": False,
                                "required": ["id", "quote"],
                                "properties": {
                                    "id": {"description": "ID of one evidence sentence", "type": "string",
                                           "enum": ev_ids},
                                    "quote": {"description": ("5 to 20 consecutive words copied character for "
                                                              "character from the sentence with this ID; never "
                                                              "an ID, a field name or a heading"),
                                              "type": "string", "minLength": QUOTE_MIN, "maxLength": QUOTE_MAX},
                                },
                            },
                        },
                        "text": {"description": ("one plain-English sentence of at most 35 words, written only "
                                                 "from the quotes above; never a field name, heading or ID"),
                                 "type": "string", "minLength": TEXT_MIN, "maxLength": TEXT_MAX},
                    },
                },
            },
            "abstain": {"description": "true only if the evidence supports no summary sentence",
                        "type": "boolean"},
            "abstain_reason": {"description": "empty string unless abstain is true", "type": "string",
                               "maxLength": 300},
        },
    }


def evidence_block(us):
    allowed = {u["id"] for u in evidence_units(us)}
    return "\n".join(f"[{u['id']}] {u['text']}" for u in us if u["id"] in allowed)


def build_messages(inv, rec, system, user_tpl):
    user = (user_tpl.replace("<<RECORD>>", inv).replace("<<TITLE>>", rec["title"])
            .replace("<<EVIDENCE>>", evidence_block(rec["units"])))
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


# ---------------------------------------------------------------------- shape check and pre-checks

def _bare(s):
    return re.sub(r"[^a-z ]+", " ", s.lower()).split()


def shape_problems(data, rec):
    """Problems with the reply's form (not its content): a field name, heading or ID in place of text."""
    if data is None:
        return ["no parsed reply"]
    labels = {evidence.FIELDS[f][1].lower().rstrip(":") for f in evidence.FIELDS}
    title = rec["title"].strip().lower()
    out = []

    def check(where, s):
        st = s.strip()
        low = " ".join(_bare(st))
        if low in FIELD_WORDS or low in labels:
            out.append(f"{where}: a field name or heading in place of text ({st!r})")
        elif any(st.lower().startswith(lab) for lab in labels | {"objective:", "hypothesis:", "approach:", "impact:"}):
            out.append(f"{where}: starts with a field label ({st[:40]!r})")
        if ID_RE.search(st):
            out.append(f"{where}: contains a unit ID ({ID_RE.search(st).group(0)})")
        if st.lower().rstrip(".") == title:
            out.append(f"{where}: the record title in place of text")

    for i, item in enumerate(data.get("summary", [])):
        check(f"summary[{i}].text", item.get("text", ""))
        if len(item.get("text", "").split()) < 6:
            out.append(f"summary[{i}].text: fewer than 6 words")
        for j, e in enumerate(item.get("evidence", [])):
            check(f"summary[{i}].evidence[{j}].quote", e.get("quote", ""))
    return out


def _norm(s):
    return evidence.normalise(s)


def _numbers(s):
    toks = set(NUM_RE.findall(s))
    words = {w for w in re.findall(r"[a-z]+", s.lower()) if w in NUMBER_WORDS}
    return toks | words


def _names(sentence):
    """Tokens a reader would take as names: two capitals, capital plus digit, or capitalised mid-sentence."""
    toks = re.findall(r"[A-Za-z][A-Za-z0-9’'\-/]*", sentence)
    out = []
    for i, t in enumerate(toks):
        caps = sum(c.isupper() for c in t)
        if caps >= 2 or (t[0].isupper() and any(c.isdigit() for c in t)) or (i > 0 and t[0].isupper()):
            out.append(t.strip("’'-/"))
    return out


def precheck(item, rec):
    """Informational checks of one summary item; not the gates (ai/checks.py is)."""
    by_id = {u["id"]: u for u in rec["units"]}
    text = item["text"]
    ev = item["evidence"]
    ids_valid = all(e["id"] in by_id for e in ev)
    quotes = []
    for e in ev:
        u = by_id.get(e["id"])
        unit_text = u["text"] if u else ""
        q = e["quote"]
        quotes.append({
            "id": e["id"],
            "field": u["field"] if u else None,
            "quote_words": len(q.split()),
            "verbatim": bool(u) and q in unit_text,
            "verbatim_normalised": bool(u) and _norm(q) in _norm(unit_text),
            "whole_unit": bool(u) and _norm(q) == _norm(unit_text),
        })
    cited_q = " ".join(e["quote"] for e in ev)
    cited_u = " ".join(by_id[e["id"]]["text"] for e in ev if e["id"] in by_id)
    record_text = rec["title"] + " " + " ".join(u["text"] for u in rec["units"])
    nums = sorted(_numbers(text))
    names = _names(text)
    fields = {q["field"] for q in quotes}
    low = text.lower()
    hedges_cited = sorted({h for h in GATE_HEDGES if re.search(rf"\b{h}\b", cited_q.lower())})
    return {
        "words": len(text.split()),
        "ids_valid": ids_valid,
        "quotes": quotes,
        "numbers_not_in_quotes": [n for n in nums if n not in _numbers(cited_q)],
        "numbers_not_in_cited_units": [n for n in nums if n not in _numbers(cited_u)],
        "names_not_in_cited_units_or_title": sorted({n for n in names
                                                     if n.lower() not in (cited_u + " " + rec["title"]).lower()}),
        "names_not_in_record": sorted({n for n in names if n.lower() not in record_text.lower()}),
        "only_objective_hypothesis_approach": bool(fields) and fields <= {"objective", "hypothesis", "approach"},
        "frame_used": [f for f in FRAMES if f in low],
        "result_verbs_not_in_quote": [v for v in RESULT_VERBS
                                      if re.search(rf"\b{v}\b", low) and not re.search(rf"\b{v}\b", cited_q.lower())],
        "hedges_in_cited_quotes": hedges_cited,
        "hedge_kept": (not hedges_cited) or any(re.search(rf"\b{h}\b", low) for h in GATE_HEDGES),
        "complete_sentence": text.rstrip().endswith((".", "!", "?")),
        "cut_at_max_length": len(text) >= TEXT_MAX,
        "kinds_cited": sorted(f for f in fields if f),
        "non_ascii_in_text": sorted({c for c in text if ord(c) > 127}),
    }


# ---------------------------------------------------------------------- run

def _now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def start_log(run, prompt_sha, records, prompt_path=PROMPT_PATH):
    path = llm.run_log_path(run)
    path.parent.mkdir(parents=True, exist_ok=True)
    first = {"_meta": {
        "what": "candidates, including rejected sentences; not product content",
        "detail": ("Raw gpt-oss:20b card candidates and call logs for component C (first half). One 'call' "
                   "line per model call (written by ai/llm.py) and one 'candidate' line per record with "
                   "informational pre-checks. Not gated; the gates, repair and cards.json are later steps. "
                   "The model's thinking text is never stored. Not copied to the public site."),
        "built_by": BUILT_BY,
        "code_written_with": config.CODE_WRITTEN_WITH,
        "model": config.MODEL,
        "model_digest": llm.model_digest(),
        "runner": config.RUNNER,
        "prompt_file": Path(prompt_path).resolve().relative_to(config.ROOT).as_posix(),
        "prompt_file_sha256": prompt_sha,
        "params": {k: config.DEFAULTS[k] for k in ("think", "temperature", "seed", "num_ctx", "num_predict",
                                                    "format_mode", "retries")},
        "records": records,
        "evidence_sha256": evidence.load()["_meta"].get("content_sha256"),
        "created": _now(),
    }}
    path.write_text(json.dumps(first, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def run_record(inv, run, system, user_tpl):
    rec = evidence.record(inv)
    schema = build_schema(rec["units"])
    messages = build_messages(inv, rec, system, user_tpl)
    t0 = time.monotonic()
    calls = []
    r = llm.chat(messages, schema, run=run, log_extra={"record": inv, "step": "card", "attempt": 0})
    calls.append(r)
    shape = shape_problems(r["data"], rec) if r["valid"] else []
    shape_retries = 0
    while r["valid"] and shape and shape_retries < SHAPE_RETRIES:
        shape_retries += 1
        retry_msgs = messages + [
            {"role": "assistant", "content": r["raw"]},
            {"role": "user", "content": ("The form of that reply is wrong: " + "; ".join(shape)
                                         + ". 'text' and 'quote' must hold sentence words copied or written "
                                           "from the evidence, never an ID, field name or heading. "
                                           "Reply again with the whole JSON object.")},
        ]
        r = llm.chat(retry_msgs, schema, run=run,
                     log_extra={"record": inv, "step": "card_shape_retry", "attempt": shape_retries})
        calls.append(r)
        shape = shape_problems(r["data"], rec) if r["valid"] else []
    seconds = round(time.monotonic() - t0, 2)
    data = r["data"]
    sentences = []
    if data:
        for i, item in enumerate(data["summary"]):
            sentences.append({"n": i, "text": item["text"], "evidence": item["evidence"],
                              "precheck": precheck(item, rec)})
    cand = {
        "time": _now(), "kind": "candidate", "record": inv,
        "valid": r["valid"], "errors": r["errors"], "shape_problems": shape, "shape_retries": shape_retries,
        "format_retries": sum(c["retries"] for c in calls),
        "calls": len(calls) + sum(c["retries"] for c in calls),
        "seconds": seconds, "eval_count": sum(c["eval_count"] for c in calls),
        "tokens_per_s": r["tokens_per_s"], "done_reason": r["done_reason"],
        "prompt_sha256": calls[0]["prompt_sha256"], "digest": r["digest"], "options": r["options"],
        "think": r["think"], "format_mode": r["format_mode"],
        "key_ids": data["key_ids"] if data else None,
        "abstain": data["abstain"] if data else None,
        "abstain_reason": data["abstain_reason"] if data else None,
        "sentences": sentences,
        "schema_enums": {"key_ids": schema["properties"]["key_ids"]["items"]["enum"],
                         "evidence_ids": schema["properties"]["summary"]["items"]["properties"]["evidence"]
                         ["items"]["properties"]["id"]["enum"]},
    }
    llm.log_line(run, cand)
    return cand


def row(c):
    s = c["sentences"]
    q = [x for sen in s for x in sen["precheck"]["quotes"]]
    return {
        "record": c["record"], "valid": c["valid"], "abstain": c["abstain"],
        "sentences": len(s),
        "ids_valid": f"{sum(sen['precheck']['ids_valid'] for sen in s)}/{len(s)}",
        "quotes_verbatim": f"{sum(x['verbatim'] for x in q)}/{len(q)}",
        "quotes_verbatim_normalised": f"{sum(x['verbatim_normalised'] for x in q)}/{len(q)}",
        "quotes_under_5_words": sum(1 for x in q if x["quote_words"] < 5 and not x["whole_unit"]),
        "numbers_not_in_quotes": sum(len(sen["precheck"]["numbers_not_in_quotes"]) for sen in s),
        "names_not_in_cited": sum(len(sen["precheck"]["names_not_in_cited_units_or_title"]) for sen in s),
        "frame_missing": sum(1 for sen in s if sen["precheck"]["only_objective_hypothesis_approach"]
                             and not sen["precheck"]["frame_used"]),
        "result_verbs": sum(len(sen["precheck"]["result_verbs_not_in_quote"]) for sen in s),
        "hedge_dropped": sum(1 for sen in s if not sen["precheck"]["hedge_kept"]),
        "over_35_words": sum(1 for sen in s if sen["precheck"]["words"] > MAX_WORDS),
        "incomplete": sum(1 for sen in s if not sen["precheck"].get("complete_sentence", True)),
        "mixed_kinds": sum(1 for sen in s if len(sen["precheck"].get("kinds_cited", [])) > 1),
        "kinds": [",".join(sen["precheck"].get("kinds_cited", [])) for sen in s],
        "shape_retries": c["shape_retries"], "format_retries": c["format_retries"],
        "seconds": c["seconds"], "eval_count": c["eval_count"], "done_reason": c["done_reason"],
    }


def report(path):
    cands = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        if d.get("kind") == "candidate":
            cands.append(d)
    return [row(c) for c in cands], cands


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--records", help="comma-separated PSI ids")
    ap.add_argument("--all", action="store_true", help="all 24 records")
    ap.add_argument("--run", help="run name (default cards_<timestamp>)")
    ap.add_argument("--prompt", default=str(PROMPT_PATH), help="prompt file (default card_v2.txt)")
    ap.add_argument("--report", help="print the per-record table of an existing cards_*.jsonl")
    a = ap.parse_args(argv)
    if a.report:
        rows, _ = report(a.report)
        for r in rows:
            print(json.dumps(r))
        return 0
    ev = evidence.load()
    if a.all:
        recs = sorted(ev["records"], key=lambda k: int(k.split("-")[1]))
    elif a.records:
        recs = [x.strip() for x in a.records.split(",") if x.strip()]
    else:
        ap.error("give --records or --all")
    for inv in recs:
        if inv not in ev["records"]:
            ap.error(f"unknown record {inv}")
    run = a.run or "cards_" + datetime.now().strftime("%Y%m%d-%H%M%S")
    system, user_tpl, psha = load_prompt(a.prompt)
    path = start_log(run, psha, recs, a.prompt)
    print(f"log: {path}", flush=True)
    t0 = time.monotonic()
    for inv in recs:
        try:
            c = run_record(inv, run, system, user_tpl)
        except llm.LLMError as e:
            llm.log_line(run, {"time": _now(), "kind": "error", "record": inv, "error": str(e)})
            print(json.dumps({"record": inv, "error": str(e)}), flush=True)
            continue
        print(json.dumps(row(c)), flush=True)
    llm.log_line(run, {"time": _now(), "kind": "end", "records": len(recs),
                       "seconds": round(time.monotonic() - t0, 1)})
    print(f"total seconds: {round(time.monotonic() - t0, 1)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
