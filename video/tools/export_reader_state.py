# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Build the frozen reader state from labelled character clusters (run once per experiment).

    python3 video/tools/export_reader_state.py --settings video/settings/bass2.json --source <folder> --out <file.npz>

<folder> holds the clustering output of the experiment's own frames: the cluster files named under
settings.reader_state.build.rounds (each an .npz with `labels` [n] and `raw` [n, cell_h, cell_w], the
real cell images that were clustered) and the per-clip grid origins (build.x0_file, JSON
{short: {"x0": px}}). The labels that turn cluster ids into characters are written in the settings.
For BASS-II they were assigned during the pilot by an AI assistant (Claude) that looked at montages of
the cluster members; no person has checked them.

For each labelled cluster: normalise every member, take the normalised mean as the centre, keep the
members whose correlation with the centre exceeds build.member_min_corr, and if at least
build.min_members remain, store the normalised mean of those members as one template. Only the
templates (one cell_h x cell_w image each, normalised) and their characters are written, plus x0 per
clip and a provenance note. No training sample is copied. Prints the SHA-256 and size of the result;
put the SHA-256 into settings.reader_state.sha256 by hand.

BASS-II: run once on 2026-11-14 on the pilot's x0.json, clusters.npz and clusters2.npz.
"""
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from read_overlay import norm  # noqa: E402  (same normalisation as at read time)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--settings", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    s = json.load(open(a.settings, encoding="utf-8"))
    b, g = s["reader_state"]["build"], s["grid"]
    ch, cw = int(g["cell_h"]), int(g["cell_w"])
    templates, chars, sources, skipped = [], [], {}, []
    for rnd in b["rounds"]:
        path = os.path.join(a.source, rnd["clusters_file"])
        sources[rnd["clusters_file"]] = sha256(path)
        d = np.load(path, allow_pickle=False)
        lab, raw = d["labels"], d["raw"]
        if raw.shape[1:] != (ch, cw):
            sys.exit(f"{path}: cell size {raw.shape[1:]} differs from settings {(ch, cw)}")
        for c, ids in rnd["labels"].items():
            for cid in ids:
                mem = raw[lab == cid]
                v = np.array([norm(m) for m in mem])
                cen = v.mean(0)
                cen /= np.linalg.norm(cen)
                good = mem[(v @ cen) > b["member_min_corr"]]
                if len(good) < b["min_members"]:
                    skipped.append(f"{rnd['clusters_file']}:{cid}({c})")
                    continue
                templates.append(norm(good.mean(0)))
                chars.append(c)
    x0p = os.path.join(a.source, b["x0_file"])
    sources[b["x0_file"]] = sha256(x0p)
    x0 = json.load(open(x0p))
    shorts = [c["short"] for c in s["clips"] if c["short"] in x0]
    prov = {"about": ("AI-generated reader state: written by video/tools/export_reader_state.py, code that an AI assistant "
                      "(Claude) wrote during the NASA Space Apps Challenge 2026 hackathon."),
            "experiment": s["experiment"]["name"], "built": time.strftime("%Y-%m-%d"), "numpy": np.__version__,
            "source_sha256": sources, "templates": len(templates), "skipped_clusters": skipped}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    np.savez_compressed(a.out, templates=np.array(templates, np.float32), template_chars=np.array(chars, dtype="<U1"),
                        clip_short=np.array(shorts, dtype="<U16"),
                        clip_x0=np.array([x0[k]["x0"] for k in shorts], np.float64),
                        cell_h=np.int32(ch), cell_w=np.int32(cw), provenance=np.array(json.dumps(prov)))
    print(json.dumps(prov, indent=1))
    print("templates per character:", {c: chars.count(c) for c in sorted(set(chars))})
    print("wrote", a.out, os.path.getsize(a.out), "bytes, sha256", sha256(a.out))


if __name__ == "__main__":
    main()
