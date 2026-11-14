# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Evidence map data: 'Where the PSI test tables stop' (component H of docs/ai_layer_design.json).

Writes data/insights/evidence_map.json from data/pipeline/tests.csv and the spec files.
No language model runs; nothing is binned, estimated or fitted.

- points: every test with an ambient-basis oxygen value, grouped to distinct
  (fuel_phase, investigation_id, o2_pct, pressure_kpa or null, balance_gas); all test ids kept.
- not_plotted: oxidizer-stream tests, tests with no ambient oxygen value, and the PSI-20
  test-day table (computed from the NASA CSV, settings kept as written).
- targets: cited atmospheres (references.json), the scorer presets (scoring_config.json) and the
  team's counting ranges (pipeline/spec/scenarios.json), each with kind, source and access.
- flight_tests_not_in_psi / saffire_note: the five samples of the Saffire IV to VI item SAF456.conditions
  (pipeline/spec/references.json, ICES-2024-365 Table 1, checked by the data role at 12:47), drawn as cited
  marks; written only when the item exists with machine-readable values, otherwise null. They are never
  counted (counted: false on every mark, and no sum below includes them). Nothing is transcribed here.
- sums.lanes: per fuel lane, the tests plotted, the highest recorded oxygen, the tests at 30% oxygen or
  more and the tests of that lane that are not plotted.

