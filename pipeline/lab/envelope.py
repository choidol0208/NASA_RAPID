# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Envelope position (branch data-lab, experiment).

For each scenario of scenarios.json and each need of needs.json: where the
scenario's nominal point and ranges lie relative to the recorded oxygen and
pressure of the tests counted for the need. Counts, minima, maxima, exact
differences, an exact convex hull and a Pareto set of nearest tests. No model,
weight, scaling, interpolation or probability. Choices and sentences are in
pipeline/spec/lab_numbers.json.

Run: python3 pipeline/lab/envelope.py   (after pipeline/run.py)
"""
import csv
import sys
from fractions import Fraction

from numlib import ROOT, META, fail, frac, dec, load_json, spec, scan_words, write_json, write_text

sys.path.insert(0, str(ROOT / "pipeline"))
from run import in_range  # noqa: E402  the pipeline's own range rule

AXES = ("o2_pct", "pressure_kpa")


def read_csv(path):
    with open(ROOT / path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def hull(points):
    """Convex hull (counter-clockwise, collinear points dropped), exact."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def on_segment(a, b, p):
    return (cross(a, b, p) == 0 and min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def position(h, p):
    """(hull kind, position, inside) of point p; inside is None without a hull."""
    if not h:
        return "none", "no hull", None
    if len(h) == 1:
        return "point", ("boundary" if h[0] == p else "outside"), h[0] == p
    if len(h) == 2:
        on = on_segment(h[0], h[1], p)
        return "segment", ("boundary" if on else "outside"), on
    signs = [cross(h[i], h[(i + 1) % len(h)], p) for i in range(len(h))]
    if any(s < 0 for s in signs):
        return "area", "outside", False
    if any(s == 0 for s in signs):
        return "area", "boundary", True
    return "area", "interior", True


def axis_flags(t, prefix):
    return [f for f in t["flags"].split(";") if f.startswith(prefix)] if t["flags"] else []


def half_unit(written):
    """Half a unit of the last written digit of a Decimal as written."""
    e = written.as_tuple().exponent
    return Fraction(1, 2) * Fraction(10) ** e


def axis_numbers(tests, axis, nominal, h, prefix):
    """tests: tests with the axis recorded; nominal exact; h half unit of the nominal."""
    if not tests:
        return {"tests_recorded": 0}
    values = [frac(t[axis]) for t in tests]
    flagged = [bool(axis_flags(t, prefix)) for t in tests]
    lo, hi = min(values), max(values)
    dist = min(abs(v - nominal) for v in values)
    nearest = sorted({v for v in values if abs(v - nominal) == dist})

    def at(v):
        return {"tests_at_value": sum(1 for x in values if x == v),
                "flagged_tests_at_value": sum(1 for x, f in zip(values, flagged) if x == v and f)}
    return {
        "tests_recorded": len(values),
        "min": dec(lo), "max": dec(hi),
        "min_flagged_tests_at_value": at(lo)["flagged_tests_at_value"],
        "max_flagged_tests_at_value": at(hi)["flagged_tests_at_value"],
        "nominal_within_min_max": lo <= nominal <= hi,
        "nearest": [{"value": dec(v), "gap": dec(v - nominal), "below_nominal_rounding": abs(v - nominal) < h,
                     **at(v)} for v in nearest],
        "flagged_tests": [{"test_id": t["test_id"], "value": t[axis], "flags": axis_flags(t, prefix),
                           "o2_range_as_written": t["o2_range_as_written"]}
                          for t, f in zip(tests, flagged) if f],
    }


def conversions(sources, used):
    """axis -> source_id -> [{from, rule, params}] for the source columns that fill the axis."""
    out = {}
    for s in sources["sources"]:
        if s["id"] not in used:
            continue
        for c in s.get("columns", []):
            to = c.get("to")
            to = to if isinstance(to, list) else [to]
            for a in AXES:
                if a in to and a in used[s["id"]]:
                    out.setdefault(a, {}).setdefault(s["id"], []).append(
                        {"from": c["from"], "rule": c["rule"], "params": c.get("params", {})})
        for a in AXES:
            if a in used[s["id"]] and a in s.get("constants", {}):
                out.setdefault(a, {}).setdefault(s["id"], []).append({"constant": s["constants"][a]})
    for a, by in out.items():
        for sid, cols in by.items():
            for c in cols:
                if c.get("rule") == "number":
                    for t in used[sid][a]:
                        if "." in t and len(t.split(".")[1]) > 4:
                            fail(f"{sid} {a} value {t} has more than 4 decimals (rule 'number' rounds to 4)")
    return out


def gravity_origin(sources):
    """source_id -> 'constant' or 'column' for gravity_level."""
    out = {}
    for s in sources["sources"]:
        col = False
        for c in s.get("columns", []):
            to = c.get("to")
            to = to if isinstance(to, list) else [to]
            col = col or "gravity_level" in to
        out[s["id"]] = "column" if col else ("constant" if "gravity_level" in s.get("constants", {}) else "none")
    return out


def main():
    S = spec()
    E = S["envelope"]
    inp = S["inputs"]
    words = S["forbidden_words"]
    sentences = E["sentences"]
    tests = {t["test_id"]: t for t in read_csv(inp["tests"])}
    links = read_csv(inp["need_tests"])
    sn = {(r["scenario_id"], r["need_id"]): r for r in read_csv(inp["scenario_needs"])}
    scenarios = load_json(ROOT / inp["scenarios"])["scenarios"]
    scen_exact = load_json(ROOT / inp["scenarios"], exact=True)["scenarios"]
    needs = load_json(ROOT / inp["needs"])["needs"]
    g_origin = gravity_origin(load_json(ROOT / inp["sources"]))
    link_vals = sorted({r[E["choices"]["counted_tests"]["column"]] for r in links})
    if E["choices"]["counted_tests"]["equals"] not in link_vals:
        fail(f"objective_link values {link_vals} do not include the counted value")
    counted = {}
    for r in links:
        if r["objective_link"] == E["choices"]["counted_tests"]["equals"]:
            if r["test_id"] not in tests:
                fail(f"{r['test_id']} of need_tests.csv not in tests.csv")
            counted.setdefault(r["need_id"], set()).add(r["test_id"])
    basis_col, basis_val = E["choices"]["ambient_oxygen"]["column"], E["choices"]["ambient_oxygen"]["equals"]
    prefix = E["choices"]["flagged_values"]["flag_prefix_by_axis"]
    sources = load_json(ROOT / inp["sources"])
    out_dir = ROOT / S["output_dir"]
    index = []
    for sc, scx in zip(scenarios, scen_exact):
        assert sc["id"] == scx["id"]
        nominal = {a: frac(scx["nominal"][a]) for a in AXES if a in scx.get("nominal", {})}
        half = {a: half_unit(scx["nominal"][a]) for a in AXES if a in scx.get("nominal", {})}
        used = {}
        has_nominal = all(a in nominal for a in AXES)
        rng = sc["ranges"]
        blocks = []
        for need in needs:
            ids = sorted(counted.get(need["id"], set()))
            amb = [tests[i] for i in ids if tests[i]["o2_pct"] != "" and tests[i][basis_col] == basis_val]
            b = {"need_id": need["id"], "need": need["name"], "counted_tests": len(ids),
                 "counted_tests_with_ambient_oxygen": len(amb),
                 "excluded_o2_not_recorded": sum(1 for i in ids if tests[i]["o2_pct"] == ""),
                 "excluded_basis_not_ambient": sum(1 for i in ids if tests[i]["o2_pct"] != ""
                                                   and tests[i][basis_col] != basis_val)}
            for t in amb:
                for a in AXES:
                    if t[a] != "":
                        used.setdefault(t["source_id"], {}).setdefault(a, set()).add(t[a])
            # ranges (pipeline rule, float as the pipeline reads; exact rule checked beside it)
            o_in = [t for t in amb if rng.get("o2_pct") and in_range(float(t["o2_pct"]), rng["o2_pct"])]
            p_rec = [t for t in amb if t["pressure_kpa"] != ""]
            p_in = [t for t in p_rec if rng.get("pressure_kpa") and in_range(float(t["pressure_kpa"]), rng["pressure_kpa"])]
            both = [t for t in o_in if t in p_in]
            exact_rng = {a: {k: (frac(v) if k in ("min", "max") and v is not None else v)
                             for k, v in scx["ranges"][a].items()} for a in AXES if a in scx["ranges"]}
            both_exact = [t for t in amb if all(a in exact_rng and t[a] != "" and in_range(frac(t[a]), exact_rng[a])
                                                for a in AXES)]
            if [t["test_id"] for t in both] != [t["test_id"] for t in both_exact]:
                fail(f"{sc['id']} {need['id']}: float and exact range reading differ")
            row = sn.get((sc["id"], need["id"]))
            if row is None or int(row["tests_atmosphere"]) != len(both):
                fail(f"{sc['id']} {need['id']}: joint range count {len(both)} != tests_atmosphere "
                     f"{row and row['tests_atmosphere']} of scenario_needs.csv")
            b["ranges"] = {
                "o2_pct": ({"set": True, "tests_inside": len(o_in), "of_tests": len(amb)} if rng.get("o2_pct")
                           else {"set": False}),
                "pressure_kpa": ({"set": True, "tests_inside": len(p_in), "of_tests": len(p_rec)} if rng.get("pressure_kpa")
                                 else {"set": False}),
                "both_inside": len(both) if rng.get("o2_pct") and rng.get("pressure_kpa") else "not set",
                "both_inside_equals_scenario_needs_tests_atmosphere": True,
                "both_inside_test_ids": sorted(t["test_id"] for t in both),
            }
            joint = [t for t in amb if t["pressure_kpa"] != ""]
            gl = sc["gravity_level"]
            origins = sorted({g_origin.get(t["source_id"], "none") for t in amb})
            b["gravity"] = {
                "scenario_gravity_level": gl,
                "levels_recorded": sorted({t["gravity_level"] for t in amb}),
                "origin_of_gravity_level": origins,
                "tests_same_level_of_ambient_oxygen_tests": (sum(t["gravity_level"] == gl for t in amb)
                                                            if gl is not None else "not set"),
                "tests_same_level_of_joint_tests": (sum(t["gravity_level"] == gl for t in joint)
                                                   if gl is not None else "not set"),
            }
            if has_nominal and amb:
                b["nominal"] = {
                    "axes": {
                        "o2_pct": axis_numbers(amb, "o2_pct", nominal["o2_pct"], half["o2_pct"], prefix["o2_pct"]),
                        "pressure_kpa": axis_numbers(p_rec, "pressure_kpa", nominal["pressure_kpa"],
                                                     half["pressure_kpa"], prefix["pressure_kpa"]),
                    }
                }
                pts = [(frac(t["o2_pct"]), frac(t["pressure_kpa"])) for t in joint]
                h = hull(pts)
                nom = (nominal["o2_pct"], nominal["pressure_kpa"])
                kind, pos, inside = position(h, nom)
                ho, hp = half["o2_pct"], half["pressure_kpa"]
                corners = [(nom[0] + so * ho, nom[1] + sp * hp) for so in (-1, 1) for sp in (-1, 1)]
                corners_in = None if kind == "none" else sum(1 for c in corners if position(h, c)[2])
                deltas = [(abs(p[0] - nom[0]), abs(p[1] - nom[1])) for p in pts]
                pareto = []
                for i, (t, d) in enumerate(zip(joint, deltas)):
                    dominated = any(e[0] <= d[0] and e[1] <= d[1] and (e[0] < d[0] or e[1] < d[1])
                                    for j, e in enumerate(deltas) if j != i)
                    if not dominated:
                        pareto.append((d, t, pts[i]))
                pareto.sort(key=lambda x: (x[0], x[1]["test_id"]))
                comp = {}
                for t in joint:
                    k = (t["investigation_id"], t["fuel_phase"], t["sample_geometry"])
                    comp[k] = comp.get(k, 0) + 1
                b["nominal"]["joint"] = {
                    "tests_with_both_recorded": len(joint),
                    "distinct_points": len(set(pts)),
                    "investigations": sorted({t["investigation_id"] for t in joint},
                                             key=lambda x: int(x.split("-")[1])),
                    "composition": [{"investigation_id": k[0], "fuel_phase": k[1], "sample_geometry": k[2], "tests": v}
                                    for k, v in sorted(comp.items(), key=lambda kv: (int(kv[0][0].split("-")[1]),
                                                                                     kv[0][1], kv[0][2]))],
                    "rounding_half_unit": {"o2_pct": dec(ho), "pressure_kpa": dec(hp)},
                    "rounding_box_corners_inside": corners_in,
                    "hull_kind": kind,
                    "hull_has_area": kind == "area",
                    "hull_vertices_ccw": [[dec(v[0]), dec(v[1])] for v in h],
                    "nominal_position": pos,
                    "nominal_inside_hull": inside,
                    "nearest_tests_pareto": [{
                        "test_id": t["test_id"], "investigation_id": t["investigation_id"],
                        "o2_pct": dec(p[0]), "pressure_kpa": dec(p[1]),
                        "delta_o2_pct": dec(p[0] - nom[0]), "delta_pressure_kpa": dec(p[1] - nom[1]),
                        "delta_o2_below_nominal_rounding": abs(p[0] - nom[0]) < ho,
                        "delta_pressure_below_nominal_rounding": abs(p[1] - nom[1]) < hp,
                        "flags_on_axes": [f for a in AXES for f in axis_flags(t, prefix[a])],
                        "source_file": t["source_file"], "source_row": t["source_row"]} for d, t, p in pareto],
                }
                if kind == "none":
                    b["nominal"]["notes"] = [sentences["no_hull"]]
            else:
                b["nominal"] = {"notes": ([sentences["no_tests"]] if not amb else [])
                                + ([sentences["no_nominal"]] if not has_nominal else [])}
            blocks.append(b)
        all_origins = sorted({o for b in blocks for o in b["gravity"]["origin_of_gravity_level"]})
        notes = [sentences["values_source"], sentences["no_outcome"], sentences["hull_inside"],
                 sentences["hull_outside"], sentences["no_hull"], sentences["pooled"], sentences["nearest_separate"],
                 sentences["flagged"], sentences["counts_not_added"]]
        notes += [sentences["nominal_not_design"], sentences["nominal_rounding"]] if has_nominal else [sentences["no_nominal"]]
        if any(a not in AXES for a in sc["ranges"]):
            notes.append(sentences["ranges_not_applied"])
        if "column" in all_origins:
            notes.append(sentences["gravity_column"])
        else:
            levels = sorted({lv for b in blocks for lv in b["gravity"]["levels_recorded"]})
            if levels not in ([], ["microgravity"]):
                fail(f"gravity_constant sentence names microgravity, levels recorded are {levels}")
            notes.append(sentences["gravity_constant"])
        gravity_note = notes[-1]
        if sc["gravity_level"] is None:
            notes.append(sentences["gravity_not_set"])
            gravity_note += " " + sentences["gravity_not_set"]
        doc = {
            "_meta": {"generated_by": META, "script": "pipeline/lab/envelope.py", "spec": "pipeline/spec/lab_numbers.json",
                      "inputs": inp, "numbers": "exact decimal strings"},
            "scenario": {"id": sc["id"], "label": sc["label"],
                         "nominal": {a: dec(nominal[a]) for a in nominal},
                         "ranges": scenarios_ranges(scx), "gravity_level": sc["gravity_level"]},
            "conversions": {a: {sid: cols for sid, cols in sorted(by.items())}
                            for a, by in sorted(conversions(sources, used).items())},
            "choices": {k: v["value"] for k, v in E["choices"].items()},
            "notes": notes,
            "gravity_note": gravity_note,
            "needs": blocks,
        }
        scan_words(doc, words, f"envelope {sc['id']}")
        md = render_md(doc)
        scan_words(md, words, f"envelope {sc['id']} md")
        write_json(out_dir / f"envelope_{sc['id']}.json", doc)
        write_text(out_dir / f"envelope_{sc['id']}.md", md)
        index.append({"scenario_id": sc["id"], "json": f"envelope_{sc['id']}.json", "md": f"envelope_{sc['id']}.md",
                      "needs": {b["need_id"]: {
                          "counted_tests_with_ambient_oxygen": b["counted_tests_with_ambient_oxygen"],
                          "nominal_inside_hull": b.get("nominal", {}).get("joint", {}).get("nominal_inside_hull"),
                          "hull_kind": b.get("nominal", {}).get("joint", {}).get("hull_kind"),
                          "both_ranges_inside": b["ranges"]["both_inside"]} for b in blocks}})
    return index


def scenarios_ranges(scx):
    out = {}
    for a, r in sorted(scx["ranges"].items()):
        out[a] = {k: (dec(frac(v)) if k in ("min", "max") and v is not None else v) for k, v in sorted(r.items())}
        out[a]["applied"] = a in AXES
    return out


def fmt_range(name, r):
    lo = r.get("min")
    hi = r.get("max")
    lo_inc = r.get("min_inclusive", True)
    hi_inc = r.get("max_inclusive", False)
    left = "(-inf" if lo is None else ("[" if lo_inc else "(") + lo
    right = "+inf)" if hi is None else hi + ("]" if hi_inc else ")")
    return f"{name} {left}, {right}"


def fmt_axis(a):
    if a.get("tests_recorded", 0) == 0:
        return "0 | - | - | - | -"
    near = "; ".join(f"{n['value']} (gap {n['gap']}{', below nominal rounding' if n['below_nominal_rounding'] else ''}, "
                     f"{n['tests_at_value']} tests, {n['flagged_tests_at_value']} flagged)" for n in a["nearest"])
    return (f"{a['tests_recorded']} | {a['min']} ({a['min_flagged_tests_at_value']} flagged) | "
            f"{a['max']} ({a['max_flagged_tests_at_value']} flagged) | {'yes' if a['nominal_within_min_max'] else 'no'} | {near}")


def render_md(doc):
    sc = doc["scenario"]
    L = [f"# Envelope position: {sc['label']} (`{sc['id']}`)", "",
         "*AI-generated (Claude Code), 2026-11-14. Not human-reviewed. Experiment on branch data-lab.*", ""]
    nom = sc["nominal"]
    L.append("Nominal point: " + (", ".join(f"{k} = {v}" for k, v in sorted(nom.items())) or "none") +
             f". Gravity level: {sc['gravity_level'] or 'not set'}.")
    L.append("Ranges: " + ("; ".join(fmt_range(k, r) + ("" if r["applied"] else " (not applied: not an axis)")
                                     for k, r in sc["ranges"].items()) or "none") + ".")
    if doc["conversions"]:
        L.append("Conversions by the pipeline (pipeline/spec/sources.json): " + "; ".join(
            f"{a} of {sid}: " + ", ".join(
                (f"'{c['from']}' rule {c['rule']}" + (f" factor {c['params']['factor']}" if "factor" in c["params"] else "")
                 if "rule" in c else f"constant {c['constant']}") for c in cols)
            for a, by in doc["conversions"].items() for sid, cols in by.items()) + ".")
    L += ["", "## Notes", ""] + [f"- {n}" for n in doc["notes"]]
    L += ["", "## Choices (spec parameters)", ""] + [f"- `{k}`: {v}" for k, v in sorted(doc["choices"].items())]
    L += ["", "## Summary per need", "",
          "| Need | counted tests | with ambient O2 | with O2 and pressure | pooled tests (investigation, phase, geometry: tests) | hull | nominal position | O2 in range | pressure in range | both in range | gravity_level string equal to scenario's (table constant, not a match in data) |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for b in doc["needs"]:
        j = b.get("nominal", {}).get("joint", {})
        r = b["ranges"]
        o = r["o2_pct"]; p = r["pressure_kpa"]
        comp = "; ".join(f"{c['investigation_id']} {c['fuel_phase']} {c['sample_geometry']}: {c['tests']}"
                         for c in j.get("composition", [])) or "-"
        L.append(f"| {b['need_id']} {b['need']} | {b['counted_tests']} | {b['counted_tests_with_ambient_oxygen']} | "
                 f"{j.get('tests_with_both_recorded', '-')} | {comp} | {j.get('hull_kind', '-')} | {j.get('nominal_position', '-')} | "
                 f"{str(o['tests_inside']) + ' of ' + str(o['of_tests']) if o['set'] else 'not set'} | "
                 f"{str(p['tests_inside']) + ' of ' + str(p['of_tests']) if p['set'] else 'not set'} | "
                 f"{r['both_inside']} | {b['gravity']['tests_same_level_of_joint_tests']} |")
    L += ["", doc["gravity_note"]]
    for b in doc["needs"]:
        L += ["", f"## {b['need_id']} {b['need']}", ""]
        n = b.get("nominal", {})
        L.append(f"Counted tests left out: {b['excluded_o2_not_recorded']} without o2_pct, "
                 f"{b['excluded_basis_not_ambient']} with o2_basis not ambient.")
        L.append("")
        if "axes" not in n:
            L += [x for note in n.get("notes", []) for x in (note, "")][:-1]
            continue
        L += ["| Axis | tests recorded | min | max | nominal within [min, max] | nearest recorded value |",
              "|---|---|---|---|---|---|"]
        for a in AXES:
            L.append(f"| {a} | {fmt_axis(n['axes'][a])} |")
        if any(n["axes"][a].get("flagged_tests") for a in AXES):
            L.append("")
        for a in AXES:
            for f in n["axes"][a].get("flagged_tests", []):
                L.append(f"- flagged test ({a}): {f['test_id']} value {f['value']}, flags {', '.join(f['flags'])}"
                         + (f", written in source as '{f['o2_range_as_written']}'" if f["o2_range_as_written"] else ""))
        j = n["joint"]
        if j["hull_kind"] == "none":
            L += ["", f"Tests with both recorded: 0. Hull: none. Nominal point: no position."]
            L += [""] + [x for note in n.get("notes", []) for x in (note, "")][:-1]
            continue
        L += ["", f"Tests with both recorded: {j['tests_with_both_recorded']} ({j['distinct_points']} distinct points; "
              f"{', '.join(j['investigations'])}). Hull: {j['hull_kind']}"
              f"{'' if j['hull_has_area'] else ' (no area)'}. Nominal point: {j['nominal_position']}, inside = "
              f"{'true' if j['nominal_inside_hull'] else 'false'}. Rounding box (nominal +- "
              f"{j['rounding_half_unit']['o2_pct']} o2_pct, +- {j['rounding_half_unit']['pressure_kpa']} pressure_kpa): "
              f"{j['rounding_box_corners_inside']} of 4 corners inside.", ""]
        if j["nearest_tests_pareto"]:
            L += ["Nearest tests (Pareto set in |delta o2_pct|, |delta pressure_kpa|):", "",
                  "| test | investigation | o2_pct | pressure_kpa | delta o2_pct | delta pressure_kpa | flags on axes | source |",
                  "|---|---|---|---|---|---|---|---|"]
            for t in j["nearest_tests_pareto"]:
                L.append(f"| {t['test_id']} | {t['investigation_id']} | {t['o2_pct']} | {t['pressure_kpa']} | "
                         f"{t['delta_o2_pct']}{' (below nominal rounding)' if t['delta_o2_below_nominal_rounding'] else ''} | "
                         f"{t['delta_pressure_kpa']}{' (below nominal rounding)' if t['delta_pressure_below_nominal_rounding'] else ''} | "
                         f"{', '.join(t['flags_on_axes']) or '-'} | {t['source_file']} row {t['source_row']} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
