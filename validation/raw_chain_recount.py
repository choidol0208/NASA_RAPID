# AI-generated code: written with an AI assistant (Claude Code), a second session independent of the pipeline, 2026-11-15. No language model runs when it runs.
"""Independent recount of the raw-data chain (build step 7 of docs/raw_data_design/design.md).

Written from the rules as they are written (docs/raw_data_design/design.md
sections 3, 7, 9, 10; docs/video_design/design.md sections 4 and 12;
pipeline/README.md "What is in the raw files"; the spec files under
pipeline/spec/). It imports nothing from pipeline/, video/, ai/, scripts/ or
scoring/: those files were read as text to learn the rules, never run.

Inputs of the counts (read only):
  data/psi/file_listings/<PSI-n>.json    PSI file listings (git-ignored)
  data/psi/raw_cache/PSI-69/test_sheets/  FLEX per-test sheets (git-ignored)
  data/psi/experimental_tables/*.csv     NASA experimental tables
  pipeline/spec/{scenarios,needs,raw_columns,sources,raw_kinds}.json
  data/pipeline/tests.csv                frozen per-test values
  data/pipeline/need_tests.csv           "counted" = objective_link 'stated'
Claimed side, only compared with (never an input of a count):
  data/pipeline/scenario_tests.csv, need_gap_states.csv, raw_inventory.json,
  question_chain.csv (if present), video/data/video_links.csv,
  the sha256 constants of pipeline/check.py (read as text).

Outputs: validation/raw_chain_recount.json and validation/raw_chain_recount_report.md.
Network: only with --fetch, and only the FLEX test sheets of PSI-69 that are
missing (the download scope approved by the team lead). Every call is
appended to validation/raw_chain_recount_netlog.jsonl; signed download links
are logged without their query string.

Usage:
  python -X utf8 -I validation/raw_chain_recount.py            # offline
  python -X utf8 -I validation/raw_chain_recount.py --fetch    # fetch missing sheets, then recount
"""
import argparse
import collections
import csv
import datetime
import decimal
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://psi.nasa.gov/geode-py/ws"
PAUSE_S = 0.6
TIMEOUT_S = 120
LISTING_DIR = os.path.join(ROOT, "data", "psi", "file_listings")
SHEET_DIR = os.path.join(ROOT, "data", "psi", "raw_cache", "PSI-69", "test_sheets")
TABLE_DIR = os.path.join(ROOT, "data", "psi", "experimental_tables")
SPEC_DIR = os.path.join(ROOT, "pipeline", "spec")
PIPE_DIR = os.path.join(ROOT, "data", "pipeline")
OUT_JSON = os.path.join(ROOT, "validation", "raw_chain_recount.json")
OUT_MD = os.path.join(ROOT, "validation", "raw_chain_recount_report.md")
NETLOG = os.path.join(ROOT, "validation", "raw_chain_recount_netlog.jsonl")
MANIFEST = os.path.join(ROOT, "data", "psi", "manifest.json")
CHECK_PY = os.path.join(ROOT, "pipeline", "check.py")
VIDEO_LINKS_CLAIMED = os.path.join(ROOT, "video", "data", "video_links.csv")
TEAM_LISTING_FETCHED = "2026-11-14T05:57:17Z"
SHEET_RE = re.compile(r"(?i)TestSheet\.txt$")
SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9 _.\-]+$")
D = decimal.Decimal


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def spec(name):
    return load_json(os.path.join(SPEC_DIR, name))


