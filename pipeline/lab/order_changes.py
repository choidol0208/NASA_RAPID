# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Order changes in published tables (branch data-lab, experiment).

For each table named in pipeline/spec/lab_numbers.json (order_changes.tables)
and each quantity: for every pair of condition columns and every pair of
materials, the pair is classified as same order, reversed, tie in one column
only or tie in both, from the values held in the reference item exactly as
printed (no tolerance). Kendall tau-b per column pair, computed exactly. Every
reference item with 'values' that is not a table here must be listed in the
spec as rejected, with its reason.

Run: python3 pipeline/lab/order_changes.py
"""
from decimal import Decimal, ROUND_HALF_EVEN, getcontext
from fractions import Fraction
from itertools import combinations
from math import isqrt

from numlib import ROOT, META, fail, frac, dec, load_json, spec, scan_words, write_json, write_text
import governance

# decision points of pipeline/lab/model_map.json behind each field (spec: order_changes.governed_by_fields)
FIELD_POINTS = spec()["order_changes"]["governed_by_fields"]
CLASSES = ("concordant", "discordant", "tied_first_column_only", "tied_second_column_only", "tied_both_columns")


def sign(x):
    return (x > 0) - (x < 0)


def held(x):
    """The digits as held in the item (JSON number read as Decimal keeps '18.0')."""
    return str(x)


def items_by_id(refs):
    out = {}
    for d in refs["references"]:
        for it in d["items"]:
            out[it["id"]] = (d, it)
    return out


def matrix(tab, item):
    """[(quantity id, label, columns [labels], criteria, rows [(material, [values], [held strings], held)])]"""
    v = item["values"]
    out = []
    if tab["layout"] == "dict_of_lists":
        for k in tab["path"]:
            v = v[k]
        cols = [held(c) for c in v[tab["columns_key"]]]
        rows = [(m, [frac(x) for x in vals], [held(x) for x in vals], None)
                for m, vals in v.items() if m != tab["columns_key"]]
        for q in tab["quantities"]:
            out.append((q["id"], q["label"], cols, [q.get("criterion")] * len(cols), rows))
    elif tab["layout"] == "rows":
        for q in tab["quantities"]:
            cols = [c[0] for c in q["columns"]]
            crit = [c[2] if len(c) > 2 else None for c in q["columns"]]
            rows = [(r[tab["material_key"]], [frac(r[c[1]]) for c in q["columns"]], [held(r[c[1]]) for c in q["columns"]],
                     held(r[tab["held_key"]]) if tab.get("held_key") else None) for r in v["rows"]]
            out.append((q["id"], q["label"], cols, crit, rows))
    else:
        fail(f"unknown layout {tab['layout']}")
    for _, _, cols, _, rows in out:
        if len(rows) < 3 or len(cols) < 2 or any(len(r[1]) != len(cols) for r in rows):
            fail(f"{tab['id']}: needs at least 3 materials and 2 columns of equal length")
    return out


def tau_b(nc, nd, tx, ty, n0, n1, n2, digits):
    """Kendall tau-b as on the NIST Dataplot page: (N_c - N_d) / sqrt((N_c + N_d + T_x)(N_c + N_d + T_y))."""
    den = (nc + nd + tx) * (nc + nd + ty)
    if den != (n0 - n1) * (n0 - n2):
        fail("tau-b denominator differs between the Dataplot form and (n0 - n1)(n0 - n2)")
    if den == 0:
        return {"numerator": nc - nd, "under_sqrt": den, "value": "undefined"}
    getcontext().prec = 50
    val = Decimal(nc - nd) / Decimal(den).sqrt()
    r = isqrt(den)
    if r * r == den:
        f = Fraction(nc - nd, r)
        exact = f"{f.numerator}/{f.denominator}" if f.denominator != 1 else str(f.numerator)
    else:
        exact = "irrational (integer under the square root is not a square)"
    q = val.quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_EVEN)
    return {"numerator": nc - nd, "under_sqrt": den, "value": str(q), "value_exact": exact}


def analyse(tab, qid, qlabel, cols, crit, rows, digits):
    n = len(rows)
    n0 = n * (n - 1) // 2
    pairs_out = []
    has_held = rows[0][3] is not None
    for (i, c1), (j, c2) in combinations(list(enumerate(cols)), 2):
        counts = {c: 0 for c in CLASSES}
        counts_hd = dict(counts)
        n1 = n2 = 0
        listed = []
        for a, b in combinations(rows, 2):
            s1 = sign(a[1][i] - b[1][i])
            s2 = sign(a[1][j] - b[1][j])
            n1 += s1 == 0
            n2 += s2 == 0
            cls = ("tied_both_columns" if s1 == 0 and s2 == 0 else "tied_first_column_only" if s1 == 0
                   else "tied_second_column_only" if s2 == 0 else "concordant" if s1 == s2 else "discordant")
            counts[cls] += 1
            if has_held and a[3] != b[3]:
                counts_hd[cls] += 1
            if cls in ("discordant", "tied_first_column_only", "tied_second_column_only"):
                e = {"class": cls, "material_a": a[0], "material_b": b[0],
                     "a_col1": a[2][i], "b_col1": b[2][i],
                     "a_col2": a[2][j], "b_col2": b[2][j]}
                if has_held:
                    e["held_a"], e["held_b"] = a[3], b[3]
                    e["held_same"] = a[3] == b[3]
                listed.append(e)
        extra = {}
        if has_held:
            extra["counts_held_differs"] = counts_hd
        if crit[i] is not None:
            extra["criterion_1"], extra["criterion_2"], extra["same_criterion"] = crit[i], crit[j], crit[i] == crit[j]
        pairs_out.append({"column_1": c1, "column_2": c2, "material_pairs": n0, "counts": counts, **extra,
                          "kendall_tau_b": tau_b(counts["concordant"], counts["discordant"],
                                                 counts["tied_first_column_only"], counts["tied_second_column_only"],
                                                 n0, n1, n2, digits),
                          "ties_in_column_1": n1, "ties_in_column_2": n2,
                          "governed_by": {k: governance.short(v) for k, v in FIELD_POINTS.items()
                                          if k.split(".")[0] in ("counts", "kendall_tau_b")
                                          or (k in extra)},
                          "discordant_and_tied_one_column_pairs": listed})
    return {"quantity": qid, "label": qlabel, "columns": cols, "materials": n,
            "values": [{"material": m, "values": hs, **({"held": h} if h is not None else {})}
                       for m, v, hs, h in rows],
            "column_pairs": pairs_out}


def render_md(doc):
    t = doc["table"]
    L = [f"# Order changes: `{t['id']}`", "",
         "*AI-generated (Claude Code), 2026-11-14. Not human-reviewed. Experiment on branch data-lab.*", "",
         f"Item `{t['item']}` of `{t['document']}` ({t['where']}); {t['url']}.",
         f"Printed title: \"{t['quote']}\"", f"Condition columns: {t['column_label']}.", "", "## Notes", ""]
    L += [f"- {n}" for n in doc["notes"]]
    L += ["", "## Choices (spec parameters)", ""] + [f"- `{k}`: {v}" for k, v in sorted(doc["choices"].items())]
    L += ["", "## Governed by (pipeline/lab/model_map.json)", ""] + governance.md_lines(doc["governed_by"])
    for q in doc["quantities"]:
        L += ["", f"## {q['quantity']}: {q['label']}", "", "Values as held:", "",
              "| material | " + " | ".join(q["columns"]) + (f" | held: {t.get('held_label')} |" if "held" in q["values"][0] else " |"),
              "|---" * (len(q["columns"]) + 1 + ("held" in q["values"][0])) + "|"]
        for r in q["values"]:
            L.append(f"| {r['material']} | " + " | ".join(r["values"]) + (f" | {r['held']} |" if "held" in r else " |"))
        hd = "counts_held_differs" in q["column_pairs"][0]
        cr = "same_criterion" in q["column_pairs"][0]
        L += ["", f"| columns | pairs | concordant [{governance.short('M06a')}] | discordant | tied in first column only (T_x) | "
              f"tied in second column only (T_y) | tied in both | tau-b [{governance.short('M06b')}; digits {governance.short('M06c')}] | tau-b exact form |"
              + (f" same criterion [{governance.short('M06d')}] |" if cr else "")
              + (f" of these, pairs at different {t.get('held_label')} (conc / disc / T_x / T_y / both) [{governance.short('M06e')}] |" if hd else ""),
              "|---" * (9 + cr + hd) + "|"]
        for p in q["column_pairs"]:
            c, k = p["counts"], p["kendall_tau_b"]
            row = (f"| {p['column_1']} vs {p['column_2']} | {p['material_pairs']} | {c['concordant']} | {c['discordant']} | "
                   f"{c['tied_first_column_only']} | {c['tied_second_column_only']} | {c['tied_both_columns']} | {k['value']} | "
                   f"{k['numerator']} / sqrt({k['under_sqrt']}) |")
            if cr:
                row += f" {'yes' if p['same_criterion'] else 'no'} |"
            if hd:
                h = p["counts_held_differs"]
                row += (f" {h['concordant']} / {h['discordant']} / {h['tied_first_column_only']} / "
                        f"{h['tied_second_column_only']} / {h['tied_both_columns']} |")
            L.append(row)
        for p in q["column_pairs"]:
            if not p["discordant_and_tied_one_column_pairs"]:
                continue
            L += ["", f"{p['column_1']} vs {p['column_2']}:", "",
                  f"| class | a | b | a at {p['column_1']} | b at {p['column_1']} | a at {p['column_2']} | b at {p['column_2']} |"
                  + (" held a | held b |" if "held_a" in p["discordant_and_tied_one_column_pairs"][0] else ""),
                  "|---" * (7 + 2 * ("held_a" in p["discordant_and_tied_one_column_pairs"][0])) + "|"]
            for e in p["discordant_and_tied_one_column_pairs"]:
                L.append(f"| {e['class']} | {e['material_a']} | {e['material_b']} | {e['a_col1']} | {e['b_col1']} | "
                         f"{e['a_col2']} | {e['b_col2']} |" + (f" {e['held_a']} | {e['held_b']} |" if "held_a" in e else ""))
    return "\n".join(L) + "\n"


def main():
    S = spec()
    O = S["order_changes"]
    words = S["forbidden_words"]
    refs = load_json(ROOT / S["inputs"]["references"], exact=True)
    by_id = items_by_id(refs)
    digits = O["choices"]["tau_b_digits"]["value"]
    with_values = sorted(i for i, (_, it) in by_id.items() if "values" in it)
    tabled = [t["item"] for t in O["tables"]]
    rejected = {r["item"]: r["reason"] for r in O["search"]["rejected"]}
    for i in with_values:
        if i not in tabled and i not in rejected:
            fail(f"item {i} has 'values' and is neither a table nor rejected in the spec")
    for i in list(tabled) + list(rejected):
        if i not in with_values:
            fail(f"item {i} of the spec has no 'values' in references.json")
    out_dir = ROOT / S["output_dir"]
    summary = []
    for tab in O["tables"]:
        doc_ref, item = by_id[tab["item"]]
        qs = [analyse(tab, *m, digits) for m in matrix(tab, item)]
        notes = list(O["fixed_notes"]) + list(tab.get("notes", []))
        for ns in tab.get("item_note_sentences", []):
            for w in ns["words_in_item_note"]:
                if w not in item.get("note", ""):
                    fail(f"{tab['id']}: '{w}' is not verbatim in the item's note")
            notes.append(ns["sentence"])
        if any(p.get("same_criterion") is False for q in qs for p in q["column_pairs"]):
            notes.append(tab["criterion_differs_note"])
        helds = {r["held"] for q in qs for r in q["values"] if "held" in r}
        if len(helds) > 1:
            notes.append(tab["held_differs_note"])
        doc = {
            "_meta": {"generated_by": META, "script": "pipeline/lab/order_changes.py", "spec": "pipeline/spec/lab_numbers.json",
                      "numbers": "exact decimal strings, as printed in the item"},
            "table": {"id": tab["id"], "item": tab["item"], "document": doc_ref["id"], "url": doc_ref.get("url"),
                      "where": item.get("where"), "quote": item.get("quote"), "column_label": tab["column_label"],
                      **({"held_label": tab["held_label"]} if tab.get("held_label") else {})},
            "choices": {k: v["value"] for k, v in O["choices"].items()},
            "governed_by": governance.block(sorted(set(FIELD_POINTS.values()))),
            "notes": notes,
            "quantities": qs,
        }
        scan_words(doc, words, f"order {tab['id']}")
        md = render_md(doc)
        scan_words(md, words, f"order {tab['id']} md")
        write_json(out_dir / f"order_{tab['id']}.json", doc)
        write_text(out_dir / f"order_{tab['id']}.md", md)
        summary.append({"table": tab["id"], "json": f"order_{tab['id']}.json", "md": f"order_{tab['id']}.md",
                        "quantities": {q["quantity"]: [{"columns": [p["column_1"], p["column_2"]], **p["counts"],
                                                        **({"same_criterion": p["same_criterion"]} if "same_criterion" in p else {}),
                                                        **({"held_differs": p["counts_held_differs"]}
                                                           if "counts_held_differs" in p else {}),
                                                        "kendall_tau_b": p["kendall_tau_b"]["value"]}
                                                       for p in q["column_pairs"]] for q in qs}})
    search = {"rule": O["search"]["rule"], "items_with_values_looked_at": len(with_values),
              "tables": tabled, "rejected": [{"item": i, "reason": rejected[i]} for i in sorted(rejected)]}
    scan_words(search, words, "order search")
    return {"tables": summary, "search": search}


if __name__ == "__main__":
    main()
