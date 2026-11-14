#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude Code, catalog role) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14). No language model runs when this script runs.
"""Data stream for the weights: how much each condition explains of a measured combustion response.

Source: the FLEX experimental table (PSI-69, CC0-1.0), data/psi/experimental_tables/, read directly
(not the data role's pipeline). 274 droplet tests on the ISS with methanol or heptane in O2/N2/CO2/He
atmospheres at 0.5 to 3 atm.

For two responses:
- ln K: the table's "Burning rate" column, read as the burning-rate constant K of the d^2 law, a measure
  of how intensely the fuel burns. The header writes the unit as "mm"; K is conventionally in mm^2/s,
  but the unit is not confirmed by the table or the record. Logs, shares and elasticities do not
  depend on the unit;
- d_ext/d0: the droplet diameter at flame extinction over the initial diameter, for tests that ended
  in extinction; a larger value means the flame went out earlier, i.e. the atmosphere suppressed it more.

Predictors, in groups that match the scorer's dimensions:
  o2 = ln X_O2;  pressure = ln P;  diluent = (X_CO2, X_He), N2 the baseline;  fuel = heptane (1) or
  methanol (0);  size = ln d0 (initial droplet diameter; no scorer dimension, kept as a control).

Method:
1. Ordinary least squares on the log-linear (power-law) model, the usual form of combustion scaling laws.
2. Relative importance by the LMG decomposition of R^2 (Lindeman, Merenda and Gold 1980; Groemping
   2006, 2007): each group's share is its sequential R^2 gain averaged over all orders of entry, which
   is the Shapley value of the R^2 "game" and stays meaningful when predictors are correlated.
3. Uncertainty by the nonparametric bootstrap (Efron and Tibshirani 1993): rows are resampled with
   replacement, percentile 95% intervals.
4. A theory check of the fitted coefficients against the d^2 law (written in the output).

Usage:
    python3 scoring/derive_data_weights.py          # print and write scoring/data_weights.json
    python3 scoring/derive_data_weights.py --check  # exit 1 if data_weights.json is not what the data give
Standard library only.
"""
import argparse
import csv
import hashlib
import io
import itertools
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FLEX = os.path.join(ROOT, "data", "psi", "experimental_tables", "PSI-69_Experimental table_FLEX.csv")
OUT = os.path.join(HERE, "data_weights.json")
MMHG_TO_KPA = 0.133322
BOOT = 1000
SEED = 20261114

GROUPS = {
    "o2": ("ln X_O2", lambda d: [math.log(d["x_o2"])]),
    "pressure": ("ln P", lambda d: [math.log(d["p_kpa"])]),
    "diluent": ("X_CO2, X_He", lambda d: [d["x_co2"], d["x_he"]]),
    "fuel": ("heptane", lambda d: [1.0 if d["fuel"] == "Heptane" else 0.0]),
    "size": ("ln d0", lambda d: [math.log(d["d0_mm"])]),
}
COEF_NAMES = ["intercept", "ln X_O2", "ln P", "X_CO2", "X_He", "heptane", "ln d0"]
RESPONSES = {
    "ln_K": dict(label="ln K, the table's Burning rate column read as the d^2-law constant (unit written as mm; not confirmed)",
                 y=lambda d: math.log(d["k"]) if d["k"] and d["k"] > 0 else None),
    "dext_over_d0": dict(label="d_ext/d0 at flame extinction (tests that ended in extinction)",
                         y=lambda d: d["dext_mm"] / d["d0_mm"] if d["end"] == "Extinction" and d["dext_mm"] is not None else None),
}
# The scorer's suppression profile uses the extinction response; ln K is reported as a check.
USE = {"suppression": "dext_over_d0"}


def _num(x):
    try:
        return float(str(x).strip())
    except ValueError:
        return None


