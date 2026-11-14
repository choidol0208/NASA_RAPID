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
        # log of the O2 ratio (config 1.1.0): above steep, below gentle
        self.assertAlmostEqual(scorer.s_o2(30, c, p), math.exp(-math.log(30 / 21) / p["above_scale_ln"]), places=6)
        self.assertAlmostEqual(scorer.s_o2(12, c, p), math.exp(-math.log(17 / 12) / p["below_scale_ln"]), places=6)
        self.assertLess(scorer.s_o2(30, c, p), scorer.s_o2(12, c, p))
        # near air the scales equal the earlier 5 and 10 percentage points
        air = {"o2_min_pct": "21", "o2_max_pct": "21"}
        self.assertAlmostEqual(scorer.s_o2(26, air, p), math.exp(-1), places=4)
        self.assertAlmostEqual(scorer.s_o2(11, air, p), math.exp(-1), places=4)

    def test_o2_ratio_not_points(self):
        # the same 6-point gap is larger at low oxygen than at high oxygen
        p = CFG["similarity"]["o2"]
        low = scorer.s_o2(15, {"o2_min_pct": "21", "o2_max_pct": "21"}, p)
        high = scorer.s_o2(30, {"o2_min_pct": "36", "o2_max_pct": "36"}, p)
        self.assertLess(low, high)
        self.assertEqual(scorer.s_o2(0, {"o2_min_pct": "12", "o2_max_pct": "21"}, p), 0.0)

    def test_diluent_by_heat_capacity(self):
        p = CFG["similarity"]["diluent"]
        s = lambda u, cd: scorer.s_diluent(u, {"diluent": cd}, p)
        self.assertEqual(s("CO2", "N2; CO2; He"), 1.0)
        self.assertEqual(s("CO2", ""), p["none"])
        self.assertGreater(s("CO2", "N2"), s("CO2", "He"))   # N2 is closer to CO2 in heat capacity than He
        self.assertGreater(s("N2", "He"), s("CO2", "He"))
        self.assertAlmostEqual(s("CO2", "N2"), (29.071 / 37.198) ** 2, places=6)
        self.assertEqual(s("CO2", "N2; He"), s("CO2", "N2"))  # best match over the configuration's diluents
        self.assertEqual(s("Ar", "N2"), p["other_inert"])      # no heat capacity listed: flat value

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
        # AHP weights (config 1.2.0): 0.285*1 + 0.090*1 + 0.166*0.9 + 0.267*0.8 + 0.111*1 + 0.081*1
        self.assertAlmostEqual(s["raw"], 0.93, places=3)
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
        # 0.285*1 + 0.090*0.8703 + 0.166*0.5 + 0.267*0.1 + 0.111*0.2 + 0.081*0.4
        self.assertAlmostEqual(s["raw"], 0.528, places=3)
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
        sc, *_ = scorer.interpret("달 기지 면직물", CFG)  # Korean: "lunar base cotton fabric"
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

    def test_not_understood_words(self):
        out = scorer.rank("battery enclosure for the ISS")
        self.assertEqual(out["not_understood"], ["battery enclosure"])
        self.assertIn("not_understood", [w["code"] for w in out["warnings"]])
        self.assertEqual(scorer.rank("3D printer on the Moon")["not_understood"], ["3d printer"])
        out = scorer.rank("glove box")
        self.assertEqual((out["status"], out["not_understood"]), ("need_input", ["glove box"]))
        for q in ("ISS", "lunar habitat", "ISS cotton fabric", "lunar habitat cotton fabric", "달 기지 면직물",  # Korean: lunar base cotton fabric
                  "ISS at 30% O2 and 10.2 psi", "CO2 suppression of heptane fire"):
            out = scorer.rank(q)
            self.assertEqual(out["not_understood"], [], q)
            self.assertNotIn("not_understood", [w["code"] for w in out["warnings"]], q)
        # words that are not read change no score
        a = [(r["config_id"], r["score"]) for r in scorer.rank("ISS")["ranking"]]
        b = [(r["config_id"], r["score"]) for r in scorer.rank("battery enclosure for the ISS")["ranking"]]
        self.assertEqual(a, b)

    def test_sentence_queries_ui_1817(self):
        # 1. a Korean particle right after the unit ("70 kPa의", "70kPa인") must not hide the typed pressure
        for q in ("산소 30% 기압 70 kPa의 달 기지",  # Korean: lunar base, 30% oxygen, air pressure 70 kPa
                  "산소 30%, 70kPa인 기지"):          # Korean: a base at 30% oxygen and 70 kPa
            sc, src, *_ = scorer.interpret(q, CFG)
            self.assertEqual((sc["pressure_kpa"], src["pressure_kpa"]), (70.0, "text"), q)
            self.assertEqual(sc["o2_pct"], 30.0, q)
        # 2. "spacecraft cabin" reads as the ISS cabin, but a named preset still wins
        for q in ("spacecraft cabin", "우주선 선실"):  # Korean: spacecraft cabin
            self.assertEqual(scorer.rank(q)["scenario"].get("preset"), "iss", q)
        self.assertEqual(scorer.rank("lunar spacecraft")["scenario"].get("preset"), "lunar_habitat")
        # 3. a planet or base that is not named gets the partial-gravity warning, with no value guessed
        for q in ("a base on a planet whose atmosphere has 30% oxygen",
                  "산소 농도 30%의 행성에서 기지를 건설"):  # Korean: building a base on a planet at 30% oxygen
            out = scorer.rank(q)
            self.assertEqual(out["scenario"].get("gravity"), "planetary", q)
            self.assertIn("partial_gravity", [w["code"] for w in out["warnings"]], q)
            self.assertNotIn("pressure_kpa", out["scenario"], q)
        self.assertEqual(scorer.rank("Mars base")["scenario"].get("gravity"), "martian")

    def test_ceiling_is_not_fabric(self):
        sc, *_ = scorer.interpret("천장 배선 과열", CFG)  # Korean: "ceiling wiring overheating"; 천장 = ceiling, not 천 (cloth)
        self.assertNotEqual(sc.get("fuel_class"), "fabric")
        sc, *_ = scorer.interpret("천으로 된 커튼", CFG)  # Korean: "a curtain made of cloth"
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
            self.assertEqual(r["coverage"], scorer._r(1.0 - lost, 2), r["config_id"])  # the scorer's rounding (half up)
        rows = {r["config_id"]: r for r in scorer.rank("ISS cotton fabric")["results"]}
        if "BASS-C01" in rows:  # O2 and pressure both assumed: never "high"
            self.assertNotEqual(rows["BASS-C01"]["confidence"], "high")

    def test_recorded_reasons_come_first(self):
        for r in scorer.rank("ISS cotton fabric")["ranking"]:
            assumed = {"o2"} if "O2" in r["assumed_dims"] else set()
            if "pressure" in r["assumed_dims"]:
                assumed.add("pressure")
            recorded = [d for d in r["contributions"] if d not in r["unknown_dims"] and d not in assumed]
            if assumed and len(recorded) >= 2:  # the first reason is never an assumed value
                pat = "|".join({"o2": "O2", "pressure": "pressure"}[d] for d in sorted(assumed))
                self.assertNotRegex(r["why"].split(";")[0], rf"^({pat}) match", r["config_id"])


