# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-15).
"""Compare the catalog's configurations with the pipeline's tests.

The catalog (data/catalog/configurations.csv, written by scripts/build_catalog.py,
catalog role) and the pipeline (data/pipeline/tests.csv, written by
pipeline/run.py, data role) are built separately from the same PSI tables.
This script compares, for every catalog configuration (41), the oxygen,
pressure and flow range and the test count with the tests of tests.csv that
the configuration maps to. It changes nothing in data/catalog/.

Run after run.py (python3 pipeline/catalog_compare.py). Reads
data/catalog/configurations.csv, data/pipeline/tests.csv, the raw tables of
PSI-25 and PSI-26 (data/psi/experimental_tables/, for the BASS families) and
pipeline/spec/sources.json (row unit of a table). Writes, in data/pipeline/:

  catalog_comparison.csv          configuration x variable (o2_pct,
                                  pressure_kpa, flow_cms, test_count)
  catalog_comparison_summary.json counts by state and variable, with and
                                  without the tolerance, fixed sentences and
                                  the list of differences

When data/catalog/ is absent it writes nothing and says so.

Mapping rule (the one of web/check_integration.py, config_subset, re-written
here so that this file does not depend on another role's code): the tests of
tests.csv whose source_file is the file named in tests_table_ref, then the
filter in parentheses: BASS families by the material cell (column 6) of the
raw row with the grouping of scripts/build_catalog.py; 'Fuel = X' by
fuel_material containing X; 'S1' by a test id ending '-S1'; '2-1 to 2-4' and
'2-5, 2-6' by the number after the last hyphen of the test id. Values: oxygen
o2_pct, pressure pressure_kpa, flow flow_cms and flow_min_cms (both, as in
check_integration.py).

States (exact comparison and with the tolerance):
  equal, catalog_wider, catalog_narrower, overlap_neither_contains,
  pipeline_has_no_value, catalog_has_no_value, both_have_no_value,
  not_comparable (with a reason).
Tolerance: the pipeline's min and max rounded half-up to the number of
decimals the catalog prints for that bound.
"""
import csv
import io
import json
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CATALOG_DIR = os.path.join(ROOT, "data", "catalog")
CONFIGS = os.path.join(CATALOG_DIR, "configurations.csv")
OUT = os.path.join(ROOT, "data", "pipeline")
RAW = os.path.join(ROOT, "data", "psi", "experimental_tables")

GENERATED_BY = "AI-generated (Claude Code), 2026-11-15. Not human-reviewed."
STATES = ("equal", "catalog_wider", "catalog_narrower", "overlap_neither_contains", "pipeline_has_no_value",
          "catalog_has_no_value", "both_have_no_value", "not_comparable")
DIFFERENCE_STATES = ("catalog_wider", "catalog_narrower", "overlap_neither_contains", "pipeline_has_no_value",
                     "catalog_has_no_value")
VARIABLES = (
    ("o2_pct", "o2_min_pct", "o2_max_pct", "o2_source", ("o2_pct",)),
    ("pressure_kpa", "pressure_min_kpa", "pressure_max_kpa", "pressure_source", ("pressure_kpa",)),
    ("flow_cms", "flow_min_cms", "flow_max_cms", "flow_source", ("flow_cms", "flow_min_cms")),
)
TOLERANCE = "pipeline min and max rounded half-up to the number of decimals the catalog prints for that bound"
MAPPING_RULE = ("tests of tests.csv whose source_file is the file named in tests_table_ref, filtered by the note in "
                "parentheses as in web/check_integration.py config_subset (BASS families by the raw material cell; "
                "'Fuel = X' by fuel_material; 'S<n>' by test id suffix; '2-<n>' by test number)")
COLUMNS = ("config_id", "investigation_id", "psi_accession", "variable", "catalog_min_as_written",
           "catalog_max_as_written", "catalog_source_label_column", "catalog_source_label", "catalog_o2_reference",
           "tests_table_ref", "table_row_unit", "mapping_note", "mapped_tests", "pipeline_columns",
           "pipeline_n_recorded", "pipeline_min", "pipeline_max", "pipeline_o2_basis", "state_exact",
           "state_with_tolerance", "tolerance", "reason")
