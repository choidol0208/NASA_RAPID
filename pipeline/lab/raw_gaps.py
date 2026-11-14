# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Raw-file gaps (experiment, branch data-lab).

For every PSI investigation and every standard variable used by the six needs
(pipeline/spec/needs.json), decide one state by fixed rule:

  no_test_table            the investigation has no per-test table
  in_table                 recorded for n of N mapped tests (data/pipeline/tests.csv)
  measured_not_summarised  empty in the table; a sampled raw file has a column
                           for it (pipeline/spec/raw_columns.json)
  documented_only          a document sentence states it for the whole table
                           (sources.json 'documented_elsewhere')
  video_or_archive_only    no sampled table column; videos or archives exist
                           (data/pipeline/raw_inventory.json)
  no_record_found          none of the above in what was sampled

Writes data/pipeline/lab/raw_gaps.json and raw_gaps.md. No value of a raw file
is read: the spec names headers only. Every sentence comes from the spec.
Same inputs give the same bytes (no timestamps, fixed order).
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "pipeline" / "spec"
DATA = ROOT / "data" / "pipeline"
OUT = DATA / "lab"

STATES = ["in_table", "measured_not_summarised", "documented_only",
          "video_or_archive_only", "no_record_found", "no_test_table"]
FORBIDDEN = re.compile(r"\b(safe|safely|safety-cleared|acceptable|sufficient|sufficiently|representative|proven)\b", re.I)


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def read_csv(p):
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def need_variables(needs):
    out = []
    for nd in needs:
        for k in ("conditions_required", "conditions_useful", "outcomes_any"):
            for v in nd[k]:
                if v not in out:
                    out.append(v)
    return out


def formula_inputs(name, derived, known):
    """Base variables a derived variable is computed from (recursive)."""
    f = derived[name]["formula"]
    toks = [t for t in re.findall(r"[a-z][a-z0-9_]*", f) if t in known or t in derived]
    base = []
    for t in toks:
        if t in derived:
            for b in formula_inputs(t, derived, known):
                if b not in base:
                    base.append(b)
        elif t not in base:
            base.append(t)
    return base


