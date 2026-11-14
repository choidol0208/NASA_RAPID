# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Component C, second half: gate the gpt-oss:20b card candidates, repair once, write cards.json.

Input: a candidate log written by ai/cards_llm.py (default ai/runs/cards_20261114-v3-all24.jsonl,
prompt ai/prompts/card_v3.txt). For each of the 24 records:

1. Every summary sentence the model proposed goes through gates 1 to 11 (ai/checks.py
   check_sentence) plus one writer rule: the first cited unit must be a quotable PSI sentence,
   because it is printed verbatim as a key point under the summary.
2. A sentence that fails gets exactly one repair call to gpt-oss:20b through ai/llm.py
   (only with --repair). The call repeats the original prompt and the model's own reply and names
   the failed sentence and every gate reason. The replacement is gated again; if it fails, the
   sentence is dropped. Nothing is ever edited by code. Repair calls are logged to
   ai/runs/cards_20261114-v3-repair.jsonl, so a later build without --repair reproduces the same
   cards with no model call.
3. Reviewed removals before the review (ai/review/pm_prereview.json, see ai/review/README.md): a
   sentence listed there (investigation_id and exact text) is dropped although it passed every gate,
   and its slot in the summary shows the quoted NASA sentence it cited first, with its field label.
   These removals are counted apart from the data role's review and never set reviewed_by.
4. Quotes marked not_relevant in the review sheet (ai/review/README.md): a quote row whose verdict is
   'not_relevant' (matched by sheet item and sentence sha) is not shown on its card. A key point is
   dropped and the pick rule below simply goes on to its next candidate (no other sentence is chosen
   in its place). The quoted slot of a removed sentence uses the next unit that sentence cited, if one
   is quotable and not marked, else the slot is left out. A quoted summary is never emptied: a marked
   quote that is the card's last summary sentence stays and is listed in quality.json
   (quotes_marked_but_kept). Every card lists what was left out under 'hidden_by_review'.
5. A card keeps the quoted baseline card of ai/build_baseline.py (status 'fallback_quote',
   ai_generated false) when no summary sentence survives. Otherwise:
   - summary = the surviving sentences, each ending with its source in brackets,
     '(PSI-25 record: objective)', built from the fields of its cited units;
   - key_points (at most 4) = the first cited unit of each surviving sentence, printed verbatim
     with its field label, then the baseline's quoted key points for fields not yet shown, then
     the model's key_ids if room is left. Every key point is a verbatim quote;
   - status 'generated' (every proposed sentence shipped) or 'generated_partial' (some dropped by a
     gate, a reviewed removal or the review);
   - every model sentence has review null and the card has reviewed_by null. Only
     ai/apply_review.py sets them, from ai/review/review_sheet.csv.
6. Writes data/insights/cards.json (disclosure block in data/insights/_meta.json) and the review
   sheet (ai/apply_review.py refresh_sheet: built with the sheet's verdicts applied, so that the sheet
   lists what the reviewed cards show, plus the rows whose verdict removed their sentence). The gate log ai/runs/cards_20261114-v3-gates.jsonl is a run
   record: it is written only with --repair (new model calls) or --write-gate-log, never by a rebuild.

Quotes are taken by code. Every key point and every stored evidence 'quote' is the exact text of the
cited unit in data/insights/evidence.json, with that unit's offsets; the model's own copy of a quote
is kept only as 'model_quote' (the input of gate 2, which ai/check_all.py re-runs) and is never shown.

    python3 ai/apply_cards.py --repair     # gate, call the model once per failed sentence, write
    python3 ai/apply_cards.py              # rebuild from the logs only (no model call), write
    python3 ai/apply_cards.py --check      # build in memory, compare with cards.json, write nothing
