# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Transcribe the text overlay of experiment videos into one CSV per clip.

    python3 video/read_overlay.py --settings video/settings/bass2.json --clips <mp4 folder> --out <folder>

Everything specific to an experiment (overlay position, character grid, fields, formats, clip names,
flag rules, frozen reader state) comes from the settings file and the reader state it names. This file
holds only the common reading code. Options:
  --list            print the clips of the settings with their NASA table test, then stop
  --fetch           download the clips named in the settings from NASA PSI into --clips first
  --dry-run         with --fetch: ask PSI for its file listing and print names and sizes, download nothing
  --verify DIR      read again and compare with the CSV files in DIR; exit 1 on any difference
  --jobs N          clips read in parallel (default: number of CPUs, at most 8)

What a CSV holds is a transcription of what the video display shows. It measures nothing.
Checked only on the 19 BASS-II clips named in settings/bass2.json. The code assumes one fixed-pitch text
grid, one frame size and a six-digit HHMMSS clock; an overlay without a clock is not supported yet.
The download path of --fetch has not been run from this package; only --fetch --dry-run was.
Needs: Python 3, NumPy, Pillow (tests only), ffmpeg and ffprobe on the PATH.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

import numpy as np

EPILOG = ("Checked only on the 19 BASS-II clips named in settings/bass2.json. "
          "A transcription of a display; it measures nothing.")


class ReaderError(Exception):
    pass


# ----------------------------------------------------------------------------- settings and state

def load_settings(path):
    with open(path, encoding="utf-8") as fh:
        s = json.load(fh)
    s["_path"] = os.path.abspath(path)
    s["_dir"] = os.path.dirname(os.path.abspath(path))
    for key, why in (("disclosure", "the disclosure sentence written into reading_manifest.json"),
                     ("clock_check", "an overlay without a clock is not supported yet")):
        if key not in s:
            raise ReaderError(f"settings: {key!r} is missing ({why})")
    known = {"t_video_s", "overlay_present", "flag"} | {f["column"] for f in s["fields"]}
    for c in s["columns"]:
        if c not in known:
            raise ReaderError(f"settings: column {c!r} is neither a field nor t_video_s/overlay_present/flag")
    return s


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_state(settings):
    """Load the frozen reader state after checking its SHA-256 against the settings."""
    rs = settings["reader_state"]
    path = os.path.normpath(os.path.join(settings["_dir"], rs["file"]))
    if not os.path.exists(path):
        raise ReaderError(f"reader state not found: {path}")
    got = sha256_file(path)
    if got != rs["sha256"]:
        raise ReaderError(f"reader state checksum mismatch for {path}: settings say {rs['sha256']}, file is {got}")
    with np.load(path, allow_pickle=False) as d:
        tm = d["templates"].astype(np.float32)
        chars = [str(c) for c in d["template_chars"]]
        x0 = {str(k): float(v) for k, v in zip(d["clip_short"], d["clip_x0"])}
        cell_hw = (int(d["cell_h"]), int(d["cell_w"]))
    g = settings["grid"]
    if cell_hw != (g["cell_h"], g["cell_w"]) or tm.shape[1] != g["cell_h"] * g["cell_w"]:
        raise ReaderError("reader state cell size does not match the settings grid")
    uniq = sorted(set(chars))
    groups = [(c, np.array([i for i, x in enumerate(chars) if x == c])) for c in uniq]
    return {"path": path, "sha256": got, "TM": tm, "groups": groups, "x0": x0}


# ----------------------------------------------------------------------------- geometry and matching

class Geometry:
    def __init__(self, settings):
        g = settings["grid"]
        self.pitch = float(g["pitch_px"])
        self.cw, self.ch = int(g["cell_w"]), int(g["cell_h"])
        self.lines = {k: int(v) for k, v in g["lines"].items()}
        self.strip_x0 = int(settings["strip"]["cols"][0])

    def cell(self, strip, line, k, x0, dx=0, dy=0):
        """The cell_h x cell_w patch of cell k on `line` (strip coordinates); x0 in frame pixels."""
        xs = int(round(x0 - self.strip_x0 + k * self.pitch)) + dx
        y = self.lines[line] + dy
        p = strip[y:y + self.ch, xs:xs + self.cw].astype(np.float32)
        if p.shape[1] < self.cw:
            p = np.pad(p, ((0, 0), (0, self.cw - p.shape[1])))
        return p

    def mean_of_cells(self, strip, line, cells, x0):
        return np.mean([self.cell(strip, line, k, x0).mean() for k in cells])


