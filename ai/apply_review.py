# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Component E tools: the review sheet, applying the verdicts, and data/insights/quality.json.

refresh_sheet() writes ai/review/review_sheet.csv (called by ai/apply_cards.py after it writes cards.json,
and by this script after it applies the verdicts). It builds the cards with the sheet's own verdicts
applied, so the sheet lists what the reviewed cards show: a review removal changes which key points the
pick rule chooses, and a sheet written from the unreviewed cards (before 14 Nov 17:10) listed quotes the
page did not show and missed some it did. One row per shown sentence (column shown = yes):
  - every model-written summary sentence (origin 'model'), lowest lexical support first: all of
    them are reviewed, not a sample;
  - every quoted key point and quoted summary (origin 'quote'): checked for relevance only;
  - every template statement of data/insights/scenarios.json (origin 'template'): read once for wording.
and one row (shown = no) for each sentence that is not shown because of a verdict in the sheet (a model
sentence marked not, partly or modality no; a quote marked not_relevant) or of --final, so that its
verdict is kept and the next build removes it again. Verdicts already filled in are kept when the sheet
is rewritten, as long as the sentence text is unchanged (matched by item id and sentence_sha); a row
that is new, or whose text changed, has no verdict and goes back to the reviewer.

Verdict values
  model     verdict supported | partly | not; modality_kept yes | no (an objective, hypothesis or plan
            is still worded as one, and hedges are kept)
  quote     verdict relevant | not_relevant (modality_kept empty)
  template  verdict wording_ok | wording_issue (modality_kept empty)
  reviewer_kind person | ai_session; reviewer_role a team role (pm, data, ui) or 'human lead'.

Applying (python3 ai/apply_review.py): rebuilds the cards from the logs through ai/apply_cards.py
(no model call; the reviewed removals of ai/review/pm_prereview.json are applied there first and are
counted apart, under removed_before_review), removes every model sentence marked 'not' or 'partly' or with modality_kept 'no'
(the card falls back to its NASA quote if its summary empties; nothing is softened), writes each
model sentence's review field, and sets reviewed_by on a card only when every model sentence of it
has a review. With --final it also reverts to its quote any card that keeps an unreviewed model
sentence (pre-freeze sync). It then writes data/insights/quality.json, reproduced from the sheet and
the gate results. Rows read by an AI session are never counted as read by a person. The support rate
is the rate before removal, with its n.

A quote marked 'not_relevant' is not shown on its card (ai/apply_cards.py; counted under
quotes_not_shown_by_review, apart from the model-sentence counts). Nothing is reworded: a quote is shown
or not shown. A 'wording_issue' template row is counted and listed; it is a request to the code that
builds the text (ai/templates.py, ai/build_baseline.py).

    python3 ai/apply_review.py                # apply the sheet as it is, write quality.json
    python3 ai/apply_review.py --final        # also revert cards with an unreviewed model sentence
    python3 ai/apply_review.py --dry-run      # print what would change; write nothing
    python3 ai/apply_review.py --sheet-only   # rewrite the sheet (cards built with the sheet's verdicts)
