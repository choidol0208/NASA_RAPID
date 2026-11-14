# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Rebuild the video tables from a saved PSI listing and the team's test tables. No network.

Reads every video file name of PSI's combustion listings (saved table, 14 November 2026), reads the clip
words, the two labels (for every investigation with a label rule) and the day keys again from each file name
and folder with the rules in video/settings/name_rules.json, checks them against the saved reading (the
summary's 'checks' counts what was compared and lists what was taken from the saved listing), gives each
video one link state, and writes:

  video/data/video_links.csv            one row per video
  video/data/video_links_summary.json   totals, tests with a video, counts per question and scenario
  video/data/shortlist_<scenario>_<question>_main_view.csv   one per demo scenario and question with videos

Usage:
  python3 video/index_by_name.py            rebuild and write
  python3 video/index_by_name.py --verify   rebuild in memory; exit 1 on any difference from the files on disk

A tie says which NASA recording belongs to which test row, by which labels. It is not a measurement,
and nothing here reads a video byte.
"""
import argparse
import collections
import csv
import datetime
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT_RULES = os.path.join(HERE, "settings", "name_rules.json")
DEFAULT_OUT = os.path.join(HERE, "data")

LISTING_DATE = "14 November 2026"
MADE_BY = ("Built by code that an AI assistant (Claude) wrote, from PSI's file listing of " + LISTING_DATE +
           ", and the team's test tables. Checked by AI sessions; not reviewed by a person.")
NOT_SAID = ("A tie says which NASA recording belongs to which test row, by the labels shown; it is not a measurement, "
            "no value was read from any video for it, and it says nothing about what a recording shows. "
            "'Video of this test' is used only where two labels agree. A research exploration aid, not safety guidance.")
LINK_STATES = ("two_labels_agree", "one_label", "labels_disagree", "day_only", "id_not_in_table", "none")


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- inputs

def read_csv_skipping_comments(path):
    with open(path, newline="", encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    return list(csv.DictReader(lines))


def sha256(path):
    """SHA-256 of a text input with line endings normalised to LF, so that the value is the same
    in a working copy with CRLF line endings and in a fresh clone (git stores these files with LF)."""
    with open(path, "rb") as fh:
        data = fh.read()
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def load_rules(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_transcribed(repo):
    with open(os.path.join(repo, "video", "settings", "bass2.json"), encoding="utf-8") as fh:
        return {c["file"] for c in json.load(fh)["clips"]}


def load_tables(repo, rules):
    t = rules["tests_tables"]
    tests = {r["test_id"]: r for r in read_csv_skipping_comments(os.path.join(repo, t["tests"]))}
    need = collections.defaultdict(dict)
    for r in read_csv_skipping_comments(os.path.join(repo, t["need_tests"])):
        need[r["need_id"]][r["test_id"]] = r
    scen = collections.defaultdict(dict)
    for r in read_csv_skipping_comments(os.path.join(repo, t["scenario_tests"])):
        scen[r["scenario_id"]][r["test_id"]] = r
    return tests, need, scen


# ---------------------------------------------------------------- reading a name

def saved_identifiers(row):
    out = {}
    for part in (row.get("identifiers") or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def stem_of(file_name, rules):
    bare = re.sub(rules["bare_name"]["prefix_pattern"], "", file_name)
    return bare.rsplit(".", 1)[0]


def clip_words(stem, folder, rules):
    words = []
    for r in rules["clip_words"]["rules"]:
        if re.search(r["pattern"], stem) or (r.get("folder_too") and re.search(r["pattern"], folder or "")):
            words.append(r["word"])
    return words


def not_a_test_recording(row, stem, words, rules):
    nt = rules["not_a_test_recording"]
    return row.get("category") in nt["categories"] or "outreach_or_interview" in words or bool(re.search(nt["name_pattern"], stem))


def acme_codes(text, rules):
    out = []
    for m in re.finditer(rules["acme"]["testpoint_pattern"], text or ""):
        if 1 <= int(m.group("ddd")) <= 366:
            out.append(m.group("yy") + m.group("ddd") + m.group("x") + m.group("n") + (m.group("suffix") or ""))
    return out


def _rule_value(rule, stem, folder):
    text = stem if rule.get("on", "stem") == "stem" else (folder or "")
    m = (re.match if rule.get("anchored") else re.search)(rule["pattern"], text)
    if not m:
        return ""
    g = rule.get("day_of_year_group")
    if g and not 1 <= int(m.group(g)) <= 366:
        return ""
    v = rule["value"].format(m.group(0), *m.groups())
    if rule.get("minus_days"):
        v = (datetime.date.fromisoformat(v) - datetime.timedelta(days=rule["minus_days"])).isoformat()
    return v


def read_days(day_rules, lab, stem, folder, words):
    """Day keys read from the name, the folder or the labels already read; the first rule that gives a value wins."""
    days = {}
    for r in day_rules or []:
        k = r["saved_key"]
        if days.get(k) or (r.get("only_if_missing") and days.get(r["only_if_missing"])):
            continue
        if set(r.get("unless_words", [])) & set(words):
            continue
        if "from_labels" in r:
            v = next((lab[x].split(",")[0] for x in r["from_labels"] if lab.get(x)), "")
            v = v[r["take"][0]:r["take"][1]] if v else ""
        else:
            v = _rule_value(r, stem, folder)
        if v:
            days[k] = v
    return days


def read_labels(investigation, file_name, folder, rules, category=""):
    """The labels this command reads itself: name_id (identifier in the file name), folder_id (in the PSI
    folder) and, for BASS-II, gmt_day and sample; extra keys of 'also_read'; the day keys of 'day_label' and
    the start of a stream recording. Only the rule of the video's own investigation is used."""
    stem = stem_of(file_name, rules)
    words = clip_words(stem, folder, rules)
    lab = {"name_id": "", "folder_id": "", "gmt_day": "", "sample": "", "name_unreadable": False, "days": {}}
    rs = _rule_value(rules["recording_start"], stem, folder)
    if rs:
        lab["days"]["recording_start"] = rs
    if not_a_test_recording({"category": category}, stem, words, rules):
        return lab, words
    inv = rules["investigations"].get(investigation)
    if not inv:
        return lab, words
    folder = folder or ""
    leaf = folder.split("/")[-1].strip()
    if inv.get("rule") == "acme":
        nc = acme_codes(stem, rules)
        fc = acme_codes(leaf, rules) or acme_codes(folder.split("/")[-2] if folder.count("/") >= 2 else "", rules)
        lab["name_id"] = ",".join(nc)
        lab["folder_id"] = fc[0] if fc else ""
        pat = inv.get("name_unreadable_pattern")
        um = re.search(pat, file_name) if pat and not nc else None
        lab["name_unreadable"] = bool(um)
        lab["name_unreadable_text"] = re.sub(r"^udp_+", "", um.group(0)) if um else ""
        lab["days"].update(read_days(rules["acme"].get("day_label"), lab, stem, folder, words))
        return lab, words
    if "name_label" in inv:
        for nl in inv["name_label"]:
            m = re.search(nl["pattern"], stem)
            if m:
                gd = m.groupdict()
                lab["name_id"] = gd.get("test") or gd.get("testpoint") or m.group(0)
                lab["gmt_day"] = gd.get("gmt_day") or ""
                lab["sample"] = gd.get("sample") or ""
                if not lab["gmt_day"] and nl.get("also", {}).get("gmt_day"):
                    g = re.search(nl["also"]["gmt_day"], stem)
                    lab["gmt_day"] = g.group(1) if g else ""
                break
        fl = inv["folder_label"]
        m = re.search(fl["pattern"], leaf if fl["on"] == "folder_leaf" else folder)
        if m:
            gd = m.groupdict()
            lab["folder_id"] = (gd.get("test") or gd.get("testpoint") or (m.group(0) if not gd else "")) or ""
        for extra in inv.get("also_read", []):
            m = re.search(extra["pattern"], stem)
            lab[extra["label"]] = m.group(0) if m else ""
        if inv.get("upper_case"):
            lab["name_id"], lab["folder_id"] = lab["name_id"].upper(), lab["folder_id"].upper()
    lab["days"].update(read_days(inv.get("day_label"), lab, stem, folder, words))
    return lab, words


def compare_with_saved(row, lab, words, rules, compared=None):
    """Differences between this command's reading and the saved listing's reading (an empty list is a pass).
    compared, a Counter, counts per saved key the values compared where at least one side holds a value."""
    diffs = []
    compared = compared if compared is not None else collections.Counter()
    if ";".join(words) != (row.get("clip_words") or ""):
        diffs.append(("clip_words", ";".join(words), row.get("clip_words")))
    compared["clip_words"] += 1
    inv = rules["investigations"].get(row["investigation"], {})
    saved = saved_identifiers(row)
    keys = rules["acme"]["saved_keys"] if inv.get("rule") == "acme" else inv.get("saved_keys")
    for mine, theirs in (keys or {}).items():
        if lab.get(mine, "") or saved.get(theirs, ""):
            compared[theirs] += 1
        if lab.get(mine, "") != saved.get(theirs, ""):
            diffs.append((mine, lab.get(mine, ""), saved.get(theirs, "")))
    day_rules = (rules["acme"].get("day_label") if inv.get("rule") == "acme" else inv.get("day_label")) or []
    day_keys = {r["saved_key"]: r.get("compare_only_where_saved", False) for r in day_rules}
    day_keys[rules["recording_start"]["saved_key"]] = False
    for k, only_where_saved in day_keys.items():
        mine, theirs = lab["days"].get(k, ""), saved.get(k, "")
        if only_where_saved and not theirs:
            continue
        if mine or theirs:
            compared[k] += 1
            if mine != theirs:
                diffs.append((k, mine, theirs))
    return diffs


def labels_values(row, lab):
    """The two labels as read, printed for a link whose labels disagree."""
    name = lab["name_id"] or (lab.get("name_unreadable_text", "") + " (not a valid test point)" if lab.get("name_unreadable") else "")
    if lab.get("gmt_day") or lab.get("sample"):
        name += f", day {lab['gmt_day']}, sample {lab['sample']}"
    out = f"file name: {name}; folder: {lab['folder_id']}"
    if saved_identifiers(row).get("check_gmt_sample", "agree") != "agree":
        out += f"; NASA's table (as looked up in the saved listing): {row.get('notes', '')}"
    return out


# ---------------------------------------------------------------- tie and link state

def norm(s):
    return re.sub(r"[\s_]+", "", s or "").upper()


def formed_test_id_ok(row, lab, rules):
    """Where the test id can be formed from the identifier without NASA's table columns, it must match."""
    inv, tid, src = row["investigation"], row["test_id"], row.get("identifier_source") or ""
    ident = lab["folder_id"] if src.startswith("folder") else lab["name_id"]
    if inv == "PSI-25":
        return tid.upper() == ("BASS2-" + ident).upper()
    if rules["investigations"].get(inv, {}).get("rule") == "acme":
        return any(norm(tid).endswith(norm(c)) for c in (ident, re.sub(r"_\d$", "", ident)) if c)
    return True


def link_state(row, lab, rules):
    """Returns (tie_scope, link_state, labels agreeing, labels against, second label scope)."""
    scope = rules["tie_scopes"][row["tie_level"]]
    inv = row["investigation"]
    if scope == "test":
        src = row.get("identifier_source") or ""
        name_id, folder_id = lab["name_id"], lab["folder_id"]
        agree, against, scope2 = [], [], ""
        if src.startswith("folder"):
            agree.append("folder_id")
            if name_id and norm(name_id) != norm(folder_id):
                against.append("name_id")
            if lab.get("name_unreadable"):
                against.append("name_id_unreadable_or_mistyped")
        else:
            agree.append("name_id")
            if folder_id:
                if norm(folder_id) == norm(name_id):
                    agree.append("folder_id")
                elif inv == "PSI-25" and re.fullmatch(re.escape(norm(folder_id)) + "[AB]", norm(name_id)):
                    scope2 = "folder names the test number without the run letter (both runs of the sample)"
                else:
                    against.append("folder_id")
        check = saved_identifiers(row).get("check_gmt_sample", "")
        if inv == "PSI-25" and check and check != "agree":
            against.append("name_gmt_or_sample_vs_table")
        state = "labels_disagree" if against else ("two_labels_agree" if len(agree) >= 2 else "one_label")
        return scope, state, agree, against, scope2
    if scope in ("run", "day", "several_days"):
        return scope, "day_only", [], [], ""
    ids = saved_identifiers(row)
    stem = stem_of(row["file_name"], rules)
    words = (row.get("clip_words") or "").split(";")
    if not_a_test_recording(row, stem, words, rules):
        return "none", "none", [], [], ""
    useless = set(rules["identifier_keys_that_name_no_test_or_day"]["keys"])
    if any(k not in useless for k in ids):
        return "none", "id_not_in_table", [], [], ""
    return "none", "none", [], [], ""


def clip_kind(investigation, file_name, words, rules):
    stem = stem_of(file_name, rules)
    ws = set(words)
    for r in rules["clip_kinds"]["rules"]:
        if r.get("investigation") and r["investigation"] != investigation:
            continue
        hit = None
        if "words_any" in r or "name_pattern" in r:
            hit = bool(ws & set(r.get("words_any", []))) or bool(r.get("name_pattern") and re.search(r["name_pattern"], file_name))
        if "name_not_pattern" in r:
            hit = not re.search(r["name_not_pattern"], stem) if hit is None else (hit and not re.search(r["name_not_pattern"], stem))
        if hit is None or hit:
            return r["view"], r["kind"]
    raise BuildError("no clip kind rule applied to " + file_name)


def day_of(row, rules):
    inv = rules["investigations"].get(row["investigation"], {})
    key = rules["acme"]["day_key"] if inv.get("rule") == "acme" else inv.get("day_key")
    if row["investigation"] == "PSI-39":
        key = "cir_day"
    ids = saved_identifiers(row)
    for k in (key if isinstance(key, list) else [key]):
        if k and ids.get(k):
            v = ids[k]
            if k == "recording_start":
                v = v.split(" ")[0]
            return f"{k}={v}"
    return ""


def placement(srow, rules):
    o, p = srow["o2_match"], srow["pressure_match"]
    if o == "out" or p == "out":
        return "outside_by_recorded_value"
    if o == "in" and p == "in":
        return "inside"
    if o == "in" and p == "not_recorded":
        return "oxygen_inside_pressure_not_in_table"
    if o == "not_ambient":
        return "oxygen_of_oxidizer_stream"
    return "cannot_be_placed_from_table"


# ---------------------------------------------------------------- build

def index_rows(listing, tests, transcribed, rules, strict=True):
    """One output row per video. strict: stop on any difference from the saved reading."""
    out, problems, compared = [], [], collections.Counter()
    useless_keys = set(rules["identifier_keys_that_name_no_test_or_day"]["keys"])
    for row in listing:
        lab, words = read_labels(row["investigation"], row["file_name"], row.get("folder", ""), rules, row.get("category", ""))
        before = collections.Counter(compared)
        for d in compare_with_saved(row, lab, words, rules, compared):
            problems.append(f"{row['file_name']}: {d[0]} read as {d[1]!r}, saved listing has {d[2]!r}")
        keys_read_again = {k for k in compared if compared[k] > before[k]}
        scope, state, agree, against, scope2 = link_state(row, lab, rules)
        if scope == "test":
            if row["test_id"] not in tests:
                problems.append(f"{row['file_name']}: test {row['test_id']} is not a row of tests.csv")
            elif not formed_test_id_ok(row, lab, rules):
                problems.append(f"{row['file_name']}: test {row['test_id']} does not match the identifier read")
        view, kind = clip_kind(row["investigation"], row["file_name"], words, rules)
        n = row.get("candidate_test_ids_n") or "0"
        out.append({
            "investigation": row["investigation"],
            "file_name": row["file_name"],
            "bytes": int(row["bytes"]),
            "folder": row.get("folder", ""),
            "clip_kind_from_name": kind,
            "view_from_name": view,
            "tie_scope": scope,
            "link_state": state,
            "labels_agreeing": " ".join(agree),
            "labels_against": " ".join(against),
            "second_label_scope": scope2,
            "labels_values": labels_values(row, lab) if state == "labels_disagree" else "",
            "test_id": row["test_id"] if scope == "test" else "",
            "day": day_of(row, rules) if state == "day_only" else "",
            "tests_that_day": n if state == "day_only" and n != "0" else "",
            "transcribed": "yes" if row["file_name"] in transcribed else "no",
            "psi_file_id": row.get("psi_file_id", ""),
            "_day_key_read_again": state == "day_only" and day_of(row, rules).split("=")[0] in keys_read_again,
            "_identifier_read_again": state == "id_not_in_table" and any(
                k in keys_read_again for k in saved_identifiers(row) if k not in useless_keys),
        })
    if strict and problems:
        raise BuildError("the reading differs from the saved listing or the tables:\n  " + "\n  ".join(problems[:20]) +
                         (f"\n  ... {len(problems) - 20} more" if len(problems) > 20 else ""))
    return out, problems, compared


def best_states(rows, rules):
    order = {s: i for i, s in enumerate(rules["link_states"]["order_for_best"])}
    best, files_of = {}, collections.defaultdict(list)
    for r in rows:
        if r["tie_scope"] == "test":
            t = r["test_id"]
            files_of[t].append(r)
            if t not in best or order[r["link_state"]] < order[best[t]]:
                best[t] = r["link_state"]
    return best, files_of


def tally(tids, best):
    c = collections.Counter(best.get(t, "no_video_tied_to_the_test") for t in tids)
    return {"tests": len(tids), "two_labels_agree": c["two_labels_agree"], "one_label": c["one_label"],
            "labels_disagree_only": c["labels_disagree"], "no_video_tied_to_the_test": c["no_video_tied_to_the_test"]}


def files_bytes(rows):
    return {"files": len(rows), "bytes": sum(r["bytes"] for r in rows)}


def counted(need, q):
    return sorted(t for t, r in need.get(q, {}).items() if r["objective_link"] == "stated")


def shortlist_rows(tids, files_of):
    rows = [r for t in tids for r in files_of.get(t, []) if r["view_from_name"] == "main"]
    return sorted(rows, key=lambda r: (r["test_id"], r["file_name"]))


def shortlist_header(scenario, q, question, scenario_name):
    extra = ""
    if q == "D1":
        extra = (" CO and CO2 are not on the screen of these videos (NASA's table takes them from sensor readings); "
                 "a video adds nothing to this question's values.")
    return (f"# Shortlist {scenario}, {q} {question}: the main-view recordings (by the words in the file name) of the "
            f"counted tests of this question whose oxygen is inside the {scenario_name} range (pressure inside or not in "
            f"NASA's table), tied at test level. 'Main view' excludes second views, still sequences, post-burn pictures, "
            f"rack, monitor and other-camera clips; portions recorded during loss of signal stay in. {MADE_BY} "
            f"{NOT_SAID}{extra} transcribed = yes: the team copied NASA's on-screen readings from this file "
            f"(a copy of NASA's display, not a measurement and not a NASA data file).")


SHORTLIST_COLUMNS = ["test_id", "file_name", "bytes", "investigation", "clip_kind_from_name", "link_state",
                     "labels_agreeing", "labels_against", "second_label_scope", "labels_values", "transcribed", "psi_file_id"]
LINK_COLUMNS = ["investigation", "file_name", "bytes", "folder", "clip_kind_from_name", "view_from_name", "tie_scope",
                "link_state", "labels_agreeing", "labels_against", "second_label_scope", "labels_values", "test_id", "day",
                "tests_that_day", "transcribed", "psi_file_id"]


def csv_text(header_line, columns, rows):
    buf = io.StringIO()
    buf.write(header_line + "\n")
    w = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def inv_key(inv):
    return int(inv.split("-")[1])


def build(repo=REPO, rules_path=DEFAULT_RULES, listing_rows=None, tables=None, transcribed=None, strict=True):
    """Returns {file name: text} for every output file."""
    rules = load_rules(rules_path)
    listing_path = os.path.join(repo, rules["listing"]["file"])
    listing = listing_rows if listing_rows is not None else read_csv_skipping_comments(listing_path)
    tests, need, scen = tables if tables is not None else load_tables(repo, rules)
    transcribed = transcribed if transcribed is not None else load_transcribed(repo)
    rows, problems, compared = index_rows(listing, tests, transcribed, rules, strict=strict)
    best, files_of = best_states(rows, rules)

    s = collections.OrderedDict()
    s["_about"] = (MADE_BY + " Summary of video/data/video_links.csv. " + NOT_SAID +
                   " The rules are in video/settings/name_rules.json; the command is video/index_by_name.py.")
    if listing_rows is None:
        ins = [rules["listing"]["file"]] + list(rules["tests_tables"].values()) + ["video/settings/name_rules.json", "video/settings/bass2.json"]
        s["inputs_sha256"] = {p: sha256(os.path.join(repo, p)) for p in ins}
    s["totals"] = files_bytes(rows)
    saved_keys_present = collections.Counter(k for r in listing for k in saved_identifiers(r))
    s["checks"] = {
        "videos": len(rows),
        "values_read_again_and_compared_by_saved_key": dict(sorted(compared.items())),
        "differences_from_saved_reading": len(problems),
        "identifier_keys_taken_from_saved_listing_without_reading_again": dict(sorted(
            (k, n) for k, n in saved_keys_present.items() if k not in compared)),
        "day_only_videos": sum(1 for r in rows if r["link_state"] == "day_only"),
        "day_only_videos_whose_day_key_was_read_again": sum(1 for r in rows if r["_day_key_read_again"]),
        "id_not_in_table_videos": sum(1 for r in rows if r["link_state"] == "id_not_in_table"),
        "id_not_in_table_videos_whose_identifier_was_read_again": sum(1 for r in rows if r["_identifier_read_again"]),
        "taken_from_saved_listing": "which table row an identifier points to (tie_level, test_id, candidate_test_ids_n) "
                                    "and, for BASS-II, the day-and-sample check against NASA's table (check_gmt_sample)",
        "tests_named_by_test_ties_found_in_tests_csv": len({r["test_id"] for r in rows if r["tie_scope"] == "test" and r["test_id"] in tests}),
        "test_rows_in_tests_csv": len(tests),
    }
    s["by_tie_scope"] = {k: files_bytes([r for r in rows if r["tie_scope"] == k]) for k in ("test", "run", "day", "several_days", "none")}
    s["by_link_state"] = {k: dict(files_bytes([r for r in rows if r["link_state"] == k]), phrase=rules["link_states"][k]["phrase"]) for k in LINK_STATES}
    s["by_investigation"] = {}
    for inv in sorted({r["investigation"] for r in rows}, key=inv_key):
        rr = [r for r in rows if r["investigation"] == inv]
        s["by_investigation"][inv] = dict(files_bytes(rr), **{k: sum(1 for r in rr if r["link_state"] == k) for k in LINK_STATES})
    s["one_label_by_investigation_and_label"] = dict(sorted(collections.Counter(
        r["investigation"] + " " + r["labels_agreeing"] + (" (run letter)" if r["second_label_scope"] else "")
        for r in rows if r["link_state"] == "one_label").items()))
    s["labels_disagree_files"] = [{"investigation": r["investigation"], "file_name": r["file_name"], "test_id": r["test_id"],
                                   "labels_agreeing": r["labels_agreeing"], "labels_against": r["labels_against"],
                                   "labels_values": r["labels_values"]}
                                  for r in rows if r["link_state"] == "labels_disagree"]
    bc = collections.Counter(best.values())
    s["tests_with_video_by_best_link_state"] = {
        "two_labels_agree": bc["two_labels_agree"], "one_label": bc["one_label"], "labels_disagree_only": bc["labels_disagree"],
        "tests_reached_at_test_scope": len(best),
        "by_investigation": {inv: dict(sorted(collections.Counter(best[t] for t in best if tests[t]["investigation_id"] == inv).items()))
                             for inv in sorted({tests[t]["investigation_id"] for t in best}, key=inv_key)},
        "tests_with_labels_disagree_only": sorted(t for t, v in best.items() if v == "labels_disagree"),
    }
    qs = rules["questions"]
    s["counted_tests_with_video_by_question"] = {}
    for q, name in qs.items():
        tids = counted(need, q)
        e = dict(question=name, **tally(tids, best))
        e["no_video_tied_by_investigation"] = dict(sorted(collections.Counter(
            tests[t]["investigation_id"] for t in tids if t not in best).items()))
        s["counted_tests_with_video_by_question"][q] = e
    any_counted = set().union(*[set(counted(need, q)) for q in qs])
    tied_counted = [r for r in rows if r["tie_scope"] == "test" and r["test_id"] in any_counted]
    s["videos_tied_to_counted_tests"] = dict(files_bytes(tied_counted), by_investigation=dict(sorted(
        collections.Counter(r["investigation"] for r in tied_counted).items(), key=lambda kv: inv_key(kv[0]))))
    b2 = [r for r in rows if r["investigation"] == "PSI-25"]
    s["bass2_by_clip_kind"] = {}
    for (v, k), n in sorted(collections.Counter((r["view_from_name"], r["clip_kind_from_name"]) for r in b2).items()):
        rr = [r for r in b2 if (r["view_from_name"], r["clip_kind_from_name"]) == (v, k)]
        s["bass2_by_clip_kind"][f"{v}: {k}"] = dict(files_bytes(rr), tests=len({r["test_id"] for r in rr if r["test_id"]}))

    outputs = collections.OrderedDict()
    s["scenarios"] = {}
    for sc in rules["demo_scenarios"]:
        e = {"by_question_and_placement": {}, "shortlists": {}}
        for q, name in qs.items():
            tids = counted(need, q)
            if not tids:
                continue
            byp = collections.defaultdict(list)
            for t in tids:
                byp[placement(scen[sc][t], rules)].append(t)
            e["by_question_and_placement"][q] = {p: tally(ts, best) for p, ts in sorted(byp.items())}
            short = [t for t in tids if placement(scen[sc][t], rules) in rules["placement"]["shortlist_placements"]]
            srows = shortlist_rows(short, files_of)
            if srows:
                fn = f"shortlist_{sc}_{q}_main_view.csv"
                outputs[fn] = csv_text(shortlist_header(sc, q, name, rules["scenario_names"][sc]), SHORTLIST_COLUMNS, srows)
                notx = [r for r in srows if r["transcribed"] == "no"]
                e["shortlists"][q] = {
                    "file": "video/data/" + fn,
                    "counted_tests_inside_or_oxygen_inside": dict(tally(short, best), by_investigation=dict(sorted(
                        collections.Counter(tests[t]["investigation_id"] for t in short).items()))),
                    "tests_with_a_listed_file": len({r["test_id"] for r in srows}),
                    "tests_without_a_listed_file": sorted(set(short) - {r["test_id"] for r in srows}),
                    **files_bytes(srows),
                    "by_link_state": dict(sorted(collections.Counter(r["link_state"] for r in srows).items())),
                    "by_clip_kind": {k: files_bytes([r for r in srows if r["clip_kind_from_name"] == k])
                                     for k in sorted({r["clip_kind_from_name"] for r in srows})},
                    "transcribed": files_bytes([r for r in srows if r["transcribed"] == "yes"]),
                    "not_transcribed": files_bytes(notx),
                }
        inside = sorted(t for t in tests if placement(scen[sc][t], rules) == "inside")
        vids = [r for t in inside for r in files_of.get(t, [])]
        e["tests_inside_the_ranges"] = dict(
            tally(inside, best),
            by_investigation=dict(sorted(collections.Counter(tests[t]["investigation_id"] for t in inside).items())),
            counted_for_a_question=len([t for t in inside if t in any_counted]),
            counted_with_a_video=len([t for t in inside if t in any_counted and t in best]),
            videos=dict(files_bytes(vids), by_link_state={k: files_bytes([r for r in vids if r["link_state"] == k])
                                                          for k in sorted({r["link_state"] for r in vids})}),
            two_labels_agree_files=[{"test_id": r["test_id"], "file_name": r["file_name"], "bytes": r["bytes"]}
                                    for r in vids if r["link_state"] == "two_labels_agree"] if len(vids) <= 30 else "see video_links.csv",
        )
        s["scenarios"][sc] = e

    links = csv_text("# Video links: one row per video file in PSI's combustion listings. " + MADE_BY + " " + NOT_SAID +
                     " transcribed = yes: the team copied NASA's on-screen readings from this file (a copy of NASA's "
                     "display, not a measurement and not a NASA data file). Rules: video/settings/name_rules.json.",
                     LINK_COLUMNS, rows)
    result = collections.OrderedDict()
    result["video_links.csv"] = links
    result["video_links_summary.json"] = json.dumps(s, indent=1, ensure_ascii=False) + "\n"
    result.update(outputs)
    return result


# ---------------------------------------------------------------- command

def write(outputs, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for fn, text in outputs.items():
        with open(os.path.join(out_dir, fn), "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("shortlist_") and fn.endswith(".csv") and fn not in outputs:
            os.remove(os.path.join(out_dir, fn))
            print("removed stale", fn)


def verify(outputs, out_dir):
    bad = 0
    for fn, text in outputs.items():
        p = os.path.join(out_dir, fn)
        if not os.path.exists(p):
            print(f"MISSING {fn}")
            bad += 1
            continue
        with open(p, encoding="utf-8", newline="") as fh:
            disk = fh.read()
        if disk != text:
            a, b = disk.splitlines(), text.splitlines()
            i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
            print(f"DIFFERS {fn}: line {i + 1}; on disk {len(a)} lines, rebuilt {len(b)} lines")
            bad += 1
        else:
            print(f"same    {fn} ({len(text.splitlines())} lines)")
    extra = [fn for fn in sorted(os.listdir(out_dir)) if fn.startswith("shortlist_") and fn.endswith(".csv") and fn not in outputs]
    for fn in extra:
        print(f"EXTRA   {fn} (on disk, not built)")
        bad += 1
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--verify", action="store_true", help="rebuild in memory and compare with the files on disk")
    ap.add_argument("--rules", default=DEFAULT_RULES)
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args(argv)
    try:
        outputs = build(rules_path=a.rules)
    except BuildError as e:
        print("build stopped:", e, file=sys.stderr)
        return 2
    if a.verify:
        bad = verify(outputs, a.out)
        print(f"{bad} files differ" if bad else "0 differences")
        return 1 if bad else 0
    write(outputs, a.out)
    s = json.loads(outputs["video_links_summary.json"])
    print("wrote", ", ".join(outputs), "to", a.out)
    print("videos", s["totals"], "| link states", {k: v["files"] for k, v in s["by_link_state"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
