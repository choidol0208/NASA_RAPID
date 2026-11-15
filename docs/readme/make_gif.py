#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Puts the screenshots of docs/readme/record_demo.mjs together as one animation.

    python3 docs/readme/make_gif.py <folder with the frames and frames.json> <out.gif>

Keeps the start page, the typed request, one frame per change of the assistant's steps, each finished answer and
the typed follow-up. Nothing is drawn onto the frames. Needs Pillow.
"""
import json
import os
import sys

from PIL import Image

src, out = sys.argv[1], sys.argv[2]
meta = json.load(open(os.path.join(src, "frames.json")))
keep, last_text = [], None
for f in meta["frames"]:
    st = f.get("state")
    if st is None:                       # start page, typed request, typed follow-up
        keep.append((f, 1600)); last_text = None
    elif f["label"].endswith("(done)"):
        keep.append((f, 6000)); last_text = None
    elif st.get("text") != last_text:    # a step finished or started
        keep.append((f, 1000)); last_text = st.get("text")
W = 800
frames, durations = [], []
for f, ms in keep:
    im = Image.open(os.path.join(src, f["file"])).convert("RGB")
    im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    frames.append(im.quantize(colors=128, method=Image.MEDIANCUT, dither=Image.Dither.NONE))
    durations.append(ms)
frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True, disposal=1)
print(f"{out}: {len(frames)} of {len(meta['frames'])} frames, {sum(durations) / 1000:.0f} s, {os.path.getsize(out):,} bytes, {frames[0].size}")