class SourceWording(unittest.TestCase):
    """'tested' only for numbers from an experimental table (catalog columns o2_source, pressure_source, flow_source)."""

    def test_every_value_has_a_source(self):
        for c in CFGS:
            for var, lo, hi in (("o2", "o2_min_pct", "o2_max_pct"), ("pressure", "pressure_min_kpa", "pressure_max_kpa"),
                                ("flow", "flow_min_cms", "flow_max_cms")):
                has = bool(c[lo] or c[hi])
                self.assertEqual(bool(c[f"{var}_source"]), has, (c["config_id"], var))
                self.assertIn(c[f"{var}_source"], ("", "table", "record", "test_matrix", "team"))

    def test_record_pressure_of_bre_is_not_tested(self):
        rows = {r["config_id"]: r for r in scorer.rank("lunar habitat")["ranking"]}
        text = rows["ACME-BRE-C01"]["why"] + " " + rows["ACME-BRE-C01"]["main_gap"]
        self.assertIn("named in the PSI record, not a test value", text)
        self.assertNotIn("pressure tested", text)

    def test_no_non_table_value_worded_as_tested(self):
        src = {c["config_id"]: c for c in CFGS}
        for q in ("lunar habitat", "ISS", "spacesuit", "heptane droplet 30% O2 10.2 psi", "stagnant PMMA 34% O2"):
            for r in scorer.rank(q)["ranking"]:
                text = r["why"] + " " + r["main_gap"]
                for var, label in (("o2", "O2"), ("pressure", "pressure")):
                    if src[r["config_id"]][f"{var}_source"] not in ("table", ""):
                        self.assertNotIn(f"{label} tested", text, (q, r["config_id"]))


