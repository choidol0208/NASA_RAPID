# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Unit tests for video/index_by_name.py on small made-up listings. No network, no video.

Run: python3 video/test_index_by_name.py
"""
import collections
import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import index_by_name as ib  # noqa: E402

RULES = ib.load_rules(ib.DEFAULT_RULES)


def row(investigation, file_name, folder, identifiers="", tie_level="none", test_id="", source="", clip_words="",
        category="Raw Data", candidates="0", size=1000):
    """One made-up row in the format of the saved listing."""
    return {"investigation": investigation, "category": category, "folder": folder, "file_name": file_name,
            "bytes": str(size), "extension": file_name.rsplit(".", 1)[-1], "pattern": "", "identifiers": identifiers,
            "clip_words": clip_words, "identifier_source": source, "tie_level": tie_level, "test_id": test_id,
            "candidate_test_ids_n": candidates, "candidate_test_ids": "", "name_folder_conflict": "", "notes": "",
            "psi_file_id": "x"}


TESTS = {t: {"test_id": t, "investigation_id": inv} for t, inv in [
    ("BASS2-O9", "PSI-25"), ("BASS2-P13a", "PSI-25"), ("BASS2-P13b", "PSI-25"), ("BASS2-B17", "PSI-25"),
    ("FD-N-19142G3", "PSI-10"), ("FLEX-33", "PSI-69")]}

O9 = row("PSI-25", "PSI-25_Raw Data_BASS_GMT177_SAMPLE_209_TEST_O9.mp4", "Raw Data/Reduced Gravity/O9",
         "gmt_day=177; sample=209; test=O9; folder_test=O9; check_gmt_sample=agree", "single_test", "BASS2-O9", "name", size=600)
O9_2ND = row("PSI-25", "PSI-25_Raw Data_BASS_GMT177_SAMPLE_209_TEST_O9_2ND_VIEW.mp4", "Raw Data/Reduced Gravity/O9",
             "gmt_day=177; sample=209; test=O9; folder_test=O9; check_gmt_sample=agree", "single_test", "BASS2-O9", "name",
             clip_words="second_view", size=800)
P13A = row("PSI-25", "PSI-25_Raw Data_BASS_GMT195_SAMPLE_203_TEST_P13a.mp4", "Raw Data/Reduced Gravity/P13",
           "gmt_day=195; sample=203; test=P13a; folder_test=P13; check_gmt_sample=agree", "single_test", "BASS2-P13a", "name")
B15 = row("PSI-25", "PSI-25_Raw Data_BASS_GMT183_SAMPLE_175_TESTB15.mp4", "Raw Data/Reduced Gravity/B17",
          "gmt_day=183; sample=175; test=B15; folder_test=B17; check_gmt_sample=agree", "single_test", "BASS2-B17",
          "folder (name corrected by GMT+sample check)")
FD_NAME_ONLY = row("PSI-10", "PSI-10_Raw Data_19142G3-vlc-record-2019-05-22-17h06m32s-udp____7300-.ts",
                   "Raw Data/Reduced Gravity/1_normal_flames/19142",
                   "recording_start=2019-05-22 17:06:32; testpoint=19142G3; test_day_yyddd=19142", "single_test",
                   "FD-N-19142G3", "name", clip_words="stream_recording")
CLD_DAY = row("PSI-21", "PSI-21_Raw Data_vlc-record-2017-12-01-10h00m00s-udp____17335A1.ts", "Raw Data/17335",
              "recording_start=2017-12-01 10:00:00; testpoint=17335A1; test_day_yyddd=17335",
              "day", "", "name", clip_words="stream_recording")
FLEX_2013 = row("PSI-69", "PSI-69_Raw Data_vlc-record-2013-05-01-10h00m00s-udp_X123M01.ts", "Raw Data/2013",
                "recording_start=2013-05-01 10:00:00; testpoint_2013=X123M01", "none", "", "", clip_words="stream_recording")
OUTREACH = row("PSI-22", "PSI-22_Presentations_ACME overview.mp4", "Presentations", "", "none", "", "",
               category="Presentations")


def link_of(r):
    lab, words = ib.read_labels(r["investigation"], r["file_name"], r["folder"], RULES, r["category"])
    return ib.link_state(r, lab, RULES)


class LinkStates(unittest.TestCase):
    def test_two_labels_agree(self):
        scope, state, agree, against, _ = link_of(O9)
        self.assertEqual((scope, state, agree, against), ("test", "two_labels_agree", ["name_id", "folder_id"], []))

    def test_one_label_run_letter(self):
        scope, state, agree, against, scope2 = link_of(P13A)
        self.assertEqual((state, agree, against), ("one_label", ["name_id"], []))
        self.assertIn("without the run letter", scope2)

    def test_one_label_name_only(self):
        self.assertEqual(link_of(FD_NAME_ONLY)[1:4], ("one_label", ["name_id"], []))

    def test_labels_disagree(self):
        scope, state, agree, against, _ = link_of(B15)
        self.assertEqual((state, agree, against), ("labels_disagree", ["folder_id"], ["name_id"]))

    def test_day_or_sample_mismatch_disagrees(self):
        r = dict(O9, identifiers=O9["identifiers"].replace("agree", "gmt_differs"))
        self.assertEqual(link_of(r)[1], "labels_disagree")

    def test_day_only(self):
        self.assertEqual(link_of(CLD_DAY)[:2], ("day", "day_only"))
        self.assertEqual(ib.day_of(CLD_DAY, RULES), "test_day_yyddd=17335")

    def test_identifier_not_in_table(self):
        self.assertEqual(link_of(FLEX_2013)[:2], ("none", "id_not_in_table"))

    def test_no_identifier(self):
        self.assertEqual(link_of(OUTREACH)[:2], ("none", "none"))
        only_start = row("PSI-69", "PSI-69_Raw Data_vlc-record-2013-05-01-10h00m00s-udp_1.ts", "Raw Data",
                         "recording_start=2013-05-01 10:00:00", clip_words="stream_recording")
        self.assertEqual(link_of(only_start)[1], "none")


class Reading(unittest.TestCase):
    def test_bass2_rule_reads_bass2_name(self):
        lab, _ = ib.read_labels("PSI-25", O9["file_name"], O9["folder"], RULES)
        self.assertEqual((lab["name_id"], lab["folder_id"], lab["gmt_day"], lab["sample"]), ("O9", "O9", "177", "209"))

    def test_other_investigation_not_read_with_bass2_rule(self):
        name = "PSI-26_Raw Data_BASS_GMT177_SAMPLE_209_TEST_O9.mp4"
        lab, _ = ib.read_labels("PSI-26", name, "Raw Data/Reduced Gravity/O9", RULES)
        self.assertEqual((lab["name_id"], lab["folder_id"], lab["gmt_day"], lab["sample"]), ("", "", "", ""))
        lab, _ = ib.read_labels("PSI-999", name.replace("PSI-26", "PSI-999"), "Raw Data/O9", RULES)
        self.assertEqual(lab["name_id"], "")

    def test_outreach_clip_gets_no_label(self):
        lab, _ = ib.read_labels("PSI-10", "PSI-10_Presentations_19142G3 overview.mp4", "Presentations", RULES, "Presentations")
        self.assertEqual(lab["name_id"], "")

    def test_clip_kind(self):
        self.assertEqual(ib.clip_kind("PSI-25", O9_2ND["file_name"], ["second_view"], RULES), ("other", "second view"))
        self.assertEqual(ib.clip_kind("PSI-25", O9["file_name"], [], RULES), ("main", "whole recording"))
        self.assertEqual(ib.clip_kind("PSI-25", "PSI-25_Raw Data_BASS_GMT195_SAMPLE_202_TEST_P5-LOS-portion.mp4",
                                      ["loss_of_signal_portion"], RULES), ("main", "portion during loss of signal"))
        self.assertEqual(ib.clip_kind("PSI-69", "PSI-69_Raw Data_Droplet View.mp4", ["camera_view_named"], RULES),
                         ("other", "named camera view"))

    def test_difference_from_saved_reading_stops_the_build(self):
        bad = dict(O9, identifiers=O9["identifiers"].replace("test=O9", "test=O8"))
        with self.assertRaises(ib.BuildError):
            ib.index_rows([bad], TESTS, set(), RULES)

    def test_test_missing_from_tests_table_stops_the_build(self):
        with self.assertRaises(ib.BuildError):
            ib.index_rows([O9], {}, set(), RULES)

    def test_flex_2013_test_point_is_read_again(self):
        lab, _ = ib.read_labels("PSI-69", FLEX_2013["file_name"], FLEX_2013["folder"], RULES)
        self.assertEqual(lab["name_id_2013"], "X123M01")
        self.assertEqual(lab["name_id"], "")
        bad = dict(FLEX_2013, identifiers=FLEX_2013["identifiers"].replace("X123M01", "X123M02"))
        with self.assertRaises(ib.BuildError):
            ib.index_rows([bad], TESTS, set(), RULES)

    def test_day_keys_are_read_again(self):
        bass = row("PSI-26", "PSI-26_Raw Data_20130406 13.07.56 iss035m020951302.mp4", "Raw Data/2013_04_06",
                   "date_on_video=2013-04-06; time_in_name=13:07:56; iss_code=iss035m020951302; iss_code_day=095; "
                   "actual_date=2013-04-05", "day")
        lab, _ = ib.read_labels("PSI-26", bass["file_name"], bass["folder"], RULES)
        self.assertEqual(lab["days"], {"date_on_video": "2013-04-06", "actual_date": "2013-04-05"})
        self.assertEqual(ib.compare_with_saved(bass, lab, [], RULES), [])
        wrong = dict(bass, identifiers=bass["identifiers"].replace("actual_date=2013-04-05", "actual_date=2013-04-06"))
        with self.assertRaises(ib.BuildError):
            ib.index_rows([wrong], TESTS, set(), RULES)
        lab, _ = ib.read_labels("PSI-106", "DIMSG462M_1.mp4", "Raw Data/Reduced Gravity/UT_120_125", RULES)
        self.assertEqual(lab["days"], {"folder_day_range": "120-125"})
        lab, _ = ib.read_labels("PSI-107", "PSI-107_Raw Data_SPICE_GMT136_Ign8b.mp4", "Raw Data", RULES)
        self.assertEqual(lab["days"], {"gmt_day": "136"})
        lab, _ = ib.read_labels("PSI-21", CLD_DAY["file_name"], CLD_DAY["folder"], RULES)
        self.assertEqual(lab["days"], {"recording_start": "2017-12-01 10:00:00", "test_day_yyddd": "17335"})

    def test_labels_values_printed_for_disagreeing_labels(self):
        rows, _, _ = ib.index_rows([B15], TESTS, set(), RULES)
        self.assertEqual(rows[0]["labels_values"], "file name: B15, day 183, sample 175; folder: B17")


class Build(unittest.TestCase):
    def test_small_listing(self):
        listing = [O9, O9_2ND, P13A, B15, FD_NAME_ONLY, CLD_DAY, FLEX_2013, OUTREACH]
        need = {"P1": {t: {"objective_link": "stated"} for t in ("BASS2-O9", "BASS2-P13a", "BASS2-B17")}}
        scen = collections.defaultdict(dict)
        for sc in RULES["demo_scenarios"]:
            for t in TESTS:
                scen[sc][t] = {"o2_match": "in", "pressure_match": "not_recorded"} if sc == "iss" else {"o2_match": "out", "pressure_match": "in"}
        out = ib.build(listing_rows=listing, tables=(TESTS, need, scen), transcribed={O9["file_name"]})
        self.assertEqual(set(out), {"video_links.csv", "video_links_summary.json", "shortlist_iss_P1_main_view.csv"})
        s = json.loads(out["video_links_summary.json"])
        self.assertEqual({k: v["files"] for k, v in s["by_link_state"].items()},
                         {"two_labels_agree": 2, "one_label": 2, "labels_disagree": 1, "day_only": 1, "id_not_in_table": 1, "none": 1})
        self.assertEqual(s["counted_tests_with_video_by_question"]["P1"]["two_labels_agree"], 1)
        self.assertEqual(s["counted_tests_with_video_by_question"]["P1"]["labels_disagree_only"], 1)
        lines = out["shortlist_iss_P1_main_view.csv"].splitlines()
        self.assertTrue(lines[0].startswith("# Shortlist iss, P1"))
        self.assertIn("not reviewed by a person", lines[0])
        rows = list(csv.DictReader(io.StringIO("\n".join(lines[1:]))))
        self.assertEqual([r["file_name"] for r in rows], [B15["file_name"], O9["file_name"], P13A["file_name"]])
        self.assertEqual([r["transcribed"] for r in rows], ["no", "yes", "no"])
        links = list(csv.DictReader(io.StringIO("\n".join(out["video_links.csv"].splitlines()[1:]))))
        self.assertEqual([r["test_id"] for r in links if r["link_state"] == "day_only"], [""])
        self.assertEqual([r["day"] for r in links if r["link_state"] == "day_only"], ["test_day_yyddd=17335"])


def shipped_csv(fn, folder=ib.DEFAULT_OUT):
    with open(os.path.join(folder, fn), encoding="utf-8") as fh:
        return list(csv.DictReader(ln for ln in fh if not ln.startswith("#")))


def shipped_summary():
    with open(os.path.join(ib.DEFAULT_OUT, "video_links_summary.json"), encoding="utf-8") as fh:
        return json.load(fh)


class SecondCodePath(unittest.TestCase):
    """The shipped files against the design job's separate recount and the fixtures of
    docs/video_design/design.md section 12 (values copied from that section)."""

    def test_link_states_equal_the_prototype_recount(self):
        mine = {(r["investigation"], r["file_name"], r["folder"]): r for r in shipped_csv("video_links.csv")}
        proto = shipped_csv("video_links_states.csv", os.path.join(ib.REPO, "docs", "video_design", "prototype"))
        self.assertEqual(len(proto), 2623)
        self.assertEqual(len(mine), 2623)
        diffs = []
        for p in proto:
            m = mine[(p["investigation"], p["file_name"], p["folder"])]
            for k in ("tie_scope", "link_state", "test_id", "labels_agreeing", "labels_against"):
                pv = p[k].replace(";", " ") if k.startswith("labels") else p[k]
                mv = m[k] if k != "test_id" or p["tie_scope"] == "test" else p[k]
                if pv != mv:
                    diffs.append((p["file_name"], k, pv, m[k]))
        self.assertEqual(diffs, [])

    def test_fixtures_of_design_section_12(self):
        s = shipped_summary()
        self.assertEqual(s["totals"], {"files": 2623, "bytes": 426053691302})
        self.assertEqual({k: v["files"] for k, v in s["by_tie_scope"].items()},
                         {"test": 1046, "run": 3, "day": 1188, "several_days": 26, "none": 360})
        self.assertEqual(s["by_tie_scope"]["test"]["bytes"], 238966365726)
        self.assertEqual({k: (v["files"], v["bytes"]) for k, v in s["by_link_state"].items()}, {
            "two_labels_agree": (662, 152320655239), "one_label": (374, 81527352372), "labels_disagree": (10, 5118358115),
            "day_only": (1217, 102112670418), "id_not_in_table": (330, 83454932324), "none": (30, 1519722834)})
        inv = s["by_investigation"]
        pick = lambda i, *ks: tuple(inv[i][k] for k in ks)
        self.assertEqual(pick("PSI-25", "two_labels_agree", "one_label", "labels_disagree"), (244, 47, 5))
        self.assertEqual(pick("PSI-159", "two_labels_agree", "one_label", "labels_disagree", "day_only"), (314, 11, 2, 10))
        self.assertEqual(pick("PSI-39", "two_labels_agree", "one_label", "labels_disagree", "day_only", "id_not_in_table"),
                         (101, 5, 2, 20, 118))
        self.assertEqual(pick("PSI-69", "two_labels_agree", "one_label", "labels_disagree", "id_not_in_table", "none"),
                         (3, 5, 1, 163, 11))
        self.assertEqual(pick("PSI-10", "one_label", "day_only"), (306, 11))
        # the per-investigation table of design section 4: two labels, one label, disagree, day only, not in table, none
        table4 = {"PSI-10": (0, 306, 0, 11, 0, 0), "PSI-20": (0, 0, 0, 163, 33, 3), "PSI-21": (0, 0, 0, 358, 2, 3),
                  "PSI-22": (0, 0, 0, 215, 0, 6), "PSI-23": (0, 0, 0, 285, 1, 4), "PSI-25": (244, 47, 5, 0, 0, 0),
                  "PSI-26": (0, 0, 0, 113, 1, 0), "PSI-39": (101, 5, 2, 20, 118, 0), "PSI-69": (3, 5, 1, 0, 163, 11),
                  "PSI-101": (0, 0, 0, 8, 0, 0), "PSI-102": (0, 0, 0, 0, 0, 2), "PSI-106": (0, 0, 0, 27, 0, 1),
                  "PSI-107": (0, 0, 0, 7, 12, 0), "PSI-159": (314, 11, 2, 10, 0, 0)}
        self.assertEqual({i: pick(i, *ib.LINK_STATES) for i in inv}, table4)
        b = s["tests_with_video_by_best_link_state"]
        self.assertEqual((b["two_labels_agree"], b["one_label"], b["labels_disagree_only"]), (463, 344, 6))
        self.assertEqual(b["by_investigation"]["PSI-25"], {"two_labels_agree": 101, "one_label": 20, "labels_disagree": 2})
        q = s["counted_tests_with_video_by_question"]
        four = lambda e: (e["two_labels_agree"], e["one_label"], e["labels_disagree_only"], e["no_video_tied_to_the_test"])
        self.assertEqual({k: four(q[k]) for k in ("P1", "D1", "S1", "P3")},
                         {"P1": (99, 18, 2, 14), "D1": (98, 16, 2, 6), "S1": (19, 10, 1, 268), "P3": (0, 0, 0, 2)})
        iss = s["scenarios"]["iss"]
        p1 = iss["by_question_and_placement"]["P1"]["oxygen_inside_pressure_not_in_table"]
        self.assertEqual((p1["tests"],) + four(p1), (55, 42, 4, 0, 9))
        sl = iss["shortlists"]["P1"]
        self.assertEqual((sl["files"], sl["bytes"], sl["tests_with_a_listed_file"]), (49, 3515643202, 45))
        self.assertEqual(sl["by_clip_kind"], {"whole recording": {"files": 44, "bytes": 3406968026},
                                              "portion during loss of signal": {"files": 5, "bytes": 108675176}})
        self.assertEqual(sl["by_link_state"], {"two_labels_agree": 44, "one_label": 4, "labels_disagree": 1})
        self.assertEqual(sl["transcribed"]["files"], 7)
        self.assertEqual(sl["not_transcribed"], {"files": 42, "bytes": 2867152457})
        lunar = s["scenarios"]["lunar_habitat"]
        ins = lunar["tests_inside_the_ranges"]
        self.assertEqual((ins["tests"], ins["two_labels_agree"]), (26, 8))
        self.assertEqual(ins["videos"]["by_link_state"]["two_labels_agree"], {"files": 8, "bytes": 2640554564})
        self.assertEqual({f["test_id"].split("-")[0] for f in ins["two_labels_agree_files"]}, {"CFIG"})
        s1 = lunar["by_question_and_placement"]["S1"]["inside"]
        self.assertEqual((s1["tests"], s1["no_video_tied_to_the_test"]), (17, 17))
        k = s["bass2_by_clip_kind"]
        self.assertEqual(k["main: whole recording"], {"files": 114, "bytes": 7547979401, "tests": 114})
        other_main = [v for n, v in k.items() if n.startswith("main:") and n != "main: whole recording"]
        self.assertEqual((sum(v["files"] for v in other_main), sum(v["bytes"] for v in other_main)), (21, 600280475))
        self.assertEqual(k["main: portion during loss of signal"]["files"], 7)
        self.assertEqual(k["main: ignition attempt"]["files"], 5)
        self.assertEqual(k["main: part of a recording"]["files"], 2)
        self.assertEqual(k["other: second view"], {"files": 102, "bytes": 9044985674, "tests": 94})
        self.assertEqual(k["other: still sequence"], {"files": 52, "bytes": 450216042, "tests": 50})
        self.assertEqual(k["other: rack, monitor or other camera"]["files"], 4)
        self.assertEqual(k["other: post-burn picture"]["files"], 3)
        self.assertEqual(sum(v["files"] for v in k.values()), 296)

    def test_every_day_tie_and_unlisted_identifier_was_read_again(self):
        c = shipped_summary()["checks"]
        self.assertEqual(c["differences_from_saved_reading"], 0)
        self.assertEqual(c["day_only_videos_whose_day_key_was_read_again"], c["day_only_videos"])
        self.assertEqual(c["id_not_in_table_videos_whose_identifier_was_read_again"], c["id_not_in_table_videos"])
        self.assertEqual(c["values_read_again_and_compared_by_saved_key"]["testpoint_2013"], 163)


class ShippedFiles(unittest.TestCase):
    def test_shipped_files_pass_verify(self):
        p = subprocess.run([sys.executable, os.path.join(HERE, "index_by_name.py"), "--verify"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("0 differences", p.stdout)

    def test_verify_catches_a_changed_file(self):
        with tempfile.TemporaryDirectory() as d:
            for fn in os.listdir(ib.DEFAULT_OUT):
                if fn.startswith(("video_links", "shortlist_")):
                    shutil.copy(os.path.join(ib.DEFAULT_OUT, fn), d)
            p = os.path.join(d, "shortlist_iss_P1_main_view.csv")
            with open(p, "a", encoding="utf-8") as fh:
                fh.write("BASS2-X,made-up.mp4,1,PSI-25,whole recording,two_labels_agree,,,,no,x\n")
            r = subprocess.run([sys.executable, os.path.join(HERE, "index_by_name.py"), "--verify", "--out", d],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1, r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
