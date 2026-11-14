# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Raw-file gaps (experiment, branch data-lab).

For every PSI investigation and every standard variable used by the six needs
(pipeline/spec/needs.json), decide one state by fixed rule:

  no_test_table                the investigation has no per-test table
  in_table                     recorded for n of N mapped tests (data/pipeline/tests.csv)
  column_in_sampled_raw_file   empty in the table; one sampled file of a group has a
                               column (or a key in a text file) whose header names the
                               quantity (pipeline/spec/raw_columns.json); 'column_is'
                               says what kind of column it is
  documented_only              a document sentence states it for the whole table
                               (sources.json 'documented_elsewhere')
  not_in_sampled_files         none of the above; the unopened files of the
                               investigation are listed by kind
                               (data/pipeline/raw_inventory.json and the checker review)

A header says only that a sampled file has such a column; it does not say that
the values are complete, calibrated, or for the same test as a table row.
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

STATES = ["in_table", "column_in_sampled_raw_file", "documented_only", "not_in_sampled_files", "no_test_table"]
COLUMN_IS = ["sensor_reading_series", "value_per_test_in_a_results_file", "setting_or_set_point",
             "calculated_by_the_workbook", "event_timestamp", "operator_entry", "free_text",
             "calibration_example", "clock", "unclear"]
COL = "column_in_sampled_raw_file"
FORBIDDEN = re.compile(r"\b(safe|safely|safety-cleared|acceptable|sufficient|sufficiently|representative|proven|measured|logged)\b", re.I)
KINDS = (("videos", ("video",)), ("archives", ("archive",)), ("documents", ("document",)),
         ("tables", ("sensor_or_telemetry_table", "document_table")), ("other files", ("other", "still_image")))


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


def check_spec(raw):
    for inv in raw["investigations"]:
        for m in inv["mappings"]:
            if m.get("column_is") not in COLUMN_IS:
                sys.exit(f"raw_gaps: {inv['investigation_id']} {m['variable']}: column_is {m.get('column_is')!r} not one of {COLUMN_IS}")
            if m.get("header_kind") not in raw["_meta"]["header_kinds"]:
                sys.exit(f"raw_gaps: {inv['investigation_id']} {m['variable']}: header_kind {m.get('header_kind')!r}")
        for r in inv["related_columns_not_mapped"]:
            if "column_is" in r and r["column_is"] not in COLUMN_IS:
                sys.exit(f"raw_gaps: {inv['investigation_id']} related {r['header_as_written']!r}: column_is {r['column_is']!r}")


def kind_counts(inv):
    bk = inv.get("by_kind", {})
    out = {}
    for label, kinds in KINDS:
        n = sum(bk.get(k, {}).get("files", 0) for k in kinds)
        if label == "archives":
            n -= bk.get("archive", {}).get("archive_content", {}).get("investigation metadata", {}).get("files", 0)
        out[label] = n
    return out