def sha256_of(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def fixture(block, what, expected, recounted):
    """One fixture row; 'match' is computed, never typed."""
    return {"block": block, "what": what, "expected": expected,
            "recounted": recounted, "match": expected == recounted}


# ======================================================================
# Network (only with --fetch; only FLEX test sheets of PSI-69)
# ======================================================================

def log_call(entry):
    entry["at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(NETLOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def http(url, log_url=None, purpose=""):
    req = urllib.request.Request(url)
    t0 = time.time()
    base = {"method": "GET", "url": log_url or url, "purpose": purpose, "bytes_sent": 0}
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            body = resp.read()
            status = resp.status
    except urllib.error.HTTPError as exc:
        log_call(dict(base, status=exc.code, bytes_received=0,
                      seconds=round(time.time() - t0, 2), error=str(exc)))
        raise
    except (urllib.error.URLError, OSError) as exc:
        log_call(dict(base, status=None, bytes_received=0,
                      seconds=round(time.time() - t0, 2), error=str(exc)))
        raise
    log_call(dict(base, status=status, bytes_received=len(body),
                  seconds=round(time.time() - t0, 2)))
    return body


def signed_link(text):
    """The download link in the reply of the download call."""
    text = text.strip()
    if text.startswith('"') or text.startswith("{"):
        value = json.loads(text)
        if isinstance(value, dict):
            for key in ("url", "link", "signedUrl", "signed_url"):
                if key in value:
                    return value[key]
            raise ValueError("no link in reply")
        return value
    return text


def fetch_sheets(sheet_files):
    """Download each missing FLEX test sheet (name from the PSI listing)."""
    os.makedirs(SHEET_DIR, exist_ok=True)
    done = 0
    for f in sheet_files:
        name = f["key_name"]
        if not SAFE_NAME_RE.match(name):
            print("skipped unsafe name", repr(name), file=sys.stderr)
            continue
        path = os.path.join(SHEET_DIR, name)
        if os.path.exists(path):
            continue
        q = urllib.parse.urlencode({"file": name, "version": f.get("version") or 1,
                                    "redirect": "false"})
        url = f"{BASE}/studies/PSI-69/download?{q}"
        time.sleep(PAUSE_S)
        reply = http(url, purpose=f"signed link {name}")
        link = signed_link(reply.decode("utf-8"))
        parts = urllib.parse.urlsplit(link)
        if parts.scheme != "https":
            raise SystemExit(f"refused link scheme for {name}")
        time.sleep(PAUSE_S)
        data = http(link, log_url=f"{parts.scheme}://{parts.netloc}{parts.path}",
                    purpose=f"download {name}")
        with open(path, "wb") as fh:
            fh.write(data)
        done += 1
    return done


def netlog_totals():
    if not os.path.exists(NETLOG):
        return {"calls": 0}
    calls = []
    with open(NETLOG, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                calls.append(json.loads(line))
    by = collections.defaultdict(lambda: {"calls": 0, "bytes_received": 0, "bytes_sent": 0})
    for c in calls:
        p = c.get("purpose", "")
        kind = ("listing (POST files/v2)" if p.startswith("listing")
                else "signed link (GET studies/PSI-69/download)" if p.startswith("signed link")
                else "sheet download (GET signed S3 link)" if p.startswith("download")
                else "other")
        by[kind]["calls"] += 1
        by[kind]["bytes_received"] += int(c.get("bytes_received") or 0)
        by[kind]["bytes_sent"] += int(c.get("bytes_sent") or 0)
    return {"calls": len(calls),
            "bytes_received": sum(int(c.get("bytes_received") or 0) for c in calls),
            "bytes_sent": sum(int(c.get("bytes_sent") or 0) for c in calls),
            "errors": sum(1 for c in calls if c.get("error") or c.get("status") != 200),
            "first_utc": min((c["at_utc"] for c in calls), default=None),
            "last_utc": max((c["at_utc"] for c in calls), default=None),
            "by_kind": dict(sorted(by.items())),
            "hosts": sorted({urllib.parse.urlsplit(c["url"]).netloc for c in calls})}


# ======================================================================
# Listings
# ======================================================================

def manifest_investigations():
    m = load_json(MANIFEST)
    out = [(i["accession"], i.get("version") or 1) for i in m["investigations"]]
    return sorted(out, key=lambda x: int(x[0].split("-")[1]))


def _is_folder(node):
    return ("displayName" in node or node.get("directory") is True
            or str(node.get("key", "")).endswith("/"))


def _walk(node, folders, rows):
    for child in node.get("files") or []:
        if not isinstance(child, dict):
            continue
        if _is_folder(child):
            _walk(child, folders + [str(child.get("displayName", ""))], rows)
        else:
            rows.append((folders, child))


def read_listing(acc):
    """Rows of the saved listing and the files counted once per file id."""
    path = os.path.join(LISTING_DIR, f"{acc}.json")
    with open(path, "rb") as fh:
        raw = fh.read()
    tree = json.loads(raw.decode("utf-8"))
    rows = []
    _walk(tree, [], rows)
    seen = set()
    files = []
    for folders, rec in rows:
        key = str(rec.get("key", ""))
        ident = rec.get("id") or (key, rec.get("version"))
        if ident in seen:
            continue
        seen.add(ident)
        size = rec.get("bytes_size")
        size = None if isinstance(size, bool) or not isinstance(size, (int, float)) else int(size)
        key_name = key.rsplit("/", 1)[-1]
        ext = key_name.rsplit(".", 1)[1].strip().lower() if "." in key_name else ""
        cat = folders[0] if folders else ""
        bare = re.sub(r"^PSI-\d+_" + re.escape(cat) + "_", "", key_name, count=1)
        if bare == key_name:
            bare = re.sub(r"^PSI-\d+_metadata_", "", key_name, count=1)
        stem = bare.rsplit(".", 1)[0] if "." in bare else bare
        files.append({"inv": acc, "id": rec.get("id"), "key": key, "key_name": key_name,
                      "bare": bare, "stem": stem, "ext": ext, "cat": cat,
                      "folders": folders, "sub": "/".join(folders[1:]),
                      "folder": "/".join(folders), "bytes": size,
                      "version": rec.get("version")})
    keys = collections.Counter(f["key"] for f in files)
    return {"files": files, "rows": len(rows),
            "rows_bytes": sum(int(r.get("bytes_size") or 0) for _, r in rows),
            "records_beyond_one_per_key": sum(v - 1 for v in keys.values() if v > 1),
            "sha256": hashlib.sha256(raw).hexdigest(), "raw_bytes": len(raw)}


# ======================================================================
# Tables and dates
# ======================================================================

def read_table(fname):
    """Rows of an experimental table as dicts, cells exactly as written but stripped.

    UTF-8 (byte-order mark removed) where the file is valid UTF-8, else
    cp1252 (only PSI-69 FLEX: its 0x96 bytes are en dashes). '_line' is the
    CSV record number with the header as 1 (no table has a blank record or a
    cell with a line break, so it equals the physical line).
    """
    with open(os.path.join(TABLE_DIR, fname), "rb") as fh:
        raw = fh.read()
    try:
        text, enc = raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        text, enc = raw.decode("cp1252"), "cp1252"
    text = text.lstrip("﻿")
    rows = list(csv.reader(io.StringIO(text)))
    header = [h.strip() for h in rows[0]]
    out = []
    for i, r in enumerate(rows[1:], start=2):
        if not any(c.strip() for c in r):
            continue
        d = {header[j]: (r[j].strip() if j < len(r) else "") for j in range(len(header))}
        d["_line"] = i
        d["_file"] = fname
        d["_enc"] = enc
        out.append(d)
    return out


MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def parse_date(s):
    """m/d/yyyy, m/d/yy, d-Mon-yy, yyyy-MON-dd, yyyy-mm-dd, 'Weekday, Month d, yyyy'."""
    s = s.strip()
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})", s)
    if m:
        mo, da, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
        yr = yr + 2000 if yr < 100 else yr
        try:
            return datetime.date(yr, mo, da)
        except ValueError:
            return None
    m = re.match(r"^(\d{1,2})-([A-Za-z]{3})[a-z]*-(\d{2,4})", s)
    if m:
        yr = int(m.group(3))
        yr = yr + 2000 if yr < 100 else yr
        mo = MONTHS.get(m.group(2).lower())
        try:
            return datetime.date(yr, mo, int(m.group(1))) if mo else None
        except ValueError:
            return None
    m = re.match(r"^(\d{4})-([A-Za-z]{3})[A-Za-z]*-(\d{1,2})", s)
    if m:
        mo = MONTHS.get(m.group(2).lower())
        try:
            return datetime.date(int(m.group(1)), mo, int(m.group(3))) if mo else None
        except ValueError:
            return None
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = re.match(r"^(?:[A-Za-z]+,\s*)?([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s)
    if m and MONTHS.get(m.group(1)[:3].lower()):
        try:
            return datetime.date(int(m.group(3)), MONTHS[m.group(1)[:3].lower()], int(m.group(2)))
        except ValueError:
            return None
    return None


def row_index(tests):
    """(table file, CSV line) -> test_id, from tests.csv source_file/source_row."""
    return {(t["source_file"], int(t["source_row"])): t["test_id"] for t in tests}


def row_index_check(tests, tables):
    """Does source_row point to the row whose identifier the test id carries? (PSI-10, 25, 39, 69, 159)."""
    out = collections.Counter()
    bad = []
    for t in tests:
        r = next((x for x in tables.get(t["source_file"], []) if x["_line"] == int(t["source_row"])), None)
        inv = t["investigation_id"]
        if r is None:
            out["row missing"] += 1
            bad.append(t["test_id"])
            continue
        want = {"PSI-69": lambda: "FLEX-" + r["FLEX Test #"], "PSI-25": lambda: "BASS2-" + r["Test #"],
                "PSI-39": lambda: "CFI-" + r["Flex Number"]}.get(inv)
        if inv in ("PSI-10", "PSI-159"):
            ok = t["test_id"].replace("-", "").upper().endswith(r["Test"].replace(" ", "").upper().replace("-", ""))
        elif want:
            ok = t["test_id"] == want()
        else:
            out["not checkable"] += 1
            continue
        out["consistent" if ok else "inconsistent"] += 1
        if not ok:
            bad.append(t["test_id"])
    return {"counts": dict(out), "inconsistent": bad[:20]}


# ======================================================================
# A. Placement per scenario (design.md 3.1), from tests.csv and scenarios.json
# ======================================================================

PLACEMENTS = ["inside", "cannot_be_placed_from_table", "oxygen_of_oxidizer_stream",
              "outside_by_recorded_value", "no_range_set"]


def in_range(v, r):
    lo, hi = r.get("min"), r.get("max")
    if lo is not None and v < lo:
        return False
    if hi is not None:
        return v <= hi if r.get("max_inclusive") else v < hi
    return True


def o2_match(t, rng):
    if "o2_pct" not in rng:
        return "not_specified"
    if t["o2_pct"] == "":
        return "not_recorded"
    if t["o2_basis"] == "oxidizer_stream":
        return "not_ambient"
    return "in" if in_range(float(t["o2_pct"]), rng["o2_pct"]) else "out"


def p_match(t, rng):
    if "pressure_kpa" not in rng:
        return "not_specified"
    if t["pressure_kpa"] == "":
        return "not_recorded"
    return "in" if in_range(float(t["pressure_kpa"]), rng["pressure_kpa"]) else "out"


def place(om, pm, precedence="outside_first"):
    """The placement of design.md 3.1 from the two matches.

    Order (this file's reading of the written list): no range set; inside
    (both in); outside (either recorded outside); oxidizer stream; otherwise
    cannot be placed. With precedence 'oxidizer_first' an oxidizer-stream test
    is never 'outside' (computed only to show the effect of the choice).
    """
    if om == "not_specified" and pm == "not_specified":
        return "no_range_set"
    if om == "in" and pm == "in":
        return "inside"
    if precedence == "oxidizer_first" and om == "not_ambient":
        return "oxygen_of_oxidizer_stream"
    if om == "out" or pm == "out":
        return "outside_by_recorded_value"
    if om == "not_ambient":
        return "oxygen_of_oxidizer_stream"
    return "cannot_be_placed_from_table"


def recount_placement(tests, scenarios, claimed_rows):
    out = {}
    per_test = {}
    for sc in scenarios:
        sid, rng = sc["id"], sc.get("ranges") or {}
        counts, solid, alt = collections.Counter(), collections.Counter(), collections.Counter()
        pairs, solid_pairs = collections.Counter(), collections.Counter()
        by_inv_inside, by_inv_cannot = collections.Counter(), collections.Counter()
        for t in tests:
            om, pm = o2_match(t, rng), p_match(t, rng)
            pl = place(om, pm)
            per_test[(sid, t["test_id"])] = (om, pm, pl)
            counts[pl] += 1
            alt[place(om, pm, "oxidizer_first")] += 1
            if pl == "cannot_be_placed_from_table":
                pairs[f"o2 {om}, pressure {pm}"] += 1
                by_inv_cannot[t["investigation_id"]] += 1
            if pl == "inside":
                by_inv_inside[t["investigation_id"]] += 1
            if t["fuel_phase"] == "solid":
                solid[pl] += 1
                solid_pairs[f"o2 {om}, pressure {pm}"] += 1
        srt = lambda c: dict(sorted(c.items(), key=lambda x: (-x[1], x[0])))
        out[sid] = {"all": {p: counts.get(p, 0) for p in PLACEMENTS},
                    "solid": {p: solid.get(p, 0) for p in PLACEMENTS},
                    "cannot_be_placed_pairs": dict(sorted(pairs.items())),
                    "cannot_be_placed_by_investigation": srt(by_inv_cannot),
                    "solid_match_pairs": dict(sorted(solid_pairs.items())),
                    "inside_by_investigation": srt(by_inv_inside),
                    "all_if_oxidizer_stream_took_precedence": {p: alt.get(p, 0) for p in PLACEMENTS}}
    disagreements, seen = [], 0
    claimed_keys = set()
    for r in claimed_rows:
        k = (r["scenario_id"], r["test_id"])
        claimed_keys.add(k)
        if k not in per_test:
            disagreements.append({"scenario": k[0], "test": k[1], "reason": "test not in tests.csv"})
            continue
        seen += 1
        om, pm, _ = per_test[k]
        if om != r["o2_match"] or pm != r["pressure_match"]:
            disagreements.append({"scenario": k[0], "test": k[1], "recount": [om, pm],
                                  "claimed": [r["o2_match"], r["pressure_match"]]})
    missing = [k for k in per_test if k not in claimed_keys]
    return out, per_test, {"rows_compared": seen, "disagreements": disagreements,
                           "pairs_not_in_claimed_file": len(missing)}


# ======================================================================
# B. States per need and variable (README "State rule", "Per need"),
#    recomputed from tests.csv, needs.json, raw_columns.json, sources.json
# ======================================================================

def recount_states(tests, needs, raw_columns, sources, need_tests):
    entries = collections.defaultdict(list)  # (inv, var) -> column_is list in spec order
    for inv in raw_columns["investigations"]:
        for e in inv.get("entries", []):
            entries[(e["investigation_id"], e["standard_variable"])].append(e["column_is"])
    documented = set()
    for s in sources["sources"]:
        for d in s.get("documented_elsewhere") or []:
            documented.add((s["investigation_id"], d["variable"]))
    counted = collections.defaultdict(set)
    for r in need_tests:
        if r["objective_link"] == "stated":
            counted[r["need_id"]].add(r["test_id"])
    result = {}
    for need in needs["needs"]:
        phases = (need.get("scope") or {}).get("fuel_phase")
        scope = [t for t in tests if not phases or t["fuel_phase"] in phases]
        roles = [("required", v) for v in need["conditions_required"]] + \
                [("outcome", v) for v in need["outcomes_any"]]
        for role, var in roles:
            cells, cells_counted = collections.Counter(), collections.Counter()
            for t in scope:
                if t.get(var, "") != "":
                    key = ("in_table", "")
                else:
                    kinds = entries.get((t["investigation_id"], var))
                    if kinds:
                        key = ("column_in_sampled_raw_file", "+".join(sorted(set(kinds))))
                    elif (t["investigation_id"], var) in documented:
                        key = ("documented_only", "")
                    else:
                        key = ("not_in_sampled_files", "")
                cells[key] += 1
                if t["test_id"] in counted[need["id"]]:
                    cells_counted[key] += 1
            result[(need["id"], role, var)] = {
                "in_scope": len(scope), "counted": len(counted[need["id"]]),
                "states": {f"{a}|{b}": [n, cells_counted.get((a, b), 0)]
                           for (a, b), n in sorted(cells.items())}}
    return result


def compare_states(mine, claimed_rows, scenario_ids):
    """Sum check of need_gap_states.csv and row-by-row comparison with the recount."""
    sums, diffs = [], []
    by_key = collections.defaultdict(dict)
    for r in claimed_rows:
        kinds = "+".join(sorted(r["column_is"].split("+"))) if r["column_is"] else ""
        k = (r["scenario_id"], r["need_id"], r["role"], r["variable"])
        by_key[k][f"{r['state']}|{kinds}"] = [int(r["in_scope_tests_in_state"]),
                                               int(r["counted_tests_in_state"])]
        by_key[k]["_in_scope"] = int(r["in_scope_tests"])
        by_key[k]["_counted"] = int(r["counted_tests"])
    for k, states in sorted(by_key.items()):
        total = sum(v[0] for s, v in states.items() if not s.startswith("_"))
        tot_c = sum(v[1] for s, v in states.items() if not s.startswith("_"))
        sums.append({"key": list(k), "sum_in_scope_over_states": total,
                     "in_scope": states["_in_scope"], "ok": total == states["_in_scope"],
                     "sum_counted_over_states": tot_c, "counted": states["_counted"],
                     "ok_counted": tot_c == states["_counted"]})
        m = mine.get(k[1:])
        if m is None:
            diffs.append({"key": list(k), "reason": "not in the recount"})
            continue
        claimed_states = {s: v for s, v in states.items() if not s.startswith("_")}
        if claimed_states != m["states"] or states["_in_scope"] != m["in_scope"] \
                or states["_counted"] != m["counted"]:
            diffs.append({"key": list(k), "claimed": claimed_states, "recount": m["states"]})
    missing = [list((s,) + k) for s in scenario_ids for k in mine if (s,) + k not in by_key]
    return {"rows_claimed": len(claimed_rows), "keys_claimed": len(by_key),
            "scenarios_in_claimed_file": sorted({k[0] for k in by_key}),
            "sum_failures": [s for s in sums if not (s["ok"] and s["ok_counted"])],
            "keys_summed": len(sums), "differences": diffs, "keys_missing_in_claimed": missing}


def state_short(states):
    """Fold the states of one (need, role, variable) into the design's words."""
    out = collections.Counter()
    for k, (n, _) in states.items():
        out[k.split("|")[0]] += n
    return dict(out)


# ======================================================================
# C. Files that name the tests inside the lunar ranges (design.md 3.1 link 4, 7, 10)
# ======================================================================

FLEX_NUM_RE = re.compile(r"(?i)(?<![A-Za-z0-9])FLEX[-_ ]?(\d{3})(?!\d)")
# identifier shapes of the FLEX table's "FLEX Identifier" column (all 273: ddd[F|R]ddd, ddCALdd, [C|H|N]dd[H|M]ddd)
FLEX_ID_SHAPE = r"\d{3}[FR]\d{3}|\d{2}CAL\d{2}|[CHN]\d{2}[HM]\d{3}"
FLEX_ID_RE = re.compile(r"(?<![A-Za-z0-9])(" + FLEX_ID_SHAPE + r")(?:[A-Da-d])?(?![A-Za-z0-9])")
CFIG_TP_RE = re.compile(r"(?<!\d)(\d{5}) ?([A-Z])(\d{1,2})(_\d)?(?!\d)")


def cfig_tp(m, known):
    """A CFI-G test point; with its '_n' suffix where the table lists that form as a test."""
    base = "".join(m.groups()[:3])
    return base + m.group(4) if m.group(4) and (base + m.group(4)) in known else base


def kind_exts(raw_kinds):
    rules = {r["id"]: r for r in raw_kinds["rules"]}
    return (set(rules["video_by_extension"]["extensions"]),
            set(rules["archive_by_extension"]["extensions"]))


def flex_rows(tables):
    rows = tables["PSI-69_Experimental table_FLEX.csv"]
    num2id = {int(r["FLEX Test #"]): r["FLEX Identifier"] for r in rows}
    id2nums = collections.defaultdict(list)
    for r in rows:
        id2nums[r["FLEX Identifier"]].append(int(r["FLEX Test #"]))
    return rows, num2id, id2nums


def flex_labels(f, num2id, id2nums):
    """The four labels of a PSI-69 file, each with the table test numbers it points to."""
    lab = {}
    m = FLEX_NUM_RE.search(f["bare"])
    if m:
        n = int(m.group(1))
        lab["name_number"] = (n, {n} if n in num2id else set())
    for m in FLEX_ID_RE.finditer(f["bare"]):
        lab["name_identifier"] = (m.group(1), set(id2nums.get(m.group(1), [])))
        break
    m = FLEX_NUM_RE.search(f["sub"])
    if m:
        n = int(m.group(1))
        lab["folder_number"] = (n, {n} if n in num2id else set())
    for m in FLEX_ID_RE.finditer(f["sub"]):
        lab["folder_identifier"] = (m.group(1), set(id2nums.get(m.group(1), [])))
        break
    return lab


def two_label_state(lab):
    """confirmed: two or more labels, all pointing to the same single row."""
    if not lab:
        return "no_label"
    sets = [v[1] for v in lab.values()]
    if any(not s for s in sets):
        return "a_label_names_no_table_row" if len(lab) > 1 else "id_not_in_table"
    inter = set.intersection(*sets)
    if len(lab) == 1:
        return "one_label" if len(sets[0]) == 1 else "one_label_several_rows"
    if len(inter) == 1 and all(len(s) == 1 for s in sets):
        return "two_or_more_labels_agree"
    return "labels_disagree"


def recount_links(listings, tables, tests, per_test, raw_kinds):
    vid_ext, arc_ext = kind_exts(raw_kinds)
    big = vid_ext | arc_ext
    t_by_id = {t["test_id"]: t for t in tests}
    inside = sorted(tid for (sid, tid), v in per_test.items()
                    if sid == "lunar_habitat" and v[2] == "inside")
    by_inv = collections.Counter(t_by_id[t]["investigation_id"] for t in inside)
    flex_tab, num2id, id2nums = flex_rows(tables)
    line2row = {(r["_file"], r["_line"]): r for rows in tables.values() for r in rows}

    # --- FLEX (PSI-69) ---
    lunar_flex = {}
    for tid in inside:
        t = t_by_id[tid]
        if t["investigation_id"] == "PSI-69":
            r = line2row[(t["source_file"], int(t["source_row"]))]
            lunar_flex[int(r["FLEX Test #"])] = {"test_id": tid, "identifier": r["FLEX Identifier"]}
    flex_files = []
    for f in listings["PSI-69"]["files"]:
        lab = flex_labels(f, num2id, id2nums)
        named = set()
        if "name_number" in lab and lab["name_number"][0] in lunar_flex:
            named.add(lab["name_number"][0])
        if "name_identifier" in lab:
            for n in lab["name_identifier"][1]:
                if n in lunar_flex:
                    named.add(n)
        if not named:
            continue
        test = min(named)
        folder_points = set()
        has_folder_label = False
        for k in ("folder_number", "folder_identifier"):
            if k in lab:
                has_folder_label = True
                folder_points |= lab[k][1] if lab[k][1] else {("not in table", lab[k][0])}
        if not has_folder_label:
            second = "folder_names_no_test"
        elif folder_points == {test}:
            second = "folder_agrees"
        else:
            second = "folder_names_another_test"
        by_name = "+".join(k for k in ("name_number", "name_identifier") if k in lab)
        flex_files.append({"test": test, "test_id": lunar_flex[test]["test_id"],
                           "name": f["bare"], "folder": f["sub"], "bytes": f["bytes"],
                           "ext": f["ext"], "big": f["ext"] in big, "second_label": second,
                           "name_labels": by_name, "several_tests_named": len(named) > 1,
                           "two_label_state": two_label_state(lab),
                           "labels": {k: v[0] for k, v in lab.items()}})

    def summary(rows):
        return {"files": len(rows), "bytes": sum(r["bytes"] for r in rows),
                "archive_or_video": {"files": sum(r["big"] for r in rows),
                                     "bytes": sum(r["bytes"] for r in rows if r["big"])},
                "other": {"files": sum(not r["big"] for r in rows),
                          "bytes": sum(r["bytes"] for r in rows if not r["big"])},
                "second_label": dict(sorted(collections.Counter(r["second_label"] for r in rows).items()))}

    flex_sum = summary(flex_files)
    flex_sum["zip"] = {"files": sum(1 for r in flex_files if r["ext"] == "zip"),
                       "bytes": sum(r["bytes"] for r in flex_files if r["ext"] == "zip")}
    flex_sum["by_extension"] = dict(sorted(collections.Counter("." + r["ext"] for r in flex_files).items()))
    flex_sum["by_name_label"] = dict(sorted(collections.Counter(r["name_labels"] for r in flex_files).items()))
    flex_sum["by_two_label_state"] = dict(sorted(collections.Counter(r["two_label_state"] for r in flex_files).items()))
    flex_sum["linked_by_name_number_alone"] = sum(
        1 for r in flex_files if r["name_labels"] == "name_number" and r["two_label_state"] == "one_label")
    flex_sum["files_naming_two_tests"] = sum(r["several_tests_named"] for r in flex_files)
    flex_sum["per_test"] = {f"FLEX-{n}": {"identifier": lunar_flex[n]["identifier"],
                                          "files": sum(1 for r in flex_files if r["test"] == n),
                                          "bytes": sum(r["bytes"] for r in flex_files if r["test"] == n),
                                          "zip": sum(1 for r in flex_files if r["test"] == n and r["ext"] == "zip")}
                            for n in sorted(lunar_flex)}
    flex_sum["folder_names_another_test"] = [
        {"test": f"FLEX-{r['test']}", "name": r["name"], "folder": r["folder"]}
        for r in flex_files if r["second_label"] == "folder_names_another_test"]

    # --- CFI-G (PSI-159) ---
    lunar_cfig = {}
    for tid in inside:
        t = t_by_id[tid]
        if t["investigation_id"] == "PSI-159":
            r = line2row[(t["source_file"], int(t["source_row"]))]
            lunar_cfig[r["Test"].replace(" ", "").upper()] = tid
    cfig_known = {r["Test"].replace(" ", "").upper() for fn, rows in tables.items()
                  if fn.startswith("PSI-159_") for r in rows}
    cfig_files = []
    for f in listings["PSI-159"]["files"]:
        tps = [cfig_tp(m, cfig_known) for m in CFIG_TP_RE.finditer(f["bare"])]
        named = [tp for tp in tps if tp in lunar_cfig]
        if not named:
            continue
        tp = named[0]
        ftps = {cfig_tp(m, cfig_known) for m in CFIG_TP_RE.finditer(f["sub"])}
        second = ("folder_names_no_test" if not ftps else
                  "folder_agrees" if ftps == {tp} else "folder_names_another_test")
        cfig_files.append({"test": tp, "test_id": lunar_cfig[tp], "name": f["bare"],
                           "folder": f["sub"], "bytes": f["bytes"], "ext": f["ext"],
                           "big": f["ext"] in big, "second_label": second,
                           "several_tests_named": len(set(named)) > 1})
    cfig_sum = summary(cfig_files)
    cfig_sum["by_extension"] = dict(sorted(collections.Counter("." + r["ext"] for r in cfig_files).items()))
    cfig_sum["per_test"] = {lunar_cfig[k]: sum(1 for r in cfig_files if r["test"] == k)
                            for k in sorted(lunar_cfig)}
    all_rows = flex_files + cfig_files
    total = summary(all_rows)
    archive_total = sum(f["bytes"] for L in listings.values() for f in L["files"])
    total["share_of_archive_bytes_pct"] = round(100.0 * total["bytes"] / archive_total, 4)

    # --- FLEX-specific fixtures ---
    sheets = [f for f in listings["PSI-69"]["files"] if SHEET_RE.search(f["key_name"])]
    sheet_nums = []
    for f in sheets:
        m = FLEX_NUM_RE.search(f["bare"])
        sheet_nums.append(int(m.group(1)) if m else None)
    max_row = max(num2id)
    flex19 = [r for r in flex_files if r["test"] == 19]
    return {
        "inside_tests": {"all": len(inside), "by_investigation": dict(sorted(by_inv.items()))},
        "flex_17": flex_sum, "cfig_9": cfig_sum, "lunar_26": total,
        "flex_table": {"rows": len(flex_tab), "distinct_identifiers": len(id2nums),
                       "identifiers_on_several_rows": {k: v for k, v in id2nums.items() if len(v) > 1},
                       "lines_of_repeated_identifiers": {k: [r["_line"] for r in flex_tab if r["FLEX Identifier"] == k]
                                                          for k, v in id2nums.items() if len(v) > 1},
                       "max_test_number": max_row},
        "flex_sheets_in_listing": {"files": len(sheets), "bytes": sum(f["bytes"] for f in sheets),
                                   "numbered_above_table": sorted(n for n in sheet_nums if n and n > max_row),
                                   "without_number": sum(1 for n in sheet_nums if n is None)},
        "flex_19": {"files": len(flex19), "bytes": sum(r["bytes"] for r in flex19),
                    "small": {"files": sum(not r["big"] for r in flex19),
                              "bytes": sum(r["bytes"] for r in flex19 if not r["big"])},
                    "archives": sorted((r["name"], r["bytes"]) for r in flex19 if r["big"])},
    }, flex_files, cfig_files


# ======================================================================
# D. FLEX test sheets against the FLEX table (design.md 3.4, 7)
# ======================================================================

def parse_sheet(text):
    """'key = value' and 'key: value' lines above COMMENTS:, values exactly as written (stripped)."""
    lines = text.splitlines()
    head = lines[0].strip() if lines else ""
    fields, seps = {}, {}
    comment = []
    in_comment = False
    for ln in lines[1:]:
        if in_comment:
            comment.append(ln)
            continue
        if re.match(r"^\s*COMMENTS\s*:", ln):
            in_comment = True
            continue
        m = re.match(r"^\s*([^=:]+?)\s*(=|:)\s*(.*?)\s*$", ln)
        if m and m.group(1).strip():
            key = re.sub(r"\s+", " ", m.group(1).strip())
            if key not in fields:
                fields[key] = m.group(3)
                seps[key] = m.group(2)
    return {"head": head, "fields": fields, "separators": seps,
            "comment_chars": len("\n".join(comment).strip())}


def num(s):
    """Decimal of a cell or sheet value written as a plain number, else None."""
    s = (s or "").strip()
    if re.fullmatch(r"[+-]?(\d+\.?\d*|\.\d+)", s):
        return D(s)
    return None


def table_dext_class(cell):
    c = cell.strip()
    if c == "":
        return "blank"
    if c in ("–", "-", "—"):
        return "dash"
    v = num(c)
    if v is None:
        return "other text"
    return "0" if v == 0 else "number above zero"


def sheet_dext_class(val, table_cell):
    v = (val or "").strip()
    if v.lower() == "nan":
        return "nan"
    n = num(v)
    if n is None:
        return "other text" if v else "missing"
    if n == 0:
        return v  # written zero, e.g. '0.00'
    t = num(table_cell)
    if t is not None and t > 0:
        return "the same number" if t == n else "a different number"
    return "a number"


def within_rounding(sheet_atm, table_mmhg):
    """Table mmHg / 760 within half a unit of the last written digit of the sheet's atm."""
    s, t = num(sheet_atm), num(table_mmhg)
    if s is None or t is None:
        return None
    places = -s.as_tuple().exponent
    tol = D(5) * D(10) ** (-(places + 1))
    return abs(t / D(760) - s) <= tol


SHEET_TABLE_PAIRS = [  # (sheet key, table column, compare)
    ("O2 Mole Fraction", "O initial ambient composition; mole fraction", "number"),
    ("N2 Mole Fraction", "N initial ambient composition; mole fraction", "number"),
    ("CO2 Mole Fraction", "CO initial ambient composition; mole fraction", "number"),
    ("He Mole Fraction", "He initial ambient composition; mole fraction", "number"),
    ("D0 (mm)", "Droplet initial diameter; mm", "number"),
    ("kavg (mm2/s)", "Burning rate; mm", "number"),
    ("Dext (mm)", "Visible flame extinction diameter; mm", "number"),
    ("Fuel", "Fuel", "text"),
]


FIELD_SOURCES = {"pressure": ("Pressure (atm)", "Ambient pressure; mmHg"), "date": ("Test Date", "Test Date"),
                 "time": ("Test Time", "Test GMT"), **{sk: (sk, tc) for sk, tc, _ in SHEET_TABLE_PAIRS}}


def hms(s):
    """(h, m, s) of a clock time as written ('05:02:52 (GMT)' and '5:02:52' are the same time)."""
    m = re.search(r"(\d{1,2}):(\d{2}):(\d{2})", s or "")
    return tuple(int(x) for x in m.groups()) if m else None


def field_values(rec, field):
    """[sheet value, table cell] exactly as written, for one compared field of a tied sheet."""
    if field == "name_number_equals_table_test_number":
        return [rec["name_number"], rec.get("table_row")]
    sk, tc = FIELD_SOURCES[field]
    return [rec["fields_as_written"].get(sk), rec.get("table_as_written", {}).get(tc)]


def recount_sheets(listings, tables, lunar_flex_numbers):
    flex_tab, num2id, id2nums = flex_rows(tables)
    by_id = collections.defaultdict(list)
    for r in flex_tab:
        by_id[r["FLEX Identifier"].upper()].append(r)
    sheets = [f for f in listings["PSI-69"]["files"] if SHEET_RE.search(f["key_name"])]
    records, missing = [], []
    for f in sorted(sheets, key=lambda x: x["key_name"]):
        path = os.path.join(SHEET_DIR, f["key_name"])
        if not os.path.exists(path):
            missing.append(f["key_name"])
            continue
        with open(path, "rb") as fh:
            raw = fh.read()
        try:
            text, enc = raw.decode("utf-8"), "utf-8"
        except UnicodeDecodeError:
            text, enc = raw.decode("cp1252"), "cp1252"
        p = parse_sheet(text)
        fl = p["fields"]
        m = FLEX_NUM_RE.search(f["bare"])
        name_num = int(m.group(1)) if m else None
        ident = fl.get("CIR Test Number", "")
        cands = by_id.get(ident.strip().upper(), [])
        sdate = parse_date(fl.get("Test Date", ""))
        tied, tie_by = [], None
        if cands:
            tied = [r for r in cands if sdate and parse_date(r["Test Date"]) == sdate]
            tie_by = "identifier + date" if tied else None
            if not tied:
                tied = [r for r in cands
                        if num(fl.get("O2 Mole Fraction")) is not None
                        and num(fl.get("O2 Mole Fraction")) == num(r["O initial ambient composition; mole fraction"])
                        and within_rounding(fl.get("Pressure (atm)"), r["Ambient pressure; mmHg"])]
                tie_by = "identifier + oxygen and pressure" if tied else None
        rec = {"file": f["key_name"], "listing_bytes": f["bytes"], "disk_bytes": len(raw),
               "encoding": enc, "head": p["head"], "name_number": name_num,
               "identifier_inside": ident, "fields_as_written": fl,
               "identifier_rows_in_table": [int(r["FLEX Test #"]) for r in cands],
               "tied_rows": [int(r["FLEX Test #"]) for r in tied], "tie_by": tie_by}
        if len(tied) == 1:
            r = tied[0]
            rec["table_row"] = int(r["FLEX Test #"])
            rec["table_line"] = r["_line"]
            cmp = {}
            cmp["name_number_equals_table_test_number"] = (name_num == int(r["FLEX Test #"]))
            cmp["date"] = sdate == parse_date(r["Test Date"])
            st_hms = hms(fl.get("Test Time", ""))
            cmp["time"] = None if st_hms is None else st_hms == hms(r["Test GMT"])
            cmp["pressure"] = within_rounding(fl.get("Pressure (atm)"), r["Ambient pressure; mmHg"])
            for sk, tc, how in SHEET_TABLE_PAIRS:
                sv, tv = fl.get(sk), r.get(tc, "")
                if how == "text":
                    cmp[sk] = None if sv is None else sv.strip().lower() == tv.strip().lower()
                else:
                    a, b = num(sv), num(tv)
                    cmp[sk] = None if a is None or b is None else a == b
            rec["agree"] = cmp
            rec["table_as_written"] = {"Ambient pressure; mmHg": r["Ambient pressure; mmHg"],
                                       "FLEX Identifier": r["FLEX Identifier"],
                                       "Test Date": r["Test Date"], "Test GMT": r["Test GMT"],
                                       **{tc: r.get(tc, "") for _, tc, _ in SHEET_TABLE_PAIRS}}
            tcell = r["Visible flame extinction diameter; mm"]
            rec["dext"] = {"table_cell": tcell, "table_class": table_dext_class(tcell),
                           "sheet_value": fl.get("Dext (mm)"),
                           "sheet_class": sheet_dext_class(fl.get("Dext (mm)"), tcell)}
        records.append(rec)

    def tally(recs):
        out = {"sheets": len(recs), "bytes": sum(r["listing_bytes"] for r in recs),
               "tied_to_one_row": sum(1 for r in recs if "table_row" in r),
               "tie_by": dict(collections.Counter(r["tie_by"] for r in recs if "table_row" in r)),
               "identifier_not_in_table": sum(1 for r in recs if not r["identifier_rows_in_table"]),
               "identifier_on_several_rows": sum(1 for r in recs if len(r["identifier_rows_in_table"]) > 1),
               "disk_bytes_equal_listing": sum(1 for r in recs if r["disk_bytes"] == r["listing_bytes"])}
        agree = collections.defaultdict(collections.Counter)
        for r in recs:
            for k, v in (r.get("agree") or {}).items():
                agree[k]["agree" if v is True else "differ" if v is False else "not comparable"] += 1
        out["field_agreement"] = {k: dict(v) for k, v in agree.items()}
        cross = collections.defaultdict(list)
        for r in recs:
            if "dext" in r:
                d = r["dext"]
                cross[(d["table_class"], d["sheet_class"])].append(
                    f"FLEX-{r['table_row']} (table {d['table_cell'] or 'blank'}, sheet {d['sheet_value']})")
        out["dext_cross_table"] = [{"table_cell": k[0], "sheet_line": k[1], "tests": len(v), "which": v}
                                   for k, v in sorted(cross.items())]
        out["differences"] = [{"sheet": r["file"], "table_row": r.get("table_row"),
                               "fields": sorted(k for k, v in (r.get("agree") or {}).items() if v is False),
                               "as_written": {k: field_values(r, k) for k, v in (r.get("agree") or {}).items()
                                              if v is False}}
                              for r in recs if any(v is False for v in (r.get("agree") or {}).values())]
        return out

    # the 17 lunar sheets are chosen by the number in their file name, then checked against the tie
    lunar = [r for r in records if r["name_number"] in lunar_flex_numbers]
    lunar_check = {"by_file_number": len(lunar),
                   "tied_row_equals_file_number": sum(1 for r in lunar if r.get("table_row") == r["name_number"]),
                   "identifier_inside_equals_table_identifier_of_that_number": sum(
                       1 for r in lunar if r["identifier_inside"].strip().upper() == num2id[r["name_number"]].upper())}
    # table census of the extinction-diameter column (design.md 9)
    cen = collections.Counter(table_dext_class(r["Visible flame extinction diameter; mm"]) for r in flex_tab)
    en_dash = sum(1 for r in flex_tab if r["Visible flame extinction diameter; mm"] == "–")
    name_vs_row = collections.Counter()
    for r in records:
        if "table_row" in r:
            name_vs_row["equal" if r["name_number"] == r["table_row"] else "differ"] += 1
        else:
            name_vs_row["not tied"] += 1
    return {"sheets_listed": len(sheets), "sheets_missing_on_disk": missing,
            "all": tally(records), "lunar_17": tally(lunar), "lunar_17_check": lunar_check,
            "lunar_17_tests": sorted(r["table_row"] for r in lunar),
            "name_number_vs_tied_row": dict(name_vs_row),
            "crosswalk_where_name_number_differs": [
                {"sheet": r["file"], "name_number": r["name_number"], "table_row": r.get("table_row"),
                 "identifier_inside": r["identifier_inside"]}
                for r in records if r.get("table_row") is not None and r["name_number"] != r["table_row"]],
            "not_tied": [{"sheet": r["file"], "identifier_inside": r["identifier_inside"],
                          "rows_with_identifier": r["identifier_rows_in_table"],
                          "sheet_date_time": [r["fields_as_written"].get("Test Date"),
                                              r["fields_as_written"].get("Test Time")],
                          "rows_date_time": {int(x["FLEX Test #"]): [x["Test Date"], x["Test GMT"]]
                                             for x in flex_tab if int(x["FLEX Test #"]) in r["identifier_rows_in_table"]}}
                         for r in records if "table_row" not in r],
            "table_extinction_column": {"rows": len(flex_tab), **dict(cen), "en_dash_cells": en_dash},
            "records": records}


# ======================================================================
# E. Videos: two-label rule of docs/video_design/design.md section 4
# ======================================================================

NON_TEST_CATS = {"Presentations", "Reference Data", "Engineering Documents"}
NON_TEST_NAME = re.compile(r"(?i)wo66\d+|Interviews")
REC_START = re.compile(r"v[il]c-record-(\d{4})-(\d{2})-(\d{2})-(\d{2})h(\d{2})m(\d{2})s")
ACME_TP = re.compile(r"(?<![0-9])(1[7-9]|2[0-2])(\d{3}) ?([A-Z])(\d{1,2})(_\d)?(?![0-9])")
ACME_RAD = re.compile(r"(?<![0-9])(1[7-9]|2[0-2])(\d{3})RAD\d+[ab]?")
ACME_IGN = re.compile(r"(?<![0-9])(1[7-9]|2[0-2])(\d{3})_IgniterCheck")
ACME_DAY_FOLDER = re.compile(r"(?<![0-9])(1[7-9]|2[0-2])(\d{3})(?![0-9])")
CFIG_UNREADABLE = re.compile(r"udp_+\d{4,6}[A-Z]\d")
B2_NAME_1 = re.compile(r"(?i)BASS_GMT_?(?P<gmt>\d+)_SAMPLE_?(?P<sample>\d+)_TEST[_ -]?(?P<test>[BFMOPT]\d+[ab]?)")
B2_NAME_2 = re.compile(r"(?:^|[-_])(?:Test-)?(?P<test>[BFMOPT]\d+[ab]?)(?=[-_.]|experiment|$)")
B2_GMT = re.compile(r"GMT(\d+)")
B2_FOLDER = re.compile(r"/(?P<test>[BFMOPT]\d+)$")
CFI_TP = re.compile(r"(?i)(?<![A-Za-z0-9])F(\d{3})([A-E])(\d{2})")
FLEXV_TP = re.compile(r"(?<![0-9A-Za-z])(" + FLEX_ID_SHAPE + r")(?![0-9])")
FLEXV_FOLDER_TP = re.compile(r"(?<![0-9A-Za-z])(" + FLEX_ID_SHAPE + r")\s*$")
FLEXV_2013 = re.compile(r"(?<![A-Z0-9])[CXNH]\d{3}[HMR]\d{2}(?:-?[A-D])?(?![0-9])")
BASS_DATE = re.compile(r"^(\d{4})(\d{2})(\d{2})[ .](\d{2})[.](\d{2})[. ](\d{2})")
SLICE_RANGE = re.compile(r"UT_(\d{3})_(\d{3})")
SLICE_DAY = re.compile(r"_(\d{3})$")
GROUND_1G = re.compile(r"(?<![A-Za-z])1g(?![A-Za-z])|MFCCalib")
SPICE_DAY = [re.compile(r"^GMT(\d+)_\d{2}\.\d{2}$"), re.compile(r"^SPICE_GMT(\d+)_Ign\d+[ab]?$"),
             re.compile(r"^SPICE_GMT\d{4}_(\d{3})_video$")]
STATE_ORDER = ["two_labels_agree", "one_label", "labels_disagree"]
ALL_STATES = ["two_labels_agree", "one_label", "labels_disagree", "day_only", "id_not_in_table", "none"]


def acme_tp(m, known=None):
    """An ACME test point; with its '_n' suffix where the table lists that form as a test."""
    yy, ddd, x, n, suf = m.groups()
    if not 1 <= int(ddd) <= 366:
        return None
    base = f"{yy}{ddd}{x}{n}"
    return base + suf if suf and known is not None and (base + suf) in known else base


def yyddd(d):
    return f"{d.year % 100:02d}{d.timetuple().tm_yday:03d}"


class VideoTables:
    """Lookups from NASA's tables, built once; rows map to tests.csv by source_file/line."""

    def __init__(self, tables, rowidx):
        self.rowidx = rowidx
        self.t = tables
        tid = lambda r: rowidx.get((r["_file"], r["_line"]))
        # ACME per-test tables: test point -> tests; days (YYDDD) -> tests
        self.acme_tp, self.acme_day = {}, {}
        for inv, files in (("PSI-10", ["PSI-10_Experimental table_Flame Design_Normal Flame.csv",
                                       "PSI-10_Experimental table_Flame Design_Inverse Flame.csv"]),
                           ("PSI-159", ["PSI-159_Experimental table_CFI-G_Normal Flames.csv",
                                        "PSI-159_Experimental table_CFI-G_Inverse Flames.csv"])):
            tp, day = collections.defaultdict(set), collections.defaultdict(set)
            for fn in files:
                for r in tables[fn]:
                    t = tid(r)
                    key = r["Test"].replace(" ", "").upper()
                    if t and key:
                        tp[key].add(t)
                        day[key[:5]].add(t)
            self.acme_tp[inv], self.acme_day[inv] = tp, day
        # ACME per-day tables: YYDDD -> number of table rows that day
        self.acme_day_rows = {}
        rows20 = collections.Counter()
        for r in tables["PSI-20_Experimental table_ACME BRE.csv"]:
            mo = MONTHS.get(r["Month"].strip().rstrip(".").lower()[:3])
            try:
                rows20[yyddd(datetime.date(int(r["Year"]), mo, int(r["Date"])))] += 1
            except (TypeError, ValueError):
                pass
        self.acme_day_rows["PSI-20"] = rows20
        for inv, fn, col in (("PSI-21", "PSI-21_Experimental table_CLD Flame.csv", "Test Day"),
                             ("PSI-22", "PSI-22_Experimental table_ACME E-FIELD Flames.csv", "Test Day"),
                             ("PSI-23", "PSI-23_Experimental table_ACME s-Flame.csv", "Test Day*")):
            c = collections.Counter()
            for r in tables[fn]:
                if re.fullmatch(r"\d{5}", r[col].strip()):
                    c[r[col].strip()] += 1
            self.acme_day_rows[inv] = c
        # BASS-II
        self.b2 = {}
        for r in tables["PSI-25_Experimental table_BASS-II.csv"]:
            self.b2[r["Test #"]] = r
        # CFI: CIR -> tests; day of year -> tests
        self.cfi_tp, self.cfi_doy = collections.defaultdict(set), collections.defaultdict(set)
        for r in tables["PSI-39_Experimental table_CFI.csv"]:
            t = tid(r)
            if t:
                self.cfi_tp[r["CIR"].upper()].add(t)
                d = parse_date(r["Test Date"])
                if d:
                    self.cfi_doy[d.timetuple().tm_yday].add(t)
        # FLEX: identifier -> tests
        self.flex_tp = collections.defaultdict(set)
        for r in tables["PSI-69_Experimental table_FLEX.csv"]:
            t = tid(r)
            if t:
                self.flex_tp[r["FLEX Identifier"].upper()].add(t)
        # BASS: date -> tests
        self.bass_day = collections.defaultdict(set)
        for r in tables["PSI-26_Experimental table_BASS.csv"]:
            d, t = parse_date(r["Date"]), tid(r)
            if d and t:
                self.bass_day[d].add(t)
        # SAME-R: (month, day) -> tests
        self.samer_day = collections.defaultdict(set)
        for r in tables["PSI-101_Experimental table_SAME-R.csv"]:
            m = re.match(r"^(\d{1,2})-([A-Za-z]{3})", r["Date"].strip())
            t = tid(r)
            if m and t and MONTHS.get(m.group(2).lower()):
                self.samer_day[(MONTHS[m.group(2).lower()], int(m.group(1)))].add(t)
        # SLICE: day of year -> table rows (no tests.csv rows)
        self.slice_doy = collections.Counter()
        for r in tables["PSI-106_Experimental table_Slice.csv"]:
            d = parse_date(r["Test Date"])
            if d:
                self.slice_doy[d.timetuple().tm_yday] += 1
        # SPICE: GMT day -> tests
        self.spice_day = collections.defaultdict(set)
        for r in tables["PSI-107_Experimental table_Spice.csv"]:
            t = tid(r)
            if t and re.fullmatch(r"\d+", r["GMT date"].strip()):
                self.spice_day[int(r["GMT date"].strip())].add(t)


def _test_scope(name_tests, folder_tests, name_present, folder_present, against=False):
    """Link state at test scope from the tests each label ties (sets)."""
    if name_tests and folder_present:
        if folder_tests and folder_tests == name_tests and len(name_tests) == 1:
            return "two_labels_agree"
        return "labels_disagree"
    if name_tests:
        return "labels_disagree" if against else "one_label"
    if folder_tests:
        return "labels_disagree" if (name_present or against) else "one_label"
    return None


def video_state(f, vt):
    """(scope, state, tests named by any label, note) of one video file."""
    inv, stem, bare = f["inv"], f["stem"], f["bare"]
    folders = f["folders"]
    if f["cat"] in NON_TEST_CATS or NON_TEST_NAME.search(stem):
        return "none", "none", set(), "outreach, reference or engineering clip"

    if inv in ("PSI-10", "PSI-159", "PSI-20", "PSI-21", "PSI-22", "PSI-23"):
        known = vt.acme_tp.get(inv)
        ntps = [tp for tp in (acme_tp(m, known) for m in ACME_TP.finditer(stem)) if tp]
        ftp = None
        for seg in (folders[-1:], folders[-2:-1]):
            for s in seg:
                for m in ACME_TP.finditer(s):
                    ftp = acme_tp(m, known)
                    if ftp:
                        break
            if ftp:
                break
        day = (ntps[0][:5] if ntps else ftp[:5] if ftp else None)
        if day is None:
            for rx, on in ((ACME_RAD, stem), (ACME_IGN, stem), (ACME_DAY_FOLDER, f["folder"])):
                m = rx.search(on)
                if m and 1 <= int(m.group(2)) <= 366:
                    day = m.group(1) + m.group(2)
                    break
        if inv in ("PSI-10", "PSI-159"):
            tpmap = vt.acme_tp[inv]
            name_tests = set().union(*[tpmap.get(tp, set()) for tp in ntps]) if ntps else set()
            folder_tests = tpmap.get(ftp, set()) if ftp else set()
            against = inv == "PSI-159" and not ntps and bool(CFIG_UNREADABLE.search(stem))
            st = _test_scope(name_tests, folder_tests, bool(ntps), bool(ftp), against)
            if st:
                return "test", st, name_tests | folder_tests, ""
            if day and vt.acme_day[inv].get(day):
                return "day", "day_only", set(), f"day {day}"
            if ntps or ftp or day:
                return "none", "id_not_in_table", set(), "identifier or day not in the table"
            return "none", "none", set(), "no identifier"
        if day and vt.acme_day_rows[inv].get(day):
            return "day", "day_only", set(), f"day {day}"
        if ntps or ftp or day:
            return "none", "id_not_in_table", set(), "identifier or day not in the table"
        return "none", "none", set(), "no identifier"

    if inv == "PSI-25":
        m = B2_NAME_1.search(bare)
        gmt = sample = None
        if m:
            test, gmt, sample = m.group("test"), int(m.group("gmt")), int(m.group("sample"))
        else:
            m = B2_NAME_2.search(bare)
            test = m.group("test") if m else None
            g = B2_GMT.search(bare)
            gmt = int(g.group(1)) if g and test else None
        if test:
            test = test[0].upper() + re.sub(r"[ABab]$", lambda x: x.group(0).lower(), test[1:])
        fm = B2_FOLDER.search(f["folder"])
        ftest = fm.group("test") if fm else None
        row = vt.b2.get(test) if test else None
        if test and row is None:
            runs = [k for k in vt.b2 if re.fullmatch(re.escape(test) + "[ab]", k)]
            if runs and (ftest is None or ftest == test):
                return "run", "day_only", set(), f"name names both runs {runs}"
            return "none", "id_not_in_table", set(), f"test {test} not in the table"
        if row is not None:
            tests = {"BASS2-" + test}
            fit_rows = []
            mismatch = False
            if gmt is not None and str(gmt) != row["GMT"].strip():
                mismatch = True
            sm = re.match(r"\d+", row["Sample #"].strip())
            if sample is not None and (sm is None or int(sm.group(0)) != sample):
                mismatch = True
            if mismatch:
                for k, r in vt.b2.items():
                    rs = re.match(r"\d+", r["Sample #"].strip())
                    if (gmt is None or str(gmt) == r["GMT"].strip()) and \
                            (sample is None or (rs and int(rs.group(0)) == sample)):
                        fit_rows.append(k)
                tests |= {"BASS2-" + k for k in fit_rows}
                if ftest:
                    tests |= {"BASS2-" + k for k in vt.b2 if re.fullmatch(re.escape(ftest) + "[ab]?", k)}
                return "test", "labels_disagree", tests, f"day/sample of the name fit {fit_rows}; folder {ftest}"
            if ftest is None:
                return "test", "one_label", tests, "file name only"
            if ftest == test:
                return "test", "two_labels_agree", tests, ""
            if test[-1] in "ab" and ftest == test[:-1]:
                return "test", "one_label", tests, "folder names both runs of this sample"
            tests |= {"BASS2-" + k for k in vt.b2 if re.fullmatch(re.escape(ftest) + "[ab]?", k)}
            return "test", "labels_disagree", tests, f"folder {ftest}"
        if ftest:
            if ftest in vt.b2:
                return "test", "one_label", {"BASS2-" + ftest}, "folder name only"
            runs = [k for k in vt.b2 if re.fullmatch(re.escape(ftest) + "[ab]", k)]
            if runs:
                return "run", "day_only", set(), f"folder names both runs {runs}"
            return "none", "id_not_in_table", set(), f"folder test {ftest} not in the table"
        return "none", "none", set(), "no identifier"

    if inv == "PSI-39":
        nm = CFI_TP.search(stem)
        ntp = "F" + "".join(nm.groups()).upper() if nm else None
        fmm = None
        for m in CFI_TP.finditer(f["folder"]):
            fmm = m
        ftp = "F" + "".join(fmm.groups()).upper() if fmm else None
        name_tests = set(vt.cfi_tp.get(ntp, set())) if ntp else set()
        folder_tests = set(vt.cfi_tp.get(ftp, set())) if ftp else set()
        if len(name_tests) > 1 or (not name_tests and len(folder_tests) > 1):
            return "day", "day_only", set(), f"CIR {ntp or ftp} on several rows"
        st = _test_scope(name_tests, folder_tests, bool(ntp), bool(ftp))
        if st:
            return "test", st, name_tests | folder_tests, ""
        code = ntp or ftp
        if code:
            doy = int(code[1:4])
            if vt.cfi_doy.get(doy):
                return "day", "day_only", set(), f"day {doy}"
            return "none", "id_not_in_table", set(), f"CIR {code} not in the table"
        return "none", "none", set(), "no identifier"

    if inv == "PSI-69":
        nm = FLEXV_TP.search(stem)
        ntp = nm.group(1).upper() if nm else None
        fm = FLEXV_FOLDER_TP.search(folders[-1]) if folders else None
        ftp = fm.group(1).upper() if fm else None
        name_tests = set(vt.flex_tp.get(ntp, set())) if ntp else set()
        folder_tests = set(vt.flex_tp.get(ftp, set())) if ftp else set()
        if len(name_tests) > 1 or (not name_tests and len(folder_tests) > 1):
            return "day", "day_only", set(), f"identifier {ntp or ftp} on several rows"
        st = _test_scope(name_tests, folder_tests, bool(ntp), bool(ftp))
        if st:
            return "test", st, name_tests | folder_tests, ""
        if ntp or ftp or FLEXV_2013.search(stem):
            return "none", "id_not_in_table", set(), "test point not in the FLEX table"
        return "none", "none", set(), "no identifier (folder FLEX number not used)"

    if inv == "PSI-26":
        m = BASS_DATE.search(stem)
        if m:
            d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))) - datetime.timedelta(days=1)
            if vt.bass_day.get(d):
                return "day", "day_only", set(), f"test day {d}"
            return "none", "id_not_in_table", set(), f"date {d} not in the table"
        return "none", "none", set(), "no identifier"

    if inv == "PSI-101":
        m = REC_START.search(stem)
        if m:
            key = (int(m.group(2)), int(m.group(3)))
            if vt.samer_day.get(key):
                return "day", "day_only", set(), f"recording date {key}"
            return "none", "id_not_in_table", set(), f"date {key} not in the table"
        return "none", "none", set(), "no identifier"

    if inv == "PSI-106":
        m = SLICE_RANGE.search(f["folder"])
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            if any(lo <= d <= hi for d in vt.slice_doy):
                return "several_days", "day_only", set(), f"days {lo}-{hi}"
            return "none", "id_not_in_table", set(), f"days {lo}-{hi} not in the table"
        m = SLICE_DAY.search(f["folder"])
        if m and not GROUND_1G.search(f["folder"]) and not GROUND_1G.search(stem):
            if vt.slice_doy.get(int(m.group(1))):
                return "day", "day_only", set(), f"day {m.group(1)}"
            return "none", "id_not_in_table", set(), f"day {m.group(1)} not in the table"
        return "none", "none", set(), "no identifier"

    if inv == "PSI-107":
        for rx in SPICE_DAY:
            m = rx.search(stem)
            if m:
                day = int(m.group(1))
                if vt.spice_day.get(day):
                    return "day", "day_only", set(), f"GMT day {day}"
                return "none", "id_not_in_table", set(), f"GMT day {day} not in the table"
        return "none", "none", set(), "no identifier"

    return "none", "none", set(), "no rule for this investigation"


