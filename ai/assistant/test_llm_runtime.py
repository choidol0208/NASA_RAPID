# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for the run-time additions to ai/llm.py and ai/config.py (log_dir, server_status). No model call.

    python3 -m unittest ai.assistant.test_llm_runtime -v
"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ai import config, llm


class RuntimeTest(unittest.TestCase):
    def test_log_dir(self):
        with tempfile.TemporaryDirectory() as d:
            llm.log_line("assistant_test", {"kind": "x"}, log_dir=d)
            p = Path(d) / "assistant_test.jsonl"
            lines = [json.loads(x) for x in p.read_text().splitlines()]
            self.assertIn("_meta", lines[0])
            self.assertEqual(lines[1], {"kind": "x"})
        self.assertEqual(llm.run_log_path("smoke"), config.RUNS_DIR / "smoke.jsonl")
        self.assertEqual(llm.run_log_path("a", log_dir="/tmp/x"), Path("/tmp/x/a.jsonl"))

    def test_server_status_without_calls(self):
        with mock.patch.dict(os.environ, {llm.NO_CALLS_ENV: "1"}), \
                mock.patch.object(llm, "_http", side_effect=AssertionError("no connection")):
            st = llm.server_status()
        self.assertEqual((st["reachable"], st["reason"]), (False, "AI_NO_MODEL_CALLS=1"))

    def test_server_status_blocked_model(self):
        st = llm.server_status("qwen2.5:3b")
        self.assertFalse(st["allowed"])

    def test_server_status_digest(self):
        def fake(method, path, payload=None, timeout=None):
            if path == "/api/version":
                return {"version": "0.40.16"}
            return {"models": [{"name": "gpt-oss:20b", "digest": "0" * 64}]}
        with mock.patch.dict(os.environ, {llm.NO_CALLS_ENV: "0"}), mock.patch.object(llm, "_http", side_effect=fake):
            st = llm.server_status()
        self.assertTrue(st["reachable"] and st["installed"])
        self.assertFalse(st["digest_ok"])
        self.assertIn("another digest", st["reason"])

    def test_unreachable(self):
        with mock.patch.dict(os.environ, {llm.NO_CALLS_ENV: "0"}), \
                mock.patch.object(llm, "_http", side_effect=llm.LLMError("down")):
            st = llm.server_status()
        self.assertEqual(st["reason"], f"Ollama is not reachable at {config.OLLAMA_URL}")

    def test_runtime_dir_is_ignored(self):
        gi = (config.ROOT / ".gitignore").read_text()
        if "ai/assistant/_runtime/" not in gi:
            self.skipTest(".gitignore line not added yet (builder C)")
        self.assertEqual(config.ASSISTANT_RUNTIME_DIR, config.ROOT / "ai" / "assistant" / "_runtime")


if __name__ == "__main__":
    unittest.main()
