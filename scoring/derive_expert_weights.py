#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude Code, catalog role) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14). No language model runs when this script runs.
"""Expert stream for the weights: pairwise judgements by team members with combustion training.

The same 51 pairs as scoring/ahp_judgements.json (AHP, Saaty 1-9 scale), filled in by people instead
of an AI session. The form shows the NASA evidence for each question type, never the AI's answers, so
the people are not anchored on them.

1. Make the blank form:   python3 scoring/derive_expert_weights.py --form
   -> scoring/expert_form.csv. Each person copies it to scoring/expert_judgements/E<n>.csv (E1, E2, ...;
   no names in the repository) and fills two columns per row:
     more_important: A, B or equal
     how_much:       1 (equal), 3 (moderately), 5 (strongly), 7 (very strongly), 9 (extremely); 2, 4, 6, 8 between
2. Derive:                python3 scoring/derive_expert_weights.py
   - each person's matrices: principal eigenvector weights and consistency ratio (CR); a matrix with
     CR above 0.10 is reported so its author can revise it;
   - the group: the element-wise geometric mean of the individual judgements (aggregation of individual
     judgements, Aczel and Saaty 1983; Forman and Peniwati 1998), then its eigenvector and CR;
   -> scoring/expert_weights.json.
Standard library only.
"""
import argparse
import csv
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import derive_weights as dw  # noqa: E402

FORM = os.path.join(HERE, "expert_form.csv")
FILLED = os.path.join(HERE, "expert_judgements")
OUT = os.path.join(HERE, "expert_weights.json")
NAMES = {"o2": "oxygen mole fraction", "pressure": "total pressure", "flow": "flow around the fuel (type and speed)",
         "fuel": "fuel material", "geometry": "sample shape and thickness", "role": "purpose of the study (what it measured)",
         "diluent": "diluent or suppressant gas"}
PURPOSE = {"prevention": "material flammability and fire spread (prevention)",
           "detection": "smoke and fire detection",
           "suppression": "suppression and extinguishment"}
EVIDENCE = {"prevention": "scoring/WEIGHTING.md section 4.1 (BASS-II, Saffire records; textbook)",
            "detection": "scoring/WEIGHTING.md section 4.2 (SAME, SAME-R records)",
            "suppression": "scoring/WEIGHTING.md section 4.3 (BASS, FLEX records); FLEX data in scoring/data_weights.json"}
COLS = ["profile", "pair", "A", "B", "question", "evidence", "more_important", "how_much", "comment"]


def pairs():
    spec = json.load(open(dw.JUDGEMENTS, encoding="utf-8"))
    for prof, block in spec.items():
        if prof.startswith("_"):
            continue
        for i, (a, b, _v, _why) in enumerate(block["pairs"], start=1):
            yield prof, f"{prof[:3].upper()}{i:02d}", a, b


def write_form():
    with open(FORM, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(COLS)
        for prof, pid, a, b in pairs():
            q = (f"For a question about {PURPOSE[prof]}: how much more important is it that an experiment matches the user's "
                 f"{NAMES[a]} (A) than the user's {NAMES[b]} (B)?")
            w.writerow([prof, pid, a, b, q, EVIDENCE[prof], "", "", ""])
    return FORM


def read_filled(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    blocks, problems = {}, []
    for r in rows:
        mi, hm = (r.get("more_important") or "").strip().lower(), (r.get("how_much") or "").strip()
        if not mi and not hm:
            problems.append(f"{r['pair']}: empty")
            continue
        try:
            v = float(hm) if hm else 1.0
        except ValueError:
            problems.append(f"{r['pair']}: how_much '{hm}' is not a number")
            continue
        if mi == "equal" or v == 1:
            v = 1.0
        elif mi == "b":
            v = 1.0 / v
        elif mi != "a":
            problems.append(f"{r['pair']}: more_important '{mi}' is not A, B or equal")
            continue
        if not 1 / 9 <= v <= 9:
            problems.append(f"{r['pair']}: {hm} is outside 1-9")
            continue
        blocks.setdefault(r["profile"], []).append([r["A"], r["B"], v, r.get("comment", "")])
    return blocks, problems


def derive():
    spec = json.load(open(dw.JUDGEMENTS, encoding="utf-8"))
    files = sorted(glob.glob(os.path.join(FILLED, "E*.csv")))
    people, per_profile = {}, {}
    for f in files:
        pid = os.path.splitext(os.path.basename(f))[0]
        blocks, problems = read_filled(f)
        people[pid] = dict(problems=problems, profiles={})
        for prof, prs in blocks.items():
            block = dict(dimensions=spec[prof]["dimensions"], pairs=prs)
            try:
                dims, A = dw.matrix(block)
            except ValueError as e:
                people[pid]["problems"].append(f"{prof}: {e}")
                continue
            wts, lam = dw.eigen_weights(A)
            n = len(dims)
            cr = ((lam - n) / (n - 1)) / dw.RI[n]
            people[pid]["profiles"][prof] = dict(cr=round(cr, 4), consistent=cr <= dw.CR_LIMIT,
                                                 weights={d: round(x, 4) for d, x in zip(dims, wts)})
            per_profile.setdefault(prof, []).append((pid, dims, A))
    group = {}
    for prof, mats in per_profile.items():
        dims = mats[0][1]
        n = len(dims)
        G = [[math.prod(A[i][j] for _, _, A in mats) ** (1 / len(mats)) for j in range(n)] for i in range(n)]
        wts, lam = dw.eigen_weights(G)
        cr = ((lam - n) / (n - 1)) / dw.RI[n]
        exact = {d: 0.0 for d in dw.ALL_DIMS}
        exact.update(dict(zip(dims, wts)))
        group[prof] = dict(people=[p for p, _, _ in mats], cr=round(cr, 4), consistent=cr <= dw.CR_LIMIT,
                           weights=dw.round_to_one(exact))
    return dict(_meta=dict(
        what="Expert stream: AHP weights from pairwise judgements by team members with combustion training.",
        label="Judgements by people (anonymous ids); weights computed by code written with an AI assistant. No language model ran.",
        method="Per person: principal eigenvector and consistency ratio. Group: element-wise geometric mean of the individual "
               "judgements (aggregation of individual judgements), then its eigenvector and consistency ratio.",
        files=[os.path.basename(f) for f in files]), people=people, group=group)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--form", action="store_true", help="write the blank form scoring/expert_form.csv")
    args = ap.parse_args()
    if args.form:
        print("wrote", write_form())
        return 0
    out = derive()
    if not out["people"]:
        print(f"no filled forms in {FILLED} (E1.csv, E2.csv, ...); the expert stream is empty")
    for pid, p in out["people"].items():
        print(pid, {k: (v["cr"], "ok" if v["consistent"] else "CR above 0.10") for k, v in p["profiles"].items()}, p["problems"][:5])
    for prof, g in out["group"].items():
        print(f"group {prof}: {len(g['people'])} people, CR {g['cr']}, weights {g['weights']}")
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
