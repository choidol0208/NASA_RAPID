#!/usr/bin/env python3
# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Spec-driven pipeline: PSI experimental tables -> fire-safety information needs.

The engine holds no knowledge about any experiment. Everything it does is
declared in pipeline/spec/:
    needs.json      what fire safety needs to know, and which variables answer it
    variables.json  the standard variables, their valid ranges, derived formulas
    sources.json    how each PSI table maps onto the standard variables

Stages
    1 ingest       read each PSI table as text; nothing is changed
    2 standardize  apply the column -> variable rules of sources.json
    3 validate     range checks; a bad value is emptied and flagged, never fixed
    4 derive       compute the formulas of variables.json
    5 assess       for every need x source: which tests carry the required
                   conditions and at least one outcome
    6 export       tables in data/pipeline/

The pipeline links tests to questions. It does not answer the questions and
draws no conclusion from the values.

Usage:  python3 pipeline/run.py
"""
import csv
import io
import json
import math
import os
import re
import sys
from collections import Counter

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from rules import RULES  # noqa: E402

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "psi", "experimental_tables")
OUT = os.path.join(ROOT, "data", "pipeline")
ID_COLS = ["test_id", "investigation_id", "source_id"]
TRACE_COLS = ["flags", "source_file", "source_row"]


def spec(name):
    with open(os.path.join(HERE, "spec", name), encoding="utf-8") as f:
        return json.load(f)


def empty(v):
    return v is None or (isinstance(v, float) and math.isnan(v))


# ------------------------------------------------------------------ 1 ingest
def ingest(file_name):
    """(header, [(source_row, {column: cell})]); the header is source row 1."""
    raw = open(os.path.join(SRC, file_name), "rb").read().decode("utf-8-sig", "replace")
    records = [[c.strip() for c in r] for r in csv.reader(io.StringIO(raw))]
    header = records[0]
    rows = [(i + 1, dict(zip(header, (r + [""] * len(header))[:len(header)])))
            for i, r in enumerate(records) if i > 0 and any(r)]
    return header, rows


# ------------------------------------------------------------- 2 standardize
def standardize(source, variables, report):
    header, rows = ingest(source["file"])
    used = [c["from"] for c in source["columns"]] + source.get("require", [])
    used += re.findall(r"\{(.+?)\}", source["test_id"])
    missing = [c for c in used if c != "row" and c not in header]
    if missing:
        raise SystemExit(f"{source['id']}: columns not in source file: {missing}")
    for c in source["columns"]:
        targets = c["to"] if isinstance(c["to"], list) else [c["to"]]
        unknown = [t for t in targets if t not in variables]
        if unknown or c["rule"] not in RULES:
            raise SystemExit(f"{source['id']}: unknown variable or rule in {c}")

    tests, cells, skipped, seen = [], [], 0, Counter()
    for source_row, r in rows:
        if any(not r[c] for c in source.get("require", [])):
            skipped += 1
            continue
        flags = []
        test_id = source["test_id"].format(row=source_row, **r).replace(" ", "")
        seen[test_id] += 1
        if seen[test_id] > 1:
            flags.append("test_id:duplicate_in_source")
            test_id = f"{test_id}@row{source_row}"
        rec = {"test_id": test_id, "investigation_id": source["investigation_id"],
               "source_id": source["id"]}
        origin = {}
        for var, value in source.get("constants", {}).items():
            rec[var], origin[var] = value, "(constant in sources.json)"
        for c in source["columns"]:
            var = c["to"] if isinstance(c["to"], str) else c["to"][0]
            result = RULES[c["rule"]](r[c["from"]], flags, var, **c.get("params", {}))
            for k, v in (result if isinstance(result, dict) else {var: result}).items():
                if not empty(v):
                    rec[k], origin[k] = v, c["from"]
        rec["_flags"], rec["_origin"] = flags, origin
        rec["source_file"], rec["source_row"] = source["file"], source_row
        tests.append(rec)
    report["sources"][source["id"]] = {
        "file": source["file"], "rows_read": len(rows), "rows_skipped": skipped,
        "tests": len(tests),
        "source_columns_not_mapped": [c for c in header if c and c not in used],
    }
    return tests


# ---------------------------------------------------------------- 3 validate
def validate(tests, ranges):
    for t in tests:
        for var, (low, high) in ranges.items():
            v = t.get(var)
            if empty(v):
                continue
            if (low is not None and v < low) or (high is not None and v > high):
                t["_flags"].append(f"{var}:out_of_range")
                t[var] = None


# ------------------------------------------------------------------ 4 derive
def derive(tests, derived):
    """Formulas are arithmetic on standard variable names (variables.json)."""
    for t in tests:
        for name, d in derived.items():
            inputs = set(re.findall(r"[a-z][a-z0-9_]*", d["formula"])) - {"e"}
            env = {k: t.get(k) for k in inputs}
            if any(empty(v) for v in env.values()):
                continue
            hit = next((s for s in d.get("skip_if", []) if eval(s["expr"], {"__builtins__": {}}, env)), None)
            if hit:
                if hit["flag"]:
                    t["_flags"].append(f"{name}:{hit['flag']}")
                continue
            value = round(eval(d["formula"], {"__builtins__": {}}, env), 5)
            for f in d.get("flag_if", []):
                if eval(f["expr"], {"__builtins__": {}}, {"value": value}):
                    t["_flags"].append(f"{name}:{f['flag']}")
            t[name] = value
            t["_origin"][name] = "(derived: " + d["formula"] + ")"


# ------------------------------------------------------------------ 5 assess
def assess(tests, needs, sources):
    """Need x source capability. Status follows needs.json 'status_rule'."""
    matrix, links = [], []
    by_source = {}
    for t in tests:
        by_source.setdefault(t["source_id"], []).append(t)
    for need in needs:
        req, outs = need["conditions_required"], need["outcomes_any"]
        for s in sources:
            row = {"need_id": need["id"], "pillar": need["pillar"], "need": need["name"],
                   "investigation_id": s["investigation_id"], "source_id": s["id"],
                   "row_unit": s["row_unit"]}
            if "not_standardized" in s:
                row.update(status="not_test_level", tests=0, tests_with_required_conditions=0,
                           tests_with_outcome=0, usable_tests=0, required_missing="",
                           outcomes_present="", note=s["not_standardized"])
                matrix.append(row)
                continue
            ts = [t for t in by_source.get(s["id"], [])
                  if all(t.get(k) in allowed for k, allowed in need.get("scope", {}).items())]
            if not ts:
                row.update(status="out_of_scope", tests=0, tests_with_required_conditions=0,
                           tests_with_outcome=0, usable_tests=0, required_missing="",
                           outcomes_present="", note="no test within the scope of this need")
                matrix.append(row)
                continue
            has_req = [all(not empty(t.get(v)) for v in req) for t in ts]
            has_out = [any(not empty(t.get(v)) for v in outs) for t in ts]
            usable = [t for t, a, b in zip(ts, has_req, has_out) if a and b]
            status = ("measured" if usable else "partial" if any(has_out)
                      else "conditions_only" if any(has_req) else "none")
            row.update(
                status=status, tests=len(ts), tests_with_required_conditions=sum(has_req),
                tests_with_outcome=sum(has_out), usable_tests=len(usable),
                required_missing=";".join(v for v in req if all(empty(t.get(v)) for t in ts)),
                outcomes_present=";".join(v for v in outs if any(not empty(t.get(v)) for t in ts)),
                note="")
            matrix.append(row)
            links += [{"need_id": need["id"], "test_id": t["test_id"],
                       "investigation_id": t["investigation_id"]} for t in usable]
    return pd.DataFrame(matrix), pd.DataFrame(links)


# ------------------------------------------------------------------ 6 export
def export(tests, variables, derived, matrix, links, report):
    os.makedirs(OUT, exist_ok=True)
    var_cols = list(variables) + list(derived)
    units = {k: v["unit"] for k, v in {**variables, **derived}.items()}
    kinds = {**{k: v["kind"] for k, v in variables.items()}, **{k: "derived" for k in derived}}
    wide, long = [], []
    for t in tests:
        wide.append({**{c: t.get(c) for c in ID_COLS + var_cols},
                     "flags": ";".join(t["_flags"]),
                     "source_file": t["source_file"], "source_row": t["source_row"]})
        for var in var_cols:
            if not empty(t.get(var)):
                long.append({"test_id": t["test_id"], "investigation_id": t["investigation_id"],
                             "variable": var, "kind": kinds[var], "value": t[var],
                             "unit": units[var], "source_file": t["source_file"],
                             "source_row": t["source_row"], "source_column": t["_origin"][var]})
    wide = pd.DataFrame(wide, columns=ID_COLS + var_cols + TRACE_COLS)
    wide.to_csv(os.path.join(OUT, "tests.csv"), index=False)
    pd.DataFrame(long).to_csv(os.path.join(OUT, "values_long.csv"), index=False)
    matrix.to_csv(os.path.join(OUT, "capability_matrix.csv"), index=False)
    links.to_csv(os.path.join(OUT, "need_tests.csv"), index=False)
    flags = Counter(f for t in tests for f in t["_flags"])
    report.update(tests=len(tests), values=len(long), flags=dict(flags.most_common()),
                  variable_fill={v: int(wide[v].notna().sum()) for v in var_cols})
    with open(os.path.join(OUT, "run_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    return wide


def main():
    needs, var_spec, src_spec = spec("needs.json"), spec("variables.json"), spec("sources.json")
    variables, derived = var_spec["variables"], var_spec["derived"]
    ranges = {k: v for k, v in var_spec["ranges"].items() if not k.startswith("_")}
    report = {"generated_by": "AI-generated code (pipeline/run.py); values come from NASA PSI tables",
              "sources": {}}
    tests = []
    for s in src_spec["sources"]:
        if "not_standardized" in s:
            report["sources"][s["id"]] = {"file": s["file"], "not_standardized": s["not_standardized"]}
            continue
        tests += standardize(s, variables, report)
    validate(tests, ranges)
    derive(tests, derived)
    matrix, links = assess(tests, needs["needs"], src_spec["sources"])
    export(tests, variables, derived, matrix, links, report)

    print(f"{len(tests)} tests, {report['values']} values, {len(links)} need-test links\n")
    shown = matrix[matrix.status != "not_test_level"]
    print(shown.pivot(index="source_id", columns="need_id", values="usable_tests").to_string())
    print()
    print(shown.pivot(index="source_id", columns="need_id", values="status").to_string())


if __name__ == "__main__":
    main()
