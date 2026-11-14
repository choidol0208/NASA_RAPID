# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Published findings: the items of spec/references.json, retrievable by environment and need.

spec/findings.json tags reference items: which needs an item is about, what kind
of statement it is (result, criterion, gap, caveat) and which conditions the item
itself states (oxygen, pressure, gravity level, flow, fuel phase, material). This
module

  1. checks the tags against spec/references.json and stops on any error:
     the item exists; every word given as basis is in the item's text or quote and
     every key is in its values; every normalized number is literally in the basis
     (or, for a pressure, is such a number times the fixed factor of its unit);
     a gravity level or a fuel phase rests on a word of the vocabulary; every item
     of type published_result, knowledge_gap and limitation is tagged or listed as
     left out with a reason;
  2. writes data/pipeline/findings.csv (one row per entry) and
     data/pipeline/findings_by_environment.json (per scenario of spec/scenarios.json
     and per need: the entries at the environment, about one of its stated
     conditions, and general).

It adds tags only. The text and quote of an item are copied unchanged, no number
is computed from a statement except the unit conversion of a pressure, and nothing
here enters the counts, tiers or indicators of the pipeline. Every sentence is a
template of spec/findings.json (_meta.sentences).

This module does not import run.py, rules.py, evidence.py, facts.py or check.py and
is not imported by them. Standard library only.

Run:  python3 pipeline/findings.py
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "spec")
OUT = os.path.join(os.path.dirname(HERE), "data", "pipeline")

NEED_GENERAL = "general"
KINDS = ("result", "criterion", "gap", "caveat")
MUST_TYPES = ("published_result", "knowledge_gap", "limitation")
NEVER_TYPES = ("stated_objective", "framework")
GRAVITY_LEVELS = ("microgravity", "lunar", "martian", "normal", "partial")
PARTIAL_INCLUDES = ("lunar", "martian")
CONDITION_KEYS = ("o2_pct", "o2_pct_exclusive", "o2_as_written", "pressure_kpa", "pressure_as_written",
                  "gravity_level", "flow_cms", "flow_as_written", "fuel_phase", "material")
BASIS_KEYS = ("o2_pct", "pressure_kpa", "gravity_level", "flow_cms", "fuel_phase", "material")
ENTRY_KEYS = ("item", "row", "row_source", "column_of", "column_index", "needs", "kind", "conditions",
              "condition_basis", "condition_words", "unsure")
LISTS = ("at_environment", "about_a_stated_condition_of_the_environment", "general")
RANGE_DEFAULTS = {"min": None, "max": None, "min_inclusive": True, "max_inclusive": False}
CSV_COLUMNS = ["finding_id", "item_id", "row", "kind", "needs", "o2_pct_min", "o2_pct_max", "pressure_kpa_min",
               "pressure_kpa_max", "pressure_as_written", "gravity_level", "flow_cms", "fuel_phase", "material",
               "text", "quote", "where", "reference_id", "title", "version", "access", "url"]

NUMBER = re.compile(r"\d+(?:\.\d+)?")
PRESSURE_UNIT = re.compile(r"kPa|psia|psi|atmospheres?|atm")
PATH_PART = re.compile(r"[^.\[\]]+|\[\d+\]")
TOKEN = re.compile(r"\{([a-z_]+)\}|\[([a-z_]+)\|([^|\[\]{}]*)\|([^|\[\]{}]*)\]")


def load(name):
    with open(os.path.join(SPEC, name), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- reading the item
def value_at(values, path):
    """The value at a path such as rows[2].o2_pct in an item's 'values'."""
    cur = values
    for part in PATH_PART.findall(path):
        cur = cur[int(part[1:-1])] if part.startswith("[") else cur[part]
    return cur


def numbers_in(value):
    """Every number literally held by a string, a number or a list of them."""
    if isinstance(value, bool) or value is None:
        return []
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, str):
        return [float(x) for x in NUMBER.findall(value)]
    if isinstance(value, list):
        return [n for v in value for n in numbers_in(v)]
    return []


def same(a, b):
    return abs(a - b) < 5e-4