"""
import argparse
import csv
import hashlib
import io
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import config, evidence as evmod, meta as metamod  # noqa: E402

ROOT = config.ROOT
BUILT_BY = "ai/apply_review.py"
SHEET = config.AI_DIR / "review" / "review_sheet.csv"
OUT_QUALITY = config.INSIGHTS_DIR / "quality.json"
CARDS = config.INSIGHTS_DIR / "cards.json"
SCENARIOS = config.INSIGHTS_DIR / "scenarios.json"

COLUMNS = ["item", "role", "origin", "sentence", "cited_ids", "cited_text", "checks", "lexical_support",
           "verdict", "modality_kept", "reviewer_kind", "reviewer_role", "note", "second_opinion_score",
           "sentence_sha", "repaired", "shown"]
REVIEW_COLUMNS = ["verdict", "modality_kept", "reviewer_kind", "reviewer_role", "note", "second_opinion_score"]
VERDICTS = {"model": ("supported", "partly", "not"), "quote": ("relevant", "not_relevant"),
            "template": ("wording_ok", "wording_issue")}
MODALITY = ("yes", "no")
REVIEWER_KINDS = ("person", "ai_session")


def _sha(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


def _now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _rel(p):
    p = Path(p).resolve()
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


# ====================================================================== sheet

def _cited_text(inv, ids, ev):
    out = []
    for uid in ids:
        try:
            u = evmod.unit(inv, uid, ev)
        except KeyError:
            out.append(f"[{uid}] (not in evidence.json)")
            continue
        out.append(f"[{uid}] {u['prefix']} \"{u['text']}\"")
    return " | ".join(out)


def card_rows(cards, ev, shown="yes"):
    from ai import apply_cards  # quote_item: the one place the row id of a quote is made
    model, quotes = [], []
    for c in cards:
        inv = c["investigation_id"]
        for s in c.get("sentences") or []:
            ids = [e["id"] for e in s.get("evidence") or []]
            if s.get("origin") == "model":
                ch = s.get("checks") or {}
                bad = [k[:-3] for k, v in ch.items() if not v]
                model.append({
                    "item": f"card:{inv}:summary:{s['n']}", "role": s["role"], "origin": "model",
                    "sentence": s["text"], "cited_ids": " ".join(ids), "cited_text": _cited_text(inv, ids, ev),
                    "checks": "all 10 gates passed" if ch and not bad else ("failed: " + ", ".join(bad)),
                    "lexical_support": "" if s.get("lexical_support") is None else f"{s['lexical_support']:.3f}",
                    "sentence_sha": _sha(s["text"]), "repaired": "yes" if s.get("repaired") else "no",
                    "shown": shown})
            else:
                quotes.append({
                    "item": apply_cards.quote_item(inv, s),
                    "role": s["role"], "origin": "quote",
                    "sentence": f"{s.get('field_label')} \"{s['text']}\"", "cited_ids": " ".join(ids),
                    "cited_text": f"{s.get('source')} [{s.get('char_start')}:{s.get('char_end')}]",
                    "checks": "verbatim span of the PSI field", "lexical_support": "",
                    "sentence_sha": _sha(s["text"]), "repaired": "", "shown": shown})
    model.sort(key=lambda r: (float(r["lexical_support"]) if r["lexical_support"] else -1.0, r["item"]))
    return model, quotes


def template_rows(scenarios):
    out = []

    def add(item, role, text, sources):
        out.append({"item": item, "role": role, "origin": "template", "sentence": text,
                    "cited_ids": "", "cited_text": " ; ".join(sources or []), "checks": "template checks (ai/check_all.py)",
                    "lexical_support": "", "sentence_sha": _sha(text), "repaired": "", "shown": "yes"})

    for sc in scenarios:
        sid = sc["id"]
        if sc.get("frame"):
            add(f"scenario:{sid}:frame", "frame", sc["frame"], sc.get("frame_sources"))
        for n in sc.get("needs") or []:
            add(f"scenario:{sid}:need:{n['need_id']}", "need_statement", n["statement"], n.get("sources"))
        for i, g in enumerate(sc.get("gaps") or []):
            add(f"scenario:{sid}:gap:{i + 1}", "gap", g["text"], g.get("sources"))
            if g.get("needed_data"):
                add(f"scenario:{sid}:gap:{i + 1}:needed_data", "gap_needed_data", g["needed_data"], g.get("sources"))
        for x in sc.get("result_notes") or []:
            add(f"scenario:{sid}:note:{x['investigation_id']}", "result_note", x["text"], x.get("sources"))
    return out


def read_sheet(path=SHEET):
    path = Path(path)
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_sheet(cards=None, scenarios=None, path=SHEET, ev=None, not_shown=()):
    """Write the review sheet; keep verdicts already filled in for unchanged sentences.
    cards: the cards as shown (rows with shown = yes); not_shown: the build's stats['not_shown'], the
    sentences left out because of a verdict or of --final (rows with shown = no)."""
    ev = ev or evmod.load()
    cards = cards if cards is not None else json.loads(CARDS.read_text(encoding="utf-8"))
    scenarios = scenarios if scenarios is not None else (
        json.loads(SCENARIOS.read_text(encoding="utf-8")) if SCENARIOS.exists() else [])
    model, quotes = card_rows(cards, ev)
    gone_m, gone_q = card_rows([{"investigation_id": x["investigation_id"], "sentences": [x["sentence"]]}
                                for x in not_shown or []], ev, shown="no")
    seen = {(r["item"], r["sentence_sha"]) for r in model + quotes}
    model += [r for r in gone_m if (r["item"], r["sentence_sha"]) not in seen]
    quotes += [r for r in gone_q if (r["item"], r["sentence_sha"]) not in seen]
    model.sort(key=lambda r: (float(r["lexical_support"]) if r["lexical_support"] else -1.0, r["item"]))
    rows = model + quotes + template_rows(scenarios)
    old = {(r["item"], r.get("sentence_sha")): r for r in read_sheet(path)}
    kept = 0
    for r in rows:
        o = old.get((r["item"], r["sentence_sha"]))
        for k in REVIEW_COLUMNS:
            r[k] = (o or {}).get(k, "") or ""
        if o and o.get("verdict"):
            kept += 1
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in COLUMNS})
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(buf.getvalue(), encoding="utf-8")
    return {"path": Path(path), "rows": len(rows), "kept": kept,
            "by_origin": dict(Counter(r["origin"] for r in rows)),
            "not_shown": sum(r["shown"] == "no" for r in rows),
            "without_verdict": [r["item"] for r in rows if not r["verdict"]]}


def refresh_sheet(path=SHEET, candidates=None, log=None):
    """Rewrite the sheet from the cards built with the sheet's own verdicts applied (no --final)."""
    from ai import apply_cards
    rows = read_sheet(path)
    validate_rows(rows)
    kw = {"candidates": candidates} if candidates else {}
    res = apply_cards.build(do_repair=False, log=log or (lambda *a, **k: None), reviews=model_reviews(rows),
                            hidden_quotes=hidden_quotes(rows), **kw)
    return write_sheet(res["cards"], path=path, not_shown=res["stats"]["not_shown"])


