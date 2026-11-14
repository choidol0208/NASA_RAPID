# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Unit tests for scoring/scorer.py (standard library only).

Run:  python3 -m unittest scoring.test_scorer -v
"""
import copy
import math
import unittest

from scoring import scorer

CFG = scorer.load_config()
INV, CFGS = scorer.load_catalog()


def fake_inv(**kw):
    base = dict(investigation_id="X", fire_safety_role="prevention", research_focus="flame_spread",
                data_availability="raw_table", mu_g_duration_class="long", verification_status="ai_extracted",
                platform="ISS", psi_url="u", dataset_doi="d", has_1g_comparison="", key_findings="")
    base.update(kw)
    return base


class SimilarityFormulas(unittest.TestCase):
    def test_o2_asymmetric(self):
        p = CFG["similarity"]["o2"]
        c = {"o2_min_pct": "17", "o2_max_pct": "21"}
        self.assertEqual(scorer.s_o2(19, c, p), 1.0)
        self.assertAlmostEqual(scorer.s_o2(30, c, p), math.exp(-9 / 5), places=6)   # 0.165, above: steep
        self.assertAlmostEqual(scorer.s_o2(12, c, p), math.exp(-5 / 10), places=6)  # 0.607, below: gentle

    def test_pressure_factor_two(self):
        c = {"pressure_min_kpa": "101.3", "pressure_max_kpa": "101.3"}
        self.assertAlmostEqual(scorer.s_pressure(50.65, c, CFG["similarity"]["pressure"]), math.exp(-0.5), places=3)

    def test_quiescent_vs_forced_flow(self):
        c = {"flow_config": "opposed", "flow_min_cms": "5", "flow_max_cms": "20"}
        s = scorer.s_flow("quiescent", 0.0, c, CFG["similarity"])
        self.assertAlmostEqual(s, 0.5 * 0.0354, places=3)

    def test_fuel_hierarchy(self):
        p = CFG["similarity"]["fuel"]
        sibal = {"fuel_phase": "solid", "fuel_material": "SIBAL (75% cotton)", "fuel_class": "fabric", "melt_behavior": "chars"}
        bre = {"fuel_phase": "gas", "fuel_material": "methane", "fuel_class": "gaseous_hydrocarbon", "surrogate_for": "solid"}
        jet = {"fuel_phase": "gas", "fuel_material": "ethylene", "fuel_class": "gaseous_hydrocarbon"}
        user = {"fuel_material": "cotton", "fuel_class": "fabric", "fuel_phase": "solid", "melt_behavior": "chars"}
        self.assertEqual(scorer.s_fuel(user, sibal, p), 1.0)
        self.assertEqual(scorer.s_fuel(user, bre, p), 0.5)
        self.assertEqual(scorer.s_fuel(user, jet, p), 0.1)


class HandCalculation(unittest.TestCase):
    """Two hypothetical configurations from the guideline document (values are invented)."""

    def setUp(self):
        self.cfg = copy.deepcopy(CFG)
        self.cfg["atmosphere_fallback"] = {}
        self.sc = dict(o2_pct=30.0, pressure_kpa=70.3, flow_state="ventilated", flow_cms=10.0,
                       fuel_material="cotton", fuel_class="fabric", fuel_phase="solid", melt_behavior="chars",
                       thermal_regime="thin", sample_geometry="flat_sheet", concern="prevention")
        self.w = self.cfg["profiles"]["prevention"]["weights"]

    def run_one(self, c):
        S, _, _, _ = scorer.similarities(self.sc, c, self.cfg)
        return scorer.score_config(self.sc, c, self.cfg, self.w, S, {})

    def test_x_fabric(self):
        x = dict(investigation_id="X", fuel_phase="solid", fuel_material="fiberglass-backed fabric blend", fuel_class="fabric",
                 melt_behavior="chars", sample_geometry="flat_sheet", thermal_regime="thin", flow_config="concurrent",
                 flow_min_cms="5", flow_max_cms="20", o2_min_pct="17", o2_max_pct="30",
                 pressure_min_kpa="50", pressure_max_kpa="101.3", _inv=fake_inv())
        s = self.run_one(x)
        self.assertAlmostEqual(s["raw"], 0.93, places=3)   # 0.25 + 0.10 + 0.18 + 0.20 + 0.10 + 0.10
        self.assertEqual(s["gate"], 1.0)
        self.assertAlmostEqual(s["evidence"], 0.97, places=3)
        self.assertAlmostEqual(s["score"], 90.2, places=1)

    def test_y_gas_jet(self):
        y = dict(investigation_id="Y", fuel_phase="gas", fuel_material="propane", fuel_class="gaseous_hydrocarbon",
                 sample_geometry="jet_burner", flow_config="coflow", flow_min_cms="5", flow_max_cms="30",
                 o2_min_pct="21", o2_max_pct="50", pressure_min_kpa="101.3", pressure_max_kpa="101.3",
                 _inv=fake_inv(fire_safety_role="fundamental", research_focus="flame_structure",
                               data_availability="processed_table"))
        s = self.run_one(y)
        self.assertAlmostEqual(s["raw"], 0.522, places=3)
        self.assertAlmostEqual(s["gate"], 0.75, places=3)  # ramp: 0.5 + 0.5 * (0.1 / 0.2)
        self.assertLess(s["score"], 45)


class Interpretation(unittest.TestCase):
    def test_iss_only(self):
        sc, src, assumptions, oos, informative = scorer.interpret("ISS", CFG)
        self.assertEqual(sc["preset"], "iss")
        self.assertEqual(sc["o2_pct"], 21.0)
        self.assertIn("o2_pct", [a["field"] for a in assumptions])
        self.assertFalse(oos)

    def test_korean_lunar_fabric(self):
        sc, *_ = scorer.interpret("달 기지 면직물", CFG)
        self.assertEqual(sc["preset"], "lunar_habitat")
        self.assertEqual(sc["fuel_class"], "fabric")

    def test_numbers_override_preset(self):
        sc, src, *_ = scorer.interpret("ISS at 30% O2 and 10.2 psi, 10 cm/s", CFG)
        self.assertEqual(sc["o2_pct"], 30.0)
        self.assertAlmostEqual(sc["pressure_kpa"], 70.3, places=1)
        self.assertEqual(sc["flow_cms"], 10.0)
        self.assertEqual(src["o2_pct"], "text")

    def test_explicit_fields_win(self):
        sc, src, *_ = scorer.interpret({"text": "ISS", "o2_pct": 25, "fuel": "PMMA"}, CFG)
        self.assertEqual(sc["o2_pct"], 25.0)
        self.assertEqual(sc["fuel_class"], "thermoplastic_solid")

    def test_word_boundaries(self):
        sc, *_ = scorer.interpret("infant safety", CFG)  # 'fan' inside a word must not match
        self.assertNotIn("flow_state", sc)

    def test_co2_is_not_oxygen(self):
        sc, src, *_ = scorer.interpret("CO2 30% suppression ISS", CFG)
        self.assertEqual(sc["o2_pct"], 21.0)  # from the ISS preset, not from "CO2 30%"
        self.assertEqual(src["o2_pct"], "preset:iss")
        sc, *_ = scorer.interpret("H2O2 leak", CFG)
        self.assertNotIn("o2_pct", sc)
        sc, *_ = scorer.interpret("CO2 5% and O2 25%", CFG)
        self.assertEqual(sc["o2_pct"], 25.0)

    def test_ceiling_is_not_fabric(self):
        sc, *_ = scorer.interpret("천장 배선 과열", CFG)  # 천장 = ceiling, not 천 (cloth)
        self.assertNotEqual(sc.get("fuel_class"), "fabric")
        sc, *_ = scorer.interpret("천으로 된 커튼", CFG)
        self.assertEqual(sc.get("fuel_class"), "fabric")


class Ranking(unittest.TestCase):
    def test_out_of_scope(self):
        self.assertEqual(scorer.rank("hybrid rocket combustion chamber")["status"], "out_of_scope")

    def test_need_input(self):
        self.assertEqual(scorer.rank("")["status"], "need_input")

    def test_top3_distinct_investigations_and_deterministic(self):
        a, b = scorer.rank("ISS cotton fabric"), scorer.rank("ISS cotton fabric")
        ids = [r["investigation_id"] for r in a["results"]]
        self.assertEqual(len(ids), 3)
        self.assertEqual(len(set(ids)), 3)
        self.assertEqual(ids, [r["investigation_id"] for r in b["results"]])

    def test_scores_bounded(self):
        out = scorer.rank("lunar habitat cotton fabric")
        for r in out["ranking"]:
            self.assertGreaterEqual(r["score"], 0)
            self.assertLessEqual(r["score"], 100)


class AssumedAtmosphereWording(unittest.TestCase):
    """A value filled in by the atmosphere fallback was not recorded, so it is never worded as 'tested'."""

    def test_bass_c01_iss_cotton_not_tested(self):
        out = scorer.rank("ISS cotton fabric")
        rows = [r for r in out["ranking"] + out["results"] if r["config_id"] == "BASS-C01"]
        self.assertTrue(rows, "BASS-C01 should be ranked for 'ISS cotton fabric'")
        for r in rows:
            self.assertIn("O2", r["assumed_dims"])
            self.assertNotIn("tested 21%", r["why"])
            self.assertNotIn("tested 21%", r["main_gap"])

    def test_no_assumed_value_worded_as_tested(self):
        for q in ("ISS cotton fabric", "lunar habitat", "heptane droplet ISS", "smoke detector on ISS", "ISS"):
            for r in scorer.rank(q)["ranking"]:
                text = r["why"] + " " + r["main_gap"]
                if "O2" in r["assumed_dims"]:
                    self.assertNotIn("O2 tested", text, (q, r["config_id"]))
                if "pressure" in r["assumed_dims"]:
                    self.assertNotIn("pressure tested", text, (q, r["config_id"]))

    def test_confidence_ignores_assumed_values(self):
        w = CFG["profiles"]["prevention"]["weights"]
        for r in scorer.rank("ISS cotton fabric")["ranking"]:
            assumed = {"O2": "o2", "pressure": "pressure"}
            lost = sum(w[assumed[x]] for x in r["assumed_dims"]) + sum(w[d] for d in r["unknown_dims"])
            self.assertAlmostEqual(r["coverage"], round(1.0 - lost, 2), places=2, msg=r["config_id"])
        rows = {r["config_id"]: r for r in scorer.rank("ISS cotton fabric")["results"]}
        if "BASS-C01" in rows:  # O2 and pressure both assumed: never "high"
            self.assertNotEqual(rows["BASS-C01"]["confidence"], "high")

    def test_recorded_reasons_come_first(self):
        for r in scorer.rank("ISS cotton fabric")["ranking"]:
            assumed = {"o2"} if "O2" in r["assumed_dims"] else set()
            if "pressure" in r["assumed_dims"]:
                assumed.add("pressure")
            recorded = [d for d in r["contributions"] if d not in r["unknown_dims"] and d not in assumed]
            if assumed and len(recorded) >= 2:
                self.assertNotRegex(r["why"].split(";")[0], r"^(O2|pressure) match", r["config_id"])


class OxidizerStream(unittest.TestCase):
    """The O2 of an inverse flame is its burner stream, not an atmosphere: never matched with the user's O2."""

    def test_stream_o2_is_unknown(self):
        p = CFG["similarity"]["o2"]
        self.assertIsNone(scorer.s_o2(21, {"o2_min_pct": "18", "o2_max_pct": "85", "o2_reference": "oxidizer_stream"}, p))
        self.assertEqual(scorer.s_o2(21, {"o2_min_pct": "18", "o2_max_pct": "85", "o2_reference": "ambient"}, p), 1.0)

    def test_stream_configs_not_matched_on_o2(self):
        streams = {c["config_id"] for c in CFGS if c["o2_reference"] == "oxidizer_stream"}
        self.assertTrue(streams)
        for r in scorer.rank("50% O2")["ranking"]:
            if r["config_id"] in streams:
                self.assertIn("o2", r["unknown_dims"])
                codes = [w["code"] for w in r["warnings"]]
                self.assertIn("oxidizer_stream", codes)
                self.assertNotIn("o2_above_result", codes)

    def test_o2_above_all_uses_ambient_maximum(self):
        ambient_max = max(float(c["o2_max_pct"]) for c in CFGS if c["o2_max_pct"] and c["o2_reference"] != "oxidizer_stream")
        self.assertEqual(ambient_max, 40.0)
        w = [x for x in scorer.rank("50% O2")["warnings"] if x["code"] == "o2_above_all"]
        self.assertEqual(len(w), 1)
        self.assertIn("40%", w[0]["message"])
        self.assertFalse([x for x in scorer.rank("39% O2")["warnings"] if x["code"] == "o2_above_all"])


