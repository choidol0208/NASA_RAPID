# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for the structured request (ai/assistant/request.py). No network, no model.

    python3 -m unittest ai.assistant.test_request -v
"""
import unittest

from ai import llm
from ai.assistant import request as rq
from ai.assistant.testkit import reading
from scoring import scorer

V = rq.load_vocab()


def build(values, extra=None, state=None, conflicts=None):
    base = {"item_words": None, "compare_with": [], "term": None, "keywords": [], "new_topic": False,
            "english": "x", "tests": [], "flow": None}
    base.update(extra or {})
    full = {f: None for f in rq.FIELDS}
    full.update({"questions": [], "investigations": [], "asks_verdict": False, "asks_prediction": False})
    full.update(values)
    return rq.build_request(full, {}, norm_extra=base, state=state, vocab=V, conflicts=conflicts)


class RuleReaderTest(unittest.TestCase):
    CASES = [
        ("Which NASA experiments are closest to a cotton fabric fire in a lunar habitat?",
         {"preset": "lunar_habitat", "material": "cotton", "intent": "find_investigations"}),
        ("Is Nomex safe to use in a 34% oxygen cabin?", {"material": "nomex", "o2_pct": 34.0, "asks_verdict": True}),
        ("Compare the ISS with a spacesuit", {"intent": "compare_environments", "preset": "iss",
                                              "compare_with": ["spacesuit"]}),
        ("Where are the raw files for FLEX-21?", {"intent": "where_data", "tests": ["FLEX-21"]}),
        ("What research is behind smoke detectors for spacecraft?", {"intent": "equipment_research",
                                                                     "equipment": "detection"}),
        ("What would happen to PMMA at 40% oxygen?", {"asks_prediction": True, "material": "pmma", "o2_pct": 40.0}),
        ("hello", {"intent": "help"}),
        ("How do rocket engines burn propellant?", {"intent": "out_of_scope"}),
        ("달 기지 로버 좌석 커버가 면직물인데, 관련 NASA 실험 뭐가 있어?", {"preset": "lunar_habitat", "material": "cotton"}),
        ("우주정거장에서 연기 감지기 연구 알려줘", {"preset": "iss", "intent": "equipment_research", "equipment": "detection"}),
        ("화성 기지에서 이 소재 써도 괜찮아?", {"preset": "mars_habitat", "asks_verdict": True}),
    ]

    def test_cases(self):
        for msg, want in self.CASES:
            r = rq.rule_reading(msg, None, V)
            for k, v in want.items():
                self.assertEqual(r[k], v, f"{msg!r}: {k}")

    def test_no_intent_word_is_no_opinion(self):
        r = rq.rule_reading("Is cotton safe in a lunar habitat?", None, V)
        self.assertFalse(r["intent_opinion"])
        self.assertEqual(r["intent"], "find_investigations")


class GroundingTest(unittest.TestCase):
    def test_oxygen_not_in_message_is_removed(self):
        n, removed, *_ = rq.ground(reading(preset="lunar_habitat", o2=30), "cotton in a lunar base", None, V)
        self.assertIsNone(n["o2_pct"])
        self.assertEqual(removed, [{"field": "environment.o2_pct", "value": 30}])

    def test_oxygen_in_message_is_kept(self):
        n, removed, *_ = rq.ground(reading(o2=26.5), "a cabin at 26.5% oxygen", None, V)
        self.assertEqual(n["o2_pct"], 26.5)
        self.assertEqual(removed, [])

    def test_psi_is_converted_by_code(self):
        n, removed, *_ = rq.ground(reading(pv=10.2, pu="psi"), "a rover at 10.2 psi", None, V)
        self.assertEqual(n["pressure_kpa"], 70.3)
        self.assertEqual(n["pressure_kpa"], scorer._r(10.2 * scorer.UNITS_TO_KPA["psi"], 1))

    def test_pressure_without_unit_is_removed(self):
        n, removed, *_ = rq.ground(reading(pv=70, pu=None), "a rover at 70", None, V)
        self.assertIsNone(n["pressure_kpa"])
        self.assertEqual(removed[0]["field"], "environment.pressure_kpa")

    def test_names_resolve(self):
        n, _, unresolved, assumptions, clarify = rq.ground(reading(investigations=["Saffire", "Zorblax"]), "x", None, V)
        self.assertEqual(n["investigations"], ["PSI-98", "PSI-99", "PSI-100"])
        self.assertEqual(unresolved, ["Zorblax"])
        self.assertTrue(assumptions)
        self.assertIsNone(clarify)

    def test_unknown_enum_value_dropped(self):
        n, removed, *_ = rq.ground(reading(material="unobtainium"), "x", None, V)
        self.assertIsNone(n["material"])


class AgreementTest(unittest.TestCase):
    def norm(self, **kw):
        n = rq.empty_norm()
        n.update(kw)
        return n

    def test_row1_models_agree(self):
        m = self.norm(intent="find_investigations", preset="iss")
        r = self.norm(intent="find_investigations", intent_opinion=False, preset="lunar_habitat")
        v, a, c = rq.agree({"M1": m, "M2": dict(m), "R": r})
        self.assertEqual(v["preset"], "iss")
        self.assertEqual(a["environment.preset"], "agree")

    def test_row2_majority(self):
        v, a, c = rq.agree({"M1": self.norm(intent="help", preset="iss"), "M2": self.norm(intent="help", preset="earth"),
                            "R": self.norm(intent="help", preset="iss")})
        self.assertEqual(v["preset"], "iss")
        self.assertEqual(a["environment.preset"], "majority")

    def test_row3_single(self):
        v, a, c = rq.agree({"M1": self.norm(intent="help"), "R": self.norm(intent="help", material="cotton")})
        self.assertEqual(v["material"], "cotton")
        self.assertEqual(a["item.material"], "rules_only")

    def test_row4_conflict(self):
        v, a, c = rq.agree({"M1": self.norm(intent="help", preset="iss"), "M2": self.norm(intent="help", preset="earth"),
                            "R": self.norm(intent="help", preset="spacesuit")})
        self.assertEqual(a["environment.preset"], "conflict")
        self.assertEqual(v["preset"], "spacesuit")  # R's value when the field is not asked about
        self.assertIn("preset", c)

    def test_conflict_of_needed_field_asks(self):
        v, a, c = rq.agree({"M1": self.norm(intent="question_evidence", preset="iss"),
                            "M2": self.norm(intent="question_evidence", preset="earth"),
                            "R": self.norm(intent="question_evidence", preset="spacesuit")})
        req = build(v, conflicts=c)
        self.assertEqual(req["clarify"]["field"], "environment")
        self.assertTrue(req["clarify"]["question"].startswith("I read this two ways"))

    def test_intent_precedence(self):
        v, a, c = rq.agree({"M1": self.norm(intent="explain"), "M2": self.norm(intent="help"),
                            "R": self.norm(intent="out_of_scope")})
        self.assertEqual(v["intent"], "out_of_scope")

    def test_rule_verdict_word_always_shows_notice(self):
        v, a, c = rq.agree({"M1": self.norm(intent="help"), "M2": self.norm(intent="help"),
                            "R": self.norm(intent="help", asks_verdict=True)})
        self.assertTrue(v["asks_verdict"])

    def test_m1_matches_rules(self):
        r = rq.rule_reading("cotton in a lunar habitat", None, V)
        m1, *_ = rq.ground(reading(preset="lunar_habitat", material="cotton"), "cotton in a lunar habitat", None, V)
        self.assertTrue(rq.m1_matches_rules(m1, r))
        m1b, *_ = rq.ground(reading(preset="iss", material="cotton"), "cotton in a lunar habitat", None, V)
        self.assertFalse(rq.m1_matches_rules(m1b, r))


class BuildTest(unittest.TestCase):
    def test_preset_expansion_and_schema(self):
        req = build({"intent": "find_investigations", "preset": "lunar_habitat", "material": "cotton"})
        self.assertEqual(llm.validate(req, rq.REQUEST), [])
        env = req["environment"]
        self.assertEqual((env["o2_pct"], env["pressure_kpa"], env["gravity"], env["scenario_id"]),
                         (30.0, 70.3, "lunar", "lunar_habitat"))
        self.assertEqual(req["sources"]["environment.o2_pct"], "preset")
        self.assertEqual(req["dashboard_q"], "lunar habitat cotton")

    def test_values_outside_preset_use_a_cell(self):
        req = build({"intent": "find_investigations", "preset": "lunar_habitat", "o2_pct": 26.5, "pressure_kpa": 70.0})
        self.assertIsNone(req["environment"]["scenario_id"])
        self.assertEqual(req["environment"]["cell"]["id"], "cell_o2_23_30__p_62_8_85_8")
        self.assertEqual(req["environment"]["gravity"], "lunar")

    def test_clarify_missing_environment(self):
        req = build({"intent": "question_evidence"})
        self.assertEqual(req["clarify"]["field"], "environment")
        self.assertEqual(req["clarify"]["question"], "Which environment is this for?")

    def test_clarify_missing_equipment(self):
        req = build({"intent": "equipment_research"})
        self.assertEqual(req["clarify"]["field"], "equipment")

    def test_carried_state(self):
        first = build({"intent": "find_investigations", "preset": "lunar_habitat", "material": "cotton"})
        state = rq.next_state(rq.empty_state(), first)
        nxt = build({"intent": "where_data"}, state=state)
        self.assertEqual(nxt["environment"]["preset"], "lunar_habitat")
        self.assertEqual(nxt["item"]["material"], "cotton")
        self.assertEqual(nxt["sources"]["environment.preset"], "carried")
        new = build({"intent": "where_data"}, extra={"new_topic": True}, state=state)
        self.assertIsNone(new["environment"]["preset"])

    def test_new_environment_does_not_carry_old_numbers(self):
        first = build({"intent": "find_investigations", "preset": "lunar_habitat", "o2_pct": 26.5, "pressure_kpa": 70.0})
        state = rq.next_state(rq.empty_state(), first)
        nxt = build({"intent": "find_investigations", "preset": "iss"}, state=state)
        self.assertEqual((nxt["environment"]["o2_pct"], nxt["environment"]["scenario_id"]), (21.0, "iss"))

    def test_compare_default(self):
        req = build({"intent": "compare_environments", "preset": "iss"})
        self.assertEqual(req["compare_with"][0]["preset"], "lunar_habitat")

    def test_apply_patch(self):
        req = build({"intent": "question_evidence"})
        new = rq.apply_patch(req, {"environment": {"preset": "iss"}}, V)
        self.assertIsNone(new["clarify"])
        self.assertEqual(new["sources"]["environment.preset"], "chip")
        self.assertEqual(llm.validate(new, rq.REQUEST), [])

    def test_dashboard_query_reads_back(self):
        cfg = V["cfg"]
        for values in ({"intent": "find_investigations", "preset": "lunar_habitat", "material": "cotton"},
                       {"intent": "find_investigations", "preset": "iss", "equipment": "detection"},
                       {"intent": "find_investigations", "o2_pct": 34.0, "pressure_kpa": 56.5},
                       {"intent": "find_investigations", "preset": "mars_habitat"}):
            req = build(values)
            q, mism = rq.dashboard_query(req, V)
            self.assertEqual(mism, [], q)
            sc = scorer.interpret(q, cfg)[0]
            if values.get("preset"):
                self.assertEqual(sc.get("preset"), values["preset"])
            if values.get("o2_pct"):
                self.assertEqual(sc["o2_pct"], values["o2_pct"])

    def test_state_schema(self):
        req = build({"intent": "find_investigations", "preset": "iss"})
        st = rq.next_state(None, req, last_list=["PSI-99"])
        self.assertEqual(llm.validate(st, rq.STATE), [])


if __name__ == "__main__":
    unittest.main()
