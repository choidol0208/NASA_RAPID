#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude Code, catalog role) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14). No language model runs when this script runs.
"""Atmosphere flame temperature: one combustion number for an O2 / N2 / CO2 / He atmosphere.

The stoichiometric adiabatic flame temperature of an atmosphere, for a generic organic fuel:
- Heat: most organic fuels release about 13.1 kJ per gram of O2 consumed (oxygen-consumption principle,
  Huggett 1980, after Thornton 1917), so 1 mol of atmosphere with O2 mole fraction X releases
  Q = X * 31.998 g/mol * 13.1 kJ/g when its oxygen is used up.
- Products: the generic fuel unit is CH2 (alkanes and most polymers are close to it):
  CH2 + 1.5 O2 -> CO2 + H2O, so each mol of O2 consumed adds 2/3 mol CO2 and 2/3 mol H2O.
  The inert part (N2, CO2, He) is carried through.
- Temperature: the products are heated from 298.15 K until their enthalpy rise equals Q, with the
  enthalpies H(T) - H(298.15 K) of the NIST-JANAF tables, linear between table rows. No dissociation
  (so values above about 2200 K are upper bounds), no radiation, no fuel-specific chemistry.

The NIST-JANAF tables are NIST Standard Reference Database 13, copyrighted by the U.S. Secretary of
Commerce under the Standard Reference Data Act. They are NOT in this repository and must not be
committed (.gitignore). To rerun, download N-023, O-029, C-095, H-064 and He-001 (.txt) from
https://janaf.nist.gov/ into scoring/reference/janaf/ yourself. The team's plan is to switch to the NASA
Glenn coefficients (McBride, Zehe and Gordon 2002, NASA/TP-2002-211556), a NASA publication.

Flame temperature joins in one physical number what the scorer now treats as two dimensions, the O2
fraction and the diluent: a diluent with a higher heat capacity (CO2) lowers it, helium (lower molar
heat capacity) lowers it less. Run as a script, it tests this on the NASA FLEX measurements: does the
flame temperature alone explain the extinction diameter ratio as well as O2 and the diluent fractions
together?

Usage: python3 scoring/flame_temperature.py      (prints the check, writes scoring/flame_temperature.json)
Standard library only.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
JANAF_DIR = os.path.join(HERE, "reference", "janaf")
TABLES = {"N2": "N-023.txt", "O2": "O-029.txt", "CO2": "C-095.txt", "H2O": "H-064.txt", "He": "He-001.txt"}
OUT = os.path.join(HERE, "flame_temperature.json")
M_O2 = 31.998            # g/mol
HEAT_PER_G_O2 = 13.1     # kJ per g of O2 consumed (Huggett 1980)
CO2_PER_O2 = 2.0 / 3.0   # generic CH2 fuel
H2O_PER_O2 = 2.0 / 3.0
T0 = 298.15


def load_janaf():
    missing = [fn for fn in TABLES.values() if not os.path.exists(os.path.join(JANAF_DIR, fn))]
    if missing:
        raise SystemExit(f"NIST-JANAF tables not found in {JANAF_DIR} ({', '.join(missing)}); they are not redistributed, see the module docstring")
    out = {}
    for sp, fn in TABLES.items():
        rows = []
        for line in open(os.path.join(JANAF_DIR, fn), encoding="ascii"):
            parts = line.split("\t")
            try:
                t, dh = float(parts[0]), float(parts[4])
            except (ValueError, IndexError):
                continue
            rows.append((t, dh))
        out[sp] = sorted(rows)
    return out


def dh(table, t):
    for (t1, h1), (t2, h2) in zip(table, table[1:]):
        if t1 <= t <= t2:
            return h1 + (h2 - h1) * (t - t1) / (t2 - t1)
    raise ValueError(f"T = {t} K outside the table")


def flame_temperature(x_o2, x_co2=0.0, x_he=0.0, x_n2=None, janaf=None):
    """Stoichiometric adiabatic flame temperature (K) of 1 mol of atmosphere; N2 is the balance by default."""
    janaf = janaf or load_janaf()
    if x_n2 is None:
        x_n2 = max(0.0, 1.0 - x_o2 - x_co2 - x_he)
    tot = x_o2 + x_co2 + x_he + x_n2
    x_o2, x_co2, x_he, x_n2 = (v / tot for v in (x_o2, x_co2, x_he, x_n2))
    q = x_o2 * M_O2 * HEAT_PER_G_O2  # kJ per mol of atmosphere
    prod = {"N2": x_n2, "He": x_he, "CO2": x_co2 + CO2_PER_O2 * x_o2, "H2O": H2O_PER_O2 * x_o2}
    lo, hi = T0, 5900.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if sum(n * dh(janaf[sp], mid) for sp, n in prod.items() if n) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def check_on_flex():
    import derive_data_weights as dd
    janaf = load_janaf()
    rows, _ = dd.read_flex()
    for d in rows:
        d["t_ad"] = flame_temperature(d["x_o2"], d["x_co2"], d["x_he"], janaf=janaf)
    y = lambda d: d["dext_mm"] / d["d0_mm"] if d["end"] == "Extinction" and d["dext_mm"] is not None else None
    use = [d for d in rows if y(d) is not None]
    yy = [y(d) for d in use]

    def fit(feats):
        X = [[1.0] + sum((f(d) for f in feats), []) for d in use]
        r2, beta = dd._ols(X, yy)
        n, k = len(use), len(X[0])
        sse = (1 - r2) * sum((v - sum(yy) / n) ** 2 for v in yy)
        return dict(r2=round(r2, 4), aic=round(n * math.log(sse / n) + 2 * k, 2), k=k, beta=[round(b, 5) for b in beta])

    base = [lambda d: [1.0 if d["fuel"] == "Heptane" else 0.0], lambda d: [math.log(d["d0_mm"])], lambda d: [math.log(d["p_kpa"])]]
    two = fit([lambda d: [math.log(d["x_o2"])], lambda d: [d["x_co2"], d["x_he"]]] + base)
    one = fit([lambda d: [d["t_ad"] / 1000.0]] + base)
    o2_only = fit([lambda d: [math.log(d["x_o2"])]] + base)
    examples = {name: round(flame_temperature(*args, janaf=janaf)) for name, args in {
        "air (21% O2 in N2)": (0.21,), "ISS-like 21% O2, N2": (0.21,), "lunar habitat 30% O2 in N2": (0.30,),
        "34% O2 in N2 (exploration atmosphere)": (0.34,), "15% O2 in N2": (0.15,),
        "21% O2, 30% CO2, rest N2": (0.21, 0.30), "21% O2, 30% He, rest N2": (0.21, 0.0, 0.30)}.items()}
    ext = sorted(d["t_ad"] for d in use)
    return dict(
        _meta=dict(label="AI-generated data file: computed by code written with an AI assistant (Claude Code). No language model ran to build it. "
                         "The team's calculation, not a NASA result.",
                   method="Stoichiometric adiabatic flame temperature of the atmosphere for a generic CH2 fuel; 13.1 kJ per g O2 (Huggett 1980); "
                          "NIST-JANAF enthalpies; no dissociation. Check: OLS of the FLEX extinction diameter ratio on the flame temperature "
                          "against O2 and diluent fractions, each with fuel, ln d0 and ln P as controls.",
                   sources=["Huggett 1980, Fire and Materials 4(2), 61-65", "NIST-JANAF Thermochemical Tables (Chase 1998), janaf.nist.gov; NIST SRD 13, copyright U.S. Secretary of Commerce; read locally, not redistributed",
                            "NASA PSI-69 FLEX experimental table (CC0-1.0)"]),
        examples_K=examples,
        flex_check=dict(n=len(use), o2_and_diluent=two, flame_temperature_only=one, o2_only=o2_only,
                        flame_temperature_range_K=[round(ext[0]), round(ext[-1])]))


def main():
    out = check_on_flex()
    for k, v in out["examples_K"].items():
        print(f"{k:42s} {v} K")
    c = out["flex_check"]
    print(f"\nFLEX extinction diameter ratio, n = {c['n']}, flame temperatures {c['flame_temperature_range_K']} K")
    for name in ("o2_only", "o2_and_diluent", "flame_temperature_only"):
        print(f"  {name:24s} R2 {c[name]['r2']:.3f}  AIC {c[name]['aic']:8.2f}  parameters {c[name]['k']}")
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
