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

Further sections: the other scoring values (run_values), weighting by purpose for all three
profiles with equal and rank-order-centroid weights (run_profiles), and SMAA, which keeps only the
order of importance of each profile's weights (run_smaa).

Run:  python3 validation/sensitivity.py        (prints the tables)
validation/run_validation.py adds the same tables to validation/report.md.
The weights themselves are the team's choice; this shows how much the ranking depends on them.
Standard library only.
"""
import math
import os
import random
import sys

ROOT =os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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


# ------------------------------------------------------- weighting by purpose (all three profiles)
# Each profile is tested on queries that the scorer reads as that purpose:
# - one-at-a-time x0.5 and x1.5 on each of its weights;
# - two other ways to derive weights from the same judgement: equal weights over its dimensions,
#   and rank-order centroid weights (ROC), which keep only the order of importance (tied ranks share
#   the mean of their centroid weights);
# - the weights of the other two profiles, to see whether the purpose changes the answer.
PROFILE_QUERIES = {
    "prevention": DEMO,
    "detection": ["smoke detector on ISS", "wire insulation overheating smoke", "smoke detector for a lunar rover", "kapton teflon smoke"],
    "suppression": ["CO2 suppression of heptane fire", "nitrogen extinguish fabric fire ISS", "fire extinguisher for a Mars habitat",
                    "inert gas suppression ISS"],
}


def roc_weights(w):
    dims = sorted([d for d, v in w.items() if v > 0], key=lambda d: -w[d])
    n = len(dims)
    base = [sum(1 / j for j in range(i, n + 1)) / n for i in range(1, n + 1)]
    out, i = {d: 0.0 for d in w}, 0
    while i < n:
        j = i
        while j + 1 < n and w[dims[j + 1]] == w[dims[i]]:
            j += 1
        m = sum(base[i:j + 1]) / (j - i + 1)
        for k in range(i, j + 1):
            out[dims[k]] = m
        i = j + 1
    return out


def run_profiles():
    cfg = scorer.load_config()
    catalog = scorer.load_catalog()

    def top(q, w):
        return [r["investigation_id"] for r in scorer.rank(q, config=cfg, catalog=catalog, weights_override=w)["results"]]

    res = {}
    for prof, qs in PROFILE_QUERIES.items():
        w = cfg["profiles"][prof]["weights"]
        read_as = {q: scorer.rank(q, config=cfg, catalog=catalog)["profile"] for q in qs}
        base = {q: top(q, w) for q in qs}
        oat = []
        for d, v in w.items():
            if v <= 0:
                continue
            for f in FACTORS:
                ww = dict(w)
                ww[d] = v * f
                t = sum(ww.values())
                ww = {k: x / t for k, x in ww.items()}
                for q in qs:
                    got = top(q, ww)
                    oat.append(dict(dim=d, factor=f, query=q, same=got == base[q], rank1=got[:1] == base[q][:1]))
        schemes = {"equal weights": {d: (1.0 if v > 0 else 0.0) for d, v in w.items()}, "rank-order centroid": roc_weights(w)}
        schemes.update({f"{o} weights": cfg["profiles"][o]["weights"] for o in PROFILE_QUERIES if o != prof})
        alt = {}
        for name, ww in schemes.items():
            alt[name] = [dict(query=q, got=top(q, ww), base=base[q]) for q in qs]
        res[prof] = dict(weights=w, read_as=read_as, oat=oat, alt=alt)
    return dict(version=cfg["version"], profiles=res)


def profiles_report_lines(res):
    lines = [f"## Weighting by purpose (config {res['version']})", "",
             "| Profile | Queries read as this purpose | One-at-a-time x0.5/x1.5: same top 3 | rank 1 changes | Scheme | Same top 3 | Same rank 1 |",
             "|---|---|---|---|---|---|---|"]
    for prof, r in res["profiles"].items():
        ok = sum(v == prof for v in r["read_as"].values())
        first = True
        for name, rows in r["alt"].items():
            same = sum(x["got"] == x["base"] for x in rows)
            r1 = sum(x["got"][:1] == x["base"][:1] for x in rows)
            head = (f"| {prof} | {ok} of {len(r['read_as'])} | {sum(x['same'] for x in r['oat'])} of {len(r['oat'])} | "
                    f"{sum(not x['rank1'] for x in r['oat'])} |") if first else "| | | | |"
            lines.append(f"{head} {name} | {same} of {len(rows)} | {r1} of {len(rows)} |")
            first = False
    lines += ["", "Rows where another scheme changes the top 3:", ""]
    for prof, r in res["profiles"].items():
        for name, rows in r["alt"].items():
            for x in rows:
                if x["got"] != x["base"]:
                    lines.append(f"- {prof}, {name}, \"{x['query']}\": {', '.join(x['got'])} (configured: {', '.join(x['base'])})")
    return lines


# ------------------------------------------------------- SMAA: uncertainty of the weights
# Stochastic multicriteria acceptability analysis with ordinal weight information (SMAA-O style):
# only the ORDER of importance of the profile's weights is trusted, not their values.
# Weight vectors are drawn uniformly from the simplex, sorted, and given to the dimensions in that
# order (dimensions with equal weights share their ranks in random order). For each query the
# share of draws that keep each investigation at rank 1 or in the top 3 is its acceptability.
SMAA_DRAWS = 300
SMAA_SEED = 20261114


def _ordinal_draw(w, rnd):
    dims = sorted([d for d, v in w.items() if v > 0], key=lambda d: -w[d])
    xs = sorted((-math.log(1.0 - rnd.random()) for _ in dims), reverse=True)
    t = sum(xs)
    xs = [x / t for x in xs]
    out, i = {d: 0.0 for d in w}, 0
    while i < len(dims):
        j = i
        while j + 1 < len(dims) and abs(w[dims[j + 1]] - w[dims[i]]) < 1e-12:
            j += 1
        vals = xs[i:j + 1]
        rnd.shuffle(vals)
        for k, d in enumerate(dims[i:j + 1]):
            out[d] = vals[k]
        i = j + 1
    return out


def run_smaa(draws=SMAA_DRAWS, seed=SMAA_SEED, weights_by_profile=None):
    cfg = scorer.load_config()
    catalog = scorer.load_catalog()
    rnd = random.Random(seed)
    res = {}
    for prof, qs in PROFILE_QUERIES.items():
        w = (weights_by_profile or {}).get(prof) or cfg["profiles"][prof]["weights"]
        samples = [_ordinal_draw(w, rnd) for _ in range(draws)]
        for q in qs:
            ref = [r["investigation_id"] for r in scorer.rank(q, config=cfg, catalog=catalog, weights_override=w)["results"]]
            first, top3, same1, same3 = {}, {}, 0, 0
            for ww in samples:
                got = [r["investigation_id"] for r in scorer.rank(q, config=cfg, catalog=catalog, weights_override=ww)["results"]]
                if got:
                    first[got[0]] = first.get(got[0], 0) + 1
                for x in got:
                    top3[x] = top3.get(x, 0) + 1
                same1 += got[:1] == ref[:1]
                same3 += set(got) == set(ref)
            res[q] = dict(profile=prof, ref=ref, same1=same1 / draws, same3=same3 / draws,
                          first={k: v / draws for k, v in first.items()}, top3={k: v / draws for k, v in top3.items()})
    return dict(version=cfg["version"], draws=draws, seed=seed, queries=res)


def smaa_report_lines(res):
    lines = [f"## Weight uncertainty: SMAA with the order of importance only (config {res['version']}, "
             f"{res['draws']} draws per profile, seed {res['seed']})", "",
             "| Profile | Query | Top 3 with the profile's weights | Same rank 1 | Same top 3 (as a set) | Top-3 acceptability of each investigation (10% or more) |",
             "|---|---|---|---|---|---|"]
    for q, r in res["queries"].items():
        acc = ", ".join(f"{k} {v:.0%}" for k, v in sorted(r["top3"].items(), key=lambda kv: -kv[1]) if v >= 0.10)
        lines.append(f"| {r['profile']} | {q} | {', '.join(r['ref'])} | {r['same1']:.0%} | {r['same3']:.0%} | {acc} |")
    return lines


if __name__ == "__main__":
    res = run()
    print("\n".join(report_lines(res)))
    print()
    print("\n".join(values_report_lines(run_values())))
    print()
    print("\n".join(profiles_report_lines(run_profiles())))
    print()
    print("\n".join(smaa_report_lines(run_smaa())))
