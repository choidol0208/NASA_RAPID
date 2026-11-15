# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-15).
"""The question chain: for each scenario and fire-safety question, where every
recorded test sits (placement) and where each quantity the question needs is
(location). Step 2 of docs/raw_data_design/design.md.

Run after raw_gaps.py (python3 pipeline/question_chain.py). Reads, all in the
repository: data/pipeline/{tests,need_tests,scenario_tests,values_long,
raw_values}.csv, pipeline/spec/{needs,scenarios,raw_columns,sources,
statements,raw_names}.json, data/pipeline/{raw_inventory.json,test_files.csv}
(through raw_gaps.States) and video/data/video_links.csv (pm's video index).
Writes, in data/pipeline/:

  question_chain.csv         scenario x need x role x variable x investigation x
                             placement (with its oxygen and pressure pair) x
                             location: tests in scope and counted tests
  question_chain_counts.csv  the counts view: per scenario, need and placement
                             (and per oxygen and pressure pair) the tests in
                             scope, counted, not counted by reason, and the
                             counted tests by the best link state of a video
                             tied to them

Placement (one per scenario and test, from scenario_tests.csv, in this order):
  no_range_set                the scenario sets no oxygen and no pressure range
  outside_by_recorded_value   oxygen or pressure is recorded outside the range
  inside                      oxygen and pressure are both recorded inside
  oxygen_of_oxidizer_stream   the oxygen is that of an oxidizer stream
  cannot_be_placed_from_table oxygen or pressure is not in the table and
                              neither is recorded outside

Location (one per test and needed quantity):
  table_cell                  the test has a value in tests.csv
  raw_file_value_read         no table value; raw_values.csv holds a value read
                              from a file tied to this test (not adopted)
  raw_file_column_seen        no table value; a header for the quantity was
                              seen in an opened file of a group of the
                              investigation (spec/raw_columns.json); not read
  document_sentence           no table value; a sentence of a record or a paper
                              (sources.json documented_elsewhere)
  not_found_in_files_opened   none of the above
  video_on_screen_text        an added row (row_kind 'video'), not one of the
                              quantity locations: the BASS-II main-view
                              recordings, whose on-screen text NASA's ReadMe
                              describes; for flow_cms only

The quantity rows (row_kind 'quantity') of a scenario, need, role and variable
sum to the tests in the need's scope. Nothing read from a raw file becomes a
value of tests.csv or a count. Same inputs give the same bytes.
"""
import collections
import csv
import json
import os
import sys

import raw_gaps as RG

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = os.path.join(HERE, "spec")
OUT = os.path.join(ROOT, "data", "pipeline")
VIDEO_LINKS = os.path.join(ROOT, "video", "data", "video_links.csv")

PLACEMENTS = ["inside", "cannot_be_placed_from_table", "oxygen_of_oxidizer_stream", "outside_by_recorded_value",
              "no_range_set"]
LOCATIONS = ["table_cell", "raw_file_value_read", "raw_file_column_seen", "document_sentence",
             "not_found_in_files_opened", "video_on_screen_text"]
STATE_LOCATION = {"in_table": "table_cell", RG.COL: "raw_file_column_seen", "documented_only": "document_sentence",
                  "not_in_sampled_files": "not_found_in_files_opened"}
# which variable a row of raw_values.csv gives a value for (by extraction, and for the FLEX test
# sheets by the key as written); a row of an extraction not named here gives no location
RAW_VALUE_VARIABLE = {
    "saffire_ambient_pressure": {"*": "pressure_kpa"},
    "same_particle_size_statistics": {"*": "smoke_particle_size_um"},
    "flex_test_sheet": {"Dext (mm)": "extinction_diameter_mm", "Pressure (atm)": "pressure_kpa",
                        "O2 Mole Fraction": "o2_pct"},
}
# the BASS as-run workbook (bass_as_run_cabin_block) is read but gives no location: the file does
# not state where its oxygen and pressure were measured (code location_not_stated)
VIDEO_GROUP = {"investigation_id": "PSI-25", "label": "BASS-II main-view recordings", "variable": "flow_cms",
               "view_from_name": "main"}
