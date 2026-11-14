# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for the review verdicts on quotes and templates (14 Nov, after the data role's review):

- a quote row marked not_relevant is not shown on its card (key point dropped, the pick rule goes on to its
  next candidate; the quoted slot of a removed sentence uses the next unit it cited, or is left out; a card's
  last quoted summary sentence is kept and listed);
- the review sheet lists what the reviewed cards show (rows with shown = yes) plus the rows whose verdict
  removed their sentence (shown = no), and a rewrite is a fixed point;
- the reworded templates (partial-gravity gap, monitoring-ranges gap, spacesuit result notes).

No model is called: the cards are rebuilt from the logged candidates in ai/runs/.

    python3 -m unittest -v ai.test_review_quotes
"""
import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from ai import apply_cards as A, apply_review as R, build_baseline as BB, check_all, checks as C, config
from ai import evidence as evmod, templates as T

CARDS = config.INSIGHTS_DIR / "cards.json"
SCENARIOS = config.INSIGHTS_DIR / "scenarios.json"
QUALITY = config.INSIGHTS_DIR / "quality.json"
RV = {"verdict": "not_relevant", "reviewer_kind": "ai_session", "reviewer_role": "data"}


def quiet(*a, **k):
    return None


def by_id(res):
    return {c["investigation_id"]: c for c in res["cards"]}


def quote_items(card):
    return {A.quote_item(card["investigation_id"], s) for s in card["sentences"] if s["origin"] == "quote"}


class Hidden(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ev = evmod.load()
        cls.ctx = BB.Ctx()
        cls.res = A.build(log=quiet, ctx=cls.ctx)
        cls.cards = by_id(cls.res)

    def build(self, hidden, **kw):
        return A.build(log=quiet, ctx=self.ctx, hidden_quotes=hidden, **kw)

    def _model_card_with_baseline_kp(self):
        """A model card with a key point taken from the quoted baseline (not a first cited unit)."""
        for inv, c in self.cards.items():
            if c["status"] == "fallback_quote":
                continue
            firsts = {s["evidence"][0]["id"] for s in c["sentences"] if s["origin"] == "model"}
            for s in c["sentences"]:
                if s["role"] == "key_point" and not {e["id"] for e in s["evidence"]} & firsts:
                    return inv, s
        self.skipTest("no model card with a baseline key point")


class KeyPointTest(Hidden):
    def test_marked_key_point_is_not_shown_and_nothing_else_changes(self):
        inv, s = self._model_card_with_baseline_kp()
        res = self.build({A.quote_key(inv, s): RV})
        c = by_id(res)[inv]
        self.assertNotIn(A.quote_item(inv, s), quote_items(c))
        self.assertFalse(any(s["text"] in kp["text"] for kp in c["key_points"]))
        self.assertEqual([h["item"] for h in c["hidden_by_review"]], [A.quote_item(inv, s)])
        self.assertEqual(c["hidden_by_review"][0]["verdict"], "not_relevant")
        self.assertEqual(len(res["stats"]["hidden_quotes"]), 1)
        self.assertEqual(res["stats"]["hidden_rows_matching_no_quote"], [])
        # the model sentences and the summary stay as they were: nothing is reworded
        self.assertEqual(c["summary"], self.cards[inv]["summary"])
        for other, c0 in self.cards.items():
            if other != inv:
                self.assertEqual(by_id(res)[other], c0, other)
        # what the pick rule shows instead comes from its own candidates, all verbatim and unmarked
        before = [k["text"] for k in self.cards[inv]["key_points"] if k["text"] != T.key_point(s["field_label"], s["text"])]
        after = [k["text"] for k in c["key_points"]]
        self.assertEqual(after[:len(before)], before)

    def test_marked_first_cited_unit_keeps_its_model_sentence_and_check_all_accepts_it(self):
        inv = next(i for i, c in self.cards.items() if c["status"] != "fallback_quote")
        c0 = self.cards[inv]
        m = next(s for s in c0["sentences"] if s["origin"] == "model")
        kp = next(s for s in c0["sentences"] if s["role"] == "key_point"
                  and m["evidence"][0]["id"] in {e["id"] for e in s["evidence"]})
        res = self.build({A.quote_key(inv, kp): RV})
        c = by_id(res)[inv]
        self.assertIn(m["text"], c["summary"])                       # the model sentence stays
        self.assertNotIn(A.quote_item(inv, kp), quote_items(c))      # its key point does not
        rep = check_all.Report()
        check_all.check_card(rep, json.loads(json.dumps(c)), self.ev)
        self.assertEqual(rep.failures(), [])
        # without the hidden_by_review entry the same card would fail the key-point check
        bare = json.loads(json.dumps(c))
        bare.pop("hidden_by_review")
        rep2 = check_all.Report()
        check_all.check_card(rep2, bare, self.ev)
        self.assertTrue(any("first cited unit" in x["message"] for x in rep2.failures()))

    def test_a_marked_row_whose_text_changed_hides_nothing(self):
        inv, s = self._model_card_with_baseline_kp()
        item, _ = A.quote_key(inv, s)
        res = self.build({(item, "0" * 16): RV})
        self.assertEqual(by_id(res)[inv], self.cards[inv])
        self.assertEqual(res["stats"]["hidden_rows_matching_no_quote"], [item])


class SlotTest(Hidden):
    def _prereview_two_cites(self, d):
        """A temporary pm_prereview.json that removes a model sentence citing two quotable units, on a card
        that keeps another model sentence (so the slot is shown)."""
        for inv, c in self.cards.items():
            ms = [s for s in c["sentences"] if s["origin"] == "model"]
            for s in ms:
                ids = [e["id"] for e in s["evidence"]]
                if len(ms) > 1 and len(ids) > 1 and all(evmod.unit(inv, i, self.ev)["quotable"] for i in ids):
                    p = Path(d) / "pre.json"
                    p.write_text(json.dumps([{"investigation_id": inv, "sentence": s["text"], "reason": "test",
                                              "reviewer_kind": "ai_session_pm"}]), encoding="utf-8")
                    return inv, s, p
        self.skipTest("no model sentence with two quotable cited units on a card with two model sentences")

    def test_slot_uses_the_next_cited_unit_then_none(self):
        with tempfile.TemporaryDirectory() as d:
            inv, s, pre = self._prereview_two_cites(d)
            r1 = A.build(log=quiet, ctx=self.ctx, prereview_path=pre)
            slot = next(x for x in by_id(r1)[inv]["sentences"] if x.get("replaces"))
            self.assertEqual(slot["evidence"][-1]["id"], s["evidence"][0]["id"])
            # first cited unit marked: the slot shows the next unit the removed sentence cited
            r2 = A.build(log=quiet, ctx=self.ctx, prereview_path=pre, hidden_quotes={A.quote_key(inv, slot): RV})
            c2 = by_id(r2)[inv]
            slot2 = next(x for x in c2["sentences"] if x.get("replaces"))
            second = s["evidence"][1]["id"]
            self.assertIn(second, [e["id"] for e in slot2["evidence"]])
            self.assertIn(f'{slot2["field_label"]} "{slot2["text"]}"', c2["summary"])
            self.assertNotIn(f'"{slot["text"]}"', c2["summary"])
            self.assertEqual(c2["hidden_by_review"][0]["slot_of_removed_sentence"], slot["n"])
            self.assertEqual(c2["removed_before_review"][0]["replaced_by"], slot2["source"])
            self.assertIn(A.LABEL_SLOT, c2["label"])
            # both cited units marked: no slot; the card says the cited sentence is not shown
            r3 = A.build(log=quiet, ctx=self.ctx, prereview_path=pre,
                         hidden_quotes={A.quote_key(inv, slot): RV, A.quote_key(inv, slot2): RV})
            c3 = by_id(r3)[inv]
            self.assertFalse(any(x.get("replaces") for x in c3["sentences"]))
            self.assertIsNone(c3["removed_before_review"][0]["replaced_by"])
            self.assertIn(A.LABEL_SLOT_NONE, c3["label"])
            self.assertTrue(c3["summary"].strip())
            self.assertTrue(any(x["origin"] == "model" for x in c3["sentences"]))

    def test_psi159_slot_on_disk(self):
        """HYP-1 of PSI-159 was marked not_relevant; the removed sentence cited only HYP-1, so no slot."""
        if not CARDS.exists():
            self.skipTest("run python3 ai/build_all.py first")
        c = {x["investigation_id"]: x for x in json.loads(CARDS.read_text(encoding="utf-8"))}["PSI-159"]
        self.assertNotIn("can demonstrate the following for the first time", c["summary"])
        self.assertTrue(c["summary"].strip())
        self.assertIsNone(c["removed_before_review"][0]["replaced_by"])


class FallbackTest(Hidden):
    def test_baseline_key_point_dropped_and_last_summary_quote_kept(self):
        base = self.res["baseline"]
        inv = next(i for i in sorted(base, key=BB.acc_key)
                   if sum(s["role"] == "summary" for s in base[i]["sentences"]) == 1
                   and any(s["role"] == "key_point" for s in base[i]["sentences"]))
        b = base[inv]
        kp = next(s for s in b["sentences"] if s["role"] == "key_point")
        summ = next(s for s in b["sentences"] if s["role"] == "summary")
        hidden_log, kept = [], []
        c = A.hide_in_base(json.loads(json.dumps(b)), inv, {A.quote_key(inv, kp): RV, A.quote_key(inv, summ): RV},
                           hidden_log, kept)
        self.assertNotIn(T.key_point(kp["field_label"], kp["text"]), [k["text"] for k in c["key_points"]])
        self.assertEqual(len(c["key_points"]), len(b["key_points"]) - 1)
        self.assertEqual(c["summary"], b["summary"])           # the last summary quote stays ...
        self.assertEqual([k["item"] for k in kept], [A.quote_item(inv, summ)])   # ... and is listed
        self.assertEqual([h["item"] for h in hidden_log], [A.quote_item(inv, kp)])

    def test_one_of_two_summary_quotes_dropped(self):
        base = self.res["baseline"]
        two = [i for i in base if sum(s["role"] == "summary" for s in base[i]["sentences"]) == 2]
        if two:
            inv = two[0]
            b = base[inv]
        else:  # no card of the current data has two (ai/build_baseline.py card: a short first objective)
            inv = sorted(base, key=BB.acc_key)[0]
            b = json.loads(json.dumps(base[inv]))
            objs = [u for u in evmod.units(inv, "objective", ev=self.ev) if u["quotable"]]
            if len(objs) < 2:
                self.skipTest("no record with two quotable objective sentences")
            u = objs[1]
            b["sentences"].insert(1, BB.sentence(inv, "summary", "objective", "Stated objective:", u["text"],
                                                 u["char_start"], u["char_end"], [u]))
        first = next(s for s in b["sentences"] if s["role"] == "summary")
        c = A.hide_in_base(json.loads(json.dumps(b)), inv, {A.quote_key(inv, first): RV}, [], [])
        self.assertNotIn(f'"{first["text"]}"', c["summary"])
        self.assertTrue(c["summary"].startswith("Quoted from the PSI record. Stated objective: "))


class SheetTest(Hidden):
    def test_rows_shown_and_not_shown(self):
        c = self.cards
        inv, kp = self._model_card_with_baseline_kp()
        res = self.build({A.quote_key(inv, kp): RV})
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sheet.csv"
            out = R.write_sheet(res["cards"], scenarios=[], path=p, not_shown=res["stats"]["not_shown"])
            rows = R.read_sheet(p)
        self.assertEqual(out["not_shown"], 1)
        hid = [r for r in rows if r["shown"] == "no"]
        self.assertEqual([(r["item"], r["origin"]) for r in hid], [(A.quote_item(inv, kp), "quote")])
        model, quotes = R.card_rows(res["cards"], self.ev)
        self.assertEqual({(r["item"], r["sentence_sha"]) for r in rows if r["shown"] == "yes"},
                         {(r["item"], r["sentence_sha"]) for r in model + quotes})
        self.assertTrue(c)

    def test_refresh_is_a_fixed_point_and_keeps_every_verdict(self):
        if not R.SHEET.exists():
            self.skipTest("run python3 ai/build_all.py first")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sheet.csv"
            shutil.copy(R.SHEET, p)
            before = R.read_sheet(p)
            R.refresh_sheet(path=p)
            once = p.read_bytes()
            R.refresh_sheet(path=p)
            self.assertEqual(p.read_bytes(), once)
            after = {(r["item"], r["sentence_sha"]): r for r in R.read_sheet(p)}
        removing = [r for r in before if (r["origin"] == "model" and r["verdict"] in ("partly", "not"))
                    or (r["origin"] == "quote" and r["verdict"] == "not_relevant")]
        for r in removing:  # a verdict that removes its sentence is never lost by a rewrite
            k = (r["item"], r["sentence_sha"])
            self.assertIn(k, after, r["item"])
            self.assertEqual(after[k]["verdict"], r["verdict"])
            self.assertEqual(after[k]["shown"], "no")
        for k, r in after.items():  # the reviewer columns are carried over unchanged
            old = next((o for o in before if (o["item"], o["sentence_sha"]) == k), None)
            if old:
                self.assertEqual({c: old[c] for c in R.REVIEW_COLUMNS}, {c: r[c] for c in R.REVIEW_COLUMNS})


class OnDiskTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (CARDS.exists() and R.SHEET.exists() and SCENARIOS.exists()):
            raise unittest.SkipTest("run python3 ai/build_all.py first")
        cls.ev = evmod.load()
        cls.cards = json.loads(CARDS.read_text(encoding="utf-8"))
        with R.SHEET.open(encoding="utf-8", newline="") as f:
            cls.rows = list(csv.DictReader(f))

    def test_no_quote_marked_not_relevant_is_shown(self):
        shown = {(A.quote_item(c["investigation_id"], s), A._sha(s["text"]))
                 for c in self.cards for s in c["sentences"] if s["origin"] == "quote"}
        marked = [r for r in self.rows if r["origin"] == "quote" and r["verdict"] == "not_relevant"]
        self.assertGreater(len(marked), 0)
        q = json.loads(QUALITY.read_text(encoding="utf-8")) if QUALITY.exists() else None
        kept = {k["item"] for k in (q or {}).get("quotes_not_shown_by_review", {}).get("kept_although_marked", [])}
        for r in marked:
            if r["item"] in kept:
                continue
            self.assertNotIn((r["item"], r["sentence_sha"]), shown, r["item"])
            self.assertEqual(r["shown"], "no", r["item"])
        if q:
            self.assertEqual(q["quotes_not_shown_by_review"]["n"], len(marked) - len(kept))
            self.assertNotIn("quotes_not_shown_by_review", q["verdicts"])

    def test_check_all_sheet_section_passes(self):
        rep = check_all.Report()
        check_all.check_sheet(rep, CARDS, SCENARIOS, self.ev)
        self.assertEqual(rep.failures(), [])

    def test_four_key_points_of_the_independent_check_have_rows(self):
        items = {r["item"] for r in self.rows if r["shown"] == "yes"}
        for inv in ("PSI-20", "PSI-23", "PSI-62", "PSI-69"):
            c = next(x for x in self.cards if x["investigation_id"] == inv)
            for s in c["sentences"]:
                if s["origin"] == "quote":
                    self.assertIn(A.quote_item(inv, s), items)


class TemplateWordingTest(unittest.TestCase):
    def test_spacesuit_note_speaks_of_this_investigation_only(self):
        t = T.note_spacesuit(95, 100)
        self.assertNotIn("inverse flames among them", t)
        self.assertNotIn("results are listed", t)
        self.assertIn("mapped PSI tables", t)
        self.assertTrue(C.check_template(t, {"o2": [95, 100]})["ok"])

    def test_partial_gravity_gap(self):
        t = T.gap_partial_gravity("Material flammability in partial gravity", 1824)
        self.assertIn("1,824 mapped tests", t)
        self.assertIn("source mapping sets the gravity level per table", t)
        self.assertNotIn("every test in the PSI tables", t.lower())
        self.assertTrue(C.check_template(t, {"mapped_tests": 1824})["ok"])
        self.assertFalse(C.check_template(t, {"mapped_tests": 1867})["ok"])  # the count must be the facts value

    def test_monitoring_gap_names_the_document_and_drops_required(self):
        t = T.gap_monitoring_targets("Toxic combustion products other than carbon monoxide (HCN, HCl, HF)",
                                     "NASA Spaceflight Human-System Standard", "NASA-STD-3001-V2",
                                     ["carbon monoxide", "carbon dioxide"])
        self.assertNotIn("Required", t)
        self.assertIn("NASA-STD-3001-V2", t)
        self.assertIn("the mapped PSI tables record carbon monoxide and carbon dioxide only", t)
        self.assertTrue(C.check_template(t, {})["ok"])

    def test_scenarios_on_disk(self):
        if not SCENARIOS.exists():
            self.skipTest("run python3 ai/build_all.py first")
        sc = json.loads(SCENARIOS.read_text(encoding="utf-8"))
        texts = [g["text"] for s in sc for g in s["gaps"]] + [x["text"] for s in sc for x in s["result_notes"]]
        for t in texts:
            self.assertNotIn("Required monitoring targets", t)
            self.assertNotIn("every test in the PSI tables is a microgravity test", t)
            self.assertNotIn("inverse flames among them", t)
        reworded = [g for s in sc for g in s["gaps"] if g["rule"].startswith("not_covered_reworded:")]
        self.assertEqual({g["rule"] for g in reworded},
                         {"not_covered_reworded:TB008.gaps", "not_covered_reworded:3001.T6.2-3"})
        with (config.ROOT / BB.F_TESTS).open(encoding="utf-8", newline="") as f:
            tests = list(csv.DictReader(f))
        for g in reworded:
            if g["rule"].endswith("TB008.gaps"):
                self.assertEqual(g["facts"]["mapped_tests"], len(tests))
        notes = {x["investigation_id"]: x["text"] for s in sc if s["id"] == "spacesuit" for x in s["result_notes"]}
        for inv in ("PSI-68", "PSI-62"):  # no test-level table: the note claims no listed result or inverse flame
            if inv in notes:
                self.assertNotIn("inverse", notes[inv])

    def test_build_stops_when_the_gravity_mapping_changes(self):
        ctx = BB.Ctx()
        sid = next(iter({t["source_id"] for t in ctx.tests}))
        ctx.source[sid] = dict(ctx.source[sid], constants=dict(ctx.source[sid]["constants"], gravity_level="1g"))
        with self.assertRaises(BB.BuildStop):
            BB.mapped_gravity_tests(ctx)

    def test_header_comment(self):
        first = (config.AI_DIR / "test_review_quotes.py").read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(first, config.HEADER_COMMENT)


if __name__ == "__main__":
    unittest.main()
