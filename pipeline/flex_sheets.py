# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-15).
"""The FLEX per-test sheets (PSI-69, 'PSI-69_Raw Data_FLEX-nnn_TestSheet.txt'):
parse, tie to a row of NASA's FLEX experimental table, compare every field.

Step 4 of docs/raw_data_design/design.md. Two uses:

  raw_rows(src)   called by raw_values_build.py: parses the sheets in
                  <src>/PSI-69/ into rows of data/pipeline/raw_values.csv
                  (extraction flex_test_sheet): one row for the first line of
                  each sheet and one per 'key = value' or 'key: value' line
                  above 'COMMENTS', the value exactly as written (leading and
                  trailing blanks and tabs removed; nan, 0.00 and dashes kept)
  compare(rows)   called by raw_gaps.py on the committed raw_values.csv: ties
                  each sheet to a table row and compares each field with the
                  table cell as NASA's table file writes it (blank and the en
                  dash kept), for flex_sheet_vs_table.csv and the block
                  flex_test_sheets of raw_values_effect.json

Tie rule: the CIR test number printed inside the sheet equals the table's
'FLEX Identifier' (first label), and a second field agrees: the FLEX number of
the sheet's first line equals 'FLEX Test #', or, where it does not, the test
date of the sheet equals the table's 'Test Date'. tie_state:
  identifier_and_number   identifier and FLEX number name the same row
  identifier_and_date     identifier and date name one row; the FLEX number
                          names another row or none (the two numberings differ)
  identifier_only         the identifier names rows, no second field agrees
  identifier_not_in_table the identifier is in no row
A sheet is tied (test_id filled) only for the first two states. Nothing read
here becomes a value of tests.csv or enters a count.
"""
import csv
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TABLE = "PSI-69_Experimental table_FLEX.csv"
TABLE_PATH = os.path.join(ROOT, "data", "psi", "experimental_tables", TABLE)
LISTING = os.path.join(ROOT, "data", "psi", "file_listings", "PSI-69.json")
NAME_RX = re.compile(r"^PSI-69_Raw Data_FLEX-(\d+)_TestSheet\.txt$")
LINE_RX = re.compile(r"^\s*([^=:\t][^=:\t]*?)\s*([=:])\s*\t?(.*)$")
FIRST_LINE = "(first line)"
STATE = "read from NASA's file, not adopted"
# sheet key (blanks collapsed) -> (table column, how to compare)
FIELDS = [
    ("CIR Test Number", "FLEX Identifier", "text"),
    ("Test Date", "Test Date", "date"),
    ("Test Time", "Test GMT", "time"),
    ("Pressure (atm)", "Ambient pressure; mmHg", "atm_vs_mmhg"),
    ("O2 Mole Fraction", "O initial ambient composition; mole fraction", "number"),
    ("N2 Mole Fraction", "N initial ambient composition; mole fraction", "number"),
    ("CO2 Mole Fraction", "CO initial ambient composition; mole fraction", "number"),
    ("He Mole Fraction", "He initial ambient composition; mole fraction", "number"),
    ("Temperature (K)", None, None),
    ("Fuel", "Fuel", "text"),
    ("D0 (mm)", "Droplet initial diameter; mm", "number"),
    ("kavg (mm2/s)", "Burning rate; mm", "number"),
    ("Fiber", None, None),
    ("Dext (mm)", "Visible flame extinction diameter; mm", "number"),
]
MMHG_PER_ATM = 760.0
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}


def norm(key):
    return " ".join(key.split())


def form(v):
    """Form of a value as written: number, zero, nan, blank, dash, text."""
    s = (v or "").strip()
    if s == "":
        return "blank"
    if s in ("-", "–", "—"):
        return "dash"
    if s.lower() == "nan":
        return "nan"
    try:
        return "zero" if float(s) == 0 else "number"
    except ValueError:
        return "text"


# ------------------------------------------------------------------ table
def read_table(path=TABLE_PATH):
    """Rows of NASA's FLEX table as the file writes them: (source_row, {column: cell text})."""
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    rd = csv.reader(io.StringIO(text))
    head = next(rd)
    out = []
    for i, row in enumerate(rd, start=2):
        out.append((i, dict(zip(head, row + [""] * (len(head) - len(row))))))
    return head, out


# ------------------------------------------------------------------ sheets
def listing_index(path=LISTING):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    out = {}

    def walk(n):
        for x in n.get("files", []) or []:
            if x.get("directory") or ("bytes_size" not in x and x.get("files")):
                walk(x)
            else:
                out.setdefault(x["key"].rsplit("/", 1)[-1], x)
    walk(d)
    return out


