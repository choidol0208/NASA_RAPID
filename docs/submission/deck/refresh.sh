#!/usr/bin/env bash
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
#
# One command to bring the deck up to date with the page and the data:
#
#   bash docs/submission/deck/refresh.sh                       # every capture, then the deck with its PDF
#   DECK_ONLY=cotton_top3.png,top.png bash docs/submission/deck/refresh.sh   # only these captures, then the deck
#
# What it does, in order:
#   1. copies the working tree (the files of "git ls-files -co --exclude-standard") to a scratch folder and
#      runs web/build.py there, so the repository's own web/dist is never written;
#   2. serves that build on 127.0.0.1 (a free port from 8821 to 8829);
#   3. runs capture.mjs (headless Chrome; it may reach 127.0.0.1 and the two hosts of the page's fonts only);
#   4. stops the server;
#   5. runs build_deck.py --pdf (numbers.json, slides.html, speaker_notes.md, ../slides.pdf, preview/);
#   6. prints the page count and the size of the PDF.
# It can be run again at any time from the repository root. It leaves no server and no browser running,
# also when a step fails. It calls no language model. It writes only under docs/submission/deck/,
# docs/submission/slides.pdf and its scratch folder.
#
# Environment: DECK_ONLY (capture file names, comma separated); DECK_SCRATCH (scratch folder to use and keep;
# default: a temporary folder, removed at the end); DECK_PORT and DECK_CDP_PORT (ports to use); CHROME.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
cd "$ROOT"

for tool in git python3 node rsync lsof curl; do
  command -v "$tool" >/dev/null 2>&1 || { echo "refresh.sh: '$tool' is not on the PATH" >&2; exit 1; }
done
CHROME_BIN="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME_BIN" ] || { echo "refresh.sh: Google Chrome not found at $CHROME_BIN (set CHROME)" >&2; exit 1; }

MADE_SCRATCH=""
SCRATCH="${DECK_SCRATCH:-}"
if [ -z "$SCRATCH" ]; then
  SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/deck-refresh.XXXXXX")"
  MADE_SCRATCH=1
fi
mkdir -p "$SCRATCH"
SCRATCH="$(cd "$SCRATCH" && pwd)"
case "$SCRATCH" in
  "$ROOT"|"$ROOT"/*) echo "refresh.sh: the scratch folder must lie outside the repository ($SCRATCH)" >&2; exit 1 ;;
esac
SITE="$SCRATCH/site_src"

SERVER_PID=""
stop_server() {
  if [ -n "$SERVER_PID" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
    SERVER_PID=""
  fi
}
cleanup() {
  stop_server
  if [ -n "$MADE_SCRATCH" ]; then rm -rf "$SCRATCH"; fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

port_free() { ! lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1; }
pick_port() {   # a free port from 8821 to 8829, other than $1
  local p
  for p in 8821 8822 8823 8824 8825 8826 8827 8828 8829; do
    if [ "$p" != "${1:-}" ] && port_free "$p"; then echo "$p"; return 0; fi
  done
  return 1
}

echo "refresh.sh: 1/6 copying the working tree to $SITE and building the page there"
rm -rf "$SITE"
mkdir -p "$SITE"
git ls-files -co --exclude-standard | grep -v '^docs/submission/deck/' | while IFS= read -r f; do
  if [ -f "$f" ]; then printf '%s\n' "$f"; fi
done > "$SCRATCH/files.txt"
rsync -a --files-from="$SCRATCH/files.txt" ./ "$SITE/"
( cd "$SITE" && python3 -B web/build.py > "$SCRATCH/build.log" 2>&1 ) || { tail -20 "$SCRATCH/build.log" >&2; echo "refresh.sh: web/build.py failed in the scratch copy" >&2; exit 1; }
[ -f "$SITE/web/dist/index.html" ] || { echo "refresh.sh: the scratch build has no web/dist/index.html" >&2; exit 1; }
tail -1 "$SCRATCH/build.log"

PORT="${DECK_PORT:-$(pick_port)}" || { echo "refresh.sh: no free port from 8821 to 8829" >&2; exit 1; }
CDP="${DECK_CDP_PORT:-$(pick_port "$PORT")}" || { echo "refresh.sh: no second free port from 8821 to 8829" >&2; exit 1; }
echo "refresh.sh: 2/6 serving the scratch build on http://127.0.0.1:$PORT/"
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$SITE/web/dist" > "$SCRATCH/server.log" 2>&1 &
SERVER_PID=$!
for _ in $(seq 1 50); do
  if curl -s -o /dev/null "http://127.0.0.1:$PORT/index.html"; then break; fi
  kill -0 "$SERVER_PID" 2>/dev/null || { cat "$SCRATCH/server.log" >&2; echo "refresh.sh: the server did not start" >&2; exit 1; }
  sleep 0.2
done
curl -s -o /dev/null "http://127.0.0.1:$PORT/index.html" || { echo "refresh.sh: the server does not answer on port $PORT" >&2; exit 1; }

echo "refresh.sh: 3/6 taking the captures${DECK_ONLY:+ ($DECK_ONLY)}"
DECK_CDP_PORT="$CDP" DECK_CHROME_PROFILE="$SCRATCH/chrome-capture" CHROME="$CHROME_BIN" node "$HERE/capture.mjs" "http://127.0.0.1:$PORT/"

echo "refresh.sh: 4/6 stopping the server"
stop_server

echo "refresh.sh: 5/6 building the deck and its PDF"
CHROME="$CHROME_BIN" python3 -B "$HERE/build_deck.py" --pdf --chrome-profile "$SCRATCH/chrome-pdf"

echo "refresh.sh: 6/6 the PDF"
python3 -B - "$ROOT/docs/submission/slides.pdf" <<'PY'
import os, re, sys
p = sys.argv[1]
data = open(p, "rb").read()
pages = len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", data))
print(f"refresh.sh: {os.path.relpath(p)}: {pages} pages, {len(data):,} bytes ({len(data) / 1e6:.2f} MB)")
sys.exit(0 if pages == 7 and len(data) < 10_000_000 else 1)
PY
for p in "$PORT" "$CDP"; do
  if ! port_free "$p"; then echo "refresh.sh: something still listens on port $p" >&2; exit 1; fi
done
echo "refresh.sh: done; nothing listens on ports $PORT and $CDP"