# ====================================================================== verdicts

class SheetError(ValueError):
    pass


def validate_rows(rows):
    errs = []
    for i, r in enumerate(rows, start=2):
        o = r.get("origin")
        v = (r.get("verdict") or "").strip()
        if o not in VERDICTS:
            errs.append(f"line {i}: unknown origin {o!r}")
            continue
        if not v:
            if any((r.get(k) or "").strip() for k in ("modality_kept", "reviewer_kind", "reviewer_role")):
                errs.append(f"line {i} ({r['item']}): reviewer fields filled but no verdict")
            continue
        if v not in VERDICTS[o]:
            errs.append(f"line {i} ({r['item']}): verdict {v!r} is not one of {VERDICTS[o]}")
        mk = (r.get("modality_kept") or "").strip()
        if o == "model" and mk not in MODALITY:
            errs.append(f"line {i} ({r['item']}): a model sentence needs modality_kept yes or no")
        if o != "model" and mk:
            errs.append(f"line {i} ({r['item']}): modality_kept is only for model sentences")
        if (r.get("reviewer_kind") or "").strip() not in REVIEWER_KINDS:
            errs.append(f"line {i} ({r['item']}): reviewer_kind must be person or ai_session")
        if not (r.get("reviewer_role") or "").strip():
            errs.append(f"line {i} ({r['item']}): reviewer_role is empty")
    if errs:
        raise SheetError("review sheet has errors:\n  " + "\n  ".join(errs))


