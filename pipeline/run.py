#!/usr/bin/env python3
# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Spec-driven pipeline: PSI experimental tables -> fire-safety information needs.

The engine holds no knowledge about any experiment. Everything it does is
declared in pipeline/spec/:
    needs.json      what fire safety needs to know, and which variables answer it
    variables.json  the standard variables, their valid ranges, derived formulas
    sources.json    how each PSI table maps onto the standard variables
    references.json the standards, requirements and published results behind each need
    coverage.json   bin edges for the coverage grid
    scenarios.json  crewed environments to compare the recorded tests with
    indicators.json what is computed per need, by fixed templates
    materials.json  one id per material, with the names used in the tables

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


MATERIAL_IDS = {alias.strip().lower(): m["id"]
                for m in spec("materials.json")["materials"] for alias in m["aliases"]}


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
        name = rec.get("fuel_material")
        if not empty(name):
            mid = MATERIAL_IDS.get(str(name).strip().lower())
            if mid:
                rec["material_id"], origin["material_id"] = mid, "(materials.json from fuel_material)"
            else:
                flags.append("material_id:not_in_vocabulary")
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


def coverage_grid(tests, cov):
    """Count recorded tests per fuel phase, oxygen basis, oxygen bin and
    pressure bin (coverage.json). Missing values go to 'not_recorded'."""
    nr = cov["not_recorded"]["id"]

    def bin_of(value, bins):
        if empty(value):
            return nr
        for b in bins:
            low = b["min"] is None or value > b["min"] or (value == b["min"] and b["min_inclusive"])
            high = b["max"] is None or value < b["max"] or (value == b["max"] and b["max_inclusive"])
            if low and high:
                return b["id"]
        raise SystemExit(f"coverage.json: no bin for value {value}")

    dims = cov["dimensions"]
    labels = {nr: cov["not_recorded"]["label"]}
    order = {}
    for name, d in dims.items():
        labels.update({b["id"]: b["label"] for b in d["bins"]})
        order[name] = [b["id"] for b in d["bins"]] + [nr]
    cells = {}
    for t in tests:
        basis = t.get("o2_basis") if not empty(t.get("o2_basis")) else nr
        key = (t.get("fuel_phase") or nr, basis,
               bin_of(t.get("o2_pct"), dims["o2_pct"]["bins"]),
               bin_of(t.get("pressure_kpa"), dims["pressure_kpa"]["bins"]))
        cells.setdefault(key, []).append(t)
    # every cell for the ambient basis, so that empty cells are visible as 0
    phases = sorted({k[0] for k in cells})
    for phase in phases:
        for o in order["o2_pct"]:
            for p in order["pressure_kpa"]:
                cells.setdefault((phase, "ambient", o, p), [])
    rows = []
    for (phase, basis, o, p), ts in sorted(
            cells.items(), key=lambda kv: (kv[0][0], kv[0][1], order["o2_pct"].index(kv[0][2]),
                                           order["pressure_kpa"].index(kv[0][3]))):
        rows.append({"fuel_phase": phase, "o2_basis": basis, "o2_bin": o, "o2_bin_label": labels[o],
                     "pressure_bin": p, "pressure_bin_label": labels[p], "tests": len(ts),
                     "investigation_ids": ";".join(sorted({t["investigation_id"] for t in ts},
                                                          key=lambda x: int(x.split("-")[1]))),
                     "source_ids": ";".join(sorted({t["source_id"] for t in ts}))})
    return pd.DataFrame(rows)


def in_range(value, r):
    low = r.get("min") is None or value > r["min"] or (value == r["min"] and r.get("min_inclusive", True))
    high = r.get("max") is None or value < r["max"] or (value == r["max"] and r.get("max_inclusive", False))
    return low and high