"""
import argparse
import copy
import hashlib
import json
import sys
from collections import Counter, OrderedDict
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import build_baseline as BB, cards_llm, checks as C, config, evidence as evmod, llm, meta as metamod  # noqa: E402
from ai import resolve  # noqa: E402
from ai import templates as T  # noqa: E402

ROOT = config.ROOT
BUILT_BY = "ai/apply_cards.py"
OUT_CARDS = config.INSIGHTS_DIR / "cards.json"
CANDIDATES = config.RUNS_DIR / "cards_20261114-v3-all24.jsonl"
REPAIR_RUN = "cards_20261114-v3-repair"
GATES_RUN = "cards_20261114-v3-gates"
MAX_KEY_POINTS = 4
MODEL_STRING = f"{config.MODEL_LABEL} via {config.RUNNER.replace(' (local)', '')}"

GATE_NAMES = [n[:-3] for n in C.CHECK_NAMES]  # ids, quote, numbers, ... hedge
WRITER_RULES = ("key_point",)

REPAIR_HINT = {
    "quote": ("copy into quote the whole evidence sentence, or one complete clause of it, character for "
              "character, and make the sentence complete without stopping where the quote stops"),
    "numbers": "use only numbers, units and quantity words written in the quotes you cite",
    "entities": "use only names, acronyms and application words that are in the record",
    "policy": "no advice or verdict word",
    "lint": "no comparison with Earth, no 'more flammable' and nothing about partial gravity the quote does not say",
    "length": "one complete sentence of 15 to 30 words (never more than 35) that ends with a full stop",
    "modality": ("word an objective as 'The investigation aimed to ...', a hypothesis as 'The record "
                 "hypothesizes that ...', an approach as 'The planned approach ...' and an impact statement as "
                 "'The record states that ...'; no result verb"),
    "hedge": "keep the hedge word of the quote, and add no certainty word (will, always, significantly ...)",
    "ids": "cite 1 to 3 IDs that exist in the evidence",
    "sources": "cite IDs that exist in the evidence",
    "key_point": "start the evidence with an ID whose line is a complete sentence, not a heading or fragment",
}

LABEL_MODEL = ("AI-written summary (gpt-oss:20b, run offline by the team) of NASA PSI record {inv}. Each "
               "sentence names and quotes its PSI source and passed the team's code checks; {review}. "
               "A summary describes what the record states (often aims and hypotheses), not what NASA measured. "
               "The key points under it are quoted from the PSI record with their field labels. "
               "Not NASA's conclusion; not operational safety guidance.")
REVIEW_NONE = "not reviewed yet"
REMOVE_VERDICTS = ("not", "partly")
PREREVIEW = config.AI_DIR / "review" / "pm_prereview.json"
PREREVIEW_KIND = "ai_session_pm"
PREREVIEW_FIELDS = ("investigation_id", "sentence", "reason", "reviewer_kind")
LABEL_SLOT = (" One summary sentence was removed after the code checks by the pm session's reviewed "
              "removals (ai/review/pm_prereview.json); its place shows the quoted NASA sentence it cited.")
LABEL_SLOT_NONE = (" One summary sentence was removed after the code checks by the pm session's reviewed "
                   "removals (ai/review/pm_prereview.json); the NASA sentence it cited is not shown, because the "
                   "review (a second AI session) marked it not relevant to show here.")
HIDE_VERDICT = "not_relevant"


def quote_item(inv, s):
    """Row id of a quoted sentence (key point, quoted summary or slot) in ai/review/review_sheet.csv."""
    ids = [e["id"] for e in s.get("evidence") or []]
    return f"card:{inv}:{s['role']}:{s.get('source')}:{ids[0] if ids else ''}"


def quote_key(inv, s):
    """(sheet item, sentence sha) of a quoted sentence: how a quote verdict is matched to it."""
    return quote_item(inv, s), _sha(s["text"])


def hidden_entry(inv, s, rv, replaced_by=None):
    return OrderedDict([("item", quote_item(inv, s)), ("role", s["role"]), ("source", s.get("source")),
                        ("unit_ids", [e["id"] for e in s.get("evidence") or []]),
                        ("verdict", HIDE_VERDICT), ("reviewer_kind", rv.get("reviewer_kind")),
                        ("reviewer_role", rv.get("reviewer_role")), ("replaced_by", replaced_by)])


def log_hidden(hidden_log, inv, entry, sent):
    """Build-side record of a quote left out: the card entry plus the sentence (for the sheet row)."""
    hidden_log.append(dict(entry, investigation_id=inv, _key=quote_key(inv, sent), _sentence=copy.deepcopy(sent)))


def public(entries):
    """Log entries without the build-side keys (for quality.json)."""
    return [{k: v for k, v in e.items() if not k.startswith("_")} for e in entries]


def _now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _sha(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


def _rel(p):
    p = Path(p).resolve()
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


# ====================================================================== logs

def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def load_candidates(path=CANDIDATES):
    """-> (meta, {inv: candidate line}, {inv: raw reply of the call the candidate came from})."""
    lines = read_jsonl(path)
    if not lines or "_meta" not in lines[0]:
        raise SystemExit(f"{_rel(path)}: no candidate log (first line must be a _meta record)")
    meta = lines[0]["_meta"]
    cands, raws = {}, {}
    for d in lines[1:]:
        if d.get("kind") == "call" and d.get("valid") and d.get("step") in ("card", "card_shape_retry"):
            raws[d["record"]] = d["raw"]
        elif d.get("kind") == "candidate":
            cands[d["record"]] = d
    return meta, cands, raws


def repair_key(inv, n, text):
    return f"{inv}|{n}|{_sha(text)}"


def load_repairs(run=REPAIR_RUN):
    out = {}
    for d in read_jsonl(llm.run_log_path(run)):
        if d.get("kind") == "repair":
            out[d["key"]] = d
    return out


# ====================================================================== gating

def dedupe_evidence(evidence):
    """The same id cited twice in one item adds nothing (v2 batch: PSI-20, PSI-101); keep the first."""
    seen, out = set(), []
    for e in evidence or []:
        if e.get("id") in seen:
            continue
        seen.add(e.get("id"))
        out.append({"id": e.get("id"), "quote": e.get("quote")})
    return out


def gate(text, evidence, inv, ev, n_summary):
    """Gates 1 to 11 plus the writer rule. Returns check_sentence's dict plus 'failed' (gate names)."""
    res = C.check_sentence(text, evidence, inv, ev, n_summary=n_summary)
    failed = [n[:-3] for n, ok in res["checks"].items() if not ok]
    writer = []
    if res["checks"]["ids_ok"] and evidence:
        first = evmod.unit(inv, evidence[0]["id"], ev)
        if not first["quotable"]:
            writer.append(("key_point", f"key_point: the first cited unit {first['id']} is not a quotable PSI "
                                        "sentence (heading, fragment or reference), so it cannot be printed "
                                        "as the key point under the summary"))
    res = dict(res)
    res["failed"] = failed + [w[0] for w in writer]
    res["reasons"] = list(res["reasons"]) + [w[1] for w in writer]
    res["ok"] = not res["failed"]
    return res


def repair_messages(inv, rec, meta, raw, n, item, res, schema_item):
    system, user_tpl, psha = cards_llm.load_prompt(ROOT / meta["prompt_file"])
    if psha != meta["prompt_file_sha256"]:
        raise SystemExit(f"{meta['prompt_file']} changed since the candidate run (sha256 {psha[:12]} != "
                         f"{meta['prompt_file_sha256'][:12]}); rerun ai/cards_llm.py first")
    messages = cards_llm.build_messages(inv, rec, system, user_tpl)
    hints = []
    for g in res["failed"]:
        h = REPAIR_HINT.get(g)
        if h and h not in hints:
            hints.append(h)
    ask = (f"Summary item {n + 1} of your reply did not pass the team's code checks.\n"
           f"The item was: {json.dumps({'evidence': item['evidence'], 'text': item['text']}, ensure_ascii=False)}\n"
           "The checks found: " + " | ".join(res["reasons"]) + "\n"
           "To fix it: " + "; ".join(hints) + ".\n"
           "Write one replacement for that item only, from the same EVIDENCE and under every rule of the system "
           "message. Reply with only one JSON object with the keys evidence (choose the IDs and copy the quotes "
           "first) and text. Do not repeat the other items.")
    return messages + [{"role": "assistant", "content": raw}, {"role": "user", "content": ask}]