SENTENCES = [
    "The catalog and the pipeline are built separately from the same PSI tables; this file compares them.",
    "A difference is information for the catalog role, not an error of either file.",
    "States are computed by the rules written in pipeline/catalog_compare.py; the team checked no state by hand.",
]

FAMILY = {"BASS-II-C01": "film", "BASS-II-C02": "slab", "BASS-II-C03": "rod", "BASS-II-C04": "sibal",
          "BASS-II-C05": "nomex", "BASS-II-C06": "other", "BASS-C01": "sibal", "BASS-C02": "slab",
          "BASS-C03": "sphere", "BASS-C04": "wax", "BASS-C05": "sheet"}


def bass2_family(m):
    m = m.lower()
    if "sibal" in m: return "sibal"
    if "nomex" in m: return "nomex"
    if "rod" in m: return "rod"
    if "spher" in m or "wax" in m or "candle" in m: return "other"
    if "film" in m or "micron" in m or re.search(r"0\.[1-4] mm", m): return "film"
    return "slab"


def bass_family(m):
    m = m.lower()
    if "sibal" in m: return "sibal"
    if "nomex" in m or "ultem" in m: return "sheet"
    if "wax" in m or "candle" in m: return "wax"
    if "sphere" in m: return "sphere"
    if "soot" in m: return "skip"
    return "slab"


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def raw_rows_by_line(file):
    data = open(os.path.join(RAW, file), "rb").read()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    rd = csv.reader(io.StringIO(text))
    next(rd)
    out, start = {}, rd.line_num + 1
    for row in rd:
        out[start] = row
        start = rd.line_num + 1
    return out


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def decimals(s):
    s = (s or "").strip()
    return len(s.split(".", 1)[1]) if "." in s else 0


def rounded(value_text, places):
    q = Decimal(1).scaleb(-places)
    return float(Decimal(value_text).quantize(q, rounding=ROUND_HALF_UP))


def subset(c, tests, raw_cache):
    ref = c["tests_table_ref"] or ""
    file = ref.split(" (")[0].strip()
    note = ref[len(file):].strip(" ()")
    ts = [t for t in tests if t["source_file"] == file]
    cid = c["config_id"]
    if cid in FAMILY:
        raw = raw_cache.setdefault(file, raw_rows_by_line(file))
        fam = bass2_family if cid.startswith("BASS-II") else bass_family
        ts = [t for t in ts if t["source_row"].isdigit()
              and fam((raw.get(int(t["source_row"])) or [""] * 6)[5]) == FAMILY[cid]]
    elif note.startswith("Fuel ="):
        fuel = note.split("=", 1)[1].strip().lower()
        ts = [t for t in ts if fuel in t["fuel_material"].lower()]
    elif re.fullmatch(r"S\d", note):
        ts = [t for t in ts if t["test_id"].endswith("-" + note)]
    elif re.match(r"2-\d", note):
        nums = [int(n) for n in re.findall(r"2-(\d)", note)]
        want = set(range(nums[0], nums[-1] + 1)) if " to " in note else set(nums)
        ts = [t for t in ts if int(t["test_id"].rsplit("-", 1)[1]) in want]
    return file, note, ts


def range_state(c_lo, c_hi, p_lo, p_hi):
    if c_lo == p_lo and c_hi == p_hi:
        return "equal"
    if c_lo <= p_lo and p_hi <= c_hi:
        return "catalog_wider"
    if p_lo <= c_lo and c_hi <= p_hi:
        return "catalog_narrower"
    return "overlap_neither_contains"


