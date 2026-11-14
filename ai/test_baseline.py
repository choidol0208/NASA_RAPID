# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for ai/build_baseline.py (design component A2).

    python3 -m unittest -v ai.test_baseline

The anchor counts are recomputed here by a second code path that reads tests.csv, need_tests.csv and
pipeline/spec/scenarios.json only (not scenario_needs.csv or scenario_tests.csv), then compared with the
'facts' the build stored and with a third path, the data role's evidence packages
(data/pipeline/evidence/scenario_<id>.json) and investigation_facts.json. No count is hard-coded: the data
role's audit moved them (1,867 -> 1,824 test rows, 377 -> 376 solid tests, ISS P1 oxygen-only 55 -> 58).
Only the rules the text states are fixed here (no solid test with a pressure value, no lunar S1 extinction,
only ambient oxygen inside the bins).
"""
import copy
import csv
import json
import re
import unittest
from collections import Counter
from pathlib import Path

from ai import build_baseline as B, checks as C, config, resolve as R, templates as T

ROOT = config.ROOT


def _csv(rel):
    with open(ROOT / rel, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _in(v, r):
    lo = r.get("min") is None or v > r["min"] or (v == r["min"] and r.get("min_inclusive", True))
    hi = r.get("max") is None or v < r["max"] or (v == r["max"] and r.get("max_inclusive", False))
    return lo and hi


class SecondPath:
    """Counts from tests.csv + need_tests.csv + scenarios.json, independent of the pipeline's scenario files."""

    def __init__(self):
        self.tests = {t["test_id"]: t for t in _csv(B.F_TESTS)}
        self.links = _csv(B.F_NEED_TESTS)
        self.scen = {s["id"]: s for s in json.loads((ROOT / B.F_SCENARIOS).read_text())["scenarios"]}

    def stated(self, need):
        return [r["test_id"] for r in self.links if r["need_id"] == need and r["objective_link"] == "stated"]

    def tier(self, sc, t):
        r = self.scen[sc]["ranges"]
        row = self.tests[t]
        o = row["o2_pct"]
        p = row["pressure_kpa"]
        o_in = bool(o) and row["o2_basis"] == "ambient" and "o2_pct" in r and _in(float(o), r["o2_pct"])
        p_in = bool(p) and "pressure_kpa" in r and _in(float(p), r["pressure_kpa"])
        if o_in and p_in:
            return "atmosphere"
        if o_in and not p and "pressure_kpa" in r:
            return "oxygen_only"
        if p_in and not o and "o2_pct" in r:
            return "pressure_only"
        return "other"

    def ids(self, sc, need, tier):
        return [t for t in self.stated(need) if self.tier(sc, t) == tier]


def package_need(sc, nid):
    doc = json.loads((ROOT / B.F_PACKAGES / f"scenario_{sc}.json").read_text(encoding="utf-8"))
    return next(n for n in doc["needs"] if n["need_id"] == nid)


class BuiltFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = B.build()
        cls.sc = {e["id"]: e for e in cls.res["scenarios"]}
        cls.sp = SecondPath()
        cls.ctx = cls.res["ctx"]

    def need(self, sc, nid):
        return next(n for n in self.sc[sc]["needs"] if n["need_id"] == nid)

    # ---------------------------------------------------------------- anchors (design A2 validation)
    def test_solid_anchors(self):
        solid = [t for t in self.sp.tests.values() if t["fuel_phase"] == "solid"]
        facts = json.loads((ROOT / "data/pipeline/investigation_facts.json").read_text(encoding="utf-8"))
        tables = [t for i in facts["investigations"] for t in i.get("tables", [])
                  if (t.get("constants") or {}).get("fuel_phase") == "solid"]
        self.assertEqual(len(solid), sum(t["tests"] for t in tables))  # third path
        self.assertEqual(self.res["global"]["solid_tests"], len(solid))
        # rule the text states: no solid-sample test has a pressure value
        self.assertEqual(sum(1 for t in solid if t["pressure_kpa"]), 0)
        top = max(float(t["o2_pct"]) for t in solid if t["o2_pct"])
        self.assertEqual(top, max((t["variables"].get("o2_pct") or {}).get("max") or 0 for t in tables))
        amb = [float(t["o2_pct"]) for t in self.sp.tests.values() if t["o2_basis"] == "ambient" and t["o2_pct"]]
        g = self.res["global"]
        self.assertEqual(g["max_solid_o2"][0], top)
        self.assertEqual(g["max_ambient_o2"][0], max(amb))
        gap = next(x for x in self.sc["lunar_habitat"]["gaps"] if x["rule"] == "solid_at_atmosphere")
        self.assertIn(f"above {T.num(top)}%", gap["text"])

    def test_lunar_s1_anchor(self):
        ids = self.sp.ids("lunar_habitat", "S1", "atmosphere")
        pk = package_need("lunar_habitat", "S1")
        self.assertEqual(len(ids), pk["counts"]["atmosphere"])
        self.assertEqual({self.sp.tests[t]["investigation_id"] for t in ids},
                         {m["investigation_id"] for m in pk["matched_tests"] if m["tier"] == "atmosphere"})
        # rule the text states: none of the matched lunar S1 tests is recorded as an extinction
        self.assertFalse(any("extinction" in self.sp.tests[t]["test_end"] for t in ids))
        n = self.need("lunar_habitat", "S1")
        f = n["facts"]
        self.assertEqual(f["tests_atmosphere"], len(ids))
        self.assertEqual(f["balance_zero"], sum(1 for m in pk["matched_tests"] if m["added_gas"] == "none"))
        self.assertNotIn("test_end_extinction", f)
        ends = Counter(self.sp.tests[t]["test_end"] for t in ids)
        self.assertEqual(set(ends), {"disruption", "completion"})
        self.assertIn(f"The {len(ids)} matched tests ended in disruption ({ends['disruption']}) or completion "
                      f"({ends['completion']}); none is recorded as an extinction.", n["statement"])

    def test_iss_anchors(self):
        p1 = package_need("iss", "P1")
        self.assertEqual(len(self.sp.ids("iss", "P1", "oxygen_only")), p1["counts"]["oxygen_only"])
        self.assertEqual(self.need("iss", "P1")["facts"]["tests_oxygen_only"], p1["counts"]["oxygen_only"])
        s1 = package_need("iss", "S1")
        ids = self.sp.ids("iss", "S1", "atmosphere")
        self.assertEqual(len(ids), s1["counts"]["atmosphere"])
        diluted = [t for t in ids if float(self.sp.tests[t]["co2_pct"] or 0) > 0 or float(self.sp.tests[t]["he_pct"] or 0) > 0]
        marks = {m["test_id"]: m["added_gas"] for m in s1["matched_tests"]}
        self.assertEqual(len(diluted), sum(marks[t] == "co2_or_helium" for t in ids))  # the pipeline's added_gas
        f = self.need("iss", "S1")["facts"]
        self.assertEqual((f["tests_atmosphere"], f["balance_diluted"], f["balance_zero"]),
                         (len(ids), len(diluted), len(ids) - len(diluted)))
        self.assertEqual(f["tests_oxygen_only"], s1["counts"]["oxygen_only"])
        ends = Counter(self.sp.tests[t]["test_end"] for t in ids)
        self.assertEqual({k: f[f"test_end_{k}"] for k in ends}, dict(ends))

    def test_counts_equal_the_evidence_packages(self):
        for sc in ("iss", "lunar_habitat"):
            for n in self.sc[sc]["needs"]:
                pk = package_need(sc, n["need_id"])
                self.assertEqual(n["facts"]["usable_tests"], pk["counts"]["usable_tests"], (sc, n["need_id"]))
                self.assertEqual(n["status"], pk["status"], (sc, n["need_id"]))

    def test_pipeline_sentences_are_cited_and_used_as_written(self):
        for e in self.res["scenarios"]:
            for n in e["needs"]:
                cited = [x for x in n["sources"] if x.startswith(B.F_PACKAGES + "/")]
                ids = [x.split("/", 4)[-1] for x in cited]
                self.assertTrue(any(i.startswith("status.") for i in ids), (e["id"], n["need_id"]))
                self.assertIn("need.reading", ids)
                for x in cited:
                    value = R.resolve(x)["data"]["value"]
                    if not (isinstance(value, str) or (isinstance(value, dict) and "text" in value)):
                        continue  # a structured value (matched_ranges) is cited for its numbers, not as a sentence
                    self.assertIn(R.resolve(x)["text"].rstrip("."), n["statement"], x)
                need = self.ctx.need[n["need_id"]]
                self.assertIn(need["reading"].rstrip("."), n["statement"])

    def test_every_in_bin_test_is_ambient(self):
        for sc in self.sc:
            for n in self.ctx.needs:
                for tier in ("atmosphere", "oxygen_only"):
                    for t in self.sp.ids(sc, n["id"], tier):
                        self.assertEqual(self.sp.tests[t]["o2_basis"], "ambient")

    def test_second_path_recount_matches_every_fact(self):
        for sc, e in self.sc.items():
            for n in e["needs"]:
                f = n["facts"]
                self.assertEqual(f["usable_tests"], len(self.sp.stated(n["need_id"])), (sc, n["need_id"]))
                for tier, key in (("atmosphere", "tests_atmosphere"), ("oxygen_only", "tests_oxygen_only"),
                                  ("pressure_only", "tests_pressure_only")):
                    if key in f:
                        self.assertEqual(f[key], len(self.sp.ids(sc, n["need_id"], tier)), (sc, n["need_id"], tier))
                # every printed number is a facts value
                nums = set(re.findall(r"(?<![\w.\-])\d+(?:\.\d+)?(?![\w.])", n["statement"]))
                vals = set()

                def walk(v):
                    if isinstance(v, bool):
                        return
                    if isinstance(v, (int, float)):
                        vals.add(T.num(v))
                    elif isinstance(v, dict):
                        for k, x in v.items():
                            walk(x)
                    elif isinstance(v, list):
                        for x in v:
                            walk(x)
                walk(f)
                spec = self.sp.scen[sc]["ranges"]
                for r in spec.values():
                    for k in ("min", "max"):
                        if r.get(k) is not None:
                            vals.add(T.num(r[k]))
                missing = {x for x in nums if x not in vals and not re.search(rf"PSI-{x}\b", n["statement"])}
                self.assertFalse(missing, (sc, n["need_id"], missing, n["statement"]))

    # ---------------------------------------------------------------- hard stops
    def test_unknown_status_stops(self):
        ctx = copy.copy(self.ctx)
        ctx.scen_needs = dict(self.ctx.scen_needs)
        row = dict(ctx.scen_needs[("iss", "P1")], status="covered")
        ctx.scen_needs[("iss", "P1")] = row
        with self.assertRaises(B.BuildStop):
            B.recount(ctx, "iss", "P1")

    def test_unknown_gap_code_stops(self):
        ctx = copy.copy(self.ctx)
        ctx.scen_needs = dict(self.ctx.scen_needs)
        row = dict(ctx.scen_needs[("iss", "P1")], gaps="pressure:not_recorded;flow:something_new")
        ctx.scen_needs[("iss", "P1")] = row
        with self.assertRaises(B.BuildStop):
            B.recount(ctx, "iss", "P1")

    def test_changed_count_stops(self):
        ctx = copy.copy(self.ctx)
        ctx.scen_needs = dict(self.ctx.scen_needs)
        ctx.scen_needs[("lunar_habitat", "S1")] = dict(ctx.scen_needs[("lunar_habitat", "S1")], tests_atmosphere="26")
        with self.assertRaises(B.BuildStop):
            B.recount(ctx, "lunar_habitat", "S1")

    def test_every_status_and_gap_code_has_a_template(self):
        self.assertEqual(len(T.STATUSES), 6)
        spec = json.loads((ROOT / "pipeline/spec/statements.json").read_text(encoding="utf-8"))
        codes = {g["code"].replace("{gravity_level}", lvl) for g in spec["statements"]["gap"]
                 for lvl in (("lunar", "martian") if "{gravity_level}" in g["code"] else ("",))}
        self.assertEqual(codes, set(T.GAP_CODES))  # nine, with flow:not_recorded and flow:no_usable_test_in_range
        self.assertIn("flow:no_usable_test_in_range", T.GAP_CODES)
        for c in T.GAP_CODES:
            self.assertTrue(c in T.GAP_PIPELINE_SENTENCE or c in ("oxygen:not_recorded", "pressure:not_recorded",
                                                                  "need:no_usable_test"), c)
        seen = {r["status"] for r in self.ctx.scen_needs.values()}
        self.assertLessEqual(seen, set(T.STATUSES))
        self.assertEqual(len(self.ctx.needs), 6)
        self.assertNotIn("P4", [n["id"] for n in self.ctx.needs])

    # ---------------------------------------------------------------- shape
    def test_shape_and_order(self):
        self.assertEqual([e["id"] for e in self.res["scenarios"]], ["iss", "lunar_habitat", "spacesuit", "mars_habitat"])
        need_ids = [n["id"] for n in self.ctx.needs]
        for e in self.res["scenarios"]:
            self.assertEqual(e["ranking_source"], "scoring.scorer.rank")
            self.assertEqual([n["need_id"] for n in e["needs"]], need_ids)
            # code-built text: the page tags text_origin 'template' as computed by team code
            self.assertIs(e["ai_generated"], False)
            self.assertEqual((e["text_origin"], e["frame_text_origin"]), ("template", "template"))
            self.assertIsNone(e["reviewed_by"])
            self.assertEqual(e["model"], T.SCENARIO_MODEL)
            for n in e["needs"]:
                self.assertTrue(n["statement"].startswith("Recorded tests (team count;"))
                self.assertEqual(n["text_origin"], "template")
                self.assertTrue(all(isinstance(s, str) for s in n["sources"]))
            for g in e["gaps"] + e["result_notes"]:
                self.assertEqual(g["text_origin"], "template")
            for g in e["gaps"]:
                self.assertTrue(g["text"] and g["needed_data"])
        self.assertNotIn("exploration_8_2_34", self.sc)

    def test_every_source_resolves(self):
        for s in set(B.all_sources(self.res["scenarios"]) + B.all_sources(self.res["cards"])):
            self.assertTrue(R.check(s), s)

    # ---------------------------------------------------------------- result notes
    def test_note_ids_are_top3_plus_near_ties(self):
        from scoring import scorer
        for sc, q in T.QUERIES:
            out = scorer.rank(q)
            top = [r["psi_accession"] for r in out["results"]]
            s3 = out["results"][-1]["score"]
            near = [r["psi_accession"] for r in out["ranking"] if r["psi_accession"] not in top
                    and abs(r["score"] - s3) < 3.0 - 1e-9]
            self.assertEqual([n["investigation_id"] for n in self.sc[sc]["result_notes"]], top + near, sc)
        iss = [n["investigation_id"] for n in self.sc["iss"]["result_notes"]]
        self.assertIn("PSI-100", iss)
        self.assertIn("PSI-98", iss)
        self.assertEqual(len(self.sc["mars_habitat"]["result_notes"]), 5)

    def test_notes_have_no_score_rank_or_best(self):
        from scoring import scorer
        for sc, q in T.QUERIES:
            scores = {f"{r['score']:.1f}" for r in scorer.rank(q)["ranking"]}
            for n in self.sc[sc]["result_notes"]:
                t = n["text"]
                self.assertNotRegex(t, r"\bbest\b", t)
                self.assertNotRegex(t, r"\brank(ed|s)?\s*(#|no\.?\s*)?\d", t)
                self.assertNotRegex(t, r"\b(first|second|third)\b(?! two)", t)
                for s in scores:
                    # a number with a unit after it is a value of the note (config 1.1.0 gives one lunar score of
                    # 70.3, the kPa of the challenge-statement bound), not a printed score
                    self.assertNotRegex(t, rf"(?<![\d.]){re.escape(s)}(?![\d.]|\s?(kPa|psi|atm|%|cm/s))", (sc, s, t))

    def test_no_table_only_without_sources_entry(self):
        with_entry = {s["investigation_id"] for s in self.ctx.sources}
        flagged = set()
        for e in self.res["scenarios"]:
            for n in e["result_notes"]:
                if T.NOTE_NO_TABLE in n["text"]:
                    self.assertNotIn(n["investigation_id"], with_entry)
                    flagged.add(n["investigation_id"])
        no_entry = {r for r in self.ctx.ev["records"] if r not in with_entry}
        self.assertEqual(no_entry, {"PSI-60", "PSI-62", "PSI-115", "PSI-117"})
        self.assertLessEqual(flagged, no_entry)

    def test_psi20_note_recomputed_from_table(self):
        with open(ROOT / B.TABLE_DIR / "PSI-20_Experimental table_ACME BRE.csv", newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 18)
        self.assertEqual(sum(int(r["Flames Ignited"]) for r in rows), 194)
        note = next(n for n in self.sc["lunar_habitat"]["result_notes"] if n["investigation_id"] == "PSI-20")
        self.assertEqual((note["facts"]["test_days"], note["facts"]["flames_ignited"]), (18, 194))
        self.assertEqual((note["facts"]["o2_setting_min"], note["facts"]["o2_setting_max"]), (21.0, 40.0))
        self.assertEqual(note["facts"]["o2_cells_as_written"], ["3400%", "2100%"])
        self.assertIn("'not identified in this summary table'", note["text"])
        self.assertIn("Tied with FLEX", note["text"])

    # ---------------------------------------------------------------- wording
    BANNED = [r"\bcovered\b", r"\bunsafe\b", r"\bsafe\b", r"\bpredict", r"\bnever tested\b", r"\bbest\b",
              r"\b101(\.\d)? ?kPa\b", r"\btreat microgravity\b", r"\bshould\b", r"\bwill burn\b",
              r"\bburns more easily\b"]

    def test_wording_linter(self):
        """Team text is read in full; a span in quotation marks that is verbatim NASA text is not (the copied
        PSI-26 line quotes 'models and predictions of heat release')."""
        for e in self.res["scenarios"]:
            texts = [e["frame"]] + [n["statement"] for n in e["needs"]] + [n["text"] for n in e["result_notes"]] \
                + [g["text"] + " " + g["needed_data"] for g in e["gaps"]]
            for t in texts:
                t = C.strip_nasa_quotes(t)
                for pat in self.BANNED:
                    self.assertNotRegex(t, pat, (e["id"], pat, t))
                # 'bounds' only in the negated form
                for m in re.finditer(r"\bbounds?\b", t):
                    self.assertRegex(t[max(0, m.start() - 60):m.start()], r"\bnot\b", t)
                self.assertNotIn("recommend", t.replace("Working Group report recommends", "")
                                 .replace("as recommendations rather than requirements", ""))

    def test_linter_reads_team_text_and_skips_verbatim_nasa_quotes(self):
        copied = next(g["text"] for g in self.sc["iss"]["gaps"] if g["text"].startswith("Heat release"))
        self.assertRegex(copied, r"\bpredict")                      # the NASA phrase is there, quoted
        self.assertNotRegex(C.strip_nasa_quotes(copied), r"\bpredict")
        self.assertTrue(C.check_template(copied, {"x": 1})["checks"]["banned_ok"])
        unquoted = copied.replace("'", "")
        self.assertFalse(C.check_template(unquoted, {})["checks"]["banned_ok"])  # team wording is read

    def test_gravity_frames(self):
        for sc in ("lunar_habitat", "mars_habitat"):
            self.assertIn(T.FRAME_GRAVITY, self.sc[sc]["frame"])
            self.assertTrue(any(g["rule"].startswith("gravity:") for g in self.sc[sc]["gaps"]))
            self.assertIn(f"{B.F_REFS}#TB008.gaps", self.sc[sc]["frame_sources"])
        for sc in ("iss", "spacesuit"):
            self.assertNotIn(T.FRAME_GRAVITY, self.sc[sc]["frame"])
        # TB008.gaps is cited only by the gravity gap (or the copied partial-gravity line where there is none)
        for e in self.res["scenarios"]:
            cites = [g for g in e["gaps"] if f"{B.F_REFS}#TB008.gaps" in g["sources"]]
            self.assertEqual(len(cites), 1, e["id"])

    def test_reference_items_used_where_the_design_planned_them(self):
        refs = {it["id"]: it for r in json.loads((ROOT / B.F_REFS).read_text())["references"] for it in r.get("items", [])}
        # Olson and Ferkul Table I: once, in the frame of the lunar and Martian scenarios, with the 5.18 s
        # drop-tower caveat and no Fig. 6 average
        self.assertIn("5.18 s drop tower tests", refs["OF2012.table1"]["text"])
        for sc in ("lunar_habitat", "mars_habitat"):
            fr = self.sc[sc]["frame"]
            self.assertEqual(fr.count("Olson and Ferkul"), 1, sc)
            self.assertIn("5.18 s drop-tower tests", fr)
            self.assertIn("extinction criteria are not the same as in 1 g", fr)
            self.assertIn(f"{B.F_REFS}#OF2012.table1", self.sc[sc]["frame_sources"])
            self.assertNotRegex(fr, r"-?2\.6\s?%|2\.7\s?%")
            self.assertFalse(any("Olson" in g["text"] for g in self.sc[sc]["gaps"]), sc)
        # the comparison the lunar frame states, recomputed here from the rows of Table I
        rows_of = refs["OF2012.table1"]["values"]["rows"]
        self.assertTrue(all(r[f"{k}_star_o2_pct_lunar"] < r[f"{k}_o2_pct_1g"]
                            and r[f"{k}_star_o2_pct_lunar"] < r[f"{k}_star_o2_pct_0g"]
                            for r in rows_of for k in ("uloi", "moc")))
        lunar = self.sc["lunar_habitat"]["frame"]
        self.assertIn(f"for {T.NUMBER_WORD[len(rows_of)]} materials; for each of them, both limits at lunar gravity "
                      "are lower than those at 1 g and at 0 g.", lunar)
        self.assertEqual(self.sc["lunar_habitat"]["frame_facts"]["of2012_materials_in_table"], len(rows_of))
        # the item does not say whose drop tower it was, and the paper is on NTRS
        self.assertNotIn("NASA drop-tower tests", lunar)
        self.assertIn("a paper on the NASA Technical Reports Server (Olson and Ferkul, NTRS-20130010991)", lunar)
        # Martian: both limits below 1 g for every material, below 0 g only for some (Mylar G is above its 0 g limits)
        mars_below_0g = [all(r[f"{k}_star_o2_pct_martian"] < r[f"{k}_star_o2_pct_0g"] for k in ("uloi", "moc"))
                         for r in rows_of]
        self.assertTrue(any(mars_below_0g) and not all(mars_below_0g))
        self.assertIn("for each of them, both limits at Martian gravity are lower than those at 1 g, and for some "
                      "of them they are lower than those at 0 g as well.", self.sc["mars_habitat"]["frame"])
        for sc in ("iss", "spacesuit"):
            self.assertNotIn("Olson and Ferkul", self.sc[sc]["frame"])
        # Saffire IV to VI (SAF456.conditions): in the solid gap, the samples inside the team bins with the
        # numbers of Table 1, never called measured values or set points, never counted
        rows = refs["SAF456.conditions"]["values"]["rows"]
        for sc in ("iss", "lunar_habitat"):
            rg = self.sp.scen[sc]["ranges"]
            inside = [r for r in rows if B.in_range(r["o2_pct"], rg["o2_pct"]) and B.in_range(r["pressure_kpa"], rg["pressure_kpa"])]
            gap = next(g for g in self.sc[sc]["gaps"] if g["rule"] == "solid_at_atmosphere")
            self.assertIn(f"{B.F_REFS}#SAF456.conditions", gap["sources"])
            self.assertIn(f"the {T.NUMBER_WORD[len(rows)]} Saffire IV to VI samples considered in that paper", gap["text"])
            for r in inside:
                self.assertIn(f"{r['flight_sample']} ({r['o2_pct']:.1f} mol % oxygen, {r['pressure_kpa']:.1f} kPa)", gap["text"])
            for r in rows:
                if r not in inside:
                    self.assertNotIn(f"{r['flight_sample']} (", gap["text"])
            self.assertNotRegex(gap["text"], r"\bmeasured\b|\bset points?\b")
            self.assertEqual(gap["facts"]["saffire_samples_counted"], 0)
        self.assertEqual([r["flight_sample"] for r in rows if B.in_range(r["o2_pct"], self.sp.scen["lunar_habitat"]["ranges"]["o2_pct"])
                          and B.in_range(r["pressure_kpa"], self.sp.scen["lunar_habitat"]["ranges"]["pressure_kpa"])],
                         ["VI-2", "VI-3"])

    # ---------------------------------------------------------------- careful-reader pass (14 Nov, afternoon)
    def test_lunar_challenge_bound_caveat_is_recounted_and_shown_wherever_the_count_is(self):
        """coord/decisions.md 14:15: no counted test at 30% oxygen or more and at or below 10.2 psi; the 17
        matched droplet tests were recorded 1 to 2 kPa above it. Recounted here from tests.csv, need_tests.csv
        and references.json only."""
        refs = {it["id"]: it for r in json.loads((ROOT / B.F_REFS).read_text())["references"] for it in r.get("items", [])}
        ch = refs["CH.moonbase"]["values"]
        bound = ch["pressure_psia_max"] * 6.894757
        counted = {r["test_id"] for r in self.sp.links if r["objective_link"] == "stated"}
        tests = self.sp.tests
        below = [t for t in counted if tests[t]["o2_basis"] == "ambient" and tests[t]["o2_pct"] and tests[t]["pressure_kpa"]
                 and float(tests[t]["o2_pct"]) >= ch["o2_pct_min"] and float(tests[t]["pressure_kpa"]) <= bound]
        self.assertEqual(below, [])  # the rule the sentence states
        inside = self.sp.ids("lunar_habitat", "S1", "atmosphere")
        every_need = {t for n in self.ctx.needs for t in self.sp.ids("lunar_habitat", n["id"], "atmosphere")}
        self.assertEqual(set(inside), every_need)  # S1 is the only need with tests inside the lunar bins
        ps = [float(tests[t]["pressure_kpa"]) for t in inside]
        os_ = [float(tests[t]["o2_pct"]) for t in inside]
        self.assertGreater(min(ps), bound)  # every one of them is above the challenge-statement pressure
        lo, hi = int(round(min(ps))), int(round(max(ps)))  # whole kPa, as decision 14:15 words it
        above = (int(round(min(ps) - bound)), int(round(max(ps) - bound)))
        atm = {round(min(ps) / 101.325, 1), round(max(ps) / 101.325, 1)}
        self.assertEqual(len(atm), 1)
        atm = atm.pop()
        at = f"{T.num(min(os_))} to {T.num(max(os_))}% oxygen and about {T.num(atm)} atm ({lo} to {hi} kPa)"
        e = self.sc["lunar_habitat"]
        want_frame = (f"No counted test was recorded at {T.num(ch['o2_pct_min'])}% oxygen or more and at or below "
                      f"{T.num(ch['pressure_psia_max'])} psi; the {len(inside)} counted tests inside the bins are "
                      f"fuel-droplet tests recorded {above[0]} to {above[1]} kPa above it, at {at}.")
        self.assertIn(want_frame, e["frame"])
        # the challenge statement in the item's own wording (hedges kept), and the data role's caveat as written
        self.assertIn(refs["CH.moonbase"]["text"].rstrip(". "), e["frame"])
        self.assertIn(f"({T.num(ch['pressure_psia_max'])} psi = {round(bound, 1)} kPa)", e["frame"])
        pk = json.loads((ROOT / B.F_PACKAGES / "scenario_lunar_habitat.json").read_text(encoding="utf-8"))
        self.assertIn(pk["environment"]["caveat"], e["frame"])
        self.assertIn(f"{B.F_PACKAGES}/scenario_lunar_habitat.json#environment.caveat", e["frame_sources"])
        f = e["frame_facts"]
        self.assertEqual(f["counted_tests_at_or_below_challenge_bound"], 0)
        self.assertEqual(f["counted_tests_inside_bins"], len(inside))
        self.assertEqual(sorted(f["recorded_pressure_kpa_in_tests_csv"].values()), [min(ps), max(ps)])
        self.assertEqual(f["kpa_above_challenge_bound_rounded"], list(above))
        # the matched ranges of the data role's package equal this recount and are cited
        s1_pk = package_need("lunar_habitat", "S1")["matched_ranges"]
        self.assertEqual((s1_pk["pressure_kpa"]["min"], s1_pk["pressure_kpa"]["max"]), (min(ps), max(ps)))
        self.assertEqual((s1_pk["o2_pct"]["min"], s1_pk["o2_pct"]["max"]), (min(os_), max(os_)))
        self.assertTrue(any(x.endswith(".matched_ranges") for x in e["frame_sources"]))
        # 'about 0.7 atm' is printed because the data role's scenario note names 0.7 atm; the frame cites it
        note_src = next(x for x in e["frame_sources"] if x.startswith(f"{B.F_SCENARIOS}#scenarios."))
        note = R.resolve(note_src)["text"]
        self.assertEqual(note, self.sp.scen["lunar_habitat"]["note"])
        self.assertIn(f"{T.num(atm)} atm", note)
        # wherever the count of the matched tests is shown, the recorded oxygen and pressure are next to it
        short = (f"recorded at {at}, {above[0]} to {above[1]} kPa above the {T.num(ch['pressure_psia_max'])} psi "
                 f"({round(bound, 1)} kPa) of the challenge statement")
        s1 = self.need("lunar_habitat", "S1")["statement"]
        self.assertIn(f"These {len(inside)} were recorded at {at}", s1)
        self.assertIn(f"{above[0]} to {above[1]} kPa above the {T.num(ch['pressure_psia_max'])} psi ({round(bound, 1)} kPa) of the "
                      "challenge statement (CH.moonbase) and inside the team's wider pressure bin; no counted test was "
                      "recorded at", s1)
        self.assertTrue(any(x.endswith(".matched_ranges") for x in self.need("lunar_habitat", "S1")["sources"]))
        gap = next(g for g in e["gaps"] if g["rule"] == "s1_phase_droplets_only")
        self.assertIn(f"They were {short}.", gap["text"])
        note69 = next(n for n in e["result_notes"] if n["investigation_id"] == "PSI-69")
        self.assertIn(f"inside this scenario's team bins ({short})", note69["text"])
        for t in (e["frame"], s1, gap["text"], note69["text"]):
            self.assertNotRegex(t, r"at or below 10\.2 psi(?! \()[^.:;]*\b17\b")  # never '17 ... at or below 10.2 psi'
            self.assertNotIn("in the lunar-habitat atmosphere", t)
        # the ISS scenario does not rest on the challenge statement: no such sentence there
        iss = self.sc["iss"]
        for t in [iss["frame"]] + [n["statement"] for n in iss["needs"]] + [g["text"] for g in iss["gaps"]]:
            self.assertNotIn("challenge statement (CH.moonbase)", t)
            self.assertNotIn("Moon Base", t)
        self.assertNotIn("counted_tests_at_or_below_challenge_bound", iss["frame_facts"])

    # ---------------------------------------------------------------- 14:59 merge (literature check of the links)
    def test_objective_links_supported_only_and_never_an_empty_field(self):
        links = _csv(B.F_OBJ_LINKS)
        supported = {(r["need_id"], r["investigation_id"]) for r in links if r["verdict"] == "supported"}
        # every counted test belongs to a supported link (need_tests.csv 'stated' = verdict 'supported')
        for r in self.sp.links:
            if r["objective_link"] == "stated":
                self.assertIn((r["need_id"], r["investigation_id"]), supported, r)
        for e in self.res["scenarios"]:
            for item in e["needs"] + e["result_notes"]:
                for s in item["sources"]:
                    self.assertNotRegex(s, r"^PSI-\d+\.$", s)  # the 'PSI-25.' failure of the interrupted run
                    self.assertTrue(R.check(s), s)
        # D1/PSI-25 has no record field: it is cited through its publication item
        d1 = self.need("iss", "D1")
        self.assertIn(f"{B.F_REFS}#BASS2TM.products", d1["sources"])
        self.assertIn(f"{B.F_OBJ_LINKS}#D1/PSI-25", d1["sources"])
        # a link with verdict 'differs' or 'topic_only' is never named as a stated objective in a note
        not_supported = {(r["need_id"], r["investigation_id"]) for r in links} - supported
        for e in self.res["scenarios"]:
            for n in e["result_notes"]:
                for nid in n["facts"].get("needs_stated", []):
                    self.assertNotIn((nid, n["investigation_id"]), not_supported)
        note25 = next(n for n in self.sc["iss"]["result_notes"] if n["investigation_id"] == "PSI-25")
        self.assertIn("D1 (Combustion products) to an objective stated in a publication on this investigation",
                      note25["text"])

    def test_detection_gap_is_built_from_d1_and_d2_as_they_are(self):
        for sc in ("iss", "lunar_habitat"):
            gap = next(g for g in self.sc[sc]["gaps"] if g["rule"] == "detection")
            d1, d2 = len(self.sp.stated("D1")), len(self.sp.stated("D2"))
            self.assertEqual((gap["facts"]["d1_counted_tests"], gap["facts"]["d2_counted_tests"]), (d1, d2))
            if d2 == 0:
                self.assertIn("no test is counted for smoke generation conditions (D2)", gap["text"])
            if d1:
                self.assertIn(f"the {d1} tests counted for combustion products (D1", gap["text"])

    def test_documented_elsewhere_sentences_are_used_as_written_next_to_the_gap(self):
        p1 = self.need("iss", "P1")
        cited = [s for s in p1["sources"] if ".statements." in s]
        self.assertTrue(cited)
        for s in cited:
            self.assertIn(R.resolve(s)["text"], p1["statement"])
        self.assertIn("The sentence is not used as a value of any test.", p1["statement"])

    def test_two_tests_read_as_both(self):
        p3 = self.need("iss", "P3")
        if p3["facts"].get("tests_oxygen_only") == 2:
            self.assertNotIn("All 2 ", p3["statement"])
            self.assertIn("Both come from", p3["statement"])

    def test_reading_that_contradicts_the_count_is_reported(self):
        # pipeline/spec/needs.json D1 reading says no test is counted although the literature check counts
        # BASS-II tests for D1; the build reports it and keeps the reading as written (not pm's file)
        reading = self.ctx.need["D1"]["reading"]
        if self.sp.stated("D1") and B.READING_SAYS_NONE.search(reading):
            self.assertTrue(any("/D1:" in w for w in self.res["warnings"]))
            self.assertIn(reading.rstrip("."), self.need("iss", "D1")["statement"])

    def test_flow_comparison_says_where_the_remaining_tests_are(self):
        for sc in ("iss",):
            r = self.sp.scen[sc]["ranges"]["flow_cms"]
            for n in self.sc[sc]["needs"]:
                matched = self.sp.ids(sc, n["need_id"], "atmosphere") + self.sp.ids(sc, n["need_id"], "oxygen_only")
                if not matched:
                    continue
                flows = [self.sp.tests[t]["flow_cms"] for t in matched]
                out = sum(1 for v in flows if v and not _in(float(v), r))
                self.assertEqual(n["facts"]["matched_flow_in_range"] + n["facts"]["matched_flow_not_recorded"] + out,
                                 len(matched), (sc, n["need_id"]))
                if out:
                    self.assertEqual(n["facts"]["matched_flow_outside_range"], out)
                    self.assertIn(f"The other {out} were recorded with a flow speed outside that range.", n["statement"])
                else:
                    self.assertNotIn("outside that range", n["statement"])
        self.assertIn("matched_flow_outside_range", self.need("iss", "P1")["facts"])  # the case exists today

    def test_reader_wording_fixes(self):
        texts = {sc: [e["frame"]] + [n["statement"] for n in e["needs"]] + [g["text"] for g in e["gaps"]]
                 + [n["text"] for n in e["result_notes"]] for sc, e in self.sc.items()}
        for sc, ts in texts.items():
            for t in ts:
                # one name per table: the PSI record's acronym (SAFFIRE-II), not the file name's (SAFFIRE-2)
                self.assertNotRegex(t, r"SAFFIRE-[123]\b", (sc, t))
                # the FLEX table does not define its 'Test end' words; no physical claim about a disruption
                self.assertNotIn("Droplet disruption is not flame extinction", t)
                self.assertNotIn("usable for smoke generation", t)
                self.assertNotIn("are quoted as written", t)
        for sc in ("iss", "lunar_habitat"):
            for n in self.sc[sc]["needs"]:
                counted = n["facts"]["usable_tests"]
                if "tests_recorded_outside_objective" in n["facts"]:
                    k = n["facts"]["tests_recorded_outside_objective"]
                    # 'further' only where tests are counted
                    self.assertIn(f"{k} further tests record" if counted else f"{k} tests record", n["statement"])
                    self.assertEqual("further tests record" in n["statement"], bool(counted))
                if n["status"] in ("in_atmosphere", "oxygen_only"):
                    self.assertNotIn("By investigation:", n["statement"])  # the breakdown names its tests
            self.assertIn("A test whose table holds no pressure value, or no oxygen value, is reported apart",
                          self.sc[sc]["frame"])
        s1 = self.need("iss", "S1")["statement"]
        self.assertIn("'Disruption' and 'extinction' are separate values of the table's 'Test end' column", s1)
        # the breakdown of ISS P1 follows the count it breaks down
        p1 = self.need("iss", "P1")
        k = p1["facts"]["tests_oxygen_only"]
        self.assertEqual(sum(p1["facts"]["oxygen_only_by_investigation"].values()), k)
        self.assertIn(f"The {k} by investigation: ", p1["statement"])

    # ---------------------------------------------------------------- second careful-reader pass (14 Nov)
    def test_no_counted_test_is_not_no_test_uncounted_tests_at_or_below_the_bound_are_named(self):
        """'No counted test was recorded at 30% oxygen or more and at or below 10.2 psi' is about counted tests.
        Tests that are counted for no need and were recorded there are named in the lunar frame, and the result
        note of the investigation says where its tests inside the bins were recorded. Recounted here from
        tests.csv, need_tests.csv and references.json only."""
        refs = {it["id"]: it for r in json.loads((ROOT / B.F_REFS).read_text())["references"] for it in r.get("items", [])}
        ch = refs["CH.moonbase"]["values"]
        bound = ch["pressure_psia_max"] * 6.894757
        tests = self.sp.tests
        counted = {r["test_id"] for r in self.sp.links if r["objective_link"] == "stated"}
        at_or_below = [t for t, row in tests.items() if row["o2_basis"] == "ambient" and row["o2_pct"]
                       and row["pressure_kpa"] and float(row["o2_pct"]) >= ch["o2_pct_min"]
                       and float(row["pressure_kpa"]) <= bound]
        self.assertTrue(at_or_below)  # such tests exist in the tables today (PSI-159 at about half an atmosphere)
        self.assertFalse(set(at_or_below) & counted)  # and none of them is counted: the decision's sentence holds
        invs = sorted({tests[t]["investigation_id"] for t in at_or_below}, key=B.acc_key)
        e = self.sc["lunar_habitat"]
        self.assertEqual(e["frame_facts"]["investigations_with_uncounted_tests_at_or_below_challenge_bound"], invs)
        supported = {r["investigation_id"] for r in _csv(B.F_OBJ_LINKS) if r["verdict"] == "supported"}
        for acc in invs:
            self.assertNotIn(acc, supported)  # the reason the frame gives
            kinds = {(tests[t]["fuel_phase"], tests[t]["sample_geometry"]) for t in at_or_below
                     if tests[t]["investigation_id"] == acc}
            self.assertEqual(len(kinds), 1)
            noun = T.cap(T.kind_noun(*next(iter(kinds)), 2))
            self.assertIn(f"{noun} of {self.ctx.name(acc)} were recorded at {T.num(ch['o2_pct_min'])}% oxygen or more "
                          f"and at or below {T.num(ch['pressure_psia_max'])} psi; they are counted for no need, because "
                          "the team pipeline links none of the needs to an objective stated for that investigation.",
                          e["frame"])
            self.assertTrue(any(s.startswith(f"{B.F_TESTS}#") and tests[s.split("#")[1]]["investigation_id"] == acc
                                for s in e["frame_sources"]))
        # the frame prints no count of them (ai/check_all.py has no second path for it); the result note does,
        # for the tests inside the team bins
        in_bins = [t for t in tests if self.sp.tier("lunar_habitat", t) == "atmosphere"
                   and tests[t]["investigation_id"] == "PSI-159"]
        self.assertTrue(in_bins)
        self.assertTrue(all(float(tests[t]["pressure_kpa"]) <= bound for t in in_bins))
        self.assertFalse(set(in_bins) & counted)
        os_ = [float(tests[t]["o2_pct"]) for t in in_bins]
        ps = [float(tests[t]["pressure_kpa"]) for t in in_bins]
        note = next(n for n in e["result_notes"] if n["investigation_id"] == "PSI-159")
        want = (f"{len(in_bins)} of its {sum(1 for t in tests.values() if t['investigation_id'] == 'PSI-159' and t['o2_basis'] == 'ambient' and t['o2_pct'])} "
                f"tests with recorded ambient oxygen have oxygen and pressure inside this scenario's team bins "
                f"(recorded at {int(round(min(os_)))} to {int(round(max(os_)))}% oxygen and {int(round(min(ps)))} kPa, "
                f"below the {T.num(ch['pressure_psia_max'])} psi ({round(bound, 1)} kPa) of the challenge statement; "
                "counted for no need)")
        self.assertEqual(int(round(min(ps))), int(round(max(ps))))
        self.assertIn(want, note["text"])
        self.assertEqual(note["facts"]["recorded_o2_pct"], {"min": min(os_), "max": max(os_)})
        self.assertEqual(note["facts"]["tests_inside_bins_counted_for_a_need"], 0)
        # the same tests are never worded as above the bound, and the FLEX note keeps the decision's wording
        self.assertNotIn("kPa above", note["text"])
        # no such sentence where the scenario does not rest on the challenge statement
        self.assertNotIn("counted for no need", self.sc["iss"]["frame"])

    def test_scenario_caveat_is_shown_as_the_teams_data_note_in_quotation_marks(self):
        """The data role's caveat is addressed to readers of its package ('Read the recorded pressure ...'); it
        is given as written, inside quotation marks, and every scenario that has one shows it."""
        for sc in ("iss", "lunar_habitat"):
            pk = json.loads((ROOT / B.F_PACKAGES / f"scenario_{sc}.json").read_text(encoding="utf-8"))
            caveat = pk["environment"]["caveat"]
            self.assertTrue(caveat)
            self.assertIn(f"The team's data note on these ranges reads: \"{caveat}\"", self.sc[sc]["frame"])
            self.assertIn(f"{B.F_PACKAGES}/scenario_{sc}.json#environment.caveat", self.sc[sc]["frame_sources"])
            self.assertEqual(self.sc[sc]["frame"].count(caveat), 1)
        for sc in ("spacesuit", "mars_habitat"):
            pk = json.loads((ROOT / B.F_PACKAGES / f"scenario_{sc}.json").read_text(encoding="utf-8"))
            if not pk["environment"].get("caveat"):
                self.assertNotIn("data note", self.sc[sc]["frame"])

    def test_evidence_rule_says_who_matched_the_sentences(self):
        meta = json.loads((ROOT / B.F_NEEDS).read_text(encoding="utf-8"))["_meta"]
        unreviewed = "not human-reviewed" in meta["generated_by"].lower()
        for e in self.res["scenarios"]:
            self.assertIn(T.FRAME_RULE, e["frame"])
            self.assertEqual(T.FRAME_RULE_AI in e["frame"], unreviewed)
            self.assertNotIn("counts only the links that the publications it read support", e["frame"])

    def test_a_reading_that_contradicts_the_count_gets_a_team_note(self):
        reading = self.ctx.need["D1"]["reading"]
        n_d1 = len(self.sp.stated("D1"))
        for sc in ("iss", "lunar_habitat"):
            for n in self.sc[sc]["needs"]:
                r = self.ctx.need[n["need_id"]]["reading"]
                contradicts = bool(n["facts"]["usable_tests"]) and bool(B.READING_SAYS_NONE.search(r))
                self.assertEqual("Team note: this reading still says that no test is counted" in n["statement"],
                                 contradicts, (sc, n["need_id"]))
                self.assertIn(r.rstrip("."), n["statement"])  # the reading itself stays as written
        if n_d1 and B.READING_SAYS_NONE.search(reading):
            links = [r for r in _csv(B.F_OBJ_LINKS) if r["need_id"] == "D1" and r["verdict"] == "supported"]
            self.assertTrue(all(not r["record_field"].strip() and r["publication_item"].strip() for r in links))
            items = sorted({r["publication_item"] for r in links})
            self.assertTrue(self.need("iss", "D1")["statement"].endswith(
                f"Team note: this reading still says that no test is counted; the {n_d1} tests in the count above "
                f"are counted, through a purpose sentence in a publication on PSI-25 (BASS-II) ({T.join_and(items)}) "
                "and not in the PSI record."))

    def test_texts_speak_of_the_tables_used_here_not_of_all_of_psi(self):
        for sc in ("iss", "lunar_habitat"):
            e = self.sc[sc]
            team = [e["frame"]] + [g["text"] for g in e["gaps"] if g["status"] == "from_rule"]
            for t in team:
                self.assertNotIn("Every test in the PSI tables", t)
                self.assertNotIn("the PSI test tables", t)
            gap = next(g for g in e["gaps"] if g["rule"] == "detection")
            self.assertNotIn("no pressure in the table", gap["text"])
            if gap["facts"]["d1_not_columns"]:
                self.assertIn("no pressure value in the PSI experimental tables", gap["text"])
            solid = next(g for g in e["gaps"] if g["rule"] == "solid_at_atmosphere")
            self.assertIn(f"In the PSI experimental tables of the {self.ctx.n_investigations} investigations used here",
                          solid["text"])
            # the droplet gap speaks of the counted tests: uncounted gas-burner tests lie inside the same bins
            drop = next(g for g in e["gaps"] if g["rule"] == "s1_phase_droplets_only")
            n_s1 = len(self.sp.ids(sc, "S1", "atmosphere"))
            self.assertTrue(drop["text"].startswith(f"The {n_s1} counted tests inside this scenario's team bins"))
            uncounted_gas = [t for t, row in self.sp.tests.items() if self.sp.tier(sc, t) == "atmosphere"
                             and row["fuel_phase"] == "gas"]
            self.assertTrue(uncounted_gas)
            self.assertFalse(set(uncounted_gas) & {r["test_id"] for r in self.sp.links if r["objective_link"] == "stated"})
        grav = next(g for g in self.sc["lunar_habitat"]["gaps"] if g["rule"].startswith("gravity:"))
        self.assertIn("Every test in the PSI experimental tables used here is a microgravity test", grav["text"])
        self.assertTrue(all(t["gravity_level"] == "microgravity" for t in self.sp.tests.values()))

    def test_tests_outside_the_objective_never_contradict_the_psi_record(self):
        """'(PSI-99) does not state this need as an objective' was wrong: the PSI-99 record names the objective
        and the card quotes it; the link is marked 'differs' by the literature check. The clause says that the
        pipeline has no supported match, and for a 'differs' link what the record and the publications say."""
        links = _csv(B.F_OBJ_LINKS)
        seen_differs = 0
        for sc in ("iss", "lunar_habitat"):
            for n in self.sc[sc]["needs"]:
                self.assertNotIn("not state this need as an objective", n["statement"])
                outside = sorted({self.sp.tests[r["test_id"]]["investigation_id"] for r in self.sp.links
                                  if r["need_id"] == n["need_id"] and r["objective_link"] != "stated"}, key=B.acc_key)
                if not outside:
                    self.assertNotIn("supported match", n["statement"])
                    continue
                self.assertIn("the team pipeline has no supported match between this need and a purpose sentence of "
                              f"the investigation{'s' if len(outside) > 1 else ''} ({T.join_and(outside)})",
                              n["statement"])
                for acc in outside:
                    rows = [r for r in links if r["need_id"] == n["need_id"] and r["investigation_id"] == acc]
                    self.assertFalse(any(r["verdict"] == "supported" for r in rows))
                    differs = [r for r in rows if r["verdict"] == "differs" and r["record_field"].strip()]
                    if differs:
                        seen_differs += 1
                        rec = json.loads((config.PSI_CATALOG_DIR / f"{acc}.json").read_text(encoding="utf-8"))
                        for r in differs:  # the record does name the objective: the quoted words are in its field
                            self.assertIn(" ".join(r["quote"].split()), " ".join(rec[r["record_field"]].split()))
                        items = sorted({r["publication_item"] for r in differs if r["publication_item"].strip()})
                        self.assertIn(f"The PSI record of {acc} names this objective, but the publications that were "
                                      f"read state a different purpose for this investigation ({T.join_and(items)}).",
                                      n["statement"])
                        for i in items:
                            self.assertIn(f"{B.F_REFS}#{i}", n["sources"])
                        self.assertEqual(n["facts"]["outside_objective_link_verdicts"][acc], "differs")
                    else:
                        self.assertNotIn(f"The PSI record of {acc} names this objective", n["statement"])
        self.assertGreater(seen_differs, 0)  # PSI-98 for P1 and PSI-99 for P3 today

    # ---------------------------------------------------------------- cards
    def test_cards_are_verbatim_quotes(self):
        cards = self.res["cards"]
        self.assertEqual(len(cards), 24)
        for c in cards:
            acc = c["investigation_id"]
            self.assertEqual(c["status"], "fallback_quote")
            self.assertFalse(c["ai_generated"])
            self.assertEqual(c["model"], T.CARD_MODEL)
            self.assertIsNone(c["reviewed_by"])
            self.assertLessEqual(len(c["key_points"]), 4)
            self.assertTrue(c["summary"].startswith('Quoted from the PSI record. Stated objective: "'))
            rec = json.loads((config.PSI_CATALOG_DIR / f"{acc}.json").read_text(encoding="utf-8"))
            for s in c["sentences"]:
                field = s["source"].split(".", 1)[1]
                self.assertEqual(B.ws(rec[field][s["char_start"]:s["char_end"]]), s["text"], (acc, s["text"]))
                self.assertEqual(s["origin"], "quote")
                self.assertIsNone(s["review"])
                for ev in s["evidence"]:
                    self.assertEqual(rec[field][ev["char_start"]:ev["char_end"]], ev["quote"])
                self.assertIn(f'"{s["text"]}"', c["summary"] + " ".join(k["text"] for k in c["key_points"]))
            for k in c["key_points"]:
                self.assertRegex(k["text"], r'^(Planned approach:|Stated hypothesis:|Impact statement in the record:) "')
                self.assertTrue(R.check(k["source"]))

    def test_build_is_deterministic(self):
        again = B.build()
        strip = lambda xs: [{k: v for k, v in x.items() if k != "updated"} for x in xs]  # noqa: E731
        self.assertEqual(json.dumps(strip(again["scenarios"])), json.dumps(strip(self.res["scenarios"])))
        self.assertEqual(json.dumps(strip(again["cards"])), json.dumps(strip(self.res["cards"])))


