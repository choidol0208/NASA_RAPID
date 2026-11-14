# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for the model guard (ai/llm.py), the validator and the disclosure helper (ai/meta.py).

    python3 -m unittest ai.test_llm -v

No test here talks to the model: every network call is replaced by a mock.
The real smoke calls are `python3 -m ai.llm --smoke`.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ai import config, llm, meta

MSGS = [{"role": "user", "content": "hello"}]
SCHEMA = {"type": "object", "required": ["a"], "additionalProperties": False,
          "properties": {"a": {"type": "string", "enum": ["x", "y"]}}}
BLOCKED = ["qwen2.5:7b", "gemma3:27b", "qwen2.5:3b", "qwen2.5:14b", "gpt-oss:120b", "GPT-OSS:20B",
           "gpt-oss:20b ", "gpt-oss", "gpt-oss:latest", "", None]


def _fake_http(content, thinking="", digest="f38aa0c53da5" + "0" * 52):
    calls = []

    def fake(method, path, payload=None, timeout=None):
        calls.append((method, path, payload))
        if path == "/api/tags":
            return {"models": [{"name": "gpt-oss:20b", "model": "gpt-oss:20b", "digest": digest}]}
        if path == "/api/chat":
            c = content.pop(0) if isinstance(content, list) else content
            return {"message": {"role": "assistant", "content": c, "thinking": thinking},
                    "eval_count": 100, "eval_duration": 2_000_000_000, "prompt_eval_count": 50,
                    "done_reason": "stop"}
        raise AssertionError(path)
    return fake, calls


class GuardTest(unittest.TestCase):
    def setUp(self):
        llm._DIGESTS.clear()

    def test_blocked_models_raise_before_any_network_call(self):
        with mock.patch("urllib.request.urlopen") as urlopen:
            urlopen.side_effect = AssertionError("network must not be reached")
            for m in BLOCKED:
                with self.subTest(model=m):
                    with self.assertRaises(llm.ModelNotAllowed):
                        llm.chat(MSGS, SCHEMA, model=m)
                    with self.assertRaises(llm.ModelNotAllowed):
                        llm.model_digest(m)
            self.assertEqual(urlopen.call_count, 0)

    def test_named_cases_from_the_design(self):
        with mock.patch("urllib.request.urlopen") as urlopen:
            with self.assertRaises(llm.ModelNotAllowed):
                llm.chat(MSGS, SCHEMA, model="qwen2.5:7b")
            with self.assertRaises(llm.ModelNotAllowed):
                llm.chat(MSGS, SCHEMA, model="gemma3:27b")
            urlopen.assert_not_called()

    def test_http_helper_refuses_a_blocked_model_in_any_payload(self):
        with mock.patch("urllib.request.urlopen") as urlopen:
            with self.assertRaises(llm.ModelNotAllowed):
                llm._http("POST", "/api/generate", {"model": "qwen2.5:14b", "prompt": "x"})
            urlopen.assert_not_called()

    def test_allowlist_is_exactly_gpt_oss_20b(self):
        self.assertEqual(config.ALLOWED, frozenset({"gpt-oss:20b"}))
        self.assertEqual(config.MODEL, "gpt-oss:20b")
        self.assertEqual(llm.check_model("gpt-oss:20b"), "gpt-oss:20b")

    def test_digest_mismatch_raises(self):
        fake, _ = _fake_http('{"a":"x"}', digest="abcdef123456" + "0" * 52)
        with mock.patch.object(llm, "_http", fake):
            with self.assertRaises(llm.DigestMismatch):
                llm.model_digest("gpt-oss:20b")