def hidden_quotes(rows):
    """{(item, sentence_sha): review} of the quote rows marked not_relevant: those quotes are not shown."""
    out = {}
    for r in rows:
        if r["origin"] == "quote" and (r.get("verdict") or "").strip() == "not_relevant":
            out[(r["item"], r["sentence_sha"])] = {"verdict": "not_relevant",
                                                   "reviewer_kind": r["reviewer_kind"].strip(),
                                                   "reviewer_role": r["reviewer_role"].strip()}
    return out


def model_reviews(rows):
    out = {}
    for r in rows:
        if r["origin"] == "model" and (r.get("verdict") or "").strip():
            out[(r["item"], r["sentence_sha"])] = {
                "verdict": r["verdict"].strip(), "modality_kept": r["modality_kept"].strip(),
                "reviewer_kind": r["reviewer_kind"].strip(), "reviewer_role": r["reviewer_role"].strip()}
    return out


# ====================================================================== quality.json

def recount_status():
    """Run check_all's second-path recount; return (ok, failure messages)."""
    from ai import check_all
    rep = check_all.Report()
    check_all.check_recount(rep, check_all.recount())
    fails = [x["message"] for x in rep.failures()]
    return not fails, fails


def quality(stats, rows, scenarios, recount):
    reviewed = [r for r in rows if r["origin"] == "model" and (r.get("verdict") or "").strip()]
    n_model_rows = sum(r["origin"] == "model" for r in rows)
    verdicts = Counter(r["verdict"].strip() for r in reviewed)
    modality = Counter(r["modality_kept"].strip() for r in reviewed)
    person = sum(r["reviewer_kind"].strip() == "person" for r in reviewed)
    ai_s = sum(r["reviewer_kind"].strip() == "ai_session" for r in reviewed)
    n = len(reviewed)
    tmpl = [r for r in rows if r["origin"] == "template"]
    quotes = [r for r in rows if r["origin"] == "quote"]
    ok, fails = recount
    return {
        "description": ("Measured counts for the model-written card sentences (gpt-oss:20b) and their checks, "
                        "reproduced by ai/apply_review.py from ai/review/review_sheet.csv and the gate results of "
                        "ai/apply_cards.py. Rates are measured before removal and carry their n. Rows read by an AI "
                        "session are never counted as read by a person. The counts reviewed_person and reviewed_ai_session say who "
                        "read the rows."),
        "proposed": stats["proposed"],
        "passed_gates_first_pass": stats["passed_first"],
        "rejected_first_pass": stats["rejected_first"],
        "rejected_by_gate": stats["rejected_by_gate"],
        "rejected_first_gate": stats["rejected_first_gate"],
        "rejected_by_gate_note": ("rejected_by_gate counts every failing gate of a first-pass sentence (a sentence "
                                  "can fail several); rejected_first_gate counts each rejected sentence once. "
                                  "'key_point' is the writer rule that the first cited unit is a quotable sentence."),
        "repair_attempted": stats["repair_attempted"],
        "repaired": stats["repaired"],
        "repair_failed": stats["repair_failed"],
        "repair_rejected_by_gate": stats["repair_rejected_by_gate"],
        "dropped_by_gates": stats["dropped_by_gates"],
        "passed_gates": stats["shipped_after_gates"],
        "removed_before_review": {
            "n": stats["removed_by_prereview"],
            "reviewer_kind": "ai_session_pm",
            "file": stats["prereview_file"],
            "entries_in_file": stats["prereview_entries"],
            "entries_matching_no_sentence": len(stats["prereview_unmatched"]),
            "sentences": stats["prereview_removed"],
            "rule": ("sentences that passed every code gate and were removed by the pm session's reviewed removals "
                     "(ai/review/pm_prereview.json) before the review; each slot shows the quoted NASA sentence it "
                     "cited. Counted apart from the review: not part of removed_by_review, verdicts or the support "
                     "rate, and never a reason to set reviewed_by."),
        },
        "removed_by_review": stats["removed_by_review"],
        "modality_removed": stats["modality_removed"],
        "reverted_by_final": stats["removed_final"],
        "shipped_model_sentences": stats["shipped"],
        "cards_by_status": stats["cards_by_status"],
        "model_rows_in_sheet": n_model_rows,
        "reviewed_person": person,
        "reviewed_ai_session": ai_s,
        "unreviewed_model_rows": n_model_rows - n,
        "verdicts": {k: verdicts.get(k, 0) for k in VERDICTS["model"]},
        "modality_kept": {k: modality.get(k, 0) for k in MODALITY},
        "support_rate": round(verdicts.get("supported", 0) / n, 3) if n else None,
        "n": n,
        "support_rate_rule": "supported / reviewed model sentences, before removal; null while n is 0",
        "quote_rows": len(quotes),
        "quote_rows_shown": sum((r.get("shown") or "yes") == "yes" for r in quotes),
        "quote_verdicts": dict(Counter(r["verdict"].strip() for r in quotes if (r.get("verdict") or "").strip())),
        "quotes_not_shown_by_review": {
            "n": len(stats["hidden_quotes"]),
            "rows": stats["hidden_quotes"],
            "kept_although_marked": stats["quotes_marked_but_kept"],
            "marked_rows_matching_no_quote": stats["hidden_rows_matching_no_quote"],
            "rule": ("a verbatim NASA quote whose sheet row is marked not_relevant is not shown on its card: a key "
                     "point is dropped and the pick rule goes on to its next candidate; the quoted slot of a "
                     "removed model sentence uses the next unit that sentence cited, or is left out; a card's last "
                     "quoted summary sentence is never removed (listed under kept_although_marked). Nothing is "
                     "reworded. Counted apart from the model-sentence counts (removed_by_review, verdicts, "
                     "support_rate)."),
        },
        "template_statements": len(tmpl),
        "template_verdicts": dict(Counter(r["verdict"].strip() for r in tmpl if (r.get("verdict") or "").strip())),
        "rows_without_verdict": {
            "n": sum(not (r.get("verdict") or "").strip() for r in rows),
            "by_origin": dict(Counter(r["origin"] for r in rows if not (r.get("verdict") or "").strip())),
            "items": [r["item"] for r in rows if not (r.get("verdict") or "").strip()],
            "rule": ("rows that are new or whose sentence text changed (matched by item and sentence_sha) have no "
                     "verdict and go back to the reviewer"),
        },
        "recount_ok": ok,
        "recount_failures": fails,
        "second_opinion": None,
        "candidates_log": stats["candidates_log"],
        "repair_log": stats["repair_log"],
        "prompt_file": stats["prompt_file"],
        "prompt_file_sha256": stats["prompt_file_sha256"],
        "date": datetime.now().astimezone().date().isoformat(),
    }