def parse(path):
    """[(line number, key as written, value as written)], the first line as key FIRST_LINE."""
    text = open(path, "rb").read().decode("utf-8", errors="replace")
    lines = text.splitlines()
    out = [(1, FIRST_LINE, lines[0].strip(" \t"))] if lines else []
    for i, line in enumerate(lines[1:], start=2):
        if line.strip().upper().startswith("COMMENTS"):
            break
        m = LINE_RX.match(line)
        if m:
            out.append((i, m.group(1).strip(" \t"), m.group(3).strip(" \t")))
    return out


def unit_of(key):
    m = re.search(r"\(([^)]*)\)\s*$", key)
    return m.group(1) if m else ""


def tie(fields, table_rows):
    """(tie_state, source_row or None, evidence) from the parsed fields of one sheet."""
    ident = fields.get("CIR Test Number", "")
    m = re.match(r"^FLEX-(\d+)$", fields.get(FIRST_LINE, ""))
    num = int(m.group(1)) if m else None
    cands = [(r, c) for r, c in table_rows if c["FLEX Identifier"].strip() == ident and ident]
    if not cands:
        return "identifier_not_in_table", None, "the CIR test number %r is in no row of %s" % (ident, TABLE)
    by_num = [(r, c) for r, c in cands if num is not None and c["FLEX Test #"].strip() == str(num)]
    if len(by_num) == 1:
        r, c = by_num[0]
        return "identifier_and_number", r, ("sheet line 'CIR Test Number' %r equals %s row %d column 'FLEX Identifier'; "
                                            "second field: the sheet's first line %r equals 'FLEX Test #' %s"
                                            % (ident, TABLE, r, fields.get(FIRST_LINE), c["FLEX Test #"]))
    by_date = [(r, c) for r, c in cands if same_date(fields.get("Test Date", ""), c["Test Date"])]
    if len(by_date) == 1:
        r, c = by_date[0]
        return "identifier_and_date", r, ("sheet line 'CIR Test Number' %r equals %s row %d column 'FLEX Identifier'; "
                                          "second field: the sheet's 'Test Date' %r equals the table's 'Test Date' %r; "
                                          "the sheet's first line %r and the table's 'FLEX Test #' %s differ"
                                          % (ident, TABLE, r, fields.get("Test Date"), c["Test Date"],
                                             fields.get(FIRST_LINE), c["FLEX Test #"]))
    return "identifier_only", None, ("the CIR test number %r is in %s rows %s; neither the FLEX number nor the date "
                                     "names one of them" % (ident, TABLE, ", ".join(str(r) for r, _ in cands)))


def sheet_date(text):
    m = re.match(r"^\s*\w+,\s*(\w+)\s+(\d+),\s*(\d{4})", text or "")
    if not m or m.group(1) not in MONTHS:
        return None
    return (int(m.group(3)), MONTHS[m.group(1)], int(m.group(2)))


def table_date(text):
    """m/d/yyyy, or m/d/yy read as 20yy (the table writes both forms)."""
    m = re.match(r"^\s*(\d+)/(\d+)/(\d{4}|\d{2})\s*$", text or "")
    if not m:
        return None
    y = int(m.group(3))
    return (y if y > 99 else 2000 + y, int(m.group(1)), int(m.group(2)))


def same_date(a, b):
    x, y = sheet_date(a), table_date(b)
    return x is not None and x == y