def match_scenarios(tests, links, needs, scen_spec, report):
    """Per scenario: mark every test against the scenario ranges, then count
    the tests usable for each need by match tier (scenarios.json)."""
    usable = {}
    for row in links.itertuples():
        usable.setdefault(row.need_id, set()).add(row.test_id)
    test_rows, need_rows = [], []
    tiers = ["atmosphere", "oxygen_only", "pressure_only", "other"]
    for sc in scen_spec["scenarios"]:
        marks = {}
        for t in tests:
            m = {}
            for var in ("o2_pct", "pressure_kpa", "flow_cms"):
                r = sc["ranges"].get(var)
                v = t.get(var)
                m[var] = ("not_specified" if r is None else "not_recorded" if empty(v)
                          else "in" if in_range(v, r) else "out")
            if m["o2_pct"] in ("in", "out") and t.get("o2_basis") != "ambient":
                m["o2_pct"] = "not_ambient"
            m["gravity"] = "same" if t.get("gravity_level") == sc["gravity_level"] else "different"
            o, p = m["o2_pct"], m["pressure_kpa"]
            m["tier"] = ("atmosphere" if o == "in" and p == "in"
                         else "oxygen_only" if o == "in" and p == "not_recorded"
                         else "pressure_only" if p == "in" and o == "not_recorded" else "other")
            marks[t["test_id"]] = m
            test_rows.append({"scenario_id": sc["id"], "test_id": t["test_id"],
                              "investigation_id": t["investigation_id"], "source_id": t["source_id"],
                              "fuel_phase": t.get("fuel_phase"), "o2_match": o, "pressure_match": p,
                              "flow_match": m["flow_cms"], "gravity_match": m["gravity"],
                              "tier": m["tier"]})
        by_id = {t["test_id"]: t for t in tests}
        for need in needs:
            ids = usable.get(need["id"], set())
            row = {"scenario_id": sc["id"], "need_id": need["id"], "need": need["name"],
                   "usable_tests": len(ids)}
            for tier in tiers:
                hit = [i for i in ids if marks[i]["tier"] == tier]
                row[f"tests_{tier}"] = len(hit)
                row[f"investigations_{tier}"] = ";".join(sorted(
                    {by_id[i]["investigation_id"] for i in hit}, key=lambda x: int(x.split("-")[1])))
            row["status"] = next((name for name, tier in (("in_atmosphere", "atmosphere"),
                                                           ("oxygen_only", "oxygen_only"),
                                                           ("pressure_only", "pressure_only"))
                                  if row[f"tests_{tier}"]),
                                 "other_atmosphere" if ids else "not_measured")
            best = [i for i in ids if marks[i]["tier"] in ("atmosphere", "oxygen_only")]
            row["matched_tests_flow_in_range"] = sum(marks[i]["flow_cms"] == "in" for i in best)
            row["matched_tests_flow_not_recorded"] = sum(marks[i]["flow_cms"] == "not_recorded" for i in best)
            row["matched_tests_same_gravity"] = sum(marks[i]["gravity"] == "same" for i in best)
            gaps = []
            if ids and not any(marks[i]["o2_pct"] == "in" for i in ids):
                gaps.append("oxygen:not_recorded" if all(marks[i]["o2_pct"] == "not_recorded" for i in ids)
                            else "oxygen:no_usable_test_in_range")
            if ids and not any(marks[i]["pressure_kpa"] == "in" for i in ids):
                gaps.append("pressure:not_recorded" if all(marks[i]["pressure_kpa"] == "not_recorded" for i in ids)
                            else "pressure:no_usable_test_in_range")
            if ids and not any(marks[i]["gravity"] == "same" for i in ids):
                gaps.append(f"gravity:no_usable_test_at_{sc['gravity_level']}")
            if not ids:
                gaps.append("need:no_usable_test")
            row["gaps"] = ";".join(gaps)
            row["scenario_gravity_level"] = sc["gravity_level"]
            need_rows.append(row)
    # consistency with the ui presets
    path = os.path.join(ROOT, "scoring", "scoring_config.json")
    mismatch = []
    if os.path.exists(path):
        presets = json.load(open(path, encoding="utf-8")).get("presets", {})
        for sc in scen_spec["scenarios"]:
            values = presets.get(sc["id"], {}).get("values")
            if values is None:
                mismatch.append(f"{sc['id']}: no preset with this id")
            else:
                mismatch += [f"{sc['id']}.{k}: {v} here, {values.get(k)} in preset"
                             for k, v in sc["nominal"].items() if values.get(k) != v]
    report["scenario_preset_mismatch"] = mismatch
    return pd.DataFrame(test_rows), pd.DataFrame(need_rows)


OPS = {"==": lambda a, b: a == b, "!=": lambda a, b: a != b, ">": lambda a, b: a > b,
       ">=": lambda a, b: a >= b, "<": lambda a, b: a < b, "<=": lambda a, b: a <= b}


def passes(t, cond):
    var, op = cond[0], cond[1]
    v = ";".join(t["_flags"]) if var == "flags" else t.get(var)
    if op == "notnull":
        return not empty(v)
    if op == "contains":
        return cond[2] in (v or "")
    return not empty(v) and OPS[op](v, cond[2])


