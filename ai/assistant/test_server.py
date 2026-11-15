# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for the local HTTP server (ai/assistant/server.py), in no-model mode on a free port. No model call.

    python3 -m unittest ai.assistant.test_server -v
"""
import http.client
import json
import os
import threading
import unittest
from unittest import mock

from ai import llm
from ai.assistant import contract, server


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = mock.patch.dict(os.environ, {llm.NO_CALLS_ENV: "1"})
        cls.env.start()
        cls.srv = server.make_server(0)
        cls.port = cls.srv.server_address[1]
        cls.th = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.th.start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.env.stop()

    def req(self, method, path, body=None, host=None, raw=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        headers = {"Host": host or f"127.0.0.1:{self.port}", "Content-Type": "application/json"}
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        c.request(method, path, body=data, headers=headers)
        r = c.getresponse()
        out = (r.status, r.getheader("Content-Type"), r.read())
        c.close()
        return out

    def test_health_no_model(self):
        st, ct, body = self.req("GET", "/api/health")
        self.assertEqual(st, 200)
        h = json.loads(body)
        self.assertEqual((h["mode"], h["reason"]), ("no_model", "AI_NO_MODEL_CALLS=1"))
        self.assertEqual(h["model"]["name"], "gpt-oss:20b")
        self.assertIn("counts_per_question", h["tools"])

    def test_answer_json(self):
        st, ct, body = self.req("POST", "/api/answer", {"message": "cotton in a lunar habitat", "state": None})
        self.assertEqual(st, 200)
        r = json.loads(body)
        self.assertEqual(contract.validate_response(r), [])
        self.assertEqual(r["mode"], "no_model")
        # the next turn with the returned state
        st, ct, body = self.req("POST", "/api/answer", {"message": "and for the ISS?", "state": r["state"]})
        self.assertEqual(json.loads(body)["request"]["environment"]["preset"], "iss")

    def test_answer_stream(self):
        st, ct, body = self.req("POST", "/api/answer?stream=1", {"message": "smoke detection on the ISS"})
        self.assertEqual(st, 200)
        self.assertEqual(ct, "application/x-ndjson")
        lines = [json.loads(x) for x in body.decode().splitlines() if x.strip()]
        self.assertEqual(lines[0]["event"], "step")
        self.assertEqual(lines[-1]["event"], "result")
        self.assertEqual(contract.validate_response(lines[-1]["response"]), [])

    def test_request_and_patch(self):
        st, ct, body = self.req("POST", "/api/answer", {"message": "Which recorded tests are relevant to my design?"})
        r = json.loads(body)
        self.assertEqual(r["kind"], "clarify")
        st, ct, body = self.req("POST", "/api/answer", {"request": r["request"], "state": r["state"],
                                                        "patch": r["clarify"]["options"][0]["patch"]})
        self.assertEqual(json.loads(body)["kind"], "answer")

    def test_understand(self):
        st, ct, body = self.req("POST", "/api/understand", {"message": "cotton in a lunar habitat"})
        self.assertEqual(st, 200)
        self.assertEqual(json.loads(body)["request"]["environment"]["preset"], "lunar_habitat")

    def test_bad_bodies(self):
        self.assertEqual(self.req("POST", "/api/answer", raw=b"not json")[0], 400)
        self.assertEqual(self.req("POST", "/api/answer", {"message": "a", "request": {}})[0], 400)
        self.assertEqual(self.req("POST", "/api/answer", raw=b"{" + b" " * 20000 + b"}")[0], 413)
        big = {"version": "1", "turn": 1, "request": None, "pending_clarify": None, "last_list": [], "last_tests": [],
               }
        big["request"] = {"x": "y" * 9000}
        self.assertEqual(self.req("POST", "/api/answer", {"message": "hi", "state": big})[0], 413)

    def test_foreign_host(self):
        self.assertEqual(self.req("GET", "/api/health", host="evil.example:80")[0], 403)
        self.assertEqual(self.req("POST", "/api/answer", {"message": "hi"}, host=f"evil.example:{self.port}")[0], 403)

    def test_path_traversal(self):
        self.assertEqual(self.req("GET", "/../../AGENTS.md")[0], 404)
        self.assertEqual(self.req("GET", "/assistant/../../config.py")[0], 404)
        self.assertEqual(self.req("GET", "/%2e%2e/%2e%2e/AGENTS.md")[0], 404)

    def test_index_injection(self):
        st, ct, body = self.req("GET", "/")
        self.assertEqual(st, 200)
        text = body.decode()
        if (server.DIST / "index.html").exists():
            self.assertIn('<script src="assistant/assistant.js" defer></script>', text)
            self.assertIn('<link rel="stylesheet" href="assistant/assistant.css">', text)
        else:
            self.assertEqual(text, server.NOT_BUILT)
        self.assertEqual(server.inject("<html><head></head><body></body></html>").count("assistant.js"), 1)
        once = server.inject("<head></head><body></body>")
        self.assertEqual(server.inject(once), once)


if __name__ == "__main__":
    unittest.main()