Run:  python3 ai/evidence_map.py            (build and write; prints the counts)
      python3 ai/evidence_map.py --strict   (also exit 1 if a count differs from the design's anchors)
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import config  # noqa: E402
from ai import meta as metamod  # noqa: E402

ROOT = config.ROOT
BUILT_BY = "ai/evidence_map.py"
OUT = config.INSIGHTS_DIR / "evidence_map.json"

TESTS = ROOT / "data/pipeline/tests.csv"
SCENARIO_TESTS = ROOT / "data/pipeline/scenario_tests.csv"
REFERENCES = ROOT / "pipeline/spec/references.json"
SCENARIOS = ROOT / "pipeline/spec/scenarios.json"
SOURCES = ROOT / "pipeline/spec/sources.json"
MANIFEST = ROOT / "data/psi/manifest.json"
SCORING = ROOT / "scoring/scoring_config.json"
TABLES_DIR = ROOT / "data/psi/experimental_tables"
PSI20_SOURCE_ID = "acme_bre"

INPUTS = [TESTS, SCENARIO_TESTS, REFERENCES, SCENARIOS, SOURCES, SCORING, MANIFEST]

LANES = [("gas", "Gas flames"), ("liquid", "Fuel droplets"), ("solid", "Solid fuels")]
LANE_ORDER = {k: i for i, (k, _) in enumerate(LANES)}
BALANCE_GAS = ("n2_only", "co2_added", "he_added", "not_recorded")

# contracts/README.md: "Pressure is in kPa everywhere (14.7 psi = 101.3 kPa, 10.2 psi = 70.3 kPa)."
PSIA_PAIRS = {14.7: 101.3, 10.2: 70.3}
KPA_PER_PSIA = 6.894757
CONTRACT_PAIR = "contract pair (contracts/README.md: 14.7 psi = 101.3 kPa, 10.2 psi = 70.3 kPa)"
TEAM_CONVERSION = "team conversion: 6.894757 kPa per psia, rounded to 0.1 kPa"

ACCESS_NOTE = {
    "full_text_read": "full text read",
    "abstract_only": "source read at abstract level",
    "cited_not_read": "known only through a citation",
    "read_from_copy": "read from a copy",
}

# Counts recounted from data/pipeline/tests.csv after the data role's audit (1,824 test rows; the design's
# component H numbers were computed on 1,867 rows before it). They are printed next to the build's own counts
# and compared, never forced; ai/test_evidence_map.py recomputes each one by a second code path instead of
# trusting this table, so a data change shows up here as a difference to look at, not as a hidden number.
ANCHORS = {
    "plotted": 879,
    "plotted_with_pressure": 738,
    "plotted_without_pressure": 141,
    "plotted_by_phase": {"gas": 386, "liquid": 353, "solid": 140},
    "oxidizer_stream": 274,
    "oxidizer_stream_without_oxygen_value": 11,
    "no_ambient_oxygen_value": 671,
    "no_ambient_oxygen_value_by_phase": {"gas": 435, "solid": 236},
    "total": 1824,
    "balance_gas_with_pressure": {"n2_only": 166, "co2_added": 122, "he_added": 64, "not_recorded": 386},
    "points_with_pressure": 593,
    "with_pressure_above_110_kpa": 147,
    "without_pressure_by_investigation": {"PSI-25": 129, "PSI-99": 9, "PSI-98": 2, "PSI-69": 1},
    "max_o2_by_phase": {"solid": 22.2, "liquid": 34.0, "gas": 40.0},
    "at_or_above_30_by_phase": {"gas": 246, "liquid": 24, "solid": 0},
    "psi20_days": 18,
    "psi20_flames_ignited": 194,
    "lunar_habitat_range_tests": 26,
}
SAFFIRE_ITEM = "SAF456.conditions"
FLIGHT_LABEL = "Saffire flight sample from a published paper (not in PSI, not counted)"

RULES = {
    "plotted": ("A test is plotted when tests.csv gives o2_basis 'ambient' and an o2_pct value. "
                "Points group tests with the same fuel_phase, investigation_id, o2_pct, pressure_kpa "
                "(or no pressure value) and balance_gas; values are used as written in tests.csv, not binned."),
    "balance_gas": ("n2_only: the table has a nitrogen column and every added-gas column it has "
                    "(carbon dioxide, helium) is 0 for the test; co2_added / he_added: that column is above 0; "
                    "not_recorded: the table has no added-gas column, or the cell is empty. "
                    "Views draw co2_added and he_added as hollow markers."),
    # review: FLEX test 114 has '0' mmHg in the NASA cell; the pipeline flags it out_of_range and uses no
    # value. 'Not recorded' was the wrong word for that cell, and the rule now says what null covers.
    "pressure_kpa_null": ("Null means the map has no pressure value for the test: pressure is not a column of the "
                          "table, or the cell is empty, or the cell holds a value the pipeline does not use (see "
                          "pressure_column and the point's value_flags). Null is never drawn as 0 and never as "
                          "101 kPa."),
    "oxidizer_stream": ("Oxygen of the oxidizer stream of an inverse flame (o2_basis 'oxidizer_stream') is not "
                        "the oxygen of an atmosphere a crew breathes, so these tests are never mixed with the "
                        "ambient points."),
    "no_ambient_oxygen_value": ("Tests with no o2_basis, or with o2_basis 'ambient' and an empty o2_pct: the table "
                                "records no oxygen value for them. Not recorded is not zero."),
    # review: the table notes call the listed values 'approximate concentrations for tests that ignited'
    "psi20_test_day_table": ("The PSI-20 table has one row per test day and lists approximate oxygen concentrations "
                             "for the tests that ignited that day, so a value cannot be tied to a test; it is "
                             "summarised, not plotted."),
}

# reader (14 Nov, afternoon; an AI session of the pm role read the labels as a combustion scientist would):
# - 'recorded tests in the tables of 24 NASA PSI investigations' read as if all 24 were plotted; the caption
#   now says how many tests are drawn and from how many investigations (counted by build());
# - 'closeness on this chart is not flammability equivalence' was jargon; it now says what a dot near a
#   target atmosphere does not mean, and why;
# - the second line now names pressure next to balance gas (both are drawn only where the table records them).
def first_caption(n_plotted, n_plotted_inv, n_inv):
    return (f"Each dot is one or more recorded tests from the experimental tables of the {n_inv} NASA PSI "
            f"investigations used here: the {n_plotted} tests with a recorded ambient oxygen value, from "
            f"{n_plotted_inv} of the investigations, all run in microgravity. Also drawn: atmospheres cited from "
            "NASA documents and the challenge statement, and the team's own presets and counting ranges. A plot by "
            "the team; a dot means a test was run at that oxygen level, not that anything burned or went out; a "
            "dot near a target atmosphere does not mean the test represents that atmosphere, because fuel, flow, "
            "pressure, balance gas and gravity can differ; not operational safety guidance.")


SECOND_CAPTION = ("Oxygen percent alone does not define an atmosphere; pressure and balance gas are shown where "
                  "the table records them.")


def num(s):
    s = (s or "").strip()
    return float(s) if s else None


def fmt(x):
    """A number as text without a trailing .0 for whole numbers (labels only)."""
    return str(int(x)) if float(x).is_integer() else repr(float(x))


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_table(file_name):
    """A NASA table decoded as pipeline/run.py does (utf-8-sig, undecodable bytes replaced)."""
    raw = (TABLES_DIR / file_name).read_bytes().decode("utf-8-sig", "replace")
    return list(csv.reader(raw.splitlines()))


def raw_header(file_name):
    return read_table(file_name)[0]


def source_columns(src):
    out = set()
    for c in src.get("columns", []):
        to = c.get("to")
        out.update(to if isinstance(to, list) else [to])
    out.update((src.get("constants") or {}).keys())
    return out


_N2 = re.compile(r"(^|\W)(nitrogen|n2|n initial)(\W|$)", re.I)
_PRESSURE = re.compile(r"press|kpa|psi|mmhg|torr|\(atm\)|\(bar\)|(^|\W)p\W", re.I)


def inv_key(inv):
    return int(inv.split("-")[1])


def psia_to_kpa(psia):
    psia = float(psia)
    if psia in PSIA_PAIRS:
        return PSIA_PAIRS[psia], CONTRACT_PAIR
    return round(psia * KPA_PER_PSIA, 1), TEAM_CONVERSION


def in_range(value, r):
    """Same semantics as pipeline/spec/scenarios.json (min inclusive, max exclusive unless stated); a second code path."""
    if value is None:
        return False
    lo = r.get("min") is None or value > r["min"] or (value == r["min"] and r.get("min_inclusive", True))
    hi = r.get("max") is None or value < r["max"] or (value == r["max"] and r.get("max_inclusive", False))
    return lo and hi


# --------------------------------------------------------------------------- points

def balance_gas(row, cols, has_n2_column):
    present = [c for c in ("co2_pct", "he_pct") if c in cols]
    if not present:
        return "not_recorded"
    vals = {c: num(row[c]) for c in present}
    added = [c for c, v in vals.items() if v is not None and v > 0]
    if len(added) > 1:
        raise SystemExit(f"{row['test_id']}: both carbon dioxide and helium added; no category for that")
    if added:
        return "co2_added" if added[0] == "co2_pct" else "he_added"
    if any(v is None for v in vals.values()) or not has_n2_column:
        return "not_recorded"
    return "n2_only"


COMPOSITION_TOLERANCE = 0.005


def composition_sum(row, info):
    """Sum of the gas fractions as written in the NASA row (oxygen, nitrogen and any added gas), or None."""
    if not info.get("composition_columns"):
        return None
    tab = info["table"]
    header, raw = tab[0], tab[int(row["source_row"]) - 1]
    vals = dict(zip(header, raw))
    try:
        return round(sum(float(vals[c]) for c in info["composition_columns"]), 6)
    except (KeyError, ValueError):
        return None


def value_flags(row):
    keep = ("o2_pct", "pressure_kpa", "co2_pct", "he_pct")
    return [f for f in row["flags"].split(";") if f and f.split(":")[0] in keep]


def build_points(tests, sources):
    plotted = [t for t in tests if t["o2_basis"] == "ambient" and num(t["o2_pct"]) is not None]
    src_info = {}
    for sid in sorted({t["source_id"] for t in plotted}):
        src = sources[sid]
        cols = source_columns(src)
        header = raw_header(src["file"])
        gas_from = [c["from"] for c in src.get("columns", []) if c.get("to") in ("o2_pct", "co2_pct", "he_pct")]
        n2_cols = [h for h in header if _N2.search(h)]
        src_info[sid] = {
            "cols": cols,
            "n2": bool(n2_cols),
            "raw_pressure_headers": [h for h in header if _PRESSURE.search(h)],
            # composition columns of the raw table (mole or volume fractions), for the sum check below
            "composition_columns": gas_from + n2_cols if n2_cols else [],
            "table": read_table(src["file"]) if n2_cols else None,
        }
    groups = defaultdict(list)
    off_tests = {}
    for t in plotted:
        if t["gravity_level"] != "microgravity":
            raise SystemExit(f"{t['test_id']}: gravity_level {t['gravity_level']!r}; the caption says microgravity")
        info = src_info[t["source_id"]]
        bg = balance_gas(t, info["cols"], info["n2"])
        key = (t["fuel_phase"], t["investigation_id"], t["source_id"], num(t["o2_pct"]), num(t["pressure_kpa"]), bg)
        groups[key].append(t)
    points = []
    for (phase, inv, sid, o2, p, bg), ts in groups.items():
        pt = {"fuel_phase": phase, "investigation_id": inv, "source_id": sid, "o2_pct": o2,
              "pressure_kpa": p, "balance_gas": bg, "n_tests": len(ts),
              "test_ids": [t["test_id"] for t in sorted(ts, key=lambda t: int(t["source_row"]))]}
        if bg == "co2_added":
            pt["co2_pct_values"] = sorted({num(t["co2_pct"]) for t in ts})
        if bg == "he_added":
            pt["he_pct_values"] = sorted({num(t["he_pct"]) for t in ts})
        flags = sorted({f for t in ts for f in value_flags(t)})
        if flags:
            pt["value_flags"] = flags
        off = {t["test_id"]: composition_sum(t, src_info[sid]) for t in ts}
        off = {k: v for k, v in off.items() if v is not None and abs(v - 1) > COMPOSITION_TOLERANCE}
        if off:
            pt["gas_fractions_sum_as_written"] = sorted(set(off.values()))
            pt["gas_fractions_sum_test_ids"] = sorted(off, key=lambda k: pt["test_ids"].index(k))
            off_tests.update(off)
        points.append(pt)
    points.sort(key=lambda q: (LANE_ORDER[q["fuel_phase"]], inv_key(q["investigation_id"]), q["source_id"],
                               q["o2_pct"], q["pressure_kpa"] is None, q["pressure_kpa"] or 0,
                               BALANCE_GAS.index(q["balance_gas"])))
    # pressure_column per source of a plotted test
    pressure_column = {}
    for sid, info in src_info.items():
        rows = [t for t in plotted if t["source_id"] == sid]
        empty = [t for t in rows if num(t["pressure_kpa"]) is None]
        if "pressure_kpa" not in info["cols"]:
            if info["raw_pressure_headers"]:
                raise SystemExit(f"{sid}: no pressure mapping but raw header has {info['raw_pressure_headers']}")
            status = "no column"
        elif empty:
            status = "column, some cells empty"
        else:
            status = "column, every cell filled"
        entry = {"status": status, "investigation_id": rows[0]["investigation_id"],
                 "fuel_phase": rows[0]["fuel_phase"], "tests_plotted": len(rows),
                 "tests_without_pressure_value": len(empty),
                 "raw_pressure_columns": info["raw_pressure_headers"],
                 "source": f"pipeline/spec/sources.json#{sid}"}
        reasons = Counter(f for t in empty for f in value_flags(t) if f.startswith("pressure_kpa:"))
        if reasons:
            entry["empty_reasons"] = dict(sorted(reasons.items()))
            # review: a flagged cell is not an empty cell. The status string is kept (a test pins it),
            # so the entry says in words what 'some cells empty' covers here.
            k = sum(reasons.values())
            entry["status_note"] = (f"for {k} of the {len(empty)} {'test' if len(empty) == 1 else 'tests'} without a "
                                    "pressure value, the NASA cell holds a value that the pipeline flags and does "
                                    "not use (see empty_reasons and the point's value_flags); that cell is not empty")
        pressure_column[sid] = entry
    return plotted, points, pressure_column, off_tests


# --------------------------------------------------------------------------- not plotted

def build_not_plotted(tests, sources):
    ox = [t for t in tests if t["o2_basis"] == "oxidizer_stream"]
    no_val = [t for t in tests if t["o2_basis"] != "oxidizer_stream"
              and not (t["o2_basis"] == "ambient" and num(t["o2_pct"]) is not None)]
    for t in no_val:
        if num(t["o2_pct"]) is not None:
            raise SystemExit(f"{t['test_id']}: o2_pct without an o2_basis; no rule for that")

    def by_inv(rows):
        c = Counter(t["investigation_id"] for t in rows)
        return {k: c[k] for k in sorted(c, key=inv_key)}

    no_basis = [t for t in no_val if not t["o2_basis"]]
    oxygen_column = {}
    for sid in sorted({t["source_id"] for t in no_val}):
        rows = [t for t in no_val if t["source_id"] == sid]
        oxygen_column[sid] = {"status": "column, cells empty" if "o2_pct" in source_columns(sources[sid])
                              else "no column",
                              "tests": len(rows), "investigation_id": rows[0]["investigation_id"],
                              "source": f"pipeline/spec/sources.json#{sid}"}
    ambient_empty = [t for t in no_val if t["o2_basis"] == "ambient"]
    return ox, no_val, {
        "oxidizer_stream": {
            "n": len(ox),
            "without_oxygen_value": sum(1 for t in ox if num(t["o2_pct"]) is None),
            "by_investigation": by_inv(ox),
            "by_source": dict(sorted(Counter(t["source_id"] for t in ox).items())),
            "why": RULES["oxidizer_stream"],
        },
        "no_ambient_oxygen_value": {
            "n": len(no_val),
            "rule": RULES["no_ambient_oxygen_value"],
            "no_oxygen_basis": len(no_basis),
            "ambient_basis_without_value": len(ambient_empty),
            "ambient_basis_without_value_test_ids": [t["test_id"] for t in ambient_empty],
            "oxygen_column_by_source": oxygen_column,
            "by_investigation": by_inv(no_val),
            "by_fuel_phase": {k: v for k, v in sorted(Counter(t["fuel_phase"] for t in no_val).items(),
                                                     key=lambda kv: LANE_ORDER[kv[0]])},
        },
    }


def build_psi20(sources):
    src = sources[PSI20_SOURCE_ID]
    if src.get("investigation_id") != "PSI-20":
        raise SystemExit("sources.json acme_bre is not PSI-20")
    rel = f"data/psi/experimental_tables/{src['file']}"
    table = read_table(src["file"])
    rows = [dict(zip(table[0], r)) for r in table[1:] if any(c.strip() for c in r)]
    o2_col = next(h for h in rows[0] if h.lower().startswith("oxygen conc"))
    fl_col = next(h for h in rows[0] if h.lower().startswith("flames ignited"))
    numeric, odd, order = set(), [], []
    for r in rows:
        for tok in (x.strip() for x in r[o2_col].split(";")):
            if not tok:
                continue
            if re.fullmatch(r"\d+(\.\d+)?", tok):
                if tok not in numeric:
                    numeric.add(tok)
            else:
                odd.append({"cell": tok, "row": f"{r['Year']} {r['Month']} {r['Date']}"})
    order = sorted(numeric, key=float)
    notes = [r["Notes"].strip() for r in rows if r.get("Notes", "").strip()]
    pressure_note = next((s.strip() + "." for n in notes for s in n.split(".") if "pressure" in s.lower()), None)
    if pressure_note is None or pressure_note.rstrip(".") not in " ".join(notes):
        raise SystemExit("PSI-20: no pressure sentence found in the Notes column")
    return {
        "days": len(rows),
        "flames_ignited": sum(int(r[fl_col]) for r in rows),
        "oxygen_settings_as_written": order,
        "oxygen_cells_not_read_as_numbers": odd,
        "highest_numeric_setting_pct": max(float(x) for x in order),
        "balance_gas_as_written": ("diluted with nitrogen on a volume basis"
                                   if any("diluted with nitrogen on a volume basis" in n for n in notes) else None),
        "pressure": pressure_note,
        "table_notes_as_written": notes,
        "why": RULES["psi20_test_day_table"],
        "source": "PSI-20",
        "source_file": rel,
        "source_spec": f"pipeline/spec/sources.json#{PSI20_SOURCE_ID}",
    }


# --------------------------------------------------------------------------- targets

def ref_index(refs):
    out = {}
    for ref in refs["references"]:
        for it in ref.get("items", []):
            out[it["id"]] = (ref, it)
    return out


def _ref_target(idx, item_id, kind, label, as_written, **values):
    ref, it = idx[item_id]
    if as_written not in it["text"]:
        raise SystemExit(f"{item_id}: {as_written!r} is not in the item text")
    t = {"id": item_id if "id" not in values else values.pop("id"), "kind": kind, "label": label}
    t.update(values)
    t.update({"as_written": as_written, "source": f"pipeline/spec/references.json#{item_id}",
              "reference_id": ref["id"], "reference_title": ref["title"], "issuer": ref["issuer"],
              "reference_kind": ref["kind"], "access": ref["access"],
              "access_note": ACCESS_NOTE.get(ref["access"], ref["access"])})
    return t


def build_targets(refs, scen, scoring, tests, scenario_tests):
    idx = ref_index(refs)
    targets = []
    # nasa_design_atmosphere: EAWG.atmospheres (four points)
    _, eawg = idx["EAWG.atmospheres"]
    for psia, o2 in eawg["values"]["atmospheres_psia_o2pct"]:
        kpa, conv = psia_to_kpa(psia)
        targets.append(_ref_target(
            idx, "EAWG.atmospheres", "nasa_design_atmosphere",
            # review: no 'recommended' on the page, even in an attribution (same rule as the scenario text);
            # the report's own caveat is kept
            f"NASA Exploration Atmospheres Working Group report: nominal atmosphere {psia} psia / {fmt(o2)}% O2 "
            "(listed in the report, which says it is not a requirement)",
            f"{psia} psia / {fmt(o2)}% O2", id=f"EAWG.atmospheres.{psia}psia_{fmt(o2)}pct",
            o2_pct=float(o2), pressure_kpa=kpa, pressure_psia=float(psia), pressure_conversion=conv,
            draw="point"))
    # EA.8.2-34
    _, ea = idx["EA.8.2-34"]
    kpa, conv = psia_to_kpa(ea["values"]["pressure_psia"])
    targets.append(_ref_target(
        idx, "EA.8.2-34", "nasa_design_atmosphere",
        f"NASA exploration atmosphere {ea['values']['pressure_psia']} psia / {fmt(ea['values']['o2_pct'])}% O2 "
        "(source read at abstract level)",
        f"{ea['values']['pressure_psia']} psia / {fmt(ea['values']['o2_pct'])}% O2",
        o2_pct=float(ea["values"]["o2_pct"]), pressure_kpa=kpa,
        pressure_psia=float(ea["values"]["pressure_psia"]), pressure_conversion=conv, draw="point"))
    # nasa_test_environment
    _, tb = idx["TB14639.worstcase"]
    kpa, conv = psia_to_kpa(tb["values"]["pressure_psia"])
    targets.append(_ref_target(
        idx, "TB14639.worstcase", "nasa_test_environment",
        # reader: the item says 'Test 1'; 'NASA-STD-6001B' (a revision letter) was not in it
        f"NASA Task Book report: Test 1 is conducted in the most severe environment expected in the "
        f"spacecraft, given there as {fmt(tb['values']['o2_pct'])}% oxygen at {tb['values']['pressure_psia']} psia",
        f"{fmt(tb['values']['o2_pct'])}% oxygen at {tb['values']['pressure_psia']} psia",
        o2_pct=float(tb["values"]["o2_pct"]), pressure_kpa=kpa,
        pressure_psia=float(tb["values"]["pressure_psia"]), pressure_conversion=conv, draw="point"))
    _, amb = idx["6001B.T1.ambient"]
    targets.append(_ref_target(
        idx, "6001B.T1.ambient", "nasa_test_environment",
        "NASA-STD-6001B test-laboratory ambient conditions (a definition for the test, not a cabin atmosphere)",
        f"{amb['values']['o2_pct']} percent oxygen, {amb['values']['pressure_kpa']} kPa",
        o2_pct=float(amb["values"]["o2_pct"]), pressure_kpa=float(amb["values"]["pressure_kpa"]),
        pressure_conversion="as written in kPa", draw="point"))
    # challenge_statement
    _, ch = idx["CH.moonbase"]
    kpa, conv = psia_to_kpa(ch["values"]["pressure_psia_max"])
    ch_t = _ref_target(
        idx, "CH.moonbase", "challenge_statement",
        # reader: the label dropped the item's hedge ('expected') and said 'challenge statement' twice; it is
        # now the item's own sentence, and the access note follows the reference (it was typed in)
        f"Challenge statement: {ch['text'].rstrip('. ')} "
        f"({ACCESS_NOTE.get(idx['CH.moonbase'][0]['access'], idx['CH.moonbase'][0]['access'])})",
        f"{fmt(ch['values']['o2_pct_min'])}% oxygen or more and {ch['values']['pressure_psia_max']} psi or less",
        o2_min=float(ch["values"]["o2_pct_min"]), pressure_max=kpa,
        pressure_psia_max=float(ch["values"]["pressure_psia_max"]), pressure_conversion=conv,
        draw="line_and_region")
    targets.append(ch_t)
    # team_preset
    presets = scoring["presets"]
    for pid, extra in (("iss", "team preset"),
                       ("lunar_habitat", "team preset: corner of the challenge-statement range"),
                       ("spacesuit", "team preset; given as text, off the oxygen axis of the map")):
        v = presets[pid]["values"]
        t = {"id": f"preset.{pid}", "kind": "team_preset",
             "label": f"{presets[pid]['label_en']} ({extra}): {fmt(v['o2_pct'])}% oxygen, {v['pressure_kpa']} kPa",
             "o2_pct": float(v["o2_pct"]), "pressure_kpa": float(v["pressure_kpa"]),
             "as_written": presets[pid]["source"],
             "source": f"scoring/scoring_config.json#presets.{pid}", "access": "team",
             "access_note": "the team's own value (ui role, scoring/scoring_config.json)",
             "draw": "text" if pid == "spacesuit" else "point"}
        if pid == "lunar_habitat" and (t["o2_pct"] != ch_t["o2_min"] or t["pressure_kpa"] != ch_t["pressure_max"]):
            raise SystemExit("lunar_habitat preset is no longer the corner of the challenge-statement range")
        targets.append(t)
    # team_counting_range: every scenario with oxygen and pressure ranges
    st = defaultdict(set)
    for r in scenario_tests:
        if r["tier"] == "atmosphere":
            st[r["scenario_id"]].add(r["test_id"])
    by_id = {t["test_id"]: t for t in tests}
    checks = {}
    for sc in scen["scenarios"]:
        rg = sc.get("ranges") or {}
        if "o2_pct" not in rg or "pressure_kpa" not in rg:
            continue
        o, p = rg["o2_pct"], rg["pressure_kpa"]
        inside = [t for t in tests if t["o2_basis"] == "ambient"
                  and in_range(num(t["o2_pct"]), o) and in_range(num(t["pressure_kpa"]), p)]
        ids = {t["test_id"] for t in inside}
        expected = {i for i in st[sc["id"]] if by_id[i]["o2_basis"] == "ambient"}
        checks[sc["id"]] = {"tests_inside": len(ids), "scenario_tests_tier_atmosphere_ambient": len(expected),
                            "same_tests": ids == expected}
        inv = Counter(t["investigation_id"] for t in inside)
        pr_inv = defaultdict(list)
        for t in inside:
            pr_inv[t["investigation_id"]].append(num(t["pressure_kpa"]))
        pr = [num(t["pressure_kpa"]) for t in inside]
        label = (f"Team counting range for '{sc['label']}' (the team's choice, used for the need counts; "
                 "drawn dashed)")
        # reader (coord/decisions.md 14:15): where the range rests on the challenge statement and its pressure
        # reaches above the challenge-statement pressure, the label says so
        if "CH.moonbase" in (sc.get("basis") or []) and p.get("max") is not None and p["max"] > ch_t["pressure_max"]:
            label += (f"; its pressure range ({'up to' if p.get('max_inclusive') else 'below'} {fmt(p['max'])} kPa) is "
                      f"wider than the {fmt(ch_t['pressure_max'])} kPa ({fmt(ch_t['pressure_psia_max'])} psi) of the "
                      "challenge statement")
        targets.append({
            "id": f"range.{sc['id']}", "kind": "team_counting_range",
            "label": label,
            "o2_min": o.get("min"), "o2_max": o.get("max"),
            "o2_min_inclusive": o.get("min_inclusive", True), "o2_max_inclusive": o.get("max_inclusive", False),
            "pressure_min": p.get("min"), "pressure_max": p.get("max"),
            "pressure_min_inclusive": p.get("min_inclusive", True),
            "pressure_max_inclusive": p.get("max_inclusive", False),
            "as_written": sc.get("note", ""),
            "basis_items": sc.get("basis", []),
            "tests_inside": len(ids),
            "tests_inside_by_investigation": {k: inv[k] for k in sorted(inv, key=inv_key)},
            "tests_inside_pressure_kpa_range": [min(pr), max(pr)] if pr else None,
            "tests_inside_pressure_kpa_range_by_investigation": {
                k: [min(pr_inv[k]), max(pr_inv[k])] for k in sorted(pr_inv, key=inv_key)},
            "source": f"pipeline/spec/scenarios.json#{sc['id']}", "access": "team",
            "access_note": "the team's own range (data role, pipeline/spec/scenarios.json)",
            "draw": "text" if (o.get("min") or 0) > 40 else "region_dashed",
        })
    return targets, checks


# --------------------------------------------------------------------------- Saffire IV to VI (only if data adds it)

_SAFFIRE_LATE = re.compile(r"saffire[\s-]*(iv|v|vi|4|5|6)\b|ICES-2024-365", re.I)


def find_saffire_item(refs):
    """(reference, item) for Saffire IV to VI: the item SAF456.conditions if it exists, else any item that
    names those flights or their paper; None when the data role has added none."""
    for ref in refs["references"]:
        for it in ref.get("items", []):
            if it.get("id") == SAFFIRE_ITEM:
                return ref, it
    for ref in refs["references"]:
        ref_hit = _SAFFIRE_LATE.search(" ".join(str(ref.get(k, "")) for k in ("id", "title", "version")))
        for it in ref.get("items", []):
            if ref_hit or _SAFFIRE_LATE.search(f"{it.get('id', '')} {it.get('text', '')}"):
                return ref, it
    return None


def saffire_markers(found):
    """Markers only from machine-readable values of the item: a list of {pressure_kpa, o2_pct} pairs."""
    ref, it = found
    vals = it.get("values") or {}
    rows = None
    for v in vals.values():
        if isinstance(v, list) and v and all(isinstance(x, dict) and "o2_pct" in x and "pressure_kpa" in x for x in v):
            rows = v
            break
    if rows is None:
        return None
    # review: 'hollow' already means 'carbon dioxide or helium added' for the PSI points
    # (labels.hollow_marker_meaning), so the flight tests get a marker of their own.
    return [{"o2_pct": float(x["o2_pct"]), "pressure_kpa": float(x["pressure_kpa"]),
             # reader: the item does not say whose flight it was; the label says what the mark is and that
             # it is not a PSI test and not counted
             "label": FLIGHT_LABEL, "marker": "cross", "counted": False,
             "what": "sample test conditions as listed in Table 1 of the paper (cited, not a PSI test)",
             **({"material": x["material"]} if "material" in x else {}),
             **({"flight_sample": x["flight_sample"]} if "flight_sample" in x else {}),
             **({"flight": x["flight"]} if "flight" in x else {}),
             "source": f"pipeline/spec/references.json#{it['id']}", "access": ref["access"]} for x in rows]


# --------------------------------------------------------------------------- assemble

def build():
    tests = read_csv(TESTS)
    scenario_tests = read_csv(SCENARIO_TESTS)
    sources = {s["id"]: s for s in read_json(SOURCES)["sources"]}
    refs = read_json(REFERENCES)
    scen = read_json(SCENARIOS)
    scoring = read_json(SCORING)

    plotted, points, pressure_column, off_tests = build_points(tests, sources)
    ox, no_val, not_plotted = build_not_plotted(tests, sources)
    psi20 = build_psi20(sources)
    not_plotted["psi20_test_day_table"] = psi20
    targets, range_checks = build_targets(refs, scen, scoring, tests, scenario_tests)

    total = len(tests)
    if len(plotted) + len(ox) + len(no_val) != total:
        raise SystemExit(f"groups do not sum: {len(plotted)} + {len(ox)} + {len(no_val)} != {total}")
    if sum(p["n_tests"] for p in points) != len(plotted):
        raise SystemExit("points do not sum to the plotted tests")
    if any(p["fuel_phase"] == "solid" and p["pressure_kpa"] is not None for p in points):
        raise SystemExit("a solid point has a pressure value")

    with_p = [t for t in plotted if num(t["pressure_kpa"]) is not None]
    tid_inv = {t["test_id"]: t["investigation_id"] for t in plotted}
    composition_off = {
        "n": len(off_tests),
        "by_investigation": dict(sorted(Counter(tid_inv[k] for k in off_tests).items())),
        "rule": (f"For tables with a nitrogen column, the oxygen, nitrogen and added-gas fractions of the NASA row "
                 f"are summed as written; a point lists the sums that differ from 1 by more than "
                 f"{COMPOSITION_TOLERANCE}. Reported, not corrected."),
    }
    without_p = [t for t in plotted if num(t["pressure_kpa"]) is None]
    bg_of = {tid: p["balance_gas"] for p in points for tid in p["test_ids"]}
    phase_rows = {ph: [t for t in plotted if t["fuel_phase"] == ph] for ph, _ in LANES}
    max_o2 = {ph: max(num(t["o2_pct"]) for t in rows) for ph, rows in phase_rows.items() if rows}
    min_o2 = {ph: min(num(t["o2_pct"]) for t in rows) for ph, rows in phase_rows.items() if rows}
    ge30 = {ph: sum(1 for t in rows if num(t["o2_pct"]) >= 30) for ph, rows in phase_rows.items()}
    wo_inv = Counter(t["investigation_id"] for t in without_p)
    no_val_phase = not_plotted["no_ambient_oxygen_value"]["by_fuel_phase"]
    sums = {
        "tests_csv_rows": total,
        "plotted": len(plotted),
        "plotted_with_pressure": len(with_p),
        "plotted_without_pressure": len(without_p),
        "plotted_by_phase": {ph: len(rows) for ph, rows in phase_rows.items()},
        "with_pressure_by_phase": {ph: sum(1 for t in with_p if t["fuel_phase"] == ph) for ph, _ in LANES},
        "without_pressure_by_investigation": {k: wo_inv[k] for k in sorted(wo_inv, key=lambda k: -wo_inv[k])},
        "with_pressure_above_110_kpa": sum(1 for t in with_p if num(t["pressure_kpa"]) > 110),
        "oxidizer_stream": len(ox),
        "no_ambient_oxygen_value": len(no_val),
        "total": len(plotted) + len(ox) + len(no_val),
        "points": len(points),
        "points_with_pressure": sum(1 for p in points if p["pressure_kpa"] is not None),
        "points_without_pressure": sum(1 for p in points if p["pressure_kpa"] is None),
        "balance_gas_with_pressure": {b: sum(1 for t in with_p if bg_of[t["test_id"]] == b) for b in BALANCE_GAS},
        "balance_gas_all_plotted": {b: sum(1 for t in plotted if bg_of[t["test_id"]] == b) for b in BALANCE_GAS},
        "tests_gas_fractions_not_summing_to_1": composition_off,
        "max_o2_by_phase": max_o2,
        "min_o2_by_phase": min_o2,
        "max_o2_ambient": max(max_o2.values()),
        "at_or_above_30_by_phase": ge30,
        "lanes": {ph: {"label": name, "plotted": len(phase_rows[ph]),
                       "max_o2_pct": max_o2.get(ph), "at_or_above_30_pct_o2": ge30[ph],
                       "not_plotted": sum(1 for t in ox + no_val if t["fuel_phase"] == ph),
                       "not_plotted_oxidizer_stream": sum(1 for t in ox if t["fuel_phase"] == ph),
                       "not_plotted_no_ambient_oxygen_value": sum(1 for t in no_val if t["fuel_phase"] == ph)}
                  for ph, name in LANES},
        "flight_tests_not_in_psi_counted": 0,
        "counting_range_checks": range_checks,
        "rules": {k: RULES[k] for k in ("plotted", "balance_gas", "pressure_kpa_null")},
    }

    # lane notes and labels, filled by code from the counts above
    solid_srcs = [s for s in sources.values() if (s.get("constants") or {}).get("fuel_phase") == "solid"]
    solid_has_pressure = [s["id"] for s in solid_srcs if "pressure_kpa" in source_columns(s)
                          or any(_PRESSURE.search(h) for h in raw_header(s["file"]))]
    if solid_has_pressure:
        raise SystemExit(f"solid tables with a pressure column: {solid_has_pressure}; the fixed note would be wrong")

    def invs(rows):
        return ", ".join(sorted({t["investigation_id"] for t in rows}, key=inv_key))

    lane_notes = {}
    for ph, name in LANES:
        rows = phase_rows[ph]
        lane_notes[ph] = {
            "name": name,
            "text": (f"{name}: {len(rows)} tests with a recorded ambient oxygen value ({invs(rows)}); "
                     f"recorded oxygen {fmt(min_o2[ph])}% to {fmt(max_o2[ph])}%; {ge30[ph]} at 30% oxygen or more."),
        }
    solid_unrec = no_val_phase.get("solid", 0)
    lane_notes["solid"]["end_label"] = (
        f"no solid-sample test with a recorded oxygen value above {fmt(max_o2['solid'])}% in the tables "
        f"of the {len(read_json(MANIFEST)['investigations'])} PSI investigations ({solid_unrec} solid-sample "
        "tests record no oxygen value)")
    lane_notes["solid"]["pressure_note"] = "pressure is not a column in the PSI tables of the solid-sample tests"

    n_inv = len(read_json(MANIFEST)["investigations"])
    if any(t["gravity_level"] != "microgravity" for t in plotted):
        raise SystemExit("a plotted test is not a microgravity test; the caption would be wrong")
    caption = [first_caption(len(plotted), len({t["investigation_id"] for t in plotted}), n_inv), SECOND_CAPTION]
    caption.append(
        f"Gas-burner flames that emulate condensed fuels (PSI-20) were run at listed oxygen concentrations up to "
        f"{fmt(psi20['highest_numeric_setting_pct'])}% (approximate, as the table notes say); that table is per "
        "test day and is not plotted.")
    caption_sources = [
        ["data/pipeline/tests.csv", "pipeline/spec/references.json", "pipeline/spec/scenarios.json",
         "scoring/scoring_config.json#presets"],
        ["data/pipeline/tests.csv", "pipeline/spec/sources.json"],
        ["PSI-20.title", "PSI-20.objective", psi20["source"], psi20["source_spec"]],
    ]

    found = find_saffire_item(refs)
    markers = saffire_markers(found) if found else None
    saffire_note = None
    if found and markers:
        # review: 'at such atmospheres' pointed at nothing in a caption list, and 'not in PSI (team
        # search)' could not be checked by code. The note now gives the ranges of the markers it
        # describes, says what the code can check (none of the 24 investigations used here is one of
        # these flights) and carries the caveats the data role recorded with the item.
        o2s = [m["o2_pct"] for m in markers]
        ps = [m["pressure_kpa"] for m in markers]
        late = [i["accession"] for i in read_json(MANIFEST)["investigations"]
                if re.search(r"(saffire|spacecraft fire (safety )?experiment)[\s-]*(iv|v|vi)\b", i.get("title", "") + " "
                             + i.get("acronym", ""), re.I)]
        # review (14 Nov, the data role's caveats on SAF456.conditions): the values are the sample test
        # conditions of the samples considered in that paper (Table 1's own title), not every Saffire IV to
        # VI sample, and they are never called measured values or set points; numbers are cited only.
        n_word = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}.get(len(markers), str(len(markers)))
        # reader: 'ICES-2024-365' alone told a reader nothing; the title comes from references.json (the part
        # before the author list). The note is a sentence and now ends with a full stop.
        title = str(found[0].get("title", "")).split(" (")[0].strip()
        paper = f"the paper '{title}' (ICES-2024-365)" if title and "ICES-2024-365" in str(found[0]) else \
            "the paper cited" if not title else f"the paper '{title}'"
        text = (f"Outside PSI, Table 1 of {paper} lists the sample test conditions of the {n_word} Saffire IV to "
                f"VI samples considered in that paper, from {min(o2s):.1f} to {max(o2s):.1f} mol % oxygen and "
                f"{min(ps):.1f} to {max(ps):.1f} kPa (drawn as crosses; cited, never counted)")
        if not late:
            text += f"; none of the {len(read_json(MANIFEST)['investigations'])} PSI investigations used here is one of these flights"
        note_txt = " ".join(str(x.get("note", "")) for x in found)
        if "not checked by a human" in note_txt:
            text += "; the values were read from the paper by an AI assistant and not checked by a person"
        text += "."
        saffire_note = {
            "text": text,
            "source": f"pipeline/spec/references.json#{found[1]['id']}",
        }
        caption.append(saffire_note["text"])
        caption_sources.append([saffire_note["source"]])

    payload = {
        "labels": {
            "title": "Where the PSI test tables stop",
            "lane_notes": lane_notes,
            "caption": caption,
            "caption_sources": caption_sources,
            "saffire_note": saffire_note,
            "saffire_status": ("item found in references.json; markers written from its values" if saffire_note
                               else "item found in references.json but its values are not machine-readable; "
                                    "nothing written" if found
                               else "no Saffire IV to VI item in pipeline/spec/references.json; nothing written"),
            "hollow_marker_meaning": "carbon dioxide or helium added to the atmosphere (balance_gas co2_added, he_added)",
        },
        "axes": {
            "o2_pct": {"label": "Ambient oxygen, % (volume or mole fraction, as recorded in the PSI table)",
                       "unit": "%", "data_min": min(min_o2.values()), "data_max": max(max_o2.values())},
            # reader: the tables give pressure in mmHg, atm or bar; the pipeline converts, so 'as recorded'
            # was not exact
            "pressure_kpa": {"label": ("Pressure, kPa (the value in the PSI table, converted to kPa by the team "
                                       "pipeline; null where the map has no value)"), "unit": "kPa",
                             "data_min": min(num(t["pressure_kpa"]) for t in with_p),
                             "data_max": max(num(t["pressure_kpa"]) for t in with_p)},
            "lanes": [{"fuel_phase": ph, "label": name} for ph, name in LANES],
            "gravity": ("every plotted test is a microgravity test (tests.csv gravity_level, set per table by "
                        "the team from the PSI record)"),
        },
        "points": points,
        "pressure_column": pressure_column,
        "not_plotted": not_plotted,
        "targets": targets,
        "flight_tests_not_in_psi": markers if saffire_note else None,
        "sums": sums,
    }
    return payload


