# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-15).
"""Rebuild data/pipeline/raw_values.csv from a folder of NASA PSI source files.

raw_values.csv holds values read from raw files of PSI; none of them is a value
of tests.csv or enters a count. Its source files are not in the repository:
each is fetched from PSI by its file id and name, as listed in the saved PSI
listing (data/psi/file_listings/, git-ignored) and in the rows of
raw_values.csv. Downloaded files are untrusted data: keep them outside the
repository and run this script with `python3 -I`.

    python3 -I pipeline/raw_values_build.py fetch SRC_DIR [--investigation PSI-69 --pattern REGEX]
        fetch the files a group needs into SRC_DIR/<PSI-n>/ (default: the 272 FLEX
        test sheets of PSI-69); the signed download link PSI answers with is used
        once and never printed or written; a transfer log is appended to
        SRC_DIR/transfer_log.jsonl (file id, name, bytes)
    python3 -I pipeline/raw_values_build.py build SRC_DIR [SRC_DIR ...] [--check] [--strict]
        rebuild raw_values.csv; --check writes nothing and exits 1 if the result
        differs from the committed file

What `build` does, by extraction (column `extraction`):

  saffire_ambient_pressure, same_particle_size_statistics
      the 9,764 rows copied on 2026-11-14 from an extraction whose code is not
      in the repository. Their ties (test_id, link_evidence) are kept as
      committed; every value field is recomputed from the workbook where it is
      in SRC_DIR (pipeline/raw_values_verify.py, which this script calls), and
      a row whose recomputed values differ stops the build. A row whose
      workbook is not in SRC_DIR is kept as committed and counted as "not
      rebuilt" (--strict makes that an error).
  flex_test_sheet
      every `key = value` and `key: value` line of the FLEX per-test sheets
      PSI-69_Raw Data_FLEX-nnn_TestSheet.txt, the value exactly as written
      (nan, 0.00, blank and dash kept), one row per line; tied to a row of the
      FLEX experimental table by the CIR test number printed inside the sheet
      (equal to the table's 'FLEX Identifier') plus a second field: the FLEX
      number printed in the sheet's first line, or the test date; written by
      pipeline/flex_sheets.py, which this script calls.
  bass_as_run_cabin_block
      the cabin-block columns of the BASS as-run workbook (PSI-26 'As Run_Test
      Matrix.xlsx'), one row per run and column, with the codes
      location_not_stated and magnitude_not_as_unit_written; no test is tied
      or placed from it (pipeline/bass_as_run.py).

Rows are written in a fixed order (the committed rows first, in their order,
then the FLEX rows, then the BASS rows), so the same files give the same bytes.
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:          # run with python3 -I: the pipeline folder is added by path, not the cwd
    sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "pipeline", "raw_values.csv")
LISTINGS = os.path.join(ROOT, "data", "psi", "file_listings")
BASE = "https://psi.nasa.gov/geode-py/ws"
PAUSE_S = 0.4
OLD_EXTRACTIONS = ("saffire_ambient_pressure", "same_particle_size_statistics")
COLS = ["extraction", "investigation_id", "test_id", "psi_file_name", "psi_file_id", "bytes", "sheet", "row",
        "cell_or_range", "header_as_written", "unit_as_written", "value", "n_readings", "min", "min_row", "max",
        "max_row", "first_value", "first_row", "last_value", "last_row", "time_first", "time_last", "link_evidence"]
DEFAULT_GROUP = ("PSI-69", r"^PSI-69_Raw Data_FLEX-\d+_TestSheet\.txt$")


def listing_files(inv):
    with open(os.path.join(LISTINGS, inv + ".json"), encoding="utf-8") as f:
        d = json.load(f)
    out = []

    def walk(n):
        for x in n.get("files", []) or []:
            if x.get("directory") or ("bytes_size" not in x and x.get("files")):
                walk(x)
            else:
                out.append(x)
    walk(d)
    seen, uniq = set(), []
    for x in out:
        if x["id"] not in seen:
            seen.add(x["id"])
            uniq.append(x)
    return uniq


def fetch(src, inv, pattern):
    os.makedirs(os.path.join(src, inv), exist_ok=True)
    rx = re.compile(pattern)
    files = [f for f in listing_files(inv) if rx.search(f["key"].rsplit("/", 1)[-1])]
    got = 0
    with open(os.path.join(src, "transfer_log.jsonl"), "a", encoding="utf-8") as log:
        for f in sorted(files, key=lambda x: x["key"]):
            name = f["key"].rsplit("/", 1)[-1]
            path = os.path.join(src, inv, name)
            if os.path.exists(path) and os.path.getsize(path) == int(f["bytes_size"]):
                continue
            q = urllib.parse.urlencode({"file": name, "version": f.get("version") or 1, "redirect": "false"})
            time.sleep(PAUSE_S)
            link = urllib.request.urlopen(f"{BASE}/studies/{inv}/download?{q}", timeout=60).read().decode().strip()
            data = urllib.request.urlopen(link, timeout=120).read()
            link = None
            with open(path, "wb") as out:
                out.write(data)
            got += len(data)
            log.write(json.dumps({"investigation_id": inv, "psi_file_id": f["id"], "name": name,
                                  "bytes": len(data), "listed_bytes": int(f["bytes_size"])}) + "\n")
    print("fetch: %d files of %s match; %d bytes transferred now" % (len(files), inv, got))


def read_committed():
    with open(OUT, encoding="utf-8", newline="") as f:
        return f.read()


def rows_of(text):
    return list(csv.DictReader(io.StringIO(text)))


def to_text(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def build(srcs, strict=False):
    import raw_values_verify as V
    import flex_sheets
    import bass_as_run
    old = [r for r in rows_of(read_committed()) if r["extraction"] in OLD_EXTRACTIONS]
    rebuilt = kept = 0
    differ = []
    books, grids = {}, {}
    for r in old:
        path = next((x for x in (V.find(d, r) for d in srcs if os.path.isdir(d)) if x), None)
        if path is None:
            kept += 1
            continue
        import openpyxl
        if path not in books:
            books[path] = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = books[path][r["sheet"]]
        if r["extraction"] == "saffire_ambient_pressure":
            got = V.saffire(ws, r)
            bad = [k for k, v in got.items() if not V.same(r[k], v)]
        else:
            m = re.fullmatch(r"([A-Z]+)(\d+)", r["cell_or_range"])
            if (path, r["sheet"]) not in grids:
                grids[(path, r["sheet"])] = [list(c) for c in ws.iter_rows(values_only=True)]
            grid, ri, ci = grids[(path, r["sheet"])], int(m.group(2)) - 1, V.col_index(m.group(1)) - 1
            v = grid[ri][ci] if ri < len(grid) and ci < len(grid[ri]) else None
            bad = [] if V.same(r["value"], v) else ["value"]
        if bad:
            differ.append((r["psi_file_name"], r["cell_or_range"], bad))
        rebuilt += 1
    if differ:
        sys.exit("build: %d committed rows differ from their workbooks, first: %r" % (len(differ), differ[0]))
    if strict and kept:
        sys.exit("build: %d committed rows have no workbook in %s" % (kept, ", ".join(srcs)))
    flex = next((x for x in (flex_sheets.raw_rows(d) for d in srcs) if x), [])
    bass = next((x for x in (bass_as_run.raw_rows(d) for d in srcs) if x), [])
    rows = old + flex + bass
    print("build: %d committed rows (%d recomputed and equal, %d not rebuilt: workbook absent), %d FLEX sheet rows, "
          "%d BASS as-run rows" % (len(old), rebuilt, kept, len(flex), len(bass)))
    return to_text(rows)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("src")
    f.add_argument("--investigation", default=DEFAULT_GROUP[0])
    f.add_argument("--pattern", default=DEFAULT_GROUP[1])
    b = sub.add_parser("build")
    b.add_argument("src", nargs="+", help="one or more folders; a workbook is taken from the first that holds it, "
                   "the FLEX sheets from <folder>/PSI-69/, the BASS workbook from <folder>/PSI-26/")
    b.add_argument("--check", action="store_true")
    b.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    if a.cmd == "fetch":
        fetch(a.src, a.investigation, a.pattern)
        return 0
    text = build(a.src, a.strict)
    if a.check:
        same = text == read_committed()
        print("build --check: %s" % ("identical to the committed raw_values.csv" if same else "DIFFERS from the committed file"))
        return 0 if same else 1
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("build: wrote %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
