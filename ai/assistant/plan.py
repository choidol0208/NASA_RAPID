# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Plan by table (ai/assistant/DESIGN.md section 5): code chooses the lookup tools; no model does.

plan(request) -> (steps, dropped), each step {"tool", "args", "why"}; at most MAX_TOOLS steps.
"""
MAX_TOOLS = 6

# needed fields per intent (DESIGN.md 4.6)
NEEDED_FIELDS = {
    "find_investigations": ("environment_or_item",),
    "compare_environments": ("environment",),
    "question_evidence": ("environment",),
    "where_data": ("environment",),
    "modelling_data": (),
    "equipment_research": ("equipment",),
    "earth_applications": (),
    "explain": ("term",),
    "help": (),
    "out_of_scope": (),
}


def _has_env(env):
    return bool(env.get("scenario_id") or env.get("cell"))


def _env_of_compare(c, vocab=None):
    return {"preset": c["preset"], "label": c["label"], "o2_pct": None, "pressure_kpa": None, "gravity": None,
            "flow": None, "scenario_id": c.get("scenario_id"), "cell": None}


def plan(req, vocab=None):
    """Ordered tool calls for a REQUEST. `vocab` (request.load_vocab()) fills the compared environments."""
    intent = req["intent"]
    env = req["environment"]
    qs = list(req.get("questions") or [])
    phase = req["item"].get("fuel_phase")
    has_o2p = env.get("o2_pct") is not None or env.get("pressure_kpa") is not None
    steps = []

    def add(tool, args, why):
        steps.append({"tool": tool, "args": args, "why": why})

    if intent in ("help", "out_of_scope"):
        return [], []
    if intent == "find_investigations":
        if req.get("dashboard_q"):
            add("rank_investigations", {"q": req["dashboard_q"]}, "find_investigations: the team's ranking")
        if _has_env(env):
            add("counts_per_question", {"env": env, "questions": qs}, "find_investigations: counts per question")
        if has_o2p:
            add("tested_range", {"env": env, "phase": phase}, "the environment has oxygen or pressure")
        if req.get("keywords"):
            add("search_records", {"keywords": req["keywords"], "limit": 3}, "the message has keywords")
    elif intent == "compare_environments":
        envs = [env] + [_compare_env(c, vocab) for c in req.get("compare_with") or []]
        for e in envs:
            if _has_env(e):
                add("counts_per_question", {"env": e, "questions": qs}, f"compare: counts for {e.get('label')}")
        for e in envs:
            if e.get("o2_pct") is not None or e.get("pressure_kpa") is not None:
                add("tested_range", {"env": e, "phase": phase}, f"compare: tested range for {e.get('label')}")
    elif intent == "question_evidence":
        item = req["item"].get("material")
        if item and req.get("dashboard_q"):
            # the counts are over all materials; the ranking is the tool that reads the user's material (added by
            # the team after the first live run: without it no fact named the material)
            add("rank_investigations", {"q": req["dashboard_q"]}, "question_evidence: the material named")
        add("counts_per_question", {"env": env, "questions": qs}, "question_evidence: counts")
        if item and has_o2p:
            add("tested_range", {"env": env, "phase": phase}, "question_evidence: the material's fuel phase")
        add("criteria", {"questions": qs}, "question_evidence: criteria")
        add("tests_table", {"env": env, "question": qs[0] if len(qs) == 1 else None},
            "question_evidence: tests in range")
    elif intent == "where_data":
        if _has_env(env):
            add("where_the_data_are", {"env": env, "questions": qs}, "where_data: the three piles")
            add("tests_table", {"env": env, "question": qs[0] if len(qs) == 1 else None}, "where_data: tests in range")
        for t in req.get("tests") or []:
            add("files_of_test", {"test_id": t}, "where_data: a test named")
    elif intent == "modelling_data":
        add("modelling_data", {"questions": qs, "investigations": req.get("investigations") or []},
            "modelling_data: readiness and variables")
        if has_o2p:
            add("tested_range", {"env": env, "phase": phase}, "the environment has oxygen or pressure")
    elif intent == "equipment_research":
        if req.get("equipment"):
            add("equipment_research", {"kind": req["equipment"]}, "equipment_research: the kind of equipment")
            from ai.assistant import texts
            add("criteria", {"questions": texts.EQUIPMENT[req["equipment"]]["questions"]},
                "equipment_research: criteria of its questions")
    elif intent == "earth_applications":
        add("earth_applications", {"investigations": req.get("investigations") or []}, "earth_applications")
    elif intent == "explain":
        if req.get("term"):
            add("explain", {"term": req["term"]}, "explain: the term")
    # added for every intent except help and out_of_scope
    for acc in (req.get("investigations") or [])[:2]:
        add("investigation_card", {"accession": acc}, "an investigation named or picked")
    if intent != "where_data":
        for t in (req.get("tests") or [])[:1]:
            add("files_of_test", {"test_id": t}, "a test named")
    if req.get("asks_prediction") and not any(s["tool"] == "tested_range" for s in steps):
        if has_o2p or _has_env(env):
            add("tested_range", {"env": env, "phase": phase}, "asks_prediction: where the values lie")
    dropped = steps[MAX_TOOLS:]
    return steps[:MAX_TOOLS], dropped


def _compare_env(c, vocab):
    e = _env_of_compare(c)
    if vocab and c["preset"] in vocab["presets"]:
        p = vocab["presets"][c["preset"]]
        e.update({"o2_pct": p.get("o2_pct"), "pressure_kpa": p.get("pressure_kpa"), "gravity": p.get("gravity"),
                  "flow": p.get("flow")})
        if not p["scenario"]:
            from ai.assistant.request import find_cell
            e["cell"] = find_cell(p.get("o2_pct"), p.get("pressure_kpa"), vocab)
    return e