def recount_videos(listings, tables, tests, need_tests, per_test, raw_kinds):
    vid_ext, _ = kind_exts(raw_kinds)
    rowidx = row_index(tests)
    vt = VideoTables(tables, rowidx)
    vids = []
    for acc, L in listings.items():
        for f in L["files"]:
            if f["ext"] in vid_ext and f["cat"] != "Experimental table":
                scope, state, tset, note = video_state(f, vt)
                vids.append(dict(f, scope=scope, state=state, tests=sorted(tset), note=note))
    tot = {"files": len(vids), "bytes": sum(v["bytes"] for v in vids)}
    st = collections.Counter(v["state"] for v in vids)
    stb = collections.Counter()
    for v in vids:
        stb[v["state"]] += v["bytes"]
    sc = collections.Counter(v["scope"] for v in vids)
    scb = collections.Counter()
    for v in vids:
        scb[v["scope"]] += v["bytes"]
    per_inv = collections.defaultdict(collections.Counter)
    for v in vids:
        per_inv[v["inv"]][v["state"]] += 1
    # best state per test over videos at test scope
    best = {}
    files_of = collections.defaultdict(list)
    for v in vids:
        if v["scope"] != "test":
            continue
        for t in v["tests"]:
            files_of[t].append(v)
            if t not in best or STATE_ORDER.index(v["state"]) < STATE_ORDER.index(best[t]):
                best[t] = v["state"]
    t_inv = {t["test_id"]: t["investigation_id"] for t in tests}
    best_c = collections.Counter(best.values())
    b2_best = collections.Counter(s for t, s in best.items() if t_inv.get(t) == "PSI-25")
    counted = collections.defaultdict(set)
    for r in need_tests:
        if r["objective_link"] == "stated":
            counted[r["need_id"]].add(r["test_id"])

    def four(ts):
        c = collections.Counter(best.get(t, "none") for t in ts)
        return [len(ts), c["two_labels_agree"], c["one_label"], c["labels_disagree"], c["none"]]

    per_question = {q: four(sorted(ts)) for q, ts in sorted(counted.items())}
    placement_of = {}
    for (sid, tid), (om, pm, pl) in per_test.items():
        if pl == "cannot_be_placed_from_table" and om == "in" and pm == "not_recorded":
            pl = "oxygen_inside_pressure_not_in_table"
        placement_of[(sid, tid)] = pl
    by_place = {}
    for sid in ("iss", "lunar_habitat"):
        for q in ("P1", "D1", "S1", "P3"):
            groups = collections.defaultdict(list)
            for t in sorted(counted.get(q, ())):
                groups[placement_of[(sid, t)]].append(t)
            for pl, ts in sorted(groups.items()):
                by_place[f"{sid}|{q}|{pl}"] = four(ts)
    lunar_inside = sorted(t for (sid, t), pl in placement_of.items() if sid == "lunar_habitat" and pl == "inside")
    lunar_two = [t for t in lunar_inside if best.get(t) == "two_labels_agree"]
    lunar_two_files = [v for t in lunar_two for v in files_of[t] if v["state"] == "two_labels_agree"]
    all_counted = set().union(*counted.values()) if counted else set()
    counted_files = {v["id"]: v for t in all_counted for v in files_of.get(t, [])}
    # claimed per-file comparison (video/data/video_links.csv, claimed side only)
    claimed_cmp = None
    if os.path.exists(VIDEO_LINKS_CLAIMED):
        with open(VIDEO_LINKS_CLAIMED, encoding="utf-8", newline="") as fh:
            lines = [ln for ln in fh if not ln.startswith("#")]
        claimed = {r["psi_file_id"]: r for r in csv.DictReader(lines)}
        diff = []
        same = 0
        for v in vids:
            c = claimed.get(v["id"])
            if c is None:
                diff.append({"file": v["key_name"], "recount": v["state"], "claimed": "absent"})
                continue
            ctests = set(t for t in re.split(r"[;,| ]+", c.get("test_id", "")) if t)
            if c["link_state"] == v["state"]:
                same += 1
            else:
                diff.append({"investigation": v["inv"], "file": v["key_name"], "folder": v["folder"],
                             "recount": v["state"], "claimed": c["link_state"],
                             "recount_tests": v["tests"], "claimed_test": c.get("test_id", ""),
                             "recount_note": v["note"]})
        claimed_cmp = {"claimed_rows": len(claimed), "files_compared": len(vids),
                       "same_state": same, "different_state": len(diff),
                       "differences_by_pair": dict(collections.Counter(
                           f"{d.get('investigation','?')}: recount {d['recount']} / claimed {d['claimed']}"
                           for d in diff)),
                       "differences": diff[:60]}
    return {
        "totals": tot,
        "by_state": {s: {"files": st.get(s, 0), "bytes": stb.get(s, 0)} for s in ALL_STATES},
        "by_scope": {s: {"files": sc.get(s, 0), "bytes": scb.get(s, 0)}
                     for s in ("test", "run", "day", "several_days", "none")},
        "per_investigation": {k: [per_inv[k].get(s, 0) for s in ALL_STATES]
                              for k in sorted(per_inv, key=lambda x: int(x.split("-")[1]))},
        "tests_by_best_state": [best_c["two_labels_agree"], best_c["one_label"], best_c["labels_disagree"]],
        "bass2_tests_by_best_state": [b2_best["two_labels_agree"], b2_best["one_label"], b2_best["labels_disagree"]],
        "counted_per_question": per_question,
        "by_placement": by_place,
        "lunar_inside": {"tests": len(lunar_inside), "with_two_labels_agree": len(lunar_two),
                         "investigations": sorted({t_inv[t] for t in lunar_two}),
                         "files": len({v["id"] for v in lunar_two_files}),
                         "bytes": sum({v["id"]: v["bytes"] for v in lunar_two_files}.values())},
        "videos_tied_to_counted_tests": {
            "files": len(counted_files), "bytes": sum(v["bytes"] for v in counted_files.values()),
            "by_investigation": dict(collections.Counter(v["inv"] for v in counted_files.values()))},
        "labels_disagree_files": [{"file": v["key_name"], "folder": v["folder"], "tests": v["tests"],
                                   "note": v["note"]} for v in vids if v["state"] == "labels_disagree"],
        "claimed_per_file_comparison": claimed_cmp,
    }