def raw_rows(src, tests_by_row=None):
    folder = os.path.join(src, "PSI-69")
    if not os.path.isdir(folder):
        return []
    head, table_rows = read_table()
    if tests_by_row is None:
        with open(os.path.join(ROOT, "data", "pipeline", "tests.csv"), encoding="utf-8", newline="") as f:
            tests_by_row = {int(t["source_row"]): t["test_id"] for t in csv.DictReader(f) if t["source_file"] == TABLE}
    idx = listing_index()
    names = sorted((n for n in os.listdir(folder) if NAME_RX.match(n)), key=lambda n: (int(NAME_RX.match(n).group(1)), n))
    out = []
    for n in names:
        rec = idx.get(n)
        if rec is None or int(float(rec["bytes_size"])) != os.path.getsize(os.path.join(folder, n)):
            raise SystemExit("flex_sheets: %s is not in the PSI-69 listing with its bytes" % n)
        parsed = parse(os.path.join(folder, n))
        fields = {norm(k): v for _, k, v in parsed}
        state, row, ev = tie(fields, table_rows)
        tid = tests_by_row.get(row, "") if row else ""
        if tid:
            ev += "; tests.csv source_file=%s, source_row=%d" % (TABLE, row)
        for line, key, value in parsed:
            out.append({"extraction": "flex_test_sheet", "investigation_id": "PSI-69", "test_id": tid,
                        "psi_file_name": n, "psi_file_id": rec["id"], "bytes": str(int(float(rec["bytes_size"]))), "sheet": "",
                        "row": str(line), "cell_or_range": "line %d" % line, "header_as_written": key,
                        "unit_as_written": unit_of(key) if key != FIRST_LINE else "", "value": value,
                        **{k: "" for k in ("n_readings", "min", "min_row", "max", "max_row", "first_value", "first_row",
                                           "last_value", "last_row", "time_first", "time_last")},
                        "link_evidence": "%s; tie %s: %s" % (STATE, state, ev)})
    return out


# ------------------------------------------------------------------ compare
def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def decimals(s):
    s = (s or "").strip()
    return len(s.split(".", 1)[1]) if "." in s else 0


def agreement(kind, sheet, cell):
    """Agreement of a sheet value with a table cell, both as written."""
    if kind == "text":
        return "agrees_as_written" if sheet.strip() == cell.strip() else "differs"
    if kind == "date":
        return "agrees" if same_date(sheet, cell) else "differs"
    if kind == "time":
        return "agrees" if sheet.split("(")[0].strip() == cell.strip() else "differs"
    fs, fc = form(sheet), form(cell)
    if fs not in ("number", "zero") or fc not in ("number", "zero"):
        return "same_form_%s" % fs if fs == fc else "forms_differ"
    a, b = num(sheet), num(cell)
    if kind == "atm_vs_mmhg":
        b = b / MMHG_PER_ATM
    half = 0.5 * 10 ** -decimals(sheet) + 1e-9
    if a == b:
        return "agrees_as_written" if kind != "atm_vs_mmhg" else "agrees_within_rounding"
    return "agrees_within_rounding" if abs(a - b) <= half else "differs"


def compare(rows, table=None):
    """Per sheet: the tie and every field against the table. rows: raw_values.csv rows."""
    head, table_rows = table or read_table()
    by_row = dict(table_rows)
    sheets = {}
    for r in rows:
        if r["extraction"] == "flex_test_sheet":
            sheets.setdefault((r["psi_file_name"], r["psi_file_id"], r["bytes"]), []).append(r)
    out = []
    for (name, fid, size) in sorted(sheets, key=lambda k: (int(NAME_RX.match(k[0]).group(1)), k[0])):
        rs = sheets[(name, fid, size)]
        fields = {norm(r["header_as_written"]): r["value"] for r in rs}
        state, row, _ = tie(fields, table_rows)
        cell = by_row.get(row, {})
        comp = []
        for key, col, kind in FIELDS:
            if key not in fields:
                comp.append({"key": key, "sheet_value": None, "table_column": col, "table_cell": cell.get(col) if col else None,
                             "agreement": "key_not_in_sheet"})
                continue
            if col is None:
                comp.append({"key": key, "sheet_value": fields[key], "table_column": None, "table_cell": None,
                             "agreement": "no_table_column"})
                continue
            if row is None:
                comp.append({"key": key, "sheet_value": fields[key], "table_column": col, "table_cell": None,
                             "agreement": "not_tied"})
                continue
            comp.append({"key": key, "sheet_value": fields[key], "table_column": col, "table_cell": cell[col],
                         "agreement": agreement(kind, fields[key], cell[col]),
                         "sheet_form": form(fields[key]), "table_form": form(cell[col])})
        m = NAME_RX.match(name)
        f1 = re.match(r"^FLEX-(\d+)$", fields.get(FIRST_LINE, ""))
        out.append({"psi_file_name": name, "psi_file_id": fid, "bytes": int(size), "number_in_name": int(m.group(1)),
                    "first_line": fields.get(FIRST_LINE, ""), "number_in_sheet": int(f1.group(1)) if f1 else None,
                    "identifier_in_sheet": fields.get("CIR Test Number", ""), "tie_state": state, "table_row": row,
                    "table_flex_test_number": cell.get("FLEX Test #") if row else None,
                    "test_id": rs[0]["test_id"], "fields": comp})
    return out