def read_flex(path=FLEX):
    raw = open(path, "rb").read()
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    rows = [r for r in csv.reader(io.StringIO(text)) if any(c.strip() for c in r)]
    out, dropped = [], []
    for i, r in enumerate(rows[1:], start=2):  # CSV row number, header = 1
        p, xo, xco2, xhe, d0 = _num(r[5]), _num(r[6]), _num(r[8]), _num(r[9]), _num(r[10])
        if not p or p <= 0 or not xo or not d0:
            dropped.append(i)  # a pressure cell of 0 (row 115) and cells that are not numbers
            continue
        out.append(dict(row=i, fuel=r[4].strip(), p_kpa=p * MMHG_TO_KPA, x_o2=xo, x_co2=xco2 or 0.0, x_he=xhe or 0.0,
                        d0_mm=d0, dext_mm=_num(r[11]), k=_num(r[12]), end=r[14].strip()))
    return out, dropped


def _ols(X, y):
    p = len(X[0])
    A = [[sum(row[i] * row[j] for row in X) for j in range(p)] + [sum(row[i] * yy for row, yy in zip(X, y))] for i in range(p)]
    for c in range(p):
        piv = max(range(c, p), key=lambda r: abs(A[r][c]))
        A[c], A[piv] = A[piv], A[c]
        if abs(A[c][c]) < 1e-12:
            return None, None
        for r in range(p):
            if r != c:
                f = A[r][c] / A[c][c]
                A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    beta = [A[i][p] / A[i][i] for i in range(p)]
    my = sum(y) / len(y)
    sst = sum((v - my) ** 2 for v in y)
    sse = sum((v - sum(b * x for b, x in zip(beta, row))) ** 2 for row, v in zip(X, y))
    return 1.0 - sse / sst, beta


def lmg(rows, yfun):
    rows = [d for d in rows if yfun(d) is not None]
    y = [yfun(d) for d in rows]
    names = list(GROUPS)
    feats = {g: [GROUPS[g][1](d) for d in rows] for g in names}
    r2 = {(): 0.0}
    for k in range(1, len(names) + 1):
        for S in itertools.combinations(names, k):
            X = [[1.0] + sum((feats[g][i] for g in S), []) for i in range(len(rows))]
            r2[S] = _ols(X, y)[0]
    n = len(names)
    share = {}
    for g in names:
        others = [h for h in names if h != g]
        tot = 0.0
        for k in range(n):
            for S in itertools.combinations(others, k):
                w = math.factorial(k) * math.factorial(n - k - 1) / math.factorial(n)
                with_g = tuple(h for h in names if h in S or h == g)
                tot += w * (r2[with_g] - r2[tuple(h for h in names if h in S)])
        share[g] = tot
    X = [[1.0] + sum((feats[g][i] for g in names), []) for i in range(len(rows))]
    full_r2, beta = _ols(X, y)
    return dict(n=len(rows), r2=full_r2, share=share, beta=beta)


def _ci(v):
    v = sorted(v)
    return [v[int(0.025 * len(v))], v[min(len(v) - 1, int(0.975 * len(v)))]]


def analyse(rows, boot=BOOT, seed=SEED):
    rnd = random.Random(seed)
    res = {}
    for key, spec in RESPONSES.items():
        base = lmg(rows, spec["y"])
        tot = sum(base["share"].values())
        bs_share = {g: [] for g in GROUPS}
        bs_beta = [[] for _ in COEF_NAMES]
        for _ in range(boot):
            sample = [rnd.choice(rows) for _ in rows]
            b = lmg(sample, spec["y"])
            t = sum(b["share"].values())
            for g in GROUPS:
                bs_share[g].append(b["share"][g] / t)
            for i, x in enumerate(b["beta"]):
                bs_beta[i].append(x)
        res[key] = dict(
            label=spec["label"], n=base["n"], r2=round(base["r2"], 4),
            coefficients={c: dict(value=round(x, 4), ci95=[round(v, 4) for v in _ci(bs_beta[i])]) for i, (c, x) in enumerate(zip(COEF_NAMES, base["beta"]))},
            importance={g: dict(r2_share=round(base["share"][g], 4), normalised=round(base["share"][g] / tot, 4),
                                ci95=[round(v, 4) for v in _ci(bs_share[g])]) for g in GROUPS})
    return res