def anchor_diffs(payload):
    s, np_ = payload["sums"], payload["not_plotted"]
    got = {
        "plotted": s["plotted"], "plotted_with_pressure": s["plotted_with_pressure"],
        "plotted_without_pressure": s["plotted_without_pressure"], "plotted_by_phase": s["plotted_by_phase"],
        "oxidizer_stream": s["oxidizer_stream"],
        "oxidizer_stream_without_oxygen_value": np_["oxidizer_stream"]["without_oxygen_value"],
        "no_ambient_oxygen_value": s["no_ambient_oxygen_value"],
        "no_ambient_oxygen_value_by_phase": np_["no_ambient_oxygen_value"]["by_fuel_phase"],
        "total": s["total"], "balance_gas_with_pressure": s["balance_gas_with_pressure"],
        "points_with_pressure": s["points_with_pressure"],
        "with_pressure_above_110_kpa": s["with_pressure_above_110_kpa"],
        "without_pressure_by_investigation": s["without_pressure_by_investigation"],
        "max_o2_by_phase": s["max_o2_by_phase"], "at_or_above_30_by_phase": s["at_or_above_30_by_phase"],
        "psi20_days": np_["psi20_test_day_table"]["days"],
        "psi20_flames_ignited": np_["psi20_test_day_table"]["flames_ignited"],
        "lunar_habitat_range_tests": s["counting_range_checks"].get("lunar_habitat", {}).get("tests_inside"),
    }
    return {k: {"design": ANCHORS[k], "now": got[k]} for k in ANCHORS if got[k] != ANCHORS[k]}