def main():
    raw = load(SPEC / "raw_columns.json")
    S = raw["_meta"]["sentences"]
    needs = load(SPEC / "needs.json")["needs"]
    sources = load(SPEC / "sources.json")["sources"]
    varspec = load(SPEC / "variables.json")
    derived = varspec["derived"]
    known = set(varspec["variables"])
    inventory = load(DATA / "raw_inventory.json")["investigations"]
    tests = read_csv(DATA / "tests.csv")
    need_tests = read_csv(DATA / "need_tests.csv")

    V = need_variables(needs)
    spec_by_inv = {x["investigation_id"]: x for x in raw["investigations"]}
    tests_by_inv = {}
    for r in tests:
        tests_by_inv.setdefault(r["investigation_id"], []).append(r)
    test_row = {r["test_id"]: r for r in tests}

    def media(inv):
        bk = inv.get("by_kind", {})
        vid = bk.get("video", {}).get("files", 0)
        arc = bk.get("archive", {})
        meta_arc = arc.get("archive_content", {}).get("investigation metadata", {}).get("files", 0)
        return vid, arc.get("files", 0) - meta_arc

    result = {}
    for inv in inventory:
        iid = inv["investigation_id"]
        srcs = [s for s in sources if s["investigation_id"] == iid]
        per_test = [s for s in srcs if s.get("row_unit") == "test" and not s.get("not_standardized")]
        spec = spec_by_inv.get(iid, {"mappings": [], "groups": []})
        maps = {}
        for m in spec["mappings"]:
            maps.setdefault(m["variable"], []).append(m)
        docs = {}
        for s in srcs:
            for d in s.get("documented_elsewhere", []) or []:
                docs.setdefault(d["variable"], []).append(
                    {"where": d.get("reference_item") or ("record field " + d.get("record_field", "")), "quote": d["quote"], "table": s["file"]})
        vids, arcs = media(inv)
        rows = tests_by_inv.get(iid, [])
        N = len(rows)
        entry = {"tests_mapped": N, "videos": vids, "archives_not_metadata": arcs, "variables": {}}
        if not per_test:
            if srcs:
                per = "; ".join(f"{s['file']}: one row per {s.get('row_unit')} ({s.get('not_standardized')})" for s in srcs)
            else:
                per = "no experimental table in the PSI listing"
            entry["table_per"] = per
        for v in V:
            if not per_test:
                cell = {"state": "no_test_table", "sentence": S["no_test_table"].format(per=entry["table_per"])}
                if v in maps:
                    cell["raw_columns_seen"] = [_m(m) for m in maps[v]]
                entry["variables"][v] = cell
                continue
            n = sum(1 for r in rows if r.get(v, "").strip())
            empty = empty_state(v, maps, docs, vids, arcs, derived, known, rows, S)
            if n > 0:
                cell = {"state": "in_table", "n": n, "N": N, "sentence": S["in_table"].format(n=n, N=N)}
                if n < N:
                    cell["remaining_tests"] = N - n
                    cell["remaining"] = empty
                    cell["sentence"] += " " + S["remaining"].format(m=N - n, state=empty["state"])
            else:
                cell = dict(empty)
                cell["n"], cell["N"] = 0, N
            entry["variables"][v] = cell
        result[iid] = entry

    def test_state(tid, v):
        r = test_row[tid]
        if r.get(v, "").strip():
            return "in_table"
        cell = result[r["investigation_id"]]["variables"][v]
        return cell["remaining"]["state"] if cell["state"] == "in_table" else cell["state"]

    per_need = []
    for nd in needs:
        scope = nd.get("scope") or {}
        phases = scope.get("fuel_phase")
        ids = [r["test_id"] for r in need_tests if r["need_id"] == nd["id"]]
        in_scope = [r["test_id"] for r in tests if not phases or r["fuel_phase"] in phases]
        no_table = [i for i, e in result.items() if "table_per" in e]
        blk = {"need_id": nd["id"], "name": nd["name"], "scope": scope,
               "counted_or_recorded_tests": len(ids), "tests_in_scope": len(in_scope),
               "investigations_without_per_test_table": no_table,
               "required_counted_or_recorded": {}, "required_in_scope": {}, "outcomes_in_scope": {}}
        for v in nd["conditions_required"]:
            blk["required_counted_or_recorded"][v] = _count(test_state(t, v) for t in ids)
            blk["required_in_scope"][v] = _count(test_state(t, v) for t in in_scope)
        for v in nd["outcomes_any"]:
            blk["outcomes_in_scope"][v] = _count(test_state(t, v) for t in in_scope)
        per_need.append(blk)

    meta = {
        "generated_by": "AI-generated (Claude Code), 2026-11-14. Not human-reviewed.",
        "experiment": "branch data-lab; not merged into the pipeline",
        "inputs": ["pipeline/spec/raw_columns.json", "pipeline/spec/needs.json", "pipeline/spec/sources.json",
                   "pipeline/spec/variables.json", "data/pipeline/tests.csv", "data/pipeline/need_tests.csv",
                   "data/pipeline/raw_inventory.json"],
        "states": raw["_meta"]["states"],
        "order_rule": S["order_rule"],
        "caution": S["caution"],
        "sampling": S["sampling"],
        "not_opened": S["not_opened"],
        "reason": S["reason"],
        "mapping_by": raw["_meta"]["mapping_by"],
        "variables": V,
        "survey_downloads": raw["_meta"]["survey_downloads"],
    }
    out = {"_meta": meta, "investigations": result, "per_need": per_need}
    text = json.dumps(out, indent=1, ensure_ascii=False, sort_keys=False) + "\n"
    md = render_md(out, raw, S, V)
    for t, name in ((text, "raw_gaps.json"), (md, "raw_gaps.md")):
        bad = FORBIDDEN.findall(t)
        if bad:
            sys.exit(f"raw_gaps: forbidden word(s) {sorted(set(bad))} in {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "raw_gaps.json", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    with open(OUT / "raw_gaps.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(md)
    print("raw_gaps: wrote", OUT / "raw_gaps.json", "and raw_gaps.md")


def _m(m):
    return {k: m[k] for k in ("group", "header_as_written", "form", "column_is", "files_in_group", "mapping_by") if k in m} | (
        {"note": m["note"]} if "note" in m else {})


def _count(states):
    c = Counter(states)
    return {s: c[s] for s in STATES if c[s]}


def empty_state(v, maps, docs, vids, arcs, derived, known, rows, S):
    if v in maps:
        ms = [_m(m) for m in maps[v]]
        m = ms[0]
        also = {"also_documented": docs[v]} if v in docs else {}
        return {"state": "measured_not_summarised", "raw_columns": ms, **also,
                "sentence": S["measured_not_summarised"].format(header=m["header_as_written"], group=m["group"],
                                                                 files=m["files_in_group"], form=m["form"], column_is=m["column_is"])}
    if v in derived:
        ins = formula_inputs(v, derived, known)
        ok = all(i in maps or any(r.get(i, "").strip() for r in rows) for i in ins)
        if ok and any(i in maps for i in ins):
            missing = [i for i in ins if not any(r.get(i, "").strip() for r in rows)]
            order = [i for i in ins if i in missing] + [i for i in ins if i not in missing]
            ms = [_m(m) | {"input": i, "input_in_table": i not in missing} for i in order if i in maps for m in maps[i]]
            m = ms[0]
            return {"state": "measured_not_summarised", "raw_columns": ms, "computed_from": ins,
                    "sentence": S["measured_not_summarised"].format(header=m["header_as_written"], group=m["group"],
                                                                     files=m["files_in_group"], form=m["form"], column_is=m["column_is"])
                    + " " + S["computable"].format(formula=derived[v]["formula"])}
    if v in docs:
        d = docs[v][0]
        return {"state": "documented_only", "documented": docs[v],
                "sentence": S["documented_only"].format(where=d["where"], quote=d["quote"])}
    if vids + arcs > 0:
        return {"state": "video_or_archive_only", "videos": vids, "archives_not_metadata": arcs,
                "sentence": S["video_or_archive_only"].format(videos=vids, archives=arcs)}
    return {"state": "no_record_found", "sentence": S["no_record_found"]}


def render_md(out, raw, S, V):
    L = [f"# {S['title']}", "", "*" + out["_meta"]["generated_by"] + "*", "", S["intro"], "",
         S["caution"], "", " ".join([S["sampling"], S["not_opened"], S["reason"]]), ""]
    d = raw["_meta"]["survey_downloads"]
    L += [S["downloads_line"].format(files=d["files"], bytes=d["bytes"], reopened=d["reopened_files"]), "",
          f"## {S['states_heading']}", ""]
    for k, t in raw["_meta"]["states"].items():
        L.append(f"- `{k}`: {t}")
    L += ["", S["order_rule"], "", f"## {S['need_heading']}", ""]
    for b in out["per_need"]:
        L += [f"### {b['need_id']} {b['name']}", "",
              S["need_counted_line"].format(n=b["counted_or_recorded_tests"]) + " " + S["need_scope_line"].format(n=b["tests_in_scope"]), "",
              "| variable | tests | " + " | ".join(STATES[:-1]) + " |", "|---|---|" + "---|" * (len(STATES) - 1)]
        for label, key in (("counted or recorded", "required_counted_or_recorded"), ("in scope", "required_in_scope")):
            for v, c in b[key].items():
                L.append(f"| {v} | {label} | " + " | ".join(str(c.get(s, 0)) for s in STATES[:-1]) + " |")
        L += ["", S["need_no_table_line"].format(names=", ".join(b["investigations_without_per_test_table"])), ""]
    L += [f"## {S['outcome_heading']}", "", "| need | variable | " + " | ".join(STATES[:-1]) + " |", "|---|---|" + "---|" * (len(STATES) - 1)]
    for b in out["per_need"]:
        for v, c in b["outcomes_in_scope"].items():
            L.append(f"| {b['need_id']} | {v} | " + " | ".join(str(c.get(s, 0)) for s in STATES[:-1]) + " |")
    L += ["", f"## {S['inv_heading']}", ""]
    for iid, e in out["investigations"].items():
        L += [f"### {iid}", ""]
        if "table_per" in e:
            L += [S["no_test_table"].format(per=e["table_per"]), ""]
            seen = [(v, c["raw_columns_seen"]) for v, c in e["variables"].items() if "raw_columns_seen" in c]
            for v, ms in seen:
                L.append(f"- {v}: " + "; ".join(f"'{m['header_as_written']}' in {m['group']} ({m['form']})" for m in ms))
            if seen:
                L.append("")
            continue
        L += ["| variable | state | text |", "|---|---|---|"]
        for v in V:
            c = e["variables"][v]
            L.append(f"| {v} | {c['state']} | {c['sentence'].replace('|', '/')} |")
        L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
