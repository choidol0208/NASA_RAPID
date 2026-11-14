# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests of ai/model_readiness.py (design component J). No language model; nothing is written.

python3 -m unittest ai.test_model_readiness
"""
import csv
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ai import config  # noqa: E402
from ai import meta as metamod  # noqa: E402
from ai import model_readiness as mr  # noqa: E402

FORBIDDEN_KEYS = ("coef", "coefficient", "coefficients", "intercept", "curve", "grid", "prediction",
                  "predictions", "fitted", "fitted_values", "weights", "slider")


def _flags(cell):
    return {p.split(":", 1)[0] for p in (cell or "").split(";") if p.strip()}


def independent_rows(spec):
    """The label's included tests, read with the csv module and the flag rule written out again."""
    need = {spec["column"], "test_id", *spec["required"]}
    out = []
    with open(mr.TESTS, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["source_id"] != spec["source_id"] or r[spec["column"]] == "":
                continue
            w = spec.get("where", {})
            if w.get("test_end") and r["test_end"] != w["test_end"]:
                continue
            if w.get("ratio_above_0") and not float(r[spec["column"]]) > 0:
                continue
            if need & _flags(r["flags"]) or any(r[c] == "" for c in need):
                continue
            out.append(r)
    return out


def _keys(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(k)
            _keys(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _keys(v, out)
    return out


class BuiltFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = mr.load_tests()
        cls.payload = mr.build(cls.df)
        cls.rows = {r["id"]: r for r in cls.payload["rows"]}

    def test_header_lines(self):
        for p in ("model_readiness.py", "test_model_readiness.py"):
            first = (config.AI_DIR / p).read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(first, config.HEADER_COMMENT)

    def test_reads_tests_csv_as_it_is(self):
        with open(mr.TESTS, newline="", encoding="utf-8") as f:
            n = sum(1 for _ in csv.DictReader(f))
        self.assertEqual(self.payload["tests_csv_rows"], n)

    def test_every_label_has_a_row(self):
        self.assertEqual([r["id"] for r in self.payload["rows"]], [s["id"] for s in mr.LABELS])

    def test_counts_equal_an_independent_tally(self):
        for spec in mr.LABELS:
            rows = independent_rows(spec)
            r = self.rows[spec["id"]]
            self.assertEqual(r["n"], len(rows), spec["id"])
            if not spec.get("numeric_label"):
                self.assertEqual(r["classes"], dict(sorted(Counter(x[spec["column"]] for x in rows).items())),
                                 spec["id"])
                self.assertEqual(sum(r["classes"].values()), r["n"])
            self.assertEqual(r["n_label_recorded"] - r["excluded"]["tests"], r["n"], spec["id"])

    def test_flagged_cells_are_left_out(self):
        for spec in mr.LABELS:
            inc, _, _ = mr.select(self.df, spec)
            need = {spec["column"], "test_id", *spec["required"]}
            for fl in inc["flags"]:
                self.assertFalse(need & _flags(fl), spec["id"])
        self.assertIn("flags column", self.payload["flag_rule"])

    def test_flex_ratio_restriction_and_diluents(self):
        r = self.rows["flex_extinction_diameter_ratio"]
        inc, _, _ = mr.select(self.df, next(s for s in mr.LABELS if s["id"] == r["id"]))
        self.assertTrue((inc["test_end"] == "extinction").all())
        self.assertTrue((inc["extinction_to_initial_diameter_ratio"].astype(float) > 0).all())
        self.assertEqual(sum(r["diluent_counts"].values()), r["n"])
        self.assertEqual(sum(r["fuel_counts"].values()), r["n"])
        self.assertEqual(set(r["diluent_counts"]), {"n2_only", "co2_added", "he_added"})

    def test_bases_are_never_pooled(self):
        for spec in mr.LABELS:
            inc, _, _ = mr.select(self.df, spec)
            if len(inc):
                self.assertEqual(len(set(inc["o2_basis"])), 1, spec["id"])
        for rid in ("cfig_inverse_test_end", "cfig_inverse_hot_ignition"):
            self.assertEqual(self.rows[rid]["o2_basis"], "oxidizer_stream")
            self.assertIn("burner-stream", self.rows[rid]["label"])
        for rid in ("cfig_normal_test_end", "cfig_normal_hot_ignition", "flex_test_end"):
            self.assertEqual(self.rows[rid]["o2_basis"], "ambient")

    def test_group_counts_are_recomputed(self):
        for spec in mr.LABELS:
            r = self.rows[spec["id"]]
            if not spec["grouping"]:
                self.assertIsNone(r["groups"])
                continue
            rows = independent_rows(spec)
            if spec["grouping"] == "cfig":
                keys = {x["test_id"].split("-")[2][:5] for x in rows}
            else:
                keys = set()
                for x in rows:
                    co2, he = float(x["co2_pct"]), float(x["he_pct"])
                    dil = "co2" if co2 > 0 else "he" if he > 0 else "n2"
                    o2 = int(np.floor(float(x["o2_pct"]) + 0.5))
                    atm = round(np.floor(float(x["pressure_kpa"]) / 101.325 / 0.1 + 0.5) * 0.1, 1)
                    keys.add((x["fuel_material"], o2, atm, dil))
            self.assertEqual(r["groups"], len(keys), spec["id"])

    def test_no_group_is_split_across_folds(self):
        spec = next(s for s in mr.LABELS if s["id"] == "flex_extinction_diameter_ratio")
        inc, _, _ = mr.select(self.df, spec)
        groups = np.array([mr.group_key(spec, r) for _, r in inc.iterrows()], dtype=object)
        held_out = []
        for tr, te in mr.splits(groups):
            self.assertFalse(set(groups[tr]) & set(groups[te]))
            held_out += list(te)
        self.assertEqual(sorted(held_out), list(range(len(groups))))
        for r in self.payload["rows"]:
            if r["cv"]:
                self.assertEqual(r["cv"]["groups_shared_between_training_and_held_out"], 0)

    def test_verdicts_follow_the_fixed_rule(self):
        allowed = {mr.VERDICT_TOO_FEW, mr.VERDICT_BEATS, mr.VERDICT_NO_BETTER, mr.VERDICT_COUNTS_ONLY,
                   mr.VERDICT_NOT_MODELABLE}
        for spec in mr.LABELS:
            r = self.rows[spec["id"]]
            self.assertIn(r["verdict"], allowed)
            self.assertTrue(r["reason"])
            if spec["kind"] == "not_modelable":
                self.assertEqual(r["verdict"], mr.VERDICT_NOT_MODELABLE)
            elif spec["kind"] == "counts_only":
                self.assertEqual(r["verdict"], mr.VERDICT_COUNTS_ONLY)
                self.assertIsNone(r["model"])
            else:
                few = mr.too_few_reasons(r["n"], r["groups"], r["classes"])
                self.assertEqual(r["verdict"] == mr.VERDICT_TOO_FEW, bool(few), spec["id"])
                if few:
                    self.assertIsNone(r["model"])
                    self.assertIsNone(r["baseline"])
                    # second careful-reader pass: where the flag rule left tests out, the reason says how many
                    # record the label, so '0 tests' is not read as 'the table has none'
                    if r["n"] < mr.MIN_N and r["n"] != r["n_label_recorded"]:
                        self.assertIn(f"{r['n']} tests left by the flag rule, of the {r['n_label_recorded']} that "
                                      "record the label", r["reason"])
                        self.assertEqual(r["excluded"]["tests"], r["n_label_recorded"] - r["n"])
                else:
                    self.assertEqual(r["verdict"], mr.cv_verdict({"baseline": r["baseline"], "model": r["model"]}))
                    for part in (r["model"], r["baseline"]):
                        self.assertIsNotNone(part["mean"])
                        self.assertIsNotNone(part["fold_sd"])
                    self.assertIn(str(r["model"]["mean"]), r["reason"])
                    self.assertIn(str(r["baseline"]["mean"]), r["reason"])

    def test_nothing_fitted_is_shipped(self):
        keys = {k.lower() for k in _keys(self.payload, set())}
        for k in FORBIDDEN_KEYS:
            self.assertNotIn(k, keys)
        for r in self.payload["rows"]:
            if r["model"]:
                self.assertEqual(set(r["model"]) - {"balanced_accuracy"},
                                 {"name", "features", "metric", "mean", "fold_sd"})

    def test_not_recorded_is_never_zero_or_101(self):
        for rid in ("bass2_flow_event", "saffire2_spread_rate", "saffire2_burn_length"):
            r = self.rows[rid]
            self.assertIn("pressure_kpa", r["not_recorded"])
            self.assertNotIn("pressure_kpa", r["ranges"])
        for r in self.payload["rows"]:
            for col, (lo, hi) in r["ranges"].items():
                self.assertLessEqual(lo, hi)
                if col == "pressure_kpa":
                    self.assertGreater(lo, 0)

    def test_fixed_closing_lines(self):
        nc = self.payload["not_covered"]
        self.assertEqual(self.payload["fixed_line"], "None is a cabin-material flammability model.")
        self.assertEqual(nc[0], self.payload["fixed_line"])
        # second careful-reader pass: 'in the PSI experimental tables', no 'empty cell' where there is no column
        self.assertTrue(any(x.startswith("No solid-fuel test has a pressure value in the PSI experimental tables "
                                         "used here (0 of ") for x in nc))
        self.assertFalse(any("cell is empty" in x for x in nc))
        self.assertIn("No solid-fuel test in these tables has a recorded oxygen value above 22.2%.", nc)
        self.assertIn("They describe the experiments in these tables only.", self.payload["labels_and_limits"])
        self.assertTrue(any(x.startswith("No table has a partial-gravity test") for x in nc))
        solid = self.df[self.df["fuel_phase"] == "solid"]
        self.assertEqual(self.payload["not_covered_facts"]["solid_tests"], len(solid))
        self.assertEqual((solid["pressure_kpa"] != "").sum(), 0)
        self.assertEqual(pd.to_numeric(solid["o2_pct"], errors="coerce").max(), 22.2)

    def test_wording_and_sources(self):
        self.assertEqual(mr.wording_problems(self.payload), [])
        self.assertEqual(mr.source_problems(self.payload), [])
        blob = json.dumps(self.payload).lower()
        for word in ("predict", "forecast", "unsafe", " safe ", "recommend"):
            self.assertNotIn(word, blob)

    def test_two_runs_are_identical(self):
        again = mr.build(self.df)
        self.assertEqual(metamod.sha256_json(self.payload), metamod.sha256_json(again))

    def test_every_table_with_an_outcome_is_accounted_for(self):
        seen = {r["source_id"] for r in self.payload["rows"]}
        seen |= {x["source_id"] for x in self.payload["outcome_columns_not_assessed"]}
        seen |= {x["source_id"] for x in self.payload["tables_without_outcome_column"]}
        self.assertEqual(seen, set(self.df["source_id"]))


class WrittenFile(unittest.TestCase):
    def test_file_matches_a_fresh_build_and_carries_its_disclosure(self):
        if not mr.OUT.exists():
            self.skipTest("data/insights/model_readiness.json not built yet")
        data = json.loads(mr.OUT.read_text(encoding="utf-8"))
        companion = json.loads((config.INSIGHTS_DIR / metamod.COMPANION).read_text(encoding="utf-8"))
        self.assertEqual(data["_meta"], companion["model_readiness.json"])
        self.assertEqual(data["_meta"]["built_by"], "ai/model_readiness.py")
        self.assertEqual(data["_meta"]["language_model_used_at_build"], config.NO_MODEL)
        body = {k: v for k, v in data.items() if k != "_meta"}
        self.assertEqual(data["_meta"]["content_sha256"], metamod.sha256_json(body))
        self.assertEqual(metamod.sha256_json(body), metamod.sha256_json(mr.build()))
        for p, h in data["_meta"]["inputs_sha256"].items():
            self.assertEqual(metamod.sha256_file(config.ROOT / p), h, p)


class RuleOnSyntheticData(unittest.TestCase):
    """The cross-validation code paths on made-up data (never written anywhere)."""

    def _frame(self, n=200, seed=0):
        rng = np.random.default_rng(seed)
        x = rng.uniform(15, 40, n)
        p = rng.choice([50.0, 101.0, 200.0], n)
        fuel = rng.choice(["a", "b"], n)
        groups = np.array([f"g{i // 5}" for i in range(n)], dtype=object)
        return pd.DataFrame({"o2_pct": x, "pressure_kpa": p, "fuel_material": fuel}), groups, rng

    def test_regression_signal_beats_and_noise_does_not(self):
        X, g, rng = self._frame()
        y_signal = 0.02 * X["o2_pct"].values + rng.normal(0, 0.01, len(X))
        cv = mr.cv_regressor(X, y_signal, g, ("o2_pct", "pressure_kpa"), ("fuel_material",))
        self.assertEqual(mr.cv_verdict(cv), mr.VERDICT_BEATS)
        y_noise = rng.normal(0, 1, len(X))
        cv = mr.cv_regressor(X, y_noise, g, ("o2_pct", "pressure_kpa"), ("fuel_material",))
        self.assertEqual(mr.cv_verdict(cv), mr.VERDICT_NO_BETTER)
        self.assertEqual(cv["groups_shared_between_training_and_held_out"], 0)

    def test_classifier_signal_beats_and_noise_does_not(self):
        X, g, rng = self._frame()
        y = np.where(X["o2_pct"].values > 27, "yes", "no")
        cv = mr.cv_classifier(X, list(y), g, ("o2_pct", "pressure_kpa"), ("fuel_material",))
        self.assertEqual(mr.cv_verdict(cv), mr.VERDICT_BEATS)
        y = rng.choice(["yes", "no"], len(X))
        cv = mr.cv_classifier(X, list(y), g, ("o2_pct", "pressure_kpa"), ("fuel_material",))
        self.assertEqual(mr.cv_verdict(cv), mr.VERDICT_NO_BETTER)

    def test_classifier_refuses_more_than_two_classes(self):
        X, g, rng = self._frame()
        with self.assertRaises(ValueError):
            mr.cv_classifier(X, list(rng.choice(["a", "b", "c"], len(X))), g, ("o2_pct",), ())

    def test_too_few_thresholds(self):
        self.assertEqual(mr.too_few_reasons(100, 20, {"a": 20, "b": 80}), [])
        self.assertTrue(mr.too_few_reasons(99, 20, None))
        self.assertTrue(mr.too_few_reasons(150, 19, None))
        self.assertTrue(mr.too_few_reasons(150, 30, {"a": 19, "b": 131}))
        self.assertTrue(mr.too_few_reasons(150, None, None))

    def test_split_helper_asserts_disjoint_groups(self):
        g = np.array([f"g{i % 7}" for i in range(70)], dtype=object)
        for tr, te in mr.splits(g):
            self.assertFalse(set(g[tr]) & set(g[te]))

    def test_cfig_run_and_flex_group(self):
        self.assertEqual(mr.cfig_run("CFIG-N-21088A1"), "21088")
        self.assertEqual(mr.cfig_run("CFIG-I-21196F1"), "21196")
        with self.assertRaises(ValueError):
            mr.cfig_run("FLEX-1")
        row = {"test_id": "x", "fuel_material": "methanol", "o2_pct": "20.5", "pressure_kpa": "101.0184",
               "co2_pct": "0.0", "he_pct": "0.0"}
        self.assertEqual(mr.flex_group(row), "methanol|O2 21%|1.0 atm|n2_only")
        row.update(co2_pct="15.0", he_pct="10.0")
        with self.assertRaises(ValueError):
            mr.flex_diluent(row)


if __name__ == "__main__":
    unittest.main()