class PmDecisions1415(unittest.TestCase):
    """coord/decisions.md 14:15: human checks do not change scores; ranges_separate on side-by-side ranges."""

    def test_human_check_does_not_change_score(self):
        v = CFG["evidence"]["verification_status"]
        self.assertEqual(v["human_verified"], v["ai_extracted"])
        cfgs = copy.deepcopy(CFGS)
        invs = {k: dict(v) for k, v in INV.items()}
        for c in cfgs:
            c["_inv"] = invs[c["investigation_id"]]
        invs["BASS"]["verification_status"] = "human_verified"
        before = [(r["config_id"], r["score"]) for r in scorer.rank("ISS cotton fabric")["ranking"]]
        after = [(r["config_id"], r["score"]) for r in scorer.rank("ISS cotton fabric", catalog=(invs, cfgs))["ranking"]]
        self.assertEqual(before, after)

    def test_ranges_separate(self):
        rows = {r["config_id"]: r for r in scorer.rank("lunar habitat")["ranking"]}
        codes = lambda cid: [w["code"] for w in rows[cid]["warnings"]]
        self.assertIn("ranges_separate", codes("FLEX-C01"))         # 12-34% and 70.2-309.3 kPa
        self.assertIn("ranges_separate", codes("ACME-BRE-C01"))     # 21-40% and 56.5-101.3 kPa
        for r in scorer.rank("ISS")["ranking"]:                     # assumed values are points, not ranges
            if {"O2", "pressure"} & set(r["assumed_dims"]):
                self.assertNotIn("ranges_separate", [w["code"] for w in r["warnings"]], r["config_id"])
        for r in scorer.rank("cotton fabric")["ranking"]:            # no O2 or pressure compared
            self.assertNotIn("ranges_separate", [w["code"] for w in r["warnings"]], r["config_id"])


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

    def test_open_range_speed_is_unknown_not_a_miss(self):
        sim = CFG["similarity"]
        c = {"flow_min_cms": "", "flow_max_cms": "40"}
        u = sim["unknown_value"]
        self.assertEqual(scorer._speed(10, c, sim), (u, None))   # below "up to 40": not recorded, no warning
        self.assertEqual(scorer._speed(40, c, sim), (u, None))   # 40 is the tunnel's limit, not a test value
        self.assertAlmostEqual(scorer._speed(40.01, c, sim)[0], u, places=3)  # no jump at the end
        s, signal = scorer._speed(80, c, sim)                     # beyond it: decays from unknown_value
        self.assertLess(s, u)
        self.assertLess(signal, 0.9)                              # and raises outside_range
        closed = {"flow_min_cms": "20", "flow_max_cms": "20"}
        self.assertLess(scorer._speed(10, closed, sim)[0], 0.9)                     # a closed range still misses
        rows = {r["config_id"]: r for r in scorer.rank("SIBAL 10 cm/s")["ranking"]}
        if "BASS-C01" in rows:
            self.assertNotIn("flow speed", " ".join(w["message"] for w in rows["BASS-C01"]["warnings"]))


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