# ======================================================================
# F. Listing totals against raw_inventory.json (drift)
# ======================================================================

def recount_inventory(listings, inventory):
    claimed = {i["investigation_id"]: i for i in inventory["investigations"]}
    rows = []
    for acc, L in listings.items():
        c = claimed.get(acc, {})
        mine = {"files": len(L["files"]), "bytes": sum(f["bytes"] or 0 for f in L["files"]),
                "listing_rows": L["rows"], "repeated_rows": L["rows"] - len(L["files"]),
                "listing_rows_bytes": L["rows_bytes"],
                "records_beyond_one_per_key": L["records_beyond_one_per_key"]}
        diff = {k: [c.get(k), v] for k, v in mine.items() if c.get(k) != v}
        rows.append({"investigation": acc, **mine, "differs_from_inventory": diff})
    tot = {k: sum(r[k] for r in rows) for k in ("files", "bytes", "listing_rows", "repeated_rows",
                                                "listing_rows_bytes")}
    ct = inventory["_meta"]["totals"]
    return {"team_listing_fetched_utc": inventory["_meta"].get("listings_fetched_at"),
            "investigations": len(rows), "totals": tot,
            "inventory_totals": {k: ct.get(k) for k in tot},
            "investigations_that_differ": [r for r in rows if r["differs_from_inventory"]],
            "per_investigation": rows}


