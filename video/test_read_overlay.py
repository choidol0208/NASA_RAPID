# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Unit tests for read_overlay.py that run without the videos.

    python3 video/test_read_overlay.py

Fixtures (video/fixtures/) are grayscale overlay strips cut from NASA's PSI-25 BASS-II clips by
video/tools/make_fixtures.py, exactly as the reader sees them (strip box of the settings only):
  O9_t576.png    O9 clip at 576 s:  FUEL -2, AIR 10, FAN 198 (frame caught mid-change), RAD 0.3, clock 15:33:17
  M17_t202.png   M17 clip at 202 s: FUEL -1, AIR 9,  FAN 69,  RAD 1.9, clock 15:15:33
  O19_t1009.png  O19 clip at 1009 s: FUEL -2, AIR 39, FAN 123, RAD 0.2, clock 17:05:47
  P25_t608.png   P25 clip at 608 s: FUEL -2, AIR 0,  FAN 41,  RAD 0.9, clock 17:57:50
  P5_t945.png    P5 clip at 945 s: blue screen, no overlay
  P22b_t430.png  P22b clip at 430 s: colour bars, no overlay
The expected values are the by-eye readings of these frames in the pilot's second review (hard cases), rows
k = 44, 4, 3, 1 of its audit file sceptic_overlay_compare.csv. That file is in the pilot folder, which is not
shipped and not part of the repository; see video/fixtures/README.md. "By eye" means that an AI assistant
(Claude) looked at each frame image and wrote the numbers down before it saw the reader's values. No person
has checked a frame.
"""
import copy
import json
import os
import shutil
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import read_overlay as ro  # noqa: E402

SETTINGS = os.path.join(HERE, "settings", "bass2.json")
FIX = os.path.join(HERE, "fixtures")
EXPECTED = {
    "O9_t576": {"FUEL": "-2", "AIR_cm_s": "10", "FAN_display": "198", "RAD_trunc1": "0.3", "clock_hhmmss": "153317"},
    "M17_t202": {"FUEL": "-1", "AIR_cm_s": "9", "FAN_display": "69", "RAD_trunc1": "1.9", "clock_hhmmss": "151533"},
    "O19_t1009": {"FUEL": "-2", "AIR_cm_s": "39", "FAN_display": "123", "RAD_trunc1": "0.2", "clock_hhmmss": "170547"},
    "P25_t608": {"FUEL": "-2", "AIR_cm_s": "0", "FAN_display": "41", "RAD_trunc1": "0.9", "clock_hhmmss": "175750"},
}
VALUE_COLS = ["FUEL", "AIR_cm_s", "FAN_display", "RAD_trunc1", "clock_hhmmss"]


def strip(name):
    return np.asarray(Image.open(os.path.join(FIX, name + ".png")), dtype=np.uint8)


class ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = ro.load_settings(SETTINGS)
        cls.state = ro.load_state(cls.settings)
        cls.reader = ro.Reader(cls.settings, cls.state)

    def read(self, name):
        short = name.split("_t")[0]
        return self.reader.read_strip(strip(name), self.state["x0"][short])

    def test_digits_read_correctly(self):
        for name, want in EXPECTED.items():
            with self.subTest(fixture=name):
                got = self.read(name)
                self.assertTrue(got["overlay_present"])
                self.assertEqual({c: got[c] for c in VALUE_COLS}, want)

    def test_no_overlay_gives_empty_cells(self):
        h, w = self.settings["strip"]["rows"][1] - self.settings["strip"]["rows"][0], \
            self.settings["strip"]["cols"][1] - self.settings["strip"]["cols"][0]
        cases = {"P5_t945": strip("P5_t945"), "P22b_t430": strip("P22b_t430"),
                 "black": np.zeros((h, w), np.uint8), "bright": np.full((h, w), 255, np.uint8)}
        for name, s in cases.items():
            with self.subTest(strip=name):
                got = self.reader.read_strip(s, 160.0)
                self.assertFalse(got["overlay_present"])
                self.assertEqual([got[c] for c in VALUE_COLS], [""] * len(VALUE_COLS))

    def test_half_updated_rule_flags_impossible_value(self):
        rows = []
        for t, name in enumerate(["P25_t608", "O9_t576", "O19_t1009"]):
            r = self.read(name)
            r["t_video_s"] = float(t)
            rows.append(r)
        ro.apply_flags(rows, self.settings)
        self.assertEqual(rows[1]["FAN_display"], "198")
        self.assertEqual([r["flag"] for r in rows], ["", "half_updated", ""])  # 198 flagged, 123 and 41 not

    def test_clock_rule_flags_isolated_off_line_clock_only(self):
        def row(t, clock):
            return {"t_video_s": float(t), "clock_hhmmss": clock, "FAN_display": "41"}
        clocks = ["144456", "144457", "144458", "144459", "144559", "144500", "144501"]  # pattern seen in O11
        rows = [row(t, c) for t, c in enumerate(clocks)]
        ro.apply_flags(rows, self.settings)
        self.assertEqual([r["flag"] for r in rows], ["", "", "", "", "half_updated", "", ""])
        rows = [row(t, c) for t, c in enumerate(["144458"] + clocks[1:])]  # first row off by 2 s: not flagged
        ro.apply_flags(rows, self.settings)
        self.assertEqual(rows[0]["flag"], "")
        rows = [row(t, c) for t, c in enumerate(clocks)]
        rows[3]["clock_hhmmss"] = ""  # unread neighbour: no flag
        ro.apply_flags(rows, self.settings)
        self.assertEqual(rows[4]["flag"], "")

    def test_partial_text_is_empty_never_guessed(self):
        f = {"kind": "number", "format": "^\\d{2,3}$"}
        self.assertEqual(ro.parse_field(f, " 41"), "41")
        self.assertEqual(ro.parse_field(f, " 4?"), "")
        self.assertEqual(ro.parse_field(f, "4 1"), "")
        c = {"kind": "clock_hhmmss"}
        self.assertEqual(ro.parse_field(c, "14413?"), "")
        self.assertEqual(ro.parse_field(c, "146100"), "")
        self.assertEqual(ro.parse_field(c, "144130"), "144130")

    def test_state_checksum_is_enforced(self):
        bad = copy.deepcopy(self.settings)
        bad["reader_state"]["sha256"] = "0" * 64
        with self.assertRaises(ro.ReaderError):
            ro.load_state(bad)
        with tempfile.TemporaryDirectory() as d:
            src = os.path.normpath(os.path.join(self.settings["_dir"], self.settings["reader_state"]["file"]))
            tampered = os.path.join(d, "state.npz")
            shutil.copy(src, tampered)
            with open(tampered, "ab") as fh:
                fh.write(b"\0")
            s2 = copy.deepcopy(self.settings)
            s2["_dir"] = d
            s2["reader_state"]["file"] = "state.npz"
            with self.assertRaises(ro.ReaderError):
                ro.load_state(s2)

    def test_settings_columns(self):
        self.assertEqual(self.settings["columns"], ["t_video_s", "clock_hhmmss", "overlay_present", "FUEL", "AIR_cm_s",
                                                    "FAN_display", "RAD_trunc1", "flag"])
        with tempfile.TemporaryDirectory() as d:
            with open(SETTINGS, encoding="utf-8") as fh:
                s = json.load(fh)
            s["columns"].append("NOT_A_FIELD")
            p = os.path.join(d, "s.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(s, fh)
            with self.assertRaises(ro.ReaderError):
                ro.load_settings(p)


    def test_settings_without_clock_or_disclosure_stop_with_a_clear_error(self):
        for key in ("clock_check", "disclosure"):
            with self.subTest(missing=key), tempfile.TemporaryDirectory() as d:
                with open(SETTINGS, encoding="utf-8") as fh:
                    s = json.load(fh)
                del s[key]
                p = os.path.join(d, "s.json")
                with open(p, "w", encoding="utf-8") as fh:
                    json.dump(s, fh)
                with self.assertRaises(ro.ReaderError):
                    ro.load_settings(p)

    def test_no_clip_read_exits_non_zero(self):
        with tempfile.TemporaryDirectory() as clips, tempfile.TemporaryDirectory() as out:
            rc = ro.main(["--settings", SETTINGS, "--clips", clips, "--out", out, "--jobs", "1"])
            self.assertNotEqual(rc, 0)
            with open(os.path.join(out, "reading_manifest.json"), encoding="utf-8") as fh:
                m = json.load(fh)
            self.assertEqual(m["clips"], [])
            self.assertEqual(m["about"], self.settings["disclosure"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
