#!/usr/bin/env bash
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
#
# Install Fire Evidence Explorer with its local assistant (macOS and Linux).
#
#   ./install.sh                  check, install Ollama if it is missing, download the model, build, self-test
#                                 (it says what it is about to install or download and asks; Enter means yes)
#   ./install.sh --check          only report what is present and what would be done; downloads nothing
#   ./install.sh --yes            do not ask before downloading the model
#   ./install.sh --install-ollama do not ask before installing Ollama by its official method
#                                 (Homebrew on macOS, https://ollama.com/install.sh on Linux)
#   ./install.sh --no-model       skip Ollama and the model; the assistant then runs rule-based
#
# The only language model it ever downloads is the one named in ai/config.py (OpenAI gpt-oss:20b,
# Apache-2.0). It never deletes anything, never edits ai/config.py and sends nothing off this machine
# except the requests of Ollama's own installer and model download.
set -euo pipefail
cd "$(dirname "$0")"

CHECK=0; YES=0; INSTALL_OLLAMA=0; NO_MODEL=0
for arg in "$@"; do
  case "$arg" in
    --check) CHECK=1 ;;
    --yes|-y) YES=1 ;;
    --install-ollama) INSTALL_OLLAMA=1 ;;
    --no-model) NO_MODEL=1 ;;
    -h|--help) sed -n '4,16p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $arg (see ./install.sh --help)"; exit 2 ;;
  esac
done

RUNTIME_DIR="ai/assistant/_runtime"
PROBLEMS=0
say()  { printf '%s\n' "$*"; }
step() { printf '\n[%s] %s\n' "$1" "$2"; }
would(){ say "  --check: would $*"; }

# ---------------------------------------------------------------- 1. Python
step 1 "Python 3.10 or newer"
if ! command -v python3 >/dev/null 2>&1; then
  say "  Python 3.10 or newer is needed (python3 was not found). Install it from https://www.python.org/downloads/ and run ./install.sh again."
  exit 1
fi
PYV=$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  say "  Python 3.10 or newer is needed; python3 is $PYV."
  exit 1
fi
say "  python3 $PYV: ok (standard library only; nothing is installed with pip)"

# Values read from the code, so this script never names a model of its own.
MODEL=$(python3 -c "from ai import config; print(config.MODEL)")
PREFIX=$(python3 -c "from ai import config; print(config.EXPECT_DIGEST_PREFIX)")
MAKER=$(python3 -c "from ai import config; print(config.MODEL_MAKER)")
LICENSE=$(python3 -c "from ai import config; print(config.MODEL_LICENSE)")
OLLAMA_URL=$(python3 -c "from ai import config; print(config.OLLAMA_URL.rstrip('/'))")
MODEL_SIZE_TEXT="about 13 GB"   # size shown by 'ollama list' for this model on the build machine, 15 Nov 2026

# ---------------------------------------------------------------- 2. memory and disk
step 2 "Memory and disk"
MEM_BYTES=0
if [ "$(uname -s)" = "Darwin" ]; then
  MEM_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
elif [ -r /proc/meminfo ]; then
  MEM_BYTES=$(awk '/^MemTotal:/ {print $2 * 1024}' /proc/meminfo)
fi
MEM_GB=$(( MEM_BYTES / 1073741824 ))
if [ "$NO_MODEL" -eq 1 ]; then
  say "  memory: ${MEM_GB} GB (the rule-based mode needs no more than Python itself)"
elif [ "$MEM_GB" -lt 16 ]; then
  say "  memory: ${MEM_GB} GB. The loaded model took 12.7 GB on the team's machine; with less than 16 GB it may not load"
  say "  or may run very slowly. You can still use the assistant rule-based: ./install.sh --no-model, then ./run.sh --no-model."
else
  say "  memory: ${MEM_GB} GB: ok (the loaded model took 12.7 GB on the team's 48 GB machine)"
fi
STORE="${OLLAMA_MODELS:-$HOME/.ollama/models}"
PROBE="$STORE"; while [ ! -d "$PROBE" ] && [ "$PROBE" != "/" ]; do PROBE=$(dirname "$PROBE"); done
FREE_KB=$(df -Pk "$PROBE" | awk 'NR==2 {print $4}')
FREE_GB=$(( FREE_KB / 1048576 ))
say "  free disk where Ollama keeps models ($STORE): ${FREE_GB} GB"
say "  the repository itself takes under 100 MB; the built page under 5 MB"