def frozen_files():
    """sha256 of the four frozen files against the constants of pipeline/check.py (read as text)."""
    with open(CHECK_PY, encoding="utf-8") as fh:
        src = fh.read()
    m = re.search(r"FROZEN_SHA256\s*=\s*\{(.*?)\}", src, re.S)
    want = dict(re.findall(r'"([\w.]+)"\s*:\s*"([0-9a-f]{64})"', m.group(1))) if m else {}
    out = {}
    for name in ("tests.csv", "need_tests.csv", "scenario_needs.csv", "scenario_tests.csv"):
        with open(os.path.join(PIPE_DIR, name), "rb") as fh:
            raw = fh.read()
        as_is = hashlib.sha256(raw).hexdigest()
        # a Windows checkout with core.autocrlf writes CRLF; the committed bytes have LF
        lf = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
        out[name] = {"snapshot": want.get(name), "working_tree_bytes": as_is,
                     "with_crlf_as_lf": lf, "crlf_in_working_tree": b"\r\n" in raw,
                     "unchanged": want.get(name) in (as_is, lf)}
    return out


# ======================================================================
# Fixtures and report
# ======================================================================

def build_fixtures(R):
    F = []
    A = R["A_placement"]["per_scenario"]
    F.append(fixture("A", "lunar_habitat, all tests: inside / cannot be placed / oxidizer stream / outside",
                     [26, 676, 63, 1059], [A["lunar_habitat"]["all"][p] for p in PLACEMENTS[:4]]))
    F.append(fixture("A", "lunar_habitat, solid-fuel tests: inside / cannot be placed / outside",
                     [0, 237, 139], [A["lunar_habitat"]["solid"][p] for p in
                                     ("inside", "cannot_be_placed_from_table", "outside_by_recorded_value")]))
    F.append(fixture("A", "iss, all tests: inside / cannot be placed / oxidizer stream / outside",
                     [179, 739, 106, 800], [A["iss"]["all"][p] for p in PLACEMENTS[:4]]))
    F.append(fixture("A", "mars_habitat: no range set", 1824, A["mars_habitat"]["all"]["no_range_set"]))
    cmpA = R["A_placement"]["claimed_scenario_tests"]
    F.append(fixture("A", "per-test o2_match and pressure_match differing from scenario_tests.csv",
                     0, len(cmpA["disagreements"])))
    B = R["B_states"]
    F.append(fixture("B", "need_gap_states.csv keys whose states do not sum to in-scope / counted totals",
                     0, len(B["comparison"]["sum_failures"])))
    F.append(fixture("B", "need_gap_states.csv keys differing from the recomputed states",
                     0, len(B["comparison"]["differences"])))
    p1 = B["P1_pressure_kpa"]
    F.append(fixture("B", "P1 pressure: raw column / document only / not found (in-scope tests)",
                     [134, 129, 113], [p1.get("column_in_sampled_raw_file", 0),
                                       p1.get("documented_only", 0), p1.get("not_in_sampled_files", 0)]))
    C = R["C_links"]
    fx = C["flex_17"]
    F.append(fixture("C", "17 lunar FLEX tests: files, bytes", [299, 24954842492], [fx["files"], fx["bytes"]]))
    F.append(fixture("C", "17 lunar FLEX tests: zip files, bytes", [47, 24923186032],
                     [fx["zip"]["files"], fx["zip"]["bytes"]]))
    F.append(fixture("C", "17 lunar FLEX tests: other files, bytes", [252, 31656460],
                     [fx["files"] - fx["zip"]["files"], fx["bytes"] - fx["zip"]["bytes"]]))
    F.append(fixture("C", "17 lunar FLEX tests by extension: .txt / .zip / .pdf / .rtf",
                     [212, 47, 23, 17], [fx["by_extension"].get(e, 0) for e in (".txt", ".zip", ".pdf", ".rtf")]))
    cg = C["cfig_9"]
    F.append(fixture("C", "9 lunar CFI-G tests: files, bytes", [99, 79403613858], [cg["files"], cg["bytes"]]))
    F.append(fixture("C", "9 lunar CFI-G tests: zip or ts files", 35, cg["archive_or_video"]["files"]))
    lt = C["lunar_26"]
    F.append(fixture("C", "26 lunar tests: files, bytes", [398, 104358456350], [lt["files"], lt["bytes"]]))
    F.append(fixture("C", "26 lunar tests: second label folder agrees / names no test / names another test",
                     [336, 47, 15], [lt["second_label"].get(k, 0) for k in
                                     ("folder_agrees", "folder_names_no_test", "folder_names_another_test")]))
    F.append(fixture("C", "26 lunar tests: small files, bytes; archives and recordings, bytes",
                     [316, 86853632, 82, 104271602718],
                     [lt["other"]["files"], lt["other"]["bytes"], lt["archive_or_video"]["files"],
                      lt["archive_or_video"]["bytes"]]))
    F.append(fixture("C", "FLEX identifier 193F001 on table rows (FLEX Test #)", [70, 73],
                     C["flex_table"]["identifiers_on_several_rows"].get("193F001")))
    F.append(fixture("C", "FLEX test sheets numbered above the last table row", 6,
                     len(C["flex_sheets_in_listing"]["numbered_above_table"])))
    F.append(fixture("C", "FLEX-19: files, bytes", [17, 1112400426], [C["flex_19"]["files"], C["flex_19"]["bytes"]]))
    Dd = R["D_sheets"]
    F.append(fixture("D", "FLEX test sheets in the listing: files, bytes", [272, 250375],
                     [Dd["all"]["sheets"], Dd["all"]["bytes"]]))
    l17 = Dd["lunar_17"]
    F.append(fixture("D", "17 lunar sheets: files, bytes", [17, 15369], [l17["sheets"], l17["bytes"]]))
    lc = Dd["lunar_17_check"]
    F.append(fixture("D", "17 lunar sheets (by file number): identifier inside equals the table's", 17,
                     lc["identifier_inside_equals_table_identifier_of_that_number"]))
    F.append(fixture("D", "17 lunar sheets: tied to one row (identifier + second field), row = file number",
                     [17, 17], [l17["tied_to_one_row"], lc["tied_row_equals_file_number"]]))
    fa = l17["field_agreement"]
    F.append(fixture("D", "17 lunar sheets: pressure agrees within rounding", 16,
                     fa.get("pressure", {}).get("agree", 0)))
    F.append(fixture("D", "17 lunar sheets: oxygen agrees", 16, fa.get("O2 Mole Fraction", {}).get("agree", 0)))
    exp_cross = {("number above zero", "the same number"): ["FLEX-21", "FLEX-25", "FLEX-26"],
                 ("number above zero", "nan"): ["FLEX-20"],
                 ("0", "0.00"): ["FLEX-39", "FLEX-43"],
                 ("blank", "a number"): ["FLEX-23", "FLEX-38"],
                 ("blank", "nan"): ["FLEX-19", "FLEX-22", "FLEX-24", "FLEX-27", "FLEX-28", "FLEX-37"],
                 ("dash", "a number"): ["FLEX-40"], ("dash", "0.00"): ["FLEX-41"], ("dash", "nan"): ["FLEX-42"]}
    got = {(r["table_cell"], r["sheet_line"]): sorted((w.split(" ")[0] for w in r["which"]),
                                                      key=lambda x: int(x.split("-")[1]))
           for r in l17["dext_cross_table"]}
    F.append(fixture("D", "17 lunar sheets: Dext cross-table of design.md section 7",
                     {f"table {a}, sheet {b}": v for (a, b), v in sorted(exp_cross.items())},
                     {f"table {a}, sheet {b}": v for (a, b), v in sorted(got.items())}))
    tc = Dd["table_extinction_column"]
    F.append(fixture("D", "FLEX table extinction column: numbers / zeros / blanks / en dashes (274 rows)",
                     [189, 8, 49, 28, 274], [tc.get("number above zero", 0), tc.get("0", 0),
                                             tc.get("blank", 0), tc.get("en_dash_cells", 0), tc["rows"]]))
    E = R["E_videos"]
    F.append(fixture("E", "videos: files, bytes", [2623, 426053691302], [E["totals"]["files"], E["totals"]["bytes"]]))
    F.append(fixture("E", "link states: two agree / one / disagree / day only / id not in table / none",
                     [662, 374, 10, 1217, 330, 30], [E["by_state"][s]["files"] for s in ALL_STATES]))
    F.append(fixture("E", "link state bytes (same order)",
                     [152320655239, 81527352372, 5118358115, 102112670418, 83454932324, 1519722834],
                     [E["by_state"][s]["bytes"] for s in ALL_STATES]))
    F.append(fixture("E", "tie scope: test / run / day / several days / none",
                     [1046, 3, 1188, 26, 360], [E["by_scope"][s]["files"] for s in
                                                ("test", "run", "day", "several_days", "none")]))
    exp_inv = {"PSI-10": [0, 306, 0, 11, 0, 0], "PSI-20": [0, 0, 0, 163, 33, 3], "PSI-21": [0, 0, 0, 358, 2, 3],
               "PSI-22": [0, 0, 0, 215, 0, 6], "PSI-23": [0, 0, 0, 285, 1, 4], "PSI-25": [244, 47, 5, 0, 0, 0],
               "PSI-26": [0, 0, 0, 113, 1, 0], "PSI-39": [101, 5, 2, 20, 118, 0], "PSI-69": [3, 5, 1, 0, 163, 11],
               "PSI-101": [0, 0, 0, 8, 0, 0], "PSI-102": [0, 0, 0, 0, 0, 2], "PSI-106": [0, 0, 0, 27, 0, 1],
               "PSI-107": [0, 0, 0, 7, 12, 0], "PSI-159": [314, 11, 2, 10, 0, 0]}
    for k, v in exp_inv.items():
        F.append(fixture("E", f"{k} videos by link state (six states)", v, E["per_investigation"].get(k)))
    F.append(fixture("E", "tests by best state: two agree / one / disagree only", [463, 344, 6],
                     E["tests_by_best_state"]))
    F.append(fixture("E", "BASS-II tests by best state", [101, 20, 2], E["bass2_tests_by_best_state"]))
    for q, v in (("P1", [133, 99, 18, 2, 14]), ("D1", [122, 98, 16, 2, 6]),
                 ("S1", [298, 19, 10, 1, 268]), ("P3", [2, 0, 0, 0, 2])):
        F.append(fixture("E", f"{q} counted tests: total / two agree / one / disagree only / none", v,
                         E["counted_per_question"].get(q)))
    bp = E["by_placement"]
    for key, v in (("iss|P1|oxygen_inside_pressure_not_in_table", [55, 42, 4, 0, 9]),
                   ("iss|P1|outside_by_recorded_value", [78, 57, 14, 2, 5]),
                   ("iss|D1|oxygen_inside_pressure_not_in_table", [45, 42, 2, 0, 1]),
                   ("iss|D1|outside_by_recorded_value", [77, 56, 14, 2, 5]),
                   ("iss|S1|inside", [56, 2, 0, 0, 54]),
                   ("iss|S1|oxygen_inside_pressure_not_in_table", [7, 3, 4, 0, 0]),
                   ("iss|S1|outside_by_recorded_value", [235, 14, 6, 1, 214]),
                   ("iss|P3|oxygen_inside_pressure_not_in_table", [2, 0, 0, 0, 2]),
                   ("lunar_habitat|S1|inside", [17, 0, 0, 0, 17]),
                   ("lunar_habitat|S1|outside_by_recorded_value", [281, 19, 10, 1, 251]),
                   ("lunar_habitat|P1|outside_by_recorded_value", [133, 99, 18, 2, 14]),
                   ("lunar_habitat|D1|outside_by_recorded_value", [122, 98, 16, 2, 6]),
                   ("lunar_habitat|P3|outside_by_recorded_value", [2, 0, 0, 0, 2])):
        F.append(fixture("E", f"{key.replace('|', ', ')}: counted / two agree / one / disagree only / none",
                         v, bp.get(key)))
    li = E["lunar_inside"]
    F.append(fixture("E", "lunar inside: tests, with a two-labels-agree video, its files, bytes",
                     [26, 8, 8, 2640554564], [li["tests"], li["with_two_labels_agree"], li["files"], li["bytes"]]))
    vc = E["videos_tied_to_counted_tests"]
    F.append(fixture("E", "videos tied at test scope to a counted test: files, bytes, BASS-II, FLEX",
                     [298, 17993880758, 289, 9], [vc["files"], vc["bytes"], vc["by_investigation"].get("PSI-25", 0),
                                                  vc["by_investigation"].get("PSI-69", 0)]))
    Finv = R["F_inventory"]
    F.append(fixture("F", "listing files, bytes against raw_inventory.json",
                     [60866, 13471850126356], [Finv["totals"]["files"], Finv["totals"]["bytes"]]))
    F.append(fixture("F", "listing rows, repeated rows against raw_inventory.json",
                     [66567, 5701], [Finv["totals"]["listing_rows"], Finv["totals"]["repeated_rows"]]))
    F.append(fixture("F", "investigations whose listing differs from raw_inventory.json", 0,
                     len(Finv["investigations_that_differ"])))
    fz = R["frozen_files"]
    F.append(fixture("O6", "frozen files with the sha256 of the check.py snapshot (of 4)", 4,
                     sum(1 for v in fz.values() if v["unchanged"])))
    return F


