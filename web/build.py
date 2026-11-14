#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Assemble the static dashboard into web/dist/ for GitHub Pages.

Usage:  python3 web/build.py
Copies the page files and the data the page reads. No third-party packages.
"""
import os
import shutil

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
}
OPTIONAL = {
    "data/insights/cards.json": "data/insights/cards.json",
    "data/insights/scenarios.json": "data/insights/scenarios.json",
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
    open(os.path.join(DIST, ".nojekyll"), "w").close()
    n = sum(len(fs) for _, _, fs in os.walk(DIST))
    print(f"built {n} files into {DIST}")


if __name__ == "__main__":
    main()
