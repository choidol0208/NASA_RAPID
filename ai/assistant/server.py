# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""The assistant's local HTTP server (ai/assistant/DESIGN.md section 11). Standard library only.

    python3 -m ai.assistant.server [--port 8765]

- Serves web/dist/ and adds the assistant's two static files to index.html as it serves it (web/ is not
  changed); serves ai/assistant/static/ under /assistant/ and the recorded and evaluation files.
- GET /api/health, GET /api/examples, POST /api/understand, POST /api/answer[?stream=1].
- Bound to 127.0.0.1 only; a Host header other than 127.0.0.1:<port> or localhost:<port> gets 403.
- One lock around turns that use the model (Ollama serves one request at a time).
- Logs one line per request to stderr (method, path, status, ms); never the message text.
"""
import argparse
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ai import config, llm  # noqa: E402
from ai.assistant import pipeline, request as rq, tools  # noqa: E402

ROOT = config.ROOT
DIST = ROOT / "web" / "dist"
STATIC = ROOT / "ai" / "assistant" / "static"
MAX_BODY = 16384
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".json": "application/json; charset=utf-8", ".csv": "text/csv; charset=utf-8", ".png": "image/png",
         ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".svg": "image/svg+xml",
         ".webp": "image/webp", ".mp4": "video/mp4", ".webm": "video/webm", ".ndjson": "application/x-ndjson",
         ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8", ".woff2": "font/woff2", ".mjs": "text/javascript"}
NOT_BUILT = "The page is not built. Run python3 web/build.py, then reload."
MODEL_LOCK = threading.Lock()


def health():
    st = pipeline.model_status(force=True)
    mode, reason = pipeline.decide_mode()
    data = pipeline.get_data()
    return {"ok": True, "mode": mode, "reason": reason,
            "model": {"name": config.MODEL, "maker": config.MODEL_MAKER, "license": config.MODEL_LICENSE,
                      "allowed": st["allowed"], "installed": st["installed"], "digest_ok": st["digest_ok"],
                      "digest_prefix": st["digest_prefix"] or config.EXPECT_DIGEST_PREFIX},
            "ollama": {"reachable": st["reachable"], "version": st["version"], "url": config.OLLAMA_URL},
            "tools": list(tools.TOOLS),
            "limits": {"max_model_calls_per_turn": config.ASSISTANT["max_model_calls"],
                       "max_message_chars": config.ASSISTANT["message_max_chars"]},
            "data_version": data.version, "commit": data.commit}


def examples():
    p = ROOT / "ai" / "assistant" / "eval" / "questions.json"
    out = []
    if p.exists():
        try:
            qs = json.loads(p.read_text(encoding="utf-8")).get("questions") or []
        except (OSError, ValueError):
            qs = []
        for q in qs:
            if q.get("example"):
                out.append({"label": q.get("label") or q["message"][:60], "message": q["message"],
                            "request": q.get("request"), "answer_mode": q.get("answer_mode")})
    return {"examples": out}


def inject(html):
    if "assistant/assistant.js" in html:
        return html
    link = '<link rel="stylesheet" href="assistant/assistant.css">'
    script = '<script src="assistant/assistant.js" defer></script>'
    html = html.replace("</head>", link + "\n</head>", 1) if "</head>" in html else link + html
    html = html.replace("</body>", script + "\n</body>", 1) if "</body>" in html else html + script
    return html


def _state_ok(state):
    if state is None:
        return None
    blob = json.dumps(state, ensure_ascii=False).encode("utf-8")
    if len(blob) > config.ASSISTANT["state_max_bytes"]:
        return "too_large"
    errs = llm.validate(state, rq.STATE)
    return "; ".join(errs[:3]) if errs else None


class Handler(BaseHTTPRequestHandler):
    server_version = "FireEvidenceAssistant/1"
    protocol_version = "HTTP/1.0"

    def log_message(self, fmt, *args):  # the default log prints the request line; ours never holds the message
        pass

    def _log(self, status):
        ms = int((time.monotonic() - self._t0) * 1000)
        sys.stderr.write(f"{self.command} {urlsplit(self.path).path} {status} {ms}ms\n")

    def _host_ok(self):
        port = self.server.server_address[1]
        return self.headers.get("Host", "") in (f"127.0.0.1:{port}", f"localhost:{port}")

    def _send(self, status, body, ctype="application/json; charset=utf-8", api=False):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        if api:
            self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass  # the client left before the reply (added after the red-team run of 15 Nov)
        self._log(status)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        self._t0 = time.monotonic()
        if not self._host_ok():
            return self._send(403, {"error": "forbidden host"})
        path = urlsplit(self.path).path
        if path == "/api/health":
            return self._send(200, health(), api=True)
        if path == "/api/examples":
            return self._send(200, examples(), api=True)
        if path.startswith("/api/"):
            return self._send(404, {"error": "not found"}, api=True)
        if path in ("/", "/index.html"):
            idx = DIST / "index.html"
            if not idx.exists():
                return self._send(200, NOT_BUILT, "text/plain; charset=utf-8")
            return self._send(200, inject(idx.read_text(encoding="utf-8")), TYPES[".html"])
        if path == "/assistant/recorded.json":
            return self._file(ROOT / "data" / "insights" / "assistant_recorded.json", ROOT / "data" / "insights")
        if path == "/assistant/eval.json":
            return self._file(ROOT / "data" / "insights" / "assistant_eval.json", ROOT / "data" / "insights")
        if path.startswith("/assistant/"):
            return self._file(STATIC / path[len("/assistant/"):], STATIC)
        return self._file(DIST / path.lstrip("/"), DIST)

    def _file(self, p, base):
        try:
            rp = Path(os.path.realpath(p))
            if not str(rp).startswith(str(Path(os.path.realpath(base))) + os.sep) or not rp.is_file():
                return self._send(404, {"error": "not found"})
            return self._send(200, rp.read_bytes(), TYPES.get(rp.suffix.lower(), "application/octet-stream"))
        except OSError:
            return self._send(404, {"error": "not found"})

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            return None, 413
        try:
            raw = self.rfile.read(n) if n else b""
            body = json.loads(raw.decode("utf-8") or "{}")
        except (ValueError, UnicodeDecodeError):
            return None, 400
        return (body, 200) if isinstance(body, dict) else (None, 400)

    def do_POST(self):
        self._t0 = time.monotonic()
        if not self._host_ok():
            return self._send(403, {"error": "forbidden host"})
        url = urlsplit(self.path)
        if url.path not in ("/api/answer", "/api/understand"):
            return self._send(404, {"error": "not found"}, api=True)
        body, code = self._body()
        if code == 413:
            return self._send(413, {"error": "body too large"}, api=True)
        if body is None:
            return self._send(400, {"error": "bad JSON body"}, api=True)
        msg, req, state = body.get("message"), body.get("request"), body.get("state")
        st_err = _state_ok(state)
        if st_err == "too_large":
            return self._send(413, {"error": "state too large"}, api=True)
        if st_err:
            return self._send(400, {"error": f"bad state: {st_err}"}, api=True)
        if (msg is None) == (req is None):
            return self._send(400, {"error": "give exactly one of message and request"}, api=True)
        if msg is not None and (not isinstance(msg, str) or not msg.strip()
                                or len(msg) > config.ASSISTANT["message_max_chars"]):
            return self._send(400, {"error": "message must be text of 1 to 1000 characters"}, api=True)
        if req is not None:
            errs = llm.validate(req, rq.REQUEST)
            if errs:
                return self._send(400, {"error": f"bad request: {'; '.join(errs[:3])}"}, api=True)
        if url.path == "/api/understand":
            return self._understand(msg, state)
        stream = parse_qs(url.query).get("stream") == ["1"]
        kw = {"answer_mode": body.get("answer_mode") if body.get("answer_mode") == "template" else None,
              "patch": body.get("patch") if isinstance(body.get("patch"), dict) else None}
        if stream:
            return self._stream(msg, req, state, kw)
        with MODEL_LOCK:
            resp = pipeline.turn(msg, state, req, **kw)
        if resp["kind"] == "error":
            return self._send(500, {"error": "Something went wrong on the assistant server.", "trace": resp["trace"]},
                              api=True)
        return self._send(200, resp, api=True)

    def _understand(self, msg, state):
        if msg is None:
            return self._send(400, {"error": "understand needs a message"}, api=True)
        data = pipeline.get_data()
        mode, _ = pipeline.decide_mode()
        tr = pipeline.Turn(llm.chat, mode, "full", None, f"assistant_{time.strftime('%Y%m%d')}",
                           config.ASSISTANT_RUNTIME_DIR)
        with MODEL_LOCK:
            tr.start("understand")
            req, detail, summary = pipeline._understand(tr, msg, state, data.vocab)
            tr.done("understand", summary, detail)
        st = rq.next_state(state, req)
        return self._send(200, {"request": req, "state": st, "trace": {"steps": tr.steps, "model_calls": tr.budget.used,
                                "total_ms": int((time.monotonic() - tr.t0) * 1000)}}, api=True)

    def _stream(self, msg, req, state, kw):
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        def emit(ev):
            if ev.get("event") == "result":
                return
            try:
                self.wfile.write((json.dumps(ev, ensure_ascii=False) + "\n").encode("utf-8"))
                self.wfile.flush()
            except OSError:
                pass
        with MODEL_LOCK:
            resp = pipeline.turn(msg, state, req, on_event=emit, **kw)
        last = {"event": "result", "response": resp} if resp["kind"] != "error" else \
            {"event": "error", "message": "Something went wrong on the assistant server."}
        try:
            self.wfile.write((json.dumps(last, ensure_ascii=False) + "\n").encode("utf-8"))
            self.wfile.flush()
        except OSError:
            pass
        self._log(200)


def make_server(port=None):
    port = int(port if port is not None else os.environ.get("ASSISTANT_PORT") or config.ASSISTANT["port"])
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fire Evidence Explorer with the assistant (local server)")
    ap.add_argument("--port", type=int, default=None)
    a = ap.parse_args(argv)
    srv = make_server(a.port)
    pipeline.get_data()
    h = health()
    print(f"Fire Evidence Explorer with the assistant: http://127.0.0.1:{srv.server_address[1]}/", flush=True)
    print(f"assistant mode: {h['mode']}" + (f" ({h['reason']})" if h["reason"] else ""), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