def pressure_numbers(as_written, units):
    """kPa values of the numbers in the as-written words: each number takes the unit that follows it."""
    found = [(m.start(), m.group()) for m in PRESSURE_UNIT.finditer(as_written)]
    out = []
    for m in NUMBER.finditer(as_written):
        after = [u for pos, u in found if pos >= m.end()]
        if not after:
            continue
        u = after[0]
        factor = 1.0 if u == "kPa" else units["psi_to_kpa"] if u.startswith("psi") else units["atm_to_kpa"]
        out.append(round(float(m.group()) * factor, units["kpa_decimals"]))
    return out


def as_range(v):
    """A normalized value as (min, max); a single value is (v, v); None stays None."""
    if v is None:
        return None
    if isinstance(v, list):
        return (v[0], v[1])
    return (v, v)


# ---------------------------------------------------------------- validation
def validate(spec, refs, need_ids):
    """Every error of spec/findings.json against spec/references.json, as a list of strings."""
    meta, errors = spec["_meta"], []
    items = {it["id"]: (d, it) for d in refs["references"] for it in d["items"]}
    order = {iid: n for n, iid in enumerate(items)}
    units, gvoc, pvoc = meta["units"], meta["gravity_vocabulary"], meta["fuel_phase_vocabulary"]
    if sorted(gvoc) != sorted(GRAVITY_LEVELS):
        errors.append("_meta.gravity_vocabulary must hold exactly: " + ", ".join(GRAVITY_LEVELS))
    seen, by_item = set(), {}

    for n, e in enumerate(spec["findings"]):
        iid = e.get("item")
        tag = f"findings[{n}] {iid}" + (f" #{e['row']}" if "row" in e else "")

        def bad(msg):
            errors.append(f"{tag}: {msg}")

        for k in e:
            if k not in ENTRY_KEYS:
                bad(f"unknown field {k}")
        if iid not in items:
            bad("item is not in references.json")
            continue
        doc, it = items[iid]
        if it["type"] in NEVER_TYPES:
            bad(f"items of type {it['type']} are not tagged")
        fid = finding_id(e)
        if fid in seen:
            bad("two entries with the same item and row")
        seen.add(fid)
        by_item.setdefault(iid, []).append(e)
        needs = e.get("needs")
        if not isinstance(needs, list) or not needs or len(set(needs)) != len(needs):
            bad("needs must be a non-empty list without repeats")
        elif needs != [NEED_GENERAL] and any(x not in need_ids for x in needs):
            bad(f"needs must be ids of needs.json or ['general']: {needs}")
        if e.get("kind") not in KINDS:
            bad(f"kind must be one of {KINDS}")
        cond, basis = e.get("conditions", {}), e.get("condition_basis", {})
        for k in cond:
            if k not in CONDITION_KEYS:
                bad(f"unknown condition {k}")
        for k in BASIS_KEYS:
            if (k in cond) != (k in basis and bool(basis[k])):
                bad(f"{k}: a normalized condition needs a basis and a basis needs a condition")
        text, quote, values = it.get("text", ""), it.get("quote", ""), it.get("values", {})

        def held(b):
            """What a basis holds: (the words or key name, the value). None, with an error, if not in the item."""
            h = held_quiet(values, it, b)
            if h is None:
                bad(f"basis not in the item: {json.dumps(b, ensure_ascii=False)}")
            return h

        resolved = {k: [h for h in (held(b) for b in basis.get(k, [])) if h] for k in BASIS_KEYS}

        # oxygen: every number is literally in the basis
        if "o2_pct" in cond:
            have = [x for _, v in resolved["o2_pct"] for x in numbers_in(v)]
            for x in as_range(cond["o2_pct"]):
                if x is not None and not any(same(x, h) for h in have):
                    bad(f"o2_pct {x} is not a number of its basis")
            lo, hi = as_range(cond["o2_pct"])
            if lo is not None and hi is not None and lo > hi:
                bad("o2_pct range is not [min, max]")
            if lo is None and hi is None:
                bad("o2_pct has no number")
            written = cond.get("o2_as_written")
            if not written or not (written in text or written in quote
                                   or any(str(v) == written for _, v in resolved["o2_pct"])):
                bad("o2_as_written must be words of the item or the cell of a values basis")
            for end in cond.get("o2_pct_exclusive", []):
                if end not in ("min", "max"):
                    bad("o2_pct_exclusive holds 'min' and/or 'max'")
        elif "o2_as_written" in cond or "o2_pct_exclusive" in cond:
            bad("o2_as_written without o2_pct")

        # pressure: every number is a number of the as-written words times the factor of its unit
        if "pressure_kpa" in cond:
            written = cond.get("pressure_as_written")
            if not written or not (written in text or written in quote):
                bad("pressure_as_written must be words of the item's text or quote")
            else:
                have = pressure_numbers(written, units)
                for x in as_range(cond["pressure_kpa"]):
                    if x is None or not any(same(x, h) for h in have):
                        bad(f"pressure_kpa {x} is not a number of {written!r} times the factor of its unit")
                if not any(w == written or written in str(w) for w, _ in resolved["pressure_kpa"]):
                    bad("pressure_as_written is not part of the basis")
            lo, hi = as_range(cond["pressure_kpa"])
            if lo is not None and hi is not None and lo > hi:
                bad("pressure_kpa range is not [min, max]")
        elif "pressure_as_written" in cond:
            bad("pressure_as_written without pressure_kpa")

        # flow: the number is literally in the basis
        if "flow_cms" in cond:
            have = [x for _, v in resolved["flow_cms"] for x in numbers_in(v)]
            if isinstance(cond["flow_cms"], list) or not any(same(cond["flow_cms"], h) for h in have):
                bad(f"flow_cms {cond['flow_cms']} is not a number of its basis")
            written = cond.get("flow_as_written")
            if not written or not (written in text or written in quote):
                bad("flow_as_written must be words of the item's text or quote")

        # gravity level and fuel phase: a word of the vocabulary, in the words or in the key name
        if "gravity_level" in cond:
            levels = cond["gravity_level"]
            if not isinstance(levels, list) or not levels or any(g not in GRAVITY_LEVELS for g in levels):
                bad(f"gravity_level must be a list of {GRAVITY_LEVELS}")
            else:
                for g in levels:
                    ok = False
                    for b in basis.get("gravity_level", []):
                        where = (b.get("words") or b.get("key") or "").lower()
                        if b.get("level") == g and any(term.lower() in where for term in gvoc.get(g, [])):
                            ok = True
                    if not ok:
                        bad(f"gravity_level {g} has no basis with a word of the vocabulary")
                for b in basis.get("gravity_level", []):
                    if b.get("level") not in levels:
                        bad(f"gravity basis for a level that is not tagged: {b.get('level')}")
        if "fuel_phase" in cond:
            phase = cond["fuel_phase"]
            if phase not in pvoc:
                bad(f"fuel_phase must be one of {sorted(pvoc)}")
            elif not any(term in str(w).lower() for w, _ in resolved["fuel_phase"] for term in pvoc[phase]):
                bad(f"fuel_phase {phase} has no basis with a word of the vocabulary")

        # material: as written in the text or quote, or a string of values, or the name of a values key
        if "material" in cond:
            names = cond["material"]
            if not isinstance(names, list) or not names:
                bad("material must be a non-empty list")
            else:
                in_values = [h for h in (held_quiet(values, it, b) for b in basis.get("material", [])
                                         if b.get("in") == "values") if h]
                for name in names:
                    in_values_ok = any(v == name or key.split(".")[-1] == name for key, v in in_values)
                    if not (name in text or name in quote or in_values_ok):
                        bad(f"material {name!r} is not written in the item")

        # words that cannot be compared: exact words of the item
        for k, words in e.get("condition_words", {}).items():
            if not isinstance(words, list) or not words:
                bad(f"condition_words.{k} must be a non-empty list")
                continue
            for w in words:
                if not (w in text or w in quote):
                    bad(f"condition_words.{k}: not words of the item's text or quote: {w!r}")

        # rows
        if "row_source" in e:
            try:
                value_at(values, e["row_source"])
            except (KeyError, IndexError, TypeError, ValueError):
                bad(f"row_source not in the item's values: {e['row_source']}")
        if "column_of" in e:
            table = values.get(e["column_of"])
            if not isinstance(table, dict) or not isinstance(e.get("column_index"), int):
                bad("column_of must name a table of the item's values, with column_index")

    # an item with several entries names each by its row; values.rows are covered row by row
    for iid, group in by_item.items():
        if len(group) > 1 and any("row" not in e for e in group):
            errors.append(f"{iid}: several entries, each needs a 'row'")
        rows = items[iid][1].get("values", {}).get("rows")
        if isinstance(rows, list) and any(e.get("row_source", "").startswith("rows[") for e in group):
            used = sorted(e.get("row_source") for e in group)
            if used != sorted(f"rows[{i}]" for i in range(len(rows))):
                errors.append(f"{iid}: the entries do not cover values.rows one by one")

    # entries follow the order of references.json
    positions = [order[e["item"]] for e in spec["findings"] if e.get("item") in order]
    if positions != sorted(positions):
        errors.append("findings must be in the order of the items of references.json")

    # every item of the three types is tagged or left out with a reason
    left_out = meta.get("left_out", {})
    for iid, (doc, it) in items.items():
        if it["type"] in MUST_TYPES and iid not in by_item and iid not in left_out:
            errors.append(f"{iid} ({it['type']}) is neither tagged nor listed under _meta.left_out")
    for iid, reason in left_out.items():
        if iid not in items:
            errors.append(f"_meta.left_out: {iid} is not in references.json")
        elif iid in by_item:
            errors.append(f"_meta.left_out: {iid} is also tagged")
        if not reason:
            errors.append(f"_meta.left_out: {iid} has no reason")

    # the sentences hold none of the forbidden words
    sentences = meta["sentences"]
    templates = [sentences[k] for k in ("counts_with_ranges", "counts_without_ranges", "nature", "none")]
    templates += list(sentences["need_phrase"].values())
    for t in templates:
        word = forbidden_in(t, meta["forbidden_words"])
        if word:
            errors.append(f"_meta.sentences: the word {word!r} is not allowed in a sentence: {t!r}")
    return errors


