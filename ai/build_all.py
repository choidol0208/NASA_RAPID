# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Rebuild every file in data/insights/ in the right order, with no language-model call, then check them.

    python3 ai/build_all.py            # every step, then ai/check_all.py; exit 0 only if all pass
    python3 ai/build_all.py --final    # the same with apply_review --final and check_all --final
    python3 ai/build_all.py --list     # print the steps and stop

Order (each step reads what the steps before it wrote):
  1 evidence      ai/evidence.py         data/insights/evidence.json (PSI record prose as numbered units)
  2 baseline      ai/build_baseline.py   data/insights/scenarios.json and the 24 quoted cards in cards.json
  3 evidence map  ai/evidence_map.py     data/insights/evidence_map.json
  4 readiness     ai/model_readiness.py  data/insights/model_readiness.json (counts, ranges, grouped
                                         cross-validation with scikit-learn; no language model)
  5 robustness    ai/robustness.py       data/insights/robustness.json (rank() under sampled weights, NumPy;
                                         about 15 s)
  6 apply cards   ai/apply_cards.py      cards.json from the logged gpt-oss:20b candidates and repairs in
                                         ai/runs/ (no --repair: no model call), minus the reviewed removals
                                         of ai/review/pm_prereview.json; rewrites ai/review/review_sheet.csv
  7 catalog audit ai/audit_catalog.py    data/insights/catalog_trace.json
  8 apply review  ai/apply_review.py     the verdicts of ai/review/review_sheet.csv; cards.json, quality.json
  9 check         ai/check_all.py        every hard check; exit 1 on any failure. With --assistant-tests it
                --assistant-tests        first runs the assistant's unit tests in ai/assistant/ (fake model,
                                         no network, no model call; writes only to temporary folders)

Step 2 overwrites cards.json with the quoted baseline, so steps 6 and 8 must run after it; that is why
this script exists. Steps 4 and 5 read only data/pipeline/tests.csv, the catalog and scoring/; they were
run by hand before the 14:59 merge and their files went stale when those inputs changed, so they are steps
here. Each step runs as its own process with AI_NO_MODEL_CALLS=1, so ai/llm.py refuses any
network call to a model (ai/llm.py ModelCallsDisabled). The run records in ai/runs/*.jsonl are read, never
written. The script stops at the first step that fails and exits with that step's code (1 if it was 0).
Standard library only.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NO_CALLS_ENV = "AI_NO_MODEL_CALLS"  # the same name as ai/llm.py NO_CALLS_ENV

STEPS = (
    ("evidence", ["ai/evidence.py"]),
    ("baseline scenarios and quoted cards", ["ai/build_baseline.py"]),
    ("evidence map", ["ai/evidence_map.py"]),
    ("model readiness", ["ai/model_readiness.py"]),
    ("robustness", ["ai/robustness.py"]),
    ("apply cards (logged model output, no model call)", ["ai/apply_cards.py", "--quiet"]),
    ("catalog audit", ["ai/audit_catalog.py"]),
    ("apply review", ["ai/apply_review.py"]),
    # the assistant's unit tests (fake model, no network) run inside the check step (check_all --assistant-tests)
    ("check", ["ai/check_all.py", "--assistant-tests"]),
)


def steps(final=False):
    out = []
    for name, cmd in STEPS:
        cmd = list(cmd)
        if final and cmd[0] in ("ai/apply_review.py", "ai/check_all.py"):
            cmd.append("--final")
        out.append((name, cmd))
    return out


def runs_snapshot():
    """{path: (size, mtime_ns)} of the run records, to show that no step wrote one."""
    d = ROOT / "ai" / "runs"
    return {p.name: (p.stat().st_size, p.stat().st_mtime_ns) for p in sorted(d.glob("*.jsonl"))} if d.exists() else {}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--final", action="store_true", help="apply_review --final and check_all --final")
    ap.add_argument("--list", action="store_true", help="print the steps and stop")
    a = ap.parse_args(argv)
    plan = steps(a.final)
    if a.list:
        for i, (name, cmd) in enumerate(plan, 1):
            print(f"{i} {name}: python3 {' '.join(cmd)}")
        return 0
    env = dict(os.environ, **{NO_CALLS_ENV: "1"})
    before = runs_snapshot()
    for i, (name, cmd) in enumerate(plan, 1):
        print(f"\n==== step {i}/{len(plan)}: {name}: python3 {' '.join(cmd)}", flush=True)
        t0 = time.time()
        r = subprocess.run([sys.executable, *cmd], cwd=ROOT, env=env)
        print(f"==== step {i} exit {r.returncode} ({time.time() - t0:.1f} s)", flush=True)
        if r.returncode != 0:
            print(f"\nBUILD STOPPED at step {i} ({name}); later steps did not run.", file=sys.stderr)
            return r.returncode or 1
    changed = [k for k, v in runs_snapshot().items() if before.get(k) != v]
    if changed:
        print(f"\nFAIL: run records in ai/runs/ changed during the build: {changed}", file=sys.stderr)
        return 1
    print(f"\nbuild_all: {len(plan)} steps passed; no model call; ai/runs/*.jsonl unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
