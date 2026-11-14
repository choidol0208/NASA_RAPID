# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Component K: how firm is each top rank of the team's ranking under the team's own weights?

For the four preset queries the page uses ("ISS", "lunar habitat", "spacesuit", "Mars base") this
script samples weight vectors around the configured profile and re-scores every catalog
configuration with each of them, then writes data/insights/robustness.json. No language model.

Method (docs/ai_layer_design.json, component K; SMAA-style weight sampling):

- Weights: draws from Dirichlet(50 x profile weights) ("local", around the configured profile) and
  from Dirichlet(1) ("uniform", no stated preference), over the profile's own keys whose weight is
  not 0; a key with profile weight 0 (diluent) stays 0. Seed 42 for the file, seed 43 for the check.
  numpy.random.default_rng([seed, 0]) draws the local run, default_rng([seed, 1]) the uniform run.
- Re-scoring, two code paths that must agree:
  1. this file's own NumPy re-score. The similarities, the gate and the evidence factor do not
     depend on the weights, so they are taken once per configuration from scoring.scorer
     (interpret, similarities, score_config, unchanged); a draw's score is then
     100 x evidence x gate x (sum of w_d x S_d over the scored dimensions) / (sum of w_d), as in
     scoring.scorer.score_config. Scores are kept unrounded.
  2. scoring.scorer.rank(query, catalog=..., config=..., weights_override=<full dict>) per draw,
     unchanged, reading the 'ranking' list (scores rounded to 0.1, as the page prints them) and
     'results' (the three results the page shows).
  Path 1 rounded like the scorer must equal path 2 for every investigation in every draw.
- Shares are tie-aware: in a draw every investigation whose (unrounded) score is within 1e-9 of the
  top score counts as first. "Among the first three" counts an investigation when fewer than three
  others score more than it (by more than 1e-9). Two investigations that are level in every draw of
  both runs are reported as a tie, not as an order.
- assumed_dims is copied from rank() at the profile weights: the atmosphere values the scorer filled
  in (scoring_config.json atmosphere_fallback) because the record does not report them.
  assumed_dims_scored keeps those that the query actually scores.

