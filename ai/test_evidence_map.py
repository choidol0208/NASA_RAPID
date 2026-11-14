# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for ai/evidence_map.py (component H). Run: python3 -m unittest -v ai.test_evidence_map

No count is hard-coded: each is recomputed here from data/pipeline/tests.csv by a second code path (the
data role's audit moved them: 1,867 -> 1,824 test rows). The Saffire IV to VI marks come from the item
SAF456.conditions of pipeline/spec/references.json and are never counted."""
import copy
import csv
import json
import re
import shutil
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

from ai import config, evidence_map as em, meta as metamod, resolve

ROOT = config.ROOT


def tests_by_id():
    return {t["test_id"]: t for t in em.read_csv(em.TESTS)}


class Built(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = em.build()
        cls.tests = tests_by_id()


class HeaderTest(unittest.TestCase):
    def test_header_comment(self):
        for f in ("evidence_map.py", "test_evidence_map.py"):
            first = (config.AI_DIR / f).read_text(encoding="utf-8").splitlines()[0]
            self.assertEqual(first, config.HEADER_COMMENT)


def second_path(tests):
    """Lane counts straight from tests.csv rows, without ai/evidence_map.py."""
    out = {}
    for ph in ("gas", "liquid", "solid"):
        rows = [t for t in tests.values() if t["fuel_phase"] == ph]
        plotted = [t for t in rows if t["o2_basis"] == "ambient" and t["o2_pct"].strip()]
        o2 = [float(t["o2_pct"]) for t in plotted]
        out[ph] = {"plotted": len(plotted), "max_o2_pct": max(o2) if o2 else None,
                   "at_or_above_30_pct_o2": sum(v >= 30 for v in o2), "not_plotted": len(rows) - len(plotted)}
    return out


class SumsTest(Built):
    def test_lanes_recomputed_by_a_second_path(self):
        lanes = self.p["sums"]["lanes"]
        for ph, want in second_path(self.tests).items():
            got = {k: lanes[ph][k] for k in want}
            self.assertEqual(got, want, ph)
            self.assertEqual(lanes[ph]["not_plotted"], lanes[ph]["not_plotted_oxidizer_stream"]
                             + lanes[ph]["not_plotted_no_ambient_oxygen_value"])
        self.assertEqual(sum(v["plotted"] + v["not_plotted"] for v in lanes.values()), len(self.tests))
        # rules the map states: no solid test above the highest solid value and none at 30% oxygen or more
        self.assertEqual(lanes["solid"]["at_or_above_30_pct_o2"], 0)

    def test_anchor_table_is_reported_not_forced(self):
        # ANCHORS is the recount of 14 November; a difference is printed by main(), never asserted here
        self.assertIsInstance(em.anchor_diffs(self.p), dict)

    def test_partition_of_tests_csv(self):
        s = self.p["sums"]
        self.assertEqual(s["plotted"] + s["oxidizer_stream"] + s["no_ambient_oxygen_value"], len(self.tests))
        self.assertEqual(s["total"], len(self.tests))
        self.assertEqual(s["tests_csv_rows"], len(self.tests))
        self.assertEqual(s["plotted_with_pressure"] + s["plotted_without_pressure"], s["plotted"])
        self.assertEqual(sum(s["balance_gas_with_pressure"].values()), s["plotted_with_pressure"])
        self.assertEqual(sum(s["balance_gas_all_plotted"].values()), s["plotted"])

    def test_every_test_in_exactly_one_point_and_rows_match(self):
        seen = Counter()
        for p in self.p["points"]:
            self.assertEqual(len(p["test_ids"]), p["n_tests"])
            for tid in p["test_ids"]:
                seen[tid] += 1
                t = self.tests[tid]  # KeyError if it does not resolve
                self.assertEqual(t["o2_basis"], "ambient")
                self.assertEqual(t["fuel_phase"], p["fuel_phase"])
                self.assertEqual(t["investigation_id"], p["investigation_id"])
                self.assertEqual(float(t["o2_pct"]), p["o2_pct"])
                self.assertEqual(em.num(t["pressure_kpa"]), p["pressure_kpa"])
                self.assertEqual(t["gravity_level"], "microgravity")
        self.assertEqual(max(seen.values()), 1)
        self.assertEqual(len(seen), self.p["sums"]["plotted"])

    def test_test_ids_resolve_through_the_resolver(self):
        for p in self.p["points"][::50]:
            r = resolve.resolve(f"data/pipeline/tests.csv#{p['test_ids'][0]}")
            self.assertEqual(r["form"], "file_ref")

    def test_points_are_distinct(self):
        keys = [(p["fuel_phase"], p["investigation_id"], p["o2_pct"], p["pressure_kpa"], p["balance_gas"])
                for p in self.p["points"]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_second_code_path_coverage_grid(self):
        # data role's coverage_grid.csv, counted by pipeline/run.py: ambient tests with an oxygen bin
        grid = em.read_csv(ROOT / "data/pipeline/coverage_grid.csv")
        c = Counter()
        for r in grid:
            if r["o2_basis"] == "ambient" and r["o2_bin"] != "not_recorded":
                c[r["fuel_phase"]] += int(r["tests"])
        self.assertEqual(dict(c), self.p["sums"]["plotted_by_phase"])
        ox = sum(int(r["tests"]) for r in grid if r["o2_basis"] == "oxidizer_stream")
        self.assertEqual(ox, self.p["sums"]["oxidizer_stream"])

    def test_oxidizer_stream_never_plotted(self):
        ids = {tid for p in self.p["points"] for tid in p["test_ids"]}
        for tid, t in self.tests.items():
            if t["o2_basis"] == "oxidizer_stream":
                self.assertNotIn(tid, ids)


class PressureTest(Built):
    def test_no_solid_point_has_pressure(self):
        self.assertFalse([p for p in self.p["points"] if p["fuel_phase"] == "solid" and p["pressure_kpa"] is not None])

    def test_null_pressure_is_never_zero_or_101(self):
        for p in self.p["points"]:
            self.assertNotEqual(p["pressure_kpa"], 0)
            if p["pressure_kpa"] is None:
                self.assertEqual(self.tests[p["test_ids"][0]]["pressure_kpa"], "")

    def test_solid_tables_have_no_pressure_column(self):
        for sid, e in self.p["pressure_column"].items():
            if e["fuel_phase"] == "solid":
                self.assertEqual(e["status"], "no column", sid)
                self.assertEqual(e["raw_pressure_columns"], [], sid)
        self.assertEqual(self.p["pressure_column"]["flex"]["status"], "column, some cells empty")
        self.assertEqual(self.p["pressure_column"]["flex"]["empty_reasons"], {"pressure_kpa:out_of_range": 1})

    def test_solid_max_and_label(self):
        self.assertEqual(self.p["sums"]["max_o2_by_phase"]["solid"], second_path(self.tests)["solid"]["max_o2_pct"])
        amb = [float(t["o2_pct"]) for t in self.tests.values() if t["o2_basis"] == "ambient" and t["o2_pct"].strip()]
        self.assertEqual(self.p["sums"]["max_o2_ambient"], max(amb))
        lab = self.p["labels"]["lane_notes"]["solid"]
        self.assertIn("above 22.2%", lab["end_label"])
        no_val = sum(1 for t in self.tests.values() if t["fuel_phase"] == "solid"
                     and not (t["o2_basis"] == "ambient" and t["o2_pct"].strip()))
        self.assertIn(f"{no_val} solid-sample tests record no oxygen value", lab["end_label"])
        self.assertEqual(lab["pressure_note"], "pressure is not a column in the PSI tables of the solid-sample tests")


class BalanceGasTest(Built):
    def test_n2_only_rows_are_oxygen_plus_nitrogen_in_the_nasa_table(self):
        tables = {}
        checked = flagged = 0
        for p in self.p["points"]:
            if p["balance_gas"] != "n2_only":
                continue
            for tid in p["test_ids"]:
                t = self.tests[tid]
                if t["source_file"] not in tables:
                    tables[t["source_file"]] = em.read_table(t["source_file"])
                tab = tables[t["source_file"]]
                header, row = tab[0], tab[int(t["source_row"]) - 1]
                n2_col = next(i for i, h in enumerate(header) if em._N2.search(h))
                o2 = float(t["o2_pct"]) / 100
                total = o2 + float(row[n2_col])
                if tid in p.get("gas_fractions_sum_test_ids", []):
                    self.assertGreater(abs(total - 1), em.COMPOSITION_TOLERANCE, tid)
                    self.assertIn(round(total, 6), p["gas_fractions_sum_as_written"])
                    flagged += 1
                else:
                    self.assertAlmostEqual(total, 1.0, delta=em.COMPOSITION_TOLERANCE, msg=tid)
                checked += 1
        self.assertEqual(checked, self.p["sums"]["balance_gas_all_plotted"]["n2_only"])
        off = {tid for p in self.p["points"] for tid in p.get("gas_fractions_sum_test_ids", [])}
        self.assertEqual(self.p["sums"]["tests_gas_fractions_not_summing_to_1"]["n"], len(off))
        self.assertLessEqual(flagged, len(off))  # n2_only rows only; the others have CO2 or He added

    def test_added_gas_values_match_rows(self):
        for p in self.p["points"]:
            if p["balance_gas"] == "co2_added":
                vals = {float(self.tests[i]["co2_pct"]) for i in p["test_ids"]}
                self.assertEqual(sorted(vals), p["co2_pct_values"])
                self.assertTrue(all(v > 0 for v in vals))
            if p["balance_gas"] == "he_added":
                vals = {float(self.tests[i]["he_pct"]) for i in p["test_ids"]}
                self.assertEqual(sorted(vals), p["he_pct_values"])

    def test_tables_without_diluent_column_are_not_recorded(self):
        for p in self.p["points"]:
            if p["source_id"] in ("flame_design_normal", "cfig_normal", "bass2", "saffire1", "saffire2"):
                self.assertEqual(p["balance_gas"], "not_recorded")

    def test_function_rules(self):
        cols = {"co2_pct", "he_pct"}
        row = {"test_id": "x", "co2_pct": "0.0", "he_pct": "0.0"}
        self.assertEqual(em.balance_gas(row, cols, True), "n2_only")
        self.assertEqual(em.balance_gas(row, cols, False), "not_recorded")
        self.assertEqual(em.balance_gas(dict(row, co2_pct=""), cols, True), "not_recorded")
        self.assertEqual(em.balance_gas(dict(row, he_pct="5"), cols, True), "he_added")
        self.assertEqual(em.balance_gas(row, set(), True), "not_recorded")
        with self.assertRaises(SystemExit):
            em.balance_gas(dict(row, co2_pct="5", he_pct="5"), cols, True)


class NotPlottedTest(Built):
    def test_counts_and_rules(self):
        n = self.p["not_plotted"]
        ox = [t for t in self.tests.values() if t["o2_basis"] == "oxidizer_stream"]
        self.assertEqual(n["oxidizer_stream"]["n"], len(ox))
        self.assertEqual(n["oxidizer_stream"]["without_oxygen_value"], sum(1 for t in ox if not t["o2_pct"].strip()))
        self.assertIn("crew breathes", n["oxidizer_stream"]["why"])
        a = n["no_ambient_oxygen_value"]
        no_val = [t for t in self.tests.values() if t["o2_basis"] != "oxidizer_stream"
                  and not (t["o2_basis"] == "ambient" and t["o2_pct"].strip())]
        amb_empty = [t["test_id"] for t in no_val if t["o2_basis"] == "ambient"]
        self.assertEqual((a["n"], a["no_oxygen_basis"], a["ambient_basis_without_value"]),
                         (len(no_val), sum(1 for t in no_val if not t["o2_basis"]), len(amb_empty)))
        self.assertEqual(sorted(a["ambient_basis_without_value_test_ids"]), sorted(amb_empty))
        self.assertEqual(sum(a["by_investigation"].values()), len(no_val))
        self.assertEqual(a["by_fuel_phase"], dict(Counter(t["fuel_phase"] for t in no_val)))
        self.assertTrue(a["rule"])

    def test_psi20_from_its_table(self):
        e = self.p["not_plotted"]["psi20_test_day_table"]
        self.assertEqual((e["days"], e["flames_ignited"]), (18, 194))
        self.assertEqual(e["oxygen_settings_as_written"], ["21", "25", "26.5", "34", "40"])
        self.assertEqual([c["cell"] for c in e["oxygen_cells_not_read_as_numbers"]], ["3400%", "2100%"])
        raw = (ROOT / e["source_file"]).read_text(encoding="utf-8-sig")
        self.assertIn(e["pressure"], raw)
        for note in e["table_notes_as_written"]:
            self.assertIn(note, raw)
        self.assertIn("not identified in this summary table", e["pressure"])
        self.assertTrue(resolve.check(e["source"]) and resolve.check(e["source_spec"]))


class TargetsTest(Built):
    KIND_RULE = {
        "nasa_design_atmosphere": lambda t: t["source"].startswith("pipeline/spec/references.json#")
        and "NASA" in t["issuer"] and t["reference_kind"] in ("nasa_report", "standard", "guideline"),
        "nasa_test_environment": lambda t: t["source"].startswith("pipeline/spec/references.json#")
        and "NASA" in t["issuer"] and t["reference_kind"] in ("nasa_report", "standard", "guideline"),
        "challenge_statement": lambda t: t["source"].startswith("pipeline/spec/references.json#")
        and t["reference_kind"] == "challenge",
        "team_preset": lambda t: t["source"].startswith("scoring/scoring_config.json#presets."),
        "team_counting_range": lambda t: t["source"].startswith("pipeline/spec/scenarios.json#"),
    }

    def test_every_target_resolves_and_kind_matches_source(self):
        ids = [t["id"] for t in self.p["targets"]]
        self.assertEqual(len(ids), len(set(ids)))
        for t in self.p["targets"]:
            r = resolve.resolve(t["source"])
            self.assertTrue(self.KIND_RULE[t["kind"]](t), t["id"])
            if t["source"].startswith("pipeline/spec/references.json#"):
                self.assertIn(t["as_written"], r["text"], t["id"])
                self.assertIn(t["access_note"], em.ACCESS_NOTE.values())
            if t["kind"].startswith("team_"):
                self.assertTrue(t["label"].startswith(t["label"].split(" (")[0]))
                self.assertIn("team", t["label"].lower())

    def test_values_and_access_notes(self):
        by = {t["id"]: t for t in self.p["targets"]}
        eawg = [(t["pressure_psia"], t["o2_pct"], t["pressure_kpa"]) for t in self.p["targets"]
                if t["source"].endswith("#EAWG.atmospheres")]
        self.assertEqual(eawg, [(14.7, 21.0, 101.3), (10.2, 26.5, 70.3), (8.0, 32.0, 55.2), (7.6, 32.0, 52.4)])
        self.assertEqual((by["EA.8.2-34"]["o2_pct"], by["EA.8.2-34"]["pressure_kpa"]), (34.0, 56.5))
        self.assertIn("source read at abstract level", by["EA.8.2-34"]["label"])
        # the challenge-statement label is the item's own sentence (its hedge kept) with the access note of
        # its reference, both read from references.json
        refs = em.ref_index(em.read_json(em.REFERENCES))
        ch_ref, ch_item = refs["CH.moonbase"]
        self.assertIn(ch_item["text"].rstrip(". "), by["CH.moonbase"]["label"])
        self.assertIn(em.ACCESS_NOTE[ch_ref["access"]], by["CH.moonbase"]["label"])
        self.assertEqual(by["CH.moonbase"]["label"].count("hallenge statement"), 1)
        self.assertNotIn("6001B", by["TB14639.worstcase"]["label"])  # the item says 'Test 1', no revision letter
        self.assertEqual((by["CH.moonbase"]["o2_min"], by["CH.moonbase"]["pressure_max"]), (30.0, 70.3))
        self.assertEqual((by["TB14639.worstcase"]["o2_pct"], by["TB14639.worstcase"]["pressure_kpa"]), (30.0, 70.3))
        self.assertEqual((by["6001B.T1.ambient"]["o2_pct"], by["6001B.T1.ambient"]["pressure_kpa"]), (20.9, 101.4))
        self.assertEqual((by["preset.iss"]["o2_pct"], by["preset.iss"]["pressure_kpa"]), (21.0, 101.3))
        self.assertEqual((by["preset.lunar_habitat"]["o2_pct"], by["preset.lunar_habitat"]["pressure_kpa"]),
                         (30.0, 70.3))
        self.assertEqual(by["preset.spacesuit"]["draw"], "text")
        for t in self.p["targets"]:
            if t.get("pressure_conversion", "").startswith("team conversion"):
                self.assertAlmostEqual(t["pressure_kpa"], t["pressure_psia"] * em.KPA_PER_PSIA, delta=0.05)

    def test_counting_ranges_hold_exactly_the_scenario_tier_atmosphere_tests(self):
        st = em.read_csv(em.SCENARIO_TESTS)
        for t in self.p["targets"]:
            if t["kind"] != "team_counting_range":
                continue
            sid = t["id"].split(".", 1)[1]
            want = {r["test_id"] for r in st if r["scenario_id"] == sid and r["tier"] == "atmosphere"
                    and self.tests[r["test_id"]]["o2_basis"] == "ambient"}
            self.assertEqual(t["tests_inside"], len(want), sid)
            self.assertTrue(self.p["sums"]["counting_range_checks"][sid]["same_tests"], sid)
        lunar = next(t for t in self.p["targets"] if t["id"] == "range.lunar_habitat")
        want = [r["test_id"] for r in st if r["scenario_id"] == "lunar_habitat" and r["tier"] == "atmosphere"
                and self.tests[r["test_id"]]["o2_basis"] == "ambient"]
        self.assertEqual(lunar["tests_inside"], len(want))
        self.assertEqual(lunar["tests_inside_by_investigation"], dict(Counter(self.tests[t]["investigation_id"] for t in want)))
        flex = [float(self.tests[t]["pressure_kpa"]) for t in want if self.tests[t]["investigation_id"] == "PSI-69"]
        lo, hi = lunar["tests_inside_pressure_kpa_range_by_investigation"]["PSI-69"]
        self.assertEqual((lo, hi), (min(flex), max(flex)))
        self.assertGreater(lo, 70.3)  # the FLEX tests in the lunar bins sit above the 70.3 kPa preset
        # so the label of that range says its pressure range is wider than the challenge-statement pressure
        # (coord/decisions.md 14:15); a range that does not rest on the challenge statement has no such clause
        ch = next(t for t in self.p["targets"] if t["id"] == "CH.moonbase")
        self.assertGreater(lunar["pressure_max"], ch["pressure_max"])
        self.assertIn(f"is wider than the {em.fmt(ch['pressure_max'])} kPa ({em.fmt(ch['pressure_psia_max'])} psi) "
                      "of the challenge statement", lunar["label"])
        iss = next(t for t in self.p["targets"] if t["id"] == "range.iss")
        self.assertNotIn("challenge statement", iss["label"])


class SaffireTest(Built):
    FAKE_ITEM = {"id": "SAF456.conditions", "type": "published_result",
                 "text": "Saffire IV to VI test conditions (fake item for a unit test).",
                 "values": {"rows": [{"pressure_kpa": 1.0, "o2_pct": 2.0}, {"pressure_kpa": 3.0, "o2_pct": 4.0}]}}

    def test_item_present_gives_cited_marks_that_are_never_counted(self):
        ref, it = em.find_saffire_item(em.read_json(em.REFERENCES))
        self.assertEqual(it["id"], "SAF456.conditions")
        rows = it["values"]["rows"]
        marks = self.p["flight_tests_not_in_psi"]
        self.assertEqual([(m["pressure_kpa"], m["o2_pct"]) for m in marks],
                         [(float(r["pressure_kpa"]), float(r["o2_pct"])) for r in rows])
        self.assertEqual([m["flight_sample"] for m in marks], [r["flight_sample"] for r in rows])
        for m in marks:
            self.assertIs(m["counted"], False)
            self.assertEqual(m["source"], "pipeline/spec/references.json#SAF456.conditions")
            self.assertTrue(resolve.check(m["source"]))
            self.assertEqual(m["label"], em.FLIGHT_LABEL)
            self.assertIn("not in PSI, not counted", m["label"])
        # never counted: the plotted points and every sum are PSI tests only
        self.assertEqual(self.p["sums"]["flight_tests_not_in_psi_counted"], 0)
        self.assertEqual(sum(p["n_tests"] for p in self.p["points"]), self.p["sums"]["plotted"])
        note = self.p["labels"]["saffire_note"]["text"]
        self.assertIn("five Saffire IV to VI samples considered in that paper", note)
        self.assertNotRegex(note, r"\bmeasured\b|\bset points?\b")
        self.assertIn(f"{min(r['o2_pct'] for r in rows):.1f} to {max(r['o2_pct'] for r in rows):.1f} mol % oxygen", note)
        self.assertIn(note, self.p["labels"]["caption"])
        # the note names the paper by its title in references.json and is a full sentence
        self.assertIn(f"'{ref['title'].split(' (')[0]}' (ICES-2024-365)", note)
        self.assertTrue(note.endswith("."))

    def _build_with(self, item):
        real = em.read_json

        def fake(path):
            doc = real(path)
            if Path(path) == em.REFERENCES:
                doc = copy.deepcopy(doc)
                for r in doc["references"]:
                    r["items"] = [x for x in r.get("items", []) if x["id"] != "SAF456.conditions"]
                    if em._SAFFIRE_LATE.search(" ".join(str(r.get(k, "")) for k in ("id", "title", "version"))):
                        r["items"] = []
                if item is not None:
                    doc["references"].append({"id": "FAKE-REF", "kind": "paper", "title": "fake", "issuer": "x",
                                              "version": "x", "url": "", "access": "full_text_read", "items": [item]})
            return doc

        with mock.patch.object(em, "read_json", fake):
            return em.build()

    def test_note_and_markers_only_from_machine_readable_values(self):
        p = self._build_with(self.FAKE_ITEM)
        self.assertIsNotNone(p["labels"]["saffire_note"])
        self.assertEqual([(m["pressure_kpa"], m["o2_pct"]) for m in p["flight_tests_not_in_psi"]],
                         [(1.0, 2.0), (3.0, 4.0)])
        self.assertTrue(all(m["label"] == em.FLIGHT_LABEL for m in p["flight_tests_not_in_psi"]))
        self.assertEqual(len(p["labels"]["caption"]), len(p["labels"]["caption_sources"]))
        p2 = self._build_with(dict(self.FAKE_ITEM, values={}))
        self.assertIsNone(p2["labels"]["saffire_note"])
        self.assertIsNone(p2["flight_tests_not_in_psi"])
        self.assertIn("not machine-readable", p2["labels"]["saffire_status"])

    def test_absent_item_means_null(self):
        p = self._build_with(None)
        self.assertIsNone(p["labels"]["saffire_note"])
        self.assertIsNone(p["flight_tests_not_in_psi"])
        self.assertFalse(any("Saffire" in c for c in p["labels"]["caption"]))


class WordingTest(Built):
    BLOCK = re.compile(r"\b(unsafe|safe to|is safe|predict\w*|will burn|would burn|bound(s|ed)?|guarantee\w*|"
                       r"we recommend|should be)\b", re.I)

    def _texts(self):
        lab = self.p["labels"]
        out = [lab["title"], lab["hollow_marker_meaning"], *lab["caption"]]
        for v in lab["lane_notes"].values():
            out += [x for k, x in v.items() if isinstance(x, str)]
        out += [t["label"] for t in self.p["targets"]]
        return out

    def test_fixed_labels(self):
        lab = self.p["labels"]
        self.assertEqual(lab["title"], "Where the PSI test tables stop")
        self.assertIn("Oxygen percent alone does not define an atmosphere; pressure and balance gas are shown "
                      "where the table records them.", lab["caption"])
        self.assertIn("not operational safety guidance", lab["caption"][0])
        # the first caption line gives the plotted tests and their investigations, counted here from tests.csv
        plotted = [t for t in self.tests.values() if t["o2_basis"] == "ambient" and t["o2_pct"]]
        n_inv = len(em.read_json(em.MANIFEST)["investigations"])
        self.assertIn(f"the {n_inv} NASA PSI investigations used here: the {len(plotted)} tests with a recorded "
                      f"ambient oxygen value, from {len({t['investigation_id'] for t in plotted})} of the "
                      "investigations, all run in microgravity", lab["caption"][0])
        self.assertTrue(all(t["gravity_level"] == "microgravity" for t in plotted))
        self.assertIn("converted to kPa by the team pipeline", self.p["axes"]["pressure_kpa"]["label"])
        self.assertEqual(len(lab["caption"]), len(lab["caption_sources"]))
        for srcs in lab["caption_sources"]:
            for s in srcs:
                self.assertTrue((ROOT / s).exists() or resolve.check(s), s)

    def test_no_verdict_or_prediction_wording_and_english(self):
        for s in self._texts():
            self.assertIsNone(self.BLOCK.search(s), s)
            self.assertTrue(s.isascii(), s)


class DisclosureAndDeterminismTest(unittest.TestCase):
    def test_written_file_carries_the_block(self):
        doc = json.loads(em.OUT.read_text(encoding="utf-8"))
        comp = json.loads((config.INSIGHTS_DIR / "_meta.json").read_text(encoding="utf-8"))
        self.assertEqual(list(doc)[0], "_meta")
        self.assertEqual(doc["_meta"], comp["evidence_map.json"])
        self.assertEqual(doc["_meta"]["built_by"], "ai/evidence_map.py")
        self.assertEqual(doc["_meta"]["language_model_used_at_build"], "none")
        body = {k: v for k, v in doc.items() if k != "_meta"}
        self.assertEqual(metamod.sha256_json(body), doc["_meta"]["content_sha256"])
        self.assertEqual(metamod.sha256_json(body), metamod.sha256_json(json.loads(json.dumps(em.build()))))

    def test_two_writes_are_byte_identical(self):
        d = Path(tempfile.mkdtemp())
        try:
            out = d / "evidence_map.json"
            em.write(out)
            a = out.read_bytes()
            em.write(out)
            self.assertEqual(a, out.read_bytes())
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