def held_quiet(values, it, b):
    """What a basis holds: (the words or key name, the value); None if it is not in the item."""
    if b.get("in") == "values":
        try:
            return b["key"], value_at(values, b["key"])
        except (KeyError, IndexError, TypeError, ValueError):
            return None
    if b.get("in") in ("text", "quote") and b.get("words") and b["words"] in it.get(b["in"], ""):
        return b["words"], b["words"]
    return None


def forbidden_in(sentence, words):
    for w in words:
        if re.search(r"\b" + re.escape(w) + r"\b", sentence, flags=re.IGNORECASE):
            return w
    return None


# ---------------------------------------------------------------- records
def finding_id(e):
    return e["item"] + ("#" + str(e["row"]) if "row" in e else "")


def records(spec, refs):
    """One record per entry: the tags, and the item and its document copied unchanged."""
    items = {it["id"]: (d, it) for d in refs["references"] for it in d["items"]}
    out = []
    for e in spec["findings"]:
        doc, it = items[e["item"]]
        cond = e.get("conditions", {})
        rec = {
            "finding_id": finding_id(e),
            "item_id": e["item"],
            "row": e.get("row"),
            "kind": e["kind"],
            "needs": list(e["needs"]),
            "item_type": it["type"],
            "conditions": {
                "o2_pct": cond.get("o2_pct"),
                "o2_pct_exclusive": cond.get("o2_pct_exclusive", []),
                "o2_as_written": cond.get("o2_as_written"),
                "pressure_kpa": cond.get("pressure_kpa"),
                "pressure_as_written": cond.get("pressure_as_written"),
                "gravity_level": cond.get("gravity_level", []),
                "flow_cms": cond.get("flow_cms"),
                "flow_as_written": cond.get("flow_as_written"),
                "fuel_phase": cond.get("fuel_phase"),
                "material": cond.get("material", []),
            },
            "condition_basis": e.get("condition_basis", {}),
            "condition_words": e.get("condition_words", {}),
            "text": it["text"],
            "quote": it.get("quote"),
            "where": it["where"],
            "row_values": row_values(e, it),
            "item_note": it.get("note"),
            "tagging_note": e.get("unsure"),
            "reference": {"id": doc["id"], "title": doc["title"], "issuer": doc["issuer"],
                          "version": doc["version"], "access": doc["access"], "url": doc["url"]},
        }
        out.append(rec)
    return out


