#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Puts the screenshots of docs/readme/record_demo.mjs together as one animation.

    python3 docs/readme/make_gif.py <folder with the frames and frames.json> <out.gif>

Every frame of the recording is used, each shown for the time frames.json gives it ("ms"). The frames are not
edited here; the pointer in them was drawn into the page by the recording script. Needs FFmpeg on the PATH.
"""
import json
import os
import subprocess
import sys

src, out = os.path.abspath(sys.argv[1]), sys.argv[2]
meta = json.load(open(os.path.join(src, "frames.json")))
frames = meta["frames"]
lines = []
for f in frames:
    lines.append(f"file '{os.path.join(src, f['file'])}'")
    lines.append(f"duration {f['ms'] / 1000:.3f}")
lines.append(f"file '{os.path.join(src, frames[-1]['file'])}'")   # the concat demuxer needs the last file once more
lst = os.path.join(src, "list.txt")
open(lst, "w").write("\n".join(lines) + "\n")
vf = ("scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];"
      "[b][p]paletteuse=dither=none:diff_mode=rectangle")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-vf", vf,
                "-fps_mode", "vfr", "-loop", "0", out], check=True)
total = sum(f["ms"] for f in frames) / 1000
print(f"{out}: {len(frames)} frames, {total:.0f} s, {os.path.getsize(out):,} bytes")