def fmt(v):
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, int):
        return f"{v:,}"
    if isinstance(v, list):
        return " / ".join(fmt(x) for x in v)
    if isinstance(v, dict):
        return "; ".join(f"{k}: {fmt(x)}" for k, x in v.items())
    return "" if v is None else str(v)


def write_report(R, fixtures, path):
    L = []
    w = L.append
    w("# Independent recount of the raw-data chain")
    w("")
    w("*AI-generated (Claude Code): code and report by a second AI session independent of the pipeline, "
      f"{R['_meta']['run_date']}. No language model runs when the script runs.*")
    w("")
    w("Recomputed by a second AI session with code that does not import the pipeline; not checked by a person.")
    w("")
    w(f"Script: `validation/raw_chain_recount.py` (offline run of {R['_meta']['run_utc']}). "
      "Figures: `validation/raw_chain_recount.json`. "
      "It imports no module of `pipeline/`, `video/`, `ai/`, `scripts/` or `scoring/`; their source and the "
      "design documents were read as text to learn the rules. Every 'match' below is computed by the script "
      "from the expected value typed from the design and the recounted value; no rule was changed to reach a "
      "number. A research exploration aid, not safety guidance; the counts are the team's, not NASA's.")
    w("")
    n_ok = sum(1 for f in fixtures if f["match"])
    w(f"**Summary: {n_ok} of {len(fixtures)} fixtures reproduce.** Fixtures that do not reproduce:")
    w("")
    bad = [f for f in fixtures if not f["match"]]
    if not bad:
        w("- none")
    for f in bad:
        w(f"- {f['block']}: {f['what']}: expected {fmt(f['expected'])}, recounted {fmt(f['recounted'])}")
    w("")
    w("## Inputs and definitions")
    w("")
    meta = R["_meta"]
    w(f"- Listings: the 24 saved listings in `data/psi/file_listings/` (git-ignored) were fetched for this recount "
      f"on {meta['listings_fetched_utc']} (the 24 listing calls of the network log), not the team's listing of "
      f"{TEAM_LISTING_FETCHED}; section F compares the two. The FLEX test sheets are in "
      "`data/psi/raw_cache/PSI-69/test_sheets/` (git-ignored).")
    w("- A file is one record of a listing, counted once per PSI file id; bytes are `bytes_size` as PSI reports them.")
    w("- Placement (A) uses `o2_pct`, `o2_basis` and `pressure_kpa` of `data/pipeline/tests.csv` and the ranges of "
      "`pipeline/spec/scenarios.json` (minimum inclusive; maximum inclusive only where `max_inclusive` is set). "
      "Order: no range set; inside; outside by a recorded value; oxygen of an oxidizer stream; otherwise cannot be "
      "placed.")
    w("- **Counted tests** are the rows of `data/pipeline/need_tests.csv` with `objective_link = stated`.")
    rc = meta["tests_csv_source_row_check"]["counts"]
    w(f"- A test of `tests.csv` is tied to its NASA table row by `source_file` and `source_row` (CSV record, header "
      f"= 1). Check where the test id carries the row's identifier (PSI-10, 25, 39, 69, 159): {fmt(rc)}.")
    w(f"- Tables are read as UTF-8, except `PSI-69_Experimental table_FLEX.csv`, which is not valid UTF-8 and is "
      f"read as cp1252 (its 0x96 bytes are en dashes), so its cells are compared exactly as written.")
    w("- The claimed side (`scenario_tests.csv`, `need_gap_states.csv`, `raw_inventory.json`, `video/data/video_links.csv`) "
      "is read only to compare; no count uses it.")
    w("")
    w("## Fixtures, expected against recounted")
    w("")
    for blk, title in (("A", "A. Placement per scenario"), ("B", "B. Chain sums (states per need and variable)"),
                       ("C", "C. Files that name the tests inside the lunar ranges"),
                       ("D", "D. FLEX test sheets against the FLEX table"),
                       ("E", "E. Videos (two-label rule)"), ("F", "F. Listing against raw_inventory.json"),
                       ("O6", "O6. Frozen files")):
        rows = [f for f in fixtures if f["block"] == blk]
        w(f"### {title}")
        w("")
        w("| Fixture | Expected | Recounted | Match |")
        w("|---|---|---|---|")
        for f in rows:
            cell = lambda x: fmt(x).replace("|", r"\|")
            w(f"| {f['what']} | {cell(f['expected'])} | {cell(f['recounted'])} | {'yes' if f['match'] else '**no**'} |")
        w("")
        for line in R["notes"].get(blk, []):
            w(line)
        w("")
    w("## Corrections made after the first run")
    w("")
    for line in RUN_HISTORY:
        w(f"- {line}")
    w("")
    w("## What this recount does not cover")
    w("")
    for line in R["not_covered"]:
        w(f"- {line}")
    w("")
    w("## Network log totals")
    w("")
    nl = R["network"]
    w("This session made no network call. Every call below was made by the first session of this job (the 24 "
      "listings, then the 272 FLEX test sheets, two calls each: a signed link from psi.nasa.gov, then the file "
      "from PSI's storage host; a fetch it had started was still running when this session began and finished "
      "the last sheets). Only FLEX test sheets were downloaded; no other raw file.")
    w("")
    w(f"All calls of this recount job are in `validation/raw_chain_recount_netlog.jsonl`: "
      f"{nl['calls']:,} calls from {nl['first_utc']} to {nl['last_utc']}, {nl['bytes_received']:,} bytes received, "
      f"{nl['bytes_sent']:,} bytes sent, {nl['errors']} errors; hosts {', '.join(nl['hosts'])}.")
    w("")
    w("| Kind | Calls | Bytes received | Bytes sent |")
    w("|---|---|---|---|")
    for k, v in nl["by_kind"].items():
        w(f"| {k} | {v['calls']:,} | {v['bytes_received']:,} | {v['bytes_sent']:,} |")
    w("")
    w(f"This run: {R['_meta']['fetch_calls_this_run']} sheet downloads (offline unless `--fetch`).")
    w("")
    w("Recomputed by a second AI session with code that does not import the pipeline; not checked by a person.")
    w("")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))


