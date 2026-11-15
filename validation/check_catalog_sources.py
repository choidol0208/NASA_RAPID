#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude Code, catalog role) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Check the catalog against the NASA sources directly: PSI records and experimental tables.

Run:  python3 validation/check_catalog_sources.py      (writes validation/catalog_source_check.md)

It reads only data/catalog/*.csv, data/psi/manifest.json, data/psi/catalog/PSI-*.json and
data/psi/experimental_tables/*.csv. It does not import scripts/build_catalog.py or the data
pipeline, so it is an independent second reading. It is not a deploy step: the catalog role runs it.

Three checks:
1. Ranking values. Every oxygen, pressure and flow number that the scorer compares must be found
   in its stated source (`o2_source`, `pressure_source`, `flow_source`):
   - for `table` and `test_matrix`, in a column of the investigation's tables whose header names
     the variable, after the unit the header names (mole fraction, atm, bar, psi, mmHg, kPa);
   - for `record`, in the PSI record text, after any of those units.
   - `team` values are listed and not searched.
   When one configuration alone uses a table, the two ends of each range are also compared with
   the lowest and highest number in the matched column.
2. Test counts. When one configuration alone uses a table, `test_count_config` is compared with
   the table's rows, after dropping blank rows and rows that repeat an earlier row cell for cell.
   For the ACME day tables, the sum of the 'Flames Ignited' column is used instead.
3. Numbers in the text the page shows (investigation objectives and key_findings, configuration
   label and key_findings). Each number must be found in the investigation's record text or table
   cells, directly or after a simple unit change (percent and fraction, cm and m, mm and cm).

"Found" means the number is written in the source. It does not prove that the number is used
with the same meaning: validation/verification_sheet.csv lists the NASA rows behind each demo value.
Exit code 1 when a ranking value or a text number is not found. Standard library only.
"""
import csv
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PSI = os.path.join(ROOT, "data", "psi")
CAT = os.path.join(ROOT, "data", "catalog")
OUT = os.path.join(ROOT, "validation", "catalog_source_check.md")

NUM = re.compile(r"(?<![\w.])-?(?:\d+(?:\.\d+)?|\.\d+)")  # "-5.92" is negative; "1.5-5" is 1.5 and 5
# header words that name each variable, and the unit factors a header can name
VAR_WORDS = {
    "o2": re.compile(r"(?i)\bo2\b|oxygen|xo2|^o initial|percent o2|atmosphere"),
    "pressure": re.compile(r"(?i)pressure|\bp\b|pinit|pfinal|pmean|psia|\(atm\)|\(bar\)|mmhg|kpa|atmosphere"),
    "flow": re.compile(r"(?i)flow|air|velocity|speed|cm/s"),
}
# a cell that names the variable itself counts too (a note such as "Atmosphere is ~1 atm")
CELL_WORDS = {
    "o2": re.compile(r"(?i)\bo2\b|oxygen"),
    "pressure": re.compile(r"(?i)\batm\b|psia?\b|kpa|mmhg|\bbar\b"),
    "flow": re.compile(r"(?i)cm/s"),
}
VALID = {"o2": (0.0, 100.0), "pressure": (0.0, 1e5), "flow": (0.0, 1e4)}  # outside: not a reading of the variable
UNITS = {
    "o2": [("mole fraction", re.compile(r"(?i)mole f|fraction|\bx\s*o2|xo2|^o initial"), 100.0), ("%", re.compile(r"%|percent"), 1.0)],
    "pressure": [("atm", re.compile(r"(?i)atm"), 101.325), ("bar", re.compile(r"(?i)\bbar\b"), 100.0),
                 ("psi", re.compile(r"(?i)psi"), 6.89476), ("mmHg", re.compile(r"(?i)mmhg"), 0.133322),
                 ("kPa", re.compile(r"(?i)kpa"), 1.0)],
    "flow": [("cm/s", re.compile(r"(?i)cm/s|cm s"), 1.0), ("mm/s", re.compile(r"(?i)mm/s"), 0.1), ("m/s", re.compile(r"(?i)(?<!c)(?<!m)m/s"), 100.0)],
}
FIELDS = {"o2": ("o2_min_pct", "o2_max_pct"), "pressure": ("pressure_min_kpa", "pressure_max_kpa"),
          "flow": ("flow_min_cms", "flow_max_cms")}


def nums(text):
    return [float(m.group(0)) for m in NUM.finditer(text or "")]


def close(a, b):
    return abs(a - b) <= max(0.051, 0.001 * abs(b))


def load_table(name):
    raw = open(os.path.join(PSI, "experimental_tables", name), "rb").read()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    rows = list(csv.reader(io.StringIO(text)))
    return [h.strip() for h in rows[0]], rows[1:]  # data row i is CSV row i + 2


def record_text(acc):
    d = json.load(open(os.path.join(PSI, "catalog", f"{acc}.json"), encoding="utf-8"))
    out = []

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, (str, int, float)) and not isinstance(o, bool):
            out.append(str(o))
    walk(d)
    return " ".join(out)


def factors_for(var, header):
    named = [(u, f) for u, rx, f in UNITS[var] if rx.search(header)]
    return named or [(u, f) for u, _, f in UNITS[var]]


def find_in_tables(var, value, tables):
    """[(file, csv_row, header, cell, unit)] where a cell of a column naming var holds value."""
    hits = []
    for name, (hdr, rows) in tables.items():
        for j, h in enumerate(hdr):
            by_header = bool(VAR_WORDS[var].search(h))
            for i, r in enumerate(rows):
                cell = r[j] if j < len(r) else ""
                if not (by_header or CELL_WORDS[var].search(cell)):
                    continue
                for n in nums(cell):
                    for unit, f in factors_for(var, h + " " + cell):
                        if close(n * f, value):
                            hits.append((name, i + 2, h, cell.strip(), unit))
    return hits


def column_extremes(var, table, hdr, rows, header):
    """Lowest and highest reading in the column, and the cells left out as not a reading
    (a negative flow, an O2 above 100%)."""
    j = hdr.index(header)
    f = factors_for(var, header)[0][1]
    lo_ok, hi_ok = VALID[var]
    vals, skipped = [], []
    for i, r in enumerate(rows):
        if j >= len(r):
            continue
        for n in nums(r[j]):
            (vals if lo_ok <= n * f <= hi_ok else skipped).append(n * f if lo_ok <= n * f <= hi_ok else f"row {i + 2} '{r[j].strip()}'")
    return ((min(vals), max(vals)) if vals else None), skipped


def find_in_record(var, value, text):
    for n in nums(text):
        for unit, _, f in UNITS[var]:
            if close(n * f, value):
                return f"{n:g} {unit}"
    return None


def text_number_found(n, text, cells):
    pool = nums(text) + [x for c in cells for x in nums(c)]
    for m in pool:
        for f in (1.0, 100.0, 0.01, 10.0, 0.1):
            if abs(m * f - n) <= max(1e-9, 0.005 * abs(n)):
                return True
    return False


def main():
    with open(os.path.join(CAT, "configurations.csv"), encoding="utf-8") as fh:
        cfgs = list(csv.DictReader(fh))
    with open(os.path.join(CAT, "investigations.csv"), encoding="utf-8") as fh:
        invs = {r["psi_accession"]: r for r in csv.DictReader(fh)}
    man = {i["accession"]: i for i in json.load(open(os.path.join(PSI, "manifest.json"), encoding="utf-8"))["investigations"]}
    tables = {acc: {t["file"]: load_table(t["file"]) for t in man[acc]["experimental_tables"]} for acc in man}
    rec = {acc: record_text(acc) for acc in man}
    ref_file = {c["config_id"]: c["tests_table_ref"].split(" (")[0].strip() for c in cfgs}
    users = {}
    for c in cfgs:
        users.setdefault(ref_file[c["config_id"]], []).append(c["config_id"])

    rank_rows, count_rows, text_rows, bad = [], [], [], 0
    for c in cfgs:
        acc, cid = c["psi_accession"], c["config_id"]
        own = ref_file[cid] if ref_file[cid] in tables[acc] and users[ref_file[cid]] == [cid] else None
        for var, (lo_f, hi_f) in FIELDS.items():
            src = c.get(f"{var}_source", "")
            for field in (lo_f, hi_f):
                if c[field] == "":
                    continue
                v = float(c[field])
                if src == "team":
                    rank_rows.append((cid, field, v, src, "team reading (by design)", "", "—"))
                    continue
                if src == "record":
                    hit = find_in_record(var, v, rec[acc])
                    status = "found" if hit else "NOT FOUND"
                    rank_rows.append((cid, field, v, src, f"PSI record: {hit}" if hit else "not in the record text", "", status))
                    bad += not hit
                    continue
                pool = {own: tables[acc][own]} if own else tables[acc]
                hits = find_in_tables(var, v, pool)
                if not hits:
                    rank_rows.append((cid, field, v, src, "not in a column that names the variable", "", "NOT FOUND"))
                    bad += 1
                    continue
                name, row, hdr, cell, unit = hits[0]
                where = f"{name}, row {row}, '{hdr}' = '{cell}' ({unit})"
                ends = ""
                if own and VAR_WORDS[var].search(hdr):
                    ext, skipped = column_extremes(var, own, *tables[acc][own], hdr)
                    if ext:
                        want = ext[0] if field == lo_f else ext[1]
                        ends = "end matches column" if close(want, v) else f"column {'min' if field == lo_f else 'max'} is {want:g}"
                        if skipped:
                            ends += f" (left out as not a reading: {', '.join(skipped[:3])}{' …' if len(skipped) > 3 else ''})"
                rank_rows.append((cid, field, v, src, where, ends, "found"))
        # test counts
        n = c["test_count_config"]
        if n and own:
            hdr, rows = tables[acc][own]
            seen, distinct = set(), 0
            for r in rows:
                k = tuple(x.strip() for x in r)
                if any(k) and k not in seen:
                    seen.add(k)
                    distinct += 1
            fi = [j for j, h in enumerate(hdr) if "flames ignited" in h.lower()]
            ignited = int(sum(x for r in rows for j in fi if j < len(r) for x in nums(r[j])[:1])) if fi else None
            if int(float(n)) == distinct:
                count_rows.append((cid, n, f"{distinct} distinct rows in {own}", "match"))
            elif ignited is not None and int(float(n)) == ignited:
                count_rows.append((cid, n, f"sum of 'Flames Ignited' in {own} = {ignited}", "match"))
            elif "Test count:" in c.get("source_notes", ""):  # the catalog states its own reading of the rows
                note = c["source_notes"].split("Test count:", 1)[1].split(". ")[0].strip()
                count_rows.append((cid, n, f"{distinct} distinct rows in {own}; source_notes: {note}", "documented"))
            else:
                count_rows.append((cid, n, f"{distinct} distinct rows in {own}" + (f"; Flames Ignited sum {ignited}" if fi else ""), "DIFFERS"))
        elif n:
            count_rows.append((cid, n, f"table shared with {', '.join(x for x in users.get(ref_file[cid], []) if x != cid) or '—'}"
                               if ref_file[cid] in tables[acc] else "no single table", "not compared"))
    # numbers in displayed text
    cells = {acc: [x for _, (h, rows) in tables[acc].items() for r in rows for x in r] + [x for _, (h, _) in tables[acc].items() for x in h]
             for acc in man}
    shown = [(acc, invs[acc]["investigation_id"], f, invs[acc][f]) for acc in invs for f in ("objectives", "key_findings")]
    shown += [(c["psi_accession"], c["config_id"], f, c[f]) for c in cfgs for f in ("config_label", "key_findings")]
    pubs = {acc: len(json.load(open(os.path.join(PSI, "catalog", f"{acc}.json"), encoding="utf-8")).get("publications") or [])
            for acc in man}
    for acc, who, field, text in shown:
        t = re.sub(r"PSI-\d+", " ", text or "")
        for m in NUM.finditer(t):
            if t[m.end():m.end() + 1].isalpha() and not t[m.end():m.end() + 2].lower().startswith(("g ", "g,", "g.")):
                continue  # part of a name such as CO2, C2H4, N2
            n = abs(float(m.group(0)))
            if re.match(r"\s+linked publications", t[m.end():]):  # a count of the record's publication list
                ok = int(n) == pubs[acc]
                text_rows.append((who, field, m.group(0), "found" if ok else "NOT FOUND"))
                bad += not ok
                continue
            ok = text_number_found(n, rec[acc], cells[acc])
            text_rows.append((who, field, m.group(0), "found" if ok else "NOT FOUND"))
            bad += not ok

    nf_rank = [r for r in rank_rows if r[6] == "NOT FOUND"]
    nf_text = [r for r in text_rows if r[3] == "NOT FOUND"]
    differs = [r for r in rank_rows if r[5].startswith("column")]
    lines = ["# Catalog against the NASA sources", "",
             "*Written by `python3 validation/check_catalog_sources.py` (AI-generated code). Not a deploy step.*", "",
             f"- Ranking values (O2, pressure, flow ends): {len(rank_rows)} checked, "
             f"{sum(r[6] == 'found' for r in rank_rows)} found, {len(nf_rank)} not found, "
             f"{sum(r[6] == '—' for r in rank_rows)} team readings.",
             f"- Range ends compared with the column of a table used by one configuration: "
             f"{sum(r[5] == 'end matches column' for r in rank_rows)} match, {len(differs)} differ.",
             f"- Test counts: {sum(r[3] == 'match' for r in count_rows)} match, "
             f"{sum(r[3] == 'documented' for r in count_rows)} differ with the reason in source_notes, "
             f"{sum(r[3] == 'DIFFERS' for r in count_rows)} differ, "
             f"{sum(r[3] == 'not compared' for r in count_rows)} not compared (shared table or no table).",
             f"- Numbers in the text the page shows: {len(text_rows)} checked, {len(text_rows) - len(nf_text)} found, {len(nf_text)} not found.",
             "", "'Found' means the number is written in the source, not that its meaning was checked.", ""]
    if nf_rank or nf_text or differs:
        lines += ["## To look at", "", "| Where | Field | Value | Note |", "|---|---|---|---|"]
        lines += [f"| {r[0]} | {r[1]} | {r[2]:g} | not found ({r[3]}): {r[4]} |" for r in nf_rank]
        lines += [f"| {r[0]} | {r[1]} | {r[2]:g} | {r[5]} |" for r in differs]
        lines += [f"| {r[0]} | {r[1]} | {r[2]} | text number not found in the record or tables |" for r in nf_text]
        lines.append("")
    lines += ["## Ranking values", "", "| Configuration | Field | Value | Source | Where | Range end |", "|---|---|---|---|---|---|"]
    lines += [f"| {r[0]} | {r[1]} | {r[2]:g} | {r[3]} | {r[4].replace('|', '/')} | {r[5]} |" for r in rank_rows]
    lines += ["", "## Test counts", "", "| Configuration | Catalog | Source | Result |", "|---|---|---|---|"]
    lines += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |" for r in count_rows]
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[4:8]))
    print(f"report: {os.path.relpath(OUT, ROOT)}")
    return 1 if (nf_rank or nf_text) else 0


if __name__ == "__main__":
    sys.exit(main())
