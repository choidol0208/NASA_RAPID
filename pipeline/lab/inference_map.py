# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Inference map for one question (experiment on branch data-lab).

Reads pipeline/spec/inference_map.json, pipeline/spec/references.json,
pipeline/spec/scenarios.json, pipeline/spec/relation_cards.json (unit factors),
data/psi/catalog/PSI-25.json, data/pipeline/findings.csv,
data/pipeline/need_tests.csv, data/pipeline/tests.csv and
data/pipeline/answers/<scenario>__<need>.json. Writes
data/pipeline/lab/inference_map_lunar_habitat.json and
data/pipeline/lab/inference_map_lunar_habitat.md.

It stops if an item id does not exist, if a quoted text is not equal to the
item's 'quote' or 'text' (or not a part of the PSI record field it names), if a
year is not written in the document's id, version or title, or if a word of the
forbidden list appears outside a quote. The state of each link is assigned by
the rule written in the spec (_meta.state_rule). Every count is read from the
data files; no number is typed here.

Run: python3 pipeline/lab/inference_map.py
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "pipeline" / "spec"
DATA = ROOT / "data" / "pipeline"
OUT = DATA / "lab"
NIH = "no item held"
AXES = ("o2", "pressure", "gravity", "flow")


def fail(msg):
    sys.exit("inference map: " + msg)


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def fnum(s):
    s = (s or "").strip()
    return float(s) if s else None


# ---------------------------------------------------------------- inputs

def load_items():
    items = {}
    for ref in load_json(SPEC / "references.json")["references"]:
        for it in ref["items"]:
            if it["id"] in items:
                fail("duplicate item id " + it["id"])
            items[it["id"]] = (it, ref)
    return items


def doc_year(spec, ref):
    years = spec["document_years"]
    if ref["id"] not in years:
        fail("no entry in document_years for " + ref["id"])
    y = years[ref["id"]]
    if y is None:
        return "year not stated in references.json"
    where = " ".join([ref["id"], ref.get("version", ""), ref.get("title", "")])
    if not re.search(r"(?<!\d)%s(?!\d)" % re.escape(y), where):
        fail("year %s not written in id, version or title of %s" % (y, ref["id"]))
    return y


def check_quote(entry, items, spec, records):
    """Check one quote entry and return it with the document it comes from."""
    if "record" in entry:
        rec = records[entry["record"]]
        src = rec.get(entry["field"])
        if not isinstance(src, str) or entry["quote"] not in src:
            fail("quote not in %s.%s: %r" % (entry["record"], entry["field"], entry["quote"][:60]))
        y = rec["releaseDate"][-4:]
        return {"record": entry["record"], "field": entry["field"], "quote": entry["quote"],
                "document": "NASA PSI record %s (%s)" % (entry["record"], rec["title"]),
                "year": "%s (PSI record release date %s)" % (y, rec["releaseDate"]),
                "access": "full_text_read"}
    iid, field = entry["item"], entry["field"]
    if iid not in items:
        fail("item not in references.json: " + iid)
    if field not in spec["_meta"]["quote_fields"]:
        fail("field %s not allowed for %s" % (field, iid))
    it, ref = items[iid]
    if field not in it:
        fail("item %s has no field %s" % (iid, field))
    if it[field] != entry["quote"]:
        fail("quoted text is not equal to %s.%s" % (iid, field))
    return {"item": iid, "field": field, "quote": entry["quote"], "where": it.get("where"),
            "document": ref["id"], "title": ref["title"], "year": doc_year(spec, ref),
            "access": ref["access"], "url": ref.get("url")}


def check_quotes(value, items, spec, records):
    if value == NIH:
        return NIH
    if isinstance(value, list):
        return [check_quote(e, items, spec, records) for e in value]
    return check_quote(value, items, spec, records)


