#!/usr/bin/env python3
# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Profile the PSI catalog records and experimental tables.

Reads what scripts/fetch_psi.py downloaded and writes one JSON file that
describes the shape of the data: per-investigation metadata, file statistics
by folder and extension, and a column-by-column profile of every
experimental table (fill rate, inferred type, numeric range, examples).

Usage:
    python3 scripts/profile_tables.py [psi_dir] [out_json]
    defaults: data/psi  data/derived/data_profile.json
"""
import collections
import csv
import io
import json
import os
import re
import sys

NUM_RE = re.compile(r"^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$")


def read_table(path):
    raw = open(path, "rb").read().decode("utf-8-sig", "replace")
    rows = list(csv.reader(io.StringIO(raw)))
    rows = [[c.strip() for c in r] for r in rows]
    rows = [r for r in rows if any(r)]
    header, body = rows[0], rows[1:]
    width = len(header)
    body = [(r + [""] * width)[:width] for r in body]
    return header, body


def profile_column(name, values):
    filled = [v for v in values if v != ""]
    nums = [float(v) for v in filled if NUM_RE.match(v)]
    n_num = len(nums)
    if not filled:
        kind = "empty"
    elif n_num == len(filled):
        kind = "numeric"
    elif n_num == 0:
        kind = "text"
    else:
        kind = "mixed"
    counts = collections.Counter(filled)
    col = {
        "name": name,
        "filled": len(filled),
        "kind": kind,
        "numeric_count": n_num,
        "unique": len(counts),
        "examples": [v for v, _ in counts.most_common(5)],
    }
    if nums:
        col["min"] = min(nums)
        col["max"] = max(nums)
    non_numeric = [v for v in counts if not NUM_RE.match(v)]
    if kind == "mixed":
        col["non_numeric_examples"] = non_numeric[:6]
    return col


def file_stats(listing):
    by_folder = collections.defaultdict(lambda: {"bytes": 0, "files": 0})
    by_ext = collections.defaultdict(lambda: {"bytes": 0, "files": 0})

    def walk(node, top):
        for f in node.get("files") or []:
            if f.get("directory") or f.get("files"):
                walk(f, top)
            else:
                size = f.get("bytes_size") or 0
                ext = os.path.splitext(f.get("key", ""))[1].lower() or "(none)"
                for bucket, key in ((by_folder, top), (by_ext, ext)):
                    bucket[key]["bytes"] += size
                    bucket[key]["files"] += 1

    for top in listing.get("files", []):
        walk(top, top.get("displayName") or top.get("key"))
    return dict(by_folder), dict(by_ext)


def main():
    psi = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "psi")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        "data", "derived", "data_profile.json")
    manifest = json.load(open(os.path.join(psi, "manifest.json")))
    result = {"source": manifest["source"],
              "fetched_at": manifest["fetched_at"], "investigations": []}

    for item in manifest["investigations"]:
        acc = item["accession"]
        inv = json.load(open(os.path.join(psi, "catalog", f"{acc}.json")))
        listing = json.load(
            open(os.path.join(psi, "file_listings", f"{acc}.json")))
        by_folder, by_ext = file_stats(listing)
        pubs = inv.get("publications") or []
        entry = {
            "accession": acc,
            "acronym": inv.get("investigationAcronym", ""),
            "title": inv.get("title", ""),
            "doi": inv.get("doi", ""),
            "license": inv.get("licenseIdentifier", ""),
            "project_type": inv.get("projectType", ""),
            "sub_research_area": inv.get("subResearchArea", ""),
            "platform": inv.get("flightProgram", ""),
            "hardware": inv.get("experimentHardware", ""),
            "start": inv.get("investigationStartDate", ""),
            "end": inv.get("investigationEndDate", ""),
            "related": inv.get("related_glds", ""),
            "proposal_title": inv.get("proposalTitle", ""),
            "version": inv.get("version"),
            "release_date": inv.get("releaseDate", ""),
            "total_bytes": inv.get("totalFileSize", 0),
            "text_lengths": {k: len(inv.get(k, "") or "") for k in
                             ("objective", "approach", "hypothesis",
                              "researchImpacts")},
            "publications": len(pubs),
            "publications_with_doi": sum(1 for p in pubs if p.get("doi")),
            "files_by_folder": by_folder,
            "files_by_ext": by_ext,
            "tables": [],
        }
        for t in item["experimental_tables"]:
            if "error" in t:
                continue
            header, body = read_table(
                os.path.join(psi, "experimental_tables", t["file"]))
            cols = [profile_column(h, [r[i] for r in body])
                    for i, h in enumerate(header)]
            entry["tables"].append({
                "file": t["file"], "rows": len(body), "columns": cols,
                "sample_rows": body[:3],
            })
        result["investigations"].append(entry)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
    n_tables = sum(len(i["tables"]) for i in result["investigations"])
    n_cols = sum(len(t["columns"]) for i in result["investigations"]
                 for t in i["tables"])
    print(f"{len(result['investigations'])} investigations, "
          f"{n_tables} tables, {n_cols} columns -> {out}")


if __name__ == "__main__":
    main()
