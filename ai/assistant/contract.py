# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""The response-side schemas of ai/assistant/DESIGN.md (FACT 6.1, PANEL 6.2, RESPONSE 10.2), in the subset
ai.llm.validate supports. READING, REQUEST and STATE are in ai/assistant/request.py; WRITE and CHECK are built
per turn in write.py and check.py.
"""
FACT = {
    "type": "object", "additionalProperties": False,
    "required": ["id", "ref", "tool", "kind", "context", "text", "numbers", "source", "source_keys", "link", "quote",
                 "field", "investigation_ids", "lead", "limit"],
    "properties": {
        "id": {"type": "string", "minLength": 2, "maxLength": 4},
        "ref": {"type": "string", "maxLength": 200},
        "tool": {"type": "string"},
        "kind": {"type": "string", "enum": ["ranking", "count", "statement", "range", "pile", "test_row", "readiness",
                                            "nasa_sentence", "criterion", "file_group", "video", "card", "definition",
                                            "limit", "published_result"]},  # published_result: added 15 November
        "context": {"type": ["string", "null"], "maxLength": 160},
        "text": {"type": "string", "minLength": 1, "maxLength": 900},
        "numbers": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                               "required": ["value", "unit", "what"],
                                               "properties": {"value": {"type": "number"}, "unit": {"type": ["string", "null"]},
                                                              "what": {"type": "string"}}}},
        "source": {"type": "object", "additionalProperties": False, "required": ["file", "line", "key"],
                   "properties": {"file": {"type": "string"}, "line": {"type": ["integer", "null"]},
                                  "key": {"type": ["string", "null"]}}},
        "source_keys": {"type": "array", "items": {"type": "string"}},
        "link": {"type": ["string", "null"]},
        "quote": {"type": "boolean"},
        "field": {"type": ["string", "null"]},
        "investigation_ids": {"type": "array", "items": {"type": "string"}},
        "lead": {"type": "boolean"},
        "limit": {"type": "boolean"},
    },
}

PANEL = {
    "type": "object", "additionalProperties": False,
    "required": ["id", "type", "title", "note", "columns", "rows", "download", "dashboard_section", "fact_ids"],
    "properties": {
        "id": {"type": "string"},
        "type": {"type": "string", "enum": ["ranking", "counts", "compare", "range", "piles", "table", "readiness",
                                            "criteria", "quotes", "files", "card", "definition"]},
        "title": {"type": "string", "maxLength": 120},
        "note": {"type": ["string", "null"]},
        "columns": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["key", "label"],
                                               "properties": {"key": {"type": "string"}, "label": {"type": "string"},
                                                              "kind": {"type": "string",
                                                                       "enum": ["text", "number", "link", "list"]}}}},
        "rows": {"type": "array", "maxItems": 500, "items": {"type": "object"}},
        "download": {"type": ["object", "null"], "additionalProperties": False, "required": ["filename", "total_rows"],
                     "properties": {"filename": {"type": "string"}, "total_rows": {"type": "integer"}}},
        "dashboard_section": {"type": ["string", "null"], "enum": ["#top", "#needs", "#tests", "#answers", "#piles",
                                                                   "#shown", "#criteria", "#stops", "#all", "#ai-use",
                                                                   None]},
        "fact_ids": {"type": "array", "items": {"type": "string"}},
    },
}

RESPONSE = {
    "type": "object", "additionalProperties": False,
    "required": ["version", "turn_id", "kind", "mode", "request", "state", "notices", "answer", "facts", "panels",
                 "followups", "clarify", "dashboard", "trace", "label"],
    "properties": {
        "version": {"const": "1"},
        "turn_id": {"type": "string"},
        "kind": {"type": "string", "enum": ["answer", "clarify", "out_of_scope", "help", "error"]},
        "mode": {"type": "string", "enum": ["live", "no_model", "recorded", "mock"]},
        "request": {"type": ["object", "null"]},
        "state": {"type": "object"},
        "notices": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["id", "text"],
                                               "properties": {"id": {"type": "string"}, "text": {"type": "string"}}}},
        "answer": {"type": ["object", "null"], "additionalProperties": False, "required": ["origin", "sentences", "removed"],
                   "properties": {
                       "origin": {"type": "string", "enum": ["model", "template"]},
                       "sentences": {"type": "array", "items": {
                           "type": "object", "additionalProperties": False,
                           "required": ["n", "text", "facts", "origin", "status"],
                           "properties": {"n": {"type": "integer"}, "text": {"type": "string"},
                                          "facts": {"type": "array", "items": {"type": "string"}},
                                          "origin": {"type": "string", "enum": ["model", "template"]},
                                          "status": {"type": "string", "enum": ["kept", "repaired"]}}}},
                       "removed": {"type": "array", "items": {
                           "type": "object", "additionalProperties": False, "required": ["text", "by", "reason"],
                           "properties": {"text": {"type": "string"}, "by": {"type": "string"},
                                          "reason": {"type": "string"}}}}}},
        "facts": {"type": "array", "items": {"type": "object"}},
        "panels": {"type": "array", "items": {"type": "object"}},
        "followups": {"type": "array", "maxItems": 3, "items": {
            "type": "object", "additionalProperties": False, "required": ["text", "request"],
            "properties": {"text": {"type": "string"}, "request": {"type": ["object", "null"]}}}},
        "clarify": {"type": ["object", "null"]},
        "dashboard": {"type": "object", "additionalProperties": False, "required": ["q", "section"],
                      "properties": {"q": {"type": "string"}, "section": {"type": ["string", "null"]}}},
        "trace": {"type": "object", "additionalProperties": False,
                  "required": ["steps", "model_calls", "total_ms", "cache", "gate_report", "data_version", "commit"],
                  "properties": {
                      "steps": {"type": "array", "items": {
                          "type": "object", "additionalProperties": False,
                          "required": ["step", "label", "summary", "ms", "model_calls"],
                          "properties": {"step": {"type": "string", "enum": ["understand", "plan", "lookup", "write",
                                                                             "check", "deliver"]},
                                         "label": {"type": "string"}, "summary": {"type": "string"},
                                         "ms": {"type": "integer"}, "model_calls": {"type": "integer"},
                                         "detail": {"type": "object"}}}},
                      "model_calls": {"type": "integer", "minimum": 0, "maximum": 4},
                      "total_ms": {"type": "integer"},
                      "cache": {"type": "string", "enum": ["hit", "miss", "none"]},
                      "gate_report": {"type": ["object", "null"]},
                      "data_version": {"type": "string"},
                      "commit": {"type": "string"}}},
        "label": {"type": "string"},
    },
}


def validate_response(resp):
    """Errors of a RESPONSE, its facts, panels, request and state (ai.llm.validate subset)."""
    from ai import llm
    from ai.assistant import request as rq
    errs = llm.validate(resp, RESPONSE)
    for i, f in enumerate(resp.get("facts") or []):
        errs += llm.validate(f, FACT, f"$.facts[{i}]")
    for i, p in enumerate(resp.get("panels") or []):
        errs += llm.validate(p, PANEL, f"$.panels[{i}]")
    if resp.get("request") is not None:
        errs += llm.validate(resp["request"], rq.REQUEST, "$.request")
    if resp.get("state"):
        errs += llm.validate(resp["state"], rq.STATE, "$.state")
        if resp["state"].get("request"):
            errs += llm.validate(resp["state"]["request"], rq.REQUEST, "$.state.request")
    return errs
