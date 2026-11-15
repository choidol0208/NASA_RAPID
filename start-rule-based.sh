#!/usr/bin/env bash
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
#
# Fire Evidence Explorer, rule-based mode: the dashboard and an assistant that answers from the team's files
# with fixed sentences. No language model is downloaded or run. Needs Python 3.10 or newer (macOS or Linux).
#
#   ./start-rule-based.sh      checks Python, builds the page, runs the self-test, opens http://127.0.0.1:8765/
#
# It runs the two commands of the README for you: ./install.sh --no-model, then ./run.sh --no-model.
# Stop it with Ctrl+C.
set -euo pipefail
cd "$(dirname "$0")"
./install.sh --no-model
exec ./run.sh --no-model "$@"