# ---------------------------------------------------------------- 3. Ollama
ollama_up() {
  python3 - "$OLLAMA_URL" <<'PY' >/dev/null 2>&1
import sys, urllib.request
urllib.request.urlopen(sys.argv[1] + "/api/version", timeout=2).read()
PY
}
ollama_version() {
  python3 - "$OLLAMA_URL" <<'PY' 2>/dev/null || true
import json, sys, urllib.request
print(json.loads(urllib.request.urlopen(sys.argv[1] + "/api/version", timeout=2).read()).get("version", "?"))
PY
}

if [ "$NO_MODEL" -eq 1 ]; then
  step 3 "Ollama and the model: skipped (--no-model)"
  say "  The assistant will answer with the rule parser and team-code templates; no language model."
else
  step 3 "Ollama (runs the model on this computer)"
  if ! command -v ollama >/dev/null 2>&1; then
    # Ollama is missing: with a terminal, ask (Enter means yes); --install-ollama answers yes without asking.
    if [ "$INSTALL_OLLAMA" -eq 0 ] && [ "$CHECK" -eq 0 ] && [ -t 0 ]; then
      if [ "$(uname -s)" = "Darwin" ]; then HOW="Homebrew (brew install ollama)"
      else HOW="its official script (curl -fsSL https://ollama.com/install.sh | sh)"; fi
      say "  Ollama is not installed. It is the program that runs the model on this computer (MIT licence)."
      read -r -p "  Install it now with $HOW? [Y/n] " ANSWER || ANSWER="n"
      case "$ANSWER" in ""|y|Y|yes|YES) INSTALL_OLLAMA=1 ;; esac
    fi
    if [ "$INSTALL_OLLAMA" -eq 1 ] && [ "$CHECK" -eq 0 ]; then
      if [ "$(uname -s)" = "Darwin" ]; then
        if command -v brew >/dev/null 2>&1; then
          say "  installing Ollama with Homebrew: brew install ollama"
          brew install ollama
        else
          say "  Homebrew is not installed. Download Ollama for macOS from https://ollama.com/download, then run ./install.sh again."
          exit 1
        fi
      else
        say "  installing Ollama with its official script: curl -fsSL https://ollama.com/install.sh | sh"
        curl -fsSL https://ollama.com/install.sh | sh
      fi
    else
      say "  Ollama is not installed. Install it from https://ollama.com/download"
      say "  (macOS: brew install ollama; Linux: curl -fsSL https://ollama.com/install.sh | sh),"
      say "  or run ./install.sh --install-ollama to have this script run that official method."
      say "  Without it: ./install.sh --no-model, then ./run.sh --no-model (rule-based answers)."
      if [ "$CHECK" -eq 1 ]; then PROBLEMS=$((PROBLEMS + 1)); else exit 1; fi
    fi
  fi
  if command -v ollama >/dev/null 2>&1; then
    say "  $(ollama --version 2>/dev/null | head -1)"
    if ollama_up; then
      say "  the Ollama server answers at $OLLAMA_URL (version $(ollama_version))"
    elif [ "$CHECK" -eq 1 ]; then
      would "start 'ollama serve' in the background (log: $RUNTIME_DIR/ollama.log)"
    else
      mkdir -p "$RUNTIME_DIR"
      say "  starting 'ollama serve' in the background (log: $RUNTIME_DIR/ollama.log)"
      nohup ollama serve >>"$RUNTIME_DIR/ollama.log" 2>&1 &
      for _ in $(seq 1 20); do ollama_up && break; sleep 1; done
      if ollama_up; then say "  the Ollama server answers (version $(ollama_version))"
      else say "  the Ollama server did not answer within 20 s; see $RUNTIME_DIR/ollama.log"; exit 1; fi
    fi
  fi

  # -------------------------------------------------------------- 4. the model
  step 4 "The model: $MAKER $MODEL ($LICENSE)"
  HAVE_MODEL=0
  if command -v ollama >/dev/null 2>&1 && ollama_up; then
    if ollama list 2>/dev/null | awk 'NR > 1 {print $1}' | grep -Fxq "$MODEL"; then HAVE_MODEL=1; fi
  fi
  if [ "$HAVE_MODEL" -eq 1 ]; then
    say "  $MODEL is installed; nothing to download"
  elif [ "$CHECK" -eq 1 ]; then
    if ollama_up; then
      would "ask, then run: ollama pull $MODEL ($MODEL_SIZE_TEXT; ${FREE_GB} GB free)"
    else
      would "check whether $MODEL is installed once the server runs, and download it ($MODEL_SIZE_TEXT) if not"
    fi
  else
    say "  The assistant uses $MAKER $MODEL ($LICENSE), $MODEL_SIZE_TEXT to download."
    if [ "$FREE_GB" -lt 15 ]; then
      say "  Only ${FREE_GB} GB are free where Ollama keeps models; about 15 GB are needed. Free some space and run ./install.sh again."
      exit 1
    fi
    ANSWER="n"
    if [ "$YES" -eq 1 ]; then ANSWER="y"
    elif [ -t 0 ]; then read -r -p "  Download it now? [Y/n] " ANSWER || ANSWER="n"
    else say "  No terminal to ask in; run ./install.sh --yes to download without asking."
    fi
    case "$ANSWER" in
      ""|y|Y|yes|YES) ollama pull "$MODEL"; HAVE_MODEL=1 ;;
      *) say "  Not downloaded. The assistant will run rule-based until you run ./install.sh again." ;;
    esac
  fi

  # -------------------------------------------------------------- 5. digest
  step 5 "The installed model is the build the team checked (digest prefix $PREFIX)"
  if [ "$HAVE_MODEL" -eq 1 ]; then
    # GET /api/tags through ai/llm.py, the project's one audited way to the model server; no model call.
    if DIGEST=$(python3 -c "from ai import llm; print(llm.model_digest()[:12])" 2>&1); then
      say "  digest $DIGEST: ok"
    else
      say "  The installed $MODEL is not the build the team checked (digest prefix $PREFIX). The assistant will"
      say "  run without the model until this is reviewed; see ai/config.py. ($(printf '%s' "$DIGEST" | tail -1))"
      PROBLEMS=$((PROBLEMS + 1))
    fi
  elif [ "$CHECK" -eq 1 ]; then
    would "compare the installed digest with $PREFIX after the download"
  else
    say "  skipped: the model is not installed"
  fi
