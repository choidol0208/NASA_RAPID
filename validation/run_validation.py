#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Run the catalog-filter validation scenarios and write a report.

Usage:
    python3 validation/run_validation.py
    python3 validation/run_validation.py --target app.pipeline:rank   # test the dashboard's own function
    python3 validation/run_validation.py --report validation/report.md --json validation/report.json

The target is any function `f(query) -> dict` that returns the scorer's shape:
    {"status": str, "scenario": {...}, "assumptions": [{"field": ...}], "warnings": [{"code": ...}],
     "results": [{"investigation_id": str, "warnings": [{"code": ...}], ...}]}
Exit code 0 = all checks passed, 1 = at least one failure.
"""
import argparse
import datetime
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)


def load_target(spec):
    mod, fn = spec.split(":")
    return getattr(importlib.import_module(mod), fn)


def check(sc, out, cache):
    e, fails = sc["expect"], []
    ids = [r["investigation_id"] for r in out.get("results", [])]
    codes = [w["code"] for w in out.get("warnings", [])]
    if "status" in e and out.get("status") != e["status"]:
        fails.append(f"status {out.get('status')} != {e['status']}")
    for k, v in e.get("scenario", {}).items():
        got = out.get("scenario", {}).get(k)
        if (isinstance(v, float) and (got is None or abs(float(got) - v) > 0.05)) or (not isinstance(v, float) and got != v):
            fails.append(f"scenario.{k} = {got!r}, expected {v!r}")
    assumed = [a["field"] for a in out.get("assumptions", [])]
    for f in e.get("assumed_fields_include", []):
        if f not in assumed:
            fails.append(f"assumption for {f} not shown")
    if "top1_in" in e and (not ids or ids[0] not in e["top1_in"]):
        fails.append(f"top1 {ids[:1]} not in {e['top1_in']}")
    for key in ("top_k_includes_any", "top_k_includes_any_2"):
        if key in e and not set(ids) & set(e[key]):
            fails.append(f"none of {e[key]} in top-k {ids}")
    if "top_k_includes_all" in e and not set(e["top_k_includes_all"]) <= set(ids):
        fails.append(f"missing {sorted(set(e['top_k_includes_all']) - set(ids))} in top-k {ids}")
    if "top_k_at_least" in e:
        n, pool = e["top_k_at_least"]
        hit = len(set(ids) & set(pool))
        if hit < n:
            fails.append(f"only {hit} of {pool} in top-k {ids} (need {n})")
    if "top_k_excludes" in e and set(ids) & set(e["top_k_excludes"]):
        fails.append(f"excluded {sorted(set(ids) & set(e['top_k_excludes']))} in top-k")
    for c in e.get("warnings_include", []):
        if c not in codes:
            fails.append(f"warning {c} missing")
    for c in e.get("warnings_exclude", []):
        if c in codes:
            fails.append(f"warning {c} should not appear")
    for inv, need in e.get("result_warnings_include", {}).items():
        for r in out.get("results", []):
            if r["investigation_id"] == inv:
                have = [w["code"] for w in r.get("warnings", [])]
                for c in need:
                    if c not in have:
                        fails.append(f"{inv} lacks warning {c}")
    if "same_top_k_as" in e:
        other = cache.get(e["same_top_k_as"])
        if other is not None and [r["investigation_id"] for r in other.get("results", [])] != ids:
            fails.append(f"top-k differs from {e['same_top_k_as']}")
    return ids, codes, fails


def stability(spec, scenarios, target_mod):
    """Perturb each weight by +/- delta; report scenarios whose rank-1 changes."""
    from scoring import scorer  # perturbation needs the reference scorer
    cfg = scorer.load_config()
    rows = []
    by_id = {s["id"]: s for s in scenarios}
    for sid in spec["scenarios"]:
        q = by_id[sid]["query"]
        base = scorer.rank(q, config=cfg)
        if not base["results"]:
            continue
        top = base["results"][0]["investigation_id"]
        flips = []
        for dim in base["weights"]:
            for sign in (+1, -1):
                w = dict(base["weights"])
                w[dim] = max(0.0, w[dim] + sign * spec["delta"])
                out = scorer.rank(q, config=cfg, weights_override=w)
                t = out["results"][0]["investigation_id"] if out["results"] else None
                if t != top:
                    flips.append(f"{dim}{'+' if sign > 0 else '-'}{spec['delta']} -> {t}")
        rows.append((sid, top, flips))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="scoring.scorer:rank")
    ap.add_argument("--scenarios", default=os.path.join(HERE, "scenarios.json"))
    ap.add_argument("--report", default=os.path.join(HERE, "report.md"))
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    spec = json.load(open(args.scenarios, encoding="utf-8"))
    fn = load_target(args.target)
    cache, rows, n_fail = {}, [], 0
    for sc in spec["scenarios"]:
        try:
            out = fn(sc["query"])
            cache[sc["id"]] = out
            ids, codes, fails = check(sc, out, cache)
        except Exception as ex:  # a crash is a failure, not a stop
            ids, codes, fails = [], [], [f"crash: {type(ex).__name__}: {ex}"]
        n_fail += bool(fails)
        rows.append(dict(id=sc["id"], group=sc["group"], query=sc["query"], top=ids, warnings=codes,
                         passed=not fails, fails=fails, why=sc.get("why_ko", "")))
    stab = stability(spec["stability"], spec["scenarios"], args.target) if "stability" in spec else []
    total = len(rows)
    lines = [f"# Catalog filter validation report", "",
             f"- Run: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} · target `{args.target}`",
             f"- Result: **{total - n_fail}/{total} scenarios passed**", "",
             "| ID | Group | Query | Top 3 | Warnings | Result |", "|---|---|---|---|---|---|"]
    for r in rows:
        res = "PASS" if r["passed"] else "FAIL: " + "; ".join(r["fails"])
        lines.append(f"| {r['id']} | {r['group']} | {r['query'] or '(empty)'} | {', '.join(r['top'])} | {', '.join(r['warnings'])} | {res} |")
    if stab:
        lines += ["", "## Weight stability (each weight ±0.05)", "", "| Scenario | Rank 1 | Changes rank 1 |", "|---|---|---|"]
        for sid, top, flips in stab:
            lines.append(f"| {sid} | {top} | {'; '.join(flips) if flips else 'stable'} |")
    if args.target == "scoring.scorer:rank":  # the sensitivity table uses the reference scorer
        sys.path.insert(0, HERE)
        import sensitivity
        lines += [""] + sensitivity.report_lines(sensitivity.run())
    report = "\n".join(lines) + "\n"
    with open(args.report, "w", encoding="utf-8") as fh:
        fh.write(report)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(dict(rows=rows, stability=stab), fh, ensure_ascii=False, indent=2)
    print(report)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