def row_values(e, it):
    """The values of the row an entry was made from, copied from the item."""
    values = it.get("values", {})
    if "column_of" in e:
        table, i = values[e["column_of"]], e["column_index"]
        return {k: v[i] for k, v in table.items() if isinstance(v, list)}
    if "row_source" in e:
        return value_at(values, e["row_source"])
    return None


# ---------------------------------------------------------------- matching
def scenario_range(scenario, variable):
    r = scenario.get("ranges", {}).get(variable)
    if not r or (r.get("min") is None and r.get("max") is None):
        return None
    return dict(RANGE_DEFAULTS, **r)


def value_inside(v, r):
    low = r["min"] is None or v > r["min"] or (v == r["min"] and r["min_inclusive"])
    high = r["max"] is None or v < r["max"] or (v == r["max"] and r["max_inclusive"])
    return low and high


def relation(stated, exclusive, r):
    """inside, overlaps or outside for a stated value or range against a scenario range."""
    if r is None:
        return "not_set"
    if stated is None:
        return "not_stated"
    lo, hi = as_range(stated)
    if lo is not None and hi is not None and lo == hi:
        return "inside" if value_inside(lo, r) else "outside"
    lo_incl, hi_incl = "min" not in exclusive, "max" not in exclusive
    # no part of the stated range is in the scenario range
    below = hi is not None and r["min"] is not None and (hi < r["min"] or (hi == r["min"]
                                                                          and not (hi_incl and r["min_inclusive"])))
    above = lo is not None and r["max"] is not None and (lo > r["max"] or (lo == r["max"]
                                                                          and not (lo_incl and r["max_inclusive"])))
    if below or above:
        return "outside"
    if lo is not None and hi is not None and value_inside(lo, r) and value_inside(hi, r):
        return "inside"
    return "overlaps"