VIDEO_STATES = ["two_labels_agree", "one_label", "labels_disagree"]

COLS = ["scenario_id", "need_id", "role", "variable", "investigation_id", "placement", "location",
        "column_is_or_doc", "file_groups", "files", "bytes", "in_scope_tests", "counted_tests",
        # added beyond the prototype chain_lunar_habitat.csv
        "row_kind", "o2_match", "pressure_match", "state", "table_value_basis", "differs_from_definition",
        "files_opened", "values_as_written", "related_columns_not_mapped", "related_columns_not_mapped_reasons",
        "pile", "pile3_ground"]
COUNT_COLS = ["scenario_id", "need_id", "level", "placement", "o2_match", "pressure_match", "in_scope_tests",
              "counted_tests", "not_counted_tests", "n_not_stated", "n_no_outcome", "n_required_condition_missing",
              "counted_with_video_two_labels_agree", "counted_with_video_one_label",
              "counted_with_video_labels_disagree_only", "counted_without_video",
              "in_scope_with_video_two_labels_agree", "in_scope_with_video_one_label",
              "in_scope_with_video_labels_disagree_only", "counted_main_view_files", "counted_main_view_bytes",
              "counted_main_view_files_transcribed"]


def placement(o2, p):
    if o2 == "not_specified" and p == "not_specified":
        return "no_range_set"
    if o2 == "out" or p == "out":
        return "outside_by_recorded_value"
    if o2 == "in" and p == "in":
        return "inside"
    if o2 == "not_ambient":
        return "oxygen_of_oxidizer_stream"
    return "cannot_be_placed_from_table"


def value_class(v):
    """Class of a value as written (for the FLEX test sheets)."""
    s = (v or "").strip()
    if s == "":
        return "blank"
    if s in ("-", "–", "—"):
        return "dash"
    if s.lower() == "nan":
        return "nan"
    try:
        f = float(s)
    except ValueError:
        return "text"
    return "zero" if f == 0 else "number"


def read_video_links(path=VIDEO_LINKS):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def video_best(videos):
    """Best link state of a video tied to each test (two_labels_agree, then one_label, then labels_disagree)."""
    best = {}
    for v in videos:
        t, s = v["test_id"], v["link_state"]
        if t and s in VIDEO_STATES:
            if t not in best or VIDEO_STATES.index(s) < VIDEO_STATES.index(best[t]):
                best[t] = s
    return best