def prompt_reproduced(inv, rec, meta, schema, cand):
    """True when the rebuilt card prompt hashes to the prompt_sha256 logged for the candidate."""
    system, user_tpl, _ = cards_llm.load_prompt(ROOT / meta["prompt_file"])
    m = cards_llm.build_messages(inv, rec, system, user_tpl)
    m[0]["content"] = m[0]["content"].rstrip() + "\n\n" + llm.schema_instruction(schema)
    return llm.prompt_sha256(m, schema) == cand.get("prompt_sha256")


def call_repair(inv, rec, meta, raw, n, item, res, schema, cand):
    if not prompt_reproduced(inv, rec, meta, schema, cand):
        raise SystemExit(f"{inv}: the rebuilt card prompt does not match the logged prompt_sha256; "
                         "the repair would not continue the same conversation")
    schema_item = copy.deepcopy(schema["properties"]["summary"]["items"])
    msgs = repair_messages(inv, rec, meta, raw, n, item, res, schema_item)
    r = llm.chat(msgs, schema_item, run=REPAIR_RUN,
                 log_extra={"record": inv, "step": "card_repair", "item": n})
    line = {"time": _now(), "kind": "repair", "key": repair_key(inv, n, item["text"]), "record": inv, "n": n,
            "original": {"text": item["text"], "evidence": item["evidence"]},
            "original_reasons": res["reasons"], "original_prompt_reproduced": True, "valid": r["valid"], "errors": r["errors"],
            "replacement": r["data"], "prompt_sha256": r["prompt_sha256"], "digest": r["digest"],
            "options": r["options"], "think": r["think"], "format_mode": r["format_mode"],
            "eval_count": r["eval_count"], "wall_s": r["wall_s"], "done_reason": r["done_reason"],
            "retries": r["retries"]}
    llm.log_line(REPAIR_RUN, line)
    return line


# ====================================================================== card assembly

def field_label(field):
    return evmod.FIELDS[field][1]


def evidence_entries(inv, evidence, ev):
    """Stored evidence. 'quote' is the exact text of the cited unit, taken by code from evidence.json
    (record[field][char_start:char_end], the unit's own offsets); it is never the model's copy. The
    model's copy is kept as 'model_quote' only, because gate 2 checks it and ai/check_all.py re-runs
    the gates; the page never shows it."""
    out = []
    for e in evidence:
        u = evmod.unit(inv, e["id"], ev)
        field_text = resolve.resolve(u["source"])["text"]
        if field_text[u["char_start"]:u["char_end"]] != u["text"]:
            raise SystemExit(f"{inv} {u['id']}: evidence.json offsets do not reproduce the unit text")
        out.append({"id": u["id"], "source": u["source"], "quote": u["text"], "char_start": u["char_start"],
                    "char_end": u["char_end"], "quote_from": "evidence.json unit text, taken by code",
                    "field": u["field"], "model_quote": e.get("quote") or ""})
    return out


def regate_evidence(evidence):
    """The evidence of a stored model sentence as the gates read it: the model's own quote (gate 2 input),
    with the unit's source and offsets."""
    return [{"id": e.get("id"), "quote": e.get("model_quote", e.get("quote")), "source": e.get("source"),
             "char_start": e.get("char_start"), "char_end": e.get("char_end")} for e in evidence or []]


# ====================================================================== reviewed removals before the review

def load_prereview(path=PREREVIEW):
    """The reviewed removals: [{investigation_id, sentence, reason, reviewer_kind}] (ai/review/README.md)."""
    path = Path(path)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"{_rel(path)}: must be a JSON list of removals")
    for i, e in enumerate(data):
        missing = [k for k in PREREVIEW_FIELDS if not isinstance(e.get(k), str) or not e[k].strip()]
        if missing:
            raise SystemExit(f"{_rel(path)} entry {i}: missing or empty {', '.join(missing)}")
        if e["reviewer_kind"] != PREREVIEW_KIND:
            raise SystemExit(f"{_rel(path)} entry {i}: reviewer_kind must be {PREREVIEW_KIND!r}")
    return data


def prereview_match(entries, inv, shown, body):
    """The entry that names this sentence (the text as shown with its bracketed source, or without it)."""
    for e in entries:
        if e["investigation_id"] == inv and e["sentence"].strip() in (shown, body.strip()):
            return e
    return None


def suffix(inv, fields):
    order = [f for f in evmod.FIELDS if f in fields]
    return f" ({inv} record: {', '.join(order)})"


def key_point_from_unit(ctx, inv, uid):
    us_all = evmod.units(inv, ev=ctx.ev)
    u = next(x for x in us_all if x["id"] == uid)
    us = [x for x in us_all if x["field"] == u["field"]]
    i = next(j for j, x in enumerate(us) if x["id"] == uid)
    text, cs, ce, used = BB.quote_span(ctx, inv, u["field"], us, i)
    label = field_label(u["field"])
    kp = {"text": T.key_point(label, text), "source": f"{inv}.{u['field']}"}
    sent = BB.sentence(inv, "key_point", u["field"], label, text, cs, ce, used)
    return kp, sent, {x["id"] for x in used}, u["field"]


