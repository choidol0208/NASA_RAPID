#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Assemble the static dashboard into web/dist/ for GitHub Pages.

Usage:  python3 web/build.py
Copies the page files and the data the page reads. No third-party packages.
"""
import csv
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(HERE, "dist")

PAGE = ["index.html", "style.css", "app.js", "scorer.js"]
DASH_SCENARIOS = {"iss", "lunar_habitat"}  # the only scenarios the page shows (same set as app.js)
DATA = {
    "scoring/scoring_config.json": "data/scoring_config.json",
    "data/catalog/investigations.csv": "data/investigations.csv",
    "data/catalog/configurations.csv": "data/configurations.csv",
    "data/pipeline/capability_matrix.csv": "data/capability_matrix.csv",
    "pipeline/spec/needs.json": "data/needs.json",
    "data/pipeline/coverage_grid.csv": "data/coverage_grid.csv",
    "pipeline/spec/coverage.json": "data/coverage.json",
    "data/pipeline/need_references.csv": "data/need_references.csv",
}
OPTIONAL = {
    "data/insights/cards.json": "data/insights/cards.json",
    "data/insights/scenarios.json": "data/insights/scenarios.json",
    "data/insights/evidence_map.json": "data/insights/evidence_map.json",
    # "How AI is used here, and how it was checked" (pm request 1705)
    "data/insights/quality.json": "data/insights/quality.json",
    "data/insights/model_readiness.json": "data/insights/model_readiness.json",
    "data/insights/robustness.json": "data/insights/robustness.json",
    "data/pipeline/scenario_needs.csv": "data/scenario_needs.csv",
    "pipeline/spec/scenarios.json": "data/scenario_spec.json",
}


def slim_csv(src, dst, columns, keep=lambda row: True, line_column=None):
    """Copy only the columns (and rows) the page reads, so a phone downloads less.
    Values are copied unchanged. With line_column, each row carries the line it starts on
    in the source file, so links still point at the exact row of the full file."""
    with open(src, encoding="utf-8-sig", newline="") as fh, open(dst, "w", encoding="utf-8", newline="") as out:
        rd = csv.reader(fh)
        header = next(rd)
        idx = [header.index(c) for c in columns]
        w = csv.writer(out, lineterminator="\n")
        w.writerow(columns + ([line_column] if line_column else []))
        start, n = rd.line_num + 1, 0
        for row in rd:
            rec = dict(zip(header, row))
            if keep(rec):
                w.writerow([row[i] if i < len(row) else "" for i in idx] + ([start] if line_column else []))
                n += 1
            start = rd.line_num + 1
    return n


OPTIONAL_BUILT = []  # optional files written by this script (listed in build.json)


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, "data", "insights"))
    for f in PAGE:
        shutil.copy(os.path.join(HERE, f), os.path.join(DIST, f))
    for src, dst in DATA.items():
        shutil.copy(os.path.join(ROOT, src), os.path.join(DIST, dst))
    for src, dst in OPTIONAL.items():
        if os.path.exists(os.path.join(ROOT, src)):
            shutil.copy(os.path.join(ROOT, src), os.path.join(DIST, dst))
    # Slim copies of the two large test files (the page links to the full files in the repository).
    slim_csv(os.path.join(ROOT, "data/pipeline/tests.csv"), os.path.join(DIST, "data/tests.csv"),
             ["test_id", "source_file", "source_row", "o2_pct", "pressure_kpa"], line_column="line")
    st = os.path.join(ROOT, "data/pipeline/scenario_tests.csv")
    if os.path.exists(st):
        slim_csv(st, os.path.join(DIST, "data/scenario_tests.csv"),
                 ["scenario_id", "test_id", "investigation_id", "fuel_phase", "flow_match", "gravity_match", "tier"],
                 keep=lambda r: r.get("scenario_id") in DASH_SCENARIOS)
    # Export for researchers (pm request 1449): the matched tests of each demo scenario, joined to
    # their row in data/pipeline/tests.csv. Values are copied as data wrote them; nothing is computed.
    if os.path.exists(st):
        os.makedirs(os.path.join(DIST, "data", "export"), exist_ok=True)
        tests = {r["test_id"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/pipeline/tests.csv"), encoding="utf-8-sig"))}
        cols = ["scenario_id", "tier", "test_id", "investigation_id", "source_id", "fuel_phase", "fuel_material", "o2_pct", "o2_basis",
                "o2_range_as_written", "pressure_kpa", "flow_cms", "flow_min_cms", "gravity_level", "flags", "source_file", "source_row"]
        for sid in sorted(DASH_SCENARIOS):
            rows = [r for r in csv.DictReader(open(st, encoding="utf-8-sig")) if r["scenario_id"] == sid and r["tier"] != "other"]
            with open(os.path.join(DIST, "data", "export", f"scenario_{sid}_matched_tests.csv"), "w", encoding="utf-8", newline="") as out:
                w = csv.writer(out, lineterminator="\n")
                w.writerow(cols)
                for r in rows:
                    t = tests.get(r["test_id"], {})
                    w.writerow([r["scenario_id"], r["tier"]] + [t.get(c, r.get(c, "")) for c in cols[2:]])
            OPTIONAL_BUILT.append(f"data/export/scenario_{sid}_matched_tests.csv")
            if os.path.exists(os.path.join(ROOT, f"data/pipeline/evidence/scenario_{sid}.json")):
                OPTIONAL_BUILT.append(f"repo:data/pipeline/evidence/scenario_{sid}.json")  # linked in the repository
    # Indicators per need for each demo scenario (pm request 1505), copied from data's evidence
    # packages, with the lines of their tests in data/pipeline/indicator_tests.csv for links.
    it_path = os.path.join(ROOT, "data/pipeline/indicator_tests.csv")
    it_lines = {}
    if os.path.exists(it_path):
        with open(it_path, encoding="utf-8-sig", newline="") as fh:
            rd = csv.reader(fh)
            head = next(rd)
            ii, gi = head.index("indicator_id"), head.index("group")
            start = rd.line_num + 1
            for row in rd:
                key = (row[ii], row[gi])
                lo, hi = it_lines.get(key, (start, start))
                it_lines[key] = (min(lo, start), max(hi, rd.line_num))
                start = rd.line_num + 1
    for sid in sorted(DASH_SCENARIOS):
        pkg = os.path.join(ROOT, f"data/pipeline/evidence/scenario_{sid}.json")
        if not os.path.exists(pkg):
            continue
        needs = json.load(open(pkg, encoding="utf-8-sig")).get("needs", [])
        pairs = needs.items() if isinstance(needs, dict) else [(b.get("need_id"), b) for b in needs]
        out = {}
        for nid, blk in pairs:
            rows = []
            for ind in blk.get("indicators") or []:
                r = dict(ind)
                span = it_lines.get((ind.get("indicator_id", ""), ind.get("group", "")))
                if span:
                    r["tests_lines"] = list(span)
                rows.append(r)
            out[nid] = rows
        os.makedirs(os.path.join(DIST, "data", "indicators"), exist_ok=True)
        with open(os.path.join(DIST, "data", "indicators", f"scenario_{sid}.json"), "w", encoding="utf-8") as fh:
            json.dump({"source": f"data/pipeline/evidence/scenario_{sid}.json", "needs": out}, fh, ensure_ascii=False)
        OPTIONAL_BUILT.append(f"data/indicators/scenario_{sid}.json")
    # Raw-data line per investigation (pm request 1449, item 3): data's fixed sentence from the PSI file listing.
    ri = os.path.join(ROOT, "data/pipeline/raw_inventory.json")
    if os.path.exists(ri):
        inv = json.load(open(ri, encoding="utf-8-sig")).get("investigations", [])
        sentences = {e["investigation_id"]: e.get("sentence", "") for e in inv if e.get("sentence")}
        with open(os.path.join(DIST, "data", "raw_inventory_sentences.json"), "w", encoding="utf-8") as fh:
            json.dump({"source": "data/pipeline/raw_inventory.json", "sentences": sentences}, fh, ensure_ascii=False)
        OPTIONAL_BUILT.append("data/raw_inventory_sentences.json")
    # pm's video side pilot (request 1709): one sentence on the page, linked to the README at the built commit.
    if os.path.exists(os.path.join(ROOT, "video", "README.md")):
        OPTIONAL_BUILT.append("repo:video/README.md")
    # data's answer files (request 1531): one per scenario and need, fixed sentences in four rungs.
    # Copied unchanged; a small index per scenario carries each need's top line, so the page loads a
    # need's file only when its section is opened.
    ans_dir = os.path.join(ROOT, "data/pipeline/answers")
    if os.path.isdir(ans_dir):
        os.makedirs(os.path.join(DIST, "data", "answers"), exist_ok=True)
        for sid in sorted(DASH_SCENARIOS):
            index = {}
            for name in sorted(os.listdir(ans_dir)):
                if not (name.startswith(sid + "__") and name.endswith(".json")):
                    continue
                need = name[len(sid) + 2:-5]
                shutil.copy(os.path.join(ans_dir, name), os.path.join(DIST, "data", "answers", name))
                doc = json.load(open(os.path.join(ans_dir, name), encoding="utf-8-sig"))
                index[need] = {"file": f"data/answers/{name}", "top_line": (doc.get("top_line") or {}).get("text", ""),
                               "source": f"data/pipeline/answers/{name}"}
            if index:
                with open(os.path.join(DIST, "data", "answers", f"{sid}_index.json"), "w", encoding="utf-8") as fh:
                    json.dump(index, fh, ensure_ascii=False)
                OPTIONAL_BUILT.append(f"data/answers/{sid}_index.json")
    # The three piles per question (pm request 20261115-0035, step 8 of docs/raw_data_design/design.md):
    # fixed sentences filled from the team's files by web/raw_piles.py. Its checks (fixture F1, chain
    # cross-check, bar sums, the "17" rule, the word scan, no unfilled slot) stop the build on failure.
    import raw_piles  # noqa: E402  (web/ is on sys.path when this script runs)
    piles = raw_piles.build(ROOT)
    os.makedirs(os.path.join(DIST, "data", "piles"), exist_ok=True)
    for sid, doc in piles.items():
        with open(os.path.join(DIST, "data", "piles", f"{sid}.json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False)
        OPTIONAL_BUILT.append(f"data/piles/{sid}.json")
    print("three piles: " + ", ".join(f"{k} ({len(v['needs'])} questions)" for k, v in piles.items()))
    # Results first (pm request 20261115-1513): what NASA's documents report, per environment and question,
    # from the data role's results_by_need.json; results_flat.csv is offered as a download.
    import results_first  # noqa: E402
    res = results_first.build(ROOT)
    if res:
        os.makedirs(os.path.join(DIST, "data", "results"), exist_ok=True)
        for sid, doc in res.items():
            with open(os.path.join(DIST, "data", "results", f"{sid}.json"), "w", encoding="utf-8") as fh:
                json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
            OPTIONAL_BUILT.append(f"data/results/{sid}.json")
        flat = os.path.join(ROOT, "data", "pipeline", "results_flat.csv")
        if os.path.exists(flat):
            shutil.copy(flat, os.path.join(DIST, "data", "results", "results_flat.csv"))
            OPTIONAL_BUILT.append("data/results/results_flat.csv")
        print("results first: " + ", ".join(f"{k} ({sum(len(n['entries']) for n in v['needs'])} results)" for k, v in res.items()))
    # the files of each test inside the ranges (data's test_files.json), loaded by the page on request
    for sid, doc in raw_piles.build_files(ROOT).items():
        with open(os.path.join(DIST, "data", "piles", f"{sid}_files.json"), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
        OPTIONAL_BUILT.append(f"data/piles/{sid}_files.json")
        print(f"files of the tests inside: {sid} ({len(doc)} tests, {sum(t['files'] for t in doc.values())} files)")
    # Link preview image: web/media/og.png (1200 x 630, written by capture_media.mjs), else the old draft.
    for og in (os.path.join(HERE, "media", "og.png"), os.path.join(HERE, "media", "02_lunar_top.png")):
        if os.path.exists(og):
            shutil.copy(og, os.path.join(DIST, "og.png"))
            break
    # The commit the site was built from, so links to source files and rows point at
    # exactly the files the page reads (GITHUB_SHA in Actions, git HEAD locally).
    sha = os.environ.get("GITHUB_SHA")
    if not sha:
        try:
            sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            sha = "main"
    # pm's SI assistant widget (request 20261115-1146, docs/assistant/for_ui.md). On the public page it runs
    # no model and calls no API: it replays the recorded conversations. ui's choice (pm left it open): the
    # widget is included only once the recorded conversations exist, so a reader never meets an empty box
    # that asks for a local server. The test fixtures under ai/assistant/static/mock/ are never published.
    assistant = False
    a_js, a_css = os.path.join(ROOT, "ai/assistant/static/assistant.js"), os.path.join(ROOT, "ai/assistant/static/assistant.css")
    a_rec, a_eval = os.path.join(ROOT, "data/insights/assistant_recorded.json"), os.path.join(ROOT, "data/insights/assistant_eval.json")
    if os.path.exists(a_js) and os.path.exists(a_css) and (os.path.exists(a_rec) or os.environ.get("ASSISTANT_PREVIEW") == "1"):
        os.makedirs(os.path.join(DIST, "assistant"), exist_ok=True)
        for src, dst in ((a_js, "assistant.js"), (a_css, "assistant.css"), (a_rec, "recorded.json"), (a_eval, "eval.json")):
            if os.path.exists(src):
                shutil.copy(src, os.path.join(DIST, "assistant", dst))
                OPTIONAL_BUILT.append(f"assistant/{dst}")
        assistant = True
    print("assistant widget: " + ("included" if assistant else "not included (data/insights/assistant_recorded.json not on this branch yet)"))
    # Optional files actually in this build: the page fetches only these (no 404 for a file not yet made).
    present = sorted(dst for dst in OPTIONAL.values() if os.path.exists(os.path.join(DIST, dst)))
    if os.path.exists(os.path.join(DIST, "data/scenario_tests.csv")):
        present.append("data/scenario_tests.csv")
    present += OPTIONAL_BUILT
    with open(os.path.join(DIST, "data", "build.json"), "w", encoding="utf-8") as fh:
        json.dump({"commit": sha, "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "optional": present}, fh)
    # Stamp the build into every asset URL (Pages lets browsers cache files for 10 minutes): a new
    # deploy is read at once, and a page never mixes files from two builds.
    v = sha[:12] if sha != "main" else datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    stamp = {
        "index.html": [('href="style.css"', f'href="style.css?v={v}"'), ('src="app.js"', f'src="app.js?v={v}"')] + (
            [("</head>", f'<link rel="stylesheet" href="assistant/assistant.css?v={v}">\n</head>'),
             ("</body>", f'<script src="assistant/assistant.js?v={v}" defer></script>\n</body>')] if assistant else []),
        "app.js": [('from "./scorer.js"', f'from "./scorer.js?v={v}"'), ('const DATA_V = "__BUILD__";', f'const DATA_V = "{v}";')],
    }
    for name, pairs in stamp.items():
        p = os.path.join(DIST, name)
        text = open(p, encoding="utf-8").read()
        for old, new in pairs:
            if old not in text:
                raise SystemExit(f"build: cannot stamp {name}: {old!r} not found")
            text = text.replace(old, new, 1)
        open(p, "w", encoding="utf-8", newline="\n").write(text)
    open(os.path.join(DIST, ".nojekyll"), "w").close()
    n = sum(len(fs) for _, _, fs in os.walk(DIST))
    print(f"built {n} files into {DIST}")


if __name__ == "__main__":
    main()
