# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Trace audit of the catalog's AI-extracted text and lint of text pm does not own (design, component F).

Standard library only; no language model. Reads the catalog text the page displays and tries to
trace every number in it to NASA PSI material. It writes data/insights/catalog_trace.json:

  {_meta, numbers:[{table, row_id, investigation_id, field, number, unit, follower, context,
                    status, matched_source, rule}],
   lint_hits:[{file, key, text, pattern}], not_audited:[...], fields_audited[], rules{}, counts{}}

Fields audited (the page shows each of them, web/app.js):
  data/catalog/investigations.csv   objectives, key_findings
  data/catalog/configurations.csv   key_findings, config_label

Numbers are found with ai.checks.extract_numbers (the number gate's own extraction: digits inside
identifiers such as CO2, PSI-25 or NASA-STD-6001 are not numbers). Gravity-level names ('1 g', '0 g',
ai.lint_patterns.GRAVITY_NAMES) name a condition, not a value; they are listed under not_audited.

For each number the statuses are tried in this order; the first that matches is kept:
  found_in_psi_text    the numeral occurs in that investigation's PSI title, objective, approach,
                       hypothesis, researchImpacts or a publication title. For a number below 100 the
                       token that follows it in the catalog (its unit, or else the next word) must
                       follow it in the PSI text too.
  found_in_table_cell  (a) it equals a value of that investigation in data/pipeline/values_long.csv at
                       the printed precision, with the same unit when both carry one (a unitless
                       single-digit integer is not matched this way); or (b) the numeral occurs as
                       written, with the same unit, in a cell of one of that investigation's NASA
                       experimental tables (data/psi/experimental_tables, notes cells included).
  found_as_count       it equals the number of publications or of publication DOIs in the PSI record,
                       the number of rows of one of its tables (tests.csv rows per source, per
                       investigation, per fuel_material; raw table rows), an integer column sum of one
                       of its tables, or the count of one test_end or flow_event category (per source,
                       per investigation, per fuel_material). The counting rule is recorded.
  not_found            none of these.

A status says that the number was found, not that its meaning was checked. 'Number found in source'
is not a check of meaning.

lint_hits are the report-only hits of ai/check_all.py (ai.check_all.lint_report: the linter and
advice lexicon of ai/checks.py over scoring/scoring_config.json warnings, the why and main_gap
strings of scoring.scorer.rank for the four preset queries, and the catalog objectives and
key_findings), plus the same check over configurations.csv config_label.

    python3 ai/audit_catalog.py            # build data/insights/catalog_trace.json and print a summary
    python3 ai/audit_catalog.py --check    # build in memory, compare with the file, write nothing
    python3 ai/audit_catalog.py --list     # also print every not_found number and lint hit
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import checks as C, config, lint_patterns as LP, meta as metamod, resolve  # noqa: E402

ROOT = config.ROOT
OUT = config.INSIGHTS_DIR / "catalog_trace.json"
BUILT_BY = "ai/audit_catalog.py"
CATALOG = ROOT / "data" / "catalog"
PIPE = ROOT / "data" / "pipeline"
TABLES = ROOT / "data" / "psi" / "experimental_tables"
SOURCES_JSON = ROOT / "pipeline" / "spec" / "sources.json"
SCORING_CONFIG = ROOT / "scoring" / "scoring_config.json"
SCORER = ROOT / "scoring" / "scorer.py"

FIELDS = (
    ("investigations.csv", "investigation_id", ("objectives", "key_findings")),
    ("configurations.csv", "config_id", ("key_findings", "config_label")),
)
PSI_TEXT_FIELDS = ("title", "objective", "approach", "hypothesis", "researchImpacts")
STATUSES = ("found_in_psi_text", "found_in_table_cell", "found_as_count", "not_found")