def hide_in_base(card, inv, hidden, hidden_log, kept_log):
    """The quoted baseline card without its quotes marked not_relevant. A key point is dropped (the
    baseline rule has one candidate per field, so nothing takes its place). A quoted summary sentence
    is dropped only while another summary quote is left; the last one stays and is logged in kept_log."""
    if not hidden:
        return card
    out_sents, kps, gone = [], [], []
    summary = [s for s in card["sentences"] if s["role"] == "summary"]
    kp_by_text = {kp["text"]: kp for kp in card["key_points"]}
    for s in card["sentences"]:
        rv = hidden.get(quote_key(inv, s))
        if rv and s["role"] == "summary":
            left = [x for x in summary if x is not s and not hidden.get(quote_key(inv, x))]
            if not left:
                kept_log.append({"investigation_id": inv, "item": quote_item(inv, s), "_key": quote_key(inv, s),
                                 "why": "the card's last quoted summary sentence; a card never shows an empty "
                                        "summary, so it stays shown and is listed here"})
                out_sents.append(s)
                continue
        if rv:
            gone.append((s, hidden_entry(inv, s, rv)))
            continue
        out_sents.append(s)
        if s["role"] == "key_point":
            kps.append(kp_by_text[T.key_point(s["field_label"], s["text"])])
    if not gone:
        return card
    card["sentences"] = out_sents
    card["key_points"] = kps
    card["summary"] = T.card_summary([s["text"] for s in out_sents if s["role"] == "summary"])
    card["hidden_by_review"] = [h for _, h in gone]
    for s, h in gone:
        log_hidden(hidden_log, inv, h, s)
    return card


def assemble(ctx, base, inv, survivors, n_proposed, cand, meta, review_word=REVIEW_NONE, slots=(), hidden=None,
             hidden_log=None, kept_log=None):
    """Card from the surviving model sentences. survivors: [{n, text, evidence, res, repaired, ...}].
    slots: sentences removed by the reviewed removals; each keeps its place in the summary as the quoted
    NASA sentence it cited first (with its field label), or the next quotable one it cited when that one is
    marked not_relevant, or no quote at all. hidden: {(sheet item, sha): review} of the quote rows marked
    not_relevant (ai/apply_review.py hidden_quotes)."""
    hidden = hidden or {}
    hidden_log = hidden_log if hidden_log is not None else []
    kept_log = kept_log if kept_log is not None else []
    if not survivors:
        return hide_in_base(copy.deepcopy(base), inv, hidden, hidden_log, kept_log)
    ev = ctx.ev
    gone = []  # (sentence, review, slot n or None)
    summary_sents, summary_sources, slot_sents, slot_ids, slot_fields = [], [], [], set(), set()
    slot_used = {}
    for s in slots:
        chosen = None
        for e in s["evidence"]:
            if not evmod.unit(inv, e["id"], ev)["quotable"]:
                continue
            kp, sent, ids, field = key_point_from_unit(ctx, inv, e["id"])
            sent["role"] = "summary"
            rv = hidden.get(quote_key(inv, sent))
            if rv:
                gone.append((sent, rv, s["n"]))
                slot_ids |= ids  # a marked unit is not shown elsewhere on this card either
                continue
            chosen = (kp, sent, ids, field)
            break
        slot_used[s["n"]] = chosen[1]["source"] if chosen else None
        if chosen is None:
            continue
        kp, sent, ids, field = chosen
        sent["n"] = s["n"]
        sent["replaces"] = {"n": s["n"], "removed_by": "ai/review/pm_prereview.json",
                            "reviewer_kind": s["prereview"]["reviewer_kind"]}
        sent["summary_text"] = kp["text"]
        slot_sents.append(sent)
        slot_ids |= ids
        slot_fields.add(field)
    for s in survivors:
        fields = [evmod.unit(inv, e["id"], ev)["field"] for e in s["evidence"]]
        text = s["text"].rstrip() + suffix(inv, set(fields))
        summary_sents.append(OrderedDict([
            ("role", "summary"), ("origin", "model"), ("n", s["n"]), ("text", text), ("field_label", None),
            ("cited_fields", [f for f in evmod.FIELDS if f in fields]),
            ("evidence", evidence_entries(inv, s["evidence"], ev)),
            ("checks", s["res"]["checks"]), ("lexical_support", s["res"]["lexical_support"]),
            ("shared_with", s["res"]["shared_with"]), ("repaired", s["repaired"]),
            ("first_pass_reasons", s.get("first_pass_reasons") or []), ("review", s.get("review")),
        ]))
    ordered = sorted(summary_sents + slot_sents, key=lambda x: x["n"])
    for x in ordered:
        if x["origin"] == "model":
            fields = x["cited_fields"]
        else:
            fields = [x["source"].split(".", 1)[1]]
        for f in evmod.FIELDS:
            src = f"{inv}.{f}"
            if f in fields and src not in summary_sources:
                summary_sources.append(src)
    # key points: first cited unit of each sentence, then the baseline's quoted key points, then key_ids
    key_points, kp_sents, used_ids, fields_shown = [], [], set(slot_ids), set(slot_fields)

    def add_unit(uid):
        if len(key_points) >= MAX_KEY_POINTS or uid in used_ids:
            return
        kp, sent, ids, field = key_point_from_unit(ctx, inv, uid)
        if ids & used_ids:
            return
        rv = hidden.get(quote_key(inv, sent))
        if rv:  # marked not_relevant: not shown; the rule goes on to its next candidate
            gone.append((sent, rv, None))
            used_ids.update(ids)
            return
        key_points.append(kp)
        kp_sents.append(sent)
        used_ids.update(ids)
        fields_shown.add(field)

    for s in survivors:
        add_unit(s["evidence"][0]["id"])
    for kp, sent in zip(base["key_points"], [x for x in base["sentences"] if x["role"] == "key_point"]):
        field = kp["source"].split(".", 1)[1]
        ids = {e["id"] for e in sent["evidence"]}
        if len(key_points) >= MAX_KEY_POINTS or field in fields_shown or ids & used_ids:
            continue
        rv = hidden.get(quote_key(inv, sent))
        if rv:
            gone.append((copy.deepcopy(sent), rv, None))
            used_ids.update(ids)
            continue
        key_points.append(copy.deepcopy(kp))
        kp_sents.append(copy.deepcopy(sent))
        used_ids.update(ids)
        fields_shown.add(field)
    for uid in cand.get("key_ids") or []:
        u = evmod.unit(inv, uid, ev)
        if u["quotable"]:
            add_unit(uid)
    shared = sorted({r for s in summary_sents for r in s["shared_with"]}, key=BB.acc_key)
    partial = len(survivors) < n_proposed
    card = OrderedDict([
        ("investigation_id", inv),
        ("summary", " ".join(x["text"] if x["origin"] == "model" else x["summary_text"] for x in ordered)),
        ("key_points", key_points),
        ("ai_generated", True),
        ("model", MODEL_STRING),
        ("reviewed_by", None),
        ("updated", None),
        ("summary_sources", summary_sources),
        ("built_by", BUILT_BY),
        ("status", "generated_partial" if partial else "generated"),
        ("sentences", [{k: v for k, v in x.items() if k != "summary_text"} for x in ordered] + kp_sents),
        ("label", LABEL_MODEL.format(inv=inv, review=review_word)
         + (LABEL_SLOT if slot_sents else "") + (LABEL_SLOT_NONE if len(slot_sents) < len(slots) else "")),
        ("prompt_sha256", meta["prompt_file_sha256"]),
        ("params", {"prompt_file": meta["prompt_file"], "call_prompt_sha256": cand.get("prompt_sha256"),
                    "model_digest": cand.get("digest"), "options": cand.get("options"),
                    "think": cand.get("think"), "format_mode": cand.get("format_mode"),
                    "candidates_log": _rel(CANDIDATES), "repair_log": _rel(llm.run_log_path(REPAIR_RUN)),
                    "sentences_proposed": n_proposed, "sentences_shipped": len(survivors),
                    "sentences_removed_by_prereview": len(slots)}),
        ("license_note", base["license_note"]),
        ("pick_rule", {"key_points": ("first cited unit of each summary sentence, then the quoted baseline key "
                                      "points for fields not yet shown, then the model's key_ids; at most 4; a "
                                      "quote marked not_relevant in the review sheet is skipped"),
                       "baseline": base.get("pick_rule")}),
        ("record_title", base.get("record_title")),
        ("dataset_doi", base.get("dataset_doi")),
    ])
    if slots:
        card["removed_before_review"] = [{"n": s["n"], "sentence": s["full"], "reason": s["prereview"]["reason"],
                                          "reviewer_kind": s["prereview"]["reviewer_kind"],
                                          "replaced_by": slot_used.get(s["n"])}
                                         for s in slots]
    if gone:
        card["hidden_by_review"] = []
        for sent, rv, n in gone:
            h = hidden_entry(inv, sent, rv, replaced_by=slot_used.get(n) if n is not None else None)
            if n is not None:
                h["slot_of_removed_sentence"] = n
            card["hidden_by_review"].append(h)
            log_hidden(hidden_log, inv, h, sent)
    if shared:
        card["shared_text_note"] = ("Part of the PSI text this summary rests on is the same, word for word, in "
                                    + " and ".join(shared) + ".")
    return card


