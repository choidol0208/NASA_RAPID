#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Export the catalog CSVs to a reviewer-friendly workbook and write the data dictionary.

Usage:
    python3 scripts/export_catalog_xlsx.py

Reads   data/catalog/investigations.csv, data/catalog/configurations.csv
Writes  data/catalog/catalog.xlsx         (shaded header bands: group / column key / meaning)
        data/catalog/data_dictionary.csv  (table, column, group, meaning, allowed values, used_by)

The CSVs stay the machine source of truth; the workbook is for people to read and review.
"""
import csv
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, "data", "catalog")

# (column, group, meaning, allowed values / unit, used_by)
INV_DICT = [
    ("investigation_id", "identification", "Investigation id (short code chosen by the team)", "like BASS-II", "join key"),
    ("psi_accession", "identification", "PSI accession number", "like PSI-25", "join key, source"),
    ("investigation_name", "identification", "Full PSI title", "English", "display"),
    ("project_group", "identification", "Parent group", "ACME, BASS, Saffire, SAME …", "grouping"),
    ("tier", "classification", "Team priority group", "1 = the challenge text links it to fire safety directly, 2 = named only, 3 = the rest", "work order"),
    ("platform", "evidence quality", "Where the experiment ran", "ISS, free_flyer (Cygnus), ground", "display"),
    ("hardware", "identification", "Experiment hardware (as in the PSI record)", "free text", "display, filter"),
    ("operation_period", "identification", "Period of operation (as in the PSI record, MM-DD-YYYY)", "", "display"),
    ("objectives", "classification", "Objective in one or two sentences (summary of the PSI record)", "English", "summary, AI evidence"),
    ("research_focus", "classification", "Research focus (several separated by ;)", "ignition, flame_spread, burning_rate, extinction_limit, flammability_boundary, smoke_soot, detection, suppression, flame_structure", "S_role"),
    ("fire_safety_role", "classification", "Fire-safety axis (team judgement; several separated by ;)", "prevention, detection, suppression, fundamental", "S_role"),
    ("fire_scenario_tags", "classification", "Fire situations it relates to (team judgement)", "cabin_material, wire_overheat, liquid_leak, gas_leak, smoldering, dust, high_oxygen, quiescent_ambient", "explanation, filter"),
    ("mu_g_duration_class", "evidence quality", "How long microgravity lasted", "long, short, none (ground)", "evidence factor M"),
    ("has_1g_comparison", "evidence quality", "Whether the record holds a normal-gravity (1 g) comparison under the same conditions", "Y, (empty = not found in the record)", "partial-gravity note, tie-break"),
    ("data_availability", "evidence quality", "Form of the data", "raw_table, summary_table, images_video, derived_analysis, papers_only", "evidence factor M"),
    ("test_count", "evidence quality", "Number of tests (table rows, or flames ignited)", "number", "display"),
    ("key_findings", "results", "Key findings (only what the PSI record or table states)", "English, numbers with units", "summary, AI evidence"),
    ("psi_url", "source", "PSI investigation page", "URL", "link to source"),
    ("psi_dataset_id", "source", "PSI dataset number", "like PSI-25", "link to source"),
    ("dataset_doi", "source", "Dataset DOI (PSI asks to be cited by it)", "10.60555/…", "link to source, citation"),
    ("doi_list", "source", "DOIs of related papers (up to 6, separated by ;)", "", "AI evidence"),
    ("license", "source", "License in the PSI record", "CC0-1.0 and others", "compliance"),
    ("source_notes", "verification", "Source notes and differences from the original", "free text", "verification"),
    ("verification_status", "verification", "Verification state", "ai_extracted, human_verified", "badge (no effect on the score)"),
    ("verified_by", "verification", "Who checked it (initials)", "", "verification"),
    ("collected_on", "verification", "Date collected", "YYYY-MM-DD", "verification"),
]
CFG_DICT = [
    ("config_id", "identification", "Configuration id (the unit the ranking scores)", "like BASS-II-C01", "join key"),
    ("investigation_id", "identification", "Link to the investigation table", "", "join key"),
    ("psi_accession", "identification", "PSI accession number", "", "join key"),
    ("config_label", "identification", "Description of the configuration", "English", "display"),
    ("fuel_phase", "fuel", "Fuel phase", "solid, liquid, gas, aerosol", "S_fuel"),
    ("fuel_material", "fuel", "Specific material", "PMMA, SIBAL, n-heptane …", "S_fuel"),
    ("fuel_class", "fuel", "Fuel class (team judgement)", "fabric, charring_solid, thermoplastic_solid, pyrolyzing_solid, liquid_hydrocarbon, liquid_alcohol, gaseous_hydrocarbon, hydrogen, particulate", "S_fuel"),
    ("melt_behavior", "fuel", "Melting or charring behaviour (solids)", "melts, chars, neither", "S_fuel"),
    ("surrogate_for", "fuel", "What this gas burner emulates", "solid", "S_fuel"),
    ("sooting_tendency", "fuel", "Sooting tendency (team judgement)", "low, medium, high", "detection profile"),
    ("sample_geometry", "geometry", "Sample or burner shape", "flat_sheet, rod, sphere, droplet, jet_burner, porous_burner, spherical_burner, counterflow_burner, heated_sample", "S_geom"),
    ("thickness_mm", "geometry", "Thickness or diameter (mm)", "number or range", "sets thermal_regime"),
    ("length_mm", "geometry", "Length (mm)", "", "display"),
    ("width_mm", "geometry", "Width (mm)", "", "display"),
    ("thermal_regime", "geometry", "Thermal thickness (solids, team judgement)", "thin, intermediate, thick", "S_geom"),
    ("flame_type", "geometry", "Flame type", "diffusion, premixed, cool_flame, none", "explanation"),
    ("flow_config", "flow", "Flow configuration (several separated by ;)", "quiescent, opposed, concurrent, coflow, counterflow, radial", "S_cfg"),
    ("flow_min_cms", "flow", "Lowest air speed tested (cm/s)", "number", "S_v"),
    ("flow_max_cms", "flow", "Highest air speed tested (cm/s)", "number", "S_v"),
    ("o2_min_pct", "atmosphere", "Lowest oxygen mole fraction (%)", "number", "S_O2"),
    ("o2_max_pct", "atmosphere", "Highest oxygen mole fraction (%)", "number", "S_O2"),
    ("o2_reference", "atmosphere", "What the oxygen value refers to (added column)", "ambient = surrounding atmosphere, oxidizer_stream = oxidizer issuing from a burner", "explanation, warning"),
    ("pressure_min_kpa", "atmosphere", "Lowest total pressure (kPa)", "number", "S_P"),
    ("pressure_max_kpa", "atmosphere", "Highest total pressure (kPa)", "number", "S_P"),
    ("ppo2_min_kpa", "atmosphere", "Lowest oxygen partial pressure (computed)", "kPa", "display"),
    ("ppo2_max_kpa", "atmosphere", "Highest oxygen partial pressure (computed)", "kPa", "display"),
    ("diluent", "atmosphere", "Diluent or inert gas", "N2, CO2, He, Ar", "S_dil"),
    ("diluent_max_pct", "atmosphere", "Highest diluent concentration (%)", "number", "S_dil"),
    ("ambient_temp_k", "atmosphere", "Ambient temperature (K)", "number", "display"),
    ("atmosphere_basis", "atmosphere", "Where the numbers come from (added column)", "table, record, not_reported", "confidence display"),
    ("o2_source", "atmosphere", "Source of the oxygen range (added column)", "table, record, test_matrix, team, empty", "reasons (the word 'tested')"),
    ("pressure_source", "atmosphere", "Source of the pressure range (added column)", "table, record, test_matrix, team, empty", "reasons (the word 'tested')"),
    ("flow_source", "atmosphere", "Source of the flow-speed range (added column)", "table, record, test_matrix, team, empty", "reasons"),
    ("gravity_level", "atmosphere", "Gravity condition", "microgravity, 1g", "warning"),
    ("ignition_method", "ignition", "Ignition method", "hot_wire and others", "display"),
    ("measured_outputs", "results", "Quantities measured", "flame_spread_rate, burning_rate, extinction_condition, particle_size …", "detection profile, link to data"),
    ("flammability_boundary_reported", "results", "Whether extinction or flammability-limit data exist", "Y, N", "explanation of evidence"),
    ("extinction_mechanism", "results", "Extinction mechanism", "radiative_loss, blowoff, dilution, quenching, burnout", "explanation"),
    ("key_findings", "results", "Results of this configuration (only what the record or table states)", "English", "AI evidence"),
    ("test_count_config", "results", "Number of tests in this configuration", "number", "display"),
    ("tests_table_ref", "results", "Test table file and filter", "file name (condition)", "link to raw data"),
    ("source_notes", "verification", "Source notes", "", "verification"),
    ("verification_status", "verification", "Verification state", "ai_extracted, human_verified", "badge (no effect on the score)"),
]

FONT = "Arial"
GROUP_FILL = {
    "identification": "1F3A5F", "classification": "2E5E4E", "evidence quality": "5B4A1F", "results": "5A2E4F",
    "source": "3D3D6B", "verification": "4A4A4A", "fuel": "7A3E12", "geometry": "2E5E4E", "flow": "1F4F7A",
    "atmosphere": "1F3A5F", "ignition": "5B4A1F",
}
KEY_FILL = PatternFill("solid", fgColor="D9E2F3")
MEANING_FILL = PatternFill("solid", fgColor="EEF2F8")
thin = Side(style="thin", color="B7C3D6")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
WIDE = {"objectives": 60, "key_findings": 60, "source_notes": 48, "investigation_name": 44, "config_label": 44,
        "hardware": 34, "fuel_material": 34, "measured_outputs": 34, "doi_list": 40, "research_focus": 30,
        "atmosphere_basis": 32, "tests_table_ref": 40, "psi_url": 44}


def read_csv(name):
    with open(os.path.join(CAT, name), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
        return rows


def to_value(v):
    if v == "":
        return None
    try:
        f = float(v)
        return int(f) if f.is_integer() and "." not in v else f
    except ValueError:
        return v


def write_sheet(ws, rows, spec, title):
    cols = [c[0] for c in spec]
    assert cols == list(rows[0].keys()), f"{title}: dictionary and CSV columns differ"
    # row 1: group band (merged), row 2: column key, row 3: meaning
    start = 1
    for i in range(1, len(spec) + 1):
        g = spec[i - 1][1]
        nxt = spec[i][1] if i < len(spec) else None
        if nxt != g:
            ws.merge_cells(start_row=1, start_column=start, end_row=1, end_column=i)
            c = ws.cell(row=1, column=start, value=g)
            c.fill = PatternFill("solid", fgColor=GROUP_FILL.get(g, "333333"))
            c.font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
            c.alignment = Alignment(horizontal="center", vertical="center")
            for j in range(start, i + 1):
                ws.cell(row=1, column=j).fill = PatternFill("solid", fgColor=GROUP_FILL.get(g, "333333"))
            start = i + 1
    for j, (col, _g, meaning, allowed, _u) in enumerate(spec, start=1):
        k = ws.cell(row=2, column=j, value=col)
        k.fill, k.font, k.border = KEY_FILL, Font(name=FONT, bold=True, size=10, color="1F2A44"), BORDER
        k.alignment = Alignment(vertical="center", wrap_text=True)
        m = ws.cell(row=3, column=j, value=meaning)
        m.fill, m.font, m.border = MEANING_FILL, Font(name=FONT, italic=True, size=9, color="44506A"), BORDER
        m.alignment = Alignment(vertical="top", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = WIDE.get(col, 16)
    for i, row in enumerate(rows, start=4):
        for j, col in enumerate(cols, start=1):
            c = ws.cell(row=i, column=j, value=to_value(row[col]))
            c.font = Font(name=FONT, size=10)
            c.border = BORDER
            c.alignment = Alignment(vertical="top", wrap_text=col in WIDE)
            if col == "psi_url" and row[col]:
                c.hyperlink = row[col]
                c.font = Font(name=FONT, size=10, color="1F4FB4", underline="single")
    ws.row_dimensions[1].height = 18
    ws.row_dimensions[2].height = 30
    ws.row_dimensions[3].height = 42
    ws.freeze_panes = "C4"
    ws.auto_filter.ref = f"A2:{get_column_letter(len(cols))}{len(rows) + 3}"
    ws.sheet_view.zoomScale = 90


def main():
    inv, cfg = read_csv("investigations.csv"), read_csv("configurations.csv")
    wb = Workbook()
    rd = wb.active
    rd.title = "README"
    lines = [
        ("Flame in Freefall experiment catalog", True),
        ("24 NASA PSI combustion-science investigations (Investigations) and 41 test configurations (Configurations), the unit the ranking scores.", False),
        ("", False),
        ("How to read it", True),
        ("Row 1 (coloured band) = column group, row 2 (blue shading) = column name (the key the code reads), row 3 (light shading, italic) = meaning. Data start at row 4.", False),
        ("Keep the column names in English as they are: the code (scoring/scorer.py) reads them. The source data are the CSV files in the same folder; this file is a copy for people to read.", False),
        ("Empty = the value was not found in the PSI record or table. It is never filled with 0. The ranking treats it as 'unknown' (0.5).", False),
        ("The atmosphere_basis column says where the numbers come from: table = a PSI experimental table, record = the PSI record text, not_reported = not recorded.", False),
        ("o2_source, pressure_source and flow_source give the source of each value: table = a value in an experimental table, record = written in the record text (not a test value), test_matrix = a planned test matrix, team = the team's reading. The ranking's reasons say 'tested' only for table values.", False),
        ("", False),
        ("Notes", True),
        ("Every row was extracted by an AI (Claude) from the PSI records (data/psi/) and has verification_status = ai_extracted. A row becomes human_verified only after a person compares it with the original; that changes no score.", False),
        ("tier, fire_safety_role, research_focus, fire_scenario_tags, fuel_class, thermal_regime and sooting_tendency are the team's judgement, not NASA's classification.", False),
        ("In rows with o2_reference = oxidizer_stream (inverse flames), the oxygen value is the oxygen of the oxidizer issuing from the burner, not of the surrounding atmosphere.", False),
        ("", False),
        ("Source", True),
        ("NASA Physical Sciences Informatics (https://psi.nasa.gov/); each experiment's DOI is in the dataset_doi column. License in the license column (mostly CC0-1.0; the PSI-10 record states none).", False),
        ("Built by scripts/build_catalog.py, then scripts/export_catalog_xlsx.py (2026-11-14).", False),
    ]
    for i, (t, bold) in enumerate(lines, start=1):
        c = rd.cell(row=i, column=1, value=t)
        c.font = Font(name=FONT, bold=bold, size=13 if i == 1 else 10)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    rd.column_dimensions["A"].width = 120
    write_sheet(wb.create_sheet("Investigations"), inv, INV_DICT, "Investigations")
    write_sheet(wb.create_sheet("Configurations"), cfg, CFG_DICT, "Configurations")
    dd = wb.create_sheet("Dictionary")
    hdr = ["table", "column", "group", "meaning", "allowed_values_or_unit", "used_by"]
    for j, h in enumerate(hdr, start=1):
        c = dd.cell(row=1, column=j, value=h)
        c.fill, c.font, c.border = KEY_FILL, Font(name=FONT, bold=True, size=10), BORDER
    rows = [("investigations",) + d for d in INV_DICT] + [("configurations",) + d for d in CFG_DICT]
    for i, r in enumerate(rows, start=2):
        for j, v in enumerate(r, start=1):
            c = dd.cell(row=i, column=j, value=v)
            c.font, c.border = Font(name=FONT, size=10), BORDER
            c.alignment = Alignment(wrap_text=True, vertical="top")
    for j, w in enumerate([16, 30, 16, 40, 60, 24], start=1):
        dd.column_dimensions[get_column_letter(j)].width = w
    dd.freeze_panes = "A2"
    wb.save(os.path.join(CAT, "catalog.xlsx"))
    with open(os.path.join(CAT, "data_dictionary.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(hdr)
        w.writerows(rows)
    print("wrote catalog.xlsx and data_dictionary.csv")


if __name__ == "__main__":
    main()