RULES = {
    "numbers": "ai.checks.extract_numbers (the number gate's extraction); thousands commas removed; "
               "digits inside identifiers are not numbers",
    "follower": "the unit after the number (ai.checks unit list, normalised; a unit written as a word such "
                "as 'meters' counts as that unit; a number joined to the next one by a dash, 'to', 'x', a comma "
                "or 'and' takes that number's unit), or else the next word in lower case, stemmed, or none",
    "not_audited": "gravity-level names (1 g, 0 g) and numbers that are part of a name ('Test 1') are listed, "
                   "not traced",
    "found_in_psi_text": "numeral as written in the investigation's PSI title, objective, approach, "
                         "hypothesis, researchImpacts or a publication title; below 100 the follower must "
                         "match too",
    "found_in_table_cell": "(a) values_long.csv value of the investigation equal at the printed precision, "
                           "same unit when both carry one, not for a unitless single-digit integer; "
                           "(b) numeral as written in a cell of the investigation's NASA table, same unit "
                           "(in the cell or the column header) when the catalog gives one",
    "found_as_count": "publications, publication DOIs, table rows (per source, investigation or "
                      "fuel_material), integer column sums of a raw table, or one test_end / flow_event "
                      "category (per source, investigation or fuel_material)",
    "not_found": "none of the above",
    "meaning": "A status says the number was found, not that its meaning was checked.",
}


# ====================================================================== inputs

def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@lru_cache(maxsize=None)
def psi_record(inv):
    p = config.PSI_CATALOG_DIR / f"{inv}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


@lru_cache(maxsize=None)
def sources():
    return json.loads(SOURCES_JSON.read_text(encoding="utf-8"))["sources"]


@lru_cache(maxsize=None)
def manifest_tables():
    m = json.loads(config.PSI_MANIFEST.read_text(encoding="utf-8"))
    return {x["accession"]: [t["file"] for t in x.get("experimental_tables") or []] for x in m["investigations"]}


def source_id_for_file(file_name):
    for s in sources():
        if s["file"] == file_name:
            return s["id"]
    return None


@lru_cache(maxsize=None)
def tests_rows():
    return _read_csv(PIPE / "tests.csv")


@lru_cache(maxsize=None)
def values_rows():
    by_inv = defaultdict(list)
    for r in _read_csv(PIPE / "values_long.csv"):
        by_inv[r["investigation_id"]].append(r)
    return by_inv


@lru_cache(maxsize=None)
def raw_table(file_name):
    p = TABLES / file_name
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8", errors="replace") as f:
        return list(csv.reader(f))


# ====================================================================== number helpers

_NEXT_WORD = re.compile(r"[\s\-–]?\s*([A-Za-z]+)")


def _word(w):
    """A following word in lower case, stemmed with the gates' stemmer ('tests' / 'testing' -> 'test')."""
    w = w.lower()
    w = w[:-1] if len(w) > 3 and w.endswith("s") else w
    return C._stem(w)


# Unit names written as words. 'meters' in a PSI record is the unit 'm' of the catalog text.
UNIT_WORDS = {"meter": "m", "metre": "m", "centimeter": "cm", "centimetre": "cm", "millimeter": "mm",
              "millimetre": "mm", "micrometer": "um", "kilopascal": "kpa", "atmosphere": "atm",
              "second": "s", "minute": "min", "hour": "h", "percent": "%"}

# A number right after one of these words names something ('Test 1' is a NASA-STD-6001 test method),
# so it is listed under not_audited, not traced.
IDENT_LABELS = ("Test", "Table", "Fig.", "Figure", "Method", "Phase", "Run", "Version", "Part", "Section")
_IDENT_BEFORE = re.compile(r"(?:^|[\s(])(" + "|".join(re.escape(w) for w in IDENT_LABELS) + r")\s*#?\s*$")


# A number without a unit takes the unit of the number it is joined to in a range or a size:
# '0.5–3 atm', '2.1–2.6 mm/s', '0.94 x 0.4 m', '0.41, 0.76 and 1.6 mm'.
_JOIN = re.compile(r"\s*(?:–|—|-|to|x|×|,|,?\s*and|or)\s*$", re.I)