# ====================================================================== build

def sheet_item(inv, n):
    """Row id of a model summary sentence in ai/review/review_sheet.csv (n = the candidate's item index)."""
    return f"card:{inv}:summary:{n}"


def reviewer_line(reviews):
    """(reviewed_by, the clause for the card label) from the reviews of every model sentence of a card."""
    kinds = {r["reviewer_kind"] for r in reviews}
    roles = sorted({r["reviewer_role"] for r in reviews})
    if kinds == {"person"}:
        return (f"hackathon team member ({', '.join(roles)})",
                "read against the PSI text by a hackathon team member, not by NASA or a combustion expert")
    if kinds == {"ai_session"}:
        return (f"second AI session ({', '.join(roles)} role)",
                "checked against the PSI text by a second AI session, not by a person, NASA or a combustion expert")
    return (f"hackathon team member and second AI session ({', '.join(roles)})",
            "checked against the PSI text by a hackathon team member or a second AI session, not by NASA or a "
            "combustion expert")


def sheet_sentence(full, s):
    """A model sentence that is not shown (removed by the review or by --final), in the shape
    ai/apply_review.py card_rows reads, so that its sheet row and verdict are kept."""
    return {"role": "summary", "origin": "model", "n": s["n"], "text": full,
            "evidence": [{"id": e["id"]} for e in s["evidence"]], "checks": s["res"]["checks"],
            "lexical_support": s["res"]["lexical_support"], "repaired": s["repaired"]}


