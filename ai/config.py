# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Fixed settings of the AI layer (ai/).

The product uses exactly one language model: OpenAI gpt-oss:20b, run locally
through Ollama. Other models installed on the build machine (qwen2.5, gemma3)
are excluded by the team's rules (AGENTS.md section 6) and are blocked by the
allowlist below, which ai/llm.py checks before any network call.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AI_DIR = ROOT / "ai"
RUNS_DIR = AI_DIR / "runs"
INSIGHTS_DIR = ROOT / "data" / "insights"
PSI_CATALOG_DIR = ROOT / "data" / "psi" / "catalog"
PSI_MANIFEST = ROOT / "data" / "psi" / "manifest.json"

OLLAMA_URL = "http://localhost:11434"

MODEL = "gpt-oss:20b"
ALLOWED = frozenset({"gpt-oss:20b"})
EXPECT_DIGEST_PREFIX = "f38aa0c53da5"
MODEL_MAKER = "OpenAI"
MODEL_LICENSE = "Apache-2.0"
RUNNER = "Ollama 0.40.16 (local)"

# The value written to language_model_used_at_build in every _meta block.
MODEL_LABEL = f"{MODEL} ({EXPECT_DIGEST_PREFIX})"
NO_MODEL = "none"

# Defaults decided by the smoke test (python3 -m ai.llm --smoke); see ai/runs/smoke.jsonl.
# Smoke run 2026-11-14 12:38 KST (Ollama 0.40.16): 'format' (JSON schema) together with think='low'
# returned schema-valid JSON in 3 of 3 calls at temperature 0, with no empty or truncated reply, so
# format_mode stays 'schema' and temperature 0. Measured 50.1 to 51.0 tokens per second, 100% GPU,
# context 16384. Temperature 0 is not bit-reproducible here: PSI-115 gave 366 and 413 output tokens
# in two runs with the same seed.
DEFAULTS = {
    "think": "low",
    "temperature": 0,
    "seed": 7,
    "num_ctx": 16384,
    "num_predict": 2048,
    "format_mode": "schema",  # 'schema': Ollama 'format' gets the JSON schema; 'prompt': schema text in the prompt only
    "retries": 2,
    "timeout_s": 600,
}

# The conversational assistant (ai/assistant/): run-time model calls log here (git-ignored), never in
# ai/runs/; evaluation and recording runs log to RUNS_DIR as the other model calls do.
ASSISTANT_RUNTIME_DIR = AI_DIR / "assistant" / "_runtime"
ASSISTANT = {"max_model_calls": 4, "port": 8765, "message_max_chars": 1000, "state_max_bytes": 8000,
             "call_timeout_s": 180}
# call_timeout_s was 90; at integration (15 Nov) the GPU slowed to about 18 tokens per second while other work
# ran on the machine, and write calls of 1,600+ tokens timed out (q10, q11). 180 s covers 3,200 tokens at 18/s.

CODE_WRITTEN_WITH = "AI assistant (Claude Code)"
HEADER_COMMENT = (
    "# AI-generated code: written with an AI assistant (Claude) during the "
    "NASA Space Apps Challenge 2026 hackathon."
)
