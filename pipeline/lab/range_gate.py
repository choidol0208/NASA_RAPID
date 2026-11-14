# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Range gate of the relation cards (experiment on branch data-lab).

For every scenario of pipeline/spec/scenarios.json and every card of
pipeline/spec/relation_cards.json, compare the scenario's oxygen, pressure,
flow ranges and gravity level with the card's stated validity, axis by axis,
and write data/pipeline/cards/gate_<scenario_id>.json with one fixed sentence
per card, a headline, and the recorded-test counts of the scenario's cells of
the coverage grid per fuel phase (copied from data/pipeline/coverage_grid.csv).

Nothing is predicted: the gate says whether a card's stated range excludes
the scenario, not what happens there. Rules and sentences are in the spec.

Run: python3 pipeline/lab/range_gate.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cardlib as cl  # noqa: E402

SCENARIO_KEYS = {"oxygen": "o2_pct", "pressure": "pressure_kpa", "flow": "flow_cms"}


def words_of(axis_spec):
    if axis_spec["words"] == "unstated":
        return None, []
    texts, items = [], []
    for w in axis_spec["words"]:
        texts.append(w.get("words", "values key " + w.get("key", "")))
        if w["item"] not in items:
            items.append(w["item"])
    return " / ".join(texts), items


def card_render(norm, unit):
    if norm["kind"] == "points":
        lead = "the single value " if len(norm["values"]) == 1 else "the single values "
        return lead + ", ".join(cl.fmt(v) for v in norm["values"]) + " " + unit
    return cl.render_range(cl.full_range(norm), unit)


def compare_axis(axis, card, scenario, units):
    v = card["validity"][axis]
    norm = v["normalized"]
    words, items = words_of(v)
    out = {"axis": axis}
    if axis == "gravity":
        level = scenario.get("gravity_level")
        out["scenario"] = level
        out["card"] = norm
        if norm == "unstated":
            out["result"] = "card_unstated"
        elif level is None:
            out["result"] = "scenario_unstated"
        elif level in norm:
            out["result"] = "inside"
        else:
            out["result"] = "outside"
            out["overlap"] = "none"
    else:
        key = SCENARIO_KEYS[axis]
        sr = scenario.get("ranges", {}).get(key)
        unit = units[axis]
        out["scenario"] = cl.render_range(cl.full_range(sr), unit) if sr else None
        out["card"] = card_render(norm, unit) if isinstance(norm, dict) else norm
        if not isinstance(norm, dict):
            out["result"] = "card_unstated"
        elif sr is None:
            out["result"] = "scenario_unstated"
        else:
            s = cl.full_range(sr)
            if norm["kind"] == "points":
                hit = any(cl.value_in(s, p) for p in norm["values"])
                out["result"] = "outside"
                out["overlap"] = "partial" if hit else "none"
            else:
                c = cl.full_range(norm)
                if cl.contains(c, s):
                    out["result"] = "inside"
                else:
                    out["result"] = "outside"
                    out["overlap"] = "partial" if cl.overlaps(c, s) else "none"
    if words is not None:
        out["card_words"] = words
        out["card_items"] = items
    if v.get("words_only"):
        out["card_words_only"] = True
    return out


def fill(template, **kw):
    return template.format(**kw)


def join_or_none(spec, names):
    return ", ".join(names) if names else spec["_meta"]["gate"]["sentences"]["none_word"]