def main():
    raw = load(SPEC / "raw_columns.json")
    check_spec(raw)
    S = raw["_meta"]["sentences"]
    needs = load(SPEC / "needs.json")["needs"]
    sources = load(SPEC / "sources.json")["sources"]
    inventory = load(DATA / "raw_inventory.json")["investigations"]
    tests = read_csv(DATA / "tests.csv")
    need_tests = read_csv(DATA / "need_tests.csv")

    V = need_variables(needs)
    spec_by_inv = {x["investigation_id"]: x for x in raw["investigations"]}
    tests_by_inv = {}
    for r in tests:
        tests_by_inv.setdefault(r["investigation_id"], []).append(r)
    test_row = {r["test_id"]: r for r in tests}

    result = {}
    for inv in inventory:
        iid = inv["investigation_id"]
        srcs = [s for s in sources if s["investigation_id"] == iid]
        per_test = [s for s in srcs if s.get("row_unit") == "test" and not s.get("not_standardized")]
        spec = spec_by_inv.get(iid, {"mappings": [], "groups": [], "related_columns_not_mapped": []})
        maps, rel = {}, {}
        for m in spec["mappings"]:
            maps.setdefault(m["variable"], []).append(m)
        for r in spec["related_columns_not_mapped"]:
            if "for_variable" in r:
                rel.setdefault(r["for_variable"], []).append(r)
        docs = {}
        for s in srcs:
            for d in s.get("documented_elsewhere", []) or []:
                docs.setdefault(d["variable"], []).append(
                    {"where": d.get("reference_item") or ("record field " + d.get("record_field", "")), "quote": d["quote"], "table": s["file"]})
        kinds = kind_counts(inv)
        opened = sum(1 for g in spec["groups"] if g.get("opened"))
        unopened = spec.get("unopened_groups_named_by_checker", [])
        rows = tests_by_inv.get(iid, [])
        N = len(rows)
        entry = {"tests_mapped": N, "files_by_kind": kinds, "groups_opened": opened,
                 "unopened_groups_named_by_checker": unopened, "variables": {}}
        if not per_test:
            if srcs:
                per = "; ".join(f"{s['file']}: one row per {s.get('row_unit')} ({s.get('not_standardized')})" for s in srcs)
            else:
                per = "no experimental table in the PSI listing"
            entry["table_per"] = per
        ctx = {"kinds": kinds, "opened": opened, "unopened": unopened}
        for v in V:
            if not per_test:
                cell = {"state": "no_test_table", "sentence": S["no_test_table"].format(per=entry["table_per"])}
                if v in maps:
                    cell["raw_columns_seen"] = [_m(m) for m in maps[v]]
                if v in rel:
                    cell["related_columns_not_mapped"] = [_r(r) for r in rel[v]]
                entry["variables"][v] = cell
                continue
            n = sum(1 for r in rows if r.get(v, "").strip())
            empty = empty_state(v, maps, docs, rel, ctx, S)
            if n > 0:
                cell = {"state": "in_table", "n": n, "N": N, "sentence": S["in_table"].format(n=n, N=N)}
                if n < N:
                    cell["remaining_tests"] = N - n
                    cell["remaining"] = empty
                    cell["sentence"] += " " + S["remaining"].format(m=N - n, state=label(empty))
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
        return label(cell["remaining"] if cell["state"] == "in_table" else cell)

    per_need = []
    no_table = [i for i, e in result.items() if "table_per" in e]
    for nd in needs:
        scope = nd.get("scope") or {}
        phases = scope.get("fuel_phase")
        ids = [r["test_id"] for r in need_tests if r["need_id"] == nd["id"]]
        in_scope = [r["test_id"] for r in tests if not phases or r["fuel_phase"] in phases]
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

    rv = raw["_meta"]["review_2026_11_14"]
    meta = {
        "generated_by": "AI-generated (Claude Code), 2026-11-14. Not human-reviewed.",
        "experiment": "branch data-lab; not merged into the pipeline",
        "inputs": ["pipeline/spec/raw_columns.json", "pipeline/spec/needs.json", "pipeline/spec/sources.json",
                   "data/pipeline/tests.csv", "data/pipeline/need_tests.csv", "data/pipeline/raw_inventory.json"],
        "states": raw["_meta"]["states"],
        "column_is": raw["_meta"]["column_is"],
        "header_kinds": raw["_meta"]["header_kinds"],
        "count_keys": "In the per-need counts a test in state column_in_sampled_raw_file is counted under 'column_in_sampled_raw_file:<column_is>' (several kinds joined by '+').",
        "order_rule": S["order_rule"],
        "caution": S["caution"],
        "sampling": S["sampling"],
        "not_opened": S["not_opened"],
        "reason": S["reason"],
        "mapping_by": raw["_meta"]["mapping_by"],
        "mapping_rule": raw["_meta"]["mapping_rule"],
        "review": rv,
        "psi69_video_count": raw["_meta"]["psi69_video_count"],
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
    return {k: m[k] for k in ("group", "header_as_written", "header_kind", "form", "column_is", "files_in_group", "mapping_by", "note") if k in m}


def _r(r):
    return {k: r[k] for k in ("group", "header_as_written", "column_is", "not_mapped_because", "decided_by") if k in r}


def label(cell):
    """State label of a cell; column_in_sampled_raw_file carries its column_is."""
    if cell["state"] == COL:
        return COL + ":" + "+".join(cell["column_is"])
    return cell["state"]


def _count(states):
    c = Counter(states)
    return {k: c[k] for k in sorted(c, key=lambda k: (STATES.index(k.split(":")[0]), k))}


def _rel_text(rs):
    return "; ".join(f"'{r['header_as_written']}' in {r['group']} ({r['not_mapped_because'].rstrip('.')})" for r in rs)


def empty_state(v, maps, docs, rel, ctx, S):
    rel_part = {"related_columns_not_mapped": [_r(r) for r in rel[v]]} if v in rel else {}
    rel_sent = S["related_line"].format(items=_rel_text(rel[v])) if v in rel else ""
    if v in maps:
        ms = [_m(m) for m in maps[v]]
        kinds = []
        for m in ms:
            if m["column_is"] not in kinds:
                kinds.append(m["column_is"])
        lead = S["column_in_sampled_raw_file_key"] if all(m["header_kind"] == "key in a text file" for m in ms) else S["column_in_sampled_raw_file"]
        det = " ".join(S["column_detail"].format(header_kind=m["header_kind"][0].upper() + m["header_kind"][1:], header=m["header_as_written"],
                                                 group=m["group"], files=m["files_in_group"], form=m["form"], column_is=m["column_is"],
                                                 note=("; " + m["note"]) if m.get("note") else "") for m in ms)
        also = {"also_documented": docs[v]} if v in docs else {}
        return {"state": COL, "column_is": kinds, "raw_columns": ms, **also, **rel_part,
                "sentence": lead + " " + det + rel_sent}
    if v in docs:
        d = docs[v][0]
        return {"state": "documented_only", "documented": docs[v], **rel_part,
                "sentence": S["documented_only"].format(where=d["where"], quote=d["quote"]) + rel_sent}
    k = ctx["kinds"]
    kinds = ", ".join(f"{k[label_]} {label_}" for label_, _ in KINDS)
    groups = ""
    if ctx["unopened"]:
        byk = {}
        for g in ctx["unopened"]:
            byk.setdefault(g["kind"], []).append(f"'{g['names']}' ({g['files']})")
        groups = S["not_in_sampled_groups"].format(groups="; ".join(f"{kk}: " + ", ".join(vv) for kk, vv in byk.items()))
    return {"state": "not_in_sampled_files", "files_by_kind": k, "groups_opened": ctx["opened"], **rel_part,
            "sentence": S["not_in_sampled_files"].format(kinds=kinds, opened=ctx["opened"], groups=groups) + rel_sent}


def render_md(out, raw, S, V):
    rv = out["_meta"]["review"]
    L = [f"# {S['title']}", "", "*" + out["_meta"]["generated_by"] + "*", "", S["intro"], "",
         S["caution"], "", " ".join([S["sampling"], S["not_opened"], S["reason"]]), "",
         S["review_line"].format(removed=rv["mappings_removed"], before=rv["mappings_before"], after=rv["mappings_after"]) + " " + rv["note"], "",
         S["video_count_line"], ""]
    d = raw["_meta"]["survey_downloads"]
    L += [S["downloads_line"].format(files=d["files"], bytes=d["bytes"], reopened=d["reopened_files"]), "",
          f"## {S['states_heading']}", ""]
    for k, t in raw["_meta"]["states"].items():
        L.append(f"- `{k}`: {t}")
    L += ["", "`column_is`:", ""]
    for k, t in raw["_meta"]["column_is"].items():
        L.append(f"- `{k}`: {t}")
    L += ["", S["order_rule"], "", f"## {S['need_heading']}", ""]
    hdr = "| " + " | ".join(["in_table", COL, S["column_is_heading"], "documented_only", "not_in_sampled_files"]) + " |"

    def row(c):
        col = {k.split(":", 1)[1]: n for k, n in c.items() if k.startswith(COL + ":")}
        by = "; ".join(f"{k} {n}" for k, n in col.items()) or "-"
        return " | ".join([str(c.get("in_table", 0)), str(sum(col.values())), by, str(c.get("documented_only", 0)), str(c.get("not_in_sampled_files", 0))])
    for b in out["per_need"]:
        L += [f"### {b['need_id']} {b['name']}", "",
              S["need_counted_line"].format(n=b["counted_or_recorded_tests"]) + " " + S["need_scope_line"].format(n=b["tests_in_scope"]), "",
              "| variable | tests " + hdr, "|---|---|---|---|---|---|---|"]
        for lab, key in (("counted or recorded", "required_counted_or_recorded"), ("in scope", "required_in_scope")):
            for v, c in b[key].items():
                L.append(f"| {v} | {lab} | " + row(c) + " |")
        L += ["", S["need_no_table_line"].format(names=", ".join(b["investigations_without_per_test_table"])), ""]
    L += [f"## {S['outcome_heading']}", "", "| need | variable " + hdr, "|---|---|---|---|---|---|---|"]
    for b in out["per_need"]:
        for v, c in b["outcomes_in_scope"].items():
            L.append(f"| {b['need_id']} | {v} | " + row(c) + " |")
    L += ["", f"## {S['inv_heading']}", ""]
    for iid, e in out["investigations"].items():
        L += [f"### {iid}", ""]
        if "table_per" in e:
            L += [S["no_test_table"].format(per=e["table_per"]), ""]
            seen = [(v, c["raw_columns_seen"]) for v, c in e["variables"].items() if "raw_columns_seen" in c]
            for v, ms in seen:
                L.append(f"- {v}: " + "; ".join(f"'{m['header_as_written']}' ({m['header_kind']}) in {m['group']} ({m['form']}; {m['column_is']})" for m in ms))
            rel = [(v, c["related_columns_not_mapped"]) for v, c in e["variables"].items() if "related_columns_not_mapped" in c]
            for v, rs in rel:
                L.append(f"- {v}, not mapped: " + _rel_text(rs).replace("|", "/"))
            if seen or rel:
                L.append("")
            continue
        first = next((c for c in e["variables"].values() if c["state"] == "not_in_sampled_files"), None)
        if first is None:
            first = next((c["remaining"] for c in e["variables"].values() if c.get("remaining", {}).get("state") == "not_in_sampled_files"), None)
        if first is not None:
            L += [S["md_unopened_lead"] + " " + first["sentence"].split(". ", 1)[1].split(" Related columns not mapped:")[0], ""]
        L += ["| variable | state | text |", "|---|---|---|"]
        for v in V:
            c = e["variables"][v]
            st = c["state"] if c["state"] != COL else COL + " (" + ", ".join(c["column_is"]) + ")"
            text = c["sentence"]
            if c["state"] == "not_in_sampled_files":
                text = S["md_not_in_sampled_short"] + (S["related_line"].format(items=_rel_text(c["related_columns_not_mapped"]))
                                                       if "related_columns_not_mapped" in c else "")
            L.append(f"| {v} | {st} | {text.replace('|', '/')} |")
        L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
