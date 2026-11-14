# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Recompute data/pipeline/raw_values.csv from the source workbooks and report
the differences.

raw_values.csv was copied from an extraction on 2026-11-14; its 15 source
workbooks (13 Saffire per-sample sensor workbooks of PSI-98, PSI-99, PSI-100;
the SAME-R results workbook and the TEM workbook of PSI-101) are not in the
repository, so pipeline/check.py checks the file ids, sizes and links of
raw_values.csv against the listings (check O4) but cannot recompute its
values. This script does, given a folder that holds the workbooks.

Getting the workbooks: each row of raw_values.csv names the PSI file
(psi_file_name) and its PSI file id (psi_file_id). Download each file once with
the public PSI call that scripts/fetch_psi.py uses,
  GET https://psi.nasa.gov/geode-py/ws/studies/<PSI-n>/download?file=<psi_file_name>&version=1&redirect=false
which answers with a temporary download link (keep the link private), and
save the file in one folder under its psi_file_name or as <psi_file_id>.<ext>.
The TEM workbook is an .xls file: openpyxl reads only .xlsx, so convert it
first (for example `soffice --headless --convert-to xlsx <file>.xls`) and keep
the converted file next to it with the same stem and the extension .xlsx; the
extraction read it the same way. Keep downloaded files outside the
repository; they are untrusted data and are only read.

What is recomputed:
  saffire_ambient_pressure  for the column range in cell_or_range of sheet
      'Calibrated Data': number of readings, lowest and highest value with the
      first row where each occurs, first and last value and row, and the
      'Timestamp (ms)' text of the first and the last row
  same_particle_size_statistics  the cached value of the cell (formulas are
      not recalculated; the value stored by the workbook is read)
Numbers are compared with a relative tolerance of 1e-12; text exactly.

Usage: python3 pipeline/raw_values_verify.py WORKBOOK_DIR [--out report.csv]
Exit code 0 when every row of a workbook that was found agrees, 1 otherwise.
Needs openpyxl.
"""
import argparse
import csv
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_VALUES = os.path.join(ROOT, "data", "pipeline", "raw_values.csv")
TOL = 1e-12


def find(folder, row):
    """The workbook of a row in the folder: by PSI name, or by file id; an .xls
    is read from its .xlsx conversion."""
    name, fid = row["psi_file_name"], row["psi_file_id"]
    stem, ext = os.path.splitext(name)
    cands = [name, fid + ext]
    if ext.lower() == ".xls":
        cands = [stem + ".xlsx", fid + ".xlsx"]
    for c in cands:
        p = os.path.join(folder, c)
        if os.path.exists(p):
            return p
    return None


def same(a, b):
    """Stored text a of raw_values.csv against the recomputed value b."""
    if b is None:
        return a == ""
    if isinstance(b, (int, float)) and not isinstance(b, bool):
        try:
            x = float(a)
        except ValueError:
            return False
        return math.isclose(x, float(b), rel_tol=TOL, abs_tol=0.0)
    return a == str(b)


def col_index(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch.upper()) - 64
    return n


def saffire(ws, row):
    m = re.fullmatch(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", row["cell_or_range"])
    col, r0, r1 = col_index(m.group(1)), int(m.group(2)), int(m.group(4))
    header = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
    tcol = header.index("Timestamp (ms)") + 1 if "Timestamp (ms)" in header else None
    vals, times = [], {}
    for i, cells in enumerate(ws.iter_rows(min_row=r0, max_row=r1, values_only=True), start=r0):
        v = cells[col - 1] if len(cells) >= col else None
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            vals.append((i, v))
        if tcol and i in (r0, r1):
            times[i] = cells[tcol - 1]
    lo = min(vals, key=lambda x: (x[1], x[0]))
    hi = max(vals, key=lambda x: (x[1], -x[0]))
    return {"n_readings": len(vals), "min": lo[1], "min_row": lo[0], "max": hi[1], "max_row": hi[0],
            "first_value": vals[0][1], "first_row": vals[0][0], "last_value": vals[-1][1], "last_row": vals[-1][0],
            "time_first": times.get(vals[0][0]), "time_last": times.get(vals[-1][0])}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("workbooks", help="folder with the source workbooks")
    ap.add_argument("--out", help="write the per-row result to this CSV")
    args = ap.parse_args()
    try:
        import openpyxl
    except ImportError:
        sys.exit("raw_values_verify: openpyxl is needed (pip install openpyxl)")
    with open(RAW_VALUES, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    books, grids, results = {}, {}, []
    for r in rows:
        path = find(args.workbooks, r)
        res = {"extraction": r["extraction"], "psi_file_id": r["psi_file_id"], "sheet": r["sheet"],
               "cell_or_range": r["cell_or_range"], "status": "", "differs": ""}
        if path is None:
            res["status"] = "workbook not found"
            results.append(res)
            continue
        if path not in books:
            books[path] = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = books[path][r["sheet"]]
        if r["extraction"] == "saffire_ambient_pressure":
            got = saffire(ws, r)
            bad = [k for k, v in got.items() if not same(r[k], v)]
        else:
            m = re.fullmatch(r"([A-Z]+)(\d+)", r["cell_or_range"])
            if (path, r["sheet"]) not in grids:   # read each sheet once
                grids[(path, r["sheet"])] = [list(c) for c in ws.iter_rows(values_only=True)]
            grid, ri, ci = grids[(path, r["sheet"])], int(m.group(2)) - 1, col_index(m.group(1)) - 1
            v = grid[ri][ci] if ri < len(grid) and ci < len(grid[ri]) else None
            bad = [] if same(r["value"], v) else ["value: file %r, workbook %r" % (r["value"], v)]
        res["status"] = "differs" if bad else "agrees"
        res["differs"] = "; ".join(bad)
        results.append(res)
    n = {s: sum(1 for x in results if x["status"] == s) for s in ("agrees", "differs", "workbook not found")}
    print("raw_values_verify: %d rows: %d agree, %d differ, %d not checked (workbook not found)"
          % (len(results), n["agrees"], n["differs"], n["workbook not found"]))
    for x in results:
        if x["status"] == "differs":
            print("  differs:", x["psi_file_id"], x["sheet"], x["cell_or_range"], x["differs"])
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, list(results[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(results)
    return 1 if n["differs"] else 0


if __name__ == "__main__":
    sys.exit(main())
