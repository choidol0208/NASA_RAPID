# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-15).
"""File-to-test links for six investigations with a two-label rule (step 3 of
docs/raw_data_design/design.md, pm request 20261115-0035 with its addenda).

Run after raw_gaps.py (python3 pipeline/file_links.py). Reads the saved PSI
listings (data/psi/file_listings/, git-ignored), the experimental tables,
tests.csv, scenario_tests.csv, spec/raw_names.json (the data role's name
rules), raw_values.csv (the FLEX test sheets read) and pm's video index
video/data/video_links.csv. Writes, in data/pipeline/:

  file_links.csv           one row per listed file of PSI-69, PSI-159, PSI-10,
                           PSI-25, PSI-99, PSI-39: labels found, link state,
                           test; video rows copied from pm's video index
  file_links_summary.json  per investigation and per scenario (tests inside)
  test_files.json          per scenario: the tests placed inside and the files
                           linked to each
  listing_snapshot.json    what the checks need of the listings (they are not
                           in the repository): per file id, name, bytes,
                           version, PSI category and folder
  video_tie_differences.csv  every video where the data role's own name tie
                           (raw_names.py, first rule that ties, one label)
                           differs from pm's video index; none is resolved

Labels (written by NASA): the identifier or test number in the file name
(the test-level name rules of spec/raw_names.json, the first that ties, and
for PSI-69 also the FLEX number 'FLEX-nnn'); the same rules on the PSI folder
path (the folder label; for PSI-69 also 'Flex-nnn' in a folder); for the FLEX
test sheets that were read, the CIR test number printed inside. A label names
the table rows whose cell it equals. Link state (one per file):
  two_labels_agree  two or more labels name one and the same row
  one_label         one label names a row (or several labels name the same
                    rows and more than one row)
  labels_disagree   labels name different rows
  id_not_in_table   the name carries a token of the form of an identifier
                    that is in no row of the table
  day_only          no label names a test; a name rule ties the file to a day
                    or session
  none              nothing of the above
FLEX rule (PSI-69): a FLEX number names the row with that 'FLEX Test #'. A
file is never linked by FLEX numbers alone: two_labels_agree needs a NASA
identifier among the agreeing labels (in the name, in the folder, inside the
file), or a folder whose test sheet was read and is tied to the same row by
its identifier and its FLEX number. Files whose agreeing labels are FLEX
numbers only stay one_label (second_label_scope says so). Files are listed one
per row; a test's file list holds the files whose NAME carries a label of it
(the count by name: 299 files for the 17 FLEX tests inside the lunar ranges).
Nothing here is a value of a test or a count of tests.csv.
"""
import collections
import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import raw_inventory  # noqa: E402
import raw_names  # noqa: E402
import flex_sheets  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "pipeline")
SPEC = os.path.join(HERE, "spec")
LISTINGS = os.path.join(ROOT, "data", "psi", "file_listings")
VIDEO_LINKS = os.path.join(ROOT, "video", "data", "video_links.csv")
INVESTIGATIONS = ["PSI-10", "PSI-25", "PSI-39", "PSI-69", "PSI-99", "PSI-159"]
STATES = ["two_labels_agree", "one_label", "labels_disagree", "id_not_in_table", "day_only", "none"]
GENERATED_BY = "AI-generated (Claude Code), 2026-11-15. Not human-reviewed."
RULE_ID = "two_label_rule_2026_11_15"
FLEX_NAME_NUMBER = re.compile(r"FLEX[-_ ]?(\d{3})(?![0-9])", re.I)
FLEX_FOLDER_NUMBER = re.compile(r"(?i)flex[-_ ](\d{3})(?![0-9])")
IDENTIFIER_LABELS = ("name_identifier", "folder_identifier", "identifier_inside_file")
BIG_KINDS = ("archive", "video")
COLS = ["investigation_id", "psi_file_id", "file_name", "psi_category", "folder", "bytes", "version", "kind",
        "name_pattern", "labels_found", "link_state", "test_id", "candidate_tests", "name_names_test",
        "second_label_scope", "rule_id", "source", "clip_kind_from_name", "transcribed"]
DIFF_COLS = ["investigation_id", "psi_file_id", "file_name", "pm_link_state", "pm_test_id", "data_role_level",
             "data_role_rule", "data_role_tests", "difference"]


