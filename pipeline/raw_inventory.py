#!/usr/bin/env python3
# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Raw-data inventory: what the NASA PSI archive lists for each investigation.

For every investigation of data/psi/manifest.json this script reads the PSI
file listing (file names, sizes and PSI categories) and writes
data/pipeline/raw_inventory.json: files and bytes per PSI category and per
kind of file (video, still image, archive, table, document, ...).

The kind is decided from the file name and the PSI category only, by the
rules of pipeline/spec/raw_kinds.json. No data file is downloaded or opened:
the only network call is the listing call POST {BASE}/files/v2, the same
public call scripts/fetch_psi.py uses. This file holds no knowledge of a
single investigation; every name rule is in the spec file.

Usage:
    python3 pipeline/raw_inventory.py             # offline if listings are saved
    python3 pipeline/raw_inventory.py --offline   # never touch the network
    python3 pipeline/raw_inventory.py --refresh   # fetch the 24 listings again

Source: NASA Physical Sciences Informatics (PSI), https://psi.nasa.gov/
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from decimal import ROUND_HALF_UP, Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://psi.nasa.gov/geode-py/ws"
PAUSE_S = 0.4  # be polite to the public server

MANIFEST = os.path.join(ROOT, "data", "psi", "manifest.json")
LISTING_DIR = os.path.join(ROOT, "data", "psi", "file_listings")
FETCHED = os.path.join(LISTING_DIR, "_fetched.json")
SPEC = os.path.join(ROOT, "pipeline", "spec", "raw_kinds.json")
OUT = os.path.join(ROOT, "data", "pipeline", "raw_inventory.json")

GENERATED_BY = "AI-generated (Claude Code), 2026-11-14. Not human-reviewed."


# ----------------------------------------------------------------- helpers

def accession_number(acc):
    return int(acc.split("-")[1])


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, indent=1) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def investigations():
    """The investigations of data/psi/manifest.json, in numeric order."""
    rows = load_json(MANIFEST)["investigations"]
    return sorted(rows, key=lambda r: accession_number(r["accession"]))


# ---------------------------------------------------------------- fetching