def notes_for(R):
    N = collections.defaultdict(list)
    A = R["A_placement"]
    for sid in ("lunar_habitat", "iss"):
        a = A["per_scenario"][sid]
        N["A"].append(f"- {sid}: cannot be placed by pair: {fmt(a['cannot_be_placed_pairs'])}; by investigation: "
                      f"{fmt(a['cannot_be_placed_by_investigation'])}. Inside by investigation: "
                      f"{fmt(a['inside_by_investigation'])}. Solid-fuel pairs: {fmt(a['solid_match_pairs'])}.")
        N["A"].append(f"- {sid}, if an oxidizer-stream test were never 'outside' (other reading of the order): "
                      f"{fmt(a['all_if_oxidizer_stream_took_precedence'])}. The fixtures follow 'outside first'.")
    c = A["claimed_scenario_tests"]
    N["A"].append(f"- Per test: {c['rows_compared']:,} (scenario, test) rows of `scenario_tests.csv` compared on "
                  f"`o2_match` and `pressure_match`; {len(c['disagreements'])} differ; "
                  f"{c['pairs_not_in_claimed_file']} recounted pairs are missing from the claimed file.")
    B = R["B_states"]
    N["B"].append(f"- `need_gap_states.csv`: {B['comparison']['rows_claimed']} rows, {B['comparison']['keys_claimed']} "
                  f"(scenario, need, role, variable) keys over {len(B['comparison']['scenarios_in_claimed_file'])} "
                  "scenarios; for every key the states sum to the in-scope and the counted totals, and every "
                  "key's states equal the states recomputed from `tests.csv`, `raw_columns.json` and `sources.json` "
                  "(README 'State rule').")
    N["B"].append(f"- P1 pressure, in-scope tests by state (counted tests in brackets): "
                  f"{fmt(B['P1_pressure_kpa_with_counted'])}.")
    N["B"].append(f"- `question_chain.csv`: {B['question_chain']}.")
    C = R["C_links"]
    N["C"].append("- Name matching. The PSI prefix (`PSI-69_Raw Data_`) is removed first. A PSI-69 file names a test "
                  "when its name carries the test's FLEX number (`FLEX-nnn`, `FLEX_nnn`, `FLEX nnn` or `FLEXnnn`, "
                  "any case) or its NASA identifier (any shape of the table's `FLEX Identifier` column: `dddFddd`, `dddRddd`, "
                  "`ddCALdd`, `[C, H or N]dd[H or M]ddd`; optionally followed by one camera letter A-D, as "
                  "`196F001A.zip`), with no letter or digit next to it. A PSI-159 file names a test when its name "
                  "carries the test point (`YYDDD`, an optional space, a letter, one or two digits). The second label "
                  "is the PSI folder path (subcategory): 'agrees' when every FLEX number and identifier (CFI-G: test "
                  "point) in it points to the same test, 'names no test' when it holds none, 'names another test' "
                  "otherwise.")
    fx = C["flex_17"]
    N["C"].append(f"- Two-label rule: the name number of a FLEX file is never taken alone. Of the {fx['files']} FLEX "
                  f"files, by the labels in the name: {fmt(fx['by_name_label'])}; by all four labels (name number, "
                  f"name identifier, folder number, folder identifier): {fmt(fx['by_two_label_state'])}; "
                  f"files whose only label is the name number: {fx['linked_by_name_number_alone']}. "
                  "The 47 archives carry the identifier in the name and sit in a folder that names no test "
                  "(one label). For these 17 tests the file number equals the table row (block D, read from the "
                  "sheets), but block D also shows 120 sheets whose file number is ahead of the table's FLEX Test #, "
                  "so a FLEX file number is a label only where a second label agrees.")
    N["C"].append(f"- Files in a folder that names another test: {len(fx['folder_names_another_test'])}, tests "
                  f"{', '.join(sorted({r['test'] for r in fx['folder_names_another_test']}))}, folder(s) "
                  + ", ".join(f"`{x}`" for x in sorted({r['folder'] for r in fx['folder_names_another_test']})) + ".")
    N["C"].append(f"- Per FLEX test (files, bytes, zip): " +
                  "; ".join(f"{k} {v['files']}, {v['bytes']:,}, {v['zip']}" for k, v in fx["per_test"].items()) + ".")
    N["C"].append(f"- CFI-G per test (files): {fmt(C['cfig_9']['per_test'])}; by extension: "
                  f"{fmt(C['cfig_9']['by_extension'])}. 26 tests: {C['lunar_26']['share_of_archive_bytes_pct']}% "
                  "of the archive's bytes.")
    N["C"].append(f"- FLEX table: {C['flex_table']['rows']} rows, {C['flex_table']['distinct_identifiers']} distinct "
                  f"identifiers; repeated: {fmt(C['flex_table']['identifiers_on_several_rows'])} (FLEX Test #), "
                  f"CSV lines {fmt(C['flex_table']['lines_of_repeated_identifiers'])}. Sheets numbered above row "
                  f"{C['flex_table']['max_test_number']}: {fmt(C['flex_sheets_in_listing']['numbered_above_table'])}.")
    N["C"].append(f"- FLEX-19: {C['flex_19']['small']['files']} small files ({C['flex_19']['small']['bytes']:,} bytes) "
                  f"and archives {fmt([f'{a} {b:,}' for a, b in C['flex_19']['archives']])}.")
    Dd = R["D_sheets"]
    N["D"].append("- Each sheet is read in full; lines `key = value` and `key: value` above `COMMENTS:` are kept "
                  "exactly as written (only surrounding blanks removed). A sheet is tied to a table row by "
                  "`CIR Test Number` equal to `FLEX Identifier` together with the test date (else oxygen and "
                  "pressure). Pressure agrees when the table's mmHg / 760 is within half a unit of the last digit "
                  "the sheet writes in atm; other numbers agree when they are the same decimal number "
                  "(`0.4` = `0.40`, `0` = `0.00`); `nan`, a blank or a dash are not comparable.")
    a = Dd["all"]
    N["D"].append(f"- All {a['sheets']} sheets ({a['bytes']:,} bytes; size on disk equals the listing for "
                  f"{a['disk_bytes_equal_listing']}): tied to one row {a['tied_to_one_row']} ({fmt(a['tie_by'])}); "
                  f"identifier not in the table {a['identifier_not_in_table']}; name number against tied row: "
                  f"{fmt(Dd['name_number_vs_tied_row'])}.")
    N["D"].append("- All sheets, field by field (agree / differ / not comparable): " +
                  "; ".join(f"{k}: {fmt(v)}" for k, v in a["field_agreement"].items()) + ".")
    N["D"].append("- All tied sheets, extinction diameter, table cell against sheet line `Dext (mm)`: " +
                  "; ".join(f"table {r['table_cell']}, sheet {r['sheet_line']}: {r['tests']}"
                            for r in a["dext_cross_table"]) + ".")
    l17 = Dd["lunar_17"]
    N["D"].append("- 17 lunar sheets, the cross-table with the values as written:")
    N["D"].append("")
    N["D"].append("  | Table cell | Sheet line `Dext (mm)` | Tests |")
    N["D"].append("  |---|---|---|")
    for r in l17["dext_cross_table"]:
        N["D"].append(f"  | {r['table_cell']} | {r['sheet_line']} | {'; '.join(r['which'])} |")
    N["D"].append("")
    N["D"].append("- 17 lunar sheets, fields that differ (sheet as written / table as written): " +
                  "; ".join(f"FLEX-{d['table_row']}: " + ", ".join(
                      f"{k} {v[0]} / {v[1]}" for k, v in d["as_written"].items()) for d in l17["differences"]) + ".")
    cw = Dd["crosswalk_where_name_number_differs"]
    if cw:
        off = collections.Counter(x["name_number"] - x["table_row"] for x in cw)
        nums = sorted(x["name_number"] for x in cw)
        runs, start = [], nums[0]
        for a, b in zip(nums, nums[1:] + [None]):
            if b is None or b != a + 1:
                runs.append(f"{start}" if start == a else f"{start} to {a}")
                start = b
        N["D"].append(f"- Crosswalk of the two FLEX numberings: the sheet's file number equals the FLEX Test # of the "
                      f"row it is tied to for {Dd['name_number_vs_tied_row'].get('equal', 0)} sheets. For "
                      f"{len(cw)} sheets (file numbers {', '.join(runs)}; some numbers have no sheet) the file "
                      "number is ahead of the row by "
                      + ", ".join(f"{k} ({v} sheets)" for k, v in sorted(off.items()))
                      + ". The full list is in the JSON (`crosswalk_where_name_number_differs`). So a FLEX file "
                      "number is not, in general, the table's FLEX Test #.")
    N["D"].append(f"- Sheets not tied to one row: {len(Dd['not_tied'])}: " +
                  "; ".join(f"{x['sheet'].replace('PSI-69_Raw Data_', '')} (identifier {x['identifier_inside']} is on "
                            f"rows {x['rows_with_identifier']}; sheet date and time {x['sheet_date_time']}; rows "
                            f"{fmt(x['rows_date_time'])})" for x in Dd["not_tied"]) +
                  ". The two rows write the same date and the same time, so no field of the tie rule separates "
                  "them and both sheets stay untied (listed, not resolved).")
    E = R["E_videos"]
    N["E"].append("- Rule as implemented (from `docs/video_design/design.md` section 4 and the rule table at its "
                  "end): two labels only, the NASA identifier in the file name and the PSI folder name. Outreach, "
                  "reference and engineering clips (categories Presentations, Reference Data, Engineering "
                  "Documents; names with `wo66...` or `Interviews`) are `none`. ACME (PSI-10, 20, 21, 22, 23, 159): "
                  "test points `YYDDDX#` in the name; the folder label is the first test point in the last folder, "
                  "else the one before; per-day tables (PSI-20 to 23) give day ties only. BASS-II: "
                  "`BASS_GMT{day}_SAMPLE_{n}_TEST_{test}` or `{test}-...`, folder `/{test}`; a run letter in the "
                  "name with the folder naming the test without it is one label; day or sample of the name not "
                  "fitting the tied row is `labels_disagree`. CFI: `F{ddd}{A-E}{nn}` against `CIR`. FLEX: a `FLEX Identifier` "
                  "of the table in the name or at the end of the leaf folder; the folder's FLEX number is never "
                  "used; 2013-2014 test points are `id_not_in_table`. BASS: name date minus one day against `Date`; "
                  "SAME-R: recording date against `Date`; SLICE: folder day or day range; SPICE: `GMT` day. A test "
                  "point that ties no row falls back to its day; an identifier or day not in the table is "
                  "`id_not_in_table`. A `labels_disagree` video is counted for every test one of its labels names.")
    N["E"].append(f"- Per investigation, six states in the order two agree / one / disagree / day only / not in table "
                  f"/ none: " + "; ".join(f"{k} {fmt(v)}" for k, v in E["per_investigation"].items()) + ".")
    N["E"].append("- `labels_disagree` files: " + "; ".join(
        f"`{x['file']}` ({', '.join(x['tests'])})" for x in E["labels_disagree_files"]) + ".")
    cc = E["claimed_per_file_comparison"]
    if cc:
        N["E"].append(f"- Per file against the claimed `video/data/video_links.csv` (compared, not used): same state "
                      f"{cc['same_state']:,} of {cc['files_compared']:,}; differing by pair: "
                      f"{fmt(cc['differences_by_pair'])}. The differing files are in the JSON.")
        diffs = cc["differences"]
        d26 = [d for d in diffs if d.get("investigation") == "PSI-26"]
        d39 = [d for d in diffs if d.get("investigation") == "PSI-39"]
        N["E"].append("- **Why the video fixtures that differ differ** (readings this recount keeps; none was changed "
                      "to reach a number):")
        N["E"].append(f"  1. BASS (PSI-26), {len(d26)} videos named `20130531 ...` in folder `2012_05_02`: the name "
                      "date minus one day is 30 May 2013. NASA's BASS table has no row whose `Date` is 5/30/2013; "
                      "its rows with `GMT` 150 (which is 30 May 2013) write `Date` 6/1/2013. This recount compares "
                      "with `Date` as written, so they are `id_not_in_table`; the claimed side reaches them through "
                      "`GMT` (`day_only`, 5 tests). The table's two columns disagree for these rows; the team does "
                      "not resolve it.")
        N["E"].append(f"  2. CFI (PSI-39), {len(d39)} videos whose name carries a CIR test point that is not a table "
                      "row while the folder's CIR test point is one (for example name `F180D04`, folder "
                      "`FLEX-1290 - F177D01`). This recount calls that `labels_disagree` (name and folder name "
                      "different test points); the claimed side falls back to the day of the name (4 `day_only`, "
                      "1 `id_not_in_table`). One more test, CFI-1225, then has a disagreeing video only.")
        N["E"].append("  3. A `labels_disagree` video is counted here for every test that one of its labels names; "
                      "the claimed side gives each such file one test. Only `_ISS_20090625_153031_256R002.mpg` "
                      "moves a count: it is counted for FLEX-13 (name) and FLEX-11 (folder), FLEX-11 has no other "
                      "video and is counted for S1, so S1 has 2 tests with a disagreeing video only, not 1 (and so "
                      "do the ISS and lunar S1 'outside' rows).")
        N["E"].append("  4. Scope: this recount has no `run` scope; the 3 SAME-R videos whose date and material "
                      "reach the two runs of one sample are `day` here (the date alone is used). Link states are "
                      "not affected.")
    Fi = R["F_inventory"]
    N["F"].append(f"- Team listing fetched {Fi['team_listing_fetched_utc']}; this recount's listing fetched "
                  f"{R['_meta']['listings_fetched_utc']}. Per investigation, files, bytes, rows, repeated rows, "
                  "row bytes and records beyond one per key were compared with `raw_inventory.json`; "
                  f"{len(Fi['investigations_that_differ'])} investigations differ" +
                  (": " + "; ".join(f"{r['investigation']} {fmt(r['differs_from_inventory'])}"
                                    for r in Fi["investigations_that_differ"]) if Fi["investigations_that_differ"] else
                   " (no drift in these figures between the two fetches).") +
                  f" Row bytes, repeats included: {Fi['totals']['listing_rows_bytes']:,} "
                  f"(inventory {Fi['inventory_totals']['listing_rows_bytes']:,}).")
    for k, v in R["frozen_files"].items():
        how = ("equal to the snapshot after reading the working tree's CRLF line ends as LF "
               "(Windows checkout with core.autocrlf; the bytes as written on disk give "
               f"{v['working_tree_bytes'][:12]}...)" if v["crlf_in_working_tree"] and v["unchanged"]
               else "equal to the snapshot" if v["unchanged"] else "DIFFERENT from the snapshot")
        N["O6"].append(f"- `{k}`: sha256 {v['with_crlf_as_lf']}, {how}.")
    return N


