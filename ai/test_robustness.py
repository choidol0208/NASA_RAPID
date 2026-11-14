# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for ai/robustness.py (component K). Run: python3 -m unittest -v ai.test_robustness

No share is hard-coded. The checks compare the NumPy re-score with scoring.scorer.rank (unchanged),
recompute ties from the scorer's own similarities, and rebuild the shares of the committed file."""
import json
import unittest

import numpy as np

from ai import checks as C
from ai import config, meta as metamod, robustness as R
from scoring import scorer

ROOT = config.ROOT
CONTRACT_RUN = ("query", "config_version", "seed", "draws", "concentration", "tie_tolerance", "results")
CONTRACT_RESULT = ("investigation_id", "first_or_tied_share_local", "top3_share_local",
                   "first_or_tied_share_uniform", "tied_for_first_with", "assumed_dims")


def setUpModule():
    global CFG, CAT, LIVE
    CFG = scorer.load_config()
    CAT = scorer.load_catalog()
    LIVE = {q: scorer.rank(q, config=CFG, catalog=CAT) for _, q in R.QUERIES}


class HeaderTest(unittest.TestCase):
    def test_header_comment(self):
        for f in ("robustness.py", "test_robustness.py"):
            first = (config.AI_DIR / f).read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(first, config.HEADER_COMMENT)

    def test_queries_are_the_page_strings(self):
        from ai import check_all
        self.assertEqual(tuple(R.QUERIES), tuple(check_all.QUERIES))


class WeightsTest(unittest.TestCase):
    def test_full_dict_zero_weights_stay_zero(self):
        w = CFG["profiles"]["prevention"]["weights"]
        for kind in R.KINDS:
            keys, W = R.sample_weights(w, 500, R.SEED, kind)
            self.assertEqual(keys, list(w))
            np.testing.assert_allclose(W.sum(axis=1), 1.0, atol=1e-12)
            for i, k in enumerate(keys):
                if w[k] == 0:
                    self.assertTrue(np.all(W[:, i] == 0), k)
                else:
                    self.assertTrue(np.all(W[:, i] > 0), k)

    def test_seeded_and_kinds_differ(self):
        w = CFG["profiles"]["prevention"]["weights"]
        a = R.sample_weights(w, 50, R.SEED, "local")[1]
        b = R.sample_weights(w, 50, R.SEED, "local")[1]
        c = R.sample_weights(w, 50, R.CHECK_SEED, "local")[1]
        d = R.sample_weights(w, 50, R.SEED, "uniform")[1]
        np.testing.assert_array_equal(a, b)
        self.assertFalse(np.array_equal(a, c))
        self.assertFalse(np.array_equal(a, d))

    def test_local_draws_centre_on_the_profile(self):
        w = CFG["profiles"]["prevention"]["weights"]
        keys, W = R.sample_weights(w, 4000, R.SEED, "local")
        np.testing.assert_allclose(W.mean(axis=0), [w[k] for k in keys], atol=0.01)


class DefaultWeightsTest(unittest.TestCase):
    def test_profile_weights_reproduce_the_live_ranking(self):
        for _, q in R.QUERIES:
            tab = R.score_table(q, CFG, CAT)
            keys = list(tab["weights"])
            S0 = R.inv_scores(tab, keys, np.array([[tab["weights"][k] for k in keys]]))[0]
            got = {inv: float(R.round_like_scorer(S0[j])) for j, inv in enumerate(tab["invs"])}
            want = {r["investigation_id"]: r["score"] for r in LIVE[q]["ranking"]}
            self.assertEqual(got, want, q)
            again = scorer.rank(q, config=CFG, catalog=CAT, weights_override=dict(tab["weights"]))
            self.assertEqual([r["investigation_id"] for r in again["results"]],
                             [r["investigation_id"] for r in LIVE[q]["results"]], q)


class ParityTest(unittest.TestCase):
    def test_numpy_rescore_equals_rank_with_override(self):
        for _, q in R.QUERIES:
            tab = R.score_table(q, CFG, CAT)
            for kind in R.KINDS:
                keys, W = R.sample_weights(tab["weights"], 60, 7, kind)
                S = R.round_like_scorer(R.inv_scores(tab, keys, W))
                rs, shown, _ = R.rank_path(tab, keys, W, CFG, CAT)
                np.testing.assert_allclose(rs, S, atol=1e-9, err_msg=f"{q} {kind}")
                self.assertTrue(np.all(shown.sum(axis=1) == CFG["selection"]["top_k"]))