def build(candidates=CANDIDATES, do_repair=False, ctx=None, log=print, reviews=None, final=False,
          prereview_path=PREREVIEW, hidden_quotes=None):
    """Gate the candidates (and repair once if do_repair) and return {cards, stats, gate_lines, baseline}.

    reviews        {(sheet item, sentence sha): {verdict, modality_kept, reviewer_kind, reviewer_role}} from
                   ai/apply_review.py; a sentence marked 'not' or 'partly' or modality_kept 'no' is removed
    hidden_quotes  {(sheet item, sentence sha): review} of the quote rows marked not_relevant; such a quote is
                   not shown (ai/review/README.md)
    final          also revert to its quote any card that keeps an unreviewed model sentence
    """
    hidden = dict(hidden_quotes or {})
    hidden_log, kept_log, not_shown = [], [], []
    ctx = ctx or BB.Ctx()
    ev = ctx.ev
    meta, cands, raws = load_candidates(candidates)
    repairs = load_repairs()
    prereview = load_prereview(prereview_path)
    prereview_used, prereview_removed = set(), []
    records = sorted(ev["records"], key=BB.acc_key)
    baseline = {acc: BB.card(ctx, acc) for acc in records}
    cards, gate_lines, per_card = [], [], {}
    st = Counter()
    first_gate, all_gates, after_gates = Counter(), Counter(), Counter()
    for inv in records:
        base = baseline[inv]
        cand = cands.get(inv)
        if not cand or not cand.get("valid") or cand.get("abstain") or not cand.get("sentences"):
            why = ("no candidate" if not cand else "invalid reply" if not cand.get("valid")
                   else "model abstained" if cand.get("abstain") else "no sentence")
            gate_lines.append({"kind": "card", "record": inv, "status": "fallback_quote", "why": why})
            st["cards_without_candidate"] += 1
            cards.append(hide_in_base(copy.deepcopy(base), inv, hidden, hidden_log, kept_log))
            per_card[inv] = {"proposed": 0, "shipped": 0, "status": "fallback_quote", "why": why}
            continue
        rec = evmod.record(inv, ev)
        schema = cards_llm.build_schema(rec["units"])
        items = cand["sentences"]
        n_items = len(items)
        survivors = []
        for item in items:
            st["proposed"] += 1
            evid = dedupe_evidence(item["evidence"])
            if len(evid) != len(item["evidence"]):
                st["evidence_duplicates_removed"] += len(item["evidence"]) - len(evid)
            res = gate(item["text"], evid, inv, ev, n_items)
            gl = {"kind": "sentence", "record": inv, "n": item["n"], "stage": "first", "text": item["text"],
                  "evidence": evid, "ok": res["ok"], "failed": res["failed"], "reasons": res["reasons"],
                  "checks": res["checks"], "lexical_support": res["lexical_support"]}
            gate_lines.append(gl)
            if res["ok"]:
                st["passed_first"] += 1
                survivors.append({"n": item["n"], "text": item["text"], "evidence": evid, "res": res,
                                  "repaired": False})
                continue
            st["rejected_first"] += 1
            first_gate[res["failed"][0]] += 1
            for g in res["failed"]:
                all_gates[g] += 1
            key = repair_key(inv, item["n"], item["text"])
            rep = repairs.get(key)
            if rep is None and do_repair:
                if inv not in raws:
                    raise SystemExit(f"{inv}: no raw reply in the candidate log to repair from")
                rep = call_repair(inv, rec, meta, raws[inv], item["n"], {"text": item["text"], "evidence": evid},
                                  res, schema, cand)
                repairs[key] = rep
                log(f"  repair call {inv} item {item['n']}: valid {rep['valid']}, {rep['wall_s']} s")
            if rep is None:
                st["not_repaired_no_call"] += 1
                gate_lines.append({"kind": "sentence", "record": inv, "n": item["n"], "stage": "repair",
                                   "ok": False, "failed": ["no_repair_call"],
                                   "reasons": ["no repair call in the log; run with --repair"]})
                continue
            st["repair_attempted"] += 1
            new = rep.get("replacement") if rep.get("valid") else None
            if not new:
                st["repair_failed"] += 1
                after_gates["invalid_reply"] += 1
                gate_lines.append({"kind": "sentence", "record": inv, "n": item["n"], "stage": "repair",
                                   "ok": False, "failed": ["invalid_reply"], "reasons": rep.get("errors") or []})
                continue
            evid2 = dedupe_evidence(new.get("evidence"))
            res2 = gate(new.get("text") or "", evid2, inv, ev, n_items)
            gate_lines.append({"kind": "sentence", "record": inv, "n": item["n"], "stage": "repair",
                               "text": new.get("text"), "evidence": evid2, "ok": res2["ok"],
                               "failed": res2["failed"], "reasons": res2["reasons"], "checks": res2["checks"],
                               "lexical_support": res2["lexical_support"]})
            if res2["ok"]:
                st["repaired"] += 1
                survivors.append({"n": item["n"], "text": new["text"], "evidence": evid2, "res": res2,
                                  "repaired": True, "first_pass_reasons": res["reasons"]})
            else:
                st["repair_failed"] += 1
                for g in res2["failed"]:
                    after_gates[g] += 1
        survivors.sort(key=lambda s: s["n"])
        # reviewed removals (pm session, before the data role's review): never counted as the review
        slots, kept = [], []
        for s in survivors:
            fields = {evmod.unit(inv, e["id"], ev)["field"] for e in s["evidence"]}
            full = s["text"].rstrip() + suffix(inv, fields)
            e = prereview_match(prereview, inv, full, s["text"])
            if e is None:
                kept.append(s)
                continue
            prereview_used.add(prereview.index(e))
            st["removed_by_prereview"] += 1
            slots.append(dict(s, prereview=e, full=full))
            prereview_removed.append({"investigation_id": inv, "n": s["n"], "sentence": full, "reason": e["reason"],
                                      "reviewer_kind": e["reviewer_kind"]})
            gate_lines.append({"kind": "sentence", "record": inv, "n": s["n"], "stage": "prereview", "text": full,
                               "ok": False, "failed": ["prereview"],
                               "reasons": [f"reviewed removal ({e['reviewer_kind']}): {e['reason']}"]})
        survivors = kept
        reviewed_by, review_word = None, REVIEW_NONE
        if reviews is not None:
            kept = []
            for s in survivors:
                fields = {evmod.unit(inv, e["id"], ev)["field"] for e in s["evidence"]}
                full = s["text"].rstrip() + suffix(inv, fields)
                rv = reviews.get((sheet_item(inv, s["n"]), _sha(full)))
                if rv:
                    s["review"] = rv
                    st["reviewed_shipped"] += 1
                    if rv["verdict"] in REMOVE_VERDICTS or rv["modality_kept"] == "no":
                        st["removed_by_review"] += 1
                        not_shown.append({"investigation_id": inv, "why": "review",
                                          "sentence": sheet_sentence(full, s)})
                        if rv["modality_kept"] == "no":
                            st["modality_removed"] += 1
                        gate_lines.append({"kind": "sentence", "record": inv, "n": s["n"], "stage": "review",
                                           "text": full, "ok": False, "failed": ["review"],
                                           "reasons": [f"review: verdict {rv['verdict']}, modality_kept "
                                                       f"{rv['modality_kept']} ({rv['reviewer_kind']}, "
                                                       f"{rv['reviewer_role']})"]})
                        continue
                kept.append(s)
            survivors = kept
            if final and any(not s.get("review") for s in survivors):
                st["reverted_final"] += 1
                st["removed_final"] += len(survivors)
                for s in survivors:
                    fields = {evmod.unit(inv, e["id"], ev)["field"] for e in s["evidence"]}
                    not_shown.append({"investigation_id": inv, "why": "final",
                                      "sentence": sheet_sentence(s["text"].rstrip() + suffix(inv, fields), s)})
                survivors = []
            if survivors and all(s.get("review") for s in survivors):
                reviewed_by, review_word = reviewer_line([s["review"] for s in survivors])
        card = assemble(ctx, base, inv, survivors, n_items, cand, meta, review_word,
                        slots=[x for x in slots if survivors], hidden=hidden, hidden_log=hidden_log,
                        kept_log=kept_log)
        if survivors:
            card["reviewed_by"] = reviewed_by
        cards.append(card)
        per_card[inv] = {"proposed": n_items, "shipped": len(survivors), "status": card["status"]}
        gate_lines.append({"kind": "card", "record": inv, "status": card["status"], "proposed": n_items,
                           "shipped": len(survivors)})
    for c in cards:
        per_card[c["investigation_id"]]["status"] = c["status"]
        per_card[c["investigation_id"]]["shipped"] = sum(x.get("origin") == "model" for x in c["sentences"])
    st["shipped"] = sum(v["shipped"] for v in per_card.values())
    st["dropped"] = st["proposed"] - st["passed_first"] - st["repaired"]
    matched = {h["_key"] for h in hidden_log} | {k["_key"] for k in kept_log}
    not_shown += [{"investigation_id": h["investigation_id"], "why": "quote_not_relevant", "sentence": h["_sentence"]}
                  for h in hidden_log]
    cands_shown = sum(1 for c in cards if c.get("removed_before_review"))
    st["cards_with_prereview_slot"] = cands_shown
    stats = {
        "proposed": st["proposed"], "passed_first": st["passed_first"], "rejected_first": st["rejected_first"],
        "rejected_by_gate": {g: all_gates[g] for g in GATE_NAMES + list(WRITER_RULES) if all_gates[g]},
        "rejected_first_gate": {g: first_gate[g] for g in GATE_NAMES + list(WRITER_RULES) if first_gate[g]},
        "repair_attempted": st["repair_attempted"], "repaired": st["repaired"],
        "repair_failed": st["repair_failed"],
        "repair_rejected_by_gate": dict(sorted(after_gates.items())),
        "not_repaired_no_call": st["not_repaired_no_call"],
        "dropped_by_gates": st["dropped"], "shipped_after_gates": st["passed_first"] + st["repaired"],
        "shipped": st["shipped"],
        "evidence_duplicates_removed": st["evidence_duplicates_removed"],
        "cards_without_candidate": st["cards_without_candidate"],
        "cards_by_status": dict(sorted(Counter(c["status"] for c in cards).items())),
        "removed_by_prereview": st["removed_by_prereview"], "prereview_removed": prereview_removed,
        "prereview_file": _rel(prereview_path), "prereview_entries": len(prereview),
        "prereview_unmatched": [e for i, e in enumerate(prereview) if i not in prereview_used],
        "reviewed_shipped": st["reviewed_shipped"], "removed_by_review": st["removed_by_review"],
        "modality_removed": st["modality_removed"], "reverted_final": st["reverted_final"],
        "removed_final": st["removed_final"],
        "hidden_quotes": public(hidden_log), "quotes_marked_but_kept": public(kept_log),
        "hidden_rows_matching_no_quote": sorted(k[0] for k in set(hidden) - matched),
        "not_shown": not_shown,
        "per_card": per_card,
        "candidates_log": _rel(candidates), "repair_log": _rel(llm.run_log_path(REPAIR_RUN)),
        "prompt_file": meta["prompt_file"], "prompt_file_sha256": meta["prompt_file_sha256"],
    }
    return {"cards": cards, "stats": stats, "gate_lines": gate_lines, "baseline": baseline, "meta": meta,
            "ctx": ctx}


