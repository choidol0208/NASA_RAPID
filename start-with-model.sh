#!/usr/bin/env bash
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
#
# Fire Evidence Explorer with the SI assistant answered by a language model on this computer.
# The model is OpenAI gpt-oss:20b (Apache-2.0), run through Ollama. It is NOT in this download: the install
# asks once and then fetches it through Ollama (about 13 GB; about 16 GB of memory is advised).
# Needs Python 3.10 or newer (macOS or Linux).
#
#   ./start-with-model.sh      checks Python, installs Ollama if you agree, downloads the model if you agree,
#                              builds the page, runs the self-test, opens http://127.0.0.1:8765/
#
# It runs the two commands of the README for you: ./install.sh, then ./run.sh.
# To try the page without the model first: ./start-rule-based.sh. Stop it with Ctrl+C.
set -euo pipefail
cd "$(dirname "$0")"
./install.sh
exec ./run.sh "$@"
