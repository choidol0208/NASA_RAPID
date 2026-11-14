#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Check that the dashboard's JavaScript scorer (web/scorer.js) gives the same results as
scoring.scorer.rank. Runs every validation scenario plus extra queries. Exit 1 on any
difference. Needs node (>= 18) on PATH.

Usage:  python3 web/parity_check.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from scoring.scorer import rank  # noqa: E402

EXTRA = [
    "ISS", "lunar habitat", "spacesuit", "Mars base", "moon cotton fabric", "ISS cotton fabric opposed flow 5 cm/s",
    "smoke detector", "CO2 suppression heptane", "helium extinguish methanol droplet", "30% O2 at 10.2 psi",
    "40% oxygen 70 kPa fabric", "PMMA rod 15 cm/s 18% O2", "thin PMMA film stagnant", "thick acrylic slab ventilation",
    "silicone sheet ISS", "nomex fabric lunar", "wire insulation overheat smoke", "kapton teflon smoke",
    "propane 40% oxygen", "methane jet", "hydrogen leak", "dust", "paper fire", "wax candle", "earth sea level fabric",
    # Korean queries: Mars base 30% oxygen; space station cotton fabric; lunar base acrylic stagnant zone;
    # smoke detection; carbon dioxide suppression heptane
    "화성 기지 산소 30%", "우주정거장 면직물", "달 기지 아크릴 정체 구역", "연기 감지", "이산화탄소 소화 헵탄",
    "rocket engine", "", "   ", "random words", "100% O2 4.3 psi", "21% O2 101.3 kPa PMMA 10 cm/s opposed",
    {"preset": "iss", "fuel": "PMMA", "o2_pct": 25}, {"text": "moon", "concern": "detection"},
    {"preset": "lunar_habitat", "fuel": "cotton", "flow_state": "quiescent"},
    # equipment queries (pm request 1453) and words the scorer does not read
    "smoke detector for a lunar rover", "fire extinguisher for a Mars habitat", "crew clothing fabric for a Moon base",
    "wire insulation for a pressurized rover", "water mist suppression system for a lunar habitat",
    "battery enclosure for the ISS", "3D printer on the Moon", "glove box", "천장 배선 과열", "달 기지 배터리 보관함",  # Korean: ceiling wiring overheating; lunar base battery box
    "oxygen sensor, ISS cabin (CO2 30%)", {"text": "battery enclosure", "preset": "iss"},
]


def key_view(o):
    """The parts that must match exactly, plus scores rounded for comparison."""
    def res(r):
        return dict(id=r["investigation_id"], cfg=r["config_id"], score=r["score"], gate=r["gate"],
                    evidence=r["evidence"], warnings=[w["code"] for w in r["warnings"]],
                    why=r["why"], gap=r["main_gap"], complementary=r.get("complementary"),
                    confidence=r.get("confidence"), unknown=r["unknown_dims"], assumed=r.get("assumed_dims", []))
    return dict(
        status=o["status"], scenario=o["scenario"], not_understood=o.get("not_understood"),
        assumptions=[(a["field"], a["source"]) for a in o["assumptions"]],
        warnings=[(w["code"], w["message"]) for w in o["warnings"]],
        results=[res(r) for r in o["results"]],
        ranking=[(r["investigation_id"], r["config_id"], r["score"]) for r in o["ranking"]],
    )


def same(a, b, path=""):
    if isinstance(a, float) or isinstance(b, float):
        try:
            return abs(float(a) - float(b)) <= 0.05 + 1e-9, path
        except (TypeError, ValueError):
            return False, path
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False, f"{path} length {len(a)} != {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            ok, p = same(x, y, f"{path}[{i}]")
            if not ok:
                return False, p
        return True, path
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return False, f"{path} keys {sorted(set(a) ^ set(b))}"
        for k in a:
            ok, p = same(a[k], b[k], f"{path}.{k}")
            if not ok:
                return False, p
        return True, path
    return a == b, path


def main():
    scen = json.load(open(os.path.join(ROOT, "validation", "scenarios.json"), encoding="utf-8"))
    queries = [s["query"] for s in scen["scenarios"]] + EXTRA
    py = [key_view(rank(q)) for q in queries]
    out = subprocess.run(["node", os.path.join(HERE, "parity_check.mjs")], input=json.dumps(queries),
                         capture_output=True, text=True, check=True)
    js = [key_view(o) for o in json.loads(out.stdout)]
    bad = 0
    for q, a, b in zip(queries, py, js):
        ok, where = same(a, b)
        if not ok:
            bad += 1
            print(f"DIFF {q!r} at {where}")
    print(f"parity: {len(queries) - bad}/{len(queries)} queries identical")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
