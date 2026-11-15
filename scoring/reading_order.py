#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude Code, catalog role) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-15). No language model runs when this script runs.
"""The order of pile 2: which unprocessed file groups to read first, per scenario and question.

Rule (docs/raw_data_design/design.md section 3.3; pm request 20261115-0035), fixed and public, with no
weights, probabilities or expected gains:

  class 1  file groups in which a column for oxygen or pressure was seen, for tests that cannot be
           placed from the table in this scenario (their oxygen or pressure is not in the table);
  class 2  file groups that could add a counted test: an outcome the question needs, for tests not
           counted for the question that have no outcome value and whose recorded oxygen or pressure lies
           inside the ranges, with none recorded outside (inside, or oxygen inside and no pressure in a
           table). design.md 3.3 says "for a test inside"; its own fixture (section 7: the BASS-II Summary
           Report, up to 44 tests, for S1 at the ISS) is 44 BASS-II tests with oxygen inside and no
           pressure in a table, so this wider reading is used and recorded in the meta file. Tests with
           neither value in a table are class-1 targets first;
  class 3  file groups that could add a value to a test already counted inside the ranges.
  Within a class: more target tests first, then fewer bytes, then investigation and group id.

A group's class is the lowest class for which it has target tests. Target tests are a set, so a test
is counted once per group; the bytes of a group are counted once. A group with no target test in any
class for this scenario and question is left out: reading it would not move a test of this question.

Inputs, all on main (data role, read only):
  data/pipeline/retrieval_queue.csv   file groups still to be read, per investigation and variable
  data/pipeline/tests.csv             which tests lack which value
  data/pipeline/scenario_tests.csv    o2_match / pressure_match per scenario and test (placement)
  data/pipeline/need_tests.csv        counted tests per question (objective_link = stated)
  data/pipeline/objective_links.csv   investigations linked to a question with verdict "supported"
  pipeline/spec/needs.json            the conditions and outcomes of each question, and its scope
Placement (design.md 3.1): inside = oxygen and pressure both in; outside_by_recorded_value = either
recorded out; oxygen_of_oxidizer_stream; cannot_be_placed_from_table = the rest; no_range_set when
the scenario sets no range.

Outputs: data/catalog/reading_order.csv and data/catalog/reading_order.json (rule, header sentence,
input hashes, counts).

Usage: python3 scoring/reading_order.py [--check]
Standard library only.
"""
import argparse
import ast
import csv
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPE = os.path.join(ROOT, "data", "pipeline")
SPEC = os.path.join(ROOT, "pipeline", "spec")
OUT_CSV = os.path.join(ROOT, "data", "catalog", "reading_order.csv")
OUT_JSON = os.path.join(ROOT, "data", "catalog", "reading_order.json")
INPUTS = [os.path.join(PIPE, f) for f in ("retrieval_queue.csv", "tests.csv", "scenario_tests.csv", "need_tests.csv",
                                           "objective_links.csv")] + [os.path.join(SPEC, "needs.json")]
HEADER = "The order is the team's rule, not a priority of NASA. It says where to read first, not that a value is there."
CLASS_MEANING = {
    1: "oxygen or pressure column seen, for tests that cannot be placed from the table",
    2: "could add a counted test: an outcome for tests not counted for the question, with no outcome value, whose recorded oxygen or pressure is inside and none outside",
    3: "could add a value to a test already counted inside the ranges",
}
PLACE_VARS = ("o2_pct", "pressure_kpa")
KIND_WORDS = {
    "documents_not_opened": "document not opened",
    "drawing_no_text_layer": "drawing without a text layer, not read",
    "document_over_size_limit": "document over the size limit, not opened",
    "download_failed": "download failed",
    "table_over_size_limit": "table over the size limit, not opened",
    "value_per_test_in_a_results_file": "value per test in a results file",
    "sensor_reading_series": "sensor reading series",
    "setting_or_set_point": "setting or set point",
}
COLS = ["scenario_id", "need_id", "order", "class", "class_meaning", "investigation_id", "file_group", "name_pattern",
        "variables", "files", "bytes", "target_tests", "target_test_ids", "state", "evidence"]


