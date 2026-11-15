# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-15).
"""How fire-safety work runs, as NASA documents state it, and what the PSI
tables record per need.

Run after question_chain.py (python3 pipeline/process_steps.py). Reads
pipeline/spec/{process,references,needs}.json and data/pipeline/{tests,
need_tests,file_links}.csv. Writes, in data/pipeline/:

  process_steps.json         the steps of pipeline/spec/process.json with the
                             quotes of their references.json items, the needs
                             that inform each step, the measures, the four
                             capability areas and the sentences on where fire
                             control puts its weight
  need_recorded_summary.csv  per need: tests in scope in PSI's tables, of which
                             of investigations whose stated purpose names the
                             subject (stated_by verdict 'supported'), of which
                             with an outcome of the need in a table cell, of
                             which counted; tests with a video tied by two
                             labels (file_links.csv); one sentence from counts

process_view(need_id) gives the 'process' field that evidence.py adds to each
need block of an evidence package and answers.py adds to each answer file. It
reads only spec files, so run.py can use it before this script has run.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = os.path.join(HERE, "spec")
OUT = os.path.join(ROOT, "data", "pipeline")
GENERATED_BY = "AI-generated (Claude Code), 2026-11-15. Not human-reviewed."
ITEM_KEYS = ("document_id", "title", "version", "url", "access")


def load(name):
    with open(os.path.join(SPEC, name + ".json"), encoding="utf-8-sig") as f:
        return json.load(f)


def reference_items():
    out = {}
    for doc in load("references")["references"]:
        for it in doc["items"]:
            out[it["id"]] = {"item_id": it["id"], "type": it["type"], "quote": it.get("quote", ""),
                             "where": it["where"], "document_id": doc["id"], "title": doc["title"],
                             "version": doc.get("version", ""), "url": doc.get("url", ""), "access": doc.get("access", "")}
    return out


def item_view(items, iid):
    if iid not in items:
        raise SystemExit("process_steps: item %s of spec/process.json is not in references.json" % iid)
    if not items[iid]["quote"]:
        raise SystemExit("process_steps: item %s has no quote" % iid)
    return dict(items[iid])


def process_doc():
    spec, items, needs = load("process"), reference_items(), load("needs")["needs"]
    informs = {s["id"]: [n["id"] for n in needs if s["id"] in n.get("informs_process_steps", {}).get("steps", [])]
               for s in spec["steps"]}
    steps = [{"id": s["id"], "order": s["order"], "label_by_team": s["label_by_team"],
              "items": [item_view(items, i) for i in s["items"]],
              "measures": [item_view(items, i) for i in s["measures"]],
              "needs_informing": informs[s["id"]]} for s in spec["steps"]]
    return {
        "_meta": {"generated_by": GENERATED_BY, "written_by": "pipeline/process_steps.py",
                  "inputs": ["pipeline/spec/process.json", "pipeline/spec/references.json", "pipeline/spec/needs.json"],
                  "authorship": spec["_meta"]["authorship"], "measure_rule": spec["_meta"]["measure_rule"]},
        "sentence": spec["_meta"]["fixed_sentence"],
        "steps": steps,
        "capability_areas": {"label_by_team": spec["capability_areas"]["label_by_team"],
                             "items": [item_view(items, i) for i in spec["capability_areas"]["items"]]},
        "where_the_weight_lies": {"label_by_team": spec["where_the_weight_lies"]["label_by_team"],
                                  "items": [item_view(items, i) for i in spec["where_the_weight_lies"]["items"]]},
        "needs": [{"need_id": n["id"], "need": n["name"],
                   "informs_process_steps": n.get("informs_process_steps", {}).get("steps", []),
                   "team_reading": n.get("informs_process_steps", {}).get("team_reading", "")} for n in needs],
    }


_CACHE = {}


def process_view(need_id):
    """The 'process' field of a need block or an answer file."""
    if "doc" not in _CACHE:
        _CACHE["doc"] = process_doc()
    doc = _CACHE["doc"]
    need = next(n for n in doc["needs"] if n["need_id"] == need_id)
    steps = [s for s in doc["steps"] if s["id"] in need["informs_process_steps"]]
    return {"steps_informed": [{"id": s["id"], "order": s["order"], "label_by_team": s["label_by_team"]} for s in steps],
            "team_reading": need["team_reading"],
            "measures": [dict(m, step_id=s["id"]) for s in steps for m in s["measures"]],
            "sentence": doc["sentence"],
            "source": "data/pipeline/process_steps.json"}


def read_csv(name):
    with open(os.path.join(OUT, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


SUMMARY_COLUMNS = ("need_id", "need", "scope", "tests_in_scope", "investigations_supported",
                   "tests_in_scope_of_supported_investigations", "with_outcome_in_table_cell",
                   "outcome_cells_by_variable", "counted_tests", "in_scope_supported_with_video_two_labels",
                   "counted_with_video_two_labels", "sentence")


def scope_text(need):
    sc = need.get("scope", {})
    return "; ".join("%s: %s" % (k, ", ".join(v)) for k, v in sc.items()) or "no scope limit"


def need_summary():
    tests = read_csv("tests.csv")
    counted = {}
    for r in read_csv("need_tests.csv"):
        if r["objective_link"] == "stated":
            counted.setdefault(r["need_id"], set()).add(r["test_id"])
    video = {r["test_id"] for r in read_csv("file_links.csv")
             if r["kind"] == "video" and r["link_state"] == "two_labels_agree" and r["test_id"]}
    rows = []
    for need in load("needs")["needs"]:
        scope = [t for t in tests if all(t.get(k) in v for k, v in need.get("scope", {}).items())]
        sup = sorted({s["investigation_id"] for s in need.get("stated_by", []) if s.get("verdict") == "supported"},
                     key=lambda x: int(x.split("-")[1]))
        linked = [t for t in scope if t["investigation_id"] in sup]
        outs = need["outcomes_any"]
        with_out = [t for t in linked if any(t[o] != "" for o in outs)]
        by_var = "; ".join("%s %d" % (o, sum(1 for t in linked if t[o] != "")) for o in outs)
        c = counted.get(need["id"], set())
        ids = {t["test_id"] for t in linked}
        row = {"need_id": need["id"], "need": need["name"], "scope": scope_text(need), "tests_in_scope": len(scope),
               "investigations_supported": "; ".join(sup), "tests_in_scope_of_supported_investigations": len(linked),
               "with_outcome_in_table_cell": len(with_out), "outcome_cells_by_variable": by_var,
               "counted_tests": len(c), "in_scope_supported_with_video_two_labels": len(ids & video),
               "counted_with_video_two_labels": len(c & video)}
        row["sentence"] = ("%d tests in the scope of '%s' (%s) of investigations whose stated purpose names this subject "
                           "(%s) are in PSI's tables; %d have an outcome of the need in a "
                           "table cell (%s); %d are counted; %d have a video tied to them by two labels."
                           % (len(linked), need["name"], row["scope"], row["investigations_supported"] or "none",
                              len(with_out), by_var, len(c), len(ids & video)))
        rows.append(row)
    return rows


def main():
    doc = process_doc()
    with open(os.path.join(OUT, "process_steps.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    rows = need_summary()
    with open(os.path.join(OUT, "need_recorded_summary.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, SUMMARY_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("process_steps: %d steps, %d measures; need_recorded_summary: %d needs"
          % (len(doc["steps"]), sum(len(s["measures"]) for s in doc["steps"]), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
