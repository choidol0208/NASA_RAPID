#!/usr/bin/env python3
# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""What differs between NASA PSI today and the copy in this repository.

Read-only. Fetches the live PSI study list, the record and the file listing
of every Combustion Science investigation, and prints what differs from
data/psi/manifest.json and from the listings saved in
data/psi/file_listings/:

  - investigations that are new on PSI or no longer listed there
  - a changed record version, title, DOI or license
  - experimental tables that are new, removed, or listed with another size
  - files that are new, removed, or listed with another size or version

It never downloads a data file (it does not call the download endpoint) and
writes nothing, unless --save-report PATH is given (a JSON copy of what was
printed). It does not update the repository: run scripts/fetch_psi.py and
pipeline/raw_inventory.py --refresh for that.

Usage:
    python3 scripts/psi_whats_new.py
    python3 scripts/psi_whats_new.py --names 30
    python3 scripts/psi_whats_new.py --save-report /tmp/psi_diff.json

Source: NASA Physical Sciences Informatics (PSI), https://psi.nasa.gov/
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://psi.nasa.gov/geode-py/ws"
RESEARCH_AREA = "combustion science"
PAUSE_S = 0.4  # be polite to the public server

MANIFEST = os.path.join(ROOT, "data", "psi", "manifest.json")
LISTING_DIR = os.path.join(ROOT, "data", "psi", "file_listings")
TABLE_CATEGORY = "Experimental table"
RECORD_FIELDS = (("version", "version"), ("title", "title"),
                 ("doi", "doi"), ("license", "licenseIdentifier"))


def get_json(url, data=None, headers=None, timeout=120):
    """Same generic client as scripts/fetch_psi.py: no personal information."""
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def accession_number(acc):
    return int(acc.split("-")[1])


def live_accessions():
    url = (f"{BASE}/repo/search?source=psi&type=investigation"
           "&sort=Public%20Release%20Date&order=desc&size=500")
    hits = get_json(url)["hits"]["hits"]
    accs = [h["_source"]["Accession"] for h in hits
            if h["_source"].get("Research Area", "").lower() == RESEARCH_AREA]
    return sorted(accs, key=accession_number), len(hits)


def live_listing(acc, version):
    body = json.dumps({"folder": f"{acc}/", "fileType": "study",
                       "studyId": acc, "version": version,
                       "obfuscationcode": ""}).encode("utf-8")
    return get_json(f"{BASE}/files/v2", data=body,
                    headers={"Content-Type": "application/json"})


def file_rows(tree):
    """key -> {"category", "states": sorted [(version, bytes)]} of a listing."""
    out = {}
    stack = [(tree, None)]
    while stack:
        node, category = stack.pop()
        for child in node.get("files") or []:
            if not isinstance(child, dict):
                continue
            if ("displayName" in child or child.get("directory") is True
                    or str(child.get("key", "")).endswith("/")):
                stack.append((child, category or child.get("displayName")))
                continue
            size = child.get("bytes_size")
            if isinstance(size, float) and size.is_integer():
                size = int(size)
            row = out.setdefault(str(child.get("key", "")), {
                "category": category or child.get("sortingCategory"),
                "states": set()})
            row["states"].add((child.get("version"), size))
    for row in out.values():
        row["states"] = sorted(row["states"], key=repr)
    return out


def base_name(key):
    return key.rsplit("/", 1)[-1]


def compare_files(saved, live):
    new = sorted(k for k in live if k not in saved)
    removed = sorted(k for k in saved if k not in live)
    changed = []
    for key in sorted(k for k in live if k in saved):
        if live[key]["states"] != saved[key]["states"]:
            changed.append({
                "file": base_name(key),
                "saved_version_and_bytes": saved[key]["states"],
                "live_version_and_bytes": live[key]["states"]})

    def total(rows, keys):
        return sum(max((s[1] for s in rows[k]["states"]
                        if isinstance(s[1], int)), default=0) for k in keys)
    return {
        "files_saved": len(saved), "files_live": len(live),
        "new_files": [base_name(k) for k in new],
        "new_files_bytes": total(live, new),
        "removed_files": [base_name(k) for k in removed],
        "removed_files_bytes": total(saved, removed),
        "changed_files": changed,
    }


