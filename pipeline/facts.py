#!/usr/bin/env python3
# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Per-investigation fact sheets: data/pipeline/investigation_facts.json.

A post-processing step. It reads the tables already written by run.py
(tests.csv, values_long.csv, capability_matrix.csv, objective_links.csv,
run_report.json), the specs in pipeline/spec/ and the PSI records in
data/psi/catalog/. It does not import or run run.py.

For every PSI investigation it writes the counts and the lowest and highest
recorded values the pipeline holds, and fixed sentences filled with them
(pipeline/spec/fact_statements.json). Nothing is estimated; an empty cell
stays "not recorded". The engine holds no experiment knowledge and no sentence
text: sentences, conditions, limits and the output notes come from the spec.

Usage:  python3 pipeline/facts.py
"""
import csv
import json
import os
import re
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = os.path.join(HERE, "spec")
OUT = os.path.join(ROOT, "data", "pipeline")
CATALOG = os.path.join(ROOT, "data", "psi", "catalog")
OUT_FILE = os.path.join(OUT, "investigation_facts.json")

NUMBER = re.compile(r"-?\d+(\.\d+)?([eE][-+]?\d+)?")
PLACEHOLDER = re.compile(r"\{([^{}]*)\}")
FORMAT = re.compile(r"(\S+)\s+(as|with)\s+(.+)")
PATH = re.compile(r"[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*")
MISSING = object()


class InputNotReady(Exception):
    """An input file could not be read or the inputs do not agree with each
    other (for example while run.py is rewriting them). build() reads again."""


# ------------------------------------------------------------------ reading
def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise InputNotReady(f"{path}: {e}")


def read_csv(name):
    path = os.path.join(OUT, name)
    try:
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    except (OSError, csv.Error, UnicodeDecodeError) as e:
        raise InputNotReady(f"{path}: {e}")
    if not rows:
        raise InputNotReady(f"{path}: no rows")
    return rows


def spec(name):
    return read_json(os.path.join(SPEC, name))


def accession_number(investigation_id):
    return int(investigation_id.rsplit("-", 1)[1])


def text_or_none(value):
    """An empty field of the PSI record is 'not recorded' (null)."""
    return value if isinstance(value, str) and value.strip() else None


def split_list(cell):
    return [x for x in cell.split(";") if x]


# ----------------------------------------------------------- variable facts
def numeric_variables(tests, var_cols):
    """A variable is numeric when every value it has in tests.csv is a number."""
    out = set()
    for v in var_cols:
        cells = [t[v] for t in tests if t[v] != ""]
        if cells and all(NUMBER.fullmatch(c) for c in cells):
            out.add(v)
    return out


def min_max(cells):
    values = [float(c) for c in cells]
    return {"n": len(values), "min": min(values), "max": max(values)}


def variable_facts(tests, var_cols, numeric, units, kinds, settings, origin=None):
    """{variable: facts} for the variables with at least one value in 'tests'."""
    limit = settings["max_category_values"]
    out = {}
    for v in var_cols:
        cells = [t[v] for t in tests if t[v] != ""]
        if not cells:
            continue
        fact = {"n": len(cells), "unit": units[v], "kind": kinds[v]}
        if v in numeric:
            fact.update(type="number", **{k: x for k, x in min_max(cells).items() if k != "n"})
            by = settings["split_by"].get(v)
            if by:
                groups = {}
                for t in tests:
                    if t[v] != "":
                        groups.setdefault(t[by] or "not_recorded", []).append(t[v])
                fact["by"] = {by: {g: min_max(groups[g]) for g in sorted(groups)}}
        else:
            counts = sorted(Counter(cells).items(), key=lambda kv: (-kv[1], kv[0]))
            fact.update(type="category", distinct=len(counts),
                        values=dict(counts[:limit]), values_truncated=len(counts) > limit)
            if len(counts) > limit:
                fact["values_shown"] = limit
        if origin is not None:
            fact["source_columns"] = sorted(origin.get(v, set()))
        out[v] = fact
    return out


def flags_by_variable(tests, var_cols):
    """{variable: {reason: occurrences}} from the 'variable:reason' flags."""
    found = {}
    for t in tests:
        for flag in split_list(t["flags"]):
            var, _, reason = flag.partition(":")
            found.setdefault(var, Counter())[reason] += 1
    order = [v for v in var_cols if v in found] + sorted(v for v in found if v not in var_cols)
    return {v: dict(sorted(found[v].items(), key=lambda kv: (-kv[1], kv[0]))) for v in order}


# --------------------------------------------------------------- statements
def resolve(ctx, path):
    cur = ctx
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return MISSING
        cur = cur[key]
    return cur


def holds(cond, ctx):
    value, op = resolve(ctx, cond["field"]), cond["op"]
    present = value is not MISSING and value is not None
    if op == "exists":
        return present
    if op == "missing":
        return not present
    if op in ("empty", "nonempty"):
        if present and not isinstance(value, (list, dict, str)):
            raise SystemExit(f"fact_statements.json: '{op}' needs a list, object or text: {cond}")
        return (not present or len(value) == 0) == (op == "empty")
    if op not in ("eq", "ne", "gt", "ge", "lt", "le", "in"):
        raise SystemExit(f"fact_statements.json: unknown operator in {cond}")
    if "value" not in cond:
        raise SystemExit(f"fact_statements.json: condition without 'value': {cond}")
    if not present:
        return False
    want = cond["value"]
    if op == "eq":
        return value == want
    if op == "ne":
        return value != want
    if op == "in":
        return value in want
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SystemExit(f"fact_statements.json: '{op}' needs a number: {cond}")
    return {"gt": value > want, "ge": value >= want, "lt": value < want, "le": value <= want}[op]


def scalar(value, where):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise SystemExit(f"fact_statements.json: {where} is not a text or a number")
    return repr(value) if isinstance(value, float) else str(value)


def fill(template, ctx):
    """Replace every {placeholder} with a field of the entry; stop on any that
    does not resolve. Inserted text is not scanned again."""
    def one(match):
        inner = match.group(1).strip()
        where = f"{template['id']}: {{{inner}}}"
        parts = FORMAT.fullmatch(inner)
        path, how, arg = (parts.group(1), parts.group(2), parts.group(3).strip()) if parts else (inner, None, None)
        if not PATH.fullmatch(path):
            raise SystemExit(f"fact_statements.json: bad placeholder in {where}")
        value = resolve(ctx, path)
        if value is MISSING or value is None:
            raise SystemExit(f"fact_statements.json: unknown placeholder in {where}")
        if how is None:
            return scalar(value, where)
        if how == "with":
            forms = arg.split("|")
            if len(forms) != 2 or isinstance(value, bool) or not isinstance(value, int):
                raise SystemExit(f"fact_statements.json: 'with' needs a count and singular|plural in {where}")
            return f"{value} {forms[0] if value == 1 else forms[1]}"
        if how == "as" and arg == "list" and isinstance(value, list) and value:
            return "; ".join(scalar(x, where) for x in value)
        if how == "as" and arg in ("counts", "pairs") and isinstance(value, dict) and value:
            items = [(k, x["n"] if isinstance(x, dict) and "n" in x else x) for k, x in value.items()]
            shape = "{} ({})" if arg == "counts" else "{}: {}"
            return "; ".join(shape.format(k, scalar(x, where)) for k, x in items)
        raise SystemExit(f"fact_statements.json: cannot write {where}")
    return PLACEHOLDER.sub(one, template["text"])


def check_wording(statement_spec):
    words = statement_spec["forbidden_words"]
    for section in statement_spec["sections"]:
        for st in section["statements"]:
            fixed = PLACEHOLDER.sub(" ", st["text"])
            found = [w for w in words if re.search(rf"\b{re.escape(w)}\b", fixed, re.I)]
            if found:
                raise SystemExit(f"fact_statements.json: {st['id']} contains {found}")


def scope_items(scope, entry):
    """(about, context) for every item of a scope, in the order of the entry."""
    tables = {t["source_id"]: t for t in entry["tables"]}
    if scope == "investigation":
        yield entry["investigation_id"], {"investigation": entry}
    elif scope == "table":
        for t in entry["tables"]:
            yield t["source_id"], {"investigation": entry, "table": t}
    elif scope == "objective_link":
        for link in entry["stated_needs"]:
            yield link["need_id"], {"investigation": entry, "link": link}
    elif scope == "need":
        for need in entry["capability"]:
            yield need["need_id"], {"investigation": entry, "need": need}
    elif scope == "need_table":
        for need in entry["capability"]:
            for row in need["by_table"]:
                yield f"{need['need_id']}/{row['source_id']}", {
                    "investigation": entry, "need": need, "row": row,
                    "table": tables[row["source_id"]]}
    else:
        raise SystemExit(f"fact_statements.json: unknown scope '{scope}'")


def statements(entry, statement_spec):
    out = []
    groups = statement_spec.get("groups", {})
    for section in statement_spec["sections"]:
        for about, ctx in scope_items(section["scope"], entry):
            hits = Counter()
            for st in section["statements"]:
                if all(holds(c, ctx) for c in st["when"]):
                    out.append({"id": st["id"], "about": about, "text": fill(st, ctx)})
                    if "group" in st:
                        hits[st["group"]] += 1
            for name in sorted({st["group"] for st in section["statements"] if "group" in st}):
                if name not in groups:
                    raise SystemExit(f"fact_statements.json: group '{name}' is not declared")
                due = all(holds(c, ctx) for c in groups[name]["exactly_one_when"])
                if hits[name] > 1 or (due and hits[name] != 1):
                    raise SystemExit(f"fact_statements.json: group '{name}' gives {hits[name]} "
                                     f"statements for {entry['investigation_id']} / {about}")
    return out


# ----------------------------------------------------------------- assemble
def column_map(source, var_cols):
    """variable -> source columns mapped to it, and the unit factors, as
    declared in sources.json."""
    cols, factors = {}, {}
    for c in source.get("columns", []):
        targets = c["to"] if isinstance(c["to"], list) else [c["to"]]
        for v in targets:
            cols.setdefault(v, []).append(c["from"])
        if "factor" in c.get("params", {}):
            factors[targets[0]] = c["params"]["factor"]
    order = [v for v in var_cols if v in cols]
    return {v: cols[v] for v in order}, {v: factors[v] for v in order if v in factors}


def assemble():
    variables, sources = spec("variables.json"), spec("sources.json")["sources"]
    needs, statement_spec = spec("needs.json"), spec("fact_statements.json")
    check_wording(statement_spec)
    var_cols = list(variables["variables"]) + list(variables["derived"])
    units = {k: v["unit"] for k, v in {**variables["variables"], **variables["derived"]}.items()}
    kinds = {**{k: v["kind"] for k, v in variables["variables"].items()},
             **{k: "derived" for k in variables["derived"]}}
    need_order = [n["id"] for n in needs["needs"]]
    need_names = {n["id"]: n["name"] for n in needs["needs"]}

    tests, values = read_csv("tests.csv"), read_csv("values_long.csv")
    matrix, links = read_csv("capability_matrix.csv"), read_csv("objective_links.csv")
    report = read_json(os.path.join(OUT, "run_report.json"))

    # the inputs must describe the same run
    absent = [c for c in var_cols + ["investigation_id", "source_id", "flags"] if c not in tests[0]]
    if absent:
        raise InputNotReady(f"tests.csv has no column {absent}")
    if len(tests) != report.get("tests") or len(values) != report.get("values"):
        raise InputNotReady("tests.csv / values_long.csv do not have the row counts of run_report.json")
    by_source = Counter(t["source_id"] for t in tests)
    for s in sources:
        if by_source.get(s["id"], 0) != report["sources"].get(s["id"], {}).get("tests", 0):
            raise InputNotReady(f"{s['id']}: tests.csv and run_report.json disagree on the number of tests")
    all_flags = Counter(f for t in tests for f in split_list(t["flags"]))
    if dict(all_flags) != report.get("flags"):
        raise InputNotReady("flags of tests.csv and run_report.json disagree")
    filled = Counter((v["investigation_id"], v["variable"]) for v in values)
    wide = Counter((t["investigation_id"], v) for t in tests for v in var_cols if t[v] != "")
    if filled != wide:
        raise InputNotReady("values_long.csv and tests.csv disagree on the values per variable")

    numeric = numeric_variables(tests, var_cols)
    origin = {}                                   # source file -> variable -> source columns
    for v in values:
        origin.setdefault(v["source_file"], {}).setdefault(v["variable"], set()).add(v["source_column"])

    records = [read_json(os.path.join(CATALOG, f)) for f in os.listdir(CATALOG) if f.endswith(".json")]
    records.sort(key=lambda r: accession_number(r["accession"]))
    known = {r["accession"] for r in records}
    stray = sorted({s["investigation_id"] for s in sources} - known)
    if stray:
        raise SystemExit(f"sources.json names investigations without a PSI record: {stray}")

    entries = []
    for rec in records:
        inv = rec["accession"]
        inv_sources = [s for s in sources if s["investigation_id"] == inv]
        in_record = sorted(e["file_name"] for e in rec.get("experimentalTable") or [])
        if in_record != sorted(s["file"] for s in inv_sources):
            raise SystemExit(f"{inv}: experimental tables of the PSI record and of sources.json differ")
        inv_tests = [t for t in tests if t["investigation_id"] == inv]

        tables = []
        for s in inv_sources:
            table = {"source_id": s["id"], "file": s["file"], "row_unit": s["row_unit"]}
            if "not_standardized" in s:
                table.update(table_status="not_test_level",
                             not_test_level_reason=s["not_standardized"], tests=0)
            else:
                run = report["sources"][s["id"]]
                rows = [t for t in inv_tests if t["source_id"] == s["id"]]
                cols, factors = column_map(s, var_cols)
                table.update(
                    table_status="test_level", rows_read=run["rows_read"],
                    rows_skipped=run["rows_skipped"], tests=len(rows),
                    rows_excluded=len(run.get("rows_excluded", [])),
                    rows_repeated=len(run.get("rows_repeating_an_earlier_row", [])),
                    row_note=s.get("row_note", ""),
                    documented_elsewhere=s.get("documented_elsewhere", []),
                    require=s.get("require", []), constants=s.get("constants", {}),
                    column_map=cols, unit_factors=factors,
                    source_columns_not_mapped=run["source_columns_not_mapped"],
                    flags_by_variable=flags_by_variable(rows, var_cols),
                    variables=variable_facts(rows, var_cols, numeric, units, kinds,
                                             statement_spec, origin.get(s["file"], {})))
            tables.append(table)
        states = {t["table_status"] for t in tables}
        status = ("no_experimental_table" if not tables
                  else states.pop() if len(states) == 1 else "mixed")

        capability = []
        for need_id in need_order:
            rows = [m for m in matrix if m["need_id"] == need_id and m["investigation_id"] == inv]
            if not rows:
                continue
            link = {m["objective_link"] for m in rows}
            if len(link) != 1 or [m["source_id"] for m in rows] != [s["id"] for s in inv_sources]:
                raise InputNotReady(f"capability_matrix.csv: unexpected rows for {need_id} x {inv}")
            link = link.pop()
            usable = sum(int(m["usable_tests"]) for m in rows)
            capability.append({
                "need_id": need_id, "need": rows[0]["need"], "pillar": rows[0]["pillar"],
                "objective_link": link,
                "tests_in_scope": sum(int(m["tests"]) for m in rows),
                "usable_tests": usable,
                "counted_tests": usable if link == "stated" else 0,
                "recorded_outside_objective": 0 if link == "stated" else usable,
                "statuses": {m["source_id"]: m["status"] for m in rows},
                "by_table": [{
                    "source_id": m["source_id"], "status": m["status"],
                    "tests_in_scope": int(m["tests"]),
                    "tests_with_required_conditions": int(m["tests_with_required_conditions"]),
                    "tests_with_outcome": int(m["tests_with_outcome"]),
                    "usable_tests": int(m["usable_tests"]),
                    "required_missing": split_list(m["required_missing"]),
                    "outcomes_present": split_list(m["outcomes_present"])} for m in rows]})

        flags = Counter(f for t in inv_tests for f in split_list(t["flags"]))
        entry = {
            "investigation_id": inv,
            "title": text_or_none(rec.get("title")),
            "acronym": text_or_none(rec.get("investigationAcronym")),
            "doi": text_or_none(rec.get("doi")),
            "license": {"identifier": text_or_none(rec.get("licenseIdentifier")),
                        "name": text_or_none(rec.get("licenseName")),
                        "link": text_or_none(rec.get("licenseLink"))},
            "table_status": status,
            "n_tables": len(tables),
            "n_tables_test_level": sum(t["table_status"] == "test_level" for t in tables),
            "tables": tables,
            "tests": len(inv_tests),
            "variables": variable_facts(inv_tests, var_cols, numeric, units, kinds, statement_spec),
            "stated_needs": [{"need_id": k["need_id"], "need": need_names[k["need_id"]],
                              "verdict": k["verdict"],
                              "publication_item": k["publication_item"],
                              "publication_quote": k["publication_quote"],
                              "record_field": k["record_field"], "quote": k["quote"]}
                             for need_id in need_order for k in links
                             if k["need_id"] == need_id and k["investigation_id"] == inv],
            "capability": capability,
            "flags": dict(sorted(flags.items(), key=lambda kv: (-kv[1], kv[0]))),
            "source_columns_not_mapped": {t["source_id"]: t["source_columns_not_mapped"]
                                          for t in tables if "source_columns_not_mapped" in t},
        }
        entry["statements"] = statements(entry, statement_spec)
        entries.append(entry)

    if sum(e["tests"] for e in entries) != len(tests):
        raise SystemExit("tests.csv holds tests of an investigation without a PSI record")
    meta = dict(statement_spec["output_meta"])
    if "status_rule" in needs["_meta"]:
        meta["status_rule"] = needs["_meta"]["status_rule"]
    meta.update(max_category_values=statement_spec["max_category_values"],
                investigations=len(entries), tests=len(tests))
    return {"_meta": meta, "investigations": entries}


def build(out_file=OUT_FILE, attempts=3, wait_s=2.0):
    """Write investigation_facts.json and return the document. The inputs are
    read again if they cannot be read or do not agree (run.py may be rewriting
    them); a problem in a spec stops the run at once."""
    for attempt in range(attempts):
        try:
            doc = assemble()
            break
        except InputNotReady as e:
            if attempt == attempts - 1:
                raise SystemExit(f"facts.py: inputs not usable: {e}")
            time.sleep(wait_s)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return doc


if __name__ == "__main__":
    document = build()
    print(f"{os.path.relpath(OUT_FILE, ROOT)}: {document['_meta']['investigations']} investigations, "
          f"{document['_meta']['tests']} tests, "
          f"{sum(len(e['statements']) for e in document['investigations'])} statements")
