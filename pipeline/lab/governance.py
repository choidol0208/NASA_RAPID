# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""The 'governed_by' block of every lab output (branch data-lab, experiment).

Looks up decision points of pipeline/lab/model_map.json and returns, per
point, the governing model key, source title, URL and opened_by, or the
string "team rule, no established model found" (or the spec-time judgement
equivalent). No rule is decided here: the map holds the classes.
"""
import json
from pathlib import Path

MAP_PATH = Path(__file__).resolve().parent / "model_map.json"
_MAP = None


def _load():
    global _MAP
    if _MAP is None:
        with open(MAP_PATH, encoding="utf-8") as fh:
            _MAP = json.load(fh)
    return _MAP


def point(pid):
    m = _load()
    for p in m["decision_points"]:
        if p["id"] == pid:
            return p
    raise SystemExit("governance: decision point %s not in model_map.json" % pid)


def entry(pid):
    p = point(pid)
    models = _load()["_meta"]["models"]
    out = {"point": pid, "classification": p["classification"]}
    if p["classification"] == "established":
        k = p["governing_model"]
        mod = models[k]
        out["model_key"] = k
        if k == "ELEM":
            out["source_title"] = "elementary mathematics (the definition is the model)"
            out["url"] = None
            out["opened_by"] = None
        else:
            out["source_title"] = mod.get("source_title") or mod.get("name")
            out["url"] = mod.get("url")
            out["opened_by"] = mod.get("opened_by")
    else:
        out["model"] = p["model_name"]
        if p.get("candidate_model"):
            out["candidate_model_not_governing"] = p["candidate_model"]
    return out


def short(pid):
    """'M01a: OECD_HULL' or 'M01b: team rule' for a label next to a number."""
    p = point(pid)
    if p["classification"] == "established":
        return "%s: %s" % (pid, p["governing_model"])
    return "%s: %s" % (pid, "team rule" if p["classification"] == "team_rule" else "spec-time judgement")


def block(pids):
    return {"map": "pipeline/lab/model_map.json", "points": [entry(p) for p in pids]}


def md_lines(blk):
    """One markdown bullet per point of a governed_by block."""
    out = []
    for e in blk["points"]:
        if e["classification"] == "established":
            src = e["source_title"] + (" (%s; opened by %s)" % (e["url"], e["opened_by"]) if e.get("url") else "")
            out.append("- %s: %s, %s" % (e["point"], e["model_key"], src))
        else:
            out.append("- %s: %s" % (e["point"], e["model"]))
    return out
