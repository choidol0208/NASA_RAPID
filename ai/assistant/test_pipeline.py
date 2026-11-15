# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for one turn (ai/assistant/pipeline.py) with FakeChat. No network, no model.

    python3 -m unittest ai.assistant.test_pipeline -v
"""
import os
import unittest
from unittest import mock

from ai import llm
from ai.assistant import contract, pipeline, request as rq, texts
from ai.assistant.fake_model import FakeChat
from ai.assistant.testkit import checker, echo_writer, reading

LUNAR = "Which NASA experiments are closest to a cotton fabric fire in a lunar habitat?"
LUNAR_READ = reading(preset="lunar_habitat", material="cotton", words="cotton fabric", english=LUNAR)


def turn(msg, script, state=None, **kw):
    chat = FakeChat(script)
    with mock.patch.dict(os.environ, {llm.NO_CALLS_ENV: "0"}):
        r = pipeline.turn(msg, state, chat=chat, mode=kw.pop("mode", "live"), use_cache=kw.pop("use_cache", False),
                          log_dir=None, **kw)
    return r, chat


class FullTurnTest(unittest.TestCase):
    def test_full_turn_within_budget(self):
        r, chat = turn(LUNAR, {"understand_1": [LUNAR_READ], "understand_2": [LUNAR_READ],
                               "write": [echo_writer(2)], "check": [checker()]})
        self.assertEqual(contract.validate_response(r), [])
        self.assertEqual(r["kind"], "answer")
        self.assertLessEqual(r["trace"]["model_calls"], 4)
        self.assertEqual(r["answer"]["origin"], "model")
        self.assertEqual(r["label"], texts.ANSWER_LABELS["model"])
        self.assertEqual([s["step"] for s in r["trace"]["steps"]],
                         ["understand", "plan", "lookup", "write", "check", "deliver"])
        ids = {f["id"] for f in r["facts"]}
        for s in r["answer"]["sentences"]:
            self.assertTrue(set(s["facts"]) <= ids)
        self.assertEqual(r["dashboard"]["q"], "lunar habitat cotton")
        for c in chat.calls:
            self.assertEqual(c["options"]["retries"], 0)
            self.assertEqual(c["options"]["num_ctx"], 16384)

    def test_m2_skipped_when_m1_equals_rules_then_repair_runs(self):
        msg = "Where are the raw files of the tests for the ISS?"
        m1 = reading(intent="where_data", preset="iss", english=msg)
        r, chat = turn(msg, {"understand_1": [m1], "write": [echo_writer(2, bad="Cotton is safe on the ISS.")],
                             "repair": [echo_writer(2)], "check": [checker()]})
        self.assertNotIn("understand_2", chat.steps())
        self.assertIn("repair", chat.steps())
        self.assertEqual(r["trace"]["model_calls"], 4)
        self.assertTrue(any(x["by"] == "policy" for x in r["answer"]["removed"]))
        self.assertEqual(r["answer"]["origin"], "model")

    def test_no_repair_after_two_readings(self):
        r, chat = turn(LUNAR, {"understand_1": [LUNAR_READ], "understand_2": [LUNAR_READ],
                               "write": [echo_writer(3, bad="Cotton is safe in a lunar habitat.")], "check": [checker()]})
        self.assertNotIn("repair", chat.steps())
        self.assertEqual(r["trace"]["gate_report"]["removed_by_gate"].get("policy"), 1)

    def test_checker_no_removes(self):
        r, chat = turn(LUNAR, {"understand_1": [LUNAR_READ], "understand_2": [LUNAR_READ],
                               "write": [echo_writer(3)], "check": [checker(no_for=(3,))]})
        self.assertEqual(r["trace"]["gate_report"]["checker_no"], 1)
        self.assertTrue(any(x["by"] == "checker" for x in r["answer"]["removed"]))
        self.assertEqual(len(r["answer"]["sentences"]), 2)

    def test_fallback_on_invalid_write(self):
        r, chat = turn(LUNAR, {"understand_1": [LUNAR_READ], "understand_2": [LUNAR_READ], "write": ["invalid"]})
        self.assertEqual(r["answer"]["origin"], "template")
        self.assertTrue(any(n["id"] == "fallback" for n in r["notices"]))
        self.assertEqual(r["label"], texts.ANSWER_LABELS["template"])
        self.assertTrue(r["answer"]["sentences"])

    def test_fallback_on_timeout_of_checker(self):
        r, chat = turn(LUNAR, {"understand_1": [LUNAR_READ], "understand_2": [LUNAR_READ],
                               "write": [echo_writer(2)], "check": ["timeout"]})
        self.assertEqual(r["answer"]["origin"], "template")
        self.assertEqual(r["trace"]["gate_report"]["fallback_reason"], "check failed")

    def test_clarify_ends_after_understand(self):
        msg = "Which NASA experiments matter for my design?"
        rd = reading(intent="question_evidence", english=msg)
        r, chat = turn(msg, {"understand_1": [rd], "understand_2": [rd]})
        self.assertEqual(r["kind"], "clarify")
        self.assertEqual(r["clarify"]["question"], texts.CLARIFY["environment"])
        self.assertEqual(r["facts"], [])
        self.assertNotIn("write", chat.steps())
        self.assertEqual(r["state"]["pending_clarify"]["field"], "environment")
        self.assertEqual(contract.validate_response(r), [])
        # the option answers it without a model
        opt = r["clarify"]["options"][0]
        r2, chat2 = turn(None, {}, state=r["state"], request=r["request"], patch=opt["patch"], mode="no_model")
        self.assertEqual(r2["kind"], "answer")
        self.assertEqual(r2["request"]["environment"]["preset"], opt["patch"]["environment"]["preset"])

    def test_refusal_notice(self):
        msg = "Is cotton safe in a lunar habitat?"
        rd = reading(intent="question_evidence", preset="lunar_habitat", material="cotton", verdict=True, english=msg)
        r, chat = turn(msg, {"understand_1": [rd], "understand_2": [rd], "write": [echo_writer(2)],
                             "check": [checker()]})
        self.assertEqual(r["notices"][0]["id"], "refuse_verdict")
        self.assertEqual(r["notices"][0]["text"], texts.NOTICES["refuse_verdict"])

    def test_refusal_without_model(self):
        r, _ = turn("Is cotton safe in a lunar habitat?", {}, mode="no_model")
        self.assertEqual([n["id"] for n in r["notices"]][:1], ["refuse_verdict"])
        self.assertIn("no_model", [n["id"] for n in r["notices"]])

    def test_prediction_notice_and_range(self):
        msg = "What would happen to cotton at 40% oxygen?"
        rd = reading(intent="question_evidence", preset="lunar_habitat", material="cotton", o2=40, prediction=True,
                     english=msg)
        r, _ = turn(msg, {"understand_1": [rd], "understand_2": [rd], "write": [echo_writer(2)], "check": [checker()]})
        self.assertIn("refuse_prediction", [n["id"] for n in r["notices"]])
        self.assertIn("tested_range", [t["tool"] for t in r["trace"]["steps"][1]["detail"]["tools"]])

    def test_not_in_files(self):
        msg = "Which tests are close to lithium battery cells in a lunar habitat?"
        rd = reading(preset="lunar_habitat", words="lithium battery cells", english=msg)
        r, _ = turn(msg, {"understand_1": [rd], "understand_2": [rd], "write": [echo_writer(2)], "check": [checker()]})
        self.assertIn("not_in_files", [n["id"] for n in r["notices"]])

    def test_named_test_needs_no_environment(self):
        r, _ = turn("Where are the raw files for FLEX-21?", {}, mode="no_model")
        self.assertEqual(r["kind"], "answer")
        self.assertEqual([t["tool"] for t in r["trace"]["steps"][1]["detail"]["tools"]], ["files_of_test"])
        self.assertIn("FLEX-21", r["answer"]["sentences"][0]["text"])

    def test_out_of_scope_and_help(self):
        r, _ = turn("How do rocket engines burn propellant?", {}, mode="no_model")
        self.assertEqual(r["kind"], "out_of_scope")
        self.assertEqual(r["notices"][0]["text"], texts.NOTICES["out_of_scope"])
        r, _ = turn("hello", {}, mode="no_model")
        self.assertEqual(r["kind"], "help")

    def test_no_model_mode_makes_no_call(self):
        r, chat = turn(LUNAR, {"understand_1": [LUNAR_READ]}, mode="no_model")
        self.assertEqual(chat.calls, [])
        self.assertEqual(r["trace"]["model_calls"], 0)
        self.assertEqual(r["answer"]["origin"], "template")
        self.assertEqual(r["trace"]["steps"][0]["summary"], texts.SUMMARY["understand_no_model"])

    def test_env_var_forces_no_model(self):
        chat = FakeChat({})
        with mock.patch.dict(os.environ, {llm.NO_CALLS_ENV: "1"}):
            r = pipeline.turn(LUNAR, None, chat=chat, mode="live", use_cache=False, log_dir=None)
        self.assertEqual(r["mode"], "no_model")
        self.assertEqual(chat.calls, [])

    def test_cache_hit_makes_no_call(self):
        pipeline.cache_clear()
        script = {"understand_1": [LUNAR_READ], "understand_2": [LUNAR_READ], "write": [echo_writer(2)],
                  "check": [checker()]}
        r1, c1 = turn(LUNAR, script, use_cache=True)
        r2, c2 = turn(LUNAR, script, use_cache=True)
        self.assertEqual(r1["trace"]["cache"], "miss")
        self.assertEqual(r2["trace"]["cache"], "hit")
        self.assertEqual(c2.calls, [])
        self.assertEqual(r2["trace"]["model_calls"], 0)
        self.assertEqual(r2["answer"], r1["answer"])

    def test_template_answer_mode(self):
        req = rq.build_request({"intent": "find_investigations", "preset": "iss", "material": None, "o2_pct": None,
                                "pressure_kpa": None, "gravity": None, "equipment": None, "questions": [],
                                "investigations": [], "asks_verdict": False, "asks_prediction": False}, {},
                               norm_extra={"english": "ISS"}, state=None, vocab=rq.load_vocab())
        r, chat = turn(None, {}, request=req, answer_mode="template")
        self.assertEqual(chat.calls, [])
        self.assertEqual(r["answer"]["origin"], "template")
        self.assertEqual(r["trace"]["steps"][0]["summary"], texts.SUMMARY["understand_set"])

    def test_follow_up_carries_state(self):
        r1, _ = turn(LUNAR, {}, mode="no_model")
        rd = reading(intent="find_investigations", preset="iss", new_topic=False, english="And for the ISS?")
        r2, _ = turn("And for the ISS?", {"understand_1": [rd], "understand_2": [rd], "write": [echo_writer(2)],
                                          "check": [checker()]}, state=r1["state"])
        self.assertEqual(r2["request"]["environment"]["preset"], "iss")
        self.assertEqual(r2["request"]["item"]["material"], "cotton")
        self.assertEqual(r2["state"]["turn"], 2)


class CleanupTest(unittest.TestCase):
    def test_clean_text(self):
        self.assertEqual(pipeline.clean_text("ACME BRE (PSI\u201120) at 26.5\u202f% O\u2082 (F1, F2)."),
                         "ACME BRE (PSI-20) at 26.5 % O2.")

    def test_back_reference_to_removed_sentence(self):
        def writer(messages, schema):
            base = echo_writer(1)(messages, schema)
            base["sentences"] = [{"text": "Cotton is safe in a lunar habitat.", "facts": ["F1"]},
                                 {"text": "Of those, SAFFIRE-II (PSI-99) is listed by the team's ranking.", "facts": ["F1"]}] + base["sentences"]
            return base
        r, _ = turn(LUNAR, {"understand_1": [LUNAR_READ], "understand_2": [LUNAR_READ], "write": [writer],
                            "check": [checker()]})
        texts_ = [s["text"] for s in r["answer"]["sentences"]]
        self.assertNotIn("Of those, SAFFIRE-II (PSI-99) is listed by the team's ranking.", texts_)
        self.assertIn("length", [x["by"] for x in r["answer"]["removed"]])


class ArmsTest(unittest.TestCase):
    def script(self):
        return {"understand_1": [LUNAR_READ], "understand_2": [LUNAR_READ], "write": [echo_writer(2)],
                "repair": [echo_writer(2)], "check": [checker()], "baseline": [lambda m, s: {
                    "intent": "find_investigations", "asks_verdict": False, "asks_prediction": False,
                    "environment": LUNAR_READ["environment"], "item": LUNAR_READ["item"], "questions": [],
                    "sentences": [{"text": "Cotton fabric is safe here.", "facts": []}], "followups": []}]}

    def test_no_repeat(self):
        r, chat = turn(LUNAR, self.script(), arm="no_repeat")
        self.assertNotIn("understand_2", chat.steps())

    def test_no_checker(self):
        r, chat = turn(LUNAR, self.script(), arm="no_checker")
        self.assertNotIn("check", chat.steps())
        self.assertEqual(r["answer"]["origin"], "model")

    def test_no_gates_reports_only(self):
        r, chat = turn(LUNAR, {"understand_1": [LUNAR_READ], "understand_2": [LUNAR_READ],
                               "write": [echo_writer(2, bad="Cotton is safe in a lunar habitat.")],
                               "check": [checker()]}, arm="no_gates")
        self.assertIn("Cotton is safe in a lunar habitat.", [s["text"] for s in r["answer"]["sentences"]])
        self.assertTrue(r["trace"]["gate_report"]["sentences"][0]["failures"])

    def test_single_call(self):
        r, chat = turn(LUNAR, self.script(), arm="single_call")
        self.assertEqual(chat.steps(), ["baseline"])
        self.assertEqual(r["answer"]["sentences"][0]["text"], "Cotton fabric is safe here.")
        self.assertTrue(r["trace"]["gate_report"]["report_only"])
        self.assertEqual(contract.validate_response(r), [])


if __name__ == "__main__":
    unittest.main()