def gravity_relation(levels, scenario_level):
    if scenario_level is None:
        return "not_set"
    if not levels:
        return "not_stated"
    if scenario_level in levels:
        return "same"
    if "partial" in levels and scenario_level in PARTIAL_INCLUDES:
        return "finding_states_partial_gravity"
    return "different"


def place(rec, scenario):
    """The list of a record for a scenario, with what matched and why."""
    c = rec["conditions"]
    rel = {
        "o2_pct": relation(c["o2_pct"], c["o2_pct_exclusive"], scenario_range(scenario, "o2_pct")),
        "pressure_kpa": relation(c["pressure_kpa"], [], scenario_range(scenario, "pressure_kpa")),
        "gravity_level": gravity_relation(c["gravity_level"], scenario.get("gravity_level")),
    }
    states_any = c["o2_pct"] is not None or c["pressure_kpa"] is not None or bool(c["gravity_level"])
    matches = {"o2_pct": ("inside", "overlaps"), "pressure_kpa": ("inside", "overlaps"),
               "gravity_level": ("same", "finding_states_partial_gravity")}
    conflicts = [k for k, v in rel.items() if v in ("outside", "different")]
    matched = [k for k, v in rel.items() if v in matches[k]]
    reason = None
    if not states_any:
        where = "general"
    elif rel["o2_pct"] == "inside" and rel["pressure_kpa"] == "inside":
        if rel["gravity_level"] == "different":
            where, reason = "other_conditions", "moved_for_gravity"
        else:
            where = "at_environment"
    elif conflicts:
        where, reason = "other_conditions", "a_stated_condition_is_outside"
    elif matched:
        where = "about_a_stated_condition_of_the_environment"
    else:
        where, reason = "other_conditions", "states_no_condition_that_this_environment_sets"

    entry = {"finding_id": rec["finding_id"], "kind": rec["kind"], "access": rec["reference"]["access"]}
    matched_on = {}
    for k in matched:
        if k == "gravity_level":
            matched_on[k] = {"finding": c["gravity_level"], "scenario": scenario["gravity_level"],
                             "relation": rel[k]}
        else:
            written = c["o2_as_written"] if k == "o2_pct" else c["pressure_as_written"]
            matched_on[k] = {"finding": c[k], "as_written": written, "relation": rel[k]}
    entry["matched_on"] = matched_on
    entry["not_stated"] = [k for k, v in rel.items() if v == "not_stated"]
    flow_range = scenario_range(scenario, "flow_cms")
    if flow_range is not None:
        entry["flow"] = relation(c["flow_cms"], [], flow_range)
    if where == "general":
        entry["states_conditions_in_words"] = bool(rec["condition_words"])
    return where, reason, entry, rel


