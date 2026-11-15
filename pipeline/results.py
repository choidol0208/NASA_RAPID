# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-15).
"""Results first: what NASA's experiments found, per scenario and question.

Writes
  data/pipeline/results_by_need.json  per scenario (6) x need (6), in page order:
      found (quoted results), criteria, process, recorded, unprocessed,
      no_record, caveats, and a headline built from counts only
  data/pipeline/results_flat.csv      one row per result x printed value
  data/pipeline/results_summary.json  counts, and the audit of what is not structured
and adds the field 'results_first' to every answer file in data/pipeline/answers/.

It is a post-processing step. It reads pipeline/spec/results.json,
references.json, needs.json, scenarios.json, process.json, and the outputs
findings.csv, findings_by_environment.json, process_steps.json,
need_recorded_summary.csv, scenario_needs.csv, question_chain.csv and
question_chain_counts.csv. It imports no other script of the pipeline and
places, counts and judges nothing again: the groups are those of
findings_by_environment.json, the counts those of the CSV files. It computes
nothing with a published value. Run it after answers.py.

Usage:  python3 pipeline/results.py
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = os.path.join(HERE, "spec")
OUT = os.path.join(ROOT, "data", "pipeline")
ANSWERS = os.path.join(OUT, "answers")
GENERATED = "AI-generated (Claude Code), 2026-11-15. Not human-reviewed."
COND_COLS = ("o2_pct_min", "o2_pct_max", "pressure_kpa_min", "pressure_kpa_max", "pressure_as_written",
             "gravity_level", "flow_cms", "fuel_phase", "material")
FLAT_COLUMNS = ("finding_id", "item_id", "finding_row", "needs", "values_scope", "value_path", "row_label",
                "material_as_printed", "material_from", "quantity", "column", "value_as_printed", "unit",
                "unit_from", "values_from", "o2_pct_min", "o2_pct_max", "pressure_kpa_min", "pressure_kpa_max",
                "pressure_as_written", "gravity_level", "flow_cms", "fuel_phase", "material_stated_by_finding",
                "reference_id", "title", "version", "where", "url", "access")
PILE_FIELDS = ("pile", "role", "variable", "investigation_id", "placement", "o2_match", "pressure_match", "location",
               "row_kind", "state", "in_scope_tests", "counted_tests", "file_groups", "files", "bytes", "files_opened",
               "values_as_written", "pile3_ground")
INT_FIELDS = {"in_scope_tests", "counted_tests", "files", "bytes", "files_opened"}
SUMMARY_INT = ("tests_in_scope", "tests_in_scope_of_supported_investigations", "with_outcome_in_table_cell",
               "counted_tests", "in_scope_supported_with_video_two_labels", "counted_with_video_two_labels")
SCEN_INT = ("usable_tests", "tests_atmosphere", "tests_oxygen_only", "tests_pressure_only", "tests_other")
NUMBER_TOKEN = re.compile(r"[-−]?\d+(?:\.\d+)?%?")
RANGE_TOKEN = re.compile(r"(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)%?")


def stop(msg):
    sys.exit("results: " + msg)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def spec(name):
    return load(os.path.join(SPEC, name + ".json"))


def read_csv(name):
    with open(os.path.join(OUT, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def dump(obj, path):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def text(v):
    """A held value as printed: lists and objects as JSON, numbers and texts as str (as material_index.py)."""
    return json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else ("" if v is None else str(v))


def as_int(v):
    return int(v) if v not in ("", None) else 0


# ---------------------------------------------------------------- printed values
class Values:
    def __init__(self, rs):
        self.unit_rules = rs["units"]["rules"]
        self.labels = rs["row_label_fields"]

    def unit(self, key, values):
        if isinstance(values, dict) and isinstance(values.get("unit"), str):
            return values["unit"], "values.unit"
        for token, unit in self.unit_rules:
            if token in key:
                return unit, "key name (spec/results.json units)"
        return "", ""

    def flatten(self, values):
        """Every printed value of an item's 'values', in the order held, with a selector for entry rows."""
        out = []
        if not isinstance(values, dict):
            return out

        def add(sel, path, quantity, value, row_label=None, material=None, column=""):
            unit, unit_from = self.unit(quantity, values)
            out.append({"sel": sel, "path": path, "row_label": row_label or "", "material": material,
                        "quantity": quantity, "column": column, "value": text(value), "unit": unit,
                        "unit_from": unit_from})

        for key, v in values.items():
            if key in ("unit", "rounding") and "rows" in values:
                continue
            if key == "rows" and isinstance(v, list) and all(isinstance(r, dict) for r in v):
                for i, r in enumerate(v):
                    label = "; ".join("%s=%s" % (f, text(r[f])) for f in self.labels if f in r)
                    for f, x in r.items():
                        if f in self.labels:
                            continue
                        add(("row", i), "rows[%d].%s" % (i, f), f, x, label, r.get("material"))
                continue
            if isinstance(v, dict):
                cols = [k for k in v if k.startswith("columns_")]
                if len(cols) == 1 and isinstance(v[cols[0]], list):
                    ccol = cols[0]
                    for mat, series in v.items():
                        if mat == ccol or not isinstance(series, list):
                            continue
                        for j, x in enumerate(series):
                            add(("col", key, j), "%s.%s[%d]" % (key, mat, j), key, x, "material=%s" % mat, mat,
                                "%s=%s" % (ccol[len("columns_"):], text(v[ccol][j])))
                    continue
                for sub, x in v.items():
                    add(("key", key), "%s.%s" % (key, sub), "%s.%s" % (key, sub), x)
                continue
            if isinstance(v, list) and not key.endswith("_range"):
                for i, x in enumerate(v):
                    add(("idx", len(v), i), "%s[%d]" % (key, i), key, x)
                continue
            add(("key", key), key, key, v)
        return out

    @staticmethod
    def select(flat, entry_spec, values):
        """(scope, rows) for one entry of spec/findings.json; see spec/results.json values_rules.entry_rows."""
        if "column_of" in entry_spec:
            return "column_of_table", [r for r in flat if r["sel"] == ("col", entry_spec["column_of"],
                                                                        entry_spec["column_index"])]
        src = entry_spec.get("row_source")
        if src:
            m = re.fullmatch(r"rows\[(\d+)\]", src)
            if m:
                return "row_of_table", [r for r in flat if r["sel"] == ("row", int(m.group(1)))]
            m = re.fullmatch(r"([^.\[\]]+)\[(\d+)\]", src)
            if m and isinstance(values.get(m.group(1)), list):
                n, i = len(values[m.group(1)]), int(m.group(2))
                return "element_of_lists", [r for r in flat if r["sel"] == ("idx", n, i)]
            stop("row_source not understood: %s" % src)
        if "row" in entry_spec:
            return "not_split_by_row", []
        return "whole_item", list(flat)