fi

# ---------------------------------------------------------------- 6. the page
step 6 "Build the page (python3 web/build.py)"
if [ "$CHECK" -eq 1 ]; then
  if [ -f web/dist/index.html ]; then say "  web/dist/index.html exists"; fi
  would "run python3 web/build.py"
else
  python3 web/build.py
fi

# ---------------------------------------------------------------- 7. self-test
step 7 "Assistant self-test (fake model, no network)"
if [ ! -f ai/assistant/server.py ]; then
  say "  ai/assistant/server.py is missing: this copy has no assistant server."
  PROBLEMS=$((PROBLEMS + 1))
elif [ "$CHECK" -eq 1 ]; then
  would "run AI_NO_MODEL_CALLS=1 python3 -m unittest discover -s ai/assistant -p 'test_*.py'"
else
  AI_NO_MODEL_CALLS=1 python3 -m unittest discover -s ai/assistant -p 'test_*.py'
fi
if [ "$CHECK" -eq 0 ] && [ -f ai/assistant/cli.py ]; then
  if [ "$NO_MODEL" -eq 0 ]; then
    say "  health:"; python3 -m ai.assistant.cli health || PROBLEMS=$((PROBLEMS + 1))
  fi
fi

# ---------------------------------------------------------------- done
if [ "$CHECK" -eq 1 ]; then
  say ""; say "Check finished: nothing was downloaded, started, built or changed. ${PROBLEMS} problem(s) found."
  [ "$PROBLEMS" -eq 0 ] && exit 0 || exit 1
fi
say ""
if [ "$PROBLEMS" -gt 0 ]; then say "Done, with ${PROBLEMS} warning(s) above."; else say "Done."; fi
if [ "$NO_MODEL" -eq 1 ]; then say "Start the page with ./run.sh --no-model"; else say "Start the page with ./run.sh"; fi
