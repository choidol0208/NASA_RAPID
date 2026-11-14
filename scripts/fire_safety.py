#!/usr/bin/env python3
# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Steps 2-4 of the data pipeline: fire-safety values, condition matching
and evidence bundles, all computed by fixed rules from the test tables.

No language model takes part in any number or judgement here. The outputs
are meant to be shown as-is or handed to a language model that may only
rephrase them.

Step 2  metrics()   descriptive fire-safety values per investigation
Step 3  match()     how close a habitat atmosphere is to what was tested
Step 4  evidence()  one JSON bundle per habitat preset: values, units,
                    source rows, warnings

These are the team's calculations from NASA PSI data, not NASA conclusions,
and they describe what was tested, not what is safe.

Usage:  python3 scripts/fire_safety.py            # writes data/derived/*.json
"""
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "derived")

# Habitat presets. The lunar values are the bounds given in the challenge
# statement ("30% or greater", "10.2 psi or less"); 10.2 psi = 70.3 kPa.
PRESETS = {
    "iss_cabin": {"label": "ISS cabin air", "o2_pct": 21.0, "pressure_kpa": 101.3,
                  "flow_cms": None, "gravity": "microgravity"},
    "lunar_base": {"label": "Moon Base atmosphere (challenge statement bounds)",
                   "o2_pct": 30.0, "pressure_kpa": 70.3, "flow_cms": None,
                   "gravity": "lunar"},
}
# One "step" on each axis for the distance used to rank nearest tests.
SCALE = {"o2_pct": 5.0, "pressure_kpa": 20.0, "flow_cms": 10.0}
BURN_O2_DROP = 0.1     # percentage points of O2 consumed that count as "burned"
BURN_CO2_RISE = 0.05   # percentage points of CO2 produced that count as "burned"


def load():
    read = lambda name: pd.read_csv(os.path.join(OUT, name))
    return read("tests_conditions.csv"), read("tests_flex.csv"), read("tests_bass2.csv")


def stats(series):
    s = series.dropna()
    if s.empty:
        return {"n": 0}
    return {"n": int(s.size), "min": round(float(s.min()), 4),
            "median": round(float(s.median()), 4), "max": round(float(s.max()), 4)}


def rows_of(df, limit=8):
    return [{"test_id": t, "source_file": f, "source_row": int(r)}
            for t, f, r in zip(df.test_id[:limit], df.source_file[:limit], df.source_row[:limit])]


# ------------------------------------------------------------------ step 2
def bass2_metrics(b):
    burned = (b.o2_consumed_pct_points >= BURN_O2_DROP) | (b.co2_produced_pct_points >= BURN_CO2_RISE)
    out = {"definition": {
        "burned": f"O2 drop >= {BURN_O2_DROP} points or CO2 rise >= {BURN_CO2_RISE} points over the test",
        "co_to_co2_molar_ratio": "CO rise (ppm x 1e-4) / CO2 rise (% points); a measure of incomplete combustion",
        "lowest_o2_with_burning_pct": "lowest initial ambient O2 among tests classed as burned"},
        "by_material_geometry": []}
    for (material, geometry), g in b.groupby(["fuel_material", "sample_geometry"]):
        gb = g[burned.loc[g.index]]
        lowest = gb.sort_values("o2_pct").head(1)
        out["by_material_geometry"].append({
            "fuel_material": material, "sample_geometry": geometry, "tests": int(len(g)),
            "tests_classed_as_burned": int(len(gb)),
            "o2_tested_pct": stats(g.o2_pct),
            "flow_tested_cms": {"min": None if g.flow_min_cms.dropna().empty else float(g.flow_min_cms.min()),
                                "max": None if g.flow_max_cms.dropna().empty else float(g.flow_max_cms.max())},
            "lowest_o2_with_burning_pct": None if lowest.empty else float(lowest.o2_pct.iloc[0]),
            "lowest_o2_with_burning_source": rows_of(lowest),
            "co_to_co2_molar_ratio": stats(g.co_to_co2_molar_ratio),
            "extinction_noted_while_lowering_flow": int((g.flow_event_noted == "extinction").sum()),
            "blowoff_noted": int((g.flow_event_noted == "blowoff").sum()),
        })
    ratio = b.co_to_co2_molar_ratio.dropna()
    out["all_tests"] = {
        "co_to_co2_molar_ratio": stats(ratio),
        "share_within_published_range_0.01_to_0.1": round(float(((ratio >= 0.01) & (ratio <= 0.1)).mean()), 3),
        "published_range_source": "Olson et al., Results from on-board CSA-CP and CDM Sensor Readings during BASS-II (listed under PSI-25 publications)"}
    return out


def flex_metrics(f):
    burned = f[f.burn_time_s >= 1.0]
    out = {"definition": {
        "lowest_o2_with_burning_pct": "lowest initial O2 among tests with a burn time of at least 1 s",
        "extinction_to_initial_diameter_ratio": "droplet diameter at visible-flame extinction / initial diameter; "
                                                "a larger ratio means the flame went out earlier in the burn",
        "o2_vs_extinction_ratio_spearman": "rank correlation between O2 and that ratio; negative means "
                                           "flames went out earlier at lower O2"},
        "by_fuel_diluent": []}
    for (fuel, diluent), g in f.groupby(["fuel_material", "diluent"]):
        gb = burned[(burned.fuel_material == fuel) & (burned.diluent == diluent)]
        lowest = gb.sort_values("o2_pct").head(1)
        pair = g[["o2_pct", "extinction_to_initial_diameter_ratio"]].dropna()
        # Spearman = Pearson correlation of the ranks (no extra dependency).
        rho = pair.o2_pct.rank().corr(pair.extinction_to_initial_diameter_ratio.rank()) if len(pair) >= 8 else None
        dil_col = {"CO2": "co2_pct", "He": "he_pct"}.get(diluent)
        out["by_fuel_diluent"].append({
            "fuel_material": fuel, "diluent": diluent, "tests": int(len(g)),
            "o2_tested_pct": stats(g.o2_pct), "pressure_tested_kpa": stats(g.pressure_kpa),
            "diluent_tested_pct": stats(g[dil_col]) if dil_col else None,
            "outcomes": {k: int(v) for k, v in g.outcome.value_counts().items()},
            "lowest_o2_with_burning_pct": None if lowest.empty else float(lowest.o2_pct.iloc[0]),
            "lowest_o2_with_burning_source": rows_of(lowest),
            "burning_rate_mm2_s": stats(g.burning_rate_mm2_s),
            "extinction_to_initial_diameter_ratio": stats(g.extinction_to_initial_diameter_ratio),
            "o2_vs_extinction_ratio_spearman": None if rho is None or pd.isna(rho) else {"rho": round(float(rho), 3), "n": int(len(pair))},
        })
    # Same-atmosphere comparison of diluents: near 1 atm, 18-21 % O2.
    band = f[f.o2_pct.between(18, 21) & f.pressure_kpa.between(95, 106)]
    out["diluent_comparison_18_to_21_pct_o2_near_1_atm"] = [
        {"fuel_material": fuel, "diluent": diluent, "tests": int(len(g)),
         "extinction_to_initial_diameter_ratio": stats(g.extinction_to_initial_diameter_ratio),
         "burning_rate_mm2_s": stats(g.burning_rate_mm2_s)}
        for (fuel, diluent), g in band.groupby(["fuel_material", "diluent"])]
    return out


def metrics(conditions, flex, bass2):
    ambient = conditions[conditions.o2_basis == "ambient"]
    coverage = []
    for inv, g in conditions.groupby("investigation_id"):
        a = ambient[ambient.investigation_id == inv]
        coverage.append({"investigation_id": inv, "tests": int(len(g)),
                         "fuel_phase": sorted(g.fuel_phase.dropna().unique().tolist()),
                         "ambient_o2_pct": stats(a.o2_pct), "pressure_kpa": stats(g.pressure_kpa),
                         "flow_cms": stats(g.flow_cms)})
    return {"note": "Team calculations from NASA PSI experimental tables. Descriptive only; "
                    "all tests are microgravity tests.",
            "tested_ranges": coverage, "PSI-25_BASS-II": bass2_metrics(bass2),
            "PSI-69_FLEX": flex_metrics(flex)}


# ------------------------------------------------------------------ step 3
def match(env, conditions, nearest=5):
    """Compare a habitat atmosphere with the tested conditions.

    Oxygen is compared only with 'ambient' values: in inverse flames the
    listed oxygen is the burner stream, not the surrounding atmosphere."""
    axes = [a for a in SCALE if env.get(a) is not None]
    results = []
    for inv, g in conditions.groupby("investigation_id"):
        g = g.copy()
        g.loc[g.o2_basis != "ambient", "o2_pct"] = float("nan")
        axis_report, used = {}, []
        for a in axes:
            col = g[a].dropna()
            if col.empty:
                axis_report[a] = {"status": "not_in_table"}
                continue
            lo, hi = float(col.min()), float(col.max())
            inside = lo <= env[a] <= hi
            axis_report[a] = {"status": "inside_tested_range" if inside else "outside_tested_range",
                              "tested_min": round(lo, 3), "tested_max": round(hi, 3),
                              "gap": 0.0 if inside else round(min(abs(env[a] - lo), abs(env[a] - hi)), 3)}
            used.append(a)
        if not used:
            continue
        dist = sum(((g[a] - env[a]).abs() / SCALE[a]) for a in used)
        g = g.assign(distance=dist).dropna(subset=["distance"]).sort_values("distance").head(nearest)
        results.append({
            "investigation_id": inv, "axes": axis_report,
            "axes_inside_tested_range": sum(v["status"] == "inside_tested_range" for v in axis_report.values()),
            "axes_compared": len(used),
            "nearest_tests": [{"test_id": t.test_id, "fuel_material": t.fuel_material,
                               "o2_pct": None if pd.isna(t.o2_pct) else float(t.o2_pct),
                               "pressure_kpa": None if pd.isna(t.pressure_kpa) else float(t.pressure_kpa),
                               "flow_cms": None if pd.isna(t.flow_cms) else float(t.flow_cms),
                               "distance": round(float(t.distance), 3),
                               "source_file": t.source_file, "source_row": int(t.source_row)}
                              for t in g.itertuples()]})
    results.sort(key=lambda r: (-r["axes_inside_tested_range"],
                                r["nearest_tests"][0]["distance"] if r["nearest_tests"] else 9e9))
    return results


def warnings_for(env, conditions):
    w = []
    if env.get("gravity") != "microgravity":
        w.append({"code": "no_partial_gravity_data",
                  "text": "Every test in these PSI tables was run in microgravity. PSI holds no "
                          "partial-gravity combustion data, so nothing here measures Moon or Mars gravity."})
    amb = conditions[conditions.o2_basis == "ambient"]
    solid = amb[amb.fuel_phase == "solid"].o2_pct.dropna()
    if env.get("o2_pct") is not None:
        if env["o2_pct"] > amb.o2_pct.max():
            w.append({"code": "o2_above_all_ambient_tests",
                      "text": f"Requested O2 {env['o2_pct']}% is above every ambient value tested "
                              f"({amb.o2_pct.max():.1f}% maximum)."})
        if not solid.empty and env["o2_pct"] > solid.max():
            w.append({"code": "o2_above_solid_fuel_tests",
                      "text": f"Solid-fuel tables (BASS-II, Saffire) go up to {solid.max():.1f}% O2. At "
                              f"{env['o2_pct']}% O2 only liquid-droplet and gas-flame tests exist; they do "
                              "not measure solid material flammability."})
    if env.get("flow_cms") is None:
        w.append({"code": "flow_not_specified",
                  "text": "No ventilation flow speed was given, so flow was not compared."})
    return w


# ------------------------------------------------------------------ step 4
def evidence(key, env, conditions, all_metrics):
    return {"preset": key, "environment": env,
            "generated_by": "scripts/fire_safety.py (rule-based; no language model)",
            "data_source": "NASA PSI experimental tables, https://psi.nasa.gov/",
            "warnings": warnings_for(env, conditions),
            "investigations_by_closeness": match(env, conditions),
            "metrics_reference": "fire_safety_metrics.json",
            "tested_ranges": all_metrics["tested_ranges"]}


def main():
    conditions, flex, bass2 = load()
    m = metrics(conditions, flex, bass2)
    with open(os.path.join(OUT, "fire_safety_metrics.json"), "w") as fh:
        json.dump(m, fh, indent=1)
    for key, env in PRESETS.items():
        with open(os.path.join(OUT, f"evidence_{key}.json"), "w") as fh:
            json.dump(evidence(key, env, conditions, m), fh, indent=1)

    print("BASS-II by material and geometry")
    for r in m["PSI-25_BASS-II"]["by_material_geometry"]:
        print(f"  {r['sample_geometry']:18} {r['fuel_material'][:22]:22} n={r['tests']:3} burned={r['tests_classed_as_burned']:3} "
              f"O2 {r['o2_tested_pct'].get('min')}-{r['o2_tested_pct'].get('max')}%  lowest O2 with burning {r['lowest_o2_with_burning_pct']}  "
              f"CO/CO2 median {r['co_to_co2_molar_ratio'].get('median')}")
    print("FLEX by fuel and diluent")
    for r in m["PSI-69_FLEX"]["by_fuel_diluent"]:
        print(f"  {r['fuel_material']:9} {r['diluent']:4} n={r['tests']:3} O2 {r['o2_tested_pct']['min']}-{r['o2_tested_pct']['max']}%  "
              f"lowest O2 with burning {r['lowest_o2_with_burning_pct']}  rho={r['o2_vs_extinction_ratio_spearman']}")
    print("FLEX diluents at 18-21% O2 near 1 atm")
    for r in m["PSI-69_FLEX"]["diluent_comparison_18_to_21_pct_o2_near_1_atm"]:
        print(f"  {r['fuel_material']:9} {r['diluent']:4} n={r['tests']:3} ratio {r['extinction_to_initial_diameter_ratio']}")
    for key, env in PRESETS.items():
        ev = json.load(open(os.path.join(OUT, f"evidence_{key}.json")))
        print(f"\n{key}: warnings {[w['code'] for w in ev['warnings']]}")
        for r in ev["investigations_by_closeness"]:
            ax = {a: v["status"].replace("_tested_range", "") for a, v in r["axes"].items()}
            print(f"  {r['investigation_id']:8} {ax}  nearest {r['nearest_tests'][0]['test_id']} d={r['nearest_tests'][0]['distance']}")


if __name__ == "__main__":
    main()