# ====================================================================== write

def keep_updated(cards, path=OUT_CARDS):
    old = {}
    if Path(path).exists():
        try:
            old = {c["investigation_id"]: c for c in json.loads(Path(path).read_text(encoding="utf-8"))}
        except (ValueError, KeyError, TypeError):
            old = {}
    now = _now()
    for c in cards:
        o = old.get(c["investigation_id"])
        same = o and {k: v for k, v in o.items() if k != "updated"} == {k: v for k, v in c.items() if k != "updated"}
        c["updated"] = o["updated"] if same else (c.get("updated") if c.get("updated") and not o else now)
    return cards


def cards_inputs(meta, cards):
    inputs = ["data/insights/evidence.json", "data/psi/manifest.json", meta["prompt_file"], _rel(CANDIDATES)]
    if PREREVIEW.exists():
        inputs.append(_rel(PREREVIEW))
    rp = llm.run_log_path(REPAIR_RUN)
    if rp.exists():
        inputs.append(_rel(rp))
    inputs += [f"data/psi/catalog/{c['investigation_id']}.json" for c in cards]
    return inputs


def write_cards(res, built_by=BUILT_BY, extra_inputs=(), extra_meta=None, path=OUT_CARDS):
    cards = keep_updated(res["cards"], path)
    n_model = sum(s.get("origin") == "model" for c in cards for s in c["sentences"])
    lm = config.MODEL_LABEL if n_model else config.NO_MODEL
    label = ("AI-generated data file: built by code written with an AI assistant (Claude Code). Cards with status "
             "'generated' or 'generated_partial' hold summary sentences written by the language model "
             f"{config.MODEL_LABEL}, run locally through {config.RUNNER}; every such sentence passed the team's "
             "code gates (ai/checks.py) and names its PSI source; see each sentence's review field. Key points and "
             "'fallback_quote' cards are verbatim NASA PSI text chosen by code. Team output, not a NASA conclusion; "
             "not operational safety guidance.")
    extra = {"entries": len(cards), "statuses": dict(sorted(Counter(c["status"] for c in cards).items())),
             "model_sentences": n_model, "prompt_file": res["meta"]["prompt_file"],
             "prompt_sha256": res["meta"]["prompt_file_sha256"],
             "params": {k: config.DEFAULTS[k] for k in ("think", "temperature", "seed", "num_ctx", "num_predict",
                                                         "format_mode")},
             "model_digest": res["meta"].get("model_digest"), "runner": config.RUNNER,
             "baseline_built_by": T.BUILT_BY,
             "removed_by_prereview": res["stats"]["removed_by_prereview"]}
    extra.update(extra_meta or {})
    block = metamod.meta(built_by, lm, cards_inputs(res["meta"], cards) + list(extra_inputs), label=label, **extra)
    metamod.write_json(path, cards, block)
    return cards