def load_findings():
    rows = {}
    with open(DATA / "findings.csv", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            rows.setdefault(r["item_id"], []).append(r)
    return rows


def load_counted_tests():
    with open(DATA / "tests.csv", encoding="utf-8", newline="") as fh:
        tests = {r["test_id"]: r for r in csv.DictReader(fh)}
    counted = {}
    with open(DATA / "need_tests.csv", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["objective_link"] == "stated":
                counted.setdefault(r["need_id"], []).append(tests[r["test_id"]])
    for need in counted:
        counted[need].sort(key=lambda t: t["test_id"])
    return counted


# ---------------------------------------------------------------- environment

def environment(spec, items, records):
    env = spec["environment"]
    it, _ = items[env["bounds_from"]]
    factors = load_json(SPEC / "relation_cards.json")["_meta"]["units"]
    nd = factors["rounding_kpa_decimals"]
    psia = it["values"][env["pressure_max_key"]]
    p_max = round(psia * factors["pressure_to_kpa"]["psia"], nd)
    scen = [s for s in load_json(SPEC / "scenarios.json")["scenarios"] if s["id"] == env["scenario_id"]]
    if len(scen) != 1:
        fail("scenario %s not found" % env["scenario_id"])
    return {
        "label": env["label"],
        "o2_pct_min": it["values"][env["o2_min_key"]],
        "pressure_psia_max": psia,
        "pressure_kpa_max": p_max,
        "gravity_level": scen[0]["gravity_level"],
        "bounds_from": env["bounds_from"],
        "gravity_from": env["gravity_from"],
        "rounding_kpa_decimals": nd,
        "stated_by": check_quotes(env["stated_by"], items, spec, records),
    }


# ---------------------------------------------------------------- axis tests

def finding_axes(row, env):
    nd = env["rounding_kpa_decimals"]
    lo, hi = fnum(row["o2_pct_min"]), fnum(row["o2_pct_max"])
    plo, phi = fnum(row["pressure_kpa_min"]), fnum(row["pressure_kpa_max"])
    grav = [g for g in row["gravity_level"].split(";") if g]
    return {
        "o2": lo is not None and hi is not None and lo >= env["o2_pct_min"],
        "pressure": plo is not None and phi is not None and round(phi, nd) <= env["pressure_kpa_max"],
        "gravity": env["gravity_level"] in grav,
        "flow": bool(row["flow_cms"].strip()),
    }


def test_axes(t, env):
    nd = env["rounding_kpa_decimals"]
    o2, p = fnum(t["o2_pct"]), fnum(t["pressure_kpa"])
    return {
        "o2": o2 is not None and o2 >= env["o2_pct_min"],
        "pressure": p is not None and round(p, nd) <= env["pressure_kpa_max"],
        "gravity": t["gravity_level"] == env["gravity_level"],
        "flow": fnum(t["flow_cms"]) is not None,
    }


def finding_conditions(row):
    out = {}
    for k in ("o2_pct_min", "o2_pct_max", "pressure_kpa_min", "pressure_kpa_max"):
        if row[k].strip():
            out[k] = fnum(row[k])
    for k in ("pressure_as_written", "gravity_level", "flow_cms", "material"):
        if row[k].strip():
            out[k] = row[k]
    return out


# ---------------------------------------------------------------- one link

def assess(link, items, findings, counted, env, scenario_id):
    req = link["required_conditions"]
    for a in req:
        if a not in AXES:
            fail("unknown condition %s in %s" % (a, link["id"]))
    rule = link["rule"]
    established, partly = [], []
    covered = {a: False for a in req}
    any_all_in = False
    for iid in link["evidence_items"]:
        if iid not in items:
            fail("evidence item not in references.json: %s (%s)" % (iid, link["id"]))
        it, ref = items[iid]
        rows = findings.get(iid, [])
        if not rows:
            partly.append({"item": iid, "row": None, "item_type": it["type"], "kind": None,
                           "document": ref["id"], "conditions": {},
                           "inside": [], "not_inside": list(req),
                           "note": "no row in findings.csv: the item states no condition that findings.py tags"})
            continue
        for r in rows:
            ax = finding_axes(r, env)
            inside = [a for a in req if ax[a]]
            for a in inside:
                covered[a] = True
            entry = {"item": iid, "row": r["row"] or None, "item_type": it["type"], "kind": r["kind"],
                     "document": ref["id"], "conditions": finding_conditions(r),
                     "inside": inside, "not_inside": [a for a in req if not ax[a]]}
            all_in = len(inside) == len(req)
            any_all_in = any_all_in or all_in
            if rule == "result":
                qualifies = all_in and r["kind"] == "result"
            elif rule == "specification":
                qualifies = all_in and it["type"] == "requirement"
            else:
                fail("unknown rule %s in %s" % (rule, link["id"]))
            (established if qualifies else partly).append(entry)

    psi = []
    any_test = False
    for need in link["psi_needs"]:
        tests = counted.get(need, [])
        n_axis = {a: 0 for a in req}
        n_all = 0
        for t in tests:
            ax = test_axes(t, env)
            for a in req:
                n_axis[a] += ax[a]
            if all(ax[a] for a in req):
                n_all += 1
        for a in req:
            covered[a] = covered[a] or n_axis[a] > 0
        any_test = any_test or len(tests) > 0
        ans = load_json(DATA / "answers" / ("%s__%s.json" % (scenario_id, need)))
        r1 = ans["rung1_recorded_at_the_condition"]["counts"]
        r4 = ans["rung4_not_known"]
        psi.append({
            "need": need,
            "need_name": ans["need"]["need"],
            "counted_tests": len(tests),
            "inside_by_condition": n_axis,
            "inside_on_every_required_condition": n_all,
            "investigations": sorted({t["investigation_id"] for t in tests}),
            "answer_file": "data/pipeline/answers/%s__%s.json" % (scenario_id, need),
            "answer_file_counts": {"usable_tests": r1["usable_tests"], "atmosphere": r1["atmosphere"],
                                   "matched_same_gravity": r1["matched_same_gravity"]},
            "answer_file_gaps": [g["code"] for g in r4["gaps"]],
            "answer_file_stated_open_elsewhere": [e["item_id"] for e in r4["stated_open_elsewhere"]],
        })
        if n_all and rule == "result":
            established.append({"psi_need": need, "tests": n_all})

    if established:
        state = "established"
    elif link["evidence_items"] or any_test:
        state = "partly"
    else:
        state = "missing"

    missing = []
    for a in req:
        if not covered[a]:
            missing.append({"condition": a, "text": "no evidence item or counted PSI test of this link is inside on this condition"})
    if not established and any_all_in:
        missing.append({"condition": "+".join(req),
                        "text": "an item states every required condition, but none is of the kind the rule counts (%s)"
                        % ("a result" if rule == "result" else "a requirement")})
    elif not established and req and all(covered[a] for a in req):
        missing.append({"condition": "+".join(req),
                        "text": "each condition is met by some item or test, but no single one is inside on all of them"})
    gap_axis = {"oxygen": "o2", "pressure": "pressure", "gravity": "gravity", "flow": "flow"}
    for p in psi:
        for g in p["answer_file_gaps"]:
            axis = gap_axis.get(g.split(":")[0])
            if axis is None or axis in req:
                missing.append({"psi_need": p["need"], "answer_file_gap": g})
    return state, established, partly, missing, psi


# ---------------------------------------------------------------- word scan

def scan_words(strings, words, where):
    pat = re.compile(r"\b(%s)\b" % "|".join(map(re.escape, words)), re.IGNORECASE)
    for s in strings:
        m = pat.search(s)
        if m:
            fail("forbidden word %r outside a quote in %s: %r" % (m.group(1), where, s[:80]))


def own_strings(obj, skip=("quote", "forbidden_words")):
    """Every string of the spec that is not a quote (team wording)."""
    if isinstance(obj, dict):
        if "quote" in obj and ("item" in obj or "record" in obj):
            return [v for k, v in obj.items() if k not in ("quote",) and isinstance(v, str)]
        out = []
        for k, v in obj.items():
            if k in skip:
                continue
            out += own_strings(v, skip)
        return out
    if isinstance(obj, list):
        out = []
        for v in obj:
            out += own_strings(v, skip)
        return out
    return [obj] if isinstance(obj, str) else []


# ---------------------------------------------------------------- rendering

def cite(q):
    if "record" in q:
        src = "%s %s, %s" % (q["record"], q["field"], q["year"])
    else:
        src = "%s, %s, %s" % (q["item"], q["document"], q["year"])
        if q["field"] == "text":
            src += "; team wording of the document, not a verbatim quote"
        if q["access"] != "full_text_read":
            src += "; access: " + q["access"]
    return src


def quote_lines(q, indent):
    pad = " " * indent
    text = " ".join(q["quote"].split())
    return ['%s"%s"' % (pad, text), "%s  [%s]" % (pad, cite(q))]


def fmt_num(x):
    return "{:g}".format(x)


def cond_text(c):
    parts = []
    if "o2_pct_min" in c:
        lo, hi = c["o2_pct_min"], c["o2_pct_max"]
        parts.append("O2 %s%%" % fmt_num(lo) if lo == hi else "O2 %s-%s%%" % (fmt_num(lo), fmt_num(hi)))
    if "pressure_kpa_min" in c:
        lo, hi = c["pressure_kpa_min"], c["pressure_kpa_max"]
        parts.append("%s kPa" % fmt_num(lo) if lo == hi else "%s-%s kPa" % (fmt_num(lo), fmt_num(hi)))
    if "gravity_level" in c:
        parts.append("gravity " + c["gravity_level"].replace(";", "/"))
    if "flow_cms" in c:
        parts.append("flow " + c["flow_cms"] + " cm/s")
    return ", ".join(parts) if parts else "no condition stated"


def evidence_line(e):
    name = e["item"] + (" (%s)" % e["row"] if e["row"] else "")
    kind = e["kind"] or e["item_type"]
    ins = ", ".join(e["inside"]) or "none"
    return "%s [%s; %s]: inside on %s" % (name, kind, cond_text(e["conditions"]), ins)


def render_md(out, spec):
    L = []
    env = out["environment"]
    meta = spec["_meta"]
    L.append("INFERENCE MAP: %s" % env["label"].upper())
    L.append("")
    L.append("AI-generated (Claude Code) on 2026-11-14, branch data-lab. Not reviewed by a person or a combustion specialist.")
    L.append("A map of what the held documents say must be known and of what the held items and PSI tests show.")
    L.append("Not a criterion, not a research plan of the team. The state of a link is the team's reading of the items.")
    yrs = out["document_years_cited"]
    L.append("NASA and investigators' documents cited: dated %s to %s (%d documents in all, %d with no year in"
             % (yrs["first"], yrs["last"], yrs["n_documents"], yrs["n_without_year"]))
    L.append("references.json; the challenge page %s is counted but not dated in this range)."
             % ", ".join(yrs["challenge_pages"]))
    L.append("They do not say what NASA considers open today.")
    L.append("")
    L.append("Question: " + meta["question"])
    L.append("Environment used by the rule: oxygen %s%% or more, pressure %s kPa (%s psia) or less, gravity %s."
             % (fmt_num(env["o2_pct_min"]), fmt_num(env["pressure_kpa_max"]), fmt_num(env["pressure_psia_max"]), env["gravity_level"]))
    L.append("  bounds from %s; gravity from %s." % (env["bounds_from"], env["gravity_from"]))
    L.append("State: established = one result item or counted PSI test states every required condition of the link;")
    L.append("       partly = items or tests held, at other conditions or stating fewer of them; missing = none held.")
    L.append("       (L1 is a specification link: established only by an item of type requirement.)")
    L.append("")

    wp = out["walked_path"]
    L.append("PART 1. A PATH ALREADY WALKED: " + wp["question"])
    L.append("  " + wp["note"])
    for i, st in enumerate(wp["steps"], 1):
        L.append("")
        L.append("  %d. %s" % (i, st["step"]))
        if st["items"] == NIH:
            L.append("     " + NIH + " (searched for: " + st["searched_for"] + ")")
        else:
            for q in st["items"]:
                L += quote_lines(q, 5)
    L.append("")

    L.append("PART 2. THE MAP (one line per link)")
    root = out["map"]["root"]
    L.append("  ROOT  %s" % root["label"])
    depth = {"ROOT": 0}
    for lk in out["map"]["links"]:
        depth[lk["id"]] = depth[lk["parent"]] + 1
        pad = "  " + "    " * depth[lk["id"]]
        L.append("%s%-5s [%s] %s" % (pad, lk["id"], lk["state"], lk["label"]))
    L.append("")

    L.append("PART 3. THE QUOTES BEHIND EACH LINK")
    L.append("")
    L.append("ROOT  %s" % root["label"])
    L.append("  claim:")
    L += quote_lines(root["claim"], 4)
    L.append("  why it is a precondition of a criterion:")
    for q in root["why_needed"]:
        L += quote_lines(q, 4)
    L.append("  verification:")
    for q in root["verification"]:
        L += quote_lines(q, 4)
    for lk in out["map"]["links"]:
        L.append("")
        L.append("%s [%s] %s   (parent %s; required conditions: %s)"
                 % (lk["id"], lk["state"], lk["label"], lk["parent"], ", ".join(lk["required_conditions"])))
        L.append("  claim:")
        L += quote_lines(lk["claim"], 4)
        L.append("  why it is a precondition of a criterion:")
        for q in lk["why_needed"]:
            L += quote_lines(q, 4)
        L.append("  established:")
        if not lk["established"]:
            L.append("    none")
        for e in lk["established"]:
            if "psi_need" in e:
                L.append("    PSI %s: %d counted tests inside on every required condition" % (e["psi_need"], e["tests"]))
            else:
                L.append("    " + evidence_line(e))
        L.append("  partly:")
        if not lk["partly"] and not lk["psi"]:
            L.append("    none")
        for e in lk["partly"]:
            L.append("    " + evidence_line(e))
        for p in lk["psi"]:
            by = ", ".join("%s %d" % (a, n) for a, n in p["inside_by_condition"].items())
            L.append("    PSI %s (%s): %d counted tests (%s); inside by condition: %s; on all: %d"
                     % (p["need"], p["need_name"], p["counted_tests"], ", ".join(p["investigations"]) or "none",
                        by, p["inside_on_every_required_condition"]))
        L.append("  missing:")
        if not lk["missing"] and not lk["stated_open"]:
            L.append("    none")
        for m in lk["missing"]:
            if "answer_file_gap" in m:
                L.append("    PSI %s gap code: %s" % (m["psi_need"], m["answer_file_gap"]))
            else:
                L.append("    %s: %s" % (m["condition"], m["text"]))
        for q in lk["stated_open"]:
            L.append("    stated open:")
            L += quote_lines(q, 6)
        L.append("  what would close it (as the documents state it):")
        if lk["what_would_close_it"] == NIH:
            L.append("    " + NIH)
        else:
            for q in lk["what_would_close_it"]:
                L += quote_lines(q, 4)
        L.append("  verification (what the documents say limits or supports such a result):")
        if lk["verification"] == NIH:
            L.append("    " + NIH)
        else:
            for q in lk["verification"]:
                L += quote_lines(q, 4)
    L.append("")
    L.append("Fields marked \"%s\": %s" % (NIH, "; ".join(out["no_item_held"]) or "none"))
    return "\n".join(L) + "\n"


def md_own_lines(md):
    """Lines of the rendering that are not quotes."""
    out = []
    for line in md.splitlines():
        s = line.strip()
        if s.startswith('"') or s.startswith("["):
            continue
        out.append(line)
    return out


# ---------------------------------------------------------------- main

def main():
    spec = load_json(SPEC / "inference_map.json")
    words = spec["_meta"]["forbidden_words"]
    scan_words(own_strings(spec), words, "pipeline/spec/inference_map.json")
    items = load_items()
    records = {"PSI-25": load_json(ROOT / "data" / "psi" / "catalog" / "PSI-25.json")}
    findings = load_findings()
    counted = load_counted_tests()
    env = environment(spec, items, records)
    scenario_id = spec["environment"]["scenario_id"]

    nih = []
    steps = []
    for st in spec["walked_path"]["steps"]:
        s = {"step": st["step"], "items": check_quotes(st["items"], items, spec, records)}
        if st["items"] == NIH:
            s["searched_for"] = st["searched_for"]
            nih.append("walked path step '%s'" % st["step"])
        steps.append(s)

    r = spec["map"]["root"]
    root = {"id": r["id"], "label": r["label"],
            "claim": check_quotes(r["claim"], items, spec, records),
            "why_needed": check_quotes(r["why_needed"], items, spec, records),
            "verification": check_quotes(r["verification"], items, spec, records)}

    ids = {"ROOT"}
    links = []
    for lk in spec["map"]["links"]:
        if lk["parent"] not in ids:
            fail("parent %s of %s is not defined before it" % (lk["parent"], lk["id"]))
        ids.add(lk["id"])
        state, est, part, miss, psi = assess(lk, items, findings, counted, env, scenario_id)
        out = {
            "id": lk["id"], "parent": lk["parent"], "label": lk["label"], "state": state, "rule": lk["rule"],
            "claim": check_quotes(lk["claim"], items, spec, records),
            "why_needed": check_quotes(lk["why_needed"], items, spec, records),
            "required_conditions": lk["required_conditions"],
            "required_conditions_basis": lk["required_conditions_basis"],
            "established": est, "partly": part, "missing": miss, "psi": psi,
            "stated_open": check_quotes(lk["stated_open"], items, spec, records),
            "what_would_close_it": check_quotes(lk["what_would_close_it"], items, spec, records),
            "verification": check_quotes(lk["verification"], items, spec, records),
        }
        for f in ("why_needed", "what_would_close_it", "verification"):
            if out[f] == NIH:
                nih.append("%s %s" % (lk["id"], f))
        links.append(out)

    docs = {}

    def collect(v):
        if isinstance(v, dict):
            if "document" in v and "year" in v and "item" in v:
                docs[v["document"]] = v["year"]
            for x in v.values():
                collect(x)
        elif isinstance(v, list):
            for x in v:
                collect(x)

    collect([steps, root, links])
    for lk in links:
        for e in lk["established"] + lk["partly"]:
            if "item" in e:
                docs[e["document"]] = doc_year(spec, items[e["item"]][1])
    kinds = {ref["id"]: ref["kind"] for _, ref in items.values()}
    dated = sorted(y for d, y in docs.items() if y[:4].isdigit() and kinds[d] != "challenge")
    years_cited = {"first": dated[0], "last": dated[-1], "n_documents": len(docs),
                   "n_without_year": sum(1 for y in docs.values() if not y[:4].isdigit()),
                   "challenge_pages": sorted(d for d in docs if kinds[d] == "challenge"),
                   "documents": dict(sorted(docs.items()))}

    result = {
        "_meta": {
            "generated_by": spec["_meta"]["generated_by"],
            "what_this_is": spec["_meta"]["what_this_is"],
            "authorship": spec["_meta"]["authorship"],
            "state_rule": spec["_meta"]["state_rule"],
            "years": spec["_meta"]["years"],
            "spec": "pipeline/spec/inference_map.json",
            "script": "pipeline/lab/inference_map.py",
        },
        "question": spec["_meta"]["question"],
        "environment": env,
        "document_years_cited": years_cited,
        "walked_path": {"question": spec["walked_path"]["question"], "note": spec["walked_path"]["note"], "steps": steps},
        "map": {"root": root, "links": links},
        "state_counts": {s: sum(1 for l in links if l["state"] == s) for s in ("established", "partly", "missing")},
        "no_item_held": nih,
    }
    md = render_md(result, spec)
    scan_words(md_own_lines(md), words, "the rendering")
    text = json.dumps(result, indent=1, ensure_ascii=False, allow_nan=False) + "\n"
    write_text(OUT / ("inference_map_%s.json" % scenario_id), text)
    write_text(OUT / ("inference_map_%s.md" % scenario_id), md)
    print("inference map: %d links (%s); wrote %s"
          % (len(links), ", ".join("%s %d" % kv for kv in result["state_counts"].items()), OUT.relative_to(ROOT)))


if __name__ == "__main__":
    main()
