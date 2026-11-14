#!/usr/bin/env python3
# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Step 1 of the data pipeline: PSI experimental tables -> clean test tables.

Every number in the outputs is either copied from a NASA source cell or
computed from source cells by a rule written in this file. Nothing is
estimated. A value that is missing or unreadable in the source stays empty
(NaN), never 0. Every output row keeps its source file and source row.

Outputs (data/derived/)
    tests_conditions.csv  one row per test for 11 tables: common columns only
    tests_flex.csv        FLEX droplet tests with results
    tests_bass2.csv       BASS-II solid-fuel tests with results
    tests_long.csv        team format: one row per test and result
    tests_dictionary.csv  meaning, unit and rule for the output columns

Column meanings come from
    FLEX:    NASA/TP-2015-216046, Appendix A.1 and Table IX
    BASS-II: PSI-25 "BASS-II_ReadMe.docx" (Science Documents)
    others:  column names and the PSI investigation descriptions

Usage:  python3 scripts/build_test_tables.py
"""
import csv
import io
import os
import re

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "psi", "experimental_tables")
OUT = os.path.join(ROOT, "data", "derived")
T = "PSI-{}_Experimental table_{}.csv"
FLEX_FILE = T.format(69, "FLEX")
BASS2_FILE = T.format(25, "BASS-II")

MMHG_TO_KPA = 0.133322368
ATM_TO_KPA = 101.325
BAR_TO_KPA = 100.0
INCH_TO_MM = 25.4
PPM_TO_PCT = 1e-4
DUCT_MAX_CMS = 40.0
NUM = re.compile(r"^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$")
FIRST_NUM = re.compile(r"\d+(?:\.\d+)?|\.\d+")


def read_rows(name):
    """(header, [(source_row, cells)]); the header is source row 1."""
    raw = open(os.path.join(SRC, name), "rb").read().decode("utf-8-sig", "replace")
    records = [[c.strip() for c in r] for r in csv.reader(io.StringIO(raw))]
    header = records[0]
    rows = [(i + 1, dict(zip(header, (r + [""] * len(header))[:len(header)])))
            for i, r in enumerate(records) if i > 0 and any(r)]
    return header, rows


def num(cell):
    """Plain number or None. '~6', '>500', 'OR', 'RAMP' return None."""
    return float(cell) if NUM.match(cell or "") else None


def leading_number(cell):
    """First number in a cell that carries its unit, e.g. '20 cm/s' -> 20."""
    m = FIRST_NUM.search(cell or "")
    return float(m.group(0)) if m else None


def o2_from_text(cell, flags):
    """'21.5', '~ 21.5', '21.5 - 21.7', '22.1 to 22.0' -> percent."""
    values = [float(v) for v in FIRST_NUM.findall(cell or "")]
    if not values:
        return None
    if len(values) >= 2:
        flags.append("o2_given_as_range_midpoint_used")
        return round(sum(values[:2]) / 2, 3)
    if "~" in cell:
        flags.append("o2_approximate_in_source")
    return values[0]


# --------------------------------------------------------------------- FLEX
def build_flex():
    header, rows = read_rows(FLEX_FILE)
    h = {k: header[i] for i, k in enumerate(
        ["n", "ident", "date", "gmt", "fuel", "p", "o2", "n2", "co2", "he",
         "d0", "de", "k", "t", "end"])}
    out = []
    for source_row, r in rows:
        flags = []
        pressure = num(r[h["p"]])
        if pressure is not None and pressure <= 0:
            flags.append("pressure_zero_in_source")
            pressure = None
        fr = [num(r[h[k]]) for k in ("o2", "n2", "co2", "he")]
        if None not in fr and abs(sum(fr) - 1.0) > 0.011:
            flags.append("mole_fractions_do_not_sum_to_1")
        o2, n2, co2, he = [None if f is None else round(f * 100, 4) for f in fr]
        diluent = "CO2+He" if (co2 and he) else "CO2" if co2 else "He" if he else "N2"
        d0, de = num(r[h["d0"]]), num(r[h["de"]])
        if r[h["d0"]] and d0 is None:
            flags.append("initial_diameter_unreadable_in_source")
        if r[h["de"]] and de is None:
            flags.append("extinction_diameter_unreadable_in_source")
        burn = num(r[h["t"]])
        if r[h["t"]] and burn is None:
            burn = num(r[h["t"]].lstrip("~"))
            if burn is not None:
                flags.append("burn_time_approximate_in_source")
        ratio = None
        if d0 and de is not None:
            ratio = round(de / d0, 4)
            if ratio > 1.0:
                flags.append("extinction_diameter_larger_than_initial")
        out.append({
            "test_id": f"FLEX-{int(r[h['n']]):03d}", "investigation_id": "PSI-69",
            "flex_identifier": r[h["ident"]], "test_date": r[h["date"]],
            "fuel_material": r[h["fuel"]].lower(), "fuel_phase": "liquid",
            "sample_geometry": "droplet", "initial_diameter_mm": d0,
            "o2_pct": o2, "o2_basis": "ambient", "n2_pct": n2, "co2_pct": co2, "he_pct": he,
            "diluent": diluent,
            "pressure_kpa": None if pressure is None else round(pressure * MMHG_TO_KPA, 3),
            "pressure_source_mmhg": num(r[h["p"]]), "flow_cms": None,
            "outcome": r[h["end"]].lower(), "extinction_diameter_mm": de,
            "burning_rate_mm2_s": num(r[h["k"]]), "burn_time_s": burn,
            "extinction_to_initial_diameter_ratio": ratio,
            "flags": ";".join(flags), "source_file": FLEX_FILE, "source_row": source_row,
        })
    return pd.DataFrame(out)


# ------------------------------------------------------------------ BASS-II
ROD_INCH = [(r"1/4", 0.25), (r"3/8", 0.375), (r"1/2", 0.5), (r"0\.5\s*\"", 0.5)]


def parse_material(raw):
    """Material, geometry and the dimensions that are stated unambiguously."""
    s = raw.lower()
    info = dict.fromkeys(["fuel_material", "sample_geometry", "thickness_mm", "width_cm",
                          "rod_diameter_mm", "sides_burning", "sample_color"])
    width = re.search(r"(\d+(?:\.\d+)?)\s*cm", s)
    if "sibal" in s:
        info.update(fuel_material="SIBAL fabric (75% cotton, 25% fiberglass)",
                    sample_geometry="fabric sheet", width_cm=float(width.group(1)) if width else None)
    elif "nomex" in s:
        info.update(fuel_material="Nomex III fabric", sample_geometry="fabric sheet")
    elif "wax" in s or "candle" in s:
        info.update(fuel_material="Japan wax", sample_geometry="candle")
    elif "rod" in s:
        info.update(fuel_material="PMMA", sample_geometry="rod")
        for pattern, inches in ROD_INCH:
            if re.search(pattern, s):
                info["rod_diameter_mm"] = round(inches * INCH_TO_MM, 3)
                break
        info["sample_color"] = "clear" if "clear" in s else "black" if "blac" in s else None
    elif "spher" in s:
        info.update(fuel_material="PMMA", sample_geometry="spherical section",
                    width_cm=float(width.group(1)) if width else None)
    else:
        # The ReadMe states that the unlabelled "micron film" samples are PMMA.
        micron = re.search(r"(\d+(?:\.\d+)?)\s*micron", s)
        mm = re.search(r"(\d+(?:\.\d+)?)\s*mm", s)
        thick = float(micron.group(1)) / 1000 if micron else float(mm.group(1)) if mm else None
        if thick is not None:
            sides = re.search(r"([12])\s*sided", s)
            info.update(fuel_material="PMMA", thickness_mm=round(thick, 4),
                        sample_geometry="film" if thick < 1.0 else "slab",
                        width_cm=float(width.group(1)) if width else None,
                        sides_burning=int(sides.group(1)) if sides else None)
    return info


def parse_flow(cell):
    """'Air display' is the duct flow speed in cm/s read off the video
    (ReadMe). A cell can list the settings used in one test, e.g.
    '5  3  2   ext'. Control-box 'pot' settings are not speeds; dropped."""
    text = re.sub(r"pot\s*[\d.]+|[\d.]+\s*pot", " ", cell.lower())
    numbers = [float(n) for n in re.findall(r"(?<![<\d.])\d+(?:\.\d+)?", text)]
    # The duct could impose at most 40 cm/s (PSI-25 description). Larger
    # numbers in this cell are fan-display readings written in the wrong
    # column, so they are not flow speeds.
    fan_values = [n for n in numbers if n > DUCT_MAX_CMS]
    numbers = [n for n in numbers if n <= DUCT_MAX_CMS]
    return {
        "fan_reading_in_flow_cell": bool(fan_values),
        "flow_first_cms": numbers[0] if numbers and not text.strip().startswith("<") else None,
        "flow_min_cms": min(numbers) if numbers else None,
        "flow_max_cms": max(numbers) if numbers else None,
        "flow_settings_count": len(numbers) or None,
        "flow_went_below_1_cms": "<1" in text.replace(" ", ""),
        "flow_event_noted": "blowoff" if "blowoff" in text else "extinction" if "ext" in text else None,
    }


def build_bass2():
    header, rows = read_rows(BASS2_FILE)
    h = {k: header[i] for i, k in enumerate(
        ["pi", "test", "date", "gmt", "sample", "material", "restrictor", "fan", "air",
         "gain", "frames", "o2_i", "o2_f", "co2_i", "co2_f", "co_i", "co_f"])}
    out = []
    for source_row, r in rows:
        flags = []
        rec = {"test_id": f"BASS2-{r[h['test']]}", "investigation_id": "PSI-25",
               "principal_investigator": r[h["pi"]], "test_date": r[h["date"]],
               "sample_number": r[h["sample"]], "material_as_written": r[h["material"]],
               "fuel_phase": "solid"}
        rec.update(parse_material(r[h["material"]]))
        if rec["fuel_material"] is None:
            flags.append("material_not_parsed")
        rec["flow_restrictor"] = num(r[h["restrictor"]])
        rec["air_display_as_written"] = r[h["air"]]
        rec.update(parse_flow(r[h["air"]]))
        if r[h["air"]] and rec["flow_min_cms"] is None and not rec["flow_went_below_1_cms"]:
            flags.append("flow_not_parsed")
        if rec.pop("fan_reading_in_flow_cell"):
            flags.append("fan_reading_in_flow_cell_ignored")

        o2_i, o2_f = num(r[h["o2_i"]]), num(r[h["o2_f"]])
        d_o2 = None
        if o2_i is not None and o2_f is not None:
            if o2_f > o2_i + 0.5:
                flags.append("final_o2_above_initial_in_source")
            elif o2_f < 5.0:
                flags.append("final_o2_implausibly_low_in_source")
            else:
                d_o2 = round(o2_i - o2_f, 4)
        co2_i, co2_f = num(r[h["co2_i"]]), num(r[h["co2_f"]])
        d_co2 = round(co2_f - co2_i, 4) if None not in (co2_i, co2_f) else None
        co_i, co_f = num(r[h["co_i"]]), num(r[h["co_f"]])
        if r[h["co_f"]].lower() in ("or", "over") or r[h["co_i"]].lower() == "or":
            flags.append("co_over_range_above_1000_ppm")
        if r[h["co_f"]].startswith(">"):
            flags.append("co_final_given_as_lower_bound")
        d_co = round(co_f - co_i, 3) if None not in (co_i, co_f) else None
        ratio = None
        if d_co is not None and d_co2 is not None and d_co > 0 and d_co2 >= 0.05:
            ratio = round(d_co * PPM_TO_PCT / d_co2, 5)
        rec.update({
            "o2_pct": o2_i, "o2_basis": "ambient", "o2_final_pct": o2_f, "pressure_kpa": None,
            "diluent": "N2",
            "co2_initial_pct": co2_i, "co2_final_pct": co2_f,
            "co_initial_ppm": co_i, "co_final_ppm": co_f,
            "o2_consumed_pct_points": d_o2, "co2_produced_pct_points": d_co2,
            "co_produced_ppm": d_co, "co_to_co2_molar_ratio": ratio,
            "flags": ";".join(flags), "source_file": BASS2_FILE, "source_row": source_row,
        })
        out.append(rec)
    return pd.DataFrame(out)


# ------------------------------------------- other tables: conditions only
def cond(test_id, inv, fuel, phase, o2, basis, p_kpa, flow, diluent, outcome,
         flags, source_file, source_row, geometry=None):
    return {"test_id": test_id, "investigation_id": inv, "fuel_material": fuel,
            "fuel_phase": phase, "sample_geometry": geometry, "o2_pct": o2,
            "o2_basis": basis if o2 is not None else None,
            "pressure_kpa": None if p_kpa is None else round(p_kpa, 3),
            "flow_cms": flow, "diluent": diluent, "outcome": outcome,
            "flags": ";".join(flags), "source_file": source_file, "source_row": source_row}


def pct(fraction):
    return None if fraction is None else round(fraction * 100, 4)


def build_other_conditions():
    out = []

    name = T.format(39, "CFI")
    for row, r in read_rows(name)[1]:
        he = num(r["Helium"])
        p = leading_number(r["Pressure"])
        out.append(cond(f"CFI-{r['Flex Number']}", "PSI-39", r["Fuel"], "liquid",
                        pct(num(r["Oxygen"])), "ambient",
                        None if p is None else p * ATM_TO_KPA, None,
                        "He" if he else "N2", None, [], name, row, "droplet"))

    for inv, label, o2_col, flow_col in ((98, "SAFFIRE-1", "Percent O2", "Air Flow (cm/s)"),
                                         (99, "SAFFIRE-2", "Percent O2 (Note 1)", "Air Flow (cm/s)"),
                                         (100, "SAFFIRE-3", None, "Air Flow")):
        name = T.format(inv, label)
        for row, r in read_rows(name)[1]:
            flow = leading_number(r.get(flow_col, ""))
            if flow is None:       # note rows and pre-test flow visualisation rows
                continue
            flags = []
            o2 = o2_from_text(r[o2_col], flags) if o2_col else None
            direction = (r.get("Flow Direction") or r.get("Direction") or "").lower() or None
            out.append(cond(f"{label}-{r['Sample Number']}", f"PSI-{inv}", r["Material"], "solid",
                            o2, "ambient", None, flow, "N2", direction, flags, name, row,
                            "sheet or slab"))

    name = T.format(159, "CFI-G_Normal Flames")
    for row, r in read_rows(name)[1]:
        p = num(r["approx p (bar)"])
        out.append(cond(f"CFIG-N-{r['Test'].replace(' ', '')}", "PSI-159", r["Fuel"], "gas",
                        pct(num(r["XO2 before test"])), "ambient",
                        None if p is None else p * BAR_TO_KPA, None, "N2",
                        "hot ignition" if r["Hot ignition"].lower() == "yes" else "no hot ignition",
                        [], name, row, "spherical burner"))

    name = T.format(159, "CFI-G_Inverse Flames")
    for row, r in read_rows(name)[1]:
        p = num(r["approx p (bar)"])
        out.append(cond(f"CFIG-I-{r['Test'].replace(' ', '')}", "PSI-159", r["Fuel"], "gas",
                        pct(num(r["XO2"])), "oxidizer_stream",
                        None if p is None else p * BAR_TO_KPA, None, "N2",
                        "hot ignition" if r["Hot ignition"].lower() == "yes" else "no hot ignition",
                        [], name, row, "spherical burner"))

    name = T.format(10, "Flame Design_Normal Flame")
    for row, r in read_rows(name)[1]:
        p = num(r["pinit (atm)"])
        out.append(cond(f"FD-N-{r['Test']}", "PSI-10", r["Fuel"], "gas",
                        pct(num(r["XO2 (init)"])), "ambient",
                        None if p is None else p * ATM_TO_KPA, None, "N2", None,
                        [], name, row, "spherical burner"))

    name = T.format(10, "Flame Design_Inverse Flame")
    for row, r in read_rows(name)[1]:
        p = num(r["pinit (atm)"])
        flags = [] if num(r["XO2"]) is not None else ["o2_not_numeric_in_source"]
        out.append(cond(f"FD-I-{r['Test']}", "PSI-10", "C2H4", "gas",
                        pct(num(r["XO2"])), "oxidizer_stream",
                        None if p is None else p * ATM_TO_KPA, None, "N2", None,
                        flags, name, row, "spherical burner"))
    return pd.DataFrame(out)


COMMON = ["test_id", "investigation_id", "fuel_material", "fuel_phase", "sample_geometry",
          "o2_pct", "o2_basis", "pressure_kpa", "flow_cms", "diluent", "outcome", "flags",
          "source_file", "source_row"]


def build_conditions(flex, bass2):
    b = bass2.rename(columns={"flow_first_cms": "flow_cms", "flow_event_noted": "outcome"})
    return pd.concat([flex[COMMON], b[COMMON], build_other_conditions()[COMMON]],
                     ignore_index=True)


def to_long(flex, bass2):
    """Team format: one row per test and per result value."""
    rows = []
    specs = [(flex, "flow_cms", "outcome",
              [("extinction_diameter_mm", "mm"), ("burning_rate_mm2_s", "mm2/s"),
               ("burn_time_s", "s"), ("extinction_to_initial_diameter_ratio", "ratio")]),
             (bass2, "flow_first_cms", "flow_event_noted",
              [("o2_consumed_pct_points", "% by volume"), ("co2_produced_pct_points", "% by volume"),
               ("co_produced_ppm", "ppm"), ("co_to_co2_molar_ratio", "mol/mol")])]
    for table, flow_col, outcome_col, results in specs:
        for _, t in table.iterrows():
            for name, unit in results:
                if pd.notna(t[name]):
                    rows.append([t.test_id, t.investigation_id, t.fuel_material, t.sample_geometry,
                                 t.o2_pct, t.pressure_kpa, t[flow_col], t.diluent, t[outcome_col],
                                 name, t[name], unit, t.source_file, t.source_row])
    return pd.DataFrame(rows, columns=[
        "test_id", "investigation_id", "fuel_material", "sample_geometry", "o2_pct",
        "pressure_kpa", "flow_cms", "diluent", "outcome", "result_name", "result_value",
        "result_unit", "source_file", "source_row"])


DICTIONARY = [
    ("all", "test_id", "Test identifier", "", "Source test or sample number with a prefix"),
    ("all", "o2_pct", "Oxygen concentration at the start of the test", "% by volume", "Mole fraction x 100, or the source percent value"),
    ("all", "o2_basis", "What the oxygen value describes", "", "'ambient' = chamber or duct atmosphere; 'oxidizer_stream' = gas issuing from the burner in inverse flames. Only 'ambient' values describe a habitat atmosphere"),
    ("all", "pressure_kpa", "Ambient pressure", "kPa", "mmHg x 0.133322, atm x 101.325, bar x 100. Empty when the table has no pressure column"),
    ("all", "flow_cms", "Imposed flow speed", "cm/s", "Copied. BASS-II: first value listed in 'Air display'. Empty when the table has no flow speed"),
    ("all", "flags", "Problems found in the source cells of this row", "", "Semicolon-separated codes set by rules in build_test_tables.py"),
    ("all", "source_file / source_row", "Where the row comes from", "", "PSI file name and row number counted with the header as row 1"),
    ("flex", "diluent", "Gas added to the O2/N2 atmosphere", "", "CO2 if CO2 fraction > 0, He if He fraction > 0, otherwise N2"),
    ("flex", "extinction_diameter_mm", "Droplet diameter when the visible flame went out", "mm", "Copied"),
    ("flex", "burning_rate_mm2_s", "Average burning rate constant (slope of diameter squared against time)", "mm2/s", "Copied. Source column is labelled 'mm'; unit per NASA/TP-2015-216046"),
    ("flex", "extinction_to_initial_diameter_ratio", "Share of the initial diameter left when the visible flame went out", "ratio", "extinction_diameter_mm / initial_diameter_mm"),
    ("bass2", "fuel_material / sample_geometry / dimensions", "Material, shape and stated dimensions", "", "Parsed from 'Fuel Sample Material' by keyword rules; inches x 25.4, microns / 1000"),
    ("bass2", "flow_min_cms / flow_max_cms", "Lowest and highest flow speed listed for the test", "cm/s", "Min and max of the numbers in 'Air display'"),
    ("bass2", "flow_event_noted", "Event written next to the flow settings", "", "'extinction' if the cell contains 'ext', 'blowoff' if it contains 'blowoff'"),
    ("bass2", "o2_consumed_pct_points", "Drop in O2 over the test", "percentage points", "initial - final. Empty when the final value is flagged"),
    ("bass2", "co2_produced_pct_points", "Rise in CO2 over the test", "percentage points", "final - initial"),
    ("bass2", "co_produced_ppm", "Rise in CO over the test", "ppm", "final - initial. Empty when a reading is over range"),
    ("bass2", "co_to_co2_molar_ratio", "CO produced per CO2 produced", "mol/mol", "(co_produced_ppm x 1e-4) / co2_produced_pct_points, only when the CO2 rise is at least 0.05 points"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    flex, bass2 = build_flex(), build_bass2()
    conditions = build_conditions(flex, bass2)
    flex.to_csv(os.path.join(OUT, "tests_flex.csv"), index=False)
    bass2.to_csv(os.path.join(OUT, "tests_bass2.csv"), index=False)
    conditions.to_csv(os.path.join(OUT, "tests_conditions.csv"), index=False)
    to_long(flex, bass2).to_csv(os.path.join(OUT, "tests_long.csv"), index=False)
    pd.DataFrame(DICTIONARY, columns=["table", "column", "meaning", "unit", "rule"]).to_csv(
        os.path.join(OUT, "tests_dictionary.csv"), index=False)

    summary = conditions.groupby("investigation_id").agg(
        tests=("test_id", "size"), o2=("o2_pct", "count"),
        pressure=("pressure_kpa", "count"), flow=("flow_cms", "count"))
    print(summary.to_string())
    print(f"\n{len(conditions)} tests in tests_conditions.csv")
    flagged = conditions["flags"].str.split(";").explode()
    print(flagged[flagged != ""].value_counts().to_string())


if __name__ == "__main__":
    main()
