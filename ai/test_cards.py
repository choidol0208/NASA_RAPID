# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for the card writer (ai/apply_cards.py), the reviewed removals (ai/review/pm_prereview.json) and
ai/build_all.py. No model is called: the cards are rebuilt from the logged candidates in ai/runs/.

    python3 -m unittest -v ai.test_cards
"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ai import apply_cards as A, build_all, checks as C, config, evidence as evmod, llm

ROOT = config.ROOT
CARDS = config.INSIGHTS_DIR / "cards.json"
QUALITY = config.INSIGHTS_DIR / "quality.json"
PSI159 = ("The record hypothesizes that testing aboard the ISS can demonstrate the first-time improvement in "
          "understanding cool flame kinetics.")


def quiet(*a, **k):
    return None


class Built(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ev = evmod.load()
        cls.res = A.build(log=quiet)
        cls.cards = {c["investigation_id"]: c for c in cls.res["cards"]}


class EvidenceQuoteTest(Built):
    def _check(self, cards):
        n = 0
        for c in cards:
            inv = c["investigation_id"]
            for s in c["sentences"]:
                for e in s["evidence"]:
                    u = evmod.unit(inv, e["id"], self.ev)
                    self.assertIn(e["quote"], u["text"], (inv, e["id"]))       # a verbatim substring of its unit
                    self.assertEqual(e["quote"], u["text"], (inv, e["id"]))    # in fact the whole unit, taken by code
                    field = json.loads((config.PSI_CATALOG_DIR / f"{inv}.json").read_text(encoding="utf-8"))[u["field"]]
                    self.assertEqual(field[e["char_start"]:e["char_end"]], e["quote"], (inv, e["id"]))
                    n += 1
        return n

    def test_every_stored_quote_is_verbatim_text_of_its_unit_built(self):
        self.assertGreater(self._check(self.res["cards"]), 0)

    def test_every_stored_quote_is_verbatim_text_of_its_unit_on_disk(self):
        if not CARDS.exists():
            self.skipTest("run python3 ai/build_all.py first")
        self.assertGreater(self._check(json.loads(CARDS.read_text(encoding="utf-8"))), 0)

    def test_the_two_clipped_quotes_found_by_the_verifier(self):
        # PSI-22 sentence 1 and PSI-69 sentence 2: the model's copy was cut mid-sentence with a full stop added
        for inv, n in (("PSI-22", 1), ("PSI-69", 2)):
            s = next(x for x in self.cards[inv]["sentences"] if x["origin"] == "model" and x["n"] == n)
            e = s["evidence"][0]
            self.assertNotEqual(e["model_quote"], e["quote"])
            self.assertEqual(e["quote"], evmod.unit(inv, e["id"], self.ev)["text"])

    def test_check_all_regates_with_the_model_quote(self):
        for c in self.res["cards"]:
            for s in c["sentences"]:
                if s["origin"] != "model":
                    continue
                res = C.check_sentence(s["text"], A.regate_evidence(s["evidence"]), c["investigation_id"], self.ev)
                self.assertTrue(res["ok"], (c["investigation_id"], res["reasons"]))
                self.assertEqual(res["checks"], s["checks"])


class PrereviewTest(Built):
    def test_listed_sentence_is_removed_and_its_slot_is_the_nasa_quote(self):
        c = self.cards["PSI-159"]
        texts = [s["text"] for s in c["sentences"] if s["origin"] == "model"]
        self.assertFalse(any(PSI159 in t for t in texts))
        self.assertNotIn(PSI159, c["summary"])
        self.assertEqual(c["status"], "generated_partial")
        self.assertTrue(c["ai_generated"])
        self.assertIsNone(c["reviewed_by"])
        slot = next(s for s in c["sentences"] if s.get("replaces"))
        self.assertEqual((slot["origin"], slot["role"], slot["field_label"]), ("quote", "summary", "Stated hypothesis:"))
        u = evmod.unit("PSI-159", "HYP-1", self.ev)
        self.assertEqual(slot["text"], u["text"])
        self.assertIn(f'Stated hypothesis: "{u["text"]}"', c["summary"])
        self.assertIn("can demonstrate the following for the first time", c["summary"])
        # the quoted unit is not repeated as a key point
        self.assertFalse(any(u["text"] in k["text"] for k in c["key_points"]))
        self.assertEqual(c["removed_before_review"][0]["reviewer_kind"], "ai_session_pm")

    def test_every_listed_removal_shows_the_quoted_unit_it_cited_first(self):
        """The careful-reader removals (PSI-26, PSI-99, PSI-117) behave like the PSI-159 one: the sentence is
        gone, its slot is the verbatim unit with its field label, and the card says who removed it."""
        for e in A.load_prereview():
            c = self.cards[e["investigation_id"]]
            body, _, _ = C.split_source_suffix(e["sentence"])
            self.assertNotIn(body, c["summary"], e["investigation_id"])
            self.assertFalse(any(body in s["text"] for s in c["sentences"] if s["origin"] == "model"))
            self.assertIn(c["status"], ("generated_partial", "fallback_quote"))
            removed = [r for r in c["removed_before_review"] if body in r["sentence"]]
            self.assertEqual(len(removed), 1, e["investigation_id"])
            self.assertEqual(removed[0]["reviewer_kind"], "ai_session_pm")
            slot = next(s for s in c["sentences"] if s.get("replaces") and s["replaces"]["n"] == removed[0]["n"])
            self.assertEqual(slot["origin"], "quote")
            unit = evmod.unit(e["investigation_id"], slot["evidence"][-1]["id"], self.ev)
            self.assertIn(unit["text"], slot["text"])
            self.assertIn(f'{slot["field_label"]} "{slot["text"]}"', c["summary"])
            self.assertIsNone(c["reviewed_by"])

    def test_counted_apart_from_the_review(self):
        st = self.res["stats"]
        # every entry of ai/review/pm_prereview.json removes exactly one sentence (4 entries on 14 Nov after
        # the careful-reader pass: PSI-159, PSI-26, PSI-99, PSI-117); the count follows the file
        entries = A.load_prereview()
        self.assertGreaterEqual(len(entries), 1)
        self.assertEqual(st["removed_by_prereview"], len(entries))
        self.assertEqual(st["removed_by_review"], 0)
        self.assertEqual(st["prereview_unmatched"], [])
        if QUALITY.exists():
            q = json.loads(QUALITY.read_text(encoding="utf-8"))
            self.assertEqual(q["removed_before_review"]["n"], len(entries))
            self.assertEqual(q["removed_before_review"]["reviewer_kind"], "ai_session_pm")
            self.assertEqual(q["reviewed_ai_session"] + q["reviewed_person"], q["n"])

    def test_file_shape_is_validated(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "pre.json"
            p.write_text(json.dumps([{"investigation_id": "PSI-159", "sentence": PSI159, "reason": "x",
                                      "reviewer_kind": "person"}]), encoding="utf-8")
            with self.assertRaises(SystemExit):
                A.load_prereview(p)
            p.write_text(json.dumps({"investigation_id": "PSI-159"}), encoding="utf-8")
            with self.assertRaises(SystemExit):
                A.load_prereview(p)
            self.assertEqual(A.load_prereview(Path(d) / "missing.json"), [])

    def test_a_new_entry_removes_a_sentence_and_only_that_one(self):
        c = self.cards["PSI-25"]
        first = next(s for s in c["sentences"] if s["origin"] == "model")
        body, _, _ = C.split_source_suffix(first["text"])
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "pre.json"
            p.write_text(json.dumps([{"investigation_id": "PSI-25", "sentence": body, "reason": "test",
                                      "reviewer_kind": "ai_session_pm"}]), encoding="utf-8")
            res = A.build(log=quiet, ctx=self.res["ctx"], prereview_path=p)
        c2 = next(x for x in res["cards"] if x["investigation_id"] == "PSI-25")
        n_before = sum(s["origin"] == "model" for s in c["sentences"])
        self.assertEqual(sum(s["origin"] == "model" for s in c2["sentences"]), n_before - 1)
        self.assertNotIn(first["text"], c2["summary"])
        self.assertEqual(res["stats"]["removed_by_prereview"], 1)
        # PSI-159 is back, since this file does not list it
        c159 = next(x for x in res["cards"] if x["investigation_id"] == "PSI-159")
        self.assertIn(PSI159, c159["summary"])


class LabelsTest(Built):
    def test_ai_generated_exactly_when_a_model_sentence_is_shown(self):
        for c in self.res["cards"]:
            n = sum(s["origin"] == "model" for s in c["sentences"])
            self.assertEqual(c["ai_generated"], n > 0, c["investigation_id"])
            if c["status"] == "fallback_quote":
                self.assertEqual(n, 0)


class BuildAllTest(unittest.TestCase):
    def test_order_of_the_steps(self):
        cmds = [cmd[0] for _, cmd in build_all.steps()]
        self.assertEqual(cmds, ["ai/evidence.py", "ai/build_baseline.py", "ai/evidence_map.py", "ai/apply_cards.py",
                                "ai/audit_catalog.py", "ai/apply_review.py", "ai/check_all.py"])
        self.assertTrue(all("--repair" not in cmd for _, cmd in build_all.steps()))
        self.assertIn("--final", dict(build_all.steps(final=True))["check"])
        self.assertEqual(build_all.NO_CALLS_ENV, llm.NO_CALLS_ENV)

    def test_no_model_call_while_the_variable_is_set(self):
        with mock.patch.dict(os.environ, {llm.NO_CALLS_ENV: "1"}):
            with mock.patch("urllib.request.urlopen") as op:
                with self.assertRaises(llm.ModelCallsDisabled):
                    llm._http("GET", "/api/tags")
                op.assert_not_called()

    def test_header_comment(self):
        for f in ("build_all.py", "test_cards.py", "apply_cards.py"):
            first = (config.AI_DIR / f).read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(first, config.HEADER_COMMENT)


if __name__ == "__main__":
    unittest.main()
