# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-15).
"""The two cabin-block columns of the BASS as-run workbook (PSI-26,
'PSI-26_Science Documents_As Run_Test Matrix.xlsx'), step 5 of
docs/raw_data_design/design.md.

Called by raw_values_build.py: raw_rows(src) reads <src>/PSI-26/<that file>
and returns rows of data/pipeline/raw_values.csv (extraction
bass_as_run_cabin_block), one per run and column, for the columns headed
'O2 % by volume' and 'pressure, atm' under the group label 'ISS environment'
in the sheets '2012' and '2013'. Only these two columns and the columns that
identify the run (actual date, as-run test number, test number, sample number)
are read; no other cell of the workbook is read or copied.

A run is tied to a row of NASA's BASS table (PSI-26_Experimental table_BASS.csv)
when its 'As run test no.' equals the table's 'As Run Test #' and its 'Test no.'
equals the table's 'Test #' (two fields); the actual date is compared with the
table's 'Date' (m/d/yy read as 20yy) and the result is written, not used. The value is the stored cell
value, written with Python's str(). Codes in link_evidence:
  location_not_stated            the group label is 'ISS environment'; the
                                 workbook does not say where or when in the
                                 run the value was taken
  magnitude_not_as_unit_written  the header says '%' and the stored number is
                                 below 1 (as a mole fraction would be)
No test is placed from these values and none enters a count.
"""
import csv
import datetime
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NAME = "PSI-26_Science Documents_As Run_Test Matrix.xlsx"
TABLE = "PSI-26_Experimental table_BASS.csv"
SHEETS = ("2012", "2013")
COLUMNS = ("O2 % by volume", "pressure, atm")
GROUP = "ISS environment"
STATE = "read from NASA's file, not adopted"


def norm(v):
    return " ".join(str(v).split()) if v is not None else ""


def as_written(v):
    if v is None:
        return ""
    if isinstance(v, datetime.datetime):
        return v.strftime("%Y-%m-%d")
    return str(v)


def day(v):
    if isinstance(v, datetime.datetime):
        return v.date()
    m = re.match(r"^\s*(\d+)/(\d+)/(\d{4}|\d{2})\s*$", str(v or ""))
    if not m:
        return None
    y = int(m.group(3))
    return datetime.date(y if y > 99 else 2000 + y, int(m.group(1)), int(m.group(2)))


def table_rows():
    raw = open(os.path.join(ROOT, "data", "psi", "experimental_tables", TABLE), "rb").read()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    rd = csv.reader(io.StringIO(text))
    head = [h.lstrip("﻿").lstrip("ï»¿") for h in next(rd)]
    return [(i, dict(zip(head, r))) for i, r in enumerate(rd, start=2)]


def listing_record(name):
    import json
    with open(os.path.join(ROOT, "data", "psi", "file_listings", "PSI-26.json"), encoding="utf-8") as f:
        d = json.load(f)
    found = []

    def walk(n):
        for x in n.get("files", []) or []:
            if x.get("directory") or ("bytes_size" not in x and x.get("files")):
                walk(x)
            elif x["key"].rsplit("/", 1)[-1] == name:
                found.append(x)
    walk(d)
    return found[0] if found else None


def raw_rows(src):
    path = os.path.join(src, "PSI-26", NAME)
    if not os.path.exists(path):
        return []
    import openpyxl
    rec = listing_record(NAME)
    if rec is None or int(float(rec["bytes_size"])) != os.path.getsize(path):
        raise SystemExit("bass_as_run: %s is not in the PSI-26 listing with its bytes" % NAME)
    with open(os.path.join(ROOT, "data", "pipeline", "tests.csv"), encoding="utf-8", newline="") as f:
        by_row = {int(t["source_row"]): t["test_id"] for t in csv.DictReader(f) if t["source_file"] == TABLE}
    table = table_rows()
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = []
    for sname in SHEETS:
        ws = wb[sname]
        grid = [list(r) for r in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True)]
        hrow = next(i for i, r in enumerate(grid) if any(norm(c) == COLUMNS[0] for c in r))
        grow = next(i for i, r in enumerate(grid[:hrow + 2]) if any(norm(c) == GROUP for c in r))
        head = [norm(c) for c in grid[hrow]]
        gcol = [norm(c) for c in grid[grow]].index(GROUP)
        ci = {h: head.index(h) for h in COLUMNS + ("As run test no.", "Test no.", "Sample no.")}
        dcol = next(i for i, h in enumerate(head) if h.startswith("Actual Date"))
        for i in range(max(hrow, grow) + 1, len(grid)):
            r = grid[i] + [None] * (len(head) - len(grid[i]))
            asrun = norm(r[ci["As run test no."]])
            if not re.fullmatch(r"\d+", asrun):
                continue
            d = day(r[dcol])
            test_no = norm(r[ci["Test no."]])
            cands = [(n, c) for n, c in table if norm(c.get("As Run Test #")) == asrun and norm(c.get("Test #")) == test_no]
            tid, ev = "", ""
            if len(cands) == 1:
                n, c = cands[0]
                tid = by_row.get(n, "")
                ev = ("'As run test no.' %s and 'Test no.' %s equal %s row %d columns 'As Run Test #' and 'Test #'; "
                      "actual date %s, table 'Date' %r: %s" % (asrun, test_no, TABLE, n, d, c.get("Date"),
                                                              "same day" if d == day(c.get("Date")) else "not the same day"))
                if tid:
                    ev += "; tests.csv source_file=%s, source_row=%d" % (TABLE, n)
            else:
                ev = "%d rows of %s have 'As Run Test #' %s and 'Test #' %s" % (len(cands), TABLE, asrun, test_no)
            for col in COLUMNS:
                v = r[ci[col]]
                codes = ["location_not_stated"]
                if col.startswith("O2") and isinstance(v, (int, float)) and 0 < v < 1:
                    codes.append("magnitude_not_as_unit_written")
                letter = openpyxl.utils.get_column_letter(ci[col] + 1)
                out.append({"extraction": "bass_as_run_cabin_block", "investigation_id": "PSI-26", "test_id": tid,
                            "psi_file_name": NAME, "psi_file_id": rec["id"], "bytes": str(int(float(rec["bytes_size"]))),
                            "sheet": sname, "row": str(i + 1), "cell_or_range": "%s%d" % (letter, i + 1),
                            "header_as_written": col, "unit_as_written": col.split(",")[-1].strip() if "," in col else "%",
                            "value": as_written(v),
                            **{k: "" for k in ("n_readings", "min", "min_row", "max", "max_row", "first_value", "first_row",
                                               "last_value", "last_row", "time_first", "time_last")},
                            "link_evidence": "%s; group label %r over column %s; codes: %s; tie: %s; no test is placed "
                                             "from this value" % (STATE, GROUP, openpyxl.utils.get_column_letter(gcol + 1),
                                                                  "; ".join(codes), ev)})
    return out
