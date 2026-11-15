# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""What the names of the PSI raw files say: ties of every listed file to a
row of an experimental table, by the identifier its name carries.

For every investigation of pipeline/spec/raw_names.json this script applies
the ordered name rules of the spec to every file of the saved PSI listing
(data/psi/file_listings/, git-ignored) and writes, in data/pipeline/:

  raw_file_groups.csv      investigation x PSI category x kind x name pattern
                           x suffix code: files, bytes, ties by level
  test_files.csv           test (or table row) x link level x kind x suffix
                           code: files and bytes tied by name (a file tied
                           to several rows counts for each row)
  name_tie_alternatives.csv  files where another rule or match would tie
                           other rows than the deciding first match
  raw_layers_summary.json  per investigation and overall: what the names,
                           the sampled structure, the archive directories and
                           the values read cover, by files and by bytes

It reads data/pipeline/archive_members_sample.csv (written by
pipeline/zip_directory.py) for the archive-directory layer of the summary.

A tie by name means that the name carries the identifier of that test (a
cell of the experimental table, equal by the transform the spec names); it
does not mean that the content of the file was checked. No file is opened or
downloaded here. When the listings are absent the script says so and leaves
the committed outputs untouched.

The kind of a file is the kind of raw_inventory.py (spec/raw_kinds.json), so
the totals per investigation and kind equal data/pipeline/raw_inventory.json.