class Requirements(unittest.TestCase):
    """Systems-engineering layer: one requirement per dimension the query sets, with its source; a compliance line per result."""

    def test_iss_cotton_fabric_requirements(self):
        out = scorer.rank("ISS cotton fabric")
        reqs = {q["dimension"]: q for q in out["requirements"]}
        self.assertEqual(list(reqs), ["gravity", "o2", "pressure", "flow", "fuel", "geometry", "role"])
        self.assertEqual(reqs["o2"]["source"], "implied by preset iss")
        self.assertEqual(reqs["o2"]["value"], "21%")
        self.assertEqual(reqs["fuel"]["source_class"], "stated")
        self.assertEqual(reqs["role"]["source_class"], "assumed")  # no purpose word: prevention by default
        self.assertEqual([q["id"] for q in out["requirements"]], [f"R{i}" for i in range(1, 8)])

    def test_compliance_follows_the_similarities(self):
        out = scorer.rank("ISS cotton fabric")
        rid = {q["dimension"]: q["id"] for q in out["requirements"]}
        for r in out["results"]:
            st = {c["id"]: c["status"] for c in r["compliance"]}
            self.assertEqual(len(st), len(out["requirements"]))
            if "O2" in r["assumed_dims"]:
                self.assertEqual(st[rid["o2"]], "unverified")  # an assumed atmosphere never counts as met
            self.assertEqual(st[rid["gravity"]], "met")
            for d in ("fuel", "geometry"):
                expect = "met" if r["similarity"][d] >= 0.999 else None
                if expect:
                    self.assertEqual(st[rid[d]], expect)

    def test_partial_gravity_is_not_met(self):
        out = scorer.rank("lunar habitat cotton fabric")
        rid = {q["dimension"]: q["id"] for q in out["requirements"]}
        for r in out["results"]:
            self.assertEqual({c["id"]: c["status"] for c in r["compliance"]}[rid["gravity"]], "not_met")

    def test_diluent_not_scored_outside_suppression(self):
        out = scorer.rank("ISS cotton fabric in CO2")
        reqs = {q["dimension"]: q["id"] for q in out["requirements"]}
        if "diluent" in reqs:
            for r in out["results"]:
                self.assertEqual({c["id"]: c["status"] for c in r["compliance"]}[reqs["diluent"]], "not_scored")

    def test_requirements_change_no_score(self):
        cfg = copy.deepcopy(CFG)
        cfg.pop("requirements")
        for q in ("ISS", "lunar habitat cotton fabric", "CO2 suppression of heptane fire"):
            a = [(r["config_id"], r["score"]) for r in scorer.rank(q)["results"]]
            b = [(r["config_id"], r["score"]) for r in scorer.rank(q, config=cfg)["results"]]
            self.assertEqual(a, b, q)


class AhpWeights(unittest.TestCase):
    """Config 1.2.0: the profile weights are the AHP derivation of scoring/ahp_judgements.json."""

    @classmethod
    def setUpClass(cls):
        from scoring import derive_weights
        cls.dw = derive_weights
        cls.res = derive_weights.derive()

    def test_config_weights_are_the_derivation(self):
        self.assertEqual(self.dw.config_differences(self.res, CFG), [])

    def test_judgements_are_consistent(self):
        for prof, r in self.res.items():
            self.assertLess(r["cr"], 0.10, prof)  # Saaty's limit

    def test_matrix_is_reciprocal_and_complete(self):
        for prof, r in self.res.items():
            A, n = r["matrix"], r["n"]
            for i in range(n):
                self.assertEqual(A[i][i], 1.0)
                for j in range(n):
                    self.assertAlmostEqual(A[i][j] * A[j][i], 1.0, places=12, msg=prof)

    def test_eigenvector_agrees_with_geometric_mean(self):
        # For a nearly consistent matrix the two standard AHP estimates must almost coincide.
        for prof, r in self.res.items():
            for d in r["dims"]:
                self.assertAlmostEqual(r["exact"][d], r["geometric_mean"][d], delta=0.005, msg=(prof, d))

    def test_consistent_matrix_gives_its_ratios(self):
        # A perfectly consistent matrix a_ij = w_i / w_j returns w exactly, with CR 0.
        w = [0.5, 0.3, 0.2]
        A = [[wi / wj for wj in w] for wi in w]
        got, lam = self.dw.eigen_weights(A)
        for x, y in zip(got, w):
            self.assertAlmostEqual(x, y, places=9)
        self.assertAlmostEqual(lam, 3.0, places=9)

    def test_rounded_weights_sum_to_one(self):
        for prof, r in self.res.items():
            self.assertAlmostEqual(sum(r["weights"].values()), 1.0, places=9, msg=prof)


if __name__ == "__main__":
    unittest.main()
