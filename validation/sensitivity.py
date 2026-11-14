#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude Code, catalog role) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""How much do the demo rankings move when one prevention weight changes?

Each non-zero weight of the default (prevention) profile is set to 0.5x and to 1.5x its value,
and the weights are rescaled to sum to 1. The demo queries are ranked with each variant, and the
top 3 investigations are compared with the top 3 under the configured weights:
- "same top 3": same investigations in the same order;
- "same set": same investigations, order changed;
- "rank 1 changed": a different investigation first.

Run:  python3 validation/sensitivity.py        (prints the table)
validation/run_validation.py adds the same table to validation/report.md.
The weights themselves are the team's choice; this shows how much the ranking depends on them.
Standard library only.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scoring import scorer  # noqa: E402

DEMO = ["ISS", "lunar habitat", "ISS cotton fabric", "lunar habitat cotton fabric"]
FACTORS = (0.5, 1.5)


def top3(query, weights, cfg, catalog):
    out = scorer.rank(query, config=cfg, catalog=catalog, weights_override=weights)
    return [r["investigation_id"] for r in out["results"]]


def run(queries=DEMO, factors=FACTORS):
    cfg = scorer.load_config()
    catalog = scorer.load_catalog()
    profile = cfg["default_profile"]
    base_w = dict(cfg["profiles"][profile]["weights"])
    dims = [d for d, w in base_w.items() if w > 0]
    rows = []
    for q in queries:
        base = top3(q, base_w, cfg, catalog)
        for d in dims:
            for f in factors:
                w = dict(base_w)
                w[d] = base_w[d] * f
                total = sum(w.values())
                w = {k: v / total for k, v in w.items()}
                got = top3(q, w, cfg, catalog)
                kind = "same top 3" if got == base else ("same set" if sorted(got) == sorted(base) else "changed")
                rows.append(dict(query=q, dim=d, factor=f, base=base, got=got, kind=kind,
                                 rank1_changed=bool(got) and bool(base) and got[0] != base[0]))
    return dict(profile=profile, version=cfg["version"], weights=base_w, rows=rows)


def summary(res):
    rows = res["rows"]
    same = sum(r["kind"] == "same top 3" for r in rows)
    same_set = sum(r["kind"] == "same set" for r in rows)
    r1 = sum(r["rank1_changed"] for r in rows)
    return same, same_set, r1, len(rows)


def report_lines(res):
    same, same_set, r1, n = summary(res)
    lines = [f"## Weight sensitivity (each {res['profile']} weight x0.5 and x1.5, rescaled to sum 1; config {res['version']})", "",
             f"- {same} of {n} variants keep the same top 3 in the same order; {same_set} keep the same three in another order; "
             f"rank 1 changes in {r1}.", "",
             "| Query | Weight | Factor | Top 3 | Result |", "|---|---|---|---|---|"]
    for r in res["rows"]:
        if r["kind"] != "same top 3":
            note = r["kind"] + ("; rank 1 changed" if r["rank1_changed"] else "")
            lines.append(f"| {r['query']} | {r['dim']} | x{r['factor']:g} | {', '.join(r['got'])} (was {', '.join(r['base'])}) | {note} |")
    if same == n:
        lines.append("| (all) | | | | same top 3 |")
    return lines


if __name__ == "__main__":
    res = run()
    print("\n".join(report_lines(res)))
