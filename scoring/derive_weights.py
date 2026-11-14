#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Derive the profile weights from pairwise comparisons (analytic hierarchy process, AHP).

Reads scoring/ahp_judgements.json and, for each question type (profile):
- builds the reciprocal pairwise comparison matrix A (A[a][b] = v, A[b][a] = 1/v, A[i][i] = 1);
- takes the principal eigenvector of A as the weights (power iteration; Saaty's method);
- reports lambda_max, the consistency index CI = (lambda_max - n) / (n - 1) and the consistency
  ratio CR = CI / RI (Saaty's random index), and the row geometric-mean weights as a cross-check.
A matrix with CR above 0.10 is rejected (Saaty's usual limit).

Usage:
    python3 scoring/derive_weights.py           # print the derivation
    python3 scoring/derive_weights.py --check   # exit 1 if scoring_config.json differs from it
    python3 scoring/derive_weights.py --write   # write the derived weights into scoring_config.json
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JUDGEMENTS = os.path.join(HERE, "ahp_judgements.json")
CONFIG = os.path.join(HERE, "scoring_config.json")
ALL_DIMS = ["o2", "pressure", "flow", "fuel", "geometry", "role", "diluent"]  # order in scoring_config.json
RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}  # Saaty's random index
CR_LIMIT = 0.10
DECIMALS = 3


def _value(v):
    if isinstance(v, str) and "/" in v:
        a, b = v.split("/")
        return float(a) / float(b)
    return float(v)


def matrix(block):
    dims = block["dimensions"]
    n = len(dims)
    idx = {d: i for i, d in enumerate(dims)}
    A = [[1.0 if i == j else None for j in range(n)] for i in range(n)]
    for a, b, v, _why in block["pairs"]:
        i, j = idx[a], idx[b]
        if A[i][j] is not None:
            raise ValueError(f"pair {a}-{b} given twice")
        x = _value(v)
        if not 1 / 9 <= x <= 9:
            raise ValueError(f"pair {a}-{b}: {v} is outside the 1-9 scale")
        A[i][j], A[j][i] = x, 1.0 / x
    missing = [(dims[i], dims[j]) for i in range(n) for j in range(n) if A[i][j] is None]
    if missing:
        raise ValueError(f"pairs missing: {missing}")
    return dims, A


def eigen_weights(A, tol=1e-13, max_iter=10000):
    n = len(A)
    w = [1.0 / n] * n
    for _ in range(max_iter):
        v = [sum(A[i][j] * w[j] for j in range(n)) for i in range(n)]
        s = sum(v)
        v = [x / s for x in v]
        if max(abs(x - y) for x, y in zip(v, w)) < tol:
            w = v
            break
        w = v
    Aw = [sum(A[i][j] * w[j] for j in range(n)) for i in range(n)]
    lam = sum(Aw[i] / w[i] for i in range(n)) / n
    return w, lam


def geometric_mean_weights(A):
    g = [math.prod(row) ** (1 / len(row)) for row in A]
    s = sum(g)
    return [x / s for x in g]


def round_to_one(w, decimals=DECIMALS):
    """Round to `decimals` and give the rounding remainder to the largest weight, so the sum is 1."""
    r = {d: round(x, decimals) for d, x in w.items()}
    top = max(r, key=lambda d: (r[d], -ALL_DIMS.index(d)))
    r[top] = round(r[top] + 1.0 - sum(r.values()), decimals)
    return r


def derive(path=JUDGEMENTS):
    spec = json.load(open(path, encoding="utf-8"))
    out = {}
    for prof, block in spec.items():
        if prof.startswith("_"):
            continue
        dims, A = matrix(block)
        n = len(dims)
        w, lam = eigen_weights(A)
        ci = (lam - n) / (n - 1)
        cr = ci / RI[n] if RI[n] else 0.0
        if cr > CR_LIMIT:
            raise ValueError(f"{prof}: consistency ratio {cr:.3f} is above {CR_LIMIT}; revise the judgements")
        exact = {d: 0.0 for d in ALL_DIMS}
        exact.update(dict(zip(dims, w)))
        gm = dict(zip(dims, geometric_mean_weights(A)))
        out[prof] = dict(dims=dims, matrix=A, exact=exact, weights=round_to_one(exact), geometric_mean=gm,
                         lambda_max=lam, ci=ci, cr=cr, n=n)
    return out


def report_lines(res):
    lines = ["| Profile | n | lambda_max | CI | CR | " + " | ".join(ALL_DIMS) + " |",
             "|---|---|---|---|---|" + "---|" * len(ALL_DIMS)]
    for prof, r in res.items():
        lines.append(f"| {prof} | {r['n']} | {r['lambda_max']:.3f} | {r['ci']:.3f} | {r['cr']:.3f} | "
                     + " | ".join(f"{r['weights'][d]:.3f}" for d in ALL_DIMS) + " |")
    return lines


STREAMS = os.path.join(HERE, "weight_streams.json")
EXPERT = os.path.join(HERE, "expert_weights.json")
DATA = os.path.join(HERE, "data_weights.json")


def final_weights(res, streams_path=STREAMS):
    """Combine the streams named in scoring/weight_streams.json into the weights the scorer uses.

    - Judgement stream: the group weights of the team's experts (scoring/expert_weights.json) for a profile
      whose group matrix is consistent, if "judgement.prefer" is "expert"; otherwise the AHP derivation above
      (the AI session's judgements).
    - Data stream: for a profile listed under "data", the weights of the listed dimensions are pooled with
      the data shares of scoring/data_weights.json by a log-linear (geometric) opinion pool,
      s_d proportional to s_judgement_d^(1 - lambda) * s_data_d^lambda, inside the subset; the subset keeps the
      total weight the judgement gave it, and the other dimensions keep theirs.
    Nothing is combined unless "apply" is true.
    """
    st = json.load(open(streams_path, encoding="utf-8")) if os.path.exists(streams_path) else {}
    expert = json.load(open(EXPERT, encoding="utf-8")).get("group", {}) if os.path.exists(EXPERT) else {}
    data = json.load(open(DATA, encoding="utf-8")).get("responses", {}) if os.path.exists(DATA) else {}
    out = {}
    for prof, r in res.items():
        w, sources = dict(r["weights"]), ["AHP, AI-session judgements (scoring/ahp_judgements.json)"]
        if st.get("apply"):
            g = expert.get(prof)
            if st.get("judgement", {}).get("prefer") == "expert" and g and g.get("consistent"):
                w, sources = dict(g["weights"]), [f"AHP, judgements of {len(g['people'])} team members (scoring/expert_weights.json)"]
            spec = st.get("data", {}).get(prof)
            if spec and spec["response"] in data:
                dims = [d for d in spec["dimensions"] if w.get(d, 0) > 0]
                imp = data[spec["response"]]["importance"]
                m = sum(w[d] for d in dims)
                sd_tot = sum(imp[d]["normalised"] for d in dims)
                lam = spec["lambda"]
                pooled = {d: (w[d] / m) ** (1 - lam) * (imp[d]["normalised"] / sd_tot) ** lam for d in dims}
                z = sum(pooled.values())
                exact = {d: w.get(d, 0.0) for d in ALL_DIMS}
                exact.update({d: m * pooled[d] / z for d in dims})
                w = round_to_one(exact)
                sources.append(f"pooled with NASA FLEX data ({spec['response']}, lambda {lam}) over {', '.join(dims)}")
        out[prof] = dict(weights={d: w.get(d, 0.0) for d in ALL_DIMS}, sources=sources)
    return out


def config_differences(res, cfg):
    diffs = []
    for prof, r in final_weights(res).items():
        have = cfg["profiles"][prof]["weights"]
        for d in ALL_DIMS:
            if abs(have.get(d, 0.0) - r["weights"][d]) > 1e-9:
                diffs.append(f"{prof}.{d}: config {have.get(d, 0.0)}, derived {r['weights'][d]}")
    return diffs


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    args = ap.parse_args()
    res = derive()
    print("\n".join(report_lines(res)))
    for prof, r in res.items():
        print(f"\n{prof}: eigenvector " + ", ".join(f"{d} {r['exact'][d]:.4f}" for d in r["dims"])
              + "; geometric mean " + ", ".join(f"{d} {r['geometric_mean'][d]:.4f}" for d in r["dims"]))
    fin = final_weights(res)
    for prof, r in fin.items():
        print(f"\nfinal {prof}: " + ", ".join(f"{d} {r['weights'][d]:.3f}" for d in ALL_DIMS) + " | " + "; ".join(r["sources"]))
    text = open(CONFIG, encoding="utf-8").read()
    cfg = json.loads(text)
    diffs = config_differences(res, cfg)
    if args.check:
        print("\nconfig matches the derivation" if not diffs else "\nconfig differs:\n  " + "\n  ".join(diffs))
        return 1 if diffs else 0
    if args.write:
        for prof, r in final_weights(res).items():
            cfg["profiles"][prof]["weights"] = {d: r["weights"][d] for d in ALL_DIMS}
        end = "\n" if text.endswith("\n") else ""
        with open(CONFIG, "w", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(cfg, ensure_ascii=False, indent=2) + end)
        print(f"\nwrote {len(diffs)} changed weights to {CONFIG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