def build(tests, need_tests, scen_tests, values_long, raw_values, videos, spec_dir=SPEC, out_dir=OUT):
    inputs = RG.load(spec_dir, out_dir)
    S = RG.States(inputs, tests, RG.text_empty)
    needs = inputs["needs"]
    scenarios = RG.read_json(os.path.join(spec_dir, "scenarios.json"))["scenarios"]
    raw_spec = {x["investigation_id"]: x for x in inputs["raw"]["investigations"]}
    tid = {t["test_id"]: t for t in tests}
    marks = {(r["scenario_id"], r["test_id"]): r for r in scen_tests}
    links = collections.defaultdict(dict)
    for r in need_tests:
        links[r["need_id"]][r["test_id"]] = r["objective_link"]
    constant = {(r["test_id"], r["variable"]) for r in values_long if r["source_column"] == "(constant in sources.json)"}
    # values read from raw files, per (test, variable)
    read = collections.defaultdict(list)
    for r in raw_values:
        m = RAW_VALUE_VARIABLE.get(r["extraction"])
        if not m or not r["test_id"]:
            continue
        var = m.get(" ".join(r["header_as_written"].split()), m.get("*"))
        if var:
            read[(r["test_id"], var)].append(r)
    best = video_best(videos)
    main_view = collections.defaultdict(list)
    for v in videos:
        if v["investigation"] == VIDEO_GROUP["investigation_id"] and v["view_from_name"] == VIDEO_GROUP["view_from_name"] \
                and v["test_id"] and v["link_state"] in VIDEO_STATES:
            main_view[v["test_id"]].append(v)
    group_videos = [v for v in videos if v["investigation"] == VIDEO_GROUP["investigation_id"]
                    and v["view_from_name"] == VIDEO_GROUP["view_from_name"]]
    vgroup = (len(group_videos), sum(int(v["bytes"]) for v in group_videos),
              sum(1 for v in group_videos if v["transcribed"] == "yes"))
    vlabels = inputs["names"]["investigations"][VIDEO_GROUP["investigation_id"]]["videos"]["labels_seen"]

    def location_of(t, var):
        st, kind = S.test_state(t, var)
        if st != "in_table" and read.get((t["test_id"], var)):
            return st, "raw_file_value_read"
        return st, STATE_LOCATION[st]

    def related(inv, var):
        rel = [e for e in raw_spec.get(inv, {}).get("related_columns_not_mapped", []) if e.get("for_variable") == var]
        return (" | ".join("%s [%s]" % (e["header_as_written"], e["group"]) for e in rel),
                " | ".join(e["not_mapped_because"] for e in rel))

    rows, counts = [], []
    for sc in scenarios:
        sid = sc["id"]
        grav = sc.get("gravity_level")
        for nd in needs:
            nid = nd["id"]
            phases = (nd.get("scope") or {}).get("fuel_phase")
            scope = [t for t in tests if not phases or t["fuel_phase"] in phases]
            counted = {t for t, l in links[nid].items() if l == "stated"}
            pl = {}
            for t in scope:
                m = marks[(sid, t["test_id"])]
                pl[t["test_id"]] = (placement(m["o2_match"], m["pressure_match"]), m["o2_match"], m["pressure_match"])
            all_out = bool(counted) and all(pl[t][0] == "outside_by_recorded_value" for t in counted if t in pl)
            roles = [("required", v) for v in nd["conditions_required"]] + \
                    [("useful", v) for v in nd.get("conditions_useful", [])] + [("outcome", v) for v in nd["outcomes_any"]]
            for role, var in roles:
                agg = collections.OrderedDict()
                for t in scope:
                    p, om, pm = pl[t["test_id"]]
                    st, loc = location_of(t, var)
                    basis = ""
                    if loc == "table_cell":
                        basis = "constant_in_sources_json" if (t["test_id"], var) in constant else "table_column"
                    key = (RG.inv_number(t["investigation_id"]), t["investigation_id"], PLACEMENTS.index(p), p, om, pm,
                           LOCATIONS.index(loc), loc, st, basis)
                    a = agg.setdefault(key, [0, 0, []])
                    a[0] += 1
                    a[1] += t["test_id"] in counted
                    a[2].append(t["test_id"])
                for key in sorted(agg):
                    _, inv, _, p, om, pm, _, loc, st, basis = key
                    n_scope, n_counted, ids = agg[key]
                    cell = S.cells[(inv, var)]
                    rem = cell.get("remainder") if st != "in_table" else None
                    r = {c: "" for c in COLS}
                    r.update(scenario_id=sid, need_id=nid, role=role, variable=var, investigation_id=inv, placement=p,
                             location=loc, in_scope_tests=n_scope, counted_tests=n_counted, row_kind="quantity",
                             o2_match=om, pressure_match=pm, state=st, table_value_basis=basis)
                    if rem:
                        if rem["groups"]:
                            r["file_groups"] = " | ".join(g["group"] for g in rem["groups"])
                            r["files"] = sum(g["files"] for g in rem["groups"])
                            r["bytes"] = sum(g["bytes"] or 0 for g in rem["groups"])
                        if st == RG.COL:
                            r["column_is_or_doc"] = "+".join(rem["column_is"])
                            r["differs_from_definition"] = RG.codes_text(rem["differs"])
                            if rem["all_files"]:
                                r["files_opened"] = r["files"]
                            else:
                                r["files_opened"] = len({e["sample_file"] for e in rem["entries"]})
                        elif st == "documented_only":
                            r["column_is_or_doc"] = " | ".join(rem["documented_by"])
                        elif st == "not_in_sampled_files":
                            r["files_opened"] = 0
                        r["related_columns_not_mapped"], r["related_columns_not_mapped_reasons"] = related(inv, var)
                    if loc == "raw_file_value_read":
                        rr = [x for t in ids for x in read[(t, var)]]
                        r["files_opened"] = len({x["psi_file_id"] for x in rr})
                        cls = collections.Counter()
                        for t in ids:
                            got = read[(t, var)]
                            if got[0]["extraction"] == "flex_test_sheet":
                                cls[value_class(got[0]["value"])] += 1
                            elif got[0]["n_readings"]:
                                cls["series"] += 1
                            else:
                                cls["cells"] += 1
                        r["values_as_written"] = "; ".join("%s %d" % (k, cls[k]) for k in sorted(cls))
                    # piles
                    ground = ""
                    if var == "gravity_level" and grav and loc == "table_cell" and \
                            all(tid[t]["gravity_level"] != grav for t in ids):
                        ground = "common_value"
                    elif all_out and p == "outside_by_recorded_value" and loc == "table_cell" and \
                            ((var == "o2_pct" and om == "out") or (var == "pressure_kpa" and pm == "out")):
                        ground = "all_counted_outside"
                    elif loc == "document_sentence":
                        ground = "investigation_sentence"
                    r["pile3_ground"] = ground
                    if ground in ("common_value", "all_counted_outside"):
                        r["pile"] = "pile_3_no_record"
                    elif p == "inside" or (p == "cannot_be_placed_from_table" and var in ("o2_pct", "pressure_kpa")
                                           and loc != "table_cell"):
                        if loc == "table_cell":
                            r["pile"] = "pile_1_in_tables"
                        elif loc == "not_found_in_files_opened":
                            r["pile"] = "pile_2_lower_shelf"
                        else:
                            r["pile"] = "pile_2_in_archive"
                    rows.append(r)
            # video rows: one per placement pair that holds BASS-II tests, for needs with counted BASS-II tests
            if any(tid[t]["investigation_id"] == VIDEO_GROUP["investigation_id"] for t in counted) and \
                    VIDEO_GROUP["variable"] in nd["conditions_required"] + nd.get("conditions_useful", []) + nd["outcomes_any"]:
                agg = collections.Counter()
                agg_c = collections.Counter()
                for t in scope:
                    if t["investigation_id"] != VIDEO_GROUP["investigation_id"]:
                        continue
                    k = pl[t["test_id"]]
                    agg[k] += 1
                    agg_c[k] += t["test_id"] in counted
                for (p, om, pm) in sorted(agg, key=lambda k: (PLACEMENTS.index(k[0]), k[1], k[2])):
                    r = {c: "" for c in COLS}
                    role = next(rl for rl, v in [("required", v) for v in nd["conditions_required"]] +
                                [("useful", v) for v in nd.get("conditions_useful", [])] +
                                [("outcome", v) for v in nd["outcomes_any"]] if v == VIDEO_GROUP["variable"])
                    r.update(scenario_id=sid, need_id=nid, role=role, variable=VIDEO_GROUP["variable"],
                             investigation_id=VIDEO_GROUP["investigation_id"], placement=p,
                             location="video_on_screen_text",
                             column_is_or_doc="on-screen labels seen: " + ", ".join(vlabels),
                             file_groups=VIDEO_GROUP["label"], files=vgroup[0], bytes=vgroup[1],
                             in_scope_tests=agg[(p, om, pm)], counted_tests=agg_c[(p, om, pm)], row_kind="video",
                             o2_match=om, pressure_match=pm, files_opened=vgroup[2],
                             values_as_written="transcribed %d of %d files" % (vgroup[2], vgroup[0]),
                             pile="pile_2_in_archive" if p in ("inside", "cannot_be_placed_from_table") else "")
                    rows.append(r)
            # counts view
            req = nd["conditions_required"]
            outs = nd["outcomes_any"]
            buckets = collections.OrderedDict()
            for t in scope:
                p, om, pm = pl[t["test_id"]]
                for k in (("placement", p, "", ""), ("placement_pair", p, om, pm)):
                    buckets.setdefault(k, []).append(t)
            for k in sorted(buckets, key=lambda k: (PLACEMENTS.index(k[1]), k[0] != "placement", k[2], k[3])):
                ts = buckets[k]
                c = [t for t in ts if t["test_id"] in counted]
                nc = [t for t in ts if t["test_id"] not in counted]
                ns = [t for t in nc if links[nid].get(t["test_id"]) == "not_stated"]
                rest = [t for t in nc if t["test_id"] not in links[nid]]
                has_req = [t for t in rest if all(not RG.text_empty(t.get(v)) for v in req)]
                no_out = [t for t in has_req if all(RG.text_empty(t.get(v)) for v in outs)]
                other = len(nc) - len(ns) - len(no_out)
                vb = collections.Counter(best.get(t["test_id"], "none") for t in c)
                vs = collections.Counter(best.get(t["test_id"], "none") for t in ts)
                mv = [v for t in c for v in main_view.get(t["test_id"], [])]
                counts.append({"scenario_id": sid, "need_id": nid, "level": k[0], "placement": k[1], "o2_match": k[2],
                               "pressure_match": k[3], "in_scope_tests": len(ts), "counted_tests": len(c),
                               "not_counted_tests": len(nc), "n_not_stated": len(ns), "n_no_outcome": len(no_out),
                               "n_required_condition_missing": other,
                               "counted_with_video_two_labels_agree": vb["two_labels_agree"],
                               "counted_with_video_one_label": vb["one_label"],
                               "counted_with_video_labels_disagree_only": vb["labels_disagree"],
                               "counted_without_video": vb["none"],
                               "in_scope_with_video_two_labels_agree": vs["two_labels_agree"],
                               "in_scope_with_video_one_label": vs["one_label"],
                               "in_scope_with_video_labels_disagree_only": vs["labels_disagree"],
                               "counted_main_view_files": len(mv), "counted_main_view_bytes": sum(int(v["bytes"]) for v in mv),
                               "counted_main_view_files_transcribed": sum(1 for v in mv if v["transcribed"] == "yes")})
    return rows, counts


def main():
    rd = RG.read_csv
    tests = rd(os.path.join(OUT, "tests.csv"))
    rows, counts = build(tests, rd(os.path.join(OUT, "need_tests.csv")), rd(os.path.join(OUT, "scenario_tests.csv")),
                         rd(os.path.join(OUT, "values_long.csv")), rd(os.path.join(OUT, "raw_values.csv")),
                         read_video_links())
    for name, cols, data in (("question_chain.csv", COLS, rows), ("question_chain_counts.csv", COUNT_COLS, counts)):
        RG.write_csv(os.path.join(OUT, name), cols, data)
        with open(os.path.join(OUT, name), encoding="utf-8") as f:
            bad = RG.FORBIDDEN.findall(f.read())
        if bad:
            sys.exit("question_chain: forbidden word(s) %s in %s" % (sorted(set(bad)), name))
    print("question_chain: wrote question_chain.csv (%d rows), question_chain_counts.csv (%d rows)" % (len(rows), len(counts)))


if __name__ == "__main__":
    main()
