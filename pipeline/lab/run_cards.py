# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Run the check of every relation card (experiment on branch data-lab).

Reads pipeline/spec/relation_cards.json, pipeline/spec/references.json,
pipeline/spec/variables.json and data/pipeline/tests.csv; writes
data/pipeline/cards/card_results.json. Every number written is a NASA cell, a
value of a reference item, or arithmetic that the card names (labelled team
computation). Filters, expressions and criteria come from the spec; this file
only knows the check kinds.

Run: python3 pipeline/lab/run_cards.py
"""
import sys

import pandas as pd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import cardlib as cl  # noqa: E402
import governance  # noqa: E402

# decision points of pipeline/lab/model_map.json behind each card's numbers
CARD_POINTS = {
    "bass2_co_co2_ratio": ["D31", "L08", "L03"],
    "of2012_gravity_margin": ["L09"],
    "h2006_moc_vs_pressure": ["L10"],
    "h2007_fixed_pressure": ["L14"],
    "h2011_linear_moc": ["L11", "L03"],
    "bass2_flammability_boundary": ["L13"],
    "flex_loi": ["L13"],
    "droplet_d_squared": ["L12", "M07"],
    "cfi_droplet": ["L14"],
}
RUN_POINTS = ["L15", "L01"]

ID_COLS = ["test_id", "source_file", "source_row"]


def query(df, expr, binds=None):
    return df.query(expr, engine="python", local_dict=binds or {})


def bind_values(items, binds):
    return {k: cl.value_at(items, v) for k, v in (binds or {}).items()}


def row_ref(r, carry=()):
    out = {"test_id": r["test_id"], "source_file": r["source_file"], "source_row": int(r["source_row"])}
    for c in carry:
        out[c] = cl.num(r[c]) if not isinstance(r[c], str) else r[c]
    return out


def rows_ref(df, carry=()):
    df = df.sort_values(["source_file", "source_row"], kind="mergesort")
    return [row_ref(r, carry) for _, r in df.iterrows()]


def decimals(v):
    if isinstance(v, int):
        return 0
    s = repr(float(v))
    return len(s.split(".")[1]) if "." in s and "e" not in s else 0


def half_unit(v):
    return 0.5 * 10 ** (-decimals(v))


# ---------------------------------------------------------------- check kinds

def share_in_published_range(card, chk, df, items, variables):
    rows = query(df, chk["filter"])
    lo, hi = cl.value_at(items, "%s:%s" % (chk["range"]["item"], chk["range"]["key"]))
    rng = {"min": lo, "max": hi, "min_inclusive": chk["range"]["min_inclusive"], "max_inclusive": chk["range"]["max_inclusive"]}
    vals = rows[chk["column"]].astype(float)
    inside = vals.apply(lambda x: cl.value_in(rng, x))
    below = vals < lo
    above = vals > hi
    n = int(len(rows))
    median = float(vals.median())
    share = int(inside.sum()) / n if n else 0.0
    crit = chk["criterion"]
    met = cl.value_in(rng, median) and share > crit["min_share_inside_exclusive"]
    groups = []
    for g, sub in rows.groupby(chk["group_by"], sort=True):
        sv = sub[chk["column"]].astype(float)
        groups.append({chk["group_by"]: g, "rows": int(len(sub)), "inside": int(sv.apply(lambda x: cl.value_in(rng, x)).sum()), "median": cl.num(sv.median())})
    outside = rows[~inside]
    imin = vals.idxmin()
    imax = vals.idxmax()
    return met, {
        "computation_label": "team computation over NASA cells (the ratio column is itself a team derived column)",
        "derived_rule_from_variables": variables["derived"][chk["derived_rule_from_variables"]],
        "published_range": {"item": chk["range"]["item"], "key": chk["range"]["key"], "values": [lo, hi], "min_inclusive": rng["min_inclusive"], "max_inclusive": rng["max_inclusive"]},
        "rows": n,
        "inside": int(inside.sum()),
        "below": int(below.sum()),
        "above": int(above.sum()),
        "share_inside": cl.num(share, 4),
        "median": cl.num(median),
        "lowest": dict(row_ref(rows.loc[imin]), value=cl.num(vals[imin])),
        "highest": dict(row_ref(rows.loc[imax]), value=cl.num(vals[imax])),
        "by_group": groups,
        "rows_outside": [dict(r, value=cl.num(outside.loc[i, chk["column"]])) for i, r in zip(outside.sort_values(["source_file", "source_row"]).index, rows_ref(outside, ["material_id"]))],
    }


def recompute_published(card, chk, df, items, variables):
    rows = cl.value_at(items, "%s:%s" % (chk["item"], chk["rows_key"]))
    out_rows = []
    ok = True
    for row in rows:
        frame = pd.DataFrame([{k: v for k, v in row.items() if not isinstance(v, str)}])
        entries = []
        for rc in chk["recompute"]:
            val = float(frame.eval(rc["expression"]).iloc[0])
            printed = row[rc["printed"]]
            diff = val - printed
            tol = half_unit(printed)
            good = abs(diff) <= tol + 1e-9
            ok = ok and good
            entries.append({"label": rc["label"], "recomputed": cl.num(val), "printed": printed, "difference": cl.num(diff), "tolerance": cl.num(tol), "agrees": good})
        out_rows.append({chk["label_key"]: row[chk["label_key"]], "recompute": entries})
    aggs = []
    for ag in chk["aggregates"]:
        vals = [(r[ag["of"]], r[chk["label_key"]]) for r in rows]
        if ag["op"] != "min":
            cl.fail("unknown aggregate op " + ag["op"])
        best = min(v for v, _ in vals)
        labels = [lab for v, lab in vals if v == best]
        printed = cl.value_at(items, "%s:%s" % (ag["printed"]["item"], ag["printed"]["key"]))
        good = abs(best - printed) <= half_unit(printed) + 1e-9
        ok = ok and good
        aggs.append({"label": ag["label"], "table_value": best, "at": labels, "printed": printed, "printed_in": ag["printed"]["item"], "agrees": good})
    return ok, {
        "computation_label": "team arithmetic on values of the reference items",
        "rows": out_rows,
        "aggregates": aggs,
        "recomputed_values": sum(len(r["recompute"]) for r in out_rows),
        "agreeing_values": sum(e["agrees"] for r in out_rows for e in r["recompute"]),
    }


def pair_order_agreement(card, chk, df, items, variables):
    table = cl.value_at(items, "%s:%s" % (chk["item"], chk["key"]))
    cols = table[chk["columns_key"]]
    names = [k for k in table if k != chk["columns_key"]]
    frame = pd.DataFrame([[table[n][i] for i in range(len(cols))] for n in names], columns=["c%d" % i for i in range(len(cols))], index=names)
    x = frame.eval(chk["x"]["expression"])
    y = frame.eval(chk["y"]["expression"])
    conc, disc, tied = [], [], []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            dx = x[a] - x[b]
            dy = y[a] - y[b]
            pair = [a, b]
            if dx == 0 or dy == 0:
                tied.append(pair)
            elif (dx > 0) == (dy > 0):
                conc.append(pair)
            else:
                disc.append(pair)
    note = chk["tests_csv_note"]
    return len(conc) > len(disc), {
        "computation_label": "team arithmetic on values of the reference item",
        "columns_kpa": cols,
        "x_label": chk["x"]["label"],
        "y_label": chk["y"]["label"],
        "materials": [{"material": n, "x": cl.num(x[n]), "y": cl.num(y[n])} for n in names],
        "pairs": len(conc) + len(disc) + len(tied),
        "concordant": len(conc),
        "discordant": len(disc),
        "tied": len(tied),
        "discordant_pairs": disc,
        "tests_csv": {"label": note["label"], "filter": note["filter"], "rows": int(len(query(df, note["filter"])))},
    }


def moc_domain(chk, items):
    """Per material: are all held MOC values inside the range for which the source states the form?"""
    d = chk["moc_domain"]
    words = cl.check_words(items, d["words"], ("text", "quote"))
    for v in (d["min"], d["max"]):
        if cl.fmt(v) not in words:
            cl.fail("moc_domain bound %s not in the words %r" % (v, words))
    rng = {k: d[k] for k in ("min", "max", "min_inclusive", "max_inclusive")}
    ex = [cl.value_at(items, r) for r in d["example_values"]]
    example = {"material": d["example_label"], "values_of": d["example_values"], "values": ex,
               "inside_stated_moc_range": all(cl.value_in(rng, v) for v in ex)}
    tab = cl.value_at(items, "%s:%s" % (d["table"]["item"], d["table"]["key"]))
    mats = []
    for name in [k for k in tab if k != d["table"]["columns_key"]]:
        vals = tab[name]
        inside = all(cl.value_in(rng, v) for v in vals)
        mats.append({"material": name, "item": d["table"]["item"], "moc_by_column": dict(zip([cl.fmt(c) for c in tab[d["table"]["columns_key"]]], vals)),
                     "inside_stated_moc_range": inside,
                     "form_applied": "domain only (no slope compared)" if inside else "refused: an MOC value lies outside the stated range"})
    return example, {
        "words": d["words"], "range": rng, "reading": d["reading"],
        "example": example,
        "materials": mats,
        "materials_refused": sum(1 for x in mats if not x["inside_stated_moc_range"]),
        "materials_inside": sum(1 for x in mats if x["inside_stated_moc_range"]),
        "table_note": d["table_note"],
    }


def value_in_published_range(card, chk, df, items, variables):
    domain = None
    if "moc_domain" in chk:
        example, domain = moc_domain(chk, items)
        if not example["inside_stated_moc_range"]:
            return None, {"computation_label": "team arithmetic on values of the reference items", "moc_domain": domain,
                          "refused": "the example values lie outside the stated MOC range; no slope is formed"}
    b = bind_values(items, chk["bind"])
    val = float(pd.DataFrame([b]).eval(chk["expression"]).iloc[0])
    bounds = [cl.value_at(items, r) for r in chk["range_bounds"]]
    rng = {"min": min(bounds), "max": max(bounds), "min_inclusive": True, "max_inclusive": True}
    also = [{"value_of": r, "value": cl.value_at(items, r), "inside": cl.value_in(rng, cl.value_at(items, r))} for r in chk["also_inside"]]
    inside = cl.value_in(rng, val)
    return inside and all(a["inside"] for a in also), {
        "computation_label": "team arithmetic on values of the reference items",
        "inputs": {k: {"value_of": chk["bind"][k], "value": v} for k, v in b.items()},
        "expression": chk["expression"],
        "computed": cl.num(val, 4),
        "unit": chk["unit"],
        "published_range": {"bounds_of": chk["range_bounds"], "min": rng["min"], "max": rng["max"]},
        "computed_inside": inside,
        "also_inside": also,
        **({"moc_domain": domain} if domain is not None else {}),
    }


def fact(f, df, items):
    binds = bind_values(items, f.get("bind"))
    rows = query(df, f["filter"], binds)
    out = {"id": f["id"], "op": f["op"], "filter": f["filter"]}
    if binds:
        out["bound_values"] = {k: {"value_of": f["bind"][k], "value": v} for k, v in binds.items()}
    if f["op"] == "count":
        out["value"] = int(len(rows))
    elif f["op"] == "value_counts":
        vc = rows[f["column"]].value_counts()
        out["value"] = {str(k): int(vc[k]) for k in sorted(vc.index)}
    elif f["op"] == "min":
        m = rows[f["column"]].min()
        out["value"] = cl.num(m)
        out["rows_at_value"] = rows_ref(rows[rows[f["column"]] == m], f.get("carry", []))
    elif f["op"] == "rows":
        out["value"] = int(len(rows))
        out["rows"] = rows_ref(rows, f.get("carry", []))
    elif f["op"] == "min_by_group":
        groups = []
        for g, sub in rows.groupby(f["group"], sort=True):
            m = sub[f["column"]].min()
            at = sub[sub[f["column"]] == m]
            groups.append({f["group"]: g, "rows_in_group": int(len(sub)), "lowest_" + f["column"]: cl.num(m), "rows_at_lowest": rows_ref(at, f.get("carry", []))})
        out["value"] = groups
    else:
        cl.fail("unknown fact op " + f["op"])
    return out


def recorded_facts(card, chk, df, items, variables):
    res = {"computation_label": "team counts over NASA cells", "status_reason": chk["status_reason"], "facts": [fact(f, df, items) for f in chk["facts"]]}
    if "published" in chk:
        pub = []
        for p in chk["published"]:
            v = cl.value_at(items, "%s:%s" % (p["item"], p["key"]))
            pub.append({"item": p["item"], "key": p["key"], "value": v, "scaled": cl.num(v * p["scale"], 6), "scaled_unit": p["unit"], "scaled_label": "team arithmetic: value times %s" % cl.fmt(p["scale"])})
        res["published"] = pub
    return None, res


def none_check(card, chk, df, items, variables):
    it = items[chk["item"]]["item"]
    return None, {"item": chk["item"], "value_keys_held": sorted(it.get("values", {}).keys())}


def columns_present(card, chk, df, items, variables):
    rows = query(df, chk["filter"])
    anyv = rows[chk["columns"]].notna().any(axis=1)
    return int(anyv.sum()) == 0, {
        "computation_label": "team counts over NASA cells",
        "rows": int(len(rows)),
        "rows_with_any_column": int(anyv.sum()),
        "per_column": {c: int(rows[c].notna().sum()) for c in chk["columns"]},
    }


def quantile_r6(values, p):
    """NIST e-Handbook 7.2.6.2 percentile (method R6 of Hyndman and Fan): position p(N+1)."""
    x = sorted(values)
    n = len(x)
    pos = p * (n + 1)
    k = int(pos)
    if k < 1:
        return x[0]
    if k >= n:
        return x[-1]
    return x[k - 1] + (pos - k) * (x[k] - x[k - 1])


def ratio_stats(r):
    vals = [float(v) for v in r]
    n = len(vals)
    if not n:
        return {"rows": 0}
    return {
        "rows": n,
        "min": cl.num(min(vals), 4),
        "quartile_1": cl.num(quantile_r6(vals, 0.25), 4),
        "median": cl.num(quantile_r6(vals, 0.5), 4),
        "quartile_3": cl.num(quantile_r6(vals, 0.75), 4),
        "max": cl.num(max(vals), 4),
        "quantile_method": "NIST 7.2.6.2, method R6",
    }


def expression_ratio(card, chk, df, items, variables):
    rows = query(df, chk["filter"]).copy()
    rows = rows.sort_values(chk["order_by"], kind="mergesort")
    rows["_ratio"] = rows.eval(chk["expression"])
    stats = ratio_stats(rows["_ratio"])
    groups = []
    for keys, sub in rows.groupby(chk["group_by"], sort=True):
        groups.append(dict(zip(chk["group_by"], keys), **ratio_stats(sub["_ratio"])))
    srt = rows.sort_values(["_ratio", "source_row"], kind="mergesort")
    k = chk["extremes"]
    carry = ["fuel_material", "test_end", "initial_diameter_mm", "extinction_diameter_mm", "burning_rate_mm2_s", "burn_time_s"]
    lowest = [dict(row_ref(r, carry), ratio=cl.num(r["_ratio"], 4)) for _, r in srt.head(k).iterrows()]
    highest = [dict(row_ref(r, carry), ratio=cl.num(r["_ratio"], 4)) for _, r in srt.tail(k).iloc[::-1].iterrows()]
    out_rows = rows.sort_values(["source_file", "source_row"], kind="mergesort")
    return None, {
        "computation_label": "team computation over NASA cells",
        "expression": chk["expression_label"],
        "filter": chk["filter"],
        "result": stats,
        "by_group": groups,
        "lowest": lowest,
        "highest": highest,
        "quantile_method": chk["quantile_method"],
        "removed": chk["removed_on_2026_11_14"],
        "rows": [dict(row_ref(r, ["fuel_material", "test_end"]), ratio=cl.num(r["_ratio"], 4)) for _, r in out_rows.iterrows()],
    }


KINDS = {
    "share_in_published_range": share_in_published_range,
    "recompute_published": recompute_published,
    "pair_order_agreement": pair_order_agreement,
    "value_in_published_range": value_in_published_range,
    "recorded_facts": recorded_facts,
    "none": none_check,
    "columns_present": columns_present,
    "expression_ratio": expression_ratio,
}


def main():
    spec, items, _ = cl.load_spec()
    variables = cl.load_json(cl.SPEC / "variables.json")
    df = pd.read_csv(cl.ROOT / "data" / "pipeline" / "tests.csv", low_memory=False)
    results = []
    for card in spec["cards"]:
        chk = card["check"]
        if chk["kind"] not in KINDS:
            cl.fail("unknown check kind " + chk["kind"])
        met, res = KINDS[chk["kind"]](card, chk, df, items, variables)
        crit = chk.get("criterion", {})
        if met is None:
            outcome = crit["status_if_refused"] if "status_if_refused" in crit else chk["status"]
        elif "status_if_none" in crit:
            if not met:
                cl.fail(card["id"] + ": rows hold the columns; this card has no check for them")
            outcome = crit["status_if_none"]
        else:
            outcome = crit["status_if_met"] if met else crit["status_if_not_met"]
        entry = {
            "card_id": card["id"],
            "title": card["title"],
            "source_items": card["source_items"],
            "in_our_references": card["in_our_references"],
            "status": outcome if card["in_our_references"] else "not_in_our_references",
        }
        if not card["in_our_references"]:
            entry["check_outcome"] = outcome
            entry["not_in_our_references_note"] = card["not_in_our_references_note"]
        entry["check"] = {"kind": chk["kind"], "description": chk["description"]}
        if crit:
            entry["check"]["criterion"] = crit
        entry["result"] = res
        entry["caption"] = card["caption"]
        if card["id"] not in CARD_POINTS:
            cl.fail("card %s has no decision points in CARD_POINTS" % card["id"])
        entry["governed_by"] = governance.block(CARD_POINTS[card["id"]])
        results.append(entry)
    out = {
        "_meta": {
            "generated_by": "pipeline/lab/run_cards.py (AI-generated code, branch data-lab, experiment, not reviewed). Deterministic: no timestamps.",
            "inputs": ["pipeline/spec/relation_cards.json", "pipeline/spec/references.json", "pipeline/spec/variables.json", "data/pipeline/tests.csv"],
            "status_values": spec["_meta"]["status_values"],
            "numbers": "Every number is a NASA cell of tests.csv, a value of a reference item, or arithmetic named by the card and labelled under computation_label. Criterion parameters are team choices.",
            "criteria_timing": spec["_meta"]["rules"]["criteria_timing"],
        },
        "governed_by": governance.block(RUN_POINTS),
        "summary": [{"card_id": e["card_id"], "status": e["status"], **({"check_outcome": e["check_outcome"]} if "check_outcome" in e else {})} for e in results],
        "cards": results,
    }
    cl.write_json(cl.OUT / "card_results.json", out)
    for s in out["summary"]:
        print(s["card_id"], s["status"], s.get("check_outcome", ""))


if __name__ == "__main__":
    main()