def read_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def read_csv(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def write_csv(p, cols, rows):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def write_json(p, obj, indent=1):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, indent=indent, ensure_ascii=False) + "\n")


def records(inv):
    """file id -> listing record (version, subcategory) of the saved listing."""
    rows = []
    raw_inventory.walk(read_json(os.path.join(LISTINGS, inv + ".json")), [], rows)
    out = {}
    for _, rec in rows:
        out.setdefault(rec.get("id"), rec)
    return out


class Labeller:
    def __init__(self, inv, I, sheets):
        self.inv, self.I = inv, I
        self.test_rules = [r for r in I.rules if r["level"] == "test" and r["where"] == "name"]
        self.flex_rows = {}
        if inv == "PSI-69":
            for t, n, cells in I.rows:
                self.flex_rows[cells["FLEX Test #"].strip()] = (t, n)
        # PSI-69: test sheets read (identifier inside), and folders a sheet validates
        self.inside, self.valid_folder = {}, {}
        for s in sheets:
            rows = [(t, n) for t, n, c in I.rows if c.get("FLEX Identifier", "").strip() == s["identifier_in_sheet"]]
            self.inside[s["psi_file_id"]] = rows
            if s["tie_state"] == "identifier_and_number":
                self.valid_folder.setdefault(s["folder"], set()).add((flex_sheets.TABLE, s["table_row"]))

    def first_test_tie(self, text, folder, cat, kind):
        for rule, level, rows in self.I.all_ties(text, folder, cat, kind):
            if level == "test":
                return rule, rows
        return None, []

    def labels(self, f):
        L = {}
        rule, rows = self.first_test_tie(f["base"], "", f["category"], f["kind"])
        if rows:
            L["name_identifier" if self.inv != "PSI-69" or rule == "ID" else "name_test_number"] = rows
        if self.inv == "PSI-69":
            m = FLEX_NAME_NUMBER.search(f["base"])
            if m:
                r = self.flex_rows.get(str(int(m.group(1))))
                L["name_flex_number"] = [r] if r else []
        segs = [s for s in f["folder"].split("/") if s]
        for seg in reversed(segs):
            rule, rows = self.first_test_tie(seg, f["folder"], f["category"], f["kind"])
            if rows:
                L["folder_identifier"] = rows
                break
        if self.inv == "PSI-69":
            for seg in reversed(segs):
                m = FLEX_FOLDER_NUMBER.search(seg)
                if m:
                    r = self.flex_rows.get(str(int(m.group(1))))
                    L["folder_flex_number"] = [r] if r else []
                    break
        if f["file_id"] in self.inside:
            L["identifier_inside_file"] = self.inside[f["file_id"]]
        return L

    def token_not_in_table(self, f, L):
        if any(not v for v in L.values()):
            return True
        for r in self.test_rules:
            if r.get("name_must_match") and not r["name_rx"].search(f["base"]):
                continue
            if r["rx"].search(f["base"]):
                return True
        return False

    def state(self, f, day_tie):
        L = self.labels(f)
        live = {k: set(v) for k, v in L.items() if v}
        scope = ""
        if not live:
            if day_tie:
                return L, "day_only", set(), scope
            return L, ("id_not_in_table" if self.token_not_in_table(f, L) else "none"), set(), scope
        dead = [k for k, v in L.items() if not v]
        inter = set.intersection(*live.values())
        union = set.union(*live.values())
        if dead or not inter:
            return L, "labels_disagree", union, scope
        if len(live) == 1 or len(inter) > 1:
            if len(inter) > 1:
                scope = "labels name %d rows" % len(inter)
            return L, "one_label", inter, scope
        if self.inv == "PSI-69" and not (set(live) & set(IDENTIFIER_LABELS)):
            if inter <= self.valid_folder.get(f["folder"], set()):
                scope = "FLEX numbers in name and folder; the folder's test sheet is tied by its identifier"
            else:
                return L, "one_label", inter, "FLEX numbers only (name and folder); no identifier"
        return L, "two_labels_agree", inter, scope


def label_text(L, I):
    """label=test (or table row where the row is not a test of tests.csv), several joined by '+'."""
    parts = []
    for k in sorted(L):
        rows = L[k]
        names = [I.test_of.get(r) or "%s#row%d" % r for r in rows]
        parts.append("%s=%s" % (k, "+".join(names) if rows else "not_in_table"))
    return "; ".join(parts)