def write_quality(q, path=OUT_QUALITY):
    inputs = ["data/insights/cards.json", _rel(SHEET), q["candidates_log"], q["prompt_file"]]
    if (ROOT / q["removed_before_review"]["file"]).exists():
        inputs.append(q["removed_before_review"]["file"])
    if (ROOT / q["repair_log"]).exists():
        inputs.append(q["repair_log"])
    if SCENARIOS.exists():
        inputs.append("data/insights/scenarios.json")
    block = metamod.meta(BUILT_BY, config.NO_MODEL, inputs, label=(
        "AI-generated data file: built by code written with an AI assistant (Claude Code); no language model ran "
        "to build it. Counts of the gpt-oss:20b card sentences, the code gates and the review verdicts, computed by "
        "code. Team output, not a NASA conclusion."))
    old = json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).exists() else {}
    if {k: v for k, v in old.items() if k not in ("_meta", "date")} == {k: v for k, v in q.items() if k != "date"}:
        q["date"] = old.get("date", q["date"])  # unchanged counts: keep the file byte-identical
    metamod.write_json(path, q, block)


# ====================================================================== main

def run(final=False, dry_run=False, sheet_path=SHEET, out=print):
    from ai import apply_cards
    rows = read_sheet(sheet_path)
    validate_rows(rows)
    reviews = model_reviews(rows)
    hidden = hidden_quotes(rows)
    res = apply_cards.build(do_repair=False, log=out, reviews=reviews, final=final, hidden_quotes=hidden)
    st = res["stats"]
    scen = json.loads(SCENARIOS.read_text(encoding="utf-8")) if SCENARIOS.exists() else []
    sheet = None
    if not dry_run:
        # the sheet follows the cards as the page shows them (verdicts applied); verdicts carry over by
        # item and sentence_sha, so a rewrite never changes one
        sheet = write_sheet(res["cards"], scenarios=scen, path=sheet_path, not_shown=st["not_shown"])
        rows = read_sheet(sheet_path)
    q = quality(st, rows, scen, recount_status())
    unmatched = len(reviews) - st["reviewed_shipped"]  # reviewed rows whose sentence no longer passes or changed
    q["reviewed_rows_not_matched"] = unmatched
    out(f"sheet: {len(rows)} rows; model rows reviewed {q['n']} of {q['model_rows_in_sheet']} "
        f"(person {q['reviewed_person']}, AI session {q['reviewed_ai_session']})")
    out(f"verdicts {q['verdicts']}; modality_kept {q['modality_kept']}; support rate {q['support_rate']} (n {q['n']})")
    out(f"removed before review (ai_session_pm, {q['removed_before_review']['file']}): "
        f"{q['removed_before_review']['n']}")
    out(f"removed by review {q['removed_by_review']} (modality {q['modality_removed']}); reverted by --final "
        f"{q['reverted_by_final']}; shipped model sentences {q['shipped_model_sentences']}")
    out(f"quotes not shown (marked not_relevant): {q['quotes_not_shown_by_review']['n']}"
        + (f"; marked but kept as a card's last summary quote: {len(q['quotes_not_shown_by_review']['kept_although_marked'])}"
           if q['quotes_not_shown_by_review']['kept_although_marked'] else "")
        + (f"; marked rows matching no quote: {q['quotes_not_shown_by_review']['marked_rows_matching_no_quote']}"
           if q['quotes_not_shown_by_review']['marked_rows_matching_no_quote'] else ""))
    out(f"cards by status {q['cards_by_status']}")
    out(f"recount_ok {q['recount_ok']}" + (f": {q['recount_failures']}" if q["recount_failures"] else ""))
    if unmatched:
        out(f"note: {unmatched} reviewed model row(s) match no sentence that passed the gates (text changed)")
    if dry_run:
        return q, res
    if sheet:
        out(f"wrote {_rel(sheet_path)}: {sheet['rows']} rows ({sheet['not_shown']} not shown), "
            f"{sheet['kept']} verdicts kept, {len(sheet['without_verdict'])} rows without a verdict")
    changed = bool(reviews) or bool(hidden) or final
    if changed:
        apply_cards.write_cards(res, built_by=BUILT_BY, extra_inputs=[_rel(sheet_path)],
                                extra_meta={"review_applied": True, "final": final})
        out(f"wrote {_rel(CARDS)} (reviews applied{', --final' if final else ''})")
    else:
        out(f"{_rel(CARDS)} left as written by ai/apply_cards.py (no verdict in the sheet, no --final)")
    write_quality(q)
    out(f"wrote {_rel(OUT_QUALITY)}")
    return q, res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--final", action="store_true", help="revert cards that keep an unreviewed model sentence")
    ap.add_argument("--dry-run", action="store_true", help="print what would change; write nothing")
    ap.add_argument("--sheet", default=str(SHEET), help="review sheet to apply")
    ap.add_argument("--sheet-only", action="store_true", help="rewrite the review sheet and stop")
    a = ap.parse_args(argv)
    if a.sheet_only:
        r = refresh_sheet(path=Path(a.sheet))
        print(f"wrote {_rel(r['path'])}: {r['rows']} rows {r['by_origin']}, {r['kept']} verdicts kept")
        return 0
    try:
        run(final=a.final, dry_run=a.dry_run, sheet_path=Path(a.sheet))
    except SheetError as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