def norm(p):
    q = p.ravel().astype(np.float32)
    q = q - q.mean()
    n = np.linalg.norm(q)
    return q / n if n > 1e-6 else q


def find_x0(strips, geo, osr):
    """Grid origin from the clip-averaged header line (only for clips without a frozen x0)."""
    m = strips.mean(0)
    best = None
    for x0 in np.arange(osr["from_px"], osr["to_px"], osr["step_px"]):
        on = np.mean([geo.cell(m, osr["line"], k, x0).mean() for k in osr["on_cells"]])
        off = np.mean([geo.cell(m, osr["line"], k, x0).mean() for k in osr["off_cells"]])
        sc = on - off
        if best is None or sc > best[0]:
            best = (sc, x0)
    return float(best[1])


class Reader:
    def __init__(self, settings, state):
        self.s = settings
        self.geo = Geometry(settings)
        self.TM = state["TM"]
        self.groups = state["groups"]
        m = settings["matching"]
        self.min_corr, self.margin = float(m["min_corr"]), float(m["margin"])
        self.shifts = [int(v) for v in m["shift_px"]]
        self.blank = m["blank"]

    def classify(self, strip, line, k, x0, ref):
        """One cell -> (character, ' ' for blank, '?' for unreadable)."""
        best = None
        for dx in self.shifts:
            for dy in self.shifts:
                q = norm(self.geo.cell(strip, line, k, x0, dx, dy))
                if not q.any():
                    continue
                cs = self.TM @ q
                per = np.array([cs[ix].max() for _, ix in self.groups])
                best = per if best is None else np.maximum(best, per)
        if best is None:
            return " "
        order = np.argsort(-best, kind="stable")
        s1, s2 = best[order[0]], best[order[1]]
        if s1 >= self.min_corr and s1 - s2 >= self.margin:
            return self.groups[order[0]][0]
        if self.geo.cell(strip, line, k, x0).mean() < self.blank["ratio"] * ref:
            return " "
        return "?"

    def read_strip(self, strip, x0):
        """One strip -> {column: text or ''} plus overlay_present."""
        geo, s = self.geo, self.s
        ref = geo.mean_of_cells(strip, self.blank["line"], self.blank["ref_cells"], x0)
        out = {}
        for f in s["fields"]:
            txt = "".join(self.classify(strip, f["line"], k, x0, ref) for k in f["cells"])
            out[f["column"]] = parse_field(f, txt)
        op = s["overlay_present"]
        on = geo.mean_of_cells(strip, op["line"], op["on_cells"], x0)
        off = geo.mean_of_cells(strip, op["line"], op["off_cells"], x0)
        out["overlay_present"] = bool(on > op["factor"] * off + op["offset"])
        return out


def parse_field(field, txt):
    """Raw cell text -> the value as shown, or '' when any part is unread or the format does not fit."""
    if field["kind"] == "clock_hhmmss":
        if re.match(r"^\d{6}$", txt) and int(txt[:2]) < 24 and int(txt[2:4]) < 60 and int(txt[4:]) < 60:
            return txt
        return ""
    t = txt.strip()
    if " " in t or "?" in t or not re.match(field["format"], t):
        return ""
    return t


def clock_seconds(v):
    return int(v[:2]) * 3600 + int(v[2:4]) * 60 + int(v[4:]) if v else None


def clock_on_line(rows, settings):
    """Per row: True/False for a read clock on/off the clip's line, None where no clock was read."""
    cc = settings["clock_check"]
    secs = [clock_seconds(r[cc["column"]]) for r in rows]
    offs = [c - r["t_video_s"] for c, r in zip(secs, rows) if c is not None]
    if not offs:
        return [None] * len(rows)
    med = float(np.median(offs))
    return [None if c is None else abs(c - r["t_video_s"] - med) <= cc["tolerance_s"] for c, r in zip(secs, rows)]