def compare_investigation(acc, entry):
    """Differences of one investigation; entry is its manifest row or None."""
    out = {"accession": acc, "differences": []}
    diff = out["differences"]
    record = get_json(f"{BASE}/repo/investigations/{acc}")
    out["acronym"] = record.get("investigationAcronym", "")
    if entry is None:
        diff.append("new investigation on PSI (not in data/psi/manifest.json)"
                    f": {record.get('title', '')}")
    else:
        for ours, theirs in RECORD_FIELDS:
            if entry.get(ours) != record.get(theirs, entry.get(ours)):
                diff.append(f"{ours} changed: manifest {entry.get(ours)!r}, "
                            f"PSI {record.get(theirs)!r}")
    time.sleep(PAUSE_S)
    live = file_rows(live_listing(acc, record.get("version", 1)))

    # experimental tables: the record's list and the listed sizes
    live_tables = {t["file_name"] for t in record.get("experimentalTable")
                   or [] if t.get("file_name")}
    listed_size = {base_name(k): max((s[1] for s in row["states"]
                                      if isinstance(s[1], int)), default=None)
                   for k, row in live.items()
                   if row["category"] == TABLE_CATEGORY}
    ours_tables = {t["file"]: t.get("bytes")
                   for t in (entry or {}).get("experimental_tables", [])}
    for name in sorted(live_tables - set(ours_tables)):
        diff.append(f"new experimental table: {name}")
    for name in sorted(set(ours_tables) - live_tables):
        diff.append(f"experimental table no longer in the record: {name}")
    for name in sorted(live_tables & set(ours_tables)):
        if (ours_tables[name] is not None and name in listed_size
                and listed_size[name] != ours_tables[name]):
            diff.append(f"experimental table size: {name}: manifest "
                        f"{ours_tables[name]} bytes, PSI lists "
                        f"{listed_size[name]} bytes")

    # files: against the saved listing
    path = os.path.join(LISTING_DIR, f"{acc}.json")
    if not os.path.exists(path):
        out["files"] = {"files_live": len(live), "saved_listing": "none"}
        diff.append(f"no saved listing to compare with ({len(live)} files "
                    "listed on PSI)")
        return out
    with open(path, encoding="utf-8") as fh:
        saved = file_rows(json.load(fh))
    files = compare_files(saved, live)
    out["files"] = files
    if files["new_files"]:
        diff.append(f"{len(files['new_files'])} new files "
                    f"({files['new_files_bytes']:,} bytes)")
    if files["removed_files"]:
        diff.append(f"{len(files['removed_files'])} files no longer listed "
                    f"({files['removed_files_bytes']:,} bytes)")
    if files["changed_files"]:
        diff.append(f"{len(files['changed_files'])} files with another size "
                    "or version")
    return out


def print_names(title, names, limit):
    if not names:
        return
    print(f"    {title}:")
    for name in names[:limit]:
        print(f"      {name}")
    if len(names) > limit:
        print(f"      ... and {len(names) - limit} more (--names N)")


def main():
    ap = argparse.ArgumentParser(
        description="Print what differs between live PSI and the copy in "
                    "this repository. Read-only; downloads no data file.")
    ap.add_argument("--names", type=int, default=10, metavar="N",
                    help="file names printed per group (default 10)")
    ap.add_argument("--save-report", metavar="PATH",
                    help="also write the comparison as JSON to PATH")
    args = ap.parse_args()

    with open(MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)
    ours = {r["accession"]: r for r in manifest["investigations"]}
    fetched = "not recorded"
    fetched_path = os.path.join(LISTING_DIR, "_fetched.json")
    if os.path.exists(fetched_path):
        with open(fetched_path, encoding="utf-8") as fh:
            fetched = json.load(fh).get("fetched_at", fetched)

    report = {"compared_at": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                           time.gmtime()),
              "manifest_fetched_at": manifest.get("fetched_at"),
              "listings_fetched_at": fetched,
              "investigations": [], "errors": []}
    try:
        accs, n_all = live_accessions()
    except (urllib.error.URLError, OSError, ValueError, KeyError) as exc:
        print(f"PSI study list not available: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return 2
    print(f"PSI lists {len(accs)} combustion investigations of {n_all}; "
          f"the manifest ({report['manifest_fetched_at']}) has {len(ours)}; "
          f"saved listings: {fetched}")
    gone = sorted(set(ours) - set(accs), key=accession_number)
    report["no_longer_listed"] = gone
    for acc in gone:
        print(f"{acc}: in the manifest, no longer in the PSI combustion list")

    with_diff = 0
    for acc in accs:
        time.sleep(PAUSE_S)
        try:
            res = compare_investigation(acc, ours.get(acc))
        except (urllib.error.URLError, OSError, ValueError, KeyError) as exc:
            reason = f"{type(exc).__name__}: {exc}"
            report["errors"].append({"accession": acc, "error": reason})
            print(f"{acc}: not available: {reason}")
            continue
        report["investigations"].append(res)
        if not res["differences"]:
            print(f"{acc}: no difference "
                  f"({res['files']['files_live']} file keys listed)")
            continue
        with_diff += 1
        print(f"{acc} ({res['acronym']}):")
        for line in res["differences"]:
            print(f"  - {line}")
        files = res.get("files", {})
        print_names("new", files.get("new_files", []), args.names)
        print_names("no longer listed", files.get("removed_files", []),
                    args.names)
        print_names("another size or version",
                    [f"{c['file']}: saved {c['saved_version_and_bytes']}, "
                     f"PSI {c['live_version_and_bytes']}"
                     for c in files.get("changed_files", [])], args.names)
    print(f"Compared {len(report['investigations'])} investigations: "
          f"{with_diff} with differences, {len(gone)} no longer listed, "
          f"{len(report['errors'])} not available. Nothing was written"
          + (f" except {args.save_report}." if args.save_report else "."))
    if args.save_report:
        with open(args.save_report, "w", encoding="utf-8",
                  newline="\n") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
