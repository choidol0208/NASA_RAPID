# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Outcome-model readiness table (design component J): diagnostics only, no predictor shipped.

python3 ai/model_readiness.py            builds data/insights/model_readiness.json (no language model)
python3 ai/model_readiness.py --check    builds in memory twice, compares, writes nothing

The question it answers is the team's own fourth goal: are the NASA PSI test tables sufficient for an
outcome model, and how well could a simple one do on conditions it has not seen? For every candidate
label of a NASA table that records an outcome it reports the number of recorded tests, the outcome
classes, the grouping rule and its group count, and the recorded range of each condition. Where the
fixed rule below allows it, it runs grouped cross-validation (scikit-learn GroupKFold) of a simple
model against the base rate and reports the two fold means with their fold spread.

Nothing fitted leaves this script: no coefficient, curve, grid, fitted value or model output for any
condition is written. Only counts, ranges, the cross-validated skill against the base rate with its
spread, and a verdict in words.

Everything below that shapes the result (labels, required cells, groupings, features, thresholds,
verdict rule, seed) is fixed in this file before any number is computed, as the design asks.

Libraries: pandas, NumPy, scikit-learn (all BSD-3-Clause). Input: data/pipeline/tests.csv as the data
role's pipeline writes it.
"""
import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import sklearn  # noqa: E402
from sklearn.compose import ColumnTransformer  # noqa: E402
from sklearn.dummy import DummyClassifier, DummyRegressor  # noqa: E402
from sklearn.linear_model import LinearRegression, LogisticRegression  # noqa: E402
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, mean_absolute_error  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # noqa: E402

from ai import checks, config, resolve  # noqa: E402
from ai import meta as metamod  # noqa: E402

TESTS = config.ROOT / "data" / "pipeline" / "tests.csv"
SOURCES_JSON = config.ROOT / "pipeline" / "spec" / "sources.json"
OUT = config.INSIGHTS_DIR / "model_readiness.json"
BUILT_BY = "ai/model_readiness.py"

# ------------------------------------------------------------------ fixed before any number is seen
SEED = 20261114
N_FOLDS = 5
MIN_N = 100          # 'too few' if fewer tests than this
MIN_GROUPS = 20      # ... or fewer groups than this
MIN_CLASS = 20       # ... or a class with fewer tests than this
DECIMALS = 4

VERDICT_TOO_FEW = "too few"
VERDICT_BEATS = "simple model beats the base rate on held-out conditions (indicative)"
VERDICT_NO_BETTER = "no better than the base rate"
VERDICT_COUNTS_ONLY = "counts only: no classifier is assessed for this label"
VERDICT_NOT_MODELABLE = "not modelable: events are noted only when they happened, and an empty cell is not a no"

VERDICT_RULE = (
    f"Fixed in code before any number was computed. 'too few' if a label has fewer than {MIN_N} tests, "
    f"fewer than {MIN_GROUPS} groups, or a class with fewer than {MIN_CLASS} tests; then no cross-validation "
    f"is run. Otherwise {N_FOLDS}-fold grouped cross-validation (scikit-learn GroupKFold, shuffled groups, "
    f"seed {SEED}): the simple model 'beats the base rate on held-out conditions (indicative)' when its mean "
    "fold error is lower than the baseline's by more than the larger of the two fold standard deviations; "
    "otherwise it is 'no better than the base rate'. Errors: Brier score for a class label (lower is better), "
    "mean absolute error for a numeric label (lower is better).")

FLAG_RULE = (
    "Cells that carry a flag in the flags column of data/pipeline/tests.csv are left out. A test is not counted "
    "in a row when its label cell, its test id, or any condition cell the row needs (listed in 'required_cells') "
    "is flagged or empty; each row gives these exclusions in 'excluded'. A recorded range uses only unflagged, "
    "non-empty cells, and 'range_values_n' gives how many.")
BASIS_RULE = (
    "Rows are split by o2_basis and never pooled: 'ambient' is the oxygen of the surrounding atmosphere, "
    "'oxidizer_stream' is the oxygen of the gas issuing from the burner (CFI-G inverse flames). Burner-stream "
    "oxygen is not a habitat atmosphere and is never compared with ambient oxygen.")
COUNTS_NOTE = ("Counts are recorded tests in NASA's open PSI experimental tables, the team's computation. "
               "'Not recorded' is never zero and never 101 kPa.")
LABELS_AND_LIMITS = (
    "The team's statistical diagnostics on NASA PSI tables. They describe these droplet and gas-burner "
    "experiments only. FLEX extinction is a droplet-flame outcome, not material flammability. \"Indicative\" "
    f"means a simple model beat the base rate under {N_FOLDS}-fold grouped cross-validation, nothing more. "
    "No fitted model, coefficient or model output is shipped, and none is offered for any condition, inside "
    "or outside the recorded ranges.")
TITLE = "Can these NASA tables support an outcome model?"
FIXED_LINE = "None is a cabin-material flammability model."

DILUENT = {"n2_only": "nitrogen only (no carbon dioxide or helium added)",
           "co2_added": "carbon dioxide added", "he_added": "helium added"}

# Grouping rules, written before any number is seen.
GROUPING_CFIG = (
    "CFI-G run: the five digits after 'CFIG-N-' or 'CFIG-I-' in the test id. Burns with the same run number "
    "are treated as one chamber fill and are never split across training and held-out folds (the team's "
    "reading of the table: the recorded oxygen changes from burn to burn within a run, as in the tests named "
    "in 'grouping_example').")
GROUPING_FLEX = (
    "FLEX condition group: fuel, oxygen rounded to 1%, pressure in atmospheres (kPa / 101.325) rounded to 0.1, "
    "and diluent (nitrogen only, carbon dioxide added, helium added). Repeat tests at one condition are never "
    "split across training and held-out folds.")
GROUPING_NONE = "none: no model is assessed for this label"

FLEX_REQ = ("test_end", "fuel_material", "o2_pct", "pressure_kpa", "co2_pct", "he_pct")
CFIG_REQ = ("fuel_material", "o2_pct", "pressure_kpa")

# One spec per candidate label. kind: 'class_cv', 'regression_cv', 'counts_only', 'not_modelable'.
LABELS = (
    {
        "id": "flex_extinction_diameter_ratio",
        "label": "FLEX droplet extinction-to-initial diameter ratio (tests that ended in extinction, ratio above 0)",
        "investigation_id": "PSI-69", "source_id": "flex", "column": "extinction_to_initial_diameter_ratio",
        "kind": "regression_cv", "numeric_label": True,
        "where": {"test_end": "extinction", "ratio_above_0": True},
        "required": FLEX_REQ + ("extinction_diameter_mm", "initial_diameter_mm"),
        "ranges": ("o2_pct", "pressure_kpa", "co2_pct", "he_pct", "initial_diameter_mm"),
        "grouping": "flex", "numeric_features": ("o2_pct", "pressure_kpa", "co2_pct", "he_pct"),
        "categorical_features": ("fuel_material",),
        "design_counts_14nov": {"n": 159, "n2_only": 46, "co2_added": 78, "he_added": 35,
                                "methanol": 103, "heptane": 56},
    },
    {
        "id": "flex_test_end",
        "label": "FLEX droplet test end",
        "investigation_id": "PSI-69", "source_id": "flex", "column": "test_end",
        "kind": "counts_only", "required": FLEX_REQ,
        "ranges": ("o2_pct", "pressure_kpa", "co2_pct", "he_pct", "initial_diameter_mm"),
        "grouping": "flex",
        "design_counts_14nov": {"extinction": 186, "disruption": 61, "completion": 27},
    },
    {
        "id": "cfig_normal_test_end",
        "label": "CFI-G normal flame test end",
        "investigation_id": "PSI-159", "source_id": "cfig_normal", "column": "test_end",
        "kind": "class_cv", "required": CFIG_REQ, "ranges": ("o2_pct", "pressure_kpa"), "grouping": "cfig",
        "numeric_features": ("o2_pct", "pressure_kpa"), "categorical_features": ("fuel_material",),
        "class_wording": {"self-extinction": "self-extinguished within the test window",
                          "flow termination": "flow termination recorded as the test end (no self-extinction "
                                              "recorded within the test window)"},
        "design_counts_14nov": {"self-extinction": 102, "flow termination": 31},
    },
    {
        "id": "cfig_inverse_test_end",
        "label": "CFI-G inverse flame test end (burner-stream oxygen)",
        "investigation_id": "PSI-159", "source_id": "cfig_inverse", "column": "test_end",
        "kind": "class_cv", "required": CFIG_REQ, "ranges": ("o2_pct", "pressure_kpa"), "grouping": "cfig",
        "numeric_features": ("o2_pct", "pressure_kpa"), "categorical_features": ("fuel_material",),
        "class_wording": {"self-extinction": "self-extinguished within the test window",
                          "flow termination": "flow termination recorded as the test end (no self-extinction "
                                              "recorded within the test window)"},
        "design_counts_14nov": {"self-extinction": 81, "flow termination": 58},
    },
    {
        "id": "cfig_normal_hot_ignition",
        "label": "CFI-G normal flame hot ignition",
        "investigation_id": "PSI-159", "source_id": "cfig_normal", "column": "hot_ignition",
        "kind": "class_cv", "required": CFIG_REQ, "ranges": ("o2_pct", "pressure_kpa"), "grouping": "cfig",
        "numeric_features": ("o2_pct", "pressure_kpa"), "categorical_features": ("fuel_material",),
        "design_counts_14nov": {"yes": 132, "no": 47},
    },
    {
        "id": "cfig_inverse_hot_ignition",
        "label": "CFI-G inverse flame hot ignition (burner-stream oxygen)",
        "investigation_id": "PSI-159", "source_id": "cfig_inverse", "column": "hot_ignition",
        "kind": "class_cv", "required": CFIG_REQ, "ranges": ("o2_pct", "pressure_kpa"), "grouping": "cfig",
        "numeric_features": ("o2_pct", "pressure_kpa"), "categorical_features": ("fuel_material",),
        "design_counts_14nov": {"yes": 131, "no": 15, "flash": 8},
    },
    {
        "id": "bass2_flow_event",
        "label": "BASS-II flow event",
        "investigation_id": "PSI-25", "source_id": "bass2", "column": "flow_event",
        "kind": "not_modelable", "required": ("o2_pct",),
        "ranges": ("o2_pct", "flow_cms"), "grouping": None,
    },
    {
        "id": "saffire2_spread_rate",
        "label": "Saffire-II flame spread rate",
        "investigation_id": "PSI-99", "source_id": "saffire2", "column": "spread_rate_mm_s",
        "kind": "regression_cv", "numeric_label": True, "required": ("o2_pct",),
        "ranges": ("o2_pct", "flow_cms"), "grouping": None,
    },
    {
        "id": "saffire2_burn_length",
        "label": "Saffire-II burn length",
        "investigation_id": "PSI-99", "source_id": "saffire2", "column": "burn_length_cm",
        "kind": "regression_cv", "numeric_label": True, "required": ("o2_pct",),
        "ranges": ("o2_pct", "flow_cms"), "grouping": None,
    },
)


# ------------------------------------------------------------------ reading tests.csv
def load_tests(path=TESTS):
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def flagged_columns(flags_cell):
    """'var:reason;var:reason' -> {var: [reason, ...]}."""
    out = {}
    for part in (flags_cell or "").split(";"):
        part = part.strip()
        if not part:
            continue
        var, _, reason = part.partition(":")
        out.setdefault(var, []).append(reason)
    return out


def _num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _r(x):
    return None if x is None else round(float(x), DECIMALS)


def cfig_run(test_id):
    tid = str(test_id)
    for prefix in ("CFIG-N-", "CFIG-I-"):
        if tid.startswith(prefix) and len(tid) >= len(prefix) + 5 and tid[len(prefix):len(prefix) + 5].isdigit():
            return tid[len(prefix):len(prefix) + 5]
    raise ValueError(f"{tid!r} is not a CFI-G test id with a five-digit run number")


def round_half_up(x, step):
    return math.floor(x / step + 0.5) * step


def flex_diluent(row):
    co2, he = _num(row["co2_pct"]), _num(row["he_pct"])
    if co2 and he:
        raise ValueError(f"{row['test_id']}: both carbon dioxide and helium added; no diluent class for it")
    return "co2_added" if co2 else "he_added" if he else "n2_only"


def flex_group(row):
    o2 = int(round_half_up(_num(row["o2_pct"]), 1))
    atm = round(round_half_up(_num(row["pressure_kpa"]) / 101.325, 0.1), 1)
    return f"{row['fuel_material']}|O2 {o2}%|{atm:.1f} atm|{flex_diluent(row)}"


def group_key(spec, row):
    if spec["grouping"] == "cfig":
        return cfig_run(row["test_id"])
    if spec["grouping"] == "flex":
        return flex_group(row)
    return None


def select(df, spec):
    """Rows of the label after the label's own restriction, the flag rule and the required cells.
    Returns (included DataFrame, n_label_recorded, excluded{})."""
    t = df[df["source_id"] == spec["source_id"]]
    t = t[t[spec["column"]] != ""]
    where = spec.get("where", {})
    if "test_end" in where:
        t = t[t["test_end"] == where["test_end"]]
    if where.get("ratio_above_0"):
        t = t[t[spec["column"]].map(lambda v: (_num(v) or 0) > 0)]
    n_recorded = len(t)
    need = (spec["column"], "test_id") + tuple(c for c in spec["required"] if c != spec["column"])
    keep, flagged, missing, rows_flagged, rows_missing = [], Counter(), Counter(), 0, 0
    for idx, row in t.iterrows():
        fl = flagged_columns(row["flags"])
        f_hit = [c for c in need if c in fl]
        m_hit = [c for c in need if c not in fl and row[c] == ""]
        for c in f_hit:
            flagged[c] += 1
        for c in m_hit:
            missing[c] += 1
        rows_flagged += bool(f_hit)
        rows_missing += bool(m_hit) and not f_hit
        if not f_hit and not m_hit:
            keep.append(idx)
    inc = t.loc[keep]
    excluded = {"tests": n_recorded - len(inc), "tests_with_a_flagged_cell": rows_flagged,
                "tests_with_an_empty_required_cell_only": rows_missing,
                "flagged_cells_by_column": dict(sorted(flagged.items())),
                "empty_cells_by_column": dict(sorted(missing.items()))}
    return inc, n_recorded, excluded


def ranges_of(df_inc, spec, table):
    """Recorded range of each condition over the included tests (unflagged, non-empty cells only).
    'not_recorded' lists the conditions with no value in any test of the whole table (never 0, never 101 kPa)."""
    ranges, n_vals, not_recorded = {}, {}, []
    for col in tuple(spec["ranges"]) + (() if "pressure_kpa" in spec["ranges"] else ("pressure_kpa",)):
        if (table[col] == "").all():
            not_recorded.append(col)
            continue
        if col not in spec["ranges"]:
            continue
        vals = [_num(v) for v, fl in zip(df_inc[col], df_inc["flags"])
                if v != "" and col not in flagged_columns(fl)]
        vals = [v for v in vals if v is not None]
        if vals:
            ranges[col] = [_r(min(vals)), _r(max(vals))]
            n_vals[col] = len(vals)
    return ranges, n_vals, not_recorded


# ------------------------------------------------------------------ second counting path (csv module)
def tally_csv(spec, path=TESTS):
    """Class counts of the label straight from tests.csv with the csv module, before the flag rule; and
    after it, with the same rule written again in plain Python. Used to assert the pandas counts."""
    before, after = Counter(), Counter()
    need = {spec["column"], "test_id", *spec["required"]}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["source_id"] != spec["source_id"] or not r[spec["column"]]:
                continue
            w = spec.get("where", {})
            if "test_end" in w and r["test_end"] != w["test_end"]:
                continue
            if w.get("ratio_above_0"):
                try:
                    if not float(r[spec["column"]]) > 0:
                        continue
                except ValueError:
                    continue
            key = "n" if spec.get("numeric_label") else r[spec["column"]]
            before[key] += 1
            flagged = {p.split(":", 1)[0] for p in r["flags"].split(";") if p.strip()}
            if need & flagged or any(not r[c] for c in need):
                continue
            after[key] += 1
    return dict(before), dict(after)


# ------------------------------------------------------------------ grouped cross-validation
def _preprocessor(numeric, categorical):
    parts = []
    if numeric:
        parts.append(("num", StandardScaler(), list(numeric)))
    if categorical:
        parts.append(("cat", OneHotEncoder(handle_unknown="ignore"), list(categorical)))
    return ColumnTransformer(parts)


def splits(groups, n_folds=N_FOLDS, seed=SEED):
    """GroupKFold splits; asserts that no group is in both the training and the held-out part."""
    gkf = GroupKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    out = []
    dummy = np.zeros(len(groups))
    for tr, te in gkf.split(dummy, dummy, groups):
        shared = set(groups[tr]) & set(groups[te])
        assert not shared, f"group split across training and held-out folds: {sorted(shared)[:3]}"
        out.append((tr, te))
    return out


def _mean_sd(xs):
    a = np.asarray(xs, dtype=float)
    return _r(a.mean()), _r(a.std(ddof=1)) if len(a) > 1 else None


def cv_classifier(X, y, groups, numeric, categorical, n_folds=N_FOLDS, seed=SEED):
    """Logistic regression against the base rate (training-fold class shares) on a binary label.
    Returns fold means and standard deviations only; nothing fitted is returned."""
    classes = sorted(set(y))
    if len(classes) != 2:
        raise ValueError("grouped cross-validation is run on two-class labels only")
    pos = classes[1]
    yb = (np.asarray(y) == pos).astype(int)
    m_brier, b_brier, m_bacc, b_bacc, n_shared = [], [], [], [], 0
    for tr, te in splits(groups, n_folds, seed):
        model = Pipeline([("prep", _preprocessor(numeric, categorical)),
                          ("clf", LogisticRegression(max_iter=1000))])
        base = DummyClassifier(strategy="prior")
        for est, brier, bacc in ((model, m_brier, m_bacc), (base, b_brier, b_bacc)):
            est.fit(X.iloc[tr], yb[tr])
            proba = est.predict_proba(X.iloc[te])
            cls = list(est.classes_)
            p = proba[:, cls.index(1)] if 1 in cls else np.zeros(len(te))
            brier.append(brier_score_loss(yb[te], p))
            bacc.append(balanced_accuracy_score(yb[te], (p >= 0.5).astype(int)))
        n_shared += len(set(groups[tr]) & set(groups[te]))
    mm, ms = _mean_sd(m_brier)
    bm, bs = _mean_sd(b_brier)
    mba, mbs = _mean_sd(m_bacc)
    bba, bbs = _mean_sd(b_bacc)
    return {
        "baseline": {"name": "base rate (training-fold class shares; scikit-learn DummyClassifier 'prior')",
                     "metric": "Brier score", "mean": bm, "fold_sd": bs,
                     "balanced_accuracy": {"mean": bba, "fold_sd": bbs}},
        "model": {"name": "logistic regression (scikit-learn, default L2 penalty, standardised numbers, "
                          "one-hot fuel)", "features": list(numeric) + list(categorical),
                  "metric": "Brier score", "mean": mm, "fold_sd": ms,
                  "balanced_accuracy": {"mean": mba, "fold_sd": mbs}},
        "brier_positive_class": pos, "groups_shared_between_training_and_held_out": n_shared,
    }


def cv_regressor(X, y, groups, numeric, categorical, n_folds=N_FOLDS, seed=SEED):
    """Linear regression against the training-fold mean. Returns fold means and standard deviations only."""
    y = np.asarray(y, dtype=float)
    m_mae, b_mae, n_shared = [], [], 0
    for tr, te in splits(groups, n_folds, seed):
        model = Pipeline([("prep", _preprocessor(numeric, categorical)), ("reg", LinearRegression())])
        base = DummyRegressor(strategy="mean")
        for est, mae in ((model, m_mae), (base, b_mae)):
            est.fit(X.iloc[tr], y[tr])
            mae.append(mean_absolute_error(y[te], est.predict(X.iloc[te])))
        n_shared += len(set(groups[tr]) & set(groups[te]))
    mm, ms = _mean_sd(m_mae)
    bm, bs = _mean_sd(b_mae)
    return {
        "baseline": {"name": "training-fold mean (scikit-learn DummyRegressor 'mean')",
                     "metric": "mean absolute error", "mean": bm, "fold_sd": bs},
        "model": {"name": "linear regression (scikit-learn, standardised numbers, one-hot fuel)",
                  "features": list(numeric) + list(categorical),
                  "metric": "mean absolute error", "mean": mm, "fold_sd": ms},
        "groups_shared_between_training_and_held_out": n_shared,
    }


def cv_verdict(cv):
    """The fixed rule: lower error by more than the larger fold standard deviation."""
    b, m = cv["baseline"], cv["model"]
    margin = max(b["fold_sd"] or 0.0, m["fold_sd"] or 0.0)
    return VERDICT_BEATS if (b["mean"] - m["mean"]) > margin else VERDICT_NO_BETTER


def too_few_reasons(n, groups, classes):
    out = []
    if n < MIN_N:
        out.append(f"{n} tests (under {MIN_N})")
    if groups is None:
        out.append("no grouping rule set for this label")
    elif groups < MIN_GROUPS:
        out.append(f"{groups} groups (under {MIN_GROUPS})")
    for c, k in sorted((classes or {}).items()):
        if k < MIN_CLASS:
            out.append(f"class '{c}' has {k} tests (under {MIN_CLASS})")
    return out


# ------------------------------------------------------------------ one row
def build_row(df, spec, n_folds=N_FOLDS, seed=SEED):
    inc, n_recorded, excluded = select(df, spec)
    bases = sorted(set(inc["o2_basis"])) if len(inc) else sorted(
        set(df[df["source_id"] == spec["source_id"]]["o2_basis"]))
    assert len(bases) == 1, f"{spec['id']}: rows of more than one o2_basis would be pooled: {bases}"
    numeric_label = spec.get("numeric_label", False)
    classes = None if numeric_label else dict(sorted(Counter(inc[spec["column"]]).items()))

    # second path: counts straight from tests.csv
    before, after = tally_csv(spec)
    got_before = ({"n": n_recorded} if numeric_label
                  else dict(Counter(df[(df["source_id"] == spec["source_id"]) & (df[spec["column"]] != "")]
                                    [spec["column"]])) if not spec.get("where") else None)
    if got_before is not None and not numeric_label:
        assert got_before == before, f"{spec['id']}: class counts differ from the csv tally {before}"
    if numeric_label:
        assert before.get("n", 0) == n_recorded, f"{spec['id']}: {n_recorded} != csv tally {before}"
        assert after.get("n", 0) == len(inc), f"{spec['id']}: {len(inc)} != csv tally {after}"
    else:
        assert after == classes, f"{spec['id']}: class counts {classes} differ from the csv tally {after}"

    groups_arr = None
    groups = None
    group_sizes = None
    if spec["grouping"]:
        groups_arr = np.array([group_key(spec, r) for _, r in inc.iterrows()], dtype=object)
        gc = Counter(groups_arr)
        groups = len(gc)
        group_sizes = {"min": min(gc.values()), "max": max(gc.values())} if gc else None
    ranges, n_vals, not_recorded = ranges_of(inc, spec, df[df["source_id"] == spec["source_id"]])

    row = {
        "id": spec["id"],
        "label": spec["label"],
        "investigation_id": spec["investigation_id"],
        "source_id": spec["source_id"],
        "column": spec["column"],
        "o2_basis": bases[0],
        "n_label_recorded": n_recorded,
        "n": len(inc),
        "excluded": excluded,
        "required_cells": [spec["column"], "test_id"] + [c for c in spec["required"] if c != spec["column"]],
        "classes": classes,
        "classes_label_recorded": None if numeric_label else dict(sorted(before.items())),
        "class_wording": spec.get("class_wording"),
        "label_range": None,
        "diluent_counts": None,
        "fuel_counts": dict(sorted(Counter(
            f for f, fl in zip(inc["fuel_material"], inc["flags"])
            if f and "fuel_material" not in flagged_columns(fl)).items())),
        "fuel_cells_flagged_or_empty": int(sum(
            (not f) or "fuel_material" in flagged_columns(fl) for f, fl in zip(inc["fuel_material"], inc["flags"]))),
        "grouping_rule": {"cfig": GROUPING_CFIG, "flex": GROUPING_FLEX}.get(spec["grouping"], GROUPING_NONE),
        "groups": groups,
        "group_sizes": group_sizes,
        "ranges": ranges,
        "range_values_n": n_vals,
        "not_recorded": not_recorded,
        "baseline": None,
        "model": None,
        "cv": None,
        "verdict": None,
        "reason": None,
        "sources": [spec["investigation_id"], f"pipeline/spec/sources.json#{spec['source_id']}"],
    }
    if numeric_label:
        vals = [float(v) for v in inc[spec["column"]]]
        row["label_range"] = [_r(min(vals)), _r(max(vals))] if vals else None
    if spec["source_id"] == "flex":
        row["diluent_counts"] = dict(sorted(Counter(flex_diluent(r) for _, r in inc.iterrows()).items()))
        row["diluent_wording"] = DILUENT
    if spec["grouping"] == "cfig":
        first = sorted(inc["test_id"])[0] if len(inc) else None
        if first:
            run = cfig_run(first)
            ex = inc[inc["test_id"].map(cfig_run) == run].sort_values("test_id").head(3)
            row["grouping_example"] = [{"test_id": t, "o2_pct": _r(_num(o)), "o2_basis": bases[0]}
                                       for t, o in zip(ex["test_id"], ex["o2_pct"])]

    if spec["kind"] == "not_modelable":
        row["verdict"] = VERDICT_NOT_MODELABLE
        row["reason"] = (f"The BASS-II table writes a flow event only for the {n_recorded} tests in which one was "
                         "noted; the other tests have an empty cell, which does not say that no event happened. "
                         "So there is no recorded 'no' class to learn from.")
        return row
    if spec["kind"] == "counts_only":
        row["verdict"] = VERDICT_COUNTS_ONLY
        row["reason"] = ("Shown as counts, as the design fixed; the test-end classes are listed with the "
                         "condition ranges and the group count, and no classifier is fitted.")
        return row

    few = too_few_reasons(len(inc), groups, classes)
    if few:
        row["verdict"] = VERDICT_TOO_FEW
        row["reason"] = "Under the fixed rule: " + "; ".join(few) + ". No cross-validation is run."
        return row

    X = inc[list(spec["numeric_features"]) + list(spec["categorical_features"])].copy()
    for c in spec["numeric_features"]:
        X[c] = X[c].astype(float)
    if spec["kind"] == "class_cv":
        cv = cv_classifier(X, list(inc[spec["column"]]), groups_arr, spec["numeric_features"],
                           spec["categorical_features"], n_folds, seed)
    else:
        cv = cv_regressor(X, inc[spec["column"]].astype(float).values, groups_arr, spec["numeric_features"],
                          spec["categorical_features"], n_folds, seed)
    assert cv["groups_shared_between_training_and_held_out"] == 0
    row["baseline"], row["model"] = cv["baseline"], cv["model"]
    row["cv"] = {"splitter": "scikit-learn GroupKFold", "folds": n_folds, "shuffle": True, "seed": seed,
                 "groups_shared_between_training_and_held_out": 0}
    if "brier_positive_class" in cv:
        row["cv"]["brier_positive_class"] = cv["brier_positive_class"]
    row["verdict"] = cv_verdict(cv)
    b, m = cv["baseline"], cv["model"]
    margin = _r(max(b["fold_sd"] or 0.0, m["fold_sd"] or 0.0))
    row["reason"] = (f"{n_folds}-fold grouped cross-validation over {groups} groups: {m['metric']} of the simple "
                     f"model {m['mean']} (fold standard deviation {m['fold_sd']}) against {b['mean']} (fold "
                     f"standard deviation {b['fold_sd']}) for the baseline; the rule asks for a lower error by "
                     f"more than {margin}. Held-out groups are conditions the model did not see in training, "
                     "inside the recorded ranges of this table only.")
    return row


# ------------------------------------------------------------------ the rest of the file
def outcome_columns_not_assessed(df, used):
    """Every outcome column (kind 'outcome' or derived, from pipeline/spec/variables.json) with a recorded value
    in a table, that is not one of the labels above: listed with its count only."""
    spec = json.loads((config.ROOT / "pipeline" / "spec" / "variables.json").read_text(encoding="utf-8"))
    cols = [k for k, v in spec["variables"].items() if v.get("kind") == "outcome"] + list(spec.get("derived", {}))
    out = []
    for sid, g in df.groupby("source_id", sort=True):
        for c in cols:
            if c not in g.columns or (sid, c) in used:
                continue
            nonempty = g[g[c] != ""]
            if not len(nonempty):
                continue
            unflagged = sum(c not in flagged_columns(f) for f in nonempty["flags"])
            out.append({"source_id": sid, "investigation_id": nonempty["investigation_id"].iloc[0], "column": c,
                        "tests_with_a_value": len(nonempty), "unflagged_values": unflagged,
                        "o2_basis": sorted(set(nonempty["o2_basis"]) - {""}) or ["not recorded"],
                        "note": "listed with its count only; not assessed as a label here"})
    return out


def tables_without_outcome(df):
    spec = json.loads((config.ROOT / "pipeline" / "spec" / "variables.json").read_text(encoding="utf-8"))
    cols = [k for k, v in spec["variables"].items() if v.get("kind") == "outcome"] + list(spec.get("derived", {}))
    out = []
    for sid, g in df.groupby("source_id", sort=True):
        if not any((g[c] != "").any() for c in cols if c in g.columns):
            out.append({"source_id": sid, "investigation_id": g["investigation_id"].iloc[0], "tests": len(g),
                        "note": "no outcome column has a recorded value in tests.csv for this table"})
    return out


def not_covered(df):
    solid = df[df["fuel_phase"] == "solid"]
    n_solid = len(solid)
    solid_with_p = int((solid["pressure_kpa"] != "").sum())
    solid_o2 = [v for v in (_num(x) for x in solid["o2_pct"]) if v is not None]
    max_solid_o2 = max(solid_o2)
    levels = sorted(set(df["gravity_level"]) - {""})
    partial = [lv for lv in levels if lv not in ("microgravity", "1g")]
    # The three fixed lines of the design must stay true; the build stops if the data say otherwise.
    assert solid_with_p == 0, f"{solid_with_p} solid-fuel tests now have a pressure; the fixed line is wrong"
    assert max_solid_o2 == 22.2, f"highest solid-fuel oxygen is now {max_solid_o2}; the fixed line is wrong"
    assert not partial, f"partial-gravity rows now exist: {partial}; the fixed line is wrong"
    level_words = " and ".join({"microgravity": "microgravity", "1g": "1 g"}[lv] for lv in levels)
    return [
        FIXED_LINE,
        f"No solid-sample table has a recorded pressure: in all {n_solid} solid-fuel tests the pressure cell is "
        "empty (not recorded, which is not 101 kPa).",
        "No solid-sample test has recorded oxygen above 22.2%.",
        f"No table has a partial-gravity test: every test row in tests.csv is recorded at {level_words}. "
        "Microgravity and 1 g results are not bounds for lunar or Martian gravity.",
    ], {"solid_tests": n_solid, "solid_tests_with_pressure": solid_with_p, "highest_solid_o2_pct": max_solid_o2,
        "gravity_levels": levels}


def build(df=None, n_folds=N_FOLDS, seed=SEED):
    df = load_tests() if df is None else df
    rows = [build_row(df, s, n_folds, seed) for s in LABELS]
    nc, nc_facts = not_covered(df)
    used = {(s["source_id"], s["column"]) for s in LABELS}
    payload = {
        "title": TITLE,
        "fixed_line": FIXED_LINE,
        "labels_and_limits": LABELS_AND_LIMITS,
        "counts_note": COUNTS_NOTE,
        "flag_rule": FLAG_RULE,
        "basis_rule": BASIS_RULE,
        "verdict_rule": VERDICT_RULE,
        "thresholds": {"min_tests": MIN_N, "min_groups": MIN_GROUPS, "min_class": MIN_CLASS, "folds": N_FOLDS,
                       "seed": SEED},
        "tests_csv_rows": len(df),
        "rows": rows,
        "outcome_columns_not_assessed": outcome_columns_not_assessed(df, used),
        "tables_without_outcome_column": tables_without_outcome(df),
        "not_covered": nc,
        "not_covered_facts": nc_facts,
        "shipped": "counts, recorded ranges, grouped cross-validation errors with their fold spread, and verdicts "
                   "in words; no fitted model, coefficient, curve, grid or model output",
    }
    return payload


# ------------------------------------------------------------------ wording and source checks
def _strings(obj, out, path=""):
    if isinstance(obj, str):
        out.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _strings(v, out, f"{path}.{k}" if path else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _strings(v, out, f"{path}[{i}]")
    return out


# Strings that are identifiers or values copied from tests.csv, not team prose.
_NOT_PROSE = ("sources", "column", "id", "source_id", "investigation_id", "required_cells", "features",
              "test_id", "o2_basis", "not_recorded", "gravity_levels")


def wording_problems(payload):
    """Team prose in the file must pass the template gates of ai/checks.py: banned wording (prediction,
    coverage, 'never tested', flammability verdicts, scores and ranks), advice words and the linter."""
    probs = []
    for path, s in _strings(payload, []):
        last = path.split(".")[-1].split("[")[0]
        if last in _NOT_PROSE or " " not in s:
            continue
        for gate in (checks.gate_banned, checks.gate_policy, checks.gate_lint):
            ok, why = gate(s)
            if not ok:
                probs.append(f"{path}: {why}: {s[:90]!r}")
    return probs


def source_problems(payload):
    srcs = {s for r in payload["rows"] for s in r["sources"]}
    return sorted(s for s in srcs if not resolve.check(s))


# ------------------------------------------------------------------ output
def disclosure_block():
    return metamod.meta(
        BUILT_BY, config.NO_MODEL, inputs=[TESTS, SOURCES_JSON,
                                           config.ROOT / "pipeline" / "spec" / "variables.json"],
        label=("AI-generated data file: built by code written with an AI assistant (Claude Code). No language "
               "model ran to build it. Counts, recorded ranges and grouped cross-validation errors are computed "
               "by code from NASA PSI tables (data/pipeline/tests.csv); the verdicts are fixed rules applied by "
               "code. Team output, not a NASA conclusion. No fitted model or model output is in this file."),
        libraries={"pandas": pd.__version__, "numpy": np.__version__, "scikit-learn": sklearn.__version__},
    )


def recorded_counts(spec, df=None):
    """Counts of a numeric label before the flag rule (for the printed comparison with the design only)."""
    df = load_tests() if df is None else df
    t = df[(df["source_id"] == spec["source_id"]) & (df[spec["column"]] != "")]
    if spec.get("where", {}).get("test_end"):
        t = t[t["test_end"] == spec["where"]["test_end"]]
    if spec.get("where", {}).get("ratio_above_0"):
        t = t[t[spec["column"]].map(lambda v: (_num(v) or 0) > 0)]
    out = {"n": len(t)}
    if spec["source_id"] == "flex":
        out.update(Counter(flex_diluent(r) for _, r in t.iterrows()))
    out.update(Counter(t["fuel_material"]))
    return out


def print_table(payload):
    print(f"{payload['title']}  (tests.csv rows: {payload['tests_csv_rows']})")
    for r in payload["rows"]:
        extra = ""
        if r["model"]:
            extra = (f" | {r['model']['metric']}: model {r['model']['mean']} (sd {r['model']['fold_sd']}) vs "
                     f"baseline {r['baseline']['mean']} (sd {r['baseline']['fold_sd']})")
        print(f"- {r['id']} [{r['o2_basis']}] n={r['n']} of {r['n_label_recorded']} "
              f"(excluded {r['excluded']['tests']}) classes={r['classes']} groups={r['groups']} "
              f"ranges={r['ranges']}{extra} -> {r['verdict']}")
        spec = next(s for s in LABELS if s["id"] == r["id"])
        d = spec.get("design_counts_14nov")
        if d:
            now = recorded_counts(spec) if spec.get("numeric_label") else r["classes_label_recorded"]
            same = all(now.get(k) == v for k, v in d.items())
            print(f"    design counts (before the flag rule; written before the 14 Nov audit; printed, not "
                  f"asserted): {'equal' if same else 'different'}: design {d}, tests.csv now {now}")
        if r["grouping_rule"] != GROUPING_NONE:
            print(f"    grouping: {r['groups']} groups (sizes {r['group_sizes']})")
    for line in payload["not_covered"]:
        print(f"  * {line}")


def check(rep):
    """Hook for ai/check_all.py run(): rep.ok / rep.fail / rep.not_built on a check_all Report.
    The written file must equal a fresh build (same seed), carry its disclosure, and pass the wording and
    source checks. One line in check_all.run(): `from ai import model_readiness; model_readiness.check(rep)`."""
    sec = "model_readiness"
    if not OUT.exists():
        rep.not_built(sec, "data/insights/model_readiness.json not built yet (python3 ai/model_readiness.py)")
        return
    try:
        fresh = build()
    except (AssertionError, ValueError) as e:
        rep.fail(sec, f"build stops on the current data: {e}")
        return
    data = json.loads(OUT.read_text(encoding="utf-8"))
    body = {k: v for k, v in data.items() if k != "_meta"}
    before = len(rep.failures())
    if metamod.sha256_json(body) != metamod.sha256_json(fresh):
        rep.fail(sec, "model_readiness.json differs from a fresh build; rerun python3 ai/model_readiness.py")
    for p in wording_problems(body):
        rep.fail(sec, f"wording: {p}")
    for s in source_problems(body):
        rep.fail(sec, f"source does not resolve: {s}")
    keys = set()
    _keys_of(body, keys)
    bad = keys & {"coef", "coefficient", "coefficients", "intercept", "curve", "grid", "prediction", "fitted"}
    if bad:
        rep.fail(sec, f"fitted output in the file: {sorted(bad)}")
    if len(rep.failures()) == before:
        cv = [r["id"] for r in body["rows"] if r["model"]]
        rep.ok(sec, f"{len(body['rows'])} rows equal a fresh build; cross-validated: {', '.join(cv) or 'none'}; "
                    "verdicts: " + "; ".join(f"{r['id']} {r['verdict']}" for r in body["rows"]))


def _keys_of(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(k.lower())
            _keys_of(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _keys_of(v, out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="build twice in memory, compare, write nothing")
    args = ap.parse_args(argv)
    a = build()
    b = build()
    if metamod.sha256_json(a) != metamod.sha256_json(b):
        print("FAIL: two builds with the same seed differ")
        return 1
    probs = wording_problems(a) + [f"source does not resolve: {s}" for s in source_problems(a)]
    print_table(a)
    if probs:
        for p in probs:
            print("FAIL:", p)
        return 1
    if args.check:
        print("OK: two builds identical; wording and sources pass; nothing written")
        return 0
    metamod.write_json(OUT, a, disclosure_block())
    print(f"wrote {OUT.relative_to(config.ROOT)} (two builds identical; wording and sources pass)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
