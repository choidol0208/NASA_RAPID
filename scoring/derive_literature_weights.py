#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude Code, catalog role) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14). No language model runs when this script runs.
"""Literature stream for the weights: the 51 AHP pairs filled in from textbooks, papers and NASA records.

scoring/literature_evidence.json gives, per question type, an evidence class for each dimension
(1 decisive, 2 strong modifier, 3 weak or not documented) with the findings and sources behind it.
This script turns the classes into pairwise judgements by a fixed rule on Saaty's verbal scale
(same class 1, one class apart 3, two classes apart 5), then derives the weights exactly as for the
other AHP streams (principal eigenvector, consistency ratio; scoring/derive_weights.py).

Outputs:
- scoring/literature_judgements.csv: the expert form (scoring/expert_form.csv) filled in, with the class,
  finding and sources of both dimensions beside each pair;
- scoring/literature_weights.json: weights and consistency ratio per question type.

Usage: python3 scoring/derive_literature_weights.py [--check]
Standard library only.
"""
import argparse
import csv
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import derive_expert_weights as de  # noqa: E402
import derive_weights as dw  # noqa: E402

EVIDENCE = os.path.join(HERE, "literature_evidence.json")
CSV_OUT = os.path.join(HERE, "literature_judgements.csv")
JSON_OUT = os.path.join(HERE, "literature_weights.json")
RULE = {0: 1, 1: 3, 2: 5}


def judgements(ev):
    rows = []
    form = list(csv.DictReader(open(de.FORM, encoding="utf-8")))
    for r in form:
        dims = ev[r["profile"]]["dimensions"]
        a, b = dims[r["A"]], dims[r["B"]]
        diff = b["class"] - a["class"]  # positive: A is in a stronger class
        v = RULE[abs(diff)]
        more = "equal" if diff == 0 else "A" if diff > 0 else "B"
        rows.append(dict(r, more_important=more, how_much=str(v),
                         comment=(f"A class {a['class']} ({', '.join(a['sources']) or 'no source'}); "
                                  f"B class {b['class']} ({', '.join(b['sources']) or 'no source'}). "
                                  f"A: {a['finding']} B: {b['finding']}")))
    return rows


def derive(ev):
    rows = judgements(ev)
    spec = json.load(open(dw.JUDGEMENTS, encoding="utf-8"))
    out = {}
    for prof in ("prevention", "detection", "suppression"):
        prs = []
        for r in rows:
            if r["profile"] != prof:
                continue
            v = float(r["how_much"])
            v = 1.0 if r["more_important"] == "equal" else v if r["more_important"] == "A" else 1.0 / v
            prs.append([r["A"], r["B"], v, ""])
        dims, A = dw.matrix(dict(dimensions=spec[prof]["dimensions"], pairs=prs))
        w, lam = dw.eigen_weights(A)
        n = len(dims)
        cr = ((lam - n) / (n - 1)) / dw.RI[n]
        exact = {d: 0.0 for d in dw.ALL_DIMS}
        exact.update(dict(zip(dims, w)))
        out[prof] = dict(classes={d: ev[prof]["dimensions"][d]["class"] for d in dims}, cr=round(cr, 4),
                         consistent=cr <= dw.CR_LIMIT, weights=dw.round_to_one(exact))
    return rows, out


def render(rows, out, ev):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=de.COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    meta = dict(ev["_about"])
    meta["outputs"] = "Weights by the AHP eigenvector method from the class-derived judgements; see scoring/BUILDUP.md B3."
    return buf.getvalue(), json.dumps(dict(_meta=meta, group=out), ensure_ascii=False, indent=2) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    ev = json.load(open(EVIDENCE, encoding="utf-8"))
    rows, out = derive(ev)
    csv_text, json_text = render(rows, out, ev)
    for prof, r in out.items():
        print(f"{prof}: CR {r['cr']}  classes {r['classes']}\n   weights " + ", ".join(f"{d} {v:.3f}" for d, v in r["weights"].items() if v))
    if args.check:
        same = all(os.path.exists(p) and open(p, encoding="utf-8").read() == t for p, t in ((CSV_OUT, csv_text), (JSON_OUT, json_text)))
        print("literature outputs are up to date" if same else "literature outputs differ from the evidence file")
        return 0 if same else 1
    for p, t in ((CSV_OUT, csv_text), (JSON_OUT, json_text)):
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(t)
    print("wrote", CSV_OUT, "and", JSON_OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