def fetch_listing(acc, version):
    """The file listing of one investigation: names and sizes, no data file.

    Same public call as scripts/fetch_psi.py (POST {BASE}/files/v2), with the
    same generic client: no cookie, no account, no personal information.
    """
    body = json.dumps({"folder": f"{acc}/", "fileType": "study",
                       "studyId": acc, "version": version,
                       "obfuscationcode": ""}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}/files/v2", data=body,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def refresh(invs):
    """Fetch every listing, save it unchanged, record the fetch once."""
    os.makedirs(LISTING_DIR, exist_ok=True)
    record = {
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": f"POST {BASE}/files/v2",
        "note": "File listings only (names and sizes). Saved as received.",
        "listings": {},
    }
    for inv in invs:
        acc = inv["accession"]
        version = inv.get("version") or 1
        path = os.path.join(LISTING_DIR, f"{acc}.json")
        time.sleep(PAUSE_S)
        try:
            raw = fetch_listing(acc, version)
            json.loads(raw.decode("utf-8"))  # must be JSON to be a listing
        except (urllib.error.URLError, OSError, ValueError) as exc:
            # A stale copy would be read as this fetch's listing: remove it.
            if os.path.exists(path):
                os.remove(path)
            reason = f"{type(exc).__name__}: {exc}"
            record["listings"][acc] = {"requested_version": version,
                                       "error": reason}
            print(acc, "listing failed:", reason, file=sys.stderr)
            continue
        with open(path, "wb") as fh:
            fh.write(raw)
        record["listings"][acc] = {
            "requested_version": version,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        print(acc, len(raw), "bytes")
    write_json(FETCHED, record)


# ------------------------------------------------------- reading a listing

def is_folder(node):
    return ("displayName" in node or node.get("directory") is True
            or str(node.get("key", "")).endswith("/"))


def walk(node, path, rows):
    """Collect (folder path, file record) for every file row of the tree."""
    for child in node.get("files") or []:
        if not isinstance(child, dict):
            continue
        if is_folder(child):
            walk(child, path + [str(child.get("displayName", ""))], rows)
        else:
            rows.append((path, child))


def size_of(record):
    """Bytes as an integer, or None when the listing gives no usable size."""
    value = record.get("bytes_size")
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    if isinstance(value, float) and value >= 0 and value.is_integer():
        return int(value)
    return None


def read_listing(path):
    """The files of a saved listing, each counted once.

    PSI listings repeat some rows (same file id, same folder); a repeated row
    is the same file and is counted once. Returns the files, the number of
    rows, the number of repeated rows and the bytes summed over all rows.
    """
    rows = []
    walk(load_json(path), [], rows)
    seen = set()
    files = []
    for folders, record in rows:
        key = str(record.get("key", ""))
        ident = record.get("id") or (key, record.get("version"))
        if ident in seen:
            continue
        seen.add(ident)
        category = (folders[0] if folders
                    else record.get("sortingCategory") or "(no category)")
        files.append({
            "name": key.rsplit("/", 1)[-1],
            "key": key,
            "category": category,
            "bytes": size_of(record),
        })
    rows_bytes = sum(size_of(record) or 0 for _, record in rows)
    return files, len(rows), len(rows) - len(files), rows_bytes


# ------------------------------------------------------------------- rules

class Rules:
    """The name rules of pipeline/spec/raw_kinds.json, compiled."""

    def __init__(self, spec):
        self.spec = spec
        self.kinds = [k["id"] for k in spec["kinds"]]
        self.default_kind = spec["default_kind"]
        self.rules = [self._compile(r) for r in spec["rules"]]
        content = spec["archive_content"]
        self.content_default = content["default"]
        self.content_rules = [self._compile(r) for r in content["rules"]]
        self.content_order = []
        for rule in content["rules"]:
            if rule["content"] not in self.content_order:
                self.content_order.append(rule["content"])
        self.content_order.append(self.content_default)
        ids = spec["test_id_patterns"]
        self.id_categories = ids["categories"]
        self.id_min_files = ids["min_files"]
        self.id_min_share = ids["min_share"]
        self.id_patterns = [dict(p, compiled=re.compile(p["regex"]))
                            for p in ids["patterns"]]
        for rule in self.rules:
            if rule["kind"] not in self.kinds:
                raise SystemExit(f"rule {rule['id']}: unknown kind")
        if self.default_kind not in self.kinds:
            raise SystemExit("default_kind is not a listed kind")

    @staticmethod
    def _compile(rule):
        out = dict(rule)
        if "name_pattern" in rule:
            out["compiled"] = re.compile(rule["name_pattern"])
        return out

    def split_name(self, name, category):
        """(stem without the PSI prefix and the last extension, extension)."""
        bare = name
        for template in self.spec["strip_prefix"]:
            pattern = template.replace("{category}", re.escape(category))
            stripped, n = re.subn(pattern, "", name, count=1)
            if n:
                bare = stripped
                break
        if "." in bare:
            stem, ext = bare.rsplit(".", 1)
            ext = ext.strip().lower()
            if ext:
                return stem, ext
        return bare, "(none)"

    @staticmethod
    def _holds(rule, category, ext, stem):
        if "categories" in rule and category not in rule["categories"]:
            return False
        if "extensions" in rule and ext not in rule["extensions"]:
            return False
        if "compiled" in rule and not rule["compiled"].search(stem):
            return False
        return True

    def classify(self, f):
        """(kind, rule id, extension, archive content or None) of a file."""
        stem, ext = self.split_name(f["name"], f["category"])
        kind, rule_id = self.default_kind, "(no rule: default)"
        for rule in self.rules:
            if self._holds(rule, f["category"], ext, stem):
                kind, rule_id = rule["kind"], rule["id"]
                break
        content = None
        if kind == "archive":
            content = self.content_default
            for rule in self.content_rules:
                if self._holds(rule, f["category"], ext, stem):
                    content = rule["content"]
                    break
        return kind, rule_id, ext, content, stem


# --------------------------------------------------------------- inventory

def tally(table, key, nbytes):
    cell = table.setdefault(key, {"files": 0, "bytes": 0})
    cell["files"] += 1
    cell["bytes"] += nbytes
    return cell


def fmt_count(n):
    return f"{n:,}"


def fmt_size(nbytes, wording):
    """One decimal, decimal units: GB from 10^9 bytes, MB below."""
    if nbytes >= 10 ** 9:
        unit, text = Decimal(10 ** 9), wording["size_gb"]
    else:
        unit, text = Decimal(10 ** 6), wording["size_mb"]
    value = (Decimal(nbytes) / unit).quantize(Decimal("0.1"),
                                              rounding=ROUND_HALF_UP)
    if value == 0 and nbytes > 0:
        return wording["size_tiny"]
    return text.format(value=f"{value:,}")


def test_ids(files, rules):
    """Name patterns carried by the files of the searched categories."""
    pool = sorted((f for f in files if f["category"] in rules.id_categories),
                  key=lambda f: f["name"])
    found = []
    for order, pattern in enumerate(rules.id_patterns):
        ids = set()
        matching = 0
        examples = []
        for f in pool:
            m = pattern["compiled"].search(f["stem"])
            if not m:
                continue
            matching += 1
            if m.group(0) not in ids and len(examples) < 3:
                examples.append(f["name"])
            ids.add(m.group(0))
        if (matching >= rules.id_min_files
                and matching >= rules.id_min_share * len(pool)):
            found.append((-matching, order, {
                "pattern_id": pattern["id"],
                "regex": pattern["regex"],
                "what_the_names_show": pattern["what_the_names_show"],
                "searched_categories": list(rules.id_categories),
                "files_searched": len(pool),
                "files_matching": matching,
                "distinct_ids": len(ids),
                "examples": examples,
            }))
    return [item for _, _, item in sorted(found, key=lambda t: t[:2])]


def sentence(entry, rules):
    """The fixed sentence of an entry, filled with the entry's own numbers."""
    w = rules.spec["sentence"]
    if entry["files"] == 0:
        return w["empty"].format(investigation_id=entry["investigation_id"])
    labels = {k["id"]: k for k in rules.spec["kinds"]}
    items = []
    for kind in rules.kinds:
        cell = entry["by_kind"].get(kind)
        if not cell:
            continue
        label = labels[kind]["one" if cell["files"] == 1 else "many"]
        fields = {"n": fmt_count(cell["files"]), "label": label,
                  "size": fmt_size(cell["bytes"], w)}
        if "archive_content" in cell:
            parts = []
            for content, sub in cell["archive_content"].items():
                shown = (w["archive_content_default_label"]
                         if content == rules.content_default else content)
                parts.append(w["archive_content_item"].format(
                    n=fmt_count(sub["files"]), content=shown))
            items.append(w["archive_item"].format(
                contents=w["separator"].join(parts), **fields))
        elif kind == rules.default_kind:
            # the extension with the most files; ties: alphabetical order
            ext, top = min(cell["extensions"].items(),
                           key=lambda kv: (-kv[1]["files"], kv[0]))
            items.append(w["other_item"].format(
                extension=ext, extension_n=fmt_count(top["files"]),
                **fields))
        else:
            items.append(w["kind_item"].format(**fields))
    no_sensor = ("" if "sensor_or_telemetry_table" in entry["by_kind"]
                 else w["no_sensor"])
    test_id = ""
    if entry["test_id_in_file_names"]:
        top = entry["test_id_in_file_names"][0]
        label = next(p["sentence_label"] for p in rules.id_patterns
                     if p["id"] == top["pattern_id"])
        test_id = w["test_id"].format(
            n=fmt_count(top["files_matching"]),
            m=fmt_count(top["files_searched"]),
            categories=" and ".join(top["searched_categories"]),
            label=label)
    files_text = w["files_one" if entry["files"] == 1 else "files_many"]
    return w["template"].format(
        files=files_text.format(n=fmt_count(entry["files"])),
        size=fmt_size(entry["bytes"], w),
        investigation_id=entry["investigation_id"],
        kinds=w["separator"].join(items),
        no_sensor=no_sensor, test_id=test_id)


def build_entry(inv, rules, fetch_record, rule_counts):
    acc = inv["accession"]
    entry = {
        "investigation_id": acc,
        "title": inv.get("title", ""),
        "acronym": inv.get("acronym", ""),
    }
    path = os.path.join(LISTING_DIR, f"{acc}.json")
    error = (fetch_record.get("listings", {}).get(acc) or {}).get("error")
    reason = None
    if error:
        reason = error
    elif not os.path.exists(path):
        reason = "no saved listing (run with --refresh)"
    else:
        try:
            files, rows, repeated, rows_bytes = read_listing(path)
        except (OSError, ValueError) as exc:
            reason = f"saved listing cannot be read ({type(exc).__name__})"
    if reason:
        entry["listing"] = f"not available: {reason}"
        entry["sentence"] = rules.spec["sentence"]["not_available"].format(
            investigation_id=acc)
        return entry

    by_category, by_kind = {}, {}
    without_size = 0
    for f in files:
        kind, rule_id, ext, content, stem = rules.classify(f)
        f["stem"] = stem
        nbytes = f["bytes"]
        if nbytes is None:
            without_size += 1
            nbytes = 0
        cat = tally(by_category, f["category"], nbytes)
        tally(cat.setdefault("by_kind", {}), kind, nbytes)
        cell = tally(by_kind, kind, nbytes)
        tally(cell.setdefault("extensions", {}), ext, nbytes)
        best = cell.get("_example")
        if best is None or (-nbytes, f["name"]) < (-best[0], best[1]):
            cell["_example"] = (nbytes, f["name"])
        if content is not None:
            tally(cell.setdefault("archive_content", {}), content, nbytes)
        tally(rule_counts, rule_id, nbytes)

    entry["listing"] = "ok"
    entry["files"] = len(files)
    entry["bytes"] = sum(f["bytes"] or 0 for f in files)
    entry["listing_rows"] = rows
    entry["repeated_rows"] = repeated
    entry["listing_rows_bytes"] = rows_bytes
    entry["records_beyond_one_per_key"] = (
        len(files) - len({f["key"] for f in files}))
    entry["files_without_size"] = without_size
    entry["by_category"] = {}
    for name in sorted(by_category):
        cat = by_category[name]
        entry["by_category"][name] = {
            "files": cat["files"], "bytes": cat["bytes"],
            "by_kind": {k: cat["by_kind"][k] for k in rules.kinds
                        if k in cat["by_kind"]},
        }
    entry["by_kind"] = {}
    for kind in rules.kinds:
        if kind not in by_kind:
            continue
        cell = by_kind[kind]
        out = {"files": cell["files"], "bytes": cell["bytes"],
               "extensions": {e: cell["extensions"][e]
                              for e in sorted(cell["extensions"])},
               "example": cell["_example"][1],
               "example_bytes": cell["_example"][0]}
        if "archive_content" in cell:
            out["archive_content"] = {
                c: cell["archive_content"][c] for c in rules.content_order
                if c in cell["archive_content"]}
        entry["by_kind"][kind] = out
    entry["test_id_in_file_names"] = test_ids(files, rules)
    entry["sentence"] = sentence(entry, rules)
    return entry


def build(invs):
    spec = load_json(SPEC)
    rules = Rules(spec)
    fetch_record = load_json(FETCHED) if os.path.exists(FETCHED) else {}
    rule_counts = {}
    entries = [build_entry(inv, rules, fetch_record, rule_counts)
               for inv in invs]
    ok = [e for e in entries if e["listing"] == "ok"]
    totals_by_kind = {}
    for kind in rules.kinds:
        cells = [e["by_kind"][kind] for e in ok if kind in e["by_kind"]]
        if cells:
            totals_by_kind[kind] = {
                "files": sum(c["files"] for c in cells),
                "bytes": sum(c["bytes"] for c in cells)}
    rule_order = [r["id"] for r in spec["rules"]] + ["(no rule: default)"]
    meta = {
        "generated_by": GENERATED_BY,
        "note": ("One entry per NASA PSI combustion investigation: what the "
                 "PSI file listing names, by PSI category and by kind of "
                 "file. Counts and sizes are computed by the team from the "
                 "listings; they are not NASA statements about the data."),
        "listings_fetched_at": fetch_record.get(
            "fetched_at", "not recorded"),
        "listings_source": (f"POST {BASE}/files/v2 (public file listing of "
                            "https://psi.nasa.gov/), saved unchanged in "
                            f"{rel(LISTING_DIR)}/"),
        "classification_rule": (
            "Kinds are decided from file names and PSI categories only, by "
            f"the ordered rules of {rel(SPEC)}. No file was opened or "
            "downloaded. A kind says what the name says, not what the file "
            "holds; a listing says nothing about the content or the quality "
            "of a file."),
        "counting_rule": (
            "A file is one record of the listing. PSI listings repeat some "
            "rows (same file id in the same folder); a repeated row is "
            "counted once ('listing_rows' minus 'repeated_rows' = 'files'; "
            "'listing_rows_bytes' is the sum over all rows, repeats "
            "included, for comparison). "
            "Where PSI lists several records under one storage key (other "
            "versions of a name) each record is counted; "
            "'records_beyond_one_per_key' says how many."),
        "units": ("'bytes' are integers as PSI reports them (bytes_size). "
                  "In 'sentence' sizes use decimal units with one decimal: "
                  "1 MB = 10^6 bytes, 1 GB = 10^9 bytes; GB from 10^9 bytes, "
                  "MB below."),
        "fields": {
            "listing": "'ok', or 'not available: <reason>' when the listing "
                       "call failed; such an entry has no counts.",
            "by_category": "The PSI category names exactly as the listing "
                           "gives them, each with files, bytes and the "
                           "kinds inside it.",
            "by_kind": "Files and bytes per kind over the whole listing, "
                       "the extensions inside the kind, and the name of "
                       "the largest file as 'example'. For archives, "
                       "'archive_content' counts what the names state.",
            "test_id_in_file_names": "Name patterns carried by the files of "
                                     "'searched_categories', with the "
                                     "number of names that match and three "
                                     "example names. Only what the names "
                                     "show; no name is mapped to a row of "
                                     "an experimental table. Empty when no "
                                     "pattern of the spec is carried.",
            "sentence": "One fixed sentence (template in the spec file) "
                        "filled only with numbers of the same entry.",
        },
        "totals": {
            "investigations": len(entries),
            "listings_available": len(ok),
            "files": sum(e["files"] for e in ok),
            "bytes": sum(e["bytes"] for e in ok),
            "listing_rows": sum(e["listing_rows"] for e in ok),
            "repeated_rows": sum(e["repeated_rows"] for e in ok),
            "listing_rows_bytes": sum(e["listing_rows_bytes"] for e in ok),
            "files_without_size": sum(e["files_without_size"] for e in ok),
            "by_kind": totals_by_kind,
            "by_rule": {r: rule_counts[r] for r in rule_order
                        if r in rule_counts},
        },
        "written_by": (f"{rel(os.path.abspath(__file__))} from "
                       f"{rel(LISTING_DIR)}/, {rel(MANIFEST)} and "
                       f"{rel(SPEC)}"),
    }
    return {"_meta": meta, "investigations": entries}


def main():
    ap = argparse.ArgumentParser(
        description="Raw-data inventory from the PSI file listings "
                    "(listings only; no data file is downloaded).")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true",
                      help="build from the saved listings; no network "
                           "(the default when listings are saved)")
    mode.add_argument("--refresh", action="store_true",
                      help="fetch the listings again, then build")
    args = ap.parse_args()

    invs = investigations()
    saved = os.path.exists(FETCHED) and any(
        os.path.exists(os.path.join(LISTING_DIR, f"{i['accession']}.json"))
        for i in invs)
    if args.refresh or (not args.offline and not saved):
        refresh(invs)
    inventory = build(invs)
    write_json(OUT, inventory)
    totals = inventory["_meta"]["totals"]
    print(f"{rel(OUT)}: {totals['investigations']} investigations, "
          f"{totals['listings_available']} listings, "
          f"{totals['files']:,} files, {totals['bytes']:,} bytes")


if __name__ == "__main__":
    main()
