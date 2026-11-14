#!/usr/bin/env python3
# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Build the team data-map page from the profile and the annotations.

Usage:
    python3 scripts/build_data_map.py
Reads   data/derived/data_profile.json, data/derived/annotations_ko.json,
        reports/data-map.template.html
Writes  reports/data-map.html
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    profile = json.load(open(os.path.join(ROOT, "data", "derived", "data_profile.json")))
    notes = json.load(open(os.path.join(ROOT, "data", "derived", "annotations_ko.json")))

    # Sanity check: every table needs one annotation per column.
    problems = []
    for inv in profile["investigations"]:
        if inv["accession"] not in notes["investigations"]:
            problems.append(f"no note for {inv['accession']}")
        for t in inv["tables"]:
            ann = notes["tables"].get(t["file"])
            if ann is None:
                problems.append(f"no table note: {t['file']}")
            elif len(ann["columns"]) != len(t["columns"]):
                problems.append(f"{t['file']}: {len(ann['columns'])} notes for "
                                f"{len(t['columns'])} columns")
        # The page does not need per-extension stats or sample rows.
        inv.pop("files_by_ext", None)
        for t in inv["tables"]:
            t.pop("sample_rows", None)
    if problems:
        sys.exit("annotation mismatch:\n  " + "\n  ".join(problems))

    payload = json.dumps({"profile": profile, "notes": notes},
                         ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")  # keep </script> out of the page
    # The FLEX table contains U+FFFD (a character lost in NASA's export).
    # Keep it as data, but as a JS escape rather than a literal in the page.
    payload = payload.replace("�", "\\ufffd")
    template = open(os.path.join(ROOT, "reports", "data-map.template.html"),
                    encoding="utf-8").read()
    marker = "/*__DATA__*/null"
    if marker not in template:
        sys.exit("template marker not found")
    out = os.path.join(ROOT, "reports", "data-map.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(template.replace(marker, payload))
    print(f"wrote {out} ({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