def apply_flags(rows, settings):
    """Fill the flag column from the rule list of the settings. Values are never changed."""
    online = clock_on_line(rows, settings)
    flags = [[] for _ in rows]
    for rule in settings["flags"]:
        if rule["type"] == "above_max":
            for i, r in enumerate(rows):
                v = r[rule["column"]]
                if v != "" and float(v) > rule["max"]:
                    flags[i].append(rule["flag"])
        elif rule["type"] == "clock_isolated_off_line":
            for i in range(1, len(rows) - 1):
                if online[i] is False and online[i - 1] is True and online[i + 1] is True:
                    flags[i].append(rule["flag"])
        else:
            raise ReaderError(f"unknown flag rule type {rule['type']!r}")
    for r, fl in zip(rows, flags):
        r["flag"] = ";".join(dict.fromkeys(fl))
    return online


# ----------------------------------------------------------------------------- video

def probe_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split(",")[:2]
    return int(w), int(h)


def extract_strips(path, settings):
    """Decode the clip with ffmpeg and return (strips uint8 [n, rows, cols], t_video_s list)."""
    v, sm, st = settings["video"], settings["sampling"], settings["strip"]
    W, H = int(v["width"]), int(v["height"])
    if probe_size(path) != (W, H):
        raise ReaderError(f"{os.path.basename(path)}: frame size {probe_size(path)} differs from settings {(W, H)}")
    (r0, r1), (c0, c1) = st["rows"], st["cols"]
    wts = np.array(st["gray_weights"], np.float32)
    every = int(sm["keep_every_nth"])
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={sm['ffmpeg_fps']}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W * H * 3 * 4)
    strips, ts, i, n = [], [], 0, W * H * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        if i % every == 0:
            f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            g = f[r0:r1, c0:c1].astype(np.float32) @ wts
            strips.append(np.clip(g, 0, 255).astype(np.uint8))
            ts.append(len(ts) * float(sm["seconds_per_row"]))
        i += 1
    if p.wait() != 0:
        raise ReaderError(f"ffmpeg failed on {path}")
    return np.array(strips), ts


def fmt_t(t):
    return str(int(t)) if float(t).is_integer() else repr(float(t))


def read_clip(path, clip, settings, state):
    """Read one clip -> (rows, info)."""
    geo = Geometry(settings)
    strips, ts = extract_strips(path, settings)
    measured = find_x0(strips, geo, settings["grid"]["origin_search"])
    x0 = state["x0"].get(clip["short"])
    source = "reader_state"
    if x0 is None:
        x0, source = measured, "measured_from_clip"
    reader = Reader(settings, state)
    rows = []
    for s, t in zip(strips, ts):
        r = reader.read_strip(s, x0)
        r["t_video_s"] = t
        rows.append(r)
    online = apply_flags(rows, settings)
    value_cols = [f["column"] for f in settings["fields"]]
    info = {"file": clip["file"], "short": clip["short"], "bytes": os.path.getsize(path), "rows": len(rows),
            "x0_used": x0, "x0_source": source, "x0_measured_now": measured,
            "rows_overlay_absent": sum(not r["overlay_present"] for r in rows),
            "rows_all_values": sum(all(r[c] != "" for c in value_cols) for r in rows),
            "rows_clock_off_line": sum(o is False for o in online),
            "rows_flagged": [{"t_video_s": r["t_video_s"], "flag": r["flag"]} for r in rows if r["flag"]]}
    return rows, info


def csv_text(rows, settings):
    buf = io.StringIO()
    cols = settings["columns"]
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    for r in rows:
        w.writerow([fmt_t(r[c]) if c == "t_video_s" else ("True" if r[c] else "False") if c == "overlay_present"
                    else r[c] for c in cols])
    return buf.getvalue()


# ----------------------------------------------------------------------------- commands

def cmd_list(settings):
    print(f"{settings['experiment']['name']} ({settings['experiment']['psi_accession']}, doi {settings['experiment']['doi']}): "
          f"{len(settings['clips'])} clips")
    print(f"{'short':6} {'NASA table test':15} {'GMT day':7} {'date':10}  {'outcome (team reading of table)':31}  file")
    for c in settings["clips"]:
        print(f"{c['short']:6} {c['nasa_table_test']:15} {c['recording_gmt_day']:<7} {c['recording_date']:10}  "
              f"{c.get('table_outcome_team_reading', ''):31}  {c['file']}")