def numbers_in(text):
    """ai.checks.extract_numbers plus 'unit_from_range' and the effective unit 'eff_unit'; gravity-level
    names ('1 g', '1-g', '0 g') are marked 'gravity'."""
    ns = [dict(n) for n in C.extract_numbers(text)]
    spans = [(m.start(), m.end()) for m in LP.GRAVITY_NAMES.finditer(text)]
    nxt_unit = None
    for i in range(len(ns) - 1, -1, -1):
        n = ns[i]
        n["gravity"] = any(s <= n["start"] < e for s, e in spans)
        lab = _IDENT_BEFORE.search(text[max(0, n["start"] - 12):n["start"]])
        n["ident_label"] = lab.group(1) if lab else None
        n["unit_from_range"] = None
        if n["unit"] is None and i + 1 < len(ns) and nxt_unit and _JOIN.match(text[n["end"]:ns[i + 1]["start"]]):
            n["unit_from_range"] = nxt_unit
        n["eff_unit"] = n["unit"] or n["unit_from_range"]
        nxt_unit = n["eff_unit"]
    return ns


def follower(text, n):
    """The token that follows a number: ('unit', u) or ('word', w) or None."""
    if n.get("eff_unit", n["unit"]):
        return ("unit", n.get("eff_unit", n["unit"]))
    m = _NEXT_WORD.match(text, n["end"])
    if m and m.start(1) - n["end"] <= 1:
        w = _word(m.group(1))
        unit = UNIT_WORDS.get(m.group(1).lower().rstrip("s")) or UNIT_WORDS.get(w)
        return ("unit", unit) if unit else ("word", w)
    return None


def _follower_str(f):
    return None if f is None else f"{f[0]}:{f[1]}"


def decimals(value):
    return len(value.split(".", 1)[1]) if "." in value else 0


def _num(v):
    try:
        x = float(str(v).strip())
    except (TypeError, ValueError):
        return None
    return x if x == x else None


def _round_half_up(x, d):
    return Decimal(repr(x)).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)


def _vl_unit(u):
    """Normalise a values_long unit to the ai.checks unit vocabulary, or None for no physical unit."""
    u = (u or "").strip()
    if u.startswith("%"):
        return "%"
    low = u.lower()
    if low in (x.lower() for x in LP.UNITS):
        return C._unit_norm(low)
    return None


_PURE_NUMBER = re.compile(r"\s*[-+]?\d[\d.,]*\s*")


# ====================================================================== tracers

def psi_texts(inv):
    """[(source string, text)] for the PSI record fields and publication titles."""
    rec = psi_record(inv)
    if not rec:
        return []
    out = []
    for f in PSI_TEXT_FIELDS:
        v = rec.get(f)
        if isinstance(v, str) and v.strip():
            out.append((f"{inv}.{f}", v))
    for p in rec.get("publications") or []:
        t = (p.get("title") or "").strip()
        if t:
            src = f"doi:{p['doi'].strip()}" if (p.get("doi") or "").strip() else inv
            out.append((src, t))
    return out


def trace_psi_text(inv, n, fol):
    need_follower = float(n["value"]) < 100
    for src, text in psi_texts(inv):
        for m in numbers_in(text):
            if m["value"] != n["value"] or m["gravity"]:
                continue
            if need_follower and fol is not None and follower(text, m) != fol:
                continue
            rule = ("numeral as written" + (f", followed by {_follower_str(fol)}" if need_follower and fol else "")
                    + f"; source text: '{_context(text, m)}'")
            return src, rule
    return None


