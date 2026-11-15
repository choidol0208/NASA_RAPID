# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for the lookup tools (ai/assistant/tools.py) against the real data files. No network, no model.

Every asserted number is recounted here from the CSV or JSON file itself, not copied from a tool.

    python3 -m unittest ai.assistant.test_tools -v
"""
import csv
import json
import re
import unittest
from collections import Counter

from ai import checks, config, llm
from ai.assistant import contract, request as rq, tools
from scoring import scorer

ROOT = config.ROOT
D = tools.Data()
V = D.vocab


def rows(rel):
    with open(ROOT / rel, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def env(pid, o2=None, p=None):
    pr = V["presets"][pid]
    o2 = pr["o2_pct"] if o2 is None else o2
    p = pr["pressure_kpa"] if p is None else p
    cell = None if pr["scenario"] else rq.find_cell(o2, p, V)
    return {"preset": pid, "label": pr["label"], "o2_pct": o2, "pressure_kpa": p, "gravity": pr["gravity"],
            "flow": pr["flow"], "scenario_id": pr["scenario"], "cell": cell}


CELL = {"preset": None, "label": "Oxygen 26.5%, pressure 70 kPa", "o2_pct": 26.5, "pressure_kpa": 70.0, "gravity": None,
        "flow": None, "scenario_id": None, "cell": rq.find_cell(26.5, 70.0, V)}
ENVS = [env("iss"), env("lunar_habitat"), env("mars_habitat"), env("spacesuit"), env("exploration_8_2_34"), CELL]
TEMPLATE_KINDS = ("ranking", "count", "range", "readiness", "file_group")


def all_calls():
    calls = []
    for e in ENVS:
        calls += [("counts_per_question", {"env": e, "questions": []}), ("tested_range", {"env": e, "phase": None}),
                  ("where_the_data_are", {"env": e, "questions": []}), ("tests_table", {"env": e, "question": "S1"})]
    calls += [("rank_investigations", {"q": "lunar habitat cotton"}), ("rank_investigations", {"q": "ISS smoke"}),
              ("modelling_data", {"questions": ["S1", "P1"]}), ("equipment_research", {"kind": "detection"}),
              ("equipment_research", {"kind": "suppression"}), ("earth_applications", {}),
              ("search_records", {"keywords": ["smoke", "detector"]}), ("criteria", {"questions": ["P1", "D1"]}),
              ("files_of_test", {"test_id": "FLEX-21"}), ("investigation_card", {"accession": "PSI-25"}),
              ("explain", {"term": "counted test"}), ("explain", {"term": "inverse flame"})]
    return calls


class EveryToolTest(unittest.TestCase):
    def test_schema_templates_limits_and_repeatability(self):
        for name, args in all_calls():
            a = tools.run([{"tool": name, "args": args, "why": "test"}], D)
            b = tools.run([{"tool": name, "args": args, "why": "test"}], D)
            self.assertEqual(json.dumps(a["facts"], sort_keys=True), json.dumps(b["facts"], sort_keys=True),
                             f"{name}: facts differ between two runs")
            self.assertTrue(a["facts"], f"{name} {args}: no facts")
            for f in a["facts"]:
                self.assertEqual(llm.validate(f, contract.FACT), [], f"{name}: {f['text'][:80]}")
                for n in checks.extract_numbers((f.get("context") or "") + " " + f["text"]):
                    self.assertTrue(any(abs(x["value"] - float(n["value"])) < 1e-9 for x in f["numbers"]))
                if f["kind"] in TEMPLATE_KINDS or f["ref"].startswith("texts#"):
                    r = checks.check_template(f["text"], facts=f["numbers"], sources=f["source_keys"])
                    self.assertTrue(r["ok"], f"{name}: {r['reasons']} in {f['text'][:120]}")
            for p in a["panels"]:
                self.assertEqual(llm.validate(p, contract.PANEL), [], name)
            if name not in ("investigation_card", "explain", "modelling_data"):
                self.assertTrue(any(f["limit"] for f in a["facts"]), f"{name}: no limit fact")

    def test_missing_argument(self):
        out = tools.run_tool("counts_per_question", {}, D)
        self.assertEqual(out["facts"], [])
        self.assertEqual(out["notes"], ["missing argument env"])

    def test_numbering(self):
        out = tools.run([{"tool": "rank_investigations", "args": {"q": "ISS"}, "why": ""},
                         {"tool": "tested_range", "args": {"env": env("iss"), "phase": "solid"}, "why": ""}], D)
        self.assertEqual([f["id"] for f in out["facts"]], [f"F{i}" for i in range(1, len(out["facts"]) + 1)])
        self.assertEqual([p["id"] for p in out["panels"]], ["p1", "p2"])
        self.assertEqual(set(out["panels"][1]["fact_ids"]) & set(out["panels"][0]["fact_ids"]), set())

    def test_writer_facts_cap(self):
        out = tools.run([{"tool": "counts_per_question", "args": {"env": env("iss"), "questions": []}, "why": ""}], D)
        wf = tools.writer_facts(out["facts"])
        self.assertLessEqual(len(wf), tools.MAX_WRITER_FACTS)
        self.assertTrue(all(f in wf for f in out["facts"] if f["lead"]))


class RecountTest(unittest.TestCase):
    """A few facts per tool, recounted from the files."""

    def test_tested_range_solid(self):
        t = [r for r in rows("data/pipeline/tests.csv") if r["fuel_phase"] == "solid"]
        o2 = [float(r["o2_pct"]) for r in t if r["o2_basis"] == "ambient" and r["o2_pct"]]
        pk = [r for r in t if r["pressure_kpa"]]
        out = tools.run_tool("tested_range", {"env": env("lunar_habitat"), "phase": "solid"}, D)
        want = (f"Solid-fuel tests in the team's tables: oxygen of the surrounding atmosphere recorded for {len(o2)} of "
                f"{len(t)}, from {min(o2):g} to {max(o2):g}%; your 30% is above the highest recorded value.")
        self.assertEqual(out["facts"][0]["text"], want)
        self.assertIn(f"pressure recorded for {len(pk)} of {len(t)}", out["facts"][1]["text"])
        self.assertTrue(any(f["text"].startswith("No table has a partial-gravity test") for f in out["facts"]))

    def test_tested_range_gas_stream(self):
        t = [r for r in rows("data/pipeline/tests.csv") if r["fuel_phase"] == "gas"]
        m = sum(1 for r in t if r["o2_basis"] == "oxidizer_stream")
        out = tools.run_tool("tested_range", {"env": env("iss"), "phase": "gas"}, D)
        stream = [f for f in out["facts"] if "oxidizer stream" in f["text"]]
        self.assertTrue(stream[0]["text"].startswith(f"{m} gas-flame tests record"))
        self.assertTrue(stream[0]["source_keys"])

    def test_counts_verbatim_and_panel(self):
        pkg = json.loads((ROOT / "data/pipeline/evidence/scenario_lunar_habitat.json").read_text())
        s1 = next(b for b in pkg["needs"] if b["need_id"] == "S1")
        status = next(s["text"] for s in s1["statements"] if s["id"].startswith("status."))
        out = tools.run_tool("counts_per_question", {"env": env("lunar_habitat"), "questions": ["S1"]}, D)
        self.assertEqual(out["facts"][0]["text"], status)
        self.assertTrue(out["facts"][0]["lead"])
        row = next(r for r in rows("data/pipeline/scenario_needs.csv")
                   if r["scenario_id"] == "lunar_habitat" and r["need_id"] == "S1")
        prow = out["panels"][0]["rows"][0]
        self.assertEqual((prow["counted"], prow["both_inside"]), (int(row["usable_tests"]), int(row["tests_atmosphere"])))

    def test_counts_cell(self):
        out = tools.run_tool("counts_per_question", {"env": CELL, "questions": ["S1"]}, D)
        self.assertTrue(out["facts"][0]["limit"])
        self.assertTrue(out["facts"][0]["text"].startswith("These counts are for a cell"))
        row = next(r for r in rows("data/pipeline/atmosphere_cells.csv")
                   if r["scenario_id"] == CELL["cell"]["id"] and r["need_id"] == "S1")
        self.assertEqual(out["panels"][0]["rows"][0]["counted"], int(row["usable_tests"]))

    def test_tests_table_recount(self):
        need = {r["test_id"] for r in rows("data/pipeline/need_tests.csv") if r["need_id"] == "S1"}
        st = [r for r in rows("data/pipeline/scenario_tests.csv") if r["scenario_id"] == "iss"
              and r["tier"] in ("atmosphere", "oxygen_only", "pressure_only") and r["test_id"] in need]
        tiers = Counter(r["tier"] for r in st)
        out = tools.run_tool("tests_table", {"env": env("iss"), "question": "S1"}, D)
        self.assertTrue(out["facts"][0]["text"].startswith(f"{len(st)} recorded tests lie in this environment's ranges"))
        self.assertIn(f"{tiers.get('atmosphere', 0)} with oxygen and pressure both inside", out["facts"][0]["text"])
        self.assertEqual(out["panels"][0]["download"]["total_rows"], len(st))
        self.assertEqual(out["state"]["last_tests"], [r["test_id"] for r in st][:10])

    def test_where_piles_and_gap_states(self):
        out = tools.run_tool("where_the_data_are", {"env": env("lunar_habitat"), "questions": ["S1"]}, D)
        doc = D.piles["lunar_habitat"][0]
        self.assertEqual(out["facts"][0]["text"], doc["header"][0])
        out = tools.run_tool("where_the_data_are", {"env": env("spacesuit"), "questions": ["S1"]}, D)
        g = [r for r in rows("data/pipeline/need_gap_states.csv") if r["scenario_id"] == "spacesuit"
             and r["need_id"] == "S1" and r["role"] in ("required", "outcome") and r["state"] != "in_table"
             and int(r["counted_tests_in_state"] or 0) > 0][0]
        self.assertIn(f"{g['counted_tests_in_state']} of {g['counted_tests']} counted tests", out["facts"][0]["text"])

    def test_files_of_test(self):
        r = [x for x in rows("data/pipeline/test_files.csv") if x["test_id"] == "FLEX-21" and x["link_level"] == "test"]
        out = tools.run_tool("files_of_test", {"test_id": "flex-21"}, D)
        self.assertTrue(out["facts"][0]["text"].startswith(f"{sum(int(x['files']) for x in r)} files ("))

    def test_equipment_counts(self):
        n = sum(1 for r in rows("data/pipeline/need_tests.csv") if r["need_id"] == "D1" and r["objective_link"] == "stated")
        out = tools.run_tool("equipment_research", {"kind": "detection"}, D)
        self.assertIn(f"Combustion products (D1): {n} tests are counted", " ".join(f["text"] for f in out["facts"]))
        inv = [r["psi_accession"] for r in rows("data/catalog/investigations.csv") if "detection" in r["fire_safety_role"]]
        for a in inv:
            self.assertIn(f"({a})", out["facts"][0]["text"])

    def test_earth_applications_rule(self):
        ev = json.loads((ROOT / "data/insights/evidence.json").read_text())["records"]
        rx = re.compile(r"\b(earth|terrestrial|industr\w*|engines?|power plants?|combustors?|emissions?|pollut\w*|"
                        r"buildings?|household|aircraft|wildfires?|furnaces?|turbines?|submarines?|automotive)\b", re.I)
        n = sum(1 for rec in ev.values() for u in rec["units"] if u["field"] == "researchImpacts" and u["quotable"]
                and rx.search(u["text"]) and not re.search(r"\bfar from earth\b|\bas they do on earth\b", u["text"], re.I))
        out = tools.run_tool("earth_applications", {}, D)
        self.assertEqual(len(out["panels"][0]["rows"]), n)
        self.assertTrue(all(f["quote"] for f in out["facts"] if not f["limit"]))

    def test_search_limit_counts(self):
        ev = json.loads((ROOT / "data/insights/evidence.json").read_text())["records"]
        n = sum(1 for rec in ev.values() for u in rec["units"] if u["quotable"])
        out = tools.run_tool("search_records", {"keywords": ["smoke"]}, D)
        self.assertIn(f"over the {n} numbered sentences of the {len(ev)} PSI records", out["facts"][-1]["text"])
        self.assertTrue(all("smoke" in f["text"].lower() for f in out["facts"][:-1]))
        self.assertEqual(tools.run_tool("search_records", {"keywords": ["zzqxv"]}, D)["facts"], [])

    def test_criteria_quote(self):
        f = [r for r in rows("data/pipeline/findings.csv") if r["kind"] == "criterion" and "P1" in r["needs"].split(";")
             and r["quote"]][0]
        out = tools.run_tool("criteria", {"questions": ["P1"]}, D)
        self.assertEqual(out["facts"][0]["text"], f'{f["reference_id"]}, {f["where"]}: "{f["quote"]}"')

    def test_modelling(self):
        mr = json.loads((ROOT / "data/insights/model_readiness.json").read_text())
        out = tools.run_tool("modelling_data", {"questions": ["S1"]}, D)
        self.assertEqual(out["facts"][0]["text"], mr["fixed_line"])
        n = sum(1 for r in rows("data/pipeline/need_tests.csv") if r["need_id"] == "S1" and r["objective_link"] == "stated")
        self.assertTrue(any(f["text"].startswith(f"Extinction conditions (S1): {n} counted tests") for f in out["facts"]))
        self.assertEqual(out["panels"][1]["download"]["total_rows"], n)

    def test_card(self):
        r = next(x for x in rows("data/catalog/investigations.csv") if x["psi_accession"] == "PSI-25")
        out = tools.run_tool("investigation_card", {"accession": "PSI-25"}, D)
        self.assertIn(f"{r['test_count']} tests listed in the catalog", out["facts"][0]["text"])

    def test_rank_order(self):
        res = scorer.rank("lunar habitat cotton")["results"]
        out = tools.run_tool("rank_investigations", {"q": "lunar habitat cotton"}, D)
        for a in [x["psi_accession"] for x in res]:
            self.assertIn(f"({a})", out["facts"][0]["text"])
        self.assertNotRegex(out["facts"][0]["text"], r"\d+\.\d")  # no score in the text
        self.assertEqual(out["state"]["last_list"], [x["psi_accession"] for x in res])

    def test_explain(self):
        meta = json.loads((ROOT / "pipeline/spec/needs.json").read_text())["_meta"]
        out = tools.run_tool("explain", {"term": "counted test"}, D)
        self.assertTrue(meta["reading_rule"].startswith(out["facts"][0]["text"][:40]))
        self.assertEqual(tools.run_tool("explain", {"term": "flux capacitor"}, D)["facts"], [])


if __name__ == "__main__":
    unittest.main()