# ---------------------------------------------------------------- sentences
def fill(template, fields):
    def one(m):
        if m.group(1):
            return str(fields[m.group(1)])
        return m.group(3) if fields[m.group(2)] == 1 else m.group(4)
    return TOKEN.sub(one, template)


def statements(meta, counts, need, has_ranges):
    s = meta["sentences"]
    fields = dict(counts, need_phrase=s["need_phrase"]["general" if need == NEED_GENERAL else "need"])
    if counts["n_listed"] == 0:
        out = [fill(s["none"], fields)]
    else:
        out = [fill(s["counts_with_ranges" if has_ranges else "counts_without_ranges"], fields),
               fill(s["nature"], fields)]
    for sentence in out:
        word = forbidden_in(sentence, meta["forbidden_words"])
        if word:
            raise SystemExit(f"findings.json: the word {word!r} is not allowed in a sentence: {sentence!r}")
    return out


# ---------------------------------------------------------------- outputs
def by_environment(spec, recs, scenarios, needs):
    meta = spec["_meta"]
    need_names = [(n["id"], n["name"]) for n in needs["needs"]] + [(NEED_GENERAL, "Fire safety in general")]
    environments = []
    for sc in scenarios["scenarios"]:
        ranges = {v: scenario_range(sc, v) for v in ("o2_pct", "pressure_kpa", "flow_cms")}
        has_ranges = ranges["o2_pct"] is not None and ranges["pressure_kpa"] is not None
        blocks = {}
        for need, name in need_names:
            block = {"name": name}
            lists = {k: [] for k in LISTS}
            other = {"count": 0, "by_reason": {}, "moved_for_gravity": []}
            for rec in recs:
                if need not in rec["needs"]:
                    continue
                where, reason, entry, rel = place(rec, sc)
                if where == "other_conditions":
                    other["count"] += 1
                    other["by_reason"][reason] = other["by_reason"].get(reason, 0) + 1
                    if reason == "moved_for_gravity":
                        c = rec["conditions"]
                        other["moved_for_gravity"].append({
                            "finding_id": rec["finding_id"],
                            "reason": "states an oxygen and a pressure inside the ranges and a gravity level "
                                      "other than that of the environment",
                            "finding": {"o2_pct": c["o2_pct"], "pressure_kpa": c["pressure_kpa"],
                                        "gravity_level": c["gravity_level"]},
                            "scenario_gravity_level": sc["gravity_level"]})
                else:
                    lists[where].append(entry)
            other["by_reason"] = dict(sorted(other["by_reason"].items()))
            listed = [x for k in LISTS for x in lists[k]]
            counts = {"n_at": len(lists["at_environment"]),
                      "n_about": len(lists["about_a_stated_condition_of_the_environment"]),
                      "n_general": len(lists["general"]), "n_listed": len(listed),
                      "n_not_full_text": sum(1 for x in listed if x["access"] != "full_text_read"),
                      "n_other_conditions": other["count"]}
            block["counts"] = counts
            block["statements"] = statements(meta, counts, need, has_ranges)
            block.update(lists)
            block["other_conditions"] = other
            blocks[need] = block
        environments.append({"id": sc["id"], "label": sc["label"], "ranges": ranges,
                             "gravity_level": sc.get("gravity_level"), "needs": blocks})

    findings = {}
    for rec in recs:
        r = {k: v for k, v in rec.items() if k != "finding_id"}
        r["conditions"] = {k: v for k, v in rec["conditions"].items() if v not in (None, [])}
        findings[rec["finding_id"]] = {k: v for k, v in r.items()
                                       if v is not None and (v != {} or k == "conditions")}
    return {
        "_meta": {
            "generated_by": meta["generated_by"],
            "written_by": "python3 pipeline/findings.py, from pipeline/spec/findings.json, references.json, "
                          "scenarios.json and needs.json",
            "content": "For each scenario and each need (and for the entries tagged 'general'): the entries of "
                       "spec/findings.json in three lists, with what matched, and fixed sentences. 'findings' "
                       "holds each entry once: its tags, the text, quote and place of the item copied from "
                       "references.json, and the document with its access level.",
            "tagging": meta["tagging"],
            "rules": meta["rules"],
            "lists": meta["lists"],
            "units": meta["units"],
            "fields": {
                "item_note": "the 'note' of the item in references.json: a note of the team's reading, not a "
                             "sentence of the document",
                "tagging_note": "the 'unsure' of the entry in spec/findings.json: written by the AI that tagged",
                "row_values": "the values of the row or table column the entry was made from, copied from the item",
            },
            "counts": summary(recs),
        },
        "environments": environments,
        "findings": findings,
    }


