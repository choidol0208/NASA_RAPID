# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""FakeChat: a stand-in for ai.llm.chat in tests (ai/assistant/DESIGN.md section 16). No network.

    chat = FakeChat({"understand_1": [reading], "write": ["invalid"], "check": [lambda messages, schema: {...}]})

Each reply is a dict (returned as `data`, checked against the schema like ai.llm.chat does), a callable
(messages, schema) -> dict, "invalid" (valid False) or "timeout" (raises ai.llm.LLMError). A step with no
reply left gives "invalid". `calls` records every call (step, messages, schema, options).
"""
from ai import llm


class FakeChat:
    def __init__(self, script=None):
        self.script = {k: list(v) for k, v in (script or {}).items()}
        self.calls = []

    def __call__(self, messages, schema, think=None, temperature=None, seed=None, num_ctx=None, num_predict=None, *,
                 model=None, format_mode=None, retries=None, run="calls", log_extra=None, timeout=None, log_dir=None):
        step = (log_extra or {}).get("step", "?")
        self.calls.append({"step": step, "messages": messages, "schema": schema,
                           "options": {"think": think, "temperature": temperature, "seed": seed, "num_ctx": num_ctx,
                                       "num_predict": num_predict, "retries": retries}})
        replies = self.script.get(step) or []
        reply = replies.pop(0) if replies else "invalid"
        if reply == "timeout":
            raise llm.LLMError("fake timeout")
        if callable(reply):
            reply = reply(messages, schema)
        base = {"model": "gpt-oss:20b", "digest": "f38aa0c53da5", "prompt_sha256": "fake", "options": {},
                "think": think, "format_mode": "schema", "eval_count": 0, "eval_duration_ns": 0,
                "prompt_eval_count": 0, "tokens_per_s": None, "wall_s": 0.0, "done_reason": "stop",
                "thinking_chars": 0, "retries": 0}
        if reply == "invalid" or not isinstance(reply, dict):
            return dict(base, data=None, valid=False, errors=["fake invalid reply"], raw="{}")
        errors = llm.validate(reply, schema)
        return dict(base, data=reply if not errors else None, valid=not errors, errors=errors, raw=str(reply))

    def steps(self):
        return [c["step"] for c in self.calls]
