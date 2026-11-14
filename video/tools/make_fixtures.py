# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Save overlay-strip fixtures for the unit tests (run once; needs the clips).

    python3 video/tools/make_fixtures.py --settings video/settings/bass2.json --clips <mp4 folder> --out video/fixtures \
        O9:576 M17:202 ...

Each fixture is the grayscale overlay strip exactly as the reader sees it (the strip box of the settings,
nothing else of the picture), saved as a lossless 8-bit PNG named <short>_t<second>.png.
"""
import argparse
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from read_overlay import extract_strips, load_settings  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--settings", required=True)
    ap.add_argument("--clips", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("items", nargs="+", help="<short>:<second>")
    a = ap.parse_args()
    s = load_settings(a.settings)
    by_short = {c["short"]: c for c in s["clips"]}
    want = {}
    for it in a.items:
        short, sec = it.split(":")
        want.setdefault(short, []).append(int(sec))
    os.makedirs(a.out, exist_ok=True)
    for short, secs in want.items():
        strips, ts = extract_strips(os.path.join(a.clips, by_short[short]["file"]), s)
        for sec in secs:
            i = ts.index(float(sec))
            p = os.path.join(a.out, f"{short}_t{sec}.png")
            Image.fromarray(strips[i], mode="L").save(p, optimize=True)
            print(p, os.path.getsize(p), "bytes")


if __name__ == "__main__":
    main()