class OpenRangeWording(unittest.TestCase):
    """A range with one recorded end is worded as such: PSI-26 says 'up to 40 cm/s', never 'at 40 cm/s'."""

    def test_fmt_range_ends(self):
        f = lambda lo, hi: scorer._fmt_range({"a": lo, "b": hi}, "a", "b", " cm/s")
        self.assertEqual(f("", "40"), "up to 40 cm/s")
        self.assertEqual(f("5", ""), "at least 5 cm/s")
        self.assertEqual(f("5", "10"), "5–10 cm/s")
        self.assertEqual(f("20", "20"), "20 cm/s")
        self.assertEqual(f("", ""), "not reported")

    def test_bass_flow_up_to_40(self):
        bass = [c for c in CFGS if c["investigation_id"] == "BASS"]
        self.assertTrue(bass and all(not c["flow_min_cms"] and c["flow_max_cms"] == "40" for c in bass))
        shown = 0
        for q in ("fabric 20 cm/s", "PMMA 10 cm/s ISS", "nitrogen extinguish fabric fire ISS", "ISS cotton fabric"):
            for r in scorer.rank(q)["ranking"]:
                if r["investigation_id"] != "BASS":
                    continue
                text = r["why"] + " " + r["main_gap"]
                self.assertNotIn("at 40 cm/s", text, (q, r["config_id"]))
                shown += "up to 40 cm/s" in text
        self.assertGreater(shown, 0, "no BASS reason mentions its flow; pick another query")
        # The range used for similarity is unchanged: 40 cm/s is still a full match at 40.
        self.assertEqual(scorer._range(bass[0], "flow_min_cms", "flow_max_cms"), (40.0, 40.0))


class CatalogIntegrity(unittest.TestCase):
    def test_counts_and_links(self):
        self.assertEqual(len(INV), 24)
        accs = {r["psi_accession"] for r in INV.values()}
        self.assertEqual(accs, {c["psi_accession"] for c in CFGS})
        for r in INV.values():
            self.assertTrue(r["psi_url"].startswith("https://psi.nasa.gov/"))
            self.assertTrue(r["dataset_doi"].startswith("10.60555/"))

    def test_ranges_ordered(self):
        for c in CFGS:
            for a, b in (("o2_min_pct", "o2_max_pct"), ("pressure_min_kpa", "pressure_max_kpa"), ("flow_min_cms", "flow_max_cms")):
                if c[a] and c[b]:
                    self.assertLessEqual(float(c[a]), float(c[b]), c["config_id"])

    def test_profile_weights_sum_to_one(self):
        for name, p in CFG["profiles"].items():
            self.assertAlmostEqual(sum(p["weights"].values()), 1.0, places=6, msg=name)


if __name__ == "__main__":
    unittest.main()