class TieStatsTest(unittest.TestCase):
    def test_ties_count_as_first_and_top3_is_tie_aware(self):
        S = np.array([[5.0, 5.0, 4.0, 4.0, 1.0],
                      [3.0, 2.0, 2.0, 2.0, 2.0]])
        first, in_top, level = R.tie_stats(S, 3)
        self.assertEqual(first[0].tolist(), [True, True, False, False, False])
        self.assertEqual(first[1].tolist(), [True, False, False, False, False])
        # row 0: two score above the 4.0s, so both are among the first three
        self.assertEqual(in_top[0].tolist(), [True, True, True, True, False])
        self.assertEqual(in_top[1].tolist(), [True, True, True, True, True])
        self.assertTrue(level[0, 0, 1] and level[0, 2, 3] and not level[0, 1, 2])

    def test_tolerance(self):
        S = np.array([[1.0, 1.0 - 1e-10, 1.0 - 1e-6]])
        first, _, _ = R.tie_stats(S, 3)
        self.assertEqual(first[0].tolist(), [True, True, False])


def structural_groups_second_path(q):
    """Investigations whose best configurations have identical scored similarities and factor, from
    scoring.scorer directly (no NumPy re-score): these are level for every weighting."""
    sc = scorer.interpret(q, CFG)[0]
    weights = CFG["profiles"][LIVE[q]["profile"]]["weights"]
    _inv, cfgs = CAT
    pre = [(c,) + tuple(scorer.similarities(sc, c, CFG)) for c in cfgs]
    caps = {}
    for d in CFG["similarity"].get("unknown_cap_dims", []):
        known = [S[d] for _, S, _, _, _ in pre if d in S and S[d] is not None]
        if known:
            caps[d] = max(known)
    sig = {}
    for c, S, *_ in pre:
        s = scorer.score_config(sc, c, CFG, weights, S, caps)
        key = (tuple(round(s["similarity"][d], 12) for d in s["weights"]),
               round(s["evidence"] * s["gate"], 12))
        sig.setdefault(c["investigation_id"], set()).add(key)
    return sig


class FileTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(R.OUT.read_text(encoding="utf-8"))
        cls.companion = json.loads((config.INSIGHTS_DIR / metamod.COMPANION).read_text(encoding="utf-8"))

    def test_disclosure(self):
        block = self.data["_meta"]
        self.assertEqual(block, self.companion["robustness.json"])
        self.assertEqual(block["built_by"], "ai/robustness.py")
        self.assertEqual(block["language_model_used_at_build"], config.NO_MODEL)
        self.assertEqual(block["content_sha256"],
                         metamod.sha256_json({k: v for k, v in self.data.items() if k != "_meta"}))
        for rel, sha in block["inputs_sha256"].items():
            self.assertEqual(metamod.sha256_file(ROOT / rel), sha, f"{rel} changed: rerun python3 ai/robustness.py")

    def test_contract_fields(self):
        self.assertEqual([r["query"] for r in self.data["runs"]], [q for _, q in R.QUERIES])
        for run in self.data["runs"]:
            for k in CONTRACT_RUN:
                self.assertIn(k, run)
            self.assertEqual(run["seed"], 42)
            self.assertEqual(run["draws"], 2000)
            self.assertEqual(run["concentration"], 50)
            self.assertEqual(run["tie_tolerance"], 1e-9)
            self.assertEqual(run["config_version"], CFG["version"])
            for r in run["results"]:
                for k in CONTRACT_RESULT:
                    self.assertIn(k, r)
                for p in r["tied_for_first_with"]:
                    self.assertEqual({"investigation_id", "share"} - set(p), set())

    def test_every_live_top3_result_is_reported_with_a_line(self):
        for run in self.data["runs"]:
            live = [r["investigation_id"] for r in LIVE[run["query"]]["results"]]
            self.assertEqual(run["live_top3"], live)
            got = [r["investigation_id"] for r in run["results"] if r["live_rank"]]
            self.assertEqual(got, live)
            for r in run["results"]:
                if r["live_rank"]:
                    self.assertTrue(r["display_line"])
                    self.assertTrue(C.check_template(r["display_line"], r["display_facts"])["ok"], r["display_line"])
                    self.assertNotIn("plausib", r["display_line"].lower())
                    if r["assumed_dims_scored"]:
                        self.assertNotIn("%", r["display_line"], "no stability figure on an assumed atmosphere")

    def test_assumed_dims_copied_from_rank(self):
        for run in self.data["runs"]:
            ranking = {r["investigation_id"]: r for r in LIVE[run["query"]]["ranking"]}
            for r in run["results"]:
                self.assertEqual(r["assumed_dims"], ranking[r["investigation_id"]]["assumed_dims"])
                self.assertEqual(r["unknown_dims"], ranking[r["investigation_id"]]["unknown_dims"])
                scored = set(run["scored_dims"])
                self.assertEqual(r["assumed_dims_scored"],
                                 [a for a in r["assumed_dims"] if R.ASSUMED_TO_DIM[a] in scored])

    def test_ties_in_every_draw_match_the_scorer_similarities(self):
        for run in self.data["runs"]:
            sig = structural_groups_second_path(run["query"])
            for r in run["results"]:
                for other in r["tied_in_every_draw_with"]:
                    self.assertTrue(sig[r["investigation_id"]] & sig[other], (run["query"], r["investigation_id"], other))
                    p = {x["investigation_id"]: x for x in r["tied_for_first_with"]}
                    if r["first_or_tied_share_local"] > 0:
                        self.assertEqual(p[other]["share"], r["first_or_tied_share_local"])

    def test_structural_ties_reported_as_ties(self):
        by_q = {run["query"]: run for run in self.data["runs"]}
        for q in ("ISS", "Mars base"):
            run = by_q[q]
            top = run["results"][0]
            self.assertEqual(top["first_or_tied_share_local"], 1.0)
            self.assertTrue(top["tied_in_every_draw_with"], q)
            self.assertTrue(any(g["first_or_tied_in_every_draw"] for g in run["structural_ties"]), q)
            self.assertIn("a tie, not an order", top["display_line"])

    def test_parity_and_default_check_recorded(self):
        for run in self.data["runs"]:
            self.assertEqual(run["parity"]["mismatches"], 0)
            self.assertEqual(run["parity"]["rank_calls"], 2 * run["draws"])
            self.assertTrue(run["default_check"]["profile_weights_reproduce_live_top3"])
            self.assertTrue(run["default_check"]["numpy_rescore_equals_ranking_scores"])

    def test_seed_check_recorded_honestly(self):
        for run in self.data["runs"]:
            s = run["seed_check"]
            self.assertEqual(s["seed"], 43)
            self.assertEqual(s["within_limit"], s["max_abs_diff_points"] <= s["limit_points"])
            self.assertEqual(s["max_abs_diff_points"], max(s["max_abs_diff_points_local"],
                                                           s["max_abs_diff_points_uniform"]))
            # the display lines print local shares only; those stay within the design's 2 points
            self.assertTrue(s["local_within_limit"], run["query"])

    def test_file_shares_rebuild(self):
        """The committed shares equal a fresh NumPy build at the same seed (no rank() calls)."""
        for run in self.data["runs"]:
            sid = run["scenario_id"]
            fresh = R.build_run(sid, run["query"], CFG, CAT, R.SEED, run["draws"], with_rank=False)
            for a, b in zip(run["results"], fresh["results"]):
                self.assertEqual(a["investigation_id"], b["investigation_id"])
                for k in R.SHARE_KEYS + ("tied_for_first_with", "tied_in_every_draw_with"):
                    self.assertEqual(a[k], b[k], (run["query"], a["investigation_id"], k))


class CheckFileTest(unittest.TestCase):
    def test_check_file_passes_on_the_committed_file(self):
        from ai import check_all
        rep = check_all.Report()
        R.check_file(rep)
        self.assertEqual(rep.failures(), [])
        self.assertTrue(any(x["level"] == "ok" and x["section"] == "robustness" for x in rep.items))

    def test_check_file_fails_on_a_changed_share(self):
        import tempfile
        from pathlib import Path
        from ai import check_all
        data = json.loads(R.OUT.read_text(encoding="utf-8"))
        data["runs"][2]["results"][0]["first_or_tied_share_local"] = 0.5
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "robustness.json"
            p.write_text(json.dumps(data), encoding="utf-8")
            rep = check_all.Report()
            R.check_file(rep, path=p)
        self.assertTrue(any("shares differ" in x["message"] for x in rep.failures()))


if __name__ == "__main__":
    unittest.main()
