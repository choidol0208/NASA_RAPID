#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Check the joins the dashboard relies on, from a ranked result to the data role's files.

For representative queries, every top-3 result of scoring.scorer.rank must reach its data:
  - the PSI record and manifest entry (accession, dataset DOI, experimental-table file);
  - the catalog row the page links to (line number in the CSV);
  - its rows in data/pipeline/capability_matrix.csv (the needs view), or no table at all;
  - its tests in data/pipeline/tests.csv: the configuration's own subset of tests, whose count
    and O2/pressure/flow ranges must agree with the catalog configuration.

Usage:  python3 web/check_integration.py [--emit expected.json]     (exit 1 on a broken join)
--emit writes what the page should show for each query (results and needs cells), so a
browser check can compare it with the rendered page. Standard library only.
"""
import csv
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from scoring.scorer import rank  # noqa: E402

QUERIES = ["ISS", "lunar habitat", "ISS cotton fabric", "lunar habitat cotton fabric", "smoke detector on ISS",
           "CO2 suppression of heptane fire", "gas jet flame ISS", "PMMA rod 15 cm/s 18% O2", "50% O2", "spacesuit", "Mars base"]
TOL = 0.051
STATUS = {"measured": "Measured", "partial": "Partial", "conditions_only": "Conditions only", "none": "Not usable",
          "out_of_scope": "Not applicable", "not_test_level": "Summary rows"}
RECORDED = {"measured", "partial", "conditions_only", "none"}


def read_csv(path):
    return list(csv.DictReader(open(os.path.join(ROOT, path), encoding="utf-8-sig")))


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def span(vals):
    v = [x for x in vals if x is not None]
    return (min(v), max(v)) if v else None


def raw_rows_by_line(file):
    """NASA table rows keyed by the line each starts on (header = line 1), as data's source_row."""
    text = open(os.path.join(ROOT, "data/psi/experimental_tables", file), "rb").read()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = text.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    rd = csv.reader(io.StringIO(text))
    next(rd)
    out, start = {}, rd.line_num + 1
    for row in rd:
        out[start] = row
        start = rd.line_num + 1
    return out


def bass2_family(m):  # same grouping as scripts/build_catalog.py
    m = m.lower()
    if "sibal" in m: return "sibal"
    if "nomex" in m: return "nomex"
    if "rod" in m: return "rod"
    if "spher" in m or "wax" in m or "candle" in m: return "other"
    if "film" in m or "micron" in m or re.search(r"0\.[1-4] mm", m): return "film"
    return "slab"


def bass_family(m):
    m = m.lower()
    if "sibal" in m: return "sibal"
    if "nomex" in m or "ultem" in m: return "sheet"
    if "wax" in m or "candle" in m: return "wax"
    if "sphere" in m: return "sphere"
    if "soot" in m: return "skip"
    return "slab"


FAMILY = {"BASS-II-C01": "film", "BASS-II-C02": "slab", "BASS-II-C03": "rod", "BASS-II-C04": "sibal", "BASS-II-C05": "nomex",
          "BASS-II-C06": "other", "BASS-C01": "sibal", "BASS-C02": "slab", "BASS-C03": "sphere", "BASS-C04": "wax", "BASS-C05": "sheet"}


def config_subset(c, tests, raw_cache):
    """The tests of tests.csv that belong to one catalog configuration."""
    ref = c["tests_table_ref"] or ""
    file = ref.split(" (")[0].strip()
    note = ref[len(file):].strip(" ()")
    ts = [t for t in tests if t["source_file"] == file]
    cid = c["config_id"]
    if cid in FAMILY:
        raw = raw_cache.setdefault(file, raw_rows_by_line(file))
        fam = bass2_family if cid.startswith("BASS-II") else bass_family
        ts = [t for t in ts if t["source_row"].isdigit() and fam(raw.get(int(t["source_row"]), [""] * 6)[5]) == FAMILY[cid]]
    elif note.startswith("Fuel ="):
        fuel = note.split("=", 1)[1].strip().lower()
        ts = [t for t in ts if fuel in t["fuel_material"].lower()]
    elif re.fullmatch(r"S\d", note):
        ts = [t for t in ts if t["test_id"].endswith("-" + note)]
    elif re.match(r"2-\d", note):
        nums = [int(n) for n in re.findall(r"2-(\d)", note)]
        want = set(range(nums[0], nums[-1] + 1)) if " to " in note else set(nums)
        ts = [t for t in ts if int(t["test_id"].rsplit("-", 1)[1]) in want]
    return ts


