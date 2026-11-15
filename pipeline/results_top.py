# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-15).
"""Five quoted results to show first, per scenario x need (README "Results first", spec/results.json top_five).

Reads data/pipeline/results_by_need.json and pipeline/spec/results.json; imports no other script.
Writes data/pipeline/results_top.json and data/pipeline/results_top.csv. No weights, no scores: the order is
the fixed rule of spec/results.json top_five.selection_rule. Run after results.py.
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "pipeline", "spec")
OUT = os.path.join(ROOT, "data", "pipeline")
GENERATED = "AI-generated (Claude Code), 2026-11-15. Not human-reviewed."

CSV_COLUMNS = ("block_id", "scenario_id", "need_id", "rank", "position", "finding_id", "item_id", "line",
               "values_line", "conditions_line", "group", "result_kind", "relation", "investigation_id",
               "source_line", "url", "access", "skipped_before", "header", "more_n")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump(obj, path):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def fill(template, fields):
    out = re.sub(r"\[(\w+)\|([^|\]]*)\|([^|\]]*)\]",
                 lambda m: m.group(2) if fields[m.group(1)] == 1 else m.group(3), template)
    return re.sub(r"\{(\w+)\}", lambda m: str(fields[m.group(1)]), out)


def order_key(entry, pos, finding, top):
    kind = entry.get("result_kind") or "measured"
    return (top["group_order"].index(entry["group"]),
            top["kind_order"].index(kind),
            1 if finding.get("relation") else 0,
            0 if finding["printed_values"] else 1,
            entry["item_id"],
            pos)


def values_line(pvs, top):
    cells = []
    for p in pvs[:top["max_value_cells"]]:
        label = ", ".join(x for x in (p["row_label"], p["quantity"], p["column"]) if x)
        cells.append(fill(top["values_template"], {"label": label, "value": p["value_as_printed"],
                                                   "unit": p["unit"]}).rstrip())
    line = "; ".join(cells)
    if len(pvs) > top["max_value_cells"]:
        line += "; " + fill(top["values_more"], {"n": len(pvs) - top["max_value_cells"]})
    return line


def conditions_line(c):
    parts = []
    if c["o2_pct_min"]:
        if c["o2_pct_min"] == c["o2_pct_max"] or not c["o2_pct_max"]:
            parts.append("oxygen: %s%% O2" % c["o2_pct_min"])
        else:
            parts.append("oxygen: %s to %s%% O2" % (c["o2_pct_min"], c["o2_pct_max"]))
    if c["pressure_as_written"]:
        parts.append("pressure: %s" % c["pressure_as_written"])
    if c["gravity_level"]:
        parts.append("gravity level: %s" % c["gravity_level"].replace(";", ", "))
    if c["flow_cms"]:
        parts.append("flow: %s cm/s" % c["flow_cms"])
    if c["material"]:
        parts.append("material: %s" % c["material"])
    return "; ".join(parts)


def build():
    rs = load(os.path.join(SPEC, "results.json"))
    top = rs["top_five"]
    groups = {g["id"]: g["label"] for g in rs["order_rule"]["groups"]}
    banned = rs["forbidden_words"]
    doc = load(os.path.join(OUT, "results_by_need.json"))
    F = doc["findings"]
    blocks, rows, hits = [], [], []
    for scen in doc["scenarios"]:
        for nb in scen["needs"]:
            own = nb["found"]["entries"]
            ordered = sorted(enumerate(own), key=lambda pe: order_key(pe[1], pe[0], F[pe[1]["finding_id"]], top))
            taken, per_doc, skipped = [], {}, []
            for position, (pos, e) in enumerate(ordered, 1):
                if len(taken) == top["take"]:
                    break
                did = e["source"]["document_id"]
                if per_doc.get(did, 0) >= top["per_document"]:
                    skipped.append({"position": position, "finding_id": e["finding_id"], "document_id": did,
                                    "reason": top["skip_reason"]})
                    continue
                per_doc[did] = per_doc.get(did, 0) + 1
                f = F[e["finding_id"]]
                src = e["source"]
                ent = {
                    "scenario_id": scen["id"], "need_id": nb["need_id"], "rank": len(taken) + 1,
                    "position": position, "finding_id": e["finding_id"], "item_id": e["item_id"],
                    "line": fill(top["line_template"], {"text": f["text"]}),
                    "values_line": values_line(f["printed_values"], top),
                    "conditions_line": conditions_line(f["conditions"]),
                    "group": groups[e["group"]],
                    "result_kind": e.get("result_kind") or "",
                    "relation": f.get("relation") or "",
                    "investigation_id": "; ".join(f.get("investigation") or []),
                    "source_line": fill(top["source_template"], src),
                    "url": src["url"], "access": src["access"],
                    "skipped_before": skipped,
                }
                skipped = []
                taken.append(ent)
                for w in sorted({m.group(0).lower() for m in re.finditer(
                        r"\b(%s)\b" % "|".join(map(re.escape, banned)), ent["line"], re.I)}):
                    hits.append({"block_id": nb["block_id"], "finding_id": e["finding_id"], "word": w})
            n = len(own)
            fields = {"n": n, "k": len(taken), "a": sum(1 for e in own if e["group"] == "at_environment"),
                      "b": sum(1 for e in own if e["group"] == "about_a_stated_condition")}
            block = {"block_id": nb["block_id"], "scenario_id": scen["id"], "scenario": scen["label"],
                     "need_id": nb["need_id"], "need": nb["need"], "question": nb["question"],
                     "header": fill(top["header_template"], fields), "header_fields": fields,
                     "entries": taken,
                     "more": {"n": n - len(taken), "file": top["more_file"],
                              "where": "block %s, found.entries" % nb["block_id"]},
                     "footer": top["footer"]}
            if not own:
                block["no_result"] = top["no_result"]
            blocks.append(block)
            for ent in taken:
                rows.append(dict(ent, block_id=nb["block_id"], header=block["header"], more_n=block["more"]["n"],
                                 skipped_before=json.dumps(ent["skipped_before"], ensure_ascii=False)))
            if not own:
                rows.append({c: "" for c in CSV_COLUMNS} | {
                    "block_id": nb["block_id"], "scenario_id": scen["id"], "need_id": nb["need_id"],
                    "line": top["no_result"], "header": block["header"], "more_n": 0, "skipped_before": "[]"})
    out = {"_meta": {
        "generated_by": GENERATED,
        "written_by": "python3 pipeline/results_top.py",
        "inputs": ["data/pipeline/results_by_need.json", "pipeline/spec/results.json"],
        "selection_rule": top["selection_rule"],
        "line": top["line_note"],
        "values_line": top["values_label"],
        "conditions_line": top["conditions_note"],
        "no_result": top["no_result"],
        "team_output": "The order and the choice are the team's computation by the rule above; they are not "
                       "NASA's conclusions. A research exploration tool, not safety guidance.",
        "forbidden_word_hits_in_lines": hits,
        "footer": top["footer"],
    }, "blocks": blocks}
    return out, rows


def main():
    out, rows = build()
    dump(out, os.path.join(OUT, "results_top.json"))
    with open(os.path.join(OUT, "results_top.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, CSV_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    short = [b["block_id"] for b in out["blocks"] if len(b["entries"]) < 5]
    print("results_top: %d blocks, %d entries, %d blocks with fewer than five, %d forbidden-word hits in lines"
          % (len(out["blocks"]), sum(len(b["entries"]) for b in out["blocks"]), len(short),
             len(out["_meta"]["forbidden_word_hits_in_lines"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
