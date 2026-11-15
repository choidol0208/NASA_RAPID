# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Independent validator of the pipeline outputs.

It does not import run.py, rules.py, evidence.py, facts.py, findings.py,
answers.py, raw_inventory.py, raw_gaps.py or raw_names.py. Every check recomputes its result from the raw
NASA PSI tables (and, for the raw inventory and the name ties, the saved PSI file listings) and
from the rules as they are written in pipeline/spec/*.json ('_meta' blocks)
and pipeline/README.md, then compares with the files in data/pipeline/.

    python3 pipeline/check.py                 all checks, writes validation_report.json
    python3 pipeline/check.py --data DIR      check another copy of data/pipeline/
    python3 pipeline/check.py --spot-check    also writes reports/spot_check.csv

Exit code 1 when a check fails. The report carries no timestamp.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import os
import random
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = os.path.join(HERE, "spec")
RAW = os.path.join(ROOT, "data", "psi", "experimental_tables")
CATALOG = os.path.join(ROOT, "data", "psi", "catalog")
MANIFEST = os.path.join(ROOT, "data", "psi", "manifest.json")

MAX_EXAMPLES = 20
ROUND_TOL = 5.1e-5      # converted values are written with 4 decimals
DERIVED_TOL = 1e-4      # tolerance for formulas of variables.json
STAT_TOL = 5.1e-6       # indicator statistics are written with 5 decimals
SPOT_SEED = 20261114
SPOT_PER_TABLE = 20
SPOT_PER_VARIABLE = 4

CONSTANT_MARK = "(constant in sources.json)"
MATERIAL_MARK = "(materials.json from fuel_material)"
ID_COLUMNS = ("test_id", "investigation_id", "source_id")
TAIL_COLUMNS = ("flags", "source_file", "source_row")
MATCHED_TIERS = ("atmosphere", "oxygen_only", "pressure_only")
TIERS = MATCHED_TIERS + ("other",)
FORBIDDEN_WORDS = ("safe", "unsafe", "flammable", "sufficient", "representative", "proves", "confirms")


# ----------------------------------------------------------------------------
# reading
# ----------------------------------------------------------------------------

class Skip(Exception):
    pass


def read_bytes(path, tries=6):
    """Other processes may rewrite the outputs while this runs: read again on failure."""
    last = None
    if not os.path.exists(path):
        raise FileNotFoundError("missing file: " + path)
    for _ in range(tries):
        try:
            with open(path, "rb") as f:
                data = f.read()
            if data:
                return data
            last = OSError("empty file: " + path)
        except OSError as exc:
            last = exc
        time.sleep(0.4)
    raise last


def read_json(path):
    last = None
    for _ in range(4):
        try:
            return json.loads(read_bytes(path).decode("utf-8"))
        except ValueError as exc:      # half-written file
            last = exc
            time.sleep(0.4)
    raise last


def read_csv(path):
    text = read_bytes(path).decode("utf-8")
    return list(csv.DictReader(io.StringIO(text, newline="")))


def read_raw_table(file_name):
    """Raw PSI table as rows of stripped cells; row 1 is the header."""
    text = read_bytes(os.path.join(RAW, file_name)).decode("utf-8-sig", "replace")
    return [[c.strip() for c in row] for row in csv.reader(io.StringIO(text, newline=""))]


_NUM_FULL = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")


def fnum(text):
    """A cell or value read as a number, or None."""
    if text is None:
        return None
    if isinstance(text, bool):
        return None
    if isinstance(text, (int, float)):
        return float(text)
    s = str(text).strip()
    if not _NUM_FULL.match(s):
        return None
    return float(s)


def close(a, b, tol=1e-9):
    return a is not None and b is not None and abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def near(a, b, tol):
    return a is not None and b is not None and abs(a - b) <= tol


def psi_key(inv):
    m = re.search(r"(\d+)$", inv or "")
    return (int(m.group(1)) if m else 10 ** 9, inv or "")


def split_list(text, sep=";"):
    return [x for x in (text or "").split(sep) if x != ""]


class Ctx:
    """Lazy access to the spec, the raw tables and the pipeline outputs."""

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self._cache = {}

    def _get(self, key, loader):
        if key not in self._cache:
            self._cache[key] = loader()
        return self._cache[key]

    def spec(self, name):
        return self._get(("spec", name), lambda: read_json(os.path.join(SPEC, name + ".json")))

    def out_path(self, name):
        return os.path.join(self.data_dir, name)

    def has(self, name):
        return os.path.exists(self.out_path(name))

    def table(self, name):
        return self._get(("csv", name), lambda: read_csv(self.out_path(name)))

    def json(self, name):
        return self._get(("json", name), lambda: read_json(self.out_path(name)))

    def raw(self, file_name):
        return self._get(("raw", file_name), lambda: read_raw_table(file_name))

    def record(self, inv):
        return self._get(("record", inv), lambda: read_json(os.path.join(CATALOG, inv + ".json")))

    # ---- shapes derived from the outputs (no pipeline logic) ----
    @property
    def tests(self):
        return self.table("tests.csv")

    @property
    def tests_by_id(self):
        return self._get("tests_by_id", lambda: {t["test_id"]: t for t in self.tests})

    @property
    def variable_columns(self):
        def load():
            cols = list(self.tests[0].keys()) if self.tests else []
            return [c for c in cols if c not in ID_COLUMNS and c not in TAIL_COLUMNS]
        return self._get("variable_columns", load)

    @property
    def sources(self):
        return self.spec("sources")["sources"]

    @property
    def source_by_file(self):
        return self._get("source_by_file", lambda: {s["file"]: s for s in self.sources})

    @property
    def source_by_id(self):
        return self._get("source_by_id", lambda: {s["id"]: s for s in self.sources})

    @property
    def needs(self):
        return self.spec("needs")["needs"]

    @property
    def var_unit(self):
        def load():
            v = self.spec("variables")
            units = {k: d.get("unit", "") for k, d in v["variables"].items()}
            units.update({k: d.get("unit", "") for k, d in v["derived"].items()})
            return units
        return self._get("var_unit", load)

    @property
    def values_index(self):
        """(test_id, variable) -> list of values_long rows."""
        def load():
            idx = {}
            for r in self.table("values_long.csv"):
                idx.setdefault((r["test_id"], r["variable"]), []).append(r)
            return idx
        return self._get("values_index", load)

    @property
    def reference_items(self):
        def load():
            items = {}
            for ref in self.spec("references")["references"]:
                for it in ref.get("items", []):
                    items[it["id"]] = (ref, it)
            return items
        return self._get("reference_items", load)


class Result:
    def __init__(self):
        self.numbers = {}
        self.failures = []
        self.details = {}
        self.checked = 0

    def fail(self, **keys):
        self.failures.append(keys)


CHECKS = []


def check(cid, verifies):
    def deco(fn):
        CHECKS.append((cid, verifies, fn))
        return fn
    return deco


# ----------------------------------------------------------------------------
# A. trace to source cells
# ----------------------------------------------------------------------------

_NUM_TOKEN = re.compile(r"\d+\.\d+|\.\d+|\d+")
_FRACTION = re.compile(r"(\d+)\s*/\s*(\d+)")
_UNIT_AFTER = re.compile(r"^\s*(microns?|um|µm|mm|cm|inch(?:es)?|in\b|\"|m\b)", re.I)
_LABEL_BEFORE = re.compile(r"(note|notes|fig|figure|table|ref|eq|see)\s*\.?\s*$", re.I)
LENGTH_TO_MM = {"micron": 0.001, "microns": 0.001, "um": 0.001, "µm": 0.001, "mm": 1.0, "cm": 10.0,
                "m": 1000.0, "inch": 25.4, "inches": 25.4, "in": 25.4, '"': 25.4}

NO_VALUE_MARKERS = ("n/a", "na", "none")

FAIL_CLASSES = {
    "unexplained": "no rule found that leads from the raw cell to the value",
    "empty_cell": "the raw cell is empty but a value is recorded. This includes columns that sources.json lists "
                  "under 'fill_down' (the value is the cell of a row above): the rule that an empty cell means "
                  "'not recorded' and is never filled in does not allow it",
    "category_not_in_cell": "a text value that is not written in the cell and that no spec file maps the cell "
                            "text to (the mapping lives in engine code, not in the spec)",
    "computed_midpoint": "the value is the midpoint of two numbers in the cell: computed, not copied, and "
                         "not a formula of variables.json",
    "reference_label_number": "the number is the label of a note or figure in the cell ('Note 4', 'Fig. 5'), "
                              "not a measurement",
    "assumed_unit": "the value needs a unit conversion whose unit is neither written in the cell nor "
                    "declared in sources.json",
    "declared_factor_not_applied": "sources.json declares a factor for the column but the value equals the "
                                   "raw number without it",
    "unit_ignored": "the number is copied although the unit written after it in the cell is not the unit of "
                    "the variable",
    "declared_exception_without_flag": "a value of a kind that README declares (one of two oxygen numbers named "
                                       "by a publication, material from the BASS-II ReadMe, cell of the row "
                                       "above) but the test does not carry the flag README names for it",
    "spec_rule_gives_other_value": "the rule written in the spec for this column (sources.json "
                                   "'_meta.sample_keywords' or '_meta.documented_start') leads from the cell "
                                   "to a different value, or to none",
    "two_number_cell_not_documented": "an oxygen value from a cell with two numbers whose exact text is not "
                                      "listed under 'documented_start' (sources.json): such a cell gives no value",
}
PASS_CLASSES = {
    "exact": "same text (ignoring case) or the same number as the raw cell",
    "declared_factor": "a number in the cell times the factor or unit conversion declared in sources.json",
    "number_in_text": "the only number written in a longer cell",
    "vocabulary": "the spec maps the cell text to this category (sources.json 'map', or the keywords "
                  "listed in the variable's meaning in variables.json)",
    "one_of_several_numbers": "one of several numbers written in the cell; which one is chosen is an engine "
                              "rule that the spec does not state",
    "unit_in_cell": "a number in the cell converted from the unit written next to it to the variable's unit",
    "text_in_cell": "the value is written inside a longer cell",
    "material_alias_in_cell": "the cell names a material of materials.json (id or alias) and the value is "
                              "another alias of the same material",
    "declared_exception_flagged": "a value of a kind README declares in the table 'Values that are not literally "
                                  "in a NASA cell' (one of two oxygen numbers written, named by a publication; "
                                  "material from the BASS-II ReadMe; cell of the row above): it is exactly what "
                                  "the declared rule gives and the test carries the named flag",
}
# kind of declared exception -> flag suffix that the test must carry on the variable
EXCEPTION_FLAGS = {
    "oxygen_start_named_in_publication": "range_in_source_start_value_named_in_publication",
    "material_from_readme": "not_written_in_cell_named_in_readme",
    "cell_of_row_above": "blank_in_source_value_of_row_above_used",
}
THICKNESS_UNITS = ("micron", "microns", "um", "µm", "mm")


def sample_keywords_reading(cell, params):
    """The validator's reading of sources.json '_meta.sample_keywords': material, shape and rod diameter that
    the keyword entries give for a sample cell, and whether the material is written in the cell."""
    low = cell.lower()
    thick = [t["v"] * LENGTH_TO_MM[t["unit"]] for t in number_tokens(cell) if t["unit"] in THICKNESS_UNITS]
    thickness = thick[0] if thick else None
    out = {"fuel_material": None, "sample_geometry": None, "rod_diameter_mm": None, "basis": "no entry applies",
           "not_in_cell": False}
    entry = None
    for e in params.get("entries", []):
        if e.get("after_thickness") and thickness is not None:
            continue
        if all(str(w).lower() in low for w in e.get("words", [])):
            entry = e
            break
    if entry is not None:
        out.update(fuel_material=entry.get("fuel_material"), sample_geometry=entry.get("sample_geometry"),
                   not_in_cell=bool(entry.get("not_in_cell")), basis="entry '%s'" % "' + '".join(entry.get("words", [])))
        if entry.get("rod"):
            for pattern, inches in (params.get("rod_inches") or {}).items():
                if re.search(pattern, cell):
                    out["rod_diameter_mm"] = float(inches) * 25.4
                    out["rod_basis"] = "rod_inches '%s' = %s in" % (pattern, inches)
                    break
    elif thickness is not None and params.get("thickness"):
        th = params["thickness"]
        out.update(fuel_material=th.get("fuel_material"), basis="thickness rule (%g mm)" % thickness,
                   sample_geometry=th.get("below") if thickness < th.get("limit_mm", 0) else th.get("from"),
                   not_in_cell=str(th.get("fuel_material", "")).lower() not in low)
    if out["sample_geometry"] is None:
        for word, shape in (params.get("shape_words") or {}).items():
            if str(word).lower() in low:
                out["sample_geometry"] = shape
                out["shape_basis"] = "shape word '%s'" % word
                break
    return out



def number_tokens(cell):
    """Numbers literally written in the cell: value, position, text and the unit written after it."""
    toks = []
    for m in _NUM_TOKEN.finditer(cell):
        unit = _UNIT_AFTER.match(cell[m.end():])
        toks.append({"v": float(m.group(0)), "s": m.start(), "e": m.end(), "txt": m.group(0),
                     "unit": unit.group(1).lower() if unit else None,
                     "label": bool(_LABEL_BEFORE.search(cell[:m.start()]))})
    return toks


def fraction_tokens(cell):
    toks = []
    for m in _FRACTION.finditer(cell):
        if int(m.group(2)) == 0:
            continue
        unit = _UNIT_AFTER.match(cell[m.end():])
        toks.append({"v": int(m.group(1)) / int(m.group(2)), "txt": m.group(0),
                     "unit": unit.group(1).lower() if unit else None})
    return toks


def length_factor(unit_name, var_unit):
    """Factor from a written length unit to the variable's unit (mm or cm), or None."""
    if unit_name not in LENGTH_TO_MM or var_unit not in ("mm", "cm"):
        return None
    return LENGTH_TO_MM[unit_name] / LENGTH_TO_MM[var_unit]


def keyword_vocabulary(variables_spec, variable):
    """Categories with the cell keywords listed in the variable's meaning, e.g. flow_event: unit
    'extinction | blowoff | ...' and meaning '... "ext" / "extinguished", "blowoff", ...' in the same
    order (keywords of one category are separated by '/', categories by ',')."""
    d = variables_spec["variables"].get(variable) or {}
    cats = [c.strip() for c in d.get("unit", "").split("|")]
    groups = []
    for part in re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', d.get("meaning", "")):
        words = re.findall(r'"([^"]+)"', part)
        if words:
            groups.append(words)
    if len(cats) > 1 and len(cats) == len(groups):
        return dict(zip(cats, groups))
    return {}


def keyword_categories(ctx, variable, cell):
    """Categories whose keywords (variables.json) are written in the cell."""
    words = keyword_vocabulary(ctx.spec("variables"), variable)
    return [cat for cat, keys in words.items() if any(k.lower() in cell.lower() for k in keys)]


def classify(cell, value, variable, col, ctx):
    """How a pipeline value relates to the raw cell text. Returns (class, note)."""
    if cell == "":
        return "empty_cell", ""
    params = col.get("params") or {}
    var_unit = ctx.var_unit.get(variable, "")
    v = fnum(value)
    c = fnum(cell)
    if cell.lower() == value.lower():
        return "exact", ""
    if col.get("rule") == "sample_keywords" and variable in ("fuel_material", "sample_geometry", "rod_diameter_mm"):
        reading = sample_keywords_reading(cell, params)
        want = reading[variable]
        if variable == "rod_diameter_mm":
            if want is not None and near(want, v, ROUND_TOL):
                return "declared_factor", reading["rod_basis"] + " x 25.4"
        elif want is not None and str(want).lower() == value.lower():
            if variable == "fuel_material" and reading["not_in_cell"]:
                return "declared_exception", "material_from_readme|sample_keywords " + reading["basis"]
            basis = reading["basis"] if variable == "fuel_material" or "shape_basis" not in reading else reading["shape_basis"]
            return "vocabulary", "sample_keywords " + basis
        return "spec_rule_gives_other_value", "sample_keywords (%s) gives %s" % (
            reading["basis"], "no value" if want is None else repr(want))
    if col.get("rule") == "o2_text" and variable == "o2_pct" and len(number_tokens(cell)) >= 2:
        # sources.json '_meta.documented_start': a two-number cell gives a value only if its exact text is listed
        entry = (params.get("documented_start") or {}).get(cell)
        if entry is None:
            return "two_number_cell_not_documented", ""
        written = [t["v"] for t in number_tokens(cell)]
        if v is not None and close(fnum(entry.get("value")), v) and any(close(w, v) for w in written) and \
                entry.get("reference_item") in ctx.reference_items:
            return "declared_exception", "oxygen_start_named_in_publication|documented_start: %s" % entry["reference_item"]
        return "spec_rule_gives_other_value", "documented_start gives %s (%s)" % (entry.get("value"), entry.get("reference_item"))
    if v is not None:
        if c is not None and close(c, v):
            return "exact", ""
        factor = params.get("factor")
        toks = number_tokens(cell)
        if c is not None and factor in (None, 1) and near(c, v, ROUND_TOL):
            return "exact", "rounded"
        declared = []
        if factor not in (None, 1):
            declared.append(("factor %s" % factor, float(factor), None))
        if params.get("default_unit") or params.get("out"):
            f = length_factor(params.get("default_unit"), params.get("out") or var_unit)
            if f not in (None, 1.0):
                declared.append(("%s to %s" % (params.get("default_unit"), params.get("out") or var_unit),
                                 f, params.get("default_unit")))
        for name, f, unit in declared:
            for t in toks:
                if unit is not None and t["unit"] not in (None, unit):
                    continue          # the cell states another unit: the default does not apply
                if near(t["v"] * f, v, ROUND_TOL):
                    return "declared_factor", name
        direct = [t for t in toks if near(t["v"], v, ROUND_TOL if c is None else 1e-12)]
        if direct:
            if factor not in (None, 1):
                return "declared_factor_not_applied", "factor %s" % factor
            if all(t["label"] for t in direct):
                return "reference_label_number", ""
            if all(length_factor(t["unit"], var_unit) not in (None, 1.0) for t in direct):
                return "unit_ignored", "%s written, variable is in %s" % (direct[0]["unit"], var_unit)
            lead = any(re.match(r"0\d", t["txt"]) for t in direct)
            distinct = sorted({t["v"] for t in toks})
            if len(distinct) == 1:
                return "number_in_text", "leading zero in the cell" if lead else ""
            which = []
            if close(toks[0]["v"], v):
                which.append("first")
            if close(distinct[0], v):
                which.append("minimum")
            if close(toks[-1]["v"], v):
                which.append("last")
            return "one_of_several_numbers", "+".join(which) or "other"
        fracs = fraction_tokens(cell)
        for t in toks + fracs:
            f = length_factor(t["unit"], var_unit)
            if f not in (None, 1.0) and near(t["v"] * f, v, ROUND_TOL):
                return "unit_in_cell", "%s to %s" % (t["unit"], var_unit)
        if var_unit in ("mm", "cm"):
            for t in toks + fracs:
                for unit_name in ("inch", "cm", "mm", "micron", "m"):
                    f = length_factor(unit_name, var_unit)
                    if f != 1.0 and near(t["v"] * f, v, ROUND_TOL):
                        return "assumed_unit", "%s (not written after '%s')" % (unit_name, t["txt"])
        values = [t["v"] for t in toks]
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                if values[i] != values[j] and near((values[i] + values[j]) / 2, v, ROUND_TOL):
                    return "computed_midpoint", "(%s + %s) / 2" % (toks[i]["txt"], toks[j]["txt"])
        return "unexplained", ""
    # text value
    mapping = {str(k).strip().lower(): str(val) for k, val in (params.get("map") or {}).items()}
    if mapping.get(cell.lower(), None) is not None and mapping[cell.lower()].lower() == value.lower():
        return "vocabulary", "sources.json map"
    if value in keyword_categories(ctx, variable, cell):
        hit = [k for k in keyword_vocabulary(ctx.spec("variables"), variable)[value] if k.lower() in cell.lower()]
        return "vocabulary", "variables.json keyword '%s'" % hit[0]
    if value.lower() in cell.lower():
        return "text_in_cell", ""
    if variable == "fuel_material":
        for m in ctx.spec("materials")["materials"]:
            aliases = [a.strip().lower() for a in m.get("aliases", [])]
            if value.strip().lower() in aliases:
                names = aliases + [m["id"].replace("_", " ").lower()]
                if any(n in cell.lower() for n in names):
                    return "material_alias_in_cell", m["id"]
    return "category_not_in_cell", ""


def column_spec(source, column, variable):
    """The sources.json column entry for a raw column header and a target variable."""
    for col in source.get("columns", []):
        if col["from"].strip() == column.strip():
            targets = col["to"] if isinstance(col["to"], list) else [col["to"]]
            if variable in targets:
                return col
    return None


def trace_rows(ctx):
    """Every values_long row with a real source column, with its raw cell and class."""
    def load():
        out = []
        for r in ctx.table("values_long.csv"):
            col_name = r["source_column"]
            if col_name.startswith("("):
                continue
            item = {"row": r, "cell": None, "cls": None, "note": "", "problem": None}
            source = ctx.source_by_file.get(r["source_file"])
            if source is None or not os.path.exists(os.path.join(RAW, r["source_file"])):
                item["problem"] = "source_file is not a table of sources.json"
            else:
                table = ctx.raw(r["source_file"])
                header = table[0]
                row_no = fnum(r["source_row"])
                col = column_spec(source, col_name, r["variable"])
                if col is None:
                    item["problem"] = "sources.json does not map this column to this variable"
                elif header.count(col_name) != 1:
                    item["problem"] = "column header found %d times in the raw file" % header.count(col_name)
                elif row_no is None or row_no != int(row_no) or not 2 <= int(row_no) <= len(table):
                    item["problem"] = "source_row outside the raw file"
                else:
                    raw_row = table[int(row_no) - 1]
                    idx = header.index(col_name)
                    item["cell"] = raw_row[idx] if idx < len(raw_row) else ""
                    item["cls"], item["note"] = classify(item["cell"], r["value"], r["variable"], col, ctx)
                    kind = None
                    if item["cls"] == "declared_exception":
                        kind, _, item["note"] = item["note"].partition("|")
                    elif item["cell"] == "" and col_name in [c.strip() for c in source.get("fill_down", [])]:
                        above = int(row_no) - 1
                        while above >= 2 and (idx >= len(table[above - 1]) or table[above - 1][idx] == ""):
                            above -= 1
                        if above >= 2:
                            cls_above, _ = classify(table[above - 1][idx], r["value"], r["variable"], col, ctx)
                            item["note"] = "sources.json fill_down: row %d holds '%s' (%s)" % (
                                above, table[above - 1][idx], cls_above)
                            if cls_above == "exact":
                                kind = "cell_of_row_above"
                    if kind:
                        flags = split_list((ctx.tests_by_id.get(r["test_id"]) or {}).get("flags", ""))
                        flag = "%s:%s" % (r["variable"], EXCEPTION_FLAGS[kind])
                        item["kind"] = kind
                        item["cls"] = "declared_exception_flagged" if flag in flags else "declared_exception_without_flag"
                        item["note"] = "%s; %s; flag %s %s" % (kind, item["note"], flag,
                                                              "present" if flag in flags else "MISSING")
            out.append(item)
        return out
    return ctx._get("trace_rows", load)


@check("A1_trace_source_cells",
       "Every value with a real source column is found in its raw NASA cell and is explained by a rule that "
       "the spec states (exact copy, declared factor, number in the cell text, spec vocabulary), or is one of "
       "the exceptions README declares, exactly as declared and with its flag on the test.")
def check_a1(ctx):
    res = Result()
    per_class = {}
    per_var = {}
    examples = {}
    leading = []
    flagged = 0
    kinds = {}
    for item in trace_rows(ctx):
        r = item["row"]
        res.checked += 1
        key = {"file": r["source_file"], "row": r["source_row"], "column": r["source_column"],
               "variable": r["variable"], "raw_cell": item["cell"], "value": r["value"]}
        if item["problem"]:
            res.fail(problem=item["problem"], **key)
            per_class["not_located"] = per_class.get("not_located", 0) + 1
            continue
        cls = item["cls"]
        per_class[cls] = per_class.get(cls, 0) + 1
        per_var.setdefault(r["variable"], {})
        per_var[r["variable"]][cls] = per_var[r["variable"]].get(cls, 0) + 1
        if cls == "declared_exception_flagged":
            kinds[item["kind"]] = kinds.get(item["kind"], 0) + 1
        if cls != "exact":
            ex = examples.setdefault(cls, [])
            if len(ex) < 10 and not any(e["raw_cell"] == item["cell"] and e["variable"] == r["variable"] for e in ex):
                ex.append(dict(key, note=item["note"]))
        if cls in FAIL_CLASSES:
            flags = [f for f in split_list((ctx.tests_by_id.get(r["test_id"]) or {}).get("flags", ""))
                     if f.split(":")[0] == r["variable"]]
            flagged += 1 if flags else 0
            res.fail(**dict(key, **{"class": cls, "note": item["note"], "test_id": r["test_id"],
                                    "pipeline_flags_on_variable": ";".join(flags)}))
        if item["note"] == "leading zero in the cell":
            leading.append(key)
    res.failures.sort(key=lambda f: (list(FAIL_CLASSES).index(f.get("class")) if f.get("class") in FAIL_CLASSES else -1,
                                     f["file"], int(fnum(f["row"]) or 0), f["variable"]))
    res.numbers = {"values_checked": res.checked}
    for cls in list(PASS_CLASSES) + list(FAIL_CLASSES) + ["not_located"]:
        if per_class.get(cls) or cls in ("exact", "declared_factor", "number_in_text", "vocabulary", "unexplained"):
            res.numbers[cls] = per_class.get(cls, 0)
    res.details = {
        "class_meaning": dict(PASS_CLASSES, **FAIL_CLASSES),
        "classes_that_fail": sorted(FAIL_CLASSES),
        "per_variable": {v: dict(sorted(c.items())) for v, c in sorted(per_var.items())},
        "examples_per_class": {k: examples[k] for k in sorted(examples)},
        "failures_per_class": {c: per_class[c] for c in FAIL_CLASSES if per_class.get(c)},
    }
    # every failing row is listed in full in the report, grouped by class
    res.details["all_failing_rows"] = res.failures
    res.details["numbers_written_with_a_leading_zero"] = {
        "note": "Copied as written (for example '037 mm' read as 37). Not a failure of the trace; a human "
                "should look at the NASA page, because the source cell may be a typing error.",
        "rows": leading}
    res.numbers["declared_exception_flagged_per_kind"] = dict(sorted(kinds.items()))
    res.numbers["numbers_written_with_a_leading_zero"] = len(leading)
    res.numbers["failing_values_that_the_pipeline_flags"] = flagged
    return res


@check("A2_tests_source_rows",
       "Every test names an existing raw file and a row inside it, and no two tests share a raw row.")
def check_a2(ctx):
    res = Result()
    seen = {}
    for t in ctx.tests:
        res.checked += 1
        key = {"test_id": t["test_id"], "source_file": t["source_file"], "source_row": t["source_row"]}
        if not os.path.exists(os.path.join(RAW, t["source_file"])) or t["source_file"] not in ctx.source_by_file:
            res.fail(problem="source_file missing or not in sources.json", **key)
            continue
        n = fnum(t["source_row"])
        if n is None or n != int(n) or not 2 <= int(n) <= len(ctx.raw(t["source_file"])):
            res.fail(problem="source_row outside the file", **key)
            continue
        source = ctx.source_by_file[t["source_file"]]
        if t["source_id"] != source["id"] or t["investigation_id"] != source["investigation_id"]:
            res.fail(problem="source_id or investigation_id differs from sources.json", **key)
        pair = (t["source_file"], int(n))
        if pair in seen:
            res.fail(problem="raw row shared with test %s" % seen[pair], **key)
        seen[pair] = t["test_id"]
    ids = [t["test_id"] for t in ctx.tests]
    dup = sorted({i for i in ids if ids.count(i) > 1}) if len(set(ids)) != len(ids) else []
    for i in dup:
        res.fail(problem="test_id used by more than one test", test_id=i)
    res.numbers = {"tests": res.checked, "distinct_raw_rows": len(seen)}
    return res


@check("A3_tests_values_consistency",
       "Every non-empty variable cell of tests.csv has exactly one row in values_long.csv with the same value, "
       "unit, file and row, and every values_long row has its cell in tests.csv.")
def check_a3(ctx):
    res = Result()
    variables = ctx.variable_columns
    kinds = {k: d.get("kind") for k, d in ctx.spec("variables")["variables"].items()}
    kinds.update({k: "derived" for k in ctx.spec("variables")["derived"]})
    idx = ctx.values_index
    cells = 0
    for t in ctx.tests:
        for var in variables:
            val = t[var]
            rows = idx.get((t["test_id"], var), [])
            if val == "":
                if rows:
                    res.fail(problem="values_long has a value for an empty tests.csv cell", test_id=t["test_id"],
                             variable=var, values_long=rows[0]["value"])
                continue
            cells += 1
            key = {"test_id": t["test_id"], "variable": var, "tests_csv": val}
            if len(rows) != 1:
                res.fail(problem="%d rows in values_long" % len(rows), **key)
                continue
            r = rows[0]
            if r["value"] != val and not close(fnum(r["value"]), fnum(val)):
                res.fail(problem="value differs", values_long=r["value"], **key)
            elif (r["source_file"], r["source_row"], r["investigation_id"]) != \
                    (t["source_file"], t["source_row"], t["investigation_id"]):
                res.fail(problem="file, row or investigation differs", **key)
            elif r["unit"] != ctx.var_unit.get(var, "") or r["kind"] != kinds.get(var):
                res.fail(problem="unit or kind differs from variables.json", unit=r["unit"], kind=r["kind"], **key)
    known = set(variables)
    derived = ctx.spec("variables")["derived"]
    for (test_id, var), rows in idx.items():
        if test_id not in ctx.tests_by_id or var not in known:
            res.fail(problem="values_long row without a test or a tests.csv column", test_id=test_id, variable=var)
        for r in rows:
            col = r["source_column"]
            if col.startswith("(") and col != CONSTANT_MARK and not (col == MATERIAL_MARK and var == "material_id") \
                    and not (var in derived and col == "(derived: %s)" % derived[var]["formula"]):
                res.fail(problem="source_column in parentheses is not a constant, the material vocabulary or the "
                                 "formula of the variable", test_id=test_id, variable=var, source_column=col)
    res.checked = cells
    res.numbers = {"non_empty_cells": cells, "values_long_rows": len(ctx.table("values_long.csv"))}
    return res


def fill_test_id(template, header, raw_row, row_no):
    def repl(m):
        name = m.group(1)
        if name == "row":
            return str(row_no)
        return raw_row[header.index(name)] if name in header and header.index(name) < len(raw_row) else ""
    return re.sub(r"\{([^}]*)\}", repl, template)


@check("A4_raw_rows_are_tests",
       "In every test-level table, each raw row that sources.json keeps (all 'require' columns filled, no "
       "'exclude' rule, not a cell-for-cell repeat of an earlier row) is exactly one test, no other row is a "
       "test, and the test id is the 'test_id' template filled from that row.")
def check_a4(ctx):
    res = Result()
    by_file = {}
    for t in ctx.tests:
        by_file.setdefault(t["source_file"], {})[int(fnum(t["source_row"]) or 0)] = t
    not_combustion = []
    squeezed = 0
    left_out = {"excluded": 0, "repeating_an_earlier_row": 0}
    for s in ctx.sources:
        if "columns" not in s:
            if s["file"] in by_file:
                res.fail(problem="table declared not test-level has tests", source=s["id"])
            continue
        table = ctx.raw(s["file"])
        header = table[0]
        require = [c.strip() for c in s.get("require", [])]
        expected = {}
        first_seen, repeated, excluded = {}, {}, []
        for i, raw_row in enumerate(table[1:], start=2):
            if not any(raw_row):
                continue
            if any(c not in header or header.index(c) >= len(raw_row) or raw_row[header.index(c)] == "" for c in require):
                continue
            if any(rule["column"].strip() in header and header.index(rule["column"].strip()) < len(raw_row)
                   and raw_row[header.index(rule["column"].strip())] == str(rule["equals"]).strip()
                   for rule in s.get("exclude", [])):
                excluded.append(i)
                continue
            if tuple(raw_row) in first_seen:
                repeated[i] = first_seen[tuple(raw_row)]
                continue
            first_seen[tuple(raw_row)] = i
            expected[i] = raw_row
        left_out["excluded"] += len(excluded)
        left_out["repeating_an_earlier_row"] += len(repeated)
        if ctx.has("run_report.json"):
            rep = (ctx.json("run_report.json").get("sources") or {}).get(s["id"]) or {}
            if "rows_excluded" in rep and sorted(x.get("source_row") for x in rep["rows_excluded"]) != excluded:
                res.fail(problem="run_report.json rows_excluded differs", source=s["id"], recomputed=excluded)
            if "rows_repeating_an_earlier_row" in rep and \
                    {x.get("source_row"): x.get("same_as_row") for x in rep["rows_repeating_an_earlier_row"]} != repeated:
                res.fail(problem="run_report.json rows_repeating_an_earlier_row differs", source=s["id"],
                         recomputed=sorted(repeated.items())[:10])
        have = by_file.get(s["file"], {})
        res.checked += len(expected)
        for i in sorted(set(expected) - set(have)):
            res.fail(problem="raw row is not a test", source=s["id"], source_row=i, raw=" | ".join(expected[i])[:160])
        for i in sorted(set(have) - set(expected)):
            res.fail(problem="test from a row that is empty or lacks a required column", source=s["id"],
                     source_row=i, test_id=have[i]["test_id"])
        for i in sorted(set(have) & set(expected)):
            base = fill_test_id(s["test_id"], header, expected[i], i)
            tid = have[i]["test_id"]
            flagged = "test_id:duplicate_in_source" in split_list(have[i]["flags"])
            squeezed += 1 if (re.sub(r"\s+", "", base) != base) else 0
            base = re.sub(r"\s+", "", base)
            if tid != base and tid != "%s@row%d" % (base, i):
                res.fail(problem="test_id is not the template filled from the row", source=s["id"], source_row=i,
                         test_id=tid, expected=base)
            elif (tid != base) != flagged:
                res.fail(problem="'@row' suffix and flag test_id:duplicate_in_source do not agree",
                         source=s["id"], source_row=i, test_id=tid)
            if re.search(r"\{[^}]+\}", s["test_id"]) and base == re.sub(r"\{[^}]*\}", "", s["test_id"]):
                not_combustion.append({"source": s["id"], "source_row": i, "test_id": tid,
                                       "raw": " | ".join(expected[i])[:160]})
    res.numbers = {"raw_rows_expected_as_tests": res.checked, "tests": len(ctx.tests),
                   "tests_with_empty_id_cell": len(not_combustion), "ids_with_whitespace_removed": squeezed,
                   "rows_left_out_by_exclude": left_out["excluded"],
                   "rows_left_out_as_repeats": left_out["repeating_an_earlier_row"]}
    res.details = {"tests_with_empty_id_cell": not_combustion,
                   "note": "A test whose id cell is empty in the raw table is listed here for a human to look at; "
                           "it is not counted as a failure because no spec rule excludes such a row. "
                           "Test ids are compared after removing whitespace inside the raw id cell; the spec "
                           "does not state that step."}
    return res


@check("A5_unread_cells_flagged",
       "A non-empty raw cell of a mapped column that left its variable empty carries a flag "
       "'<variable>:<reason>' (README: a cell that a rule cannot read stays empty and gets a flag).")
def check_a5(ctx):
    res = Result()
    silent, markers = {}, {}
    no_keyword = 0
    for t in ctx.tests:
        source = ctx.source_by_file.get(t["source_file"])
        if not source or "columns" not in source:
            continue
        table = ctx.raw(t["source_file"])
        header = table[0]
        n = int(fnum(t["source_row"]) or 0)
        if not 2 <= n <= len(table):
            continue
        raw_row = table[n - 1]
        flag_vars = {f.split(":")[0] for f in split_list(t["flags"])}
        for col in source["columns"]:
            name = col["from"].strip()
            if name not in header or header.index(name) >= len(raw_row):
                continue
            cell = raw_row[header.index(name)]
            if cell == "":
                continue
            targets = col["to"] if isinstance(col["to"], list) else [col["to"]]
            res.checked += 1
            if all(keyword_vocabulary(ctx.spec("variables"), v) for v in targets):
                # a column read only for the keywords of variables.json: nothing to read without one
                for v in targets:
                    found = keyword_categories(ctx, v, cell)
                    if not found:
                        no_keyword += 1
                    elif t.get(v, "") not in found and v not in flag_vars:
                        res.fail(test_id=t["test_id"], file=t["source_file"], row=t["source_row"], column=name,
                                 raw_cell=cell, variables=v, value=t.get(v, ""), keyword_says=";".join(found),
                                 flags=t["flags"])
                continue
            if all(t.get(v, "") == "" for v in targets) and not (flag_vars & set(targets)):
                k = (source["id"], name, cell)
                if not re.search(r"[A-Za-z0-9]", cell) or cell.lower() in NO_VALUE_MARKERS:
                    markers[k] = markers.get(k, 0) + 1
                    continue
                res.fail(test_id=t["test_id"], file=t["source_file"], row=t["source_row"], column=name,
                         raw_cell=cell, variables=";".join(targets), flags=t["flags"])
                silent[k] = silent.get(k, 0) + 1
    res.numbers = {"non_empty_mapped_cells": res.checked, "left_empty_without_flag": len(res.failures),
                   "no_value_markers_without_flag": sum(markers.values()),
                   "keyword_column_cells_without_keyword": no_keyword}
    as_list = lambda d: [{"source": k[0], "column": k[1], "raw_cell": k[2], "tests": n} for k, n in sorted(d.items())]
    res.details = {"distinct_cells_left_empty_without_flag": as_list(silent),
                   "no_value_markers_without_flag": as_list(markers),
                   "note": "Cells that hold no letter or digit (a dash) or only 'n/a' are counted apart and do not "
                           "fail the check: they say that there is no value. The pipeline is not consistent "
                           "here: the same kind of cell gets a flag in some tables and none in others."}
    return res


def expected_flow_numbers(cell):
    """flow_cms and flow_min_cms as their meanings in variables.json read a flow cell:
    flow_cms is 'the number the flow cell starts with'; flow_min_cms is the 'lowest flow speed written in
    the cell', 'not read where the cell also holds fan potentiometer settings or bracketed numbers'."""
    toks = number_tokens(cell)
    starts = toks[0]["v"] if toks and cell[:toks[0]["s"]].strip() in ("", "~") else None
    blocked = bool(re.search(r"[(\[][^)\]]*\d|\bpots?\b", cell, re.I))
    lowest = None if (blocked or not toks) else min(t["v"] for t in toks)
    return {"flow_cms": starts, "flow_min_cms": lowest}


@check("A6_number_chosen_from_cell",
       "In a column mapped to both flow_cms and flow_min_cms, flow_cms is the number the cell starts with and "
       "flow_min_cms the lowest number written, and flow_min_cms is empty where the cell holds potentiometer "
       "settings or bracketed numbers (the meanings in variables.json), unless a flag on the variable says otherwise.")
def check_a6(ctx):
    res = Result()
    flagged = 0
    meanings = {v: ctx.spec("variables")["variables"].get(v, {}).get("meaning", "") for v in ("flow_cms", "flow_min_cms")}
    for t in ctx.tests:
        source = ctx.source_by_file.get(t["source_file"]) or {}
        for col in source.get("columns", []):
            targets = col["to"] if isinstance(col["to"], list) else [col["to"]]
            if "flow_cms" not in targets or "flow_min_cms" not in targets:
                continue
            table = ctx.raw(t["source_file"])
            header = table[0]
            name = col["from"].strip()
            n = int(fnum(t["source_row"]) or 0)
            if name not in header or not 2 <= n <= len(table) or header.index(name) >= len(table[n - 1]):
                continue
            cell = table[n - 1][header.index(name)]
            if not number_tokens(cell):
                continue
            expected = expected_flow_numbers(cell)
            flag_vars = {f.split(":")[0] for f in split_list(t["flags"])}
            for var in ("flow_cms", "flow_min_cms"):
                res.checked += 1
                got = fnum(t.get(var, ""))
                want = expected[var]
                if (got is None and want is None) or close(got, want):
                    continue
                if var in flag_vars:
                    flagged += 1
                    continue
                res.fail(file=t["source_file"], row=t["source_row"], column=name, variable=var, raw_cell=cell,
                         value=t.get(var, ""), expected_by_meaning="" if want is None else want,
                         flags=t["flags"])
    res.numbers = {"cell_x_variable": res.checked, "differs_with_flag": flagged, "differs_without_flag": len(res.failures)}
    res.details = {"meanings_applied": meanings,
                   "note": "How the engine chooses among the numbers of a cell is written in pipeline/rules.py, "
                           "which this check does not read. It applies the two meanings literally."}
    return res


@check("A7_sample_keywords",
       "For every test of a column read with rule 'sample_keywords', fuel_material, sample_geometry and "
       "rod_diameter_mm in tests.csv are what the entries of sources.json give for the cell (also where they "
       "give no value), and the flag 'not_written_in_cell_named_in_readme' is on exactly the tests whose "
       "material is not written in the cell.")
def check_a7(ctx):
    res = Result()
    seen = False
    per = {}
    for t in ctx.tests:
        source = ctx.source_by_file.get(t["source_file"]) or {}
        for col in source.get("columns", []):
            if col.get("rule") != "sample_keywords":
                continue
            seen = True
            table = ctx.raw(t["source_file"])
            header = table[0]
            name = col["from"].strip()
            n = int(fnum(t["source_row"]) or 0)
            if name not in header or not 2 <= n <= len(table) or header.index(name) >= len(table[n - 1]):
                continue
            cell = table[n - 1][header.index(name)]
            reading = sample_keywords_reading(cell, col.get("params") or {})
            key = {"file": t["source_file"], "row": t["source_row"], "test_id": t["test_id"], "raw_cell": cell}
            for var in ("fuel_material", "sample_geometry", "rod_diameter_mm"):
                res.checked += 1
                got, want = t.get(var, ""), reading[var]
                same = (got == "" and want is None) or (want is not None and (
                    near(fnum(got), want, ROUND_TOL) if var == "rod_diameter_mm" else got.lower() == str(want).lower()))
                if not same:
                    res.fail(variable=var, value=got, spec_gives="" if want is None else want, basis=reading["basis"], **key)
                elif got != "":
                    per[var] = per.get(var, 0) + 1
            flag = "fuel_material:" + EXCEPTION_FLAGS["material_from_readme"] in split_list(t["flags"])
            expect = bool(reading["not_in_cell"] and reading["fuel_material"])
            if flag != expect:
                res.fail(variable="fuel_material", problem="flag %s although the material %s written in the cell" % (
                    "present" if flag else "missing", "is" if not expect else "is not"), basis=reading["basis"], **key)
    if not seen:
        raise Skip("no column of sources.json uses rule 'sample_keywords'")
    res.numbers = {"cell_x_variable": res.checked, "values_that_follow_from_the_spec": dict(sorted(per.items()))}
    return res


def cell_of(ctx, test, column):
    """The raw cell of a test in a column, or None when it cannot be located."""
    table = ctx.raw(test["source_file"])
    header = table[0]
    name = column.strip()
    n = int(fnum(test["source_row"]) or 0)
    if name not in header or not 2 <= n <= len(table) or header.index(name) >= len(table[n - 1]):
        return None
    return table[n - 1][header.index(name)]


@check("A8_oxygen_two_number_cells",
       "An oxygen cell with two numbers gives a value only if 'documented_start' lists its exact text: then "
       "o2_pct is the listed number, which is one of the two written, and the test carries the flag "
       "'range_in_source_start_value_named_in_publication'; otherwise o2_pct is empty with the flag "
       "'range_in_source_start_value_not_documented'. o2_range_as_written holds the cell text in both cases.")
def check_a8(ctx):
    res = Result()
    named = "o2_pct:" + EXCEPTION_FLAGS["oxygen_start_named_in_publication"]
    not_documented = "o2_pct:range_in_source_start_value_not_documented"
    seen = False
    numbers = {"two_number_cells": 0, "listed_in_documented_start": 0, "not_listed": 0}
    for s in ctx.sources:
        for col in s.get("columns", []):
            if col.get("rule") != "o2_text":
                continue
            seen = True
            for text, entry in ((col.get("params") or {}).get("documented_start") or {}).items():
                key = {"source_id": s["id"], "documented_start": text}
                if not any(close(t["v"], fnum(entry.get("value"))) for t in number_tokens(text)):
                    res.fail(problem="listed value is not one of the numbers of the cell text", value=entry.get("value"), **key)
                if entry.get("reference_item") not in ctx.reference_items:
                    res.fail(problem="reference_item is not in references.json", reference_item=entry.get("reference_item"), **key)
    for t in ctx.tests:
        source = ctx.source_by_file.get(t["source_file"]) or {}
        for col in source.get("columns", []):
            if col.get("rule") != "o2_text":
                continue
            cell = cell_of(ctx, t, col["from"])
            if cell is None:
                continue
            res.checked += 1
            targets = col["to"] if isinstance(col["to"], list) else [col["to"]]
            flags = split_list(t["flags"])
            key = {"file": t["source_file"], "row": t["source_row"], "test_id": t["test_id"], "raw_cell": cell,
                   "o2_pct": t.get("o2_pct", ""), "flags": ";".join(f for f in flags if f.startswith("o2_pct:"))}
            two = len(number_tokens(cell)) >= 2
            if "o2_range_as_written" in targets and t.get("o2_range_as_written", "") != (cell if two else ""):
                res.fail(problem="o2_range_as_written is not the cell text of a two-number cell",
                         o2_range_as_written=t.get("o2_range_as_written", ""), **key)
            if not two:
                if named in flags or not_documented in flags:
                    res.fail(problem="two-number flag on a cell that does not hold two numbers", **key)
                continue
            numbers["two_number_cells"] += 1
            entry = ((col.get("params") or {}).get("documented_start") or {}).get(cell)
            if entry is not None:
                numbers["listed_in_documented_start"] += 1
                if not close(fnum(t.get("o2_pct", "")), fnum(entry.get("value"))):
                    res.fail(problem="o2_pct is not the number documented_start names", documented=entry.get("value"), **key)
                if named not in flags or not_documented in flags:
                    res.fail(problem="flags of a listed two-number cell are wrong", expected=named, **key)
            else:
                numbers["not_listed"] += 1
                if t.get("o2_pct", "") != "":
                    res.fail(problem="value from a two-number cell that documented_start does not list", **key)
                if not_documented not in flags or named in flags:
                    res.fail(problem="flags of an unlisted two-number cell are wrong", expected=not_documented, **key)
    if not seen:
        raise Skip("no column of sources.json uses rule 'o2_text'")
    res.numbers = dict(numbers, oxygen_cells=res.checked)
    return res


# ----------------------------------------------------------------------------
# B. constants, derived values, material ids
# ----------------------------------------------------------------------------

@check("B1_constants",
       "Values marked '(constant in sources.json)' equal the constant declared for the test's source, and "
       "every declared constant is recorded for every test of the source.")
def check_b1(ctx):
    res = Result()
    idx = ctx.values_index
    for r in ctx.table("values_long.csv"):
        if r["source_column"] != CONSTANT_MARK:
            continue
        res.checked += 1
        source = ctx.source_by_file.get(r["source_file"]) or {}
        declared = (source.get("constants") or {}).get(r["variable"])
        if declared is None or str(declared) != r["value"]:
            res.fail(test_id=r["test_id"], variable=r["variable"], value=r["value"],
                     declared=declared, source=source.get("id"))
    missing = 0
    for t in ctx.tests:
        source = ctx.source_by_id.get(t["source_id"]) or {}
        for var, declared in (source.get("constants") or {}).items():
            rows = idx.get((t["test_id"], var), [])
            if len(rows) != 1 or rows[0]["source_column"] != CONSTANT_MARK or t.get(var) != str(declared):
                missing += 1
                res.fail(problem="declared constant not recorded as such", test_id=t["test_id"], variable=var,
                         declared=declared, tests_csv=t.get(var))
    res.numbers = {"constant_values": res.checked, "declared_constants_missing": missing}
    return res


_EXPR_OK = re.compile(r"^[A-Za-z0-9_ .+\-*/()<>=]+$")


def evaluate(expr, names):
    """Arithmetic or comparison of variables.json; None when an input is empty."""
    if not _EXPR_OK.match(expr):
        raise ValueError("expression not understood: " + expr)
    used = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr)) - {"e"}
    env = {}
    for name in used:
        if names.get(name) is None:
            return None
        env[name] = names[name]
    try:
        return eval(expr, {"__builtins__": {}}, env)      # noqa: S307 - whitelisted characters only
    except ZeroDivisionError:
        return None


@check("B2_derived_values",
       "Every derived value equals its formula in variables.json recomputed from the test's own recorded "
       "inputs (tolerance 1e-4), is absent exactly when an input is empty or a skip_if holds, and carries "
       "the flags the spec names.")
def check_b2(ctx):
    res = Result()
    derived = ctx.spec("variables")["derived"]
    idx = ctx.values_index
    max_dev = 0.0
    for t in ctx.tests:
        actual_flags = {f for f in split_list(t["flags"]) if f.split(":")[0] in derived}
        expected_flags = set()
        for var, d in derived.items():
            names = {c: fnum(t.get(c, "")) for c in ctx.variable_columns}
            value = evaluate(d["formula"], names)
            skipped = False
            if value is not None:
                for rule in d.get("skip_if", []):
                    if evaluate(rule["expr"], names):
                        skipped = True
                        if rule.get("flag"):
                            expected_flags.add("%s:%s" % (var, rule["flag"]))
                        break
            if value is None or skipped:
                expected = None
            else:
                expected = value
                for rule in d.get("flag_if", []):
                    if evaluate(rule["expr"], dict(names, value=value)) and rule.get("flag"):
                        expected_flags.add("%s:%s" % (var, rule["flag"]))
            recorded = fnum(t.get(var, ""))
            res.checked += 1
            key = {"test_id": t["test_id"], "variable": var, "formula": d["formula"], "recorded": t.get(var, ""),
                   "inputs": {k: t.get(k, "") for k in sorted(set(re.findall(r"[a-z_][a-z0-9_]*", d["formula"])) - {"e"})}}
            if expected is None and recorded is not None:
                res.fail(problem="value recorded although an input is empty or a skip_if holds", **key)
            elif expected is not None and recorded is None:
                res.fail(problem="value missing", recomputed=round(expected, 6), **key)
            elif expected is not None:
                max_dev = max(max_dev, abs(expected - recorded))
                if abs(expected - recorded) > DERIVED_TOL:
                    res.fail(problem="value differs", recomputed=round(expected, 6), **key)
            if recorded is not None:
                rows = idx.get((t["test_id"], var), [])
                if len(rows) == 1 and rows[0]["source_column"] != "(derived: %s)" % d["formula"]:
                    res.fail(problem="source_column does not carry the formula of variables.json",
                             source_column=rows[0]["source_column"], **key)
        if expected_flags != actual_flags:
            res.fail(problem="flags of derived variables differ", test_id=t["test_id"],
                     expected=sorted(expected_flags), recorded=sorted(actual_flags))
    res.numbers = {"test_x_formula": res.checked,
                   "derived_values": sum(1 for t in ctx.tests for v in derived if t.get(v, "") != ""),
                   "largest_deviation": round(max_dev, 7)}
    return res


@check("B3_material_id",
       "material_id is the materials.json entry whose aliases contain fuel_material (ignoring case and "
       "surrounding spaces); a name that is not listed has no id and the flag material_id:not_in_vocabulary.")
def check_b3(ctx):
    res = Result()
    alias = {}
    clash = []
    for m in ctx.spec("materials")["materials"]:
        for a in m.get("aliases", []):
            k = a.strip().lower()
            if k in alias and alias[k] != m["id"]:
                clash.append(a)
            alias[k] = m["id"]
    for a in clash:
        res.fail(problem="alias listed for two materials", alias=a)
    idx = ctx.values_index
    with_id = 0
    for t in ctx.tests:
        res.checked += 1
        name = t.get("fuel_material", "")
        expected = alias.get(name.strip().lower(), "") if name else ""
        flag = "material_id:not_in_vocabulary" in split_list(t["flags"])
        key = {"test_id": t["test_id"], "fuel_material": name, "material_id": t.get("material_id", "")}
        if t.get("material_id", "") != expected:
            res.fail(problem="material_id differs", expected=expected, **key)
        elif flag != (name != "" and expected == ""):
            res.fail(problem="flag material_id:not_in_vocabulary wrong", flags=t["flags"], **key)
        if t.get("material_id", ""):
            with_id += 1
            rows = idx.get((t["test_id"], "material_id"), [])
            if len(rows) != 1 or rows[0]["source_column"] != MATERIAL_MARK:
                res.fail(problem="values_long does not mark the id as coming from materials.json", **key)
    res.numbers = {"tests": res.checked, "with_material_id": with_id, "aliases": len(alias)}
    return res


# ----------------------------------------------------------------------------
# C. ranges
# ----------------------------------------------------------------------------

@check("C1_ranges", "No value in tests.csv lies outside the 'ranges' of variables.json.")
def check_c1(ctx):
    res = Result()
    for var, rng in ctx.spec("variables")["ranges"].items():
        if var.startswith("_"):
            continue
        lo, hi = rng
        for t in ctx.tests:
            if t.get(var, "") == "":
                continue
            res.checked += 1
            v = fnum(t[var])
            if v is None or (lo is not None and v < lo) or (hi is not None and v > hi):
                res.fail(test_id=t["test_id"], variable=var, value=t[var], range=rng)
    res.numbers = {"values_checked": res.checked}
    return res


@check("C2_consistency_rules",
       "A raw reading for which a 'consistency' expression of variables.json holds (for example a final "
       "oxygen below 5, or above the initial oxygen + 0.5) has no value in tests.csv and carries "
       "'<variable>:<flag>'; no other reading of the variable was emptied by the rule or carries its flag.")
def check_c2(ctx):
    res = Result()
    rules = (ctx.spec("variables").get("consistency") or {}).get("rules") or []
    if not rules:
        raise Skip("variables.json has no consistency rules")
    held = {"%s:%s" % (r["variable"], r["flag"]): 0 for r in rules}
    by_var = {}
    for r in rules:
        by_var.setdefault(r["variable"], []).append(r)
    for t in ctx.tests:
        source = ctx.source_by_file.get(t["source_file"]) or {}
        flags = split_list(t["flags"])
        names = {c: fnum(t.get(c, "")) for c in ctx.variable_columns}
        for var, var_rules in by_var.items():
            rule_flags = ["%s:%s" % (var, r["flag"]) for r in var_rules]
            # a recorded value must not satisfy any rule
            if t.get(var, "") != "":
                for r in var_rules:
                    if evaluate(r["expr"], names):
                        res.fail(problem="value recorded although the expression holds", test_id=t["test_id"],
                                 variable=var, value=t[var], expr=r["expr"])
            cols = [c for c in source.get("columns", []) if c.get("to") == var]
            if not cols:
                if any(f in flags for f in rule_flags):
                    res.fail(problem="consistency flag on a test whose table has no column for the variable",
                             test_id=t["test_id"], variable=var, flags=t["flags"])
                continue
            cell = cell_of(ctx, t, cols[0]["from"])
            raw = fnum(cell) if cell is not None else None
            if raw is None:
                if any(f in flags for f in rule_flags):
                    res.fail(problem="consistency flag although the raw cell is not a number", test_id=t["test_id"],
                             variable=var, raw_cell=cell, flags=t["flags"])
                continue
            raw *= float((cols[0].get("params") or {}).get("factor", 1))
            res.checked += 1
            key = {"file": t["source_file"], "row": t["source_row"], "test_id": t["test_id"], "variable": var,
                   "raw_cell": cell, "value": t.get(var, ""), "o2_pct": t.get("o2_pct", ""),
                   "flags": ";".join(f for f in flags if f.split(":")[0] == var)}
            first = next((r for r in var_rules if evaluate(r["expr"], dict(names, **{var: raw}))), None)
            other_flags = [f for f in flags if f.split(":")[0] == var and f not in rule_flags]
            if first is not None:
                flag = "%s:%s" % (var, first["flag"])
                held[flag] += 1
                if t.get(var, "") != "" or flag not in flags:
                    res.fail(problem="expression holds for the raw reading but the value is kept or the flag is missing",
                             expr=first["expr"], expected_flag=flag, **key)
            else:
                if any(f in flags for f in rule_flags):
                    res.fail(problem="consistency flag although no expression holds for the raw reading", **key)
                elif t.get(var, "") == "" and not other_flags:
                    res.fail(problem="reading emptied although no expression holds and no other flag explains it", **key)
    res.numbers = {"raw_readings": res.checked, "readings_for_which_a_rule_holds": held}
    return res


# ----------------------------------------------------------------------------
# D. needs
# ----------------------------------------------------------------------------

def in_scope(test, need):
    return all(test.get(k, "") in allowed for k, allowed in (need.get("scope") or {}).items())


def documented_variables(ctx, need, source_id):
    """Required conditions of the need that a document about the whole table meets (needs.json
    'documented_rule'): listed under 'conditions_documented_ok' and present in the table's
    'documented_elsewhere' (sources.json)."""
    source = ctx.source_by_id.get(source_id) or {}
    documented = {e.get("variable") for e in source.get("documented_elsewhere", [])}
    return [v for v in need["conditions_required"] if v in (need.get("conditions_documented_ok") or []) and v in documented]


def has_required(ctx, test, need):
    """Every required condition is recorded for the test, or is met by a document about its table. The
    test still has no value for a documented variable."""
    documented = documented_variables(ctx, need, test.get("source_id", ""))
    return all(test.get(v, "") != "" or v in documented for v in need["conditions_required"])


def has_outcome(test, need):
    return any(test.get(v, "") != "" for v in need["outcomes_any"])


def supported_links(need):
    """Only links with verdict 'supported' are counted (needs.json 'stated_by_rule')."""
    return [s for s in need.get("stated_by", []) if s.get("verdict") == "supported"]


def stated_investigations(need):
    return {s["investigation_id"] for s in supported_links(need)}


def publication_quote(ctx, link):
    item = ctx.reference_items.get(link.get("publication") or "")
    return (item[1].get("quote") or "") if item else ""


def link_rows(ctx):
    """All links of needs.json as the rows objective_links.csv must hold."""
    def load():
        return [{"need_id": n["id"], "investigation_id": s.get("investigation_id", ""),
                 "record_field": s.get("field") or "", "quote": s.get("quote") or "",
                 "publication_item": s.get("publication") or "", "publication_quote": publication_quote(ctx, s),
                 "verdict": s.get("verdict") or ""}
                for n in ctx.needs for s in n.get("stated_by", [])]
    return ctx._get("link_rows", load)


LINK_FIELDS = ("record_field", "quote", "publication_item", "publication_quote", "verdict")


def need_links(ctx):
    """Recomputed need_tests: {need_id: {test_id: objective_link}} for in-scope tests that record every
    required condition (or have it documented for their table) and at least one outcome; 'stated' where
    the investigation has a link with verdict 'supported'."""
    def load():
        out = {}
        for need in ctx.needs:
            stated = stated_investigations(need)
            out[need["id"]] = {
                t["test_id"]: ("stated" if t["investigation_id"] in stated else "not_stated")
                for t in ctx.tests if in_scope(t, need) and has_required(ctx, t, need) and has_outcome(t, need)}
        return out
    return ctx._get("need_links", load)


def usable_ids(ctx, need_id):
    return [tid for tid, link in need_links(ctx)[need_id].items() if link == "stated"]


@check("D1_need_tests",
       "need_tests.csv lists exactly the in-scope tests that record every required condition (or have it "
       "documented for their table) and at least one outcome of each need, with objective_link 'stated' only "
       "when a 'stated_by' link of the investigation has verdict 'supported'.")
def check_d1(ctx):
    res = Result()
    links = need_links(ctx)
    have = {}
    for r in ctx.table("need_tests.csv"):
        k = (r["need_id"], r["test_id"])
        if k in have:
            res.fail(problem="listed twice", need_id=k[0], test_id=k[1])
        have[k] = r
    expected = {(n, tid): link for n, d in links.items() for tid, link in d.items()}
    res.checked = len(expected)
    for k in sorted(set(expected) - set(have)):
        res.fail(problem="usable by the rule but not listed", need_id=k[0], test_id=k[1], objective_link=expected[k])
    for k in sorted(set(have) - set(expected)):
        res.fail(problem="listed but not usable by the rule", need_id=k[0], test_id=k[1])
    for k in sorted(set(have) & set(expected)):
        t = ctx.tests_by_id[k[1]]
        if have[k]["objective_link"] != expected[k] or have[k]["investigation_id"] != t["investigation_id"]:
            res.fail(problem="objective_link or investigation differs", need_id=k[0], test_id=k[1],
                     listed=have[k]["objective_link"], recomputed=expected[k])
    res.numbers = {"rows_recomputed": len(expected), "rows_in_file": len(have),
                   "stated": sum(1 for v in expected.values() if v == "stated"),
                   "per_need_stated": {n: sum(1 for v in d.values() if v == "stated") for n, d in links.items()}}
    return res


@check("D2_capability_matrix",
       "capability_matrix.csv has one row per need and source whose counts (tests in scope, with required "
       "conditions, with an outcome, usable), status, missing and documented conditions, objective_link and "
       "publication quote equal the recomputation from tests.csv, needs.json and sources.json.")
def check_d2(ctx):
    res = Result()
    have = {(r["need_id"], r["source_id"]): r for r in ctx.table("capability_matrix.csv")}
    by_source = {}
    for t in ctx.tests:
        by_source.setdefault(t["source_id"], []).append(t)
    for need in ctx.needs:
        stated = stated_investigations(need)
        for s in ctx.sources:
            res.checked += 1
            key = {"need_id": need["id"], "source_id": s["id"]}
            row = have.get((need["id"], s["id"]))
            if row is None:
                res.fail(problem="row missing", **key)
                continue
            exp = {"objective_link": "stated" if s["investigation_id"] in stated else "not_stated",
                   "investigation_id": s["investigation_id"], "row_unit": s.get("row_unit", "")}
            if "columns" not in s:
                exp.update(status="not_test_level", tests=0, tests_with_required_conditions=0,
                           tests_with_outcome=0, usable_tests=0, required_missing=[], outcomes_present=[],
                           required_documented_not_in_table=[])
            else:
                scope = [t for t in by_source.get(s["id"], []) if in_scope(t, need)]
                no_value = [v for v in need["conditions_required"] if not any(t.get(v, "") != "" for t in scope)]
                documented = [v for v in no_value if v in documented_variables(ctx, need, s["id"])]
                missing = [v for v in no_value if v not in documented]
                present = [v for v in need["outcomes_any"] if any(t.get(v, "") != "" for t in scope)]
                if not scope:
                    status, missing, documented = "out_of_scope", [], []
                elif present and not missing:
                    status = "measured"
                elif present:
                    status = "partial"
                elif not missing:
                    status = "conditions_only"
                else:
                    status = "none"
                exp.update(status=status, tests=len(scope),
                           tests_with_required_conditions=sum(1 for t in scope if has_required(ctx, t, need)),
                           tests_with_outcome=sum(1 for t in scope if has_outcome(t, need)),
                           usable_tests=sum(1 for t in scope if has_required(ctx, t, need) and has_outcome(t, need)),
                           required_missing=missing, outcomes_present=present,
                           required_documented_not_in_table=documented)
            for col, want in exp.items():
                if col == "required_documented_not_in_table" and col not in row and not want:
                    continue
                got = row.get(col, "")
                if isinstance(want, list):
                    same = sorted(split_list(got)) == sorted(want)
                elif isinstance(want, int):
                    same = fnum(got) == want
                else:
                    same = got == want
                if not same:
                    res.fail(column=col, in_file=got, recomputed=want, **key)
            q = row.get("objective_quote", "")
            if exp["objective_link"] == "stated":
                mine = [publication_quote(ctx, x) for x in supported_links(need)
                        if x["investigation_id"] == s["investigation_id"]]
                if q == "" or (q not in mine and not all(x in q for x in mine)):
                    res.fail(column="objective_quote", in_file=q[:120], recomputed=mine[0][:120], **key)
            elif q != "":
                res.fail(column="objective_quote", in_file=q[:120], recomputed="", **key)
    extra = set(have) - {(n["id"], s["id"]) for n in ctx.needs for s in ctx.sources}
    for k in sorted(extra):
        res.fail(problem="row for an unknown need or source", need_id=k[0], source_id=k[1])
    res.numbers = {"need_x_source": res.checked, "rows_in_file": len(have)}
    return res


def clean_text(html):
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text).strip()


@check("D3_objective_quotes",
       "Every 'stated_by' link of needs.json has a known verdict; its record sentence, where given, is "
       "literally in the named field of the PSI record; its publication, where given, is a reference item "
       "with a quote; and a link with verdict 'supported' has a publication.")
def check_d3(ctx):
    res = Result()
    meta = ctx.spec("needs")["_meta"]
    verdicts = meta.get("verdict_values") or []
    fields = meta.get("stated_by_fields") or []
    counts = {}
    for need in ctx.needs:
        for s in need.get("stated_by", []):
            res.checked += 1
            inv = s.get("investigation_id")
            key = {"need_id": need["id"], "investigation_id": inv, "verdict": s.get("verdict")}
            counts[s.get("verdict")] = counts.get(s.get("verdict"), 0) + 1
            if verdicts and s.get("verdict") not in verdicts:
                res.fail(problem="verdict is not one of verdict_values", **key)
            if not os.path.exists(os.path.join(CATALOG, "%s.json" % inv)):
                res.fail(problem="no PSI record", **key)
            if ("field" in s) != ("quote" in s):
                res.fail(problem="'field' and 'quote' must come together", **key)
            elif "field" in s:
                if fields and s["field"] not in fields:
                    res.fail(problem="field is not one of stated_by_fields", field=s["field"], **key)
                problem = quote_in_record(ctx, inv, s["field"], s["quote"])
                if problem:
                    res.fail(problem=problem, field=s["field"], quote=s["quote"][:160], **key)
            if s.get("publication"):
                item = ctx.reference_items.get(s["publication"])
                if item is None:
                    res.fail(problem="publication is not an item of references.json", publication=s["publication"], **key)
                elif not item[1].get("quote"):
                    res.fail(problem="publication item has no quote", publication=s["publication"], **key)
                elif item[1].get("type") not in ("stated_objective", "framework"):
                    res.fail(problem="publication item is not of type stated_objective or framework",
                             publication=s["publication"], item_type=item[1].get("type"), **key)
            elif s.get("verdict") == "supported":
                res.fail(problem="supported link without a publication", **key)
            if "field" not in s and not s.get("publication"):
                res.fail(problem="link with neither a record sentence nor a publication", **key)
    res.numbers = {"links": res.checked, "per_verdict": dict(sorted(counts.items(), key=str))}
    return res


@check("D4_objective_links",
       "objective_links.csv lists exactly the links of needs.json 'stated_by' (all verdicts) with record "
       "field and sentence, publication item, the quote of that item in references.json, and verdict.")
def check_d4(ctx):
    res = Result()
    cols = ("need_id", "investigation_id") + LINK_FIELDS
    expected = [tuple(r[c] for c in cols) for r in link_rows(ctx)]
    have = [tuple(r.get(c, "") for c in cols) for r in ctx.table("objective_links.csv")]
    res.checked = len(expected)
    for k in sorted(set(expected) - set(have)):
        res.fail(problem="in needs.json, not in the file (or a field differs)", need_id=k[0], investigation_id=k[1],
                 quote=k[3][:80], publication_item=k[4], publication_quote=k[5][:80], verdict=k[6])
    for k in sorted(set(have) - set(expected)):
        res.fail(problem="in the file, not in needs.json (or a field differs)", need_id=k[0], investigation_id=k[1],
                 quote=k[3][:80], publication_item=k[4], publication_quote=k[5][:80], verdict=k[6])
    if sorted(have) != sorted(expected) and len(have) != len(expected):
        res.fail(problem="number of rows", in_file=len(have), in_spec=len(expected))
    res.numbers = {"links_in_spec": len(expected), "rows_in_file": len(have)}
    return res


def quote_in_record(ctx, inv, field, quote):
    if not os.path.exists(os.path.join(CATALOG, "%s.json" % inv)):
        return "no PSI record"
    text = ctx.record(inv).get(field)
    if not isinstance(text, str):
        return "field missing in the record"
    return None if clean_text(quote) in clean_text(text) else "quote not in the record field"


@check("D5_side_quotes",
       "Every 'see_also' entry of scenarios.json and every 'documented_elsewhere' entry of sources.json is "
       "literally in the named PSI record field, raw table cell or references.json item, and a variable "
       "documented elsewhere has no value in the tests of that table.")
def check_d5(ctx):
    res = Result()
    for scen in ctx.spec("scenarios")["scenarios"]:
        for e in scen.get("see_also", []):
            res.checked += 1
            key = {"spec": "scenarios.json", "scenario_id": scen["id"], "investigation_id": e.get("investigation_id")}
            if "table_cell" in e:
                c = e["table_cell"]
                try:
                    table = ctx.raw(c["file"])
                    cell = table[int(c["row"]) - 1][table[0].index(c["column"].strip())]
                except (OSError, ValueError, IndexError, KeyError):
                    cell = None
                if cell != str(c.get("text", "")).strip():
                    res.fail(problem="table cell differs", quoted=c.get("text"), raw_cell=cell, **key)
            else:
                problem = quote_in_record(ctx, e.get("investigation_id"), e.get("record_field"), e.get("quote", ""))
                if problem:
                    res.fail(problem=problem, field=e.get("record_field"), quote=e.get("quote", "")[:120], **key)
    for s in ctx.sources:
        for e in s.get("documented_elsewhere", []):
            res.checked += 1
            key = {"spec": "sources.json", "source_id": s["id"], "variable": e.get("variable")}
            if "reference_item" in e:
                item = ctx.reference_items.get(e["reference_item"])
                if item is None:
                    res.fail(problem="reference_item is not in references.json", reference_item=e["reference_item"], **key)
                elif not e.get("quote") or clean_text(e["quote"]) not in clean_text(item[1].get("quote", "")):
                    res.fail(problem="quote is not contained in the quote of the references.json item",
                             reference_item=e["reference_item"], **key)
            elif "record_field" in e:
                problem = quote_in_record(ctx, s["investigation_id"], e.get("record_field"), e.get("quote", ""))
                if problem:
                    res.fail(problem=problem, field=e.get("record_field"), quote=e.get("quote", "")[:120], **key)
            else:
                res.fail(problem="entry has neither record_field nor reference_item", **key)
            n = sum(1 for t in ctx.tests if t["source_id"] == s["id"] and t.get(e.get("variable"), "") != "")
            if n:
                res.fail(problem="variable documented elsewhere has values in the tests of the table", tests=n, **key)
    if not res.checked:
        raise Skip("no see_also or documented_elsewhere entry in the spec")
    res.numbers = {"entries": res.checked}
    return res


# ----------------------------------------------------------------------------
# E. coverage grid
# ----------------------------------------------------------------------------

def in_range(value, rng):
    """Range with 'min'/'max' (None = open). Edges follow coverage.json: the lower edge belongs to the
    range, the upper edge does not, unless min_inclusive / max_inclusive say otherwise."""
    lo, hi = rng.get("min"), rng.get("max")
    if lo is not None:
        if value < lo or (value == lo and not rng.get("min_inclusive", True)):
            return False
    if hi is not None:
        if value > hi or (value == hi and not rng.get("max_inclusive", False)):
            return False
    return True


def bin_of(text, dim, not_recorded):
    if text == "":
        return not_recorded
    v = fnum(text)
    hits = [b["id"] for b in dim["bins"] if v is not None and in_range(v, b)]
    return hits[0] if len(hits) == 1 else "?(%d bins)" % len(hits)


def coverage_counts(ctx):
    cov = ctx.spec("coverage")
    nr = cov["not_recorded"]["id"]
    cells = {}
    for t in ctx.tests:
        group = tuple(t.get(g, "") or nr for g in cov["group_by"])
        key = group + (bin_of(t.get("o2_pct", ""), cov["dimensions"]["o2_pct"], nr),
                       bin_of(t.get("pressure_kpa", ""), cov["dimensions"]["pressure_kpa"], nr))
        cells.setdefault(key, []).append(t)
    return cells


@check("E1_coverage_grid",
       "Every count of coverage_grid.csv equals the number of tests that tests.csv puts in that fuel phase, "
       "oxygen basis, oxygen bin and pressure bin (coverage.json), and no non-empty cell is missing.")
def check_e1(ctx):
    res = Result()
    cov = ctx.spec("coverage")
    cells = coverage_counts(ctx)
    have = {}
    for r in ctx.table("coverage_grid.csv"):
        k = tuple(r[g] for g in cov["group_by"]) + (r["o2_bin"], r["pressure_bin"])
        if k in have:
            res.fail(problem="cell listed twice", cell="/".join(k))
        have[k] = r
    for k in sorted(set(cells) | set(have)):
        res.checked += 1
        tests = cells.get(k, [])
        row = have.get(k)
        if row is None:
            res.fail(problem="cell with tests missing from the file", cell="/".join(k), recomputed=len(tests))
            continue
        if fnum(row["tests"]) != len(tests):
            res.fail(problem="count differs", cell="/".join(k), in_file=row["tests"], recomputed=len(tests))
        elif sorted(split_list(row["investigation_ids"])) != sorted({t["investigation_id"] for t in tests}) or \
                sorted(split_list(row["source_ids"])) != sorted({t["source_id"] for t in tests}):
            res.fail(problem="investigation or source ids differ", cell="/".join(k))
    res.numbers = {"cells_compared": res.checked, "cells_with_tests": len(cells), "rows_in_file": len(have)}
    return res


@check("E2_coverage_total", "The counts of coverage_grid.csv add up to the number of tests.")
def check_e2(ctx):
    res = Result()
    total = sum(int(fnum(r["tests"]) or 0) for r in ctx.table("coverage_grid.csv"))
    res.checked = 1
    if total != len(ctx.tests):
        res.fail(grid_total=total, tests=len(ctx.tests))
    res.numbers = {"grid_total": total, "tests": len(ctx.tests)}
    return res


# ----------------------------------------------------------------------------
# F. scenarios
# ----------------------------------------------------------------------------

def match_range(text, rng):
    if not rng:
        return "not_specified"
    if text == "":
        return "not_recorded"
    return "in" if in_range(fnum(text), rng) else "out"


def scenario_marks(test, scen):
    """o2, pressure, flow and gravity marks, the tier and the added-gas mark of one test (scenarios.json
    match_values, tier_rule, added_gas)."""
    ranges = scen.get("ranges") or {}
    o2 = match_range(test.get("o2_pct", ""), ranges.get("o2_pct"))
    if o2 in ("in", "out") and test.get("o2_basis", "") == "oxidizer_stream":
        o2 = "not_ambient"
    pressure = match_range(test.get("pressure_kpa", ""), ranges.get("pressure_kpa"))
    flow = match_range(test.get("flow_cms", ""), ranges.get("flow_cms"))
    level = scen.get("gravity_level")
    if not level:
        gravity = "not_specified"
    elif test.get("gravity_level", "") == "":
        gravity = "not_recorded"
    else:
        gravity = "same" if test["gravity_level"] == level else "different"
    co2, he = fnum(test.get("co2_pct", "")), fnum(test.get("he_pct", ""))
    if (co2 is not None and co2 > 0) or (he is not None and he > 0):
        added = "co2_or_helium"
    elif co2 == 0 and he == 0:
        added = "none"
    else:
        added = "not_recorded"
    if o2 == "in" and pressure == "in":
        tier = "atmosphere"
    elif o2 == "in" and pressure == "not_recorded":
        tier = "oxygen_only"
    elif pressure == "in" and o2 == "not_recorded":
        tier = "pressure_only"
    else:
        tier = "other"
    return {"o2_match": o2, "pressure_match": pressure, "flow_match": flow, "gravity_match": gravity, "tier": tier,
            "added_gas": added}


def scenario_need_row(ctx, scen, need, marks):
    """Recomputed scenario_needs row: counts by tier, status and gap codes (scenarios.json status_rule,
    evidence_rule; README 'Scenarios')."""
    links = need_links(ctx)[need["id"]]
    usable = [tid for tid, link in links.items() if link == "stated"]
    ranges = scen.get("ranges") or {}
    row = {"usable_tests": len(usable),
           "tests_recorded_outside_objective": sum(1 for link in links.values() if link == "not_stated")}
    by_tier = {tier: [tid for tid in usable if marks[tid]["tier"] == tier] for tier in TIERS}
    for tier in TIERS:
        row["tests_" + tier] = len(by_tier[tier])
        row["investigations_" + tier] = sorted({ctx.tests_by_id[tid]["investigation_id"] for tid in by_tier[tier]}, key=psi_key)
    # README: "The flow and gravity counts cover tiers atmosphere and oxygen_only only"
    compared = [tid for tid in usable if marks[tid]["tier"] in ("atmosphere", "oxygen_only")]
    matched = [tid for tid in usable if marks[tid]["tier"] in MATCHED_TIERS]
    row["matched_tests_flow_in_range"] = sum(1 for tid in compared if marks[tid]["flow_match"] == "in")
    row["matched_tests_flow_not_recorded"] = sum(1 for tid in compared if marks[tid]["flow_match"] == "not_recorded")
    row["matched_tests_same_gravity"] = sum(1 for tid in compared if marks[tid]["gravity_match"] == "same")
    row["matched_tests_co2_or_helium_added"] = sum(1 for tid in compared if marks[tid]["added_gas"] == "co2_or_helium")
    row["_matched"] = matched
    row["_pressure_only_would_change_flow_counts"] = any(
        marks[tid]["flow_match"] in ("in", "not_recorded") or marks[tid]["gravity_match"] == "same"
        for tid in by_tier["pressure_only"])
    has_atmosphere = bool(ranges.get("o2_pct")) or bool(ranges.get("pressure_kpa"))
    if not usable:
        status = "not_measured"
    elif not has_atmosphere:
        status = "atmosphere_not_specified"
    elif by_tier["atmosphere"]:
        status = "in_atmosphere"
    elif by_tier["oxygen_only"]:
        status = "oxygen_only"
    elif by_tier["pressure_only"]:
        status = "pressure_only"
    else:
        status = "other_atmosphere"
    row["status"] = status
    gaps, flow_gap = [], []
    if not usable:
        gaps.append("need:no_usable_test")
    else:
        for name, var, mark in (("oxygen", "o2_pct", "o2_match"), ("pressure", "pressure_kpa", "pressure_match"),
                                ("flow", "flow_cms", "flow_match")):
            if not ranges.get(var):
                continue
            got = {marks[tid][mark] for tid in usable}
            if "in" in got:
                continue
            code = "%s:%s" % (name, "not_recorded" if got <= {"not_recorded"} else "no_usable_test_in_range")
            (flow_gap if name == "flow" else gaps).append(code)
        level = scen.get("gravity_level")
        if level and not any(marks[tid]["gravity_match"] == "same" for tid in usable):
            gaps.append("gravity:no_usable_test_at_%s" % level)
    row["gaps"] = gaps
    row["_flow_gap"] = flow_gap
    row["scenario_gravity_level"] = scen.get("gravity_level") or ""
    return row


def all_marks(ctx, scen):
    return {t["test_id"]: scenario_marks(t, scen) for t in ctx.tests}


OPTIONAL_NEED_COUNTS = ["matched_tests_co2_or_helium_added"]      # compared when the file has the column
SCENARIO_NEED_COUNTS = ["usable_tests"] + ["tests_" + t for t in TIERS] + [
    "tests_recorded_outside_objective", "matched_tests_flow_in_range", "matched_tests_flow_not_recorded",
    "matched_tests_same_gravity"]


def compare_scenario_need(res, key, file_row, exp, parts):
    """Compare one scenario_needs / atmosphere_cells row with the recomputation."""
    if "counts" in parts:
        for col in SCENARIO_NEED_COUNTS + [c for c in OPTIONAL_NEED_COUNTS if c in file_row]:
            if fnum(file_row.get(col, "")) != exp[col]:
                res.fail(column=col, in_file=file_row.get(col, ""), recomputed=exp[col], **key)
        for tier in TIERS:
            col = "investigations_" + tier
            if sorted(split_list(file_row.get(col, ""))) != sorted(exp[col]):
                res.fail(column=col, in_file=file_row.get(col, ""), recomputed=";".join(exp[col]), **key)
    if "status" in parts and file_row.get("status", "") != exp["status"]:
        res.fail(column="status", in_file=file_row.get("status", ""), recomputed=exp["status"], **key)
    if "gaps" in parts:
        listed = [g for g in split_list(file_row.get("gaps", "")) if not g.startswith("flow:")]
        if sorted(listed) != sorted(exp["gaps"]):
            res.fail(column="gaps (all but flow)", in_file=file_row.get("gaps", ""), recomputed=";".join(exp["gaps"]), **key)
        if "scenario_gravity_level" in file_row and file_row["scenario_gravity_level"] != exp["scenario_gravity_level"]:
            res.fail(column="scenario_gravity_level", in_file=file_row["scenario_gravity_level"],
                     recomputed=exp["scenario_gravity_level"], **key)
    if "flow_gap" in parts:
        got = [g for g in split_list(file_row.get("gaps", "")) if g.startswith("flow:")]
        if sorted(got) != sorted(exp["_flow_gap"]):
            res.fail(column="gaps (flow)", in_file=";".join(got), recomputed=";".join(exp["_flow_gap"]),
                     matched_tests_flow_in_range=file_row.get("matched_tests_flow_in_range", ""), **key)


@check("F1_scenario_marks",
       "For every scenario and test, the oxygen, pressure, flow and gravity marks and the tier of "
       "scenario_tests.csv equal the recomputation from tests.csv and the ranges of scenarios.json.")
def check_f1(ctx):
    return scenario_marks_check(ctx, added_gas_only=False)


def scenario_marks_check(ctx, added_gas_only):
    res = Result()
    scens = ctx.spec("scenarios")["scenarios"]
    rows = ctx.table("scenario_tests.csv")
    if added_gas_only and rows and "added_gas" not in rows[0]:
        raise Skip("scenario_tests.csv has no added_gas column")
    have = {(r["scenario_id"], r["test_id"]): r for r in rows}
    tiers = {}
    for scen in scens:
        for tid, m in all_marks(ctx, scen).items():
            res.checked += 1
            row = have.get((scen["id"], tid))
            tiers[m["tier"]] = tiers.get(m["tier"], 0) + 1
            if row is None:
                res.fail(problem="row missing", scenario_id=scen["id"], test_id=tid)
                continue
            for col, want in m.items():
                if (col == "added_gas") != added_gas_only:
                    continue
                if row.get(col, "") != want:
                    t = ctx.tests_by_id[tid]
                    res.fail(scenario_id=scen["id"], test_id=tid, column=col, in_file=row.get(col, ""),
                             recomputed=want, o2_pct=t.get("o2_pct"), pressure_kpa=t.get("pressure_kpa"),
                             flow_cms=t.get("flow_cms"), co2_pct=t.get("co2_pct"), he_pct=t.get("he_pct"))
    if len(have) != len(scens) * len(ctx.tests):
        res.fail(problem="row count", in_file=len(have), expected=len(scens) * len(ctx.tests))
    res.numbers = {"scenario_x_test": res.checked, "rows_in_file": len(have), "tiers_recomputed": dict(sorted(tiers.items()))}
    return res


def scenario_needs_check(ctx, parts):
    res = Result()
    have = {(r["scenario_id"], r["need_id"]): r for r in ctx.table("scenario_needs.csv")}
    scens = ctx.spec("scenarios")["scenarios"]
    for scen in scens:
        marks = all_marks(ctx, scen)
        for need in ctx.needs:
            res.checked += 1
            key = {"scenario_id": scen["id"], "need_id": need["id"]}
            row = have.get((scen["id"], need["id"]))
            if row is None:
                res.fail(problem="row missing", **key)
                continue
            compare_scenario_need(res, key, row, scenario_need_row(ctx, scen, need, marks), parts)
    if "counts" in parts and len(have) != len(scens) * len(ctx.needs):
        res.fail(problem="row count", in_file=len(have), expected=len(scens) * len(ctx.needs))
    res.numbers = {"scenario_x_need": res.checked, "rows_in_file": len(have)}
    return res


@check("F2_scenario_need_counts",
       "Every numeric column and investigation list of scenario_needs.csv equals the recomputation from "
       "tests.csv, the recomputed usable tests and the recomputed tiers.")
def check_f2(ctx):
    return scenario_needs_check(ctx, {"counts"})


@check("F3_scenario_need_status",
       "The status of every scenario and need follows the status_rule of scenarios.json.")
def check_f3(ctx):
    return scenario_needs_check(ctx, {"status"})


@check("F4_scenario_need_gaps",
       "The oxygen, pressure, gravity and no-usable-test gap codes of scenario_needs.csv say which variable "
       "has no usable test in range or is not in the table (README 'Scenarios').")
def check_f4(ctx):
    return scenario_needs_check(ctx, {"gaps"})


@check("F5_scenario_flow_gap",
       "A scenario that sets a flow range carries a flow gap code exactly when no usable test has its flow in "
       "range (README: gap codes say which variable - oxygen, pressure, flow, gravity - has no usable test in "
       "range or is not in the table).")
def check_f5(ctx):
    return scenario_needs_check(ctx, {"flow_gap"})


# ----------------------------------------------------------------------------
# G. indicators
# ----------------------------------------------------------------------------

def passes(test, cond):
    var, op = cond[0], cond[1]
    val = test.get(var, "")
    if op == "notnull":
        return val != ""
    target = cond[2]
    if op == "contains":
        return str(target) in val
    if val == "":
        return False
    a, b = fnum(val), fnum(target)
    if op in ("==", "!="):
        same = (a == b) if (a is not None and b is not None) else (val == str(target))
        return same if op == "==" else not same
    if a is None or b is None:
        return False
    return {">": a > b, ">=": a >= b, "<": a < b, "<=": a <= b}[op]


def median(values):
    s = sorted(values)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def population_ids(ctx, ind):
    """Test ids of the indicator's population (indicators.json _meta 'population')."""
    need = next(n for n in ctx.needs if n["id"] == ind["need_id"])
    links = need_links(ctx)[need["id"]]
    pop = ind.get("population", "usable")
    if pop == "usable":
        return [tid for tid, link in links.items() if link == "stated"]
    if pop == "recorded":
        return list(links)
    if pop == "in_scope":
        stated = stated_investigations(need)
        return [t["test_id"] for t in ctx.tests
                if in_scope(t, need) and has_required(ctx, t, need) and t["investigation_id"] in stated]
    raise ValueError("unknown population " + str(pop))


def compute_indicator(ctx, ind, test_ids):
    """Rows of one indicator over the given tests: ({(group, stat, category): (value, n_tests, investigations)},
    {(group, test_id): value})."""
    var = ind["variable"]
    template = ind["template"]
    groups = {}
    for tid in test_ids:
        t = ctx.tests_by_id[tid]
        if not all(passes(t, c) for c in ind.get("where", [])):
            continue
        if template != "count" and t.get(var, "") == "":
            continue
        label = ";".join("%s=%s" % (g, t.get(g, "")) for g in ind.get("group_by", []))
        groups.setdefault(label, []).append(t)
    rows, tests = {}, {}
    for label, members in groups.items():
        invs = sorted({t["investigation_id"] for t in members}, key=psi_key)
        for t in members:
            tests[(label, t["test_id"])] = t.get(var, "")
        if template == "summary":
            values = [fnum(t[var]) for t in members]
            for stat in ind.get("stats", []):
                value = {"min": min, "max": max, "median": median}[stat](values)
                rows[(label, stat, "")] = (value, len(members), invs)
        elif template == "count_by":
            for cat in sorted({t[var] for t in members}):
                rows[(label, "count", cat)] = (sum(1 for t in members if t[var] == cat), len(members), invs)
        elif template == "count":
            rows[(label, "count", "")] = (len(members), len(members), invs)
        else:
            raise ValueError("unknown template " + str(template))
    return rows, tests


@check("F6_added_gas_mark",
       "The added_gas mark of scenario_tests.csv is 'none' only where carbon dioxide and helium are both "
       "recorded as 0, 'co2_or_helium' where either is above 0, and 'not_recorded' otherwise (scenarios.json "
       "'added_gas').")
def check_f6(ctx):
    res = scenario_marks_check(ctx, added_gas_only=True)
    tests = {f["test_id"] for f in res.failures if "test_id" in f}
    res.numbers = {"scenario_x_test": res.checked, "tests_with_a_different_mark": len(tests)}
    by_source = {}
    for tid in tests:
        k = ctx.tests_by_id[tid]["source_id"]
        by_source[k] = by_source.get(k, 0) + 1
    res.details = {"tests_with_a_different_mark_per_source": dict(sorted(by_source.items()))}
    return res


@check("G1_indicators",
       "Every row of indicators.csv (value, n_tests, investigations, texts) equals the recomputation of its "
       "template over its population, filter and grouping (indicators.json), and no row is missing.")
def check_g1(ctx):
    res = Result()
    have = {}
    for r in ctx.table("indicators.csv"):
        k = (r["indicator_id"], r["group"], r["stat"], r["category"])
        if k in have:
            res.fail(problem="row listed twice", indicator_id=k[0], group=k[1], stat=k[2], category=k[3])
        have[k] = r
    expected = {}
    spec_of = {}
    for ind in ctx.spec("indicators")["indicators"]:
        rows, _ = compute_indicator(ctx, ind, population_ids(ctx, ind))
        for (label, stat, cat), val in rows.items():
            expected[(ind["id"], label, stat, cat)] = val
            spec_of[ind["id"]] = ind
    res.checked = len(expected)
    for k in sorted(set(expected) | set(have)):
        key = {"indicator_id": k[0], "group": k[1], "stat": k[2], "category": k[3]}
        if k not in have:
            res.fail(problem="row missing", recomputed=expected[k][0], **key)
            continue
        if k not in expected:
            res.fail(problem="row not produced by the rule", in_file=have[k]["value"], **key)
            continue
        row, (value, n, invs) = have[k], expected[k]
        ind = spec_of[k[0]]
        if not near(fnum(row["value"]), float(value), STAT_TOL):
            res.fail(column="value", in_file=row["value"], recomputed=value, **key)
        if fnum(row["n_tests"]) != n:
            res.fail(column="n_tests", in_file=row["n_tests"], recomputed=n, **key)
        if sorted(split_list(row["investigation_ids"])) != sorted(invs):
            res.fail(column="investigation_ids", in_file=row["investigation_ids"], recomputed=";".join(invs), **key)
        texts = {"need_id": ind["need_id"], "label": ind["label"], "variable": ind["variable"],
                 "unit": ctx.var_unit.get(ind["variable"], ""), "reading": ind.get("reading", ""),
                 "definition_ref": ";".join(ind.get("definition_ref", [])),
                 "compare_with": ";".join(ind.get("compare_with", []))}
        for col, want in texts.items():
            if col in row and row[col] != want:
                res.fail(column=col, in_file=row[col][:80], recomputed=want[:80], **key)
    res.numbers = {"rows_recomputed": len(expected), "rows_in_file": len(have),
                   "indicators_with_rows": len({k[0] for k in expected}),
                   "indicators_in_spec": len(ctx.spec("indicators")["indicators"])}
    return res


@check("G2_indicator_tests",
       "indicator_tests.csv lists exactly the tests behind each indicator row, with the value each test "
       "contributes.")
def check_g2(ctx):
    res = Result()
    have = {}
    for r in ctx.table("indicator_tests.csv"):
        k = (r["indicator_id"], r["group"], r["test_id"])
        if k in have:
            res.fail(problem="listed twice", indicator_id=k[0], group=k[1], test_id=k[2])
        have[k] = r["value"]
    expected = {}
    for ind in ctx.spec("indicators")["indicators"]:
        _, tests = compute_indicator(ctx, ind, population_ids(ctx, ind))
        for (label, tid), value in tests.items():
            expected[(ind["id"], label, tid)] = value
    res.checked = len(expected)
    for k in sorted(set(expected) | set(have)):
        key = {"indicator_id": k[0], "group": k[1], "test_id": k[2]}
        if k not in have:
            res.fail(problem="test behind the indicator is not listed", **key)
        elif k not in expected:
            res.fail(problem="listed test is not behind the indicator", **key)
        elif have[k] != expected[k] and not close(fnum(have[k]), fnum(expected[k])):
            res.fail(problem="value differs", in_file=have[k], tests_csv=expected[k], **key)
    res.numbers = {"rows_recomputed": len(expected), "rows_in_file": len(have)}
    return res


# ----------------------------------------------------------------------------
# H. references
# ----------------------------------------------------------------------------

@check("H1_reference_ids",
       "Every reference item id used in needs.json, indicators.json and scenarios.json exists in references.json.")
def check_h1(ctx):
    res = Result()
    items = ctx.reference_items
    used = []
    for n in ctx.needs:
        used += [("needs.json", n["id"], i) for i in n.get("references", [])]
    for ind in ctx.spec("indicators")["indicators"]:
        used += [("indicators.json", ind["id"], i) for i in ind.get("definition_ref", []) + ind.get("compare_with", [])]
    for s in ctx.spec("scenarios")["scenarios"]:
        used += [("scenarios.json", s["id"], i) for i in s.get("basis", [])]
    res.checked = len(used)
    for where, owner, item in used:
        if item not in items:
            res.fail(spec=where, used_by=owner, item_id=item)
    ids = [it["id"] for ref in ctx.spec("references")["references"] for it in ref.get("items", [])]
    for i in sorted({i for i in ids if ids.count(i) > 1}):
        res.fail(problem="item id defined twice in references.json", item_id=i)
    res.numbers = {"uses": len(used), "distinct_items_used": len({u[2] for u in used}), "items_defined": len(items)}
    return res


@check("H2_need_references",
       "need_references.csv has exactly the reference items each need lists, with the text, place, document "
       "and URL of references.json.")
def check_h2(ctx):
    res = Result()
    items = ctx.reference_items
    have = {}
    for r in ctx.table("need_references.csv"):
        have[(r["need_id"], r["item_id"])] = r
    expected = [(n["id"], i) for n in ctx.needs for i in n.get("references", [])]
    res.checked = len(expected)
    for k in sorted(set(expected) - set(have)):
        res.fail(problem="in needs.json, not in the file", need_id=k[0], item_id=k[1])
    for k in sorted(set(have) - set(expected)):
        res.fail(problem="in the file, not in needs.json", need_id=k[0], item_id=k[1])
    for k in expected:
        if k not in have or k[1] not in items:
            continue
        ref, it = items[k[1]]
        row = have[k]
        want = {"item_type": it.get("type", ""), "text": it.get("text", ""), "where": it.get("where", ""),
                "variables": ";".join(it.get("variables", [])), "reference_id": ref.get("id", ""),
                "title": ref.get("title", ""), "issuer": ref.get("issuer", ""), "version": ref.get("version", ""),
                "access": ref.get("access", ""), "url": ref.get("url", "")}
        for col, w in want.items():
            if col in row and row[col] != (w or ""):
                res.fail(need_id=k[0], item_id=k[1], column=col, in_file=row[col][:80], spec=str(w)[:80])
        if "values" in row:
            got = json.loads(row["values"]) if row["values"] else None
            if got != it.get("values"):
                res.fail(need_id=k[0], item_id=k[1], column="values", in_file=row["values"][:80])
    res.numbers = {"links_in_spec": len(expected), "rows_in_file": len(have)}
    return res


# ----------------------------------------------------------------------------
# I. evidence packages (contract sections 1 and 2; README 'Evidence packages')
# ----------------------------------------------------------------------------

COUNT_KEYS = {"usable_tests": "usable_tests", "atmosphere": "tests_atmosphere", "oxygen_only": "tests_oxygen_only",
              "pressure_only": "tests_pressure_only", "other": "tests_other",
              "recorded_outside_objective": "tests_recorded_outside_objective",
              "matched_flow_in_range": "matched_tests_flow_in_range",
              "matched_flow_not_recorded": "matched_tests_flow_not_recorded",
              "matched_same_gravity": "matched_tests_same_gravity"}
OPTIONAL_COUNT_KEYS = {"matched_added_gas": "matched_tests_co2_or_helium_added"}
NEED_BLOCK_KEYS = ["need_id", "need", "pillar", "status", "counts", "objective", "investigations", "matched_tests",
                   "usable_elsewhere", "indicators", "gaps", "statements", "references"]
MATCHED_TEST_KEYS = ["test_id", "investigation_id", "source_id", "tier", "o2_match", "pressure_match", "flow_match",
                     "gravity_match", "values", "flags", "source_file", "source_row"]
REFERENCE_KEYS = ["item_id", "type", "text", "where", "title", "version", "url", "access"]
RANGE_VARS = ("o2_pct", "pressure_kpa", "flow_cms")


def full_range(rng):
    """A range with its inclusive flags written out; None when the environment sets none."""
    if not rng:
        return None
    return {"min": rng.get("min"), "max": rng.get("max"),
            "min_inclusive": rng.get("min_inclusive", True), "max_inclusive": rng.get("max_inclusive", False)}


def environments(ctx):
    """The scenarios of scenarios.json, then every oxygen bin x pressure bin of coverage.json."""
    def load():
        envs = []
        for s in ctx.spec("scenarios")["scenarios"]:
            envs.append({"id": s["id"], "kind": "scenario", "file": "scenario_%s.json" % s["id"], "label": s["label"],
                         "ranges": s.get("ranges") or {}, "gravity_level": s.get("gravity_level"), "spec": s})
        dims = ctx.spec("coverage")["dimensions"]
        for ob in dims["o2_pct"]["bins"]:
            for pb in dims["pressure_kpa"]["bins"]:
                cid = "cell_%s__%s" % (ob["id"], pb["id"])
                envs.append({"id": cid, "kind": "cell", "file": cid + ".json", "label": None,
                             "ranges": {"o2_pct": full_range(ob), "pressure_kpa": full_range(pb)},
                             "gravity_level": None, "o2_bin": ob["id"], "pressure_bin": pb["id"]})
        return envs
    return ctx._get("environments", load)


def env_marks(ctx, env):
    return ctx._get(("marks", env["id"]), lambda: all_marks(ctx, env))


def evidence_index(ctx):
    name = os.path.join("evidence", "index.json")
    if not ctx.has(name):
        raise Skip("data/pipeline/evidence/index.json does not exist yet")
    return ctx.json(name)


def packages(ctx):
    """(environment, package or None) for every expected environment."""
    evidence_index(ctx)
    out = []
    for env in environments(ctx):
        name = os.path.join("evidence", env["file"])
        out.append((env, ctx.json(name) if ctx.has(name) else None))
    return out


def need_blocks(ctx):
    """(environment, need spec, block) for every need block that exists."""
    for env, pack in packages(ctx):
        if not pack:
            continue
        blocks = {b.get("need_id"): b for b in pack.get("needs", []) if isinstance(b, dict)}
        for need in ctx.needs:
            if need["id"] in blocks:
                yield env, need, blocks[need["id"]]


def reference_view(ctx, item_id):
    ref, it = ctx.reference_items[item_id]
    return {"item_id": item_id, "type": it.get("type"), "text": it.get("text"), "where": it.get("where"),
            "title": ref.get("title"), "version": ref.get("version"), "url": ref.get("url"), "access": ref.get("access")}


@check("I1_evidence_schema",
       "index.json lists the scenarios of scenarios.json and then every oxygen bin x pressure bin of "
       "coverage.json, every package file exists and has the contract's shape: environment with ranges and "
       "basis, and one block per need of needs.json with all its fields.")
def check_i1(ctx):
    res = Result()
    index = evidence_index(ctx)
    envs = environments(ctx)
    listed = index.get("packages", [])
    if not (index.get("_meta") or {}).get("generated_by"):
        res.fail(problem="index.json has no _meta.generated_by")
    if [p.get("id") for p in listed] != [e["id"] for e in envs]:
        res.fail(problem="index order or ids differ from scenarios.json + coverage.json",
                 in_file=[p.get("id") for p in listed][:8], expected=[e["id"] for e in envs][:8])
    by_id = {p.get("id"): p for p in listed}
    folder = ctx.out_path("evidence")
    extra = sorted(set(os.listdir(folder)) - {e["file"] for e in envs} - {"index.json"})
    for name in extra:
        res.fail(problem="file in evidence/ that is not a package of the index", file=name)
    need_ids = [n["id"] for n in ctx.needs]
    extra_keys = set()
    for env, pack in packages(ctx):
        res.checked += 1
        key = {"package": env["id"]}
        if pack is None:
            res.fail(problem="package file missing", file=env["file"], **key)
            continue
        meta = pack.get("_meta") or {}
        for k in ("generated_by", "note", "rules"):
            if not meta.get(k):
                res.fail(problem="_meta.%s missing" % k, **key)
        e = pack.get("environment") or {}
        want = {"id": env["id"], "kind": env["kind"], "gravity_level": env["gravity_level"]}
        if env["kind"] == "scenario":
            want["label"] = env["label"]
            want["nominal"] = env["spec"].get("nominal")
            want["note"] = env["spec"].get("note")
        for k, w in want.items():
            if e.get(k) != w:
                res.fail(problem="environment.%s differs from the spec" % k, in_file=e.get(k), spec=w, **key)
        for k in ("label", "note"):
            if not e.get(k):
                res.fail(problem="environment.%s missing" % k, **key)
        for var in RANGE_VARS:
            if (e.get("ranges") or {}).get(var) != full_range(env["ranges"].get(var)):
                res.fail(problem="environment.ranges.%s differs from the spec" % var,
                         in_file=(e.get("ranges") or {}).get(var), spec=full_range(env["ranges"].get(var)), **key)
        basis_ids = env["spec"].get("basis", []) if env["kind"] == "scenario" else []
        if [b.get("item_id") for b in e.get("basis", [])] != basis_ids:
            res.fail(problem="environment.basis differs from the spec", in_file=[b.get("item_id") for b in e.get("basis", [])], **key)
        else:
            for b in e.get("basis", []):
                if b.get("item_id") in ctx.reference_items and {k: b.get(k) for k in REFERENCE_KEYS} != reference_view(ctx, b["item_id"]):
                    res.fail(problem="basis item differs from references.json", item_id=b.get("item_id"), **key)
        entry = by_id.get(env["id"]) or {}
        for k in ("kind", "label", "ranges", "gravity_level"):
            if entry.get(k) != e.get(k):
                res.fail(problem="index.%s differs from the package" % k, **key)
        if entry.get("file") != env["file"]:
            res.fail(problem="index.file", in_file=entry.get("file"), expected=env["file"], **key)
        blocks = pack.get("needs", [])
        if [b.get("need_id") for b in blocks] != need_ids:
            res.fail(problem="need blocks are not the needs of needs.json in order", **key)
        for b in blocks:
            nk = dict(key, need_id=b.get("need_id"))
            missing = [k for k in NEED_BLOCK_KEYS if k not in b]
            if missing:
                res.fail(problem="need block lacks fields", missing=missing, **nk)
                continue
            spec = next((n for n in ctx.needs if n["id"] == b["need_id"]), None)
            if spec and (b["need"], b["pillar"]) != (spec["name"], spec["pillar"]):
                res.fail(problem="need name or pillar differs from needs.json", **nk)
            if set(COUNT_KEYS) - set(b["counts"]):
                res.fail(problem="counts lacks keys of the contract", missing=sorted(set(COUNT_KEYS) - set(b["counts"])), **nk)
            extra_keys.update(set(b) - set(NEED_BLOCK_KEYS))
            extra_keys.update("counts." + k for k in set(b["counts"]) - set(COUNT_KEYS))
            for mt in b["matched_tests"]:
                lack = [k for k in MATCHED_TEST_KEYS if k not in mt]
                if lack:
                    res.fail(problem="matched test lacks fields", test_id=mt.get("test_id"), missing=lack, **nk)
                    break
            for s in b["statements"]:
                if not s.get("id") or not s.get("text"):
                    res.fail(problem="statement without id or text", **nk)
                    break
    res.numbers = {"packages": res.checked, "listed_in_index": len(listed), "extra_files": len(extra),
                   "need_block_fields_not_in_contract": len(extra_keys)}
    res.details = {"need_block_fields_not_in_contract": sorted(extra_keys)}
    return res


def csv_rows_for_envs(ctx):
    rows = {(r["scenario_id"], r["need_id"]): r for r in ctx.table("scenario_needs.csv")}
    if ctx.has("atmosphere_cells.csv"):
        rows.update({(r["scenario_id"], r["need_id"]): r for r in ctx.table("atmosphere_cells.csv")})
    return rows


@check("I2_evidence_status_counts",
       "status, counts and gap codes of every need block equal the environment's row in scenario_needs.csv "
       "or atmosphere_cells.csv; index.json carries the same status, the first statement of the block as "
       "status text, and the caveat of the scenario.")
def check_i2(ctx):
    res = Result()
    index = {p.get("id"): p for p in evidence_index(ctx).get("packages", [])}
    rows = csv_rows_for_envs(ctx)
    texts = 0
    for env, need, b in need_blocks(ctx):
        res.checked += 1
        key = {"package": env["id"], "need_id": need["id"]}
        row = rows.get((env["id"], need["id"]))
        if row is None:
            res.fail(problem="no CSV row for this environment and need", **key)
            continue
        if b.get("status") != row["status"]:
            res.fail(field="status", package_value=b.get("status"), csv=row["status"], **key)
        pairs = dict(COUNT_KEYS)
        pairs.update({k: col for k, col in OPTIONAL_COUNT_KEYS.items() if k in (b.get("counts") or {}) or col in row})
        for k, col in pairs.items():
            if (b.get("counts") or {}).get(k) != fnum(row.get(col, "")):
                res.fail(field="counts." + k, package_value=(b.get("counts") or {}).get(k), csv=row[col], **key)
        codes = [g.get("code") for g in b.get("gaps", [])]
        if codes != split_list(row["gaps"]):
            res.fail(field="gaps", package_value=codes, csv=row["gaps"], **key)
        entry = index.get(env["id"]) or {}
        if (entry.get("status_by_need") or {}).get(need["id"]) != row["status"]:
            res.fail(field="index.status_by_need", csv=row["status"], **key)
        if "status_text_by_need" in entry:
            texts += 1
            first = (b.get("statements") or [{}])[0].get("text")
            if entry["status_text_by_need"].get(need["id"]) != first or not first:
                res.fail(field="index.status_text_by_need", problem="is not the first statement of the block",
                         index=str(entry["status_text_by_need"].get(need["id"]))[:100], first_statement=str(first)[:100], **key)
    for env, pack in packages(ctx):
        e = (pack or {}).get("environment") or {}
        entry = index.get(env["id"]) or {}
        if "caveat" in e or "caveat" in entry:
            if (entry.get("caveat") or None) != (e.get("caveat") or None):
                res.fail(package=env["id"], field="index.caveat", problem="differs from environment.caveat")
            want = (env["spec"].get("caveat") if env["kind"] == "scenario" else None) or None
            if (e.get("caveat") or None) != want:
                res.fail(package=env["id"], field="environment.caveat", problem="differs from scenarios.json",
                         package_value=str(e.get("caveat"))[:100], spec=str(want)[:100])
    res.numbers = {"need_blocks": res.checked, "status_texts_compared": texts}
    return res


@check("I3_atmosphere_cells",
       "atmosphere_cells.csv equals the recomputation of every oxygen bin x pressure bin of coverage.json as "
       "a scenario whose ranges are the bin edges, with no flow range and no gravity level.")
def check_i3(ctx):
    res = Result()
    evidence_index(ctx)
    have = {(r["scenario_id"], r["need_id"]): r for r in ctx.table("atmosphere_cells.csv")}
    cells = [e for e in environments(ctx) if e["kind"] == "cell"]
    by_need = {n["id"]: n for n in ctx.needs}
    would_change = 0
    for env in cells:
        marks = env_marks(ctx, env)
        for need in ctx.needs:
            res.checked += 1
            key = {"scenario_id": env["id"], "need_id": need["id"]}
            row = have.get((env["id"], need["id"]))
            if row is None:
                res.fail(problem="row missing", **key)
                continue
            exp = scenario_need_row(ctx, env, need, marks)
            would_change += 1 if exp["_pressure_only_would_change_flow_counts"] else 0
            compare_scenario_need(res, key, row, exp, {"counts", "status", "gaps"})
            if (row.get("o2_bin"), row.get("pressure_bin")) != (env["o2_bin"], env["pressure_bin"]):
                res.fail(column="o2_bin/pressure_bin", in_file="%s/%s" % (row.get("o2_bin"), row.get("pressure_bin")), **key)
            if row.get("need") != by_need[need["id"]]["name"]:
                res.fail(column="need", in_file=row.get("need"), **key)
    for k in sorted(set(have) - {(e["id"], n["id"]) for e in cells for n in ctx.needs}):
        res.fail(problem="row for an unknown cell or need", scenario_id=k[0], need_id=k[1])
    res.numbers = {"cell_x_need": res.checked, "rows_in_file": len(have),
                   "rows_where_pressure_only_tests_would_change_flow_or_gravity_counts": would_change}
    return res


def same_value(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    fa, fb = fnum(a), fnum(b)
    if fa is not None and fb is not None:
        return close(fa, fb)
    return str(a) == str(b)


@check("I4_evidence_matched_tests",
       "matched_tests of every need block is exactly the usable tests of tier atmosphere, oxygen_only or "
       "pressure_only; marks, flags, source file and row equal tests.csv; every value, unit and source "
       "column equals values_long.csv and covers the need's recorded variables.")
def check_i4(ctx):
    res = Result()
    values = 0
    for env, need, b in need_blocks(ctx):
        marks = env_marks(ctx, env)
        key = {"package": env["id"], "need_id": need["id"]}
        expected = {tid for tid in usable_ids(ctx, need["id"]) if marks[tid]["tier"] in MATCHED_TIERS}
        listed = [mt.get("test_id") for mt in b.get("matched_tests", [])]
        if set(listed) != expected or len(listed) != len(set(listed)):
            res.fail(problem="matched_tests is not the set of matched usable tests", in_file=len(listed),
                     recomputed=len(expected), only_in_file=sorted(set(listed) - expected)[:5],
                     missing=sorted(expected - set(listed))[:5], **key)
        need_vars = need["conditions_required"] + need.get("conditions_useful", []) + need["outcomes_any"]
        for mt in b.get("matched_tests", []):
            res.checked += 1
            t = ctx.tests_by_id.get(mt.get("test_id"))
            tk = dict(key, test_id=mt.get("test_id"))
            if t is None:
                res.fail(problem="unknown test", **tk)
                continue
            want = dict(marks[t["test_id"]], investigation_id=t["investigation_id"], source_id=t["source_id"],
                        source_file=t["source_file"], fuel_phase=t.get("fuel_phase", ""))
            for k, w in want.items():
                if k in ("added_gas", "fuel_phase") and k not in mt:
                    continue
                if mt.get(k) != w:
                    res.fail(field=k, package_value=mt.get(k), recomputed=w, **tk)
            if not same_value(mt.get("source_row"), t["source_row"]):
                res.fail(field="source_row", package_value=mt.get("source_row"), tests_csv=t["source_row"], **tk)
            if list(mt.get("flags") or []) != split_list(t["flags"]):
                res.fail(field="flags", package_value=mt.get("flags"), tests_csv=t["flags"], **tk)
            recorded = [v for v in dict.fromkeys(need_vars) if t.get(v, "") != ""]
            got = mt.get("values") or {}
            if sorted(got) != sorted(recorded):
                res.fail(field="values (variables)", only_in_package=sorted(set(got) - set(recorded)),
                         missing=sorted(set(recorded) - set(got)), **tk)
            for var in recorded:
                if var not in got:
                    continue
                values += 1
                rows = ctx.values_index.get((t["test_id"], var), [])
                if len(rows) != 1:
                    res.fail(field="values." + var, problem="no single values_long row", **tk)
                    continue
                r = rows[0]
                g = got[var]
                if not same_value(g.get("value"), r["value"]) or g.get("unit") != r["unit"] or \
                        g.get("source_column") != r["source_column"]:
                    res.fail(field="values." + var, package_value=g, values_long=[r["value"], r["unit"], r["source_column"]], **tk)
    res.numbers = {"matched_test_entries": res.checked, "values_compared": values}
    return res


@check("I5_evidence_need_context",
       "objective entries equal the links of needs.json, the investigations list equals the usable tests per "
       "investigation and tier with the title of the PSI record, references equal the need's items in "
       "references.json, and every gap code has a sentence.")
def check_i5(ctx):
    res = Result()
    links = {}
    for r in link_rows(ctx):
        links.setdefault(r["need_id"], []).append(dict({"investigation_id": r["investigation_id"]}, **{f: r[f] for f in LINK_FIELDS}))
    for env, need, b in need_blocks(ctx):
        res.checked += 1
        marks = env_marks(ctx, env)
        key = {"package": env["id"], "need_id": need["id"]}
        got = [dict({"investigation_id": o.get("investigation_id")}, **{f: o.get(f) or "" for f in LINK_FIELDS})
               for o in b.get("objective", [])]
        if got != links.get(need["id"], []):
            res.fail(field="objective", problem="differs from the links of needs.json (all verdicts, with "
                     "publication item and quote)", in_package=len(got), in_spec=len(links.get(need["id"], [])), **key)
        per = {}
        for tid in usable_ids(ctx, need["id"]):
            inv = ctx.tests_by_id[tid]["investigation_id"]
            per.setdefault(inv, dict.fromkeys(TIERS, 0))[marks[tid]["tier"]] += 1
        want = [dict({"investigation_id": inv, "title": ctx.record(inv).get("title")}, **per[inv])
                for inv in sorted(per, key=psi_key)]
        got = sorted(b.get("investigations", []), key=lambda x: psi_key(x.get("investigation_id")))
        if got != want:
            res.fail(field="investigations", package_value=got[:3], recomputed=want[:3], **key)
        refs = [reference_view(ctx, i) for i in need.get("references", []) if i in ctx.reference_items]
        if [{k: r.get(k) for k in REFERENCE_KEYS} for r in b.get("references", [])] != refs:
            res.fail(field="references", problem="differs from needs.json + references.json", **key)
        for g in b.get("gaps", []):
            if not g.get("text"):
                res.fail(field="gaps", problem="gap code without a sentence", code=g.get("code"), **key)
        if "matched_by_fuel_phase" in b:
            phases = {}
            for tid in usable_ids(ctx, need["id"]):
                if marks[tid]["tier"] in MATCHED_TIERS:
                    ph = ctx.tests_by_id[tid].get("fuel_phase", "")
                    phases[ph] = phases.get(ph, 0) + 1
            if b["matched_by_fuel_phase"] != phases:
                res.fail(field="matched_by_fuel_phase", package_value=b["matched_by_fuel_phase"], recomputed=phases, **key)
        for f in ("reading", "note"):
            if f in b and (b[f] or None) != (need.get(f) or None):
                res.fail(field=f, problem="differs from needs.json", **key)
    res.numbers = {"need_blocks": res.checked}
    return res


@check("I6_evidence_usable_elsewhere",
       "usable_elsewhere of every need block (tests of tier other: how many, lowest and highest recorded "
       "ambient oxygen and pressure, investigations) equals the recomputation from tests.csv.")
def check_i6(ctx):
    res = Result()
    for env, need, b in need_blocks(ctx):
        res.checked += 1
        marks = env_marks(ctx, env)
        key = {"package": env["id"], "need_id": need["id"]}
        other = [ctx.tests_by_id[tid] for tid in usable_ids(ctx, need["id"]) if marks[tid]["tier"] == "other"]
        o2 = [fnum(t["o2_pct"]) for t in other if t.get("o2_pct", "") != "" and t.get("o2_basis") == "ambient"]
        not_ambient = sum(1 for t in other if t.get("o2_pct", "") != "" and t.get("o2_basis") != "ambient")
        pr = [fnum(t["pressure_kpa"]) for t in other if t.get("pressure_kpa", "") != ""]
        got = b.get("usable_elsewhere") or {}
        want = {"tests": len(other),
                "o2_pct.recorded": len(o2), "o2_pct.min": min(o2) if o2 else None, "o2_pct.max": max(o2) if o2 else None,
                "o2_pct.not_ambient": not_ambient,
                "pressure_kpa.recorded": len(pr), "pressure_kpa.min": min(pr) if pr else None,
                "pressure_kpa.max": max(pr) if pr else None}
        for path, w in want.items():
            g = got
            for part in path.split("."):
                g = (g or {}).get(part) if isinstance(g, dict) else None
            if path == "o2_pct.not_ambient" and g is None and w == 0:
                continue
            if (g is None) != (w is None) or (w is not None and not close(float(g), float(w))):
                res.fail(field="usable_elsewhere." + path, package_value=g, recomputed=w, **key)
        invs = sorted({t["investigation_id"] for t in other}, key=psi_key)
        if got.get("investigation_ids") != invs:
            res.fail(field="usable_elsewhere.investigation_ids", package_value=got.get("investigation_ids"), recomputed=invs, **key)
    res.numbers = {"need_blocks": res.checked}
    return res


@check("I10_evidence_recorded_tests",
       "environment.recorded_tests of every package lists, per investigation and fuel phase, how many tests of "
       "tests.csv (whatever the need) have tier atmosphere, oxygen_only or pressure_only in that environment, "
       "and 'counted_for' names the needs that count at least one of these matched tests.")
def check_i10(ctx):
    res = Result()
    seen = False
    counted = 0
    for env, pack in packages(ctx):
        e = (pack or {}).get("environment") or {}
        if "recorded_tests" not in e:
            continue
        seen = True
        res.checked += 1
        marks = env_marks(ctx, env)
        groups = {}
        for t in ctx.tests:
            tier = marks[t["test_id"]]["tier"]
            if tier in MATCHED_TIERS:
                g = groups.setdefault((t["investigation_id"], t.get("fuel_phase", "")), dict.fromkeys(MATCHED_TIERS, 0))
                g[tier] += 1
        got = {(r.get("investigation_id"), r.get("fuel_phase")): {k: r.get(k) for k in MATCHED_TIERS} for r in e["recorded_tests"]}
        if got != groups:
            diff = sorted(k for k in set(got) | set(groups) if got.get(k) != groups.get(k))
            res.fail(package=env["id"], differing_groups=["%s/%s" % k for k in diff][:6],
                     package_value=[got.get(k) for k in diff][:3], recomputed=[groups.get(k) for k in diff][:3])
        for r in e["recorded_tests"]:
            inv = r.get("investigation_id")
            if "title" in r and os.path.exists(os.path.join(CATALOG, "%s.json" % inv)) and r["title"] != ctx.record(inv).get("title"):
                res.fail(package=env["id"], investigation_id=inv, field="title")
            if "counted_for" in r:
                counted += 1
                want = [n["id"] for n in ctx.needs if any(
                    marks[tid]["tier"] in MATCHED_TIERS and ctx.tests_by_id[tid]["investigation_id"] == inv
                    and ctx.tests_by_id[tid].get("fuel_phase", "") == r.get("fuel_phase")
                    for tid in usable_ids(ctx, n["id"]))]
                if r["counted_for"] != want:
                    res.fail(package=env["id"], investigation_id=inv, fuel_phase=r.get("fuel_phase"), field="counted_for",
                             package_value=r["counted_for"], recomputed=want)
    if not seen:
        raise Skip("no package carries environment.recorded_tests")
    res.numbers = {"packages": res.checked, "counted_for_lists": counted}
    return res


@check("I11_evidence_matched_ranges",
       "matched_ranges of every need block (how many matched tests record oxygen of the surrounding "
       "atmosphere and pressure, with the lowest and highest recorded value) equals the recomputation from "
       "tests.csv over the counted tests of tier atmosphere, oxygen_only or pressure_only.")
def check_i11(ctx):
    res = Result()
    seen = False
    for env, need, b in need_blocks(ctx):
        if "matched_ranges" not in b:
            continue
        seen = True
        res.checked += 1
        marks = env_marks(ctx, env)
        key = {"package": env["id"], "need_id": need["id"]}
        matched = [ctx.tests_by_id[tid] for tid in usable_ids(ctx, need["id"]) if marks[tid]["tier"] in MATCHED_TIERS]
        o2 = [fnum(t["o2_pct"]) for t in matched if t.get("o2_pct", "") != "" and t.get("o2_basis") == "ambient"]
        pr = [fnum(t["pressure_kpa"]) for t in matched if t.get("pressure_kpa", "") != ""]
        want = {"o2_pct": o2, "pressure_kpa": pr}
        for var, values in want.items():
            g = (b["matched_ranges"] or {}).get(var) or {}
            exp = {"recorded": len(values), "min": min(values) if values else None, "max": max(values) if values else None}
            for k, w in exp.items():
                if (g.get(k) is None) != (w is None) or (w is not None and not close(float(g[k]), float(w))):
                    res.fail(field="matched_ranges.%s.%s" % (var, k), package_value=g.get(k), recomputed=w, **key)
            if "unit" in g and g["unit"] != ctx.var_unit.get(var, ""):
                res.fail(field="matched_ranges.%s.unit" % var, package_value=g["unit"], **key)
        if "not_ambient" in ((b["matched_ranges"] or {}).get("o2_pct") or {}):
            n = sum(1 for t in matched if t.get("o2_pct", "") != "" and t.get("o2_basis") != "ambient")
            if b["matched_ranges"]["o2_pct"]["not_ambient"] != n:
                res.fail(field="matched_ranges.o2_pct.not_ambient", package_value=b["matched_ranges"]["o2_pct"]["not_ambient"],
                         recomputed=n, **key)
    if not seen:
        raise Skip("no need block carries matched_ranges")
    res.numbers = {"need_blocks": res.checked}
    return res


def package_indicators(ctx, env, need):
    """Indicator entries of a need recomputed over the tests of their population that are matched here."""
    marks = env_marks(ctx, env)
    out = {}
    for ind in ctx.spec("indicators")["indicators"]:
        if ind["need_id"] != need["id"]:
            continue
        subset = [tid for tid in population_ids(ctx, ind) if marks[tid]["tier"] in MATCHED_TIERS]
        rows, tests = compute_indicator(ctx, ind, subset)
        for (label, stat, cat), (value, n, invs) in rows.items():
            entry = out.setdefault((ind["id"], label), {"n_tests": n, "investigation_ids": invs, "values": {},
                                                        "test_ids": set(), "spec": ind})
            entry["values"][(stat, cat)] = value
        for (label, tid) in tests:
            out[(ind["id"], label)]["test_ids"].add(tid)
    return out


@check("I7_evidence_indicators",
       "The indicators of every need block equal the need's indicators recomputed over the tests of their "
       "population whose tier in this environment is atmosphere, oxygen_only or pressure_only.")
def check_i7(ctx):
    res = Result()
    for env, need, b in need_blocks(ctx):
        expected = package_indicators(ctx, env, need)
        got = {}
        key = {"package": env["id"], "need_id": need["id"]}
        for e in b.get("indicators", []):
            k = (e.get("indicator_id"), e.get("group"))
            if k in got:
                res.fail(problem="indicator group listed twice", indicator_id=k[0], group=k[1], **key)
            got[k] = e
        for k in sorted(set(expected) | set(got), key=str):
            res.checked += 1
            ik = dict(key, indicator_id=k[0], group=k[1])
            if k not in got:
                res.fail(problem="indicator group missing", **ik)
                continue
            if k not in expected:
                res.fail(problem="indicator group not produced by the rule", **ik)
                continue
            e, x = got[k], expected[k]
            ind = x["spec"]
            vals = {(v.get("stat"), v.get("category") or ""): v.get("value") for v in e.get("values", [])}
            if set(vals) != set(x["values"]) or any(not near(fnum(vals[s]), float(x["values"][s]), STAT_TOL) for s in vals if s in x["values"]):
                res.fail(field="values", package_value=sorted(vals.items(), key=str)[:4],
                         recomputed=sorted(x["values"].items(), key=str)[:4], **ik)
            if e.get("n_tests") != x["n_tests"]:
                res.fail(field="n_tests", package_value=e.get("n_tests"), recomputed=x["n_tests"], **ik)
            if set(e.get("test_ids") or []) != x["test_ids"]:
                res.fail(field="test_ids", package_value=len(e.get("test_ids") or []), recomputed=len(x["test_ids"]), **ik)
            if list(e.get("investigation_ids") or []) != x["investigation_ids"]:
                res.fail(field="investigation_ids", package_value=e.get("investigation_ids"), recomputed=x["investigation_ids"], **ik)
            texts = {"template": ind["template"], "population": ind.get("population", "usable"),
                     "variable": ind["variable"], "unit": ctx.var_unit.get(ind["variable"], ""),
                     "label": ind["label"], "reading": ind.get("reading", ""), "need_id": ind["need_id"]}
            for f, w in texts.items():
                if e.get(f) != w:
                    res.fail(field=f, package_value=str(e.get(f))[:60], spec=str(w)[:60], **ik)
    res.numbers = {"indicator_groups": res.checked}
    return res


_TEXT_NUMBER = re.compile(r"\d+(?:\.\d+)?")


def numbers_of(obj, out=None):
    """Every number in a JSON value: numeric fields and numbers written inside texts (sign ignored)."""
    out = set() if out is None else out
    if isinstance(obj, bool) or obj is None:
        return out
    if isinstance(obj, (int, float)):
        out.add(round(abs(float(obj)), 9))
    elif isinstance(obj, str):
        out.update(round(float(m), 9) for m in _TEXT_NUMBER.findall(obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            numbers_of(k, out)
            numbers_of(v, out)
    elif isinstance(obj, (list, tuple, set)):
        for v in obj:
            numbers_of(v, out)
    return out


def text_numbers(text):
    return [round(float(m), 9) for m in _TEXT_NUMBER.findall(text or "")]


@check("I8_evidence_statement_numbers",
       "Every number written in a statement of an evidence package is a field of the same need block (for an "
       "indicator sentence: of its indicator entry; for an environment sentence: of its recorded_tests row), "
       "or one of the two sums that statements.json declares.")
def check_i8(ctx):
    res = Result()
    computed_only = 0
    listed_only = 0
    sentences = 0
    for env, need, b in need_blocks(ctx):
        pack_env = None
        for e, pack in packages(ctx):
            if e["id"] == env["id"]:
                pack_env = (pack or {}).get("environment") or {}
        counts = b.get("counts") or {}
        heavy = ("statements", "matched_tests", "indicators", "references", "gaps")
        base = numbers_of({k: v for k, v in b.items() if k not in heavy})
        numbers_of([g.get("code") for g in b.get("gaps", [])], base)
        numbers_of({k: pack_env.get(k) for k in ("id", "label", "ranges", "gravity_level", "nominal")}, base)
        rest = numbers_of({k: b.get(k) for k in ("matched_tests", "indicators", "references")})
        declared = {round(float(len(b.get("matched_tests", []))), 9),
                    round(float((counts.get("atmosphere") or 0) + (counts.get("oxygen_only") or 0)), 9)}
        entries = {(e.get("indicator_id"), e.get("group")): e for e in b.get("indicators", [])}
        for s in b.get("statements", []):
            sentences += 1
            key = {"package": env["id"], "need_id": need["id"], "statement": s.get("id")}
            if "indicator_id" in s or str(s.get("id", "")).startswith("indicator."):
                entry = entries.get((s.get("indicator_id"), s.get("group")))
                if entry is None:
                    res.fail(problem="indicator sentence without its indicator entry", indicator_id=s.get("indicator_id"),
                             group=s.get("group"), **key)
                    continue
                pool, extra = numbers_of(entry), set()
            else:
                pool, extra = base, declared
            for n in text_numbers(s.get("text")):
                res.checked += 1
                if n in pool:
                    continue
                if n in extra:
                    computed_only += 1
                    continue
                if pool is base and n in rest:
                    listed_only += 1
                    continue
                res.fail(number=n, text=s.get("text", "")[:200], **key)
    for env, pack in packages(ctx):
        e = (pack or {}).get("environment") or {}
        rows = {(r.get("investigation_id"), r.get("fuel_phase")): r for r in e.get("recorded_tests", [])}
        wide = numbers_of({k: v for k, v in e.items() if k != "statements"})
        for s in e.get("statements", []):
            sentences += 1
            row = rows.get((s.get("investigation_id"), s.get("fuel_phase")))
            pool = numbers_of(row) if row is not None else wide
            for n in text_numbers(s.get("text")):
                res.checked += 1
                if n not in pool:
                    res.fail(package=env["id"], statement=s.get("id"), number=n, text=s.get("text", "")[:200],
                             investigation_id=s.get("investigation_id"))
    res.numbers = {"numbers_in_statements": res.checked, "statements": sentences,
                   "numbers_that_are_a_declared_sum_not_a_stored_field": computed_only,
                   "numbers_found_only_in_matched_tests_indicators_or_references": listed_only}
    res.details = {"note": "statements.json declares two computed fields: the number of entries of matched_tests "
                           "and counts.atmosphere + counts.oxygen_only. A number found only there is counted "
                           "apart; it is recomputed here from the block."}
    return res


def forbidden_in(text, spec_texts):
    """Forbidden words in a sentence, after removing texts copied from the spec (need names, readings)."""
    for piece in sorted(spec_texts, key=len, reverse=True):
        if piece:
            text = text.replace(piece, " ")
    return sorted({m.group(0).lower() for m in re.finditer(r"\b(%s)\b" % "|".join(FORBIDDEN_WORDS), text, re.I)})


def verbatim_quotes(ctx):
    """Sentences copied word for word from a NASA record or a publication: the quotes of references.json
    items and the record sentences of needs.json, sources.json and scenarios.json. A forbidden word inside
    such a quote is the source's word, not the team's; it is counted apart."""
    def load():
        quotes = [it.get("quote") or "" for _, it in ctx.reference_items.values()]
        quotes += [s.get("quote") or "" for n in ctx.needs for s in n.get("stated_by", [])]
        quotes += [e.get("quote") or "" for s in ctx.sources for e in s.get("documented_elsewhere", [])]
        quotes += [e.get("quote") or "" for s in ctx.spec("scenarios")["scenarios"] for e in s.get("see_also", [])]
        return [q for q in quotes if q]
    return ctx._get("verbatim_quotes", load)


def copied_spec_texts(ctx):
    texts = [n["name"] for n in ctx.needs]
    texts += [i.get("reading", "") for i in ctx.spec("indicators")["indicators"]]
    return texts


@check("I9_evidence_statement_words",
       "No statement of an evidence package contains the words safe, unsafe, flammable, sufficient, "
       "representative, proves or confirms (outside a need name or an indicator reading copied from the spec, "
       "and outside a sentence quoted word for word from a NASA record or a publication).")
def check_i9(ctx):
    res = Result()
    spec_texts = copied_spec_texts(ctx)
    quotes = verbatim_quotes(ctx)
    quoted_only = 0
    sentences = [(env["id"], need["id"], s) for env, need, b in need_blocks(ctx)
                 for s in b.get("statements", []) + [{"id": "gap:" + str(g.get("code")), "text": g.get("text")} for g in b.get("gaps", [])]]
    sentences += [(env["id"], "", s) for env, pack in packages(ctx)
                  for s in ((pack or {}).get("environment") or {}).get("statements", [])]
    for package, need_id, s in sentences:
        res.checked += 1
        if forbidden_in(s.get("text") or "", spec_texts):
            words = forbidden_in(s.get("text") or "", spec_texts + quotes)
            if words:
                res.fail(package=package, need_id=need_id, statement=s.get("id"), words=words,
                         text=(s.get("text") or "")[:200])
            else:
                quoted_only += 1
    res.numbers = {"sentences": res.checked, "sentences_with_such_a_word_only_inside_a_verbatim_quote": quoted_only}
    return res


# ----------------------------------------------------------------------------
# J. investigation facts (contract section 4)
# ----------------------------------------------------------------------------

def facts(ctx):
    if not ctx.has("investigation_facts.json"):
        raise Skip("data/pipeline/investigation_facts.json does not exist yet")
    return ctx.json("investigation_facts.json").get("investigations", [])


def catalog_ids():
    return sorted((f[:-5] for f in os.listdir(CATALOG) if f.endswith(".json")), key=psi_key)


def expected_test_rows(ctx, source):
    """Non-empty data rows of a raw table, and those that have every 'require' column."""
    table = ctx.raw(source["file"])
    header = table[0]
    require = [c.strip() for c in source.get("require", [])]
    rows = [r for r in table[1:] if any(r)]
    kept = [r for r in rows if all(c in header and header.index(c) < len(r) and r[header.index(c)] != "" for c in require)]
    return len(rows), len(kept)


@check("J1_facts_entries",
       "investigation_facts.json has one entry per PSI record (numeric order) with title, acronym, DOI "
       "and license of the record, its tables as in sources.json, and test counts that add up to tests.csv.")
def check_j1(ctx):
    res = Result()
    entries = facts(ctx)
    ids = [e.get("investigation_id") for e in entries]
    if ids != catalog_ids():
        res.fail(problem="entries are not the PSI records in numeric order", in_file=ids, expected=catalog_ids())
    if len(entries) != len(catalog_ids()):
        res.fail(problem="number of entries", in_file=len(entries), expected=len(catalog_ids()))
    total = sum(e.get("tests") or 0 for e in entries)
    if total != len(ctx.tests):
        res.fail(problem="tests do not add up to tests.csv", sum_of_entries=total, tests_csv=len(ctx.tests))
    per_inv, per_source = {}, {}
    for t in ctx.tests:
        per_inv[t["investigation_id"]] = per_inv.get(t["investigation_id"], 0) + 1
        per_source[t["source_id"]] = per_source.get(t["source_id"], 0) + 1
    for e in entries:
        res.checked += 1
        inv = e.get("investigation_id")
        key = {"investigation_id": inv}
        if not os.path.exists(os.path.join(CATALOG, "%s.json" % inv)):
            res.fail(problem="no PSI record", **key)
            continue
        rec = ctx.record(inv)
        lic = e.get("license")
        lic_id = lic.get("identifier") if isinstance(lic, dict) else lic
        want = {"title": rec.get("title"), "acronym": rec.get("investigationAcronym") or None, "doi": rec.get("doi") or None}
        for k, w in want.items():
            if (e.get(k) or None) != w:
                res.fail(field=k, in_file=e.get(k), psi_record=w, **key)
        if (lic_id or None) != (rec.get("licenseIdentifier") or None):
            res.fail(field="license", in_file=lic, psi_record=rec.get("licenseIdentifier"), **key)
        if e.get("tests") != per_inv.get(inv, 0):
            res.fail(field="tests", in_file=e.get("tests"), tests_csv=per_inv.get(inv, 0), **key)
        sources = [s for s in ctx.sources if s["investigation_id"] == inv]
        tables = {t.get("source_id"): t for t in e.get("tables", [])}
        if sorted(tables) != sorted(s["id"] for s in sources):
            res.fail(field="tables", in_file=sorted(tables), sources_json=sorted(s["id"] for s in sources), **key)
        if not sources and (rec.get("experimentalTable") or []):
            res.fail(problem="the PSI record lists an experimental table that sources.json does not map", **key)
        level = [s for s in sources if "columns" in s]
        status = "no_experimental_table" if not sources else "test_level" if len(level) == len(sources) else \
            "not_test_level" if not level else "mixed"
        if "table_status" in e and e["table_status"] != status:
            res.fail(field="table_status", in_file=e["table_status"], recomputed=status, **key)
        for s in sources:
            t = tables.get(s["id"])
            if t is None:
                continue
            tk = dict(key, source_id=s["id"])
            want = {"file": s["file"], "row_unit": s.get("row_unit"), "tests": per_source.get(s["id"], 0)}
            if "columns" not in s:
                if s.get("not_standardized") not in [v for v in t.values() if isinstance(v, str)]:
                    res.fail(field="reason not test-level", sources_json=s.get("not_standardized"), **tk)
            else:
                read, kept = expected_test_rows(ctx, s)
                want.update(rows_read=read, rows_skipped=read - kept)
                header = ctx.raw(s["file"])[0]
                mapped = {c["from"].strip() for c in s["columns"]} | set(re.findall(r"\{([^}]*)\}", s["test_id"]))
                want["source_columns_not_mapped"] = [h for h in header if h and h not in mapped]
                want["constants"] = s.get("constants") or {}
                cmap = {}
                for c in s["columns"]:
                    for v in (c["to"] if isinstance(c["to"], list) else [c["to"]]):
                        cmap.setdefault(v, []).append(c["from"].strip())
                want["column_map"] = cmap
                want["unit_factors"] = {c["to"]: c["params"]["factor"] for c in s["columns"]
                                        if isinstance(c["to"], str) and (c.get("params") or {}).get("factor") is not None}
            for k, w in want.items():
                if k in t and t[k] != w:
                    if isinstance(w, dict) and isinstance(t[k], dict) and \
                            {a: sorted(b) if isinstance(b, list) else b for a, b in t[k].items()} == \
                            {a: sorted(b) if isinstance(b, list) else b for a, b in w.items()}:
                        continue
                    res.fail(field=k, in_file=str(t[k])[:160], recomputed=str(w)[:160], **tk)
                elif k not in t and k in ("file", "tests"):
                    res.fail(field=k, problem="missing", **tk)
    res.numbers = {"entries": len(entries), "psi_records": len(catalog_ids()), "tests_in_entries": total,
                   "tests_csv": len(ctx.tests)}
    return res


def variable_facts(ctx, tests, var):
    values = [t[var] for t in tests if t.get(var, "") != ""]
    nums = [fnum(v) for v in values]
    if values and all(n is not None for n in nums):
        return {"n": len(values), "type": "number", "min": min(nums), "max": max(nums)}
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return {"n": len(values), "type": "category", "counts": counts}


def compare_variables(ctx, res, key, got, tests, limit, split_by, check_columns=False):
    recorded = [v for v in ctx.variable_columns if any(t.get(v, "") != "" for t in tests)]
    if sorted(got) != sorted(recorded):
        res.fail(problem="variables listed differ from those with a value", only_in_file=sorted(set(got) - set(recorded)),
                 missing=sorted(set(recorded) - set(got)), **key)
    n = 0
    for var in recorded:
        if var not in got:
            continue
        n += 1
        g, x = got[var], variable_facts(ctx, tests, var)
        vk = dict(key, variable=var)
        if g.get("n") != x["n"]:
            res.fail(field="n", in_file=g.get("n"), recomputed=x["n"], **vk)
        if "unit" in g and g["unit"] != ctx.var_unit.get(var, ""):
            res.fail(field="unit", in_file=g["unit"], **vk)
        if x["type"] == "number":
            if not close(fnum(g.get("min")), x["min"]) or not close(fnum(g.get("max")), x["max"]):
                res.fail(field="min/max", in_file=[g.get("min"), g.get("max")], recomputed=[x["min"], x["max"]], **vk)
        else:
            listed = g.get("values") or {}
            top = sorted(x["counts"].items(), key=lambda kv: -kv[1])
            if any(x["counts"].get(k) != c for k, c in listed.items()):
                res.fail(field="values", in_file=dict(list(listed.items())[:5]), recomputed=dict(top[:5]), **vk)
            elif "distinct" in g and g["distinct"] != len(x["counts"]):
                res.fail(field="distinct", in_file=g["distinct"], recomputed=len(x["counts"]), **vk)
            elif len(listed) != min(len(x["counts"]), limit) or (len(listed) < len(x["counts"])) != bool(g.get("values_truncated")):
                res.fail(field="values (how many are listed)", in_file=len(listed), distinct=len(x["counts"]), **vk)
            elif listed and min(listed.values()) < max([c for k, c in x["counts"].items() if k not in listed] or [0]):
                res.fail(field="values (not the most frequent)", **vk)
        if var in split_by:
            by = (g.get("by") or {}).get(split_by[var]) or {}
            parts = {}
            for t in tests:
                if t.get(var, "") != "":
                    parts.setdefault(t.get(split_by[var], ""), []).append(t)
            if sorted(by) != sorted(parts):
                res.fail(field="by." + split_by[var], in_file=sorted(by), recomputed=sorted(parts), **vk)
            for name, sub in parts.items():
                xs = variable_facts(ctx, sub, var)
                gs = by.get(name) or {}
                if gs.get("n") != xs["n"] or not close(fnum(gs.get("min")), xs.get("min")) or not close(fnum(gs.get("max")), xs.get("max")):
                    res.fail(field="by.%s.%s" % (split_by[var], name), in_file=gs, recomputed=xs, **vk)
        if check_columns and "source_columns" in g:
            cols = {r["source_column"] for t in tests for r in ctx.values_index.get((t["test_id"], var), [])}
            if set(g["source_columns"]) != cols:
                res.fail(field="source_columns", in_file=g["source_columns"], values_long=sorted(cols), **vk)
    return n


@check("J2_facts_variables",
       "For every investigation and every table, the listed variables are exactly those with a value, and "
       "each n, min, max and value count equals the recomputation from tests.csv.")
def check_j2(ctx):
    res = Result()
    entries = facts(ctx)
    fs_path = os.path.join(SPEC, "fact_statements.json")
    fs = read_json(fs_path) if os.path.exists(fs_path) else {}
    limit = fs.get("max_category_values", 10 ** 9)
    split_by = fs.get("split_by", {})
    for e in entries:
        inv = e.get("investigation_id")
        tests = [t for t in ctx.tests if t["investigation_id"] == inv]
        res.checked += compare_variables(ctx, res, {"investigation_id": inv}, e.get("variables") or {}, tests, limit, split_by)
        for tab in e.get("tables", []):
            if "variables" not in tab:
                continue
            sub = [t for t in tests if t["source_id"] == tab.get("source_id")]
            res.checked += compare_variables(ctx, res, {"investigation_id": inv, "source_id": tab.get("source_id")},
                                             tab["variables"], sub, limit, split_by, check_columns=True)
        flags = {}
        for t in tests:
            for f in split_list(t["flags"]):
                flags[f] = flags.get(f, 0) + 1
        if "flags" in e and e["flags"] != flags:
            res.fail(investigation_id=inv, field="flags", in_file=dict(list(e["flags"].items())[:4]),
                     recomputed=dict(list(flags.items())[:4]))
    res.numbers = {"variable_summaries": res.checked}
    return res


@check("J3_facts_needs",
       "stated_needs of every investigation equal the links of needs.json, and capability equals the rows of "
       "capability_matrix.csv (status, counts, objective_link per need and table).")
def check_j3(ctx):
    res = Result()
    links = {}
    for r in link_rows(ctx):
        links.setdefault(r["investigation_id"], []).append((r["need_id"],) + tuple(r[f] for f in LINK_FIELDS))
    matrix = {}
    for r in ctx.table("capability_matrix.csv"):
        matrix.setdefault(r["investigation_id"], {}).setdefault(r["need_id"], {})[r["source_id"]] = r
    names = {n["id"]: n["name"] for n in ctx.needs}
    for e in facts(ctx):
        inv = e.get("investigation_id")
        key = {"investigation_id": inv}
        res.checked += 1
        got = [(s.get("need_id"),) + tuple(s.get(f) or "" for f in LINK_FIELDS) for s in e.get("stated_needs", [])]
        if sorted(got) != sorted(links.get(inv, [])):
            res.fail(field="stated_needs", problem="differs from the links of needs.json (all verdicts, with "
                     "publication item and quote)", in_file=len(got), in_spec=len(links.get(inv, [])), **key)
        for s in e.get("stated_needs", []):
            if "need" in s and s["need"] != names.get(s.get("need_id")):
                res.fail(field="stated_needs.need", in_file=s["need"], **key)
        level = [s["id"] for s in ctx.sources if s["investigation_id"] == inv]
        cap = {c.get("need_id"): c for c in e.get("capability") or []}
        if not level:
            if cap:
                res.fail(field="capability", problem="given for an investigation without an experimental table", **key)
            continue
        if sorted(cap) != sorted(names):
            res.fail(field="capability", problem="not one entry per need", in_file=sorted(cap), **key)
        for need_id, c in cap.items():
            res.checked += 1
            nk = dict(key, need_id=need_id)
            rows = {sid: r for sid, r in (matrix.get(inv, {}).get(need_id, {})).items() if sid in level}
            if not rows:
                res.fail(problem="no capability_matrix row", **nk)
                continue
            link = {r["objective_link"] for r in rows.values()}
            usable = sum(int(fnum(r["usable_tests"])) for r in rows.values())
            want = {"objective_link": link.pop() if len(link) == 1 else None,
                    "tests_in_scope": sum(int(fnum(r["tests"])) for r in rows.values()), "usable_tests": usable}
            want["counted_tests"] = usable if want["objective_link"] == "stated" else 0
            want["recorded_outside_objective"] = 0 if want["objective_link"] == "stated" else usable
            want["statuses"] = {sid: r["status"] for sid, r in rows.items()}
            for k, w in want.items():
                if k in c and c[k] != w:
                    res.fail(field=k, in_file=c[k], capability_matrix=w, **nk)
                elif k not in c and k in ("objective_link", "usable_tests"):
                    res.fail(field=k, problem="missing", **nk)
            by_table = {b.get("source_id"): b for b in c.get("by_table", [])}
            if "by_table" in c and sorted(by_table) != sorted(rows):
                res.fail(field="by_table", in_file=sorted(by_table), capability_matrix=sorted(rows), **nk)
            for sid, b in by_table.items():
                r = rows.get(sid)
                if r is None:
                    continue
                wt = {"status": r["status"], "tests_in_scope": int(fnum(r["tests"])),
                      "tests_with_required_conditions": int(fnum(r["tests_with_required_conditions"])),
                      "tests_with_outcome": int(fnum(r["tests_with_outcome"])), "usable_tests": int(fnum(r["usable_tests"])),
                      "required_missing": split_list(r["required_missing"]), "outcomes_present": split_list(r["outcomes_present"])}
                for k, w in wt.items():
                    if k in b and b[k] != w:
                        res.fail(field="by_table.%s.%s" % (sid, k), in_file=b[k], capability_matrix=w, **nk)
    res.numbers = {"entries_and_need_rows": res.checked}
    return res


@check("J4_facts_statements",
       "Every number written in a statement of investigation_facts.json is a field of the same entry (of the "
       "table or need the sentence is about), and no statement contains a word that judges safety or sufficiency.")
def check_j4(ctx):
    res = Result()
    spec_texts = copied_spec_texts(ctx)
    wider = 0
    quoted_only = 0
    sentences = 0
    for e in facts(ctx):
        inv = e.get("investigation_id")
        whole = numbers_of({k: v for k, v in e.items() if k != "statements"})
        tables = {t.get("source_id"): t for t in e.get("tables", [])}
        caps = {c.get("need_id"): c for c in e.get("capability") or []}
        top = numbers_of({k: v for k, v in e.items() if k not in ("statements", "tables", "capability", "stated_needs")})
        for s in e.get("statements", []):
            sentences += 1
            about = str(s.get("about", ""))
            need_id, _, source_id = about.partition("/")
            if about == inv:
                pool = top
            elif about in tables:
                pool = numbers_of(tables[about]) | numbers_of(inv)
            elif need_id in caps or any(x.get("need_id") == need_id for x in e.get("stated_needs", [])):
                pool = numbers_of(caps.get(need_id)) | numbers_of(inv) | \
                    numbers_of([x for x in e.get("stated_needs", []) if x.get("need_id") == need_id])
                if source_id in tables:
                    pool |= numbers_of({k: tables[source_id].get(k) for k in ("file", "source_id", "tests")})
                else:
                    pool |= numbers_of([{k: t.get(k) for k in ("file", "source_id")} for t in tables.values()])
            else:
                pool = whole
            key = {"investigation_id": inv, "statement": s.get("id"), "about": about}
            for n in text_numbers(s.get("text")):
                res.checked += 1
                if n in pool:
                    continue
                if n in whole:
                    wider += 1
                    continue
                res.fail(number=n, text=(s.get("text") or "")[:200], **key)
            quotes = [x.get("quote", "") for x in e.get("stated_needs", [])] + [e.get("title") or ""] + \
                     [str(v) for t in tables.values() for v in t.values() if isinstance(v, str)]
            if forbidden_in(s.get("text") or "", spec_texts + quotes):
                words = forbidden_in(s.get("text") or "", spec_texts + quotes + verbatim_quotes(ctx))
                if words:
                    res.fail(problem="forbidden word", words=words, text=(s.get("text") or "")[:200], **key)
                else:
                    quoted_only += 1
    res.numbers = {"numbers_in_statements": res.checked, "statements": sentences,
                   "numbers_found_only_elsewhere_in_the_entry": wider,
                   "sentences_with_a_forbidden_word_only_inside_a_verbatim_quote": quoted_only}
    return res


# ----------------------------------------------------------------------------
# spot-check sheet for a human with the NASA page open
# ----------------------------------------------------------------------------

SPOT_COLUMNS = ["table", "investigation_id", "psi_url", "source_file", "source_row", "source_column", "raw_cell",
                "variable", "pipeline_value", "unit", "how_related", "checked_by", "same_as_nasa_page", "comment"]


def write_spot_check(ctx, path):
    """For each test-level table: up to 20 values with a real source column, drawn with a fixed seed, at
    most 4 per variable (the cap is raised only when a table has too few variables to reach 20)."""
    by_file = {}
    for item in trace_rows(ctx):
        if item["cell"] is not None:
            by_file.setdefault(item["row"]["source_file"], []).append(item)
    out = []
    for order, s in enumerate(ctx.sources):
        if "columns" not in s:
            continue
        items = sorted(by_file.get(s["file"], []), key=lambda i: (int(fnum(i["row"]["source_row"])), i["row"]["variable"]))
        rng = random.Random("%d:%s" % (SPOT_SEED, s["id"]))
        groups = {}
        for item in items:
            groups.setdefault(item["row"]["variable"], []).append(item)
        for var in sorted(groups):
            rng.shuffle(groups[var])
        picked = []
        cap = SPOT_PER_VARIABLE
        taken = dict.fromkeys(groups, 0)
        while len(picked) < SPOT_PER_TABLE:
            progress = False
            for var in sorted(groups):
                if len(picked) >= SPOT_PER_TABLE:
                    break
                if taken[var] < min(cap, len(groups[var])):
                    picked.append(groups[var][taken[var]])
                    taken[var] += 1
                    progress = True
            if not progress:
                if all(taken[v] >= len(groups[v]) for v in groups):
                    break
                cap += 1
        doi = ""
        rec_path = os.path.join(CATALOG, s["investigation_id"] + ".json")
        if os.path.exists(rec_path):
            doi = ctx.record(s["investigation_id"]).get("doi") or ""
        for item in picked:
            r = item["row"]
            how = item["cls"] + (" (%s)" % item["note"] if item["note"] else "")
            out.append((order, int(fnum(r["source_row"])), r["source_column"], r["variable"], {
                "table": s["id"], "investigation_id": s["investigation_id"],
                "psi_url": "https://doi.org/" + doi if doi else "",
                "source_file": r["source_file"], "source_row": r["source_row"], "source_column": r["source_column"],
                "raw_cell": item["cell"], "variable": r["variable"], "pipeline_value": r["value"], "unit": r["unit"],
                "how_related": how, "checked_by": "", "same_as_nasa_page": "", "comment": ""}))
    out.sort(key=lambda x: x[:4])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SPOT_COLUMNS, lineterminator="\n")
        w.writeheader()
        for row in out:
            w.writerow(row[4])
    return len(out)


# ----------------------------------------------------------------------------
# K. determinism of inputs
# ----------------------------------------------------------------------------

@check("K1_raw_inputs",
       "Every raw table named in data/psi/manifest.json and in sources.json exists, and its size (and hash, "
       "when the manifest carries one) matches the manifest.")
def check_k1(ctx):
    res = Result()
    manifest = read_json(MANIFEST)
    listed = {}
    for inv in manifest.get("investigations", []):
        for tab in inv.get("experimental_tables", []):
            listed[tab["file"]] = tab
    hashes = 0
    for name, tab in sorted(listed.items()):
        res.checked += 1
        path = os.path.join(RAW, name)
        if not os.path.exists(path):
            res.fail(problem="file missing", file=name)
            continue
        data = read_bytes(path)
        if "bytes" in tab and tab["bytes"] != len(data):
            res.fail(problem="size differs", file=name, manifest=tab["bytes"], on_disk=len(data))
        for algo in ("sha256", "sha1", "md5"):
            if tab.get(algo):
                hashes += 1
                if hashlib.new(algo, data).hexdigest() != tab[algo]:
                    res.fail(problem=algo + " differs", file=name)
    for s in ctx.sources:
        if s["file"] not in listed:
            res.fail(problem="table of sources.json is not in the manifest", file=s["file"])
    on_disk = sorted(f for f in os.listdir(RAW) if f.lower().endswith(".csv"))
    for name in on_disk:
        if name not in listed:
            res.fail(problem="raw file on disk is not in the manifest", file=name)
    res.numbers = {"tables_in_manifest": len(listed), "tables_in_sources_json": len(ctx.sources),
                   "files_on_disk": len(on_disk), "hashes_in_manifest": hashes}
    res.details = {"note": "The manifest carries sizes only; contents are compared by size, not by hash."} if not hashes else {}
    return res


# ----------------------------------------------------------------------------
# L. published findings (README "Published findings"; spec/findings.json _meta)
# ----------------------------------------------------------------------------

FINDING_LISTS = ("at_environment", "about_a_stated_condition_of_the_environment", "general")
PARTIAL_GRAVITY_SCENARIOS = ("lunar", "martian")
_MISSING = object()


def findings_inputs(ctx):
    for name in ("findings.csv", "findings_by_environment.json"):
        if not ctx.has(name):
            raise Skip("data/pipeline/%s does not exist yet" % name)
    return ctx.table("findings.csv"), ctx.json("findings_by_environment.json")


def finding_id_of(entry):
    return entry["item"] + ("#" + str(entry["row"]) if entry.get("row") not in (None, "") else "")


def spec_findings(ctx):
    def load():
        out = {}
        for e in ctx.spec("findings")["findings"]:
            out.setdefault(finding_id_of(e), e)
        return out
    return ctx._get("spec_findings", load)


def range_ends(value):
    """A condition of findings.json as (min, max): a value gives (v, v), a list [min, max] (None = open)."""
    if value is None:
        return None, None
    if isinstance(value, (list, tuple)):
        return (value[0] if len(value) > 0 else None), (value[1] if len(value) > 1 else None)
    return value, value


def same_number_text(cell, value):
    """A CSV cell against a number of the spec (None = empty cell)."""
    if value is None:
        return cell == ""
    return close(fnum(cell), float(value), 1e-12)


@check("L1_findings_entries",
       "Every entry of spec/findings.json points to an item of references.json; findings.csv has one row per "
       "entry, and its text, quote, where, title, version, access, url and reference id are those of the item "
       "and its document, its kind, needs and condition columns those of the entry; the 'findings' of "
       "findings_by_environment.json carry the same text, quote, place and document.")
def check_l1(ctx):
    res = Result()
    rows, fbe = findings_inputs(ctx)
    items = ctx.reference_items
    entries = ctx.spec("findings")["findings"]
    seen = {}
    for e in entries:
        fid = finding_id_of(e)
        if fid in seen:
            res.fail(problem="finding id twice in spec/findings.json", finding_id=fid)
        seen[fid] = e
        if e.get("item") not in items:
            res.fail(problem="item of spec/findings.json not in references.json", finding_id=fid, item=e.get("item"))
    by_csv = {}
    for r in rows:
        if r["finding_id"] in by_csv:
            res.fail(problem="finding id twice in findings.csv", finding_id=r["finding_id"])
        by_csv[r["finding_id"]] = r
    for fid in sorted(set(seen) - set(by_csv)):
        res.fail(problem="entry of spec/findings.json has no row in findings.csv", finding_id=fid)
    for fid in sorted(set(by_csv) - set(seen)):
        res.fail(problem="row of findings.csv is not an entry of spec/findings.json", finding_id=fid)
    compared = 0
    for fid, r in by_csv.items():
        e = seen.get(fid)
        if e is None or e.get("item") not in items:
            continue
        res.checked += 1
        ref, it = items[e["item"]]
        c = e.get("conditions") or {}
        expected = {"item_id": e["item"], "row": "" if e.get("row") is None else str(e["row"]), "kind": e.get("kind"),
                    "needs": ";".join(e.get("needs") or []),
                    "text": it.get("text") or "", "quote": it.get("quote") or "", "where": it.get("where") or "",
                    "reference_id": ref.get("id") or "", "title": ref.get("title") or "",
                    "version": ref.get("version") or "", "access": ref.get("access") or "", "url": ref.get("url") or "",
                    "pressure_as_written": c.get("pressure_as_written") or "", "fuel_phase": c.get("fuel_phase") or "",
                    "gravity_level": ";".join(c.get("gravity_level") or [])}
        for col, want in expected.items():
            compared += 1
            if r.get(col) != want:
                a, b = str(r.get(col)), str(want)
                i = next((j for j, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
                res.fail(finding_id=fid, column=col, first_difference_at=i, csv=a[max(0, i - 30):i + 50],
                         expected=b[max(0, i - 30):i + 50])
        for var in ("o2_pct", "pressure_kpa"):
            lo, hi = range_ends(c.get(var))
            for end, want in (("min", lo), ("max", hi)):
                compared += 1
                if not same_number_text(r.get("%s_%s" % (var, end), ""), want):
                    res.fail(finding_id=fid, column="%s_%s" % (var, end), csv=r.get("%s_%s" % (var, end)), expected=want)
        compared += 1
        if not same_number_text(r.get("flow_cms", ""), c.get("flow_cms")):
            res.fail(finding_id=fid, column="flow_cms", csv=r.get("flow_cms"), expected=c.get("flow_cms"))
        compared += 1
        if [x.strip() for x in split_list(r.get("material", ""))] != [str(m).strip() for m in c.get("material") or []]:
            res.fail(finding_id=fid, column="material", csv=r.get("material", "")[:80], expected=c.get("material"))
    published = fbe.get("findings") or {}
    for fid in sorted(set(seen) - set(published)):
        res.fail(problem="entry missing from findings_by_environment.json 'findings'", finding_id=fid)
    for fid, f in sorted(published.items()):
        e = seen.get(fid)
        if e is None or e.get("item") not in items:
            res.fail(problem="'findings' entry of findings_by_environment.json is not an entry of the spec", finding_id=fid)
            continue
        ref, it = items[e["item"]]
        doc = f.get("reference") or {}
        pairs = [("item_id", f.get("item_id"), e["item"]), ("kind", f.get("kind"), e.get("kind")),
                 ("needs", f.get("needs"), e.get("needs")), ("text", f.get("text") or "", it.get("text") or ""),
                 ("quote", f.get("quote") or "", it.get("quote") or ""), ("where", f.get("where") or "", it.get("where") or ""),
                 ("conditions", f.get("conditions"), e.get("conditions"))]
        pairs += [("reference." + k, doc.get(k), ref.get(k)) for k in ("id", "title", "version", "access", "url")]
        for name, got, want in pairs:
            compared += 1
            if got != want:
                res.fail(problem="findings_by_environment.json 'findings' differs", finding_id=fid, field=name,
                         file=str(got)[:80], expected=str(want)[:80])
    res.numbers = {"spec_entries": len(entries), "items": len({e.get("item") for e in entries}), "csv_rows": len(rows),
                   "json_findings": len(published), "fields_compared": compared}
    return res


def basis_numbers(text):
    """Numbers written in basis words, each with the unit word right after it (kpa, psi, atm or None). In a
    range written 'a to b psia' the first number takes the unit of the second."""
    text = text or ""
    toks = []
    for m in _TEXT_NUMBER.finditer(text):
        unit = re.match(r"\s*(kpa|psi|atm)", text[m.end():], re.I)
        toks.append([float(m.group(0)), unit.group(1).lower() if unit else None, m.start(), m.end()])
    for i in range(len(toks) - 2, -1, -1):
        if toks[i][1] is None and toks[i + 1][1] and \
                re.match(r"^\s*(to|-|\u2013|and|or|,)\s*$", text[toks[i][3]:toks[i + 1][2]], re.I):
            toks[i][1] = toks[i + 1][1]
    return [(n, u) for n, u, _, _ in toks]


def value_at(values, path):
    """A value of an item's 'values' by a path such as 'rows[0].pressure_psia' or 'pressure_kpa[1]'."""
    cur = values
    for part in path.split("."):
        m = re.match(r"^([^\[\]]+)((?:\[\d+\])*)$", part)
        if not m or not isinstance(cur, dict) or m.group(1) not in cur:
            return _MISSING
        cur = cur[m.group(1)]
        for idx in re.findall(r"\[(\d+)\]", m.group(2)):
            if not isinstance(cur, list) or int(idx) >= len(cur):
                return _MISSING
            cur = cur[int(idx)]
    return cur


def plain_numbers(value):
    out = []
    if isinstance(value, bool) or value is None:
        return out
    if isinstance(value, (int, float)):
        out.append(float(value))
    elif isinstance(value, str):
        out += [float(x) for x in _TEXT_NUMBER.findall(value)]
    elif isinstance(value, dict):
        for v in value.values():
            out += plain_numbers(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            out += plain_numbers(v)
    return out


@check("L2_findings_condition_basis",
       "Every normalized number of an entry (oxygen, pressure, flow; each end of a range) follows from its "
       "condition_basis: literally present in the basis words or values, or, for a pressure, a number of the "
       "basis times the factor of its unit (1 psi = 6.894757 kPa, 1 atm = 101.325 kPa), rounded to 3 decimals. "
       "The basis words are in the item's text or quote, a values key exists, and a gravity level or fuel "
       "phase has a word of its vocabulary behind it.")
def check_l2(ctx):
    res = Result()
    spec = ctx.spec("findings")
    meta = spec["_meta"]
    factors = {"kpa": 1.0, "psi": meta["units"]["psi_to_kpa"], "atm": meta["units"]["atm_to_kpa"]}
    decimals = meta["units"].get("kpa_decimals", 3)
    vocab = {"gravity_level": meta.get("gravity_vocabulary") or {}, "fuel_phase": meta.get("fuel_phase_vocabulary") or {}}
    items = ctx.reference_items
    numbers = 0
    converted = 0
    word_start_only = []
    for e in spec["findings"]:
        fid = finding_id_of(e)
        if e.get("item") not in items:
            continue
        _, it = items[e["item"]]
        conds = e.get("conditions") or {}
        bases = e.get("condition_basis") or {}
        for var, blist in bases.items():
            for b in blist if isinstance(blist, list) else [blist]:
                where = b.get("in")
                if where in ("text", "quote"):
                    if (b.get("words") or "") == "" or b["words"] not in (it.get(where) or ""):
                        res.fail(problem="basis words not in the item", finding_id=fid, condition=var, words=b.get("words"), field=where)
                elif where == "values":
                    if value_at(it.get("values") or {}, b.get("key") or "") is _MISSING:
                        res.fail(problem="basis key not in the item's values", finding_id=fid, condition=var, key=b.get("key"))
                else:
                    res.fail(problem="basis without 'in' text, quote or values", finding_id=fid, condition=var)
        for var in ("o2_pct", "pressure_kpa", "flow_cms"):
            if conds.get(var) is None:
                continue
            blist = bases.get(var) or []
            blist = blist if isinstance(blist, list) else [blist]
            if not blist:
                res.fail(problem="normalized condition without a basis", finding_id=fid, condition=var)
                continue
            literal, scaled = set(), set()
            for b in blist:
                if b.get("in") in ("text", "quote"):
                    pairs = basis_numbers(b.get("words") or "")
                elif b.get("in") == "values":
                    v = value_at(it.get("values") or {}, b.get("key") or "")
                    key = (b.get("key") or "").split(".")[-1].lower()
                    unit = "psi" if "psi" in key else "atm" if "atm" in key else None
                    pairs = [] if v is _MISSING else [(n, unit) for n in plain_numbers(v)]
                else:
                    pairs = []
                for n, unit in pairs:
                    if var == "pressure_kpa" and unit in ("psi", "atm"):
                        scaled.add(round(n * factors[unit], decimals))
                    else:
                        literal.add(round(n, 9))
            for end in range_ends(conds[var]):
                if end is None:
                    continue
                numbers += 1
                x = round(float(end), 9)
                if x in literal:
                    continue
                if var == "pressure_kpa" and round(x, decimals) in scaled:
                    converted += 1
                    continue
                res.fail(problem="normalized number not reproducible from its basis", finding_id=fid, condition=var,
                         value=end, literal=sorted(literal)[:8], by_factor=sorted(scaled)[:8])
        for var in ("gravity_level", "fuel_phase"):
            if not conds.get(var):
                continue
            levels = conds[var] if isinstance(conds[var], list) else [conds[var]]
            blist = bases.get(var) or []
            blist = blist if isinstance(blist, list) else [blist]
            for level in levels:
                res.checked += 1
                words = vocab[var].get(level, [])
                ok = whole = False
                for b in blist:
                    if var == "gravity_level" and b.get("level") != level:
                        continue
                    said = b.get("words") if b.get("in") in ("text", "quote") else b.get("key")
                    if any(re.search(r"(?<![A-Za-z0-9])%s" % re.escape(w), said or "", re.I) for w in words):
                        ok = True
                    if any(re.search(r"(?<![A-Za-z0-9])%s(?![A-Za-z])" % re.escape(w), said or "", re.I) for w in words):
                        whole = True
                if ok and not whole:
                    word_start_only.append("%s:%s" % (fid, level))
                if not ok:
                    res.fail(problem="level or phase without a word of the vocabulary in its basis", finding_id=fid,
                             condition=var, level=level)
    res.checked += numbers
    res.numbers = {"normalized_numbers": numbers, "by_unit_factor": converted,
                   "literally_in_basis": numbers - converted - len([f for f in res.failures if "value" in f]),
                   "levels_or_phases_whose_vocabulary_word_starts_a_longer_word": len(word_start_only)}
    if word_start_only:
        res.details = {"note": "A vocabulary word is accepted where it starts a word of the basis ('solid' in 'thick "
                               "solids'); the rule text does not say whole word. Such cases: " + ", ".join(word_start_only)}
    return res


def interval_of(rng):
    """(lo, lo_inclusive, hi, hi_inclusive) of a scenario or bin range; None = open end."""
    return (rng.get("min"), rng.get("min_inclusive", True), rng.get("max"), rng.get("max_inclusive", False))


def intervals_meet(a, b):
    lo_a, lo_ia, hi_a, hi_ia = a
    lo_b, lo_ib, hi_b, hi_ib = b
    if lo_a is None or (lo_b is not None and lo_b > lo_a):
        lo, lo_i = lo_b, lo_ib
    elif lo_b is None or lo_a > lo_b:
        lo, lo_i = lo_a, lo_ia
    else:
        lo, lo_i = lo_a, lo_ia and lo_ib
    if hi_a is None or (hi_b is not None and hi_b < hi_a):
        hi, hi_i = hi_b, hi_ib
    elif hi_b is None or hi_a < hi_b:
        hi, hi_i = hi_a, hi_ia
    else:
        hi, hi_i = hi_a, hi_ia and hi_ib
    if lo is None or hi is None:
        return True
    return lo < hi or (lo == hi and lo_i and hi_i)


def stated_condition(row, var, entry):
    """A condition of a findings.csv row: None (not stated), ('value', v) or ('range', interval)."""
    lo, hi = fnum(row.get(var + "_min", "")), fnum(row.get(var + "_max", ""))
    if lo is None and hi is None:
        return None
    if lo is not None and hi is not None and lo == hi and not isinstance((entry.get("conditions") or {}).get(var), list):
        return ("value", lo)
    excl = (entry.get("conditions") or {}).get(var + "_exclusive") or []
    return ("range", (lo, "min" not in excl, hi, "max" not in excl))


def condition_relation(cond, rng):
    if not rng:
        return "not_set"
    if cond is None:
        return "not_stated"
    if cond[0] == "value":
        return "inside" if in_range(cond[1], rng) else "outside"
    lo, _, hi, _ = cond[1]
    if lo is not None and hi is not None and in_range(lo, rng) and in_range(hi, rng):
        return "inside"
    return "overlaps" if intervals_meet(cond[1], interval_of(rng)) else "outside"


def gravity_relation(levels, scen_level):
    if not scen_level:
        return "not_set"
    if not levels:
        return "not_stated"
    if scen_level in levels:
        return "same"
    if "partial" in levels and scen_level in PARTIAL_GRAVITY_SCENARIOS:
        return "finding_states_partial_gravity"
    return "different"


def place_finding(row, entry, scen):
    """List of one entry for one scenario (findings.json _meta.lists) and the relations it rests on."""
    ranges = scen.get("ranges") or {}
    o2 = stated_condition(row, "o2_pct", entry)
    p = stated_condition(row, "pressure_kpa", entry)
    levels = split_list(row.get("gravity_level", ""))
    rel = {"o2_pct": condition_relation(o2, ranges.get("o2_pct")),
           "pressure_kpa": condition_relation(p, ranges.get("pressure_kpa")),
           "gravity_level": gravity_relation(levels, scen.get("gravity_level"))}
    if o2 is None and p is None and not levels:
        return "general", rel
    if rel["o2_pct"] == "inside" and rel["pressure_kpa"] == "inside":
        return ("moved_for_gravity" if rel["gravity_level"] == "different" else "at_environment"), rel
    good = rel["o2_pct"] in ("inside", "overlaps") or rel["pressure_kpa"] in ("inside", "overlaps") or \
        rel["gravity_level"] in ("same", "finding_states_partial_gravity")
    bad = "outside" in (rel["o2_pct"], rel["pressure_kpa"]) or rel["gravity_level"] == "different"
    if good and not bad:
        return "about_a_stated_condition_of_the_environment", rel
    return "other_conditions", rel


def expected_finding_lists(ctx, scen, key):
    """The three lists, other_conditions and moved_for_gravity of one scenario and one need (or 'general')."""
    rows, _ = findings_inputs(ctx)
    spec = spec_findings(ctx)
    out = {name: [] for name in FINDING_LISTS + ("other_conditions", "moved_for_gravity")}
    rels = {}
    for r in rows:
        if key not in split_list(r.get("needs", "")):
            continue
        entry = spec.get(r["finding_id"]) or {}
        lst, rel = place_finding(r, entry, scen)
        rels[r["finding_id"]] = rel
        if lst == "moved_for_gravity":
            out["moved_for_gravity"].append(r["finding_id"])
            out["other_conditions"].append(r["finding_id"])
        else:
            out[lst].append(r["finding_id"])
    return out, rels


def finding_blocks(ctx):
    """(scenario spec, key, block of findings_by_environment.json) for every scenario and need or 'general'."""
    _, fbe = findings_inputs(ctx)
    envs = {e.get("id"): e for e in fbe.get("environments", [])}
    for scen in ctx.spec("scenarios")["scenarios"]:
        env = envs.get(scen["id"]) or {}
        for key in [n["id"] for n in ctx.needs] + ["general"]:
            yield scen, key, (env.get("needs") or {}).get(key)


@check("L3_findings_lists",
       "For each scenario and each need (and 'general'), the three lists of findings_by_environment.json, the "
       "entries counted under other_conditions and moved_for_gravity, the counts, and for each listed entry "
       "the relations of matched_on, not_stated and flow are recomputed from findings.csv and scenarios.json "
       "by the rule of spec/findings.json _meta.lists.")
def check_l3(ctx):
    res = Result()
    rows, fbe = findings_inputs(ctx)
    spec = spec_findings(ctx)
    by_id = {r["finding_id"]: r for r in rows}
    env_ids = [e.get("id") for e in fbe.get("environments", [])]
    scen_ids = [s["id"] for s in ctx.spec("scenarios")["scenarios"]]
    if env_ids != scen_ids:
        res.fail(problem="environments differ from scenarios.json", file=env_ids, spec=scen_ids)
    listed = {name: 0 for name in FINDING_LISTS}
    other = 0
    for scen, key, block in finding_blocks(ctx):
        k = {"scenario": scen["id"], "need": key}
        if block is None:
            res.fail(problem="block missing", **k)
            continue
        res.checked += 1
        exp, rels = expected_finding_lists(ctx, scen, key)
        for name in FINDING_LISTS:
            got = [x.get("finding_id") for x in block.get(name, [])]
            listed[name] += len(exp[name])
            if len(set(got)) != len(got):
                res.fail(problem="entry listed twice", list=name, **k)
            if set(got) != set(exp[name]):
                res.fail(list=name, missing=sorted(set(exp[name]) - set(got))[:6],
                         not_expected=sorted(set(got) - set(exp[name]))[:6], **k)
        oc = block.get("other_conditions") or {}
        other += len(exp["other_conditions"])
        if oc.get("count") != len(exp["other_conditions"]):
            res.fail(field="other_conditions.count", file=oc.get("count"), recomputed=len(exp["other_conditions"]), **k)
        moved = [m.get("finding_id") if isinstance(m, dict) else m for m in oc.get("moved_for_gravity", [])]
        if sorted(moved) != sorted(exp["moved_for_gravity"]):
            res.fail(field="other_conditions.moved_for_gravity", file=moved, recomputed=exp["moved_for_gravity"], **k)
        n_listed = sum(len(exp[n]) for n in FINDING_LISTS)
        counts = {"n_at": len(exp["at_environment"]), "n_about": len(exp["about_a_stated_condition_of_the_environment"]),
                  "n_general": len(exp["general"]), "n_listed": n_listed,
                  "n_not_full_text": sum(1 for n in FINDING_LISTS for f in exp[n] if by_id[f].get("access") != "full_text_read"),
                  "n_other_conditions": len(exp["other_conditions"])}
        for ck, want in counts.items():
            if (block.get("counts") or {}).get(ck) != want:
                res.fail(field="counts." + ck, file=(block.get("counts") or {}).get(ck), recomputed=want, **k)
        ranges = scen.get("ranges") or {}
        scen_sets = [v for v in ("o2_pct", "pressure_kpa") if ranges.get(v)] + (["gravity_level"] if scen.get("gravity_level") else [])
        for name in FINDING_LISTS:
            for x in block.get(name, []):
                fid = x.get("finding_id")
                if fid not in rels:
                    continue
                rel = rels[fid]
                want_on = {v: r for v, r in rel.items() if r in ("inside", "overlaps", "same", "finding_states_partial_gravity")}
                got_on = {v: (m or {}).get("relation") for v, m in (x.get("matched_on") or {}).items()}
                if got_on != want_on:
                    res.fail(field="matched_on", finding_id=fid, file=got_on, recomputed=want_on, **k)
                want_ns = [v for v in scen_sets if rel[v] == "not_stated"]
                if list(x.get("not_stated") or []) != want_ns:
                    res.fail(field="not_stated", finding_id=fid, file=x.get("not_stated"), recomputed=want_ns, **k)
                if ranges.get("flow_cms"):
                    f = fnum(by_id[fid].get("flow_cms", ""))
                    want_flow = "not_stated" if f is None else ("inside" if in_range(f, ranges["flow_cms"]) else "outside")
                    if x.get("flow") != want_flow:
                        res.fail(field="flow", finding_id=fid, file=x.get("flow"), recomputed=want_flow, **k)
                if x.get("access") != by_id[fid].get("access") or x.get("kind") != by_id[fid].get("kind"):
                    res.fail(field="access or kind", finding_id=fid, **k)
                if name == "general":
                    words = bool((spec.get(fid) or {}).get("condition_words"))
                    if x.get("states_conditions_in_words") is not words:
                        res.fail(field="states_conditions_in_words", finding_id=fid, file=x.get("states_conditions_in_words"),
                                 recomputed=words, **k)
    res.numbers = {"blocks": res.checked, "listed": listed, "other_conditions": other}
    return res


def forbidden_words_in(text, words):
    if not words:
        return []
    return sorted({m.group(0).lower() for m in re.finditer(r"\b(%s)\b" % "|".join(map(re.escape, words)), text or "", re.I)})


@check("L4_findings_sentences",
       "Every number in a fixed sentence of findings_by_environment.json is one of the counts of its block "
       "(n_at, n_about, n_general, n_listed, n_not_full_text), and no sentence or sentence template holds a "
       "word of spec/findings.json forbidden_words.")
def check_l4(ctx):
    res = Result()
    meta = ctx.spec("findings")["_meta"]
    banned = meta.get("forbidden_words") or []
    sentences = 0
    for name, tpl in (meta.get("sentences") or {}).items():
        for t in (tpl.values() if isinstance(tpl, dict) else [tpl]):
            if name != "fields" and forbidden_words_in(t, banned):
                res.fail(problem="forbidden word in a template", template=name, words=forbidden_words_in(t, banned))
    for scen, key, block in finding_blocks(ctx):
        if block is None:
            continue
        counts = block.get("counts") or {}
        pool = {round(float(counts[c]), 9) for c in ("n_at", "n_about", "n_general", "n_listed", "n_not_full_text")
                if isinstance(counts.get(c), (int, float))}
        for s in block.get("statements", []):
            text = s.get("text") if isinstance(s, dict) else s
            sentences += 1
            for n in text_numbers(text):
                res.checked += 1
                if n not in pool:
                    res.fail(problem="number not a count of the lists", scenario=scen["id"], need=key, number=n, text=text[:160])
            words = forbidden_words_in(text, banned)
            if words:
                res.fail(problem="forbidden word", scenario=scen["id"], need=key, words=words, text=text[:160])
    res.numbers = {"sentences": sentences, "numbers_in_sentences": res.checked}
    return res


# ----------------------------------------------------------------------------
# M. answer files (README "Answer files"; spec/answers.json)
# ----------------------------------------------------------------------------

ANSWER_RUNGS = {"frame": "frame", "rung1": "rung1_recorded_at_the_condition", "rung2": "rung2_recorded_near_the_condition",
                "rung3": "rung3_published", "rung4": "rung4_not_known"}
RUNG3_LISTS = {"at_environment": "at_the_environment",
               "about_a_stated_condition_of_the_environment": "about_a_stated_condition",
               "general": "stated_without_these_conditions"}
ENTRY_PLACES = [("frame", "criteria"), ("frame", "nasa_questions"), ("rung3", "at_the_environment"),
                ("rung3", "about_a_stated_condition"), ("rung3", "stated_without_these_conditions"),
                ("rung4", "stated_open_elsewhere")]


def answer_files(ctx):
    """(scenario spec, need spec, file name, content or None) for every scenario x need."""
    if not ctx.has(os.path.join("answers", "index.json")):
        raise Skip("data/pipeline/answers/index.json does not exist yet")
    out = []
    for scen in ctx.spec("scenarios")["scenarios"]:
        for need in ctx.needs:
            name = "%s__%s.json" % (scen["id"], need["id"])
            path = os.path.join("answers", name)
            out.append((scen, need, name, ctx.json(path) if ctx.has(path) else None))
    return out


def package_block(ctx, env_file, need_id):
    path = os.path.join("evidence", env_file)
    if not ctx.has(path):
        return None
    for b in ctx.json(path).get("needs", []):
        if isinstance(b, dict) and b.get("need_id") == need_id:
            return b
    return None


def fill_template(template, fields):
    """{field} and [field|one|many] of spec/answers.json _meta.format."""
    def plural(m):
        return m.group(2) if fields.get(m.group(1)) == 1 else m.group(3)
    text = re.sub(r"\[(\w+)\|([^|\]]*)\|([^\]]*)\]", plural, template)
    return re.sub(r"\{(\w+)\}", lambda m: str(fields.get(m.group(1), "{%s}" % m.group(1))), text)


_OPS = {"==": lambda a, b: a == b, "!=": lambda a, b: a != b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b,
        "<": lambda a, b: a < b, "<=": lambda a, b: a <= b}


def conditions_hold(when, fields):
    return all(_OPS[op](fields.get(f), v) for f, op, v in when)


@check("M1_answers_files_and_index",
       "answers/ holds one file per scenario of scenarios.json and need of needs.json (36) and index.json, and "
       "nothing else; index.json lists them in spec order with the file's top line and the number of entries "
       "of every list it names.")
def check_m1(ctx):
    res = Result()
    files = answer_files(ctx)
    expected = {name for _, _, name, _ in files} | {"index.json"}
    on_disk = set(f for f in os.listdir(ctx.out_path("answers")) if not f.startswith("."))
    for f in sorted(on_disk - expected):
        res.fail(problem="file in answers/ that no scenario x need explains", file=f)
    index = ctx.json(os.path.join("answers", "index.json"))
    rows = index.get("answers", [])
    if [r.get("file") for r in rows] != [name for _, _, name, _ in files]:
        res.fail(problem="index order or files differ from scenarios x needs", index=[r.get("file") for r in rows][:8])
    by_file = {r.get("file"): r for r in rows}
    compared = 0
    for scen, need, name, doc in files:
        k = {"answer_file": name}
        if doc is None:
            res.fail(problem="answer file missing", **k)
            continue
        res.checked += 1
        r = by_file.get(name) or {}
        pairs = [("scenario", r.get("scenario"), scen["id"]), ("need", r.get("need"), need["id"]),
                 ("top_line_id", r.get("top_line_id"), (doc.get("top_line") or {}).get("id")),
                 ("top_line", r.get("top_line"), (doc.get("top_line") or {}).get("text")),
                 ("environment.id", (doc.get("environment") or {}).get("id"), scen["id"]),
                 ("need.need_id", (doc.get("need") or {}).get("need_id"), need["id"])]
        for rung, lists in (r.get("entries") or {}).items():
            block = doc.get(ANSWER_RUNGS.get(rung, rung)) or {}
            for lname, n in lists.items():
                if rung == "rung1" and lname == "matched_tests":
                    got = block.get("matched")
                else:
                    got = len(block.get(lname) or []) if isinstance(block.get(lname), list) else None
                pairs.append(("entries.%s.%s" % (rung, lname), n, got))
        for field, a, b in pairs:
            compared += 1
            if a != b:
                res.fail(field=field, index_or_file=str(a)[:80], expected=str(b)[:80], **k)
    res.numbers = {"answer_files": res.checked, "index_rows": len(rows), "files_on_disk": len(on_disk),
                   "fields_compared": compared}
    return res


@check("M2_answers_rung1",
       "Rung 1 of every answer file: status, counts and the gap codes of rung 4 equal the scenario's row of "
       "scenario_needs.csv; matched is the number of matched tests of the evidence package block; matched "
       "ranges, fuel phases, investigations, documented sentences and indicator values are those of the block; "
       "the copied sentences are the block's statements selected by answers.json rung1.copied_statements, in "
       "order and unchanged, and the gap sentences are the block's gap texts.")
def check_m2(ctx):
    res = Result()
    spec = ctx.spec("answers")
    sel = spec["rung1"]["copied_statements"]
    rows = {(r["scenario_id"], r["need_id"]): r for r in ctx.table("scenario_needs.csv")}
    for scen, need, name, doc in answer_files(ctx):
        if doc is None:
            continue
        res.checked += 1
        k = {"answer_file": name}
        r1 = doc.get("rung1_recorded_at_the_condition") or {}
        row = rows.get((scen["id"], need["id"]))
        if row is None:
            res.fail(problem="no row in scenario_needs.csv", **k)
            continue
        if r1.get("status") != row["status"]:
            res.fail(field="status", file=r1.get("status"), csv=row["status"], **k)
        counts = r1.get("counts") or {}
        for key, col in list(COUNT_KEYS.items()) + list(OPTIONAL_COUNT_KEYS.items()):
            if col in row and counts.get(key) != int(row[col]):
                res.fail(field="counts." + key, file=counts.get(key), csv=row[col], **k)
        codes = [g.get("code") for g in (doc.get("rung4_not_known") or {}).get("gaps", [])]
        if codes != split_list(row.get("gaps", "")):
            res.fail(field="rung4.gaps codes", file=codes, csv=row.get("gaps"), **k)
        block = package_block(ctx, "scenario_%s.json" % scen["id"], need["id"])
        if block is None:
            res.fail(problem="evidence package block missing", **k)
            continue
        if r1.get("matched") != len(block.get("matched_tests", [])):
            res.fail(field="matched", file=r1.get("matched"), package=len(block.get("matched_tests", [])), **k)
        for f in ("matched_ranges", "matched_by_fuel_phase", "investigations", "documented_elsewhere"):
            if r1.get(f) != block.get(f):
                res.fail(field=f, problem="differs from the evidence package block", **k)
        pack_ind = [(i.get("indicator_id"), i.get("group"), i.get("n_tests"), i.get("values")) for i in block.get("indicators", [])]
        file_ind = [(i.get("id"), i.get("group"), i.get("n_tests"), i.get("values")) for i in r1.get("indicators", [])]
        if pack_ind != file_ind:
            res.fail(field="indicators", problem="ids, groups, test counts or values differ from the package", **k)
        want = [s.get("text") for s in block.get("statements", [])
                if s.get("id") in sel["ids"] or any(str(s.get("id", "")).startswith(p) for p in sel["prefixes"])]
        got = [s.get("text") for s in r1.get("sentences", [])]
        if got != want:
            res.fail(field="rung1.sentences", file_n=len(got), package_n=len(want),
                     first_difference=next((g for g, w in zip(got + [None] * 99, want + [None] * 99) if g != w), None), **k)
        want_gaps = [g.get("text") for g in block.get("gaps", [])]
        got_gaps = [g.get("text") for g in (doc.get("rung4_not_known") or {}).get("gaps", [])]
        if got_gaps != want_gaps:
            res.fail(field="rung4.gaps texts", problem="differ from the package gap sentences", **k)
    res.numbers = {"answer_files": res.checked}
    return res


def range_words(spec_words, rng):
    if not rng:
        return None
    lo, hi = rng.get("min"), rng.get("max")
    inc = rng.get("max_inclusive", False)
    if lo is not None and hi is not None:
        t = spec_words["both_max_inclusive" if inc else "both_max_exclusive"]
    elif hi is not None:
        t = spec_words["max_only_inclusive" if inc else "max_only_exclusive"]
    else:
        t = spec_words["min_only"]
    return t.replace("{min}", str(lo)).replace("{max}", str(hi))


@check("M3_answers_rung2_near",
       "Rung 2 of every answer file: the scenario's cells, the candidate cells and the listed cells are "
       "recomputed from coverage.json, scenarios.json and atmosphere_cells.csv by answers.json 'near'; every "
       "listed cell carries the counts and status of its row, matched and also_matched_at_the_condition "
       "recomputed from the evidence packages, the environment's range words, and the counts of the rung.")
def check_m3(ctx):
    res = Result()
    spec = ctx.spec("answers")
    dims = ctx.spec("coverage")["dimensions"]
    obins, pbins = dims["o2_pct"]["bins"], dims["pressure_kpa"]["bins"]
    cells_csv = {(r["scenario_id"], r["need_id"]): r for r in ctx.table("atmosphere_cells.csv")}
    listed_total = 0
    repeating_agree = 0
    for scen, need, name, doc in answer_files(ctx):
        if doc is None:
            continue
        res.checked += 1
        k = {"answer_file": name}
        r2 = doc.get("rung2_recorded_near_the_condition") or {}
        ranges = scen.get("ranges") or {}
        has = bool(ranges.get("o2_pct")) and bool(ranges.get("pressure_kpa"))
        scen_cells, cand = [], []
        if has:
            oi = [i for i, b in enumerate(obins) if intervals_meet(interval_of(b), interval_of(ranges["o2_pct"]))]
            pi = [j for j, b in enumerate(pbins) if intervals_meet(interval_of(b), interval_of(ranges["pressure_kpa"]))]
            sc = {(i, j) for i in oi for j in pi}
            near = set()
            for i, j in sc:
                for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    c = (i + di, j + dj)
                    if 0 <= c[0] < len(obins) and 0 <= c[1] < len(pbins) and c not in sc:
                        near.add(c)
            cid = lambda c: "cell_%s__%s" % (obins[c[0]]["id"], pbins[c[1]]["id"])
            scen_cells = [cid(c) for c in sorted(sc)]
            cand = [cid(c) for c in sorted(near)]
            differs = {cid(c): ("oxygen" if any(c[1] == s[1] and abs(c[0] - s[0]) == 1 for s in sc) else "pressure")
                       for c in near}
        else:
            differs = {}
        listed = []
        for c in cand:
            row = cells_csv.get((c, need["id"]))
            if row and int(row["tests_atmosphere"]) + int(row["tests_oxygen_only"]) + int(row["tests_pressure_only"]) >= 1:
                listed.append(c)
        if r2.get("scenario_cells", []) != scen_cells:
            res.fail(field="scenario_cells", file=r2.get("scenario_cells"), recomputed=scen_cells, **k)
        if r2.get("candidate_cells", []) != cand:
            res.fail(field="candidate_cells", file=r2.get("candidate_cells"), recomputed=cand, **k)
        got_cells = [c.get("cell_id") for c in r2.get("cells", [])]
        if got_cells != listed:
            res.fail(field="cells", file=got_cells, recomputed=listed, **k)
        listed_total += len(listed)
        words = {v: range_words(spec["range_words"][v], ranges.get(v)) for v in ("o2_pct", "pressure_kpa")} if has else {}
        if has and r2.get("environment_words") != words:
            res.fail(field="environment_words", file=r2.get("environment_words"), recomputed=words, **k)
        scen_block = package_block(ctx, "scenario_%s.json" % scen["id"], need["id"]) or {}
        scen_ids = {t.get("test_id") for t in scen_block.get("matched_tests", [])}
        repeating = 0
        for cell in r2.get("cells", []):
            c = cell.get("cell_id")
            row = cells_csv.get((c, need["id"]))
            ck = dict(k, cell=c)
            if row is None:
                continue
            for col, v in (cell.get("counts") or {}).items():
                want = int(row[col]) if col.startswith("tests_") or col == "usable_tests" else row.get(col)
                if v != want:
                    res.fail(field="counts." + col, file=v, csv=row.get(col), **ck)
            if cell.get("status") != row["status"]:
                res.fail(field="status", file=cell.get("status"), csv=row["status"], **ck)
            if cell.get("differs_in") != differs.get(c):
                res.fail(field="differs_in", file=cell.get("differs_in"), recomputed=differs.get(c), **ck)
            cb = package_block(ctx, c + ".json", need["id"])
            if cb is None:
                res.fail(problem="cell package block missing", **ck)
                continue
            ids = {t.get("test_id") for t in cb.get("matched_tests", [])}
            tiers = int(row["tests_atmosphere"]) + int(row["tests_oxygen_only"]) + int(row["tests_pressure_only"])
            if cell.get("matched") != len(ids) or len(ids) != tiers:
                res.fail(field="matched", file=cell.get("matched"), package=len(ids), csv_tiers=tiers, **ck)
            if cell.get("also_matched_at_the_condition") != len(ids & scen_ids):
                res.fail(field="also_matched_at_the_condition", file=cell.get("also_matched_at_the_condition"),
                         recomputed=len(ids & scen_ids), **ck)
            if cell.get("matched_ranges") != cb.get("matched_ranges"):
                res.fail(field="matched_ranges", problem="differs from the cell package", **ck)
            if int(row["tests_oxygen_only"]) + int(row["tests_pressure_only"]) > 0:
                repeating += 1
        counts = r2.get("counts") or {}
        want_counts = {"has_ranges": has, "n_scenario_cells": len(scen_cells), "n_candidates": len(cand), "n_cells": len(listed)}
        for ck, v in want_counts.items():
            if counts.get(ck) != v:
                res.fail(field="counts." + ck, file=counts.get(ck), recomputed=v, **k)
        if counts.get("n_cells_with_repeating_tier") == repeating:
            repeating_agree += 1
    res.numbers = {"answer_files": res.checked, "cells_listed": listed_total,
                   "files_where_n_cells_with_repeating_tier_equals_cells_with_oxygen_only_or_pressure_only": repeating_agree}
    res.details = {"note": "answers.json defines no rule for n_cells_with_repeating_tier; it is compared with the number "
                           "of listed cells whose row has a test of tier oxygen_only or pressure_only and is reported, "
                           "not failed."}
    return res


def nasa_question(ctx, fid):
    rule = ctx.spec("answers")["placement"]["nasa_questions"]
    row = {r["finding_id"]: r for r in findings_inputs(ctx)[0]}.get(fid) or {}
    return row.get("kind") == "gap" and row.get("quote", "") != "" and row.get("reference_id") in rule["reference_ids"]


def file_entries(doc):
    """(rung, list name, entry) of every finding entry of an answer file."""
    for rung, lname in ENTRY_PLACES:
        for e in (doc.get(ANSWER_RUNGS[rung]) or {}).get(lname, []) or []:
            yield rung, lname, e


@check("M4_answers_findings_placement",
       "Every finding that findings_by_environment.json lists for the scenario under the need or under "
       "'general' is in the answer file exactly once, placed by its kind (answers.json placement: criterion -> "
       "frame.criteria; gap -> frame.nasa_questions or rung4.stated_open_elsewhere; result, caveat -> the rung 3 "
       "list of its list), with applies, the name of its list, text and quote equal to references.json, the "
       "place and document of findings.csv, the order of placement.order, and the counts of frame, rung 3 and "
       "rung 4 recomputed from the lists.")
def check_m4(ctx):
    res = Result()
    rows, fbe = findings_inputs(ctx)
    by_id = {r["finding_id"]: r for r in rows}
    items = ctx.reference_items
    envs = {e.get("id"): e for e in fbe.get("environments", [])}
    spec = ctx.spec("answers")
    not_covered = ctx.spec("needs")["_meta"].get("not_covered", [])
    placed = 0
    list_name_differs = 0
    for scen, need, name, doc in answer_files(ctx):
        if doc is None:
            continue
        res.checked += 1
        k = {"answer_file": name}
        blocks = (envs.get(scen["id"]) or {}).get("needs") or {}
        expected = {}
        for key, applies in ((need["id"], "need"), ("general", "general")):
            for lst in FINDING_LISTS:
                for x in (blocks.get(key) or {}).get(lst, []):
                    fid = x.get("finding_id")
                    kind = (by_id.get(fid) or {}).get("kind")
                    if kind == "criterion":
                        place = ("frame", "criteria")
                    elif kind == "gap":
                        place = ("frame", "nasa_questions") if nasa_question(ctx, fid) else ("rung4", "stated_open_elsewhere")
                    else:
                        place = ("rung3", RUNG3_LISTS[lst])
                    expected.setdefault(fid, []).append((place, applies, lst))
        got = {}
        for rung, lname, e in file_entries(doc):
            got.setdefault(e.get("finding_id"), []).append(((rung, lname), e))
        for fid, wants in sorted(expected.items()):
            if len(wants) > 1:
                res.fail(problem="finding listed twice in findings_by_environment.json for this file", finding_id=fid, **k)
            have = got.get(fid, [])
            if len(have) != 1:
                res.fail(problem="finding placed %d times" % len(have), finding_id=fid, **k)
                continue
            (place, e), (want_place, applies, lst) = have[0], wants[0]
            placed += 1
            if place != want_place:
                res.fail(problem="placed in the wrong list", finding_id=fid, file=".".join(place), expected=".".join(want_place), **k)
            if e.get("applies") != applies:
                res.fail(field="applies", finding_id=fid, file=e.get("applies"), expected=applies, **k)
            if e.get("list") != lst:
                list_name_differs += 1
                res.fail(field="list", problem="'list' is not the name of the entry's list in findings_by_environment.json",
                         finding_id=fid, file=e.get("list"), expected=lst, **k)
            r = by_id.get(fid) or {}
            item = items.get(r.get("item_id"))
            if item is None:
                res.fail(problem="item not in references.json", finding_id=fid, **k)
                continue
            ref, it = item
            for f, want in (("text", it.get("text") or ""), ("quote", it.get("quote") or ""), ("where", it.get("where") or ""),
                            ("reference_id", ref.get("id")), ("title", ref.get("title")), ("version", ref.get("version")),
                            ("access", ref.get("access")), ("url", ref.get("url")), ("kind", r.get("kind")),
                            ("item_id", r.get("item_id")), ("row", r.get("row") or None)):
                if (e.get(f) or "") != (want or ""):
                    res.fail(field=f, finding_id=fid, file=str(e.get(f))[:60], expected=str(want)[:60], **k)
        for fid in sorted(set(got) - set(expected)):
            res.fail(problem="entry in the file that findings_by_environment.json does not list here", finding_id=fid, **k)
        for rung, lname in ENTRY_PLACES:
            lst = (doc.get(ANSWER_RUNGS[rung]) or {}).get(lname, []) or []
            keys = [(e.get("reference_id") or "", e.get("item_id") or "", str(e.get("row") or "")) for e in lst]
            if keys != sorted(keys):
                res.fail(problem="entries not in placement.order (reference id, item id, row)", list=rung + "." + lname, **k)
        fr, r3, r4 = (doc.get(ANSWER_RUNGS[x]) or {} for x in ("frame", "rung3", "rung4"))
        crit = fr.get("criteria", [])
        listof = lambda e: (expected.get(e.get("finding_id")) or [(None, None, None)])[0][2]
        r3all = r3.get("at_the_environment", []) + r3.get("about_a_stated_condition", []) + r3.get("stated_without_these_conditions", [])
        want = {("frame", "n_criteria"): len(crit), ("frame", "n_nasa_questions"): len(fr.get("nasa_questions", [])),
                ("frame", "n_criteria_at"): sum(1 for e in crit if listof(e) == "at_environment"),
                ("frame", "n_criteria_about"): sum(1 for e in crit if listof(e) == "about_a_stated_condition_of_the_environment"),
                ("frame", "n_criteria_general"): sum(1 for e in crit if listof(e) == "general"),
                ("rung3", "n_at"): len(r3.get("at_the_environment", [])),
                ("rung3", "n_about"): len(r3.get("about_a_stated_condition", [])),
                ("rung3", "n_general"): len(r3.get("stated_without_these_conditions", [])),
                ("rung3", "n_listed"): len(r3all),
                ("rung3", "n_not_full_text"): sum(1 for e in r3all if e.get("access") != "full_text_read"),
                ("rung4", "n_gaps"): len(r4.get("gaps", [])), ("rung4", "n_stated_open_elsewhere"): len(r4.get("stated_open_elsewhere", [])),
                ("rung4", "n_not_covered"): len(not_covered),
                ("rung4", "n_searches"): sum(1 for s in spec.get("searches", []) if need["id"] in (s.get("needs") or []))}
        for (rung, field), v in want.items():
            got_v = ((doc.get(ANSWER_RUNGS[rung]) or {}).get("counts") or {}).get(field)
            if got_v != v:
                res.fail(field="%s.counts.%s" % (rung, field), file=got_v, recomputed=v, **k)
        if [{x: a.get(x) for x in ("area", "source_item", "why")} for a in r4.get("not_covered", [])] != not_covered or \
                any(a.get("applies") != "general" for a in r4.get("not_covered", [])):
            res.fail(field="rung4.not_covered", problem="not the entries of needs.json _meta.not_covered with applies general", **k)
        want_s = [s for s in spec.get("searches", []) if need["id"] in (s.get("needs") or [])]
        if r4.get("searches", []) != want_s:
            res.fail(field="rung4.searches", problem="not the searches of answers.json for this need", **k)
    res.numbers = {"answer_files": res.checked, "entries_placed": placed,
                   "entries_whose_list_field_is_not_the_list_name": list_name_differs}
    return res


def top_line_fields(doc):
    r1 = doc.get("rung1_recorded_at_the_condition") or {}
    c = r1.get("counts") or {}
    r3 = doc.get("rung3_published") or {}
    n_at, n_about = len(r3.get("at_the_environment", [])), len(r3.get("about_a_stated_condition", []))
    return {"status": r1.get("status"), "usable_tests": c.get("usable_tests"), "atmosphere": c.get("atmosphere"),
            "oxygen_only": c.get("oxygen_only"), "pressure_only": c.get("pressure_only"), "matched": r1.get("matched"),
            "n_near_cells": len((doc.get("rung2_recorded_near_the_condition") or {}).get("cells", [])),
            "n_at": n_at, "n_about": n_about, "n_published_here": n_at + n_about}


@check("M5_answers_top_line",
       "The top line of every answer file starts with the fixed start of answers.json and is the one its rule "
       "selects: the first 'tests' sentence and the first 'published' sentence whose conditions hold for the "
       "fields recomputed from rungs 1 to 3, filled with those fields; id and fields as the rule says.")
def check_m5(ctx):
    res = Result()
    rule = ctx.spec("answers")["top_line"]
    per_id = {}
    for scen, need, name, doc in answer_files(ctx):
        if doc is None:
            continue
        res.checked += 1
        k = {"answer_file": name}
        top = doc.get("top_line") or {}
        fields = top_line_fields(doc)
        t = next((s for s in rule["tests"] if conditions_hold(s["when"], fields)), None)
        p = next((s for s in rule["published"] if conditions_hold(s["when"], fields)), None)
        if t is None or p is None:
            res.fail(problem="no sentence of the rule holds", fields=fields, **k)
            continue
        want_id = t["id"] + "+" + p["id"]
        want_text = " ".join([rule["start"], fill_template(t["text"], fields), fill_template(p["text"], fields)])
        per_id[want_id] = per_id.get(want_id, 0) + 1
        if not str(top.get("text", "")).startswith(rule["start"]):
            res.fail(problem="top line does not start with the fixed start", text=str(top.get("text"))[:80], **k)
        if top.get("id") != want_id:
            res.fail(field="id", file=top.get("id"), expected=want_id, **k)
        if top.get("text") != want_text:
            res.fail(field="text", file=str(top.get("text"))[:200], expected=want_text[:200], **k)
        if top.get("fields") != fields:
            res.fail(field="fields", file=top.get("fields"), recomputed=fields, **k)
        first = (doc.get("sentences") or [{}])[0]
        if first.get("rung") != "top" or first.get("text") != top.get("text"):
            res.fail(problem="the first sentence of the file is not the top line", **k)
    res.numbers = {"answer_files": res.checked, "by_top_line": dict(sorted(per_id.items()))}
    return res


def sentence_pools(doc):
    """For every sentence of the file's 'sentences': the numbers of the block it belongs to."""
    r1 = doc.get("rung1_recorded_at_the_condition") or {}
    r2 = doc.get("rung2_recorded_near_the_condition") or {}
    r4 = doc.get("rung4_not_known") or {}
    rung1 = numbers_of({k: v for k, v in r1.items() if k != "sentences"})
    cells = {}
    for c in r2.get("cells", []):
        pool = numbers_of({k: v for k, v in c.items() if k not in ("differs", "recorded")}) | numbers_of(r2.get("environment_words"))
        cells[c.get("differs")] = pool
        cells[c.get("recorded")] = pool
    gap_texts = {g.get("text") for g in r4.get("gaps", [])}
    for s in doc.get("sentences", []):
        rung, sid, text = str(s.get("rung")), str(s.get("id", "")), s.get("text") or ""
        if rung == "top":
            yield s, numbers_of((doc.get("top_line") or {}).get("fields")), "top_line.fields"
        elif rung == "frame":
            yield s, numbers_of((doc.get("frame") or {}).get("counts")), "frame.counts"
        elif rung == "1":
            yield s, rung1, "rung1 (copied package block)"
        elif rung == "2" and sid.startswith("rung2.cell."):
            yield s, cells.get(text), "rung2 cell"
        elif rung == "2":
            yield s, numbers_of(r2.get("counts")), "rung2.counts"
        elif rung == "3":
            yield s, numbers_of((doc.get("rung3_published") or {}).get("counts")), "rung3.counts"
        elif rung == "4" and sid.startswith("gap."):
            yield s, (rung1 | numbers_of(r4.get("gaps"))) if text in gap_texts else None, "rung4 gap (copied package block)"
        elif rung == "4" and sid == "rung4.search":
            yield s, numbers_of(r4.get("searches")), "rung4.searches"
        elif rung == "4":
            yield s, numbers_of(r4.get("counts")), "rung4.counts"
        else:
            yield s, None, "unknown rung"


@check("M6_answers_sentence_numbers",
       "Every number in every sentence of an answer file is found in the block the sentence belongs to (top "
       "line: its fields; frame, rung 2, 3 and 4 sentences: the counts of the rung; a cell sentence: its cell; "
       "a copied package sentence: the copied package block of rung 1; a search sentence: the search entry), "
       "and the file's 'sentences' are exactly the sentences of its blocks.")
def check_m6(ctx):
    res = Result()
    sentences = 0
    for scen, need, name, doc in answer_files(ctx):
        if doc is None:
            continue
        k = {"answer_file": name}
        blocks = [(doc.get("top_line") or {}).get("text")]
        for key in ("frame", "rung1_recorded_at_the_condition", "rung2_recorded_near_the_condition", "rung3_published",
                    "rung4_not_known"):
            blocks += [s.get("text") for s in (doc.get(key) or {}).get("sentences", [])]
        for c in (doc.get("rung2_recorded_near_the_condition") or {}).get("cells", []):
            blocks += [c.get("differs"), c.get("recorded")]
        listed = [s.get("text") for s in doc.get("sentences", [])]
        if sorted(map(str, listed)) != sorted(map(str, blocks)):
            res.fail(problem="'sentences' differ from the sentences of the blocks", only_in_list=sorted(set(listed) - set(blocks))[:2],
                     only_in_blocks=sorted(set(map(str, blocks)) - set(map(str, listed)))[:2], **k)
        for s, pool, where in sentence_pools(doc):
            sentences += 1
            if pool is None:
                res.fail(problem="sentence without a block", rung=s.get("rung"), id=s.get("id"), text=(s.get("text") or "")[:120], **k)
                continue
            for n in text_numbers(s.get("text")):
                res.checked += 1
                if n not in pool:
                    res.fail(number=n, block=where, id=s.get("id"), text=(s.get("text") or "")[:200], **k)
    res.numbers = {"sentences": sentences, "numbers_in_sentences": res.checked}
    return res


def answer_templates(spec):
    """Every template text of spec/answers.json (top line, sentences, cell, search, range words)."""
    out = [("top_line.start", spec["top_line"]["start"])]
    out += [("top_line." + s["id"], s["text"]) for part in ("tests", "published") for s in spec["top_line"][part]]
    for part, v in spec["sentences"].items():
        if isinstance(v, list):
            out += [(s["id"], s["text"]) for s in v]
        elif isinstance(v, dict):
            out += [("sentences.%s.%s" % (part, kk), t) for kk, t in v.items()]
        else:
            out.append(("sentences." + part, v))
    for var, d in spec.get("range_words", {}).items():
        out += [("range_words.%s.%s" % (var, kk), t) for kk, t in d.items()]
    return out


@check("M7_answers_words",
       "No template of spec/answers.json holds a digit or a word of its forbidden_words, and no sentence of an "
       "answer file holds such a word (whole words; outside the need name, a reading copied from the spec and a "
       "sentence quoted word for word from a NASA record or a publication, which are counted apart).")
def check_m7(ctx):
    res = Result()
    spec = ctx.spec("answers")
    banned = spec.get("forbidden_words") or []
    for tid, text in answer_templates(spec):
        res.checked += 1
        if re.search(r"\d", re.sub(r"\{\w+\}|\[\w+\|", " ", text)):
            res.fail(problem="digit in a template", template=tid, text=text[:120])
        if forbidden_words_in(text, banned):
            res.fail(problem="forbidden word in a template", template=tid, words=forbidden_words_in(text, banned))
    copied = copied_spec_texts(ctx) + [n.get("reading", "") for n in ctx.needs]
    quotes = verbatim_quotes(ctx)
    exempt = 0
    sentences = 0
    for scen, need, name, doc in answer_files(ctx):
        if doc is None:
            continue
        for s in doc.get("sentences", []):
            sentences += 1
            text = s.get("text") or ""
            if not forbidden_words_in(text, banned):
                continue
            stripped = text
            for piece in sorted([p for p in copied + quotes if p], key=len, reverse=True):
                stripped = stripped.replace(piece, " ")
            words = forbidden_words_in(stripped, banned)
            if words:
                res.fail(file=name, id=s.get("id"), words=words, text=text[:200])
            else:
                exempt += 1
    res.numbers = {"templates": res.checked, "sentences": sentences,
                   "sentences_with_such_a_word_only_inside_a_quote_or_copied_reading": exempt}
    res.checked += sentences
    return res


# ----------------------------------------------------------------------------
# N. raw inventory (README raw-data paragraph; spec/raw_kinds.json)
# ----------------------------------------------------------------------------

LISTINGS = os.path.join(ROOT, "data", "psi", "file_listings")


def listing_records(listing):
    """Every file record of a saved PSI listing (directories walked), in listing order."""
    out = []

    def walk(node):
        for f in node.get("files", []) or []:
            if f.get("directory") or ("bytes_size" not in f and f.get("files")):
                walk(f)
            else:
                out.append(f)
    walk(listing)
    return out


def raw_kind(spec, category, name):
    """(kind, rule id, extension, name without prefix and extension) by the ordered rules of raw_kinds.json."""
    ext = name.rsplit(".", 1)[1].strip().lower() if "." in name else "(none)"
    core = name
    for pat in spec["strip_prefix"]:
        core = re.sub(pat.replace("{category}", re.escape(category)), "", core, count=1)
    if "." in core:
        core = core.rsplit(".", 1)[0]
    for rule in spec["rules"]:
        if "categories" in rule and category not in rule["categories"]:
            continue
        if "extensions" in rule and ext not in rule["extensions"]:
            continue
        if "name_pattern" in rule and not re.search(rule["name_pattern"], core):
            continue
        return rule["kind"], rule["id"], ext, core
    return spec["default_kind"], "(no rule: default)", ext, core


def archive_content(spec, category, core):
    for rule in spec["archive_content"]["rules"]:
        if "categories" in rule and category not in rule["categories"]:
            continue
        if "name_pattern" in rule and not re.search(rule["name_pattern"], core):
            continue
        return rule["content"]
    return spec["archive_content"]["default"]


def raw_inventory(ctx):
    if not os.path.isdir(LISTINGS):
        raise Skip("data/psi/file_listings/ is absent (git-ignored; fetched by pipeline/raw_inventory.py --refresh), "
                   "so raw_inventory.json cannot be recounted")
    if not ctx.has("raw_inventory.json"):
        raise Skip("data/pipeline/raw_inventory.json does not exist yet")
    return ctx.json("raw_inventory.json")


def add_fb(d, key, size):
    e = d.setdefault(key, {"files": 0, "bytes": 0})
    e["files"] += 1
    e["bytes"] += size
    return e


def recount_listing(spec, listing):
    recs = listing_records(listing)
    seen = set()
    files = []
    for f in recs:
        fid = f.get("id") or f.get("key")
        if fid in seen:
            continue
        seen.add(fid)
        files.append(f)
    out = {"files": len(files), "bytes": sum(int(f.get("bytes_size") or 0) for f in files),
           "listing_rows": len(recs), "repeated_rows": len(recs) - len(files),
           "listing_rows_bytes": sum(int(f.get("bytes_size") or 0) for f in recs),
           "files_without_size": sum(1 for f in files if f.get("bytes_size") is None),
           "by_category": {}, "by_kind": {}, "by_rule": {}, "largest": {}, "names": []}
    for f in files:
        category = f.get("sortingCategory") or ""
        name = (f.get("key") or "").rsplit("/", 1)[-1]
        size = int(f.get("bytes_size") or 0)
        kind, rule, ext, core = raw_kind(spec, category, name)
        cat = add_fb(out["by_category"], category, size)
        add_fb(cat.setdefault("by_kind", {}), kind, size)
        k = add_fb(out["by_kind"], kind, size)
        add_fb(k.setdefault("extensions", {}), ext, size)
        if kind == "archive":
            add_fb(k.setdefault("archive_content", {}), archive_content(spec, category, core), size)
        add_fb(out["by_rule"], rule, size)
        out["largest"].setdefault(kind, []).append((size, name))
        out["names"].append((category, name))
    return out


def fb_view(d):
    """{key: {files, bytes, [nested ...]}} without other fields, for comparison."""
    out = {}
    for k, v in (d or {}).items():
        e = {"files": v.get("files"), "bytes": v.get("bytes")}
        for sub in ("by_kind", "extensions", "archive_content"):
            if sub in v:
                e[sub] = fb_view(v[sub])
        out[k] = e
    return out


@check("N1_raw_inventory_counts",
       "raw_inventory.json has one entry per PSI record (numeric order); files and bytes per investigation, per "
       "PSI category and per kind (with extensions and archive content), the listing rows and repeats, the "
       "largest file of each kind, the totals, and the id patterns of the file names are recounted from the "
       "saved listings by the rules of raw_kinds.json, each file id counted once.")
def check_n1(ctx):
    res = Result()
    inv = raw_inventory(ctx)
    spec = ctx.spec("raw_kinds")
    entries = inv.get("investigations", [])
    ids = [e.get("investigation_id") for e in entries]
    if ids != catalog_ids():
        res.fail(problem="investigations differ from the PSI records", file=ids[:6], catalog=catalog_ids()[:6])
    totals = {"files": 0, "bytes": 0, "listing_rows": 0, "repeated_rows": 0, "listing_rows_bytes": 0,
              "files_without_size": 0, "by_kind": {}, "by_rule": {}}
    tid = spec["test_id_patterns"]
    distinct_agree = 0
    patterns_found = 0
    for e in entries:
        inv_id = e.get("investigation_id")
        k = {"investigation_id": inv_id}
        path = os.path.join(LISTINGS, "%s.json" % inv_id)
        if not os.path.exists(path):
            res.fail(problem="no saved listing", **k)
            continue
        res.checked += 1
        got = recount_listing(spec, read_json(path))
        for f in ("files", "bytes", "listing_rows", "repeated_rows", "listing_rows_bytes", "files_without_size"):
            totals[f] += got[f]
            if e.get(f) != got[f]:
                res.fail(field=f, file=e.get(f), recounted=got[f], **k)
        for kind, v in got["by_kind"].items():
            add = totals["by_kind"].setdefault(kind, {"files": 0, "bytes": 0})
            add["files"] += v["files"]
            add["bytes"] += v["bytes"]
        for rule, v in got["by_rule"].items():
            add = totals["by_rule"].setdefault(rule, {"files": 0, "bytes": 0})
            add["files"] += v["files"]
            add["bytes"] += v["bytes"]
        if fb_view(e.get("by_category")) != fb_view(got["by_category"]):
            diff = sorted(c for c in set(got["by_category"]) | set(e.get("by_category") or {})
                          if fb_view({c: (e.get("by_category") or {}).get(c, {})}) != fb_view({c: got["by_category"].get(c, {})}))
            res.fail(field="by_category", categories=diff[:5], **k)
        if fb_view(e.get("by_kind")) != fb_view(got["by_kind"]):
            diff = sorted(c for c in set(got["by_kind"]) | set(e.get("by_kind") or {})
                          if fb_view({c: (e.get("by_kind") or {}).get(c, {})}) != fb_view({c: got["by_kind"].get(c, {})}))
            res.fail(field="by_kind", kinds=diff[:5],
                     file={c: (e.get("by_kind") or {}).get(c, {}).get("files") for c in diff[:3]},
                     recounted={c: got["by_kind"].get(c, {}).get("files") for c in diff[:3]}, **k)
        for kind, sizes in got["largest"].items():
            top = max(s for s, _ in sizes)
            ke = (e.get("by_kind") or {}).get(kind) or {}
            if ke.get("example_bytes") != top or (top, ke.get("example")) not in sizes:
                res.fail(field="by_kind.%s.example" % kind, file=[ke.get("example"), ke.get("example_bytes")], largest_bytes=top, **k)
        searched = [n for c, n in got["names"] if c in tid["categories"]]
        want = []
        for p in tid["patterns"]:
            hits = [n for n in searched if re.search(p["regex"], n)]
            if len(hits) >= tid["min_files"] and searched and len(hits) >= tid["min_share"] * len(searched):
                want.append((p["id"], len(searched), len(hits), {m for n in hits for m in re.findall(p["regex"], n)}, set(hits)))
        have = e.get("test_id_in_file_names") or []
        if [(h.get("pattern_id"), h.get("files_searched"), h.get("files_matching")) for h in have] != [w[:3] for w in want]:
            res.fail(field="test_id_in_file_names", file=[(h.get("pattern_id"), h.get("files_searched"), h.get("files_matching")) for h in have],
                     recounted=[w[:3] for w in want], **k)
        for h, w in zip(have, want):
            patterns_found += 1
            if h.get("distinct_ids") == len(w[3]):
                distinct_agree += 1
            if any(x not in w[4] for x in h.get("examples") or []):
                res.fail(field="test_id_in_file_names.examples", pattern=h.get("pattern_id"), problem="example does not carry the pattern", **k)
    t = inv.get("_meta", {}).get("totals") or {}
    for f in ("files", "bytes", "listing_rows", "repeated_rows", "listing_rows_bytes", "files_without_size"):
        if t.get(f) != totals[f]:
            res.fail(field="_meta.totals." + f, file=t.get(f), recounted=totals[f])
    if t.get("investigations") != len(entries):
        res.fail(field="_meta.totals.investigations", file=t.get("investigations"), recounted=len(entries))
    for part in ("by_kind", "by_rule"):
        if fb_view(t.get(part)) != fb_view(totals[part]):
            res.fail(field="_meta.totals." + part, problem="differs from the recount")
    res.numbers = {"investigations": res.checked, "files": totals["files"], "listing_rows": totals["listing_rows"],
                   "repeated_rows": totals["repeated_rows"], "files_by_kind": {k: v["files"] for k, v in totals["by_kind"].items()},
                   "id_patterns_reported": patterns_found,
                   "distinct_ids_equal_to_distinct_matched_strings": distinct_agree}
    res.details = {"note": "raw_kinds.json does not define 'distinct_ids'; it is compared with the number of distinct "
                           "strings the pattern matches in the searched names and reported, not failed. Kinds are read "
                           "from the name without prefix and extension (name_rule); id patterns from the whole name."}
    return res


_SIZE = re.compile(r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?) (GB|MB)\b")
_GROUPED_NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def grouped_numbers(text):
    """Numbers of a sentence that writes thousands with commas ('3,807')."""
    return [round(float(m.replace(",", "")), 9) for m in _GROUPED_NUMBER.findall(text or "")]


@check("N2_raw_inventory_sentences",
       "Every number in the sentence of a raw_inventory.json entry is a field of the same entry, and every size "
       "written in it (GB from 10^9 bytes, MB below, one decimal) is a byte count of the entry in that unit.")
def check_n2(ctx):
    res = Result()
    inv = raw_inventory(ctx)
    tiny = ctx.spec("raw_kinds")["sentence"].get("size_tiny", "")
    sizes = 0
    for e in inv.get("investigations", []):
        text = e.get("sentence") or ""
        k = {"investigation_id": e.get("investigation_id")}
        pool = numbers_of({kk: v for kk, v in e.items() if kk != "sentence"})
        byte_counts = [v for v in plain_byte_counts(e)]
        rest = text.replace(tiny, " ") if tiny else text
        for m in _SIZE.finditer(rest):
            sizes += 1
            res.checked += 1
            unit = m.group(2)
            ok = any((b >= 10 ** 9 if unit == "GB" else b < 10 ** 9) and
                     ("%.1f" % (b / (1e9 if unit == "GB" else 1e6))) == m.group(1).replace(",", "") for b in byte_counts)
            if not ok:
                res.fail(problem="size not a byte count of the entry", size=m.group(0), text=text[:160], **k)
        rest = _SIZE.sub(" ", rest)
        for n in grouped_numbers(rest):
            res.checked += 1
            if n not in pool:
                res.fail(number=n, text=text[:200], **k)
    res.numbers = {"sentences": len(inv.get("investigations", [])), "numbers_in_sentences": res.checked, "sizes": sizes}
    return res


def plain_byte_counts(obj):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, int) and not isinstance(v, bool) and "bytes" in k:
                out.append(v)
            else:
                out += plain_byte_counts(v)
    elif isinstance(obj, list):
        for v in obj:
            out += plain_byte_counts(v)
    return out


# ----------------------------------------------------------------------------
# O. raw-file states (raw_gaps.py outputs), raw values and their effect
#    own code path: nothing of raw_gaps.py is imported
# ----------------------------------------------------------------------------

# sha256 of the four files whose bytes the raw-file layer must not change: a
# snapshot of 2026-11-14 17:30 KST (the files were last changed in commit
# a5a9e87, 14:41 KST); see pipeline/README.md, "What is in the raw files".
FROZEN_SHA256 = {
    "tests.csv": "b8acc1073fbc33a37563eb7f7cd12811e602fb7363ee69982d97860f05522211",
    "need_tests.csv": "8f2cf847728016c6669a95931c89d06286ce7030214cece1d65d66a93d119a77",
    "scenario_needs.csv": "ad7fcfeba56661d448b8c8bef9fb66667e749d58a2e5d84a450988725e535796",
    "scenario_tests.csv": "6581e840553a2d4197d90ecc2ad94b5b307747112f81b4d418a2e357ae45eaab",
}
FROZEN_COUNTED = {"P1": 133, "P2": 0, "P3": 2, "S1": 298, "D1": 122, "D2": 0}
O_STATES = ("in_table", "column_in_sampled_raw_file", "documented_only", "not_in_sampled_files", "no_test_table")
O_ONE_FILE = "one file of the group was opened"
O_READABLE = ("sensor_reading_series", "value_per_test_in_a_results_file")


def o_blank(v):
    return v is None or str(v).strip() == ""


def o_vars(ctx):
    out = []
    for n in ctx.needs:
        for k in ("conditions_required", "conditions_useful", "outcomes_any"):
            for v in n[k]:
                if v not in out:
                    out.append(v)
    return out


def o_listing(inv):
    """{file id: (name, bytes)} of the saved PSI listing of an investigation."""
    path = os.path.join(LISTINGS, "%s.json" % inv)
    if not os.path.exists(path):
        raise Skip("data/psi/file_listings/%s.json is absent (git-ignored)" % inv)
    out = {}
    for f in listing_records(read_json(path)):
        if f.get("id") and f.get("key") and f.get("bytes_size") is not None:
            out.setdefault(f["id"], (f["key"].rsplit("/", 1)[-1], int(f["bytes_size"])))
    return out


def o_spec(ctx):
    return ctx._get("o_spec", lambda: {i["investigation_id"]: i for i in ctx.spec("raw_columns")["investigations"]})


def o_cells(ctx):
    """(investigation, variable) -> the rows of gap_states.csv as this check
    derives them from tests.csv, raw_columns.json, sources.json and the raw
    inventory, by the rule of the README (no_test_table; then n tests
    in_table; the other N-n tests in the first of column, documented, not
    in sampled files)."""
    def load():
        spec = o_spec(ctx)
        by_inv = {}
        for t in ctx.tests:
            by_inv.setdefault(t["investigation_id"], []).append(t)
        docs = {}
        for s in ctx.sources:
            for d in s.get("documented_elsewhere", []) or []:
                docs.setdefault((s["investigation_id"], d["variable"]), []).append(
                    d.get("reference_item") or ("record field " + d.get("record_field", "")))
        invs = sorted({x["investigation_id"] for x in ctx.json("raw_inventory.json")["investigations"]}, key=psi_key)
        out = {}
        for inv in invs:
            sp = spec.get(inv, {"entries": [], "unopened_groups": []})
            rows = by_inv.get(inv, [])
            for var in o_vars(ctx):
                key = (inv, var)
                if not rows:
                    out[key] = [{"state": "no_test_table", "tests_in_state": 0, "n": 0, "N": 0}]
                    continue
                n = sum(1 for t in rows if not o_blank(t.get(var)))
                cell = []
                if n:
                    cell.append({"state": "in_table", "tests_in_state": n, "n": n, "N": len(rows)})
                if n < len(rows):
                    es = [e for e in sp["entries"] if e["standard_variable"] == var]
                    r = {"tests_in_state": len(rows) - n, "n": n, "N": len(rows)}
                    if es:
                        gs = list(dict.fromkeys(e["group"] for e in es))
                        byg = {e["group"]: e for e in es}
                        r.update(state="column_in_sampled_raw_file",
                                 column_is="+".join(dict.fromkeys(e["column_is"] for e in es)),
                                 link_kind=" | ".join(dict.fromkeys(e["link_kind"] for e in es)),
                                 differs=o_codes(ctx, es),
                                 groups=gs, files=sum(byg[g]["files_in_listing"] for g in gs),
                                 bytes=sum(byg[g]["bytes_in_listing"] or 0 for g in gs), entries=len(es),
                                 all_files=all(e["sampling"] != O_ONE_FILE for e in es))
                    elif key in docs:
                        r.update(state="documented_only", groups=[], documented_by=docs[key])
                    else:
                        us = sp.get("unopened_groups", [])
                        r.update(state="not_in_sampled_files", groups=[u["group"] for u in us],
                                 files=sum(u["files_in_listing"] for u in us), bytes=sum(u["bytes_in_listing"] for u in us))
                    cell.append(r)
                out[key] = cell
        return out
    return ctx._get("o_cells", load)


def o_codes(ctx, entries):
    """differs_from_definition of a set of entries as the CSV files write it: the codes in the order of
    _meta.differs_from_definition joined by ';', or 'none'."""
    order = list(ctx.spec("raw_columns")["_meta"]["differs_from_definition"])
    have = {c for e in entries for c in e["differs_from_definition"]}
    return ";".join(c for c in order if c in have) or "none"


def o_qualifies(e):
    return (e["column_is"] in O_READABLE and not e["differs_from_definition"]
            and e["link_kind"] == "literal_key_or_label")


def o_test_state(ctx, test, var):
    if not o_blank(test.get(var)):
        return "in_table", ""
    rem = o_cells(ctx)[(test["investigation_id"], var)][-1]
    return rem["state"], rem.get("column_is", "")


@check("O1_gap_states",
       "gap_states.csv recounted from tests.csv: one row per investigation x need variable and state; n of N and the "
       "split of a mixed row as the README states it; the state of the other tests follows the fixed order (entry in "
       "raw_columns.json, then documented_elsewhere of sources.json, then not_in_sampled_files); file groups, files and "
       "bytes are those of the spec.")
def check_o1(ctx):
    res = Result()
    if not ctx.has("gap_states.csv"):
        raise Skip("gap_states.csv not written (python3 pipeline/raw_gaps.py)")
    rows = ctx.table("gap_states.csv")
    got = {}
    for r in rows:
        got.setdefault((r["investigation_id"], r["variable"]), []).append(r)
    cells = o_cells(ctx)
    if set(got) != set(cells):
        res.fail(problem="investigation x variable pairs differ", missing=sorted(set(cells) - set(got))[:5],
                 extra=sorted(set(got) - set(cells))[:5])
    states = {}
    for key, want in cells.items():
        have = got.get(key, [])
        res.checked += 1
        if [h["state"] for h in have] != [w["state"] for w in want]:
            res.fail(problem="states differ", pair=key, file=[h["state"] for h in have], expected=[w["state"] for w in want])
            continue
        for h, w in zip(have, want):
            states[w["state"]] = states.get(w["state"], 0) + 1
            for col, val in (("tests_in_state", w["tests_in_state"]), ("tests_in_table", w["n"]), ("tests_mapped", w["N"])):
                if int(h[col]) != val:
                    res.fail(problem="%s differs" % col, pair=key, state=w["state"], file=h[col], expected=val)
            if w["state"] in ("column_in_sampled_raw_file", "not_in_sampled_files"):
                if h["file_groups"] != " | ".join(w["groups"]) or (w["groups"] and (int(h["files"]) != w["files"] or int(h["bytes"]) != w["bytes"])):
                    res.fail(problem="file groups, files or bytes differ", pair=key, state=w["state"])
            if w["state"] == "column_in_sampled_raw_file" and (h["column_is"] != w["column_is"] or int(h["entries"]) != w["entries"]
                                                               or h["link_kind"] != w["link_kind"] or h["differs_from_definition"] != w["differs"]):
                res.fail(problem="column_is, entries, link_kind or differs_from_definition differ", pair=key,
                         file=(h["column_is"], h["link_kind"], h["differs_from_definition"]),
                         expected=(w["column_is"], w["link_kind"], w["differs"]))
            if w["state"] == "documented_only" and h["documented_by"] != " | ".join(w["documented_by"]):
                res.fail(problem="documented_by differs", pair=key)
        if sum(int(h["tests_in_state"]) for h in have) != (want[0]["N"]):
            res.fail(problem="tests of the rows do not add up to N", pair=key)
    res.numbers = {"pairs": res.checked, "rows": len(rows), "rows_by_state": {s: states.get(s, 0) for s in O_STATES}}
    return res


@check("O2_need_gap_states",
       "need_gap_states.csv: for every scenario, need and required or outcome variable, the in-scope and counted tests "
       "equal capability_matrix.csv (tests, and usable_tests of the stated rows) and need_tests.csv; the states of the "
       "tests and the counted tests left unmatched because the variable is empty are recounted from tests.csv and "
       "scenario_tests.csv; the counted tests per need are the frozen numbers.")
def check_o2(ctx):
    res = Result()
    if not ctx.has("need_gap_states.csv"):
        raise Skip("need_gap_states.csv not written")
    rows = ctx.table("need_gap_states.csv")
    cap = ctx.table("capability_matrix.csv")
    counted = {}
    for r in ctx.table("need_tests.csv"):
        if r["objective_link"] == "stated":
            counted.setdefault(r["need_id"], set()).add(r["test_id"])
    for nid, n in FROZEN_COUNTED.items():
        if len(counted.get(nid, ())) != n:
            res.fail(problem="counted tests of a need changed", need_id=nid, now=len(counted.get(nid, ())), frozen=n)
    marks = {(r["scenario_id"], r["test_id"]): r for r in ctx.table("scenario_tests.csv")}
    want = []
    for sc in ctx.spec("scenarios")["scenarios"]:
        for nd in ctx.needs:
            phases = (nd.get("scope") or {}).get("fuel_phase")
            scope = [t for t in ctx.tests if not phases or t["fuel_phase"] in phases]
            in_scope_cap = sum(int(r["tests"]) for r in cap if r["need_id"] == nd["id"])
            counted_cap = sum(int(r["usable_tests"]) for r in cap if r["need_id"] == nd["id"] and r["objective_link"] == "stated")
            if (len(scope), len(counted.get(nd["id"], ()))) != (in_scope_cap, counted_cap):
                res.fail(problem="in-scope or counted tests differ from capability_matrix.csv", need_id=nd["id"],
                         recount=(len(scope), len(counted.get(nd["id"], ()))), capability_matrix=(in_scope_cap, counted_cap))
            ids = counted.get(nd["id"], set())
            for role, var in [("required", v) for v in nd["conditions_required"]] + [("outcome", v) for v in nd["outcomes_any"]]:
                g = {}
                for t in scope:
                    k = o_test_state(ctx, t, var)
                    x = g.setdefault(k, [0, 0, 0])
                    x[0] += 1
                    if t["test_id"] in ids:
                        x[1] += 1
                        m = marks[(sc["id"], t["test_id"])]
                        o, p = m["o2_match"], m["pressure_match"]
                        if var in ("o2_pct", "pressure_kpa") and m["tier"] == "other" and o == "not_recorded" and p == "not_recorded":
                            x[2] += 1
                for (st, kind) in sorted(g, key=lambda k: (O_STATES.index(k[0]), k[1])):
                    a, b, u = g[(st, kind)]
                    want.append({"scenario_id": sc["id"], "need_id": nd["id"], "role": role, "variable": var, "state": st,
                                 "column_is": kind, "in_scope_tests": str(in_scope_cap), "counted_tests": str(counted_cap),
                                 "in_scope_tests_in_state": str(a), "counted_tests_in_state": str(b),
                                 "counted_unmatched_for_lack_of_this_variable": str(u)})
    res.checked = len(want)
    if len(rows) != len(want):
        res.fail(problem="row count differs", file=len(rows), expected=len(want))
    for h, w in zip(rows, want):
        if {k: h.get(k) for k in w} != w:
            res.fail(problem="row differs", file={k: h.get(k) for k in w}, expected=w)
    res.numbers = {"rows": len(rows), "unmatched_for_lack": sum(int(r["counted_unmatched_for_lack_of_this_variable"]) for r in rows),
                   "counted_per_need": {k: len(v) for k, v in sorted(counted.items())}}
    return res


@check("O3_retrieval_queue",
       "retrieval_queue.csv: one row per investigation, variable and file group for the variables in state column (one "
       "row per group with an entry) or not_in_sampled_files (one row per unopened group of the spec), only where a test "
       "of an investigation linked as supported to a need that uses the variable lacks the value; the numbers are "
       "recounted; retrievable_by_reading is yes only where an entry of the group is a sensor series or a value per test "
       "in a results file, carries no code of differs_from_definition and has link_kind literal_key_or_label; the "
       "rows are sorted by the stated rule and ranked 1..n.")
def check_o3(ctx):
    res = Result()
    if not ctx.has("retrieval_queue.csv"):
        raise Skip("retrieval_queue.csv not written")
    rows = ctx.table("retrieval_queue.csv")
    spec = o_spec(ctx)
    counted = {}
    for r in ctx.table("need_tests.csv"):
        if r["objective_link"] == "stated":
            counted.setdefault(r["test_id"], set()).add(r["need_id"])
    supported = {n["id"]: {l["investigation_id"] for l in n.get("stated_by", []) if l["verdict"] == "supported"} for n in ctx.needs}
    uses = {v: [n for n in ctx.needs if v in n["conditions_required"] + n["conditions_useful"] + n["outcomes_any"]] for v in o_vars(ctx)}
    by_inv = {}
    for t in ctx.tests:
        by_inv.setdefault(t["investigation_id"], []).append(t)
    want = {}
    for (inv, var), cell in o_cells(ctx).items():
        rem = cell[-1]
        if rem["state"] not in ("column_in_sampled_raw_file", "not_in_sampled_files") or not rem["groups"]:
            continue
        empty = [t for t in by_inv.get(inv, []) if o_blank(t.get(var))]
        lack = [t for t in empty if any((not (n.get("scope") or {}).get("fuel_phase") or t["fuel_phase"] in n["scope"]["fuel_phase"])
                                        and inv in supported[n["id"]] for n in uses[var])]
        if not lack:
            continue
        ids_uses = {n["id"] for n in uses[var]}
        cnt = [t for t in lack if counted.get(t["test_id"], set()) & ids_uses]
        for gid in rem["groups"]:
            if rem["state"] == "column_in_sampled_raw_file":
                es = [e for e in spec[inv]["entries"] if e["standard_variable"] == var and e["group"] == gid]
                kinds = list(dict.fromkeys(e["column_is"] for e in es))
                kind, files, byts = "+".join(kinds), es[0]["files_in_listing"], es[0]["bytes_in_listing"]
                yes = "yes" if any(o_qualifies(e) for e in es) else "no"
                differs, lk = o_codes(ctx, es), " | ".join(dict.fromkeys(e["link_kind"] for e in es))
            else:
                u = next(u for u in spec[inv]["unopened_groups"] if u["group"] == gid)
                kind, files, byts, yes = u["kind"], u["files_in_listing"], u["bytes_in_listing"], "no"
                differs, lk = "", ""
            want[(inv, var, gid)] = {"state": rem["state"], "kind": kind, "retrievable_by_reading": yes,
                                     "differs_from_definition": differs, "link_kind": lk,
                                     "tests_without_value": str(len(empty)), "tests_lacking_value": str(len(lack)),
                                     "counted_tests_lacking_value": str(len(cnt)), "files": str(files),
                                     "bytes": "" if byts is None else str(byts)}
    got = {(r["investigation_id"], r["variable"], r["file_group"]): r for r in rows}
    if set(got) != set(want):
        res.fail(problem="rows differ", missing=sorted(set(want) - set(got))[:5], extra=sorted(set(got) - set(want))[:5])
    for k, w in want.items():
        res.checked += 1
        h = got.get(k)
        if h and {c: h[c] for c in w} != w:
            res.fail(problem="row values differ", row=k, file={c: h[c] for c in w}, expected=w)
    key = lambda r: (-int(r["tests_lacking_value"]), (1, 0) if r["bytes"] == "" else (0, int(r["bytes"])),
                     psi_key(r["investigation_id"]), r["variable"], r["file_group"])
    if rows != sorted(rows, key=key):
        res.fail(problem="rows are not in the order of the stated rule")
    if [r["rank"] for r in rows] != [str(i) for i in range(1, len(rows) + 1)]:
        res.fail(problem="rank is not 1..n")
    res.numbers = {"rows": len(rows), "retrievable_by_reading": sum(r["retrievable_by_reading"] == "yes" for r in rows)}
    return res


@check("O4_raw_values",
       "raw_values.csv: every row names a PSI file id of the listing of its investigation with the listed name and "
       "bytes; a test_id is given only with literal link evidence and exists in tests.csv for the same investigation; "
       "a series row has n_readings >= 1, min <= first, last <= max as stored numbers, and the rows of the lowest and "
       "the highest reading inside its first and last row.")
def check_o4(ctx):
    res = Result()
    if not ctx.has("raw_values.csv"):
        raise Skip("raw_values.csv absent")
    rows = ctx.table("raw_values.csv")
    listings, tests = {}, ctx.tests_by_id
    by = {}
    for r in rows:
        res.checked += 1
        inv = r["investigation_id"]
        if inv not in listings:
            listings[inv] = o_listing(inv)
        rec = listings[inv].get(r["psi_file_id"])
        if rec is None or rec[0] != r["psi_file_name"] or rec[1] != int(r["bytes"]):
            res.fail(problem="file id, name or bytes not as in the listing", file_id=r["psi_file_id"], name=r["psi_file_name"])
        if r["test_id"]:
            t = tests.get(r["test_id"])
            if t is None or t["investigation_id"] != inv:
                res.fail(problem="test_id not in tests.csv for this investigation", test_id=r["test_id"])
            if "tests.csv" not in r["link_evidence"]:
                res.fail(problem="test_id without literal link evidence", test_id=r["test_id"])
        if r["extraction"] == "saffire_ambient_pressure":
            lo, hi = float(r["min"]), float(r["max"])
            if int(r["n_readings"]) < 1 or not (lo <= float(r["first_value"]) <= hi and lo <= float(r["last_value"]) <= hi):
                res.fail(problem="series numbers inconsistent", test_id=r["test_id"])
            first, last = int(r["first_row"]), int(r["last_row"])
            if not (first <= int(r["min_row"]) <= last and first <= int(r["max_row"]) <= last):
                res.fail(problem="row of the lowest or highest reading outside the series", test_id=r["test_id"])
        elif r["min_row"] or r["max_row"]:
            res.fail(problem="min_row or max_row on a row that is not a series", cell=r["cell_or_range"])
        by[r["extraction"]] = by.get(r["extraction"], 0) + 1
    res.numbers = {"rows": len(rows), "by_extraction": by, "files": len({r["psi_file_id"] for r in rows}),
                   "rows_with_test_id": sum(1 for r in rows if r["test_id"]),
                   "tests_named": len({r["test_id"] for r in rows if r["test_id"]})}
    return res


@check("O5_raw_columns_spec",
       "spec/raw_columns.json: every group with a name_regex has the files and bytes that the regex gives on the saved "
       "listing (less exclude_ids); every sample and entry file id is in the listing with the listed name and bytes; "
       "every entry carries the name pattern, files and bytes of its group, a standard variable of a need, a column_is "
       "and header_kind of _meta, has_values true, a link_to_table_row, a link_kind of _meta and a list of codes of "
       "_meta.differs_from_definition.")
def check_o5(ctx):
    res = Result()
    raw = ctx.spec("raw_columns")
    meta, need_vars = raw["_meta"], set(o_vars(ctx))
    groups_n = entries_n = 0
    for inv in raw["investigations"]:
        iid = inv["investigation_id"]
        if not (inv["groups"] or inv.get("unopened_groups")):
            continue
        L = o_listing(iid)
        for u in inv.get("unopened_groups", []):
            if u["kind"] not in meta["unread_kinds"]:
                res.fail(problem="unopened group kind not in _meta.unread_kinds", investigation_id=iid, group=u["group"])
        for g in inv["groups"] + inv.get("unopened_groups", []):
            if not g.get("name_regex"):
                continue
            groups_n += 1
            c = re.compile(g["name_regex"])
            hit = [(k, v) for k, v in L.items() if c.search(v[0]) and k not in set(g.get("exclude_ids", []))]
            if (len(hit), sum(v[1] for k, v in hit)) != (g["files_in_listing"], g["bytes_in_listing"]):
                res.fail(problem="files or bytes differ from the listing recount", investigation_id=iid, group=g["group"],
                         spec=(g["files_in_listing"], g["bytes_in_listing"]), recount=(len(hit), sum(v[1] for k, v in hit)))
            for s in g.get("samples", []):
                rec = L.get(s["psi_file_id"])
                if rec is None or rec[1] != int(s["bytes_listing"]) or (g.get("round") == 2 and rec[0] != s["psi_name"]):
                    res.fail(problem="sample not in the listing", investigation_id=iid, group=g["group"], file_id=s["psi_file_id"])
        gby = {g["group"]: g for g in inv["groups"]}
        for e in inv["entries"]:
            entries_n += 1
            g = gby.get(e["group"])
            k = {"investigation_id": iid, "group": e["group"], "header": e["header_as_written"]}
            if g is None:
                res.fail(problem="entry of an unknown group", **k)
                continue
            if any(e[x] != g[x] for x in ("name_pattern", "files_in_listing", "bytes_in_listing")):
                res.fail(problem="entry and group differ", **k)
            rec = L.get(e["sample_file_id"])
            if rec is None or rec[0] != e["sample_file"] or rec[1] != int(e["sample_bytes"]):
                res.fail(problem="entry sample not as in the listing", **k)
            if e["standard_variable"] not in need_vars or e["column_is"] not in meta["column_is"] \
                    or e["header_kind"] not in meta["header_kinds"] or e["has_values"] is not True \
                    or not e.get("link_to_table_row") or e.get("mapping_by") != meta["mapping_by"] \
                    or e.get("link_kind") not in meta["link_kind"] or not isinstance(e.get("differs_from_definition"), list) \
                    or any(c not in meta["differs_from_definition"] for c in e["differs_from_definition"]):
                res.fail(problem="entry field outside the vocabulary or missing", **k)
    res.checked = groups_n + entries_n
    res.numbers = {"groups_recounted": groups_n, "entries": entries_n,
                   "entries_round_2": sum(1 for i in raw["investigations"] for e in i["entries"] if e["round"] == 2)}
    return res


@check("O6_frozen_files",
       "tests.csv, need_tests.csv, scenario_needs.csv and scenario_tests.csv have the sha256 of the snapshot of "
       "2026-11-14 17:30 KST that the README names.")
def check_o6(ctx):
    res = Result()
    for name, want in FROZEN_SHA256.items():
        res.checked += 1
        with open(ctx.out_path(name), "rb") as f:
            got = hashlib.sha256(f.read()).hexdigest()
        if got != want:
            res.fail(problem="file changed", file=name, sha256=got, snapshot=want)
    res.numbers = {"files": res.checked}
    return res


@check("O7_raw_values_effect",
       "raw_values_effect.json: the Saffire lowest and highest readings times the psi factor of spec/findings.json, "
       "their pressure bins and scenario ranges, and the SAME-R counts per size statistic are recounted from "
       "raw_values.csv, tests.csv and the specs; the file states that nothing is adopted.")
def check_o7(ctx):
    res = Result()
    if not ctx.has("raw_values_effect.json"):
        raise Skip("raw_values_effect.json not written")
    eff = ctx.json("raw_values_effect.json")
    E = ctx.spec("raw_columns")["_meta"]["effect"]
    factor = ctx.spec("findings")["_meta"]["units"]["psi_to_kpa"]
    bins = ctx.spec("coverage")["dimensions"]["pressure_kpa"]["bins"]
    rows = ctx.table("raw_values.csv")
    if eff.get("not_adopted") != E["not_adopted"] or eff["saffire_pressure"]["factor_kpa_per_psi"] != factor:
        res.fail(problem="not_adopted sentence or factor differs")
    sa = {t["test_id"]: t for t in eff["saffire_pressure"]["tests"]}
    for r in rows:
        if r["extraction"] != "saffire_ambient_pressure" or not r["test_id"]:
            continue
        res.checked += 1
        t = sa.get(r["test_id"])
        lo, hi = round(float(r["min"]) * factor, 4), round(float(r["max"]) * factor, 4)
        bl = next((b["id"] for b in bins if in_range(lo, b)), None)
        bh = next((b["id"] for b in bins if in_range(hi, b)), None)
        if t is None or (t["min_kpa"], t["max_kpa"], t["bin_of_min"], t["bin_of_max"], t["same_bin"], t["min_row"], t["max_row"]) \
                != (lo, hi, bl, bh, bl == bh, int(r["min_row"]), int(r["max_row"])):
            res.fail(problem="Saffire conversion or bin differs", test_id=r["test_id"])
            continue
        for sc in ctx.spec("scenarios")["scenarios"]:
            rng = sc["ranges"].get("pressure_kpa")
            if rng is not None and t["scenario_pressure_ranges"].get(sc["id"]) != {"min_in_range": in_range(lo, rng), "max_in_range": in_range(hi, rng)}:
                res.fail(problem="scenario range mark differs", test_id=r["test_id"], scenario=sc["id"])
    d2 = next(n for n in ctx.needs if n["id"] == "D2")
    sup = {l["investigation_id"] for l in d2["stated_by"] if l["verdict"] == "supported"}
    scope = {t["test_id"]: t for t in ctx.tests if t["fuel_phase"] in d2["scope"]["fuel_phase"] and t["investigation_id"] in sup}
    req = {i for i, t in scope.items() if all(not o_blank(t.get(v)) for v in d2["conditions_required"])}
    stats = {s["statistic"]: s for s in eff["same_r_particle_size"]["statistics"]}
    same = [r for r in rows if r["extraction"] == "same_particle_size_statistics"]
    every = {h for hs in E["same_statistic_classes"].values() for h in hs}
    tied = {r["test_id"] for r in same if r["test_id"]}
    pos = set()
    for r in same:
        if r["test_id"] and r["header_as_written"] in every:
            try:
                if float(r["value"]) > 0:
                    pos.add(r["test_id"])
            except ValueError:
                pass
    sr = eff["same_r_particle_size"]
    if (sr.get("tied_tests"), sr.get("tied_tests_without_a_positive_value")) != (len(tied), sorted(tied - pos)):
        res.fail(problem="tied tests or tied tests without a positive value differ")
    for name, headers in E["same_statistic_classes"].items():
        res.checked += 1
        vals = {}
        for r in same:
            if r["test_id"] in scope and r["header_as_written"] in headers:
                try:
                    if float(r["value"]) != 0:
                        vals.setdefault(r["test_id"], {}).setdefault(r["psi_file_id"], set()).add(r["value"])
                except ValueError:
                    pass
        tid = set(vals)
        differ = sorted(t for t, pf in vals.items() if len(pf) > 1 and len({frozenset(v) for v in pf.values()}) > 1)
        within = sum(1 for pf in vals.values() if any(len(v) > 1 for v in pf.values()))
        s = stats.get(name, {})
        got = (s.get("tests_with_a_stored_nonzero_value"), s.get("of_which_meet_every_required_condition"),
               s.get("tests_whose_files_hold_different_values_ids"), s.get("tests_with_more_than_one_value_in_one_file"))
        if got != (len(tid), len(tid & req), differ, within):
            res.fail(problem="SAME-R count differs", statistic=name, file=got, recount=(len(tid), len(tid & req), differ, within))
    counted_d2 = sum(1 for r in ctx.table("need_tests.csv") if r["need_id"] == "D2" and r["objective_link"] == "stated")
    if eff["same_r_particle_size"]["d2_counted_tests_now"] != counted_d2:
        res.fail(problem="D2 counted tests differ")
    res.numbers = {"saffire_tests": len(sa), "same_bin": sum(1 for t in sa.values() if t["same_bin"]),
                   "same_r": {k: v["tests_with_a_stored_nonzero_value"] for k, v in stats.items()}, "d2_counted": counted_d2}
    return res


@check("O8_evidence_raw_state",
       "Every need block of every evidence package has raw_state for each required variable: the counted and in-scope "
       "test numbers equal need_tests.csv and the need's scope, and the tests per state (summed over investigations) "
       "equal this check's recount; every gap entry has raw_state for its variable.")
def check_o8(ctx):
    res = Result()
    counted = {}
    for r in ctx.table("need_tests.csv"):
        if r["objective_link"] == "stated":
            counted.setdefault(r["need_id"], []).append(r["test_id"])
    need = {n["id"]: n for n in ctx.needs}
    cache = {}

    def want(nid, var, pop):
        if (nid, var, pop) not in cache:
            nd = need[nid]
            phases = (nd.get("scope") or {}).get("fuel_phase")
            ts = ([ctx.tests_by_id[i] for i in counted.get(nid, [])] if pop == "counted"
                  else [t for t in ctx.tests if not phases or t["fuel_phase"] in phases])
            c = {}
            for t in ts:
                st = o_test_state(ctx, t, var)[0]
                c[st] = c.get(st, 0) + 1
            cache[(nid, var, pop)] = (len(ts), c)
        return cache[(nid, var, pop)]
    gaps_n = 0
    for env, pack in packages(ctx):
        for b in (pack or {}).get("needs", []):
            res.checked += 1
            rs = b.get("raw_state")
            if not isinstance(rs, dict) or list(rs) != need[b["need_id"]]["conditions_required"]:
                res.fail(problem="raw_state missing or not the required variables", package=env["id"], need_id=b["need_id"])
                continue
            for var, v in rs.items():
                for pop in ("counted", "in_scope"):
                    c = {}
                    for item in v[pop]["states"]:
                        c[item["state"]] = c.get(item["state"], 0) + item["tests"]
                    if (v[pop]["tests"], c) != want(b["need_id"], var, pop):
                        res.fail(problem="raw_state numbers differ", package=env["id"], need_id=b["need_id"], variable=var, population=pop)
            for g in b["gaps"]:
                gaps_n += 1
                if not g.get("raw_state"):
                    res.fail(problem="gap without raw_state", package=env["id"], need_id=b["need_id"], code=g["code"])
                for x in g.get("raw_state", []):
                    c = {}
                    for item in x["states"]:
                        c[item["state"]] = c.get(item["state"], 0) + item["tests"]
                    if (x["tests"], c) != want(b["need_id"], x["variable"], x["population"]):
                        res.fail(problem="gap raw_state numbers differ", package=env["id"], code=g["code"])
    res.numbers = {"need_blocks": res.checked, "gaps": gaps_n}
    return res


# ----------------------------------------------------------------------------
# P. names of the raw files (raw_names.py outputs) and their join into the
#    raw-file layer; own code path: nothing of raw_names.py or raw_gaps.py is
#    imported, the name rules of spec/raw_names.json are applied again here
# ----------------------------------------------------------------------------

P_LEVELS = ("test", "day_or_session", "none")
P_MON = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9,
         "oct": 10, "nov": 11, "dec": 12, "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
         "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}
P_ABBR = ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")


def p_day(y, m, d):
    import datetime as _dt
    try:
        return _dt.date(y, m, d)
    except (ValueError, TypeError):
        return None


def p_cell_date(c):
    """A table cell as a date, by the formats the spec names."""
    c = c.strip()
    for rx, f in ((r"(\d{1,2})/(\d{1,2})/(\d{4})$", lambda g: (int(g[2]), int(g[0]), int(g[1]))),
                  (r"(\d{1,2})-([A-Za-z]{3})-(\d{2})$", lambda g: (2000 + int(g[2]), P_MON.get(g[1].lower()), int(g[0]))),
                  (r"(\d{4})-([A-Za-z]{3})-(\d{2})\b", lambda g: (int(g[0]), P_MON.get(g[1].lower()), int(g[2]))),
                  (r"(\d{4})-(\d{2})-(\d{2})$", lambda g: (int(g[0]), int(g[1]), int(g[2])))):
        m = re.match(rx, c)
        if m:
            return p_day(*f(m.groups()))
    return None


def p_key(tr, s):
    import datetime as _dt
    s = s.strip()
    digits = re.sub(r"\D", "", s)
    if tr in ("text",):
        return s
    if tr == "upper":
        return s.upper()
    if tr == "nospace_upper":
        return "".join(s.split()).upper()
    if tr == "int":
        return str(int(s)) if s.isdigit() else None
    if tr == "cir":
        return s.upper() if s.upper()[:1] == "F" else "F" + s.upper()
    if tr == "upper_prefix6":
        return "".join(ch for ch in s if ch.isalpha()).upper()[:6] or None
    if tr == "yyddd_date":
        if len(s) != 5 or not s.isdigit():
            return None
        y = 2000 + int(s[:2])
        d = _dt.date(y, 1, 1) + _dt.timedelta(days=int(s[2:]) - 1)
        return d.isoformat() if 1 <= int(s[2:]) and d.year == y else None
    if tr in ("ymd_date", "ymd_yyddd", "ymd_dmon"):
        d = p_day(int(digits[:4]), int(digits[4:6]), int(digits[6:])) if len(digits) == 8 else None
        if d is None:
            return None
        if tr == "ymd_date":
            return d.isoformat()
        if tr == "ymd_yyddd":
            return "%02d%03d" % (d.year % 100, d.timetuple().tm_yday)
        return "%d-%s" % (d.day, P_ABBR[d.month - 1])
    if tr == "dmony_date":
        m = re.match(r"(\d{1,2})([A-Za-z]{3})(\d{4})$", s)
        d = p_day(int(m.group(3)), P_MON.get(m.group(2).lower()), int(m.group(1))) if m else None
        return d.isoformat() if d else None
    raise ValueError("unknown key transform " + tr)


def p_cells(tr, cells, pairs=None):
    c = cells[0].strip()
    if tr == "lookup_date":
        d = p_cell_date(c) if c else None
        return set(pairs.get(d.isoformat(), [])) if d else set()
    if tr == "ymd_cols":
        y, mo, d = [x.strip() for x in cells]
        mo = mo.rstrip(".").lower()
        mon = int(mo) if mo.isdigit() else P_MON.get(mo)
        day = p_day(int(y), mon, int(d)) if y.isdigit() and d.isdigit() and mon else None
        return {day.isoformat()} if day else set()
    if tr == "each_upper":
        return {x.strip().upper() for x in cells if x.strip()}
    if c == "":
        return set()
    one = {"text": lambda: c, "upper": lambda: c.upper(), "nospace_upper": lambda: "".join(c.split()).upper(),
           "first5": lambda: "".join(c.split())[:5],
           "int": lambda: str(int(c)) if c.isdigit() else None,
           "digits_prefix": lambda: (str(int(re.match(r"\d+", c).group())) if re.match(r"\d+", c) else None),
           "cir": lambda: c.upper() if c.upper()[:1] == "F" else "F" + c.upper(),
           "date": lambda: (p_cell_date(c).isoformat() if p_cell_date(c) else None),
           "doy": lambda: (str(p_cell_date(c).timetuple().tm_yday) if p_cell_date(c) else None),
           "dmon": lambda: ("%d-%s" % (int(c.split("-")[0]), c.split("-")[1].lower())
                            if re.match(r"\d{1,2}-[A-Za-z]{3}$", c) else None),
           "gmt_int": lambda: (str(int(re.match(r"GMT\s*(\d+)", c).group(1))) if re.match(r"GMT\s*(\d+)", c) else None),
           "after_hyphen": lambda: c.split("-", 1)[1].strip() if "-" in c else None,
           "upper_prefix6": lambda: "".join(ch for ch in c if ch.isalpha()).upper()[:6] or None}
    if tr == "slash_parts_upper":
        return {p.strip().upper() for p in c.split("/") if p.strip()}
    v = one[tr]()
    return {v} if v else set()


def p_listing_files(ctx, inv):
    """(name without the PSI prefix, category, folder, bytes, kind, file id) of every file once."""
    path = os.path.join(LISTINGS, inv + ".json")
    if not os.path.exists(path):
        raise Skip("data/psi/file_listings/%s.json is absent (git-ignored; python3 pipeline/raw_inventory.py --refresh "
                   "fetches the listings); the name ties cannot be recounted" % inv)
    kinds = ctx.spec("raw_kinds")
    out, seen = [], set()
    for f in listing_records(read_json(path)):
        fid = f.get("id") or f.get("key")
        if fid in seen:
            continue
        seen.add(fid)
        cat = f.get("sortingCategory") or ""
        name = (f.get("key") or "").rsplit("/", 1)[-1]
        base = name
        for pat in kinds["strip_prefix"]:
            new = re.sub(pat.replace("{category}", re.escape(cat)), "", base, count=1)
            if new != base:
                base = new
                break
        out.append({"base": base, "category": cat, "folder": f.get("subcategory") or "",
                    "bytes": int(f.get("bytes_size") or 0), "kind": raw_kind(kinds, cat, name)[0], "id": f.get("id") or ""})
    return out


def p_rows(spec_inv):
    rows = []
    for t in spec_inv["tables"]:
        table = read_raw_table(t)
        header = table[0]
        for i, cells in enumerate(table[1:], start=2):
            if any(cells):
                rows.append((t, i, dict(zip(header, cells + [""] * (len(header) - len(cells))))))
    return rows


def p_pattern(base):
    """name_pattern as _meta.name_pattern of raw_names.json defines it."""
    m = re.search(r"\.[A-Za-z0-9]{1,5}$", base)
    stem, ext = (base[:m.start()], m.group()) if m else (base, "")
    parts = re.split(r"([\s_\-.()\[\],])", stem)
    return "".join("<ID>" if any(ch.isdigit() for ch in x) and not re.fullmatch(r"[\s_\-.()\[\],]", x) else x
                   for x in parts) + ext


def p_nested(a, b):
    a, b = set(a), set(b)
    return a <= b or b <= a


def p_ties(ctx):
    """{investigation: [(file, level, [row keys], [test ids], suffix code, rule id, [other ties])]} by the rules of
    raw_names.json; other ties: (rule id, level, [row keys]) of later matches whose rows are not nested with the
    deciding rows."""
    def load():
        spec = ctx.spec("raw_names")
        test_of = {(t["source_file"], int(t["source_row"])): t["test_id"] for t in ctx.tests}
        out = {}
        for inv, si in sorted(spec["investigations"].items(), key=lambda kv: psi_key(kv[0])):
            files = p_listing_files(ctx, inv)
            rows = p_rows(si)
            res = []
            for f in files:
                found = None
                every = []
                for r in si["rules"]:
                    fl = re.I if r.get("ignore_case") else 0
                    if (r.get("categories") and f["category"] not in r["categories"]) or f["kind"] in r.get("exclude_kinds", []):
                        continue
                    if r.get("name_must_match") and not re.search(r["name_must_match"], f["base"], fl):
                        continue
                    for m in re.finditer(r["pattern"], f["folder"] if r["where"] == "folder" else f["base"], fl):
                        keys = {g: p_key(fd["key"], m.group(g)) for g, fd in r["fields"].items() if m.group(g) is not None}
                        if not keys or None in keys.values():
                            continue
                        cand = [(t, n, c) for t, n, c in rows if (not r.get("tables") or t in r["tables"])
                                and all(re.search(x["regex"], c[x["column"]]) for x in r.get("row_filter", []))]
                        hit = {g: [(t, n) for t, n, c in cand
                                   if keys[g] in p_cells(r["fields"][g]["cell"], [c[k] for k in r["fields"][g]["columns"]],
                                                         si.get("lookups", {}).get(r["fields"][g].get("lookup"), {}).get("pairs"))]
                               for g in keys}
                        if r.get("mode") == "each_field_ties_union":
                            got = sorted({x for v in hit.values() for x in v}, key=[(t, n) for t, n, _ in rows].index) \
                                if all(hit.values()) else []
                        else:
                            got = [x for x in next(iter(hit.values())) if all(x in v for v in hit.values())]
                        if got:
                            lv = r.get("level_if_several_rows") if len(got) > 1 and r.get("level_if_several_rows") else r["level"]
                            every.append((r["id"], lv, got))
                found = every[0] if every else None
                rule, level, got = found or ("", "none", [])
                others = []
                for o in every[1:]:
                    if not p_nested(o[2], got) and o not in others:
                        others.append(o)
                suf = next((s["code"] for s in si["suffix_codes"]
                            if re.search(s["pattern"], f["base"], re.I if s.get("ignore_case") else 0)), "(no suffix code)")
                res.append((f, level, ["%s#row%d" % x for x in got], sorted({test_of[x] for x in got if x in test_of}), suf,
                            rule, [(o[0], o[1], ["%s#row%d" % x for x in o[2]]) for o in others]))
            out[inv] = res
        return out
    return ctx._get("p_ties", load)


@check("P1_raw_file_groups_totals",
       "raw_file_groups.csv: the files and bytes of the groups add up, per investigation and kind, to the files and "
       "bytes of raw_inventory.json; in every group the files and bytes by link level add up to the group.")
def check_p1(ctx):
    res = Result()
    if not ctx.has("raw_file_groups.csv"):
        raise Skip("raw_file_groups.csv not written (python3 pipeline/raw_names.py)")
    got = {}
    for r in ctx.table("raw_file_groups.csv"):
        res.checked += 1
        a = got.setdefault((r["investigation_id"], r["kind"]), [0, 0])
        a[0] += int(r["files"])
        a[1] += int(r["bytes"])
        parts = [(int(r["files_tied_to_a_test"]), int(r["bytes_tied_to_a_test"])),
                 (int(r["files_tied_to_a_day_or_session"]), int(r["bytes_tied_to_a_day_or_session"])),
                 (int(r["files_not_tied"]), int(r["bytes_not_tied"]))]
        if (sum(p[0] for p in parts), sum(p[1] for p in parts)) != (int(r["files"]), int(r["bytes"])):
            res.fail(problem="levels do not add up to the group", group=(r["investigation_id"], r["name_pattern"]))
    want = {}
    for inv in ctx.json("raw_inventory.json")["investigations"]:
        for k, v in inv["by_kind"].items():
            want[(inv["investigation_id"], k)] = [v["files"], v["bytes"]]
    for k in sorted(set(got) | set(want)):
        if got.get(k) != want.get(k):
            res.fail(problem="files or bytes differ from raw_inventory.json", investigation_kind=k,
                     groups=got.get(k), inventory=want.get(k))
    res.numbers = {"groups": res.checked, "investigation_kind_pairs": len(want),
                   "files": sum(v[0] for v in got.values()), "bytes": sum(v[1] for v in got.values())}
    return res


@check("P2_test_files_ids",
       "test_files.csv: every test_id is a test of tests.csv of the same investigation and is the test of its table "
       "row (source_file, source_row); every table_row_key names a row of an experimental table of the investigation; "
       "levels are test or day_or_session.")
def check_p2(ctx):
    res = Result()
    if not ctx.has("test_files.csv"):
        raise Skip("test_files.csv not written (python3 pipeline/raw_names.py)")
    by_row = {"%s#row%s" % (t["source_file"], t["source_row"]): t for t in ctx.tests}
    tables = {t["file"]: m["accession"] for m in read_json(MANIFEST)["investigations"]
              for t in (m.get("experimental_tables") or [])}
    n_rows = {}
    for r in ctx.table("test_files.csv"):
        res.checked += 1
        t, _, n = r["table_row_key"].rpartition("#row")
        if tables.get(t) != r["investigation_id"]:
            res.fail(problem="table of another investigation or unknown", row=r["table_row_key"])
            continue
        if t not in n_rows:
            n_rows[t] = len(read_raw_table(t))
        if not n.isdigit() or not 2 <= int(n) <= n_rows[t]:
            res.fail(problem="row number outside the table", row=r["table_row_key"])
        if r["link_level"] not in ("test", "day_or_session"):
            res.fail(problem="link level", row=r["table_row_key"], level=r["link_level"])
        if r["test_id"]:
            tt = ctx.tests_by_id.get(r["test_id"])
            if tt is None or tt["investigation_id"] != r["investigation_id"]:
                res.fail(problem="test_id not a test of tests.csv of this investigation", test_id=r["test_id"])
            elif by_row.get(r["table_row_key"], {}).get("test_id") != r["test_id"]:
                res.fail(problem="test_id is not the test of its table row", test_id=r["test_id"], row=r["table_row_key"])
        elif r["table_row_key"] in by_row:
            res.fail(problem="table row is a test but test_id is empty", row=r["table_row_key"])
    res.numbers = {"rows": res.checked, "with_test_id": sum(1 for r in ctx.table("test_files.csv") if r["test_id"])}
    return res


@check("P3_name_ties_recount",
       "Every listed file is tied again by the ordered rules of spec/raw_names.json with this check's own code; the "
       "files and bytes by link level per investigation, per group of raw_file_groups.csv and per row of test_files.csv "
       "equal the outputs; the suffix codes too. SKIP without the git-ignored listings.")
def check_p3(ctx):
    res = Result()
    for name in ("raw_file_groups.csv", "test_files.csv", "raw_layers_summary.json"):
        if not ctx.has(name):
            raise Skip("%s not written (python3 pipeline/raw_names.py)" % name)
    ties = p_ties(ctx)
    tf, groups, summary = {}, {}, {}
    by_row = {"%s#row%s" % (t["source_file"], t["source_row"]): t["test_id"] for t in ctx.tests}
    full, alt = {}, []
    rel = {inv: {e["code"]: (e.get("meaning") or {}).get("quote_relation", "")
                 for e in si["suffix_codes"]} for inv, si in ctx.spec("raw_names")["investigations"].items()}
    for inv, recs in ties.items():
        for f, level, rows, tests, suf, rule, others in recs:
            fg = full.setdefault((inv, f["category"], f["kind"], p_pattern(f["base"]), suf), [set(), 0, 0, rel[inv].get(suf, "")])
            if rule:
                fg[0].add(rule)
            fg[1] += bool(others)
            fg[2] += len(rows) > 1
            for o in others:
                alt.append((inv, f["id"], rule, level, ";".join(rows), o[0], o[1], ";".join(o[2])))
            res.checked += 1
            s = summary.setdefault(inv, {lv: [0, 0] for lv in P_LEVELS})
            s[level][0] += 1
            s[level][1] += f["bytes"]
            g = groups.setdefault((inv, f["category"], f["kind"], suf), [0, 0, 0, 0])
            g[0] += 1
            g[1] += f["bytes"]
            if level == "test":
                g[2] += 1
                g[3] += f["bytes"]
            if level == "none":
                continue
            for rk in rows:
                a = tf.setdefault((inv, by_row.get(rk, ""), rk, level, f["kind"], suf), [0, 0, 0])
                a[0] += 1
                a[1] += f["bytes"]
                a[2] += len(rows) > 1
    got_tf = {(r["investigation_id"], r["test_id"], r["table_row_key"], r["link_level"], r["kind"], r["suffix_code"]):
              [int(r["files"]), int(r["bytes"]), int(r["files_also_counted_for_another_row"])]
              for r in ctx.table("test_files.csv")}
    if got_tf != tf:
        diff = sorted(set(got_tf) ^ set(tf)) + sorted(k for k in set(got_tf) & set(tf) if got_tf[k] != tf[k])
        res.fail(problem="test_files.csv differs from the recount", rows=len(diff), examples=diff[:5])
    got_g = {}
    for r in ctx.table("raw_file_groups.csv"):
        g = got_g.setdefault((r["investigation_id"], r["psi_category"], r["kind"], r["suffix_code"]), [0, 0, 0, 0])
        for i, c in enumerate(("files", "bytes", "files_tied_to_a_test", "bytes_tied_to_a_test")):
            g[i] += int(r[c])
    if got_g != groups:
        res.fail(problem="raw_file_groups.csv by category, kind and suffix code differs from the recount",
                 examples=sorted(k for k in set(got_g) | set(groups) if got_g.get(k) != groups.get(k))[:5])
    got_full = {(r["investigation_id"], r["psi_category"], r["kind"], r["name_pattern"], r["suffix_code"]):
                [set(x for x in r["rules"].split(";") if x), int(r["files_with_another_tie_by_name"]),
                 int(r["files_tied_to_several_rows"]), r["quote_relation"]] for r in ctx.table("raw_file_groups.csv")}
    if got_full != full:
        res.fail(problem="raw_file_groups.csv by name pattern: rules, other ties, several rows or quote relation "
                         "differ from the recount",
                 examples=sorted(k for k in set(got_full) | set(full) if got_full.get(k) != full.get(k))[:5])
    if not ctx.has("name_tie_alternatives.csv"):
        res.fail(problem="name_tie_alternatives.csv not written")
    else:
        got_alt = sorted((r["investigation_id"], r["file_id"], r["deciding_rule"], r["deciding_level"], r["deciding_rows"],
                          r["other_rule"], r["other_level"], r["other_rows"]) for r in ctx.table("name_tie_alternatives.csv"))
        if got_alt != sorted(alt):
            res.fail(problem="name_tie_alternatives.csv differs from the recount", rows=len(got_alt), recount=len(alt))
    for e in ctx.json("raw_layers_summary.json")["investigations"]:
        want = summary.get(e["investigation_id"])
        if want is None or {lv: [e["names"][lv]["files"], e["names"][lv]["bytes"]] for lv in P_LEVELS} != want:
            res.fail(problem="names layer of the summary differs from the recount", investigation=e["investigation_id"])
    res.numbers = {"files": res.checked, "by_level": {lv: sum(s[lv][0] for s in summary.values()) for lv in P_LEVELS},
                   "test_files_rows": len(tf), "name_patterns": len(full), "alternative_ties": len(alt)}
    return res


@check("P4_layers_summary",
       "raw_layers_summary.json: per investigation and overall, the names layer equals the sums of raw_file_groups.csv, "
       "the structure layer the sample files of spec/raw_columns.json, the values layer the files of raw_values.csv, the "
       "archive layer archive_members_sample.csv; the overall numbers are the sums; the fixed sentences carry these numbers.")
def check_p4(ctx):
    res = Result()
    if not ctx.has("raw_layers_summary.json"):
        raise Skip("raw_layers_summary.json not written (python3 pipeline/raw_names.py)")
    S = ctx.json("raw_layers_summary.json")
    names = {}
    for r in ctx.table("raw_file_groups.csv"):
        n = names.setdefault(r["investigation_id"], {lv: [0, 0] for lv in P_LEVELS})
        for lv, f, b in (("test", "files_tied_to_a_test", "bytes_tied_to_a_test"),
                         ("day_or_session", "files_tied_to_a_day_or_session", "bytes_tied_to_a_day_or_session"),
                         ("none", "files_not_tied", "bytes_not_tied")):
            n[lv][0] += int(r[f])
            n[lv][1] += int(r[b])
    opened = {}
    for i in ctx.spec("raw_columns")["investigations"]:
        o = opened.setdefault(i["investigation_id"], {})
        for g in i["groups"]:
            for s in g.get("samples", []):
                o[s["psi_file_id"]] = s["bytes_listing"]
        for e in i["entries"]:
            o.setdefault(e["sample_file_id"], e["sample_bytes"])
    values = {}
    for r in ctx.table("raw_values.csv"):
        values.setdefault(r["investigation_id"], {})[r["psi_file_id"]] = int(r["bytes"])
    zips = {}
    for r in (ctx.table("archive_members_sample.csv") if ctx.has("archive_members_sample.csv") else []):
        zips.setdefault(r["investigation_id"], {})[r["archive_file_id"]] = (int(r["archive_bytes"]), int(r["bytes_fetched"]))
    tot = {"names": {lv: [0, 0] for lv in P_LEVELS}, "o": [0, 0], "v": [0, 0], "z": [0, 0, 0]}
    for e in S["investigations"]:
        inv = e["investigation_id"]
        res.checked += 1
        n = names.get(inv, {lv: [0, 0] for lv in P_LEVELS})
        if {lv: [e["names"][lv]["files"], e["names"][lv]["bytes"]] for lv in P_LEVELS} != n:
            res.fail(problem="names layer differs from raw_file_groups.csv", investigation=inv)
        o, v, z = opened.get(inv, {}), values.get(inv, {}), zips.get(inv, {})
        if [e["opened_for_structure"]["files"], e["opened_for_structure"]["bytes"]] != [len(o), sum(o.values())]:
            res.fail(problem="structure layer differs from raw_columns.json", investigation=inv)
        if [e["values_read"]["files"], e["values_read"]["bytes"]] != [len(v), sum(v.values())]:
            res.fail(problem="values layer differs from raw_values.csv", investigation=inv)
        a = e["archive_directories_listed"]
        if [a["archives"], a["bytes_of_those_archives"], a["bytes_fetched"]] != [len(z), sum(x[0] for x in z.values()), sum(x[1] for x in z.values())]:
            res.fail(problem="archive layer differs from archive_members_sample.csv", investigation=inv)
        for lv in P_LEVELS:
            tot["names"][lv][0] += n[lv][0]
            tot["names"][lv][1] += n[lv][1]
        tot["o"] = [tot["o"][0] + len(o), tot["o"][1] + sum(o.values())]
        tot["v"] = [tot["v"][0] + len(v), tot["v"][1] + sum(v.values())]
        tot["z"] = [tot["z"][0] + len(z), tot["z"][1] + sum(x[0] for x in z.values()), tot["z"][2] + sum(x[1] for x in z.values())]
    O = S["overall"]
    if {lv: [O["names"][lv]["files"], O["names"][lv]["bytes"]] for lv in P_LEVELS} != tot["names"]:
        res.fail(problem="overall names layer is not the sum")
    if [O["opened_for_structure"]["files"], O["opened_for_structure"]["bytes"]] != tot["o"] or \
            [O["values_read"]["files"], O["values_read"]["bytes"]] != tot["v"]:
        res.fail(problem="overall structure or values layer is not the sum")
    A = O["archive_directories_listed"]
    if [A["archives"], A["bytes_of_those_archives"], A["bytes_fetched"]] != tot["z"]:
        res.fail(problem="overall archive layer is not the sum")
    sev = {}
    for r in ctx.table("raw_file_groups.csv"):
        a = sev.setdefault(r["investigation_id"], [0, 0])
        a[0] += int(r["files_tied_to_several_rows"])
        a[1] += int(r["files_with_another_tie_by_name"])
    for e in S["investigations"]:
        if [e["files_tied_to_several_rows"], e["files_with_another_tie_by_name"]] != sev.get(e["investigation_id"], [0, 0]):
            res.fail(problem="several-rows or other-tie counts differ from raw_file_groups.csv", investigation=e["investigation_id"])
    if [O["files_tied_to_several_rows"], O["files_with_another_tie_by_name"]] != [sum(v[0] for v in sev.values()),
                                                                                 sum(v[1] for v in sev.values())]:
        res.fail(problem="overall several-rows or other-tie counts are not the sum")
    spec_n = ctx.spec("raw_names")
    rel_n, none_n, n_entries = {}, 0, 0
    for si in spec_n["investigations"].values():
        for e in si["suffix_codes"]:
            n_entries += 1
            m = e.get("meaning")
            if m:
                rel_n[m["quote_relation"]] = rel_n.get(m["quote_relation"], 0) + 1
            else:
                none_n += 1
    SC = O["suffix_codes"]
    if [SC["entries"], SC["entries_with_a_quote"], SC["entries_without_a_quote"]] != [n_entries, rel_n, none_n]:
        res.fail(problem="suffix code counts of the summary differ from the spec")
    used = {(r["investigation_id"], r["suffix_code"]) for r in ctx.table("raw_file_groups.csv")}
    unused = sorted((inv, e["code"]) for inv, si in spec_n["investigations"].items() for e in si["suffix_codes"]
                    if (inv, e["code"]) not in used)
    if sorted((x["investigation_id"], x["code"]) for x in SC["entries_matching_no_file"]) != unused:
        res.fail(problem="suffix entries matching no file differ from raw_file_groups.csv")
    byrel = {}
    for r in ctx.table("raw_file_groups.csv"):
        k = r["quote_relation"] or ("no quote" if r["suffix_code"] != "(no suffix code)" else "no suffix code")
        byrel[k] = byrel.get(k, 0) + int(r["files"])
    if SC["files_by_quote_relation"] != byrel:
        res.fail(problem="files by quote relation differ from raw_file_groups.csv")
    text = " ".join(S["sentences"])
    for num in (O["files"], tot["names"]["test"][0], tot["names"]["day_or_session"][0], tot["names"]["none"][0],
                tot["o"][0], tot["v"][0], tot["z"][0], tot["z"][2], tot["z"][1]):
        if not re.search(r"(?<![0-9])%d(?![0-9])" % num, text):
            res.fail(problem="a number of the summary is not in its sentences", number=num)
    for phrase in ("not checked", "not a priority"):
        if phrase not in text:
            res.fail(problem="fixed sentence missing", phrase=phrase)
    res.numbers = {"investigations": res.checked, "names_test_files": tot["names"]["test"][0],
                   "opened_files": tot["o"][0], "values_files": tot["v"][0], "archives_listed": tot["z"][0]}
    return res


def p_tied(ctx):
    def load():
        out = {}
        for r in ctx.table("test_files.csv"):
            if r["link_level"] == "test" and r["test_id"] and r["kind"] in ("video", "archive"):
                a = out.setdefault((r["test_id"], r["kind"]), [0, 0])
                a[0] += int(r["files"])
                a[1] += int(r["bytes"])
        return out
    return ctx._get("p_tied", load)


def p_tied_cols(ctx, inv, ids):
    tied = p_tied(ctx)
    out = {}
    for kind, pre in (("video", "videos"), ("archive", "archives")):
        hits = [tied[(t, kind)] for t in ids if (t, kind) in tied]
        out[pre + "_tied_to_those_tests_files"] = str(sum(h[0] for h in hits))
        out[pre + "_tied_to_those_tests_bytes"] = str(sum(h[1] for h in hits))
        out[pre + "_tied_to_those_tests_tests"] = str(len(hits))
    v = ctx.spec("raw_names")["investigations"].get(inv, {}).get("videos")
    out["video_on_screen_text"] = v["on_screen_text"] if v else "no video in the listing"
    return out


def p_video_sentences(ctx, inv, ids):
    T = ctx.spec("raw_names")["raw_state_sentences"]
    tied = p_tied(ctx)
    hits = [tied[(t, "video")] for t in ids if (t, "video") in tied]
    if not hits:
        return []
    out = [T["videos_tied"].format(n=sum(h[0] for h in hits), m=len(hits))]
    v = ctx.spec("raw_names")["investigations"][inv].get("videos")
    if v and v["labels_seen"]:
        out.append(T["videos_on_screen"].format(labels=", ".join(v["labels_seen"]), seen=v["seen_in"]))
    return out


@check("P5_raw_state_tied_files",
       "The columns that the name layer added to gap_states.csv, retrieval_queue.csv and need_gap_states.csv (videos and "
       "archives tied by name to the tests that lack the value, the class of on-screen text) and the fields added to the "
       "raw_state items of the evidence packages are recounted from test_files.csv, tests.csv and spec/raw_names.json; "
       "no sentence says that the quantity of an item can be read from a video.")
def check_p5(ctx):
    res = Result()
    for name in ("test_files.csv", "gap_states.csv", "retrieval_queue.csv", "need_gap_states.csv"):
        if not ctx.has(name):
            raise Skip(name + " not written")
    cols = ["videos_tied_to_those_tests_files", "videos_tied_to_those_tests_bytes", "videos_tied_to_those_tests_tests",
            "archives_tied_to_those_tests_files", "archives_tied_to_those_tests_bytes", "archives_tied_to_those_tests_tests",
            "video_on_screen_text"]
    by_inv = {}
    for t in ctx.tests:
        by_inv.setdefault(t["investigation_id"], []).append(t)
    for r in ctx.table("gap_states.csv"):
        res.checked += 1
        if r["state"] in ("in_table", "no_test_table"):
            want = {c: "" for c in cols}
        else:
            want = p_tied_cols(ctx, r["investigation_id"], [t["test_id"] for t in by_inv[r["investigation_id"]]
                                                             if o_blank(t.get(r["variable"]))])
        if {c: r.get(c) for c in cols} != want:
            res.fail(problem="gap_states.csv tied columns differ", row=(r["investigation_id"], r["variable"], r["state"]))
    supported = {n["id"]: {l["investigation_id"] for l in n.get("stated_by", []) if l["verdict"] == "supported"} for n in ctx.needs}
    uses = {}
    for n in ctx.needs:
        for v in n["conditions_required"] + n["conditions_useful"] + n["outcomes_any"]:
            uses.setdefault(v, []).append(n)
    for r in ctx.table("retrieval_queue.csv"):
        res.checked += 1
        lack = [t["test_id"] for t in by_inv[r["investigation_id"]] if o_blank(t.get(r["variable"])) and any(
            (not (n.get("scope") or {}).get("fuel_phase") or t["fuel_phase"] in n["scope"]["fuel_phase"])
            and r["investigation_id"] in supported[n["id"]] for n in uses[r["variable"]])]
        if {c: r.get(c) for c in cols} != p_tied_cols(ctx, r["investigation_id"], lack):
            res.fail(problem="retrieval_queue.csv tied columns differ", rank=r["rank"])
    need = {n["id"]: n for n in ctx.needs}
    for r in ctx.table("need_gap_states.csv"):
        res.checked += 1
        if r["state"] in ("in_table", "no_test_table"):
            want = ["", "", "", ""]
        else:
            nd = need[r["need_id"]]
            ph = (nd.get("scope") or {}).get("fuel_phase")
            members = [t for t in ctx.tests if (not ph or t["fuel_phase"] in ph)
                       and o_test_state(ctx, t, r["variable"]) == (r["state"], r["column_is"])]
            ids = [t["test_id"] for t in members]
            tied = p_tied(ctx)
            v = [tied[(i, "video")] for i in ids if (i, "video") in tied]
            a = [tied[(i, "archive")] for i in ids if (i, "archive") in tied]
            sent = []
            for inv in sorted({t["investigation_id"] for t in members}, key=psi_key):
                sent += p_video_sentences(ctx, inv, [t["test_id"] for t in members if t["investigation_id"] == inv])
            want = [str(sum(x[0] for x in v)), str(len(v)), str(sum(x[0] for x in a)), " ".join(sent)]
        have = [r["videos_tied_to_in_scope_tests_in_state"], r["video_tests_in_state"],
                r["archives_tied_to_in_scope_tests_in_state"], r["raw_state_video_sentences"]]
        if have != want:
            res.fail(problem="need_gap_states.csv tied columns differ", row=(r["scenario_id"], r["need_id"], r["variable"], r["state"]))
    items = 0
    for env, pack in packages(ctx):
        for b in (pack or {}).get("needs", []):
            for var, v in (b.get("raw_state") or {}).items():
                for pop in ("counted", "in_scope"):
                    for it in v[pop]["states"]:
                        if it["state"] in ("in_table", "no_test_table"):
                            continue
                        items += 1
                        if "files_tied_by_name" not in it or not isinstance(it.get("video_sentences"), list):
                            res.fail(problem="raw_state item without the name fields", package=env["id"], variable=var)
                            continue
                        for s in it["video_sentences"]:
                            if re.search(r"\bis in (the|a|these) video", s) or "can be read from them was not checked" not in s \
                                    and not s.startswith("Opened videos of this investigation show readings"):
                                res.fail(problem="video sentence not a fixed sentence", package=env["id"], sentence=s)
    res.numbers = {"rows": res.checked, "evidence_items_with_name_fields": items}
    return res


@check("P6_raw_names_spec",
       "spec/raw_names.json: every investigation of the listings is present; every meaning is a quote of 25 words or "
       "fewer with document, PSI file id and place, and the file id is a file of a listing of the same investigation "
       "(SKIP for the ids without listings); every rule names columns of its tables and known transforms.")
def check_p6(ctx):
    res = Result()
    spec = ctx.spec("raw_names")
    invs = {x["investigation_id"] for x in ctx.json("raw_inventory.json")["investigations"]}
    if set(spec["investigations"]) != invs:
        res.fail(problem="investigations differ from raw_inventory.json")
    known_key = set(spec["_meta"]["transforms"])
    have_list = os.path.isdir(LISTINGS)
    for inv, si in spec["investigations"].items():
        ids = None
        if have_list and os.path.exists(os.path.join(LISTINGS, inv + ".json")):
            ids = {f.get("id") for f in listing_records(read_json(os.path.join(LISTINGS, inv + ".json")))}
        for e in si["suffix_codes"] + si["identifier_meanings"]:
            m = e.get("meaning")
            if m is None:
                continue
            res.checked += 1
            if len(m["quote"].split()) > 25 or not all(m.get(k) for k in ("document", "file_id", "where")):
                res.fail(problem="quote too long or source incomplete", investigation=inv, code=e["code"])
            if ids is not None and m["file_id"] not in ids:
                res.fail(problem="file id of the quote is not in the listing", investigation=inv, file_id=m["file_id"])
            if m.get("quote_relation") not in spec["_meta"]["quote_relation"]:
                res.fail(problem="quote without a known quote_relation", investigation=inv, code=e["code"])
        headers = {t: read_raw_table(t)[0] for t in si["tables"]}
        for r in si["rules"]:
            for g, f in r["fields"].items():
                if f["key"] not in known_key or f["cell"] not in known_key:
                    res.fail(problem="unknown transform", investigation=inv, rule=r["id"])
                for t in (r.get("tables") or si["tables"]):
                    if any(c not in headers[t] for c in f["columns"]):
                        res.fail(problem="column not in table", investigation=inv, rule=r["id"], table=t)
                if f.get("lookup") and not (si.get("lookups", {}).get(f["lookup"], {}).get("pairs")):
                    res.fail(problem="lookup of the field is not in the investigation", investigation=inv, rule=r["id"])
                if (f["cell"] == "lookup_date") != bool(f.get("lookup")):
                    res.fail(problem="lookup_date without a lookup, or a lookup without lookup_date", investigation=inv, rule=r["id"])
                if "(?P<%s>" % g not in r["pattern"]:
                    res.fail(problem="field has no group in the pattern", investigation=inv, rule=r["id"], field=g)
    res.numbers = {"quotes": res.checked, "listings_present": have_list,
                   "rules": sum(len(si["rules"]) for si in spec["investigations"].values())}
    return res




# ----------------------------------------------------------------------------
# Q. the question chain (question_chain.csv, question_chain_counts.csv), written by
#    pipeline/question_chain.py; recomputed here from the inputs with separate code
# ----------------------------------------------------------------------------

# Fixtures of docs/raw_data_design/design.md section 10 (placement of all tests, and of the solid-fuel
# scope), of the video design (docs/video_design/design.md section 12) and of claims.md (the nine CFI-G
# tests inside the lunar ranges: 7 not stated, 2 without an outcome).
Q_PLACEMENT_FIXTURES = {
    ("lunar_habitat", "S1"): {"inside": 26, "cannot_be_placed_from_table": 676, "oxygen_of_oxidizer_stream": 63,
                              "outside_by_recorded_value": 1059},
    ("lunar_habitat", "P1"): {"inside": 0, "cannot_be_placed_from_table": 237, "outside_by_recorded_value": 139},
    ("iss", "S1"): {"inside": 179, "cannot_be_placed_from_table": 739, "oxygen_of_oxidizer_stream": 106,
                    "outside_by_recorded_value": 800},
    ("mars_habitat", "S1"): {"no_range_set": 1824},
}
Q_P1_PRESSURE_STATES = {"column_in_sampled_raw_file": 134, "documented_only": 129, "not_in_sampled_files": 113}
Q_LOC_STATE = {"table_cell": "in_table", "raw_file_value_read": "column_in_sampled_raw_file",
               "raw_file_column_seen": "column_in_sampled_raw_file", "document_sentence": "documented_only",
               "not_found_in_files_opened": "not_in_sampled_files"}
# a row of raw_values.csv gives a value for this variable (extraction -> key as written -> variable; '*' any key)
Q_RAW_VARIABLE = {"saffire_ambient_pressure": {"*": "pressure_kpa"},
                  "same_particle_size_statistics": {"*": "smoke_particle_size_um"},
                  "flex_test_sheet": {"Dext (mm)": "extinction_diameter_mm", "Pressure (atm)": "pressure_kpa",
                                      "O2 Mole Fraction": "o2_pct"}}
Q_VIDEO_ORDER = ("two_labels_agree", "one_label", "labels_disagree")
Q_NO_VIDEO_VARIABLES = ("o2_pct", "pressure_kpa", "co_produced_ppm", "co2_produced_pct_points",
                        "co_to_co2_molar_ratio", "smoke_particle_size_um", "aging_time_s")


def q_place(o2, p):
    if (o2, p) == ("not_specified", "not_specified"):
        return "no_range_set"
    if "out" in (o2, p):
        return "outside_by_recorded_value"
    if (o2, p) == ("in", "in"):
        return "inside"
    return "oxygen_of_oxidizer_stream" if o2 == "not_ambient" else "cannot_be_placed_from_table"


def q_inputs(ctx):
    if not ctx.has("question_chain.csv"):
        raise Skip("question_chain.csv not written")

    def load():
        tests = ctx.tests
        marks = {(r["scenario_id"], r["test_id"]): r for r in ctx.table("scenario_tests.csv")}
        link = {}
        for r in ctx.table("need_tests.csv"):
            link[(r["need_id"], r["test_id"])] = r["objective_link"]
        scope = {}
        for n in ctx.needs:
            ph = (n.get("scope") or {}).get("fuel_phase")
            scope[n["id"]] = [t for t in tests if not ph or t["fuel_phase"] in ph]
        return {"tests": tests, "marks": marks, "link": link, "scope": scope,
                "scenarios": [s["id"] for s in ctx.spec("scenarios")["scenarios"]],
                "rows": ctx.table("question_chain.csv")}
    return ctx._get("q_inputs", load)


def q_location(ctx, test, var):
    """Location of one quantity of one test, from the inputs (not from raw_gaps.py)."""
    def raw_index():
        idx = set()
        for r in ctx.table("raw_values.csv"):
            m = Q_RAW_VARIABLE.get(r["extraction"])
            if m and r["test_id"]:
                v = m.get(" ".join(r["header_as_written"].split()), m.get("*"))
                if v:
                    idx.add((r["test_id"], v))
        return idx

    def entries():
        e = set()
        for inv in ctx.spec("raw_columns")["investigations"]:
            for x in inv["entries"]:
                e.add((inv["investigation_id"], x["standard_variable"]))
        return e

    def docs():
        d = set()
        for s in ctx.sources:
            for x in s.get("documented_elsewhere", []) or []:
                d.add((s["investigation_id"], x["variable"]))
        return d
    if not o_blank(test.get(var)):
        return "table_cell"
    if (test["test_id"], var) in ctx._get("q_raw", raw_index):
        return "raw_file_value_read"
    inv = test["investigation_id"]
    if (inv, var) in ctx._get("q_entries", entries):
        return "raw_file_column_seen"
    if (inv, var) in ctx._get("q_docs", docs):
        return "document_sentence"
    return "not_found_in_files_opened"


@check("Q1_chain_placements",
       "question_chain.csv: the placement of every test (scenario_tests.csv oxygen and pressure match, recomputed); "
       "the quantity rows of each scenario, need, role and variable sum to the tests in the need's scope and to its "
       "counted tests, per placement; fixtures of design.md section 10 (lunar habitat 26 / 676 / 63 / 1,059; solid "
       "0 / 237 / 139; ISS 179 / 739 / 106 / 800; Mars habitat no range set for 1,824).")
def check_q1(ctx):
    res = Result()
    Q = q_inputs(ctx)
    got = {}
    for r in Q["rows"]:
        if r["row_kind"] != "quantity":
            continue
        k = (r["scenario_id"], r["need_id"], r["role"], r["variable"])
        a = got.setdefault(k, {})
        b = a.setdefault(r["placement"], [0, 0])
        b[0] += int(r["in_scope_tests"])
        b[1] += int(r["counted_tests"])
        if q_place(r["o2_match"], r["pressure_match"]) != r["placement"]:
            res.fail(problem="placement does not follow from the pair", row=k, pair=(r["o2_match"], r["pressure_match"]))
    for sid in Q["scenarios"]:
        for n in ctx.needs:
            want = {}
            for t in Q["scope"][n["id"]]:
                m = Q["marks"][(sid, t["test_id"])]
                w = want.setdefault(q_place(m["o2_match"], m["pressure_match"]), [0, 0])
                w[0] += 1
                w[1] += Q["link"].get((n["id"], t["test_id"])) == "stated"
            roles = [("required", v) for v in n["conditions_required"]] + \
                    [("useful", v) for v in n.get("conditions_useful", [])] + [("outcome", v) for v in n["outcomes_any"]]
            for role, var in roles:
                res.checked += 1
                g = got.get((sid, n["id"], role, var), {})
                if g != want:
                    res.fail(problem="placement sums differ", scenario=sid, need=n["id"], variable=var, file=g, recount=want)
            fx = Q_PLACEMENT_FIXTURES.get((sid, n["id"]))
            if fx:
                have = {k: v[0] for k, v in want.items()}
                if {k: v for k, v in have.items() if v} != {k: v for k, v in fx.items() if v}:
                    res.fail(problem="fixture of design.md section 10 not reproduced", scenario=sid, need=n["id"],
                             recount=have, fixture=fx)
    res.numbers = {"blocks": res.checked, "rows": len(Q["rows"]),
                   "lunar_S1": {k: v[0] for k, v in sorted(got.get(("lunar_habitat", "S1", "required", "o2_pct"), {}).items())}}
    return res


@check("Q2_chain_locations",
       "question_chain.csv: the location of every quantity of every test recomputed from tests.csv, raw_values.csv, "
       "spec/raw_columns.json and spec/sources.json (table cell, value read, column seen, document sentence, not "
       "found), aggregated by scenario, need, role, variable, investigation, placement and location; summed over "
       "placement the rows equal need_gap_states.csv (required and outcome roles); lunar habitat P1 pressure: raw "
       "column 134, document only 129, not found 113.")
def check_q2(ctx):
    res = Result()
    Q = q_inputs(ctx)
    file_agg, state_agg = {}, {}
    for r in Q["rows"]:
        if r["row_kind"] != "quantity":
            continue
        if Q_LOC_STATE.get(r["location"]) != r["state"]:
            res.fail(problem="location and state do not agree", location=r["location"], state=r["state"])
        k = (r["scenario_id"], r["need_id"], r["role"], r["variable"], r["investigation_id"], r["placement"], r["location"])
        a = file_agg.setdefault(k, [0, 0])
        a[0] += int(r["in_scope_tests"])
        a[1] += int(r["counted_tests"])
        k2 = (r["scenario_id"], r["need_id"], r["role"], r["variable"], r["state"],
              r["column_is_or_doc"] if r["state"] == "column_in_sampled_raw_file" else "")
        b = state_agg.setdefault(k2, [0, 0])
        b[0] += int(r["in_scope_tests"])
        b[1] += int(r["counted_tests"])
    want = {}
    for sid in Q["scenarios"]:
        for n in ctx.needs:
            roles = [("required", v) for v in n["conditions_required"]] + \
                    [("useful", v) for v in n.get("conditions_useful", [])] + [("outcome", v) for v in n["outcomes_any"]]
            for t in Q["scope"][n["id"]]:
                m = Q["marks"][(sid, t["test_id"])]
                p = q_place(m["o2_match"], m["pressure_match"])
                c = Q["link"].get((n["id"], t["test_id"])) == "stated"
                for role, var in roles:
                    k = (sid, n["id"], role, var, t["investigation_id"], p, q_location(ctx, t, var))
                    w = want.setdefault(k, [0, 0])
                    w[0] += 1
                    w[1] += c
    for k in sorted(set(want) | set(file_agg)):
        res.checked += 1
        if want.get(k) != file_agg.get(k):
            res.fail(problem="location count differs", key=k, file=file_agg.get(k), recount=want.get(k))
    n_rows = 0
    for r in ctx.table("need_gap_states.csv"):
        n_rows += 1
        k = (r["scenario_id"], r["need_id"], r["role"], r["variable"], r["state"], r["column_is"])
        if state_agg.get(k) != [int(r["in_scope_tests_in_state"]), int(r["counted_tests_in_state"])]:
            res.fail(problem="chain summed over placement differs from need_gap_states.csv", key=k,
                     chain=state_agg.get(k), need_gap_states=[r["in_scope_tests_in_state"], r["counted_tests_in_state"]])
    covered = {k for k in state_agg if k[2] in ("required", "outcome")}
    if len(covered) != n_rows:
        res.fail(problem="chain has state rows that need_gap_states.csv lacks, or the reverse", chain=len(covered), ngs=n_rows)
    p1 = {}
    for k, v in state_agg.items():
        if k[:4] == ("lunar_habitat", "P1", "required", "pressure_kpa") and k[4] != "in_table":
            p1[k[4]] = p1.get(k[4], 0) + v[0]
    if p1 != Q_P1_PRESSURE_STATES:
        res.fail(problem="P1 pressure fixture not reproduced", recount=p1, fixture=Q_P1_PRESSURE_STATES)
    res.numbers = {"keys": res.checked, "need_gap_state_rows": n_rows, "lunar_P1_pressure": p1}
    return res


@check("Q3_chain_inside_and_counts",
       "Counted tests placed inside equal tests_atmosphere of scenario_needs.csv; question_chain_counts.csv per "
       "scenario, need, placement and pair: tests in scope, counted, not counted split into objective not stated, "
       "no outcome in the table, a required condition missing (recomputed); claims.md: of the 9 CFI-G tests inside "
       "the lunar ranges 7 are not stated and 2 hold no outcome for S1; the 17 counted lunar S1 tests are FLEX.")
def check_q3(ctx):
    res = Result()
    Q = q_inputs(ctx)
    inside = {}
    for r in Q["rows"]:
        if r["row_kind"] == "quantity" and r["placement"] == "inside" and r["variable"] == "o2_pct" and r["role"] in ("required", "useful"):
            inside[(r["scenario_id"], r["need_id"])] = inside.get((r["scenario_id"], r["need_id"]), 0) + int(r["counted_tests"])
    for r in ctx.table("scenario_needs.csv"):
        res.checked += 1
        if inside.get((r["scenario_id"], r["need_id"]), 0) != int(r["tests_atmosphere"]):
            res.fail(problem="inside counted differs from scenario_needs.csv", scenario=r["scenario_id"], need=r["need_id"],
                     chain=inside.get((r["scenario_id"], r["need_id"]), 0), scenario_needs=r["tests_atmosphere"])
    if not ctx.has("question_chain_counts.csv"):
        res.fail(problem="question_chain_counts.csv absent")
        return res
    file_rows = {(r["scenario_id"], r["need_id"], r["level"], r["placement"], r["o2_match"], r["pressure_match"]): r
                 for r in ctx.table("question_chain_counts.csv")}
    seen = set()
    cfig = None
    for sid in Q["scenarios"]:
        for n in ctx.needs:
            b = {}
            for t in Q["scope"][n["id"]]:
                m = Q["marks"][(sid, t["test_id"])]
                p = q_place(m["o2_match"], m["pressure_match"])
                for k in ((sid, n["id"], "placement", p, "", ""), (sid, n["id"], "placement_pair", p, m["o2_match"], m["pressure_match"])):
                    b.setdefault(k, []).append(t)
            for k, ts in b.items():
                res.checked += 1
                seen.add(k)
                lk = [Q["link"].get((n["id"], t["test_id"])) for t in ts]
                counted = sum(1 for x in lk if x == "stated")
                not_stated = sum(1 for x in lk if x == "not_stated")
                no_row = [t for t, x in zip(ts, lk) if x is None]
                no_out = sum(1 for t in no_row if all(not o_blank(t.get(v)) for v in n["conditions_required"])
                             and all(o_blank(t.get(v)) for v in n["outcomes_any"]))
                want = (len(ts), counted, len(ts) - counted, not_stated, no_out, len(ts) - counted - not_stated - no_out)
                r = file_rows.get(k)
                got = None if r is None else tuple(int(r[c]) for c in ("in_scope_tests", "counted_tests", "not_counted_tests",
                                                                          "n_not_stated", "n_no_outcome", "n_required_condition_missing"))
                if got != want:
                    res.fail(problem="counts view differs", key=k, file=got, recount=want)
                if k == ("lunar_habitat", "S1", "placement", "inside", "", ""):
                    cf = [t for t in ts if t["investigation_id"] == "PSI-159"]
                    cfig = (len(cf), sum(1 for t in cf if Q["link"].get(("S1", t["test_id"])) == "not_stated"),
                            sum(1 for t in cf if ("S1", t["test_id"]) not in Q["link"]))
                    fl = {t["investigation_id"] for t in ts if Q["link"].get(("S1", t["test_id"])) == "stated"}
                    if cfig != (9, 7, 2) or fl != {"PSI-69"} or counted != 17:
                        res.fail(problem="claims.md fixture (9 CFI-G = 7 + 2; 17 counted FLEX) not reproduced",
                                 cfig=cfig, counted_investigations=sorted(fl), counted=counted)
    if set(file_rows) != seen:
        res.fail(problem="counts view rows differ from the recount", extra=sorted(set(file_rows) - seen)[:5],
                 missing=sorted(seen - set(file_rows))[:5])
    res.numbers = {"rows": res.checked, "lunar_S1_inside_cfig_total_not_stated_no_outcome": cfig}
    return res


@check("Q4_chain_video",
       "Video in the chain: the best link state of a video tied to each test, recomputed from pm's video index "
       "(video/data/video_links.csv), in the counts view; the video rows are the BASS-II main-view recordings "
       "(investigation PSI-25, view 'main'; files, bytes, transcribed) for flow_cms only, never for oxygen, "
       "pressure, CO, CO2, the CO to CO2 ratio, particle size or aging time; fixtures: ISS P1, oxygen inside and "
       "pressure not in the table, 55 counted: 42 / 4 / 0 / 9, main view 49 files, 3,515,643,202 bytes, 7 transcribed; "
       "lunar habitat inside 26, 8 with two agreeing labels (all CFI-G), 0 of 17 counted.")
def check_q4(ctx):
    res = Result()
    Q = q_inputs(ctx)
    path = os.path.join(ROOT, "video", "data", "video_links.csv")
    if not os.path.exists(path):
        raise Skip("video/data/video_links.csv absent")
    with open(path, encoding="utf-8", newline="") as f:
        vids = list(csv.DictReader(l for l in f if not l.startswith("#")))
    best, main = {}, {}
    for v in vids:
        if v["test_id"] and v["link_state"] in Q_VIDEO_ORDER:
            b = best.get(v["test_id"])
            if b is None or Q_VIDEO_ORDER.index(v["link_state"]) < Q_VIDEO_ORDER.index(b):
                best[v["test_id"]] = v["link_state"]
            if v["investigation"] == "PSI-25" and v["view_from_name"] == "main":
                main.setdefault(v["test_id"], []).append(v)
    grp = [v for v in vids if v["investigation"] == "PSI-25" and v["view_from_name"] == "main"]
    g = (len(grp), sum(int(v["bytes"]) for v in grp), sum(1 for v in grp if v["transcribed"] == "yes"))
    for r in Q["rows"]:
        if r["row_kind"] != "video":
            continue
        res.checked += 1
        if r["variable"] in Q_NO_VIDEO_VARIABLES or r["variable"] != "flow_cms" or r["location"] != "video_on_screen_text":
            res.fail(problem="video row for a variable the screen does not show", variable=r["variable"])
        if (int(r["files"]), int(r["bytes"]), int(r["files_opened"])) != g:
            res.fail(problem="video group files, bytes or transcribed differ", file=(r["files"], r["bytes"], r["files_opened"]), recount=g)
    for r in Q["rows"]:
        if r["location"] == "video_on_screen_text" and r["row_kind"] != "video":
            res.fail(problem="video location on a quantity row")
    tid = {t["test_id"]: t for t in Q["tests"]}
    for r in ctx.table("question_chain_counts.csv"):
        res.checked += 1
        ts = []
        for t in Q["scope"][r["need_id"]]:
            m = Q["marks"][(r["scenario_id"], t["test_id"])]
            if q_place(m["o2_match"], m["pressure_match"]) == r["placement"] and \
                    (r["level"] == "placement" or (m["o2_match"], m["pressure_match"]) == (r["o2_match"], r["pressure_match"])):
                ts.append(t["test_id"])
        c = [t for t in ts if Q["link"].get((r["need_id"], t)) == "stated"]
        want = tuple(sum(1 for t in c if best.get(t) == s) for s in Q_VIDEO_ORDER) + (sum(1 for t in c if t not in best),)
        want += tuple(sum(1 for t in ts if best.get(t) == s) for s in Q_VIDEO_ORDER)
        mv = [v for t in c for v in main.get(t, [])]
        want += (len(mv), sum(int(v["bytes"]) for v in mv), sum(1 for v in mv if v["transcribed"] == "yes"))
        got = tuple(int(r[k]) for k in ("counted_with_video_two_labels_agree", "counted_with_video_one_label",
                                        "counted_with_video_labels_disagree_only", "counted_without_video",
                                        "in_scope_with_video_two_labels_agree", "in_scope_with_video_one_label",
                                        "in_scope_with_video_labels_disagree_only", "counted_main_view_files",
                                        "counted_main_view_bytes", "counted_main_view_files_transcribed"))
        if got != want:
            res.fail(problem="video counts differ", key=(r["scenario_id"], r["need_id"], r["level"], r["placement"], r["o2_match"], r["pressure_match"]),
                     file=got, recount=want)
        if (r["scenario_id"], r["need_id"], r["level"], r["o2_match"], r["pressure_match"]) == ("iss", "P1", "placement_pair", "in", "not_recorded"):
            fx = (int(r["counted_tests"]),) + want[:4] + want[7:]
            if fx != (55, 42, 4, 0, 9, 49, 3515643202, 7):
                res.fail(problem="ISS P1 video fixture not reproduced", recount=fx)
        if (r["scenario_id"], r["need_id"], r["level"], r["placement"]) == ("lunar_habitat", "S1", "placement", "inside"):
            two = [t for t in ts if best.get(t) == "two_labels_agree"]
            fx = (len(ts), len(two), {tid[t]["investigation_id"] for t in two}, want[0])
            if fx != (26, 8, {"PSI-159"}, 0):
                res.fail(problem="lunar video fixture not reproduced", recount=str(fx))
    res.numbers = {"rows": res.checked, "video_group": g, "tests_with_a_video_by_best_state":
                   {s: sum(1 for v in best.values() if v == s) for s in Q_VIDEO_ORDER}}
    return res



# ----------------------------------------------------------------------------
# R. values read from raw files that design steps 4 and 5 added to raw_values.csv
#    (FLEX test sheets, BASS as-run cabin block); recomputed with separate code
# ----------------------------------------------------------------------------

R_FLEX_TABLE = "PSI-69_Experimental table_FLEX.csv"
R_LUNAR_DEXT = {  # design.md section 7: (table form, sheet form) -> tests
    ("number", "number"): {"FLEX-21", "FLEX-25", "FLEX-26"}, ("number", "nan"): {"FLEX-20"},
    ("zero", "zero"): {"FLEX-39", "FLEX-43"}, ("blank", "number"): {"FLEX-23", "FLEX-38"},
    ("blank", "nan"): {"FLEX-19", "FLEX-22", "FLEX-24", "FLEX-27", "FLEX-28", "FLEX-37"},
    ("dash", "number"): {"FLEX-40"}, ("dash", "zero"): {"FLEX-41"}, ("dash", "nan"): {"FLEX-42"}}


def r_form(v):
    v = (v or "").strip()
    if not v:
        return "blank"
    if v in ("-", "–", "—"):
        return "dash"
    if v.lower() == "nan":
        return "nan"
    try:
        return "zero" if float(v) == 0 else "number"
    except ValueError:
        return "text"


def r_table(name):
    """(source row, {column: cell as written}) of a raw table; cp1252 where the file is not UTF-8 (en dashes)."""
    raw = read_bytes(os.path.join(RAW, name))
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    rows = list(csv.reader(io.StringIO(text, newline="")))
    head = [h.strip() for h in rows[0]]
    return [(i, dict(zip(head, r + [""] * (len(head) - len(r))))) for i, r in enumerate(rows[1:], start=2)]


def r_flex_table():
    return r_table(R_FLEX_TABLE)


def r_sheets(ctx):
    sheets = {}
    for r in ctx.table("raw_values.csv"):
        if r["extraction"] == "flex_test_sheet":
            k = " ".join(r["header_as_written"].split())
            sheets.setdefault(r["psi_file_name"], {"rows": [], "fields": {}, "id": r["psi_file_id"], "bytes": int(r["bytes"])})
            sheets[r["psi_file_name"]]["rows"].append(r)
            sheets[r["psi_file_name"]]["fields"][k] = r["value"]
    return sheets


@check("R1_flex_test_sheets",
       "FLEX test sheets in raw_values.csv (extraction flex_test_sheet): each sheet tied again by the CIR test number "
       "printed inside plus its FLEX number or test date against NASA's FLEX table; identifier, pressure (sheet atm "
       "against table mmHg / 760, half a unit of the sheet's last decimal) and oxygen compared again; values kept as "
       "written; flex_sheet_vs_table.csv and the block flex_test_sheets of raw_values_effect.json agree; fixture of "
       "design.md section 7 for the 17 FLEX tests inside the lunar ranges (identifier 17 of 17, pressure 16 of 17 "
       "with FLEX-23 off, oxygen 16 of 17 with FLEX-28 off, the extinction-diameter cross-table).")
def check_r1(ctx):
    res = Result()
    sheets = r_sheets(ctx)
    if not sheets:
        raise Skip("no FLEX test sheet in raw_values.csv")
    table = r_flex_table()
    test_of = {int(t["source_row"]): t["test_id"] for t in ctx.tests if t["source_file"] == R_FLEX_TABLE}
    rec = {}
    for name, sh in sheets.items():
        res.checked += 1
        f = sh["fields"]
        ident = f.get("CIR Test Number", "")
        num = re.match(r"^FLEX-(\d+)$", f.get("(first line)", ""))
        cands = [(n, c) for n, c in table if c["FLEX Identifier"].strip() == ident]
        pick = [(n, c) for n, c in cands if num and c["FLEX Test #"].strip() == str(int(num.group(1)))]
        if len(pick) != 1:
            m = re.match(r"^\s*\w+,\s*(\w+)\s+(\d+),\s*(\d{4})", f.get("Test Date", ""))
            months = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                      "October", "November", "December"]
            want = (int(m.group(3)), months.index(m.group(1)) + 1, int(m.group(2))) if m and m.group(1) in months else None
            def tdate(x):
                mm = re.match(r"^\s*(\d+)/(\d+)/(\d{2,4})\s*$", x)
                return (int(mm.group(3)) + (2000 if len(mm.group(3)) == 2 else 0), int(mm.group(1)), int(mm.group(2))) if mm else None
            pick = [(n, c) for n, c in cands if want and tdate(c["Test Date"]) == want]
        row = pick[0] if len(pick) == 1 else None
        tid = test_of.get(row[0], "") if row else ""
        if any(r["test_id"] != tid for r in sh["rows"]):
            res.fail(problem="tie of the sheet differs from the recount", sheet=name, recount=tid)
        if any(r["test_id"] and "tests.csv" not in r["link_evidence"] for r in sh["rows"]):
            res.fail(problem="tied row without tests.csv evidence", sheet=name)
        if row:
            c = row[1]
            p_sheet = fnum(f.get("Pressure (atm)", ""))
            p_tab = fnum(c["Ambient pressure; mmHg"])
            dec = len(f.get("Pressure (atm)", "").split(".", 1)[1]) if "." in f.get("Pressure (atm)", "") else 0
            p_ok = p_sheet is not None and p_tab is not None and abs(p_sheet - p_tab / 760.0) <= 0.5 * 10 ** -dec + 1e-9
            o_sheet, o_tab = fnum(f.get("O2 Mole Fraction", "")), fnum(c["O initial ambient composition; mole fraction"])
            dec = len(f.get("O2 Mole Fraction", "").split(".", 1)[1]) if "." in f.get("O2 Mole Fraction", "") else 0
            o_ok = o_sheet is not None and o_tab is not None and abs(o_sheet - o_tab) <= 0.5 * 10 ** -dec + 1e-9
            rec[name] = {"test_id": tid, "id": ident == c["FLEX Identifier"].strip(), "p": p_ok, "o": o_ok,
                        "dext": (r_form(c["Visible flame extinction diameter; mm"]), r_form(f.get("Dext (mm)", "")))}
        for r in sh["rows"]:
            if r["value"] != r["value"].strip(" \t"):
                res.fail(problem="value not stripped as the rule says", sheet=name)
    lunar = {m["test_id"] for m in ctx.table("scenario_tests.csv") if m["scenario_id"] == "lunar_habitat"
             and m["investigation_id"] == "PSI-69" and m["o2_match"] == "in" and m["pressure_match"] == "in"}
    by_t = {}
    for v in rec.values():
        by_t.setdefault(v["test_id"], []).append(v)
    lun = {t: (by_t.get(t) or [None])[0] for t in lunar}
    if any(len(by_t.get(t, [])) > 1 for t in lunar):
        res.fail(problem="a lunar FLEX test has more than one tied sheet")
    nums = {}
    if all(lun.values()) and len(lunar) == 17:
        nums = {"identifier": sum(1 for v in lun.values() if v["id"]), "pressure": sum(1 for v in lun.values() if v["p"]),
                "oxygen": sum(1 for v in lun.values() if v["o"])}
        off = ({t for t, v in lun.items() if not v["p"]}, {t for t, v in lun.items() if not v["o"]})
        cross = {}
        for t, v in lun.items():
            cross.setdefault(v["dext"], set()).add(t)
        if nums != {"identifier": 17, "pressure": 16, "oxygen": 16} or off != ({"FLEX-23"}, {"FLEX-28"}) or cross != R_LUNAR_DEXT:
            res.fail(problem="lunar fixture of design.md section 7 not reproduced", recount=nums,
                     off=[sorted(off[0]), sorted(off[1])], cross={"%s/%s" % k: sorted(v) for k, v in cross.items()})
    else:
        res.fail(problem="not all 17 lunar FLEX tests have a tied sheet", tied=sorted(t for t, v in lun.items() if v))
    # flex_sheet_vs_table.csv and the effect block
    if ctx.has("flex_sheet_vs_table.csv"):
        ft = ctx.table("flex_sheet_vs_table.csv")
        if len({r["psi_file_name"] for r in ft}) != len(sheets):
            res.fail(problem="flex_sheet_vs_table.csv sheets differ from raw_values.csv")
        for r in ft:
            t = r["psi_file_name"]
            if r["key"] == "Pressure (atm)" and t in rec and (r["agreement"] in ("agrees_within_rounding", "agrees_as_written")) != rec[t]["p"]:
                res.fail(problem="pressure agreement differs", test_id=t)
            if r["key"] == "O2 Mole Fraction" and t in rec and (r["agreement"] in ("agrees_within_rounding", "agrees_as_written")) != rec[t]["o"]:
                res.fail(problem="oxygen agreement differs", test_id=t)
    else:
        res.fail(problem="flex_sheet_vs_table.csv absent")
    eff = ctx.json("raw_values_effect.json").get("flex_test_sheets")
    if not eff:
        res.fail(problem="raw_values_effect.json has no block flex_test_sheets")
    else:
        a = eff["all_sheets"]
        want = (len(sheets), sum(s["bytes"] for s in sheets.values()), sum(1 for v in rec.values() if v["p"]),
                sum(1 for v in rec.values() if v["o"]))
        if (a["sheets_read"], a["bytes_read"], a["pressure_agrees_within_rounding"], a["oxygen_agrees"]) != want:
            res.fail(problem="effect block counts differ", block=(a["sheets_read"], a["bytes_read"], a["pressure_agrees_within_rounding"], a["oxygen_agrees"]), recount=want)
        l = eff["lunar_habitat_inside"]
        if nums and (l["identifier_equals_table"], l["pressure_agrees_within_rounding"], l["oxygen_agrees"]) != (17, 16, 16):
            res.fail(problem="effect block lunar counts differ")
        if "not adopted" not in eff["state"]:
            res.fail(problem="state is not 'not adopted'")
    res.numbers = {"sheets": len(sheets), "bytes": sum(s["bytes"] for s in sheets.values()), "tied": len(rec),
                   "tests_with_two_tied_sheets": sorted(t for t, v in by_t.items() if len(v) > 1),
                   "lunar": nums}
    return res


@check("R2_bass_as_run",
       "BASS as-run workbook in raw_values.csv (extraction bass_as_run_cabin_block): two rows per run for 121 runs, "
       "the columns 'O2 % by volume' and 'pressure, atm'; each run tied to a distinct test of PSI-26 in tests.csv "
       "('As Run Test #' and 'Test #' recomputed from NASA's table); every row carries location_not_stated and every "
       "oxygen value below 1 magnitude_not_as_unit_written; no row gives a location in question_chain.csv; the block "
       "of raw_values_effect.json recounts.")
def check_r2(ctx):
    res = Result()
    rows = [r for r in ctx.table("raw_values.csv") if r["extraction"] == "bass_as_run_cabin_block"]
    if not rows:
        raise Skip("no BASS as-run row in raw_values.csv")
    table = r_table("PSI-26_Experimental table_BASS.csv")
    test_of = {int(t["source_row"]): t["test_id"] for t in ctx.tests if t["source_file"] == "PSI-26_Experimental table_BASS.csv"}
    runs = {}
    for r in rows:
        res.checked += 1
        runs.setdefault((r["sheet"], r["row"]), []).append(r)
        if "location_not_stated" not in r["link_evidence"]:
            res.fail(problem="row without location_not_stated", cell=r["cell_or_range"])
        v = fnum(r["value"])
        if r["header_as_written"].startswith("O2") and v is not None and 0 < v < 1 and "magnitude_not_as_unit_written" not in r["link_evidence"]:
            res.fail(problem="oxygen below 1 without magnitude_not_as_unit_written", cell=r["cell_or_range"])
        m = re.search(r"'As run test no\.' (\S+) and 'Test no\.' (\S+) equal", r["link_evidence"])
        if r["test_id"]:
            if not m:
                res.fail(problem="tie evidence not parseable", cell=r["cell_or_range"])
                continue
            c = [n for n, c in table if c.get("As Run Test #", "").strip() == m.group(1) and c.get("Test #", "").strip() == m.group(2)]
            if len(c) != 1 or test_of.get(c[0]) != r["test_id"]:
                res.fail(problem="tie differs from the recount", cell=r["cell_or_range"], test_id=r["test_id"])
    tids = {r["test_id"] for r in rows if r["test_id"]}
    heads = sorted({r["header_as_written"] for r in rows})
    if len(runs) != 121 or len(tids) != 121 or any(len(v) != 2 for v in runs.values()) or heads != ["O2 % by volume", "pressure, atm"]:
        res.fail(problem="not 121 runs with two columns tied to 121 tests", runs=len(runs), tests=len(tids), headers=heads)
    if any(not t.startswith("BASS-") for t in tids) or len(tids & {t["test_id"] for t in ctx.tests if t["investigation_id"] == "PSI-26"}) != len(tids):
        res.fail(problem="a tied test is not a PSI-26 test")
    if ctx.has("question_chain.csv"):
        for r in ctx.table("question_chain.csv"):
            if r["investigation_id"] == "PSI-26" and r["location"] == "raw_file_value_read":
                res.fail(problem="a PSI-26 test has a value-read location")
    eff = ctx.json("raw_values_effect.json").get("bass_as_run_cabin_block")
    if not eff or eff["runs"] != len(runs) or any(eff["columns"][h]["rows"] != sum(1 for r in rows if r["header_as_written"] == h) for h in heads):
        res.fail(problem="effect block bass_as_run_cabin_block differs")
    res.numbers = {"rows": len(rows), "runs": len(runs), "tests": len(tids)}
    return res



# ----------------------------------------------------------------------------
# S. file-to-test links (file_links.csv, file_links_summary.json, test_files.json,
#    listing_snapshot.json, video_tie_differences.csv), written by pipeline/file_links.py
# ----------------------------------------------------------------------------

S_INVS = ("PSI-10", "PSI-25", "PSI-39", "PSI-69", "PSI-99", "PSI-159")
S_VIDEO_FIXTURE = {"PSI-25": (244, 47, 5), "PSI-159": (314, 11, 2), "PSI-39": (101, 5, 2), "PSI-69": (3, 5, 1),
                   "PSI-10": (0, 306, 0)}
S_VIDEO_TOTALS = {"two_labels_agree": 662, "one_label": 374, "labels_disagree": 10, "day_only": 1217,
                  "id_not_in_table": 330, "none": 30}
S_STATES = ("two_labels_agree", "one_label", "labels_disagree", "id_not_in_table", "day_only", "none")


@check("S1_file_links",
       "file_links.csv: one row per file of the six linked investigations; files and bytes per investigation equal "
       "raw_inventory.json and listing_snapshot.json (and the snapshot's sha256 equals the saved listing where it is "
       "present); every link state is one of six; video rows equal pm's video index (state and test), with its "
       "fixtures (PSI-25 244 / 47 / 5, PSI-159 314 / 11 / 2, PSI-39 101 / 5 / 2, PSI-69 3 / 5 / 1, PSI-10 306 with one "
       "label; all videos 662 / 374 / 10 / 1,217 / 330 / 30); a two_labels_agree row of PSI-69 has a NASA identifier "
       "among its labels or a folder validated by its test sheet.")
def check_s1(ctx):
    res = Result()
    if not ctx.has("file_links.csv"):
        raise Skip("file_links.csv not written")
    rows = ctx.table("file_links.csv")
    snap = ctx.json("listing_snapshot.json")["investigations"]
    inv = {x["investigation_id"]: x for x in ctx.json("raw_inventory.json")["investigations"]}
    for i in S_INVS:
        rs = [r for r in rows if r["investigation_id"] == i]
        res.checked += len(rs)
        tot = (len(rs), sum(int(r["bytes"] or 0) for r in rs))
        sn = snap.get(i, {})
        srows = {x[0]: x for x in sn.get("rows", [])}
        if tot != (inv[i]["files"], inv[i]["bytes"]) or tot != (sn.get("files"), sn.get("bytes")) or len(srows) != len(rs):
            res.fail(problem="files or bytes differ from raw_inventory.json or the snapshot", investigation=i, file_links=tot,
                     inventory=(inv[i]["files"], inv[i]["bytes"]))
        for r in rs:
            x = srows.get(r["psi_file_id"])
            if x is None or (x[1], x[2], str(x[3] if x[3] is not None else "")) != (r["file_name"], int(r["bytes"] or 0), r["version"]):
                res.fail(problem="row not as in the snapshot", file_id=r["psi_file_id"])
            if r["link_state"] not in S_STATES:
                res.fail(problem="unknown link state", state=r["link_state"])
            if i == "PSI-69" and r["link_state"] == "two_labels_agree" and not r["source"].startswith("pm video"):
                if not re.search(r"(name_identifier|folder_identifier|identifier_inside_file)=", r["labels_found"]) \
                        and "test sheet" not in r["second_label_scope"]:
                    res.fail(problem="FLEX file linked by FLEX numbers alone", file=r["file_name"])
        lp = os.path.join(LISTINGS, i + ".json")
        if os.path.exists(lp):
            with open(lp, "rb") as f:
                if hashlib.sha256(f.read()).hexdigest() != sn.get("listing_sha256"):
                    res.fail(problem="snapshot sha256 differs from the saved listing", investigation=i)
    path = os.path.join(ROOT, "video", "data", "video_links.csv")
    with open(path, encoding="utf-8", newline="") as f:
        vids = list(csv.DictReader(l for l in f if not l.startswith("#")))
    vby = {v["psi_file_id"]: v for v in vids}
    vrows = [r for r in rows if r["source"].startswith("pm video")]
    for r in vrows:
        v = vby.get(r["psi_file_id"])
        if v is None or (v["link_state"], v["test_id"]) != (r["link_state"], r["test_id"]):
            res.fail(problem="video row differs from pm's index", file_id=r["psi_file_id"])
    if len(vrows) != sum(1 for v in vids if v["investigation"] in S_INVS):
        res.fail(problem="video rows are not all videos of pm's index for the six investigations")
    per = {}
    for v in vids:
        per.setdefault(v["investigation"], collections.Counter())[v["link_state"]] += 1
    for i, (a, b, c) in S_VIDEO_FIXTURE.items():
        got = (per[i]["two_labels_agree"], per[i]["one_label"], per[i]["labels_disagree"])
        if got != (a, b, c):
            res.fail(problem="video fixture not reproduced", investigation=i, recount=got)
    tot = collections.Counter(v["link_state"] for v in vids)
    if dict(tot) != S_VIDEO_TOTALS:
        res.fail(problem="video totals not reproduced", recount=dict(tot))
    res.numbers = {"rows": len(rows), "video_rows": len(vrows),
                   "by_state": dict(collections.Counter(r["link_state"] for r in rows))}
    return res


@check("S2_file_links_lunar",
       "Files whose name carries a label of the 26 tests inside the lunar ranges, recounted from file_links.csv with "
       "own regexes for PSI-69 (identifier or FLEX number in the name) and PSI-159 (identifier in the name): 398 "
       "files, 104,358,456,350 bytes, 316 small files of 86,853,632 bytes; PSI-69 299 files of 24,954,842,492 bytes; "
       "PSI-159 99 files of 79,403,613,858 bytes; by second label 336 / 47 / 15; FLEX-19 17 files, 1,112,400,426 bytes; "
       "identifier 193F001 on the rows of FLEX-70 and FLEX-73; file_links_summary.json and test_files.json agree.")
def check_s2(ctx):
    res = Result()
    if not ctx.has("file_links.csv"):
        raise Skip("file_links.csv not written")
    rows = ctx.table("file_links.csv")
    inside = sorted({m["test_id"] for m in ctx.table("scenario_tests.csv") if m["scenario_id"] == "lunar_habitat"
                     and m["o2_match"] == "in" and m["pressure_match"] == "in"})
    flex = r_flex_table()
    num2id = {c["FLEX Test #"].strip(): c["FLEX Identifier"].strip() for _, c in flex}
    id_rows = {}
    for _, c in flex:
        id_rows.setdefault(c["FLEX Identifier"].strip(), []).append(c["FLEX Test #"].strip())
    lun_num = {t.split("-")[1] for t in inside if t.startswith("FLEX-")}
    lun_id = {num2id[n]: n for n in lun_num}
    cfig = {re.search(r"(\d{5}[A-Z]\d{1,2})$", t).group(1): t for t in inside if t.startswith("CFIG")}
    hit = []
    for r in rows:
        name = re.sub(r"^PSI-\d+_[^_]+_", "", r["file_name"], count=1)
        if r["investigation_id"] == "PSI-69":
            m = re.search(r"FLEX[-_ ]?(\d{3})(?![0-9])", name, re.I)
            n = str(int(m.group(1))) if m else None
            ids = [k for k in lun_id if re.search(r"(?<![A-Za-z0-9])" + re.escape(k) + r"(?![0-9])", name)]
            if (n in lun_num) or ids:
                hit.append(r)
        elif r["investigation_id"] == "PSI-159":
            m = re.search(r"(?<!\d)(\d{5}[A-Z]\d{1,2})(?!\d)", name)
            if m and m.group(1) in cfig:
                hit.append(r)
    big = ("archive", "video")
    got = {"files": len(hit), "bytes": sum(int(r["bytes"]) for r in hit),
           "small_files": sum(1 for r in hit if r["kind"] not in big),
           "small_bytes": sum(int(r["bytes"]) for r in hit if r["kind"] not in big),
           "flex": (sum(1 for r in hit if r["investigation_id"] == "PSI-69"), sum(int(r["bytes"]) for r in hit if r["investigation_id"] == "PSI-69")),
           "cfig": (sum(1 for r in hit if r["investigation_id"] == "PSI-159"), sum(int(r["bytes"]) for r in hit if r["investigation_id"] == "PSI-159")),
           "second_label": tuple(sum(1 for r in hit if r["link_state"] == s) for s in ("two_labels_agree", "one_label", "labels_disagree"))}
    want = {"files": 398, "bytes": 104358456350, "small_files": 316, "small_bytes": 86853632,
            "flex": (299, 24954842492), "cfig": (99, 79403613858), "second_label": (336, 47, 15)}
    if got != want:
        res.fail(problem="lunar link fixture not reproduced", recount=str(got))
    f19 = [r for r in hit if r["investigation_id"] == "PSI-69" and ("FLEX-19" in r["name_names_test"].split("+"))]
    if (len(f19), sum(int(r["bytes"]) for r in f19)) != (17, 1112400426):
        res.fail(problem="FLEX-19 fixture not reproduced", recount=(len(f19), sum(int(r["bytes"]) for r in f19)))
    if sorted(id_rows.get("193F001", []), key=int) != ["70", "73"]:
        res.fail(problem="193F001 not on the rows of FLEX-70 and FLEX-73", rows=id_rows.get("193F001"))
    s = ctx.json("file_links_summary.json")["scenarios"]["lunar_habitat"]
    if (s["files_naming_inside_tests"], s["bytes"], s["small_files"], s["small_bytes"]) != (got["files"], got["bytes"], got["small_files"], got["small_bytes"]):
        res.fail(problem="summary differs from the recount")
    tf = ctx.json("test_files.json")["scenarios"]["lunar_habitat"]
    ids = {x["psi_file_id"] for t in tf.values() for x in t["file_list"]}
    if set(tf) != set(inside) or ids != {r["psi_file_id"] for r in hit}:
        res.fail(problem="test_files.json differs from the recount", tests=len(tf), files=len(ids))
    res.checked = len(rows)
    res.numbers = {"lunar": got}
    return res


@check("S3_video_tie_differences",
       "video_tie_differences.csv: every video of pm's index is compared with the data role's own first name tie "
       "(raw_names.py, the level and tests behind test_files.csv); every row has a known class that follows from its "
       "two sides, its pm side equals pm's index, and the counts equal file_links_summary.json.")
def check_s3(ctx):
    res = Result()
    if not ctx.has("video_tie_differences.csv"):
        raise Skip("video_tie_differences.csv not written")
    rows = ctx.table("video_tie_differences.csv")
    known = {"different_tests", "data_role_day_only", "data_role_not_tied", "data_role_ties_a_test_pm_does_not",
             "pm_day_only_data_role_not_tied", "data_role_day_only_pm_not"}
    path = os.path.join(ROOT, "video", "data", "video_links.csv")
    with open(path, encoding="utf-8", newline="") as f:
        vby = {v["psi_file_id"]: v for v in csv.DictReader(l for l in f if not l.startswith("#"))}
    for r in rows:
        res.checked += 1
        v = vby.get(r["psi_file_id"])
        if r["difference"] not in known or v is None or (v["link_state"], v["test_id"]) != (r["pm_link_state"], r["pm_test_id"]):
            res.fail(problem="difference row not consistent", file_id=r["psi_file_id"])
        pm_test = r["pm_link_state"] in ("two_labels_agree", "one_label", "labels_disagree")
        if ((r["data_role_level"] == "test") and pm_test) != (r["difference"] == "different_tests"):
            res.fail(problem="class does not follow from the two sides", file_id=r["psi_file_id"])
    summ = ctx.json("file_links_summary.json")["video_tie_differences"]
    if summ["rows"] != len(rows) or summ["by_difference"] != dict(sorted(collections.Counter(r["difference"] for r in rows).items())):
        res.fail(problem="summary counts differ")
    res.numbers = {"rows": len(rows), "by_difference": dict(collections.Counter(r["difference"] for r in rows))}
    return res



@check("Q5_gravity_basis",
       "gravity_level: microgravity for 1,824 of 1,824 tests of tests.csv over the 14 tables whose constants set it "
       "(sources.json); each of these tables names its basis, the PSI record field Comment[Flight Platform], with the "
       "value as written: 'International Space Station (ISS)' for 11 of the 12 investigations and 'Cygnus Spacecraft' "
       "for PSI-99 (addendum 01:40 e of pm request 20261115-0035).")
def check_q5(ctx):
    res = Result()
    g = collections.Counter(t["gravity_level"] for t in ctx.tests)
    files = {t["source_file"] for t in ctx.tests}
    srcs = [s for s in ctx.sources if (s.get("constants") or {}).get("gravity_level")]
    vals = {}
    for s in srcs:
        res.checked += 1
        b = s.get("gravity_level_basis") or {}
        if b.get("record_field") != "Comment[Flight Platform]" or not b.get("value_as_written") or not b.get("archive"):
            res.fail(problem="table without a gravity basis", source=s["id"])
        vals[s["investigation_id"]] = b.get("value_as_written")
    want = {i: ("Cygnus Spacecraft" if i == "PSI-99" else "International Space Station (ISS)") for i in vals}
    if dict(g) != {"microgravity": 1824} or len(files) != 14 or len(srcs) != 14 or len(vals) != 12 or vals != want:
        res.fail(problem="gravity fixture not reproduced", gravity=dict(g), tables=len(files), sources=len(srcs), values=vals)
    res.numbers = {"tests": sum(g.values()), "tables": len(files),
                   "flight_platform": dict(collections.Counter(vals.values()))}
    return res



@check("S4_archive_members",
       "archive_members.csv (design step 12): one row per .zip archive whose name carries a label of a FLEX test inside "
       "the lunar ranges (test_files.json): 47 archives, 24,923,186,032 bytes; members parsed equal the count of the "
       "end record in every row; archive bytes equal file_links.csv; FLEX-19: 886 tif, 852 tif and 122 bmp frames.")
def check_s4(ctx):
    res = Result()
    if not ctx.has("archive_members.csv"):
        raise Skip("archive_members.csv not written")
    rows = ctx.table("archive_members.csv")
    tf = ctx.json("test_files.json")["scenarios"]["lunar_habitat"]
    want = {x["psi_file_id"]: (t, x["bytes"]) for t, v in tf.items() if v["investigation_id"] == "PSI-69"
            for x in v["file_list"] if x["file_name"].lower().endswith(".zip")}
    fl = {r["psi_file_id"]: int(r["bytes"]) for r in ctx.table("file_links.csv") if r["investigation_id"] == "PSI-69"}
    for r in rows:
        res.checked += 1
        if r["members_declared"] != r["members_parsed"]:
            res.fail(problem="members parsed differ from the end record", file_id=r["psi_file_id"])
        if want.get(r["psi_file_id"]) != (r["test_id"], int(r["archive_bytes"])) or fl.get(r["psi_file_id"]) != int(r["archive_bytes"]):
            res.fail(problem="archive not as in test_files.json or file_links.csv", file_id=r["psi_file_id"])
    f19 = sorted(re.sub(r"; txt \d+", "", r["members_by_extension"]) for r in rows if r["test_id"] == "FLEX-19")
    if len(rows) != 47 or set(want) != {r["psi_file_id"] for r in rows} or sum(int(r["archive_bytes"]) for r in rows) != 24923186032 \
            or f19 != ["bmp 122", "tif 852", "tif 886"]:
        res.fail(problem="fixture not reproduced", archives=len(rows), flex19=f19)
    res.numbers = {"archives": len(rows), "bytes_fetched": sum(int(r["bytes_fetched"]) for r in rows),
                   "members": sum(int(r["members_parsed"]) for r in rows)}
    return res


# ----------------------------------------------------------------------------
# T. comparison with the catalog (another role's file; differences are NOTES)
# ----------------------------------------------------------------------------

T_CATALOG = os.path.join(ROOT, "data", "catalog", "configurations.csv")
T_STATES = ("equal", "catalog_wider", "catalog_narrower", "overlap_neither_contains", "pipeline_has_no_value",
            "catalog_has_no_value", "both_have_no_value", "not_comparable")
T_DIFF = ("catalog_wider", "catalog_narrower", "overlap_neither_contains", "pipeline_has_no_value",
          "catalog_has_no_value")


def t_num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def t_family(cid, m):
    m = m.lower()
    if cid.startswith("BASS-II"):
        for key, fam in (("sibal", "sibal"), ("nomex", "nomex"), ("rod", "rod")):
            if key in m:
                return fam
        if "spher" in m or "wax" in m or "candle" in m:
            return "other"
        return "film" if ("film" in m or "micron" in m or re.search(r"0\.[1-4] mm", m)) else "slab"
    if "sibal" in m:
        return "sibal"
    if "nomex" in m or "ultem" in m:
        return "sheet"
    for key in ("wax", "candle"):
        if key in m:
            return "wax"
    return "sphere" if "sphere" in m else ("skip" if "soot" in m else "slab")


T_FAMILY = {"BASS-II-C01": "film", "BASS-II-C02": "slab", "BASS-II-C03": "rod", "BASS-II-C04": "sibal",
            "BASS-II-C05": "nomex", "BASS-II-C06": "other", "BASS-C01": "sibal", "BASS-C02": "slab",
            "BASS-C03": "sphere", "BASS-C04": "wax", "BASS-C05": "sheet"}


def t_round(text, places):
    from decimal import Decimal, ROUND_HALF_UP
    return float(Decimal(text).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def t_state(c, p):
    if c == p:
        return "equal"
    if c[0] <= p[0] and p[1] <= c[1]:
        return "catalog_wider"
    if p[0] <= c[0] and c[1] <= p[1]:
        return "catalog_narrower"
    return "overlap_neither_contains"


@check("T1_catalog_comparison",
       "catalog_comparison.csv and its summary reproduce from data/catalog/configurations.csv and tests.csv: the "
       "mapped tests, n, min, max and the states with and without the tolerance per configuration and variable. "
       "Differences between the catalog and the pipeline are reported as a NOTE and never fail the check.")
def check_t1(ctx):
    res = Result()
    if not os.path.exists(T_CATALOG):
        raise Skip("data/catalog/ is absent (another role's folder): nothing to compare")
    if not ctx.has("catalog_comparison.csv"):
        raise Skip("catalog_comparison.csv not written (run pipeline/catalog_compare.py)")
    configs = read_csv(T_CATALOG)
    unit = {s["file"]: s.get("row_unit", "") for s in ctx.sources}
    rows = {(r["config_id"], r["variable"]): r for r in ctx.table("catalog_comparison.csv")}
    seen = 0
    for c in configs:
        ref = c["tests_table_ref"].strip()
        file = ref.split(" (")[0].strip()
        note = ref[len(file):].strip(" ()")
        sub = [t for t in ctx.tests if ref and t["source_file"] == file]
        cid = c["config_id"]
        if cid in T_FAMILY:
            sub = [t for t in sub if t_family(cid, t_raw_cell(file, t["source_row"], 5)) == T_FAMILY[cid]]
        elif note.startswith("Fuel ="):
            sub = [t for t in sub if note.split("=", 1)[1].strip().lower() in t["fuel_material"].lower()]
        elif re.fullmatch(r"S\d", note):
            sub = [t for t in sub if t["test_id"].endswith("-" + note)]
        elif re.match(r"2-\d", note):
            ns = [int(n) for n in re.findall(r"2-(\d)", note)]
            want = set(range(ns[0], ns[-1] + 1)) if " to " in note else set(ns)
            sub = [t for t in sub if int(t["test_id"].rsplit("-", 1)[1]) in want]
        gate = (not ref) or (not sub)
        for var, lo, hi, cols in (("o2_pct", "o2_min_pct", "o2_max_pct", ("o2_pct",)),
                                  ("pressure_kpa", "pressure_min_kpa", "pressure_max_kpa", ("pressure_kpa",)),
                                  ("flow_cms", "flow_min_cms", "flow_max_cms", ("flow_cms", "flow_min_cms")),
                                  ("test_count", None, None, ())):
            r = rows.get((cid, var))
            res.checked += 1
            seen += 1
            if r is None:
                res.fail(problem="row missing", config_id=cid, variable=var)
                continue
            if int(r["mapped_tests"]) != len(sub) or r["table_row_unit"] != (unit.get(file, "") if ref else ""):
                res.fail(problem="mapped tests or row unit differ", config_id=cid, variable=var)
            if var == "test_count":
                cnt = c["test_count_config"].strip()
                if gate and (ref or cnt):
                    want = "not_comparable"
                elif not cnt:
                    want = "both_have_no_value" if not sub else "catalog_has_no_value"
                else:
                    want = ("equal" if float(cnt) == len(sub) else
                            "catalog_wider" if float(cnt) > len(sub) else "catalog_narrower")
                if r["state_exact"] != want or r["state_with_tolerance"] != want:
                    res.fail(problem="test_count state", config_id=cid, want=want, got=r["state_exact"])
                continue
            vals = [(t_num(t[k]), t[k]) for t in sub for k in cols if t_num(t[k]) is not None]
            n = sum(1 for t in sub if any(t_num(t[k]) is not None for k in cols))
            pmin, pmax = (min(vals)[1], max(vals)[1]) if vals else ("", "")
            if (int(r["pipeline_n_recorded"]), r["pipeline_min"], r["pipeline_max"]) != (n, pmin, pmax):
                res.fail(problem="n, min or max differ", config_id=cid, variable=var)
            ls, hs = c[lo].strip(), c[hi].strip()
            basis = sorted({t.get("o2_basis", "") or "(empty)" for t in sub if t_num(t["o2_pct"]) is not None})
            if gate:
                want = ("not_comparable",) * 2
            elif not (ls or hs):
                want = ("both_have_no_value",) * 2 if not vals else ("catalog_has_no_value",) * 2
            elif not vals:
                want = ("pipeline_has_no_value",) * 2
            elif not (ls and hs) or t_num(ls) is None or t_num(hs) is None:
                want = ("not_comparable",) * 2
            elif var == "o2_pct" and basis != [c.get("o2_reference", "").strip() or "(empty)"]:
                want = ("not_comparable",) * 2
            else:
                cat = (float(ls), float(hs))
                want = (t_state(cat, (min(vals)[0], max(vals)[0])),
                        t_state(cat, (t_round(pmin, len(ls.split(".")[1]) if "." in ls else 0),
                                      t_round(pmax, len(hs.split(".")[1]) if "." in hs else 0))))
            if (r["state_exact"], r["state_with_tolerance"]) != want:
                res.fail(problem="state differs", config_id=cid, variable=var, want=list(want),
                         got=[r["state_exact"], r["state_with_tolerance"]])
    if seen != len(rows):
        res.fail(problem="rows in the file that no configuration produces", rows=len(rows), expected=seen)
    summ = ctx.json("catalog_comparison_summary.json")
    for key in ("state_exact", "state_with_tolerance"):
        for var, cnts in summ["counts_by_state"][key].items():
            for st in T_STATES:
                if cnts.get(st, 0) != sum(1 for r in rows.values() if r["variable"] == var and r[key] == st):
                    res.fail(problem="summary count differs", key=key, variable=var, state=st)
        nd = sum(1 for r in rows.values() if r[key] in T_DIFF)
        if summ["differences"][key] != nd or len(summ["difference_list"][key]) != nd:
            res.fail(problem="difference count differs", key=key)
    ex, tol = summ["differences"]["state_exact"], summ["differences"]["state_with_tolerance"]
    res.numbers = {"configurations": len(configs), "rows": len(rows), "differences_exact": ex,
                   "differences_with_tolerance": tol}
    res.note = ("%d configuration-variable rows differ between the catalog and the pipeline (%d with the "
                "tolerance of rounding to the catalog's printed digits); information for the catalog role, "
                "not a failure (catalog_comparison_summary.json)" % (ex, tol))
    return res


@check("T2_process_steps",
       "process_steps.json and the 'process' field of every evidence-package need block and answer file: every item id "
       "of spec/process.json exists in references.json with a quote; every measure's text equals its item's quote and "
       "its item text (no team-written measure text); item types are in references.json _meta.item_types; quotes of "
       "items added for the process are at most 40 words; each need's steps exist; the field of each need equals the "
       "steps and measures of spec/process.json.")
def check_t2(ctx):
    res = Result()
    if not ctx.has("process_steps.json"):
        raise Skip("process_steps.json not written (run pipeline/process_steps.py)")
    refs = ctx.spec("references")
    accepted = set(refs["_meta"]["item_types"])
    items = {}
    for doc in refs["references"]:
        for it in doc["items"]:
            items[it["id"]] = (doc, it)
            if it["type"] not in accepted:
                res.fail(problem="item type not in _meta.item_types", item_id=it["id"], type=it["type"])
    spec = ctx.spec("process")
    out = ctx.json("process_steps.json")
    needs = {n["id"]: n for n in ctx.needs}
    step_ids = [s["id"] for s in spec["steps"]]

    def view_ok(v, iid, where):
        res.checked += 1
        if iid not in items:
            res.fail(problem="item id not in references.json", item_id=iid, where=where)
            return
        doc, it = items[iid]
        q = it.get("quote", "")
        if not q or v.get("quote") != q or v.get("item_id") != iid or v.get("document_id") != doc["id"] \
                or v.get("where") != it["where"] or v.get("url") != doc.get("url", "") or v.get("access") != doc.get("access", ""):
            res.fail(problem="item view differs from references.json", item_id=iid, where=where)
        if len(q.split()) > 40:
            res.fail(problem="quote longer than 40 words", item_id=iid)

    if [s["id"] for s in out["steps"]] != step_ids:
        res.fail(problem="steps differ from spec/process.json")
    for s_spec, s_out in zip(spec["steps"], out["steps"]):
        if [v["item_id"] for v in s_out["items"]] != s_spec["items"] or \
                [v["item_id"] for v in s_out["measures"]] != s_spec["measures"]:
            res.fail(problem="items or measures of a step differ", step=s_spec["id"])
        for v in s_out["items"] + s_out["measures"]:
            view_ok(v, v.get("item_id"), s_spec["id"])
        for v in s_out["measures"]:
            it = items.get(v["item_id"], (None, {}))[1]
            if it.get("text") != it.get("quote"):
                res.fail(problem="measure text is not the NASA quote", item_id=v["item_id"])
        want = [n for n in needs if s_spec["id"] in needs[n].get("informs_process_steps", {}).get("steps", [])]
        if s_out["needs_informing"] != want:
            res.fail(problem="needs informing a step differ", step=s_spec["id"])
    for blk in ("capability_areas", "where_the_weight_lies"):
        if [v["item_id"] for v in out[blk]["items"]] != spec[blk]["items"]:
            res.fail(problem="block items differ", block=blk)
        for v in out[blk]["items"]:
            view_ok(v, v["item_id"], blk)
    if out["sentence"] != spec["_meta"]["fixed_sentence"]:
        res.fail(problem="fixed sentence differs")
    for nid, n in needs.items():
        f = n.get("informs_process_steps")
        if not f or not f.get("steps") or set(f["steps"]) - set(step_ids) \
                or not f.get("team_reading", "").startswith("Team's reading"):
            res.fail(problem="informs_process_steps missing, unknown step or not marked as the team's reading", need_id=nid)
    by_step = {s["id"]: s for s in out["steps"]}

    def field_ok(fld, nid, where):
        res.checked += 1
        steps = needs[nid]["informs_process_steps"]["steps"]
        want_m = [(m["item_id"], sid) for sid in step_ids if sid in steps for m in by_step[sid]["measures"]]
        if fld is None or [x["id"] for x in fld["steps_informed"]] != [s for s in step_ids if s in steps] \
                or [(m["item_id"], m["step_id"]) for m in fld["measures"]] != want_m \
                or fld["sentence"] != spec["_meta"]["fixed_sentence"] \
                or fld["team_reading"] != needs[nid]["informs_process_steps"]["team_reading"]:
            res.fail(problem="process field differs", need_id=nid, where=where)
            return
        for m in fld["measures"]:
            view_ok(m, m["item_id"], where)
    packs = answers = 0
    for e in ctx.json("evidence/index.json")["packages"]:
        pack = ctx.json("evidence/" + e["file"])
        packs += 1
        for b in pack["needs"]:
            field_ok(b.get("process"), b["need_id"], e["file"])
    for name in sorted(os.listdir(ctx.out_path("answers"))):
        if name == "index.json" or not name.endswith(".json"):
            continue
        a = ctx.json("answers/" + name)
        answers += 1
        field_ok(a.get("process"), name.rsplit("__", 1)[1][:-5], name)
    res.numbers = {"steps": len(out["steps"]), "measures": sum(len(s["measures"]) for s in out["steps"]),
                   "packages": packs, "answer_files": answers, "item_views": res.checked}
    return res


@check("T3_need_recorded_summary",
       "need_recorded_summary.csv recounted from tests.csv, need_tests.csv, file_links.csv and needs.json: tests in "
       "scope, of investigations with a 'supported' stated_by link, with an outcome in a table cell (per variable), "
       "counted (objective_link stated) and with a video tied by two labels.")
def check_t3(ctx):
    res = Result()
    if not ctx.has("need_recorded_summary.csv"):
        raise Skip("need_recorded_summary.csv not written")
    rows = {r["need_id"]: r for r in ctx.table("need_recorded_summary.csv")}
    counted = collections.defaultdict(set)
    for r in ctx.table("need_tests.csv"):
        if r["objective_link"] == "stated":
            counted[r["need_id"]].add(r["test_id"])
    video = {r["test_id"] for r in ctx.table("file_links.csv")
             if r["kind"] == "video" and r["link_state"] == "two_labels_agree" and r["test_id"]}
    for n in ctx.needs:
        res.checked += 1
        r = rows.get(n["id"])
        scope = [t for t in ctx.tests if all(t.get(k) in v for k, v in n.get("scope", {}).items())]
        sup = {s["investigation_id"] for s in n.get("stated_by", []) if s.get("verdict") == "supported"}
        linked = [t for t in scope if t["investigation_id"] in sup]
        wo = sum(1 for t in linked if any(t[o] != "" for o in n["outcomes_any"]))
        per = "; ".join("%s %d" % (o, sum(1 for t in linked if t[o] != "")) for o in n["outcomes_any"])
        ids = {t["test_id"] for t in linked}
        want = (len(scope), len(linked), wo, per, len(counted[n["id"]]), len(ids & video), len(counted[n["id"]] & video))
        got = None if r is None else (int(r["tests_in_scope"]), int(r["tests_in_scope_of_supported_investigations"]),
                                      int(r["with_outcome_in_table_cell"]), r["outcome_cells_by_variable"],
                                      int(r["counted_tests"]), int(r["in_scope_supported_with_video_two_labels"]),
                                      int(r["counted_with_video_two_labels"]))
        if got != want:
            res.fail(problem="recount differs", need_id=n["id"], want=list(want), got=list(got) if got else None)
        elif not r["sentence"].startswith("%d tests in the scope" % len(linked)):
            res.fail(problem="sentence does not carry the count", need_id=n["id"])
    res.numbers = {n: "%s/%s/%s" % (r["tests_in_scope_of_supported_investigations"], r["with_outcome_in_table_cell"],
                                    r["counted_tests"]) for n, r in rows.items()}
    return res


def t_raw_cell(file, source_row, col):
    """Cell <col> of the raw table row that starts on line <source_row> (header = line 1)."""
    cache = T_RAW_LINES.setdefault(file, None)
    if cache is None:
        data = read_bytes(os.path.join(RAW, file))
        for enc in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                text = data.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        rd = csv.reader(io.StringIO(text))
        next(rd)
        cache, start = {}, rd.line_num + 1
        for row in rd:
            cache[start] = row
            start = rd.line_num + 1
        T_RAW_LINES[file] = cache
    row = cache.get(int(source_row)) if str(source_row).isdigit() else None
    return row[col] if row and len(row) > col else ""


T_RAW_LINES = {}


# ----------------------------------------------------------------------------
# running
# ----------------------------------------------------------------------------

def compact(numbers):
    parts = []
    for k, v in numbers.items():
        if isinstance(v, dict):
            v = "{" + ",".join("%s:%s" % kv for kv in v.items()) + "}"
        parts.append("%s=%s" % (k, v))
    return " ".join(parts)


def run_checks(ctx):
    report = []
    order = lambda c: (c[0][0], int(re.match(r"[A-Z](\d+)", c[0]).group(1)))
    for cid, verifies, fn in sorted(CHECKS, key=order):
        entry = {"id": cid, "verifies": verifies}
        try:
            res = fn(ctx)
            entry["status"] = "FAIL" if res.failures else "PASS"
            entry["numbers"] = res.numbers
            entry["failures"] = len(res.failures)
            entry["failing_examples"] = res.failures[:MAX_EXAMPLES]
            if res.details:
                entry["details"] = res.details
            if getattr(res, "note", None):
                entry["note"] = res.note
        except Skip as exc:
            entry.update(status="SKIP", numbers={}, failures=0, failing_examples=[], reason=str(exc))
        except Exception as exc:        # a check that cannot run is a failed check
            entry.update(status="FAIL", numbers={}, failures=1,
                         failing_examples=[{"problem": "check could not run: %s: %s" % (type(exc).__name__, exc)}])
        report.append(entry)
        line = "%-4s %-34s" % (entry["status"], cid)
        if entry["status"] == "SKIP":
            line += " " + entry["reason"]
        else:
            line += " failures=%d %s" % (entry["failures"], compact(entry["numbers"]))
            if entry.get("note"):
                line += "\n     NOTE " + entry["note"]
        print(line)
    return report


def main():
    ap = argparse.ArgumentParser(description="Independent validation of the pipeline outputs.")
    ap.add_argument("--data", default=os.path.join(ROOT, "data", "pipeline"),
                    help="directory with the pipeline outputs (default: data/pipeline)")
    ap.add_argument("--spot-check", action="store_true", help="also write reports/spot_check.csv")
    ap.add_argument("--spot-out", default=os.path.join(ROOT, "reports", "spot_check.csv"))
    args = ap.parse_args()
    ctx = Ctx(os.path.abspath(args.data))
    report = run_checks(ctx)
    counts = {s: sum(1 for e in report if e["status"] == s) for s in ("PASS", "FAIL", "SKIP")}
    doc = {
        "_meta": {
            "generated_by": "AI-generated (Claude Code), 2026-11-14. Not human-reviewed.",
            "written_by": "pipeline/check.py",
            "note": "Independent recomputation of the pipeline outputs from the raw NASA PSI tables and the "
                    "rules written in pipeline/spec/*.json and pipeline/README.md. check.py does not import the "
                    "pipeline code. A check that fails names a disagreement; it does not say which side is right.",
            "tolerances": {"converted_values": ROUND_TOL, "derived_formulas": DERIVED_TOL, "indicator_statistics": STAT_TOL},
        },
        "summary": dict(counts, checks=len(report)),
        "notes": [{"id": e["id"], "note": e["note"]} for e in report if e.get("note")],
        "checks": report,
    }
    out = os.path.join(ctx.data_dir, "validation_report.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("%d checks: %d PASS, %d FAIL, %d SKIP -> %s" % (len(report), counts["PASS"], counts["FAIL"], counts["SKIP"],
                                                        os.path.relpath(out, ROOT)))
    if args.spot_check:
        n = write_spot_check(ctx, args.spot_out)
        print("spot-check sheet: %d rows -> %s" % (n, os.path.relpath(args.spot_out, ROOT)))
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