RUN_HISTORY = [
    "First offline run (2026-11-15): 59 of 71 fixtures reproduced. Four things were then corrected; in each the "
    "code did not do what its own rule, as written in this file and in the design, says. No rule was added or "
    "loosened to reach a number, and the fixtures that still differ are explained under E.",
    "FLEX test points were read in one shape only (`ddd[F|R]ddd`), although the rule ties the name and the folder "
    "to the `FLEX Identifier` column, which also holds `ddCALdd` and `[C|H|N]dd[H|M]ddd` identifiers. Now every "
    "shape of that column is read. Effect: 5 PSI-69 videos in folders that end with such an identifier (for "
    "example `FLEX 116_01_Sep_2010_MeOH_C11M401`) moved from `none` to `one_label`; the figures of block C did not "
    "change.",
    "An ACME or CFI-G test point written with a `_n` suffix was cut to its base, although the CFI-G table lists "
    "`21196M2_1` as a test of its own. The suffix is now kept where the table lists the suffixed form. Effect: 1 "
    "video moved from test CFIG-I-21196M2 to CFIG-I-21196M2_1 (tests with a two-labels video 462 to 463); no link "
    "state and no figure of block C changed.",
    "Sheet against table: the test time was compared as text, so `05:02:52 (GMT)` and `5:02:52` differed. It is "
    "now compared as hours, minutes and seconds. No fixture uses the time.",
    "The sha256 of the four frozen files was taken of the working-tree bytes, which on this Windows checkout "
    "(git `core.autocrlf`) end lines with CRLF. The check now also hashes the bytes with CRLF read as LF, which "
    "are the committed bytes, and prints both.",
]

NOT_COVERED = [
    "Nothing here reads a raw file other than the 272 FLEX test sheets; no archive, video or document was opened.",
    "Placement uses the table values of `tests.csv` only; no raw value enters any count (as the design requires).",
    "Link fixtures (C) cover the 26 tests inside the lunar ranges (17 FLEX, 9 CFI-G) only; no link total for other "
    "tests or investigations, and no claim that a file which names a test holds what a question needs.",
    "The ISS screen's link totals, pile 2 reading order (`reading_order.csv`) and the cost ladder (reading steps "
    "and their unit costs) are not recounted.",
    "`question_chain.csv` is not in the repository, so its sums against `need_gap_states.csv` are not checked.",
    "Video: the scope split of 'day' into a test day, a folder of several days and runs, the BASS-II clip kinds, "
    "the ISS P1 shortlist (49 files), the transcriptions (`O9.csv`) and the BASS-II day/sample pairs are not "
    "recounted.",
    "The FLEX sheet comparison says what the sheet and the table write; it does not say which is right, nor what "
    "`nan`, `0.00`, a blank or a dash mean.",
    "No person has checked any figure of this recount.",
]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch", action="store_true",
                    help="download the PSI-69 FLEX test sheets that are missing, then recount")
    args = ap.parse_args()

    invs = manifest_investigations()
    missing = [a for a, _ in invs if not os.path.exists(os.path.join(LISTING_DIR, f"{a}.json"))]
    if missing:
        raise SystemExit(f"listings missing: {missing}. This script does not fetch listings "
                         "(outside the approved download scope); save them first.")
    listings = {a: read_listing(a) for a, _ in invs}
    fetched = 0
    if args.fetch:
        sheets = sorted((f for f in listings["PSI-69"]["files"] if SHEET_RE.search(f["key_name"])),
                        key=lambda f: f["key_name"])
        fetched = fetch_sheets(sheets)

    tests = read_csv(os.path.join(PIPE_DIR, "tests.csv"))
    need_tests = read_csv(os.path.join(PIPE_DIR, "need_tests.csv"))
    scenarios = spec("scenarios.json")["scenarios"]
    raw_kinds = spec("raw_kinds.json")
    tables = {fn: read_table(fn) for fn in sorted(os.listdir(TABLE_DIR)) if fn.endswith(".csv")}

    R = {"_meta": {"made_by": "AI-generated (Claude Code), second session independent of the pipeline; "
                              "not checked by a person",
                   "run_date": time.strftime("%Y-%m-%d"),
                   "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "script": "validation/raw_chain_recount.py",
                   "fetch_calls_this_run": fetched,
                   "listings": {a: {"sha256": L["sha256"], "bytes": L["raw_bytes"]} for a, L in listings.items()},
                   "table_encodings": {fn: rows[0]["_enc"] for fn, rows in tables.items() if rows},
                   "tests_csv_source_row_check": row_index_check(tests, tables)}}
    nl = netlog_totals()
    listing_calls = []
    if os.path.exists(NETLOG):
        with open(NETLOG, encoding="utf-8") as fh:
            listing_calls = [json.loads(x)["at_utc"] for x in fh if '"listing ' in x]
    R["_meta"]["listings_fetched_utc"] = (f"{min(listing_calls)} to {max(listing_calls)}"
                                          if listing_calls else "not in the network log")
    R["network"] = nl

    # A
    placement, per_test, cmpA = recount_placement(
        tests, scenarios, read_csv(os.path.join(PIPE_DIR, "scenario_tests.csv")))
    R["A_placement"] = {"per_scenario": placement, "claimed_scenario_tests": cmpA}
    # B
    mine = recount_states(tests, spec("needs.json"), spec("raw_columns.json"), spec("sources.json"), need_tests)
    cmpB = compare_states(mine, read_csv(os.path.join(PIPE_DIR, "need_gap_states.csv")),
                          [s["id"] for s in scenarios])
    qc = os.path.join(PIPE_DIR, "question_chain.csv")
    p1 = mine[("P1", "required", "pressure_kpa")]
    R["B_states"] = {"comparison": cmpB, "P1_pressure_kpa": state_short(p1["states"]),
                     "P1_pressure_kpa_with_counted": p1["states"],
                     "question_chain": ("present; not compared by this version" if os.path.exists(qc)
                                        else "not in data/pipeline/ (not compared)"),
                     "recomputed": {"|".join(k): v for k, v in mine.items()}}
    # C
    C, flex_files, cfig_files = recount_links(listings, tables, tests, per_test, raw_kinds)
    R["C_links"] = C
    R["C_link_files"] = {"flex": flex_files, "cfig": cfig_files}
    # D
    lunar_nums = {int(k.split("-")[1]) for k in C["flex_17"]["per_test"]}
    R["D_sheets"] = recount_sheets(listings, tables, lunar_nums)
    # E
    R["E_videos"] = recount_videos(listings, tables, tests, need_tests, per_test, raw_kinds)
    # F
    R["F_inventory"] = recount_inventory(listings, load_json(os.path.join(PIPE_DIR, "raw_inventory.json")))
    R["frozen_files"] = frozen_files()

    fixtures = build_fixtures(R)
    R["fixtures"] = fixtures
    R["fixtures_summary"] = {"total": len(fixtures), "reproduced": sum(f["match"] for f in fixtures),
                             "not_reproduced": [f["what"] for f in fixtures if not f["match"]]}
    R["not_covered"] = NOT_COVERED
    R["notes"] = notes_for(R)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(R, fh, ensure_ascii=False, indent=1, default=sorted)
        fh.write("\n")
    write_report(R, fixtures, OUT_MD)
    print(f"fixtures reproduced: {R['fixtures_summary']['reproduced']} of {len(fixtures)}")
    for f in fixtures:
        if not f["match"]:
            print(f"  NOT {f['block']} {f['what']}: expected {fmt(f['expected'])}, recounted {fmt(f['recounted'])}")


if __name__ == "__main__":
    main()
