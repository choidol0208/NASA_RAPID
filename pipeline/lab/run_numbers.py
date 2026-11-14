# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Runs the lab numbers (envelope position, order changes) and writes
data/pipeline/lab/numbers/index.json (branch data-lab, experiment).

Run: python3 pipeline/lab/run_numbers.py   (after pipeline/run.py)
"""
import envelope
import order_changes
from numlib import ROOT, META, spec, scan_words, write_json


def main():
    S = spec()
    env = envelope.main()
    order = order_changes.main()
    index = {
        "_meta": {"generated_by": META, "script": "pipeline/lab/run_numbers.py", "spec": "pipeline/spec/lab_numbers.json",
                  "status": S["_meta"]["status"]},
        "what_each_number_is": S["readme"]["numbers"],
        "choices": {"envelope": {k: v["value"] for k, v in S["envelope"]["choices"].items()},
                    "order_changes": {k: v["value"] for k, v in S["order_changes"]["choices"].items()}},
        "what_these_numbers_cannot_say": S["readme"]["cannot_say"],
        "envelope": env,
        "order_changes": order,
    }
    scan_words(index, S["forbidden_words"], "index")
    write_json(ROOT / S["output_dir"] / "index.json", index)


if __name__ == "__main__":
    main()
