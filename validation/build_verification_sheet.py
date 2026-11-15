#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude Code, catalog role) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Write validation/verification_sheet.csv: the catalog values behind the demo rankings, each with
where it is found in the NASA source (table rows and raw cells, or the PSI record text).

Run:  python3 validation/build_verification_sheet.py

The configurations come from the current ranking of the demo queries (DEMO below), so rerun it
after any change to the catalog or the scorer. The sheet has no sign-off columns (the human lead's
decision, 2026-11-15): it is a reference from each value to its NASA source.

Row numbers are CSV row numbers of the file in data/psi/experimental_tables/ (the header is row 1).
data/pipeline/tests.csv (`source_row`) and the catalog's `source_notes` use the same numbers.
The sheet copies values; it decides nothing. `tests_csv_extreme` is what the data pipeline
recorded for the same rows, so a difference from `catalog_value` is a place to look first.
Standard library only.
"""
import csv
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from scoring.scorer import rank  # noqa: E402
import build_catalog as bc  # noqa: E402  (reads the tables, writes nothing on import)

OUT = os.path.join(ROOT, "validation", "verification_sheet.csv")
TABLES = os.path.join(ROOT, "data", "psi", "experimental_tables")
TESTS = os.path.join(ROOT, "data", "pipeline", "tests.csv")
VALUES = os.path.join(ROOT, "data", "pipeline", "values_long.csv")

# Demo queries (the page's presets and the two typed examples) and how many ranked
# investigations of each to include beyond the top 3 results.
DEMO = [("ISS", 5), ("lunar habitat", 5), ("ISS cotton fabric", 3), ("lunar habitat cotton fabric", 3)]
TOL = 0.051  # catalog numbers carry one decimal; pipeline numbers carry more

# catalog field -> (tests.csv variable, unit, which end of the range)
NUMERIC = [
    ("o2_min_pct", "o2_pct", "%", min), ("o2_max_pct", "o2_pct", "%", max),
    ("pressure_min_kpa", "pressure_kpa", "kPa", min), ("pressure_max_kpa", "pressure_kpa", "kPa", max),
    ("flow_min_cms", "flow_cms", "cm/s", min), ("flow_max_cms", "flow_cms", "cm/s", max),
]
COLS = ["check_id", "config_id", "investigation_id", "psi_accession", "psi_url", "field", "catalog_value", "unit",
        "basis", "source", "source_column", "source_rows", "raw_cells", "tests_csv_extreme", "how_to_check"]


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _g(x):
    return f"{x:g}" if isinstance(x, float) else str(x)


def demo_configs():
    ids = []
    for q, k in DEMO:
        out = rank(q)
        for r in out["results"] + out["ranking"][:k]:
            if r["config_id"] not in ids:
                ids.append(r["config_id"])
    return ids


def raw_table(name, cache={}):
    if name not in cache:
        path = os.path.join(TABLES, name)
        if not os.path.exists(path):
            cache[name] = None
        else:
            raw = open(path, "rb").read()
            for enc in ("utf-8-sig", "cp1252", "latin-1"):  # same order as build_catalog.load_table
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            rows = list(csv.reader(io.StringIO(text)))  # blank rows kept, so numbers match the file
            cache[name] = (rows[0], rows)  # rows[n - 1] is CSV row n (header = row 1)
    return cache[name]


def raw_cell(table, row, column):
    t = raw_table(table)
    names = [h.strip().lower() for h in t[0]] if t else []
    if not t or column.strip().lower() not in names or row - 1 >= len(t[1]):
        return None
    r = t[1][row - 1]
    j = names.index(column.strip().lower())
    return r[j].strip() if j < len(r) else ""


def _tokens(s):
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w) >= 4}


def main():
    with open(os.path.join(ROOT, "data", "catalog", "configurations.csv"), encoding="utf-8") as fh:
        cfgs = {c["config_id"]: c for c in csv.DictReader(fh)}
    with open(os.path.join(ROOT, "data", "catalog", "investigations.csv"), encoding="utf-8") as fh:
        invs = {i["investigation_id"]: i for i in csv.DictReader(fh)}
    with open(TESTS, encoding="utf-8") as fh:
        tests = list(csv.DictReader(fh))
    columns = {}  # (source_file, variable) -> source column name
    with open(VALUES, encoding="utf-8") as fh:
        for v in csv.DictReader(fh):
            columns.setdefault((v["source_file"], v["variable"]), v["source_column"])

    def table_of(c):
        ref = c["tests_table_ref"].split(" (")[0].strip()
        return ref if ref.endswith(".csv") else ""

    sharing = {}
    for c in cfgs.values():
        sharing.setdefault(table_of(c), []).append(c["config_id"])

    out, n = [], 0
    for cid in demo_configs():
        c = cfgs[cid]
        inv = invs[c["investigation_id"]]
        table = table_of(c)
        rows = [t for t in tests if t["source_file"] == table] if table else []
        scope, split = "all rows of the table", True
        if rows and cid in bc.BASS2_CONFIG_FAMILY:
            fam = bc.BASS2_CONFIG_FAMILY[cid]
            rows = [t for t in rows if bc.bass2_family(raw_cell(table, int(t["source_row"]), "Fuel Sample Material") or "") == fam]
            scope = f"rows whose 'Fuel Sample Material' is in family '{fam}' (bass2_family in scripts/build_catalog.py)"
        elif rows and len(sharing.get(table, [])) > 1:
            fuel = _tokens(c["fuel_material"])
            by_fuel = [t for t in rows if _tokens(t["fuel_material"]) & fuel]
            if by_fuel and len(by_fuel) < len(rows):
                rows, scope = by_fuel, "rows whose fuel is this configuration's"
            else:  # the table cannot be split by fuel; the numbers below would be the whole table's
                split = False
                scope = (f"the table is shared with {', '.join(x for x in sharing[table] if x != cid)}; "
                         f"this configuration's rows are the ones named in tests_table_ref: {c['tests_table_ref']}")
        no_rows = ("The data pipeline has no test rows for this source (the table is not test-level or not mapped); "
                   f"find the value in {table or 'the PSI record'} (basis: {c['atmosphere_basis']}).")
        record = f"PSI record {c['psi_accession']}, {inv['psi_url']}"

        def add(field, value, unit, source, column, srows, raws, extreme, how):
            nonlocal n
            n += 1
            out.append(dict(check_id=f"V{n:03d}", config_id=cid, investigation_id=c["investigation_id"],
                            psi_accession=c["psi_accession"], psi_url=inv["psi_url"], field=field,
                            catalog_value=value, unit=unit, basis=c["atmosphere_basis"], source=source,
                            source_column=column, source_rows=srows, raw_cells=raws, tests_csv_extreme=extreme,
                            how_to_check=how))

        # Fuel: the distinct raw cells of the fuel column.
        col = columns.get((table, "fuel_material"), "")
        cells = sorted({raw_cell(table, int(t["source_row"]), col) or "" for t in rows} - {""}) if col else []
        add("fuel_material", c["fuel_material"], "", table or record, col, "", " | ".join(cells[:8]), "",
            f"Confirm that the fuel named in the catalog is the one in the source ({scope}).")

        # Oxygen, pressure, flow: the rows where the catalog's end of the range is recorded.
        for field, var, unit, end in NUMERIC:
            cat = _f(c[field])
            vals = [(_f(t[var]), int(t["source_row"])) for t in rows if _f(t[var]) is not None]
            extreme = _g(end(v for v, _ in vals)) if vals and split else ""
            col = columns.get((table, var), "")
            if cat is None:
                how = (f"Confirm that the source records no {field.split('_')[0]} value for this configuration "
                       f"({scope}); the catalog leaves it empty and the scorer shows it as not recorded or assumed.")
                add(field, "", unit, table or record, col, "", "", extreme, how)
                continue
            hits = [r for v, r in vals if abs(v - cat) <= TOL]
            if not hits and var == "flow_cms" and cid in bc.BASS2_CONFIG_FAMILY:
                # The catalog reads every air speed in a BASS-II cell (bass2_air); tests.csv keeps the first.
                col = "Air display"
                hits = [int(t["source_row"]) for t in rows
                        if any(abs(a - cat) <= TOL for a in bc.bass2_air(raw_cell(table, int(t["source_row"]), col) or ""))]
            raws = [raw_cell(table, r, col) for r in hits[:5]] if col else []
            if hits:
                how = f"Open the table on the PSI page; in column '{col}', rows {', '.join(map(str, hits[:5]))} should hold the value."
                if extreme and abs(_f(extreme) - cat) > TOL:
                    how += f" tests.csv's {end.__name__} over these rows is {extreme}; source_notes says why they differ."
                if not split:
                    how += f" Note: {scope}."
                add(field, _g(cat), unit, table, col, ", ".join(map(str, hits[:5])), " | ".join(x or "" for x in raws), extreme, how)
            elif not rows:
                add(field, _g(cat), unit, table or record, col, "", "", "", no_rows)
            else:
                how = ("Not in the table columns the data pipeline reads; the catalog value comes from the PSI record or a "
                       f"team reading. Check the basis ('{c['atmosphere_basis']}'), the record and source_notes: {c['source_notes'][:240]}")
                add(field, _g(cat), unit, table or record, col, "", "", extreme, how)

        # Test count.
        srows = sorted(int(t["source_row"]) for t in rows)
        add("test_count_config", c["test_count_config"], "tests", table or record, "",
            f"{srows[0]}–{srows[-1]}" if srows and split else "", "", str(len(rows)) if rows and split else "",
            (f"Count this configuration's rows in the table ({scope}); rows that repeat an earlier row cell for cell are not tests."
             if rows else no_rows))

    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    with_rows = sum(1 for r in out if r["source_rows"])
    print(f"wrote {len(out)} checks for {len(demo_configs())} configurations -> {os.path.relpath(OUT, ROOT)}; "
          f"{with_rows} point to table rows, the others to the record, source_notes or an empty value")


if __name__ == "__main__":
    main()
