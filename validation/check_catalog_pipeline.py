#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Check the catalog (data/catalog/configurations.csv) against the data role's audited
pipeline (data/pipeline/tests.csv), for every investigation with a test-level table.

Usage:  python3 validation/check_catalog_pipeline.py      (exit 1 on any difference)

Per investigation:
- Test count: the catalog's test_count_config, summed over its configurations, equals the
  number of rows in tests.csv.
- O2 (separately for the surrounding atmosphere and for oxidizer streams) and pressure:
  the catalog's lowest and highest values equal tests.csv's, to the catalog's rounding.
  Where tests.csv flags that it used the midpoint of a range written in the NASA cell
  (`<variable>:range_in_source_midpoint_used`), the catalog keeps the written range, so only
  containment is checked.
- Flow: every tests.csv flow value (flow_cms, flow_min_cms, and flow_max_cms if present)
  lies inside the catalog range, and the bounds are equal, except where a documented
  reading of the NASA table explains a wider catalog range (FLOW_WIDER below).
- A value the catalog has and tests.csv lacks (record text, quiescent tests) is listed,
  not failed. A value tests.csv has and the catalog lacks fails.
Standard library only.
"""
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOL = 0.051  # catalog values carry one decimal; pipeline values carry more

# Catalog flow ranges wider than tests.csv, with the reason read from the NASA table.
FLOW_WIDER = {
    "PSI-25": "BASS-II 'Air display' cells record the flow raised during a test (row 72 'incr to max 38.5', "
              "73 'incr to 28', 74 '4 incr to 26.5' for rods; row 115 '9 29' for SIBAL), within the record's 40 cm/s; "
              "tests.csv keeps each cell's starting number (request 20261114-1319 to data). "
              "See source_notes of BASS-II-C03 and C04.",
}


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def span(values):
    v = [x for x in values if x is not None]
    return (min(v), max(v)) if v else None


def fmt(r):
    return "-" if r is None else f"{r[0]:g}-{r[1]:g}"


def main():
    tests = list(csv.DictReader(open(os.path.join(ROOT, "data", "pipeline", "tests.csv"), encoding="utf-8")))
    cfgs = list(csv.DictReader(open(os.path.join(ROOT, "data", "catalog", "configurations.csv"), encoding="utf-8")))
    by_inv = {}
    for t in tests:
        by_inv.setdefault(t["investigation_id"], []).append(t)
    has_flow_max = bool(tests) and "flow_max_cms" in tests[0]
    fails, notes, rows = [], [], []

    for inv in sorted(by_inv, key=lambda a: int(a.split("-")[1])):
        ts = by_inv[inv]
        cs = [c for c in cfgs if c["psi_accession"] == inv]
        name = cs[0]["investigation_id"] if cs else inv
        if not cs:
            fails.append(f"{inv}: {len(ts)} tests in tests.csv, no catalog configuration")
            continue
        flags = ";".join(t.get("flags", "") for t in ts)

        n_cat = sum(int(float(c["test_count_config"])) for c in cs if c["test_count_config"] and c["tests_table_ref"])
        ok = n_cat == len(ts)
        if not ok:
            fails.append(f"{name} ({inv}): test count catalog {n_cat}, tests.csv {len(ts)}")
        out = [f"{name} ({inv})", f"tests {n_cat}/{len(ts)}{'' if ok else ' DIFF'}"]

        def compare(label, var, cat, pipe):
            if cat is None and pipe is None:
                return
            if pipe is None:
                notes.append(f"{name}: {label} {fmt(cat)} in the catalog only (not in tests.csv)")
                out.append(f"{label} {fmt(cat)}/-")
                return
            if cat is None:
                fails.append(f"{name} ({inv}): {label} {fmt(pipe)} in tests.csv, missing in the catalog")
                out.append(f"{label} -/{fmt(pipe)} DIFF")
                return
            inside = cat[0] - TOL <= pipe[0] and pipe[1] <= cat[1] + TOL
            equal = abs(cat[0] - pipe[0]) <= TOL and abs(cat[1] - pipe[1]) <= TOL
            if var == "flow" and inv in FLOW_WIDER and inside and not equal:
                notes.append(f"{name}: flow catalog {fmt(cat)} wider than tests.csv {fmt(pipe)}: {FLOW_WIDER[inv]}")
                good, tag = True, " (documented)"
            elif var != "flow" and f"{var}:range_in_source_midpoint_used" in flags and inside:
                good, tag = True, "" if equal else " (range kept; pipeline uses midpoint)"
            else:
                good, tag = equal, ""
            if not good:
                fails.append(f"{name} ({inv}): {label} catalog {fmt(cat)}, tests.csv {fmt(pipe)}")
            out.append(f"{label} {fmt(cat)}/{fmt(pipe)}{'' if good else ' DIFF'}{tag}")

        for basis in ("ambient", "oxidizer_stream"):
            sel = [c for c in cs if (c["o2_reference"] or "ambient") == basis]
            cat = span([f(c[k]) for c in sel for k in ("o2_min_pct", "o2_max_pct")])
            pipe = span(f(t["o2_pct"]) for t in ts if t["o2_basis"] == basis)
            compare("O2" if basis == "ambient" else "O2 stream", "o2_pct", cat, pipe)
        compare("kPa", "pressure_kpa", span([f(c[k]) for c in cs for k in ("pressure_min_kpa", "pressure_max_kpa")]),
                span(f(t["pressure_kpa"]) for t in ts))
        fkeys = ("flow_cms", "flow_min_cms") + (("flow_max_cms",) if has_flow_max else ())
        compare("flow", "flow", span([f(c[k]) for c in cs for k in ("flow_min_cms", "flow_max_cms")]),
                span(f(t[k]) for t in ts for k in fkeys))
        rows.append(out)

    print("Catalog vs data/pipeline/tests.csv (catalog/pipeline)")
    for r in rows:
        print("  " + " | ".join(r))
    for n in notes:
        print("note: " + n)
    if fails:
        print(f"\n{len(fails)} difference(s):")
        for x in fails:
            print("  " + x)
        return 1
    print(f"\nOK: {len(rows)} investigations with test-level tables agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