def gate_card(spec, card, scenario):
    m = spec["_meta"]
    S = m["gate"]["sentences"]
    axes = [compare_axis(a, card, scenario, m["axes"]["units"]) for a in m["axes"]["compared_by_gate"]]
    by = {a["axis"]: a for a in axes}
    outside = [a for a in axes if a["result"] == "outside"]
    common = dict(title=card["title"], card_id=card["id"], scenario_label=scenario["label"])
    summary = "; ".join("%s %s" % (a["axis"], a["result"]) for a in axes)
    if not card["in_our_references"]:
        overall, reason = "not_applicable", "not_in_our_references"
        sentence = fill(S["not_applicable__not_in_our_references"], **common)
    elif outside:
        overall, reason = "outside_stated_range", "axis_outside"
        details = " ".join(fill(S["outside_axis"], axis=a["axis"], scenario_range=a["scenario"], words=a["card_words"], items=", ".join(a["card_items"]), card_range=a["card"] if isinstance(a["card"], str) else ", ".join(a["card"]), overlap=a["overlap"]) for a in outside)
        sentence = fill(S["outside_stated_range"], outside_details=details, **common)
    elif by["gravity"]["result"] != "inside":
        overall = "not_applicable"
        reason = "gravity_" + by["gravity"]["result"]
        sentence = fill(S["not_applicable__" + reason], axes_summary=summary, **common)
    else:
        overall, reason = "may_be_quoted_here", "no_axis_outside"
        inside = [a["axis"] for a in axes if a["result"] == "inside" and a["axis"] != "gravity"]
        clause = fill(S["inside_clause"], inside_axes=", ".join(inside)) if inside else ""
        sentence = fill(S["may_be_quoted_here"], inside_clause=clause,
                        card_unstated_axes=join_or_none(spec, [a["axis"] for a in axes if a["result"] == "card_unstated"]),
                        scenario_unstated_axes=join_or_none(spec, [a["axis"] for a in axes if a["result"] == "scenario_unstated"]),
                        **common)
    cl.forbidden_check(spec, sentence, "gate sentence %s/%s" % (scenario["id"], card["id"]))
    shown = {}
    for a in m["axes"]["shown_not_compared"]:
        v = card["validity"][a]
        w, its = words_of(v)
        shown[a] = {"card_words": w if w is not None else "unstated", "card_items": its, "normalized": v["normalized"]}
    return {
        "card_id": card["id"],
        "title": card["title"],
        "in_our_references": card["in_our_references"],
        "axes": axes,
        "shown_not_compared": shown,
        "overall": overall,
        "reason": reason,
        "sentence": sentence,
    }


def bins_hit(bins, r):
    if r is None:
        return []
    s = cl.full_range(r)
    return [b for b in bins if cl.overlaps(cl.full_range(b), s)]


def coverage(spec, scenario, cov, grid):
    S = spec["_meta"]["gate"]["sentences"]
    ob = bins_hit(cov["dimensions"]["o2_pct"]["bins"], scenario.get("ranges", {}).get("o2_pct"))
    pb = bins_hit(cov["dimensions"]["pressure_kpa"]["bins"], scenario.get("ranges", {}).get("pressure_kpa"))
    has_cells = bool(ob) and bool(pb)
    phases = []
    for phase in sorted(grid["fuel_phase"].unique()):
        g = grid[grid["fuel_phase"] == phase]
        n_phase = int(g["tests"].sum())
        n_p = int(g[g["pressure_bin"] != "not_recorded"]["tests"].sum())
        entry = {"fuel_phase": phase, "rows_of_phase": n_phase, "rows_with_recorded_pressure": n_p}
        if has_cells:
            amb = g[g["o2_basis"] == "ambient"]
            cells, texts = [], []
            for o in ob:
                for p in pb:
                    row = amb[(amb["o2_bin"] == o["id"]) & (amb["pressure_bin"] == p["id"])]
                    n = int(row["tests"].sum()) if len(row) else 0
                    inv = row["investigation_ids"].iloc[0] if len(row) and isinstance(row["investigation_ids"].iloc[0], str) else ""
                    cells.append({"o2_bin": o["id"], "pressure_bin": p["id"], "o2_bin_label": o["label"], "pressure_bin_label": p["label"], "tests": n, "investigation_ids": inv})
                    texts.append(fill(S["coverage_cell"], oxygen_label=o["label"], pressure_label=p["label"], tests=n))
            nr = amb[amb["o2_bin"].isin([o["id"] for o in ob]) & (amb["pressure_bin"] == "not_recorded")]
            n_nr = int(nr["tests"].sum())
            entry.update({"cells": cells, "tests_in_oxygen_bins_pressure_not_recorded": n_nr})
            entry["sentence"] = fill(S["coverage_phase"], fuel_phase=phase, cells_text="; ".join(texts), n_oxygen_no_pressure=n_nr, n_with_pressure=n_p, n_phase=n_phase)
        else:
            entry["cells"] = []
            entry["sentence"] = fill(S["coverage_no_cells"], fuel_phase=phase, n_with_pressure=n_p, n_phase=n_phase)
        cl.forbidden_check(spec, entry["sentence"], "coverage sentence")
        phases.append(entry)
    return {
        "rule": spec["_meta"]["gate"]["cells_rule"],
        "scenario_oxygen_bins": [o["id"] for o in ob],
        "scenario_pressure_bins": [p["id"] for p in pb],
        "has_cells": has_cells,
        "by_fuel_phase": phases,
    }


