#!/usr/bin/env bash
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
#
# Start Fire Evidence Explorer with its assistant on this computer: http://127.0.0.1:8765/
#
#   ./run.sh               start Ollama if it is installed and not running, then the assistant server
#   ./run.sh --no-model    rule-based answers only (AI_NO_MODEL_CALLS=1); Ollama is not touched
#   ./run.sh --port N      another port (default 8765)
#   ./run.sh --build       rebuild web/dist first
#   ./run.sh --no-open     do not open a browser
#
# The server listens on 127.0.0.1 only. Stop it with Ctrl+C; an Ollama server that this script started
# is stopped with it. Conversations are not stored in the repository (logs go to ai/assistant/_runtime/).
set -euo pipefail
cd "$(dirname "$0")"

PORT="${ASSISTANT_PORT:-8765}"; NO_MODEL=0; BUILD=0; OPEN=1
while [ $# -gt 0 ]; do
  case "$1" in
    --port) PORT="${2:?--port needs a number}"; shift ;;
    --port=*) PORT="${1#--port=}" ;;
    --no-model) NO_MODEL=1 ;;
    --build) BUILD=1 ;;
    --no-open) OPEN=0 ;;
    -h|--help) sed -n '4,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1 (see ./run.sh --help)"; exit 2 ;;
  esac
  shift
done
case "$PORT" in ''|*[!0-9]*) echo "The port must be a number."; exit 2 ;; esac

if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "Python 3.10 or newer is needed. See ./install.sh."; exit 1
fi
if [ ! -f ai/assistant/server.py ]; then
  echo "ai/assistant/server.py is missing: this copy has no assistant server."; exit 1
fi

RUNTIME_DIR="ai/assistant/_runtime"
mkdir -p "$RUNTIME_DIR"
STARTED_OLLAMA=""
OLLAMA_URL=$(python3 -c "from ai import config; print(config.OLLAMA_URL.rstrip('/'))")
ollama_up() {
  python3 - "$OLLAMA_URL" <<'PY' >/dev/null 2>&1
import sys, urllib.request
urllib.request.urlopen(sys.argv[1] + "/api/version", timeout=2).read()
PY
}

if [ "$NO_MODEL" -eq 1 ]; then
  export AI_NO_MODEL_CALLS=1
  echo "Rule-based mode: no language model is called (AI_NO_MODEL_CALLS=1)."
elif command -v ollama >/dev/null 2>&1; then
  if ollama_up; then
    echo "Ollama answers at $OLLAMA_URL."
  else
    echo "Starting 'ollama serve' in the background (log: $RUNTIME_DIR/ollama.log)."
    nohup ollama serve >>"$RUNTIME_DIR/ollama.log" 2>&1 &
    STARTED_OLLAMA=$!
    for _ in $(seq 1 20); do ollama_up && break; sleep 1; done
    ollama_up || echo "Ollama did not answer within 20 s; the assistant will run rule-based (see $RUNTIME_DIR/ollama.log)."
  fi
else
  echo "Ollama is not installed, so the assistant runs rule-based. See ./install.sh to add the model."
fi

if [ "$BUILD" -eq 1 ] || [ ! -f web/dist/index.html ]; then
  echo "Building the page: python3 web/build.py"
  python3 web/build.py
fi

if python3 - "$PORT" <<'PY' 2>/dev/null
import socket, sys
s = socket.socket(); s.settimeout(1)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
PY
then
  echo "Port $PORT is already in use. Is the assistant already running? Try ./run.sh --port $((PORT + 1))."
  exit 1
fi

URL="http://127.0.0.1:${PORT}/"
echo "Fire Evidence Explorer with the assistant: $URL"
echo "Stop with Ctrl+C."

cleanup() {
  if [ -n "$STARTED_OLLAMA" ] && kill -0 "$STARTED_OLLAMA" 2>/dev/null; then
    echo "Stopping the Ollama server this script started."
    kill "$STARTED_OLLAMA" 2>/dev/null || true
  fi
}
trap cleanup EXIT
trap 'exit 130' INT TERM

if [ "$OPEN" -eq 1 ]; then
  (
    for _ in $(seq 1 30); do
      python3 - "$PORT" <<'PY' 2>/dev/null && break
import socket, sys
s = socket.socket(); s.settimeout(1)
sys.exit(0 if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0 else 1)
PY
      sleep 0.5
    done
    if command -v open >/dev/null 2>&1; then open "$URL"
    elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL" >/dev/null 2>&1
    else echo "Open $URL in a browser."; fi
  ) &
fi

python3 -m ai.assistant.server --port "$PORT"