THEORY = [
    "d^2 law: K = (8 k_g / (rho_l c_pg)) ln(1 + B) (Turns 2012, ch. 10). With B roughly proportional to the ambient O2 mass fraction, "
    "the elasticity d ln K / d ln Y_O2 = B / ((1 + B) ln(1 + B)) lies between 0 and 1; the fitted ln X_O2 coefficient of ln K should lie there too.",
    "The d^2-law K does not depend on pressure to first order (k_g and c_pg do not); the fitted ln P coefficient of ln K should be small.",
    "Helium raises the thermal conductivity of the gas, so K should rise with X_He; CO2 has a higher heat capacity and lowers the O2 mass "
    "fraction at the same mole fraction, so K should fall with X_CO2.",
    "A lower O2 fraction brings the flame nearer its extinction limit, so the extinction diameter ratio d_ext/d0 should fall as X_O2 rises "
    "(negative ln X_O2 coefficient) and rise with an inert that suppresses (positive X_CO2 coefficient).",
]


def theory_check(res):
    c = res["ln_K"]["coefficients"]
    e = res["dext_over_d0"]["coefficients"]
    return [
        dict(statement=THEORY[0], fitted=c["ln X_O2"], holds=0 < c["ln X_O2"]["ci95"][0] and c["ln X_O2"]["ci95"][1] < 1),
        dict(statement=THEORY[1], fitted=c["ln P"], holds=abs(c["ln P"]["value"]) < 0.25),
        dict(statement=THEORY[2], fitted=dict(X_He=c["X_He"], X_CO2=c["X_CO2"]), holds=c["X_He"]["ci95"][0] > 0 and c["X_CO2"]["ci95"][1] < 0),
        dict(statement=THEORY[3], fitted=dict(ln_X_O2=e["ln X_O2"], X_CO2=e["X_CO2"]), holds=e["ln X_O2"]["ci95"][1] < 0 and e["X_CO2"]["ci95"][0] > 0),
    ]


def build():
    rows, dropped = read_flex()
    res = analyse(rows)
    sha = hashlib.sha256(open(FLEX, "rb").read()).hexdigest()
    return {
        "_meta": {
            "what": "Data stream for the scoring weights: share of the explained variance of measured FLEX responses that each condition accounts for.",
            "label": "AI-generated data file: computed by code written with an AI assistant (Claude Code). No language model ran to build it. "
                     "The team's analysis of NASA data, not a NASA result.",
            "source": "NASA PSI-69 FLEX experimental table (CC0-1.0), https://psi.nasa.gov/ ; read directly, not through the data pipeline",
            "input_sha256": sha, "rows_used": len(rows), "rows_dropped": dropped, "bootstrap": BOOT, "seed": SEED,
            "method": "OLS on a log-linear model; LMG (Shapley) decomposition of R^2 over predictor groups; nonparametric bootstrap, "
                      "percentile 95% intervals. See scoring/WEIGHTING.md section 'Data stream'.",
            "use": USE,
        },
        "responses": res,
        "theory_check": theory_check(res),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    out = build()
    for key, r in out["responses"].items():
        print(f"{r['label']}: n = {r['n']}, R2 = {r['r2']}")
        for g, v in r["importance"].items():
            print(f"   {g:9s} share {v['normalised']:.3f}  95% CI [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}]")
        print("   coefficients: " + ", ".join(f"{c} {v['value']} [{v['ci95'][0]}, {v['ci95'][1]}]" for c, v in r["coefficients"].items()))
    for t in out["theory_check"]:
        print(("HOLDS  " if t["holds"] else "FAILS  ") + t["statement"][:110])
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        same = os.path.exists(OUT) and open(OUT, encoding="utf-8").read() == text
        print("data_weights.json is up to date" if same else "data_weights.json differs from the data")
        return 0 if same else 1
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