def indicators(tests, links, needs, ind_spec, variables, derived, ref_items):
    """Apply the fixed templates of indicators.json. Returns the indicator
    table and the list of tests behind every row."""
    units = {k: v["unit"] for k, v in {**variables, **derived}.items()}
    need_by_id = {n["id"]: n for n in needs}
    usable = {}
    for row in links.itertuples():
        usable.setdefault(row.need_id, set()).add(row.test_id)
    rows, members = [], []
    for ind in ind_spec["indicators"]:
        need = need_by_id[ind["need_id"]]
        for ref in ind["definition_ref"] + ind.get("compare_with", []):
            if ref not in ref_items:
                raise SystemExit(f"indicator {ind['id']}: unknown reference item {ref}")
        var = ind.get("variable")
        if var and var not in units and var != "flags":
            raise SystemExit(f"indicator {ind['id']}: unknown variable {var}")
        if ind["population"] == "usable":
            pop = [t for t in tests if t["test_id"] in usable.get(need["id"], set())]
        else:
            pop = [t for t in tests
                   if all(t.get(k) in allowed for k, allowed in need.get("scope", {}).items())
                   and all(not empty(t.get(v)) for v in need["conditions_required"])]
        pop = [t for t in pop if all(passes(t, c) for c in ind["where"])]
        if ind["template"] != "count":
            pop = [t for t in pop if not empty(t.get(var))]
        groups = {}
        for t in pop:
            key = tuple("" if empty(t.get(g)) else str(t.get(g)) for g in ind["group_by"])
            groups.setdefault(key, []).append(t)
        for key, ts in sorted(groups.items()):
            group = ";".join(f"{g}={v}" for g, v in zip(ind["group_by"], key))
            base = {"indicator_id": ind["id"], "need_id": ind["need_id"], "label": ind["label"],
                    "group": group, "variable": var, "unit": units.get(var, ""), "n_tests": len(ts),
                    "investigation_ids": ";".join(sorted({t["investigation_id"] for t in ts},
                                                         key=lambda x: int(x.split("-")[1]))),
                    "definition_ref": ";".join(ind["definition_ref"]),
                    "compare_with": ";".join(ind.get("compare_with", [])),
                    "reading": ind["reading"]}
            if ind["template"] == "summary":
                values = pd.Series([t[var] for t in ts], dtype=float)
                for stat in ind["stats"]:
                    rows.append({**base, "stat": stat, "category": "",
                                 "value": round(float(getattr(values, stat)()), 5)})
            elif ind["template"] == "count_by":
                for cat, n in sorted(Counter(str(t[var]) for t in ts).items()):
                    rows.append({**base, "stat": "count", "category": cat, "value": n})
            else:
                rows.append({**base, "stat": "count", "category": "", "value": len(ts)})
            members += [{"indicator_id": ind["id"], "group": group, "test_id": t["test_id"],
                         "value": t.get(var) if var != "flags" else ""} for t in ts]
    cols = ["indicator_id", "need_id", "label", "group", "stat", "category", "value", "unit",
            "n_tests", "investigation_ids", "variable", "definition_ref", "compare_with", "reading"]
    return pd.DataFrame(rows, columns=cols), pd.DataFrame(members)


def need_references(needs, references):
    """Need -> reference items. Fails if a need points to an unknown item."""
    items = {i["id"]: (r, i) for r in references for i in r["items"]}
    rows = []
    for need in needs:
        for item_id in need.get("references", []):
            if item_id not in items:
                raise SystemExit(f"need {need['id']}: unknown reference item {item_id}")
            r, i = items[item_id]
            rows.append({"need_id": need["id"], "item_id": item_id, "item_type": i["type"],
                         "text": i["text"], "where": i["where"],
                         "variables": ";".join(i.get("variables", [])),
                         "values": json.dumps(i["values"]) if "values" in i else "",
                         "reference_id": r["id"], "title": r["title"], "issuer": r["issuer"],
                         "version": r["version"], "access": r["access"], "url": r["url"]})
    return pd.DataFrame(rows)


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
    grid = coverage_grid(tests, spec("coverage.json"))
    assert grid.tests.sum() == len(tests)
    grid.to_csv(os.path.join(OUT, "coverage_grid.csv"), index=False)
    sc_tests, sc_needs = match_scenarios(tests, links, needs["needs"], spec("scenarios.json"), report)
    sc_tests.to_csv(os.path.join(OUT, "scenario_tests.csv"), index=False)
    sc_needs.to_csv(os.path.join(OUT, "scenario_needs.csv"), index=False)
    with open(os.path.join(OUT, "run_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    all_refs = spec("references.json")["references"]
    ref_items = {i["id"] for r in all_refs for i in r["items"]}
    ind_table, ind_tests = indicators(tests, links, needs["needs"], spec("indicators.json"),
                                      variables, derived, ref_items)
    ind_table.to_csv(os.path.join(OUT, "indicators.csv"), index=False)
    ind_tests.to_csv(os.path.join(OUT, "indicator_tests.csv"), index=False)
    refs = need_references(needs["needs"], spec("references.json")["references"])
    refs.to_csv(os.path.join(OUT, "need_references.csv"), index=False)

    print(f"{len(tests)} tests, {report['values']} values, {len(links)} need-test links, "
          f"{len(refs)} need-reference links\n")
    shown = matrix[matrix.status != "not_test_level"]
    print(shown.pivot(index="source_id", columns="need_id", values="usable_tests").to_string())
    print()
    print(shown.pivot(index="source_id", columns="need_id", values="status").to_string())


if __name__ == "__main__":
    main()