class ChatTest(unittest.TestCase):
    def setUp(self):
        llm._DIGESTS.clear()
        self.tmp = tempfile.TemporaryDirectory()
        self.runs = mock.patch.object(config, "RUNS_DIR", Path(self.tmp.name))
        self.runs.start()

    def tearDown(self):
        self.runs.stop()
        self.tmp.cleanup()

    def test_valid_reply_logged_without_thinking(self):
        fake, calls = _fake_http('{"a": "x"}', thinking="SECRET-THOUGHT-TEXT")
        with mock.patch.object(llm, "_http", fake):
            r = llm.chat(MSGS, SCHEMA, run="t1", temperature=0)
        self.assertTrue(r["valid"])
        self.assertEqual(r["data"], {"a": "x"})
        self.assertEqual(r["tokens_per_s"], 50.0)
        chat_payload = [c[2] for c in calls if c[1] == "/api/chat"][0]
        self.assertEqual(chat_payload["model"], "gpt-oss:20b")
        self.assertEqual(chat_payload["format"], SCHEMA)
        self.assertEqual(chat_payload["think"], "low")
        self.assertEqual(chat_payload["options"]["temperature"], 0)
        text = (Path(self.tmp.name) / "t1.jsonl").read_text()
        self.assertNotIn("SECRET-THOUGHT-TEXT", text)
        lines = [json.loads(x) for x in text.splitlines()]
        self.assertEqual(lines[0]["_meta"]["what"], "model candidates and call logs, not product content")
        self.assertTrue(lines[1]["digest"].startswith(config.EXPECT_DIGEST_PREFIX))
        self.assertEqual(lines[1]["options"]["temperature"], 0)
        self.assertNotIn("thinking", lines[1])

    def test_invalid_then_valid_retries_once(self):
        fake, calls = _fake_http(['not json', '{"a": "z"}', '{"a": "y"}'])
        with mock.patch.object(llm, "_http", fake):
            r = llm.chat(MSGS, SCHEMA, run="t2", retries=2)
        self.assertTrue(r["valid"])
        self.assertEqual(r["retries"], 2)
        self.assertEqual(r["data"], {"a": "y"})

    def test_invalid_after_retries_returns_invalid(self):
        fake, _ = _fake_http(['', '', ''])
        with mock.patch.object(llm, "_http", fake):
            r = llm.chat(MSGS, SCHEMA, run="t3", retries=1)
        self.assertFalse(r["valid"])
        self.assertIsNone(r["data"])

    def test_prompt_mode_sends_no_format(self):
        fake, calls = _fake_http('{"a": "x"}')
        with mock.patch.object(llm, "_http", fake):
            llm.chat(MSGS, SCHEMA, run="t4", format_mode="prompt")
        payload = [c[2] for c in calls if c[1] == "/api/chat"][0]
        self.assertNotIn("format", payload)
        self.assertIn("JSON schema", payload["messages"][0]["content"])

    def test_log_refuses_thinking(self):
        with self.assertRaises(ValueError):
            llm.log_line("t5", {"thinking": "x"})


class ValidatorTest(unittest.TestCase):
    def test_cases(self):
        s = {"type": "object", "required": ["ids"], "additionalProperties": False,
             "properties": {"ids": {"type": "array", "maxItems": 2, "items": {"type": "string", "enum": ["A", "B"]}},
                            "n": {"type": "integer", "minimum": 0}}}
        self.assertEqual(llm.validate({"ids": ["A"]}, s), [])
        self.assertTrue(llm.validate({}, s))
        self.assertTrue(llm.validate({"ids": ["C"]}, s))
        self.assertTrue(llm.validate({"ids": ["A", "B", "A"]}, s))
        self.assertTrue(llm.validate({"ids": [], "x": 1}, s))
        self.assertTrue(llm.validate({"ids": [], "n": True}, s))
        self.assertTrue(llm.validate({"ids": [], "n": -1}, s))
        self.assertTrue(llm.validate([], s))

    def test_parse_json(self):
        self.assertEqual(llm.parse_json('```json\n{"a": 1}\n```'), {"a": 1})
        self.assertEqual(llm.parse_json('Here: {"a": 1} done'), {"a": 1})
        with self.assertRaises(ValueError):
            llm.parse_json("   ")


class MetaTest(unittest.TestCase):
    def test_block_fields(self):
        b = meta.meta("ai/x.py", config.NO_MODEL, [config.PSI_MANIFEST])
        for k in ("built_by", "code_written_with", "language_model_used_at_build", "generated_at",
                  "inputs_sha256", "label"):
            self.assertIn(k, b)
        self.assertEqual(b["code_written_with"], "AI assistant (Claude Code)")
        self.assertIn("data/psi/manifest.json", b["inputs_sha256"])
        self.assertEqual(meta.meta("ai/x.py", config.MODEL_LABEL)["language_model_used_at_build"],
                         "gpt-oss:20b (f38aa0c53da5)")
        with self.assertRaises(ValueError):
            meta.meta("ai/x.py", "qwen2.5:7b")
        with self.assertRaises(ValueError):
            meta.meta("scripts/x.py")

    def test_write_object_array_and_idempotence(self):
        with tempfile.TemporaryDirectory() as d:
            obj, arr = Path(d) / "a.json", Path(d) / "b.json"
            meta.write_json(obj, {"x": 1}, meta.meta("ai/a.py"))
            meta.write_json(arr, [1, 2], meta.meta("ai/b.py"))
            self.assertIn("_meta", json.loads(obj.read_text()))
            self.assertEqual(json.loads(arr.read_text()), [1, 2])
            comp = json.loads((Path(d) / "_meta.json").read_text())
            self.assertEqual(set(comp), {"_meta", "a.json", "b.json"})
            self.assertEqual(comp["b.json"]["built_by"], "ai/b.py")
            before = obj.read_bytes(), (Path(d) / "_meta.json").read_bytes()
            meta.write_json(obj, {"x": 1}, meta.meta("ai/a.py"))
            self.assertEqual(before, (obj.read_bytes(), (Path(d) / "_meta.json").read_bytes()))


class HeaderTest(unittest.TestCase):
    def test_every_ai_python_file_has_the_header(self):
        for p in sorted(config.AI_DIR.rglob("*.py")):
            with self.subTest(file=p.name):
                self.assertEqual(p.read_text(encoding="utf-8").splitlines()[0], config.HEADER_COMMENT)


if __name__ == "__main__":
    unittest.main()
