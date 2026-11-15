# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Terminal access to the assistant (ai/assistant/DESIGN.md section 11.7).

    python3 -m ai.assistant.cli health [--json]
    python3 -m ai.assistant.cli tools
    python3 -m ai.assistant.cli facts TOOL 'JSON_ARGS'
    python3 -m ai.assistant.cli ask "message" [--no-model] [--arm full] [--json]
    python3 -m ai.assistant.cli chat [--no-model]          # a conversation; the state is carried between turns
"""
import argparse
import json
import os
import sys
import textwrap

from ai.assistant import pipeline, request as rq, tools


def _print_response(r, show_facts=True):
    w = textwrap.TextWrapper(width=110, subsequent_indent="    ")
    print(f"[{r['kind']}; mode {r['mode']}; {r['trace']['model_calls']} model calls; "
          f"{r['trace']['total_ms'] / 1000:.1f} s; cache {r['trace']['cache']}]")
    req = r.get("request") or {}
    if req:
        env = req.get("environment") or {}
        print(f"Read as: {req.get('intent')} | environment: {env.get('label')} | item: {(req.get('item') or {}).get('label')}"
              f" | questions: {', '.join(req.get('questions') or []) or '-'} | equipment: {req.get('equipment') or '-'}")
        for a in req.get("assumptions") or []:
            print("  Assumed: " + a["text"])
    for n in r.get("notices") or []:
        print(w.fill("! " + n["text"]))
    if r.get("clarify"):
        print("One question before I look this up: " + r["clarify"]["question"])
        for i, o in enumerate(r["clarify"]["options"], 1):
            print(f"  {i}. {o['label']}")
    ans = r.get("answer") or {}
    cites = {}
    for s in ans.get("sentences") or []:
        marks = []
        for fid in s["facts"]:
            cites.setdefault(fid, len(cites) + 1)
            marks.append(f"[{cites[fid]}]")
        print(w.fill(f"- {s['text']} {''.join(marks)}"))
    if ans:
        print("  " + r["label"])
    for x in ans.get("removed") or []:
        print(w.fill(f"  removed by {x['by']}: {x['text']} ({x['reason']})"))
    if show_facts and cites:
        by = {f["id"]: f for f in r.get("facts") or []}
        print("Facts this answer rests on:")
        for fid, n in cites.items():
            f = by.get(fid)
            if f:
                src = f["source"]["file"] + (f":{f['source']['line']}" if f["source"]["line"] else "")
                print(w.fill(f"  [{n}] {('(' + f['context'] + ') ') if f.get('context') else ''}{f['text']} <{src}>"))
    if r.get("panels"):
        print("Panels: " + "; ".join(f"{p['title']} ({len(p['rows'])} rows)" for p in r["panels"]))
    if r.get("followups"):
        print("You could ask next: " + " | ".join(f["text"] for f in r["followups"]))
    print("Steps:")
    for s in r["trace"]["steps"]:
        print(f"  {s['label']}: {s['summary']} ({s['ms']} ms, {s['model_calls']} calls)")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fire Evidence Explorer assistant (terminal)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("health")
    h.add_argument("--json", action="store_true")
    sub.add_parser("tools")
    f = sub.add_parser("facts")
    f.add_argument("tool")
    f.add_argument("args", nargs="?", default="{}")
    a = sub.add_parser("ask")
    a.add_argument("message")
    a.add_argument("--no-model", action="store_true")
    a.add_argument("--arm", default="full", choices=pipeline.ARMS)
    a.add_argument("--json", action="store_true")
    c = sub.add_parser("chat")
    c.add_argument("--no-model", action="store_true")
    o = ap.parse_args(argv)

    if o.cmd == "health":
        from ai.assistant import server
        hv = server.health()
        if o.json:
            print(json.dumps(hv, indent=1))
        else:
            print(f"mode: {hv['mode']}" + (f" ({hv['reason']})" if hv["reason"] else ""))
            print(f"model: {hv['model']['name']} by {hv['model']['maker']} ({hv['model']['license']}); installed "
                  f"{hv['model']['installed']}; digest ok {hv['model']['digest_ok']}")
            print(f"ollama: reachable {hv['ollama']['reachable']}, version {hv['ollama']['version']}")
            print(f"data version {hv['data_version']}, commit {hv['commit'][:12]}")
        return 0
    if o.cmd == "tools":
        from ai.assistant import texts
        for name, (_, files) in tools.TOOLS.items():
            print(f"{name}: {texts.TOOL_LABELS[name]}\n    reads: {', '.join(files)}")
        return 0
    if o.cmd == "facts":
        if o.tool not in tools.TOOLS:
            print(f"unknown tool {o.tool}; see: python3 -m ai.assistant.cli tools", file=sys.stderr)
            return 2
        data = pipeline.get_data()
        out = tools.run([{"tool": o.tool, "args": json.loads(o.args), "why": "cli"}], data)
        print(json.dumps({"facts": out["facts"], "panels": [dict(p, rows=p["rows"][:5]) for p in out["panels"]],
                          "notes": out["notes"]}, indent=1, ensure_ascii=False))
        return 0
    if getattr(o, "no_model", False):
        os.environ["AI_NO_MODEL_CALLS"] = "1"
    if o.cmd == "ask":
        r = pipeline.turn(o.message, None, arm=o.arm)
        if o.json:
            print(json.dumps(r, indent=1, ensure_ascii=False))
        else:
            _print_response(r)
        return 0 if r["kind"] != "error" else 1
    # chat
    state = rq.empty_state()
    print("Fire Evidence Explorer assistant. Type a question; an empty line or Ctrl-D ends. "
          "A research exploration tool, not safety guidance.")
    while True:
        try:
            msg = input("\nyou> ").strip()
        except EOFError:
            break
        if not msg:
            break
        if state.get("pending_clarify") and msg.isdigit() and (state.get("request") or {}).get("clarify"):
            opts = state["request"]["clarify"]["options"]
            i = int(msg) - 1
            if 0 <= i < len(opts) and opts[i]["patch"]:
                r = pipeline.turn(None, state, state["request"], patch=opts[i]["patch"])
                _print_response(r)
                state = r["state"]
                continue
        r = pipeline.turn(msg, state)
        _print_response(r)
        state = r["state"]
    return 0


if __name__ == "__main__":
    sys.exit(main())