def write(path=OUT):
    payload = build()
    block = metamod.meta(BUILT_BY, config.NO_MODEL, INPUTS + [ROOT / payload["not_plotted"]["psi20_test_day_table"]
                                                                ["source_file"]])
    return payload, metamod.write_json(path, payload, block)


def main(argv):
    payload, block = write()
    s = payload["sums"]
    print(f"wrote {OUT.relative_to(ROOT)}  content_sha256 {block['content_sha256']}")
    for k in ("tests_csv_rows", "lanes", "plotted", "plotted_with_pressure", "plotted_without_pressure", "plotted_by_phase",
              "with_pressure_by_phase", "without_pressure_by_investigation", "with_pressure_above_110_kpa",
              "oxidizer_stream", "no_ambient_oxygen_value", "total", "points", "points_with_pressure",
              "points_without_pressure", "balance_gas_with_pressure", "balance_gas_all_plotted",
              "max_o2_by_phase", "min_o2_by_phase", "at_or_above_30_by_phase", "counting_range_checks"):
        print(f"  {k}: {json.dumps(s[k])}")
    npl = payload["not_plotted"]
    print(f"  oxidizer_stream: {json.dumps({k: v for k, v in npl['oxidizer_stream'].items() if k != 'why'})}")
    print(f"  no_ambient_oxygen_value: "
          f"{json.dumps({k: v for k, v in npl['no_ambient_oxygen_value'].items() if k != 'rule'})}")
    p20 = npl["psi20_test_day_table"]
    print(f"  psi20: days {p20['days']}, flames {p20['flames_ignited']}, settings {p20['oxygen_settings_as_written']}, "
          f"odd cells {[c['cell'] for c in p20['oxygen_cells_not_read_as_numbers']]}")
    print(f"  pressure_column: {json.dumps({k: v['status'] for k, v in payload['pressure_column'].items()})}")
    print(f"  targets: {len(payload['targets'])} ({json.dumps(Counter(t['kind'] for t in payload['targets']))})")
    print(f"  saffire: {payload['labels']['saffire_status']}")
    diffs = anchor_diffs(payload)
    if diffs:
        print("DIFFERENCES from the design's anchors:")
        for k, v in diffs.items():
            print(f"  {k}: design {json.dumps(v['design'])}, now {json.dumps(v['now'])}")
        if "--strict" in argv:
            return 1
    else:
        print("all design anchors match")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