def compare_range(c, var, lo_col, hi_col, cols, sub, gate):
    lo_s, hi_s = c[lo_col].strip(), c[hi_col].strip()
    cells = [(num(t[k]), t[k]) for t in sub for k in cols if num(t[k]) is not None]
    n = sum(1 for t in sub if any(num(t[k]) is not None for k in cols))
    p_min = min(cells)[1] if cells else ""
    p_max = max(cells)[1] if cells else ""
    basis = sorted({t.get("o2_basis", "") for t in sub if num(t["o2_pct"]) is not None}) if var == "o2_pct" else []
    row = {"pipeline_n_recorded": n, "pipeline_min": p_min, "pipeline_max": p_max,
           "pipeline_o2_basis": "; ".join(b or "(empty)" for b in basis)}
    if gate:
        return row, "not_comparable", "not_comparable", gate
    has_cat = bool(lo_s or hi_s)
    has_pipe = bool(cells)
    if not has_cat and not has_pipe:
        return row, "both_have_no_value", "both_have_no_value", ""
    if not has_cat:
        return row, "catalog_has_no_value", "catalog_has_no_value", ""
    if not has_pipe:
        return row, "pipeline_has_no_value", "pipeline_has_no_value", ""
    if not (lo_s and hi_s) or num(lo_s) is None or num(hi_s) is None:
        r = "the catalog gives one bound only" if not (lo_s and hi_s) else "a catalog bound is not a number"
        return row, "not_comparable", "not_comparable", r
    if var == "o2_pct":
        ref = c.get("o2_reference", "").strip() or "(empty)"
        if basis != [ref]:
            return row, "not_comparable", "not_comparable", (
                "the catalog's oxygen refers to '%s' and the pipeline's o2_basis of the mapped tests is '%s'"
                % (ref, row["pipeline_o2_basis"]))
    c_lo, c_hi = float(lo_s), float(hi_s)
    exact = range_state(c_lo, c_hi, min(cells)[0], max(cells)[0])
    tol = range_state(c_lo, c_hi, rounded(p_min, decimals(lo_s)), rounded(p_max, decimals(hi_s)))
    reason = ""
    if max(cells)[0] < c_lo or min(cells)[0] > c_hi:
        reason = "the two ranges do not overlap"
    ranged = sorted({t["test_id"] for t in sub for k in cols if (k + ":range_in_source") in t["flags"]})
    if ranged and exact != "equal":
        reason = (reason + "; " if reason else "") + (
            "the table cell of %s is a range (tests.csv flag %s:range_in_source_*); the pipeline keeps one value"
            % (", ".join(ranged), cols[0]))
    return row, exact, tol, reason


def build(configs, tests, row_unit):
    raw_cache, rows = {}, []
    for c in configs:
        ref = (c["tests_table_ref"] or "").strip()
        file, note, sub = subset(c, tests, raw_cache) if ref else ("", "", [])
        unit = row_unit.get(file, "") if file else ""
        if not ref:
            gate = "the configuration names no experimental table (tests_table_ref is empty)"
        elif not sub and unit and unit != "test":
            gate = "the configuration's table has row unit '%s' in spec/sources.json; tests.csv holds no row of it" % unit
        elif not sub:
            gate = "no test of tests.csv maps to the configuration"
        else:
            gate = ""
        base = {"config_id": c["config_id"], "investigation_id": c["investigation_id"],
                "psi_accession": c["psi_accession"], "catalog_o2_reference": c.get("o2_reference", ""),
                "tests_table_ref": ref, "table_row_unit": unit, "mapping_note": note, "mapped_tests": len(sub),
                "tolerance": ""}
        for var, lo_col, hi_col, src_col, cols in VARIABLES:
            row, exact, tol, reason = compare_range(c, var, lo_col, hi_col, cols, sub, gate)
            if not gate and c[src_col].strip() == "test_matrix" and exact != "both_have_no_value":
                reason = (reason + "; " if reason else "") + "the catalog's source label is 'test_matrix'"
            if c[src_col].strip() == "team" and exact != "both_have_no_value":
                reason = (reason + "; " if reason else "") + "the catalog's source label is 'team'"
            rows.append(dict(base, variable=var, catalog_min_as_written=c[lo_col], catalog_max_as_written=c[hi_col],
                             catalog_source_label_column=src_col, catalog_source_label=c[src_col],
                             pipeline_columns="; ".join(cols), state_exact=exact, state_with_tolerance=tol,
                             tolerance=TOLERANCE if tol != exact else "", reason=reason, **row))
        cnt = c["test_count_config"].strip()
        if gate and not (not ref and not cnt):
            st, reason = "not_comparable", gate
        elif not cnt and not sub:
            st, reason = "both_have_no_value", gate
        elif not cnt:
            st, reason = "catalog_has_no_value", ""
        else:
            n_cat = num(cnt)
            st = "equal" if n_cat == len(sub) else ("catalog_wider" if n_cat > len(sub) else "catalog_narrower")
            reason = "catalog count larger than the mapped tests" if st == "catalog_wider" else (
                "catalog count smaller than the mapped tests" if st == "catalog_narrower" else "")
        rows.append(dict(base, variable="test_count", catalog_min_as_written=cnt, catalog_max_as_written=cnt,
                         catalog_source_label_column="test_count_config", catalog_source_label="",
                         pipeline_columns="test_id", pipeline_n_recorded=len(sub), pipeline_min="", pipeline_max="",
                         pipeline_o2_basis="", state_exact=st, state_with_tolerance=st, reason=reason))
    return rows


