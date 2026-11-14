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


# --------------------------------------------------------------- the other values of the config
# Each group is scaled by 0.5 and 1.5. Similarity values are capped at 1.0, and table entries that are
# already 1.0 (a full match) are left alone. Thresholds that only change labels or warnings
# (confidence, outside_range_threshold) and decisions that are not scales (atmosphere fallback 21%
# and 101.3 kPa, top_k) are not varied.
SCALARS = [
    ("similarity.o2.above_scale_ln", "O2 decay above the tested maximum"),
    ("similarity.o2.below_scale_ln", "O2 decay below the tested minimum"),
    ("similarity.pressure.sigma_ln", "pressure width (log)"),
    ("similarity.flow_speed.sigma_ln", "flow-speed width (log)"),
    ("similarity.flow_speed.offset_cms", "flow-speed offset"),
    ("similarity.unknown_value", "value for 'not recorded'"),
    ("gate.min_similarity", "gate threshold"),
    ("gate.factor", "gate floor"),
    ("evidence.span", "evidence factor span (base = 1 - span)"),
    ("selection.tie_points", "tie margin"),
    ("complementary_slot.min_score_ratio", "complementary slot minimum score"),
    ("similarity.diluent.cp_ratio_exponent", "diluent heat-capacity exponent"),
]
TABLES = [
    ("similarity.flow_config_matrix", "flow configuration matrix (off-diagonal)"),
    ("similarity.fuel", "fuel similarity table"),
    ("similarity.geometry", "sample-shape table"),
    ("similarity.role", "research-purpose table"),
    ("evidence.data_availability", "data-availability table"),
]


def _get(d, path):
    for k in path.split("."):
        d = d[k]
    return d


def _scale_table(t, f):
    for k, v in t.items():
        if isinstance(v, dict):
            _scale_table(v, f)
        elif isinstance(v, (int, float)) and v < 1.0:
            t[k] = min(1.0, v * f)


def run_values(queries=DEMO, factors=FACTORS):
    import copy
    cfg0 = scorer.load_config()
    catalog = scorer.load_catalog()
    base = {q: [r["investigation_id"] for r in scorer.rank(q, config=cfg0, catalog=catalog)["results"]] for q in queries}
    rows = []
    for path, label in SCALARS + TABLES:
        for f in factors:
            cfg = copy.deepcopy(cfg0)
            parent, key = (path.rsplit(".", 1) + [None])[:2]
            if (path, label) in TABLES:
                _scale_table(_get(cfg, path), f)
            elif path == "evidence.span":
                cfg["evidence"]["span"] = min(1.0, cfg0["evidence"]["span"] * f)
                cfg["evidence"]["base"] = 1.0 - cfg["evidence"]["span"]
            else:
                obj = _get(cfg, parent)
                v = obj[key] * f
                obj[key] = min(1.0, v) if path in ("similarity.unknown_value", "gate.factor", "complementary_slot.min_score_ratio") else v
            for q in queries:
                got = [r["investigation_id"] for r in scorer.rank(q, config=cfg, catalog=catalog)["results"]]
                kind = "same top 3" if got == base[q] else ("same set" if sorted(got) == sorted(base[q]) else "changed")
                rows.append(dict(value=path, label=label, factor=f, query=q, base=base[q], got=got, kind=kind,
                                 rank1_changed=bool(got) and bool(base[q]) and got[0] != base[q][0]))
    return dict(version=cfg0["version"], rows=rows)


def values_report_lines(res):
    rows = res["rows"]
    lines = [f"## Sensitivity to the other values (each x0.5 and x1.5 on the four demo queries; config {res['version']})", "",
             f"- {sum(r['kind'] == 'same top 3' for r in rows)} of {len(rows)} runs keep the same top 3 in the same order; "
             f"{sum(r['kind'] == 'same set' for r in rows)} keep the same three in another order; rank 1 changes in "
             f"{sum(r['rank1_changed'] for r in rows)}.", "",
             "| Value | Same top 3 (of 8) | Changes |", "|---|---|---|"]
    order = []
    for r in rows:
        if r["value"] not in order:
            order.append(r["value"])
    for v in order:
        rs = [r for r in rows if r["value"] == v]
        ch = [f"x{r['factor']:g} {r['query']}: {', '.join(r['got'])}" + (" (rank 1)" if r["rank1_changed"] else "")
              for r in rs if r["kind"] != "same top 3"]
        lines.append(f"| {rs[0]['label']} (`{v}`) | {sum(r['kind'] == 'same top 3' for r in rs)} | {'; '.join(ch) or '—'} |")
    return lines


if __name__ == "__main__":
    res = run()
    print("\n".join(report_lines(res)))
    print()
    print("\n".join(values_report_lines(run_values())))