Usage: python3 pipeline/raw_names.py
Source: NASA Physical Sciences Informatics (PSI), https://psi.nasa.gov/
"""
import calendar
import csv
import datetime
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import raw_inventory  # noqa: E402  (kind rules and listing reader)

SPEC = os.path.join(HERE, "spec", "raw_names.json")
KINDS = os.path.join(HERE, "spec", "raw_kinds.json")
LISTINGS = os.path.join(ROOT, "data", "psi", "file_listings")
TABLES = os.path.join(ROOT, "data", "psi", "experimental_tables")
OUT = os.path.join(ROOT, "data", "pipeline")
ARCHIVE_TOTALS = os.path.join(OUT, "archive_summary_totals.json")
GENERATED_BY = "AI-generated (Claude Code), 2026-11-14. Not human-reviewed."
FORBIDDEN = re.compile(r"\b(safe|safely|acceptable|sufficient|sufficiently|representative|proven|proves)\b", re.I)
LEVELS = ("test", "day_or_session", "none")
MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_abbr) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_name) if m})
MONTHS["sept"] = 9


# ------------------------------------------------------------------ helpers
def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


NASA_TEXT = ("psi_category", "name_pattern", "suffix_code", "example_name", "archive_name", "member_name_pattern", "name")


def team_text(row):
    """The text of a row that the team wrote: names and categories as PSI
    gives them and quotes of NASA documents are left out."""
    parts = []
    for k, v in row.items():
        if k in NASA_TEXT:
            continue
        parts.append(re.sub(r'"[^"]*"', "", str(v)))
    return " ".join(parts)


def write_csv(path, cols, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, cols, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    text = buf.getvalue()
    if any(FORBIDDEN.search(team_text(r)) for r in rows):
        sys.exit("raw_names: forbidden word in %s: %s" % (os.path.basename(path), sorted(set(FORBIDDEN.findall(text)))))
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def write_json(path, obj):
    text = json.dumps(obj, ensure_ascii=False, indent=1) + "\n"
    if FORBIDDEN.search(re.sub(r'\\"[^"\\]*\\"', "", text)):
        sys.exit("raw_names: forbidden word in %s" % os.path.basename(path))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def psi_key(inv):
    return int(inv.split("-")[1])


def ingest(file_name):
    """(header, [(source_row, {column: cell})]) as run.py reads a table: the
    header is source row 1, cells are stripped, blank rows are left out."""
    raw = open(os.path.join(TABLES, file_name), "rb").read().decode("utf-8-sig", "replace")
    records = [[c.strip() for c in r] for r in csv.reader(io.StringIO(raw))]
    header = records[0]
    rows = [(i + 1, dict(zip(header, (r + [""] * len(header))[:len(header)])))
            for i, r in enumerate(records) if i > 0 and any(r)]
    return header, rows


# --------------------------------------------------------------- transforms
def _iso(y, m, d):
    try:
        return datetime.date(y, m, d).isoformat()
    except ValueError:
        return None


def parse_date(text):
    """ISO date of a table cell written m/d/yyyy, d-Mon-yy, yyyy-MON-dd (a
    leading date followed by words), or yyyy-mm-dd; None otherwise."""
    t = text.strip()
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", t)
    if m:
        return _iso(int(m.group(3)), int(m.group(1)), int(m.group(2)))
    m = re.match(r"^(\d{1,2})-([A-Za-z]{3})-(\d{2})$", t)
    if m and m.group(2).lower() in MONTHS:
        return _iso(2000 + int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
    m = re.match(r"^(\d{4})-([A-Za-z]{3})-(\d{2})\b", t)
    if m and m.group(2).lower() in MONTHS:
        return _iso(int(m.group(1)), MONTHS[m.group(2).lower()], int(m.group(3)))
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", t)
    if m:
        return _iso(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def month_number(text):
    t = text.strip().rstrip(".").lower()
    if t.isdigit():
        return int(t)
    return MONTHS.get(t)


def key_value(tr, s):
    """The value a name token stands for under the key transform tr."""
    s = s.strip()
    if tr == "text":
        return s
    if tr == "upper":
        return s.upper()
    if tr == "nospace_upper":
        return re.sub(r"\s+", "", s).upper()
    if tr == "int":
        return str(int(s)) if s.isdigit() else None
    if tr == "cir":
        u = s.upper()
        return u if u.startswith("F") else "F" + u
    if tr == "yyddd_date":
        if not re.fullmatch(r"\d{5}", s):
            return None
        y, d = 2000 + int(s[:2]), int(s[2:])
        if not 1 <= d <= (366 if calendar.isleap(y) else 365):
            return None
        return (datetime.date(y, 1, 1) + datetime.timedelta(days=d - 1)).isoformat()
    if tr == "ymd_date":
        d = re.sub(r"\D", "", s)
        return _iso(int(d[:4]), int(d[4:6]), int(d[6:8])) if len(d) == 8 else None
    if tr == "ymd_dmon":
        d = re.sub(r"\D", "", s)
        if len(d) != 8 or not _iso(int(d[:4]), int(d[4:6]), int(d[6:8])):
            return None
        return "%d-%s" % (int(d[6:8]), calendar.month_abbr[int(d[4:6])].lower())
    if tr == "ymd_yyddd":
        v = key_value("ymd_date", s)
        if not v:
            return None
        d = datetime.date.fromisoformat(v)
        return "%02d%03d" % (d.year % 100, d.timetuple().tm_yday)
    if tr == "upper_prefix6":
        return re.sub(r"[^A-Za-z]", "", s).upper()[:6] or None
    if tr == "dmony_date":
        m = re.fullmatch(r"(\d{1,2})([A-Za-z]{3})(\d{4})", s)
        if not m or m.group(2).lower() not in MONTHS:
            return None
        return _iso(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
    raise SystemExit("raw_names: unknown key transform %r" % tr)


def cell_values(tr, cells, lookup=None):
    """The set of values the cells of one table row stand for under the cell
    transform tr (cells: the cells of the columns of the field, in order).
    Transforms over several columns (ymd_cols, each_upper) come before the
    test for a blank first cell: a blank 'Camera 1' cell does not hide the
    'Camera 2' cell of the same row. lookup: the pairs of a 'lookups' entry
    of the investigation, for lookup_date."""
    c = cells[0].strip() if cells else ""
    if tr == "each_upper":
        return {x.strip().upper() for x in cells if x.strip()}
    if tr == "ymd_cols":
        y, mo, d = (x.strip() for x in cells)
        if not (y.isdigit() and d.isdigit()) or month_number(mo) is None:
            return set()
        v = _iso(int(y), month_number(mo), int(d))
        return {v} if v else set()
    if not c:
        return set()
    if tr == "text":
        return {c}
    if tr == "upper":
        return {c.upper()}
    if tr == "nospace_upper":
        return {re.sub(r"\s+", "", c).upper()}
    if tr == "first5":
        return {re.sub(r"\s+", "", c)[:5]}
    if tr == "int":
        return {str(int(c))} if c.isdigit() else set()
    if tr == "digits_prefix":
        m = re.match(r"\d+", c)
        return {str(int(m.group(0)))} if m else set()
    if tr == "cir":
        u = c.upper()
        return {u if u.startswith("F") else "F" + u}
    if tr == "date":
        v = parse_date(c)
        return {v} if v else set()
    if tr == "doy":
        v = parse_date(c)
        return {str(datetime.date.fromisoformat(v).timetuple().tm_yday)} if v else set()
    if tr == "dmon":
        m = re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})", c)
        return {"%d-%s" % (int(m.group(1)), m.group(2).lower())} if m else set()
    if tr == "gmt_int":
        m = re.match(r"GMT\s*(\d+)", c)
        return {str(int(m.group(1)))} if m else set()
    if tr == "lookup_date":
        v = parse_date(c)
        return set(lookup.get(v, [])) if v else set()
    if tr == "after_hyphen":
        return {c.split("-", 1)[1].strip()} if "-" in c else set()
    if tr == "upper_prefix6":
        v = re.sub(r"[^A-Za-z]", "", c).upper()[:6]
        return {v} if v else set()
    if tr == "slash_parts_upper":
        return {p.strip().upper() for p in c.split("/") if p.strip()}
    raise SystemExit("raw_names: unknown cell transform %r" % tr)


# -------------------------------------------------------------------- rules
class Investigation:
    def __init__(self, inv, spec, tests):
        self.id = inv
        self.spec = spec
        self.rows = []          # (table file, source row, cells)
        for t in spec["tables"]:
            _, rows = ingest(t)
            self.rows += [(t, n, r) for n, r in rows]
        self.test_of = {(t["source_file"], int(t["source_row"])): t["test_id"]
                        for t in tests if t["investigation_id"] == inv}
        self.rules = []
        for r in spec["rules"]:
            flags = re.I if r.get("ignore_case") else 0
            self.rules.append({**r, "rx": re.compile(r["pattern"], flags),
                               "name_rx": re.compile(r.get("name_must_match") or "", flags)})
        self.order = [(t, n) for t, n, _ in self.rows]
        self.suffixes = [{**s, "rx": re.compile(s["pattern"], re.I if s.get("ignore_case") else 0)}
                         for s in spec["suffix_codes"]]
        # value sets per (rule, field) and row, computed once
        self.values = {}
        for r in self.rules:
            for g, fld in r["fields"].items():
                for t, n, cells in self.rows:
                    if r.get("tables") and t not in r["tables"]:
                        continue
                    if any(c not in cells for c in fld["columns"]):
                        raise SystemExit("raw_names: %s %s: column not in %s: %s" % (self.id, r["id"], t, fld["columns"]))
                    lk = spec.get("lookups", {})[fld["lookup"]]["pairs"] if fld.get("lookup") else None
                    self.values[(r["id"], g, t, n)] = cell_values(fld["cell"], [cells[c] for c in fld["columns"]], lk)

    def row_key(self, t, n):
        return "%s#row%d" % (t, n)

    def tie(self, name, folder, category, kind):
        """(rule id, level, [(table, row)]) of the first rule that ties the
        file to at least one row; (None, 'none', []) if no rule does."""
        ties = self.all_ties(name, folder, category, kind)
        return ties[0] if ties else (None, "none", [])

    def all_ties(self, name, folder, category, kind):
        """Every (rule id, level, [(table, row)]) that a match of a rule gives,
        in rule order and, within a rule, from left to right."""
        out = []
        for r in self.rules:
            if r.get("categories") and category not in r["categories"]:
                continue
            if kind in r.get("exclude_kinds", []):
                continue
            if r.get("name_must_match") and not r["name_rx"].search(name):
                continue
            target = folder if r["where"] == "folder" else name
            for m in r["rx"].finditer(target):
                keys = {}
                for g, fld in r["fields"].items():
                    if m.group(g) is not None:
                        keys[g] = key_value(fld["key"], m.group(g))
                if not keys or any(v is None for v in keys.values()):
                    continue
                cand = [(t, n) for t, n, cells in self.rows
                        if (not r.get("tables") or t in r["tables"])
                        and all(re.search(f["regex"], cells[f["column"]]) for f in r.get("row_filter", []))]
                if r.get("mode") == "each_field_ties_union":
                    per = [{(t, n) for t, n in cand if keys[g] in self.values[(r["id"], g, t, n)]} for g in keys]
                    rows = sorted(set().union(*per), key=self.order.index) if all(per) else []
                else:
                    rows = [(t, n) for t, n in cand if all(keys[g] in self.values[(r["id"], g, t, n)] for g in keys)]
                if rows:
                    level = r["level"]
                    if len(rows) > 1 and r.get("level_if_several_rows"):
                        level = r["level_if_several_rows"]
                    out.append((r["id"], level, rows))
        return out

    def suffix(self, name):
        for s in self.suffixes:
            if s["rx"].search(name):
                return s
        return None


def name_pattern(name):
    """The name with every token that holds a digit replaced by <ID> (tokens
    are split at spaces, underscores, hyphens, dots, brackets and commas);
    the extension (up to five letters or digits after the last dot) is kept."""
    m = re.match(r"^(.*?)(\.[A-Za-z0-9]{1,5})?$", name)
    return re.sub(r"[^\s_\-.()\[\],]*\d[^\s_\-.()\[\],]*", "<ID>", m.group(1)) + (m.group(2) or "")


def listing_files(inv, kinds):
    """Every file of the saved listing once (as raw_inventory.read_listing
    counts them), with its kind, its name without the PSI prefix ('base'),
    its PSI subcategory path ('folder') and its file id."""
    path = os.path.join(LISTINGS, inv + ".json")
    files, _, _, _ = raw_inventory.read_listing(path)
    rows = []
    raw_inventory.walk(read_json(path), [], rows)
    seen, recs = set(), []
    for _, rec in rows:
        ident = rec.get("id") or (str(rec.get("key", "")), rec.get("version"))
        if ident not in seen:
            seen.add(ident)
            recs.append(rec)
    if len(recs) != len(files):
        raise SystemExit("raw_names: %s: listing rows and files differ" % inv)
    result = []
    for f, rec in zip(files, recs):
        kind = kinds.classify(f)[0]
        base = f["name"]
        for template in kinds.spec["strip_prefix"]:
            stripped, n = re.subn(template.replace("{category}", re.escape(f["category"])), "", base, count=1)
            if n:
                base = stripped
                break
        result.append({"name": f["name"], "base": base, "category": f["category"], "bytes": f["bytes"] or 0,
                       "kind": kind, "folder": rec.get("subcategory") or "", "file_id": rec.get("id") or ""})
    return result


# ------------------------------------------------------------------ outputs
def link_files(spec, tests, kinds):
    """Per investigation: one record per listed file with its tie."""
    out = {}
    for inv in sorted(spec["investigations"], key=psi_key):
        I = Investigation(inv, spec["investigations"][inv], tests)
        recs = []
        for f in listing_files(inv, kinds):
            ties = I.all_ties(f["base"], f["folder"], f["category"], f["kind"])
            rule, level, rows = ties[0] if ties else (None, "none", [])
            others = []
            for t in ties[1:]:
                # a tie whose rows contain, or are contained in, the deciding
                # rows (a test and its day) agrees with it; only others count
                o, d = set(t[2]), set(rows)
                if not (o <= d or d <= o) and t not in others:
                    others.append(t)
            s = I.suffix(f["base"])
            recs.append({**f, "rule": rule or "", "level": level,
                         "rows": [I.row_key(t, n) for t, n in rows],
                         "tests": sorted({I.test_of[(t, n)] for t, n in rows if (t, n) in I.test_of}),
                         "suffix": s["code"] if s else "(no suffix code)",
                         "suffix_meaning": meaning_text(s),
                         "quote_relation": (s.get("meaning") or {}).get("quote_relation", "") if s else "",
                         "other_ties": [(o[0], o[1], [I.row_key(t, n) for t, n in o[2]]) for o in others],
                         "pattern": name_pattern(f["base"])})
        out[inv] = (I, recs)
    return out


QUOTE_LEAD = {"states_meaning": "quoted",
              "expansion_only": "quoted, expands the abbreviation only and does not say what these files hold",
              "about_another_thing": "quoted, about a related thing, not about what these files hold",
              "name_form_only": "quoted, gives the form of the name only, not what these files hold"}


def meaning_text(s):
    if not s:
        return ""
    m = s.get("meaning")
    return '%s: "%s" (%s, PSI file id %s, %s)' % (QUOTE_LEAD[m["quote_relation"]], m["quote"], m["document"],
                                                  m["file_id"], m["where"]) if m else "no stated meaning found"


def group_rows(linked):
    rows = []
    for inv, (I, recs) in linked.items():
        groups = {}
        for r in recs:
            k = (r["category"], r["kind"], r["pattern"], r["suffix"])
            groups.setdefault(k, []).append(r)
        for k in sorted(groups):
            g = sorted(groups[k], key=lambda r: (r["base"], r["file_id"]))
            by = {lv: [r for r in g if r["level"] == lv] for lv in LEVELS}
            ex = g[0]
            rows.append({"investigation_id": inv, "psi_category": k[0], "kind": k[1], "name_pattern": k[2],
                         "suffix_code": k[3], "files": len(g), "bytes": sum(r["bytes"] for r in g),
                         "link_levels": ";".join(lv for lv in LEVELS if by[lv]),
                         "rules": ";".join(sorted({r["rule"] for r in g if r["rule"]})),
                         "files_tied_to_a_test": len(by["test"]), "bytes_tied_to_a_test": sum(r["bytes"] for r in by["test"]),
                         "files_tied_to_a_day_or_session": len(by["day_or_session"]),
                         "bytes_tied_to_a_day_or_session": sum(r["bytes"] for r in by["day_or_session"]),
                         "files_not_tied": len(by["none"]), "bytes_not_tied": sum(r["bytes"] for r in by["none"]),
                         "distinct_tests_reached": len({t for r in by["test"] for t in r["tests"]}),
                         "distinct_table_rows_reached": len({x for r in g for x in r["rows"]}),
                         "suffix_meaning": ex["suffix_meaning"],
                         "example_name": ex["name"], "example_file_id": ex["file_id"],
                         "quote_relation": ex["quote_relation"],
                         "files_with_another_tie_by_name": sum(1 for r in g if r["other_ties"]),
                         "files_tied_to_several_rows": sum(1 for r in g if len(r["rows"]) > 1)})
    return rows


def test_file_rows(linked):
    rows = []
    for inv, (I, recs) in linked.items():
        acc = {}
        for r in recs:
            if r["level"] == "none":
                continue
            for rk in r["rows"]:
                t, n = rk.rsplit("#row", 1)
                tid = I.test_of.get((t, int(n)), "")
                k = (tid, rk, r["level"], r["kind"], r["suffix"])
                a = acc.setdefault(k, [0, 0, 0])
                a[0] += 1
                a[1] += r["bytes"]
                a[2] += len(r["rows"]) > 1
        for k in sorted(acc, key=lambda k: (k[1].rsplit("#row", 1)[0], int(k[1].rsplit("#row", 1)[1]), k[2], k[3], k[4])):
            rows.append({"investigation_id": inv, "test_id": k[0], "table_row_key": k[1], "link_level": k[2],
                         "kind": k[3], "suffix_code": k[4], "files": acc[k][0], "bytes": acc[k][1],
                         "files_also_counted_for_another_row": acc[k][2]})
    return rows


def alternative_rows(linked):
    """One row per file and other tie: files where another rule, or another
    match of the same rule, would tie a set of rows that neither contains nor
    is contained in the rows of the deciding (first) tie."""
    rows = []
    for inv, (I, recs) in linked.items():
        for r in sorted(recs, key=lambda r: (r["base"], r["file_id"])):
            for rule, level, rks in r["other_ties"]:
                rows.append({"investigation_id": inv, "file_id": r["file_id"], "name": r["name"], "kind": r["kind"],
                             "bytes": r["bytes"], "deciding_rule": r["rule"], "deciding_level": r["level"],
                             "deciding_rows": ";".join(r["rows"]), "other_rule": rule, "other_level": level,
                             "other_rows": ";".join(rks)})
    return rows


def suffix_entry_use(spec, linked):
    """Per investigation, the suffix entries and how many files each one is
    the code of; entries that are the code of no file are listed (they stay
    in the spec), with whether their pattern is found in a name whose code is
    an earlier entry."""
    out = {"entries": 0, "entries_with_a_quote": {}, "entries_without_a_quote": 0, "entries_matching_no_file": [],
           "files_by_quote_relation": {}}
    for inv, (I, recs) in linked.items():
        n = {}
        for r in recs:
            n[r["suffix"]] = n.get(r["suffix"], 0) + 1
            rel = r["quote_relation"] or ("no quote" if r["suffix"] != "(no suffix code)" else "no suffix code")
            out["files_by_quote_relation"][rel] = out["files_by_quote_relation"].get(rel, 0) + 1
        for e in spec["investigations"][inv]["suffix_codes"]:
            out["entries"] += 1
            m = e.get("meaning")
            if m:
                out["entries_with_a_quote"][m["quote_relation"]] = out["entries_with_a_quote"].get(m["quote_relation"], 0) + 1
            else:
                out["entries_without_a_quote"] += 1
            if not n.get(e["code"]):
                rx = re.compile(e["pattern"], re.I if e.get("ignore_case") else 0)
                out["entries_matching_no_file"].append({"investigation_id": inv, "code": e["code"], "has_quote": bool(m),
                                                        "pattern_found_in_a_name_of_an_earlier_entry": any(
                                                            rx.search(r["base"]) for r in recs)})
    out["entries_with_a_quote"] = dict(sorted(out["entries_with_a_quote"].items()))
    out["files_by_quote_relation"] = dict(sorted(out["files_by_quote_relation"].items()))
    return out


def opened_for_structure(raw_columns):
    """{investigation: {file id: bytes in the listing}} of the sample files
    that spec/raw_columns.json names (groups[].samples and the sample file of
    each entry): files opened for their headers, keys or labels."""
    out = {}
    for i in raw_columns["investigations"]:
        o = out.setdefault(i["investigation_id"], {})
        for g in i.get("groups", []):
            for smp in g.get("samples", []):
                o[smp["psi_file_id"]] = smp["bytes_listing"]
        for e in i.get("entries", []):
            o.setdefault(e["sample_file_id"], e["sample_bytes"])
    return out


def summary(spec, linked, raw_columns, raw_values, zip_sample):
    S = spec["summary"]
    opened = opened_for_structure(raw_columns)
    values = {}
    for r in raw_values:
        inv = r["investigation_id"]
        values.setdefault(inv, {})[r["psi_file_id"]] = int(r["bytes"])
    zips = {}
    for z in zip_sample:
        zips.setdefault(z["investigation_id"], {})[z["archive_file_id"]] = (int(z["archive_bytes"]), int(z["bytes_fetched"]))
    invs = []
    tot = None
    for inv, (I, recs) in linked.items():
        e = {"investigation_id": inv, "files": len(recs), "bytes": sum(r["bytes"] for r in recs)}
        e["names"] = {lv: {"files": sum(1 for r in recs if r["level"] == lv),
                           "bytes": sum(r["bytes"] for r in recs if r["level"] == lv)} for lv in LEVELS}
        kinds = sorted({r["kind"] for r in recs})
        e["names_by_kind"] = {k: {lv: {"files": sum(1 for r in recs if r["level"] == lv and r["kind"] == k),
                                       "bytes": sum(r["bytes"] for r in recs if r["level"] == lv and r["kind"] == k)}
                                  for lv in LEVELS} for k in kinds}
        e["tests_reached_by_name"] = len({t for r in recs if r["level"] == "test" for t in r["tests"]})
        e["table_rows_reached_by_name"] = len({x for r in recs if r["level"] != "none" for x in r["rows"]})
        e["files_tied_to_several_rows"] = sum(1 for r in recs if len(r["rows"]) > 1)
        e["files_with_another_tie_by_name"] = sum(1 for r in recs if r["other_ties"])
        o = opened.get(inv, {})
        e["opened_for_structure"] = {"files": len(o), "bytes": sum(o.values())}
        v = values.get(inv, {})
        e["values_read"] = {"files": len(v), "bytes": sum(v.values())}
        arch = [r for r in recs if r["kind"] == "archive"]
        zz = zips.get(inv, {})
        e["archive_directories_listed"] = {"archives": len(zz), "archives_in_listing": len(arch),
                                           "bytes_of_those_archives": sum(a for a, _ in zz.values()),
                                           "bytes_fetched": sum(b for _, b in zz.values()),
                                           "bytes_of_all_archives": sum(r["bytes"] for r in arch)}
        invs.append(e)
    overall = {"files": sum(e["files"] for e in invs), "bytes": sum(e["bytes"] for e in invs)}
    overall["names"] = {lv: {"files": sum(e["names"][lv]["files"] for e in invs),
                             "bytes": sum(e["names"][lv]["bytes"] for e in invs)} for lv in LEVELS}
    kinds = sorted({k for e in invs for k in e["names_by_kind"]})
    overall["names_by_kind"] = {k: {lv: {"files": sum(e["names_by_kind"].get(k, {}).get(lv, {}).get("files", 0) for e in invs),
                                         "bytes": sum(e["names_by_kind"].get(k, {}).get(lv, {}).get("bytes", 0) for e in invs)}
                                    for lv in LEVELS} for k in kinds}
    overall["tests_reached_by_name"] = sum(e["tests_reached_by_name"] for e in invs)
    for key in ("files_tied_to_several_rows", "files_with_another_tie_by_name"):
        overall[key] = sum(e[key] for e in invs)
    overall["suffix_codes"] = suffix_entry_use(spec, linked)
    for key in ("opened_for_structure", "values_read"):
        overall[key] = {"files": sum(e[key]["files"] for e in invs), "bytes": sum(e[key]["bytes"] for e in invs)}
    overall["archive_directories_listed"] = {k: sum(e["archive_directories_listed"][k] for e in invs)
                                             for k in invs[0]["archive_directories_listed"]}
    allz = read_json(ARCHIVE_TOTALS) if os.path.exists(ARCHIVE_TOTALS) else None
    if allz:    # added 2026-11-15: totals of archive_summary.py (member lists of all listed archives)
        keys = ("archives_in_listing", "archive_bytes_in_listing", "archives_listed", "bytes_of_listed_archives",
                "bytes_fetched", "members", "directories", "members_by_class", "uncompressed_bytes")
        for e in invs:
            b = allz["investigations"].get(e["investigation_id"])
            if b:
                e["archive_directories_all"] = {k: b[k] for k in keys}
        overall["archive_directories_all"] = dict({k: allz["overall"][k] for k in keys},
                                                  archives_not_listed=allz["overall"]["archives_not_listed"],
                                                  not_listed_by_reason=allz["overall"]["not_listed_by_reason"],
                                                  source="data/pipeline/archive_summary_totals.json")
    o = overall
    sent = [S["tie_by_name"],
            S["names"].format(files=o["files"], t=o["names"]["test"]["files"], d=o["names"]["day_or_session"]["files"],
                              n=o["names"]["none"]["files"]),
            S["structure"].format(files=o["opened_for_structure"]["files"]),
            S["values"].format(files=o["values_read"]["files"]),
            S["archives"].format(a=o["archive_directories_listed"]["archives"],
                                 all=o["archive_directories_listed"]["archives_in_listing"],
                                 f=o["archive_directories_listed"]["bytes_fetched"],
                                 b=o["archive_directories_listed"]["bytes_of_those_archives"]),
            S["rank"], S["not_content"]]
    meta = {"generated_by": GENERATED_BY, "written_by": "pipeline/raw_names.py",
            "inputs": ["data/psi/file_listings/ (git-ignored)", "data/psi/experimental_tables/", "data/pipeline/tests.csv",
                       "pipeline/spec/raw_names.json", "pipeline/spec/raw_kinds.json", "pipeline/spec/raw_columns.json",
                       "data/pipeline/raw_values.csv", "data/pipeline/archive_members_sample.csv"],
            "layers": S["layers"], "levels": S["levels"], "units": S["units"],
            "archive_sample": spec["archive_sample_note"],
            "quote_relation": spec["_meta"]["quote_relation"],
            "several_rows_and_other_ties": spec["_meta"]["several_rows_and_other_ties"],
            "open_points": spec["_meta"]["open_points"]}
    doc = {"_meta": meta, "sentences": sent, "overall": overall, "investigations": invs}
    if allz:
        doc["sentences_archive_directories_all"] = allz["sentences"]
    return doc


def main():
    spec = read_json(SPEC)
    missing = [inv for inv in spec["investigations"] if not os.path.exists(os.path.join(LISTINGS, inv + ".json"))]
    if missing:
        print("raw_names: the PSI file listings are absent (data/psi/file_listings/ is git-ignored; missing: %s). "
              "Fetch them with python3 pipeline/raw_inventory.py --refresh. Nothing was written; the committed "
              "outputs are left as they are." % ", ".join(missing))
        return 0
    tests = read_csv(os.path.join(OUT, "tests.csv"))
    kinds = raw_inventory.Rules(read_json(KINDS))
    linked = link_files(spec, tests, kinds)
    gcols = ["investigation_id", "psi_category", "kind", "name_pattern", "suffix_code", "files", "bytes", "link_levels",
             "rules", "files_tied_to_a_test", "bytes_tied_to_a_test", "files_tied_to_a_day_or_session",
             "bytes_tied_to_a_day_or_session", "files_not_tied", "bytes_not_tied", "distinct_tests_reached",
             "distinct_table_rows_reached", "suffix_meaning", "example_name", "example_file_id",
             "quote_relation", "files_with_another_tie_by_name", "files_tied_to_several_rows"]
    write_csv(os.path.join(OUT, "raw_file_groups.csv"), gcols, group_rows(linked))
    tcols = ["investigation_id", "test_id", "table_row_key", "link_level", "kind", "suffix_code", "files", "bytes",
             "files_also_counted_for_another_row"]
    write_csv(os.path.join(OUT, "test_files.csv"), tcols, test_file_rows(linked))
    acols = ["investigation_id", "file_id", "name", "kind", "bytes", "deciding_rule", "deciding_level", "deciding_rows",
             "other_rule", "other_level", "other_rows"]
    write_csv(os.path.join(OUT, "name_tie_alternatives.csv"), acols, alternative_rows(linked))
    sample_path = os.path.join(OUT, "archive_members_sample.csv")
    arows = read_csv(sample_path) if os.path.exists(sample_path) else []
    raw_columns = read_json(os.path.join(HERE, "spec", "raw_columns.json"))
    raw_values = read_csv(os.path.join(OUT, "raw_values.csv"))
    write_json(os.path.join(OUT, "raw_layers_summary.json"), summary(spec, linked, raw_columns, raw_values, arows))
    n = sum(len(r) for _, r in linked.values())
    print("raw_names: %d files of %d investigations; wrote raw_file_groups.csv, test_files.csv, "
          "name_tie_alternatives.csv, raw_layers_summary.json" % (n, len(linked)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