def trace_values_long(inv, n):
    """A values_long value equal at the printed precision with the same unit. A number without a unit
    is never matched this way (a bare integer equals some rounded cell too easily)."""
    unit = n["eff_unit"]
    if unit is None:
        return None
    d = decimals(n["value"])
    target = Decimal(n["value"])
    for r in values_rows().get(inv, []):
        v = _num(r["value"])
        if v is None or _vl_unit(r["unit"]) != unit:
            continue
        if _round_half_up(v, d) != target:
            continue
        src = f"data/pipeline/tests.csv#{r['test_id']}"
        rule = (f"values_long.csv: {r['test_id']} {r['variable']} = {r['value']} {r['unit']}"
                f" (equal at {d} decimal place{'s' if d != 1 else ''}); NASA cell "
                f"{r['source_file']} row {r['source_row']} column '{r['source_column']}'")
        return src, rule
    return None


def _header_units(head):
    units = {x["unit"] for x in C.extract_numbers("1 " + head) if x["unit"]}
    units |= {C._unit_norm(t) for t in re.split(r"[\s;,()\[\]]+", head) if t
              and t.lower() in (u.lower() for u in LP.UNITS)}
    return units


def trace_raw_cells(inv, n, fol):
    """The numeral as written in a NASA table cell. With a catalog unit the cell (or its column header)
    must carry the same unit. Without one, the cell must hold more than a bare number (a bare number
    is an id or a reading in some other column), and a word that follows the number in the catalog
    must follow it in the cell too."""
    unit = n["eff_unit"]
    for fname in manifest_tables().get(inv, []):
        rows = raw_table(fname)
        if not rows:
            continue
        header = rows[0]
        for i, row in enumerate(rows[1:], start=2):
            for j, cell in enumerate(row):
                if n["value"] not in cell.replace(",", ""):
                    continue
                head = header[j] if j < len(header) else ""
                for m in numbers_in(cell):
                    if m["value"] != n["value"] or m["gravity"]:
                        continue
                    if unit is not None:
                        if m["eff_unit"] != unit and not (m["eff_unit"] is None and unit in _header_units(head)):
                            continue
                    else:
                        if _PURE_NUMBER.fullmatch(cell):
                            continue
                        if fol is not None and follower(cell, m) != fol:
                            continue
                    sid = source_id_for_file(fname)
                    src = f"pipeline/spec/sources.json#{sid}" if sid else inv
                    col = head or f"column {j + 1}"
                    return src, (f"NASA table cell as written: {fname} row {i} column '{col.strip()}': "
                                 f"'{_context(cell, m)}'")
    return None


@lru_cache(maxsize=None)
def counts_for(inv):
    """{int value: [(source string, rule)]} of every counting rule for one investigation."""
    out = defaultdict(list)

    def put(v, src, rule):
        if isinstance(v, (int, float)) and float(v).is_integer():
            out[int(v)].append((src, rule))

    rec = psi_record(inv) or {}
    pubs = rec.get("publications") or []
    put(len(pubs), inv, "number of publications listed in the PSI record")
    put(len({(p.get("doi") or "").strip() for p in pubs if (p.get("doi") or "").strip()}), inv,
        "number of distinct publication DOIs in the PSI record")

    rows = [r for r in tests_rows() if r["investigation_id"] == inv]
    if rows:
        put(len(rows), inv, f"tests.csv rows with investigation_id {inv}")
    groups = {}
    for r in rows:
        groups.setdefault(("source", r["source_id"]), []).append(r)
        if r["fuel_material"]:
            groups.setdefault(("source_fuel", r["source_id"], r["fuel_material"].lower()), []).append(r)
    groups[("investigation",)] = rows
    for key, rs in sorted(groups.items()):
        if key[0] == "source":
            scope, src = f"source {key[1]}", f"pipeline/spec/sources.json#{key[1]}"
            put(len(rs), src, f"tests.csv rows of {scope}")
        elif key[0] == "source_fuel":
            scope, src = f"source {key[1]} with fuel_material '{key[2]}'", f"pipeline/spec/sources.json#{key[1]}"
            put(len(rs), src, f"tests.csv rows of {scope}")
        else:
            scope, src = f"investigation {inv}", inv
        for col in ("test_end", "flow_event"):
            for cat, k in sorted(Counter(r[col] for r in rs if r[col]).items()):
                put(k, src, f"tests.csv rows of {scope} with {col} = '{cat}'")

    for fname in manifest_tables().get(inv, []):
        raw = raw_table(fname)
        if len(raw) < 2:
            continue
        sid = source_id_for_file(fname)
        src = f"pipeline/spec/sources.json#{sid}" if sid else inv
        put(len(raw) - 1, src, f"data rows of the NASA table {fname}")
        for j, h in enumerate(raw[0]):
            vals = [_num(r[j]) if j < len(r) else None for r in raw[1:]]
            if vals and all(v is not None and float(v).is_integer() for v in vals):
                put(int(sum(vals)), src, f"sum of the integer column '{h.strip()}' of the NASA table {fname}")
    return dict(out)