def public_value(r, i):
    return {"id": i, "path": r["path"], "row_label": r["row_label"], "material_as_printed": r["material"],
            "quantity": r["quantity"], "column": r["column"], "value_as_printed": r["value"], "unit": r["unit"],
            "unit_from": r["unit_from"]}


# ---------------------------------------------------------------- audit
def printed_numbers(words, label_words):
    toks = (words or "").split()
    out = []
    for i, tok in enumerate(toks):
        t = tok.strip("()[]{},;:\"'“”‘’")
        t = t[:-1] if t.endswith(".") else t
        prev = toks[i - 1].strip("(") if i else ""
        if prev in label_words:
            continue
        if NUMBER_TOKEN.fullmatch(t):
            out.append(abs(float(t.rstrip("%").replace("−", "-"))))
        else:
            m = RANGE_TOKEN.fullmatch(t)
            if m:
                out += [float(m.group(1)), float(m.group(2))]
    return out


def held_numbers(v, out):
    if isinstance(v, bool) or v is None:
        return out
    if isinstance(v, (int, float)):
        out.add(round(abs(float(v)), 9))
    elif isinstance(v, str):
        out.update(round(abs(float(x)), 9) for x in re.findall(r"\d+(?:\.\d+)?", v))
    elif isinstance(v, list):
        for x in v:
            held_numbers(x, out)
    elif isinstance(v, dict):
        for k, x in v.items():
            held_numbers(x, out)
    return out


