# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for the code gates (ai/assistant/check.py): every gate with a passing and a failing sentence, the fixed
texts and the template answers. No network, no model.

    python3 -m unittest ai.assistant.test_check -v
"""
import unittest

from ai.assistant import check as ck, texts, tools, write
from ai.assistant.test_tools import D


def F(text, fid="F1", context=None, quote=False, kind="statement", field=None, source_keys=()):
    return {"id": fid, "context": context, "text": text, "numbers": [], "kind": kind, "quote": quote, "field": field,
            "source_keys": list(source_keys), "lead": False, "limit": False}


RANGE = F("Solid-fuel tests in the team's tables: oxygen of the surrounding atmosphere recorded for 139 of 376, "
          "from 13.6 to 22.2%; your 30% is above the highest recorded value.")
RANK = F("Closest to this input by the team's ranking, in order: SAFFIRE-II (PSI-99), SAFFIRE-I (PSI-98), ACME BRE "
         "(PSI-20).", "F2")
AIM = F('BASS-II (PSI-25) record, stated objective: "Study the ignition, flame growth, flame spread, and extinction '
        'limits for solid fuels burning in low-velocity forced flows in microgravity."', "F3", quote=True,
        kind="nasa_sentence", field="objective")
HEDGED = F('ACME BRE (PSI-20) record, impact statement: "The results may improve material flammability tests."', "F4",
           quote=True, kind="nasa_sentence", field="researchImpacts")
STREAM = F("63 gas-flame tests record the oxygen of an oxidizer stream (an inverse flame), not of a surrounding "
           "atmosphere; they are left out of the oxygen span.", "F5", source_keys=["pipeline/spec/sources.json#cfig_inverse"])
REQ = {"environment": {"label": "Lunar base or pressurized rover"}, "english": "cotton in a lunar habitat",
       "item": {"label": "cotton"}}


def gates(text, cited, ids=None):
    return [g for g, _ in ck.gate_sentence(text, cited, REQ, {"F1", "F2", "F3", "F4", "F5"}, cited_ids=ids)]


class GateTest(unittest.TestCase):
    GOOD = "Solid-fuel tests in the team's tables record oxygen from 13.6 to 22.2%, below the 30% of this environment."

    def test_good_sentence_passes(self):
        self.assertEqual(gates(self.GOOD, [RANGE]), [])

    def test_cites(self):
        self.assertIn("cites", gates(self.GOOD, [RANGE], ids=["F9"]))
        self.assertIn("cites", gates(self.GOOD, [RANGE], ids=[]))
        self.assertIn("cites", gates(self.GOOD, [RANGE], ids=["F1", "F2", "F3", "F4", "F5"]))

    def test_numbers(self):
        self.assertIn("numbers", gates("Solid-fuel tests record oxygen up to 23.5%.", [RANGE]))
        self.assertIn("numbers", gates("Solid-fuel tests record oxygen up to 22.2 kPa.", [RANGE]))
        self.assertIn("numbers", gates("Twice as many solid-fuel tests record oxygen.", [RANGE]))
        self.assertIn("numbers", gates("Seven solid-fuel tests record oxygen.", [RANGE]))
        self.assertNotIn("numbers", gates("Of 376 solid-fuel tests, 139 record oxygen.", [RANGE]))
        self.assertNotIn("numbers", gates("Solid-fuel tests record oxygen from 13.6% to 22.2%.", [RANGE]))
        self.assertIn("numbers", gates("Solid-fuel tests record 376% oxygen.", [RANGE]))
        req = {"environment": {"o2_pct": 26.5, "pressure_kpa": 70.0}, "sources": {"environment.o2_pct": "message",
               "environment.pressure_kpa": "message"}}
        self.assertEqual(ck.g_numbers("The team's ranking for a 26.5% oxygen, 70 kPa cabin lists SAFFIRE-II.", [RANK],
                                      req), None)
        self.assertIsNotNone(ck.g_numbers("The team's ranking for a 26.5% oxygen cabin lists SAFFIRE-II.", [RANK]))

    def test_quotes(self):
        ok = 'The BASS-II (PSI-25) record states the aim to "study the ignition, flame growth, flame spread".'
        self.assertNotIn("quotes", gates(ok, [AIM]))
        bad = 'The BASS-II (PSI-25) record states that it aims to "measure the smoke of cotton".'
        self.assertIn("quotes", gates(bad, [AIM]))

    def test_names(self):
        self.assertNotIn("names", gates("The team's ranking lists SAFFIRE-II (PSI-99) and SAFFIRE-I (PSI-98).", [RANK]))
        self.assertIn("names", gates("The team's ranking lists FLEX (PSI-69) beside SAFFIRE-II (PSI-99).", [RANK]))
        self.assertIn("names", gates("The team's ranking lists SAFFIRE-II (PSI-99) for a Mars rover.", [RANK]))
        self.assertNotIn("names", gates("For a lunar habitat the team's ranking lists SAFFIRE-II (PSI-99).", [RANK]))

    def test_policy(self):
        self.assertIn("policy", gates("Cotton is safe at 30% oxygen in this environment.", [RANGE]))
        self.assertNotIn("policy", gates(self.GOOD, [RANGE]))

    def test_wording(self):
        self.assertIn("wording", gates("Solid-fuel tests have covered oxygen from 13.6 to 22.2%.", [RANGE]))
        self.assertIn("wording", gates("Cotton would burn at 30% oxygen in these tests.", [RANGE]))

    def test_banned(self):
        self.assertIn("banned", gates("SAFFIRE-II (PSI-99) is the best match by the team's ranking.", [RANK]))
        self.assertNotIn("banned", gates("SAFFIRE-II (PSI-99) is listed by the team's ranking.", [RANK]))

    def test_lint(self):
        bad = "In microgravity, flames are more dangerous than on Earth because there is no buoyancy."
        self.assertIn("lint", gates(bad, [F(bad)]))
        self.assertNotIn("lint", gates(self.GOOD, [RANGE]))

    def test_need_names_are_labels_for_the_linter(self):
        t = ("None of the 2 counted tests for flame spread and growth (P3) were recorded with oxygen and pressure "
             "inside the lunar base ranges.")
        self.assertNotIn("lint", gates(t, [F(t)]))
        self.assertIn("lint", gates("Flames spread faster in a lunar base.", [F("Flames spread faster in a lunar base.")]))

    def test_extra(self):
        self.assertIn("extra", gates("Solid-fuel tests from 13.6 to 22.2% oxygen, covering your 30%.", [RANGE]))
        self.assertIn("extra", gates("The 139 solid-fuel tests are validated by NASA.", [RANGE]))
        self.assertIn("extra", gates("The solid-fuel tests are representative of this cabin.", [RANGE]))
        self.assertNotIn("extra", gates(self.GOOD, [RANGE]))

    def test_length(self):
        self.assertIn("length", gates("Solid-fuel tests record oxygen from 13.6 to 22.2%", [RANGE]))
        self.assertIn("length", gates("Solid-fuel tests record oxygen. They stop at 22.2%.", [RANGE]))
        long = "Solid-fuel tests " + "in the team's tables " * 9 + "record oxygen."
        self.assertIn("length", gates(long, [RANGE]))

    def test_english(self):
        self.assertIn("english", gates("고체 연료 시험은 산소 13.6 to 22.2%를 기록합니다.", [RANGE]))
        self.assertNotIn("english", gates(self.GOOD, [RANGE]))

    def test_inverse(self):
        self.assertIn("inverse", gates("63 gas-flame tests are left out of the oxygen span.", [STREAM]))
        self.assertNotIn("inverse", gates("63 gas-flame tests of an inverse flame are left out of the oxygen span.",
                                          [STREAM]))

    def test_attribution_needs_record_text(self):
        self.assertIn("modality", gates("The record states that solid-fuel tests record oxygen from 13.6 to 22.2%.",
                                        [RANGE]))
        self.assertNotIn("names", gates("For lunar habitats the team's ranking lists SAFFIRE-II (PSI-99).", [RANK]))

    def test_hypothesis_stays_a_hypothesis(self):
        hyp = F('SAME (PSI-102) record, stated hypothesis: "It is hypothesized that smokes produced in microgravity '
                'will exhibit larger droplet sizes."', "F3", quote=True, kind="nasa_sentence", field="hypothesis")
        self.assertIn("modality", gates("The SAME (PSI-102) record states that smokes in microgravity exhibit larger "
                                        "droplet sizes.", [hyp]))
        self.assertNotIn("modality", gates("The SAME (PSI-102) record hypothesizes that smokes in microgravity will "
                                           "exhibit larger droplet sizes.", [hyp]))

    def test_modality(self):
        self.assertIn("modality", gates("BASS-II (PSI-25) found the extinction limits for solid fuels.", [AIM]))
        self.assertNotIn("modality", gates("The BASS-II (PSI-25) record states the aim to study extinction limits for "
                                           "solid fuels.", [AIM]))

    def test_hedge(self):
        self.assertIn("hedge", gates("The ACME BRE (PSI-20) record states that the results improve flammability tests.",
                                     [HEDGED]))
        self.assertNotIn("hedge", gates("The ACME BRE (PSI-20) record states that the results may improve flammability "
                                        "tests.", [HEDGED]))
        self.assertIn("hedge", gates("Solid-fuel tests will always stop at 22.2%.", [RANGE]))


class FixedTextTest(unittest.TestCase):
    def test_every_fixed_text(self):
        fixed = [t for k, t in texts.NOTICES.items() if "{" not in t]
        fixed.append(texts.NOTICES["not_in_files"].format(needed=texts.NEEDED["material"].format(words="lithium cells")))
        fixed += [texts.CLARIFY["environment"], texts.CLARIFY["equipment"], texts.CLARIFY["term"],
                  texts.ASSUME_QUESTIONS, texts.ASSUME_CELL.format(preset="ISS cabin"), texts.ERROR]
        for label in list(texts.ANSWER_LABELS.values())[:2]:  # labels say "not safety guidance" on purpose
            self.assertEqual([g for g, _ in ck.gate_fixed(label) if g != "extra"], [], label)
        fixed += [v for v in texts.LIMITS.values() if "{" not in v]
        for t in fixed:
            self.assertEqual(ck.gate_fixed(t), [], t)

    def test_followups(self):
        for intent, qs in texts.FOLLOWUPS.items():
            for q in qs:
                self.assertEqual(ck.gate_question(q), [], q)
        self.assertTrue(ck.gate_question("Is it safe?"))
        self.assertTrue(ck.gate_question("Where are the data."))


class TemplateAnswerTest(unittest.TestCase):
    def test_template_answers_pass(self):
        from ai.assistant.test_tools import all_calls
        for name, args in all_calls():
            out = tools.run([{"tool": name, "args": args, "why": "test"}], D)
            by = {f["id"]: f for f in out["facts"]}
            for s in write.template_answer(out["facts"]):
                cited = [by[i] for i in s["facts"]]
                for gate, reason in ck.gate_sentence(s["text"], cited, {"environment": {}}, set(by)):
                    # template text is team or NASA text: G2 and G5 to G12 must pass (G10 and G13/G14 are for
                    # model sentences; a copied team sentence may hold several sentences)
                    self.assertIn(gate, ("length", "modality", "hedge", "names", "extra", "lint", "policy", "wording"),
                                  f"{name}: {gate}: {reason}: {s['text'][:100]}")
                    if gate in ("policy", "wording", "extra", "lint"):
                        self.assertEqual(cited[0]["kind"], "nasa_sentence" if cited[0]["quote"] else cited[0]["kind"])


class CheckerTest(unittest.TestCase):
    def test_messages_see_only_cited_facts(self):
        m = ck.checker_messages([{"text": "A.", "facts": ["F1"]}], {"F1": RANGE, "F2": RANK})
        self.assertIn("[F1]", m[1]["content"])
        self.assertNotIn("[F2]", m[1]["content"])

    def test_read_verdicts(self):
        v = ck.read_verdicts({"verdicts": [{"n": 1, "supported": "yes", "reason": ""},
                                           {"n": 2, "supported": "yes", "reason": ""},
                                           {"n": 2, "supported": "no", "reason": ""}]}, 3)
        self.assertEqual([v[i][0] for i in (1, 2, 3)], [True, False, False])


if __name__ == "__main__":
    unittest.main()