class WrittenFiles(unittest.TestCase):
    """The files as ai/build_all.py leaves them: scenarios.json from ai/build_baseline.py; cards.json from the
    last card step (ai/apply_cards.py, or ai/apply_review.py when verdicts were applied), which runs after the
    baseline and replaces its quoted cards."""

    def test_files_on_disk(self):
        for path, n in ((B.OUT_SCENARIOS, 4), (B.OUT_CARDS, 24)):
            if not path.exists():
                self.skipTest("run python3 ai/build_all.py first")
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(data, list)  # the page requires arrays
            self.assertEqual(len(data), n)
        meta = json.loads((config.INSIGHTS_DIR / "_meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["scenarios.json"]["built_by"], "ai/build_baseline.py")
        self.assertEqual(meta["scenarios.json"]["language_model_used_at_build"], "none")
        cards = json.loads(B.OUT_CARDS.read_text(encoding="utf-8"))
        n_model = sum(s["origin"] == "model" for c in cards for s in c["sentences"])
        self.assertIn(meta["cards.json"]["built_by"], ("ai/build_baseline.py", "ai/apply_cards.py", "ai/apply_review.py"))
        self.assertEqual(meta["cards.json"]["language_model_used_at_build"],
                         config.MODEL_LABEL if n_model else "none")
        for name in ("scenarios.json", "cards.json"):
            m = meta[name]
            self.assertEqual(m["code_written_with"], "AI assistant (Claude Code)")
            self.assertTrue(m["inputs_sha256"] and m["generated_at"] and m["label"])
        for e in json.loads(B.OUT_SCENARIOS.read_text(encoding="utf-8")):
            self.assertEqual((e["text_origin"], e["frame_text_origin"], e["ai_generated"]), ("template", "template", False))

    def test_header_comment(self):
        for f in ("build_baseline.py", "templates.py", "test_baseline.py"):
            first = (config.AI_DIR / f).read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(first, config.HEADER_COMMENT)


if __name__ == "__main__":
    unittest.main()