def audit(refs, findings_spec, result_items, label_words):
    tagged = {e["item"] for e in findings_spec["findings"]}
    left = findings_spec["_meta"].get("left_out", {})
    not_in_findings, numbers, added = [], [], []
    for doc in refs["references"]:
        for it in doc["items"]:
            if it["type"] == "published_result" and it["id"] not in tagged:
                not_in_findings.append({"item_id": it["id"], "document_id": doc["id"],
                                        "reason_left_out": left.get(it["id"], "")})
            if it.get("values_from"):
                added.append({"item_id": it["id"], "values_from": it["values_from"], "values": it["values"]})
            if it["type"] != "published_result" and it["id"] not in result_items:
                continue
            held = held_numbers(it.get("values"), set())
            seen, miss = set(), []
            for n in printed_numbers(it.get("text"), label_words) + printed_numbers(it.get("quote"), label_words):
                n = round(n, 9)
                if n not in held and n not in seen:
                    seen.add(n)
                    miss.append(n)
            if miss:
                numbers.append({"item_id": it["id"], "document_id": doc["id"], "type": it["type"],
                                "has_values": "values" in it, "result_finding": it["id"] in result_items,
                                "numbers_in_words_not_in_values": [int(x) if x == int(x) else x for x in miss]})
    return not_in_findings, numbers, added


# ---------------------------------------------------------------- building
def fill(template, fields):
    def plural(m):
        return m.group(2) if fields[m.group(1)] == 1 else m.group(3)
    out = re.sub(r"\[(\w+)\|([^|\]]*)\|([^|\]]*)\]", plural, template)
    return re.sub(r"\{(\w+)\}", lambda m: str(fields[m.group(1)]), out)


def check_templates(rs):
    banned = rs["forbidden_words"]
    pieces = [("headline." + k, v) for k, v in rs["headline"].items()]
    pieces += [("sentences." + k, v) for k, v in rs["sentences"].items()]
    pieces += [("labels." + k, v) for k, v in rs["labels"].items()]
    pieces += [("order_rule.text", rs["order_rule"]["text"])]
    for name, t in pieces:
        if name != "labels.no_record" and re.search(r"\d", re.sub(r"\{\w+\}|\[\w+\|", " ", t)):
            stop("digit in template %s" % name)
        for w in banned:
            if re.search(r"\b%s\b" % re.escape(w), t, re.I):
                stop("forbidden word '%s' in %s" % (w, name))