def summary(rows):
    variables = [v[0] for v in VARIABLES] + ["test_count"]
    counts = {}
    for key in ("state_exact", "state_with_tolerance"):
        counts[key] = {v: {s: sum(1 for r in rows if r["variable"] == v and r[key] == s) for s in STATES}
                       for v in variables}
    diffs = {key: [{"config_id": r["config_id"], "variable": r["variable"], "state": r[key],
                    "catalog": "%s to %s" % (r["catalog_min_as_written"], r["catalog_max_as_written"])
                    if r["variable"] != "test_count" else r["catalog_min_as_written"],
                    "pipeline": "%s to %s (n=%s)" % (r["pipeline_min"], r["pipeline_max"], r["pipeline_n_recorded"])
                    if r["variable"] != "test_count" else str(r["pipeline_n_recorded"]),
                    "reason": r["reason"]}
                   for r in rows if r[key] in DIFFERENCE_STATES] for key in ("state_exact", "state_with_tolerance")}
    return {
        "_meta": {"generated_by": GENERATED_BY, "written_by": "pipeline/catalog_compare.py",
                  "inputs": ["data/catalog/configurations.csv", "data/pipeline/tests.csv",
                             "data/psi/experimental_tables/ (PSI-25, PSI-26 material cells)",
                             "pipeline/spec/sources.json (row_unit)"],
                  "mapping_rule": MAPPING_RULE, "tolerance": TOLERANCE, "states": list(STATES),
                  "difference_states": list(DIFFERENCE_STATES)},
        "configurations": len({r["config_id"] for r in rows}),
        "rows": len(rows),
        "counts_by_state": counts,
        "differences": {k: len(v) for k, v in diffs.items()},
        "difference_list": diffs,
        "sentences": SENTENCES,
    }


def write(rows, summ):
    with open(os.path.join(OUT, "catalog_comparison.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLUMNS})
    with open(os.path.join(OUT, "catalog_comparison_summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summ, f, indent=1, ensure_ascii=False)
        f.write("\n")


def main():
    if not os.path.exists(CONFIGS):
        print("catalog_compare: data/catalog/configurations.csv is absent; committed outputs left untouched")
        return 0
    configs = read_csv(CONFIGS)
    tests = read_csv(os.path.join(OUT, "tests.csv"))
    sources = json.load(open(os.path.join(HERE, "spec", "sources.json"), encoding="utf-8-sig"))["sources"]
    row_unit = {s["file"]: s.get("row_unit", "") for s in sources}
    rows = build(configs, tests, row_unit)
    summ = summary(rows)
    write(rows, summ)
    print("catalog_compare: %d configurations, %d rows, differences exact %d, with tolerance %d"
          % (summ["configurations"], len(rows), summ["differences"]["state_exact"],
             summ["differences"]["state_with_tolerance"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
