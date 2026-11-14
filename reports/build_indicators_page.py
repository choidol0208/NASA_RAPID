#!/usr/bin/env python3
# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Build the internal team page of indicator results (Korean).

Reads   data/pipeline/indicators.csv, scenario_needs.csv, need_references.csv,
        run_report.json, pipeline/spec/*.json, reports/indicators_ko.json,
        reports/indicators.template.html
Writes  reports/indicators.html

The page shows pipeline outputs as they are; it computes nothing new.
Usage:  python3 reports/build_indicators_page.py
"""
import json
import os
import subprocess
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "pipeline")


def load(name):
    return pd.read_csv(os.path.join(OUT, name)).fillna("")


def main():
    ko = json.load(open(os.path.join(ROOT, "reports", "indicators_ko.json"), encoding="utf-8"))
    needs = json.load(open(os.path.join(ROOT, "pipeline", "spec", "needs.json"), encoding="utf-8"))["needs"]
    spec = json.load(open(os.path.join(ROOT, "pipeline", "spec", "indicators.json"), encoding="utf-8"))["indicators"]
    report = json.load(open(os.path.join(OUT, "run_report.json"), encoding="utf-8"))
    ind, sc, refs = load("indicators.csv"), load("scenario_needs.csv"), load("need_references.csv")

    missing = [i["id"] for i in spec if i["id"] not in ko["indicators"]]
    missing += [n["id"] for n in needs if n["id"] not in ko["needs"]]
    if missing:
        sys.exit(f"no Korean label for: {missing}")

    def group_label(group):
        parts = []
        for kv in group.split(";"):
            if "=" not in kv:
                continue
            k, v = kv.split("=", 1)
            parts.append(ko["values"].get(k, {}).get(v, v))
        return " · ".join(parts) or "전체"

    page_needs = []
    for need in needs:
        items = []
        for s in spec:
            if s["need_id"] != need["id"]:
                continue
            rows = ind[ind.indicator_id == s["id"]]
            unit = ko["units"].get(rows.unit.iloc[0], rows.unit.iloc[0]) if len(rows) else ""
            groups = []
            for group, g in rows.groupby("group", sort=False):
                entry = {"label": group_label(group), "n": int(g.n_tests.iloc[0]),
                         "inv": g.investigation_ids.iloc[0].replace(";", ", ")}
                if s["template"] == "summary":
                    entry.update({r.stat: float(r.value) for r in g.itertuples()})
                elif s["template"] == "count_by":
                    cats = ko["values"].get(s["variable"], {})
                    entry["cats"] = [[cats.get(r.category, r.category), int(r.value)] for r in g.itertuples()]
                else:
                    entry["count"] = int(g.value.iloc[0])
                groups.append(entry)
            items.append({"id": s["id"], "template": s["template"], "unit": unit,
                          "label": ko["indicators"][s["id"]]["label"],
                          "reading": ko["indicators"][s["id"]]["reading"],
                          "compare": s.get("compare_with", []), "groups": groups})
        docs = refs[refs.need_id == need["id"]][["title", "version", "url"]].drop_duplicates("title")
        k = ko["needs"][need["id"]]
        page_needs.append({"id": need["id"], "name": k["name"], "pillar": k["pillar"],
                           "question": k["question"], "criterion": k["criterion"],
                           "docs": docs.to_dict("records"), "indicators": items})

    scenarios = []
    for sid, g in sc.groupby("scenario_id", sort=False):
        scenarios.append({"id": sid, "label": ko["scenarios"][sid], "ranges": ko["scenario_ranges"][sid],
                          "needs": [{"need_id": r.need_id, "status": r.status,
                                     "status_label": ko["status"][r.status],
                                     "usable": int(r.usable_tests), "atmosphere": int(r.tests_atmosphere),
                                     "oxygen_only": int(r.tests_oxygen_only),
                                     "inv": (r.investigations_atmosphere or r.investigations_oxygen_only).replace(";", ", "),
                                     "gaps": [ko["gaps"][c] for c in r.gaps.split(";") if c]}
                                    for r in g.itertuples()]})

    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    data = {"commit": commit, "tests": report["tests"], "values": report["values"],
            "n_indicators": len(spec), "n_docs": int(refs.reference_id.nunique()),
            "needs": page_needs, "scenarios": scenarios}
    template = open(os.path.join(ROOT, "reports", "indicators.template.html"), encoding="utf-8").read()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("/*DATA*/null", payload)
    with open(os.path.join(ROOT, "reports", "indicators.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"reports/indicators.html  {len(html) // 1024} KB, commit {commit}")


if __name__ == "__main__":
    main()