def main():
    cfgs = {c["config_id"]: c for c in read_csv("data/catalog/configurations.csv")}
    invs = {r["psi_accession"]: r for r in read_csv("data/catalog/investigations.csv")}
    man = {m["accession"]: m for m in json.load(open(os.path.join(ROOT, "data/psi/manifest.json"), encoding="utf-8"))["investigations"]}
    matrix = read_csv("data/pipeline/capability_matrix.csv")
    tests = read_csv("data/pipeline/tests.csv")
    needs = json.load(open(os.path.join(ROOT, "pipeline/spec/needs.json"), encoding="utf-8-sig"))["needs"]
    order = [n for p in ("prevention", "suppression", "detection") for n in needs if n["pillar"] == p]
    cfg_lines = open(os.path.join(ROOT, "data/catalog/configurations.csv"), encoding="utf-8-sig").read().split("\n")
    cfg_index = list(cfgs)
    inv_lines = open(os.path.join(ROOT, "data/catalog/investigations.csv"), encoding="utf-8-sig").read().split("\n")
    inv_order = [r["investigation_id"] for r in read_csv("data/catalog/investigations.csv")]
    raw_cache, problems, notes, expected = {}, [], [], {}

    for q in QUERIES:
        out = rank(q)
        exp = {"results": [], "needs_rows": []}
        for r in out["results"]:
            acc, cid = r["psi_accession"], r["config_id"]
            c, m, inv = cfgs[cid], man.get(acc), invs.get(acc)
            tag = f"{q!r} #{r['rank']} {r['investigation_id']} ({cid})"
            if not m:
                problems.append(f"{tag}: {acc} not in data/psi/manifest.json")
                continue
            if r["dataset_doi"] != m["doi"]:
                problems.append(f"{tag}: DOI {r['dataset_doi']} != manifest {m['doi']}")
            if not os.path.exists(os.path.join(ROOT, f"data/psi/catalog/{acc}.json")):
                problems.append(f"{tag}: data/psi/catalog/{acc}.json missing")
            files = [t["file"] for t in m.get("experimental_tables", [])]
            ref = (c["tests_table_ref"] or "").split(" (")[0].strip()
            if ref and ref not in files:
                problems.append(f"{tag}: source table {ref!r} is not one of {acc}'s tables in the manifest")
            line = cfg_index.index(cid) + 2  # what web/app.js links to
            if not cfg_lines[line - 1].startswith(cid + ","):
                problems.append(f"{tag}: catalog row link L{line} does not start with {cid}")
            iline = inv_order.index(r["investigation_id"]) + 2
            if not inv_lines[iline - 1].startswith(r["investigation_id"] + ","):
                problems.append(f"{tag}: investigation row link L{iline} does not start with {r['investigation_id']}")
            rows = [x for x in matrix if x["investigation_id"] == acc]
            if files and not rows:
                problems.append(f"{tag}: {acc} has tables but no rows in capability_matrix.csv")
            sub = config_subset(c, tests, raw_cache) if ref else []
            line_notes = []
            if sub or (c["test_count_config"] and any(t["investigation_id"] == acc for t in tests)):
                n_cat = int(float(c["test_count_config"] or 0))
                if n_cat != len(sub):
                    problems.append(f"{tag}: catalog says {n_cat} tests, tests.csv subset has {len(sub)}")
                for label, lo, hi, vals in (
                        ("O2", "o2_min_pct", "o2_max_pct", [f(t["o2_pct"]) for t in sub]),
                        ("kPa", "pressure_min_kpa", "pressure_max_kpa", [f(t["pressure_kpa"]) for t in sub]),
                        ("flow", "flow_min_cms", "flow_max_cms", [f(t[k]) for t in sub for k in ("flow_cms", "flow_min_cms")])):
                    cat, pipe = span([f(c[lo]), f(c[hi])]), span(vals)
                    if cat and pipe:
                        inside = cat[0] - TOL <= pipe[0] and pipe[1] <= cat[1] + TOL
                        equal = abs(cat[0] - pipe[0]) <= TOL and abs(cat[1] - pipe[1]) <= TOL
                        if not inside:
                            problems.append(f"{tag}: {label} catalog {cat} does not contain tests.csv {pipe}")
                        elif not equal:
                            # (a note on the flag range_in_source_midpoint_used was removed on 15 Nov: the pipeline
                            # stopped writing that flag on 14 Nov, 14:40, so it could never fire; data's note 0927)
                            line_notes.append(f"{label} catalog {cat[0]:g}-{cat[1]:g} wider than tests {pipe[0]:g}-{pipe[1]:g}")
                    elif pipe and not cat:
                        problems.append(f"{tag}: {label} {pipe} in tests.csv, missing in the catalog")
            if line_notes:
                notes.append(f"{tag}: " + "; ".join(line_notes))
            exp["results"].append({"rank": r["rank"], "id": r["investigation_id"], "score": r["score"], "config": cid,
                                   "psi": acc, "doi": r["dataset_doi"], "catalog_line": line, "tests_in_config": len(sub)})
        # needs rows the page should draw for the top 3 (one row per source table)
        for r in out["results"]:
            acc = r["psi_accession"]
            by_src = {}
            for x in matrix:
                if x["investigation_id"] == acc:
                    by_src.setdefault(x["source_id"], {})[x["need_id"]] = x
            if not by_src:
                exp["needs_rows"].append({"id": r["investigation_id"], "source": None, "cells": "No experimental table"})
                continue
            for sid, cells in by_src.items():
                labels = []
                for n in order:
                    x = cells.get(n["id"])
                    if not x:
                        labels.append("—")
                    elif x.get("objective_link") == "not_stated" and x["status"] in RECORDED:
                        labels.append("Outside stated objective")
                    else:
                        labels.append(STATUS.get(x["status"], x["status"]))
                exp["needs_rows"].append({"id": r["investigation_id"], "source": sid, "cells": labels})
        expected[q] = exp
        print(f"{q!r}: " + ", ".join(f"{x['rank']}. {x['id']} {x['score']} [{x['config']}, {x['tests_in_config']} tests]" for x in exp["results"]))

    # catalog request 2001: the requirements table needs one compliance entry per requirement, in the
    # same order, with a status the page knows, for every result.
    known = {"met", "near", "not_met", "unverified", "not_scored", "documented"}  # "documented": catalog 0945, config 1.5.0
    known_basis = {"table", "record", "test_matrix", "published", "team", "assumed", "none", "catalog", ""}
    n_cells = 0
    for q in QUERIES:
        o = rank(q)
        ids = [r["id"] for r in o.get("requirements", [])]
        for res in o.get("results", []):
            comp = res.get("compliance") or []
            if [c["id"] for c in comp] != ids:
                problems.append(f"{q!r} {res['investigation_id']}: compliance ids {[c['id'] for c in comp]} != requirements {ids}")
            bad = [c["status"] for c in comp if c["status"] not in known]
            if bad:
                problems.append(f"{q!r} {res['investigation_id']}: unknown compliance status {bad}")
            badb = [c.get("basis") for c in comp if (c.get("basis") or "") not in known_basis]
            if badb:
                problems.append(f"{q!r} {res['investigation_id']}: compliance basis with no wording on the page {badb}")
            n_cells += len(comp)
    print(f"requirements table: {n_cells} cells checked")

    # pm request 2340, item 1: the page shows each scenario frame as a lead (two sentences) and a folded
    # rest. Both parts joined must give the whole frame: no text may be lost at a decimal point.
    frame_split_js = r"/(?<=[.!?])\s+(?=[A-Z(\"'])/"
    app_js = open(os.path.join(ROOT, "web", "app.js"), encoding="utf-8").read()
    if f"const FRAME_SPLIT = {frame_split_js.replace(chr(92) + chr(34), chr(34))};" not in app_js:
        problems.append("web/app.js: FRAME_SPLIT is not the expression this check tests")
    frame_split = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\"'])")
    scen_path = os.path.join(ROOT, "data", "insights", "scenarios.json")
    n_frames = 0
    if os.path.exists(scen_path):
        for e in json.load(open(scen_path, encoding="utf-8")):
            frame = (e.get("frame") or "").strip()
            if not frame:
                continue
            n_frames += 1
            parts = frame_split.split(frame)
            shown = " ".join(parts[:2]) + (" " + " ".join(parts[2:]) if len(parts) > 2 else "")
            if re.sub(r"\s+", "", shown) != re.sub(r"\s+", "", frame):
                problems.append(f"scenario {e.get('id')}: the frame shown as lead and rest differs from the frame text")
    print(f"scenario frames: {n_frames} checked (lead plus rest equals the frame)")

    if "--emit" in sys.argv:
        json.dump(expected, open(sys.argv[sys.argv.index("--emit") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for n in notes:
        print("note: " + n)
    for p in problems:
        print("BROKEN " + p)
    print(f"\n{len(QUERIES)} queries, {sum(len(e['results']) for e in expected.values())} results checked, {len(problems)} broken joins")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
