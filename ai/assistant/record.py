# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Record conversations with the local model for the public page (ai/assistant/DESIGN.md section 13.6).

    python3 -m ai.assistant.record                     # every conversation of eval/record_script.json, live;
                                                       #   writes data/insights/assistant_recorded.json
    python3 -m ai.assistant.record --only lunar_cotton,earth --out DIR
    python3 -m ai.assistant.record --fake --out DIR    # a fake model (tests); never into data/insights/

Each turn runs through ai.assistant.pipeline.turn() with mode "live" and arm "full", starting from the state
the previous turn of the same conversation returned (follow-ups are carried as structured state, as on the
page). The model calls are logged to ai/runs/assistant_record_<YYYYMMDD-HHMM>.jsonl through ai/llm.py.

Every recorded response is marked mode "recorded" and gets the recorded answer label with the date. The file
is not written when a turn ends in an error, when a response does not match the RESPONSE schema of
DESIGN.md, or when a model-written sentence fails a code gate against the facts it cites.
Standard library only.
"""
import argparse
import copy
import json
import sys
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ai import config, llm, meta as metamod  # noqa: E402
from ai.assistant import evaluate as EV  # noqa: E402

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "eval" / "record_script.json"
OUT_JSON = config.INSIGHTS_DIR / "assistant_recorded.json"
LABEL = ("AI-generated data file: built by code written with an AI assistant (Claude Code). Conversations recorded "
         "with the local language model gpt-oss:20b (f38aa0c53da5): the answers were written by the model only from "
         "facts that code looked up in the team's files, checked by code gates and a model checker, and are "
         "replayed on the public page marked as recorded. Team output, not a NASA conclusion, and not safety "
         "guidance.")
LABEL_FAKE = ("AI-generated data file: built by code written with an AI assistant (Claude Code). A test run of the "
              "recording code with a fake model; no language model ran. Not for the public page.")


def recorded_label(date):
    try:
        from ai.assistant import texts
        return texts.ANSWER_LABELS["recorded"].format(date=date)
    except (ImportError, KeyError, AttributeError):
        return (f"Recorded on {date} with the local language model (gpt-oss:20b) and replayed here; no model runs "
                "on this page. A research exploration tool, not safety guidance.")


def problems_of(resp, schema, gate_sentence):
    """Why a response must not be recorded (empty list when it may)."""
    out = []
    if resp.get("kind") == "error":
        out.append("the turn ended in an error")
    errs = llm.validate(resp, schema)
    if errs:
        out.append("not a RESPONSE: " + "; ".join(errs[:3]))
    facts = {f.get("id"): f for f in resp.get("facts") or [] if isinstance(f, dict)}
    answer = resp.get("answer") or {}
    for s in answer.get("sentences") or []:
        ids = s.get("facts") or []
        missing = [i for i in ids if i not in facts]
        if missing:
            out.append(f"sentence {s.get('n')} cites unknown facts {missing}")
        if (s.get("origin") or answer.get("origin")) == "model":
            fails = EV.gates(gate_sentence, s.get("text", ""), [facts[i] for i in ids if i in facts],
                             resp.get("request"), turn_ids=set(facts), cited_ids=ids)
            if fails:
                out.append(f"sentence {s.get('n')} fails {', '.join(g for g, _ in fails)}")
    return out


PROGRESS = config.ASSISTANT_RUNTIME_DIR / "record_progress.json"


def record(only=None, fake=False, out_dir=None, quiet=False, script_path=SCRIPT, skip_failed=False, resume=False):
    """skip_failed: leave out a conversation that has a problem (named in the file) instead of writing nothing.
    resume: reuse the conversations already recorded in this run (git-ignored progress file), live runs only."""
    say = (lambda *a: None) if quiet else (lambda *a: print(*a, flush=True))
    if fake and out_dir is None:
        raise SystemExit("--fake writes only into --out DIR, never into data/insights/")
    script = json.loads(Path(script_path).read_text(encoding="utf-8"))
    convs = [c for c in script["conversations"] if not only or c["id"] in set(only)]
    if not convs:
        raise SystemExit("no conversation selected")
    from ai.assistant import pipeline
    gate_sentence = EV._gate_fn()
    schema = EV.design_block("RESPONSE")
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    out_dir = Path(out_dir) if out_dir else None
    log_dir = out_dir if fake else None
    chat = EV.ReuseChat(EV.SchemaFake() if fake else llm.chat, f"assistant_record_{stamp}", log_dir=log_dir)
    if not fake:
        status = llm.server_status()
        if status.get("reason"):
            raise SystemExit(f"the model cannot be called: {status['reason']}")
    date = datetime.now().strftime("%d %B %Y").lstrip("0")
    label = recorded_label(date)
    try:
        from ai.assistant import tools as TL
        shared_data = TL.Data()
    except Exception:  # noqa: BLE001 - the pipeline loads its own data then
        shared_data = None

    out, problems, meta_seen, dropped = [], [], {}, []
    prog = {}
    if resume and not fake and PROGRESS.exists():
        prog = json.loads(PROGRESS.read_text(encoding="utf-8"))
    tkw = EV.turn_kwargs(pipeline, chat.run)
    for c in convs:
        if c["id"] in (prog.get("done") or {}) and prog["done"][c["id"]]["turns_script"] == c["turns"]:
            out.append(prog["done"][c["id"]]["conversation"])
            meta_seen.update(prog.get("meta") or {})
            say(f"[{c['id']}] reused from {EV._rel(PROGRESS)}")
            continue
        state, turns = None, []
        conv_problems = []
        for i, t in enumerate(c["turns"], 1):
            kw = {"message": t["message"]} if "message" in t else {"request": t["request"],
                                                                     "answer_mode": t.get("answer_mode")}
            try:
                with (EV.fake_live() if fake else nullcontext()):
                    resp = pipeline.turn(state=copy.deepcopy(state), chat=chat, mode="live", arm="full",
                                         data=shared_data, **kw, **tkw)
            except Exception as exc:  # noqa: BLE001 - reported, the file is then not written
                conv_problems.append(f"{c['id']} turn {i}: {type(exc).__name__}: {exc}")
                break
            resp = copy.deepcopy(resp)
            resp["mode"] = "recorded"
            resp["label"] = label if (resp.get("answer") or {}).get("origin") == "model" else resp.get("label", "")
            for p in problems_of(resp, schema, gate_sentence):
                conv_problems.append(f"{c['id']} turn {i}: {p}")
            for k in ("data_version", "commit"):
                if (resp.get("trace") or {}).get(k):
                    meta_seen[k] = resp["trace"][k]
            state = resp.get("state")
            turns.append({"message": t.get("message") or t.get("label") or "", "response": resp})
            tr = resp.get("trace") or {}
            say(f"[{c['id']} {i}/{len(c['turns'])}] {resp.get('kind')} calls={tr.get('model_calls')} "
                f"{round((tr.get('total_ms') or 0) / 1000, 1)} s")
        if conv_problems and skip_failed:
            dropped.append({"id": c["id"], "problems": conv_problems})
            for p in conv_problems:
                print("DROPPED:", p, file=sys.stderr)
            continue
        problems += conv_problems
        conv = {"id": c["id"], "title": c["title"], "turns": turns}
        out.append(conv)
        if not fake and not conv_problems:
            prog.setdefault("done", {})[c["id"]] = {"turns_script": c["turns"], "conversation": conv}
            prog["meta"] = meta_seen
            PROGRESS.parent.mkdir(parents=True, exist_ok=True)
            PROGRESS.write_text(json.dumps(prog, ensure_ascii=False), encoding="utf-8")

    payload = {"recorded_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
               "model": config.NO_MODEL if fake else config.MODEL_LABEL, "fake_model": bool(fake),
               "data_version": meta_seen.get("data_version"), "commit": meta_seen.get("commit"),
               "run_log": EV._rel(EV._log_path(chat.run, log_dir)),
               "conversations": out, "left_out": dropped}
    if problems:
        for p in problems:
            print("PROBLEM:", p, file=sys.stderr)
        raise SystemExit(f"not written: {len(problems)} problem(s)")
    target = (out_dir / "assistant_recorded.json") if out_dir else OUT_JSON
    metamod.write_json(target, payload, metamod.meta(
        "ai/assistant/record.py", config.NO_MODEL if fake else config.MODEL_LABEL, inputs=[script_path],
        label=LABEL_FAKE if fake else LABEL))
    say(f"wrote {EV._rel(target)}: {len(out)} conversations, {sum(len(c['turns']) for c in out)} turns")
    return payload


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", default=None, help="comma-separated conversation ids")
    ap.add_argument("--fake", action="store_true", help="a fake model (needs --out)")
    ap.add_argument("--out", default=None, help="write into this folder instead of data/insights/")
    ap.add_argument("--skip-failed", action="store_true",
                    help="leave out a conversation with a problem (listed under left_out) instead of writing nothing")
    ap.add_argument("--resume", action="store_true", help="reuse conversations already recorded (live runs)")
    a = ap.parse_args(argv)
    record(only=[x.strip() for x in a.only.split(",")] if a.only else None, fake=a.fake, out_dir=a.out,
           skip_failed=a.skip_failed, resume=a.resume)
    return 0


if __name__ == "__main__":
    sys.exit(main())
