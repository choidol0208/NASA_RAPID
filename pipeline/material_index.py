# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-15).
"""Per-material index of the tests in PSI's tables, and the per-material
values printed in the reference items.

Run after process_steps.py (python3 pipeline/material_index.py). Reads
data/pipeline/{tests,need_tests,scenario_tests,file_links}.csv and
pipeline/spec/{materials,needs,scenarios,references}.json. Writes, in
data/pipeline/:

  material_tests.csv      one row per normalised material (material_id of
                          tests.csv, from spec/materials.json) x investigation
                          x sample form (sample_geometry, sample_thickness_mm,
                          sample_width_cm, rod_diameter_mm as recorded; empty
                          where not recorded): the material as written, the
                          tests, how the name is known, n/min/max of o2_pct,
                          pressure_kpa and flow_cms, the outcome variables
                          recorded, counted tests per need, scenarios with the
                          oxygen inside / oxygen and pressure inside, and
                          videos tied by two labels
  material_published.csv  for each reference item whose 'values' hold a
                          per-material table: material as printed, quantity,
                          condition and value as printed, and a literal match
                          to a material of the index (case, spaces and hyphens
                          ignored) or 'no literal match'

Counts only; nothing is compared with anything.
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

FORM = ("sample_geometry", "sample_thickness_mm", "sample_width_cm", "rod_diameter_mm")
RANGE_VARS = ("o2_pct", "pressure_kpa", "flow_cms")
README_FLAG = "fuel_material:not_written_in_cell_named_in_readme"
ROW_ABOVE_FLAG = "fuel_material:blank_in_source_value_of_row_above_used"
# fields of a 'rows' table of references.json that are written as the condition of a row (a stated parameter)
CONDITION_FIELDS = ("flight_sample", "flight", "sample", "pressure_psia", "pressure_kpa", "o2_pct", "flow_cms",
                    "flow_direction", "length_cm", "free_volume_m3")
NO_MATCH = "no literal match"
MT_COLUMNS = (("material_id", "material_label", "fuel_phase", "investigation_id") + FORM +
              ("materials_as_written", "tests", "test_ids", "name_in_table_cell", "name_from_readme_flag",
               "name_from_row_above_flag") +
              tuple("%s_%s" % (v, s) for v in RANGE_VARS for s in ("n", "min", "max")) +
              ("outcomes_recorded",))
MP_COLUMNS = ("item_id", "document_id", "item_type", "table_shape", "table_row", "material_as_printed", "quantity",
              "condition", "value_as_printed", "normalised_material_match")


def load(name):
    with open(os.path.join(SPEC, name + ".json"), encoding="utf-8-sig") as f:
        return json.load(f)


def read_csv(name):
    with open(os.path.join(OUT, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def span(rows, var):
    vals = [(num(t[var]), t[var]) for t in rows if num(t[var]) is not None]
    if not vals:
        return 0, "", ""
    return len(vals), min(vals)[1], max(vals)[1]


def key_num(x):
    v = num(x)
    return (0, v, "") if v is not None else (1 if x else -1, 0.0, x)


def material_tests(needs, scenarios):
    tests = read_csv("tests.csv")
    mats = {m["id"]: m for m in load("materials")["materials"]}
    counted = {}
    for r in read_csv("need_tests.csv"):
        if r["objective_link"] == "stated":
            counted.setdefault(r["test_id"], set()).add(r["need_id"])
    scen = {}
    for r in read_csv("scenario_tests.csv"):
        scen.setdefault(r["test_id"], {})[r["scenario_id"]] = (r["o2_match"] == "in", r["o2_match"] == "in"
                                                                and r["pressure_match"] == "in")
    video_files = {}
    for r in read_csv("file_links.csv"):
        if r["kind"] == "video" and r["link_state"] == "two_labels_agree" and r["test_id"]:
            video_files.setdefault(r["test_id"], set()).add(r["psi_file_id"])
    outcomes = []
    for n in needs:
        outcomes += [o for o in n["outcomes_any"] if o not in outcomes]
    groups = {}
    for t in tests:
        k = (t["material_id"], t["investigation_id"]) + tuple(t[f] for f in FORM)
        groups.setdefault(k, []).append(t)
    order = lambda k: (k[0], int(k[1].split("-")[1]), k[2]) + tuple(key_num(x) for x in k[3:])
    rows = []
    for k in sorted(groups, key=order):
        g = groups[k]
        m = mats.get(k[0], {})
        row = {"material_id": k[0], "material_label": m.get("label", ""), "fuel_phase": m.get("fuel_phase", ""),
               "investigation_id": k[1]}
        row.update(dict(zip(FORM, k[2:])))
        row["materials_as_written"] = "; ".join(sorted({t["fuel_material"] for t in g}))
        row["tests"] = len(g)
        row["test_ids"] = " ".join(t["test_id"] for t in g)
        readme = sum(1 for t in g if README_FLAG in t["flags"])
        above = sum(1 for t in g if ROW_ABOVE_FLAG in t["flags"])
        row["name_in_table_cell"] = len(g) - readme - above
        row["name_from_readme_flag"] = readme
        row["name_from_row_above_flag"] = above
        for v in RANGE_VARS:
            row["%s_n" % v], row["%s_min" % v], row["%s_max" % v] = span(g, v)
        row["outcomes_recorded"] = "; ".join("%s %d" % (o, c) for o in outcomes
                                             for c in [sum(1 for t in g if t[o] != "")] if c)
        for n in needs:
            row["counted_%s" % n["id"]] = sum(1 for t in g if n["id"] in counted.get(t["test_id"], ()))
        for s in scenarios:
            row["scenario_%s_o2_in" % s["id"]] = sum(1 for t in g if scen.get(t["test_id"], {}).get(s["id"], (0, 0))[0])
            row["scenario_%s_o2_and_pressure_in" % s["id"]] = sum(
                1 for t in g if scen.get(t["test_id"], {}).get(s["id"], (0, 0))[1])
        row["tests_with_video_two_labels"] = sum(1 for t in g if t["test_id"] in video_files)
        row["videos_two_labels"] = len(set().union(*[video_files.get(t["test_id"], set()) for t in g]))
        rows.append(row)
    cols = (list(MT_COLUMNS) + ["counted_%s" % n["id"] for n in needs] +
            [c for s in scenarios for c in ("scenario_%s_o2_in" % s["id"], "scenario_%s_o2_and_pressure_in" % s["id"])] +
            ["tests_with_video_two_labels", "videos_two_labels"])
    return rows, cols


def norm_name(s):
    return re.sub(r"[\s\-]+", "", str(s)).lower()


def index_names(mt_rows):
    """Normalised name -> material_ids, from the ids, labels and aliases of materials.json and the names as written."""
    names = {}
    mats = {m["id"]: m for m in load("materials")["materials"]}
    present = {r["material_id"] for r in mt_rows}
    for mid in sorted(present):
        m = mats.get(mid, {})
        cand = [mid, m.get("label", "")] + m.get("aliases", [])
        cand += [x for r in mt_rows if r["material_id"] == mid for x in r["materials_as_written"].split("; ")]
        for c in cand:
            if c:
                names.setdefault(norm_name(c), set()).add(mid)
    return names


def text(v):
    return json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else ("" if v is None else str(v))


def published_tables():
    """Items whose 'values' hold a per-material table, found by shape:
    'rows': a list of objects with a 'material' field; or an object of one
    'columns_*' list and material keys whose lists have the same length."""
    out = []
    for doc in load("references")["references"]:
        for it in doc["items"]:
            v = it.get("values")
            if not isinstance(v, dict):
                continue
            rows = v.get("rows")
            if isinstance(rows, list) and rows and all(isinstance(r, dict) and "material" in r for r in rows):
                out.append((doc, it, "rows", rows))
                continue
            for qname, tab in v.items():
                if not isinstance(tab, dict):
                    continue
                cols = [k for k in tab if k.startswith("columns_")]
                if len(cols) == 1 and isinstance(tab[cols[0]], list):
                    mats = [k for k in tab if k != cols[0] and isinstance(tab[k], list)
                            and len(tab[k]) == len(tab[cols[0]])]
                    if mats:
                        out.append((doc, it, "material_by_column", (qname, cols[0], tab, mats)))
    return out


def material_published(mt_rows):
    names = index_names(mt_rows)
    rows = []
    for doc, it, shape, tab in published_tables():
        base = {"item_id": it["id"], "document_id": doc["id"], "item_type": it["type"], "table_shape": shape}
        if shape == "rows":
            for i, r in enumerate(tab, 1):
                mat = r["material"]
                match = "; ".join(sorted(names.get(norm_name(mat), ()))) or NO_MATCH
                cond = "; ".join("%s=%s" % (k, text(r[k])) for k in r if k in CONDITION_FIELDS)
                qs = [k for k in r if k != "material" and k not in CONDITION_FIELDS]
                for q in qs or [""]:
                    rows.append(dict(base, table_row=i, material_as_printed=mat, quantity=q, condition=cond,
                                     value_as_printed=text(r[q]) if q else "", normalised_material_match=match))
        else:
            qname, ccol, t, mats = tab
            for i, mat in enumerate(mats, 1):
                match = "; ".join(sorted(names.get(norm_name(mat), ()))) or NO_MATCH
                for c, val in zip(t[ccol], t[mat]):
                    rows.append(dict(base, table_row=i, material_as_printed=mat, quantity=qname,
                                     condition="%s=%s" % (ccol[len("columns_"):], text(c)),
                                     value_as_printed=text(val), normalised_material_match=match))
    return rows


def write(name, cols, rows):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def main():
    needs = load("needs")["needs"]
    scenarios = load("scenarios")["scenarios"]
    mt, cols = material_tests(needs, scenarios)
    write("material_tests.csv", cols, mt)
    mp = material_published(mt)
    write("material_published.csv", MP_COLUMNS, mp)
    lit = {r["material_as_printed"] for r in mp if r["normalised_material_match"] != NO_MATCH}
    print("material_index: %d rows, %d materials; published: %d rows, %d materials, %d with a literal match"
          % (len(mt), len({r["material_id"] for r in mt}), len(mp), len({r["material_as_printed"] for r in mp}), len(lit)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