def _worker(args):
    path, clip, settings_path = args
    settings = load_settings(settings_path)
    state = load_state(settings)
    t0 = time.time()
    rows, info = read_clip(path, clip, settings, state)
    info["seconds"] = round(time.time() - t0, 1)
    return clip["short"], csv_text(rows, settings), info


def run_reading(settings, clips_dir, jobs):
    todo, missing, wrong = [], [], []
    for c in settings["clips"]:
        p = os.path.join(clips_dir, c["file"])
        if not os.path.exists(p):
            missing.append(c["file"])
        elif c.get("bytes") and os.path.getsize(p) != c["bytes"]:
            wrong.append((c["file"], os.path.getsize(p), c["bytes"]))
        else:
            todo.append((p, c, settings["_path"]))
    for name in missing:
        print("not present, skipped:", name, file=sys.stderr)
    for name, got, want in wrong:
        print(f"size differs from settings ({got} != {want} bytes), skipped: {name}", file=sys.stderr)
    results = {}
    if jobs > 1 and len(todo) > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            for short, text, info in ex.map(_worker, todo):
                results[short] = (text, info)
                print(f"{short}: {info['rows']} rows, {info['rows_all_values']} with FUEL, AIR, FAN, RAD and clock, "
                      f"{info['rows_overlay_absent']} overlay absent, flagged {len(info['rows_flagged'])}, {info['seconds']} s",
                      flush=True)
    else:
        for item in todo:
            short, text, info = _worker(item)
            results[short] = (text, info)
            print(f"{short}: {info['rows']} rows, {info['rows_all_values']} with FUEL, AIR, FAN, RAD and clock, "
                  f"{info['rows_overlay_absent']} overlay absent, flagged {len(info['rows_flagged'])}, {info['seconds']} s",
                  flush=True)
    return results, missing, wrong


def ffmpeg_version():
    try:
        return subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.splitlines()[0]
    except (OSError, IndexError):
        return "unknown"


