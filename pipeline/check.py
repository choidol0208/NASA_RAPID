# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Independent validator of the pipeline outputs.

It does not import run.py, rules.py, evidence.py or facts.py. Every check
recomputes its result from the raw NASA PSI tables and from the rules as they
are written in pipeline/spec/*.json ('_meta' blocks) and pipeline/README.md,
then compares with the files in data/pipeline/.

    python3 pipeline/check.py                 all checks, writes validation_report.json
    python3 pipeline/check.py --data DIR      check another copy of data/pipeline/
    python3 pipeline/check.py --spot-check    also writes reports/spot_check.csv

Exit code 1 when a check fails. The report carries no timestamp.
"""
import argparse
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
    "declared_exception_without_flag": "a value of a kind that README declares as 'not literally in a NASA cell' "
                                       "(oxygen midpoint, material from the BASS-II ReadMe, cell of the row "
                                       "above) but the test does not carry the flag README names for it",
    "spec_rule_gives_other_value": "the rule written in the spec for this column (sources.json "
                                   "'_meta.sample_keywords') leads from the cell to a different value, or to none",
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
    "declared_exception_flagged": "a value that is not literally in the cell, of a kind README declares (table "
                                  "'Values that are not literally in a NASA cell'): it is exactly what the "
                                  "declared rule gives and the test carries the named flag",
}
# kind of declared exception -> flag suffix that the test must carry on the variable
EXCEPTION_FLAGS = {
    "oxygen_midpoint": "range_in_source_midpoint_used",
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
                    elif item["cls"] == "computed_midpoint" and r["variable"] == "o2_pct" and \
                            len(number_tokens(item["cell"])) == 2:
                        kind = "oxygen_midpoint"      # README: midpoint of an oxygen range written in the cell
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
    for (test_id, var), rows in idx.items():
        if test_id not in ctx.tests_by_id or var not in known:
            res.fail(problem="values_long row without a test or a tests.csv column", test_id=test_id, variable=var)
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


# ----------------------------------------------------------------------------
# D. needs
# ----------------------------------------------------------------------------

def in_scope(test, need):
    return all(test.get(k, "") in allowed for k, allowed in (need.get("scope") or {}).items())


def has_required(test, need):
    return all(test.get(v, "") != "" for v in need["conditions_required"])


def has_outcome(test, need):
    return any(test.get(v, "") != "" for v in need["outcomes_any"])


def stated_investigations(need):
    return {s["investigation_id"] for s in need.get("stated_by", [])}


def need_links(ctx):
    """Recomputed need_tests: {need_id: {test_id: objective_link}} for in-scope tests that record every
    required condition and at least one outcome."""
    def load():
        out = {}
        for need in ctx.needs:
            stated = stated_investigations(need)
            out[need["id"]] = {
                t["test_id"]: ("stated" if t["investigation_id"] in stated else "not_stated")
                for t in ctx.tests if in_scope(t, need) and has_required(t, need) and has_outcome(t, need)}
        return out
    return ctx._get("need_links", load)


def usable_ids(ctx, need_id):
    return [tid for tid, link in need_links(ctx)[need_id].items() if link == "stated"]


@check("D1_need_tests",
       "need_tests.csv lists exactly the in-scope tests that record every required condition and at least "
       "one outcome of each need, with objective_link 'stated' only when the investigation is in 'stated_by'.")
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
       "conditions, with an outcome, usable), status and objective_link equal the recomputation from "
       "tests.csv and needs.json.")
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
                           tests_with_outcome=0, usable_tests=0, required_missing=[], outcomes_present=[])
            else:
                scope = [t for t in by_source.get(s["id"], []) if in_scope(t, need)]
                missing = [v for v in need["conditions_required"] if not any(t.get(v, "") != "" for t in scope)]
                present = [v for v in need["outcomes_any"] if any(t.get(v, "") != "" for t in scope)]
                if not scope:
                    status, missing = "out_of_scope", []
                elif present and not missing:
                    status = "measured"
                elif present:
                    status = "partial"
                elif not missing:
                    status = "conditions_only"
                else:
                    status = "none"
                exp.update(status=status, tests=len(scope),
                           tests_with_required_conditions=sum(1 for t in scope if has_required(t, need)),
                           tests_with_outcome=sum(1 for t in scope if has_outcome(t, need)),
                           usable_tests=sum(1 for t in scope if has_required(t, need) and has_outcome(t, need)),
                           required_missing=missing, outcomes_present=present)
            for col, want in exp.items():
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
                mine = [x["quote"] for x in need["stated_by"] if x["investigation_id"] == s["investigation_id"]]
                if q not in mine and not all(x in q for x in mine):
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
       "Every 'stated_by' quote of needs.json is literally in the named field of the investigation's PSI "
       "record (HTML tags removed, whitespace collapsed).")
def check_d3(ctx):
    res = Result()
    for need in ctx.needs:
        for s in need.get("stated_by", []):
            res.checked += 1
            key = {"need_id": need["id"], "investigation_id": s["investigation_id"], "field": s["field"]}
            path = os.path.join(CATALOG, s["investigation_id"] + ".json")
            if not os.path.exists(path):
                res.fail(problem="no PSI record", **key)
                continue
            field = ctx.record(s["investigation_id"]).get(s["field"])
            if not isinstance(field, str):
                res.fail(problem="field missing in the record", **key)
            elif clean_text(s["quote"]) not in clean_text(field):
                res.fail(problem="quote not in the record field", quote=s["quote"][:160], **key)
    res.numbers = {"quotes": res.checked}
    return res


@check("D4_objective_links",
       "objective_links.csv has exactly the (need, investigation, field, quote) entries of needs.json 'stated_by'.")
def check_d4(ctx):
    res = Result()
    expected = [(n["id"], s["investigation_id"], s["field"], s["quote"]) for n in ctx.needs for s in n.get("stated_by", [])]
    have = [(r["need_id"], r["investigation_id"], r["record_field"], r["quote"]) for r in ctx.table("objective_links.csv")]
    res.checked = len(expected)
    for k in sorted(set(expected) - set(have)):
        res.fail(problem="in needs.json, not in the file", need_id=k[0], investigation_id=k[1], quote=k[3][:100])
    for k in sorted(set(have) - set(expected)):
        res.fail(problem="in the file, not in needs.json", need_id=k[0], investigation_id=k[1], quote=k[3][:100])
    if len(have) != len(set(have)):
        res.fail(problem="duplicate rows in the file")
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
                texts = [clean_text(item[1].get(k, "")) for k in ("quote", "text")] if item else []
                if not any(clean_text(e.get("quote", "")) in t for t in texts if t):
                    res.fail(problem="quote not in the references.json item", reference_item=e["reference_item"], **key)
            else:
                problem = quote_in_record(ctx, s["investigation_id"], e.get("record_field"), e.get("quote", ""))
                if problem:
                    res.fail(problem=problem, field=e.get("record_field"), quote=e.get("quote", "")[:120], **key)
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
                if in_scope(t, need) and has_required(t, need) and t["investigation_id"] in stated]
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
       "or atmosphere_cells.csv, and index.json carries the same status.")
def check_i2(ctx):
    res = Result()
    index = {p.get("id"): p for p in evidence_index(ctx).get("packages", [])}
    rows = csv_rows_for_envs(ctx)
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
        if ((index.get(env["id"]) or {}).get("status_by_need") or {}).get(need["id"]) != row["status"]:
            res.fail(field="index.status_by_need", csv=row["status"], **key)
    res.numbers = {"need_blocks": res.checked}
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
       "objective sentences equal objective_links.csv, the investigations list equals the usable tests per "
       "investigation and tier with the title of the PSI record, references equal the need's items in "
       "references.json, and every gap code has a sentence.")
def check_i5(ctx):
    res = Result()
    links = {}
    for r in ctx.table("objective_links.csv"):
        links.setdefault(r["need_id"], []).append(
            {"investigation_id": r["investigation_id"], "record_field": r["record_field"], "quote": r["quote"]})
    for env, need, b in need_blocks(ctx):
        res.checked += 1
        marks = env_marks(ctx, env)
        key = {"package": env["id"], "need_id": need["id"]}
        if b.get("objective") != links.get(need["id"], []):
            res.fail(field="objective", problem="differs from objective_links.csv", **key)
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
       "tests.csv (whatever the need) have tier atmosphere, oxygen_only or pressure_only in that environment.")
def check_i10(ctx):
    res = Result()
    seen = False
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
    if not seen:
        raise Skip("no package carries environment.recorded_tests")
    res.numbers = {"packages": res.checked}
    res.details = {"note": "No rule text describes this field; the rule checked here is the validator's reading of its name."}
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
       "indicator sentence: of its indicator entry), or one of the two sums that statements.json declares.")
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


def copied_spec_texts(ctx):
    texts = [n["name"] for n in ctx.needs]
    texts += [i.get("reading", "") for i in ctx.spec("indicators")["indicators"]]
    return texts


@check("I9_evidence_statement_words",
       "No statement of an evidence package contains the words safe, unsafe, flammable, sufficient, "
       "representative, proves or confirms (outside a need name or an indicator reading copied from the spec).")
def check_i9(ctx):
    res = Result()
    spec_texts = copied_spec_texts(ctx)
    for env, need, b in need_blocks(ctx):
        for s in b.get("statements", []) + [{"id": "gap:" + str(g.get("code")), "text": g.get("text")} for g in b.get("gaps", [])]:
            res.checked += 1
            words = forbidden_in(s.get("text") or "", spec_texts)
            if words:
                res.fail(package=env["id"], need_id=need["id"], statement=s.get("id"), words=words,
                         text=(s.get("text") or "")[:200])
    res.numbers = {"sentences": res.checked}
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
       "stated_needs of every investigation equal objective_links.csv, and capability equals the rows of "
       "capability_matrix.csv (status, counts, objective_link per need and table).")
def check_j3(ctx):
    res = Result()
    links = {}
    for r in ctx.table("objective_links.csv"):
        links.setdefault(r["investigation_id"], []).append((r["need_id"], r["record_field"], r["quote"]))
    matrix = {}
    for r in ctx.table("capability_matrix.csv"):
        matrix.setdefault(r["investigation_id"], {}).setdefault(r["need_id"], {})[r["source_id"]] = r
    names = {n["id"]: n["name"] for n in ctx.needs}
    for e in facts(ctx):
        inv = e.get("investigation_id")
        key = {"investigation_id": inv}
        res.checked += 1
        got = [(s.get("need_id"), s.get("record_field"), s.get("quote")) for s in e.get("stated_needs", [])]
        if sorted(got) != sorted(links.get(inv, [])):
            res.fail(field="stated_needs", in_file=len(got), objective_links_csv=len(links.get(inv, [])), **key)
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
            words = forbidden_in(s.get("text") or "", spec_texts + quotes)
            if words:
                res.fail(problem="forbidden word", words=words, text=(s.get("text") or "")[:200], **key)
    res.numbers = {"numbers_in_statements": res.checked, "statements": sentences,
                   "numbers_found_only_elsewhere_in_the_entry": wider}
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
