#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Assemble the static dashboard into web/dist/ for GitHub Pages.

Usage:  python3 web/build.py
Copies the page files and the data the page reads. No third-party packages.
"""
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(HERE, "dist")

PAGE = ["index.html", "style.css", "app.js", "scorer.js"]
DATA = {
    "scoring/scoring_config.json": "data/scoring_config.json",
    "data/catalog/investigations.csv": "data/investigations.csv",
    "data/catalog/configurations.csv": "data/configurations.csv",
    "data/pipeline/capability_matrix.csv": "data/capability_matrix.csv",
    "data/pipeline/tests.csv": "data/tests.csv",
    "pipeline/spec/needs.json": "data/needs.json",
    "data/pipeline/coverage_grid.csv": "data/coverage_grid.csv",
    "pipeline/spec/coverage.json": "data/coverage.json",
    "data/pipeline/need_references.csv": "data/need_references.csv",
}
OPTIONAL = {
    "data/insights/cards.json": "data/insights/cards.json",
    "data/insights/scenarios.json": "data/insights/scenarios.json",
    "data/insights/evidence_map.json": "data/insights/evidence_map.json",
    "data/pipeline/scenario_needs.csv": "data/scenario_needs.csv",
    "data/pipeline/scenario_tests.csv": "data/scenario_tests.csv",
    "pipeline/spec/scenarios.json": "data/scenario_spec.json",
}


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, "data", "insights"))
    for f in PAGE:
        shutil.copy(os.path.join(HERE, f), os.path.join(DIST, f))
    for src, dst in DATA.items():
        shutil.copy(os.path.join(ROOT, src), os.path.join(DIST, dst))
    for src, dst in OPTIONAL.items():
        if os.path.exists(os.path.join(ROOT, src)):
            shutil.copy(os.path.join(ROOT, src), os.path.join(DIST, dst))
    # The commit the site was built from, so links to source files and rows point at
    # exactly the files the page reads (GITHUB_SHA in Actions, git HEAD locally).
    sha = os.environ.get("GITHUB_SHA")
    if not sha:
        try:
            sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            sha = "main"
    with open(os.path.join(DIST, "data", "build.json"), "w", encoding="utf-8") as fh:
        json.dump({"commit": sha, "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}, fh)
    open(os.path.join(DIST, ".nojekyll"), "w").close()
    n = sum(len(fs) for _, _, fs in os.walk(DIST))
    print(f"built {n} files into {DIST}")


if __name__ == "__main__":
    main()