def cmd_read(settings, state, clips_dir, out_dir, jobs):
    os.makedirs(out_dir, exist_ok=True)
    results, missing, wrong = run_reading(settings, clips_dir, jobs)
    order = [c["short"] for c in settings["clips"] if c["short"] in results]
    for short in order:
        with open(os.path.join(out_dir, f"{short}.csv"), "w", newline="", encoding="utf-8") as fh:
            fh.write(results[short][0])
    manifest = {
        "about": settings["disclosure"],
        "what": "One CSV per clip, one row per sampled frame: NASA's on-screen overlay values as read by video/read_overlay.py.",
        "settings_file": os.path.basename(settings["_path"]), "settings_sha256": sha256_file(settings["_path"]),
        "reader_state_file": os.path.basename(state["path"]), "reader_state_sha256": state["sha256"],
        "ffmpeg": ffmpeg_version(), "numpy": np.__version__, "python": sys.version.split()[0],
        "clips": [{k: v for k, v in results[s][1].items() if k != "seconds"} for s in order],
        "clips_not_present": missing, "clips_wrong_size": [w[0] for w in wrong],
    }
    with open(os.path.join(out_dir, "reading_manifest.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    print(f"wrote {len(order)} CSV files and reading_manifest.json to {out_dir}")
    if not order:
        print("error: no clip of the settings was read from", clips_dir, file=sys.stderr)
        return 1
    return 0 if not wrong else 1


def cmd_verify(settings, clips_dir, ref_dir, jobs):
    results, missing, wrong = run_reading(settings, clips_dir, jobs)
    ndiff, nfiles, nrows = 0, 0, 0
    for c in settings["clips"]:
        ref = os.path.join(ref_dir, f"{c['short']}.csv")
        if c["short"] not in results:
            if os.path.exists(ref):
                print(f"DIFF {c['short']}: reference file exists but the clip could not be read")
                ndiff += 1
            continue
        if not os.path.exists(ref):
            print(f"DIFF {c['short']}: no reference file {ref}")
            ndiff += 1
            continue
        new = list(csv.reader(io.StringIO(results[c["short"]][0])))
        with open(ref, newline="", encoding="utf-8") as fh:
            old = list(csv.reader(fh))
        nfiles += 1
        nrows += len(new) - 1
        if len(new) != len(old):
            print(f"DIFF {c['short']}: {len(new) - 1} rows now, {len(old) - 1} in reference")
            ndiff += 1
        for i, (a, b) in enumerate(zip(new, old)):
            if a != b:
                ndiff += 1
                if ndiff <= 50:
                    print(f"DIFF {c['short']} line {i + 1}: now {a} reference {b}")
    print(f"verify: {nfiles} files, {nrows} rows compared, {ndiff} differences")
    return 0 if ndiff == 0 and nfiles > 0 and not wrong else 1


def psi_listing(settings):
    """File listing of the accession from PSI (names, sizes, versions; no file body)."""
    e, base = settings["experiment"], settings["psi"]["base_url"]
    acc = e["psi_accession"]
    body = json.dumps({"folder": f"{acc}/", "fileType": "study", "studyId": acc,
                       "version": e["psi_investigation_version"], "obfuscationcode": ""}).encode("utf-8")
    req = urllib.request.Request(f"{base}/files/v2", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    leaves = {}

    def walk(node):
        for f in node.get("files") or []:
            if f.get("files"):
                walk(f)
            elif not f.get("directory"):
                name = f["key"].rsplit("/", 1)[-1]
                leaves[name] = {"bytes": int(f.get("bytes_size") or 0), "version": f.get("version") or 1}
    walk(data)
    return leaves


def cmd_fetch(settings, clips_dir, dry_run):
    acc, base = settings["experiment"]["psi_accession"], settings["psi"]["base_url"]
    listing = psi_listing(settings)
    print(f"PSI listing of {acc}: {len(listing)} files")
    bad = []
    for c in settings["clips"]:
        dest = os.path.join(clips_dir, c["file"])
        f = listing.get(c["file"])
        if f is None:
            print(f"NOT IN PSI LISTING: {c['file']}")
            bad.append(c["file"])
            continue
        here = os.path.exists(dest) and os.path.getsize(dest) == f["bytes"]
        note = "" if (f["bytes"] == c.get("bytes") and f["version"] == c.get("psi_version")) else \
            f"  (settings: {c.get('bytes')} bytes, version {c.get('psi_version')})"
        print(f"{c['short']:6} {f['bytes']:>11} bytes  v{f['version']}  {'present' if here else 'to download'}  {c['file']}{note}")
        if dry_run or here:
            continue
        os.makedirs(clips_dir, exist_ok=True)
        q = urllib.parse.urlencode({"file": c["file"], "version": f["version"], "redirect": "false"})
        try:
            link = urllib.request.urlopen(f"{base}/studies/{acc}/download?{q}", timeout=60).read().decode().strip()
            with urllib.request.urlopen(link, timeout=120) as r, open(dest + ".part", "wb") as w:
                for chunk in iter(lambda: r.read(1 << 20), b""):
                    w.write(chunk)
            if os.path.getsize(dest + ".part") != f["bytes"]:
                os.remove(dest + ".part")
                raise ReaderError("size differs from the PSI listing")
            os.replace(dest + ".part", dest)
        except (OSError, ReaderError, ValueError) as exc:
            print(f"FAILED {c['file']}: {str(exc)[:160]}")
            bad.append(c["file"])
    if dry_run:
        print("dry run: nothing downloaded")
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], epilog=EPILOG)
    ap.add_argument("--settings", required=True)
    ap.add_argument("--clips", help="folder with the clip files")
    ap.add_argument("--out", help="folder for the CSV files")
    ap.add_argument("--verify", metavar="DIR", help="compare a fresh reading with the CSV files in DIR")
    ap.add_argument("--fetch", action="store_true", help="download the clips named in the settings from PSI first")
    ap.add_argument("--dry-run", action="store_true", help="with --fetch: list names and sizes, download nothing")
    ap.add_argument("--list", action="store_true", help="print the clips of the settings and stop")
    ap.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1))
    a = ap.parse_args(argv)
    try:
        settings = load_settings(a.settings)
        if a.list:
            cmd_list(settings)
            return 0
        if not a.clips:
            ap.error("--clips is required")
        if a.fetch:
            rc = cmd_fetch(settings, a.clips, a.dry_run)
            if a.dry_run or rc:
                return rc
        state = load_state(settings)
        if a.verify:
            return cmd_verify(settings, a.clips, a.verify, a.jobs)
        if not a.out:
            ap.error("--out is required (or --verify, --list, --fetch --dry-run)")
        return cmd_read(settings, state, a.clips, a.out, a.jobs)
    except ReaderError as exc:
        print("error:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
