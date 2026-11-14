# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for the verification gates (ai/checks.py), the linter (ai/lint_patterns.py) and the
hard checks of ai/check_all.py that can run without the baseline files.

    python3 -m unittest ai.test_checks -v

Negative cases (each must fail with the named reason): a changed number, a unit conversion,
an invented acronym, a 3-word quote, a quote that is not in the source, 'NASA recommends', a
safety verdict, 'materials burn more easily in space', a hypothesis reported with 'showed', a
dropped 'may', the 'microgravity and 1 g are bounds' claim (the current partial_gravity warning
string), an invented id, a too-long sentence, a number word not in the quote, a wrong source.
Positive cases (must pass): the corrected warning strings, a sentence containing 'fire safety',
a copied PSI sentence with its frame, the 24 verbatim first objective sentences (gates 1-4, 6, 8).

Added by the wording review of 14 November (classes LinterGapTest, ReviewerGapTest, TemplateWordingTest):
rewordings of each misconception that the first linter let through, the sentences of the first
gpt-oss:20b batch that passed every gate and were still wrong (a sentence cut off with its quote, a
dropped 'if not better than', a bare 'that due to ...' clause, 'the following', an added 'will'), impact
statements reported in the page's own voice, lower-case application words ('lunar habitat'), number
words above twenty, and the team's own template sentences, which must stay clean.
"""
import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path

from ai import check_all, checks as C, config, evidence as E, lint_patterns as LP, templates as T

EV = E.load()

CURRENT_PARTIAL_GRAVITY = ("PSI has no partial-gravity (lunar or Martian) combustion data. Results are "
                           "microgravity tests; treat microgravity and 1g behaviour as bounds.")
CORRECTED_LONG = ("PSI has no partial-gravity (lunar or Martian) combustion data. All results here are microgravity "
                  "tests. NASA drop-tower tests found materials burning at lower oxygen in lunar gravity than in either "
                  "microgravity or 1 g (Olson and Ferkul 2012), so microgravity and 1 g results do not bound "
                  "partial-gravity behaviour.")
CORRECTED_SHORT = ("PSI has no partial-gravity (lunar or Martian) combustion data. All results here are microgravity "
                   "tests; they are not bounds for lunar or Martian gravity. NASA names partial-gravity material "
                   "flammability a major gap (OCHMO-TB-008).")
FRAME_GRAVITY = ("PSI has no partial-gravity combustion data; every recorded test is a microgravity test, and "
                 "microgravity and 1 g results are not shown here as bounds for lunar or Martian gravity.")


def text(inv, uid):
    return E.unit(inv, uid, EV)["text"]


def ev1(inv, uid, quote=None):
    return [{"id": uid, "quote": text(inv, uid) if quote is None else quote}]


def reasons(res):
    return " | ".join(res["reasons"])


def fixture_packet():
    """A packet that is not NASA text: for gates that do not need the resolver."""
    t1 = "The experiment aims to measure flame spread over PMMA at 21% oxygen and 1,867 points."
    t2 = "Results may indicate a limit near 0.21 mole fraction for three samples."
    return {"records": {"PSI-900": {
        "title": "Fixture Flame Record", "acronym": "FFR-2",
        "units": [
            {"id": "OBJ-1", "field": "objective", "source": "PSI-900.objective", "text": t1,
             "shared_with": [], "quotable": True},
            {"id": "IMP-1", "field": "researchImpacts", "source": "PSI-900.researchImpacts", "text": t2,
             "shared_with": ["PSI-901"], "quotable": True},
        ]}}}


class NumberGateTest(unittest.TestCase):
    def test_changed_number_fails(self):
        q = text("PSI-26", "APP-2")  # '75% cotton and 25% fiberglass'
        ok, why = C.gate_numbers("The planned approach used samples of 70% cotton and 25% fiberglass.", [q])
        self.assertFalse(ok)
        self.assertIn("70%", why)

    def test_unit_conversion_fails(self):
        q = text("PSI-20", "IMP-3")  # '... a normal atmosphere of 21% oxygen self-extinguished ...'
        self.assertTrue(C.gate_numbers("Flames in a normal atmosphere of 21% oxygen self-extinguished.", [q])[0])
        ok, why = C.gate_numbers("Flames in a normal atmosphere of 0.21 oxygen mole fraction self-extinguished.", [q])
        self.assertFalse(ok)
        self.assertIn("0.21", why)
        q2 = text("PSI-20", "OBJ-5")  # '14.7 psia, 21 % oxygen: 10.2 psia, 26.5 %; ...'
        self.assertTrue(C.gate_numbers("One atmosphere was 10.2 psia with 26.5% oxygen.", [q2])[0] is False)  # 'One'
        self.assertTrue(C.gate_numbers("An atmosphere of 10.2 psia with 26.5% oxygen was planned.", [q2])[0])
        ok, why = C.gate_numbers("An atmosphere of 70.3 kPa with 26.5% oxygen was planned.", [q2])
        self.assertFalse(ok)
        ok, why = C.gate_numbers("An atmosphere of 10.2 kPa was planned.", [q2])  # same number, other unit
        self.assertFalse(ok)
        self.assertIn("kpa", why)

    def test_number_word_must_be_in_quote(self):
        q = text("PSI-25", "OBJ-3")
        ok, why = C.gate_numbers("The investigation aimed to study three solid fuels.", [q])
        self.assertFalse(ok)
        self.assertIn("three", why)

    def test_identifiers_are_not_numbers(self):
        got = [(n["value"], n["unit"]) for n in C.extract_numbers(
            "PSI-25, CO2, NASA-STD-6001B, SAFFIRE-II-C01, OCHMO-TB-008: 1,867 tests at 21-40% and 70.3 kPa in 1g")]
        self.assertEqual(got, [("1867", None), ("21", None), ("40", "%"), ("70.3", "kpa"), ("1", "g")])

    def test_document_numbers_are_identifiers(self):
        self.assertEqual(C.extract_numbers("Listed in NASA/CP-2003-212103 and OCHMO-TB-008."), [])

    def test_decimal_token_is_strict(self):
        pk = fixture_packet()
        q = pk["records"]["PSI-900"]["units"][0]["text"]
        self.assertTrue(C.gate_numbers("It used 1,867 points at 21% oxygen.", [q])[0])
        self.assertFalse(C.gate_numbers("It used points at 21.0% oxygen.", [q])[0])


class QuoteAndIdGateTest(unittest.TestCase):
    def test_three_word_quote_fails(self):
        ok, why = C.gate_quote([{"id": "OBJ-3", "quote": "low-velocity forced flows"}], "PSI-25", EV)
        self.assertFalse(ok)
        self.assertIn("3 words", why)

    def test_quote_not_in_source_fails(self):
        ok, why = C.gate_quote([{"id": "OBJ-3", "quote": "Study the ignition and extinction of solid fuels"}],
                               "PSI-25", EV)
        self.assertFalse(ok)
        self.assertIn("not in PSI-25 OBJ-3", why)

    def test_quote_in_wrong_unit_fails(self):
        ok, _ = C.gate_quote([{"id": "OBJ-4", "quote": "solid fuels burning in low-velocity forced flows"}], "PSI-25", EV)
        self.assertFalse(ok)

    def test_quote_normalisation(self):
        # curly quotes, case, whitespace and a trailing period differ; the words are verbatim
        q = "SOLID FUELS   burning in low-velocity forced flows."
        self.assertTrue(C.gate_quote([{"id": "OBJ-3", "quote": q}], "PSI-25", EV)[0])

    def test_invented_id_fails(self):
        ok, why = C.gate_ids([{"id": "OBJ-99", "quote": "x"}], "PSI-25", EV)
        self.assertFalse(ok)
        self.assertIn("OBJ-99", why)
        self.assertFalse(C.gate_ids([], "PSI-25", EV)[0])
        self.assertFalse(C.gate_ids(ev1("PSI-25", "OBJ-3") * 4, "PSI-25", EV)[0])

    def test_sources_gate(self):
        self.assertTrue(C.gate_sources(ev1("PSI-25", "OBJ-3"), "PSI-25", EV)[0])
        bad = [{"id": "OBJ-3", "quote": text("PSI-25", "OBJ-3"), "source": "PSI-25.hypothesis"}]
        self.assertFalse(C.gate_sources(bad, "PSI-25", EV)[0])
        u = E.unit("PSI-25", "OBJ-3", EV)
        good = [{"id": "OBJ-3", "quote": u["text"], "source": u["source"],
                 "char_start": u["char_start"], "char_end": u["char_end"]}]
        self.assertTrue(C.gate_sources(good, "PSI-25", EV)[0])
        shifted = [dict(good[0], char_start=u["char_start"] + 1)]
        self.assertFalse(C.gate_sources(shifted, "PSI-25", EV)[0])


class EntityGateTest(unittest.TestCase):
    def test_invented_acronym_in_bass_card_fails(self):
        # SoFIE is named in the BASS-II record (PSI-25) but not in the BASS record (PSI-26)
        self.assertTrue(C.gate_entities("The record names SoFIE as a user of the data.", "PSI-25", EV)[0])
        ok, why = C.gate_entities("The record names SoFIE as a user of the data.", "PSI-26", EV)
        self.assertFalse(ok)
        self.assertIn("SoFIE", why)

    def test_capitalised_mid_sentence_word(self):
        ok, why = C.gate_entities("The planned approach used fabric samples on Mars.", "PSI-26", EV)
        self.assertFalse(ok)
        self.assertIn("Mars", why)
        self.assertTrue(C.gate_entities("NASA lists the record in PSI as BASS.", "PSI-26", EV)[0])

    def test_fixture_packet(self):
        pk = fixture_packet()
        self.assertTrue(C.gate_entities("The FFR-2 study used PMMA.", "PSI-900", pk)[0])
        self.assertFalse(C.gate_entities("The FFR-2 study used PMMA and CO2.", "PSI-900", pk)[0])


class PolicyAndLintTest(unittest.TestCase):
    def test_nasa_recommends_fails(self):
        ok, why = C.gate_policy("NASA recommends thicker fabrics for cabins.")
        self.assertFalse(ok)
        self.assertIn("nasa recommends", why)

    def test_safety_verdict_fails(self):
        for s in ("The record states that these fabrics are safe in microgravity.",
                  "The results show the material is unsafe at 30% oxygen.",
                  "This approach would ensure crew protection.",
                  "The cabin should use less oxygen."):
            self.assertFalse(C.gate_policy(s)[0], s)

    def test_fire_safety_passes(self):
        self.assertTrue(C.gate_policy("A primary goal is improved spacecraft fire safety.")[0])
        self.assertTrue(C.gate_lint("A primary goal is improved spacecraft fire safety.")[0])

    def test_gate5_rejects_a_paraphrase_of_psi47(self):
        # PSI-47 OBJ-8 itself says 'Ensure the reliability ...'; a model paraphrase with the word is rejected
        self.assertIn("Ensure", text("PSI-47", "OBJ-8"))
        ok, why = C.gate_policy("The investigation aimed to ensure the reliability of future aerosol experiments.")
        self.assertFalse(ok)
        self.assertIn("ensure", why)

    def test_burns_more_easily_in_space_fails(self):
        ok, why = C.gate_lint("Materials burn more easily in space.")
        self.assertFalse(ok)
        self.assertIn("comparative_in_space", why)
        self.assertFalse(C.gate_lint("Fabric is more flammable in microgravity than expected.")[0])

    def test_bounds_claim_fails(self):
        for s in (CURRENT_PARTIAL_GRAVITY,
                  "Lunar behaviour lies between microgravity and 1 g results.",
                  "Microgravity and normal gravity results bracket partial-gravity flammability.",
                  "Treat 0 g and Earth gravity behaviour as bounds."):
            ok, why = C.gate_lint(s)
            self.assertFalse(ok, s)
            self.assertIn("micro_and_1g_as_bounds", why)

    def test_corrected_strings_pass(self):
        for s in (CORRECTED_LONG, CORRECTED_SHORT, FRAME_GRAVITY,
                  "Microgravity and 1 g results do not bound lunar behaviour."):
            self.assertEqual(C.lint_text(s), [], s)
        # the PSI-26 and PSI-60 objectives use 'between' with 1 g and 0 g without a bounds claim
        self.assertEqual(LP.lint(text("PSI-26", "OBJ-2")), [])
        self.assertEqual(LP.lint(text("PSI-60", "OBJ-1")), [])

    def test_each_linter_pattern(self):
        cases = {
            "test1_conservative": "The NASA-STD-6001 Test 1 is a worst-case test.",
            "no_airflow_goes_out": "Without ventilation a flame goes out.",
            "cool_flame_harmless": "Cool flames are harmless.",
            "equivalent_to_earth_air": "The 21% cabin is equivalent to Earth air.",
            "flames_spherical_in_space": "Flames in space are spherical.",
            "partial_gravity_result_from_psi": "PSI-25 tests found that PMMA burned at lunar gravity.",
            "flames_spherical_in_space": "Flames in space are spherical.",
            "burns_more_easily": "Cotton burns more easily at low flow.",
        }
        for name, s in cases.items():
            self.assertIn(name, LP.lint(s), s)
        clean = ["Every recorded test is a microgravity test; none was run at lunar gravity.",
                 "The preset sets no atmosphere; the results reflect assumed cabin air, not a match to a Mars habitat.",
                 "In NASA drop-tower tests, three thin materials burned at lower oxygen in lunar gravity than in "
                 "either microgravity or 1 g (Olson and Ferkul 2012, Table I).",
                 "The FLEX investigation aims to develop predictive models under reduced gravity conditions.",
                 "Counts for the Lunar base or pressurized rover scenario are recorded tests whose oxygen falls "
                 "in the team bins.",
                 "Test-level records in PSI from combustion tests run at lunar gravity.",
                 "Material flammability in partial gravity: Named a major gap; every test in the PSI tables is a "
                 "microgravity test."]
        for s in clean:
            self.assertEqual(LP.lint(s), [], s)

    def test_reader_pass_template_sentences_are_clean(self):
        """The sentences added by the careful-reader pass (14 Nov): the lunar challenge-statement caveat, the
        reworded Olson and Ferkul sentence, the flow and test-end clauses. Each is lint-clean, carries no
        advice, prediction or verdict wording, and prints only numbers that are in its facts."""
        from ai import templates as T
        inside = {"n": 17, "noun": "fuel-droplet tests", "o2": (30.0, 34.0), "kpa": (71, 72), "atm": 0.7,
                  "above": (1, 2)}
        facts = {"o2": [30, 34], "psi": 10.2, "kpa": [70.3, 71, 72, 85.8], "atm": 0.7, "above": [1, 2], "n": 17,
                 "materials": 3, "seconds": 5.18, "flow_rest": 9}
        item = ("Moon Base and pressurized-rover atmosphere expected between spacesuit and Earth conditions: oxygen "
                "likely 30% or more, pressure 10.2 psi or less.")
        caveat = ("The pressure range of this scenario reaches up to 85.8 kPa, above the 70.3 kPa (10.2 psi) of the "
                  "challenge statement, so that tests set to 0.7 atm are inside it.")
        sentences = [
            T.frame_challenge_bound(item, 10.2, 70.3, 30, 0, inside, caveat),
            T.matched_bound_clause(17, (30.0, 34.0), (71, 72), 0.7, (1, 2), 10.2, 70.3, 30, 0),
            "They were " + T.bound_short((30.0, 34.0), (71, 72), 0.7, (1, 2), 10.2, 70.3) + ".",
            T.frame_drop_tests("lunar", "every", "every", 5.18, True, True, 3, True),
            T.frame_drop_tests("martian", "every", "some", 5.18, True, True, 3, True),
            T.flow_outside(9),
            T.TEST_END_NOTES["disruption"],
            T.FRAME_STREAM,
            T.frame_bins("Lunar base or pressurized rover", {"o2_pct": {"min": 30, "max": 36, "max_inclusive": True},
                                                            "pressure_kpa": {"min": None, "max": 85.8}}),
        ]
        facts["bins"] = [30, 36, 85.8]
        for s in sentences:
            res = C.check_template(s, facts)
            self.assertTrue(res["ok"], (res["reasons"], s))
            for part in C.sentences_of(s) or [s]:
                self.assertEqual(LP.lint(part), [], part)
        # the same claims without their guard words still trip the linter
        self.assertIn("micro_and_1g_as_bounds",
                      LP.lint("At lunar gravity the limits lie between those at 0 g and 1 g."))
        self.assertIn("partial_gravity_result_from_psi",
                      LP.lint("The 17 FLEX tests showed how droplets burned at lunar gravity."))
        # the caveat never says the 17 tests were at or below the challenge-statement pressure, and it uses the
        # wording of coord/decisions.md 14:15
        self.assertNotRegex(sentences[1], r"17 were recorded at or below")
        for s in sentences[:3]:
            self.assertIn("30 to 34% oxygen and about 0.7 atm (71 to 72 kPa)", s)
        self.assertIn("No counted test was recorded at 30% oxygen or more and at or below 10.2 psi", sentences[0])


class ModalityAndHedgeTest(unittest.TestCase):
    def test_hypothesis_reported_with_showed_fails(self):
        q = "materials in microgravity, with adequate ventilation, burn as well if not better"
        evid = [{"id": "HYP-1", "quote": q}]
        ok, why = C.gate_modality("BASS-II showed that materials in microgravity, with adequate ventilation, burn as "
                                  "well if not better than in normal gravity.", evid, "PSI-25", EV)
        self.assertFalse(ok)
        self.assertIn("no frame", why)
        ok, why = C.gate_modality("The record hypothesizes, and BASS-II showed, that materials in microgravity burn "
                                  "as well if not better.", evid, "PSI-25", EV)
        self.assertFalse(ok)
        self.assertIn("showed", why)
        self.assertTrue(C.gate_modality("The record hypothesizes that materials in microgravity, with adequate "
                                        "ventilation, burn as well if not better.", evid, "PSI-25", EV)[0])

    def test_result_verb_allowed_when_in_quote(self):
        evid = ev1("PSI-26", "APP-8")  # 'Flames were observed in the top and edge profiles ...'
        self.assertTrue(C.gate_modality("The planned approach: flames were observed in the top and edge profiles.",
                                        evid, "PSI-26", EV)[0])

    def test_impact_units_need_an_attribution(self):
        # review: an impact statement is the record's claim of significance, not a result; the first
        # version of the gate let it through in the page's own voice
        ok, why = C.gate_modality("A primary goal of BASS-II is improved fire safety.",
                                  ev1("PSI-25", "IMP-1"), "PSI-25", EV)
        self.assertFalse(ok)
        self.assertIn("not attributed", why)
        self.assertTrue(C.gate_modality("The record states that a primary goal of BASS-II is improved fire safety.",
                                        ev1("PSI-25", "IMP-1"), "PSI-25", EV)[0])
        # an objective cited together with an impact statement still needs the aim frame
        mixed = ev1("PSI-25", "OBJ-3") + ev1("PSI-25", "IMP-1")
        self.assertFalse(C.gate_modality("The record states that BASS-II studies ignition for fire safety.",
                                         mixed, "PSI-25", EV)[0])
        self.assertTrue(C.gate_modality("The investigation aimed to study ignition for fire safety.",
                                        mixed, "PSI-25", EV)[0])

    def test_dropped_may_fails(self):
        q = text("PSI-20", "HYP-2")  # 'Steady burning may never be achieved, ...'
        ok, why = C.gate_hedge("The record hypothesizes that steady burning is never achieved.", [q])
        self.assertFalse(ok)
        self.assertIn("may", why)
        self.assertTrue(C.gate_hedge("The record hypothesizes that steady burning may never be achieved.", [q])[0])
        self.assertTrue(C.gate_hedge("Any sentence.", [text("PSI-25", "OBJ-3")])[0])


class LengthTest(unittest.TestCase):
    def test_too_long_and_two_sentences(self):
        self.assertFalse(C.gate_length(" ".join(["word"] * 36) + ".")[0])
        self.assertTrue(C.gate_length(" ".join(["word"] * 35) + ".")[0])
        self.assertFalse(C.gate_length("It aims to burn. It aims to stop.")[0])
        self.assertFalse(C.gate_length("It aims to burn.", n_summary=4)[0])


class SentenceTest(unittest.TestCase):
    def test_copied_sentence_with_frame_passes(self):
        res = C.check_sentence("The investigation aimed to study the ignition, flame growth, flame spread, and "
                               "extinction limits for solid fuels burning in low-velocity forced flows in microgravity.",
                               ev1("PSI-25", "OBJ-3"), "PSI-25", EV)
        self.assertTrue(res["ok"], reasons(res))
        self.assertEqual(set(res["checks"]), set(C.CHECK_NAMES))
        self.assertGreaterEqual(res["lexical_support"], 0.9)

    def test_fire_safety_sentence_passes(self):
        res = C.check_sentence("The record states that a primary goal of BASS-II is improved spacecraft fire safety. "
                               "(PSI-25 record: researchImpacts)",
                               ev1("PSI-25", "IMP-1"), "PSI-25", EV)
        self.assertTrue(res["ok"], reasons(res))

    def test_each_negative_fails_with_its_gate(self):
        cases = [
            ("numbers_ok", "PSI-26", "The planned approach used samples of 70% cotton and 25% fiberglass.",
             ev1("PSI-26", "APP-2")),
            ("entities_ok", "PSI-26", "The planned approach used SoFIE fabric samples of 75% cotton and 25% fiberglass.",
             ev1("PSI-26", "APP-2")),
            ("quote_ok", "PSI-25", "The investigation aimed to study extinction limits for solid fuels.",
             [{"id": "OBJ-3", "quote": "extinction limits for"}]),
            ("policy_ok", "PSI-25", "NASA recommends the record's study of improved spacecraft fire safety.",
             ev1("PSI-25", "IMP-1")),
            ("lint_ok", "PSI-25", "The record states that materials burn more easily in space.", ev1("PSI-25", "IMP-1")),
            ("modality_ok", "PSI-25", "BASS-II showed that materials in microgravity, with adequate ventilation, burn "
             "as well if not better.", ev1("PSI-25", "HYP-1")),
            ("hedge_ok", "PSI-20", "The record hypothesizes that steady burning is never achieved.",
             ev1("PSI-20", "HYP-2")),
            ("ids_ok", "PSI-25", "The investigation aimed to study flames.", [{"id": "OBJ-42", "quote": "x y z w v"}]),
        ]
        for gate, inv, s, evid in cases:
            res = C.check_sentence(s, evid, inv, EV)
            self.assertFalse(res["ok"], s)
            self.assertFalse(res["checks"][gate], f"{gate}: {s} -> {reasons(res)}")

    def test_shared_tag(self):
        self.assertEqual(C.shared_tag(ev1("PSI-98", "HYP-1"), "PSI-98", EV), ["PSI-99", "PSI-100"])
        self.assertEqual(C.shared_tag(ev1("PSI-25", "OBJ-3"), "PSI-25", EV), [])
        self.assertEqual(C.shared_tag([{"id": "IMP-1"}], "PSI-900", fixture_packet()), ["PSI-901"])

    def test_first_objective_sentences_pass_gates_1_to_4_6_and_8(self):
        """False-rejection check: the 24 verbatim first quotable objective units. Gate 5 is excluded
        (PSI-47 says 'Ensure'), gates 10 and 11 are about wording a model adds; gate 7 is reported."""
        self.assertEqual(len(EV["records"]), 24)
        failures, too_long = [], []
        for inv, rec in EV["records"].items():
            u = next(x for x in rec["units"] if x["field"] == "objective" and x["quotable"])
            res = C.check_sentence(u["text"], [{"id": u["id"], "quote": u["text"]}], inv, EV)
            for g in ("ids_ok", "quote_ok", "numbers_ok", "entities_ok", "lint_ok", "sources_ok"):
                if not res["checks"][g]:
                    failures.append((inv, u["id"], g, reasons(res)))
            if not res["checks"]["length_ok"]:
                too_long.append(inv)
        self.assertEqual(failures, [])
        # gate 7 limits model sentences to 35 words; these NASA sentences are longer and are shown as quotes
        print(f"\n  first objective units over {C.MAX_WORDS} words (gate 7, quotes are never gated): "
              f"{len(too_long)} of 24: {', '.join(too_long)}")


class TemplateTest(unittest.TestCase):
    def test_numbers_must_be_in_facts(self):
        t = "Recorded tests (team count; team bins: oxygen 30 to 36%, pressure below 85.8 kPa). 17 of the 294 usable tests."
        facts = {"o2_min": 30, "o2_max": 36, "p_max": 85.8, "in_bins": 17, "usable": 294}
        self.assertTrue(C.check_template(t, facts)["ok"])
        res = C.check_template(t, dict(facts, in_bins=16))
        self.assertFalse(res["checks"]["numbers_ok"])
        self.assertIn("17", reasons(res))

    def test_gravity_names_and_one(self):
        self.assertTrue(C.check_template(FRAME_GRAVITY, {})["ok"], reasons(C.check_template(FRAME_GRAVITY, {})))
        self.assertTrue(C.check_template("PSI's table has one row per test day (18 days).", {"days": 18})["ok"])
        self.assertFalse(C.check_template("Three thin materials burned.", {})["ok"])
        self.assertTrue(C.check_template("Three thin materials burned.", {"materials": 3})["ok"])

    def test_banned_tokens(self):
        for t in ("It is the best match.", "It ranks first for this scenario.", "Score 94.0 under the team weights.",
                  "It is #1 here.", "It is in the top 3.", "It scored 79.1 points."):
            self.assertFalse(C.check_template(t, {"x": 94.0, "y": 79.1, "z": 1, "w": 3})["checks"]["banned_ok"], t)
        self.assertTrue(C.check_template("Tied with FLEX under the team's current weights.", {})["ok"])

    def test_advice_and_lint_in_templates(self):
        self.assertFalse(C.check_template("Designers should avoid this atmosphere.", {})["checks"]["policy_ok"])
        self.assertFalse(C.check_template(CURRENT_PARTIAL_GRAVITY, {})["checks"]["lint_ok"])

    def test_inverse_flame_sources(self):
        inv = sorted(C.inverse_flame_sources())
        self.assertIn("pipeline/spec/sources.json#cfig_inverse", inv)
        src = ["pipeline/spec/sources.json#cfig_inverse"]
        self.assertFalse(C.check_template("Its tests record oxygen.", {}, src)["checks"]["inverse_ok"])
        self.assertTrue(C.check_template("Its inverse-flame tests record burner-stream oxygen.", {}, src)["ok"])


class CheckAllTest(unittest.TestCase):
    def test_missing_files_are_not_built_yet(self):
        with tempfile.TemporaryDirectory() as d:
            rep = check_all.Report()
            check_all.check_cards(rep, Path(d) / "cards.json", EV)
            check_all.check_scenarios(rep, Path(d) / "scenarios.json", EV, recount=None)
            self.assertEqual(rep.failures(), [])
            self.assertEqual(sorted(x["section"] for x in rep.items if x["level"] == "not_built"),
                             ["cards", "scenarios"])

    def test_unknown_status_or_gap_code_fails(self):
        path = config.ROOT / "data" / "pipeline" / "scenario_needs.csv"
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        fake = copy.deepcopy(rows)
        fake[0]["status"] = "covered"
        fake[1]["gaps"] = "pressure:made_up_code"
        rep = check_all.Report()
        check_all.check_codes(rep, fake)
        msgs = " ".join(x["message"] for x in rep.failures())
        self.assertIn("covered", msgs)
        self.assertIn("pressure:made_up_code", msgs)
        rep2 = check_all.Report()
        check_all.check_codes(rep2, rows)
        self.assertEqual(rep2.failures(), [])

    def test_header_comment_check(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "good.py").write_text(config.HEADER_COMMENT + "\nx = 1\n")
            (Path(d) / "bad.py").write_text("x = 1\n")
            rep = check_all.Report()
            check_all.check_headers(rep, Path(d))
            self.assertEqual([x["message"].split(":")[0] for x in rep.failures()], ["bad.py"])

    def test_verbatim_span_with_list_marker(self):
        # PSI-159's objective starts with a list; a quoted span may start at its '1.' marker
        u = E.units("PSI-159", "objective", ev=EV)[0]
        raw = json.loads((config.PSI_CATALOG_DIR / "PSI-159.json").read_text(encoding="utf-8"))["objective"]
        k = raw.rfind(u["list_marker"], 0, u["char_start"]) if u["list_marker"] else u["char_start"]
        span = " ".join(raw[k:u["char_end"]].split())
        self.assertTrue(check_all._verbatim("PSI-159", "Stated objective:", span, EV))
        self.assertFalse(check_all._verbatim("PSI-159", "Stated objective:", span.replace("ISS", "the ISS"), EV))
        self.assertFalse(check_all._verbatim("PSI-159", "Stated hypothesis:", span, EV))

    def test_psi_to_kpa_conversion_is_the_only_derived_value(self):
        src = ["pipeline/spec/references.json#EAWG.atmospheres"]
        missing, n, _ = check_all._facts_found({"a": [8.0, 55.2, 32]}, [], src)
        self.assertEqual(missing, [])
        missing, _, _ = check_all._facts_found({"a": 55.3}, [], src)
        self.assertEqual(missing, [55.3])

    def test_model_sentence_in_card_is_gated(self):
        u = E.unit("PSI-25", "OBJ-3", EV)
        sent = {"role": "summary", "origin": "model",
                "text": "BASS-II showed the ignition, flame growth, flame spread, and extinction limits for solid "
                        "fuels burning in low-velocity forced flows in microgravity. (PSI-25 record: objective)",
                "field_label": None,
                "evidence": [{"id": "OBJ-3", "source": u["source"], "quote": u["text"],
                              "char_start": u["char_start"], "char_end": u["char_end"]}],
                "checks": {}, "review": None}
        card = {"investigation_id": "PSI-25", "summary": sent["text"], "summary_sources": ["PSI-25.objective"],
                "key_points": [{"text": E.quote_line(u), "source": u["source"]}], "ai_generated": True,
                "model": config.MODEL_LABEL, "reviewed_by": None, "updated": "2026-11-14T13:00:00+09:00",
                "status": "generated", "sentences": [sent]}
        rep = check_all.Report()
        check_all.check_card(rep, card, EV, final=False)
        self.assertTrue(any("modality" in x["message"] for x in rep.failures()), rep.failures())


class LinterGapTest(unittest.TestCase):
    """Rewordings that the first linter let through (wording review, 14 November)."""

    MUST_HIT = {
        "micro_and_1g_as_bounds": [
            "Lunar-gravity flammability can be interpolated from microgravity and normal-gravity data.",
            "Flammability at lunar gravity falls within the range spanned by microgravity and 1 g tests.",
            "Microgravity and 1-g results give the lower and upper limits for Martian gravity.",
            "Partial gravity is an intermediate case of the microgravity and Earth-gravity results.",
            "Zero-g and one-g tests envelope the lunar case.",
            "There is no doubt that microgravity and 1 g bound lunar behaviour.",
        ],
        "partial_gravity_result_from_psi": [
            # the old rule excused any sentence that had a 'not' anywhere
            "PSI tests at lunar gravity showed flames that did not go out.",
            "At Martian gravity the PSI-69 droplets extinguished earlier.",
            "Cotton burns at lunar gravity in 30% oxygen.",
        ],
        "behaviour_at_untested_place": [
            "Cotton fabric burns in a lunar habitat at 30% oxygen.",
            "PMMA is flammable on the Moon.",
            "Materials ignite on Mars at lower oxygen.",
        ],
        "comparative_in_space": [
            "Microgravity makes materials more flammable.",
            "Fires are more dangerous aboard a spacecraft.",
            "Flames spread faster under reduced gravity.",
            "There is a higher fire risk on the ISS.",
        ],
        "test1_conservative": [
            "The upward flame test is conservative for spacecraft.",
            "Normal-gravity screening tests give a safety margin.",
            "1 g flammability limits are an upper bound.",
        ],
        "no_airflow_goes_out": [
            "A fire in still air dies out.",
            "With the fan off, the flame self-extinguishes.",
            "When the flow is stopped the flame cannot spread.",
        ],
        "cool_flame_harmless": [
            "Cool flames pose no risk to a crew.",
            "A cool flame is not dangerous.",
        ],
        "equivalent_to_earth_air": [
            "The exploration atmosphere has the same oxygen partial pressure as sea-level air.",
            "A normoxic atmosphere is no more flammable.",
            "At 34% oxygen and 56.5 kPa a material is as flammable as in normal air.",
        ],
    }

    def test_rewordings_hit(self):
        for name, sentences in self.MUST_HIT.items():
            for s in sentences:
                self.assertIn(name, LP.lint(s), s)

    def test_negated_and_reported_forms_stay_clean(self):
        clean = [
            # the ui role's corrected warning, as it is in scoring_config.json since 13:06
            "PSI has no partial-gravity (lunar or Martian) combustion data. All results here are microgravity "
            "tests; they are not bounds for lunar or Martian gravity.",
            # catalog findings that report NASA results (report-only lint must not flag them)
            "Quasi-steady burning emulating condensed fuels (e.g., PMMA, nylon) was seen without airflow, notably "
            "in elevated-oxygen atmospheres; in 21% O2 such flames self-extinguished in a short time.",
            "Hypothesis tested: with adequate ventilation, materials burn as well or better in microgravity than "
            "in normal gravity, so the upward 1g test may not be conservative in space.",
            # PSI wording that a model paraphrase may keep
            "The investigation aimed to establish the burning conditions in a quiescent microgravity ambient in "
            "terms of material properties.",
            "The record hypothesizes that materials in microgravity, with adequate ventilation, burn as well if "
            "not better than the same material in normal gravity with other conditions being identical.",
            "The investigation aimed to investigate the low-g flammability limits compared to those obtained in "
            "NASA's normal gravity material flammability screening test.",
        ]
        for s in clean:
            self.assertEqual(C.lint_text(s), [], s)

    def test_test1_is_strict_and_other_screening_tests_allow_negation(self):
        self.assertIn("test1_conservative", LP.lint("NASA-STD-6001 Test 1 may not be conservative."))  # by design
        self.assertEqual(LP.lint("Normal-gravity screening tests may not be conservative."), [])
        self.assertIn("test1_conservative", LP.lint("Normal-gravity screening tests are conservative."))


class TemplateWordingTest(unittest.TestCase):
    """The team's own sentences (ai/templates.py) stay clean under the widened linter and lexicon."""

    QUOTE = "Material flammability in partial gravity remains a major gap for exploration missions."

    def sentences(self):
        return [
            T.FRAME_RULE, T.FRAME_STREAM, T.FRAME_GRAVITY, T.nasa_gravity_gap(self.QUOTE), T.nasa_gravity_gap(None),
            T.frame_mars([(8.0, "55.2"), (7.6, "52.4")]), T.frame_spacesuit(40.0, 85.0),
            T.gap_gravity("lunar", self.QUOTE), T.gap_gravity("martian", None),
            T.frame_drop_tests("lunar", "every", "every", 5.18, True, True),
            T.frame_drop_tests("martian", "every", "some", 5.18, True, True),
            T.frame_drop_tests("martian", "some", None, None, False, False),
            T.gap_gravity_needed("lunar"), T.gap_solid(24, 22.2, ["PSI-26 (BASS)"]), T.gap_solid_psi20(40.0, True),
            T.gap_solid_saffire([("VI-2", 31.0, 54.1), ("VI-3", 30.3, 54.6)], 5, 24, True), T.GAP_SOLID_NEEDED,
            T.test_end_clause(17, [("disruption", 15), ("completion", 2)], True),
            T.gap_phase(17, ["PSI-69 (FLEX)"]),
            T.gap_detection({"n": 122, "invs": ["PSI-25 (BASS-II)"], "missing": ["pressure"]},
                            {"n": 0, "invs": [], "missing": []}),
            T.note_objectives(["P1 (Flammability limit)"], ["D1 (Combustion products)"]),
            T.note_phase("gas", "solid"), T.note_assumed(["pressure"]), T.note_spacesuit(95, 100), T.NOTE_MARS,
            T.note_stream(154), T.NOTE_NEAR, T.note_tie(["FLEX"]),
            T.note_test_day_oxygen(21.0, 40.0, ["3400%", "2100%"], True),
            T.cell_not_used("pressure_kpa", 1, ["PSI-69 (FLEX)"], ["0"], "Ambient pressure; mmHg", "out_of_range"),
            T.outside_objective(272, ["PSI-159"], True), T.status_atmosphere_not_specified(136),
            T.gravity_sentence("lunar"), T.SCENARIO_LABEL, T.CARD_LABEL,
            # second careful-reader pass (14 Nov)
            T.frame_rule(True), T.frame_rule(False),
            T.data_note("The ranges set oxygen, pressure and flow only. Matched tests can have carbon dioxide or "
                        "helium added to the atmosphere; each need block gives the number."),
            T.uncounted_below("gas-burner flames", "PSI-159 (ACME CFI-G)",
                              "at 30% oxygen or more and at or below 10.2 psi", False),
            T.uncounted_below("tests", "PSI-39 (CFI)", "at 30% oxygen or more and at or below 10.2 psi", True),
            "9 of its 179 tests have oxygen and pressure inside this scenario's team bins ("
            + T.bound_short_below((33, 36), (51, 51), None, 10.2, 70.3, True) + ").",
            T.reading_mismatch(122, ["PSI-25 (BASS-II)"], ["BASS2TM.products"]), T.reading_mismatch(1, [], []),
            T.outside_objective(2, ["PSI-98"], False, True, differs=[("PSI-98", ["SAF16.saffire1"])]),
            T.outside_objective(9, ["PSI-10", "PSI-39"], False, False, topic_only=[("PSI-10", ["ACME14.flamedesign"]),
                                                                                   ("PSI-39", [])]),
            T.gap_phase(17, ["PSI-69 (FLEX)"], "recorded at 30 to 34% oxygen"),
        ]

    def test_second_reader_pass_sentences(self):
        """What the second careful-reader pass changed, pinned: which tables a sentence speaks for, whose voice
        the data role's caveat is in, and that 'no counted test' is followed by the tests that are not counted."""
        for s in (T.FRAME_GRAVITY, T.gravity_sentence("lunar"), T.gap_gravity("lunar", self.QUOTE)):
            self.assertIn("Every test in the PSI experimental tables used here is a microgravity test", s)
        self.assertIn("investigations used here", T.gap_solid(24, 22.2))
        self.assertIn("have no pressure value in the PSI experimental tables",
                      T.gap_detection({"n": 122, "invs": ["PSI-25 (BASS-II)"], "missing": ["pressure"]},
                                      {"n": 0, "invs": [], "missing": []}))
        caveat = "Read the recorded pressure of the matched tests in each need block before calling a test 'x'."
        note = T.data_note(caveat)
        self.assertEqual(note, f"The team's data note on these ranges reads: \"{caveat}\"")
        inside = {"n": 17, "noun": "fuel-droplet tests", "o2": (30.0, 34.0), "kpa": (71, 72), "atm": 0.7,
                  "above": (1, 2)}
        frame = T.frame_challenge_bound("Oxygen likely 30% or more, pressure 10.2 psi or less.", 10.2, 70.3, 30, 0,
                                        inside, caveat,
                                        [{"noun": "gas-burner flames", "inv": "PSI-159 (ACME CFI-G)", "linked": False}])
        # the decision's sentence is kept word for word, the caveat sits inside the quotation marks before it, and
        # the uncounted tests follow it
        decision = ("No counted test was recorded at 30% oxygen or more and at or below 10.2 psi; the 17 counted "
                    "tests inside the bins are fuel-droplet tests recorded 1 to 2 kPa above it, at 30 to 34% oxygen "
                    "and about 0.7 atm (71 to 72 kPa).")
        self.assertIn(note + " " + decision + " Gas-burner flames of PSI-159 (ACME CFI-G) were recorded at 30% "
                      "oxygen or more and at or below 10.2 psi; they are counted for no need, because the team "
                      "pipeline links none of the needs to an objective stated for that investigation.", frame)
        self.assertNotIn("because the team pipeline",
                         T.uncounted_below("tests", "PSI-39 (CFI)", "at 30% oxygen or more and at or below 10.2 psi", True))
        self.assertEqual(T.bound_short_below((33, 36), (51, 51), None, 10.2, 70.3, True),
                         "recorded at 33 to 36% oxygen and 51 kPa, below the 10.2 psi (70.3 kPa) of the challenge "
                         "statement; counted for no need")
        self.assertTrue(T.frame_rule(True).endswith(T.FRAME_RULE_AI))
        self.assertEqual(T.frame_rule(False), T.FRAME_RULE)
        self.assertEqual(T.reading_mismatch(122, ["PSI-25 (BASS-II)"], ["BASS2TM.products"]),
                         "Team note: this reading still says that no test is counted; the 122 tests in the count "
                         "above are counted, through a purpose sentence in a publication on PSI-25 (BASS-II) "
                         "(BASS2TM.products) and not in the PSI record.")
        self.assertEqual(T.reading_mismatch(1, [], []),
                         "Team note: this reading still says that no test is counted; the 1 test in the count above "
                         "is counted.")
        # tests outside the stated objective: never 'does not state this need as an objective' (the PSI record of
        # PSI-98 and PSI-99 names the objective; the literature check marks the link 'differs')
        out = T.outside_objective(2, ["PSI-98"], False, True, differs=[("PSI-98", ["SAF16.saffire1"])])
        self.assertEqual(out, "2 further tests record the needed variables, but the team pipeline has no supported "
                              "match between this need and a purpose sentence of the investigation (PSI-98); they "
                              "are not counted. The PSI record of PSI-98 names this objective, but the publications "
                              "that were read state a different purpose for this investigation (SAF16.saffire1).")
        self.assertNotIn("not state this need", T.outside_objective(272, ["PSI-159"], True))
        self.assertTrue(T.outside_objective(272, ["PSI-159"], True).endswith(
            "These include inverse-flame tests, whose oxygen value is the burner stream and not an atmosphere."))
        self.assertTrue(T.gap_phase(17, ["PSI-69 (FLEX)"]).startswith("The 17 counted tests inside"))

    def test_no_lint_no_advice_no_banned_token(self):
        for s in self.sentences():
            self.assertEqual(C.lint_text(s), [], s)
            self.assertTrue(C.gate_banned(s)[0], s)

    def test_reviewed_wording(self):
        # no 'recommend' even in an attribution, no rank word, no 'cabin atmosphere' for a suit
        self.assertNotIn("recommend", T.frame_mars([(8.0, "55.2")]))
        self.assertNotRegex(T.note_spacesuit(95, 100), r"\b(first|second|third)\b")
        self.assertNotIn("cabin atmosphere", T.note_stream(154) + T.FRAME_STREAM)
        # the bounds statement is what the page does, not a finding of the team
        self.assertIn("not treated here as bounds", T.gap_gravity("lunar", self.QUOTE))
        self.assertIn(f'"{self.QUOTE}"', T.gap_gravity("lunar", self.QUOTE))
        # a NASA cell that holds a value is never called empty
        t = T.cell_not_used("pressure_kpa", 1, ["PSI-69 (FLEX)"], ["0"], "Ambient pressure; mmHg", "out_of_range")
        self.assertIn("reads '0'", t)
        self.assertNotIn("empty", t)
        # the PSI-20 oxygen values are what its table notes call them
        self.assertIn("approximate", T.note_test_day_oxygen(21.0, 40.0, [], True))
        self.assertIn("approximate", T.gap_solid_psi20(40.0))

    def test_template_bans(self):
        for t in ("This need is covered by 17 tests.", "Solid fuels were never tested at 30% oxygen.",
                  "The team predicts spread at 34% oxygen.", "Cotton will burn at 30% oxygen.",
                  "This fabric is flammable at 30% oxygen."):
            self.assertFalse(C.check_template(t, {"a": 17, "b": 30, "c": 34})["checks"]["banned_ok"], t)
        # a NASA phrase quoted in a copied line is not the page predicting anything
        copied = ("Heat release of a fire: The record says the results 'are used in first order models and "
                  "predictions of heat release in spacecraft fires'; no standard variable holds a heat release.")
        self.assertTrue(C.check_template(copied, {})["ok"], reasons(C.check_template(copied, {})))
        # the same words written by the team, or quoted but not verbatim NASA text, are read
        for t in ("Heat release of a fire: the results are used in predictions of heat release in spacecraft fires.",
                  "The record says the results 'are used in predictions of heat release on the Moon'."):
            self.assertFalse(C.check_template(t, {})["checks"]["banned_ok"], t)

    def test_quoted_nasa_text_is_not_read_by_the_wording_gates(self):
        quoted = "'are used in first order models and predictions of heat release in spacecraft fires'"
        spans = C.quoted_nasa_spans(f"The record says the results {quoted}.")
        self.assertEqual(len(spans), 1)
        self.assertNotIn("predictions", C.strip_nasa_quotes(f"The record says the results {quoted}."))
        # a model sentence is read too: unquoted 'predict' wording is a policy failure
        self.assertFalse(C.gate_wording("The record states that the models will predict flame spread.")[0])
        self.assertTrue(C.gate_wording(f"The record states that the results {quoted}.")[0])