def main():
    spec, items, _ = cl.load_spec()
    scenarios = cl.load_json(cl.SPEC / "scenarios.json")["scenarios"]
    cov = cl.load_json(cl.SPEC / "coverage.json")
    grid = pd.read_csv(cl.ROOT / "data" / "pipeline" / "coverage_grid.csv")
    S = spec["_meta"]["gate"]["sentences"]
    written = set()
    for sc in scenarios:
        cards = [gate_card(spec, c, sc) for c in spec["cards"]]
        quotable = [c["card_id"] for c in cards if c["overall"] == "may_be_quoted_here"]
        n_out = sum(c["overall"] == "outside_stated_range" for c in cards)
        n_na = sum(c["overall"] == "not_applicable" for c in cards)
        if quotable:
            result = "some_cards_may_be_quoted"
            sentence = fill(S["headline_some"], n_cards=len(cards), n_quotable=len(quotable), scenario_label=sc["label"], quotable_ids=", ".join(quotable), n_outside=n_out, n_not_applicable=n_na)
        else:
            result = "no_held_relation_covers_this_condition"
            sentence = fill(S["headline_none"], n_cards=len(cards), scenario_label=sc["label"], n_outside=n_out, n_not_applicable=n_na)
        cl.forbidden_check(spec, sentence, "headline " + sc["id"])
        out = {
            "_meta": {
                "generated_by": "pipeline/lab/range_gate.py (AI-generated code, branch data-lab, experiment, not reviewed). Deterministic: no timestamps.",
                "inputs": ["pipeline/spec/relation_cards.json", "pipeline/spec/references.json", "pipeline/spec/scenarios.json", "pipeline/spec/coverage.json", "data/pipeline/coverage_grid.csv"],
                "axis_values": spec["_meta"]["gate"]["axis_values"],
                "containment_rule": spec["_meta"]["gate"]["containment_rule"],
                "overall": spec["_meta"]["gate"]["overall"],
                "overall_note": spec["_meta"]["gate"]["overall_note"],
                "range_notation": "[a, b] includes both ends, (a, b) neither; -inf or +inf marks an end the range does not set.",
            },
            "scenario": {"id": sc["id"], "label": sc["label"], "ranges": sc.get("ranges", {}), "gravity_level": sc.get("gravity_level")},
            "headline": {"result": result, "may_be_quoted_here": quotable, "outside_stated_range": n_out, "not_applicable": n_na, "sentence": sentence},
            "cards": cards,
            "coverage": coverage(spec, sc, cov, grid),
        }
        name = "gate_%s.json" % sc["id"]
        cl.write_json(cl.OUT / name, out)
        written.add(name)
        print(sc["id"], result, quotable)
    for p in sorted(cl.OUT.glob("gate_*.json")):
        if p.name not in written:
            p.unlink()


if __name__ == "__main__":
    main()