def build():
    rs, refs, needs_spec = spec("results"), spec("references"), spec("needs")
    scen_spec, process_spec, findings_spec = spec("scenarios"), spec("process"), spec("findings")
    check_templates(rs)
    fcsv = read_csv("findings.csv")
    fbe = load(os.path.join(OUT, "findings_by_environment.json"))
    psteps = load(os.path.join(OUT, "process_steps.json"))
    summary_rows = {r["need_id"]: r for r in read_csv("need_recorded_summary.csv")}
    scen_needs = {(r["scenario_id"], r["need_id"]): r for r in read_csv("scenario_needs.csv")}
    qchain = read_csv("question_chain.csv")
    qcounts = read_csv("question_chain_counts.csv")
    access_text = refs["_meta"]["access_values"]

    docs, items = {}, {}
    for d in refs["references"]:
        docs[d["id"]] = {"title": d["title"], "issuer": d["issuer"], "version": d["version"], "url": d["url"],
                         "access": d["access"]}
        for it in d["items"]:
            items[it["id"]] = (d["id"], it)
    entry_specs = {e["item"] + ("#" + str(e["row"]) if "row" in e else ""): e for e in findings_spec["findings"]}
    order = {r["finding_id"]: i for i, r in enumerate(fcsv)}
    frow = {r["finding_id"]: r for r in fcsv}
    fdict = fbe["findings"]
    vals = Values(rs)

    used_items = {}

    def item_view(iid):
        if iid not in used_items:
            did, it = items[iid]
            flat = vals.flatten(it.get("values"))
            v = {"document_id": did, "type": it["type"], "where": it["where"], "text": it["text"],
                 "quote": it.get("quote"), "printed_values": [public_value(r, i) for i, r in enumerate(flat)]}
            if it.get("values_from"):
                v["values_from"] = it["values_from"]
            if it.get("note"):
                v["item_note"] = it["note"]
            used_items[iid] = (v, flat)
        return used_items[iid]

    def source(iid):
        did, it = items[iid]
        d = docs[did]
        return {"item_id": iid, "document_id": did, "title": d["title"], "version": d["version"],
                "where": it["where"], "url": d["url"], "access": d["access"]}

    # one record per finding of kind result, criterion or caveat
    findings_out = {}
    for r in fcsv:
        if r["kind"] not in ("result", "criterion", "caveat"):
            continue
        fid, iid = r["finding_id"], r["item_id"]
        did, it = items[iid]
        if r["text"] != it["text"] or (r["quote"] or None) != (it.get("quote") or None):
            stop("%s: text or quote differs from references.json" % fid)
        iv, flat = item_view(iid)
        scope, rows = vals.select(flat, entry_specs[fid], it.get("values") or {})
        ids = [flat.index(x) for x in rows]
        f = fdict[fid]
        findings_out[fid] = {
            "item_id": iid, "row": r["row"] or None, "kind": r["kind"], "needs": r["needs"].split(";"),
            "text": r["text"], "quote": r["quote"] or None,
            "conditions": {c: r[c] for c in COND_COLS},
            "condition_words": f.get("condition_words", {}),
            "values_scope": scope,
            "printed_values": [public_value(flat[i], i) for i in ids],
        }
        if f.get("tagging_note"):
            findings_out[fid]["tagging_note"] = f["tagging_note"]

    groups = rs["order_rule"]["groups"]
    gindex = {g["id"]: i for i, g in enumerate(groups)}

    def placed_entries(env, nid, kind):
        """The findings of one kind for a need (tagged for it or for all needs), in the groups of findings_by_environment."""
        out = []
        for key, applies in ((nid, "need"), ("general", "general")):
            block = env["needs"][key]
            listed = {}
            for g in groups[:3]:
                for e in block[g["from"]]:
                    listed[e["finding_id"]] = (g["id"], e)
            moved = {m.get("finding_id"): m for m in block["other_conditions"].get("moved_for_gravity", [])
                     if isinstance(m, dict)}
            for r in fcsv:
                if r["kind"] != kind or key not in r["needs"].split(";"):
                    continue
                fid = r["finding_id"]
                g, e = listed.get(fid, ("other_conditions", None))
                ent = {"finding_id": fid, "item_id": r["item_id"], "row": r["row"] or None, "group": g,
                       "applies": applies, "names_material": bool(r["material"]),
                       "matched_on": e.get("matched_on") if e else None,
                       "not_stated": e.get("not_stated") if e else None,
                       "n_printed_values": len(findings_out[fid]["printed_values"]),
                       "source": source(r["item_id"])}
                if e and "flow" in e:
                    ent["flow"] = e["flow"]
                if fid in moved:
                    ent["moved_for_gravity"] = moved[fid]
                if r["access"] != "full_text_read":
                    ent["access_label"] = access_text[r["access"]]
                out.append(ent)
        out.sort(key=lambda x: (gindex[x["group"]], 0 if x["names_material"] else 1, x["item_id"],
                                order[x["finding_id"]]))
        return out

    def group_counts(entries):
        c = {g["id"]: sum(1 for e in entries if e["group"] == g["id"]) for g in groups}
        c.update(n=len(entries), n_tagged_for_need=sum(1 for e in entries if e["applies"] == "need"),
                 n_tagged_for_all_needs=sum(1 for e in entries if e["applies"] == "general"),
                 n_with_printed_values=sum(1 for e in entries if e["n_printed_values"]),
                 n_not_full_text=sum(1 for e in entries if e["source"]["access"] != "full_text_read"))
        return c

    def step_items(step):
        return list(step.get("items", [])) + list(step.get("measures", []))

    scenarios_out = []
    blocks_index = []
    for scen in scen_spec["scenarios"]:
        env = next(e for e in fbe["environments"] if e["id"] == scen["id"])
        has_ranges = any(v and (v.get("min") is not None or v.get("max") is not None)
                         for k, v in scen.get("ranges", {}).items() if k in ("o2_pct", "pressure_kpa"))
        nblocks = []
        for need in needs_spec["needs"]:
            nid = need["id"]
            bid = "%s__%s" % (scen["id"], nid)
            found = placed_entries(env, nid, "result")
            caveats = placed_entries(env, nid, "caveat")
            caveats_need = [e for e in caveats if e["applies"] == "need"]
            caveats_all = [e for e in caveats if e["applies"] == "general"]
            crit = placed_entries(env, nid, "criterion")
            crit_items = {e["item_id"] for e in crit}
            ties = {}
            for iid in need.get("references", []):
                ties.setdefault(iid, []).append("needs.json references")
            for step in process_spec["steps"]:
                if step["id"] in need.get("informs_process_steps", []):
                    for iid in step_items(step):
                        ties.setdefault(iid, []).append("process.json step %s" % step["id"])
            extra = []
            for iid in sorted(ties):
                if iid not in items:
                    stop("%s: item %s of needs.json or process.json not in references.json" % (bid, iid))
                if items[iid][1]["type"] in rs["criteria_item_types"] and iid not in crit_items:
                    item_view(iid)
                    did = items[iid][0]
                    ent = {"item_id": iid, "type": items[iid][1]["type"], "tied_by": ties[iid],
                           "has_quote": bool(items[iid][1].get("quote")),
                           "n_printed_values": len(used_items[iid][0]["printed_values"]), "source": source(iid)}
                    if docs[did]["access"] != "full_text_read":
                        ent["access_label"] = access_text[docs[did]["access"]]
                    extra.append(ent)
            # process
            pneed = next(n for n in psteps["needs"] if n["need_id"] == nid)
            process = {"id": bid + ".process", "label": rs["labels"]["process"], "sentence": psteps["sentence"],
                       "team_reading": pneed["team_reading"],
                       "steps": [s for s in psteps["steps"] if s["id"] in pneed["informs_process_steps"]],
                       "source": "data/pipeline/process_steps.json"}
            # recorded
            sm = summary_rows[nid]
            sn = scen_needs[(scen["id"], nid)]
            places = [r for r in qcounts if r["scenario_id"] == scen["id"] and r["need_id"] == nid
                      and r["level"] == "placement"]
            inside = next((r for r in places if r["placement"] == "inside"), None)
            chain = [r for r in qchain if r["scenario_id"] == scen["id"] and r["need_id"] == nid]
            recorded = {
                "id": bid + ".recorded", "label": rs["labels"]["recorded"], "sentence": rs["sentences"]["recorded"],
                "need": dict({k: as_int(sm[k]) for k in SUMMARY_INT},
                             investigations_supported=sm["investigations_supported"],
                             outcome_cells_by_variable=sm["outcome_cells_by_variable"], sentence=sm["sentence"]),
                "environment": dict({k: as_int(sn[k]) for k in SCEN_INT}, status=sn["status"], gaps=sn["gaps"],
                                    has_ranges=has_ranges,
                                    counted_inside_ranges=as_int(inside["counted_tests"]) if inside else 0,
                                    counted_inside_ranges_with_video_two_labels=
                                    as_int(inside["counted_with_video_two_labels_agree"]) if inside else 0,
                                    by_placement=[{"placement": r["placement"],
                                                   "in_scope_tests": as_int(r["in_scope_tests"]),
                                                   "counted_tests": as_int(r["counted_tests"]),
                                                   "counted_with_video_two_labels_agree":
                                                       as_int(r["counted_with_video_two_labels_agree"])}
                                                  for r in places]),
                "question_chain_rows_in_tables": sum(1 for r in chain if r["pile"] == "pile_1_in_tables"),
                "sources": ["data/pipeline/need_recorded_summary.csv", "data/pipeline/scenario_needs.csv",
                            "data/pipeline/question_chain_counts.csv"],
            }

            def pile_rows(piles):
                out = []
                for r in chain:
                    if r["pile"] in piles:
                        out.append({k: (as_int(r[k]) if k in INT_FIELDS and r[k] != "" else r[k]) for k in PILE_FIELDS})
                return out
            unproc = pile_rows(("pile_2_in_archive", "pile_2_lower_shelf"))
            norec = pile_rows(("pile_3_no_record",))
            grounds = {}
            for r in norec:
                grounds[r["pile3_ground"]] = grounds.get(r["pile3_ground"], 0) + 1
            unprocessed = {"id": bid + ".unprocessed", "label": rs["labels"]["unprocessed"],
                           "sentence": rs["sentences"]["unprocessed"], "lower_shelf_label": rs["labels"]["lower_shelf"],
                           "lower_shelf_sentence": rs["sentences"]["lower_shelf"],
                           "counts": {"n_rows": len(unproc),
                                      "n_rows_in_archive": sum(1 for r in unproc if r["pile"] == "pile_2_in_archive"),
                                      "n_rows_lower_shelf": sum(1 for r in unproc if r["pile"] == "pile_2_lower_shelf")},
                           "rows": unproc, "source": "data/pipeline/question_chain.csv (column pile)"}
            no_record = {"id": bid + ".no_record", "label": rs["labels"]["no_record"],
                         "sentence": rs["sentences"]["no_record"],
                         "counts": {"n_rows": len(norec), "by_ground": dict(sorted(grounds.items()))},
                         "rows": norec, "source": "data/pipeline/question_chain.csv (columns pile, pile3_ground)"}
            found_need = [e for e in found if e["applies"] == "need"]
            found_all = [e for e in found if e["applies"] == "general"]
            fc, fa = group_counts(found_need), group_counts(found_all)
            hfields = {"n_tagged": fc["n"], "n_at": fc["at_environment"],
                       "n_about": fc["about_a_stated_condition"], "n_without": fc["stated_without_these_conditions"],
                       "n_other": fc["other_conditions"], "n_with_values": fc["n_with_printed_values"],
                       "n_general_need": fa["n"], "n_general_at": fa["at_environment"],
                       "n_general_about": fa["about_a_stated_condition"],
                       "counted": recorded["environment"]["usable_tests"],
                       "inside": recorded["environment"]["counted_inside_ranges"]}
            headline = fill(rs["headline"]["results"], hfields) + " " + fill(rs["headline"]["all_questions"], hfields) + " " + fill(
                rs["headline"]["tests_ranges" if has_ranges else "tests_no_ranges"], hfields)
            block = {
                "block_id": bid, "scenario_id": scen["id"], "need_id": nid, "need": need["name"],
                "question": need["question"],
                "headline": {"text": headline, "fields": hfields},
                "found": {"id": bid + ".found", "label": rs["labels"]["found"], "sentence": rs["sentences"]["found"],
                          "printed_values_sentence": rs["sentences"]["printed_values"],
                          "all_questions_sentence": rs["sentences"]["found_all_questions"],
                          "counts": fc, "counts_tagged_for_all_questions": fa,
                          "entries": found_need, "entries_tagged_for_all_questions": found_all},
                "criteria": {"id": bid + ".criteria", "label": rs["labels"]["criteria"],
                             "sentence": rs["sentences"]["criteria"],
                             "counts": {"n_criterion_findings": len(crit), "n_items_tied_by_spec": len(extra)},
                             "criterion_findings": crit, "items_tied_by_spec": extra},
                "process": process,
                "recorded": recorded,
                "unprocessed": unprocessed,
                "no_record": no_record,
                "caveats": {"id": bid + ".caveats", "label": rs["labels"]["caveats"],
                            "sentence": rs["sentences"]["caveats"], "counts": group_counts(caveats_need),
                            "counts_tagged_for_all_questions": group_counts(caveats_all),
                            "entries": caveats_need, "entries_tagged_for_all_questions": caveats_all,
                            "scenario_caveat": scen.get("caveat")},
            }
            nblocks.append(block)
            blocks_index.append((scen["id"], nid, bid, headline))
        scenarios_out.append({"id": scen["id"], "label": scen["label"], "ranges": scen.get("ranges", {}),
                              "gravity_level": scen.get("gravity_level"), "caveat": scen.get("caveat"),
                              "needs": nblocks})

    doc = {
        "_meta": {
            "generated_by": GENERATED,
            "written_by": "python3 pipeline/results.py",
            "inputs": ["pipeline/spec/results.json", "pipeline/spec/references.json", "pipeline/spec/needs.json",
                       "pipeline/spec/scenarios.json", "pipeline/spec/process.json", "data/pipeline/findings.csv",
                       "data/pipeline/findings_by_environment.json", "data/pipeline/process_steps.json",
                       "data/pipeline/need_recorded_summary.csv", "data/pipeline/scenario_needs.csv",
                       "data/pipeline/question_chain.csv", "data/pipeline/question_chain_counts.csv"],
            "content": "For each scenario (6) and question (6), in page order: found (quoted results of NASA's "
                       "experiments), criteria, process, recorded, unprocessed, no_record, caveats; and a "
                       "headline built from counts only.",
            "shared_dictionaries": "To keep the file small, the text, quote, conditions and printed values of a "
                                   "finding are held once in 'findings' (key: finding_id) and the text, quote, place "
                                   "and printed values of an item once in 'items' (key: item_id); documents are in "
                                   "'documents' (key: document_id). Entries of the blocks refer to them by id and "
                                   "carry their source (item id, document title, version, where, url, access).",
            "order_rule": rs["order_rule"],
            "printed_values": rs["sentences"]["printed_values"],
            "values_rules": rs["values_rules"],
            "units": rs["units"]["note"],
            "access_values": access_text,
            "not_research_guidance": rs["sentences"]["not_research_guidance"],
            "team_output": "Groups, order, headlines and counts are the team's computation from the files named "
                           "in 'inputs'; they are not NASA's conclusions.",
        },
        "documents": {k: docs[k] for k in sorted({items[i][0] for i in used_items})},
        "items": {k: used_items[k][0] for k in sorted(used_items)},
        "findings": findings_out,
        "scenarios": scenarios_out,
    }
    return doc, rs, refs, findings_spec, items, docs, used_items, blocks_index


