# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""One turn of the assistant (ai/assistant/DESIGN.md section 10).

understand (model readings + rule parser, grounding, agreement, one clarifying question)
-> plan (code table) -> look up (tools, numbered facts) -> write (model, cites fact ids)
-> check (code gates, one repair, model checker, template fallback) -> deliver (RESPONSE with trace).

At most four model calls per turn (Budget). Without a model every step still runs with the rule parser and
template answers. Run-time model calls log to the git-ignored ai/assistant/_runtime/.

    from ai.assistant import pipeline
    r = pipeline.turn("Which NASA tests are closest to a cotton fabric fire in a lunar habitat?")
"""
import copy
import hashlib
import json
import os
import socket
import threading
import re
import time
import unicodedata
import uuid
from collections import OrderedDict
from datetime import datetime

from ai import config, llm
from ai.assistant import check as ck, plan as planmod, request as rq, texts, tools, understand, write

ARMS = ("full", "no_repeat", "no_gates", "no_checker", "single_call")
# DESIGN.md 8.1. num_predict counts the model's thinking tokens too: the first live run (15 Nov) ended a write
# call at 1600 tokens with 1,200 of them spent on thinking (done_reason 'length'), so the limits are higher than
# the contract's first values.
SETTINGS = {
    "understand_1": {"think": "low", "temperature": 0, "seed": 7, "num_predict": 1200},
    "understand_2": {"think": "low", "temperature": 0.7, "seed": 23, "num_predict": 1200},
    "write": {"think": "medium", "temperature": 0.2, "seed": 7, "num_predict": 3200},
    # repair at low effort: it fixes named failures; at medium the first live repair spent 2,509 tokens (53 s)
    "repair": {"think": "low", "temperature": 0.2, "seed": 11, "num_predict": 3200},
    "check": {"think": "medium", "temperature": 0, "seed": 7, "num_predict": 2400},
    "baseline": {"think": "medium", "temperature": 0.2, "seed": 7, "num_predict": 3600},
}
_DATA = None
_DATA_LOCK = threading.Lock()
_CACHE = OrderedDict()
_CACHE_MAX = 256
_STATUS = {"t": 0.0, "value": None}


class Budget:
    def __init__(self, max_calls=None):
        self.max = config.ASSISTANT["max_model_calls"] if max_calls is None else max_calls
        self.used = 0

    def remaining(self):
        return self.max - self.used

    def take(self):
        if self.used >= self.max:
            return False
        self.used += 1
        return True


def get_data():
    """The shared Data object, reloaded when a listed file changed."""
    global _DATA
    with _DATA_LOCK:
        if _DATA is None or _DATA.version != tools.data_version():
            _DATA = tools.Data()
        return _DATA


def model_status(force=False):
    """llm.server_status(), cached for 30 s."""
    if os.environ.get(llm.NO_CALLS_ENV) == "1":
        return llm.server_status()
    if force or _STATUS["value"] is None or time.monotonic() - _STATUS["t"] > 30:
        _STATUS["value"] = llm.server_status()
        _STATUS["t"] = time.monotonic()
    return _STATUS["value"]


def decide_mode(mode=None):
    if os.environ.get(llm.NO_CALLS_ENV) == "1":
        return "no_model", f"{llm.NO_CALLS_ENV}=1"
    if mode in ("live", "no_model"):
        return mode, None if mode == "live" else "no model requested"
    st = model_status()
    if st["reachable"] and st["installed"] and st["digest_ok"]:
        return "live", None
    return "no_model", st["reason"]


def cache_clear():
    _CACHE.clear()


def _cache_get(key):
    if key in _CACHE:
        _CACHE.move_to_end(key)
        return copy.deepcopy(_CACHE[key])
    return None


def _cache_put(key, value):
    _CACHE[key] = copy.deepcopy(value)
    _CACHE.move_to_end(key)
    while len(_CACHE) > _CACHE_MAX:
        _CACHE.popitem(last=False)


def _sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


class Turn:
    """The mutable record of one turn: trace steps, events, budget."""

    def __init__(self, chat, mode, arm, on_event, run, log_dir):
        self.chat, self.mode, self.arm, self.on_event = chat, mode, arm, on_event
        self.run, self.log_dir = run, log_dir
        self.id = uuid.uuid4().hex[:12]
        self.budget = Budget()
        self.steps = []
        self.t0 = time.monotonic()
        self._step_t = None
        self._step_calls = 0
        self.calls_log = []

    def emit(self, ev):
        if self.on_event:
            try:
                self.on_event(ev)
            except Exception:  # noqa: BLE001 - a broken listener never ends the turn
                pass

    def start(self, step):
        self._step_t = time.monotonic()
        self._step_calls = self.budget.used
        self.emit({"event": "step", "step": step, "status": "start", "label": texts.STEPS[step]})

    def done(self, step, summary, detail=None):
        ms = int((time.monotonic() - self._step_t) * 1000)
        calls = self.budget.used - self._step_calls
        rec = {"step": step, "label": texts.STEPS[step], "summary": summary, "ms": ms, "model_calls": calls}
        if detail is not None:
            rec["detail"] = detail
        self.steps.append(rec)
        self.emit({"event": "step", "step": step, "status": "done", "summary": summary, "ms": ms, "model_calls": calls})

    def call(self, step, messages, schema):
        """One model call within the budget; None on budget, invalid reply, timeout or server error."""
        if self.mode != "live" or not self.budget.take():
            return None
        s = SETTINGS[step]
        t = time.monotonic()
        try:
            r = self.chat(messages, schema, think=s["think"], temperature=s["temperature"], seed=s["seed"],
                          num_ctx=config.DEFAULTS["num_ctx"], num_predict=s["num_predict"], format_mode="schema",
                          retries=0, run=self.run, log_extra={"step": step, "turn_id": self.id, "arm": self.arm},
                          timeout=config.ASSISTANT["call_timeout_s"], log_dir=self.log_dir)
        except (llm.LLMError, llm.DigestMismatch, llm.ModelCallsDisabled, socket.timeout, TimeoutError, OSError) as e:
            self.calls_log.append({"step": step, "valid": False, "error": type(e).__name__,
                                   "ms": int((time.monotonic() - t) * 1000)})
            return {"invalid": True, "valid": False, "error": type(e).__name__, "data": None}
        self.calls_log.append({"step": step, "valid": r["valid"], "ms": int((time.monotonic() - t) * 1000),
                               "eval_count": r.get("eval_count"), "errors": r.get("errors", [])[:3]})
        return r if r["valid"] else {"invalid": True, **r}


# ---------------------------------------------------------------- understand
def _understand(tr, message, state, vocab):
    """-> (request, detail, summary)."""
    R = rq.rule_reading(message, state, vocab)
    readings_detail = [{"reader": "R", "valid": True, "ms": 0}]
    readers = {"R": R}
    removed_all, unresolved, assumptions, clarify_names = [], [], [], None
    m1 = m2 = None
    if tr.mode == "live" and tr.arm != "single_call":
        msgs = understand.messages(message, state, vocab)
        t = time.monotonic()
        r1 = tr.call("understand_1", msgs, rq.READING)
        readings_detail.append({"reader": "M1", "valid": bool(r1 and not r1.get("invalid")),
                                "ms": int((time.monotonic() - t) * 1000)})
        if r1 and not r1.get("invalid"):
            m1, rem, unr, ass, cl = rq.ground(r1["data"], message, state, vocab)
            removed_all += rem
            unresolved += unr
            assumptions += ass
            clarify_names = clarify_names or cl
        need_m2 = tr.arm != "no_repeat" and (
            m1 is None or not rq.m1_matches_rules(m1, R)
            or (not R.get("intent_opinion") and len((message or "").split()) > 3)
            or _m1_misses_needed(m1, state, vocab))
        if need_m2:
            t = time.monotonic()
            r2 = tr.call("understand_2", msgs, rq.READING)
            readings_detail.append({"reader": "M2", "valid": bool(r2 and not r2.get("invalid")),
                                    "ms": int((time.monotonic() - t) * 1000)})
            if r2 and not r2.get("invalid"):
                m2, rem, unr, ass, cl = rq.ground(r2["data"], message, state, vocab)
                removed_all += [x for x in rem if x not in removed_all]
                unresolved += [x for x in unr if x not in unresolved]
                assumptions += [a for a in ass if a not in assumptions]
                clarify_names = clarify_names or cl
    if tr.arm == "no_repeat" and m1 is not None:
        readers = {"M1": m1}
        values = {f: m1.get(f) for f in rq.FIELDS}
        agreement = {rq.PATH[f]: "single" for f in rq.FIELDS if m1.get(f) not in (None, [], False)}
        conflicts = {}
    else:
        if m1 is not None:
            readers["M1"] = m1
        if m2 is not None:
            readers["M2"] = m2
        values, agreement, conflicts = rq.agree(readers)
        if m1 is None and m2 is None:
            agreement = {k: "rules_only" for k, v in agreement.items()}
    order = [x for x in (m1, m2, R) if x is not None]
    extra = {}
    for k in ("item_words", "compare_with", "term", "keywords", "english", "flow", "pick_from_last"):
        extra[k] = next((x.get(k) for x in order if x.get(k) not in (None, [], "")), None)
    extra["new_topic"] = (m1 or m2 or R).get("new_topic")
    extra["tests"] = R.get("tests") or []
    if not extra.get("compare_with") and R.get("compare_with"):
        extra["compare_with"] = R["compare_with"]
    if not extra.get("keywords"):
        extra["keywords"] = R.get("keywords") or []
    if not extra.get("flow"):
        extra["flow"] = R.get("flow")
    pending = (state or {}).get("pending_clarify")
    prev = (state or {}).get("request")
    if prev and not pending and SAME_AS_BEFORE.search(message or "") and len((message or "").split()) <= 10 \
            and values.get("intent") not in ("out_of_scope", "help") and prev.get("intent") not in ("help", "out_of_scope"):
        # "And the same for smoke generation?" keeps the previous intent; only the named field changes (changed at
        # integration, 15 Nov: the readings took it as question_evidence and the turn asked for an environment)
        values["intent"] = prev["intent"]
        agreement["intent"] = "carried"
        extra["new_topic"] = False
    # a short reply that gives the value the pending question asked for continues the pending request even when a
    # reading called it out of scope ("A Mars base" after "Which environment is this for?"; changed at integration,
    # 15 Nov, after the recording run)
    answers_pending = bool(pending and prev and (
        (str(pending.get("field", "")).startswith("environment") and (values.get("preset") or values.get("o2_pct")))
        or (pending.get("field") == "equipment" and values.get("equipment"))))
    if pending and prev and len((message or "").split()) <= 8 and (
            values.get("intent") not in ("out_of_scope",) or answers_pending):
        # an answer to the clarifying question continues the pending request
        values["intent"] = prev["intent"]
        values["asks_verdict"] = values.get("asks_verdict") or prev.get("asks_verdict")
        values["asks_prediction"] = values.get("asks_prediction") or prev.get("asks_prediction")
        extra["new_topic"] = False
        if not extra.get("item_words") and prev["item"].get("words"):
            extra["item_words"] = prev["item"]["words"]
        if prev.get("english") and extra.get("english"):
            extra["english"] = (prev["english"] + " " + extra["english"])[:300]
    req = rq.build_request(values, agreement, norm_extra=extra, state=state, vocab=vocab, removed=removed_all,
                           unresolved=unresolved, assumptions=assumptions, clarify=clarify_names, conflicts=conflicts)
    for x in removed_all:
        req["assumptions"].append({"field": x["field"], "text": texts.ASSUME_UNGROUNDED.format(
            field=x["field"].split(".")[-1].replace("_", " "), value=x["value"])})
    fields = [k for k in agreement]
    n_agree = sum(1 for k in fields if agreement[k] in ("agree", "majority"))
    model_readings = sum(1 for d in readings_detail if d["reader"] != "R")
    if model_readings == 0:
        summary = texts.SUMMARY["understand_no_model"]
    else:
        summary = texts.SUMMARY["understand_live"].format(readers=len(readings_detail), model_readings=model_readings,
                                                          agree=n_agree, fields=len(fields))
    detail = {"readings": readings_detail, "agreement": req["agreement"], "removed_ungrounded": removed_all,
              "asked": req["clarify"] is not None, "conflicts": {k: [r for r, _ in v] for k, v in conflicts.items()}}
    return req, detail, summary


def _m1_misses_needed(m1, state, vocab):
    probe = rq.build_request({f: m1.get(f) for f in rq.FIELDS}, {}, norm_extra={
        k: m1.get(k) for k in ("item_words", "compare_with", "term", "keywords", "new_topic", "english", "flow")},
        state=state, vocab=vocab)
    return rq.needed_missing(probe["intent"], probe) is not None


# ---------------------------------------------------------------- notices
def _notices(req, mode, facts, lookup):
    out = []
    if req["asks_verdict"]:
        out.append({"id": "refuse_verdict", "text": texts.NOTICES["refuse_verdict"]})
    if req["asks_prediction"]:
        out.append({"id": "refuse_prediction", "text": texts.NOTICES["refuse_prediction"]})
    needed = None
    st = lookup.get("state") or {}
    if req["intent"] == "explain" and req.get("term") and not facts:
        needed = texts.NEEDED["term"].format(term=req["term"])
    elif req["item"].get("words") and not req["item"].get("material"):
        q = req.get("dashboard_q") or ""
        sc = rq.scorer.interpret(q + " " + req["item"]["words"], rq.load_vocab()["cfg"])[0]
        if not sc.get("fuel_material") and not sc.get("fuel_class") and not sc.get("fuel_phase"):
            needed = texts.NEEDED["material"].format(words=req["item"]["words"])
    elif req.get("unresolved_names") and not req.get("investigations"):
        needed = texts.NEEDED["investigation"].format(name=", ".join(req["unresolved_names"]))
    elif st.get("no_hits") and not facts:
        needed = texts.NEEDED["search"].format(keywords=", ".join(st["no_hits"]))
    if needed:
        out.append({"id": "not_in_files", "text": texts.NOTICES["not_in_files"].format(needed=needed)})
    if mode == "no_model":
        out.append({"id": "no_model", "text": texts.NOTICES["no_model"]})
    return out


# ---------------------------------------------------------------- write and check
_TYPO = {"\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2212": "-", "\u00a0": " ", "\u202f": " ",
         "\u2009": " "}


SAME_AS_BEFORE = re.compile(r"\b(?:the same|same for|same thing|likewise)\b|똑같이|마찬가지|同じ|lo mismo", re.I)
BACKREF = re.compile(r"^(?:of (?:those|these|them)|these|those|they|both|neither|the (?:remaining|other|rest))\b",
                     re.I)


def clean_text(t):
    """Typographic variants the model writes (non-breaking hyphens in 'PSI-20', subscript digits in 'O2', thin
    spaces) become plain characters before any gate reads the sentence; nothing else is changed."""
    t = unicodedata.normalize("NFKC", t or "")
    t = re.sub(r"\s*[\(\[]\s*(?:facts?\s+)?F\d+(?:\s*(?:,|;|and)\s*F\d+)*\s*[\)\]]", "", t)  # '(F1, F2)' in the text
    for a, b in _TYPO.items():
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def _is_aim(f):
    return bool(f) and (f.get("kind") == "nasa_sentence" or f.get("quote")) and f.get("field") in ck.LP.NON_RESULT_FIELDS


def _gate_all(sentences, by_id, req, turn_ids):
    """Gate failures per sentence. A sentence that fails only the record-frame gate because it also cites a record's
    aim, hypothesis or approach next to team facts is gated again without those record facts; if every gate then
    passes (numbers and names must still be in the facts it keeps), its citations are narrowed in place and the
    sentence is kept (s["pruned"] lists the dropped ids). Added after the first evaluation questions of 15 Nov:
    the writer cited a planned-approach quote for '75% cotton' beside the ranking fact that holds the same values."""
    fails = []
    for i, s in enumerate(sentences, 1):
        cited = [by_id.get(x) for x in s["facts"]]
        g = ck.gate_sentence(s["text"], [c for c in cited if c], req, turn_ids, cited_ids=s["facts"])
        if g and all(gate == "modality" for gate, _ in g):
            keep = [x for x in s["facts"] if by_id.get(x) and not _is_aim(by_id[x])]
            if keep and len(keep) < len(s["facts"]):
                g2 = ck.gate_sentence(s["text"], [by_id[x] for x in keep], req, turn_ids, cited_ids=keep)
                if not g2:
                    s["pruned"] = [x for x in s["facts"] if x not in keep]
                    s["facts"] = keep
                    g = g2
        fails.append(g)
    return fails


_SALVAGE_ERR = re.compile(r"^\$\.sentences(?:\[\d+\]\.facts)?: more than \d+ items$")


def _salvage(r, sch):
    """A write or repair reply whose only schema errors are too many sentences or too many fact ids in a sentence
    is kept instead of discarded (added after the red-team and clean-clone runs of 15 Nov: 3 of 24 writes were lost
    for this alone). The sentences past the limit are dropped; a sentence citing more than 4 facts stays and fails
    the citation gate on its own. Returns the data, or None when the reply cannot be kept."""
    if not r or not r.get("invalid") or not r.get("errors") or not all(_SALVAGE_ERR.match(e) for e in r["errors"]):
        return None
    try:
        data = llm.parse_json(r.get("raw") or "")
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("sentences"), list):
        return None
    data["sentences"] = data["sentences"][:sch["properties"]["sentences"]["maxItems"]]
    loose = copy.deepcopy(sch)
    loose["properties"]["sentences"]["items"]["properties"]["facts"].pop("maxItems", None)
    if llm.validate(data, loose):
        return None
    return data


def _call_write(tr, step, msgs, sch):
    r = tr.call(step, msgs, sch)
    if r and r.get("invalid"):
        data = _salvage(r, sch)
        if data is not None:
            return dict(r, invalid=False, valid=True, data=data, salvaged=list(r["errors"]))
    return r


def _write_and_check(tr, req, vocab, notices, facts, panels, message):
    """-> (answer, chosen panel ids, followup texts, gate_report, write detail, check detail)."""
    by_id = {f["id"]: f for f in facts}
    wf = tools.writer_facts(facts)
    turn_ids = set(by_id)
    report = {"written": 0, "repaired": 0, "removed": 0, "removed_by_gate": {}, "checker_no": 0, "kept": 0,
              "fallback": False, "fallback_reason": None, "sentences": []}
    removed = []
    need_calls = 1 if tr.arm == "no_checker" else 2
    wdetail = {"sentences": 0, "valid": False, "facts_given": len(wf)}
    cdetail = {"gate_failures": [], "repair": False, "checker": {"yes": 0, "no": 0}}

    def fallback(reason):
        report["fallback"] = True
        report["fallback_reason"] = reason
        return write.template_answer(facts, req)

    if tr.mode != "live" or tr.budget.remaining() < need_calls or not wf:
        reason = "no model" if tr.mode != "live" else ("no facts" if not wf else "budget")
        return {"origin": "template", "sentences": write.template_answer(facts, req), "removed": []}, [], [], \
            dict(report, fallback=tr.mode == "live", fallback_reason=reason), wdetail, cdetail
    msgs = write.messages(req, vocab, notices, wf, panels)
    sch = write.schema(req, wf, panels)
    w = _call_write(tr, "write", msgs, sch)
    ok = bool(w and not w.get("invalid"))
    tr.done("write", texts.SUMMARY["write_model"].format(written=len(w["data"]["sentences"])) if ok
            else texts.SUMMARY["write_template"], {"sentences": len(w["data"]["sentences"]) if ok else 0, "valid": ok,
                                                   "facts_given": len(wf)})
    tr.start("check")
    tr.wrote = True
    if not w or w.get("invalid"):
        wdetail["valid"] = False
        sents = fallback("write failed" if w else "write call not made")
        return {"origin": "template", "sentences": sents, "removed": []}, [], [], report, wdetail, cdetail
    data = w["data"]
    wdetail.update({"sentences": len(data["sentences"]), "valid": True})
    if w.get("salvaged"):
        wdetail["salvaged"] = w["salvaged"][:3]
        report["salvaged"] = w["salvaged"][:3]
    written = [{"text": clean_text(s["text"]), "facts": list(s["facts"])} for s in data["sentences"]]
    report["written"] = len(written)
    fails = _gate_all(written, by_id, req, turn_ids)
    for i, (s, g) in enumerate(zip(written, fails), 1):
        report["sentences"].append({"n": i, "text": s["text"], "facts": s["facts"], "failures": [list(x) for x in g],
                                    **({"citations_narrowed": s["pruned"]} if s.get("pruned") else {})})
        if s.get("pruned"):
            report["citations_narrowed"] = report.get("citations_narrowed", 0) + 1
        for gate, reason in g:
            cdetail["gate_failures"].append({"n": i, "gate": gate, "reason": reason})
    status = ["kept"] * len(written)
    current = written
    # Repair needs one call, the checker another: a repair is made only when a call is left for the checker after
    # it. No model sentence is ever shown without having passed both the code gates and the model checker. (Changed
    # after the red-team and grounding audits of 15 Nov: an earlier rule let the last call go to the repair and
    # skipped the checker, and a wrong definition and a sentence against the catalog were shown unchecked.)
    if tr.arm != "no_gates" and any(fails):
        if tr.budget.remaining() >= need_calls:
            failures = [(i, g[0][0], g[0][1]) for i, g in enumerate(fails, 1) if g]
            rmsgs = write.repair_messages(msgs, json.dumps(data, ensure_ascii=False), failures)
            r = _call_write(tr, "repair", rmsgs, sch)
            cdetail["repair"] = True
            if r and not r.get("invalid"):
                rep = [{"text": clean_text(s["text"]), "facts": list(s["facts"])} for s in r["data"]["sentences"]]
                rfails = _gate_all(rep, by_id, req, turn_ids)
                old_texts = {s["text"] for s in written}
                for s, g in zip(written, fails):
                    if g:
                        removed.append({"text": s["text"], "by": g[0][0], "reason": g[0][1]})
                        report["removed_by_gate"][g[0][0]] = report["removed_by_gate"].get(g[0][0], 0) + 1
                current, status = [], []
                for s, g in zip(rep, rfails):
                    if g:
                        if s["text"] not in old_texts:
                            removed.append({"text": s["text"], "by": g[0][0], "reason": g[0][1]})
                        continue
                    current.append(s)
                    st = "kept" if s["text"] in old_texts else "repaired"
                    status.append(st)
                    report["repaired"] += st == "repaired"
                data["followups"] = r["data"].get("followups") or data["followups"]
                data["panels"] = r["data"].get("panels") or data["panels"]
                fails = None
        if fails is not None:
            keep, st2 = [], []
            for s, g in zip(written, fails):
                if g:
                    removed.append({"text": s["text"], "by": g[0][0], "reason": g[0][1]})
                    report["removed_by_gate"][g[0][0]] = report["removed_by_gate"].get(g[0][0], 0) + 1
                else:
                    keep.append(s)
                    st2.append("kept")
            current, status = keep, st2
    # the model checker
    if tr.arm != "no_checker" and current and tr.budget.remaining() < 1:
        # cannot happen with the rule above (kept as a guard): no checker call is left, so no model sentence is shown
        cdetail["checker"]["skipped"] = "no model call was left for the checker"
        report["checker_skipped"] = True
        report["removed"] = len(removed)
        sents = fallback("no checker call left")
        return {"origin": "template", "sentences": sents, "removed": removed}, [], [], report, wdetail, cdetail
    elif tr.arm != "no_checker" and current:
        cm = ck.checker_messages(current, by_id, req)
        c = tr.call("check", cm, ck.check_schema(len(current)))
        if not c or c.get("invalid"):
            report["removed"] = len(removed)
            sents = fallback("check failed" if c else "check call not made")
            return {"origin": "template", "sentences": sents, "removed": removed}, [], [], report, wdetail, cdetail
        verdicts = ck.read_verdicts(c["data"], len(current))
        keep, st2 = [], []
        for i, (s, stt) in enumerate(zip(current, status), 1):
            ok, reason = verdicts[i]
            if ok:
                cdetail["checker"]["yes"] += 1
                keep.append(s)
                st2.append(stt)
            else:
                cdetail["checker"]["no"] += 1
                report["checker_no"] += 1
                removed.append({"text": s["text"], "by": "checker", "reason": reason or "not supported"})
        current, status = keep, st2
    # a kept sentence that opens with a back reference ('Of those', 'These') to a removed sentence reads wrong
    order = [s["text"] for s in written]
    keep, st2 = [], []
    for s, stt in zip(current, status):
        i = order.index(s["text"]) if s["text"] in order else -1
        prev_kept = i > 0 and any(k["text"] == order[i - 1] for k in keep)
        if BACKREF.match(s["text"]) and not prev_kept:
            removed.append({"text": s["text"], "by": "length", "reason": "opens with a reference to a sentence that is "
                                                                            "not shown"})
            report["removed_by_gate"]["length"] = report["removed_by_gate"].get("length", 0) + 1
            continue
        keep.append(s)
        st2.append(stt)
    current, status = keep, st2
    report["removed"] = len(removed)
    report["kept"] = len(current)
    lead_ids = {f["id"] for f in facts if f["lead"]}
    n_written = max(report["written"], 1)
    reason = None
    # Changed at integration (15 Nov): every kept sentence has passed the code gates and the checker, so a turn
    # falls back to the template answer only when fewer than two sentences remain after more than half were
    # removed (or none remains). When no kept sentence cites a lead fact, the team-code sentence of the lead fact
    # is put first (marked as team code) instead of dropping the model's checked sentences.
    if not current:
        reason = "no sentence remains"
    elif report["removed"] - report["repaired"] > n_written / 2 and len(current) < 2:
        reason = "more than half of the written sentences were removed"
    if reason:
        return {"origin": "template", "sentences": fallback(reason), "removed": removed}, data.get("panels") or [], \
            data.get("followups") or [], report, wdetail, cdetail
    lead = []
    if lead_ids and not any(set(s["facts"]) & lead_ids for s in current):
        lead = [s for s in write.template_answer([f for f in facts if f["lead"]], req)[:1]]
        report["lead_from_template"] = bool(lead)
    sents = [{"text": s["text"], "facts": s["facts"], "origin": "template", "status": "kept"} for s in lead]
    sents += [{"text": s["text"], "facts": s["facts"], "origin": "model", "status": stt}
              for s, stt in zip(current, status)]
    for i, s in enumerate(sents, 1):
        s["n"] = i
    return {"origin": "model", "sentences": sents, "removed": removed}, data.get("panels") or [], \
        data.get("followups") or [], report, wdetail, cdetail


FALLBACK_NOTICE = {"write failed": "fallback_write", "write call not made": "fallback_write",
                   "budget": "fallback_write", "check failed": "fallback_check", "check call not made": "fallback_check",
                   "no checker call left": "fallback_check", "no facts": None}


def _followups(texts_in, req, facts):
    out = []
    for t in texts_in or []:
        t = (t or "").strip()
        if t and not ck.gate_question(t, facts, req) and t not in [o["text"] for o in out]:
            out.append({"text": t, "request": None})
        if len(out) == 3:
            break
    for t in texts.FOLLOWUPS.get(req["intent"] if req else "help", []):
        if len(out) >= 2:
            break
        if t not in [o["text"] for o in out]:
            out.append({"text": t, "request": None})
    return out[:3]


# ---------------------------------------------------------------- the turn
def _response(tr, kind, req, state, notices, answer, facts, panels, followups, clarify, gate_report, data, cache):
    if answer and answer.get("origin") == "model":
        label = texts.ANSWER_LABELS["model"]
    else:
        label = texts.ANSWER_LABELS["template"]
    section = next((p.get("dashboard_section") for p in panels if p.get("dashboard_section")), None)
    return {"version": "1", "turn_id": tr.id, "kind": kind, "mode": tr.mode, "request": req, "state": state,
            "notices": notices, "answer": answer, "facts": facts, "panels": panels, "followups": followups,
            "clarify": clarify, "dashboard": {"q": (req or {}).get("dashboard_q") or "", "section": section},
            "trace": {"steps": tr.steps, "model_calls": tr.budget.used, "total_ms": int((time.monotonic() - tr.t0) * 1000),
                      "cache": cache, "gate_report": gate_report, "data_version": data.version,
                      "commit": data.commit},
            "label": label}


def turn(message=None, state=None, request=None, *, chat=None, mode=None, arm="full", answer_mode=None, on_event=None,
         data=None, patch=None, run=None, log_dir="runtime", use_cache=True):
    """Run one turn and return a RESPONSE (DESIGN.md 10.2). Exactly one of `message` and `request`.

    chat       the model call (ai.llm.chat; a FakeChat in tests)
    mode       'live' | 'no_model' | None (server_status decides; AI_NO_MODEL_CALLS=1 always means no_model)
    arm        'full' | 'no_repeat' | 'no_gates' | 'no_checker' | 'single_call' (evaluation)
    patch      a chip edit or clarify option applied to `request`
    run        log name (default assistant_<YYYYMMDD>); log_dir 'runtime' = config.ASSISTANT_RUNTIME_DIR,
               None = ai/runs/ (evaluation and recording)
    """
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}")
    data = data or get_data()
    vocab = data.vocab
    mode, reason = decide_mode(mode)
    chat = chat or llm.chat
    run = run or f"assistant_{datetime.now().strftime('%Y%m%d')}"
    if log_dir == "runtime":
        log_dir = config.ASSISTANT_RUNTIME_DIR
    tr = Turn(chat, mode, arm, on_event, run, log_dir)
    state = state or rq.empty_state()
    req = None
    try:
        if message is not None:
            message = str(message)[:config.ASSISTANT["message_max_chars"]]
        key = None
        if use_cache:
            if message is not None:
                key = _sha(["m", rq.normalise_message(message), state.get("request"), state.get("pending_clarify"),
                            mode, arm, data.version])
            else:
                key = _sha(["r", {k: v for k, v in (request or {}).items() if k not in ("sources", "agreement")},
                            patch, mode, arm, answer_mode, data.version])
            hit = _cache_get(key)
            if hit is not None:
                hit["turn_id"] = tr.id
                hit["trace"]["cache"] = "hit"
                hit["trace"]["model_calls"] = 0
                hit["trace"]["total_ms"] = int((time.monotonic() - tr.t0) * 1000)
                hit["state"] = rq.next_state(state, hit["request"], last_list=hit["state"].get("last_list"),
                                             last_tests=hit["state"].get("last_tests"),
                                             pending=hit["state"].get("pending_clarify"))
                for s in hit["trace"]["steps"]:
                    tr.emit({"event": "step", "step": s["step"], "status": "done", "label": texts.STEPS[s["step"]],
                             "summary": s["summary"],
                             "ms": 0, "model_calls": 0})
                return hit
        tr.start("understand")
        if request is not None:
            req = rq.apply_patch(request, patch or _chip_patch(request), vocab)
            tr.done("understand", texts.SUMMARY["understand_set"], {"readings": [], "agreement": req["agreement"],
                                                                     "removed_ungrounded": [], "asked": False})
        else:
            req, detail, summary = _understand(tr, message, state, vocab)
            tr.done("understand", summary, detail)
        others = [c["label"] for c in req.get("compare_with") or []]
        if message is not None:
            # environments the rule parser found in the message beyond the one looked up (the live spot check of
            # 15 Nov: the model readings left compare_with empty and the spacesuit was again dropped without a word)
            for pid in rq.rule_reading(message, state, vocab).get("presets_named") or []:
                lab = (vocab["presets"].get(pid) or {}).get("label")
                if pid != (req["environment"] or {}).get("preset") and lab and lab not in others:
                    others.append(lab)
        if others and req["intent"] != "compare_environments" and not req["clarify"]:
            # two environments in a message that is not a comparison: only the first is looked up, and the
            # request says so (added after the red-team run of 15 Nov: the spacesuit was dropped without a word)
            first = (req["environment"] or {}).get("label") or "the first environment"
            txt = texts.ASSUME_COMPARE_ONLY.format(label=first, others=", ".join(others))
            if not any(a.get("text") == txt for a in req["assumptions"]):
                req["assumptions"].append({"field": "compare_with", "text": txt})
        if arm == "single_call" and message is not None:
            return _single_call(tr, message, req, state, data, key)
        if req["clarify"]:
            pend = {"field": req["clarify"]["field"], "question": req["clarify"]["question"]}
            st = rq.next_state(state, req, pending=pend)
            # a verdict or prediction request that also needs a clarifying question says first that it gives none
            refusals = [n for n in _notices(req, "live", [], {}) if n["id"] in ("refuse_verdict", "refuse_prediction")]
            resp = _response(tr, "clarify", req, st, refusals, None, [], [], [], req["clarify"], None, data,
                             "miss" if use_cache else "none")
            tr.start("deliver")
            tr.done("deliver", texts.SUMMARY["deliver"].format(seconds=_secs(tr), calls=tr.budget.used))
            resp["trace"]["steps"] = tr.steps
            resp["trace"]["total_ms"] = int((time.monotonic() - tr.t0) * 1000)
            return _finish(tr, resp, key, use_cache)
        if req["intent"] in ("help", "out_of_scope"):
            notices = [{"id": req["intent"], "text": texts.NOTICES[req["intent"]]}]
            if req["asks_verdict"]:
                notices.insert(0, {"id": "refuse_verdict", "text": texts.NOTICES["refuse_verdict"]})
            st = rq.next_state(state, req)
            tr.start("deliver")
            tr.done("deliver", texts.SUMMARY["deliver"].format(seconds=_secs(tr), calls=tr.budget.used))
            resp = _response(tr, req["intent"], req, st, notices, None, [], [], _followups([], req, []), None, None,
                             data, "miss" if use_cache else "none")
            return _finish(tr, resp, key, use_cache)
        # plan
        tr.start("plan")
        steps, dropped = planmod.plan(req, vocab)
        q, mism = rq.dashboard_query(req, vocab)
        labels = ", ".join(dict.fromkeys(texts.TOOL_LABELS[s["tool"]] for s in steps))
        tr.done("plan", texts.SUMMARY["plan"].format(labels=labels) if steps else texts.SUMMARY["plan_none"],
                {"tools": steps, "dropped": dropped, "dashboard_mismatch": mism})
        # look up
        tr.start("lookup")
        look = tools.run(steps, data)
        facts, panels = look["facts"], look["panels"]
        tr.done("lookup", texts.SUMMARY["lookup"].format(facts=len(facts), files=len(look["files"])),
                {"tools": look["trace"], "notes": look["notes"], "files": look["files"]})
        notices = _notices(req, mode, facts, look)
        # write and check
        tr.start("write")
        if answer_mode == "template":
            answer = {"origin": "template", "sentences": write.template_answer(facts, req), "removed": []}
            chosen, fups, report = [], [], None
            wdetail, cdetail = {"sentences": 0, "valid": False}, None
            tr.done("write", texts.SUMMARY["write_template"], wdetail)
        else:
            tr.wrote = False
            answer, chosen, fups, report, wdetail, cdetail = _write_and_check(tr, req, vocab, notices, facts, panels,
                                                                              message)
            if not tr.wrote:
                tr.done("write", texts.SUMMARY["write_template"], wdetail)
                tr.start("check")
        if answer_mode == "template":
            tr.start("check")
        if report and report["written"]:
            summ = texts.SUMMARY["check"].format(written=report["written"], removed=report["removed"],
                                                 repaired=report["repaired"])
            if cdetail and (cdetail["checker"]["yes"] or cdetail["checker"]["no"]):
                summ += texts.SUMMARY["check_model"].format(yes=cdetail["checker"]["yes"],
                                                            checked=cdetail["checker"]["yes"] + cdetail["checker"]["no"])
            elif cdetail and cdetail["checker"].get("skipped"):
                summ += texts.SUMMARY["check_skipped"]
        else:
            summ = texts.SUMMARY["check_none"]
        tr.done("check", summ, cdetail or {"gate_failures": [], "repair": False, "checker": {"yes": 0, "no": 0}})
        if answer["origin"] == "template" and report and report.get("fallback") and mode == "live":
            # the notice says what happened (separate texts added after the red-team run of 15 Nov); a turn with
            # no facts to write from gets no fallback notice (the not-in-files notice says what is missing)
            nid = FALLBACK_NOTICE.get(report.get("fallback_reason"), "fallback")
            if nid:
                notices.append({"id": "fallback", "text": texts.NOTICES[nid]})
        if not answer["sentences"] and not any(n["id"] == "not_in_files" for n in notices):
            notices.append({"id": "not_in_files", "text": texts.NOTICES["not_in_files"].format(
                needed=texts.NEEDED["search"].format(keywords=", ".join(req.get("keywords") or ["these"])))})
        # order panels: the writer's choice first
        if chosen:
            order = [p for pid in chosen for p in panels if p["id"] == pid]
            panels = order + [p for p in panels if p["id"] not in chosen]
        st = rq.next_state(state, req, last_list=look["state"].get("last_list") or req.get("investigations") or None,
                           last_tests=look["state"].get("last_tests"))
        tr.start("deliver")
        tr.done("deliver", texts.SUMMARY["deliver"].format(seconds=_secs(tr), calls=tr.budget.used))
        resp = _response(tr, "answer", req, st, notices, answer, facts, panels, _followups(fups, req, facts), None,
                         report, data, "miss" if use_cache else "none")
        return _finish(tr, resp, key, use_cache)
    except Exception as e:  # noqa: BLE001 - the page gets the fixed error text and the trace so far
        resp = {"version": "1", "turn_id": tr.id, "kind": "error", "mode": mode, "request": req,
                "state": state, "notices": [{"id": "error", "text": texts.ERROR}], "answer": None, "facts": [],
                "panels": [], "followups": [], "clarify": None, "dashboard": {"q": "", "section": None},
                "trace": {"steps": tr.steps, "model_calls": tr.budget.used,
                          "total_ms": int((time.monotonic() - tr.t0) * 1000), "cache": "none",
                          "gate_report": {"error": f"{type(e).__name__}: {e}"[:300]},
                          "data_version": data.version, "commit": data.commit},
                "label": texts.ANSWER_LABELS["template"]}
        tr.emit({"event": "error", "message": texts.ERROR})
        return resp


def _chip_patch(request):
    """A request sent back by the page with edited chips: fields whose source is 'chip' become a patch."""
    src = request.get("sources") or {}
    env = request.get("environment") or {}
    p = {}
    if src.get("environment.preset") == "chip":
        p.setdefault("environment", {})["preset"] = env.get("preset")
    for f in ("o2_pct", "pressure_kpa", "gravity"):
        if src.get(f"environment.{f}") == "chip":
            p.setdefault("environment", {})[f] = env.get(f)
    if src.get("item.material") == "chip":
        p["item"] = {"material": (request.get("item") or {}).get("material")}
    for f in ("equipment", "questions", "investigations", "intent"):
        if src.get(f) == "chip":
            p[f] = request.get(f)
    return p


def _secs(tr):
    return f"{(time.monotonic() - tr.t0):.1f}"


def _finish(tr, resp, key, use_cache):
    errs = llm.validate(resp, _response_schema())
    if errs:
        resp["trace"]["gate_report"] = dict(resp["trace"].get("gate_report") or {}, response_errors=errs[:5])
    if use_cache and key and resp["kind"] != "error":
        _cache_put(key, resp)
    tr.emit({"event": "result", "response": resp})
    return resp


def _response_schema():
    from ai.assistant import contract
    return contract.RESPONSE


# ---------------------------------------------------------------- the single-call baseline (8.5)
def _single_call(tr, message, req, state, data, key):
    vocab = data.vocab
    tr.start("plan")
    steps, dropped = planmod.plan(req, vocab)
    tr.done("plan", texts.SUMMARY["plan"].format(labels=", ".join(texts.TOOL_LABELS[s["tool"]] for s in steps))
            if steps else texts.SUMMARY["plan_none"], {"tools": steps, "dropped": dropped, "dashboard_mismatch": []})
    tr.start("lookup")
    look = tools.run(steps, data)
    facts, panels = look["facts"], look["panels"]
    tr.done("lookup", texts.SUMMARY["lookup"].format(facts=len(facts), files=len(look["files"])),
            {"tools": look["trace"], "notes": look["notes"], "files": look["files"]})
    wf = tools.writer_facts(facts)
    by_id = {f["id"]: f for f in facts}
    tr.start("write")
    r = tr.call("baseline", write.baseline_messages(message, req, vocab, wf, panels),
                write.baseline_schema(req, wf, rq.READING)) if wf else None
    report = {"written": 0, "repaired": 0, "removed": 0, "removed_by_gate": {}, "checker_no": 0, "kept": 0,
              "fallback": False, "fallback_reason": None, "sentences": [], "report_only": True}
    if r and not r.get("invalid"):
        d = r["data"]
        sents = [{"n": i, "text": s["text"], "facts": [x for x in s["facts"] if x in by_id], "origin": "model",
                  "status": "kept"} for i, s in enumerate(d["sentences"], 1)]
        report["written"] = report["kept"] = len(sents)
        for s in sents:
            g = ck.gate_sentence(s["text"], [by_id[x] for x in s["facts"]], req, set(by_id), cited_ids=s["facts"])
            report["sentences"].append({"n": s["n"], "text": s["text"], "facts": s["facts"], "failures": [list(x) for x in g]})
        answer = {"origin": "model", "sentences": sents, "removed": []}
        report["baseline_reading"] = {k: d.get(k) for k in ("intent", "asks_verdict", "asks_prediction", "environment",
                                                            "item", "questions")}
        fups = [{"text": t, "request": None} for t in (d.get("followups") or [])[:3]]
        notices = []
        if d.get("asks_verdict"):
            notices.append({"id": "refuse_verdict", "text": texts.NOTICES["refuse_verdict"]})
        if d.get("asks_prediction"):
            notices.append({"id": "refuse_prediction", "text": texts.NOTICES["refuse_prediction"]})
        tr.done("write", texts.SUMMARY["write_model"].format(written=len(sents)), {"sentences": len(sents), "valid": True})
    else:
        answer = {"origin": "template", "sentences": write.template_answer(facts), "removed": []}
        report["fallback"], report["fallback_reason"] = True, "baseline call failed"
        fups, notices = [], []
        tr.done("write", texts.SUMMARY["write_template"], {"sentences": 0, "valid": False})
    tr.start("deliver")
    tr.done("deliver", texts.SUMMARY["deliver"].format(seconds=_secs(tr), calls=tr.budget.used))
    st = rq.next_state(state, req, last_list=look["state"].get("last_list"), last_tests=look["state"].get("last_tests"))
    resp = _response(tr, "answer", req, st, notices, answer, facts, panels, fups, None, report, data, "none")
    return _finish(tr, resp, None, False)