def trace_count(inv, n):
    """Counts carry no unit and no decimal point."""
    if "." in n["value"] or n["eff_unit"] is not None:
        return None
    hits = counts_for(inv).get(int(n["value"]))
    return hits[0] if hits else None


def _context(text, n, width=40):
    s = max(0, n["start"] - width)
    e = min(len(text), n["end"] + width)
    return re.sub(r"\s+", " ", ("..." if s else "") + text[s:e] + ("..." if e < len(text) else "")).strip()


def trace(inv, text, n):
    fol = follower(text, n)
    for status, fn in (("found_in_psi_text", lambda: trace_psi_text(inv, n, fol)),
                       ("found_in_table_cell", lambda: trace_values_long(inv, n) or trace_raw_cells(inv, n, fol)),
                       ("found_as_count", lambda: trace_count(inv, n))):
        hit = fn()
        if hit:
            return status, hit[0], hit[1], fol
    return "not_found", None, "no rule matched", fol


# ====================================================================== lint

def lint_hits():
    """Report-only hits from ai/check_all.py, plus the same check over configurations.csv config_label."""
    from ai import check_all
    rep = check_all.Report()
    check_all.lint_report(rep, live_rank=True)
    hits = [dict(h) for h in rep.lint_hits]
    for row in _read_csv(CATALOG / "configurations.csv"):
        text = row.get("config_label") or ""
        for pat in C.lint_text(text):
            hits.append({"file": "data/catalog/configurations.csv", "key": f"{row['config_id']}.config_label",
                         "text": text, "pattern": pat})
    return hits


# ====================================================================== build

def build():
    numbers, not_audited = [], []
    for table, idcol, fields in FIELDS:
        for line_no, row in enumerate(_read_csv(CATALOG / table), start=2):
            inv = row["psi_accession"]
            for field in fields:
                text = row.get(field) or ""
                for n in numbers_in(text):
                    base = {"table": f"data/catalog/{table}", "row_id": row[idcol], "csv_line": line_no,
                            "investigation_id": inv, "field": field, "number": n["value"], "unit": n["unit"],
                            "unit_from_range": n["unit_from_range"]}
                    if n["gravity"]:
                        not_audited.append(dict(base, context=_context(text, n),
                                                reason="gravity-level name (1 g / 0 g), not a recorded value"))
                        continue
                    if n["ident_label"]:
                        not_audited.append(dict(base, context=_context(text, n),
                                                reason=f"part of a name ('{n['ident_label']} {n['value']}'), "
                                                       "not a recorded value"))
                        continue
                    status, src, rule, fol = trace(inv, text, n)
                    if src is not None and not resolve.check(src):
                        raise SystemExit(f"matched_source does not resolve: {src}")
                    numbers.append(dict(base, follower=_follower_str(fol), context=_context(text, n),
                                        status=status, matched_source=src, rule=rule))
    hits = lint_hits()
    by_status = Counter(x["status"] for x in numbers)
    by_field = defaultdict(Counter)
    for x in numbers:
        by_field[f"{x['table'].rsplit('/', 1)[1]}:{x['field']}"][x["status"]] += 1
    counts = {
        "numbers": len(numbers),
        "by_status": {s: by_status.get(s, 0) for s in STATUSES},
        "by_field": {k: {s: v.get(s, 0) for s in STATUSES} for k, v in sorted(by_field.items())},
        "not_audited": len(not_audited),
        "lint_hits": len(hits),
        "lint_hits_by_pattern": dict(sorted(Counter(h["pattern"] for h in hits).items())),
    }
    payload = {
        "description": ("Trace audit of the numbers in the AI-extracted catalog text that the page shows, and "
                        "linter hits in text pm does not own. A status says the number was found in a NASA "
                        "source, not that its meaning was checked. Catalog values remain AI-extracted and not "
                        "yet checked by a person."),
        "fields_audited": [f"data/catalog/{t}:{f}" for t, _, fs in FIELDS for f in fs],
        "rules": RULES,
        "counts": counts,
        "numbers": numbers,
        "not_audited": not_audited,
        "lint_hits": hits,
    }
    return payload