def write_gate_log(res):
    path = llm.run_log_path(GATES_RUN)
    head = {"_meta": {"what": "gate results for every candidate and repair sentence, including rejected ones; "
                              "not product content",
                      "built_by": BUILT_BY, "code_written_with": config.CODE_WRITTEN_WITH,
                      "candidates_log": res["stats"]["candidates_log"], "repair_log": res["stats"]["repair_log"],
                      "gates": "ai/checks.py check_sentence (gates 1 to 11) plus the writer rule key_point",
                      "created": _now()}}
    lines = [head] + res["gate_lines"] + [{"kind": "stats", **{k: v for k, v in res["stats"].items()
                                                                 if k not in ("per_card", "not_shown")}}]
    path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lines), encoding="utf-8")
    return path


def print_stats(res, out=print):
    s = res["stats"]
    out(f"sentences proposed: {s['proposed']}")
    out(f"passed every gate on the first pass: {s['passed_first']}; rejected: {s['rejected_first']}")
    out(f"  rejected by gate (a sentence can fail several): {s['rejected_by_gate']}")
    out(f"  first failing gate: {s['rejected_first_gate']}")
    out(f"repair calls: {s['repair_attempted']}; repaired (replacement passed every gate): {s['repaired']}; "
        f"repair failed (dropped): {s['repair_failed']} {s['repair_rejected_by_gate']}")
    if s["not_repaired_no_call"]:
        out(f"  not repaired because no repair call is logged: {s['not_repaired_no_call']}")
    out(f"dropped by the gates: {s['dropped_by_gates']}; passed the gates: {s['shipped_after_gates']}; "
        f"removed before review: {s['removed_by_prereview']}; "
        f"removed by review: {s['removed_by_review']}; reverted by --final: {s['removed_final']}; "
        f"shipped model sentences: {s['shipped']}")
    out(f"removed by the reviewed removals ({PREREVIEW_KIND}, {s['prereview_file']}): {s['removed_by_prereview']}"
        + (f"; entries that match no sentence: {len(s['prereview_unmatched'])}" if s["prereview_unmatched"] else ""))
    out(f"cards by status: {s['cards_by_status']}")
    for line in res["gate_lines"]:
        if line["kind"] == "sentence" and not line["ok"]:
            out(f"  REJECTED {line['record']} item {line['n']} ({line['stage']}): {line.get('text')!r}")
            for r in line["reasons"]:
                out(f"      {r}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--candidates", default=str(CANDIDATES), help="candidate log from ai/cards_llm.py")
    ap.add_argument("--repair", action="store_true", help="call gpt-oss:20b once for each failed sentence "
                                                          "that has no logged repair yet")
    ap.add_argument("--check", action="store_true", help="build from the logs and compare with cards.json; write nothing")
    ap.add_argument("--write-gate-log", action="store_true",
                    help="also rewrite the run record ai/runs/cards_20261114-v3-gates.jsonl (done anyway with --repair)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    out = (lambda *x, **k: None) if a.quiet else print
    res = build(Path(a.candidates), do_repair=a.repair and not a.check, log=out)
    print_stats(res, out)
    if a.check:
        old = json.loads(OUT_CARDS.read_text(encoding="utf-8")) if OUT_CARDS.exists() else None
        strip = lambda xs: [{k: v for k, v in x.items() if k not in ("updated",)} for x in xs]  # noqa: E731
        # review fields are set by ai/apply_review.py; compare without them
        def unrev(xs):
            ys = copy.deepcopy(strip(xs))
            for c in ys:
                c.pop("reviewed_by", None)
                c.pop("label", None)
                for s in c.get("sentences", []):
                    s.pop("review", None)
            return ys
        same = old is not None and unrev(old) == unrev(res["cards"])
        print(f"{_rel(OUT_CARDS)}: {'matches the build (review fields aside)' if same else 'DIFFERS from the build'}")
        return 0 if same else 1
    write_cards(res)
    written = [_rel(OUT_CARDS)]
    if a.repair or a.write_gate_log:
        written.append(_rel(write_gate_log(res)))
    from ai import apply_review  # noqa: E402  (the sheet writer lives with the review tools)
    # The sheet lists what the cards show once the sheet's verdicts are applied (a review removal changes
    # which key points are picked), plus the rows whose verdict removed their sentence; a sheet written from
    # the unreviewed cards above went out of step with the page (independent check, 14 Nov 17:10).
    sheet = apply_review.refresh_sheet(candidates=Path(a.candidates))
    out(f"\nwrote {', '.join(written)} and {_rel(sheet['path'])} ({sheet['rows']} rows, "
        f"{sheet['kept']} earlier verdicts kept)" + ("" if len(written) > 1 else
                                                    "; the gate log in ai/runs/ was left as it is (a run record)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