class ReviewerGapTest(unittest.TestCase):
    """Sentences of the first gpt-oss:20b batch (ai/runs/cards_20261114-v2-all24.jsonl) that passed every
    gate and were still wrong, and other holes found by reading the gates."""

    def check(self, inv, sentence, evid):
        return C.check_sentence(sentence, evid, inv, EV)

    def test_sentence_cut_off_with_its_quote(self):
        # PSI-98 S0: the quote is verbatim and stops after 'normal'; so did the sentence
        q = ("determine how rapidly a large scale fire grows in low-gravity and (2) investigate the low-g "
             "flammability limits compared to those obtained in NASA\u2019s normal")
        res = self.check("PSI-98", "The investigation aimed to determine how rapidly a large scale fire grows in "
                         "low-gravity and investigate the low-g flammability limits compared to those obtained in "
                         "NASA\u2019s normal.", [{"id": "OBJ-2", "quote": q}])
        self.assertFalse(res["checks"]["quote_ok"], reasons(res))
        self.assertIn("stops where its clipped quote", reasons(res))

    def test_sentence_that_skips_the_qualifier_after_a_clipped_quote(self):
        # PSI-26 S1: 'burn as well [if not better than] the same material' became 'burn as well as'
        q = ("BASS experiments were based on the hypothesis that materials in microgravity, with adequate "
             "ventilation, burn as well")
        res = self.check("PSI-26", "The record hypothesizes that materials in microgravity, with adequate ventilation, "
                         "burn as well as the same material in normal gravity.", [{"id": "HYP-1", "quote": q}])
        self.assertFalse(res["checks"]["quote_ok"], reasons(res))
        self.assertIn("leaves the source", reasons(res))

    def test_clipped_quote_is_fine_when_the_sentence_goes_on_as_the_source_does(self):
        # PSI-20 S1: the quote stops before 'as a function of materials properties', the sentence does not
        q = "The BRE investigation hypothesizes that there can exist a regime of quasi-steady burning in microgravity"
        res = self.check("PSI-20", "The record hypothesizes that there can exist a regime of quasi-steady burning in "
                         "microgravity as a function of materials properties.", [{"id": "HYP-1", "quote": q}])
        self.assertTrue(res["ok"], reasons(res))
        # and a quote that stops at a comma or before 'and' is a clause, not a cut
        self.assertFalse(C.quote_stops_mid_phrase("The objectives of SAFFIRE-II are to determine how rapidly a large "
                                                  "scale fire grows in low-gravity", text("PSI-99", "OBJ-1")))
        self.assertTrue(C.quote_stops_mid_phrase(q, text("PSI-20", "HYP-1")))

    def test_bare_subordinate_clause(self):
        # PSI-99 S1: the whole 'sentence' is the 'due to' clause of the hypothesis
        q = "This investigation hypothesizes that due to large differences between fire behavior in normal and reduced gravity"
        res = self.check("PSI-99", "The record hypothesizes that due to large differences between fire behavior in "
                         "normal and reduced gravity.", [{"id": "HYP-1", "quote": q}])
        self.assertFalse(res["checks"]["length_ok"], reasons(res))
        self.assertIn("no main clause", reasons(res))
        self.assertTrue(C.gate_length("The record hypothesizes that due to large differences between fire behavior in "
                                      "normal and reduced gravity, the use of terrestrial fire standards presents an "
                                      "inherent risk.")[0])

    def test_dangling_reference_and_missing_full_stop(self):
        ok, why = C.gate_length("The record hypothesizes that testing aboard the ISS can demonstrate the following "
                                "for the first time.")
        self.assertFalse(ok)
        self.assertIn("the following", why)
        self.assertFalse(C.gate_length("The investigation aimed to study flame spread over thin fuels")[0])

    def test_added_certainty(self):
        # PSI-21 S1: 'focused on gathering bench mark data to validate' became 'will validate'
        q = "This investigation was focused on gathering bench mark data to validate the hypothesis of computation models"
        ok, why = C.gate_hedge("The record hypothesizes that gathering benchmark data will validate the hypothesis "
                               "of computational models.", [q])
        self.assertFalse(ok)
        self.assertIn("'will'", why)
        # a 'will' that the quote has is kept
        self.assertTrue(C.gate_hedge("The record hypothesizes that electric fields will significantly influence "
                                     "laminar diffusion flames.", [text("PSI-22", "HYP-1")])[0])

    def test_result_verbs_added_by_the_review(self):
        evid = ev1("PSI-25", "OBJ-3")
        for verb in ("determined", "verified", "concluded", "yielded"):
            ok, why = C.gate_modality(f"The investigation aimed to study ignition and {verb} the extinction limits.",
                                      evid, "PSI-25", EV)
            self.assertFalse(ok, verb)
            self.assertIn(verb, why)

    def test_number_and_quantity_words(self):
        q = text("PSI-25", "OBJ-3")
        self.assertFalse(C.gate_numbers("The investigation aimed to study solid fuels at thirty percent oxygen.", [q])[0])
        ok, why = C.gate_numbers("The investigation aimed to show that solid fuels burn twice as fast.", [q])
        self.assertFalse(ok)
        self.assertIn("twice", why)

    def test_application_words_must_be_in_the_record(self):
        # none of the 24 records says lunar, Martian, habitat, rover or spacesuit
        for inv, rec in EV["records"].items():
            joined = " ".join(u["text"] for u in rec["units"]).lower()
            for w in ("lunar", "martian", "habitat", "rover", "spacesuit"):
                self.assertNotRegex(joined, rf"\b{w}\b", (inv, w))
        ok, why = C.gate_entities("The investigation aimed to inform fire protection for a lunar habitat.", "PSI-25", EV)
        self.assertFalse(ok)
        self.assertIn("lunar", why)
        self.assertTrue(C.gate_entities("The record states that a primary goal is improved spacecraft fire safety.",
                                        "PSI-25", EV)[0])
        # 'spacecraft' is not in the E-FIELD Flames objective text of every record: it is checked, not assumed
        has = bool(__import__("re").search(r"\bcrew\b", C.record_text("PSI-10", EV), __import__("re").I))
        self.assertEqual(C.gate_entities("The investigation aimed to protect the crew.", "PSI-10", EV)[0], has)

    def test_advice_lexicon_additions(self):
        for s in ("The cabin can be operated safely at this oxygen level.",
                  "The record makes recommendations for cabin design.",
                  "NASA found that the fabric burns.",
                  "This material is acceptable for flight."):
            self.assertFalse(C.gate_policy(s)[0], s)

    def test_first_batch_rejections_by_gate(self):
        """The 69 candidates of the first batch: the gates reject the ones named in the review."""
        path = config.AI_DIR / "runs" / "cards_20261114-v2-all24.jsonl"
        if not path.exists():
            self.skipTest("the first batch log is not here")
        rejected = set()
        total = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("kind") != "candidate":
                continue
            for srow in row["sentences"]:
                total += 1
                res = C.check_sentence(srow["text"], srow["evidence"], row["record"], EV, n_summary=len(row["sentences"]))
                if not res["ok"]:
                    rejected.add((row["record"], srow["n"]))
        self.assertEqual(total, 69)
        for must in (("PSI-21", 1), ("PSI-26", 0), ("PSI-26", 1), ("PSI-39", 1), ("PSI-68", 1), ("PSI-98", 0),
                     ("PSI-99", 1), ("PSI-159", 1)):
            self.assertIn(must, rejected)
        print(f"\n  first batch under the reviewed gates: {total - len(rejected)} of {total} pass, "
              f"{len(rejected)} rejected")


if __name__ == "__main__":
    unittest.main()
