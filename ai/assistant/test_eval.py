# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests of evaluate.py and record.py with a fake model, writing into a temporary folder. No network."""
import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("AI_NO_MODEL_CALLS", "1")

from ai import config, llm  # noqa: E402
from ai.assistant import evaluate as EV  # noqa: E402

WHY = ""
try:
    from ai.assistant import pipeline  # noqa: F401
    from ai.assistant import check  # noqa: F401
    HAVE_PIPELINE = True
except Exception as exc:  # noqa: BLE001 - reported as the skip reason
    HAVE_PIPELINE, WHY = False, f"{type(exc).__name__}: {exc}"


class QuestionFile(unittest.TestCase):
    def test_schema_and_coverage(self):
        data, errors = EV.load_questions()
        self.assertEqual(errors, [])
        counts, problems = EV.coverage(data)
        self.assertEqual(problems, [])
        self.assertGreaterEqual(counts["questions"], 48)

    def test_design_example_validates(self):
        self.assertEqual(llm.validate(EV.design_block("QUESTIONS", "example"), EV.questions_schema()), [])

    def test_frozen_hash(self):
        now, frozen = EV.freeze_state()
        if frozen is None:
            self.skipTest("questions.sha256 not written yet")
        self.assertEqual(now, frozen, "questions.json changed after it was frozen")

    def test_every_expected_value_is_in_the_vocabulary(self):
        data, _ = EV.load_questions()
        reading = EV.design_block("READING")
        env = reading["properties"]["environment"]["properties"]
        mats = set(reading["properties"]["item"]["properties"]["material"]["enum"])
        intents = set(reading["properties"]["intent"]["enum"])
        presets = set(env["preset"]["enum"])
        equip = set(reading["properties"]["equipment"]["enum"])
        qids = set(reading["properties"]["questions"]["items"]["enum"])
        tools = {"rank_investigations", "counts_per_question", "tested_range", "where_the_data_are", "tests_table",
                 "modelling_data", "equipment_research", "earth_applications", "search_records", "criteria",
                 "files_of_test", "videos_of_test", "investigation_card", "explain"}
        for q in data["questions"]:
            e = q["expect"]
            with self.subTest(q=q["id"]):
                self.assertTrue(set(q["expected_tools"]) <= tools)
                if "intent" in e:
                    self.assertIn(e["intent"], intents)
                if e.get("environment.preset") is not None:
                    self.assertIn(e["environment.preset"], presets)
                if e.get("item.material") is not None:
                    self.assertIn(e["item.material"], mats)
                if e.get("equipment") is not None:
                    self.assertIn(e["equipment"], equip)
                self.assertTrue(set(e.get("questions", [])) <= qids)
                self.assertTrue(set(e.get("environments", [])) <= presets)

    def test_named_tests_and_investigations_exist(self):
        import csv
        with open(config.ROOT / "data/pipeline/tests.csv", encoding="utf-8") as f:
            tests = {r["test_id"] for r in csv.DictReader(f)}
        with open(config.ROOT / "data/catalog/investigations.csv", encoding="utf-8") as f:
            accs = {r["psi_accession"] for r in csv.DictReader(f)}
        data, _ = EV.load_questions()
        for q in data["questions"]:
            for t in q["expect"].get("tests", []):
                self.assertIn(t, tests, q["id"])
            for a in q["expect"].get("investigations", []):
                self.assertIn(a, accs, q["id"])


class Scoring(unittest.TestCase):
    REQ = {"intent": "find_investigations", "environment": {"preset": "lunar_habitat", "o2_pct": 30.0,
           "pressure_kpa": 70.3, "gravity": "lunar", "flow": "ventilated"},
           "compare_with": [{"preset": "iss", "scenario_id": "iss", "label": "ISS cabin"}],
           "item": {"material": "cotton"}, "questions": ["S1"], "term": "Counted test",
           "sources": {"environment.o2_pct": "preset", "environment.pressure_kpa": "message"}}

    def test_preset_filled_values_count_as_empty(self):
        self.assertIsNone(EV.got_value(self.REQ, "environment.o2_pct"))
        self.assertEqual(EV.got_value(self.REQ, "environment.pressure_kpa"), 70.3)
        self.assertTrue(EV.score_field("environment.o2_pct", None, None))
        self.assertFalse(EV.invented("environment.o2_pct", None, None))
        self.assertTrue(EV.invented("environment.pressure_kpa", None, 70.3))

    def test_sets_numbers_terms(self):
        self.assertEqual(EV.got_value(self.REQ, "environments"), ["iss", "lunar_habitat"])
        self.assertTrue(EV.score_field("environments", ["lunar_habitat", "iss"], ["iss", "lunar_habitat"]))
        self.assertTrue(EV.score_field("environment.pressure_kpa", 70, 70.3))
        self.assertFalse(EV.score_field("environment.pressure_kpa", 69, 70.3))
        self.assertTrue(EV.score_field("term", "counted test", "Counted test"))
        self.assertTrue(EV.score_field("asks_verdict", False, False))
        self.assertFalse(EV.score_field("asks_verdict", False, None))


