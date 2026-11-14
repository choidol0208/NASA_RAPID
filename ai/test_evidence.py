# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Tests for the evidence packets (ai/evidence.py) and the source resolver (ai/resolve.py).

    python3 -m unittest ai.test_evidence -v
"""
import json
import re
import unittest

from ai import config, evidence, meta, resolve

DESIGN_FORMS = [
    "PSI-25.objective", "PSI-25", "doi:10.60555/4qc4-de67",
    "data/pipeline/tests.csv#FLEX-41", "data/pipeline/scenario_needs.csv#lunar_habitat/S1",
    "data/pipeline/objective_links.csv#S1/PSI-69", "pipeline/spec/references.json#TB008.gaps",
    "pipeline/spec/scenarios.json#lunar_habitat", "pipeline/spec/sources.json#acme_bre",
    "pipeline/spec/needs.json#not_covered", "data/catalog/configurations.csv#FLEX-C01",
    "scoring/scoring_config.json#atmosphere_fallback",
]


class SplitterTest(unittest.TestCase):
    def texts(self, s):
        return [s[x["start"]:x["end"]] for x in evidence.split_field(s)]

    def test_abbreviations_initials_decimals(self):
        self.assertEqual(self.texts("Flames, e.g. Methane flames, burn. Dr. Smith agreed."),
                         ["Flames, e.g. Methane flames, burn.", "Dr. Smith agreed."])
        self.assertEqual(self.texts("Work by S. L. Olson et al. Results follow. Next one."),
                         ["Work by S. L. Olson et al. Results follow.", "Next one."])
        self.assertEqual(self.texts("Tested at 0.5 atm. Then 1.5 atm."), ["Tested at 0.5 atm.", "Then 1.5 atm."])
        self.assertEqual(self.texts("Made in the U.S. Navy labs. Done."), ["Made in the U.S. Navy labs.", "Done."])

    def test_lines_markers_and_soft_wraps(self):
        s = "Objectives:\n  1) Study flames in low flow.\n  2) Begin to bridge the gap.\nPressure, O2\nconcentration, etc."
        spans = evidence.split_field(s)
        self.assertEqual([s[x["start"]:x["end"]] for x in spans],
                         ["Objectives:", "Study flames in low flow.", "Begin to bridge the gap.",
                          "Pressure, O2\nconcentration, etc."])
        self.assertEqual([x["list_marker"] for x in spans], [None, "1)", "2)", None])


class EvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = evidence.build()
        cls.recs = cls.payload["records"]
        cls.psi = evidence.load_records()

    def test_24_records(self):
        self.assertEqual(len(self.recs), 24)
        self.assertEqual(set(self.recs), {x["accession"] for x in json.loads(config.PSI_MANIFEST.read_text())["investigations"]})

    def test_offset_round_trip_every_unit(self):
        n = 0
        for inv, r in self.recs.items():
            for u in r["units"]:
                self.assertEqual(self.psi[inv][u["field"]][u["char_start"]:u["char_end"]], u["text"], (inv, u["id"]))
                self.assertEqual(u["source"], f"{inv}.{u['field']}")
                n += 1
        self.assertGreater(n, 400)

    def test_ids_unique_and_sequential(self):
        for inv, r in self.recs.items():
            ids = [u["id"] for u in r["units"]]
            self.assertEqual(len(ids), len(set(ids)), inv)
            for f, (pre, _) in evidence.FIELDS.items():
                ks = [int(u["id"].split("-")[1]) for u in r["units"] if u["field"] == f]
                self.assertEqual(ks, list(range(1, len(ks) + 1)), (inv, f))
                self.assertTrue(all(u["id"].startswith(pre + "-") for u in r["units"] if u["field"] == f))

    def test_known_duplicate_groups(self):
        def shared(inv, field, other):
            us = evidence.units(inv, field, ev=self.payload)
            return bool(us) and all(other in u["shared_with"] for u in us)
        self.assertTrue(shared("PSI-98", "objective", "PSI-100"))
        self.assertTrue(shared("PSI-100", "objective", "PSI-98"))
        self.assertTrue(shared("PSI-98", "researchImpacts", "PSI-100"))
        for a in ("PSI-98", "PSI-99", "PSI-100"):
            for b in ("PSI-98", "PSI-99", "PSI-100"):
                if a != b:
                    self.assertTrue(shared(a, "hypothesis", b), (a, b))

    def test_quotable_units_are_sentences(self):
        for inv, r in self.recs.items():
            for u in r["units"]:
                if not u["quotable"]:
                    continue
                t = u["text"].strip()
                self.assertGreaterEqual(u["words"], 6, (inv, u["id"]))
                self.assertFalse(t.endswith(":"), (inv, u["id"]))
                self.assertIsNone(re.fullmatch(r"\(?(\d+|[A-Za-z])[.)]?\)?", t), (inv, u["id"]))
                self.assertNotEqual(u["field"], "title")
                self.assertNotRegex(t, r"https?://")

    def test_known_non_quotable_openers(self):
        hyp101 = evidence.units("PSI-101", "hypothesis", ev=self.payload)[0]
        self.assertTrue(hyp101["text"].endswith(":") and not hyp101["quotable"])
        hyp102 = evidence.units("PSI-102", "hypothesis", ev=self.payload)[0]
        self.assertTrue(hyp102["text"].endswith(":") and not hyp102["quotable"])
        # PSI-10 hypothesis and PSI-106 impacts start with '1.': the marker is kept out of the unit text
        for inv, f in (("PSI-10", "hypothesis"), ("PSI-106", "researchImpacts")):
            first = evidence.units(inv, f, ev=self.payload)[0]
            self.assertEqual(first["list_marker"], "1.")
            self.assertTrue(first["quotable"])

    def test_prefix_and_hedge(self):
        for r in self.recs.values():
            for u in r["units"]:
                self.assertEqual(u["prefix"], evidence.FIELDS[u["field"]][1])
        u = [x for x in evidence.units("PSI-25", "hypothesis", ev=self.payload) if "may not" in x["text"]][0]
        self.assertTrue(u["hedged"])
        self.assertIn("may", u["hedge_words"])

    def test_license(self):
        self.assertEqual(self.recs["PSI-10"]["license"], "not stated in the record")
        self.assertEqual(sum(r["license"] == "CC0-1.0" for r in self.recs.values()), 23)

    def test_determinism_and_file_up_to_date(self):
        self.assertEqual(meta.sha256_json(evidence.build()), meta.sha256_json(self.payload))
        on_disk = json.loads(evidence.EVIDENCE_PATH.read_text())
        self.assertEqual(on_disk["_meta"]["content_sha256"], meta.sha256_json(self.payload))
        comp = json.loads((config.INSIGHTS_DIR / "_meta.json").read_text())
        self.assertEqual(comp["evidence.json"], on_disk["_meta"])
        self.assertEqual(on_disk["_meta"]["language_model_used_at_build"], "none")


class ResolveTest(unittest.TestCase):
    def test_three_agreed_forms_give_real_text(self):
        psi25 = json.loads((config.PSI_CATALOG_DIR / "PSI-25.json").read_text())
        r = resolve.resolve("PSI-25.objective")
        self.assertEqual(r["text"], psi25["objective"])
        r = resolve.resolve("doi:" + psi25["doi"])
        self.assertEqual(r["text"], psi25["title"])
        pub = psi25["publications"][0]
        r = resolve.resolve("doi:" + pub["doi"])
        self.assertEqual(r["text"], pub["title"])
        r = resolve.resolve("data/pipeline/tests.csv#FLEX-41")
        self.assertEqual(r["data"]["rows"][0]["test_id"], "FLEX-41")
        self.assertEqual(r["data"]["rows"][0]["investigation_id"], "PSI-69")

    def test_every_design_form_resolves(self):
        for s in DESIGN_FORMS:
            with self.subTest(source=s):
                r = resolve.resolve(s)
                self.assertTrue(r["text"].strip())

    def test_every_unit_source_resolves_to_its_field(self):
        ev = evidence.build()
        for inv, rec in ev["records"].items():
            for u in rec["units"]:
                text = resolve.resolve(u["source"])["text"]
                self.assertEqual(text[u["char_start"]:u["char_end"]], u["text"])

    def test_failures_raise(self):
        for s in ("PSI-9999.objective", "PSI-25.nofield", "doi:10.0000/not-a-real-doi",
                  "data/pipeline/tests.csv#NOPE-1", "pipeline/spec/references.json#NOPE"):
            with self.subTest(source=s):
                with self.assertRaises(resolve.SourceNotFound):
                    resolve.resolve(s)
        for s in ("../etc/passwd#x", "/etc/hosts#x", "free text", " PSI-25", "doi:",
                  "data/psi/experimental_tables/PSI-25_Experimental table_BASS-II.csv#1",
                  "README.md#x"):
            with self.subTest(source=s):
                with self.assertRaises((resolve.BadSource, resolve.SourceNotFound)):
                    resolve.resolve(s)
        self.assertFalse(resolve.check("PSI-9999"))
        self.assertTrue(resolve.check("PSI-25"))


if __name__ == "__main__":
    unittest.main()
