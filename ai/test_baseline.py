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
                    self.assertNotIn(s, t, (sc, s, t))

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
        lo, hi = round(min(ps), 1), round(max(ps), 1)
        above = (int(round(min(ps) - bound)), int(round(max(ps) - bound)))
        atm = {round(min(ps) / 101.325, 1), round(max(ps) / 101.325, 1)}
        self.assertEqual(len(atm), 1)
        e = self.sc["lunar_habitat"]
        want_frame = (f"No counted test was recorded at {T.num(ch['o2_pct_min'])}% oxygen or more and at or below "
                      f"{T.num(ch['pressure_psia_max'])} psi: the {len(inside)} counted tests inside the bins are "
                      f"fuel-droplet tests recorded at {T.num(min(os_))} to {T.num(max(os_))}% oxygen and {lo} to {hi} kPa "
                      f"(about {T.num(atm.pop())} atm), {above[0]} to {above[1]} kPa above it.")
        self.assertIn(want_frame, e["frame"])
        self.assertIn(f"{T.num(ch['pressure_psia_max'])} psi ({round(bound, 1)} kPa) or less as the expected Moon Base "
                      "atmosphere", e["frame"])
        self.assertIn("expected", refs["CH.moonbase"]["text"])  # the hedge kept in the frame is the item's own
        f = e["frame_facts"]
        self.assertEqual(f["counted_tests_at_or_below_challenge_bound"], 0)
        self.assertEqual(f["counted_tests_inside_bins"], len(inside))
        self.assertEqual(sorted(f["recorded_pressure_kpa_in_tests_csv"].values()), [min(ps), max(ps)])
        self.assertEqual(f["kpa_above_challenge_bound_rounded"], list(above))
        # the rounded pressures are stated by the data role's scenario note, which the frame cites
        note_src = next(x for x in e["frame_sources"] if x.startswith(f"{B.F_SCENARIOS}#scenarios."))
        note = R.resolve(note_src)["text"]
        self.assertEqual(note, self.sp.scen["lunar_habitat"]["note"])
        self.assertIn(f"{lo} to {hi} kPa", note)
        # wherever the count of the matched tests is shown, the recorded pressure is next to it
        short = f"recorded at {lo} to {hi} kPa, above the {T.num(ch['pressure_psia_max'])} psi ({round(bound, 1)} kPa) of the challenge statement"
        s1 = self.need("lunar_habitat", "S1")["statement"]
        self.assertIn(f"These {len(inside)} were recorded at {T.num(min(os_))} to {T.num(max(os_))}% oxygen and {lo} to {hi} kPa", s1)
        self.assertIn(f"{above[0]} to {above[1]} kPa above the {T.num(ch['pressure_psia_max'])} psi ({round(bound, 1)} kPa) of the "
                      "challenge statement (CH.moonbase); no counted test was recorded at", s1)
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