def main():
    if any(not os.path.exists(os.path.join(LISTINGS, i + ".json")) for i in INVESTIGATIONS):
        print("file_links: the PSI file listings are absent (data/psi/file_listings/ is git-ignored); nothing was "
              "written; the committed outputs stay as they are.")
        return 0
    spec = read_json(os.path.join(SPEC, "raw_names.json"))
    tests = read_csv(os.path.join(OUT, "tests.csv"))
    tests_by_id = {t["test_id"]: t for t in tests}
    kinds = raw_inventory.Rules(read_json(os.path.join(SPEC, "raw_kinds.json")))
    videos = read_csv(VIDEO_LINKS)
    video_by_id = {v["psi_file_id"]: v for v in videos}
    raw_values = read_csv(os.path.join(OUT, "raw_values.csv"))
    sheets = flex_sheets.compare(raw_values)
    fetched = read_json(os.path.join(LISTINGS, "_fetched.json"))
    inventory = {x["investigation_id"]: x for x in read_json(os.path.join(OUT, "raw_inventory.json"))["investigations"]}

    rows, snapshot, diffs = [], {}, []
    # the data role's own one-label tie of every video of every investigation (for the differences file)
    linked_all = raw_names.link_files(spec, tests, kinds)
    for inv in sorted(linked_all, key=raw_names.psi_key):
        I, recs = linked_all[inv]
        for f in recs:
            v = video_by_id.get(f["file_id"])
            if v is None:
                continue
            pm_test = v["link_state"] in ("two_labels_agree", "one_label", "labels_disagree")
            data_test = f["level"] == "test"
            if pm_test and data_test:
                diff = "" if [v["test_id"]] == f["tests"] else "different_tests"
            elif pm_test:
                diff = "data_role_day_only" if f["level"] == "day_or_session" else "data_role_not_tied"
            elif data_test:
                diff = "data_role_ties_a_test_pm_does_not"
            elif v["link_state"] == "day_only" and f["level"] != "day_or_session":
                diff = "pm_day_only_data_role_not_tied"
            elif v["link_state"] != "day_only" and f["level"] == "day_or_session":
                diff = "data_role_day_only_pm_not"
            else:
                diff = ""
            if diff:
                diffs.append({"investigation_id": inv, "psi_file_id": f["file_id"], "file_name": f["name"],
                              "pm_link_state": v["link_state"], "pm_test_id": v["test_id"], "data_role_level": f["level"],
                              "data_role_rule": f["rule"], "data_role_tests": "+".join(f["tests"]), "difference": diff})
    for inv in INVESTIGATIONS:
        I, recs = linked_all[inv]
        recmap = records(inv)
        my_sheets = []
        for s in sheets:
            rec = recmap.get(s["psi_file_id"]) or {}
            my_sheets.append({**s, "folder": rec.get("subcategory") or ""})
        lab = Labeller(inv, I, my_sheets if inv == "PSI-69" else [])
        snap = []
        for f in recs:
            rec = recmap.get(f["file_id"], {})
            snap.append([f["file_id"], f["name"], f["bytes"], rec.get("version"), f["category"], f["folder"]])
            v = video_by_id.get(f["file_id"])
            base = {"investigation_id": inv, "psi_file_id": f["file_id"], "file_name": f["name"], "psi_category": f["category"],
                    "folder": f["folder"], "bytes": f["bytes"], "version": rec.get("version", ""), "kind": f["kind"],
                    "name_pattern": f["pattern"], "rule_id": RULE_ID}
            if v is not None:
                lab_text = "; ".join(x for x in ("agreeing: " + v["labels_agreeing"] if v["labels_agreeing"] else "",
                                                 "against: " + v["labels_against"] if v["labels_against"] else "",
                                                 "values: " + v["labels_values"] if v["labels_values"] else "") if x)
                rows.append({**base, "labels_found": lab_text, "link_state": v["link_state"], "test_id": v["test_id"],
                             "candidate_tests": v["test_id"], "name_names_test": "",
                             "second_label_scope": v["second_label_scope"], "source": "pm video index (video/data/video_links.csv)",
                             "clip_kind_from_name": v["clip_kind_from_name"], "transcribed": v["transcribed"]})
                continue
            L, st, rws, scope = lab.state(f, f["level"] == "day_or_session")
            tids = sorted({I.test_of[r] for r in rws if r in I.test_of}, key=lambda t: (len(t), t))
            name_rows = set()
            for k in ("name_identifier", "name_test_number", "name_flex_number"):
                name_rows |= set(L.get(k) or [])
            name_tests = sorted({I.test_of[r] for r in name_rows if r in I.test_of}, key=lambda t: (len(t), t))
            rows.append({**base, "labels_found": label_text(L, I), "link_state": st,
                         "test_id": tids[0] if st in ("two_labels_agree", "one_label") and len(tids) == 1 else "",
                         "candidate_tests": "+".join(tids), "name_names_test": "+".join(name_tests),
                         "second_label_scope": scope, "source": "two-label rule (pipeline/file_links.py)",
                         "clip_kind_from_name": "", "transcribed": ""})
        info = fetched["listings"].get(inv, {})
        snapshot[inv] = {"listing_fetched_at": fetched.get("fetched_at"), "listing_bytes": info.get("bytes"),
                         "listing_sha256": info.get("sha256"), "files": len(snap),
                         "bytes": sum(x[2] or 0 for x in snap),
                         "columns": ["psi_file_id", "file_name", "bytes", "version", "psi_category", "folder"],
                         "rows": sorted(snap, key=lambda x: x[0])}
    rows.sort(key=lambda r: (raw_names.psi_key(r["investigation_id"]), r["psi_file_id"]))

    # test_files.json and the summary
    scen = read_json(os.path.join(SPEC, "scenarios.json"))["scenarios"]
    marks = read_csv(os.path.join(OUT, "scenario_tests.csv"))
    by_test = collections.defaultdict(list)
    for r in rows:
        if r["source"].startswith("pm video"):
            if r["test_id"]:
                by_test[r["test_id"]].append(r)
        else:
            for t in r["name_names_test"].split("+") if r["name_names_test"] else []:
                by_test[t].append(r)
    test_files, per_scen = {}, {}
    for s in scen:
        inside = sorted({m["test_id"] for m in marks if m["scenario_id"] == s["id"] and m["o2_match"] == "in"
                         and m["pressure_match"] == "in"}, key=lambda t: (tests_by_id[t]["investigation_id"], len(t), t))
        if not inside:
            continue
        tf, files_seen = {}, {}
        for t in inside:
            fl = sorted(by_test.get(t, []), key=lambda r: r["file_name"])
            tf[t] = {"investigation_id": tests_by_id[t]["investigation_id"], "fuel_phase": tests_by_id[t]["fuel_phase"],
                     "files": len(fl), "bytes": sum(int(r["bytes"] or 0) for r in fl),
                     "by_link_state": dict(collections.Counter(r["link_state"] for r in fl)),
                     "file_list": [{"psi_file_id": r["psi_file_id"], "file_name": r["file_name"], "bytes": int(r["bytes"] or 0),
                                    "kind": r["kind"], "link_state": r["link_state"], "labels_found": r["labels_found"]}
                                   for r in fl]}
            for r in fl:
                files_seen[r["psi_file_id"]] = r
        fs = list(files_seen.values())
        linked_invs = sorted({tests_by_id[t]["investigation_id"] for t in inside} & set(INVESTIGATIONS), key=raw_names.psi_key)
        per_scen[s["id"]] = {
            "tests_inside": len(inside),
            "tests_inside_by_investigation": dict(sorted(collections.Counter(tests_by_id[t]["investigation_id"] for t in inside).items())),
            "tests_inside_in_linked_investigations": sum(1 for t in inside if tests_by_id[t]["investigation_id"] in INVESTIGATIONS),
            "files_naming_inside_tests": len(fs), "bytes": sum(int(r["bytes"] or 0) for r in fs),
            "small_files": sum(1 for r in fs if r["kind"] not in BIG_KINDS),
            "small_bytes": sum(int(r["bytes"] or 0) for r in fs if r["kind"] not in BIG_KINDS),
            "archive_and_video_files": sum(1 for r in fs if r["kind"] in BIG_KINDS),
            "archive_and_video_bytes": sum(int(r["bytes"] or 0) for r in fs if r["kind"] in BIG_KINDS),
            "by_link_state": {st: {"files": sum(1 for r in fs if r["link_state"] == st),
                                   "bytes": sum(int(r["bytes"] or 0) for r in fs if r["link_state"] == st)} for st in STATES},
            "by_investigation": {inv: {"files": sum(1 for r in fs if r["investigation_id"] == inv),
                                       "bytes": sum(int(r["bytes"] or 0) for r in fs if r["investigation_id"] == inv)}
                                 for inv in linked_invs},
            "labels_disagree_files": [{"psi_file_id": r["psi_file_id"], "file_name": r["file_name"], "folder": r["folder"],
                                       "labels_found": r["labels_found"], "candidate_tests": r["candidate_tests"]}
                                      for r in sorted(fs, key=lambda r: r["file_name"]) if r["link_state"] == "labels_disagree"]}
        test_files[s["id"]] = tf
    arch = read_json(os.path.join(OUT, "raw_inventory.json"))["_meta"]["totals"]
    for sid, v in per_scen.items():
        v["share_of_archive_bytes"] = v["bytes"] / arch["bytes"]
    per_inv = {}
    for inv in INVESTIGATIONS:
        rs = [r for r in rows if r["investigation_id"] == inv]
        per_inv[inv] = {"files": len(rs), "bytes": sum(int(r["bytes"] or 0) for r in rs),
                        "by_link_state": {st: {"files": sum(1 for r in rs if r["link_state"] == st),
                                               "bytes": sum(int(r["bytes"] or 0) for r in rs if r["link_state"] == st)}
                                          for st in STATES},
                        "video_rows_from_pm_index": sum(1 for r in rs if r["source"].startswith("pm video")),
                        "tests_with_a_file_named": len({t for r in rs for t in (r["name_names_test"] or r["test_id"]).split("+") if t})}
    dcount = collections.Counter(d["difference"] for d in diffs)
    summary = {"_meta": {"generated_by": GENERATED_BY, "written_by": "pipeline/file_links.py", "rule_id": RULE_ID,
                         "rule": __doc__.split("Labels (written by NASA): ", 1)[1].split("\n\n")[0].replace("\n", " "),
                         "listing": "PSI file listings fetched " + str(fetched.get("fetched_at")) + " (listing_snapshot.json)",
                         "not_said": "A file that names a test is not shown to hold what a question needs. The links are "
                                     "the team's description by NASA's labels, not NASA metadata. 'Video of this test' is "
                                     "said only for two_labels_agree.",
                         "flex_rule_chosen": "by name: a FLEX file is listed for a test when its name carries the test's "
                                             "identifier or FLEX number; the folder (and, for test sheets, the identifier "
                                             "inside) is the second label; one row per file, not per file and test pair"},
               "investigations": per_inv, "scenarios": per_scen,
               "video_tie_differences": {"rows": len(diffs), "by_difference": dict(sorted(dcount.items())),
                                         "file": "data/pipeline/video_tie_differences.csv",
                                         "note": "pm's video index against the data role's own first name tie "
                                                 "(raw_names.py, test_files.csv); listed, none resolved"}}
    write_csv(os.path.join(OUT, "file_links.csv"), COLS, rows)
    write_csv(os.path.join(OUT, "video_tie_differences.csv"), DIFF_COLS, sorted(diffs, key=lambda d: (raw_names.psi_key(d["investigation_id"]), d["file_name"], d["psi_file_id"])))
    write_json(os.path.join(OUT, "file_links_summary.json"), summary)
    write_json(os.path.join(OUT, "test_files.json"), {"_meta": {"generated_by": GENERATED_BY, "written_by": "pipeline/file_links.py",
                                                               "content": "per scenario, the tests placed inside (oxygen and pressure both in) and the files whose name carries a label of the test (videos: tied to the test in pm's index)"},
                                                     "scenarios": test_files})
    with open(os.path.join(OUT, "listing_snapshot.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"_meta": {"generated_by": GENERATED_BY, "written_by": "pipeline/file_links.py",
                                      "content": "per linked investigation: the saved PSI listing's fetch time, bytes and sha256, and one row per file (id, name, bytes, version, category, folder)"},
                            "investigations": snapshot}, ensure_ascii=False, separators=(",", ":")) + "\n")
    print("file_links: %d rows; differences with the data role's video ties: %d" % (len(rows), len(diffs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