Reads scoring/scorer.py, scoring/scoring_config.json and data/catalog/*.csv read-only; changes none
of them. Sensitivity of the team's ranking to the team's own weights: not a probability that a study
is relevant, and not a NASA result.

Run:  python3 ai/robustness.py            (writes data/insights/robustness.json, about 15 s: 16,000 rank() calls)
      python3 ai/robustness.py --check    (builds in memory, compares with the file, writes nothing)
      check_file(rep)                     (for ai/check_all.py: fast checks, NumPy path only)
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import checks as C  # noqa: E402
from ai import config, meta as metamod  # noqa: E402
from scoring import scorer  # noqa: E402

ROOT = config.ROOT
OUT = config.INSIGHTS_DIR / "robustness.json"
BUILT_BY = "ai/robustness.py"
INPUTS = [ROOT / "scoring" / "scorer.py", ROOT / "scoring" / "scoring_config.json",
          ROOT / "data" / "catalog" / "investigations.csv", ROOT / "data" / "catalog" / "configurations.csv"]

# The exact strings the page passes to rank() (same list as ai/check_all.py QUERIES).
QUERIES = (("iss", "ISS"), ("lunar_habitat", "lunar habitat"), ("spacesuit", "spacesuit"),
           ("mars_habitat", "Mars base"))
SEED = 42
CHECK_SEED = 43
DRAWS = 2000
CONCENTRATION = 50.0
TIE_TOL = 1e-9
MAX_SEED_DIFF_POINTS = 2.0
KINDS = ("local", "uniform")
DIM_LABELS = {"o2": "O2", "pressure": "pressure", "flow": "flow", "fuel": "fuel", "geometry": "sample shape",
              "role": "research purpose", "diluent": "diluent"}
ASSUMED_TO_DIM = {"O2": "o2", "pressure": "pressure"}  # rank() assumed_dims names -> scorer dimensions

LABEL = ("Sensitivity of the team's ranking to the team's own weights. Not a probability that a study is "
         "relevant, and not a NASA result. Weight sampling cannot show that a rank rests on an assumed "
         "atmosphere; that is stated separately (assumed_dims).")


class RobustnessError(RuntimeError):
    pass


# ------------------------------------------------------------------------------ weights

def sample_weights(profile_weights, n, seed, kind):
    """n weight vectors over the profile's own keys (a full dict each, keys in profile order).
    Keys with profile weight 0 stay 0. Returns (keys, matrix n x len(keys))."""
    keys = list(profile_weights)
    w = np.array([float(profile_weights[k]) for k in keys])
    nz = w > 0
    if kind == "local":
        alpha = CONCENTRATION * w[nz]
    elif kind == "uniform":
        alpha = np.ones(int(nz.sum()))
    else:
        raise ValueError(kind)
    rng = np.random.default_rng([seed, KINDS.index(kind)])
    out = np.zeros((n, len(keys)))
    out[:, nz] = rng.dirichlet(alpha, n)
    return keys, out


def as_dict(keys, row):
    return {k: float(v) for k, v in zip(keys, row)}


# ------------------------------------------------------------------------------ scoring

def score_table(query, cfg, cat):
    """Everything about a query that does not depend on the weights, from scoring.scorer itself."""
    sc, _src, _assumptions, out_of_scope, informative = scorer.interpret(query, cfg)
    live = scorer.rank(query, config=cfg, catalog=cat)
    if live["status"] != "ok":
        raise RobustnessError(f"{query!r}: rank() status {live['status']}")
    profile = live["profile"]
    weights = dict(cfg["profiles"][profile]["weights"])
    _inv, cfgs = cat
    pre = [(c,) + tuple(scorer.similarities(sc, c, cfg)) for c in cfgs]
    caps = {}
    for d in cfg["similarity"].get("unknown_cap_dims", []):
        known = [S[d] for _, S, _, _, _ in pre if d in S and S[d] is not None]
        if known:
            caps[d] = max(known)
    rows = [(c, scorer.score_config(sc, c, cfg, weights, S, caps), fb) for c, S, fb, _sp, _ce in pre]
    scored = [d for d in rows[0][1]["similarity"] if weights.get(d, 0.0) > 0]
    for _, s, _ in rows:
        if [d for d in s["similarity"] if weights.get(d, 0.0) > 0] != scored:
            raise RobustnessError(f"{query!r}: scored dimensions differ between configurations")
    sim = np.array([[s["similarity"][d] for d in scored] for _, s, _ in rows])
    factor = np.array([100.0 * s["evidence"] * s["gate"] for _, s, _ in rows])
    invs = list(dict.fromkeys(c["investigation_id"] for c, _, _ in rows))
    inv_index = np.array([invs.index(c["investigation_id"]) for c, _, _ in rows])
    return dict(query=query, scenario=sc, live=live, profile=profile, weights=weights, scored=scored,
                sim=sim, factor=factor, invs=invs, inv_index=inv_index,
                config_ids=[c["config_id"] for c, _, _ in rows])


def inv_scores(tab, keys, W):
    """Unrounded score of each investigation (its best configuration) for each weight row."""
    cols = [keys.index(d) for d in tab["scored"]]
    Ws = W[:, cols]
    cfg_scores = tab["factor"][None, :] * (Ws @ tab["sim"].T) / Ws.sum(axis=1, keepdims=True)
    out = np.full((W.shape[0], len(tab["invs"])), -np.inf)
    for j in range(len(tab["invs"])):
        out[:, j] = cfg_scores[:, tab["inv_index"] == j].max(axis=1)
    return out


def round_like_scorer(x, n=1):
    """scoring.scorer._r, vectorised: snap to 9 decimals, then round half up."""
    m = 10 ** n
    return np.floor(np.round(x, 9) * m + 0.5) / m


def rank_path(tab, keys, W, cfg, cat):
    """Per draw, scoring.scorer.rank with weights_override: rounded ranking scores, shown results."""
    n, J = W.shape[0], len(tab["invs"])
    scores = np.full((n, J), np.nan)
    shown = np.zeros((n, J), dtype=bool)
    listed_first = np.zeros((n, J), dtype=bool)
    pos = {inv: j for j, inv in enumerate(tab["invs"])}
    for i in range(n):
        out = scorer.rank(tab["query"], config=cfg, catalog=cat, weights_override=as_dict(keys, W[i]))
        for r in out["ranking"]:
            scores[i, pos[r["investigation_id"]]] = r["score"]
        for k, r in enumerate(out["results"]):
            shown[i, pos[r["investigation_id"]]] = True
            if k == 0:
                listed_first[i, pos[r["investigation_id"]]] = True
    return scores, shown, listed_first


def tie_stats(S, top_k):
    """Tie-aware per-draw indicators from a draws x investigations score matrix."""
    top = S.max(axis=1, keepdims=True)
    first = S >= top - TIE_TOL
    greater = (S[:, None, :] > S[:, :, None] + TIE_TOL).sum(axis=2)  # [i, j]: how many score above j
    in_top = greater < top_k
    level = np.abs(S[:, :, None] - S[:, None, :]) <= TIE_TOL      # [i, j, k]: j and k level
    return first, in_top, level


def run_kind(tab, cfg, cat, seed, kind, draws, top_k, with_rank=True):
    keys, W = sample_weights(tab["weights"], draws, seed, kind)
    S = inv_scores(tab, keys, W)
    first, in_top, level = tie_stats(S, top_k)
    shown_disp = round_like_scorer(S)
    first_disp = shown_disp >= shown_disp.max(axis=1, keepdims=True) - TIE_TOL
    res = dict(keys=keys, W=W, S=S, first=first, in_top=in_top, level=level, first_disp=first_disp)
    if with_rank:
        t0 = time.time()
        rs, shown, listed_first = rank_path(tab, keys, W, cfg, cat)
        mism = int(np.sum(np.abs(rs - shown_disp) > 1e-9))
        res.update(rank_scores=rs, shown=shown, listed_first=listed_first, mismatches=mism,
                   rank_calls=draws, rank_seconds=time.time() - t0)
    return res


# ------------------------------------------------------------------------------ the file

def _share(mask):
    return round(float(np.mean(mask)), 4)


def _names(ids):
    ids = list(ids)
    if len(ids) <= 1:
        return "".join(ids)
    return ", ".join(ids[:-1]) + " and " + ids[-1]


def display_line(entry, run_facts):
    """The one line a dashboard could print under a live top-3 result, and the rule that chose it."""
    n = run_facts["draws_per_run"]
    n_all = run_facts["draws_both_runs"]
    assumed = [DIM_LABELS[ASSUMED_TO_DIM[a]] for a in entry["assumed_dims_scored"]]
    tied_all = entry["tied_in_every_draw_with"]
    level = f"Level with {_names(tied_all)} in every one of the team's {n_all:,} sampled weightings"
    if assumed:
        # Design rule: no stability figure where the rank rests on an assumed atmosphere.
        rule = "assumed_atmosphere"
        line = (f"Rank uses an assumed atmosphere for values the record does not report "
                f"({' and '.join(assumed)}).")
        if tied_all:
            rule = "assumed_atmosphere_and_tie"
            line = (f"{level} (a tie, not an order); the rank uses an assumed atmosphere for values the "
                    f"record does not report ({' and '.join(assumed)}).")
    elif tied_all:
        rule = "tie_in_every_draw"
        g = entry["first_or_tied_share_local"]  # level in every draw, so first together
        if g >= 1.0:
            line = f"{level}: a tie, not an order."
        else:
            line = (f"{level} (a tie, not an order); the two are first together in {round(100 * g, 1):g}% "
                    f"of the {n:,} drawn around the profile weights.") if len(tied_all) == 1 else (
                    f"{level} (a tie, not an order); they are first together in {round(100 * g, 1):g}% "
                    f"of the {n:,} drawn around the profile weights.")
    else:
        x = round(100 * entry["first_or_tied_share_local"], 1)
        z = round(100 * entry["top3_share_local"], 1)
        partners = [p for p in entry["tied_for_first_with"] if p["share"] > 0]
        if partners:
            p = max(partners, key=lambda q: q["share"])
            y = round(100 * p["share"], 1)
            rule = "tied_share"
            line = f"Tied for first with {p['investigation_id']} in {y:g}% of the team's {n:,} sampled weightings around the profile weights."
        elif x > 0:
            rule = "first_share"
            line = (f"First in {x:g}% of the team's {n:,} sampled weightings around the profile weights, and among the first three in "
                    f"{z:g}%.")
        else:
            rule = "top3_share"
            line = (f"Among the first three in {z:g}% of the team's {n:,} sampled weightings around the profile "
                    f"weights, and first in none of them.")
    return line, rule


def build_run(scenario_id, query, cfg, cat, seed=SEED, draws=DRAWS, with_rank=True):
    tab = score_table(query, cfg, cat)
    live = tab["live"]
    top_k = cfg["selection"]["top_k"]
    invs = tab["invs"]
    J = len(invs)
    pos = {inv: j for j, inv in enumerate(invs)}

    # 1. the unperturbed profile weights reproduce the live ranking, by both paths
    keys = list(tab["weights"])
    W0 = np.array([[float(tab["weights"][k]) for k in keys]])
    S0 = inv_scores(tab, keys, W0)[0]
    live_scores = {r["investigation_id"]: r["score"] for r in live["ranking"]}
    np_equal = all(abs(float(round_like_scorer(S0[pos[i]])) - s) < 1e-9 for i, s in live_scores.items())
    again = scorer.rank(query, config=cfg, catalog=cat, weights_override=dict(tab["weights"]))
    live_top = [r["investigation_id"] for r in live["results"]]
    again_top = [r["investigation_id"] for r in again["results"]]
    if not np_equal or again_top != live_top:
        raise RobustnessError(f"{query!r}: the profile weights do not reproduce the live ranking "
                              f"(numpy equal {np_equal}; rank {again_top} vs live {live_top})")

    runs = {k: run_kind(tab, cfg, cat, seed, k, draws, top_k, with_rank=with_rank) for k in KINDS}
    loc, uni = runs["local"], runs["uniform"]
    if with_rank:
        for k in KINDS:
            if runs[k]["mismatches"]:
                raise RobustnessError(f"{query!r} {k}: {runs[k]['mismatches']} score(s) differ between the "
                                      "NumPy re-score and scoring.scorer.rank")

    level_all = loc["level"].all(axis=0) & uni["level"].all(axis=0)  # [j, k] level in every draw of both runs
    ranking_pos = {r["investigation_id"]: n for n, r in enumerate(live["ranking"], start=1)}
    live_entry = {r["investigation_id"]: r for r in live["ranking"]}
    shown_rank = {r["investigation_id"]: r["rank"] for r in live["results"]}
    report = [i for i in live_top]
    for j in range(J):
        if (loc["first"][:, j].any() or uni["first"][:, j].any()) and invs[j] not in report:
            report.append(invs[j])
    report = sorted(report, key=lambda i: (shown_rank.get(i, 99), ranking_pos[i]))

    results = []
    for inv in report:
        j = pos[inv]
        e = live_entry[inv]
        partners = []
        for k in range(J):
            if k == j:
                continue
            both_l = loc["first"][:, j] & loc["first"][:, k]
            both_u = uni["first"][:, j] & uni["first"][:, k]
            if both_l.any() or both_u.any():
                partners.append({"investigation_id": invs[k], "share": _share(both_l),
                                 "share_uniform": _share(both_u)})
        partners.sort(key=lambda p: (-p["share"], -p["share_uniform"], ranking_pos[p["investigation_id"]]))
        tied_all = [invs[k] for k in range(J) if k != j and level_all[j, k]]
        tied_all.sort(key=lambda i: ranking_pos[i])
        assumed = list(e.get("assumed_dims") or [])
        entry = {
            "investigation_id": inv,
            "live_rank": shown_rank.get(inv),
            "live_position_in_ranking": ranking_pos[inv],
            "live_config_id": e["config_id"],
            "first_or_tied_share_local": _share(loc["first"][:, j]),
            "top3_share_local": _share(loc["in_top"][:, j]),
            "first_or_tied_share_uniform": _share(uni["first"][:, j]),
            "top3_share_uniform": _share(uni["in_top"][:, j]),
            "first_alone_share_local": _share(loc["first"][:, j] & (loc["first"].sum(axis=1) == 1)),
            "first_or_tied_share_local_at_displayed_precision": _share(loc["first_disp"][:, j]),
            "tied_for_first_with": partners,
            "tied_in_every_draw_with": tied_all,
            "assumed_dims": assumed,
            "assumed_dims_scored": [a for a in assumed if ASSUMED_TO_DIM.get(a) in tab["scored"]],
            "unknown_dims": list(e.get("unknown_dims") or []),
        }
        if with_rank:
            entry["shown_in_results_share_local"] = _share(loc["shown"][:, j])
            entry["listed_first_share_local"] = _share(loc["listed_first"][:, j])
        if inv not in shown_rank and loc["first"][:, j].all():
            moved = [r["investigation_id"] for r in live["results"] if r.get("tie_note")]
            entry["note"] = ("Level with the top score in every sampled weighting but not one of the results "
                             "the page lists: the scorer orders equal scores by evidence factor, 1 g comparison "
                             "and configuration id"
                             + (f", and its near-tie rule (scoring_config.json selection.tie_points) moved "
                                f"{_names(moved)} up" if moved else "") + ".")
        if e.get("tie_note") and inv in shown_rank:
            entry["listing_note"] = ("Listed by the scorer's near-tie rule (scoring_config.json "
                                     "selection.tie_points), which orders close scores by evidence quality; "
                                     f"{_names(i for i in invs if S0[pos[i]] > S0[j] + TIE_TOL)} score more "
                                     "at the profile weights.")
        results.append(entry)

    # 2. ties that hold in every draw, as groups
    groups, seen = [], set()
    for r in results:
        if r["investigation_id"] in seen or not r["tied_in_every_draw_with"]:
            continue
        g = [r["investigation_id"]] + r["tied_in_every_draw_with"]
        seen.update(g)
        js = [pos[i] for i in g]
        groups.append({
            "investigations": sorted(g, key=lambda i: ranking_pos[i]),
            "first_or_tied_in_every_draw": bool(all(loc["first"][:, k].all() and uni["first"][:, k].all()
                                                    for k in js)),
            "why": ("their best configurations have the same similarity on every scored dimension "
                    f"({', '.join(DIM_LABELS[d] for d in tab['scored'])}) and the same evidence and gate "
                    "factor, so no weighting separates them"),
            "same_similarity_and_factor": _same_profile(tab, js, S0),
        })

    run = {
        "scenario_id": scenario_id,
        "query": query,
        "profile": tab["profile"],
        "config_version": live["config_version"],
        "seed": seed,
        "draws": draws,
        "draws_uniform": draws,
        "concentration": CONCENTRATION,
        "tie_tolerance": TIE_TOL,
        "rng": f"numpy.random.default_rng([{seed}, 0]) local, default_rng([{seed}, 1]) uniform",
        "profile_weights": dict(tab["weights"]),
        "sampled_dims": [k for k in keys if tab["weights"][k] > 0],
        "zero_weight_dims": [k for k in keys if not tab["weights"][k] > 0],
        "scored_dims": list(tab["scored"]),
        "scenario": {k: v for k, v in tab["scenario"].items()},
        "live_top3": live_top,
        "default_check": {"profile_weights_reproduce_live_top3": again_top == live_top,
                          "numpy_rescore_equals_ranking_scores": np_equal},
        "structural_ties": groups,
        "results": results,
    }
    if with_rank:
        run["parity"] = {"rank_calls": int(sum(runs[k]["rank_calls"] for k in KINDS)),
                         "investigation_scores_compared": int(sum(runs[k]["rank_scores"].size for k in KINDS)),
                         "mismatches": int(sum(runs[k]["mismatches"] for k in KINDS)),
                         "rank_seconds": round(sum(runs[k]["rank_seconds"] for k in KINDS), 1)}
    return run


def _same_profile(tab, js, S0):
    """True when, for these investigations, the best configuration at the profile weights has the same
    similarity vector and the same factor (the reason a tie cannot depend on the weights)."""
    best = []
    for j in js:
        idx = np.where(tab["inv_index"] == j)[0]
        cfg_s = tab["factor"][idx] * (tab["sim"][idx] @ np.ones(len(tab["scored"])))  # any positive weights
        k = idx[int(np.argmax(cfg_s))]
        best.append((tuple(np.round(tab["sim"][k], 12)), round(float(tab["factor"][k]), 12)))
    return len(set(best)) == 1


SHARE_KEYS = ("first_or_tied_share_local", "top3_share_local", "first_or_tied_share_uniform",
              "top3_share_uniform", "first_alone_share_local")


def compare_seeds(a, b, kind=None):
    """Largest difference, in percentage points, between two runs' shares (same investigations).
    kind 'local' or 'uniform' keeps only that run's shares."""
    worst = (0.0, None)
    for ra, rb in zip(a["results"], b["results"]):
        if ra["investigation_id"] != rb["investigation_id"]:
            continue
        for k in SHARE_KEYS:
            if kind and not k.endswith("_" + kind) and not (kind == "local" and k == "first_alone_share_local"):
                continue
            d = abs(ra[k] - rb[k]) * 100
            if d > worst[0]:
                worst = (d, f"{ra['investigation_id']}.{k}")
        pb = {p["investigation_id"]: p for p in rb["tied_for_first_with"]}
        for p in ra["tied_for_first_with"]:
            q = pb.get(p["investigation_id"], {"share": 0.0, "share_uniform": 0.0})
            for k in ("share", "share_uniform"):
                if kind and (k == "share") != (kind == "local"):
                    continue
                d = abs(p[k] - q[k]) * 100
                if d > worst[0]:
                    worst = (d, f"{ra['investigation_id']}.tied_for_first_with.{p['investigation_id']}.{k}")
    return round(worst[0], 2), worst[1]


def add_lines(run, cfg):
    facts = {"draws_per_run": run["draws"], "draws_both_runs": run["draws"] + run["draws_uniform"],
             "top_k": cfg["selection"]["top_k"]}
    for r in run["results"]:
        if r["live_rank"] is None:
            r["display_line"], r["display_rule"] = None, None
            continue
        line, rule = display_line(r, facts)
        # Every number the line prints must be one of these values (ai/checks.py template gates).
        nums = dict(facts, group_size=1 + len(r["tied_in_every_draw_with"]),
                    shares_pct=[round(100 * r[k], 1) for k in SHARE_KEYS]
                    + [round(100 * p["share"], 1) for p in r["tied_for_first_with"]])
        chk = C.check_template(line, nums)
        if not chk["ok"]:
            raise RobustnessError(f"{run['query']!r} {r['investigation_id']}: display line fails the template "
                                  f"gates: {chk['reasons']} :: {line}")
        r["display_line"], r["display_rule"], r["display_text_origin"] = line, rule, "template"
        r["display_facts"] = nums


def build(draws=DRAWS, with_rank=True, seed_check=True, log=print):
    cfg = scorer.load_config()
    cat = scorer.load_catalog()
    runs = []
    for sid, q in QUERIES:
        t0 = time.time()
        run = build_run(sid, q, cfg, cat, SEED, draws, with_rank=with_rank)
        add_lines(run, cfg)
        if seed_check:
            other = build_run(sid, q, cfg, cat, CHECK_SEED, draws, with_rank=False)
            diff, where = compare_seeds(run, other)
            d_loc, w_loc = compare_seeds(run, other, "local")
            d_uni, w_uni = compare_seeds(run, other, "uniform")
            run["seed_check"] = {"seed": CHECK_SEED, "max_abs_diff_points": diff, "largest_at": where,
                                 "max_abs_diff_points_local": d_loc, "largest_at_local": w_loc,
                                 "max_abs_diff_points_uniform": d_uni, "largest_at_uniform": w_uni,
                                 "limit_points": MAX_SEED_DIFF_POINTS, "within_limit": diff <= MAX_SEED_DIFF_POINTS,
                                 "local_within_limit": d_loc <= MAX_SEED_DIFF_POINTS,
                                 "note": ("display lines print local shares only; the design's limit is "
                                          f"{MAX_SEED_DIFF_POINTS:g} points for every share")}
            if diff > MAX_SEED_DIFF_POINTS:
                log(f"WARNING {q!r}: seed {SEED} and {CHECK_SEED} differ by {diff} points at {where} "
                    f"(limit {MAX_SEED_DIFF_POINTS:g}); local shares differ by at most {d_loc}")
        runs.append(run)
        log(f"{q!r}: {time.time() - t0:.1f}s; top3 {run['live_top3']}; "
            + "; ".join(f"{r['investigation_id']} first/tied {100 * r['first_or_tied_share_local']:.1f}% "
                        f"(uniform {100 * r['first_or_tied_share_uniform']:.1f}%), top3 "
                        f"{100 * r['top3_share_local']:.1f}%, level always with {r['tied_in_every_draw_with']}, "
                        f"assumed {r['assumed_dims']} (scored {r['assumed_dims_scored']})"
                        for r in run["results"])
            + (f"; parity mismatches {run['parity']['mismatches']} of "
               f"{run['parity']['investigation_scores_compared']}" if with_rank else "")
            + (f"; seed 43 max diff {run['seed_check']['max_abs_diff_points']} points" if seed_check else ""))
    payload = {
        "description": ("Rank stability of the team's ranking (scoring.scorer.rank) for the four preset "
                        "queries under sampled weights, tie-aware. " + LABEL),
        "label": LABEL,
        "method": {
            "family": "multi-criteria decision analysis: sensitivity of a weighted sum to its weights (SMAA-style)",
            "local": f"Dirichlet({CONCENTRATION:g} x profile weights) over the profile's keys with weight above 0",
            "uniform": "Dirichlet(1) over the same keys: no stated preference",
            "zero_weight_dims": "a key whose profile weight is 0 stays 0",
            "rescore": ("NumPy re-score from the scorer's own similarities, gate and evidence factor; checked "
                        "against scoring.scorer.rank(weights_override=...) for every draw of the seed-42 runs"),
            "first_or_tied": f"score within {TIE_TOL:g} of the top score of the draw (unrounded scores)",
            "top3": f"fewer than {cfg['selection']['top_k']} other investigations score more (by more than {TIE_TOL:g})",
            "at_displayed_precision": "the same share with scores rounded to 0.1 as the page prints them",
            "shown_in_results": "share of draws in which rank() lists the investigation among its results "
                                "(after the scorer's near-tie and complementary-slot rules)",
            "tied_in_every_draw_with": "level (within the tolerance) in every draw of both runs: a tie, not an order",
            "assumed_dims": "copied from rank() at the profile weights; assumed_dims_scored keeps those the query scores",
            "display_rule": ("assumed_dims_scored not empty: the line says the rank uses an assumed atmosphere and "
                             "shows no stability figure; else a tie in every draw is said as a tie; else "
                             "'tied for first with <id> in y%' or 'first in x%'"),
            "not_varied": "only the weights are sampled; similarities, presets, gate, evidence factor and catalog are fixed",
            "reference": "Lahdelma and Salminen, SMAA-2, Operations Research 49(3), 2001 (method idea only)",
        },
        "runs": runs,
    }
    return payload, cfg


def block():
    return metamod.meta(BUILT_BY, config.NO_MODEL, INPUTS,
                        label=("AI-generated data file: built by code written with an AI assistant (Claude Code). "
                               "No language model ran to build it. Shares are computed by code from the team's "
                               "ranking (scoring.scorer) under sampled weights. " + LABEL),
                        params={"seed": SEED, "check_seed": CHECK_SEED, "draws": DRAWS,
                                "concentration": CONCENTRATION, "tie_tolerance": TIE_TOL,
                                "numpy": np.__version__})


def check_file(rep, path=OUT):
    """For ai/check_all.py: is data/insights/robustness.json complete and current? No rank() loop:
    the shares are rebuilt by the NumPy path only (about a second). rep is check_all's Report.
    The disclosure block and its input hashes are checked by check_all's own disclosure check."""
    import json
    sec = "robustness"
    if not path.exists():
        rep.not_built(sec, f"{path.relative_to(ROOT)}: not built yet (python3 ai/robustness.py)")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    cfg, cat = scorer.load_config(), scorer.load_catalog()
    bad = []
    runs = data.get("runs") or []
    if [r.get("query") for r in runs] != [q for _, q in QUERIES]:
        bad.append(f"runs are {[r.get('query') for r in runs]}, not the four page queries")
    for run in runs:
        q = run["query"]
        live = scorer.rank(q, config=cfg, catalog=cat)
        ranking = {r["investigation_id"]: r for r in live["ranking"]}
        if run.get("live_top3") != [r["investigation_id"] for r in live["results"]]:
            bad.append(f"{q!r}: live_top3 {run.get('live_top3')} differs from rank() now")
        if run.get("config_version") != cfg["version"]:
            bad.append(f"{q!r}: config_version {run.get('config_version')} is not {cfg['version']}")
        if (run.get("parity") or {}).get("mismatches") != 0:
            bad.append(f"{q!r}: NumPy re-score and rank() disagreed ({(run.get('parity') or {}).get('mismatches')})")
        if not all((run.get("default_check") or {}).values()):
            bad.append(f"{q!r}: profile weights did not reproduce the live ranking")
        fresh = build_run(run["scenario_id"], q, cfg, cat, run["seed"], run["draws"], with_rank=False)
        for a, b in zip(run["results"], fresh["results"]):
            if a["investigation_id"] != b["investigation_id"] or any(
                    a[k] != b[k] for k in SHARE_KEYS + ("tied_for_first_with", "tied_in_every_draw_with")):
                bad.append(f"{q!r} {a['investigation_id']}: shares differ from a fresh build")
                break
        for r in run["results"]:
            want = (ranking.get(r["investigation_id"]) or {}).get("assumed_dims")
            if r.get("assumed_dims") != want:
                bad.append(f"{q!r} {r['investigation_id']}: assumed_dims {r.get('assumed_dims')} != rank() {want}")
            if r.get("display_line") and not C.check_template(r["display_line"], r.get("display_facts"))["ok"]:
                bad.append(f"{q!r} {r['investigation_id']}: display line fails the template gates")
            if r.get("assumed_dims_scored") and "%" in (r.get("display_line") or ""):
                bad.append(f"{q!r} {r['investigation_id']}: a stability figure on an assumed atmosphere")
        s = run.get("seed_check") or {}
        if not s.get("local_within_limit"):
            bad.append(f"{q!r}: local shares of seeds {SEED} and {CHECK_SEED} differ by "
                       f"{s.get('max_abs_diff_points_local')} points (limit {MAX_SEED_DIFF_POINTS:g})")
        elif not s.get("within_limit"):
            rep.info(sec, f"{q!r}: uniform-run shares of seeds {SEED} and {CHECK_SEED} differ by "
                          f"{s['max_abs_diff_points_uniform']} points at {s['largest_at_uniform']} (limit "
                          f"{MAX_SEED_DIFF_POINTS:g}; two independent samples of {run['draws']} draws each; uniform "
                          "shares are printed on no display line)")
    for b in bad:
        rep.fail(sec, b)
    if not bad:
        ties = "; ".join(f"{run['query']}: " + ", ".join("=".join(g["investigations"]) for g in run["structural_ties"])
                         for run in runs if run["structural_ties"])
        rep.ok(sec, f"{len(runs)} runs current: live top 3 and assumed_dims equal rank(), shares rebuild, "
                    f"0 parity mismatches, display lines pass the template gates; ties in every draw: {ties}")


def _strip_timing(p):
    import copy
    q = copy.deepcopy(p)
    for r in q.get("runs", []):
        (r.get("parity") or {}).pop("rank_seconds", None)
    return q


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="build in memory and compare with the file; write nothing")
    ap.add_argument("--draws", type=int, default=DRAWS, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    payload, _cfg = build(draws=args.draws)
    # rank_seconds is a timing, not a result; keep the earlier value so a rebuild is byte-identical.
    import json
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None
    if old is not None and _strip_timing({k: v for k, v in old.items() if k != "_meta"}) == _strip_timing(payload):
        payload = {k: v for k, v in old.items() if k != "_meta"}
    if args.check:
        same = old is not None and _strip_timing({k: v for k, v in old.items() if k != "_meta"}) == _strip_timing(payload)
        print(f"robustness.json {'matches' if same else 'DIFFERS from'} a fresh build")
        return 0 if same else 1
    if args.draws != DRAWS:
        print(f"--draws {args.draws} is for testing; the file is written with {DRAWS} draws only")
        return 0
    written = metamod.write_json(OUT, payload, block())
    print(f"wrote {OUT.relative_to(ROOT)} (content_sha256 {written['content_sha256'][:12]})")
    for run in payload["runs"]:
        for r in run["results"]:
            if r.get("display_line"):
                print(f"  {run['query']!r} #{r['live_rank']} {r['investigation_id']}: {r['display_line']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
