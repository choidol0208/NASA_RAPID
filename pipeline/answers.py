# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Answer files: for one environment and one need, what is known and how well.

A post-processing step. It reads the evidence packages, the cell table, the
published findings and the specs, and writes one JSON file per scenario and
need to data/pipeline/answers/, plus index.json. It computes nothing on a
published value and changes no count, status or gap: rung 1 is the block of
the evidence package, rungs 2 to 4 are lists assembled by the rules of
spec/answers.json, and every sentence is a template of that spec.

It does not import run.py, evidence.py, facts.py or findings.py.
Rebuild: python3 pipeline/run.py; python3 pipeline/findings.py;
python3 pipeline/answers.py
"""
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import process_steps  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = os.path.join(HERE, "spec")
DATA = os.path.join(ROOT, "data", "pipeline")
EVID = os.path.join(DATA, "evidence")
OUT = os.path.join(DATA, "answers")

OPS = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
}
NUM = re.compile(r"\d+(?:\.\d+)?")
TIERS = ("tests_atmosphere", "tests_oxygen_only", "tests_pressure_only")
CSV_TO_COUNT = {
    "usable_tests": "usable_tests",
    "tests_atmosphere": "atmosphere",
    "tests_oxygen_only": "oxygen_only",
    "tests_pressure_only": "pressure_only",
    "tests_other": "other",
    "tests_recorded_outside_objective": "recorded_outside_objective",
    "matched_tests_flow_in_range": "matched_flow_in_range",
    "matched_tests_flow_not_recorded": "matched_flow_not_recorded",
    "matched_tests_same_gravity": "matched_same_gravity",
    "matched_tests_co2_or_helium_added": "matched_added_gas",
}
CELL_COUNT_COLUMNS = (
    "usable_tests", "tests_atmosphere", "investigations_atmosphere",
    "tests_oxygen_only", "investigations_oxygen_only", "tests_pressure_only",
    "investigations_pressure_only", "tests_other", "investigations_other",
    "tests_recorded_outside_objective",
)
CONDITION_COLUMNS = (
    "o2_pct_min", "o2_pct_max", "pressure_kpa_min", "pressure_kpa_max",
    "pressure_as_written", "gravity_level", "flow_cms", "fuel_phase", "material",
)
LISTS = (
    ("at_environment", "at_environment"),
    ("about_a_stated_condition_of_the_environment", "about_a_stated_condition"),
    ("general", "general"),
)


def stop(message):
    sys.exit("answers.py stopped: " + message)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def rows_of(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def shown(v):
    """A number as it is written in a sentence: 30.0 -> 30, 85.8 -> 85.8."""
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def numbers(text):
    return {float(n) for n in NUM.findall(text)}


def numbers_of(obj, into=None):
    """Every number of a block: numeric leaves and the numbers inside its strings and keys."""
    into = set() if into is None else into
    if isinstance(obj, bool) or obj is None:
        return into
    if isinstance(obj, (int, float)):
        into.add(float(abs(obj)))
    elif isinstance(obj, str):
        into |= numbers(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            into |= numbers(str(k))
            numbers_of(v, into)
    elif isinstance(obj, list):
        for v in obj:
            numbers_of(v, into)
    return into


class Texts:
    """The templates of spec/answers.json. No sentence is written in the code."""

    def __init__(self, spec):
        self.spec = spec
        self.words = [w.lower() for w in spec["forbidden_words"]]
        self._check_templates(spec, "answers.json")

    def _check_templates(self, node, where):
        # every template string of the spec: no digit, no forbidden word
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("_meta", "file_meta", "index_meta", "forbidden_words", "searches",
                         "placement", "near", "not_covered", "rule", "id", "when"):
                    continue
                self._check_templates(v, where + "." + k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                self._check_templates(v, "%s[%d]" % (where, i))
        elif isinstance(node, str):
            if NUM.search(re.sub(r"\{\w+\}|\[\w+\|", "", node)):
                stop("template %s holds a digit: %r" % (where, node))
            self.banned(node, where)

    def banned(self, text, where, exempt=()):
        low = text.lower()
        for e in exempt:
            low = low.replace(e.lower(), " ")
        for w in self.words:
            if re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(w), low):
                stop("forbidden word %r in %s: %r" % (w, where, text))

    def fill(self, text, fields, where, exempt=()):
        def plural(m):
            name, one, many = m.group(1), m.group(2), m.group(3)
            if name not in fields:
                stop("unknown placeholder [%s|..] in %s" % (name, where))
            return one if fields[name] == 1 else many

        def value(m):
            name = m.group(1)
            if name not in fields or fields[name] is None:
                stop("unknown or empty placeholder {%s} in %s" % (name, where))
            return shown(fields[name])

        out = re.sub(r"\[(\w+)\|([^|\]]*)\|([^\]]*)\]", plural, text)
        out = re.sub(r"\{(\w+)\}", value, out)
        self.banned(out, where, exempt)
        return out

    def holds(self, when, fields, where):
        for name, op, value in when:
            if name not in fields:
                stop("unknown field %r in a condition of %s" % (name, where))
            if op not in OPS:
                stop("unknown operator %r in %s" % (op, where))
            if not OPS[op](fields[name], value):
                return False
        return True

    def section(self, name, fields, exempt=()):
        out = []
        for t in self.spec["sentences"][name]:
            where = "sentences.%s.%s" % (name, t["id"])
            if self.holds(t["when"], fields, where):
                out.append({"id": t["id"], "text": self.fill(t["text"], fields, where, exempt)})
        return out

    def first(self, rules, fields, where, exempt=()):
        for t in rules:
            if self.holds(t["when"], fields, where + "." + t["id"]):
                return t["id"], self.fill(t["text"], fields, where + "." + t["id"], exempt)
        stop("no rule of %s holds for %r" % (where, fields))


# ---------------------------------------------------------------- near cells

def intersects(a, b):
    """Two ranges {min, max, min_inclusive, max_inclusive} share at least one value."""
    lo = [(r["min"], r["min_inclusive"]) for r in (a, b) if r["min"] is not None]
    hi = [(r["max"], r["max_inclusive"]) for r in (a, b) if r["max"] is not None]
    if not lo or not hi:
        return True
    low = max(v for v, _ in lo)
    high = min(v for v, _ in hi)
    if low < high:
        return True
    if low > high:
        return False
    return all(inc for v, inc in lo if v == low) and all(inc for v, inc in hi if v == high)


def range_words(texts, dim, r, where):
    forms = texts.spec["range_words"][dim]
    if r["min"] is not None and r["max"] is not None:
        key = "both_max_inclusive" if r["max_inclusive"] else "both_max_exclusive"
    elif r["max"] is not None:
        key = "max_only_inclusive" if r["max_inclusive"] else "max_only_exclusive"
    elif r["min"] is not None:
        key = "min_only"
    else:
        stop("range without a bound in %s" % where)
    return texts.fill(forms[key], {"min": r["min"], "max": r["max"]}, where)


def cells_of(env, cov):
    """(scenario cells, candidates with the dimension they differ in), in bin order."""
    o2_bins = cov["dimensions"]["o2_pct"]["bins"]
    p_bins = cov["dimensions"]["pressure_kpa"]["bins"]
    ro, rp = env["ranges"].get("o2_pct"), env["ranges"].get("pressure_kpa")
    if not ro or not rp:
        return None, []
    own = [(i, j) for i, bo in enumerate(o2_bins) for j, bp in enumerate(p_bins)
           if intersects(ro, bo) and intersects(rp, bp)]
    cand = []
    for i in range(len(o2_bins)):
        for j in range(len(p_bins)):
            if (i, j) in own:
                continue
            by_o2 = any(b == j and abs(a - i) == 1 for a, b in own)
            by_p = any(a == i and abs(b - j) == 1 for a, b in own)
            if by_o2 and by_p:
                stop("cell %d,%d is one step away in both dimensions for %s" % (i, j, env["id"]))
            if by_o2 or by_p:
                cand.append((i, j, "oxygen" if by_o2 else "pressure"))
    return own, cand


# ---------------------------------------------------------------- findings

def finding_entry(fid, listed, list_name, applies, csv_row, full, ref_items):
    item = ref_items.get(csv_row["item_id"])
    if item is None:
        stop("finding %s: item %s is not in references.json" % (fid, csv_row["item_id"]))
    for key in ("text", "quote"):
        if (item.get(key) or "") != csv_row[key]:
            stop("finding %s: %s differs from references.json" % (fid, key))
    cond = {}
    for c in CONDITION_COLUMNS:
        v = csv_row[c]
        if v == "":
            cond[c] = None
        elif c.endswith(("_min", "_max")):
            cond[c] = float(v)
        else:
            cond[c] = v
    e = {
        "finding_id": fid,
        "item_id": csv_row["item_id"],
        "row": csv_row["row"] or None,
        "kind": csv_row["kind"],
        "applies": applies,
        "list": list_name,
        "text": csv_row["text"],
        "quote": csv_row["quote"] or None,
        "where": csv_row["where"],
        "reference_id": csv_row["reference_id"],
        "title": csv_row["title"],
        "version": csv_row["version"],
        "access": csv_row["access"],
        "url": csv_row["url"],
        "conditions": cond,
        "matched_on": listed.get("matched_on", {}),
        "not_stated": listed.get("not_stated", []),
    }
    if "states_conditions_in_words" in listed:
        e["states_conditions_in_words"] = listed["states_conditions_in_words"]
    for key in ("condition_words", "row_values", "item_note", "tagging_note"):
        if key in full:
            e[key] = full[key]
    return e


def order(entries):
    return sorted(entries, key=lambda e: (e["reference_id"], e["item_id"], e["row"] or ""))


def place(sid, nid, fenv, findings_csv, findings_full, ref_items, rule):
    """Every listed entry of the need and of 'general', placed once by its kind."""
    out = {"criteria": [], "nasa_questions": [], "stated_open_elsewhere": [],
           "at_environment": [], "about_a_stated_condition": [], "general": []}
    seen = set()
    nasa_refs = set(rule["nasa_questions"]["reference_ids"])
    n_expected = 0
    for key, applies in ((nid, "need"), ("general", "general")):
        block = fenv["needs"][key]
        for src, name in LISTS:
            for listed in block[src]:
                n_expected += 1
                fid = listed["finding_id"]
                if fid in seen:
                    stop("%s %s: finding %s is listed twice" % (sid, nid, fid))
                seen.add(fid)
                if fid not in findings_csv or fid not in findings_full:
                    stop("finding %s is not in findings.csv or in the findings list" % fid)
                e = finding_entry(fid, listed, src, applies, findings_csv[fid],
                                  findings_full[fid], ref_items)
                if e["kind"] == "criterion":
                    out["criteria"].append(e)
                elif e["kind"] == "gap":
                    if e["quote"] and e["reference_id"] in nasa_refs:
                        out["nasa_questions"].append(e)
                    else:
                        out["stated_open_elsewhere"].append(e)
                elif e["kind"] in ("result", "caveat"):
                    out[name].append(e)
                else:
                    stop("finding %s has kind %r with no place" % (fid, e["kind"]))
    if sum(len(v) for v in out.values()) != n_expected:
        stop("%s %s: placed entries do not add up" % (sid, nid))
    return {k: order(v) for k, v in out.items()}


def ids_of(entries):
    return [e["finding_id"] for e in entries]


# ---------------------------------------------------------------- one answer

def build_answer(sid, nid, ctx):
    texts, spec = ctx["texts"], ctx["spec"]
    pkg = ctx["scenario_pkg"][sid]
    env_in = pkg["environment"]
    block = next(b for b in pkg["needs"] if b["need_id"] == nid)
    need_spec = ctx["needs"][nid]
    pkg_file = "data/pipeline/evidence/scenario_%s.json" % sid
    pkg_key = "%s#needs.%s" % (pkg_file, nid)
    exempt = (block["need"],)
    sentences = []

    def add(rung, items, sources):
        for s in items:
            src = s.pop("sources", None)
            sentences.append({"rung": rung, "id": s["id"], "text": s["text"],
                              "sources": src if src is not None else sources})

    environment = {k: env_in.get(k) for k in ("id", "label", "ranges", "gravity_level", "caveat")}
    need = {"need_id": nid, "need": block["need"], "pillar": block["pillar"],
            "question": need_spec["question"], "reading": block["reading"]}

    # rung 1: the block of the evidence package, checked against scenario_needs.csv
    row = ctx["scenario_rows"][(sid, nid)]
    if row["status"] != block["status"]:
        stop("%s %s: status differs from scenario_needs.csv" % (sid, nid))
    for col, name in CSV_TO_COUNT.items():
        if int(row[col]) != block["counts"][name]:
            stop("%s %s: count %s differs from scenario_needs.csv" % (sid, nid, name))
    if [g for g in row["gaps"].split(";") if g] != [g["code"] for g in block["gaps"]]:
        stop("%s %s: gap codes differ from scenario_needs.csv" % (sid, nid))
    matched_ids = sorted(t["test_id"] for t in block["matched_tests"])
    c = block["counts"]
    if len(matched_ids) != c["atmosphere"] + c["oxygen_only"] + c["pressure_only"]:
        stop("%s %s: matched tests do not add up to the tier counts" % (sid, nid))
    cp = spec["rung1"]["copied_statements"]
    copied = [s for s in block["statements"]
              if s["id"] in cp["ids"] or any(s["id"].startswith(p) for p in cp["prefixes"])]
    r1_sent = []
    for s in copied:
        src = ["%s.statements.%s" % (pkg_key, s["id"])]
        if s["id"] == "documented.elsewhere":
            src += [d["said_in"] for d in block["documented_elsewhere"]
                    if d["source_id"] == s.get("source_id") and d["variable"] == s.get("variable")]
        r1_sent.append({"id": s["id"], "text": s["text"], "sources": src})
    rung1 = {
        "status": block["status"],
        "counts": block["counts"],
        "matched": len(matched_ids),
        "matched_ranges": block["matched_ranges"],
        "matched_by_fuel_phase": block["matched_by_fuel_phase"],
        "investigations": block["investigations"],
        "documented_elsewhere": block["documented_elsewhere"],
        "indicators": [{"id": i["indicator_id"], "label": i["label"], "group": i["group"],
                        "values": i["values"], "n_tests": i["n_tests"], "reading": i["reading"]}
                       for i in block["indicators"]],
        "source": pkg_file,
        "sentences": [{"id": s["id"], "text": s["text"]} for s in r1_sent],
    }

    # findings, placed once
    placed = place(sid, nid, ctx["findings_env"][sid], ctx["findings_csv"],
                   ctx["findings_full"], ctx["ref_items"], spec["placement"])
    f_key = "data/pipeline/findings_by_environment.json#environments.%s.needs.%s" % (sid, nid)
    f_src = [f_key, f_key.rsplit(".", 1)[0] + ".general"]

    # frame
    crit = placed["criteria"]
    frame_counts = {
        "n_criteria": len(crit),
        "n_criteria_at": sum(1 for e in crit if e["list"] == "at_environment"),
        "n_criteria_about": sum(1 for e in crit if e["list"] == "about_a_stated_condition_of_the_environment"),
        "n_criteria_general": sum(1 for e in crit if e["list"] == "general"),
        "n_nasa_questions": len(placed["nasa_questions"]),
    }
    frame_sent = texts.section("frame", frame_counts, exempt)
    frame = {"counts": frame_counts, "criteria": crit,
             "nasa_questions": placed["nasa_questions"], "sentences": frame_sent}

    # rung 2
    own, cand = ctx["cells"][sid]
    cov = ctx["coverage"]
    o2_bins = cov["dimensions"]["o2_pct"]["bins"]
    p_bins = cov["dimensions"]["pressure_kpa"]["bins"]
    cells = []
    env_words = None
    if own is not None:
        env_words = {
            "o2_pct": range_words(texts, "o2_pct", environment["ranges"]["o2_pct"], sid),
            "pressure_kpa": range_words(texts, "pressure_kpa",
                                        environment["ranges"]["pressure_kpa"], sid),
        }
    for i, j, dim in cand:
        bo, bp = o2_bins[i], p_bins[j]
        cid = "cell_%s__%s" % (bo["id"], bp["id"])
        crow = ctx["cell_rows"][(cid, nid)]
        if sum(int(crow[t]) for t in TIERS) < 1:
            continue
        cblock = next(b for b in ctx["cell_pkg"][cid]["needs"] if b["need_id"] == nid)
        if cblock["status"] != crow["status"]:
            stop("%s %s: status differs from atmosphere_cells.csv" % (cid, nid))
        cell_ids = {t["test_id"] for t in cblock["matched_tests"]}
        if len(cell_ids) != sum(int(crow[t]) for t in TIERS):
            stop("%s %s: matched tests do not add up to atmosphere_cells.csv" % (cid, nid))
        counts = {k: (int(crow[k]) if not k.startswith("investigations") else crow[k])
                  for k in CELL_COUNT_COLUMNS}
        cell = {
            "cell_id": cid,
            "o2_bin": bo["id"], "o2_bin_label": bo["label"],
            "pressure_bin": bp["id"], "pressure_bin_label": bp["label"],
            "differs_in": dim,
            "status": crow["status"],
            "counts": counts,
            "matched": len(cell_ids),
            "also_matched_at_the_condition": len(cell_ids & set(matched_ids)),
            "matched_ranges": cblock["matched_ranges"],
            "source": "data/pipeline/evidence/%s.json" % cid,
        }
        fields = dict(counts, matched=cell["matched"],
                      also_matched_at_the_condition=cell["also_matched_at_the_condition"],
                      o2_bin_label=bo["label"], pressure_bin_label=bp["label"],
                      env_o2_words=env_words["o2_pct"],
                      env_pressure_words=env_words["pressure_kpa"])
        cs = spec["sentences"]["cell"]
        cell["differs"] = texts.fill(cs["differs_" + dim], fields, "cell.differs", exempt)
        cell["recorded"] = texts.fill(cs["recorded"], fields, "cell.recorded", exempt)
        cells.append(cell)
    r2_counts = {
        "has_ranges": own is not None,
        "n_scenario_cells": len(own or []),
        "n_candidates": len(cand),
        "n_cells": len(cells),
        "n_cells_with_repeating_tier": sum(
            1 for x in cells
            if x["counts"]["tests_oxygen_only"] or x["counts"]["tests_pressure_only"]),
    }
    r2_sent = texts.section("rung2", r2_counts, exempt)
    rung2 = {
        "counts": r2_counts,
        "environment_words": env_words,
        "scenario_cells": ["cell_%s__%s" % (o2_bins[i]["id"], p_bins[j]["id"])
                           for i, j in (own or [])],
        "candidate_cells": ["cell_%s__%s" % (o2_bins[i]["id"], p_bins[j]["id"])
                            for i, j, _ in cand],
        "cells": cells,
        "sentences": r2_sent,
    }

    # rung 3
    r3_lists = (placed["at_environment"], placed["about_a_stated_condition"], placed["general"])
    r3_all = [e for part in r3_lists for e in part]
    r3_counts = {
        "n_at": len(r3_lists[0]), "n_about": len(r3_lists[1]), "n_general": len(r3_lists[2]),
        "n_listed": len(r3_all),
        "n_not_full_text": sum(1 for e in r3_all if e["access"] != "full_text_read"),
    }
    r3_sent = texts.section("rung3", r3_counts, exempt)
    rung3 = {"counts": r3_counts,
             "at_the_environment": r3_lists[0],
             "about_a_stated_condition": r3_lists[1],
             "stated_without_these_conditions": r3_lists[2],
             "sentences": r3_sent}

    # rung 4
    searches = [s for s in spec["searches"] if nid in s["needs"]]
    not_covered = [dict(x, applies="general") for x in ctx["not_covered"]]
    r4_counts = {"n_gaps": len(block["gaps"]),
                 "n_stated_open_elsewhere": len(placed["stated_open_elsewhere"]),
                 "n_not_covered": len(not_covered), "n_searches": len(searches)}
    head = texts.section("rung4", r4_counts, exempt)
    gap_sent = []
    for g in block["gaps"]:
        st = [s for s in block["statements"] if s["id"].startswith("gap.") and s["text"] == g["text"]]
        if len(st) != 1:
            stop("%s %s: gap %s has no single sentence in the package" % (sid, nid, g["code"]))
        gap_sent.append({"id": st[0]["id"], "text": g["text"],
                         "sources": ["%s.gaps.%s" % (pkg_key, g["code"])]})
    search_sent = [{"id": "rung4.search",
                    "text": texts.fill(spec["sentences"]["search"], s, "sentences.search", exempt),
                    "sources": ["pipeline/spec/answers.json#searches"]} for s in searches]
    r4_sent = head[:1] + gap_sent + head[1:] + search_sent
    rung4 = {"counts": r4_counts,
             "gaps": [{"code": g["code"], "text": g["text"]} for g in block["gaps"]],
             "stated_open_elsewhere": placed["stated_open_elsewhere"],
             "not_covered": not_covered,
             "searches": searches,
             "sentences": [{"id": s["id"], "text": s["text"]} for s in r4_sent]}

    # top line
    tf = {"status": block["status"], "usable_tests": c["usable_tests"],
          "atmosphere": c["atmosphere"], "oxygen_only": c["oxygen_only"],
          "pressure_only": c["pressure_only"], "matched": len(matched_ids),
          "n_near_cells": len(cells), "n_at": r3_counts["n_at"], "n_about": r3_counts["n_about"],
          "n_published_here": len(r3_lists[0]) + len(r3_lists[1])}
    tl = spec["top_line"]
    id_a, text_a = texts.first(tl["tests"], tf, "top_line.tests", exempt)
    id_b, text_b = texts.first(tl["published"], tf, "top_line.published", exempt)
    top = {"id": id_a + "+" + id_b, "text": " ".join([tl["start"], text_a, text_b]), "fields": tf}
    if not top["text"].startswith("Not judged here."):
        stop("top line does not start with the fixed words")
    texts.banned(top["text"], "top line of %s %s" % (sid, nid), exempt)

    # all sentences, in reading order
    add("top", [{"id": top["id"], "text": top["text"]}], ["#top_line.fields"])
    add("frame", [dict(s) for s in frame_sent], f_src)
    add("1", r1_sent, [pkg_key])
    r2_all = [dict(s) for s in r2_sent]
    for x in cells:
        r2_all.append({"id": "rung2.cell.differs", "text": x["differs"], "cell_id": x["cell_id"],
                       "sources": ["pipeline/spec/coverage.json", "%s#environment.ranges" % pkg_file]})
        r2_all.append({"id": "rung2.cell.recorded", "text": x["recorded"], "cell_id": x["cell_id"],
                       "sources": ["data/pipeline/atmosphere_cells.csv#%s,%s" % (x["cell_id"], nid),
                                   "%s#needs.%s.matched_tests" % (x["source"], nid)]})
    add("2", r2_all, ["pipeline/spec/coverage.json", "data/pipeline/atmosphere_cells.csv"])
    add("3", [dict(s) for s in r3_sent], f_src)
    add("4", r4_sent, [pkg_key, "pipeline/spec/needs.json#_meta.not_covered"] + f_src)

    answer = {
        "_meta": spec["file_meta"],
        "environment": environment,
        "need": need,
        "top_line": top,
        "frame": frame,
        "rung1_recorded_at_the_condition": rung1,
        "rung2_recorded_near_the_condition": rung2,
        "rung3_published": rung3,
        "rung4_not_known": rung4,
        "sentences": sentences,
    }
    verify_numbers(answer, "%s__%s" % (sid, nid))
    answer["process"] = process_steps.process_view(nid)   # added 2026-11-15 (pipeline/spec/process.json)
    return answer


RUNG_BLOCK = {"frame": "frame", "1": "rung1_recorded_at_the_condition",
              "2": "rung2_recorded_near_the_condition", "3": "rung3_published",
              "4": "rung4_not_known", "top": "top_line"}


def verify_numbers(answer, name):
    """Every number of a sentence is found in the block the sentence was built from."""
    for s in answer["sentences"]:
        block = answer[RUNG_BLOCK[s["rung"]]]
        if s["rung"] == "top":
            block = block["fields"]
        else:
            # the block without its own sentences, so a sentence cannot vouch for itself
            block = {k: v for k, v in block.items() if k != "sentences"}
            if s["rung"] == "2":
                block = dict(block, cells=[{k: v for k, v in x.items()
                                            if k not in ("differs", "recorded")}
                                           for x in block["cells"]])
        allowed = numbers_of(block)
        if s["rung"] in ("1", "2"):
            allowed |= numbers_of(answer["environment"])
        missing = numbers(s["text"]) - allowed
        if missing:
            stop("%s: sentence %s holds numbers %s that are not in its block: %r"
                 % (name, s["id"], sorted(missing), s["text"]))
    # the fields of the top line are those of the rungs
    tf = answer["top_line"]["fields"]
    r1 = answer["rung1_recorded_at_the_condition"]
    r3 = answer["rung3_published"]
    same = (tf["status"] == r1["status"]
            and all(tf[k] == r1["counts"][k]
                    for k in ("usable_tests", "atmosphere", "oxygen_only", "pressure_only"))
            and tf["matched"] == r1["matched"]
            and tf["n_near_cells"] == len(answer["rung2_recorded_near_the_condition"]["cells"])
            and tf["n_at"] == len(r3["at_the_environment"])
            and tf["n_about"] == len(r3["about_a_stated_condition"])
            and tf["n_published_here"] == tf["n_at"] + tf["n_about"])
    if not same:
        stop("%s: the fields of the top line differ from the rungs" % name)


def dump(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def build():
    spec = load(os.path.join(SPEC, "answers.json"))
    texts = Texts(spec)
    for s in spec["searches"]:
        for k in ("what", "where", "result", "when", "by"):
            texts.banned(s[k], "searches." + k)
    needs_spec = load(os.path.join(SPEC, "needs.json"))
    scen_spec = load(os.path.join(SPEC, "scenarios.json"))
    cov = load(os.path.join(SPEC, "coverage.json"))
    refs = load(os.path.join(SPEC, "references.json"))
    fbe = load(os.path.join(DATA, "findings_by_environment.json"))
    index = load(os.path.join(EVID, "index.json"))
    known = {p["id"] for p in index["packages"]}

    ref_items = {}
    for r in refs["references"]:
        for it in r["items"]:
            ref_items[it["id"]] = it
    sids = [s["id"] for s in scen_spec["scenarios"]]
    nids = [n["id"] for n in needs_spec["needs"]]
    scenario_pkg = {}
    for sid in sids:
        if sid not in known:
            stop("scenario %s has no evidence package" % sid)
        scenario_pkg[sid] = load(os.path.join(EVID, "scenario_%s.json" % sid))
    cell_pkg = {}
    for bo in cov["dimensions"]["o2_pct"]["bins"]:
        for bp in cov["dimensions"]["pressure_kpa"]["bins"]:
            cid = "cell_%s__%s" % (bo["id"], bp["id"])
            cell_pkg[cid] = load(os.path.join(EVID, cid + ".json"))

    ctx = {
        "spec": spec, "texts": texts, "coverage": cov,
        "needs": {n["id"]: n for n in needs_spec["needs"]},
        "not_covered": needs_spec["_meta"]["not_covered"],
        "scenario_pkg": scenario_pkg, "cell_pkg": cell_pkg,
        "scenario_rows": {(r["scenario_id"], r["need_id"]): r
                          for r in rows_of(os.path.join(DATA, "scenario_needs.csv"))},
        "cell_rows": {(r["scenario_id"], r["need_id"]): r
                      for r in rows_of(os.path.join(DATA, "atmosphere_cells.csv"))},
        "findings_csv": {r["finding_id"]: r for r in rows_of(os.path.join(DATA, "findings.csv"))},
        "findings_full": fbe["findings"],
        "findings_env": {e["id"]: e for e in fbe["environments"]},
        "ref_items": ref_items,
        "cells": {sid: cells_of(scenario_pkg[sid]["environment"], cov) for sid in sids},
    }

    os.makedirs(OUT, exist_ok=True)
    written = set()
    entries = []
    for sid in sids:
        for nid in nids:
            a = build_answer(sid, nid, ctx)
            name = "%s__%s.json" % (sid, nid)
            dump(a, os.path.join(OUT, name))
            written.add(name)
            entries.append({
                "scenario": sid, "need": nid, "file": name,
                "top_line_id": a["top_line"]["id"], "top_line": a["top_line"]["text"],
                "entries": {
                    "frame": {"criteria": len(a["frame"]["criteria"]),
                              "nasa_questions": len(a["frame"]["nasa_questions"])},
                    "rung1": {"matched_tests": a["rung1_recorded_at_the_condition"]["matched"],
                              "indicators": len(a["rung1_recorded_at_the_condition"]["indicators"])},
                    "rung2": {"cells": len(a["rung2_recorded_near_the_condition"]["cells"])},
                    "rung3": {"at_the_environment": len(a["rung3_published"]["at_the_environment"]),
                              "about_a_stated_condition":
                                  len(a["rung3_published"]["about_a_stated_condition"]),
                              "stated_without_these_conditions":
                                  len(a["rung3_published"]["stated_without_these_conditions"])},
                    "rung4": {"gaps": len(a["rung4_not_known"]["gaps"]),
                              "stated_open_elsewhere":
                                  len(a["rung4_not_known"]["stated_open_elsewhere"]),
                              "not_covered": len(a["rung4_not_known"]["not_covered"]),
                              "searches": len(a["rung4_not_known"]["searches"])},
                },
            })
    dump({"_meta": spec["index_meta"], "answers": entries}, os.path.join(OUT, "index.json"))
    written.add("index.json")
    for name in sorted(os.listdir(OUT)):
        if name not in written:
            os.remove(os.path.join(OUT, name))
    print("answers.py: %d answer files and index.json written to %s" % (len(entries), rel(OUT)))


if __name__ == "__main__":
    build()