def inputs():
    files = [CATALOG / "investigations.csv", CATALOG / "configurations.csv", PIPE / "tests.csv",
             PIPE / "values_long.csv", SOURCES_JSON, config.PSI_MANIFEST, SCORING_CONFIG, SCORER]
    invs = sorted({r["psi_accession"] for r in _read_csv(CATALOG / "investigations.csv")})
    files += [config.PSI_CATALOG_DIR / f"{i}.json" for i in invs if (config.PSI_CATALOG_DIR / f"{i}.json").exists()]
    for i in invs:
        files += [TABLES / f for f in manifest_tables().get(i, []) if (TABLES / f).exists()]
    return files


def block():
    return metamod.meta(BUILT_BY, config.NO_MODEL, inputs=inputs(),
                        label=("AI-generated data file: built by code written with an AI assistant (Claude Code); "
                               "no language model ran to build it. It traces numbers in the team's AI-extracted "
                               "catalog text to NASA PSI records and tables; a found number is not a check of its "
                               "meaning. Team output, not a NASA conclusion."))


def summary(payload, full=False):
    c = payload["counts"]
    lines = [f"numbers audited: {c['numbers']} ({', '.join(f'{k} {v}' for k, v in c['by_status'].items())}); "
             f"not audited (gravity names): {c['not_audited']}; lint hits: {c['lint_hits']} {c['lint_hits_by_pattern']}"]
    for k, v in c["by_field"].items():
        lines.append(f"  {k}: " + ", ".join(f"{s} {n}" for s, n in v.items()))
    if full:
        lines.append("NOT FOUND:")
        for x in payload["numbers"]:
            if x["status"] == "not_found":
                lines.append(f"  {x['table']} line {x['csv_line']} {x['row_id']}.{x['field']}: "
                             f"{x['number']}{(' ' + x['unit']) if x['unit'] else ''} :: {x['context']}")
        lines.append("LINT HITS:")
        for h in payload["lint_hits"]:
            lines.append(f"  {h['file']} {h['key']}: {h['pattern']} :: {h['text']}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="compare a fresh build with the file; write nothing")
    ap.add_argument("--list", action="store_true", help="print every not_found number and lint hit")
    args = ap.parse_args(argv)
    payload = build()
    if args.check:
        if not OUT.exists():
            print("catalog_trace.json does not exist")
            return 1
        on_disk = json.loads(OUT.read_text(encoding="utf-8"))
        same = {k: v for k, v in on_disk.items() if k != "_meta"} == payload
        print("catalog_trace.json matches the build" if same else "catalog_trace.json differs from the build")
        print(summary(payload, full=args.list))
        return 0 if same else 1
    metamod.write_json(OUT, payload, block())
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(summary(payload, full=args.list))
    return 0


if __name__ == "__main__":
    sys.exit(main())
