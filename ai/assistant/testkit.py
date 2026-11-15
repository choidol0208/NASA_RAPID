# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Helpers shared by the assistant's tests: model replies for FakeChat that are built from the prompt they get."""
import re

from ai.assistant import check as ck

LINE = re.compile(r"^\[(F\d+)\](?: \((.*?)\))? (.*)$")


def reading(intent="find_investigations", preset=None, o2=None, pv=None, pu=None, gravity=None, material=None,
            words=None, equipment=None, questions=(), investigations=(), verdict=False, prediction=False, term=None,
            compare=(), new_topic=True, english="A message.", keywords=(), pick=None):
    return {"intent": intent, "asks_verdict": verdict, "asks_prediction": prediction,
            "environment": {"preset": preset, "o2_pct": o2, "pressure_value": pv, "pressure_unit": pu,
                            "gravity": gravity, "flow": None},
            "compare_with": list(compare), "item": {"material": material, "words": words}, "equipment": equipment,
            "questions": list(questions), "investigations": list(investigations), "pick_from_last": pick,
            "term": term, "keywords": list(keywords), "new_topic": new_topic, "english": english}


def prompt_facts(messages):
    """[(id, context, text)] of the 'Facts:' lines of a write prompt."""
    out = []
    for line in messages[-1]["content"].splitlines() if messages[-1]["role"] == "user" else []:
        m = LINE.match(line)
        if m:
            out.append(m.groups())
    if not out:
        for msg in messages:
            if msg["role"] == "user":
                for line in msg["content"].splitlines():
                    m = LINE.match(line)
                    if m:
                        out.append(m.groups())
    return out


def _pseudo(fid, ctx, text):
    return {"id": fid, "context": ctx, "text": text, "numbers": [], "kind": "statement", "quote": False,
            "source_keys": [], "field": None}


def echo_writer(n=2, bad=None, request=None):
    """A WRITE reply that copies `n` fact texts that pass the gates; `bad` adds a failing sentence first."""
    def reply(messages, schema):
        sents = []
        if bad:
            ids = schema["properties"]["sentences"]["items"]["properties"]["facts"]["items"]["enum"]
            sents.append({"text": bad, "facts": [ids[0]]})
        for fid, ctx, text in prompt_facts(messages):
            if len(sents) >= n + (1 if bad else 0):
                break
            if not ck.gate_sentence(text, [_pseudo(fid, ctx, text)], request):
                sents.append({"text": text, "facts": [fid]})
        pids = schema["properties"]["panels"].get("items", {}).get("enum", [])
        return {"sentences": sents or [{"text": "The facts are listed.", "facts": ["F1"]}],
                "panels": pids[:1], "followups": ["Where are the raw data of these tests?",
                                                  "Which NASA documents state criteria for this question?"]}
    return reply


def checker(verdict="yes", no_for=()):
    def reply(messages, schema):
        k = schema["properties"]["verdicts"]["maxItems"]
        return {"verdicts": [{"n": i, "supported": "no" if i in no_for else verdict, "reason": "fake"}
                             for i in range(1, k + 1)]}
    return reply
