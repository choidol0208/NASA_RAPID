# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""The contract: every <!-- example:NAME --> block of ai/assistant/DESIGN.md validates against its
<!-- schema:NAME --> block and against the code's schema of the same name; every file in static/mock/ validates
against RESPONSE (HEALTH has no schema block and is checked for its keys). No network, no model.

    python3 -m unittest ai.assistant.test_contract -v
"""
import json
import re
import unittest
from pathlib import Path

from ai import llm
from ai.assistant import check as ck, contract, request as rq

HERE = Path(__file__).resolve().parent
DESIGN = (HERE / "DESIGN.md").read_text(encoding="utf-8")
BLOCK = re.compile(r"<!-- (schema|example):(\w+) -->\s*```json\n(.*?)```", re.S)
CODE = {"READING": rq.READING, "REQUEST": rq.REQUEST, "STATE": rq.STATE, "FACT": contract.FACT,
        "PANEL": contract.PANEL, "RESPONSE": contract.RESPONSE}


def blocks():
    out = {"schema": {}, "example": {}}
    for kind, name, body in BLOCK.findall(DESIGN):
        out[kind][name] = json.loads(body)
    return out


class ContractTest(unittest.TestCase):
    def test_examples_validate(self):
        b = blocks()
        self.assertTrue(b["example"])
        for name, ex in b["example"].items():
            if name in b["schema"]:
                self.assertEqual(llm.validate(ex, b["schema"][name]), [], f"{name} vs DESIGN schema")
            if name in CODE:
                self.assertEqual(llm.validate(ex, CODE[name]), [], f"{name} vs code schema")
            if name == "CHECK":
                self.assertEqual(llm.validate(ex, ck.check_schema(3)), [])
            if name == "HEALTH":
                for k in ("ok", "mode", "reason", "model", "ollama", "tools", "limits", "data_version", "commit"):
                    self.assertIn(k, ex)

    def test_code_schemas_match_design(self):
        b = blocks()
        for name, sch in CODE.items():
            self.assertEqual(sch, b["schema"][name], f"{name}: the code schema differs from DESIGN.md")

    def test_mock_files(self):
        mock = HERE / "static" / "mock"
        if not mock.exists():
            self.skipTest("static/mock/ not written yet (builder B)")
        for p in sorted(mock.glob("*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            if p.name == "health.json":
                self.assertIn("mode", d)
            elif p.name in ("examples.json", "eval.json"):
                continue
            elif p.name == "recorded.json":
                for c in d.get("conversations", []):
                    for t in c["turns"]:
                        self.assertEqual(llm.validate(t["response"], contract.RESPONSE), [], f"{p.name}")
            else:
                self.assertEqual(llm.validate(d, contract.RESPONSE), [], p.name)
        for p in sorted(mock.glob("*.ndjson")):
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    ev = json.loads(line)
                    if ev.get("event") == "result":
                        self.assertEqual(llm.validate(ev["response"], contract.RESPONSE), [], p.name)


if __name__ == "__main__":
    unittest.main()