class Reuse(unittest.TestCase):
    def test_equal_calls_are_reused_and_logged(self):
        with tempfile.TemporaryDirectory() as d:
            fake = EV.SchemaFake()
            chat = EV.ReuseChat(fake, "assistant_eval_test", log_dir=d)
            schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}
            msgs = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
            r1 = chat(msgs, schema, think="low", temperature=0, seed=7, log_extra={"step": "x"})
            r2 = chat(msgs, schema, think="low", temperature=0, seed=7, log_extra={"step": "x"})
            r3 = chat(msgs, schema, think="low", temperature=0, seed=23, log_extra={"step": "x"})
            self.assertEqual((chat.calls, chat.reused), (2, 1))
            self.assertTrue(r2.get("reused"))
            self.assertEqual(r1["data"], r2["data"])
            self.assertFalse(r3.get("reused", False))
            lines = (Path(d) / "assistant_eval_test.jsonl").read_text().splitlines()
            self.assertIn("_meta", json.loads(lines[0]))
            self.assertEqual(json.loads(lines[1])["kind"], "reused")

    def test_cache_refills_from_a_call_log(self):
        with tempfile.TemporaryDirectory() as d:
            schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}
            msgs = [{"role": "user", "content": "u"}]
            kw = {"think": "low", "temperature": 0, "seed": 7}
            psha = EV.call_key(msgs, schema, kw).split("|")[0]
            rec = {"kind": "call", "valid": True, "prompt_sha256": psha, "options": EV._options(kw), "think": "low",
                   "format_mode": "schema", "model": config.MODEL, "parsed": {"a": "logged"}}
            log = Path(d) / "r.jsonl"
            log.write_text(json.dumps({"_meta": {}}) + "\n" + json.dumps(rec) + "\n")
            chat = EV.ReuseChat(EV.SchemaFake(), "r", log_dir=d)
            self.assertEqual(chat.load_log(log), 1)
            self.assertEqual(chat(msgs, schema, **kw)["data"], {"a": "logged"})
            self.assertEqual(chat.calls, 0)

    def test_fake_matches_schema(self):
        for name in ("READING", "WRITE", "CHECK"):
            schema = EV.design_block(name)
            res = EV.SchemaFake()([{"role": "user", "content": "[F1] (ctx) A fact."}], schema)
            self.assertEqual(llm.validate(res["data"], schema), [], name)


@unittest.skipUnless(HAVE_PIPELINE, f"the pipeline is not importable yet ({WHY})")
class EndToEnd(unittest.TestCase):
    def test_evaluate_with_fake_model(self):
        with tempfile.TemporaryDirectory() as d:
            p = EV.run(arms=("single_call", "full", "no_gates"), only=["q01", "q64", "q51", "q54"], fake=True,
                       out_dir=d, allow_changed=True, quiet=True)
            self.assertFalse(p["complete"])
            out = json.loads((Path(d) / "assistant_eval.json").read_text())
            self.assertIn("_meta", out)
            self.assertEqual(out["_meta"]["language_model_used_at_build"], config.NO_MODEL)
            for arm in ("single_call", "full", "no_gates"):
                m = out["arms"][arm]["metrics"]
                for k in ("reading_accuracy", "invented_values", "plan_exact", "plan_jaccard", "asks_correct",
                          "asks_unneeded", "refusals_correct", "not_in_files_correct", "out_of_scope_correct",
                          "sentences_shown", "citation_valid", "numbers_unsupported", "forbidden_wording",
                          "quote_errors", "name_errors", "language_errors", "removed", "repaired", "checker_no",
                          "fallback_rate", "seconds_per_turn", "model_calls_per_turn", "injection_resisted"):
                    self.assertIn(k, m)
                self.assertLessEqual(m["model_calls_per_turn"]["max"], 4)
                ids = [r["id"] for r in out["arms"][arm]["per_question"]]
                self.assertEqual(ids, ["q01", "q51", "q54", "q64"])
            self.assertTrue((Path(d) / "eval_progress.json").exists())
            self.assertTrue(list(Path(d).glob("assistant_eval_*.jsonl")))
            # resume: nothing is run again
            p2 = EV.run(arms=("full",), only=["q01"], fake=True, out_dir=d, allow_changed=True, quiet=True)
            self.assertEqual(p2["model_calls_made"], 0)
            md = EV.report(Path(d) / "assistant_eval.json", Path(d) / "evaluation.md")
            self.assertIn("| Measure |", Path(md).read_text())

    def test_record_with_fake_model(self):
        from ai.assistant import record as RC
        with tempfile.TemporaryDirectory() as d:
            try:
                p = RC.record(only=["lunar_cotton"], fake=True, out_dir=d, quiet=True)
            except SystemExit as exc:
                self.fail(f"record refused: {exc}")
            self.assertEqual(len(p["conversations"][0]["turns"]), 2)
            out = json.loads((Path(d) / "assistant_recorded.json").read_text())
            for t in out["conversations"][0]["turns"]:
                self.assertEqual(t["response"]["mode"], "recorded")
                self.assertEqual(llm.validate(t["response"], EV.design_block("RESPONSE")), [])


if __name__ == "__main__":
    unittest.main()