def summary(recs):
    kinds = {k: sum(1 for r in recs if r["kind"] == k) for k in KINDS}
    needs = {}
    for r in recs:
        for n in r["needs"]:
            needs[n] = needs.get(n, 0) + 1
    return {
        "entries": len(recs),
        "items": len({r["item_id"] for r in recs}),
        "by_kind": kinds,
        "by_need": dict(sorted(needs.items())),
        "with_oxygen": sum(1 for r in recs if r["conditions"]["o2_pct"] is not None),
        "with_pressure": sum(1 for r in recs if r["conditions"]["pressure_kpa"] is not None),
        "with_oxygen_and_pressure": sum(1 for r in recs if r["conditions"]["o2_pct"] is not None
                                        and r["conditions"]["pressure_kpa"] is not None),
        "with_gravity_level": sum(1 for r in recs if r["conditions"]["gravity_level"]),
        "with_no_oxygen_pressure_or_gravity_level": sum(
            1 for r in recs if r["conditions"]["o2_pct"] is None and r["conditions"]["pressure_kpa"] is None
            and not r["conditions"]["gravity_level"]),
        "with_condition_words": sum(1 for r in recs if r["condition_words"]),
        "from_documents_not_read_in_full_text": sum(1 for r in recs
                                                    if r["reference"]["access"] != "full_text_read"),
    }


def cell(v):
    """A CSV cell: empty for nothing, numbers without a trailing .0."""
    if v is None:
        return ""
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def csv_rows(recs):
    for r in recs:
        c = r["conditions"]
        o2 = as_range(c["o2_pct"]) or (None, None)
        p = as_range(c["pressure_kpa"]) or (None, None)
        yield {
            "finding_id": r["finding_id"], "item_id": r["item_id"], "row": cell(r["row"]), "kind": r["kind"],
            "needs": ";".join(r["needs"]),
            "o2_pct_min": cell(o2[0]), "o2_pct_max": cell(o2[1]),
            "pressure_kpa_min": cell(p[0]), "pressure_kpa_max": cell(p[1]),
            "pressure_as_written": cell(c["pressure_as_written"]),
            "gravity_level": ";".join(c["gravity_level"]),
            "flow_cms": cell(c["flow_cms"]), "fuel_phase": cell(c["fuel_phase"]),
            "material": "; ".join(c["material"]),
            "text": r["text"], "quote": cell(r["quote"]), "where": r["where"],
            "reference_id": r["reference"]["id"], "title": r["reference"]["title"],
            "version": r["reference"]["version"], "access": r["reference"]["access"],
            "url": r["reference"]["url"],
        }


def main():
    spec, refs = load("findings.json"), load("references.json")
    needs, scenarios = load("needs.json"), load("scenarios.json")
    errors = validate(spec, refs, [n["id"] for n in needs["needs"]])
    if errors:
        print("findings.json does not agree with references.json:", file=sys.stderr)
        for e in errors:
            print("  " + e, file=sys.stderr)
        raise SystemExit(1)

    recs = records(spec, refs)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "findings.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(csv_rows(recs))
    package = by_environment(spec, recs, scenarios, needs)
    with open(os.path.join(OUT, "findings_by_environment.json"), "w", encoding="utf-8") as f:
        json.dump(package, f, ensure_ascii=False, indent=1)
        f.write("\n")

    counts = package["_meta"]["counts"]
    print(f"findings: {counts['entries']} entries from {counts['items']} items; "
          f"{len(spec['_meta'].get('left_out', {}))} items left out with a reason")
    for env in package["environments"]:
        n = {k: sum(len(b[k]) for b in env["needs"].values()) for k in LISTS}
        print(f"  {env['id']}: at_environment {n['at_environment']}, "
              f"about a stated condition {n['about_a_stated_condition_of_the_environment']}, "
              f"general {n['general']} (entries with several needs are counted once per need)")


if __name__ == "__main__":
    main()