def flat_rows(doc, items, docs):
    rows = []
    for fid, f in doc["findings"].items():
        if f["kind"] != "result":
            continue
        did, it = items[f["item_id"]]
        d = docs[did]
        base = {"finding_id": fid, "item_id": f["item_id"], "finding_row": f["row"] or "",
                "needs": ";".join(f["needs"]), "values_scope": f["values_scope"],
                "values_from": it.get("values_from", ""),
                "material_stated_by_finding": f["conditions"]["material"],
                "reference_id": did, "title": d["title"], "version": d["version"], "where": it["where"],
                "url": d["url"], "access": d["access"]}
        base.update({c: f["conditions"][c] for c in COND_COLS if c != "material"})
        pv = f["printed_values"] or [None]
        for v in pv:
            r = dict(base)
            if v is None:
                r.update(value_path="", row_label="", material_as_printed=f["conditions"]["material"],
                         material_from="finding conditions" if f["conditions"]["material"] else "",
                         quantity="", column="", value_as_printed="", unit="", unit_from="")
            else:
                mat = v["material_as_printed"]
                r.update(value_path=v["path"], row_label=v["row_label"],
                         material_as_printed=mat if mat else f["conditions"]["material"],
                         material_from="values row" if mat else ("finding conditions" if f["conditions"]["material"] else ""),
                         quantity=v["quantity"], column=v["column"], value_as_printed=v["value_as_printed"],
                         unit=v["unit"], unit_from=v["unit_from"])
            rows.append(r)
    return rows