def _rows(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def _list(v):
    if isinstance(v, list):
        return v
    if not v:
        return []
    try:
        x = ast.literal_eval(v)
        return list(x) if isinstance(x, (list, tuple)) else [x]
    except (ValueError, SyntaxError):
        return [s.strip() for s in str(v).split(";") if s.strip()]


def placement(o2, p):
    if "not_specified" in (o2, p):
        return "no_range_set"
    if o2 == "out" or p == "out":
        return "outside_by_recorded_value"
    if o2 == "not_ambient":
        return "oxygen_of_oxidizer_stream"
    if o2 == "in" and p == "in":
        return "inside"
    return "cannot_be_placed_from_table"


def load():
    tests = {r["test_id"]: r for r in _rows(os.path.join(PIPE, "tests.csv"))}
    place, partly_inside = {}, set()
    for r in _rows(os.path.join(PIPE, "scenario_tests.csv")):
        pl = placement(r["o2_match"], r["pressure_match"])
        place[(r["scenario_id"], r["test_id"])] = pl
        if pl == "inside" or (pl == "cannot_be_placed_from_table" and "in" in (r["o2_match"], r["pressure_match"])):
            partly_inside.add((r["scenario_id"], r["test_id"]))
    counted = {}
    for r in _rows(os.path.join(PIPE, "need_tests.csv")):
        if r["objective_link"] == "stated":
            counted.setdefault(r["need_id"], set()).add(r["test_id"])
    linked = {}
    for r in _rows(os.path.join(PIPE, "objective_links.csv")):
        if r["verdict"] == "supported":
            linked.setdefault(r["need_id"], set()).add(r["investigation_id"])
    spec = json.load(open(os.path.join(SPEC, "needs.json"), encoding="utf-8"))
    needs = {}
    for n in spec["needs"]:
        scope = n.get("scope")
        if isinstance(scope, str):
            scope = ast.literal_eval(scope) if scope else {}
        needs[n["id"]] = dict(required=_list(n.get("conditions_required")), useful=_list(n.get("conditions_useful")),
                              outcomes=_list(n.get("outcomes_any")), phases=(scope or {}).get("fuel_phase"))
    queue = _rows(os.path.join(PIPE, "retrieval_queue.csv"))
    scenarios = sorted({s for s, _ in place}, key=lambda s: ["iss", "lunar_habitat", "mars_habitat", "spacesuit",
                                                              "exploration_8_2_34", "exploration_10_2_26_5"].index(s)
                       if s in ["iss", "lunar_habitat", "mars_habitat", "spacesuit", "exploration_8_2_34",
                                "exploration_10_2_26_5"] else 99)
    return tests, place, partly_inside, counted, linked, needs, queue, scenarios


def evidence(r):
    if r["state"] == "column_in_sampled_raw_file":
        head = r["headers_as_written"] or "a column"
        return f"column seen: {head}; {r['sampling']}"
    words = KIND_WORDS.get(r["kind"], r["kind"].replace("_", " "))
    return f"{words}; no column seen ({r['sampling']})"


def build():
    tests, place, partly_inside, counted, linked, needs, queue, scenarios = load()
    out = []
    for s in scenarios:
        for nid, n in needs.items():
            vars_n = set(n["required"]) | set(n["useful"]) | set(n["outcomes"])
            groups = {}
            for q in queue:
                v, inv = q["variable"], q["investigation_id"]
                if v not in vars_n or inv not in linked.get(nid, set()):
                    continue
                lacking = [t for t, tr in tests.items() if tr["investigation_id"] == inv
                           and (not n["phases"] or tr["fuel_phase"] in n["phases"]) and (tr.get(v) or "").strip() == ""]
                key = (inv, q["file_group"])
                g = groups.setdefault(key, dict(q=q, variables=set(), t={1: set(), 2: set(), 3: set()}))
                g["variables"].add(v)
                for t in lacking:
                    pl = place.get((s, t))
                    if v in PLACE_VARS and q["state"] == "column_in_sampled_raw_file" and pl == "cannot_be_placed_from_table":
                        g["t"][1].add(t)
                    # Class 2 as design.md section 7 counts it ("the only file group that could add a counted S1 test
                    # is the BASS-II Summary Report, up to 44 tests"): a test not counted for the question, with no
                    # value for any of its outcomes, whose recorded atmosphere values all lie inside the ranges with
                    # at least one recorded (inside, or oxygen inside with no pressure in a table). Section 3.3 says
                    # "for a test inside"; the fixture needs this wider reading, and the meta file records it. A test
                    # with neither value in a table goes to class 1 first: it has to be placed before it can count.
                    if (v in n["outcomes"] and (s, t) in partly_inside and t not in counted.get(nid, set())
                            and all(not (tests[t].get(o) or "").strip() for o in n["outcomes"])):
                        g["t"][2].add(t)
                    if pl == "inside" and t in counted.get(nid, set()):
                        g["t"][3].add(t)
            rows = []
            for (inv, grp), g in groups.items():
                cls = next((c for c in (1, 2, 3) if g["t"][c]), None)
                if cls is None:
                    continue
                q = g["q"]
                b = int(q["bytes"]) if q["bytes"] else None
                rows.append(dict(scenario_id=s, need_id=nid, cls=cls, investigation_id=inv, file_group=grp,
                                 name_pattern=q["name_pattern"], variables=";".join(sorted(g["variables"])),
                                 files=q["files"], bytes=q["bytes"], targets=sorted(g["t"][cls]), state=q["state"],
                                 evidence=evidence(q), _b=b))
            rows.sort(key=lambda r: (r["cls"], -len(r["targets"]), r["_b"] is None, r["_b"] or 0, r["investigation_id"], r["file_group"]))
            for i, r in enumerate(rows, start=1):
                out.append({"scenario_id": s, "need_id": nid, "order": i, "class": r["cls"], "class_meaning": CLASS_MEANING[r["cls"]],
                            "investigation_id": r["investigation_id"], "file_group": r["file_group"], "name_pattern": r["name_pattern"],
                            "variables": r["variables"], "files": r["files"], "bytes": r["bytes"], "target_tests": len(r["targets"]),
                            "target_test_ids": ";".join(r["targets"]), "state": r["state"], "evidence": r["evidence"]})
    return out


def render(out):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(out)
    counts = {}
    for r in out:
        k = f"{r['scenario_id']}/{r['need_id']}"
        counts.setdefault(k, {"rows": 0, "class_1": 0, "class_2": 0, "class_3": 0})
        counts[k]["rows"] += 1
        counts[k][f"class_{r['class']}"] += 1
    meta = {
        "label": "AI-generated data file: built by code written with an AI assistant (Claude Code, catalog role). No language model ran to build it. "
                 "The team's ordering rule applied to the data role's files, not a NASA priority.",
        "header": HEADER,
        "rule": [CLASS_MEANING[1], CLASS_MEANING[2], CLASS_MEANING[3],
                 "Within a class: more target tests first, then fewer bytes, then investigation and group id. A group takes its lowest class; "
                 "target tests are a set; bytes are counted once per group; groups with no target test are left out."],
        "source": "docs/raw_data_design/design.md section 3.3; pm request 20261115-0035",
        "interpretation": "Class 2 takes tests not counted for the question, with no outcome value, whose recorded oxygen or pressure is inside the "
                          "ranges and none outside (inside, or oxygen inside and no pressure in a table). design.md 3.3 says 'for a test inside'; the "
                          "fixture of design.md 6 and 7 (S1 at the ISS: only the BASS-II Summary Report, up to 44 tests) needs this wider reading: the "
                          "44 are BASS-II tests with oxygen inside the ISS range and no pressure in a table. Tests with neither value in a table are "
                          "class-1 targets first.",
        "inputs_sha256": {os.path.relpath(p, ROOT).replace(os.sep, "/"): hashlib.sha256(open(p, "rb").read().replace(b"\r\n", b"\n")).hexdigest()
                          for p in INPUTS},
        "counts": counts,
    }
    return buf.getvalue(), json.dumps(meta, ensure_ascii=False, indent=2) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    out = build()
    csv_text, json_text = render(out)
    if args.check:
        same = all(os.path.exists(p) and open(p, encoding="utf-8").read() == t for p, t in ((OUT_CSV, csv_text), (OUT_JSON, json_text)))
        print("reading order is up to date" if same else "reading order differs from its inputs")
        return 0 if same else 1
    for p, t in ((OUT_CSV, csv_text), (OUT_JSON, json_text)):
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(t)
    print(f"wrote {len(out)} rows to {OUT_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
