#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Puts the screenshots of docs/readme/record_demo.mjs together as one animation, with a caption per scene.

    python3 docs/readme/make_gif.py <folder with the frames and frames.json> <out.gif>

Every frame of the recording is used, each shown for the time frames.json gives it ("ms"). This script adds a band
at the foot of every frame: one line that says what the scene shows, and one line that says what the recording
is. The pointer in the frames was drawn into the page by the recording script. Needs Pillow and FFmpeg.
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

CAPTIONS = {
    "start page": "Fire Evidence Explorer: NASA fire tests for what you build.",
    "to the input": "Type what you are building, in plain words.",
    "click the input": "Type what you are building, in plain words.",
    "typing the request": "Type what you are building, in plain words.",
    "to the button": "Press Find evidence.",
    "click Find evidence": "Press Find evidence.",
    "first answer": "The dashboard is there at once. The SI assistant reads, looks up, writes and checks.",
    "first answer (done)": "The answer: every sentence cites a fact from the team's files.",
    "the answer, lower part": "Ask a follow-up in your own words.",
    "to the follow-up box": "Ask a follow-up in your own words.",
    "click the follow-up box": "Ask a follow-up in your own words.",
    "typing the follow-up": "Ask a follow-up in your own words.",
    "to Send": "Send it.",
    "click Send": "Send it.",
    "follow-up answer": "The assistant keeps the material and answers for the ISS.",
    "follow-up answer (done)": "A cited answer for the ISS cabin; the dashboard follows.",
    "dashboard": "One request: how it was read, three key figures, five tabs.",
    "tab closest": "Closest investigations: match score, reason and largest gap.",
    "tab found": "What was found: NASA's reported results, question by question.",
    "tab data": "Where the data are: NASA's tables, the archive, or no record.",
    "tab stops": "Where the evidence stops: every recorded test on the oxygen axis.",
    "tab all": "All 24 investigations, ranked for this request.",
}
for _t in ("closest", "found", "data", "stops", "all"):
    CAPTIONS[f"tab {_t} move"] = CAPTIONS[f"tab {_t} click"] = "Five tabs, each with its own colour and one line on what it holds."
NOTE = "Recording of the local install · the language model gpt-oss:20b answers · pointer, typing and captions added by script · waiting shortened"

src, out = os.path.abspath(sys.argv[1]), sys.argv[2]
meta = json.load(open(os.path.join(src, "frames.json")))
frames = meta["frames"]
NOTE = meta.get("note_line") or NOTE
big = ImageFont.load_default(size=27)      # Pillow's built-in face (Aileron), so no font file is needed
small = ImageFont.load_default(size=13)
cap_dir = os.path.join(src, "captioned")
os.makedirs(cap_dir, exist_ok=True)
BAND, FADE = 78, 26
for f in frames:
    im = Image.open(os.path.join(src, f["file"])).convert("RGBA")
    w, h = im.size
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(FADE):                                   # a short fade above the band
        d.line([(0, h - BAND - FADE + i), (w, h - BAND - FADE + i)], fill=(18, 24, 36, int(232 * (i + 1) / FADE)))
    d.rectangle([0, h - BAND, w, h], fill=(18, 24, 36, 236))
    text = CAPTIONS.get(f["label"], "")
    tw = d.textlength(text, font=big)
    d.text(((w - tw) / 2, h - BAND + 8), text, font=big, fill=(255, 255, 255, 255), stroke_width=1, stroke_fill=(255, 255, 255, 255))
    nw = d.textlength(NOTE, font=small)
    d.text(((w - nw) / 2, h - 24), NOTE, font=small, fill=(196, 204, 216, 255))
    Image.alpha_composite(im, ov).convert("RGB").save(os.path.join(cap_dir, f["file"]))
lines = []
for f in frames:
    lines.append(f"file '{os.path.join(cap_dir, f['file'])}'")
    lines.append(f"duration {f['ms'] / 1000:.3f}")
lines.append(f"file '{os.path.join(cap_dir, frames[-1]['file'])}'")   # the concat demuxer needs the last file once more
lst = os.path.join(src, "list.txt")
open(lst, "w").write("\n".join(lines) + "\n")
vf = ("scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];"
      "[b][p]paletteuse=dither=none:diff_mode=rectangle")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-vf", vf,
                "-fps_mode", "vfr", "-loop", "0", out], check=True)
print(f"{out}: {len(frames)} frames, {sum(f['ms'] for f in frames) / 1000:.0f} s, {os.path.getsize(out):,} bytes")