def summary(doc, flat, rs, refs, findings_spec, needs_spec):
    results = {fid: f for fid, f in doc["findings"].items() if f["kind"] == "result"}
    per_need = {}
    for n in [x["id"] for x in needs_spec["needs"]] + ["general"]:
        fs = [f for f in results.values() if n in f["needs"]]
        per_need[n] = {"results": len(fs), "with_printed_values": sum(1 for f in fs if f["printed_values"]),
                       "without_printed_values": sum(1 for f in fs if not f["printed_values"])}
    per_scen = {}
    for s in doc["scenarios"]:
        g = {}
        for b in s["needs"]:
            for e in b["found"]["entries"] + b["found"]["entries_tagged_for_all_questions"]:
                g.setdefault(e["finding_id"], e["group"])
        per_scen[s["id"]] = {grp["id"]: sum(1 for v in g.values() if v == grp["id"]) for grp in rs["order_rule"]["groups"]}
        per_scen[s["id"]]["distinct_results"] = len(g)
    per_doc = {}
    for f in results.values():
        did = doc["items"][f["item_id"]]["document_id"]
        per_doc[did] = per_doc.get(did, 0) + 1
    per_mat = {}
    for r in flat:
        m = r["material_as_printed"]
        if not m:
            continue
        e = per_mat.setdefault(m, {"results": set(), "printed_value_rows": 0})
        e["results"].add(r["finding_id"])
        e["printed_value_rows"] += 1 if r["value_as_printed"] != "" else 0
    per_mat = {k: {"results": len(v["results"]), "printed_value_rows": v["printed_value_rows"]}
               for k, v in sorted(per_mat.items())}
    result_items = {f["item_id"] for f in results.values()}
    nif, nums, added = audit(refs, findings_spec, result_items, rs["audit"]["label_words"])
    return {
        "_meta": {"generated_by": GENERATED, "written_by": "python3 pipeline/results.py",
                  "content": "Counts of the results of results_by_need.json and results_flat.csv, and the audit "
                             "of the reference items whose numbers cannot be filtered.",
                  "audit_rule": rs["audit"]["number_rule"], "added_values": rs["audit"]["added_values_topics"],
                  "team_output": "Counts are the team's computation; they are not NASA's conclusions."},
        "counts": {
            "results": len(results),
            "results_with_printed_values": sum(1 for f in results.values() if f["printed_values"]),
            "results_without_printed_values": sum(1 for f in results.values() if not f["printed_values"]),
            "printed_value_rows": sum(1 for r in flat if r["value_as_printed"] != ""),
            "flat_rows": len(flat),
            "per_need": per_need,
            "per_scenario_group": per_scen,
            "per_document": dict(sorted(per_doc.items())),
            "per_material_as_printed": per_mat,
            "values_scope": {s: sum(1 for f in results.values() if f["values_scope"] == s)
                             for s in sorted({f["values_scope"] for f in results.values()})},
        },
        "needs_without_quoted_result": [n for n in [x["id"] for x in needs_spec["needs"]] if per_need[n]["results"] == 0],
        "not_structured": {
            "published_result_items_not_in_findings": nif,
            "items_with_numbers_not_in_values": nums,
            "values_blocks_added_from_item_text": added,
        },
    }


def patch_answers(blocks_index):
    n = 0
    for sid, nid, bid, headline in blocks_index:
        path = os.path.join(ANSWERS, "%s__%s.json" % (sid, nid))
        if not os.path.exists(path):
            stop("answer file %s missing; run answers.py first" % path)
        a = load(path)
        a["results_first"] = {"file": "data/pipeline/results_by_need.json", "block_id": bid,
                              "parts": {p: "%s.%s" % (bid, p) for p in
                                        ("found", "criteria", "process", "recorded", "unprocessed", "no_record",
                                         "caveats")},
                              "headline": headline}
        dump(a, path)
        n += 1
    return n


def main():
    doc, rs, refs, findings_spec, items, docs, used_items, blocks_index = build()
    dump(doc, os.path.join(OUT, "results_by_need.json"))
    flat = flat_rows(doc, items, docs)
    with open(os.path.join(OUT, "results_flat.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, FLAT_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(flat)
    summ = summary(doc, flat, rs, refs, findings_spec, spec("needs"))
    dump(summ, os.path.join(OUT, "results_summary.json"))
    n = patch_answers(blocks_index)
    c = summ["counts"]
    print("results: %d results (%d with printed values), %d printed value rows, %d blocks, %d answer files patched"
          % (c["results"], c["results_with_printed_values"], c["printed_value_rows"], len(blocks_index), n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
